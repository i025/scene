import argparse
from datetime import datetime
import json
import shutil
from benchmark import copy_snapshot, evaluate, freeze, open_run
import codex_wrapper
from data import ROOT, write_json
from evidence import archive_index, candidate_evidence
from gpu_watch import before_task, refresh_report


def read_history(run_dir):
    path = run_dir / 'history.json'
    return json.loads(path.read_text()) if path.exists() else []


def record(run_dir, iteration, summary):
    history = read_history(run_dir)
    if not any(r['agent'] == summary['agent'] for r in history):
        history.append({'iteration': iteration, **{k: v for k, v in summary.items() if k != 'scenes'}})
        write_json(run_dir / 'history.json', history)
    archive_index(run_dir, history)


def update_frontier(run_dir, summary):
    path = run_dir / 'frontier_search.json'
    best = json.loads(path.read_text()) if path.exists() else None
    if best is None or summary['overall'] > best['overall']:
        best = {k: v for k, v in summary.items() if k != 'scenes'}
        write_json(path, best)
    return best


def commit_proposals(workspace, run_dir):
    prepared = json.loads((workspace / 'prepared.json').read_text())
    names = prepared['candidates']
    for name in names:
        folder = workspace / name
        destination = ROOT / 'harnesses' / name
        if not destination.exists():
            copy_snapshot(folder, destination)
        freeze(name, run_dir)
    write_json(workspace / 'proposals.json', names)
    refresh_report(run_dir)
    return names


def proposals(run_dir, config, iteration):
    workspace = run_dir / 'proposals' / f'{iteration:04d}'
    committed = workspace / 'proposals.json'
    if committed.exists(): return json.loads(committed.read_text())
    if (workspace / 'prepared.json').exists(): return commit_proposals(workspace, run_dir)
    before_task(run_dir, 'proposing', f'round_{iteration:04d}/two_candidates')
    workspace.mkdir(parents=True, exist_ok=True)
    best = json.loads((run_dir / 'frontier_search.json').read_text())
    parent = run_dir / 'candidates' / best['agent']
    names = [f'candidate_{run_dir.name}_{iteration:04d}_{j+1}' for j in range(config['evolution']['proposals_per_round'])]
    for name in names:
        folder = workspace / name
        if folder.exists():
            folder.rename(workspace / f'{name}_interrupted_{datetime.now():%Y%m%d%H%M%S%f}')
        shutil.copytree(parent, folder, ignore=shutil.ignore_patterns('__pycache__'))
        write_json(folder / 'lineage.json', {'parent': best['agent'], 'round': iteration,
                   'candidate': name, 'parent_snapshot': str(parent)})
    history = read_history(run_dir)
    latest = max(r['iteration'] for r in history)
    images = []
    for row in history:
        if row['iteration'] == latest:
            images.extend(json.loads((run_dir / 'evidence' / row['agent'] / 'sheets.json').read_text()))
    prompt = (ROOT / 'prompt-templates/proposer.txt').read_text() + '\n' + json.dumps({
        'round': iteration, 'parent': best, 'candidate_directories': [str(workspace / n) for n in names],
        'archive': str(run_dir / 'evidence' / 'archive.json'),
        'fixed_sceneact_api': str(ROOT / 'sceneact'), 'budget': config['budget'],
        'attached_comparison_sheets': images,
        'required_response': {'candidates': names}}, ensure_ascii=False, indent=2)
    response = codex_wrapper.run(prompt, config, workspace, images)
    if response.get('candidates') != names: raise ValueError(f'Expected exactly {names}')
    for name in names:
        folder = workspace / name
        if not (folder / 'policy.py').is_file(): raise ValueError('Candidate needs policy.py')
        validation_errors = []
        for path in folder.rglob('*.py'):
            try:
                compile(path.read_text(), str(path), 'exec')
            except SyntaxError as error:
                validation_errors.append({'file': str(path.relative_to(folder)), 'error': str(error)})
        if validation_errors:
            write_json(folder / 'proposal_validation.json', {'errors': validation_errors})
        write_json(folder / 'lineage.json', {'parent': best['agent'], 'round': iteration,
                   'candidate': name, 'parent_snapshot': str(parent)})
    write_json(workspace / 'prepared.json', {'candidates': names, 'parent': best['agent'], 'round': iteration})
    return commit_proposals(workspace, run_dir)



