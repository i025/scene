"""Read-only V2.1 failure audit; no model invocation or Blender execution."""
import ast
from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'outputs/scene_rsi_v2_1'
DEST = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text())


def audit_record(path):
    record = load(path)
    folder = path.parent
    trajectory = folder / 'trajectory.jsonl'
    events = [json.loads(line) for line in trajectory.read_text().splitlines()]
    sessions = []
    for session_path in sorted(folder.glob('student_calls/*/session.json')):
        session = load(session_path)
        request_path = session_path.with_name('request.json')
        request = load(request_path) if request_path.exists() else None
        sessions.append({
            'path': str(session_path.relative_to(ROOT)),
            'status': session['status'], 'exit_code': session.get('exit_code'),
            'seconds': session['seconds'], 'error': session.get('error'),
            'requested_model': session['requested_model'],
            'actual_model': session.get('actual_model'),
            'reasoning_effort': session['reasoning_effort'],
            'thread_id': session.get('thread_id'),
            'started_unix': session.get('started'), 'finished_unix': session.get('finished'),
            'input_tokens': session['input_tokens'], 'output_tokens': session['output_tokens'],
            'request': request,
            'events_file': str(session_path.with_name('events.jsonl').relative_to(ROOT)),
        })
    executions = []
    for result_path in sorted(folder.glob('steps/*/result.json')):
        result = load(result_path)
        step = result_path.parent
        started = next(e['time'] for e in events if e['event'] == 'execute' and e['step'] == result['step'])
        ended = next(e['time'] for e in events if e['event'] == 'execution_result' and e['step'] == result['step'])
        code_path = step / 'build.py'
        code = code_path.read_text()
        syntax_valid = True
        syntax_error = None
        try:
            ast.parse(code)
        except SyntaxError as error:
            syntax_valid = False
            syntax_error = str(error)
        executions.append({
            'result_path': str(result_path.relative_to(ROOT)),
            'build_path': str(code_path.relative_to(ROOT)),
            'ok': result['ok'], 'error': result['error'],
            'started_unix': started, 'ended_unix': ended, 'wall_seconds': ended-started,
            'remaining_at_start_estimate': 600-(started-events[0]['time']),
            'stdout_bytes': (step/'stdout.log').stat().st_size,
            'stderr_bytes': (step/'stderr.log').stat().st_size,
            'blend_exists': (step/'scene.blend').exists(),
            'render_exists': (step/'final.png').exists(),
            'stage_telemetry_exists': (step/'stage_events.jsonl').exists(),
            'program_bytes': code_path.stat().st_size,
            'program_lines': len(code.splitlines()),
            'syntax_valid': syntax_valid, 'syntax_error': syntax_error,
        })
    valid = record['metrics']['valid']
    if valid:
        classification = None
        reason = 'Executable scene and measured visual metrics were saved.'
        phase = 'completed'
    elif any(s['status'] == 'failed' and 'TimeoutExpired' in str(s['error']) for s in sessions):
        classification = 'model_call_timeout'
        reason = 'Codex subprocess exceeded the 300-second model-call deadline; no build program was produced. Service-side cause is unobserved.'
        phase = 'model_call'
    elif executions and all('TimeoutExpired' in str(e['error']) for e in executions):
        classification = 'total_budget_exceeded'
        reason = 'The CLI completed. Blender subprocess timeout was capped by the scene deadline remainder; total recorded runtime was approximately 600 seconds. No pre/post-build telemetry exists. All failed steps lack scene.blend and final.png; because render.py saves before rendering, timeout appears pre-render, but startup/build/validation/device-setup/save cannot be separated.'
        phase = 'blender_pre_render_inferred_substage_unknown'
    else:
        classification = 'unknown'
        reason = 'Not enough logged evidence for a more specific classification.'
        phase = 'unknown'
    return {
        'experiment': 'scene_rsi_v2_1', 'method': record['method'],
        'run_id': record['run_id'], 'candidate_id': record['candidate_id'],
        'scene_id': record['scene_id'], 'split': record['split'],
        'original_status': record['status'], 'terminal': True, 'valid': valid,
        'original_failure_type': record.get('failure_type'),
        'audited_failure_type': classification,
        'observed_stage': phase, 'evidence_summary': reason,
        'seconds': record['seconds'], 'runtime_status': record['runtime_status'],
        'record_path': str(path.relative_to(ROOT)),
        'trajectory_path': str(trajectory.relative_to(ROOT)),
        'sessions': sessions, 'executions': executions,
        'model_wall_seconds': sum(s['seconds'] for s in sessions),
        'model_service_queue_seconds': None,
        'blender_wall_seconds': sum(e['wall_seconds'] for e in executions),
        'cli_session_count': len(sessions), 'execution_count': len(executions),
        'measured_Q': record['metrics']['overall'],
    }


