#!/usr/bin/env python3
"""Summarize assessor-authored claim judgments; never infer truth from model labels."""

import argparse
import json
from pathlib import Path

ROLES = ("defect", "consequence", "correction")
JUDGMENTS = ("supported", "overstated", "inconclusive")


def summarize(ledger):
    def text(value):
        return isinstance(value, str) and bool(value.strip())

    if not isinstance(ledger, dict) or type(ledger.get("version")) is not int or ledger["version"] != 1:
        raise ValueError("Expected claim ledger version 1.")
    assessor = ledger.get("assessor")
    if not isinstance(assessor, dict) or not all(text(assessor.get(k)) for k in ("identity", "prior_exposure")):
        raise ValueError("Assessor identity and prior exposure are required.")
    if not text(ledger.get("coverage")):
        raise ValueError("Describe extraction coverage and sampling limits.")
    claims = ledger.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Claims must be an array.")
    counts = {role: dict.fromkeys(JUDGMENTS, 0) for role in ROLES}
    seen = set()
    for claim in claims:
        if not isinstance(claim, dict) or not all(text(claim.get(k)) for k in
                ("id", "case_id", "response_location", "quote", "reason")):
            raise ValueError("Each claim needs identity, location, exact excerpt and judgment reason.")
        if claim["id"] in seen:
            raise ValueError("Duplicate claim ID.")
        seen.add(claim["id"])
        role, judgment = claim.get("role"), claim.get("judgment")
        if role not in ROLES or judgment not in JUDGMENTS:
            raise ValueError("Unknown claim role or judgment.")
        refs = claim.get("evidence_refs")
        if not isinstance(refs, list) or not refs or not all(text(r) for r in refs):
            raise ValueError("Record source references supporting the assessment, including its limits.")
        counts[role][judgment] += 1
    results = {}
    for role, count in counts.items():
        adjudicated = count["supported"] + count["overstated"]
        results[role] = {**count, "adjudicated": adjudicated,
                         "overstatement_rate": count["overstated"] / adjudicated if adjudicated else None,
                         "support_rate": count["supported"] / adjudicated if adjudicated else None}
    return {"claims_counted": len(claims), "coverage": ledger["coverage"], "by_role": results,
            "validation_scope": "assessor_ledger_counts_only", "substantive_truth_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(json.loads(args.ledger.read_text()))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "substantive_truth_verified": False}))
        return 3
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
