"""Regression for the actual 1491/1757-object development packet failure."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot
records=[]
for rid in ['r1','r2']:
    path=ROOT/'results'/rid/'fixed_h0/H0/development/commons_187101683/record.json'
    row=pilot.read(path)
    context,images=pilot.context_for([row],[],1,'before_patch',['camera','material','parts'])
    old=pilot.read(ROOT/'attempt_archive/payload_cap_failure/candidates'/rid/'scene_rsi_v2_1/C1/stage2.json')
    context['visual_findings']=pilot.read(ROOT/'attempt_archive/payload_cap_failure/candidates'/rid/'scene_rsi_v2_1/C1/localization/findings.json')
    source=ROOT/'backend/harnesses/baseline'
    sources={name:(source/name).read_text() for name in ['policy.py','system.txt']}
    sources['meta.py']=(ROOT/'initial_meta/scene_rsi_v2_1/meta.py').read_text()
    api={p.name:p.read_text() for p in (ROOT/'backend/sceneact').glob('*.py')}
    plan=pilot.meta_execute(ROOT/'initial_meta/scene_rsi_v2_1/meta.py','plan_probes',context)
    decision=pilot.meta_execute(ROOT/'initial_meta/scene_rsi_v2_1/meta.py','plan_patch',context,old['observations'])
    payload=dict(attached_image_order=images,sources=sources,sceneact_api=api,context=context,stage1=plan,actual_observations=old['observations'],stage2_M_decision=decision)
    size=len((pilot.COMMON+'\n'+json.dumps(payload,ensure_ascii=False)).encode())
    raw=pilot.read(Path(row['folder'])/'functional/scene_structure.json')['objects']
    assert len(context['development'][0]['all_object_ids'])==len(raw)
    assert len(context['development'][0]['objects'])<=128
    assert size<600000,(rid,size)
    assert context['remaining_probe_budget']==2
    records.append(dict(run_id=rid,raw_object_count=len(raw),numeric_objects=len(context['development'][0]['objects']),all_real_ids_retained=True,proposal_bytes=size,limit=600000,model_calls=0))
(ROOT/'tests/evidence_cap.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))
