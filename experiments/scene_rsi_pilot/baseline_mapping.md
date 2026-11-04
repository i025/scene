# 基线映射与适配边界

共同 H0 = 本地 SceneEvolve_Code/harnesses/baseline/policy.py + system.txt 原样快照；不是已进化最终流程。共同5次student调用、3次execute、1200秒、SceneAct、CPU Cycles、Q及功能验收。P仅为单图build.py与blend。

- fixed_h0：原仓库初始循环，错误/渲染反馈属于单任务修复，跨任务不改H。
- sceneevolve_cli：保留本地完整teacher模板、共享policy改写、开发全轨迹与图像反馈、按固定Selection严格改善保留。原实现每轮同时两个子代，本轮为K=2顺序子代，M固定；这是CLI/backend-adapted baseline，非论文原始分数协议。
- generic_rsi：未发现本地官方HyperAgents。准备阶段读取官方 `meta_agent.py`、`generate_loop.py` 和 `select_next_parent.py`。官方 MetaAgent.forward 调用聊天工具修改整个代码库；task_agent为任务程序，generate_loop保存代际差异和评估档案并移除val/test原始证据。这里映射为policy.py/system.txt (H)、meta.py的可执行plan(packet) (M)、candidates/与archive.json。模型统一CLI；工具动作由固定外部runner执行；只允许H/M文件，测评器不可改。K2显式调用最新有效M源码；即使其H未被选中也允许沿该后代探索，但最终Selection仍包含H0。这取代官方随机档案父代策略，属于有实质限制的自引用循环适配，不等价于官方完整HyperAgents。若M从未实际改变/后续使用，将按结果标为generic_fixed_meta，不宣称已验证通用RSI。
- scene_rsi_pilot：与Generic相同H0、输入原始证据、工具/探测额度；M_initial增加带类型的诊断记录、单因素探测及依赖回归指导。最终分数与门槛完全共用。静态初始策略不构成研究发现，只有后续实际运行过的M改动才记录为元级自修改。

官方准备资料（正式阶段不联网）：
https://github.com/facebookresearch/HyperAgents/blob/main/meta_agent.py
https://github.com/facebookresearch/HyperAgents/blob/main/generate_loop.py
https://github.com/facebookresearch/HyperAgents/blob/main/select_next_parent.py

这里未采用官方Docker、第三模型、内容哈希、无限重试或可改评价器配置。所有适配均在本轮独立目录；原仓库未修改。

实际视觉档案边界：当前M附件包含每个开发场景的参考图、最终选中渲染和本轮诊断图；中间执行的代码/错误/文本轨迹保留在有界证据中，中间渲染文件也完整存盘，但并未全部作为M的图像附件。这一共同输入适配适用于所有方法，区别于本地teacher可附带全部render_history的入口，不能称逐项完全相同复现。

资源补充：以上 CPU 描述初始共同后端。用户后续授权空闲 GPU 后，所有方法共用 gpu_adaptation.md 的单卡策略和相同质量设置；不将混合设备耗时解释为算法效率。


## 独立消融阶段的证据对照适配

`generic_same_structured_evidence` 的初始策略复用 Generic 指令与探测选择，仅增加从 Ours 初始程序抽取的 diagnoses / regression_priorities 格式化函数。原合并实现中未使用的完整 Ours 指令及探测策略源码，在该独立阶段冻结和首次恢复调用前移除。已用冻结的 r1 H0 开发数据核对：证据两字段与 Ours 完全相同，指令与探测输出与 Generic 完全相同。原源码、diff 和检查数据见 `quota_restored_20261103/ablation_evidence_control/`；这是初始对照适配，不是模型学得的 M 自修改。主终测当时已开始，此修正未参考终测表现，未修改主方法 H/M、目标或预算。

`ours_without_regression_guidance` 还屏蔽历史 accepted 位，避免 K=2 时由该位反推出被隐藏的功能门槛结果；保留原始几何和视觉指标，最终评价与验收不变。原始几何仍可支持功能风险推断，本对照不声称去除全部功能相关信息。
