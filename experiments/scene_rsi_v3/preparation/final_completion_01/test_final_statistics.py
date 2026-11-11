"""Source weighting and missing-data counterexamples; no experiment measurements."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from final_statistics import QUALITY, aggregate, bootstrap

scenes = [{'scene_id': str(i), 'source_id': str(i)} for i in range(6)]
versions = ['start_fixture', 'best_fixture']
rows = []
for scene in scenes:
    for version in versions:
        for repeat in [1, 2]:
            value = 10 if version == versions[0] else 20 if scene['scene_id'] == '0' else 30
            rows.append({'scene_id': scene['scene_id'], 'H_version': version, 'repeat': repeat,
                         'generation_success': True, 'generation_status': 'completed',
                         'evaluation_status': 'completed', 'failure_type': None,
                         'evaluation_failure_type': None, 'function_gate_pass': True,
                         'BW_utility': value, **{key: value for key in QUALITY}})
failure = next(r for r in rows if r['scene_id'] == '0' and r['H_version'] == versions[1] and r['repeat'] == 2)
failure.update(generation_success=False, generation_status='failed', BW_utility=0,
               evaluation_status='not_started', failure_type='fixture_service_failure',
               function_gate_pass=False, **{key: None for key in QUALITY})
sources, endpoints, differences = aggregate(scenes, versions, rows)
assert abs(endpoints[1]['BW_source_equal_conditional_mean'] - 170 / 6) < 1e-9
assert abs(endpoints[1]['BW_completed_task_conditional_mean'] - 320 / 11) < 1e-9
assert abs(differences['BW']['mean'] - 110 / 6) < 1e-9
assert abs(differences['BW_utility']['mean'] - 100 / 6) < 1e-9
assert differences['BW']['sources'] == 6
checks = ['Unequal completed repeats retain six source weights; conditional quality and failure-zero utility differ']

pending_eval = copy.deepcopy(rows)
row = next(r for r in pending_eval if r['scene_id'] == '0' and r['H_version'] == versions[1] and r['repeat'] == 2)
row.update(generation_success=True, generation_status='completed', BW_utility=None,
           evaluation_status='eval_failed', failure_type=None,
           evaluation_failure_type='fixture_external_judge_failure')
_, endpoints, differences = aggregate(scenes, versions, pending_eval)
assert endpoints[1]['BW_utility_all_scheduled'] is None
assert differences['BW_utility']['ci95'] is None
checks.append('Evaluator failure is never silently assigned zero utility')

unstarted = copy.deepcopy(rows)
for row in unstarted:
    if row['scene_id'] == '0' and row['H_version'] == versions[1]:
        row.update(generation_success=None, BW_utility=None,
                   generation_status='not_started', **{key: None for key in QUALITY})
_, _, differences = aggregate(scenes, versions, unstarted)
assert differences['BW']['sources'] == 5 and differences['BW']['ci95'] is None
assert bootstrap([5] * 6)['ci95'] == [5, 5]
checks.append('Pending source withholds a six-source interval; repetitions are never counted as independent sources')

Path(__file__).with_name('statistics_test_results.json').write_text(json.dumps({
    'status': 'passed', 'checks': checks, 'fixture_only': True,
    'new_model_calls': 0, 'new_Blender_jobs': 0}, indent=2) + '\n')
print(json.dumps(checks))
