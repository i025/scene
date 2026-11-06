# Scene-RSI V2.2：固定 H 复验与真实诊断机制实验

本轮检查两个问题：V2.1 自动发现的固定共享流程 r1/C2 是否比原始 H0 更可靠；三维诊断证据是否提高共享程序修复能力。**已实际完成24次新来源重建、零模型机制验收、10个控制故障×2组的诊断与修复/迁移。没有启动新一轮多代RSI。**

A支持这批任务上的执行可靠性提高；C没有显示共享修复成功率优势。工程师修复M不算自动元自修改，也没有元能力提升结论。

## 固定 H 的实际结果

6个新来源场景，每场景2次模型随机重复。统计场景数是6，不能将12次重复当成12个独立场景。全部预定任务均保留，失败视觉指标为null。

|流程|执行成功/预定|必要功能通过|成功条件Q|全任务执行效用（失败=0）|真实CLI会话|
|---|---:|---:|---:|---:|---:|
|原始H0|4/12|4/12|0.4450|0.1483|27|
|固定V2.1 r1/C2|10/12|10/12|0.4414|0.3678|32|

双方成功的4组配对平均Q差为 **+0.0213**；条件均值来自不同成功子集。r1/C2并非所有视觉质量均提高。两个H的policy.py相同，真实修改在共享system.txt，混合了覆盖、复杂度规划和执行验证，不能把收益归因于三维诊断或某单条规则。

4个双成功配对的Mesh数均更低，均值645→246.75；但实际Boolean事件总数22→108，构建时间也并非所有配对更短。失败构建的几何规模被删失，不能声称已经证明普遍减少昂贵布尔。CLI超时、程序/构建错误和明确服务故障分别报告。

![全部预定场景和失败](experiments/scene_rsi_v2_2/figures/figure1_all_A_scenes.png)

![执行成功、功能、条件质量与全任务效用](experiments/scene_rsi_v2_2/figures/figure2_execution_quality.png)

## 三维诊断与共享修复的实际结果

控制为真实冻结的V2.1初始M0；V2.2为工程师修复后的两阶段M。两组看到同一份真实图像/对象/代码证据，拥有相同菜单与探测上限、各一次astra编码机会。共同视觉定位只实际调用10次，原样给双方，不双计为20次。

|指标|V2.1固定M0|V2.2证据策略|
|---|---:|---:|
|主要对象top1（2个相机任务N/A）|6/8|6/8|
|M计划的首个探测模块|9/10|9/10|
|第二阶段精确模块|2/10|6/10|
|第二阶段宽泛相关模块|8/10|6/10|
|实际探测完成/请求|9/9|9/9|
|事前方向预测区分候选解释|0/5|0/5|
|观测改变最终模块（同M空观测对照）|6/10|6/10|
|实测源程序修复|10/10|10/10|
|新参数/几何/名称/共享数据的helper迁移|10/10|10/10|
|自有编码CLI；共同视觉分摊后CLI|10；15|10；15|
|自有探测与修复渲染帧|29|29|

**不能仅按新模块标签宣称诊断整体改善。** 新M有4个unresolved；编码器仍从完整源码和强API契约修复成功。两组都达到修复天花板，没有观察到修复成功率收益，探测也未以事前方向预测区分解释。

这些是10个参数化控制任务、来自两种家具模板，不是10个独立自然房间。修复对象是辅助环境的共享helper H，迁移通过不等于自然图像重建收益或M元能力提高。几何/编辑检查是真实机械操作，不能冒称文字编辑能力或自然场景三维真值。

![诊断指标与原始点](experiments/scene_rsi_v2_2/figures/figure3_diagnosis_comparison.png)

![成功及未解析的真实诊断案例，修复结果分开标注](experiments/scene_rsi_v2_2/figures/figure4_diagnostic_cases.png)

![A实际调用成本与效用](experiments/scene_rsi_v2_2/figures/figure5_A_cost.png)

![C实际调用成本与修复效用](experiments/scene_rsi_v2_2/figures/figure5_C_cost.png)

## 实际机制、成本与局限

