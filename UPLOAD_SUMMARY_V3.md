# Scene-RSI V3 实际收尾摘要

这是一条连续程序研发轨迹，不是十次独立实验，也不是基础模型权重训练。
监看的真实launch终态：completed，退出码 0；state阶段：all_scheduled_terminal。
保存终态研发回合 10/10；H接受 2 次，M接受 1 个。失败、拒绝和unchanged保留，不能称十次成功升级。
各轮状态：{"completed": 10}。后代版本作为后续轮次父代：['M07']；这个版本关系不证明改动内容真正执行。

H请求模型 gpt-6.1-terra / medium；M与共享编码 gpt-6-astra / medium；独立judge gpt-6-astra。
全部通过Codex CLI。observed_model与请求模型分开；没有元数据则unknown，本地费用未知，不宣称降本。
CPU 8，内存上限 32 GB，Blender 1×8线程，CPU-only，未使用GPU（数量0）。
H整场3600秒、CLI900秒、build1200秒、render600秒。进程树RSS为采样下界，阶段时长不相加作总墙钟。

正式场景记录 81；有效执行 79，终测状态 all_scheduled_records_terminal，已结束记录 24，另有未结算终测中断 0。
终测重复计划：{"repeats": 2, "source": "test_repeat_plan.json", "finalized": true}。未开始/缺测保持null，服务评价失败与生成失败分开。
生成失败分类：{"model_call_timeout": 2}；外部评价失败：{"external_judge_failure": 1}。

| 划分 / H | 全预定 | 执行完成 / 成功 | BW覆盖 | 条件BW | 条件Q | 端到端BW效用 |
|---|---:|---|---:|---:|---:|---:|
| selection / H01 | 3 | 3 / 3 | 3 | 32.5495 | 0.3496 | 32.5495 |
| development / H02 | pending/null | 6 / 6 | 0 | pending/null | 0.3913 | pending/null |
| selection / H02 | 3 | 3 / 3 | 3 | 34.6897 | 0.3790 | 34.6897 |
| selection / H03 | 3 | 3 / 3 | 3 | 29.9927 | 0.3827 | 29.9927 |
| development / H04 | 12 | 12 / 12 | 12 | 76.9213 | 0.4428 | 76.9213 |
| selection / H04 | 3 | 3 / 3 | 3 | 37.8952 | 0.3520 | 37.8952 |
| test / H04 | 12 | 12 / 11 | 11 | 40.2180 | 0.3876 | 36.8665 |
| selection / H05 | 3 | 3 / 3 | 3 | 31.6594 | 0.3915 | 31.6594 |
| selection / H06 | 3 | 3 / 3 | 3 | 34.8893 | 0.3542 | 34.8893 |
| selection / H08 | 3 | 3 / 3 | 3 | 36.4369 | 0.3577 | 36.4369 |
| selection / H10 | 3 | 3 / 3 | 3 | 34.8893 | 0.3582 | 34.8893 |
| development / historical_r1_C2_start | 12 | 12 / 12 | 12 | 77.9282 | 0.4413 | 77.9282 |
| selection / historical_r1_C2_start | 3 | 3 / 3 | 3 | 31.6594 | 0.3659 | 31.6594 |
| test / historical_r1_C2_start | 12 | 12 / 11 | 11 | 41.3288 | 0.3951 | 37.8847 |

独立来源配对：6/6 来源、10 对双方成功且已评分的生成；来源等权条件BW差 -0.0130。全预定来源的端到端BW效用差 -1.0182；完整效用覆盖 6/6。重复和视角不作为独立场景。

[终测逐来源配对数据](experiments/scene_rsi_v3/metrics/paired_test_sources.csv) / [逐生成点](experiments/scene_rsi_v3/metrics/paired_test_generations.csv)。

