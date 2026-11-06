"""One-GPU, resumable seven-hour runner with optional resident metric models."""
import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

from data import ROOT, load_config, write_json

if __name__ == '__main__':
    sys.modules['gpu_watch'] = sys.modules[__name__]

MONITOR_HOURS = 7
POLL_INTERVAL_SECONDS = 120
REQUIRED_IDLE_CHECKS = 3


class WindowClosed(RuntimeError):
    pass


class StopRequested(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def results_dir(config):
    return Path(config.get('results_dir', ROOT / 'results')).resolve()


def event(run_dir, kind, **fields):
    with (run_dir / 'monitor.jsonl').open('a') as stream:
        stream.write(json.dumps({'time': now(), 'event': kind, **fields}, ensure_ascii=False) + '\n')


def state_update(run_dir, **fields):
    path = run_dir / 'monitor_state.json'
    state = json.loads(path.read_text()) if path.exists() else {}
    state.update(fields)
    state['updated_at'] = now()
    write_json(path, state)
    return state


def deadline_check(run_dir=None):
    stop_file = os.environ.get('SCENEEVOLVE_STOP_FILE')
    if stop_file and Path(stop_file).exists():
        raise StopRequested('STOP file requested a scene-boundary stop')
    deadline = os.environ.get('SCENEEVOLVE_DEADLINE')
    if deadline is not None and time.time() >= float(deadline):
        if run_dir is not None:
            state_update(run_dir, phase='window_expired', running_task=None)
        raise WindowClosed('Seven-hour window expired; resume from saved scene results')


def before_task(run_dir, phase, task):
    deadline_check(run_dir)
    state_update(run_dir, phase=phase, running_task=task, resume_position=task)
    refresh_report(run_dir)


def query_gpus():
    command = ['nvidia-smi', '--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu', '--format=csv,noheader,nounits']
    result = subprocess.run(command, text=True, capture_output=True, timeout=20)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    devices = []
    for fields in csv.reader(result.stdout.splitlines(), skipinitialspace=True):
        index, uuid, name, total, used, utilization = fields
        devices.append({'index': index, 'uuid': uuid, 'name': name,
                        'memory_total_mb': int(total), 'memory_used_mb': int(used),
                        'utilization_percent': int(utilization)})
    processes = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,process_name,used_memory',
                                '--format=csv,noheader,nounits'], text=True, capture_output=True, timeout=20)
    if processes.returncode:
        raise RuntimeError(processes.stderr.strip() or processes.stdout.strip())
    for device in devices:
        device['processes'] = [row for row in csv.reader(processes.stdout.splitlines(), skipinitialspace=True)
                               if row and row[0] == device['uuid']]
    return devices


def allocation():
    """Scheduler presence requires both a job allocation and explicit GPU visibility."""
    scheduler = next((name for name in ('srun', 'sbatch', 'qsub', 'bsub') if shutil.which(name)), None)
    job = os.environ.get('SLURM_JOB_ID') or os.environ.get('PBS_JOBID') or os.environ.get('LSB_JOBID')
    visible = (os.environ.get('SLURM_STEP_GPUS') or os.environ.get('SLURM_JOB_GPUS') or
               os.environ.get('SCENEEVOLVE_ALLOCATION_DEVICES', os.environ.get('CUDA_VISIBLE_DEVICES', '')))
    scheduler = scheduler or ('allocated_scheduler' if job else None)
    return scheduler, job, [v.strip() for v in visible.split(',') if v.strip()]


def eligible_devices(devices, selected):
    scheduler, job, visible = allocation()
    if scheduler and (not job or not visible):
        return [], f'Scheduler {scheduler} detected without an allocated visible GPU'
    allowed = []
    for device in devices:
        if 'A100' not in device['name'] or not 35000 <= device['memory_total_mb'] <= 45000:
            continue
        if selected and device['uuid'] != selected:
            continue
        if scheduler and not any(v == device['index'] or device['uuid'].startswith(v) for v in visible):
            continue
        allowed.append(device)
    return allowed, None


def gpu_samples(run_dir, config, restriction=None):
    try:
        devices = query_gpus()
        choices, reason = eligible_devices(devices, restriction)
        settings = config.get('gpu_watch', {})
        idle = [d for d in choices if not d['processes']
                and d['memory_used_mb'] <= settings.get('idle_memory_mb', 256)
                and d['utilization_percent'] <= settings.get('idle_utilization_percent', 0)]
        reason = reason or ('idle' if idle else 'GPU has active processes/memory/utilization' if choices
                            else 'No permitted A100 40GB visible')
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
        choices, reason, idle = [], str(error), []
    idle_uuids = {device['uuid'] for device in idle}
    entries = []
    for device in choices or [None]:
        is_idle = bool(device and device['uuid'] in idle_uuids)
        entries.append({'time': now(), 'uuid': device['uuid'] if device else restriction,
                        'memory_used_mb': device['memory_used_mb'] if device else None,
                        'utilization_percent': device['utilization_percent'] if device else None,
                        'process_count': len(device['processes']) if device else None,
                        'idle': is_idle, 'reason': 'idle' if is_idle else reason if not device
                        else 'GPU has active processes/memory/utilization'})
    destination = results_dir(config)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / 'gpu_usage.csv'
    new = not path.exists()
    with path.open('a', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(entries[0]))
        if new:
            writer.writeheader()
        writer.writerows(entries)
    for entry in entries:
        event(run_dir, 'gpu_check', **entry)
    return idle, reason


