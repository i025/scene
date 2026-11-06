"""Offline implementation, forecast and render-cost audit; no models or Blender."""
import argparse
import ast
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re


METHODS = ['fixed', 'structured', 'active']
GROUPS = METHODS + ['common_H_start', 'smoke', 'calibration', 'preparation']


def read(path):
    return json.loads(path.read_text())


def optional(path):
    return read(path) if path.exists() else None


def write_table(folder, name, rows, fields=None):
    (folder/(name+'.json')).write_text(json.dumps(rows, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    columns = fields or list(dict.fromkeys(key for row in rows for key in row))
    with (folder/(name+'.csv')).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: 'null' if value is None else json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                         for key, value in row.items()} for row in rows)


def group_for(relative):
    parts = relative.parts
    if parts[0] == 'tests':
        return 'calibration'
    if parts[0] in ['tasks', 'results'] and len(parts) >= 3:
        if parts[1].startswith('smoke'):
            return 'smoke'
        if parts[1] in ['task01', 'task02']:
            return 'common_H_start' if parts[2] == 'reference' else parts[2] if parts[2] in METHODS else 'preparation'
    return 'preparation'


def frozen_sources(root):
    frozen = root/'code_snapshots/formal_frozen'
    paths = [frozen/name for name in ['experiment.py', 'meta.py', 'pilot.py', 'inspect_blend.py', 'regression.py', 'config.json']]
    paths += sorted((frozen/'backend').rglob('*.py'))
    paths += sorted((frozen/'fixed_h').rglob('*.py'))
    paths += sorted((frozen/'fixed_h').rglob('*.txt'))
    result = []
    for source in paths:
        relative = source.relative_to(frozen)
        current = root/relative
        result.append({'source': str(relative), 'frozen_path': str(source.relative_to(root)),
            'current_path': str(relative), 'frozen_exists': source.exists(), 'current_exists': current.exists(),
            'direct_text_equal': source.read_text() == current.read_text() if source.exists() and current.exists() else None,
            'comparison': 'Direct UTF-8 text equality; no fingerprint or checksum.'})
    return result


