"""One visual/code selection call per allowed model; never a cost guess."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from codex_wrapper import call
from data import write_json

def run(model,attempt):
    cfg=json.loads((ROOT/'config.json').read_text())
    old=json.loads((ROOT.parent/'scene_rsi_v2_4/manifest.json').read_text())
    image=old[0]['source']['image_path']
    api=ROOT/'backend/sceneact'
    sources={p.name:p.read_text() for p in api.glob('*.py')}
    system=(ROOT/'fixed_h/historical_r1_C2_start/system.txt').read_text()
    prompt=('Development-only model selection smoke. Inspect the real attached photograph. '
        'First describe three concrete visible features including their relative locations, then '
        'produce one complete Python SceneAct/Blender scene program matching the photograph. '
        'No tools, no files, no renders; fixed runtime will execute. This checks actual image reception '
        'and basic executable code, not model self-identification or cost.\n'+system+'\nSCENEACT_API:\n'+json.dumps(sources))
    settings={**cfg['model'],'name':model}
    folder=ROOT/'preparation/model_selection'/model/attempt
    try:
        text,session=call(prompt,settings,folder,[image],role='preparation')
    except RuntimeError as exc:
        write_json(folder/'selection_status.json',{'status':'failed','error':str(exc),'cost_unknown':True})
        print(str(exc),flush=True);return 1
    import re
    blocks=re.findall(r'```python\s*\n(.*?)```',text,re.S)
    if not blocks:
        write_json(folder/'selection_status.json',{'status':'invalid_generated_program','cost_unknown':True})
        return 1
    (folder/'build.py').write_text(blocks[-1])
    write_json(folder/'selection_status.json',{'status':'generated_pending_execution','actual_image_attached':True,'cost_unknown':True,'observed_model':session['observed_model']})
    print(folder,flush=True);return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',choices=['gpt-5.6-sol','gpt-6.1-terra'],required=True);p.add_argument('--attempt',default='host_attempt');a=p.parse_args();raise SystemExit(run(a.model,a.attempt))
