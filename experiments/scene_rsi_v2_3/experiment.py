"""Paired, interleaved fixed/structured/active diagnosis; one coding proposal per arm."""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import json
import shutil
import subprocess
import time
from common import ROOT,read,write,blender,current,call
import meta

METHODS=['fixed','structured','active']
MODULES=['set_view','SceneCompiler.emit.geometry','SceneCompiler.emit.position','SceneCompiler.emit.coverage','SceneCompiler.emit.parent','set_render_visibility','support_on','prepare_edit_mesh','edit_surface','unresolved']


def schema_object(properties):return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
TEXT={'type':'string'};NUMBER={'type':'number'}
HYPOTHESIS=schema_object({'id':TEXT,'module':{'type':'string','enum':MODULES},'object_id':TEXT,'explanation':TEXT,
    'predictions':schema_object({t:schema_object({'lower':NUMBER,'upper':NUMBER,'reason':TEXT}) for t in meta.MENU})})
FINDINGS=schema_object({'observation':TEXT,'object_id':TEXT,'initial_module':{'type':'string','enum':MODULES},'initial_confidence':{'type':'number','minimum':0,'maximum':1},'probe_targets':schema_object({t:TEXT for t in meta.MENU}),
    'hypotheses':{'type':'array','items':HYPOTHESIS,'minItems':2,'maxItems':3},'limitations':TEXT})
REPAIR=schema_object({'code':TEXT,'reason':TEXT,'diagnosis_agreement':TEXT,'changed_regions':{'type':'array','items':TEXT}})
TOOL_MEANING={
    'camera_calibration':'Execute current H.set_view with public lens*1.2 and sensor*.85. Outcome abs(returned_sensor-requested_sensor)/requested_sensor.',
    'geometry_replay':'Recompile current public SceneAct plan with nonuniform root scale [1.17,.82,1.09]. Outcome maximum emitted mesh basis-length discrepancy from public input geometry_frame * primitive dimensions.',
    'position_replay':'Recompile public plan with furniture offset [1.7,2.6,0]. Outcome maximum y translation discrepancy from public geometry_frame/primitive origin plus final group move, divided by furniture width.',
    'visibility_isolation':'Call current H.set_render_visibility(panel,True), hide other nonstructural objects. On the explicitly selected group/mesh toggle False then True. Outcome 2 if no emitted meshes; else visible fraction after False plus hidden fraction after True. It measures this H visibility contract and missing emission, not a new visibility label.',
    'support_relation':'Displace furniture upward then run current H.support_on. Outcome absolute AABB bottom-to-floor-top gap divided by furniture height. Approximate support only.',
    'dependency_move':'Move actual furniture group. Outcome max(fraction of parts not following, fraction parented contrary to emitted named part contract).',
    'material_dependency':'Execute current H.edit_surface with a fresh target color. Outcome number of non-target objects whose geometry/transform/material parameters changed. Uses actual H, shared mesh and material ownership.'}


def saved_call(prompt,folder,images,role,schema):
    if (folder/'session.json').exists():
        prior=read(folder/'session.json')
        if prior['status']!='complete':raise RuntimeError('Prior CLI attempt failed or interrupted; preserve without automatic resampling: '+str(folder))
        return json.loads((folder/'response.txt').read_text())
    answer,_=call(prompt,read(ROOT/'config.json')['proposer'],folder,images,role=role,schema=schema)
    return json.loads(answer)


def common_findings(case):
    folder=ROOT/'tasks'/case;public=read(folder/'public.json');source=(folder/'H0.py').read_text()
    prompt='You are diagnosing a reusable SceneAct-to-Blender compiler and editing pipeline from desired and faulty images. This is an engineered controlled mechanism test. You do not receive fault injection labels or original correct code. All three arms receive this identical initial report. Read the attached REAL images (first desired, second current). Identify an actual object/group using public IDs, or unknown if unmappable; camera-only may use unknown. Choose actual per-tool object IDs in probe_targets: dependency/support need the relevant furniture group, material needs one concrete mesh (not a multi-mesh group), visibility needs the suspected group. Camera and whole-plan geometry/position replay allow unknown. Provide at least two reasonable competing explanations, each associated with a module. For EVERY tool predict a numerical interval for the explicitly defined scalar outcome BEFORE any tool is run. Intervals must reflect uncertainty; do not invent certainty. Predict differences only justified by the supplied code and evidence. Two hypotheses predicting the same response are not distinguished by that tool. Do not assert a Q increase identifies cause. Output a tentative initial module and confidence, competing explanations and limitations.\n'+json.dumps({'tools':TOOL_MEANING,'public_evidence':public,'current_shared_H':source,'available_modules':MODULES},ensure_ascii=False)
    findings=saved_call(prompt,folder/'common_diagnosis',[folder/'reference.png',folder/'final.png'],'shared_initial_diagnosis',FINDINGS)
    if not 0<=findings['initial_confidence']<=1:raise ValueError('Invalid external confidence')
    for hypothesis in findings['hypotheses']:
        for interval in hypothesis['predictions'].values():
            if interval['lower']>interval['upper']:raise ValueError('Invalid external prediction interval')
    return findings


