# Scene-RSI首轮归档与上传摘要

## 实际上传状态

- 目标仓库：https://github.com/i025/scene 。本地分支main。
- **本地整理、脱敏、报告核对、完整分包和Git提交已完成；推送与Release均被GitHub403拒绝，远端仍为空。没有可访问的远端提交链接。**
- 实验归档本地提交：`faea649445ef8b3c77637cb315b4c037f7dd1a0b`。本摘要在其后另做提交；最终提交标识以本地Git HEAD为准，避免摘要自指。
- 实际推送1次失败；创建Release1次失败：`Resource not accessible by personal access token`。未上传任何Release附件，没有反复重试。
- 现有认证是fine-grained PAT，账户元数据push=true不等于该凭据有实际仓库写入。SSH agent socket和配置引用身份文件均不可用。没有读取私钥、保存凭据或修改仓库可见性/全局配置。
- 恢复上传需要现有GitHub凭据授权i025/scene及Contents读写权限；无需在对话中发送任何凭据。
- 原始证据：[UPLOAD_ATTEMPTS.json](docs/UPLOAD_ATTEMPTS.json)、[Release实际403](docs/RELEASE_UPLOAD_ATTEMPT.json)。最后远端读取成功且无refs，README/代码/图片/数据尚不能在远端访问，不把本地commit当成功上传。

## 本地审查入口

- [中文README与真实图](README.md)
- [审查索引：主张→代码→数据→图→局限](docs/REVIEW_INDEX.md)
- [事后整理as-run协议](docs/AS_RUN_PROTOCOL.md)（不补写成预注册）
- [中文完整报告](experiments/scene_rsi_pilot/reports/report.md) / [离线HTML](experiments/scene_rsi_pilot/reports/index.html)
- [运行表](experiments/scene_rsi_pilot/metrics/runs.csv)、[主候选](experiments/scene_rsi_pilot/metrics/candidates.csv)、[全部候选/准备目录](experiments/scene_rsi_pilot/metrics/all_candidate_attempts.csv)
- [逐场景原始指标表](experiments/scene_rsi_pilot/metrics/scene_metrics.csv)、[逐对数据](experiments/scene_rsi_pilot/reports/paired.csv)、[调用/usage](experiments/scene_rsi_pilot/reports/calls.csv)
- 可视化：`experiments/scene_rsi_pilot/reports/`、`experiments/scene_rsi_pilot/figures/`；每图关联原CSV/JSON和实际绘图脚本。
- [现有产物索引](artifacts_index.csv)：13,085个归档成员；实际下载URL为null、上传状态全部明确not_uploaded_permission_denied；计划URL单列，不能当实际下载。

## 完整附件与未上传原因

27个已脱敏分包合计 **2,363,490,125字节**，位于原实验工作区 `work/scene_archive/bundles/`。相对本归档仓库为 `../../work/scene_archive/bundles/`。完整列表、各文件大小和相对路径见 [LOCAL_ARTIFACTS.csv](docs/LOCAL_ARTIFACTS.csv)。**没有实际Release或附件URL**，原因是上述GitHub写入权限403。

它们覆盖全部已有运行、失败与未选中候选、完整prompt/图像附件/stdout JSONL/stderr/response/usage、全部场景程序/.blend/渲染和大几何JSON。不是只选胜者。原始未脱敏实验仍在原服务器，不改动、不删除。公开副本只替换账户/资源路径、隐藏5条未用预留数据；.blend的账户路径用等长字节替换，保留场景数据块尺寸。原本缺失的2次CLI原日志、2个历史悬空参考链接目标仍如实记缺失。

没有上传权重、环境、缓存、node_modules、重复数据集或未用预留标签。13张实际使用Commons图片的署名/许可、两BlenderWorld任务来源和MIT许可证另存；不为整仓库另加覆盖第三方内容的许可证。

## 各方法实际规模

|方法|研发重复|主候选记录/源码合格|完成场景槽/计划|执行失败|提案拒绝未运行|
|---|---:|---:|---:|---:|---:|
|fixed_h0|2|0/0|12/16|4|0|
|sceneevolve_cli|2|4/4|24/24|0|0|
|generic_rsi_cli_adapted|2|4/4|23/24|1|0|
|scene_rsi_pilot|2|4/3|19/24|1|4|

以上为主计划88逻辑槽：78完成、6失败、4未运行；每组同2开发/2选择/4测试。不是88个独立场景。主终测32逻辑槽27有效5失败，H0复用有明确别名与零新增成本。

- 三消融各1研发、K1、8个开发/选择/测试槽：结构证据组8/8，其余两组各7/8；终测合计10/12有效、2路由失败。所有消融与参考共同有效配对0，不能比较不一致条件均值。
- 冻结M回放：2个提案、7个新物理重建全部成功；一个共同陌生H起点、每M一次提案、一个独立共享测试场景。两者都选回H_start。
- BlenderWorld：两个独立阶段共4重建槽，3成功、1程序失败；2次独立judge路由失败、1次因重建失败未评审，仅Ours/bw0005评分完成。
- smoke：2场，1成功1失败；全部排除正式对照。当前共125场景记录（含smoke和复用别名），不是125个独立样本。
- 全部提案结果文件44份（当前17、历史27）；另外9个准备目录无proposal_result，只记录继承源码/探测，不当作9个已提出的新H候选。

## 已观察关键数值与边界

累计596/600 CLI、660完成帧、715/1500尝试上界不变；594份会话记录508完成86失败，另2次初始日志损失仍计入。87 usage未知，费用unknown。模型请求为sol重建/固定编辑、astra提案/评审，均medium，实际路由unknown。

主终测相对同重复H0配对Q差：SceneEvolve +0.02567/+0.05691，Generic +0.02474/0，Ours +0.00983/0；有效配对仅r1=2/4、r2=3/4。六个完整有效改进标志均未通过，不以不完整数据宣称质量退化或普遍优势。

文字编辑11/16端到端通过，已执行条件11/14；与机械操作区分。冻结元回放两M测试增益均0，不宣称元能力提高。bw0005 H0/Ours Q=0.28543/0.31289；bw0011仅Ours Q=0.48763，均缺完整适配评分配对。这是adapted evaluation、非官方榜单。无3D真值，AABB仅近似，多视角不是独立样本或真实新视角；A/B机制部分实现。更大元回放、完整机制、严格新盲测和转台视频未完成。

## 归档验证与命令

归档没有新增模型调用、重建、终测、渲染或指标前向，也未使用GPU。汇总/画图/压缩单重任务，数值库最多2线程。离线重算记录数、状态、账本和配对统计与原报告一致，2513个HTML本地引用无缺失。四种方法各一个脱敏工程与原件共8次只读打开，已测对象/材质/相机参数一致；没有保存/渲染或计作新实验。详见 [OFFLINE_VERIFICATION](docs/OFFLINE_VERIFICATION.json)、[BLEND_COPY_CHECK](docs/BLEND_COPY_CHECK.json)。

取得27个附件并在仓库根解压后：

```bash
for file in release-assets/*.tar.gz; do tar -xzf "$file"; done
python scripts/offline_report.py --output derived/offline_01
python scripts/archive_tables.py
```

第一条Python在新目录重算/重画，不覆盖保存报告。只需Python3.11及requirements-report.txt列出的已有依赖，无需Blender/CLI/模型权重。

原服务器、原实验工作区的唯一实验续跑命令如下，**本次未执行**：

```bash
bash outputs/scene_rsi_pilot/run.sh resume
```

它复用现有记录，不自动重开失败任务、扩大600预算或开展新一轮研究。
