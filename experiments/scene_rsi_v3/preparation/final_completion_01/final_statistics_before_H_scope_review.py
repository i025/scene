"""Source-level final statistics and contact sheets from saved V3 records only."""
import argparse
from collections import Counter
import csv
import json
import os
from pathlib import Path
import statistics

for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS']:
    os.environ[key] = '1'
os.environ['MPLCONFIGDIR'] = '/tmp/scene_rsi_v3_matplotlib'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
DIMENSIONS = ['scene_fidelity', 'physics', 'style_color', 'realism', 'layout_spatial',
              'proportion_scale', 'lighting_material', 'completeness']
QUALITY = ['BW', 'S_rubric', 'S_dimension', 'Q', 'PSNR', 'SSIM', 'LPIPS', 'DINO', *DIMENSIONS]


def read(path):
    return json.loads(path.read_text())


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def save_csv(name, rows):
    with (ROOT / 'metrics' / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]));writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list))
                         else v for k, v in row.items()} for row in rows)


def bootstrap(values):
    """Resample six independent source summaries, never views or repetitions."""
    valid = [v for v in values if v is not None]
    if len(valid) != 6:
        return {'sources': len(valid), 'mean': mean(valid), 'ci95': None,
                'reason': 'Interval withheld until all six sources have this measurement'}
    data = np.asarray(valid, dtype=float)
    rng = np.random.default_rng(20261111)
    draws = data[rng.integers(0, 6, size=(10000, 6))].mean(axis=1)
    return {'sources': 6, 'mean': float(data.mean()),
            'source_standard_deviation': float(data.std(ddof=1)),
            'ci95': [float(v) for v in np.quantile(draws, [.025, .975])],
            'method': '10000 percentile bootstrap draws over source summaries; seed 20261111; exploratory with n=6'}


def collect():
    frozen = read(ROOT / 'final_selection_freeze.json')
    versions = ['historical_r1_C2_start', frozen['H_best']]
    scenes = [s for s in read(ROOT / 'manifest.json') if s['split'] == 'test']
    repeats = read(ROOT / 'test_repeat_plan.json')['repeats']
    if len(scenes) != 6 or repeats != 2:
        raise ValueError('This report describes the existing 6-source, 24-slot frozen plan')
    rows = []
    for scene in scenes:
        for version in versions:
            for repeat in [1, 2]:
                folder = ROOT / 'results' / version / 'test' / scene['scene_id'] / str(repeat)
                path = folder / 'record.json'
                record = read(path) if path.exists() else None
                bw = record['bw'] if record else {}
                metrics = record['metrics'] if record else {}
                measured = bw.get('evaluation_status') == 'completed'
                dimensions = {x['id']: x['score'] for x in bw.get('dimension_scores', [])} if measured else {}
                valid = record['valid'] if record else None
                status = record['status'] if record else 'interrupted' if list(folder.glob('student_calls/*/request.json')) else 'not_started'
                row = {'scene_id': scene['scene_id'], 'source_id': scene['source_id'],
                       'H_version': version, 'repeat': repeat, 'split': 'test',
                       'generation_status': status, 'generation_success': valid,
                       'evaluation_status': bw.get('evaluation_status', 'not_started'),
                       'failure_type': record['failure_type'] if record else None,
                       'evaluation_failure_type': bw.get('failure_type'),
                       'BW': bw.get('S_BW') if measured else None,
                       'S_rubric': bw.get('S_rubric') if measured else None,
                       'S_dimension': bw.get('S_dimension') if measured else None,
                       **{target: metrics.get(key) for target, key in [('Q', 'overall'), ('PSNR', 'psnr'),
                          ('SSIM', 'ssim'), ('LPIPS', 'lpips'), ('DINO', 'dino')]},
                       **{key: dimensions.get(key) for key in DIMENSIONS},
                       'function_gate_pass': record['functional']['functional_pass'] if record else None,
                       'function_checks': record['functional']['checks'] if record else None,
                       'BW_utility': bw['S_BW'] if measured else 0 if valid is False else None,
                       'device': record['device'] if record else None,
                       'threads': record['threads'] if record else None,
                       'generation_seconds': record['generation_seconds'] if record else None,
                       'H_CLI_sessions': len(list(folder.glob('student_calls/*/request.json'))),
                       'judge_CLI_sessions': len(list(folder.glob('judge_A03_*/request.json'))),
                       'record_path': str(path.relative_to(ROOT)), 'folder': str(folder.relative_to(ROOT))}
                rows.append(row)
    return scenes, versions, rows


