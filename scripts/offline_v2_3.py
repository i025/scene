"""Recompute V2.3 reports in a new derived directory; no CLI or Blender.

Adapted from scripts/offline_v2_2.py. Works with Git core evidence alone or
the same experiment directory after extracting the four Release bundles.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=Path('experiments/scene_rsi_v2_3'))
    parser.add_argument('--output', type=Path, default=Path('derived/v2_3_offline'))
    args = parser.parse_args()
    source, output = args.experiment.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError('Use a new output directory; preserve original evidence')
    if output.is_relative_to(source):
        raise ValueError('Place derived output outside the source experiment')
    view = output / 'experiment'

    def copy(src, dst):
        path = Path(src)
        if path.suffix in ('.json', '.py', '.md', '.diff', '.txt', '.yaml', '.yml', '.csv'):
            return shutil.copy2(src, dst)
        os.symlink(path.resolve(), dst)
        return dst

    shutil.copytree(source, view, copy_function=copy, ignore=lambda directory, names:
                    ['metrics', 'figures', 'reports', '__pycache__']
                    if Path(directory) == source else ['__pycache__'])
    for name in ['metrics', 'figures', 'reports']:
        (view / name).mkdir()

    def rebase(value):
        if isinstance(value, str):
            return value.replace('__EXPERIMENT_ROOT__', str(view)).replace(str(source), str(view))
        if isinstance(value, list):
            return [rebase(item) for item in value]
        if isinstance(value, dict):
            return {key: rebase(item) for key, item in value.items()}
        return value

    # Import the copied code: common.ROOT and backend/budget.ROOT then point
    # at the derived view. No modules are imported from the immutable source.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(view))
    import analyze
    import common
    old_read = common.read

    def read(path):
        return rebase(old_read(path))

    common.read = read
    analyze.read = read
    analyze.main()
    import runpy
    runpy.run_path(str(view / 'audit_results.py'), run_name='__main__')
    (output / 'OFFLINE_RUN.json').write_text(json.dumps({
        'source': str(source), 'derived': str(view),
        'new_model_calls': 0, 'new_render_frames': 0,
        'history_untouched': True,
        'media_policy': 'read-only source media symlinks; tables/figures/reports written only in derived output',
        'paths_rebased': ['__EXPERIMENT_ROOT__', str(source)],
    }, ensure_ascii=False, indent=2) + '\n')
    print(view / 'reports/index.html')


if __name__ == '__main__':
    for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[key] = '2'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['MPLCONFIGDIR'] = '/tmp/scene-rsi-v23-offline-mpl'
    main()
