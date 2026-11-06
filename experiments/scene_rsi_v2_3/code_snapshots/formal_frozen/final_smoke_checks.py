from common import ROOT,read,write,blender,current
rows=[]
for case in ['smoke01','smoke02']:
    for method in ['fixed','structured','active']:
        folder=ROOT/'tasks'/case/method;dest=folder/'final_evaluator_verification'
        status=blender('evaluate',dest,case,folder/'candidate.py',frames=2)
        result=read(dest/'evaluation.json') if status['status']=='completed' else None
        rows.append({'scene_id':case,'method':method,'status':status,'effective_repair':result['effective_shared_repair'] if result else None})
assert all(r['effective_repair'] for r in rows),rows
write(ROOT/'calibration/final_smoke_checks.json',{'passed':True,'all_six':rows,'new_model_calls':0,'original_smoke_evaluation_unchanged':True,'ledger':current()})
print('All six saved smoke proposals pass final evaluator')
