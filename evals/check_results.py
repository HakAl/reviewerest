#!/usr/bin/env python3
"""Check captured forward-test records against frozen routing expectations.

Semantic finding truth and actual tool behavior require separate assessment.
This script writes only a JSON receipt to stdout. It never invokes a model.
"""

import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_record", ROOT / "review/scripts/validate_record.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def assess(records, expectations, *, allow_legacy=False):
    results = []
    seen = set()
    for item in records:
        case_id = item.get("case_id")
        if case_id not in expectations or case_id in seen:
            results.append({"case_id": case_id, "error": "Unknown or duplicate case ID."})
            continue
        seen.add(case_id)
        report = item.get("review")
        schema_errors = validator.validate(report, allow_legacy=allow_legacy)
        lenses = report.get("lenses", []) if isinstance(report, dict) else []
        selected = {lens["id"] for lens in lenses if isinstance(lens, dict)
                    and isinstance(lens.get("id"), str) and lens.get("selection") == "selected"}
        expected = expectations[case_id]
        findings = report.get("findings", []) if isinstance(report, dict) else []
        findings = findings if isinstance(findings, list) else []
        contract_errors = []
        bounds = expected.get("finding_count")
        if bounds and not bounds["min"] <= len(findings) <= bounds["max"]:
            contract_errors.append("Finding count outside declared fixture bounds.")
        if "allowed_severities" in expected and any(
                not isinstance(f, dict) or f.get("severity") not in expected["allowed_severities"]
                for f in findings):
            contract_errors.append("Finding severity outside declared fixture choices.")
        results.append({
            "case_id": case_id,
            "record_version": report.get("version") if isinstance(report, dict) else None,
            "legacy_validation": allow_legacy and isinstance(report, dict) and report.get("version") in (1, 2),
            "schema_errors": schema_errors,
            "missing_required_lenses": sorted(set(expected["required_lenses"]) - selected),
            "forbidden_lenses_selected": sorted(set(expected["forbidden_lenses"]) & selected),
            "finding_count": len(findings),
            "fixture_contract_errors": contract_errors,
            "semantic_assessment": "not performed by this checker",
        })
    return {"cases_checked": len(seen), "missing_cases": sorted(set(expectations) - seen),
            "results": results, "substantive_truth_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", help="JSON arrays of case_id/review objects")
    parser.add_argument("--cases", help="Explicit planned subset, comma-separated (default: all cases)")
    parser.add_argument("--allow-legacy", action="store_true", help="Use historical checks for version 1 or 2 records")
    parser.add_argument("--expectations", type=Path, default=ROOT / "evals/expectations.json",
                        help="Frozen scoring expectations; kept out of reviewer inputs")
    args = parser.parse_args()
    expected = json.loads(args.expectations.read_text())
    records = []
    for path in args.results:
        records.extend(json.loads(Path(path).read_text()))
    expectations = {c["case_id"]: c for c in expected["cases"]}
    if args.cases is not None:
        selected = args.cases.split(",")
        if len(set(selected)) != len(selected) or any(c not in expectations for c in selected):
            parser.error("--cases must contain unique known case IDs")
        expectations = {c: expectations[c] for c in selected}
    result = assess(records, expectations, allow_legacy=args.allow_legacy)
    result["planned_cases"] = sorted(expectations)
    print(json.dumps(result, indent=2))
    bad = result["missing_cases"] or any(r.get("error") or r.get("schema_errors") or
          r.get("missing_required_lenses") or r.get("forbidden_lenses_selected") or
          r.get("fixture_contract_errors") for r in result["results"])
    return 3 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
