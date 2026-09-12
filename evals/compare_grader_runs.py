#!/usr/bin/env python3
"""Compare raw verdict stability and citation resolution on identical grader inputs."""

import argparse
import json
from pathlib import Path

import grade_reviews as grader


def citation_counts(packets, answers):
    totals = {"quotes": 0, "resolving": 0, "unchecked_authority_quotes": 0,
              "unchecked_authority_resolving": 0, "unavailable_citation_lists": [], "authority_quotes": []}
    for ident, packet in packets.items():
        grade = answers.get("grades", {}).get(ident)
        if not isinstance(grade, dict) or not isinstance(grade.get("citations"), list):
            totals["unavailable_citation_lists"].append(ident)
            continue
        sources = {a["source"]: a["text"].splitlines() for a in packet["artifacts"]}
        readiness = next(a["text"] for a in packet["artifacts"] if a["source"] == "readiness.json")
        unchecked = json.loads(readiness).get("authority_service") == "not_checked"
        for index, cite in enumerate(grade["citations"]):
            totals["quotes"] += 1
            cite = cite if isinstance(cite, dict) else {}
            source, quote = cite.get("source"), cite.get("quote")
            start, end = cite.get("start_line"), cite.get("end_line")
            resolves = (isinstance(source, str) and source in sources and type(start) is int and type(end) is int
                        and 1 <= start <= end <= len(sources[source]) and isinstance(quote, str) and bool(quote.strip())
                        and quote in "\n".join(sources[source][start - 1:end]))
            totals["resolving"] += resolves
            if unchecked and source == "readiness.json" and isinstance(quote, str) and "authority_service" in quote:
                totals["unchecked_authority_quotes"] += 1
                totals["unchecked_authority_resolving"] += resolves
                totals["authority_quotes"].append({"packet_id": ident, "citation_index": index,
                                                  "start_line": start, "end_line": end, "resolves": resolves})
    return totals


def compare(suite, runs):
    if len(runs) < 2:
        raise ValueError("At least two named runs required.")
    scored = {name: grader.score(suite, answers) for name, answers in runs.items()}
    _, _, packets = grader.inputs(suite)
    identities = [a.get("assessor", {}) for a in runs.values()]
    identity_fields = ("model", "cli_version")
    identity_known = all(all(isinstance(a.get(k), str) and a[k].strip() for k in identity_fields) for a in identities)
    same_identity = identity_known and all(all(a[k] == identities[0][k] for k in identity_fields) for a in identities)
    rows = []
    for offset, original in enumerate(next(iter(scored.values()))["results"]):
        observations = {name: result["results"][offset] for name, result in scored.items()}
        valid_verdicts = all(r["verdict_valid"] for r in observations.values())
        values = [r["raw_outcome"] for r in observations.values()]
        stable = len(set(values)) == 1 if valid_verdicts else None
        rows.append({"packet_id": original["packet_id"], "expected": original["expected"],
                     "verdict_stable": stable,
                     "all_citations_resolve": all(r["citations_resolve"] is True for r in observations.values()),
                     "runs": {name: {k:r[k] for k in ("raw_outcome", "verdict_valid", "citations_resolve", "grade_valid")}
                              for name, r in observations.items()}})
    return {"version": 1, "run_order": list(runs), "planned_packets": len(rows),
            "same_recorded_model_and_cli": same_identity,
            "comparison_status": "same_recorded_condition" if same_identity else "host_identity_missing_or_changed",
            "stable_verdict_packets": sum(r["verdict_stable"] is True for r in rows),
            "changed_verdict_packets": sum(r["verdict_stable"] is False for r in rows),
            "unknown_verdict_packets": sum(r["verdict_stable"] is None for r in rows),
            "all_citations_resolve_packets": sum(r["all_citations_resolve"] for r in rows),
            "rows": rows,
            "scores": {name: {k: result[k] for k in ("status", "planned", "matches", "raw_matches", "raw_defect_counts")}
                       for name, result in scored.items()},
            "citation_counts": {name: citation_counts(packets, answers) for name, answers in runs.items()},
            "limits": ["Input hashes must match exactly; this command compares unchanged packets, not variants.",
                       "Model aliases, CLI versions and output wrappers do not establish immutable host state or statistical independence.",
                       "Raw outcome stability is separate from citation resolution and substantive correctness.",
                       "A disagreement with the unresolved p31 author label is not a calibrated correctness or error judgment."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answers", nargs="+", type=Path)
    parser.add_argument("--suite", type=Path, default=grader.ROOT / "evals/grader-v1")
    args = parser.parse_args()
    if len(set(p.name for p in args.answers)) != len(args.answers):
        parser.error("Use distinct answer filenames to identify runs.")
    try:
        result = compare(args.suite, {p.name: grader.read(p) for p in args.answers})
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if result["same_recorded_model_and_cli"] and not result["unknown_verdict_packets"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