def render_costs(root, snapshot):
    costs = {group: {'cost_group': group, **snapshot,
        'reconstruction_execution_attempts': 0, 'reconstruction_render_started_measured': 0,
        'reconstruction_render_completed_measured': 0, 'reconstruction_final_pngs': 0,
        'reconstruction_start_count_unknown_executions': 0, 'inspection_render_attempts': 0,
        'inspection_renders_completed': 0, 'render_ledger_files': 0, 'probe_processes': 0,
        'reconstruction_seconds_measured': 0., 'probe_Blender_seconds_measured': 0.,
        'inspection_other_Blender_seconds_measured': 0.} for group in GROUPS}
    sources = []
    for path in sorted(root.glob('results/*/*/*/*/*/steps/*/build.py')):
        relative = path.relative_to(root)
        group = group_for(relative)
        cost = costs[group]
        step = path.parent
        telemetry = step/'stage_events.jsonl'
        events = [json.loads(line) for line in telemetry.read_text().splitlines()] if telemetry.exists() else []
        started = sum(event['stage'] == 'render_started' for event in events)
        completed = sum(event['stage'] == 'render_completed' for event in events)
        png_exists = (step/'final.png').exists()
        unknown = not telemetry.exists() and not png_exists
        cost['reconstruction_execution_attempts'] += 1
        cost['reconstruction_render_started_measured'] += started if telemetry.exists() else int(png_exists)
        cost['reconstruction_render_completed_measured'] += completed
        cost['reconstruction_final_pngs'] += int(png_exists)
        cost['reconstruction_start_count_unknown_executions'] += int(unknown)
        process = optional(step/'result.json')
        if process is not None:
            cost['reconstruction_seconds_measured'] += process['seconds']
        sources.append({'cost_group': group, 'kind': 'reconstruction_execution', 'path': str(relative),
            'stage_telemetry_exists': telemetry.exists(), 'render_started_events': started,
            'render_completed_events': completed, 'final_png_exists': png_exists,
            'start_count_unknown': unknown, 'count_note': 'An execution attempt counts in the budget upper bound even when it fails before rendering.'})
    for path in sorted(root.rglob('render_ledger.json')):
        relative = path.relative_to(root)
        if relative.parts[0] in ['audit_sources', 'code_snapshots']:
            continue
        group = group_for(relative)
        cost = costs[group]
        ledger = read(path)
        cost['inspection_render_attempts'] += ledger['render_attempts']
        cost['inspection_renders_completed'] += ledger['renders_completed']
        cost['render_ledger_files'] += 1
        process = optional(path.with_name('process.json'))
        is_probe = 'probes' in relative.parts
        if process is not None:
            if is_probe:
                cost['probe_processes'] += 1
                cost['probe_Blender_seconds_measured'] += process['seconds']
            else:
                cost['inspection_other_Blender_seconds_measured'] += process['seconds']
        sources.append({'cost_group': group, 'kind': 'inspection_render_ledger', 'path': str(relative),
            'render_attempts': ledger['render_attempts'], 'renders_completed': ledger['renders_completed'],
            'is_probe': is_probe, 'process_saved': process is not None})
    for cost in costs.values():
        cost['render_attempts_upper_bound'] = cost['reconstruction_execution_attempts']+cost['inspection_render_attempts']
        cost['render_attempts_measured_lower_bound'] = cost['reconstruction_render_started_measured']+cost['inspection_render_attempts']
        cost['actual_render_attempts'] = (cost['render_attempts_measured_lower_bound']
            if cost['reconstruction_start_count_unknown_executions'] == 0 else None)
        cost['renders_completed'] = cost['reconstruction_final_pngs']+cost['inspection_renders_completed']
        cost['completed_from_explicit_events_and_ledgers'] = cost['reconstruction_render_completed_measured']+cost['inspection_renders_completed']
        cost['interpretation'] = 'Render attempts are ledger/telemetry counts; build execution attempts are a separate conservative budget upper bound. No historical reused images counted.'
    return list(costs.values()), sources


