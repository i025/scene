"""Recompute V2.4 audit and reports in a new directory, without models/Blender."""
from pathlib import Path
import argparse
import json
import os
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=Path('experiments/scene_rsi_v2_4'))
    parser.add_argument('--output', type=Path, default=Path('derived/v2_4_offline'))
    args = parser.parse_args()
    source, output = args.experiment.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError('Use a new derived directory; preserve original evidence')
    if output.is_relative_to(source):
        raise ValueError('Derived output must be outside the source experiment')
    view = output/'experiment'

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
        (view/name).mkdir()

    def rebase(value):
        if isinstance(value, str):
            return value.replace('__EXPERIMENT_ROOT__', str(view)).replace(str(source), str(view))
        if isinstance(value, list):
            return [rebase(item) for item in value]
        if isinstance(value, dict):
            return {key: rebase(item) for key, item in value.items()}
        return value

    def read(path):
        return rebase(json.loads(Path(path).read_text()))

    # All generators read local snapshots, never paths into the original server.
    # Code/JSON are real copies; .blend, images and other media are read-only links.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(view))
    import audit
    import audit_results
    import analyze
    audit.read = read
    audit_results.read = read
    analyze.read = read
    audit.main(view)
    audit_results.main(view)
    analyze.main()

    measured = []
    for path in sorted(source.rglob('record.json')):
        if path.relative_to(source).parts[0] in ['audit_sources', 'code_snapshots']:
            continue
        saved = json.loads(path.read_text())
        if saved['metrics']['valid']:
            measured.append({'record': str(path.relative_to(source)),
                             'measured_opened_success': True,
                             'local_blend_available': path.with_name('scene.blend').exists()})
    sessions = [p for p in source.rglob('session.json')
                if p.relative_to(source).parts[0] not in ['audit_sources', 'code_snapshots']
                and p.with_name('request.json').exists()]
    referenced = set()

    def blend_names(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ['edited_blend', 'probe_blend'] and isinstance(item, str) and Path(item).name == item:
                    yield item
                else:
                    yield from blend_names(item)
        elif isinstance(value, list):
            for item in value:
                yield from blend_names(item)

    for pattern in ['probe.json', 'mechanical.json']:
        for path in source.rglob(pattern):
            if path.relative_to(source).parts[0] in ['audit_sources', 'code_snapshots']:
                continue
            for name in blend_names(json.loads(path.read_text())):
                referenced.add(path.with_name(name))
    missing_blends = sum(not row['local_blend_available'] for row in measured)
    missing_edit_probe_blends = [str(p.relative_to(source)) for p in sorted(referenced) if not p.exists()]
    missing_events = sum(not p.with_name('events.jsonl').exists() for p in sessions)
    note = ('核心 Git 数据可重画主要统计图；精确复现完整证据可用性需要把 fixed、structured、active、'
            'shared-evidence 四个 Release 包都解压覆盖到仓库根目录。缺少二进制时，派生表中的 '
            'blend_file_exists=False 只表示本地文件不在；原 record 保存的实际打开/执行测量仍然保留。'
            '本入口不重测 Q，不改原始 JSON，不启动模型、Blender 或 GPU。')
    receipt = {'source': str(source), 'derived': str(view), 'new_model_calls': 0,
               'new_Blender_jobs': 0, 'new_render_frames': 0, 'history_untouched': True,
               'paths_rebased': ['__EXPERIMENT_ROOT__', str(source)],
               'generators': ['audit.py', 'audit_results.py', 'analyze.py'],
               'implementation_audit': 'experiment/metrics/implementation_audit.json',
               'media_policy': 'read-only source symlinks, including every available .blend',
               'measured_successful_records': measured,
               'measured_success_blends_missing_locally': missing_blends,
               'referenced_edit_probe_blends_missing_locally': missing_edit_probe_blends,
               'CLI_event_logs_missing_locally': missing_events,
               'binary_artifact_presence_complete': missing_blends == 0 and not missing_edit_probe_blends,
               'CLI_event_presence_complete': missing_events == 0,
               'full_release_overlay_required_for_exact_evidence_recompute': True,
               'release_bundles': ['fixed.tar.gz', 'structured.tar.gz', 'active.tar.gz', 'shared-evidence.tar.gz'],
               'note': note}
    (output/'OFFLINE_RUN.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    (output/'OFFLINE_NOTE.md').write_text('# 离线重画范围\n\n'+note+'\n\n缺少成功记录的 .blend：'+str(missing_blends)+'；缺少编辑/探测工程：'+str(len(missing_edit_probe_blends))+'；缺少 CLI events.jsonl：'+str(missing_events)+'。\n')
    report = view/'reports/index.html'
    content = report.read_text()
    content = content.replace('<h1>', '<p>'+note+'</p><h1>', 1)
    report.write_text(content)
    print(json.dumps({'report': str(report), 'missing_blends': missing_blends,
                      'missing_CLI_events': missing_events, 'original_scores_remeasured': False}, ensure_ascii=False))


if __name__ == '__main__':
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[key] = '2'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['MPLCONFIGDIR'] = '/tmp/scene-rsi-v24-offline-mpl'
    main()
