"""Offline summaries and figures from saved V2 measurements; no models or Blender."""
from pathlib import Path
import csv,json,html,difflib
import numpy as np
from PIL import Image,ImageOps,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def read(path,default=None):return json.loads(path.read_text()) if path.exists() else default

def csv_write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:return
    fields=list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) or v is None else v for k,v in row.items()})

def folder(row):return Path(row['alias_of'] if 'alias_of' in row else row['folder'])

def contact(rows,tests,dest):
    size=(300,240);canvas=Image.new('RGB',(930,len(tests)*285),'white');draw=ImageDraw.Draw(canvas)
    for i,scene in enumerate(tests):
        base=next((r for r in rows if r['scene_id']==scene['scene_id'] and r['method']=='fixed_h0'),None)
        ours=next((r for r in rows if r['scene_id']==scene['scene_id'] and r['method']=='scene_rsi_v2'),None)
        files=[Path(scene['image_path']),folder(base)/'final.png' if base else None,folder(ours)/'final.png' if ours else None]
        for j,path in enumerate(files):
            x=j*310;y=i*285
            if path and path.exists():canvas.paste(ImageOps.contain(Image.open(path).convert('RGB'),size),(x,y+35))
            else:draw.rectangle((x,y+35,x+300,y+275),fill='#eee');draw.text((x+8,y+100),'MISSING / NOT RUN',fill='black')
            label='Reference '+scene['scene_id'] if j==0 else ('H0' if j==1 else 'Selected H*')
            row=base if j==1 else ours if j==2 else None
            if row:label+=f" {row['candidate_id']} {row['status']} Q={round(row['metrics']['overall'],4) if row['metrics']['overall'] is not None else 'null'}"
            draw.text((x+4,y+5),label[:72],fill='black')
    canvas.save(dest)

