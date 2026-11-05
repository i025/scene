"""Blinded fixture comparison: same probe/menu caps, all real calls retained."""
from pathlib import Path
import sys,json,ast,time,shutil
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot
from diagnostics import localize
from regression import MENU

def quality(reference,render):
    a=np.array(Image.open(reference).convert('RGB'));b=np.array(Image.open(render).convert('RGB').resize((a.shape[1],a.shape[0])))
    return float(structural_similarity(a,b,channel_axis=2,data_range=255))

def main():
    out=ROOT/'tests/diagnosis'
    fixture_config=pilot.read(out/'fixture_settings.json')
    pilot.config=lambda:fixture_config
    tree=ast.parse((ROOT/'code_snapshots/v2_parent/strategies.py').read_text())
    initial=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='INITIAL' for v in n.targets))
    fixed=out/'fixed_meta.py';fixed.write_text(initial)
    meta=ROOT/'initial_meta/scene_rsi_v2_1/meta.py'
    truth=pilot.read(out/'ground_truth_evaluator_only.json');records=[]
    for case in sorted(out.glob('case*')):
        started=time.monotonic();raw=pilot.read(case/'functional/scene_structure.json')
        q=quality(case/'reference.png',case/'final.png')
        scene=dict(scene_id=case.name,status='complete',metrics={'valid':True,'overall':q},objects=raw['objects'],all_object_ids=[o['name'] for o in raw['objects']],structure=raw,
                   functional={'functional_pass':True},failure_evidence={'category':'successful_visual_reconstruction'},attached_images=[str(case/'reference.png'),str(case/'final.png')])
        context=dict(development=[scene],visual_findings=[],remaining_probe_budget=2,already_executed_probe_count=0,available_probe_menu=['camera_focal','object_scale','isolate'],available_regression_menu={n:{'available':True} for n in MENU},remaining_regression_budget=3,modification_risks=['camera','material','parts'],archive=[])
        # Failure truth is read only after both plans/observations have been persisted.
        for name,source in [('fixed_heuristic',fixed),('scene_rsi_v2_1',meta)]:
            dest=case/name;dest.mkdir(exist_ok=True)
            if (dest/'record.json').exists():records.append(pilot.read(dest/'record.json'));continue
            ctx=json.loads(json.dumps(context))
            if name=='scene_rsi_v2_1':ctx['visual_findings']=localize([scene],dest/'localization')
            plan=pilot.meta_execute(source,'plan_probes',ctx);pilot.write_json(dest/'stage1.json',{'context':ctx,'decision':plan,'M_source':str(source)})
            assert len(plan['probes'])<=2 and len(plan['regressions'])<=3
            obs={'probes':[],'regression':[]}
            for i,request in enumerate(plan['probes']):
                probe_dest=dest/'probes'/str(i)
                execution=pilot.inspect(case,'probe',request['probe'],probe_dest,object_id=request['object_id'])
                png=probe_dest/f"probe_{request['probe']}.png"
                delta=quality(case/'reference.png',png)-q if execution['status']=='completed' else None
                obs['probes'].append(dict(request=request,execution=execution,quality_delta=delta,visual_metrics={'fixture_SSIM':delta+q if delta is not None else None}))
                ctx['remaining_probe_budget']-=1;ctx['already_executed_probe_count']+=1
            for i,request in enumerate(plan['regressions']):
                result=pilot.inspect(case,'regression',output=dest/'regression'/str(i),test=request['test'])
                obs['regression'].append({'request':request,'result':result})
                ctx['remaining_regression_budget']-=1
            decision=pilot.meta_execute(source,'plan_patch',ctx,obs)
            neutral=pilot.meta_execute(source,'plan_patch',ctx,{'probes':[],'regression':[]})
            pilot.write_json(dest/'observations.json',obs);pilot.write_json(dest/'stage2.json',{'observations':obs,'decision':decision})
            label=next(t for t in truth if t['scene_id']==case.name)
            targets=[r['object_id'] for r in plan['probes']]
            modules=[f['code_module'] for f in ctx['visual_findings']]+[decision['shared_module']]
            correct_target=None in targets if label['object_id'] is None else any(t==label['object_id'] or t in label['related_object_ids'] for t in targets)
            record={'method':name,'scene_id':case.name,'status':'completed','probe_budget':2,'probes_executed':len(obs['probes']),'targets':targets,
                    'correct_object':correct_target,'correct_or_related_module':label['module'] in modules,
                    'probe_changes_decision':decision['shared_module']!=neutral['shared_module'] or decision['decision']!=neutral['decision'],
                    'positive_sensitivity':any(o['quality_delta'] is not None and o['quality_delta']>.005 for o in obs['probes']),
                    'valid_shared_patch':None,'patch_status':'not_measured_in_fixture_stage; requires separate shared-code execution, never inferred from localization',
                    'metric':'fixture_SSIM (not formal composite Q)','seconds':time.monotonic()-started,'decision':decision}
            pilot.write_json(dest/'record.json',record);records.append(record)
            pilot.write_json(out/'comparison.json',records)
    print(json.dumps(records))

if __name__=='__main__':main()
