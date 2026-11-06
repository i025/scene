# V2.4 复用

复用 V2.2 backend、SceneAct、CLI adapter、pilot.run_scene、inspect_blend、regression。
共同起点 fixed_h/r1_C2 是 V2.1 已演化版本，明确称 H_start，原始 H0另存 fixed_h/H0；不冒充原始起点。
诊断输入为 V2.2 已成功真实图像重建与完整程序，不提供正确场景程序、注入补丁或故障标签。
本轮 CPU2线程、单重任务，Cycles16samples、512长边、AgX、seed42。权重与Blender直接引用旧路径，不下载。
历史图像全部已暴露，本轮探索性；不把源图和迁移图混成独立重复。
