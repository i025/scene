# V2.4 依赖、来源与迁移配置

- 工作基于 V2.3 分支/检查点 d72817b；本轮 H_start 来自已运行的 V2.1 r1/C2，原始 H0 也随包保存。复用关系见 reuse_inventory.md 与 fixed_h，不依赖服务器绝对路径作为版本证明。
- SceneAct/执行后端源于本地 SceneEvolve CLI 复现及 V2.2 适配，保留 `backend/LICENSE`。本轮 common Runtime 的预算边界修订、M 的五工具/ROI 选择在正式前冻结；未重新实现上游框架。
- 离线审计/绘图只需 Python 3.11、NumPy、Pillow、Matplotlib。实际重建还需既有 scikit-image、PyYAML、requests、torch、transformers、lpips 等环境；未向共享环境新安装/升级。
- Blender 4.2.10 LTS 复用既有 BlenderWorld runtime；Codex CLI 沿用此前已跑通版本与参数，不分发可执行文件、登录信息或凭据。实际返回模型无法独立确认时保留 unknown。

- 实际包版本见 [dependency_versions.json](../experiments/scene_rsi_v2_4/configs/dependency_versions.json)；CLI 版本与真实支持参数见 configs/cli_version.txt、configs/cli_exec_help.txt。资源清单初版与事后补充分别保存，不补写成预注册。

## 服务器原资源路径的可迁移标签

|配置字段|现场资源位置（脱敏标签）|其他机器所需动作|
|---|---|---|
|blender.executable|`<SERVER_USER_ROOT>/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/blender`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|
|model.command|`<SERVER_USER_ROOT>/.local/bin/codex`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|
|metrics.dino_model|`<SERVER_USER_ROOT>/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/model-cache/dinov2-base`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|
|metrics.alexnet_weights|`<SERVER_USER_ROOT>/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/model-cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|
|metrics.lpips_model_path|`<SERVER_USER_ROOT>/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/lib/python3.11/site-packages/lpips/weights/v0.1/alex.pth`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|
|dataset.manifest|`<EXPERIMENT_ROOT>/manifest.json`|在独立执行副本中指向自己已获准的本地资源；不自动下载或全局安装|

实际服务器 Python 为原 SceneEvolve 复现的 `<PROJECT_PARENT>/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python`。数值权重来自已有缓存；CPU 前向不是用 Codex 估分。离线重画不会加载权重。

归档用 `__EXPERIMENT_ROOT__`、`__SERVER_USER_ROOT__` 等替换服务器路径；离线工具将实验根重定位到新 derived 目录。正式执行还要迁移 results_dir、dataset.manifest/source_root、模型/Blender 路径，恢复全部 Release 与许可媒体；不能直接拿归档目录当原运行现场。

## 本轮实际使用的自然图像归属

|scene_id|来源|许可|作者（原始 HTML/归属保留于 manifest）|
|---|---|---|---|
|commons_104864364|[File:Empty classroom with benches spread out during the pandemic year in Goa, 2021.jpg](https://commons.wikimedia.org/wiki/File:Empty_classroom_with_benches_spread_out_during_the_pandemic_year_in_Goa,_2021.jpg)|[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0)|Fredericknoronha|
|commons_192968130|[File:Modern luxury living room with kitchen interior.jpg](https://commons.wikimedia.org/wiki/File:Modern_luxury_living_room_with_kitchen_interior.jpg)|[CC BY 2.0](https://creativecommons.org/licenses/by/2.0)|Shixart1985|
|commons_31294395|[File:Bedroom - Longfellow National Historic Site - DSC04810.JPG](https://commons.wikimedia.org/wiki/File:Bedroom_-_Longfellow_National_Historic_Site_-_DSC04810.JPG)|[CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en)|Daderot|
|commons_92056365|[File:Empty restaurant interior HC08164.jpg](https://commons.wikimedia.org/wiki/File:Empty_restaurant_interior_HC08164.jpg)|[CC0](http://creativecommons.org/publicdomain/zero/1.0/deed.en)|Community Archives|
|commons_96943062|[File:Empty interior half portable modular classroom IMG 7277.jpg](https://commons.wikimedia.org/wiki/File:Empty_interior_half_portable_modular_classroom_IMG_7277.jpg)|[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0)|Germsteel|

只归档本轮访问的来源，不公开未使用的预留盲测标签。历史审计数据已标记 V2.1/V2.2，不能冒充新的模型结果。大日志、全部 `.blend` 与大几何 JSON 放 Release，关键指标和真实图片放 Git。未给整个仓库添加覆盖第三方代码/媒体的新许可证。

可执行离线入口与原服务器续跑边界见 [COMMANDS_V2_4.md](COMMANDS_V2_4.md)。资源恢复和联网模型工作不属于离线重画。
