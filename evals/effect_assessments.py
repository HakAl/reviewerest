#!/usr/bin/env python3
"""Blinded assessor handoff, declared-provenance Gemini capture and offline counts."""

import argparse
from collections import Counter
import json
from pathlib import Path
import secrets
import tempfile

import effect_candidates as candidate
import run_claude as host

ROOT, SUITE = candidate.ROOT, candidate.SUITE
read, sha = candidate.read, candidate.sha
CLASSES = ('supported_defect', 'secondary_observation', 'neutral', 'unsupported', 'out_of_scope', 'mixed', 'unresolved')


def inputs():
    candidate.pinned(SUITE / 'assessor-manifest.json')
    criteria = read(ROOT / read(SUITE / 'plan.json')['criteria_path'])
    return criteria


def loaded_run(run_dir):
    _, plan, cases = candidate.inputs()
    state = read(run_dir / 'run.json')
    if state['manifest_sha256'] != sha(SUITE / 'candidate-manifest.json') or state['schedule'] != plan['schedule']:
        raise ValueError('Candidate run belongs to a different frozen plan.')
    rows = {}
    schedule = {t['trial_id']: t for t in plan['schedule']}
    for ident, digest in state['trials'].items():
        if ident not in schedule:
            raise ValueError('Unscheduled trial.')
        path = run_dir / ident / 'trial.json'
        if sha(path) != digest:
            raise ValueError('Candidate trial changed.')
        row = read(path)
        if row['trial'] != schedule[ident]:
            raise ValueError('Candidate trial metadata changed.')
        for stream in ('stdout', 'stderr'):
            if sha(run_dir / ident / (stream + '.bin')) != row[stream + '_sha256']:
                raise ValueError('Raw candidate capture changed.')
        rows[ident] = row
    return plan, cases, rows


def make_packet(ident, case, criteria, record):
    candidate.shape(record)  # No projection or selective removal of metadata.
    return {'assessment_id': ident, 'case': case,
            'criteria': {'criteria_id': criteria['criteria_id'], 'rules': criteria['rules'],
                         'case': next(c for c in criteria['cases'] if c['id'] == case['id'])},
            'candidate': record, 'entry_ids': ['e%03d' % (i + 1) for i in range(len(record['findings']))],
            'candidate_source': {'source': 'candidate_review.json', 'text': json.dumps(record, indent=2, ensure_ascii=True)}}


