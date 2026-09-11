#!/usr/bin/env python3
"""Run frozen cases through native Claude Code skills in fresh temporary projects.

This runner never reads expectations. Scoring is a separate, offline operation.
Requires Claude Code >=2.1.248 and existing authentication. Each invocation has
a CLI cost limit and a wall-clock timeout; no retry or fallback is automatic.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = "Read,Glob,Grep,Skill"
EXPECTED_SKILL = "reviewerest-eval:review"
SKILL_PATH = "reviewerest-plugin/skills/review"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {str(p.relative_to(root)): digest(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n")


def extract_record(result):
    """Accept a bare JSON object or one whole fenced object, never repair it."""
    value = result.strip()
    if value.startswith("```json\n") and value.endswith("\n```"):
        value = value[8:-4]
    elif value.startswith("```\n") and value.endswith("\n```"):
        value = value[4:-4]
    record = json.loads(value)
    if not isinstance(record, dict):
        raise ValueError("Expected one review object")
    return record


def command(cli, budget, session, prompt, work):
    return [cli, "--restricted", "--strict-mcp-config", "--mcp-config",
            '{"mcpServers":{}}', "--tools", ALLOWED, "--allowedTools", ALLOWED,
            "--permission-mode", "dontAsk", "--permission-prompts", "none",
            "--no-chrome", "--no-session-persistence", "--session-id", session,
            "--max-budget-usd", str(budget), "--output-format", "stream-json",
            "--verbose", "--include-hook-events", "--plugin-dir",
            str(work / "reviewerest-plugin"), "-p", prompt]


def loading_errors(calls, events):
    successful = {block.get("tool_use_id") for event in events
                  for block in event.get("message", {}).get("content", [])
                  if isinstance(block, dict) and block.get("type") == "tool_result"
                  and not block.get("is_error", False)}
    skill_calls = [c for c in calls if c.get("name") == "Skill"]
    errors = []
    if not any(c.get("input", {}).get("skill") == EXPECTED_SKILL and c.get("id") in successful
               for c in skill_calls):
        errors.append("No successful Skill(" + EXPECTED_SKILL + ") invocation in the trace")
    if any(c.get("input", {}).get("skill") != EXPECTED_SKILL for c in skill_calls):
        errors.append("Another skill was invoked; instruction attribution is confounded")
    return errors


def invoke(cmd, cwd, timeout):
    started = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        # Kill only this newly created process group, including any CLI children.
        try:
            import os
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = proc.communicate()
    return stdout, stderr, proc.returncode, timed_out, round(time.monotonic() - started, 3)


def run_case(cli, packet, skill, destination, budget, timeout):
    destination.mkdir()
    with tempfile.TemporaryDirectory(prefix="reviewerest-claude-") as temporary:
        work = Path(temporary).resolve()
        installed = work / SKILL_PATH
        shutil.copytree(skill, installed, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        plugin_metadata = work / "reviewerest-plugin/.claude-plugin"
        plugin_metadata.mkdir()
        save(plugin_metadata / "plugin.json", {"name": "reviewerest-eval", "version": "1.0.0"})
        if not packet["capabilities"].get("specialist_references", False):
            for path in (installed / "references").iterdir():
                if path.name != "report-contract.md":
                    path.unlink()
        save(work / "case.json", packet)
        session = str(uuid.uuid4())
        version_match = re.search(r'version:\s*"([^"\n]+)"', (installed / "SKILL.md").read_text())
        context = {"skill_version": version_match.group(1) if version_match else None,
                   "skill_revision": "sha256:" + digest(json.dumps(snapshot(installed), sort_keys=True).encode()),
                   "run_id": session,
                   "reviewer": {"model": None, "family": None},
                   "generator": {"model": None, "family": None}}
        save(work / "review-context.json", context)
        prompt = ("Use the Skill tool to invoke exactly " + EXPECTED_SKILL + " "
                  "(installed at " + SKILL_PATH + "). If it is unavailable, stop and "
                  "report that; do not substitute another skill. "
                  "Perform the request in case.json using its supplied context, "
                  "capabilities, and artifacts. Host-provided provenance is in review-context.json; "
                  "unknown identities there remain null. Source locations refer to the artifacts "
                  "inside that packet. Return only the requested structured review record "
                  "as one JSON object. This is an unattended invocation.")
        cmd = command(cli, budget, session, prompt, work)
        before = snapshot(work)
        receipt = {"case_id": packet["case_id"], "command": cmd,
                   "provided_provenance": context,
                   "started_at": datetime.now(timezone.utc).isoformat(),
                   "workspace": str(work), "before": before}
        save(destination / "invocation.json", receipt)
        stdout, stderr, code, timed_out, elapsed = invoke(cmd, work, timeout)
        # Lossless text capture with ASCII JSON escapes, plus original byte hashes.
        # Keep failures and malformed output. Never rewrite a review to make it pass.
        save(destination / "capture.json", {
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr)})
        events, malformed = [], []
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("Event is not an object")
                events.append(event)
            except (ValueError, UnicodeDecodeError):
                malformed.append(line.decode("utf-8", errors="replace"))
        final = next((e for e in reversed(events) if e.get("type") == "result"), {})
        initial = next((e for e in events if e.get("type") == "system"
                        and e.get("subtype") == "init"), {})
        calls = [block for event in events if event.get("type") == "assistant"
                 for block in event.get("message", {}).get("content", [])
                 if isinstance(block, dict) and block.get("type") == "tool_use"]
        after = snapshot(work)
        receipt.update({"exit_code": code, "timed_out": timed_out,
                        "elapsed_seconds": elapsed, "after": after,
                        "workspace_unchanged": before == after,
                        "malformed_event_lines": malformed,
                        "host_init": initial, "tool_calls": calls,
                        "eligibility_errors": loading_errors(calls, events),
                        "result_metadata": {k: v for k, v in final.items() if k != "result"},
                        "record_error": None})
        record = None
        try:
            if code or timed_out or final.get("is_error") or not final:
                raise ValueError("Invocation failed or produced no successful result event")
            if not final.get("modelUsage"):
                raise ValueError("No model invocation recorded: " + str(final.get("result", "")))
            record = extract_record(final.get("result", ""))
        except ValueError as exc:
            receipt["record_error"] = str(exc)
        save(destination / "invocation.json", receipt)
        if record is not None:
            save(destination / "record.json", record)
        return receipt, record


def positive(value):
    result = float(value)
    if not 0 < result < float("inf"):
        raise argparse.ArgumentTypeError("Must be finite and positive")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--case-dir", type=Path, default=ROOT / "evals/cases",
                        help="Directory containing case packets only; never reads labels")
    parser.add_argument("--output", type=Path, required=True, help="New directory; never overwritten")
    parser.add_argument("--budget-per-case", type=positive, default=1.0)
    parser.add_argument("--timeout", type=positive, default=240)
    parser.add_argument("--cli", default="claude")
    args = parser.parse_args()
    if len(set(args.cases)) != len(args.cases) or any(not re.fullmatch(r"\d{2}", c) for c in args.cases):
        parser.error("Case IDs must be unique two-digit numbers")
    raw_packets = {c: (args.case_dir / (c + ".json")).read_bytes() for c in args.cases}
    packets = [json.loads(raw_packets[c]) for c in args.cases]
    if any(p.get("case_id") != c for c, p in zip(args.cases, packets)):
        parser.error("Each packet case_id must match its requested file name")
    cli = shutil.which(args.cli)
    if cli is None:
        parser.error("Claude CLI not found")
    version = subprocess.check_output([cli, "--version"], text=True, timeout=15).strip()
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (2, 1, 248):
        parser.error("Requires Claude Code >=2.1.248 for --restricted")
    args.output.mkdir(parents=True, exist_ok=False)
    candidate = args.output / "candidate"
    shutil.copytree(ROOT / "review", candidate, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(Path(__file__), args.output / "runner-source.py")
    manifest = {"version": 1, "cli_version": version, "cases": args.cases,
                "candidate_commit": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "candidate_files": snapshot(candidate),
                "candidate_identity": "Commit anchors the repository baseline; saved candidate/ files pin the evaluated working-tree package.",
                "runner_sha256": digest(Path(__file__).read_bytes()),
                "fixture_files": {c: digest(raw_packets[c]) for c in args.cases},
                "budget_per_case_usd": args.budget_per_case,
                "timeout_per_case_seconds": args.timeout,
                "model_selection": "CLI default; actual identity recorded in each trace",
                "expected_skill": EXPECTED_SKILL,
                "labels_provided": False, "schema_forced_by_host": False,
                "automatic_retries": False,
                "limits": ["Author-written synthetic fixtures; this runner does not grade truth.",
                           "Native explicit invocation, not automatic skill selection.",
                           "Restricted tools are not a general operating-system sandbox.",
                           "Managed host policy and CLI startup context may still apply.",
                           "CLI dollar estimates can differ from billing and caps can overshoot a response."]}
    save(args.output / "manifest.json", manifest)
    records, summaries = [], []
    for packet in packets:
        print("Starting case " + packet["case_id"], flush=True)
        receipt, record = run_case(cli, packet, candidate,
                                   args.output / packet["case_id"], args.budget_per_case, args.timeout)
        if record is not None:
            records.append({"case_id": packet["case_id"], "review": record})
        summaries.append({k: receipt[k] for k in ["case_id", "exit_code", "timed_out",
                          "elapsed_seconds", "workspace_unchanged", "record_error", "eligibility_errors"]})
        save(args.output / "records.json", records)
        save(args.output / "summary.json", summaries)
        print(json.dumps(summaries[-1]), flush=True)
        # Stop on setup/runtime failures rather than spending the rest of a batch.
        if (receipt["exit_code"] or receipt["timed_out"]
                or receipt["eligibility_errors"]
                or not receipt["result_metadata"].get("modelUsage")):
            break
    failed = len(summaries) != len(packets) or any(s["record_error"] or s["eligibility_errors"]
                                                or not s["workspace_unchanged"]
                                                for s in summaries)
    return 3 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
