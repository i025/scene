# 服务故障恢复补丁草案（尚未应用）

本文件及 `RECOVERY_PATCH.diff` 是工程修订建议。当前正式 runner、冻结快照、失败日志和场景产物均未修改；本次没有模型调用、Blender 执行、联网或凭据操作。

## 已核对的故障

- 位置：`tasks/T01/stages/05/calls/visual_revision/attempt_1`。
- 角色：`student_visual_revision`，请求模型 `gpt-6.1-terra / medium`。
- 实际状态：`failed`，退出码 1，耗时约 34.872 秒。
- 原始错误：`workspace routing discovery failed`。
- 没有成功的程序响应；usage 为 null；不能归因于场景几何或视觉质量。
- 全局 `service_pause.json` 指向本次失败，当前 `invoke()` 在检查暂停后立即退出。因此简单重复 `resume` 不会绕开暂停，也不会自动获得第二次机会。
- 当时账本：46 个 CLI 会话（开发 24、测试 20、联通 2），23 次构建、22 帧渲染；仍需由运行时守卫核对后续实际余额。

## 最小修改范围

只改 `runner.py` 与 `launch.py`：增加 `resume --service-recovered`。不是新采样模式，不改变学生、策略、提示语言、质量标准或预算。

1. 该参数仅对 `resume` 有效。启动器原样转发参数。
2. runner 取得现有实验独占锁后才接受恢复确认。
3. 仅接受已保存的第一尝试、精确路由错误、失败状态、无有效响应且尚未创建第二尝试的情况。
4. 将原 `service_pause.json` 移入独立 `recovery/R.../service_pause.json`，原文保留；同时保存显式确认收据及对应调用目录的收据引用内容。
5. 收据只授权这一个逻辑调用的 `attempt_2`。它记录操作者明确使用了恢复参数，**不声称已经验证外部服务恢复**。
6. `invoke()` 重新读取失败尝试原始提示、JSON schema 和实际图片引用；模型、effort 与角色必须一致。不会根据剩余时间重新生成不同研究上下文。
7. 第二尝试仍经过测试分区、全局 CLI、活动时限等既有守卫。成功结果缓存继续复用，已完成阶段不重跑。
8. 第二尝试再次失败即停止；路由故障仍会生成新的暂停记录。禁止 `attempt_3`，恢复参数也不能绕开这个限制。
9. `protocol_pause.json` 属于工具／隔离协议故障，不能被本参数清除。默认 `resume` 仍保留暂停行为。

若应用，应在修订说明中记录它是对“瞬时服务错误最多一次重试、服务故障先暂停”的显式恢复入口补充。保存原预正式源码快照，不能把此补丁冒充实验开始时已经存在的入口。

## 提案文件与验证

- `RECOVERY_PATCH.diff`：待主代理审查后应用的统一 diff。
- `recovery_proposal/runner.py`、`recovery_proposal/launch.py`：对应候选源码，未覆盖正式文件。
- `RECOVERY_PATCH_TESTS.json`：纯离线 stub 验证。

候选源码已通过 Python AST 解析。六项离线检查通过：默认暂停、原暂停档案保留、只开放第二尝试并复用原请求、缓存成功结果不重跑、禁止第三次、不能清除协议暂停。测试在临时合成目录进行，未读写实际实验状态，没有模型或 Blender 调用。

## 应用后唯一恢复命令（本次未执行）

```bash
${USER_STORAGE}/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python \
  ${PROJECT_ROOT}/outputs/stagewise_teaching_student_selfcheck_pilot/launch.py \
  resume --service-recovered
```

该命令应在外部连接具备恢复条件且主代理确认修订后执行。不要为了验证连接额外消耗新的联通模型会话；第二尝试本身就是唯一允许的恢复尝试。
