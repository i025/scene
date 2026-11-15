"""Deterministic checkpoint fixture; three builds, two renders, no model calls."""
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'backend'))
from budget import guard, current
from data import write_json
from devices import render_settings
from processes import run_measured
from incremental_blender import validate_patch


INITIAL_PATCH = '''from sceneact import *
scene = Scene('FixtureRoom')
floor = box((6, 6, .1), center=(0, 0, -.05), color=(.55, .55, .55))
floor.name = 'floor_geometry'
scene.include('floor_group', floor)
cube = box((1, 1, 1), center=(0, 0, .5), color=(.75, .05, .03))
cube.name = 'red_cube_geometry'
scene.include('red_cube_group', cube)
realize(scene)
set_view((4, -6, 4), (0, 0, .5), lens=45)
area_emitter((0, -3, 6), power=1200, size=5, target=(0, 0, 0))
'''

INCREMENTAL_PATCH = '''import bpy
from sceneact import *
cube = bpy.data.objects['red_cube_geometry']
cube.location.x += .75
scene = Scene('FixtureAddition')
second = box((.6, .6, 1.4), center=(-1.2, 0, .7), color=(.03, .1, .8))
second.name = 'blue_block_geometry'
scene.include('blue_block_group', second)
realize(scene, clear=False)
'''

FAILING_PATCH = '''import bpy
bpy.data.objects['red_cube_geometry'].location.x += 100
raise RuntimeError('intentional_fixture_failure_after_local_change')
'''


def read(path):
    return json.loads(Path(path).read_text())


def contract_checks():
    validate_patch(INITIAL_PATCH, False)
    validate_patch(INCREMENTAL_PATCH, True)
    invalid = {
        'clear_rejected': 'from sceneact import *\nrealize(Scene())',
        'reset_rejected': 'import bpy\nbpy.ops.wm.read_factory_settings(use_empty=True)',
        'load_rejected': 'import bpy\nbpy.ops.wm.open_mainfile(filepath="old.blend")',
        'file_io_rejected': 'open("external.txt", "w")',
    }
    checks = {}
    for name, source in invalid.items():
        try:
            validate_patch(source, True)
        except ValueError:
            checks[name] = True
        else:
            raise AssertionError(name)
    return checks


def run_process(config, folder, name, command, environment, expected_success=True):
    saved = folder / f'{name}_process.json'
    if saved.exists():
        result = read(saved)
        if result['status'] == 'running':
            raise RuntimeError('Audit unfinished fixture process before resuming: ' + str(saved))
    else:
        guard('render' if name == 'render' else 'build')
        timeout = config['blender']['render_timeout' if name == 'render' else 'build_timeout']
        with (folder / f'{name}_stdout.log').open('w') as stdout, (folder / f'{name}_stderr.log').open('w') as stderr:
            result = run_measured(command, timeout=timeout, measurement_path=saved,
                                  memory_limit_bytes=int(config['resources']['memory_limit_gb'] * 1024 ** 3),
                                  cwd=folder, stdout=stdout, stderr=stderr, env=environment)
    if expected_success and result['returncode'] != 0:
        raise RuntimeError('Fixture process failed: ' + str(saved))
    if not expected_success and (result['returncode'] == 0 or result['timed_out']):
        raise AssertionError('Expected a deterministic patch error, not success or timeout')
    return result


def prepare_folder(config, folder):
    folder.mkdir(parents=True, exist_ok=True)
    settings, environment = render_settings(config, folder)
    settings.update(width=256, height=192, samples=4)
    write_json(folder / 'render_settings.json', settings)
    environment['SCENE_RSI_TELEMETRY'] = str(folder / 'stage_events.jsonl')
    return settings, environment


def blender_prefix(config, settings):
    return [config['blender']['executable'], '--background', '-noaudio', '--factory-startup',
            '--disable-autoexec', '--threads', str(settings['threads']), '--python-exit-code', '1']


def build(config, folder, source, parent=None, expected_success=True):
    settings, environment = prepare_folder(config, folder)
    (folder / 'patch.py').write_text(source)
    command = blender_prefix(config, settings) + [
        '--python', str(ROOT / 'incremental_blender.py'), '--',
        '--patch', str(folder / 'patch.py'), '--output-blend', str(folder / 'scene.blend'),
        '--inventory', str(folder / 'scene_inventory.json'), '--events', str(folder / 'stage_events.jsonl'),
        '--settings', str(folder / 'render_settings.json'), '--backend-dir', str(ROOT / 'backend')]
    if parent:
        command += ['--previous-checkpoint', str(parent)]
    return run_process(config, folder, 'build', command, environment, expected_success)


