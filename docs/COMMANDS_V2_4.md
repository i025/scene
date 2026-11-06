# V2.4 离线复核与既有实验续跑

## 离线汇总、审计和重画

离线入口只需要 Python 3.11，以及 NumPy、Matplotlib、Pillow；使用已有环境即可，不需要 Codex、Blender、模型权重、API Key 或 GPU。本轮没有为离线报告安装或升级依赖。

在其他机器上若没有合适环境，可在自己的独立环境准备这三个 Python 包；不要向共享环境安装。以下命令均在仓库根目录执行，`python3` 应指向该独立环境：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python3 scripts/offline_v2_4.py --experiment experiments/scene_rsi_v2_4 --output derived/v2_4_review
```

输出目录必须不存在，且不能放在原实验目录内。原始 JSON/分数不覆盖；代码和 JSON 复制到新目录，全部已有图片、`.blend` 与其他媒体只读引用。入口依次执行 `audit.py`、`audit_results.py` 和 `analyze.py`。输出入口为 `derived/v2_4_review/experiment/reports/index.html`；同时生成历史失败审计、实现/预测/成本审计 `metrics/implementation_audit.json`、中文报告、CSV/JSON、PNG，以及 `OFFLINE_RUN.json` 和可用性说明。

核心 Git 数据可以重画主要图表。要恢复完整 `.blend`、原始模型 JSONL 和大几何快照，请将该版本 Release 的四包 `fixed.tar.gz`、`structured.tar.gz`、`active.tar.gz`、`shared-evidence.tar.gz` 全部解压到仓库根目录，再指定另一个全新的输出目录重画。不要把 V2.3 的同名包混入 V2.4。

核心副本没有 `.blend` 时，`blend_file_exists=False` 仅表示本地缺少该大文件，不能改写原始 record 中实际执行/打开成功的测量。精确复现完整证据可用性需要全部 Release 包；缺少项会记入 `OFFLINE_RUN.json` 并显示在 HTML 提示中。入口不会下载附件、打开 Blender 工程或重算 LPIPS/DINO/Q。

需要指定已有 Python 环境时，先将 `SCENE_PYTHON` 设为该环境的解释器路径，再从仓库根目录运行：

```bash
: "${SCENE_PYTHON:?请设置已有环境的 Python 解释器路径}"
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" scripts/offline_v2_4.py --experiment experiments/scene_rsi_v2_4 --output derived/v2_4_review_with_existing_python
```

入口曾以当时尚未终止的现场证据，在独立 `work` 派生目录测试；未改动原始数据、现场报告或启动模型与 Blender。局部快照不代表最终结果，发布时应按完整归档重新运行。服务器专用绝对路径只保留在本地工作记录，不写入公开命令。

## 服务器原实验的离线报告

以下命令只更新现场目录中的派生指标、图表与报告；需要保留旧派生报告时，使用上一节的新目录入口。先将 `SCENE_PROJECT_ROOT` 设为原实验现场的项目根目录，将 `SCENE_PYTHON` 设为原实验环境的 Python 解释器。二者都由运行者设置，不使用归档仓库猜测现场路径。

```bash
: "${SCENE_PROJECT_ROOT:?请设置原实验现场的项目根目录}"
: "${SCENE_PYTHON:?请设置原实验环境的 Python 解释器路径}"
cd "$SCENE_PROJECT_ROOT"
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" outputs/scene_rsi_v2_4/audit.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" outputs/scene_rsi_v2_4/audit_results.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" outputs/scene_rsi_v2_4/analyze.py
```

## 同一冻结实验的续跑入口（本次编写工具时未执行）

这不是新研究或新一轮演化命令。它仅在原服务器现场、原 V2.4 ID/状态/预算下恢复尚未完成的阶段；已经存在 `FINAL_STATUS.json` 时，实验入口会报告全部任务终止，不提交新实验。不要删除终态文件来强行重跑。

```bash
: "${SCENE_PROJECT_ROOT:?请设置原实验现场的项目根目录}"
: "${SCENE_PYTHON:?请设置原实验环境的 Python 解释器路径}"
cd "$SCENE_PROJECT_ROOT"
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= "$SCENE_PYTHON" outputs/scene_rsi_v2_4/experiment.py resume
```

不要直接从 Git 中的 `experiments/scene_rsi_v2_4` 副本启动实验：归档配置含脱敏路径占位符。恢复执行前必须先还原全部 Release、将 Blender/Python/模型缓存/数据路径重定位到获准资源，并核对冻结协议与预算；不能把归档目录直接冒充原运行现场。离线重画不需要这些执行资源。
