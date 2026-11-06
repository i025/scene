# V2.4 复用

复用 V2.2 backend、SceneAct、CLI adapter、pilot.run_scene、inspect_blend、regression。
共同起点 fixed_h/r1_C2 是 V2.1 已演化版本，明确称 H_start，原始 H0另存 fixed_h/H0；不冒充原始起点。
诊断输入为 V2.2 已成功真实图像重建与完整程序，不提供正确场景程序、注入补丁或故障标签。
本轮 CPU2线程、单重任务，Cycles16samples、512长边、AgX、seed42。权重与Blender直接引用旧路径，不下载。
历史图像全部已暴露，本轮探索性；不把源图和迁移图混成独立重复。


## 事后补充的实际资源路径索引

此表是归档准备时依据本轮配置补充，初版文本保存在 report_history/reuse_inventory_initial.md；不冒充实验前新增冻结。

|已有资源|真实路径|本轮复用方式|
|---|---|---|
|V2.1 实验|`__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_1`|只读审计正式20次重建；不修改旧状态、分数与源码|
|V2.2 实验|`__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2`|只读审计正式24次重建及失败原始日志|
|V2.2 后端/SceneAct|`__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/backend`|复制既有小型后端源码；资源与权重仍引用已有路径|
|原始 H0|`__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/fixed_h/H0`|保存来源；本轮不重新运行|
|共同 H_start|`__SERVER_USER_ROOT__/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/scene_rsi_v2_2/fixed_h/r1_C2`|已演化的V2.1 r1/C2固定起点，复制到本轮 fixed_h/r1_C2|
|Python环境|`__SCENEEVOLVE_REPRO__/work/.venv/bin/python`|已有独立复现环境；无安装/升级|
|Blender|`__SERVER_USER_ROOT__/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/blender`|既有4.2.10 LTS；CPU两线程|
|Codex CLI|`__SERVER_USER_ROOT__/.local/bin/codex`|已有0.163.0登录；真实附件，完整调用日志；不复制凭据|
|DINOv2|`__SCENEEVOLVE_REPRO__/work/model-cache/dinov2-base`|已有缓存，CPU数值前向，不下载|
|AlexNet|`__SCENEEVOLVE_REPRO__/work/model-cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth`|已有缓存，LPIPS CPU数值前向，不下载|
|LPIPS|`__SCENEEVOLVE_REPRO__/work/.venv/lib/python3.11/site-packages/lpips/weights/v0.1/alex.pth`|已有包内权重；不复制环境或权重|

实际使用的5张参考媒体及许可见 data/ATTRIBUTION.md；完整包只含本轮真正使用的缩小RGB参考图，不复制整套数据。配置、版本及缺失实际模型路由见 configs/dependency_versions.json、cli_version.txt、cli_exec_help.txt 和真实 session.json。

确实缺少：自然图像三维真值、未暴露的独立盲测数据、CLI独立返回的实际模型路由、旧V2.1构建子阶段遥测；服务排队与纯推理时间无法分开。没有执行旧失败程序独立重放或增加时限的预算敏感性对照。所有这些缺失不补造。
