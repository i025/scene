"""Offline V3 tables and figures from saved records; never executes a model or Blender."""
import argparse
from collections import Counter
import csv
import html
import json
from pathlib import Path
import statistics
import os
import re

os.environ['MPLCONFIGDIR'] = '/tmp/scene_rsi_v3_matplotlib'
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
DIMENSIONS = ['scene_fidelity', 'physics', 'style_color', 'realism',
              'layout_spatial', 'proportion_scale', 'lighting_material', 'completeness']
TERMINAL = {'completed', 'failed', 'timeout', 'invalid', 'selected', 'rejected', 'unchanged'}


def read(path):
    return json.loads(path.read_text())


def encode(value):
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else 'null' if value is None else value


def save_csv(name, rows, fields):
    path = ROOT / 'metrics' / name
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: encode(row.get(key)) for key in fields})
    return path


def mean(values):
    values = [value for value in values if isinstance(value, (int, float))]
    return statistics.mean(values) if values else None


def show(value, digits=3):
    return f'{value:.{digits}f}' if isinstance(value, (int, float)) else 'pending' if value is None else str(value)


def relative(path):
    return str(Path(path).relative_to(ROOT))


def get_rounds():
    records = []
    for number in range(1,11):
        folder = ROOT / 'rounds' / f'{number:02d}'
        record = folder / 'record.json'
        row = {'round':number,'status':'not_started'}
        if record.exists():
            row.update(read(record))
        else:
            started = ROOT / 'candidates' / f'C{number:02d}' / 'research_started.json'
            if started.exists():
                evidence = read(started)
                row.update(status='record_pending',H_parent=evidence['H_parent'],M_parent=evidence['M_parent'],
                           M_program_used=evidence['M_program_used'],
                           reason='Research-start trace exists; no terminal round record. Live process state not inferred.')
            interrupted = folder / 'interrupted.json'
            if interrupted.exists():
                evidence = read(interrupted)
                row.update(status='interrupted',reason=evidence['error'],interrupted_phase=evidence['phase'])
        records.append(row)
    return records


def evaluator_failure(bw):
    error=bw.get('evaluation_error') or ''
    if bw['evaluation_status']=='completed':return 'scored'
    if 'protocol_pause.json' in error:return 'operator_pause_before_judge'
    if 'Final PNG signature' in error or 'delivery metadata were not supplied' in error:return 'missing_delivery_evidence'
    return 'other_eval_failure' if bw['evaluation_status']=='eval_failed' else 'not_started_or_pending'


def evaluator_revision(path):
    folder=path.parent;old=read(folder/'record_before_A02_evaluator.json');current=read(path)
    before,now=old['bw'],current['bw']
    evidence=read(folder/'bw_evidence/evidence_status.json') if (folder/'bw_evidence/evidence_status.json').exists() else {}
    revised=(now.get('native_evidence_version')==read(ROOT/'config.json')['evaluation']['native_evidence_version']
             and now.get('delivery_evidence_version')=='original_delivery_metadata_A02')
    old_calls=[p/'request.json' for p in folder.iterdir() if p.is_dir() and re.fullmatch(r'judge_\d+',p.name) and (p/'request.json').exists()]
    fresh_calls=[p/'request.json' for p in folder.glob('judge_A*') if (p/'request.json').exists()]
    old_sessions=[read(p.with_name('session.json')) for p in old_calls if p.with_name('session.json').exists()]
    return {'scene_id':current['scene_id'],'split':current['split'],'H_version':current['H_version'],'repeat':current['repeat'],
        'old_record_path':relative(folder/'record_before_A02_evaluator.json'),'current_record_path':relative(path),
        'old_execution_status':old['status'],'current_execution_status':current['status'],
        'old_evaluation_status':before['evaluation_status'],'old_BW':before.get('S_BW'),
        'old_S_rubric':before.get('S_rubric'),'old_S_dimension':before.get('S_dimension'),
        'old_rubric_results':before.get('rubric_scores'),'old_dimension_results':before.get('dimension_scores'),
        'old_failure_type':before.get('failure_type'),'old_evaluation_error':before.get('evaluation_error'),
        'old_audited_failure_class':evaluator_failure(before),
        'old_native_version':before.get('native_evidence_version') or 'pre_A02',
        'old_delivery_version':before.get('delivery_evidence_version') or 'pre_A02',
        'old_CLI_request_count':len(old_calls),'old_CLI_request_paths':[relative(p) for p in old_calls],
        'old_saved_session_count':len(old_sessions),'old_session_statuses':dict(Counter(s['status'] for s in old_sessions)),
        'old_known_input_tokens':sum(s['input_tokens'] for s in old_sessions if isinstance(s.get('input_tokens'),int)),
        'old_known_output_tokens':sum(s['output_tokens'] for s in old_sessions if isinstance(s.get('output_tokens'),int)),
        'old_usage_known_session_count':sum(isinstance(s.get('input_tokens'),int) for s in old_sessions),
        'current_raw_evaluation_status':now['evaluation_status'],'current_raw_BW':now.get('S_BW'),
        'current_result_native_version':now.get('native_evidence_version') or 'unknown',
        'current_result_delivery_version':now.get('delivery_evidence_version') or 'unknown',
        'available_native_version':evidence.get('native_evidence_version'),'available_delivery_version':evidence.get('delivery_evidence_version'),
        'available_evidence_status':evidence.get('evaluation_status'),'current_result_is_current_protocol':revised,
        'new_evaluation_status':now['evaluation_status'] if revised else 'pending_current_evaluation',
        'new_BW':now.get('S_BW') if revised else None,'new_S_rubric':now.get('S_rubric') if revised else None,
        'new_S_dimension':now.get('S_dimension') if revised else None,
        'new_failure_type':now.get('failure_type') if revised else None,
        'new_audited_failure_class':evaluator_failure(now) if revised else 'pending',
        'new_CLI_request_count':len(fresh_calls),'new_CLI_request_paths':[relative(p) for p in fresh_calls],
        'same_H_version_and_artifact_folder':old['H_version']==current['H_version'] and old['folder']==current['folder'],
        'algorithm_gain_comparison':False,
        'note':'Evaluator evidence revision of saved artifact; old score/failed attempts retained, no H resampling inferred'}


def get_evaluator_revisions():
    return [evaluator_revision(path.with_name('record.json')) for path in sorted((ROOT/'results').rglob('record_before_A02_evaluator.json'))]


def get_scenes():
    records = []
    expected_native=read(ROOT/'config.json')['evaluation']['native_evidence_version']
    selection_repeats=read(ROOT/'configs/selection_repeats.json')
    exclusion_reasons=read(ROOT/'configs/selection_repeat_rationale.json')
    for path in sorted((ROOT / 'results').rglob('record.json')):
        row = read(path)
        if 'scene_id' not in row:
            continue
        metrics = row.get('metrics') or {}
        bw = row.get('bw') or {}
        revision=evaluator_revision(path) if path.with_name('record_before_A02_evaluator.json').exists() else None
        if (bw.get('native_evidence_version')!=expected_native
                or bw.get('delivery_evidence_version')!='original_delivery_metadata_A02'):
            bw={**bw,'S_BW':None,'S_rubric':None,'S_dimension':None,'dimension_scores':[],
                'rubric_scores':None,'evaluation_status':'pending_current_evaluation'}
        functional = row.get('functional') or {}
        primary=(row['split']!='selection' or row['repeat']==selection_repeats[row['H_version']][row['scene_id']])
        records.append({**row, 'record_path': relative(path), 'primary_analysis':primary,
            'analysis_scope':'primary' if primary else 'superseded_selection_attempt_retained_raw',
            'excluded_primary_reason':None if primary else exclusion_reasons[row['H_version']][row['scene_id']][str(row['repeat'])],
            'record_raw_BW':row['bw'].get('S_BW'),'record_raw_evaluation_status':row['bw']['evaluation_status'],
            'evaluator_revision_status':revision['new_evaluation_status'] if revision is not None else None,
            'Q': metrics.get('overall'), 'PSNR': metrics.get('psnr'), 'SSIM': metrics.get('ssim'),
            'LPIPS': metrics.get('lpips'), 'DINO': metrics.get('dino'),
            'BW': bw.get('S_BW'), 'S_rubric': bw.get('S_rubric'), 'S_dimension': bw.get('S_dimension'),
            'dimensions': {row['id']:row['score'] for row in bw.get('dimension_scores', [])},
            'rubric_results': bw.get('rubric_scores'),
            'evaluation_status': bw.get('evaluation_status', 'not_started'),
            'functional_pass': functional.get('functional_pass'), 'functional_checks': functional.get('checks'),
            'e2e_BW_utility': bw.get('S_BW') if row.get('valid') is True and bw.get('S_BW') is not None
                              else 0 if row.get('status') in {'failed', 'timeout', 'invalid'} else None})
    return records


