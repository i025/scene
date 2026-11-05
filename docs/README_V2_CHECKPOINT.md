# Scene-RSI V2：可执行三维诊断与功能保持

研究跨图像重建流程 H 及其元策略 M；P 是单场景程序，不算共享算法改进。V2 修复两阶段 M（选择探测 → 执行 → 观测进入 M → 共享修改）和 required/applicable/measured/gate 的功能回归，允许 H-only、M-only、H+M。

**当前是机制修复与烟测检查点，正式两次演化已启动但尚未完成；不能据此声称获得 Selection/Test 增益或元能力提升。** 只运行 Scene-RSI 与 H0 内部参照，不重跑其他方法。

确定性夹具：正确组合、独立编辑和组合移动通过；脱离、缺件、破坏支撑、共享材质误改与表面交叉均被检出。真实开发烟测 H0 Q=0.3725，H-only 候选 Q=0.4173，双方功能检查通过；这两个值不是终测结果。烟测8次CLI，1次末轮反馈超时但有效场景产物保留。

![真实校准检查](experiments/scene_rsi_v2/figures/figure3_calibration.png)
![真实烟测诊断（排除出正式样本）](experiments/scene_rsi_v2/figures/figure2_diagnostic.png)

- [冻结协议](docs/AS_RUN_PROTOCOL_V2.md)：4 Development / 4 Selection / 6 Test，两个研发重复，各K=2；保守404/420次CLI，1500帧硬上限。
- [审查索引](docs/REVIEW_INDEX_V2.md) · [中文报告](experiments/scene_rsi_v2/reports/REPORT_ZH.md) · [离线HTML](experiments/scene_rsi_v2/reports/index.html)
- [逐场景原始表](experiments/scene_rsi_v2/metrics/scene_metrics.csv) · [候选状态](experiments/scene_rsi_v2/metrics/candidates.csv) · [CLI实际用量](experiments/scene_rsi_v2/metrics/calls.csv)
- [源码和真实入口](experiments/scene_rsi_v2/README.md) · [依赖/迁移](docs/DEPENDENCIES_V2.md) · [V2产物索引](artifacts_index_v2.csv)

当前索引中的大产物仍为 pending，正式阶段完成后再打包上传；没有把本地已有文件冒称成已上传附件。已有2个正式H0开发任务失败，Selection/Test尚未开始。失败路径的功能记录已修复为未测量null与失败门槛分开；原记录、原冻结源码和修订diff保留，未重新调用模型生成这两项。

离线重算（解压附件后，使用已有环境）：

```bash
python scripts/offline_v2.py --experiment experiments/scene_rsi_v2 --output derived/v2_replot
```

局限：数据有历史联系表曝光，exploratory；来源组物理独立性不完全可证。无三维真值；声明部件完整性不等于语义完整性；AABB支撑近似、三角表面交叉与真实语义碰撞分开。M0最大生成对象规则是覆盖启发式，未知参考对象映射；烟测真实尺度探测选中地板，不能当家具尺度诊断。机械操作不等于文字编辑。没有冻结M回放结果，不展示元能力提升曲线。

V1 原代码、报告与数据完整保留：[V1 README](docs/README_V1.md) · [V1 Release](https://github.com/i025/scene/releases/tag/scene-rsi-pilot-2026-11-04)。其文档保留当时归档记录，V2结果与V1历史分开。
