# A03：保存的灯光与 World 原生证据补全

此前 bw_0045 的 judge_A02_1、judge_A02_2 因缺少 light energy/color/world 配置将 R06 记为 null，评价状态为 eval_failed。旧回复、历史记录与原评分不变。

仅在 eval_blend.py 增加只读字段 authored_lights 与 authored_world，并将原生证据版本设为 authored_native_project_facts_A03_lighting。LIGHT 保存类型、颜色、能量、节点启用、阴影开关及适用的 AREA 尺寸、SUN 角度和 POINT/SPOT 半径。World 保存颜色、节点启用与真实图。图记录已保存的顶层节点、默认值、连接状态、实际 links 及输出激活状态；不递归展开节点组，节点组名称明确记录。被停用的图仍保留但明确 use_nodes=false；World 不存在为 null。

7 项旧原生证据契约与 9 项灯光契约通过。测试用实际收集器函数 AST 和显式 Blender 对象 stub，不导入 bpy、不执行模型或 Blender、不渲染。render_view/camera_plan/main 源码与修改前相同。纯契约不能替代后续真实 inspect-only 检查，也不能视为新评分或算法收益。

离线纯测试（输出目录必须尚不存在）：

```bash
python test_native_scene_evidence.py --root /path/to/scene_rsi_v3 --output /tmp/scene_rsi_A03_native_tests
```

原源码：eval_blend_before_A03.py；实际差异：eval_blend_A03.diff；测试与证据索引：A03_LIGHTING_FIX.json、pure_tests/test_results.json。
