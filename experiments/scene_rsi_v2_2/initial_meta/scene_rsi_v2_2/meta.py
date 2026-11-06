"""Engineered V2.2 strategy, not an automatically evolved M descendant."""


def plan_probes(context):
    budget=context['remaining_probe_budget']
    used=context['already_executed_probe_count']
    scenes={s['scene_id']:s for s in context['development']}
    findings=context['visual_findings']
    probes=[];hypotheses=[]
    for finding in findings:
        scene=scenes[finding['scene_id']]
        explanations=finding['alternatives']
        hypotheses.append({'scene_id':scene['scene_id'],'object_id':finding['object_id'],
                           'observation':finding['observation'],'explanations':explanations,
                           'evidence_kind':'visual_guess_with_projected_ID_not_ground_truth'})
        if scene['status']!='complete' or finding['confidence']=='low':continue
        if finding['probe'] not in context['available_probe_menu']:continue
        object_id=None if finding['probe']=='camera_focal' else finding['object_id']
        if finding['probe']!='camera_focal' and object_id not in scene['all_object_ids']:continue
        if len(probes)<budget:
            probes.append({'scene_id':scene['scene_id'],'object_id':object_id,
                'hypothesis':finding['hypothesis'],'observation':finding['observation'],
                'probe':finding['probe'],'code_module':finding['code_module'],
                'alternatives':explanations,'probe_reason':finding['probe_reason']})
    regressions=[]
    for scene in context['development']:
        if scene['status']!='complete':continue
        relevant=[f['code_module'] for f in findings if f['scene_id']==scene['scene_id']]
        names=[]
        if 'material_edit' in relevant:names+=['material_preservation']
        if 'support_relations' in relevant:names+=['known_support','hierarchy_parts','composite_move']
        if 'part_dependencies' in relevant:names+=['hierarchy_parts','composite_move']
        if any(m in relevant for m in ['camera','object_parameters']):names+=['camera_framing','known_support']
        names+=['hierarchy_parts','material_preservation','composite_move']
        chosen=[]
        for name in names:
            if name in chosen:continue
            offered=context['available_regression_menu'][name]
            if not offered['available']:continue
            applicable=offered['scene_applicability'][scene['scene_id']]
            if applicable is False:continue
            chosen.append(name)
            if len(regressions)<context['remaining_regression_budget']:
                regressions.append({'scene_id':scene['scene_id'],'test':name,
                    'reason':'Check actual current H behavior and declared relations related to the visual hypotheses; unknown applicability remains measurable, not passing'})
    failures=[{'scene_id':s['scene_id'],**s['failure_evidence']} for s in context['development'] if s['status']!='complete']
    return {'probes':probes,'regressions':regressions,'hypotheses':hypotheses,
            'budget_seen':budget,'used_seen':used,'failure_diagnoses':failures,
            'no_probe_reason':None if probes else 'No valid current blend, confident real target, or remaining budget. Read failure stages rather than invent geometry evidence.'}


