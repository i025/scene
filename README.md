# Scene-RSI V2.4：自然图像共享 H 诊断与修复先导实验

研究问题：三维主动实验的真实观测是否帮助修改跨图像复用的重建流程，而不仅是修好某张图的 P？

分支：`research/scene-rsi-v2.4`。本地归档已整理；推送与 Release 上传状态尚未确认，不声称已上传。

归档提交链接：pending，由实际提交后补充。

已完成范围：2 个自然图像研发任务 × 3 种方法 × 1 个 H 提案，计划 16 个新重建任务；所有真实成功、失败、拒绝与未选候选均保留。

## 实际结果

|方法|执行成功/预定|功能通过/预定|失败/未执行|真实提案/预定|源条件 Q (n)|迁移条件 Q (n)|严格有效修复|
|---|---|---|---|---|---|---|---|
|新 H_start|4/4|4/4|0/0|N/A|0.3488 (2)|0.3235 (2)|N/A|
|Fixed|4/4|4/4|0/0|2/2|0.3911 (2)|0.5149 (2)|2/2|
|Structured|4/4|4/4|0/0|2/2|0.3725 (2)|0.4955 (2)|2/2|
|Active|4/4|4/4|0/0|2/2|0.3640 (2)|0.4873 (2)|1/2|

|方法|选后 Test ΔQ（双方执行成功）|有效配对 n / 全预定|全预定失败效用差均值|
|---|---|---|---|
|Fixed|0.1914|2/2|0.1914|
|Structured|0.1721|2/2|0.1721|
|Active|0.1398|2/2|0.1398|

选后 ΔQ 按实际 selection_freeze 选择计算；原始候选迁移另见 candidates.csv。条件 ΔQ 不包含任何填零的视觉测量，全预定效用差则保留执行失败分母。

## 四个问题的证据回答

**1. 为什么H0失败？哪些属于模型调用，哪些属于构造程序与执行复杂度，哪些尚不能确定？**

历史审计中 H0 共 20 次，失败类别 {"total_budget_exceeded": 7, "blender_build_error": 2, "model_call_timeout": 2, "blender_build_timeout": 3}。另有 r1/C2 的两次明确 CLI 路由/服务错误，不能算作 H0 的程序错误。原始日志区分连接故障、生成参数/World 错误，以及共享 600 秒预算截断；仅有 build_started 的超时不能定位为布尔重载或 GPU 问题。远端纯推理/排队、V2.1 具体 Blender 子阶段及增加预算后的可恢复性仍未知。

**2. 主动三维诊断是否被真正执行？是否形成了有区分性的观测？**

Active 正式完成 2 次探测；第二阶段 unresolved 2/2，启发式权重比 [1.048708021229195, 1.142104784555224]。实际观测进入可执行 M，但执行探测不等于区分原因。自然图像无故障真值，SSIM 敏感性和软兼容分数不是因果识别或后验概率。

**3. 这种观测是否改善了共享重建H的研发？是否比固定诊断更有效？**

严格有效修复为 Active 1/2、Fixed 2/2、Structured 2/2。保留全部点、功能与成本；每方法只有两个研发任务，重建使用独立远端采样，不能把这一小样本差异证明为可靠的主动诊断优势或普遍研发能力提升。

**4. 是否存在真实的跨场景收益？需要哪些进一步实验才能支持论文贡献？**

实际 Selection 选后迁移的条件质量差异和全预定失败效用差异见下表；它们只支持这些历史已暴露的房间及本次采样。需增加独立未暴露来源、独立选择集、匹配实际探测成本、重复模型采样、可识别的干预与结构/编辑回归，再验证下游共享 H 收益；本轮没有自动 M 后代或冻结元回放。

## 方法与结论边界

- 本轮从 V2.1 r1/C2 的共享 H_start 出发；`fixed_h/H0` 仅保存原始起点源码，没有作为本轮新评估对照。三组是 Scene-RSI 内部机制对照，不是重跑 SceneEvolve/Hyperagents 的 RSI 基线。
- 源图先用于诊断和编码，再作为名为 Selection 的同图研发/筛选；不属于独立验证。另一房间 transfer 在候选与选择冻结后新执行，但图像曾在 V2.2 暴露，不能称全新盲测。
- 冻结文字要求源 Q 提升 >0.01；实际 runner 在 H_start 功能资格失败时接受任意合格候选，即使 H_start 有有效 Q。保留实际选择，`selection_strict_gain_disagreement` 记录偏离，不事后改选。严格有效修复的额外派生条件仍为：源合格且 ΔQ>0.01，迁移合格且 ΔQ≥-0.01。
- 每种方法只有两个研发任务，每个 H/图仅一次新重建，模型远端采样未被本地种子控制，也未量化其波动。各组初诊独立采样，不把质量差异唯一归因于探测。条件质量均值只含成功案例，执行失败且没有测量时 Q 保持 null，失败效用单独记零并保留全部预定分母；多视角不是独立重复。
- 报告整理时目视可见 task01 新 H_start 的厨房迁移图近乎全黑，Q 约 0.195，仍执行成功且机械功能合规。原图和分数保留，不重采样；这个低基线放大了该场景的配对增益，限制均值的普遍解释。目视标注不改变评分或选择规则。
- M 是工程修订，无自动后代、无跨代能力提升或陌生 H 起点冻结元回放。全部最终编辑为机械操作，不存在文字指令编辑能力结果。
- 实际模型角色由 calls.csv 决定：initial_diagnosis/shared_H_patch 使用 gpt-6-astra medium，student 使用 gpt-6.1-sol medium。record.model_roles 中 editor/judge 是沿用但未执行的元数据，不能计为实际编辑器或独立视觉评审。
- 元诊断/共享修改 CLI 单次 600 秒；student 单次至多 300 秒且受内层剩余时间限制；内层总计 600 秒、最多 3 次调用/2 次执行。数值指标与外层功能检查在内层期限外另行执行，不把全部耗时误写为 600 秒以内。
- M 的平均归一化残差 ≤3 是软兼容阈值，不要求严格区间命中；指数权重比不是后验概率。所有假设的软残差均超阈值时保留 unresolved，不把 Q 或 SSIM 改善当唯一原因。

