"""Adjudication handoff boundaries, source fidelity and neutral output shape."""

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import adjudication_packet as packet


class AdjudicationPacketTests(unittest.TestCase):
    def test_export_works_without_coordinator_and_contains_only_phase_one(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / 'suite'
            shutil.copytree(packet.SUITE / 'phase1', suite / 'phase1')
            destination = Path(temp) / 'export'
            packet.export(suite, destination)
            manifest, _ = packet.phase_one(suite)
            files = {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(files, set(manifest['files']) | {'manifest.json', 'START-HERE.md'})
            text = (destination / 'START-HERE.md').read_text()
            for hidden in ('required_lenses', 'forbidden_lenses', 'semantic_expectation', 'historical_label', 'original_case_id'):
                self.assertNotIn(hidden, text)
            with self.assertRaises(FileExistsError):
                packet.export(suite, destination)

    def test_source_packets_preserve_original_decoded_content_except_alias(self):
        selection = packet.grader.read(packet.SUITE / 'coordinator/selection.json')
        for entry in selection['entries']:
            source = ROOT / entry['source_path']
            self.assertEqual(packet.grader.host.digest(source.read_bytes()), entry['source_sha256'])
            original = packet.grader.read(source)
            del original['case_id']
            actual = packet.grader.read(packet.SUITE / entry['phase1_path'])
            self.assertEqual(actual.pop('id'), entry['id'])
            self.assertEqual(actual, original)
        pilot = [e for e in selection['entries'] if e['role'] == 'pilot']
        self.assertEqual(len(pilot), 6)
        self.assertFalse({e['original_case_id'] for e in pilot} & {'08', '19', '20', '24'})
        self.assertEqual(sum(e['selection_reason'] == 'clean candidate' for e in pilot), 2)
        self.assertEqual(selection['candidate_review_calls_if_approved'], len(pilot) * 2 * 3)

    def test_artifact_directive_cannot_close_bundle_boundary(self):
        text = packet.bundle(packet.SUITE)
        parts = text.split('\n<artifact_content>\n')[1:]
        self.assertEqual(len(parts), 9)
        _, originals = packet.phase_one(packet.SUITE)
        for part, original in zip(parts, originals):
            encoded = part.split('\n</artifact_content>', 1)[0]
            self.assertNotIn('<', encoded)
            self.assertNotIn('>', encoded)
            self.assertEqual(json.loads(encoded), original)

    def test_input_drift_and_path_shaped_alias_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temp:
            suite = Path(temp) / 'suite'
            shutil.copytree(packet.SUITE / 'phase1', suite / 'phase1')
            path = suite / 'phase1/protocol.md'
            path.write_text(path.read_text() + '\nChanged criteria.\n')
            with self.assertRaisesRegex(ValueError, 'Frozen phase-one'):
                packet.export(suite, Path(temp) / 'export')
            self.assertFalse((Path(temp) / 'export').exists())
            manifest = packet.grader.read(suite / 'phase1/manifest.json')
            manifest['case_ids'][0] = '../coordinator/labels'
            packet.grader.host.save(suite / 'phase1/manifest.json', manifest)
            with self.assertRaisesRegex(ValueError, 'neutral'):
                packet.phase_one(suite)

    def test_candidate_schema_accepts_empty_and_checks_bounds_not_truth(self):
        case = packet.phase_one(packet.SUITE)[1][0]
        packet.validate_candidate({'findings': []}, case)
        finding = {'finding': 'Synthetic claim', 'claim': 'This assertion is not checked for truth.',
                   'severity': 'unrated', 'location': [{'source': 'plan.md', 'start_line': 1, 'end_line': 1}]}
        packet.validate_candidate({'findings': [finding]}, case)
        finding['location'][0]['end_line'] = 999
        with self.assertRaisesRegex(ValueError, 'Location'):
            packet.validate_candidate({'findings': [finding]}, case)

    def test_candidate_metadata_is_rejected_without_rewriting_claim_text(self):
        case = packet.phase_one(packet.SUITE)[1][0]
        item = {'finding': 'Title', 'claim': 'Exact original wording.', 'severity': 'unrated',
                'location': [{'source': 'plan.md', 'start_line': 1, 'end_line': 1}]}
        for value in ({'findings': [item], 'provenance': {'arm': 'on'}},
                      {'findings': [dict(item, lenses=['correctness'])]},
                      {'findings': [dict(item, coverage_limits='reveals format')]}):
            saved = copy.deepcopy(value)
            with self.assertRaises(ValueError):
                packet.validate_candidate(value, case)
            self.assertEqual(value, saved)

    def test_published_adjudication_reproduces_receipt_without_certifying_truth(self):
        record = packet.grader.read(packet.SUITE / 'initial-01.json')
        receipt = packet.grader.read(packet.SUITE / 'initial-receipt-01.json')
        result = packet.validate_adjudication(record, packet.SUITE)
        self.assertEqual(result, receipt['mechanical_validation'])
        self.assertEqual(result['case_count'], 9)
        self.assertEqual(result['resolving_evidence_quotes'], 26)
        self.assertFalse(result['substantive_truth_verified'])
        for name, digest in receipt['public_artifact_sha256'].items():
            self.assertEqual(packet.grader.host.digest((packet.SUITE / name).read_bytes()), digest)
        record['cases'][0]['reference_findings'][0]['claim'] = 'An unsupported assertion with valid locations.'
        self.assertTrue(packet.validate_adjudication(record, packet.SUITE)['valid'])

    def test_adjudication_rejects_missing_duplicate_unfinished_and_drifted_records(self):
        original = packet.grader.read(packet.SUITE / 'initial-01.json')
        for kind in ('missing', 'duplicate', 'unfinished', 'manifest', 'empty_defect', 'boolean_version'):
            value = copy.deepcopy(original)
            if kind == 'missing':
                value['cases'].pop()
            elif kind == 'duplicate':
                value['cases'][1]['id'] = value['cases'][0]['id']
            elif kind == 'unfinished':
                value['cases'][0]['status'] = 'unfilled'
            elif kind == 'manifest':
                value['phase1_manifest_sha256'] = '0' * 64
            elif kind == 'empty_defect':
                value['cases'][0]['reference_findings'] = []
            else:
                value['version'] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                packet.validate_adjudication(value, packet.SUITE)

    def test_adjudication_rejects_fabricated_and_mislocated_evidence(self):
        for kind in ('quote', 'line', 'source'):
            value = packet.grader.read(packet.SUITE / 'initial-01.json')
            cite = value['cases'][0]['located_evidence'][0]
            if kind == 'quote':
                cite['quote'] = 'This sentence is absent from the source.'
            elif kind == 'line':
                cite['start_line'] = cite['end_line'] = 2
            else:
                cite['source'] = 'absent.md'
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'quote does not resolve'):
                packet.validate_adjudication(value, packet.SUITE)


if __name__ == '__main__':
    unittest.main()
