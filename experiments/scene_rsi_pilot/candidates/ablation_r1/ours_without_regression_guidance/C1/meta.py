"""Evidence triage and budget-aware diagnostic planning; no functional feedback inference."""
import ast


INSTRUCTION = (
    'Functional regression feedback is withheld. Keep the evaluator, objectives, gates, '
    'model roles, splits and resource limits fixed. Improve shared H from supplied raw '
    'geometry, execution logs and controlled diagnostics only. Separate measured records, '
    'visual hypotheses and historical heuristics. No single score delta establishes cause. '
    'A probe on a subpart does not test the scale of its semantic parent. Missing output '
    'is failure. AABB candidates are not mesh collision or semantic support labels. '
    'Unknown mappings must remain unknown; no scene-specific reconstruction patches.')


def _location(program, name):
    if not name or name == 'unknown':
        return 'unknown'
    try:
        tree = ast.parse(program)
    except (SyntaxError, TypeError):
        return 'unknown'
    hits = sorted({n.lineno for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and n.value == name})
    return 'program literal at line ' + str(hits[0]) if len(hits) == 1 else 'unknown'


def plan(packet):
    scenes = packet.get('development', [])
    records = packet.get('controlled_probes', []) or []
    # Every supplied probe record conservatively consumes at least one attempt.
    spent = sum(max(1, int((r.get('result') or {}).get('render_attempts', 1)))
                for r in records)
    explicit_count = packet.get('already_executed_probe_count')
    if isinstance(explicit_count, int):
        spent = max(spent, explicit_count)
    available = max(0, 2 - spent)
    diagnoses = []
    probes = []
    eligible = []
    for scene in scenes:
        sid = scene.get('scene_id', 'unknown')
        structure = scene.get('structure') or {}
        target = structure.get('target') or {}
        oid = target.get('object') or scene.get('target_object') or 'unknown'
        program = scene.get('program') or ''

        def emit(object_id, location, observation, kind, hypothesis, probe, result, change):
            diagnoses.append(dict(scene_id=sid, object_id=object_id,
                code_location=location, observation=observation,
                observation_type=kind, hypothesis=hypothesis, probe=probe,
                probe_result=result, planned_change=change))

        if scene.get('status') != 'complete' or structure.get('blend_opened') is False:
            emit('unknown', 'unknown', 'No complete usable output reported.',
                 'reported_failure', 'Execution or output production failed; cause unresolved.',
                 'none', 'not_run', 'Repair execution before visual diagnosis.')
            continue
        eligible.append((sid, oid))
        events = (scene.get('trajectory') or {}).get('events', [])
        for event in events:
            if event.get('event') == 'execution_result' and event.get('ok') is False:
                error = event.get('stderr') or event.get('error') or 'Failure without error detail'
                emit('unknown', 'execution step ' + str(event.get('step', 'unknown')),
                     error, 'reported_execution_failure',
                     'Inspect the supplied traceback; unrelated visual causes remain unknown.',
                     'none', 'no_render',
                     'Audit all API preconditions and initialization before the next build; preserve geometry.')
        emit(oid, _location(program, oid),
             {'target_selection': target,
              'mesh_count': structure.get('mesh_count'),
              'finite_nonempty_mesh_count': structure.get('finite_nonempty_mesh_count')},
             'reported_geometry',
             'Collector-selected target may be a small component rather than the visible subject.',
             'none', 'not_run',
             'Resolve target ancestry and builder mapping before interpreting local scale sensitivity.')
        relations = structure.get('approximate_relations') or {}
        emit('unknown', 'unknown',
             {k: relations.get(k) for k in (
                 'approximate_support_candidates_total_count',
                 'approximate_overlap_candidates_total_count', 'limitation')},
             'reported_approximate_geometry',
             'Component intersections may be intentional; semantic contact remains unresolved.',
             'none', 'not_run',
             'Use named support dependencies and local contact heights; inspect pose and contacts after edits.')
        emit('unknown', 'unknown', structure.get('evidence_projection', {}),
             'reported_evidence_coverage',
             'A visually absent object could be cropped, occluded, overwritten, or omitted.',
             'none', 'not_run',
             'Check inventory, unique sibling keys, construction and camera depth order before duplication.')
        for record in records:
            if record.get('scene_id') != sid:
                continue
            result = record.get('result') or {}
            kind = record.get('probe', result.get('probe', 'unknown'))
            selection = result.get('target_selection') or {}
            probe_target = selection.get('object', 'unknown')
            location = _location(program, probe_target)
            if kind == 'camera_focal':
                camera_lines = [i for i, line in enumerate(program.splitlines(), 1)
                                if line.lstrip().startswith('set_view(')]
                if len(camera_lines) == 1:
                    location = 'program set_view at line ' + str(camera_lines[0])
            completed = result.get('status') == 'completed'
            emit(probe_target, location,
                 {'intervention': result,
                  'visual_metrics': record.get('visual_metrics'),
                  'baseline_visual_metrics': record.get('baseline_visual_metrics')},
                 'reported_controlled_observation' if completed else 'reported_probe_failure',
                 'Sensitivity is local to this intervention; camera, depth, shape and visibility remain confounded.'
                 if completed else 'Missing diagnostic output cannot establish visual sensitivity.',
                 kind, result.get('status', 'unknown'),
                 'Compare global landmarks with local silhouette and target ancestry; change one parameter family.'
                 if completed else 'Investigate diagnostic failure; do not invent measurements.')
    # Do not repeat supplied interventions. Choose a pair only when both fit the budget.
    seen = {(r.get('scene_id'), r.get('probe', (r.get('result') or {}).get('probe')))
            for r in records}
    for sid, oid in eligible:
        if available >= 2 and oid != 'unknown' and all(
                (sid, kind) not in seen for kind in ('camera_focal', 'object_scale')):
            probes = [{'scene_id': sid, 'kind': kind}
                      for kind in ('camera_focal', 'object_scale')]
            break
        if available == 1 and oid != 'unknown' and (sid, 'isolate') not in seen:
            probes = [{'scene_id': sid, 'kind': 'isolate'}]
            break
    return {'probes': probes, 'diagnoses': diagnoses,
            'regression_priorities': [], 'regression_guidance': False,
            'instruction': INSTRUCTION}
