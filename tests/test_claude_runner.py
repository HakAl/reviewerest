"""Harness integrity checks; these do not simulate review quality."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_claude", ROOT / "evals/run_claude.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ClaudeRunnerTests(unittest.TestCase):
    def test_loading_requires_successful_exact_skill_and_rejects_substitution(self):
        call = {"id": "load", "name": "Skill", "input": {"skill": runner.EXPECTED_SKILL}}
        event = {"message": {"content": [{"type": "tool_result", "tool_use_id": "load"}]}}
        self.assertEqual(runner.loading_errors([call], [event]), [])
        self.assertTrue(runner.loading_errors([call], []))
        event["message"]["content"][0]["is_error"] = True
        self.assertTrue(runner.loading_errors([call], [event]))
        event["message"]["content"][0]["is_error"] = False
        other = {"id": "other", "name": "Skill", "input": {"skill": "code-review"}}
        self.assertTrue(runner.loading_errors([call, other], [event]))

    def test_record_extraction_does_not_repair_or_select_an_answer(self):
        for text in ['{"version":1}', '```json\n{"version":1}\n```']:
            self.assertEqual(runner.extract_record(text), {"version": 1})
        for text in ['Explanation\n{"version":1}', '{"version":1}\n{"version":2}', '[]']:
            with self.assertRaises(ValueError):
                runner.extract_record(text)

    def make_run(self, root, body, references=True):
        skill = root / "skill"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text("test skill\n")
        (skill / "references/report-contract.md").write_text("test contract\n")
        (skill / "references/security-boundaries.md").write_text("specialist reference\n")
        # A neighboring label file must not enter the candidate's project.
        (root / "expectations.json").write_text('{"secret_label":true}')
        cli = root / "fake-cli"
        cli.write_text("#!" + sys.executable + "\n" + body)
        cli.chmod(0o700)
        packet = {"case_id": "01", "capabilities": {"specialist_references": references},
                  "artifacts": [{"source": "code.py", "text": "original"}]}
        return runner.run_case(str(cli), packet, skill, root / "output", 1, 5)

    def test_zero_exit_auth_failure_is_not_a_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, record = self.make_run(root, 'print(\'{"type":"result",'
                                           '"is_error":false,"num_turns":0,'
                                           '"result":"Not logged in"}\')\n')
            self.assertEqual(receipt["exit_code"], 0)
            self.assertIsNone(record)
            self.assertIn("No model invocation", receipt["record_error"])
            self.assertTrue(receipt["workspace_unchanged"])
            self.assertIn("Not logged in", (root / "output/capture.json").read_text())

    def test_inputs_exclude_labels_and_unavailable_references(self):
        body = '''import json
from pathlib import Path
files = sorted(str(p) for p in Path('.').rglob('*') if p.is_file())
print(json.dumps({"type":"result", "num_turns":1, "modelUsage":{"fake":{}},
                  "result":json.dumps({"files":files})}))
'''
        with tempfile.TemporaryDirectory() as tmp:
            receipt, record = self.make_run(Path(tmp), body, references=False)
            self.assertEqual(record["files"], ["case.json",
                                             "review-context.json",
                                             "reviewerest-plugin/.claude-plugin/plugin.json",
                                             runner.SKILL_PATH + "/SKILL.md",
                                             runner.SKILL_PATH + "/references/report-contract.md"])
            self.assertTrue(receipt["workspace_unchanged"])

    def test_local_command_result_can_have_usage_with_zero_outer_turns(self):
        body = '''import json
print(json.dumps({"type":"result", "num_turns":0, "modelUsage":{"fake":{"outputTokens":1}},
                  "result":"{\\"version\\":1}"}))
'''
        with tempfile.TemporaryDirectory() as tmp:
            receipt, record = self.make_run(Path(tmp), body)
            self.assertIsNone(receipt["record_error"])
            self.assertEqual(record, {"version": 1})

    def test_workspace_writes_are_detected_even_with_valid_response(self):
        body = '''from pathlib import Path
import json
Path("approved.txt").write_text("unexpected")
print(json.dumps({"type":"result", "num_turns":1, "modelUsage":{"fake":{}},
                  "result":"{\\"version\\":1}"}))
'''
        with tempfile.TemporaryDirectory() as tmp:
            receipt, record = self.make_run(Path(tmp), body)
            self.assertEqual(record, {"version": 1})
            self.assertFalse(receipt["workspace_unchanged"])
            self.assertIn("approved.txt", receipt["after"])

    def test_timeout_preserves_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout, _, code, timed_out, _ = runner.invoke(
                [sys.executable, "-c", 'import time; print("started", flush=True); time.sleep(10)'],
                tmp, 0.2)
            self.assertTrue(timed_out)
            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, b"started\n")


if __name__ == "__main__":
    unittest.main()
