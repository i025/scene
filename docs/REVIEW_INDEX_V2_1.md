# Scene-RSI V2.1 审查索引

证据索引，不预先判定科研机制有效。旧V1/V2不被新评分覆盖。

| 主张 | 对应代码 | 原始数据 | 图表 | 局限或缺失 |
|---|---|---|---|---|
| 原V2已停止，未误启重复任务 | V2.1 configs/v2_status_at_start.json | V2原始13正式记录及pipeline最后退出 | configs/v2_completed_records_at_start.csv | 另有2个旧smoke记录；stale running_scene不是活进程 |
| 候选先绝对资格，再质量排序 | pilot.py eligible_scene/summarize/better | tests/contracts.json、各Selection functional/checks、archive.json | Figure4 | H0允许不合格fallback但不叫功能通过；V2旧选择不回写 |
| M读取明确预算、对象ID和失败阶段 | strategies.py、diagnostics.py、pilot.py | stage1、stage2、failure_evidence、真实CLI/步骤错误 | Figure2 | 服务错误与算法失败分开；缺blend不做几何 |
| 图像差异映射真实对象/组再探测 | diagnostics.localize、inspect_blend.projected_box | 五夹具localization调用、真实附件、目标、探测PNG | diagnostic_fixture_contact、diagnostic_comparison | 边框不是分割；unknown允许；组或部件命中不代表唯一病因 |
| 实际观测进入可执行M第二阶段 | strategies.py plan_patch、pilot.propose | observations、stage2、源码diff | Figure2 | 图片定位模块命中与M第二阶段模块命中分别列；分数敏感性不是唯一因果 |
| 已知结构与编辑错误被检测 | regression.py、tests/calibrate.py | calibration.json、contracts.json | Figure3 calibration | 合成结构真值；自然图像无真实3D真值，AABB支撑近似 |
| 同预算辅助共享代码修复可迁移执行 | tests/repair_fixture.py、validate_fixture_patch.py | 双方candidate.py/diff、shared_patch_transfer.json | controlled_shared_patch.csv | API契约提供提示；辅助helper不是自然图像H，双方均可成功，不能据此宣称优势 |
| M选择研发测试，最终验收不变 | pilot.execute_plan、regression.MENU | pre/post regression、post_patch_feedback | Figure3/4 | 不允许M关闭最终不利检查 |
| H-only/M-only/H+M与后续M使用 | pilot.candidate_type/main | contracts、候选proposal_result/source/diff | Figure5、meta_participation.csv | stub测试不冒充真实M后代；实际代码变化和能力改进不同 |
| Selection冻结后才评价Test（有提前生成偏离） | pilot.main | protocol_frozen、selection_freeze、Test逐场景 | Figure1、paired_test.csv | 1/1/2来源、2研发；其中吊灯是建筑细节；一个H0 Test生成提前提交，冻结后才评分；exploratory |
| pending不写0% | analyze.terminal_summary/execution_state | report_contracts、terminal_summary、scheduled_slots | statistics | 全分母结果仅全部结束时给；观察分母另报，失败Q保持null |
| 成本和失败完整可查 | backend/codex_wrapper/budget | request/session/events/stderr/render_ledger | calls.csv、cost_gain | actual_model未知时unknown；无模型价格或隐含推理轮数猜测 |

所有V2.1相对路径以 experiments/scene_rsi_v2_1 为根。可离线报告 reports/index.html，中文 reports/REPORT_ZH.md；统计源CSV在metrics，重画脚本analyze.py。Release大附件见 artifacts_index_v2_1.csv，未上传状态以该表与UPLOAD_SUMMARY_V2_1.md为准。

## 完成后的可审查结论

