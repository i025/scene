# V2.3 复用清单

- 父版本：research/scene-rsi-v2.2 / 0e1731fc3876202d350cf18d595679c77cc41a4f。旧目录 outputs/scene_rsi_v2_2 保留。
- SceneAct：从 V2.2 backend/sceneact 原样复制；共享可修 H 是实际 blender_scene.py 加少量材质/可见性/支撑接口，非上轮五个赋值 helper。
- Codex CLI：复用 backend/codex_wrapper.py、budget.py、processes.py。新会话/真实图像附件/完整日志/可观察 usage；不读取登录凭据。
- Blender 4.2.10：沿用 config.json 的 executable；CPU 单重任务两线程。
- inspect_blend.py / regression.py：复用对象快照、投影、材质和层级检查；新回归实际执行待修 H 的编辑接口。
- 已有 Python：../files-pasted-by-the-user-sceneevolve/work/.venv/bin/python。无新增依赖、下载或 GPU 工作。
- 本轮主指标是可控程序修复/迁移/回归；PSNR/SSIM 作辅助，未调用 DINO/LPIPS，因此原始字段 null。
- 缺少：自然图像共享 H 的独立研发效益、自动 M 后代、冻结元回放，本轮不声称已验证。
