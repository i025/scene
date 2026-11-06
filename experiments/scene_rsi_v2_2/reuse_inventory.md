# V2.2 复用清单

- 实际 V2.1 运行目录：outputs/scene_rsi_v2_1；旧结果只作历史参考，未复制旧 state/selection/metrics 为新测量。
- H0 与 r1/C2：configs/source_versions.json 中的真实绝对路径；逐文件复制到 fixed_h，文本 diff 可审查，不做内容哈希。
- V2.1 backend/sceneact、CLI adapter、固定图像指标、机械功能检查复用；仅增加共同运行阶段观测，diff 位于 configs/common_telemetry.diff。
- Python：../files-pasted-by-the-user-sceneevolve/work/.venv/bin/python（现有 Python3.11 环境）；模型与 LPIPS/DINO 权重路径见 config.json，全部本地加载，不重新下载或安装。
- Blender：__SERVER_USER_ROOT__/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/blender，等价真实位置 __BLENDERWORLD_ROOT__/runtime/blender-4.2.10-linux-x64/blender。
- Codex CLI：__SERVER_USER_ROOT__/.local/bin/codex，版本和真实帮助保存在 configs。重建 sol medium；诊断/共享代码修复 astra medium；实际返回路由未暴露则 unknown。
- 数据：旧 web_scenes 人工接触清单不能充当新盲测；新 Commons 来源页面和下载 URL、许可保存在 data。旧数据仅用于排除重叠与一张开发烟测。
- 缺少：可确认已分配的 GPU、可用 nvidia-smi 驱动查询；不修驱动，CPU 两线程运行。没有真实自然图像三维真值或远端采样种子控制。
