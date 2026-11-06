"""One bounded engineering handoff, before first formal M proposal.

Wait for the already-running last baseline judge; request the platform's normal
submission pause, preserve the completed baseline, then start one recorded resume.
No candidate edits, retries, extra proposals or GPU monitoring.
"""
import json,os,subprocess,sys,time,shutil,fcntl
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'outputs/scene_rsi_v3'
WORK=Path(__file__).resolve().parent
OUT=ROOT/'preparation/M_validation_boundary_A02'
OUT.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    launch=ROOT/'launches/002_resume.json';selection=[s for s in read(ROOT/'manifest.json') if s['split']=='selection']
    last=ROOT/'results/historical_r1_C2_start/selection'/selection[-1]['scene_id']/'1'
    pause=ROOT/'protocol_pause.json';deadline=time.monotonic()+2*3600
    while time.monotonic()<deadline:
        state=read(ROOT/'state.json')
        if state['round_completed']!=0 or list((ROOT/'candidates').glob('*/research_started.json')):
            raise RuntimeError('Formal M already began; do not automatically apply pre-M amendment')
        original=read(launch)
        if original['status']!='running':raise RuntimeError('Main launch ended before planned handoff; preserve it for explicit review')
        session=last/'judge_1/session.json'
        if session.exists() and read(session)['status']=='running':
            if pause.exists():raise RuntimeError('An existing protocol pause must be reviewed first')
            write(pause,{'reason':'Operator engineering A02: bounded M validation before first formal proposal',
                         'time':time.time(),'wait_for_current_judge':str(session),'not_model_service_failure':True})
            write(OUT/'pause_requested.json',read(pause));break
        time.sleep(.2)
    else:raise TimeoutError('Two-hour handoff watch expired; no resume started')
    deadline=time.monotonic()+1800
    while time.monotonic()<deadline:
        original=read(launch)
        if original['status']!='running':break
        time.sleep(.2)
    else:raise TimeoutError('Current launch did not stop at its submission boundary')
    if not (ROOT/'round0.json').exists():raise RuntimeError('Baseline incomplete at pause; no automatic resampling')
    if read(ROOT/'round0.json')['selection']['evaluation_completed']!=4:raise RuntimeError('Baseline Selection incomplete; review failure instead of resuming automatically')
    with (ROOT/'experiment.lock').open('r') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
    if len(list((ROOT/'launches').glob('*.json')))!=2:raise RuntimeError('Unexpected launch number; no duplicate started')
    shutil.copyfile(ROOT/'config.json',OUT/'config_before_A02.json')
    shutil.copyfile(ROOT/'state.json',OUT/'state_before_A02.json')
    config=read(ROOT/'config.json');config['pilot']['platform_version']='V3_A02_bounded_M_import';write(ROOT/'config.json',config)
    state=read(ROOT/'state.json');state['platform_version']=config['pilot']['platform_version'];state['phase']='platform_restart_pending';write(ROOT/'state.json',state)
    amendment={'id':'A02','time':time.time(),'reason':'Outer source validation must not execute candidate M before bounded contract worker',
       'formal_M_proposals_before_fix':0,'baseline_records_reused':len(list((ROOT/'results/historical_r1_C2_start').rglob('record.json'))),
       'H_start_and_M000_unchanged':True,'model_budget_scores_and_selection_rules_unchanged':True,
       'new_CLI_calls_for_fix':0,'new_Blender_runs_for_fix':0,'pure_tests':'preparation/M_validation_boundary_A02/tests.json',
       'snapshot':'code_snapshots/platform_A02','previous_launch':'launches/002_resume.json','resume_launch':'launches/003_resume.json'}
    write(ROOT/'configs/amendment_02.json',amendment)
    snapshot=ROOT/'code_snapshots/platform_A02';snapshot.mkdir()
    for file in ROOT.glob('*.py'):shutil.copyfile(file,snapshot/file.name)
    shutil.copytree(ROOT/'backend',snapshot/'backend',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(ROOT/'config.json',snapshot/'config.json')
    (ROOT/'PROTOCOL_AMENDMENT_02.md').write_text('# A02：候选 M 的限时验证边界\n\n这是首次正式 M 研发前的固定平台工程修订，不是自动演化。外层只检查源码与入口，真实导入和契约运行留在15秒 worker。报错/死循环/合法与缺入口夹具共七项通过；不调用模型或 Blender。\n\n原 freeze、A01 与旧源码保留。H_start、M000、模型、预算、评分及选择门槛均未改变。完整 round0 Development/Selection 复用，不重新采样。新配置与源码见 configs/amendment_02.json 和 code_snapshots/platform_A02。002 launch 在既有最后一次 Selection judge 完成后通过提交暂停退出，属于工程中断，不是算法或模型服务失败。\n')
    pause.rename(OUT/'protocol_pause_resolved_A02.json')
    write(OUT/'handoff.json',{'status':'resuming','time':time.time(),'previous_launch':original,'amendment':amendment})
    with (ROOT/'formal_resume_A02_stdout.log').open('w') as out,(ROOT/'formal_resume_A02_stderr.log').open('w') as err:
        result=subprocess.run([sys.executable,str(ROOT/'launch.py'),'resume'],stdout=out,stderr=err,timeout=36*3600+30)
    write(OUT/'resume_returned.json',{'status':'completed' if result.returncode==0 else 'failed','returncode':result.returncode,'time':time.time(),'launch':'launches/003_resume.json'})
    return result.returncode
if __name__=='__main__':raise SystemExit(main())
