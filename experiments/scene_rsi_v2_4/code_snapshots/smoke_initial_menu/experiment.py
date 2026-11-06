"""Natural-image shared-H development; bounded three-arm single proposals."""
from pathlib import Path
import argparse
import copy
import difflib
import json
import shutil
import time
import subprocess
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity
import pilot
import meta

ROOT = Path(__file__).resolve().parent
METHODS = ['fixed', 'structured', 'active']
MODULES = ['camera_framing', 'geometry_scale_depth', 'coverage_occlusion', 'support_layout', 'material_dependencies', 'execution_complexity', 'unresolved']
TOOLS = {
    'camera_focal': 'Fixed scene geometry; multiply current perspective focal length by1.1. Outcome: SSIM(reference,probe)-SSIM(reference,current).',
    'object_scale': 'Fixed camera; scale the explicitly named real object/group by1.1 around its geometry AABB center. Outcome: delta SSIM to reference.',
    'isolate': 'Keep only the explicitly named object/group meshes visible, temporarily hiding other meshes. Outcome: delta SSIM to reference. The probe image reveals emitted geometry, not true missing geometry.'}


def read(path): return json.loads(path.read_text())
write = pilot.write_json


def obj(properties):
    return {'type':'object', 'additionalProperties':False, 'properties':properties, 'required':list(properties)}


S = {'type':'string'}
INTERVAL = obj({'lower':{'type':'number'}, 'upper':{'type':'number'}, 'reason':S})
FINDINGS = obj({'visual_difference':S, 'object_id':S, 'initial_module':{'type':'string','enum':MODULES},
    'initial_confidence':{'type':'number','minimum':0,'maximum':1},
    'probe_targets':obj({t:S for t in meta.MENU}),
    'hypotheses':{'type':'array','minItems':2,'maxItems':3,'items':obj({'id':S,'module':{'type':'string','enum':MODULES},'object_id':S,'explanation':S,'predictions':obj({t:INTERVAL for t in meta.MENU})})},
    'program_evidence':S, 'limitations':S})
PATCH = obj({'policy':S, 'system':S, 'reason':S, 'observation_used':S, 'scope':S})


def saved_call(prompt, folder, images, role, schema):
    if (folder/'session.json').exists():
        if read(folder/'session.json')['status'] != 'complete':
            raise RuntimeError('Saved failed CLI attempt; no automatic resampling: '+str(folder))
        return json.loads((folder/'response.txt').read_text())
    answer, _ = pilot.call(prompt, pilot.config()['proposer'], folder, images, role=role, schema=schema)
    return json.loads(answer)


def ssim(reference, render):
    a, b = [np.asarray(Image.open(p).convert('RGB')) for p in [reference, render]]
    return float(structural_similarity(a,b,channel_axis=2,data_range=255))


def prepare():
    old = ROOT.parent/'scene_rsi_v2_2'
    scenes = {s['scene_id']:s for s in read(old/'manifest.json')}
    specs = [('smoke','commons_104864364',None),
             ('task01','commons_31294395','commons_192968130'),
             ('task02','commons_92056365','commons_96943062')]
    manifest=[]
    for task_id, source, transfer in specs:
        dest=ROOT/'tasks'/task_id;dest.mkdir(parents=True,exist_ok=True)
        original=old/'results/r1/fixed_h/r1_C2/fixed_version_test'/source
        assert read(original/'record.json')['metrics']['valid']
        evidence=dest/'evidence';evidence.mkdir(exist_ok=True)
        for name in ['scene.blend','final.png','build.py','reference.png','record.json']:
            if not (evidence/name).exists():shutil.copy2(original/name,evidence/name)
        structure=pilot.inspect(evidence,mode='inspect')
        row={'task_id':task_id,'source':{**scenes[source],'split':'selection'},
             'transfer':{**scenes[transfer],'split':'test'} if transfer else None,
             'diagnostic_scene_source':str(original),'diagnostic_H':'V2.1 r1/C2; same policy/system copied unchanged',
             'exposure':'Previously evaluated V2.2 natural images; exploratory, not a fresh blind test.',
             'valid_blend':structure['blend_opened']}
        write(dest/'task.json',row);manifest.append(row)
    write(ROOT/'manifest.json',manifest)
    (ROOT/'reuse_inventory.md').write_text('''# V2.4 复用\n\n复用 V2.2 backend、SceneAct、CLI adapter、pilot.run_scene、inspect_blend、regression。\n共同起点 fixed_h/r1_C2 是 V2.1 已演化版本，明确称 H_start，原始 H0另存 fixed_h/H0；不冒充原始起点。\n诊断输入为 V2.2 已成功真实图像重建与完整程序，不提供正确场景程序、注入补丁或故障标签。\n本轮 CPU2线程、单重任务，Cycles16samples、512长边、AgX、seed42。权重与Blender直接引用旧路径，不下载。\n历史图像全部已暴露，本轮探索性；不把源图和迁移图混成独立重复。\n''')


