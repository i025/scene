# V2 复用清单

实际运行目录：outputs/scene_rsi_v2。V1 原件 outputs/scene_rsi_pilot 未改。

- backend/、SceneAct、H0 来自 V1 实际运行源码；H0 policy.py/system.txt 原样。SceneAct 导出仅增加预期直接子部件名称的测量元数据，不改变几何。
- Python：../files-pasted-by-the-user-sceneevolve/work/.venv/bin/python；不安装依赖。
- Blender：__BLENDERWORLD_ROOT__/runtime/blender-4.2.10-linux-x64/blender。
- Codex CLI 0.163.0；复用 subprocess 数组、图像附件与完整事件日志适配器。
- DINOv2/AlexNet/LPIPS 路径见 config.json；本地加载，数值指标 CPU。
- 数据：e-harness/datasets/web_scenes/human_free_manifest.json；14 个新于 V1 实际重建的来源组，历史联系表曝光，exploratory。
- scenespec geometry.py 为二维 footprint/Rect，不能用作本轮 Blender Mesh 真碰撞；Continuous Mesh 的真实几何检查依赖 authored convex 分件、PyBullet body/task schema 和 geometry.json，不直接兼容本轮 SceneAct 的任意 Blender Mesh；不为适配重写表示。沿用归一化距离及“不能把 bbox 相交当真碰撞”的测量原则，新增少量 Blender BVH 表面相交计算，明确其不支持完整包含检测。
- 未发现调度器命令；默认单重任务、2 CPU 线程。首次检查全部忙，复查 GPU1 空闲；每次子进程重新检查授权池。
- /etc/codex/network-policy.json 和 managed environment_status 工具不可用；未修改网络/认证/全局配置。
- 无自然图像三维真值、语义对象对应标签；声明完整性不是参考图像完整性，支撑检查近似，表面相交不等于不合理穿插。


## V2.1 本轮复用补充

实际运行根目录为同级 outputs/scene_rsi_v2_1；以上V2调查作为来源记录保留。H0取 outputs/scene_rsi_v2/backend/harnesses/baseline，普通文本比较policy/system相同，未取任何历史最优后代。实际旧M0与固定启发式夹具源码普通文本相同，见configs/fixed_heuristic_source_relation.json。

本轮CPU-only、单重任务2线程，不使用旧GPU授权池。沿用同一Blender4.2.10、Python3.11 venv、Codex CLI0.163.0与CPU数值权重，未安装、升级或下载任何模型。新的四来源任务从已有web_scenes索引按标题分组，来源和许可在manifest，历史曝光不可完全确认，exploratory。

本轮新增实际缺口/局限：Git凭据缓存缺失导致V2.1检查点未推送；无自然场景3D真值；无冻结M回放或元能力提升证据；图像定位有独立CLI成本且未分离结构化证据与策略效果。旧V2正式只13记录、Test0，未重复重启旧实验。payload_fix1与提前生成但未评分的一个H0终测控制样本偏离，见protocol事后修订。
