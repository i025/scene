"""Build the offline human-review report from saved records; no model calls."""
import csv
import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'backend'))
from budget import current


STATUS = {
    'not_started': '尚未开始', 'running': '运行中（状态文件记录）',
    'completed': '已完成', 'failed': '失败', 'timeout': '超时',
    'invalid': '无效', 'interrupted': '中断', 'paused': '暂停', 'blocked': '受阻，未运行',
    'visual_loop_incomplete': '实际看图闭环未完成',
    'advance': '进入下一阶段', 'revise': '请求局部修订',
    'advance_with_issue': '保留未解决问题并继续',
}
ACTION = {
    'initial': '本阶段初建', 'build': '本阶段建模',
    'stage_build': '本阶段建模', 'visual_revision': '视觉纠错',
    'revision': '局部修订', 'technical_repair': '程序错误修复',
    'repair': '程序错误修复', 'final_render': '最终交付渲染',
}


def read(path):
    return json.loads(path.read_text())


def esc(value):
    return html.escape(str(value))


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def csv_write(path, rows, fields):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            values = {}
            for key in fields:
                value = row.get(key)
                values[key] = ('null' if value is None else
                               json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value)
            writer.writerow(values)


def relative(path):
    path = Path(path)
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def file_link(path, label):
    return f'<a href="../{esc(relative(path))}" target="_blank">{esc(label)}</a>'


def raw_record(path, title):
    if not path.exists():
        return f'<p class="muted">{esc(title)}：尚未产生记录。</p>'
    return (f'<details><summary>{esc(title)}（英文原文／实际记录）</summary>'
            f'{file_link(path, "打开原始文件")}<pre>{esc(path.read_text())}</pre></details>')


def picture(path, caption, absent='未生成图像；没有用其他阶段的结果补位。'):
    if not path or not (ROOT / path).is_file():
        content = f'<div class="missing">{esc(absent)}</div>'
    else:
        url = '../' + relative(path)
        content = f'<a href="{esc(url)}" target="_blank"><img src="{esc(url)}" loading="lazy" alt="{esc(caption)}"></a>'
    return f'<figure><figcaption>{esc(caption)}</figcaption>{content}</figure>'


def findings_panel(record, heading):
    if record is None:
        return f'<h4>{heading}</h4><p class="muted">尚无实际看图反馈记录。</p>'
    decision = record['decision']
    rows = []
    for finding in record['findings']:
        fields = [('id', '发现编号'), ('target', '对象或关系'),
                  ('problem_source', '问题来源'), ('rule_source', '规则来源'),
                  ('reference_evidence', '参考图证据'), ('render_evidence', '实际渲染证据'),
                  ('proposed_change', '建议修改'), ('preserve', '需要保持'),
                  ('check_after', '修改后检查'), ('uncertainty', '不确定性'), ('status', '记录状态')]
        rows.append('<dl>' + ''.join(f'<dt>{label}</dt><dd>{esc(finding[key])}</dd>'
                                    for key, label in fields if key in finding) + '</dl>')
    if not rows:
        rows.append('<p>该次反馈没有提出问题；不补造问题。</p>')
    return (f'<h4>{heading}：{esc(STATUS.get(decision, decision))}</h4>'
            '<details><summary>展开发现、证据和决定（英文原文）</summary>'
            f'<p>{esc(record["summary"])}</p>{"".join(rows)}</details>')


def collect_calls():
    calls = []
    for base in ('tasks', 'transfer', 'preparation'):
        for path in sorted((ROOT / base).glob('**/request.json')):
            session_path = path.with_name('session.json')
            request = read(path)
            session = read(session_path) if session_path.exists() else {}
            parts = path.relative_to(ROOT).parts
            task_id = parts[1] if parts[0] == 'tasks' else None
            stage_id = parts[parts.index('stages') + 1] if 'stages' in parts else None
            calls.append({**request, **session,
                          'path': relative(path.parent), 'task_id': task_id,
                          'stage_id': stage_id, 'attempt': path.parent.name,
                          'status': session.get('status', 'unknown'),
                          'image_attachments': len(request['original_images_for_audit'])})
    return calls


def collect_stages(folder):
    stages = []
    for path in sorted((folder / 'stages').glob('*/stage.json')):
        stage = read(path)
        recorded = {attempt['patch'] for attempt in stage['attempts']}
        additional = []
        for result_path in path.parent.glob('*/result.json'):
            result = read(result_path)
            if result['patch'] not in recorded:
                additional.append((read(result_path.with_name('build_request.json'))['time'], result))
        stage['attempts'] += [result for _, result in sorted(additional, key=lambda item: item[0])]
        stage['report_recovered_attempts'] = len(additional)
        stages.append(stage)
    return stages


