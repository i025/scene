# V2.2 实际入口

归档仓库离线汇总/重画（只读现有数据；新输出目录不能存在）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= \
python scripts/offline_v2_2.py --output derived/v2_2_review_01
```

输出 `derived/v2_2_review_01/experiment/reports/index.html`。核心图像和表格在Git；若还要审查全部原始日志、blend、步骤图，先从本轮Release下载所有包解压到仓库根。离线重画不使用模型、Blender或GPU。

原服务器live目录的执行命令（使用原有Python3.11环境；不从归档占位符配置直接启动）：

```bash
python outputs/scene_rsi_v2_2/experiment.py smoke
python outputs/scene_rsi_v2_2/experiment.py experiment-a
python outputs/scene_rsi_v2_2/mechanism_tests.py
python outputs/scene_rsi_v2_2/freeze_bc.py
python outputs/scene_rsi_v2_2/diagnosis_runner.py
python outputs/scene_rsi_v2_2/analyze.py
```

唯一统一续跑入口（先确认没有旧活动进程）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= \
python outputs/scene_rsi_v2_2/resume.py
```

已全部结束时只重画，不新增模型调用/重建。已有真实失败保持终态，不为成功重采样。服务暂停不会静默删除；仅在恢复后使用下一个尚未使用的 `--recover-incident N`，整轮最多3次独立事件检查，仍在原预算内；旧检查与原失败全部保留。

代码和协议不构成重新开始一轮演化的入口：V2.2不调用旧pilot.main搜索。新机器开展新研究须先显式设置外部依赖并冻结新协议；当前提供的跨机器一条命令是离线重算。