def aggregate(scenes, versions, rows):
    sources = []
    for scene in scenes:
        sid = scene['scene_id']
        groups = {v: [r for r in rows if r['scene_id'] == sid and r['H_version'] == v] for v in versions}
        source = {'scene_id': sid, 'source_id': scene['source_id']}
        for label, version in zip(['start', 'H04'], versions):
            items = groups[version]
            source[label + '_generation_success'] = sum(r['generation_success'] is True for r in items)
            source[label + '_BW_measured'] = sum(r['BW'] is not None for r in items)
            source[label + '_BW_repeat_sd'] = statistics.stdev([r['BW'] for r in items]) if all(r['BW'] is not None for r in items) else None
            source[label + '_BW_utility'] = mean(r['BW_utility'] for r in items) if all(r['BW_utility'] is not None for r in items) else None
            for key in QUALITY:source[label + '_' + key] = mean(r[key] for r in items)
        paired = [(a, b) for a, b in zip(groups[versions[0]], groups[versions[1]])
                  if a['repeat'] == b['repeat'] and a['generation_success'] and b['generation_success']]
        source['successful_generation_pairs'] = len(paired)
        source['BW_measured_pairs'] = sum(a['BW'] is not None and b['BW'] is not None for a, b in paired)
        for key in QUALITY:
            source[key + '_paired_difference'] = mean(b[key] - a[key] for a, b in paired if a[key] is not None and b[key] is not None)
        source['BW_utility_difference'] = source['H04_BW_utility'] - source['start_BW_utility'] if source['H04_BW_utility'] is not None and source['start_BW_utility'] is not None else None
        sources.append(source)
    endpoints = []
    for label, version in zip(['start', 'H04'], versions):
        items = [r for r in rows if r['H_version'] == version]
        finished = [r for r in items if r['generation_success'] is not None]
        endpoint = {'H_version': version, 'scheduled': 12, 'records_finished': len(finished),
                    'execution_success': sum(r['generation_success'] is True for r in items),
                    'execution_success_rate_all_scheduled': sum(r['generation_success'] is True for r in items) / 12 if finished else None,
                    'BW_measured': sum(r['BW'] is not None for r in items),
                    'required_function_gate_pass': sum(r['function_gate_pass'] is True for r in items),
                    'required_function_rate_all_scheduled': sum(r['function_gate_pass'] is True for r in items) / 12 if len(finished) == 12 else None,
                    'required_function_rate_conditioned_on_generation_success': mean(int(r['function_gate_pass']) for r in items if r['generation_success']),
                    'model_or_generation_failure_types': dict(Counter(r['failure_type'] for r in items if r['generation_success'] is False)),
                    'evaluation_failure_types': dict(Counter(r['evaluation_failure_type'] for r in items if r['evaluation_status'] == 'eval_failed')),
                    'BW_utility_all_scheduled': mean(s[label + '_BW_utility'] for s in sources) if all(s[label + '_BW_utility'] is not None for s in sources) else None}
        for key in QUALITY:
            endpoint[key + '_source_equal_conditional_mean'] = mean(s[label + '_' + key] for s in sources)
            endpoint[key + '_completed_task_conditional_mean'] = mean(r[key] for r in items)
            endpoint[key + '_sources_measured'] = sum(s[label + '_' + key] is not None for s in sources)
        endpoints.append(endpoint)
    differences = {key: bootstrap([s[key + '_paired_difference'] for s in sources]) for key in QUALITY}
    differences['BW_utility'] = bootstrap([s['BW_utility_difference'] for s in sources])
    return sources, endpoints, differences


