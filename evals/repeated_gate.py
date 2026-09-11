#!/usr/bin/env python3
"""Evaluate a repeated pilot from captured evidence and separately supplied judgments."""

import argparse
import importlib.util
import json
from pathlib import Path

import run_claude as runner
from run_repeated import plan

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_record", ROOT / "review/scripts/validate_record.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode()


def read(path):
    return json.loads(path.read_text())


def inspect_run(root, policy_path):
    policy = read(policy_path)
    manifest = read(root / "manifest.json")
    policy_hash = runner.digest(policy_path.read_bytes())
    if manifest["policy_sha256"] != policy_hash or runner.digest((root / "policy.json").read_bytes()) != policy_hash:
        raise ValueError("Policy does not match the frozen run.")
    if manifest["schedule"] != plan(policy):
        raise ValueError("Schedule differs from the complete policy denominator.")
    if runner.snapshot(root / "candidate") != manifest["candidate_files"]:
        raise ValueError("Candidate snapshot changed.")
    if runner.digest(Path(validator.__file__).read_bytes()) != manifest["candidate_files"]["scripts/validate_record.py"]:
        raise ValueError("Current validator differs from the evaluated package; use the matching checkout.")
    if set(manifest["runner_files"]) != {"run_claude.py", "run_repeated.py"}:
        raise ValueError("Both frozen runner sources are required.")
    for name, digest in manifest["runner_files"].items():
        if name not in ("run_claude.py", "run_repeated.py") or runner.digest((root / name).read_bytes()) != digest:
            raise ValueError("Runner source hash mismatch.")
    packets = {}
    for case, entry in policy["cases"].items():
        path = root / "fixtures" / (case + ".json")
        if runner.digest(path.read_bytes()) != entry["sha256"]:
            raise ValueError("Fixture hash mismatch.")
        packets[case] = read(path)
    body = (root / "candidate/SKILL.md").read_text().split("---", 2)[-1].strip()
    observed = {}
    for item in manifest["schedule"]:
        directory = root / item["id"]
        try:
            inv, cap = read(directory / "invocation.json"), read(directory / "capture.json")
            for stream in ("stdout", "stderr"):
                if runner.digest(cap[stream].encode()) != cap[stream + "_sha256"]:
                    raise ValueError("Capture bytes changed or cannot be reconstructed losslessly.")
            events = [json.loads(line) for line in cap["stdout"].splitlines() if line.strip()]
            calls = [b for e in events if e.get("type") == "assistant"
                     for b in e.get("message", {}).get("content", []) if b.get("type") == "tool_use"]
            texts = [b.get("text", "") for e in events if e.get("type") == "user"
                     for b in e.get("message", {}).get("content", []) if b.get("type") == "text"]
            init = next(e for e in events if e.get("type") == "system" and e.get("subtype") == "init")
            final = next(e for e in reversed(events) if e.get("type") == "result")
            if (inv["exit_code"] or inv["timed_out"] or final.get("is_error") or not final.get("modelUsage")
                    or runner.loading_errors(calls, events) or not any(body in t for t in texts)
                    or any(c["name"] not in runner.ALLOWED.split(",") for c in calls)
                    or set(init["tools"]) != set(runner.ALLOWED.split(","))
                    or init["permissionMode"] != "dontAsk"):
                raise ValueError("Unsuccessful or ineligible host invocation.")
            packet = packets[item["case_id"]]
            expected = {runner.SKILL_PATH + "/" + name: digest for name, digest in manifest["candidate_files"].items()
                        if packet["capabilities"].get("specialist_references") or not name.startswith("references/")
                        or name == "references/report-contract.md"}
            expected.update({"case.json": runner.digest(encoded(packet)),
                             "review-context.json": runner.digest(encoded(inv["provided_provenance"])),
                             "reviewerest-plugin/.claude-plugin/plugin.json": runner.digest(encoded({"name": "reviewerest-eval", "version": "1.0.0"}))})
            if inv["before"] != expected or inv["after"] != expected:
                raise ValueError("Inputs differ from the frozen packet and candidate or changed during review.")
            model = init.get("model")
            if not isinstance(model, str) or not model or init["claude_code_version"] != manifest["cli_version"].split()[0]:
                raise ValueError("Missing model identity or CLI drift.")
            try:
                record = runner.extract_record(final["result"])
            except (ValueError, KeyError):
                observed[item["id"]] = {"status": "invalid_record", "model": model, "reason": "Response extraction failed."}
                continue
            if read(directory / "record.json") != record or record.get("provenance") != inv["provided_provenance"]:
                raise ValueError("Saved response or provided provenance differs from capture.")
            errors = validator.validate(record)
            observed[item["id"]] = {"status": "invalid_record" if errors else "eligible", "model": model,
                                     "record_sha256": runner.digest((directory / "record.json").read_bytes()), "errors": errors}
        except (OSError, ValueError, KeyError, TypeError, AttributeError, StopIteration) as exc:
            observed[item["id"]] = {"status": "unavailable", "reason": str(exc)}
    return policy, policy_hash, observed