def forecasts(root, task_ids, snapshot):
    rows, cases = [], []
    for task_id in task_ids:
        for method in METHODS:
            folder = root/'tasks'/task_id/method
            first = optional(folder/'stage1.json')
            second = optional(folder/'stage2.json')
            observations = optional(folder/'observations.json')
            measured = {item['request']['probe']: item['outcome'] for item in observations or []
                        if item['status'] == 'completed' and item['outcome'] is not None}
            if first is None:
                cases.append({'task_id': task_id, 'method': method, 'stage1_saved': False,
                    'hypothesis_count': None, 'distinct_module_count': None, 'at_least_two_distinct_modules': None,
                    'completed_measured_probes': len(measured), 'M_stage2_saved': second is not None})
                continue
            context = first['context']
            hypotheses = context['hypotheses']
            modules = sorted({item['module'] for item in hypotheses})
            residuals = {}
            for hypothesis in hypotheses:
                values = []
                for tool, outcome in measured.items():
                    interval = hypothesis['predictions'][tool]
                    center = (interval['lower']+interval['upper'])/2
                    half_width = (interval['upper']-interval['lower'])/2+.003
                    values.append(abs(outcome-center)/half_width)
                residuals[hypothesis['id']] = sum(values)/len(values) if values else None
            soft = min(residuals.values()) <= 3 if measured else None
            any_hits = {tool: any(hypothesis['predictions'][tool]['lower'] <= outcome <= hypothesis['predictions'][tool]['upper']
                                  for hypothesis in hypotheses) for tool, outcome in measured.items()}
            all_missed = not any(any_hits.values()) if measured else None
            decision = second['M_decision'] if second else None
            expected_soft_label = ('at_least_one_compatible' if soft else 'insufficient_or_no_observation')
            cases.append({'task_id': task_id, 'method': method, **snapshot, 'stage1_saved': True,
                'hypothesis_count': len(hypotheses), 'distinct_modules': modules, 'distinct_module_count': len(modules),
                'at_least_two_distinct_modules': len(modules)>=2, 'completed_measured_probes': len(measured),
                'measurements_with_any_strict_interval_hit': sum(any_hits.values()),
                'all_measured_probes_miss_all_strict_intervals': all_missed,
                'soft_case_compatible_recomputed': soft,
                'soft_compatible_despite_all_strict_intervals_missed': bool(soft and all_missed) if measured else None,
                'hypothesis_mean_residuals': residuals, 'M_stage2_saved': second is not None,
                'actual_soft_calibration_label': decision['forecast_calibration'] if decision else None,
                'soft_label_matches_recomputed': decision['forecast_calibration'] == expected_soft_label if decision else None,
                'initial_module': context['initial_module'],
                'selected_module': decision['selected_module'] if decision else None,
                'decision_changed': decision['decision_changed'] if decision else None,
                'stage1_path': str((folder/'stage1.json').relative_to(root)),
                'stage2_path': str((folder/'stage2.json').relative_to(root))})
            requested = {item['probe'] for item in first['plan']['probes']}
            for hypothesis in hypotheses:
                for tool, interval in hypothesis['predictions'].items():
                    value = measured.get(tool)
                    center = (interval['lower']+interval['upper'])/2
                    half_width = (interval['upper']-interval['lower'])/2+.003
                    residual = abs(value-center)/half_width if value is not None else None
                    rows.append({'task_id': task_id, 'method': method, **snapshot,
                        'hypothesis_id': hypothesis['id'], 'module': hypothesis['module'],
                        'object_id': hypothesis['object_id'], 'tool': tool, 'requested': tool in requested,
                        'prediction_lower': interval['lower'], 'prediction_upper': interval['upper'],
                        'actual_balanced_outcome': value,
                        'strict_interval_hit': interval['lower'] <= value <= interval['upper'] if value is not None else None,
                        'measurement_normalized_residual': residual,
                        'measurement_soft_compatible': residual <= 3 if residual is not None else None,
                        'hypothesis_mean_residual': residuals[hypothesis['id']],
                        'hypothesis_soft_compatible': residuals[hypothesis['id']] <= 3 if measured else None,
                        'case_soft_compatible': soft,
                        'actual_M_soft_label': decision['forecast_calibration'] if decision else None,
                        'saved_before_probe': first['saved_before_probe'],
                        'forecast_unit': 'One subjective hypothesis/tool interval, not an independent reconstruction or a calibrated probability.'})
    return rows, cases


def literal_review(root, task_ids):
    rows = []
    for task_id in task_ids:
        for method in METHODS:
            folder = root/'tasks'/task_id/method
            first = optional(folder/'stage1.json')
            candidate = optional(folder/'candidate.json')
            if candidate is None:
                rows.append({'task_id': task_id, 'method': method, 'candidate_saved': False,
                             'review_flags': None, 'automatic_rejection': False})
                continue
            ids = first['context']['raw_evidence']['valid_object_ids']
            ids_set = set(ids)
            patterns = [(object_id, re.compile(r'(?<!\w)'+re.escape(object_id)+r'(?!\w)'))
                        for object_id in ids if len(object_id)>=3]
            flags, changed = [], []
            for filename in ['policy.py', 'system.txt']:
                path = folder/'H'/filename
                text = path.read_text()
                changed.append({'file': filename, 'direct_text_changed_from_H_start': text != (root/'fixed_h/r1_C2'/filename).read_text()})
                if filename == 'policy.py':
                    literals = [(node.lineno, node.value) for node in ast.walk(ast.parse(text))
                                if isinstance(node, ast.Constant) and isinstance(node.value, str)]
                    for line_number, value in literals:
                        if value in ids_set:
                            flags.append({'file': filename, 'line': line_number, 'source_object_id': value,
                                          'match_kind': 'exact_python_string_literal'})
                else:
                    for line_number, line in enumerate(text.splitlines(), 1):
                        for object_id, pattern in patterns:
                            if pattern.search(line):
                                flags.append({'file': filename, 'line': line_number, 'source_object_id': object_id,
                                              'match_kind': 'whole_identifier_in_shared_prompt'})
            rows.append({'task_id': task_id, 'method': method, 'candidate_saved': True,
                'actual_candidate_type': candidate['type'], 'changed_H_files': changed,
                'any_H_text_changed': any(item['direct_text_changed_from_H_start'] for item in changed),
                'review_flags': flags, 'flag_count': len(flags), 'automatic_rejection': False,
                'interpretation': 'Literal overlap is a manual review flag, not proof of task hardcoding. Ordinary semantic words, Camera, Root, etc. may overlap legitimately.'})
    return rows


