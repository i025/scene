"""Final evaluator catches camera pose and generated surface regressions."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fixtures import *
folder=ROOT/'calibration/extended';folder.mkdir(parents=True,exist_ok=True)
source=(ROOT/'fixtures/reference_renderer_evaluator_only.py').read_text();spec=config(1,False)
reference=signature(build(load(ROOT/'fixtures/reference_renderer_evaluator_only.py'),spec))
patches=[('camera_pose','bpy.context.scene.camera=result','result.rotation_euler.z += .2\n    bpy.context.scene.camera=result','camera'),
         ('surface_shader',"'Base Color':finish.rgba","'Base Color':(.9,.0,.0,1)",'surface_integrity')]
rows=[]
for name,old,new,key in patches:
    path=folder/(name+'.py');path.write_text(source.replace(old,new));checks=compare(signature(build(load(path),spec)),reference)
    assert not checks[key],(name,checks)
    rows.append({'name':name,'check':key,'detected':True,'checks':checks})
write(folder/'results.json',{'passed':True,'rows':rows,'remote_calls':0})
print('Extended calibration passed')
