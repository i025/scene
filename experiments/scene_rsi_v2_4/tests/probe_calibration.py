"""Calibrate physical intervention controls, excluded 64px smoke renders."""
from pathlib import Path
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pilot

checks={}
for tool in ['camera_focal','camera_tilt','object_depth']:
    dest=ROOT/'tests'/tool;dest.mkdir(exist_ok=True)
    command=[pilot.config()['blender']['executable'],'--background','--threads','2','--python-exit-code','2',
        '--python',str(ROOT/'inspect_blend.py'),'--','--blend',str(ROOT/'tests/fixture.blend'),
        '--output-dir',str(dest),'--settings',str(ROOT/'tests/probe_settings.json'),'--mode','probe','--probe',tool,'--object-id','Z_fault_target']
    pilot.guard('render',1)
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        subprocess.run(command,stdout=out,stderr=err,check=True,env=pilot.cpu_environment(),timeout=60)
    d=json.loads((dest/'probe.json').read_text());assert d['status']=='completed'
    if tool=='camera_focal':assert abs(d['focal_length_after']/d['focal_length_before']-1.1)<1e-6 and d['geometry_unchanged']
    elif tool=='camera_tilt':assert d['local_pitch_degrees']==4 and d['geometry_unchanged'] and d['camera_matrix_before']!=d['camera_matrix_after']
    else:assert d['target_selection']['object']=='Z_fault_target' and d['non_target_preserved'] and any(abs(v)>0 for v in d['depth_offset_scene_units'])
    checks[tool]=d
pilot.write_json(ROOT/'tests/physical_probe_calibration.json',{'status':'passed','checks':checks,'remote_calls':0,'quality':'64x64 one sample, excluded from formal comparisons'})
print('PHYSICAL_PROBE_CALIBRATION_PASS')