def selection_audit(root):
    frozen = optional(root/'configs/selection_freeze.json')
    rows = []
    for choice in frozen['selections'] if frozen else []:
        source_q, baseline_q = choice.get('source_Q'), choice.get('baseline_Q')
        delta = source_q-baseline_q if source_q is not None and baseline_q is not None else None
        strict = choice.get('candidate_eligible') is True and delta is not None and delta>.01
        rows.append({**choice, 'paired_source_delta_Q': delta,
            'strict_source_qualification_and_quality_gain': strict,
            'selected_without_strict_paired_Q_gain': choice['selected']=='C1' and not strict,
            'baseline_ineligible_recovery_branch': choice.get('baseline_eligible') is False and choice['selected']=='C1',
            'interpretation': 'Retain actual frozen selection. Baseline-ineligible acceptance differs from unconditional Q-gain wording; it is not automatically measured visual improvement.'})
    return {'freeze_exists': frozen is not None, 'selection_rows': rows,
            'selected_without_strict_Q_gain_count': sum(row['selected_without_strict_paired_Q_gain'] for row in rows) if frozen else None,
            'candidate_selected_count': sum(row['selected']=='C1' for row in rows) if frozen else None,
            'rule_text_discrepancy': 'freeze.json requires eligibility and Q gain>.01; executable experiment.py also accepts an eligible candidate whenever H_start is ineligible.'}


def effective_timeout(error):
    text = str(error)
    if 'TimeoutExpired' not in text:
        return None
    match = re.search(r',\s*([0-9.eE+-]+)\)\s*$', text)
    if match is None:
        match = re.search(r'timed out after ([0-9.eE+-]+) seconds', text)
    return float(match.group(1)) if match else None


