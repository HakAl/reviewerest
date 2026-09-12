#!/usr/bin/env python3
"""Export source-first packets or mechanically validate a returned adjudication."""

import argparse
import json
from pathlib import Path
import re
import shutil

import grade_reviews as grader

SUITE = grader.ROOT / "evals/skill-effect-adjudication-v1"
PHASE_FILES = ("protocol.md", "response-template.json", "shared-output.schema.json")


def phase_one(suite):
    manifest = grader.read(suite / "phase1/manifest.json")
    ids = manifest["case_ids"]
    if not isinstance(ids, list) or len(ids) != 9 or any(not isinstance(i, str) or not re.fullmatch(r"r\d{2}", i) for i in ids):
        raise ValueError("Phase-one case IDs must be nine neutral rNN aliases.")
    names = list(PHASE_FILES) + ["cases/" + ident + ".json" for ident in manifest["case_ids"]]
    if len(set(manifest["case_ids"])) != 9 or set(manifest["files"]) != set(names):
        raise ValueError("Phase one must contain exactly its fixed protocol and nine source packets.")
    for name in names:
        path = suite / "phase1" / name
        if grader.host.digest(path.read_bytes()) != manifest["files"][name]:
            raise ValueError("Frozen phase-one input changed: " + name)
    packets = [grader.read(suite / "phase1/cases" / (ident + ".json")) for ident in manifest["case_ids"]]
    for ident, packet in zip(manifest["case_ids"], packets):
        if set(packet) != {"id", "request", "mode", "capabilities", "context", "artifacts"} or packet["id"] != ident:
            raise ValueError("Unexpected source-packet fields or identity.")
    return manifest, packets


def bundle(suite):
    manifest, packets = phase_one(suite)
    parts = [(suite / "phase1/protocol.md").read_text(),
             "\nPhase-one manifest SHA-256: " + grader.host.digest((suite / "phase1/manifest.json").read_bytes()),
             "\nProposed common candidate-output schema:\n```json\n" + (suite / "phase1/shared-output.schema.json").read_text() + "```",
             "\nRecord your adjudication using this template:\n```json\n" + (suite / "phase1/response-template.json").read_text() + "```"]
    for packet in packets:
        encoded = json.dumps(packet, indent=2, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        parts += ["\nSource packet " + packet["id"], "<artifact_content>\n" + encoded + "\n</artifact_content>"]
    return "\n".join(parts) + "\n"


def export(suite, destination):
    manifest, _ = phase_one(suite)
    text = bundle(suite)
    destination.mkdir(parents=True, exist_ok=False)
    for name in (*manifest["files"], "manifest.json"):
        dest = destination / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(suite / "phase1" / name, dest)
    (destination / "START-HERE.md").write_text(text)


def validate_candidate(value, packet):
    """Check the proposed common output shape and location bounds, not review truth."""
    if not isinstance(value, dict) or set(value) != {"findings"} or not isinstance(value["findings"], list):
        raise ValueError("Only a findings array is allowed at the root.")
    sources = {a["source"]: a["text"].splitlines() for a in packet["artifacts"]}
    for finding in value["findings"]:
        if not isinstance(finding, dict) or set(finding) != {"finding", "location", "claim", "severity"}:
            raise ValueError("Each finding must contain exactly finding, location, claim and severity.")
        if not all(isinstance(finding[k], str) and finding[k].strip() for k in ("finding", "claim")):
            raise ValueError("Finding and claim must be nonempty text.")
        if finding["severity"] not in ("high", "medium", "low", "unrated"):
            raise ValueError("Unknown severity token.")
        if not isinstance(finding["location"], list) or not finding["location"]:
            raise ValueError("Each finding requires at least one source location.")
        for loc in finding["location"]:
            if not isinstance(loc, dict) or set(loc) != {"source", "start_line", "end_line"}:
                raise ValueError("Location fields differ from the shared schema.")
            source, start, end = loc["source"], loc["start_line"], loc["end_line"]
            if (not isinstance(source, str) or source not in sources or type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= len(sources[source])):
                raise ValueError("Location does not resolve within a supplied source.")


def validate_adjudication(record, suite):
    """Validate submitted structure and evidence; never adjudicate its conclusions."""
    manifest, packets = phase_one(suite)
    expected_digest = grader.host.digest((suite / "phase1/manifest.json").read_bytes())
    if (not isinstance(record, dict) or type(record.get("version")) is not int or record.get("version") != 1 or record.get("status") != "adjudicated"
            or record.get("phase1_manifest_sha256") != expected_digest):
        raise ValueError("Completed adjudication must identify the frozen phase-one manifest.")
    identity = record.get("adjudicator")
    if not isinstance(identity, dict) or not all(isinstance(identity.get(k), str) and identity[k].strip()
                                               for k in ("identity", "role", "prior_exposure")):
        raise ValueError("Adjudicator identity, role and exposure must be recorded.")
    cases = record.get("cases")
    if not isinstance(cases, list) or len(cases) != len(packets) or any(not isinstance(c, dict) for c in cases):
        raise ValueError("Every phase-one case requires one judgment.")
    ids = [c.get("id") for c in cases]
    if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids) or set(ids) != set(manifest["case_ids"]):
        raise ValueError("Adjudication cases differ from phase one.")
    by_id = {p["id"]: p for p in packets}
    quotes = 0
    for case in cases:
        if case.get("status") != "adjudicated" or type(case.get("clean_within_scope")) is not bool:
            raise ValueError("Case judgment is unfinished.")
        for key in ("scope_interpretation", "evidence_sufficiency", "acceptance_notes", "severity_range_and_basis"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise ValueError("Missing case judgment: " + key)
        for key in ("legitimate_alternatives", "unsupported_or_out_of_scope_claims", "open_questions"):
            if not isinstance(case.get(key), list) or any(not isinstance(v, str) for v in case[key]):
                raise ValueError("Case judgment list is malformed: " + key)
        packet = by_id[case["id"]]
        validate_candidate({"findings": case.get("reference_findings")}, packet)
        if case["clean_within_scope"] and case["reference_findings"]:
            raise ValueError("Clean reference case also contains defect findings.")
        if not case["clean_within_scope"] and not case["reference_findings"]:
            raise ValueError("Defective reference case requires a finding.")
        sources = {a["source"]: a["text"].splitlines() for a in packet["artifacts"]}
        evidence = case.get("located_evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError("Located evidence is required for each judgment.")
        for cite in evidence:
            if not isinstance(cite, dict) or set(cite) != {"source", "start_line", "end_line", "quote"}:
                raise ValueError("Evidence citation fields differ from the contract.")
            source, start, end, quote = (cite[k] for k in ("source", "start_line", "end_line", "quote"))
            if (not isinstance(source, str) or source not in sources or type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= len(sources[source]) or not isinstance(quote, str) or not quote.strip()
                    or quote not in "\n".join(sources[source][start - 1:end])):
                raise ValueError("Adjudication quote does not resolve to supplied text.")
            quotes += 1
    return {"valid": True, "case_count": len(cases), "resolving_evidence_quotes": quotes,
            "validation_scope": "submitted_case_structure_source_locations_and_quotes",
            "substantive_truth_verified": False,
            "limits": ["Identity and prior exposure are recorded declarations, not authenticated host evidence.",
                       "This does not accept criteria, resolve open questions, or authorize comparison runs."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=SUITE)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--record", type=Path)
    args = parser.parse_args()
    try:
        if args.record:
            print(json.dumps(validate_adjudication(grader.read(args.record), args.suite), indent=2))
            return 0
        export(args.suite, args.output)
        print("Exported source-first packet. This does not perform or certify adjudication.")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
