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

原图现已按用户最后要求冻结：D01沙发茶几、D02小办公室、E01少家具房间、E02规整中岛厨房。新任务目录已开始正式开发调用，实际进度以tasks/*/status.json和进程记录为准。

初始冻结前模型调用为0；确定性preflight验证了12项顺序、Hint约束、教师接口及学生保留/修订失败回退/执行错误修复三种控制分支（stub，不计研究结果）。首项开发承担真实图像—程序—Blender—渲染—学生观察联通检验；成功证据已保存在D01_M0_R1。FROZEN.json时间早于首个CLI请求，code_snapshots/preformal保留实际冻结源码。
