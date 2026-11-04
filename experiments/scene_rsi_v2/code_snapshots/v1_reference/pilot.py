"""Fixed experiment runner. Candidate code controls H/M only; scoring stays external."""
from pathlib import Path
import ast
import difflib
import importlib.util
import json
import shutil
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json
from processes import cpu_environment,run_group
from budget import current,guard
from codex_wrapper import call,check_service_pause
from strategies import initialize,COMMON
from model_evidence import compact_structure,compact_trajectory,bound_payload
from devices import inspection_config

METHODS=['sceneevolve_cli','generic_rsi','scene_rsi_pilot']

def read(path,default=None):
    return json.loads(path.read_text()) if path.exists() else default

def config():return read(ROOT/'config.json')

def load_module(path):
    spec=importlib.util.spec_from_file_location('candidate_'+str(time.time_ns()),path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def validate_source(text,kind):
    tree=ast.parse(text)
    allowed=set(config()['candidate_validation']['allowed_imports'])
    forbidden={'exec','eval','compile','open','__import__','getattr','setattr','delattr','globals','locals'}
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]]
            if any(name not in allowed for name in names):raise ValueError('Disallowed candidate import')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in forbidden:raise ValueError('Disallowed candidate execution primitive')
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='runtime' and node.attr not in {'ask','execute','select','remaining','image'}:raise ValueError('Only frozen Runtime interfaces are allowed')
        if isinstance(node,ast.Attribute) and node.attr.startswith('__'):
            # Ordinary type-name logging does not expose object internals.
            type_name=(node.attr=='__name__' and isinstance(node.value,ast.Call)
                       and isinstance(node.value.func,ast.Name) and node.value.func.id=='type'
                       and len(node.value.args)==1 and not node.value.keywords)
            if not type_name:raise ValueError('Candidate introspection outside contract')
        if isinstance(node,ast.Attribute) and node.attr in {'rglob','glob','iterdir','write_text','write_bytes','unlink','mkdir','system','popen','run','connect'}:raise ValueError('Candidate may not explore or mutate filesystem/processes')
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            if '/srv/' in node.value or '/home/' in node.value or 'commons_' in node.value:raise ValueError('Hardcoded data identifier/path in candidate')
    required='solve' if kind=='policy.py' else 'plan'
    if not any(isinstance(n,ast.FunctionDef) and n.name==required for n in tree.body):raise ValueError('Missing '+required)
    permitted_system_paths={ast.dump(ast.parse(expr,mode='eval').body) for expr in ("Path(__file__).parent / 'system.txt'","Path(__file__).with_name('system.txt')")}
    for node in ast.walk(tree):
        if isinstance(node,ast.Name) and node.id.startswith('__') and node.id!='__file__':raise ValueError('Candidate built-in introspection outside contract')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
            if node.func.attr in ('open','read_bytes'):raise ValueError('Candidate file access outside contract')
            if node.func.attr=='read_text' and (kind!='policy.py' or ast.dump(node.func.value) not in permitted_system_paths):raise ValueError('Only literal candidate system.txt read is permitted')

