"""Two reserved BlenderWorld room tasks; direct local blend, adapted evaluation only."""
from pathlib import Path
import ast
import json
import shutil
import subprocess
import time
from pilot import ROOT,read,write_json,config,current,run_scene,inspect,call
from model_evidence import compact_structure
BW=Path('__BLENDERWORLD_ROOT__')

def judge(row,task_root,index,dimensions):
    dest=ROOT/'external_judgments'/f'anon_{index:02d}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'result.json').exists():return read(dest/'result.json')
    if row['status']!='complete':
        result={'status':'not_run','reason':'reconstruction_failed','adapted_fused_score_0_100':None};write_json(dest/'result.json',result);return result
    folder=Path(row['folder']);inspect(folder,'views')
    rubric=read(task_root/'rubric.json');items=rubric['rubrics']
    images=[]
    for i,p in enumerate([folder/'reference.png',folder/'final.png',folder/'views/view_side60.png',folder/'views/view_top.png']):
        if p.exists():
            target=dest/f'image_{i:02d}.png';shutil.copy2(p,target);images.append(target)
    structure=compact_structure(read(folder/'functional/scene_structure.json',{}))
    schema={'type':'object','additionalProperties':False,'properties':{'rubric_scores':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{'id':{'type':'string','enum':[str(r['id']) for r in items]},'score':{'type':'integer','enum':[0,1]},'evidence':{'type':'string'}},'required':['id','score','evidence']}},'dimension_scores':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{'id':{'type':'string','enum':[d['id'] for d in dimensions]},'score':{'type':'integer','minimum':1,'maximum':10},'reason':{'type':'string'}},'required':['id','score','reason']}}},'required':['rubric_scores','dimension_scores']}
    prompt='Independent anonymized BlenderWorld ADAPTED evaluation. Image 0 is the reference. Remaining images are submitted camera, fixed side and top views. Use original rubric pass_condition and importance weights without redefining them. Binary score 1 only for clear unambiguous evidence; absent, contradicted or uncertain earns 0, following the local official rubric rules. Holistic dimensions are integers 1..10 with the original meanings below. No prompt statement is evidence of an object existing. AABB overlap is not true mesh collision. This uses Codex CLI and three fixed views at the common pilot rendering settings, omits official blind-description stages, and is NOT an official leaderboard evaluation. Do not use tools.\n'+json.dumps({'public_query':(task_root/'query.txt').read_text(),'original_rubric':rubric,'original_dimensions':dimensions,'actual_scene_summary':structure},ensure_ascii=False)
    try:
        response,session=call(prompt,config()['proposer'],dest/'judge_call',images,role='external_anonymous_judge',schema=schema)
        values=json.loads(response);scores=values['rubric_scores'];dims=values['dimension_scores']
        if len(scores)!=len(items) or {s['id'] for s in scores}!={str(r['id']) for r in items}:raise ValueError('Missing/duplicate original rubric IDs')
        if len(dims)!=len(dimensions) or {d['id'] for d in dims}!={d['id'] for d in dimensions}:raise ValueError('Missing/duplicate quality dimensions')
        by_id={s['id']:s['score'] for s in scores};weights=[float(r.get('importance_weight') or 1) for r in items]
        rubric_score=100*sum(w*by_id[str(r['id'])] for r,w in zip(items,weights))/sum(weights)
        dimension_score=10*sum(d['score'] for d in dims)/len(dims)
        result={'status':'complete','evaluation':'adapted_evaluation_not_official','rubric_score_0_100':rubric_score,'dimension_score_0_100':dimension_score,'adapted_fused_score_0_100':.5*(rubric_score+dimension_score),**values}
    except (ValueError,RuntimeError,OSError,subprocess.TimeoutExpired) as error:result={'status':'failed','error':str(error),'adapted_fused_score_0_100':None}
    write_json(dest/'result.json',result);write_json(dest/'mapping.json',{k:row[k] for k in ['method','run_id','scene_id','H_version']});return result


