#!/usr/bin/env python3
"""Validate report structure and evidence links, not substantive truth.

Reads a JSON file or stdin; writes a JSON receipt to stdout. Exit 0 valid,
3 invalid, 2 usage. Python 3.11+, standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

LENSES = {"intent", "correctness", "design", "ux", "security", "reliability",
          "performance", "evidence", "clarity", "feasibility"}


def validate(record, *, allow_legacy=False):
    errors = []

    def require(condition, path, message):
        if not condition:
            errors.append({"path": path, "message": message})

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    if not isinstance(record, dict):
        return [{"path": "$", "message": "Record must be an object."}]
    version = record.get("version")
    require(type(version) is int and (version == 3 or (allow_legacy and version in (1, 2))),
            "version", "Expected version 3; versions 1 and 2 require explicit legacy mode.")
    require(record.get("status") in ("complete", "partial", "needs_scope",), "status", "Invalid status.")
    require(text(record.get("scope")), "scope", "Scope must be a nonempty string.")
    target = record.get("target")
    require(isinstance(target, dict) and text(target.get("artifact")), "target", "Target artifact is required.")
    if isinstance(target, dict):
        require(isinstance(target.get("assumptions"), list), "target.assumptions", "Expected an array.")
        require("revision" in target and (target["revision"] is None or text(target["revision"])), "target.revision", "Expected a revision or null.")
        require("base" in target and (target["base"] is None or isinstance(target["base"], dict)), "target.base", "Expected a resolved base object or null.")

    groups = {}
    indexes = {}
    for group in ["lenses", "evidence", "checks", "candidates", "findings"]:
        entries = record.get(group)
        require(isinstance(entries, list), group, "Expected an array.")
        groups[group] = entries if isinstance(entries, list) else []
        indexes[group] = {}
        for i, entry in enumerate(groups[group]):
            path = f"{group}[{i}]"
            if not isinstance(entry, dict):
                require(False, path, "Expected an object.")
                continue
            ident = entry.get("id")
            if not text(ident):
                require(False, path + ".id", "Nonempty ID required.")
            elif ident in indexes[group]:
                require(False, path + ".id", "Duplicate ID.")
            else:
                indexes[group][ident] = entry

    def refs(value, available, path, nonempty=False):
        if not isinstance(value, list):
            require(False, path, "Expected an array of IDs.")
            return []
        require(not nonempty or bool(value), path, "Supporting references required.")
        for item in value:
            require(text(item) and item in available, path, "Unknown or invalid reference ID.")
        return value

    for ident, ev in indexes["evidence"].items():
        for field in ["source", "location", "observation"]:
            require(text(ev.get(field)), f"evidence.{ident}.{field}", "Nonempty string required.")
        require(ev.get("kind") in ("source", "observation", "execution", "reference",), f"evidence.{ident}.kind", "Invalid evidence kind.")
        require("revision" in ev, f"evidence.{ident}.revision", "Revision or explicit null required.")

    selected = set()
    for ident, lens in indexes["lenses"].items():
        path = "lenses." + ident
        require(ident in LENSES, path, "Unknown lens.")
        require(lens.get("selection") in ("selected", "excluded", "unresolved",), path + ".selection", "Invalid selection.")
        require(text(lens.get("reason")), path + ".reason", "Artifact-based reason required.")
        if lens.get("selection") == "selected":
            selected.add(ident)
        if lens.get("selection") == "excluded":
            require(lens.get("coverage") is None, path + ".coverage", "Excluded lens cannot claim coverage.")
        else:
            require(lens.get("coverage") in ("checked", "partial", "unavailable",), path + ".coverage", "Invalid coverage.")
        require(lens.get("depth") in ("core", "specialized",), path + ".depth", "Invalid depth.")
        reads = lens.get("reference_reads")
        require(isinstance(reads, list), path + ".reference_reads", "Expected reference-read array.")
        successful_read = False
        for read in reads if isinstance(reads, list) else []:
            valid = isinstance(read, dict) and text(read.get("path")) and read.get("outcome") in ("read", "success", "unavailable")
            require(valid, path + ".reference_reads", "Use path and outcome read/success/unavailable.")
            successful_read |= bool(valid and read.get("outcome") in ("read", "success"))
        if lens.get("depth") == "specialized" and lens.get("coverage") == "checked":
            require(successful_read, path, "Checked specialized coverage needs a successful reference read.")
        refs(lens.get("evidence_ids"), indexes["evidence"], path + ".evidence_ids", lens.get("coverage") == "checked")

    for ident, check in indexes["checks"].items():
        path = "checks." + ident
        require(check.get("method") in ("static", "compare", "host_execution", "human", "model",), path + ".method", "Invalid check method.")
        require(check.get("status") in ("pass", "fail", "not_run", "inconclusive",), path + ".status", "Invalid check status.")
        refs(check.get("evidence_ids"), indexes["evidence"], path + ".evidence_ids", check.get("status") in ("pass", "fail",))
        if check.get("status") in ("not_run", "inconclusive",):
            require(text(check.get("limitation")), path + ".limitation", "Unperformed/inconclusive checks need a limitation.")

    mapped = set()
    for ident, candidate in indexes["candidates"].items():
        path = "candidates." + ident
        require(candidate.get("disposition") in ("reported", "merged", "discarded",), path + ".disposition", "Invalid candidate disposition.")
        require(text(candidate.get("reason")), path + ".reason", "Disposition reason required.")
        if candidate.get("disposition") == "discarded":
            require(candidate.get("finding_id") is None, path + ".finding_id", "Discarded candidate must not map to a finding.")
        else:
            finding_id = candidate.get("finding_id")
            if text(finding_id) and finding_id in indexes["findings"]:
                mapped.add(finding_id)
            else:
                require(False, path + ".finding_id", "Candidate needs an existing finding.")

    for ident, finding in indexes["findings"].items():
        path = "findings." + ident
        require(ident in mapped, path, "Finding has no candidate traceability.")
        require(finding.get("severity") in ("blocker", "major", "minor",), path + ".severity", "Invalid severity.")
        for field in ["title", "trigger", "consequence", "recommendation"]:
            require(text(finding.get(field)), path + "." + field, "Nonempty string required.")
        require(isinstance(finding.get("locations"), list) and bool(finding["locations"]), path + ".locations", "At least one location required.")
        require(finding.get("basis") in ("observed", "inferred",), path + ".basis", "Invalid finding basis.")
        require("uncertainty" in finding, path + ".uncertainty", "Explicit uncertainty field required.")
        refs(finding.get("evidence_ids"), indexes["evidence"], path + ".evidence_ids", True)
        refs(finding.get("lenses"), selected, path + ".lenses", True)

        if version == 3:
            support = finding.get("claim_support")
            require(isinstance(support, dict), path + ".claim_support", "Separate defect, consequence and correction support required.")
            if not isinstance(support, dict):
                continue
            for role in ("defect", "consequence", "correction"):
                claim = support.get(role)
                cp = path + ".claim_support." + role
                require(isinstance(claim, dict), cp, "Claim support object required.")
                if not isinstance(claim, dict):
                    continue
                level = claim.get("level")
                require(level in ("demonstrated", "inspected", "conditional", "unresolved"), cp + ".level", "Invalid support level.")
                require(role != "defect" or level != "unresolved", cp, "An unresolved concern cannot be a defect finding.")
                ev_ids = refs(claim.get("evidence_ids"), indexes["evidence"], cp + ".evidence_ids", level != "unresolved")
                check_ids = refs(claim.get("check_ids"), indexes["checks"], cp + ".check_ids")
                require(text(claim.get("reasoning")), cp + ".reasoning", "Explain how evidence supports this claim, or what is missing.")
                assumptions = claim.get("assumptions")
                require(isinstance(assumptions, list) and all(text(a) for a in assumptions), cp + ".assumptions", "Expected explicit assumptions as strings.")
                if level == "conditional":
                    require(isinstance(assumptions, list) and bool(assumptions), cp + ".assumptions", "Conditional support needs an unverified assumption.")
                require("next_check" in claim and (claim["next_check"] is None or text(claim["next_check"])), cp + ".next_check", "Use a concrete next check or explicit null.")
                if level in ("conditional", "unresolved"):
                    require(text(claim.get("next_check")), cp + ".next_check", "Name the check or evidence needed to resolve uncertainty.")
                if level == "demonstrated":
                    # Checks and evidence are still self-reported: this validates links only.
                    execution_checks = [indexes["checks"][c] for c in check_ids
                                        if text(c) and c in indexes["checks"]
                                        and indexes["checks"][c].get("method") == "host_execution"
                                        and indexes["checks"][c].get("status") in ("pass", "fail")]
                    execution_evidence = [e for e in ev_ids if text(e) and e in indexes["evidence"]
                                          and indexes["evidence"][e].get("kind") == "execution"]
                    require(any(isinstance(c.get("evidence_ids"), list) and
                                any(e in c["evidence_ids"] for e in execution_evidence)
                                for c in execution_checks), cp,
                            "Demonstrated support needs a performed host check linked to the claim's execution evidence.")

    require(isinstance(record.get("limits"), list), "limits", "Expected limits array.")
    if record.get("status") in ("partial", "needs_scope",):
        require(bool(record.get("limits")), "limits", "Incomplete coverage requires explicit limits.")
    if record.get("status") == "needs_scope":
        require(text(record.get("missing_input")), "missing_input", "Missing scope input required.")
    require(isinstance(record.get("candidates_for_scope"), list), "candidates_for_scope", "Expected scope-candidate array.")
    require("missing_input" in record and "handoff" in record, "$", "Explicit missing_input and handoff fields required.")
    handoff = record.get("handoff")
    if handoff is not None:
        if not isinstance(handoff, dict):
            require(False, "handoff", "Expected object or null.")
        else:
            require(handoff.get("phase") == "edit" and handoff.get("applied") is False, "handoff", "Review may request editing but cannot claim applied edits.")
            require(text(handoff.get("authorized_by")), "handoff.authorized_by", "Authorization source required.")
            refs(handoff.get("finding_ids"), indexes["findings"], "handoff.finding_ids")
    if type(version) is int and version in (2, 3):
        # These are consistency conditions, not a semantic approval gate.
        limits = record.get("limits")
        require(isinstance(limits, list) and all(text(item) for item in limits),
                "limits", "Limits must be nonempty strings when present.")
        incomplete = any(lens.get("selection") == "unresolved" or
                         (lens.get("selection") == "selected" and
                          lens.get("coverage") in ("partial", "unavailable"))
                         for lens in indexes["lenses"].values())
        if incomplete:
            require(record.get("status") != "complete", "status", "Unresolved or incomplete selected coverage cannot be complete.")
            require(isinstance(limits, list) and bool(limits), "limits", "Incomplete lens coverage requires limits.")
        no_review = record.get("no_review_reason")
        require("no_review_reason" in record and (no_review is None or text(no_review)),
                "no_review_reason", "Use null or an evidenced reason nothing was reviewable.")
        if no_review is not None:
            require(not selected and not indexes["findings"], "no_review_reason",
                    "A no-review outcome cannot include selected lenses or findings.")
        if record.get("status") == "complete":
            require(bool(selected) or text(no_review), "lenses", "Complete review needs selected coverage or an explicit no-review reason.")
            require(bool(indexes["evidence"]), "evidence", "Completion needs evidence, including for an empty target.")
            require(any(c.get("status") in ("pass", "fail") for c in indexes["checks"].values()),
                    "checks", "Completion needs a performed check with an outcome.")

        def nullable_field(obj, field, path):
            require(field in obj and (obj[field] is None or text(obj[field])),
                    path + "." + field, "Use a known identity/reference or explicit null.")

        def actor(value, path):
            require(isinstance(value, dict), path, "Expected model and family, each known or null.")
            if isinstance(value, dict):
                nullable_field(value, "model", path)
                nullable_field(value, "family", path)

        provenance = record.get("provenance")
        require(isinstance(provenance, dict), "provenance", "Record skill, reviewer, generator and run identity.")
        if isinstance(provenance, dict):
            require(text(provenance.get("skill_version")), "provenance.skill_version", "Record the skill's criteria version.")
            for field in ("skill_revision", "run_id"):
                nullable_field(provenance, field, "provenance")
            for field in ("reviewer", "generator"):
                actor(provenance.get(field), "provenance." + field)
        for ident, check in indexes["checks"].items():
            path = "checks." + ident
            require(text(check.get("criterion")), path + ".criterion", "State the expected behavior or decision criterion.")
            if check.get("status") == "fail":
                finding_ids = refs(check.get("finding_ids"), indexes["findings"], path + ".finding_ids")
                require(bool(finding_ids) or text(check.get("disposition_reason")), path,
                        "A failed check needs linked findings or a reason it is not reported.")
            if check.get("method") == "model":
                actor(check.get("assessor"), path + ".assessor")
            if check.get("method") == "host_execution":
                execution = check.get("execution")
                require(isinstance(execution, dict), path + ".execution", "Record run_id and result_ref, known or null.")
                if isinstance(execution, dict):
                    for field in ("run_id", "result_ref"):
                        nullable_field(execution, field, path + ".execution")
                    if not execution.get("run_id") or not execution.get("result_ref"):
                        require(text(check.get("limitation")), path + ".limitation", "Explain missing execution provenance.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", help="JSON file or - for stdin")
    parser.add_argument("--allow-legacy", action="store_true", help="Accept versions 1 and 2 with their historical checks only")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.record == "-" else Path(args.record).read_text(encoding="utf-8")
        record = json.loads(raw)
        errors = validate(record, allow_legacy=args.allow_legacy)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors = [{"path": "$", "message": f"Record unavailable or invalid JSON: {type(exc).__name__}."}]
        record = None
    legacy = isinstance(record, dict) and type(record.get("version")) is int and record["version"] in (1, 2)
    print(json.dumps({"valid": not errors, "errors": errors,
                      "validation_scope": "legacy_structure_only" if legacy and args.allow_legacy else "current_structure_coverage_and_claim_links",
                      "substantive_truth_verified": False}, indent=2))
    return 3 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