def regions(code):
    tree=ast.parse(code);result={}
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):result[node.name+('('+ast.unparse(node.args.args[0].annotation)+')' if node.name=='_' else '')]=ast.get_source_segment(code,node)
        if isinstance(node,ast.ClassDef):
            for child in node.body:
                if isinstance(child,ast.FunctionDef):result[node.name+'.'+child.name]=ast.get_source_segment(code,child)
    return result


def validate(code,original):
    before=regions(original);after=regions(code)
    if set(before)-set(after):raise ValueError('Shared public entry points removed: '+str(set(before)-set(after)))
    for node in ast.walk(ast.parse(code)):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]]
            if any(n not in ['bpy','math','mathutils','functools','kernel','composition','telemetry','json'] for n in names):raise ValueError('Import outside compiler scope')
        if isinstance(node,ast.Name) and node.id in ['open','exec','eval','__import__','compile']:raise ValueError('File/execution primitive outside H scope')
        if isinstance(node,ast.Attribute) and node.attr in ['render','save_as_mainfile','open_mainfile','load']:raise ValueError('Evaluator/file access outside H scope')
        if isinstance(node,ast.Constant) and isinstance(node.value,str) and any(tag in node.value for tag in ['/srv/','/home/','task01','smoke01','reference.png','NovelDesk','StudyDesk','StudyBench','NovelBench']):raise ValueError('Case/path/asset-specific code')
    return [name for name in after if name not in before or before[name]!=after[name]]


