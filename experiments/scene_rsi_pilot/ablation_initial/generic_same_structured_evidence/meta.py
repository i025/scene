"""CLI/backend adaptation of the HyperAgents self-referential meta entry point."""
def generic_plan(packet):
    # Keep the complete explicit archive available and use the common probe menu.
    scenes = packet['development']
    probes = []
    if scenes and scenes[0]['status'] == 'complete':
        probes = [{'scene_id': scenes[0]['scene_id'], 'kind': kind} for kind in ['camera_focal', 'object_scale']]
    return {'probes': probes, 'regression_guidance': True,
            'instruction': 'Improve the shared task program H and your meta-program M. Inspect the entire supplied development archive, sources, execution errors, renders, geometry, and regression measurements. Design a general change to the reconstruction process under the fixed objective and limits. You may change meta.py planning, probe selection, evidence prioritization, and the next research instruction. Preserve callable plan(packet). The next candidate uses the latest valid meta program; this is an exploration branch, not acceptance of its task program. Do not specialize to scene identifiers.'}

def structured_evidence(packet):
    scenes = packet['development']
    diagnoses = []
    for scene in scenes:
        if scene['status'] != 'complete':
            diagnoses.append({'scene_id': scene['scene_id'], 'object_id': 'unknown', 'code_location': 'unknown', 'observation': 'No valid output; consult execution log', 'observation_type': 'measured', 'hypothesis': 'unknown', 'probe': 'none', 'probe_result': 'not_run', 'planned_change': 'Investigate general runtime failure before visual diagnosis'})
            continue
        target = scene.get('target_object', 'unknown')
        diagnoses.append({'scene_id': scene['scene_id'], 'object_id': target, 'code_location': 'unknown', 'observation': 'Reference/render disagreement; magnitude is measured by fixed visual metrics', 'observation_type': 'measured_metric_with_unresolved_visual_cause', 'hypothesis': 'Camera framing or object scale may contribute; this is a hypothesis, not attribution', 'probe': 'camera_focal and object_scale', 'probe_result': 'awaiting controlled intervention', 'planned_change': 'Use probe sensitivity and dependency regression evidence to choose a shared H change'})
        break
    failures = {key: sum((not row.get('functional', {}).get(key, False) for row in scenes)) for key in ['structure_pass', 'material_pass', 'composite_pass']}
    priorities = sorted(failures, key=lambda key: (-failures[key], key))
    return {'diagnoses': diagnoses, 'regression_priorities': priorities}
def plan(packet):
    generic = generic_plan(packet)
    evidence = structured_evidence(packet)
    generic['diagnoses'] = evidence['diagnoses']
    generic['regression_priorities'] = evidence['regression_priorities']
    return generic
