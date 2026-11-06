"""Write V2.4 publication documents after terminal offline analysis; no experiments."""
from pathlib import Path
from collections import Counter
import argparse
import json
import re
import shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = 'experiments/scene_rsi_v2_4'
TAG = 'scene-rsi-v2.4-2026-11-06'
BRANCH = 'research/scene-rsi-v2.4'
METHODS = ['fixed', 'structured', 'active']
LABEL = {'reference': '新 H_start', 'fixed': 'Fixed', 'structured': 'Structured', 'active': 'Active'}
BUNDLES = ['fixed.tar.gz', 'structured.tar.gz', 'active.tar.gz', 'shared-evidence.tar.gz']


def read(path):
    return json.loads(path.read_text())


def fmt(value):
    return 'null' if value is None else format(value, '.4f') if isinstance(value, float) else str(value)


def mean(values):
    return sum(values)/len(values) if values else None


def clean(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def public_path(value, source):
    return str(value).replace(str(source), '<EXPERIMENT_ROOT>').replace(str(ROOT), '<PROJECT_ROOT>').replace('__SERVER_USER_ROOT__', '<SERVER_USER_ROOT>').replace('__SERVER_USER_ROOT__', '<SERVER_USER_ROOT>')


def selected_test(scenes, selections):
    lookup = {(r['task_id'], r['method'], r['role']): r for r in scenes if r['scope'] == 'formal'}
    rows = []
    for choice in selections:
        base = lookup[(choice['task_id'], 'reference', 'transfer')]
        method = choice['method'] if choice['selected'] == 'C1' else 'reference'
        chosen = lookup[(choice['task_id'], method, 'transfer')]
        q_pair = base['execution_success'] is True and chosen['execution_success'] is True and base['Q'] is not None and chosen['Q'] is not None
        rows.append({'task_id': choice['task_id'], 'method': choice['method'], 'selected': choice['selected'],
                     'baseline_Q': base['Q'], 'selected_Q': chosen['Q'],
                     'paired_delta_Q': chosen['Q']-base['Q'] if q_pair else None,
                     'baseline_utility': base['failure_utility'], 'selected_utility': chosen['failure_utility'],
                     'utility_delta': chosen['failure_utility']-base['failure_utility']
                         if chosen['failure_utility'] is not None and base['failure_utility'] is not None else None})
    return {method: {'all_planned': len([r for r in rows if r['method'] == method]),
                    'nonnull_both_success_n': sum(r['method'] == method and r['paired_delta_Q'] is not None for r in rows),
                    'paired_delta_Q_mean': mean([r['paired_delta_Q'] for r in rows if r['method'] == method and r['paired_delta_Q'] is not None]),
                    'all_planned_utility_delta_mean': mean([r['utility_delta'] for r in rows if r['method'] == method])
                        if all(r['utility_delta'] is not None for r in rows if r['method'] == method) else None}
            for method in METHODS}, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'outputs/scene_rsi_v2_4')
    parser.add_argument('--repo', type=Path, default=ROOT/'archive/scene')
    parser.add_argument('--commit', help='Scientific archive commit ID or its actual GitHub URL')
    parser.add_argument('--uploaded', action='store_true', help='Only after actual Release remote verification')
    args = parser.parse_args()
    source, repo = args.source.resolve(), args.repo.resolve()
    final = read(source/'FINAL_STATUS.json')
    summary = read(source/'metrics/summary.json')
    if final['phase'] != 'all_scheduled_terminal' or not summary['workflow_terminal']:
        raise RuntimeError('Wait for terminal experiment and fresh final offline analysis')
    scenes = read(source/'metrics/scene_metrics.json')
    candidates = read(source/'metrics/candidates.json')
    calls = read(source/'metrics/calls.json')
    costs = read(source/'metrics/costs.json')
    cfg = read(source/'config.json')
    freeze = read(source/'configs/freeze.json')
    selections = read(source/'configs/selection_freeze.json')['selections']
    if len(candidates) != 6 or sum(r['scope'] == 'formal' for r in scenes) != 16:
        raise ValueError('Expected all six proposals and sixteen scheduled fresh evaluation rows')
    if not all(r['schedule_terminal'] for r in scenes if r['scope'] == 'formal'):
        raise ValueError('Final tables still contain pending formal work')
    selected, selected_rows = selected_test(scenes, selections)
    audit = read(source/'metrics/H_failure_audit.json')
    h0 = [r for r in audit['rows'] if r['candidate_id'] == 'H0']
    h0_failures = Counter(r['audited_failure_type'] for r in h0 if not r['execution_success'])
    total = summary['cost']
    if total['CLI_sessions'] != final['ledger']['cli_sessions']:
        raise ValueError('Final metrics and terminal ledger disagree; refresh offline analysis first')
    commit = (args.commit if args.commit.startswith('https://') else 'https://github.com/i025/scene/commit/'+args.commit) if args.commit else None
    release = None
    if args.uploaded:
        release = read(repo/'docs/V2_4_RELEASE_UPLOAD_STATE.json')
        if not release['remote_asset_listing_verified'] or release['tag'] != TAG:
            raise ValueError('Release remote verification receipt is absent or belongs to another version')
        if {a['name'] for a in release['assets']} != set(BUNDLES) or not all(a['status'] == 'uploaded' for a in release['assets']):
            raise ValueError('All four actual Release assets must be verified before --uploaded')
    publication = '完整四包 Release 已有远端资产列表确认；提交链接由主任务核对。' if args.uploaded else '本地归档已整理；推送与 Release 上传状态尚未确认，不声称已上传。'
    docs = repo/'docs'
    checkpoint = docs/'README_V2_3_CHECKPOINT_d72817b.md'
    if not checkpoint.exists():
        if not (repo/'README.md').read_text().startswith('# Scene-RSI V2.3'):
            raise ValueError('V2.3 README checkpoint missing; do not mislabel another README as V2.3')
        shutil.copy2(repo/'README.md', checkpoint)
    formal = [r for r in scenes if r['scope'] == 'formal']
    counts = {}
    for method in ['reference', *METHODS]:
        group = [r for r in formal if r['method'] == method]
        arms = [c for c in candidates if c['method'] == method]
        counts[method] = {'scheduled': len(group), 'completed': sum(r['status'] == 'completed' for r in group),
            'execution': sum(r['execution_success'] is True for r in group),
            'functional': sum(r['functional_eligible'] is True for r in group),
            'failures': sum(r['status'] in ['failed', 'timeout', 'invalid'] for r in group),
            'not_executed': sum(r['status'] == 'not_started' for r in group),
            'source_Q': mean([r['Q'] for r in group if r['role'] == 'source' and r['Q'] is not None]),
            'source_Q_n': sum(r['role'] == 'source' and r['Q'] is not None for r in group),
            'transfer_Q': mean([r['Q'] for r in group if r['role'] == 'transfer' and r['Q'] is not None]),
            'transfer_Q_n': sum(r['role'] == 'transfer' and r['Q'] is not None for r in group),
            'generated': sum(c['status'] == 'completed' for c in arms),
            'candidate_failures': sum(c['status'] in ['failed', 'invalid', 'timeout'] for c in arms),
            'effective': sum(c['effective_shared_repair'] is True for c in arms)}
    active = [c for c in candidates if c['method'] == 'active']
    active_probes = sum(c['probes_completed'] for c in active)
    active_unresolved = sum(c['diagnosis_unresolved'] is True for c in active)
    ratios = [c['evidence_ratio'] for c in active]
    questions = [
        ('为什么H0失败？哪些属于模型调用，哪些属于构造程序与执行复杂度，哪些尚不能确定？',
         '历史审计中 H0 共 '+str(len(h0))+' 次，失败类别 '+json.dumps(dict(h0_failures), ensure_ascii=False)+'。另有 r1/C2 的两次明确 CLI 路由/服务错误，不能算作 H0 的程序错误。原始日志区分连接故障、生成参数/World 错误，以及共享 600 秒预算截断；仅有 build_started 的超时不能定位为布尔重载或 GPU 问题。远端纯推理/排队、V2.1 具体 Blender 子阶段及增加预算后的可恢复性仍未知。'),
        ('主动三维诊断是否被真正执行？是否形成了有区分性的观测？',
         'Active 正式完成 '+str(active_probes)+' 次探测；第二阶段 unresolved '+str(active_unresolved)+'/2，启发式权重比 '+str(ratios)+'。实际观测进入可执行 M，但执行探测不等于区分原因。自然图像无故障真值，SSIM 敏感性和软兼容分数不是因果识别或后验概率。'),
        ('这种观测是否改善了共享重建H的研发？是否比固定诊断更有效？',
         '严格有效修复为 Active '+str(counts['active']['effective'])+'/2、Fixed '+str(counts['fixed']['effective'])+'/2、Structured '+str(counts['structured']['effective'])+'/2。保留全部点、功能与成本；每方法只有两个研发任务，重建使用独立远端采样，不能把这一小样本差异证明为可靠的主动诊断优势或普遍研发能力提升。'),
        ('是否存在真实的跨场景收益？需要哪些进一步实验才能支持论文贡献？',
         '实际 Selection 选后迁移的条件质量差异和全预定失败效用差异见下表；它们只支持这些历史已暴露的房间及本次采样。需增加独立未暴露来源、独立选择集、匹配实际探测成本、重复模型采样、可识别的干预与结构/编辑回归，再验证下游共享 H 收益；本轮没有自动 M 后代或冻结元回放。')]
    comparison = ['|方法|执行成功/预定|功能通过/预定|失败/未执行|真实提案/预定|源条件 Q (n)|迁移条件 Q (n)|严格有效修复|',
                  '|---|---|---|---|---|---|---|---|']
    for method in ['reference', *METHODS]:
        c = counts[method]
        comparison.append('|'+LABEL[method]+'|'+str(c['execution'])+'/'+str(c['scheduled'])+'|'+str(c['functional'])+'/'+str(c['scheduled'])+'|'+str(c['failures'])+'/'+str(c['not_executed'])+'|'+(str(c['generated'])+'/2' if method != 'reference' else 'N/A')+'|'+fmt(c['source_Q'])+' ('+str(c['source_Q_n'])+')|'+fmt(c['transfer_Q'])+' ('+str(c['transfer_Q_n'])+')|'+(str(c['effective'])+'/2' if method != 'reference' else 'N/A')+'|')
    selected_table = ['|方法|选后 Test ΔQ（双方执行成功）|有效配对 n / 全预定|全预定失败效用差均值|', '|---|---|---|---|']
    for method in METHODS:
        s = selected[method]
        selected_table.append('|'+LABEL[method]+'|'+fmt(s['paired_delta_Q_mean'])+'|'+str(s['nonnull_both_success_n'])+'/'+str(s['all_planned'])+'|'+fmt(s['all_planned_utility_delta_mean'])+'|')
    cost_table = ['|成本组|CLI 会话|已知输入/输出 token|usage 缺失|探测 Blender 秒|重建流水线秒|', '|---|---|---|---|---|---|']
    for c in costs:
        cost_table.append('|'+c['cost_group']+'|'+str(c['CLI_sessions'])+'|'+str(c['known_input_tokens'])+'/'+str(c['known_output_tokens'])+'|'+str(c['usage_unknown_sessions'])+'|'+fmt(c['probe_Blender_seconds'])+'|'+fmt(c['reconstruction_pipeline_seconds'])+'|')
    representative = next((r for task in ['task01', 'task02'] for method in ['reference', *METHODS]
                           for r in formal if r['task_id'] == task and r['method'] == method and r['role'] == 'transfer'
                           and r['status'] == 'completed' and (source/r['folder']/'scene.blend').exists()), None)
    artifact = (EXPERIMENT+'/'+representative['folder']+'/scene.blend') if representative else None
    program = (EXPERIMENT+'/'+representative['folder']+'/build.py') if representative else None
    representative_text = ('代表工程按固定 task01、task02；H_start、Fixed、Structured、Active 顺序选择首个实际完成且文件存在的迁移输出，不挑赢家：`'+artifact+'`；对应 [场景程序]('+program+')。`.blend` 在完整 Release 包中，解压后可打开。') if representative else '没有满足规则且实际存在的迁移 `.blend`，不生成替代工程。'
    links = [('- ['+a['name']+']('+a['url']+')，'+str(a['size_bytes'])+' bytes') for a in release['assets']] if release else ['- 四个完整附件仍为 pending；本地工作目录 `work/scene_v2_4_archive/bundles/`。']
    question_text = '\n\n'.join('**'+str(i+1)+'. '+q+'**\n\n'+a for i, (q, a) in enumerate(questions))
    common = ['本轮从 V2.1 r1/C2 的共享 H_start 出发；`fixed_h/H0` 仅保存原始起点源码，没有作为本轮新评估对照。三组是 Scene-RSI 内部机制对照，不是重跑 SceneEvolve/Hyperagents 的 RSI 基线。',
              '源图先用于诊断和编码，再作为名为 Selection 的同图研发/筛选；不属于独立验证。另一房间 transfer 在候选与选择冻结后新执行，但图像曾在 V2.2 暴露，不能称全新盲测。',
              '冻结文字要求源 Q 提升 >0.01；实际 runner 在 H_start 功能资格失败时接受任意合格候选，即使 H_start 有有效 Q。保留实际选择，`selection_strict_gain_disagreement` 记录偏离，不事后改选。严格有效修复的额外派生条件仍为：源合格且 ΔQ>0.01，迁移合格且 ΔQ≥-0.01。',
              '每种方法只有两个研发任务，每个 H/图仅一次新重建，模型远端采样未被本地种子控制，也未量化其波动。各组初诊独立采样，不把质量差异唯一归因于探测。条件质量均值只含成功案例，执行失败且没有测量时 Q 保持 null，失败效用单独记零并保留全部预定分母；多视角不是独立重复。',
              '报告整理时目视可见 task01 新 H_start 的厨房迁移图近乎全黑，Q 约 0.195，仍执行成功且机械功能合规。原图和分数保留，不重采样；这个低基线放大了该场景的配对增益，限制均值的普遍解释。目视标注不改变评分或选择规则。',
              'M 是工程修订，无自动后代、无跨代能力提升或陌生 H 起点冻结元回放。全部最终编辑为机械操作，不存在文字指令编辑能力结果。',
              '实际模型角色由 calls.csv 决定：initial_diagnosis/shared_H_patch 使用 gpt-6-astra medium，student 使用 gpt-6.1-sol medium。record.model_roles 中 editor/judge 是沿用但未执行的元数据，不能计为实际编辑器或独立视觉评审。',
              '元诊断/共享修改 CLI 单次 600 秒；student 单次至多 300 秒且受内层剩余时间限制；内层总计 600 秒、最多 3 次调用/2 次执行。数值指标与外层功能检查在内层期限外另行执行，不把全部耗时误写为 600 秒以内。',
              'M 的平均归一化残差 ≤3 是软兼容阈值，不要求严格区间命中；指数权重比不是后验概率。所有假设的软残差均超阈值时保留 unresolved，不把 Q 或 SSIM 改善当唯一原因。']
    preparation_calls = sum(c['CLI_sessions'] for c in costs if c['cost_group'] in ['smoke', 'preparation'])
    cost_text = '本轮新增 CLI '+str(total['CLI_sessions'])+'/'+str(total['max_CLI_sessions'])+'；已知输入 '+str(total['known_input_tokens'])+'、输出 '+str(total['known_output_tokens'])+' token；usage 缺失 '+str(total['usage_unknown_sessions'])+'。渲染尝试上界 '+str(total['render_attempts_upper_bound'])+'/'+str(total['max_render_frames'])+'，完成 '+str(total['renders_completed'])+'。CPU 两线程、单重任务、GPU 0。新增全局预算和调用总数包含全部 '+str(preparation_calls)+' 次准备/烟测调用；每方法正式曲线不含这些共同准备费用及新 H_start，二者另表单列。历史复制日志不计新增。外层工程对话和固定模型服务基础设施成本不可观测、未定价，不声称各方法总研发实耗相等。模型、流水线与 Blender wall time 互有包含，不相加或据此声称算法速度优势；美元费用未知。'
    title = '# Scene-RSI V2.4：自然图像共享 H 诊断与修复先导实验'
    readme = [title, '', '研究问题：三维主动实验的真实观测是否帮助修改跨图像复用的重建流程，而不仅是修好某张图的 P？', '',
              '分支：`'+BRANCH+'`。'+publication, '', ('归档提交：['+args.commit+']('+commit+')。') if commit else '归档提交链接：pending，由实际提交后补充。', '',
              '已完成范围：2 个自然图像研发任务 × 3 种方法 × 1 个 H 提案，计划 16 个新重建任务；所有真实成功、失败、拒绝与未选候选均保留。', '',
              '## 实际结果', '', *comparison, '', *selected_table, '',
              '选后 ΔQ 按实际 selection_freeze 选择计算；原始候选迁移另见 candidates.csv。条件 ΔQ 不包含任何填零的视觉测量，全预定效用差则保留执行失败分母。', '',
              '## 四个问题的证据回答', '', question_text, '', '## 方法与结论边界', '', *['- '+s for s in common], '',
              '## 真实可视化', '', '统计单位是研发任务或新重建任务；源/迁移图按固定顺序展示全部输出，空白是真实缺失，不用历史图替代新 H_start。', '',
              '![历史 H0 与生成执行失败审计]('+EXPERIMENT+'/figures/figure1_failure_audit.png)', '',
              '![真实三维探测、事前预测与 M 观测更新]('+EXPERIMENT+'/figures/figure3_actual_diagnostics.png)', '',
              '![全部四场景：本轮新 H_start 与三个原始候选]('+EXPERIMENT+'/figures/figure4_fresh_reconstructions.png)', '',
              '![两个迁移场景：按冻结选择展示实际 H*，包含 H_start 回退]('+EXPERIMENT+'/figures/figure4_selected_transfer.png)', '',
              '![固定首个 Active 案例的真实 H diff 摘录与全部候选修改计数]('+EXPERIMENT+'/figures/figure4_shared_H_diff.png)', '',
              '![原始 Q、六个配对点与实际成本]('+EXPERIMENT+'/figures/figure5_results_cost.png)', '',
              '![两个预选迁移场景的机械编辑与非目标保持]('+EXPERIMENT+'/figures/figure6_real_edit_preservation.png)', '',
              '源图诊断输入与旧 V2.2 渲染单独见 [Figure 2]('+EXPERIMENT+'/figures/figure2_natural_diagnosis_inputs.png)；它们不是本轮新 H_start 的数值结果。已知结构错误检测见 [Figure 6]('+EXPERIMENT+'/figures/figure6_structural_calibration.png)。', '',
              '## 成本与原始证据', '', cost_text, '', *cost_table, '',
              '- [中文报告]('+EXPERIMENT+'/reports/REPORT_ZH.md) / [离线 HTML]('+EXPERIMENT+'/reports/index.html)',
              '- [逐场景原始指标]('+EXPERIMENT+'/metrics/scene_metrics.csv) / [六候选]('+EXPERIMENT+'/metrics/candidates.csv) / [调用]('+EXPERIMENT+'/metrics/calls.csv)',
              '- [分阶段模型成本]('+EXPERIMENT+'/metrics/costs_by_phase.csv)：共享 H 研发、源图重建、迁移推理和准备烟测分别列出。迁移成本包含预定的原始未选候选评价。',
              '- [事前预测]('+EXPERIMENT+'/metrics/forecasts.csv) / [实际观测]('+EXPERIMENT+'/metrics/probe_observations.json) / [图表来源]('+EXPERIMENT+'/metrics/figure_sources.json)',
              '- [事后审查索引](docs/REVIEW_INDEX_V2_4.md) / [as-run protocol](docs/AS_RUN_PROTOCOL_V2_4.md) / [离线命令](docs/COMMANDS_V2_4.md)', '',
              representative_text, '', '## 完整附件', '', *links, '',
              '全部路径与附件状态见 [artifacts_index_v2_4.csv](artifacts_index_v2_4.csv)。完整 stdout/JSONL、全部 `.blend`、大几何 JSON 按四包保留；普通 Git 提供关键代码、配置、原始表和真实图片。', '',
              '旧版入口：[V2.3 原提交 README](https://github.com/i025/scene/blob/d72817b0d90e9ecc5e156344128bacf76317e25e/README.md)；未经改写的本地文本另存 `docs/README_V2_3_CHECKPOINT_d72817b.md`，其相对链接仍以原仓库根为基准。V1/V2/V2.1/V2.2/V2.3 的实验和原始分数保持原样。未为第三方代码、Commons 图片或模型另加覆盖性许可证。']
    (repo/'README.md').write_text('\n'.join(readme)+'\n')
    protocol = ['# V2.4 AS-RUN PROTOCOL（事后整理）', '',
        '本文在实验结束后依据真实代码、配置、日志与数据整理，不冒充严格预注册。原始冻结文件 [protocol.md](../'+EXPERIMENT+'/protocol.md)、[freeze.json](../'+EXPERIMENT+'/configs/freeze.json) 和 [formal_frozen 快照](../'+EXPERIMENT+'/code_snapshots/formal_frozen/) 保持原样。', '',
        '## 实际执行设置', '', *['- '+s for s in common], '',
        '- 固定起点和各 H 变体：`fixed_h/r1_C2/{policy.py,system.txt}`；6 个独立工作区位于 `tasks/task01|task02/fixed|structured|active/H/`，保存真实 diff。M 为 `meta.py`；SceneAct/渲染/外部指标/资源控制不由候选修改。',
        '- 三组共同拥有原始图像、历史 P/渲染、对象/层级、结构及执行信息，都是最多两个探测和一次 H 提案。Fixed 取固定相机/尺度，Structured 不探测，Active 用事前预测排序。实际探测数和不同模型采样成本分别报告，不声称严格实耗相等。',
        '- Codex 使用全新 ephemeral 会话、真实图像附件、只读工作区与固定禁用工具；无隐藏共享对话、网页搜索或额外 subagent。模型只返回内容，runner 显式执行代码/Blender/修复。输入、stdout JSONL、stderr、usage 与实际请求参数全部留存。',
        '- 五类工具：camera_focal、camera_tilt、object_scale、object_depth、isolate；临时副本执行。固定 ROI 下 outcome=0.5×全图 ΔSSIM+0.5×ROI ΔSSIM，预测在操作前保存。最多两个，不根据输赢增加预算。',
        '- 渲染为 Cycles、512 长边、16 samples、AgX、seed42；CPU 两线程、单重任务。低质量确定性工具校准另标，排除正式图像质量对比。',
        '- 主 Q 沿用 `(clip(SSIM,0,1)+1-clip(LPIPS,0,1)+(1+clip(DINO,-1,1))/2)/3`；PSNR 另报。缺测保留 null，不用语言模型猜数值。',
        '- 代码冻结后先 source/同图 Selection，统一保存选择，再新执行另一房间 transfer；测试结果未用于这一轮重新提案。实际访问顺序保留在日志与 selection_freeze 中；由于历史暴露，不声称严格盲测。', '',
        '## 原始事实与事后派生分析', '', *comparison, '', *selected_table, '', cost_text, '',
        'P：各场景新生成的 build.py；H：跨图像复用的 policy.py/system.txt；M：工程编写并实际执行的两阶段策略。H-only 提案不算自动 M 自修改。记录模型中 editor/judge 字段的存在不代表这些调用实际发生。', '',
        '全部选择保留实际分支，严格有效修复及配对 ΔQ 是透明的事后派生统计。不能把 source/Selection 重叠掩盖为独立验证，也不能把归档修订的报告器替换成实验时 H/M/评价器；原代码与 report_history 均保留。', '',
        '结构门槛分别保存 required/applicable/measured_pass/gate_pass。机械材质/组合移动和声明部件完整性不是语义三维真值；AABB 支撑近似与三角面交叉的限制见原始报告。没有文字编辑器、没有不可见区域恢复精度或新视角真值。', '',
        '## 未执行与偏离', '',
        '未开展自动 M 后代、冻结元能力回放、SceneEvolve/Hyperagents 演化或 BlenderWorld 全量测试。准备期无效对象、旧菜单无可区分预测等记录完整保留，费用计入新预算。没有因正负结果扩大上限。', '',
        '现场仍存在的失败/缺测按 scene_metrics 与 failure 日志报告；终态不代表所有任务成功。发布、重画不调用模型或重跑重建。']
    (docs/'AS_RUN_PROTOCOL_V2_4.md').write_text('\n'.join(protocol)+'\n')
    review = ['# V2.4 审查索引', '', '主张 → 对应代码 → 原始数据 → 图表 → 局限或缺失证据。此表不预先宣判方法有效。', '',
        '|待审查主张|代码|原始数据|图表|局限|', '|---|---|---|---|---|',
        '|历史 H0 失败来源可区分|audit.py；audit_sources/audit_v21.py|metrics/H_failure_audit.csv；audit_sources/raw_failures/；audit_review.json|Figure 1|事后审计；部分构建子阶段和远端根因未知|',
        '|主动探测真实执行并返回 M|meta.py plan_probes/plan_patch；experiment.py propose；inspect_blend.py|tasks/*/*/stage1.json、observations.json、stage2.json；真实 probe PNG/.blend|Figure 3|执行不等于成功区分原因；软残差兼容不是后验|',
        '|改变的是共享 H|tasks/*/*/H/；policy.py.diff、system.txt.diff|candidate.json；coding/response.txt；新 results/ 记录；metrics/shared_H_diff_summary.csv、shared_H_diff_excerpt.json|Figure 4 联系表与真实 diff 摘录；完整 tasks/task01/active/policy.py.diff|编码者 observation_used 是自述，不证明诊断因果收益；摘录按固定案例选择，未按质量挑选|',
        '|新的 Selection 与迁移收益|experiment.py run；analyze.py collect_candidates|configs/selection_freeze.json；metrics/scene_metrics.csv、candidates.csv|Figure 5|source 同图研发/筛选；实际 baseline-ineligible 分支偏离冻结文字；仅两个任务|',
        '|机械编辑和结构保持|inspect_blend.py mechanical；regression.py|functional/mechanical.json、summary.json；metrics/actual_mechanical_preservation.csv|Figure 6 real edits 与结构校准|预定义机械操作；无文字编辑；自然几何真值缺失|',
        '|全部研发成本与失败分母|backend/codex_wrapper.py；backend/runtime.py；analyze.py collect_costs|session/request/stdout JSONL/stderr；metrics/calls.csv、costs.csv|Figure 5|未知 usage 不补造；wall time 有包含关系，不宣称速度优势|', '',
        '以上相对代码/数据路径均位于 [实验目录](../'+EXPERIMENT+'/)。[中文报告](../'+EXPERIMENT+'/reports/REPORT_ZH.md)、[图表来源表](../'+EXPERIMENT+'/metrics/figure_sources.json)、[实现审计](../'+EXPERIMENT+'/metrics/implementation_audit.json)、[审计脚本](../'+EXPERIMENT+'/audit_results.py)、[历史报告器](../'+EXPERIMENT+'/report_history/) 均保留。', '',
        question_text, '', '## 全部附件', '', *links, '', representative_text]
    (docs/'REVIEW_INDEX_V2_4.md').write_text('\n'.join(review)+'\n')
    manifest = read(source/'manifest.json')
    media = {entry[role]['scene_id']: entry[role] for entry in manifest for role in ['source', 'transfer'] if entry[role] is not None}
    deps = ['# V2.4 依赖、来源与迁移配置', '',
        '- 工作基于 V2.3 分支/检查点 d72817b；本轮 H_start 来自已运行的 V2.1 r1/C2，原始 H0 也随包保存。复用关系见 reuse_inventory.md 与 fixed_h，不依赖服务器绝对路径作为版本证明。',
        '- SceneAct/执行后端源于本地 SceneEvolve CLI 复现及 V2.2 适配，保留 `backend/LICENSE`。本轮 common Runtime 的预算边界修订、M 的五工具/ROI 选择在正式前冻结；未重新实现上游框架。',
        '- 离线审计/绘图只需 Python 3.11、NumPy、Pillow、Matplotlib。实际重建还需既有 scikit-image、PyYAML、requests、torch、transformers、lpips 等环境；未向共享环境新安装/升级。',
        '- Blender 4.2.10 LTS 复用既有 BlenderWorld runtime；Codex CLI 沿用此前已跑通版本与参数，不分发可执行文件、登录信息或凭据。实际返回模型无法独立确认时保留 unknown。', '',
        '- 实际包版本见 [dependency_versions.json](../'+EXPERIMENT+'/configs/dependency_versions.json)；CLI 版本与真实支持参数见 configs/cli_version.txt、configs/cli_exec_help.txt。资源清单初版与事后补充分别保存，不补写成预注册。', '',
        '## 服务器原资源路径的可迁移标签', '',
        '|配置字段|现场资源位置（脱敏标签）|其他机器所需动作|', '|---|---|---|']
    locations = [('blender.executable', cfg['blender']['executable']), ('model.command', cfg['model']['command']),
                 ('metrics.dino_model', cfg['metrics']['dino_model']), ('metrics.alexnet_weights', cfg['metrics']['alexnet_weights']),
                 ('metrics.lpips_model_path', cfg['metrics']['lpips_model_path']), ('dataset.manifest', cfg['dataset']['manifest'])]
    for field, value in locations:
        deps.append('|'+field+'|`'+clean(public_path(value, source))+'`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|')
    deps += ['', '实际服务器 Python 为原 SceneEvolve 复现的 `<PROJECT_PARENT>/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python`。数值权重来自已有缓存；CPU 前向不是用 Codex 估分。离线重画不会加载权重。', '',
        '归档用 `__EXPERIMENT_ROOT__`、`__SERVER_USER_ROOT__` 等替换服务器路径；离线工具将实验根重定位到新 derived 目录。正式执行还要迁移 results_dir、dataset.manifest/source_root、模型/Blender 路径，恢复全部 Release 与许可媒体；不能直接拿归档目录当原运行现场。', '',
        '## 本轮实际使用的自然图像归属', '', '|scene_id|来源|许可|作者（原始 HTML/归属保留于 manifest）|', '|---|---|---|---|']
    for scene_id, row in sorted(media.items()):
        deps.append('|'+scene_id+'|['+clean(row['title'])+']('+row['source_page']+')|['+clean(row['license'])+']('+row['license_url']+')|'+clean(re.sub('<[^>]+>', '', row['author']))+'|')
    deps += ['', '只归档本轮访问的来源，不公开未使用的预留盲测标签。历史审计数据已标记 V2.1/V2.2，不能冒充新的模型结果。大日志、全部 `.blend` 与大几何 JSON 放 Release，关键指标和真实图片放 Git。未给整个仓库添加覆盖第三方代码/媒体的新许可证。', '',
        '可执行离线入口与原服务器续跑边界见 [COMMANDS_V2_4.md](COMMANDS_V2_4.md)。资源恢复和联网模型工作不属于离线重画。']
    (docs/'DEPENDENCIES_V2_4.md').write_text('\n'.join(deps)+'\n')
    upload = ['# V2.4 上传审查摘要', '', '仓库：[i025/scene](https://github.com/i025/scene)；分支：`'+BRANCH+'`。', '',
        ('归档提交：'+commit) if commit else '归档提交：pending。', '', publication, '',
        'README、docs/REVIEW_INDEX_V2_4.md、docs/AS_RUN_PROTOCOL_V2_4.md、'+EXPERIMENT+'/reports/REPORT_ZH.md 与 reports/index.html 是主要审查入口。核心数据位于 '+EXPERIMENT+'/metrics/，真实图位于 figures/。', '',
        *comparison, '', *selected_table, '', cost_text, '', question_text, '', representative_text, '', '## 完整附件', '', *links, '',
        '未上传项：'+('以 artifacts_index_v2_4.csv 为准；本脚本仅确认四包远端回执，不替代主任务的代码/图片远端读取。' if args.uploaded else '全部上传状态尚未由本摘要确认；完整包和本地提交保留，不声称已上传。'), '',
        '离线重画：`python scripts/offline_v2_4.py --experiment experiments/scene_rsi_v2_4 --output derived/v2_4_review`。',
        '同一冻结现场唯一续跑入口（本次归档文档生成不执行）：`OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" "$SCENE_PROJECT_ROOT/outputs/scene_rsi_v2_4/experiment.py" resume`。先将两个变量设为原实验环境 Python 与项目根目录；终态已存在时不新增研究，归档副本不能直接替代现场。', '',
        '归档说明是 as-run 整理，不伪造预注册；当前结果不足以单独支持可靠主动诊断研发优势、完整 RSI 贡献或自动元能力提升。']
    (repo/'UPLOAD_SUMMARY_V2_4.md').write_text('\n'.join(upload)+'\n')
    print(json.dumps({'written': ['README.md', 'UPLOAD_SUMMARY_V2_4.md', 'docs/AS_RUN_PROTOCOL_V2_4.md',
                                  'docs/REVIEW_INDEX_V2_4.md', 'docs/DEPENDENCIES_V2_4.md'],
                      'release_verified_flag': args.uploaded, 'commit_link': commit,
                      'representative_blend': artifact, 'new_model_calls': 0, 'new_render_frames': 0,
                      'created_UTC': datetime.now(timezone.utc).isoformat()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
