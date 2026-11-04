"""Real image + CLI + Blender loop, excluded from formal dataset."""
from pathlib import Path
import json
import pilot
from strategies import initialize
ROOT=Path(__file__).resolve().parent
initialize(ROOT)
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--kitchen',action='store_true');args=parser.parse_args()
run_id='smoke2' if args.kitchen else 'smoke'
assert (ROOT/'tests/contracts.json').exists() and (ROOT/'tests/calibration.json').exists()
scene=next(s for s in json.loads((ROOT.parent/'scene_rsi_pilot/manifest.json').read_text()) if s['split']=='development')
if args.kitchen:
    source=Path(pilot.config()['dataset']['source_root'])
    raw=next(r for r in json.loads((source/'human_free_manifest.json').read_text())['commons_candidates'] if r['id']=='commons_108221125')
    scene={**scene,'scene_id':raw['id'],'image_path':str(source/raw['image']),'group_id':'old_kitchen_smoke'}
scene={**scene,'split':'smoke'}
base=pilot.run_scene('fixed_h0',run_id,'H0',scene,ROOT/'backend/harnesses/baseline')
source,result=pilot.propose('scene_rsi_v2',run_id,1,ROOT/'backend/harnesses/baseline',ROOT/'initial_meta/scene_rsi_v2/meta.py',[base],[])
if result['status']!='proposed':raise RuntimeError('Smoke proposal failed; inspect proposal_result.json')
child=pilot.run_scene('scene_rsi_v2',run_id,'C1',scene,source)
pilot.write_json(ROOT/'tests'/f'real_{run_id}.json',{'H0':base,'candidate':result,'H1':child,'passed':base['status']=='complete' and child['status']=='complete','formal_data':False})

if (ROOT/'tests/real_smoke.json').exists() and run_id!='smoke':
    import shutil
    shutil.copy2(ROOT/'tests/real_smoke.json',ROOT/'tests/real_smoke_first_attempt.json')
if run_id!='smoke':pilot.write_json(ROOT/'tests/real_smoke.json',pilot.read(ROOT/'tests'/f'real_{run_id}.json'))
