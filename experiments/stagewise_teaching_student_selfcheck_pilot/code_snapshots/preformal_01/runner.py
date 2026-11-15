"""Two persistent scenes: online teaching, then frozen student self-checking."""
import argparse
import ast
import difflib
import fcntl
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
from budget import current, guard, guard_partition
from codex_wrapper import call, check_service_pause
from processes import cpu_environment, run_measured
import prompts

CONFIG = json.loads((ROOT/'config.json').read_text())
ACTIVE = None


class RunStopped(RuntimeError):
    pass


def read(path):
    return json.loads(Path(path).read_text())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def event(kind, **fields):
    record = {'time':time.time(),'event':kind,**fields}
    with (ROOT/'events.jsonl').open('a') as out:
        out.write(json.dumps(record,ensure_ascii=False)+'\n')
    print(json.dumps(record,ensure_ascii=False),flush=True)


def remaining():
    if ACTIVE is None:
        return 5400
    return CONFIG['stage_limits']['task_active_seconds']-ACTIVE['base']-(time.monotonic()-ACTIVE['started'])


def english_output(value):
    if re.search(r'[\u4e00-\u9fff]',json.dumps(value,ensure_ascii=False)):
        raise RunStopped('Output language violation: raw response retained; no unbudgeted translation retry')


def invoke(prompt, folder, images, role, schema, partition, model=None):
    """Saved successful responses are reused; failed calls are never resampled silently."""
    folder = Path(folder)
    check_service_pause()
    if partition=='test' and (not role.startswith('student') or model is not None):
        raise ValueError('Protocol error: test calls must use the fixed student, no teacher/Astra')
    settings = CONFIG['model'] if role.startswith('student') else CONFIG['proposer']
    if model is not None:
        settings = model
    for n in (1,2):
        attempt = folder/f'attempt_{n}'
        session_path = attempt/'session.json'
        if session_path.exists():
            session = read(session_path)
            if session['status']=='completed':
                if session['tool_calls']:
                    raise RunStopped('Cached CLI response includes forbidden tool calls')
                response = json.loads((attempt/'response.txt').read_text())
                english_output(response)
                return response
            if session['status']=='running':
                raise RunStopped('Interrupted CLI requires process audit: '+rel(attempt))
        else:
            check_service_pause()
            guard_partition(partition)
            available = min(settings['timeout'],remaining()-90)
            if available<=0:
                raise RunStopped('total_budget_exceeded before CLI')
            event('cli_submitted',role=role,partition=partition,path=rel(attempt),images=[rel(p) for p in images])
            try:
                text,session = call(prompt,settings,attempt,images,role=role,timeout=available,schema=schema)
            except RuntimeError:
                if not session_path.exists():
                    raise
                session = read(session_path)
            event('cli_finished',role=role,partition=partition,path=rel(attempt),status=session['status'],seconds=session['seconds'])
            if session['status']=='completed':
                if session['tool_calls']:
                    raise RunStopped('Unexpected inner tools; call retained and charged')
                response = json.loads((attempt/'response.txt').read_text())
                english_output(response)
                return response
        check_service_pause()
        raw = (attempt/'stderr.log').read_text()+(attempt/'events.jsonl').read_text()
        transient = any(x in raw.lower() for x in ['service unavailable','rate limit','502','503','connection reset','overloaded'])
        if n==2 or not transient:
            raise RunStopped('model_call_timeout' if session['status']=='timeout' else 'model_service_error: '+rel(attempt))
        event('transient_retry_authorized',previous=rel(attempt),next_attempt=n+1)
    raise AssertionError('Unreachable CLI loop')


def settings_for(source, final=False):
    quality = CONFIG['final' if final else 'preview']
    with Image.open(source) as im:
        width,height = im.size
    scale = quality['long_edge']/max(width,height)
    return {**CONFIG['render'],'width':round(width*scale),'height':round(height*scale),
            'samples':quality['samples'],'threads':CONFIG['resources']['threads_per_blender'],'device':'CPU'}


