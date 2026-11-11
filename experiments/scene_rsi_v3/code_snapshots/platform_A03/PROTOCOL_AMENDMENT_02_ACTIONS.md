# A02补充：新研究动作在两个独立开发配置上执行

这是首次正式M研发前的固定平台工程补足，落实原V3动作复用契约；不是自动演化、不是新增机制，不改初始M000或任何H/M候选。源码将在既有A02交接创建的003_resume中加载，当前002进程仍使用其已缓存代码。总config和state未由本修订修改。

固定ResearchAPI.ask现在明确告知：每个新建或修改的可复用动作，必须以最终源码在至少两个不同的Development scene_id上真实成功执行，才能随M保留。runner读取保存的action.py与observation.json，逐字匹配最终源码和动作名称，只累计status=completed且属于当前Development面板的不同场景；重复同一场景不增加覆盖，失败或unavailable不算成功。每个动作的成功场景列表、数量、要求及未满足原因写入候选M_action_reuse_validation.json。没有此类动作修改时不额外要求运行，H的资格和接受规则保持独立且不变。

三项确定性夹具通过：一场成功拒绝、两场成功接受、第二场失败拒绝。只写固定测量记录并测试选择逻辑，没有执行动作源码、Codex CLI或Blender，均为0新增模型/Blender调用。此前七项限时M导入测试与旧夹具原样保留。

- [实际三项测试结果](preparation/M_validation_boundary_A02/action_reuse_contract_portable/tests.json)
- [可公开复跑的测试源码](preparation/M_validation_boundary_A02/action_reuse_contract_portable/test_driver.py)
- [此前首次夹具记录](preparation/M_validation_boundary_A02/action_reuse_contract/tests.json)
- [此前七项限时M边界测试](preparation/M_validation_boundary_A02/tests.json)
- [本修订机器可读记录](configs/amendment_02_actions.json)

在已配置项目依赖的Python环境中，从实际或归档实验根目录执行以下离线检查；输出目录必须是新的，命令不调用模型或Blender：

```bash
python preparation/M_validation_boundary_A02/action_reuse_contract_portable/test_driver.py --root . --output derived/action_reuse_check_01
```

现有A02交接将在完整round0后保存源码到code_snapshots/platform_A02。成功复用只是动作可执行与覆盖证据，不证明动作有效或元能力提高。
