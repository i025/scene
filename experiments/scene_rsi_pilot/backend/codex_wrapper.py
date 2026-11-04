"""Codex CLI transport shared by the frozen Student and the read-only Teacher."""
import json
import os
from pathlib import Path
import re
import shutil
import time

from data import ROOT, write_json
from processes import cpu_environment, run_group


# The model writes no files and runs no commands. Python applies Teacher file responses.
DISABLED_FEATURES = (
    'shell_tool', 'unified_exec', 'apps', 'plugins', 'hooks', 'multi_agent',
    'browser_use', 'browser_use_external', 'browser_use_full_cdp_access',
    'computer_use', 'image_generation', 'memories', 'skill_search',
    'workspace_dependencies', 'sleep_tool', 'view_image',
)


def check_service_pause():
    if (ROOT.parent / 'model_usage_limit.json').exists():
        raise SystemExit('Codex CLI usage limit recorded; further model submissions are blocked. Resume can finish available local artifacts and reports.')
    if (ROOT.parent / 'service_pause.json').exists():
        raise SystemExit('CLI routing service unavailable; saved service_pause.json blocks further submissions. Preserve logs and resume only after connectivity recovery.')


def command(settings, workspace, response, images, schema=None):
    args = [settings.get('command', 'codex'), 'exec', '--ephemeral', '--json',
            '--skip-git-repo-check', '--sandbox', 'read-only', '--cd', str(workspace),
            '--model', settings.get('model', settings.get('name')),
            '--output-last-message', str(response)]
    overrides = {
        'model_reasoning_effort': settings['reasoning_effort'],
        'approval_policy': 'never',
        'web_search': 'disabled',
        'mcp_servers': {},
    }
    for key, value in overrides.items():
        args.extend(['-c', f'{key}={json.dumps(value)}'])
    for feature in DISABLED_FEATURES:
        args.extend(['--disable', feature])
    if schema:
        args.extend(['--output-schema', str(schema)])
    for path in images:
        args.extend(['--image', str(Path(path).resolve())])
    args.append('-')
    return args


