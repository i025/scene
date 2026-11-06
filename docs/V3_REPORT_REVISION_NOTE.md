# V3 报告脚本事后整理说明

正式平台已冻结并开始执行后，仅离线报告脚本 analyze.py 修订了 Test 分母、动作与时序汇总。冻结时实际源码仍保存于 experiments/scene_rsi_v3/code_snapshots/platform_frozen/analyze.py；当前整理脚本单独保存于 experiments/scene_rsi_v3/analyze.py。

文本差异见 [V3_REPORT_POSTFREEZE.diff](V3_REPORT_POSTFREEZE.diff)。本次归档不以新报告脚本替代冻结源码，不改写旧实验分数、H/M、正式调用/渲染预算或选择结果。报告整理不等于新增实验完成；缺测仍为 null/pending。