def plan_patch(context,observations):
    failures=[s['failure_evidence'] for s in context['development'] if s['status']!='complete']
    if failures:
        categories=[f['category'] for f in failures]
        service=any(c in ['codex_service_failure','codex_timeout'] for c in categories)
        module='unresolved_service' if service else 'program_generation_and_verification'
        return {'shared_module':module,'decision':'Service failure cannot identify a 3D fault; retain H and record infrastructure failure.' if service else 'Use observed failure stage and traceback to repair the reusable construction/verification contract, not camera parameters without an image.',
                'failure_diagnoses':failures,'supported_explanations':[],
                'unresolved_explanations':categories,'observations_received':observations,
                'scope':'No image-specific parameter copying; no attribution from build.py existence',
                'evidence_status':'infrastructure' if service else 'measured_execution_error'}
    supported=[];unresolved=[];evidence=[];modules=[]
    for row in observations['regression']:
        result=row['result'];name=row['request']['test']
        if result['measured_pass'] is False:
            module={'known_support':'support_relations','hierarchy_parts':'part_dependencies',
                    'composite_move':'part_dependencies','material_preservation':'material_edit',
                    'camera_framing':'camera'}.get(name)
            if module:
                modules.append(module)
                supported.append({'module':module,'test':name,'kind':'direct_current_program_or_declared_relation_measurement','result':result})
        elif result['measured_pass'] is None:
            unresolved.append({'test':name,'reason':'Unavailable measurement is not passing evidence'})
    for row in observations['probes']:
        request=row['request'];execution=row['execution']
        alternatives=request['alternatives']
        evidence.append({'request':request,'actual_measurement':execution,
                         'visual_metric_delta':row['quality_delta'],
                         'alternatives':alternatives,'interpretation':'Controlled sensitivity, not a unique cause'})
        if execution['status']!='completed':
            unresolved.append({'hypothesis':request['hypothesis'],'reason':'Probe did not execute'});continue
        finding_module=request['code_module'];probe=request['probe']
        controlled=(execution['geometry_unchanged'] is True if probe=='camera_focal'
                    else execution['non_target_preserved'] is True and execution['fixed_camera'] is True
                    if probe=='object_scale' else False)
        if probe=='isolate':
            visibility=execution['target_mesh_visibility_before']
            if visibility and all(v['hide_render'] for v in visibility) and finding_module=='object_coverage':
                modules.append('object_coverage')
                supported.append({'module':'object_coverage','hypothesis':request['hypothesis'],
                    'reason':'The image-localized target exists but all its measured meshes are excluded from rendering; isolation never unhides it. This distinguishes a render-visibility exclusion from mere depth occlusion, without treating full-image Q as causal truth.',
                    'visibility_measurement':visibility})
            else:unresolved.append({'module':finding_module,'reason':'Isolation can expose membership, but full-image Q cannot distinguish omission from correct context removal'})
        elif controlled and row['quality_delta'] is not None:
            delta=row['quality_delta']
            direction='improve' if delta>.005 else 'worsen' if delta<-.005 else 'unchanged'
            matched=[a for a in alternatives if a['predicted_direction']==direction]
            unspecified=[a for a in alternatives if a['predicted_direction']=='unknown']
            candidate_modules=list(dict.fromkeys(a['module'] for a in matched))
            if len(candidate_modules)==1 and not unspecified:
                module=candidate_modules[0];modules.append(module)
                supported.append({'module':module,'hypotheses':matched,'observed_direction':direction,
                    'reason':'The actual controlled response matches a pre-probe prediction and differs from the other supplied predictions. Support is conditional on those hypotheses, not unique causal truth.'})
            else:unresolved.append({'module':finding_module,'observed_direction':direction,
                    'matched_predictions':matched,'unknown_predictions':unspecified,
                    'reason':'The observed response did not distinguish the competing pre-probe predictions'})
        else:unresolved.append({'module':finding_module,'reason':'Sensitivity measurement does not distinguish the candidate explanations'})
    direct=[s['module'] for s in supported if 'test' in s]
    unique=list(dict.fromkeys(direct or modules))
    module=unique[0] if len(unique)==1 else 'unresolved'
    return {'shared_module':module,
            'decision':'Repair the measured shared behavior for '+module if module!='unresolved' else 'Retain competing explanations; permit coder to investigate supplied source, without claiming unique localization.',
            'supported_explanations':supported,'unresolved_explanations':unresolved,
            'probe_evidence':evidence,'observations_received':observations,
            'scope':'Change the reusable parameter transformation, support/dependency or material ownership rule across scenes; never copy fixture object names, IDs or per-image constants.',
            'evidence_status':'supported_not_unique' if module!='unresolved' else 'unresolved',
            'provenance':'Engineer-written V2.2 M; no automatic meta-evolution or capacity-improvement claim'}
