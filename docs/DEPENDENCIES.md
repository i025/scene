# 依赖、来源与路径

归档保留原目录结构：`experiments/scene_rsi_pilot/`。根目录Python文件、backend、initial_meta、candidates、frozen、校正与preuse目录是已执行/保存的版本；`scripts/`只为本次归档新增，不属于被研究的H或M。源码和日志中的服务器账户路径已做明确替换；.blend公开副本仅对账户路径做等长字节替换，保留全部数据块尺寸和场景数值，未公开原账户。没有对594个会话逐个保存完整工程快照；应结合既有快照、diff、冻结标记和时间确认版本，不能确认的逐调用版本不补造。

|来源|实际版本/所需资源|归档方式|
|---|---|---|
|本地SceneEvolve复现|MIT，haoyu-agent 2026；初始baseline、SceneAct、Runtime、teacher模板|必要源码在backend、初始H0、baseline_mapping；原MIT许可随附，不采用历史分数。|
|Hyperagents|官方方法/代码作为准备阶段映射参考，本地没有完整实现|本地generic_rsi_cli_adapted及映射说明；没有伪称完整官方执行。|
|BlenderWorld|QwenLM/BlenderWorld，本地数据卡和代码声明MIT|使用的两个任务query/rubric、评审意义与数据许可；未复制223任务全集。|
|Blender|4.2.10 LTS|不上传软件、运行环境或编译缓存；新机器自行提供可用Blender。CPU路径可用，不要求GPU。|
|Codex CLI|0.163.0，本机已登录；sol/astra medium|适配器、help/version、请求与真实日志；不上传登录文件。归档重算不需要CLI。|
|DINOv2|本地facebook/dinov2-base|不上传权重；正式指标为已有真实前向。未来计算需同版本本地模型目录，local_files_only。|
|LPIPS|lpips0.1.4、AlexNet、v0.1/alex.pth|不上传权重/缓存；未来前向需明确AlexNet checkpoint与LPIPS权重路径。|
|FFmpeg|7.1.1|可选，未制作转台，不上传二进制。|

实际Python3.11；已有环境可直接复用，本次没有安装依赖或更改共享环境。记录的库：Pillow11.3.0、numpy1.26.0、matplotlib3.9.4、torch2.5.1+cu121、transformers4.57.6、scikit-image0.23.1、PyYAML6.0.3、requests2.34.2。只离线汇总/重画需要Python3.11、Pillow、numpy、matplotlib；GitHub附件上传脚本另需requests和现有Git凭据。

公共占位符：`__EXPERIMENT_ROOT__`是本实验根；`__SCENEEVOLVE_REPRO__`是原复现根；`__BLENDERWORLD_ROOT__`是已获取的BlenderWorld根；`__COMMONS_DATA_ROOT__`是本地Commons资源根；`__SERVER_USER_ROOT__`隐藏服务器账户根。离线脚本仅把实验内部路径重定位到独立输出视图，不会尝试寻找账户、下载权重、调用CLI或Blender。

原run.sh/runner中的环境特定路径作为as-run源码保留并脱敏，不冒称新机器可直接启动研究。其他机器如要开展新研究，应显式配置上述资源与config.json，另冻结协议；本次提供并实际验证的可移植入口是离线汇总/重画。原服务器续跑入口见README，本次未执行。

## 许可与署名

没有给整个仓库新增统一许可证。原SceneEvolve和BlenderWorld MIT文本在 [third_party_licenses](third_party_licenses/)；Blender为外部GPL软件，未打包它的二进制或源码。模型/数值库继续遵守各自许可，不随归档转授权。

Commons实际使用图片的作者、页面、许可和链接见 [DATA_ATTRIBUTIONS.csv](DATA_ATTRIBUTIONS.csv)。保存的参考经过等比缩放/RGB转换；联系表组合、排版、缩略处理属于归档加工，保留各组成图像署名和原CC BY/CC BY-SA条件，不能用代码MIT许可覆盖图片。生成场景与渲染关联源图并保留同一归属索引，不声称消除底层图片权利。

BlenderWorld只随附本轮实际使用的bw_0005、bw_0011及上游声明MIT的本地数据许可证/数据卡摘录；不为参考中可能包含的独立第三方内容另行宣称权利。其来源通过上游任务ID获取，不称为自建原图。未使用的预留数据、权重、环境、缓存不公开。