def get_actions():
    records = []
    rounds = {row['round']:row for row in get_rounds()}
    for path in sorted((ROOT / 'meta_traces').glob('round*/actions/*/observation.json')):
        observation = read(path)
        request_path = path.with_name('action_request.json')
        request = read(request_path) if request_path.exists() else {}
        round_id = path.parents[2].name
        number = int(round_id.removeprefix('round'))
        parent = rounds[number].get('M_parent')
        started = ROOT / 'candidates' / f'C{number:02d}' / 'research_started.json'
        if parent is None and started.exists():
            parent = read(started)['M_parent']
        snapshot = path.parent / request['source_snapshot'] if 'source_snapshot' in request else None
        revision = request.get('action_revision')
        records.append({'round_id':round_id,
            'action_name':request.get('action_name',observation.get('action','unknown')),
            'creator_M':request.get('creator_M'), 'action_revision':revision,
            'source_version':str(request['creator_M']) + ':' + str(request['action_name']) + ':r' + str(revision)
                             if revision is not None and request.get('creator_M') is not None else None,
            'source_snapshot':relative(snapshot) if snapshot is not None else None,
            'source_snapshot_available':snapshot.exists() if snapshot is not None else False,
            'executed_M':parent, 'action_library_M':request.get('M',observation.get('M')),
            'scene_id':request.get('scene_id',observation.get('scene_id')),
            'status':observation['status'], 'input':request, 'output':observation,
            'expected':request.get('expectation',observation.get('expectation')),
            'decision_changed':observation.get('decision_changed'), 'source':relative(path)})
    seen, first_sources = Counter(), {}
    for row in records:
        identity = (row['action_name'],row['creator_M'],row['action_revision'])
        if row['source_version'] is not None and row['source_snapshot_available'] and row['output'].get('process') is not None:
            source = (ROOT / row['source_snapshot']).read_text()
            if identity not in first_sources:
                first_sources[identity] = source
            consistent = first_sources[identity] == source
            row['snapshot_consistent_for_recorded_version'] = consistent
            if consistent:
                seen[identity] += 1
                row['execution_index_for_action_identity'] = seen[identity]
                row['reuse'] = seen[identity] > 1
            else:
                row['execution_index_for_action_identity'] = None
                row['reuse'] = None
        else:
            row['snapshot_consistent_for_recorded_version'] = None
            row['execution_index_for_action_identity'] = None
            row['reuse'] = None
    return records


def get_cli():
    records = []
    for path in sorted(ROOT.rglob('session.json')):
        if 'code_snapshots' in path.relative_to(ROOT).parts:
            continue
        session = read(path)
        if not path.with_name('request.json').exists():
            continue
        tools = session.get('observable_tool_counts') or {}
        records.append({**session, 'session_path': relative(path),
            'observed_model': session.get('observed_model', session.get('actual_model', 'unknown')),
            'command_executions': tools.get('command_execution'), 'file_changes': tools.get('file_change'),
            'image_reads': tools.get('image_view'), 'visible_subagent_calls': tools.get('collab_tool_call'),
            'visible_tools': session.get('tool_calls'),
            'observable_model_requests_lower_bound': session.get('observable_model_requests_lower_bound'),
            'exact_model_requests': session.get('exact_model_requests'),
            'request_visibility_coverage': session.get('request_visibility_coverage'),
            'image_attachment_count': len(session.get('images', []))})
    return records


def get_timings():
    records = []
    for path in sorted(ROOT.rglob('*process.json')):
        data = read(path)
        if 'seconds' not in data or 'command' not in data:
            continue
        records.append({**data,'record_path':relative(path),'measurement_type':'process_tree',
            'stage':path.stem.removesuffix('_process'), 'scope':data.get('cpu_scope','unknown'),
            'cpu_seconds':data['cpu_user_seconds'] + data['cpu_system_seconds']
                           if all(isinstance(data.get(key),(int,float)) for key in
                                  ('cpu_user_seconds','cpu_system_seconds')) else None,
            'aggregation_note':'Nested process-tree scopes overlap; do not add to enclosing wall/CPU totals'})
    for path in sorted(ROOT.rglob('metric_timing.jsonl')):
        for line_number,line in enumerate(path.read_text().splitlines(),1):
            event = json.loads(line)
            records.append({**event,'record_path':relative(path),'line_number':line_number,
                'measurement_type':'numeric_metric_stage', 'stage':event['stage'],
                'scope':event.get('scope','numeric metric model load in current process; no child-tree CPU measurement'),
                'finished':event['time'], 'started':None,
                'cpu_seconds':event['cpu_user_seconds'] + event['cpu_system_seconds']
                               if all(isinstance(event.get(key),(int,float)) for key in
                                      ('cpu_user_seconds','cpu_system_seconds')) else None,
                'aggregation_note':'Substage event, not additive with enclosing process scope; parent RSS is lifetime high-water mark'})
    return records


def get_render_accounting():
    ledgers = {path.parent:path for path in ROOT.rglob('render_ledger.json')
               if 'code_snapshots' not in path.relative_to(ROOT).parts}
    events = {path.parent:path for path in ROOT.rglob('stage_events.jsonl')
              if 'code_snapshots' not in path.relative_to(ROOT).parts}
    views = {}
    for path in ROOT.rglob('*_render.json'):
        if 'code_snapshots' in path.relative_to(ROOT).parts:
            continue
        metadata = read(path)
        if 'view_id' in metadata and metadata.get('status') in ['running','completed']:
            views.setdefault(path.parent,[]).append(path)
    rows = []
    for folder in sorted(set(ledgers) | set(events) | set(views)):
        ledger = read(ledgers[folder]) if folder in ledgers else None
        event_rows = [json.loads(line) for line in events[folder].read_text().splitlines()] if folder in events else []
        if folder in views:
            metadata = [read(path) for path in views[folder]]
            selected,attempts,completed = 'per_view_render_metadata',len(metadata),sum(row['status']=='completed' for row in metadata)
            selected_paths = [relative(path) for path in views[folder]]
            note = 'One metadata record per view; running means renderer-entry attempt recorded, not proof of a completed frame'
        elif folder in events:
            selected = 'stage_render_events'
            attempts = sum(row['stage']=='render_started' for row in event_rows)
            completed = sum(row['stage']=='render_completed' for row in event_rows)
            selected_paths = [relative(events[folder])]
            note = 'Count only explicit render_started/completed events; do not also add the same-folder ledger'
        else:
            selected = 'outer_prelaunch_ledger' if any(part.startswith('cpu_benchmark') for part in folder.relative_to(ROOT).parts) else 'render_ledger'
            attempts,completed = ledger['render_attempts'],ledger['renders_completed']
            selected_paths = [relative(ledgers[folder])]
            note = 'Ledger counters as recorded; some callers record attempts before process launch, so these are not exact renderer starts'
        rows.append({'scope_path':relative(folder),'selected_source_type':selected,'selected_sources':selected_paths,
            'recorded_attempts':attempts,'recorded_completed':completed,
            'ledger_source':relative(ledgers[folder]) if folder in ledgers else None,
            'ledger_recorded_attempts':ledger['render_attempts'] if ledger is not None else None,
            'ledger_recorded_completed':ledger['renders_completed'] if ledger is not None else None,
            'exact_whole_experiment_count':False,'note':note})
    budget_path = ROOT / 'render_attempts.jsonl'
    budget_rows = [json.loads(line) for line in budget_path.read_text().splitlines()] if budget_path.exists() else None
    selected_counts = {}
    for source_type in sorted({row['selected_source_type'] for row in rows}):
        source_rows = [row for row in rows if row['selected_source_type']==source_type]
        selected_counts[source_type] = {'scope_count':len(source_rows),
            'recorded_attempts':sum(row['recorded_attempts'] for row in source_rows),
            'recorded_completed':sum(row['recorded_completed'] for row in source_rows)}
    correction_path = ROOT / 'preparation/cpu_benchmark_budget_correction.json'
    correction = read(correction_path) if correction_path.exists() else None
    main_charged=sum(row['frames'] for row in budget_rows) if budget_rows is not None else None
    stage=ROOT/'meta_replay_stage';stage_ledger=stage/'render_attempts.jsonl'
    stage_charged=sum(json.loads(line)['frames'] for line in stage_ledger.read_text().splitlines()) if stage_ledger.exists() else None
    combined=main_charged+stage_charged if main_charged is not None and stage_charged is not None else main_charged if not stage.exists() else None
    summary = {'render_budget_charged':main_charged,
        'main_render_budget_charged':main_charged,'replay_render_budget_charged':stage_charged,
        'combined_render_budget_charged':combined,
        'render_budget_charge_events':len(budget_rows) if budget_rows is not None else None,
        'render_budget_source':'render_attempts.jsonl','actual_render_attempts_exact':None,
        'actual_render_completed_exact':None,'selected_evidence_scope_count':len(rows),
        'selected_recorded_counts_by_source_type':selected_counts,
        'same_scope_source_precedence':'per-view metadata, else stage events, else ledger; no duplicate addition within a scope',
        'CPU_benchmark_budget_correction':correction,
        'coverage_note':'Global guard ledger measures budget charges; functional() reserves 3 even when fewer frames are applicable. '
                         'Physical renderer counts are not comprehensively instrumented; exact actual totals remain unknown. '
                         'Recorded counters from different interface semantics are reported separately, not added into an exact total.'}
    return rows,summary


