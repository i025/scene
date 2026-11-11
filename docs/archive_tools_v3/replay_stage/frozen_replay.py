"""Optional post-ten-round frozen-M replay. Not part of the formal V3 runner."""
import argparse
import ast
import csv
import difflib
import fcntl
import html
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
DEV = ('commons_109923183', 'commons_118588033', 'commons_105241439')
SELECTION, TEST = 'bw_0082', 'bw_0092'
MAX_CLI, MAX_FRAMES = 100, 300
PLANNED_CLI, PLANNED_FRAMES = 90, 230
PLATFORM_VERSION = 'platform_A04'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def sources(folder):
    return {str(p.relative_to(folder)): p.read_text() for p in sorted(folder.rglob('*'))
            if p.is_file() and p.suffix in {'.py', '.txt', '.md'} and '__pycache__' not in p.parts}


def usage(root):
    sessions = [read(p) for p in root.rglob('session.json') if 'code_snapshots' not in p.parts]
    charges = root / 'render_attempts.jsonl'
    return {'cli_sessions': len(list(root.rglob('request.json'))),
            'render_attempts': sum(json.loads(line)['frames'] for line in charges.read_text().splitlines()) if charges.exists() else 0,
            'known_input_tokens': sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'), int)),
            'known_output_tokens': sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'), int)),
            'usage_unknown_sessions': sum(not isinstance(s.get('input_tokens'), int) for s in sessions)}


def starts(main):
    old = main.parent / 'scene_rsi_v2_4'
    return {'original_H0': old / 'fixed_h/H0',
            'v24_task01_active_shared_H': old / 'tasks/task01/active/H'}


def m_changed_content_execution(program, m0, execution_path, trace):
    """Associate changed M Python sources with one completed later research trace."""
    before, after = sources(m0), sources(program)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    changed_python = [name for name in changed if name.endswith('.py')]
    result = {'source': str(program), 'compared_to': str(m0), 'changed_source_files': changed,
              'changed_python_files': changed_python, 'execution_record': str(execution_path),
              'trace_folder': str(trace) if trace is not None else None,
              'source_diff': ''.join(''.join(difflib.unified_diff(
                  before.get(name, '').splitlines(True), after.get(name, '').splitlines(True),
                  fromfile='M0/' + name, tofile='M_descendant/' + name)) for name in changed_python),
              'execution_evidence': [], 'eligible': False,
              'comparison': 'Exact source text/name/path comparison, no hashes; execution is not an ability claim'}
    if not execution_path.exists():
        result['reason'] = 'Later M_program_execution.json was not saved'
        return result
    execution = read(execution_path)
    if execution['status'] != 'completed' or Path(execution['program']).resolve() != (program / 'meta.py').resolve():
        result['reason'] = 'Later M entry did not complete or its recorded program differs'
        return result
    evidence = result['execution_evidence']
    if 'meta.py' in changed_python and 'meta.py' in after:
        evidence.append({'file': 'meta.py', 'kind': 'completed_changed_entry',
                         'record': str(execution_path), 'program': execution['program']})
    for raw in execution['loaded_M_helpers']:
        loaded = Path(raw).resolve()
        if loaded.is_relative_to(program.resolve()):
            name = str(loaded.relative_to(program.resolve()))
            if name in changed_python and name in after and name != 'meta.py' and not name.startswith('actions/'):
                evidence.append({'file': name, 'kind': 'changed_imported_helper',
                                 'record': str(execution_path), 'logged_loaded_path': raw})
    if trace is not None:
        for path in sorted((trace / 'actions').glob('*/observation.json')):
            observation = read(path)
            snapshot = path.with_name('action.py')
            if observation['status'] != 'completed' or not snapshot.exists():
                continue
            name = observation['action']
            if name in changed_python and name.startswith('actions/') and name in after and snapshot.read_text() == after[name]:
                evidence.append({'file': name, 'kind': 'completed_changed_action',
                                 'record': str(path), 'source_snapshot': str(snapshot),
                                 'scene_id': observation['scene_id'], 'exact_action_name_and_source_match': True})
    result['executed_changed_files'] = sorted({row['file'] for row in evidence})
    result['unexecuted_changed_python_files'] = sorted(set(changed_python) - set(result['executed_changed_files']))
    result['eligible'] = bool(evidence)
    result['reason'] = ('Changed Python entry/helper/action participated in this completed later research trace'
                        if evidence else 'Changed M content only available as text/library, removed, or lacks actual later execution evidence')
    return result