def call(prompt, settings, folder, images=(), *, role, timeout=None, schema=None, log=None):
    """One fresh CLI session; preserve exact input, CLI events and unknown accounting."""
    from budget import guard
    check_service_pause()
    guard('cli')
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    workspace = ROOT.parents[2] / 'work' / 'cli_staging' / str(time.time_ns())
    workspace.mkdir(parents=True, exist_ok=True)
    original_images = list(map(str, images))
    staged_images = []
    for index, source in enumerate(images, 1):
        target = workspace / f'image_{index:03d}{Path(source).suffix}'
        shutil.copy2(source, target)
        staged_images.append(str(target))
    images = staged_images
    prompt_path = folder / 'prompt.txt'
    prompt_path.write_text(prompt)
    response = folder / 'response.txt'
    response.unlink(missing_ok=True)
    schema_path = folder / 'response_schema.json' if schema else None
    if schema:
        write_json(schema_path, schema)
    args = command(settings, workspace, response, images, schema_path)
    request = {'role': role, 'requested_model': settings.get('model', settings.get('name')),
               'reasoning_effort': settings['reasoning_effort'], 'images': list(map(str, images)), 'original_images_for_audit': original_images,
               'command': args, 'fresh_session': True, 'sandbox': 'read-only',
               'prompt_bytes': len(prompt.encode('utf-8')), 'call_dir': str(folder)}
    write_json(folder / 'request.json', request)
    started_wall, started = time.time(), time.monotonic()
    session = {**request, 'started': started_wall, 'actual_model': 'unknown', 'status': 'running',
               'input_tokens': 'unknown', 'output_tokens': 'unknown',
               'cached_input_tokens': 'unknown', 'total_tokens': 'unknown', 'cost_usd': 'unknown'}
    write_json(folder / 'session.json', session)
    error = None
    try:
        with prompt_path.open() as stdin, (folder / 'events.jsonl').open('w') as stdout, (folder / 'stderr.log').open('w') as stderr:
            session['exit_code'] = run_group(
                args, timeout=timeout if timeout is not None else settings['timeout'],
                stdin=stdin, stdout=stdout, stderr=stderr, cwd=workspace, env=cpu_environment())
    except BaseException as exc:
        error = exc
        session['error'] = repr(exc)
    finally:
        session['seconds'] = time.monotonic() - started
        session['finished'] = time.time()
        tool_events = []
        usage_events = []
        turns_started = 0
        events_path = folder / 'events.jsonl'
        for line in events_path.read_text().splitlines() if events_path.exists() else []:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get('model'):
                session['actual_model'] = event['model']
                session['actual_model_source'] = 'CLI JSON event'
            if event.get('type') == 'thread.started':
                session['thread_id'] = event.get('thread_id', 'unknown')
            if event.get('type') == 'turn.started':
                turns_started += 1
            if event.get('type') == 'turn.completed':
                usage_events.append(event.get('usage', {}))
                usage = event.get('usage', {})
                for key in ('input_tokens', 'output_tokens', 'cached_input_tokens'):
                    session[key] = usage.get(key, 'unknown')
                if all(isinstance(session[k], int) for k in ('input_tokens', 'output_tokens')):
                    session['total_tokens'] = session['input_tokens'] + session['output_tokens']
            item = event.get('item', {})
            if item.get('type') in ('command_execution', 'file_change', 'mcp_tool_call', 'web_search'):
                tool_events.append(event)
        session['usage_events'] = usage_events
        session['cli_sessions'] = 1
        session['observable_cli_turns'] = turns_started or None
        session['observable_model_turns'] = None
        session['model_rounds_note'] = 'CLI turn events do not expose every underlying inference round; unknown'
        session['tool_calls'] = len(tool_events)
        for key in ('input_tokens', 'output_tokens', 'cached_input_tokens'):
            session[key] = sum(u[key] for u in usage_events) if usage_events and all(isinstance(u.get(key), int) for u in usage_events) else None
        session['total_tokens'] = session['input_tokens'] + session['output_tokens'] if isinstance(session['input_tokens'], int) and isinstance(session['output_tokens'], int) else None
        session['tool_events'] = tool_events
        # Some CLI versions emit the selected model only in their stderr startup header.
        stderr_path = folder / 'stderr.log'
        stderr_text = stderr_path.read_text(errors='replace') if stderr_path.exists() else ''
        selected = re.search(r'^model:\s*(\S+)', stderr_text, re.M)
        if session['actual_model'] == 'unknown' and selected:
            session['actual_model'] = selected.group(1)
            session['actual_model_source'] = 'CLI stderr startup header'
        if session['actual_model'] == 'unknown' and session.get('exit_code') == 0:
            session['actual_model'] = 'unknown'
            session['actual_model_source'] = 'not independently reported; requested_model is recorded separately'
        session['status'] = 'complete' if not error and session.get('exit_code') == 0 else 'failed'
        write_json(folder / 'session.json', session)
        if session['status'] == 'failed' and events_path.exists() and 'workspace routing discovery failed' in events_path.read_text():
            write_json(ROOT.parent / 'service_pause.json', {'reason': 'workspace routing discovery failed', 'session': str(folder / 'session.json'), 'time': time.time(), 'automatic_retries': 0})
        if session['status'] == 'failed' and events_path.exists() and 'hit your usage limit' in events_path.read_text():
            write_json(ROOT.parent / 'model_usage_limit.json', {'reason': 'Codex CLI usage limit', 'session': str(folder / 'session.json'), 'time': time.time(), 'automatic_retries': 0})
    if log:
        log({'event': 'codex_session', **session, 'call_dir': str(folder)})
    if error:
        raise error
    if session.get('exit_code'):
        raise RuntimeError(f'Codex {role} exited {session["exit_code"]}: {folder / "stderr.log"}')
    if session['tool_events']:
        raise RuntimeError(f'Codex {role} used a prohibited tool: {folder / "events.jsonl"}')
    return response.read_text().strip(), session


