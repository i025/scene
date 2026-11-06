# V2.3 依赖与来源

- 父版本 research/scene-rsi-v2.2，0e1731fc3876202d350cf18d595679c77cc41a4f。
- Python 3.11：复用原 SceneEvolve 本地venv；需要 numpy、Pillow、matplotlib、scikit-image、PyYAML、requests。没有新安装/升级依赖。
- Blender 4.2.10 LTS：既有 BlenderWorld runtime；设置 BLENDER_EXECUTABLE 或修改独立新工作副本 config.json 的 blender.executable 为本机路径。CPU两线程，Cycles16samples/256x192/AgX/seed42。归档不包含Blender二进制。
- Codex CLI 0.163.0：本机已有登录；help记录位于 configs/。请求模型 gpt-6-astra medium；gpt-6.1-sol medium仅真实图像联通。不能由请求名称确认实际服务模型，actual_model未知保留unknown。没有认证/令牌/模型权重分发。
- SceneAct及后端来源沿用V2.2存档的本地SceneEvolve复现；backend/LICENSE保留。新支持/可见性/编辑接口在 reference_renderer_evaluator_only.py 末尾标记。未给整个仓库新加覆盖第三方代码的许可证。
- 场景/图像均本轮用SceneAct程序生成，无外部素材/自然图像数据下载。不发布未使用预留标签。
- 数值 PSNR/SSIM 由 scikit-image 计算；LPIPS/DINO本轮未运行，不需要其权重，缺测为null。
- archive路径配置用 __EXPERIMENT_ROOT__ / __SERVER_USER_ROOT__ 等占位符脱敏；离线脚本自动在派生目录重定位，不依赖服务器绝对路径。正式源码和实际原始日志在本地及完整Release保留，归档不冒充原服务器可直接续跑目录。
