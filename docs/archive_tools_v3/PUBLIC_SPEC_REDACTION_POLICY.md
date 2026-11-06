# V3 公开任务规格正文的归档政策

本次只修订归档工具，不改变正式输入、生成器、分数或实际执行记录。BW 仓库根 LICENSE 为软件及附带文档的 MIT 文本；目前未找到明确覆盖每个数据任务公开附件正文的单独再分发声明，因此不据此推断第三方附件均可公开。

A01 将 metadata 声明的公开文本附件实际附加到 H 的 `task.json.instruction`，随后可进入 CLI 提示与 JSONL。原附件文件已排除公开归档，内嵌正文也适用同一保留政策。工具仅从已存在的生成任务记录 `public_attachment_sources` 与 `instruction` 提取完整正文；不打开附件原文件，不读取尚未使用的 Test 规格、图像或 rubric。来源必须在真实 manifest 的附件元数据中出现。

普通 Git 与 Release 打包共用同一文本清理函数：完整正文的原文本及 JSON 转义形式替换为清晰的 `WITHHELD_PUBLIC_TASK_ATTACHMENT` 标记，保留 BlenderWorld 来源、任务 ID 和附件名。`V3_REDACTIONS.json` / 打包收据列出来源及已有任务记录，不包含正文。原始完整提示、调用 JSONL 与任务记录原样留在服务器。模型角色、可见 usage、预算、选择、错误和失败事实保留；这不是补造或重跑实验。

本工具不承诺重建已经未保存的文本，也不把嵌入标记解释成模型确已读到该正文。存在生成任务记录仅证明该输入已经构造；实际会话仍以对应 request/session/JSONL 为依据。此前已发布的包不得覆写；需要重新发布时使用新的显式附件版本并注明脱敏政策。

离线验收只用合成文字，覆盖原始提示、Unicode/ASCII JSON、嵌套 JSON 与保留 usage/预算/失败字段；结果见 `public_specs_redaction_test.json`。未调用模型或 Blender。
