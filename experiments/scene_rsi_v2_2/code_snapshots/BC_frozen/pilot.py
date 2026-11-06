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
from model_evidence import compact_structure,compact_trajectory,bound_payload,projected_objects
from devices import inspection_config

METHODS=['scene_rsi_v2_1']

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
    required=['solve'] if kind=='policy.py' else ['plan_probes','plan_patch']
    for name in required:
        if not any(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body):raise ValueError('Missing '+name)
    permitted_system_paths={ast.dump(ast.parse(expr,mode='eval').body) for expr in ("Path(__file__).parent / 'system.txt'","Path(__file__).with_name('system.txt')")}
    for node in ast.walk(tree):
        if isinstance(node,ast.Name) and node.id.startswith('__') and node.id!='__file__':raise ValueError('Candidate built-in introspection outside contract')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
            if node.func.attr in ('open','read_bytes'):raise ValueError('Candidate file access outside contract')
            if node.func.attr=='read_text' and (kind!='policy.py' or ast.dump(node.func.value) not in permitted_system_paths):raise ValueError('Only literal candidate system.txt read is permitted')

def inspect(folder,mode='mechanical',probe=None,output=None,object_id=None,test=None):
    cfg=config();dest=output or folder/('functional' if mode=='mechanical' else mode)
    dest.mkdir(parents=True,exist_ok=True)
    result_file=dest/({'mechanical':'mechanical','inspect':'scene_structure','views':'views','probe':'probe','regression':'regression'}[mode]+'.json')
    if result_file.exists():return read(result_file)
    guard('render',{'inspect':0,'mechanical':3,'views':2,'probe':1,'regression':0}[mode])
    settings_path, environment = inspection_config(cfg, dest)
    args=[cfg['blender']['executable'],'--background','--disable-autoexec','--threads','2','--python-exit-code','2','--python',str(ROOT/'inspect_blend.py'),'--','--blend',str(folder/'scene.blend'),'--output-dir',str(dest),'--mode',mode,'--settings',str(settings_path)]
    if probe:args+=['--probe',probe]
    if object_id:args+=['--object-id',object_id]
    if test:args+=['--test',test]
    start=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        try:
            result=subprocess.run(args,stdout=out,stderr=err,env=environment,timeout=cfg['blender']['timeout'])
            status={'exit_code':result.returncode,'seconds':time.monotonic()-start}
        except subprocess.TimeoutExpired:
            status={'exit_code':None,'seconds':time.monotonic()-start,'error':'blender_timeout'}
    write_json(dest/'process.json',status)
    failure={'status':'failed','process':status}
    if mode=='regression':failure.update(applicable=False,measured_pass=None,reason='External Blender regression failed; not a passing check')
    return read(result_file,failure)

def functional(folder,scene):
    from regression import gate
    result=inspect(folder)
    structure=read(folder/'functional/scene_structure.json',{})
    material=result.get('material',{})
    move=result.get('move',{})
    geometric=structure.get('structural_checks',{})
    hierarchy=geometric.get('hierarchy_parts',{'applicable':False,'measured_pass':None})
    checks={
        'structure':gate(True,structure.get('blend_opened',False),structure.get('structure_pass')),
        'material':gate(True,material.get('applicable',False),material.get('pass')),
        'composite':gate(scene['expected_composite'],move.get('applicable',False),move.get('pass')),
        'declared_parts':gate(scene['expected_composite'],hierarchy['applicable'],hierarchy['measured_pass'])}
    record={'checks':checks,'functional_pass':all(c['gate_pass'] for c in checks.values()),
            'structure_pass':checks['structure']['gate_pass'] and checks['declared_parts']['gate_pass'],
            'material_pass':material.get('pass'),'composite_required':scene['expected_composite'],
            'composite_pass':move.get('pass'),'target_object':structure.get('target',{}).get('object','unknown'),
            'geometry':geometric,'semantic_object_completeness':None,'support_collision_truth':None,
            'interpretation':'Mechanical operations; emitted-part integrity; natural-image semantic completeness unknown. Optional failed checks retained but do not gate.'}
    write_json(folder/'functional/summary.json',record)
    return record

