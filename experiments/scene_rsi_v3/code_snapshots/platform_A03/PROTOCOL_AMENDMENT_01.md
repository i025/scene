# A01：首个 BW 正式任务和首轮 M 研发之前的平台修订

原 protocol.md、configs/freeze.json 和 code_snapshots/platform_frozen 原样保留。本修订属于固定平台工程修复，不是自动 H/M 演化。

原因一：元数据核对发现原 prepare_task 只传主参考图与 query，未传 metadata 声明的公开规格。Selection 4图中3图共3个文本附件，Test 6图中1图有1个文本附件。没有打开 Test 像素、rubric 或真实附件内容来决定修订，也没有任何 Selection/主 Test 分数、H/M正式候选可供挑选。固定入口现在把 metadata 白名单公开 txt/md/yaml/json 规格加入 PUBLIC TASK REQUIREMENTS；rubric 命名文件明确拒绝，其他不支持类型直接暴露错误，不静默省略。Test 规格仍只在终测冻结后该任务真正运行时加载。所有 H 使用同一入口和信息条件。

12张开发图均无此类附件。已完成的9张开发图和第10张保存的完整H生成结果信息条件不变，保留复用，不重新抽模型。当前图已经保存生成与渲染后暂停主 pilot，原 launch=001、退出143、真实CPU/耗时记录保留；本次操作是工程暂停，不归类为H算法或服务失败。独立judge子进程当时已经开始，之后自行完成并写出真实回复与GNU time退出0；保存原running元数据，依据实际JSONL usage恢复会话记录并用完全相同提示/评分公式首次解析回复，无新增CLI或渲染。其精确结束墙钟未由原监测器采集，保留null，CPU时间来自实际GNU time行，不补造。

原因二：补充确定性检查发现，仅增加M说明文件或未加载的Python辅助文件不应算有效元程序后代。change_kind 只把M的Python源码变化作为程序候选；有效探索保留还要求变更meta入口、实际加载的辅助模块或真实执行过的新动作。原始所有diff仍保存。五个纯检查覆盖说明文件、未用辅助模块、已加载辅助模块、实际新动作与meta入口变更。此判定只表示可执行修改，不证明元能力提高。首轮M尚未开始，没有旧候选需要重选或回写。

四个公开输入边界检查通过，包括规格确实进入现有H CLI提示构造、不含附件时内容不变、rubric拒绝；均未调用模型/Blender。模型、effort、H_start/M000、数据划分、预算、CPU、渲染、BW公式、晋升门槛和最终功能标准均不改变。没有依据正式质量结果调门槛。

实际源码与配置另存 code_snapshots/platform_A01。后续执行使用新 launch 的 resume，读取已完成记录，不重抽终态失败、不增加第11轮。独立post-stage冻结回放仍明确其1图Selection/1图Test、较小内层预算及陌生性局限；不能把跨阶段分差直接当成M能力提升。
