"""Recompute reports from saved evidence in a separate view; no model/Blender calls."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=Path('experiments/scene_rsi_pilot'))
    parser.add_argument('--output', type=Path, default=Path('derived/offline'))
    args = parser.parse_args()
    source = args.experiment.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError('Choose a new output directory; historical reports are never overwritten.')
    if not list((source / 'results').glob('*/*/*/*/*/final.png')):
        raise FileNotFoundError('Extract the release bundles at repository root before recomputing reports.')
    view = output / 'experiment'

    def copy_file(src, dst):
        path = Path(src)
        if path.suffix in ('.json', '.py', '.md', '.diff', '.txt', '.sh', '.yaml', '.yml') and path.stat().st_size < 524288:
            return shutil.copy2(src, dst)
        os.symlink(path.resolve(), dst)
        return dst

    shutil.copytree(source, view, copy_function=copy_file,
                    ignore=lambda directory, names: ['reports'] if Path(directory) == source else ['__pycache__'])
    # The experiment's report code is preserved. Only its file reader is rebased.
    sys.path.insert(0, str(source))
    import report
    original_read = report.read

    def rebase(value):
        if isinstance(value, str):
            return value.replace('__EXPERIMENT_ROOT__', str(view))
        if isinstance(value, list):
            return [rebase(item) for item in value]
        if isinstance(value, dict):
            return {key: rebase(item) for key, item in value.items()}
        return value

    def read(path, default=None):
        return rebase(original_read(path, default))

    report.read = read
    import analyze
    analyze.ROOT = view
    ledger = read(view / 'ledger.json')
    # No recount of missing/retired render files: use the actual frozen ledger.
    analyze.current = lambda: dict(ledger)
    analyze.main()
    summary = report.generate(view)
    (output / 'OFFLINE_RUN.json').write_text(json.dumps({
        'source': str(source), 'reports': str(view / 'reports'),
        'new_model_calls': 0, 'new_render_frames': 0,
        'accounting': 'Frozen as-run ledger; no new experimental work.',
        'records': summary['record_count'], 'cli_sessions': ledger['cli_sessions'],
    }, indent=2) + '\n')
    print(view / 'reports/index.html')


if __name__ == '__main__':
    for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[name] = '2'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['MPLCONFIGDIR'] = str(Path('derived/matplotlib').resolve())
    main()
