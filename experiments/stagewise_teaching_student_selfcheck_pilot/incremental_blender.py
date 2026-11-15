"""Apply one scene patch to a checkpoint; rendering remains a separate process."""
import argparse
import ast
import json
import os
from pathlib import Path
import runpy
import sys
import time


ID_KEY = 'scene_rsi_object_id'
COUNTER_KEY = 'scene_rsi_next_object_id'


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def emit(path, stage, **values):
    with Path(path).open('a') as stream:
        stream.write(json.dumps({'stage': stage, 'time': time.time(), **values}) + '\n')


def validate_patch(source, continuing):
    tree = ast.parse(source)
    allowed = {'sceneact', 'bpy', 'math', 'mathutils', 'numpy', 'random',
               'itertools', 'collections'}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ([item.name.split('.')[0] for item in node.names]
                     if isinstance(node, ast.Import) else [(node.module or '').split('.')[0]])
            if any(name not in allowed for name in names):
                raise ValueError('Patch import outside the frozen scene contract')
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                    'exec', 'eval', 'open', '__import__', 'compile'}:
                raise ValueError('Patch external execution and file IO are prohibited')
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                    'render', 'save_as_mainfile', 'save_mainfile', 'open_mainfile',
                    'read_factory_settings', 'read_homefile', 'load', 'write'}:
                raise ValueError('Patch must not reset, load, save, or render a scene')
            name = (node.func.id if isinstance(node.func, ast.Name) else
                    node.func.attr if isinstance(node.func, ast.Attribute) else None)
            if continuing and name == 'realize':
                clear = next((item.value for item in node.keywords if item.arg == 'clear'), None)
                positional = node.args[1] if len(node.args) > 1 else None
                value = clear if clear is not None else positional
                if not isinstance(value, ast.Constant) or value.value is not False:
                    raise ValueError('Continuation must call realize(..., clear=False)')
    return tree


def assign_ids(scene, originals=None):
    """Preserve IDs on surviving objects; copied objects receive distinct new IDs."""
    originals = originals or {}
    next_id = int(scene.get(COUNTER_KEY, 1))
    used = set(originals.values())
    for obj in scene.objects:
        pointer = obj.as_pointer()
        if pointer in originals:
            if obj.get(ID_KEY) != originals[pointer]:
                raise ValueError('Patch changed a persistent object ID: ' + obj.name)
            continue
        current = obj.get(ID_KEY)
        if not current or current in used:
            current = f'obj_{next_id:05d}'
            while current in used:
                next_id += 1
                current = f'obj_{next_id:05d}'
            next_id += 1
            obj[ID_KEY] = current
        used.add(current)
    scene[COUNTER_KEY] = next_id


def socket_value(value):
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    if hasattr(value, 'name'):
        return {'datablock_name': value.name}
    return list(value)


def node_tree_record(tree):
    if tree is None:
        return None
    return {
        'nodes': [{
            'name': node.name, 'type': node.bl_idname,
            'inputs': {socket.identifier: socket_value(socket.default_value)
                       for socket in node.inputs if hasattr(socket, 'default_value')},
        } for node in tree.nodes],
        'links': [[link.from_node.name, link.from_socket.identifier,
                   link.to_node.name, link.to_socket.identifier] for link in tree.links],
    }


def snapshot(scene):
    """Record direct scene facts, including raw mesh coordinates, without digests."""
    import bpy
    bpy.context.view_layer.update()
    objects = {}
    materials = {}
    for obj in scene.objects:
        slots = [slot.material.name if slot.material else None for slot in obj.material_slots]
        for slot in obj.material_slots:
            material = slot.material
            if material is not None:
                materials[material.name] = {
                    'diffuse_color': list(material.diffuse_color),
                    'use_nodes': material.use_nodes,
                    'node_tree': node_tree_record(material.node_tree),
                }
        geometry = None
        if obj.type == 'MESH':
            geometry = {
                'datablock_name': obj.data.name,
                'vertices': [list(vertex.co) for vertex in obj.data.vertices],
                'edges': [list(edge.vertices) for edge in obj.data.edges],
                'polygons': [list(polygon.vertices) for polygon in obj.data.polygons],
                'polygon_material_indices': [polygon.material_index for polygon in obj.data.polygons],
            }
        elif obj.type in {'CURVE', 'SURFACE'}:
            geometry = {
                'datablock_name': obj.data.name, 'dimensions': obj.data.dimensions,
                'bevel_depth': obj.data.bevel_depth, 'extrude': obj.data.extrude,
                'splines': [{'type': spline.type,
                             'points': [list(point.co) for point in spline.points],
                             'bezier_points': [{'co': list(point.co),
                                                'handle_left': list(point.handle_left),
                                                'handle_right': list(point.handle_right)}
                                               for point in spline.bezier_points]}
                            for spline in obj.data.splines],
            }
        camera = ({'type': obj.data.type, 'lens': obj.data.lens,
                   'sensor_width': obj.data.sensor_width, 'ortho_scale': obj.data.ortho_scale,
                   'shift_x': obj.data.shift_x, 'shift_y': obj.data.shift_y,
                   'clip_start': obj.data.clip_start, 'clip_end': obj.data.clip_end}
                  if obj.type == 'CAMERA' else None)
        light = ({'type': obj.data.type, 'energy': obj.data.energy,
                  'color': list(obj.data.color)} if obj.type == 'LIGHT' else None)
        objects[obj[ID_KEY]] = {
            'name': obj.name, 'type': obj.type,
            'parent_id': obj.parent[ID_KEY] if obj.parent else None,
            'matrix_world': [list(row) for row in obj.matrix_world],
            'matrix_local': [list(row) for row in obj.matrix_local],
            'dimensions': list(obj.dimensions), 'geometry': geometry,
            'material_slots': slots, 'camera': camera, 'light': light,
            'hide_render': obj.hide_render, 'hide_viewport': obj.hide_viewport,
            'modifiers': [{'name': mod.name, 'type': mod.type,
                           'show_render': mod.show_render, 'show_viewport': mod.show_viewport}
                          for mod in obj.modifiers],
        }
    world = ({'name': scene.world.name, 'color': list(scene.world.color),
              'use_nodes': scene.world.use_nodes,
              'node_tree': node_tree_record(scene.world.node_tree)} if scene.world else None)
    return {'objects': objects, 'materials': materials, 'world': world,
            'active_camera_id': scene.camera[ID_KEY] if scene.camera else None}


