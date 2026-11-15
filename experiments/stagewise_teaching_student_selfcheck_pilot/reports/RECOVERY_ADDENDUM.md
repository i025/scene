# 路由故障的一次显式恢复说明

这是正式运行后的恢复控制补充，不改写运行前冻结协议。用户于 2026-11-15 确认“连接已稳定，可尝试唯一一次恢复”。

受影响的唯一调用：T01 第五阶段 visual_revision/attempt_1。它在工作区路由阶段失败，没有返回模型程序，已计入调用预算；失败日志完整保留。新增 resume --service-recovered 只授权它的 attempt_2，复用原提示、schema、真实附件、模型和 effort。再次失败不允许 attempt_3。

恢复入口不修改场景、教师指导、冻结学生策略、质量配置、分区预算或每阶段修复次数，也不重新抽取任何成功结果。服务确认不等于独立证明路由健康。原暂停文件移入 recovery 目录保留，确认收据绑定失败调用路径。

修改前后源码、diff 和六项离线 stub 验证见 code_snapshots/recovery_control_01；最初实际运行版本仍在 code_snapshots/preformal_01。外层 launches/002.json 的 running 是未收尾快照；进程核对确认已退出，不能据此声称仍在后台运行。
