"""Archive tables and one completion plot from existing records only."""
import csv
import json
from pathlib import Path
import os
from collections import Counter

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / 'experiments/scene_rsi_pilot'


def read_csv(path):
    with path.open(encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({key: 'null' if value is None else value for key, value in row.items()} for row in rows)


def main():
    out = ROOT / 'metrics'
    scheduled = read_csv(ROOT / 'reports/main_scheduled.csv')
    calls = read_csv(ROOT / 'reports/calls.csv')
    archive = json.loads((ROOT / 'archive.json').read_text())
    runs = []
    for method in ['fixed_h0', 'sceneevolve_cli', 'generic_rsi', 'scene_rsi_pilot']:
        for run in ['r1', 'r2']:
            slots = [row for row in scheduled if row['method'] == method and row['run_id'] == run]
            candidates = [row for row in archive if row['method'] == method and row['run_id'] == run]
            model_calls = [row for row in calls if row['method'] == method and row['run_id'] == run]
            runs.append({'method': method, 'run_id': run, 'scheduled_slots': len(slots),
                'completed': sum(row['status'] == 'complete' for row in slots),
                'failed': sum(row['status'] == 'failed' for row in slots),
                'not_run_proposal_failed': sum(row['status'] == 'not_run_proposal_failed' for row in slots),
                'candidate_records': len(candidates),
                'evaluated_candidates': sum(row['status'] == 'evaluated' for row in candidates),
                'candidate_failures': sum(row['status'] == 'proposal_failed' for row in candidates),
                'active_cli_sessions': sum(row['preserved_service_attempt'] == 'False' for row in model_calls),
                'preserved_historical_cli_sessions': sum(row['preserved_service_attempt'] == 'True' for row in model_calls),
                'unit': 'logical reconstruction slot; reused H0 outputs are not new samples'})
    write_csv(out / 'runs.csv', runs)
    candidates = []
    for row in archive:
        folder = Path('candidates') / row['run_id'] / row['method'] / row['candidate_id']
        result_path = ROOT / folder / 'proposal_result.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else {}
        candidates.append({'method': row['method'], 'run_id': row['run_id'], 'candidate_id': row['candidate_id'],
            'parent': row.get('parent_id') or result.get('parent_source'), 'H_version': str(folder),
            'M_version': str(folder / 'meta.py') if (ROOT / folder / 'meta.py').exists() else None,
            'status': row['status'], 'accepted_on_selection': row['accepted'],
            'development': json.dumps(row.get('development'), ensure_ascii=False),
            'selection': json.dumps(row.get('selection'), ensure_ascii=False),
            'failure_reason': row.get('error') or result.get('error'),
            'source': str(folder / 'proposal_result.json')})
    write_csv(out / 'candidates.csv', candidates)
    attempts = []
    for prefix in ['', 'service_incident_01/retired/', 'quota_restored_20261103/retired/']:
        for folder in sorted((ROOT / prefix / 'candidates').glob('*/*/C*')):
            path = folder / 'proposal_result.json'
            value = json.loads(path.read_text()) if path.exists() else {}
            attempts.append({'attempt_phase': 'current' if not prefix else prefix.rstrip('/'),
                'run_id': folder.parts[-3], 'method': folder.parts[-2], 'candidate_id': folder.parts[-1],
                'proposal_status': value.get('status', 'no_proposal_result_saved'),
                'failure_reason': value.get('error') if path.exists() else
                    'Preparation/inherited source or probes only; no submitted proposal result saved; exact individual stopping cause unconfirmed.',
                'source': str((path if path.exists() else folder).relative_to(ROOT))})
    write_csv(out / 'all_candidate_attempts.csv', attempts)
    scenes = read_csv(ROOT / 'reports/scenes.csv')
    write_csv(out / 'scene_metrics.csv', scenes)
    totals = []
    for method in dict.fromkeys(row['method'] for row in runs):
        subset = [row for row in runs if row['method'] == method]
        totals.append({'method': method, **{key: sum(row[key] for row in subset) for key in
            ['scheduled_slots', 'completed', 'failed', 'not_run_proposal_failed', 'candidate_records', 'evaluated_candidates']}})
    write_csv(out / 'method_completion.csv', totals)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4))
    bottoms = [0] * len(totals)
    for key, color in [('completed', '#407d58'), ('failed', '#bf5b49'), ('not_run_proposal_failed', '#c8a454')]:
        values = [row[key] for row in totals]
        ax.bar(range(len(totals)), values, bottom=bottoms, label=key, color=color)
        bottoms = [a + b for a, b in zip(bottoms, values)]
    ax.set_xticks(range(len(totals)), [row['method'] for row in totals], fontsize=9)
    ax.set_ylabel('Logical scheduled reconstruction slots')
    ax.set_title('Main pilot: all 88 scheduled slots; two R&D runs per method')
    ax.legend(fontsize=8)
    fig.tight_layout()
    figures = ROOT / 'figures'
    figures.mkdir(exist_ok=True)
    fig.savefig(figures / 'main_completion.png', dpi=150)
    plt.close(fig)
    print(json.dumps({'main': totals, 'candidate_attempt_records': len(attempts), 'scene_records': len(scenes)}))


if __name__ == '__main__':
    for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS']:
        os.environ[key] = '2'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['MPLCONFIGDIR'] = str(REPO / 'derived/matplotlib')
    main()
