# V2.1 只读失败审计

本次只读取本地实际运行记录，不调用模型、不重建场景、不修改历史结果。

正式重建共预定20项，20项均已有终态记录：9项成功，11项失败；Development 5/6成功、Selection 2/6成功、Test 2/8成功。Test不是未开始状态。H0共8项（成功2、失败6）；C1共4项（成功1、失败3）；C2共8项（成功6、失败2）。

## 有证据支持的分类

- 1项 `model_call_timeout`：r1/C1/Selection/commons_194983350。Codex记录thread.started、turn.started及一句开场消息，300.16秒后本地TimeoutExpired；无build.py。不能据此判定服务端故障。剩余场景预算约300秒，但策略异常结束，没有后续修复。
- 10项 `total_budget_exceeded`：CLI先正常返回，耗时83.15–283.88秒；随后Blender单次执行获得剩余316.03–516.68秒，并消耗到整个场景约600秒。原failure_type全部为budget_or_scene_timeout，保留不变。这些记录的stdout/stderr为0字节，无阶段遥测、无.blend、无final.png。render.py先保存.blend再渲染，因此更接近渲染前阶段，但启动、构建、验证、设备配置或保存之间无法细分，不强行计作已证实几何构建失败。

## 预算与阶段

实际配置：CLI单次300秒、Blender配置600秒、场景总计600秒、最多3次CLI/2次执行、外层610秒、CPU两线程。Blender实际超时采用min(600, 剩余场景预算)。构建与渲染共用同一进程超时，未预留渲染和修复时间。十项失败在第一次执行耗尽时间，虽然调用/执行次数未用满，也没有机会继续；未发现失败后反复调用模型的证据。

保存的十个失败程序均通过Python AST语法解析；这不证明Blender执行正确，也不能仅凭代码长度确定复杂度。没有执行独立重放。

## 可复核证据

逐项证据、CLI会话配置及完整错误、实际执行起止时间和失败程序路径见v21_audit.json；紧凑逐场景表见v21_audit.csv。原始记录位于outputs/scene_rsi_v2_1/results/r{1,2}/，未被修改。

配置实现对应backend/llm.py（模型剩余预算）、backend/runtime.py（Blender剩余预算）、backend/render.py（先保存后渲染）、pilot.py（外层610秒与原分类）。缺失阶段信息不能事后补造。
