"""Scene-RSI pilot entry point, reusing the local SceneEvolve runtime."""
from pathlib import Path
import argparse
import json
import os
import sys
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json

def smoke():
    from PIL import Image
    from inner_loop import run
    from evaluate import score
    config=json.loads((ROOT/'config.json').read_text())
    src=Path('__SCENEEVOLVE_REPRO__/SceneEvolve_Code/data/mini')
    rows=[]
    for number in (1,2):
        folder=ROOT/'smoke'/f'smoke_{number:02d}';folder.mkdir(parents=True,exist_ok=True)
        if (folder/'record.json').exists():
            rows.append(json.loads((folder/'record.json').read_text()));continue
        with Image.open(src/f'scene_{number:03d}.png') as im:
            image=im.convert('RGB');image.thumbnail((256,256));image.save(folder/'reference.png')
        task={'id':f'smoke_{number:02d}','image':str(folder/'reference.png'),'width':image.width,'height':image.height}
        write_json(folder/'task.json',task)
        started=time.monotonic()
        run(task,config,folder,ROOT/'backend/harnesses/baseline')
        metrics=score(task['image'],folder,config)
        row={'method':'fixed_h0','run_id':'smoke','scene_id':task['id'],'split':'smoke','candidate_id':'H0','parent_id':None,'H_version':'baseline','M_version':None,'model_roles':{'student':'gpt-6.1-sol/medium','proposer':'gpt-6-astra/medium'},'status':'complete' if metrics['valid'] else 'failed','metrics':metrics,'device':'CPU','seconds':time.monotonic()-started,'formal':False,'usage':json.loads((folder/'usage.json').read_text())}
        write_json(folder/'record.json',row);rows.append(row)
        print(json.dumps(row),flush=True)
    write_json(ROOT/'smoke/results.json',rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['smoke']);args=parser.parse_args()
    smoke()
