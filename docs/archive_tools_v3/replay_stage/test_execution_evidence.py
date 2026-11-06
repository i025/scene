"""Pure, synthetic provenance fixtures; no model, Blender, or M code execution."""
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frozen_replay_evidence', HERE / 'frozen_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def run():
    cases = []
    with tempfile.TemporaryDirectory(prefix='scene_v3_M_evidence_') as raw:
        root = Path(raw)
        m0, changed, trace = root / 'M0', root / 'M1', root / 'later_trace'
        m0.mkdir(); changed.mkdir()
        base_meta = 'def research(context, api):\n    return {"decision": "stop"}\n'
        for folder in [m0, changed]:
            (folder / 'meta.py').write_text(base_meta)
            (folder / 'helper.py').write_text('def plan():\n    return 1\n')
            (folder / 'actions').mkdir()
        action_source = 'def run(context):\n    return {"measured": 2}\n'
        (changed / 'actions/new_measure.py').write_text(action_source)
        execution = root / 'M_program_execution.json'
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'),
                                 'loaded_M_helpers': [str(changed / 'meta.py')]})

        def check(name, expected):
            result = replay.m_changed_content_execution(changed, m0, execution, trace)
            assert result['eligible'] is expected, (name, result)
            cases.append({'test': name, 'passed': True,
                          'executed_changed_files': result.get('executed_changed_files', [])})

        check('Action library only visible in source/prompt is insufficient', False)
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'),
                                 'loaded_M_helpers': [str(changed / 'actions/new_measure.py')]})
        check('Importing an action without completed action run is insufficient', False)
        action_folder = trace / 'actions/01'; action_folder.mkdir(parents=True)
        snapshot = action_folder / 'action.py'; snapshot.write_text(action_source)
        observation = action_folder / 'observation.json'
        replay.write(observation, {'status': 'failed', 'action': 'actions/new_measure.py', 'scene_id': 'fixture_A'})
        check('Failed matching action is insufficient', False)
        replay.write(observation, {'status': 'completed', 'action': 'actions/other.py', 'scene_id': 'fixture_A'})
        check('Source match with wrong action name is insufficient', False)
        replay.write(observation, {'status': 'completed', 'action': 'actions/new_measure.py', 'scene_id': 'fixture_A'})
        snapshot.write_text(action_source + '\n# other revision\n')
        check('Name match with another source revision is insufficient', False)
        snapshot.write_text(action_source)
        check('Same trace completed action name and exact source qualifies', True)
        outside = root / 'unrelated_trace/actions/01'; outside.mkdir(parents=True)
        (outside / 'action.py').write_text(action_source)
        replay.write(outside / 'observation.json', replay.read(observation))
        observation.unlink()
        check('Completed matching action in unrelated trace does not qualify', False)
        (changed / 'actions/new_measure.py').unlink()
        (changed / 'helper.py').write_text('def plan():\n    return 2\n')
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'),
                                 'loaded_M_helpers': [str(changed / 'meta.py')]})
        check('Changed helper merely present in package is insufficient', False)
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'),
                                 'loaded_M_helpers': [str(changed / 'meta.py'), str(changed / 'helper.py')]})
        check('Changed helper logged loaded in completed later execution qualifies', True)
        (changed / 'helper.py').write_text((m0 / 'helper.py').read_text())
        (changed / 'meta.py').write_text('def research(context, api):\n    return {"decision": "propose"}\n')
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'), 'loaded_M_helpers': []})
        check('Changed meta.py with completed matching entry qualifies', True)
        replay.write(execution, {'status': 'entered', 'program': str(changed / 'meta.py'), 'loaded_M_helpers': []})
        check('Entered but incomplete M strategy does not qualify', False)
        replay.write(execution, {'status': 'completed', 'program': str(m0 / 'meta.py'), 'loaded_M_helpers': []})
        check('Completed other M program does not qualify', False)
        (changed / 'meta.py').write_text(base_meta)
        (changed / 'NOTES.md').write_text('A synthetic updated strategy description.\n')
        replay.write(execution, {'status': 'completed', 'program': str(changed / 'meta.py'), 'loaded_M_helpers': []})
        check('Documentation-only difference does not qualify', False)
    result = {'status': 'passed', 'scope': 'Synthetic source/provenance fixtures only', 'cases': cases,
              'new_model_calls': 0, 'new_Blender_jobs': 0, 'M_code_executed': False,
              'Test_pixels_specs_or_rubrics_read': False, 'ability_improvement_inferred': False}
    replay.write(HERE / 'EXECUTION_EVIDENCE_TESTS.json', result)
    print(json.dumps({'status': result['status'], 'passed_cases': len(cases),
                      'new_model_calls': 0, 'new_Blender_jobs': 0}))


if __name__ == '__main__':
    run()
