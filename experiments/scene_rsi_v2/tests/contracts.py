"""Tests A–E: fixed contexts and stubs, zero remote calls."""
import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot
from strategies import initialize
from regression import gate,MENU
initialize(ROOT)
meta=ROOT/'initial_meta/scene_rsi_v2/meta.py'
objects=[dict(name=n,type='MESH',excluded_as_structural=False,finite_nonempty_mesh=True,world_geometry_aabb_approx={'diagonal_scene_units':d}) for n,d in [('A_good',1),('Z_fault_target',4)]]
scene={'scene_id':'fixture','status':'complete','metrics':{'overall':.4},'objects':objects}
context={'development':[scene],'remaining_probe_budget':2,'already_executed_probe_count':0,'available_probe_menu':['camera_focal','object_scale','isolate'],'available_regression_menu':{n:{'available':True} for n in MENU},'remaining_regression_budget':3,'modification_risks':['camera'],'archive':[]}
plan=pilot.meta_execute(meta,'plan_probes',context);assert plan['budget_seen']==2 and len(plan['probes'])==2
assert plan['probes'][1]['object_id']=='Z_fault_target'
# Stub external execution only; exercise the actual runner's budget update and exact object forwarding.
seen=[]
def stub_inspect(folder,mode,probe=None,output=None,object_id=None,test=None):
    seen.append((probe,object_id,test));return {'status':'not_applicable','applicable':False,'measured_pass':None}
real=pilot.inspect;pilot.inspect=stub_inspect
folder=ROOT/'tests/stub_scene';(folder/'functional').mkdir(parents=True,exist_ok=True)
(folder/'functional/scene_structure.json').write_text(json.dumps({'objects':objects}))
obs=pilot.execute_plan(context,plan,[{'scene_id':'fixture','folder':str(folder),'metrics':{'overall':.4}}],ROOT/'tests/stub_execution')
pilot.inspect=real
assert context['remaining_probe_budget']==0 and context['already_executed_probe_count']==2
assert ('object_scale','Z_fault_target',None) in seen
assert [item[2] for item in seen if item[2] is not None]==[r['test'] for r in plan['regressions']]
assert pilot.candidate_type({'policy.py':'H','system.txt':'S','meta.py':'M'}, {'policy.py':'H2','system.txt':'S','meta.py':'M'})=='H-only'
assert pilot.candidate_type({'policy.py':'H','system.txt':'S','meta.py':'M'}, {'policy.py':'H2','system.txt':'S','meta.py':'M2'})=='H+M'
positive={'probes':[{'request':plan['probes'][0],'execution':{'status':'completed'},'quality_delta':.1}],'regression':[]}
negative={'probes':[{'request':plan['probes'][0],'execution':{'status':'completed'},'quality_delta':-.1}],'regression':[]}
p=pilot.meta_execute(meta,'plan_patch',context,positive);n=pilot.meta_execute(meta,'plan_patch',context,negative);assert p['shared_module']!=n['shared_module']
truth=[]
for required in [False,True]:
 for applicable in [False,True]:
  for measured in [None,False,True]:
   value=gate(required,applicable,measured);assert value['gate_pass']==(not required or (applicable and measured is True));truth.append(value)
before={'policy.py':'H','system.txt':'S','meta.py':meta.read_text()}
child=ROOT/'tests/descendant_meta.py';child.write_text(meta.read_text().replace("module = 'camera' if", "module = 'camera_calibration_descendant' if"))
after={**before,'meta.py':child.read_text()};assert pilot.candidate_type(before,after)=='M-only'
next_decision=pilot.meta_execute(child,'plan_patch',context,positive);assert next_decision['shared_module']=='camera_calibration_descendant'
result={'A_budget_contract':True,'B_explicit_target_runner':True,'C_observation_feedback':True,'M_controls_executed_regression_menu':True,'D_gate_truth_table':truth,'E_M_only_valid_and_used':True,'H_improvement_from_M_only':False,'positive_decision':p,'negative_decision':n,'next_descendant_decision':next_decision}
(ROOT/'tests/contracts.json').write_text(json.dumps(result,indent=2));print('CONTRACTS_A_B_C_E_PASS')

failed=pilot.failed_functional({'expected_composite':True})
assert all(check['measured_pass'] is None and check['gate_pass'] is False for check in failed['checks'].values())
assert failed['material_pass'] is None and failed['composite_pass'] is None
assert not failed['functional_pass']
print('FAILED_SCENE_CONTRACT_PASS')

(ROOT/'tests/failed_scene_contract.json').write_text(json.dumps({'required_composite':failed,'optional_composite':pilot.failed_functional({'expected_composite':False})},indent=2))
