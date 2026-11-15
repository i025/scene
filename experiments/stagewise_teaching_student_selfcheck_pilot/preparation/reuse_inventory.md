# 复用清单

- 上轮真实运行目录：`${PROJECT_ROOT}/outputs/teacher_self_evolution_human_pilot`；已完成12项，保留不变。
- 新目录：`${PROJECT_ROOT}/outputs/stagewise_teaching_student_selfcheck_pilot`。
- CLI/计时/Blender设置/SceneAct：复用上轮backend源码快照，新增增量场景入口，不使用旧的整场重建Runtime。
- Python：`${USER_STORAGE}/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python`。
- Blender：`${USER_HOME}/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/blender`，4.2.10。
- CLI 0.163.0；Terra与Astra medium；不读取认证，不升级。
- LPIPS/DINO/BW均关闭，不需要权重。两张原图许可及历史见manifest。
- CPU8核、32GB；无调度器分配证据支持更多CPU，GPU不用。
- 本轮缺少并将新增：增量检查点入口、阶段循环、从开发轨迹提炼的测试自查入口、分阶段中文看图页。
