"""Read saved native lighting, without reconstructing or rendering any artifact."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from data import write_json
from processes import cpu_environment, run_measured
from bw_evaluate import enrich_delivered_evidence


def read(path):
    return json.loads(path.read_text())


def preserve(path, name):
    backup = path.with_name(name)
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)


def main():
    config = read(ROOT / 'config.json')
    out = ROOT / 'preparation/lighting_evidence_A03/inspection'
    folders = sorted((ROOT / 'results').glob('*/*/*/*/bw_evidence'))
    folders += sorted((ROOT / 'preparation/bw_calibration/evidence').iterdir())
    rows = []
    for number, folder in enumerate(folders):
        if not (folder / 'scene_facts.json').exists():
            continue
        previous = read(folder / 'scene_facts.json')
        preserve(folder / 'scene_facts.json', 'scene_facts_before_A03.json')
        preserve(folder / 'evidence_status.json', 'evidence_status_before_A03.json')
        preserve(folder / 'evaluation.json', 'evaluation_before_A03.json')
        preserve(folder.parent / 'record.json', 'record_before_A03_evaluator.json')
        dest = out / f'I{number:03d}'
        dest.mkdir(parents=True, exist_ok=True)
        process_file = dest / 'process.json'
        if not process_file.exists():
            command = [config['blender']['executable'], '--background', '--disable-autoexec',
                       '--threads', '8', '--python-exit-code', '2', '--python',
                       str(ROOT / 'eval_blend.py'), '--', '--blend', str(folder / 'artifact.blend'),
                       '--folder', str(dest), '--settings', str(folder / 'settings.json')]
            with (dest / 'stdout.log').open('w') as stdout, (dest / 'stderr.log').open('w') as stderr:
                run_measured(command, timeout=config['blender']['build_timeout'],
                             measurement_path=process_file, memory_limit_bytes=32 * 1024**3,
                             stdout=stdout, stderr=stderr, env=cpu_environment(threads=8))
        assert read(process_file)['returncode'] == 0, str(dest)
        facts = read(dest / 'scene_facts.json')
        assert facts['native_evidence_version'] == 'authored_native_project_facts_A03_lighting'
        assert facts['blend_opened'] and facts['mesh_count'] == previous['mesh_count']
        assert [v['object_id'] for v in facts['objects']] == [v['object_id'] for v in previous['objects']]
        assert len(facts['authored_lights']) == sum(v['type'] == 'LIGHT' for v in facts['objects'])
        shutil.copy2(dest / 'scene_facts.json', folder / 'scene_facts.json')
        status = enrich_delivered_evidence(folder)
        assert status['native_evidence_version'] == facts['native_evidence_version']
        if (folder / 'evaluation.json').exists():
            (folder / 'evaluation.json').rename(folder / 'evaluation_superseded_A03.json')
        rows.append({'evidence': str(folder), 'inspection': str(dest),
                     'light_count': len(facts['authored_lights']),
                     'world_present': facts['authored_world'] is not None,
                     'native_version': facts['native_evidence_version'], 'new_renders': 0})
        print('A03 inspect', number, folder.parent.name, len(facts['authored_lights']), flush=True)
    write_json(out.parent / 'inspection_summary.json', {
        'status': 'passed', 'artifacts': rows, 'new_H_calls': 0, 'new_judge_calls': 0,
        'new_renders': 0, 'calibration_scores': 'Existing A02 calibration judgments untouched; A03 lighting fields were not separately noise-calibrated',
    })


if __name__ == '__main__':
    main()
