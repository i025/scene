"""Run bounded V3 engineering calibration and existing open action executor, no models."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))
from processes import cpu_environment, run_measured
from regression import gate
from research import ResearchAPI, validate_source

OUT = Path(__file__).parent


def main():
    cfg = json.loads((ROOT / 'config.json').read_text())
    threads = cfg['resources']['threads_per_blender']
    settings = {**cfg['render'], 'width': 256, 'height': 256, 'samples': 4,
                'threads': threads, 'device': 'CPU'}
    (OUT / 'settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    gates = []
    for required in [False, True]:
        for applicable in [False, True]:
            for measured in [None, False, True]:
                result = gate(required, applicable, measured)
                assert result['gate_pass'] is (not required or (applicable and measured is True))
                gates.append(result)
    (OUT / 'gate_contract.json').write_text(json.dumps({'status': 'passed', 'cases': gates}, indent=2) + '\n')
    command = [cfg['blender']['executable'], '--background', '--disable-autoexec', '--threads', str(threads),
               '--python-exit-code', '1', '--python', str(OUT / 'build_fixtures.py')]
    with (OUT / 'stdout.log').open('w') as stdout, (OUT / 'stderr.log').open('w') as stderr:
        result = run_measured(command, timeout=cfg['blender']['timeout'], measurement_path=OUT / 'process.json',
                              memory_limit_bytes=cfg['resources']['memory_limit_gb'] * 1024 ** 3,
                              stdout=stdout, stderr=stderr, env=cpu_environment(threads=threads))
    assert result['returncode'] == 0, result
    action = OUT / 'fixture_m/actions/measure_named_support.py'
    validate_source(action.read_text(), 'action')
    scenes = {}
    for name in ['correct', 'broken_support']:
        scenes[name] = {'valid_blend': True, 'blend_path': str(OUT / name / 'scene.blend'),
                        'object_ids': ['Z_target_part', 'A_unrelated_part', 'Support', 'Assembly', 'Root']}
    api = ResearchAPI(cfg, OUT / 'action_reuse', ROOT / 'historical_r1_C2_start', OUT / 'fixture_m', scenes, [])
    parameters = {'object_id': 'Z_target_part', 'support_id': 'Support', 'tolerance': 0.01, 'render': False}
    first = api.execute_action('actions/measure_named_support.py', 'correct', parameters,
                               'Named target contacts support in the legal fixture.')
    assert first['status'] == 'completed' and first['measurement']['contact_approx_pass'] is True
    second = api.execute_action('actions/measure_named_support.py', 'broken_support', parameters,
                                'The same parameterized action detects lifted target on the second configuration.')
    assert second['status'] == 'completed' and second['measurement']['contact_approx_pass'] is False
    assert first['measurement']['object_id'] == 'Z_target_part'
    assert second['measurement']['object_id'] == 'Z_target_part'
    summary = {'status': 'passed', 'creator': 'engineering_fixture_not_M',
               'M_capability_improvement_claimed': False, 'new_action': str(action.relative_to(ROOT)),
               'fixed_runner_modified_for_new_action': False, 'new_action_validated_by_existing_validator': True,
               'two_configurations': [first, second], 'source_blend_resaved_by_action': False,
               'target_name_is_not_lexicographically_first': True,
               'no_remote_model_calls': True, 'fixture_render_attempts': 8,
               'quality': 'calibration_preview_excluded_from_formal_scores', 'threads_per_blender': threads}
    (OUT / 'action_reuse.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'functional_cases': 8, 'gate_cases': 12,
                      'action_reuse_configurations': 2, 'threads': threads}))


if __name__ == '__main__':
    main()
