# V2.3 命令

## 离线重算/重画（无模型、无Blender、原始数据不覆盖）

在仓库根目录，用具有上述依赖的 Python：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python scripts/offline_v2_3.py --experiment experiments/scene_rsi_v2_3 --output /tmp/scene-rsi-v23-review
```

目标目录必须不存在。完整媒体可从Release四包解压到仓库根；核心Git数据也足以重画主要图。HTML在新派生目录 reports/index.html，用本地浏览器打开，无CDN。

## 既有实验的实际入口（先激活Python3.11环境）

```bash
# smoke（已运行，缓存结果保留，不新增重复会话）
python outputs/scene_rsi_v2_3/experiment.py smoke
# pilot（已冻结正式任务；不要无意另开重复任务）
python outputs/scene_rsi_v2_3/experiment.py pilot
# report：只读现有数据生成衍生图表
python outputs/scene_rsi_v2_3/analyze.py
# resume：缺失阶段按既有ID；已经终结时仅离线报告，不新增模型调用/渲染
python outputs/scene_rsi_v2_3/experiment.py resume
```

## 后续元级研究入口（本轮未执行）

本轮没有自动M后代，不能将工程M称为后代。下一阶段须另建独立目录/协议，提供至少两个陌生共享H起点、未参与本轮调试的新任务、冻结 M_initial 和实际产生并参与后续研发的 M_descendant，并匹配显式历史。现有 experiments/scene_rsi_pilot/replay.py 是 V1 历史入口，其上下文/辅助H与本轮不同；不能直接把这十个公开任务当新盲测或假称本轮已完成元回放。未为此新增多代演化/回放框架。
