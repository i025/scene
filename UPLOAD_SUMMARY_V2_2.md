# Scene-RSI V2.2 归档与上传摘要

实验和上传均已完成。仓库：[i025/scene](https://github.com/i025/scene/tree/research/scene-rsi-v2.2)；分支 `research/scene-rsi-v2.2`。实际实验归档提交：[d4b327d](https://github.com/i025/scene/commit/d4b327df69656652eadc7fc6e1ba12de940aa47a)。本轮没有新RSI演化或自动M后代。

- A：24/24终态，H0成功4/12、失败8；r1/C2成功10/12、失败2。功能通过同为4/12、10/12。条件Q为0.444996、0.441361；4个双成功配对平均Q差+0.021329；失败零效用0.148332、0.367801。
- B：预算/对象/实际观测/失败分类与回归选择契约通过，8类真实几何编辑夹具验收通过，真实指定对象64px探测通过（排除正式）。
- C：10任务×2组，20/20修复候选实际生成/执行，双方源修复10/10、有限helper迁移10/10，无修复失败。对象top1双方6/8；最终精确模块2/10→6/10，宽泛相关模块8/10→6/10；事前方向预测区分0/5双方相同，不能宣称修复收益。
- 全轮94/180新CLI，已知input2,397,787/output243,045 token，5会话usage未知；163/600渲染尝试上界、148完成帧，CPU两线程、单重任务、0 GPU。
- A模型为sol medium；C公共视觉/共享代码修改为astra medium。实际路由未独立报告时unknown。A自身CLI27/32；C自有编码各10、共同视觉10一次计数，分摊后各15；自身探测/修复帧各29。
- 4/4个完整附件已上传，共230,909,420字节，覆盖全部3022个已索引产物：正式/烟测/诊断/失败日志和所有blend。[Release](https://github.com/i025/scene/releases/tag/scene-rsi-v2.2-2026-11-06)；artifacts_index_v2_2.csv全部行均为uploaded。

入口：README；docs/AS_RUN_PROTOCOL_V2_2.md；docs/REVIEW_INDEX_V2_2.md；中文 reports/REPORT_ZH.md、HTML reports/index.html、metrics/A_scene_metrics.csv、A_paired_metrics.csv、C_diagnosis.csv、calls.csv、figures，均位于 experiments/scene_rsi_v2_2。

本地完整大产物已打包，原始未脱敏现场保留。没有上传凭据、权重、环境或缓存；第三方许可与图片署名保留。归档副本已解码185张图像；离线重算的A/C汇总与调用统计字段一致，没有新增模型或Blender渲染。

离线命令：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python scripts/offline_v2_2.py --output derived/v2_2_review_01
```

原服务器统一续跑命令（已全部结束时仅重画）：

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= python outputs/scene_rsi_v2_2/resume.py
```

本轮固定H结果是小规模新来源复验；辅助helper修复存在强API提示天花板；没有三维真值、严格盲测或元能力提高结论。已公开测试以后不能重新标为全新盲测。

## 实际远端核对

- 已匿名GET读取README、协议、M/H代码、A/C原始CSV、真实PNG与HTML共10项；两张远端PNG正常解码。见docs/V2_2_REMOTE_CONTENT_CHECK.json。
- 4个Release下载URL均匿名HEAD成功，平台大小与本地包大小一致；未做内容哈希。见docs/V2_2_REMOTE_ASSET_CHECK.json、V2_2_RELEASE_UPLOAD_STATE.json。
- 3022个索引路径与4包成员逐一对应；没有本轮科学产物缺包。模型权重、环境、缓存、未脱敏服务器副本及重复暂存附件拷贝按要求不上传；所有附件的原始媒体和引用映射保留。
- 所有代码/数据/图片本地链接已核对。两个脱敏代表性blend实际打开成功，原始场景未改动。
- 包内研究状态快照在上传前冻结，可能仍写publication pending；最终上传状态以本摘要与仓库docs/上传收据为准，不回写原实验分数或伪造事后冻结时间。

可直接审查的代表场景：A的results/r1/fixed_h/r1_C2/fixed_version_test/commons_104864364/scene.blend（r1包）；C的diagnosis/case05/v2_2_evidence/source_repaired.blend及transfer_repaired.blend（shared-evidence包），其candidate.py和changes.diff在Git可读。
