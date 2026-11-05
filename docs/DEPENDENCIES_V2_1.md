# V2 依赖与迁移

V2 复用 V1 的 SceneEvolve CLI/backend 适配代码及 SceneAct，源关系、原有许可见 V1 归档和 `experiments/scene_rsi_v2_1/backend/LICENSE`。不新增覆盖第三方代码或数据的总许可证。

实际环境：Python 3.11、Blender 4.2.10 LTS、Codex CLI 0.163.0、Pillow 11.3.0、NumPy 1.26.0、Matplotlib 3.9.4、PyTorch 2.5.1+cu121、LPIPS 0.1.4、Transformers 4.57.6、scikit-image 0.23.1、PyYAML 6.0.3。沿用既有环境，不安装/升级共享包。

DINOv2-base、AlexNet 和 LPIPS 权重不上传，已有本地路径见脱敏配置；按原来源获取后只替换配置中的资源路径。参考图来自 Wikimedia Commons，逐图来源、作者与 CC 许可见 manifest；图片不是本项目独占数据。模型、数据、软件分别遵循原许可。

归档脱敏占位符：

- `__EXPERIMENT_ROOT__`：解压后 `experiments/scene_rsi_v2_1` 的绝对位置。
- `__SCENEEVOLVE_REPRO__`：原复现环境/缓存根目录，仅资源来源，不需要其历史输出。
- `__BLENDERWORLD_ROOT__`：可用 Blender 安装根目录，只使用 Blender，不重跑 BlenderWorld。
- `__COMMONS_DATA_ROOT__`：本地图像源目录；Release 中每个已执行场景还保留预处理 reference.png。
- `__SERVER_USER_ROOT__`：账号路径脱敏，不是可执行路径。

复制 `config.json` 为本机配置并替换 Blender、Codex CLI、模型缓存和数据路径。runner 在本目录读 `config.json`；不改 H/M 或评价协议。离线重画无需模型、Blender、GPU、网络；相对图像保存在 Release 解压后的结果目录。`analyze.py` 中当前路径来自历史记录，迁移时需映射 `__EXPERIMENT_ROOT__` 到解压目录，不能改历史分数。

正式复现命令见实验目录 README。续跑仍产生真实模型调用，需本机正常登录 CLI；不要把登录文件放进仓库。

V2.1新增诊断仅使用已有Pillow、numpy、skimage、Matplotlib及Codex CLI；没有新增环境依赖。CPU-only。受控夹具由本仓库Blender程序生成，非外部图片。V2源码参考保留来源关系，不更改第三方许可。
