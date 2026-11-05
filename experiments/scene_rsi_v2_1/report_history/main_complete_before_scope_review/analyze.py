"""Offline summaries and figures from saved V2 measurements; no models or Blender."""
from pathlib import Path
import csv,json,html,difflib,sys
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

def execution_state(row,task_folder=None):
    if row is None:return 'running' if task_folder and (task_folder/'task.json').exists() else 'not_started'
    if row['status']=='complete':return 'completed'
    if 'timeout' in str(row.get('failure_type')) or 'TimeoutExpired' in str(row.get('runtime_status')):return 'timeout'
    if row['status'] in ['invalid','running','not_started']:return row['status']
    return 'failed'

def terminal_summary(data,scheduled):
    successful=[r for r in data if r['metrics']['valid']]
    finished=len(data);done=finished==scheduled and scheduled>0
    return dict(scheduled=scheduled,recorded=finished,completed=finished,succeeded=len(successful),
                status='completed' if done else 'running' if finished else 'not_started',
                execution_success_rate=len(successful)/scheduled if done else None,
                observed_success_rate=len(successful)/finished if finished else None,
                conditional_Q=sum(r['metrics']['overall'] for r in successful)/len(successful) if successful else None,
                task_utility_v2=sum(r['task_utility_v2'] for r in data)/scheduled if done else None,
                functional_passes=sum(r['functional']['functional_pass'] for r in data),
                functional_compliance_rate=sum(r['functional']['functional_pass'] for r in data)/scheduled if done else None,
                failed=sum(execution_state(r)=='failed' for r in data),timeout=sum(execution_state(r)=='timeout' for r in data),not_run=scheduled-finished)

def mechanism_figures(out,fig):
    comparisons=read(ROOT/'tests/diagnosis/comparison.json',[])
    truth=read(ROOT/'tests/diagnosis/ground_truth_evaluator_only.json',[])
    for item in comparisons:
        label=next(t for t in truth if t['scene_id']==item['scene_id'])
        item['M_second_stage_module_exact']=item['decision']['shared_module']==label['module']
        # The material fixture's non-target fault is the separate block; chair parts
        # are not related parts of that block. Preserve the earlier broad raw field.
        allowed=[label['object_id']]+([] if label['module']=='material_edit' else label['related_object_ids'])
        item['fault_object_match_corrected']=any(t in allowed for t in item['targets'])
        item['module_match_scope']='correct_or_related_module includes visual localization; M second-stage exact match reported separately. Broad generic modules are not exact fault localization.'
        dest=ROOT/'tests/diagnosis'/item['scene_id']/item['method']
        processes=[read(p) for p in dest.glob('probes/*/process.json')]+[read(p) for p in dest.glob('regression/*/process.json')]
        calls=[read(p) for p in dest.glob('localization/*/visual_call/session.json')]
        item['measured_blender_seconds_aligned']=sum(p['seconds'] for p in processes)
        item['localizer_cli_sessions']=len(calls)
        item['localizer_cli_seconds']=sum(c['seconds'] for c in calls)
        item['legacy_seconds_scope']='Raw case timer includes earlier strategy; use boundary process/CLI times. Includes no claim of algorithm speed; TLS wait occurred.'
    csv_write(out/'diagnostic_comparison.csv',comparisons)
    if not comparisons:return
    f,axes=plt.subplots(1,4,figsize=(14,4))
    for i,key in enumerate(['fault_object_match_corrected','correct_or_related_module','M_second_stage_module_exact','probe_changes_decision']):
        for j,method in enumerate(['fixed_heuristic','scene_rsi_v2_1']):
            points=[r for r in comparisons if r['method']==method]
            axes[i].scatter([j]*len(points),[k for k in range(len(points))],c=['#299269' if r[key] else '#c84747' for r in points],s=140)
        axes[i].set(xticks=[0,1],xticklabels=['fixed','V2.1'],yticks=list(range(5)),yticklabels=[f'case{k+1:02d}' for k in range(5)],title=key)
    f.suptitle('5 known faults; green=yes, red=no; localization is not RSI gain')
    f.tight_layout();f.savefig(fig/'diagnostic_comparison.png',dpi=160);plt.close(f)
    cases=sorted((ROOT/'tests/diagnosis').glob('case*'))
    canvas=Image.new('RGB',(930,len(cases)*230),'white');d=ImageDraw.Draw(canvas)
    for i,case in enumerate(cases):
        probes=sorted((case/'scene_rsi_v2_1/probes').glob('*/probe_*.png'))
        paths=[case/'reference.png',case/'final.png',probes[0] if probes else None]
        for j,p in enumerate(paths):
            if p and p.exists():canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(300,195)),(j*310,i*230+30))
            d.text((j*310+3,i*230+3),case.name+' '+['Reference','Injected error','Actual selected probe'][j],fill='black')
    canvas.save(fig/'diagnostic_fixture_contact.png')
    transfer=read(ROOT/'tests/diagnosis/shared_patch_transfer.json')
    if transfer:
        csv_write(out/'controlled_shared_patch.csv',[{'method':method,**tests} for method,tests in transfer.items()])
        repair_calls=[read(p) for p in (ROOT/'tests/diagnosis').glob('repair_*/proposal_call/session.json')]
        csv_write(out/'controlled_shared_patch_cost.csv',[{k:c.get(k) for k in ['call_dir','status','requested_model','actual_model','seconds','input_tokens','output_tokens','total_tokens']} for c in repair_calls])

