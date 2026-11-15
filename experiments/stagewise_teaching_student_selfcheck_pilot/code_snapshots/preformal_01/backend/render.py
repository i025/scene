import argparse
import ast
import json
from pathlib import Path
import runpy
import sys


def configure_scene(output_dir, settings):
    import bpy
    from telemetry import event
    scene = bpy.context.scene
    if scene.camera is None:
        raise ValueError('Scene needs a camera matching the input photograph')
    if not any(o.type == 'MESH' and len(o.data.polygons) for o in scene.objects):
        raise ValueError('Scene has no mesh geometry')
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = settings['threads']
    scene.render.engine = settings['engine']
    scene.render.resolution_x, scene.render.resolution_y = settings['width'], settings['height']
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = settings.get('view_transform', 'AgX')
    scene.view_settings.look = settings.get('look', 'None')
    scene.view_settings.exposure = settings.get('exposure', 0)
    scene.view_settings.gamma = settings.get('gamma', 1)
    scene.render.use_border = False
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    if scene.render.engine == 'CYCLES':
        from devices import configure_cycles
        scene.cycles.samples = settings['samples']
        scene.cycles.seed = settings['seed']
        configure_cycles(scene, settings, output_dir / 'actual_device.json')
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.use_denoising = settings.get('denoise', False)
        scene.cycles.use_animated_seed = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.render.filepath = str(output_dir / 'final.png')
    actual = {'engine': scene.render.engine, 'threads': scene.render.threads,
              'threads_mode': scene.render.threads_mode,
              'width': scene.render.resolution_x, 'height': scene.render.resolution_y,
              'samples': scene.cycles.samples if scene.render.engine == 'CYCLES' else None,
              'device': settings['device']}
    (output_dir / 'actual_render_settings.json').write_text(json.dumps(actual, indent=2))
    event('render_configured', **actual)
    return scene


def save_scene(output_dir, settings):
    import bpy
    from telemetry import event
    scene = configure_scene(output_dir, settings)
    meshes = [o for o in scene.objects if o.type == 'MESH']
    event('scene_built', meshes=len(meshes), vertices=sum(len(o.data.vertices) for o in meshes),
          polygons=sum(len(o.data.polygons) for o in meshes),
          remaining_boolean_modifiers=sum(m.type == 'BOOLEAN' for o in meshes for m in o.modifiers))
    event('save_started')
    bpy.ops.wm.save_as_mainfile(filepath=str(output_dir / 'scene.blend'))
    (output_dir / 'camera.json').write_text(json.dumps({
        'matrix_world': [list(row) for row in scene.camera.matrix_world],
        'lens': scene.camera.data.lens, 'type': scene.camera.data.type,
        'width': settings['width'], 'height': settings['height']}))
    event('save_completed')


def render_scene(output_dir, settings):
    import bpy
    from telemetry import event
    configure_scene(output_dir, settings)
    event('render_started')
    bpy.ops.render.render(write_still=True)
    event('render_completed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=Path)
    parser.add_argument('--scene', type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--settings', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from telemetry import event
    if args.code:
        settings=json.loads(args.settings.read_text())
        import random
        import numpy as np
        random.seed(settings['seed']);np.random.seed(settings['seed'])
        event('local_program_seed',seed=settings['seed'],scope='Python random and numpy only; remote model sampling not controlled')
        event('python_validation_started')
        tree=ast.parse(args.code.read_text())
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]]
                if any(n not in {'sceneact','bpy','math','mathutils','numpy','random','itertools','collections'} for n in names):raise ValueError('Scene program import outside frozen contract')
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Name) and node.func.id in {'exec','eval','open','__import__','compile'}:raise ValueError('Scene program external execution/file IO is prohibited')
                if isinstance(node.func,ast.Attribute) and node.func.attr in {'render','save_as_mainfile','open_mainfile','load'}:raise ValueError('Scene program must not render, save or load external files')
        event('scene_build_started')
        runpy.run_path(str(args.code), run_name='__sceneact_build__')
        event('scene_build_completed')
    else:
        import bpy
        event('scene_load_started')
        bpy.ops.wm.open_mainfile(filepath=str(args.scene))
        event('scene_load_completed')
    if args.validate_only:
        import bpy
        scene = bpy.context.scene
        if scene.camera is None or not any(o.type == 'MESH' and len(o.data.polygons) for o in scene.objects):
            raise ValueError('Submission needs mesh geometry and an active camera')
        (args.output_dir / 'validated.json').write_text(json.dumps({'valid': True}))
    else:
        settings = json.loads(args.settings.read_text())
        if args.code:
            save_scene(args.output_dir, settings)
        if not args.build_only:
            render_scene(args.output_dir, settings)


if __name__ == '__main__':
    import os
    import traceback
    try:
        main()
        status = 0
    except BaseException:
        traceback.print_exc()
        status = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(status)