def main():
    if read(ROOT/'external_status.json',{}).get('status')=='complete':return
    if not (ROOT/'selection_freeze.json').exists():raise RuntimeError('Main selection must be frozen')
    available=600-current()['cli_sessions']
    prior_protocol=read(ROOT/'external_protocol.json')
    if available<24 and not prior_protocol:
        write_json(ROOT/'external_status.json',{'status':'pending_budget','required_upper_cli':24,'remaining_cli':available,'tasks':['bw_0005','bw_0011'],'official_score':None});return
    chosen=next(c for c in read(ROOT/'selections.json') if c['method']=='scene_rsi_pilot' and c['run_id']=='r1')
    sources={'fixed_h0':ROOT/'backend/harnesses/baseline','scene_rsi_pilot':Path(chosen['source'])}
    module=ast.parse((BW/'blenderworld/evaluators/judge_blender_binary_rubrics.py').read_text())
    dimensions=next(ast.literal_eval(node.value) for node in module.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DIMENSIONS' for t in node.targets))
    if not prior_protocol:write_json(ROOT/'external_protocol.json',{'common_config_snapshot':config(),'tasks':['bw_0005','bw_0011'],'methods':{k:str(v) for k,v in sources.items()},'selection':'predeclared main r1 Selection winner, never main Test winner','generation_input':'reference plus original public query appended by a common task-input adapter to system.txt; hidden rubric only in judge','render':'pilot 512-long-edge Cycles16, common cpu_if_busy authorized-single-GPU policy, three fixed views; replaces official higher resolution/eight-view adaptive protocol','judge':'fresh anonymous gpt-6-astra/medium; original rubric meanings/importance weights and 8 dimensions; no official blind-description passes','formula':'0.5*(weighted binary rubric percent + 10*mean(dimension scores 1..10))','evaluation':'adapted; not official leaderboard','identical_H0_policy':'If selected Ours source is H0, reuse the same current-task reconstruction/views/functionals and record zero extra generation cost; judge remains a fresh supplemental call, not an algorithm comparison','hash_validation':'not executed; direct local blend loading','historical_exposure':'gallery/index screening possible, not new blind data','time':time.time()})
    records=[]
    for task_id in ['bw_0005','bw_0011']:
        task_root=BW/'data/hf-snapshot'/task_id/'tests/dataset/tasks'/task_id
        scene={'scene_id':task_id,'split':'external','image_path':str(task_root/'references/image_01.jpg'),'expected_composite':True}
        for method,source in sources.items():
            staging=ROOT/'external_inputs'/task_id/method;staging.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source/'policy.py',staging/'policy.py')
            (staging/'system.txt').write_text((source/'system.txt').read_text()+'\nPUBLIC TASK INPUT:\n'+(task_root/'query.txt').read_text()+'\nBENCHMARK ADAPTATION: Preserve the scene intent; the fixed external runner owns saving/rendering and uses its frozen resolution/samples. Do not render/save in the generated program. Do not access hidden rubrics.')
            write_json(staging/'input_adapter.json',{'source_H':str(source),'public_query':str(task_root/'query.txt'),'hidden_rubric_exposed_to_generator':False})
            if method!='fixed_h0' and source==sources['fixed_h0']:
                original=ROOT/'results/external/fixed_h0/selected/external'/task_id
                reused=ROOT/'results/external'/method/'selected/external'/task_id
                reused.mkdir(parents=True,exist_ok=True)
                if not (reused/'record.json').exists():
                    original_row=read(original/'record.json')
                    row={**original_row,'method':method,'folder':str(reused),'reuse_of':str(original),'seconds':0,'usage':{'calls':0,'executions':0,'input_tokens':0,'output_tokens':0,'total_tokens':0,'reuse_original_usage':original_row['usage']},'reuse_basis':'Selected source is the identical H0; same task/public query/config. Independent judge call remains supplemental variability, not an algorithm difference.'}
                    for name in ['reference.png','final.png','scene.blend','build.py','camera.json']:
                        if (original/name).exists() and not (reused/name).exists():(reused/name).symlink_to(original/name)
                    for subdir in ['functional','views']:
                        if (original/subdir).exists() and not (reused/subdir).exists():(reused/subdir).symlink_to(original/subdir,target_is_directory=True)
                    write_json(reused/'record.json',row)
                row=read(reused/'record.json')
            else:
                row=run_scene(method,'external','selected',scene,staging)
            evaluation=judge(row,task_root,len(records)+1,dimensions)
            records.append({'method':method,'task_id':task_id,'reconstruction':row,'adapted_evaluation':evaluation})
    write_json(ROOT/'external_status.json',{'status':'complete','evaluation':'adapted_evaluation_not_official','records':records,'remaining_cli':600-current()['cli_sessions']})

if __name__=='__main__':main()
