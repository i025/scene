"""M0: select controlled sensitivity tests and act on actual observations."""
def plan_probes(context):
    remaining = context['remaining_probe_budget']
    used = context['already_executed_probe_count']
    menu = context['available_probe_menu']
    valid = [s for s in context['development'] if s['status'] == 'complete']
    probes = []
    regressions = []
    if valid:
        scene = min(valid, key=lambda s: s['metrics']['overall'])
        objects = [o for o in scene['objects'] if o['type'] == 'MESH' and not o['excluded_as_structural'] and o['finite_nonempty_mesh']]
        # Largest generated geometry is a reproducible coverage heuristic, not semantic identification.
        target = max(objects, key=lambda o: o['world_geometry_aabb_approx']['diagonal_scene_units'])['name'] if objects else 'unknown'
        requested = [dict(scene_id=scene['scene_id'], object_id=None, hypothesis='Framing may be sensitive to focal length; geometry held fixed', probe='camera_focal'),
                     dict(scene_id=scene['scene_id'], object_id=target, hypothesis='Generated dominant object scale may explain part of the visual mismatch; camera held fixed', probe='object_scale')]
        probes = [p for p in requested if p['probe'] in menu and p['object_id'] != 'unknown'][:remaining]
        risks = context['modification_risks']
        names = ['hierarchy_parts', 'material_preservation', 'composite_move']
        if 'geometry' in risks: names = ['hierarchy_parts', 'known_support', 'mesh_intersection']
        available = context['available_regression_menu']
        regressions = [dict(scene_id=scene['scene_id'], test=name, reason='Risk: ' + ','.join(risks)) for name in names if available[name]['available']][:context['remaining_regression_budget']]
    return dict(probes=probes, regressions=regressions, budget_seen=remaining, used_seen=used,
                target_rule='Largest nonstructural generated mesh; reference mapping unknown',
                no_probe_reason=None if probes else 'No successful scene/eligible object or budget')


def plan_patch(context, observations):
    successful = [o for o in observations['probes'] if o['execution']['status'] == 'completed' and o['quality_delta'] is not None]
    best = max(successful, key=lambda o: o['quality_delta']) if successful else None
    if best and best['quality_delta'] > 0.005:
        module = 'camera' if best['request']['probe'] == 'camera_focal' else 'object_parameters'
        decision = 'Generalize sensitivity evidence in shared reconstruction reasoning; do not copy probe parameters per scene'
    else:
        module = 'representation_and_verification'
        decision = 'No meaningful improvement from tested perturbations; revise object coverage and verification rather than assert a unique scale/camera cause'
    failures = [o for o in observations['regression'] if o['result']['measured_pass'] is False]
    unknown = [o for o in observations['regression'] if o['result']['measured_pass'] is None]
    if failures: decision += '; repair observed structural/edit risks before visual optimization'
    return dict(shared_module=module, decision=decision, best_probe=best['request'] if best else None,
                observed_deltas=[o['quality_delta'] for o in successful], regression_failures=failures,
                observation_count=len(observations['probes']), unmeasured_regressions=unknown,
                instruction='Modify reusable H and/or executable two-stage M. Explain how actual observations motivated the change. Preserve fixed final functional gates. Sensitivity is not unique causal identification.',
                scope='Cross-image reconstruction; no scene IDs, paths or per-image parameter tables',
                candidate_type_allowed=['H-only','M-only','H+M'])