def process(command, folder, stage, settings):
    timeout = min(CONFIG['blender'][stage+'_timeout'],remaining())
    if timeout<=0:
        raise RunStopped('total_budget_exceeded before '+stage)
    env = cpu_environment(threads=settings['threads'])
    env['SCENE_RSI_TELEMETRY'] = str(folder/'stage_events.jsonl')
    event(stage+'_submitted',folder=rel(folder),timeout=timeout,threads=settings['threads'])
    with (folder/f'{stage}_stdout.log').open('w') as out,(folder/f'{stage}_stderr.log').open('w') as err:
        result = run_measured(command,timeout=timeout,measurement_path=folder/f'{stage}_process.json',
                              memory_limit_bytes=CONFIG['resources']['memory_limit_gb']*1024**3,
                              cwd=folder,env=env,stdout=out,stderr=err)
    event(stage+'_finished',folder=rel(folder),status=result['status'],seconds=result['seconds'])
    return result


def blender_prefix():
    return [CONFIG['blender']['executable'],'--background','-noaudio','--factory-startup',
            '--disable-autoexec','--threads',str(CONFIG['resources']['threads_per_blender']),'--python-exit-code','1']


def render_checkpoint(checkpoint, folder, source, final=False):
    path = folder/'render_process.json'
    settings = settings_for(source,final)
    write_json(folder/'render_settings.json',settings)
    if path.exists():
        measured = read(path)
        if measured['status']=='running':
            raise RunStopped('Interrupted render needs audit: '+rel(folder))
        return measured
    guard('render')
    command = blender_prefix()+['--python',str(ROOT/'backend/render.py'),'--','--scene',str(ROOT/checkpoint),
                                '--settings',str(folder/'render_settings.json'),'--output-dir',str(folder)]
    return process(command,folder,'render',settings)