def attempt_failures(root, config, snapshot):
    rows = []
    failed_cli_paths = []

    def base_row(path, phase, kind, error, seconds, cap):
        relative = path.relative_to(root)
        parts = relative.parts
        scene_folder = path.parents[2] if parts[0]=='results' and kind in ['CLI_session','Blender_execution'] else None
        record = optional(scene_folder/'record.json') if scene_folder else None
        valid = record['metrics']['valid'] if record else None
        return {**snapshot, 'evidence_path': str(relative), 'phase': phase, 'event_kind': kind,
            'task_id': parts[1] if parts[0] in ['results','tasks'] else None,
            'method': parts[2] if parts[0] in ['results','tasks'] else None,
            'cost_group': group_for(relative), 'classification': 'unknown',
            'raw_error': error, 'actual_seconds': seconds, 'configured_timeout_cap_seconds': cap,
            'effective_timeout_seconds_from_saved_exception': effective_timeout(error),
            'service_queue_seconds': None, 'count_as_distinct_attempt_failure': True,
            'same_attempt_as': [], 'related_reconstruction_folder': str(scene_folder.relative_to(root)) if scene_folder else None,
            'task_record_available': record is not None, 'task_record_valid_when_available': valid,
            'original_end_task_failure_type': record['failure_type'] if record else None,
            'recovered_inner_attempt_failure': valid if scene_folder else None,
            'interpretation': 'Attempt failure is distinct from final project validity; a later successful scene is retained as a successful task.'}

    for path in sorted(root.rglob('session.json')):
        if path.relative_to(root).parts[0] in ['audit_sources','code_snapshots','report_history'] or not path.with_name('request.json').exists():
            continue
        session = read(path)
        if session['status']!='failed':
            continue
        failed_cli_paths.append(path)
        role = session['role']
        phase = 'student_model_call' if role=='student' else 'proposal_model_call'
        cap = config['model']['timeout'] if role=='student' else config['proposer']['timeout']
        row = base_row(path, phase, 'CLI_session', session.get('error'), session.get('seconds'), cap)
        events_path = path.with_name('events.jsonl')
        events = events_path.read_text() if events_path.exists() else ''
        transport = [line for line in events.splitlines() if any(term in line.lower()
                     for term in ['connection refused','waiting for network','routing discovery failed'])]
        timeout = row['effective_timeout_seconds_from_saved_exception']
        row.update(role=role, requested_model=session['requested_model'], actual_model=session['actual_model'],
                   exit_code=session.get('exit_code'), transport_evidence_lines=transport,
                   events_path=str(events_path.relative_to(root)))
        if timeout is not None:
            row['classification'] = 'model_call_timeout'
            row['deadline_scope'] = 'scene_remainder' if role=='student' and timeout<cap-1 else 'configured_model_cap'
        elif transport:
            row['classification'] = 'model_service_error'
        else:
            row['classification'] = 'unknown'
            row['classification_limit'] = 'A failed CLI exit alone does not identify service versus local process cause.'
        rows.append(row)

    for path in sorted(root.glob('results/*/*/*/*/*/steps/*/result.json')):
        result = read(path)
        if result['ok']:
            continue
        row = base_row(path, 'Blender_execution', 'Blender_execution', result['error'], result['seconds'], config['blender']['timeout'])
        telemetry = path.with_name('stage_events.jsonl')
        events = [json.loads(line) for line in telemetry.read_text().splitlines()] if telemetry.exists() else []
        stages = [event['stage'] for event in events]
        stderr = result['stderr']
        timed_out = row['effective_timeout_seconds_from_saved_exception'] is not None
        if timed_out and 'render_started' in stages:
            category = 'render_timeout'
        elif timed_out and 'scene_build_started' in stages and 'scene_build_completed' not in stages:
            category = 'blender_build_timeout'
        elif not timed_out and 'python_validation_started' in stages and 'scene_build_started' not in stages:
            category = 'invalid_generated_program'
        elif not timed_out and 'scene_build_started' in stages and 'scene_build_completed' not in stages:
            category = 'blender_build_error'
        else:
            category = 'unknown'
        row.update(classification=category, last_observed_stage=stages[-1] if stages else None,
            stage_counts=dict(Counter(stages)), stage_telemetry_path=str(telemetry.relative_to(root)),
            stderr_path=str(path.with_name('stderr.log').relative_to(root)),
            stderr_last_line=stderr.splitlines()[-1] if stderr.splitlines() else None,
            classification_limit='No unobserved build/render or service cause is imputed.')
        rows.append(row)

    seen_preparation = {}
    for path in sorted((root/'tasks').glob('*/*/failure.json')):
        failure = read(path)
        row = base_row(path, failure['phase'], 'proposal_or_diagnosis_validation',
                       failure.get('error',failure.get('reason')), None, None)
        related = [str(p.relative_to(root)) for p in failed_cli_paths if p.is_relative_to(path.parent)]
        row.update(original_status=failure['status'], annotation=failure,
            classification='invalid_diagnosis' if failure['phase']=='diagnosis_object_contract' else 'unknown',
            same_attempt_as=related, count_as_distinct_attempt_failure=not bool(related),
            annotation_duplicate_of_failed_CLI=bool(related))
        associated = [session_path for session_path in sorted(path.parent.rglob('session.json'))
                      if session_path.with_name('request.json').exists()]
        row['associated_model_sessions'] = [{'path':str(session_path.relative_to(root)),
            'status':read(session_path)['status'], 'seconds':read(session_path).get('seconds')}
            for session_path in associated]
        row['associated_model_wall_seconds'] = sum(item['seconds'] for item in row['associated_model_sessions'] if item['seconds'] is not None)
        row['configured_timeout_cap_seconds'] = config['proposer']['timeout'] if associated else None
        row['timing_limit'] = 'Validation duration itself was not separately recorded; associated model wall time is retained separately.'
        if 'id' in failure:
            seen_preparation[failure['id']] = row
        rows.append(row)
    preparation = optional(root/'preparation_failures.json')
    for index, failure in enumerate(preparation or []):
        path = root/'preparation_failures.json'
        if failure['id'] in seen_preparation:
            seen_preparation[failure['id']]['additional_evidence_paths'] = [str(path.relative_to(root))+'#'+str(index)]
            continue
        row = base_row(path, failure['phase'], 'preparation_validation', failure.get('error',failure.get('reason')), None, None)
        row.update(classification='invalid_diagnosis' if failure['phase']=='diagnosis_object_contract' else 'unknown',
                   preparation_id=failure['id'], annotation=failure)
        rows.append(row)

    records = [(path,read(path)) for path in sorted(root.glob('results/*/*/*/*/*/record.json'))]
    statuses = [(path,read(path)) for path in sorted(root.glob('results/*/*/*/*/*/status.json'))]
    recovered_folders = {row['related_reconstruction_folder'] for row in rows if row['recovered_inner_attempt_failure'] is True}
    runtime_error_successes = [str(path.parent.relative_to(root)) for path,record in records
                               if record['metrics']['valid'] and record['runtime_status']['error'] is not None]
    distinct = [row for row in rows if row['count_as_distinct_attempt_failure']]
    summary = {**snapshot, 'attempt_failure_records': len(rows), 'distinct_attempt_failures': len(distinct),
        'scope': 'All current V2.4 reconstruction/proposal/preparation attempts, including smoke; copied historical audits excluded.',
        'distinct_attempt_failures_by_phase': dict(Counter(row['phase'] for row in distinct)),
        'distinct_attempt_failures_by_classification': dict(Counter(row['classification'] for row in distinct)),
        'failure_records_by_phase_including_annotations': dict(Counter(row['phase'] for row in rows)),
        'proposal_annotations_of_already_counted_CLI_failures': sum(not row['count_as_distinct_attempt_failure'] for row in rows),
        'tasks_successful_with_mapped_inner_attempt_failure': len(recovered_folders),
        'successful_task_folders_with_mapped_inner_attempt_failure': sorted(recovered_folders),
        'tasks_successful_with_runtime_error': len(runtime_error_successes),
        'successful_task_folders_with_runtime_error': runtime_error_successes,
        'tasks_successful_with_any_inner_error': len(recovered_folders|set(runtime_error_successes)),
        'completed_inner_status_files': len(statuses),
        'clean_inner_terminations': sum(status['error'] is None for _,status in statuses),
        'inner_terminations_with_error': sum(status['error'] is not None for _,status in statuses),
        'saved_task_records': len(records), 'valid_project_successes': sum(record['metrics']['valid'] for _,record in records),
        'clean_inner_termination_but_invalid_project': sum(record['runtime_status']['error'] is None and not record['metrics']['valid'] for _,record in records),
        'raw_runtime_errors': [{'record_path':str(path.relative_to(root)), 'valid_project':record['metrics']['valid'],
                               'raw_error':record['runtime_status']['error']} for path,record in records if record['runtime_status']['error'] is not None],
        'definition': 'Count failed CLI sessions, failed Blender executions, and unmapped validation/proposal failures. Preserve mapped wrapper annotations without double-counting the same CLI attempt. A raw runtime error is retained separately and does not create an invented failed attempt or invalidate a measured valid project.'}
    return rows, summary


