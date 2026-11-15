# 阶段式教学与学生自主检查：最终审查索引

这是证据入口，不是方法有效性的认证。源码、原始模型文本、对象清单和图像必须共同阅读；教师或学生的过程判断不能直接当成质量真值。本文件供归档整理使用，不传入模型上下文。

本轮两个完整任务均已交付，每个按保存计划处理五个阶段。D01 为历史办公室图，T01 为另一来源的历史厨房图；两图都有历史暴露。D01 五阶段中一阶段复核允许直接继续，四阶段带问题继续；T01 五阶段均带问题继续。流程完成不等于问题全部解决。

以下代码、数据和图的路径均相对于 `experiments/stagewise_teaching_student_selfcheck_pilot/`（服务器实际运行目录对应 `outputs/stagewise_teaching_student_selfcheck_pilot/`）。Git 核心副本不一定包含大型清单、`.blend`、完整 `.jsonl` 和 `.log`，完整证据需使用本轮 Release 完整包。上传与可访问状态另以 `artifacts_index_stagewise.csv` 和远端收据为准，本索引不预先声称上传成功。

| 主张或需要核查的问题 | 对应代码 | 原始数据 | 图与展示 | 局限或反证 |
|---|---|---|---|---|
| 每个任务在同一持续场景上增量建模 | `runner.py:execute`、`incremental_blender.py` | `tasks/*/stages/*/*_build/build_request.json`、`inventory.json`、父检查点与独立新检查点 | HTML A/C 时间线，各阶段 `final.png`；联系图及 `*_contact_sources.json` | ID 与已记录字段稳定不是所有 Blender 属性均保持的证明；未完整测量修改器参数、ColorRamp、UV、灯光尺寸等 |
| 教师只在有效画面产生后提供开发反馈 | `runner.py:run_stage`、`review`；`prompts.py:TEACHER` | `events.jsonl`、D01 各阶段 `stage.json`、`calls/review/attempt_*/request.json` 与真实附件 | HTML A：首次结果→教师意见→局部修订→复核 | 教师是过程指导，未提供独立质量真值；比例位置估计不是外部几何测量 |
| 学生落实声明必须经过实际补丁与复核核对 | `apply_operation`；D01 阶段 1—3 的 `visual_revision_build/patch.py` | `advice_implementation`、`actual_executed_patch`、`inventory.changes`、教师 `confirmation` | `reports/CASE_STUDY_ZH.md`、D01 阶段前后图 | 阶段 1、3 学生写 `implemented`，教师仍判部分解决。不能按实现声明计成全部问题已解决 |
| 阶段 2 的局部改动集中在两把椅子 | `tasks/D01/stages/02/visual_revision_build/patch.py` | 同目录 `inventory.json`：332 条变化按父链全部位于两把访客椅，各 166 条；无新增、删除、相机和已测材质变化 | 阶段 2 前后真实渲染 | 332 是底层对象／部件记录数，不是独立对象任务数；接地细节受噪声限制 |
| 程序错误修复没有冒充视觉纠错 | `apply_operation` 的技术修复分支 | `tasks/D01/stages/04/initial_build/result.json`、`technical_repair_build/patch.py` 与结果、后续教师反馈和视觉修订记录 | HTML 阶段 4 首次失败留空，技术修复与视觉修订各有真实图 | 首错为 `fillet_box` 圆角越界；修复成功只表示技术有效，之后仍另做实际看图反馈与纠错 |
| 共享规则确实由开发轨迹提炼并在测试前冻结 | `extract_policy`、`transfer/frozen/student_self_review.py` | `transfer/extraction.json`、`extraction_corrected.json`、`validation_error_1.json`、`lesson_provenance.json`、`freeze.json` | HTML B；实际规则和源码 diff | 初稿技术错误规则引用了不存在的反馈 ID，唯一格式修正将该规则删除，未伪造 ID。最终六条规则中一条明确为已有通用规则，五条标记为开发轨迹提炼；不是已证明新增能力 |
| 测试确实执行冻结入口，而不只是保存了一份文档 | `runner.py:review` 测试分支；冻结入口 `build_review_prompt` | `events.jsonl` 的十次 `frozen_self_check_executed`；T01 review/confirmation 提示与 request | HTML C 五阶段的自查及复查记录 | 入口只组织提示和已有上下文，不自行进行几何测量或发现图像问题；不等于权重蒸馏或教师自进化 |
| T01 的问题声称来自当前测试观察 | `SELF_REVIEW_CONTRACT` 与冻结规则 | `tasks/T01/stages/*/stage.json` 中 `problem_source=test_observation`、`rule_source`、图像证据、实际附件 | 测试各阶段初建与修订后图；中文案例 | 标签本身不能保证观察正确。阶段 3 两次声称原图与渲染宽高比不同是明确错误：实际分别为 1280×960、768×576，均为 4:3。原始错误没有删改 |
| T01 没有教师／Astra 代替学生看图 | `invoke` 的测试角色与模型限制；固定配置 | 全部测试 request/session，`metrics/cli_calls.csv`；测试 22 个 CLI 会话全部为学生角色、请求 Terra，其中含一次路由失败 | HTML C 显示实际教师／Astra 调用数 0 | 请求型号与实际路由分列；CLI 未提供可独立确认的底层路由元数据，仍为 unknown |
| R6 的跨阶段问题保留尚未完整落实 | `runner.py:review` 的 `previous_findings` 传递；冻结 R6 | 同阶段 confirmation 上下文有此前发现，后续阶段首次 review 中为空；`reports/TRANSFER_AUDIT.json` | HTML B 的明确局限提示与中文报告 | 持续场景与前后图片仍保留，但没有结构化跨阶段未解决问题记忆；不能把规则要求冒充已执行能力 |
| 服务路由失败与学生建模失败分开保留 | `code_snapshots/preformal_01`；`code_snapshots/recovery_control_01` 的恢复控制补丁 | `tasks/T01/stages/05/calls/visual_revision/attempt_1`、唯一 `attempt_2`、`recovery/*/acknowledgement.json`、原暂停文件、`reports/RECOVERY_ADDENDUM.md` | HTML 服务中断与恢复记录；`cli_calls.csv` | 初次在 workspace routing 阶段失败，无有效模型程序、usage 缺失；不是几何质量失败。用户确认后只重试一次，原提示、附件、模型、effort 与预算不变，没有第三次 |
| 最终图与最终场景确实保存，但没有最终高质量图复评 | `final_delivery`、固定 `backend/render.py` | `tasks/{D01,T01}/delivery/{final.json,render_settings.json,scene.blend,final.png}` | HTML 原图／最终交付，两任务分别展示 | 最终图为同一保留几何的 1024 长边／32 samples 渲染；`final.json` 明确教师、学生均未另看这张最终质量图。不能据此补写最终复核通过 |
| 调用、构建、渲染分开计数并保留失败 | `backend/budget.py`、`processes.py`、`report.py` | `metrics/{steps,stages,tasks,cli_calls,cost_by_role,timing}.csv`、`summary.json`、全部请求、JSONL 与进程记录 | HTML 成本表和阶段联系图 | 48 个 CLI 会话不等于底层精确模型请求。47 次 usage 已知，1 次路由失败未知；已知输入 4,643,621、输出 42,948 token。24 次构建／24 帧尝试包含准备夹具，不是 24 个独立场景 |
| 不把历史曝光与单轨迹包装成泛化收益 | `protocol.md`、`manifest.json`、`config.json` | 两个实际来源、计划、状态；不调用自动质量评价器 | 原图与每阶段实际产物，人工意见默认空白 | 无同图无教师对照、无独立重复、无权重训练；没有自动评分胜负、普遍能力增强或教师自进化收益证明 |