def descendant_execution_audit(main):
    """Metadata/source-only audit reusable by offline reports and replay readiness."""
    m0 = main / 'code_snapshots/platform_frozen/initial_m'
    records = [read(path) for path in sorted((main / 'rounds').glob('*/record.json'))]
    audits = []
    for row in records:
        program = Path(row['M_program_used']).parent
        if sources(program) == sources(m0):
            continue
        folder = Path(row['proposal_path']).parent
        request_path = folder / 'research_request.json'
        request = read(request_path) if request_path.exists() else None
        trace = Path(request['trace_folder']) if request is not None else None
        audit = m_changed_content_execution(program, m0, folder / 'M_program_execution.json', trace)
        origin = [old['round'] for old in records if old['round'] < row['round']
                  and old['M_accepted'] and old['M_candidate'] == row['M_parent']]
        audit.update(M_version=row['M_parent'], executed_in_round=row['round'],
                     accepted_in_earlier_rounds=origin, research_request=str(request_path))
        if not origin or request is None or Path(request['M_program']).resolve() != program.resolve():
            audit['eligible'] = False
            audit['reason'] = 'Accepted earlier descendant origin or matching later research_request was not saved'
        audits.append(audit)
    qualifying = [row for row in audits if row['eligible']]
    return {'recorded_at': time.time(), 'M0_source': str(m0), 'descendant_uses': audits,
            'final_executed_descendant': qualifying[-1] if qualifying else None,
            'status': 'changed_content_execution_observed' if qualifying else 'no_qualifying_changed_content_execution',
            'evidence_limit': 'File/module entry or logged import/action execution, not line/branch coverage or proof that the changed statements improved decisions',
            'ability_improvement_verified': False, 'new_model_calls': 0, 'new_Blender_jobs': 0}


def platform_snapshot_audit(main):
    source = main / 'code_snapshots' / PLATFORM_VERSION
    required = ['config.json', 'pilot.py', 'research.py', 'research_worker.py', 'model_evidence.py',
                'bw_evaluate.py', 'eval_blend.py', 'backend/runtime.py', 'backend/codex_wrapper.py',
                'initial_m/meta.py', 'analyze.py', 'configs/selection_repeats.json']
    missing = [name for name in required if not (source / name).is_file()]
    return {'eligible': not missing, 'source': str(source), 'version': PLATFORM_VERSION,
            'missing_required_snapshot_files': missing,
            'reason': 'Fixed formal A04 snapshot is available' if not missing else 'Fixed formal A04 snapshot has not been completely frozen',
            'source_copy_policy': 'Only the complete fixed platform_A04 snapshot; no old-platform fallback or partial live-source overlays',
            'main_live_source_files_used': [], 'new_model_calls_for_audit': 0, 'new_Blender_jobs_for_audit': 0}


def main_completion_check(main):
    state, problems = read(main / 'state.json'), []
    if state['round_completed'] != 10 or state['phase'] != 'all_scheduled_terminal':
        problems.append('Main ten rounds and scheduled endpoint work are not terminal')
    if (main / 'experiment.lock').exists():
        with (main / 'experiment.lock').open('r') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError:
                problems.append('Main launcher owns its exclusive flock; do not start concurrent replay')
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)
    return state, problems