def inspect(folder,mode='mechanical',probe=None,output=None):
    cfg=config();dest=output or folder/('functional' if mode=='mechanical' else mode)
    dest.mkdir(parents=True,exist_ok=True)
    result_file=dest/({'mechanical':'mechanical','inspect':'scene_structure','views':'views','probe':'probe'}[mode]+'.json')
    if result_file.exists():return read(result_file)
    guard('render',{'inspect':0,'mechanical':3,'views':2,'probe':1}[mode])
    settings_path, environment = inspection_config(cfg, dest)
    args=[cfg['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python',str(ROOT/'inspect_blend.py'),'--','--blend',str(folder/'scene.blend'),'--output-dir',str(dest),'--mode',mode,'--settings',str(settings_path)]
    if probe:args+=['--probe',probe]
    start=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        try:
            result=subprocess.run(args,stdout=out,stderr=err,env=environment,timeout=cfg['blender']['timeout'])
            status={'exit_code':result.returncode,'seconds':time.monotonic()-start}
        except subprocess.TimeoutExpired:
            status={'exit_code':None,'seconds':time.monotonic()-start,'error':'blender_timeout'}
    write_json(dest/'process.json',status)
    return read(result_file,{'status':'failed','process':status})

def functional(folder,scene):
    result=inspect(folder)
    structure=read(folder/'functional/scene_structure.json',{})
    material=result.get('material',{})
    move=result.get('move',{})
    composite_required=scene['expected_composite']
    composite_ok=bool(move.get('pass')) if composite_required else move.get('pass')
    passed=bool(structure.get('structure_pass')) and bool(material.get('pass')) and (composite_ok is not False)
    record={'structure_pass':bool(structure.get('structure_pass')),'material_pass':bool(material.get('pass')),'composite_required':composite_required,'composite_pass':composite_ok,'functional_pass':passed,'target_object':structure.get('target',{}).get('object','unknown'),'semantic_object_completeness':None,'support_collision_truth':None,'interpretation':'Structural/edit operability only; expected composite absent counts failure, never N/A.'}
    write_json(folder/'functional/summary.json',record)
    return record

def task(scene,folder):
    from PIL import Image,ImageOps
    folder.mkdir(parents=True,exist_ok=True)
    with Image.open(scene['image_path']) as original:
        im=ImageOps.exif_transpose(original).convert('RGB');im.thumbnail((512,512));im.save(folder/'reference.png')
    return {'id':scene['scene_id'],'image':str(folder/'reference.png'),'width':im.width,'height':im.height}

def run_scene(method,run_id,candidate,scene,source,parent=None,meta=None):
    check_service_pause()
    from inner_loop import run
    from evaluate import score
    folder=ROOT/'results'/run_id/method/candidate/scene['split']/scene['scene_id']
    if (folder/'record.json').exists():return read(folder/'record.json')
    finished_generation=(folder/'status.json').exists() and (folder/'task.json').exists()
    if not finished_generation and (folder/'student_calls').exists():
        # Interrupted work is preserved, never silently overwritten or resumed into a model session.
        previous=folder.with_name(folder.name+'_interrupted_'+str(time.time_ns()));folder.rename(previous)
    cfg=config();t=task(scene,folder);write_json(folder/'task.json',t)
    write_json(ROOT/'state.json',{'phase':'running_scene','method':method,'run_id':run_id,'candidate_id':candidate,'scene_id':scene['scene_id'],'split':scene['split'],'folder':str(folder)})
    start=time.monotonic()
    command=[sys.executable,str(ROOT/'backend/inner_loop.py'),'--config',str(ROOT/'config.json'),'--task',str(folder/'task.json'),'--source-dir',str(source),'--output-dir',str(folder)]
    if not finished_generation:
        with (folder/'runner_stdout.log').open('w') as out,(folder/'runner_stderr.log').open('w') as err:
            try:
                rc=run_group(command,timeout=cfg['budget']['seconds']+10,stdout=out,stderr=err,env=cpu_environment())
            except subprocess.TimeoutExpired:
                write_json(folder/'status.json',{'error':'outer_scene_deadline','seconds':time.monotonic()-start})
            if not (folder/'status.json').exists():write_json(folder/'status.json',{'error':'inner_process_missing_status','seconds':time.monotonic()-start})
    else:
        write_json(folder/'evaluation_resume.json',{'time':time.time(),'generation_reused':True,'reason':'Finished inner generation exists; continue external measurements without model resampling','prior_generation_seconds':read(folder/'status.json').get('seconds')})
    metrics=score(t['image'],folder,cfg)
    checks=functional(folder,scene) if metrics['valid'] else {'functional_pass':False,'structure_pass':False,'material_pass':False,'composite_pass':False,'target_object':'unknown'}
    status=read(folder/'status.json');usage=read(folder/'usage.json',{'calls':None,'executions':None})
    failed_calls=[read(p) for p in folder.glob('student_calls/*/session.json') if read(p).get('status')=='failed']
    failure_type=None
    if not metrics['valid']:
        reason=str(status).lower()
        if 'budget' in reason or 'outer_scene_deadline' in reason or status.get('seconds',0)>=cfg['budget']['seconds']-1:
            failure_type='budget_or_scene_timeout'
        elif failed_calls:
            failure_type='model_call_timeout' if any('TimeoutExpired' in str(c.get('error')) for c in failed_calls) else 'cli_service_or_process_failure_unresolved'
        else:
            failure_type='generated_program_or_execution_failure'
    row={'method':method,'run_id':run_id,'scene_id':scene['scene_id'],'split':scene['split'],'candidate_id':candidate,'parent_id':parent,'H_version':str(source.relative_to(ROOT)),'M_version':meta,'model_roles':{'student':'gpt-6.1-sol/medium','meta':'gpt-6-astra/medium','editor':'gpt-6.1-sol/medium','judge':'gpt-6-astra/medium'},'status':'complete' if metrics['valid'] else 'failed','metrics':metrics,'functional':checks,'target_object':checks['target_object'],'device':'CPU','seconds':time.monotonic()-start,'usage':usage,'runtime_status':status,'failure_type':failure_type,'resource_wait_seconds':0,'service_queue_seconds':None,'folder':str(folder),'selected':None}
    row['device_mapping']=read(folder/'actual_device.json',{'device':'CPU','note':'Original CPU-only renderer before user-authorized GPU adaptation'})
    row['device']=row['device_mapping']['device']
    row['render_device_history']=[read(p) for p in sorted(folder.glob('steps/*/actual_device.json'))]
    row['functional_device_mapping']=read(folder/'functional/actual_device.json')
    if finished_generation:
        row['seconds']+=status.get('seconds',0)
        row['resumed_external_evaluation']=True
    write_json(folder/'record.json',row)
    if (folder/'build.py').exists() and not (folder/'scene.py').exists():(folder/'scene.py').symlink_to('build.py')
    write_json(ROOT/'ledger.json',current())
    check_service_pause()
    print(json.dumps({k:row[k] for k in ['method','run_id','scene_id','candidate_id','split','status','metrics']},ensure_ascii=False),flush=True)
    return row

def summarize(rows):
    valid=[r for r in rows if r['metrics']['valid']]
    return {'all_scheduled':len(rows),'completed':len(valid),'success_rate':len(valid)/len(rows),'functional_passes':sum(r['functional']['functional_pass'] for r in rows),'conditional_quality':sum(r['metrics']['overall'] for r in valid)/len(valid) if valid else None,'endpoint_quality':sum(r['metrics']['overall'] for r in valid)/len(rows),'measured_metrics_missing':len(rows)-len(valid)}

def better(child,base,best):
    # Fixed non-degradation gates; endpoint Q uses explicit failed-outcome utility, not fabricated measurements.
    return child['completed']>=base['completed'] and child['functional_passes']>=base['functional_passes'] and child['endpoint_quality']>best['endpoint_quality']+config()['pilot']['quality_tolerance']

def dev_packet(rows):
    packet=[];images=[]
    for row in rows:
        folder=Path(row['folder']);entry={k:row[k] for k in ['scene_id','status','metrics','functional','target_object']}
        entry['program']=(folder/'build.py').read_text() if (folder/'build.py').exists() else 'missing'
        entry['trajectory']=compact_trajectory((folder/'trajectory.jsonl').read_text())
        entry['structure']=compact_structure(read(folder/'functional/scene_structure.json'))
        entry['regression']=read(folder/'functional/mechanical.json')
        for f in [folder/'reference.png',folder/'final.png']:
            if f.exists():images.append(str(f))
        entry['attached_images']=images[-(2 if (folder/'final.png').exists() else 1):]
        packet.append(entry)
    return packet,images

def propose(method,run_id,k,parent_source,meta_source,parent_dev,archive,total_candidates=2):
    check_service_pause()
    cid=f'C{k}';folder=ROOT/'candidates'/run_id/method/cid;result_path=folder/'proposal_result.json'
    if result_path.exists():return folder,read(result_path)
    folder.mkdir(parents=True,exist_ok=True)
    for name in ['policy.py','system.txt']:shutil.copy2(parent_source/name,folder/name)
    shutil.copy2(meta_source,folder/'meta.py')
    dev,images=dev_packet(parent_dev)
    packet={'development':dev,'archive':archive,'sceneevolve_teacher_template':(ROOT/'backend/prompt-templates/proposer.txt').read_text(),'iteration':k,'remaining_candidates':total_candidates-k}
    def meta_timeout(signum,frame):
        raise TimeoutError('Meta program exceeded 10 CPU/wall seconds')
    previous_handler=signal.signal(signal.SIGALRM,meta_timeout)
    signal.alarm(10)
    try:
        meta=load_module(meta_source);plan=meta.plan(packet)
        if not isinstance(plan,dict) or not isinstance(plan.get('instruction'),str):raise ValueError('Invalid meta plan')
        requested=plan.get('probes',[])
        if not isinstance(requested,list) or len(requested)>2:raise ValueError('Meta probe menu budget is at most two')
        for p in requested:
            if not isinstance(p,dict) or p.get('kind') not in ('camera_focal','object_scale','isolate') or p.get('scene_id') not in {r['scene_id'] for r in parent_dev}:raise ValueError('Meta probe is outside frozen development/menu contract')
        json.dumps(plan)
    except Exception as error:
        result={'status':'meta_execution_failed','error':repr(error),'M_changed':False,'used_M':str(meta_source)}
        write_json(result_path,result);return folder,result
    finally:
        signal.alarm(0);signal.signal(signal.SIGALRM,previous_handler)
    write_json(folder/'meta_execution.json',{'source':str(meta_source),'plan':plan,'actually_used_for_proposal':True,'phase':'before_proposal'})
    probes=[]
    for i,p in enumerate(plan.get('probes',[])[:2]):
        if p['kind'] not in ['camera_focal','object_scale','isolate']:raise ValueError('Invalid probe menu request')
        row=next((r for r in parent_dev if r['scene_id']==p['scene_id']),None)
        if row is None:raise ValueError('Probe scene is outside current development evidence')
        if row['status']!='complete':continue
        dest=folder/'probes'/f'{i+1}_{p["kind"]}';obs=inspect(Path(row['folder']),'probe',p['kind'],dest)
        observation={'scene_id':p['scene_id'],'probe':p['kind'],'result':obs}
        probe_png=dest/f'probe_{p["kind"]}.png'
        if probe_png.exists():
            images.append(str(probe_png))
            # Image-only measurement uses the unchanged submitted blend only for reopen validation.
            from evaluate import score
            shutil.copy2(Path(row['folder'])/'scene.blend',dest/'scene.blend')
            shutil.copy2(probe_png,dest/'final.png')
            observation['visual_metrics']=score(Path(row['folder'])/'reference.png',dest,config())
            observation['baseline_visual_metrics']=row['metrics']
        probes.append(observation)
    write_json(folder/'diagnostic_observations.json',{'initial_diagnoses':plan.get('diagnoses',[]),'probes':probes})
    sources={name:(folder/name).read_text() for name in ['policy.py','system.txt','meta.py']}
    api={str(p.relative_to(ROOT/'backend/sceneact')):p.read_text() for p in sorted((ROOT/'backend/sceneact').glob('*.py'))}
    archive_dev=[]
    for item in archive:
        old=ROOT/'results'/run_id/method/item['candidate_id']/'development'
        previous=[read(p) for p in sorted(old.glob('*/record.json')) if str(p.parent) not in {r['folder'] for r in parent_dev}]
        evidence,attached=dev_packet(previous)
        archive_dev.extend(evidence);images.extend(attached)
    payload={'archive_raw_development':archive_dev,'method':method,'candidate_id':cid,'source_files':sources,'fixed_sceneact_sources':api,'development':dev,'archive':archive,'controlled_probes':probes,'meta_plan':plan,'attached_images':images}
    projection=bound_payload(payload)
    write_json(folder/'evidence_projection.json',projection)
    prompt=COMMON+' You may return requested_probes (up to the unused portion of two probes) to inspect a current parent development scene before finalizing changes; a second and final proposer call then receives results. Return an empty list when no further diagnostics are needed. Already executed probe count: '+str(len(probes))+'\n'+plan['instruction']+'\nEXPLICIT_INPUT_JSON\n'+json.dumps(payload,ensure_ascii=False)
    schema={'type':'object','additionalProperties':False,'properties':{'requested_probes':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{'scene_id':{'type':'string'},'kind':{'type':'string','enum':['camera_focal','object_scale','isolate']}},'required':['scene_id','kind']}},'files':{'type':'array','items':{'type':'object','additionalProperties':False,'properties':{'path':{'type':'string','enum':['policy.py','system.txt','meta.py']},'content':{'type':'string'}},'required':['path','content']}},'rationale':{'type':'string'},'scope':{'type':'string'},'diagnosis':{'type':'string'}},'required':['requested_probes','files','rationale','scope','diagnosis']}
    try:
        if len(prompt.encode())>600000:raise ValueError('Common proposer evidence cap exceeded after fixed projection (600000 bytes)')
        answer,session=call(prompt,config()['proposer'],folder/'proposal_call',images,role='proposer',schema=schema)
        result=json.loads(answer)
        requested=result.get('requested_probes',[])
        if requested:
            if len(requested)+len(probes)>2:raise ValueError('Diagnostic budget exceeded')
            for i,p in enumerate(requested,len(probes)+1):
                row=next((r for r in parent_dev if r['scene_id']==p['scene_id']),None)
                if row is None:raise ValueError('Probe scene is outside current development evidence')
                if row['status']!='complete':raise ValueError('Probe needs valid parent output')
                dest=folder/'probes'/f'{i}_{p["kind"]}'
                obs=inspect(Path(row['folder']),'probe',p['kind'],dest)
                observation={'scene_id':p['scene_id'],'probe':p['kind'],'result':obs}
                png=dest/f'probe_{p["kind"]}.png'
                if png.exists():
                    images.append(str(png))
                    from evaluate import score
                    shutil.copy2(Path(row['folder'])/'scene.blend',dest/'scene.blend');shutil.copy2(png,dest/'final.png')
                    observation['visual_metrics']=score(Path(row['folder'])/'reference.png',dest,config());observation['baseline_visual_metrics']=row['metrics']
                probes.append(observation)
            write_json(folder/'diagnostic_observations.json',{'initial_diagnoses':plan.get('diagnoses',[]),'probes':probes})
            continuation=prompt+'\nYOUR_PRELIMINARY_RESPONSE\n'+answer+'\nACTUAL_PROBE_RESULTS\n'+json.dumps(probes,ensure_ascii=False)+'\nThis is the last proposal call. Return requested_probes=[] and complete final shared files.'
            if len(continuation.encode())>600000:raise ValueError('Common proposer continuation cap exceeded (600000 bytes)')
            answer,session=call(continuation,config()['proposer'],folder/'proposal_call_2',images,role='proposer',schema=schema)
            result=json.loads(answer)
            if result.get('requested_probes'):raise ValueError('No further proposer calls allowed')
        changes={item['path']:item['content'] for item in result['files']}
        if method=='sceneevolve_cli' and 'meta.py' in changes and changes['meta.py']!=sources['meta.py']:raise ValueError('SceneEvolve meta must stay fixed')
        for name,content in changes.items():
            if name not in sources:raise ValueError('File outside allowed set')
            if name.endswith('.py'):validate_source(content,name)
        if all(changes.get(n,sources[n])==sources[n] for n in ['policy.py','system.txt']):raise ValueError('Candidate did not modify shared H')
        for name,content in changes.items():(folder/name).write_text(content)
        diff=''.join(''.join(difflib.unified_diff(sources[n].splitlines(True),(folder/n).read_text().splitlines(True),fromfile='parent/'+n,tofile=cid+'/'+n)) for n in sources)
        (folder/'changes.diff').write_text(diff)
        before_meta=ast.parse(sources['meta.py']);after_meta=ast.parse((folder/'meta.py').read_text())
        for tree in [before_meta,after_meta]:
            for node in ast.walk(tree):
                if isinstance(node,ast.Constant) and isinstance(node.value,str):node.value='<string>'
        strategy_changed=ast.dump(before_meta)!=ast.dump(after_meta)
        result.update({'M_strategy_structure_changed':strategy_changed,'status':'proposed','M_changed':(folder/'meta.py').read_text()!=sources['meta.py'],'parent_source':str(parent_source),'used_M':str(meta_source)})
    except (ValueError,SyntaxError,RuntimeError,OSError,subprocess.TimeoutExpired) as error:
        result={'status':'proposal_failed','error':str(error),'M_changed':False,'parent_source':str(parent_source),'used_M':str(meta_source)}
    write_json(result_path,result);write_json(ROOT/'ledger.json',current());check_service_pause();return folder,result

