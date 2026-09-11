"""Count explicit assessor judgments without hiding uncertainty or empty samples."""

import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("score_claims", Path(__file__).resolve().parents[1] / "evals/score_claims.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


def ledger():
    return {"version": 1, "assessor": {"identity": "fixture assessor", "prior_exposure": "Author knew labels."},
            "coverage": "Selected synthetic consequences only.", "claims": [
                {"id": str(i), "case_id": "47", "response_location": "findings[0].consequence",
                 "quote": "A synthetic claim.", "role": "consequence", "judgment": judgment,
                 "reason": "Synthetic grade for aggregation test.", "evidence_refs": ["fixture.txt:1"]}
                for i, judgment in enumerate(["supported", "overstated", "inconclusive"])]}


class ClaimScoringTests(unittest.TestCase):
    def test_denominators_exclude_inconclusive_but_keep_it_visible(self):
        result = scorer.summarize(ledger())
        count = result["by_role"]["consequence"]
        self.assertEqual(count["adjudicated"], 2)
        self.assertEqual(count["inconclusive"], 1)
        self.assertEqual(count["overstatement_rate"], 0.5)
        self.assertFalse(result["substantive_truth_verified"])

    def test_empty_sample_has_no_perfect_score(self):
        sample = ledger()
        sample["claims"] = []
        for count in scorer.summarize(sample)["by_role"].values():
            self.assertIsNone(count["overstatement_rate"])
            self.assertIsNone(count["support_rate"])

    def test_bad_judgment_duplicate_or_missing_attribution_fails(self):
        for change in ("judgment", "duplicate", "assessor", "coverage"):
            sample = ledger()
            if change == "judgment":
                sample["claims"][0]["judgment"] = "probably fine"
            elif change == "duplicate":
                sample["claims"].append(copy.deepcopy(sample["claims"][0]))
            else:
                sample.pop(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                scorer.summarize(sample)


if __name__ == "__main__":
    unittest.main()
