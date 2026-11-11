"""Small deterministic recovery checks; fixture numbers are not measurements."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
import finish_test

checks = []
record = {'valid': True, 'bw': {'evaluation_status': 'completed'}}
assert finish_test.next_step(record, 1, 1) == 'reuse_completed'
assert finish_test.next_step({'valid': False}, 0, 1) == 'keep_generation_failure'
failed = {'valid': True, 'bw': {'evaluation_status': 'eval_failed'}}
assert finish_test.next_step(failed, 1, 1) == 'judge'
assert finish_test.next_step(failed, 2, 1) == 'keep_evaluation_failure'
assert finish_test.next_step(None, 0, 1) == 'generate'
checks.append('Completed deliveries and generation failures never request regeneration; evaluation retry is bounded at two actual sessions')

with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    (folder / 'bw_evidence').mkdir()
    (folder / 'scene.blend').write_bytes(b'fixture-only-not-a-real-blend')
    (folder / 'scene.py').write_text('# fixed fixture program\n')
    (folder / 'rubric.json').write_text('{}')
    old = {**failed, 'H_version': 'fixture', 'repeat': 2, 'metrics': {'overall': 0.1},
           'functional': {'checks': {'fixture': {'required': True, 'applicable': True,
                                                'measured_pass': True, 'gate_pass': True}}}}
    (folder / 'record.json').write_text(json.dumps(old))
    (folder / 'bw_evidence/evaluation.json').write_text(json.dumps(old['bw']))
    calls = []
    def judge(reference, evidence, rubric, config, destination):
        calls.append((reference, evidence, destination))
        return {'evaluation_status': 'completed', 'S_BW': 42}
    finish_test.judge_artifact = judge
    finish_test.recover_judge({'scene_id': 'fixture', 'rubric_path': str(folder / 'rubric.json')},
                             folder, old, 1, {})
    new = json.loads((folder / 'record.json').read_text())
    assert len(calls) == 1 and calls[0][2].name == 'judge_A03_2'
    assert (folder / 'scene.blend').read_bytes() == b'fixture-only-not-a-real-blend'
    assert (folder / 'scene.py').read_text() == '# fixed fixture program\n'
    assert json.loads((folder / 'evaluation_recovery_A06/before_record.json').read_text()) == old
    assert new['metrics'] == old['metrics'] and new['functional'] == old['functional']
    assert new['evaluation_recovery']['H_regenerated'] is False
    assert new['evaluation_recovery']['new_renders'] == 0
    checks.append('Judge-only recovery preserves old failure, generated program, blend and numerical/function measurements')

output = Path(__file__).with_name('test_results.json')
output.write_text(json.dumps({'status': 'passed', 'checks': checks, 'fixture_only': True,
                              'new_model_calls': 0, 'new_Blender_jobs': 0}, indent=2) + '\n')
print(json.dumps(checks))