实际CLI会话 406；usage可见 402/406；已知输入/输出token 35094982/1313761（不是缺失部分的估计）。
主根渲染预算扣额 1117；主根+独立回放根联合扣额 1117，包括保守预扣；精确实际attempt/completed仍unknown，分来源证据见render_evidence.csv。
文字编辑状态：{"failed": 4}；机械结构/编辑检查不等于语义目标正确。
冻结元回放状态：pending_budget_and_actual_descendant_check，优先读取真实独立收据；原state中的历史字段：pending_budget_and_actual_descendant_check。本工具不从H分数曲线推断元能力，未完成真实回放就不作元能力提升结论。

| round | 实际H / M父代 | 类型 | H接受 / M接受 | 保留H / M | 状态 |
|---|---|---|---|---|---|
| 1 | historical_r1_C2_start / M000 | H-only | False / False | historical_r1_C2_start / M000 | completed |
| 2 | historical_r1_C2_start / M000 | H-only | True / False | H02 / M000 | completed |
| 3 | H02 / M000 | H-only | False / False | H02 / M000 | completed |
| 4 | H02 / M000 | H-only | True / False | H04 / M000 | completed |
| 5 | H04 / M000 | H-only | False / False | H04 / M000 | completed |
| 6 | H04 / M000 | H-only | False / False | H04 / M000 | completed |
| 7 | H04 / M000 | M-only | False / True | H04 / M07 | completed |
| 8 | H04 / M07 | H-only | False / False | H04 / M07 | completed |
| 9 | H04 / M07 | unchanged | False / False | H04 / M07 | completed |
| 10 | H04 / M07 | H-only | False / False | H04 / M07 | completed |

主要评价为 **BW-style / CLI-adapted**，不是官方榜单分数；开发preview与正式Selection/Test分开。全部数据是探索性研究，历史暴露和来源独立性限制保留。
本轮平台与M0属于工程实现；只有实际模型提出、保存diff并执行的H/M变化才属于自动演化。可执行后代与动作复用都不自动等于能力改善。
原始冻结平台保留：True；实际续跑A03快照保留：True；A04编码修复快照保留：True；A05终测续跑快照保留：True。整理版分析脚本不替换实际执行的H/M/生成器/评价器快照。

## 审查入口

- [README](README.md) / [审查索引](docs/V3_REVIEW_INDEX.md)
- [A01实际平台修订](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_01.md)：公开附件已通过同一入口转发；原偏离记录保留，M0未变。修订在首个BW正式任务和首轮正式M前完成，已有10个H生成结果按相同信息条件复用。
- [A03实际修订与操作员重跑](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_03.md) / [A03源码](experiments/scene_rsi_v3/code_snapshots/platform_A03/)：首个M提案产生后修复原生照明证据；M提案原样保留、旧产物不覆盖、共同重跑与预算分配明确记录。
- [A04无损编码修复](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_04.md) / [A04源码](experiments/scene_rsi_v3/code_snapshots/platform_A04/)：第6轮后、第7轮M调用前修复JSON空格触发的证据大小检查；H/M、评分和预算不变，原中断保留。
- [A05网络恢复与冻结续跑](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_05.md)：保留服务超时失败，不替换样本，原终测前H/M冻结与时间戳不变；不是自动M修改。
- [中文报告](experiments/scene_rsi_v3/reports/REPORT_ZH.md) / [本地HTML](experiments/scene_rsi_v3/reports/index.html)
- [逐轮](experiments/scene_rsi_v3/metrics/rounds.csv) / [逐场景](experiments/scene_rsi_v3/metrics/scenes.csv) / [动作](experiments/scene_rsi_v3/metrics/actions.csv)
- [CLI](experiments/scene_rsi_v3/metrics/cli_audit.csv) / [时序](experiments/scene_rsi_v3/metrics/timing.csv) / [渲染记录](experiments/scene_rsi_v3/metrics/render_evidence.csv)
- [真实图表](experiments/scene_rsi_v3/figures/) / [全部附件索引](artifacts_index_v3.csv)
- 代表工程包内相对位置：`experiments/scene_rsi_v3/results/H01/selection/bw_0017/1/scene.blend`；二进制在Release包，不冒充Git中已存在的文件。

