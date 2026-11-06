# V3 实际资源与数据复用清单

本表在 V3 准备阶段依据本地已有文件整理；不是已完成十轮的声明。所有大资源仅引用路径，不复制模型或数据集、不安装或升级共享环境、不做内容哈希。

| 真实路径 | 现有用途 | V3 复用方式 / 缺少什么 |
|---|---|---|
| `__PROJECT_ROOT__/archive/scene` | GitHub 归档仓库；V2.4 参考提交 `9fd480eb7ec65a6c44b37b86a05bf715ed870e4f` | 在新 V3 分支归档，实际运行不假设归档代码可直接执行；旧实验保留 |
| `__PROJECT_ROOT__/outputs/scene_rsi_v2_4` | V2.4 实际运行源码、失败审计和产物 | 只读来源；V3 后端与必要模块局部修改到独立目录，旧分数不回写 |
| `__PROJECT_ROOT__/outputs/scene_rsi_v2_1` | V2.1 H/M 轨迹及历史场景记录 | 确认实际演化起点来源与暴露历史，不充作新协议公平基线 |
| `__PROJECT_ROOT__/outputs/scene_rsi_v2_4/fixed_h/r1_C2` | 继承 V2.1 r1/C2 的共享 `policy.py`、`system.txt` | V3 固定 `historical_r1_C2_start` 的源码来源；不是 original_H0；新模型/预算/评分下须重新运行 |
| `__PROJECT_ROOT__/outputs/scene_rsi_v2_4/backend` | SceneEvolve/SceneAct 复现后端、CLI 薄适配器、执行与数值指标 | 保留既有 SceneAct 表示与后端；V3 只修资源/日志/预算与外部评分适配所需部分，不重写上游 |
| `__BLENDERWORLD_ROOT__` | 本用户已有 BlenderWorld 项目；上游代码 MIT | 只读 rubric 语义、八维定义、证据路由和取景规则，使用本地 `.blend` 的轻量 BW-style / CLI-adapted 入口；不运行 pack/plan/verify 的哈希流程 |
| `__BLENDERWORLD_ROOT__/data/BlenderWorld/dataset.jsonl` | 本地 223 个官方发布 test 任务，含真实参考与任务文件 | 按实际 `task_id`、metadata/query 和路径选 12 个多对象室内空间；本项目 4 Selection、6 Test、2 meta_replay 是自定义研究划分，不是官方训练/验证划分；不复制整个数据集 |
| `__COMMONS_DATA_ROOT__/manifest.json` | 709 条本地 web_scenes 参考图来源 | 开发集优先沿用旧实验明确记录的 12 张照片，保留作者/来源/许可；原图仅路径引用 |
| `__PROJECT_ROOT__/outputs/scene_rsi_v2_2/data` | V2.2 实际取得并缩放的 Commons 图片 | 本轮引用其中 5 张历史图片进入开发；旧测试身份永久记为已暴露；精确文件逐项见 manifest |
| `__SCENEEVOLVE_REPRO__/work/.venv/bin/python` | 已跑通复现的独立 Python 环境，既有 numpy/Pillow/Matplotlib/torch/LPIPS 等 | 直接复用，不改共享环境；V3 实际依赖版本由准备过程记录 |
| `__BLENDERWORLD_ROOT__/runtime/blender-4.2.10-linux-x64/blender` | 已有 Blender 4.2.10 LTS | CPU 构建、固定质量 Cycles 渲染与真实场景检查；线程/并发以 V3 CPU 基准及冻结配置为准 |
| `__SERVER_USER_ROOT__/.local/bin/codex` | 已登录 Codex CLI，V3 help/version 实际记录为 0.163.0 | 复用 CLI 调用与真实图像附件；不读取、复制认证令牌，不全局升级 |
| `__SCENEEVOLVE_REPRO__/work/model-cache/dinov2-base` | 既有 DINOv2 数值前向权重 | CPU 直接加载；不下载、不把 CLI 判断当作数值前向 |
| `__SCENEEVOLVE_REPRO__/work/model-cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth` | 既有 AlexNet 权重 | LPIPS CPU 前向复用，不复制权重到 Git |
| `__SCENEEVOLVE_REPRO__/work/.venv/lib/python3.11/site-packages/lpips/weights/v0.1/alex.pth` | 既有 LPIPS 包内权重 | 与 AlexNet 路径共同引用，原环境不升级 |