def contact_sheet(scenes, versions, rows, target, *, include_references):
    width, height = 330, 285
    image = Image.new('RGB', (5 * width, 55 + len(scenes) * height), 'white')
    draw = ImageDraw.Draw(image)
    for x, label in enumerate(['Reference', 'H_start / repeat 1', 'H04 / repeat 1', 'H_start / repeat 2', 'H04 / repeat 2']):
        draw.text((x * width + 12, 12), label, fill='black')
    for index, scene in enumerate(scenes):
        top = 55 + index * height
        if include_references:
            with Image.open(scene['image_path']) as ref:
                ref = ImageOps.contain(ref.convert('RGB'), (width - 12, height - 50));image.paste(ref, (6, top))
        else:
            draw.multiline_text((10, top + 55), 'REFERENCE WITHHELD\nRedistribution permission unknown.\nAvailable on original server.\nNot an experimental output.', fill='#555555', spacing=6)
        draw.text((10, top + height - 35), scene['scene_id'], fill='black')
        for column, (repeat, version) in enumerate([(1, versions[0]), (1, versions[1]), (2, versions[0]), (2, versions[1])], 1):
            row = next(r for r in rows if r['scene_id'] == scene['scene_id'] and r['H_version'] == version and r['repeat'] == repeat)
            path = ROOT / row['folder'] / 'final.png'
            if row['generation_success'] is True and path.exists():
                with Image.open(path) as render:
                    render = ImageOps.contain(render.convert('RGB'), (width - 12, height - 50));image.paste(render, (column * width + 6, top))
            else:
                draw.text((column * width + 10, top + 65), row['generation_status'], fill='#990000')
                draw.text((column * width + 10, top + 85), str(row['failure_type'] or ''), fill='#990000')
            draw.text((column * width + 10, top + height - 35), f"{scene['scene_id']}  BW={row['BW']}", fill='black')
            draw.text((column * width + 10, top + height - 19), 'Q=' + str(round(row['Q'], 4) if row['Q'] is not None else None) + '  ' + row['evaluation_status'], fill='black')
    target.parent.mkdir(parents=True, exist_ok=True);image.save(target)