def context_for(task_id, method):
    folder=ROOT/'tasks'/task_id;ev=folder/'evidence'
    structure=read(ev/'inspect/scene_structure.json')
    objects=pilot.projected_objects(structure['objects'])
    public={'visual_metrics':read(ev/'record.json')['metrics'],
            'functional':read(ev/'record.json')['functional'],
            'objects':objects, 'valid_object_ids':[o['name'] for o in structure['objects']],
            'scene_program_P':(ev/'build.py').read_text(),
            'shared_H_policy':(ROOT/'fixed_h/r1_C2/policy.py').read_text(),
            'shared_H_system':(ROOT/'fixed_h/r1_C2/system.txt').read_text(),
            'tools':TOOLS, 'limitation':'No 3D ground truth. No correct module given. Naming/projection are approximate object correspondence.'}
    prompt = ('Read both actual attached images: natural photograph first, historical reconstruction second. '
              'Diagnose a reusable image-to-SceneAct reconstruction workflow, not an injected helper bug. '
              'Describe an observable discrepancy and at least two competing explanations from DIFFERENT modules. '
              'Localize an object using actual supplied IDs/projection and program, or unknown. Do not select largest/first Mesh by default. '
              'Before experiments, predict a numerical delta-SSIM interval for EACH tool under EACH hypothesis. '
              'Intervals may overlap; uncertainty is expected. Different forecasts need evidence, not a desire to force probes. '
              'Do not assume an increase uniquely identifies cause. Do not use tools or external files.\n'+json.dumps(public,ensure_ascii=False))
    schema=copy.deepcopy(FINDINGS)
    target_schema={'type':'string','enum':public['valid_object_ids']+['unknown']}
    schema['properties']['object_id']=target_schema
    for tool in meta.MENU:schema['properties']['probe_targets']['properties'][tool]=target_schema
    schema['properties']['hypotheses']['items']['properties']['object_id']=target_schema
    findings=saved_call(prompt,folder/method/'diagnosis',[ev/'reference.png',ev/'final.png'],'initial_diagnosis',schema)
    ids=set(public['valid_object_ids'])|{'unknown'}
    for target in [findings['object_id'],*findings['probe_targets'].values(),*[h['object_id'] for h in findings['hypotheses']]]:
        if target not in ids:raise ValueError('Model target is absent from actual scene: '+target)
    for h in findings['hypotheses']:
        for p in h['predictions'].values():
            if p['lower']>p['upper']:raise ValueError('Inverted external forecast interval')
    return {'method':method,'valid_blend':True,'remaining_probe_budget':2,'already_executed_probe_count':0,
            'available_probe_menu':TOOLS,'raw_evidence':public,**findings}


