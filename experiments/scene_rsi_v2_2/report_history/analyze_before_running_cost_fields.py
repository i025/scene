"""Offline summaries and figures from saved measurements; never invokes a model."""
from pathlib import Path
import csv
import json
import statistics
import argparse
import html
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)


def read(path):
    return json.loads(path.read_text())


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))


def table(path,rows):
    if not rows:return
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader()
        writer.writerows([{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else 'null' if v is None else v for k,v in row.items()} for row in rows])


def average(values):
    return statistics.mean(values) if values else None


def calls(folder):
    sessions=[read(p) for p in folder.glob('student_calls/*/session.json')]
    return {'cli_sessions':len(sessions),'known_input_tokens':sum(s['input_tokens'] or 0 for s in sessions),
            'known_output_tokens':sum(s['output_tokens'] or 0 for s in sessions),
            'usage_unknown_sessions':sum(s['total_tokens'] is None for s in sessions),
            'cli_seconds':sum(s['seconds'] for s in sessions if 'seconds' in s)}


def measured_rows():
    rows=[]
    for job in read(ROOT/'configs/A_schedule.json'):
        folder=ROOT/'results'/job['run_id']/'fixed_h'/job['candidate_id']/'fixed_version_test'/job['scene_id']
        record=read(folder/'record.json') if (folder/'record.json').exists() else None
        row={k:job[k] for k in ['job_id','scene_id','run_id','candidate_id','status']}
        row.update(method='fixed_h',split='fixed_version_test',Q=None,psnr=None,ssim=None,lpips=None,dino=None,
                   execution_success=None,functional_pass=None,utility=None,seconds=None,device='CPU',
                   cli_sessions=None,known_input_tokens=None,known_output_tokens=None,usage_unknown_sessions=None,cli_seconds=None,
                   checks=None,failure_type=None,meshes=None,vertices=None,polygons=None,boolean_started=0,boolean_completed=0,
                   scene_build_seconds=None,render_seconds=None,blender_executions=0,final_image=None,folder=str(folder.relative_to(ROOT)))
        if record:
            row.update(Q=record['metrics']['overall'],psnr=record['metrics']['psnr'],ssim=record['metrics']['ssim'],lpips=record['metrics']['lpips'],dino=record['metrics']['dino'],
                       execution_success=record['metrics']['valid'],functional_pass=record['functional']['functional_pass'],
                       utility=record['task_utility_v2'],seconds=record['seconds'],checks=record['functional']['checks'],
                       failure_type=record['failure_type'],**calls(folder))
            if record['metrics']['valid']:row['final_image']=str((folder/'final.png').relative_to(ROOT))
            row['blender_executions']=len(list(folder.glob('steps/*/build.py')))
            builds=[];renders=[]
            for path in sorted(folder.glob('steps/*/stage_events.jsonl')):
                events=[json.loads(s) for s in path.read_text().splitlines()]
                row['boolean_started']+=sum(e['stage']=='boolean_started' for e in events)
                row['boolean_completed']+=sum(e['stage']=='boolean_completed' for e in events)
                times={e['stage']:e['time'] for e in events}
                if 'scene_build_completed' in times:builds.append(times['scene_build_completed']-times['scene_build_started'])
                if 'render_completed' in times:renders.append(times['render_completed']-times['render_started'])
                built=[e for e in events if e['stage']=='scene_built']
                if built:row.update({k:built[-1][k] for k in ['meshes','vertices','polygons']})
            row['scene_build_seconds']=sum(builds) if builds else None
            row['render_seconds']=sum(renders) if renders else None
        rows.append(row)
    return rows


