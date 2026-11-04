"""Recompute V2 tables/figures in a new directory; no models, Blender or GPU."""
import argparse,json,os,shutil,sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--experiment',type=Path,default=Path('experiments/scene_rsi_v2'));parser.add_argument('--output',type=Path,default=Path('derived/v2_offline'));args=parser.parse_args()
    source=args.experiment.resolve();output=args.output.resolve()
    if output.exists():raise FileExistsError('Choose a new derived output directory; preserve historical results')
    view=output/'experiment'
    def copy(src,dst):
        path=Path(src)
        if path.suffix in ('.json','.py','.md','.diff','.txt','.yaml','.yml') and path.stat().st_size<524288:return shutil.copy2(src,dst)
        os.symlink(path.resolve(),dst);return dst
    shutil.copytree(source,view,copy_function=copy,ignore=lambda directory,names: ['metrics','figures','reports','__pycache__'] if Path(directory)==source else ['__pycache__'])
    sys.path.insert(0,str(source));import analyze
    old_read=analyze.read
    def rebase(value):
        if isinstance(value,str):return value.replace('__EXPERIMENT_ROOT__',str(view))
        if isinstance(value,list):return [rebase(v) for v in value]
        if isinstance(value,dict):
            item={k:rebase(v) for k,v in value.items()}
            if 'image_path' in item and 'scene_id' in item and not Path(item['image_path']).exists():
                references=list((view/'results').glob('*/*/*/*/'+item['scene_id']+'/reference.png'))
                if references:item['image_path']=str(references[0])
            return item
        return value
    analyze.read=lambda path,default=None:rebase(old_read(path,default))
    analyze.ROOT=view;analyze.main()
    (output/'OFFLINE_RUN.json').write_text(json.dumps({'source':str(source),'report':str(view/'reports/index.html'),'new_model_calls':0,'new_render_frames':0,'history_untouched':True},indent=2))
    print(view/'reports/index.html')


if __name__=='__main__':
    for name in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[name]='2'
    os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['MPLCONFIGDIR']=str(Path('derived/matplotlib').resolve())
    main()
