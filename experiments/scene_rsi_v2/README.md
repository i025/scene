# Scene-RSI V2

本目录是 V2 真实运行入口，复用 V1 backend、SceneAct、H0 与模型缓存。V1 未修改。

按顺序运行；不自动下载、升级或安装任何共享依赖。配置中有本机绝对路径，迁移时只调整资源路径；实验分割、预算和评价配置不可根据结果修改。

```bash
# 从本目录执行；Python 使用既有 SceneEvolve 独立环境
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
PY=__SCENEEVOLVE_REPRO__/work/.venv/bin/python
"$PY" tests/contracts.py
__BLENDERWORLD_ROOT__/runtime/blender-4.2.10-linux-x64/blender -b -t 2 --python-exit-code 2 --python tests/calibrate.py
"$PY" smoke.py
# 确认 smoke 和机制验收通过后才能冻结；正式 run/resume 使用 resume.py 顺序入口
"$PY" resume.py
# 分阶段入口也可独立运行：pilot.py / supplement.py
# 离线分析与重画，不调用模型或 Blender
"$PY" analyze.py
```

`pilot.py` 的前置条件是 `protocol_frozen.json`。恢复运行保留已有记录；未完成的任务留下 interrupted 记录，受同一 420 CLI / 1500 帧预算限制。服务故障写暂停文件，不自动无限重试。缓存场景可以离线分析，不需要恢复模型服务。

H0 的 policy.py 和 system.txt 保持原样。SceneAct 导出器只增加部件声明测量元数据。M 接口只有 `plan_probes(context)` 与 `plan_patch(context, observations)`。H 与 M 的候选类型和选择状态分别记录。M-only 可探索、不计 H 重建改善。候选文件不含最终 Test 原始数据。

图：`figures/`；原始测量与汇总：`metrics/`；中文 Markdown/HTML：`reports/`；确定性已知错误证据：`tests/`；真实后代源码和 diff：`candidates/`。缺测为 null；失败效用为独立字段 `task_utility_v2=0`，不是测得的 Q。