def finalize(run_dir, config):
    path = run_dir / 'finalized.json'
    if path.exists(): final = json.loads(path.read_text())
    else:
        state = json.loads((run_dir / 'evolution_state.json').read_text())
        if state['completed_rounds'] < config['evolution']['rounds']:
            raise RuntimeError('Finish configured search rounds before held-out evaluation')
        best = json.loads((run_dir / 'frontier_search.json').read_text())
        final = {'agents': {'baseline': 'baseline', 'best': best['agent']}, 'tests': {}, 'status': 'in_progress'}
        write_json(path, final)  # Close search before exposing test evidence.
    for label, name in final['agents'].items():
        if label not in final['tests']:
            summary = evaluate(name, 'final_test', run_dir, config, experiment=f'final_{label}')
            final['tests'][label] = {k: v for k, v in summary.items() if k != 'scenes'}
            write_json(path, final)
        refresh_report(run_dir)
    final['status'] = 'complete'
    final['overall_delta'] = final['tests']['best']['overall'] - final['tests']['baseline']['overall']
    write_json(path, final)
    refresh_report(run_dir)
    return final


def search(run_dir, config, rounds=None):
    if (run_dir / 'finalized.json').exists(): raise RuntimeError('Search is finalized')
    target = config['evolution']['rounds'] if rounds is None else rounds
    if target < 0 or target > config['evolution']['rounds']: raise ValueError('Invalid target round')
    baseline = evaluate('baseline', 'search', run_dir, config)
    candidate_evidence(baseline, run_dir, config)
    record(run_dir, 0, baseline)
    update_frontier(run_dir, baseline)
    state_file = run_dir / 'evolution_state.json'
    state = json.loads(state_file.read_text()) if state_file.exists() else {'completed_rounds': 0}
    for iteration in range(state['completed_rounds'] + 1, target + 1):
        names = proposals(run_dir, config, iteration)
        results = []
        # Both proposals derive from the same retained parent and archived round history.
        for name in names:
            summary = evaluate(name, 'search', run_dir, config)
            candidate_evidence(summary, run_dir, config)
            record(run_dir, iteration, summary)
            results.append(summary)
        winner = max(results, key=lambda r: r['overall'])
        prepared = json.loads((run_dir / 'proposals' / f'{iteration:04d}' / 'prepared.json').read_text())
        parent = next(row for row in read_history(run_dir) if row['agent'] == prepared['parent'])
        best = update_frontier(run_dir, winner)
        write_json(run_dir / 'proposals' / f'{iteration:04d}' / 'selection.json', {
            'round': iteration, 'parent': parent['agent'], 'parent_q': parent['overall'],
            'candidates': {result['agent']: result['overall'] for result in results},
            'winner': winner['agent'], 'retained': best['agent'],
            'improved': winner['overall'] > parent['overall']})
        state = {'completed_rounds': iteration, 'best': best['agent']}
        write_json(state_file, state)
        refresh_report(run_dir)
        print(f"round={iteration} best={best['agent']} score={best['overall']:.6f}", flush=True)
    if not state_file.exists(): write_json(state_file, state)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-name', default=datetime.now().strftime('%Y%m%d_%H%M%S'))
    parser.add_argument('--config')
    parser.add_argument('--rounds', '--iterations', type=int, help='Target completed round, not extra rounds')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    run_dir, config = open_run(args.run_name, args.config)
    if args.test: print(json.dumps(finalize(run_dir, config), indent=2))
    else: search(run_dir, config, args.rounds)


if __name__ == '__main__': main()