- M明确收到剩余探测额度、已用数、真实对象ID和测试菜单；实际Blender观测进入可执行plan_patch。第二阶段比较事前预测、可见性与真实结构/编辑反馈；不按最大Q增量直接择因。
- 指定对象探测保存真实修改后的probe_scene.blend；旧定位在修复后只作历史，当前库存与新回归另存。diff关键词只作近似风险提示。
- 已实际通过预算/对象/观测契约、9类阶段分类/unknown、8种正确/故意损坏几何编辑夹具和一次真实指定对象探测。64px目标探测仅验收，排除正式统计。
- 整轮新增 **94/180 CLI会话**，已知input **2,397,787**、output **243,045** token；**5次usage未知**，不估费用或底层推理轮数。模型请求sol/astra medium；实际路由未独立报告则unknown。
- Blender渲染尝试上界 **163/600**，完成 **148帧**。全部CPU、两个计算线程、单重任务、0 GPU，没有安装/升级环境或下载模型。相同调用机会不等于相同实际token；原始usage逐组公开。
- 6个来源未命中已检查的旧清单，但有本轮资格审查接触记录，不宣称严格盲测。无自然图像三维真值；多视角、AABB与机械编辑不能证明不可见几何恢复正确。
- 两次明确路由故障及恢复检查保留，原失败不重采样。服务处理细则是运行中的as-run补充，不补写为预注册。H0另有3次CLI超时，不能自动认定都是服务商故障或三维退化。

## 直接审查与离线使用

- [中文实验报告](experiments/scene_rsi_v2_2/reports/REPORT_ZH.md)；[离线HTML](experiments/scene_rsi_v2_2/reports/index.html)（本地打开，图片相对路径，无CDN）。
- [A逐场景原始表](experiments/scene_rsi_v2_2/metrics/A_scene_metrics.csv)、[配对质量](experiments/scene_rsi_v2_2/metrics/A_paired_metrics.csv)、[配对几何](experiments/scene_rsi_v2_2/metrics/A_complexity_pairs.csv)、[失败阶段](experiments/scene_rsi_v2_2/metrics/A_failure_stages.csv)。
- [C全部20臂逐任务表](experiments/scene_rsi_v2_2/metrics/C_diagnosis.csv)、[真实调用表](experiments/scene_rsi_v2_2/metrics/calls.csv)、[完整配置](experiments/scene_rsi_v2_2/config.json)。
- [实际执行协议](docs/AS_RUN_PROTOCOL_V2_2.md)、[主张→证据审查索引](docs/REVIEW_INDEX_V2_2.md)、[依赖与许可](docs/DEPENDENCIES_V2_2.md)、[数据归属](experiments/scene_rsi_v2_2/data/ATTRIBUTION.md)。
- [完整产物索引](artifacts_index_v2_2.csv)、[本轮Release](https://github.com/i025/scene/releases/tag/scene-rsi-v2.2-2026-11-06)、[上传收据摘要](UPLOAD_SUMMARY_V2_2.md)。完整日志、全部.blend和失败步骤按运行分包；代码、关键指标和真实小图可直接浏览。

离线重算/重画，不调用模型、Blender或GPU：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= \
python scripts/offline_v2_2.py --output derived/v2_2_review_01
```

原服务器唯一统一续跑入口及各阶段命令见 [COMMANDS_V2_2.md](docs/COMMANDS_V2_2.md)。已全部结束时resume只重画，不新增调用。请勿把归档占位符配置当作已配置的新机器研究环境。

## 保留的旧实验

[V2.1原README](docs/README_V2_1_CHECKPOINT_3a593b3.md)、[V2.1报告](experiments/scene_rsi_v2_1/reports/REPORT_ZH.md)、[V2报告](experiments/scene_rsi_v2/reports/REPORT_ZH.md)、[V1报告](experiments/scene_rsi_pilot/reports/report.md)。旧数据和分支没有覆盖、reset或改写。未新增覆盖第三方资源的仓库统一许可证。

本轮已实际推送并核对远端：4/4 Release附件、230,909,420字节，完整3022项产物覆盖。实验归档提交[d4b327d](https://github.com/i025/scene/commit/d4b327df69656652eadc7fc6e1ba12de940aa47a)；最新上传状态见[上传摘要](UPLOAD_SUMMARY_V2_2.md)。
