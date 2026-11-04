# 复用清单（准备阶段，2026-11-02）

本轮仅写当前工作区 outputs/scene_rsi_pilot；原项目只读。不生成指纹、校验和或哈希，不安装/升级共享环境。

| 真实路径 | 现有用途 | 本轮复用 | 缺失/限制 |
|---|---|---|---|
| __SCENEEVOLVE_REPRO__/SceneEvolve_Code | 已完成的 SceneEvolve CLI 复现 | baseline/policy.py 与 system.txt 为共同 H0；SceneAct、Runtime、render、evaluate、codex_wrapper 最小源码快照 | 原线程硬编码4，统一改2；原失败指标0改null；实际路由不由请求名推断；不复用历史分数 |
| 同项目 outputs/results/reproduction_config.yaml | Student sol、Teacher astra、medium；5调用/3执行/1200秒 | 角色、effort、调用边界、Cycles16/seed42、最长边512、Q公式 | 原指标CUDA改CPU；GPU监控不复用 |
| 同项目 work/.venv/bin/python | Python3.11.18/torch2.5.1/lpips/transformers/skimage | 只读使用，已验证导入 | 无需安装 |
| 同项目 work/model-cache/dinov2-base | DINOv2-base本地模型 | 路径引用、local_files_only CPU加载 | 已在本轮smoke通过CPU实际加载/前向，见smoke/smoke_01/record.json |
| 同项目 work/model-cache/torch/hub/checkpoints/alexnet-owt-7be5be79.pth 及 work/.venv/lib/python3.11/site-packages/lpips/weights/v0.1/alex.pth | AlexNet/LPIPS已有权重 | 路径引用，不下载 | 已在本轮smoke通过CPU实际加载/前向，见smoke/smoke_01/record.json |
| __COMMONS_DATA_ROOT__ | Commons室内图片和来源/组/暴露元数据 | 8正式场景候选+8预留，仅按来源分组；本轮为 exploratory | 全图历史联系表/人物检查暴露；不能宣称全新盲测 |
| __BLENDERWORLD_ROOT__ | 223官方任务、本地参考媒体、历史提交 | 仅外部候选保留；复用Blender运行文件 | 官方evaluate强制哈希，本轮不调用；外部实验待主对照之后 |
| __BLENDERWORLD_ROOT__/runtime/blender-4.2.10-linux-x64/blender | Blender4.2.10LTS | CPU保存、重开、渲染 | 已执行--version；不重装 |
| __BLENDERWORLD_ROOT__/runtime/eval-media/bin/ffmpeg | FFmpeg7.1.1 | 可选转台 | 主结果优先 |
| __SERVER_USER_ROOT__/rsi/scene_rsi_phase2 | scenespec M0-M3/布局RSI | 参考隔离、档案与测量设计；不冒充图像重建算法 | 旧adapter认证relay不使用；旧验收米级/位置多样性不使用；未找到满足本轮的材质/组合回归 |
| __SERVER_USER_ROOT__/.local/bin/codex | 登录的CLI0.163.0 | subprocess数组、真实--image、fresh/ephemeral/read-only、工具关闭 | 内层JSON不独立报告模型路由；usage仅按实际事件记录 |

Hyperagents 官方实现未在有限本地搜索中找到。准备阶段查阅官方 meta_agent.py、generate_loop.py、select_next_parent.py；本轮基线若采用重新适配须明确对应，不复用其Docker/哈希/多模型工具入口。

资源：沙箱内无调度命令/分配变量；cgroup CPU quota=-1，cpuset0–255；本轮主动限制2线程/1重任务。GPU查询驱动失败且没有设备授权证据，CUDA_VISIBLE_DEVICES为空。没有以GPU空闲推定授权。

CLI首次两次在外层工作区沙箱内因状态目录只读失败。随后按正常主机权限调用成功，子CLI仍read-only/无工具。首次原日志路径在第二次尝试中被复用，已在initial_sandbox_failures.json如实披露记录损失；以后调用使用唯一ID。

主机正常权限只读复核：8张A100全部有活跃进程，各占约29–40GB；4–6号瞬时利用率0也不为空闲/授权。无调度器/分配变量。本轮继续CPU；具体查询见resources.json。

用户后续授权后的资源补充：宿主机核对未发现调度器；GPU 0–3 当时空闲。本轮仅允许 GPU 0 UUID `GPU-f099fdbd-adf2-6157-3462-4145bc2a8359`。复用 `/usr/local/cuda-12.2/bin/nvcc` 和原 Blender 自带的 Cycles `source/`，在本实验 `gpu_kernel/` 补编译缺少的 sm_80 内核；原 PTX 与驱动不兼容的失败已保留。实际 GPU 渲染、重开 .blend、固定编辑均已通过，详见 gpu_adaptation.md。未更改共享安装。

2026-11-03续跑资源：用户通知CLI额度恢复后，两指定模型再次真实图片调用成功。GPU0现有其他任务约25GB占用，当前单卡allowlist切为已核对空闲的GPU1（A100，UUID GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5，PCI00000000:25:00.0）；smoke/gpu_reassignment_check真实渲染通过，复用同一GPU内核。仅同时占一张，忙时CPU，原质量及CPU两线程不变。旧额度/路由失败均保留，不复用其缺失指标。

2026-11-03续跑资源再次切换：GPU1出现其他计算进程后，本实验当前子任务已自动选CPU并继续收尾；之后只允许已核对空闲的GPU2（UUID GPU-158426a4-6684-7863-8cbe-ed6595f97683）。仍逐次检查空闲、CUDA UUID隔离和Cycles PCI映射，至多一张GPU、忙时CPU，相同渲染质量；不改其他任务。实际使用以各产物actual_device.json为准。

资源策略澄清：0–3是用户空闲卡授权下的候选池（UUID见quota_restored_20261103/idle_gpu_pool.json），下一子进程只选择其中一张经两次空闲检查的设备；不是同时占用四张。保持单重任务、最多一张GPU，其他任务进入则后续用其他获准空闲卡或CPU。具体实际设备逐产物记录。
