#!/usr/bin/env python3
"""Run or compare the frozen scope-position experiment, retaining both score columns."""

import argparse
import copy
import json
from pathlib import Path
import shutil

import grade_reviews as grader
import compare_grader_runs as repeated

SUITE = grader.ROOT / "evals/grader-format-v1"
BASE = grader.ROOT / "evals/grader-v1"


def validate_design(suite):
    manifest, protocol, packets = grader.inputs(suite)
    raw = (suite / "pairing.json").read_bytes()
    if grader.host.digest(raw) != manifest["files"]["pairing.json"]:
        raise ValueError("Pairing plan changed.")
    design = json.loads(raw)
    if design["repetitions"] != 2 or design["planned_assessments"] != 8:
        raise ValueError("This pilot requires two repeats of four packets.")
    if (suite / "protocol.json").read_bytes() != (BASE / "protocol.json").read_bytes():
        raise ValueError("Protocol must match the unchanged baseline.")
    covered = []
    for pair in design["pairs"]:
        original, moved = pair["original"], pair["moved"]
        covered.extend((original, moved))
        source = (BASE / "packets" / (pair["base"] + ".json")).read_bytes()
        if (suite / "packets" / (original + ".json")).read_bytes() != source:
            raise ValueError("Original packet bytes differ from the baseline.")
        expected = copy.deepcopy(packets[original])
        expected["packet_id"] = moved
        artifact = next(a for a in expected["artifacts"] if a["source"] == "readiness.json")
        values = json.loads(artifact["text"])
        scope = values.pop("scope")
        values["scope"] = scope
        artifact["text"] = json.dumps(values, indent=2) + "\n"
        if packets[moved] != expected:
            raise ValueError("Variant differs from the exact scope-position manipulation.")
        changed = next(a["text"] for a in packets[moved]["artifacts"] if a["source"] == "readiness.json")
        before = next(a["text"] for a in packets[original]["artifacts"] if a["source"] == "readiness.json")
        if json.loads(changed) != json.loads(before):
            raise ValueError("Parsed readiness values changed.")
    if len(covered) != 4 or len(set(covered)) != 4 or set(covered) != set(packets):
        raise ValueError("Every packet must belong to exactly one pair.")
    return design, packets


def compare(suite, runs):
    design, packets = validate_design(suite)
    if len(runs) != design["repetitions"]:
        raise ValueError("Supply exactly the two planned answer files; missing grades stay in their files.")
    scored = {name: grader.score(suite, answers) for name, answers in runs.items()}
    within = repeated.compare(suite, runs)
    rows = []
    for name, score in scored.items():
        indexed = {row["packet_id"]: row for row in score["results"]}
        for pair in design["pairs"]:
            a, b = indexed[pair["original"]], indexed[pair["moved"]]
            same = a["raw_outcome"] == b["raw_outcome"] if a["verdict_valid"] and b["verdict_valid"] else None
            rows.append({"run": name, "base": pair["base"], "same_raw_verdict": same,
                         "original": {k:a[k] for k in ("packet_id", "raw_outcome", "verdict_valid", "citations_resolve", "grade_valid")},
                         "moved": {k:b[k] for k in ("packet_id", "raw_outcome", "verdict_valid", "citations_resolve", "grade_valid")}})
    counts = {}
    for arm in ("original", "moved"):
        selected = {p[arm]: packets[p[arm]] for p in design["pairs"]}
        per_run = {name: repeated.citation_counts(selected, answers) for name, answers in runs.items()}
        counts[arm] = {"planned_answers": 4,
                       "answers_with_resolving_citations": sum(row[arm]["citations_resolve"] is True for row in rows),
                       "invalid_citation_answers": sum(row[arm]["citations_resolve"] is False for row in rows),
                       "missing_citation_answers": sum(row[arm]["citations_resolve"] is None for row in rows),
                       "per_run": per_run}
    return {"version": 1, "planned_assessments": 8, "planned_pair_comparisons": 4,
            "same_recorded_model_and_cli": within["same_recorded_model_and_cli"],
            "same_raw_verdict_pairs": sum(r["same_raw_verdict"] is True for r in rows),
            "changed_raw_verdict_pairs": sum(r["same_raw_verdict"] is False for r in rows),
            "unknown_raw_verdict_pairs": sum(r["same_raw_verdict"] is None for r in rows),
            "pairs": rows, "citation_counts_by_arm": counts,
            "within_arm_repetition": {k:within[k] for k in ("stable_verdict_packets", "changed_verdict_packets", "unknown_verdict_packets", "rows")},
            "scores": {name:{k:s[k] for k in ("status", "planned", "matches", "raw_matches", "raw_defect_counts")} for name,s in scored.items()},
            "substantive_truth_verified": False,
            "limits": design["limits"] + ["Temperature was not pinned. Fresh sessions do not establish statistical independence.",
                       "Quote choices are assessor-selected; omission of an authority quote is not successful relocation.",
                       "This is a position/formatting sensitivity pilot, not a causal test of terminal wrapping or an error-rate estimate."]}


def run(suite, output, cli):
    design, _ = validate_design(suite)
    output.mkdir(parents=True, exist_ok=False)
    # Freeze everything used by the orchestrator and assessor before spending.
    frozen_suite = output / "suite"
    shutil.copytree(suite, frozen_suite)
    for module in (grader, repeated):
        shutil.copyfile(module.__file__, output / Path(module.__file__).name)
    shutil.copyfile(__file__, output / Path(__file__).name)
    grader.host.save(output / "experiment.json", design)
    grader.host.save(output / "orchestrator.json", {"sha256": grader.host.digest(Path(__file__).read_bytes())})
    budget = design["budget"]
    models = set()
    failed_answer = False
    for number in range(1, design["repetitions"] + 1):
        dest = output / f"run-{number:02d}"
        code = grader.run(frozen_suite, dest, cli, budget["per_packet_usd"], budget["per_batch_usd"], budget["timeout_seconds"])
        failed_answer = failed_answer or code != 0
        summaries = grader.read(dest / "summary.json")
        answers = grader.read(dest / "answers.json")
        grader.host.save(output / f"answers-{number:02d}.json", answers)
        models.add((answers["assessor"].get("model"), answers["assessor"].get("cli_version")))
        print(json.dumps({"completed_run": number, "exit_code": code}), flush=True)
        if len(summaries) != 4 or not all(s["eligible"] for s in summaries) or len(models) != 1:
            return 4
    return 4 if failed_answer else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    running = subs.add_parser("run")
    running.add_argument("--output", type=Path, required=True)
    running.add_argument("--cli", default="claude")
    scoring = subs.add_parser("compare")
    scoring.add_argument("answers", nargs=2, type=Path)
    for sub in (running, scoring):
        sub.add_argument("--suite", type=Path, default=SUITE)
    args = parser.parse_args()
    try:
        if args.action == "run":
            cli = shutil.which(args.cli)
            if cli is None:
                raise ValueError("Claude CLI not found.")
            return run(args.suite, args.output, cli)
        if args.answers[0].name == args.answers[1].name:
            raise ValueError("Use distinct filenames for the two runs.")
        result = compare(args.suite, {p.name: grader.read(p) for p in args.answers})
        print(json.dumps(result, indent=2))
        return 0 if result["same_recorded_model_and_cli"] and not result["unknown_raw_verdict_pairs"] else 4
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
