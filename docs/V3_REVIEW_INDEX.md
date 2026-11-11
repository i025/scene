# V3实际证据审查索引

本索引不预判方法有效。当前终态、失败、缺测、上传及未完成项见[收尾摘要](../UPLOAD_SUMMARY_V3.md)；旧准备阶段索引另存带snapshot编号的副本。

| 主张 → 问题 | 对应代码 | 原始数据 → 图表 | 局限 |
|---|---|---|---|
| 共享H起点及实际候选 | [H_start](../experiments/scene_rsi_v3/fixed_h/historical_r1_C2_start/) / [所有候选](../experiments/scene_rsi_v3/candidates/) | [rounds](../experiments/scene_rsi_v3/metrics/rounds.csv) → [演化图](../experiments/scene_rsi_v3/figures/evolution.png) | 历史r1/C2不是original_H0，10轮是连续轨迹 |
| M决策、动作与后续实际执行 | [初始M](../experiments/scene_rsi_v3/initial_m/) / [研究接口](../experiments/scene_rsi_v3/research.py) | [动作表](../experiments/scene_rsi_v3/metrics/actions.csv) / [真实轨迹](../experiments/scene_rsi_v3/meta_traces/) → [研究链](../experiments/scene_rsi_v3/figures/research_chain.png) | 新动作、可执行后代和后续使用不是能力提高的充分证据 |
| Selection选择及独立Test覆盖 | [实际续跑平台](../experiments/scene_rsi_v3/code_snapshots/platform_A04/) / [报告整理差异](../experiments/scene_rsi_v3/REPORT_ADAPTATION_AFTER_ROUND10.md) | [逐生成](../experiments/scene_rsi_v3/metrics/scenes.csv) / [独立来源配对](../experiments/scene_rsi_v3/metrics/paired_test_sources.csv) → [原始点与差异](../experiments/scene_rsi_v3/figures/final_test_pairs.png) | 生成重复与视角不作独立来源，pending不填零；同模型评审偏差 |
| A01平台修订与真实公开输入 | [A01修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_01.md) / [A01源码](../experiments/scene_rsi_v3/code_snapshots/platform_A01/) | 旧001工程暂停退出143及新002续跑记录保留；已有10个H生成复用 | M0未变，修订在首个BW正式任务和首轮正式M前；旧偏离文档是历史记录 |
| A03评价器修复与中断重跑 | [A03修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_03.md) / [固定原生收集器](../experiments/scene_rsi_v3/eval_blend.py) | 旧score/facts/record全部保留，scenes.csv的primary_analysis区分原attempt；成本含全部失败与中断 | 发生在首个H-only提案后，不冒充pre-M；A03照明字段的评分抖动未重测 |
| A04研究证据编码修复 | [实际源码](../experiments/scene_rsi_v3/code_snapshots/platform_A04/) / [修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_04.md) | 第7轮失败包428577字节→无损紧凑JSON405383字节，9个实际面板与stub通过；0模型/Blender调用 | 原6轮、H/M、原始证据、评分与硬预算不变；不是自动M后代 |
| A05终测服务中断与续跑 | [续跑快照](../experiments/scene_rsi_v3/code_snapshots/platform_A05_postten_resume/) / [原始恢复证据](../experiments/scene_rsi_v3/preparation/service_recovery_01/) | [服务事件](../experiments/scene_rsi_v3/metrics/cli_service_events.csv) / [协议](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_05.md) | Connection refused后900秒超时保留；不重抽失败，不将传输失败归因为几何退化 |
| 结构与编辑保持 | [固定回归](../experiments/scene_rsi_v3/regression.py) / [文字编辑器](../experiments/scene_rsi_v3/semantic_edit.py) | [机械检查](../experiments/scene_rsi_v3/metrics/scenes.csv) / [文字编辑](../experiments/scene_rsi_v3/metrics/semantic_edit_summary.csv) → [实际前后图](../experiments/scene_rsi_v3/figures/semantic_edit_results.png) / [校准夹具](../experiments/scene_rsi_v3/preparation/functional_fixtures/index.html) | 文字编辑是否实际执行以逐任务状态为准；未完成不作通过结论，中心家具语义身份未独立验证，无自然图像3D真值 |
| 成本与失败来源 | [固定运行时](../experiments/scene_rsi_v3/backend/runtime.py) | [CLI](../experiments/scene_rsi_v3/metrics/cli_audit.csv) / [时序](../experiments/scene_rsi_v3/metrics/timing.csv) / [渲染证据](../experiments/scene_rsi_v3/metrics/render_evidence.csv) → [成本图](../experiments/scene_rsi_v3/figures/cost_and_timing.png) | 全局frame字段为预算扣额，实际精确帧总量未知；缺失usage不计为零 |

