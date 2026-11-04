"""Evidence-driven M: failure triage, bounded probes and dependency-aware review.
Pure packet processing; no rendering, filesystem exploration or model calls.
"""
import re


CHECKS = ('structure_pass', 'material_pass', 'composite_pass')
GUIDANCE = {
    'structure_pass': {
        'modules': ['object builders', 'SceneAct ownership', 'realize and world initialization'],
        'dependencies': ['primitive validity', 'unique child keys', 'complete semantic inventory'],
        'risk': 'Simplification can omit support parts; duplicate keys silently replace objects.',
        'check': 'Preserve finite separate meshes and meaningful parent groups; inspect omissions separately.'},
    'material_pass': {
        'modules': ['semantic material assignment', 'post-realize shader customization'],
        'dependencies': ['target descendants', 'shared finish/material users'],
        'risk': 'Mutating a shared material or selecting by color can change unrelated objects.',
        'check': 'Copy target materials before local edits; preserve non-target materials, geometry and transforms.'},
    'composite_pass': {
        'modules': ['semantic assembly builders', 'placement and support parameters'],
        'dependencies': ['all intended attached parts', 'external supports', 'explicit transform pivot'],
        'risk': 'Root-level accessories are left behind; changing hierarchy can change fixed target selection.',
        'check': 'Audit intended membership and relative transforms; preserve non-target objects and recheck dependent contacts.'}
}