def contact(rows,tests,dest):
    size=(300,240);canvas=Image.new('RGB',(930,len(tests)*285),'white');draw=ImageDraw.Draw(canvas)
    for i,scene in enumerate(tests):
        base=next((r for r in rows if r['scene_id']==scene['scene_id'] and r['method']=='fixed_h0'),None)
        ours=next((r for r in rows if r['scene_id']==scene['scene_id'] and r['method']=='scene_rsi_v2_1'),None)
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
    sys.path.insert(0,str(ROOT/'backend'))
    import budget
    budget.ROOT=ROOT
    (ROOT/'ledger.json').write_text(json.dumps(budget.current(),indent=2))
    out=ROOT/'metrics';fig=ROOT/'figures';report=ROOT/'reports'
    for d in [out,fig,report]:d.mkdir(exist_ok=True)
    mechanism_figures(out,fig)
    manifest=read(ROOT/'manifest.json',[]);archive=read(ROOT/'archive.json',[])
    rows=[read(p) for p in sorted((ROOT/'results').glob('*/*/*/*/*/record.json'))]
    from diagnostics import failure_evidence
    calls=[read(p) | {'observed_session_file':str(p.relative_to(ROOT))} for p in ROOT.rglob('session.json') if p.parent.joinpath('request.json').exists()]
    for call_row in calls:
        parts=Path(call_row['observed_session_file']).parts
        call_row['phase']='payload_cap_failure' if parts[0]=='attempt_archive' else 'controlled_diagnostics' if parts[0]=='tests' else 'smoke' if 'smoke' in parts else 'test_inference_or_edit' if 'test' in parts else 'independent_judge' if parts[0]=='judgments' else 'development_selection_research'
    costs=[]
    for phase in sorted({c['phase'] for c in calls}):
        group=[c for c in calls if c['phase']==phase]
        costs.append({'phase':phase,'cli_sessions':len(group),'completed_cli_sessions':sum(c['status']=='complete' for c in group),'known_input_tokens':sum(c['input_tokens'] for c in group if isinstance(c.get('input_tokens'),int)),'known_output_tokens':sum(c['output_tokens'] for c in group if isinstance(c.get('output_tokens'),int)),'usage_unknown_sessions':sum(not isinstance(c.get('total_tokens'),int) for c in group),'cost_usd':None})
    csv_write(out/'cost_by_phase.csv',costs)
    failed_attempts=read(ROOT/'attempt_archive/payload_cap_failure/archive.json',[])
    csv_write(out/'candidate_attempts.csv',[{'attempt_phase':'payload_cap_failure',**a} for a in failed_attempts]+[{'attempt_phase':'payload_fix1' if failed_attempts else 'original',**a} for a in archive])
    csv_write(out/'scene_metrics.csv',[{k:r.get(k) for k in ['method','run_id','candidate_id','scene_id','split','status','metrics','functional','task_utility_v2','failure_type','device','seconds','usage','H_version','M_version','alias_of']} | {'execution_state':execution_state(r),'observed_failure_stage':failure_evidence(r)['category']} for r in rows])
    scheduled=[next((a for a in archive if a['run_id']==rid and a['candidate_id']==f'C{k}'),{'method':'scene_rsi_v2_1','run_id':rid,'candidate_id':f'C{k}','status':'not_started','accepted':None}) for k in [1,2] for rid in ['r1','r2']]
    choices_now=read(ROOT/'selection_freeze.json',{}).get('choices',[])
    for item in scheduled:
        dest=ROOT/'candidates'/item['run_id']/'scene_rsi_v2_1'/item['candidate_id']
        if item['status']=='evaluated':
            item['candidate_state']='selected' if any(c['run_id']==item['run_id'] and c['candidate_id']==item['candidate_id'] and c['method']==item['method'] for c in choices_now) else 'completed'
        elif item['status']=='proposal_failed':
            result=read(dest/'proposal_result.json');error=result['traceback'] if 'traceback' in result else result['error']
            item['candidate_state']='timeout' if 'Timeout' in error else 'invalid' if any(t in error for t in ['SyntaxError','ValueError','KeyError','TypeError']) else 'failed'
        else:
            session=read(dest/'proposal_call/session.json')
            proposal=read(dest/'proposal_result.json')
            paused=read(ROOT/'state.json',{}).get('phase')=='paused_after_stage_failure'
            item['candidate_state']='failed' if dest.exists() and paused else 'running' if dest.exists() and (proposal is None or proposal['status']=='proposed') else 'not_started'
            item['state_basis']='Archive terminal result, candidate workspace/stages, and pipeline pause; source state.json is only the last runner event.'
    csv_write(out/'candidates.csv',scheduled)
    slots=[]
    for rid in ['r1','r2']:
        for method,cid,scenes in [('fixed_h0','H0',manifest)]+[('scene_rsi_v2_1',f'C{k}',[q for q in manifest if q['split']!='test']) for k in [1,2]]:
            for scene in scenes:
                row=next((r for r in rows if r['run_id']==rid and r['method']==method and r['candidate_id']==cid and r['scene_id']==scene['scene_id']),None)
                candidate=next((a for a in scheduled if a['run_id']==rid and a['candidate_id']==cid),None)
                slots.append({'method':method,'run_id':rid,'candidate_id':cid,'scene_id':scene['scene_id'],'split':scene['split'],'status':execution_state(row,ROOT/'results'/rid/method/cid/scene['split']/scene['scene_id']),'metrics':row['metrics'] if row else None,'failure_reason':candidate.get('error') if candidate else None})
    frozen_choices=read(ROOT/'selection_freeze.json',{}).get('choices',[])
    for rid in ['r1','r2']:
        selected=next((c for c in frozen_choices if c['run_id']==rid and c['method']=='scene_rsi_v2_1'),None)
        for scene in [q for q in manifest if q['split']=='test']:
            row=next((r for r in rows if r['run_id']==rid and r['method']=='scene_rsi_v2_1' and r['split']=='test' and r['scene_id']==scene['scene_id'] and selected and r['candidate_id']==selected['candidate_id']),None)
            slots.append({'method':'scene_rsi_v2_1','run_id':rid,'candidate_id':selected['candidate_id'] if selected else 'selection_pending','scene_id':scene['scene_id'],'split':'test','status':execution_state(row,ROOT/'results'/rid/'scene_rsi_v2_1'/(selected['candidate_id'] if selected else 'selection_pending')/'test'/scene['scene_id']),'metrics':row['metrics'] if row else None,'failure_reason':None})
    csv_write(out/'scheduled_slots.csv',slots)

    csv_write(out/'calls.csv',[{k:c.get(k) for k in ['role','phase','requested_model','actual_model','actual_model_source','reasoning_effort','status','exit_code','seconds','input_tokens','output_tokens','total_tokens','observable_cli_turns','observable_model_turns','tool_calls','call_dir','observed_session_file','error','started','finished']} for c in calls])
    choices=read(ROOT/'selection_freeze.json',{}).get('choices',[])
    terminal=[r for r in rows if r['split']=='test' and any(all(r[k]==c[k] for k in ['method','run_id','candidate_id']) for c in choices)]
    summary=[]
    for rid in ['r1','r2']:
        for method in ['fixed_h0','scene_rsi_v2_1']:
            data=[r for r in terminal if r['method']==method and r['run_id']==rid];valid=[r for r in data if r['status']=='complete'];n=sum(s['split']=='test' for s in manifest)
            partial=sum((ROOT/'results'/rid/method/'H0'/'test'/s['scene_id']/'status.json').exists() for s in manifest if s['split']=='test' and not any(r['scene_id']==s['scene_id'] for r in data)) if method=='fixed_h0' else 0
            stats=terminal_summary(data,n)
            stats['unscored_generations']=partial
            if partial and stats['status']=='not_started':stats['status']='running'
            summary.append(dict(run_id=rid,method=method,**stats))
    csv_write(out/'terminal_summary.csv',summary)
    paired=[]
    for rid in ['r1','r2']:
        for scene in [s for s in manifest if s['split']=='test']:
            pair=[next((r for r in terminal if r['run_id']==rid and r['method']==m and r['scene_id']==scene['scene_id']),None) for m in ['fixed_h0','scene_rsi_v2_1']]
            a,b=pair
            paired.append(dict(run_id=rid,scene_id=scene['scene_id'],both_completed=bool(a and b and a['status']==b['status']=='complete'),quality_difference=b['metrics']['overall']-a['metrics']['overall'] if a and b and a['status']==b['status']=='complete' else None,
                utility_difference=b['task_utility_v2']-a['task_utility_v2'] if a and b else None,
                complete_effective_improvement=bool(a and b and a['status']==b['status']=='complete' and b['functional']['functional_pass'] and b['metrics']['overall']>a['metrics']['overall']+.01) if a and b else None))
    csv_write(out/'paired_test.csv',paired)
    joint={'scheduled_pairs':len(paired),'recorded_pairs':sum(p['utility_difference'] is not None for p in paired),
           'valid_quality_pairs':sum(p['both_completed'] for p in paired),
           'complete_effective_improvement_rate':sum(p['complete_effective_improvement'] is True for p in paired)/len(paired) if paired and all(p['complete_effective_improvement'] is not None for p in paired) else None,
           'unit':'scene/run pair; same scene across runs is not another independent scene'}
    csv_write(out/'joint_improvement.csv',[joint])
    if choices:
      for rid in ['r1','r2']:contact([r for r in terminal if r['run_id']==rid],[s for s in manifest if s['split']=='test'],fig/f'figure1_{rid}.png')
    plt.rcParams.update({'font.size':9})
    f,axes=plt.subplots(1,3,figsize=(12,3.5))
    for i,method in enumerate(['fixed_h0','scene_rsi_v2_1']):
        points=[r for r in terminal if r['method']==method and r['status']=='complete'];axes[0].scatter([i]*len(points),[r['metrics']['overall'] for r in points],alpha=.5,label=method)
        groups=[s for s in summary if s['method']==method];axes[1].bar([i*3+k for k in range(2)],[s['functional_passes']/s['scheduled'] if s['recorded']==s['scheduled'] else np.nan for s in groups],label=method)
    axes[0].set(xticks=[0,1],xticklabels=['H0','Selected'],ylabel='Conditional Q (individual scene/run points)')
    axes[1].set(ylabel='Functional passes / all scheduled',xticks=[])
    counts={s:sum(c['status']==s for c in calls) for s in ['complete','failed','running']};axes[2].bar(list(counts),list(counts.values()));axes[2].set(ylabel='CLI sessions, all stages')
    f.tight_layout();f.savefig(fig/'statistics.png',dpi=160);plt.close(f)
    failures=[r for r in rows if r['split']!='smoke' and r['status']!='complete' and 'alias_of' not in r]
    failure_counts={stage:sum(failure_evidence(r)['category']==stage for r in failures) for stage in sorted({failure_evidence(r)['category'] for r in failures})}
    csv_write(out/'failure_stages.csv',[{'observed_stage':k,'physical_scene_attempts':v,'scope':'Recorded formal reconstructions, no aliases; not-started tasks excluded'} for k,v in failure_counts.items()])
    if failure_counts:
        f,ax=plt.subplots(figsize=(9,3));ax.barh(list(failure_counts),list(failure_counts.values()),color='#bd4b47')
        ax.set(xlabel='Recorded physical reconstruction failures; all formal splits, aliases excluded');f.tight_layout();f.savefig(fig/'failure_stages.png',dpi=160);plt.close(f)
    f,ax=plt.subplots(figsize=(8,4))
    for rid in ['r1','r2']:
        baseline=[r for r in rows if r['run_id']==rid and r['method']=='fixed_h0' and r['split']=='selection'];q=sum(r['task_utility_v2'] for r in baseline)/len(baseline) if len(baseline)==sum(q['split']=='selection' for q in manifest) and baseline else None
        entries=sorted([a for a in archive if a['run_id']==rid and a['status']=='evaluated'],key=lambda a:int(a['candidate_id'][1:]))
        xs=[0]+[int(a['candidate_id'][1:]) for a in entries];ys=[q]+[a['selection']['endpoint_quality'] for a in entries]
        ax.plot(xs,ys,'o:',label=rid+' raw candidate')
        retained=[q]
        for a in entries:retained.append(a['selection']['endpoint_quality'] if a['accepted'] else retained[-1])
        ax.plot(xs,retained,'s-',label=rid+' retained H*')
        for a,x,y in zip(entries,xs[1:],ys[1:]):ax.annotate(f"{a['candidate_id']} {a['candidate_type']} accept={a['accepted']} Mchg={a['M_changed']}\nCLI={a['ledger_after']['cli_sessions']}",(x,y),fontsize=7)
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
                if c['observed_session_file'].startswith('attempt_archive/'):
                    included.append(c);continue
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
                baseline=[r for r in rows if r['method']=='fixed_h0' and r['run_id']==rid and r['split']=='selection'];best=sum(r['task_utility_v2'] for r in baseline)/len(baseline) if len(baseline)==sum(q['split']=='selection' for q in manifest) and baseline else None
            if a['accepted']:best=quality
            cost_points.append({'run_id':rid,'candidate_id':a['candidate_id'],'cli_sessions_cumulative':len(included),'known_input_tokens':sum(c['input_tokens'] for c in included if isinstance(c.get('input_tokens'),int)),'known_output_tokens':sum(c['output_tokens'] for c in included if isinstance(c.get('output_tokens'),int)),'usage_unknown_sessions':sum(c.get('total_tokens') is None for c in included),'selected_utility':best,'candidate_utility':quality,'H_accepted':a['accepted']})
    csv_write(out/'development_cost_points.csv',cost_points)
    if cost_points:
        f,ax=plt.subplots(figsize=(8,4))
        for rid in ['r1','r2']:
            points=[p for p in cost_points if p['run_id']==rid];ax.plot([p['cli_sessions_cumulative'] for p in points],[p['selected_utility'] for p in points],'o-',label=rid+' retained')
            ax.scatter([p['cli_sessions_cumulative'] for p in points],[p['candidate_utility'] for p in points],marker='x',label=rid+' candidate')
        ax.set(xlabel='Cumulative CLI sessions within research run (H0 + proposals + Dev/Selection)',ylabel='Selection Q utility');ax.legend();f.tight_layout();f.savefig(fig/'cost_gain.png',dpi=160);plt.close(f)
    stages=sorted((ROOT/'candidates').glob('r*/scene_rsi_v2_1/C*/stage2.json'))
    diagnostic=None
    if not stages:stages=sorted((ROOT/'candidates').glob('smoke*/scene_rsi_v2_1/C*/stage2.json'))
    if stages:
        path=stages[0];trace=read(path);observations=trace['observations']['probes'];dest=path.parent
        images=[]
        sid=trace['context_after_execution']['development'][0]['scene_id']
        for entry in trace['context_after_execution']['development']:
            if not observations or entry['scene_id']==observations[0]['request']['scene_id']:sid=entry['scene_id'];images=entry['attached_images']
        probes=list(dest.glob('probes/*/probe_*.png'));pictures=[Path(p) for p in images]+probes
        child_split='smoke' if dest.parent.parent.name.startswith('smoke') else 'development'
        child_folder=ROOT/'results'/dest.parent.parent.name/dest.parent.name/dest.name/child_split/sid
        child=read(child_folder/'record.json')
        child_index=len(pictures);pictures.append(child_folder/'final.png')
        canvas=Image.new('RGB',(max(1,len(pictures))*270,330),'white');d=ImageDraw.Draw(canvas)
        for i,p in enumerate(pictures):
            if p.exists():canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(260,240)),(i*270,30))
            d.text((i*270+4,4),'Candidate: '+(child['status'] if child else 'pending') if i==child_index else ['Reference','Parent reconstruction'][i] if i<2 else p.stem,fill='black')
            if not p.exists():d.text((i*270+8,130),'NO RENDER / '+(child['status'] if child else 'pending'),fill='black')
        d.text((6,280),str([(o['request']['object_id'],o['quality_delta']) for o in observations])[:170],fill='black');d.text((6,305),trace['decision']['shared_module'][:160],fill='black');canvas.save(fig/'figure2_diagnostic.png')
        diagnostic={'trace':str(path.relative_to(ROOT)),'scene':sid,'decision':trace['decision'],'probes':observations,'diff':str((dest/'changes.diff').relative_to(ROOT)) if (dest/'changes.diff').exists() else None,'phase':'smoke_excluded_from_formal' if 'smoke' in str(path) else 'formal'}
        proposal=read(dest/'proposal_result.json',{})
        diagnostic['proposal_explanation_self_reported']={k:proposal.get(k) for k in ['rationale','scope','evidence_alignment']}
        diagnostic['actual_diff_preview']=(dest/'changes.diff').read_text().splitlines()[:40] if (dest/'changes.diff').exists() else None
        diagnostic['candidate_development_outcome']={k:child[k] for k in ['status','metrics','functional','failure_type']} if child else None
    # Actual mechanical before/after, not a language-edit claim.
    measured=next((r for r in terminal if (folder(r)/'functional/before.png').exists()),None)
    if measured is None:measured=next((r for r in rows if r['split']=='smoke' and (folder(r)/'functional/before.png').exists()),None)
    if measured:
        canvas=Image.new('RGB',(930,340),'white');d=ImageDraw.Draw(canvas)
        for i,name in enumerate(['before.png','after_material.png','after_move.png']):
            p=folder(measured)/'functional'/name
            if p.exists():canvas.paste(ImageOps.contain(Image.open(p).convert('RGB'),(300,250)),(i*310,30))
            d.text((i*310+3,5),name+' (mechanical)',fill='black')
        d.text((4,285),f"{measured['split']} / {measured['run_id']} / {measured['scene_id']} / {measured['candidate_id']} (mechanical, not text editing)",fill='black')
        d.text((4,310),str(measured['functional']['checks'])[:170],fill='black');canvas.save(fig/'figure3_edits.png')
        raw=read(folder(measured)/'functional/scene_structure.json')
        wanted=set(raw['target']['mesh_names'])|{raw['target']['object']}
        by_name={o['name']:o for o in raw['objects']}
        for name in list(wanted):
            if name in by_name:wanted.update(by_name[name]['parent_chain'])
        shown=sorted([o for o in raw['objects'] if o['name'] in wanted],key=lambda o:tuple(reversed(o['parent_chain']))+(o['name'],))[:64]
        hierarchy=[{'object_id':o['name'],'parent':o['parent'],'type':o['type'],'depth':len(o['parent_chain'])} for o in shown]
        csv_write(out/'hierarchy_case.csv',hierarchy)
        f,ax=plt.subplots(figsize=(11,max(3,len(shown)*.18)));ax.axis('off')
        lines=['  '*min(row['depth'],8)+row['object_id']+' ['+row['type']+']' for row in hierarchy]
        ax.text(.01,.98,'\n'.join(lines),va='top',family='monospace',fontsize=8)
        ax.set_title('Actual editable target hierarchy; up to64 nodes; full object graph in scene_structure.json')
        f.tight_layout();f.savefig(fig/'figure3_hierarchy.png',dpi=150);plt.close(f)
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
    for p in sorted((ROOT/'candidates').glob('r*/scene_rsi_v2_1/C*/proposal_result.json')):
        result=read(p);meta_rows.append(dict(run=p.parts[-4],candidate=p.parent.name,status=result['status'],candidate_type=result.get('candidate_type'),M_changed=result['M_changed'],used_M=result['used_M'],descendant_executed=bool(result['M_changed'] and result.get('M_descendant_executed')),stage1=str((p.parent/'stage1.json').relative_to(ROOT)),stage2=str((p.parent/'stage2.json').relative_to(ROOT))))
    for record in meta_rows:
        path=ROOT/'candidates'/record['run']/'scene_rsi_v2_1'/record['candidate']/'meta.py'
        later=[p for p in stages if read(p.parent/'stage1.json')['M_source']==str(path)]
        record['used_in_later_patch_proposal']=bool(record['M_changed'] and any((p.parent/'proposal_call/request.json').exists() for p in later))
        record['later_valid_candidate_produced']=bool(record['M_changed'] and any(read(p.parent/'proposal_result.json',{}).get('status')=='proposed' for p in later))
        record['later_usage_scope']='Separate executable M decisions, submitted proposal attempts, and valid produced H/M; no meta ability claim from source change alone.'
        record['later_decision_traces']=[str(p.relative_to(ROOT)) for p in later] if record['M_changed'] else []
    csv_write(out/'meta_participation.csv',meta_rows)
    f,ax=plt.subplots(figsize=(11,max(2,len(meta_rows)*.7)));ax.axis('off')
    for i,m in enumerate(meta_rows):ax.text(.01,1-(i+.5)/max(1,len(meta_rows)),f"{m['run']} {m['candidate']} | {m['candidate_type']} | M changed={m['M_changed']} | descendant executed={m['descendant_executed']} | later proposal={m['used_in_later_patch_proposal']}\nused M: {m['used_M'].split('/candidates/')[-1][-95:]}",va='center',fontsize=9)
    ax.set_title('Figure 5: executable M participation; not evidence of improved meta ability');f.tight_layout();f.savefig(fig/'figure5_meta.png',dpi=160);plt.close(f)
    changed=next((p for p in sorted((ROOT/'candidates').glob('r*/scene_rsi_v2_1/C*/proposal_result.json')) if read(p)['M_changed']),None)
    if changed:
        result=read(changed);before=Path(result['used_M']).read_text();after=(changed.parent/'meta.py').read_text()
        changes=list(difflib.unified_diff(before.splitlines(),after.splitlines(),fromfile='parent M',tofile='descendant M'))
        f,ax=plt.subplots(figsize=(13,max(4,min(35,len(changes))*.17)));ax.axis('off');ax.text(0,1,'\n'.join(line[:150] for line in changes[:35]),va='top',family='monospace',fontsize=7)
        ax.set_title('Real M source diff (first 35 lines; complete diff in candidate directory)');f.tight_layout();f.savefig(fig/'figure5_meta_diff.png',dpi=160);plt.close(f)
    data={'state':read(ROOT/'state.json'),'ledger':read(ROOT/'ledger.json'),'summary':summary,'paired':paired,'joint_improvement':joint,'archive':archive,'meta':meta_rows,'diagnostic':diagnostic,'calibration':read(ROOT/'tests/calibration.json')}
    (out/'summary.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    text='# Scene-RSI V2.1 中文实验报告\n\n本轮只比较共享 H0 与 Scene-RSI V2.1，不重跑其他方法。数据为 exploratory，历史联系表曝光，不能宣称严格盲测。\n\n'
    text+='## 实际状态与结果\n\n```json\n'+json.dumps({'state':data['state'],'summary':summary,'ledger':data['ledger']},ensure_ascii=False,indent=2)+'\n```\n\n'
    text+='## 实际候选和 Selection\n\n|研发|候选|类型|开发成功/预定|Selection成功/预定|绝对资格|Selection条件Q|选择保留|M源码改变|\n|---|---|---|---|---|---|---|---|---|\n'
    for a in archive:
        if a['status']=='evaluated':
            ds,ss=a['development'],a['selection']
            text+='|'+ '|'.join(map(str,[a['run_id'],a['candidate_id'],a['candidate_type'],str(ds['completed'])+'/'+str(ds['all_scheduled']),str(ss['completed'])+'/'+str(ss['all_scheduled']),ss['eligible'],ss['conditional_quality'],a['accepted'],a['M_changed']]))+'|\n'
        else:text+=f"|{a['run_id']}|{a['candidate_id']}|{a['status']}|null|null|False|null|False|null|\n"
    text+='\n条件Q缺测为None/null，不等于0。H0失败不放宽候选资格；不合格H0仅为fallback。未选候选没有终测，不能称其终测联合通过。\n\n'
    text+='## 选中版本的逐场景 Test\n\n|研发|方法|版本|场景|状态|实测Q|独立任务效用|功能通过|设备|\n|---|---|---|---|---|---|---|---|---|\n'
    for row in terminal:
        text+='|'+'|'.join(map(str,[row['run_id'],row['method'],row['candidate_id'],row['scene_id'],execution_state(row),row['metrics']['overall'],row['task_utility_v2'],row['functional']['functional_pass'],row['device']]))+'|\n'
    if not terminal:text+='\nTest pending，未开始或尚无完成评价记录；不报告0%成功率。\n'
    text+='\n完整配对差见metrics/paired_test.csv。失败Q保留null；失败效用0是另一个字段。仅双方成功时计算条件Q差。joint_improvement.csv单位为选中流程的scene/run配对，不是所有原始候选的终测改进率。两次研发复用同两个Test来源组，不是四个独立场景。\n\n'
    changed=sum(m['M_changed'] for m in meta_rows)
    text+='## H 与 M 实际变化\n\n'+f'实际产生 {len(meta_rows)} 个正式共享候选，其中 M 源码变化 {changed} 个。'
    text+='本轮没有新 M 参与后续提案，未发生元级程序自修改；不能报告元能力提升。' if not changed else 'M变化、接口执行、后续提案尝试和有效后代生成分别见metrics/meta_participation.csv；代码改变本身不证明能力提升。'
    text+='\n\n单图P保存在results各scene.py/build.py与steps；共享H/M在candidates保存完整源码和diff。外层工程师的runner修复不是M自修改。\n\n'
    text+='## 运行偏离与成本\n\n四次原提案在模型提交前触发600KB限制，未生成H/M候选，原始失败与旧选择保存在attempt_archive/payload_cap_failure。payload_fix1保留全部ID并限制128份数值详情，真实包回归测试通过；这些额外诊断全部计入同一个160 CLI/600帧预算。一个H0 Test生成曾提前提交，未查看媒体/代码/质量、未回流研发，只在新的选择冻结后评价并明确复用。该项属于事后as-run修订，不宣称严格盲测。见protocol.md和configs/payload_evidence_fix1.json。\n\n成本按实际CLI调用、CLI返回usage、渲染和设备记录，见metrics/cost_by_phase.csv、calls.csv及ledger.json。CLI会话不等于一次底层模型推理；缺失usage、实际返回模型、费用、服务排队时间保持unknown/null。CPU两线程单重任务，无GPU；网络等待和CAD计算混在端到端时间中，不据此宣称算法速度优势。\n\n'
    text+='## 机制证据与边界\n\nM 的 plan_probes 选择真实对象和测试，runner 执行，真实观测进入 M.plan_patch。见 candidates 下 stage1/stage2、observations、changes.diff。M-only 不计 H 改善；M 被执行不证明元能力提高。\n\n结构校准涵盖正确组合、脱离父对象、破坏支撑、共享材质误改、独立编辑和表面相交。自然图像无三维真值；声明部件完整性不等于参考对象完整性。支撑是归一化 AABB 近似，Mesh BVH 仅测三角表面相交，不能判断所有穿插、包含或合理接缝。\n\n主 Q 沿用 V1 公式；未测量指标为 null，执行失败效用单独为零，此Q效用不包含全部功能要求，功能合规另报。条件质量与全分母效用分别报告；多视角不计独立样本。只有 2 个研发重复，不作普遍优势或显著性结论。机械编辑与文字编辑分别保留，文字编辑只按预定少量终测场景执行。\n\n'
    text+='## 可控诊断比较\n\n五个夹具，绿色/红色分别是已执行测试中的命中/未命中；目标组或相关部件命中不等于精准视觉定位。对象计数按材质非目标方块修正，旧宽泛字段保留，见configs/diagnostic_object_count_correction.json。图像定位模块命中和M第二阶段最终模块精确命中单列，后者双方均仅1/5。V2.1新增5次定位调用，双方辅助共享程序各1次修复调用，实际成本并不相同。源代码API契约本身提供修复提示；辅助helper通过不代表自然图像重建H改进。家具尺度定位正确仍可能没有正向探测效果；隐藏对象的隔离实验不自动恢复可见性。原始来源为 tests/diagnosis/comparison.json、shared_patch_transfer.json，统计表 metrics/diagnostic_comparison.csv、controlled_shared_patch.csv，脚本 tests/diagnose.py 与 analyze.py。\n\n'
    text+='## 图与数据\n\n每张图由 analyze.py 从 metrics/scene_metrics.csv、candidates.csv、paired_test.csv、calls.csv、meta_participation.csv 与原始 JSON 重画。Figure1 按冻结顺序纳入全部测试场景；Figure2 采用按路径排序的首个正式诊断，无成功筛选；Figure3 采用首个有机械渲染的终测场景。\n'
    for p in sorted(fig.glob('*.png')):text+=f'\n![{p.stem}](../figures/{p.name})\n'
    (report/'REPORT_ZH.md').write_text(text)
    content='<html lang="zh"><meta charset="utf-8"><title>Scene-RSI V2.1</title><style>body{font:16px sans-serif;max-width:1300px;margin:auto}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>Scene-RSI V2.1 真实结果</h1><p>Exploratory；两次独立研发；不将机制运行等同于科研结论。</p><a href="REPORT_ZH.md">中文报告</a> · <a href="../metrics/summary.json">原始汇总</a><pre>'+html.escape(json.dumps({'state':data['state'],'summary':summary,'ledger':data['ledger']},ensure_ascii=False,indent=2))+'</pre>'
    for p in sorted(fig.glob('*.png')):content+=f'<h2>{p.stem}</h2><img src="../figures/{p.name}">'
    if diagnostic:content+='<h2>诊断原始证据</h2><pre>'+html.escape(json.dumps(diagnostic,ensure_ascii=False,indent=2))+'</pre>'
    content+='</html>';(report/'index.html').write_text(content)
    print(json.dumps({'rows':len(rows),'calls':len(calls),'summary':summary}))

if __name__=='__main__':main()
