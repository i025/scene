"""Fixed evaluator for one tool-free editor response, separate from mechanical edits."""
import argparse
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inspect_blend import reload_blend,configure,snapshot_objects,unchanged,blue_success,render,write_json,json_number


def scalar_parameters(value):
    result={}
    for prop in value.bl_rna.properties:
        if prop.is_readonly:continue
        item=getattr(value,prop.identifier)
        if prop.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
            result[prop.identifier]=json_number(item)
        elif prop.type=='POINTER' and (item is None or isinstance(item,bpy.types.ID)):
            result[prop.identifier]=item.name if item is not None else None
    return result


def node_state(tree):
    if tree is None:return None
    nodes=[]
    for node in sorted(tree.nodes,key=lambda n:n.name):
        item={'name':node.name,'type':node.bl_idname,'parameters':scalar_parameters(node),
              'inputs':{socket.identifier:json_number(socket.default_value) for socket in node.inputs if hasattr(socket,'default_value')},
              'outputs':{socket.identifier:json_number(socket.default_value) for socket in node.outputs if hasattr(socket,'default_value')}}
        if hasattr(node,'color_ramp'):item['color_ramp']=[[e.position,list(e.color)] for e in node.color_ramp.elements]
        nodes.append(item)
    return {'nodes':nodes,'links':sorted([link.from_node.name,link.from_socket.identifier,link.to_node.name,link.to_socket.identifier] for link in tree.links)}


def edit_snapshot():
    result=snapshot_objects()
    for obj in bpy.context.scene.objects:
        record=result[obj.name]
        record.update(type=obj.type,hide_render=obj.hide_render,hide_viewport=obj.hide_viewport,
                      data_name=obj.data.name if obj.data else None,
                      modifiers=[{'type':m.type,'parameters':scalar_parameters(m)} for m in obj.modifiers],
                      constraints=[{'type':c.type,'parameters':scalar_parameters(c)} for c in obj.constraints],
                      material_nodes=[node_state(slot.material.node_tree) if slot.material else None for slot in obj.material_slots])
        if obj.type=='MESH':
            record.update(edges=[list(edge.vertices) for edge in obj.data.edges],
                          faces=[list(face.vertices) for face in obj.data.polygons],
                          smooth_faces=[face.use_smooth for face in obj.data.polygons],
                          polygon_material_indices=[face.material_index for face in obj.data.polygons])
        elif obj.type in {'CAMERA','LIGHT'}:
            record['data_parameters']=scalar_parameters(obj.data)
            if obj.type=='LIGHT':record['light_nodes']=node_state(obj.data.node_tree)
    return result


def scene_state():
    scene=bpy.context.scene;world=scene.world
    return {'active_camera':scene.camera.name if scene.camera else None,
            'world_name':world.name if world else None,
            'world_parameters':scalar_parameters(world) if world else None,
            'world_nodes':node_state(world.node_tree) if world else None}


p=argparse.ArgumentParser();p.add_argument('--blend',type=Path);p.add_argument('--output',type=Path);p.add_argument('--settings',type=Path);p.add_argument('--targets',type=Path);p.add_argument('--code',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.settings.read_text());a.output.mkdir(exist_ok=True)
reload_blend(a.blend,cfg)
# Preserve the submitted dimensions even if the editor tries to change them.
cfg['render'].update(width=bpy.context.scene.render.resolution_x,height=bpy.context.scene.render.resolution_y)
before=edit_snapshot();global_before=scene_state();targets=json.loads(a.targets.read_text())
exec(compile(a.code.read_text(),str(a.code),'exec'),{'__name__':'__text_edit__'})
bpy.context.view_layer.update();after=edit_snapshot();non=unchanged(before,after,set(targets))
non['comparison']='Exact object transforms/vertices/topology/materials/node parameters/parent/modifier/constraint/scalar camera-light parameters; no hashes. Not a proof about unmeasured animation, drivers or nested shader-group internals.'
allowed_material_fields={'materials','material_nodes','data_name','polygon_material_indices'}
geometry=all(all(value==after.get(name,{}).get(field) for field,value in before[name].items() if field not in allowed_material_fields) for name in targets)
global_preserved=global_before==scene_state()
success=blue_success(targets)
# Defaults on a linked color socket do not change the rendered material.
if success:
    for name in targets:
        for slot in bpy.data.objects[name].material_slots:
            output=next((n for n in slot.material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
            links=list(output.inputs['Surface'].links) if output else []
            shader=links[0].from_node if len(links)==1 else None
            success &= bool(shader and shader.type=='BSDF_PRINCIPLED' and not shader.inputs['Base Color'].is_linked and not shader.inputs['Roughness'].is_linked and abs(shader.inputs['Roughness'].default_value-0.45)<1e-6)
# The fixed external renderer owns quality, independent of generated editor code.
final_settings=configure(cfg)
ledger={'render_attempts':0,'renders_completed':0,'images':[],'settings':final_settings,'device_mapping':json.loads((a.output/'actual_device.json').read_text())};render(a.output,'after.png',ledger)
bpy.ops.wm.save_as_mainfile(filepath=str(a.output/'edited.blend'))
cli_edit=(a.output/'editor_call/session.json').exists()
write_json(a.output/'text_edit.json',{'test_type':'fixed_sol_text_instruction_editing' if cli_edit else 'checker_engineering_smoke','checker_version':'preuse_v2_parameters_topology','applicable':True,'passed':success and geometry and non['pass'] and global_preserved,'target_success':success,'target_geometry_preserved':geometry,'target_dependencies_and_visibility_preserved':geometry,'non_target_preservation':non,'scene_camera_world_preserved':global_preserved,'target_material_edit_exceptions':sorted(allowed_material_fields),'fixed_render_quality_reapplied':True,'targets':targets,'editor_calls':int(cli_edit),'repair_calls':0,'render_attempts':1})