def _location(program, target):
    if not isinstance(program, str) or target == 'unknown':
        return 'unknown'
    pattern = re.compile(r'\.include\(\s*[\"\x27]' + re.escape(str(target)) + r'[\"\x27]\s*,')
    for number, line in enumerate(program.splitlines(), 1):
        if pattern.search(line):
            return f'program:{number}: {line.strip()}'
    return 'unknown'


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def plan(packet):
    scenes = packet.get('development', [])
    controlled = packet.get('controlled_probes', []) or []
    diagnoses = []
    queue = []
    counts = {key: {'failed': 0, 'passed': 0, 'unknown': 0, 'unavailable_output': 0} for key in CHECKS}
    attempted = set()
    consumed = 0
    for probe in controlled:
        result = probe.get('result') or {}
        kind = probe.get('probe', result.get('probe', 'unknown'))
        attempted.add((probe.get('scene_id'), kind))
        attempts = result.get('render_attempts', 1)
        consumed += max(1, int(attempts)) if _numeric(attempts) else 1
    explicit_count = packet.get('already_executed_probe_count')
    if _numeric(explicit_count):
        consumed = max(consumed, int(explicit_count))
    unused = max(0, 2 - consumed)

    for scene in scenes:
        sid = scene.get('scene_id', 'unknown')
        functional = scene.get('functional') or {}
        target = scene.get('target_object') or functional.get('target_object') or 'unknown'
        program = scene.get('program', '')
        location = _location(program, target)
        metrics = scene.get('metrics') or {}
        complete = scene.get('status') == 'complete' and metrics.get('valid') is not False
        base = {'scene_id': sid, 'object_id': target, 'code_location': location}
        if not complete:
            diagnoses.append(dict(base, observation=metrics.get('error') or 'No complete output reported',
                                  observation_type='measured_output_failure', hypothesis='Visual cause unknown; no valid output',
                                  probe='none', probe_result='not_applicable_without_valid_output',
                                  planned_change='Prioritize compact valid builds and exception-specific recovery before visual changes'))
            for key in CHECKS:
                counts[key]['unavailable_output'] += 1
            queue.append(dict(base, priority=0, modules=['policy execution control', 'primitive construction', 'world initialization'],
                              dependencies=['successful runner output'], risk='An unexecuted repair cannot change the submission',
                              planned_change='Fix build validity; retain successful fallback; do not treat missing output as a visual score'))
        for event in (scene.get('trajectory') or {}).get('events', []):
            if event.get('event') != 'execution_result' or event.get('ok') is not False:
                continue
            stderr = event.get('stderr') or ''
            error = event.get('error') or ''
            trace = re.findall(r'File "([^"]+)", line (\d+)', stderr)
            code_location = f'{trace[-1][0]}:{trace[-1][1]}' if trace else 'unknown'
            observation = stderr.strip().splitlines()[-1] if stderr.strip() else error
            change = 'Repair the explicit runtime failure before changing scene appearance'
            hypothesis = 'unknown'
            if 'Fillet exceeds' in observation:
                change = 'Check every fillet radius against half the smallest dimension before execution'
            elif 'NoneType' in observation and 'use_nodes' in observation:
                change = 'Create a Blender world after realize when world is None'
            elif 'TimeoutExpired' in error:
                hypothesis = 'Primitive expansion or other build/render cost may contribute; timeout stage is unknown'
                change = 'Reduce decorative primitive expansion and keep a compact complete first build'
            diagnoses.append({'scene_id': sid, 'object_id': 'unknown', 'code_location': code_location,
                              'observation': observation, 'observation_type': 'measured_execution_failure',
                              'hypothesis': hypothesis, 'probe': 'none', 'probe_result': 'not_run', 'planned_change': change})
        if not complete:
            continue
        regression = scene.get('regression') or {}
        for key in CHECKS:
            value = functional.get(key)
            state = 'failed' if value is False else 'passed' if value is True else 'unknown'
            counts[key][state] += 1
            guide = GUIDANCE[key]
            queue.append(dict(base, check=key, measured_status=state,
                              priority=1 if state == 'failed' else 2 if state == 'unknown' else 3,
                              modules=guide['modules'], dependencies=guide['dependencies'], risk=guide['risk'],
                              planned_change=guide['check']))
        diagnoses.append(dict(base, observation={'functional': functional,
                              'material': regression.get('material'), 'move': regression.get('move')},
                              observation_type='supplied_fixed_regression',
                              hypothesis='Operability does not establish semantic completeness, support truth or true scale',
                              probe='prescribed material and composite operations',
                              probe_result='supplied regression only',
                              planned_change='Preserve passing behavior; audit semantic membership and local edit scope before changes'))
        relations = ((scene.get('structure') or {}).get('approximate_relations') or {})
        if relations:
            diagnoses.append(dict(base, observation={key: relations.get(key) for key in (
                'approximate_support_candidates_total_count', 'approximate_overlap_candidates_total_count',
                'semantic_support_pass', 'true_mesh_collision_pass', 'limitation')},
                observation_type='approximate_AABB_evidence',
                hypothesis='Some overlaps may be internal construction; semantic object mappings and true contacts remain unknown',
                probe='none', probe_result='No true contact or collision measurement',
                planned_change='Audit object-level supports using semantic anchors; do not repair primitive AABB overlaps indiscriminately'))

    for probe in controlled:
        sid = probe.get('scene_id', 'unknown')
        result = probe.get('result') or {}
        kind = probe.get('probe', result.get('probe', 'unknown'))
        target = (result.get('target_selection') or {}).get('object', 'unknown')
        source = next((scene for scene in scenes if scene.get('scene_id') == sid), {})
        baseline = probe.get('baseline_visual_metrics') or {}
        after = probe.get('visual_metrics') or {}
        valid = result.get('status') == 'completed' and after.get('valid') is True
        deltas = {key: after[key] - baseline[key] for key in ('ssim', 'lpips', 'dino', 'psnr', 'overall')
                  if valid and _numeric(after.get(key)) and _numeric(baseline.get(key))}
        camera_location = 'unknown'
        if kind == 'camera_focal':
            for number, line in enumerate(str(source.get('program', '')).splitlines(), 1):
                if 'set_view(' in line:
                    camera_location = f'program:{number}: {line.strip()}'
                    break
        diagnoses.append({'scene_id': sid, 'object_id': target,
                          'code_location': camera_location if kind == 'camera_focal' else _location(source.get('program'), target),
                          'observation': {'baseline': baseline, 'after': after, 'deltas': deltas,
                                          'controls': {key: result[key] for key in (
                                              'focal_length_before', 'focal_length_after', 'geometry_unchanged',
                                              'scale_factor', 'pivot_world_scene_units', 'pivot_rule',
                                              'fixed_camera', 'non_target_preserved') if key in result}},
                          'observation_type': 'measured_controlled_probe' if valid else 'probe_failure_or_missing_measurement',
                          'hypothesis': 'Camera, object size, pose, depth and occlusion remain competing explanations; a one-sided delta is not causal attribution',
                          'probe': kind, 'probe_result': result.get('status', 'unknown'),
                          'planned_change': 'Compare global architecture anchors against local object landmarks; choose one correction family and audit support and group dependencies'})

    probes = []
    # Use the common menu only, never repeat a recorded intervention or exceed two attempts.
    for scene in scenes:
        if len(probes) >= unused:
            break
        if scene.get('status') != 'complete' or (scene.get('metrics') or {}).get('valid') is False:
            continue
        sid = scene.get('scene_id')
        if sid is None:
            continue
        for kind in ('camera_focal', 'object_scale'):
            if (sid, kind) not in attempted and len(probes) < unused:
                probes.append({'scene_id': sid, 'kind': kind})
        if probes:
            break
    priorities = sorted(CHECKS, key=lambda key: (-counts[key]['failed'], -counts[key]['unknown'], CHECKS.index(key)))
    queue.sort(key=lambda row: (row['priority'], CHECKS.index(row['check']) if row.get('check') in CHECKS else -1))
    return {'probes': probes, 'diagnoses': diagnoses, 'regression_priorities': priorities,
            'regression_counts': counts, 'regression_guidance': True, 'change_queue': queue,
            'unused_probe_budget': unused - len(probes),
            'instruction': (
                'Improve reusable H using supplied development evidence only. First repair missing output, '
                'then prioritize measured regressions and preserve passing checks. Keep observations, visual '
                'hypotheses and heuristics separate; unknown object/code mappings remain unknown. '
                'Use the change queue modules, dependencies and risks for structure, local material '
                'non-target preservation and composite movement checks. Compare camera framing across '
                'distributed anchors with local object scale, pose and depth. Audit support and '
                'occlusion/omission without treating AABB candidates as true contact or semantic labels. '
                'Do not infer causality or an optimum from a single probe delta. Do not request additional '
                'probes after the common two-attempt budget. Keep all final objectives, target rules, '
                'acceptance tests, model roles and resource limits unchanged.')}
