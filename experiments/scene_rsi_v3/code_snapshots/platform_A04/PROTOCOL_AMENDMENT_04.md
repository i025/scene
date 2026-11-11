# A04：第七轮前的无损 JSON 编码修复（as-run）

这是固定平台工程修复，发生在六轮提案及 Selection 决策完成后、第七轮 M 调用之前。不是预注册，不是自动产生的 M 后代。

## 实际故障

`launches/004_resume.json` 以退出码 1 结束。第七轮三张 H04 开发图都已保存；`context_for → bound_payload` 报 `Development evidence exceeds frozen byte budget after explicit projection: 428577`。第七轮尚无 `research_started.json`、M 会话或提案。它是证据打包平台错误，不是模型、Blender、H 或候选失败。

失败包和逐字段大小保留在 `preparation/context_budget_A04/`；原日志、状态、源码和六轮记录不覆盖。已有归档等待工具已停止并保存取消记录，未把中断误报为十轮完成。

## 最小修复与边界

旧上限检查及 M 提示使用带分隔空格的 JSON。保留原投影顺序和中间大小判断，只在最终字节检查与真实 M 提示中使用 `separators=(',', ':')`。同一失败包变为 405,383 字节；唯一新增证据字段是明确的编码说明。完整 M0 提示为 407,916 字节。

对象、完整当前 P、错误、H/M 源码、观测、三图图像附件和既有投影选择均未删改。逐字段比较九个真实已完成的三图面板，与 A03 投影所得证据字段完全相同；JSON 往返还原相等。超过真实上限的夹具仍被拒绝。联通使用 stub，新增模型和 Blender 调用均为零。证据见 `preparation/context_budget_A04/tests.json`、`test_packet_encoding.py`。

保持包上限 420,000 字节、M 提示 480,000 字节，以及 1,200 CLI / 3,000 保守渲染扣额 / 4,000 万可见输入 / 300 万可见输出、25% 最终预留不变。数据、模型、effort、H/M、动作库、渲染、评价器、资格、delta=2 和候选选择都不变。无需重建或重评前六轮。第七轮复用已经完成的三张当前 H04 开发产物，只执行此前尚未发生的研究提案。

## 版本与续跑

评价平台继续为 A03，保证原基线和 Selection 分数口径相同；独立记录 `research_packet_version=A04_lossless_compact_JSON` 与 `platform_snapshot=code_snapshots/platform_A04`。第 7–10 轮新记录包含这两项。前六轮原记录不回写，来源保持 A03。前后实际源码及 diff、配置、失败记录和无模型测试均保留。

这是一条有工程中断及编码修订的连续探索轨迹，不能写成全程未修订的预注册十轮。H 变化由实际 M 提案决定；外层工程师没有修改候选，也不补采样以获得成功升级。
