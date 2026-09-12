"""Long-source scope, exact-location controls and reproducible case construction."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import long_evidence as experiment


def fixture_answers():
    _, _, packets, design = experiment.inputs(experiment.SUITE)
    answers = {"input_manifest_sha256": experiment.grader.host.digest((experiment.SUITE / "manifest.json").read_bytes()), "trials": {}}
    for spec in design['schedule']:
        packet = packets[spec['packet_id']]
        sources = {a['source']: a['text'].splitlines() for a in packet['artifacts']}
        expected = experiment.oracle(packet)
        citations = [{'source': source, 'start_line': 1, 'end_line': 1, 'quote': sources[source][0]} for source in ('review.md', 'policy.md')]
        citations += [{'source': f['source'], 'start_line': f['line'], 'end_line': f['line'], 'quote': f['quote']} for f in expected['facts'].values()]
        grade = {'packet_id': packet['packet_id'], 'target_condition': 'readiness', 'outcome': expected['outcome'], 'reason': 'Controlled synthetic judgment.', 'citations': citations}
        answers['trials'][spec['id']] = dict(spec, eligible=True, model='fixture', cli_version='fixture', grade=grade)
    return answers


class LongEvidenceTests(unittest.TestCase):
    def test_published_comparison_reproduces_and_receipt_hashes_match(self):
        suite = experiment.SUITE
        receipt = experiment.grader.read(suite / 'receipt-01.json')
        answers_path = suite / receipt['answers_file']
        comparison_path = suite / receipt['comparison_file']
        for path, key in ((answers_path, 'answers_sha256'), (comparison_path, 'comparison_sha256')):
            self.assertEqual(experiment.grader.host.digest(path.read_bytes()), receipt[key])
        self.assertEqual(experiment.compare(suite, experiment.grader.read(answers_path)),
                         experiment.grader.read(comparison_path))

    def test_build_is_byte_reproducible_and_labels_follow_actual_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / 'suite'
            experiment.build(suite)
            for name in experiment.grader.read(suite / 'manifest.json')['files']:
                self.assertEqual((suite / name).read_bytes(), (experiment.SUITE / name).read_bytes())
        _, _, packets, _ = experiment.inputs(experiment.SUITE)
        outcomes = [experiment.oracle(p)['outcome'] for p in packets.values()]
        self.assertEqual(outcomes.count('pass'), 2)
        self.assertEqual(outcomes.count('fail'), 2)
        for p in packets.values():
            facts = experiment.oracle(p)
            self.assertGreater(facts['ledger_lines'], 200)
            lines = next(a['text'].splitlines() for a in p['artifacts'] if a['source'] == 'readiness-ledger.json')
            for fact in facts['facts'].values():
                self.assertIn(fact['quote'], lines[fact['line'] - 1])

    def test_oracle_rejects_ambiguous_identity_and_changes_label_with_target_state(self):
        _, _, packets, _ = experiment.inputs(experiment.SUITE)
        p = copy.deepcopy(packets['p61'])
        a = next(a for a in p['artifacts'] if a['source'] == 'readiness-ledger.json')
        ledger = json.loads(a['text'])
        target = ledger['records'][3]
        self.assertEqual(experiment.oracle(p)['outcome'], 'fail')
        target['authority_service'] = 'verified'
        a['text'] = json.dumps(ledger, indent=2) + '\n'
        self.assertEqual(experiment.oracle(p)['outcome'], 'pass')
        ledger['records'].append(copy.deepcopy(target))
        a['text'] = json.dumps(ledger, indent=2) + '\n'
        with self.assertRaisesRegex(ValueError, 'Exactly one'):
            experiment.oracle(p)

    def test_wrong_record_quote_can_resolve_but_fails_scope(self):
        answers = fixture_answers()
        grade = answers['trials']['t01']['grade']
        packet = experiment.grader.inputs(experiment.SUITE)[2][grade['packet_id']]
        citation = next(c for c in grade['citations'] if '"byte_hash_revalidation"' in c['quote'])
        lines = next(a['text'].splitlines() for a in packet['artifacts'] if a['source'] == 'readiness-ledger.json')
        wrong = next(i for i, line in enumerate(lines, 1) if citation['quote'] in line and i != citation['start_line'])
        citation.update(start_line=wrong, end_line=wrong)
        experiment.grader.validate_grade(packet, grade)
        result = experiment.compare(experiment.SUITE, answers)
        row = result['rows'][0]
        self.assertTrue(row['citations_resolve'])
        self.assertFalse(row['exact_evidence_contract'])
        self.assertEqual(row['facts']['byte_hash_revalidation'], 'wrong_record_or_line')

    def test_broad_range_is_valid_legacy_citation_but_fails_new_contract(self):
        answers = fixture_answers()
        grade = answers['trials']['t01']['grade']
        c = grade['citations'][-2]
        c['start_line'] -= 1
        c['end_line'] += 1
        row = experiment.compare(experiment.SUITE, answers)['rows'][0]
        self.assertTrue(row['citations_resolve'])
        self.assertEqual(row['facts']['authority_service'], 'overbroad')
        self.assertFalse(row['admissible_label_match'])

    def test_missing_duplicate_invented_and_extra_ledger_citations_fail(self):
        for mutation, expected in [('missing', 'omitted'), ('duplicate', 'multiple'), ('fabricated', 'quote_does_not_resolve'), ('outside', 'invalid_location')]:
            with self.subTest(mutation=mutation):
                answers = fixture_answers()
                cites = answers['trials']['t01']['grade']['citations']
                cite = cites[-2]
                if mutation == 'missing': cites.remove(cite)
                if mutation == 'duplicate': cites.append(copy.deepcopy(cite))
                if mutation == 'fabricated': cite['quote'] += ' fabricated'
                if mutation == 'outside': cite.update(start_line=900, end_line=900)
                row = experiment.compare(experiment.SUITE, answers)['rows'][0]
                self.assertEqual(row['facts']['authority_service'], expected)
                self.assertFalse(row['exact_evidence_contract'])
        answers = fixture_answers()
        cites = answers['trials']['t01']['grade']['citations']
        cites.append({'source':'readiness-ledger.json', 'start_line':1, 'end_line':1, 'quote':'{'})
        self.assertFalse(experiment.compare(experiment.SUITE, answers)['rows'][0]['exact_evidence_contract'])

    def test_citation_failure_does_not_mask_verdict_flip_or_missing_trial(self):
        answers = fixture_answers()
        grade = answers['trials']['t02']['grade']
        grade['outcome'] = 'pass'
        grade['citations'][-2]['start_line'] = 999
        del answers['trials']['t03']
        result = experiment.compare(experiment.SUITE, answers)
        self.assertEqual(result['planned'], 24)
        self.assertEqual(result['changed_raw_verdict_pairs'], 1)
        self.assertEqual(result['unknown_raw_verdict_pairs'], 1)
        self.assertEqual(sum(a['planned_facts'] for a in result['arms'].values()), 144)

    def test_schedule_reverses_each_packets_first_arm_between_rounds(self):
        _, _, packets, design = experiment.inputs(experiment.SUITE)
        first = []
        for i in range(0, 24, 2):
            a, b = design['schedule'][i:i+2]
            self.assertEqual((a['round'], a['packet_id']), (b['round'], b['packet_id']))
            self.assertNotEqual(a['arm'], b['arm'])
            first.append(a)
        for ident in packets:
            arms = [t['arm'] for t in first if t['packet_id'] == ident]
            self.assertNotEqual(arms[0], arms[1])
            self.assertNotEqual(arms[1], arms[2])

    def test_paired_prompts_hold_identity_sources_and_instructions_constant(self):
        _, protocol, packets, _ = experiment.inputs(experiment.SUITE)
        for packet in packets.values():
            plain = experiment.numbered.prompt(protocol, packet, 'plain')
            numbered = experiment.numbered.prompt(protocol, packet, 'numbered')
            stripped = '\n'.join('| ' + row.split(' | ', 1)[1] if ' | ' in row and row.split(' | ', 1)[0].isdigit() else row for row in numbered.splitlines()) + '\n'
            self.assertEqual(plain, stripped)
            self.assertNotIn('"ready":', plain)
            self.assertNotIn('"facts":', plain)

    def test_shared_runner_snapshots_extension_and_stops_on_host_failure(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(experiment.numbered.subprocess, 'check_output', side_effect=['fixture CLI', 'frozen']), patch.object(experiment.grader.host, 'invoke', return_value=(b'', b'', 1, False, .1)) as invoke:
            dest = Path(temp) / 'out'
            code = experiment.numbered.run(experiment.SUITE, dest, 'unused', load_inputs=experiment.inputs, additional_sources=(Path(experiment.__file__),))
            self.assertEqual(code, 4)
            self.assertEqual(invoke.call_count, 1)
            self.assertEqual((dest / 'long_evidence.py').read_bytes(), Path(experiment.__file__).read_bytes())
            result = experiment.compare(experiment.SUITE, experiment.grader.read(dest / 'answers.json'))
            self.assertEqual((result['planned'], result['eligible_completed']), (24, 0))


if __name__ == '__main__':
    unittest.main()
