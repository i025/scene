import json
import os
from pathlib import Path
import sys
sys.path.insert(0, '${PROJECT_ROOT}/outputs/stagewise_teaching_student_selfcheck_pilot')
sys.path.insert(0, '${PROJECT_ROOT}/outputs/stagewise_teaching_student_selfcheck_pilot/backend')
import bpy
from incremental_blender import snapshot
from render import render_scene
from telemetry import event
folder = Path('${PROJECT_ROOT}/outputs/stagewise_teaching_student_selfcheck_pilot/preparation/fixture/incremental')
event('scene_load_started', parent_checkpoint=str(folder / 'scene.blend'))
bpy.ops.wm.open_mainfile(filepath=str(folder / 'scene.blend'))
event('scene_load_completed')
actual = snapshot(bpy.context.scene)
(folder / 'reopened_inventory.json').write_text(json.dumps(actual, indent=2))
expected = json.loads((folder / 'scene_inventory.json').read_text())['after']
assert set(actual['objects']) == set(expected['objects'])
cube_id = 'obj_00005'
assert actual['objects'][cube_id]['name'] == 'red_cube_geometry'
assert abs(actual['objects'][cube_id]['matrix_world'][0][3] - .75) < 1e-6
assert any(value['name'] == 'blue_block_geometry' for value in actual['objects'].values())
render_scene(folder, json.loads((folder / 'render_settings.json').read_text()))
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
