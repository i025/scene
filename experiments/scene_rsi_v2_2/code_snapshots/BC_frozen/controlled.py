"""New controlled SceneAct rooms and shared helper transfer evaluation.

Truth is written by the fixture constructor; diagnosis receives only public.json.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import inspect_blend as ib
import bpy
from mathutils import Vector
from sceneact import Scene,Asset,box,realize,set_view,area_emitter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'diagnosis'

GOOD='''def frame(camera, nominal_lens):
    camera.data.lens=nominal_lens

def size(group, nominal_scale):
    group.scale=tuple(nominal_scale)

def show(objects, visible):
    for obj in objects:obj.hide_render=not visible

def support(group, nominal_z):
    group.location.z=nominal_z

def local_material(obj, rgba):
    obj.data=obj.data.copy()
    for i,original in enumerate(list(obj.data.materials)):
        material=original.copy()
        obj.data.materials[i]=material
        material.diffuse_color=rgba
        material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba
'''


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2))


def load(path):
    spec=importlib.util.spec_from_file_location('shared_helper',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def meshes(group):return [o for o in group.children_recursive if o.type=='MESH']


def build(helper, variant, transfer=False):
    style=variant%2
    wide=(2.5 if style else 1.7)+.08*(variant//2)+(.35 if transfer else 0)
    prefix='Transfer' if transfer else 'Primary'
    scene=Scene('ControlledRoom');item=Asset(prefix+'Furniture')
    item.include('Seat',box((wide,1.5,.24),center=(0,0,1.3),color=(.15,.45,.18)))
    item.include('Back',box((wide,.20,1.4),center=(0,.65,2),color=(.15,.45,.18)))
    for i,(x,y) in enumerate([(-wide*.38,-.55),(-wide*.38,.55),(wide*.38,-.55),(wide*.38,.55)]):
        item.include('Leg'+str(i),box((.18,.18,1.18),center=(x,y,.59),color=(.15,.45,.18)))
    scene.include(prefix+'Item',item)
    scene.include('Floor',box((10,9,.2),center=(0,0,-.1),color=(.56,.53,.48)))
    scene.include('BackWall',box((10,.18,5),center=(0,4,2.4),color=(.68,.72,.77)))
    scene.include('Sideboard',box((1.2,1,1.2),center=(3,-.1,.6),color=(.15,.45,.18)))
    realize(scene)
    group=bpy.data.objects[prefix+'Item'];parts=list(group.children)
    seat=next(o for o in meshes(group) if o.parent.name=='Seat')
    other=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='Sideboard')
    # Shared shader and, in transfer, shared mesh data expose ownership errors.
    other.data.materials[0]=seat.data.materials[0]
    if transfer:other.data=seat.data
    bpy.context.scene['scene_rsi_supports']=json.dumps([{'object':next(o for o in meshes(group) if o.parent.name=='Leg0').name,'support':next(o.name for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='Floor')}])
    distance=7+.12*variant+(.6 if transfer else 0)
    camera=set_view((distance,-10,6) if not style else (-distance,-10,5.8),(.7,.2,1),lens=52)
    area_emitter((1,-4,7),power=1100,size=6)
    world=bpy.data.worlds.new('ControlledWorld');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.6,.6,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
    nominal={'lens':61+variant if transfer else 52+variant,'scale':(1.15,.9,1.05) if transfer else (1,1,1),
             'visible':True,'support_z':0.0,'rgba':(.7,.12,.04,1) if transfer else (.04,.12,.72,1)}
    helper.frame(camera,nominal['lens']);helper.size(group,nominal['scale'])
    helper.support(group,nominal['support_z']);helper.show([group,*group.children_recursive],nominal['visible'])
    bpy.context.view_layer.update();before=ib.snapshot_objects()
    helper.local_material(seat,nominal['rgba']);bpy.context.view_layer.update()
    after=ib.snapshot_objects();keep=ib.unchanged(before,after,{seat.name})
    actual_color=seat.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    edit_pass=keep['pass'] and max(abs(a-b) for a,b in zip(actual_color,nominal['rgba']))<1e-6
    structure=ib.structure()
    tests={'camera':abs(camera.data.lens-nominal['lens'])<1e-6,
           'object_parameters':max(abs(a-b) for a,b in zip(group.scale,nominal['scale']))<1e-6,
           'object_coverage':all(not o.hide_render for o in meshes(group)),
           'support_relations':abs(group.location.z-nominal['support_z'])<1e-6 and structure['structural_checks']['hierarchy_parts']['measured_pass'] is True,
           'material_edit':edit_pass}
    dependents=[o for part in parts for o in [part,*part.children_recursive] if o.type=='MESH']
    positions={o.name:o.matrix_world.translation.copy() for o in dependents}
    original_matrix=group.matrix_world.copy();delta=Vector((.25,0,0))
    moved=original_matrix.copy();moved.translation+=delta;group.matrix_world=moved
    bpy.context.view_layer.update()
    movement_errors={o.name:float((o.matrix_world.translation-positions[o.name]-delta).length) for o in dependents}
    tests['part_dependency_move']=bool(dependents) and max(movement_errors.values())<1e-5
    group.matrix_world=original_matrix;bpy.context.view_layer.update()
    return {'group':group,'parts':parts,'seat':seat,'other':other,'nominal':nominal,'structure':structure,
            'edit_observation':{'applicable':True,'measured_pass':edit_pass,'target':seat.name,'non_target':keep,
                                'meaning':'Execute current shared helper local_material; compare actual object parameters, geometry and shader values, not background pixels'},
            'part_move_observation':{'group':group.name,'normalized_intent':'temporary fixed scene-unit displacement in a synthetic scene','displacement':list(delta),'errors':movement_errors},'tests':tests}


def render(dest,name,settings,ledger):
    scene=bpy.context.scene;scene.render.resolution_x=256;scene.render.resolution_y=192;scene.render.resolution_percentage=100
    ib.configure(settings);ib.render(dest,name,ledger)


def defect(kind,variant):
    code=GOOD
    if kind=='camera':code=code.replace('camera.data.lens=nominal_lens','camera.data.lens=nominal_lens*'+('.68' if not variant else '1.4'))
    if kind=='object_parameters':code=code.replace('group.scale=tuple(nominal_scale)','group.scale=tuple(v*'+('.58' if not variant else '1.45')+' for v in nominal_scale)')
    if kind=='object_coverage':code=code.replace('obj.hide_render=not visible','obj.hide_render=visible')
    if kind=='support_relations':
        code=code.replace('group.location.z=nominal_z','group.location.z=nominal_z+.8' if not variant else 'group.children[0].parent=None\n    group.location.z=nominal_z')
    if kind=='material_edit':
        code=code.replace('obj.data=obj.data.copy()','obj.data=obj.data').replace('material=original.copy()','material=original')
    return code


def create():
    settings=json.loads((ROOT/'config.json').read_text());truth=[]
    reference_helper=OUT/'fixture_reference_evaluator_only.py';reference_helper.write_text(GOOD)
    index=0
    for kind in ['camera','object_parameters','object_coverage','support_relations','material_edit']:
        for variant in [0,1]:
            index+=1;dest=OUT/f'case{index:02d}';dest.mkdir(exist_ok=True)
            if (dest/'public.json').exists():raise FileExistsError('Preserve existing controlled fixtures')
            ledger={'render_attempts':0,'renders_completed':0,'images':[],'settings':settings}
            build(load(reference_helper),index-1);render(dest,'reference.png',settings,ledger)
            source=dest/'shared_h0.py';source.write_text(defect(kind,variant))
            state=build(load(source),index-1);render(dest,'final.png',settings,ledger)
            bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'))
            (dest/'functional').mkdir();write(dest/'functional/scene_structure.json',state['structure'])
            names=[o.name for o in [state['group'],*state['group'].children_recursive]]
            truth_objects=[] if kind=='camera' else [state['other'].name,state['other'].parent.name] if kind=='material_edit' else [state['group'].name]
            if kind=='support_relations' and variant:truth_objects+=[state['parts'][0].name]
            truth.append({'scene_id':dest.name,'fault_module':kind,'allowed_modules':['support_relations','part_dependencies'] if kind=='support_relations' and variant else [kind],
                          'allowed_related_modules':([kind,'part_dependencies','structure_and_edit_contract'] if kind=='support_relations' else
                            [kind,'structure_and_edit_contract'] if kind=='material_edit' else
                            [kind,'object_coverage_and_verification'] if kind=='object_coverage' else [kind]),
                          'allowed_object_ids':truth_objects,'related_object_ids':names,'camera_object_applicable':kind!='camera',
                          'material_actually_changed_non_targets':state['edit_observation']['non_target']['changed_fields'] if kind=='material_edit' else None,
                          'variant':index-1,'template_family':variant,'injected_source':'shared_h0.py','expected':'Reference helper contract; verify all five API behaviors and non-target invariance on independent transfer values',
                          'provided_to_M':False})
            write(dest/'public.json',{'scene_id':dest.name,'variant':index-1,'nominal_parameters':state['nominal'],
                'edit_observation':state['edit_observation'],
                'public_program':'SceneAct room construction calls frame(camera, lens), size(group, scale), support(group, support_z), show(objects, visible), local_material(target, rgba). No task-conditional dispatch.\n'+source.read_text(),
                'source_scope':'Auxiliary shared fixture H, not natural-image H0/r1-C2; explicit API contracts can make repair easy.'})
            write(dest/'render_ledger.json',ledger)
    write(OUT/'ground_truth_evaluator_only.json',truth)
    write(OUT/'creation.json',{'tasks':len(truth),'renders':sum(json.loads((p/'render_ledger.json').read_text())['renders_completed'] for p in OUT.glob('case*')),'truth_frozen_before_diagnosis':True})


def evaluate(case,method):
    settings=json.loads((ROOT/'config.json').read_text());dest=OUT/case/method
    candidate=dest/'candidate.py';truth=next(r for r in json.loads((OUT/'ground_truth_evaluator_only.json').read_text()) if r['scene_id']==case)
    variant=truth['variant'];ledger={'render_attempts':0,'renders_completed':0,'images':[],'settings':settings}
    result={'scene_id':case,'method':method,'status':'running','source':'candidate.py'}
    for transfer in [False,True]:
        key='transfer' if transfer else 'source'
        state=build(load(candidate),variant,transfer)
        result[key]={'checks':state['tests'],'all_pass':all(state['tests'].values()),'edit_observation':state['edit_observation'],'part_move_observation':state['part_move_observation']}
        render(dest,key+'_repaired.png',settings,ledger)
        bpy.ops.wm.save_as_mainfile(filepath=str(dest/(key+'_repaired.blend')))
        write(dest/(key+'_structure.json'),state['structure'])
    result['status']='completed';write(dest/'repair_evaluation.json',result);write(dest/'render_ledger.json',ledger)


def material_regression(case,method):
    dest=OUT/case;public=json.loads((dest/'public.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(dest/'scene.blend'))
    helper=load(dest/'shared_h0.py');target=bpy.data.objects[public['edit_observation']['target']]
    rgba=(.8,.2,.6,1)
    before=ib.snapshot_objects();helper.local_material(target,rgba);bpy.context.view_layer.update()
    after=ib.snapshot_objects();preserve=ib.unchanged(before,after,{target.name})
    color=target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    target_success=max(abs(a-b) for a,b in zip(color,rgba))<1e-6
    geometry=before[target.name]['vertices']==after[target.name]['vertices'] and before[target.name]['matrix_world']==after[target.name]['matrix_world']
    write(dest/method/'material_regression.json',{'applicable':True,'measured_pass':preserve['pass'] and target_success and geometry,
          'target_success':target_success,'target_geometry_preserved':geometry,
          'non_target':preserve,'target':target.name,'adapter':'Execute current shared H local_material on a temporary in-memory scene; not the safe ib.set_blue operation'})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['create','evaluate','material-regression']);parser.add_argument('--case');parser.add_argument('--method')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.action=='create':create()
    elif args.action=='evaluate':evaluate(args.case,args.method)
    else:material_regression(args.case,args.method)
