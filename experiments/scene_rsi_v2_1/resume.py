"""Finite sequential pilot, supplemental evaluation and offline report; no daemon."""
from pathlib import Path
import json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
if not (ROOT/'protocol_frozen.json').exists():raise RuntimeError('Run freeze.py after real smoke acceptance first')
for name in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[name]='2'
os.environ['MPLCONFIGDIR']=str(ROOT/'reports/matplotlib_cache')
state=json.loads((ROOT/'state.json').read_text()) if (ROOT/'state.json').exists() else {}
phases=[] if state.get('phase')=='supplement_complete' else ['supplement.py'] if state.get('phase')=='main_complete' else ['pilot.py','supplement.py']
phases+=['analyze.py']
log=ROOT/'pipeline';log.mkdir(exist_ok=True)
for script in phases:
    label=str(time.time_ns())+'_'+script
    with (log/(label+'.stdout.log')).open('w') as out,(log/(label+'.stderr.log')).open('w') as err:
        proc=subprocess.run([sys.executable,str(ROOT/script)],env=os.environ,stdout=out,stderr=err)
    (log/'last_stage.json').write_text(json.dumps({'stage':script,'exit_code':proc.returncode,'stdout':label+'.stdout.log','stderr':label+'.stderr.log','time':time.time()},indent=2))
    if proc.returncode:
        state_path=ROOT/'state.json'
        previous=json.loads(state_path.read_text()) if state_path.exists() else None
        state_path.write_text(json.dumps({'phase':'paused_after_stage_failure','previous_state':previous,'stage':script,'exit_code':proc.returncode,'time':time.time()},indent=2))
        raise SystemExit(proc.returncode)
