"""Fixed evaluator for one tool-free editor response, separate from mechanical edits."""
import argparse
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inspect_blend import reload_blend,snapshot_objects,unchanged,blue_success,render,write_json
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path);p.add_argument('--output',type=Path);p.add_argument('--settings',type=Path);p.add_argument('--targets',type=Path);p.add_argument('--code',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.settings.read_text());a.output.mkdir(exist_ok=True)
reload_blend(a.blend,cfg);before=snapshot_objects();targets=json.loads(a.targets.read_text())
exec(compile(a.code.read_text(),str(a.code),'exec'),{'__name__':'__text_edit__'})
bpy.context.view_layer.update();after=snapshot_objects();non=unchanged(before,after,set(targets))
geometry=all(before[n]['vertices']==after.get(n,{}).get('vertices') and before[n]['matrix_world']==after.get(n,{}).get('matrix_world') for n in targets)
success=blue_success(targets)
# Defaults on a linked color socket do not change the rendered material.
if success:
    for name in targets:
        for slot in bpy.data.objects[name].material_slots:
            output=next((n for n in slot.material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
            links=list(output.inputs['Surface'].links) if output else []
            shader=links[0].from_node if len(links)==1 else None
            success &= bool(shader and shader.type=='BSDF_PRINCIPLED' and not shader.inputs['Base Color'].is_linked and not shader.inputs['Roughness'].is_linked and abs(shader.inputs['Roughness'].default_value-0.45)<1e-6)
ledger={'render_attempts':0,'renders_completed':0,'images':[],'device_mapping':json.loads((a.output/'actual_device.json').read_text())};render(a.output,'after.png',ledger)
bpy.ops.wm.save_as_mainfile(filepath=str(a.output/'edited.blend'))
write_json(a.output/'text_edit.json',{'test_type':'fixed_sol_text_instruction_editing','applicable':True,'passed':success and geometry and non['pass'],'target_success':success,'target_geometry_preserved':geometry,'non_target_preservation':non,'targets':targets,'editor_calls':1,'repair_calls':0,'render_attempts':1})
