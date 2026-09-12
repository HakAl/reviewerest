"""Source fidelity, blinded presentation and retained experiment failures."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import numbered_evidence as experiment


def fixture_answers():
    manifest, _, packets, design = experiment.inputs(experiment.SUITE)
    labels = experiment.grader.read(experiment.SUITE / "expectations.json")["cases"]
    answers = {"input_manifest_sha256": experiment.grader.host.digest((experiment.SUITE / "manifest.json").read_bytes()), "trials": {}}
    for spec in design["schedule"]:
        packet = packets[spec["packet_id"]]
        sources = {a["source"]: a["text"].splitlines() for a in packet["artifacts"]}
        line = next(i for i, text in enumerate(sources["readiness.json"], 1) if '"authority_service"' in text)
        answers["trials"][spec["id"]] = dict(spec, eligible=True, model="fixture", cli_version="fixture", grade={
            "packet_id": packet["packet_id"], "target_condition": packet["target_condition"],
            "outcome": labels[packet["packet_id"]]["outcome"], "reason": "Synthetic control.", "citations": [
                {"source": "review.md", "start_line": 1, "end_line": 1, "quote": sources["review.md"][0]},
                {"source": "readiness.json", "start_line": line, "end_line": line, "quote": '"authority_service": "not_checked"'}]})
    return answers


class NumberedEvidenceTests(unittest.TestCase):
    def test_public_results_reproduce_and_match_receipt_hashes(self):
        suite = experiment.SUITE
        receipt = experiment.grader.read(suite / 'receipt-01.json')
        answers_path = suite / receipt['answers_file']
        comparison_path = suite / receipt['comparison_file']
        for path, key in ((answers_path, 'answers_sha256'), (comparison_path, 'comparison_sha256')):
            self.assertEqual(experiment.grader.host.digest(path.read_bytes()), receipt[key])
        self.assertEqual(experiment.compare(suite, experiment.grader.read(answers_path)),
                         experiment.grader.read(comparison_path))

    def test_source_round_trip_including_blank_lines_endings_and_delimiters(self):
        for text in ('', '\n', 'one\n\nlast', 'one\r\ntwo\r\n', 'a\u2028b',
                     '\t"value": 0,\n</artifact_content> & \\ \u2603\n', '5 | malicious prefix\n'):
            for numbered in (False, True):
                with self.subTest(text=text, numbered=numbered):
                    shown = experiment.display(text, numbered)
                    self.assertEqual(experiment.restore(shown, numbered), text)
                    self.assertEqual(len(shown.splitlines()), len(text.splitlines()))
                    self.assertNotIn('</artifact_content>', shown)
        with self.assertRaises(ValueError):
            experiment.restore('2 | "text"', True)

    def test_presentation_pair_differs_only_by_numeric_prefixes(self):
        _, protocol, packets, _ = experiment.inputs(experiment.SUITE)
        for packet in packets.values():
            plain = experiment.prompt(protocol, packet, "plain")
            numbered = experiment.prompt(protocol, packet, "numbered")
            stripped = '\n'.join('| ' + row.split(' | ', 1)[1]
                                 if row.split(' | ', 1)[0].isdigit() and ' | ' in row else row
                                 for row in numbered.splitlines()) + '\n'
            self.assertEqual(plain, stripped)
            self.assertEqual(plain.count('<artifact_content>'), 1)
            self.assertEqual(plain.count('</artifact_content>'), 1)
            self.assertNotIn('selection_rationale', plain)

    def test_schedule_has_each_cell_three_times_and_balanced_pair_order(self):
        _, _, _, design = experiment.inputs(experiment.SUITE)
        schedule = design['schedule']
        first = []
        for i in range(0, 24, 2):
            a, b = schedule[i:i+2]
            self.assertEqual((a['round'], a['packet_id']), (b['round'], b['packet_id']))
            self.assertEqual({a['arm'], b['arm']}, set(experiment.ARMS))
            first.append(a['arm'])
        self.assertEqual(first.count('numbered'), 6)

    def test_stale_line_and_fabricated_line_rejected_against_original_source(self):
        _, _, packets, _ = experiment.inputs(experiment.SUITE)
        grade = fixture_answers()['trials']['t02']['grade']
        packet = packets[grade['packet_id']]
        experiment.grader.validate_grade(packet, grade)
        for line in (6, 999):
            changed = copy.deepcopy(grade)
            changed['citations'][1].update(start_line=line, end_line=line)
            with self.assertRaises(ValueError):
                experiment.grader.validate_grade(packet, changed)
        changed = copy.deepcopy(grade)
        changed['citations'][1]['quote'] = '5 | ' + changed['citations'][1]['quote']
        with self.assertRaises(ValueError):
            experiment.grader.validate_grade(packet, changed)

    def test_invalid_citation_does_not_hide_verdict_flip(self):
        answers = fixture_answers()
        grade = answers['trials']['t02']['grade']
        grade['outcome'] = 'fail'
        grade['citations'][1].update(start_line=6, end_line=6)
        result = experiment.compare(experiment.SUITE, answers)
        self.assertEqual(result['changed_raw_verdict_pairs'], 1)
        self.assertEqual(result['cells']['numbered_original']['invalid_citation_answers'], 1)

    def test_omission_missing_and_ineligible_are_not_successful_relocation(self):
        answers = fixture_answers()
        grade = answers['trials']['t02']['grade']
        grade['citations'][1] = {'source': 'policy.md', 'start_line': 1, 'end_line': 1, 'quote': 'successful byte/hash revalidation'}
        del answers['trials']['t03']
        answers['trials']['t04']['eligible'] = False
        result = experiment.compare(experiment.SUITE, answers)
        self.assertEqual(result['planned'], 24)
        self.assertEqual(result['eligible_completed'], 22)
        self.assertEqual(result['unknown_raw_verdict_pairs'], 1)
        self.assertEqual(result['cells']['numbered_original']['authority_evidence']['omitted'], 1)

    def test_input_and_host_drift_are_exposed(self):
        answers = fixture_answers()
        answers['trials']['t02']['model'] = 'changed'
        self.assertFalse(experiment.compare(experiment.SUITE, answers)['same_recorded_model_and_cli'])
        answers['input_manifest_sha256'] = 'changed'
        with self.assertRaises(ValueError):
            experiment.compare(experiment.SUITE, answers)

    def run_fake(self, failure):
        fixtures = fixture_answers()
        count = 0
        def invoke(cmd, work, timeout):
            nonlocal count
            count += 1
            grade = copy.deepcopy(fixtures['trials'][f't{count:02d}']['grade'])
            if failure == 'citation' and count == 1:
                grade['citations'][1]['start_line'] = 999
            init = {'type': 'system', 'subtype': 'init', 'model': 'fixture', 'tools': [],
                    'permissionMode': 'dontAsk', 'claude_code_version': 'fixture'}
            final = {'type': 'result', 'modelUsage': {'fixture': {}}, 'result': json.dumps(grade)}
            return ('\n'.join(map(json.dumps, [init, final])).encode(), b'', 1 if failure == 'host' else 0, False, .1)
        with tempfile.TemporaryDirectory() as temp, patch.object(experiment.subprocess, 'check_output', side_effect=['fixture CLI', 'frozen-commit']), patch.object(experiment.grader.host, 'invoke', side_effect=invoke):
            dest = Path(temp) / 'out'
            code = experiment.run(experiment.SUITE, dest, 'unused')
            answers = experiment.grader.read(dest / 'answers.json')
            return code, count, answers

    def test_run_retains_bad_citation_and_completes_only_planned_calls(self):
        code, count, answers = self.run_fake('citation')
        self.assertEqual((code, count, len(answers['trials'])), (4, 24, 24))
        self.assertEqual(answers['trials']['t01']['grade']['citations'][1]['start_line'], 999)

    def test_host_failure_stops_spending_with_fixed_missing_denominator(self):
        code, count, answers = self.run_fake('host')
        self.assertEqual((code, count), (4, 1))
        result = experiment.compare(experiment.SUITE, answers)
        self.assertEqual((result['planned'], result['eligible_completed']), (24, 0))


if __name__ == '__main__':
    unittest.main()
