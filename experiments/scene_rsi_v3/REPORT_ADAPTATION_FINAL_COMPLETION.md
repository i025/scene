# 终测收尾的事后报告补充

按本次用户要求增加 final_statistics.py 和 audit_m07.py。它们只读原始记录、图片、源码和真实动作轨迹，不调用模型或Blender，不改变已冻结的评分、H/M选择、样本数或预算。

新增统计属于事后整理，不称为原协议预注册：保留原有完成任务条件均值，另列每来源合并两次重复后来源等权均值；配对差仍只比较同一repeat双方成功且有相应实测指标的生成，并在来源内部先取平均。新增95%来源percentile bootstrap以六个来源为单位重采样10,000次，本地固定种子20261111只用于重采样，不控制远端模型采样。不足六个来源的指标不给六来源区间。小样本探索性区间不作为普遍优势或统计显著性证明。

未开始、评审服务失败、缺测保持null。仅闭合的生成失败在独立BW_utility字段中赋0，原始Q/PSNR/SSIM/LPIPS/DINO/BW不回写为0。来源差、重复波动、必需功能、执行率和调用/渲染/耗时分开。原始24项输出保留所有失败。

M07审查覆盖全部六次appearance_audit，按时间排序；动作源码、动作索引注册、未变化的meta.py和后续H08/unchanged/H10分别记录，不将动作调用当成元能力提升。最终H04早于M07，不能将H04收益归因于M07。

公开图不嵌入没有再分发许可的BW原始参考。含真实参考图的完整联系表生成到实验目录之外的服务器 work/scene_v3_archive/private_final_test_contact_sheet.png，明确不打包；Git/Release中的公开图保留明确标注的Reference列。所有生成场景和允许公开的重建渲染不受此限制。

原有实际执行生成器/评价器留在A04/A05源码快照中；A06只增加终测恢复入口。原分析脚本及本次报告diff见preparation/final_completion_01/。归档阶段只补原13包缺失的6包，baseline和round01–10按显式运行版本复用，最终preparation/final两个组另作增量包，避免重复上传；附件索引逐项保存实际URL与状态，不做哈希验证。

## 修正外部评审渲染的耗时汇总遗漏

发现旧get_timings仅读取*process.json，漏读BW逐视角实际保存的*_timing.json（如author_timing.json、wide_01_timing.json）。现在同时读取这两类互不重叠的进程测量文件，仍要求记录含seconds和command；数值指标子阶段另外保留。新增的是已真实发生的BW渲染/检查耗时和CPU/RSS证据，不是新执行，也不改变任何质量分或候选选择。

旧timing.csv、summary.json和cost_and_timing.png保留在preparation/final_completion_01/before_BW_timing_*。修正后耗时图和记录覆盖会改变，不能将这项日志覆盖变化解释为速度改善。嵌套父子进程作用域仍不直接求和当总墙钟或总CPU。

## 明确H修改的实现边界

H的实际改动边界：H02改变了内层反馈的数据流，每次有效渲染后重新附上原参考图与当前渲染，并加入共享比较指导；H04在此基础上增加数值投影代码示例和相机调整指导。这是共享重建流程和提示的变化，不是新增由固定runner强制执行的投影校准器。H08的材质指导也只是共享生成/修复指导，未成为独立材质修复模块。实际差异见C02/C04/C08的H.diff，不把提示中的代码示例写成已强制执行的新算法。

该说明只读历史代码diff，不改变H/M、生成执行、质量分、选择或任何预算。

## 未闭合耗时测量

实际离线汇总发现进程记录可能保存seconds=null（仍运行或历史中断），排序不能把null与数值比较。耗时CSV保留这些原记录；专项耗时合计只累加实测数值，并在final_test_summary.json的leaf_process_wall_time_unmeasured显式列出未测路径，不把缺测填0。该报告脚本错误不影响任何生成/评价原始结果。

专项CSV沿用原analyze.py的空值写法：None显式写为null；原始JSON空值不变。此前CSV空格形式的派生表样例保留于preparation/final_completion_01/before_literal_null_final_test_raw.csv。这只是展示格式，未改变分数或统计公式。
