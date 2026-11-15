"""Finite sequential run within the user's configured CPU/memory allocation."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from processes import cpu_environment,run_measured

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','resume','report','model_checks'])
    p.add_argument('--service-recovered',action='store_true');a=p.parse_args()
    if a.service_recovered and a.command!='resume':
        p.error('--service-recovered is valid only with resume')
    c=json.loads((ROOT/'config.json').read_text())
    os.sched_setaffinity(0,set(c['resources']['cpu_affinity']))
    folder=ROOT/'launches';folder.mkdir(exist_ok=True)
    number=len(list(folder.glob('*.json')))+1
    command=[sys.executable,'-u',str(ROOT/'runner.py'),a.command]+(['--service-recovered'] if a.service_recovered else [])
    with (folder/f'{number:03d}.stdout.log').open('w') as out,(folder/f'{number:03d}.stderr.log').open('w') as err:
        result=run_measured(command,timeout=4*3600,
                            measurement_path=folder/f'{number:03d}.json',
                            memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,
                            env=cpu_environment(threads=c['resources']['threads_per_blender']),stdout=out,stderr=err)
    print(json.dumps(result),flush=True)
    raise SystemExit(result['returncode'])