def propose(task_id,method):
    folder=ROOT/'tasks'/task_id;dest=folder/method;dest.mkdir(exist_ok=True)
    if (dest/'candidate.json').exists():return
    ctx=context_for(task_id,method)
    plan=meta.plan_probes(copy.deepcopy(ctx))
    if (dest/'stage1.json').exists():
        prior=read(dest/'stage1.json');ctx,plan=prior['context'],prior['plan']
    else:write(dest/'stage1.json',{'context':ctx,'plan':plan,'saved_before_probe':time.time()})
    observations=[];ev=folder/'evidence'
    for i, request in enumerate(plan['probes']):
        pd=dest/'probes'/str(i+1)
        result=pilot.inspect(ev,mode='probe',probe=request['probe'],object_id=None if request['object_id']=='unknown' else request['object_id'],output=pd)
        png=pd/('probe_'+request['probe']+'.png')
        observed={'request':request,'status':result['status'],'measurement':result,'delta_ssim':None,'image':None}
        if result['status']=='completed':
            observed.update(delta_ssim=ssim(ev/'reference.png',png)-ssim(ev/'reference.png',ev/'final.png'),image=str(png))
        observations.append(observed)
        ctx['remaining_probe_budget']-=1;ctx['already_executed_probe_count']+=1
        write(dest/'observations.json',observations)
    decision=meta.plan_patch(copy.deepcopy(ctx),copy.deepcopy(observations))
    write(dest/'stage2.json',{'context':ctx,'actual_observations':observations,'M_decision':decision,'M_program':'meta.py','executed':True})
    prompt=('Modify ONLY the shared image-to-SceneAct H. Return complete policy.py and system.txt. '
            'This is one proposal, no extra tools/calls. Keep the frozen Runtime API and SceneAct representation. '
            'No task IDs, image paths, per-image scene coordinates, object-name-specific branches or test answers. '
            'General reconstruction reasoning, validation and complexity management may change. '
            'The scene program P is evidence only: never return a repaired P as H. '
            'Use the actual executable M decision and report how observations did or did not influence your change. '
            'Do not claim a unique cause or guaranteed improvement. Preserve editability and group structure.\n'+json.dumps({'development_evidence':ctx['raw_evidence'],'initial_findings':{k:v for k,v in ctx.items() if k not in ['raw_evidence']},'M_stage2':decision,'probe_observations':observations},ensure_ascii=False))
    images=[ev/'reference.png',ev/'final.png']+[Path(o['image']) for o in observations if o['image']]
    patch=saved_call(prompt,dest/'coding',images,'shared_H_patch',PATCH)
    pilot.validate_source(patch['policy'],'policy.py')
    if any(tag in patch['system'] for tag in ['commons_','/srv/','/home/']):raise ValueError('Per-task or server-specific H prompt')
    hd=dest/'H';hd.mkdir(exist_ok=True)
    for key,name in [('policy','policy.py'),('system','system.txt')]:
        (hd/name).write_text(patch[key])
        original=(ROOT/'fixed_h/r1_C2'/name).read_text()
        (dest/(name+'.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),patch[key].splitlines(True),fromfile='H_start/'+name,tofile='candidate/'+name)))
    write(dest/'candidate.json',{'status':'generated','H_version':str(hd.relative_to(ROOT)),'M_version':'engineered_v2_4','type':'H-only','patch_reason':patch['reason'],'observation_used':patch['observation_used'],'scope':patch['scope'],'created':time.time()})


def freeze():
    assert not (ROOT/'configs/freeze.json').exists()
    smoke=read(ROOT/'tasks/smoke/active/stage1.json')
    obs=read(ROOT/'tasks/smoke/active/observations.json')
    assert smoke['plan']['probes'] and any(o['status']=='completed' for o in obs)
    assert len({h['module'] for h in smoke['context']['hypotheses']})>=2
    cfg=pilot.config();cfg['pilot']['status']='formal_frozen';write(ROOT/'config.json',cfg)
    write(ROOT/'configs/freeze.json',{'time':time.time(),'formal_tasks':['task01','task02'],'methods':METHODS,
        'proposals_per_task_arm':1,'maximum_probes':2,'H_start':'fixed_h/r1_C2','original_H0':'fixed_h/H0',
        'model':'gpt-6.1-sol medium; gpt-6-astra medium','calls_per_arm_research':2,
        'formal_upper_cli':12+16*3,'preparation_cli':pilot.current()['cli_sessions'],'cap':80,
        'frames_upper':150,'frame_cap':240,'render':'Cycles16 seed42 AgX 512longedge CPU2threads',
        'inner_budget':cfg['budget'],'CLI_timeout':300,'build_and_render_timeout':'min(600,remaining_scene_seconds)',
        'primary':'Absolute execution/required functional gates pass, Selection Q improves by >0.01, transfer execution/function pass and transfer Q does not drop >0.01. Report stronger transfer Q improvement separately.',
        'candidate_selection':'H_start fallback always; single candidate must be eligible on source Selection and improve Q >0.01. No transfer data returned before all candidates are frozen.',
        'failure_raw_metrics':None,'failure_utility':0,'remote_seed':None,'new_blind_test':False,
        'cost_forecast':'16 fresh 600s reconstruction envelopes <=160min plus CLI research/CPU evaluation; measured smoke stored separately. No automatic retry or extra repair.',
        'scope':'Two natural-image development tasks, two other real scenes for transfer, one proposal/arm. Not independent RSI repeats, no M auto evolution, no full baseline evolution.'})
    snap=ROOT/'code_snapshots/formal_frozen';snap.mkdir(parents=True)
    for name in ['experiment.py','meta.py','pilot.py','inspect_blend.py','regression.py','config.json']:
        shutil.copy2(ROOT/name,snap/name)
    shutil.copytree(ROOT/'backend',snap/'backend',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT/'fixed_h',snap/'fixed_h')


def evaluation(task_id,method,role,source):
    task=read(ROOT/'tasks'/task_id/'task.json');scene=task[role]
    return pilot.run_scene(method,task_id,'H_start' if method=='reference' else 'C1',scene,source,parent='fixed_h/r1_C2',meta='engineered_v2_4')


def run(smoke=False):
    if smoke:
        propose('smoke','active')
        evaluation('smoke','active','source',ROOT/'tasks/smoke/active/H')
        write(ROOT/'configs/smoke_cost.json',{'ledger':pilot.current(),'record':list((ROOT/'results/smoke').rglob('record.json'))[0].read_text()})
        return
    read(ROOT/'configs/freeze.json')
    for index, task_id in enumerate(['task01','task02']):
        for method in METHODS[index:]+METHODS[:index]:
            dest=ROOT/'tasks'/task_id/method
            try:propose(task_id,method)
            except (ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
                write(dest/'failure.json',{'status':'failed','phase':'proposal','error':str(error)})
            print('proposal',task_id,method,pilot.current()['cli_sessions'],flush=True)
    write(ROOT/'configs/all_candidates_frozen.json',{'time':time.time(),'candidates':[str(p.relative_to(ROOT)) for p in (ROOT/'tasks').glob('task*/*/candidate.json')]})
    # Selection first. All selected versions fixed before any fresh transfer results.
    selections=[]
    for task_id in ['task01','task02']:
        baseline=evaluation(task_id,'reference','source',ROOT/'fixed_h/r1_C2')
        for method in METHODS:
            hd=ROOT/'tasks'/task_id/method/'H'
            if not (hd/'policy.py').exists():
                selections.append({'task_id':task_id,'method':method,'selected':'H_start','reason':'No executable candidate'});continue
            row=evaluation(task_id,method,'source',hd)
            selected=pilot.eligible_scene(row) and (not pilot.eligible_scene(baseline) or row['metrics']['overall']>baseline['metrics']['overall']+.01)
            selections.append({'task_id':task_id,'method':method,'selected':'C1' if selected else 'H_start','candidate_eligible':pilot.eligible_scene(row),'baseline_eligible':pilot.eligible_scene(baseline),'source_Q':row['metrics']['overall'],'baseline_Q':baseline['metrics']['overall']})
    write(ROOT/'configs/selection_freeze.json',{'time':time.time(),'selections':selections,'test_not_used':True})
    for task_id in ['task01','task02']:
        evaluation(task_id,'reference','transfer',ROOT/'fixed_h/r1_C2')
        for method in METHODS:
            hd=ROOT/'tasks'/task_id/method/'H'
            if (hd/'policy.py').exists():evaluation(task_id,method,'transfer',hd)
    write(ROOT/'FINAL_STATUS.json',{'phase':'all_scheduled_terminal','tasks':2,'arms':6,'M_automatic_descendants':0,'ledger':pilot.current()})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','smoke','freeze','pilot','resume']);args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='freeze':freeze()
    elif args.action=='resume' and (ROOT/'FINAL_STATUS.json').exists():print('All scheduled jobs terminal; use analyze.py for offline report.')
    else:run(args.action=='smoke')
