# Scene-RSI V2.2 归档与上传摘要

实验已全部结束；本文件的首次归档版本记录本地完成状态，实际推送/附件收据将在上传后补充。目标仓库：https://github.com/i025/scene；分支 `research/scene-rsi-v2.2`。本轮没有新RSI演化或自动M后代。

- A：24/24终态，H0成功4/12、失败8；r1/C2成功10/12、失败2。功能通过同为4/12、10/12。条件Q为0.444996、0.441361；4个双成功配对平均Q差+0.021329；失败零效用0.148332、0.367801。
- B：预算/对象/实际观测/失败分类与回归选择契约通过，8类真实几何编辑夹具验收通过，真实指定对象64px探测通过（排除正式）。
- C：10任务×2组，20/20修复候选实际生成/执行，双方源修复10/10、有限helper迁移10/10，无修复失败。对象top1双方6/8；最终精确模块2/10→6/10，宽泛相关模块8/10→6/10；事前方向预测区分0/5双方相同，不能宣称修复收益。
- 全轮94/180新CLI，已知input2,397,787/output243,045 token，5会话usage未知；163/600渲染尝试上界、148完成帧，CPU两线程、单重任务、0 GPU。
- A模型为sol medium；C公共视觉/共享代码修改为astra medium。实际路由未独立报告时unknown。A自身CLI27/32；C自有编码各10、共同视觉10一次计数，分摊后各15；自身探测/修复帧各29。
- 4个完整本地附件共230,909,420字节，覆盖全部正式/烟测/诊断/失败日志和blend；上传状态以artifacts_index_v2_2.csv及后续Release收据为准，当前待上传。

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