def render(config, folder, script=None):
    settings, environment = prepare_folder(config, folder)
    command = blender_prefix(config, settings) + [
        '--python', str(script or ROOT / 'backend' / 'render.py'), '--',
        '--scene', str(folder / 'scene.blend'), '--settings', str(folder / 'render_settings.json'),
        '--output-dir', str(folder)]
    result = run_process(config, folder, 'render', command, environment)
    from PIL import Image
    with Image.open(folder / 'final.png') as image:
        image.load()
        assert image.size == (256, 192)
    return result


def run():
    saved = ROOT / 'preparation' / 'preflight.json'
    if saved.exists() and read(saved)['status'] == 'completed':
        return read(saved)
    started = time.time()
    config = read(ROOT / 'config.json')
    affinity = set(config['resources']['cpu_affinity'])
    if not affinity <= os.sched_getaffinity(0):
        raise ValueError('Configured fixture CPU set exceeds current allowed affinity')
    os.sched_setaffinity(0, affinity)
    checks = contract_checks()
    first = ROOT / 'preparation' / 'fixture' / 'initial'
    second = ROOT / 'preparation' / 'fixture' / 'incremental'
    failed = ROOT / 'preparation' / 'fixture' / 'intentional_failure'
    budget_before = current()
    build(config, first, INITIAL_PATCH)
    render(config, first)
    build(config, second, INCREMENTAL_PATCH, first / 'scene.blend')
    before = read(first / 'scene_inventory.json')['after']
    record = read(second / 'scene_inventory.json')
    after = record['after']
    cube_id = next(key for key, value in before['objects'].items() if value['name'] == 'red_cube_geometry')
    assert cube_id in after['objects']
    assert set(before['objects']) <= set(after['objects'])
    assert not record['changes']['deleted']
    assert cube_id in {item['object_id'] for item in record['changes']['modified']}
    assert any(after['objects'][key]['name'] == 'blue_block_geometry' for key in record['changes']['created'])
    assert abs(after['objects'][cube_id]['matrix_world'][0][3] - .75) < 1e-6
    checks.update(existing_ids_preserved=True, incremental_transform_measured=True,
                  appended_object_measured=True, no_existing_object_deleted=True)
    parent = second / 'scene.blend'
    stat = parent.stat()
    parent_before = {'path': str(parent), 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    write_json(failed.parent / 'parent_before_failure.json', parent_before)
    build(config, failed, FAILING_PATCH, parent, expected_success=False)
    assert not (failed / 'scene.blend').exists()
    assert 'intentional_fixture_failure_after_local_change' in (failed / 'build_stderr.log').read_text()
    stat = parent.stat()
    parent_after = {'path': str(parent), 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    assert parent_before == parent_after
    # Reopen the preserved parent in the second render process; record direct facts again.
    verify = second / 'verify_and_render.py'
    verify.write_text(f'''import json
import os
from pathlib import Path
import sys
sys.path.insert(0, {str(ROOT)!r})
sys.path.insert(0, {str(ROOT / 'backend')!r})
import bpy
from incremental_blender import snapshot
from render import render_scene
from telemetry import event
folder = Path({str(second)!r})
event('scene_load_started', parent_checkpoint=str(folder / 'scene.blend'))
bpy.ops.wm.open_mainfile(filepath=str(folder / 'scene.blend'))
event('scene_load_completed')
actual = snapshot(bpy.context.scene)
(folder / 'reopened_inventory.json').write_text(json.dumps(actual, indent=2))
expected = json.loads((folder / 'scene_inventory.json').read_text())['after']
assert set(actual['objects']) == set(expected['objects'])
cube_id = {cube_id!r}
assert actual['objects'][cube_id]['name'] == 'red_cube_geometry'
assert abs(actual['objects'][cube_id]['matrix_world'][0][3] - .75) < 1e-6
assert any(value['name'] == 'blue_block_geometry' for value in actual['objects'].values())
render_scene(folder, json.loads((folder / 'render_settings.json').read_text()))
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
''')
    render(config, second, verify)
    checks.update(failed_patch_did_not_save=True, parent_path_size_mtime_unchanged=True,
                  parent_reopened_after_failure=True, actual_renders_available=True)
    images = [str(first / 'final.png'), str(second / 'final.png')]
    result = {
        'status': 'completed', 'started': started, 'finished': time.time(),
        'seconds': time.time() - started, 'checks': checks,
        'scope': 'Deterministic synthetic checkpoint fixture; excluded from the two formal scene tasks.',
        'build_attempts': 3, 'intentional_build_failures': 1, 'render_attempts': 2,
        'model_calls': 0, 'automatic_quality_evaluation': False,
        'image_paths': images, 'next_cli_picture_check_attachments': images,
        'next_cli_picture_check_status': 'pending',
        'resources': config['resources'], 'render_configuration': {'width': 256, 'height': 192, 'samples': 4},
        'parent_before_failure': parent_before, 'parent_after_failure': parent_after,
        'budget_before': budget_before, 'budget_after': current(),
    }
    write_json(saved, result)
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
