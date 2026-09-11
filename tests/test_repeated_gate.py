"""Exercise the gate with controlled receipts; no model account is used."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_review_records import supported_record

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import run_repeated as repeat
import repeated_gate as gate


def inputs():
    policy = {"repetitions": 3, "confirmed_failures_to_fail": 1,
              "cases": {c: {"conditions": ["authority"]} for c in ("47", "48")}}
    observed = {i["id"]: {"status": "eligible", "model": "fixture", "record_sha256": i["id"]}
                for i in repeat.plan(policy)}
    grades = {"policy_sha256": "policy", "trials": {
        i["id"]: {"record_sha256": i["id"], "assessor": {"identity": "fixture assessor", "prior_exposure": "Known labels."},
                  "conditions": {"authority": {"outcome": "pass", "reason": "Controlled judgment.", "evidence_refs": ["source:1"]}}}
        for i in repeat.plan(policy)}}
    calibration = {"policy_sha256": "policy", "approved": True, "independent": True,
                   "reviewed_by": "fixture calibrator", "evidence_ref": "fixture-calibration"}
    return policy, observed, grades, calibration


class RepeatedGateTests(unittest.TestCase):
    def test_fixed_denominator_and_alternating_case_order(self):
        policy, *_ = inputs()
        self.assertEqual([i["id"] for i in repeat.plan(policy)],
                         ["r01-47", "r01-48", "r02-48", "r02-47", "r03-47", "r03-48"])

    def test_behavior_pass_does_not_bypass_calibration(self):
        p, obs, grades, calibration = inputs()
        result = gate.decide(p, "policy", obs, grades)
        self.assertEqual(result["observed_behavior"], "pass")
        self.assertEqual(result["decision"], "inconclusive")
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "pass")
        calibration["policy_sha256"] = "another policy"
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "inconclusive")

    def test_missing_attempt_is_not_dropped_from_denominator(self):
        p, obs, grades, calibration = inputs()
        del obs["r02-47"]
        result = gate.decide(p, "policy", obs, grades, calibration)
        self.assertEqual(result["planned_trials"], 6)
        self.assertEqual(result["trial_counts"], {"pass": 5, "fail": 0, "inconclusive": 1})
        self.assertEqual(result["decision"], "inconclusive")

    def test_one_confirmed_failure_blocks_without_majority_voting(self):
        p, obs, grades, calibration = inputs()
        claim = grades["trials"]["r01-47"]["conditions"]["authority"]
        claim.update(outcome="fail", confirmation={"by": "fixture adjudicator", "reference": "counterexample"})
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "fail")
        p["confirmed_failures_to_fail"] = 2
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "inconclusive")
        grades["trials"]["r03-47"]["conditions"]["authority"] = copy.deepcopy(claim)
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "fail")

    def test_disputed_failure_and_model_drift_cannot_pass(self):
        p, obs, grades, calibration = inputs()
        grades["trials"]["r01-47"]["conditions"]["authority"]["outcome"] = "fail"
        self.assertEqual(gate.decide(p, "policy", obs, grades, calibration)["decision"], "inconclusive")
        p, obs, grades, calibration = inputs()
        obs["r01-47"]["model"] = "different fixture model"
        result = gate.decide(p, "policy", obs, grades, calibration)
        self.assertTrue(result["model_drift"])
        self.assertEqual(result["decision"], "inconclusive")

    def test_stale_assessment_and_omitted_condition_are_rejected(self):
        for error in ("digest", "condition"):
            p, obs, grades, calibration = inputs()
            trial = grades["trials"]["r01-47"]
            if error == "digest":
                trial["record_sha256"] = "old response"
            else:
                trial["conditions"] = {}
            with self.subTest(error=error), self.assertRaises(ValueError):
                gate.decide(p, "policy", obs, grades, calibration)

    def make_fixture(self, root):
        shutil.copytree(ROOT / "review", root / "review")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "--allow-empty", "-qm", "fixture"], check=True)
        packet = {"case_id": "47", "capabilities": {"specialist_references": True}, "artifacts": []}
        raw = gate.encoded(packet)
        (root / "case.json").write_bytes(raw)
        policy = {"version": 1, "repetitions": 2, "confirmed_failures_to_fail": 1,
                  "cases": {"47": {"file": "case.json", "sha256": repeat.runner.digest(raw), "conditions": ["authority"]}}}
        (root / "policy.json").write_bytes(gate.encoded(policy))
        cli = root / "fake-cli"
        body = '''import json,sys
from pathlib import Path
if '--version' in sys.argv:
    print('2.1.268 (fixture)'); raise SystemExit(0)
record = json.loads(RECORD)
record['provenance'] = json.loads(Path('review-context.json').read_text())
body = Path('reviewerest-plugin/skills/review/SKILL.md').read_text().split('---',2)[-1].strip()
events = [
 {'type':'system','subtype':'init','model':'fixture-model','claude_code_version':'2.1.268','tools':['Read','Glob','Grep','Skill'],'permissionMode':'dontAsk'},
 {'type':'assistant','message':{'content':[{'type':'tool_use','id':'load','name':'Skill','input':{'skill':'reviewerest-eval:review'}}]}},
 {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'load'},{'type':'text','text':body}]}},
 {'type':'result','is_error':False,'modelUsage':{'fixture-model':{}},'result':json.dumps(record)}]
for event in events: print(json.dumps(event))
'''.replace("RECORD", repr(json.dumps(supported_record())))
        cli.write_text("#!" + sys.executable + "\n" + body)
        cli.chmod(0o700)
        return cli

    def test_frozen_runner_round_trip_and_tampered_capture(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = self.make_fixture(root)
            with patch.object(repeat, "ROOT", root):
                self.assertEqual(repeat.run(root / "policy.json", root / "out", str(cli), 1, 2, 5), 0)
                with self.assertRaises(FileExistsError):
                    repeat.run(root / "policy.json", root / "out", str(cli), 1, 2, 5)
            _, _, observed = gate.inspect_run(root / "out", root / "policy.json")
            self.assertTrue(all(o["status"] == "eligible" for o in observed.values()), observed)
            cap = root / "out/r01-47/capture.json"
            data = gate.read(cap)
            data["stdout"] += "tampered"
            cap.write_bytes(gate.encoded(data))
            _, _, observed = gate.inspect_run(root / "out", root / "policy.json")
            self.assertEqual(observed["r01-47"]["status"], "unavailable")
            self.assertEqual(observed["r02-47"]["status"], "eligible")
            # A different version string that happens to be a prefix is still drift.
            cap = root / "out/r02-47/capture.json"
            data = gate.read(cap)
            data["stdout"] = data["stdout"].replace('"claude_code_version": "2.1.268"', '"claude_code_version": "2.1.26"')
            data["stdout_sha256"] = repeat.runner.digest(data["stdout"].encode())
            cap.write_bytes(gate.encoded(data))
            _, _, observed = gate.inspect_run(root / "out", root / "policy.json")
            self.assertEqual(observed["r02-47"]["status"], "unavailable")

    def test_over_budget_plan_never_invokes_cli_or_creates_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = self.make_fixture(root)
            with patch.object(repeat, "ROOT", root), self.assertRaises(ValueError):
                repeat.run(root / "policy.json", root / "out", str(cli), 1, 1, 5)
            self.assertFalse((root / "out").exists())

    def test_runtime_failure_stops_spend_and_retains_unfinished_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = self.make_fixture(root)
            cli.write_text("#!" + sys.executable + "\nimport sys\n"
                           "if '--version' in sys.argv:\n    print('2.1.268 (fixture)'); raise SystemExit(0)\n"
                           "print('fixture host unavailable'); raise SystemExit(1)\n")
            with patch.object(repeat, "ROOT", root):
                self.assertEqual(repeat.run(root / "policy.json", root / "out", str(cli), 1, 2, 5), 3)
            self.assertEqual(len(gate.read(root / "out/manifest.json")["schedule"]), 2)
            self.assertEqual(len(gate.read(root / "out/summary.json")), 1)
            self.assertTrue((root / "out/r01-47/capture.json").exists())
            self.assertFalse((root / "out/r02-47").exists())


if __name__ == "__main__":
    unittest.main()
