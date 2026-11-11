"""V3 continuous ten-round experiment; explicit state, fixed evaluator, no hidden retries."""
import argparse,ast,difflib,json,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from data import write_json
from processes import cpu_environment,run_measured
from budget import current,guard
from codex_wrapper import check_service_pause
from regression import gate,MENU
from research import ResearchAPI,load_meta,sources,validate_source,change_kind,m_change_executed,action_reuse_evidence
from bw_evaluate import collect_evidence,judge_artifact,qualification

H_START='historical_r1_C2_start'
def cfg():return json.loads((ROOT/'config.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def manifest(split):return [s for s in read(ROOT/'manifest.json') if s['split']==split]
def hpath(name):return ROOT/'fixed_h'/name if name==H_START else ROOT/'candidates'/('C'+name[1:])/'H'
def mpath(name):return ROOT/'initial_m' if name=='M000' else ROOT/'candidates'/('C'+name[1:])/'M'
def settings_env(kind='blender'):
    c=cfg();return cpu_environment(threads=c['resources']['threads_per_'+kind])

def prepare_task(scene,folder):
    from PIL import Image,ImageOps
    folder.mkdir(parents=True,exist_ok=True)
    with Image.open(scene['image_path']) as im:
        im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((512,512));im.save(folder/'reference.png')
    instruction=Path(scene['query_path']).read_text() if scene['query_path'] else 'Reconstruct the visible indoor scene as editable three-dimensional objects, preserving visible layout, proportions and appearance.'
    public_specs=[]
    for raw in scene['attachments']:
        path=Path(raw)
        if path.suffix.lower() not in {'.txt','.md','.yaml','.yml','.json'} or 'rubric' in path.name.lower():
            raise ValueError('Unsupported public task attachment; do not silently omit: '+str(path))
        instruction+='\nPUBLIC TASK ATTACHMENT '+path.name+':\n'+path.read_text()
        public_specs.append(str(path))
    task={'image':str(folder/'reference.png'),'width':im.width,'height':im.height,'instruction':instruction,'public_attachment_sources':public_specs}
    write_json(folder/'task.json',task);return task

def functional(folder):
    c=cfg();dest=folder/'functional';dest.mkdir(exist_ok=True)
    if not (folder/'scene.blend').exists():
        return {'checks':{'structure':gate(True,False,None),'material':gate(True,False,None)},'functional_pass':False}
    if not (dest/'process.json').exists():
        from devices import inspection_config
        settings,env=inspection_config(c,dest)
        command=[c['blender']['executable'],'--background','--disable-autoexec','--threads',str(c['resources']['threads_per_blender']),'--python-exit-code','1','--python',str(ROOT/'inspect_blend.py'),'--','--blend',str(folder/'scene.blend'),'--output-dir',str(dest),'--settings',str(settings),'--mode','mechanical']
        guard('render',3)
        with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
            run_measured(command,timeout=c['blender']['timeout'],measurement_path=dest/'process.json',memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=env)
    structure=read(dest/'scene_structure.json') if (dest/'scene_structure.json').exists() else None
    mechanical=read(dest/'mechanical.json') if (dest/'mechanical.json').exists() else {}
    measured=bool(structure['finite_nonempty_mesh_count']>0 and structure['finite_nonempty_mesh_count']==structure['mesh_count'] and structure['finite_matrices']) if structure else None
    material=mechanical.get('material',{});move=mechanical.get('move',{})
    checks={'structure':gate(True,structure is not None,measured),
            'material':gate(True,material.get('applicable',False),material.get('pass')),
            'composite_move':gate(False,move.get('applicable',False),move.get('pass'))}
    for name,row in (structure['structural_checks'].items() if structure else []):
        if isinstance(row,dict) and 'applicable' in row and 'measured_pass' in row:
            checks[name]=gate(name=='hierarchy_parts' and row['applicable'],row['applicable'],row['measured_pass'])
    result={'checks':checks,'functional_pass':all(v['gate_pass'] for v in checks.values()),
            'structure':structure,'mechanical':mechanical,
            'interpretation':'Mechanical structure/material operation; no text editor or natural-image 3D ground truth. Support AABB approximate; optional collision crossings not full solidity truth.'}
    write_json(dest/'summary.json',result);return result

def run_scene(scene,h,m,repeat=1,*,preparation=False,evaluate_bw=True):
    check_service_pause()
    c=cfg();folder=ROOT/('preparation/second_smoke' if preparation else 'results')/h/scene['split']/scene['scene_id']/str(repeat)
    if (folder/'record.json').exists():
        cached=read(folder/'record.json')
        if not evaluate_bw:return cached
        current_evidence=(cached['bw'].get('delivery_evidence_version')=='original_delivery_metadata_A02'
                          and cached['bw'].get('native_evidence_version')==c['evaluation']['native_evidence_version'])
        if current_evidence and cached['bw']['evaluation_status']!='not_requested_preview':return cached
        write_json(folder/'record_before_endpoint_evaluation.json',cached)
    if scene['split']=='test' and not (ROOT/'final_selection_freeze.json').exists():raise RuntimeError('Final Test sealed until ten rounds and H selection frozen')
    task=prepare_task(scene,folder);start=time.monotonic()
    # H receives only its own task/config: no manifest, evaluator rubric or test root.
    inner={k:c[k] for k in ['model','budget','render','blender','resources']}
    write_json(folder/'generation_config.json',inner)
    if not (folder/'status.json').exists():
        if (folder/'student_calls').exists():raise RuntimeError('Interrupted generation requires explicit review; never resample automatically: '+str(folder))
        cmd=[sys.executable,str(ROOT/'backend/inner_loop.py'),'--config',str(folder/'generation_config.json'),'--task',str(folder/'task.json'),'--source-dir',str(hpath(h)),'--output-dir',str(folder)]
        write_json(ROOT/'state.json',{**read(ROOT/'state.json'),'phase':'generation','current_scene':scene['scene_id'],'current_H':h,'current_split':scene['split']})
        with (folder/'runner_stdout.log').open('w') as out,(folder/'runner_stderr.log').open('w') as err:
            process=run_measured(cmd,timeout=c['budget']['seconds']+15,measurement_path=folder/'generation_process.json',memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=settings_env())
        if not (folder/'status.json').exists():write_json(folder/'status.json',{'error':'outer_timeout' if process['timed_out'] else 'missing_inner_status','seconds':process['seconds']})
    check_service_pause()
    from evaluate import score
    import torch
    torch.set_num_threads(c['resources']['threads_per_metric'])
    metrics=score(task['image'],folder,c)
    fn=functional(folder)
    status=read(folder/'status.json');generation_valid=metrics['valid']
    bw={'evaluation_status':'not_started','S_BW':None,'S_rubric':None,'S_dimension':None}
    if generation_valid and evaluate_bw:
        evidence=folder/'bw_evidence'
        if not (evidence/'evidence_status.json').exists():collect_evidence(folder/'scene.blend',evidence,c,preview=scene['split']=='development')
        if (evidence/'evaluation.json').exists():bw=read(evidence/'evaluation.json')
        else:
            rubric=read(Path(scene['rubric_path']))
            bw=judge_artifact(task['image'],evidence,rubric,c,folder/(c['evaluation']['judge_revision']+'_1'))
            if bw['evaluation_status']=='eval_failed':
                write_json(evidence/'evaluation_attempt1.json',bw)
                bw=judge_artifact(task['image'],evidence,rubric,c,folder/(c['evaluation']['judge_revision']+'_2'))
    if generation_valid and not evaluate_bw:bw['evaluation_status']='not_requested_preview'
    failure_type=None
    if not generation_valid:
        sessions=[read(p) for p in folder.glob('student_calls/*/session.json')]
        steps=[read(p) for p in folder.glob('steps/*/result.json')]
        failure_type=next((r['failure_type'] for r in reversed(steps) if r.get('failure_type')),None)
        if not failure_type and any(s['status']!='completed' for s in sessions):failure_type='model_call_timeout' if any('TimeoutExpired' in str(s.get('error')) for s in sessions) else 'model_service_error'
        if not failure_type:failure_type='total_budget_exceeded' if 'timeout' in str(status).lower() or 'Budget' in str(status) else 'invalid_generated_program'
    eligible=qualification('completed' if generation_valid else 'failed',bw['evaluation_status'],list(fn['checks'].values()))['eligible']
    record={'method':'scene_rsi_v3','run_id':'continuous_10','scene_id':scene['scene_id'],'source_id':scene['source_id'],'split':scene['split'],'H_version':h,'M_version':m,'repeat':repeat,
            'status':'completed' if generation_valid else 'failed','evaluation_status':bw['evaluation_status'],'failure_type':failure_type,'valid':generation_valid,'eligible':eligible,'loaded_H_modules':status.get('loaded_H_modules',[]),'metrics':metrics,'bw':bw,'functional':fn,
            'e2e_utility':bw['S_BW'] if bw['evaluation_status']=='completed' else 0 if not generation_valid else None,
            'folder':str(folder),'seconds':time.monotonic()-start,'generation_seconds':status['seconds'],'evaluation_scope':'seconds is current evaluation/generation invocation wall; resumed evaluation is recorded separately; see timing.csv for every process','device':'CPU','threads':c['resources']['threads_per_blender'],
            'model_roles':{'H':c['model']['name'],'M':c['proposer']['model'],'judge':c['evaluation']['judge_model']},'cost':read(folder/'usage.json')}
    write_json(folder/'record.json',record)
    print(json.dumps({'scene':scene['scene_id'],'H':h,'split':scene['split'],'valid':generation_valid,'BW':bw['S_BW'],'eligible':eligible}),flush=True)
    return record

def aggregate(records):
    measured=[r['bw']['S_BW'] for r in records if r['bw']['evaluation_status']=='completed']
    return {'all_scheduled':len(records),'completed':sum(r['status']=='completed' for r in records),
            'evaluation_completed':len(measured),'eligible':all(r['eligible'] for r in records) and len(records)==cfg()['pilot']['selection_size'],
            'S_BW':sum(measured)/len(measured) if measured else None,'Q':sum(r['metrics']['overall'] for r in records if r['metrics']['overall'] is not None)/sum(r['metrics']['overall'] is not None for r in records) if any(r['metrics']['overall'] is not None for r in records) else None}

def decide_h(selected,parent,delta):
    gain=selected['S_BW']-parent['S_BW'] if selected['S_BW'] is not None and parent['S_BW'] is not None else None
    expected=cfg()['pilot']['selection_size']
    recovery=not parent['eligible'] and (parent['completed']<expected or parent['evaluation_completed']==expected)
    accepted=selected['eligible'] and (recovery or parent['eligible'] and gain is not None and gain>=delta)
    return accepted,gain,recovery

def context_for(records,h,m,round_number):
    scenes={};images=[];evidence=[]
    for r in records:
        f=Path(r['folder']);objects=(r['functional'].get('structure') or {}).get('objects',[])
        from PIL import Image
        with Image.open(f/('final.png' if r['valid'] else 'reference.png')) as input_image:width,height=input_image.size
        scenes[r['scene_id']]={'width':width,'height':height,'valid_blend':bool((r['functional'].get('structure') or {}).get('blend_opened')),'blend_path':str(f/'scene.blend'),'object_ids':[o['name'] for o in objects]}
        img=[str(f/'reference.png')]+([str(f/'final.png')] if r['valid'] else [])
        indices=list(range(len(images)+1,len(images)+len(img)+1));images+=img
        from model_evidence import compact_structure,compact_trajectory
        summary=compact_structure(json.loads(json.dumps(r['functional'].get('structure'))))
        from model_evidence import projected_objects
        concise_objects=[{k:o[k] for k in ['name','type','parent','projected_bbox_normalized_approx']} for o in projected_objects(objects)]
        trajectory=compact_trajectory((f/'trajectory.jsonl').read_text()) if (f/'trajectory.jsonl').exists() else None
        evidence.append({'scene_id':r['scene_id'],'H_version':h,'reference_and_render_attachment_indices':indices,'status':r['status'],'metrics':r['metrics'],'BW_preview':{'evaluation_status':'not_provided_during_research','S_BW':None,'reason':'A02 common protocol: current references/renders, numeric image metrics and native functional evidence; independent development BW only for final endpoints. Historical A01 preview ratings remain archived.'},'object_inventory_all':[[o[k] for k in ['name','type','parent']] for o in objects],'object_inventory_columns':['name','type','parent'],'objects':concise_objects,'object_projection_rule':'At most128 named groups/cameras/lights/named meshes in fixed name order for detailed projection; every actual object remains in object_inventory_all. This is an evidence budget, not fault attribution.','functional':{'checks':r['functional']['checks'],'structure_summary':summary},'program':(f/'build.py').read_text() if (f/'build.py').exists() else None,'trajectory':trajectory})
    archive=[]
    for p in sorted((ROOT/'rounds').glob('*/record.json')):
        row=read(p);archive.append({k:row[k] for k in ['round','candidate_type','H_accepted','M_accepted','reason','selection','status']})
    packet={'round':round_number,'H_sources':sources(hpath(h)),'M_sources':sources(m),'development':evidence,'archive_aggregate_selection_only':archive,
            'available_public_sceneact_API':{p.name:p.read_text() for p in (ROOT/'backend/sceneact').glob('*.py')},
            'regression_interface':{'public_module':'regression','tests':MENU,'description':'M chooses which actual checks to execute via actions; final gates stay fixed.'},
            'available_probe_menu':[name for name in sources(m) if name.startswith('actions/')],
            'remaining_probe_budget':cfg()['pilot']['diagnostic_frames_per_round'],'already_executed_probe_count':0,
            'fixed_goal':'BW-style reconstruction quality with absolute execution and necessary functional qualification on separate Selection. Test inaccessible.'}
    from model_evidence import bound_payload
    bound_payload(packet,limit=420000)
    return packet,scenes,images

def validate_side(folder,kind):
    names=[p.stem for p in folder.glob('*.py')]
    for p in folder.rglob('*.py'):
        validate_source(p.read_text(),p.name if p.name in ['policy.py','meta.py'] else 'action' if 'actions' in p.parts else 'helper',names+['regression'])
    if kind=='H' and (not (folder/'policy.py').exists() or not (folder/'system.txt').exists()):raise ValueError('H entry contract missing')
    if kind=='M' and not (folder/'meta.py').exists():raise ValueError('M entry contract missing')

def validate_candidate(h,m):
    validate_side(h,'H');validate_side(m,'M')

def exercise_meta_interface(m,packet):
    class StopAPI:
        def __init__(self):self.calls=0
        def remaining(self):return {'sessions':1-self.calls,'diagnostic_frames':0,'seconds':1}
        def ask(self,context):
            self.calls+=1
            return {'decision':'stop','scene_id':'','action_name':'','parameters_json':'{}','expectation':'','analysis':'Interface fixture stop; no model call','scope':'','new_action_source':'','changes':[]}
        def record_decision(self,decision):pass
        def create_action(self,name,source,scope):validate_source(source,'action')
        def execute_action(self,*args):
            self.calls+=1
            return {'status':'unavailable','measurement':None,'reason':'Interface fixture only; no geometry measurement was made'}
    api=StopAPI();result=load_meta(m).research(packet,api)
    if not isinstance(result,dict) or 'changes' not in result:raise ValueError('M returned invalid proposal contract')
    return {'executed':True,'model_calls':0,'fixture':'fixed stop response, not ability evidence'}

def selection(h,m):
    repeats=read(ROOT/'configs/selection_repeats.json')[h]
    return [run_scene(s,h,m,repeats[s['scene_id']]) for s in manifest('selection')]

def request_boundary_case(comparison_id):
    path=ROOT/'selection_boundary_cases.json'
    cases=read(path) if path.exists() else []
    if any(case['candidate']==comparison_id for case in cases):return True
    if len(cases)>=cfg()['pilot']['boundary_case_limit']:return False
    cases.append({'candidate':comparison_id,'time':time.time(),'judge_sessions':2*cfg()['pilot']['selection_size']})
    write_json(path,cases);return True

def boundary_review(candidate_records,parent_records,comparison_id):
    c=cfg()
    for records in [parent_records,candidate_records]:
        for index,r in enumerate(records):
            if r['bw']['evaluation_status']!='completed':continue
            folder=Path(r['folder']);newpath=folder/('boundary_evaluation_'+comparison_id+'.json')
            if not newpath.exists():
                scene=next(s for s in manifest('selection') if s['scene_id']==r['scene_id'])
                judge=ROOT/'evaluation_sessions'/('boundary_'+comparison_id+'_'+str(time.time_ns()))
                original=read(folder/'bw_evidence/evaluation.json')
                write_json(folder/'bw_evidence/evaluation_before_boundary.json',original)
                new=judge_artifact(folder/'reference.png',folder/'bw_evidence',read(Path(scene['rubric_path'])),c,judge)
                write_json(newpath,new)
            new=read(newpath)
            if new['evaluation_status']!='completed':
                r['bw_judgments']=r.get('bw_judgments',[{'comparison':'initial','S_BW':r['bw']['S_BW']}])+[{'comparison':comparison_id,'S_BW':None,'status':'eval_failed'}]
                r['eligible']=False
                r['bw']={**r['bw'],'S_BW':None,'evaluation_status':'eval_failed','boundary_error':new.get('evaluation_error')}
            else:
                history=r.get('bw_judgments',[{'comparison':'initial','S_BW':r['bw']['S_BW']}])
                if not any(j['comparison']==comparison_id for j in history):history.append({'comparison':comparison_id,'S_BW':new['S_BW']})
                r['bw_judgments']=history
                r['bw']={**r['bw'],'S_BW':sum(j['S_BW'] for j in history)/len(history),'repeated_judgments_used':len(history)}
            write_json(folder/'record.json',r)
    return aggregate(candidate_records),aggregate(parent_records)

def run_round(t,state):
    check_service_pause()
    c=cfg();dest=ROOT/'rounds'/f'{t:02d}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'record.json').exists():return read(dest/'record.json')
    h,m=state['H_retained'],state['M_retained'];candidate=f'C{t:02d}';h_candidate=f'H{t:02d}';m_candidate=f'M{t:02d}'
    folder=ROOT/'candidates'/candidate;ch,cm=folder/'H',folder/'M'
    if (folder/'research_started.json').exists() and not (folder/'proposal.json').exists():raise RuntimeError('Interrupted research has no completed proposal; preserve state for explicit review, do not resample candidate')
    if not ch.exists():shutil.copytree(hpath(h),ch)
    if not cm.exists():shutil.copytree(mpath(m),cm)
    dev=manifest('development');n=c['pilot']['development_panel_size'];panel=[dev[((t-1)*n+i)%len(dev)] for i in range(n)]
    records=[run_scene(s,h,m,evaluate_bw=False) for s in panel]
    packet,scenes,images=context_for(records,h,cm,t)
    write_json(dest/'development_evidence_versions.json',{'H':h,'M':m,'scene_ids':[s['scene_id'] for s in panel],'records':[r['folder'] for r in records]})
    api=ResearchAPI(c,ROOT/'meta_traces'/f'round{t:02d}',ch,cm,scenes,images)
    if not (folder/'research_started.json').exists():write_json(folder/'research_started.json',{'time':time.time(),'H_parent':h,'M_parent':m,'M_program_used':str(mpath(m)/'meta.py')})
    kind='unchanged';h_ok=False;m_ok=False;reason='';proposal=None;selected=None;phase='research'
    try:
        # Execute actual current M, not a fixed external prompt-only policy.
        if not (folder/'proposal.json').exists():
            request={'context':packet,'scenes':scenes,'images':images,'H':str(ch),'M_candidate':str(cm),'M_program':str(mpath(m)),'trace_folder':str(api.folder),'result_folder':str(folder)}
            write_json(folder/'research_request.json',request)
            command=[sys.executable,str(ROOT/'research_worker.py'),'research','--request',str(folder/'research_request.json')]
            with (folder/'research_stdout.log').open('w') as out,(folder/'research_stderr.log').open('w') as err:
                process=run_measured(command,timeout=c['pilot']['research_seconds_per_round'],measurement_path=folder/'research_process.json',memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=settings_env())
        else:
            request=read(folder/'research_request.json');packet=request['context']
            process=read(folder/'research_process.json')
            write_json(folder/'research_explicit_reuse.json',{'time':time.time(),'reason':'Resume complete recorded proposal; no new research call'})
        if (folder/'worker_summary.json').exists():
            summary=read(folder/'worker_summary.json');api.sessions=summary['sessions'];api.frames=summary['frames'];api.executed_actions=summary['actions']
        else:
            api.sessions=len(list((api.folder/'calls').glob('*/request.json')))
            api.executed_actions=[read(p) for p in (api.folder/'actions').glob('*/observation.json')]
            api.frames=len(list((api.folder/'actions').glob('*/settings.json')))
        if process['returncode']!=0:raise RuntimeError('M research worker failed or timed out; '+str(folder/'research_stderr.log'))
        proposal=read(folder/'proposal.json')
        phase='validation'
        for change in proposal['changes']:
            base=ch if change['target']=='H' else cm
            relative=Path(change['path']);target=base/relative
            if relative.stem in {'runtime','processes','codex_wrapper','evaluate','render','sceneact','budget','eval_blend','bw_evaluate'}:raise ValueError('Cannot shadow fixed runtime/representation/evaluator modules')
            if relative.is_absolute() or '..' in relative.parts or target.suffix not in ['.py','.txt','.md']:raise ValueError('Patch outside allowed H/M files')
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(change['content'])
        kind=change_kind(hpath(h),mpath(m),ch,cm)
        h_valid=True;h_error=None
        try:validate_side(ch,'H')
        except (ValueError,SyntaxError,ImportError) as error:
            h_valid=False;h_error=repr(error);write_json(folder/'H_validation_error.json',{'error':h_error})
        for name,parent,new in [('H',hpath(h),ch),('M',mpath(m),cm)]:
            before,after=sources(parent),sources(new)
            diff=''.join(''.join(difflib.unified_diff(before.get(p,'').splitlines(True),after.get(p,'').splitlines(True),fromfile=name+'_parent/'+p,tofile=name+'_candidate/'+p)) for p in sorted(set(before)|set(after)))
            (folder/(name+'.diff')).write_text(diff)
        if kind in ['M-only','H+M']:
            try:
                validate_side(cm,'M')
                command=[sys.executable,str(ROOT/'research_worker.py'),'contract','--request',str(folder/'research_request.json')]
                with (folder/'M_contract_stdout.log').open('w') as out,(folder/'M_contract_stderr.log').open('w') as err:
                    measured=run_measured(command,timeout=15,measurement_path=folder/'M_contract_process.json',memory_limit_bytes=c['resources']['memory_limit_gb']*1024**3,stdout=out,stderr=err,env=settings_env())
                m_ok=measured['returncode']==0
                if not m_ok:write_json(folder/'M_validation_error.json',{'phase':'bounded_M_contract','returncode':measured['returncode'],'timed_out':measured['timed_out'],'stderr':str(folder/'M_contract_stderr.log')})
                created=[read(p) for p in api.folder.glob('created_action_*.json')]
                executed={a['action'] for a in api.executed_actions if a['status']=='completed'}
                executed_sources=[p.read_text() for p in (api.folder/'actions').glob('*/action.py') if (p.parent/'observation.json').exists() and read(p.parent/'observation.json')['status']=='completed']
                used=read(folder/'M_execution_contract.json')['loaded_M_helpers'] if measured['returncode']==0 else []
                program_change=m_change_executed(mpath(m),cm,used,executed_sources)
                write_json(folder/'M_program_change_evidence.json',program_change)
                m_ok=m_ok and program_change['effective_program_change']
                reuse=action_reuse_evidence(mpath(m),cm,list((api.folder/'actions').glob('*')),set(api.scenes))
                write_json(folder/'M_action_reuse_validation.json',{'actions':reuse,'required_distinct_development_scenes':2})
                if any(not row['pass'] for row in reuse):m_ok=False
                if any(a['name'] not in executed for a in created):
                    m_ok=False
                    write_json(folder/'M_action_validation.json',{'valid':False,'reason':'New reusable action not executed successfully','unexecuted':[a['name'] for a in created if a['name'] not in executed]})
            except (ValueError,SyntaxError,ImportError,KeyError,TypeError) as error:
                m_ok=False;write_json(folder/'M_validation_error.json',{'error':repr(error)})
        if kind in ['H-only','H+M'] and h_valid:
            phase='evaluation'
            candidate_records=selection(h_candidate,m);parent_records=selection(h,m)
            selected=aggregate(candidate_records);parent=aggregate(parent_records)
            old_sources,new_sources=sources(hpath(h)),sources(ch)
            changed_files={name for name in set(old_sources)|set(new_sources) if old_sources.get(name)!=new_sources.get(name)}
            used={str(Path(path).relative_to(ch)) for r in candidate_records for path in r['loaded_H_modules']}
            h_effective=bool(changed_files & ({'policy.py','system.txt'}|used))
            selected['changed_files']=sorted(changed_files);selected['changed_module_executed_or_entry_used']=h_effective
            selected['eligible']=selected['eligible'] and h_effective
            delta=c['evaluation']['promotion_delta'];gain=(selected['S_BW']-parent['S_BW']) if selected['S_BW'] is not None and parent['S_BW'] is not None else None
            boundary_unresolved=False
            if selected['eligible'] and parent['eligible'] and gain is not None and abs(gain-delta)<=c['evaluation']['boundary_width']:
                if request_boundary_case(candidate):
                    selected,parent=boundary_review(candidate_records,parent_records,candidate);gain=selected['S_BW']-parent['S_BW'] if selected['S_BW'] is not None and parent['S_BW'] is not None else None
                else:
                    boundary_unresolved=True
                    selected['boundary_evaluation_status']='not_started_budget'
                    selected['ranking_status']='unresolved_budget_rejection'
            h_ok,gain,parent_known_ineligible=decide_h(selected,parent,delta)
            h_ok=h_ok and not boundary_unresolved
            reason=('Frozen boundary-case allowance exhausted; quality promotion unresolved, parent retained. Not an algorithm/functional failure.' if boundary_unresolved else 'Absolute qualification recovery from ineligible parent; not a paired visual gain claim' if h_ok and parent_known_ineligible else 'Selection absolute eligibility then frozen BW gain rule; delta='+str(gain))
        else:reason=('Independent H validation failed: '+str(h_error)) if not h_valid else 'M-only exploration; H unchanged' if m_ok else 'No source change or invalid M; not an accepted descendant'
        status='completed'
    except (RuntimeError,ValueError,SyntaxError,KeyError,TypeError,ImportError) as exc:
        if (ROOT/'service_pause.json').exists() or (ROOT/'protocol_pause.json').exists() or phase=='evaluation' or 'Budget exhausted' in str(exc) or 'safety cap' in str(exc):
            write_json(dest/'interrupted.json',{'phase':phase,'error':repr(exc),'traceback':traceback.format_exc(),'round_complete':False})
            raise
        reason=repr(exc);status='invalid' if proposal is not None else 'failed'
        write_json(folder/'error.json',{'error':reason,'traceback':traceback.format_exc(),'phase':'proposal_or_validation'})
    row={'round':t,'H_parent':h,'M_parent':m,'H_candidate':h_candidate if kind in ['H-only','H+M'] else None,'M_candidate':m_candidate if kind in ['M-only','H+M'] else None,'proposal_returned':proposal is not None,'new_source_candidate':kind!='unchanged',
         'candidate_type':kind,'H_accepted':h_ok,'M_accepted':m_ok,'H_retained':h_candidate if h_ok else h,'M_retained':m_candidate if m_ok else m,
         'status':status,'selection':selected,'reason':reason,'usage':current(),'M_program_used':str(mpath(m)/'meta.py'),'action_count':len(api.executed_actions),'sessions':api.sessions,'frames':api.frames,'proposal_path':str(folder/'proposal.json'),
         'platform_snapshot':c['pilot']['platform_snapshot'],'research_packet_version':c['pilot']['research_packet_version']}
    write_json(dest/'record.json',row)
    print(json.dumps(row,ensure_ascii=False),flush=True);return row

def run_10_rounds():
    if not (ROOT/'configs/freeze.json').exists():raise RuntimeError('Preflight/calibration/protocol must freeze before formal rounds')
    write_json(ROOT/'budget_phase.json',{'phase':'research','reserve_fraction':cfg()['pilot']['reserve_fraction']})
    state=read(ROOT/'state.json');state.update(formal_started=True,H_retained=state.get('H_retained',H_START),M_retained=state.get('M_retained','M000'))
    write_json(ROOT/'state.json',state)
    if not (ROOT/'round0.json').exists():
        dev=[run_scene(s,H_START,'M000',evaluate_bw=False) for s in manifest('development')]
        baseline=selection(H_START,'M000')
        write_json(ROOT/'round0.json',{'H':H_START,'development':len(dev),'selection':aggregate(baseline),'ledger':current(),
                                     'platform_version':cfg()['pilot']['platform_version']})
    for t in range(1,11):
        row=run_round(t,state);state.update(round_completed=t,H_retained=row['H_retained'],M_retained=row['M_retained'],phase='round_complete')
        write_json(ROOT/'state.json',state)
        if t in [5,10]:shutil.copytree(mpath(state['M_retained']),ROOT/'code_snapshots'/f'M_round{t:02d}',dirs_exist_ok=True)
    write_json(ROOT/'budget_phase.json',{'phase':'final'})
    state.update(H_best=state['H_retained'],final_selection_frozen=True)
    frozen=ROOT/'final_selection_freeze.json'
    choice={'rounds':10,'H_best':state['H_best'],'selection_only':True,'M_final':state['M_retained']}
    if frozen.exists():
        original=read(frozen)
        if any(original[key]!=value for key,value in choice.items()):raise RuntimeError('Resume cannot change the selection frozen before Final Test')
    else:write_json(frozen,{'time':time.time(),**choice})
    write_json(ROOT/'state.json',state)
    # Full development endpoints; identical versions deliberately reuse logged artifacts.
    for s in manifest('development'):
        for version in dict.fromkeys([H_START,state['H_best']]):
            run_scene(s,version,state['M_retained'])
    for checkpoint in [5,10]:
        version=read(ROOT/'rounds'/f'{checkpoint:02d}'/'record.json')['H_retained']
        for s in manifest('development')[:cfg()['pilot']['checkpoint_development_subset_size']]:run_scene(s,version,state['M_retained'],evaluate_bw=False)
    if not (ROOT/'test_repeat_plan.json').exists():
        usage=current();caps=cfg()['pilot'];needed=caps['final_test']['repeat2_requires_remaining']
        remaining={'cli_sessions':caps['max_cli_sessions']-usage['cli_sessions'],'render_attempts':caps['max_render_frames']-usage['render_attempts'],'input_tokens':caps['max_input_tokens']-usage['known_input_tokens'],'output_tokens':caps['max_output_tokens']-usage['known_output_tokens']}
        repeats=2 if all(remaining[k]>=v for k,v in needed.items()) else 1
        write_json(ROOT/'test_repeat_plan.json',{'time':time.time(),'repeats':repeats,'remaining_budget':remaining,'thresholds':needed,'decision_before_any_test':not any((ROOT/'results').glob('*/test/*/*/record.json')),'uses_test_quality':False})
    test_repeats=read(ROOT/'test_repeat_plan.json')['repeats']
    for s in manifest('test'):
        for repeat in range(1,test_repeats+1):
            for h in dict.fromkeys([H_START,state['H_best']]):run_scene(s,h,state['M_retained'],repeat)
    from semantic_edit import run_edit
    for scene_id in cfg()['pilot']['semantic_edit_subset']:
        scene=next(s for s in manifest('development') if s['scene_id']==scene_id)
        for version in dict.fromkeys([H_START,state['H_best']]):
            artifact=ROOT/'results'/version/'development'/scene_id/'1'
            destination=ROOT/'semantic_edits'/version/scene_id
            if (destination/'status.json').exists():continue
            if (artifact/'scene.blend').exists() and (artifact/'bw_evidence/scene_facts.json').exists():
                run_edit(scene_id,artifact/'scene.blend',artifact/'final.png',read(artifact/'bw_evidence/scene_facts.json'),cfg(),destination)
            else:
                destination.mkdir(parents=True,exist_ok=True);write_json(destination/'status.json',{'status':'not_started','reason':'No valid delivered blend/scene facts; no editor call','semantic_target_correctness':None})
    state.update(phase='all_scheduled_terminal',round_completed=10,meta_replay_status='pending_budget_and_actual_descendant_check')
    write_json(ROOT/'state.json',state)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['smoke','run_10_rounds','resume','report']);a=p.parse_args()
    if a.command=='report':
        import analyze;analyze.main()
    elif a.command=='smoke':run_scene(manifest('development')[0],H_START,'M000',preparation=True)
    else:run_10_rounds()
if __name__=='__main__':main()
