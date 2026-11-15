# 教师一次自修改：人工判断先导实验

预定 12 项；已启动 12 项；技术交付 12 项。内部构建 24 次。

学生 S 固定：gpt-6.1-terra / medium；教师及自修改：gpt-6-astra / medium。全部通过现有 Codex CLI。
四个来源、两题开发、两题比较、单条教师演化轨迹。历史暴露见 manifest；本次隔离不代表从未见过的盲测。
关闭 BW、VLM judge、Q、SSIM、LPIPS、DINO。没有自动质量接受或晋升。M1 可执行不等于更强，质量等待用户看图判断。
学生实际收到本任务中间渲染的任务数：7。内部构建失败数：5；失败程序与日志保留。首建失败时第二次调用用于错误修复，不能声称学生已经看过修复后final；不额外补第三次调用。

|任务|状态|选择构建|内部构建|
|---|---|---|---|
|D01_M0_R1|completed|2|2|
|D02_M0_R1|completed|2|2|
|D01_M0_R2|completed|2|2|
|D02_M0_R2|completed|2|2|
|E01_M0_R1|completed|2|2|
|E02_M1_R1|completed|2|2|
|E01_M1_R1|completed|2|2|
|E02_M0_R1|completed|2|2|
|E01_M1_R2|completed|2|2|
|E02_M0_R2|completed|2|2|
|E01_M0_R2|completed|2|2|
|E02_M1_R2|completed|2|2|

完整原图、渲染、Hint、内部 checkpoint 与源码 diff：[离线HTML](index.html)。
全部真实联系表：[开发](../figures/development_contact.png) · [匿名比较](../figures/comparison_contact.png)。
联系表来自 plan.json、display_mapping.json、metrics/tasks.json 与原始PNG；重画脚本 report.py，按冻结顺序展示全部四题，没有按质量筛选。
阶段耗时与进程CPU：[cost_by_stage.csv](../metrics/cost_by_stage.csv)；模型等待无法拆为纯推理时间，底层请求数未知。

成本（usage 缺失不作零，底层模型请求数及货币费用未知）：
```json
{
  "cli_sessions": 37,
  "render_attempts": 19,
  "known_input_tokens": 566940,
  "known_output_tokens": 117152,
  "usage_known_sessions": 37,
  "usage_unknown_sessions": 0,
  "observable_tool_calls": 0
}
```

## 耗时与成本边界

首轮有限运行实际墙钟 56.91 分钟；全部模型调用 37/60，构建 24，实际渲染尝试 19/24。可见输入 566,940 tokens、输出 117,152 tokens；usage覆盖 37/37，可见内层工具调用 0。输入包含CLI返回的上下文token，不等同于货币费用；缓存token见逐调用表。请求路由未由独立元数据确认，实际模型与费用unknown。没有评审模型调用。

|阶段|进程数|累计阶段秒|进程CPU user+system秒|
|---|---:|---:|---:|
|student_cli|24|1927.40|23.50|
|teacher_cli|12|894.53|10.67|
|self_modification_cli|1|74.07|0.98|
|blender_build|24|352.41|484.73|
|blender_render|19|163.96|1111.42|

阶段时间包含成功与失败进程；CLI阶段包含无法拆分的远端等待，不叫纯推理时间。CPU来自GNU time子进程及其已回收后代，RSS为单进程峰值或进程树采样下界，二者不得混同。总墙钟来自单独launch记录，不是阶段求和。CPU0–7，8核/32GB上限、单个Blender×8线程，GPU使用0。

## 科研解释

仅发生一次自动教师共享提示策略修改；学生S未变，任务P各自独立生成。M1是可执行且已使用的候选，质量等待人工看图；M1的新self_modify入口未参与下一代研发。无M2、无第三次指导、无追加质量采样。四图与单条轨迹不能支持统计显著性、普遍元能力提升或因果机制有效的结论。

[教师修改审查](M_SELF_MODIFICATION_REVIEW_ZH.md) · [数据访问与源码核对](../metrics/provenance_audit.json) · [错误明细](../metrics/build_attempts.csv)。
