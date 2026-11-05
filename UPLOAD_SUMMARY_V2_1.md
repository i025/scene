# Scene-RSI V2.1 完成与上传摘要

## 仓库和实际上传状态

目标：https://github.com/i025/scene ，本地分支 `research/scene-rsi-v2.1`。实验归档提交 **`a3e73b98a6a6ca574fc23edec705b5c912b5cd29`** 已在本地保存；本摘要可由后续小提交保存，不制造自指循环。

**新分支未推送，Release未创建、7附件未上传。没有可用的远端提交或附件链接。** 已实际尝试HTTP/1.1推送；TLS证书校验通过，但GitHub返回401，Git凭据助手无可用凭据，非交互终端不能读取用户名。既有SSH读取也因主机名解析失败不可用，没有关闭证书或主机校验。失败收据见docs/V2_1_UPLOAD_ATTEMPT.json。远端可读取的V2仍为79f5b54；没有覆盖旧分支。

这是认证阻塞，不是实验仍在后台，也不是模型服务导致未做终测。用户需在服务器终端恢复GitHub认证，不能把Token发到聊天。原有本地认证说明文件未提交。

## 实际完成范围

只运行Scene-RSI与共同H0。1 Development、1 Selection、2 Test来源，2个独立研发，每次K=2。开始前确认旧V2已退出：13条正式记录、0正式候选、Test未开始；其旧数据和分数保留，不重复启动V2。

|方法|完整研发/评价重复|实际新候选|正式任务记录|成功|失败|
|---|---:|---:|---:|---:|---:|
|fixed_h0|2|0（同一固定H0）|8|2|6|
|scene_rsi_v2_1|2|4|12|7|5|

20个正式预定任务全部有终态；9个成功产物均有实际打开校验。11个正式失败的观察阶段为10个Blender执行、1个Codex调用超时，不能统称服务故障或纯算法退化。另有2个烟测任务（1成功1失败），4次超包失败发生在候选模型提交前，没有产生候选；不将这些失败副本计作额外H后代。

4个真实候选均H-only，M源码变化0。H-only/M-only/H+M接口都通过确定性测试，但本轮没有真实M后代参与后续研发，未发生元级程序自修改。没有冻结M回放或MetaImp图。

## 主要修复与机制测试

- pilot.py：先检查执行与必要功能绝对资格，再按固定Q排序；保留H0回退，但H0失败不放宽门槛。required/applicable/measured_pass/gate_pass分别保存。
- strategies.py、diagnostics.py、inspect_blend.py：真实图像差异关联真实对象/投影，明确预算；失败分阶段，无有效blend不做几何探测。实际观测返回可执行plan_patch，保留两阶段决策。
- model_evidence.py：真实大场景证据超过600KB时的运行修订，保留全部ID、限制128份详细测量，未改H0/M0/门槛/总预算；所有受影响提案统一重做，原失败完整保存。
- analyze.py：pending不写0%，失败原始Q保持null，单独任务效用、全预定分母、条件质量、配对质量、失败阶段和累计成本。旧衍生报告保存于report_history。

预算、指定对象、观测后决策、绝对资格/12种门槛组合、M控制回归、M-only实际执行stub均通过；tests/contracts.json的前七项通过。8个真实Blender校准结果符合预期，包括正确组合、脱离/缺失部件、支撑损坏、共享材质误改、安全局部编辑、组合移动、三角表面相交。

已知故障机制比较：四个需要对象的夹具，固定启发式/V2.1定位为2/4与4/4；相机无对象，双方均请求相机探测。相关模块定位1/5与5/5，但M第二阶段精确模块命中双方均仅1/5。旧宽泛计数保留，修正仅在衍生列。双方辅助共享helper修复的迁移测试都5/5（损坏起点0/5），API契约提供提示；V2.1多5次视觉定位调用，不是等实际计算量优势，也不是自然图像RSI提升证明。

## H与M轨迹及Selection

|研发|候选|共享修改|Dev Q|Selection Q|资格/选择|M变化|
|---|---|---|---:|---:|---|---|
|r1|C1|system.txt：覆盖/轮廓审查与World初始化|null|null|不合格、拒绝|否|
|r1|C2|system.txt：SceneAct展开复杂度规划|0.4576982334|0.4173230040|必要功能通过、选中|否|
|r2|C1|system.txt：部件覆盖与World初始化|0.4618329116|null|不合格、拒绝|否|
|r2|C2|policy.py：图像成对反馈、部件差异账本|0.4819417090|0.3952040293|必要功能通过、选中|否|

H0的Dev Q为r1 0.4655227617、r2 0.4821030148。两条C2开发质量都略降，未掩盖退化。H0两次Selection均预算内失败、原始Q为null，不能把C2相对失败效用的正值解释为配对视觉提升。

## 选中流程的Test

|研发|来源|H0实测Q|选中C2实测Q|选中必要功能|
|---|---|---:|---:|---|
|r1|commons_189918915 仓库|null|0.4031707887|通过|
|r1|commons_80372956 吊灯/屋顶细节|null|0.5187468620|通过|
|r2|commons_189918915 仓库|null|null|未通过：超时|
|r2|commons_80372956 吊灯/屋顶细节|null|null|未通过：超时|

H0成功0/4，选中H*成功2/4；条件Q分别null与0.4609588253。失败另设效用0后，全分母任务效用0对0.2304794127；r1/r2效用差分别+0.4609588253、0。双方成功的有效质量配对为0，无法测量配对视觉增益。严格双方成功且提升的选中流程联合指标0/4，不是所有原始候选的终测联合通过率，未选候选未终测。

