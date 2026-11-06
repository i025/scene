# A01 后的输入路径核对更新

原 `MAIN_INPUT_METADATA_DEVIATION.json/.md` 是 A01 前的历史核对，原样保留；文件 mtime 见本次 JSON，不据此补写不存在的创建时间。

A01 在首次正式 BW 任务与任何正式 M 提案前，统一把 metadata 的公开文本附件加入主 H 输入。主线 H_start 和 M000 源码不变，修复未新增 CLI 或 Blender 调用。回放入口继续复制旧 platform_frozen，通过其单独适配器补一次相同公开附件，因此与主线 A01 的输入路由相同，不再具有此前所述的附件信息优势。预算、Selection 规模和边界复评仍有明确差异，不能将跨阶段分差当作元能力收益。

本更新仅读 A01 工程记录与旧元数据审计，没有读取 Test 图像、rubric 或附件原文件，也没有修改主线状态。公开归档政策同时覆盖附件原文件及已实际嵌入 task/prompt/JSONL 的正文；完整原件保留服务器。
