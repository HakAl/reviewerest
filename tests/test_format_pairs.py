"""Scope movement controls and paired scoring; no model account required."""

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import format_pairs as experiment


def fixture_answers():
    suite = experiment.SUITE
    manifest, _, packets = experiment.grader.inputs(suite)
    labels = experiment.grader.read(suite / "expectations.json")["cases"]
    result = {"protocol_sha256": manifest["files"]["protocol.json"],
              "packet_sha256": {i:manifest["files"]["packets/" + i + ".json"] for i in packets},
              "assessor": {"model": "fixture-model", "cli_version": "fixture"}, "grades": {}}
    for ident, packet in packets.items():
        sources = {a["source"]:a["text"].splitlines() for a in packet["artifacts"]}
        line = next(i for i,text in enumerate(sources["readiness.json"], 1) if '"authority_service"' in text)
        result["grades"][ident] = {"packet_id": ident, "target_condition": packet["target_condition"],
            "outcome": labels[ident]["outcome"], "reason": "Controlled fixture judgment.", "citations": [
                {"source": "review.md", "start_line": 1, "end_line": 1, "quote": sources["review.md"][0]},
                {"source": "readiness.json", "start_line": line, "end_line": line, "quote": '"authority_service": "not_checked"'}]}
    return result


class FormatPairTests(unittest.TestCase):
    def test_published_comparison_reproduces_and_receipt_hashes_match(self):
        suite = experiment.SUITE
        receipt = experiment.grader.read(suite / "receipt-01.json")
        runs = {}
        for run in receipt["runs"]:
            path = suite / run["answers_file"]
            self.assertEqual(experiment.grader.host.digest(path.read_bytes()), run["answers_sha256"])
            runs[path.name] = experiment.grader.read(path)
        path = suite / receipt["comparison_file"]
        self.assertEqual(experiment.grader.host.digest(path.read_bytes()), receipt["comparison_sha256"])
        self.assertEqual(experiment.compare(suite, runs), experiment.grader.read(path))

    def test_only_scope_position_changes_with_identical_json_values(self):
        design, packets = experiment.validate_design(experiment.SUITE)
        self.assertEqual(design["planned_assessments"], 8)
        for pair in design["pairs"]:
            original = next(a["text"] for a in packets[pair["original"]]["artifacts"] if a["source"] == "readiness.json")
            moved = next(a["text"] for a in packets[pair["moved"]]["artifacts"] if a["source"] == "readiness.json")
            self.assertEqual(json.loads(original), json.loads(moved))
            self.assertIn('"authority_service"', original.splitlines()[4])
            self.assertIn('"authority_service"', moved.splitlines()[3])
            self.assertIn('"scope"', moved.splitlines()[6])
            self.assertFalse(moved.splitlines()[6].endswith(','))
            self.assertTrue(moved.splitlines()[5].endswith(','))

    def test_altered_review_refused_even_if_manifest_is_rehashed(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / "suite"
            shutil.copytree(experiment.SUITE, suite)
            path = suite / "packets/p14.json"
            packet = experiment.grader.read(path)
            next(a for a in packet["artifacts"] if a["source"] == "review.md")["text"] += "Changed meaning."
            experiment.grader.host.save(path, packet)
            manifest = experiment.grader.read(suite / "manifest.json")
            manifest["files"]["packets/p14.json"] = experiment.grader.host.digest(path.read_bytes())
            experiment.grader.host.save(suite / "manifest.json", manifest)
            with self.assertRaisesRegex(ValueError, "exact scope-position"):
                experiment.validate_design(suite)

    def test_stale_logical_line_cannot_mask_verdict_flip(self):
        first, second = fixture_answers(), fixture_answers()
        grade = second["grades"]["p14"]
        grade["outcome"] = "fail"
        grade["citations"][1].update(start_line=5, end_line=5)
        result = experiment.compare(experiment.SUITE, {"one": first, "two": second})
        self.assertEqual(result["changed_raw_verdict_pairs"], 1)
        row = next(r for r in result["pairs"] if r["run"] == "two" and r["base"] == "p42")
        self.assertFalse(row["same_raw_verdict"])
        self.assertFalse(row["moved"]["citations_resolve"])
        self.assertEqual(result["citation_counts_by_arm"]["moved"]["invalid_citation_answers"], 1)

    def test_missing_answer_keeps_eight_planned_observations(self):
        first, second = fixture_answers(), fixture_answers()
        del second["grades"]["p68"]
        result = experiment.compare(experiment.SUITE, {"one": first, "two": second})
        self.assertEqual(result["planned_assessments"], 8)
        self.assertEqual(result["unknown_raw_verdict_pairs"], 1)
        self.assertEqual(result["citation_counts_by_arm"]["moved"]["missing_citation_answers"], 1)

    def test_mismatched_recorded_host_is_exposed(self):
        first, second = fixture_answers(), fixture_answers()
        second["assessor"]["model"] = "other-model"
        self.assertFalse(experiment.compare(experiment.SUITE, {"one": first, "two": second})["same_recorded_model_and_cli"])

    def test_citation_failure_retains_both_planned_batches_without_repair(self):
        def batch(suite, output, cli, budget, total, timeout):
            output.mkdir()
            self.assertEqual((budget, total, timeout), (.5, 2, 120))
            answers = fixture_answers()
            if output.name == "run-01":
                answers["grades"]["p14"]["citations"][1].update(start_line=5, end_line=5)
            experiment.grader.host.save(output / "answers.json", answers)
            experiment.grader.host.save(output / "summary.json", [{"eligible": True}] * 4)
            return 4 if output.name == "run-01" else 0
        with tempfile.TemporaryDirectory() as temp, patch.object(experiment.grader, "run", side_effect=batch) as mocked:
            output = Path(temp) / "out"
            self.assertEqual(experiment.run(experiment.SUITE, output, "unused"), 4)
            self.assertEqual(mocked.call_count, 2)
            self.assertTrue((output / "answers-02.json").exists())
            retained = experiment.grader.read(output / "answers-01.json")
            self.assertEqual(retained["grades"]["p14"]["citations"][1]["start_line"], 5)

    def test_ineligible_first_batch_stops_further_spending(self):
        def batch(suite, output, *args):
            output.mkdir()
            experiment.grader.host.save(output / "answers.json", fixture_answers())
            experiment.grader.host.save(output / "summary.json", [{"eligible": False}])
            return 4
        with tempfile.TemporaryDirectory() as temp, patch.object(experiment.grader, "run", side_effect=batch) as mocked:
            output = Path(temp) / "out"
            self.assertEqual(experiment.run(experiment.SUITE, output, "unused"), 4)
            self.assertEqual(mocked.call_count, 1)
            self.assertFalse((output / "run-02").exists())


if __name__ == "__main__":
    unittest.main()
