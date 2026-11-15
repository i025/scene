# 阶段式教师纠错 → 学生自主检查

本轮只执行办公室D01开发和厨房T01测试两个持续场景任务。开发时教师在真实构建后给意见；测试时教师退出，学生使用开发轨迹提炼并冻结的通用检查流程。没有自动质量分数、A/B、模型权重训练或教师自进化结论。

[运行前协议](protocol.md) · [来源与历史](manifest.json) · [原图归属](SOURCE_ATTRIBUTION.md) · [离线HTML](reports/index.html)

服务器原目录使用 config.json 中已有独立 Python 环境；无需安装或升级依赖。以下命令在本目录执行：

```bash
# 一次性正式运行，run/resume均不重抽已完成步骤
python launch.py run
# 仅补未完成步骤；服务暂停需先核对原因与实际进程
python launch.py resume
# 仅在确认代理／服务恢复后，启用已保存首尝试路由失败的唯一剩余重试
python launch.py resume --service-recovered
# 离线重画，不调用模型或Blender
python launch.py report
```

本服务器的已验证解释器是：

```bash
${USER_STORAGE}/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python report.py
```

离线重画只需要 Python、Pillow 与本目录已有文件，不调用模型或 Blender，也不需要原服务器的 CPU affinity。执行实验还使用 psutil、PyYAML、已安装的 Codex CLI 0.163.0 与 Blender 4.2.10。配置中的可执行文件路径是本次实际使用路径；公开归档会将用户目录替换为 `${USER_STORAGE}` / `${USER_HOME}` 等占位符。迁移机器时需明确配置本机路径和授权 CPU 集合；不要把已有完成记录当作新实验，也不要覆盖它们。SceneAct 与相关后端来自原实验，代码和所带 LICENSE 一起保留。

确定性 preflight.py 仅用于首次准备，不重复执行已有夹具记录。model_checks 入口实际调用最多两个模型会话，完成后不会重跑。真正实验必须具有 protocol_freeze.json 和联通成功记录。

每次增量程序位于 tasks/{D01,T01}/stages/*/*_build/patch.py；父检查点、对象变化、执行失败与真实渲染同目录保存。后续补丁加载父 .blend，不清空场景。最终工程在 tasks/{D01,T01}/delivery/scene.blend。

`resume` 默认复用已保存的成功回复、补丁和检查点，只补未完成步骤；不会从空场景重抽两个任务。成功流程结束后不会新增第三张图或下一教师版本。若存在服务暂停，普通 `resume` 保持暂停，不自动重试。

本轮在 T01 第 5 阶段的视觉修订调用出现 `workspace routing discovery failed`，原失败记录没有可用模型回复。用户确认连接稳定后，外层只添加了 `recovery_control_01` 恢复控制补丁，见[实际应用与恢复修订说明](reports/RECOVERY_ADDENDUM.md)；修改前后源码与 diff 保留，它不是研究策略更新。`--service-recovered` 只确认这一次已保存的首尝试路由失败，并允许唯一的 `attempt_2`，重新使用原始提示、附件、模型与 effort。旧失败、恢复确认和用量继续保留，不提高任何预算；已有 `attempt_2` 时不能用此参数再次增加机会。确认连接恢复不等于程序已经验证服务健康，恢复成功与否仍以真实调用日志为准。本次确认已经执行，后续普通续跑使用上面的 `resume` 即可，不要反复执行恢复确认参数。

阶段原文件在中断时可能保留 `running`。报告根据任务与整体停止状态显示 `interrupted`／`blocked`，并在 `metrics/stages.csv` 中保留 `raw_status`；不覆盖原文件。未交付时只展示最近成功检查点并明确标注“非最终交付”，不会用它填补最终图或生成质量零分。

完整离线页面需要整个实验目录，不能只下载 HTML。Git 分支保留代码、报告、关键图片与数据；大 `.blend`、完整 `.jsonl`／`.log` 及大型对象清单由本轮 Release 完整包提供。请在[仓库 Releases](https://github.com/i025/scene/releases)中查找本轮 `stagewise_teaching_student_selfcheck_pilot` 归档，下载后按包内原目录解压，再打开 `reports/index.html`。Git 核心副本中这些附件链接可能缺失，不表示原实验没有产物。实际上传状态以仓库的 `artifacts_index_stagewise.csv` 和上传收据为准；未确认上传的附件仅保证存在服务器本地。

模型侧文本统一英文；中文摘要单独展示，原始输出保留。问题发现和“已落实”自述不等于独立质量验证。原图已历史曝光，只有本次开发/提炼与测试的访问隔离。完成和失败以 state.json、metrics/steps.csv 和逐阶段记录为准。
