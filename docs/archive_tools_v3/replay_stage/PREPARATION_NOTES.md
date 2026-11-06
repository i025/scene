# 可选回放入口工程准备记录

仅运行了静态语法、纯 Selection 函数与 prepare/audit 元数据检查；没有模型、Blender、媒体/rubric/附件内容读取。完整 post-stage 执行链尚未实际 smoke，不能凭静态通过声称运行成功。

首次 audit 误把 experiment.lock 当成 JSON，实际主 launcher 用空文件 flock；该次 JSONDecodeError 未触发实验。随后读取 launch.py 修正为真实非阻塞共享锁检查，当前能检测主任务持有独占 flock 并返回 pending。中间初版脚本未单独保存源码快照，现有文件是修正版，不伪造历史快照。

准备协议冻结了 original_H0 与 V2.4 task01/active/H 两个源路径；原始H0与主Hstart共享policy.py，必须披露。完整源码是否在十轮中曾交给M，需要主终态后重新逐请求比对文本。没有已实际执行后代、足量余量或完整陌生性时，finalizer不运行。

后续工程审计进一步收紧“实际执行后代”的证据：仅有较早保留版本和后续父代名称不够。较早接受来源、匹配的 research_request 与完成记录必须同时存在；至少一个变更 Python 文件要对应同一后续 trace 的入口、已记录加载 helper，或名称与源码均匹配的 completed 动作。动作库仅放入提示不算执行，未执行 helper 与说明文件也不算。具体纯测试见 EXECUTION_EVIDENCE_TESTS.json；实际只读核对见 M_CHANGED_CONTENT_CURRENT_AUDIT.json。入口/导入/动作层证据不提供行或分支覆盖，也不能证明改动内容改善了决策。此审计不修改主线 M 接受与保留规则。

主线评分器的原交付图证据修复独立纳入本阶段：`prepare` 在复制旧冻结平台后，才覆盖已校正的主 `bw_evaluate.py`，版本 `original_delivery_metadata_A02`；保留前后源码与 diff，并记录交付证据纯测试。当前仅审查并写入口，未执行 stage prepare/run，尚无实际覆盖副本或新评分结果。
