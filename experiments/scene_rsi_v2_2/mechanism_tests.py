"""Run the real bounded acceptance checks only after fixed-H experiment A."""
from pathlib import Path
import json
import subprocess
import sys
import time
import pilot

ROOT=Path(__file__).resolve().parent


def run(args,dest):
    dest.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        result=subprocess.run(args,stdout=out,stderr=err,env=pilot.cpu_environment(),timeout=600)
    pilot.write_json(dest/'process.json',{'exit_code':result.returncode,'seconds':time.monotonic()-start,'new_remote_calls':0})
    if result.returncode:raise RuntimeError('Deterministic mechanism check failed: '+str(dest))


def main():
    assert pilot.read(ROOT/'state.json')['phase']=='A_completed'
    run([sys.executable,str(ROOT/'tests/contracts.py')],ROOT/'tests/contracts_process')
    cfg=pilot.config();blender=[cfg['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python']
    run(blender+[str(ROOT/'tests/calibrate.py')],ROOT/'tests/calibration_process')
    target_plan=pilot.read(ROOT/'tests/target_plan.json')
    target=target_plan['requested_object']
    settings={'render':{**cfg['render'],'samples':1,'width':64,'height':64}}
    pilot.write_json(ROOT/'tests/target_settings_64.json',settings)
    pilot.guard('render',1)
    args=blender+[str(ROOT/'inspect_blend.py'),'--','--blend',str(ROOT/'tests/fixture.blend'),
        '--output-dir',str(ROOT/'tests/target_probe_64'),'--mode','probe','--probe','object_scale',
        '--object-id',target,'--settings',str(ROOT/'tests/target_settings_64.json')]
    run(args,ROOT/'tests/target_process')
    measured=pilot.read(ROOT/'tests/target_probe_64/probe.json')
    assert measured['target_selection']['object']==target and measured['non_target_preserved']
    pilot.write_json(ROOT/'tests/MECHANISM_ACCEPTANCE.json',{'status':'passed','remote_model_calls':0,
        'strategy_contracts':'diagnostic_contracts.json','known_geometry_and_edit_cases':'calibration.json',
        'real_Blender_target_probe':'target_probe_64/probe.json',
        'target_probe_quality':'64x64/1 sample excluded from formal A/C',
        'automatic_meta_evolution':False})
    print('ALL_DETERMINISTIC_MECHANISMS_PASSED')


if __name__=='__main__':main()
