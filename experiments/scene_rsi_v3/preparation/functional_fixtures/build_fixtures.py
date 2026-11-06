"""Engineering calibration scenes with known defects; no language model calls."""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))
import inspect_blend as ib
from budget import guard
from regression import geometric_checks
from render import render_scene

OUT = Path(__file__).parent
SETTINGS = json.loads((OUT / 'settings.json').read_text())


def cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = color
    return mat


def base_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene['scene_rsi_supports'] = json.dumps([
        {'object': 'Z_target_part', 'support': 'Support'}])
    root = bpy.data.objects.new('Root', None)
    scene.collection.objects.link(root)
    group = bpy.data.objects.new('Assembly', None)
    scene.collection.objects.link(group)
    group.parent = root
    shared = material('Shared_orange', (0.65, 0.22, 0.05, 1))
    gray = material('Support_gray', (0.22, 0.28, 0.32, 1))
    part = cube('Z_target_part', (0, 0, 1.5), (1, 1, 1), shared)
    other = cube('A_unrelated_part', (3, 0, 1.5), (1, 1, 1), shared)
    part.parent = group
    other.parent = group
    support = cube('Support', (0, 0, 0.5), (2, 2, 1), gray)
    group['scene_rsi_expected_children'] = json.dumps([part.name, other.name])
    bpy.ops.object.camera_add(location=(7, -10, 7))
    camera = bpy.context.object
    camera.name = 'Fixture_camera'
    camera.rotation_euler = (Vector((1.2, 0, 1.4)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 7
    scene.camera = camera
    bpy.ops.object.light_add(type='AREA', location=(0, -4, 7))
    light = bpy.context.object
    light.data.energy = 1200
    light.data.size = 5
    light.rotation_euler = (Vector((1, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.7, 0.7, 0.7, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
    bpy.context.view_layer.update()
    return group, part, other, support, shared


def save_case(name, measurement):
    folder = OUT / name
    folder.mkdir()
    (folder / 'measurement.json').write_text(json.dumps(measurement, indent=2) + '\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'scene.blend'))
    guard('render')
    render_scene(folder, SETTINGS)


records = {}

group, part, other, support, shared = base_scene()
checks = geometric_checks()
assert checks['hierarchy_parts']['measured_pass'] is True
assert checks['known_support']['measured_pass'] is True
records['correct'] = {'expected_error_detected': None, 'legal_scene_passed': True, 'checks': checks}
save_case('correct', records['correct'])

group, part, other, support, shared = base_scene()
part.parent = None
bpy.context.view_layer.update()
checks = geometric_checks()
assert checks['hierarchy_parts']['measured_pass'] is False
records['detached_part'] = {'expected_error_detected': True, 'checks': checks,
                            'note': 'Detachment preserves the current world pose; image alone need not expose the hierarchy defect.'}
save_case('detached_part', records['detached_part'])

group, part, other, support, shared = base_scene()
bpy.data.objects.remove(other, do_unlink=True)
checks = geometric_checks()
assert checks['hierarchy_parts']['measured_pass'] is False
records['missing_declared_part'] = {'expected_error_detected': True, 'checks': checks}
save_case('missing_declared_part', records['missing_declared_part'])

group, part, other, support, shared = base_scene()
part.location.z += 2
bpy.context.view_layer.update()
checks = geometric_checks()
assert checks['known_support']['measured_pass'] is False
records['broken_support'] = {'expected_error_detected': True, 'checks': checks}
save_case('broken_support', records['broken_support'])

group, part, other, support, shared = base_scene()
before = ib.snapshot_objects()
shared.diffuse_color = ib.BLUE
shared.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = ib.BLUE
after = ib.snapshot_objects()
preserve = ib.unchanged(before, after, {part.name})
assert preserve['pass'] is False
assert other.name in preserve['changed_fields']
records['shared_material_bad_edit'] = {'expected_error_detected': True, 'target': part.name,
                                     'non_target': other.name, 'non_target_preservation': preserve,
                                     'type': 'mechanical_not_text'}
save_case('shared_material_bad_edit', records['shared_material_bad_edit'])

group, part, other, support, shared = base_scene()
before = ib.snapshot_objects()
ib.set_blue([part.name])
after = ib.snapshot_objects()
preserve = ib.unchanged(before, after, {part.name})
target_success = ib.blue_success([part.name])
geometry_preserved = before[part.name]['vertices'] == after[part.name]['vertices'] and before[part.name]['matrix_world'] == after[part.name]['matrix_world']
assert target_success and preserve['pass'] and geometry_preserved
records['independent_local_edit'] = {'legal_scene_passed': True, 'target': part.name,
                                   'non_target': other.name, 'target_success': target_success,
                                   'target_geometry_preserved': geometry_preserved,
                                   'non_target_preservation': preserve, 'type': 'mechanical_not_text'}
save_case('independent_local_edit', records['independent_local_edit'])

group, part, other, support, shared = base_scene()
before = ib.snapshot_objects()
relations = ib.relative_matrices(group)
group.location.x += 0.4
bpy.context.view_layer.update()
error = ib.max_matrix_delta(relations, ib.relative_matrices(group))
preserve = ib.unchanged(before, ib.snapshot_objects(), {group.name} | {obj.name for obj in ib.descendants(group)})
assert error <= 1e-5 and preserve['pass']
records['correct_group_move'] = {'legal_scene_passed': True, 'relative_matrix_max_error': error,
                                 'non_target_preservation': preserve, 'type': 'mechanical_not_text'}
save_case('correct_group_move', records['correct_group_move'])

group, part, other, support, shared = base_scene()
cube('Intruder', (0.4, 0.2, 1.5), (1, 1, 1), shared)
bpy.context.view_layer.update()
checks = geometric_checks()
assert checks['mesh_intersection']['crossings']
records['triangle_crossing'] = {'expected_error_detected': True, 'checks': checks,
                                'limitation': 'Triangle-surface intersections are measured; intended joints and containment require separate interpretation.'}
save_case('triangle_crossing', records['triangle_crossing'])

(OUT / 'calibration.json').write_text(json.dumps({'status': 'passed', 'creator': 'engineering_fixture_not_M',
    'render_quality': 'calibration_preview_256_square_4_samples_excluded_from_formal_scores',
    'cases': records}, indent=2) + '\n')
print('V3_FUNCTIONAL_FIXTURES_PASSED')