def decide(policy, policy_hash, observed, assessments, calibration=None):
    schedule = plan(policy)
    threshold = policy.get("confirmed_failures_to_fail")
    if type(threshold) is not int or not 1 <= threshold <= policy["repetitions"]:
        raise ValueError("Invalid failure threshold.")
    if assessments.get("policy_sha256") != policy_hash:
        raise ValueError("Assessment policy identity mismatch.")
    grades = assessments.get("trials")
    if not isinstance(grades, dict) or set(grades) - {i["id"] for i in schedule}:
        raise ValueError("Unknown trial or invalid assessment map.")
    models = {o["model"] for o in observed.values() if o.get("model")}
    drift = len(models) > 1
    results, failures = [], {}
    for item in schedule:
        obs = observed.get(item["id"], {"status": "unavailable"})
        status, reason = "inconclusive", "Missing or ineligible evidence/assessment."
        failed_conditions = []
        if obs["status"] == "invalid_record":
            status, reason = "fail", "Captured response violates the structured-output contract."
            failed_conditions = ["record_structure"]
        elif obs["status"] == "eligible" and item["id"] in grades:
            grade = grades[item["id"]]
            if grade.get("record_sha256") != obs["record_sha256"]:
                raise ValueError("Assessment refers to another response: " + item["id"])
            actor = grade.get("assessor", {})
            if not all(isinstance(actor.get(k), str) and actor[k].strip() for k in ("identity", "prior_exposure")):
                raise ValueError("Assessor identity and exposure required.")
            conditions = grade.get("conditions", {})
            if set(conditions) != set(policy["cases"][item["case_id"]]["conditions"]):
                raise ValueError("Every planned condition must be assessed exactly once.")
            outcomes = []
            for name, condition in conditions.items():
                outcome = condition.get("outcome")
                refs = condition.get("evidence_refs")
                if (outcome not in ("pass", "fail", "inconclusive")
                        or not isinstance(condition.get("reason"), str) or not condition["reason"].strip()
                        or not isinstance(refs, list) or not refs
                        or not all(isinstance(r, str) and r.strip() for r in refs)):
                    raise ValueError("Condition needs outcome, reasoning and evidence references.")
                confirmation = condition.get("confirmation")
                if outcome == "fail" and not (isinstance(confirmation, dict) and confirmation.get("by") and confirmation.get("reference")):
                    outcome = "inconclusive"
                if outcome == "fail":
                    failed_conditions.append(name)
                outcomes.append(outcome)
            status = "fail" if "fail" in outcomes else "inconclusive" if "inconclusive" in outcomes else "pass"
            reason = "Assessor-supplied condition judgments; not automatically established truth."
        for name in failed_conditions:
            key = item["case_id"] + ":" + name
            failures[key] = failures.get(key, 0) + 1
        results.append({**item, "status": status, "reason": reason})
    enough_failures = any(count >= threshold for count in failures.values())
    complete_pass = all(r["status"] == "pass" for r in results)
    calibration_ok = bool(isinstance(calibration, dict) and calibration.get("policy_sha256") == policy_hash
                          and calibration.get("approved") is True and calibration.get("independent") is True
                          and calibration.get("reviewed_by") and calibration.get("evidence_ref"))
    behavior = "inconclusive" if drift else "fail" if enough_failures else "pass" if complete_pass else "inconclusive"
    decision = "pass" if behavior == "pass" and calibration_ok else "fail" if behavior == "fail" else "inconclusive"
    counts = {s: sum(r["status"] == s for r in results) for s in ("pass", "fail", "inconclusive")}
    return {"decision": decision, "observed_behavior": behavior, "planned_trials": len(schedule),
            "trial_counts": counts, "trials": results, "confirmed_failure_counts": failures,
            "model_drift": drift, "observed_models": sorted(models), "calibration_record_present": calibration_ok,
            "limits": ["Calibration and judgments are recorded attestations, not independently authenticated by this tool.",
                       "A passing small repeated sample does not establish population reliability or a regression against another version."],
            "substantive_truth_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--assessments", type=Path, required=True)
    parser.add_argument("--calibration", type=Path)
    args = parser.parse_args()
    try:
        policy, digest, observed = inspect_run(args.run, args.policy)
        result = decide(policy, digest, observed, read(args.assessments), read(args.calibration) if args.calibration else None)
        result["policy_sha256"] = digest
        result["assessments_sha256"] = runner.digest(args.assessments.read_bytes())
        result["calibration_sha256"] = runner.digest(args.calibration.read_bytes()) if args.calibration else None
        result["observations"] = observed
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {"decision": "inconclusive", "error": str(exc), "substantive_truth_verified": False}
    result["gate_sha256"] = runner.digest(Path(__file__).read_bytes())
    result["validator_sha256"] = runner.digest(Path(validator.__file__).read_bytes())
    print(json.dumps(result, indent=2))
    return {"pass": 0, "fail": 3, "inconclusive": 4}[result["decision"]]


if __name__ == "__main__":
    raise SystemExit(main())
