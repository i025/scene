# V3 十轮之后的可选冻结 M 回放（尚未执行）

本协议是新阶段的预备模板，不属于正式十轮，也不是第十一轮。当前仅完成静态工程准备；没有调用模型、Blender 或读取预留 Test 像素/rubric。最终是否运行由主实验完成后的实际后代与预算决定，不能凭本文件报告元能力改善。

## 启动条件与陌生性

必须先完成主实验十轮、端点终测和固定文字编辑流程，主 `state.phase=all_scheduled_terminal`，launcher 的独占 flock 已释放。冻结主阶段累计成本。没有真实参与后续正式研发的 M 后代则停止为 pending；本入口使用最近一次具有改动内容执行证据的真实 M 包，不把最后一轮尚未执行的 M 候选冒称已发挥作用。

资格审计保留确切改动文件、Python 源码 diff、较早接受轮次与同一后续研发 trace 的证据。`meta.py` 改变且匹配的入口完成，或变更的非动作 helper 出现在该次 `loaded_M_helpers`，或变更的 `actions/*.py` 名称和保存的 `action.py` 正文同时匹配该 trace 的 completed 观测，至少满足一项。只增加动作库、把动作文字放进提示、导入但未完成动作、其他 trace 的执行、文档或版本路径变化都不够。没有该证据仍为 pending；改动内容执行不等于策略改善，更不等于普遍能力提升。主线保留 M 的原规则不受本回放入口的资格审计修改影响。

预定两个共享起点为：

1. `outputs/scene_rsi_v2_4/fixed_h/H0`：历史 original_H0。其 `policy.py` 与 V3 `historical_r1_C2_start` 相同、`system.txt` 不同，必须披露部分模块熟悉，不能称每个模块都陌生。
2. `outputs/scene_rsi_v2_4/tasks/task01/active/H`：V2.4 task01 已保存的共享 H 提案，两文件都与 V3 H_start 不同。按显式来源及可用接口选取，不根据旧 Selection/Test 分数择优。

两者都保留 `solve(task,runtime)` 和原程序，不人工改好再冒称原起点。启动前逐个读取主阶段正式 `research_request.json` 的 `context.H_sources`，直接比较源码文本、记录逐文件重合与完整 H 是否已提供；不做内容哈希或指纹。若任何完整起点已给正式 M，整组 pending，不偷偷换起点。基础模型预训练或历史跨会话暴露无法确认，“陌生”只限可审计的本轮显式输入。

## 相同显式档案、固定 M 与 K=1

共同显式研发档案固定前三张历史开发图：`commons_109923183`、`commons_118588033`、`commons_105241439`。每个陌生 H 起点先独立运行这三图，M000 与 M_final 获得完全相同的该起点 P、参考、渲染、对象、功能、错误轨迹和 H 源码；不回收主 Test。两个 M 的上下文字典只允许 `M_sources` 不同。`available_probe_menu=[]` 对双方相同，并明确动作库从各自 `M_sources` 读取，外部无固定五选一菜单。

实际加载只读 M 源码快照；临时动作目录为独立可写副本，新增动作只用于本次回放，不形成下一代 M。只接受 H 提案，含任何 M 修改的最终提案作 inadmissible 保存，不删 M 修改后继续采用 H，也不重新采样。一次未修改/失败/停止同样占本次 K=1 机会。

固定模型及 CLI 权限复用主冻结平台：H Terra medium、M 与独立评审 Astra medium。每次回放最多3研究CLI、8诊断帧、7200活动秒；H每场最多3 CLI/2构建，其他活动时限与正式质量不增加。M 与共享 H 代码修改均通过现有 CLI，不直接 API。元策略必须由其 `research()` 真正执行，继续使用 `ResearchAPI` 和 `research_worker.py`。

## 独立的新阶段选择与测试

预留 `bw_0082` 只作本阶段 Selection，`bw_0092` 只作本阶段 Test；两者与主 dev/Selection/Test 均不同，不读取主 Test 作为回放研发输入。两者原媒体历史暴露不完全可证，整个回放仍为 exploratory。正式任务 query 给 H，rubric 仅评价器可见。当前准备未打开它们的像素或 rubric。

主线最初冻结平台仅传 primary reference+query；A01 于首次正式 BW 评价及任何正式 M 提案前统一补充了 metadata 公开文本附件，未改变 H_start/M000，也未新增修复用模型调用。原核对保留为历史快照，更新见 `MAIN_INPUT_METADATA_DEVIATION_A01_UPDATE.json`。本阶段仍复制旧 `platform_frozen`，再由独立输入适配统一追加 metadata 的 `attachments` 白名单公开文本规格，因此不重复追加，输入路由与主线 A01 相同；不读取 rubric 文件，也不按模型返回的路径任意读文件。当前两个预留任务仅有 layout/spec 文本，无额外图附件；若冻结清单出现非文本附件，入口明确停止，不静默忽略。M0/M_final 在同一陌生H起点上输入相同。阶段预算和 Selection 规模仍与主线不同，不将跨阶段分差归因于 M。stage Test 附件只在四个选择冻结后，由 Test 的实际生成入口加载；prepare 只记录元数据路径，不打开附件内容。