## 终测收尾与M07专项审查

| 主张 → 问题 | 对应代码 | 原始数据 → 图表 | 局限 |
|---|---|---|---|
| 24项原计划是否结算 | [A06恢复入口](../experiments/scene_rsi_v3/finish_test.py) / [修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_06.md) | [逐项状态](../experiments/scene_rsi_v3/metrics/final_test_schedule.csv) / [完整原始值](../experiments/scene_rsi_v3/metrics/final_test_raw.csv) → [全部来源与重复](../experiments/scene_rsi_v3/figures/final_test_contact_sheet.png) | 保留两项生成失败；已有生成结果只恢复尚未使用的固定评审重试，旧失败另存原件 |
| 六来源的收益和不确定性 | [统计脚本](../experiments/scene_rsi_v3/final_statistics.py) | [来源配对](../experiments/scene_rsi_v3/metrics/final_test_sources.csv) / [完整统计](../experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md) → [质量与八维](../experiments/scene_rsi_v3/figures/final_test_quality.png) | 事后补充的六来源bootstrap，小样本探索性；重复和视角不是独立来源，未用Test重新选H |
| 公共编辑执行器恢复 | [执行器](../experiments/scene_rsi_v3/semantic_edit.py) / [确定性恢复入口](../experiments/scene_rsi_v3/recover_edits.py) | [A07修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_07.md) / [真实恢复收据](../experiments/scene_rsi_v3/A07_EDIT_RECOVERY.json) / [编辑表](../experiments/scene_rsi_v3/metrics/semantic_edit_summary.csv) → [前后图](../experiments/scene_rsi_v3/figures/semantic_edit_results.png) | 四个原失败保留；每项共同增加一次相同程序执行，没有新增模型或人工编辑补丁；机械通过不等于语义准确 |
| M07真实修改及作用 | [M07差异](../experiments/scene_rsi_v3/candidates/C07/M.diff) / [动作源码](../experiments/scene_rsi_v3/candidates/C07/M/actions/appearance_audit.py) | [逐动作证据](../experiments/scene_rsi_v3/metrics/M07_action_review.csv) / [深入审查](../experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md) → [全部六次动作](../experiments/scene_rsi_v3/figures/M07_action_evidence.png) | meta.py未变；H04早于M07；H08拒绝、R9停止、H10拒绝，没有元能力增强证明 |
| 修正外部BW耗时覆盖 | [报告修订说明](../experiments/scene_rsi_v3/REPORT_ADAPTATION_FINAL_COMPLETION.md) | [耗时](../experiments/scene_rsi_v3/metrics/timing.csv) / [角色成本](../experiments/scene_rsi_v3/metrics/final_cost_by_role.csv) → [成本图](../experiments/scene_rsi_v3/figures/cost_and_timing.png) | 旧汇总漏读*_timing.json，旧表图保留；不叠加父子进程作用域，不把补日志解释成速度收益 |

归档只整理已存在产物，不调用模型/Blender、不补采样。实际执行H/M与冻结源码保留，整理版分析脚本单列。BW未获分发许可的原始参考及附件不公开；完整许可与上传状态见[附件索引](../artifacts_index_v3.csv)。

## 归档后离线审查

[完整终测解读、M07/A07、预算与数据边界](V3_FINAL_AUDIT_APPENDIX_ZH.md)；[回放当前检查](V3_META_REPLAY_FINAL_READINESS.json)。不改原评分、程序或选择。
