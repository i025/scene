"""Run the finite pilot with the user's eight CPUs and 32 GB tree limit."""
import argparse
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from processes import cpu_environment,run_measured

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['resume','report']);a=p.parse_args()
    c=json.loads((ROOT/'config.json').read_text())
    os.sched_setaffinity(0,set(c['resources']['cpu_affinity']))
    folder=ROOT/'launches';folder.mkdir(exist_ok=True)
    number=len(list(folder.glob('*.json')))+1
    with (folder/f'{number:03d}.stdout.log').open('w') as out,(folder/f'{number:03d}.stderr.log').open('w') as err:
        result=run_measured([sys.executable,'-u',str(ROOT/'runner.py'),a.command],timeout=24*3600,
                            measurement_path=folder/f'{number:03d}.json',
                            memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,
                            env=cpu_environment(threads=8),stdout=out,stderr=err)
    print(json.dumps(result),flush=True)
    raise SystemExit(result['returncode'])
