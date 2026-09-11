"""Executable correction oracles and quote-location controls for fictional cases."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals/review-quality-v1"
spec = importlib.util.spec_from_file_location("check_citations", ROOT / "evals/check_citations.py")
citations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(citations)


def packet(case):
    return json.loads((SUITE / "cases" / (case + ".json")).read_text())


class QualityEvalTests(unittest.TestCase):
    def test_patch_oracle_catches_lost_plural_and_accepts_valid_correction(self):
        oracle = json.loads((SUITE / "matcher-oracle.json").read_text())["checks"]
        errors = {}
        for case in ("39", "40"):
            namespace = {}
            exec(packet(case)["artifacts"][-1]["text"], namespace)
            errors[case] = [c["text"] for c in oracle
                            if namespace["matches"](c["text"]) is not c["expected"]]
        self.assertEqual(errors["39"], ["LLMs", "llms,", "LLMs: a survey"])
        self.assertEqual(errors["40"], [])

    def test_measurement_changes_frequency_not_possible_bug(self):
        a,b = packet("41"),packet("42")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][:2], b["artifacts"][:2])
        counts = []
        for p in (a,b):
            titles = json.loads(p["artifacts"][2]["text"])["titles"]
            measurement = json.loads(p["artifacts"][3]["text"])
            count = sum("bellman" in t.casefold() for t in titles)
            self.assertEqual(measurement["matching_titles"], count)
            self.assertEqual(measurement["total_titles"], len(titles))
            counts.append(count)
        self.assertEqual(counts, [0,3])
        namespace = {}
        exec(a["artifacts"][0]["text"], namespace)
        self.assertTrue(namespace["anchor_match"]("Bellman equation"))

    def evidence(self, **changes):
        item = {"id":"e1", "source":"protocol.txt", "revision":"synthetic-v1",
                "location":"lines 3-3", "quote":"Unknown parameters return badArgument.",
                "observation":"Therefore future dates are rejected."}
        item.update(changes)
        return {"evidence":[item]}

    def test_resolving_quote_does_not_establish_semantic_support(self):
        result = citations.assess(packet("43"), self.evidence(), require_quotes=True)
        self.assertTrue(result["valid"])
        self.assertFalse(result["semantic_support_verified"])
        self.assertEqual(result["checked_evidence"], [0])

    def test_wrong_line_revision_and_fabricated_quote_are_rejected(self):
        for change in [{"location":"lines 2-2"}, {"location":"lines 3-99"},
                       {"location":"lines 4-3"}, {"revision":"other"},
                       {"quote":"Future dates are always rejected."}, {"quote":""},
                       {"source":"../../outside.txt"}, {"location":{}}, {"source":[]}]:
            with self.subTest(change=change):
                self.assertFalse(citations.assess(packet("43"), self.evidence(**change))["valid"])

    def test_absent_quotes_are_not_silent_success(self):
        self.assertFalse(citations.assess(packet("43"), {"evidence":[]})["valid"])
        record = self.evidence()
        record["evidence"].append({"id":"e2"})
        self.assertEqual(citations.assess(packet("43"), record)["unchecked_evidence"], [1])
        self.assertFalse(citations.assess(packet("43"), record, require_quotes=True)["valid"])

    def test_cli_reports_quote_failure_without_changing_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / "record.json"
            command = [sys.executable, "-B", str(ROOT / "evals/check_citations.py"),
                       str(SUITE / "cases/43.json"), str(record), "--require-quotes"]
            for location, expected_exit in [("lines 3-3", 0), ("lines 2-2", 3)]:
                with self.subTest(location=location):
                    record.write_text(json.dumps(self.evidence(location=location)))
                    before = record.read_bytes()
                    result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, expected_exit, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["valid"], expected_exit == 0)
                    self.assertEqual(record.read_bytes(), before)

    def test_protocol_pair_changes_only_claim_support(self):
        a,b = packet("43"),packet("44")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][0], b["artifacts"][0])
        self.assertEqual(a["artifacts"][1]["text"].splitlines()[:3], b["artifacts"][1]["text"].splitlines()[:3])
        quote = b["artifacts"][1]["text"].splitlines()[3]
        self.assertTrue(citations.assess(b, self.evidence(location="lines 4-4", quote=quote))["valid"])
        self.assertFalse(citations.assess(a, self.evidence(location="lines 4-4", quote=quote))["valid"])

    def test_retry_pair_preserves_abort_while_exposing_missing_retries(self):
        a,b = packet("45"),packet("46")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][0], b["artifacts"][0])
        self.assertEqual(a["artifacts"][2], b["artifacts"][2])
        namespace = {}
        exec(a["artifacts"][2]["text"], namespace)
        action = namespace["next_action"]
        self.assertEqual(action(503,0,2), "retry")
        for status in (502,504):
            self.assertEqual(action(status,0,2), "abort_without_partial_output")
        for status in range(500,600):
            self.assertEqual(action(status,2,2), "abort_without_partial_output")


if __name__ == "__main__":
    unittest.main()
