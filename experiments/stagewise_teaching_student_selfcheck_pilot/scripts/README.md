# 实际归档与发布实现快照

本目录保存本轮实际使用的打包脚本及从既有项目导入的实现；SOURCE_MAP.json 记录原部署位置。archive.py 使用 prepare_archive.py 的路径脱敏函数与排除列表、github_release_v3.py 的 auth_session、github_askpass.py 的 Git 认证桥。旧 V3 打包主函数不是本轮执行入口。文件不含认证值。

这些是实际服务器部署源码快照，archive.py 的路径以原 work/stagewise_teacher_archive/ 层级解析，不能直接从本 scripts 目录执行发布。部署到其他机器前应明确设置 PROJECT/SOURCE/REPO 与辅助路径。离线报告无需这些发布依赖，直接在实验目录运行 `python report.py`。无需重跑模型或渲染。

原服务器归档命令：`<config.python> work/stagewise_teacher_archive/archive.py prepare`，已生成包不能重复覆盖。上传使用同一入口 `push`、`release`，使用服务器现有授权 GitHub 凭据，不要求在聊天中提供令牌。发布收据位于仓库 docs/STAGEWISE_RELEASE.json；全产物表为 artifacts_index_stagewise.csv。
