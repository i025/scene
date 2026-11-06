"""Offline V2.4 tables, figures and report from existing evidence only."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import html
import json
import os
import textwrap

for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS']:
    os.environ[key] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ.setdefault('MPLCONFIGDIR', '/tmp/scene-rsi-v24-report-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
METHODS = ['fixed', 'structured', 'active']
LABELS = {'reference': 'Fresh H_start', 'fixed': 'Fixed', 'structured': 'Structured', 'active': 'Active'}
COLORS = {'reference': '#555b68', 'fixed': '#718096', 'structured': '#c98a23', 'active': '#287f8e'}
TERMINAL = {'completed', 'failed', 'timeout', 'invalid'}
TOLERANCE = .01


def read(path):
    return json.loads(path.read_text())


def optional(path):
    return read(path) if path.exists() else None


def relative(path):
    return str(path.relative_to(ROOT))


def table(name, rows):
    path = ROOT/'metrics'/name
    path.with_suffix('.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.with_suffix('.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                         for key, value in row.items()} for row in rows)


def eligible(record):
    if record is None:
        return None
    if not record['metrics']['valid'] or record['status'] != 'complete':
        return False
    checks = record['functional']['checks']
    return bool(checks) and all(not check['required'] or
        (check['applicable'] is True and check['measured_pass'] is True and check['gate_pass'] is True)
        for check in checks.values())


def state(record, folder):
    if record is not None:
        if record['status'] == 'complete':
            return 'completed'
        error = str(record['runtime_status']['error'])
        return 'timeout' if 'TimeoutExpired' in error or 'outer_scene_deadline' in error or record['failure_type'] == 'budget_or_scene_timeout' else 'failed'
    return 'running' if (folder/'task.json').exists() else 'not_started'


def collect_scenes(manifest, final):
    rows = []
    for task in manifest:
        task_id = task['task_id']
        smoke = task_id.startswith('smoke')
        methods = ['active'] if smoke else ['reference', *METHODS]
        roles = ['source'] if smoke else ['source', 'transfer']
        for method in methods:
            cid = 'H_start' if method == 'reference' else 'C1'
            failure = optional(ROOT/'tasks'/task_id/method/'failure.json')
            for role in roles:
                scene = task[role]
                folder = ROOT/'results'/task_id/method/cid/scene['split']/scene['scene_id']
                record = optional(folder/'record.json')
                status = state(record, folder)
                terminal = status in TERMINAL or (final and status == 'not_started')
                metrics = record['metrics'] if record else None
                valid = metrics['valid'] if metrics else None
                measured = metrics if valid else None
                checks = record['functional']['checks'] if record else None
                reason = (record['failure_type'] if record and not valid else
                          failure['error'] if failure and record is None else
                          'Scheduled evaluation not executed before terminal workflow' if final and record is None else None)
                rows.append({'method': method, 'run_id': task_id, 'task_id': task_id, 'candidate_id': cid,
                    'parent': 'fixed_h/r1_C2', 'H_version': record['H_version'] if record else
                        'fixed_h/r1_C2' if method == 'reference' else 'tasks/'+task_id+'/'+method+'/H',
                    'M_version': 'engineered_v2_4' if method != 'reference' else None,
                    'scene_id': scene['scene_id'], 'split': scene['split'], 'role': role,
                    'scope': 'smoke' if smoke else 'formal', 'status': status,
                    'original_status': record['status'] if record else None, 'schedule_terminal': terminal,
                    'execution_success': valid, 'functional_eligible': eligible(record),
                    'Q': measured['overall'] if measured else None,
                    'PSNR': measured['psnr'] if measured else None,
                    'SSIM': measured['ssim'] if measured else None,
                    'LPIPS': measured['lpips'] if measured else None,
                    'DINOv2': measured['dino'] if measured else None,
                    'failure_utility': (metrics['overall'] if valid else 0) if record else 0 if terminal else None,
                    'failure_reason': reason, 'function_checks': checks,
                    'blend_opened_measured': checks['structure']['applicable'] if checks else None,
                    'blend_file_exists': (folder/'scene.blend').exists(),
                    'scene_pipeline_seconds': record['seconds'] if record else None,
                    'inner_runtime_seconds': record['runtime_status']['seconds'] if record else None,
                    'resource_wait_seconds': record['resource_wait_seconds'] if record else None,
                    'service_queue_seconds': record['service_queue_seconds'] if record else None,
                    'device': record['device'] if record else None, 'threads': 2,
                    'model_roles': record['model_roles'] if record else None,
                    'record_path': relative(folder/'record.json'), 'folder': relative(folder),
                    'reference_image': relative(folder/'reference.png'), 'render_image': relative(folder/'final.png'),
                    'expected_composite': scene['expected_composite']})
    return rows


def collect_candidates(manifest, scenes, final):
    frozen = optional(ROOT/'configs/selection_freeze.json')
    choices = {(s['task_id'], s['method']): s for s in frozen['selections']} if frozen else {}
    lookup = {(r['task_id'], r['method'], r['role']): r for r in scenes}
    candidates, forecasts, observations = [], [], []
    for task in manifest:
        task_id = task['task_id']
        if task_id.startswith('smoke'):
            continue
        for method in METHODS:
            dest = ROOT/'tasks'/task_id/method
            candidate = optional(dest/'candidate.json')
            failure = optional(dest/'failure.json')
            stage1 = optional(dest/'stage1.json')
            stage2 = optional(dest/'stage2.json')
            observed = optional(dest/'observations.json')
            observed = observed if observed is not None else []
            diagnosis = optional(dest/'diagnosis/session.json')
            status = 'completed' if candidate else 'failed' if failure else 'running' if stage1 or diagnosis else 'not_started'
            baseline_s, baseline_t = [lookup[(task_id, 'reference', role)] for role in ['source', 'transfer']]
            source, transfer = [lookup[(task_id, method, role)] for role in ['source', 'transfer']]
            ds = source['Q']-baseline_s['Q'] if source['Q'] is not None and baseline_s['Q'] is not None else None
            dt = transfer['Q']-baseline_t['Q'] if transfer['Q'] is not None and baseline_t['Q'] is not None else None
            ready = all(r['schedule_terminal'] for r in [source, transfer, baseline_s, baseline_t])
            source_gain = (source['functional_eligible'] is True and ds is not None and ds > TOLERANCE) if source['schedule_terminal'] and baseline_s['schedule_terminal'] else None
            transfer_ok = (transfer['functional_eligible'] is True and dt is not None and dt >= -TOLERANCE) if transfer['schedule_terminal'] and baseline_t['schedule_terminal'] else None
            strong = (transfer['functional_eligible'] is True and dt is not None and dt > TOLERANCE) if transfer['schedule_terminal'] and baseline_t['schedule_terminal'] else None
            effective = bool(source_gain and transfer_ok) if ready else None
            chosen = choices[(task_id, method)]['selected'] if (task_id, method) in choices else None
            selected_row = transfer if chosen == 'C1' else baseline_t if chosen == 'H_start' else None
            selected_q = selected_row['Q'] if selected_row else None
            selected_delta = selected_q-baseline_t['Q'] if selected_q is not None and baseline_t['Q'] is not None else None
            changes = []
            for name in ['policy.py', 'system.txt']:
                diff = dest/(name+'.diff')
                if diff.exists():
                    lines = diff.read_text().splitlines()
                    added = sum(s.startswith('+') and not s.startswith('+++') for s in lines)
                    removed = sum(s.startswith('-') and not s.startswith('---') for s in lines)
                    if added or removed:
                        changes.append({'file': name, 'added_lines': added, 'removed_lines': removed,
                                        'diff_path': relative(diff)})
            decision = stage2['M_decision'] if stage2 else None
            completed_probes = [o for o in observed if o['status'] == 'completed']
            measurable = [o for o in completed_probes if o['outcome'] is not None]
            selected_module = decision['selected_module'] if decision else None
            row = {'method': method, 'run_id': task_id, 'task_id': task_id, 'candidate_id': 'C1', 'parent': 'H_start',
                'source_scene': task['source']['scene_id'], 'transfer_scene': task['transfer']['scene_id'],
                'H_version': candidate['H_version'] if candidate else None, 'M_version': 'engineered_v2_4',
                'status': status, 'failure_reason': failure['error'] if failure else None,
                'candidate_type': candidate['type'] if candidate else None,
                'source_status': source['status'], 'transfer_status': transfer['status'],
                'source_Q': source['Q'], 'fresh_H_start_source_Q': baseline_s['Q'], 'source_delta_Q': ds,
                'transfer_Q': transfer['Q'], 'fresh_H_start_transfer_Q': baseline_t['Q'], 'raw_candidate_transfer_delta_Q': dt,
                'source_functional_eligible': source['functional_eligible'], 'transfer_functional_eligible': transfer['functional_eligible'],
                'source_execution_recovery': (baseline_s['execution_success'] is False and source['execution_success'] is True) if source['schedule_terminal'] and baseline_s['schedule_terminal'] else None,
                'transfer_execution_recovery': (baseline_t['execution_success'] is False and transfer['execution_success'] is True) if transfer['schedule_terminal'] and baseline_t['schedule_terminal'] else None,
                'source_execution_regression_observed': (baseline_s['execution_success'] is True and source['execution_success'] is False) if source['schedule_terminal'] and baseline_s['schedule_terminal'] else None,
                'transfer_execution_regression_observed': (baseline_t['execution_success'] is True and transfer['execution_success'] is False) if transfer['schedule_terminal'] and baseline_t['schedule_terminal'] else None,
                'strict_source_gain': source_gain, 'transfer_nondegradation': transfer_ok,
                'effective_shared_repair': effective, 'strong_transfer_improvement': strong,
                'effective_with_strong_transfer': bool(effective and strong) if ready else None,
                'all_relevant_evaluations_terminal': ready,
                'actual_selection': chosen, 'selection_record': choices.get((task_id, method)),
                'selected_transfer_Q': selected_q, 'selected_transfer_delta_Q': selected_delta,
                'selected_transfer_execution_success': selected_row['execution_success'] if selected_row else None,
                'selected_transfer_functional_eligible': selected_row['functional_eligible'] if selected_row else None,
                'selection_strict_gain_disagreement': chosen == 'C1' and source_gain is not True if chosen else None,
                'probes_requested': len(stage1['plan']['probes']) if stage1 else None,
                'probes_completed': len(completed_probes), 'probes_measured': len(measurable),
                'M_two_stage_executed': stage2['executed'] if stage2 else None,
                'initial_module': stage1['context']['initial_module'] if stage1 else None,
                'selected_module': selected_module,
                'decision_changed': decision['decision_changed'] if decision else None,
                'forecast_calibration': decision['forecast_calibration'] if decision else None,
                'evidence_ratio': decision['evidence_ratio'] if decision else None,
                'diagnosis_unresolved': selected_module == 'unresolved' if decision else None,
                'probe_based_decision': bool(measurable) if decision else None,
                'changed_files': changes, 'patch_reason': candidate['patch_reason'] if candidate else None,
                'observation_used_claim': candidate['observation_used'] if candidate else None,
                'provenance_limit': 'Coder statement is not an independently verified causal effect of diagnosis.',
                'new_M_descendant': False, 'stage1_path': relative(dest/'stage1.json'),
                'stage2_path': relative(dest/'stage2.json'), 'candidate_path': relative(dest/'candidate.json')}
            candidates.append(row)
            if stage1:
                ctx = stage1['context']
                requested = {p['probe']: p for p in stage1['plan']['probes']}
                result_by_tool = {o['request']['probe']: o for o in observed}
                for hypothesis in ctx['hypotheses']:
                    for tool, interval in hypothesis['predictions'].items():
                        actual = result_by_tool.get(tool)
                        value = actual['outcome'] if actual else None
                        forecasts.append({'task_id': task_id, 'method': method, 'hypothesis': hypothesis['id'],
                            'module': hypothesis['module'], 'object_id': hypothesis['object_id'], 'tool': tool,
                            'selected_probe': tool in requested, 'lower': interval['lower'], 'upper': interval['upper'],
                            'reason': interval['reason'], 'observation_balanced_outcome': value,
                            'outcome_definition': '.5*global_delta_SSIM+.5*fixed_reference_ROI_delta_SSIM',
                            'interval_contains_observation': interval['lower'] <= value <= interval['upper'] if value is not None else None,
                            'measurement_status': actual['status'] if actual else 'not_requested',
                            'saved_before_probe': stage1['saved_before_probe'], 'stage1_path': relative(dest/'stage1.json'),
                            'interpretation': 'Subjective forecasts for competing hypotheses, no known true module or calibrated probability.'})
            for index, actual in enumerate(observed, 1):
                pd = dest/'probes'/str(index)
                process = optional(pd/'process.json')
                observations.append({'task_id': task_id, 'method': method, 'probe_index': index,
                    'tool': actual['request']['probe'], 'object_id': actual['request']['object_id'],
                    'predicted_discrimination': actual['request']['predicted_discrimination'],
                    'status': actual['status'], 'delta_SSIM': actual['delta_ssim'],
                    'delta_ROI_SSIM': actual['delta_roi_ssim'], 'balanced_outcome': actual['outcome'],
                    'reference_ROI': stage1['context']['reference_roi'],
                    'blender_seconds': process['seconds'] if process else None,
                    'image': relative(pd/('probe_'+actual['request']['probe']+'.png')),
                    'measurement': actual['measurement'], 'evidence_path': relative(dest/'observations.json')})
    return candidates, forecasts, observations


def collect_costs(scenes):
    calls = []
    for path in sorted(ROOT.rglob('session.json')):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in ['audit_sources', 'code_snapshots'] or not path.with_name('request.json').exists():
            continue
        session = read(path)
        parts = rel.parts
        task_id = parts[1] if parts[0] in ['tasks', 'results'] else None
        method = next((part for part in parts if part in [*METHODS, 'reference']), None)
        scope = 'formal' if task_id in ['task01', 'task02'] else 'smoke' if task_id and task_id.startswith('smoke') else 'preparation'
        group = 'common_H_start' if method == 'reference' else method if scope == 'formal' and method else scope
        calls.append({'path': str(rel), 'task_id': task_id, 'method': method, 'scope': scope, 'cost_group': group,
            'role': session['role'], 'requested_model': session['requested_model'],
            'actual_returned_model': session['actual_model'], 'effort': session['reasoning_effort'],
            'status': session['status'], 'exit_code': session.get('exit_code'),
            'input_tokens': session['input_tokens'] if isinstance(session['input_tokens'], int) else None,
            'output_tokens': session['output_tokens'] if isinstance(session['output_tokens'], int) else None,
            'observable_cli_turns': session.get('observable_cli_turns'), 'underlying_model_rounds': None,
            'tool_calls': session.get('tool_calls'), 'seconds': session.get('seconds'), 'cost_USD': None})
    costs = []
    for group in [*METHODS, 'common_H_start', 'smoke', 'preparation']:
        owned = [c for c in calls if c['cost_group'] == group]
        selected = [r for r in scenes if (r['scope'] == 'formal' and r['method'] == group) or
                    (group == 'common_H_start' and r['scope'] == 'formal' and r['method'] == 'reference') or
                    (group == 'smoke' and r['scope'] == 'smoke')]
        pipeline_seconds = [r['scene_pipeline_seconds'] for r in selected if r['scene_pipeline_seconds'] is not None]
        if group == 'smoke':
            # Keep earlier real smoke attempts after they move to labelled paths.
            selected = []
            pipeline_seconds = []
            for path in sorted((ROOT/'results').glob('smoke*/*/*/*/*/record.json')):
                saved = read(path)
                selected.append({'folder': relative(path.parent)})
                pipeline_seconds.append(saved['seconds'])
        execution_seconds = []
        for row in selected:
            for path in sorted((ROOT/row['folder']).glob('steps/*/result.json')):
                execution_seconds.append(read(path)['seconds'])
        probes = []
        if group in METHODS:
            probes = [read(p) for p in sorted((ROOT/'tasks').glob('task*/'+group+'/probes/*/process.json'))]
        elif group == 'smoke':
            probes = [read(p) for p in sorted((ROOT/'tasks').glob('smoke*/*/probes/*/process.json'))]
        costs.append({'cost_group': group, 'CLI_sessions': len(owned), 'CLI_status_counts': dict(Counter(c['status'] for c in owned)),
            'role_counts': dict(Counter(c['role'] for c in owned)),
            'known_input_tokens': sum(c['input_tokens'] for c in owned if c['input_tokens'] is not None),
            'known_output_tokens': sum(c['output_tokens'] for c in owned if c['output_tokens'] is not None),
            'usage_unknown_sessions': sum(c['input_tokens'] is None or c['output_tokens'] is None for c in owned),
            'model_wall_seconds_known': sum(c['seconds'] for c in owned if c['seconds'] is not None),
            'model_seconds_unknown_sessions': sum(c['seconds'] is None for c in owned),
            'reconstruction_pipeline_seconds': sum(pipeline_seconds),
            'inner_Blender_execution_seconds': sum(execution_seconds),
            'probe_process_count': len(probes), 'probe_Blender_seconds': sum(p['seconds'] for p in probes),
            'timing_limit': 'Scene pipeline includes model and execution time; overlapping components must not be summed. Queue and pure model inference are not separately measured.'})
    ledgers = [read(path) for path in ROOT.rglob('render_ledger.json') if path.relative_to(ROOT).parts[0] not in ['audit_sources', 'code_snapshots']]
    steps = [p for p in ROOT.glob('results/*/*/*/*/*/steps/*/build.py')]
    totals = {'CLI_sessions': len(calls), 'known_input_tokens': sum(c['input_tokens'] for c in calls if c['input_tokens'] is not None),
        'known_output_tokens': sum(c['output_tokens'] for c in calls if c['output_tokens'] is not None),
        'usage_unknown_sessions': sum(c['input_tokens'] is None or c['output_tokens'] is None for c in calls),
        'observable_cli_turns': sum(c['observable_cli_turns'] or 0 for c in calls), 'underlying_model_rounds': None,
        'render_attempts_upper_bound': len(steps)+sum(d['render_attempts'] for d in ledgers),
        'renders_completed': sum(p.with_name('final.png').exists() for p in steps)+sum(d['renders_completed'] for d in ledgers),
        'historical_audit_and_reused_image_cost': 'Excluded from new-session/render totals; historical provenance preserved separately.',
        'device': 'CPU', 'threads': 2, 'max_concurrent_heavy_jobs': 1, 'GPUs_used': 0}
    limits = read(ROOT/'config.json')['pilot']
    totals.update(max_CLI_sessions=limits['max_cli_sessions'], max_render_frames=limits['max_render_frames'])
    return calls, costs, totals


def preparation_rows():
    rows = []
    for path in sorted((ROOT/'tasks').glob('smoke*/*/diagnosis/session.json')):
        dest = path.parent.parent
        stage1 = optional(dest/'stage1.json')
        stage2 = optional(dest/'stage2.json')
        obs = optional(dest/'observations.json')
        session = read(path)
        rows.append({'attempt_folder': relative(dest), 'CLI_status': session['status'],
            'stage1_saved': stage1 is not None, 'M_stage2_executed': stage2['executed'] if stage2 else None,
            'probes_requested': len(stage1['plan']['probes']) if stage1 else None,
            'probes_completed': sum(o['status'] == 'completed' for o in obs) if obs is not None else None,
            'forecast_menu': list(stage1['context']['hypotheses'][0]['predictions']) if stage1 else None,
            'failure_record': optional(dest/'failure.json'),
            'status_limit': 'A saved response without stage1 is not an accepted executable diagnosis. Retained attempts do not become independent formal samples.'})
    return rows


def structural_rows():
    path = ROOT/'tests/calibration.json'
    if not path.exists():
        return []
    data = read(path)
    menu = [('correct', 'hierarchy_parts', True), ('missing_declared_part', 'hierarchy_parts', False),
            ('detached', 'hierarchy_parts', False), ('broken_support', 'known_support', False),
            ('shared_material_bad_edit', None, False), ('independent_local_edit', None, True),
            ('correct_group_move', None, True), ('triangle_crossing', 'mesh_intersection', False)]
    result = []
    for name, test, expected in menu:
        measured = data[name][test] if test else data[name]
        passed = measured['measured_pass'] if 'measured_pass' in measured else measured['pass']
        result.append({'case': name, 'check': test or name, 'expected_measured_pass': expected,
            'actual_measured_pass': passed, 'expected_behavior_detected': passed is expected,
            'measurement': measured, 'source': 'tests/calibration.json',
            'scope': 'Deterministic fixture calibration; mechanical operation, not text editing or natural-image 3D truth.'})
    return result


def counts(values):
    return {'passed': sum(v is True for v in values), 'measured': sum(v is not None for v in values),
            'scheduled': len(values), 'pending_or_missing': sum(v is None for v in values)}


def summarize(scenes, candidates, totals):
    result = {'methods': {}, 'cost': totals, 'M_automatic_descendants': 0,
              'localization_accuracy': None, 'module_accuracy': None,
              'accuracy_unavailable_reason': 'Natural images have no known faulty object/module truth.',
              'strict_effective_rule': 'Source eligible and paired Q gain >0.01; transfer eligible and paired Q delta >=-0.01. Missing measured Q cannot establish gain.',
              'selection_policy_note': 'As-run source Selection reuses the diagnosis/coding image; no independent validation. Runner selects any eligible candidate over an ineligible baseline, even when baseline has measured Q. Actual choices preserved; strict Q gain is a separate derived field.'}
    for method in ['reference', *METHODS]:
        rows = [r for r in scenes if r['scope'] == 'formal' and r['method'] == method]
        arms = [c for c in candidates if c['method'] == method]
        valid = [r['Q'] for r in rows if r['Q'] is not None]
        result['methods'][method] = {'scene_tasks_scheduled': len(rows),
            'scene_status_counts': dict(Counter(r['status'] for r in rows)),
            'scene_tasks_terminal': sum(r['schedule_terminal'] for r in rows),
            'execution': counts([r['execution_success'] if r['execution_success'] is not None else
                                 False if r['schedule_terminal'] else None for r in rows]),
            'functional': counts([r['functional_eligible'] if r['functional_eligible'] is not None else
                                  False if r['schedule_terminal'] else None for r in rows]),
            'conditional_Q_mean': sum(valid)/len(valid) if valid else None, 'conditional_Q_n': len(valid),
            'failure_utility_mean': sum(r['failure_utility'] for r in rows)/len(rows) if rows and all(r['failure_utility'] is not None for r in rows) else None,
            'candidates_scheduled': len(arms), 'generated_candidates': sum(c['status'] == 'completed' for c in arms),
            'candidate_status_counts': dict(Counter(c['status'] for c in arms)),
            'effective_shared_repair': counts([c['effective_shared_repair'] for c in arms]),
            'strong_transfer_improvement': counts([c['strong_transfer_improvement'] for c in arms]),
            'actual_selected_C1': sum(c['actual_selection'] == 'C1' for c in arms),
            'probes_requested': sum(c['probes_requested'] or 0 for c in arms),
            'probes_completed': sum(c['probes_completed'] for c in arms),
            'probes_measured': sum(c['probes_measured'] for c in arms),
            'M_stage2_executed': sum(c['M_two_stage_executed'] is True for c in arms),
            'forecast_calibration_counts': dict(Counter(c['forecast_calibration'] for c in arms if c['forecast_calibration'])),
            'unresolved': sum(c['diagnosis_unresolved'] is True for c in arms)}
    return result


def font(size=15):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def tile(canvas, path, box, caption, missing_label='No output / pending'):
    draw = ImageDraw.Draw(canvas)
    x, y, w, h = box
    if path.exists():
        picture = ImageOps.contain(Image.open(path).convert('RGB'), (w-12, h-55))
        canvas.paste(picture, (x+(w-picture.width)//2, y+4))
    else:
        draw.rectangle((x+5, y+5, x+w-5, y+h-55), outline='#b9bec6')
        draw.text((x+15, y+35), missing_label, fill='#9c3f37', font=font())
    for index, line in enumerate(textwrap.wrap(caption, width=max(15, w//8))[:3]):
        draw.text((x+6, y+h-50+index*16), line, fill='#252c35', font=font(12))


def contacts(manifest, scenes, candidates):
    tasks = [t for t in manifest if not t['task_id'].startswith('smoke')]
    historical = []
    canvas = Image.new('RGB', (1024, 285*len(tasks)), 'white')
    draw = ImageDraw.Draw(canvas)
    for index, task in enumerate(tasks):
        folder = ROOT/'tasks'/task['task_id']/'evidence'
        old = read(folder/'record.json')
        tile(canvas, folder/'reference.png', (0, index*285, 350, 280), task['source']['scene_id']+' photograph')
        tile(canvas, folder/'final.png', (350, index*285, 350, 280), 'V2.2 historical P; Q='+format(old['metrics']['overall'], '.4f'))
        draw.text((710, index*285+15), 'Historical diagnosis input', fill='#1d4b5c', font=font(16))
        draw.text((710, index*285+45), 'Not a fresh H_start result', fill='#9b4933', font=font(15))
        for line_no, line in enumerate(textwrap.wrap(task['source']['scene_id']+'; previously exposed natural image, no injected fault labels.', 32)):
            draw.text((710, index*285+80+line_no*22), line, fill='black', font=font())
        historical.append({'task_id': task['task_id'], 'scene_id': task['source']['scene_id'],
            'historical_Q': old['metrics']['overall'], 'reference': relative(folder/'reference.png'),
            'historical_render': relative(folder/'final.png'), 'origin': 'V2.2 copied P and render, not a new evaluation'})
    canvas.save(ROOT/'figures/figure2_natural_diagnosis_inputs.png')
    table('historical_diagnostic_inputs', historical)
    rows = [r for r in scenes if r['scope'] == 'formal']
    lookup = {(r['task_id'], r['role'], r['method']): r for r in rows}
    canvas = Image.new('RGB', (1280, 245*len(tasks)*2+130+len(candidates)*45), 'white')
    draw = ImageDraw.Draw(canvas)
    for col, label in enumerate(['Reference', 'Fresh H_start', 'Fixed raw C1', 'Structured raw C1', 'Active raw C1']):
        draw.text((col*256+7, 10), label, font=font(15), fill='black')
    line = 0
    for task in tasks:
        for role in ['source', 'transfer']:
            baseline = lookup[(task['task_id'], role, 'reference')]
            reference = ROOT/baseline['reference_image']
            if role == 'source' and not reference.exists():
                reference = ROOT/'tasks'/task['task_id']/'evidence/reference.png'
            y = 40+line*245
            tile(canvas, reference, (0, y, 256, 240), task[role]['scene_id']+' '+role)
            for col, method in enumerate(['reference', *METHODS], 1):
                row = lookup[(task['task_id'], role, method)]
                q = format(row['Q'], '.4f') if row['Q'] is not None else 'null'
                tile(canvas, ROOT/row['render_image'], (col*256, y, 256, 240), row['candidate_id']+' '+row['status']+' Q='+q)
            line += 1
    y = 40+line*245
    draw.text((10, y), 'All four scheduled source/transfer scenes. Raw candidates shown even if rejected; actual choices are in candidates.csv.', fill='black', font=font(14))
    draw.text((10, y+24), 'Missing transfer reference stays blank until evaluation; historical images do not replace fresh H_start.', fill='black', font=font(14))
    for index, row in enumerate(candidates):
        changes = '; '.join(c['file']+' +'+str(c['added_lines'])+'/-'+str(c['removed_lines']) for c in row['changed_files'])
        draw.text((10, y+55+index*45), row['task_id']+' '+LABELS[row['method']]+': '+(changes or 'No saved H diff yet'), fill='black', font=font(14))
        draw.text((10, y+74+index*45), 'Raw source deltaQ='+str(row['source_delta_Q'])+'; independent-scene deltaQ='+str(row['raw_candidate_transfer_delta_Q']), fill='#44505d', font=font(12))
    canvas.save(ROOT/'figures/figure4_fresh_reconstructions.png')


def diagnosis_figure(manifest, candidates, observations):
    canvas = Image.new('RGB', (1280, 300*len(candidates)), 'white')
    draw = ImageDraw.Draw(canvas)
    for index, row in enumerate(candidates):
        task, method = row['task_id'], row['method']
        dest = ROOT/'tasks'/task/method
        ys = index*300
        ev = ROOT/'tasks'/task/'evidence'
        tile(canvas, ev/'reference.png', (0, ys, 256, 240), task+' photograph')
        tile(canvas, ev/'final.png', (256, ys, 256, 240), 'Historical diagnosis P')
        probes = [p for p in observations if p['task_id'] == task and p['method'] == method]
        for offset in range(2):
            probe = probes[offset] if offset < len(probes) else None
            path = ROOT/probe['image'] if probe else ROOT/'__no_requested_probe__'
            caption = (probe['tool']+' @ '+probe['object_id']+' outcome='+str(probe['balanced_outcome'])) if probe else 'No probe requested; no invented image'
            tile(canvas, path, (512+offset*256, ys, 256, 240), caption)
        text = LABELS[method]+' '+task+' | module='+str(row['selected_module'])+' | calibration='+str(row['forecast_calibration'])
        draw.text((8, ys+244), text[:155], font=font(13), fill='black')
        draw.text((8, ys+267), 'Executed probes '+str(row['probes_completed'])+'; M changed decision '+str(row['decision_changed'])+'; no fault-module truth.', font=font(13), fill='black')
        stage1 = optional(dest/'stage1.json')
        if stage1:
            lines = ['Pre-probe predictions:']
            for h in stage1['context']['hypotheses']:
                for tool in stage1['plan']['probes']:
                    p = h['predictions'][tool['probe']]
                    lines.append(h['module']+' '+tool['probe']+' ['+format(p['lower'], '.3f')+','+format(p['upper'], '.3f')+']')
            for j, line in enumerate(lines[:9]):
                for k, part in enumerate(textwrap.wrap(line, 28)[:2]):
                    draw.text((1033, ys+10+j*25+k*12), part, font=font(10), fill='#1c4651')
    canvas.save(ROOT/'figures/figure3_actual_diagnostics.png')


def structural_figure(rows):
    physical = optional(ROOT/'tests/physical_probe_calibration.json')
    canvas = Image.new('RGB', (1350, 745 if physical else 455), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 12), 'Eight saved deterministic checks: expected behavior vs measured result', font=font(19), fill='black')
    for index, row in enumerate(rows):
        y = 58+index*42
        draw.text((12, y), row['case'], font=font(15), fill='black')
        draw.text((370, y), 'expected '+str(row['expected_measured_pass'])+'; measured '+str(row['actual_measured_pass']), font=font(15), fill='black')
        draw.text((730, y), 'detected' if row['expected_behavior_detected'] else 'mismatch', font=font(15), fill='#236d45' if row['expected_behavior_detected'] else '#b23c30')
    tile(canvas, ROOT/'tests/target_probe/probe_object_scale.png', (915, 55, 425, 300), 'Real specified-target probe; not eight rendered fixtures')
    draw.text((12, 410), 'False on a deliberately broken case means detection. JSON facts; mechanical checks, not text editing or natural 3D truth.', font=font(13), fill='black')
    if physical:
        draw.text((12, 452), 'Additional physical probe calibration: actual 64x64 / 1 sample images, excluded from formal comparisons', font=font(16), fill='black')
        for index, (name, measured) in enumerate(physical['checks'].items()):
            path = ROOT/'tests'/name/('probe_'+name+'.png')
            tile(canvas, path, (index*450, 485, 440, 240), name+' '+measured['status']+'; original scene preserved '+str(measured['original_scene_not_modified']))
    canvas.save(ROOT/'figures/figure6_structural_calibration.png')


def mechanical_edit_contact(scenes):
    """Both preselected transfer rooms and all methods, irrespective of quality."""
    chosen = [r for r in scenes if r['scope'] == 'formal' and r['role'] == 'transfer']
    selection = [{'task_id': task_id, 'scene_id': next(r['scene_id'] for r in chosen if r['task_id'] == task_id),
                  'methods': ['reference', *METHODS], 'split': 'test',
                  'rule': 'Both preselected transfer cases, task01 kitchen and task02 portable classroom; all four methods; never selected by score.'}
                 for task_id in ['task01', 'task02']]
    rows = []
    for row in chosen:
        folder = ROOT/row['folder']/'functional'
        raw = optional(folder/'mechanical.json')
        summary = optional(folder/'summary.json')
        material = raw['material'] if raw else None
        move = raw['move'] if raw else None
        material_available = material is not None and material['applicable'] is True
        move_available = move is not None and move['applicable'] is True
        rows.append({'task_id': row['task_id'], 'scene_id': row['scene_id'], 'method': row['method'],
            'split': row['split'], 'evaluation_status': row['status'],
            'mechanical_status': 'completed' if raw else 'not_started' if row['status'] == 'not_started' else 'missing',
            'edit_type': raw['test_type'] if raw else None,
            'meaning': 'Predefined mechanical Blender operations; no text instruction editor and no semantic edit success claim.',
            'target_selection': raw['target_selection'] if raw else None,
            'original_blend_unchanged_reported': raw['original_blend_unchanged'] if raw else None,
            'material_applicable': material['applicable'] if material else None,
            'material_pass': material['pass'] if material else None,
            'material_target_success': material['target_success'] if material_available else None,
            'material_target_geometry_unchanged': material['target_geometry_unchanged'] if material_available else None,
            'material_non_target_preservation': material['non_target_preservation'] if material_available else None,
            'move_applicable': move['applicable'] if move else None,
            'move_pass': move['pass'] if move else None,
            'move_target_success': move['target_success'] if move_available else None,
            'part_relations_preserved': move['part_relations_preserved'] if move_available else None,
            'relation_max_abs_matrix_delta': move['relation_max_abs_matrix_delta'] if move_available else None,
            'relation_tolerance': raw['relation_tolerance'] if raw else None,
            'move_non_target_preservation': move['non_target_preservation'] if move_available else None,
            'move_displacement_normalized': move['displacement_normalized'] if move_available else None,
            'functional_summary': summary,
            'before_image': relative(folder/'before.png'),
            'after_material_image': relative(folder/'after_material.png'),
            'after_move_image': relative(folder/'after_move.png'),
            'mechanical_source': relative(folder/'mechanical.json'),
            'functional_summary_source': relative(folder/'summary.json')})
    table('edit_case_selection', selection)
    table('actual_mechanical_preservation', rows)
    canvas = Image.new('RGB', (1380, 65+260*len(rows)), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), 'Actual mechanical edits: both preselected transfer rooms, all methods; NOT text instruction editing', font=font(18), fill='black')
    for index, row in enumerate(rows):
        y = 55+index*260
        tile(canvas, ROOT/row['before_image'], (0, y, 320, 250), row['task_id']+' '+LABELS[row['method']]+' before')
        tile(canvas, ROOT/row['after_material_image'], (320, y, 320, 250), 'Mechanical local blue material',
             missing_label='Not applicable' if row['material_applicable'] is False else 'No output / pending')
        tile(canvas, ROOT/row['after_move_image'], (640, y, 320, 250), 'Mechanical group translation',
             missing_label='Not applicable' if row['move_applicable'] is False else 'No output / pending')
        material_keep = row['material_non_target_preservation']
        move_keep = row['move_non_target_preservation']
        lines = [row['scene_id']+' '+row['evaluation_status'],
                 'Target: '+str(row['target_selection']['object'] if row['target_selection'] else None),
                 'Material target success: '+str(row['material_target_success']),
                 'Non-target material keep: '+str(material_keep['pass'] if material_keep else None),
                 'Geometry keep: '+str(row['material_target_geometry_unchanged']),
                 'Move applicable / pass: '+str(row['move_applicable'])+' / '+str(row['move_pass']),
                 'Part relation max error: '+str(row['relation_max_abs_matrix_delta']),
                 'Move non-target keep: '+str(move_keep['pass'] if move_keep else None)]
        line_y = y+8
        for line in lines:
            for part in textwrap.wrap(line, 48):
                draw.text((975, line_y), part, font=font(12), fill='black')
                line_y += 18
    canvas.save(ROOT/'figures/figure6_real_edit_preservation.png')


def quantitative_figure(scenes, candidates, costs, calls):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    ax = axes[0, 0]
    for index, method in enumerate(['reference', *METHODS]):
        rows = [r for r in scenes if r['scope'] == 'formal' and r['method'] == method and r['Q'] is not None]
        for k, row in enumerate(rows):
            ax.scatter(index+(k-1.5)*.045, row['Q'], color=COLORS[method], marker='o' if row['role'] == 'source' else '^')
    ax.set_xticks(range(4), ['H_start', 'Fixed', 'Structured', 'Active'])
    ax.set(title='All measured raw Q (circle: source; triangle: transfer)', ylabel='Measured Q')
    if not any(r['Q'] is not None for r in scenes if r['scope'] == 'formal'):
        ax.text(.5, .5, 'Pending fresh evaluation', transform=ax.transAxes, ha='center')
    ax = axes[0, 1]
    for row in candidates:
        if row['source_delta_Q'] is not None and row['raw_candidate_transfer_delta_Q'] is not None:
            ax.scatter(row['source_delta_Q'], row['raw_candidate_transfer_delta_Q'], color=COLORS[row['method']])
            ax.annotate(row['method'][0].upper()+row['task_id'][-2:], (row['source_delta_Q'], row['raw_candidate_transfer_delta_Q']), fontsize=9)
    ax.axvline(.01, color='#777777', linestyle='--');ax.axhline(-.01, color='#777777', linestyle='--')
    ax.set(title='Six paired candidate points when measurable', xlabel='Source delta Q vs fresh H_start', ylabel='Raw candidate transfer delta Q')
    if not any(c['source_delta_Q'] is not None and c['raw_candidate_transfer_delta_Q'] is not None for c in candidates):
        ax.text(.5, .5, 'Pending valid pairs', transform=ax.transAxes, ha='center')
    ax = axes[1, 0]
    for i, method in enumerate(METHODS):
        arms = [c for c in candidates if c['method'] == method]
        n = sum(c['effective_shared_repair'] is True for c in arms)
        measured = sum(c['effective_shared_repair'] is not None for c in arms)
        if measured:
            ax.bar(i, n/len(arms), color=COLORS[method])
        ax.text(i, n/len(arms)+.04 if measured else .05, str(n)+'/'+str(len(arms))+'; assessed '+str(measured) if measured else 'pending', ha='center', fontsize=9)
    ax.set_xticks(range(3), ['Fixed', 'Structured', 'Active']);ax.set_ylim(0, 1.2)
    ax.set(title='Strict effective shared repair / all scheduled', ylabel='Fraction (function gates also required)')
    ax = axes[1, 1]
    for method in METHODS:
        cost, benefit = 0, 0
        x, y = [], []
        for row in [c for c in candidates if c['method'] == method]:
            task_calls = [c for c in calls if c['method'] == method and c['task_id'] == row['task_id']]
            cost += sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in task_calls)
            if row['effective_shared_repair'] is not None:
                benefit += int(row['effective_shared_repair'])
                x.append(cost);y.append(benefit)
        if x:
            ax.plot(x, y, 'o-', label=LABELS[method], color=COLORS[method])
    if not ax.lines:
        ax.text(.5, .5, 'Pending terminal paired results\nCosts are already recorded in costs.csv', transform=ax.transAxes, ha='center')
    else:
        ax.legend()
    ax.set(title='Cumulative known-token cost / strict repairs', xlabel='Known own tokens (common H_start cost separate)', ylabel='Strict repairs')
    fig.tight_layout();fig.savefig(ROOT/'figures/figure5_results_cost.png', dpi=150);plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for i, method in enumerate(['reference', *METHODS]):
        rows = [r for r in scenes if r['scope'] == 'formal' and r['method'] == method]
        measured = sum(r['schedule_terminal'] for r in rows)
        if measured:
            axes[0].bar(i-.15, sum(r['execution_success'] is True for r in rows)/len(rows), width=.28, color='#9ba4ad')
            axes[0].bar(i+.15, sum(r['functional_eligible'] is True for r in rows)/len(rows), width=.28, color=COLORS[method])
        axes[0].text(i, 1.02, 'terminal '+str(measured)+'/'+str(len(rows)), ha='center', fontsize=8)
    axes[0].set_xticks(range(4), ['H_start', 'Fixed', 'Structured', 'Active'])
    axes[0].set(ylim=(0, 1.18), title='Execution (gray) / absolute functional compliance', ylabel='All-scheduled fraction; pending remains unmeasured')
    groups = [*METHODS, 'common_H_start', 'smoke', 'preparation']
    by_group = {c['cost_group']: c for c in costs}
    axes[1].bar(range(len(groups)), [by_group[g]['CLI_sessions'] for g in groups], color=[COLORS.get(g, '#999999') for g in groups])
    axes[1].set_xticks(range(len(groups)), ['Fixed', 'Structured', 'Active', 'H_start', 'Smoke', 'Prep'], rotation=20)
    axes[1].set(title='All actual CLI sessions; H_start cost separate', ylabel='Sessions (all roles, failures included)')
    fig.tight_layout();fig.savefig(ROOT/'figures/figure5_functional_cost_counts.png', dpi=150);plt.close(fig)


def report(summary, scenes, candidates, costs, observations, structural):
    total = summary['cost']
    fmt = lambda value: 'pending / null' if value is None else format(value, '.4f') if isinstance(value, float) else str(value)
    text = ['# Scene-RSI V2.4 中文实验报告', '',
        '本轮研究自然图像重建共享流程 H 的有限诊断与修改。共同起点 H_start 是 V2.1 r1/C2；原始 H0 仅保留源码，并未冒称本轮实际对照起点。M 由工程修订，未自动进化。', '',
        '## 实际状态', '',
        '正式计划为 2 个研发任务 × 3 种诊断方法 × 1 个共享 H 提案，共 6 个候选；4 个真实源/迁移场景配置中计划 16 个新重建任务。烟测单列。代码将源图 split 命名为 Selection，但这张图已用于 H 的诊断与编码：这是同图研发/筛选，不是独立验证。另一房间的 transfer 在候选与选择冻结后执行，但图像曾在 V2.2 暴露；本轮探索性，不称新盲测。', '',
        '|方法|新执行成功 / 预定|功能合规 / 预定|条件 Q（n）|严格有效修复 / 预定候选|实际选中 C1|',
        '|---|---|---|---|---|---|']
    for method in ['reference', *METHODS]:
        s = summary['methods'][method];e, f, q = s['execution'], s['functional'], s['effective_shared_repair']
        text.append('|'+LABELS[method]+'|'+str(e['passed'])+'/'+str(e['scheduled'])+'; pending '+str(e['pending_or_missing'])+'|'+str(f['passed'])+'/'+str(f['scheduled'])+'|'+fmt(s['conditional_Q_mean'])+' ('+str(s['conditional_Q_n'])+')|'+(str(q['passed'])+'/'+str(q['scheduled'])+'; pending '+str(q['pending_or_missing']) if q['scheduled'] else 'N/A')+'|'+str(s['actual_selected_C1'])+'|')
    text += ['', '## 六个候选的全部点', '',
        '|任务 / 方法|提案状态|源 ΔQ|原始候选迁移 ΔQ|实际 Selection 选择|选后迁移 ΔQ|严格有效修复|',
        '|---|---|---|---|---|---|---|']
    for c in candidates:
        text.append('|'+c['task_id']+' / '+LABELS[c['method']]+'|'+c['status']+'|'+fmt(c['source_delta_Q'])+'|'+fmt(c['raw_candidate_transfer_delta_Q'])+'|'+str(c['actual_selection'] or 'pending')+'|'+fmt(c['selected_transfer_delta_Q'])+'|'+fmt(c['effective_shared_repair'])+'|')
    text += ['', '严格有效修复：源场景必要功能全部通过，源 Q 相对本轮新 H_start 提升 >0.01；迁移执行/必要功能通过，Q 不下降超过 0.01。更强的迁移提升 >0.01 另存字段。缺少原始 Q 不证明收益。实际选择与此严格收益派生值分开保留，不改写冻结选择。',
        '如实执行规则与冻结文字存在偏离：runner 在 H_start 的绝对功能资格不通过时，接受任意合格候选；即使 H_start 有有效 Q，也不要求候选再提高 >0.01。这里的不合格可能来自功能失败，并不等于没有图像/Q。保留实际 selection_freeze 选择，不事后重新选择；严格视觉增益另作派生分析，selection_strict_gain_disagreement 逐点标记不一致。缺少基线 Q 时不能量出增益，也不把 Q 填零；source_execution_recovery / transfer_execution_recovery 单列执行恢复。执行退化观测不自动等于算法退化，服务错误需结合原始日志解释。', '',
        '## 真实诊断闭环与结构检查', '',
        '|方法|请求 / 完成 / 可测探测|M 第二阶段执行|预测校准状态|unresolved|', '|---|---|---|---|---|']
    for method in METHODS:
        s = summary['methods'][method]
        text.append('|'+LABELS[method]+'|'+str(s['probes_requested'])+' / '+str(s['probes_completed'])+' / '+str(s['probes_measured'])+'|'+str(s['M_stage2_executed'])+'|'+json.dumps(s['forecast_calibration_counts'], ensure_ascii=False)+'|'+str(s['unresolved'])+'|')
    text += ['', '预测表保存所有竞争假设、所有可用探测的事前区间，包括未选择的工具。正式标量为 0.5 × 全图 ΔSSIM + 0.5 × 固定参考 ROI 的 ΔSSIM；三个原始量分别保留，实际标量返回可执行 M.plan_patch。事前区间是模型给出的主观预测，不是统计置信区间。M 的 soft compatibility 以区间中心/半宽加 0.003 计算残差，至少一个假设的平均归一化残差 <=3 才算兼容，并非观测严格落在区间内。exp(-0.5*min(z²,25)) 的权重比是启发式证据分数，不是贝叶斯后验概率；保留程序原字段及 unresolved。自然图像没有故障对象/模块真值，因此定位/模块准确率为 null，不能用文本丰富或 SSIM 上升代替因果定位。',
        'Fixed/Active 同为最多两个探测；实际次数可能不同，不宣称严格实际计算量匹配。各组独立诊断调用及编码调用全部计成本。',
        '准备期保留了无效对象 ID、早期菜单无法形成可区分预测等尝试，列于 preparation_smoke.csv；不得把这些尝试隐藏或并入独立正式样本。最终 refined 烟测与先前尝试分别保存。',
        '八个确定性结构检查：'+str(sum(r['expected_behavior_detected'] for r in structural))+'/'+str(len(structural))+' 个与已知预期相符。图 6 显示保存的真实 JSON 测量与一张实际指定对象探测图，不为其他夹具补造渲染。机械材质/移动测试不代表文字指令编辑；支撑 AABB 近似与三角面交叉也不是自然场景三维真值。', '',
        '## 实际新增成本', '',
        'CLI 会话 '+str(total['CLI_sessions'])+'；已知输入 '+str(total['known_input_tokens'])+'，输出 '+str(total['known_output_tokens'])+' token；usage 缺失 '+str(total['usage_unknown_sessions'])+'。渲染尝试上界 '+str(total['render_attempts_upper_bound'])+'，完成 '+str(total['renders_completed'])+'。CPU 两线程、单重任务，GPU 0。', '',
        '|成本组|CLI|已知输入 / 输出|usage 缺失|探测 Blender 秒|重建流水线秒|', '|---|---|---|---|---|---|']
    for c in costs:
        text.append('|'+c['cost_group']+'|'+str(c['CLI_sessions'])+'|'+str(c['known_input_tokens'])+' / '+str(c['known_output_tokens'])+'|'+str(c['usage_unknown_sessions'])+'|'+fmt(c['probe_Blender_seconds'])+'|'+fmt(c['reconstruction_pipeline_seconds'])+'|')
    text += ['', '诊断/共享 H 编码的 gpt-6-astra 单次 CLI 上限为 600 秒；重建 student gpt-6.1-sol 单次上限为 300 秒，且受内层总计 600 秒的剩余时间限制。Blender 同样只能使用该内层剩余时间。不是各阶段各获 600 秒。H_start 的共同评估成本单列；烟测/准备费用不摊入某一正式方法。模型 wall time、重建流水线及内层 Blender 是重叠分量，不能相加；共享服务器耗时与未知队列不支持算法速度优势结论。费用美元未知，模型请求名称与真实返回字段分别保留。历史 V2.1/V2.2 复制日志不计入本轮新增调用。', '',
        '## 真实图与审查入口', '',
        '![历史失败审计](../figures/figure1_failure_audit.png)',
        '![自然图像与历史诊断输入](../figures/figure2_natural_diagnosis_inputs.png)',
        '![真实探测与决策](../figures/figure3_actual_diagnostics.png)',
        '![本轮新重建全部联系表](../figures/figure4_fresh_reconstructions.png)',
        '![全部数值点与成本](../figures/figure5_results_cost.png)',
        '![功能合规与实际会话](../figures/figure5_functional_cost_counts.png)',
        '![已知结构错误检测](../figures/figure6_structural_calibration.png)', '',
        '![真实机械局部编辑与非目标保持](../figures/figure6_real_edit_preservation.png)', '',
        '真实编辑联系表预先覆盖 task01 厨房、task02 便携教室这两个迁移场景的 H_start / Fixed / Structured / Active；没有按分数挑选。before、材质编辑、组合移动图全部读取本轮 functional 原始产物。缺测留空，不适用单列；材料、非目标保持、组合关系与功能门槛的原始值见 [actual_mechanical_preservation.csv](../metrics/actual_mechanical_preservation.csv)。这只是预定义机械操作，不是文字指令编辑。', '',
        '原始逐场景 [scene_metrics.csv](../metrics/scene_metrics.csv)，六候选 [candidates.csv](../metrics/candidates.csv)，事前预测 [forecasts.csv](../metrics/forecasts.csv)，真实观测 [probe_observations.json](../metrics/probe_observations.json)，调用 [calls.csv](../metrics/calls.csv)，成本 [costs.csv](../metrics/costs.csv)，图表来源 [figure_sources.json](../metrics/figure_sources.json)。',
        '所有图按固定 task01、task02 / fixed、structured、active 顺序展示，未挑赢家。图 2 的旧 V2.2 输出仅为诊断输入；图 4 用本轮新 H_start，与其余方法渲染条件一致。失败无输出留空，pending 不当零质量。', '',
        '## 科研结论边界', '',
        '- 当前是否有共享流程收益，以六个真实候选与选后迁移数据为准；pending 不产生结论。负差异、拒绝候选和服务失败完整保留。',
        '- 两个研发任务不是两次独立 RSI 演化；多个渲染视角不是额外场景。本轮没有自动 M 后代、陌生 H 起点冻结元回放或通用 RSI 基线重跑。',
        '- 新修复只属于共享 H 的 policy/system；场景 P 的变化来自这些流程的新执行。源码 diff 与编码者的观测使用说明是轨迹，不自动证明诊断因果收益。',
        '- 源图已参与本轮诊断和编码，随后同图研发/筛选不能证明跨图像验证收益；另一房间 transfer 在候选/选择冻结后新执行，但历史图像已暴露。冻结顺序与实际选择另存，不得把这些公开图像称新盲测。',
        '- 保留历史 failure_type 与审计后的预算/阶段解释；不回写历史分数。原始视觉缺测为 null，端到端失败效用单独赋零。', '',
        '## 离线重画', '', '`python analyze.py` 只读本目录已有输入并更新派生 metrics/figures/reports，不调用模型、Blender 或 GPU。若要保留本次派生报告，请使用归档提供的离线新目录入口。']
    if (ROOT/'metrics/implementation_audit.json').exists():
        text += ['', '执行实现与逐臂探测/渲染复核：[implementation_audit.json](../metrics/implementation_audit.json)。这是事后工程审计，不修改实际 M/H 或冻结选择。']
    body = '\n'.join(text)+'\n'
    (ROOT/'reports/REPORT_ZH.md').write_text(body)
    images = ['figure1_failure_audit.png', 'figure2_natural_diagnosis_inputs.png', 'figure3_actual_diagnostics.png',
              'figure4_fresh_reconstructions.png', 'figure5_results_cost.png', 'figure5_functional_cost_counts.png', 'figure6_structural_calibration.png', 'figure6_real_edit_preservation.png']
    links = ' · '.join('<a href="../metrics/'+n+'.csv">'+n+'</a>' for n in ['scene_metrics', 'candidates', 'forecasts', 'calls', 'costs'])
    picture_html = ''.join('<h2>'+html.escape(name)+'</h2><img src="../figures/'+name+'">' for name in images if (ROOT/'figures'/name).exists())
    evidence_links = '<h2>逐候选可检查证据</h2><ul>'
    for c in candidates:
        paths = [c['stage1_path'], c['stage2_path'], c['candidate_path']]
        paths += [v['diff_path'] for v in c['changed_files']]
        available = [p for p in paths if (ROOT/p).exists()]
        evidence_links += '<li>'+html.escape(c['task_id']+' '+LABELS[c['method']])+'：'+(' · '.join('<a href="../'+html.escape(p, quote=True)+'">'+html.escape(Path(p).name)+'</a>' for p in available) or 'pending / 无产物')+'</li>'
    if (ROOT/'metrics/implementation_audit.json').exists():
        evidence_links += '<li><a href="../metrics/implementation_audit.json">事后执行实现审计（未改变原实验）</a></li>'
    evidence_links += '</ul><h2>实际场景工程</h2><p>大文件在完整 Release 中；解压后以下本地链接可用。</p><ul>'
    for row in scenes:
        blend = ROOT/row['folder']/'scene.blend'
        if blend.exists():
            evidence_links += '<li><a href="../'+html.escape(relative(blend), quote=True)+'">'+html.escape(row['task_id']+' '+row['method']+' '+row['role']+' .blend')+'</a></li>'
    evidence_links += '</ul>'
    (ROOT/'reports/index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>Scene-RSI V2.4</title><style>body{font:16px sans-serif;max-width:1400px;margin:30px auto;padding:15px}img{max-width:100%}pre{white-space:pre-wrap}a{color:#176577}</style><h1>Scene-RSI V2.4 真实实验</h1><p><a href="REPORT_ZH.md">中文报告</a> · '+links+'</p>'+picture_html+evidence_links+'<pre>'+html.escape(body)+'</pre></html>')


def main():
    for name in ['metrics', 'figures', 'reports']:
        (ROOT/name).mkdir(exist_ok=True)
    manifest = read(ROOT/'manifest.json')
    refined = ROOT/'tasks/smoke_refined/task.json'
    if refined.exists() and not any(t['task_id'] == 'smoke_refined' for t in manifest):
        manifest.append(read(refined))
    final_status = optional(ROOT/'FINAL_STATUS.json')
    final = final_status is not None and final_status['phase'] == 'all_scheduled_terminal'
    scenes = collect_scenes(manifest, final)
    candidates, forecasts, observations = collect_candidates(manifest, scenes, final)
    calls, costs, totals = collect_costs(scenes)
    for row in candidates:
        owned = [c for c in calls if c['task_id'] == row['task_id'] and c['method'] == row['method']]
        row.update(actual_CLI_sessions=len(owned), actual_CLI_role_counts=dict(Counter(c['role'] for c in owned)),
            known_input_tokens=sum(c['input_tokens'] for c in owned if c['input_tokens'] is not None),
            known_output_tokens=sum(c['output_tokens'] for c in owned if c['output_tokens'] is not None),
            usage_unknown_sessions=sum(c['input_tokens'] is None or c['output_tokens'] is None for c in owned))
    structural = structural_rows()
    physical = optional(ROOT/'tests/physical_probe_calibration.json')
    physical_rows = [{'probe': name, 'measurement': measured, 'source': 'tests/physical_probe_calibration.json',
                      'quality': physical['quality'], 'remote_calls': physical['remote_calls']}
                     for name, measured in physical['checks'].items()] if physical else []
    summary = summarize(scenes, candidates, totals)
    summary['workflow_terminal'] = final
    summary['generated_at_UTC'] = datetime.now(timezone.utc).isoformat()
    summary['scheduled_fresh_formal_scenes'] = sum(r['scope'] == 'formal' for r in scenes)
    summary['scheduled_shared_proposals'] = len(candidates)
    for name, rows in [('scene_metrics', scenes), ('candidates', candidates), ('forecasts', forecasts),
                       ('probe_observations', observations), ('calls', calls), ('costs', costs),
                       ('structural_calibration', structural), ('physical_probe_calibration', physical_rows),
                       ('preparation_smoke', preparation_rows())]:
        table(name, rows)
    (ROOT/'metrics/summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    contacts(manifest, scenes, candidates)
    diagnosis_figure(manifest, candidates, observations)
    structural_figure(structural)
    mechanical_edit_contact(scenes)
    quantitative_figure(scenes, candidates, costs, calls)
    sources = [
        {'figure': 'figure1_failure_audit.png', 'sources': ['metrics/H_failure_audit.csv', 'audit_sources/'], 'script': 'audit.py', 'unit': 'Historical V2.1/V2.2 scheduled record; not a new V2.4 outcome'},
        {'figure': 'figure2_natural_diagnosis_inputs.png', 'sources': ['metrics/historical_diagnostic_inputs.csv', 'tasks/*/evidence/'], 'script': 'analyze.py', 'unit': 'Two historical diagnosis input scenes; fixed task order'},
        {'figure': 'figure3_actual_diagnostics.png', 'sources': ['metrics/forecasts.csv', 'metrics/probe_observations.json', 'tasks/*/*/stage1.json', 'tasks/*/*/stage2.json'], 'script': 'analyze.py', 'unit': 'All six task/method decisions; no ground-truth localization accuracy'},
        {'figure': 'figure4_fresh_reconstructions.png', 'sources': ['metrics/scene_metrics.csv', 'metrics/candidates.csv', 'tasks/*/*/*.diff', 'results/'], 'script': 'analyze.py', 'unit': 'Four scenes times fresh H_start and three raw candidate outputs; no winner selection'},
        {'figure': 'figure5_results_cost.png', 'sources': ['metrics/scene_metrics.csv', 'metrics/candidates.csv', 'metrics/calls.csv', 'metrics/costs.csv'], 'script': 'analyze.py', 'unit': 'Six paired H proposals; all scheduled denominators and actual known tokens'},
        {'figure': 'figure5_functional_cost_counts.png', 'sources': ['metrics/scene_metrics.csv', 'metrics/costs.csv'], 'script': 'analyze.py', 'unit': 'All scheduled formal scene execution/function gates; all actual new sessions including preparation'},
        {'figure': 'figure6_structural_calibration.png', 'sources': ['metrics/structural_calibration.csv', 'tests/calibration.json', 'tests/target_probe/probe_object_scale.png', 'metrics/physical_probe_calibration.json'], 'script': 'analyze.py', 'unit': 'Eight deterministic cases, existing measurement facts and real explicitly labelled smoke-quality probes'},
        {'figure': 'figure6_real_edit_preservation.png', 'sources': ['metrics/edit_case_selection.json', 'metrics/actual_mechanical_preservation.csv', 'results/*/*/*/test/*/functional/mechanical.json', 'results/*/*/*/test/*/functional/summary.json'], 'script': 'analyze.py', 'unit': 'Both preselected transfer scenes times all four methods; actual mechanical edit images and parameter measurements, not text editing'},
    ]
    table('figure_sources', sources)
    report(summary, scenes, candidates, costs, observations, structural)
    print(json.dumps({'workflow_terminal': final, 'formal_scene_rows': summary['scheduled_fresh_formal_scenes'],
                      'candidate_rows': len(candidates), 'new_calls': totals['CLI_sessions'],
                      'report': str(ROOT/'reports/index.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
