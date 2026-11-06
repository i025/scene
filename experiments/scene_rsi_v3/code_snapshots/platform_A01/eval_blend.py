"""Read-only BW-style scene evidence and fixed evaluator cameras in Blender.

The evaluator changes cameras and render parameters only, never the saved project.
Camera locations are framing rules, not visual error localization or geometry truth.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from budget import guard
import inspect_blend as ib


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def scene_facts():
    from regression import geometric_checks

    bpy.context.view_layer.update()
    scene = bpy.context.scene
    objects = []
    for obj in sorted(scene.objects, key=lambda item: item.name):
        objects.append({
            'object_id': obj.name, 'type': obj.type,
            'parent': obj.parent.name if obj.parent else None,
            'children': sorted(child.name for child in obj.children),
            'parent_chain': ib.parent_chain(obj),
            'matrix_world': ib.matrix_values(obj.matrix_world),
            'dimensions_scene_units': list(obj.dimensions),
            'world_aabb_approx': ib.world_bounds(obj),
            'vertices': len(obj.data.vertices) if obj.type == 'MESH' else None,
            'polygons': len(obj.data.polygons) if obj.type == 'MESH' else None,
            'finite_nonempty_mesh': ib.mesh_valid(obj) if obj.type == 'MESH' else None,
            'hide_render': obj.hide_render,
            'modifiers': [{'name': m.name, 'type': m.type, 'show_render': m.show_render}
                          for m in obj.modifiers],
            'material_slots': [slot.material.name if slot.material else None for slot in obj.material_slots],
            'declared_children': json.loads(obj['scene_rsi_expected_children'])
                                 if 'scene_rsi_expected_children' in obj else None,
        })
    dependencies = []
    for image in bpy.data.images:
        if image.source not in {'FILE', 'SEQUENCE'} or not image.filepath:
            continue
        resolved = Path(bpy.path.abspath(image.filepath))
        dependencies.append({'image': image.name, 'authored_path': image.filepath,
                             'packed': image.packed_file is not None,
                             'resolved_exists': resolved.is_file()})
    camera = scene.camera
    return {
        'blend_opened': True, 'blender_version': bpy.app.version_string,
        'objects': objects, 'mesh_count': sum(o['type'] == 'MESH' for o in objects),
        'camera': {'object_id': camera.name, 'type': camera.data.type,
                   'lens_mm': camera.data.lens, 'ortho_scale': camera.data.ortho_scale,
                   'matrix_world': ib.matrix_values(camera.matrix_world)} if camera else None,
        'unit_settings': {'system': scene.unit_settings.system,
                          'scale_length': scene.unit_settings.scale_length},
        'color_management': {'view_transform': scene.view_settings.view_transform,
                             'look': scene.view_settings.look,
                             'exposure': scene.view_settings.exposure,
                             'gamma': scene.view_settings.gamma},
        'authored_resolution': [scene.render.resolution_x, scene.render.resolution_y],
        'declared_supports': json.loads(scene.get('scene_rsi_supports', '[]')),
        'structural_measurements': geometric_checks(),
        'materials': {material.name: ib.material_values(material) for material in bpy.data.materials},
        'material_dependencies': [
            {'material': material.name, 'objects': sorted(obj.name for obj in scene.objects
             if any(slot.material == material for slot in obj.material_slots))}
            for material in sorted(bpy.data.materials, key=lambda item: item.name)],
        'texture_dependencies': dependencies,
        'required_dependencies_available': all(d['packed'] or d['resolved_exists'] for d in dependencies),
        'limits': ['Object names and emitted relationships are declarations, not semantic ground truth.',
                   'AABB extents are approximate; no mesh collision or true 3D fidelity is inferred.',
                   'No metric scale accuracy or hidden geometry accuracy is measured.'],
    }


def camera_plan(facts, settings):
    meshes = [o for o in bpy.context.scene.objects if ib.mesh_valid(o) and not o.hide_render]
    framing_meshes = [o for o in meshes if not ib.is_structural(o)] or meshes
    boxes = [ib.world_bounds(o) for o in framing_meshes]
    room_boxes = [ib.world_bounds(o) for o in meshes]
    if not boxes:
        raise ValueError('No finite nonempty mesh for evaluator camera framing')
    subject = ib.bounds(Vector(p) for box in boxes for p in [box['min'], box['max']])
    room = ib.bounds(Vector(p) for box in room_boxes for p in [box['min'], box['max']])
    low, high = Vector(subject['min']), Vector(subject['max'])
    room_low, room_high = Vector(room['min']), Vector(room['max'])
    span = high - low
    diagonal = max(span.length, 1e-3)
    center = (low + high) / 2
    room_center = (room_low + room_high) / 2
    room_span = room_high - room_low
    views = []
    if facts['camera'] is not None:
        authored_width, authored_height = facts['authored_resolution']
        authored_scale = settings['resolution'] / max(authored_width, authored_height)
        views.append({'view_id': 'author', 'kind': 'author',
                      'camera_object': facts['camera']['object_id'],
                      'file': 'author.png', 'camera_matrix_world': facts['camera']['matrix_world'],
                      'resolution': [max(1, round(authored_width * authored_scale)),
                                     max(1, round(authored_height * authored_scale))]})
    # Six in-bounds wide camera positions; two additional closer spatial details.
    # This selection is fixed before seeing candidate quality and never names a fault.
    angles = [0, math.pi / 3, 2 * math.pi / 3, math.pi,
              4 * math.pi / 3, 5 * math.pi / 3]
    for index, angle in enumerate(angles):
        if settings['interior']:
            position = Vector((room_center.x + .34 * max(room_span.x, 1e-3) * math.cos(angle),
                               room_center.y + .34 * max(room_span.y, 1e-3) * math.sin(angle),
                               room_low.z + (.48 if index % 2 == 0 else .64) * max(room_span.z, 1e-3)))
        else:
            position = center + Vector((diagonal * math.cos(angle), diagonal * math.sin(angle),
                                        diagonal * (.35 if index % 2 == 0 else .65)))
        target = center.copy()
        if (target - position).length < diagonal * .01:
            target.x += diagonal * .1
        views.append({'view_id': f'wide_{index + 1:02d}', 'kind': 'wide',
                      'position': list(position), 'target': list(target),
                      'lens_mm': 20 if settings['interior'] else 42,
                      'file': f'wide_{index + 1:02d}.png'})
    for index, fraction in enumerate([.3, .7]):
        target = Vector((low.x + span.x * fraction, center.y, low.z + span.z * .45))
        if settings['interior']:
            position = Vector((room_low.x + room_span.x * fraction,
                               room_low.y + room_span.y * (.28 if index == 0 else .72),
                               room_low.z + room_span.z * .52))
        else:
            position = target + Vector((diagonal * .2, diagonal * (-.35 if index == 0 else .35),
                                         diagonal * .22))
        if (target - position).length < diagonal * .01:
            target.y += diagonal * .1
        views.append({'view_id': f'detail_{index + 1:02d}', 'kind': 'detail',
                      'position': list(position), 'target': list(target),
                      'lens_mm': 38, 'file': f'detail_{index + 1:02d}.png'})
    if settings['preview']:
        views = [v for v in views if v['view_id'] in {'author', 'wide_01', 'wide_03', 'detail_01'}]
    return {'rule_version': 'bw_style_fixed_inbounds_v3_1', 'subject_bounds_approx': subject,
            'room_bounds_approx': room, 'interior': settings['interior'], 'views': views,
            'view_selection_limit': 'Fixed spatial framing adaptation, not official adaptive agent selection. '
              'Name-based exclusion of architectural meshes is used only for framing; not diagnosis. '
              'Details use fixed spatial regions, not candidate-specific semantic object targeting. '
              'In-bounds camera positions can still be occluded; authored defects are never repaired.'}


def render_view(folder, settings, view_id):
    plan = json.loads((folder / 'view_plan.json').read_text())
    view = next(v for v in plan['views'] if v['view_id'] == view_id)
    scene = bpy.context.scene
    if view['kind'] == 'author':
        scene.camera = bpy.data.objects[view['camera_object']]
    else:
        data = bpy.data.cameras.new('_BW_evaluation_camera')
        camera = bpy.data.objects.new('_BW_evaluation_camera', data)
        scene.collection.objects.link(camera)
        camera.location = Vector(view['position'])
        camera.rotation_euler = (Vector(view['target']) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.lens = view['lens_mm']
        data.clip_start = max(plan['subject_bounds_approx']['diagonal_scene_units'] * 1e-5, 1e-5)
        data.clip_end = max(plan['room_bounds_approx']['diagonal_scene_units'] * 100, 100)
        scene.camera = camera
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = settings['threads']
    resolution = view['resolution'] if view['kind'] == 'author' else [settings['resolution']] * 2
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.cycles.samples = settings['samples']
    scene.cycles.seed = settings['seed']
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.use_border = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(folder / view['file'])
    bpy.context.view_layer.update()
    guard('render')
    result = {'view_id': view_id, 'status': 'running', 'started': time.time(),
              'engine': scene.render.engine, 'resolution': resolution,
              'samples': scene.cycles.samples, 'device': scene.cycles.device,
              'threads': scene.render.threads, 'seed': scene.cycles.seed,
              'denoise': scene.cycles.use_denoising,
              'camera_matrix_world': ib.matrix_values(scene.camera.matrix_world),
              'color_management': {'view_transform': scene.view_settings.view_transform,
                                   'look': scene.view_settings.look,
                                   'exposure': scene.view_settings.exposure,
                                   'gamma': scene.view_settings.gamma},
              'source_unchanged': 'Source project opened read-only and never saved',
              'preview': settings['preview'], 'file': view['file']}
    write_json(folder / f'{view_id}_render.json', result)
    bpy.ops.render.render(write_still=True)
    result.update(status='completed', finished=time.time())
    result['seconds'] = result['finished'] - result['started']
    write_json(folder / f'{view_id}_render.json', result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blend', required=True, type=Path)
    parser.add_argument('--folder', required=True, type=Path)
    parser.add_argument('--settings', required=True, type=Path)
    parser.add_argument('--view-id')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    settings = json.loads(args.settings.read_text())
    args.folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
    # Copying a native project must not break its declared relative texture paths.
    # Resolve only the same artifact's original asset folder; never search or repair
    # visual contents. Source and copied blend files remain untouched on disk.
    restored = []
    for image in bpy.data.images:
        if image.filepath.startswith('//') and image.packed_file is None:
            source = Path(settings['dependency_source_folder']) / image.filepath[2:]
            restored.append({'image': image.name, 'authored_path': image.filepath,
                             'source_path': str(source.resolve()), 'exists': source.is_file()})
            image.filepath = str(source.resolve())
    write_json(args.folder / 'dependency_resolution.json', restored)
    if args.view_id:
        render_view(args.folder, settings, args.view_id)
    else:
        facts = scene_facts()
        write_json(args.folder / 'scene_facts.json', facts)
        write_json(args.folder / 'view_plan.json', camera_plan(facts, settings))


if __name__ == '__main__':
    main()
