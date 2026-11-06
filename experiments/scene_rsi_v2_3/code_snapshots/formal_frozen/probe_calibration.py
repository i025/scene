"""Run every probe against a correct H and each intentionally broken compiler."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fixtures import *
from meta import MENU

folder=ROOT/'calibration/probes';folder.mkdir(parents=True,exist_ok=True)
case='calibration_scene';casefolder=OUT/case;casefolder.mkdir(parents=True,exist_ok=True)
spec=config(1,False);write(casefolder/'public.json',{'spec':spec})
source=(ROOT/'fixtures/reference_renderer_evaluator_only.py').read_text();goodpath=ROOT/'fixtures/reference_renderer_evaluator_only.py'
targets={'camera_calibration':'unknown','geometry_replay':'unknown','position_replay':'unknown','visibility_isolation':spec['screen'],
         'support_relation':spec['target'],'dependency_move':spec['target'],'material_dependency':'Top.001'}
rows=[]
for tool in MENU:
    dest=folder/('correct_'+tool);dest.mkdir(exist_ok=True)
    run_probe(case,goodpath,{'probe':tool,'object_id':targets[tool]},dest)
    measurement=json.loads((dest/'measurement.json').read_text())
    assert measurement['outcome'] is not None and abs(measurement['outcome'])<1e-4,(tool,measurement)
    rows.append({'kind':'correct','tool':tool,'measurement':measurement,'expected':'approximately zero','passed':True})
tools=['camera_calibration','geometry_replay','position_replay','geometry_replay','visibility_isolation','visibility_isolation','dependency_move','support_relation','material_dependency','material_dependency']
for i,tool in enumerate(tools):
    broken,module,_,_=inject(i,source);path=folder/f'broken_{i}.py';path.write_text(broken);dest=folder/('defect_'+str(i));dest.mkdir(exist_ok=True)
    run_probe(case,path,{'probe':tool,'object_id':targets[tool]},dest)
    measurement=json.loads((dest/'measurement.json').read_text())
    assert measurement['outcome'] is not None and measurement['outcome']>1e-3,(i,tool,measurement)
    rows.append({'kind':'injected','module':module,'tool':tool,'measurement':measurement,'expected':'positive contract discrepancy','passed':True})
write(ROOT/'calibration/probe_calibration.json',{'passed':True,'rows':rows,'remote_calls':0,'rendered_frames':17})
print('Probe calibration passed:',len(rows))
