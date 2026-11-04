# 用户授权后的设备适配（不修改 H/M）

2026-11-02 用户明确要求“现在有空闲的gpu就用呗”。检查时未发现调度器命令或分配环境，GPU 0–3 的显存为 0 MiB、利用率 0%、无计算进程；4–7 有其他任务。本轮只允许物理 GPU 0，UUID `GPU-f099fdbd-adf2-6157-3462-4145bc2a8359`，PCI `00000000:01:00.0`。枚举已确认 Blender 子进程只看到此 CUDA 设备；正式 GPU 渲染仅启用 CUDA 对应设备。

每个新的 Blender 工作检查此 UUID 的活跃进程、显存和利用率；忙或无法确认时转 CPU。没有等待守护进程，不动其他用户任务。CPU 仍为最多2线程，重任务串行，LPIPS/DINO 等数值前向仍在 CPU。CUDA_VISIBLE_DEVICES 仅对子进程传入。

引擎、采样数、分辨率、种子、颜色管理、线程上限、模型、调用/渲染预算、数据、验收规则保持原冻结设置。仅资源管理和设备记录适配；不是 H 或 M 的实验候选。冻结前配置保存在 config_before_gpu.json，代码差异见 gpu_adaptation.diff。每个新渲染保存 device_selection.json 和 actual_device.json；早期 CPU 渲染没有此文件，但原始配置和命令可追溯。

暂停点：r2/sceneevolve_cli/C1/selection/commons_133800864。仅暂停外层 runner，正在执行的原 CPU 内层任务允许正常结束。完成后重启 runner，复用该内层已完成状态，不重采样。GPU smoke 用已完成的开发专用 smoke 场景另存，不纳入正式结果，并计入全局帧预算。

本轮包含 CPU 与 GPU 结果，不能用混合设备 wall time 宣称算法速度优势。GPU/CPU 数值差异及相同时间上限下执行机会差异是限制，不宣称硬件完全等价；质量设置相同不等于逐像素相同。后续所有方法共用相同资源策略。GPU smoke 实际结果见 smoke/gpu_compiled_check/；原 CUDA/OptiX 失败日志另存 smoke/gpu_device_check/ 与 smoke/gpu_optix_check/。

## 实际兼容性修复与验证

原始内核缺少 sm_80 cubin，回退的 PTX 与现有驱动 535.247.01 不兼容；CUDA 和 OptiX 各失败一次，两次均计帧预算，未触发模型调用。复用原 Blender 内置未修改的 Cycles 源码与已安装 nvcc 12.2.140，在 gpu_kernel/ 编译 A100 sm_80 原生内核（标签 local_a100_cuda122_v1）。其余资源为原路径符号链接，不升级/重装原环境。编译约六分钟、单线程；精确起止见 build_timing.json。

实际 GPU smoke 已完成一帧：256×171、Cycles16、seed42，唯一启用设备为指定 A100 CUDA。总 Blender 进程耗时约1.42秒；正确匹配的是协议冻结时的 CPU render_repeat_1（相同关闭降噪设置），Q 为0.4248264678；GPU Q 为0.4248767447，差+0.0000502769。最初比较的旧 smoke_01/final.png 启用了降噪，不能用于设备等价比较；该次不匹配计算也保留。匹配的逐像素差见 comparison.json，仍不是逐像素一致。此单场景检查不能证明设备普遍等价，正式比较必须保留混合设备限制。重编译入口为 `bash gpu_kernel/build.sh`（从此实验目录运行）；通常续跑直接使用已编译内核。

诊断口径：切换后的探测可能使用GPU，而其父场景图来自CPU。报告案例板及来源JSON逐项标出 baseline_device、probe_device、device_matched。设备不匹配时，分数差同时包含设备数值差，不能称严格隔离的单因素因果证据；只有匹配设备的真实案例可作为较干净的敏感性展示。探测策略与模型预算未为某组单独更改。

实际慢几何构建触发的资源补充：除提交 Blender 前检查外，configure_cycles 在开始 GPU 渲染前再次检查同一 UUID。只忽略当前 Blender 自己的已有 CUDA 上下文；如有其他计算进程、无法解释的利用率/显存或查询失败，则记录原因并改用 CPU，质量设置不变。这个检查对所有方法一致，不查询或干预其他用户任务内容。

2026-11-03续跑：GPU0已有计算进程及约25GB显存占用，GPU1为空闲A100。依据用户已有空闲GPU授权，将当前allowlist改为GPU1 UUID GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5（PCI00000000:25:00.0），同时最多占用一张。smoke/gpu_reassignment_check已用真实场景验证CUDA映射和同一内核，21.4034秒、1帧、计入预算；正式质量不变，旧GPU0记录保留。

2026-11-03续跑资源再次切换：GPU1出现其他计算进程后，本实验当前子任务已自动选CPU并继续收尾；之后只允许已核对空闲的GPU2（UUID GPU-158426a4-6684-7863-8cbe-ed6595f97683）。仍逐次检查空闲、CUDA UUID隔离和Cycles PCI映射，至多一张GPU、忙时CPU，相同渲染质量；不改其他任务。实际使用以各产物actual_device.json为准。

资源策略澄清：0–3是用户空闲卡授权下的候选池（UUID见quota_restored_20261103/idle_gpu_pool.json），下一子进程只选择其中一张经两次空闲检查的设备；不是同时占用四张。保持单重任务、最多一张GPU，其他任务进入则后续用其他获准空闲卡或CPU。具体实际设备逐产物记录。
