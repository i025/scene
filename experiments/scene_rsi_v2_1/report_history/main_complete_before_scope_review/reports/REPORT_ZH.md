# Scene-RSI V2.1 中文实验报告

本轮只比较共享 H0 与 Scene-RSI V2.1，不重跑其他方法。数据为 exploratory，历史联系表曝光，不能宣称严格盲测。

## 实际状态与结果

```json
{
  "state": {
    "phase": "supplement_complete",
    "ledger": {
      "cli_sessions": 65,
      "initial_sandbox_failures": 0,
      "observable_cli_turns": 65,
      "observable_model_rounds": null,
      "tool_calls": 0,
      "known_input_tokens": 3007308,
      "known_output_tokens": 164797,
      "usage_unknown_sessions": 1,
      "render_attempts_upper_bound": 117,
      "renders_completed": 103,
      "device": "CPU",
      "device_mapping_record_counts": {
        "CPU": 171
      },
      "max_cli_sessions": 160,
      "max_render_frames": 600
    }
  },
  "summary": [
    {
      "run_id": "r1",
      "method": "fixed_h0",
      "scheduled": 2,
      "recorded": 2,
      "completed": 2,
      "succeeded": 0,
      "status": "completed",
      "execution_success_rate": 0.0,
      "observed_success_rate": 0.0,
      "conditional_Q": null,
      "task_utility_v2": 0.0,
      "functional_passes": 0,
      "functional_compliance_rate": 0.0,
      "failed": 0,
      "timeout": 2,
      "not_run": 0,
      "unscored_generations": 0
    },
    {
      "run_id": "r1",
      "method": "scene_rsi_v2_1",
      "scheduled": 2,
      "recorded": 2,
      "completed": 2,
      "succeeded": 2,
      "status": "completed",
      "execution_success_rate": 1.0,
      "observed_success_rate": 1.0,
      "conditional_Q": 0.4609588253436397,
      "task_utility_v2": 0.4609588253436397,
      "functional_passes": 2,
      "functional_compliance_rate": 1.0,
      "failed": 0,
      "timeout": 0,
      "not_run": 0,
      "unscored_generations": 0
    },
    {
      "run_id": "r2",
      "method": "fixed_h0",
      "scheduled": 2,
      "recorded": 2,
      "completed": 2,
      "succeeded": 0,
      "status": "completed",
      "execution_success_rate": 0.0,
      "observed_success_rate": 0.0,
      "conditional_Q": null,
      "task_utility_v2": 0.0,
      "functional_passes": 0,
      "functional_compliance_rate": 0.0,
      "failed": 0,
      "timeout": 2,
      "not_run": 0,
      "unscored_generations": 0
    },
    {
      "run_id": "r2",
      "method": "scene_rsi_v2_1",
      "scheduled": 2,
      "recorded": 2,
      "completed": 2,
      "succeeded": 0,
      "status": "completed",
      "execution_success_rate": 0.0,
      "observed_success_rate": 0.0,
      "conditional_Q": null,
      "task_utility_v2": 0.0,
      "functional_passes": 0,
      "functional_compliance_rate": 0.0,
      "failed": 0,
      "timeout": 2,
      "not_run": 0,
      "unscored_generations": 0
    }
  ],
  "ledger": {
    "cli_sessions": 65,
    "initial_sandbox_failures": 0,
    "observable_cli_turns": 65,
    "observable_model_rounds": null,
    "tool_calls": 0,
    "known_input_tokens": 3007308,
    "known_output_tokens": 164797,
    "usage_unknown_sessions": 1,
    "render_attempts_upper_bound": 117,
    "renders_completed": 103,
    "device": "CPU",
    "device_mapping_record_counts": {
      "CPU": 171
    },
    "max_cli_sessions": 160,
    "max_render_frames": 600
  }
}
```

## 实际候选和 Selection

|研发|候选|类型|开发成功/预定|Selection成功/预定|绝对资格|Selection条件Q|选择保留|M源码改变|
|---|---|---|---|---|---|---|---|---|
|r1|C1|H-only|0/1|0/1|False|None|False|False|
|r2|C1|H-only|1/1|0/1|False|None|False|False|
|r1|C2|H-only|1/1|1/1|True|0.4173230039975933|True|False|
|r2|C2|H-only|1/1|1/1|True|0.3952040292567605|True|False|

条件Q缺测为None/null，不等于0。H0失败不放宽候选资格；不合格H0仅为fallback。未选候选没有终测，不能称其终测联合通过。

## 选中版本的逐场景 Test

|研发|方法|版本|场景|状态|实测Q|独立任务效用|功能通过|设备|
|---|---|---|---|---|---|---|---|---|
|r1|fixed_h0|H0|commons_189918915|timeout|None|0.0|False|CPU|
|r1|fixed_h0|H0|commons_80372956|timeout|None|0.0|False|CPU|
|r1|scene_rsi_v2_1|C2|commons_189918915|completed|0.40317078867799094|0.40317078867799094|True|CPU|
|r1|scene_rsi_v2_1|C2|commons_80372956|completed|0.5187468620092884|0.5187468620092884|True|CPU|
|r2|fixed_h0|H0|commons_189918915|timeout|None|0.0|False|CPU|
|r2|fixed_h0|H0|commons_80372956|timeout|None|0.0|False|CPU|
|r2|scene_rsi_v2_1|C2|commons_189918915|timeout|None|0.0|False|CPU|
|r2|scene_rsi_v2_1|C2|commons_80372956|timeout|None|0.0|False|CPU|

