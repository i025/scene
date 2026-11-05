"""Known camera/scale/visibility/support/edit errors. Labels withheld from M."""
from pathlib import Path
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import bpy
from mathutils import Vector
import inspect_blend as ib

OUT=ROOT/'tests/diagnosis';OUT.mkdir(exist_ok=True)
settings=json.loads((ROOT/'config.json').read_text());settings['render'].update(samples=4)
(OUT/'fixture_settings.json').write_text(json.dumps(settings))
def cube(name,xyz,size,material,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(material);o.parent=parent;return o
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);return m
def build():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    grey=material('Grey',(.5,.5,.5));red=material('Red',(.7,.08,.04));green=material('Green',(.05,.5,.13))
    floor=cube('A_floor',(0,0,-.1),(9,9,.2),grey)
    group=bpy.data.objects.new('Z_Chair',None);bpy.context.collection.objects.link(group)
    seat=cube('ChairSeat',(0,0,1.3),(1.7,1.6,.25),red,group)
    back=cube('ChairBack',(0,.7,2.2),(1.7,.2,1.8),red,group)
    children=[seat,back]
    for x in [-.65,.65]:
        for y in [-.6,.6]:children.append(cube('ChairLeg',(x,y,.6),(.16,.16,1.2),red,group))
    group['scene_rsi_expected_children']=json.dumps([o.name for o in children])
    table=cube('B_Table',(2.4,1,.65),(1,1,1.3),green)
    bpy.context.scene['scene_rsi_supports']=json.dumps([{'object':children[2].name,'support':floor.name}])
    bpy.ops.object.camera_add(location=(6,-9,6));camera=bpy.context.object;camera.name='Camera';camera.data.lens=48
    camera.rotation_euler=(Vector((.4,.3,1))-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type='AREA',location=(1,-3,7));bpy.context.object.data.energy=900;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=6
    bpy.context.scene.world=bpy.data.worlds.new('FixtureWorld');bpy.context.scene.world.use_nodes=True;bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.6,.6,1)
    bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    bpy.context.scene.render.resolution_x=240;bpy.context.scene.render.resolution_y=180;bpy.context.scene.render.resolution_percentage=100
    ib.configure(settings);bpy.context.view_layer.update()
    return group,children,table
truth=[]
for index,kind in enumerate(['camera','scale','visibility','support','material'],1):
    dest=OUT/f'case{index:02d}';dest.mkdir(exist_ok=True)
    group,children,table=build();ledger={'render_attempts':0,'renders_completed':0,'images':[],'settings':settings}
    ib.render(dest,'reference.png',ledger)
    before=ib.snapshot_objects()
    if kind=='camera':bpy.context.scene.camera.data.lens*=.65
    if kind=='scale':group.scale*=.55
    if kind=='visibility':
        for o in [group,*children]:o.hide_render=True
    if kind=='support':
        for o in children:o.location.z+=.9
    if kind=='material':
        children[0].data.materials[0]=table.data.materials[0]
        children[0].data.materials[0].diffuse_color=(.02,.08,.8,1)
        children[0].data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.02,.08,.8,1)
    bpy.context.view_layer.update();ib.render(dest,'final.png',ledger)
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'))
    (dest/'functional').mkdir(exist_ok=True);(dest/'functional/scene_structure.json').write_text(json.dumps(ib.structure()))
    after=ib.snapshot_objects()
    edit=ib.unchanged(before,after,{children[0].name}) if kind=='material' else None
    truth.append({'scene_id':dest.name,'module':{'camera':'camera','scale':'object_parameters','visibility':'object_coverage','support':'support_relations','material':'material_edit'}[kind],
                  'object_id':None if kind=='camera' else 'B_Table' if kind=='material' else group.name,
                  'related_object_ids':[o.name for o in children]+[group.name] if kind!='camera' else [],
                  'non_target_changed':edit,'fault':kind,'provided_to_M':False})
    (dest/'render_ledger.json').write_text(json.dumps(ledger))
(OUT/'ground_truth_evaluator_only.json').write_text(json.dumps(truth,indent=2))
print('DIAGNOSTIC_FIXTURES_5_READY')