def call_panel(calls):
    lines = []
    for call in calls:
        path = ROOT / call['path']
        lines.append(f'<li>{esc(call["role"])} · 请求 {esc(call["requested_model"])} · '
                     f'观测路由 {esc(call.get("observed_model", "unknown"))} · '
                     f'{esc(STATUS.get(call["status"], call["status"]))} · '
                     f'{esc(call.get("seconds", "unknown"))} 秒 · 实际附件 {call["image_attachments"]} 张<br>'
                     + ' · '.join(file_link(path / name, label) for name, label in [
                         ('prompt.txt', '提示'), ('response.txt', '回复'),
                         ('request.json', '真实附件引用'), ('session.json', '调用与用量'),
                         ('events.jsonl', '原始事件'), ('stderr.log', '错误记录')]
                         if (path / name).exists()) + '</li>')
    return '<details><summary>实际模型调用与输入图片</summary><ul>' + ''.join(lines) + '</ul></details>'


def contact_sheet(task_id, source, stages, figures):
    panels = [(source['image_path'], task_id + ' / REF', 'source')]
    for stage in stages:
        for number, attempt in enumerate(stage['attempts'], 1):
            panels.append((attempt.get('render'), f'{task_id} / {stage["stage_id"]} / {number}', attempt['status']))
    delivery = f'tasks/{task_id}/delivery/final.png'
    panels.append((delivery, task_id + ' / FINAL',
                   'delivery' if (ROOT / delivery).exists() else 'not_delivered'))
    columns = min(3, len(panels))
    sheet = Image.new('RGB', (columns * 440, ((len(panels) + columns - 1) // columns) * 330), '#f4f5f7')
    draw = ImageDraw.Draw(sheet)
    for index, (path, title, status) in enumerate(panels):
        x, y = index % columns * 440, index // columns * 330
        draw.text((x + 12, y + 10), title + ' | ' + status, fill='#202a35')
        if path and (ROOT / path).is_file():
            with Image.open(ROOT / path) as source_image:
                image = ImageOps.contain(source_image.convert('RGB'), (420, 286))
            sheet.paste(image, (x + (440 - image.width) // 2, y + 35 + (286 - image.height) // 2))
        else:
            draw.rectangle((x + 10, y + 35, x + 430, y + 320), fill='#e9e9e9')
            draw.text((x + 20, y + 140), 'No render: ' + status, fill='#803030')
    sheet.save(figures / f'{task_id}_contact.png')
    save_json(figures / f'{task_id}_contact_sources.json', [
        {'image': path, 'label': label, 'status': status} for path, label, status in panels])


def stage_panel(task_id, stage, calls, presentation):
    folder = ROOT / 'tasks' / task_id / 'stages' / str(stage['stage_id']).zfill(2)
    stage_calls = [call for call in calls if call['task_id'] == task_id
                   and call['stage_id'] == folder.name]
    chinese = presentation.get(f'{task_id}/{stage["stage_id"]}', '')
    lines = [f'<article><h3>阶段 {esc(stage["stage_id"])} · '
             f'{esc(STATUS.get(stage["status"], stage["status"]))}</h3>']
    if stage['status'] != stage['raw_status']:
        lines.append(f'<p class="notice">阶段原文件状态为 {esc(stage["raw_status"])}；'
                     f'根据已停止的任务／整体状态，页面显示为 {esc(STATUS[stage["status"]])}。'
                     '这是展示层状态推导，没有修改阶段原始记录，也不表示后台仍在执行。</p>')
    lines.append('<p>本阶段来源：' + file_link(folder / 'stage.json', '阶段原始 JSON')
                 + ' · ' + file_link(ROOT / 'metrics/steps.csv', '步骤与失败 CSV') + '</p>')
    if chinese:
        lines.append(f'<p class="translation">中文展示摘要：{esc(chinese)}</p>')
    if stage['report_recovered_attempts']:
        lines.append(f'<p class="notice">阶段汇总尚未登记的构建记录 {stage["report_recovered_attempts"]} 条已从实际 result.json 列出；'
                     '没有据此补写已完成反馈或改变阶段状态。</p>')
    lines.append('<details><summary>阶段计划：目标与已完成范围（英文原文）</summary>'
                 f'<p>{esc(stage["title"])}</p><p>目标：{esc(stage["targets"])}</p>'
                 f'<p>完成范围：{esc(stage["completed_scope"])}</p></details>')
    lines.append('<div class="images">' + picture(stage['initial_render'], '本阶段首次有效结果') + '</div>')
    lines.append(findings_panel(stage['review'], '教师纠错' if task_id == 'D01' else '学生实际自查'))
    revision = stage['student_revision']
    if revision is not None:
        lines.append('<details><summary>学生修改决定与建议落实情况（英文原文）</summary>'
                     f'<pre>{esc(json.dumps(revision, ensure_ascii=False, indent=2))}</pre></details>')
    else:
        lines.append('<p class="muted">没有已保存的视觉修订响应；不等同于已修好。</p>')
    same = stage['initial_render'] is not None and stage['initial_render'] == stage['final_render']
    lines.append('<div class="images">' + picture(stage['final_render'],
                 '本阶段保留结果（复用首次结果）' if same else '本阶段修订后／最后保留结果') + '</div>')
    lines.append(findings_panel(stage['confirmation'], '教师复核' if task_id == 'D01' else '学生修订后复查'))
    lines.append('<details><summary>全部增量构建、错误和真实代码 diff</summary>')
    lines.append('<p>对象变化表只测量已记录的字段，不是完整的非目标保持证明。未覆盖的项目包括部分修改器参数、'
                 'ColorRamp 内部值、UV、灯光尺寸及着色设置等；请同时检查真实补丁与渲染。'
                 '失败 inventory 中的 patch_running 是未完成快照，实际执行状态以 result.json 和 build_process.json 为准。</p>')
    for number, attempt in enumerate(stage['attempts'], 1):
        action = attempt['action_type']
        lines.append(f'<h4>尝试 {number} · {esc(ACTION.get(action, action))} · '
                     f'{esc(STATUS.get(attempt["status"], attempt["status"]))}</h4>'
                     f'<p>父检查点：{esc(attempt["parent_checkpoint"])}<br>'
                     f'本次检查点：{esc(attempt["checkpoint"])}<br>'
                     f'失败类型：{esc(attempt["failure_type"])}</p>')
        lines.append(picture(attempt.get('render'), f'阶段 {stage["stage_id"]}／尝试 {number}',
                             '本次没有有效渲染；程序错误与视觉问题分开记录。'))
        for key, label in [('patch', '实际增量补丁'), ('inventory', '真实对象与变化记录'),
                           ('checkpoint', '本次 .blend')]:
            if attempt[key] and (ROOT / attempt[key]).exists():
                lines.append(file_link(attempt[key], label) + ' · ')
        if attempt['patch']:
            attempt_folder = (ROOT / attempt['patch']).parent
            for filename, label in [('result.json', '构建与渲染结果'), ('build_process.json', '构建进程证据'),
                                    ('render_settings.json', '本次真实渲染配置')]:
                if (attempt_folder / filename).exists():
                    lines.append(file_link(attempt_folder / filename, label) + ' · ')
            diff = attempt_folder / 'patch.diff'
            lines.append(raw_record(diff, '代码 diff'))
        lines.append('<pre>' + esc(json.dumps(attempt, ensure_ascii=False, indent=2)) + '</pre>')
    lines.append('</details>' + call_panel(stage_calls))
    lines.append(f'<label>可选人工意见：<select data-key="{task_id}/{stage["stage_id"]}">'
                 '<option value="">尚未判断</option><option>修正有帮助</option><option>无帮助</option>'
                 '<option>变差</option><option>无法判断</option></select></label>'
                 f'<textarea data-key="{task_id}/{stage["stage_id"]}" placeholder="可选备注；未填写不代表任何结论"></textarea></article>')
    return ''.join(lines)


def generate():
    generated_at = datetime.now(timezone.utc).isoformat()
    manifest = read(ROOT / 'manifest.json')
    config = read(ROOT / 'config.json')
    reports, metrics, figures = [ROOT / name for name in ('reports', 'metrics', 'figures')]
    for path in (reports, metrics, figures):
        path.mkdir(exist_ok=True)
    presentation_path = ROOT / 'presentation_zh.json'
    presentation = read(presentation_path) if presentation_path.exists() else {}
    overall_path = ROOT / 'state.json'
    overall = read(overall_path) if overall_path.exists() else {'status': 'not_started'}
    calls = collect_calls()
    csv_write(metrics / 'cli_calls.csv', calls, [
        'path', 'task_id', 'stage_id', 'role', 'requested_model', 'observed_model',
        'reasoning_effort', 'status', 'started', 'finished', 'seconds',
        'original_images_for_audit', 'image_attachments', 'input_tokens', 'output_tokens',
        'cached_input_tokens', 'observable_cli_turns', 'tool_calls', 'observable_tool_counts',
        'observable_model_requests_lower_bound', 'exact_model_requests', 'cost_usd'])
    costs = []
    for role in sorted({call['role'] for call in calls}):
        selected = [call for call in calls if call['role'] == role]
        measured_seconds = [call['seconds'] for call in selected if call.get('seconds') is not None]
        costs.append({'role': role, 'sessions': len(selected),
                      'statuses': dict(Counter(call['status'] for call in selected)),
                      'wall_seconds_sum': sum(measured_seconds) if measured_seconds else None,
                      'time_measured_sessions': len(measured_seconds),
                      'known_input_tokens': sum(call['input_tokens'] for call in selected if isinstance(call.get('input_tokens'), int)),
                      'known_output_tokens': sum(call['output_tokens'] for call in selected if isinstance(call.get('output_tokens'), int)),
                      'usage_unknown_sessions': sum(not isinstance(call.get('input_tokens'), int) for call in selected),
                      'exact_model_requests': None, 'cost_usd': None})
    csv_write(metrics / 'cost_by_role.csv', costs, ['role', 'sessions', 'statuses', 'wall_seconds_sum', 'time_measured_sessions',
              'known_input_tokens', 'known_output_tokens', 'usage_unknown_sessions', 'exact_model_requests', 'cost_usd'])
    timing = [{**read(path), 'path': relative(path)} for base in ('tasks', 'transfer', 'preparation')
              for path in sorted((ROOT / base).glob('**/*process.json'))]
    csv_write(metrics / 'timing.csv', timing, ['path', 'status', 'started', 'finished', 'seconds',
              'cpu_user_seconds', 'cpu_system_seconds', 'peak_individual_rss_kib',
              'sampled_peak_tree_rss_kib_lower_bound', 'timed_out', 'memory_limit_exceeded'])
    steps, tasks, stage_rows, task_html = [], [], [], {}
    for source in manifest:
        task_id = source['id']
        folder = ROOT / 'tasks' / task_id
        state_path = folder / 'state.json'
        state = read(state_path) if state_path.exists() else {'status': 'not_started'}
        display_status = state['status']
        if display_status == 'running' and overall['status'] in {'blocked', 'interrupted', 'failed', 'paused'}:
            display_status = 'blocked' if overall['status'] == 'blocked' else 'interrupted'
        plan_path = folder / 'plan.json'
        planned_stages = read(plan_path)['stages'] if plan_path.exists() else None
        stages = collect_stages(folder)
        for stage in stages:
            stage['raw_status'] = stage['status']
            if stage['status'] == 'running' and display_status in {'blocked', 'interrupted', 'failed', 'paused'}:
                stage['status'] = 'blocked' if display_status == 'blocked' else 'interrupted'
            stage_rows.append({'task_id': task_id, 'split': source['split'], 'stage_id': stage['stage_id'],
                               'raw_status': stage['raw_status'], 'status': stage['status'],
                               'task_raw_status': state['status'], 'overall_status': overall['status'],
                               'initial_render': stage['initial_render'], 'retained_render': stage['final_render'],
                               'retained_checkpoint': stage['final_checkpoint'],
                               'review_recorded': stage['review'] is not None,
                               'confirmation_recorded': stage['confirmation'] is not None})
        task_calls = [call for call in calls if call['task_id'] == task_id]
        teacher_calls = [call for call in task_calls if 'teacher' in call['role'].lower()
                         or 'astra' in call['requested_model'].lower()]
        attempts = [attempt for stage in stages for attempt in stage['attempts']]
        latest = next((stage for stage in reversed(stages)
                       if stage['final_checkpoint'] and stage['final_render']
                       and (ROOT / stage['final_checkpoint']).exists() and (ROOT / stage['final_render']).exists()), None)
        row = {'task_id': task_id, 'split': source['split'], 'status': display_status, 'raw_status': state['status'],
               'planned_stages': len(planned_stages) if planned_stages is not None else None,
               'recorded_stages': len(stages),
               'processed_stages': sum(stage['status'] in {'completed', 'advance_with_issue'} for stage in stages),
               'no_remaining_issue_stages': sum(stage['status'] == 'completed' for stage in stages),
               'advanced_with_issue_stages': sum(stage['status'] == 'advance_with_issue' for stage in stages),
               'build_attempts': len(attempts), 'failed_build_attempts': sum(not attempt['ok'] for attempt in attempts),
               'cli_sessions': len(task_calls), 'teacher_or_astra_calls': len(teacher_calls),
               'active_seconds': state.get('active_seconds'),
               'final_render_exists': (folder / 'delivery/final.png').exists(),
               'final_blend_exists': (folder / 'delivery/scene.blend').exists(),
               'latest_successful_checkpoint': latest['final_checkpoint'] if latest else None,
               'latest_successful_render': latest['final_render'] if latest else None}
        tasks.append(row)
        for stage in stages:
            for number, attempt in enumerate(stage['attempts'], 1):
                steps.append({**attempt, 'record_type': 'build', 'task_id': task_id,
                              'split': source['split'], 'stage_id': stage['stage_id'],
                              'raw_status': attempt['status'],
                              'attempt': number, 'cli_calls': 0,
                              'actual_input_images': None, 'build_context_images': attempt['images'],
                              'output_path': attempt['checkpoint']})
        for call in task_calls:
            steps.append({'record_type': 'cli', 'task_id': task_id, 'split': source['split'],
                          'stage_id': call['stage_id'], 'attempt': call['attempt'],
                          'role': call['role'], 'action_type': 'cli_session',
                          'actual_input_images': call['original_images_for_audit'],
                          'status': call['status'], 'raw_status': call['status'], 'cli_calls': 1, 'seconds': call.get('seconds'),
                          'output_path': call['path'], 'started': call.get('started')})
        contact_sheet(task_id, source, stages, figures)
        label = '开发：教师在线纠错' if source['split'] == 'development' else '测试：学生自主检查'
        content = [f'<section id="{task_id}"><h2>{"A" if source["split"] == "development" else "C"}．{task_id} · {label}</h2>',
                   f'<p>任务状态：<strong>{esc(STATUS.get(display_status, display_status))}</strong>；'
                   f'已记录阶段 {len(stages)}；已处理阶段 {row["processed_stages"]}，其中保留问题继续 {row["advanced_with_issue_stages"]}。</p>',
                   '<p>已处理包含“保留问题继续”，不表示没有剩余问题；流程完成也不表示视觉质量通过。</p>']
        if source['split'] == 'test':
            content.append(f'<p class="notice">本任务已记录教师／Astra 调用数：<strong>{len(teacher_calls)}</strong>。'
                           + ('发现协议违规调用，不能声称教师退出。' if teacher_calls else
                              '此数来自实际调用记录；任务尚未完成时只代表当前记录。') + '</p>')
        content.append('<div class="images">' + picture(source['image_path'], '参考原图') + '</div>')
        content.append('<p>原图曾在历史实验和人工交流中暴露；本次任务隔离不等于全新盲测。'
                       f'来源：<a href="{esc(source["source_page"])}">{esc(source["author"])}</a> · '
                       f'<a href="{esc(source["license_url"])}">{esc(source["license"])}</a>。</p>')
        content.append(raw_record(folder / 'plan.json', '学生制定的阶段计划'))
        if not stages:
            content.append('<p class="missing">尚无实际阶段结果。没有自动生成示意图或补写完成状态。</p>')
        content.extend(stage_panel(task_id, stage, calls, presentation) for stage in stages)
        if planned_stages is not None:
            started_ids = {stage['stage_id'] for stage in stages}
            for planned in planned_stages:
                if planned['stage_id'] not in started_ids:
                    content.append(f'<article><h3>阶段 {planned["stage_id"]} · 尚未开始</h3>'
                                   '<div class="missing">没有本阶段构建或渲染，不以其他阶段补位。</div>'
                                   '<details><summary>已保存的阶段计划（英文原文）</summary>'
                                   f'<pre>{esc(json.dumps(planned, ensure_ascii=False, indent=2))}</pre></details></article>')
        content.append('<h3>最终交付</h3><div class="images">' + picture(source['image_path'], '参考原图')
                       + picture(f'tasks/{task_id}/delivery/final.png', '最终交付渲染') + '</div>')
        if row['final_blend_exists']:
            content.append(file_link(folder / 'delivery/scene.blend', '下载可打开的最终 .blend'))
        if not row['final_render_exists'] and latest is not None:
            content.append('<h3>最近成功检查点：尚非最终交付</h3>'
                           '<p class="notice">以下仅是中断前已保存、已渲染的场景。不代表尚未执行的纠错、复核或最终交付已经完成。</p>'
                           '<div class="images">' + picture(latest['final_render'], f'阶段 {latest["stage_id"]} 的最近成功检查点（非最终图）')
                           + '</div>' + file_link(latest['final_checkpoint'], '下载最近成功检查点 .blend（非最终交付）'))
        content.append(raw_record(folder / 'delivery/final.json', '最终交付事实'))
        content.append(raw_record(folder / 'delivery/render_settings.json', '最终交付的实际渲染配置'))
        content.append('<p>最终图由保留的同一场景另外渲染；交付 .blend 保留检查点，内存储的预览设置不自动等同于最终图设置。'
                       '最终分辨率与采样数以本节 render_settings.json 为准。</p>')
        content.append(raw_record(state_path, '任务状态原始记录'))
        content.append(file_link(figures / f'{task_id}_contact.png', '全部阶段联系图') + ' · ' +
                       file_link(figures / f'{task_id}_contact_sources.json', '联系图来源清单') + '</section>')
        task_html[task_id] = ''.join(content)
    csv_write(metrics / 'steps.csv', steps, ['record_type', 'task_id', 'split', 'stage_id', 'attempt',
              'parent_checkpoint', 'role', 'action_type', 'targets', 'actual_input_images', 'build_context_images', 'status', 'raw_status',
              'failure_type', 'checkpoint', 'render', 'patch', 'inventory', 'output_path', 'cli_calls', 'seconds', 'started'])
    csv_write(metrics / 'tasks.csv', tasks, list(tasks[0]))
    csv_write(metrics / 'stages.csv', stage_rows, ['task_id', 'split', 'stage_id', 'raw_status', 'status',
              'task_raw_status', 'overall_status', 'initial_render', 'retained_render', 'retained_checkpoint',
              'review_recorded', 'confirmation_recorded'])
    save_json(metrics / 'tasks.json', tasks)
    summary = {'generated_at': generated_at, 'overall_status': overall['status'], 'tasks': tasks, 'calls': len(calls), 'cost_by_role': costs, 'budget': current(),
               'automatic_quality_evaluation': False, 'human_quality_verdict': None,
               'source_images': len(manifest), 'language_model_context': 'English', 'presentation_language': 'Chinese',
               'test_teacher_or_astra_calls': sum(task['teacher_or_astra_calls'] for task in tasks if task['split'] == 'test'),
               'process_cpu_user_seconds': sum(item.get('cpu_user_seconds') or 0 for item in timing),
               'process_cpu_system_seconds': sum(item.get('cpu_system_seconds') or 0 for item in timing),
               'cpu_measured_process_count': sum(item.get('cpu_user_seconds') is not None for item in timing),
               'process_count': len(timing)}
    save_json(metrics / 'summary.json', summary)
    transfer = ROOT / 'transfer'
    transfer_html = ['<section id="transfer"><h2>B．教学经验怎样进入学生</h2>',
                     '<p>下列文件只在实际产生后展示。通用策略来自开发轨迹；测试中发现的问题必须另有测试原图与当前渲染证据。'
                     '这是检查策略提炼，不是模型权重训练、教师自进化或已证实的能力提升。</p>']
    if (transfer / 'freeze.json').exists():
        transfer_html.append('<p class="notice">已知执行边界：冻结规则 R6 要求保留未解决问题，但运行器只在同一阶段的复核中传入 previous_findings；'
                             '后续阶段首次自查收到的该字段为空。实际图像仍随场景保留，但没有结构化的跨阶段未解决问题记忆。'
                             '因此不能把规则文本中的要求写成已经实现的跨阶段问题追踪能力。</p>')
    if 'transfer' in presentation:
        transfer_html.append(f'<p class="translation">中文展示摘要：{esc(presentation["transfer"])}</p>')
    for filename, label in [('self_check_policy.md', '实际共享自检查规则'),
                            ('lesson_provenance.json', '逐条规则的开发来源、实际修复与适用限制'),
                            ('student_self_review.py', '实际执行的学生检查入口'),
                            ('student_self_review.diff', '共享流程补丁'),
                            ('freeze.json', '首次测试前的冻结记录'),
                            ('extraction.json', '提炼调用原始输出')]:
        transfer_html.append(raw_record(transfer / filename, label))
    transfer_html.append(call_panel([call for call in calls if call['path'].startswith('transfer/')]) + '</section>')
    cost_table = '<table><tr><th>实际角色</th><th>会话</th><th>已测累计调用秒</th><th>已有耗时的会话</th><th>已知输入 token</th><th>已知输出 token</th><th>usage 缺失会话</th></tr>'
    for cost in costs:
        cost_table += '<tr>' + ''.join(f'<td>{esc(cost[key]) if cost[key] is not None else "未知"}</td>' for key in [
            'role', 'sessions', 'wall_seconds_sum', 'time_measured_sessions', 'known_input_tokens', 'known_output_tokens', 'usage_unknown_sessions']) + '</tr>'
    cost_table += '</table>'
    evidence = '<section><h2>技术状态、成本与原始证据</h2>' + cost_table
    evidence += ('<p>两张原图是两个场景任务；阶段、补丁、渲染和模型会话都不是独立场景样本。'
                 '累计调用耗时包括远端等待，不等于模型纯计算时间，也不等于整轮总墙钟。'
                 '已知 token 只累加真实 usage；缺失值另列。底层精确请求数、实际路由和费用没有证据时保持 unknown/null。</p>')
    evidence += '<p>' + ' · '.join(file_link(metrics / name, label) for name, label in [
        ('steps.csv', '逐步骤与失败'), ('tasks.csv', '任务状态'), ('stages.csv', '阶段原始与展示状态'), ('cli_calls.csv', '调用与真实附件'),
        ('cost_by_role.csv', '分角色成本'), ('timing.csv', '进程树耗时与资源'), ('summary.json', '汇总原始数据')]) + '</p>'
    if (reports / 'CASE_STUDY_ZH.md').exists():
        evidence += '<p>' + file_link(reports / 'CASE_STUDY_ZH.md', '逐阶段中文案例与证据核对') + '</p>'
    for filename, label in [('DEV_AUDIT.json', '开发记录核对'),
                            ('TRANSFER_AUDIT.json', '策略提炼核对（保存时的局部快照）'),
                            ('RECOVERY_AUTHORIZATION.json', '用户恢复授权记录')]:
        if (reports / filename).exists():
            evidence += file_link(reports / filename, label) + ' · '
    evidence += '<p>审计文件中的观察范围与时间保持原样，早期局部快照不代表最终任务状态；最终完成数见当前汇总和各任务实际交付。</p>'
    for path, label in [(ROOT / 'events.jsonl', '真实顺序事件'), (ROOT / 'manifest.json', '图片来源与历史暴露'),
                        (ROOT / 'config.json', '配置'), (ROOT / 'protocol.md', '运行协议'), (ROOT / 'report.py', '离线生成脚本')]:
        if path.exists():
            evidence += file_link(path, label) + ' · '
    recoveries = sorted((ROOT / 'recovery').glob('*/acknowledgement.json'))
    if recoveries:
        evidence += ('<h3>服务中断与一次恢复控制</h3><p>以下恢复记录仅授权已保存路由故障的唯一剩余重试，'
                     '不重抽成功回复、不改变图片、模型、effort、冻结策略或预算。原失败仍计入调用。'
                     '连接恢复确认不等于已验证服务健康；是否成功以对应真实 session.json 为准。</p>')
        for receipt_path in recoveries:
            receipt = read(receipt_path)
            evidence += raw_record(receipt_path, '服务恢复确认')
            evidence += file_link(receipt_path.with_name('service_pause.json'), '保留的原始服务暂停证据') + ' · '
            for key, label in [('failed_attempt', '原失败调用'), ('authorized_attempt', '唯一恢复尝试')]:
                session_path = ROOT / receipt[key] / 'session.json'
                if session_path.exists():
                    evidence += file_link(session_path, label) + ' · '
        rationale = ROOT / 'reports/RECOVERY_ADDENDUM.md'
        if rationale.exists():
            evidence += file_link(rationale, '恢复控制工程修订及适用范围')
    evidence += '<p>继续未完成步骤使用 <code>python launch.py resume</code>，默认保留成功缓存。只有新的、尚有一次机会的路由故障经用户确认恢复后才使用 <code>resume --service-recovered</code>；本轮已有的恢复确认不能重复增加机会。完整说明见 '+file_link(ROOT / 'README.md', 'README')+'。</p>'
    evidence += '<p>steps.csv 同时列出构建与 CLI 行；实际图片附件归属相应 CLI 行，build_context_images 单独保留构建元数据的上下文图片，不把 Blender 执行说成模型看图。真实先后以 events.jsonl 为准。</p></section>'
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>阶段式教学与学生自主检查</title><style>
body{font:16px/1.65 system-ui,sans-serif;margin:0;background:#f3f5f8;color:#203044}main{max-width:1440px;margin:auto;padding:24px}h1,h2,h3{line-height:1.3}section,article{background:white;border:1px solid #dce3ea;border-radius:10px;padding:22px;margin:20px 0}article{background:#fbfcfe}.images{display:flex;gap:18px;flex-wrap:wrap}.images>figure{flex:1;min-width:260px;max-width:650px}figure{margin:12px 0}figcaption{font-weight:600;margin:8px 0}img{display:block;max-width:100%;height:auto;max-height:650px;object-fit:contain}.missing{padding:70px 20px;background:#eee;color:#6e5360;min-height:50px}.muted{color:#667}.notice{padding:12px;background:#fff3d6}details{margin:12px 0;border-top:1px solid #ddd;padding-top:10px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef1f5;padding:14px;max-height:600px;overflow:auto;font-size:13px}dt{font-weight:600}dd{margin:0 0 10px;white-space:pre-wrap}table{border-collapse:collapse;width:100%;display:block;overflow:auto}th,td{padding:9px;border:1px solid #ddd;text-align:left}a{color:#155ca4}textarea{display:block;box-sizing:border-box;width:100%;min-height:65px;margin:8px 0}button,select{font:inherit;padding:8px}li{margin:12px 0}.translation{background:#edf4f0;padding:12px}
</style><main><h1>阶段式教师纠错 → 学生自主检查</h1>
<p>单图开发、单图测试；同一任务内持续加载前一 .blend 并应用增量补丁。开发教师纠错与测试学生自查是过程指导，均不是外部质量评分。模型原始记录为英文，页面说明为中文；没有自动排名。</p>
<details><summary>如何完整下载：Git 核心文件与大附件</summary><p>服务器本地完整实验目录可直接打开本页。若只下载 GitHub 分支的核心文件，完整日志、对象清单或 .blend 链接可能不在该下载中；请到 <a href="https://github.com/i025/scene/releases" target="_blank">仓库 Releases</a> 查找本轮 stagewise_teaching_student_selfcheck_pilot 的完整归档，按包内说明解压并保持原有相对目录，再打开 reports/index.html。不要只单独下载 HTML。</p><p>这里只说明完整包的使用方式，不代表附件已经上传或核验。上传状态以本轮 artifacts_index／上传收据为准；尚无确认收据时，完整产物只保证保存在服务器本地。</p></details>
<p><a href="#D01">A 开发教学</a> · <a href="#transfer">B 规则迁移</a> · <a href="#T01">C 学生测试</a></p>
<button onclick="exportOpinions()">导出本地人工意见 JSON</button><p>所有人工意见默认未填写。点击图片可打开原始大小；联系图只缩放显示，不改变原始文件。</p>'''
    page += f'<p class="muted">报告生成时间：{esc(generated_at)}。整体状态：{esc(STATUS.get(overall["status"], overall["status"]))}。这是保存记录的快照，页面不会自动刷新运行状态。</p>'
    if overall['status'] in {'blocked', 'interrupted', 'failed', 'paused'}:
        page += '<p class="notice">任务已停止提交；原阶段文件可能保留最后一次 running 状态，页面依据任务／整体状态显示中断或受阻，不代表仍在后台执行。未交付图保持缺失，没有自动质量零分。</p>'
        page += raw_record(ROOT / 'service_pause.json', '外部服务中断证据')
    page += task_html['D01'] + ''.join(transfer_html) + task_html['T01'] + evidence
    page += '''<script>function exportOpinions(){const rows=[...document.querySelectorAll('select[data-key]')].map(s=>({stage:s.dataset.key,judgment:s.value||null,note:document.querySelector('textarea[data-key="'+s.dataset.key+'"]').value||null}));const u=URL.createObjectURL(new Blob([JSON.stringify({source:'user_entered_only',opinions:rows},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='human_opinions.json';a.click();URL.revokeObjectURL(u)}</script></main></html>'''
    (reports / 'index.html').write_text(page)
    report = ['# 阶段式教师纠错 → 学生自主检查：实际记录', '',
              f'报告生成时间：{generated_at}。这是记录快照，不会自动刷新。', '',
              f'整体状态：{STATUS.get(overall["status"], overall["status"])}。原始与展示状态分列保存在 metrics/stages.csv；不修改原始状态文件。', '',
              '本报告仅从现有文件重算，没有模型调用或质量评分。模型输入输出为英文，给用户的说明为中文。', '',
              'D01 为历史小办公室图；T01 为另一来源的规整厨房图。两图均有历史暴露；T01 与本次开发／提炼隔离不能等同于全新盲测。', '',
              '|任务|状态|已处理／已记录阶段|带问题继续阶段|构建尝试|构建失败|CLI 会话|教师／Astra 调用|',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for task in tasks:
        report.append(f'|{task["task_id"]}|{STATUS.get(task["status"], task["status"])}|{task["processed_stages"]}/{task["recorded_stages"]}|{task["advanced_with_issue_stages"]}|{task["build_attempts"]}|{task["failed_build_attempts"]}|{task["cli_sessions"]}|{task["teacher_or_astra_calls"]}|')
    for task in tasks:
        if not task['final_render_exists'] and task['latest_successful_checkpoint']:
            report.extend(['', f'{task["task_id"]} 尚无最终交付。最近成功的 [.blend 检查点](../{task["latest_successful_checkpoint"]})及[实际渲染](../{task["latest_successful_render"]})仅供检查，不代表后续纠错或复核已完成。'])
    report.extend(['', f'本轮已记录 CLI 会话 {len(calls)} 次；分角色成本见 [cost_by_role.csv](../metrics/cost_by_role.csv)。',
                   '“已处理阶段”包含带问题继续的阶段；只有相应过程记录明确没有待解决问题才列入 no_remaining_issue_stages，仍不是独立质量验收。',
                   f'已测进程 CPU user/system 秒分别为 {summary["process_cpu_user_seconds"]:.2f} / {summary["process_cpu_system_seconds"]:.2f}；覆盖 {summary["cpu_measured_process_count"]}/{len(timing)} 个进程记录。',
                   f'资源配置：CPU {config["resources"]["cpu_total"]} 核，内存上限 {config["resources"]["memory_limit_gb"]} GB，单重任务，设备 CPU。', '',
                   '完整过程、真实图和英文发现见 [离线 HTML](index.html)。所有失败保留在 [steps.csv](../metrics/steps.csv)，输入附件和真实 usage 见 [cli_calls.csv](../metrics/cli_calls.csv)。', '',
                   '提炼策略的实际规则、来源与冻结记录位于 transfer/。存在文件不自动证明所有规则得到落实；测试发现必须对应测试原图与当前输出。', '',
                   '对象 inventory 仅比较已记录字段，不证明完整的非目标保持；部分修改器、ColorRamp 内部、UV、灯光尺寸及着色设置未测。失败快照的 patch_running 不等于仍在执行，以实际 result/build_process 为准。最终图的实际渲染设置见各 delivery/render_settings.json，.blend 中的预览设置可能不同。', '',
                   '没有无教师同图对照、重复采样、模型权重训练或教师自进化收益证明。教师／学生自述不作为视觉质量真值；尚无人工质量结论。', '',
                   '离线重画：在实验目录运行 `python report.py`。图的逐面板来源在 figures/*_contact_sources.json；生成脚本为 report.py。'])
    if (transfer / 'freeze.json').exists():
        report.extend(['', '冻结规则 R6 要求保留未解决问题，但实际 previous_findings 仅用于同阶段复核，后续阶段首次自查收到空列表。图像仍保留，结构化的跨阶段未解决问题记忆未实现；不能把规则要求当成已执行能力。'])
    if (reports / 'CASE_STUDY_ZH.md').exists():
        report.extend(['', '逐阶段中文解释及证据见 [CASE_STUDY_ZH.md](CASE_STUDY_ZH.md)。'])
    if recoveries:
        report.extend(['', '服务路由中断的原始失败与恢复确认保留在 recovery/，恢复控制修订保留在 code_snapshots/recovery_control_01/。只授权原失败的唯一剩余重试，原提示、附件、模型及预算不变；不将路由失败归为几何能力失败。是否完成以本报告实际状态和原始 session 为准。'])
    report.extend(['', '续跑使用 `python launch.py resume`，默认复用已有成功缓存；只有明确确认新的服务暂停恢复、且原调用尚有唯一重试机会时使用 `--service-recovered`。本轮已经确认过的恢复不能反复增加机会。完整包与 Git 核心文件的区别见 [README](../README.md)。'])
    (reports / 'REPORT_ZH.md').write_text('\n'.join(report) + '\n')
    return summary


if __name__ == '__main__':
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
