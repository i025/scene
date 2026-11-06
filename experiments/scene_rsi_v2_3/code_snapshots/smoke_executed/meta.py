"""Engineered three-arm experiment policy; no automatically evolved M."""
from itertools import combinations

MENU=['camera_calibration','geometry_replay','position_replay','visibility_isolation','support_relation','dependency_move','material_dependency']


def separation(predictions, tool):
    pairs=list(combinations(predictions,2))
    if not pairs:return 0.0
    separated=0
    for a,b in pairs:
        left=a['predictions'][tool];right=b['predictions'][tool]
        if left['upper'] < right['lower'] or right['upper'] < left['lower']:separated+=1
    return separated/len(pairs)


def plan_probes(context):
    assert context['remaining_probe_budget']>=0
    hypotheses=context['hypotheses']
    if context['method']=='structured':
        return {'probes':[],'reason':'Structured evidence only; no active experimentation. Actual lower tool cost recorded.','predictions_frozen':hypotheses}
    if context['method']=='fixed':
        # V2.1 camera + object-scale fixed policy, now replaying actual H's corresponding operation.
        chosen=['camera_calibration','geometry_replay']
        reason='Frozen camera/scale heuristic; independent of hypothesis predictions.'
    else:
        ranked=sorted(MENU,key=lambda t:(-separation(hypotheses,t),MENU.index(t)))
        chosen=[t for t in ranked if separation(hypotheses,t)>0][:context['remaining_probe_budget']]
        # A non-informative probe is not manufactured to match a count.
        reason='Choose disjoint pre-observation scalar prediction intervals; no predicted separation => no probe.'
    return {'probes':[{'probe':t,'object_id':context['probe_targets'][t],'predicted_pair_separation':separation(hypotheses,t)} for t in chosen[:context['remaining_probe_budget']]],
            'reason':reason,'predictions_frozen':hypotheses,
            'menu_scores':{t:separation(hypotheses,t) for t in MENU}}


def plan_patch(context,observations):
    outcomes={row['request']['probe']:row['measurement']['outcome'] for row in observations if row['status']=='completed' and row['measurement']['outcome'] is not None}
    updated=[]
    for hypothesis in context['hypotheses']:
        matches=[];contradictions=[]
        for tool,value in outcomes.items():
            prediction=hypothesis['predictions'][tool]
            (matches if prediction['lower']<=value<=prediction['upper'] else contradictions).append(tool)
        updated.append({'id':hypothesis['id'],'module':hypothesis['module'],'object_id':hypothesis['object_id'],
                        'supported_by':matches,'contradicted_by':contradictions,
                        'state':'contradicted' if contradictions else 'supported' if matches else 'unresolved'})
    viable=[h for h in updated if h['state']!='contradicted']
    if len(viable)==1 and outcomes:
        selected=viable[0]['module'];basis='One surviving hypothesis within this supplied prediction set; not proof of unique real cause.'
    elif not outcomes and context['initial_confidence']>=.7:
        selected=context['initial_module'];basis='Initial structured diagnosis only; no discriminating experimental update.'
    else:
        selected='unresolved';basis='No unique surviving hypothesis; retain competing explanations for coder investigation.'
    return {'hypothesis_update':updated,'selected_code_module':selected,'planned_shared_H_change':
            'Investigate '+selected+' and preserve public SceneAct reconstruction/edit behavior.' if selected!='unresolved' else 'Investigate competing modules from shared source and public evidence without assuming a unique diagnosis.',
            'evidence':outcomes,'limitations':basis,'M_self_modification':False}