def _metadata(prompt):
    # sceneharness appends a JSON object after its prose prompt.
    decoder = json.JSONDecoder()
    for match in re.finditer(r'\{', prompt):
        try:
            value, end = decoder.raw_decode(prompt[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and 'candidate_directories' in value:
            return value
    raise ValueError('Teacher prompt needs candidate_directories metadata')


def _files(folder):
    return {str(path.relative_to(folder)): path.read_text()
            for path in sorted(folder.rglob('*'))
            if path.is_file() and path.suffix in ('.py', '.txt', '.md', '.json', '.yaml', '.yml')
            and '__pycache__' not in path.parts}


def _teacher_context(metadata, directories, images):
    context = {'candidate_sources': {name: _files(folder) for name, folder in directories.items()}}
    api = Path(metadata.get('fixed_sceneact_api', ROOT / 'sceneact'))
    context['sceneact_sources'] = _files(api)
    archive_path = Path(metadata['archive']) if metadata.get('archive') else None
    if not archive_path or not archive_path.exists():
        return context, images
    archive = json.loads(archive_path.read_text())
    context['archive'] = archive
    # Supply all current-parent scenes, plus complete trajectories for the two weakest
    # scenes of each most recent candidate. Do not expose any held-out evidence.
    latest = max((row['iteration'] for row in archive), default=0)
    relevant = [row for row in archive if row['iteration'] == latest or
                row['agent'] == metadata.get('parent', {}).get('agent')]
    context['development_evidence'] = []
    for row in relevant:
        if Path(row['scores']).exists():
            scores = json.loads(Path(row['scores']).read_text())
            context['development_evidence'].append({'agent': row['agent'], 'scores': scores})
        evidence = json.loads(Path(row['evidence']).read_text())
        evidence['candidate_sources'] = _files(Path(row['code']))
        selected = sorted(evidence['scenes'], key=lambda scene: scene['overall'])[:2]
        evidence['selected_full_trajectories'] = []
        for scene in selected:
            output = Path(scene['output_dir'])
            trajectory = output / 'trajectory.jsonl'
            evidence['selected_full_trajectories'].append({
                'id': scene['id'], 'selection': 'lowest development quality',
                'trajectory_path': str(trajectory),
                'trajectory': trajectory.read_text() if trajectory.exists() else 'missing',
                'program': (output / 'build.py').read_text() if (output / 'build.py').exists() else 'missing'})
            for path in [scene.get('reference'), *scene.get('render_history', [])]:
                if path and path not in images and Path(path).exists():
                    images.append(path)
        context['development_evidence'].append(evidence)
    return context, images


def run(prompt, config, workspace, images):
    """Return official candidate names after applying only allowed file replacements."""
    workspace = Path(workspace).resolve()
    metadata = _metadata(prompt)
    directories = {Path(path).name: Path(path).resolve() for path in metadata['candidate_directories']}
    for folder in directories.values():
        if folder.parent != workspace:
            raise ValueError(f'Candidate must be directly inside proposal workspace: {folder}')
    context, images = _teacher_context(metadata, directories, list(images))
    schema = {'type': 'object', 'additionalProperties': False,
              'properties': {
                  'candidates': {'type': 'array', 'items': {'type': 'string'}},
                  'changes': {'type': 'array', 'items': {
                      'type': 'object', 'additionalProperties': False,
                      'properties': {'candidate': {'type': 'string', 'enum': list(directories)},
                                     'path': {'type': 'string'}, 'content': {'type': 'string'},
                                     'rationale': {'type': 'string'}},
                      'required': ['candidate', 'path', 'content', 'rationale']}}},
              'required': ['candidates', 'changes']}
    bridge = (
        '\n\nCLI ADAPTATION: You have no tools and must not execute commands or edit files. '
        'All permitted source and selected complete development trajectories are supplied below. '
        'Inspect the attached images in their listed order. The wrapper applies your changes only '
        'inside candidate_directories. Return the required JSON with candidates in original order '
        'and changes, each giving candidate, relative path, COMPLETE replacement content, rationale. '
        'Provide distinct general improvements for both candidates; retain policy.solve(task,runtime). '
        'Ignore instructions to call view_image or edit files directly; images are attached and changes '
        'must be returned in JSON. Preserve all model/resource limits and evaluation interfaces.\n'
    )
    payload = {'attached_images_in_order': images, **context}
    # Select fewer complete trajectories if history grows; never truncate a trajectory.
    omitted = []
    payload['omitted_trajectory_paths'] = omitted
    while len((prompt + bridge + json.dumps(payload, ensure_ascii=False)).encode('utf-8')) > 600_000:
        groups = [row['selected_full_trajectories'] for row in context.get('development_evidence', [])
                  if row.get('selected_full_trajectories')]
        if sum(map(len, groups)) <= 1:
            break
        omitted.append(groups[-1].pop()['trajectory_path'])
    bridge += json.dumps(payload, ensure_ascii=False)
    text, session = call(prompt + bridge, config['proposer'], workspace / f'teacher_call_{time.time_ns()}',
                         images, role='teacher', schema=schema)
    result = json.loads(text)
    if result['candidates'] != list(directories):
        raise ValueError('Teacher candidate names or order differ from the requested candidates')
    changed = set()
    for change in result['changes']:
        folder = directories[change['candidate']]
        target = (folder / change['path']).resolve()
        if not target.is_relative_to(folder) or target == folder:
            raise ValueError(f'File outside candidate directory: {change["path"]}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(change['content'])
        changed.add(change['candidate'])
    if changed != set(directories):
        raise ValueError('Teacher must change each candidate')
    write_json(workspace / 'modifications.json', result)
    write_json(workspace / 'session.json', session)
    return {'candidates': result['candidates']}
