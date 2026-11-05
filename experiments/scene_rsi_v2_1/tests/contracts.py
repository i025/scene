"""Deterministic V2.1 selection, failures, budget and M-only contracts; no models."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot
from strategies import initialize
from regression import gate,MENU
initialize(ROOT)
meta=ROOT/'initial_meta/scene_rsi_v2_1/meta.py'
objects=[dict(name='A_floor',type='MESH'),dict(name='Z_chair',type='MESH')]
scene=dict(scene_id='fixture',status='complete',metrics={'overall':.4,'valid':True},objects=objects,all_object_ids=['A_floor','Z_chair'],functional={'functional_pass':True},failure_evidence={'category':'successful_visual_reconstruction'})
finding=dict(scene_id='fixture',object_id='Z_chair',observation='Chair too small in image',hypothesis='Furniture scale',probe='object_scale',code_module='object_parameters',confidence='high')
ctx=dict(development=[scene],visual_findings=[finding],remaining_probe_budget=2,already_executed_probe_count=0,available_probe_menu=['camera_focal','object_scale','isolate'],available_regression_menu={n:{'available':True} for n in MENU},remaining_regression_budget=3,modification_risks=['geometry'],archive=[])
plan=pilot.meta_execute(meta,'plan_probes',ctx)
assert plan['budget_seen']==2 and plan['probes'][0]['object_id']=='Z_chair'
assert all(p['object_id']!='A_floor' for p in plan['probes'])
scene2={**scene,'status':'failed','failure_evidence':{'category':'blender_execution_failure','runtime_status':{'error':'world is None'}},'functional':{'functional_pass':False}}
failed_ctx={**ctx,'development':[scene2],'visual_findings':[]}
failed_plan=pilot.meta_execute(meta,'plan_probes',failed_ctx)
assert failed_plan['probes']==[] and failed_plan['failure_diagnoses']
failed_decision=pilot.meta_execute(meta,'plan_patch',failed_ctx,{'probes':[],'regression':[]})
assert failed_decision['shared_module']=='program_generation_and_verification'
positive={'probes':[{'request':plan['probes'][0],'execution':{'status':'completed'},'quality_delta':.1}],'regression':[]}
negative={'probes':[{'request':plan['probes'][0],'execution':{'status':'completed'},'quality_delta':-.1}],'regression':[]}
assert pilot.meta_execute(meta,'plan_patch',ctx,positive)['shared_module']!=pilot.meta_execute(meta,'plan_patch',ctx,negative)['shared_module']
seen=[]
def stub(folder,mode,probe=None,output=None,object_id=None,test=None):
    seen.append((probe,object_id,test));return {'status':'not_applicable','applicable':False,'measured_pass':None}
folder=ROOT/'tests/stub';(folder/'functional').mkdir(parents=True,exist_ok=True)
(folder/'functional/scene_structure.json').write_text(json.dumps({'objects':objects}))
original=pilot.inspect;pilot.inspect=stub
obs=pilot.execute_plan(ctx,plan,[{'scene_id':'fixture','folder':str(folder),'metrics':{'overall':.4}}],ROOT/'tests/stub_execution')
pilot.inspect=original
assert ctx['remaining_probe_budget']==1 and ctx['already_executed_probe_count']==1
assert ('object_scale','Z_chair',None) in seen
assert [v[2] for v in seen if v[2]]==[r['test'] for r in plan['regressions']]
def row(required,applicable,passed,valid=True):
    return dict(metrics={'valid':valid,'overall':.4 if valid else None},status='complete' if valid else 'failed',functional={'checks':{'test':gate(required,applicable,passed)}})
ineligible=pilot.summarize([row(True,False,None)])
assert ineligible['eligible'] is False
assert pilot.better({**ineligible,'endpoint_quality':.9},ineligible,ineligible) is False
eligible=pilot.summarize([row(True,True,True)])
assert pilot.better(eligible,ineligible,ineligible) is True
assert pilot.summarize([row(False,False,None)])['eligible'] is True
assert not pilot.summarize([row(True,True,False)])['eligible']
assert not pilot.summarize([row(True,True,True,False)])['eligible']
assert not pilot.better(eligible,eligible,eligible)
before={'policy.py':'H','system.txt':'S','meta.py':meta.read_text()}
child=ROOT/'tests/descendant_meta.py';child.write_text(meta.read_text().replace("module='camera'", "module='camera_descendant'"))
assert pilot.candidate_type(before,{**before,'meta.py':child.read_text()})=='M-only'
camera_obs={'probes':[{'request':{'probe':'camera_focal'},'execution':{'status':'completed'},'quality_delta':.1}],'regression':[]}
assert pilot.meta_execute(child,'plan_patch',ctx,camera_obs)['shared_module']=='camera_descendant'
assert pilot.candidate_type(before,{**before,'policy.py':'H2'})=='H-only'
assert pilot.candidate_type(before,{**before,'policy.py':'H2','meta.py':child.read_text()})=='H+M'
for required in [True,False]:
 for applicable in [True,False]:
  for measured in [None,True,False]:
   assert gate(required,applicable,measured)['gate_pass']==(not required or (applicable and measured is True))
result={'A_budget':True,'B_specific_object':True,'C_observations_change_decision':True,'D_absolute_selection_and_gate_truth_table':True,'E_M_only_executable':True,'M_controls_regression':True,'failure_path_no_geometry':True,'first_seven_requirements_passed':True,'remote_calls':0,'selection_edge_cases':6}
(ROOT/'tests/contracts.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
