# Scene-RSI V2.1 中文实验报告

本轮只比较共享 H0 与 Scene-RSI V2.1，不重跑其他方法。数据为 exploratory，历史联系表曝光，不能宣称严格盲测。

## 实际状态与结果

```json
{
  "state": {
    "phase": "running_scene",
    "method": "fixed_h0",
    "run_id": "r1",
    "candidate_id": "H0",
    "scene_id": "commons_187101683",
    "split": "development",
    "folder": "__EXPERIMENT_ROOT__/results/r1/fixed_h0/H0/development/commons_187101683"
  },
  "summary": [
    {
      "run_id": "r1",
      "method": "fixed_h0",
      "scheduled": 2,
      "recorded": 0,
      "completed": 0,
      "succeeded": 0,
      "status": "not_started",
      "execution_success_rate": null,
      "observed_success_rate": null,
      "conditional_Q": null,
      "task_utility_v2": null,
      "functional_passes": 0,
      "functional_compliance_rate": null,
      "failed": 0,
      "timeout": 0,
      "not_run": 2
    },
    {
      "run_id": "r1",
      "method": "scene_rsi_v2_1",
      "scheduled": 2,
      "recorded": 0,
      "completed": 0,
      "succeeded": 0,
      "status": "not_started",
      "execution_success_rate": null,
      "observed_success_rate": null,
      "conditional_Q": null,
      "task_utility_v2": null,
      "functional_passes": 0,
      "functional_compliance_rate": null,
      "failed": 0,
      "timeout": 0,
      "not_run": 2
    },
    {
      "run_id": "r2",
      "method": "fixed_h0",
      "scheduled": 2,
      "recorded": 0,
      "completed": 0,
      "succeeded": 0,
      "status": "not_started",
      "execution_success_rate": null,
      "observed_success_rate": null,
      "conditional_Q": null,
      "task_utility_v2": null,
      "functional_passes": 0,
      "functional_compliance_rate": null,
      "failed": 0,
      "timeout": 0,
      "not_run": 2
    },
    {
      "run_id": "r2",
      "method": "scene_rsi_v2_1",
      "scheduled": 2,
      "recorded": 0,
      "completed": 0,
      "succeeded": 0,
      "status": "not_started",
      "execution_success_rate": null,
      "observed_success_rate": null,
      "conditional_Q": null,
      "task_utility_v2": null,
      "functional_passes": 0,
      "functional_compliance_rate": null,
      "failed": 0,
      "timeout": 0,
      "not_run": 2
    }
  ],
  "ledger": {
    "cli_sessions": 14,
    "initial_sandbox_failures": 0,
    "observable_cli_turns": 14,
    "observable_model_rounds": null,
    "tool_calls": 0,
    "known_input_tokens": 621684,
    "known_output_tokens": 22866,
    "usage_unknown_sessions": 0,
    "render_attempts_upper_bound": 49,
    "renders_completed": 47,
    "device": "CPU",
    "device_mapping_record_counts": {
      "CPU": 96
    },
    "max_cli_sessions": 160,
    "max_render_frames": 600
  }
}
```

## 机制证据与边界

M 的 plan_probes 选择真实对象和测试，runner 执行，真实观测进入 M.plan_patch。见 candidates 下 stage1/stage2、observations、changes.diff。M-only 不计 H 改善；M 被执行不证明元能力提高。

结构校准涵盖正确组合、脱离父对象、破坏支撑、共享材质误改、独立编辑和表面相交。自然图像无三维真值；声明部件完整性不等于参考对象完整性。支撑是归一化 AABB 近似，Mesh BVH 仅测三角表面相交，不能判断所有穿插、包含或合理接缝。

主 Q 沿用 V1 公式；未测量指标为 null，失败效用单独为零。条件质量与全分母效用分别报告；多视角不计独立样本。只有 2 个研发重复，不作普遍优势或显著性结论。机械编辑与文字编辑分别保留，文字编辑只按预定少量终测场景执行。

## 可控诊断比较

五个夹具，绿色/红色分别是已执行测试中的命中/未命中；目标组或相关部件命中不等于精准视觉定位。V2.1新增5次定位调用，双方辅助共享程序各1次修复调用，实际成本并不相同。源代码API契约本身提供修复提示；辅助helper通过不代表自然图像重建H改进。家具尺度定位正确仍可能没有正向探测效果；隐藏对象的隔离实验不自动恢复可见性。原始来源为 tests/diagnosis/comparison.json、shared_patch_transfer.json，统计表 metrics/diagnostic_comparison.csv、controlled_shared_patch.csv，脚本 tests/diagnose.py 与 analyze.py。

## 图与数据

每张图由 analyze.py 从 metrics/scene_metrics.csv、candidates.csv、paired_test.csv、calls.csv、meta_participation.csv 与原始 JSON 重画。Figure1 按冻结顺序纳入全部测试场景；Figure2 采用按路径排序的首个正式诊断，无成功筛选；Figure3 采用首个有机械渲染的终测场景。

![diagnostic_comparison](../figures/diagnostic_comparison.png)

![diagnostic_fixture_contact](../figures/diagnostic_fixture_contact.png)

![figure2_diagnostic](../figures/figure2_diagnostic.png)

![figure3_calibration](../figures/figure3_calibration.png)

![figure3_edits](../figures/figure3_edits.png)

![figure4_evolution](../figures/figure4_evolution.png)

![figure5_meta](../figures/figure5_meta.png)

![statistics](../figures/statistics.png)
