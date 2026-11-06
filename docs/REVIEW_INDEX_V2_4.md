# V2.4 审查索引

主张 → 对应代码 → 原始数据 → 图表 → 局限或缺失证据。此表不预先宣判方法有效。

|待审查主张|代码|原始数据|图表|局限|
|---|---|---|---|---|
|历史 H0 失败来源可区分|audit.py；audit_sources/audit_v21.py|metrics/H_failure_audit.csv；audit_sources/raw_failures/；audit_review.json|Figure 1|事后审计；部分构建子阶段和远端根因未知|
|主动探测真实执行并返回 M|meta.py plan_probes/plan_patch；experiment.py propose；inspect_blend.py|tasks/*/*/stage1.json、observations.json、stage2.json；真实 probe PNG/.blend|Figure 3|执行不等于成功区分原因；软残差兼容不是后验|
|改变的是共享 H|tasks/*/*/H/；policy.py.diff、system.txt.diff|candidate.json；coding/response.txt；新 results/ 记录；metrics/shared_H_diff_summary.csv、shared_H_diff_excerpt.json|Figure 4 联系表与真实 diff 摘录；完整 tasks/task01/active/policy.py.diff|编码者 observation_used 是自述，不证明诊断因果收益；摘录按固定案例选择，未按质量挑选|
|新的 Selection 与迁移收益|experiment.py run；analyze.py collect_candidates|configs/selection_freeze.json；metrics/scene_metrics.csv、candidates.csv|Figure 5|source 同图研发/筛选；实际 baseline-ineligible 分支偏离冻结文字；仅两个任务|
|机械编辑和结构保持|inspect_blend.py mechanical；regression.py|functional/mechanical.json、summary.json；metrics/actual_mechanical_preservation.csv|Figure 6 real edits 与结构校准|预定义机械操作；无文字编辑；自然几何真值缺失|
|全部研发成本与失败分母|backend/codex_wrapper.py；backend/runtime.py；analyze.py collect_costs|session/request/stdout JSONL/stderr；metrics/calls.csv、costs.csv|Figure 5|未知 usage 不补造；wall time 有包含关系，不宣称速度优势|

以上相对代码/数据路径均位于 [实验目录](../experiments/scene_rsi_v2_4/)。[中文报告](../experiments/scene_rsi_v2_4/reports/REPORT_ZH.md)、[图表来源表](../experiments/scene_rsi_v2_4/metrics/figure_sources.json)、[实现审计](../experiments/scene_rsi_v2_4/metrics/implementation_audit.json)、[审计脚本](../experiments/scene_rsi_v2_4/audit_results.py)、[历史报告器](../experiments/scene_rsi_v2_4/report_history/) 均保留。

**1. 为什么H0失败？哪些属于模型调用，哪些属于构造程序与执行复杂度，哪些尚不能确定？**

历史审计中 H0 共 20 次，失败类别 {"total_budget_exceeded": 7, "blender_build_error": 2, "model_call_timeout": 2, "blender_build_timeout": 3}。另有 r1/C2 的两次明确 CLI 路由/服务错误，不能算作 H0 的程序错误。原始日志区分连接故障、生成参数/World 错误，以及共享 600 秒预算截断；仅有 build_started 的超时不能定位为布尔重载或 GPU 问题。远端纯推理/排队、V2.1 具体 Blender 子阶段及增加预算后的可恢复性仍未知。

**2. 主动三维诊断是否被真正执行？是否形成了有区分性的观测？**

Active 正式完成 2 次探测；第二阶段 unresolved 2/2，启发式权重比 [1.048708021229195, 1.142104784555224]。实际观测进入可执行 M，但执行探测不等于区分原因。自然图像无故障真值，SSIM 敏感性和软兼容分数不是因果识别或后验概率。

**3. 这种观测是否改善了共享重建H的研发？是否比固定诊断更有效？**

严格有效修复为 Active 1/2、Fixed 2/2、Structured 2/2。保留全部点、功能与成本；每方法只有两个研发任务，重建使用独立远端采样，不能把这一小样本差异证明为可靠的主动诊断优势或普遍研发能力提升。

**4. 是否存在真实的跨场景收益？需要哪些进一步实验才能支持论文贡献？**

实际 Selection 选后迁移的条件质量差异和全预定失败效用差异见下表；它们只支持这些历史已暴露的房间及本次采样。需增加独立未暴露来源、独立选择集、匹配实际探测成本、重复模型采样、可识别的干预与结构/编辑回归，再验证下游共享 H 收益；本轮没有自动 M 后代或冻结元回放。

## 全部附件

- [active.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/active.tar.gz)，63897749 bytes
- [fixed.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/fixed.tar.gz)，67437377 bytes
- [shared-evidence.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/shared-evidence.tar.gz)，66406921 bytes
- [structured.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/structured.tar.gz)，56431924 bytes

代表工程按固定 task01、task02；H_start、Fixed、Structured、Active 顺序选择首个实际完成且文件存在的迁移输出，不挑赢家：`experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/scene.blend`；对应 [场景程序](../experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/build.py)。`.blend` 在完整 Release 包中，解压后可打开。