两项固定sol文字编辑各1调用、0修复，在有效r1产物上目标修改和非目标保持均通过；其余任务没有有效可编辑产物，不计为已测编辑通过。机械操作另列。两次独立匿名视觉评审仅作补充，不用于选择。

## 预算与资源

请求模型：gpt-6.1-sol medium负责重建/固定文字编辑；gpt-6-astra medium负责定位、提案、独立视觉评审。CLI0.163.0；实际返回型号未被独立报告时unknown，不采用模型自称作路由证据。

新CLI共65：可控诊断7、烟测7、研发/选择35（含4次超包诊断开销）、终测重建/文字编辑14、独立评审2。64会话完成、1次调用超时。已返回usage合计input 3,007,308/output 164,797 tokens，1会话usage未知，费用和不可观察的模型轮数null。

渲染尝试上界117，完成103；冻结上限160CLI/600帧。正式512最长边、Cycles16采样、seed42、统一颜色管理。CPU单重任务2线程，GPU0张；没有安装/升级、下载模型或干扰其他用户。

## 数据边界和运行偏离

本轮exploratory，历史曝光不能排除；标题分组不证明物理独立。Test只有两个来源，其中吊灯/天花图不是完整房间场景。全任务主表保留，仓库子集的事后敏感性为选中1/2、H0为0/2，不能替换冻结主指标。吊灯预先组合检查为可选，r1产物实际测得通过；不回写为原先必需。

初始冻结在正式场景前本地完成，不是外部预注册。四次原提案因超包未提交模型，修复后统一重做，旧失败与费用保留；一个H0 Test生成提前提交，媒体/代码/质量没有回流研发，只在新的Selection冻结后才评价，属于明确的as-run顺序偏离。原始record.json中M_version为null，真实M0由stage1/proposal_result定位，未补造字段。

无自然图像3D真值；AABB支撑近似和三角表面相交不等于真实不合理碰撞。多视角不计独立样本。没有真实M后代或独立回放，不支持元能力提升或普遍优势结论。公开/分析过的Test以后不能再当全新盲测。

## 文件与完整附件

- README.md；docs/AS_RUN_PROTOCOL_V2_1.md；docs/REVIEW_INDEX_V2_1.md。
- experiments/scene_rsi_v2_1/reports/index.html、REPORT_ZH.md（离线本地资源）。
- experiments/scene_rsi_v2_1/metrics/scene_metrics_flat.csv、functional_checks.csv、candidates.csv、candidate_attempts.csv、terminal_overview.csv、calls.csv；完整原始JSON/日志随附件。
- experiments/scene_rsi_v2_1/figures/：全部真实联系表、诊断、结构/编辑、演化、成本和失败PNG。
- experiments/scene_rsi_v2_1/candidates/：实际H/M源码与diff；code_snapshots/：原冻结、payload修订、报告修订源码。
- 代表性产物：results/r1/scene_rsi_v2_1/C2/test/commons_189918915/scene.blend、scene.py、final.png；同级commons_80372956也完整保留。以上相对实验根，完整文件在本地/附件，不强塞普通Git。

完整7包总计449,528,152字节，覆盖所有现有V2.1运行、失败与未选候选。索引artifacts_index_v2_1.csv共2956原始文件行+7附件行；逐文件size为原件脱敏前大小，附件行是实际压缩包大小。下载URL均空，状态local_only，不能当作已上传。

附件名：r1--fixed_h0.tar.gz、r2--fixed_h0.tar.gz、r1--scene_rsi_v2_1.tar.gz、r2--scene_rsi_v2_1.tar.gz、smoke--fixed_h0.tar.gz、smoke--scene_rsi_v2_1.tar.gz、shared-evidence.tar.gz。服务器位置见本地work/scene_v2_1_archive/bundles。旧V1/V2的大产物仍保留原现场，不声称这7包包含它们。

已从最终包解压并实际离线重画；汇总和ledger与原件一致。4个代表性blend原件/脱敏副本实际打开，测得结构/材质/相机不变。初次PNG元数据直接替换导致的归档格式错误已修复并保留失败包；最终PNG只重新编码元数据、去EXIF、保持解码像素不变。没有重跑重建、终测或指标前向。见docs/V2_1_ARCHIVE_VALIDATION.json及PACK_REDACTIONS。

## 可执行命令

已有Python3.11依赖环境中，解压全部附件后离线重算（新输出目录，0模型/0渲染）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python scripts/offline_v2_1.py --experiment experiments/scene_rsi_v2_1 --output derived/v2_1_replot
```

恢复GitHub凭据后，从归档仓库继续上传（本次未成功；不新跑实验）：

```bash
git -c http.version=HTTP/1.1 push -u origin research/scene-rsi-v2.1
python scripts/github_release_v2_1.py --bundles ../../work/scene_v2_1_archive/bundles --state docs/V2_1_RELEASE_UPLOAD_STATE.json
```

上传器只在API成功后填真实URL与状态；上传后需提交附件索引与Release状态并推送，不改旧历史。恢复认证后再读取远端README/代码/CSV/PNG与附件确认，当前未做到，不能宣称上传验收通过。

唯一实验续跑入口：`python outputs/scene_rsi_v2_1/resume.py`，在原项目根使用既有Python3.11。当前状态supplement_complete，只离线汇总，不产生新模型调用。新一轮研究需要新协议与目录，不能重用当前公开Test作盲测。