def report(private_output=None):
    scenes, versions, rows = collect()
    sources, endpoints, differences = aggregate(scenes, versions, rows)
    from analyze import get_cli, get_timings, get_render_accounting
    cli, timing = get_cli(), get_timings()
    config = read(ROOT / 'config.json')
    role_costs = []
    for role in ['H', 'M', 'judge', 'preparation']:
        sessions = [s for s in cli if s['role'] == role]
        role_costs.append({'role': role, 'CLI_sessions': len(sessions),
                           'statuses': dict(Counter(s['status'] for s in sessions)),
                           'CLI_wall_seconds': sum(s['seconds'] for s in sessions if isinstance(s.get('seconds'), (int, float))),
                           'known_input_tokens': sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'), int)),
                           'known_output_tokens': sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'), int)),
                           'usage_known_sessions': sum(isinstance(s.get('input_tokens'), int) for s in sessions),
                           'observable_turns': sum(s['observable_cli_turns'] for s in sessions if isinstance(s.get('observable_cli_turns'), int)),
                           'visible_tool_calls': sum(s['visible_tools'] for s in sessions if isinstance(s.get('visible_tools'), int)),
                           'exact_model_requests': None, 'cost_usd': None})
    leaf = [t for t in timing if t['measurement_type'] == 'process_tree'
            and t['command'][0] in [config['blender']['executable'], config['model']['command']]]
    blender = [t for t in leaf if t['command'][0] == config['blender']['executable']]
    slow = sorted(leaf, key=lambda t: t['seconds'], reverse=True)[:12]
    save_csv('final_cost_by_role.csv', role_costs)
    if slow:save_csv('final_slowest_processes.csv', [{key: row.get(key) for key in ['record_path', 'seconds', 'cpu_seconds', 'cpu_user_seconds', 'cpu_system_seconds', 'sampled_peak_tree_rss_kib_lower_bound', 'returncode', 'timed_out']} for row in slow])
    _, render_cost = get_render_accounting()
    summary = {'scheduled': 24, 'independent_sources': 6, 'repeats_per_source_endpoint': 2,
               'records_finished': sum(r['generation_success'] is not None for r in rows),
               'execution_success': sum(r['generation_success'] is True for r in rows),
               'BW_measured': sum(r['BW'] is not None for r in rows),
               'endpoints': endpoints, 'paired_differences': differences,
               'selection_start_BW': read(ROOT / 'round0.json')['selection']['S_BW'],
               'selection_H04_BW': read(ROOT / 'rounds/04/record.json')['selection']['S_BW'],
               'uncertainty_unit': 'Six independent sources, repetitions aggregated inside source',
               'pending_or_evaluator_failure_utility': None, 'closed_generation_failure_utility': 0,
               'cost_usd': None, 'CLI_cost_by_role': role_costs,
               'render_accounting': render_cost,
               'Blender_leaf_processes_measured': len(blender),
               'Blender_leaf_CPU_seconds': sum(t['cpu_seconds'] for t in blender if t['cpu_seconds'] is not None),
               'Blender_leaf_wall_seconds_cumulative': sum(t['seconds'] for t in blender),
               'cost_scope': 'CLI wall includes unknown remote queue/inference; direct Blender measurement scopes summed separately; never added to enclosing launch/generation scopes as total wall time',
               'meta_capability_improvement': 'not established by H score trajectory',
               'private_reference_sheet': str(private_output) if private_output else None}
    save_csv('final_test_raw.csv', rows);save_csv('final_test_sources.csv', sources);save_csv('final_test_endpoints.csv', endpoints)
    (ROOT / 'metrics/final_test_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    contact_sheet(scenes, versions, rows, ROOT / 'figures/final_test_contact_sheet.png', include_references=False)
    if private_output:contact_sheet(scenes, versions, rows, private_output, include_references=True)
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    colors = ['#4477aa', '#cc6677']
    for label, version, offset, color in zip(['start', 'H04'], versions, [-.12, .12], colors):
        for index, scene in enumerate(scenes):
            values = [r['BW'] for r in rows if r['scene_id'] == scene['scene_id'] and r['H_version'] == version and r['BW'] is not None]
            axes[0].scatter([index + offset] * len(values), values, color=color, label=label if index == 0 else None)
        endpoint = next(e for e in endpoints if e['H_version'] == version)
        axes[1].plot(range(8), [endpoint[key + '_source_equal_conditional_mean'] for key in DIMENSIONS], 'o-', color=color, label=label)
    axes[0].set_xticks(range(6), [s['scene_id'] for s in scenes], rotation=35);axes[0].set_ylabel('BW-style score');axes[0].set_title('Every measured repetition; six sources');axes[0].legend()
    axes[1].set_xticks(range(8), [key.replace('_', '\n') for key in DIMENSIONS], fontsize=7);axes[1].set_ylim(0, 10);axes[1].set_title('Eight dimensions; source-equal conditional means');axes[1].legend()
    for index, source in enumerate(sources):
        if source['BW_paired_difference'] is not None:axes[2].scatter(index, source['BW_paired_difference'], color='#4477aa', marker='o')
        if source['BW_utility_difference'] is not None:axes[2].scatter(index, source['BW_utility_difference'], color='#cc6677', marker='x')
    axes[2].axhline(0, color='black', lw=.7);axes[2].set_xticks(range(6), [s['scene_id'] for s in scenes], rotation=35)
    axes[2].set_title('H04 - start: matched quality (o), failure-zero utility (x)')
    fig.tight_layout();fig.savefig(ROOT / 'figures/final_test_quality.png', dpi=140);plt.close(fig)
    def show(value):return 'pending/null' if value is None else f'{value:.4f}' if isinstance(value, float) else str(value)
    lines = ['# V3 Final Test：独立来源统计', '',
             f"当前24项中保存终态 {summary['records_finished']}，生成成功 {summary['execution_success']}，BW实测 {summary['BW_measured']}。", '',
             '六个真实来源是统计单位；每来源两次生成先合并。成功条件质量与全部预定任务的失败零效用分列。评价服务失败和未开始项保持null，不算零。没有重新选择H_best。', '',
             '| endpoint | 全预定 | 生成成功 | BW实测 | 来源等权条件BW | 完成任务条件BW | 全预定BW效用 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for e in endpoints:
        lines.append(f"| {e['H_version']} | 12 | {e['execution_success']} | {e['BW_measured']} | {show(e['BW_source_equal_conditional_mean'])} | {show(e['BW_completed_task_conditional_mean'])} | {show(e['BW_utility_all_scheduled'])} |")
    lines += ['', '| 来源 | start 成功/2 | H04 成功/2 | 匹配实测BW对数 | BW配对差 | BW零效用差 | start重复SD | H04重复SD |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for s in sources:
        lines.append('| ' + ' | '.join(show(s[k]) for k in ['scene_id', 'start_generation_success', 'H04_generation_success', 'BW_measured_pairs', 'BW_paired_difference', 'BW_utility_difference', 'start_BW_repeat_sd', 'H04_BW_repeat_sd']) + ' |')
    lines += ['', '配对BW差（H04-start）：' + json.dumps(differences['BW'], ensure_ascii=False),
              '全预定BW效用差：' + json.dumps(differences['BW_utility'], ensure_ascii=False), '',
              f"Selection：{summary['selection_start_BW']:.6f} → {summary['selection_H04_BW']:.6f}；Test的变化以上述六来源配对结果为准。",
              '95%区间用固定种子20261111，对六个来源的汇总值做10,000次percentile bootstrap；不足六个来源时不输出区间。这是小样本探索性不确定性描述，不是显著性或普遍优势证明。', '',
              '补充统计口径：原有group_summary中的完成任务条件均值仍保留；这里另列“每来源先合并重复，再来源等权平均”，没有回写旧指标或改变BW评分公式。',
              '模型服务失败、生成失败和评价失败见逐项原始表。失败零效用包含服务失败造成的交付损失，不能把它全部归因于几何算法。', '',
              '## 实际调用与计算成本', '',
              '| 角色 | CLI会话 | 状态 | 可见输入token | 可见输出token | usage已知会话 | 累计CLI墙钟秒 |',
              '|---|---:|---|---:|---:|---:|---:|']
    for cost in role_costs:
        lines.append('| ' + ' | '.join(show(cost[key]) for key in ['role', 'CLI_sessions', 'statuses', 'known_input_tokens', 'known_output_tokens', 'usage_known_sessions', 'CLI_wall_seconds']) + ' |')
    lines += ['', f"实测Blender叶进程 {len(blender)} 个，累计该作用域CPU秒 {summary['Blender_leaf_CPU_seconds']:.2f}；其阶段墙钟累加值不是全研究墙钟。渲染预算扣额 {render_cost['render_budget_charged']}，全局精确实际帧数仍unknown，逐目录证据见render_evidence.csv。",
              '费用不可见，精确底层模型请求数unknown；CLI会话、可观测turn、工具执行和token分开。远端排队与推理无法准确拆分，不伪造纯推理秒数。[角色成本CSV](../metrics/final_cost_by_role.csv)、[最慢实际子进程](../metrics/final_slowest_processes.csv)。旧耗时汇总漏读BW的*_timing.json已按事后报告说明补入，旧表图保留。', '',
              '原始Q、PSNR、SSIM、LPIPS、DINO、Rubric与八维分项、required/applicable/measured_pass/gate_pass、设备和调用数均保留在[逐项CSV](../metrics/final_test_raw.csv)。[来源CSV](../metrics/final_test_sources.csv)、[端点CSV](../metrics/final_test_endpoints.csv)、[汇总JSON](../metrics/final_test_summary.json)。', '',
              '![完整终测联系表](../figures/final_test_contact_sheet.png)', '',
              '公开联系表因原始BW参考图再分发许可未确认而明确留出Reference列；包含真实参考图的完整联系表只保留服务器本地，不进入Git或Release。失败输出留空，不用其他场景替代。', '',
              '![来源配对与八维质量](../figures/final_test_quality.png)', '',
              '这些图只读取本轮保存数据；生成脚本：`python final_statistics.py`。没有新模型调用或Blender渲染。']
    (ROOT / 'reports/FINAL_TEST_SUMMARY_ZH.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: summary[k] for k in ['scheduled', 'records_finished', 'execution_success', 'BW_measured']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-output', type=Path)
    args = parser.parse_args();report(args.private_output)
