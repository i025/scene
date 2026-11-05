"""Zero-render execution on changed names, nominal values and shared data."""
from pathlib import Path
import sys,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
import bpy
def load(path):
    spec=importlib.util.spec_from_file_location('helpers',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def measure(module):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.object.camera_add();camera=bpy.context.object
    module.frame(camera,61);camera_pass=abs(camera.data.lens-61)<1e-6
    bpy.ops.mesh.primitive_cube_add();target=bpy.context.object;target.name='Target_reordered'
    module.size(target,(1.2,.8,2.));scale_pass=max(abs(a-b) for a,b in zip(target.scale,(1.2,.8,2.)))<1e-6
    module.show([target],True);visible_pass=target.hide_render is False
    module.support(target,3.25);support_pass=abs(target.location.z-3.25)<1e-6
    material=bpy.data.materials.new('SharedDifferent');material.use_nodes=True;material.diffuse_color=(.7,.2,.1,1)
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.7,.2,.1,1)
    target.data.materials.append(material);other=target.copy();other.data=target.data;bpy.context.collection.objects.link(other)
    before=list(other.data.materials[0].diffuse_color)
    module.local_material(target,(.02,.08,.8,1))
    material_pass=(max(abs(a-b) for a,b in zip(target.data.materials[0].diffuse_color,(.02,.08,.8,1)))<1e-6 and list(other.data.materials[0].diffuse_color)==before)
    return dict(camera=camera_pass,scale=scale_pass,visibility=visible_pass,support=support_pass,material_non_target=material_pass)
results={'fixture_H0':measure(load(ROOT/'tests/fixture_h0.py'))}
for method in ['fixed_heuristic','scene_rsi_v2_1']:
    p=ROOT/'tests/diagnosis'/('repair_'+method)/'candidate.py'
    if p.exists():results[method]=measure(load(p))
(ROOT/'tests/diagnosis/shared_patch_transfer.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