def candidate_code_provenance(root, task_ids):
    rows = []
    for task_id in task_ids:
        for method in METHODS:
            folder = root/'tasks'/task_id/method
            candidate = optional(folder/'candidate.json')
            response = folder/'coding/response.txt'
            reply = json.loads(response.read_text()) if candidate and response.exists() else None
            files = []
            for key,filename in [('policy','policy.py'),('system','system.txt')]:
                path = folder/'H'/filename
                diff = folder/(filename+'.diff')
                files.append({'file':filename, 'candidate_file_exists':path.exists(),
                    'decoded_coding_response_field_exists':reply is not None and key in reply,
                    'direct_text_equals_decoded_coding_response':path.read_text()==reply[key] if path.exists() and reply is not None else None,
                    'diff_path':str(diff.relative_to(root)), 'diff_exists':diff.exists()})
            records = []
            for path in sorted((root/'results'/task_id/method).glob('*/*/*/record.json')):
                record = read(path)
                records.append({'record_path':str(path.relative_to(root)), 'recorded_H_version':record['H_version'],
                    'expected_candidate_H_version':candidate['H_version'] if candidate else None,
                    'version_matches_candidate':record['H_version']==candidate['H_version'] if candidate else None})
            rows.append({'task_id':task_id,'method':method,'candidate_saved':candidate is not None,
                'coding_response_path':str(response.relative_to(root)), 'coding_response_exists':response.exists(),
                'files':files, 'current_H_matches_both_model_response_fields':
                    all(item['direct_text_equals_decoded_coding_response'] is True for item in files) if candidate else None,
                'evaluation_records':records,
                'interpretation':'Post-hoc direct decoded-string equality documents current H versus the saved model reply; this is not tamper-proof historical authorship or a claim of blind testing.'})
    return rows


