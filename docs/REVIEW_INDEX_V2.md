# Scene-RSI V2 审查索引

本文件是证据入口，不预先判定科研机制有效。

| 主张 | 对应代码 | 原始数据 | 图表 | 局限或缺失 |
|---|---|---|---|---|
| M 接收显式预算并决定指定对象探测 | `experiments/scene_rsi_v2/pilot.py`、`strategies.py`、`inspect_blend.py` | `tests/contracts.json`、`tests/mechanism_acceptance.json`、各候选 `stage1.json` | Figure2 | 初始最大对象规则是生成几何覆盖启发式，未知参考语义对应 |
| 实际观测进入可执行 M 的第二阶段 | `meta_execute` / `execute_plan` / `propose` | `stage2.json`、`observations.json`、`changes.diff` | Figure2 | 分数敏感性不证明唯一原因；提案中的 alignment 是模型解释而非独立因果证明 |
| 研发期回归由 M 选择并实际执行 | `regression.py`、`pilot.py` | 候选 `regression/`、`post_patch_feedback.json` | Figure3 | 外部最终验收固定；近似与未知保留 |
| 已知结构及编辑错误被检测 | `tests/calibrate.py` | `tests/calibration.json`、`metrics/calibration_checks.csv` | `figure3_calibration.png` | 合成确定性夹具，不等于自然图像三维真值 |
| H-only / M-only / H+M 可分别探索 | `candidate_type`、`main` | `tests/contracts.json`、`metrics/candidates.csv` | Figure4/5 | M-only 不算 H 改善；后代执行不自动证明元能力提升 |
| 最终 H 仅依据 Selection 冻结 | `better`、`main` | `selection_freeze.json`、`archive.json` | Figure4 | 数据历史曝光，exploratory；两次研发不足以作普遍结论 |
| 质量、成功率、全分母效用分别报告 | `backend/evaluate.py`、`analyze.py` | `metrics/scene_metrics.csv`、`paired_test.csv`、`terminal_summary.csv` | Figure1、statistics | 缺测 null，失败效用为独立字段；未完成不当完成 |
| 机械编辑与文字编辑分开 | `inspect_blend.py`、`supplement.py`、`text_edit_worker.py` | `functional/`、`text_edit/`、`metrics/text_edits.csv` | Figure3 | 目标来自生成场景规则；无参考语义定位真值 |
| 全部真实调用与失败保留 | `backend/codex_wrapper.py`、`budget.py` | request/session/events/stderr、`metrics/calls.csv`、Release | 成本与失败图 | actual_model 若未独立报告则 unknown；CLI turn 不等于底层推理轮数 |

统计图均由 `experiments/scene_rsi_v2/analyze.py` 离线生成，原始 CSV/JSON 在同目录 metrics。产物附件见 `artifacts_index_v2.csv`，包含失败与未选候选。不存在的结果不得据此表当作已完成证据；以状态文件与上传摘要为准。
