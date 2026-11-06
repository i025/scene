# V3归档与发布工具

`prepare_archive.py`、`offline_v3.py`不调用模型、不执行Blender、不操作Git、不覆盖V1–V2.4。V3可处于未完成状态；状态按实际保存，不把准备/会话结束当成十轮结束。下方另列的`publish.py`与`finalize.py`会按明确选项提交或发布。

```bash
PY=/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python
ROOT=/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender
cd "$ROOT"

# 只盘点，不写归档仓库、不打包。
"$PY" work/scene_v3_archive/prepare_archive.py \
  --source outputs/scene_rsi_v3 --repo archive/scene \
  --bundles work/scene_v3_archive/bundles \
  --tag scene-rsi-v3-10rounds-2026-11-07 --dry-run

# 在独立仓库的V3目录准备核心代码、指标、真实图、许可归属与逐文件索引。
"$PY" work/scene_v3_archive/prepare_archive.py \
  --source outputs/scene_rsi_v3 --repo archive/scene \
  --bundles work/scene_v3_archive/bundles \
  --tag scene-rsi-v3-10rounds-2026-11-07

# 所有许可允许的完整原始产物按preparation/baseline/roundXX/final打包。
# 现有同名包会拒绝覆盖；需要不同快照时使用新bundles目录。
"$PY" work/scene_v3_archive/prepare_archive.py \
  --source outputs/scene_rsi_v3 --repo archive/scene \
  --bundles work/scene_v3_archive/bundles \
  --tag scene-rsi-v3-10rounds-2026-11-07 --pack

# 从公开核心归档离线重画；新目录必须不存在。
"$PY" work/scene_v3_archive/offline_v3.py \
  --experiment archive/scene/experiments/scene_rsi_v3 \
  --output work/scene_v3_archive/derived_public_01
```

普通Git索引写入 `archive/scene/artifacts_index_v3.csv`；不修改旧的总索引或README。上传状态初始一律 `not_uploaded`；planned_download_url不是已经上传的链接。后续发布者需依据真实Git/Release上传结果更新状态。

大日志、全部生成的`.blend`/图像、失败与不完整轨迹进入对应Release包；不只保存成功方法。脚本未下载第三方资源，也不跟随源目录外的目录链接。参考媒体只明确公开已有CC许可的web_scenes图片并保留归属；优先采用本轮已经保存的参考副本，避免重复携带大图。BlenderWorld原始参考、其缩放副本和附件不进入Git或Release。公开引用处可以生成醒目标记的许可占位图，占位不算实验产物。没有许可来源依据的未知组合图亦保守占位，真实生成渲染仍保留。

文本只做服务器路径前缀替换。CLI角色、调用、usage、失败、选择与历史分数不删。二进制`.blend`原样保存，不以未经打开验证的字节替换修改工程文件；可能仍有服务器内部资源路径，来源依赖在复用清单中记录。未脱敏原件始终留在原服务器。

已经执行的验证：脚本语法检查、真实V3目录dry-run、离线重画到 `work/scene_v3_archive/offline_smoke_01/experiment/reports/index.html`。离线收据记录新模型调用0、Blender任务0。没有执行正式Release打包、git add、commit、push或上传。

## 发布与远端确认（工具已准备，本次编写工具未执行网络/上传）

以下需要先完成脱敏归档、检查并提交本次明确文件清单。发布工具不替你执行 `git add` 或commit，不更改origin/全局Git配置，不force push。目标分支固定 `research/scene-rsi-v3-10rounds`，默认tag为 `scene-rsi-v3-10rounds-2026-11-07`。

```bash
PY=/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/files-pasted-by-the-user-sceneevolve/work/.venv/bin/python
ROOT=/srv/lab-disks/disk2/users/xymo/Documents/Codex/2026-11-02/scene-rsi-rsi-1-3d-blender
cd "$ROOT"

# 先用现有Git helper；不读取登录配置或打印任何凭据。
"$PY" work/scene_v3_archive/publish.py status
"$PY" work/scene_v3_archive/publish.py push
"$PY" work/scene_v3_archive/publish.py release

# Release成功后检查并提交两个真实上传状态文件，再推送最终版本。
git -C archive/scene diff --stat -- docs/V3_RELEASE_UPLOAD_STATE.json artifacts_index_v3.csv
git -C archive/scene add -- docs/V3_RELEASE_UPLOAD_STATE.json artifacts_index_v3.csv
git -C archive/scene commit -m "Record actual V3 Release uploads"
"$PY" work/scene_v3_archive/publish.py push

V3_COMMIT=$(git -C archive/scene rev-parse HEAD)
"$PY" work/scene_v3_archive/verify_remote.py --commit "$V3_COMMIT" \
  --png experiments/scene_rsi_v3/figures/cpu_benchmark.png
```

只有现有Git helper实际失效、并且仍使用用户此前明确授权的两个shell变量时，才显式选择下面的子进程认证方式；它不是自动fallback，不向聊天或日志输出令牌。`.bashrc`只在授权子shell载入；令牌只经该认证子进程环境传入Git/Release API，不保存到文件，不更改账号或Git配置。

```bash
"$PY" work/scene_v3_archive/publish.py push --auth bashrc
"$PY" work/scene_v3_archive/publish.py release --auth bashrc
```

