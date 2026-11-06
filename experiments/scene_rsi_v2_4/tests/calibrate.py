"""Known valid/broken Blender fixtures, no remote model calls."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import bpy
import inspect_blend as ib
from regression import geometric_checks,execute_test,gate

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def cube(name,loc,scale):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;return o
root=bpy.data.objects.new('Root',None);bpy.context.collection.objects.link(root)
group=bpy.data.objects.new('Assembly',None);bpy.context.collection.objects.link(group);group.parent=root
part=cube('Z_fault_target',(0,0,1.5),(1,1,1));part.parent=group
other=cube('A_good',(3,0,.5),(1,1,1));other.parent=group
support=cube('Support',(0,0,.5),(2,2,1))
group['scene_rsi_expected_children']=json.dumps([part.name,other.name])
bpy.context.scene['scene_rsi_supports']=json.dumps([dict(object=part.name,support=support.name)])
bpy.context.view_layer.update()
records={};good=geometric_checks();assert good['hierarchy_parts']['measured_pass'];assert good['known_support']['measured_pass'];records['correct']=good
group['scene_rsi_expected_children']=json.dumps([part.name,other.name,'Missing_required_part']);missing=geometric_checks();assert missing['hierarchy_parts']['measured_pass'] is False;records['missing_declared_part']=missing
group['scene_rsi_expected_children']=json.dumps([part.name,other.name])
part.parent=None;bpy.context.view_layer.update();bad=geometric_checks();assert bad['hierarchy_parts']['measured_pass'] is False;records['detached']=bad
part.parent=group;part.location.z+=2;bpy.context.view_layer.update();bad=geometric_checks();assert bad['known_support']['measured_pass'] is False;records['broken_support']=bad
part.location.z-=2;bpy.context.view_layer.update()
material=bpy.data.materials.new('Shared');material.diffuse_color=(.2,.3,.4,1);part.data.materials.append(material);other.data.materials.append(material)
before=ib.snapshot_objects();material.diffuse_color=(0,0,1,1);after=ib.snapshot_objects();unsafe=ib.unchanged(before,after,{part.name});assert unsafe['pass'] is False;records['shared_material_bad_edit']=unsafe
safe=execute_test('material_preservation');assert safe['measured_pass'];records['independent_local_edit']=safe
move=execute_test('composite_move');assert move['measured_pass'];records['correct_group_move']=move
# Distinct overlapping triangle surfaces, not merely touching AABBs.
intruder=cube('Intruder',(0.4,0.2,part.matrix_world.translation.z),(1,1,1));bpy.context.view_layer.update();over=geometric_checks();assert over['mesh_intersection']['crossings'];records['triangle_crossing']=over
bpy.data.objects.remove(intruder,do_unlink=True)
bpy.ops.object.camera_add(location=(6,-8,6));camera=bpy.context.object;bpy.context.scene.camera=camera
camera.rotation_euler=((part.matrix_world.translation-camera.location).to_track_quat('-Z','Y')).to_euler()
bpy.context.scene.render.resolution_x=64;bpy.context.scene.render.resolution_y=64
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tests/fixture.blend'))
(ROOT/'tests/calibration.json').write_text(json.dumps(records,indent=2))
print('CALIBRATION_PASS')