def run_arm(case,method,findings):
    folder=ROOT/'tasks'/case;dest=folder/method;dest.mkdir(exist_ok=True)
    if (dest/'result.json').exists():return
    public=read(folder/'public.json');original=(folder/'H0.py').read_text()
    if findings['object_id']!='unknown' and findings['object_id'] not in public['valid_object_ids']:raise ValueError('Diagnosis object ID not in scene')
    ctx={'method':method,'scene_id':case,'object_id':findings['object_id'],'hypotheses':findings['hypotheses'],
         'initial_module':findings['initial_module'],'initial_confidence':findings['initial_confidence'],'probe_targets':findings['probe_targets'],
         'remaining_probe_budget':2,'already_executed_probe_count':0,'available_probe_menu':meta.MENU,
         'raw_evidence':public}
    if (dest/'stage1.json').exists():
        saved=read(dest/'stage1.json');ctx=saved['context'];plan=saved['plan']
    else:plan=meta.plan_probes(copy.deepcopy(ctx))
    # This exact file is written before any selected experiment; never backfilled.
    if not (dest/'stage1.json').exists():write(dest/'stage1.json',{'context':ctx,'plan':plan,'saved_before_probe':time.time()})
    observations=[]
    for index,request in enumerate(plan['probes']):
        pd=dest/'probes'/str(index+1);pd.mkdir(parents=True,exist_ok=True)
        request_path=pd/'request.json';write(request_path,request)
        if (pd/'process.json').exists():status=read(pd/'process.json')
        else:status=blender('probe',pd,case,folder/'H0.py',request_path,frames=1)
        measurement=read(pd/'measurement.json') if status['status']=='completed' else None
        obs={'request':request,'status':status['status'],'measurement':measurement,'folder':str(pd)}
        observations.append(obs);ctx['remaining_probe_budget']-=1;ctx['already_executed_probe_count']+=1
    write(dest/'observations.json',observations)
    decision=meta.plan_patch(ctx,observations)
    neutral=meta.plan_patch(ctx,[])
    write(dest/'stage2.json',{'decision':decision,'neutral_without_observations':neutral,'module_changed_by_observations':decision['selected_code_module']!=neutral['selected_code_module'],
          'budget_after_execution':{k:ctx[k] for k in ['remaining_probe_budget','already_executed_probe_count']}})
    # Identical prompt template and source permissions. No correct source, injection, hidden tests or per-function solutions.
    prompt='Repair the supplied reusable SceneAct Blender compiler/editing program. You receive desired/current images, public scene-plan requirements and this method diagnosis. Investigate and modify ANY module if warranted, including if diagnosis is wrong or unresolved. Preserve public entry points and dependencies; change reusable implementation, never task IDs, asset names or a single scene parameter. One complete-code proposal; no iterative repair. You cannot run tools here; actual probes and public feedback are provided. Hidden independent scene checks will be executed externally, never shared. Return complete program, rationale, diagnosis agreement and changed regions.\n'+json.dumps({'requirements':public['requirements'],'public_scene_plan':public['spec'],'initial_public_evidence':public,
             'current_shared_H':original,'initial_diagnosis':findings,'method_stage1':plan,'actual_observations':observations,'M_stage2':decision},ensure_ascii=False)
    images=[folder/'reference.png',folder/'final.png',*[Path(o['folder'])/'probe.png' for o in observations if o['status']=='completed']]
    try:answer=saved_call(prompt,dest/'repair_call',images,'shared_H_repair',REPAIR)
    except (RuntimeError,subprocess.TimeoutExpired) as error:
        write(dest/'result.json',{'scene_id':case,'method':method,'status':'failed','failure_stage':'model_call','reason':str(error),'effective_shared_repair':None,'transfer_repair':None,'regression':None});return
    (dest/'candidate.py').write_text(answer['code']);write(dest/'rationale.json',answer)
    (dest/'changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),answer['code'].splitlines(True),fromfile='shared_H0.py',tofile='shared_candidate.py')))
    try:changed=validate(answer['code'],original)
    except (ValueError,SyntaxError) as error:
        write(dest/'result.json',{'scene_id':case,'method':method,'status':'invalid','failure_stage':'source_validation','reason':str(error),'effective_shared_repair':None,'transfer_repair':None,'regression':None});return
    status=read(dest/'process.json') if (dest/'process.json').exists() else blender('evaluate',dest,case,dest/'candidate.py',frames=2)
    evaluation=read(dest/'evaluation.json') if status['status']=='completed' else None
    selected=decision['selected_code_module'];region=selected.split('.geometry')[0].split('.position')[0].split('.coverage')[0].split('.parent')[0]
    write(dest/'result.json',{'scene_id':case,'method':method,'status':status['status'],'failure_stage':None if evaluation else 'candidate_execution','reason':None if evaluation else 'See Blender stdout/stderr',
          'changed_regions':changed,'changed_module_count':len(changed),'diagnosis_region_changed':region in changed if selected!='unresolved' else None,
          'selected_code_module':selected,'object_id':findings['object_id'],'effective_shared_repair':evaluation['effective_shared_repair'] if evaluation else None,
          'transfer_repair':evaluation['transfer_repair'] if evaluation else None,'regression':evaluation['regression'] if evaluation else None,
          'new_M_descendant':False,'H_scope':'Actual SceneAct compiler subset and reusable editing/support interfaces; not end-to-end natural-image H'})


def run(smoke=False):
    assert smoke or (ROOT/'configs/freeze.json').exists()
    cases=['smoke01','smoke02'] if smoke else ['task'+str(i).zfill(2) for i in range(1,11)]
    for index,case in enumerate(cases):
        write(ROOT/'state.json',{'phase':'running','scene_id':case,'ledger':current()})
        try:findings=common_findings(case)
        except (RuntimeError,subprocess.TimeoutExpired,ValueError) as error:
            write(ROOT/'tasks'/case/'common_failure.json',{'status':'failed','reason':str(error),'dependent_arms':METHODS});continue
        order=METHODS[index%3:]+METHODS[:index%3]
        for method in order:
            write(ROOT/'state.json',{'phase':'running','scene_id':case,'method':method,'ledger':current()})
            run_arm(case,method,findings)
            print(case,method,read(ROOT/'tasks'/case/method/'result.json')['status'],current()['cli_sessions'],flush=True)
    write(ROOT/('smoke_state.json' if smoke else 'FINAL_STATUS.json'),{'phase':'all_scheduled_terminal','scheduled':len(cases)*3,
         'result_files':sum((ROOT/'tasks'/c/m/'result.json').exists() for c in cases for m in METHODS),'ledger':current(),'automatic_M_descendants':0})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['smoke','pilot','resume']);args=parser.parse_args()
    if args.action=='resume' and (ROOT/'FINAL_STATUS.json').exists():
        from analyze import main as report
        report();return
    run(args.action=='smoke')


if __name__=='__main__':main()
