# Scene-RSI V2.1

独立于旧V1/V2的探索性实验。实际状态见 state.json、ledger.json、metrics、reports；未冻结或未完成不等于0分。修复绝对候选资格、失败诊断路径、基于真实图像与对象投影的定位、缺测统计。五类夹具标签不传给M；辅助共享helper修复和自然图像重建分别报告。

先复用原 Python3.11 环境和 Blender4.2.10，在本目录运行：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python tests/contracts.py
blender --background --threads 2 --python-exit-code 2 --python tests/calibrate.py
blender --background --threads 2 --python-exit-code 2 --python tests/diagnostic_fixtures.py
python tests/diagnose.py
python tests/repair_fixture.py
blender --background --threads 2 --python-exit-code 2 --python tests/validate_fixture_patch.py
python smoke.py
python freeze.py
python resume.py
# 离线汇总重画：不调用模型或渲染
python analyze.py
```

上面 python/blender 指已有环境可执行文件；真实路径见config.json及reuse_inventory.md，勿安装到共享环境。源数据、Blender与权重路径需在迁移机器修改config；大资源不复制。resume.py只继续当前ID，不重复已有场景；正式阶段必须先冻结。旧数据不复用作新测量。框架、SceneAct与适配器来源见旧DEPENDENCIES及 code_snapshots/v2_parent。数值权重不包含在归档里。

报告为reports/index.html和reports/REPORT_ZH.md；各图来源为metrics同名CSV及原始JSON。helpers诊断的正确对象可计相关部件；不是精准分割，不把辅助程序通过当成RSI提升。当前实验进度及局限以报告和上传摘要为准。
