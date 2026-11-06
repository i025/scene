"""Symmetric common visual evidence, two frozen M programs, one repair call each."""
from pathlib import Path
import ast
import copy
import difflib
import json
import subprocess
import sys
import time
import pilot
from diagnostics import localize,failure_evidence
from regression import MENU
from evaluate import score

ROOT=Path(__file__).resolve().parent
METHODS=['v2_1_fixed','v2_2_evidence']


def blender(action,dest,case=None,method=None):
    dest.mkdir(parents=True,exist_ok=True)
    args=[pilot.config()['blender']['executable'],'--background','--disable-autoexec','--threads','2',
          '--python-exit-code','2','--python',str(ROOT/'tests/controlled.py'),'--',action]
    if case:args+=['--case',case,'--method',method]
    started=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        try:result=subprocess.run(args,stdout=out,stderr=err,env=pilot.cpu_environment(),timeout=600)
        except subprocess.TimeoutExpired:
            measured={'status':'timeout','exit_code':None,'seconds':time.monotonic()-started}
        else:measured={'status':'completed' if result.returncode==0 else 'failed','exit_code':result.returncode,'seconds':time.monotonic()-started}
    pilot.write_json(dest/'process.json',measured);return measured


def context(case):
    folder=ROOT/'diagnosis'/case
    metrics=score(folder/'reference.png',folder,pilot.config())
    public=pilot.read(folder/'public.json');structure=pilot.read(folder/'functional/scene_structure.json')
    functional={'functional_pass':public['edit_observation']['measured_pass'] and structure['structure_pass'],
                'checks':{'structure':{'gate_pass':structure['structure_pass']}}}
    row={'scene_id':case,'status':'complete','folder':str(folder),'metrics':metrics,
         'functional':functional,'runtime_status':{'error':None}}
    entry={**row,'objects':structure['objects'],'all_object_ids':[o['name'] for o in structure['objects']],
           'structure':structure,'failure_evidence':failure_evidence(row),
           'attached_images':[str(folder/'reference.png'),str(folder/'final.png')],
           'public_program':public['public_program']}
    applicability={name:(structure['structural_checks'][name]['applicable'] if name in structure['structural_checks'] else True) for name in MENU}
    return {'development':[entry],'visual_findings':[],'archive':[],'phase':'before_patch',
            'remaining_probe_budget':2,'already_executed_probe_count':0,
            'available_probe_menu':['camera_focal','object_scale','isolate'],
            'remaining_regression_budget':3,'modification_risks':[],
            'available_regression_menu':{name:{'available':True,'cost':1,'scene_applicability':{case:applicability[name]}} for name in MENU}},row


def validate(code,case):
    tree=ast.parse(code)
    for name in ['frame','size','show','support','local_material']:
        if not any(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body):raise ValueError('Missing shared helper '+name)
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in n.names] if isinstance(n,ast.Import) else [n.module]
            if any(name not in ['bpy','math','mathutils'] for name in names):raise ValueError('Import outside shared helper contract')
        if isinstance(n,ast.Name) and n.id in ['open','exec','eval','__import__','compile']:raise ValueError('External execution in helper')
        if isinstance(n,ast.Attribute) and (n.attr.startswith('__') or n.attr in ['render','save_as_mainfile','open_mainfile','read_homefile','read_factory_settings','load']):raise ValueError('Global/file operation outside helper contract')
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and any(tag in n.value for tag in [case,'/home/','/srv/','reference.png']):raise ValueError('Task/path-specific shared code')


