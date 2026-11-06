from pathlib import Path
import json
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json as write
from processes import cpu_environment
from budget import guard,current
from codex_wrapper import call


def read(path):return json.loads(path.read_text())


def blender(action,dest,case=None,candidate=None,request=None,frames=0):
    guard('render',frames);dest.mkdir(parents=True,exist_ok=True)
    command=[read(ROOT/'config.json')['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python',str(ROOT/'fixtures.py'),'--',action,'--dest',str(dest)]
    if case:command+=['--case',case]
    if candidate:command+=['--candidate',str(candidate)]
    if request:command+=['--request',str(request)]
    write(dest/'command.json',{'command':command,'device':'CPU','threads':2,'started':time.time()})
    started=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        try:result=subprocess.run(command,stdout=out,stderr=err,env=cpu_environment(),timeout=600)
        except subprocess.TimeoutExpired:
            status={'status':'timeout','exit_code':None,'seconds':time.monotonic()-started}
        else:status={'status':'completed' if result.returncode==0 else 'failed','exit_code':result.returncode,'seconds':time.monotonic()-started}
    write(dest/'process.json',status)
    if status['status']!='completed':print('Blender failure:',dest,flush=True)
    return status