def main():
    if not (ROOT/'protocol_frozen.json').exists():raise RuntimeError('Freeze protocol after successful smoke before pilot')
    frozen=read(ROOT/'selection_freeze.json')
    if frozen:
        final_scenes=[s for s in read(ROOT/'manifest.json') if s['split']=='test']
        if all((ROOT/'results'/c['run_id']/c['method']/c['candidate_id']/'test'/s['scene_id']/'record.json').exists() for c in frozen['choices'] for s in final_scenes):
            write_json(ROOT/'state.json',{'phase':'main_complete','source':'resume_of_existing_completed_records','selection_freeze_preserved':True})
            return
    initialize(ROOT);cfg=config();scenes=read(ROOT/'manifest.json');dev=[s for s in scenes if s['split']=='development'];selection=[s for s in scenes if s['split']=='selection'];test=[s for s in scenes if s['split']=='test']
    baseline=ROOT/'backend/harnesses/baseline';archive=read(ROOT/'archive.json',[])
    states={}
    for rid in ['r1','r2']:
        bdev=[run_scene('fixed_h0',rid,'H0',s,baseline) for s in dev]
        bsel=[run_scene('fixed_h0',rid,'H0',s,baseline) for s in selection]
        for method in METHODS:
            states[(rid,method)]={'source':baseline,'meta':ROOT/'initial_meta'/method/'meta.py','dev':bdev,'base':summarize(bsel),'best':summarize(bsel),'selected':'H0','selected_source':baseline}
    # Interleave repeat and method at each candidate number. No method runs its full search first.
    for k in [1,2]:
        for rid in ['r1','r2']:
            for method in METHODS:
                state=states[(rid,method)]
                prior=[a for a in archive if a['run_id']==rid and a['method']==method and a['candidate_id']!=f'C{k}']
                source,result=propose(method,rid,k,state['source'],state['meta'],state['dev'],prior)
                if result['status']=='proposed':
                    drows=[run_scene(method,rid,f'C{k}',s,source,str(state['source']),str(state['meta'])) for s in dev]
                    srows=[run_scene(method,rid,f'C{k}',s,source,str(state['source']),str(state['meta'])) for s in selection]
                    summary=summarize(srows);accepted=better(summary,state['base'],state['best'])
                    entry={'method':method,'run_id':rid,'candidate_id':f'C{k}','parent_id':str(state['source']),'status':'evaluated','development':summarize(drows),'selection':summary,'accepted':accepted,'M_changed':result['M_changed'],'M_strategy_structure_changed':result.get('M_strategy_structure_changed',False),'M_used':str(state['meta'])}
                    if accepted:state.update({'best':summary,'selected':f'C{k}','selected_source':source})
                    if method=='sceneevolve_cli':
                        if accepted:state.update({'source':source,'dev':drows})
                    else:
                        # Explore the valid descendant even when not accepted; H0 remains in the selection pool.
                        state.update({'source':source,'meta':source/'meta.py','dev':drows})
                else:
                    entry={'method':method,'run_id':rid,'candidate_id':f'C{k}','status':result['status'],'error':result.get('error'),'accepted':False}
                archive=[a for a in archive if not (a['method']==method and a['run_id']==rid and a['candidate_id']==f'C{k}')]+[entry]
                write_json(ROOT/'archive.json',archive)
    choices=[{'method':m,'run_id':r,'candidate_id':s['selected'],'source':str(s['selected_source']),'selection':s['best']} for (r,m),s in states.items()]
    choices += [{'method':'fixed_h0','run_id':r,'candidate_id':'H0','source':str(baseline)} for r in ['r1','r2']]
    write_json(ROOT/'selections.json',choices)
    if frozen:
        if choices!=frozen['choices']:raise RuntimeError('Resume choices differ from original frozen Selection; refusing to overwrite')
    else:
        write_json(ROOT/'selection_freeze.json',{'frozen':True,'time':time.time(),'choices':choices,'test_feedback_available_before_freeze':False})
    for scene in test:
        for rid in ['r1','r2']:
            for method in ['fixed_h0']+METHODS:
                chosen=next(c for c in choices if c['run_id']==rid and c['method']==method)
                if method!='fixed_h0' and chosen['candidate_id']=='H0':
                    original=ROOT/'results'/rid/'fixed_h0'/'H0'/'test'/scene['scene_id']
                    reused=ROOT/'results'/rid/method/'H0'/'test'/scene['scene_id']
                    reused.mkdir(parents=True,exist_ok=True)
                    if not (reused/'record.json').exists():
                        row=read(original/'record.json')
                        row={**row,'method':method,'folder':str(reused),'reuse_of':str(original),'usage':{'calls':0,'executions':0,'input_tokens':0,'output_tokens':0,'total_tokens':0,'reuse_original_usage':row['usage']},'seconds':0,'selected':True}
                        for name in ['reference.png','final.png','scene.blend','build.py','camera.json']:
                            if (original/name).exists() and not (reused/name).exists():(reused/name).symlink_to(original/name)
                        if (original/'functional').exists():
                            (reused/'functional').mkdir(exist_ok=True)
                            for f in (original/'functional').iterdir():
                                if f.is_file() and f.name!='text_edit.json':(reused/'functional'/f.name).symlink_to(f)
                        write_json(reused/'record.json',row)
                    row=read(reused/'record.json')
                else:
                    row=run_scene(method,rid,chosen['candidate_id'],scene,Path(chosen['source']))
                if row['status']=='complete' and scene==test[0]:inspect(Path(row['folder']),'views')
    write_json(ROOT/'state.json',{'phase':'main_complete','time':time.time(),'pending':['text_editor','independent_judge','ablations','frozen_meta_replay','external_blenderworld']})
    write_json(ROOT/'ledger.json',current())

if __name__=='__main__':main()