## 终态与原始状态

当前 `state.json` 为完成，两份 `delivery/final.json` 也均为完成。T01 在第五阶段路由失败后曾中断，旧日志、暂停文件与失败会话完整保留。中断期阶段文件的 `running` 快照不能被说成进程一直存活；报告的 `raw_status` 与展示状态分列，不通过覆盖原始文件掩盖历史。

默认续跑是 `python launch.py resume`：复用已成功回复和检查点，不从头重抽、不增加第三张图或自动 M2。已完成时不新增实验。唯一一次路由恢复确认已经使用；`--service-recovered` 不是增加重试次数的开关。离线重画是 `python report.py`，只读取已保存数据。

## 推荐阅读顺序

先看 `reports/index.html` 的 A/B/C 过程，再读 `reports/CASE_STUDY_ZH.md` 和 `reports/REPORT_ZH.md`；核对主张时进入上表原始文件。历史局部审计如 `TRANSFER_AUDIT.json` 保留其实际审计时间与范围，不把当时仅观察到的测试调用数当成最终计数。最终调用与产物数量以终态数据表和真实交付为准。

公开包脱敏只处理用户目录及必要敏感字段，模型角色、失败、预算、选择与恢复事实应完整保留。原图各自许可和署名见 `SOURCE_ATTRIBUTION.md`，不为第三方代码和媒体统一添加覆盖性新许可。


最终独立测试轨迹审计：[T01_AUDIT](../experiments/stagewise_teaching_student_selfcheck_pilot/reports/T01_AUDIT.json)。上传后核对：[Release收据](STAGEWISE_RELEASE.json)、[远端核心文件读取](STAGEWISE_REMOTE_CORE_READ.json)、[上传摘要](../UPLOAD_SUMMARY_STAGEWISE.md)。
