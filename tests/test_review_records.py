"""Check report relationships and fail-closed handling of malformed inputs."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("validate_record", Path(__file__).resolve().parents[1] / "review/scripts/validate_record.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def supported_record():
    return {
        "version": 2, "status": "complete", "scope": "Review arithmetic against the supplied integer contract.",
        "provenance": {"skill_version": "1.1.0", "skill_revision": None, "run_id": None,
                       "reviewer": {"model": None, "family": None}, "generator": {"model": None, "family": None}},
        "no_review_reason": None,
        "target": {"artifact": "calc.py", "revision": "fixture-v1", "base": None, "assumptions": []},
        "lenses": [{"id": "correctness", "selection": "selected", "reason": "Integer contract supplied.",
                    "coverage": "checked", "depth": "core", "reference_reads": [], "evidence_ids": ["e1"]}],
        "evidence": [{"id": "e1", "source": "calc.py", "location": "line 2", "revision": "fixture-v1",
                      "kind": "source", "observation": "Returns n+2 where contract requires 2*n."}],
        "checks": [{"id": "k1", "method": "static", "criterion": "Return 2*n for integer n.",
                    "status": "fail", "evidence_ids": ["e1"], "limitation": None, "finding_ids": ["f1"]}],
        "candidates": [{"id": "c1", "disposition": "reported", "finding_id": "f1", "reason": "Counterexample n=3."}],
        "findings": [{"id": "f1", "severity": "major", "title": "Wrong arithmetic", "locations": ["calc.py:2"],
                      "trigger": "n=3", "consequence": "Returns 5 instead of 6", "evidence_ids": ["e1"],
                      "lenses": ["correctness"], "basis": "inferred", "uncertainty": None, "recommendation": "Return 2*n."}],
        "limits": [], "missing_input": None, "candidates_for_scope": [], "handoff": None,
    }


class RecordTests(unittest.TestCase):
    def test_audit_probes_rejected_for_coverage_not_just_version(self):
        directory = Path(__file__).parent / "fixtures/review-audit-2026-09-09"
        for name in ("empty", "failpass"):
            record = json.loads((directory / (name + ".json")).read_text())
            self.assertTrue(validator.validate(record))
            self.assertEqual(validator.validate(record, allow_legacy=True), [])
            record.update(version=2, provenance=supported_record()["provenance"], no_review_reason=None)
            if record["checks"]:
                record["checks"][0].update(criterion="Compare the token safely.", finding_ids=[], disposition_reason="No supported defect established.")
            paths = {error["path"] for error in validator.validate(record)}
            self.assertNotIn("version", paths)
            self.assertTrue(paths & {"status", "limits", "lenses", "evidence", "checks"})

    def test_clean_review_and_completed_review_with_failure_are_valid(self):
        record = supported_record()
        self.assertEqual(validator.validate(record), [])
        record["findings"] = []
        record["candidates"] = []
        record["checks"][0].update(status="pass", finding_ids=[])
        record["evidence"][0]["observation"] = "Returns 2*n for integer n."
        self.assertEqual(validator.validate(record), [])

    def test_no_review_outcome_needs_evidence_and_cannot_hide_findings(self):
        record = supported_record()
        record.update(lenses=[], findings=[], candidates=[], no_review_reason="The supplied diff is empty.")
        record["checks"][0].update(status="pass", method="compare", criterion="Determine whether the supplied diff has changes.", finding_ids=[])
        record["evidence"][0]["observation"] = "Host-supplied diff is empty."
        self.assertEqual(validator.validate(record), [])
        record["evidence"] = []
        self.assertTrue(validator.validate(record))
        record = supported_record()
        record["no_review_reason"] = "Nothing to review."
        self.assertTrue(validator.validate(record))

    def test_unavailable_selected_coverage_requires_partial_and_limits(self):
        record = supported_record()
        record["lenses"][0]["coverage"] = "unavailable"
        self.assertTrue(validator.validate(record))
        record.update(status="partial", limits=["Required implementation was unavailable."])
        self.assertEqual(validator.validate(record), [])

    def test_failed_check_requires_disposition_even_without_findings(self):
        record = supported_record()
        record.update(findings=[], candidates=[])
        record["checks"][0]["finding_ids"] = []
        self.assertTrue(validator.validate(record))
        record["checks"][0]["disposition_reason"] = "Exploratory hypothesis failed; the observed behavior satisfies the actual requirement."
        self.assertEqual(validator.validate(record), [])

    def test_criteria_and_provenance_are_explicit_and_unknowns_are_allowed(self):
        record = supported_record()
        for path in ("criterion",):
            record["checks"][0].pop(path)
        self.assertTrue(validator.validate(record))
        record = supported_record()
        record.pop("provenance")
        self.assertTrue(validator.validate(record))
        record = supported_record()
        record["checks"][0].update(method="model", assessor={"model": None, "family": None})
        self.assertEqual(validator.validate(record), [])
        record["checks"][0]["assessor"].pop("family")
        self.assertTrue(validator.validate(record))

    def test_host_check_unknown_run_needs_limitation_and_known_run_is_recorded(self):
        record = supported_record()
        check = record["checks"][0]
        check.update(method="host_execution", execution={"run_id": None, "result_ref": None})
        self.assertTrue(validator.validate(record))
        check["limitation"] = "Host supplied results without a run identifier or persistent trace."
        self.assertEqual(validator.validate(record), [])
        check.update(execution={"run_id": "host-run-123", "result_ref": "host://results/123"}, limitation=None)
        self.assertEqual(validator.validate(record), [])

    def test_scope_block_and_unperformed_optional_check_remain_representable(self):
        record = supported_record()
        record.update(status="needs_scope", lenses=[], evidence=[], checks=[], candidates=[], findings=[],
                      missing_input="The explicit target is absent.", limits=["No target artifact was available."])
        self.assertEqual(validator.validate(record), [])
        record = supported_record()
        record["checks"].append({"id": "optional", "method": "host_execution", "status": "not_run",
                                 "criterion": "Optional runtime confirmation of the static result.",
                                 "evidence_ids": [], "execution": {"run_id": None, "result_ref": None},
                                 "limitation": "No execution facility; runtime confirmation is outside the completed static scope."})
        self.assertEqual(validator.validate(record), [])

    def test_supported_record(self):
        self.assertEqual(validator.validate(supported_record()), [])

    def test_dangling_evidence_cannot_validate(self):
        r = supported_record()
        r["evidence"] = []
        self.assertTrue(validator.validate(r))

    def test_unselected_lens_cannot_support_finding(self):
        r = supported_record()
        r["lenses"][0].update(selection="excluded", coverage=None)
        self.assertTrue(validator.validate(r))

    def test_missing_candidate_mapping_cannot_validate(self):
        r = supported_record()
        r["candidates"] = []
        self.assertTrue(validator.validate(r))

    def test_merging_can_preserve_multiple_candidates(self):
        r = supported_record()
        r["candidates"].append({"id": "c2", "disposition": "merged", "finding_id": "f1", "reason": "Same evidenced operation."})
        self.assertEqual(validator.validate(r), [])

    def test_specialized_coverage_requires_successful_read(self):
        r = supported_record()
        r["lenses"][0]["depth"] = "specialized"
        self.assertTrue(validator.validate(r))
        r["lenses"][0]["reference_reads"] = [{"path": "reference.md", "outcome": "unavailable"}]
        self.assertTrue(validator.validate(r))
        r["lenses"][0]["reference_reads"][0]["outcome"] = "read"
        self.assertEqual(validator.validate(r), [])
        r["lenses"][0]["reference_reads"][0]["outcome"] = "success"
        self.assertEqual(validator.validate(r), [])

    def test_partial_coverage_requires_limits(self):
        r = supported_record()
        r["status"] = "partial"
        self.assertTrue(validator.validate(r))

    def test_review_handoff_cannot_claim_edits(self):
        r = supported_record()
        r["handoff"] = {"phase": "edit", "authorized_by": "user request", "finding_ids": ["f1"], "suggested_diff": None, "applied": False}
        self.assertEqual(validator.validate(r), [])
        r["handoff"]["applied"] = True
        self.assertTrue(validator.validate(r))

    def test_duplicate_ids_rejected(self):
        r = supported_record()
        r["evidence"].append(copy.deepcopy(r["evidence"][0]))
        self.assertTrue(validator.validate(r))

    def test_boolean_is_not_version_number(self):
        r = supported_record()
        r["version"] = True
        self.assertTrue(validator.validate(r))

    def test_no_crash_for_bad_field_types(self):
        base = supported_record()
        for field in base:
            for value in [None, [], {}, True, 12, ""]:
                r = copy.deepcopy(base)
                r[field] = value
                with self.subTest(field=field, value=value):
                    self.assertIsInstance(validator.validate(r), list)
        for group in ["lenses", "evidence", "checks", "candidates", "findings"]:
            for field in base[group][0]:
                for value in [None, [], {}, True, 12, ""]:
                    r = copy.deepcopy(base)
                    r[group][0][field] = value
                    with self.subTest(group=group, field=field, value=value):
                        self.assertIsInstance(validator.validate(r), list)


if __name__ == "__main__":
    unittest.main()
