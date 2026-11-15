# 教师一次自修改：上传与审查摘要

分支：`research/teacher-self-evolution-human-pilot`。本轮只做一次M0→M1，学生S固定，没有第11轮H/M、M2或自动质量评价。

实验归档提交：[b6283ac8a120f71ade1386eb30757dde9015573a](https://github.com/i025/scene/commit/b6283ac8a120f71ade1386eb30757dde9015573a)。该提交已推送；最终上传收据单独提交，不制造提交自引用。

Release：[完整离线资源包](https://github.com/i025/scene/releases/download/teacher-self-evolution-human-pilot-2026-11-15/teacher_self_evolution_human_pilot_full.tar.gz)，114,888,215字节。远端资产状态`uploaded`，公开下载确认HTTP 200；完整附件1/1已上传。包含31个.blend文件（19个成功内部构建及12份最终交付副本），不把副本算成独立重建。

[上传收据](docs/TEACHER_HUMAN_RELEASE.json) · [远端读取收据](docs/TEACHER_HUMAN_REMOTE_READ.json)。可公开科学产物无待上传项；刻意排除的缓存/重复暂存文件见下文。README、代码、CSV/JSON、PNG与HTML共7项公开回读均HTTP200。附加匿名Release API曾返回403限流，保留该记录；附件确认采用已经成功的认证资产列表与公开下载HEAD，不将限流当成上传或实验失败。

## 实际完成

|范围|计划|启动|交付|终态失败|
|---|---:|---:|---:|---:|
|M0开发（D01/D02各R1/R2）|4|4|4|0|
|M0比较（E01/E02各R1/R2）|4|4|4|0|
|M1比较（E01/E02各R1/R2）|4|4|4|0|
|合计|12|12|12|0|

24次内部构建，5次首建失败，19次实际渲染。三次圆角尺寸越界、一次空对象材质访问、一次杆端点重合；全部由固定学生第二次调用修复，外层没有手工改P。7/12项学生真实接收了中间渲染；其余5项仅看执行错误后修复，没有额外第三次看图。最终都交付第二次构建；这不等于内容质量合格。

M0只提交一次M1，无技术修复。M1实际变化是共享提示策略：关系组合、纠错优先级、记录状态与压缩要求；已用于4次比较指导。没有新增三维算法；M1.self_modify未再次运行。M1为“可执行、已使用、等待人工判断”，没有自动胜负或元能力增强结论。

学生请求gpt-6.1-terra/medium，教师及自修改请求gpt-6-astra/medium。实际路由unknown。模型调用37/60：学生24、指导12、自修改1；无压缩、重试或judge。可见输入566,940，输出117,152 tokens，usage 37/37；可见工具执行0，底层精确请求与费用unknown。运行56.91分钟，模型调用累计约48.27分钟（包含不能拆分的远端等待）。CPU8核、单Blender×8线程、32GB上限，GPU0。

四图保留①②③并把④换为规整厨房；来源和许可均保留。两比较图仅隔离于本次M1开发，不是全新盲测；R2依赖教师R1反馈，不是同提示独立重复。仅四图、单条轨迹，不做显著性或普遍改进声明。

## 浏览入口

- [实验README](experiments/teacher_self_evolution_human_pilot/README.md)
- [审查索引](docs/TEACHER_HUMAN_REVIEW_INDEX.md)
- [中文报告](experiments/teacher_self_evolution_human_pilot/reports/REPORT_ZH.md)
- [离线HTML](experiments/teacher_self_evolution_human_pilot/reports/index.html)
- [逐任务状态](experiments/teacher_self_evolution_human_pilot/metrics/tasks.csv)
- [全部内部构建与错误](experiments/teacher_self_evolution_human_pilot/metrics/build_attempts.csv)
- [调用与usage](experiments/teacher_self_evolution_human_pilot/metrics/cli_calls.csv)
- [阶段耗时](experiments/teacher_self_evolution_human_pilot/metrics/cost_by_stage.csv)
- [全部真实图](experiments/teacher_self_evolution_human_pilot/figures)
- [M0源码](experiments/teacher_self_evolution_human_pilot/teachers/M0/teacher.py)、[M1源码](experiments/teacher_self_evolution_human_pilot/teachers/M1/teacher.py)、[diff](experiments/teacher_self_evolution_human_pilot/self_modification/M0_to_M1.diff)
- [逐文件产物清单](artifacts_index_teacher_human.csv)

完整附件解压后打开 `teacher_self_evolution_human_pilot/reports/index.html`，包含四张原图、全部渲染、所有内部程序和完整调用日志；A/B可揭示身份、导出空白起始的人工意见。所有12项 `.blend` 在 `tasks/<task_id>/scene.blend`，内部版本在 `tasks/<task_id>/steps/<step>/scene.blend`；例如 `tasks/E02_M1_R2/scene.blend`。

未重复上传：匿名暂存附件副本、Python缓存、备份blend1、未采用选图拼图；实际输入原图/渲染与逐请求附件引用全部保留，不丢弃失败记录。公开文本仅脱敏本机用户路径前缀，tar所有者信息清空，未脱敏日志保留服务器原目录；没有凭据、权重或共享环境。

## 重画与续跑

在完整包的实验目录，或Git中 `experiments/teacher_self_evolution_human_pilot` 下：

```bash
python runner.py report
```

需要Python、Pillow、PyYAML；不调用模型或Blender。图像来自固定plan/display_mapping及真实final，未筛选赢家。生成报告脚本不会改动冻结的P/S/M。

在原服务器的 `outputs/teacher_self_evolution_human_pilot` 目录，用原来的venv Python执行：

```bash
python launch.py resume
```

已实际验证所有终态任务跳过、CLI/渲染消费不变，只重画报告；不生成M2或第三轮指导。没有待运行实验；只待用户自愿进行人工质量判断。
