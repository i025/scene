"""M0 V2.1: explicit failures and image-grounded object/probe decisions."""
def plan_probes(context):
    budget=context['remaining_probe_budget']
    used=context['already_executed_probe_count']
    menu=context['available_probe_menu']
    development=context['development']
    findings=context['visual_findings']
    failures=[dict(scene_id=s['scene_id'],**s['failure_evidence']) for s in development if s['status']!='complete' or not s['functional']['functional_pass']]
    probes=[]
    for finding in findings:
        scene=next(s for s in development if s['scene_id']==finding['scene_id'])
        target=finding['object_id']
        if scene['status']!='complete' or finding['confidence']=='low':continue
        if finding['probe'] not in menu:continue
        if finding['probe']!='camera_focal' and (target in [None,'unknown'] or target not in scene['all_object_ids']):continue
        if finding['probe']=='camera_focal':target=None
        if len(probes)<budget:
            probes.append(dict(scene_id=scene['scene_id'],object_id=target,hypothesis=finding['hypothesis'],observation=finding['observation'],code_module=finding['code_module'],probe=finding['probe']))
    regressions=[]
    names=['hierarchy_parts','material_preservation','composite_move']
    if any(f['code_module']=='support_relations' for f in findings):names=['known_support','hierarchy_parts','composite_move']
    elif 'geometry' in context['modification_risks']:names=['hierarchy_parts','mesh_intersection','composite_move']
    valid=[s for s in development if s['status']=='complete']
    if valid:
        scene=min(valid,key=lambda s:s['metrics']['overall'])
        regressions=[dict(scene_id=scene['scene_id'],test=n,reason='Observed module and candidate diff risk') for n in names if context['available_regression_menu'][n]['available']][:context['remaining_regression_budget']]
    return dict(probes=probes,regressions=regressions,budget_seen=budget,used_seen=used,failure_diagnoses=failures,
                no_probe_reason=None if probes else 'No confident mapping, valid blend, or remaining budget; use execution/coverage evidence',
                mapping_rule='Actual image discrepancy plus projected IDs; never default to largest/first mesh')


def plan_patch(context,observations):
    failures=[s['failure_evidence'] for s in context['development'] if s['status']!='complete']
    measured=[o for o in observations['probes'] if o['execution']['status']=='completed' and o['quality_delta'] is not None]
    best=max(measured,key=lambda o:o['quality_delta']) if measured else None
    regression_failures=[o for o in observations['regression'] if o['result']['measured_pass'] is False]
    unmeasured=[o for o in observations['regression'] if o['result']['measured_pass'] is None]
    if failures:
        categories=[f['category'] for f in failures]
        module='policy_execution' if any(c in ['codex_timeout','codex_call_failure'] for c in categories) else 'program_generation_and_verification'
        decision='Use saved error/trajectory to change reusable execution or program-generation instructions. Service failures are not visual algorithm failures; do not perform geometry probes without valid blend.'
    elif regression_failures:
        module='structure_and_edit_contract'
        decision='Repair the measured required structure/edit failure before improving appearance.'
    elif best and best['quality_delta']>0.005:
        module='camera' if best['request']['probe']=='camera_focal' else 'object_parameters' if best['request']['probe']=='object_scale' else 'object_coverage'
        decision='Sensitivity evidence supports studying this shared module; compare alternatives, not a unique cause or per-scene parameter copy.'
    else:
        module='object_coverage_and_verification'
        decision='Tested perturbations do not show a meaningful quality gain. Revisit omissions or uncertain mapping; do not claim successful attribution.'
    return dict(shared_module=module,decision=decision,failure_diagnoses=failures,observed_deltas=[o['quality_delta'] for o in measured],
                regression_failures=regression_failures,unmeasured_regressions=unmeasured,observation_count=len(observations['probes']),
                best_probe=best['request'] if best else None,candidate_type_allowed=['H-only','M-only','H+M'],
                scope='Shared H/M only; no task IDs or image-specific answer tables',
                instruction='Explain correspondence between actual observations and reusable code change. Retain fixed final gates and explicit unknowns.')
