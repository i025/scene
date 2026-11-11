"""Fixed text editor; adapted from the pilot supplement/text_edit_worker checks.

One Terra CLI response selects its target and writes edit(); one Blender process
applies it to a disposable project. Mechanical preservation is not semantic truth.
"""
import ast
import json
from pathlib import Path
import runpy
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
SUBSET = ('commons_109923183', 'commons_104864364')
INSTRUCTION = '将画面中心的一件独立家具表面改为蓝色，保持它的几何及其余对象不变'
EDITOR_MODEL = 'gpt-6.1-terra'
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'target_object_ids': {'type': 'array', 'items': {'type': 'string'}},
    'target_reason': {'type': 'string'}, 'semantic_uncertainty': {'type': 'string'},
    'edit_code': {'type': 'string'}},
    'required': ['target_object_ids', 'target_reason', 'semantic_uncertainty', 'edit_code']}


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def validate_editor_code(code):
    from research import validate_source
    validate_source(code, 'semantic_edit')
    tree = ast.parse(code)
    if not any(isinstance(node, ast.FunctionDef) and node.name == 'edit' for node in tree.body):
        raise ValueError('Editor must define edit()')
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module]
            if any(name.split('.')[0] not in {'bpy', 'math', 'mathutils'} for name in names):
                raise ValueError('Editor imports only bpy/math/mathutils')
        if isinstance(node, ast.Attribute) and node.attr == 'ops':
            raise ValueError('Editor uses datablocks, not Blender operators')


def run_edit(scene_id, blend, author_image, scene_facts, cfg, output_folder):
    from PIL import Image
    from codex_wrapper import call
    from processes import cpu_environment, run_measured
    if scene_id not in SUBSET:
        raise ValueError('Scene outside the frozen development editing subset')
    output = Path(output_folder).resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    status = {'status': 'running', 'scene_id': scene_id, 'instruction': INSTRUCTION,
              'test_type': 'fixed_text_instruction_editing', 'requested_model': EDITOR_MODEL,
              'observed_model': 'unknown', 'reasoning_effort': 'medium', 'editor_calls': 0,
              'cli_role': 'H', 'cli_subrole': 'fixed_text_editor',
              'repair_calls': 0, 'blender_executions': 0, 'semantic_target_correctness': None,
              'semantic_target_correctness_status': 'not_independently_validated', 'started': started}
    write_json(output / 'status.json', status)
    prompt = ('You are the frozen Blender text-instruction editor. Image 1 is the current authored '
              'view of the supplied scene. Choose ONE independent furniture item near the image '
              'center, identify its actual mesh IDs from the object list, and generate a complete '
              'Python module defining edit() for the already-open scene. Parent-related mesh parts '
              'of the same furniture may be targets; unrelated furniture must not be targets. '
              'Explain uncertainty and return no targets if there is no identifiable furniture. '
              'Do not use tools, read files, access disk/network/models, render or save. Only '
              'bpy/math/mathutils imports, direct datablocks, no bpy.ops. Copy target mesh/material '
              'datablocks as needed to preserve all non-targets. Preserve geometry, topology, '
              'transforms, parenting, modifiers, visibility, camera, lights and world. Technical '
              'blue convention: RGBA=(0.02,0.08,0.8,1), roughness=0.45; synchronize diffuse_color '
              'and the actual unlinked Principled Base Color connected to Material Output. '
              'No trial execution or repair. Return the JSON schema with full code.\nInstruction: '
              + INSTRUCTION + '\nActual objects:\n' + json.dumps(scene_facts['objects'], ensure_ascii=False))
    editor = {**cfg['model'], 'name': EDITOR_MODEL, 'model': EDITOR_MODEL, 'reasoning_effort': 'medium'}
    status['editor_calls'] = 1
    write_json(output / 'status.json', status)
    try:
        response, session = call(prompt, editor, output / 'editor_call', [author_image], role='H', schema=SCHEMA)
    except RuntimeError as error:
        status.update(status='failed', failure_type='editor_model_call_failed', error=str(error), finished=time.time())
        write_json(output / 'status.json', status)
        return status
    status['observed_model'] = session['observed_model']
    try:
        proposal = json.loads(response)
        validate_editor_code(proposal['edit_code'])
        mesh_ids = {obj['object_id'] for obj in scene_facts['objects'] if obj['type'] == 'MESH'}
        targets = proposal['target_object_ids']
        if not targets or len(targets) != len(set(targets)) or not set(targets) <= mesh_ids:
            raise ValueError('Editor target IDs missing, duplicated, or outside actual mesh list')
    except (json.JSONDecodeError, ValueError, SyntaxError) as error:
        status.update(status='invalid', failure_type='invalid_editor_program_or_target', error=str(error), finished=time.time())
        write_json(output / 'status.json', status)
        return status
    write_json(output / 'proposal.json', proposal)
    (output / 'edit.py').write_text(proposal['edit_code'])
    write_json(output / 'targets.json', targets)
    with Image.open(author_image) as image:
        width, height = image.size
    settings = {**cfg['render'], 'width': width, 'height': height, 'device': 'CPU',
                'threads': cfg['resources']['threads_per_blender']}
    write_json(output / 'settings.json', settings)
    command = [cfg['blender']['executable'], '--background', '--disable-autoexec', '--threads', str(settings['threads']),
               '--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--', '--worker',
               '--blend', str(Path(blend).resolve()), '--output', str(output)]
    with (output / 'stdout.log').open('w') as stdout, (output / 'stderr.log').open('w') as stderr:
        process = run_measured(command, timeout=cfg['blender']['timeout'], measurement_path=output / 'process.json',
                               memory_limit_bytes=int(cfg['resources']['memory_limit_gb'] * 1024 ** 3),
                               stdout=stdout, stderr=stderr, env=cpu_environment(threads=settings['threads']))
    status.update(status='completed' if process['returncode'] == 0 else 'timeout' if process['timed_out'] else 'failed',
                  blender_executions=1, finished=time.time(), seconds=time.time() - started,
                  process=process, failure_type=None if process['returncode'] == 0 else 'editor_blender_failure')
    if process['returncode'] == 0:
        status['checks'] = json.loads((output / 'text_edit.json').read_text())
    write_json(output / 'status.json', status)
    return status


