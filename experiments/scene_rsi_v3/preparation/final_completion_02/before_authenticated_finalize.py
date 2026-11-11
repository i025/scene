"""Bounded V3 archival after one recorded launch; never resumes the main study.

Default authentication stays with Git. --auth bashrc is forwarded only to the
existing child publisher; this script never reads shell credentials or tokens.
Only --replay-entry explicitly opts into the separately reviewed replay entry.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

WORK = Path(__file__).resolve().parent
PROJECT = WORK.parents[1]
EXPERIMENT = Path('experiments/scene_rsi_v3')
BRANCH = 'research/scene-rsi-v3-10rounds'
TERMINAL = {'completed','invalid','failed','timeout','unchanged','rejected','selected'}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def launch_classification(record):
    terminal = (record.get('status') in {'completed','failed','timeout'}
                and isinstance(record.get('returncode'),int)
                and isinstance(record.get('finished'),(int,float)))
    return {'terminal':terminal,'status':record['status'],'returncode':record.get('returncode'),
            'pid':record['pid'],'finished':record.get('finished')}


def source_busy(source):
    path = source/'experiment.lock'
    if not path.exists():
        return False
    with path.open('r') as stream:
        try:
            fcntl.flock(stream,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(stream,fcntl.LOCK_UN)
    return False


def wait_launch(path,source,wait,hours):
    """Only this launch result and its experiment lock are observed, never a GPU."""
    if not 0 < hours <= 36:
        raise ValueError('Wait limit must be >0 and <=36 hours')
    deadline = time.monotonic()+hours*3600
    while True:
        # A02 deliberately records this exact resume only after baseline closes.
        if not path.exists():
            if not wait:
                raise FileNotFoundError(path)
            if time.monotonic()>=deadline:
                raise TimeoutError('Planned launch was not created before bounded wait ended; nothing archived')
            time.sleep(min(5,deadline-time.monotonic()))
            continue
        # run_measured replaces its external JSON at completion; allow one brief read retry.
        try:
            record = read(path)
        except json.JSONDecodeError:
            time.sleep(.2);record = read(path)
        status = launch_classification(record)
        if status['terminal']:
            # The launcher may still be releasing its lock after writing the final record.
            for _ in range(5):
                if not source_busy(source):
                    return {**status,'launch_record':record}
                time.sleep(1)
            raise RuntimeError('Terminal watched launch, but an experiment still holds its lock; no archive started')
        if not wait:
            raise RuntimeError('Launch has no recorded terminal result; state.json alone is not process evidence. Use --wait.')
        if time.monotonic()>=deadline:
            raise TimeoutError('Bounded wait ended without a terminal launch result; no experiment was restarted or archived')
        time.sleep(min(30,deadline-time.monotonic()))


def run(command,folder,name,*,cwd=None,timeout=1800):
    environment = os.environ.copy()
    for key in ['GIT_CURL_VERBOSE','GIT_TRACE','GIT_TRACE_CURL','BASH_ENV','ENV']:
        environment.pop(key,None)
    environment.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
                       NUMEXPR_NUM_THREADS='1',GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',
                       CUDA_VISIBLE_DEVICES='')
    started = time.time()
    with (folder/(name+'.stdout.log')).open('w') as out,(folder/(name+'.stderr.log')).open('w') as err:
        process = subprocess.Popen(command,cwd=cwd,stdout=out,stderr=err,env=environment,start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Only this finalizer-owned command tree is stopped, never the main job.
            os.killpg(process.pid,signal.SIGKILL);process.wait()
            write(folder/(name+'.json'),{'command':command,'status':'timeout','returncode':process.returncode,
                                         'started':started,'finished':time.time(),'timeout_seconds':timeout})
            return 124
    write(folder/(name+'.json'),{'command':command,'status':'completed' if code==0 else 'failed',
                                 'returncode':code,'started':started,'finished':time.time()})
    return code


def replay_request(path):
    """Eligibility is produced after the main run, never filled by this tool."""
    entry = read(path)
    decision = {'entry':str(path),'entry_status':entry['status'],'executed':False,
                'eligibility':entry['eligibility'],'budget':entry['budget']}
    if entry['status']!='ready':
        return {**decision,'status':'skipped_not_ready'}
    if not entry['eligibility']['eligible']:
        return {**decision,'status':'skipped_ineligible'}
    if not entry['budget']['allowed']:
        return {**decision,'status':'skipped_budget'}
    if not isinstance(entry['command'],list) or not entry['command'] or any(not isinstance(s,str) for s in entry['command']):
        raise ValueError('Replay command must be a nonempty subprocess argument array')
    if not 0 < entry['timeout_seconds'] <= 36*3600:
        raise ValueError('Replay entry timeout must be positive and bounded by 36 hours')
    return {**decision,'status':'approved','command':entry['command'],
            'timeout_seconds':entry['timeout_seconds']}


def recorded_usage(source):
    stage=source/'meta_replay_stage'
    requests=set(source.rglob('request.json'))
    charges={}
    for name,root in [('main',source),('replay_stage',stage)]:
        ledger=root/'render_attempts.jsonl'
        charges[name]=sum(json.loads(line)['frames'] for line in ledger.read_text().splitlines()) if ledger.exists() else None
    joint=(charges['main']+charges['replay_stage']) if all(value is not None for value in charges.values()) else charges['main'] if not stage.exists() else None
    return {'recorded_cli_sessions':len(requests),'model_requests':None,
            'render_budget_charged_by_root':charges,'combined_render_budget_charged':joint,
            'actual_render_attempts_exact':None,'actual_render_completed_exact':None}


def optional_replay(path,folder,source):
    before=recorded_usage(source)
    if path is None:
        return {'status':'not_started','reason':'Replay entry not requested','executed':False,
                'actual_cli_sessions_delta':0,'model_requests':None,'usage_before':before,'usage_after':before}
    # --replay-entry is an explicit opt-in to the one code-reviewed Python entry.
    code = run([sys.executable,str(path.resolve()),'prepare'],folder,'replay_prepare',timeout=180)
    if code:
        decision={'status':'prepare_failed','executed':False,'returncode':code,'entry_program':str(path)}
    else:
        prepared = json.loads((folder/'replay_prepare.stdout.log').read_text().splitlines()[-1])
        decision = replay_request(Path(prepared['entry_json']))
        if decision['status']=='approved':
            code = run(decision['command'],folder,'replay_run',timeout=decision['timeout_seconds'])
            decision.update(executed=True,returncode=code,
                            status='entry_returned_success' if code==0 else 'entry_failed')
    after=recorded_usage(source)
    decision.update(actual_cli_sessions_delta=after['recorded_cli_sessions']-before['recorded_cli_sessions'],
                    model_requests=None,usage_before=before,usage_after=after,
                    accounting_note='Unique saved request.json paths, not exact underlying model requests; render values are conservative budget charges')
    write(folder/'REPLAY_DECISION.json',decision)
    return decision


def required(command,folder,name,*,cwd=None,timeout=1800):
    code = run(command,folder,name,cwd=cwd,timeout=timeout)
    if code:
        raise RuntimeError(name+' failed; local logs retained in '+str(folder))


def changed_content_audit(source):
    path=WORK/'replay_stage/frozen_replay.py'
    spec=importlib.util.spec_from_file_location('v3_archive_changed_content_audit',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.descendant_execution_audit(source)


def facts(source):
    state,config,summary = read(source/'state.json'),read(source/'config.json'),read(source/'metrics/summary.json')
    rounds = [read(path) for path in sorted((source/'rounds').glob('*/record.json'))]
    scenes = [read(path) for path in sorted((source/'results').rglob('record.json'))]
    H = state.get('H_best',state.get('H_retained',state['H_start']))
    accepted_M = {row['M_candidate'] for row in rounds if row['M_accepted']}
    used_M = {row['M_parent'] for row in rounds}
    representative = next((row for row in scenes if row['valid'] and (Path(row['folder'])/'scene.blend').exists()),None)
    edits = [read(path) for path in (source/'semantic_edits').glob('*/*/status.json')]
    replay_status_path=source/'META_REPLAY_STATUS.json'
    replay_receipt_path=source/'meta_replay_stage/COMPLETION_RECEIPT.json'
    replay_status=read(replay_status_path) if replay_status_path.exists() else None
    replay_receipt=read(replay_receipt_path) if replay_receipt_path.exists() else None
    observed_replay=replay_receipt if replay_receipt is not None else replay_status
    changed_audit=changed_content_audit(source)
    final_stats=read(source/'metrics/final_test_summary.json') if (source/'metrics/final_test_summary.json').exists() else None
    m07=read(source/'metrics/M07_review.json') if (source/'metrics/M07_review.json').exists() else None
    return {'state':state,'config':config,'summary':summary,'rounds':rounds,'H_best_or_current':H,
        'final_test_statistics':final_stats,
        'M07_review_summary':{key:m07[key] for key in ['changed_files','entrypoint_identical','action_count','subsequent_M07_action_count','H08_validation_delta','best_H_created_before_M07','retained_H_updates_after_M07','meta_capability_improvement_established']} if m07 else None,
        'round_statuses':dict(Counter(row['status'] for row in rounds)),
        'terminal_rounds':sum(row['status'] in TERMINAL for row in rounds),
        'H_accepted':sum(row['H_accepted'] for row in rounds),'M_accepted':len(accepted_M),
        'M_descendants_used_in_later_recorded_round':sorted(accepted_M & used_M),
        'M_descendant_versions_as_later_parents':sorted(accepted_M & used_M),
        'M_changed_content_execution_audit':changed_audit,
        'scene_failures':dict(Counter(row['failure_type'] or 'unknown' for row in scenes if not row['valid'])),
        'evaluation_failures':dict(Counter(row['bw'].get('failure_type') or 'unknown' for row in scenes if row['bw']['evaluation_status']=='eval_failed')),
        'semantic_edit_statuses':dict(Counter(row['status'] for row in edits)),
        'semantic_target_independent_validation':'not inferred from editing execution or preservation',
        'representative_blend':str((Path(representative['folder'])/'scene.blend').relative_to(source)) if representative else None,
        'frozen_platform_snapshot_present':(source/'code_snapshots/platform_frozen').is_dir(),
        'active_A03_snapshot_present':(source/'code_snapshots/platform_A03').is_dir(),
        'active_A04_snapshot_present':(source/'code_snapshots/platform_A04').is_dir(),
        'postten_A05_snapshot_present':(source/'code_snapshots/platform_A05_postten_resume').is_dir(),
        'meta_replay_status':observed_replay['status'] if observed_replay is not None else state.get('meta_replay_status','not_recorded'),
        'meta_replay_status_record':replay_status,'meta_replay_completion_receipt':replay_receipt,
        'historical_state_meta_replay_status':state.get('meta_replay_status'),
        'joint_recorded_usage':recorded_usage(source)}


def number(value):
    return 'pending/null' if value is None else f'{value:.4f}' if isinstance(value,float) else str(value)


def summary_text(data,launch,publication,core_commit,replay=None):
    summary,config = data['summary'],data['config']
    lines = ['# Scene-RSI V3 实际收尾摘要','',
        '这是一条连续程序研发轨迹，不是十次独立实验，也不是基础模型权重训练。',
        f"监看的真实launch终态：{launch['status']}，退出码 {launch['returncode']}；state阶段：{data['state']['phase']}。",
        f"保存终态研发回合 {data['terminal_rounds']}/10；H接受 {data['H_accepted']} 次，M接受 {data['M_accepted']} 个。失败、拒绝和unchanged保留，不能称十次成功升级。",
        f"各轮状态：{json.dumps(data['round_statuses'],ensure_ascii=False)}。后代版本作为后续轮次父代：{data['M_descendant_versions_as_later_parents'] or '无保存证据'}；这个版本关系不证明改动内容真正执行。",'',
        f"H请求模型 {config['model']['name']} / {config['model']['reasoning_effort']}；M与共享编码 {config['proposer']['model']} / {config['proposer']['reasoning_effort']}；独立judge {config['evaluation']['judge_model']}。",
        '全部通过Codex CLI。observed_model与请求模型分开；没有元数据则unknown，本地费用未知，不宣称降本。',
        f"CPU {config['resources']['cpu_total']}，内存上限 {config['resources']['memory_limit_gb']} GB，Blender {config['resources']['blender_workers']}×{config['resources']['threads_per_blender']}线程，CPU-only，未使用GPU（数量0）。",
        f"H整场{config['budget']['seconds']}秒、CLI{config['model']['timeout']}秒、build{config['blender']['build_timeout']}秒、render{config['blender']['render_timeout']}秒。进程树RSS为采样下界，阶段时长不相加作总墙钟。",'',
        f"正式场景记录 {summary['scene_records']}；有效执行 {summary['scene_execution_success_count']}，终测状态 {summary['test_status']}，已结束记录 {summary['test_completed']}，另有未结算终测中断 {summary.get('test_interrupted_without_final_record','unknown')}。",
        f"终测重复计划：{json.dumps(summary['test_repeat_policy'],ensure_ascii=False)}。未开始/缺测保持null，服务评价失败与生成失败分开。",
        f"生成失败分类：{json.dumps(data['scene_failures'],ensure_ascii=False)}；外部评价失败：{json.dumps(data['evaluation_failures'],ensure_ascii=False)}。",'',
        '| 划分 / H | 全预定 | 执行完成 / 成功 | BW覆盖 | 条件BW | 条件Q | 端到端BW效用 |','|---|---:|---|---:|---:|---:|---:|']
    for row in summary['group_summary']:
        lines.append(f"| {row['split']} / {row['H_version']} | {number(row['all_scheduled'])} | {row['execution_finished']} / {row['execution_success']} | {row['BW_measured']} | {number(row['BW_conditional_mean'])} | {number(row['Q_conditional_mean'])} | {number(row['end_to_end_BW_utility'])} |")
    if 'paired_final_test' in summary:
        pairs=summary['paired_final_test']
        lines += ['',f"独立来源配对：{pairs['sources_with_scored_pair']}/{pairs['sources_scheduled']} 来源、{pairs['matched_successful_generation_pairs']} 对双方成功且已评分的生成；来源等权条件BW差 {number(pairs['conditional_BW_difference_source_mean'])}。全预定来源的端到端BW效用差 {number(pairs['all_scheduled_BW_utility_difference_source_mean'])}；完整效用覆盖 {pairs['sources_with_complete_utility']}/{pairs['sources_scheduled']}。重复和视角不作为独立场景。",'',
                  '[终测逐来源配对数据](experiments/scene_rsi_v3/metrics/paired_test_sources.csv) / [逐生成点](experiments/scene_rsi_v3/metrics/paired_test_generations.csv)。']
    lines += ['',f"实际CLI会话 {summary['cli_sessions']}；usage可见 {summary['usage_coverage_sessions']}/{summary['usage_total_sessions']}；已知输入/输出token {summary['known_input_tokens']}/{summary['known_output_tokens']}（不是缺失部分的估计）。",
        f"主根渲染预算扣额 {summary['render_accounting']['render_budget_charged']}；主根+独立回放根联合扣额 {number(data['joint_recorded_usage']['combined_render_budget_charged'])}，包括保守预扣；精确实际attempt/completed仍unknown，分来源证据见render_evidence.csv。",
        f"文字编辑状态：{json.dumps(data['semantic_edit_statuses'],ensure_ascii=False)}；机械结构/编辑检查不等于语义目标正确。",
        '[A07公共文字编辑执行器恢复](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_07.md)：四项原程序外层校验通过，Blender重复导入模型适配器后缺少yaml导致平台失败；保留四次失败，各用原程序额外执行一次，未新增模型调用、修改目标或编辑程序。原单次执行协议与恢复后的累计两次分列；语义身份未独立验证。',
        f"冻结元回放状态：{data['meta_replay_status']}，优先读取真实独立收据；原state中的历史字段：{data['historical_state_meta_replay_status']}。本工具不从H分数曲线推断元能力，未完成真实回放就不作元能力提升结论。",'',
        '| round | 实际H / M父代 | 类型 | H接受 / M接受 | 保留H / M | 状态 |','|---|---|---|---|---|---|']
    for row in data['rounds']:
        lines.append(f"| {row['round']} | {row['H_parent']} / {row['M_parent']} | {row['candidate_type']} | {row['H_accepted']} / {row['M_accepted']} | {row['H_retained']} / {row['M_retained']} | {row['status']} |")
    lines += ['', '主要评价为 **BW-style / CLI-adapted**，不是官方榜单分数；开发preview与正式Selection/Test分开。全部数据是探索性研究，历史暴露和来源独立性限制保留。',
        '本轮平台与M0属于工程实现；只有实际模型提出、保存diff并执行的H/M变化才属于自动演化。可执行后代与动作复用都不自动等于能力改善。',
        f"原始冻结平台保留：{data['frozen_platform_snapshot_present']}；实际续跑A03快照保留：{data['active_A03_snapshot_present']}；A04编码修复快照保留：{data['active_A04_snapshot_present']}；A05终测续跑快照保留：{data['postten_A05_snapshot_present']}。整理版分析脚本不替换实际执行的H/M/生成器/评价器快照。",'',
        '## 审查入口','',
        '- [README](README.md) / [审查索引](docs/V3_REVIEW_INDEX.md)',
        '- [A01实际平台修订](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_01.md)：公开附件已通过同一入口转发；原偏离记录保留，M0未变。修订在首个BW正式任务和首轮正式M前完成，已有10个H生成结果按相同信息条件复用。',
        '- [A03实际修订与操作员重跑](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_03.md) / [A03源码](experiments/scene_rsi_v3/code_snapshots/platform_A03/)：首个M提案产生后修复原生照明证据；M提案原样保留、旧产物不覆盖、共同重跑与预算分配明确记录。',
        '- [A04无损编码修复](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_04.md) / [A04源码](experiments/scene_rsi_v3/code_snapshots/platform_A04/)：第6轮后、第7轮M调用前修复JSON空格触发的证据大小检查；H/M、评分和预算不变，原中断保留。',
        '- [A05网络恢复与冻结续跑](experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_05.md)：保留服务超时失败，不替换样本，原终测前H/M冻结与时间戳不变；不是自动M修改。',
        '- [中文报告](experiments/scene_rsi_v3/reports/REPORT_ZH.md) / [本地HTML](experiments/scene_rsi_v3/reports/index.html)',
        '- [逐轮](experiments/scene_rsi_v3/metrics/rounds.csv) / [逐场景](experiments/scene_rsi_v3/metrics/scenes.csv) / [动作](experiments/scene_rsi_v3/metrics/actions.csv)',
        '- [CLI](experiments/scene_rsi_v3/metrics/cli_audit.csv) / [时序](experiments/scene_rsi_v3/metrics/timing.csv) / [渲染记录](experiments/scene_rsi_v3/metrics/render_evidence.csv)',
        '- [真实图表](experiments/scene_rsi_v3/figures/) / [全部附件索引](artifacts_index_v3.csv)',
        f"- 代表工程包内相对位置：`{str(EXPERIMENT/data['representative_blend']) if data['representative_blend'] else '未保存可用.blend'}`；二进制在Release包，不冒充Git中已存在的文件。",'',
        '## 上传与尚未完成项','',
        f"Git发布：{publication['git']}；Release：{publication['release']}；远端读取确认：{publication['verification']}。",
        f"Release实际收据链接：{publication.get('release_url') or '尚无上传成功收据'}。未获分发许可的BW原始参考及附件保留本地，公开占位不算实验结果。"]
    if replay:
        lines += [f"可选回放入口：{replay['status']}；入口是否执行：{replay['executed']}；前后保存request计数差 {number(replay['actual_cli_sessions_delta'])} 次CLI会话。精确底层model_requests=null，不将整条收尾链称为零调用。归档自身模型/Blender调用为0，回放另计。入口退出码0也不自动证明回放完成或元能力提高，实际结果仍以独立回放记录为准。"]
    changed=data['M_changed_content_execution_audit']
    executed=[{'M_version':row['M_version'],'round':row['executed_in_round'],'executed_changed_files':row['executed_changed_files']}
              for row in changed['descendant_uses'] if row['eligible']]
    lines += [f"改动M内容参与后续研发的保存证据：{json.dumps(executed,ensure_ascii=False) if executed else '未验证/null'}；审计状态：{changed['status']}。证据仅到改动入口/模块/动作的实际参与，不是语句覆盖或能力提升。详见[源码与执行关联审计](experiments/scene_rsi_v3/metrics/M_changed_content_execution_audit.json)。"]
    if data['meta_replay_completion_receipt'] is not None:
        receipt=data['meta_replay_completion_receipt']
        values={key:receipt[key] for key in ['status','scheduled_trials','terminal_trials','complete_valid_paired_starts','MetaImp_at_1']}
        lines += ['[独立回放实际收据](experiments/scene_rsi_v3/meta_replay_stage/COMPLETION_RECEIPT.json)：'+json.dumps(values,ensure_ascii=False)+
                  '。少量陌生起点上的一次提案仅为可行性证据，不能证明普遍元能力提高。']
    if publication.get('verified_commit'):
        lines += [f"已实际读取确认的归档提交：[查看提交](https://github.com/i025/scene/commit/{publication['verified_commit']})。后续收据提交不反向改变这次读取的对象。"]
    if core_commit:
        lines += ['',f'实验数据归档提交：[查看提交](https://github.com/i025/scene/commit/{core_commit})。此链接指向已确定的数据提交，摘要的后续提交不自指。']
    if data['final_test_statistics'] is not None:
        result=data['final_test_statistics']
        lines += ['', '## 六来源终测与M07专项审查', '',
                  '[完整终测统计](experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md) / [24项原始数据](experiments/scene_rsi_v3/metrics/final_test_raw.csv) / [六来源配对](experiments/scene_rsi_v3/metrics/final_test_sources.csv)。',
                  f"Selection BW：{result['selection_start_BW']:.6f} → {result['selection_H04_BW']:.6f}；Final Test BW配对差及来源bootstrap区间：{json.dumps(result['paired_differences']['BW'],ensure_ascii=False)}。",
                  f"失败零效用差：{json.dumps(result['paired_differences']['BW_utility'],ensure_ascii=False)}。生成失败计零效用、原始测量保持null；评价服务失败与pending不计零。",
                  'H的实际改动边界：H02改变了内层反馈的数据流，每次有效渲染后重新附上原参考图与当前渲染，并加入共享比较指导；H04在此基础上增加数值投影代码示例和相机调整指导。这是共享重建流程和提示的变化，不是新增由固定runner强制执行的投影校准器。H08的材质指导也只是共享生成/修复指导，未成为独立材质修复模块。实际差异见C02/C04/C08的H.diff，不把提示中的代码示例写成已强制执行的新算法。',
                  '[M07源码与全动作审查](experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md)：'+json.dumps(data['M07_review_summary'],ensure_ascii=False)+'。H04产生于第4轮，早于M07，不能将H04收益归因于M07。']
    if publication.get('base_release_url'):
        lines += ['', '原13包的基础Release：'+publication['base_release_url']+'；本次仅上传preparation/final两个更新包，未变化的baseline与round01–10按显式版本复用原附件，不重复上传。']
    lines += ['', '## 离线与续跑','',
        '离线重画（不调用模型/Blender）：', '```bash',
        'python docs/archive_tools_v3/offline_v3.py --experiment experiments/scene_rsi_v3 --output derived/v3_review_01','```',
        '仅在实际存在未完成任务并经现场核对后，激活原有venv并在服务器项目根目录续跑；收尾工具本次不执行此命令：','```bash',
        'python outputs/scene_rsi_v3/launch.py finish_test','```',
        'resume仅补未完成任务，不重抽终态失败、不启动第11轮。完整完成时无须续跑；不足部分明确保留pending。']
    return '\n'.join(lines)+'\n'


def replace_readme(old,summary):
    marker = '\n# Scene-RSI V2.4：'
    start = old.index(marker)+1
    old_tail = old[start:]
    intro = ['# Scene-RSI V3：十轮连续演化的实际状态','',
             '本区依据保存的运行与候选记录整理；不把退出码0、会话结束或旧state单独当成全部实验完成。',
             '[完整收尾摘要](UPLOAD_SUMMARY_V3.md) · [审查索引](docs/V3_REVIEW_INDEX.md) · [中文报告](experiments/scene_rsi_v3/reports/REPORT_ZH.md) · [离线HTML](experiments/scene_rsi_v3/reports/index.html)','']
    # Summary text is already derived from real records. Keep its substantive status lines.
    intro += summary.splitlines()[3:12]
    intro += ['',next((line for line in summary.splitlines() if line.startswith('独立来源配对：')),'独立来源配对数据尚未保存。')]
    intro += ['', '![历史开发图全体面板](experiments/scene_rsi_v3/figures/development_contact_sheet.png)',
              '![真实候选与实际保留版本](experiments/scene_rsi_v3/figures/evolution.png)',
              '![真实研究动作与负结果](experiments/scene_rsi_v3/figures/shared_patch_case.png)',
              '![终测原始重复与独立来源配对](experiments/scene_rsi_v3/figures/final_test_pairs.png)',
              '![实际成本与耗时](experiments/scene_rsi_v3/figures/cost_and_timing.png)',
              '![六来源终测全部重复](experiments/scene_rsi_v3/figures/final_test_contact_sheet.png)',
              '![六来源BW与八维分项](experiments/scene_rsi_v3/figures/final_test_quality.png)',
              '![M07六次实际动作](experiments/scene_rsi_v3/figures/M07_action_evidence.png)','',
              '[终测专项统计](experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md) · [M07深入审查](experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md)。公开BW参考列因许可未确认而留空；含真实参考的完整联系表仅保留本地。','',
              'BW-style / CLI-adapted，不是官方榜单。开发历史图为研发已暴露数据；失败、服务故障、缺测与pending分开。没有真实冻结元回放就不宣称元能力提升。',
              '以下V2.4原文逐字保留，其数值不属于V3。','','---','']
    return '\n'.join(intro)+old_tail


def review_text():
    return '''# V3实际证据审查索引

本索引不预判方法有效。当前终态、失败、缺测、上传及未完成项见[收尾摘要](../UPLOAD_SUMMARY_V3.md)；旧准备阶段索引另存带snapshot编号的副本。

| 主张 → 问题 | 对应代码 | 原始数据 → 图表 | 局限 |
|---|---|---|---|
| 共享H起点及实际候选 | [H_start](../experiments/scene_rsi_v3/fixed_h/historical_r1_C2_start/) / [所有候选](../experiments/scene_rsi_v3/candidates/) | [rounds](../experiments/scene_rsi_v3/metrics/rounds.csv) → [演化图](../experiments/scene_rsi_v3/figures/evolution.png) | 历史r1/C2不是original_H0，10轮是连续轨迹 |
| M决策、动作与后续实际执行 | [初始M](../experiments/scene_rsi_v3/initial_m/) / [研究接口](../experiments/scene_rsi_v3/research.py) | [动作表](../experiments/scene_rsi_v3/metrics/actions.csv) / [真实轨迹](../experiments/scene_rsi_v3/meta_traces/) → [研究链](../experiments/scene_rsi_v3/figures/research_chain.png) | 新动作、可执行后代和后续使用不是能力提高的充分证据 |
| Selection选择及独立Test覆盖 | [实际续跑平台](../experiments/scene_rsi_v3/code_snapshots/platform_A04/) / [报告整理差异](../experiments/scene_rsi_v3/REPORT_ADAPTATION_AFTER_ROUND10.md) | [逐生成](../experiments/scene_rsi_v3/metrics/scenes.csv) / [独立来源配对](../experiments/scene_rsi_v3/metrics/paired_test_sources.csv) → [原始点与差异](../experiments/scene_rsi_v3/figures/final_test_pairs.png) | 生成重复与视角不作独立来源，pending不填零；同模型评审偏差 |
| A01平台修订与真实公开输入 | [A01修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_01.md) / [A01源码](../experiments/scene_rsi_v3/code_snapshots/platform_A01/) | 旧001工程暂停退出143及新002续跑记录保留；已有10个H生成复用 | M0未变，修订在首个BW正式任务和首轮正式M前；旧偏离文档是历史记录 |
| A03评价器修复与中断重跑 | [A03修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_03.md) / [固定原生收集器](../experiments/scene_rsi_v3/eval_blend.py) | 旧score/facts/record全部保留，scenes.csv的primary_analysis区分原attempt；成本含全部失败与中断 | 发生在首个H-only提案后，不冒充pre-M；A03照明字段的评分抖动未重测 |
| A04研究证据编码修复 | [实际源码](../experiments/scene_rsi_v3/code_snapshots/platform_A04/) / [修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_04.md) | 第7轮失败包428577字节→无损紧凑JSON405383字节，9个实际面板与stub通过；0模型/Blender调用 | 原6轮、H/M、原始证据、评分与硬预算不变；不是自动M后代 |
| A05终测服务中断与续跑 | [续跑快照](../experiments/scene_rsi_v3/code_snapshots/platform_A05_postten_resume/) / [原始恢复证据](../experiments/scene_rsi_v3/preparation/service_recovery_01/) | [服务事件](../experiments/scene_rsi_v3/metrics/cli_service_events.csv) / [协议](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_05.md) | Connection refused后900秒超时保留；不重抽失败，不将传输失败归因为几何退化 |
| 结构与编辑保持 | [固定回归](../experiments/scene_rsi_v3/regression.py) / [文字编辑器](../experiments/scene_rsi_v3/semantic_edit.py) | [机械检查](../experiments/scene_rsi_v3/metrics/scenes.csv) / [文字编辑](../experiments/scene_rsi_v3/metrics/semantic_edit_summary.csv) → [实际前后图](../experiments/scene_rsi_v3/figures/semantic_edit_results.png) / [校准夹具](../experiments/scene_rsi_v3/preparation/functional_fixtures/index.html) | 文字编辑是否实际执行以逐任务状态为准；未完成不作通过结论，中心家具语义身份未独立验证，无自然图像3D真值 |
| 成本与失败来源 | [固定运行时](../experiments/scene_rsi_v3/backend/runtime.py) | [CLI](../experiments/scene_rsi_v3/metrics/cli_audit.csv) / [时序](../experiments/scene_rsi_v3/metrics/timing.csv) / [渲染证据](../experiments/scene_rsi_v3/metrics/render_evidence.csv) → [成本图](../experiments/scene_rsi_v3/figures/cost_and_timing.png) | 全局frame字段为预算扣额，实际精确帧总量未知；缺失usage不计为零 |

## 终测收尾与M07专项审查

| 主张 → 问题 | 对应代码 | 原始数据 → 图表 | 局限 |
|---|---|---|---|
| 24项原计划是否结算 | [A06恢复入口](../experiments/scene_rsi_v3/finish_test.py) / [修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_06.md) | [逐项状态](../experiments/scene_rsi_v3/metrics/final_test_schedule.csv) / [完整原始值](../experiments/scene_rsi_v3/metrics/final_test_raw.csv) → [全部来源与重复](../experiments/scene_rsi_v3/figures/final_test_contact_sheet.png) | 保留两项生成失败；已有生成结果只恢复尚未使用的固定评审重试，旧失败另存原件 |
| 六来源的收益和不确定性 | [统计脚本](../experiments/scene_rsi_v3/final_statistics.py) | [来源配对](../experiments/scene_rsi_v3/metrics/final_test_sources.csv) / [完整统计](../experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md) → [质量与八维](../experiments/scene_rsi_v3/figures/final_test_quality.png) | 事后补充的六来源bootstrap，小样本探索性；重复和视角不是独立来源，未用Test重新选H |
| 公共编辑执行器恢复 | [执行器](../experiments/scene_rsi_v3/semantic_edit.py) / [确定性恢复入口](../experiments/scene_rsi_v3/recover_edits.py) | [A07修订](../experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_07.md) / [真实恢复收据](../experiments/scene_rsi_v3/A07_EDIT_RECOVERY.json) / [编辑表](../experiments/scene_rsi_v3/metrics/semantic_edit_summary.csv) → [前后图](../experiments/scene_rsi_v3/figures/semantic_edit_results.png) | 四个原失败保留；每项共同增加一次相同程序执行，没有新增模型或人工编辑补丁；机械通过不等于语义准确 |
| M07真实修改及作用 | [M07差异](../experiments/scene_rsi_v3/candidates/C07/M.diff) / [动作源码](../experiments/scene_rsi_v3/candidates/C07/M/actions/appearance_audit.py) | [逐动作证据](../experiments/scene_rsi_v3/metrics/M07_action_review.csv) / [深入审查](../experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md) → [全部六次动作](../experiments/scene_rsi_v3/figures/M07_action_evidence.png) | meta.py未变；H04早于M07；H08拒绝、R9停止、H10拒绝，没有元能力增强证明 |
| 修正外部BW耗时覆盖 | [报告修订说明](../experiments/scene_rsi_v3/REPORT_ADAPTATION_FINAL_COMPLETION.md) | [耗时](../experiments/scene_rsi_v3/metrics/timing.csv) / [角色成本](../experiments/scene_rsi_v3/metrics/final_cost_by_role.csv) → [成本图](../experiments/scene_rsi_v3/figures/cost_and_timing.png) | 旧汇总漏读*_timing.json，旧表图保留；不叠加父子进程作用域，不把补日志解释成速度收益 |

归档只整理已存在产物，不调用模型/Blender、不补采样。实际执行H/M与冻结源码保留，整理版分析脚本单列。BW未获分发许可的原始参考及附件不公开；完整许可与上传状态见[附件索引](../artifacts_index_v3.csv)。
'''


def git(repo,*args):
    return ['git','-c','pack.threads=1','-C',str(repo),*args]


def commit(repo,paths,folder,name):
    required(git(repo,'add','--',*[str(path) for path in paths if (repo/path).exists()]),folder,name+'_add')
    changed = subprocess.run(git(repo,'diff','--cached','--quiet'),capture_output=True).returncode
    if changed==1:
        required(git(repo,'commit','-q','-m','Archive Scene-RSI V3 '+name),folder,name+'_commit')
    elif changed:
        raise RuntimeError('Cannot inspect staged Git changes')
    return subprocess.check_output(git(repo,'rev-parse','HEAD'),text=True).strip()


def mark_git_uploaded(index,core,tracked):
    """Called only after the push actually succeeded, never for planned uploads."""
    with index.open(newline='') as stream:
        reader = csv.DictReader(stream);fields,rows = reader.fieldnames,list(reader)
    for field in ['git_commit_url','git_file_url']:
        if field not in fields:fields.append(field)
    for row in rows:
        if row['git_status']=='included' and row['relative_path'] in tracked:
            row.update(git_status='git_uploaded',git_commit_url='https://github.com/i025/scene/commit/'+core,
                       git_file_url='https://github.com/i025/scene/blob/'+core+'/'+row['relative_path'])
            if row['upload_status']=='not_uploaded':
                row.update(upload_status='git_uploaded',download_url=row['git_file_url'],not_uploaded_reason='')
    with index.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def link_immutable_base_groups(index,base,new_groups):
    """The finisher never writes baseline/round groups; reuse their explicit run archives."""
    if base['remote_asset_listing_verified'] is not True:
        raise RuntimeError('Base Release has not completed its remote listing verification')
    assets={asset['name']:asset for asset in base['assets']}
    with index.open(newline='') as stream:
        reader=csv.DictReader(stream);fields,rows=reader.fieldnames,list(reader)
    fields.append('bundle_snapshot_tag')
    for row in rows:
        row['bundle_snapshot_tag']=''
        if row['archive_group'] not in new_groups and row['git_status']!='withheld_license':
            asset=assets[row['bundle_name']]
            row.update(upload_status='uploaded',download_url=asset['url'],not_uploaded_reason='',
                       bundle_snapshot_tag=base['tag'])
    with index.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def index_private_contact_sheet(index):
    path=WORK/'private_final_test_contact_sheet.png'
    with index.open(newline='') as stream:
        reader=csv.DictReader(stream);fields,rows=reader.fieldnames,list(reader)
    row={field:'' for field in fields}
    row.update(run_id='continuous_10',artifact_type='local_only_reference_contact_sheet',
               relative_path='local_only/private_final_test_contact_sheet.png',
               source_size_bytes=path.stat().st_size,file_size_bytes=path.stat().st_size,
               git_status='withheld_license',upload_status='not_uploaded',archive_group='local_private',
               not_uploaded_reason='Contains original BlenderWorld references; redistribution permission not confirmed; retained at server work/scene_v3_archive/private_final_test_contact_sheet.png')
    rows.append(row)
    with index.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def finalize(args):
    source,repo = args.source.resolve(),args.repo.resolve()
    snapshot = args.snapshot_id or datetime.now(timezone.utc).strftime('S%Y%m%dT%H%M%SZ')
    if not snapshot.replace('_','').replace('-','').isalnum():raise ValueError('Invalid snapshot ID')
    folder = WORK/'finalizations'/snapshot
    if args.resume_publication:
        if args.snapshot_id is None:raise ValueError('Publication resume needs an explicit snapshot ID')
        receipt = read(folder/'FINALIZATION.json')
        if receipt['status']!='pack_all_groups':raise ValueError('This resume entry only accepts a completed pack awaiting publication')
        bundles=Path(receipt['bundles'])
        packed=read(bundles/'PACK_RECEIPT.json')
        rows=[json.loads(line) for line in (folder/'pack_all_groups.stdout.log').read_text().splitlines()]
        expected=packed['new_groups'] if 'new_groups' in packed else packed['groups']
        if {row['group'] for row in rows}!=set(expected):raise ValueError('Pack log does not cover every planned new group')
        for row in rows:
            if Path(row['path']).parent!=bundles or Path(row['path']).stat().st_size!=row['bytes']:
                raise ValueError('Recorded archive path or byte size differs')
        if source_busy(source) or read(source/'state.json')!=packed['source_status']:
            raise RuntimeError('The live experiment changed or is active; do not mix it into this snapshot')
    else:
        folder.mkdir(parents=True,exist_ok=False)
    args.receipt_path = folder/'FINALIZATION.json'
    if not args.resume_publication:receipt = {'snapshot_id':snapshot,'source':str(source),'repo':str(repo),'launch':str(args.launch),
               'status':'waiting_launch','archive_model_calls':0,'archive_Blender_jobs':0,
               'replay_entry_requested':args.replay_entry is not None,'experiment_restarted':False,
               'cpu_affinity':sorted(os.sched_getaffinity(0)),'numeric_threads':1,
               'resume_command_not_executed':[sys.executable,str(source/'launch.py'),'resume']}
    def stage(status,**values):
        receipt.update(status=status,**values);write(args.receipt_path,receipt)
    if args.resume_publication:
        launch=receipt['launch_status']
        if not launch['terminal']:raise ValueError('Recorded experiment launch is not terminal')
        stage('publication_resumed_from_completed_pack',publication_resume=True)
    else:
        stage('waiting_launch')
        launch = wait_launch(args.launch.resolve(),source,args.wait,args.wait_hours)
        stage('launch_terminal',launch_status=launch)
    branch = subprocess.check_output(git(repo,'branch','--show-current'),text=True).strip()
    if branch!=BRANCH:raise ValueError('Refuse Git mutation on another branch')
    staged = subprocess.check_output(git(repo,'diff','--cached','--name-only','-z')).decode().split('\0')
    if any(path for path in staged):raise RuntimeError('Pre-existing staged changes must be reviewed; nothing was staged by this tool')
    if args.resume_publication:
        replay=receipt['replay'];data=facts(source);tag=receipt['tag']
    else:
        stage('optional_replay_preparation')
        replay = optional_replay(args.replay_entry,folder,source)
        stage('offline_report',replay=replay)
        required([sys.executable,str(source/'audit_m07.py')],folder,'offline_M07_review')
        required([sys.executable,str(source/'final_statistics.py'),'--private-output',str(WORK/'private_final_test_contact_sheet.png')],folder,'offline_final_statistics')
        required([sys.executable,str(source/'analyze.py'),'report'],folder,'offline_report')
        data = facts(source)
        write(source/'metrics/M_changed_content_execution_audit.json',data['M_changed_content_execution_audit'])
        stage('offline_report_completed',M_changed_content_execution_audit=data['M_changed_content_execution_audit'])
        tag = args.tag or 'scene-rsi-v3-10rounds-'+snapshot
        bundles = WORK/'bundles'/snapshot
        common = [sys.executable,str(WORK/'prepare_archive.py'),'--source',str(source),'--repo',str(repo),'--bundles',str(bundles),'--tag',tag]
        stage('prepare_core',tag=tag,bundles=str(bundles))
        required(common,folder,'prepare_core')
        index_private_contact_sheet(repo/'artifacts_index_v3.csv')
        derived=WORK/('offline_final_'+snapshot)
        required([sys.executable,str(WORK/'offline_v3.py'),'--experiment',str(repo/EXPERIMENT),'--output',str(derived)],folder,'offline_core_reproduction',timeout=1800)
        original_stats=read(source/'metrics/final_test_summary.json')
        derived_stats=read(derived/'experiment/metrics/final_test_summary.json')
        for key in ['records_finished','execution_success','BW_measured','endpoints','paired_differences']:
            if original_stats[key]!=derived_stats[key]:raise RuntimeError('Offline core reproduction changed final statistics: '+key)
        shutil.copy2(derived/'OFFLINE_RUN.json',repo/'docs'/('V3_OFFLINE_REPRODUCTION_'+snapshot+'.json'))
        stage('pack_all_groups')
        if args.base_release_state:
            if args.delta_groups!=['preparation','final']:
                raise ValueError('V3 completion changes only preparation and final archive groups')
            base=read(repo/args.base_release_state)
            link_immutable_base_groups(repo/'artifacts_index_v3.csv',base,args.delta_groups)
            for group in args.delta_groups:
                required(common+['--pack','--only-group',group],folder,'pack_'+group,timeout=7200)
            packed=read(bundles/'PACK_RECEIPT.json')
            packed.update(new_groups=args.delta_groups,reused_groups=[g for g in packed['groups'] if g not in args.delta_groups],
                          base_release_url=base['release_url'],base_release_tag=base['tag'],
                          reuse_basis='Explicit unchanged historical baseline/round run versions; finisher writes only new final/preparation/semantic outputs; no content fingerprints')
            write(bundles/'PACK_RECEIPT.json',packed)
            write(repo/'docs/V3_ARCHIVE_STATE.json',packed)
            (folder/'pack_all_groups.stdout.log').write_text(''.join((folder/('pack_'+g+'.stdout.log')).read_text() for g in args.delta_groups))
            stage('pack_all_groups',incremental_base_state=str(args.base_release_state),new_archive_groups=args.delta_groups)
        else:
            required(common+['--pack'],folder,'pack_all_groups',timeout=7200)
    publication = {'git':'not_pushed','release':'not_uploaded','verification':'not_run','release_url':None}
    if args.base_release_state:publication['base_release_url']=read(repo/args.base_release_state)['release_url']
    text = summary_text(data,launch,publication,None,replay)
    (repo/'README.md').write_text(replace_readme((repo/'README.md').read_text(),text))
    review = repo/'docs/V3_REVIEW_INDEX.md'
    old_review = Path('docs')/('V3_REVIEW_INDEX_PRE_FINALIZE_'+snapshot+'.md')
    if review.exists():shutil.copy2(review,repo/old_review)
    review.write_text(review_text())
    tools = repo/'docs/archive_tools_v3';tools.mkdir(parents=True,exist_ok=True)
    for name in ['prepare_archive.py','offline_v3.py','finalize.py','finish_after_test.py','publish.py','github_release_v3.py','verify_remote.py','apply_A02_after_baseline.py','COMMANDS.md']:
        shutil.copy2(WORK/name,tools/name)
    replay_tools=tools/'replay_stage';replay_tools.mkdir(exist_ok=True)
    for path in sorted((WORK/'replay_stage').iterdir()):
        if path.is_file() and (path.suffix in {'.py','.md'} or path.name=='EXECUTION_EVIDENCE_TESTS.json'):
            shutil.copy2(path,replay_tools/path.name)
    paths = [EXPERIMENT,Path('README.md'),Path('artifacts_index_v3.csv'),Path('docs/V3_ARCHIVE_STATE.json'),
             Path('docs/V3_REDACTIONS.json'),Path('docs/V3_REVIEW_INDEX.md'),old_review,Path('docs/archive_tools_v3')]
    if args.base_release_state:paths.append(args.base_release_state)
    if not args.resume_publication:paths.append(Path('docs')/('V3_OFFLINE_REPRODUCTION_'+snapshot+'.json'))
    stage('commit_core')
    core = commit(repo,paths,folder,'data_'+snapshot)
    text = summary_text(data,launch,publication,core,replay)
    (repo/'UPLOAD_SUMMARY_V3.md').write_text(text)
    latest = commit(repo,[Path('UPLOAD_SUMMARY_V3.md')],folder,'summary_'+snapshot)
    stage('local_committed',core_commit=core,latest_commit=latest,publication=publication)
    if args.publish:
        release_state = 'docs/V3_RELEASE_UPLOAD_STATE_'+snapshot+'.json'
        publisher = [sys.executable,str(WORK/'publish.py'),'--repo',str(repo),'--auth',args.auth,'--tag',tag,'--bundles',str(bundles),'--state',release_state]
        stage('push_core')
        push_ok = run(publisher+['push'],folder,'push_core')==0
        publication['git'] = 'core_and_summary_pushed' if push_ok else 'push_failed_local_commits_retained'
        if push_ok:
            tracked = set(subprocess.check_output(git(repo,'ls-tree','-r','--name-only',core),text=True).splitlines())
            mark_git_uploaded(repo/'artifacts_index_v3.csv',core,tracked)
            stage('release_upload')
            release_ok = run(publisher+['release'],folder,'release_upload',timeout=7200)==0
            publication['release'] = 'uploaded' if release_ok else 'upload_failed_or_partial'
            state_path = repo/release_state
            if state_path.exists():publication['release_url']=read(state_path)['release_url']
            (repo/'UPLOAD_SUMMARY_V3.md').write_text(summary_text(data,launch,publication,core,replay))
            latest = commit(repo,[Path('UPLOAD_SUMMARY_V3.md'),Path('artifacts_index_v3.csv'),Path(release_state)],folder,'publication_'+snapshot)
            stage('push_publication',latest_commit=latest)
            final_push_ok = run(publisher+['push'],folder,'push_publication')==0
            if final_push_ok:
                stage('verify_remote')
                if state_path.exists():
                    verify = [sys.executable,str(WORK/'verify_remote.py'),'--commit',latest,'--repo',str(repo),'--release-state',release_state]
                    verified = run(verify,folder,'verify_remote',timeout=900)==0
                    if verified and args.base_release_state:
                        shutil.copy2(WORK/'REMOTE_VERIFICATION.json',folder/'DELTA_REMOTE_VERIFICATION.json')
                        base_verify=[sys.executable,str(WORK/'verify_remote.py'),'--commit',latest,'--repo',str(repo),'--release-state',str(args.base_release_state)]
                        verified=run(base_verify,folder,'verify_base_release',timeout=1200)==0
                        shutil.copy2(WORK/'REMOTE_VERIFICATION.json',folder/'BASE_REMOTE_VERIFICATION.json')
                        delta_receipt=read(folder/'DELTA_REMOTE_VERIFICATION.json')
                        base_receipt=read(folder/'BASE_REMOTE_VERIFICATION.json')
                        write(WORK/'REMOTE_VERIFICATION.json',{'requested_commit':latest,'complete':verified,
                              'branch':BRANCH,'new_model_calls':0,'new_Blender_jobs':0,
                              'core_files':delta_receipt['core_files'],
                              'release_assets':delta_receipt['release_assets']+base_receipt['release_assets'],
                              'delta_receipt':str(folder/'DELTA_REMOTE_VERIFICATION.json'),
                              'base_receipt':str(folder/'BASE_REMOTE_VERIFICATION.json')})
                    publication['verification']='passed' if verified else 'failed_or_partial_readability'
                    if verified:publication['verified_commit']=latest
                    remote_receipt = WORK/'REMOTE_VERIFICATION.json'
                    if remote_receipt.exists() and read(remote_receipt)['requested_commit']==latest:
                        verification = Path('docs')/('V3_REMOTE_VERIFICATION_'+snapshot+'.json')
                        shutil.copy2(remote_receipt,repo/verification)
                    else:
                        verification = None
                        publication['verification']='failed_no_current_verification_receipt'
                else:
                    publication['verification']='not_run_no_release_receipt'
                    verification = None
                # Persist what was actually verified; this separate metadata commit
                # links the known data commit and never claims to verify itself.
                (repo/'UPLOAD_SUMMARY_V3.md').write_text(summary_text(data,launch,publication,core,replay))
                latest = commit(repo,[Path('UPLOAD_SUMMARY_V3.md')]+([verification] if verification else []),folder,'readability_'+snapshot)
                stage('push_readability_receipt',latest_commit=latest)
                if run(publisher+['push'],folder,'push_readability_receipt'):
                    publication['git']='data_pushed_readability_receipt_commit_local_only'
                else:
                    publication['git']='data_and_readability_receipt_pushed'
                    # One branch-head read confirms the receipt commit too. The
                    # full media read above remains bound to verified_commit.
                    head_code = run(publisher+['status'],folder,'verify_final_head',timeout=90)
                    remote = (folder/'verify_final_head.stdout.log').read_text().split()
                    publication['final_branch_head_verified']=head_code==0 and bool(remote) and remote[0]==latest
                    if not publication['final_branch_head_verified']:
                        publication['git']='data_pushed_final_head_unconfirmed'
            else:
                publication['git']='core_pushed_publication_metadata_push_failed'
        else:
            # Even upload failure must be represented in the local committed summary.
            (repo/'UPLOAD_SUMMARY_V3.md').write_text(summary_text(data,launch,publication,core,replay))
            latest = commit(repo,[Path('UPLOAD_SUMMARY_V3.md')],folder,'push_failure_'+snapshot)
        stage('publish_attempt_finished',latest_commit=latest,publication=publication)
    print(json.dumps({'receipt':str(folder/'FINALIZATION.json'),'core_commit':core,'latest_commit':latest,
                      'commit_url':'https://github.com/i025/scene/commit/'+latest,'publication':publication,
                      'archive_model_calls':0,'archive_Blender_jobs':0,'optional_replay':replay,
                      'joint_recorded_usage':data['joint_recorded_usage']},ensure_ascii=False))
    return 0 if not args.publish or (publication['release']=='uploaded' and publication['verification']=='passed' and publication['git']=='data_and_readability_receipt_pushed') else 1


def self_test():
    checks = []
    assert launch_classification({'status':'completed','pid':1,'returncode':0,'finished':2})['terminal']
    assert not launch_classification({'status':'running','pid':1})['terminal']
    assert not launch_classification({'status':'completed','pid':1,'returncode':None,'finished':2})['terminal']
    checks.append('Launch terminal requires actual exit/finished metadata, not running state')
    old = '# V3 prior snapshot\n\n# Scene-RSI V2.4：original\n\n原始数值与结论保持。\n'
    new = replace_readme(old,'\n'.join(['fixture']*15))
    assert new.endswith(old[old.index('\n# Scene-RSI V2.4：')+1:])
    checks.append('README V2.4 tail preserved exactly')
    with tempfile.TemporaryDirectory(dir=WORK) as tmp:
        source = Path(tmp)
        (source/'experiment.lock').touch();assert not source_busy(source)
        with (source/'experiment.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assert source_busy(source)
        checks.append('Existing experiment lock is observed without starting or stopping processes')
        entry = source/'entry.json'
        write(entry,{'status':'pending','eligibility':{'eligible':False,'reason':'fixture: no descendant'},
                     'budget':{'allowed':False,'reason':'not evaluated'}})
        assert replay_request(entry)['status']=='skipped_not_ready'
        write(entry,{'status':'ready','eligibility':{'eligible':False,'reason':'fixture'},
                     'budget':{'allowed':True,'reason':'fixture'}})
        assert replay_request(entry)['status']=='skipped_ineligible'
        checks.append('Replay eligibility comes from the entry; pending/ineligible do not execute')
        index=source/'index.csv'
        fields=['relative_path','git_status','upload_status','download_url','not_uploaded_reason']
        rows=[dict(zip(fields,['experiments/v3/a.csv','included','not_uploaded','','pending'])),
              dict(zip(fields,['experiments/v3/ref.png','withheld_license','not_uploaded','','license'])),
              dict(zip(fields,['experiments/v3/b.csv','included','not_uploaded','','pending']))]
        with index.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        mark_git_uploaded(index,'fixture_commit',{'experiments/v3/a.csv'})
        with index.open(newline='') as stream:uploaded=list(csv.DictReader(stream))
        assert uploaded[0]['git_status']=='git_uploaded' and uploaded[0]['git_commit_url'].endswith('fixture_commit')
        assert uploaded[1]['git_status']=='withheld_license' and uploaded[1]['upload_status']=='not_uploaded'
        assert uploaded[2]['git_status']=='included' and uploaded[2]['upload_status']=='not_uploaded'
        checks.append('Only confirmed pushed and tracked Git rows are marked; withheld/untracked stay unchanged')
        code=run([sys.executable,'-c',
            'import json,os;print(json.dumps({k:os.environ[k] for k in ["OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS","CUDA_VISIBLE_DEVICES"]}))'],
            source,'child_environment',timeout=5)
        environment=json.loads((source/'child_environment.stdout.log').read_text())
        assert code==0 and environment['CUDA_VISIBLE_DEVICES']==''
        assert all(environment[key]=='1' for key in environment if key!='CUDA_VISIBLE_DEVICES')
        code=run([sys.executable,'-c','import time;time.sleep(1)'],source,'bounded_fixture',timeout=.05)
        assert code==124 and read(source/'bounded_fixture.json')['status']=='timeout'
        checks.append('Archive child numeric threads/GPU exclusion and bounded owned-command timeout verified')
        (source/'render_attempts.jsonl').write_text('{"frames":2}\n')
        assert recorded_usage(source)['combined_render_budget_charged']==2
        stage=source/'meta_replay_stage';stage.mkdir()
        (source/'request.json').write_text('{}');(stage/'request.json').write_text('{}')
        assert recorded_usage(source)['combined_render_budget_charged'] is None
        (stage/'render_attempts.jsonl').write_text('{"frames":3}\n')
        usage=recorded_usage(source)
        assert usage['recorded_cli_sessions']==2 and usage['model_requests'] is None
        assert usage['combined_render_budget_charged']==5
        write(source/'state.json',{'H_start':'H0','meta_replay_status':'pending'})
        write(source/'config.json',{});write(source/'metrics/summary.json',{})
        write(source/'META_REPLAY_STATUS.json',{'status':'partial'})
        write(stage/'COMPLETION_RECEIPT.json',{'status':'completed'})
        actual=facts(source)
        assert actual['meta_replay_status']=='completed' and actual['historical_state_meta_replay_status']=='pending'
        checks.append('Main/replay costs counted once; missing counts stay null and actual replay receipt outranks historical state')
        m0=source/'code_snapshots/platform_frozen/initial_m';m0.mkdir(parents=True)
        (m0/'meta.py').write_text('def research(context, api):\n    return {"changes": []}\n')
        descendant=source/'candidates/C01/M';(descendant/'actions').mkdir(parents=True)
        (descendant/'meta.py').write_text((m0/'meta.py').read_text())
        (descendant/'actions/unused.py').write_text('def run(context):\n    return {}\n')
        later=source/'candidates/C02';later.mkdir()
        trace=source/'meta_traces/round02'
        write(later/'research_request.json',{'M_program':str(descendant),'trace_folder':str(trace)})
        write(later/'M_program_execution.json',{'program':str(descendant/'meta.py'),'status':'completed','loaded_M_helpers':[]})
        for t,parent,program,accepted,candidate in [(1,'M000',m0,True,'M01'),(2,'M01',descendant,False,None)]:
            write(source/'rounds'/f'{t:02d}'/'record.json',{'round':t,'M_parent':parent,'M_program_used':str(program/'meta.py'),
                  'M_accepted':accepted,'M_candidate':candidate,'H_accepted':False,'status':'completed',
                  'proposal_path':str(source/'candidates'/f'C{t:02d}'/'proposal.json')})
        actual=facts(source)
        assert actual['M_descendant_versions_as_later_parents']==['M01']
        assert actual['M_changed_content_execution_audit']['final_executed_descendant'] is None
        checks.append('Later M parent identity alone never becomes changed-content execution evidence')
    write(WORK/'FINALIZE_SELF_TEST.json',{'status':'passed','checks':checks,'fixture_only':True,
          'finalize_executed':False,'pack_executed':False,'Git_mutation':False,'new_model_calls':0,'new_Blender_jobs':0})
    print(json.dumps(checks,ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=PROJECT/'outputs/scene_rsi_v3')
    parser.add_argument('--repo',type=Path,default=PROJECT/'archive/scene')
    parser.add_argument('--launch',type=Path,default=PROJECT/'outputs/scene_rsi_v3/launches/006_resume.json')
    parser.add_argument('--wait',action='store_true');parser.add_argument('--wait-hours',type=float,default=36)
    parser.add_argument('--snapshot-id');parser.add_argument('--tag');parser.add_argument('--publish',action='store_true')
    parser.add_argument('--resume-publication',action='store_true',help='Reuse a recorded completed pack; no model, render, report or pack rerun')
    parser.add_argument('--base-release-state',type=Path,help='Completed base Release receipt for immutable baseline/round archives')
    parser.add_argument('--delta-groups',nargs='+',help='V3 final completion updates preparation and final only')
    parser.add_argument('--replay-entry',type=Path,help='Explicit root-reviewed Python entry; prepare checks real eligibility after main terminal')
    parser.add_argument('--auth',choices=['git','bashrc'],default='git');parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test();return 0
    approved = set(range(8))
    if not approved.issubset(os.sched_getaffinity(0)):
        raise RuntimeError('Authorized CPUs 0..7 are unavailable to this process; no archive or job was started')
    os.sched_setaffinity(0,approved)
    lock=(WORK/'finalization.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    args.receipt_path=None
    try:
        return finalize(args)
    finally:
        error=sys.exc_info()[1]
        if error is not None and args.receipt_path is not None:
            receipt=read(args.receipt_path)
            receipt.update(status='finalizer_failed',failed_stage=receipt['status'],
                           error_type=type(error).__name__,error=str(error),finished=time.time())
            write(args.receipt_path,receipt)


if __name__=='__main__':
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        os.environ[key]='1'
    os.environ['CUDA_VISIBLE_DEVICES']=''
    raise SystemExit(main())
