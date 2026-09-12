#!/usr/bin/env python3
"""Matched candidate trials. Live calls require a separate, one-use authorization."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

import adjudication_packet as packets
import run_claude as host

ROOT = host.ROOT
SUITE = ROOT / 'evals/skill-effect-v1'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return host.digest(path.read_bytes())


def pinned(manifest_path):
    manifest = read(manifest_path)
    for name, digest in manifest['files'].items():
        path = ROOT / name
        if path.resolve().is_relative_to(ROOT) is False or sha(path) != digest:
            raise ValueError('Frozen input changed: ' + name)
    return manifest


def inputs():
    # This manifest deliberately excludes criteria, historical labels and answers.
    manifest = pinned(SUITE / 'candidate-manifest.json')
    plan = read(SUITE / 'plan.json')
    schedule = plan['schedule']
    counts = Counter((t['case_id'], t['arm']) for t in schedule)
    expected = Counter({(c, a): 3 for c in plan['case_ids'] for a in ('skill_on', 'skill_off')})
    if counts != expected or len(schedule) != 36 or len({t['trial_id'] for t in schedule}) != 36:
        raise ValueError('Schedule must cover six cases, two arms and three repeats.')
    if len({(t['case_id'], t['repeat'], t['arm']) for t in schedule}) != 36:
        raise ValueError('Repeated schedule slot.')
    acceptance = read(ROOT / plan['acceptance_path'])
    if acceptance['criteria_accepted'] is not True or acceptance['criteria_sha256'] != plan['criteria_sha256']:
        raise ValueError('Plan is not bound to accepted criteria.')
    cases = {c: read(ROOT / plan['packet_paths'][c]) for c in plan['case_ids']}
    if any(p['id'] != c for c, p in cases.items()):
        raise ValueError('Case identity mismatch.')
    return manifest, plan, cases


def parse_object(text):
    value = text.strip()
    if value.startswith('```json\n') and value.endswith('\n```'):
        value = value[8:-4]
    def unique(pairs):
        obj = {}
        for key, item in pairs:
            if key in obj:
                raise ValueError('Duplicate JSON field: ' + key)
            obj[key] = item
        return obj
    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant: ' + value)
    obj = json.loads(value, object_pairs_hook=unique, parse_constant=invalid_constant)
    if not isinstance(obj, dict):
        raise ValueError('Expected exactly one JSON object.')
    return obj


def shape(record):
    if not isinstance(record, dict) or set(record) != {'findings'} or not isinstance(record['findings'], list):
        raise ValueError('Expected only a findings array.')
    for item in record['findings']:
        if not isinstance(item, dict) or set(item) != {'finding', 'claim', 'location', 'severity'}:
            raise ValueError('Each entry must have exactly the four shared fields.')
        if any(not isinstance(item[k], str) or not item[k].strip() for k in ('finding', 'claim')):
            raise ValueError('Finding and claim must be nonempty strings.')
        if item['severity'] not in ('high', 'medium', 'low', 'unrated'):
            raise ValueError('Unknown severity token.')
        if not isinstance(item['location'], list) or not item['location']:
            raise ValueError('Location array required.')
        for loc in item['location']:
            if (not isinstance(loc, dict) or set(loc) != {'source', 'start_line', 'end_line'}
                    or not isinstance(loc['source'], str) or type(loc['start_line']) is not int
                    or type(loc['end_line']) is not int):
                raise ValueError('Malformed location.')


def workspace(work, packet, arm, skill=ROOT / 'review'):
    host.save(work / 'case.json', packet)
    shutil.copyfile(ROOT / 'evals/skill-effect-adjudication-v1/phase1/shared-output.schema.json', work / 'output-schema.json')
    if arm == 'skill_on':
        shutil.copytree(skill, work / host.SKILL_PATH, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        meta = work / 'reviewerest-plugin/.claude-plugin'
        meta.mkdir()
        host.save(meta / 'plugin.json', {'name': 'reviewerest-eval', 'version': '1.0.0'})
    elif arm != 'skill_off':
        raise ValueError('Unknown arm.')


def command(cli, work, arm, plan):
    allowed = 'Read,Glob,Grep,Skill' if arm == 'skill_on' else 'Read,Glob,Grep'
    prompt = (SUITE / 'candidate-prompt.md').read_text()
    if arm == 'skill_on':
        prompt = 'Invoke exactly reviewerest-eval:review using the Skill tool, then perform the following task.\n' + prompt
    args = [cli, '--restricted', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--tools', allowed, '--allowedTools', allowed, '--permission-mode', 'dontAsk',
            '--permission-prompts', 'none', '--no-chrome', '--no-session-persistence',
            '--model', plan['candidate_model'], '--effort', plan['candidate_effort'],
            '--max-budget-usd', str(plan['candidate_budget_per_call_usd']),
            '--output-format', 'stream-json', '--verbose', '--include-hook-events']
    if arm == 'skill_on':
        args += ['--plugin-dir', str(work / 'reviewerest-plugin')]
    else:
        args += ['--disable-slash-commands']
    return args + ['-p', prompt]


def text_parts(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n'.join(text_parts(x) for x in value)
    if isinstance(value, dict):
        return text_parts(value.get('text', value.get('content', '')))
    return ''


def path_errors(calls, work):
    errors = []
    for call in calls:
        args = call.get('input', {})
        if not isinstance(args, dict):
            errors.append('Malformed tool arguments.')
            continue
        name = call.get('name')
        value = args.get('file_path') if name == 'Read' else args.get('path')
        if name in ('Read', 'Glob', 'Grep') and value is not None:
            if not isinstance(value, str) or not (work / value).resolve().is_relative_to(work.resolve()):
                errors.append('File inspection attempted outside the candidate workspace.')
        if name == 'Glob':
            pattern = args.get('pattern', '')
            if not isinstance(pattern, str) or Path(pattern).is_absolute() or '..' in Path(pattern).parts:
                errors.append('Glob pattern escapes the candidate workspace.')
    return errors


def trace(stdout, arm, model, skill_body):
    errors = []
    events = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('not an object')
            events.append(event)
        except (ValueError, UnicodeDecodeError):
            errors.append('Unparseable host event.')
    finals = [e for e in events if e.get('type') == 'result']
    inits = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    final = finals[0] if len(finals) == 1 else {}
    init = inits[0] if len(inits) == 1 else {}
    normalize = lambda name: name.removesuffix('[1m]') if isinstance(name, str) else ''
    wanted = normalize(model)
    if not init or normalize(init.get('model')) != wanted:
        errors.append('Missing or unexpected primary model identity.')
    allowed = {'Read', 'Glob', 'Grep'} | ({'Skill'} if arm == 'skill_on' else set())
    init_tools = init.get('tools')
    if not isinstance(init_tools, list) or any(not isinstance(t, str) for t in init_tools) or set(init_tools) != allowed:
        errors.append('Host tool inventory differs from the frozen allowlist.')
    usage = final.get('modelUsage', {})
    if not isinstance(usage, dict) or not usage or any(normalize(m) != wanted for m in usage):
        errors.append('Missing usage or unexpected model usage; auxiliary models are not pre-approved.')
    elif any(not isinstance(v, dict) or type(v.get('outputTokens')) is not int or v['outputTokens'] <= 0 for v in usage.values()):
        errors.append('No positive model output-token usage recorded.')
    calls = [b for e in events if e.get('type') == 'assistant'
             for b in e.get('message', {}).get('content', []) if isinstance(b, dict) and b.get('type') == 'tool_use']
    if any(c.get('name') not in allowed for c in calls):
        errors.append('Prohibited tool attempt observed.')
    if arm == 'skill_on':
        errors += host.loading_errors(calls, events)
        call_ids = {c.get('id') for c in calls if c.get('name') == 'Skill'
                    and c.get('input', {}).get('skill') == host.EXPECTED_SKILL}
        bodies = [text_parts(b.get('content')) for e in events for b in e.get('message', {}).get('content', [])
                  if isinstance(b, dict) and b.get('type') == 'tool_result'
                  and b.get('tool_use_id') in call_ids and not b.get('is_error')]
        if not any(skill_body.strip() in body for body in bodies):
            errors.append('Exact skill body absent from successful loading evidence.')
    elif any(c.get('name') == 'Skill' for c in calls):
        errors.append('Control invoked a skill.')
    cost = final.get('total_cost_usd')
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
        errors.append('Missing finite nonnegative usage cost.')
        cost = None
    if not final or final.get('is_error') or not isinstance(final.get('result'), str):
        errors.append('No successful final response.')
    return errors, final.get('result'), cost, calls


def run_trial(cli, trial, packet, plan, destination, invoke=host.invoke):
    destination.mkdir()
    with tempfile.TemporaryDirectory(prefix='reviewerest-effect-') as temp:
        work = Path(temp)
        workspace(work, packet, trial['arm'])
        before = host.snapshot(work)
        args = command(cli, work, trial['arm'], plan)
        host.save(destination / 'started.json', {'trial': trial, 'command': args, 'before': before})
        stdout, stderr, code, timeout, elapsed = invoke(args, work, plan['candidate_timeout_seconds'])
        (destination / 'stdout.bin').write_bytes(stdout)
        (destination / 'stderr.bin').write_bytes(stderr)
        body = (ROOT / 'review/SKILL.md').read_text().split('---', 2)[-1].strip()
        runtime, text, cost, calls = trace(stdout, trial['arm'], plan['candidate_model'], body)
        runtime += path_errors(calls, work)
        after = host.snapshot(work)
        if before != after:
            runtime.append('Workspace changed.')
        if code or timeout:
            runtime.append('CLI failed or timed out.')
        record, format_error, location_error = None, None, None
        try:
            record = parse_object(text or '')
            shape(record)
        except (ValueError, TypeError) as exc:
            format_error = str(exc)
        if not format_error:
            try:
                packets.validate_candidate(record, packet)
            except ValueError as exc:
                location_error = str(exc)
        result = {'trial': trial, 'exit_code': code, 'timed_out': timeout, 'elapsed_seconds': elapsed,
                  'runtime_errors': runtime, 'format_error': format_error, 'location_error': location_error,
                  'record': record, 'raw_review': text, 'cost_usd': cost, 'calls': calls,
                  'before': before, 'after': after, 'stdout_sha256': host.digest(stdout),
                  'stderr_sha256': host.digest(stderr), 'substantive_truth_verified': False}
        host.save(destination / 'trial.json', result)
        return result


def authorization(path, stage, manifest_digest, max_calls):
    value = read(path)
    if (value.get('approved') is not True or value.get('stage') != stage
            or value.get('manifest_sha256') != manifest_digest or value.get('max_calls') != max_calls
            or not isinstance(value.get('operator'), str) or not value['operator'].strip()):
        raise ValueError('Explicit, matching operator authorization required.')
    return value


def consume_authorization(path):
    # A one-use local receipt prevents accidentally reusing the same authorization.
    with path.with_name(path.name + '.used').open('x') as used:
        used.write(sha(path) + '\n')


def run(output, auth_path, cli='claude', trial_runner=run_trial):
    _, plan, cases = inputs()
    digest = sha(SUITE / 'candidate-manifest.json')
    auth = authorization(auth_path, 'candidates', digest, len(plan['schedule']))
    if auth.get('budget_per_call_usd') != plan['candidate_budget_per_call_usd'] or auth.get('cli_cap_overshoot_acknowledged') is not True:
        raise ValueError('Candidate usage limit and its billing limitation require acceptance.')
    version = subprocess.check_output([cli, '--version'], text=True, timeout=15).strip()
    if version != plan['candidate_cli_version']:
        raise ValueError('Claude version changed; revise and freeze the plan before running.')
    output.mkdir(parents=True, exist_ok=False)
    consume_authorization(auth_path)
    state = {'manifest_sha256': digest, 'schedule': plan['schedule'], 'trials': {}, 'started_trials': [],
             'status': 'running', 'recorded_cost_usd': 0.0, 'cost_complete': True}
    host.save(output / 'run.json', state)
    for trial in plan['schedule']:
        try:
            if sha(SUITE / 'candidate-manifest.json') != digest:
                raise ValueError('Candidate manifest changed during the run.')
            inputs()  # Stop on input/code drift before each additional paid call.
            if state['recorded_cost_usd'] >= plan['candidate_total_nominal_usd']:
                raise ValueError('Recorded candidate budget exhausted.')
            state['started_trials'].append(trial['trial_id'])
            host.save(output / 'run.json', state)
            result = trial_runner(cli, trial, cases[trial['case_id']], plan, output / trial['trial_id'])
            state['trials'][trial['trial_id']] = sha(output / trial['trial_id'] / 'trial.json')
            if result['cost_usd'] is None:
                state['cost_complete'] = False
            else:
                state['recorded_cost_usd'] += result['cost_usd']
            if result['runtime_errors']:
                raise ValueError('; '.join(result['runtime_errors']))
        except Exception as exc:
            if trial['trial_id'] in state['started_trials'] and trial['trial_id'] not in state['trials']:
                state['cost_complete'] = False
            state.update(status='stopped', stop_reason=str(exc))
            host.save(output / 'run.json', state)
            return state
        host.save(output / 'run.json', state)
    state['status'] = 'completed'
    host.save(output / 'run.json', state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--authorization', type=Path)
    parser.add_argument('--cli', default='claude')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        if args.check:
            _, plan, _ = inputs()
            print(json.dumps({'valid': True, 'planned_calls': len(plan['schedule']), 'substantive_truth_verified': False}))
        else:
            if not args.output or not args.authorization:
                parser.error('--output and --authorization are required for live execution')
            result = run(args.output, args.authorization, args.cli)
            print(json.dumps({'status': result['status'], 'completed_trials': len(result['trials'])}))
            return 0 if result['status'] == 'completed' else 2
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
