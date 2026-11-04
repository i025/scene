"""scene_rsi_pilot M_initial: bounded intervention and dependency regression guidance."""
def plan(packet):
    scenes = packet['development']
    probes = []
    diagnoses = []
    for scene in scenes:
        if scene['status'] != 'complete':
            diagnoses.append({'scene_id': scene['scene_id'], 'object_id': 'unknown', 'code_location': 'unknown', 'observation': 'No valid output; consult execution log', 'observation_type': 'measured', 'hypothesis': 'unknown', 'probe': 'none', 'probe_result': 'not_run', 'planned_change': 'Investigate general runtime failure before visual diagnosis'})
            continue
        target = scene.get('target_object', 'unknown')
        # Paired one-factor interventions distinguish camera from geometry sensitivity.
        probes = [{'scene_id': scene['scene_id'], 'kind': kind} for kind in ['camera_focal', 'object_scale']]
        diagnoses.append({'scene_id': scene['scene_id'], 'object_id': target, 'code_location': 'unknown', 'observation': 'Reference/render disagreement; magnitude is measured by fixed visual metrics', 'observation_type': 'measured_metric_with_unresolved_visual_cause', 'hypothesis': 'Camera framing or object scale may contribute; this is a hypothesis, not attribution', 'probe': 'camera_focal and object_scale', 'probe_result': 'awaiting controlled intervention', 'planned_change': 'Use probe sensitivity and dependency regression evidence to choose a shared H change'})
        break
    failures = {key: sum(not row.get('functional', {}).get(key, False) for row in scenes) for key in ['structure_pass', 'material_pass', 'composite_pass']}
    priorities = sorted(failures, key=lambda key: (-failures[key], key))
    return {'probes': probes, 'diagnoses': diagnoses, 'regression_priorities': priorities, 'regression_guidance': True,
            'instruction': 'Improve shared H and executable M using the controlled probe results and fixed functional regression evidence. Cover camera/object scale confusion, support/spatial relations, and occlusion/omission as applicable. Keep measured facts separate from visual hypotheses and historical heuristics. Link scene_id, object_id, code_location, observation, hypothesis, probe, probe_result, planned_change; unknown mappings must remain unknown. Do not assert causality from a single score delta. Use target modules/dependencies and modification risks to prioritize object structure, local material non-target preservation and composite movement checks. All final objectives and acceptance remain fixed. Modify meta.py only when an executable strategy change is justified; a memory append alone is not meta improvement. Return a reusable H, never a per-scene patched P.'}
