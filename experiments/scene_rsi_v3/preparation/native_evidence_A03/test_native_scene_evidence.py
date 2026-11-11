"""Pure stub contract for native scene-fact fields; does not launch Blender."""
import ast
import argparse
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[2] / 'outputs' / 'scene_rsi_v3'


class NamedRows(list):
    def __contains__(self, value):
        return any(row.name == value for row in self) if isinstance(value, str) else super().__contains__(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root))
    import regression
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
    def socket(identifier, default_value=None, is_linked=False):
        return NS(identifier=identifier, default_value=default_value, is_linked=is_linked)
    emission = NS(name='Emission', type='EMISSION', bl_idname='ShaderNodeEmission', mute=False,
                  inputs=[socket('Color', (0.4, 0.6, 1.0, 1.0)), socket('Strength', 2.0)],
                  outputs=[NS(identifier='Emission')])
    light_output = NS(name='Light Output', type='OUTPUT_LIGHT', bl_idname='ShaderNodeOutputLight',
                      mute=False, is_active_output=True,
                      inputs=[NS(identifier='Surface', is_linked=True)], outputs=[])
    light_link = NS(from_node=emission, from_socket=emission.outputs[0],
                    to_node=light_output, to_socket=light_output.inputs[0])
    area_data = NS(name='Cool overhead data', type='AREA', color=(0.4, 0.6, 1.0),
                   energy=750.0, use_nodes=True, use_shadow=True, shape='RECTANGLE', size=4.0,
                   size_y=6.0, node_tree=NS(nodes=[light_output, emission], links=[light_link]))
    area = Object(**vars(obj('Cool overhead', 'LIGHT', area_data)))
    sun_data = NS(name='Sun data', type='SUN', color=(1.0, 0.9, 0.8), energy=1.5,
                  use_nodes=False, use_shadow=False, angle=0.1, node_tree=None)
    sun = Object(**vars(obj('Sun', 'LIGHT', sun_data)))
    point_data = NS(name='Unlinked point data', type='POINT', color=(1.0, 1.0, 1.0), energy=100.0,
                    use_nodes=False, use_shadow=True, shadow_soft_size=0.25, node_tree=None)
    unlinked_point = Object(**vars(obj('Unlinked point', 'LIGHT', point_data)))
    objects = NamedRows([camera, secondary, text, area, sun])
    detail = NS(name='Details', children=NamedRows(), objects=NamedRows(), hide_render=True)
    room = NS(name='Room', children=NamedRows([detail]), objects=NamedRows([secondary, text]), hide_render=False)
    master = NS(name='Scene Collection', children=NamedRows([room]), objects=NamedRows([camera]), hide_render=False)
    render = NS(engine='BLENDER_EEVEE_NEXT', resolution_x=374, resolution_y=512, resolution_percentage=100,
                image_settings=NS(file_format='PNG'), use_compositing=True)
    cycles = NS(use_denoising=False, denoiser='OPENIMAGEDENOISE', samples=16, device='CPU')
    nodes = [NS(name='EnabledDenoise', type='DENOISE', mute=False, inputs=[], outputs=[]),
             NS(name='MutedDenoise', type='DENOISE', mute=True, inputs=[], outputs=[])]
    background = NS(name='Background', type='BACKGROUND', bl_idname='ShaderNodeBackground', mute=False,
                    inputs=[socket('Color', (0.02, 0.03, 0.04, 1.0)), socket('Strength', 0.3)],
                    outputs=[NS(identifier='Background')])
    world_output = NS(name='World Output', type='OUTPUT_WORLD', bl_idname='ShaderNodeOutputWorld',
                      mute=False, is_active_output=True,
                      inputs=[NS(identifier='Surface', is_linked=True)], outputs=[])
    world_link = NS(from_node=background, from_socket=background.outputs[0],
                    to_node=world_output, to_socket=world_output.inputs[0])
    world = NS(name='Authored world', color=(0.1, 0.2, 0.3), use_nodes=True,
               node_tree=NS(nodes=[world_output, background], links=[world_link]))
    scene = NS(objects=objects, collection=master, camera=camera, render=render, cycles=cycles, world=world,
               use_nodes=True, node_tree=NS(nodes=nodes),
               unit_settings=NS(system='NONE', scale_length=1),
               view_settings=NS(view_transform='AgX', look='None', exposure=0, gamma=1),
               view_layers=[NS(name='Layer', cycles=NS(use_denoising=True, denoising_store_passes=False))],
               get=lambda key, default: default)
    bpy = NS(context=NS(scene=scene, view_layer=NS(update=lambda: None)),
             data=NS(collections=[room, detail], objects=NamedRows([*objects, unlinked_point]), materials=[], images=[]),
             app=NS(version_string='pure_stub_not_Blender'))
    ib = NS(parent_chain=lambda _: [], matrix_values=lambda value: value,
            world_bounds=lambda _: None)
    numeric_source = ast.parse((root / 'inspect_blend.py').read_text())
    numeric_definition = next(node for node in numeric_source.body
                              if isinstance(node, ast.FunctionDef) and node.name == 'json_number')
    numeric_namespace = {'math': math}
    exec(compile(ast.Module(body=[numeric_definition], type_ignores=[]), 'native_socket_values', 'exec'), numeric_namespace)
    ib.json_number = numeric_namespace['json_number']
    source = ast.parse((root / 'eval_blend.py').read_text())
    definitions = [node for node in source.body if isinstance(node, ast.FunctionDef)
                   and node.name in {'scene_facts', 'light_values', 'lighting_node_values'}]
    namespace = {'bpy': bpy, 'ib': ib, 'json': json, 'Path': Path}
    original = regression.geometric_checks
    regression.geometric_checks = lambda: {'pure_stub': True}
    try:
        exec(compile(ast.Module(body=definitions, type_ignores=[]), 'scene_facts_contract', 'exec'), namespace)
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
        lights = {row['object_id']: row for row in facts['authored_lights']}
        assert lights['Cool overhead']['energy'] == 750.0 and lights['Cool overhead']['color'] == [0.4, 0.6, 1.0]
        assert lights['Cool overhead']['type'] == 'AREA' and lights['Cool overhead']['size'] == 4.0
        assert lights['Cool overhead']['size_y'] == 6.0 and lights['Cool overhead']['angle'] is None
        assert lights['Sun']['angle'] == 0.1 and lights['Sun']['size'] is None and lights['Sun']['use_shadow'] is False
        assert lights['Unlinked point']['shadow_soft_size'] == 0.25 and lights['Unlinked point']['angle'] is None
        assert lights['Cool overhead']['linked_to_active_scene'] is True
        assert lights['Unlinked point']['linked_to_active_scene'] is False
        assert lights['Cool overhead']['links'] == [['Emission', 'Emission', 'Light Output', 'Surface']]
        emission_fact = next(row for row in lights['Cool overhead']['nodes'] if row['name'] == 'Emission')
        assert emission_fact['inputs']['Strength'] == 2.0 and emission_fact['inputs']['Color'] == [0.4, 0.6, 1.0, 1.0]
        output_fact = next(row for row in lights['Cool overhead']['nodes'] if row['name'] == 'Light Output')
        assert output_fact['is_active_output'] is True and output_fact['input_linked']['Surface'] is True
        assert facts['authored_world']['name'] == 'Authored world' and facts['authored_world']['color'] == [0.1, 0.2, 0.3]
        assert facts['authored_world']['links'] == [['Background', 'Background', 'World Output', 'Surface']]
        world_fact = next(row for row in facts['authored_world']['nodes'] if row['name'] == 'Background')
        assert world_fact['inputs']['Strength'] == 0.3 and world_fact['inputs']['Color'] == [0.02, 0.03, 0.04, 1.0]
        assert area_data.energy == 750.0 and area_data.use_nodes is True and world.use_nodes is True
        assert area_data.node_tree.nodes == [light_output, emission] and world.node_tree.nodes == [world_output, background]
        world.use_nodes = False
        disabled_world = namespace['scene_facts']()['authored_world']
        assert disabled_world['use_nodes'] is False and disabled_world['node_tree_present'] is True
        assert disabled_world['links'] == facts['authored_world']['links']
        scene.world = None
        assert namespace['scene_facts']()['authored_world'] is None
        scene.use_nodes = False
        assert namespace['scene_facts']()['authored_render_configuration']['compositor_denoise_nodes'] == []
    finally:
        regression.geometric_checks = original
    out = args.output or root / 'preparation' / 'native_evidence_A03' / 'pure_tests'
    out.mkdir(parents=True, exist_ok=False)
    (out / 'test_results.json').write_text(json.dumps({
        'status': 'passed', 'test_type': 'pure_stub_actual_collector_function',
        'checked': ['saved_engine_not_evaluator_engine', 'separate_Cycles_and_viewlayer_denoise',
                    'unmuted_vs_muted_compositor_nodes', 'all_authored_cameras', 'collection_parents_children_members',
                    'actual_FONT_body', 'disabled_compositor'],
        'lighting_checked': ['saved_light_energy_color_type_shadow', 'AREA_dimensions_and_SUN_angle_applicability',
                             'POINT_shadow_radius', 'linked_and_unlinked_lights_distinguished',
                             'actual_light_nodes_and_links', 'saved_world_color_and_background_nodes',
                             'disabled_graph_preserved_as_disabled', 'absent_world_is_null',
                             'collection_did_not_modify_lighting'],
        'native_evidence_version': facts['native_evidence_version'],
        'Blender_jobs': 0, 'model_calls': 0, 'renders': 0,
        'limits': 'Contract only; root must perform the planned actual inspect-only Blender pass before rejudging.'
    }, ensure_ascii=False, indent=2) + '\n')
    (out / 'scene_facts_fixture.json').write_text(json.dumps(facts, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print('Seven native scene-fact contracts and nine lighting contracts passed; no Blender/model/render calls.')


if __name__ == '__main__':
    main()