def figure(name, caption, sources):
    path = ROOT / 'figures' / name
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return {'path': relative(path), 'caption': caption, 'sources': sources, 'script': 'analyze.py'}


def plot_evolution(rounds):
    plt.figure(figsize=(10, 4))
    base_path = ROOT / 'round0.json'
    baseline_record=read(base_path) if base_path.exists() else None
    config=read(ROOT/'config.json')
    current=(baseline_record is not None
             and baseline_record.get('platform_version')==config['pilot']['platform_version']
             and baseline_record['selection']['evaluation_completed']==config['pilot']['selection_size'])
    baseline=baseline_record['selection']['S_BW'] if current else None
    retained = [(0, baseline)] if isinstance(baseline, (int,float)) else []
    previous = baseline
    measured = []
    for row in rounds:
        score = row['selection'].get('S_BW') if isinstance(row.get('selection'),dict) else None
        if isinstance(score, (int,float)):
            measured.append((row['round'],score))
            plt.scatter(row['round'],score,marker='o' if row.get('H_accepted') else 'x',
                        color='#16834a' if row.get('H_accepted') else '#be4b36',s=50)
        if row.get('H_accepted') and score is not None:
            previous = score
        if row['status'] != 'not_started' and isinstance(previous,(int,float)):
            retained.append((row['round'],previous))
    if retained:
        plt.plot([p[0] for p in retained],[p[1] for p in retained],'-s',color='#215e9d',label='Actually retained H')
        plt.legend()
    if not measured and not retained:
        plt.text(.5,.5,'Selection pending: no measured formal scores',transform=plt.gca().transAxes,ha='center')
    plt.xticks(range(0,11));plt.xlim(-.5,10.5);plt.xlabel('Continuous research round (0 = fresh baseline)')
    plt.ylabel('BW-style / CLI-adapted (0-100)')
    return figure('evolution.png','蓝线记录实际保留版本的晋升时验证评分，圆点为接受候选、叉号为未接受候选；后续边界复评原始记录另见scenes.csv中的bw_judgments，不反向覆盖历史决策点。资格恢复晋升不自动代表配对视觉增益。不对未运行轮次填零；连续轨迹不是十次独立重复。', ['metrics/rounds.csv'] + (['round0.json'] if base_path.exists() else []))


def plot_quality(scenes):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for axis, split in zip(axes, ['development', 'selection', 'test']):
        rows = [row for row in scenes if row['split'] == split and isinstance(row['BW'], (int, float))]
        versions = list(dict.fromkeys(row['H_version'] for row in rows))
        for index, version in enumerate(versions):
            values = [row['BW'] for row in rows if row['H_version'] == version]
            axis.scatter([index] * len(values), values, s=24, alpha=.8)
        axis.set_xticks(range(len(versions)), versions, rotation=35, ha='right')
        if not rows:
            axis.text(.5, .5, 'pending / no measured BW', transform=axis.transAxes, ha='center')
        axis.set_title(f'{split}: n={len(rows)} measured generations')
        axis.set_ylim(0, 100); axis.set_ylabel('BW-style / CLI-adapted')
    return figure('quality_points.png', '当前有效评价协议下各划分逐生成 BW 点；开发 preview 与正式 Selection/Test 分开。修订前评分完整另存evaluator_revision.csv，不混作同协议提升。缺测和未开始不显示零分。统计单位为生成产物，独立场景数另见CSV。', ['metrics/scenes.csv','metrics/evaluator_revision.csv'])


def paired_test_data(scenes, manifest, state, repeats):
    start=state['H_start'];best=state.get('H_best',state.get('H_retained',start))
    rows=[];points=[]
    for scene in manifest:
        if scene['split']!='test':continue
        groups={}
        row={'scene_id':scene['scene_id'],'H_start':start,'H_best':best,'planned_repeats':repeats,
             'same_H_artifact_reuse':start==best}
        for role,version in [('start',start),('best',best)]:
            records={record['repeat']:record for record in scenes if record['split']=='test'
                     and record['scene_id']==scene['scene_id'] and record['H_version']==version}
            groups[role]=records
            row[role+'_finished']=sum(record['status'] in TERMINAL for record in records.values())
            row[role+'_execution_success']=sum(record['valid'] is True for record in records.values())
            row[role+'_BW_measured']=sum(record['BW'] is not None for record in records.values())
            row[role+'_BW_conditional']=mean(record['BW'] for record in records.values())
            utilities=[records[index]['e2e_BW_utility'] if index in records else None for index in range(1,repeats+1)]
            row[role+'_BW_utility']=mean(utilities) if all(value is not None for value in utilities) else None
            for index in range(1,repeats+1):
                record=records.get(index)
                points.append({'scene_id':scene['scene_id'],'role':role,'H_version':version,'repeat':index,
                    'status':record['status'] if record else 'not_started','BW':record['BW'] if record else None,
                    'Q':record['Q'] if record else None,'utility':record['e2e_BW_utility'] if record else None})
        paired=[(groups['start'][index],groups['best'][index]) for index in range(1,repeats+1)
                if index in groups['start'] and index in groups['best']
                and groups['start'][index]['valid'] and groups['best'][index]['valid']
                and groups['start'][index]['BW'] is not None and groups['best'][index]['BW'] is not None]
        row['paired_successful_generations']=len(paired)
        row['BW_paired_difference']=mean(right['BW']-left['BW'] for left,right in paired)
        row['Q_paired_difference']=mean(right['Q']-left['Q'] for left,right in paired if left['Q'] is not None and right['Q'] is not None)
        row['BW_utility_difference']=row['best_BW_utility']-row['start_BW_utility'] if row['best_BW_utility'] is not None and row['start_BW_utility'] is not None else None
        rows.append(row)
    return rows,points


def plot_test_pairs(rows, points):
    fig,axes=plt.subplots(1,2,figsize=(13,4))
    for index,row in enumerate(rows):
        for role,color,offset in [('start','#315f9c',-.12),('best','#16834a',.12)]:
            values=[point for point in points if point['scene_id']==row['scene_id'] and point['role']==role and point['BW'] is not None]
            for point in values:
                axes[0].scatter(index+offset+.025*(point['repeat']-1),point['BW'],color=color,s=24,alpha=.55)
            value=row[role+'_BW_conditional']
            if value is not None:axes[0].scatter(index+offset,value,color=color,marker='D',s=55)
        delta=row['BW_paired_difference']
        if delta is None:axes[1].text(index,0,'pending /\nno scored pair',rotation=90,ha='center',va='bottom',fontsize=8)
        else:axes[1].scatter(index,delta,color='#16834a' if delta>=0 else '#be4b36',s=50)
    if not any(point['BW'] is not None for point in points):axes[0].text(.5,.5,'Final Test pending',transform=axes[0].transAxes,ha='center')
    axes[0].set_ylim(0,100);axes[0].set_ylabel('BW-style / CLI-adapted')
    axes[0].set_title('Raw repeats + source means (diamonds): blue start, green best')
    axes[1].axhline(0,color='#999',linewidth=.8);axes[1].set_ylabel('Best - start BW, matched successful repeat IDs')
    axes[1].set_title('One conditional difference per independent source')
    for axis in axes:axis.set_xticks(range(len(rows)),[row['scene_id'] for row in rows],rotation=35,ha='right')
    return figure('final_test_pairs.png','按真实独立来源聚合重复生成；左图保留全部实测原始点与每来源条件均值，右图仅在同一repeat双方都成功且取得BW时计算差异。失败原始BW仍为null；失败计零的端到端效用另列CSV，评价服务失败与pending不填零。同一H复用不是独立生成。没有置信区间或显著性声明。',['metrics/paired_test_sources.csv','metrics/paired_test_generations.csv','metrics/scenes.csv'])