|主张|对应代码|原始数据|图表|局限或缺失证据|
|---|---|---|---|---|
|最终选中流程成功2/4，H0为0/4|analyze.py terminal_summary|results各record.json；metrics/terminal_overview.csv、paired_test.csv|Figure1 r1/r2、statistics|两个来源×两次研发；没有双方成功配对，不能量化条件视觉增益|
|两个C2通过绝对Selection资格|pilot.py eligible_scene/better|selection_freeze.json；metrics/candidates.csv、functional_checks.csv|Figure4|H0两次Selection失败；不据此降低候选绝对门槛|
|原始失败不被零分覆盖|analyze.py execution_state|scene_metrics_flat.csv；failure_stages.csv|failure_stages|11个正式重建失败：10 Blender阶段、1 Codex超时；服务/执行不是同一种算法退化|
|4个正式候选只有H变化|候选policy.py/system.txt/meta.py、changes.diff|proposal_result.json；meta_participation.csv|Figure5|M0确实执行但源码未变；无元后代、无冻结M回放、无MetaImp结论|
|两次固定文字编辑均保持非目标|supplement.py、text_edit_worker.py|text_edit/status.json、text_edit.json；metrics/text_edits.csv|figure3_text_editor|仅两个有效产物；无H0可编辑产物，无法形成配对编辑增益|
|任务范围混合且不事后改分|analyze.py scope_rows|configs/posthoc_scope_review.json、manifest；posthoc_scope_sensitivity.csv|Figure1按原顺序全展示|仓库是场景，另一图是吊灯/天花细节；组合检查原先可选，实测通过但不回写为硬约束|
|payload修订完整保留|model_evidence.py、pilot.py；code_snapshots/payload_fix1|attempt_archive/payload_cap_failure；candidate_attempts.csv；evidence_cap.json|成本图计入旧失败|四次超包均未提交候选模型；提前生成的H0 Test只冻结后评价，属于as-run偏离|
|全部新增调用与资源可查|backend/budget.py/codex_wrapper.py|ledger.json、calls.csv、cost_by_phase.csv|cost_gain|65会话、1 usage缺失；CLI轮次≠底层推理轮数，实际返回模型未知、费用null；CPU2线程0GPU|

## 图表来源与选择规则

- Figure1：manifest固定全部Test顺序，scene_metrics_flat.csv、原reference/final.png；失败空白，不挑赢家。
- Figure2：首个正式stage2，candidates/r1/scene_rsi_v2_1/C1/observations.json、stage2.json、changes.diff；子代Development实际失败，不能编造诊断收益。
- Figure3 calibration：tests/calibration.json、metrics/calibration_checks.csv；8个已知真值夹具，不是自然图像三维精度。
- Figure3 hierarchy/mechanical/text：第一个有相应真实产物的Test；functional/scene_structure.json、text_edit.json、metrics/hierarchy_case.csv、text_edits.csv。文字指令在报告和status.json中，机械操作另列。
- Figure4/cost：全部4真实候选与H0，archive.json、metrics/candidates.csv、development_cost_points.csv；失败效用零是独立字段。初始超包失败见candidate_attempts.csv且成本计入。
- Figure5：每个真实proposal_result和stage1/stage2、metrics/meta_participation.csv；实际没有M源码diff，不画虚构跨代能力曲线。
- diagnostic_comparison：tests/diagnosis/comparison.json、ground_truth_evaluator_only.json、metrics/diagnostic_comparison.csv；旧宽泛对象计数保留，适用对象率为2/4对4/4，相机无需对象；旧目标决策3/5对5/5字段保留。M第二阶段精确模块命中另列，双方均1/5。
- statistics/failure_stages：terminal_overview.csv、calls.csv、failure_stages.csv；全体预定终测、有效条件质量及边界失败分开。

重画统一入口 scripts/offline_v2_1.py → analyze.py。原报告被修正时保存旧版于report_history，原record.json的实测分数不变。完整CLI附件、所有blend、失败/未选候选随各运行tar.gz；上传与缺失状态以artifacts_index_v2_1.csv和UPLOAD_SUMMARY_V2_1.md为准。

术语：terminal_summary中completed计已结束的终态记录，包含失败；succeeded才是执行成功数。逐场景execution_state区分completed/timeout/failed等状态，不能混用。归档验证结果见V2_1_ARCHIVE_VALIDATION.json。