每起点×每 M 各1个主要 H 提案；共同 Selection 对比同一 H_base 与各候选。候选须完成1/1执行、1/1独立BW评价及所有必要功能门槛，再以 BW 至少提升2.5接受；H_base 始终回退，不因它失败放松候选绝对资格。父代明确生成失败/功能不合格时可资格恢复，单列而非成对视觉提升。评审服务缺测不触发恢复。

本阶段固定单次独立评审，按主平台共同规则服务失败最多重试一次；不做边界重评。这是相对主四图+边界评审协议的明确适配，只有1张Selection/1张Test，无法支持普遍元能力结论。所有4次选择均冻结后才运行新阶段 Test；对每个起点基线和各 M 所选 H 统一评价，完全相同 H 引用同一产物并记 reuse，不当新独立样本。

报告每个陌生起点上相对相同 H_base 的 Test BW/Q、执行、功能和独立效用变化，保留4个原始提案点、未修改/失败分母与研究成本。两个起点×各一次提案仅为可行性证据；M代码变多、动作变多或H得分曲线均不证明元能力递归提升。

## 预算、隔离与记录

阶段目录固定 `outputs/scene_rsi_v3/meta_replay_stage`，从 `code_snapshots/platform_frozen` 仅复制已冻结源码/配置，不复制任何旧 session/results。不修改主 runner、H/M、配置或原日志。

固定评分平台显式应用交付证据修订 `original_delivery_metadata_A02`：复制主线已修正的 `bw_evaluate.py`，覆盖旧平台副本；没有其他固定文件覆盖。原评分器未给 judge 原始交付 `final.png` 的实际格式、尺寸和附件，导致可直接判定不合格的条目被记成证据缺失。修正版只测量并附加原交付图，不上采样、不改变作品或 rubric。阶段 `code_snapshots/poststage_fixed_evaluator_A02` 保存覆盖前后源码及真实 diff，`stage_freeze.json` 记录来源、版本与已通过的纯验收；不能把工程修复当成 M 自动改进。其余旧冻结平台与 A01 输入适配的组合保持明确，M0/M_final 使用完全相同的固定评分入口。

阶段上限为 `min(100 CLI, 主全局剩余CLI)`、`min(300渲染扣额, 主全局剩余渲染)`；可见输入/输出token上限严格取主全局剩余。预定保守数量上界：18次H重建×最多3CLI + 4次研究×3CLI + 12次独立评审×最多2尝试 = 90 CLI；渲染扣额约230（18×14的极端简单加和不适用：6个开发基线不做BW，12个Selection/Test产物才做9视图）。这些是上界估算，不是实际消耗或费用。可见token缺测保留覆盖率，不以unknown当零成本。单次远端返回后才能知道实际usage，临界token限额不能保证预先准确预测；余额不足时不启动或按原边界停机，不追正结果。

启动前还按主日志每个角色可见单次最大 input/output usage×预定角色会话数估算 token，需要全局可见余量覆盖该保守历史估算；没有某角色的可见usage则 pending。它不是未来调用的数学上界，不能推断实际费用。外层使用8CPU亲和与32GB进程树监测，整阶段最多36小时，主 launcher 的 shared flock 防止主线同时重新启动。

主预算递归发现新阶段CLI/token，但主根 `render_attempts.jsonl` 不递归包含阶段渲染。本阶段明确保存联合账：主终态渲染扣额+stage根渲染扣额；不把二者相加的CLI/token重复计数。主阶段终态后不再提交新工作，阶段cap≤最初全局余量才能保证联合数量帽。

保存只读M与两H快照、真实diff、共同上下文、每次M请求/动作/观测、候选与选择、统一测试冻结、完整日志、逐场景表和联合成本。没有实际执行的数据为null/pending。入口 `frozen_replay.py audit` 可检查门槛；`run`/`resume` 只有门槛满足才执行，已存在终态失败不重抽，不进入第11轮。当前脚本只做静态契约检查，尚未跑通该可选阶段的真实执行链。

本阶段只生成独立 replay_results.csv/JSON、replay_summary.json、少量真实原始点PNG和独立 index.html/中文摘要；不调用复制平台的十轮 analyze 来制造 pending 演化图。完整有效配对要求两个M都成功执行冻结策略、提案状态为completed/unchanged、相同H_base和所选H的Test均有可比较BW及必要功能通过。只有2/2起点形成完整有效配对才计算总体MetaImp@1，否则为null。逐起点原始差异照实保留。独立 COMPLETION_RECEIPT.json 记 completed/partial，主 META_REPLAY_STATUS.json 仅引用该收据或具体pending失败原因，不回写主指标、主选择或旧结论。入口返回成功本身不等于获得有效配对或元能力改善。

finalizer 调用同一现有 venv 的 `frozen_replay.py prepare`，stdout 最后一行返回 `{"entry_json":"绝对路径"}`。只有 entry.status=ready、eligibility.eligible=true、budget.allowed=true 才执行 command 参数数组；其他条件保留 pending/skipped。root 的代码审阅不替代这些真实运行条件。prepare 不启动模型/Blender，不在主未终态时加载预留媒体或规格内容。