def failed_functional(scene):
    from regression import gate
    checks={'structure':gate(True,False,None),'material':gate(True,False,None),
            'composite':gate(scene['expected_composite'],False,None),
            'declared_parts':gate(scene['expected_composite'],False,None)}
    return {'checks':checks,'functional_pass':False,'structure_pass':False,
            'material_pass':None,'composite_pass':None,'composite_required':scene['expected_composite'],
            'target_object':'unknown','semantic_object_completeness':None,'support_collision_truth':None,
            'interpretation':'Reconstruction failed: no edit/structure measurement exists; required gates fail, raw measurements remain null.'}


def task(scene,folder):
    from PIL import Image,ImageOps
    folder.mkdir(parents=True,exist_ok=True)
    with Image.open(scene['image_path']) as original:
        im=ImageOps.exif_transpose(original).convert('RGB');im.thumbnail((512,512));im.save(folder/'reference.png')
    return {'id':scene['scene_id'],'image':str(folder/'reference.png'),'width':im.width,'height':im.height}

def run_scene(method,run_id,candidate,scene,source,parent=None,meta=None):
    from inner_loop import run
    from evaluate import score
    folder=ROOT/'results'/run_id/method/candidate/scene['split']/scene['scene_id']
    if (folder/'record.json').exists():return read(folder/'record.json')
    check_service_pause()
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
    checks=functional(folder,scene) if metrics['valid'] else failed_functional(scene)
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
    row['task_utility_v2']=metrics['overall'] if metrics['valid'] else 0.0
    write_json(folder/'record.json',row)
    if (folder/'build.py').exists() and not (folder/'scene.py').exists():(folder/'scene.py').symlink_to('build.py')
    write_json(ROOT/'ledger.json',current())
    check_service_pause()
    print(json.dumps({k:row[k] for k in ['method','run_id','scene_id','candidate_id','split','status','metrics']},ensure_ascii=False),flush=True)
    return row

def summarize(rows):
    valid=[r for r in rows if r['metrics']['valid']]
    qualified=[r for r in rows if eligible_scene(r)]
    return {'all_scheduled':len(rows),'completed':len(valid),'success_rate':len(valid)/len(rows) if rows else None,'functional_passes':len(qualified),'eligible':bool(rows) and len(qualified)==len(rows),'conditional_quality':sum(r['metrics']['overall'] for r in valid)/len(valid) if valid else None,'endpoint_quality':sum(r['metrics']['overall'] for r in valid)/len(rows) if rows else None,'measured_metrics_missing':len(rows)-len(valid)}

def eligible_scene(row):
    if not row['metrics']['valid'] or row['status']!='complete':return False
    checks=row['functional']['checks']
    return bool(checks) and all(not c['required'] or (c['applicable'] is True and c['measured_pass'] is True and c['gate_pass'] is True) for c in checks.values())

def better(child,base,best):
    # Absolute eligibility first. H0 remains a fallback, never a lower functional threshold.
    return child['eligible'] and (not best['eligible'] or child['endpoint_quality']>best['endpoint_quality']+config()['pilot']['quality_tolerance'])

