# 冻结前工程记录

- V2 复制自 V1 实际工作目录，不从脱敏归档直接运行。
- 首次 `python` 命令不存在；系统 python3 无 Pillow，改用既有 SceneEvolve venv，未安装依赖。
- 指定对象实际探测前两次工程尝试失败：夹具文件名 fixture.blend 与入口 scene.blend 不符；随后 Blender 入口缺少本目录模块搜索路径。日志完整保留于 explicit_target/ 与 explicit_target_2/，第三次真正执行通过。无模型调用。
- 校准初版与扩展缺件检查分别保存 calibration_initial.json、calibration.json。测试脚本及 fixture.blend 保留；这些不是自然图像重建样本。
- 真实烟测运行期间继续完成固定 runner 的研发期候选后反馈、上下文只读拷贝、证据长度投影及离线报告整理。烟测进程已加载的 pilot.py 工程中间版本没有独立完整快照，不能声称它等同于最终 v2_frozen 源码。实际 H0、生成的 P、候选 H/M、CLI 提示、观测和差异按各自记录保存。正式实验开始前将完整冻结源码。
- 初始 M 在冻结前增加了“未测得回归”显式记录字段；该早期中间工程版本没有另存完整源码，不当作元程序后代或能力变化。正式 M0 将在冻结后保持不变。
- 首次离线报告工程检查在冻结前生成了 Test 参考联系表，未传给模型或人工视觉审阅。文件与说明保留在 offline_preformal_contact_generation/；报告入口已改为 Selection 冻结后才生成正式 Test 联系表。数据原本即有历史联系表曝光，本轮 exploratory，不宣称严格盲测。
- 本轮未运行 SceneEvolve、Generic 或新方法消融。V1 原始源码、分数与结果未改写。

- 首次 smoke 提案为 H-only；当时原始字段 M_descendant_executed=true 实际指候选内 M 接口执行检查，M 源码未变，不能解释为新 M 后代。保留原记录；正式写出独立 M_contract_executed 字段，M_descendant_executed 只在 M_changed=true 时成立，分析脚本同样约束。
