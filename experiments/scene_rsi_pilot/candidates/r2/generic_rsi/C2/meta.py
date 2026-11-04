"""Plan only from supplied development evidence; never execute or explore data."""
import json
import math
import re


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _failed(scene):
    if scene.get('status') != 'complete' or (scene.get('metrics') or {}).get('valid') is not True:
        return True
    if (scene.get('structure') or {}).get('blend_opened') is False:
        return True
    if 'attached_images' in scene and not scene['attached_images']:
        return True
    if 'program' in scene and not scene['program']:
        return True
    return False


def _score(scene):
    value = (scene.get('metrics') or {}).get('overall')
    return float(value) if _number(value) else None


def _probe_kind(probe):
    return probe.get('kind') or probe.get('probe') or (probe.get('result') or {}).get('probe')


def _events(scene):
    trajectory = scene.get('trajectory') or {}
    return trajectory.get('events') or [] if isinstance(trajectory, dict) else []


def _response_text(event):
    message = event.get('message') or {}
    content = message.get('content') or ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(part.get('text', '') for part in content if isinstance(part, dict))
    return ''


def _trajectory_audit(scene):
    events = [e for e in _events(scene) if isinstance(e, dict)]
    counts = {name: sum(e.get('event') == name for e in events)
              for name in ('model_request', 'model_response', 'codex_session',
                           'execute', 'execution_result', 'select')}
    pending = []
    unexecuted = 0
    for event in events:
        if event.get('event') == 'model_response':
            blocks = re.findall(r'```python\s*\n(.*?)```', _response_text(event), re.S | re.I)
            pending.extend(code.strip() for code in blocks)
        elif event.get('event') == 'execute':
            code = (event.get('code') or '').strip()
            if code in pending:
                index = pending.index(code)
                unexecuted += index
                pending = pending[index + 1:]
    results = [e for e in events if e.get('event') == 'execution_result']
    return {
        'scene_id': scene.get('scene_id'),
        'logged_counts': counts,
        'explicit_failed_execution_results': sum(e.get('ok') is not True for e in results),
        'execution_result_count_deficit': max(0, counts['execute'] - len(results)),
        'unexecuted_code_blocks_in_logged_responses': unexecuted + len(pending),
        'trajectory_available': bool(events),
        'limit': 'Logged events only; request/session/response counts are distinct. Missing event payloads do not identify a stalled stage.'
    }


def _target_audit(scene):
    structure = scene.get('structure') or {}
    target = structure.get('target') or (scene.get('regression') or {}).get('target_selection') or {}
    name = target.get('group_name') or target.get('object') or scene.get('target_object')
    rows = structure.get('objects') or []
    by_name = {r.get('name'): r for r in rows if isinstance(r, dict)}
    row = by_name.get(name) or {}
    parent = by_name.get(row.get('parent')) or {}
    # A nested target is a reason to inspect scope, not evidence that membership is wrong.
    nested = bool(parent.get('parent'))
    functional = scene.get('functional') or {}
    regression = scene.get('regression') or {}
    broken = (functional.get('composite_pass') is False or
              (regression.get('move') or {}).get('pass') is False or
              (regression.get('material') or {}).get('pass') is False)
    return {'scene_id': scene.get('scene_id'), 'target': name,
            'nested_target': nested, 'explicit_edit_failure': broken,
            'target_mesh_count': len(target.get('mesh_names') or []),
            'semantic_completeness': functional.get('semantic_object_completeness'),
            'instruction': 'Inspect source membership and siblings; helper or architecture edit passes do not certify whole-object completeness.'}