## 真实可视化

统计单位是研发任务或新重建任务；源/迁移图按固定顺序展示全部输出，空白是真实缺失，不用历史图替代新 H_start。

![历史 H0 与生成执行失败审计](experiments/scene_rsi_v2_4/figures/figure1_failure_audit.png)

![真实三维探测、事前预测与 M 观测更新](experiments/scene_rsi_v2_4/figures/figure3_actual_diagnostics.png)

![全部四场景：本轮新 H_start 与三个原始候选](experiments/scene_rsi_v2_4/figures/figure4_fresh_reconstructions.png)

![两个迁移场景：按冻结选择展示实际 H*，包含 H_start 回退](experiments/scene_rsi_v2_4/figures/figure4_selected_transfer.png)

![固定首个 Active 案例的真实 H diff 摘录与全部候选修改计数](experiments/scene_rsi_v2_4/figures/figure4_shared_H_diff.png)

![原始 Q、六个配对点与实际成本](experiments/scene_rsi_v2_4/figures/figure5_results_cost.png)

![两个预选迁移场景的机械编辑与非目标保持](experiments/scene_rsi_v2_4/figures/figure6_real_edit_preservation.png)

源图诊断输入与旧 V2.2 渲染单独见 [Figure 2](experiments/scene_rsi_v2_4/figures/figure2_natural_diagnosis_inputs.png)；它们不是本轮新 H_start 的数值结果。已知结构错误检测见 [Figure 6](experiments/scene_rsi_v2_4/figures/figure6_structural_calibration.png)。

## 成本与原始证据

本轮新增 CLI 54/80；已知输入 2040784、输出 252990 token；usage 缺失 0。渲染尝试上界 101/240，完成 100。CPU 两线程、单重任务、GPU 0。新增全局预算和调用总数包含全部 10 次准备/烟测调用；每方法正式曲线不含这些共同准备费用及新 H_start，二者另表单列。历史复制日志不计新增。外层工程对话和固定模型服务基础设施成本不可观测、未定价，不声称各方法总研发实耗相等。模型、流水线与 Blender wall time 互有包含，不相加或据此声称算法速度优势；美元费用未知。

|成本组|CLI 会话|已知输入/输出 token|usage 缺失|探测 Blender 秒|重建流水线秒|
|---|---|---|---|---|---|
|fixed|12|475535/56258|0|45.0786|1635.6549|
|structured|12|465528/64495|0|0|1670.5621|
|active|12|425161/52286|0|22.5116|1245.6472|
|common_H_start|8|196992/46119|0|0|1475.7934|
|smoke|10|477568/33832|0|11.4820|728.2418|
|preparation|0|0/0|0|0|0|

- [中文报告](experiments/scene_rsi_v2_4/reports/REPORT_ZH.md) / [离线 HTML](experiments/scene_rsi_v2_4/reports/index.html)
- [逐场景原始指标](experiments/scene_rsi_v2_4/metrics/scene_metrics.csv) / [六候选](experiments/scene_rsi_v2_4/metrics/candidates.csv) / [调用](experiments/scene_rsi_v2_4/metrics/calls.csv)
- [分阶段模型成本](experiments/scene_rsi_v2_4/metrics/costs_by_phase.csv)：共享 H 研发、源图重建、迁移推理和准备烟测分别列出。迁移成本包含预定的原始未选候选评价。
- [事前预测](experiments/scene_rsi_v2_4/metrics/forecasts.csv) / [实际观测](experiments/scene_rsi_v2_4/metrics/probe_observations.json) / [图表来源](experiments/scene_rsi_v2_4/metrics/figure_sources.json)
- [事后审查索引](docs/REVIEW_INDEX_V2_4.md) / [as-run protocol](docs/AS_RUN_PROTOCOL_V2_4.md) / [离线命令](docs/COMMANDS_V2_4.md)

代表工程按固定 task01、task02；H_start、Fixed、Structured、Active 顺序选择首个实际完成且文件存在的迁移输出，不挑赢家：`experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/scene.blend`；对应 [场景程序](experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/build.py)。`.blend` 在完整 Release 包中，解压后可打开。

## 完整附件

- 四个完整附件仍为 pending；本地工作目录 `work/scene_v2_4_archive/bundles/`。

全部路径与附件状态见 [artifacts_index_v2_4.csv](artifacts_index_v2_4.csv)。完整 stdout/JSONL、全部 `.blend`、大几何 JSON 按四包保留；普通 Git 提供关键代码、配置、原始表和真实图片。

旧版入口：[V2.3 原提交 README](https://github.com/i025/scene/blob/d72817b0d90e9ecc5e156344128bacf76317e25e/README.md)；未经改写的本地文本另存 `docs/README_V2_3_CHECKPOINT_d72817b.md`，其相对链接仍以原仓库根为基准。V1/V2/V2.1/V2.2/V2.3 的实验和原始分数保持原样。未为第三方代码、Commons 图片或模型另加覆盖性许可证。