def scalar_parameters(value):
    import bpy
    import inspect_blend as ib
    result = {}
    for prop in value.bl_rna.properties:
        if prop.is_readonly:
            continue
        item = getattr(value, prop.identifier)
        if prop.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            result[prop.identifier] = ib.json_number(item)
        elif prop.type == 'POINTER' and (item is None or isinstance(item, bpy.types.ID)):
            result[prop.identifier] = item.name if item is not None else None
    return result


def node_state(tree):
    import inspect_blend as ib
    if tree is None:
        return None
    return {'nodes': [{'name': n.name, 'type': n.bl_idname, 'parameters': scalar_parameters(n),
                       'inputs': {s.identifier: ib.json_number(s.default_value) for s in n.inputs if hasattr(s, 'default_value')},
                       'outputs': {s.identifier: ib.json_number(s.default_value) for s in n.outputs if hasattr(s, 'default_value')}}
                      for n in sorted(tree.nodes, key=lambda n: n.name)],
            'links': sorted([link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier]
                            for link in tree.links)}


def scene_state():
    import bpy
    scene = bpy.context.scene
    return {'active_camera': scene.camera.name if scene.camera else None,
            'world_name': scene.world.name if scene.world else None,
            'world_parameters': scalar_parameters(scene.world) if scene.world else None,
            'world_nodes': node_state(scene.world.node_tree) if scene.world else None}