def main():
    config = load(SOURCE/'config.json')
    rows = [audit_record(p) for p in sorted(SOURCE.glob('results/r*/**/record.json'))]
    counts = Counter(row['audited_failure_type'] or 'completed' for row in rows)
    by_split = {}
    by_candidate = {}
    for column, output in [('split', by_split), ('candidate_id', by_candidate)]:
        for value in sorted({row[column] for row in rows}):
            matching = [row for row in rows if row[column] == value]
            output[value] = {'recorded': len(matching), 'terminal': len(matching),
                             'succeeded': sum(row['valid'] for row in matching),
                             'failed': sum(not row['valid'] for row in matching)}
    result = {
        'source_root': str(SOURCE), 'scope': 'All formal reconstruction record.json files; smoke and supplemental mechanism cases excluded.',
        'counts': {'scheduled': config['pilot']['scheduled_main_reconstructions'], 'recorded': len(rows),
                   'terminal': len(rows), 'succeeded': sum(row['valid'] for row in rows),
                   'failed': sum(not row['valid'] for row in rows), 'not_started': 0,
                   'classification': dict(counts), 'by_split': by_split, 'by_candidate': by_candidate},
        'budgets': {'model_timeout_seconds': config['model']['timeout'],
                    'blender_configured_timeout_seconds': config['blender']['timeout'],
                    'scene_total_seconds': config['budget']['seconds'],
                    'model_calls_max_per_scene': config['budget']['model_calls'],
                    'executions_max_per_scene': config['budget']['executions'],
                    'outer_timeout_seconds': config['budget']['seconds']+10,
                    'effective_blender_timeout': 'min(configured Blender timeout, runtime.remaining()[seconds])',
                    'effective_model_timeout': 'min(configured model timeout, scene deadline remainder)',
                    'threads': config['render']['threads'], 'device': config['render']['device']},
        'budget_conclusion': 'No separate build/render reservation. A single Blender execution can consume all remaining scene time, leaving no repair opportunity despite unused model-call/execution units. This happened in ten failed scenes. Only one failed scene reached a model timeout. There is no evidence of model calls after a failed execution in these eleven failed formal records.',
        'uncertainties': ['Blender stdout/stderr were empty for all ten subprocess timeouts, with no stage telemetry. The absence of a pre-render saved blend suggests timeout before render, but does not identify startup versus generated build versus validation/device setup/save.',
                          'CLI elapsed time includes model/service waiting and generation. Queue time and server-side fault cause were not exposed.',
                          'Syntactically valid saved Python is not proof of executable geometry or appropriate complexity. No independent Blender replay was performed in this read-only sub-audit.',
                          'All scheduled Test records exist; no not-started Test was counted as a failure. Test failure measurements remain null.'],
        'rows': rows,
    }
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST/'v21_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    fields = ['experiment','method','run_id','candidate_id','scene_id','split','original_status','valid','original_failure_type','audited_failure_type','observed_stage','seconds','model_wall_seconds','model_service_queue_seconds','blender_wall_seconds','cli_session_count','execution_count','measured_Q','record_path','trajectory_path','evidence_summary']
    with (DEST/'v21_audit.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)
    text = '''# V2.1 只读失败审计

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
'''
    (DEST/'v21_audit.md').write_text(text)
    print(json.dumps(result['counts'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