def dev_packet(rows):
    packet=[];images=[]
    for row in rows:
        folder=Path(row['folder']);entry={k:row[k] for k in ['scene_id','status','metrics','functional','target_object']}
        entry['program']=(folder/'build.py').read_text() if (folder/'build.py').exists() else 'missing'
        entry['trajectory']=compact_trajectory((folder/'trajectory.jsonl').read_text()) if (folder/'trajectory.jsonl').exists() else []
        entry['structure']=compact_structure(read(folder/'functional/scene_structure.json'))
        all_objects=read(folder/'functional/scene_structure.json',{'objects':[]})['objects']
        entry['all_object_ids']=[o['name'] for o in all_objects]
        meshes=[o for o in all_objects if o['type']=='MESH']
        projected=sorted(meshes,key=lambda o: (o['world_geometry_aabb_approx'] or {'diagonal_scene_units':0})['diagonal_scene_units'],reverse=True)[:128]
        entry['objects']=[{key:o[key] for key in ['name','type','parent','finite_nonempty_mesh','excluded_as_structural']} | {'world_geometry_aabb_approx':{'diagonal_scene_units':o['world_geometry_aabb_approx']['diagonal_scene_units']} if o['world_geometry_aabb_approx'] else None} for o in projected]
        entry['object_projection']='All real IDs retained. Detailed projected objects capped128: named groups, camera/lights, named geometry, then remaining names. Collector display order is not attribution; full raw structure remains saved.'
        entry['regression']=read(folder/'functional/mechanical.json')
        from diagnostics import failure_evidence
        entry['failure_evidence']=failure_evidence(row)
        entry['objects']=projected_objects(all_objects)
        for f in [folder/'reference.png',folder/'final.png']:
            if f.exists():images.append(str(f))
        entry['attached_images']=images[-(2 if (folder/'final.png').exists() else 1):]
        packet.append(entry)
    return packet,images


def meta_execute(source, function, *args):
    """Generated strategy is an external boundary; preserve failures rather than repair it."""
    validate_source(source.read_text(),'meta.py')
    args=json.loads(json.dumps(args))  # Strategies cannot mutate runner budgets or measured records.
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('M decision exceeded 10 seconds')))
    signal.alarm(10)
    try:
        module=load_module(source)
        return module.plan_probes(*args) if function=='plan_probes' else module.plan_patch(*args)
    finally:signal.alarm(0)


def candidate_type(before, after):
    h=any(before[n]!=after[n] for n in ['policy.py','system.txt'])
    m=before['meta.py']!=after['meta.py']
    if not (h or m):raise ValueError('No H or M source change')
    return 'H+M' if h and m else 'H-only' if h else 'M-only'


def context_for(rows,archive,k,phase,risks):
    from regression import MENU
    development,images=dev_packet(rows)
    projection=bound_payload({'development':development},limit=300000)
    return {'development':development,'visual_findings':[],'archive':[{key:value for key,value in a.items() if key!='post_patch_feedback'} | {'prior_post_patch_M_decision':a['post_patch_feedback']['M_decision'] if a.get('post_patch_feedback') and 'M_decision' in a['post_patch_feedback'] else None} for a in archive],'iteration':k,'phase':phase,'evidence_projection':projection,
            'remaining_probe_budget':2 if phase=='before_patch' else 0,'already_executed_probe_count':0 if phase=='before_patch' else 2,
            'available_probe_menu':['camera_focal','object_scale','isolate'],
            'remaining_regression_budget':3,
            'available_regression_menu':{name:{'available':any(r['status']=='complete' for r in rows),'cost':1,
                'scene_applicability':{r['scene_id']:r['functional'].get('geometry',{}).get(name,{}).get('applicable') for r in rows},
                'condition':'Declared relations for support/parts, real eligible objects for edits; unavailable measured facts stay null'} for name in MENU},
            'modification_risks':risks},images


