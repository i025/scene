"""Bound the entire experiment-owned tree; never manages unrelated processes."""
import argparse,json,os,sys,fcntl
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from processes import cpu_environment,run_measured
p=argparse.ArgumentParser();p.add_argument('command',choices=['run_10_rounds','resume','report']);a=p.parse_args()
lock=(ROOT/'experiment.lock').open('a')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('This V3 experiment is already running; no duplicate was started.')
c=json.loads((ROOT/'config.json').read_text());os.sched_setaffinity(0,set(c['resources']['cpu_affinity']))
folder=ROOT/'launches';folder.mkdir(exist_ok=True)
number=len(list(folder.glob('*.json')))+1
result=run_measured([sys.executable,str(ROOT/'pilot.py'),a.command],timeout=36*3600,
                    measurement_path=folder/f'{number:03d}_{a.command}.json',
                    memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,
                    env=cpu_environment(threads=c['resources']['threads_per_blender']))
raise SystemExit(result['returncode'])
