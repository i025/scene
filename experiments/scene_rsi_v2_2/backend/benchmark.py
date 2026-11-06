import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import yaml
from data import ROOT, load_config, prepare, public_task, write_json
from evaluate import aggregate
from processes import cpu_environment, run_group
from gpu_watch import before_task, refresh_report, scene_boundary, wait_for_gpu


def open_run(run_name, config_path=None):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', run_name):
        raise ValueError('Invalid run name')
    run_dir = ROOT / 'logs' / run_name
    config_file = run_dir / 'config.yaml'
    if config_file.exists():
        return run_dir, load_config(config_file)
    config = load_config(config_path)
    rows = prepare(config)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / 'splits.json', rows)
    config['dataset']['manifest'] = str(run_dir / 'splits.json')
    config.pop('_config_dir', None)
    config_file.write_text(yaml.safe_dump(config, sort_keys=False))
    return run_dir, load_config(config_file)


def copy_snapshot(source, target):
    temporary = target.with_name('.' + target.name + '.copying')
    if temporary.exists():
        shutil.rmtree(temporary)
    shutil.copytree(source, temporary, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.bak', '*.bak.*'))
    temporary.replace(target)


def freeze(name, run_dir):
    target = run_dir / 'candidates' / name
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        copy_snapshot(ROOT / 'harnesses' / name, target)
    return target


def usage_sum(rows, key):
    values = [r['usage'].get(key, 'unknown') for r in rows]
    return sum(values) if all(isinstance(value, (int, float)) for value in values) else 'unknown'


def evaluate(name, split, run_dir, config, experiment=None):
    if config['benchmark']['concurrency'] != 1:
        raise ValueError('Mini reproduction uses exactly one scene/GPU task at a time')
    source = freeze(name, run_dir)
    rows = [r for r in json.loads((run_dir / 'splits.json').read_text()) if r['split'] == split]
    if not rows:
        raise ValueError('Empty split')
    label = experiment or name
    config_path = run_dir / 'config.yaml'
    results = []
    for index, row in enumerate(rows, 1):
        # Sequential opaque names keep reference scene identity out of Student prompts.
        output = ROOT / 'jobs' / run_dir.name / label / f'scene_{index:03d}'
        result_path = output / 'metrics.json'
        if result_path.exists():
            results.append(json.loads(result_path.read_text()))
            continue
        task_label = f'{label}/{split}/scene_{index:03d}'
        before_task(run_dir, 'generation', task_label)
        output.mkdir(parents=True, exist_ok=True)
        if (output / 'task.json').exists() and not (output / 'generation_complete.json').exists():
            archived = output.with_name(output.name + f'_interrupted_{time.time_ns()}')
            output.rename(archived)
            output.mkdir()
        task = public_task(row)
        reference = output / 'reference.png'
        from PIL import Image
        with Image.open(task['image']) as image:
            image.convert('RGB').save(reference)
        task['image'] = str(reference)
        write_json(output / 'task.json', task)
        runtime_config = {k: config[k] for k in ('model', 'budget', 'render', 'blender')}
        write_json(output / 'runtime.json', runtime_config)
        started = time.monotonic()
        if not (output / 'generation_complete.json').exists():
            error = None
            with (output / 'worker_stdout.log').open('w') as stdout, (output / 'worker_stderr.log').open('w') as stderr:
                try:
                    code = run_group([sys.executable, str(ROOT / 'inner_loop.py'), '--config', str(output / 'runtime.json'),
                        '--task', str(output / 'task.json'), '--source-dir', str(source), '--output-dir', str(output)],
                        timeout=config['budget']['seconds'], cwd=output, stdout=stdout, stderr=stderr,
                        env=cpu_environment())
                    if code:
                        error = f'Worker exited {code}'
                except subprocess.TimeoutExpired:
                    error = 'Scene wall-clock timeout'
            status_path = output / 'status.json'
            if not error and status_path.exists():
                error = json.loads(status_path.read_text()).get('error')
            write_json(output / 'generation_complete.json', {'seconds': time.monotonic() - started, 'error': error})
        generation = json.loads((output / 'generation_complete.json').read_text())
        # A complete prior render remains eligible after a later generation error.
        if config['metrics']['device'].startswith('cuda'):
            uuid = wait_for_gpu(run_dir, config, task_label + '/score')
            scoring_env = cpu_environment(cuda_visible=uuid)
        else:
            scoring_env = cpu_environment()
        before_task(run_dir, 'scoring', task_label + '/score')
        scoring_started = time.monotonic()
        with (output / 'scoring_stdout.log').open('w') as stdout, (output / 'scoring_stderr.log').open('w') as stderr:
            from metric_worker import current_worker
            worker = current_worker()
            if worker is not None:
                stderr.write(f'Resident metric worker PID {worker.pid}; shared logs: {run_dir / "resident_metrics"}\n')
                measured = worker.request('score', reference, output_dir=output, timeout=config['metrics']['timeout'])
                stdout.write(json.dumps(measured) + '\n')
                code = 0
            else:
                code = run_group([sys.executable, str(ROOT / 'evaluate.py'), '--config', str(config_path),
                    '--image', str(reference), '--output-dir', str(output)], timeout=config['metrics']['timeout'],
                    cwd=ROOT, stdout=stdout, stderr=stderr, env=scoring_env)
        if code:
            raise RuntimeError(f'Scorer failed: {output / "scoring_stderr.log"}')
        metrics = json.loads((output / 'image_metrics.json').read_text())
        usage_path = output / 'usage.json'
        usage = json.loads(usage_path.read_text()) if usage_path.exists() else {
            'calls': 'unknown', 'input_tokens': 'unknown', 'output_tokens': 'unknown',
            'total_tokens': 'unknown', 'seconds': 'unknown', 'executions': 'unknown'}
        result = {**metrics, 'id': row['id'], 'dataset': row['dataset'], 'split': split,
            'candidate': name, 'usage': usage, 'seconds': generation['seconds'],
            'scoring_seconds': time.monotonic() - scoring_started,
            'generation_error': generation['error'], 'output_dir': str(output),
            'reference': str(reference), 'render': str(output / 'final.png') if (output / 'final.png').exists() else None,
            'trajectory': str(output / 'trajectory.jsonl')}
        write_json(result_path, result)
        results.append(result)
        scene_boundary(run_dir, config)
    summary = {'agent': name, 'split': split, 'count': len(results), **aggregate(results),
        'datasets': {dataset: aggregate([r for r in results if r['dataset'] == dataset])
                     for dataset in sorted({r['dataset'] for r in results})},
        'usage': {key: usage_sum(results, key) for key in
                  ('calls', 'input_tokens', 'output_tokens', 'total_tokens', 'cached_input_tokens', 'seconds', 'executions')},
        'scene_seconds': sum(r['seconds'] for r in results),
        'scoring_seconds': sum(r.get('scoring_seconds', 0) for r in results), 'scenes': results}
    write_json(run_dir / 'results' / label / f'{split}.json', summary)
    refresh_report(run_dir)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-name', required=True)
    parser.add_argument('--config')
    parser.add_argument('--agent', default='baseline')
    args = parser.parse_args()
    run_dir, config = open_run(args.run_name, args.config)
    if (run_dir / 'finalized.json').exists():
        raise RuntimeError('Search closed')
    print(json.dumps(evaluate(args.agent, 'search', run_dir, config), indent=2))
