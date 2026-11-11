# 可选回放入口工程准备记录

仅运行了静态语法、纯 Selection 函数与 prepare/audit 元数据检查；没有模型、Blender、媒体/rubric/附件内容读取。完整 post-stage 执行链尚未实际 smoke，不能凭静态通过声称运行成功。

首次 audit 误把 experiment.lock 当成 JSON，实际主 launcher 用空文件 flock；该次 JSONDecodeError 未触发实验。随后读取 launch.py 修正为真实非阻塞共享锁检查，当前能检测主任务持有独占 flock 并返回 pending。中间初版脚本未单独保存源码快照，现有文件是修正版，不伪造历史快照。

准备协议冻结了 original_H0 与 V2.4 task01/active/H 两个源路径；原始H0与主Hstart共享policy.py，必须披露。完整源码是否在十轮中曾交给M，需要主终态后重新逐请求比对文本。没有已实际执行后代、足量余量或完整陌生性时，finalizer不运行。

后续工程审计进一步收紧“实际执行后代”的证据：仅有较早保留版本和后续父代名称不够。较早接受来源、匹配的 research_request 与完成记录必须同时存在；至少一个变更 Python 文件要对应同一后续 trace 的入口、已记录加载 helper，或名称与源码均匹配的 completed 动作。动作库仅放入提示不算执行，未执行 helper 与说明文件也不算。具体纯测试见 EXECUTION_EVIDENCE_TESTS.json；实际只读核对见 M_CHANGED_CONTENT_CURRENT_AUDIT.json。入口/导入/动作层证据不提供行或分支覆盖，也不能证明改动内容改善了决策。此审计不修改主线 M 接受与保留规则。

主线评分器的原交付图证据修复独立纳入本阶段：`prepare` 在复制旧冻结平台后，才覆盖已校正的主 `bw_evaluate.py`，版本 `original_delivery_metadata_A02`；保留前后源码与 diff，并记录交付证据纯测试。当前仅审查并写入口，未执行 stage prepare/run，尚无实际覆盖副本或新评分结果。

上述局部覆盖计划随后在任何 M 后代或回放执行前撤销，以免后代依赖的完整对象清单/420k上下文投影/480k提示上限与旧接口不一致。当前唯一平台来源改为主线实际 `code_snapshots/platform_A02`，待校准完成及固定快照就绪；缺失时 pending，禁止旧平台回退或动态最新源码 overlay。附件直接由 A02 `prepare_task` 转发，删除重复拼接包装。M0 仍为原始策略源码，两个被测 M 共用 A02 固定平台。各自真实动作库及派生动作名索引作为 M 的一部分保留，不再清空菜单；共同开发证据和公共工具/预算不变。原 EVALUATOR_OVERLAY_ENGINEERING_AUDIT.json 与 A01 更新 JSON 保留为带时间线的未执行准备历史；新的状态见 PLATFORM_A02_STAGE_UPDATE.json。

门槛与启动审计进一步移除了当前协议中的历史常数。实际代码原本已经从所复制配置读取 `evaluation.promotion_delta`，现协议与 stage_freeze/summary 同样记录该固定 A02 值，不把校准未完成时主目录的2.5冒充最终冻结阈值。原初始审计中的四图Selection计数属于 A02 前历史；当前主线为12Dev、每轮3图/3M会话、3Selection、6Test，bw_0085 unused。独立回放仍为3张共同Dev/1Selection/1Test，配置明确标识本阶段而非十轮主线。

补齐了直接 run/resume 已存在阶段时的共同主终态检查，避免跳过首次准备门槛。主十轮未完、端点工作未终态，或 launcher 仍持有独占锁时，入口在复制平台或加载运行时之前停止。STAGE_GATE_TESTS.json 的7项纯夹具验证了该行为及非固定阈值；现有13项 M 变更执行证据夹具继续通过。均未执行模型、Blender、最终评分或阶段实验。