def plot_dimensions_and_functions(scenes):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    observed = []
    for row in scenes:
        dims = row['dimensions']
        if isinstance(dims, dict):
            values = [dims.get(name) for name in DIMENSIONS]
            values = [value.get('rating') if isinstance(value, dict) else value for value in values]
            if all(isinstance(value, (int, float)) for value in values):
                observed.append(values)
                axes[0].plot(range(8), values, 'o-', alpha=.4, linewidth=.8)
    axes[0].set_xticks(range(8), [name.replace('_', '\n') for name in DIMENSIONS], fontsize=7)
    axes[0].set_ylim(1, 10); axes[0].set_ylabel('Raw eight-dimension rating')
    if not observed:
        axes[0].text(.5, .5, 'pending', transform=axes[0].transAxes, ha='center')
    statuses = Counter()
    for row in scenes:
        if row.get('functional_pass') is not None:
            statuses['measured_pass' if row['functional_pass'] else 'measured_fail'] += 1
        else:
            statuses['not_measured'] += 1
    if statuses:
        axes[1].bar(list(statuses), list(statuses.values()))
        axes[1].set_ylabel('Recorded scene generations (counts)')
    else:
        axes[1].text(.5, .5, 'Functional evaluation pending', transform=axes[1].transAxes, ha='center')
    axes[1].set_title('Functional observations; required/applicable/gate in CSV')
    return figure('dimensions_and_function.png', '当前有效评价协议的逐产物八维评分与实际功能测量计数；修订前评分另存evaluator_revision.csv。未测不算失败，也不算通过。required/applicable/measured_pass/gate_pass原始对象完整保留于CSV。机械编辑不等于文字编辑能力。', ['metrics/scenes.csv','metrics/evaluator_revision.csv'])


def plot_cost(cli, timing, render_summary):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    roles = Counter(row.get('role', 'unknown') for row in cli)
    axes[0].bar(list(roles), list(roles.values())); axes[0].set_title(f'Actual CLI sessions: {len(cli)}')
    values = [row['seconds'] for row in timing if isinstance(row.get('seconds'), (int, float))]
    if values:
        axes[1].scatter(range(1, len(values) + 1), values, s=18)
    else:
        axes[1].text(.5, .5, 'pending', transform=axes[1].transAxes, ha='center')
    axes[1].set_title('Observed stage/process duration'); axes[1].set_ylabel('wall seconds (overlapping scopes not summed)')
    token_rows = [row for row in cli if isinstance(row.get('input_tokens'), int) and isinstance(row.get('output_tokens'), int)]
    axes[2].bar(['input', 'output'], [sum(row[key] for row in token_rows) for key in ('input_tokens', 'output_tokens')])
    axes[2].set_title(f'Visible tokens; coverage {len(token_rows)}/{len(cli)} sessions')
    return figure('cost_and_timing.png', '实际会话、阶段/进程墙钟原始点和可见token总量。timing.csv中进程树与metric阶段可能嵌套，不加和。主根渲染预算扣额为' + str(render_summary['render_budget_charged']) + '，主根+独立回放根联合扣额为' + str(render_summary['combined_render_budget_charged']) + '，包含功能检查的保守预扣；它不是精确实际帧数。实际总尝试/完成数未知，分来源记录见render_evidence.csv。parent RSS是生命周期高水位；费用未知。', ['metrics/cli_audit.csv', 'metrics/timing.csv', 'metrics/render_evidence.csv']
        + (['render_attempts.jsonl'] if (ROOT/'render_attempts.jsonl').exists() else [])
        + (['preparation/cpu_benchmark_budget_correction.json'] if (ROOT/'preparation/cpu_benchmark_budget_correction.json').exists() else []))


def plot_cpu_benchmark():
    path = ROOT / 'preparation/cpu_benchmark_corrected_import/cpu_benchmark.json'
    plt.figure(figsize=(7, 4))
    if path.exists():
        rows = read(path)
        for row in rows:
            if row['ok']:
                plt.scatter(row['threads'], row['seconds'], s=50)
                plt.annotate(f"{row['seconds']:.2f}s", (row['threads'], row['seconds']))
        plt.xticks([row['threads'] for row in rows])
    else:
        plt.text(.5, .5, 'benchmark pending', transform=plt.gca().transAxes, ha='center')
    plt.xlabel('Blender threads, one worker'); plt.ylabel('Wall seconds / identical saved scene')
    return figure('cpu_benchmark.png', '同一历史场景、同一512×512/Cycles16配置的2/4/8线程微基准，各一次；不是算法速度比较。首次psutil导入错误3次均保留，不纳入成功吞吐。', ['preparation/cpu_benchmark_corrected_import/cpu_benchmark.json'])


