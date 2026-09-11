"""Validate paired fixture controls and bounded scoring, not model judgment."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_records import supported_record

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/calibration-v1"
spec = importlib.util.spec_from_file_location("check_results", ROOT / "evals/check_results.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def packet(case):
    return json.loads((SUITE / "cases" / (case + ".json")).read_text())


class CalibrationTests(unittest.TestCase):
    def test_runner_rejects_mislabeled_packet_before_invoking_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "27.json").write_text(json.dumps(packet("28")))
            result = subprocess.run([sys.executable, "-B", str(ROOT / "evals/run_claude.py"),
                                     "--case-dir", str(directory), "--cases", "27",
                                     "--output", str(directory / "output"), "--cli", "absent-fixture-cli"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("case_id must match", result.stderr)
            self.assertFalse((directory / "output").exists())

    def test_command_pair_changes_bytes_only_in_write_variant(self):
        for case,expected_bytes in [("27", b"different\n"), ("28", b"stable\n")]:
            source = packet(case)["artifacts"][1]["text"]
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / "verify.py").write_text(source)
                fixtures = root / "fixtures"
                fixtures.mkdir()
                (fixtures / "expected.txt").write_bytes(b"different\n")
                result = subprocess.run([sys.executable, "-B", str(root / "verify.py"),
                                         "--out", str(fixtures)], capture_output=True)
                self.assertEqual(result.returncode, 1)
                self.assertEqual((fixtures / "expected.txt").read_bytes(), expected_bytes)
                self.assertEqual([p.name for p in fixtures.iterdir()], ["expected.txt"])

    def test_pair_inputs_hold_unrelated_factors_constant(self):
        a,b = packet("27"),packet("28")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][0], b["artifacts"][0])
        altered = b["artifacts"][1]["text"].replace('    (out / "expected.txt").write_text(expected)\n', '')
        self.assertEqual(a["artifacts"][1]["text"], altered)
        a,b = packet("29"),packet("30")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"], b["artifacts"][:-1])
        a,b = packet("31"),packet("32")
        self.assertNotEqual(a["request"], b["request"])
        for p in (a,b):
            p.pop("case_id")
            p.pop("request")
        self.assertEqual(a,b)

    def test_added_mapping_evidence_supports_specific_canceled_result(self):
        namespace = {}
        exec(packet("30")["artifacts"][-1]["text"], namespace)
        self.assertEqual(namespace["label"]("canceled"), "Running")
        self.assertEqual(namespace["label"]("success"), "Done")
        self.assertEqual(namespace["label"]("failed"), "Failed")

    def test_scorer_detects_count_and_severity_without_claiming_truth(self):
        expected = {c["case_id"]:c for c in json.loads((SUITE / "expectations.json").read_text())["cases"]}
        report = supported_record()
        # Valid structure but an unrelated arithmetic finding: semantic review is still required.
        result = checker.assess([{"case_id":"28", "review":report}], {"28":expected["28"]})
        self.assertEqual(result["results"][0]["fixture_contract_errors"], [])
        self.assertFalse(result["substantive_truth_verified"])
        report["findings"][0]["severity"] = "blocker"
        result = checker.assess([{"case_id":"28", "review":report}], {"28":expected["28"]})
        self.assertTrue(result["results"][0]["fixture_contract_errors"])
        result = checker.assess([{"case_id":"27", "review":report}], {"27":expected["27"]})
        self.assertTrue(result["results"][0]["fixture_contract_errors"])
        missing = checker.assess([], expected)
        self.assertEqual(missing["missing_cases"], ["27","28","29","30","31","32"])

    def test_cli_uses_selected_suite_and_returns_failure_for_unmet_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            records = Path(temp) / "records.json"
            records.write_text(json.dumps([{"case_id":"27", "review":supported_record()}]))
            command = [sys.executable, "-B", str(ROOT / "evals/check_results.py"), str(records),
                       "--expectations", str(SUITE / "expectations.json"), "--cases", "27"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["planned_cases"], ["27"])
            self.assertEqual(receipt["missing_cases"], [])
            self.assertTrue(receipt["results"][0]["fixture_contract_errors"])


if __name__ == "__main__":
    unittest.main()
