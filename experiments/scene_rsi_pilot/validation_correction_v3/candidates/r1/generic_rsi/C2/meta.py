"""Plan from supplied development evidence; never run evaluation or inspect files."""
import json
import math


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _scenes(value):
    # Called only on explicitly supplied raw development evidence, never Selection.
    if isinstance(value, list):
        for item in value:
            yield from _scenes(item)
    elif isinstance(value, dict):
        if 'scene_id' in value and any(k in value for k in ('trajectory', 'status', 'metrics')):
            yield value
        else:
            for key in ('development', 'archive_raw_development', 'scenes'):
                if key in value:
                    yield from _scenes(value[key])


def _execution_summary(scene):
    events = [e for e in _list(_dict(scene.get('trajectory')).get('events'))
              if isinstance(e, dict)]
    results = [e for e in events if e.get('event') == 'execution_result']
    ok = [e for e in results if e.get('ok') is True]
    failed = [e for e in results if e.get('ok') is False]
    unknown = [e for e in results if e.get('ok') is not True and e.get('ok') is not False]
    # Lossless projected traces can omit the image key; absence alone is unknown.
    explicit_missing = [e for e in ok if 'image' in e and not e['image']]
    metrics = _dict(scene.get('metrics'))
    regression = _dict(scene.get('regression'))
    functional = _dict(scene.get('functional'))
    return {
        'execution_result_events': len(results),
        'ok_events': len(ok),
        'failed_events': len(failed),
        'unknown_result_events': len(unknown),
        'explicit_missing_render_events': len(explicit_missing),
        'timeout_events': sum('timeout' in str(e.get('error', '')).lower() for e in failed),
        'first_execution_ok': results[0].get('ok') if results else None,
        'successful_later_execution_events': sum(e.get('ok') is True for e in results[1:]),
        'model_response_events': sum(e.get('event') == 'model_response' for e in events),
        'cli_session_events': sum(e.get('event') == 'codex_session' for e in events),
        'execution_cap_reached': len(results) >= 3,
        'endpoint_status': scene.get('status'),
        'endpoint_valid': metrics.get('valid'),
        'overall': metrics.get('overall'),
        'functional_pass': functional.get('functional_pass'),
        'regression_target': _dict(regression.get('target_selection')).get('object'),
        'material_operation_pass': _dict(regression.get('material')).get('pass'),
        'move_operation_pass': _dict(regression.get('move')).get('pass'),
        'regression_renders_completed_separate': regression.get('renders_completed'),
        'mesh_count': _dict(scene.get('structure')).get('mesh_count')
    }