def contact_sheet(manifest, scenes, rounds, state):
    versions = [('Reference', None), ('H_start', state.get('H_start', 'historical_r1_C2_start')),
                ('Round 5 retained', rounds[4].get('H_retained')), ('Round 10 retained', rounds[9].get('H_retained')),
                ('H_best', state.get('H_best'))]
    dev = sorted((row for row in manifest if row['split'] == 'development'), key=lambda row: row['order'])
    cell_w, cell_h = 230, 220
    panel = Image.new('RGB', (cell_w * 5, 40 + cell_h * len(dev)), 'white')
    draw = ImageDraw.Draw(panel)
    for column, (label, version) in enumerate(versions):
        draw.text((column * cell_w + 5, 8), label + (' / pending' if version is None and column else ''), fill='black')
    for index, scene in enumerate(dev):
        for column, (label, version) in enumerate(versions):
            x, y = column * cell_w, 40 + index * cell_h
            draw.rectangle((x, y, x + cell_w - 2, y + cell_h - 2), outline='#bbbbbb')
            record = next((row for row in scenes if row['scene_id'] == scene['scene_id'] and row['split'] == 'development'
                           and row['H_version'] == version), None) if version else None
            image_path = Path(scene['image_path']) if column == 0 else Path(record['folder']) / 'final.png' if record else None
            if image_path is not None and image_path.exists():
                with Image.open(image_path) as image:
                    thumbnail = ImageOps.contain(image.convert('RGB'), (cell_w - 8, 160))
                panel.paste(thumbnail, (x + (cell_w - thumbnail.width) // 2, y + 4))
            else:
                draw.text((x + 15, y + 65), 'No output / pending' if not record else str(record['status']), fill='#880000')
            draw.text((x + 4, y + 167), scene['scene_id'], fill='black')
            if column:
                draw.text((x + 4, y + 181), (str(version)[:32] if version else 'pending'), fill='black')
                draw.text((x + 4, y + 195), f"BW={show(record['BW']) if record else 'pending'} Q={show(record['Q']) if record else 'pending'}", fill='black')
                if version is not None and any(previous == version for _, previous in versions[1:column]):
                    draw.text((x + 170, y + 181), 'reuse', fill='#225588')
    path = ROOT / 'figures/development_contact_sheet.png'
    panel.save(path)
    return {'path': relative(path), 'caption': f'历史开发图按预定顺序全部展示，n={len(dev)}来源；这些图片为研发已暴露数据，不是泛化证据。同一H版本复用同一产物标reuse，失败或未运行保留空位。',
            'sources': ['manifest.json', 'metrics/scenes.csv', 'metrics/rounds.csv'], 'script': 'analyze.py'}


def plot_research_chain(actions, scenes, rounds):
    completed = [row for row in actions if row['status'] == 'completed']
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for axis in axes:
        axis.axis('off')
    if completed:
        action = completed[0]  # Prespecified first completed action, independent of score.
        observation = action['output']
        round_number = int(action['round_id'].removeprefix('round'))
        parent_H = rounds[round_number-1].get('H_parent')
        scene = next((row for row in scenes if row['scene_id']==observation['scene_id']
                      and row['split']=='development' and row['H_version']==parent_H),None)
        paths = [Path(scene['folder']) / 'reference.png' if scene else None,
                 Path(scene['folder']) / 'final.png' if scene else None]
        for axis, path, title in zip(axes[:2], paths, ['Actual reference', 'Current reconstruction']):
            if path is not None and path.exists():
                with Image.open(path) as image:
                    axis.imshow(image.convert('RGB'))
            else:
                axis.text(.5, .5, 'No rendered output', ha='center')
            axis.set_title(title)
        detail = 'Action: ' + str(action['action_name']) + '\nExpected: ' + json.dumps(action['expected'], ensure_ascii=True)[:300]
        detail += '\nObserved: ' + json.dumps(observation.get('measurement'), ensure_ascii=True)[:600]
        candidate=ROOT/'candidates'/f'C{round_number:02d}'
        proposal=read(candidate/'proposal.json')
        detail += '\nFinal decision: '+proposal['analysis'][:450]
        detail += '\nActual changed files: '+str([(change['target'],change['path']) for change in proposal['changes']])
        detail += '\nRead-only facts; no diagnostic render.' if not observation.get('render') else '\nDiagnostic render retained with raw action record.'
        import textwrap
        axes[2].text(0, 1, '\n'.join(textwrap.wrap(detail, 58)), va='top', fontsize=8)
        sources = ['metrics/actions.csv', action['source'], 'metrics/rounds.csv',relative(candidate/'proposal.json'),relative(candidate/'M.diff'),relative(candidate/'H.diff')]
    else:
        axes[1].text(.5, .5, 'No completed formal research action yet.\nResearch chain pending.', ha='center')
        sources = ['metrics/actions.csv', 'metrics/rounds.csv']
    return figure('research_chain.png', '按时间选择第一条完成的正式研究动作，无论成功或失败；图像和观测均来自该动作。动作执行本身不证明原因唯一或H改善，后续决策、diff和迁移结果需合并审查。', sources)


def plot_shared_patch_case(actions, scenes, rounds, manifest):
    """Post-run process illustration, selected by chronology rather than gain."""
    linked=[action for action in actions if action['status']=='completed'
            and rounds[int(action['round_id'].removeprefix('round'))-1]['H_candidate'] is not None]
    if not linked:
        return None
    action=linked[0];number=int(action['round_id'].removeprefix('round'))
    row=rounds[number-1];candidate=ROOT/'candidates'/f'C{number:02d}'
    proposal=read(candidate/'proposal.json');observation=action['output']
    development=next(scene for scene in scenes if scene['split']=='development'
                     and scene['scene_id']==observation['scene_id'] and scene['H_version']==row['H_parent'])
    pairs=[]
    for item in manifest:
        if item['split']!='selection':continue
        parent=next((scene for scene in scenes if scene['scene_id']==item['scene_id']
                     and scene['split']=='selection' and scene['H_version']==row['H_parent']),None)
        child=next((scene for scene in scenes if scene['scene_id']==item['scene_id']
                    and scene['split']=='selection' and scene['H_version']==row['H_candidate']),None)
        pairs.append({'scene_id':item['scene_id'],'parent':parent,'candidate':child})
    material_summary=[]
    for obj in observation['measurement']['objects']:
        values={'Roughness':set(),'Metallic':set()};linked=set()
        for material in obj['materials']:
            for node in material['shader_nodes']:
                for name,socket in node['inputs'].items():
                    if socket['linked']:linked.add(name)
                    elif name in values:values[name].add(socket['value'])
        material_summary.append({'object_id':obj['object_id'],'mesh_count':obj['mesh_count'],
                                 'unlinked_input_defaults':{key:sorted(value) for key,value in values.items()},
                                 'linked_inputs':sorted(linked)})
    compact_pairs=[{'scene_id':pair['scene_id'],**{role:{key:pair[role][key] for key in
                   ['record_path','H_version','status','BW','Q','functional_pass']} if pair[role] else None
                   for role in ['parent','candidate']}} for pair in pairs]
    facts={'case_selection':'Post-ten-round illustration: earliest completed action in a round with an H candidate, independent of acceptance or score',
           'round':number,'action_source':action['source'],'action_name':action['action_name'],
           'action_scene_id':observation['scene_id'],'expectation':action['expected'],
           'H_parent':row['H_parent'],'H_candidate':row['H_candidate'],
           'H_accepted':row['H_accepted'],'proposal_source':relative(candidate/'proposal.json'),
           'M_after_observation':proposal['analysis'],'H_diff_source':relative(candidate/'H.diff'),'selection_pairs':compact_pairs,
           'material_summary':material_summary,'causal_effect_verified':False}
    (ROOT/'metrics/shared_patch_case.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
    fig,axes=plt.subplots(len(pairs)+1,4,figsize=(17,4*(len(pairs)+1)))
    for axis in axes.flat:axis.axis('off')
    def show_image(axis,path,title):
        if path is not None and path.exists():
            with Image.open(path) as image:axis.imshow(image.convert('RGB'))
        else:axis.text(.5,.5,'No saved output',ha='center')
        axis.set_title(title)
    def text(axis,value):
        import textwrap
        axis.text(0,1,'\n'.join(textwrap.wrap(value,49)),va='top',fontsize=9)
    show_image(axes[0,0],Path(development['folder'])/'reference.png','Development reference (exposed)')
    show_image(axes[0,1],Path(development['folder'])/'final.png',row['H_parent']+' current reconstruction')
    text(axes[0,2],'ACTION: '+action['action_name']+'\nEXPECTED: '+str(action['expected'])[:350]
         +'\nMEASURED (excerpt): '+json.dumps(material_summary,ensure_ascii=True)[:700]
         +'\nRead-only inspection; no intervention render. Full values in linked JSON.')
    patch=(candidate/'H.diff').read_text()
    added='\n'.join(line for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
    text(axes[0,3],'M AFTER OBSERVATION: '+proposal['analysis'][:500]
         +'\nACTUAL H DIFF (excerpt): '+added[:400])
    for index,pair in enumerate(pairs,1):
        parent,child=pair['parent'],pair['candidate']
        text(axes[index,0],pair['scene_id']+'\nSelection; fixed source order.\nSeparate generation per H.\nAuthor views shown; BW uses independent fixed evaluation views.')
        for axis,record,label in [(axes[index,1],parent,row['H_parent']),(axes[index,2],child,row['H_candidate'])]:
            show_image(axis,Path(record['folder'])/'final.png' if record else None,label)
        text(axes[index,3],f"BW: {show(parent['BW']) if parent else 'pending'} -> {show(child['BW']) if child else 'pending'}\n"
             +f"Q: {show(parent['Q']) if parent else 'pending'} -> {show(child['Q']) if child else 'pending'}\n"
             +f"Execution: {parent['status'] if parent else 'pending'} / {child['status'] if child else 'pending'}\n"
             +f"Functional: {parent['functional_pass'] if parent else 'pending'} / {child['functional_pass'] if child else 'pending'}\n"
             +f"Candidate retained: {row['H_accepted']}. No causal or meta-ability improvement inferred.")
    sources=['metrics/shared_patch_case.json',action['source'],relative(candidate/'proposal.json'),relative(candidate/'H.diff'),'metrics/scenes.csv','metrics/actions.csv','metrics/rounds.csv']
    return figure('shared_patch_case.png','十轮结束后按时间选择最早具有真实动作与共享H候选的研发回合，不按收益挑选；展示全部三张Selection来源。上行是实际开发参考、重建、原生测量与后续代码修改；下行是不同来源的真实产物与指标。只说明程序研发链运行；独立生成的差异不能证明动作的因果收益。只读材质检查没有干预渲染，也不自动确认亮度的唯一原因。',sources)


def service_event_rows():
    rows=[]
    for path in sorted(ROOT.rglob('request.json')):
        events=path.with_name('events.jsonl');session_path=path.with_name('session.json')
        if not events.exists() or not session_path.exists():continue
        request=read(path);session=read(session_path)
        for line_number,line in enumerate(events.read_text().splitlines(),1):
            if not line.strip():continue
            event=json.loads(line)
            if event['type']=='error':message=event['message']
            elif event.get('item',{}).get('type')=='error':message=event['item']['message']
            else:continue
            category=('transport_refused' if 'Connection refused' in message else
                      'model_capacity' if 'at capacity' in message else 'other_CLI_error_event')
            rows.append({'session_path':relative(path.parent),'role':request['role'],
                         'requested_model':request['requested_model'],'session_status':session['status'],
                         'session_seconds':session.get('seconds'),'event_line':line_number,
                         'event_time':None,'category':category,'message':message,
                         'model_request_count':None,'interpretation':'Observable service event, not a model inference count or geometry failure'})
    return rows


def interrupted_generation_rows():
    rows=[]
    for path in sorted((ROOT/'results').glob('*/*/*/*/status.json')):
        if path.with_name('record.json').exists():continue
        status=read(path)
        if not status.get('error'):continue
        version,split,scene,repeat=path.relative_to(ROOT/'results').parts[:4]
        sessions=[read(p) for p in path.parent.glob('student_calls/*/session.json')]
        rows.append({'H_version':version,'split':split,'scene_id':scene,'repeat':int(repeat),
                     'status':'interrupted','raw_generation_error':status['error'],
                     'generation_seconds':status['seconds'],'CLI_statuses':[s['status'] for s in sessions],
                     'scene_blend_exists':path.with_name('scene.blend').exists(),
                     'final_image_exists':path.with_name('final.png').exists(),
                     'BW':None,'Q':None,'utility':None,'source':relative(path),
                     'interpretation':'Saved generation error; final task record was not written. Not an unstarted sample or a measured geometry score.'})
    return rows


def plot_semantic_edits(state,config):
    versions=list(dict.fromkeys([state['H_start'],state.get('H_best',state.get('H_retained',state['H_start']))]))
    planned=[(version,scene) for scene in config['pilot']['semantic_edit_subset'] for version in versions]
    fig,axes=plt.subplots(len(planned),3,figsize=(13,3.5*len(planned)),squeeze=False)
    rows=[];sources=['metrics/semantic_edit_summary.csv','semantic_edit.py']
    for index,(version,scene) in enumerate(planned):
        folder=ROOT/'semantic_edits'/version/scene;status_path=folder/'status.json'
        status=read(status_path) if status_path.exists() else {'status':'not_started'}
        checks=status['checks'] if 'checks' in status else None
        row={'H_version':version,'scene_id':scene,'status':status['status'],
             'instruction':config['pilot']['semantic_edit_instruction'],'checks':checks,
             'semantic_target_correctness':status.get('semantic_target_correctness'),
             'semantic_target_correctness_status':'not_independently_validated',
             'source':relative(status_path) if status_path.exists() else None}
        rows.append(row)
        if status_path.exists():sources.append(relative(status_path))
        for axis,name in zip(axes[index,:2],['before.png','after.png']):
            path=folder/name
            if path.exists():
                with Image.open(path) as image:axis.imshow(image.convert('RGB'))
            else:axis.text(.5,.5,status['status']+' / no saved image',ha='center')
            axis.set_title(version+' / '+scene+' / '+name);axis.axis('off')
        import textwrap
        detail='Same fixed text instruction: change central furniture surface to blue; preserve geometry and all other objects.\nStatus: '+status['status']
        detail+='\nMEASURED CHECKS: '+json.dumps(checks,ensure_ascii=True)[:1000]
        detail+='\nText-to-edit procedure, one Terra call / one execution / no repair. Center/furniture semantic identity NOT independently validated.'
        axes[index,2].text(0,1,'\n'.join(textwrap.wrap(detail,55)),va='top',fontsize=8);axes[index,2].axis('off')
    save_csv('semantic_edit_summary.csv',rows,['H_version','scene_id','status','instruction','checks','semantic_target_correctness','semantic_target_correctness_status','source'])
    return figure('semantic_edit_results.png','预先固定的两张开发图、共同起点与H_best；同一文字编辑器、同一指令和调用/执行上限，展示全部四个预定编辑。快照测量目标颜色、几何与非目标保持，真实中心家具语义身份仍未独立验证。不同于直接预定义机械操作；未完成与失败留空，不用其他案例替代。',sources)


def plot_lineage(rounds, actions):
    plt.figure(figsize=(13, 5))
    plt.axis('off')
    rows = []
    for row in rounds:
        count = sum(action['round_id'] == f"round{row['round']:02d}" and action['output'].get('process') is not None for action in actions)
        rows.append([row['round'], row['status'], row.get('H_parent', 'pending'), row.get('H_retained', 'pending'),
                     row.get('M_parent', 'pending'), row.get('M_retained', 'pending'), count if row['status'] != 'not_started' else 'pending'])
    plt.table(cellText=rows, colLabels=['Round', 'Status', 'H used', 'H retained', 'M used', 'M retained', 'Actual actions'], loc='center', cellLoc='left')
    return figure('HM_lineage.png', 'H与M分别记录实际使用、保留和动作观测次数。不变代码不作为后代，M可执行或被使用不等于能力改善；末轮尚未再执行的M不能声称已发挥作用。', ['metrics/rounds.csv', 'metrics/actions.csv'])


def test_repeat_policy(config):
    plan = ROOT / 'test_repeat_plan.json'
    if plan.exists():
        return {'repeats':read(plan)['repeats'],'source':'test_repeat_plan.json','finalized':True}
    return {'repeats':config['pilot']['final_test']['primary_repeats'],
            'source':'config.json:pilot.final_test.primary_repeats','finalized':False}


def group_statistics(scenes, manifest, state, test_policy):
    groups = []
    keys = list(dict.fromkeys((row['H_version'],row['split']) for row in scenes))
    for version,split in keys:
        rows = [row for row in scenes if row['H_version']==version and row['split']==split]
        repeats = test_policy['repeats'] if split=='test' else 1
        scheduled = len([row for row in manifest if row['split']==split]) * repeats
        if split=='development' and version not in [state.get('H_start'),state.get('H_best')]:
            scheduled = None
        completed = [row for row in rows if row['status'] in TERMINAL]
        passed = [row for row in completed if row.get('valid') is True]
        measured = [row for row in rows if row['evaluation_status']=='completed' and row['BW'] is not None]
        utilities = [row['e2e_BW_utility'] for row in rows if row['e2e_BW_utility'] is not None]
        groups.append({'H_version':version,'split':split,'all_scheduled':scheduled,
            'planned_repeats':repeats,'repeat_plan_source':test_policy['source'] if split=='test' else 'configs/selection_repeats.json' if split=='selection' else 'one generation per requested source/version',
            'repeat_plan_finalized':test_policy['finalized'] if split=='test' else True,
            'records_saved':len(rows),'execution_finished':len(completed),'execution_success':len(passed),
            'execution_success_rate_all_scheduled':len(passed)/scheduled if scheduled and completed else None,
            'BW_measured':len(measured),'evaluation_coverage':len(measured)/scheduled if scheduled and completed else None,
            'BW_conditional_mean':mean(row['BW'] for row in measured),
            'Q_conditional_mean':mean(row['Q'] for row in passed),
            'end_to_end_BW_utility':sum(utilities)/scheduled if scheduled and len(utilities)==scheduled else None,
            'function_measured':sum(row['functional_pass'] is not None for row in rows),
            'function_pass':sum(row['functional_pass'] is True for row in rows),
            'independent_sources_observed':len({row['scene_id'] for row in rows}),
            'note':'Development intermediate-panel denominator not inferred' if scheduled is None
                    else 'Frozen source coverage; Test repetitions from explicit budget-only plan or primary minimum'})
    return groups


def html_table(rows, keys):
    def cell(value):
        return html.escape(str(encode(value)))
    return '<table><tr>' + ''.join('<th>' + html.escape(key) + '</th>' for key in keys) + '</tr>' + ''.join(
        '<tr>' + ''.join('<td>' + cell(row.get(key)) + '</td>' for key in keys) + '</tr>' for row in rows) + '</table>'


def report():
    for name in ('metrics', 'figures', 'reports'):
        (ROOT / name).mkdir(exist_ok=True)
    state = read(ROOT / 'state.json')
    config = read(ROOT / 'config.json')
    manifest = read(ROOT / 'manifest.json') if (ROOT / 'manifest.json').exists() else []
    rounds, scenes, actions, cli, timing = get_rounds(), get_scenes(), get_actions(), get_cli(), get_timings()
    revisions=get_evaluator_revisions()
    inspection_path=ROOT/'preparation/evaluator_A02/inspection_summary.json'
    inspection=read(inspection_path) if inspection_path.exists() else None
    save_csv('evaluator_revision.csv',revisions,list(revisions[0]) if revisions else [
        'scene_id','split','H_version','repeat','old_record_path','current_record_path','old_evaluation_status',
        'old_BW','old_S_rubric','old_S_dimension','old_failure_type','old_audited_failure_class',
        'current_raw_evaluation_status','current_raw_BW','current_result_native_version','current_result_delivery_version',
        'available_native_version','available_delivery_version','current_result_is_current_protocol','new_evaluation_status','new_BW',
        'old_CLI_request_count','new_CLI_request_count','algorithm_gain_comparison'])
    save_csv('rounds.csv', rounds, ['round', 'H_parent', 'M_parent', 'H_candidate', 'M_candidate', 'candidate_type',
        'proposal_returned', 'new_source_candidate', 'M_program_used', 'interrupted_phase', 'platform_snapshot', 'research_packet_version',
        'H_accepted', 'M_accepted', 'H_retained', 'M_retained', 'status', 'selection', 'reason', 'usage'])
    save_csv('scenes.csv', scenes, ['primary_analysis','analysis_scope','excluded_primary_reason','scene_id', 'split', 'H_version', 'M_version', 'repeat', 'status', 'valid',
        'evaluation_status', 'BW', 'S_rubric', 'S_dimension', 'dimensions', 'rubric_results', 'Q', 'PSNR', 'SSIM',
        'LPIPS', 'DINO', 'functional_pass', 'functional_checks', 'e2e_BW_utility', 'model_roles', 'device',
        'seconds', 'generation_seconds', 'evaluation_scope', 'failure_type', 'eligible',
        'record_raw_BW','record_raw_evaluation_status','evaluator_revision_status',
        'bw_judgments', 'loaded_H_modules', 'folder', 'record_path'])
    save_csv('actions.csv', actions, ['round_id', 'action_name', 'creator_M', 'executed_M', 'status',
        'action_revision', 'source_version', 'source_snapshot', 'source_snapshot_available',
        'snapshot_consistent_for_recorded_version', 'action_library_M', 'scene_id',
        'execution_index_for_action_identity', 'reuse', 'expected', 'decision_changed', 'input', 'output', 'source'])
    save_csv('cli_audit.csv', cli, ['session_path', 'role', 'requested_model', 'observed_model', 'reasoning_effort',
        'status', 'exit_code', 'error', 'started', 'finished', 'seconds', 'observable_cli_turns',
        'observable_model_requests_lower_bound', 'exact_model_requests', 'request_visibility_coverage',
        'command_executions', 'file_changes', 'image_reads', 'image_attachment_count', 'visible_subagent_calls',
        'visible_tools', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'cost_usd', 'H_execution_bypass_detected'])
    service_events=service_event_rows()
    save_csv('cli_service_events.csv',service_events,['session_path','role','requested_model','session_status','session_seconds','event_line','event_time','category','message','model_request_count','interpretation'])
    save_csv('timing.csv', timing, ['record_path', 'line_number', 'measurement_type', 'stage', 'scope', 'started', 'finished', 'seconds', 'returncode',
        'timed_out', 'timeout_seconds', 'memory_limit_exceeded', 'memory_limit_bytes', 'cpu_user_seconds',
        'cpu_system_seconds', 'cpu_seconds', 'peak_individual_rss_kib',
        'sampled_peak_tree_rss_kib_lower_bound', 'sample_interval_seconds', 'sampled_process_count', 'rss_scope', 'peak_parent_rss_kib',
        'cache_hit', 'aggregation_note'])
    render_rows,render_summary = get_render_accounting()
    save_csv('render_evidence.csv',render_rows,['scope_path','selected_source_type','selected_sources','recorded_attempts',
        'recorded_completed','ledger_source','ledger_recorded_attempts','ledger_recorded_completed','exact_whole_experiment_count','note'])
    raw_scene_count=len(scenes)
    scenes=[row for row in scenes if row['primary_analysis']]
    test_policy = test_repeat_policy(config)
    paired_sources,paired_points=paired_test_data(scenes,manifest,state,test_policy['repeats'])
    interrupted_attempts=interrupted_generation_rows()
    save_csv('interrupted_generation_attempts.csv',interrupted_attempts,['H_version','split','scene_id','repeat','status','raw_generation_error','generation_seconds','CLI_statuses','scene_blend_exists','final_image_exists','BW','Q','utility','source','interpretation'])
    for point in paired_points:
        for attempt in interrupted_attempts:
            if point['status']=='not_started' and attempt['split']=='test' and all(point[key]==attempt[key] for key in ['scene_id','H_version','repeat']):
                point.update(status='interrupted',attempt_source=attempt['source'])
    save_csv('paired_test_sources.csv',paired_sources,list(paired_sources[0]) if paired_sources else ['scene_id'])
    save_csv('paired_test_generations.csv',paired_points,['scene_id','role','H_version','repeat','status','BW','Q','utility','attempt_source'])
    paired_summary={'statistical_unit':'independent source, not repeat or view',
        'sources_scheduled':len(paired_sources),
        'sources_with_scored_pair':sum(row['paired_successful_generations']>0 for row in paired_sources),
        'matched_successful_generation_pairs':sum(row['paired_successful_generations'] for row in paired_sources),
        'conditional_BW_difference_source_mean':mean(row['BW_paired_difference'] for row in paired_sources),
        'sources_with_complete_utility':sum(row['BW_utility_difference'] is not None for row in paired_sources),
        'all_scheduled_BW_utility_difference_source_mean':mean(row['BW_utility_difference'] for row in paired_sources)
            if paired_sources and all(row['BW_utility_difference'] is not None for row in paired_sources) else None}
    groups = group_statistics(scenes, manifest, state, test_policy)
    save_csv('group_summary.csv', groups, ['H_version','split','all_scheduled','planned_repeats','repeat_plan_source','repeat_plan_finalized','records_saved','execution_finished','execution_success',
        'execution_success_rate_all_scheduled','BW_measured','evaluation_coverage','BW_conditional_mean','Q_conditional_mean',
        'end_to_end_BW_utility','function_measured','function_pass','independent_sources_observed','note'])
    figures = [contact_sheet(manifest, scenes, rounds, state), plot_evolution(rounds), plot_quality(scenes),plot_test_pairs(paired_sources,paired_points),
               plot_dimensions_and_functions(scenes), plot_cost(cli, timing, render_summary), plot_cpu_benchmark(),
               plot_research_chain(actions, scenes, rounds), plot_lineage(rounds, actions),plot_semantic_edits(state,config)]
    shared_case=plot_shared_patch_case(actions,scenes,rounds,manifest)
    if shared_case is not None:figures.append(shared_case)
    finished_rounds = [row for row in rounds if row['status'] in TERMINAL]
    known_usage = [row for row in cli if isinstance(row.get('input_tokens'), int) and isinstance(row.get('output_tokens'), int)]
    test_records = [row for row in scenes if row['split']=='test']
    test_sources = sum(row['split']=='test' for row in manifest)
    expected_test = test_sources * test_policy['repeats'] * len({state['H_start'],state['H_best']}) if state.get('final_selection_frozen') else None
    test_finished = sum(row['status'] in TERMINAL for row in test_records)
    test_status = 'pending' if not test_records else 'all_scheduled_records_terminal' if expected_test is not None and test_finished==expected_test else 'partially_completed'
    summary = {'phase': state['phase'], 'rounds_completed': len(finished_rounds), 'rounds_scheduled': 10,'paired_final_test':paired_summary,
        'interrupted_generation_attempts_without_final_record':len(interrupted_attempts),
        'test_interrupted_without_final_record':sum(row['split']=='test' for row in interrupted_attempts),
        'data_source_counts':dict(Counter(row['split'] for row in manifest)),
        'evaluator_revision':{'paired_record_count':len(revisions),
            'inspection_status':inspection['status'] if inspection is not None else None,
            'inspected_saved_artifact_count':len(inspection['artifacts']) if inspection is not None else None,
            'inspection_new_H_calls':inspection['new_H_calls'] if inspection is not None else None,
            'inspection_new_renders':inspection['new_renders'] if inspection is not None else None,
            'old_evaluation_statuses':dict(Counter(row['old_evaluation_status'] for row in revisions)),
            'old_audited_failure_classes':dict(Counter(row['old_audited_failure_class'] for row in revisions)),
            'old_saved_CLI_request_count':sum(row['old_CLI_request_count'] for row in revisions),
            'new_saved_CLI_request_count':sum(row['new_CLI_request_count'] for row in revisions),
            'new_evaluation_statuses':dict(Counter(row['new_evaluation_status'] for row in revisions)),
            'algorithm_gain_comparison':False},
        'raw_scene_records':raw_scene_count,'superseded_selection_records_excluded_from_primary':raw_scene_count-len(scenes),
        'scene_records': len(scenes), 'scene_status_counts': dict(Counter(row['status'] for row in scenes)),
        'scene_execution_success_count': sum(row.get('valid') is True for row in scenes),
        'scene_execution_success_rate_over_recorded_tasks': sum(row.get('valid') is True for row in scenes) / len(scenes) if scenes else None,
        'scene_all_scheduled_denominator': None, 'all_scheduled_denominator_note': 'No inference from the number of record files; use frozen task schedule',
        'BW_measured_count': sum(isinstance(row['BW'], (int, float)) for row in scenes),
        'BW_measurement_scope':'Current effective evaluator protocol; superseded pre_A02 measurements are retained in evaluator_revision.csv',
        'BW_pre_A02_scored_record_count':sum(isinstance(row['old_BW'],(int,float)) for row in revisions),
        'BW_conditional_means_by_split': {split:mean(row['BW'] for row in scenes if row['split']==split)
                                         for split in ['development','selection','test']},
        'test_completed':test_finished, 'test_status':test_status,
        'test_repeat_policy':test_policy, 'test_scheduled_sources':test_sources,
        'test_planned_comparison_slots':test_sources * test_policy['repeats'] * 2,
        'test_expected_unique_generations':expected_test,
        'test_execution_success_rate_all_scheduled':sum(row.get('valid') is True for row in test_records)/expected_test if expected_test and test_finished else None,
        'timing_measurement_types':dict(Counter(row['measurement_type'] for row in timing)),
        'render_accounting':render_summary,
        'cli_sessions': len(cli), 'cli_by_role': dict(Counter(row.get('role', 'unknown') for row in cli)),
        'known_input_tokens': sum(row['input_tokens'] for row in known_usage),
        'known_output_tokens': sum(row['output_tokens'] for row in known_usage),
        'usage_coverage_sessions': len(known_usage), 'usage_total_sessions': len(cli),
        'cost_usd': None, 'actual_model_request_count': None,
        'actual_M_descendant_count': len({row['M_candidate'] for row in rounds if row.get('M_accepted') and row.get('M_candidate')}),
        'action_observations': len(actions), 'meta_capability_improvement': 'not established by H trajectory',
        'group_summary': groups, 'figures': figures}
    (ROOT / 'metrics/summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    status_text = (f"本轮状态：{state['phase']}；正式研发完成 {len(finished_rounds)}/10 轮。"
        f"保存了 {len(scenes)} 条正式场景记录、当前有效评价协议 {summary['BW_measured_count']} 次BW测量；修订前已测BW记录 {summary['BW_pre_A02_scored_record_count']} 条另行保留。终测 {summary['test_status']}（已完成记录 {test_finished}）。"
        f"另有 {summary['test_interrupted_without_final_record']} 个已开始但未写入最终任务记录的终测中断，不作not_started。"
        f"实际CLI会话 {len(cli)} 次（包括准备阶段），usage可见 {len(known_usage)}/{len(cli)}。")
    data_sizes_text='当前manifest来源数：'+ '、'.join(f'{name}={count}' for name,count in summary['data_source_counts'].items())+'；Selection绝对覆盖按实际冻结配置，不沿用旧4图口径。'
    revision_text=(f"A02评价器修订保留{len(revisions)}条前后记录；旧状态{summary['evaluator_revision']['old_evaluation_statuses']}，"
        f"旧原因核对{summary['evaluator_revision']['old_audited_failure_classes']}；新状态{summary['evaluator_revision']['new_evaluation_statuses']}。"
        '旧评分与失败、实际judge会话完整保留于evaluator_revision.csv及before_A02原件；新协议缺测保持pending/null。'
        '旧12张dev BW不供正式M，最终端点才统一重评；这些变化属于评价证据修复，不是H算法改进。')
    test_plan_text = (f"终测每来源每端点计划 {test_policy['repeats']} 次生成；依据 {test_policy['source']}，"
        + ('预算分支已冻结。' if test_policy['finalized'] else '当前为最低保证次数，尚未作最终预算分支决定。')
        + ' H_best与H_start相同时复用同一版本的真实产物，不增加独立生成数。')
    render_note = (f"主根渲染预算扣额 render_budget_charged={render_summary['render_budget_charged']}，主根+独立回放根联合扣额={render_summary['combined_render_budget_charged']}，分别读取两根render_attempts.jsonl且不重复相加；"
        'functional()一次保守预扣3帧，N/A时实际可能更少，因此不将原render_attempts字段解释为精确帧数。'
        '实际全局尝试数和完成数保持unknown/null。render_evidence.csv逐目录选择一种记录来源，避免stage事件、逐视角metadata与ledger重复相加。'
        + (' 早期CPU基准6次命令（3次成功、3次初始导入失败）已在冻结前补扣，原补扣证据保留。' if render_summary['CPU_benchmark_budget_correction'] is not None else ''))
    limits_text = ('所有结果均为 BW-style / CLI-adapted，不是官方榜单分数。开发历史图已暴露；同模型研发与评审存在偏差。'
        '未完成项保留pending/null；没有真实冻结元回放时不宣称元能力改善。进程树RSS为0.1秒采样下界；'
        '嵌套阶段墙钟和CPU作用域有重叠，不相加冒充总耗时。')
    paired_text=(f"独立来源配对：{paired_summary['sources_with_scored_pair']}/{paired_summary['sources_scheduled']} 来源有双方成功且实测的生成对，"
        f"合计 {paired_summary['matched_successful_generation_pairs']} 对生成；来源等权条件BW差 {show(paired_summary['conditional_BW_difference_source_mean'])}。"
        f"全预定来源的端到端BW效用差 {show(paired_summary['all_scheduled_BW_utility_difference_source_mean'])}，"
        f"完整效用覆盖 {paired_summary['sources_with_complete_utility']}/{paired_summary['sources_scheduled']}；缺失评价和pending不当零。")
    markdown = ['# Scene-RSI V3 中文实验报告', '', status_text, '', data_sizes_text,'',test_plan_text, '',paired_text,'', render_note, '', limits_text, '',
        revision_text,'','[评价修订逐记录表](../metrics/evaluator_revision.csv) · [A02协议修订](../PROTOCOL_AMENDMENT_02.md) · [A03灯光证据与操作员中断记录](../PROTOCOL_AMENDMENT_03.md) · [A04无损证据编码修复](../PROTOCOL_AMENDMENT_04.md) · [A05网络恢复与冻结续跑](../PROTOCOL_AMENDMENT_05.md)','',
        '请求模型与可确认路由分开见 cli_audit.csv；没有路由元数据时 observed_model=unknown。费用未知，不宣称降本。', '',
        '## 十轮实际状态', '', '| round | status | H retained | M retained | type |', '|---|---|---|---|---|']
    if (ROOT/'PROTOCOL_AMENDMENT_01.md').exists():
        markdown[1:1]=['','[A01实际平台修订](../PROTOCOL_AMENDMENT_01.md)：公开附件已统一转发，原偏离文档保留为历史；M0未变，修订在首个BW正式任务和首轮正式M前完成，10个已生成H产物按相同信息条件复用。','']
    for row in rounds:
        markdown.append(f"| {row['round']} | {row['status']} | {row.get('H_retained', 'null')} | {row.get('M_retained', 'null')} | {row.get('candidate_type', 'null')} |")
    for item in figures:
        markdown += ['', '![真实实验图](../' + item['path'] + ')', '', item['caption'], '',
                     '来源：' + '、'.join('[' + name + '](../' + name + ')' for name in item['sources']) + '；生成脚本：[analyze.py](../analyze.py)。']
    markdown += ['', '## 重画命令', '', '```bash', f"{config.get('python_executable', '__SCENEEVOLVE_REPRO__/work/.venv/bin/python')} {ROOT / 'analyze.py'} report", '```', '',
                 '本命令只读取保存的记录、图片和配置，不运行模型或Blender。续跑入口由主runner提供，不由报告触发。']
    (ROOT / 'reports/REPORT_ZH.md').write_text('\n'.join(markdown) + '\n')
    body = '<!doctype html><html lang="zh"><meta charset="utf-8"><title>Scene-RSI V3</title><style>body{font:16px/1.6 sans-serif;max-width:1400px;margin:24px auto;padding:0 20px;color:#17202a}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border:1px solid #ccd;padding:6px;vertical-align:top;word-break:break-word}figure{margin:25px 0}code{background:#f4f5f6}a{color:#125d98}</style><h1>Scene-RSI V3 实际运行报告</h1>'
    body += '<p>' + html.escape(status_text) + '</p><p>' + html.escape(test_plan_text) + '</p><p>'+html.escape(paired_text)+'</p><p>' + html.escape(render_note) + '</p><p>' + html.escape(limits_text) + '</p>'
    body += '<p>'+html.escape(data_sizes_text)+'</p><p>'+html.escape(revision_text)+'</p><p><a href="../metrics/evaluator_revision.csv">评价器修订逐记录表</a> · <a href="../PROTOCOL_AMENDMENT_02.md">A02协议修订</a> · <a href="../PROTOCOL_AMENDMENT_03.md">A03修订</a> · <a href="../PROTOCOL_AMENDMENT_04.md">A04无损证据编码修复</a> · <a href="../PROTOCOL_AMENDMENT_05.md">A05网络恢复续跑</a></p>'
    body += '<p><a href="REPORT_ZH.md">中文Markdown</a> · <a href="../metrics/summary.json">原始汇总JSON</a> · <a href="../analyze.py">离线重画脚本</a> · <a href="../manifest.json">来源与暴露记录</a></p>'
    if (ROOT/'PROTOCOL_AMENDMENT_01.md').exists():
        body += '<p><a href="../PROTOCOL_AMENDMENT_01.md">A01实际平台修订</a>：公开附件已统一转发；旧偏离文档保留为历史。M0未变，修订在首个BW正式任务和首轮正式M前完成，10个H生成产物按相同信息条件复用。</p>'
    body += '<h2>十轮状态</h2>' + html_table(rounds, ['round', 'status', 'H_parent', 'M_parent', 'candidate_type', 'H_retained', 'M_retained', 'H_accepted', 'M_accepted'])
    for item in figures:
        body += '<figure><img src="../' + item['path'] + '"><figcaption>' + html.escape(item['caption']) + '<br>来源：'
        body += ' · '.join('<a href="../' + name + '">' + html.escape(name) + '</a>' for name in item['sources'])
        body += ' · <a href="../analyze.py">生成脚本</a></figcaption></figure>'
    body += '<h2>原始证据</h2><ul>' + ''.join('<li><a href="../metrics/' + name + '.csv">' + name + '.csv</a></li>' for name in ['rounds', 'scenes', 'actions', 'cli_audit', 'timing', 'group_summary', 'render_evidence','evaluator_revision','cli_service_events','paired_test_sources','semantic_edit_summary','interrupted_generation_attempts']) + '</ul>'
    body += '<p>没有实际记录的诊断链、元回放和结构收益保持未验证；报告不会以概念图或其他场景代替缺失结果。</p></html>'
    (ROOT / 'reports/index.html').write_text(body)
    print(json.dumps({key: value for key, value in summary.items() if key != 'figures'}, ensure_ascii=False, indent=2))


def main():
    report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['report'], nargs='?', default='report')
    parser.parse_args()
    report()
