# V2.4 AS-RUN PROTOCOL（事后整理）

本文在实验结束后依据真实代码、配置、日志与数据整理，不冒充严格预注册。原始冻结文件 [protocol.md](../experiments/scene_rsi_v2_4/protocol.md)、[freeze.json](../experiments/scene_rsi_v2_4/configs/freeze.json) 和 [formal_frozen 快照](../experiments/scene_rsi_v2_4/code_snapshots/formal_frozen/) 保持原样。

## 实际执行设置

- 本轮从 V2.1 r1/C2 的共享 H_start 出发；`fixed_h/H0` 仅保存原始起点源码，没有作为本轮新评估对照。三组是 Scene-RSI 内部机制对照，不是重跑 SceneEvolve/Hyperagents 的 RSI 基线。
- 源图先用于诊断和编码，再作为名为 Selection 的同图研发/筛选；不属于独立验证。另一房间 transfer 在候选与选择冻结后新执行，但图像曾在 V2.2 暴露，不能称全新盲测。
- 冻结文字要求源 Q 提升 >0.01；实际 runner 在 H_start 功能资格失败时接受任意合格候选，即使 H_start 有有效 Q。保留实际选择，`selection_strict_gain_disagreement` 记录偏离，不事后改选。严格有效修复的额外派生条件仍为：源合格且 ΔQ>0.01，迁移合格且 ΔQ≥-0.01。
- 每种方法只有两个研发任务，每个 H/图仅一次新重建，模型远端采样未被本地种子控制，也未量化其波动。各组初诊独立采样，不把质量差异唯一归因于探测。条件质量均值只含成功案例，执行失败且没有测量时 Q 保持 null，失败效用单独记零并保留全部预定分母；多视角不是独立重复。
- 报告整理时目视可见 task01 新 H_start 的厨房迁移图近乎全黑，Q 约 0.195，仍执行成功且机械功能合规。原图和分数保留，不重采样；这个低基线放大了该场景的配对增益，限制均值的普遍解释。目视标注不改变评分或选择规则。
- M 是工程修订，无自动后代、无跨代能力提升或陌生 H 起点冻结元回放。全部最终编辑为机械操作，不存在文字指令编辑能力结果。
- 最早烟测在修正对象 ID 契约之前的完整源码快照未保存，无法逐字确认；其真实请求、响应和错误记录保留。smoke_initial_menu 快照形成于该修正后，不冒充修正前版本。正式冻结代码与六个候选保存完整，并已核对候选源码等于实际编码响应。
- 实际模型角色由 calls.csv 决定：initial_diagnosis/shared_H_patch 使用 gpt-6-astra medium，student 使用 gpt-6.1-sol medium。record.model_roles 中 editor/judge 是沿用但未执行的元数据，不能计为实际编辑器或独立视觉评审。
- 元诊断/共享修改 CLI 单次 600 秒；student 单次至多 300 秒且受内层剩余时间限制；内层总计 600 秒、最多 3 次调用/2 次执行。数值指标与外层功能检查在内层期限外另行执行，不把全部耗时误写为 600 秒以内。
- M 的平均归一化残差 ≤3 是软兼容阈值，不要求严格区间命中；指数权重比不是后验概率。所有假设的软残差均超阈值时保留 unresolved，不把 Q 或 SSIM 改善当唯一原因。

- 固定起点和各 H 变体：`fixed_h/r1_C2/{policy.py,system.txt}`；6 个独立工作区位于 `tasks/task01|task02/fixed|structured|active/H/`，保存真实 diff。M 为 `meta.py`；SceneAct/渲染/外部指标/资源控制不由候选修改。
- 三组共同拥有原始图像、历史 P/渲染、对象/层级、结构及执行信息，都是最多两个探测和一次 H 提案。Fixed 取固定相机/尺度，Structured 不探测，Active 用事前预测排序。实际探测数和不同模型采样成本分别报告，不声称严格实耗相等。
- Codex 使用全新 ephemeral 会话、真实图像附件、只读工作区与固定禁用工具；无隐藏共享对话、网页搜索或额外 subagent。模型只返回内容，runner 显式执行代码/Blender/修复。输入、stdout JSONL、stderr、usage 与实际请求参数全部留存。
- 五类工具：camera_focal、camera_tilt、object_scale、object_depth、isolate；临时副本执行。固定 ROI 下 outcome=0.5×全图 ΔSSIM+0.5×ROI ΔSSIM，预测在操作前保存。最多两个，不根据输赢增加预算。
- 渲染为 Cycles、512 长边、16 samples、AgX、seed42；CPU 两线程、单重任务。低质量确定性工具校准另标，排除正式图像质量对比。
- 主 Q 沿用 `(clip(SSIM,0,1)+1-clip(LPIPS,0,1)+(1+clip(DINO,-1,1))/2)/3`；PSNR 另报。缺测保留 null，不用语言模型猜数值。
- 代码冻结后先 source/同图 Selection，统一保存选择，再新执行另一房间 transfer；测试结果未用于这一轮重新提案。实际访问顺序保留在日志与 selection_freeze 中；由于历史暴露，不声称严格盲测。

## 原始事实与事后派生分析

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

P：各场景新生成的 build.py；H：跨图像复用的 policy.py/system.txt；M：工程编写并实际执行的两阶段策略。H-only 提案不算自动 M 自修改。记录模型中 editor/judge 字段的存在不代表这些调用实际发生。

全部选择保留实际分支，严格有效修复及配对 ΔQ 是透明的事后派生统计。不能把 source/Selection 重叠掩盖为独立验证，也不能把归档修订的报告器替换成实验时 H/M/评价器；原代码与 report_history 均保留。

结构门槛分别保存 required/applicable/measured_pass/gate_pass。机械材质/组合移动和声明部件完整性不是语义三维真值；AABB 支撑近似与三角面交叉的限制见原始报告。没有文字编辑器、没有不可见区域恢复精度或新视角真值。

## 未执行与偏离

未开展自动 M 后代、冻结元能力回放、SceneEvolve/Hyperagents 演化或 BlenderWorld 全量测试。准备期无效对象、旧菜单无可区分预测等记录完整保留，费用计入新预算。没有因正负结果扩大上限。

现场仍存在的失败/缺测按 scene_metrics 与 failure 日志报告；终态不代表所有任务成功。发布、重画不调用模型或重跑重建。
