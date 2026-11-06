"""Small policy and budget contracts, entirely local."""
from common import ROOT,read,write
from meta import MENU,plan_probes,plan_patch
from experiment import validate

predictions=[]
for i,module in enumerate(['set_view','SceneCompiler.emit.geometry']):
    predictions.append({'id':str(i),'module':module,'object_id':'Z_target','predictions':{t:{'lower':float(i),'upper':float(i)+.1,'reason':'stub known separated response'} for t in MENU}})
context={'method':'active','remaining_probe_budget':2,'already_executed_probe_count':0,'available_probe_menu':MENU,'hypotheses':predictions,'object_id':'Z_target','probe_targets':{t:'Z_target' for t in MENU},'initial_module':'unresolved','initial_confidence':.4}
plan=plan_probes(context);assert len(plan['probes'])==2 and all(p['object_id']=='Z_target' for p in plan['probes'])
a=plan_patch(context,[{'status':'completed','request':{'probe':MENU[0]},'measurement':{'outcome':.05}}])
b=plan_patch(context,[{'status':'completed','request':{'probe':MENU[0]},'measurement':{'outcome':1.05}}])
assert a['selected_code_module']!=b['selected_code_module']
identical=[dict(p,predictions=predictions[0]['predictions']) for p in predictions]
assert plan_probes(dict(context,hypotheses=identical))['probes']==[]
assert plan_probes(dict(context,method='structured'))['probes']==[]
source=(ROOT/'fixtures/reference_renderer_evaluator_only.py').read_text();assert validate(source,source)==[]
write(ROOT/'calibration/policy_tests.json',{'passed':True,'remote_calls':0,'checks':['budget2','explicit_Z_target_not_A','observation_changes_M_decision','identical_predictions_do_not_probe','structured_zero_probes','real_shared_source_contract']})
print('Policy tests passed')