def readiness(main):
    state, problems = main_completion_check(main)
    cfg, rows = read(main / 'config.json'), []
    m0 = main / 'code_snapshots/platform_frozen/initial_m'
    descendant_audit = descendant_execution_audit(main)
    final = descendant_audit['final_executed_descendant']
    if final is None:
        problems.append('No changed executable M content has saved execution evidence in subsequent formal research; text/library availability is insufficient')
    platform_snapshot = platform_snapshot_audit(main)
    if not platform_snapshot['eligible']:
        problems.append(platform_snapshot['reason'])
    requests = [(path, read(path)['context']['H_sources']) for path in sorted((main / 'candidates').glob('C*/research_request.json'))]
    hstart = sources(main / 'fixed_h/historical_r1_C2_start')
    for name, path in starts(main).items():
        code = sources(path)
        tree = ast.parse(code['policy.py'])
        valid = any(isinstance(n, ast.FunctionDef) and n.name == 'solve' and len(n.args.args) == 2 for n in tree.body)
        seen = [str(p) for p, context in requests if all(context.get(key) == value for key, value in code.items())]
        row = {'id': name, 'source': str(path), 'solve_task_runtime_contract': valid,
               'same_complete_source_as_main_start': code == hstart,
               'files_identical_to_main_start': [key for key in code if code[key] == hstart.get(key)],
               'formal_M_complete_source_exposures': seen, 'formal_M_requests_checked': len(requests),
               'foundation_model_prior_exposure': None}
        rows.append(row)
        if not valid or code == hstart or seen:
            problems.append('Historical start fails contract/difference/explicit-unfamiliarity: ' + name)
    eligibility_reasons = list(problems)
    budget_reasons = []
    spent = usage(main)
    pairs = [('cli_sessions', 'max_cli_sessions'), ('render_attempts', 'max_render_frames'),
             ('known_input_tokens', 'max_input_tokens'), ('known_output_tokens', 'max_output_tokens')]
    remaining = {key: cfg['pilot'][cap] - spent[key] for key, cap in pairs}
    if remaining['cli_sessions'] < PLANNED_CLI or remaining['render_attempts'] < PLANNED_FRAMES:
        budget_reasons.append('Remaining global CLI/render budget below the frozen complete-stage upper estimate')
    if remaining['known_input_tokens'] <= 0 or remaining['known_output_tokens'] <= 0:
        budget_reasons.append('No positive observable token remainder')
    planned_calls = {'H': 54, 'M': 12, 'judge': 24}
    maxima = {role: {'input_tokens': None, 'output_tokens': None} for role in planned_calls}
    for path in main.rglob('session.json'):
        if 'code_snapshots' in path.parts:
            continue
        session = read(path)
        role = session['role']
        if role not in maxima:
            continue
        for key in ['input_tokens', 'output_tokens']:
            value = session.get(key)
            if isinstance(value, int):
                maxima[role][key] = max(maxima[role][key] or 0, value)
    estimated_tokens = {}
    for key in ['input_tokens', 'output_tokens']:
        if any(maxima[role][key] is None for role in planned_calls):
            estimated_tokens[key] = None
            budget_reasons.append('Missing measured per-role usage for conservative ' + key + ' estimate')
        else:
            estimated_tokens[key] = sum(planned_calls[role] * maxima[role][key] for role in planned_calls)
            if remaining['known_' + key] < estimated_tokens[key]:
                budget_reasons.append('Observed token remainder below max-historical-per-role plan: ' + key)
    problems += budget_reasons
    return {'status': 'pending' if problems else 'ready_for_root_execution_decision', 'reasons': problems,
            'main_phase': state['phase'], 'main_rounds_completed': state['round_completed'],
            'M0_source': str(m0), 'final_executed_descendant': final,
            'M_changed_content_execution_audit': descendant_audit, 'historical_starts': rows,
            'fixed_platform_snapshot': platform_snapshot,
            'global_usage_before_stage': spent, 'global_remaining_before_stage': remaining,
            'planned_token_estimate': {'method': 'Maximum visible single-session usage by role times frozen planned role counts; not a guarantee',
                                      'role_session_counts': planned_calls, 'observed_maxima': maxima, 'estimated': estimated_tokens},
            'eligibility': {'eligible': not eligibility_reasons, 'reason': '; '.join(eligibility_reasons) or 'Main terminal, executed descendant and explicit-unfamiliarity conditions satisfied'},
            'budget': {'allowed': not budget_reasons, 'reason': '; '.join(budget_reasons) or 'Stage quantity caps can fit the observed global remainder; token visibility limitations remain'},
            'source_audit': 'Direct source-text comparison, no hashes or fingerprints',
            'new_model_calls': 0, 'new_Blender_jobs': 0, 'Test_pixels_or_rubrics_read': False}


def copy_program(source, destination, *, readonly=False):
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for path in destination.rglob('*'):
        path.chmod(0o555 if path.is_dir() and readonly else 0o755 if path.is_dir() else 0o444 if readonly else 0o644)
    destination.chmod(0o555 if readonly else 0o755)


def selection_repeat_plan():
    labels = [f'B{index:02d}' for index in range(2)]
    labels += [f'B{index:02d}_{label}_C1' for index in range(2) for label in ['M0', 'Mfinal']]
    return {label: {SELECTION: 1} for label in labels}