def execute_plan(context,plan,rows,dest):
    from evaluate import score
    if len(plan['probes'])>context['remaining_probe_budget']:raise ValueError('M exceeded probe budget')
    if len(plan['regressions'])>context['remaining_regression_budget']:raise ValueError('M exceeded regression budget')
    observations={'probes':[],'regression':[]}
    lookup={r['scene_id']:r for r in rows}
    for i,request in enumerate(plan['probes']):
        row=lookup[request['scene_id']];folder=Path(row['folder'])
        objects=read(folder/'functional/scene_structure.json')['objects']
        if request['probe'] not in context['available_probe_menu']:raise ValueError('Probe outside menu')
        if request['probe']!='camera_focal' and request['object_id'] not in [o['name'] for o in objects]:raise ValueError('Unknown requested object ID')
        output=dest/'probes'/str(i)
        result=inspect(folder,'probe',request['probe'],output,object_id=request['object_id'])
        png=output/f"probe_{request['probe']}.png"
        metrics=None;delta=None
        if result['status']=='completed' and png.exists():
            shutil.copy2(output/'probe_scene.blend',output/'scene.blend');shutil.copy2(png,output/'final.png')
            metrics=score(folder/'reference.png',output,config())
            if metrics['valid']:delta=metrics['overall']-row['metrics']['overall']
        observations['probes'].append({'request':request,'execution':result,'visual_metrics':metrics,'quality_delta':delta,'interpretation':'Controlled sensitivity, not unique causal attribution'})
        context['remaining_probe_budget']-=1;context['already_executed_probe_count']+=1
    for i,request in enumerate(plan['regressions']):
        if request['test'] not in context['available_regression_menu']:raise ValueError('Regression outside menu')
        result=inspect(Path(lookup[request['scene_id']]['folder']),'regression',output=dest/'regression'/str(i),test=request['test'])
        observations['regression'].append({'request':request,'result':result})
        context['remaining_regression_budget']-=1
    write_json(dest/'observations.json',observations)
    return observations


def propose(method,run_id,k,parent_source,meta_source,parent_dev,archive,total_candidates=2):
    cid=f'C{k}';folder=ROOT/'candidates'/run_id/method/cid;result_path=folder/'proposal_result.json'
    if result_path.exists():return folder,read(result_path)
    folder.mkdir(parents=True,exist_ok=True)
    write_json(ROOT/'state.json',{'phase':'planning_candidate','method':method,'run_id':run_id,'candidate_id':cid,'M_source':str(meta_source)})
    sources={n:(parent_source/n).read_text() for n in ['policy.py','system.txt']}
    sources['meta.py']=meta_source.read_text()
    for n,s in sources.items():(folder/n).write_text(s)
    try:
        context,images=context_for(parent_dev,archive,k,'before_patch',['camera','material','parts'])
        from diagnostics import localize
        context['visual_findings']=localize(context['development'],folder/'localization')
        before=json.loads(json.dumps(context))
        plan=meta_execute(meta_source,'plan_probes',context)
        write_json(folder/'stage1.json',{'M_source':str(meta_source),'context':before,'decision':plan})
        write_json(ROOT/'state.json',{'phase':'executing_diagnostics','method':method,'run_id':run_id,'candidate_id':cid})
        observations=execute_plan(context,plan,parent_dev,folder)
        decision=meta_execute(meta_source,'plan_patch',context,observations)
        write_json(folder/'stage2.json',{'M_source':str(meta_source),'context_after_execution':context,'observations':observations,'decision':decision})
        write_json(ROOT/'state.json',{'phase':'generating_candidate','method':method,'run_id':run_id,'candidate_id':cid})
        api={str(p.relative_to(ROOT/'backend/sceneact')):p.read_text() for p in (ROOT/'backend/sceneact').glob('*.py')}
        images += [str(p) for p in sorted((folder/'probes').glob('*/probe_*.png'))]
        payload={'attached_image_order':images,'sources':sources,'sceneact_api':api,'context':before,'stage1':plan,'actual_observations':observations,'stage2_M_decision':decision}
        prompt=COMMON+'\n'+json.dumps(payload,ensure_ascii=False)
        if len(prompt.encode())>600000:raise ValueError('Proposal payload exceeds frozen 600000 byte cap')
        schema={'type':'object','properties':{'files':{'type':'array','items':{'type':'object','properties':{'path':{'type':'string','enum':['policy.py','system.txt','meta.py']},'content':{'type':'string'}},'required':['path','content'],'additionalProperties':False}},'rationale':{'type':'string'},'scope':{'type':'string'},'evidence_alignment':{'type':'string'}},'required':['files','rationale','scope','evidence_alignment'],'additionalProperties':False}
        answer,session=call(prompt,config()['proposer'],folder/'proposal_call',images,role='meta_proposer',schema=schema)
        result=json.loads(answer)
        changes={item['path']:item['content'] for item in result['files']}
        for n,s in changes.items():
            if n not in sources:raise ValueError('File outside candidate scope')
            if any(tag in s for tag in ['/srv/','/home/','commons_']):raise ValueError('Hardcoded dataset path or task ID in shared candidate file')
            if n.endswith('.py'):validate_source(s,n)
        after={**sources,**changes};kind=candidate_type(sources,after)
        for n,s in after.items():(folder/n).write_text(s)
        diff=''.join(''.join(difflib.unified_diff(sources[n].splitlines(True),after[n].splitlines(True),fromfile='parent/'+n,tofile=cid+'/'+n)) for n in sources)
        (folder/'changes.diff').write_text(diff)
        # Descendant executable contract is tested without letting it change budgets/evaluator.
        meta_execute(folder/'meta.py','plan_probes',before)
        meta_execute(folder/'meta.py','plan_patch',context,observations)
        result.update(status='proposed',candidate_type=kind,H_changed=kind!='M-only',M_changed=kind!='H-only',parent_source=str(parent_source),used_M=str(meta_source),M_contract_executed=True,M_descendant_executed=kind!='H-only',ledger_after=current())
    except (ValueError,SyntaxError,RuntimeError,OSError,subprocess.TimeoutExpired,TimeoutError,KeyError,TypeError,AttributeError) as error:
        import traceback
        result={'status':'proposal_failed','error':str(error),'traceback':traceback.format_exc(),'H_changed':False,'M_changed':False,'used_M':str(meta_source),'parent_source':str(parent_source)}
    write_json(result_path,result);write_json(ROOT/'ledger.json',current());return folder,result


