# Scene-RSI：可编辑三维场景重建的 RSI 先导实验

V2.1修复绝对候选资格、失败诊断、真实对象定位与缺测统计。研究对象是共享重建流程H和元策略程序M；单图程序P单独记录。

**运行中检查点：正式V2.1已启动，Selection/Test未完成，终测结果为pending/null。** 只运行Scene-RSI与H0内部参照，无新SceneEvolve/Generic。1开发/1选择/2终测，两个独立研发、K2，CPU单重任务2线程，无GPU。数据exploratory；烟测后本地冻结，非外部预注册。

![真实故障与探测](experiments/scene_rsi_v2_1/figures/diagnostic_fixture_contact.png)

![诊断各阶段全部点](experiments/scene_rsi_v2_1/figures/diagnostic_comparison.png)

五夹具中，固定启发式/V2.1的对象或相关部件命中分别4/5、5/5，图像定位或决策模块命中1/5、5/5。**M第二阶段最终模块精确命中双方均1/5**，不能把视觉定位成功包装成整个闭环成功。V2.1多用5次定位CLI，实际成本不同。双方辅助共享helper修复各一次astra，换参数、名字和共享数据后均通过5/5；API契约提供提示，不是自然图像重建H改善或RSI优势。

![已知正确和损坏结构实测](experiments/scene_rsi_v2_1/figures/figure3_calibration.png)

真实厨柜图烟测：H0两次执行遇到圆角半径和空World错误，无有效Q。M根据轨迹提出H-only system.txt补丁，子代Q=0.556475909，必要功能通过。烟测不进入正式分数，不继承为新H0。所有失败和调用计入预算。正式收益尚未知。

审查入口：[审查索引](docs/REVIEW_INDEX_V2_1.md) · [冻结协议](docs/AS_RUN_PROTOCOL_V2_1.md) · [中文报告](experiments/scene_rsi_v2_1/reports/REPORT_ZH.md) · [离线HTML](experiments/scene_rsi_v2_1/reports/index.html)。

数据：[逐场景](experiments/scene_rsi_v2_1/metrics/scene_metrics.csv) · [候选](experiments/scene_rsi_v2_1/metrics/candidates.csv) · [Test状态](experiments/scene_rsi_v2_1/metrics/terminal_summary.csv) · [全部调用](experiments/scene_rsi_v2_1/metrics/calls.csv) · [诊断全部点](experiments/scene_rsi_v2_1/metrics/diagnostic_comparison.csv)。

代码：[运行入口](experiments/scene_rsi_v2_1/README.md) · [依赖](docs/DEPENDENCIES_V2_1.md) · [H0](experiments/scene_rsi_v2_1/backend/harnesses/baseline) · [初始M](experiments/scene_rsi_v2_1/initial_meta/scene_rsi_v2_1/meta.py) · [候选](experiments/scene_rsi_v2_1/candidates) · [快照](experiments/scene_rsi_v2_1/code_snapshots)。

大产物在正式流程结束后按运行打包，状态见[附件索引](artifacts_index_v2_1.csv)。包括失败与未选候选，不只保存赢家。未完成冻结M回放时不展示元能力提升图。第三方图像作者和许可在manifest；不上传权重、环境、缓存或凭证，不添加覆盖第三方代码的许可证。

离线重画（已有依赖环境；先解压Release全部附件到仓库根）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python scripts/offline_v2_1.py --experiment experiments/scene_rsi_v2_1 --output derived/v2_1_replot
```

旧实验完整保留：[V1](docs/README_V1.md) · [V2旧检查点](docs/README_V2_CHECKPOINT.md)。V2实际13条正式记录：开发4成功4失败、选择3成功2失败、Test0、正式候选0；另有2条旧V2烟测。旧running_scene为路由服务失败后的残留，不等于活进程。新分支补入当时未推送的V2证据，不以新规则回写旧分数。[状态核对](experiments/scene_rsi_v2_1/configs/v2_status_at_start.json)。
