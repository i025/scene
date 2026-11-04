# 证据审查索引

本索引组织可检查的证据，不预先判定方法有效。以下路径相对本文件。大文件需从 [Release](https://github.com/i025/scene/releases/tag/scene-rsi-pilot-2026-11-04) 解压到仓库根；成员清单、大小和上传状态见 [artifacts_index.csv](../artifacts_index.csv)。

|主张/待审问题|对应代码|原始数据|图表|局限或缺失证据|
|---|---|---|---|---|
|四组从同一未演化H0出发|[H0](../experiments/scene_rsi_pilot/backend/harnesses/baseline/)、[pilot.py](../experiments/scene_rsi_pilot/pilot.py)、[映射](../experiments/scene_rsi_pilot/baseline_mapping.md)|[config](../experiments/scene_rsi_pilot/config.json)、[选择档案](../experiments/scene_rsi_pilot/archive.json)、[全部88槽](../experiments/scene_rsi_pilot/reports/main_scheduled.csv)|[r1全部测试](../experiments/scene_rsi_pilot/reports/comparison_r1.png)、[r2](../experiments/scene_rsi_pilot/reports/comparison_r2.png)|探索性数据；适配基线不等于论文协议；失败格不替换。|
|所选H的测试条件收益|[analyze.py](../experiments/scene_rsi_pilot/analyze.py)、[evaluate.py](../experiments/scene_rsi_pilot/backend/evaluate.py)|[逐对数据](../experiments/scene_rsi_pilot/reports/paired.csv)、[有效改进](../experiments/scene_rsi_pilot/reports/effective_improvement.csv)、[原始逐场景](../experiments/scene_rsi_pilot/metrics/scene_metrics.csv)|[全部配对点](../experiments/scene_rsi_pilot/reports/effective_improvement.png)、[终测质量](../experiments/scene_rsi_pilot/reports/terminal_quality.png)|r1仅2/4、r2仅3/4有效配对；2重复，完整有效改进均未达标；不作显著性/普遍优势结论。|
|成本和失败分母完整保留|[budget.py](../experiments/scene_rsi_pilot/backend/budget.py)、[归档计数脚本](../scripts/archive_tables.py)|[ledger](../experiments/scene_rsi_pilot/ledger.json)、[calls](../experiments/scene_rsi_pilot/reports/calls.csv)、[全部尝试](../experiments/scene_rsi_pilot/reports/service_attempts.csv)、[运行表](../experiments/scene_rsi_pilot/metrics/runs.csv)|[研发成本/收益](../experiments/scene_rsi_pilot/reports/rd_cost_gain.png)、[主计划完成状态](../experiments/scene_rsi_pilot/figures/main_completion.png)|596会话含2次初始日志损失，87 usage未知；混合设备wall不作算法速度比较。完成状态图源为metrics/method_completion.csv，单位是88逻辑槽。|
|M后代真的参与了后续研发|[初始M](../experiments/scene_rsi_pilot/initial_meta/)、[候选H/M](../experiments/scene_rsi_pilot/candidates/)、[strategies.py](../experiments/scene_rsi_pilot/strategies.py)|[参与证据](../experiments/scene_rsi_pilot/quota_restored_20261103/meta_program_participation.json)、[analysis](../experiments/scene_rsi_pilot/reports/analysis.json)、各C2/meta_execution.json|[冻结M结果](../experiments/scene_rsi_pilot/reports/frozen_meta_replay.png)|有实际后代不等于元能力提高；逐调用完整工程快照并非全部保存。|
|冻结M从相同陌生H起点研发|[replay.py](../experiments/scene_rsi_pilot/replay.py)、[冻结M源码/diff](../experiments/scene_rsi_pilot/replay_programs/)|[协议](../experiments/scene_rsi_pilot/replay_protocol.json)、[配对表](../experiments/scene_rsi_pilot/reports/frozen_meta_paired.csv)、[实际执行核对](../experiments/scene_rsi_pilot/service_incident_03/frozen_M_execution_check.json)|[回放对照](../experiments/scene_rsi_pilot/reports/frozen_meta_comparison.png)|一个起点、每M一次提案、一个共享测试场景；均选H_start，增益0；不是上涨曲线。|
|诊断探测怎样影响提案|[策略](../experiments/scene_rsi_pilot/strategies.py)、[证据整理](../experiments/scene_rsi_pilot/model_evidence.py)、[候选diff](../experiments/scene_rsi_pilot/candidates/r1/scene_rsi_pilot/C1/changes.diff)|[真实观测](../experiments/scene_rsi_pilot/candidates/r1/scene_rsi_pilot/C1/diagnostic_observations.json)、meta_execution、probes及proposal_result|[Ours首候选诊断板](../experiments/scene_rsi_pilot/reports/diagnostic_r1_scene_rsi_pilot_C1.png)|按已保存诊断顺序展示；映射unknown保留；敏感性不是充分因果归因；该候选未必被选中。|
|结构可操作与局部编辑保持|[inspect_blend.py](../experiments/scene_rsi_pilot/inspect_blend.py)、[text_edit_worker.py](../experiments/scene_rsi_pilot/text_edit_worker.py)|[结构/机械数据](../experiments/scene_rsi_pilot/reports/functional.csv)、[文字编辑](../experiments/scene_rsi_pilot/reports/text_edit.csv)、[预用控制](../experiments/scene_rsi_pilot/text_editor_preuse_check/)|[固定多视角](../experiments/scene_rsi_pilot/reports/multiview_r1.png)、[文字编辑前后](../experiments/scene_rsi_pilot/reports/text_edit_r1_commons_155212263.png)|预定首测试场景/前2文字编辑任务，含失败；机械操作不同于文本能力；无3D真值，AABB仅近似，语义目标匹配有局限。|
|三消融为独立生成而非共享候选池|[extras.py](../experiments/scene_rsi_pilot/extras.py)、[ablation_initial](../experiments/scene_rsi_pilot/ablation_initial/)|[协议](../experiments/scene_rsi_pilot/ablation_protocol.json)、[全部终测](../experiments/scene_rsi_pilot/reports/ablation_terminal.csv)、[共同配对覆盖](../experiments/scene_rsi_pilot/reports/ablation_pair_coverage.csv)|[消融全场景](../experiments/scene_rsi_pilot/reports/ablation_comparison_ablation_r1.png)|10/12有效；所有条件共同有效配对0；不能凭不同条件均值宣称机制增益。|
|BlenderWorld外部任务真实执行|[external.py](../experiments/scene_rsi_pilot/external.py)、[原阶段适配](../experiments/scene_rsi_pilot/external_budget_adaptation/)、[后续冻结](../experiments/scene_rsi_pilot/external_followup_preuse/)|[第一阶段](../experiments/scene_rsi_pilot/reports/blenderworld_adapted.csv)、[独立后续](../experiments/scene_rsi_pilot/reports/blenderworld_followup_adapted.csv)、两阶段status|[bw0005](../experiments/scene_rsi_pilot/reports/blenderworld_adapted_comparison.png)、[bw0011含失败](../experiments/scene_rsi_pilot/reports/blenderworld_followup_adapted_comparison.png)|adapted evaluation、非官方榜单；3/4重建有效，两个阶段均无完整评审评分配对。|

## 文件与统计单位

- 主表：[运行](../experiments/scene_rsi_pilot/metrics/runs.csv)、[12个主候选](../experiments/scene_rsi_pilot/metrics/candidates.csv)、[全部历史/当前提案及无结果准备目录](../experiments/scene_rsi_pilot/metrics/all_candidate_attempts.csv)、[125条场景记录](../experiments/scene_rsi_pilot/metrics/scene_metrics.csv)。125包含2个smoke及复用别名，不是125个独立场景。
- 每张统计PNG通常由同名CSV/JSON提供来源；成本、配对、功能、消融、回放分别由原analyze.py/report.py绘制。诊断/比较/多视角/编辑联系表有同名JSON，文字/机械细节另在text_edit.csv、functional.csv。smoke_evidence取自smoke/*/record.json，不算正式统计。
- 主图r1/r2按原清单全部4测试场景顺序，不挑赢家；固定多视角按预定首场景；编辑按预定前2场景；多视角不是独立样本。README案例包含成功和空白失败格。
- 全部.blend、逐次step程序/图、几何JSON、真实图像附件、prompt、JSONL、stderr、response、usage在27个Release分包。索引说明其成员位置；不只覆盖胜者。
- 原始日志保留本机未脱敏版本；公开副本替换账户路径、隐藏5条未用预留数据，不删除失败或成本。见[脱敏清单](REDACTIONS.json)。2次原始CLI日志未保存，不补造。

## 重算入口

先从Release下载全部tar.gz并在仓库根解压，然后使用既有Python环境：

```bash
python scripts/offline_report.py --output derived/offline_01
python scripts/archive_tables.py
```

第一条在新目录重算/重画，不覆盖归档报告；第二条从原始冻结表重新生成归档运行/候选表和完成状态图。只需Pillow/numpy/matplotlib，不执行模型、Blender或指标前向。检查记录见[OFFLINE_VERIFICATION.json](OFFLINE_VERIFICATION.json)。实验续跑另见README，本次未执行。