def execute(code, parent, folder, source, metadata):
    result_path = folder/'result.json'
    if result_path.exists():
        return read(result_path)
    folder.mkdir(parents=True,exist_ok=True)
    settings = settings_for(source)
    patch = folder/'patch.py'
    if patch.exists() and patch.read_text()!=code:
        raise ValueError('Attempt code changed after submission')
    patch.write_text(code)
    previous_code = (ROOT/parent).parent/'patch.py' if parent else None
    before = previous_code.read_text() if previous_code and previous_code.exists() else ''
    (folder/'patch.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),code.splitlines(True),fromfile='previous_incremental_script',tofile='current_incremental_script')))
    write_json(folder/'render_settings.json',settings)
    request = {**metadata,'parent_checkpoint':parent,'patch':rel(patch),'settings':settings,'time':time.time()}
    if not (folder/'build_request.json').exists():
        guard('build')
        write_json(folder/'build_request.json',request)
    command = blender_prefix()+['--python',str(ROOT/'incremental_blender.py'),'--',
              '--patch',str(patch),'--output-blend',str(folder/'scene.blend'),
              '--inventory',str(folder/'inventory.json'),'--events',str(folder/'stage_events.jsonl'),
              '--settings',str(folder/'render_settings.json'),'--backend-dir',str(ROOT/'backend')]
    if parent:
        command+=['--previous-checkpoint',str(ROOT/parent)]
    build_path = folder/'build_process.json'
    if build_path.exists():
        build = read(build_path)
        if build['status']=='running':
            raise RunStopped('Interrupted build needs audit: '+rel(folder))
    else:
        event('incremental_patch',**request)
        build = process(command,folder,'build',settings)
    failure = None
    render = None
    if build['returncode']:
        failure = 'resource_memory_limit' if build['memory_limit_exceeded'] else 'blender_build_timeout' if build['timed_out'] else 'blender_build_error'
    else:
        render = render_checkpoint(rel(folder/'scene.blend'),folder,source)
        if render['returncode']:
            failure = 'resource_memory_limit' if render['memory_limit_exceeded'] else 'render_timeout' if render['timed_out'] else 'render_error'
        else:
            with Image.open(folder/'final.png') as im:
                im.load()
                if im.size!=(settings['width'],settings['height']):
                    raise ValueError('Unexpected render dimensions')
    error = '\n'.join((folder/f'{s}_stderr.log').read_text()[-4000:] for s in ['build','render'] if (folder/f'{s}_stderr.log').exists())
    result = {**metadata,'ok':failure is None,'status':'completed' if failure is None else 'failed',
              'failure_type':failure,'parent_checkpoint':parent,'checkpoint':rel(folder/'scene.blend') if build['returncode']==0 else None,
              'render':rel(folder/'final.png') if failure is None else None,'patch':rel(patch),'inventory':rel(folder/'inventory.json'),
              'seconds':build['seconds']+(render['seconds'] if render else 0),'error':error,'build_ok':build['returncode']==0,
              'render_ok':failure is None,'images':metadata['images']}
    write_json(result_path,result)
    event('checkpoint_result',**{k:result[k] for k in ['task_id','stage_id','action_type','ok','failure_type','parent_checkpoint','checkpoint','render']})
    if failure and parent:
        event('parent_checkpoint_retained',task_id=metadata['task_id'],failed_attempt=rel(folder),checkpoint=parent)
    return result


def inventory(checkpoint):
    if checkpoint is None:
        return {'objects':[],'active_camera_id':None,'world':None}
    full = read((ROOT/checkpoint).parent/'inventory.json')['after']
    objects = []
    for object_id,item in full['objects'].items():
        objects.append({'object_id':object_id,**{k:item[k] for k in ['name','type','parent_id','matrix_world','dimensions','material_slots','camera','light','hide_render']}})
    return {'objects':objects,'active_camera_id':full['active_camera_id'],'world':full['world']}


def render_of(checkpoint):
    return rel((ROOT/checkpoint).parent/'final.png') if checkpoint else None


def make_patch(task, stage, action, parent, source, feedback=None, failed=None):
    folder = ROOT/'tasks'/task['id']/'stages'/f"{stage['stage_id']:02d}"
    saved = folder/f'{action}_response.json'
    if saved.exists():
        return read(saved)
    images = [source]
    if parent:
        images.append(ROOT/render_of(parent))
    context = {'stage':stage,'previous_checkpoint_exists':parent is not None,'inventory':inventory(parent),
               'feedback':feedback,'execution_error':failed,'operation':action,
               'completed_scope':stage['completed_scope'],'remaining_active_seconds':round(remaining())}
    if failed:
        context['failed_patch'] = (ROOT/failed['patch']).read_text()
        context['error_instruction'] = 'Repair this incremental patch against its ORIGINAL unchanged parent. No valid output image exists for the failed patch. Do not claim a visual revision occurred.'
    prompt = prompts.COMMON+prompts.PATCH_INSTRUCTION+'\nPUBLIC SCENEACT API:\n'+(ROOT/'sceneact_api.txt').read_text()+prompts.context_text(context)
    response = invoke(prompt,folder/'calls'/action,images,'student_'+action,prompts.PATCH,task['split'])
    if response['decision']=='apply' and not response['code'].strip():
        raise RunStopped('invalid_generated_program: empty patch')
    write_json(saved,response)
    return response


def apply_operation(task, stage, action, parent, source, feedback=None):
    folder = ROOT/'tasks'/task['id']/'stages'/f"{stage['stage_id']:02d}"
    response = make_patch(task,stage,action,parent,source,feedback)
    if response['decision']=='decline':
        event('student_declined_patch',task_id=task['id'],stage_id=stage['stage_id'],action=action,reason=response['reason'])
        return parent,[],response
    metadata = {'task_id':task['id'],'split':task['split'],'stage_id':stage['stage_id'],'action_type':action,'role':'student',
                'targets':stage['targets'],'images':[rel(source)]+([render_of(parent)] if parent else [])}
    result = execute(response['code'],parent,folder/(action+'_build'),source,metadata)
    attempts = [result]
    if not result['ok']:
        repair_record = folder/'technical_repair.json'
        if repair_record.exists() and read(repair_record)['for_action']!=action:
            return parent,attempts,response
        if not repair_record.exists():
            write_json(repair_record,{'for_action':action,'failure_type':result['failure_type'],'time':time.time()})
        repair = make_patch(task,stage,'technical_repair',parent,source,feedback,failed=result)
        response={**response,'technical_repair_response':repair}
        if repair['decision']=='apply':
            result = execute(repair['code'],parent,folder/'technical_repair_build',source,{**metadata,'action_type':'technical_repair'})
            attempts.append(result)
    response={**response,'actual_executed_patch':result['patch'],'actual_execution_ok':result['ok']}
    if result['ok']:
        measured=read(ROOT/result['inventory'])
        response['measured_scene_changes']=measured['changes']
        response['actual_executed_code']=(ROOT/result['patch']).read_text()
    return result['checkpoint'] if result['ok'] else parent,attempts,response


def validate_policy(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[x.name for x in node.names] if isinstance(node,ast.Import) else [node.module]
            if any(x!='json' for x in names):
                raise ValueError('Policy may import only json')
        if isinstance(node,ast.Name) and node.id in {'open','exec','eval','compile','__import__','globals','locals','getattr','setattr','input'}:
            raise ValueError('External effects forbidden in policy')
        if isinstance(node,ast.Attribute) and node.attr.startswith('__'):
            raise ValueError('Private introspection forbidden')
    if re.search(r'\b(?:D01|T01)\b|commons_\d+|/srv/|/home/',source):
        raise ValueError('Task-specific source or path in transferable policy')
    namespace = {}
    exec(compile(tree,'student_self_review.py','exec'),namespace)
    if not callable(namespace['build_review_prompt']):
        raise ValueError('Missing self-review entry')
    fixture = {'stage':{'stage_id':1,'title':'Fixture','targets':['environment'],'completed_scope':'environment'},'completed_scope':'environment','inventory':{'objects':[]},
               'previous_findings':[],'verification':False,'visual_correction_available':True,
               'operation':{'decision':'apply','changes':'fixture','code':'','reason':'fixture','advice_implementation':[],'completed_scope':'environment'}}
    if not isinstance(namespace['build_review_prompt'](fixture),str):
        raise ValueError('Self-review entry must return a string')
    return namespace['build_review_prompt']


def review(task, stage, checkpoint, previous, source, *, verification, prior=None, operation=None):
    folder = ROOT/'tasks'/task['id']/'stages'/f"{stage['stage_id']:02d}"
    name = 'confirmation' if verification else 'review'
    saved = folder/(name+'.json')
    if saved.exists():
        return read(saved)
    images = [source,ROOT/render_of(checkpoint)]
    if previous and previous!=checkpoint:
        images.append(ROOT/render_of(previous))
    context = {'stage':stage,'completed_scope':stage['completed_scope'],'inventory':inventory(checkpoint),
               'previous_findings':prior['findings'] if prior else [],'verification':verification,
               'visual_correction_available':not verification,'operation':operation}
    if task['split']=='development':
        prompt = prompts.TEACHER+prompts.context_text(context)
        role = 'teacher_verification' if verification else 'teacher_feedback'
    else:
        frozen = ROOT/'transfer/frozen'
        context['allowed_rule_sources']=[r['rule_id'] for r in read(ROOT/'transfer/lesson_provenance.json')['rules']]+['student_prior_judgment']
        entry = validate_policy((frozen/'student_self_review.py').read_text())
        prompt = prompts.SELF_REVIEW_CONTRACT+'\nFROZEN POLICY:\n'+(frozen/'self_check_policy.md').read_text()+'\n'+entry(context)
        role = 'student_self_verification' if verification else 'student_self_review'
        event('frozen_self_check_executed',task_id=task['id'],stage_id=stage['stage_id'],entry='transfer/frozen/student_self_review.py:build_review_prompt',verification=verification)
    response = invoke(prompt,folder/'calls'/name,images,role,prompts.REVIEW,task['split'])
    for finding in response['findings']:
        expected = 'test_observation' if task['split']=='test' else 'development_observation'
        if finding['problem_source']!=expected:
            raise RunStopped('Invalid observation provenance: '+finding['problem_source'])
        if not finding['reference_evidence'] or not finding['render_evidence']:
            raise RunStopped('Observation missing image evidence')
        if task['split']=='test':
            allowed={r['rule_id'] for r in read(ROOT/'transfer/lesson_provenance.json')['rules']}|{'student_prior_judgment'}
            if finding['rule_source'] not in allowed:
                raise RunStopped('Unknown frozen rule reference: '+finding['rule_source'])
    response['input_images'] = [rel(p) for p in images]
    response['role'] = role
    response['code_entry'] = 'transfer/frozen/student_self_review.py:build_review_prompt' if task['split']=='test' else 'prompts.py:TEACHER'
    write_json(saved,response)
    event('visual_observation',task_id=task['id'],stage_id=stage['stage_id'],verification=verification,decision=response['decision'],finding_ids=[x['id'] for x in response['findings']])
    return response


def run_stage(task, stage, parent, source):
    folder = ROOT/'tasks'/task['id']/'stages'/f"{stage['stage_id']:02d}"
    folder.mkdir(parents=True,exist_ok=True)
    saved = folder/'stage.json'
    if saved.exists() and read(saved)['status']!='running':
        return read(saved)
    record = {'task_id':task['id'],'split':task['split'],**stage,'status':'running','parent_checkpoint':parent,
              'initial_checkpoint':None,'final_checkpoint':parent,'initial_render':None,'final_render':render_of(parent),
              'attempts':[],'review':None,'confirmation':None,'student_revision':None}
    write_json(saved,record)
    checkpoint,attempts,response = apply_operation(task,stage,'initial',parent,source)
    record['attempts']+=attempts
    record['initial_response']=response
    if checkpoint is None or (attempts and not attempts[-1]['ok']):
        record.update(status='visual_loop_incomplete',failure_reason='No valid current-stage render after technical allowance',final_checkpoint=checkpoint)
        write_json(saved,record)
        return record
    record.update(initial_checkpoint=checkpoint,initial_render=render_of(checkpoint),final_checkpoint=checkpoint,final_render=render_of(checkpoint))
    write_json(saved,record)
    feedback = review(task,stage,checkpoint,parent,source,verification=False,operation=response)
    record['review']=feedback
    write_json(saved,record)
    if feedback['decision']=='revise':
        revised,attempts,response = apply_operation(task,stage,'visual_revision',checkpoint,source,feedback)
        record['attempts']+=attempts
        record['student_revision']=response
        actual = {'student_response':response,'execution_results':attempts,'retained_checkpoint':revised}
        confirmation = review(task,stage,revised,checkpoint,source,verification=True,prior=feedback,operation=actual)
        record.update(confirmation=confirmation,final_checkpoint=revised,final_render=render_of(revised))
        if attempts and not attempts[-1]['ok']:
            record['status']='advance_with_issue'
            record['failure_reason']='Visual patch failed; parent explicitly retained and reviewed'
        else:
            record['status']='advance_with_issue' if confirmation['decision']!='advance' else 'completed'
    else:
        record['status']='completed' if feedback['decision']=='advance' else 'advance_with_issue'
    write_json(saved,record)
    event('stage_finished',task_id=task['id'],stage_id=stage['stage_id'],status=record['status'],checkpoint=record['final_checkpoint'])
    return record


def final_delivery(task, checkpoint, source):
    folder = ROOT/'tasks'/task['id']/'delivery'
    saved = folder/'final.json'
    if saved.exists():
        return read(saved)
    folder.mkdir(exist_ok=True)
    rendered = render_checkpoint(checkpoint,folder,source,final=True)
    result={'status':'completed' if rendered['returncode']==0 else 'failed','checkpoint':checkpoint,
            'final_render':rel(folder/'final.png') if rendered['returncode']==0 else None,'quality_verdict':None,
            'teacher_review_of_final_quality_render':False,'student_review_of_final_quality_render':False}
    shutil.copy2(ROOT/checkpoint,folder/'scene.blend')
    result['blend']=rel(folder/'scene.blend')
    write_json(saved,result)
    event('final_delivery',task_id=task['id'],**result)
    return result


def run_task(task):
    global ACTIVE
    folder = ROOT/'tasks'/task['id'];folder.mkdir(exist_ok=True)
    state_path = folder/'state.json'
    state = read(state_path) if state_path.exists() else {'task_id':task['id'],'split':task['split'],'status':'not_started','stage_index':0,'last_checkpoint':None,'active_seconds':0}
    if state['status'] in {'completed','failed','visual_loop_incomplete'}:
        return state
    measured = sum(read(p)['seconds'] for p in folder.glob('**/*process.json') if read(p)['status']!='running')
    state['active_seconds']=max(state['active_seconds'],measured)
    ACTIVE={'base':state['active_seconds'],'started':time.monotonic()}
    state['status']='running';write_json(state_path,state)
    source=ROOT/task['image_path']
    try:
        plan_path=folder/'plan.json'
        if not plan_path.exists():
            prompt=prompts.COMMON+prompts.PLAN_INSTRUCTION
            if task['split']=='test':
                prompt+='\nFROZEN GENERAL SELF-CHECK POLICY:\n'+(ROOT/'transfer/frozen/self_check_policy.md').read_text()
            plan=invoke(prompt,folder/'calls/plan',[source],'student_plan',prompts.PLAN,task['split'])
            if [x['stage_id'] for x in plan['stages']]!=list(range(1,len(plan['stages'])+1)):
                raise RunStopped('Invalid stage numbering')
            write_json(plan_path,plan)
            event('stage_plan_frozen',task_id=task['id'],stages=plan['stages'])
        plan=read(plan_path)
        for stage in plan['stages']:
            if stage['stage_id']<=state['stage_index']:
                continue
            record=run_stage(task,stage,state['last_checkpoint'],source)
            state.update(stage_index=stage['stage_id'],last_checkpoint=record['final_checkpoint'])
            write_json(state_path,state)
            if record['status']=='visual_loop_incomplete':
                state['status']='visual_loop_incomplete';break
        else:
            delivered=final_delivery(task,state['last_checkpoint'],source)
            state['status']='completed' if delivered['status']=='completed' else 'failed'
        return state
    finally:
        state['active_seconds']=ACTIVE['base']+time.monotonic()-ACTIVE['started']
        if state['status']=='running':
            state['status']='interrupted'
        write_json(state_path,state)
        ACTIVE=None


def extract_policy():
    folder=ROOT/'transfer';freeze=folder/'freeze.json'
    if freeze.exists():
        return
    records=[read(p) for p in sorted((ROOT/'tasks/D01/stages').glob('*/stage.json'))]
    context={'development_plan':read(ROOT/'tasks/D01/plan.json'),'public_student_contract':prompts.COMMON,
             'entry_contract':'build_review_prompt(context) -> English string, json import only',
             'development_stages':records,'current_policy':'No learned policy; student follows the fixed incremental execution contract and can visually compare attachments.'}
    images=[ROOT/'sources/D01.jpg']
    for record in records:
        for key in ['initial_render','final_render']:
            if record[key] and ROOT/record[key] not in images:
                images.append(ROOT/record[key])
    prompt=prompts.DISTILL+prompts.context_text(context)
    response=invoke(prompt,folder/'calls/extract',images,'development_distillation',prompts.EXTRACTION,'development')
    write_json(folder/'extraction.json',response)
    for attempt in range(2):
        try:
            validate_policy(response['student_self_review_py'])
            english_output(response)
            for rule in response['lesson_provenance']:
                if rule['origin']=='development_derived' and not rule['evidence']:
                    raise ValueError('Derived rule lacks development evidence')
                for evidence in rule['evidence']:
                    record=next(x for x in records if x['stage_id']==evidence['stage_id'])
                    ids=[x['id'] for name in ['review','confirmation'] if record[name] for x in record[name]['findings']]
                    if evidence['feedback_id'] not in ids:
                        raise ValueError('Unknown feedback provenance: '+evidence['feedback_id'])
            break
        except (SyntaxError,ValueError,KeyError,StopIteration) as exc:
            write_json(folder/f'validation_error_{attempt+1}.json',{'error':str(exc)})
            if attempt==1:
                raise RunStopped('Extracted policy invalid after one format/interface correction')
            response=invoke(prompts.DISTILL+'\nCorrect only the format/interface/provenance error; do not add evidence.\n'+str(exc)+prompts.context_text({'previous_response':response,'development':context}),folder/'calls/format_correction',images,'development_distillation_repair',prompts.EXTRACTION,'development')
            write_json(folder/'extraction_corrected.json',response)
    (folder/'self_check_policy.md').write_text(response['policy_markdown']+'\n')
    (folder/'student_self_review.py').write_text(response['student_self_review_py']+'\n')
    write_json(folder/'lesson_provenance.json',{'rules':response['lesson_provenance'],'not_transferred':response['not_transferred'],'limitations':response['limitations']})
    (folder/'student_self_review.diff').write_text(''.join(difflib.unified_diff([],response['student_self_review_py'].splitlines(True),fromfile='no_learned_self_review_entry',tofile='student_self_review.py')))
    frozen=folder/'frozen';frozen.mkdir()
    for name in ['self_check_policy.md','student_self_review.py']:
        shutil.copy2(folder/name,frozen/name)
    write_json(freeze,{'version':'student_self_check_01','time':time.time(),'source_task':'D01','test_access':False,'code':'transfer/frozen/student_self_review.py','policy':'transfer/frozen/self_check_policy.md','test_started':False,'automatic_quality_evaluation':False,'is_weight_training':False,'is_teacher_self_evolution':False})
    event('student_policy_frozen',version='student_self_check_01',rules=len(response['lesson_provenance']),test_access=False)


def model_checks():
    fixture=read(ROOT/'preparation/preflight.json')
    if fixture['status']!='completed' or not all(fixture['checks'].values()):
        raise RunStopped('Deterministic preflight has not passed')
    images=[ROOT/'preparation/fixture/initial/final.png',ROOT/'preparation/fixture/incremental/final.png']
    schema=prompts.obj({'observation':prompts.TEXT,'difference':prompts.TEXT,'image_input_confirmed':{'type':'boolean'}})
    for role,settings in [('student_connectivity',CONFIG['model']),('preparation_teacher_connectivity',CONFIG['proposer'])]:
        response=invoke('In English only, briefly describe the two attached actual Blender fixture images and one visible difference. Do not use any tools or read files. Return the required JSON. Do not claim a model name or give a quality score.',ROOT/'preparation/model_checks'/role,images,role,schema,'preparation',model=settings)
        write_json(ROOT/'preparation/model_checks'/role/'result.json',response)
    write_json(ROOT/'preparation/model_checks.json',{'status':'completed','roles':['student','development_teacher'],'image_paths':[rel(p) for p in images],'model_route_independently_verified':False})


def run():
    if not (ROOT/'protocol_freeze.json').exists():
        raise RunStopped('Formal protocol must be frozen before running')
    if not (ROOT/'preparation/model_checks.json').exists():
        raise RunStopped('Image connectivity preflight missing')
    tasks=read(ROOT/'manifest.json')
    overall={'status':'running','started':time.time(),'experiment':ROOT.name}
    write_json(ROOT/'state.json',overall)
    try:
        dev=run_task(next(x for x in tasks if x['id']=='D01'))
        if dev['status']!='completed':
            raise RunStopped('Development incomplete; no invented lessons or automatic test')
        extract_policy()
        # The test receives only the frozen transferable code/text, never the provenance archive.
        test=run_task(next(x for x in tasks if x['id']=='T01'))
        overall.update(status='completed' if test['status']=='completed' else 'partial',finished=time.time(),budget=current())
    except (RunStopped,RuntimeError) as exc:
        overall.update(status='blocked' if (ROOT/'service_pause.json').exists() else 'interrupted',error=str(exc),finished=time.time(),budget=current())
        write_json(ROOT/'state.json',overall)
        raise
    write_json(ROOT/'state.json',overall)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['run','resume','report','model_checks']);args=parser.parse_args()
    os.sched_setaffinity(0,set(CONFIG['resources']['cpu_affinity']))
    if args.command=='report':
        import report
        report.generate();return
    with (ROOT/'experiment.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.command=='model_checks':model_checks()
        else:run()


if __name__=='__main__':
    main()
