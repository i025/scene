"""Rebuild V3 tables/plots in a new derived directory; no models or Blender."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

TEXT = {'.py', '.sh', '.json', '.jsonl', '.txt', '.log', '.md', '.diff', '.yaml', '.yml', '.csv', '.html', '.css', '.toml', '.svg'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=Path('experiments/scene_rsi_v3'))
    parser.add_argument('--output', type=Path, default=Path('derived/v3_offline'))
    args = parser.parse_args()
    source, output = args.experiment.resolve(), args.output.resolve()
    if not (source / 'analyze.py').exists():
        raise FileNotFoundError(source / 'analyze.py')
    if output.exists():
        raise FileExistsError('Use a new derived path; do not overwrite earlier evidence')
    if output.is_relative_to(source):
        raise ValueError('Derived directory must be outside the archived/live experiment')
    view = output / 'experiment'

    def copy(src, dst):
        path = Path(src)
        if path.suffix in TEXT and path.stat().st_size <= 8_000_000:
            return shutil.copy2(src, dst)
        os.symlink(path.resolve(), dst)
        return dst

    def ignore(directory, names):
        return ['metrics','figures','reports','__pycache__'] if Path(directory) == source else ['__pycache__']

    shutil.copytree(source, view, copy_function=copy, ignore=ignore, symlinks=False)
    for name in ('metrics','figures','reports'):
        (view / name).mkdir()
    # Keep input evidence separately; analyze regenerates its derived render table.
    copied_evidence = []
    for relative in ('metrics/render_evidence.csv', 'ledger.json', 'render_attempts.jsonl',
                     'preparation/cpu_benchmark_budget_correction.json'):
        original = source / relative
        if original.is_file():
            target = output / 'source_records' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, target)
            copied_evidence.append(relative)

    def rebase(value):
        if isinstance(value,str):
            return value.replace('__EXPERIMENT_ROOT__',str(view)).replace(str(source),str(view))
        if isinstance(value,list):
            return [rebase(item) for item in value]
        if isinstance(value,dict):
            return {key:rebase(item) for key,item in value.items()}
        return value

    reference_map_path = source / 'data/public_reference_map.json'
    reference_map = json.loads(reference_map_path.read_text()) if reference_map_path.exists() else {}

    def read(path):
        data = rebase(json.loads(Path(path).read_text()))
        if Path(path).name == 'manifest.json' and isinstance(data,list):
            # Only the derived reader's view changes, not the saved manifest/measurements.
            for scene in data:
                if scene['scene_id'] in reference_map:
                    reference = reference_map[scene['scene_id']]
                    scene['image_path'] = str(view / reference['path'])
                    scene['public_reference_status'] = reference['status']
        return data

    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('scene_rsi_v3_offline_analyze',view/'analyze.py')
    analyze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyze)
    analyze.ROOT = view
    analyze.read = read
    analyze.main()
    note = ('本次只重算已保存记录、重画真实已有图像，不重测视觉指标，不调用模型、Blender或GPU。'
            '文本为独立副本，较大原始日志与媒体只通过只读用途链接引用。'
            '未获分发许可的BlenderWorld参考媒体保持占位；占位不算实验图像或测量。'
            '只有Git核心文件时可重画核心表格和已有媒体；完整CLI证据及.blend需要解压对应Release包。'
            'pending/null及原始失败不会被补造。')
    receipt = {'source':str(source),'derived':str(view),'new_model_calls':0,'new_Blender_jobs':0,
               'new_render_frames':0,'original_files_untouched':True,'path_rebase':'__EXPERIMENT_ROOT__ and source run path',
               'media_policy':'Read-only-use links, never modifies linked source media',
               'source_state':read(source/'state.json'),'public_reference_map_used':bool(reference_map),
               'source_CLI_sessions':len(list(source.rglob('session.json'))),
               'source_blend_files_available':len(list(source.rglob('*.blend'))),
               'source_records_copied':copied_evidence,
               'report':str(view/'reports/index.html'),'note':note}
    (output/'OFFLINE_RUN.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    (output/'OFFLINE_NOTE.md').write_text('# V3离线重画范围\n\n'+note+'\n')
    report = view/'reports/index.html'
    content = report.read_text();content = content.replace('<h1>','<p>'+note+'</p><h1>',1)
    report.write_text(content)
    print(json.dumps({'report':str(report),'new_model_calls':0,'new_Blender_jobs':0,
                      'source_phase':receipt['source_state']['phase']},ensure_ascii=False))


if __name__ == '__main__':
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key]='1'
    os.environ['CUDA_VISIBLE_DEVICES']=''
    os.environ['MPLCONFIGDIR']='/tmp/scene_rsi_v3_offline_mpl'
    main()
