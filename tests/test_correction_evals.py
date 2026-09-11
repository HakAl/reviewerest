"""Check controlled differences and evidence oracles for fictional evals."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "evals/correction-v1"


def packet(case):
    return json.loads((ROOT / "cases" / (case + ".json")).read_text())


class CorrectionEvalTests(unittest.TestCase):
    def test_current_untracked_status_does_not_rule_out_git_recovery(self):
        # Added during baseline adjudication; frozen packets and labels are unchanged.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                       GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], env=env, stderr=subprocess.PIPE)
            git("init", "-b", "main")
            original = b"recoverable fictional harness\n"
            (root / "harness.py").write_bytes(original)
            git("add", "harness.py")
            git("commit", "-m", "Retain original fixture")
            revision = git("rev-parse", "HEAD").decode().strip()
            git("rm", "--cached", "harness.py")
            git("commit", "-m", "Stop tracking fixture")
            self.assertEqual(git("status", "--porcelain").decode().strip(), "?? harness.py")
            self.assertEqual(git("show", revision + ":harness.py"), original)

    def test_ownership_swap_changes_valid_destination_not_original_defect(self):
        first, second = packet("33"), packet("34")
        self.assertEqual(first["request"], second["request"])
        self.assertEqual(first["artifacts"][:2], second["artifacts"][:2])
        owners = []
        for p in (first, second):
            resources = json.loads(p["artifacts"][2]["text"])
            self.assertNotIn("destination_store", resources["Pack"])
            owners.append([name for name, values in resources.items() if "destination_store" in values])
        self.assertEqual(owners, [["Vault"], ["Relay"]])

    def test_acceptance_counterexample_changes_only_second_clause(self):
        first, second = packet("35"), packet("36")
        self.assertEqual(first["request"], second["request"])
        self.assertEqual(first["artifacts"][0], second["artifacts"][0])
        self.assertEqual(first["artifacts"][2], second["artifacts"][2])
        a, b = (p["artifacts"][1]["text"].splitlines() for p in (first, second))
        self.assertEqual(a[:-1], b[:-1])
        self.assertEqual(a[-1], "B. Every owner has accepted the same exact packet version.")
        self.assertEqual(b[-1], "B. Every recorded response refers to the same exact packet version, whether accepted or contested.")
        responses = list(json.loads(first["artifacts"][2]["text"]).values())
        recorded = all(r["status"] in {"accepted", "contested"} for r in responses)
        same_packet = len({r["packet"] for r in responses}) == 1
        unanimous = all(r["status"] == "accepted" for r in responses) and same_packet
        self.assertFalse(recorded and unanimous)
        self.assertTrue(recorded and same_packet)

    def test_unknown_copy_state_becomes_bounded_absence_only_with_inventory(self):
        first, second = packet("37"), packet("38")
        self.assertEqual(first["request"], second["request"])
        self.assertEqual(first["artifacts"], second["artifacts"][:-1])
        observation = json.loads(first["artifacts"][-1]["text"])
        self.assertEqual(set(observation), {"tracked_status", "path", "exists", "sha256", "recycle_executed"})
        self.assertFalse(observation["recycle_executed"])
        inventory = json.loads(second["artifacts"][-1]["text"])
        self.assertEqual(set(inventory["locations"]), {"scratch", "archive", "backup"})
        self.assertEqual(inventory["locations"]["archive"], [])
        self.assertEqual(inventory["locations"]["backup"], [])
        original = inventory["locations"]["scratch"][0]
        self.assertEqual(original["sha256"], observation["sha256"])
        self.assertTrue(original["recoverable"])

    def test_suite_inventory_has_no_label_fields_in_candidate_packets(self):
        expectations = json.loads((ROOT / "expectations.json").read_text())
        rubric = json.loads((ROOT / "rubric.json").read_text())
        ids = {c["case_id"] for c in expectations["cases"]}
        self.assertEqual(ids, {"33", "34", "35", "36", "37", "38"})
        self.assertEqual(ids, {c for pair in rubric["pairs"] for c in pair["cases"]})
        for case in ids:
            self.assertEqual(set(packet(case)), {"case_id", "request", "mode", "capabilities", "context", "artifacts"})
        self.assertTrue(all("allowed_severities" not in c for c in expectations["cases"]))


if __name__ == "__main__":
    unittest.main()