def wait_for_gpu(run_dir, config, task):
    if 'SCENEEVOLVE_DEADLINE' not in os.environ:
        raise RuntimeError('CUDA evaluation must run through gpu_watch.py with its saved monitoring deadline')
    from metric_worker import current_worker
    worker = current_worker()
    if worker is not None:
        while True:
            deadline_check(run_dir)
            if worker.process.poll() is not None:
                raise RuntimeError('Resident metric worker exited; its GPU cannot be reused silently')
            available, reason = reserved_gpu_status(run_dir, worker)
            if available:
                os.environ['CUDA_VISIBLE_DEVICES'] = worker.gpu_uuid
                state_update(run_dir, phase='gpu_ready', running_task=task, gpu_uuid=worker.gpu_uuid,
                             gpu_selection='reserved', waiting_reason=None)
                return worker.gpu_uuid
            state_update(run_dir, phase='waiting_reserved_gpu', running_task=None,
                         resume_position=task, waiting_reason=reason)
            refresh_report(run_dir)
            remaining = float(os.environ['SCENEEVOLVE_DEADLINE']) - time.time()
            time.sleep(max(0, min(POLL_INTERVAL_SECONDS, remaining)))
    # A previous binding is a recorded result, never a constraint for the next task.
    restriction = config.get('gpu_watch', {}).get('gpu_uuid')
    counts = {}
    while True:
        deadline_check(run_dir)
        idle, reason = gpu_samples(run_dir, config, restriction)
        counts = {device['uuid']: counts.get(device['uuid'], 0) + 1 for device in idle}
        ready = [device for device in idle if counts[device['uuid']] >= REQUIRED_IDLE_CHECKS]
        device = ready[0] if ready else max(idle, key=lambda d: counts[d['uuid']], default=None)
        selected = device['uuid'] if device else restriction
        consecutive = counts.get(selected, 0)
        waiting = f'Confirming idle GPU: {consecutive}/{REQUIRED_IDLE_CHECKS}' if idle else reason
        state_update(run_dir, phase='waiting_gpu', running_task=None, resume_position=task,
                     gpu_uuid=selected, gpu_selection='fixed' if restriction else 'any_idle',
                     idle_checks=consecutive, idle_checks_by_gpu=counts, waiting_reason=waiting)
        refresh_report(run_dir)
        if ready:
            # Bind exactly one physical card by UUID; each scorer exits at its scene boundary.
            os.environ['CUDA_VISIBLE_DEVICES'] = selected
            state_update(run_dir, phase='gpu_ready', running_task=task, waiting_reason=None)
            event(run_dir, 'gpu_ready', gpu_uuid=selected, task=task)
            return selected
        remaining = float(os.environ['SCENEEVOLVE_DEADLINE']) - time.time()
        time.sleep(max(0, min(POLL_INTERVAL_SECONDS, remaining)))


def reserved_gpu_status(run_dir, worker):
    try:
        devices, reason = eligible_devices(query_gpus(), worker.gpu_uuid)
        device = devices[0] if devices else None
        others = [row for row in device['processes'] if int(row[1]) != worker.pid] if device else []
        available = bool(device) and not others
        reason = reason or ('held by resident metric worker' if available else
                            'Another process appeared on the retained GPU' if device else 'Retained GPU is unavailable')
        event(run_dir, 'gpu_reservation_check', gpu_uuid=worker.gpu_uuid, worker_pid=worker.pid,
              memory_used_mb=device['memory_used_mb'] if device else None,
              other_processes=others, ready=available, reason=reason)
        return available, reason
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
        event(run_dir, 'gpu_reservation_check', gpu_uuid=worker.gpu_uuid, ready=False, reason=str(error))
        return False, str(error)


def scene_boundary(run_dir, config):
    state_update(run_dir, running_task=None)
    if config['metrics']['device'].startswith('cuda'):
        from metric_worker import current_worker
        worker = current_worker()
        if worker is not None:
            reserved_gpu_status(run_dir, worker)
        else:
            state = json.loads((run_dir / 'monitor_state.json').read_text())
            gpu_samples(run_dir, config, state.get('gpu_uuid'))
    refresh_report(run_dir)


def _known_sum(rows, key):
    values = [r.get('usage', {}).get(key) for r in rows]
    return sum(values) if values and all(isinstance(v, (int, float)) for v in values) else None


def _display(value):
    if value is None:
        return 'unknown'
    return f'{value:.6f}' if isinstance(value, float) else str(value)


