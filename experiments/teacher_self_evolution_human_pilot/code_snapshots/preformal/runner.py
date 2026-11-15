"""One teacher self-modification, twelve fresh reconstructions, human review only."""
import argparse
import ast
import difflib
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'backend'))
from data import write_json
from budget import current
from codex_wrapper import call, check_service_pause
from runtime import Runtime


def read(path):
    return json.loads(Path(path).read_text())


def schema(fields):
    return {'type':'object','properties':{key:{'type':'string'} for key in fields},
            'required':list(fields),'additionalProperties':False}


HINT_SCHEMA = schema(['draft','hint','observations','correction_record','change_reason'])
STUDENT_SCHEMA = schema(['decision','reason','observation','code'])
MODIFY_SCHEMA = schema(['decision','teacher_py','evidence','expected_effect','change_type'])
TEACHER_FUNCTIONS = ['initial_hint','update_hint','compress_hint','self_modify']
TERMINAL = {'completed','failed','timeout','invalid','not_run_no_teacher'}


def validate_teacher(source):
    tree = ast.parse(source)
    imports = {'json','re','math','textwrap','statistics','copy'}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import,ast.ImportFrom)):
            names = [n.name for n in node.names] if isinstance(node,ast.Import) else [node.module]
            if any(n not in imports for n in names):
                raise ValueError('Teacher import outside evidence-only contract')
        if isinstance(node,ast.Name) and node.id in {'open','exec','eval','compile','__import__','globals','locals','getattr','setattr','delattr','input','breakpoint'}:
            raise ValueError('Teacher external access is forbidden: '+node.id)
        if isinstance(node,ast.Attribute) and node.attr.startswith('__'):
            raise ValueError('Teacher private introspection is forbidden')
    if re.search(r'\b(?:D0[12]|E0[12])\b|commons_\d+|/srv/|/home/', source):
        raise ValueError('Teacher hardcodes a task ID or server path')
    namespace = {}
    exec(compile(tree,'teacher_candidate','exec'), namespace)
    fixture = {'public_task':'Reconstruct a simple room','hint_max_chars':1200,
               'previous':None,'reference_attachment':1,'result_attachment':None}
    for name in TEACHER_FUNCTIONS:
        if not callable(namespace[name]):
            raise ValueError('Missing teacher function: '+name)
    # Only syntax and common entry contract. Actual evidence shapes are tested preflight.
    return namespace


def load_teacher(version):
    return validate_teacher((ROOT/'teachers'/version/'teacher.py').read_text())


def invoke(prompt, settings, base, images, role, response_schema, timeout=None, retries=1, deadline=None):
    """Reuse saved attempts; a transient failed call may get one bounded retry."""
    for attempt in range(1,retries+2):
        folder = base/f'attempt_{attempt}'
        session_path = folder/'session.json'
        if session_path.exists():
            session = read(session_path)
            if session['status']=='completed':
                return json.loads((folder/'response.txt').read_text()), session
            if session['status']=='running':
                raise RuntimeError('Unfinished CLI needs process audit before resume: '+str(folder))
        else:
            available=min(timeout or settings['timeout'],deadline-time.monotonic()) if deadline else timeout
            if available is not None and available<=0:
                raise RuntimeError('total_budget_exceeded before CLI submission')
            try:
                text, session = call(prompt,settings,folder,images,role=role,
                                     timeout=available,schema=response_schema)
                return json.loads(text), session
            except RuntimeError:
                if not session_path.exists():
                    raise
                session = read(session_path)
                if session['status']=='completed':
                    raise
        # Known route/transport failures halt the whole run instead of burning tasks.
        check_service_pause()
        raw = (folder/'stderr.log').read_text()+(folder/'events.jsonl').read_text()
        transient = any(x in raw.lower() for x in ['service unavailable','rate limit','502','503','connection reset','overloaded'])
        if not transient or attempt==retries+1:
            raise RuntimeError('CLI terminal failure: '+str(folder))
    raise AssertionError('Unreachable attempt loop')


def hint_error(hint, limit):
    if not hint.strip():return 'empty_hint'
    if len(hint)>limit:return 'over_length'
    if re.search(r'```|https?://|/srv/|/home/|\bimport\s+\w+|\bdef\s+\w+|bpy\.|sceneact\.|[A-Za-z0-9+/]{160,}',hint):
        return 'code_path_or_encoded_payload'
    return None


