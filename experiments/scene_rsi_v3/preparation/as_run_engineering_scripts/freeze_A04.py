"""Record a lossless packet-encoding repair after six completed rounds."""
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2] / 'outputs/scene_rsi_v3'
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from budget import current


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    destination = ROOT / 'configs/amendment_04.json'
    snapshot = ROOT / 'code_snapshots/platform_A04'
    evidence = ROOT / 'preparation/context_budget_A04'
    assert not destination.exists() and not snapshot.exists()
    assert read(ROOT / 'launches/004_resume.json')['returncode'] == 1
    assert len(list((ROOT / 'rounds').glob('*/record.json'))) == 6
    assert not (ROOT / 'candidates/C07/research_started.json').exists()
    assert read(evidence / 'tests.json')['status'] == 'passed'
    assert (ROOT / 'candidates/C07/H/policy.py').read_text() == (ROOT / 'candidates/C04/H/policy.py').read_text()
    assert (ROOT / 'candidates/C07/M/meta.py').read_text() == (ROOT / 'initial_m/meta.py').read_text()
    config = read(ROOT / 'config.json')
    assert config == read(evidence / 'before_A04_config.json')
    config['pilot']['research_packet_version'] = 'A04_lossless_compact_JSON'
    config['pilot']['platform_snapshot'] = 'code_snapshots/platform_A04'
    config['pilot']['status'] = 'A04_after_round6_before_first_round7_M'
    write(ROOT / 'config.json', config)
    failure = {'phase': 'evidence_packaging', 'error': read(evidence / 'failure_analysis.json')['error'],
               'round_complete': False, 'M_call_started': False, 'candidate_produced': False,
               'launch': 'launches/004_resume.json', 'failure_class': 'fixed_platform_context_byte_limit'}
    write(ROOT / 'rounds/07/interrupted.json', failure)
    changes = []
    for name in ['model_evidence.py', 'research.py', 'pilot.py', 'analyze.py']:
        before = ROOT / 'code_snapshots/platform_A03' / name
        after = ROOT / name
        changes.extend(difflib.unified_diff(before.read_text().splitlines(True), after.read_text().splitlines(True),
                                           fromfile='platform_A03/' + name, tofile='platform_A04/' + name))
    (evidence / 'platform.diff').write_text(''.join(changes))
    for name in ['metrics', 'figures', 'reports']:
        shutil.copytree(ROOT / name, evidence / ('before_A04_' + name))
    record = {'time_utc': datetime.now(timezone.utc).isoformat(),
              'nature': 'as-run lossless JSON encoding repair; not an M descendant',
              'first_effective_round': 7, 'completed_rounds_preserved': 6,
              'evaluation_platform_version_unchanged': config['pilot']['platform_version'],
              'research_packet_version': config['pilot']['research_packet_version'],
              'code_snapshot': str(snapshot.relative_to(ROOT)),
              'protocol': 'PROTOCOL_AMENDMENT_04.md', 'failure': failure,
              'tests': read(evidence / 'tests.json'), 'H_M_sources_unchanged': True,
              'new_model_calls': 0, 'new_Blender_jobs': 0, 'M_resampling': False,
              'actual_usage_at_freeze': current(), 'final_reserve_fraction': .25,
              'total_caps_unchanged': {key: config['pilot'][key] for key in
                   ['max_cli_sessions', 'max_render_frames', 'max_input_tokens', 'max_output_tokens']}}
    snapshot.mkdir()
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in {'.py', '.md'}:
            shutil.copy2(path, snapshot / path.name)
    for name in ['backend', 'initial_m', 'fixed_h']:
        shutil.copytree(ROOT / name, snapshot / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ['config.json', 'manifest.json']:
        shutil.copy2(ROOT / name, snapshot / name)
    for name in ['selection_repeats.json', 'selection_repeat_rationale.json']:
        target = snapshot / 'configs' / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'configs' / name, target)
    write(snapshot / 'PLATFORM_SNAPSHOT.json', record)
    write(destination, record)
    state = read(ROOT / 'state.json')
    assert state['round_completed'] == 6 and state['H_retained'] == 'H04' and state['M_retained'] == 'M000'
    state.update(phase='A04_resume_ready', research_packet_version=config['pilot']['research_packet_version'],
                 platform_snapshot=config['pilot']['platform_snapshot'])
    write(ROOT / 'state.json', state)
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
