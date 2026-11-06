"""Offline V3 tables and figures from saved records; never executes a model or Blender."""
import argparse
from collections import Counter
import csv
import html
import json
from pathlib import Path
import statistics
import os

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
    records = {record['round']: record for path in sorted((ROOT / 'rounds').glob('*/record.json'))
               for record in [read(path)]} if (ROOT / 'rounds').exists() else {}
    return [{**{'round': number, 'status': 'not_started'}, **records.get(number, {})}
            for number in range(1, 11)]


def get_scenes():
    records = []
    for path in sorted((ROOT / 'results').rglob('record.json')):
        row = read(path)
        if 'scene_id' not in row:
            continue
        metrics = row.get('metrics') or {}
        bw = row.get('bw') or {}
        functional = row.get('functional') or {}
        records.append({**row, 'record_path': relative(path),
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
    for path in sorted((ROOT / 'meta_traces').glob('round*/actions/*/observation.json')):
        observation = read(path)
        request_path = path.with_name('action_request.json')
        request = read(request_path) if request_path.exists() else {}
        name = request.get('name', request.get('action', observation.get('action', path.parent.name)))
        if isinstance(name, dict):
            name = name.get('name', 'unknown')
        records.append({'round_id': path.parents[2].name, 'action_name': name,
            'creator_M': request.get('creator_M', observation.get('creator_M')),
            'source_version': request.get('source_version'),
            'executed_M': request.get('M_version', observation.get('M')),
            'status': observation.get('status', 'observation_saved'),
            'input': request, 'output': observation,
            'expected': request.get('expected', observation.get('expectation')), 'decision_changed': observation.get('decision_changed'),
            'source': relative(path)})
    seen = Counter()
    for row in records:
        # A repeated name is insufficient if action source/version provenance was not saved.
        identity = (row['action_name'], row['creator_M'], row['source_version'])
        if row['source_version'] is not None and row['output'].get('process') is not None:
            seen[identity] += 1
            row['execution_index_for_action_identity'] = seen[identity]
            row['reuse'] = seen[identity] > 1
        else:
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
        records.append({**data, 'record_path': relative(path),
            'stage': path.stem.removesuffix('_process'),
            'scope': data.get('cpu_scope', 'unknown'),
            'cpu_seconds': (data['cpu_user_seconds'] + data['cpu_system_seconds'])
                           if all(isinstance(data.get(key), (int, float)) for key in
                                  ('cpu_user_seconds', 'cpu_system_seconds')) else None})
    for path in sorted(ROOT.rglob('process.json')):
        if any(row['record_path'] == relative(path) for row in records):
            continue
        data = read(path)
        if 'seconds' in data and 'command' in data:
            records.append({**data, 'record_path': relative(path), 'stage': 'CLI_or_benchmark',
                            'scope': data.get('cpu_scope', 'unknown'),
                            'cpu_seconds': data['cpu_user_seconds'] + data['cpu_system_seconds']
                              if all(isinstance(data.get(key), (int, float)) for key in
                                     ('cpu_user_seconds', 'cpu_system_seconds')) else None})
    return records


def figure(name, caption, sources):
    path = ROOT / 'figures' / name
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return {'path': relative(path), 'caption': caption, 'sources': sources, 'script': 'analyze.py'}


def plot_evolution(rounds):
    plt.figure(figsize=(10, 4))
    base_path = ROOT / 'round0.json'
    baseline = read(base_path)['selection']['S_BW'] if base_path.exists() else None
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
    return figure('evolution.png','蓝线为实际保留H的验证评分，圆点为接受候选、叉号为未接受候选；不对未运行轮次填零。连续轨迹不是十次独立重复。', ['metrics/rounds.csv'] + (['round0.json'] if base_path.exists() else []))


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
    return figure('quality_points.png', '各划分所有实际测得的逐生成 BW 点；开发 preview 与正式 Selection/Test 分开。缺测和未开始不显示零分。统计单位为生成产物，独立场景数另见CSV。', ['metrics/scenes.csv'])


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
    return figure('dimensions_and_function.png', '逐产物八维原始评分与功能测量计数；未测不算失败，也不算通过。required/applicable/measured_pass/gate_pass原始对象完整保留于CSV。机械编辑不等于文字编辑能力。', ['metrics/scenes.csv'])


def plot_cost(cli, timing):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    roles = Counter(row.get('role', 'unknown') for row in cli)
    axes[0].bar(list(roles), list(roles.values())); axes[0].set_title(f'Actual CLI sessions: {len(cli)}')
    values = [row['seconds'] for row in timing if isinstance(row.get('seconds'), (int, float))]
    if values:
        axes[1].scatter(range(1, len(values) + 1), values, s=18)
    else:
        axes[1].text(.5, .5, 'pending', transform=axes[1].transAxes, ha='center')
    axes[1].set_title('Observed process duration'); axes[1].set_ylabel('wall seconds (overlapping scopes not summed)')
    token_rows = [row for row in cli if isinstance(row.get('input_tokens'), int) and isinstance(row.get('output_tokens'), int)]
    axes[2].bar(['input', 'output'], [sum(row[key] for row in token_rows) for key in ('input_tokens', 'output_tokens')])
    axes[2].set_title(f'Visible tokens; coverage {len(token_rows)}/{len(cli)} sessions')
    return figure('cost_and_timing.png', '实际会话、进程墙钟原始点和可见token总量。CPU秒、峰值RSS边界与错误位置见timing.csv；嵌套计时作用域不能简单相加。费用不可见时保持unknown。', ['metrics/cli_audit.csv', 'metrics/timing.csv'])


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
        scene = next((row for row in scenes if row['scene_id'] == observation['scene_id'] and row['split'] == 'development'), None)
        paths = [Path(scene['folder']) / 'final.png' if scene else None,
                 Path(observation['render']) if observation.get('render') else None]
        for axis, path, title in zip(axes[:2], paths, ['Current reconstruction', 'Actual action output']):
            if path is not None and path.exists():
                with Image.open(path) as image:
                    axis.imshow(image.convert('RGB'))
            else:
                axis.text(.5, .5, 'No rendered output', ha='center')
            axis.set_title(title)
        detail = 'Action: ' + str(action['action_name']) + '\nExpected: ' + json.dumps(action['expected'], ensure_ascii=True)[:300]
        detail += '\nObserved: ' + json.dumps(observation.get('measurement'), ensure_ascii=True)[:900]
        detail += '\nActual decision linkage: see decisions.json and candidate H.diff.'
        import textwrap
        axes[2].text(0, 1, '\n'.join(textwrap.wrap(detail, 58)), va='top', fontsize=8)
        sources = ['metrics/actions.csv', action['source'], 'metrics/rounds.csv']
    else:
        axes[1].text(.5, .5, 'No completed formal research action yet.\nResearch chain pending.', ha='center')
        sources = ['metrics/actions.csv', 'metrics/rounds.csv']
    return figure('research_chain.png', '按时间选择第一条完成的正式研究动作，无论成功或失败；图像和观测均来自该动作。动作执行本身不证明原因唯一或H改善，后续决策、diff和迁移结果需合并审查。', sources)


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


def group_statistics(scenes, manifest, state):
    groups = []
    keys = list(dict.fromkeys((row['H_version'], row['split']) for row in scenes))
    for version, split in keys:
        rows = [row for row in scenes if row['H_version'] == version and row['split'] == split]
        scheduled = len([row for row in manifest if row['split'] == split]) * (2 if split == 'test' else 1)
        if split == 'development' and version not in [state.get('H_start'), state.get('H_best')]:
            scheduled = None  # Intermediate-H development panels are adaptive, not full-12 scheduled.
        completed = [row for row in rows if row['status'] in TERMINAL]
        passed = [row for row in completed if row.get('valid') is True]
        measured = [row for row in rows if row['evaluation_status'] == 'completed' and row['BW'] is not None]
        utilities = [row['e2e_BW_utility'] for row in rows if row['e2e_BW_utility'] is not None]
        groups.append({'H_version':version, 'split':split, 'all_scheduled':scheduled,
            'records_saved':len(rows), 'execution_finished':len(completed), 'execution_success':len(passed),
            'execution_success_rate_all_scheduled':len(passed)/scheduled if scheduled and completed else None,
            'BW_measured':len(measured), 'evaluation_coverage':len(measured)/scheduled if scheduled else None,
            'BW_conditional_mean':mean(row['BW'] for row in measured),
            'Q_conditional_mean':mean(row['Q'] for row in passed),
            'end_to_end_BW_utility':sum(utilities)/scheduled if scheduled and len(utilities)==scheduled else None,
            'function_measured':sum(row['functional_pass'] is not None for row in rows),
            'function_pass':sum(row['functional_pass'] is True for row in rows),
            'independent_sources_observed':len({row['scene_id'] for row in rows}),
            'note':'Development intermediate-panel denominator not inferred' if scheduled is None else 'Frozen manifest coverage, Test two generation repeats per source'})
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
    save_csv('rounds.csv', rounds, ['round', 'H_parent', 'M_parent', 'H_candidate', 'M_candidate', 'candidate_type',
        'H_accepted', 'M_accepted', 'H_retained', 'M_retained', 'status', 'selection', 'reason', 'usage'])
    save_csv('scenes.csv', scenes, ['scene_id', 'split', 'H_version', 'M_version', 'repeat', 'status', 'valid',
        'evaluation_status', 'BW', 'S_rubric', 'S_dimension', 'dimensions', 'rubric_results', 'Q', 'PSNR', 'SSIM',
        'LPIPS', 'DINO', 'functional_pass', 'functional_checks', 'e2e_BW_utility', 'model_roles', 'device',
        'seconds', 'folder', 'record_path'])
    save_csv('actions.csv', actions, ['round_id', 'action_name', 'creator_M', 'executed_M', 'status',
        'source_version', 'execution_index_for_action_identity', 'reuse', 'expected', 'decision_changed', 'input', 'output', 'source'])
    save_csv('cli_audit.csv', cli, ['session_path', 'role', 'requested_model', 'observed_model', 'reasoning_effort',
        'status', 'exit_code', 'error', 'started', 'finished', 'seconds', 'observable_cli_turns',
        'observable_model_requests_lower_bound', 'exact_model_requests', 'request_visibility_coverage',
        'command_executions', 'file_changes', 'image_reads', 'image_attachment_count', 'visible_subagent_calls',
        'visible_tools', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'cost_usd', 'H_execution_bypass_detected'])
    save_csv('timing.csv', timing, ['record_path', 'stage', 'scope', 'started', 'finished', 'seconds', 'returncode',
        'timed_out', 'timeout_seconds', 'memory_limit_exceeded', 'memory_limit_bytes', 'cpu_user_seconds',
        'cpu_system_seconds', 'cpu_seconds', 'peak_individual_rss_kib',
        'sampled_peak_tree_rss_kib_lower_bound', 'sample_interval_seconds', 'sampled_process_count', 'rss_scope'])
    groups = group_statistics(scenes, manifest, state)
    save_csv('group_summary.csv', groups, ['H_version','split','all_scheduled','records_saved','execution_finished','execution_success',
        'execution_success_rate_all_scheduled','BW_measured','evaluation_coverage','BW_conditional_mean','Q_conditional_mean',
        'end_to_end_BW_utility','function_measured','function_pass','independent_sources_observed','note'])
    figures = [contact_sheet(manifest, scenes, rounds, state), plot_evolution(rounds), plot_quality(scenes),
               plot_dimensions_and_functions(scenes), plot_cost(cli, timing), plot_cpu_benchmark(),
               plot_research_chain(actions, scenes, rounds), plot_lineage(rounds, actions)]
    finished_rounds = [row for row in rounds if row['status'] in TERMINAL]
    known_usage = [row for row in cli if isinstance(row.get('input_tokens'), int) and isinstance(row.get('output_tokens'), int)]
    summary = {'phase': state['phase'], 'rounds_completed': len(finished_rounds), 'rounds_scheduled': 10,
        'scene_records': len(scenes), 'scene_status_counts': dict(Counter(row['status'] for row in scenes)),
        'scene_execution_success_count': sum(row.get('valid') is True for row in scenes),
        'scene_execution_success_rate_over_recorded_tasks': sum(row.get('valid') is True for row in scenes) / len(scenes) if scenes else None,
        'scene_all_scheduled_denominator': None, 'all_scheduled_denominator_note': 'No inference from the number of record files; use frozen task schedule',
        'BW_measured_count': sum(isinstance(row['BW'], (int, float)) for row in scenes),
        'BW_conditional_means_by_split': {split:mean(row['BW'] for row in scenes if row['split']==split)
                                         for split in ['development','selection','test']},
        'test_completed': sum(row['split'] == 'test' and row['status'] in TERMINAL for row in scenes),
        'test_status': 'completed_records_available' if any(row['split'] == 'test' and row['status'] in TERMINAL for row in scenes) else 'pending',
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
        f"保存了 {len(scenes)} 条正式场景记录、{summary['BW_measured_count']} 次BW测量；终测 {summary['test_status']}。"
        f"实际CLI会话 {len(cli)} 次（包括准备阶段），usage可见 {len(known_usage)}/{len(cli)}。")
    limits_text = ('所有结果均为 BW-style / CLI-adapted，不是官方榜单分数。开发历史图已暴露；同模型研发与评审存在偏差。'
        '未完成项保留pending/null；没有真实冻结元回放时不宣称元能力改善。进程树RSS为0.1秒采样下界；'
        '嵌套阶段墙钟和CPU作用域有重叠，不相加冒充总耗时。')
    markdown = ['# Scene-RSI V3 中文实验报告', '', status_text, '', limits_text, '',
        '请求模型与可确认路由分开见 cli_audit.csv；没有路由元数据时 observed_model=unknown。费用未知，不宣称降本。', '',
        '## 十轮实际状态', '', '| round | status | H retained | M retained | type |', '|---|---|---|---|---|']
    for row in rounds:
        markdown.append(f"| {row['round']} | {row['status']} | {row.get('H_retained', 'null')} | {row.get('M_retained', 'null')} | {row.get('candidate_type', 'null')} |")
    for item in figures:
        markdown += ['', '![真实实验图](../' + item['path'] + ')', '', item['caption'], '',
                     '来源：' + '、'.join('[' + name + '](../' + name + ')' for name in item['sources']) + '；生成脚本：[analyze.py](../analyze.py)。']
    markdown += ['', '## 重画命令', '', '```bash', f"{config.get('python_executable', '__SCENEEVOLVE_REPRO__/work/.venv/bin/python')} {ROOT / 'analyze.py'} report", '```', '',
                 '本命令只读取保存的记录、图片和配置，不运行模型或Blender。续跑入口由主runner提供，不由报告触发。']
    (ROOT / 'reports/REPORT_ZH.md').write_text('\n'.join(markdown) + '\n')
    body = '<!doctype html><html lang="zh"><meta charset="utf-8"><title>Scene-RSI V3</title><style>body{font:16px/1.6 sans-serif;max-width:1400px;margin:24px auto;padding:0 20px;color:#17202a}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border:1px solid #ccd;padding:6px;vertical-align:top;word-break:break-word}figure{margin:25px 0}code{background:#f4f5f6}a{color:#125d98}</style><h1>Scene-RSI V3 实际运行报告</h1>'
    body += '<p>' + html.escape(status_text) + '</p><p>' + html.escape(limits_text) + '</p>'
    body += '<p><a href="REPORT_ZH.md">中文Markdown</a> · <a href="../metrics/summary.json">原始汇总JSON</a> · <a href="../analyze.py">离线重画脚本</a> · <a href="../manifest.json">来源与暴露记录</a></p>'
    body += '<h2>十轮状态</h2>' + html_table(rounds, ['round', 'status', 'H_parent', 'M_parent', 'candidate_type', 'H_retained', 'M_retained', 'H_accepted', 'M_accepted'])
    for item in figures:
        body += '<figure><img src="../' + item['path'] + '"><figcaption>' + html.escape(item['caption']) + '<br>来源：'
        body += ' · '.join('<a href="../' + name + '">' + html.escape(name) + '</a>' for name in item['sources'])
        body += ' · <a href="../analyze.py">生成脚本</a></figcaption></figure>'
    body += '<h2>原始证据</h2><ul>' + ''.join('<li><a href="../metrics/' + name + '.csv">' + name + '.csv</a></li>' for name in ['rounds', 'scenes', 'actions', 'cli_audit', 'timing', 'group_summary']) + '</ul>'
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
