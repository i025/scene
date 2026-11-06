# Scene-RSI V2.3 审查索引

这里按主张定位证据，不预先判定方法有效。所有路径相对仓库根目录。旧 V1/V2/V2.1/V2.2 数据不覆盖。

|主张/待检验问题|对应代码|原始数据|图表|局限或缺证据|
|---|---|---|---|---|
|实际采用竞争假设的事前预测选择探测|experiments/scene_rsi_v2_3/meta.py plan_probes|tasks/*/common_diagnosis/response.txt、*/stage1.json、*/probes/*/request.json|figure1_executed_pipeline.png、figure4_cases.png|允许无预测分歧而不探测；框架实现不代表正式案例已展现有效区分|
|真实观测返回可执行 M 后更新判断|meta.py plan_patch；experiment.py run_arm|*/observations.json、*/stage2.json、metrics/probe_predictions.csv|figure2_diagnosis.png、figure4_cases.png|区间匹配只是当前解释集合中的支持/矛盾；不是唯一因果证明|
|工具能正确测量已知故障|fixtures.py run_probe；probe_calibration.py、calibrate.py、extended_calibration.py|calibration/probe_calibration.json、calibration/calibration.json、calibration/extended/results.json；全部.blend在Release|calibration/probes/*/probe.png|人工可控真值；仅证明工具与固定测试灵敏，不等于模型会选对工具|
|实际共享 H 修复能迁移|实际SceneAct backend/sceneact/blender_scene.py；fixtures.py check_case；tasks/*/*/candidate.py|metrics/scene_metrics.csv、*/evaluation.json、*/source_signature.json、*/transfer_signature.json、changes.diff|figure3_repair.png、all_cases_contact.png|两个参数化模板，不是十个独立自然场景；全源码可见可能让编码器无需诊断直接修复|
|修复未破坏必要原功能|fixtures.py compare；当前H编辑接口|每项 required/applicable/measured_pass/gate_pass；baseline_checks/new_regressions|figure3_repair.png、结构校准图|回归率条件于执行成功；另列执行失败/无效程序/未测，不能把服务故障视为能力退化|
|预算、成本与信息权限对齐|backend/codex_wrapper.py、budget.py；experiment.py共同提示|metrics/calls.csv、call_totals.json、request/session/events/stderr、stage1/2|figure5_cost.png|共同初诊只实际调用一次，三组分摊1/3；Structured零探测成本单列；实际探测次数匹配子集另存|
|是否产生主动诊断下游收益|相同编码模板与完整候选diff|metrics/summary.json、scene_metrics.csv、actual_probe_count_matched_subset.json|figure2/3/5|若三组修复率相同或Active无探测，不能声称共享研发优势|
|M是否自动演化、元能力是否提升|本轮meta.py是工程实现；没有后代生成代码|FINAL_STATUS.json、configs/freeze.json|无跨代上涨图|没有自动M后代或冻结陌生起点回放，完全不支持此主张|

主要入口：[中文报告](../experiments/scene_rsi_v2_3/reports/REPORT_ZH.md)、[HTML](../experiments/scene_rsi_v2_3/reports/index.html)、[冻结协议](AS_RUN_PROTOCOL_V2_3.md)、[逐任务CSV](../experiments/scene_rsi_v2_3/metrics/scene_metrics.csv)、[全部大产物索引](../artifacts_index_v2_3.csv)。

完整 prompts/JSONL/stderr、所有.blend按fixed/structured/active/shared-evidence分包：
https://github.com/i025/scene/releases/tag/scene-rsi-v2.3-2026-11-06

上传状态以 UPLOAD_SUMMARY_V2_3.md 与 V2_3_RELEASE_UPLOAD_STATE.json 为准；链接存在不表示已经上传。
