# 教师一次自修改：审查索引

这是证据索引，不预判教师质量。所有相对路径指向本轮；旧实验原样保留。

|主张|对应代码|原始数据|图表|局限或缺失证据|
|---|---|---|---|---|
|固定学生、12项真实任务|[runner](../experiments/teacher_self_evolution_human_pilot/runner.py)、[冻结源码](../experiments/teacher_self_evolution_human_pilot/code_snapshots/preformal)|[逐任务](../experiments/teacher_self_evolution_human_pilot/metrics/tasks.csv)、[计划](../experiments/teacher_self_evolution_human_pilot/plan.json)|[全开发](../experiments/teacher_self_evolution_human_pilot/figures/development_contact.png)、[全比较](../experiments/teacher_self_evolution_human_pilot/figures/comparison_contact.png)|技术交付不等于质量合格；四图单轨迹|
|R2仅语言跨轮|[输入控制](../experiments/teacher_self_evolution_human_pilot/runner.py)|[权限和附件核对](../experiments/teacher_self_evolution_human_pilot/metrics/provenance_audit.json)、每任务student_input及request|[HTML](../experiments/teacher_self_evolution_human_pilot/reports/index.html)|外部隐藏系统提示及底层请求不可完全观测|
|一次M0→M1共享变更|[M0](../experiments/teacher_self_evolution_human_pilot/teachers/M0/teacher.py)、[M1](../experiments/teacher_self_evolution_human_pilot/teachers/M1/teacher.py)、[diff](../experiments/teacher_self_evolution_human_pilot/self_modification/M0_to_M1.diff)|[唯一原提案](../experiments/teacher_self_evolution_human_pilot/self_modification/proposal_1.json)、[实际指导链](../experiments/teacher_self_evolution_human_pilot/metrics/guidance_chains.json)|[源码审查](../experiments/teacher_self_evolution_human_pilot/reports/M_SELF_MODIFICATION_REVIEW_ZH.md)|提示策略修改，未证明更强；M1.self_modify未参与后续自修改|
|内部错误和修复真实保留|[固定Runtime](../experiments/teacher_self_evolution_human_pilot/backend/runtime.py)|[全部构建](../experiments/teacher_self_evolution_human_pilot/metrics/build_attempts.csv)、steps/*/result.json|[HTML内展开](../experiments/teacher_self_evolution_human_pilot/reports/index.html)|首建失败的任务没有学生看中间渲染；最终交付不再额外看图|
|成本与资源|[CLI适配器](../experiments/teacher_self_evolution_human_pilot/backend/codex_wrapper.py)、[进程控制](../experiments/teacher_self_evolution_human_pilot/backend/processes.py)|[调用](../experiments/teacher_self_evolution_human_pilot/metrics/cli_calls.csv)、[阶段时间](../experiments/teacher_self_evolution_human_pilot/metrics/timing.csv)、[角色成本](../experiments/teacher_self_evolution_human_pilot/metrics/cost_by_role.csv)|[中文报告](../experiments/teacher_self_evolution_human_pilot/reports/REPORT_ZH.md)|usage可见、费用未知；精确底层请求数unknown|
|没有自动质量判断|[报告](../experiments/teacher_self_evolution_human_pilot/report.py)、[配置](../experiments/teacher_self_evolution_human_pilot/config.json)|[技术汇总](../experiments/teacher_self_evolution_human_pilot/metrics/summary.json)|[人工HTML](../experiments/teacher_self_evolution_human_pilot/reports/index.html)|尚无人工意见，不做自动胜负、分数或显著性声明|

完整日志、全部.blend和内部渲染在 [Release](https://github.com/i025/scene/releases/tag/teacher-self-evolution-human-pilot-2026-11-15)；逐文件上传状态见 [artifacts_index_teacher_human.csv](../artifacts_index_teacher_human.csv)。原图按各自CC许可提供，[归属](../experiments/teacher_self_evolution_human_pilot/SOURCE_ATTRIBUTION.md)不覆盖第三方原许可。

离线重画：在解压后的实验目录执行 `python runner.py report`（Python+Pillow+PyYAML），不调用模型或Blender。报告脚本重画技术汇总和两张联系表；手工审查附记保存在单独文件及Git历史。
