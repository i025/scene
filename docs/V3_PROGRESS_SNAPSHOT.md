# Scene-RSI V3 当前归档进度快照

采集时间：2026-11-07T05:32:33.047280+08:00（北京时间）；对应 UTC 2026-11-06T21:32:33.047280+00:00。这是运行中归档，不是实验收尾。后续归档刷新另见 V3_ARCHIVE_STATE.json；本页保留最初进度快照数值，不充作实时监控。

- 分支：`research/scene-rsi-v3-10rounds`，参考提交 `9fd480eb7ec65a6c44b37b86a05bf715ed870e4f`；此工程步骤未提交或推送。
- 冻结记录时间：2026-11-06T21:30:49Z，正式平台、H_start/M000 与协议均已保存。准备属于 as-run；正式协议在 round0 前冻结。
- 复制时 state.phase=`generation`，formal_started=true，已完成正式研发 **0/10** 轮；当前在 `historical_r1_C2_start` 的开发图生成阶段。
- 已归档报告记录正式 scene_records=0、正式 BW=0、Test completed=0；Selection/Test/十轮改进结果仍 pending/null。不能用尚未运行的分母报告 0% 终测成功率。
- 执行者已由主代理启动；本归档子任务未终止或重启进程。当前工具进程命名空间无法独立看到主代理保存的 host PID，因此本文件不把 lock 中 running 单独视为持续执行保证。

## 已有准备证据

1. 历史固定起点 `historical_r1_C2_start`，不是 original_H0；H 与固定编辑器请求 Terra、M/评审请求 Astra，medium。真实路由没有元数据则 unknown，本地实际费用不可见，不宣称降本。
2. 用户授权 CPU8、内存32GB；CPU-only，单 Blender×8线程。2/4/8线程同场景微基准为12.276/6.335/4.188秒，各一次，非算法速度比较。
3. 8个确定性功能夹具、12资格条件组合、两配置新动作复用与真实图像 CLI/Blender smoke 已记录；准备最终契约验收 passed。
4. 10产物×2独立校准评审=20次，20完成/0评价失败；最大绝对重复差2.5，正式晋升容差2.5。校准包含 preview/正式视图差异，不能拿坏例BW分差作方法优势。
5. 冻结时准备消耗：CLI 30，渲染尝试80，可见输入token 1707671、输出53412，usage已知29、未知1；后续正式运行成本另见实际日志。
6. 数据12 development/4 selection/6 test/2 meta_replay，整个研究 exploratory。开发旧测试永久暴露；BW官方发布结构是test，本项目划分为自定义研究划分。

## 本次归档已准备什么

- 产物索引发现 1557 项，分组为 {"preparation": 1504, "baseline": 53}；这是文件项数，不是独立场景、模型推理或实验重复数。
- Git核心准备目录：[experiments/scene_rsi_v3](../experiments/scene_rsi_v3/)，包含真实源码、固定H/M、`code_snapshots/platform_frozen`、协议、configs、manifest、准备测量表、报告和PNG。
- 入口：[审查索引](V3_REVIEW_INDEX.md)、[HTML](../experiments/scene_rsi_v3/reports/index.html)、[中文报告](../experiments/scene_rsi_v3/reports/REPORT_ZH.md)、[原始指标目录](../experiments/scene_rsi_v3/metrics/)、[图目录](../experiments/scene_rsi_v3/figures/)。
- 未打大包、未上传Release、未git commit/push；本地完整日志/.blend不因核心归档而删除。`artifacts_index_v3.csv`仍为not_uploaded，planned URL不可当真实下载链接。
- 用户原有未追踪 `docs/GITHUB_AUTH_COMMANDS_V2.md`、`docs/RELEASE_UPLOAD_STATE.json`保持原样，本次没有stage它们。

## 脱敏、许可与可续用性

文本路径按[V3_REDACTIONS.json](V3_REDACTIONS.json)替换占位符；这保留方法、预算、调用、失败与选择事实。归档脚本未读取凭据，未扫描其他用户目录，未计算内容哈希。明确CC许可的12张web_scenes开发原图保留归属；BW原媒体、附件及未用Test rubric不公开，许可占位图不当实验结果。

本次只复制当前已有文件；源码冻结副本才是正式平台版本。动态日志/state/报告跨若干秒复制可能不是原子快照，后续正式结果须再刷新。普通源码中的外部路径占位符需要在另一机器按资源清单配置，不能声称离线归档无需依赖即可运行模型实验。报告离线重画不调用模型或Blender。

最终仍需：完整新基线、十轮真实提案与H/M轨迹、Selection选择、冻结后Test、预算内语义编辑/元回放、完整附件打包、脱敏复核、Git提交推送与远端访问确认；未完成前不宣称算法或元能力提升。

报告脚本离线修订及冻结版本的差异另见 [V3_REPORT_REVISION_NOTE.md](V3_REPORT_REVISION_NOTE.md)。归档分包识别 results/H01–H10 的改动有8条确定性路径测试，见 [归档工具](archive_tools_v3/)。