def prompt(packet, digest):
    encoded = json.dumps(packet, indent=2, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return ((SUITE / 'assessor-protocol.md').read_text() + '\nPacket SHA-256: ' + digest
            + '\n<artifact_content>\n' + encoded + '\n</artifact_content>\n')


def export(run_dir, output):
    criteria = inputs()
    _, cases, rows = loaded_run(run_dir)
    output.mkdir(parents=True, exist_ok=False)
    mapping = {'candidate_run_sha256': sha(run_dir / 'run.json'),
               'assessor_manifest_sha256': sha(SUITE / 'assessor-manifest.json'), 'packets': {}, 'unavailable': {}}
    items = list(rows.items())
    secrets.SystemRandom().shuffle(items)
    for trial_id, row in items:
        if row['runtime_errors'] or row['format_error']:
            mapping['unavailable'][trial_id] = 'Candidate runtime or structural failure.'
            continue
        ident = 'a' + secrets.token_hex(8)
        packet = make_packet(ident, cases[row['trial']['case_id']], criteria, row['record'])
        folder = output / ident
        folder.mkdir()
        host.save(folder / 'packet.json', packet)
        digest = sha(folder / 'packet.json')
        (folder / 'START-HERE.md').write_text(prompt(packet, digest))
        mapping['packets'][ident] = {'trial_id': trial_id, 'packet_sha256': digest,
                                     'prompt_sha256': sha(folder / 'START-HERE.md')}
    host.save(output / 'coordinator-map.json', mapping)
    return mapping


def exact(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        raise ValueError(label + ' fields differ from the protocol.')


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' requires a reason/text value.')


def citations(packet, values, needs_candidate=False):
    if not isinstance(values, list) or not values:
        raise ValueError('Located citations are required.')
    sources = {s['source']: s['text'].splitlines() for s in packet['case']['artifacts'] + [packet['candidate_source']]}
    cited = set()
    for cite in values:
        exact(cite, 'source start_line end_line quote', 'Citation')
        source, start, end, quote = (cite[k] for k in ('source', 'start_line', 'end_line', 'quote'))
        if (not isinstance(source, str) or source not in sources or type(start) is not int or type(end) is not int
                or not 1 <= start <= end <= len(sources[source]) or not isinstance(quote, str) or not quote.strip()
                or quote not in '\n'.join(sources[source][start - 1:end])):
            raise ValueError('Citation does not resolve to supplied text.')
        cited.add(source)
    if not (cited - {'candidate_review.json'}) or (needs_candidate and 'candidate_review.json' not in cited):
        raise ValueError('Cite source evidence and, for entry judgments, candidate text.')


def validate(packet, digest, grade):
    exact(grade, 'assessment_id packet_sha256 assessor entries required_defects case_reason case_citations criteria_dispute', 'Assessment')
    if grade['assessment_id'] != packet['assessment_id'] or grade['packet_sha256'] != digest:
        raise ValueError('Assessment belongs to another packet.')
    exact(grade['assessor'], 'model family prior_exposure', 'Assessor')
    for value in grade['assessor'].values():
        text(value, 'Assessor declaration')
    if grade['assessor']['family'] != 'Gemini':
        raise ValueError('Assessment family differs from the planned family.')
    text(grade['case_reason'], 'Case judgment')
    if grade['criteria_dispute'] is not None:
        text(grade['criteria_dispute'], 'Criteria dispute')
    entries = grade['entries']
    if not isinstance(entries, list) or len(entries) != len(packet['entry_ids']):
        raise ValueError('Every candidate entry requires a judgment.')
    required = set(packet['criteria']['case']['required_defect_ids'])
    seen, supported = set(), set()
    quote_errors = []
    fields = ('entry_id classification reason citations recovered_defects unsupported_assertion '
              'unsupported_defect_claim out_of_scope misplaced_note severity_assessment severity_reason duplicate_of')
    for entry, ident, original in zip(entries, packet['entry_ids'], packet['candidate']['findings']):
        exact(entry, fields, 'Entry judgment')
        if entry['entry_id'] != ident or entry['classification'] not in CLASSES:
            raise ValueError('Entry identity/order or classification mismatch.')
        text(entry['reason'], 'Entry classification')
        text(entry['severity_reason'], 'Severity diagnostic')
        for key in ('unsupported_assertion', 'unsupported_defect_claim', 'out_of_scope', 'misplaced_note'):
            if type(entry[key]) is not bool:
                raise ValueError('Entry flags must be booleans.')
        if entry['unsupported_defect_claim'] and not entry['unsupported_assertion']:
            raise ValueError('Unsupported defect claim requires unsupported assertion.')
        neutral = entry['classification'] == 'neutral'
        if entry['misplaced_note'] != neutral:
            raise ValueError('Only a neutral-only entry is a misplaced note.')
        if neutral and (entry['unsupported_assertion'] or entry['out_of_scope'] or entry['recovered_defects']):
            raise ValueError('Neutral classification cannot manufacture a substantive defect or false positive.')
        expected_severity = 'mismatch' if neutral and original['severity'] != 'unrated' else ('not_mismatch' if neutral else 'unresolved')
        if entry['severity_assessment'] != expected_severity:
            raise ValueError('Severity is diagnostic; substantive severity calibration remains unresolved.')
        recovered = entry['recovered_defects']
        if (not isinstance(recovered, list) or any(not isinstance(r, str) for r in recovered)
                or len(set(recovered)) != len(recovered) or not set(recovered) <= required):
            raise ValueError('Unknown or duplicate required defect.')
        if recovered and entry['classification'] not in ('supported_defect', 'mixed'):
            raise ValueError('Recovery requires a supported assertion.')
        if entry['classification'] == 'unsupported' and not entry['unsupported_assertion']:
            raise ValueError('Unsupported classification requires its flag.')
        if entry['classification'] == 'out_of_scope' and not entry['out_of_scope']:
            raise ValueError('Out-of-scope classification requires its flag.')
        if entry['classification'] in ('supported_defect', 'secondary_observation', 'unresolved') and (entry['unsupported_assertion'] or entry['out_of_scope']):
            raise ValueError('Mixed substantive assertions require mixed classification.')
        duplicate = entry['duplicate_of']
        if duplicate is not None and (not isinstance(duplicate, str) or duplicate not in seen):
            raise ValueError('Duplicate must refer to a preceding entry.')
        seen.add(ident)
        supported.update(recovered)
        try:
            citations(packet, entry['citations'], needs_candidate=True)
        except ValueError as exc:
            quote_errors.append(ident + ': ' + str(exc))
    defects = grade['required_defects']
    if not isinstance(defects, list):
        raise ValueError('Required-defect judgments must be a list.')
    observed = set()
    for result in defects:
        exact(result, 'defect_id outcome reason', 'Required defect')
        ident = result['defect_id']
        if not isinstance(ident, str) or ident not in required or ident in observed or result['outcome'] not in ('recovered', 'missed', 'unresolved'):
            raise ValueError('Required-defect judgments differ from criteria.')
        text(result['reason'], 'Required-defect judgment')
        if (result['outcome'] == 'recovered') != (ident in supported):
            raise ValueError('Case recovery must agree with per-entry recovery.')
        observed.add(ident)
    if observed != required:
        raise ValueError('Missing required-defect judgment.')
    try:
        citations(packet, grade['case_citations'])
    except ValueError as exc:
        quote_errors.append('case: ' + str(exc))
    return {'structure_valid': True, 'citations_resolve': not quote_errors, 'citation_errors': quote_errors,
            'substantive_truth_verified': False, 'identity_authenticated': False}


def load_packet(export_dir, ident):
    mapping = read(export_dir / 'coordinator-map.json')
    if mapping['assessor_manifest_sha256'] != sha(SUITE / 'assessor-manifest.json'):
        raise ValueError('Assessor manifest changed.')
    if ident not in mapping['packets']:
        raise ValueError('Unknown assessment ID.')
    info = mapping['packets'][ident]
    path = export_dir / ident / 'packet.json'
    if sha(path) != info['packet_sha256'] or sha(export_dir / ident / 'START-HERE.md') != info['prompt_sha256']:
        raise ValueError('Exported assessor input changed.')
    return read(path), info


def decode_response(raw):
    value = candidate.parse_object(raw)
    failed = False
    if 'assessment_id' not in value and 'result' in value:
        failed = bool(value.get('is_error'))
        final = value['result']
        value = candidate.parse_object(final) if isinstance(final, str) else final
    return value, failed


def import_response(export_dir, ident, response, destination):
    inputs()
    packet, info = load_packet(export_dir, ident)
    destination.mkdir(parents=True, exist_ok=False)
    raw = response.read_bytes()
    (destination / 'response.bin').write_bytes(raw)
    grade, checks, error = None, None, None
    try:
        # Accept this explicit adapter contract, never fragments. Compatibility
        # with this installed host's live output has not yet been measured.
        grade, failed = decode_response(raw.decode('utf-8'))
        if failed:
            raise ValueError('Host wrapper reports a failed response.')
        checks = validate(packet, info['packet_sha256'], grade)
    except (ValueError, TypeError, KeyError, UnicodeError) as exc:
        error = str(exc)
    receipt = {'assessment_id': ident, 'packet_sha256': info['packet_sha256'],
               'response_sha256': host.digest(raw), 'grade': grade, 'checks': checks, 'error': error,
               'provenance': 'Submitted model/family/exposure are declarations; this adapter does not authenticate identity or source-only access.'}
    host.save(destination / 'assessment.json', receipt)
    return receipt


def run_assessors(export_dir, output, auth_path, cli='agy', invoke=host.invoke):
    inputs()
    mapping = read(export_dir / 'coordinator-map.json')
    plan = read(SUITE / 'plan.json')
    auth = candidate.authorization(auth_path, 'assessors', sha(SUITE / 'assessor-manifest.json'), plan['assessor_max_calls'])
    if auth.get('export_map_sha256') != sha(export_dir / 'coordinator-map.json') or auth.get('no_dollar_cap_acknowledged') is not True:
        raise ValueError('Gemini export and absence of a dollar cap require explicit acceptance.')
    if len(mapping['packets']) > plan['assessor_max_calls']:
        raise ValueError('Assessor call cap exceeded.')
    output.mkdir(parents=True, exist_ok=False)
    candidate.consume_authorization(auth_path)
    state = {'status': 'running', 'assessments': {}, 'started_assessments': [], 'export_map_sha256': sha(export_dir / 'coordinator-map.json')}
    host.save(output / 'run.json', state)
    for ident in mapping['packets']:
        try:
            if sha(export_dir / 'coordinator-map.json') != state['export_map_sha256']:
                raise ValueError('Assessor mapping changed during execution.')
            inputs()
            load_packet(export_dir, ident)
            with tempfile.TemporaryDirectory(prefix='reviewerest-assessor-') as temp:
                work = Path(temp)
                # Only one prepared prompt goes into a fresh host workspace.
                source = (export_dir / ident / 'START-HERE.md').read_text()
                args = [cli, '--new-project', '--sandbox', '--mode', 'plan', '--disable-slash-commands',
                        '--model', plan['assessor_model'], '--print-timeout', str(plan['assessor_timeout_seconds']) + 's',
                        '--output-format', 'json', '--json-schema', (SUITE / 'assessment-schema.json').read_text(), '-p', source]
                start = output / (ident + '-started.json')
                host.save(start, {'command': args, 'workspace_before': host.snapshot(work)})
                state['started_assessments'].append(ident)
                host.save(output / 'run.json', state)
                stdout, stderr, code, timeout, elapsed = invoke(args, work, plan['assessor_timeout_seconds'])
                raw_path = output / (ident + '-response.bin')
                raw_path.write_bytes(stdout)
                (output / (ident + '-stderr.bin')).write_bytes(stderr)
                result = import_response(export_dir, ident, raw_path, output / ident)
                capture = {'exit_code': code, 'timed_out': timeout, 'elapsed_seconds': elapsed,
                           'workspace_after': host.snapshot(work), 'requested_model': plan['assessor_model'],
                           'cost_usd': None, 'source_only_access_verified': False,
                           'host_enforcement_verified': False,
                           'limit': 'CLI JSON capture and declared identity; tool activity and actual served identity are not authenticated.'}
                host.save(output / ident / 'host.json', capture)
                result['host_capture_sha256'] = sha(output / ident / 'host.json')
                host.save(output / ident / 'assessment.json', result)
                state['assessments'][ident] = sha(output / ident / 'assessment.json')
                if code or timeout or capture['workspace_after']:
                    raise ValueError('Assessor invocation failed, timed out or changed its workspace.')
                # Unknown CLI output shapes stop spending, rather than silently
                # accepting an unverified adapter or trying another prompt.
                if result['error']:
                    raise ValueError('Assessor output contract failed: ' + result['error'])
        except Exception as exc:
            state.update(status='stopped', stop_reason=str(exc))
            host.save(output / 'run.json', state)
            return state
        host.save(output / 'run.json', state)
    state['status'] = 'completed'
    host.save(output / 'run.json', state)
    return state


def aggregate(run_dir, export_dir, assessments):
    criteria = inputs()
    plan, cases, rows = loaded_run(run_dir)
    mapping = read(export_dir / 'coordinator-map.json')
    if mapping['candidate_run_sha256'] != sha(run_dir / 'run.json'):
        raise ValueError('Assessor export belongs to a different candidate run.')
    assessor_run = read(assessments / 'run.json') if (assessments / 'run.json').exists() else None
    if assessor_run and assessor_run['export_map_sha256'] != sha(export_dir / 'coordinator-map.json'):
        raise ValueError('Assessor run belongs to a different export.')
    by_trial = {}
    for ident, info in mapping['packets'].items():
        packet, _ = load_packet(export_dir, ident)
        trial_id = info['trial_id']
        if trial_id not in rows or trial_id in by_trial:
            raise ValueError('Duplicate or unknown mapped trial.')
        expected = make_packet(ident, cases[rows[trial_id]['trial']['case_id']], criteria, rows[trial_id]['record'])
        if packet != expected:
            raise ValueError('Assessor packet no longer matches its candidate and accepted criteria.')
        by_trial[trial_id] = (ident, packet, info)
    arms = {a: Counter() for a in ('skill_on', 'skill_off')}
    report_rows = []
    case_criteria = {c['id']: c for c in criteria['cases']}
    for trial in plan['schedule']:
        counts = arms[trial['arm']]
        counts['planned_trials'] += 1
        case = case_criteria[trial['case_id']]
        required = len(case['required_defect_ids'])
        counts['planned_required_defects'] += required
        counts['planned_clean_trials'] += int(case['case_nature'] == 'clean')
        row = rows.get(trial['trial_id'])
        summary = dict(trial, assessment_available=False, raw_grade=None, assessment_error=None)
        valid_grade = None
        if row:
            counts['attempted_trials'] += 1
            counts['candidate_runtime_failures'] += bool(row['runtime_errors'])
            counts['candidate_structural_failures'] += bool(row['format_error'])
            counts['candidate_location_failures'] += bool(row['location_error'])
        if trial['trial_id'] in by_trial:
            ident, packet, info = by_trial[trial['trial_id']]
            path = assessments / ident / 'assessment.json'
            if path.exists():
                result = read(path)
                if assessor_run and assessor_run['assessments'].get(ident) != sha(path):
                    raise ValueError('Stored assessment changed after its run.')
                if sha(assessments / ident / 'response.bin') != result['response_sha256']:
                    raise ValueError('Raw assessor response changed.')
                try:
                    # Do not trust stored validation booleans or copied grades.
                    raw, failed = decode_response((assessments / ident / 'response.bin').read_text())
                    summary['raw_grade'] = raw
                    if raw != result['grade']:
                        raise ValueError('Stored grade differs from raw response.')
                    if failed:
                        raise ValueError('Host wrapper reports a failed response.')
                    if result.get('host_capture_sha256'):
                        host_path = assessments / ident / 'host.json'
                        if sha(host_path) != result['host_capture_sha256']:
                            raise ValueError('Assessor host receipt changed.')
                        capture = read(host_path)
                        if capture['exit_code'] or capture['timed_out'] or capture['workspace_after']:
                            raise ValueError('Assessor host failed or changed its workspace.')
                    checks = validate(packet, info['packet_sha256'], raw)
                    if not checks['citations_resolve']:
                        raise ValueError('Assessment citations do not resolve.')
                    if raw['criteria_dispute'] is not None:
                        counts['criteria_disputed_trials'] += 1
                        raise ValueError('Assessor disputes accepted criteria; awaiting adjudication.')
                    if row['runtime_errors'] or row['format_error']:
                        raise ValueError('Candidate is not eligible for semantic grading.')
                    valid_grade = raw
                except (ValueError, KeyError, TypeError) as exc:
                    summary['assessment_error'] = str(exc)
        if valid_grade is None:
            counts['unavailable_assessments'] += 1
            counts['unavailable_required_defects'] += required
        else:
            summary['assessment_available'] = True
            counts['available_assessments'] += 1
            for result in valid_grade['required_defects']:
                counts['required_defects_' + result['outcome']] += 1
            for entry in valid_grade['entries']:
                counts['unsupported_assertion_entries'] += entry['unsupported_assertion']
                counts['out_of_scope_entries'] += entry['out_of_scope']
                counts['misplaced_note_entries'] += entry['misplaced_note']
                counts['severity_mismatch_entries'] += entry['severity_assessment'] == 'mismatch'
                counts['severity_unresolved_entries'] += entry['severity_assessment'] == 'unresolved'
                counts['duplicate_entries'] += entry['duplicate_of'] is not None
                counts['unresolved_entry_judgments'] += entry['classification'] == 'unresolved'
            if case['case_nature'] == 'clean':
                counts['clean_trials_with_false_positive'] += any(e['unsupported_defect_claim'] for e in valid_grade['entries'])
                counts['clean_trials_with_unresolved_entries'] += any(e['classification'] == 'unresolved' for e in valid_grade['entries'])
        report_rows.append(summary)
    # Stable keys make absence visible and prevent a omitted zero from being read
    # as an unmeasured metric. Availability denominators remain explicit above.
    keys = set().union(*(a.keys() for a in arms.values())) | {
        'required_defects_recovered', 'required_defects_missed', 'required_defects_unresolved',
        'unsupported_assertion_entries', 'out_of_scope_entries', 'misplaced_note_entries',
        'severity_mismatch_entries', 'clean_trials_with_false_positive', 'criteria_disputed_trials',
        'unresolved_entry_judgments', 'clean_trials_with_unresolved_entries'}
    return {'version': 1, 'arms': {a: {k: c[k] for k in sorted(keys)} for a, c in arms.items()},
            'trials': report_rows, 'substantive_truth_verified': False,
            'limits': ['Counts reproduce submitted judgments, not independently established truth.',
                       'Diagnostic note/severity counts do not enter recovery or false-positive totals.',
                       'No composite score. Missing or disputed judgments remain unavailable.',
                       'Assessor identity and source-only access are declarations, not authenticated host evidence.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('export')
    p.add_argument('run', type=Path); p.add_argument('output', type=Path)
    p = sub.add_parser('import')
    p.add_argument('export', type=Path); p.add_argument('id'); p.add_argument('response', type=Path); p.add_argument('output', type=Path)
    p = sub.add_parser('run')
    p.add_argument('export', type=Path); p.add_argument('output', type=Path); p.add_argument('--authorization', type=Path, required=True)
    p.add_argument('--cli', default='agy')
    p = sub.add_parser('aggregate')
    p.add_argument('run', type=Path); p.add_argument('export', type=Path); p.add_argument('assessments', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'export':
            result = export(args.run, args.output)
            print(json.dumps({'exported_packets': len(result['packets']), 'unavailable': result['unavailable']}))
        elif args.action == 'import':
            result = import_response(args.export, args.id, args.response, args.output)
            print(json.dumps({'checks': result['checks'], 'error': result['error']}))
            return 2 if result['error'] else 0
        elif args.action == 'run':
            result = run_assessors(args.export, args.output, args.authorization, args.cli)
            print(json.dumps({'status': result['status'], 'completed_assessments': len(result['assessments'])}))
            return 0 if result['status'] == 'completed' else 2
        else:
            print(json.dumps(aggregate(args.run, args.export, args.assessments), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