def changes_between(before, after):
    old, new = before['objects'], after['objects']
    created = sorted(set(new) - set(old))
    deleted = sorted(set(old) - set(new))
    modified = []
    material_changes = sorted(name for name in set(before['materials']) | set(after['materials'])
                              if before['materials'].get(name) != after['materials'].get(name))
    for object_id in sorted(set(old) & set(new)):
        fields = [key for key in old[object_id] if old[object_id][key] != new[object_id][key]]
        affected = [name for name in new[object_id]['material_slots'] if name in material_changes]
        if affected:
            fields.append('material_content')
        if fields:
            modified.append({'object_id': object_id, 'name': new[object_id]['name'],
                             'fields': fields, 'changed_materials': affected})
    camera_ids = sorted(object_id for object_id in set(old) | set(new)
                        if (old[object_id]['type'] if object_id in old else new[object_id]['type']) == 'CAMERA'
                        and old.get(object_id) != new.get(object_id))
    return {'created': created, 'deleted': deleted, 'modified': modified,
            'camera_changes': {'object_ids': camera_ids,
                               'active_before': before['active_camera_id'],
                               'active_after': after['active_camera_id']},
            'material_changes': material_changes, 'world_changed': before['world'] != after['world']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--patch', required=True, type=Path)
    parser.add_argument('--previous-checkpoint', type=Path)
    parser.add_argument('--output-blend', required=True, type=Path)
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--events', required=True, type=Path)
    parser.add_argument('--settings', required=True, type=Path)
    parser.add_argument('--backend-dir', required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.output_blend.exists():
        raise FileExistsError('A checkpoint must never overwrite an earlier artifact')
    args.output_blend.parent.mkdir(parents=True, exist_ok=True)
    os.environ['SCENE_RSI_TELEMETRY'] = str(args.events)
    sys.path.insert(0, str(args.backend_dir))
    import bpy
    import numpy as np
    import random
    settings = json.loads(args.settings.read_text())
    random.seed(settings['seed'])
    np.random.seed(settings['seed'])
    emit(args.events, 'python_validation_started')
    validate_patch(args.patch.read_text(), args.previous_checkpoint is not None)
    if args.previous_checkpoint:
        emit(args.events, 'scene_load_started', parent_checkpoint=str(args.previous_checkpoint))
        bpy.ops.wm.open_mainfile(filepath=str(args.previous_checkpoint))
        emit(args.events, 'scene_load_completed')
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        emit(args.events, 'empty_scene_initialized')
    scene = bpy.context.scene
    assign_ids(scene)
    originals = {obj.as_pointer(): obj[ID_KEY] for obj in scene.objects}
    before = snapshot(scene)
    write_json(args.inventory, {'parent_checkpoint': str(args.previous_checkpoint) if args.previous_checkpoint else None,
                               'patch': str(args.patch), 'status': 'patch_running', 'before': before,
                               'after': None, 'changes': None})
    if args.previous_checkpoint:
        import sceneact
        import sceneact.blender_scene
        original_realize = sceneact.realize
        def append_sceneact(scene, clear=False):
            if clear:
                raise ValueError('Continuation cannot clear the loaded checkpoint')
            return original_realize(scene, clear=False)
        sceneact.realize = append_sceneact
        sceneact.blender_scene.realize = append_sceneact
    emit(args.events, 'scene_build_started')
    runpy.run_path(str(args.patch), run_name='__sceneact_patch__')
    scene = bpy.context.scene
    survivors = {obj.as_pointer() for obj in scene.objects} & set(originals)
    if originals and not survivors:
        raise ValueError('Continuation removed every object from its parent checkpoint')
    assign_ids(scene, originals)
    after = snapshot(scene)
    changes = changes_between(before, after)
    emit(args.events, 'scene_build_completed', created=len(changes['created']),
         deleted=len(changes['deleted']), modified=len(changes['modified']))
    from render import configure_scene
    configure_scene(args.output_blend.parent, settings)
    scene.render.filepath = str(args.output_blend.parent / 'final.png')
    bpy.context.preferences.filepaths.save_version = 0
    emit(args.events, 'save_started', output_checkpoint=str(args.output_blend))
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output_blend))
    emit(args.events, 'save_completed')
    write_json(args.inventory, {
        'status': 'completed', 'parent_checkpoint': str(args.previous_checkpoint) if args.previous_checkpoint else None,
        'output_checkpoint': str(args.output_blend), 'patch': str(args.patch),
        'before': before, 'after': after, 'changes': changes,
        'measurement_scope': 'Raw mesh/curve data, transforms, hierarchy, material sockets and links; not a visual quality score. Modifier parameters beyond type and visibility are not exhaustively measured.',
    })


if __name__ == '__main__':
    import traceback
    try:
        main()
        status = 0
    except Exception:
        traceback.print_exc()
        status = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(status)
