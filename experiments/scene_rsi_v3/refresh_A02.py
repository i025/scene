"""One explicit evaluator correction: inspect saved artifacts, repeat calibration.

Never rebuilds an H artifact or renders. Original facts, scores and CLI sessions
remain saved. Only the pre-existing development calibration schedule is judged.
"""
import argparse,json,random,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from data import write_json
from processes import run_measured,cpu_environment
from bw_evaluate import enrich_delivered_evidence,judge_artifact
import calibrate
OUT=ROOT/'preparation/evaluator_A02'
def read(path):return json.loads(path.read_text())
def preserve(path,name):
    backup=path.with_name(name)
    if path.exists() and not backup.exists():shutil.copy2(path,backup)
def inspect():
    config=read(ROOT/'config.json');OUT.mkdir(exist_ok=True)
    folders=sorted((ROOT/'results').glob('*/*/*/*/bw_evidence'))+sorted((ROOT/'preparation/bw_calibration/evidence').iterdir())
    rows=[]
    for number,folder in enumerate(folders):
        if not (folder/'scene_facts.json').exists():continue
        dest=OUT/'inspection'/f'I{number:03d}';dest.mkdir(parents=True,exist_ok=True)
        original=read(folder/'scene_facts.json')
        preserve(folder/'scene_facts.json','scene_facts_before_native_project_A02.json')
        preserve(folder/'evidence_status.json','evidence_status_before_A02.json')
        preserve(folder/'evaluation.json','evaluation_before_A02.json')
        preserve(folder.parent/'record.json','record_before_A02_evaluator.json')
        command=[config['blender']['executable'],'--background','--disable-autoexec','--threads','8','--python-exit-code','2','--python',str(ROOT/'eval_blend.py'),'--','--blend',str(folder/'artifact.blend'),'--folder',str(dest),'--settings',str(folder/'settings.json')]
        measured=dest/'process.json'
        if not measured.exists():
            with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
                run_measured(command,timeout=config['blender']['build_timeout'],measurement_path=measured,memory_limit_bytes=32*1024**3,stdout=out,stderr=err,env=cpu_environment(threads=8))
        if read(measured)['returncode']!=0:raise RuntimeError('A02 inspect-only failed: '+str(dest))
        facts=read(dest/'scene_facts.json')
        assert facts['native_evidence_version']=='authored_native_project_facts_A02'
        assert facts['blend_opened'] and facts['mesh_count']==original['mesh_count']
        assert facts['objects'][0]['object_id']==original['objects'][0]['object_id']
        shutil.copy2(dest/'scene_facts.json',folder/'scene_facts.json')
        status=enrich_delivered_evidence(folder)
        status['native_evidence_version']=facts['native_evidence_version'];write_json(folder/'evidence_status.json',status)
        # Preserve the previous exact score. This is a documented new evaluator,
        # not another attempt chosen according to the previous score.
        if (folder/'evaluation.json').exists():
            (folder/'evaluation.json').rename(folder/'evaluation_superseded_A02.json')
        rows.append({'source':str(folder),'inspection':str(dest),'native_facts':facts['native_evidence_version'],'delivered_metadata':status['delivery_evidence_version'],'new_renders':0})
        print('inspect-only',number,folder,flush=True)
    write_json(OUT/'inspection_summary.json',{'status':'passed','artifacts':rows,'new_H_calls':0,'new_renders':0,'seconds_scope':'See individual process records'})
def calibration():
    config=read(ROOT/'config.json');plan=read(ROOT/'preparation/bw_calibration/plan.json')
    target=ROOT/'preparation/bw_calibration_A02';target.mkdir(exist_ok=True)
    plan={**plan,'version':'bw_calibration_A02_corrected_native_and_delivery_facts','created':time.time(),'previous_plan':'preparation/bw_calibration/plan.json','expected_render_attempts_without_failures':0,'purpose':'Common evaluator evidence correction and repeat noise; same saved development fixtures, no H regeneration or rendering'}
    write_json(target/'plan.json',plan)
    by_id={row['artifact_id']:row for row in plan['artifacts']};resultdir=target/'judgements';resultdir.mkdir(exist_ok=True)
    for index,item in enumerate(plan['judge_schedule']):
        output=resultdir/f"{item['artifact_id']}_repeat{item['repeat']}.json"
        if output.exists():continue
        artifact=by_id[item['artifact_id']];evidence=ROOT/'preparation/bw_calibration/evidence'/item['artifact_id']
        status=read(evidence/'evidence_status.json');assert status['evaluation_status']=='pending_judge'
        views=list(status['images']);random.Random(4200+index).shuffle(views);session=calibrate.next_session()
        write_json(target/f'judge_assignment_{index:03d}.json',{**item,'session':str(session),'display_order':views,'evidence':str(evidence)})
        result=judge_artifact(artifact['reference'],evidence,read(Path(artifact['rubric'])),config,session,display_order=views)
        write_json(output,{**item,**result,'anonymous_session':str(session),'display_order':views})
        print('calibration',item,result['evaluation_status'],result['S_BW'],flush=True)
    calibrate.OUT=target;calibrate.report(plan)
    report=read(target/'calibration.json')
    write_json(OUT/'calibration_returned.json',{'time':time.time(),'summary':report,'source':str(target)})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['inspect','calibrate']);args=parser.parse_args()
    if args.command=='inspect':inspect()
    else:calibration()