def plan(packet):
    packet = _dict(packet)
    current = list(_scenes(packet.get('development', [])))
    raw = list(_scenes(packet.get('archive_raw_development', [])))
    # Exact repeated scene records are not independent evidence. Distinct runs survive.
    records = []
    seen_records = set()
    for scene in current + raw:
        signature = json.dumps(scene, sort_keys=True, default=str)
        if signature not in seen_records:
            seen_records.add(signature)
            records.append(scene)
    summaries = [_execution_summary(s) for s in records]
    observations = [o for o in _list(packet.get('controlled_probes')) if isinstance(o, dict)]
    supplied_used = packet.get('executed_probe_count', len(observations))
    used = max(len(observations), int(supplied_used) if _number(supplied_used) else 0)
    available = max(0, 2 - used)
    seen_probes = {(o.get('scene_id'), o.get('probe', o.get('kind'))) for o in observations}
    probe_evidence = []
    for observation in observations:
        result = _dict(observation.get('result'))
        before = _dict(observation.get('baseline_visual_metrics')).get('overall')
        after = _dict(observation.get('visual_metrics')).get('overall')
        probe_evidence.append({
            'kind': observation.get('probe', observation.get('kind')),
            'status': result.get('status'),
            'actual_target': result.get('target_selection'),
            'focal_before': result.get('focal_length_before'),
            'focal_after': result.get('focal_length_after'),
            'overall_delta': after - before if _number(before) and _number(after) else None,
            'interpretation': 'Only this intervention; missing target/pivot/measurement remains unknown.'
        })
    failures = sum(s['failed_events'] + s['explicit_missing_render_events'] for s in summaries)
    probes = []
    # First repair observed reliability/time starvation from traces. A render cannot
    # recover an exhausted correction opportunity. Never select probes from Selection.
    if not failures and available:
        eligible = [s for s in current if s.get('status') == 'complete'
                    and _dict(s.get('metrics')).get('valid') is True]
        def quality(scene):
            value = _dict(scene.get('metrics')).get('overall')
            return value if _number(value) else float('inf')
        eligible.sort(key=quality)
        for scene in eligible:
            sid = scene.get('scene_id')
            if not isinstance(sid, str):
                continue
            kind = 'isolate' if _dict(scene.get('functional')).get('functional_pass') is False else 'camera_focal'
            if (sid, kind) not in seen_probes:
                probes.append({'scene_id': sid, 'kind': kind})
            if len(probes) >= available:
                break
    instruction = (
        'Improve the shared solve(task,runtime) and callable plan(packet), using every supplied '
        'development case, raw archive, source, execution trace, image, geometry summary and '
        'prescribed edit regression, including failures. Do not explore files or specialize '
        'to scene IDs. Preserve fixed SceneAct APIs, model roles, objective, splits and budgets: '
        '5 fresh CLI sessions, 3 Blender executions, 1200 seconds. Only runtime.ask, execute, '
        'select, remaining and image are permitted model/execution interfaces. No independent '
        'evaluation, rendering, external tools, network or hidden agents in the proposer session. '
        'Count actual execution_result events; regression renders are a separate operation. '
        'Count observable model responses separately from CLI sessions, which may contain more '
        'than one turn. Distinguish API/build failures, missing required output, time exhaustion '
        'and visible mismatch. An absent measurement is unknown; absent required output is '
        'failure. A missing image key in a projected event does not alone prove missing output: '
        'check supplied feedback and endpoint artifacts. Check first-build success and whether '
        'remaining time enabled useful visual revisions. Use complete execute elapsed time '
        'rather than renderer-only timing. Keep API safeguards unless evidence justifies a change. '
        'Next falsifiable branch: reduce expanded decorative geometry, preserve solid silhouettes '
        'and semantic assemblies, and reserve measured build time before requesting revisions. '
        'Expected evidence: first-build validity remains intact, complete build wall time falls '
        'on expensive cases, timeout attempts decline, and completed revisions improve large '
        'visible errors without losing object coverage or prescribed edit passes. A lower mesh '
        'count or fewer attempts alone is not improvement. An early-selection gate that merely '
        'avoids attempts without better outputs is insufficient. Check this against simpler cases '
        'that already finish all three builds. Assess framing, coverage, silhouette, occlusion '
        'and broad tones before fine detail, with expected landmark movement and preserved regions. '
        'Interpret each diagnostic only at its actual target and pivot. A tiny component scale '
        'change cannot diagnose whole-object scale, and a single focal perturbation cannot find '
        'an optimal camera or identify true geometry. Structural/edit passes certify only the '
        'prescribed selected operations, not semantic completeness, physical contact or metric '
        'accuracy; AABBs are approximate. Do not manipulate names for target selection. '
        'Selection aggregates inform retention only; never request Selection images or labels. '
        'Compare all available aggregates without inventing unavailable baselines. Return complete '
        'working replacement files and state risks, especially silhouette loss from simplification '
        'and conservative time estimates suppressing useful revisions. The latest valid meta '
        'program governs the next exploration branch independently of task program acceptance. '
        'Evidence bookkeeping below is descriptive, not a visual diagnosis or new evaluation.\n'
    )
    instruction += json.dumps({'development_records': summaries, 'controlled_probes': probe_evidence}, default=str)
    return {'probes': probes, 'regression_guidance': True, 'instruction': instruction}