完整配对差见metrics/paired_test.csv。失败Q保留null；失败效用0是另一个字段。仅双方成功时计算条件Q差。joint_improvement.csv单位为选中流程的scene/run配对，不是所有原始候选的终测改进率。两次研发复用同两个Test来源组，不是四个独立场景。

## H 与 M 实际变化

实际产生 4 个正式共享候选，其中 M 源码变化 0 个。本轮没有新 M 参与后续提案，未发生元级程序自修改；不能报告元能力提升。

单图P保存在results各scene.py/build.py与steps；共享H/M在candidates保存完整源码和diff。外层工程师的runner修复不是M自修改。

## 运行偏离与成本

四次原提案在模型提交前触发600KB限制，未生成H/M候选，原始失败与旧选择保存在attempt_archive/payload_cap_failure。payload_fix1保留全部ID并限制128份数值详情，真实包回归测试通过；这些额外诊断全部计入同一个160 CLI/600帧预算。一个H0 Test生成曾提前提交，未查看媒体/代码/质量、未回流研发，只在新的选择冻结后评价并明确复用。该项属于事后as-run修订，不宣称严格盲测。见protocol.md和configs/payload_evidence_fix1.json。

成本按实际CLI调用、CLI返回usage、渲染和设备记录，见metrics/cost_by_phase.csv、calls.csv及ledger.json。CLI会话不等于一次底层模型推理；缺失usage、实际返回模型、费用、服务排队时间保持unknown/null。CPU两线程单重任务，无GPU；网络等待和CAD计算混在端到端时间中，不据此宣称算法速度优势。

## 机制证据与边界

M 的 plan_probes 选择真实对象和测试，runner 执行，真实观测进入 M.plan_patch。见 candidates 下 stage1/stage2、observations、changes.diff。M-only 不计 H 改善；M 被执行不证明元能力提高。

结构校准涵盖正确组合、脱离父对象、破坏支撑、共享材质误改、独立编辑和表面相交。自然图像无三维真值；声明部件完整性不等于参考对象完整性。支撑是归一化 AABB 近似，Mesh BVH 仅测三角表面相交，不能判断所有穿插、包含或合理接缝。

主 Q 沿用 V1 公式；未测量指标为 null，执行失败效用单独为零，此Q效用不包含全部功能要求，功能合规另报。条件质量与全分母效用分别报告；多视角不计独立样本。只有 2 个研发重复，不作普遍优势或显著性结论。机械编辑与文字编辑分别保留，文字编辑只按预定少量终测场景执行。

## 可控诊断比较

五个夹具，绿色/红色分别是已执行测试中的命中/未命中；目标组或相关部件命中不等于精准视觉定位。对象计数按材质非目标方块修正，旧宽泛字段保留，见configs/diagnostic_object_count_correction.json。图像定位模块命中和M第二阶段最终模块精确命中单列，后者双方均仅1/5。V2.1新增5次定位调用，双方辅助共享程序各1次修复调用，实际成本并不相同。源代码API契约本身提供修复提示；辅助helper通过不代表自然图像重建H改进。家具尺度定位正确仍可能没有正向探测效果；隐藏对象的隔离实验不自动恢复可见性。原始来源为 tests/diagnosis/comparison.json、shared_patch_transfer.json，统计表 metrics/diagnostic_comparison.csv、controlled_shared_patch.csv，脚本 tests/diagnose.py 与 analyze.py。

## 图与数据

每张图由 analyze.py 从 metrics/scene_metrics.csv、candidates.csv、paired_test.csv、calls.csv、meta_participation.csv 与原始 JSON 重画。Figure1 按冻结顺序纳入全部测试场景；Figure2 采用按路径排序的首个正式诊断，无成功筛选；Figure3 采用首个有机械渲染的终测场景。

![cost_gain](../figures/cost_gain.png)

![diagnostic_comparison](../figures/diagnostic_comparison.png)

![diagnostic_fixture_contact](../figures/diagnostic_fixture_contact.png)

![failure_stages](../figures/failure_stages.png)

![figure1_r1](../figures/figure1_r1.png)

![figure1_r2](../figures/figure1_r2.png)

![figure2_diagnostic](../figures/figure2_diagnostic.png)

![figure3_calibration](../figures/figure3_calibration.png)

![figure3_edits](../figures/figure3_edits.png)

![figure3_hierarchy](../figures/figure3_hierarchy.png)

![figure3_text_editor](../figures/figure3_text_editor.png)

![figure4_evolution](../figures/figure4_evolution.png)

![figure5_meta](../figures/figure5_meta.png)

![multiview](../figures/multiview.png)

![statistics](../figures/statistics.png)
