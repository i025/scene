"""One real development-only image; fresh CLI and candidate, excluded from formal data."""
from pathlib import Path
import json
import pilot
from strategies import initialize
ROOT=Path(__file__).resolve().parent
initialize(ROOT)
assert pilot.read(ROOT/'tests/contracts.json')['first_seven_requirements_passed']
assert (ROOT/'tests/calibration.json').exists()
assert (ROOT/'tests/diagnosis/comparison.json').exists()
scene=pilot.read(ROOT/'configs/smoke_scene.json')
base=pilot.run_scene('fixed_h0','smoke','H0',scene,ROOT/'backend/harnesses/baseline')
source,result=pilot.propose('scene_rsi_v2_1','smoke',1,ROOT/'backend/harnesses/baseline',ROOT/'initial_meta/scene_rsi_v2_1/meta.py',[base],[])
if result['status']!='proposed':raise RuntimeError('Real smoke proposal failed; preserve logs and do not freeze')
child=pilot.run_scene('scene_rsi_v2_1','smoke','C1',scene,source)
passed=child['status']=='complete' and (source/'stage2.json').exists()
pilot.write_json(ROOT/'tests/real_smoke.json',{'H0':base,'candidate':result,'H1':child,'passed':passed,'formal_data':False,'H0_may_fail':True,'probe_loop_covered_by_real_blinded_fixtures':True})
if not passed:raise RuntimeError('No valid smoke descendant; formal evolution blocked')
