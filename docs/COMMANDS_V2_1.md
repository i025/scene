# V2.1 实际入口

Python 3.11及依赖版本见DEPENDENCIES_V2_1.md。下面是离线重算，不调用CLI/Blender，不改变原始测量；先把全部Release tar.gz解压到仓库根。输出目录必须尚不存在。

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python scripts/offline_v2_1.py --experiment experiments/scene_rsi_v2_1 --output derived/v2_1_replot
```

原服务器实验续跑（当前已supplement_complete，只汇总，不新建实验或模型调用）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" "$SCENE_PROJECT/outputs/scene_rsi_v2_1/resume.py"
```

SCENE_PYTHON为既有Python3.11环境，SCENE_PROJECT为实际实验项目根；真实路径保留在服务器本地摘要，公开归档使用占位符。不要从归档对旧状态启动新实验；未完成阶段才可能真正调用模型。V2.1已结束，不需为补齐报告重新运行重建或终测。
