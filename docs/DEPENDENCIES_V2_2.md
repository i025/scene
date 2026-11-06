# V2.2 依赖与许可

沿用 [原依赖与第三方许可](DEPENDENCIES.md) 和 [V2.1依赖](DEPENDENCIES_V2_1.md)。实际Python/包版本见V2.2 configs/python_packages.json；没有补装或升级共享环境。

- 新机器离线重算只需Python3.11、Pillow、numpy、matplotlib；不需要Codex、Blender、GPU或模型权重。
- 新机器继续实验需显式提供Blender4.2.10、已登录Codex CLI、现有DINOv2-base/AlexNet/LPIPS权重和配置中的外部资源；不自动寻找凭据、下载模型或修改环境。
- 归档沿用 `__EXPERIMENT_ROOT__`、`__SCENEEVOLVE_REPRO__`、`__BLENDERWORLD_ROOT__`、`__COMMONS_DATA_ROOT__`、`__SERVER_USER_ROOT__` 脱敏占位符。离线脚本只重定位实验内部路径；原服务器直接使用独立live目录。
- 6个正式Commons来源及资格审查候选的归属、原图页与CC许可见V2.2 data/ATTRIBUTION.md、manifest、preparation_candidates。只做缩放/方向校正与联系表组合，保留各组成图像许可，不用代码许可覆盖图片。
- 原SceneEvolve/BlenderWorld的MIT文本继续保留在docs/third_party_licenses；不上传模型权重、Blender二进制、环境、缓存或未授权第三方资源，也没有给整个仓库新增覆盖第三方内容的统一许可证。

完整CLI提示/日志及所有blend在Release；必要代码、真实小尺寸参考/渲染/探测图片、CSV、JSON和报告保留Git，方便离线审查。原始未脱敏文件仍在服务器，具体替换字段见V2_2_REDACTIONS.json。
