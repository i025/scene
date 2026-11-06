"""Record one prospective pre-M amendment; preserve all preceding experiment data."""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / 'outputs/scene_rsi_v3'
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from budget import current


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    target = ROOT / 'configs/amendment_02.json'
    snapshot = ROOT / 'code_snapshots/platform_A02'
    if target.exists() or snapshot.exists():
        raise RuntimeError('A02 freeze already exists; never replace a frozen platform')
    assert not list((ROOT / 'rounds').glob('*/record.json'))
    assert not list((ROOT / 'candidates').glob('*/research_started.json'))
    assert not (ROOT / 'service_pause.json').exists()
    assert not (ROOT / 'protocol_pause.json').exists()
    launch = read(ROOT / 'launches/002_resume.json')
    assert isinstance(launch['finished'], (int, float)) and launch['returncode'] != 0
    calibration = read(ROOT / 'preparation/bw_calibration_A02/calibration.json')
    assert calibration['completed'] == 20 and calibration['eval_failed'] == 0
    assert not calibration['manual_review_pending']
    assert all(row['criterion_detected_expected_problem'] for row in calibration['known_problem_detection'])
    checked = read(ROOT / 'preparation/M_validation_boundary_A02/corrected_selection_check.json')
    assert checked['status'] == 'passed' and checked['new_H_calls'] == checked['new_renders'] == 0
    assert read(ROOT / 'preparation/M_validation_boundary_A02/contracts_A02.json')['status'] == 'passed'
    config = read(ROOT / 'config.json')
    assert config['model']['name'] == 'gpt-6.1-terra'
    assert config['evaluation']['promotion_delta'] == calibration['promotion_delta_recommendation']
    config['pilot']['status'] = 'A02_frozen_before_first_formal_M'
    write(ROOT / 'config.json', config)
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        'version': config['pilot']['platform_version'], 'time_utc': timestamp,
        'nature': 'Prospective pre-first-M amendment after observed round0 evaluator failure; original freeze/as-run history retained',
        'original_freeze': 'configs/freeze.json', 'previous_platform': 'code_snapshots/platform_A01',
        'code_snapshot': 'code_snapshots/platform_A02', 'protocol': 'PROTOCOL_AMENDMENT_02.md',
        'formal_M_rounds_completed': 0, 'formal_M_proposals_started': 0,
        'old_formal_started_flag_scope': 'Earlier launcher included baseline round0; it does not mean a formal M proposal occurred',
        'baseline_H_generated': {'development': 12, 'selection': 2},
        'original_scores_and_failures_preserved': True,
        'calibration': {'path': config['evaluation']['calibration_report'], 'completed': 20,
                        'eval_failed': 0, 'maximum_repeat_difference': calibration['maximum_absolute_repeat_difference'],
                        'promotion_delta': config['evaluation']['promotion_delta'], 'human_validation': False},
        'resource_scope': config['resources'],
        'research_scope': {'rounds': 10, 'development_sources': 12, 'development_per_round': 3,
                           'M_sessions_per_round': 3, 'selection_sources': 3, 'selection_absolute_coverage': '3/3',
                           'final_test_sources': 6, 'preferred_test_repeat_rule_unchanged': True,
                           'unused_source_by_original_order': 'bw_0085', 'boundary_complete_case_limit': 2},
        'budget_estimate': 'configs/budget_pre_M_A02.json; mean estimates are not token guarantees',
        'caps': {key: config['pilot'][key] for key in ['max_cli_sessions','max_render_frames','max_input_tokens','max_output_tokens','reserve_fraction']},
        'actual_usage_at_freeze': current(),
        'acceptance_evidence': ['preparation/M_validation_boundary_A02/contracts_A02.json',
                               'preparation/M_validation_boundary_A02/tests.json',
                               'preparation/M_validation_boundary_A02/action_reuse_contract_portable/tests.json',
                               'preparation/evaluator_A02/inspection_summary.json',
                               'preparation/M_validation_boundary_A02/corrected_selection_check.json'],
        'engineering_changes_not_automatic_M_descendants': True,
        'intermediate_preparation_source_snapshots': 'Some initial intermediate variants were not separately saved; documented diffs and preceding complete snapshots remain',
    }
    snapshot.mkdir()
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in {'.py', '.md'}:
            shutil.copy2(path, snapshot / path.name)
    for name in ['backend', 'initial_m', 'fixed_h']:
        shutil.copytree(ROOT / name, snapshot / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ['config.json', 'manifest.json']:
        shutil.copy2(ROOT / name, snapshot / name)
    write(snapshot / 'PLATFORM_SNAPSHOT.json', record)
    write(target, record)
    state = read(ROOT / 'state.json')
    state.update(platform_version=record['version'], phase='baseline_selection_A02_ready')
    write(ROOT / 'state_before_A02_activation.json', read(ROOT / 'state.json'))
    write(ROOT / 'state.json', state)
    print(json.dumps({'status': 'frozen', 'time': timestamp, 'snapshot': str(snapshot),
                      'promotion_delta': config['evaluation']['promotion_delta'],
                      'formal_M_rounds_completed': 0, 'usage': record['actual_usage_at_freeze']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
