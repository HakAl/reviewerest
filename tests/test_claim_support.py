"""Reject unsupported evidence labels structurally; do not pretend to grade truth."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_records import supported_record, validator


class ClaimSupportTests(unittest.TestCase):
    def test_each_role_needs_its_own_support(self):
        for role in ("defect", "consequence", "correction"):
            record = supported_record()
            del record["findings"][0]["claim_support"][role]
            self.assertTrue(validator.validate(record))

    def test_static_evidence_cannot_be_relabelled_demonstrated(self):
        record = supported_record()
        support = record["findings"][0]["claim_support"]
        support["defect"]["level"] = "demonstrated"
        self.assertTrue(validator.validate(record))
        record["checks"][0].update(method="host_execution", execution={"run_id": "fixture-run", "result_ref": "fixture-result"})
        record["evidence"][0]["kind"] = "execution"
        self.assertEqual(validator.validate(record), [])
        # A requested, unperformed check cannot substantiate a demonstrated claim.
        record["checks"][0].update(status="not_run", limitation="Execution unavailable.")
        self.assertTrue(validator.validate(record))

    def test_an_unrelated_execution_result_does_not_supply_claim_links(self):
        record = supported_record()
        record["evidence"].append(dict(record["evidence"][0], id="other", kind="execution"))
        record["checks"][0].update(method="host_execution", evidence_ids=["other"],
                                   execution={"run_id": "fixture-run", "result_ref": "fixture-result"})
        record["findings"][0]["claim_support"]["correction"]["level"] = "demonstrated"
        self.assertTrue(validator.validate(record))

    def test_conditional_claim_needs_assumption_and_next_check(self):
        record = supported_record()
        claim = record["findings"][0]["claim_support"]["consequence"]
        claim["level"] = "conditional"
        self.assertTrue(validator.validate(record))
        claim["assumptions"] = ["The unavailable caller uses this result unchanged."]
        self.assertTrue(validator.validate(record))
        claim["next_check"] = "Inspect caller handling of the returned integer."
        self.assertEqual(validator.validate(record), [])

    def test_unresolved_harm_or_fix_does_not_erase_supported_defect(self):
        record = supported_record()
        for role in ("consequence", "correction"):
            record["findings"][0]["claim_support"][role].update(
                level="unresolved", evidence_ids=[], check_ids=[],
                reasoning="Caller contract was not supplied.", next_check="Read the caller contract.")
        self.assertEqual(validator.validate(record), [])
        record["findings"][0]["claim_support"]["defect"]["level"] = "unresolved"
        self.assertTrue(validator.validate(record))

    def test_link_validation_cannot_establish_truth_or_correct_prose(self):
        record = supported_record()
        record["findings"][0]["consequence"] = "Unrelated catastrophe asserted without evidence."
        # Structural acceptance is deliberately not an entailment verdict.
        self.assertEqual(validator.validate(record), [])

    def test_nested_bad_field_types_return_errors_without_crashing(self):
        for field in supported_record()["findings"][0]["claim_support"]["defect"]:
            for value in (None, [], {}, True, 12, ""):
                record = supported_record()
                record["findings"][0]["claim_support"]["defect"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertIsInstance(validator.validate(record), list)

    def test_archived_v2_requires_explicit_legacy_and_keeps_coverage_checks(self):
        record = supported_record()
        record["version"] = 2
        del record["findings"][0]["claim_support"]
        self.assertTrue(validator.validate(record))
        self.assertEqual(validator.validate(record, allow_legacy=True), [])
        invalid = copy.deepcopy(record)
        invalid["checks"] = []
        self.assertTrue(validator.validate(invalid, allow_legacy=True))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"
            path.write_text(json.dumps(record))
            result = subprocess.run([sys.executable, "-B", validator.__file__, str(path), "--allow-legacy"],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["validation_scope"], "legacy_structure_only")


if __name__ == "__main__":
    unittest.main()
