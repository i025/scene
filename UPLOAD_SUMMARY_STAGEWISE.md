# 本轮归档摘要

分支：`research/stagewise-teaching-student-selfcheck-pilot`。仓库：https://github.com/i025/scene 。实验完成、尚待本次提交和远端上传确认；该状态将以真实收据更新。

- D01办公室、T01厨房：2/2任务；各5阶段、5次视觉修改；D01另有1次程序错误修复。T01全程教师/Astra 0。
- D01 CLI22/22完成；T01 CLI21/22完成，原路由失败保留且只恢复一次。提炼2、准备2，累计48CLI；构建24（含准备故意错误和D01错误），渲染24。
- 可见token输入4,643,621、输出42,948；usage47/48覆盖，可见工具0，实际路由/精确底层请求/费用unknown。
- D01活动816.55秒，T01活动654.69秒；CLI墙钟累计1461.26秒，包括服务等待。CPU user/system1015.62/31.15秒，不与墙钟混用；CPU8核、32GB上限、GPU0。
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
