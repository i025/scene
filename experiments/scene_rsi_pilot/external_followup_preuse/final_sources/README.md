# scene_rsi_pilot

当前收尾（2026-11-04）：主对照、补充测试、三消融、最小冻结M回放及两个独立BlenderWorld阶段均已遍历；不是全部成功。累计596/600 CLI，实际完成660帧、尝试上界715/1500。有限队列12已退出，无后台实验。元回放两M均选回H_start、Test增益0；bw_0005两重建成功但H0评分服务失败；bw_0011的H0程序失败，Ours重建有效但评分服务失败。所有失败/null和超时保留。当前状态见state.json与service_incident_05/closeout.json；下文旧停止快照仅为历史。唯一续跑入口为 `bash outputs/scene_rsi_pilot/run.sh resume`，依ID复用已完成/失败记录，不会重开失败任务或扩展本轮范围。

独立先导实验，复用本机SceneEvolve初始Harness、SceneAct、Blender4.2.10与本地指标权重；全部模型经已登录Codex CLI。原项目不修改。CPU最多2线程、单重任务。初始使用CPU；用户追加授权后，Blender逐次检查GPU 0 UUID的占用，空闲时使用一张卡，忙时继续CPU；数值指标仍在CPU运行。详见gpu_adaptation.md。

从当前目录运行：

```bash
bash outputs/scene_rsi_pilot/run.sh smoke
bash outputs/scene_rsi_pilot/run.sh pilot
bash outputs/scene_rsi_pilot/run.sh evaluate
bash outputs/scene_rsi_pilot/run.sh resume
```

`smoke`只运行两个开发专用场景；`pilot`要求protocol_frozen.json已存在，依ID跳过已有record；`evaluate`/`report`仅从原始记录重建离线报告；`resume`依次完成smoke、主对照、固定编辑与匿名评审、预算内消融、符合条件的冻结元代理回放、预算内BlenderWorld外部任务，再报告。中断目录保留并注明，不恢复远端模型隐藏会话。失败完成记录不会自动反复重试；已冻结Selection不因续跑重写时间戳。

输出：reports/index.html和reports/report.md；config.json唯一运行配置；manifest.json显式场景与分组；protocol.md协议；backend源码快照及backend_adaptation.diff；candidates代际H/M源码、changes.diff、真实提案日志；results逐场景P/build.py、scene.blend、final.png、指标及功能数据。

当前状态以state.json、ledger.json和各record.json为准，不把后台进程等同完成。未完成的消融/元回放/外部测试写入报告状态。源码中的初始策略仅为工程实现，不是已验证创新。

服务故障恢复记录在`service_incident_01/recovery_prepared.json`：原无输出的路由失败及旧冻结文件移入`service_incident_01/retired`，所有日志和费用继续计入账本；仅统一准备过一次服务重试。已有有效场景和普通程序错误不会重新采样。`reports/service_attempts.csv`同时保留旧失败尝试与当前任务结果。出现新的`service_pause.json`时，续跑会停止提交；不得删除故障证据或重复运行恢复准备脚本来无限重试。恢复阶段仍用同一个`resume`入口。完整规则和原冻结失效原因见`protocol.md`的服务故障补充。

2026-11-03收尾：CLI额度耗尽已记录于`model_usage_limit.json`。该标记存在时，`resume`只复用已有场景补齐本地多视角/机械编辑联系表及报告，不发起模型调用，也不再次打开已用完统一服务重试的失败任务。终测、文本编辑、独立评审、消融及外部比较缺少有效结果，不能将遍历完成当作实验成功。额度恢复后需要另外冻结续轮规则才能重新采样这些任务；本轮的失败和费用仍保留。`finish_available.py`是四张补充开发联系表及其CSV的可重跑脚本；它们覆盖全部Development和首场景固定视角，明确排除终测解释。

可复现的代表场景：`smoke/smoke_01/build.py`使用本目录`backend/sceneact`，可直接打开`smoke/smoke_01/scene.blend`。重建程序通过`backend/render.py --code ... --settings ... --output-dir 新目录`在Blender中执行。两个smoke中1成功1失败，完整失败预算与日志保留。

剩余预算阶段的实际入口由resume顺序执行extras.py、replay.py：三消融优先，按剩余预算预先选择完整匹配组（最多2重复×K2；最低1重复×K1加匹配原始Ours首候选），不足则pending；冻结M回放仅对真实执行过的策略后代和预留陌生H/新场景运行。单起点回放仅可行性验证，不宣称泛化。

若消融剩余预算仅68–145会话，resume执行四条件各自重新生成的最小1/1/1、一次重复K1组，包括全新Ours参考；它不是共享候选池选择分析，只能作为可行性比较。

