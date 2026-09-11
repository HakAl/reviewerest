"""Check controlled evidence changes and reproduce the fictional consumer probe."""

import hashlib
import json
from pathlib import Path
import unittest

SUITE = Path(__file__).resolve().parents[1] / "evals/claim-evidence-v1"


def packet(case):
    return json.loads((SUITE / "cases" / f"{case}.json").read_text())


class ClaimEvidenceTests(unittest.TestCase):
    def test_reconstruction_matches_in_both_authority_states(self):
        a, b = packet("47"), packet("48")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][:-1], b["artifacts"][:-1])
        receipts = []
        for p in (a, b):
            candidate = json.loads(p["artifacts"][2]["text"])
            # Reconstruction validates bytes identically regardless of authority state.
            rebuilt = hashlib.sha256(candidate["payload"].encode()).hexdigest()
            self.assertEqual(rebuilt, candidate["sha256"])
            receipt = json.loads(p["artifacts"][-1]["text"])
            self.assertEqual(rebuilt, receipt["sha256"])
            receipts.append(receipt)
        self.assertEqual(receipts[0].pop("authority_service"), "not_checked")
        self.assertEqual(receipts[1].pop("authority_service"), "verified")
        self.assertEqual(receipts[0], receipts[1])

    def test_consumer_probe_accepts_payload_with_mismatched_digest(self):
        a, b = packet("49"), packet("50")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][:2], b["artifacts"][:2])
        namespace = {}
        exec(b["artifacts"][2]["text"], namespace)
        probe = json.loads(b["artifacts"][3]["text"])
        candidate = probe["input"]
        self.assertNotEqual(hashlib.sha256(candidate["payload"].encode()).hexdigest(),
                            candidate["digest_of_original"])
        actual = namespace["consume"](candidate)
        self.assertEqual(actual, probe["actual"])
        self.assertNotEqual(actual, probe["expected"])
        # This reproduces acceptance only; there is no signer to exercise.
        self.assertNotIn("sign", namespace)

    def test_current_preflight_changes_without_erasing_historical_failure(self):
        a, b = packet("51"), packet("52")
        self.assertEqual(a["request"], b["request"])
        self.assertEqual(a["artifacts"][:-1], b["artifacts"][:-1])
        absent = json.loads(a["artifacts"][-1]["text"])
        current = json.loads(b["artifacts"][-1]["text"])
        historical = json.loads(a["artifacts"][2]["text"])
        self.assertEqual(absent["preflight"], "not_run")
        self.assertEqual(current["preflight"], "pass")
        self.assertEqual(current["readback"], current["expected"])
        self.assertEqual(current["worker"], historical["worker"])
        self.assertNotEqual(current["sandbox"], historical["sandbox"])

    def test_packets_are_label_free_and_rubric_covers_each_case_once(self):
        rubric = json.loads((SUITE / "rubric.json").read_text())
        expected = [f"{n}" for n in range(47, 53)]
        self.assertEqual(sorted(c for pair in rubric["pairs"] for c in pair["cases"]), expected)
        for case in expected:
            p = packet(case)
            self.assertEqual(p["case_id"], case)
            self.assertFalse({"pass_conditions", "expected_findings", "rubric"} & p.keys())
            self.assertFalse(p["capabilities"]["artifact_execution"])


if __name__ == "__main__":
    unittest.main()