def main():
    if not (ROOT/'protocol_frozen.json').exists():raise RuntimeError('Mechanism acceptance and smoke must precede freeze')
    initialize(ROOT)
    scenes=read(ROOT/'manifest.json');dev=[s for s in scenes if s['split']=='development'];selection=[s for s in scenes if s['split']=='selection'];test=[s for s in scenes if s['split']=='test']
    baseline=ROOT/'backend/harnesses/baseline';archive=read(ROOT/'archive.json',[]);states={};method='scene_rsi_v2_1'
    for rid in ['r1','r2']:
        bdev=[run_scene('fixed_h0',rid,'H0',s,baseline) for s in dev]
        bsel=[run_scene('fixed_h0',rid,'H0',s,baseline) for s in selection]
        states[rid]={'source':baseline,'meta':ROOT/'initial_meta/scene_rsi_v2_1/meta.py','dev':bdev,'sel':bsel,'base':summarize(bsel),'best':summarize(bsel),'selected':'H0','selected_source':baseline}
    for k in [1,2]:
        for rid in ['r1','r2']:
            state=states[rid];prior=[a for a in archive if a['run_id']==rid and int(a['candidate_id'][1:])<k]
            source,result=propose(method,rid,k,state['source'],state['meta'],state['dev'],prior)
            if result['status']=='proposed':
                if result['H_changed']:
                    drows=[run_scene(method,rid,f'C{k}',s,source,str(state['source']),str(source/'meta.py')) for s in dev]
                    srows=[run_scene(method,rid,f'C{k}',s,source,str(state['source']),str(source/'meta.py')) for s in selection]
                else:
                    drows,srows=state['dev'],state['sel']
                    for row in drows+srows:
                        dest=ROOT/'results'/rid/method/f'C{k}'/row['split']/row['scene_id'];dest.mkdir(parents=True,exist_ok=True)
                        alias={**row,'method':method,'candidate_id':f'C{k}','folder':str(dest),'alias_of':row['folder'],'H_unchanged':True,'M_version':str(source/'meta.py'),'additional_cli_sessions':0,'additional_renders':0,'reused_generation_seconds':row['seconds'],'seconds':0}
                        write_json(dest/'record.json',alias)
                if result['H_changed'] and not (source/'post_patch_feedback.json').exists():
                    try:
                        diff=(source/'changes.diff').read_text().lower()
                        risks=['geometry'] if any(word in diff for word in ['scale','part','support','mesh','primitive']) else ['camera','material','parts']
                        post,unused_images=context_for(drows,prior,k,'after_patch',risks)
                        post['historical_visual_findings']=read(source/'localization/findings.json',[])
                        post['visual_findings']=[]
                        post['localization_status']='not_relocalized_after_patch'
                        post['diff_risk_basis']='Approximate keyword screen only; not precise module attribution'
                        post['already_executed_probe_count']=read(source/'stage2.json')['context_after_execution']['already_executed_probe_count']
                        post_plan=meta_execute(source/'meta.py','plan_probes',post)
                        post_observations=execute_plan(post,post_plan,drows,source/'post_patch_regression')
                        post_decision=meta_execute(source/'meta.py','plan_patch',post,post_observations)
                        write_json(source/'post_patch_feedback.json',{'actual_diff_risks':risks,'M_source':str(source/'meta.py'),'test_plan':post_plan,'observations':post_observations,'M_decision':post_decision})
                    except (ValueError,KeyError,TypeError,AttributeError,RuntimeError,TimeoutError) as error:
                        write_json(source/'post_patch_feedback.json',{'status':'M_runtime_failed','error':str(error),'M_source':str(source/'meta.py'),'next_M':'retain_previous_executable_M'})
                summary=summarize(srows);accepted=result['H_changed'] and better(summary,state['base'],state['best'])
                entry={'method':method,'run_id':rid,'candidate_id':f'C{k}','parent_id':str(state['source']),'status':'evaluated','candidate_type':result['candidate_type'],'development':summarize(drows),'selection':summary,'accepted':accepted,'H_changed':result['H_changed'],'M_changed':result['M_changed'],'M_used':str(state['meta']),'post_patch_feedback':read(source/'post_patch_feedback.json'),'ledger_after':current()}
                if accepted:state.update(best=summary,selected=f'C{k}',selected_source=source)
                # Valid descendants are explored independently of H retention; K2 executes K1 M.
                feedback=read(source/'post_patch_feedback.json',{})
                next_meta=state['meta'] if feedback.get('status')=='M_runtime_failed' else source/'meta.py'
                state.update(source=source,meta=next_meta,dev=drows,sel=srows)
            else:entry={'method':method,'run_id':rid,'candidate_id':f'C{k}','status':result['status'],'error':result['error'],'accepted':False,'ledger_after':current()}
            previous=next((a for a in archive if a['run_id']==rid and a['candidate_id']==f'C{k}'),None)
            if previous and previous['status']==entry['status']:entry['ledger_after']=previous['ledger_after']
            archive=[a for a in archive if not(a['run_id']==rid and a['candidate_id']==f'C{k}')]+[entry];write_json(ROOT/'archive.json',archive)
    choices=[{'method':method,'run_id':rid,'candidate_id':s['selected'],'source':str(s['selected_source']),'selection':s['best']} for rid,s in states.items()]
    choices += [{'method':'fixed_h0','run_id':rid,'candidate_id':'H0','source':str(baseline)} for rid in states]
    frozen=read(ROOT/'selection_freeze.json')
    if frozen and frozen['choices']!=choices:raise RuntimeError('Selection freeze differs on resume')
    if not frozen:write_json(ROOT/'selection_freeze.json',{'choices':choices,'time':time.time(),'test_feedback_before_freeze':False})
    for rid in states:
        own=next(c for c in choices if c['method']==method and c['run_id']==rid)
        for scene in test:
            base=run_scene('fixed_h0',rid,'H0',scene,baseline)
            if own['candidate_id']=='H0':
                dest=ROOT/'results'/rid/method/'H0'/'test'/scene['scene_id'];dest.mkdir(parents=True,exist_ok=True)
                alias={**base,'method':method,'folder':str(dest),'alias_of':base['folder'],'selected':True};write_json(dest/'record.json',alias)
            else:run_scene(method,rid,own['candidate_id'],scene,Path(own['source']))
    write_json(ROOT/'state.json',{'phase':'main_complete','time':time.time(),'ledger':current()})


if __name__=='__main__':raise SystemExit('V2.2 performs no RSI evolution; use experiment.py or diagnosis_runner.py')
