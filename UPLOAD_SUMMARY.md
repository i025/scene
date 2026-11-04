# 上传摘要（首次归档提交）

目标：https://github.com/i025/scene ，分支main。此文件初版随实验归档提交，附件上传后另行更新实际下载链接、远端读取确认与最终状态；当前不把本地提交当作上传完成。

归档范围：scene_rsi_pilot首轮真实实验，2开发/2选择/4测试、两次研发、K≤2，以及实际执行的消融、冻结M回放和两个独立BlenderWorld阶段。保留全部成功/失败/拒绝/未选中候选和历史故障；不包括模型权重、环境、缓存或5条未使用预留数据。

本次归档没有新增模型调用、重建、终测或渲染，没有使用GPU。原实验账本596/600 CLI、660完成帧、715尝试上界保持不变。缺失日志及指标不补造。

审查入口：README.md、docs/AS_RUN_PROTOCOL.md、docs/REVIEW_INDEX.md、experiments/scene_rsi_pilot/reports/report.md、experiments/scene_rsi_pilot/metrics/、artifacts_index.csv。

完整证据已本地打成27个分包；上传状态以artifacts_index.csv和后续本摘要为准。远端附件计划入口：https://github.com/i025/scene/releases/tag/scene-rsi-pilot-2026-11-04 。在真实上传和远端读取确认前，不声称全部上传。

离线命令（先解压全部附件）：`python scripts/offline_report.py --output derived/offline_01`；归档表/完成状态重画：`python scripts/archive_tables.py`。

原服务器续跑唯一入口：`bash outputs/scene_rsi_pilot/run.sh resume`。本次未执行，不重开失败、不扩充预算或新研究。