## V3 数据事实与访问边界

`manifest.json` 共 24 个显式来源：12 development、4 selection、6 test、2 meta_replay；完整来源、历史 split、路径与暴露记录见 `configs/data_exposure.csv`。划分依据来源与任务类型，在新 V3 结果产生前制定，不根据候选分数挑样本。

开发集均为历史实验图。`commons_189918915`、`commons_96943062`、`commons_104864364`、`commons_31294395`、`commons_92056365`、`commons_192968130` 具有旧 test/fixed_version_test 记录，本轮进入开发后永久标记暴露。局部 shoemaker workbench 未纳入，使用完整多对象现代厨房补足 12 图；不能把单物体任务混称整场景。

BW Selection：`bw_0031`、`bw_0017`、`bw_0045`、`bw_0085`。

BW Final Test：`bw_0016`、`bw_0023`、`bw_0039`、`bw_0056`、`bw_0005`、`bw_0011`。

BW meta_replay：`bw_0082`、`bw_0092`。

`bw_0005` 与 `bw_0011` 在旧 pilot 的 external/external_followup 下各有 2 条真实 `record.json`，因此明确已暴露。其余任务未在当前 Scene-RSI results 中发现执行记录，但本地已有 task index/gallery，不能证明此前从未人工查看；标为 exposure_unknown，整轮仍为 exploratory。任务所属地点并无完整来源真值，当前只能保证显式 source/group/解析后图片路径不跨 split，不能宣称所有真实地点独立性已得到证明。木工车间近族 `bw_0054` 未纳入，避免与 `bw_0016` 跨 split；`bw_0098` 要求 before-after 装修改造，未作为图像重建样本。

初次划分准备只读取 BW metadata/query 与文件存在性，未打开所选 BW 的 rubric 内容或参考像素。后续正式前适配核对仅读取 4 个 Selection 官方 rubric，确认均为顶层 object + rubrics 数组，能够由 bw_evaluate 直接接收；细项见 configs/rubric_schema_audit.json。Final Test 与 meta_replay 的 rubric 及像素仍未打开。12 张开发照片现已生成 configs/dev_rubrics/*.json，版本 reference_requirements_v1_preformal，统一 7 条参考/任务驱动标准；只用来源原题名与固定可编辑重建要求，不依据候选输出、历史分数或隐藏几何制定。`expected_min_meshes`/`expected_composite` 仅为继承字段，不代表 V3 BW 忠实度、绝对资格或最终功能协议已经冻结；最终可靠必要门槛须另行冻结。

M 只能接收本回合暂存开发证据；Selection 固定入口仅返回协议允许的聚合结果；第十轮结束及最终 H 选择冻结前，Final Test 不运行、不展示、不反馈给研发。此根 manifest 是资源管理资料，不得原样挂入 M/H 工作区；尤其不得暴露完整 BW 根目录或 rubric 路径。

## 缺少或尚不能确认

- 没有可证明全新盲测的足量独立来源；本轮只能报告探索性研究，不能把历史/未知曝光图称盲测。
- 自然图像和 BW 参考没有本轮可用的精确三维几何真值；对象关系检查须区分可测事实与标签依赖。
- 单张 BW 参考的独立媒体分发许可尚未逐张确认；默认仅提交来源/任务 ID/路径，原媒体不随 Git 或 Release 重新公开，除非后续确认许可。
- CLI 实际路由、底层精确请求数、可见本地费用与远端等待拆分仍以真实日志为准；本清单不补造。
- 模型联通、CPU 布局、BW 校准、正式冻结与十轮执行由主流程独立记录，本清单不将其标成完成。

离线划分检查：在本目录运行 `python3 check_data_split.py`。该检查只验证显式来源/路径与计数，不读图片或 rubric、不进行哈希验证。
