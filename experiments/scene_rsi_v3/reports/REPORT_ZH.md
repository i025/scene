# Scene-RSI V3 中文实验报告

本轮状态：generation；正式研发完成 0/10 轮。保存了 0 条正式场景记录、0 次BW测量；终测 pending（已完成记录 0）。实际CLI会话 32 次（包括准备阶段），usage可见 30/32。

终测每来源每端点计划 1 次生成；依据 config.json:pilot.final_test.primary_repeats，当前为最低保证次数，尚未作最终预算分支决定。 H_best与H_start相同时复用同一版本的真实产物，不增加独立生成数。

所有结果均为 BW-style / CLI-adapted，不是官方榜单分数。开发历史图已暴露；同模型研发与评审存在偏差。未完成项保留pending/null；没有真实冻结元回放时不宣称元能力改善。进程树RSS为0.1秒采样下界；嵌套阶段墙钟和CPU作用域有重叠，不相加冒充总耗时。

请求模型与可确认路由分开见 cli_audit.csv；没有路由元数据时 observed_model=unknown。费用未知，不宣称降本。

## 十轮实际状态

| round | status | H retained | M retained | type |
|---|---|---|---|---|
| 1 | not_started | null | null | null |
| 2 | not_started | null | null | null |
| 3 | not_started | null | null | null |
| 4 | not_started | null | null | null |
| 5 | not_started | null | null | null |
| 6 | not_started | null | null | null |
| 7 | not_started | null | null | null |
| 8 | not_started | null | null | null |
| 9 | not_started | null | null | null |
| 10 | not_started | null | null | null |

![真实实验图](../figures/development_contact_sheet.png)

历史开发图按预定顺序全部展示，n=12来源；这些图片为研发已暴露数据，不是泛化证据。同一H版本复用同一产物标reuse，失败或未运行保留空位。

来源：[manifest.json](../manifest.json)、[metrics/scenes.csv](../metrics/scenes.csv)、[metrics/rounds.csv](../metrics/rounds.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/evolution.png)

蓝线记录实际保留版本的晋升时验证评分，圆点为接受候选、叉号为未接受候选；后续边界复评原始记录另见scenes.csv中的bw_judgments，不反向覆盖历史决策点。资格恢复晋升不自动代表配对视觉增益。不对未运行轮次填零；连续轨迹不是十次独立重复。

来源：[metrics/rounds.csv](../metrics/rounds.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/quality_points.png)

各划分所有实际测得的逐生成 BW 点；开发 preview 与正式 Selection/Test 分开。缺测和未开始不显示零分。统计单位为生成产物，独立场景数另见CSV。

来源：[metrics/scenes.csv](../metrics/scenes.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/dimensions_and_function.png)

逐产物八维原始评分与功能测量计数；未测不算失败，也不算通过。required/applicable/measured_pass/gate_pass原始对象完整保留于CSV。机械编辑不等于文字编辑能力。

来源：[metrics/scenes.csv](../metrics/scenes.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/cost_and_timing.png)

实际会话、阶段/进程墙钟原始点和可见token总量。timing.csv同时保留进程树和metric_timing.jsonl事件；两者作用域可能嵌套，禁止加和成总耗时。缺少CPU的模型加载事件保持null；parent RSS是进程生命周期高水位。费用未知。

来源：[metrics/cli_audit.csv](../metrics/cli_audit.csv)、[metrics/timing.csv](../metrics/timing.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/cpu_benchmark.png)

同一历史场景、同一512×512/Cycles16配置的2/4/8线程微基准，各一次；不是算法速度比较。首次psutil导入错误3次均保留，不纳入成功吞吐。

来源：[preparation/cpu_benchmark_corrected_import/cpu_benchmark.json](../preparation/cpu_benchmark_corrected_import/cpu_benchmark.json)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/research_chain.png)

按时间选择第一条完成的正式研究动作，无论成功或失败；图像和观测均来自该动作。动作执行本身不证明原因唯一或H改善，后续决策、diff和迁移结果需合并审查。

来源：[metrics/actions.csv](../metrics/actions.csv)、[metrics/rounds.csv](../metrics/rounds.csv)；生成脚本：[analyze.py](../analyze.py)。

![真实实验图](../figures/HM_lineage.png)

H与M分别记录实际使用、保留和动作观测次数。不变代码不作为后代，M可执行或被使用不等于能力改善；末轮尚未再执行的M不能声称已发挥作用。

来源：[metrics/rounds.csv](../metrics/rounds.csv)、[metrics/actions.csv](../metrics/actions.csv)；生成脚本：[analyze.py](../analyze.py)。

## 重画命令

```bash
__SCENEEVOLVE_REPRO__/work/.venv/bin/python __EXPERIMENT_ROOT__/analyze.py report
```

本命令只读取保存的记录、图片和配置，不运行模型或Blender。续跑入口由主runner提供，不由报告触发。