def prepare(main, stage, audit):
    fixed_platform = audit['fixed_platform_snapshot']
    if not fixed_platform['eligible']:
        raise RuntimeError('Fixed formal A04 platform snapshot is not ready')
    platform = Path(fixed_platform['source'])
    if list(platform.rglob('session.json')) or list(platform.rglob('request.json')) or (platform / 'results').exists():
        raise ValueError('Platform copy must contain code/configuration, not old execution history')
    shutil.copytree(platform, stage, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    write(stage / 'configs/selection_repeats_main_source.json', read(platform / 'configs/selection_repeats.json'))
    write(stage / 'configs/selection_repeats.json', selection_repeat_plan())
    c = read(platform / 'config.json')
    write(stage / 'config_v3_source.json', c)
    remaining = audit['global_remaining_before_stage']
    c['results_dir'] = str(stage)
    c['dataset']['manifest'] = str(stage / 'manifest.json')
    c['budget'].update(model_calls=3, executions=2)
    c['pilot'].update(name='scene_rsi_v3_frozen_meta_replay', rounds=0, development_panel_size=3,
                      selection_size=1, research_sessions_per_round=3,
                      diagnostic_frames_per_round=8, max_cli_sessions=min(MAX_CLI, remaining['cli_sessions']),
                      max_render_frames=min(MAX_FRAMES, remaining['render_attempts']),
                      max_input_tokens=remaining['known_input_tokens'], max_output_tokens=remaining['known_output_tokens'])
    c['pilot'].update(semantic_edit_subset=[], checkpoint_development_subset_size=0, boundary_case_limit=0,
                      final_test={'primary_repeats': 1, 'independent_sources': 1,
                                  'decision_before_any_test_generation': True,
                                  'rule': 'One fixed stage Test source only after all four K=1 choices freeze'},
                      forecast={'scope': 'Optional frozen-M replay only; main forecast preserved in config_v3_source.json',
                                'H_cli_upper': 54, 'M_cli_upper': 12, 'judge_cli_upper_with_one_service_retry': 24,
                                'all_cli_forecast_upper': PLANNED_CLI, 'render_forecast_upper': PLANNED_FRAMES})
    write(stage / 'config.json', c)
    write(stage / 'budget_phase.json', {'phase': 'final', 'independent_stage': 'frozen_M_replay'})
    selected = []
    for scene in read(main / 'manifest.json'):
        if scene['scene_id'] in DEV:
            selected.append({**scene, 'split': 'development'})
        elif scene['scene_id'] == SELECTION:
            selected.append({**scene, 'split': 'selection'})
        elif scene['scene_id'] == TEST:
            selected.append({**scene, 'split': 'test'})
    assert len(selected) == 5
    write(stage / 'manifest.json', selected)
    write(stage / 'public_attachment_allowlist.json', {scene['scene_id']: scene['attachments'] for scene in selected})
    for index, row in enumerate(audit['historical_starts']):
        copy_program(Path(row['source']), stage / 'replay_starts' / f'B{index:02d}')
    for name, source in [('M0', audit['M0_source']), ('Mfinal', audit['final_executed_descendant']['source'])]:
        copy_program(Path(source), stage / 'frozen_M' / name, readonly=True)
    shutil.copy2(HERE / 'PROTOCOL_TEMPLATE.md', stage / 'REPLAY_PROTOCOL.md')
    write(stage / 'stage_freeze.json', {'time': time.time(), 'audit': audit,
          'M_frozen': True, 'K': 1, 'independent_starts': 2, 'planned_CLI_upper_bound': PLANNED_CLI,
          'planned_render_charge_upper_bound': PLANNED_FRAMES, 'stage_caps': c['pilot'],
          'source_copy': str(platform), 'evaluation': 'BW-style / CLI-adapted; one Selection/one Test; no boundary rejudge',
          'fixed_platform_snapshot': fixed_platform,
          'promotion_delta': c['evaluation']['promotion_delta'],
          'promotion_delta_source': 'Copied fixed platform_A04/config.json evaluation.promotion_delta; never a hardcoded historical value',
          'selection_repeat_plan': selection_repeat_plan(),
          'selection_repeat_plan_source': 'Independent stage configs/selection_repeats.json; all six stage H labels use repeat1, no inherited main operator-replay IDs',
          'public_input_route': 'Unmodified fixed A04 prepare_task forwards metadata-declared public specs exactly once',
          'same_explicit_context_except': ['M_sources', 'available_probe_menu derived only from each frozen M_sources'],
          'data_status': 'exploratory', 'global_main_cap': read(main / 'config.json')['pilot']})
    write(stage / 'state.json', {'phase': 'prepared_not_executed', 'completed_trials': 0,
                                'formal_V3_rounds_added': 0, 'M_evolution_allowed': False})


def load_platform(stage):
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(stage), str(stage / 'backend')]
    spec = importlib.util.spec_from_file_location('frozen_replay_pilot', stage / 'pilot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lookup = {f'B{i:02d}': stage / 'replay_starts' / f'B{i:02d}' for i in range(2)}
    for index in range(2):
        for label in ['M0', 'Mfinal']:
            lookup[f'B{index:02d}_{label}_C1'] = stage / 'trials' / f'B{index:02d}_{label}' / 'H'
    module.hpath = lambda label: lookup[label]
    return module


def choose(candidate, parent, delta):
    gain = candidate['bw']['S_BW'] - parent['bw']['S_BW'] if candidate['bw']['evaluation_status'] == parent['bw']['evaluation_status'] == 'completed' else None
    recovery = not parent['valid'] or (parent['bw']['evaluation_status'] == 'completed' and not parent['functional']['functional_pass'])
    return candidate['eligible'] and (recovery or parent['eligible'] and gain is not None and gain >= delta), gain, recovery


def run_trial(p, stage, start, label, baseline, parent_selection):
    trial = stage / 'trials' / f'{start}_{label}'
    if (trial / 'record.json').exists():
        return read(trial / 'record.json')
    trial.mkdir(parents=True, exist_ok=True)
    candidate = f'{start}_{label}_C1'
    if not (trial / 'H').exists():
        copy_program(p.hpath(start), trial / 'H')
        copy_program(stage / 'frozen_M' / label, trial / 'M_actions')
    if (trial / 'research_process.json').exists() and not (trial / 'proposal.json').exists():
        row = {'start': start, 'M': label, 'status': 'interrupted', 'selected_H': start,
               'H_candidate': candidate, 'H_accepted': False, 'reason': 'Prior research has no proposal; preserve it, never resample'}
        write(trial / 'record.json', row)
        return row
    packet, scenes, images = p.context_for(baseline, start, stage / 'frozen_M/M0', 1)
    packet['fixed_goal'] = ('Frozen-M K=1 replay. Only H changes are admissible. Never propose M changes. '
                            'Own action library is in M_sources; the menu lists those actual action filenames and is not restrictive. '
                            'Temporary actions are permitted, no M evolution or access to Selection/Test raw data.')
    shared = json.loads(json.dumps(packet))
    shared.pop('M_sources')
    shared.pop('available_probe_menu')
    common = stage / 'common_context' / (start + '.json')
    if common.exists():
        assert read(common) == shared, 'Explicit development archives differ between frozen M arms'
    else:
        write(common, shared)
    packet['M_sources'] = p.sources(stage / 'frozen_M' / label)
    packet['available_probe_menu'] = [name for name in packet['M_sources'] if name.startswith('actions/')]
    request = {'context': packet, 'scenes': scenes, 'images': images, 'H': str(trial / 'H'),
               'M_candidate': str(trial / 'M_actions'), 'M_program': str(stage / 'frozen_M' / label),
               'trace_folder': str(trial / 'trace'), 'result_folder': str(trial)}
    write(trial / 'research_request.json', request)
    frozen_sources_before = p.sources(stage / 'frozen_M' / label)
    if not (trial / 'proposal.json').exists():
        command = [sys.executable, str(stage / 'research_worker.py'), 'research', '--request', str(trial / 'research_request.json')]
        with (trial / 'stdout.log').open('w') as stdout, (trial / 'stderr.log').open('w') as stderr:
            c = p.cfg()
            process = p.run_measured(command, timeout=c['pilot']['research_seconds_per_round'],
                      measurement_path=trial / 'research_process.json', memory_limit_bytes=int(c['resources']['memory_limit_gb'] * 1024 ** 3),
                      stdout=stdout, stderr=stderr, env=p.settings_env())
        if process['returncode'] != 0:
            row = {'start': start, 'M': label, 'status': 'failed', 'selected_H': start,
                   'H_candidate': candidate, 'H_accepted': False, 'reason': 'Bounded M worker failed; no extra proposal'}
            write(trial / 'record.json', row)
            return row
    assert p.sources(stage / 'frozen_M' / label) == frozen_sources_before, 'Frozen M source changed during replay'
    proposal = read(trial / 'proposal.json')
    row = {'start': start, 'M': label, 'status': 'unchanged', 'H_candidate': candidate,
           'H_accepted': False, 'selected_H': start, 'reason': 'No shared H change', 'proposal': str(trial / 'proposal.json')}
    row['M_program_unchanged'] = True
    try:
        if any(change['target'] != 'H' for change in proposal['changes']):
            raise ValueError('Frozen replay rejects proposals containing M changes; no partial cherry-pick')
        for change in proposal['changes']:
            relative = Path(change['path'])
            if relative.is_absolute() or '..' in relative.parts or relative.suffix not in {'.py', '.txt', '.md'}:
                raise ValueError('Proposal outside shared H source files')
            if relative.stem in {'runtime', 'processes', 'codex_wrapper', 'evaluate', 'render', 'sceneact', 'budget', 'eval_blend', 'bw_evaluate'}:
                raise ValueError('Proposal shadows fixed evaluator/backend')
            if any(marker in change['content'] for marker in ['commons_', 'bw_00', '/home/', '/srv/']):
                raise ValueError('Shared H patch hardcodes a private task identifier or server path')
            target = trial / 'H' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(change['content'])
        p.validate_side(trial / 'H', 'H')
        before, after = p.sources(p.hpath(start)), p.sources(trial / 'H')
        changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
        (trial / 'H.diff').write_text(''.join(''.join(difflib.unified_diff(before.get(name, '').splitlines(True), after.get(name, '').splitlines(True), fromfile='H_base/' + name, tofile='H_candidate/' + name)) for name in sorted(changed)))
        if changed:
            evaluated = p.run_scene(p.manifest('selection')[0], candidate, label, repeat=1)
            used = {str(Path(path).relative_to(trial / 'H')) for path in evaluated['loaded_H_modules']}
            effective = bool(changed & ({'policy.py', 'system.txt'} | used))
            accepted, gain, recovery = choose(evaluated, parent_selection, p.cfg()['evaluation']['promotion_delta'])
            accepted &= effective
            row.update(status='completed', H_accepted=accepted, selected_H=candidate if accepted else start,
                       selection_BW=evaluated['bw']['S_BW'], selection_gain=gain,
                       changed_source_files=sorted(changed), changed_entry_or_module_executed=effective,
                       reason='Absolute qualification recovery' if accepted and recovery else 'Frozen absolute qualification then BW gain rule')
    except (ValueError, SyntaxError, ImportError) as error:
        row.update(status='invalid', reason=repr(error))
    write(trial / 'record.json', row)
    return row


def write_report(stage, rows):
    """Only saved replay outcomes; never reuse the ten-round report or draw empty gains."""
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    pairs = []
    for index in range(2):
        by_m = {r['M']: r for r in rows if r['start'] == f'B{index:02d}'}
        valid = len(by_m) == 2 and all(r['status'] in {'completed', 'unchanged'} and r.get('M_program_unchanged') is True
                and r['test_valid'] and r['test_functional_pass'] and r['base_test_functional_pass']
                and r['test_gain'] is not None for r in by_m.values())
        pairs.append({'start': f'B{index:02d}', 'complete_valid_pair': valid,
                      'M0_test_gain': by_m['M0']['test_gain'], 'Mfinal_test_gain': by_m['Mfinal']['test_gain'],
                      'paired_gain_difference': by_m['Mfinal']['test_gain'] - by_m['M0']['test_gain'] if valid else None})
    complete = sum(pair['complete_valid_pair'] for pair in pairs)
    summary = {'status': 'completed' if complete == 2 else 'partial', 'scheduled_trials': 4,
               'terminal_trials': len(rows), 'complete_valid_paired_starts': complete,
               'independent_test_sources': 1, 'unfamiliar_H_conditions': 2, 'K': 1,
               'MetaImp_at_1': sum(pair['paired_gain_difference'] for pair in pairs) / 2 if complete == 2 else None,
               'promotion_delta': read(stage / 'stage_freeze.json')['promotion_delta'],
               'pairs': pairs, 'meta_capability_conclusion': 'Feasibility only; one continuous V3 trajectory, two H conditions and one Test source cannot establish general recursive improvement',
               'data_source': 'replay_results.csv and each trial/results record', 'plot_script': str(Path(__file__).resolve())}
    write(stage / 'replay_summary.json', summary)
    figures = stage / 'figures'
    figures.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    for label, offset, color in [('M0', -.08, '#3465a4'), ('Mfinal', .08, '#c43c39')]:
        visible = [(i, next(r for r in rows if r['start'] == f'B{i:02d}' and r['M'] == label)['test_gain']) for i in range(2)]
        visible = [(i, value) for i, value in visible if value is not None]
        if visible:
            ax.scatter([i + offset for i, _ in visible], [value for _, value in visible], color=color, label=label)
    ax.set_xticks([0, 1], ['original H0', 'V2.4 shared candidate'])
    ax.set_ylabel('Selected H Test BW - same starting H Test BW')
    ax.set_title('Frozen M replay: raw points; same Test source ' + TEST)
    if any(r['test_gain'] is not None for r in rows):
        ax.axhline(0, color='gray', linewidth=.7)
        ax.legend()
    else:
        ax.text(.5, .5, 'No measured paired Test gains', transform=ax.transAxes, ha='center')
    fig.tight_layout()
    fig.savefig(figures / 'replay_paired_points.png', dpi=140)
    plt.close(fig)
    columns = ['start', 'M', 'status', 'selected_H', 'test_gain', 'test_functional_pass', 'test_H_reuse', 'research_cli_sessions', 'research_diagnostic_frames']
    header = '<tr>' + ''.join('<th>' + key + '</th>' for key in columns) + '</tr>'
    table = ''.join('<tr>' + ''.join('<td>' + html.escape(str(row.get(key))) + '</td>' for key in columns) + '</tr>' for row in rows)
    panels = []
    for row in rows:
        image = stage / 'results' / row['selected_H'] / 'test' / TEST / '1/final.png'
        panels.append('<figure><figcaption>' + html.escape(row['start'] + '/' + row['M'] + ': ' + row['selected_H']) +
                      '</figcaption>' + ('<img src="' + str(image.relative_to(stage)) + '">' if image.exists() else '<p>No valid rendered output</p>') + '</figure>')
    (stage / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>冻结M回放</title><style>body{font-family:sans-serif;max-width:1100px;margin:auto}img{max-width:100%}figure{width:46%;display:inline-block}td,th{padding:6px;border:1px solid #ccc}table{border-collapse:collapse}</style><h1>冻结 M 的 K=1 回放</h1><p>仅本阶段真实产物；不是额外十轮。2个H起点、1个Selection来源、1个Test来源。完整有效配对=' + str(complete) + '/2；MetaImp@1=' + str(summary['MetaImp_at_1']) + '。样本极小，不能据此宣称普遍元能力提升。</p><img src="figures/replay_paired_points.png"><table>' + header + table + '</table>' + ''.join(panels) + '<p><a href="replay_results.csv">逐提案CSV</a> / <a href="replay_results.json">原始JSON</a> / <a href="joint_ledger.json">联合成本</a> / <a href="final_selection_freeze.json">选择冻结</a> / <a href="REPLAY_PROTOCOL.md">独立协议</a></p><p>图中的点为同一Test图在不同H起点条件的结果，不是两张独立测试图。缺测不填零；失败与回退保留。M0/Mfinal使用相同显式开发档案，研究成本为实际可见会话与诊断扣额；共享基线/评价成本在联合账中单列，不重复分摊。机械功能通过不等于人类语义验证。BW-style / CLI-adapted。</p>')
    markdown = ['# 冻结M回放：实际结果', '', '状态：'+summary['status']+'；完整有效配对起点 '+str(complete)+'/2；MetaImp@1='+str(summary['MetaImp_at_1'])+'。', '',
                '仅1个Selection来源、1个Test来源和2个H起点条件，不是2张独立Test图；单次生成波动和同模型评审偏差仍存在，不能宣称普遍元能力提升。', '',
                '|起点|M|提案状态|所选H|Test ΔBW|功能保持|产物复用|研究CLI|', '|---|---|---|---|---|---|---|---|']
    markdown += ['|'+'|'.join(str(row.get(key)) for key in ['start','M','status','selected_H','test_gain','test_functional_pass','test_H_reuse','research_cli_sessions'])+'|' for row in rows]
    markdown += ['', '![原始配对点](figures/replay_paired_points.png)', '', '来源：[逐提案CSV](replay_results.csv)、[原始JSON](replay_results.json)、[配对汇总](replay_summary.json)；真实全量CLI与场景记录见trials/和results/；成本见[joint_ledger.json](joint_ledger.json)。未知/缺测保留null，完整有效配对不足时MetaImp为null。']
    (stage / 'REPORT_ZH.md').write_text('\n'.join(markdown)+'\n')
    return summary


def run(main, stage):
    _, problems = main_completion_check(main)
    if problems:
        raise RuntimeError('Replay pending: ' + '; '.join(problems))
    if not stage.exists():
        audit = readiness(main)
        if audit['status'] != 'ready_for_root_execution_decision':
            raise RuntimeError('Replay pending: ' + '; '.join(audit['reasons']))
        prepare(main, stage, audit)
    if (stage / 'state.json').exists() and read(stage / 'state.json')['phase'] == 'all_scheduled_terminal':
        print('Frozen replay already terminal; no new proposal or resampling')
        return
    assert read(stage / 'stage_freeze.json')['fixed_platform_snapshot']['version'] == PLATFORM_VERSION
    p = load_platform(stage)
    rows = []
    for index in range(2):
        start = f'B{index:02d}'
        dev = [p.run_scene(s, start, 'shared_frozen_replay', repeat=1, evaluate_bw=False) for s in p.manifest('development')]
        parent = p.run_scene(p.manifest('selection')[0], start, 'shared_frozen_replay', repeat=1)
        order = ['M0', 'Mfinal'] if index == 0 else ['Mfinal', 'M0']
        for label in order:
            rows.append(run_trial(p, stage, start, label, dev, parent))
    write(stage / 'final_selection_freeze.json', {'time': time.time(), 'all_four_K1_trials_terminal': True,
          'selection_only': True, 'choices': rows, 'no_Test_feedback_used': True})
    for index in range(2):
        start = f'B{index:02d}'
        baseline = p.run_scene(p.manifest('test')[0], start, 'shared_frozen_replay', repeat=1)
        for row in [r for r in rows if r['start'] == start]:
            tested = p.run_scene(p.manifest('test')[0], row['selected_H'], row['M'], repeat=1)
            both = tested['bw']['evaluation_status'] == baseline['bw']['evaluation_status'] == 'completed'
            row.update(test_BW=tested['bw']['S_BW'], base_test_BW=baseline['bw']['S_BW'],
                       test_gain=tested['bw']['S_BW'] - baseline['bw']['S_BW'] if both else None,
                       test_H_reuse=row['selected_H'] == start, test_valid=tested['valid'],
                       test_functional_pass=tested['functional']['functional_pass'],
                       base_test_functional_pass=baseline['functional']['functional_pass'],
                       test_Q=tested['metrics']['overall'], base_test_Q=baseline['metrics']['overall'],
                       test_Q_gain=tested['metrics']['overall'] - baseline['metrics']['overall']
                                   if tested['metrics']['overall'] is not None and baseline['metrics']['overall'] is not None else None,
                       test_e2e_utility=tested['e2e_utility'], base_test_e2e_utility=baseline['e2e_utility'])
            trace = stage / 'trials' / (row['start'] + '_' + row['M']) / 'trace'
            row['research_cli_sessions'] = len(list(trace.glob('calls/*/request.json')))
            row['research_diagnostic_frames'] = sum(1 for path in trace.glob('actions/*/settings.json'))
    write(stage / 'replay_results.json', rows)
    fields = ['start', 'M', 'status', 'H_candidate', 'H_accepted', 'selected_H', 'selection_BW', 'selection_gain',
              'test_BW', 'base_test_BW', 'test_gain', 'test_H_reuse', 'test_valid', 'test_functional_pass', 'reason']
    fields += ['test_Q', 'base_test_Q', 'test_Q_gain', 'test_e2e_utility', 'base_test_e2e_utility', 'M_program_unchanged']
    fields += ['base_test_functional_pass', 'research_cli_sessions', 'research_diagnostic_frames']
    with (stage / 'replay_results.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows([{key: row.get(key) if row.get(key) is not None else 'null' for key in fields} for row in rows])
    freeze = read(stage / 'stage_freeze.json')
    joint = {'main_plus_stage_CLI_and_tokens': usage(main), 'stage_only': usage(stage),
             'combined_render_budget_charged': freeze['audit']['global_usage_before_stage']['render_attempts'] + usage(stage)['render_attempts'],
             'no_model_request_count_or_fee_inferred': True, 'scope': 'Main is terminal; no double-counting nested stage CLI/token'}
    write(stage / 'joint_ledger.json', joint)
    summary = write_report(stage, rows)
    receipt = {'status': summary['status'], 'scheduled_trials': 4, 'terminal_trials': len(rows),
               'complete_valid_paired_starts': summary['complete_valid_paired_starts'],
               'MetaImp_at_1': summary['MetaImp_at_1'], 'entry_returned_success': True,
               'scientific_conclusion': 'Feasibility only, not established general M ability improvement',
               'report': str(stage / 'index.html'), 'raw_results': str(stage / 'replay_results.csv'),
               'joint_ledger': str(stage / 'joint_ledger.json')}
    write(stage / 'COMPLETION_RECEIPT.json', receipt)
    write(main / 'META_REPLAY_STATUS.json', {**receipt, 'independent_stage_receipt': str(stage / 'COMPLETION_RECEIPT.json'),
          'main_scores_or_selection_modified': False})
    write(stage / 'state.json', {'phase': 'all_scheduled_terminal', 'completed_trials': len(rows),
          'formal_V3_rounds_added': 0, 'M_evolution_allowed': False, 'meta_capability_claim': 'Feasibility only; two starts with one proposal each do not establish general recursive improvement'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'prepare', 'run', 'resume', '_bounded_worker'])
    parser.add_argument('--main', type=Path, default=PROJECT / 'outputs/scene_rsi_v3')
    args = parser.parse_args()
    main_root = args.main.resolve()
    if args.command == 'audit':
        result = readiness(main_root)
        write(HERE / 'LATEST_READINESS.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == 'prepare':
        result = readiness(main_root)
        entry = {'status': 'ready' if result['status'] == 'ready_for_root_execution_decision' else 'pending',
                 'eligibility': result['eligibility'], 'budget': result['budget'],
                 'command': [sys.executable, str(Path(__file__).resolve()), 'run', '--main', str(main_root)],
                 'timeout_seconds': 36 * 3600, 'readiness': result,
                 'new_model_calls': 0, 'new_Blender_jobs': 0}
        stage = main_root / 'meta_replay_stage'
        if stage.exists():
            entry['status'] = 'skipped' if (stage / 'state.json').exists() and read(stage / 'state.json')['phase'] == 'all_scheduled_terminal' else 'pending'
            entry['eligibility'] = {'eligible': False, 'reason': 'Stage already exists; never start a duplicate or silently resample. Explicit resume requires its own review.'}
        write(HERE / 'entry.json', entry)
        print(json.dumps({'entry_json': str(HERE / 'entry.json')}))
    elif args.command == '_bounded_worker':
        run(main_root, main_root / 'meta_replay_stage')
    else:
        # Match the V3 launcher's whole-tree CPU/RSS bound without editing it.
        _, problems = main_completion_check(main_root)
        if problems:
            raise RuntimeError('Replay pending: ' + '; '.join(problems))
        platform = platform_snapshot_audit(main_root)
        if not platform['eligible']:
            raise RuntimeError('Replay pending: ' + platform['reason'])
        platform_root = Path(platform['source'])
        sys.path.insert(0, str(platform_root / 'backend'))
        from processes import cpu_environment, run_measured
        c = read(platform_root / 'config.json')
        with (HERE / 'replay_execution.lock').open('a') as own_lock, (main_root / 'experiment.lock').open('r') as main_lock:
            fcntl.flock(own_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(main_lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            os.sched_setaffinity(0, set(c['resources']['cpu_affinity']))
            launches = HERE / 'launches'
            launches.mkdir(exist_ok=True)
            number = len(list(launches.glob('*_process.json'))) + 1
            command = [sys.executable, str(Path(__file__).resolve()), '_bounded_worker', '--main', str(main_root)]
            environment = cpu_environment(threads=c['resources']['threads_per_blender'])
            environment['MPLCONFIGDIR'] = str(main_root / 'meta_replay_stage/matplotlib_cache')
            result = run_measured(command, timeout=36 * 3600 - 60, measurement_path=launches / f'{number:03d}_process.json',
                                  memory_limit_bytes=int(c['resources']['memory_limit_gb'] * 1024 ** 3),
                                  env=environment)
            if result['returncode'] != 0:
                stage = main_root / 'meta_replay_stage'
                write(main_root / 'META_REPLAY_STATUS.json', {'status': 'partial' if list(stage.glob('trials/*/record.json')) else 'pending',
                      'reason': 'Bounded post-stage worker did not return success', 'process': str(launches / f'{number:03d}_process.json'),
                      'MetaImp_at_1': None, 'main_scores_or_selection_modified': False})
            raise SystemExit(result['returncode'])


if __name__ == '__main__':
    main()
