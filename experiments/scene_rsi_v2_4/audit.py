"""Recompute historical H failure audit from saved evidence, without models or Blender."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


CATEGORIES = [
    'successful', 'model_call_timeout', 'model_service_error',
    'invalid_generated_program', 'blender_build_error', 'blender_build_timeout',
    'render_timeout', 'total_budget_exceeded', 'functional_rejection', 'unknown',
]
LABELS = {
    'successful': 'Successful', 'model_call_timeout': 'CLI timeout',
    'model_service_error': 'Routing / service error',
    'invalid_generated_program': 'Invalid program', 'blender_build_error': 'Build error',
    'blender_build_timeout': 'Build timeout', 'render_timeout': 'Render timeout',
    'total_budget_exceeded': 'Total scene deadline',
    'functional_rejection': 'Functional rejection', 'unknown': 'Unknown',
}


def read(path):
    return json.loads(path.read_text())


def local_path(path):
    if path is None:
        return None
    marker = '/scene-rsi-rsi-1-3d-blender/'
    return path.split(marker, 1)[1] if marker in path else path


def v21_rows(source):
    rows = []
    for saved in source['rows']:
        failed = not saved['valid']
        rows.append({
            'experiment': 'V2.1', 'method': saved['method'],
            'run_id': saved['run_id'], 'candidate_id': saved['candidate_id'],
            'scene_id': saved['scene_id'], 'split': saved['split'],
            'original_status': saved['original_status'], 'terminal': True,
            'execution_success': saved['valid'],
            'original_failure_type': saved['original_failure_type'],
            'historical_secondary_classifier': None,
            'audited_failure_type': saved['audited_failure_type'] or 'successful',
            'audited_detail': saved['observed_stage'],
            'stage': saved['observed_stage'],
            'scene_deadline_limited': failed and saved['audited_failure_type'] == 'total_budget_exceeded',
            'transport_or_routing_evidence': False,
            'total_task_seconds': saved['seconds'],
            'inner_runtime_seconds': saved['runtime_status']['seconds'],
            'model_cli_wall_seconds': saved['model_wall_seconds'],
            'model_service_queue_seconds': None,
            'blender_wall_seconds': saved['blender_wall_seconds'],
            'cli_sessions': saved['cli_session_count'], 'blender_executions': saved['execution_count'],
            'actual_model': None, 'requested_model': 'gpt-6.1-sol', 'reasoning_effort': 'medium',
            'measured_Q': saved['measured_Q'],
            'record_path': saved['record_path'], 'trajectory_path': saved['trajectory_path'],
            'evidence_summary': saved['evidence_summary'],
            'limitations': ('No stage telemetry and empty Blender stdout/stderr. Pre-render is inferred from no saved blend; exact startup/build/device/save substage unknown.'
                            if failed and saved['audited_failure_type'] == 'total_budget_exceeded'
                            else 'CLI queue and remote inference time are not separately measured.'),
            'evidence_source': 'audit_sources/v21_audit.json',
        })
    return rows


def v22_rows(records, review):
    reviewed = {local_path(row['record_path']): row for row in review['records']}
    rows = []
    for saved in records:
        record = saved['record']
        record_path = saved['record_path']
        valid = record['metrics']['valid']
        item = reviewed.get(record_path)
        if valid:
            category = 'successful'
            detail = 'completed'
            stage = 'completed'
            evidence = 'Executable scene and visual metrics saved.'
            limitations = 'Natural-image reconstruction has no three-dimensional ground truth.'
        else:
            detail = item['reviewed_type']
            stage = item['terminal_observed_stage']
            evidence = item['evidence_conclusion']
            limitations = item['limitations']
            if detail == 'scene_program_build_errors_after_two_execution_attempts':
                category = 'blender_build_error'
            elif detail == 'scene_deadline_limited_repair_cli_after_build_error':
                category = 'total_budget_exceeded'
            elif detail == 'cli_model_cap_timeout_with_network_failure_evidence':
                category = 'model_call_timeout'
            elif detail == 'cli_routing_service_failure_exit_1':
                category = 'model_service_error'
            else:
                category = 'blender_build_timeout'
        folder = Path(record['folder'])
        # Successful call/execution costs are retained in original trajectory snapshots below.
        if item is not None:
            model_seconds = sum(call['seconds'] for call in item['calls'])
            blender_seconds = sum(execution['seconds'] for execution in item['executions'])
        else:
            model_seconds = record['usage']['seconds']
            blender_seconds = saved['blender_wall_seconds']
        rows.append({
            'experiment': 'V2.2', 'method': record['method'],
            'run_id': record['run_id'], 'candidate_id': record['candidate_id'],
            'scene_id': record['scene_id'], 'split': record['split'],
            'original_status': record['status'], 'terminal': True, 'execution_success': valid,
            'original_failure_type': record['failure_type'],
            'historical_secondary_classifier': item['historical_B_classifier_category'] if item else None,
            'audited_failure_type': category, 'audited_detail': detail, 'stage': stage,
            'scene_deadline_limited': item['runtime_scene_deadline_limited'] if item else False,
            'transport_or_routing_evidence': any(call['transport_messages'] for call in item['calls']) if item else False,
            'total_task_seconds': record['seconds'],
            'inner_runtime_seconds': record['runtime_status']['seconds'],
            'model_cli_wall_seconds': model_seconds, 'model_service_queue_seconds': None,
            'blender_wall_seconds': blender_seconds,
            'cli_sessions': record['usage']['calls'], 'blender_executions': record['usage']['executions'],
            'actual_model': None, 'requested_model': 'gpt-6.1-sol', 'reasoning_effort': 'medium',
            'measured_Q': record['metrics']['overall'],
            'record_path': record_path,
            'trajectory_path': local_path(str(folder/'trajectory.jsonl')),
            'evidence_summary': evidence, 'limitations': limitations,
            'evidence_source': 'audit_sources/audit_review.json' if item else 'audit_sources/v22_records.json',
        })
    return rows


def figure(rows, destination):
    categories = [category for category in CATEGORIES[1:] if any(row['audited_failure_type'] == category for row in rows)]
    versions = ['V2.1', 'V2.2']
    colors = ['#377eb8', '#ff9e4a']
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8), gridspec_kw={'width_ratios': [1, 1.2]})
    left = np.zeros(len(categories))
    for version, color in zip(versions, colors):
        values = np.array([sum(row['experiment'] == version and row['audited_failure_type'] == category for row in rows) for category in categories])
        axes[0].barh(range(len(categories)), values, left=left, color=color, label=version)
        for index, count in enumerate(values):
            if count:
                axes[0].text(left[index]+count/2, index, str(count), ha='center', va='center', color='white', fontweight='bold')
        left += values
    axes[0].set_yticks(range(len(categories)), [LABELS[category] for category in categories])
    axes[0].invert_yaxis()
    axes[0].set_xlabel('Failed scheduled reconstructions (n = 21)')
    axes[0].set_title('Audited terminal category; original types retained')
    axes[0].legend()
    point_categories = ['successful'] + categories
    for version_index, (version, color) in enumerate(zip(versions, colors)):
        for category_index, category in enumerate(point_categories):
            matching = [row for row in rows if row['experiment'] == version and row['audited_failure_type'] == category]
            if not matching:
                continue
            offsets = np.linspace(-0.09, 0.09, len(matching)) if len(matching)>1 else [0]
            y = [category_index+(version_index-0.5)*0.24+offset for offset in offsets]
            axes[1].scatter([row['total_task_seconds'] for row in matching], y, color=color, marker='o' if version_index==0 else '^', s=36, alpha=0.8)
    axes[1].set_yticks(range(len(point_categories)), [LABELS[category] for category in point_categories])
    axes[1].invert_yaxis()
    axes[1].axvline(600, color='#555555', linestyle='--', linewidth=1)
    axes[1].set_xlabel('Recorded task wall time (seconds); every formal record')
    axes[1].set_title('44 raw observations; model queue time unknown')
    axes[1].grid(axis='x', alpha=0.2)
    fig.suptitle('Figure 1. Historical H failure audit — V2.1 and V2.2', fontsize=14)
    fig.text(0.5, 0.015, '14 failures exhausted a 600 s scene deadline. V2.1 has no build/render stage telemetry; no provider-time attribution.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def report(rows, summary):
    lines = ['# H_FAILURE_AUDIT：V2.1 / V2.2 的实际失败原因', '',
             '这是V2.4启动前的事后工程审计。仅重读已有记录和冻结代码，不调用模型、不运行Blender，不修改V2.1/V2.2的failure_type、状态、分数或候选选择。', '',
             '**主要发现：高失败率不能统一解释为三维几何算法失败。44个预定正式重建全部有终态记录，其中23个成功、21个失败。14个失败耗尽600秒场景总预算；3个触发模型调用超时，其中V2.2的两个有明确连接拒绝/网络等待证据；2个有明确CLI路由服务错误；2个在期限前因生成程序构建错误并用尽两次执行额度结束。**', '',
             '三项V2.2构建超时同时也是场景总预算耗尽。图中的终态分类将它们记为blender_build_timeout；scene_deadline_limited字段保留这个交叉事实，类别计数不得再次相加。', '',
             '## 实际覆盖与分母', '',
             '|实验|预定/记录/终态|重建成功|失败|尚未开始|', '|---|---:|---:|---:|---:|',
             '|V2.1|20 / 20 / 20|9|11|0|', '|V2.2固定H比较|24 / 24 / 24|14|10|0|', '',
             'V2.1的Development成功5/6、Selection成功2/6、Test成功2/8；所有Test均确实执行，不存在将未开始的Test计为失败。V2.2为同一固定比较协议下H0与r1/C2各12项：H0成功4/12，r1/C2成功10/12。历史机制实验、烟测和外部编辑不混入44项分母。', '',
             '## 实际时间与内层预算', '',
             '两个版本均为gpt-6.1-sol / medium重建，单CLI上限300秒，Blender配置上限600秒，**整个场景Runtime总预算600秒**，最多3次CLI、2次Blender执行，外层610秒，CPU两线程。CLI和Blender的实际超时都取各自上限与剩余场景时间的较小值；这不是每阶段各有600秒。没有独立的构建、渲染或修复时间保留。', '',
             '- V2.1的10个场景期限失败：CLI正常结束，耗时83.15–283.88秒；首次Blender执行随后获得剩余316.03–516.68秒并耗尽。所有这些执行的stdout/stderr均为空、无阶段遥测、无.blend或final.png。render.py先保存.blend再渲染，因此推测尚未完成渲染前流程，但不能区分启动、生成程序构建、验证、设备设置及保存。主分类为total_budget_exceeded，不强行归咎于几何、Boolean或Cycles。',
             '- V2.1另1个C1/Selection调用在约300秒本地超时，没有生成程序。JSONL只有启动事件和一句开场消息；服务端原因、远端推理时间与排队时间未知。',
             '- V2.2 H0的两个首调用超时约300秒，JSONL明确出现Connection refused和waiting for network。观察到连接故障，不代表已识别远端根因。',
             '- V2.2 H0 r1/commons_192968130先构建422.34秒后因World缺失失败，修复CLI只剩82.246529秒后被场景期限截断；它不是一次独立的300秒模型超时。',
             '- V2.2的三项构建超时，实际子进程额度仅29.734320、390.001982、454.524263秒；有scene_build_started、无scene_build_completed或render_started。没有证据表明它们是Cycles渲染超时。',
             '- V2.2的两个程序错误终态均先出现fillet半径非法、再出现World为None。执行额度已经用尽后，固定policy仍发出第三次CLI并收到完整程序，却不再执行；这是可定位的预算浪费。保持原始失败，不以这份未执行程序宣称重建完成。',
             '- V2.2 r1/C2两个错误为CLI明确报告routing discovery failed、turn.failed并退出1，耗时13.69和19.09秒；无Blender执行，不属于图像难度或几何失败。', '',
             '本次没有统一增加预算，没有重放或修补失败程序。若后续评估更宽松时限，必须以同一H做单独预算敏感性实验，不能解释为算法改善。模型CLI wall time包含等待与生成；服务排队时间没有单独测量，始终保留null。', '',
             '## 21项失败逐项索引', '',
             '|实验 / 重复 / H / 场景|原始failure_type|本次分类|观测阶段|任务秒|',
             '|---|---|---|---|---:|']
    for row in rows:
        if row['execution_success']:
            continue
        label = ' / '.join(row[key] for key in ['experiment','run_id','candidate_id','scene_id'])
        lines.append(f"|{label}|{row['original_failure_type']}|{row['audited_failure_type']}|{row['stage']}|{row['total_task_seconds']:.3f}|")
    lines += ['', '逐项解释、原始记录路径、CLI时间、Blender时间、原始类型及审计依据见[CSV](metrics/H_failure_audit.csv)与[JSON](metrics/H_failure_audit.json)。完整细阶段证据见[audit_review.json](audit_sources/audit_review.json)、[V2.1审计](audit_sources/v21_audit.json)。原始日志继续保留在其V2.1/V2.2实验目录及既有Release，不将本次归因回写历史指标。', '',
              '## 图与可重算命令', '',
              '![失败分类及所有任务耗时](figures/figure1_failure_audit.png)', '',
              '统计单位为正式重建尝试；同一场景跨H/研发重复的尝试不是新的独立场景。柱图使用终态主分类，右图展示全部44个真实任务耗时点，未筛选案例。原始分数缺测保持null，不生成虚假PSNR、Q或服务等待时间。', '',
              '```bash', 'OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python audit.py', '```', '',
              '该命令只读取同目录audit_sources中的审计快照，重生成表格、图及本文；无需模型、Blender或GPU。快照为事后审计证据，不冒充实验前冻结协议。', '',
              '## 可以与不能得出的结论', '',
              '可确定的是：错误来源混合了连接/路由故障、生成代码的参数/World错误，以及被共享期限截断的构建或修复。14个失败受到总预算限制；H0尤其容易在没有.blend时结束，不能直接进入视觉三维探测。此时应研究程序与执行证据。', '',
              '尚不能确定的是：V2.1超时的具体Blender子阶段，V2.2三次构建超时的精确慢操作，服务故障的远端根因，以及任何增加时限后的成功率。未运行独立重放，也没有声称所有已生成代码可正确执行。Boolean完成计数不是布尔成本归因；没有三维真值，不推断真实几何精度。', '',
              '本审计只澄清H的失败分母和执行条件，不是主动诊断有效性或共享H研发收益的证据。']
    return '\n'.join(lines)+'\n'


def main(root):
    source = root/'audit_sources'
    v21 = read(source/'v21_audit.json')
    v22 = read(source/'audit_review.json')
    rows = v21_rows(v21) + v22_rows(read(source/'v22_records.json'), v22)
    assert len(rows) == 44 and sum(not row['execution_success'] for row in rows) == 21
    summary = {
        'scope': 'All44 formal V2.1 reconstruction and V2.2 fixed-H comparison records, no smoke/supplemental tests.',
        'scheduled': 44, 'recorded': 44, 'terminal': 44, 'successful': 23, 'failed': 21, 'not_started': 0,
        'category_counts': dict(Counter(row['audited_failure_type'] for row in rows)),
        'scene_deadline_limited_failures': sum(row['scene_deadline_limited'] for row in rows),
        'transport_or_routing_evidence_failures': sum(row['transport_or_routing_evidence'] for row in rows),
        'service_queue_seconds': None, 'remote_inference_seconds': None,
        'new_model_calls': 0, 'new_blender_jobs': 0,
        'category_rule': 'Terminal stage first where logged. V2.2 three logged build timeouts are blender_build_timeout and also have scene_deadline_limited=true. V2.1 no stage telemetry: total_budget_exceeded with substage unresolved.',
        'figure_source': 'metrics/H_failure_audit.csv', 'generator': 'audit.py',
        'statistical_unit': 'Scheduled reconstruction attempt; repeated H/runs are not independent natural scenes.',
        'by_experiment': {version: {'scheduled': sum(row['experiment'] == version for row in rows),
                                    'successful': sum(row['experiment'] == version and row['execution_success'] for row in rows)}
                          for version in ['V2.1','V2.2']},
    }
    metrics = root/'metrics'; metrics.mkdir(exist_ok=True)
    figures = root/'figures'; figures.mkdir(exist_ok=True)
    (metrics/'H_failure_audit.json').write_text(json.dumps({'summary': summary, 'rows': rows}, ensure_ascii=False, indent=2)+'\n')
    with (metrics/'H_failure_audit.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({key: 'null' if value is None else value for key, value in row.items()} for row in rows)
    figure(rows, figures/'figure1_failure_audit.png')
    (root/'H_FAILURE_AUDIT.md').write_text(report(rows, summary))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    main(parser.parse_args().root)
