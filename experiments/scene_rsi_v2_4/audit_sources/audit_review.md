# V2.4 准备：V2.2 十个失败任务独立工程审计

本审计只读既存日志和已冻结代码。没有模型调用、Blender 任务或对原始输出的修改；不是被研究 M 的输入，也不构成新的实验效果。原始 failure_type 和旧 B 分类均保留于 JSON。

## 核心区别

- 10 个失败：H0 8 个，r1/C2 2 个。4 个有明确连接/路由故障证据；4 个受整个 Runtime 的 600 秒预算限制；2 个在期限前因生成程序构建错误且两次执行额度用尽而结束。
- 其中两例 H0 首调用超时约 300 秒，JSONL 明确包含 Connection refused / waiting for network；不能当模型纯推理耗时。C2 两例则是 routing discovery failed 后明确退出 1。
- H0 r1/commons_192968130 是构建失败后剩余 82.246529 秒截断修复 CLI，不是独立 300 秒超时。旧分类 codex_timeout 把两种期限混在一起。
- 三例构建超时的实际子进程额度仅 29.734320、390.001982、454.524263 秒，来自剩余场景预算。没有一次达到 render_started；不能叫 Cycles 渲染超时，也不能无证据归于布尔/显存问题。
- 旧 outer_budget_exhausted=False 只是旧分类器没有在错误文本发现关键词；不能否定 Runtime 600 秒额度已经用尽。最外层 610 秒进程硬终止在这十例中未出现。

## 逐任务

|重复 / H / 场景|原始 failure_type|审计类型|总任务秒 / Runtime 秒|模型/执行次数|
|---|---|---|---:|---:|
|r1 / H0 / commons_104864364|generated_program_or_execution_failure|scene_program_build_errors_after_two_execution_attempts|397.714 / 397.578|3 / 2|
|r1 / H0 / commons_192968130|budget_or_scene_timeout|scene_deadline_limited_repair_cli_after_build_error|600.270 / 600.178|2 / 1|
|r1 / H0 / commons_49800017|model_call_timeout|cli_model_cap_timeout_with_network_failure_evidence|300.287 / 300.165|1 / 0|
|r1 / H0 / commons_92056365|budget_or_scene_timeout|scene_deadline_limited_build_after_world_error|600.122 / 600.030|2 / 2|
|r1 / H0 / commons_96943062|model_call_timeout|cli_model_cap_timeout_with_network_failure_evidence|300.301 / 300.167|1 / 0|
|r1 / r1_C2 / commons_49800017|cli_service_or_process_failure_unresolved|cli_routing_service_failure_exit_1|13.837 / 13.713|1 / 0|
|r1 / r1_C2 / commons_96943062|cli_service_or_process_failure_unresolved|cli_routing_service_failure_exit_1|19.247 / 19.112|1 / 0|
|r2 / H0 / commons_104864364|budget_or_scene_timeout|scene_deadline_limited_build_after_fillet_error|600.156 / 600.030|2 / 2|
|r2 / H0 / commons_31294395|generated_program_or_execution_failure|scene_program_build_errors_after_two_execution_attempts|450.731 / 450.613|3 / 2|
|r2 / H0 / commons_92056365|budget_or_scene_timeout|scene_deadline_limited_first_build|600.168 / 600.035|1 / 1|

## 证据入口与限制

### r1 / H0 / commons_104864364

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/record.json
- 观测：Two execution attempts failed: invalid fillet radius, then absent World. Third complete code response was not executed because the common execution allowance was already spent.
- 限制：Generated-program errors confirmed; no time deadline reached. No useful saved blend.
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/stage_events.jsonl
- 构建 002：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/stage_events.jsonl

### r1 / H0 / commons_192968130

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/record.json
- 观测：First model succeeded; build ran 422.34 seconds and ended with absent World. The repair CLI then received only 82.246529 seconds from the remaining 600-second scene deadline.
- 限制：Repair CLI cause beyond deadline unknown: its JSONL contains only thread.started and turn.started, with no network error. Do not call this a proven provider failure or a standalone 300-second model cap.
- 失败 CLI：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/student_calls/002_1793937258194860408/session.json
- CLI 原始事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/student_calls/002_1793937258194860408/events.jsonl
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_192968130/steps/001/stage_events.jsonl

### r1 / H0 / commons_49800017

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_49800017/record.json
- 观测：First CLI hit its approximately 300-second cap; actual events show Connection refused and repeated waiting for network. No scene program executed.
- 限制：Transport/connectivity fault evidence is direct. Provider/root network cause and remote inference time remain unknown.
- 失败 CLI：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_49800017/student_calls/001_1793937340802126442/session.json
- CLI 原始事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_49800017/student_calls/001_1793937340802126442/events.jsonl