def run_case(case,method,base,findings,row):
    dest=ROOT/'diagnosis'/case/method;dest.mkdir(exist_ok=True)
    if (dest/'result.json').exists():return
    source=ROOT/'code_snapshots/v2_1_initial_meta/scene_rsi_v2_1/meta.py' if method=='v2_1_fixed' else ROOT/'initial_meta/scene_rsi_v2_2/meta.py'
    ctx=copy.deepcopy(base);ctx['visual_findings']=findings
    plan=pilot.meta_execute(source,'plan_probes',ctx)
    pilot.write_json(dest/'stage1.json',{'context':ctx,'M_source':str(source),'decision':plan})
    normalized=copy.deepcopy(plan)
    if method=='v2_1_fixed':
        for request in normalized['probes']:
            finding=next(f for f in findings if f['scene_id']==request['scene_id'] and f['probe']==request['probe'] and (request['probe']=='camera_focal' or f['object_id']==request['object_id']))
            request.update(alternatives=finding['alternatives'],probe_reason=finding['probe_reason'])
    observations=pilot.execute_plan(ctx,{'probes':normalized['probes'],'regressions':[]},[row],dest)
    for i,request in enumerate(normalized['regressions']):
        if request['test']=='material_preservation':
            process=blender('material-regression',dest/'material_process',case,method)
            result=pilot.read(dest/'material_regression.json') if process['status']=='completed' else {'applicable':False,'measured_pass':None,'process':process}
        else:result=pilot.inspect(Path(row['folder']),'regression',output=dest/'regression'/str(i),test=request['test'])
        observations['regression'].append({'request':request,'result':result});ctx['remaining_regression_budget']-=1
    pilot.write_json(dest/'observations.json',observations)
    decision=pilot.meta_execute(source,'plan_patch',ctx,observations)
    neutral=pilot.meta_execute(source,'plan_patch',ctx,{'probes':[],'regression':[]})
    pilot.write_json(dest/'stage2.json',{'context_after_execution':ctx,'observations':observations,'decision':decision,
        'neutral_without_observations':neutral,'module_changed_by_observations':decision['shared_module']!=neutral['shared_module'],
        'neutral_scope':'Deterministic same-M program replay only; no extra model, probe, repair attempt or meta-capacity test'})
    original=(ROOT/'diagnosis'/case/'shared_h0.py').read_text()
    prompt='Repair this shared SceneAct/Blender fixture transformation helper from the same starting source used by both strategies. All five public functions must remain. frame uses requested focal length; size uses requested scale; show implements requested visibility; support places the group at the requested support coordinate while preserving part dependency; local_material changes only the target material appearance, preserving non-target geometry and shader values even with shared mesh/material data. This API contract provides repair hints and is identical for both arms. You receive no injected-fault label or evaluator truth. Use the actual M decisions/observations. You may investigate any helper function, including when M is unresolved; one coding call, no repair retries. Return complete shared code and reason. No task IDs, object names, image paths, filesystem or network. It will be tested on new names/nominal parameters and ownership patterns.\n'+json.dumps({'shared_H_source':original,'public_program':base['development'][0]['public_program'],'stage1':plan,'actual_observations':observations,'stage2':decision},ensure_ascii=False)
    images=[str(ROOT/'diagnosis'/case/'reference.png'),str(ROOT/'diagnosis'/case/'final.png'),*[str(p) for p in sorted((dest/'probes').glob('*/probe_*.png'))]]
    schema={'type':'object','additionalProperties':False,'properties':{'code':{'type':'string'},'reason':{'type':'string'}},'required':['code','reason']}
    try:
        saved_session=dest/'repair_call/session.json'
        if saved_session.exists():
            session=pilot.read(saved_session)
            if session['status']!='complete':raise RuntimeError('Prior submitted CLI call failed or was interrupted; preserve it without automatic resampling')
            answer=(dest/'repair_call/response.txt').read_text()
        else:answer,session=pilot.call(prompt,pilot.config()['proposer'],dest/'repair_call',images,role='controlled_shared_repair',schema=schema)
    except (RuntimeError,subprocess.TimeoutExpired) as error:
        pilot.write_json(dest/'result.json',{'method':method,'scene_id':case,'status':'failed',
            'failure_stage':'Codex shared-repair call','failure_reason':str(error),
            'source_pass':None,'transfer_pass':None,'shared_module':decision['shared_module'],
            'algorithm_failure_confirmed':False})
        pilot.check_service_pause()
        if 'Global budget exhausted' in str(error):raise
        return
    response=json.loads(answer);(dest/'candidate.py').write_text(response['code']);pilot.write_json(dest/'rationale.json',response)
    (dest/'changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),response['code'].splitlines(True),fromfile='shared_H0.py',tofile='shared_H_repaired.py')))
    try:validate(response['code'],case)
    except (ValueError,SyntaxError) as error:
        result={'status':'invalid','failure_reason':str(error),'source_pass':None,'transfer_pass':None}
    else:
        if (dest/'repair_process').exists():
            process=pilot.read(dest/'repair_process/process.json',{'status':'failed','exit_code':None,'reason':'Prior evaluation was interrupted; no automatic rerender'})
        else:
            pilot.guard('render',2)
            process=blender('evaluate',dest/'repair_process',case,method)
        evaluation=pilot.read(dest/'repair_evaluation.json') if process['status']=='completed' else None
        if evaluation:
            current_structure=pilot.read(dest/'source_structure.json')
            diff=(dest/'changes.diff').read_text().lower()
            tags=[word for word in ['mesh','scale','material','support','camera'] if word in diff]
            pilot.write_json(dest/'post_patch_evidence.json',{
                'historical_visual_findings':findings,'current_visual_findings':[],
                'localization_status':'not_relocalized_after_patch','new_visual_calls':0,
                'current_object_ids':[o['name'] for o in current_structure['objects']],
                'current_structure':current_structure,'current_functional_measurements':evaluation,
                'diff_risks':{'tags':tags,'basis':'approximate keyword screen only, not precise module attribution'},
                'further_M_decision':'not_requested; one coding attempt frozen; no historical mapping reused as current fact'})
        result={'status':process['status'],'failure_reason':None if evaluation else 'Candidate execution failed; inspect repair_process logs',
                'source_pass':evaluation['source']['all_pass'] if evaluation else None,
                'transfer_pass':evaluation['transfer']['all_pass'] if evaluation else None,'process':process}
    result.update(method=method,scene_id=case,M_source=str(source),shared_module=decision['shared_module'],
                  shared_localizer_calls=1,own_repair_calls=1,localizer_allocation='One identical cached visual call per case shared by both arms; not two independent calls',
                  new_M_descendant=False,H_scope='Auxiliary shared fixture program; not natural-image reconstruction H',
                  post_patch_visual_findings='historical only; no new visual localization requested; current measured structure is saved in source_structure.json and transfer_structure.json')
    if result['status']!='invalid':
        def functions(code):
            tree=ast.parse(code)
            return {n.name:ast.get_source_segment(code,n) for n in tree.body if isinstance(n,ast.FunctionDef)}
        before=functions(original);after=functions(response['code'])
        changed=[name for name in before if before[name]!=after[name]]
        related={'camera':'frame','object_parameters':'size','object_coverage':'show',
                 'support_relations':'support','part_dependencies':'support','material_edit':'local_material'}
        result['changed_function_regions']=changed
        result['M_module_region_changed']=related[decision['shared_module']] in changed if decision['shared_module'] in related else None
        result['alignment_limit']='Function-region text changes identify patch scope, not semantic causality; external source and transfer checks remain separate.'
    pilot.write_json(dest/'result.json',result)


def main():
    assert (ROOT/'configs/BC_freeze.json').exists()
    if not (ROOT/'diagnosis/creation.json').exists():
        pilot.guard('render',20)
        if blender('create',ROOT/'diagnosis/creation_process')['status']!='completed':raise RuntimeError('Controlled fixture construction failed; no model diagnosis submitted')
    for index,folder in enumerate(sorted((ROOT/'diagnosis').glob('case*'))):
        base,row=context(folder.name)
        if (folder/'common_localization_failure.json').exists():continue
        try:findings=localize(base['development'],folder/'common_localization')
        except (RuntimeError,subprocess.TimeoutExpired,ValueError) as error:
            pilot.write_json(folder/'common_localization_failure.json',{'status':'failed','error':str(error),
                'dependent_arms':METHODS,'actual_module_measurement':None,'automatic_retries':0})
            pilot.check_service_pause()
            if 'Global budget exhausted' in str(error):raise
            continue
        order=METHODS if index%2==0 else list(reversed(METHODS))
        for method in order:run_case(folder.name,method,base,findings,row)
    results=list((ROOT/'diagnosis').glob('case*/*/result.json'))
    pilot.write_json(ROOT/'diagnosis/state.json',{'phase':'C_finished_with_records',
        'scheduled_cases':10,'scheduled_arm_results':20,'actual_arm_results':len(results),
        'common_localization_failures':len(list((ROOT/'diagnosis').glob('case*/common_localization_failure.json'))),
        'ledger':pilot.current()})


if __name__=='__main__':main()
