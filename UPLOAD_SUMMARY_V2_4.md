# V2.4 上传审查摘要

仓库：[i025/scene](https://github.com/i025/scene)；分支：`research/scene-rsi-v2.4`。

归档提交：https://github.com/i025/scene/commit/4f23a8ba4513dc199f113f66b8ce969dd067b17c

完整四包 Release 已有远端资产列表确认；提交链接由主任务核对。

README、docs/REVIEW_INDEX_V2_4.md、docs/AS_RUN_PROTOCOL_V2_4.md、experiments/scene_rsi_v2_4/reports/REPORT_ZH.md 与 reports/index.html 是主要审查入口。核心数据位于 experiments/scene_rsi_v2_4/metrics/，真实图位于 figures/。

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

本轮新增 CLI 54/80；已知输入 2040784、输出 252990 token；usage 缺失 0。渲染尝试上界 101/240，完成 100。CPU 两线程、单重任务、GPU 0。新增全局预算和调用总数包含全部 10 次准备/烟测调用；每方法正式曲线不含这些共同准备费用及新 H_start，二者另表单列。历史复制日志不计新增。外层工程对话和固定模型服务基础设施成本不可观测、未定价，不声称各方法总研发实耗相等。模型、流水线与 Blender wall time 互有包含，不相加或据此声称算法速度优势；美元费用未知。

**1. 为什么H0失败？哪些属于模型调用，哪些属于构造程序与执行复杂度，哪些尚不能确定？**

历史审计中 H0 共 20 次，失败类别 {"total_budget_exceeded": 7, "blender_build_error": 2, "model_call_timeout": 2, "blender_build_timeout": 3}。另有 r1/C2 的两次明确 CLI 路由/服务错误，不能算作 H0 的程序错误。原始日志区分连接故障、生成参数/World 错误，以及共享 600 秒预算截断；仅有 build_started 的超时不能定位为布尔重载或 GPU 问题。远端纯推理/排队、V2.1 具体 Blender 子阶段及增加预算后的可恢复性仍未知。

**2. 主动三维诊断是否被真正执行？是否形成了有区分性的观测？**

Active 正式完成 2 次探测；第二阶段 unresolved 2/2，启发式权重比 [1.048708021229195, 1.142104784555224]。实际观测进入可执行 M，但执行探测不等于区分原因。自然图像无故障真值，SSIM 敏感性和软兼容分数不是因果识别或后验概率。

**3. 这种观测是否改善了共享重建H的研发？是否比固定诊断更有效？**

严格有效修复为 Active 1/2、Fixed 2/2、Structured 2/2。保留全部点、功能与成本；每方法只有两个研发任务，重建使用独立远端采样，不能把这一小样本差异证明为可靠的主动诊断优势或普遍研发能力提升。

**4. 是否存在真实的跨场景收益？需要哪些进一步实验才能支持论文贡献？**

实际 Selection 选后迁移的条件质量差异和全预定失败效用差异见下表；它们只支持这些历史已暴露的房间及本次采样。需增加独立未暴露来源、独立选择集、匹配实际探测成本、重复模型采样、可识别的干预与结构/编辑回归，再验证下游共享 H 收益；本轮没有自动 M 后代或冻结元回放。

代表工程按固定 task01、task02；H_start、Fixed、Structured、Active 顺序选择首个实际完成且文件存在的迁移输出，不挑赢家：`experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/scene.blend`；对应 [场景程序](experiments/scene_rsi_v2_4/results/task01/reference/H_start/test/commons_192968130/build.py)。`.blend` 在完整 Release 包中，解压后可打开。

## 完整附件

- [active.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/active.tar.gz)，63897749 bytes
- [fixed.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/fixed.tar.gz)，67437377 bytes
- [shared-evidence.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/shared-evidence.tar.gz)，66406921 bytes
- [structured.tar.gz](https://github.com/i025/scene/releases/download/scene-rsi-v2.4-2026-11-06/structured.tar.gz)，56431924 bytes

未上传项：以 artifacts_index_v2_4.csv 为准；本脚本仅确认四包远端回执，不替代主任务的代码/图片远端读取。

离线重画：`python scripts/offline_v2_4.py --experiment experiments/scene_rsi_v2_4 --output derived/v2_4_review`。
同一冻结现场唯一续跑入口（本次归档文档生成不执行）：`OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" "$SCENE_PROJECT_ROOT/outputs/scene_rsi_v2_4/experiment.py" resume`。先将两个变量设为原实验环境 Python 与项目根目录；终态已存在时不新增研究，归档副本不能直接替代现场。

归档说明是 as-run 整理，不伪造预注册；当前结果不足以单独支持可靠主动诊断研发优势、完整 RSI 贡献或自动元能力提升。