### r1 / H0 / commons_92056365

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/record.json
- 观测：First build ran 391.64 seconds then failed on absent World.color. A successful second model response left only 29.734320 seconds for the second build, which timed out before build_completed.
- 限制：Timed-out build substage is unknown. The first build completed 22 Boolean operations, but that does not prove the final timeout was in a Boolean or explain all construction time.
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/stage_events.jsonl
- 构建 002：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/002/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/002/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_92056365/steps/002/stage_events.jsonl

### r1 / H0 / commons_96943062

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_96943062/record.json
- 观测：First CLI hit its approximately 300-second cap; actual events show Connection refused and repeated waiting for network. No scene program executed.
- 限制：Transport/connectivity fault evidence is direct. Provider/root network cause and remote inference time remain unknown.
- 失败 CLI：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_96943062/student_calls/001_1793933622503570860/session.json
- CLI 原始事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/H0/fixed_version_test/commons_96943062/student_calls/001_1793933622503570860/events.jsonl

### r1 / r1_C2 / commons_49800017

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_49800017/record.json
- 观测：CLI explicitly emitted workspace routing discovery failed and turn.failed, exiting 1 after 13.69 seconds. No Blender execution occurred.
- 限制：Routing failure confirmed; cannot attribute to scene program, image difficulty or a geometric module.
- 失败 CLI：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_49800017/student_calls/001_1793937641182152975/session.json
- CLI 原始事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_49800017/student_calls/001_1793937641182152975/events.jsonl

### r1 / r1_C2 / commons_96943062

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_96943062/record.json
- 观测：CLI explicitly emitted workspace routing discovery failed and turn.failed, exiting 1 after 19.09 seconds. No Blender execution occurred.
- 限制：Routing failure confirmed; cannot attribute to scene program, image difficulty or a geometric module.
- 失败 CLI：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_96943062/student_calls/001_1793933922960442935/session.json
- CLI 原始事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r1/fixed_h/r1_C2/fixed_version_test/commons_96943062/student_calls/001_1793933922960442935/events.jsonl

### r2 / H0 / commons_104864364

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/record.json
- 观测：Initial build failed with invalid fillet radius. Both model calls completed. Second build was given 390.001982 seconds remaining from the common scene deadline and timed out in scene_build.
- 限制：No Boolean-start event or completed scene geometry was saved for the timed-out build. Precise construction substage and timeout root cause remain unknown.
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/001/stage_events.jsonl
- 构建 002：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_104864364/steps/002/stage_events.jsonl

### r2 / H0 / commons_31294395

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/record.json
- 观测：Two execution attempts failed: invalid fillet radius, then absent World. Third complete code response was not executed because the common execution allowance was already spent.
- 限制：Generated-program errors confirmed; no time deadline reached. No useful saved blend.
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/001/stage_events.jsonl
- 构建 002：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/002/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/002/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_31294395/steps/002/stage_events.jsonl

### r2 / H0 / commons_92056365

- 原始记录：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_92056365/record.json
- 观测：One successful model call consumed 145.39 seconds; first build received the remaining 454.524263 seconds and timed out before scene_build_completed.
- 限制：No Boolean-start event or completed scene geometry was saved. This is not a demonstrated 600-second Cycles rendering timeout; rendering never started.
- 构建 001：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/result.json
- 原始报错：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/stderr.log
- 阶段事件：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/results/r2/fixed_h/H0/fixed_version_test/commons_92056365/steps/001/stage_events.jsonl

## 实际预算与版本证据

- 冻结配置：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/code_snapshots/A_frozen/config.json
- 冻结来源：__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/configs/A_freeze.json
- 单场景共同额度：3 次 CLI、2 次执行、600 秒。CLI 单次上限 300 秒，但每次都取剩余场景时间与该上限的较小值；Blender 同样取剩余场景时间与 600 秒的较小值。
- Runtime / LLM / inner_loop / config 的冻结与现用源码直接文本一致；run_scene 函数直接文本一致；H0 与 C2 policy.py 直接文本一致。未做内容哈希。
- 两个构建错误任务的第三次模型返回包含 Python 程序，但已有 2 次执行，policy 在返回之后才检查执行额度，因此没有第三次执行。不能把未执行代码说成修复已通过。
- 没有几何完成快照的超时案例，其具体慢点、CPU竞争、网格/布尔规模、独立“更长预算必定修好”均无法确认。未使用额外运行补证。
- 原始 Q 保持 null；所有失败仍在原始预定分母中，单独的原始失败效用为 0，不回写任何历史分数。

## 有限定位 V2.1

- __SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_1/selection_freeze.json
- __SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_1/backend/harnesses/baseline/policy.py
- __SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_1/candidates/r1/scene_rsi_v2_1/C2/policy.py
- 实际 results 记录数：20；仅定位，不重算其分数。

机器可读详细记录：audit_review.json。每条均保存原始分类、具体会话/执行/阶段路径、实际耗时、异常中的子额度、已证实事实与 unknown。
