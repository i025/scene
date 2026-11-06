"""Independent forecast fixtures; no images, remote models or formal results."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import meta
from regression import gate


def hypothesis(name, lower, upper):
    return {'id':name,'module':name,'object_id':'Z_fault_target',
            'predictions':{t:{'lower':lower,'upper':upper,'reason':'Independent numerical fixture'} for t in meta.MENU}}


ctx={'method':'active','valid_blend':True,'remaining_probe_budget':2,'already_executed_probe_count':0,
     'available_probe_menu':meta.MENU,'probe_targets':{t:('unknown' if t.startswith('camera') else 'Z_fault_target') for t in meta.MENU},
     'hypotheses':[hypothesis('camera_framing',-.02,.02),hypothesis('geometry_scale_depth',.01,.05)],'initial_module':'camera_framing'}
plan=meta.plan_probes(ctx)
assert len(plan['probes'])==2
assert meta.discrimination(ctx['hypotheses'],'camera_focal')>=.15
assert ctx['hypotheses'][0]['predictions']['camera_focal']['upper']>ctx['hypotheses'][1]['predictions']['camera_focal']['lower']
assert meta.plan_probes({**ctx,'method':'fixed'})['probes'][1]['object_id']=='Z_fault_target'
rows=[]
for value, expected in [(-.015,'camera_framing'),(.045,'geometry_scale_depth'),(.5,'unresolved')]:
    obs=[{'request':{'probe':'camera_focal'},'status':'completed','outcome':value}]
    decision=meta.plan_patch(ctx,obs);assert decision['selected_module']==expected
    rows.append({'observed':value,'decision':decision})
identical={**ctx,'hypotheses':[hypothesis('a',-.02,.02),hypothesis('b',-.02,.02)]}
assert meta.plan_probes(identical)['probes']==[]
assert meta.plan_probes({**ctx,'remaining_probe_budget':0})['probes']==[]
assert meta.plan_probes({**ctx,'valid_blend':False})['probes']==[]
assert gate(True,False,None)['gate_pass'] is False
assert gate(False,True,False)['gate_pass'] is True
assert gate(True,True,True)['gate_pass'] is True
(ROOT/'tests/contracts.json').write_text(json.dumps({'status':'passed','partial_overlap_selected':plan,'different_observations':rows,
    'identical_forecasts_abstain':True,'calibration_miss_not_causal_refutation':True,'budget_zero_abstain':True,
    'no_blend_execution_path':True,'required_gate_cases':True,'remote_calls':0},indent=2))
print('CONTRACTS_PASS')