def summarize(rows):
    result={}
    for h in ['H0','r1_C2']:
        all_rows=[r for r in rows if r['candidate_id']==h]
        terminal=[r for r in all_rows if r['status'] in ['completed','failed','timeout','invalid']]
        valid=[r for r in terminal if r['execution_success']]
        result[h]={'scheduled':len(all_rows),'terminal':len(terminal),'not_started':sum(r['status']=='not_started' for r in all_rows),
                   'running':sum(r['status']=='running' for r in all_rows),'successes':len(valid),'failed':len(terminal)-len(valid),
                   'success_rate_all_scheduled':len(valid)/len(all_rows) if len(terminal)==len(all_rows) else None,
                   'functional_passes':sum(r['functional_pass'] is True for r in terminal),
                   'functional_rate_all_scheduled':sum(r['functional_pass'] is True for r in terminal)/len(all_rows) if len(terminal)==len(all_rows) else None,
                   'conditional_Q':average([r['Q'] for r in valid]),
                   'utility_all_scheduled':average([r['utility'] for r in terminal]) if len(terminal)==len(all_rows) else None,
                   'cli_sessions':sum(r['cli_sessions'] or 0 for r in terminal),'known_input_tokens':sum(r['known_input_tokens'] or 0 for r in terminal),
                   'known_output_tokens':sum(r['known_output_tokens'] or 0 for r in terminal),
                   'wall_seconds':sum(r['seconds'] or 0 for r in terminal),'blender_executions':sum(r['blender_executions'] for r in terminal),
                   'actual_SceneAct_booleans_completed':sum(r['boolean_completed'] for r in terminal)}
    pairs=[]
    for scene in read(ROOT/'manifest.json'):
        for run in ['r1','r2']:
            a=next(r for r in rows if r['scene_id']==scene['scene_id'] and r['run_id']==run and r['candidate_id']=='H0')
            b=next(r for r in rows if r['scene_id']==scene['scene_id'] and r['run_id']==run and r['candidate_id']=='r1_C2')
            pairs.append({'scene_id':scene['scene_id'],'run_id':run,'H0_success':a['execution_success'],'C2_success':b['execution_success'],
                          'H0_Q':a['Q'],'C2_Q':b['Q'],
                          'paired_Q_difference':b['Q']-a['Q'] if a['execution_success'] and b['execution_success'] else None,
                          'utility_difference':b['utility']-a['utility'] if a['utility'] is not None and b['utility'] is not None else None})
    result['pairs']={'both_success_n':sum(p['paired_Q_difference'] is not None for p in pairs),
                     'conditional_paired_Q_difference':average([p['paired_Q_difference'] for p in pairs if p['paired_Q_difference'] is not None]),
                     'unit':'6 physical source scenes, each 2 stochastic CLI repetitions; not 12 independent scenes'}
    return result,pairs