def main(root):
    freeze = read(root/'configs/freeze.json')
    config = read(root/'config.json')
    final = optional(root/'FINAL_STATUS.json')
    sessions = [read(path) for path in root.rglob('session.json')
                if path.relative_to(root).parts[0] not in ['audit_sources','code_snapshots'] and path.with_name('request.json').exists()]
    running = sum(session['status']=='running' for session in sessions)
    snapshot = {'snapshot_UTC': datetime.now(timezone.utc).isoformat(),
                'snapshot_status': 'terminal_workflow_snapshot' if final and running==0 else 'partial',
                'final_marker_present': final is not None}
    sources = frozen_sources(root)
    costs, cost_sources = render_costs(root, snapshot)
    forecast_rows, cases = forecasts(root, freeze['formal_tasks'], snapshot)
    selections = selection_audit(root)
    all_frozen = optional(root/'configs/all_candidates_frozen.json')
    selected = optional(root/'configs/selection_freeze.json')
    test_starts = [read(path)['started'] for path in root.glob('results/task*/*/*/test/*/student_calls/*/session.json')]
    source_starts = [read(path)['started'] for path in root.glob('results/task*/*/*/selection/*/student_calls/*/session.json')]
    failures, failure_summary = attempt_failures(root, config, snapshot)
    code_provenance = candidate_code_provenance(root, freeze['formal_tasks'])
    result = {**snapshot, 'audit_kind': 'Offline engineering implementation/evidence audit, not a new model experiment.',
        'new_model_calls': 0, 'new_Blender_jobs': 0, 'formal_protocol_or_selection_modified': False,
        'formal_scheduled_evaluations': 16, 'formal_scheduled_proposals': len(freeze['formal_tasks'])*len(METHODS),
        'formal_saved_records': len(list(root.glob('results/task*/*/*/*/*/record.json'))),
        'actual_new_session_status_counts': dict(Counter(session['status'] for session in sessions)),
        'source_frozen_comparisons': sources,
        'all_available_frozen_source_text_equal': all(item['direct_text_equal'] is True for item in sources),
        'missing_frozen_or_live_files': [item['source'] for item in sources if not item['frozen_exists'] or not item['current_exists']],
        'stage1_distinct_module_cases': cases,
        'completed_stage1_cases': sum(case['stage1_saved'] for case in cases),
        'stage1_cases_with_two_or_more_modules': sum(case['at_least_two_distinct_modules'] is True for case in cases),
        'forecast_audit_measurement_definition': '.5*global_delta_SSIM+.5*fixed_reference_ROI_delta_SSIM.',
        'forecast_interpretation': 'Strict interval membership and soft compatibility (mean normalized residual<=3) are separate. Neither establishes calibrated hypothesis probabilities or causal truth.',
        'candidate_source_object_literal_review': literal_review(root, freeze['formal_tasks']),
        'candidate_code_response_provenance': code_provenance,
        'all_generated_current_H_equal_saved_coding_replies': (all(row['current_H_matches_both_model_response_fields'] is True
            for row in code_provenance if row['candidate_saved']) if any(row['candidate_saved'] for row in code_provenance) else None),
        'generated_H_vs_model_reply_checked': sum(row['candidate_saved'] for row in code_provenance),
        'current_attempt_failures_summary': failure_summary,
        'selection_audit': selections,
        'source_Selection_same_image': True,
        'source_Selection_interpretation': 'The source scene photograph/P supports diagnosis and coding, then a new reconstruction on that same source scene is called Selection. This is same-image development/selection; transfer is a different historically exposed scene, not a new blind test.',
        'H_start': freeze['H_start'], 'H_start_origin': 'V2.1 evolved r1/C2, disclosed; original H0 is historical source only.',
        'M_automatic_descendants': 0,
        'student_CLI_timeout_seconds': config['model']['timeout'],
        'diagnosis_and_coder_CLI_timeout_seconds': config['proposer']['timeout'],
        'scene_total_seconds': config['budget']['seconds'],
        'proposal_freeze_before_selection': all_frozen['time']<=selected['time'] if all_frozen and selected else None,
        'first_fresh_source_CLI_started': min(source_starts) if source_starts else None,
        'all_candidates_frozen_before_every_fresh_source_CLI': all(start>=all_frozen['time'] for start in source_starts) if source_starts and all_frozen else None,
        'first_fresh_test_CLI_started': min(test_starts) if test_starts else None,
        'test_started_after_selection_freeze': min(test_starts)>=selected['time'] if test_starts and selected else None,
        'every_fresh_test_CLI_started_after_selection_freeze': all(start>=selected['time'] for start in test_starts) if test_starts and selected else None,
        'render_cost_sources': cost_sources,
        'render_attempts_upper_bound_total': sum(row['render_attempts_upper_bound'] for row in costs),
        'actual_render_attempts_total': sum(row['actual_render_attempts'] for row in costs) if all(row['actual_render_attempts'] is not None for row in costs) else None,
        'renders_completed_total': sum(row['renders_completed'] for row in costs),
        'historical_cost_exclusion': 'audit_sources and code_snapshots excluded; copied historical .blend/reference/final images are not new render executions.',
        'limits': ['This snapshot can be partial while the formal process runs.',
                   'A final marker does not by itself prove every scheduled evaluation was executed; saved-record counts are separate.',
                   'Source-ID literal overlap flags require manual interpretation and do not reject candidates or change scores.',
                   'Render budget upper bounds count build attempts; actual render starts use stage events and inspection ledgers. Missing start evidence yields null rather than an invented count.']}
    metrics = root/'metrics';metrics.mkdir(exist_ok=True)
    write_table(metrics, 'cost_render_by_group', costs)
    write_table(metrics, 'forecasting_audit', forecast_rows,
                fields=list(forecast_rows[0]) if forecast_rows else ['task_id','method','hypothesis_id','tool','actual_balanced_outcome','strict_interval_hit'])
    write_table(metrics, 'current_attempt_failures', failures,
                fields=None if failures else ['evidence_path','phase','classification','raw_error','task_record_valid_when_available'])
    (metrics/'implementation_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps({key: result[key] for key in ['snapshot_status','formal_saved_records','completed_stage1_cases',
        'stage1_cases_with_two_or_more_modules','all_available_frozen_source_text_equal','render_attempts_upper_bound_total',
        'actual_render_attempts_total','renders_completed_total']}, ensure_ascii=False, indent=2))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    main(parser.parse_args().root)
