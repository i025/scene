"""Finish the frozen V3 schedule; reuse deliveries and never resample failures."""
import csv
import json
import shutil
import time
from pathlib import Path

from pilot import ROOT, H_START, cfg, manifest, read, run_scene
from data import write_json
from codex_wrapper import check_service_pause
from bw_evaluate import judge_artifact, qualification


def next_step(record, judge_sessions, retry_limit):
    if record is None:
        return 'generate'
    if not record['valid']:
        return 'keep_generation_failure'
    if record['bw']['evaluation_status'] == 'completed':
        return 'reuse_completed'
    return 'judge' if judge_sessions < 1 + retry_limit else 'keep_evaluation_failure'


def schedule():
    frozen = read(ROOT / 'final_selection_freeze.json')
    repeats = read(ROOT / 'test_repeat_plan.json')['repeats']
    return [(scene, version, repeat) for scene in manifest('test')
            for repeat in range(1, repeats + 1)
            for version in [H_START, frozen['H_best']]]


def save_schedule():
    rows = []
    for scene, version, repeat in schedule():
        folder = ROOT / 'results' / version / 'test' / scene['scene_id'] / str(repeat)
        record = read(folder / 'record.json') if (folder / 'record.json').exists() else None
        attempted = len(list(folder.glob('judge_A03_*/request.json')))
        if record is not None:
            state = 'completed' if record['bw']['evaluation_status'] == 'completed' else 'eval_failed' if record['valid'] else 'failed'
        else:
            state = 'interrupted' if list(folder.glob('student_calls/*/request.json')) else 'not_started'
        rows.append({'scene_id': scene['scene_id'], 'H_version': version, 'repeat': repeat,
                     'status': state, 'generation_success': record['valid'] if record else None,
                     'evaluation_status': record['bw']['evaluation_status'] if record else None,
                     'BW': record['bw']['S_BW'] if record else None,
                     'failure_type': record['failure_type'] if record else None,
                     'judge_sessions': attempted, 'record_path': str(folder / 'record.json')})
    path = ROOT / 'metrics/final_test_schedule.csv'
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    return rows


def recover_judge(scene, folder, record, attempted, config):
    """Use an unused, originally allowed retry on the exact saved delivery."""
    backup = folder / 'evaluation_recovery_A06'
    backup.mkdir(exist_ok=False)
    for name in ['record.json', 'bw_evidence/evaluation.json']:
        shutil.copy2(folder / name, backup / ('before_' + Path(name).name))
    judge_folder = folder / ('judge_A03_' + str(attempted + 1))
    started = time.time()
    bw = judge_artifact(folder / 'reference.png', folder / 'bw_evidence',
                        read(Path(scene['rubric_path'])), config, judge_folder)
    updated = {**record, 'bw': bw, 'evaluation_status': bw['evaluation_status'],
               'eligible': qualification('completed', bw['evaluation_status'],
                                         list(record['functional']['checks'].values()))['eligible'],
               'e2e_utility': bw['S_BW'] if bw['evaluation_status'] == 'completed' else None,
               'evaluation_recovery': {'amendment': 'A06', 'original_record': str(backup / 'before_record.json'),
                                       'original_judge_sessions': attempted,
                                       'new_judge_session': str(judge_folder),
                                       'seconds': time.time() - started,
                                       'H_regenerated': False, 'new_renders': 0}}
    write_json(folder / 'record.json', updated)
    write_json(backup / 'recovery_result.json', updated['evaluation_recovery'])
    print(json.dumps({'scene': scene['scene_id'], 'H': record['H_version'],
                      'repeat': record['repeat'], 'step': 'judge_only',
                      'evaluation_status': bw['evaluation_status'], 'BW': bw['S_BW']}), flush=True)


def run():
    config = cfg()
    frozen_text = (ROOT / 'final_selection_freeze.json').read_text()
    frozen = json.loads(frozen_text)
    if frozen['rounds'] != 10 or frozen['H_best'] != 'H04' or frozen['M_final'] != 'M07':
        raise ValueError('This completion entry is for the existing frozen V3 experiment')
    if len(schedule()) != 24 or config['pilot']['retry_limit'] != 1:
        raise ValueError('Frozen 24-slot schedule or common one-retry rule changed')
    check_service_pause()
    write_json(ROOT / 'budget_phase.json', {'phase': 'final'})
    save_schedule()
    for scene, version, repeat in schedule():
        check_service_pause()
        folder = ROOT / 'results' / version / 'test' / scene['scene_id'] / str(repeat)
        record = read(folder / 'record.json') if (folder / 'record.json').exists() else None
        attempted = len(list(folder.glob('judge_A03_*/request.json')))
        step = next_step(record, attempted, config['pilot']['retry_limit'])
        try:
            if step == 'generate':
                run_scene(scene, version, frozen['M_final'], repeat)
            elif step == 'judge':
                recover_judge(scene, folder, record, attempted, config)
        finally:
            save_schedule()
        if (ROOT / 'final_selection_freeze.json').read_text() != frozen_text:
            raise RuntimeError('Final selection changed; stop without selecting from Test')
    # Complete only the four text-editor tasks fixed before formal round 1.
    from semantic_edit import run_edit
    for scene_id in config['pilot']['semantic_edit_subset']:
        for version in [H_START, frozen['H_best']]:
            folder = ROOT / 'results' / version / 'development' / scene_id / '1'
            output = ROOT / 'semantic_edits' / version / scene_id
            if (output / 'status.json').exists():
                continue
            check_service_pause()
            run_edit(scene_id, folder / 'scene.blend', folder / 'final.png',
                     read(folder / 'bw_evidence/scene_facts.json'), config, output)
    state = read(ROOT / 'state.json')
    state.update(phase='all_scheduled_terminal', round_completed=10,
                 meta_replay_status='pending_budget_and_actual_descendant_check')
    write_json(ROOT / 'state.json', state)
    rows = save_schedule()
    write_json(ROOT / 'FINAL_TEST_COMPLETION.json', {
        'time': time.time(), 'amendment': 'A06', 'scheduled': 24,
        'generation_success': sum(row['generation_success'] is True for row in rows),
        'BW_completed': sum(row['evaluation_status'] == 'completed' for row in rows),
        'statuses': {status: sum(row['status'] == status for row in rows)
                     for status in ['completed', 'failed', 'eval_failed', 'not_started', 'interrupted']},
        'H_best': frozen['H_best'], 'M_final': frozen['M_final'],
        'final_selection_text_unchanged': True, 'additional_research_rounds': 0})


if __name__ == '__main__':
    run()