## 上传与尚未完成项

Git发布：not_pushed；Release：not_uploaded；远端读取确认：not_run。
Release实际收据链接：尚无上传成功收据。未获分发许可的BW原始参考及附件保留本地，公开占位不算实验结果。
可选回放入口：not_started；入口是否执行：False；前后保存request计数差 0 次CLI会话。精确底层model_requests=null，不将整条收尾链称为零调用。归档自身模型/Blender调用为0，回放另计。入口退出码0也不自动证明回放完成或元能力提高，实际结果仍以独立回放记录为准。
改动M内容参与后续研发的保存证据：[{"M_version": "M07", "round": 8, "executed_changed_files": ["actions/appearance_audit.py"]}, {"M_version": "M07", "round": 9, "executed_changed_files": ["actions/appearance_audit.py"]}]；审计状态：changed_content_execution_observed。证据仅到改动入口/模块/动作的实际参与，不是语句覆盖或能力提升。详见[源码与执行关联审计](experiments/scene_rsi_v3/metrics/M_changed_content_execution_audit.json)。

实验数据归档提交：[查看提交](https://github.com/i025/scene/commit/452fa223460cb1db9dbd115fb96ff2c43b8696a6)。此链接指向已确定的数据提交，摘要的后续提交不自指。

## 六来源终测与M07专项审查

[完整终测统计](experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md) / [24项原始数据](experiments/scene_rsi_v3/metrics/final_test_raw.csv) / [六来源配对](experiments/scene_rsi_v3/metrics/final_test_sources.csv)。
Selection BW：31.659382 → 37.895230；Final Test BW配对差及来源bootstrap区间：{"sources": 6, "mean": -0.012994528619529136, "source_standard_deviation": 5.867802238382397, "ci95": [-4.434869528619529, 4.068023989898989], "method": "10000 percentile bootstrap draws over source summaries; seed 20261111; exploratory with n=6"}。
失败零效用差：{"sources": 6, "mean": -1.0182028619528627, "source_standard_deviation": 11.919157806610647, "ci95": [-10.563920454545455, 6.337384259259259], "method": "10000 percentile bootstrap draws over source summaries; seed 20261111; exploratory with n=6"}。生成失败计零效用、原始测量保持null；评价服务失败与pending不计零。
H的实际改动边界：H02改变了内层反馈的数据流，每次有效渲染后重新附上原参考图与当前渲染，并加入共享比较指导；H04在此基础上增加数值投影代码示例和相机调整指导。这是共享重建流程和提示的变化，不是新增由固定runner强制执行的投影校准器。H08的材质指导也只是共享生成/修复指导，未成为独立材质修复模块。实际差异见C02/C04/C08的H.diff，不把提示中的代码示例写成已强制执行的新算法。
[M07源码与全动作审查](experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md)：{"changed_files": ["actions/appearance_audit.py", "actions_index.json"], "entrypoint_identical": true, "action_count": 6, "subsequent_M07_action_count": 4, "H08_validation_delta": -1.4583333333333286, "best_H_created_before_M07": true, "retained_H_updates_after_M07": 0, "meta_capability_improvement_established": false}。H04产生于第4轮，早于M07，不能将H04收益归因于M07。

原13包的基础Release：https://github.com/i025/scene/releases/tag/scene-rsi-v3-10rounds-S20261111T034024Z；本次仅上传preparation/final两个更新包，未变化的baseline与round01–10按显式版本复用原附件，不重复上传。

## 离线与续跑

离线重画（不调用模型/Blender）：
```bash
python docs/archive_tools_v3/offline_v3.py --experiment experiments/scene_rsi_v3 --output derived/v3_review_01
```
仅在实际存在未完成任务并经现场核对后，激活原有venv并在服务器项目根目录续跑；收尾工具本次不执行此命令：
```bash
python outputs/scene_rsi_v3/launch.py finish_test
```
resume仅补未完成任务，不重抽终态失败、不启动第11轮。完整完成时无须续跑；不足部分明确保留pending。
