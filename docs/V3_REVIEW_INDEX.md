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
| 结构与编辑保持 | [固定回归](../experiments/scene_rsi_v3/regression.py) / [文字编辑器](../experiments/scene_rsi_v3/semantic_edit.py) | [机械检查](../experiments/scene_rsi_v3/metrics/scenes.csv) / [文字编辑](../experiments/scene_rsi_v3/metrics/semantic_edit_summary.csv) → [实际前后图](../experiments/scene_rsi_v3/figures/semantic_edit_results.png) / [校准夹具](../experiments/scene_rsi_v3/preparation/functional_fixtures/index.html) | 文字编辑流程真实执行；中心家具语义身份未独立验证，无自然图像3D真值 |
| 成本与失败来源 | [固定运行时](../experiments/scene_rsi_v3/backend/runtime.py) | [CLI](../experiments/scene_rsi_v3/metrics/cli_audit.csv) / [时序](../experiments/scene_rsi_v3/metrics/timing.csv) / [渲染证据](../experiments/scene_rsi_v3/metrics/render_evidence.csv) → [成本图](../experiments/scene_rsi_v3/figures/cost_and_timing.png) | 全局frame字段为预算扣额，实际精确帧总量未知；缺失usage不计为零 |

归档只整理已存在产物，不调用模型/Blender、不补采样。实际执行H/M与冻结源码保留，整理版分析脚本单列。BW未获分发许可的原始参考及附件不公开；完整许可与上传状态见[附件索引](../artifacts_index_v3.csv)。