Release正文来自 `bundles/PACK_RECEIPT.json` 中实际归档的 `source_status`，不从未来计划补写完成情况。只有保存状态为 `all_scheduled_terminal` 且 `round_completed=10` 才写十轮终态；活动state仅写“不完整快照”，不据此声称进程当前仍在运行。已有同名附件只检查平台记录字节数；不同大小立刻拒绝，不覆盖、不删除。相同大小复用只代表大小匹配，不声称内容验证。

若需新的不可变快照，归档/打包和上传须统一使用新tag及新bundle目录，例如将三个命令中的tag均设置为 `scene-rsi-v3-10rounds-2026-11-07-snapshot02`、bundles均设置为 `work/scene_v3_archive/bundles_snapshot02`：

```bash
"$PY" work/scene_v3_archive/publish.py release \
  --tag scene-rsi-v3-10rounds-2026-11-07-snapshot02 \
  --bundles work/scene_v3_archive/bundles_snapshot02
```

`verify_remote.py`读取实际分支HEAD、公开README/代码/三张核心CSV/HTML/PNG，以及Release API附件列表和附件URL的HTTP可访问性；不下载大包、不做内容哈希。逐项收据写入 `work/scene_v3_archive/REMOTE_VERIFICATION.json`。网络、认证或API限流会明确报错并保留已核对部分，不无限重试、不声称所有内容已公开。

## 主任务终态后的单次收尾

`finalize.py`只读取指定主launch的实际退出记录与本实验锁，不根据旧state推断进程存活，不监视GPU，不重启任务。`--wait`最多36小时；未取得真实终态就退出并保存失败收据，不启动汇总、压缩或发布。真实终态为失败或超时时，仍按已有证据归档不完整状态。所有归档子进程绑定已获准CPU 0–7、数值线程1。它不启动第11轮，也不补采样。

```bash
# 此命令尚未由编写工具的子任务执行；实际启动由主工程师进行。
"$PY" work/scene_v3_archive/finalize.py --wait --wait-hours 36 --publish \
  --launch outputs/scene_rsi_v3/launches/003_resume.json

# 只有明确选用此前授权的shell认证桥时才加 --auth bashrc。
# 默认不启动任何新研究；可选回放必须另行显式指定已审阅的真实入口。
"$PY" work/scene_v3_archive/finalize.py --wait --wait-hours 36 --publish \
  --launch outputs/scene_rsi_v3/launches/003_resume.json \
  --auth bashrc --replay-entry work/scene_v3_archive/replay_stage/frozen_replay.py

# 仅纯临时夹具检查，不启动收尾、打包、Git、模型或Blender。
"$PY" work/scene_v3_archive/finalize.py --self-test
```

可选回放在主launch终态后首先执行`[PY, entry, 'prepare']`。该入口不调用模型，只检查当时真实的后代、陌生起点、数据隔离和剩余预算，并在stdout最后一行返回`{"entry_json":"/absolute/path/entry.json"}`。只有生成文件中`status=ready`、`eligibility.eligible=true`且`budget.allowed=true`时，收尾工具才执行其中的参数数组`command`，按其`timeout_seconds`限时。未ready、不合格和预算不足保留具体原因；入口退出0不自动代表元能力提高。

计划监看的正确主入口为A02交接后实际创建的`launches/003_resume.json`；该文件创建前不启动收尾。原001因A01工程修订主动暂停，退出143；002将在完整round0后通过提交边界暂停，以加载A02限时M验证修复，二者都不能当作本轮全部完成而提前收尾。A01在首个BW正式任务和首轮正式M之前修复公开规格附件路由及有效M程序判定；M0未变、10个已有H生成按相同信息条件复用，原偏离记录保留为历史。归档自身模型/Blender调用为0；可选回放的`actual_cli_sessions_delta`、主根与stage根联合渲染扣额单独记录，底层精确`model_requests`未知保留null，不把整条链称为零新增调用。真实`META_REPLAY_STATUS.json`及`COMPLETION_RECEIPT.json`优先于旧state.pending。

核心数据先形成已确定的提交，摘要随后链接该提交。推送成功后才把实际已跟踪的核心索引行标为`git_uploaded`并保存真实Git证据；Release收据只按实际返回URL更新。匿名远端读取后将真实验证收据与`verified_commit`另行提交，最后只核对新分支HEAD，避免摘要自指循环。推送、上传、API或读取失败均保留本地提交和准确状态，不无限重试。

每次收尾使用唯一`snapshot_id`，完整包放`work/scene_v3_archive/bundles/<snapshot_id>/`，原始V3源码、候选、失败与冻结平台保留。私有运行收据及命令日志在`work/scene_v3_archive/finalizations/<snapshot_id>/`，含实际但本次未执行的完整续跑参数数组。未开始的Test与缺失指标保持null，渲染预算扣额不冒充精确实际帧数。

M后代“作为后续轮次父代”的版本关系单独记录，不能替代“改动内容实际参与执行”的证据。收尾会调用replay_stage中纯读取的`descendant_execution_audit`，保存`metrics/M_changed_content_execution_audit.json`：只关联同一次后续研发中的改动入口、已加载helper或名称+源码匹配的成功动作。没有合资格记录时明确未验证/null；动作库只作为文字出现在上下文不算执行，更不证明能力提高。更新脚本源码不会改变已经启动并缓存旧代码的等待控制器，是否重新载入由主工程师另行记录。
