# 审计输入来源

这些文件是V2.4工程审计读取既有V2.1/V2.2运行记录后保存的输入，属于事后证据整理，不是新的模型实验，也不是事前冻结协议。

- `v21_audit.json/csv/md`：从全部20个V2.1正式record、CLI session、trajectory、Blender result及现存源码读取。原始运行未修改。读取脚本保留为`audit_v21.py`；脚本原本位于项目`work/scene_v2_4_archive`，因此其服务器路径解析与本目录不同。
- `audit_review.json/md`：独立工程审计读取V2.2十个失败正式record及冻结A代码，保存详细证据、预算关系和逐阶段错误。最初由一次内联Python生成，独立生成器**未保存**；不能声称本目录恢复了那次内联脚本。上一级`audit.py`使用保存的审计事实重新合并、生成表图。
- `v22_records.json`：全部24个V2.2正式原始record的JSON副本，另保留各次Blender execute/result事件时间。`record`成员的历史状态、分数和failure_type未改写。
- `v21_config_at_audit.json`：审计时现存V2.1 config.json副本；其候选校验器已包含原实验的后续修订。没有将它冒充早期全部调用前的初始配置快照。
- `v22_executed_config.json`：来自V2.2 `code_snapshots/A_frozen/config.json`，对应本次核对的固定H比较。

JSON中的原始证据路径用于关联服务器旧实验和既有归档。模型等待/推理耗时不能拆分，缺失日志或阶段信息没有事后补造。任何已整理指标应以保留的原始record与事件核对，而不只依据审计文字。
