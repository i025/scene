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
| Selection冻结后统一Test | pilot.main | protocol_frozen、selection_freeze、Test逐场景 | Figure1、paired_test.csv | 1/1/2场景、2研发，exploratory历史曝光；无足够样本显著性结论 |
| pending不写0% | analyze.terminal_summary/execution_state | report_contracts、terminal_summary、scheduled_slots | statistics | 全分母结果仅全部结束时给；观察分母另报，失败Q保持null |
| 成本和失败完整可查 | backend/codex_wrapper/budget | request/session/events/stderr/render_ledger | calls.csv、cost_gain | actual_model未知时unknown；无模型价格或隐含推理轮数猜测 |

所有V2.1相对路径以 experiments/scene_rsi_v2_1 为根。可离线报告 reports/index.html，中文 reports/REPORT_ZH.md；统计源CSV在metrics，重画脚本analyze.py。Release大附件见 artifacts_index_v2_1.csv，未上传状态以该表与UPLOAD_SUMMARY_V2_1.md为准。
