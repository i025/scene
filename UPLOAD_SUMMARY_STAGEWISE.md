# 本轮归档摘要

分支：`research/stagewise-teaching-student-selfcheck-pilot`。仓库：https://github.com/i025/scene 。**实验完成且上传已确认。** 实验归档提交：[40c1ce68a638d62bd3b4ef85019779482b9e6b0b](https://github.com/i025/scene/commit/40c1ce68a638d62bd3b4ef85019779482b9e6b0b)。此摘要及上传收据另做后续提交，不改写实验数据。

- D01办公室、T01厨房：2/2任务；各5阶段、5次视觉修改；D01另有1次程序错误修复。T01全程教师/Astra 0。
- D01 CLI22/22完成；T01 CLI21/22完成，原路由失败保留且只恢复一次。提炼2、准备2，累计48CLI；构建24（含准备故意错误和D01错误），渲染24。
- 可见token输入4,643,621、输出42,948；usage47/48覆盖，可见工具0，实际路由/精确底层请求/费用unknown。
- D01活动816.55秒，T01活动654.69秒；CLI子进程墙钟累计约1461.26秒，包括服务等待；会话计时范围稍大，分角色表保留原值。CPU user/system1015.62/31.15秒，不与墙钟混用；CPU8核、32GB上限、GPU0。
- 6条冻结通用规则，测试实际入口10次。存在真实局部修改，也保留相机黑图、错误纵横比判断及未解决黑边；没有自动评分或方法优势结论。R6跨阶段问题档案尚未实现。

入口：[报告](experiments/stagewise_teaching_student_selfcheck_pilot/reports/REPORT_ZH.md)、[完整解释](experiments/stagewise_teaching_student_selfcheck_pilot/reports/CASE_STUDY_ZH.md)、[审查索引](docs/STAGEWISE_REVIEW_INDEX.md)、[步骤表](experiments/stagewise_teaching_student_selfcheck_pilot/metrics/steps.csv)、[调用表](experiments/stagewise_teaching_student_selfcheck_pilot/metrics/cli_calls.csv)、[图片](experiments/stagewise_teaching_student_selfcheck_pilot/figures)、[HTML](experiments/stagewise_teaching_student_selfcheck_pilot/reports/index.html)。

[Release](https://github.com/i025/scene/releases/tag/stagewise-teaching-student-selfcheck-pilot-2026-11-15) · [完整离线包](https://github.com/i025/scene/releases/download/stagewise-teaching-student-selfcheck-pilot-2026-11-15/stagewise_teaching_student_selfcheck_pilot_full.tar.gz) · [全产物索引](artifacts_index_stagewise.csv)。原始实验仍保留服务器 outputs/stagewise_teaching_student_selfcheck_pilot；公开副本只脱敏路径，保留实验事实。

离线重画命令（原服务器）：
```bash
cd /srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/stagewise_teaching_student_selfcheck_pilot
/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python report.py
```
明确续跑命令（现在已完成，只会复用终态，不新增模型调用）：
```bash
/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python /srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender/outputs/stagewise_teaching_student_selfcheck_pilot/launch.py resume
```

## 实际上传确认

- 核心代码、CSV、中文报告、HTML、PNG已推送；远端独立读取7个关键文件均HTTP200，见 [读取收据](docs/STAGEWISE_REMOTE_CORE_READ.json)。
- 完整附件 `stagewise_teaching_student_selfcheck_pilot_full.tar.gz`：80,912,142字节，覆盖1,081个文件；Release返回state=uploaded，资产列表确认大小，公开下载HEAD200，见[发布收据](docs/STAGEWISE_RELEASE.json)。没有内容哈希验证。
- 全部可公开的已有实验产物已纳入；未上传内容只包括缓存/pyc、重复临时附件、Blender备份和锁文件，不丢弃失败日志。两张参考原图按各自CC许可和署名保留；未上传认证、环境、权重或其他用户文件。
- 压缩单线程，用时7.68秒，CPU user/system5.58/1.99秒；与实验计费和模型CPU分开。
- 本地未脱敏原始数据完整保留。Git核心数据约54.54 MiB，大对象清单、全部.blend、JSONL和log在Release包；不能只下载HTML当完整离线包。
- 本轮没有未启动的正式任务。未完成的是科研验证：没有同题无教师对照、独立重复或人工质量判断；R6跨阶段问题档案未实现。
