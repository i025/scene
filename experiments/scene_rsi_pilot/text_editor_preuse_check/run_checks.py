"""Two mechanical controls for the unused editor checker; zero model calls."""
from pathlib import Path
import json,subprocess,sys,time
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'backend'))
from pilot import config,read,write_json
from devices import inspection_config
from budget import guard,current
cfg=config();output=ROOT/'smoke/text_editor_checker';output.mkdir(exist_ok=True)
status=output/'status.json'
if status.exists():
    if read(status)['status']!='complete':raise RuntimeError('Existing checker smoke failed; inspect saved evidence before any rerun')
    print('Existing editor checker controls passed');raise SystemExit(0)
source=ROOT/'smoke/smoke_01';structure=read(source/'functional/scene_structure.json');targets=structure['target']['mesh_names']
size=Image.open(source/'final.png').size
code='''import bpy
for name in TARGETS:
    obj=bpy.data.objects[name]
    obj.data=obj.data.copy()
    mat=bpy.data.materials.new('checker_blue_'+name)
    mat.use_nodes=True
    mat.diffuse_color=(.02,.08,.8,1)
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.02,.08,.8,1)
    shader.inputs['Roughness'].default_value=.45
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:face.material_index=0
'''.replace('TARGETS',repr(targets))
checks=[]
for label in ['positive','negative_camera_parameter']:
    folder=output/label;folder.mkdir(exist_ok=True);write_json(folder/'targets.json',targets)
    edit=code
    if label.startswith('negative'):
        edit+='\nbpy.context.scene.camera.data.lens *= 1.1\nbpy.context.scene.render.resolution_x=127\nbpy.context.scene.cycles.samples=1\n'
    (folder/'edit.py').write_text(edit);settings,environment=inspection_config(cfg,folder);guard('render')
    write_json(folder/'render_ledger.json',{'render_attempts':1,'renders_completed':0,'purpose':'Engineering checker control; excluded from method comparison'})
    args=[cfg['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python',str(ROOT/'text_edit_worker.py'),'--','--blend',str(source/'scene.blend'),'--output',str(folder),'--settings',str(settings),'--targets',str(folder/'targets.json'),'--code',str(folder/'edit.py')]
    started=time.monotonic()
    error=None;exit_code=None
    with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
        try:
            proc=subprocess.run(args,stdout=out,stderr=err,env=environment,timeout=600)
            exit_code=proc.returncode
        except subprocess.TimeoutExpired as failure:
            error=str(failure)
    evidence=read(folder/'text_edit.json',{});ledger=read(folder/'render_ledger.json',{})
    expected=label=='positive'
    correct=exit_code==0 and evidence.get('passed') is expected and evidence.get('target_success') is True and evidence.get('non_target_preservation',{}).get('pass') is expected and ledger.get('settings',{}).get('samples')==16 and tuple(ledger.get('settings',{}).get('resolution',[]))==size
    checks.append({'control':label,'expected_edit_pass':expected,'observed_edit_pass':evidence.get('passed'),'expected_result_observed':correct,'exit_code':exit_code,'error':error,'seconds':time.monotonic()-started,'editor_cli_calls':0,'source':str(folder.relative_to(ROOT))})
    if exit_code!=0:break
result={'status':'complete' if all(c['expected_result_observed'] for c in checks) else 'failed','checks':checks,'formal':False,'model_calls':0,'note':'Mechanical engineering controls, not evidence of text-instruction editing ability. The deliberate negative camera change must fail preservation while fixed quality is restored.'}
write_json(status,result);write_json(ROOT/'ledger.json',current());print(json.dumps(result))
if result['status']!='complete':raise RuntimeError('Editor checker controls failed; no formal text editing may proceed')
