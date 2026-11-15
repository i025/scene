# 本轮复用与准备状态

本轮新分支：research/teacher-self-evolution-human-pilot。原 V3 已结束，当前没有该实验的活动子进程；不影响其他项目服务。

- 原实际运行后端：../scene_rsi_v3/backend。复制既有 Codex CLI 适配器、Runtime.execute、SceneAct、CPU 进程记录与渲染器，保留 LICENSE；原文件不修改。
- Python：${USER_STORAGE}/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python。
- Blender：${USER_HOME}/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/blender。
- Codex：${USER_HOME}/.local/bin/codex，0.163.0；实际帮助已核对，无模型选型或额外收费烟测。
- S：gpt-6.1-terra / medium；M：gpt-6-astra / medium；实际返回路由没有证据则 unknown。
- 配额：用户已有授权 8 CPU / 32GB，1 Blender × 8线程，CPU-only。
- 原数据：既有各代 manifest 指向的 Commons 原图，不读取旧分数选题。
- 新写薄 runner：固定首建、看本次渲染、至多一次内部修订；两阶段自然语言教师；一次源码自修改；没有质量评价器导入。
- 离线 report.py：原图和全部实际版本、匿名 A/B、可导出人工意见；不调用模型。

当前图片未冻结，所有重建/模型调用均为 0；旧四图不再作为正式任务。新的简易四图候选见 preparation/proposed_simpler_four.png；用户选择“保留部分，另换几张”，等待保留编号。manifest.json 仍是撤下方案，正式入口在 FROZEN.json 不存在时拒绝启动。

准备阶段仅通过接口、任务顺序与Hint边界6项确定性检查；不声称学生流程或M1已经实际运行。没有生成FROZEN.json。完成选图和剩余必要工程检查后，才冻结协议、源码与配置并启动第一项开发重建。
