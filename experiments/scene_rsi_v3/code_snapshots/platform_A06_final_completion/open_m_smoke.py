"""Development-only exercise of real M decisions; no proposal is promoted."""
import json,shutil,sys
from pathlib import Path
from pilot import ROOT,cfg,read,context_for,H_START
from processes import cpu_environment,run_measured
from data import write_json

def main():
    root=ROOT/'preparation/open_m_smoke';root.mkdir(exist_ok=True)
    if (root/'proposal.json').exists():return
    original=root
    retry=(root/'worker_summary.json').exists()
    if retry:root=root/'attempt_02';root.mkdir(exist_ok=True)
    h,m=original/'H',original/'M'
    if not h.exists():shutil.copytree(ROOT/'fixed_h'/H_START,h)
    if not m.exists():shutil.copytree(ROOT/'initial_m',m)
    bedroom=next((ROOT/'preparation/second_smoke').rglob('record.json'))
    records=[read(bedroom)]
    goa=ROOT/'preparation/model_selection/gpt-6.1-terra/host_attempt/execution'
    facts=read(ROOT/'preparation/bw_calibration/evidence/development_photo/scene_facts.json')
    objects=[{**o,'name':o['object_id']} for o in facts['objects']]
    records.append({'scene_id':'commons_104864364','status':'completed','valid':True,'folder':str(goa),
                    'metrics':{'overall':None,'reason':'not measured for selection smoke'},'bw':{'S_BW':None,'evaluation_status':'not_started'},
                    'functional':{'structure':{'blend_opened':True,'objects':objects},'checks':{}}})
    packet,scenes,images=context_for(records,H_START,m,0)
    packet['preflight_only']='This is a two-image capability smoke, not a formal research round. Design one new parameterized reusable action, execute it on BOTH supplied development configurations, inspect actual observations, then stop or propose a shared change. Preserve unknown image-object correspondences. Do not change fixed platform or evaluator. Reusable action may compute silhouette/projected/object/material/dependency facts without causal attribution.'
    request={'context':packet,'scenes':scenes,'images':images,'H':str(h),'M_candidate':str(m),'M_program':str(ROOT/'initial_m'),'trace_folder':str(original/'trace'),'result_folder':str(root)}
    write_json(root/'research_request.json',request)
    c=cfg();command=[sys.executable,str(ROOT/'research_worker.py'),'research','--request',str(root/'research_request.json')]
    with (root/'stdout.log').open('w') as out,(root/'stderr.log').open('w') as err:
        result=run_measured(command,timeout=1800,measurement_path=root/'process.json',memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=cpu_environment(threads=c['resources']['threads_per_blender']))
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
