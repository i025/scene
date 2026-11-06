# V2.2 审查索引

这是证据导航，不预先判定方法有效。以下相对路径以 `experiments/scene_rsi_v2_2/` 为根。

|主张/问题|对应代码|原始数据|图表|局限/缺失|
|---|---|---|---|---|
|固定真实H0与r1/C2|fixed_h、source_versions、A_frozen|configs/A_freeze.json、H0_to_r1_C2.diff|Figure1全部6来源×2重复|policy相同，system含多种规则；非新搜索，不能隔离诊断因果|
|24个新来源重复任务实际执行|experiment.py、pilot.run_scene|A_schedule、results各record/status/usage/trajectory|Figure1、Figure2|6来源不是12独立场景，当前资格审查接触，不严格盲测|
|质量、执行和失败零效用分开|backend/evaluate.py、analyze.py|A_scene_metrics.csv、A_paired_metrics.csv、A_summary.json|Figure2、Figure5 A|条件均值与双方成功配对有不同分母，失败Q保持null|
|功能门槛不因H0失败降低|pilot.functional、regression.gate|functional/summary.json、原任务expected_composite|Figure2|机械操作/声明完整性，不是自然图像语义完整性或文字编辑|
|观察构造/渲染和实际Boolean|backend/telemetry、SceneCompiler|steps/stage_events.jsonl、A_failure_stages.csv、A_COMPLEXITY_AUDIT|成本图、全部失败空格|SceneAct事件不是所有可能bpy操作；失败Mesh数量被删失，不能声称必然减少Boolean|
|M得到明确预算和真实对象ID|strategies.py、initial_meta、pilot.execute_plan|diagnostic_contracts、target_plan、target_probe_64|真实目标探测PNG|64px仅验收，不混入正式对照|
|实际观测进入可执行M第二阶段|meta.plan_probes/plan_patch|case*/stage1、observations、stage2含空观测回放|Figure4、C_diagnosis.csv|事前方向区分不等于唯一因果；unresolved允许|
|不是最大Q增量直接择因|M22策略、公共localize|事前alternatives/predicted_direction和实际probe数据|Figure3/4|视觉解释仍可错误；不能靠字段增加认定科研收益|
|已知结构/编辑错误实际检测|tests/calibrate.py、regression.py|tests/calibration.json、Blender process与fixture.blend|控制场景结构证据|8个验收条件，不当作8个自然场景样本|
|M选择测试真正影响执行|diagnosis_runner、controlled.material_regression|各M plan.regressions、regression和实际shared_API材料测试|Figure3/4|研发适应性菜单不改变固定最终6项验收|
|同工具/证据/修复机会|protocol_BC、BC_freeze|common_localization、两份固定M源码、repair_call日志|Figure3、Figure5 C|同上限不等实际token；共同视觉实际10次，只分摊不双计|
|真实共享代码修复与有限迁移|case*/candidate.py、changes.diff、controlled.evaluate|repair_evaluation.json、source/transfer_structure、post_patch_evidence|Figure4/5 C|API提示可能导致天花板；辅助helper不是自然图像H|
|旧定位不冒充修改后事实|pilot后补分支、diagnosis_runner|post_patch_evidence中的historical/current对象/新检查|Figure4与原始JSON|没有新增修改后视觉定位；diff关键词仅近似风险|
|没有自动M能力提升结论|engineering scope、M源码diff|无自动后代、无MetaImp数据|不画跨代元能力图|工程师修复M不能作为元自修改|
|成本、资源和服务故障完整|CLI adapter/budget、resources|calls.csv、ledger、两次recovery、原始stderr|Figure5、A_failure_stages|底层模型轮数/费用unknown，CLI超时原因未细分|

Figure1按冻结manifest顺序全展示，失败空白并标注。Figure2/5 A源为A_scene_metrics.csv与A_paired_metrics.csv；Figure3/5 C源为C_diagnosis.csv和C_summary.json。Figure4按预定规则选首个V2.2正确模块且修复成功，再选首个实际模块错误/修复失败，模块失败与编码器修复成功明确分开。所有统计图由analyze.py重画；实际案例选择记录在metrics/diagnostic_case_selection.json。

完整日志、全部blend与失败产物见仓库 artifacts_index_v2_2.csv 对应Release包。HTML使用相对路径和本地资源；中文报告在reports/REPORT_ZH.md。原始记录不可因汇总/归档改写。实际上传与可访问性以UPLOAD_SUMMARY_V2_2.md及远端核对收据为准。

## 完成后观察（非预先宣判）

- 固定H执行与必需功能：4/12→10/12；条件Q 0.444996→0.441361；4双成功配对差+0.021329；效用0.148332→0.367801，来源A_summary/paired_metrics。
- 对象top1双方6/8；第二阶段精确模块2/10→6/10、相关模块8/10→6/10。不能仅以新标签词汇得出整体优势。
- 事前预测方向区分0/5双方相同；观测改变模块6/10双方相同。机制执行证据与有效诊断证据不同。
- 源修复和有限helper迁移双方10/10，强API提示形成天花板；未观察到修复成功率收益。
- 全轮94 CLI、已知input2397787/output243045、5usage未知；163渲染尝试上界/148完成帧；CPU2线程0GPU，无自动M后代。
- 全部4Release包和核心10项远端内容已实际匿名读取。3022产物路径覆盖见V2_2_ARCHIVE_COVERAGE；公开PNG/blend检查及上传状态见对应V2_2收据。
