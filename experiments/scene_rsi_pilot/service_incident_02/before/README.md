# scene_rsi_pilot

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