def bounded_trace(folder, config):
    """Same deterministic evidence window for every teacher; no other task lookup."""
    steps=[]
    for path in sorted((folder/'steps').glob('*/result.json')):
        result=read(path)
        steps.append({'step':result['step'],'ok':result['ok'],'failure_type':result['failure_type'],
                      'error':result['error'],'seconds':result['seconds'],
                      'stderr_tail':result['stderr'][-2000:]})
    selected = read(folder/'selected.json') if (folder/'selected.json').exists() else None
    code = (folder/'build.py').read_text() if (folder/'build.py').exists() else ''
    if not code:
        codes=sorted((folder/'steps').glob('*/build.py'))
        if codes:code=codes[-1].read_text()
    evidence={'steps':steps,'selected':selected,'code_excerpt':code[:config['teacher']['code_excerpt_chars']],
              'code_excerpt_truncated':len(code)>config['teacher']['code_excerpt_chars'],
              'delivery_status':read(folder/'status.json')['status']}
    text=json.dumps(evidence,ensure_ascii=False)
    return {'bounded_trace':text[:config['teacher']['trace_max_chars']],
            'trace_truncated':len(text)>config['teacher']['trace_max_chars']}


def guide(item, config, source):
    folder=ROOT/'tasks'/item['task_id'];folder.mkdir(parents=True,exist_ok=True)
    saved=folder/'guidance.json'
    if saved.exists():return read(saved)
    teacher=load_teacher(item['teacher'])
    context={'public_task':(ROOT/'public_task.txt').read_text(),
             'hint_max_chars':config['teacher']['hint_max_chars'],
             'reference_attachment':1,'result_attachment':None,'previous':None}
    images=[source]
    if item['round']==2:
        previous=ROOT/'tasks'/f"{item['scene']}_{item['teacher']}_R1"
        prev_hint=read(previous/'guidance.json')
        prev_state=read(previous/'status.json')
        context['previous']={'hint':prev_hint['hint'],'correction_record':prev_hint['correction_record'],
                             **bounded_trace(previous,config)}
        if prev_state['status']=='completed':
            images.append(previous/'final.png');context['result_attachment']=2
        context['missing_result_reason']=prev_state['failure_reason']
    write_json(folder/'teacher_context.json',context)
    function='initial_hint' if item['round']==1 else 'update_hint'
    started=time.time()
    result, session=invoke(teacher[function](context),config['proposer'],folder/'teacher_calls'/'guidance',
                          images,'teacher_hint',HINT_SCHEMA,retries=1)
    write_json(folder/'guidance_draft.json',result)
    error=hint_error(result['hint'],config['teacher']['hint_max_chars'])
    used=len(list((folder/'teacher_calls').glob('**/request.json')))
    if error and used<config['teacher']['max_calls_per_hint']:
        result,session=invoke(teacher['compress_hint']({'previous_response':result,'constraint_error':error,
                                   'hint_max_chars':config['teacher']['hint_max_chars']}),
                              config['proposer'],folder/'teacher_calls'/'compression',[],
                              'teacher_compression',HINT_SCHEMA,retries=0)
        error=hint_error(result['hint'],config['teacher']['hint_max_chars'])
    if error:
        write_json(folder/'invalid_guidance.json',{'error':error,'response':result})
        raise ValueError('Teacher guidance invalid: '+error)
    result.update(teacher=item['teacher'],function=function,seconds=time.time()-started,
                  characters=len(result['hint']),previous_student_visible_only_to_teacher=item['round']==2)
    write_json(saved,result)
    return result