def tile(canvas,box,path,label):
    x,y,w,h=box
    if path and Path(path).exists():
        with Image.open(path) as src:
            im=src.convert('RGB');im.thumbnail((w-8,h-52));canvas.paste(im,(x+(w-im.width)//2,y))
    draw=ImageDraw.Draw(canvas)
    for i,line in enumerate(label.split('\n')):draw.text((x+4,y+h-46+i*16),line[:41],font=FONT,fill='black')


def figures(rows,summary,pairs):
    scenes=read(ROOT/'manifest.json');canvas=Image.new('RGB',(1250,len(scenes)*230+40),'white')
    ImageDraw.Draw(canvas).text((8,8),'All frozen A scenes; empty cells retain failure / pending status. Q is conditional.',font=FONT,fill='black')
    for i,s in enumerate(scenes):
        tile(canvas,(0,40+i*230,250,230),s['image_path'],s['scene_id']+'\nReference')
        for j,(h,run) in enumerate([('H0','r1'),('r1_C2','r1'),('H0','r2'),('r1_C2','r2')],1):
            r=next(r for r in rows if r['scene_id']==s['scene_id'] and r['candidate_id']==h and r['run_id']==run)
            q=f"{r['Q']:.4f}" if r['Q'] is not None else 'null'
            tile(canvas,(j*250,40+i*230,250,230),ROOT/r['final_image'] if r['final_image'] else None,f"{h} {run}: {r['status']}\nQ={q}; func={r['functional_pass']}")
    canvas.save(ROOT/'figures/figure1_all_A_scenes.png')
    fig,axes=plt.subplots(1,4,figsize=(14,3.5))
    for i,h in enumerate(['H0','r1_C2']):
        d=summary[h];group=[r for r in rows if r['candidate_id']==h]
        for ax,key,num in [(axes[0],'success_rate_all_scheduled','successes'),(axes[1],'functional_rate_all_scheduled','functional_passes')]:
            if d[key] is not None:
                ax.bar(i,d[key],width=.5);ax.text(i,d[key]+.02,f"{d[num]}/{d['scheduled']}",ha='center')
        q=[r['Q'] for r in group if r['Q'] is not None]
        axes[2].scatter([i+(j-len(q)/2)*.012 for j in range(len(q))],q,s=22)
        if d['conditional_Q'] is not None:axes[2].plot([i-.15,i+.15],[d['conditional_Q']]*2,'k-')
        u=[r['utility'] for r in group if r['utility'] is not None]
        axes[3].scatter([i+(j-len(u)/2)*.012 for j in range(len(u))],u,s=22)
    for pair in pairs:
        if pair['paired_Q_difference'] is not None:
            axes[2].plot([0,1],[pair['H0_Q'],pair['C2_Q']],color='grey',alpha=.35,linewidth=.8)
    for ax,title in zip(axes,['Execution success (all scheduled)','Required functional gates','Conditional Q (raw points)','Utility (failure=0, distinct field)']):
        ax.set_title(title,fontsize=9);ax.set_xticks([0,1],['H0','r1/C2']);ax.set_ylim(-.04,1.15);ax.grid(axis='y',alpha=.2)
    fig.suptitle(f"6 source scenes x 2 repetitions; both-success pairs n={summary['pairs']['both_success_n']}",fontsize=11)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure2_execution_quality.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for h in ['H0','r1_C2']:
        group=[r for r in rows if r['candidate_id']==h and r['utility'] is not None]
        x=[];y=[];n=0;total=0
        for r in group:n+=r['cli_sessions'];total+=r['utility'];x.append(n);y.append(total/len(x))
        axes[0].plot(x,y,'o-',label=h)
        axes[1].scatter([r['seconds'] for r in group],[r['utility'] for r in group],label=h)
    axes[0].set(xlabel='Cumulative CLI sessions',ylabel='Mean task utility',title='Frozen order, CPU only')
    axes[1].set(xlabel='Reconstruction + external checks (seconds)',ylabel='Task utility',title='All terminal tasks')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure5_A_cost.png',dpi=160);plt.close(fig)


def main():
    rows=measured_rows();summary,pairs=summarize(rows)
    save(ROOT/'metrics/A_scene_metrics.json',rows);table(ROOT/'metrics/A_scene_metrics.csv',rows)
    save(ROOT/'metrics/A_summary.json',summary);table(ROOT/'metrics/A_paired_metrics.csv',pairs)
    figures(rows,summary,pairs)
    audit_tables()
    diagnosis_analysis()
    report(rows,summary,pairs)
    print(json.dumps(summary,indent=2))


def audit_tables():
    from diagnostics import failure_evidence
    failures=[];full=[];call_rows=[]
    for path in sorted((ROOT/'results').glob('r*/fixed_h/*/fixed_version_test/*/record.json')):
        record=read(path);evidence=failure_evidence(record)
        full.append({'run_id':record['run_id'],'candidate_id':record['candidate_id'],'scene_id':record['scene_id'],'evidence':evidence})
        failures.append({'run_id':record['run_id'],'candidate_id':record['candidate_id'],'scene_id':record['scene_id'],
            'original_failure_type':record['failure_type'],'classified_category':evidence['category'],
            'last_observed_stage':evidence['last_observed_stage'],'outer_budget_exhausted':evidence['outer_budget_exhausted'],
            'seconds':record['seconds'],'scope':'Post-run B classifier; original measurements unchanged'})
    save(ROOT/'metrics/A_failure_evidence.json',full);table(ROOT/'metrics/A_failure_stages.csv',failures)
    for path in sorted(ROOT.rglob('session.json')):
        if not path.with_name('request.json').exists():continue
        s=read(path);confirmed=s['actual_model'] if s.get('actual_model_source')=='CLI JSON event' else None
        call_rows.append({'path':str(path.relative_to(ROOT)),'role':s['role'],'requested_model':s['requested_model'],
            'effort':s['reasoning_effort'],'status':s['status'],'CLI_sessions':1,
            'CLI_reported_model':s['actual_model'],'confirmed_returned_model':confirmed,
            'observable_CLI_turns':s.get('observable_cli_turns'),'underlying_model_rounds':None,
            'input_tokens':s['input_tokens'] if isinstance(s['input_tokens'],int) else None,
            'output_tokens':s['output_tokens'] if isinstance(s['output_tokens'],int) else None,
            'total_tokens':s['total_tokens'] if isinstance(s['total_tokens'],int) else None,
            'tool_calls':s.get('tool_calls'),'seconds':s.get('seconds'),'exit_code':s.get('exit_code'),
            'device':'CPU; remote model compute unobserved'})
    table(ROOT/'metrics/calls.csv',call_rows);save(ROOT/'metrics/calls.json',call_rows)
    from collections import Counter
    save(ROOT/'metrics/call_totals.json',{'actual_CLI_sessions':len(call_rows),
        'known_input_tokens':sum(r['input_tokens'] or 0 for r in call_rows),
        'known_output_tokens':sum(r['output_tokens'] or 0 for r in call_rows),
        'usage_unknown_sessions':sum(r['total_tokens'] is None for r in call_rows),
        'by_role':dict(Counter(r['role'] for r in call_rows)),
        'actual_returned_model_note':'Unknown unless separately exposed in a CLI JSON event; a startup/request name is not backend routing proof',
        'extra_model_cost_usd':None})


def report(rows,summary,pairs):
    lines=['# Scene-RSI V2.2：固定 H 复验与诊断修复机制实验','',
           '本轮不继续多代 RSI，不生成新的 M 后代。实验 A 固定 V2.1 原始 H0 与真实 r1/C2；B/C 是工程修复后的诊断机制比较。','',
           '## 实验 A：全部预定任务','',
           '|H|预定|结束|执行成功|功能通过|成功条件 Q|全任务效用|CLI 会话|',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    def value(v):return 'pending/null' if v is None else f'{v:.6f}' if isinstance(v,float) else str(v)
    for h in ['H0','r1_C2']:
        d=summary[h];lines.append('|'+ '|'.join(map(value,[h,d['scheduled'],d['terminal'],d['successes'],d['functional_passes'],d['conditional_Q'],d['utility_all_scheduled'],d['cli_sessions']]))+'|')
    lines+=['',f"双方成功的配对数：{summary['pairs']['both_success_n']}；配对 Q 差：{value(summary['pairs']['conditional_paired_Q_difference'])}。",
            '统计单位为 6 个真实来源场景，每场景 2 次 CLI 随机重复；不能将 12 个重复当成 12 个独立场景。失败原始视觉指标为 null，零只用于独立 utility 字段。',
            '', '![全部场景](../figures/figure1_all_A_scenes.png)','![执行与质量](../figures/figure2_execution_quality.png)',
            '', '## 诊断机制与共享修复','']
    csummary=ROOT/'metrics/C_summary.json'
    if csummary.exists():
        lines+=['实际结果见 [C_summary.json](../metrics/C_summary.json) 与 [逐任务表](../metrics/C_diagnosis.csv)。',
                '```json',json.dumps(read(csummary),ensure_ascii=False,indent=2),'```']
    else:lines+=['pending：尚无完成的 B/C 对照结果；不绘制假定的诊断提升或元能力曲线。']
    lines+=['','## 解释边界','',
            '- H0 与 r1/C2 的 policy.py 相同；差异是共享 system.txt 的覆盖检查、复杂度规划和执行验证。本实验不能分离其中单条规则的因果收益。',
            '- 固定 H 复验的结果不能证明 RSI 搜索优于其他框架，也不能把收益归因于三维诊断。',
            '- B/C 源码由工程师修复，不是自动演化出的 M 后代；不存在 MetaImp 或跨代元能力提升结果。',
            '- 新 Commons 页面 ID 在旧收集/实验清单中未命中；本轮适用性接触检查已记录，未做重建驱动样本筛选，不宣称严格盲测。图像本身不提供真实三维几何真值。',
            '- 固定结构/编辑检查是机械操作与已声明部件关系，不等同自然语言编辑能力或自然图像真实三维恢复精度。',
            '- 只有 SceneAct Boolean 的真实开始/结束事件计为已观测操作；缺日志不推测次数。最终残留修饰器不代表已执行布尔次数。',
            '- 全部使用 CPU，两计算线程、单重任务；未使用 GPU。CLI 轮次不能当作底层模型推理轮数，实际返回模型未报告时 unknown。',
            '', '## 审查与重算','',
            'A 协议：protocol_A.md、configs/A_freeze.json；真实源版本：configs/source_versions.json；原始场景表：metrics/A_scene_metrics.csv；配对表：metrics/A_paired_metrics.csv。',
            'Figure1 按预先冻结的全部场景顺序和两重复展示，不挑赢家。Figure2/5 的数据源均为 A_scene_metrics.csv，生成脚本为 analyze.py。',
            '离线入口：analyze.py，仅读取现有文件并重算图表；不会调用模型、Blender 或 GPU。归档后的跨机器重算入口见仓库 scripts/offline_v2_2.py。',
            '![成本与效用](../figures/figure5_A_cost.png)']
    (ROOT/'reports/REPORT_ZH.md').write_text('\n'.join(lines)+'\n')
    pictures=['figure1_all_A_scenes.png','figure2_execution_quality.png','figure3_diagnosis_comparison.png','figure4_diagnostic_cases.png','figure5_A_cost.png','figure5_C_cost.png']
    body='<h1>Scene-RSI V2.2</h1><p>真实固定 H 复验与诊断修复。缺失结果保持 pending/null；不开展多代 M 演化。</p>'
    for name in pictures:
        if (ROOT/'figures'/name).exists():body+=f'<figure><img src="../figures/{name}" alt="{name}"><figcaption>{name}；来源 CSV/JSON 与脚本见中文报告。</figcaption></figure>'
    body+='<h2>中文报告</h2><pre>'+html.escape('\n'.join(lines))+'</pre>'
    body+='<p><a href="REPORT_ZH.md">Markdown 报告</a> | <a href="../metrics/A_scene_metrics.csv">A 原始指标 CSV</a> | <a href="../metrics/A_summary.json">A 汇总 JSON</a></p>'
    (ROOT/'reports/index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>Scene-RSI V2.2</title><style>body{max-width:1280px;margin:24px auto;font-family:sans-serif;padding:16px;background:#f7f8fa;color:#17212b}img{max-width:100%}figure{margin:24px 0;padding:16px;background:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:20px}a{color:#1656b0}</style>'+body+'</html>')


"""Functions appended to the existing V2.2 offline analyzer after experiment A."""


def diagnosis_analysis():
    truth_path=ROOT/'diagnosis/ground_truth_evaluator_only.json'
    if not truth_path.exists():return
    truth=read(truth_path);rows=[]
    for item in truth:
        case=item['scene_id'];folder=ROOT/'diagnosis'/case
        for method in ['v2_1_fixed','v2_2_evidence']:
            dest=folder/method;result=read(dest/'result.json') if (dest/'result.json').exists() else None
            stage1=read(dest/'stage1.json')['decision'] if (dest/'stage1.json').exists() else None
            stage2=read(dest/'stage2.json')['decision'] if (dest/'stage2.json').exists() else None
            decision_change=read(dest/'stage2.json')['module_changed_by_observations'] if stage2 else None
            observations=read(dest/'observations.json') if (dest/'observations.json').exists() else None
            status=result['status'] if result else 'failed_dependency' if (folder/'common_localization_failure.json').exists() else 'running' if stage1 else 'not_started'
            probes=stage1['probes'] if stage1 else []
            target=probes[0]['object_id'] if probes else None
            module=probes[0]['code_module'] if probes else None
            measured=observations['probes'] if observations else []
            applicable=item['camera_object_applicable']
            final_module=stage2['shared_module'] if stage2 else None
            repair_calls=[read(p) for p in dest.glob('repair_call/session.json')]
            localizer_calls=[read(p) for p in (folder/'common_localization').glob('*/visual_call/session.json')]
            discriminated=[]
            for p in measured:
                delta=p['quality_delta'];alternatives=p['request']['alternatives']
                if delta is None or p['execution']['status']!='completed' or p['request']['probe']=='isolate':
                    discriminated.append(None);continue
                direction='improve' if delta>.005 else 'worsen' if delta<-.005 else 'unchanged'
                matched=[a for a in alternatives if a['predicted_direction']==direction]
                discriminated.append(len(matched)==1 and all(a['predicted_direction']!='unknown' for a in alternatives))
            terminal=status in ['completed','failed','timeout','invalid','failed_dependency']
            source=result['source_pass'] if result else None;transfer=result['transfer_pass'] if result else None
            ledger_paths=list(dest.rglob('render_ledger.json')) if dest.exists() else []
            frames=sum(read(p)['render_attempts'] for p in ledger_paths)
            row={'method':method,'run_id':case,'scene_id':case,'split':'controlled_diagnosis',
                 'candidate_id':'shared_helper_repair','parent_id':'injected_shared_H0',
                 'H_version':f'diagnosis/{case}/shared_h0.py','M_version':'V2.1 frozen M0' if method=='v2_1_fixed' else 'engineer-written V2.2',
                 'status':status,'fault_module_evaluator_only':item['fault_module'],'allowed_modules':item['allowed_modules'],
                 'target_object':target,'object_applicable':applicable,
                 'object_hit_top1':target in item['allowed_object_ids'] if stage1 and applicable else None,
                 'module_top1':module,'module_hit_top1':module in item['allowed_modules'] if stage1 else None,
                 'module_hit_any':any(p['code_module'] in item['allowed_modules'] for p in probes) if stage1 else None,
                 'final_module':final_module,'final_module_hit':final_module in item['allowed_modules'] if stage2 else None,
                 'final_module_related_hit':final_module in item['allowed_related_modules'] if stage2 else None,
                 'module_changed_by_observations':decision_change,
                 'probes_requested':len(probes) if stage1 else None,
                 'probes_executed':sum(p['execution']['status']=='completed' for p in measured) if observations else None,
                 'pre_prediction_discrimination':discriminated,
                 'source_repair_measured_pass':source,'transfer_measured_pass':transfer,
                 'source_repair_utility':float(source is True) if terminal else None,
                 'transfer_utility':float(transfer is True) if terminal else None,
                 'own_repair_cli_sessions':len(repair_calls),'shared_visual_sessions_seen':len(localizer_calls),
                 'allocated_cli_sessions':len(repair_calls)+len(localizer_calls)/2,
                 'known_own_input_tokens':sum(s['input_tokens'] or 0 for s in repair_calls),
                 'known_own_output_tokens':sum(s['output_tokens'] or 0 for s in repair_calls),
                 'own_usage_unknown':sum(s['total_tokens'] is None for s in repair_calls),
                 'shared_known_input_tokens':sum(s['input_tokens'] or 0 for s in localizer_calls),
                 'shared_known_output_tokens':sum(s['output_tokens'] or 0 for s in localizer_calls),
                 'own_cli_seconds':sum(s['seconds'] for s in repair_calls),
                 'own_render_attempts':frames,'device':'CPU',
                 'failure_reason':result['failure_reason'] if result and 'failure_reason' in result else None,
                 'folder':str(dest.relative_to(ROOT))}
            rows.append(row)
    summary={}
    for method in ['v2_1_fixed','v2_2_evidence']:
        group=[r for r in rows if r['method']==method]
        done=[r for r in group if r['status'] in ['completed','failed','timeout','invalid','failed_dependency']]
        d={'scheduled':len(group),'terminal':len(done),'not_started':sum(r['status']=='not_started' for r in group),
           'actual_repair_results':sum(r['source_repair_measured_pass'] is not None for r in group)}
        for key in ['object_hit_top1','module_hit_top1','module_hit_any','final_module_hit','final_module_related_hit','source_repair_measured_pass','transfer_measured_pass']:
            values=[r[key] for r in group if r[key] is not None]
            d[key]={'passed':sum(v is True for v in values),'measured_n':len(values),
                    'applicable_scheduled':sum(r['object_applicable'] for r in group) if key=='object_hit_top1' else len(group)}
        d.update(own_repair_cli_sessions=sum(r['own_repair_cli_sessions'] for r in group),
                 probes_requested=sum(r['probes_requested'] or 0 for r in group),
                 probes_executed=sum(r['probes_executed'] or 0 for r in group),
                 prediction_direction_discrimination={'passed':sum(v is True for r in group for v in r['pre_prediction_discrimination']),
                     'measured_n':sum(v is not None for r in group for v in r['pre_prediction_discrimination'])},
                 decision_changed_by_observations={'changed':sum(r['module_changed_by_observations'] is True for r in group),
                     'measured_n':sum(r['module_changed_by_observations'] is not None for r in group)},
                 shared_visual_sessions_seen=sum(r['shared_visual_sessions_seen'] for r in group),
                 allocated_cli_sessions=sum(r['allocated_cli_sessions'] for r in group),
                 own_render_attempts=sum(r['own_render_attempts'] for r in group),
                 source_utility_all_scheduled=average([r['source_repair_utility'] for r in done]) if len(done)==len(group) else None,
                 transfer_utility_all_scheduled=average([r['transfer_utility'] for r in done]) if len(done)==len(group) else None)
        summary[method]=d
    summary['interpretation']={'tasks':'10 parameterized rooms from two controlled template families, 5 fault types x2; not 10 natural scene samples',
        'localizer':'One common astra image call per case. Same output delivered to both fixed M programs; shared cost split equally only for accounting.',
        'repair':'One astra coding opportunity per arm/case with identical public API contract hints; any helper module may be repaired even if M is wrong/unresolved.',
        'discrimination':'Match to a unique pre-probe predicted Q direction among stated alternatives; not unique causal truth, isolation full-image Q excluded.',
        'transfer':'New helper parameters, geometry width, names and mesh/material sharing; not proof of natural-image reconstruction transfer or M self-improvement.'}
    save(ROOT/'metrics/C_diagnosis.json',rows);table(ROOT/'metrics/C_diagnosis.csv',rows)
    save(ROOT/'metrics/C_summary.json',summary)
    diagnosis_figures(rows,summary)


def diagnosis_figures(rows,summary):
    methods=['v2_1_fixed','v2_2_evidence']
    keys=['object_hit_top1','module_hit_top1','final_module_hit','source_repair_measured_pass','transfer_measured_pass']
    fig,axes=plt.subplots(1,5,figsize=(15,3.8))
    for ax,key in zip(axes,keys):
        for index,method in enumerate(methods):
            d=summary[method][key];n=d['measured_n']
            if n:ax.bar(index,d['passed']/n,width=.5);ax.text(index,d['passed']/n+.04,f"{d['passed']}/{n}",ha='center',fontsize=9)
            group=[r for r in rows if r['method']==method and r[key] is not None]
            ax.scatter([index+(i-len(group)/2)*.016 for i in range(len(group))],[int(r[key]) for r in group],s=18,color='black',alpha=.55)
        ax.set_title(key.replace('_',' '),fontsize=8);ax.set_xticks([0,1],['V2.1 M0','V2.2'],rotation=15);ax.set_ylim(-.08,1.28)
    fig.suptitle('Raw points + measured denominators; 10 scheduled tasks/arm, object N/A for 2 camera cases',fontsize=10)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure3_diagnosis_comparison.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for method in methods:
        group=[r for r in rows if r['method']==method and r['source_repair_utility'] is not None]
        x=[];y=[];cost=0;total=0
        for r in group:cost+=r['allocated_cli_sessions'];total+=r['source_repair_utility'];x.append(cost);y.append(total/len(x))
        axes[0].plot(x,y,'o-',label=method)
        axes[1].scatter([r['own_render_attempts'] for r in group],[r['source_repair_utility'] for r in group],label=method)
    axes[0].set(xlabel='Cumulative own + half common CLI sessions',ylabel='Source repair utility',title='Common visual cost allocated, never double-counted')
    axes[1].set(xlabel='Own probe + repair render attempts',ylabel='Source repair utility',title='CPU only; shared setup frames excluded here')
    for ax in axes:ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure5_C_cost.png',dpi=160);plt.close(fig)
    success=next((r for r in rows if r['method']=='v2_2_evidence' and r['final_module_hit'] is True and r['source_repair_measured_pass'] is True),None)
    failure=next((r for r in rows if r['final_module_hit'] is False or r['source_repair_measured_pass'] is False),None)
    selected=[r for r in [success,failure] if r]
    save(ROOT/'metrics/diagnostic_case_selection.json',{'rule':'First V2.2 correct final module + measured source repair; first actual wrong module or failed source repair across frozen case order. A wrong module may still be repaired by coder.',
         'selected':[{'scene_id':r['scene_id'],'method':r['method'],'final_module_hit':r['final_module_hit'],'repair_pass':r['source_repair_measured_pass']} for r in selected],
         'missing_failure':failure is None,'missing_success':success is None})
    if selected:
        canvas=Image.new('RGB',(1500,len(selected)*390),'white');draw=ImageDraw.Draw(canvas)
        for i,r in enumerate(selected):
            dest=ROOT/r['folder'];case=dest.parent
            probes=sorted((dest/'probes').glob('*/probe_*.png'))
            pictures=[case/'reference.png',case/'final.png',case/'common_localization/0/object_map.png',probes[0] if probes else None,dest/'source_repaired.png',dest/'transfer_repaired.png']
            for j,(picture,label) in enumerate(zip(pictures,['Reference','Faulty H','Actual object projection','Selected sensitivity probe','Repaired source','Independent helper transfer'])):
                tile(canvas,(j*250,i*390,250,240),picture,label+'\n'+r['scene_id']+' '+r['method'])
            text=f"{r['scene_id']} {r['method']}: target={r['target_object']}; stage1 module={r['module_top1']}; final={r['final_module']}; module correct={r['final_module_hit']}; repair={r['source_repair_measured_pass']}; transfer={r['transfer_measured_pass']}"
            draw.text((8,i*390+246),text,font=FONT,fill='black')
            obs=read(dest/'observations.json')
            draw.text((8,i*390+267),'Actual probe deltas: '+str([p['quality_delta'] for p in obs['probes']]),font=FONT,fill='black')
            diff=(dest/'changes.diff').read_text().splitlines() if (dest/'changes.diff').exists() else ['No code output']
            for n,line in enumerate(diff[:5]):draw.text((8,i*390+290+n*17),line[:170],font=FONT,fill='black')
        canvas.save(ROOT/'figures/figure4_diagnostic_cases.png')


if __name__=='__main__':main()
