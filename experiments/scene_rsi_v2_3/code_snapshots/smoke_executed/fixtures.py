"""Evaluator-owned controlled SceneAct tasks, probes and independent scene evaluation."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import math
import random
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parent/'backend'))
import bpy
from mathutils import Matrix,Vector
from sceneact import Scene,Asset,box,area_emitter
import inspect_blend as ib

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'tasks'


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))


def load(path):
    spec=importlib.util.spec_from_file_location('sceneact.v23_candidate',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def meshes(group):return [o for o in [group,*group.children_recursive] if o.type=='MESH']


def aabb(objects):
    points=[o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]} if points else None


def config(variant,transfer=False):
    furniture='Desk' if variant==0 else 'Bench'
    prefix='Novel' if transfer else 'Study'
    return {'template':variant,'target':prefix+furniture,'peer':prefix+'Storage','screen':prefix+'Panel',
            'width':(2.2 if variant==0 else 3.1)+(.47 if transfer else 0),
            'depth':1.3 if variant==0 else 1.7,'height':1.45 if variant==0 else 1.7,
            'offset':[.45 if transfer else -.8,1.8 if variant else .4,0],
            'angle':(-17 if transfer else 12)*(1 if variant else -1),'root_scale':[1.12,.9,1.08] if transfer else [1,1,1],
            'lens':59 if transfer else 46,'sensor':42 if transfer else 48,
            'camera':[8 if variant==0 else -8,-12,7 if transfer else 6],
            'share_mesh':True,'rgba':[.1,.35,.7,1],
            'final_move':[.45,-.3,0] if transfer else [.3,.1,0],
            'panel_alpha':.63 if transfer else .72,'peer_position':[3.6,1.7,.7]}


def build(H,spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    room=Scene('Room');item=Asset(spec['target']);w=spec['width'];d=spec['depth'];h=spec['height']
    item.include('Top',box((w,d,.22),center=(0,0,h),color=(.32,.48,.22)))
    for index,(x,y) in enumerate([(-w*.39,-d*.36),(-w*.39,d*.36),(w*.39,-d*.36),(w*.39,d*.36)]):
        item.include('Support'+str(index),box((.18,.18,h-.11),center=(x,y,(h-.11)/2),color=(.32,.48,.22)))
    if spec['template']:
        item.include('Back',box((w,.16,.85),center=(0,d*.44,h+.5),color=(.32,.48,.22)))
    item.resize(spec['root_scale'],pivot=(0,0,0));item.turn(euler=(0,0,spec['angle']),pivot=(0,0,0));item.move(spec['offset'])
    room.include(spec['target'],item)
    room.include('Floor',box((11,10,.22),center=(0,1,-.11),color=(.61,.57,.51)))
    room.include('Wall',box((11,.16,5),center=(0,5,2.4),color=(.7,.73,.77)))
    room.include(spec['peer'],box((1.3,1.2,1.4),center=spec['peer_position'],color=(.32,.48,.22)))
    room.include(spec['screen'],box((1.3,.15,1.8),center=(-.6,-.8,1.05),color=(.6,.22,.12),opacity=spec['panel_alpha']))
    room.include('Accent',box((2.0,.12,1.1),center=(1.4,4.7,2.7),color=(.2,.45,.65),opacity=spec['panel_alpha']))
    for node in room.traverse():
        for slot,child in node.members.items():child.name=slot
    H.SceneCompiler().emit(room)
    bpy.context.view_layer.update()
    group=bpy.data.objects[spec['target']]
    panel=bpy.data.objects[spec['screen']]
    H.set_render_visibility(panel,False)
    floor=bpy.data.objects['Floor.001']
    H.support_on(group,floor)
    camera=H.set_view(spec['camera'],(.3,.7,1),lens=spec['lens'],sensor=spec['sensor'])
    area_emitter((1,-5,8),power=1300,size=6)
    world=bpy.data.worlds.new('RoomWorld');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.65,.65,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.55;bpy.context.scene.world=world
    expected_parts=[spec['target']+'/'+key for key in item.members]
    # Public plan identifies groups, independent of whether a damaged emitter parented them correctly.
    parts=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Asset')]
    top_marker=bpy.data.objects.get('Top')
    top=bpy.data.objects.get('Top.001')
    peer_marker=bpy.data.objects[spec['peer']]
    peer=bpy.data.objects.get(spec['peer']+'.001')
    if top and peer:
        peer.data=top.data if spec['share_mesh'] else peer.data
        if not spec['share_mesh']:peer.data.materials[0]=top.data.materials[0]
        before=ib.snapshot_objects();H.edit_surface(top,spec['rgba']);bpy.context.view_layer.update()
        after=ib.snapshot_objects();preservation=ib.unchanged(before,after,{top.name})
        actual=list(top.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
        edit={'applicable':True,'measured_pass':preservation['pass'] and max(abs(a-b) for a,b in zip(actual,spec['rgba']))<1e-5,'non_target':preservation,'target':top.name}
    else:edit={'applicable':False,'measured_pass':None,'non_target':None,'target':None}
    # Move the group after compilation; incorrectly parented geometry visibly stays behind.
    matrix=group.matrix_world.copy();matrix.translation+=Vector(spec['final_move']);group.matrix_world=matrix
    bpy.context.view_layer.update()
    return {'group':group,'top':top,'peer':peer,'floor':floor,'camera':camera,'edit':edit,
            'input_scene':room,'expected_parts':expected_parts,'public_spec':spec}


def signature(state):
    objects={o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':ib.matrix_values(o.matrix_world),
             'bounds':aabb([o]) if o.type=='MESH' else None,'visible':not o.hide_render,
             'projected':ib.projected_box(o),'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in bpy.context.scene.objects}
    return {'objects':objects,'camera':{'lens':state['camera'].data.lens,'sensor':state['camera'].data.sensor_width},
            'edit':state['edit']}


def render(dest,name):
    settings=json.loads((ROOT/'config.json').read_text())
    ib.configure(settings)
    ledger=json.loads((dest/'render_ledger.json').read_text()) if (dest/'render_ledger.json').exists() else {'render_attempts':0,'renders_completed':0,'images':[]}
    ib.render(dest,name,ledger)
    write(dest/'actual_device.json',{'device':'CPU','threads':2,'engine':'CYCLES','samples':16,'resolution':[256,192]})


def inject(index,source):
    edits=[
        ('set_view','data.lens,data.sensor_width=lens,sensor','data.lens,data.sensor_width=lens,36'),
        ('SceneCompiler.emit.geometry','world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()',
         'world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()\n            world=world @ Matrix.Diagonal((.76,.76,.76,1))'),
        ('SceneCompiler.emit.position','world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()',
         'world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()\n            world.translation.y *= 1.45'),
        ('SceneCompiler.emit.geometry','world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()',
         'world=Matrix(node.geometry_frame.tolist()) @ obj.matrix_world.copy()\n            world=world @ Matrix.Diagonal((1.25,.74,1,1))'),
        ('set_render_visibility','for obj in [group, *group.children_recursive]:','for obj in [group]:'),
        ('SceneCompiler.emit.coverage','if node.solid is not None:','if node.solid is not None and node.finish.rgba[3] >= 1.0:'),
        ('SceneCompiler.emit.parent','obj.parent=marker','obj.parent=parent'),
        ('support_on','bottom = min((o.matrix_world @ Vector(v)).z for o in meshes for v in o.bound_box)',
         'bottom = min(Vector(v).z for o in meshes for v in o.bound_box)'),
        ('prepare_edit_mesh','obj.data = obj.data.copy()','obj.data = obj.data'),
        ('edit_surface','material = original.copy()','material = original'),
    ]
    module,old,new=edits[index];assert source.count(old)==1
    return source.replace(old,new),module,old,new


def create(smoke=False):
    source=(ROOT/'fixtures/reference_renderer_evaluator_only.py').read_text()
    indices=[0,8] if smoke else [4,1,8,2,6,0,9,5,7,3]
    truth=[]
    for order,index in enumerate(indices):
        name=('smoke' if smoke else 'task')+str(order+1).zfill(2)
        dest=OUT/name;dest.mkdir(parents=True,exist_ok=True)
        if (dest/'public.json').exists():continue
        broken,module,old,new=inject(index,source);(dest/'H0.py').write_text(broken)
        spec=config(index%2,False)
        ref=build(load(ROOT/'fixtures/reference_renderer_evaluator_only.py'),spec)
        ref_sig=signature(ref);render(dest,'reference.png')
        write(dest/'reference_signature_evaluator_only.json',ref_sig)
        damaged=build(load(dest/'H0.py'),spec);damaged_sig=signature(damaged)
        render(dest,'final.png');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'))
        write(dest/'public.json',{'scene_id':name,'source_scope':'Actual SceneAct Blender compiler plus visibility/support/edit interfaces; controlled scene-description-to-Blender program repair, not natural-image end-to-end H',
             'spec':spec,'objects':damaged_sig['objects'],'camera':damaged_sig['camera'],'edit':damaged_sig['edit'],
             'requirements':'Compile a reusable SceneAct scene plan, retain intended world transforms and visibility, support composite furniture, preserve dependencies under group movement and local edits. Use images as desired appearance; investigate any shared module.',
             'valid_object_ids':list(damaged_sig['objects'])})
        truth.append({'scene_id':name,'family':index//2,'template':index%2,'fault_index':index,'exact_module':module,
                      'related_modules':{'SceneCompiler.emit.geometry':['SceneCompiler.emit.geometry','SceneCompiler.emit.position'],
                        'SceneCompiler.emit.position':['SceneCompiler.emit.position','SceneCompiler.emit.geometry'],
                        'SceneCompiler.emit.coverage':['SceneCompiler.emit.coverage','set_render_visibility'],
                        'set_render_visibility':['set_render_visibility','SceneCompiler.emit.coverage'],
                        'support_on':['support_on','SceneCompiler.emit.parent'],
                        'SceneCompiler.emit.parent':['SceneCompiler.emit.parent','support_on']}.get(module,[module]),
                      'object_ids':([spec['target'],'Top',damaged_sig['edit']['target']] if index in [1,2,3,6,7,8,9] else [spec['screen']] if index==4 else ['Accent',spec['screen']] if index==5 else []),
                      'object_applicable':index!=0,'injection':{'before':old,'after':new},'labels_supplied_to_models':False})
    write(ROOT/'configs'/('smoke_truth.json' if smoke else 'truth_evaluator_only.json'),truth)


def compare(actual,reference):
    names=reference['objects'];got=actual['objects']
    mesh_names=[n for n,o in names.items() if o['type']=='MESH']
    coverage=all(n in got and got[n]['type']=='MESH' for n in mesh_names)
    transforms=coverage and all(max(abs(got[n]['matrix'][i][j]-names[n]['matrix'][i][j]) for i in range(4) for j in range(4))<1e-4 for n in mesh_names)
    geometry=coverage and all(max(abs(got[n]['bounds'][k][i]-names[n]['bounds'][k][i]) for i in range(3) for k in ['min','max'])<1e-4 for n in mesh_names)
    parenting=coverage and all(got[n]['parent']==names[n]['parent'] for n in mesh_names)
    visibility=coverage and all(got[n]['visible']==names[n]['visible'] for n in mesh_names)
    camera=all(abs(actual['camera'][k]-reference['camera'][k])<1e-5 for k in ['lens','sensor'])
    material=actual['edit']['applicable'] and actual['edit']['measured_pass'] is True
    return {'camera':camera,'geometry':geometry,'transforms':transforms,'coverage':coverage,'parenting':parenting,'visibility':visibility,'material':material}


def check_case(case,candidate,dest):
    public=json.loads((OUT/case/'public.json').read_text());spec=public['spec'];H=load(candidate)
    result={}
    for split in ['source','transfer']:
        selected=spec if split=='source' else config(1-spec['template'],True)
        state=build(H,selected);sig=signature(state)
        write(dest/(split+'_signature.json'),sig)
        render(dest,split+'_repaired.png');bpy.ops.wm.save_as_mainfile(filepath=str(dest/(split+'_repaired.blend')))
        good=build(load(ROOT/'fixtures/reference_renderer_evaluator_only.py'),selected);ref=signature(good)
        checks=compare(sig,ref)
        baseline=build(load(OUT/case/'H0.py'),selected);basechecks=compare(signature(baseline),ref)
        regression=[k for k in checks if basechecks[k] and not checks[k]]
        fault_fixed=all(checks[k] for k in checks if not basechecks[k])
        result[split]={'checks':checks,'gates':{k:{'required':True,'applicable':True,'measured_pass':v,'gate_pass':v} for k,v in checks.items()},
                       'all_pass':all(checks.values()),'fault_fixed':fault_fixed,'new_regressions':regression,'baseline_checks':basechecks}
    result['effective_shared_repair']=result['source']['all_pass'] and result['transfer']['all_pass']
    result['transfer_repair']=result['transfer']['all_pass']
    result['regression']=bool(result['source']['new_regressions'] or result['transfer']['new_regressions'])
    write(dest/'evaluation.json',result)


def run_probe(case,Hpath,request,dest):
    public=json.loads((OUT/case/'public.json').read_text());spec=copy.deepcopy(public['spec'])
    H=load(Hpath);tool=request['probe'];target_id=request['object_id']
    if tool=='geometry_replay':spec['root_scale']=[1.17,.82,1.09]
    if tool=='position_replay':spec['offset']=[1.7,2.6,0]
    state=build(H,spec)
    target=bpy.data.objects.get(target_id)
    if tool=='camera_calibration':
        cam=H.set_view(spec['camera'],(.3,.7,1),lens=spec['lens']*1.2,sensor=spec['sensor']*.85)
        outcome=abs(cam.data.sensor_width-spec['sensor']*.85)/(spec['sensor']*.85)
        details={'requested_lens':spec['lens']*1.2,'actual_lens':cam.data.lens,'requested_sensor':spec['sensor']*.85,'actual_sensor':cam.data.sensor_width}
        bpy.context.scene.camera=cam
    elif tool in ['geometry_replay','position_replay']:
        # Compare current compiler outputs with public SceneAct input frames, not an unexposed correct renderer.
        errors=[]
        for node in state['input_scene'].traverse():
            if node.solid is None:continue
            marker=bpy.data.objects.get(node.name)
            candidates=[o for o in marker.children if o.type=='MESH'] if marker else []
            if not candidates:continue
            obj=candidates[0]
            if tool=='position_replay':
                delta=obj.matrix_world.translation-(Matrix(node.geometry_frame.tolist()) @ Vector(node.solid.origin))
                if node in list(state['input_scene'].members[spec['target']].traverse()):delta-=Vector(spec['final_move'])
                outcome_i=abs(delta.y)/max(spec['width'],1)
            else:
                # Emitted mesh local dimensions vs canonical primitive dimensions from the input node.
                canonical=node.solid
                if type(canonical).__name__!='Brick':continue
                from sceneact.kernel import affine
                nominal=Matrix(node.geometry_frame.tolist())
                actual=obj.matrix_world.to_3x3();expected=nominal.to_3x3()
                outcome_i=max(abs(actual.col[j].length-expected.col[j].length*canonical.dimensions[j]) for j in range(3))
            errors.append(float(outcome_i))
        outcome=max(errors) if errors else None;details={'public_frame_errors':errors,'target_requested':target_id,'scope':'all emitted public plan primitives; group IDs and mesh membership retained'}
    elif tool=='visibility_isolation':
        panel=target
        if panel is None:raise ValueError('Visibility probe requires a real selected object')
        emitted=meshes(panel);H.set_render_visibility(panel,False);bpy.context.view_layer.update()
        hidden_error=sum(not o.hide_render for o in emitted)/len(emitted) if emitted else 1.0
        H.set_render_visibility(panel,True);bpy.context.view_layer.update()
        outcome=2.0 if not emitted else hidden_error+sum(o.hide_render for o in emitted)/len(emitted)
        for o in bpy.context.scene.objects:
            if o.type=='MESH' and o not in emitted and o.parent and o.parent.name not in ['Floor','Wall']:o.hide_render=True
        details={'requested_group':panel.name,'emitted_mesh_count':len(emitted),'hidden_mesh_count':sum(o.hide_render for o in emitted),'interpretation':'Missing emission and visibility remain competing explanations if same outcome.'}
    elif tool=='support_relation':
        group=target
        if group is None:raise ValueError('Support probe requires a selected object')
        matrix=group.matrix_world.copy();matrix.translation.z+=.4;group.matrix_world=matrix;bpy.context.view_layer.update()
        H.support_on(group,state['floor']);box=aabb(meshes(group));floor=aabb([state['floor']]);outcome=abs(box['min'][2]-floor['max'][2])/spec['height'] if box else None
        details={'normalized_gap_after_H_support':outcome,'approximation':'AABB vertical support contact, no mesh collision claim'}
    elif tool=='dependency_move':
        group=target
        if group is None:raise ValueError('Dependency probe requires a selected object')
        members=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.parent and o.parent.name in ['Top','Support0','Support1','Support2','Support3','Back'] or o.parent==group)]
        before={o.name:o.matrix_world.translation.copy() for o in members};matrix=group.matrix_world.copy();delta=Vector((.4,.1,0));matrix.translation+=delta;group.matrix_world=matrix;bpy.context.view_layer.update()
        errors={o.name:(o.matrix_world.translation-before[o.name]-delta).length for o in members};parent_errors=[o.name for o in members if o.parent and o.parent.name!=o.name.rsplit('.',1)[0]]
        outcome=max(sum(v>1e-4 for v in errors.values()),len(parent_errors))/len(errors) if errors else None
        details={'part_motion_errors':errors,'parent_contract_errors':parent_errors,'displacement':list(delta),'applicability':bool(members)}
    else:
        if target and target.type!='MESH':
            eligible=meshes(target);target=eligible[0] if len(eligible)==1 else None
        if target:
            before=ib.snapshot_objects();H.edit_surface(target,(.8,.16,.3,1));bpy.context.view_layer.update();after=ib.snapshot_objects();preserve=ib.unchanged(before,after,{target.name})
            outcome=float(len(preserve['changed_fields']));details={'target':target.name,'non_target':preserve,'scope':'Execute current H.edit_surface, not a safe external edit'}
        else:outcome=None;details={'applicable':False,'reason':'No emitted editable top mesh'}
    render(dest,'probe.png');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'probe.blend'))
    write(dest/'measurement.json',{'outcome':outcome,'details':details,'requested_object_id':target_id,'tool':tool,'numeric_not_unique_causal_proof':True})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['create','smoke-create','evaluate','probe']);parser.add_argument('--case');parser.add_argument('--candidate',type=Path);parser.add_argument('--dest',type=Path);parser.add_argument('--request',type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.action in ['create','smoke-create']:create(args.action=='smoke-create')
    elif args.action=='evaluate':check_case(args.case,args.candidate,args.dest)
    else:run_probe(args.case,args.candidate,json.loads(args.request.read_text()),args.dest)
