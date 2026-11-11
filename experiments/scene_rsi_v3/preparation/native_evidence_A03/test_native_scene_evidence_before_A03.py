"""Pure stub contract for native scene-fact fields; does not launch Blender."""
import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[2] / 'outputs' / 'scene_rsi_v3'
sys.path.insert(0, str(ROOT))
import regression


class NamedRows(list):
    def __contains__(self, value):
        return any(row.name == value for row in self) if isinstance(value, str) else super().__contains__(value)


def main():
    matrix = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]
    def obj(name, kind, data):
        return NS(name=name, type=kind, data=data, parent=None, children=NamedRows(), matrix_world=matrix,
                  dimensions=(1, 1, 1), hide_render=False, modifiers=[], material_slots=[],
                  __contains__=lambda value: False)
    # Blender ID properties support membership; this small object implements it.
    class Object(NS):
        def __contains__(self, value):
            return False
    camera = Object(**vars(obj('AuthorCam', 'CAMERA', NS(type='PERSP', lens=28., ortho_scale=3.5))))
    secondary = Object(**vars(obj('DetailCam', 'CAMERA', NS(type='ORTHO', lens=50., ortho_scale=2.))))
    text = Object(**vars(obj('Label', 'FONT', NS(body='Actual native label', font=NS(name='Bfont')))))
    objects = NamedRows([camera, secondary, text])
    detail = NS(name='Details', children=NamedRows(), objects=NamedRows(), hide_render=True)
    room = NS(name='Room', children=NamedRows([detail]), objects=NamedRows([secondary, text]), hide_render=False)
    master = NS(name='Scene Collection', children=NamedRows([room]), objects=NamedRows([camera]), hide_render=False)
    render = NS(engine='BLENDER_EEVEE_NEXT', resolution_x=374, resolution_y=512, resolution_percentage=100,
                image_settings=NS(file_format='PNG'), use_compositing=True)
    cycles = NS(use_denoising=False, denoiser='OPENIMAGEDENOISE', samples=16, device='CPU')
    nodes = [NS(name='EnabledDenoise', type='DENOISE', mute=False, inputs=[], outputs=[]),
             NS(name='MutedDenoise', type='DENOISE', mute=True, inputs=[], outputs=[])]
    scene = NS(objects=objects, collection=master, camera=camera, render=render, cycles=cycles,
               use_nodes=True, node_tree=NS(nodes=nodes),
               unit_settings=NS(system='NONE', scale_length=1),
               view_settings=NS(view_transform='AgX', look='None', exposure=0, gamma=1),
               view_layers=[NS(name='Layer', cycles=NS(use_denoising=True, denoising_store_passes=False))],
               get=lambda key, default: default)
    bpy = NS(context=NS(scene=scene, view_layer=NS(update=lambda: None)),
             data=NS(collections=[room, detail], objects=objects, materials=[], images=[]),
             app=NS(version_string='pure_stub_not_Blender'))
    ib = NS(parent_chain=lambda _: [], matrix_values=lambda value: value,
            world_bounds=lambda _: None)
    source = ast.parse((ROOT / 'eval_blend.py').read_text())
    definition = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'scene_facts')
    namespace = {'bpy': bpy, 'ib': ib, 'json': json, 'Path': Path}
    original = regression.geometric_checks
    regression.geometric_checks = lambda: {'pure_stub': True}
    try:
        exec(compile(ast.Module(body=[definition], type_ignores=[]), 'scene_facts_contract', 'exec'), namespace)
        facts = namespace['scene_facts']()
        authored = facts['authored_render_configuration']
        assert authored['engine'] == 'BLENDER_EEVEE_NEXT' and authored['cycles_use_denoising'] is False
        assert authored['view_layer_denoising'][0]['use_denoising'] is True
        assert [node['enabled_in_compositor'] for node in authored['compositor_denoise_nodes']] == [True, False]
        assert {row['object_id'] for row in facts['authored_cameras']} == {'AuthorCam', 'DetailCam'}
        room_fact = next(row for row in facts['collections'] if row['name'] == 'Room')
        assert room_fact['parents'] == ['Scene Collection'] and room_fact['children'] == ['Details']
        assert room_fact['direct_object_ids'] == ['DetailCam', 'Label']
        assert next(row for row in facts['objects'] if row['object_id'] == 'Label')['text_body'] == 'Actual native label'
        scene.use_nodes = False
        assert namespace['scene_facts']()['authored_render_configuration']['compositor_denoise_nodes'] == []
    finally:
        regression.geometric_checks = original
    out = ROOT / 'preparation' / 'native_evidence_contract'
    out.mkdir(parents=True, exist_ok=False)
    (out / 'test_results.json').write_text(json.dumps({
        'status': 'passed', 'test_type': 'pure_stub_actual_collector_function',
        'checked': ['saved_engine_not_evaluator_engine', 'separate_Cycles_and_viewlayer_denoise',
                    'unmuted_vs_muted_compositor_nodes', 'all_authored_cameras', 'collection_parents_children_members',
                    'actual_FONT_body', 'disabled_compositor'],
        'native_evidence_version': facts['native_evidence_version'],
        'Blender_jobs': 0, 'model_calls': 0, 'renders': 0,
        'limits': 'Contract only; root must perform the planned actual inspect-only Blender pass before rejudging.'
    }, ensure_ascii=False, indent=2) + '\n')
    print('Seven native scene-fact stub contracts passed; no Blender/model/render calls.')


if __name__ == '__main__':
    main()
