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
TOOLS['camera_tilt']='Rotate camera upward by4degrees about its localX axis, fix geometry/lens. Tests pitch separately from focal length.'
TOOLS['object_depth']='Move the explicitly named real object/group center 10percent farther along its camera ray, preserve size and camera. Tests distance separately from size.'
for tool in TOOLS:TOOLS[tool]=TOOLS[tool].split('Outcome:')[0]+' Scalar for every tool: .5*global deltaSSIM+.5*fixed referenceROI deltaSSIM.'


def read(path): return json.loads(path.read_text())
write = pilot.write_json


def obj(properties):
    return {'type':'object', 'additionalProperties':False, 'properties':properties, 'required':list(properties)}


S = {'type':'string'}
INTERVAL = obj({'lower':{'type':'number'}, 'upper':{'type':'number'}, 'reason':S})
FINDINGS = obj({'visual_difference':S, 'object_id':S, 'reference_roi':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'number','minimum':0,'maximum':1}}, 'initial_module':{'type':'string','enum':MODULES},
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


def ssim(reference, render, roi=None):
    a, b = [np.asarray(Image.open(p).convert('RGB')) for p in [reference, render]]
    if roi:
        x0,y0,x1,y1=roi;h,w=a.shape[:2]
        a=a[round(y0*h):round(y1*h),round(x0*w):round(x1*w)]
        b=b[round(y0*h):round(y1*h),round(x0*w):round(x1*w)]
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
              'Choose a prominent discrepancy rather than a tiny incidental pixel feature. Supply reference_roi=[x0,y0,x1,y1] normalized bounds of its region in the photograph; minimum width/height .05. '
              'The scalar outcome for EVERY tool is .5*full_image_delta_SSIM+.5*reference_roi_delta_SSIM, with the SAME fixed ROI before and after intervention. This is an appearance sensitivity score, not geometry truth. '
              'Before experiments, predict an interval for this balanced scalar under EACH hypothesis. '
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
    x0,y0,x1,y1=findings['reference_roi']
    if x1-x0<.05 or y1-y0<.05:raise ValueError('Diagnostic ROI too small or inverted')
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
        observed={'request':request,'status':result['status'],'measurement':result,'delta_ssim':None,'delta_roi_ssim':None,'outcome':None,'image':None}
        if result['status']=='completed':
            full=ssim(ev/'reference.png',png)-ssim(ev/'reference.png',ev/'final.png')
            local=ssim(ev/'reference.png',png,ctx['reference_roi'])-ssim(ev/'reference.png',ev/'final.png',ctx['reference_roi'])
            observed.update(delta_ssim=full,delta_roi_ssim=local,outcome=.5*(full+local),image=str(png))
        observations.append(observed)
        ctx['remaining_probe_budget']-=1;ctx['already_executed_probe_count']+=1
        write(dest/'observations.json',observations)
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
    smoke=read(ROOT/'tasks/smoke_refined/active/stage1.json')
    obs=read(ROOT/'tasks/smoke_refined/active/observations.json')
    assert smoke['plan']['probes'] and any(o['status']=='completed' for o in obs)
    assert len({h['module'] for h in smoke['context']['hypotheses']})>=2
    smoke_records=list((ROOT/'results/smoke_refined').rglob('record.json'))
    assert len(smoke_records)==1 and read(smoke_records[0])['metrics']['valid']
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
    (ROOT/'protocol.md').write_text('''# Scene-RSI V2.4：正式对照执行前冻结协议

本轮先完成44项历史执行审计，再使用独立开发课堂案例修正对象ID契约和探测菜单。旧三工具烟测没有预测区分性，完整保留；没有通过降低阈值强迫探测。新增相机俯仰、对象深度干预以及固定局部ROI与全图SSIM的等权敏感性观测，已进行零模型物理控制及独立数值夹具校准。最新真实图像烟测实际执行探测，观测进入可执行meta.plan_patch，再产生共享H提案并完成重建/保存/渲染/数值评价。具体时间与预算见configs/freeze.json和configs/smoke_cost.json。

正式任务在探测前按来源类别指定：task01历史卧室诊断，厨房迁移；task02历史餐厅诊断，便携教室迁移。Goa课堂只作开发，不进入正式结果。所有图像均来自已公开的V2.2来源和历史重建，因此为exploratory，非全新盲测。没有注入正式故障、正确代码或模块标签，不能计算真实对象/模块定位准确率。选择规则不根据正式Active结果调整。两项任务不是两次独立RSI研发重复。

三组Fixed Diagnosis、Structured Evidence、Active3D Diagnosis都从fixed_h/r1_C2出发。它是V2.1已演化H，不冒充原始H0；原始H0另存fixed_h/H0，仅作出处记录。本轮不重跑SceneEvolve或Generic演化。每组一次独立gpt-6-astra medium初诊、一次独立相同模型编码；看到相同自然图像、历史P、H源码、数值及结构证据，无共同教师正确诊断。工具菜单一致、最多2次，Fixed固定焦距/尺度，Structured不用探测，Active由预测部分区分分数选择，阈值.15。不强制使用额度，各组实际成本另报，不声称实际计算量相等。M两阶段代码由工程师修订，未自动产生后代，不做元能力提升结论。

H只允许共享policy.py与system.txt修改，禁止逐图参数、任务ID、路径和答案硬编码。P由冻结内层生成并只作为证据，不能替代共享H候选。模型全部通过已有CLI真实图像附件、新会话、只读无工具；sol medium负责重建，astra medium负责初诊和共享程序修改。无额外视觉judge。请求模型和CLI返回model分别保留，缺失实际路由为unknown。远端采样不可固定。

正式6个候选，16个新重建任务（4项共同H_start、12项候选source/transfer）；每重建最多3CLI、2执行、600秒总时间，CLI单次300秒、执行取min(600,场景剩余时间)。不增加旧预算；共同Runtime修正为执行额度耗尽后不再请求不可执行的新程序。所有组和H_start相同。CPU单重任务、2线程，Cycles16samples、512长边、AgX、seed42，禁用GPU。探测与正式渲染质量相同；64像素校准明确排除。指标沿用V2.1 Q，由真实SSIM/LPIPS/DINOv2组成，权重复用本地缓存。

所有提案冻结后才新跑Selection；每项候选必须绝对满足执行、基础结构、局部机械材质非目标保持，以及任务必需的组合移动/已声明部件关系。required/applicable/measured_pass/gate_pass分别保存；必需缺测不通过。支撑近似、三角交叉为有适用边界的补充，未知语义完整性和真实几何不当作通过。没有三维真值或文字编辑评价，不宣称真实3D恢复精度或指令编辑能力。

候选资格通过且Q比H_start高>.01才在Selection接受，H_start始终回退；若H_start失败，合格候选可按执行恢复接受，不能取消候选绝对约束。先保存selection_freeze再统一迁移Test。原始候选也在迁移上评估，不能把未选中候选收益冒充选择后收益。严格有效共享修复要求源图执行/功能合规、源Q提高>.01，迁移执行/功能合规且Q下降不超过.01；另列迁移提高>.01的更强结果。原始失败视觉值null、独立失败零效用；未开始为pending/null。全部样本、失败和所有点保留，不把多个视角作为独立样本。

预测使用平滑残差更新，所有预测均不匹配时记录校准不足，不把它们全判作被证伪。观测是受控敏感性，不唯一因果归因。正式最多80次CLI、240渲染帧，包含所有开发失败、烟测、提案与修复；无自动服务重试。预算预估在freeze.json，不能按结果扩大。本轮没有多代搜索、M回放或论文优势验证。
''')


def evaluation(task_id,method,role,source):
    task=read(ROOT/'tasks'/task_id/'task.json');scene=task[role]
    return pilot.run_scene(method,task_id,'H_start' if method=='reference' else 'C1',scene,source,parent='fixed_h/r1_C2',meta='engineered_v2_4')


def run(smoke=False):
    if smoke:
        propose('smoke_refined','active')
        evaluation('smoke_refined','active','source',ROOT/'tasks/smoke_refined/active/H')
        write(ROOT/'configs/smoke_cost.json',{'ledger':pilot.current(),'record':list((ROOT/'results/smoke_refined').rglob('record.json'))[0].read_text()})
        return
    read(ROOT/'configs/freeze.json')
    for index, task_id in enumerate(['task01','task02']):
        for method in METHODS[index:]+METHODS[:index]:
            dest=ROOT/'tasks'/task_id/method
            try:propose(task_id,method)
            except (ValueError,SyntaxError,RuntimeError,subprocess.TimeoutExpired) as error:
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