def plan(packet):
    scenes = [s for s in packet.get('development') or [] if isinstance(s, dict)]
    failures = [s for s in scenes if _failed(s)]
    valid = [s for s in scenes if not _failed(s)]
    measured = [s for s in valid if _score(s) is not None]
    weakest = min(measured, key=_score) if measured else None
    prior = [p for p in packet.get('controlled_probes') or [] if isinstance(p, dict)]
    declared = []
    for key in ('executed_probe_count', 'already_executed_probe_count'):
        value = packet.get(key)
        if _number(value):
            declared.append(max(0, int(value)))
    attempts = sum(max(1, int((p.get('result') or {}).get('render_attempts') or 1))
                   for p in prior)
    used = max([attempts] + declared)
    available = max(0, 2 - used)
    seen = {(p.get('scene_id'), _probe_kind(p)) for p in prior}
    probes = []
    if weakest is not None and available:
        target = _target_audit(weakest)
        kinds = (['isolate', 'camera_focal'] if target['nested_target'] or target['explicit_edit_failure']
                 else ['camera_focal', 'object_scale'])
        for kind in kinds:
            key = (weakest.get('scene_id'), kind)
            if key[0] and key not in seen and len(probes) < available:
                probes.append({'scene_id': key[0], 'kind': kind})

    probe_audit = []
    for probe in prior:
        result = probe.get('result') or {}
        baseline = (probe.get('baseline_visual_metrics') or {}).get('overall')
        observed = (probe.get('visual_metrics') or {}).get('overall')
        usable = (result.get('status') == 'completed' and bool(result.get('images'))
                  and (probe.get('visual_metrics') or {}).get('valid') is True)
        probe_audit.append({
            'scene_id': probe.get('scene_id'), 'kind': _probe_kind(probe),
            'usable_output': usable,
            'target': result.get('target_selection'),
            'overall_delta': float(observed - baseline) if usable and _number(observed) and _number(baseline) else None,
            'limit': 'Single controlled perturbation of the reported target; no optimum, whole-object scale or causal decomposition is established.'})

    audit = {
        'failed_or_missing_output_scenes': [s.get('scene_id') for s in failures],
        'valid_scenes_with_unavailable_overall': [s.get('scene_id') for s in valid if _score(s) is None],
        'weakest_measured_valid': weakest.get('scene_id') if weakest else None,
        'logged_trajectories': [_trajectory_audit(s) for s in scenes],
        'target_scope': [_target_audit(s) for s in scenes],
        'controlled_observations': probe_audit,
        'probe_budget_used': used,
        'raw_archive_entries_supplied': len(packet.get('archive_raw_development') or [])
    }
    instruction = (
        'Improve shared policy.solve(task,runtime) and callable meta.plan(packet) using only supplied '
        'development records, raw archive entries, source, trajectories, images, geometry and regression '
        'measurements. Do not explore disk or obtain external evidence. Investigate output failures and '
        'the weakest measured valid reconstruction; separate camera, local geometry and appearance. '
        'Trace behavior to implementation semantics before adding instructions, especially attachment '
        'replacement/cloning, emitted mesh versus parent names, material sharing and texture-coordinate '
        'frames. Audit all major objects, silhouette-defining surfaces and source group membership even '
        'when prescribed edits pass. Keep complete semantic subassemblies with their attached trim. '
        'Do not alter names merely to manipulate target selection. Treat primitive targets as unvalidated '
        'heuristics. Count logged requests, responses, sessions and executions separately, including '
        'failed builds and unexecuted rewrites; a session may contain multiple observable turns. '
        'Missing output is failure, null scores are unavailable, and a timeout without logs does not '
        'identify its stalled stage. Functional passes establish prescribed edit operability only; '
        'AABB candidates are not true support/contact/collision measurements. Inspect the exact target '
        'and intervention of every probe: helper scaling is not whole-object scaling. Report paired '
        'metric changes only when both measurements exist; mixed metric directions are not universal '
        'improvement. Use supplied paired development evidence without inventing candidate gains. '
        'Selection aggregates inform retention only; infer no Selection images or labels. Preserve '
        'SceneAct, roles, evaluator, objective, splits and limits: five fresh CLI sessions, three Blender '
        'executions, 1200 seconds, and at most two actual diagnostic renders. Only runtime.ask, execute, '
        'select, remaining and image may mediate model/execution interaction. No independent evaluation '
        'or rendering in the proposer session. Return complete replacement contents only for policy.py, '
        'system.txt and meta.py; preserve the complete system API except documented semantic corrections. '
        'Do not specialize to scene IDs, paths or answers. Explain applicable scope, uncertainty and risks. '
        'The latest valid meta program guides the next exploration branch without implying task-program '
        'acceptance. Supplied-evidence audit follows; it is not an independent evaluation:\n' +
        json.dumps(audit, ensure_ascii=False, default=str))
    return {'probes': probes, 'regression_guidance': True, 'instruction': instruction}
