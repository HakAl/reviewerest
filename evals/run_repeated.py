#!/usr/bin/env python3
"""Run a frozen repeated-case plan with bounded usage and no adaptive retries."""

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

import run_claude as runner

ROOT = Path(__file__).resolve().parents[1]


def plan(policy):
    if not isinstance(policy, dict):
        raise ValueError("Policy must be an object.")
    count = policy.get("repetitions")
    cases = policy.get("cases")
    if type(count) is not int or not 1 <= count <= 20 or not isinstance(cases, dict) or not cases:
        raise ValueError("Use 1-20 repetitions and a nonempty case map.")
    if any(not re.fullmatch(r"\d{2}", case) for case in cases):
        raise ValueError("Case IDs must be two digits.")
    for entry in cases.values():
        conditions = entry.get("conditions") if isinstance(entry, dict) else None
        if (not isinstance(conditions, list) or not conditions
                or not all(isinstance(c, str) and c.strip() for c in conditions)
                or len(set(conditions)) != len(conditions)):
            raise ValueError("Each case needs unique nonempty condition IDs.")
    return [{"id": f"r{trial:02d}-{case}", "trial": trial, "case_id": case}
            for trial in range(1, count + 1)
            for case in sorted(cases, reverse=trial % 2 == 0)]


def run(policy_path, output, cli, budget, total_budget, timeout):
    raw_policy = policy_path.read_bytes()
    policy = json.loads(raw_policy)
    schedule = plan(policy)
    if len(schedule) * budget > total_budget + 1e-9:
        raise ValueError("Planned per-case caps exceed the declared total budget.")
    packets, raw_packets = {}, {}
    for case, entry in policy["cases"].items():
        source = (ROOT / entry["file"]).resolve()
        if not source.is_relative_to(ROOT.resolve()):
            raise ValueError("Fixture must be inside the repository.")
        raw = source.read_bytes()
        if runner.digest(raw) != entry["sha256"]:
            raise ValueError("Frozen fixture hash mismatch: " + case)
        packet = json.loads(raw)
        if packet.get("case_id") != case:
            raise ValueError("Packet case ID mismatch.")
        raw_packets[case], packets[case] = raw, packet
    version = subprocess.check_output([cli, "--version"], text=True, timeout=15).strip()
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (2, 1, 248):
        raise ValueError("Claude Code >=2.1.248 required.")
    output.mkdir(parents=True, exist_ok=False)
    (output / "policy.json").write_bytes(raw_policy)
    (output / "fixtures").mkdir()
    for case, raw in raw_packets.items():
        (output / "fixtures" / (case + ".json")).write_bytes(raw)
    candidate = output / "candidate"
    shutil.copytree(ROOT / "review", candidate, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for source in (Path(__file__), Path(runner.__file__)):
        shutil.copyfile(source, output / source.name)
    manifest = {"version": 1, "policy_sha256": runner.digest(raw_policy), "schedule": schedule,
                "candidate_files": runner.snapshot(candidate), "cli_version": version,
                "candidate_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "runner_files": {p.name: runner.digest(p.read_bytes()) for p in (Path(__file__), Path(runner.__file__))},
                "budget_per_case_usd": budget, "declared_total_budget_usd": total_budget,
                "timeout_seconds": timeout,
                "limits": ["CLI cost caps are estimates and may overshoot a response.",
                           "Model uses the CLI default; drift across trials prevents a comparable gate result.",
                           "Separate fresh sessions do not prove statistically independent samples."]}
    runner.save(output / "manifest.json", manifest)
    completed = []
    for item in schedule:
        print("Starting " + item["id"], flush=True)
        receipt, record = runner.run_case(cli, packets[item["case_id"]], candidate,
                                          output / item["id"], budget, timeout)
        completed.append({**item, **{k: receipt[k] for k in
                         ("exit_code", "timed_out", "record_error", "eligibility_errors", "workspace_unchanged")}})
        runner.save(output / "summary.json", completed)
        print(json.dumps(completed[-1]), flush=True)
        # Preserve the full plan and all attempts. A setup failure does not buy more attempts.
        if (receipt["exit_code"] or receipt["timed_out"] or receipt["eligibility_errors"]
                or not receipt["result_metadata"].get("modelUsage")
                or not receipt["workspace_unchanged"]):
            break
    return 0 if len(completed) == len(schedule) and all(not r["record_error"] for r in completed) else 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget-per-case", type=runner.positive, default=1)
    parser.add_argument("--total-budget", type=runner.positive, required=True)
    parser.add_argument("--timeout", type=runner.positive, default=240)
    parser.add_argument("--cli", default="claude")
    args = parser.parse_args()
    cli = shutil.which(args.cli)
    if cli is None:
        parser.error("Claude CLI not found.")
    try:
        return run(args.policy, args.output, cli, args.budget_per_case, args.total_budget, args.timeout)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