def refresh_report(run_dir):
    """Regenerate only actual measurements; unfinished scenes remain absent."""
    config_path = run_dir / 'config.yaml'
    if not config_path.exists():
        return
    config = load_config(config_path)
    destination = results_dir(config)
    destination.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / 'monitor_state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    resume_position = state.get('resume_position') or (
        '已完成，无待执行任务' if state.get('phase') == 'complete' else 'baseline/search/scene_001')
    summaries = []
    for path in sorted((run_dir / 'results').glob('*/*.json')):
        summary = json.loads(path.read_text())
        experiment = path.parent.name
        valid_psnr = [row['psnr'] for row in summary['scenes'] if row.get('valid') and 'psnr' in row
                      and (row['psnr'] is None or isinstance(row['psnr'], (int, float)))]
        # The scorer stores a perfect image's infinite PSNR as null in JSON.
        psnr_mean = ('infinity' if any(value is None for value in valid_psnr)
                     else sum(valid_psnr) / len(valid_psnr) if valid_psnr else None)
        role = {'final_baseline': 'Baseline', 'final_best': 'Best'}.get(
            experiment, 'Baseline' if summary['agent'] == 'baseline' else 'Candidate')
        summaries.append({**summary, 'experiment': experiment, 'evaluation_role': role,
                          'psnr_valid_mean': psnr_mean, 'psnr_valid_count': len(valid_psnr)})
    scene_rows = []
    for path in sorted((ROOT / 'jobs' / run_dir.name).glob('*/*/metrics.json')):
        row = json.loads(path.read_text())
        scene_rows.append({**row, 'experiment': path.parent.parent.name})
    session_paths = list((ROOT / 'jobs' / run_dir.name).glob('*/*/student_calls/*/session.json'))
    session_paths += list((run_dir / 'proposals').glob('*/teacher_call*/session.json'))
    sessions = [json.loads(path.read_text()) for path in sorted(session_paths)]
    call_columns = ['role', 'requested_model', 'actual_model', 'actual_model_source', 'status', 'reasoning_effort', 'started', 'finished',
                    'seconds', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'total_tokens',
                    'cost_usd', 'exit_code', 'error', 'call_dir']
    with (destination / 'calls.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=call_columns)
        writer.writeheader()
        for session in sessions:
            writer.writerow({key: _display(session.get(key)) for key in call_columns})
    columns = ['experiment', 'candidate', 'split', 'id', 'valid', 'ssim', 'lpips', 'dino', 'psnr', 'overall',
               'seconds', 'scoring_seconds', 'calls', 'input_tokens', 'output_tokens', 'total_tokens',
               'executions', 'generation_error', 'output_dir']
    with (destination / 'scenes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in scene_rows:
            writer.writerow({key: _display(row.get('usage', {}).get(key) if key in
                ('calls', 'input_tokens', 'output_tokens', 'total_tokens', 'executions') else row.get(key)) for key in columns})
    shutil.copyfile(destination / 'scenes.csv', destination / 'metrics.csv')
    write_json(destination / 'metrics.json', {'scenes': scene_rows, 'summaries': summaries})
    columns = ['experiment', 'evaluation_role', 'agent', 'split', 'count', 'overall', 'valid_rate',
               'ssim', 'lpips', 'dino', 'psnr_valid_mean', 'psnr_valid_count', 'scene_seconds',
               'scoring_seconds', 'calls', 'input_tokens', 'output_tokens', 'total_tokens']
    with (destination / 'candidates.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for summary in summaries:
            writer.writerow({key: _display(summary.get('usage', {}).get(key) if key in
                ('calls', 'input_tokens', 'output_tokens', 'total_tokens') else summary.get(key)) for key in columns})
    history_path = run_dir / 'history.json'
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    selections = [json.loads(p.read_text()) for p in sorted((run_dir / 'proposals').glob('*/selection.json'))]
    proposal_rows = []
    search_count = sum(row['split'] == 'search' for row in json.loads((run_dir / 'splits.json').read_text()))
    for workspace in sorted((run_dir / 'proposals').glob('*')):
        if not workspace.is_dir() or not workspace.name.isdigit():
            continue
        prepared_path, committed_path = workspace / 'prepared.json', workspace / 'proposals.json'
        prepared = json.loads(prepared_path.read_text()) if prepared_path.exists() else {}
        names = list(prepared.get('candidates', []))
        if committed_path.exists():
            names.extend(json.loads(committed_path.read_text()))
        names.extend(path.parent.name for path in workspace.glob('*/lineage.json')
                     if '_interrupted_' not in path.parent.name)
        selection = next((row for row in selections if row['round'] == int(workspace.name)), None)
        for name in dict.fromkeys(names):
            lineage_path = run_dir / 'candidates' / name / 'lineage.json'
            if not lineage_path.exists():
                lineage_path = workspace / name / 'lineage.json'
            lineage = json.loads(lineage_path.read_text()) if lineage_path.exists() else prepared
            completed = next((row for row in summaries if row['experiment'] == name and row['split'] == 'search'), None)
            scored_count = sum(row['experiment'] == name and row['split'] == 'search' for row in scene_rows)
            if completed:
                status = '开发集评价完成' if selection else '开发集评价完成，待保留决策'
            elif (run_dir / 'candidates' / name).exists():
                status = '已提交，开发集评价未完成'
            elif prepared_path.exists():
                status = '已生成，待提交/评价'
            else:
                status = '提案中，尚未提交'
            proposal_rows.append({'round': int(workspace.name), 'candidate': name,
                                  'parent': lineage.get('parent', 'unknown'), 'status': status,
                                  'scored_scenes': scored_count, 'expected_scenes': search_count,
                                  'overall': completed['overall'] if completed else None,
                                  'retained': selection['retained'] == name if selection else None})
    write_json(destination / 'evolution_history.json', {
        'evaluations': history, 'selections': selections, 'proposals': proposal_rows})
    final_path = run_dir / 'finalized.json'
    final = json.loads(final_path.read_text()) if final_path.exists() else None
    best_path = run_dir / 'frontier_search.json'
    best = json.loads(best_path.read_text()) if best_path.exists() else None
    baseline = next((row for row in summaries if row['experiment'] == 'baseline' and row['split'] == 'search'), None)
    development_delta = best['overall'] - baseline['overall'] if best and baseline else None
    monitor_end = datetime.fromisoformat(state['ended_at']).timestamp() if state.get('ended_at') else time.time()
    monitor_elapsed = monitor_end - state['started_epoch'] if state.get('started_epoch') is not None else None
    generations = [json.loads(path.read_text()) for path in
                   sorted((ROOT / 'jobs' / run_dir.name).glob('*/*/generation_complete.json'))]
    generation_seconds = (sum(row['seconds'] for row in generations) if generations and
                          all(isinstance(row.get('seconds'), (int, float)) for row in generations) else None)
    scoring_seconds = (sum(row['scoring_seconds'] for row in scene_rows) if scene_rows and
                       all(isinstance(row.get('scoring_seconds'), (int, float)) for row in scene_rows) else None)
    notes_path = destination / 'environment_notes.md'
    notes = notes_path.read_text() if notes_path.exists() else '环境准备详情见 local_resources.md 和 environment.json（若已生成）。'
    lines = ['# SceneEvolve 小规模复现实际报告', '', f'自动更新时间（UTC）：{now()}', '',
             f"运行目录：`{run_dir}`", f"阶段：**{state.get('phase', 'prepared')}**；已评分场景：{len(scene_rows)}；完整候选/测试评价：{len(summaries)}。", '',
             '## 环境、数据与模型', '', notes, '',
             f"Student：`{config['model'].get('name', config['model'].get('model', 'unknown'))}`，推理强度 `{config['model'].get('reasoning_effort', 'unknown')}`。",
             f"Proposer：`{config['proposer'].get('model', 'unknown')}`，推理强度 `{config['proposer'].get('reasoning_effort', 'unknown')}`。", '',
             '[数据来源与划分](dataset.md)；[本地模型资源与加载验证](local_resources.md)；[环境静态记录](environment_notes.md)。', '',
             '所有远程语言模型调用通过 Codex CLI；登录用量没有可比 API 美元费用，成本记为 unknown。CLI 将角色提示和历史序列化为输入，不能视作论文裸 Chat Completions 调用的等价实现。', '',
             f"预算：每场景 {config['budget']['model_calls']} 次模型调用、{config['budget']['executions']} 次 Blender 执行、{config['budget']['seconds']} 秒。渲染为 {config['render']['engine']} / {config['render']['samples']} samples / CPU，最多 4 线程；正式指标设备 `{config['metrics']['device']}`。", '',
             '## GPU 监控与恢复', '',
             f"启动（UTC）：{state.get('started_at', '尚未启动')}；截止：{state.get('deadline_at', '尚未启动')}；结束：{state.get('ended_at') or '尚未结束'}。",
             f"北京时间：启动 {state.get('started_at_shanghai', '尚未启动')}；截止 {state.get('deadline_at_shanghai', '尚未启动')}。",
             f"监控 PID：{state.get('pid', 'unknown')}；GPU 选择：{state.get('gpu_selection', 'unknown')}；候选或最近绑定 UUID：{state.get('gpu_uuid') or '尚未选择'}。",
             f"等待原因：{state.get('waiting_reason') or '无'}；恢复位置：`{resume_position}`。", '',
             f"本监控窗口已过 {_display(monitor_elapsed)} 秒（含 GPU 等待、生成和评分；尚在运行时统计至报告更新时间）。恢复和停止命令见 [resume.md](resume.md)。", '',
             ('初次选择采用逐 UUID 连续 3 次空闲检测，间隔 120 秒。按用户后续要求，选中后将评价模型常驻同一张卡，生成、进化和测试期间保留显存；只在完成、停止、失败或七小时窗口结束后释放。每次评分前检查同卡其他进程，发现其他作业则暂停评分，保持本项目模型常驻。此方式不是调度器独占分配。'
              if config.get('gpu_watch', {}).get('retain_gpu') else
              '监控采用连续 3 次空闲检测，间隔 120 秒；每次 GPU 评价前重新检查，场景结束释放模型进程。七小时截止后不启动新任务，已启动任务按原预算保存。'), '',
             f"常驻评价进程 PID：{state.get('gpu_worker_pid') or '尚未启动或已释放'}；保留状态：{state.get('gpu_reservation', 'unknown')}。", '',
             '## 开发集与独立测试实际结果', '',
             '| 实验 / 角色 | Harness | split | N | Q ↑ | SSIM ↑ | LPIPS ↓ | DINOv2 ↑ | PSNR dB ↑（有效 N） | 有效率 |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for summary in summaries:
        values = [f"{summary['experiment']} / {summary['evaluation_role']}",
                  *[_display(summary[key]) for key in ('agent', 'split', 'count', 'overall', 'ssim', 'lpips', 'dino')],
                  f"{_display(summary['psnr_valid_mean'])} (N={summary['psnr_valid_count']})", _display(summary['valid_rate'])]
        lines.append('| ' + ' | '.join(values) + ' |')
    if not summaries:
        lines.append('| 尚无完整评价 | unknown | unknown | 0 | unknown | unknown | unknown | unknown | unknown (N=0) | unknown |')
    lines += ['', 'Q = mean([clip(SSIM,0,1) + 1 − clip(LPIPS,0,1) + (1 + clip(DINOv2,−1,1))/2] / 3)。只按开发集 Q 严格改善保留子代；测试集在两轮搜索结束并冻结 Harness 后独立执行。', '',
              'search 为开发集，final_test 为独立测试集。PSNR 均值只包含有效渲染，括号 N 为其实际测量数；无有效测量为 unknown，infinity 表示与参考图完全相同。无渲染时的 PSNR=0 惩罚占位不参与 PSNR 均值。', '',
              f"当前开发集最佳：{best['agent'] if best else '尚无'}；开发集 Q 差值（Best − Baseline）：{_display(development_delta)}；独立测试状态：{final['status'] if final else '尚未启动'}。"]
    if final and final.get('status') == 'complete':
        lines.append(f"独立测试 Q 差值（Best − Baseline）：{_display(final['overall_delta'])}。")
    lines += ['', '## 候选谱系与保留决策', '', '| 轮次 | 父代 | 子代 | Q | 保留 | 状态 |', '|---:|---|---|---:|---|---|']
    for row in history:
        lineage = run_dir / 'candidates' / row['agent'] / 'lineage.json'
        parent = json.loads(lineage.read_text()).get('parent', 'baseline') if lineage.exists() else '—'
        decision_path = run_dir / 'proposals' / f"{row['iteration']:04d}" / 'selection.json'
        decision = json.loads(decision_path.read_text()) if decision_path.exists() else {}
        kept = 'initial' if not row['iteration'] else ('yes' if decision.get('retained') == row['agent'] else 'no' if decision else 'pending')
        lines.append(f"| {row['iteration']} | {parent} | {row['agent']} | {_display(row['overall'])} | {kept} | 开发集评价完成 |")
    archived = {row['agent'] for row in history}
    pending_proposals = [row for row in proposal_rows if row['candidate'] not in archived]
    for row in pending_proposals:
        kept = 'pending' if row['retained'] is None else 'yes' if row['retained'] else 'no'
        lines.append(f"| {row['round']} | {row['parent']} | {row['candidate']} | {_display(row['overall'])} | {kept} | {row['status']}；已评分 {row['scored_scenes']}/{row['expected_scenes']} |")
    lines += ['', '以下为教师提案时的原始说明；“not evaluated / no evaluation was run”等表述指提案阶段，后续实际评价见上表。']
    for path in sorted((run_dir / 'proposals').glob('*/modifications.json')):
        modifications = json.loads(path.read_text())
        lines += ['', f'### 第 {int(path.parent.name)} 轮教师修改', '']
        for change in modifications.get('changes', []):
            lines.append(f"- `{change['candidate']}/{change['path']}`：{change['rationale']}")
    if history:
        lines += ['', '```mermaid', 'graph TD', '  baseline[Baseline]']
        for row in history:
            if row['iteration']:
                lineage_path = run_dir / 'candidates' / row['agent'] / 'lineage.json'
                parent = json.loads(lineage_path.read_text()).get('parent', 'baseline') if lineage_path.exists() else 'baseline'
                lines.append(f"  {parent} --> {row['agent']}[\"Round {row['iteration']}: Q={row['overall']:.4f}\"]")
        for row in pending_proposals:
            lines.append(f"  {row['parent']} --> {row['candidate']}[\"Round {row['round']}: {row['status']} ({row['scored_scenes']}/{row['expected_scenes']})\"]")
        lines += ['```']
        plot_history(run_dir, destination, history)
        lines += ['', '![开发集候选实际 Q](development_curve.png)']
    for summary in summaries:
        sheets = run_dir / 'evidence' / summary['agent'] / 'sheets.json'
        if summary['split'] == 'search' and sheets.exists():
            for path in json.loads(sheets.read_text()):
                lines += ['', f"![{summary['agent']} 开发集参考与重建]({path})"]
    if final and final.get('status') == 'complete':
        test_comparison(run_dir, destination)
        lines += ['', '![独立测试参考、Baseline 与 Best](test_comparison.png)']
    lines += ['', '## Token、耗时与失败记录', '',
              f"实验累计已保存的完整生成阶段：{len(generations)} 个，耗时 {_display(generation_seconds)} 秒；已保存评分：{len(scene_rows)} 个，耗时 {_display(scoring_seconds)} 秒。生成耗时包含 Student 调用及 CPU Blender 执行；评分耗时独立统计，GPU 等待不并入这两项。未完成阶段的耗时不估计。", '',
              f"已保存正式实验调用（含失败和未评分场景）：{len(sessions)}，其中 Student {sum(s.get('role') == 'student' for s in sessions)}、Teacher {sum(s.get('role') == 'teacher' for s in sessions)}；输入 Token：{_display(_known_sum([{'usage': s} for s in sessions], 'input_tokens'))}；输出 Token：{_display(_known_sum([{'usage': s} for s in sessions], 'output_tokens'))}；总 Token：{_display(_known_sum([{'usage': s} for s in sessions], 'total_tokens'))}。费用：unknown。", '',
              '每次正式调用的角色、请求/实际模型、推理强度、Token、耗时、退出状态和日志路径见 calls.csv；准备阶段的 smoke 调用独立保存在 work/codex_smoke，不混入正式实验。', '',
              '逐场景指标、PSNR、有效状态、耗时、调用量和路径见 scenes.csv；完整候选均值见 candidates.csv；初次空闲轮询见 gpu_usage.csv，后续常驻检查、完成与释放见 gpu_monitor.log（原始monitor.jsonl）。教师调用的逐次 JSON、事件、耗时和修改说明保存在 proposals/<round>/ 下。', '']
    lines += ['| 实验 / 角色 | N | 生成秒 / 场景 | 评分秒 / 场景 | Student 调用数 | 输入 Token | 输出 Token | 总 Token |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for summary in summaries:
        generation_per_scene = summary['scene_seconds'] / summary['count'] if isinstance(summary.get('scene_seconds'), (int, float)) else None
        scoring_per_scene = summary['scoring_seconds'] / summary['count'] if isinstance(summary.get('scoring_seconds'), (int, float)) else None
        values = [f"{summary['experiment']} / {summary['evaluation_role']}", _display(summary['count']),
                  _display(generation_per_scene), _display(scoring_per_scene),
                  *[_display(summary.get('usage', {}).get(key)) for key in
                    ('calls', 'input_tokens', 'output_tokens', 'total_tokens')]]
        lines.append('| ' + ' | '.join(values) + ' |')
    lines.append('')
    for row in scene_rows:
        if row.get('generation_error') or not row.get('valid'):
            lines.append(f"- {row['experiment']} / {row['split']} / {row['id']}：{row.get('generation_error') or row.get('error') or 'invalid'}")
            failures = []
            for path in sorted((Path(row['output_dir']) / 'steps').glob('*/result.json')):
                result = json.loads(path.read_text())
                if not result['ok']:
                    detail = ('执行超时（约600秒）' if 'TimeoutExpired' in (result.get('error') or '')
                              else (result.get('stderr') or result.get('error') or '执行失败')
                              .replace('\\n', '\n').strip().splitlines()[-1])
                    failures.append(f"第{int(path.parent.name)}次：{detail}")
            if failures:
                lines.append('  执行记录：' + '；'.join(failures) + '。无有效渲染，SSIM=0、LPIPS=1、DINOv2=-1、Q=0为官方失败惩罚，不是图像实测值。')
    for session in sessions:
        if session.get('error') or session.get('exit_code', 0):
            lines.append(f"- {session.get('role')} CLI：{session.get('error') or 'exit ' + str(session.get('exit_code'))}；日志 `{session.get('call_dir', 'unknown')}`")
    if state.get('error'):
        lines += ['', f"监控错误：`{state['error']}`。"]
    completion = (f"本次完成 Baseline、{len(selections)}轮各2子代、按开发集Q严格择优及2张独立测试图上的Baseline/Best比较，共{len(scene_rows)}次场景评价；其中{sum(not row.get('valid') for row in scene_rows)}次无有效渲染，已按失败规则计分。没有待执行的实验任务。"
                  if final and final.get('status') == 'complete' else
                  f"目前已完成{len(scene_rows)}次场景评价；未完成的场景、候选或测试不计入均值，也不填充推测数值。恢复位置见上文。")
    lines += ['', '## 局限与完成范围', '', completion, '',
              '小数据量、模型及数据集替换、Codex CLI调用语义差异使本结果不能与论文数值直接比较。CLI未独立报告后端模型名，actual_model由成功的--model选择推断，来源已在calls.csv中标注。每个场景只运行一次；开发集提升包含减少执行失败的贡献，不能据此分离各项Harness改动的因果效果，也不构成统计显著性结论。', '',
              '渲染、.blend、生成程序、轨迹和每次调用事件保留在 jobs/<run>/<experiment>/scene_NNN；候选代码及父子关系保留在 logs/<run>/candidates。', '']
    report = '\n'.join(lines)
    (destination / 'final_report.md').write_text(report)
    (run_dir / 'report.md').write_text(report)
    (destination / 'run_status.md').write_text('\n'.join([
        '# SceneEvolve 运行状态', '', f'更新时间：{now()}', f"阶段：{state.get('phase', 'prepared')}",
        f"已评分场景：{len(scene_rows)}", f"完整评价：{len(summaries)}", f"GPU：{state.get('gpu_uuid') or '未选择'}",
        f"恢复位置：{resume_position}", f"GPU保留状态：{state.get('gpu_reservation', 'unknown')}", f"等待原因：{state.get('waiting_reason') or '无'}", '']))


def plot_history(run_dir, destination, history):
    cache = ROOT.parent / 'work' / 'matplotlib'
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(figsize=(8, 4))
    x = list(range(len(history)))
    scores = [row['overall'] for row in history]
    retained = []
    best = scores[0]
    for index, row in enumerate(history):
        selection = run_dir / 'proposals' / f"{row['iteration']:04d}" / 'selection.json'
        round_end = index + 1 == len(history) or history[index + 1]['iteration'] != row['iteration']
        if row['iteration'] and round_end and selection.exists():
            decision = json.loads(selection.read_text())
            best = max(decision['parent_q'], *decision['candidates'].values())
        retained.append(best)
    axes.plot(x, scores, 'o-', label='Evaluated candidate Q')
    axes.step(x, retained, where='post', label='Retained best Q')
    axes.set_xticks(x, ['Baseline' if row['iteration'] == 0 else f"R{row['iteration']} C{1 + sum(r['iteration'] == row['iteration'] for r in history[:i])}"
                        for i, row in enumerate(history)], rotation=20)
    axes.set_ylabel('Development Q')
    axes.set_xlabel('Completed candidate evaluation')
    axes.legend()
    axes.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(destination / 'development_curve.png', dpi=160)
    plt.close(figure)


def test_comparison(run_dir, destination):
    from PIL import Image, ImageDraw, ImageOps
    baseline = json.loads((run_dir / 'results' / 'final_baseline' / 'final_test.json').read_text())
    best = json.loads((run_dir / 'results' / 'final_best' / 'final_test.json').read_text())
    size, label_height = 256, 42
    sheet = Image.new('RGB', (3 * size, len(baseline['scenes']) * (size + label_height)), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, (a, b) in enumerate(zip(baseline['scenes'], best['scenes'])):
        y = index * (size + label_height)
        for column, (label, path) in enumerate([('Reference', a['reference']),
                (f"Baseline Q={a['overall']:.4f}", a.get('render')),
                (f"Best Q={b['overall']:.4f}", b.get('render'))]):
            draw.text((column * size + 5, y + 5), f'Test {index + 1}: {label}', fill='black')
            if path and Path(path).exists():
                with Image.open(path) as image:
                    thumb = ImageOps.contain(image.convert('RGB'), (size, size))
                    sheet.paste(thumb, (column * size + (size - thumb.width) // 2, y + label_height + (size - thumb.height) // 2))
            else:
                draw.text((column * size + 36, y + label_height + size // 2),
                          'Failed: no valid render\nQ=0 failure penalty', fill='darkred')
    sheet.save(destination / 'test_comparison.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=str(ROOT / 'config-mini.yaml'))
    parser.add_argument('--run-name', default='mini_reproduction')
    parser.add_argument('--gpu-uuid', help='Only this permitted A100 40GB UUID may be used')
    parser.add_argument('--new-window', action='store_true',
                        help='Explicitly renew an expired monitoring window; retain all previous window records')
    args = parser.parse_args()
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        os.environ[key] = '4'
    os.nice(10)
    from benchmark import open_run
    from sceneharness import search, finalize
    from metric_worker import start_worker, current_worker, close_worker
    run_dir, config = open_run(args.run_name, args.config)
    if args.gpu_uuid:
        config.setdefault('gpu_watch', {})['gpu_uuid'] = args.gpu_uuid
    previous_path = run_dir / 'monitor_state.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    if args.new_window and previous:
        history_path = run_dir / 'window_history.json'
        history = json.loads(history_path.read_text()) if history_path.exists() else []
        history.append(previous)
        write_json(history_path, history)
    started = time.time() if args.new_window else previous.get('started_epoch', time.time())
    deadline = started + MONITOR_HOURS * 3600
    os.environ['SCENEEVOLVE_DEADLINE'] = str(deadline)
    os.environ['SCENEEVOLVE_ALLOCATION_DEVICES'] = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    os.environ['SCENEEVOLVE_STOP_FILE'] = str(results_dir(config) / 'STOP')
    def stop_signal(signum, frame):
        raise StopRequested(f'Monitor received signal {signum}; project process groups are being stopped')
    signal.signal(signal.SIGTERM, stop_signal)
    signal.signal(signal.SIGINT, stop_signal)
    (run_dir / 'monitor.pid').write_text(str(os.getpid()) + '\n')
    state_update(run_dir, started_epoch=started, started_at=datetime.fromtimestamp(started, timezone.utc).isoformat(),
                 deadline_at=datetime.fromtimestamp(deadline, timezone.utc).isoformat(),
                 started_at_shanghai=datetime.fromtimestamp(started, ZoneInfo('Asia/Shanghai')).isoformat(),
                 deadline_at_shanghai=datetime.fromtimestamp(deadline, ZoneInfo('Asia/Shanghai')).isoformat(), pid=os.getpid(),
                 gpu_uuid=config.get('gpu_watch', {}).get('gpu_uuid'),
                 gpu_selection='fixed' if config.get('gpu_watch', {}).get('gpu_uuid') else 'any_idle',
                 idle_checks=0, idle_checks_by_gpu={}, gpu_worker_pid=None,
                 gpu_reservation='not_acquired', phase='starting', error=None, ended_at=None)
    event(run_dir, 'monitor_start', pid=os.getpid(), deadline=deadline, resumed=bool(previous), new_window=args.new_window)
    refresh_report(run_dir)
    try:
        uuid = wait_for_gpu(run_dir, config, previous.get('resume_position') or 'baseline/search/scene_001')
        smoke = results_dir(config) / 'metric_smoke'
        if config.get('gpu_watch', {}).get('retain_gpu', False):
            before_task(run_dir, 'metric_model_smoke', 'resident_metrics/load_and_hold')
            worker = start_worker(run_dir / 'config.yaml', run_dir / 'resident_metrics', uuid)
            state_update(run_dir, gpu_worker_pid=worker.pid, gpu_selection='reserved', gpu_reservation='loading')
            rows = json.loads((run_dir / 'splits.json').read_text())
            reference = next(row['image'] for row in rows if row['split'] == 'search')
            result = worker.request('check_models', reference, timeout=config['metrics']['timeout'])
            smoke.mkdir(parents=True, exist_ok=True)
            write_json(smoke / 'resident_model_load_test.json', {**result, 'gpu_uuid': uuid, 'worker_pid': worker.pid})
            state_update(run_dir, gpu_reservation='held')
            event(run_dir, 'gpu_reserved', gpu_uuid=uuid, worker_pid=worker.pid, result=result)
            scene_boundary(run_dir, config)
        elif not (smoke / 'model_load_test.json').exists():
            before_task(run_dir, 'metric_model_smoke', 'metric_models/load_and_forward')
            smoke.mkdir(parents=True, exist_ok=True)
            rows = json.loads((run_dir / 'splits.json').read_text())
            reference = next(row['image'] for row in rows if row['split'] == 'search')
            from processes import cpu_environment, run_group
            with (smoke / 'stdout.log').open('w') as stdout, (smoke / 'stderr.log').open('w') as stderr:
                result = run_group([sys.executable, str(ROOT / 'evaluate.py'), '--config', str(run_dir / 'config.yaml'),
                                    '--image', reference, '--output-dir', str(smoke), '--check-models'],
                                   timeout=config['metrics']['timeout'], cwd=ROOT, stdout=stdout, stderr=stderr,
                                   env=cpu_environment(cuda_visible=os.environ['CUDA_VISIBLE_DEVICES']))
            if result:
                raise RuntimeError(f"Metric smoke failed: {smoke / 'stderr.log'}")
            event(run_dir, 'metric_smoke_complete', result=json.loads((smoke / 'model_load_test.json').read_text()))
            scene_boundary(run_dir, config)
        if not (run_dir / 'finalized.json').exists():
            search(run_dir, config)
        finalize(run_dir, config)
        state_update(run_dir, phase='complete', running_task=None, ended_at=now(), resume_position=None)
        event(run_dir, 'experiment_complete')
    except StopRequested as error:
        state_update(run_dir, phase='stopped', running_task=None, ended_at=now(), waiting_reason=str(error))
        event(run_dir, 'stopped', reason=str(error))
    except WindowClosed as error:
        state_update(run_dir, phase='window_expired', running_task=None, ended_at=now(), waiting_reason=str(error))
        event(run_dir, 'window_expired')
    except Exception as error:
        state_update(run_dir, phase='failed', error=repr(error), running_task=None, ended_at=now())
        event(run_dir, 'experiment_error', error=repr(error))
        raise
    finally:
        worker = current_worker()
        if worker is not None:
            uuid, pid = worker.gpu_uuid, worker.pid
            close_worker()
            state_update(run_dir, gpu_reservation='released', gpu_worker_pid=None)
            event(run_dir, 'gpu_released', gpu_uuid=uuid, worker_pid=pid)
        refresh_report(run_dir)


if __name__ == '__main__':
    main()
