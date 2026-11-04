"""Evidence-driven planning using only the supplied development packet."""
import math


def _failed(scene):
    return (scene.get('status') != 'complete' or
            (scene.get('metrics') or {}).get('valid') is not True)


def _score(scene):
    value = (scene.get('metrics') or {}).get('overall')
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return float('inf')


def plan(packet):
    scenes = packet.get('development') or []
    failures = [s for s in scenes if _failed(s)]
    completed = [s for s in scenes if not _failed(s)]
    prior = packet.get('controlled_probes') or []
    used = max(len(prior), int(packet.get('executed_probe_count', 0) or 0))
    available = max(0, 2 - used)
    probes = []
    # Invalid artifacts cannot support camera/scale diagnostics. Address execution first.
    if not failures and completed and available:
        scene = min(completed, key=_score)
        functional = scene.get('functional') or {}
        regression = scene.get('regression') or {}
        broken_group = (functional.get('composite_pass') is False or
                        (regression.get('move') or {}).get('pass') is False or
                        (regression.get('material') or {}).get('pass') is False)
        kinds = ['isolate', 'object_scale'] if broken_group else ['camera_focal', 'object_scale']
        seen = {(p.get('scene_id'), p.get('kind')) for p in prior if isinstance(p, dict)}
        for kind in kinds:
            key = (scene.get('scene_id'), kind)
            if key[0] and key not in seen and len(probes) < available:
                probes.append({'scene_id': key[0], 'kind': kind})
    priority = ('First investigate missing artifacts, exceptions, timeouts and wasted calls; '
                'preserve successful-scene quality while improving reliability.' if failures else
                'Investigate the weakest measured valid reconstruction using available controlled '
                'diagnostics; separate camera error, object geometry and appearance.')
    instruction = (
        'Improve shared policy.solve(task,runtime) and callable meta.plan(packet). Inspect all supplied '
        'development records, raw archive entries, source, execution trajectories, images, geometry and '
        'regression measurements; do not explore disk or obtain external evidence. ' + priority + ' '
        'Trace failures to implementation semantics before adding instructions. Count actual logged '
        'model events and executions, including failed builds and unexecuted final rewrites. Evaluate '
        'whether the compact first-build procedure preserves all major objects, complete semantic '
        'groups and sufficient silhouette detail. Treat primitive budgets as unvalidated heuristics. '
        'Report missing output as failure and null scores as unavailable. Distinguish direct evidence '
        'from causal hypotheses; timeouts without logs do not identify the exact stalled stage. '
        'Functional passes establish prescribed edit operability only; AABB overlap/support candidates '
        'are not collision or contact truth. Inspect group membership in source even when edits pass. '
        'Use paired development evidence when available; do not invent before/after gains or infer '
        'selection images/labels from aggregate retention results. Preserve SceneAct, roles, evaluator, '
        'objective, splits and budgets: five fresh CLI sessions, three executions, 1200 seconds. '
        'Use only runtime.ask, execute, select, remaining and image for model/execution interaction. '
        'Return complete replacement contents only for policy.py, system.txt and meta.py; preserve '
        'the complete system API unless explicitly correcting documented semantics. Do not specialize '
        'to scene IDs, paths or scene answers. Explain applicable scope and risks. The latest valid '
        'meta program guides the next exploration branch; this does not imply task-program acceptance.')
    return {'probes': probes, 'regression_guidance': True, 'instruction': instruction}
