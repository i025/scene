"""Recompute V2.2 summaries and PNGs in a new directory; no CLI or Blender."""
from pathlib import Path
import argparse
import json
import os
import shutil
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiment',type=Path,default=Path('experiments/scene_rsi_v2_2'))
    parser.add_argument('--output',type=Path,default=Path('derived/v2_2_offline'))
    args=parser.parse_args();source=args.experiment.resolve();output=args.output.resolve()
    if output.exists():raise FileExistsError('Use a new output directory; preserve original measurements')
    view=output/'experiment'
    def copy(src,dst):
        path=Path(src)
        if path.suffix in ('.json','.py','.md','.diff','.txt','.yaml','.yml') and path.stat().st_size<524288:
            return shutil.copy2(src,dst)
        os.symlink(path.resolve(),dst);return dst
    shutil.copytree(source,view,copy_function=copy,ignore=lambda directory,names:
        ['metrics','figures','reports','__pycache__'] if Path(directory)==source else ['__pycache__'])
    for name in ['metrics','figures','reports']:(view/name).mkdir()
    sys.path.insert(0,str(source));import analyze
    old_read=analyze.read
    def rebase(value):
        if isinstance(value,str):return value.replace('__EXPERIMENT_ROOT__',str(view)).replace(str(source),str(view))
        if isinstance(value,list):return [rebase(v) for v in value]
        if isinstance(value,dict):
            result={k:rebase(v) for k,v in value.items()}
            if 'image_path' in result and 'scene_id' in result and not Path(result['image_path']).exists():
                local=view/'data'/(result['scene_id']+'.jpg')
                if local.exists():result['image_path']=str(local)
            return result
        return value
    analyze.read=lambda path:rebase(old_read(path))
    analyze.ROOT=view;analyze.main()
    (output/'OFFLINE_RUN.json').write_text(json.dumps({'source':str(source),'derived':str(view),
        'new_model_calls':0,'new_render_frames':0,'history_untouched':True},indent=2))
    print(view/'reports/index.html')


if __name__=='__main__':
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
    os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['MPLCONFIGDIR']=str(Path('/tmp/scene-rsi-v22-mpl').resolve())
    main()
