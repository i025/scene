# V3 确定性功能与开放动作验收

本目录是准备阶段工程夹具，不是 M 自动生成的研发动作或正式重建样本。无远端模型调用。

- 8/8 结构与编辑断言通过：合法组合、断开部件、遗漏声明部件、破坏支撑、共享材质误改、合法独立编辑、组合移动、三角面交叉。
- 12/12 required/applicable/measured_pass 组合符合 gate 规则；必需但缺测或不适用不通过，非必需不会错误拦截。
- 新参数化 `fixture_m/actions/measure_named_support.py` 通过既有 `validate_source`，经现有 `ResearchAPI.execute_action` 与 `action_worker.py` 在两个不同 `.blend` 执行，未添加固定 runner 菜单。
- 指定目标为 `Z_target_part`，字母序首个 Mesh 是 `A_unrelated_part`；实际测量目标来自参数。

实际动作测量 `(配置, 归一化间隙, 接触近似通过)`：`[('correct', 0.0, True), ('broken_support', 0.4082482904638631, False)]`。

8 张真实校准 PNG 与 8 个 `.blend` 均在对应 case 目录。渲染固定 CPU 8线程、Cycles、256×256、4 samples，明确为 calibration_preview，不进入正式 BW/质量提升曲线。进程树 CPU/RSS 与时间见 `process.json`、`action_reuse/actions/*/process.json`。

局部材质测试直接按预定义 Blender 操作执行；没有文字编辑器。支撑为声明关系上的 AABB 接触近似。三角面交叉仅作补充，既不能检测完全包含，也不提供语义碰撞真值。正确层级与断开层级可有相同渲染，必须读真实场景结构。

离线重画（不启动 Blender、不调用模型）：`python report.py`，需要现有 Pillow 环境。原始测量及 CSV 同目录。

原始夹具生成脚本为 `build_fixtures.py`，一次性执行驱动为 `run.py`。为保留已有证据，不在原目录覆盖重复运行；主 preflight 检测已保存的 passed 记录后应直接引用。