def student(item, config, source, guidance):
    folder=ROOT/'tasks'/item['task_id']
    state_path=folder/'status.json'
    if state_path.exists() and read(state_path)['status'] in TERMINAL:return
    task={'image':str(source),'instruction':(ROOT/'public_task.txt').read_text()}
    with Image.open(source) as image:
        width,height=image.size
    scale=config['long_edge']/max(width,height)
    task.update(width=round(width*scale),height=round(height*scale))
    write_json(folder/'student_input.json',{'public_task':task['instruction'],'hint':guidance['hint'],
               'reference_attachment':str(source),'reference_original_dimensions':[width,height],
               'render_dimensions':[task['width'],task['height']],
               'student_version':config['student_version'],'previous_reconstruction_artifacts':[],
               'fresh_workspace':True,'remote_sampling_seed':None})
    if state_path.exists() and read(state_path)['student_started']:
        raise RuntimeError('Interrupted student needs explicit stage recovery; refusing to resample: '+item['task_id'])
    started=time.time()
    write_json(state_path,{**item,'status':'running','student_started':True,'started':started,
                          'failure_reason':None,'phase':'student_first_call'})
    runtime=Runtime(task,config,folder)
    fixed=(ROOT/'student_prompt.txt').read_text()+'\n'+(ROOT/'sceneact_api.txt').read_text()
    common=fixed+'\nPUBLIC TASK:\n'+task['instruction']+'\nTEACHER LANGUAGE HINT:\n'+guidance['hint']
    selected=None;selection_reason=None;observed_steps=[];failure=None;last_result=None
    # Each main call is fresh, with explicit within-task state on call two only.
    for number in (1,2):
        if number==2 and runtime.remaining()['model_calls']<=0:
            failure='total_budget_exceeded_before_internal_review';break
        images=[source]
        prompt=common+'\nReturn JSON string fields decision, reason, observation, code. '
        if number==1:
            prompt+='decision=build; code is the complete new SceneAct program. No earlier scene exists.'
        else:
            prompt+='This is the one allowed internal review of YOUR CURRENT reconstruction only. '
            if last_result['ok']:
                images.append(Path(last_result['image']));observed_steps.append(last_result['step'])
                prompt+='Attachment 2 is the actual current render. Inspect it against reference attachment 1. '
                prompt+='Choose keep (empty code) or revise (complete replacement program). Explain observation and reason. '
            else:
                prompt+='No valid current render exists; diagnose the actual error only. Choose revise with a complete repair or stop. '
            prompt+='\nCURRENT PROGRAM:\n'+(folder/'steps'/'001'/'build.py').read_text()
            prompt+='\nCURRENT EXECUTION:\n'+json.dumps({k:last_result[k] for k in ['ok','failure_type','error','stderr']},ensure_ascii=False)[-14000:]
        runtime.calls+=1;runtime.save_usage()
        timeout=min(config['model']['timeout'],max(1,runtime.deadline-time.monotonic()-600))
        try:
            response,session=invoke(prompt,config['model'],folder/'student_calls'/f'{number:03d}',
                                    images,'H',STUDENT_SCHEMA,timeout=timeout,deadline=runtime.deadline-600)
        except (RuntimeError,json.JSONDecodeError) as error:
            failure=str(error);break
        write_json(folder/f'student_decision_{number}.json',response)
        selection_reason=response['reason']
        if number==2 and response['decision'] in {'keep','stop'}:
            break
        if response['decision'] not in {'build','revise'} or not response['code'].strip():
            failure='invalid_generated_response';break
        last_result=runtime.execute(response['code'])
        if last_result['ok']:
            selected=last_result['step']
            if not (folder/'first_checkpoint.json').exists():
                write_json(folder/'first_checkpoint.json',{'step':selected,'path':f'steps/{selected:03d}',
                                                          'immutable':True})
        else:failure=last_result['failure_type']
    delivered=selected is not None
    restored=delivered and runtime.executions>selected
    result={**item,'status':'completed' if delivered else 'failed','student_started':True,
            'started':started,'finished':time.time(),'seconds':time.time()-started,
            'failure_reason':None if delivered else failure,'internal_failure':failure,
            'build_attempts':runtime.executions,'main_student_calls':runtime.calls,
            'selected_step':selected,'selection_reason':selection_reason,
            'restored_checkpoint':restored,'render_attached_for_student_review':observed_steps,
            'final_seen_by_student':selected in observed_steps if delivered else False,
            'quality_verdict':None,'blend_opened_for_render':delivered,'technical_success_only':True}
    write_json(state_path,result)
    print(json.dumps({'task':item['task_id'],'status':result['status'],'selected':selected},ensure_ascii=False),flush=True)


