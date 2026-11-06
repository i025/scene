"""Deterministic strategy/trace contracts; no remote calls or generated scene rescue."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pilot
from diagnostics import classify_failure
from regression import MENU

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'initial_meta/scene_rsi_v2_2/meta.py'
alternatives=[{'module':'camera','explanation':'Framing mismatch','predicted_probe_phenomenon':'Global framing response','predicted_direction':'improve'},
              {'module':'object_parameters','explanation':'Local scale mismatch','predicted_probe_phenomenon':'Wrong-direction camera response','predicted_direction':'worsen'}]
finding={'scene_id':'dev_stub','object_id':'Z_fault_target','observation':'Local reference mismatch',
         'hypothesis':'Object scale or camera confusion','probe':'object_scale','code_module':'object_parameters',
         'confidence':'high','alternatives':alternatives,'probe_reason':'Compare pre-recorded opposite predicted directions'}
scene={'scene_id':'dev_stub','status':'complete','all_object_ids':['A_good','Z_fault_target'],
       'metrics':{'overall':.4},'functional':{'functional_pass':True},'failure_evidence':{'category':'successful_visual_reconstruction'}}
ctx={'development':[scene],'visual_findings':[finding]*3,'remaining_probe_budget':2,
     'already_executed_probe_count':0,'available_probe_menu':['camera_focal','object_scale','isolate'],
     'remaining_regression_budget':3,'modification_risks':[],
     'available_regression_menu':{n:{'available':True,'scene_applicability':{'dev_stub':True}} for n in MENU}}
plan=pilot.meta_execute(source,'plan_probes',ctx)
assert plan['budget_seen']==2 and len(plan['probes'])==2
assert all(p['object_id']=='Z_fault_target' for p in plan['probes'])
pilot.write_json(ROOT/'tests/target_plan.json',{'requested_object':plan['probes'][0]['object_id'],
    'note':'M receives the real calibration object IDs and selects Z rather than A; runner passes this exact ID to Blender.'})
after=copy.deepcopy(ctx);after['remaining_probe_budget']=0;after['already_executed_probe_count']=2
assert not pilot.meta_execute(source,'plan_probes',after)['probes']
request=plan['probes'][0]
def observations(delta):
    return {'probes':[{'request':request,'execution':{'status':'completed','fixed_camera':True,'non_target_preserved':True},'quality_delta':delta}], 'regression':[]}
positive=pilot.meta_execute(source,'plan_patch',after,observations(.02))
negative=pilot.meta_execute(source,'plan_patch',after,observations(-.02))
assert positive['shared_module']=='camera' and negative['shared_module']=='object_parameters'
assert positive['observations_received']['probes'][0]['quality_delta']==.02
ambiguous=copy.deepcopy(request);ambiguous['alternatives'][1]['predicted_direction']='improve'
obs=observations(.02);obs['probes'][0]['request']=ambiguous
assert pilot.meta_execute(source,'plan_patch',after,obs)['shared_module']=='unresolved'
functional={'checks':{'structure':{'gate_pass':True}},'functional_pass':True}
def classify(events,error='RuntimeError',calls=None,status_error=None):
    return classify_failure(False,functional,{'error':status_error},calls or [],[{'error':error}], [{'stage':stage} for stage in events])['category']
assert classify(['python_validation_started'])=='python_program_construction_error'
assert classify(['python_validation_started','scene_build_started'])=='blender_scene_build_error'
assert classify(['scene_build_started','boolean_started'],'TimeoutExpired')=='blender_geometry_timeout'
assert classify(['scene_build_started'],'TimeoutExpired')=='blender_scene_build_timeout_unresolved'
assert classify(['scene_build_completed','render_started'],'TimeoutExpired')=='render_timeout'
assert classify([],calls=[{'status':'failed','error':'TimeoutExpired'}])=='codex_timeout'
assert classify([],calls=[{'status':'failed','error':'routing discovery failed'}])=='codex_service_failure'
assert classify([],status_error='outer_scene_deadline')=='outer_total_budget_exhausted'
assert classify([])=='execution_failure_stage_unknown'
failed=copy.deepcopy(ctx);failed['development'][0].update(status='failed',failure_evidence={'category':'codex_service_failure'})
assert not pilot.meta_execute(source,'plan_probes',failed)['probes']
assert pilot.meta_execute(source,'plan_patch',failed,{'probes':[],'regression':[]})['shared_module']=='unresolved_service'
reg={'probes':[],'regression':[{'request':{'test':'material_preservation'},'result':{'measured_pass':False,'non_target_changed':['Other']}}]}
assert pilot.meta_execute(source,'plan_patch',after,reg)['shared_module']=='material_edit'
support=copy.deepcopy(ctx);support['visual_findings'][0]['code_module']='support_relations'
support['remaining_regression_budget']=1
assert pilot.meta_execute(source,'plan_probes',support)['regressions'][0]['test']=='known_support'
material=copy.deepcopy(ctx);material['visual_findings'][0]['code_module']='material_edit'
material['remaining_regression_budget']=1
assert pilot.meta_execute(source,'plan_probes',material)['regressions'][0]['test']=='material_preservation'
pilot.write_json(ROOT/'tests/diagnostic_contracts.json',{'status':'passed','remote_calls':0,
    'cases':['explicit probe budget','real target not first name','remaining budget updated','two observations change executable second decision','ambiguous predictions remain unresolved','9 stage classifications including unknown','service failure never interpreted as geometry','actual material regression selects shared material ownership module']})
print('DIAGNOSTIC_CONTRACTS_PASSED')