2026-11-03用户明确通知额度恢复并要求补完后，两个模型真实图片检查通过，已按quota_restored_20261103/recovery_prepared.json重新开放无输出额度失败；保留所有历史失败及费用。model_usage_limit.json移入该恢复档案，普通resume再次执行完整顺序。原有成功/部分成功产物不重采样，正常程序与验证拒绝不重试。GPU0繁忙，当前仅用空闲GPU1 UUID GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5，逐次检查，忙时CPU。

2026-11-03续跑资源再次切换：GPU1出现其他计算进程后，本实验当前子任务已自动选CPU并继续收尾；之后只允许已核对空闲的GPU2（UUID GPU-158426a4-6684-7863-8cbe-ed6595f97683）。仍逐次检查空闲、CUDA UUID隔离和Cycles PCI映射，至多一张GPU、忙时CPU，相同渲染质量；不改其他任务。实际使用以各产物actual_device.json为准。

资源策略澄清：0–3是用户空闲卡授权下的候选池（UUID见quota_restored_20261103/idle_gpu_pool.json），下一子进程只选择其中一张经两次空闲检查的设备；不是同时占用四张。保持单重任务、最多一张GPU，其他任务进入则后续用其他获准空闲卡或CPU。具体实际设备逐产物记录。

2026-11-04停止快照：主对照搜索和终测、固定文字编辑与独立评审已结束。消融终测7成功、1路由服务失败、4待运行；冻结元回放与BlenderWorld外部任务未启动。该次有限队列已经退出，累计533/600会话。`service_incident_02/closeout.json`保存当时停止状态，`quota_restored_20261103/session_jump_373_to_529.json`逐项解释373→529的156次会话。普通`resume`保留路由停止标记并阻止新调用。

服务恢复后，只使用以下明确的续跑命令：

```bash
bash outputs/scene_rsi_pilot/run.sh resume-service
```

这是该历史故障的显式恢复入口；该次收尾尚未执行，后续执行见下文。它最多新增一次已计费的gpt-6.1-sol/medium连接检查，成功后继续尚未运行的槽位；已有失败场景、H/M、选择与总预算不改。检查再次失败则保留停止标记，同一入口不会反复提交连接检查。后续可选阶段仍按实际剩余预算判定，不保证都能运行。单独重建离线报告继续使用`report`。

后续用户明确要求继续后，`resume-service`的一次连接检查已经成功，队列09继续尚未运行的槽位。实时执行状态见`service_incident_02/execution_09.json`和`state.json`，最终结果见各阶段状态；这是同一600会话预算内的续跑，失败任务没有重开。消融缓存续跑的冻结时间戳修正记录见`service_incident_02/ablation_freeze_resume_audit.json`。

历史停止快照（546次时）：队列09新增13次会话后，以路由服务错误退出，累计546/600。原4个待运行消融槽全部尝试，新增3个成功和1个路由失败；消融终测最终10/12成功、2服务失败。元回放、BlenderWorld尚未启动，原因是服务阻塞，剩余54次预算未消耗。`service_incident_03/closeout.json`保存本次逐调用对账；`resume-service`为新故障03保留一个需要显式执行的连接检查入口，该次停止快照尚未执行它；后续执行见下文，失败场景未重开。已有消融完成状态包含失败，续跑会直接复用。

后续队列10已通过故障03的一次连接检查并启动元回放，实时状态见`service_incident_03/execution_10.json`和阶段状态。BlenderWorld随后按`config.json/external_stage`、纯余额缩放：≥24次运行原2任务，12–23次仅首任务bw_0005，<12待运行；H0与Ours同规模，不改模型、H选择、内层预算、渲染或评分。该独立外部阶段适配在外部调用/结果为0、元回放Test冻结前记录，非原始预注册，见`external_budget_adaptation/preuse_rule.json`；单任务只报告可行性，未跑bw_0011明确pending。总600/1500不扩大。

后续队列10已完成冻结M回放，两份M均选回同一H_start，实际Test增益0；bw_0005的H0评分遇路由故障后，队列11仅检查一次连接并补尚未提交的Ours，保留H0失败评分。原外部阶段完成后仍有12次CLI，因此按任务自身结果前固定的`external_followup_preuse/rule.json`启动独立bw_0011后续阶段；条件仅为余额≥12、前阶段遍历完成，不读取胜负或评分。结果单独报告，不改上一阶段样本数、不冒充原预注册两任务组。`config.json/external_followup_stage`给出范围，`resume`自动按条件进入，也可运行`bash outputs/scene_rsi_pilot/run.sh external-followup`；已有记录缓存复用，不重开失败。