def modify_teacher(config, plan):
    folder=ROOT/'self_modification';folder.mkdir(exist_ok=True)
    if (folder/'status.json').exists():return read(folder/'status.json')['status']=='executable_candidate'
    teacher=load_teacher('M0');source=(ROOT/'teachers/M0/teacher.py').read_text()
    records=[];images=[]
    manifest={s['id']:s for s in read(ROOT/'manifest.json')}
    for item in plan[:4]:
        f=ROOT/'tasks'/item['task_id']
        images.append(ROOT/manifest[item['scene']]['image_path'])
        state=read(f/'status.json')
        record={'public_task':(ROOT/'public_task.txt').read_text(),'round':item['round'],
                'reference_attachment':len(images),'result_attachment':None,
                'guidance':read(f/'guidance.json'),**bounded_trace(f,config)}
        if state['status']=='completed':images.append(f/'final.png');record['result_attachment']=len(images)
        records.append(record)
    context={'own_source':source,'development_records':records,
             'fixed_student_contract':(ROOT/'student_prompt.txt').read_text(),
             'data_boundary':'Only these two development sources; no comparison inputs or results.',
             'functions':TEACHER_FUNCTIONS}
    write_json(folder/'context.json',context)
    prompt=teacher['self_modify'](context)
    errors=[]
    for attempt in (1,2):
        response,session=invoke(prompt,config['proposer'],folder/f'proposal_{attempt}',images,
                                'teacher_self_modify' if attempt==1 else 'teacher_technical_repair',
                                MODIFY_SCHEMA,retries=0)
        write_json(folder/f'proposal_{attempt}.json',response)
        if response['decision']=='unchanged' or response['teacher_py']==source:
            write_json(folder/'status.json',{'status':'unchanged','attempt':attempt,'response':response});return False
        try:
            module=validate_teacher(response['teacher_py'])
            # Exercise every interface with the same saved admissible records, no model calls.
            contexts=[read(ROOT/'tasks'/p['task_id']/'teacher_context.json') for p in plan[:4]]
            checks=[('initial_hint',contexts[0]),('update_hint',contexts[2]),
                    ('compress_hint',{'previous_response':records[0]['guidance'],'constraint_error':'over_length','hint_max_chars':1200}),
                    ('self_modify',context)]
            for name,c in checks:
                output=module[name](c)
                if not isinstance(output,str) or not output.strip():raise ValueError(name+' returned no prompt')
        except (SyntaxError,ValueError,KeyError,NameError,TypeError,AttributeError) as error:
            errors.append(repr(error));write_json(folder/f'validation_error_{attempt}.json',{'error':repr(error)})
            prompt='Technical repair ONLY of the prior teacher proposal. Preserve its research strategy; correct this interface error: '+repr(error)+'\nPrevious proposal:\n'+json.dumps(response,ensure_ascii=False)+'\nRequired context/interface:\n'+json.dumps(context,ensure_ascii=False)
            continue
        target=ROOT/'teachers/M1';target.mkdir()
        (target/'teacher.py').write_text(response['teacher_py'])
        (folder/'frozen_M1.py').write_text(response['teacher_py'])
        difference=''.join(difflib.unified_diff(source.splitlines(True),response['teacher_py'].splitlines(True),fromfile='M0/teacher.py',tofile='M1/teacher.py'))
        (folder/'M0_to_M1.diff').write_text(difference)
        write_json(target/'provenance.json',{'creator':'M0.self_modify via gpt-6-astra/medium',
                   'proposal_attempt':attempt,'change_type':response['change_type'],'evidence':response['evidence'],
                   'expected_effect':response['expected_effect'],'quality_status':'awaiting_human_judgment'})
        write_json(folder/'status.json',{'status':'executable_candidate','attempt':attempt,'errors':errors,
                    'quality_accepted':None,'comparison_used':False,'automatic_quality_evaluation':False})
        write_json(ROOT/'teacher_freeze.json',{'M0':'teachers/M0/teacher.py','M1':'teachers/M1/teacher.py',
                                              'time':time.time(),'development_tasks':4,'no_further_modification':True})
        return True
    write_json(folder/'status.json',{'status':'invalid','errors':errors});return False


def resume():
    if not (ROOT/'FROZEN.json').exists():raise RuntimeError('Images and protocol are not yet frozen')
    config=read(ROOT/'config.json');plan=read(ROOT/'plan.json')
    os.sched_setaffinity(0,set(config['resources']['cpu_affinity']))
    lock=(ROOT/'experiment.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for relative in read(ROOT/'FROZEN.json')['fixed_files']:
        if (ROOT/relative).read_bytes()!=(ROOT/'code_snapshots/preformal'/relative).read_bytes():
            raise RuntimeError('Frozen code/config changed: '+relative)
    if (ROOT/'self_modification/frozen_M1.py').exists():
        assert (ROOT/'teachers/M1/teacher.py').read_text()==(ROOT/'self_modification/frozen_M1.py').read_text()
    manifest={s['id']:s for s in read(ROOT/'manifest.json')}
    for i,item in enumerate(plan):
        check_service_pause()
        if i==4 and not modify_teacher(config,plan):
            for pending in plan[4:]:
                write_json(ROOT/'tasks'/pending['task_id']/'status.json',{**pending,'status':'not_run_no_teacher',
                    'student_started':False,'failure_reason':'No executable changed M1; no comparison was launched'})
            break
        f=ROOT/'tasks'/item['task_id'];state=f/'status.json'
        if state.exists() and read(state)['status'] in TERMINAL:continue
        source=ROOT/manifest[item['scene']]['image_path']
        guidance=guide(item,config,source)
        student(item,config,source,guidance)
        write_json(ROOT/'state.json',{'last_task':item['task_id'],'cost':current(),'phase':'running'})
        from report import generate
        generate()
    write_json(ROOT/'state.json',{'phase':'all_scheduled_terminal','cost':current(),
                                 'M1_quality_status':'awaiting_human_judgment','M2':False})
    if (ROOT/'teacher_freeze.json').exists():
        s=read(ROOT/'self_modification/status.json')
        s['comparison_used']=any(read(f)['student_started'] for f in (ROOT/'tasks').glob('E*_M1_*/status.json'))
        write_json(ROOT/'self_modification/status.json',s)
    from report import generate
    generate()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['resume','report'])
    args=parser.parse_args()
    if args.command=='resume':resume()
    else:
        from report import generate
        generate()
