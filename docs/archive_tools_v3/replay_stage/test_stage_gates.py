"""Pure startup/threshold checks; no stage, model, Blender or evaluator execution."""
import fcntl
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('replay_stage_gates', HERE / 'frozen_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def run():
    tests = []
    with tempfile.TemporaryDirectory(prefix='scene_v3_replay_gates_') as raw:
        main, stage = Path(raw) / 'main', Path(raw) / 'stage'
        main.mkdir()
        for rounds, phase, existing in [(0, 'generation', False), (0, 'generation', True),
                                        (0, 'all_scheduled_terminal', True), (10, 'generation', True)]:
            replay.write(main / 'state.json', {'round_completed': rounds, 'phase': phase})
            if existing:
                stage.mkdir(exist_ok=True)
                replay.write(stage / 'state.json', {'phase': 'prepared_not_executed'})
            with (patch.object(replay, 'prepare', side_effect=AssertionError('Preparation must not execute')),
                  patch.object(replay, 'load_platform', side_effect=AssertionError('Runtime must not load'))):
                try:
                    replay.run(main, stage)
                except RuntimeError as error:
                    assert 'Main ten rounds and scheduled endpoint work are not terminal' in str(error)
                else:
                    raise AssertionError('Nonterminal main unexpectedly allowed stage work')
            tests.append({'rounds': rounds, 'phase': phase, 'existing_stage': existing,
                          'blocked_before_preparation_or_runtime': True})
        replay.write(main / 'state.json', {'round_completed': 10, 'phase': 'all_scheduled_terminal'})
        with (main / 'experiment.lock').open('w') as owned:
            fcntl.flock(owned, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _, problems = replay.main_completion_check(main)
            assert any('exclusive flock' in reason for reason in problems)
        tests.append({'test': 'Terminal JSON while launcher still owns lock remains blocked', 'passed': True})
        _, problems = replay.main_completion_check(main)
        assert not problems
        tests.append({'test': 'Main terminal and unlocked passes only completion prerequisite, not replay eligibility', 'passed': True})
    parent = {'eligible': True, 'valid': True, 'bw': {'evaluation_status': 'completed', 'S_BW': 80},
              'functional': {'functional_pass': True}}
    candidate = {**parent, 'bw': {'evaluation_status': 'completed', 'S_BW': 85}}
    assert replay.choose(candidate, parent, 6.25)[0] is False
    assert replay.choose(candidate, parent, 4.5)[0] is True
    tests.append({'test': 'Threshold argument controls acceptance; historical 2.5 is not hardcoded', 'passed': True})
    result = {'status': 'passed', 'scope': 'Synthetic source/startup/threshold tests only', 'tests': tests,
              'new_model_calls': 0, 'new_Blender_jobs': 0, 'runtime_or_evaluation_executed': False}
    replay.write(HERE / 'STAGE_GATE_TESTS.json', result)
    print(json.dumps({'status': 'passed', 'checks': len(tests), 'new_model_calls': 0, 'new_Blender_jobs': 0}))


if __name__ == '__main__':
    run()