def main():
    out=ROOT/'metrics';fig=ROOT/'figures';report=ROOT/'reports'
    for d in [out,fig,report]:d.mkdir(exist_ok=True)
    manifest=read(ROOT/'manifest.json',[]);archive=read(ROOT/'archive.json',[])
    rows=[read(p) for p in sorted((ROOT/'results').glob('*/*/*/*/*/record.json'))]
    calls=[read(p) for p in ROOT.rglob('session.json') if p.parent.joinpath('request.json').exists()]
    csv_write(out/'scene_metrics.csv',[{k:r.get(k) for k in ['method','run_id','candidate_id','scene_id','split','status','metrics','functional','task_utility_v2','failure_type','device','seconds','usage','H_version','M_version','alias_of']} for r in rows])
    scheduled=[next((a for a in archive if a['run_id']==rid and a['candidate_id']==f'C{k}'),{'method':'scene_rsi_v2','run_id':rid,'candidate_id':f'C{k}','status':'not_started','accepted':None}) for k in [1,2] for rid in ['r1','r2']]
    csv_write(out/'candidates.csv',scheduled)
    slots=[]
    for rid in ['r1','r2']:
        for method,cid,scenes in [('fixed_h0','H0',manifest)]+[('scene_rsi_v2',f'C{k}',[q for q in manifest if q['split']!='test']) for k in [1,2]]:
            for scene in scenes:
                row=next((r for r in rows if r['run_id']==rid and r['method']==method and r['candidate_id']==cid and r['scene_id']==scene['scene_id']),None)
                candidate=next((a for a in scheduled if a['run_id']==rid and a['candidate_id']==cid),None)
                slots.append({'method':method,'run_id':rid,'candidate_id':cid,'scene_id':scene['scene_id'],'split':scene['split'],'status':row['status'] if row else 'not_produced_candidate' if candidate and candidate['status']=='proposal_failed' else 'not_started_or_running','metrics':row['metrics'] if row else None,'failure_reason':candidate.get('error') if candidate else None})
    frozen_choices=read(ROOT/'selection_freeze.json',{}).get('choices',[])
    for rid in ['r1','r2']:
        selected=next((c for c in frozen_choices if c['run_id']==rid and c['method']=='scene_rsi_v2'),None)
        for scene in [q for q in manifest if q['split']=='test']:
            row=next((r for r in rows if r['run_id']==rid and r['method']=='scene_rsi_v2' and r['split']=='test' and r['scene_id']==scene['scene_id'] and selected and r['candidate_id']==selected['candidate_id']),None)
            slots.append({'method':'scene_rsi_v2','run_id':rid,'candidate_id':selected['candidate_id'] if selected else 'selection_pending','scene_id':scene['scene_id'],'split':'test','status':row['status'] if row else 'not_started_or_running','metrics':row['metrics'] if row else None,'failure_reason':None})
    csv_write(out/'scheduled_slots.csv',slots)

    csv_write(out/'calls.csv',[{k:c.get(k) for k in ['role','requested_model','actual_model','actual_model_source','reasoning_effort','status','exit_code','seconds','input_tokens','output_tokens','total_tokens','observable_cli_turns','observable_model_turns','tool_calls','call_dir','error','started','finished']} for c in calls])
    choices=read(ROOT/'selection_freeze.json',{}).get('choices',[])
    terminal=[r for r in rows if r['split']=='test' and any(all(r[k]==c[k] for k in ['method','run_id','candidate_id']) for c in choices)]
    summary=[]
    for rid in ['r1','r2']:
        for method in ['fixed_h0','scene_rsi_v2']:
            data=[r for r in terminal if r['method']==method and r['run_id']==rid];valid=[r for r in data if r['status']=='complete'];n=sum(s['split']=='test' for s in manifest)
            summary.append(dict(run_id=rid,method=method,scheduled=n,recorded=len(data),completed=len(valid),execution_success_rate=len(valid)/n if n else None,
                 conditional_Q=np.mean([r['metrics']['overall'] for r in valid]).item() if valid else None,
                 task_utility_v2=sum(r['metrics']['overall'] for r in valid)/n if len(data)==n and n else None,
                 functional_passes=sum(r['functional']['functional_pass'] for r in data),failed=sum(r['status']=='failed' for r in data),not_run=n-len(data)))
    csv_write(out/'terminal_summary.csv',summary)
    paired=[]
    for rid in ['r1','r2']:
        for scene in [s for s in manifest if s['split']=='test']:
            pair=[next((r for r in terminal if r['run_id']==rid and r['method']==m and r['scene_id']==scene['scene_id']),None) for m in ['fixed_h0','scene_rsi_v2']]
            a,b=pair
            paired.append(dict(run_id=rid,scene_id=scene['scene_id'],both_completed=bool(a and b and a['status']==b['status']=='complete'),quality_difference=b['metrics']['overall']-a['metrics']['overall'] if a and b and a['status']==b['status']=='complete' else None,
                utility_difference=b['task_utility_v2']-a['task_utility_v2'] if a and b else None,
                complete_effective_improvement=bool(a and b and a['status']==b['status']=='complete' and b['functional']['functional_pass'] and b['metrics']['overall']>a['metrics']['overall']+.01) if a and b else None))
    csv_write(out/'paired_test.csv',paired)
    if choices:
      for rid in ['r1','r2']:contact([r for r in terminal if r['run_id']==rid],[s for s in manifest if s['split']=='test'],fig/f'figure1_{rid}.png')
    plt.rcParams.update({'font.size':9})
    f,axes=plt.subplots(1,3,figsize=(12,3.5))
    for i,method in enumerate(['fixed_h0','scene_rsi_v2']):
        points=[r for r in terminal if r['method']==method and r['status']=='complete'];axes[0].scatter([i]*len(points),[r['metrics']['overall'] for r in points],alpha=.5,label=method)
        groups=[s for s in summary if s['method']==method];axes[1].bar([i*3+k for k in range(2)],[s['functional_passes']/s['scheduled'] if s['recorded']==s['scheduled'] else np.nan for s in groups],label=method)
    axes[0].set(xticks=[0,1],xticklabels=['H0','Selected'],ylabel='Conditional Q (individual scene/run points)')
    axes[1].set(ylabel='Functional passes / all scheduled',xticks=[])
    counts={s:sum(c['status']==s for c in calls) for s in ['complete','failed','running']};axes[2].bar(list(counts),list(counts.values()));axes[2].set(ylabel='CLI sessions, all stages')
    f.tight_layout();f.savefig(fig/'statistics.png',dpi=160);plt.close(f)
    f,ax=plt.subplots(figsize=(8,4))
    for rid in ['r1','r2']:
        baseline=[r for r in rows if r['run_id']==rid and r['method']=='fixed_h0' and r['split']=='selection'];q=sum(r['task_utility_v2'] for r in baseline)/len(baseline) if baseline else None
        entries=sorted([a for a in archive if a['run_id']==rid and a['status']=='evaluated'],key=lambda a:int(a['candidate_id'][1:]))
        xs=[0]+[int(a['candidate_id'][1:]) for a in entries];ys=[q]+[a['selection']['endpoint_quality'] for a in entries]
        ax.plot(xs,ys,'o:',label=rid+' raw candidate')
        retained=[q]
        for a in entries:retained.append(a['selection']['endpoint_quality'] if a['accepted'] else retained[-1])
        ax.plot(xs,retained,'s-',label=rid+' retained H*')
        for a,x,y in zip(entries,xs[1:],ys[1:]):ax.annotate(f"{a['candidate_id']} {a['candidate_type']} accept={a['accepted']}\nCLI={a['ledger_after']['cli_sessions']}",(x,y),fontsize=7)
    ax.set(xlabel='Actual candidate index (raw Selection performance)',ylabel='End-to-end Q utility; failure=0');ax.legend();f.tight_layout();f.savefig(fig/'figure4_evolution.png',dpi=160);plt.close(f)
    calibration=read(ROOT/'tests/calibration.json',{})
    cal_rows=[]
    specs=[('correct','hierarchy_parts','measured_pass'),('detached','hierarchy_parts','measured_pass'),('missing_declared_part','hierarchy_parts','measured_pass'),('broken_support','known_support','measured_pass'),('shared_material_bad_edit',None,'pass'),('independent_local_edit',None,'measured_pass'),('correct_group_move',None,'measured_pass'),('triangle_crossing','mesh_intersection','measured_pass')]
    for case,test,key in specs:
        if case in calibration:
            entry=calibration[case] if test is None else calibration[case][test]
            cal_rows.append({'fixture':case,'check':test,'measured_pass':entry[key]})
    csv_write(out/'calibration_checks.csv',cal_rows)
    if cal_rows:
        f,ax=plt.subplots(figsize=(9,3.8));ax.barh([r['fixture'] for r in cal_rows],[1 for r in cal_rows],color=['#37966f' if r['measured_pass'] else '#c74343' for r in cal_rows])
        for i,r in enumerate(cal_rows):ax.text(.1,i,'MEASURED PASS' if r['measured_pass'] else 'MEASURED FAIL (injected error)',va='center',color='white')
        ax.set(xticks=[],title='Known fixtures: actual check outcomes, not reconstruction accuracy');f.tight_layout();f.savefig(fig/'figure3_calibration.png',dpi=160);plt.close(f)
    # Observable development costs; no invented prices or remote inference-round counts.
    cost_points=[]
    for rid in ['r1','r2']:
        entries=sorted([a for a in archive if a['run_id']==rid and a['status']=='evaluated'],key=lambda a:int(a['candidate_id'][1:]))
        best=None
        for a in entries:
            k=int(a['candidate_id'][1:]);included=[]
            for c in calls:
                path=Path(c['call_dir']);parts=path.parts
                if rid not in parts:continue
                if 'results' in parts:
                    index=parts.index('results');candidate=parts[index+3];split=parts[index+4]
                    if split not in ['development','selection']:continue
                    if candidate!='H0' and int(candidate[1:])>k:continue
                elif 'candidates' in parts:
                    index=parts.index('candidates');candidate=parts[index+3]
                    if int(candidate[1:])>k:continue
                else:continue
                included.append(c)
            quality=a['selection']['endpoint_quality']
            if best is None:
                baseline=[r for r in rows if r['method']=='fixed_h0' and r['run_id']==rid and r['split']=='selection'];best=sum(r['task_utility_v2'] for r in baseline)/len(baseline) if baseline else None
            if a['accepted']:best=quality
            cost_points.append({'run_id':rid,'candidate_id':a['candidate_id'],'cli_sessions_cumulative':len(included),'known_input_tokens':sum(c['input_tokens'] for c in included if isinstance(c.get('input_tokens'),int)),'known_output_tokens':sum(c['output_tokens'] for c in included if isinstance(c.get('output_tokens'),int)),'usage_unknown_sessions':sum(c.get('total_tokens') is None for c in included),'selected_utility':best,'candidate_utility':quality,'H_accepted':a['accepted']})
    csv_write(out/'development_cost_points.csv',cost_points)
    if cost_points:
        f,ax=plt.subplots(figsize=(8,4))
        for rid in ['r1','r2']:
            points=[p for p in cost_points if p['run_id']==rid];ax.plot([p['cli_sessions_cumulative'] for p in points],[p['selected_utility'] for p in points],'o-',label=rid+' retained')
            ax.scatter([p['cli_sessions_cumulative'] for p in points],[p['candidate_utility'] for p in points],marker='x',label=rid+' candidate')
        ax.set(xlabel='Cumulative CLI sessions within research run (H0 + proposals + Dev/Selection)',ylabel='Selection Q utility');ax.legend();f.tight_layout();f.savefig(fig/'cost_gain.png',dpi=160);plt.close(f)
    stages=sorted((ROOT/'candidates').glob('r*/scene_rsi_v2/C*/stage2.json'))
    diagnostic=None
    if not stages:stages=sorted((ROOT/'candidates').glob('smoke*/scene_rsi_v2/C*/stage2.json'))
    if stages:
        path=stages[0];trace=read(path);observations=trace['observations']['probes'];dest=path.parent
        images=[]
        sid=trace['context_after_execution']['development'][0]['scene_id']
        for entry in trace['context_after_execution']['development']:
            if observations and entry['scene_id']==observations[0]['request']['scene_id']:sid=entry['scene_id'];images=entry['attached_images']
        probes=list(dest.glob('probes/*/probe_*.png'));pictures=[Path(p) for p in images]+probes
        canvas=Image.new('RGB',(max(1,len(pictures))*270,330),'white');d=ImageDraw.Draw(canvas)
        for i,p in enumerate(pictures):
            if p.exists():canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(260,240)),(i*270,30))
            d.text((i*270+4,4),['Reference','Reconstruction'][i] if i<2 else p.stem,fill='black')
        d.text((6,280),str([(o['request']['object_id'],o['quality_delta']) for o in observations])[:170],fill='black');d.text((6,305),trace['decision']['shared_module'][:160],fill='black');canvas.save(fig/'figure2_diagnostic.png')
        diagnostic={'trace':str(path.relative_to(ROOT)),'scene':sid,'decision':trace['decision'],'probes':observations,'diff':str((dest/'changes.diff').relative_to(ROOT)) if (dest/'changes.diff').exists() else None,'phase':'smoke_excluded_from_formal' if 'smoke' in str(path) else 'formal'}
    # Actual mechanical before/after, not a language-edit claim.
    measured=next((r for r in terminal if (folder(r)/'functional/before.png').exists()),None)
    if measured is None:measured=next((r for r in rows if r['split']=='smoke' and (folder(r)/'functional/before.png').exists()),None)
    if measured:
        canvas=Image.new('RGB',(930,310),'white');d=ImageDraw.Draw(canvas)
        for i,name in enumerate(['before.png','after_material.png','after_move.png']):
            p=folder(measured)/'functional'/name
            if p.exists():canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(300,250)),(i*310,30))
            d.text((i*310+3,5),name+' (mechanical)',fill='black')
        d.text((4,290),str(measured['functional']['checks'])[:170],fill='black');canvas.save(fig/'figure3_edits.png')
    # Actual text editor outputs are separate from prescribed mechanical operations.
    text_cases=[]
    for row in terminal:
        dest=folder(row)/'text_edit'
        if (dest/'status.json').exists():text_cases.append({'run_id':row['run_id'],'method':row['method'],'scene_id':row['scene_id'],'status':read(dest/'status.json'),'check':read(dest/'text_edit.json')})
    csv_write(out/'text_edits.csv',text_cases)
    edited=next((r for r in terminal if (folder(r)/'text_edit/after.png').exists()),None)
    if edited:
        dest=folder(edited)/'text_edit';canvas=Image.new('RGB',(620,320),'white');draw=ImageDraw.Draw(canvas)
        for i,name in enumerate(['before.png','after.png']):
            canvas.paste(ImageOps.contain(Image.open(dest/name).convert('RGB'),(300,250)),(i*310,35));draw.text((i*310+4,8),name+' (fixed text editor)',fill='black')
        result=read(dest/'text_edit.json');draw.text((4,295),'target='+str(result['target_success'])+' non-target='+str(result['non_target_preservation']['pass'])+' calls=1 repairs=0',fill='black');canvas.save(fig/'figure3_text_editor.png')
    view_case=next((r for r in terminal if (folder(r)/'views/views.json').exists()),None)
    if view_case:
        dest=folder(view_case)/'views';pngs=[folder(view_case)/'final.png']+sorted(dest.glob('*.png'));canvas=Image.new('RGB',(310*len(pngs),290),'white');draw=ImageDraw.Draw(canvas)
        for i,p in enumerate(pngs):
            canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(300,250)),(i*310,30));draw.text((i*310+3,4),p.stem,fill='black')
        canvas.save(fig/'multiview.png')
    meta_rows=[]
    for p in sorted((ROOT/'candidates').glob('r*/scene_rsi_v2/C*/proposal_result.json')):
        result=read(p);meta_rows.append(dict(run=p.parts[-4],candidate=p.parent.name,status=result['status'],candidate_type=result.get('candidate_type'),M_changed=result['M_changed'],used_M=result['used_M'],descendant_executed=bool(result['M_changed'] and result.get('M_descendant_executed')),stage1=str((p.parent/'stage1.json').relative_to(ROOT)),stage2=str((p.parent/'stage2.json').relative_to(ROOT))))
    for record in meta_rows:
        path=ROOT/'candidates'/record['run']/'scene_rsi_v2'/record['candidate']/'meta.py'
        later=[p for p in stages if read(p.parent/'stage1.json')['M_source']==str(path)]
        record['used_in_later_patch_proposal']=bool(record['M_changed'] and any((p.parent/'proposal_call/request.json').exists() for p in later))
        record['later_decision_traces']=[str(p.relative_to(ROOT)) for p in later] if record['M_changed'] else []
    csv_write(out/'meta_participation.csv',meta_rows)
    f,ax=plt.subplots(figsize=(11,max(2,len(meta_rows)*.7)));ax.axis('off')
    for i,m in enumerate(meta_rows):ax.text(.01,1-(i+.5)/max(1,len(meta_rows)),f"{m['run']} {m['candidate']} | {m['candidate_type']} | M changed={m['M_changed']} | descendant executed={m['descendant_executed']} | later proposal={m['used_in_later_patch_proposal']}\nused M: {m['used_M'].split('/candidates/')[-1][-95:]}",va='center',fontsize=9)
    ax.set_title('Figure 5: executable M participation; not evidence of improved meta ability');f.tight_layout();f.savefig(fig/'figure5_meta.png',dpi=160);plt.close(f)
    changed=next((p for p in sorted((ROOT/'candidates').glob('r*/scene_rsi_v2/C*/proposal_result.json')) if read(p)['M_changed']),None)
    if changed:
        result=read(changed);before=Path(result['used_M']).read_text();after=(changed.parent/'meta.py').read_text()
        changes=list(difflib.unified_diff(before.splitlines(),after.splitlines(),fromfile='parent M',tofile='descendant M'))
        f,ax=plt.subplots(figsize=(13,max(4,min(35,len(changes))*.17)));ax.axis('off');ax.text(0,1,'\n'.join(line[:150] for line in changes[:35]),va='top',family='monospace',fontsize=7)
        ax.set_title('Real M source diff (first 35 lines; complete diff in candidate directory)');f.tight_layout();f.savefig(fig/'figure5_meta_diff.png',dpi=160);plt.close(f)
    data={'state':read(ROOT/'state.json'),'ledger':read(ROOT/'ledger.json'),'summary':summary,'paired':paired,'archive':archive,'meta':meta_rows,'diagnostic':diagnostic,'calibration':read(ROOT/'tests/calibration.json')}
    (out/'summary.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    text='# Scene-RSI V2 中文实验报告\n\n本轮只比较共享 H0 与 Scene-RSI V2，不重跑其他方法。数据为 exploratory，历史联系表曝光，不能宣称严格盲测。\n\n'
    text+='## 实际状态与结果\n\n```json\n'+json.dumps({'state':data['state'],'summary':summary,'ledger':data['ledger']},ensure_ascii=False,indent=2)+'\n```\n\n'
    text+='## 机制证据与边界\n\nM 的 plan_probes 选择真实对象和测试，runner 执行，真实观测进入 M.plan_patch。见 candidates 下 stage1/stage2、observations、changes.diff。M-only 不计 H 改善；M 被执行不证明元能力提高。\n\n结构校准涵盖正确组合、脱离父对象、破坏支撑、共享材质误改、独立编辑和表面相交。自然图像无三维真值；声明部件完整性不等于参考对象完整性。支撑是归一化 AABB 近似，Mesh BVH 仅测三角表面相交，不能判断所有穿插、包含或合理接缝。\n\n主 Q 沿用 V1 公式；未测量指标为 null，失败效用单独为零。条件质量与全分母效用分别报告；多视角不计独立样本。只有 2 个研发重复，不作普遍优势或显著性结论。机械编辑与文字编辑分别保留，文字编辑只按预定少量终测场景执行。\n\n'
    text+='## 图与数据\n\n每张图由 analyze.py 从 metrics/scene_metrics.csv、candidates.csv、paired_test.csv、calls.csv、meta_participation.csv 与原始 JSON 重画。Figure1 按冻结顺序纳入全部测试场景；Figure2 采用按路径排序的首个正式诊断，无成功筛选；Figure3 采用首个有机械渲染的终测场景。\n'
    for p in sorted(fig.glob('*.png')):text+=f'\n![{p.stem}](../figures/{p.name})\n'
    (report/'REPORT_ZH.md').write_text(text)
    content='<html lang="zh"><meta charset="utf-8"><title>Scene-RSI V2</title><style>body{font:16px sans-serif;max-width:1300px;margin:auto}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>Scene-RSI V2 真实结果</h1><p>Exploratory；两次独立研发；不将机制运行等同于科研结论。</p><a href="REPORT_ZH.md">中文报告</a> · <a href="../metrics/summary.json">原始汇总</a><pre>'+html.escape(json.dumps({'state':data['state'],'summary':summary,'ledger':data['ledger']},ensure_ascii=False,indent=2))+'</pre>'
    for p in sorted(fig.glob('*.png')):content+=f'<h2>{p.stem}</h2><img src="../figures/{p.name}">'
    if diagnostic:content+='<h2>诊断原始证据</h2><pre>'+html.escape(json.dumps(diagnostic,ensure_ascii=False,indent=2))+'</pre>'
    content+='</html>';(report/'index.html').write_text(content)
    print(json.dumps({'rows':len(rows),'calls':len(calls),'summary':summary}))

if __name__=='__main__':main()
