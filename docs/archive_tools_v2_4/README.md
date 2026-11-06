# V2.4 归档工具源码快照

这些是服务器实际使用的文档生成和上传核对工具，个人资源路径已脱敏；正式模型/Blender/指标代码在 experiments/scene_rsi_v2_4，冻结版本另存 formal_frozen。此处工具的默认目录遵循原服务器项目布局，运行应显式指定 --source、--repo、--bundles 等参数；离线审查应使用仓库根目录 scripts/offline_v2_4.py，见 ../COMMANDS_V2_4.md。

完整打包、Release 上传及只读 Blender 兼容检查沿用 scripts/prepare_v2_4_archive.py、github_release_v2_4.py、check_blend_copies_v2_4.py。未打包认证文件或令牌；Git认证仅在授权上传子进程中使用。
