"""Record the fixed-evaluator amendment, retaining the actual first proposal."""
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


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    target = ROOT / 'configs/amendment_03.json'
    snapshot = ROOT / 'code_snapshots/platform_A03'
    if target.exists() or snapshot.exists():
        raise RuntimeError('A03 freeze already exists; no frozen source was replaced')
    assert read(ROOT / 'launches/003_resume.json')['status'] == 'failed'
    assert not list((ROOT / 'rounds').glob('*/record.json'))
    assert not (ROOT / 'protocol_pause.json').exists()
    assert not (ROOT / 'service_pause.json').exists()
    check = read(ROOT / 'preparation/lighting_evidence_A03/controlled_evaluator_check.json')
    assert check['status'] == 'passed'
    inspection = read(ROOT / 'preparation/lighting_evidence_A03/inspection_summary.json')
    assert inspection['status'] == 'passed' and len(inspection['artifacts']) == 26
    proposal = read(ROOT / 'candidates/C01/proposal.json')
    assert proposal['changes'] and all(change['target'] == 'H' for change in proposal['changes'])
    for change in proposal['changes']:
        assert (ROOT / 'candidates/C01/H' / change['path']).read_text() == change['content']
    assert read(ROOT / 'candidates/C01/worker_summary.json')['sessions'] == 1
    config = read(ROOT / 'config.json')
    assert config['pilot']['reserve_fraction'] == .25 and config['pilot']['boundary_case_limit'] == 1
    assert config['evaluation']['promotion_delta'] == 2
    assert config['model']['name'] == 'gpt-6.1-terra'
    config['pilot']['status'] = 'A03_frozen_after_first_proposal_before_first_H_decision'
    write(ROOT / 'config.json', config)
    record = {
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'version': config['pilot']['platform_version'], 'code_snapshot': 'code_snapshots/platform_A03',
        'nature': 'As-run fixed evaluator repair after one actual M proposal; not pre-registration or an M descendant',
        'protocol': 'PROTOCOL_AMENDMENT_03.md', 'previous_freezes': ['configs/freeze.json', 'configs/amendment_01.json', 'configs/amendment_02.json'],
        'formal_rounds_completed': 0, 'M_proposals_already_returned': 1,
        'first_M_platform': 'code_snapshots/platform_A02', 'first_M_program': 'initial_m/meta.py',
        'first_proposal': 'candidates/C01/proposal.json', 'first_proposal_kind': 'H-only',
        'first_proposal_actual_M_sessions': 1, 'first_proposal_actions': 0,
        'proposal_source_exactly_preserved': True, 'M_resampling': False,
        'interrupted_generation': 'preparation/lighting_evidence_A03/operator_interrupted_generation.json',
        'selection_repeats': 'configs/selection_repeats.json', 'selection_rationale': 'configs/selection_repeat_rationale.json',
        'original_artifacts_retained_in_place': True,
        'native_evidence_version': config['evaluation']['native_evidence_version'],
        'inspection_artifacts': 26, 'inspection_new_renders': 0,
        'evaluator_check': check,
        'calibration': {'source': 'preparation/bw_calibration_A02/calibration.json',
                        'promotion_delta': 2, 'new_lighting_noise_recalibrated': False},
        'total_caps_unchanged': {key: config['pilot'][key] for key in ['max_cli_sessions','max_render_frames','max_input_tokens','max_output_tokens']},
        'minimum_final_reserve': .25, 'complete_boundary_case_limit': 1,
        'budget_forecast': 'configs/budget_A03_25percent.json', 'forecast_is_guarantee': False,
        'actual_usage_at_freeze': current(), 'engineering_change_only': True,
    }
    snapshot.mkdir()
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in {'.py', '.md'}:
            shutil.copy2(path, snapshot / path.name)
    for name in ['backend', 'initial_m', 'fixed_h']:
        shutil.copytree(ROOT / name, snapshot / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ['config.json', 'manifest.json']:
        shutil.copy2(ROOT / name, snapshot / name)
    (snapshot / 'configs').mkdir()
    for name in ['selection_repeats.json', 'selection_repeat_rationale.json']:
        shutil.copy2(ROOT / 'configs' / name, snapshot / 'configs' / name)
    write(snapshot / 'PLATFORM_SNAPSHOT.json', record)
    write(target, record)
    state = read(ROOT / 'state.json')
    write(ROOT / 'preparation/lighting_evidence_A03/state_before_activation.json', state)
    state.update(platform_version=record['version'], phase='A03_resume_ready')
    write(ROOT / 'state.json', state)
    print(json.dumps({'status': 'frozen', 'version': record['version'], 'M_proposals_preserved': 1,
                      'rounds_completed': 0, 'usage': record['actual_usage_at_freeze']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