def edit_snapshot():
    import bpy
    import inspect_blend as ib
    result = ib.snapshot_objects()
    for obj in bpy.context.scene.objects:
        result[obj.name].update(type=obj.type, hide_render=obj.hide_render, hide_viewport=obj.hide_viewport,
                               modifiers=[{'name': m.name, 'type': m.type, 'parameters': scalar_parameters(m)} for m in obj.modifiers],
                               constraints=[{'name': c.name, 'type': c.type, 'parameters': scalar_parameters(c)} for c in obj.constraints],
                               material_nodes=[node_state(slot.material.node_tree) if slot.material else None for slot in obj.material_slots])
        if obj.type == 'MESH':
            result[obj.name].update(edges=[list(e.vertices) for e in obj.data.edges],
                                    faces=[list(p.vertices) for p in obj.data.polygons],
                                    smooth_faces=[p.use_smooth for p in obj.data.polygons])
        elif obj.type == 'CAMERA':
            result[obj.name]['camera_parameters'] = scalar_parameters(obj.data)
        elif obj.type == 'LIGHT':
            result[obj.name]['light_parameters'] = scalar_parameters(obj.data)
            result[obj.name]['light_nodes'] = node_state(obj.data.node_tree)
    return result


def worker(blend, output):
    import bpy
    import inspect_blend as ib
    from budget import guard
    from render import render_scene
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    settings = json.loads((output / 'settings.json').read_text())
    targets = json.loads((output / 'targets.json').read_text())
    before = edit_snapshot()
    global_before = scene_state()
    before_folder = output / 'before_render'
    before_folder.mkdir()
    guard('render')
    render_scene(before_folder, settings)
    (before_folder / 'final.png').rename(output / 'before.png')
    code = (output / 'edit.py').read_text()
    validate_editor_code(code)
    runpy.run_path(str(output / 'edit.py'))['edit']()
    bpy.context.view_layer.update()
    after = edit_snapshot()
    non_target = ib.unchanged(before, after, set(targets))
    geometry = all(all(after.get(name, {}).get(key) == value for key, value in before[name].items()
                       if key not in {'materials', 'material_nodes'}) for name in targets)
    material_changed = all(before[name]['materials'] != after.get(name, {}).get('materials') for name in targets)
    target_blue = ib.blue_success(targets)
    if target_blue:
        for name in targets:
            for slot in bpy.data.objects[name].material_slots:
                material = slot.material
                output_node = next((n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
                links = list(output_node.inputs['Surface'].links) if output_node else []
                shader = links[0].from_node if len(links) == 1 else None
                target_blue &= bool(shader and shader.type == 'BSDF_PRINCIPLED' and not shader.inputs['Base Color'].is_linked
                                    and not shader.inputs['Roughness'].is_linked and abs(shader.inputs['Roughness'].default_value - .45) < 1e-6)
    global_preserved = global_before == scene_state()
    write_json(output / 'before_snapshot.json', before)
    write_json(output / 'after_snapshot.json', after)
    after_folder = output / 'after_render'
    after_folder.mkdir()
    guard('render')
    render_scene(after_folder, settings)
    (after_folder / 'final.png').rename(output / 'after.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'edited.blend'))
    write_json(output / 'text_edit.json', {'test_type': 'fixed_text_instruction_editing',
        'instruction': INSTRUCTION, 'targets': targets, 'target_surface_blue': target_blue,
        'target_material_changed': material_changed, 'target_geometry_preserved': geometry,
        'non_target_preservation': non_target, 'camera_world_preserved': global_preserved,
        'mechanical_pass': target_blue and material_changed and geometry and non_target['pass'] and global_preserved,
        'semantic_target_correctness': None, 'semantic_target_correctness_status': 'not_independently_validated',
        'editor_calls': 1, 'repair_calls': 0, 'blender_executions': 1, 'render_attempts': 2,
        'limits': 'Snapshots cover measured geometry/transforms/materials/topology/parent and scalar modifier/constraint/camera/light parameters; not arbitrary drivers or nested shader-group internals. Target center/furniture identity has no independent semantic ground truth.'})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--blend', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not args.worker:
        raise ValueError('Use run_edit() through the frozen experiment runner')
    worker(args.blend, args.output)
