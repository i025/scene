"""Transparent paired terminal outcomes, all candidate points, and observable CLI costs."""
from pathlib import Path
import csv
import json
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from budget import current
from report import collect,write_csv,read,plots

METHODS=['fixed_h0','sceneevolve_cli','generic_rsi','scene_rsi_pilot']

def additional_stage_tables(out, rows, choices, calls):
    """Summarize completed optional stages without inventing pending measurements."""
    import matplotlib.pyplot as plt
    tables={}
    status=read(ROOT/'extras_status.json',{})
    if status.get('status')=='complete':
        protocol=read(ROOT/'ablation_protocol.json')
        selected=read(ROOT/'ablation_selection_freeze.json')['choices']
        points=[]
        for choice in selected:
            run=choice['run_id'].replace('ablation_','')
            if protocol['scope']=='minimum_four_condition_feasibility':
                reference=next(c for c in selected if c['run_id']==choice['run_id'] and c['method']=='ours_ablation_reference')
            elif protocol['K']==1:
                reference=read(ROOT/'ablation_reference_selection.json')
            else:
                reference=next(c for c in choices if c['run_id']==run and c['method']=='scene_rsi_pilot')
            for sid in protocol['scene_ids']['test']:
                def find(condition):
                    return next((r for r in rows if all(r[k]==condition[k] for k in ('method','run_id','candidate_id')) and r['scene_id']==sid and r['split']=='test'),None)
                row=find(choice);base=find({'method':'fixed_h0','run_id':run,'candidate_id':'H0'});ref=find(reference)
                q=lambda r:r['metrics']['overall'] if r and r['metrics']['valid'] else None
                value,bq,rq=q(row),q(base),q(ref)
                points.append({'method':choice['method'],'run_id':choice['run_id'],'scene_id':sid,'candidate_id':choice['candidate_id'],'status':row['status'] if row else 'pending','Q':value,'H0_Q':bq,'reference_Q':rq,'reference_method':reference['method'],'paired_gain_H0':value-bq if value is not None and bq is not None else None,'paired_difference_reference':value-rq if value is not None and rq is not None else None,'functional_pass':row['functional']['functional_pass'] if row else None,'reference_functional_pass':ref['functional']['functional_pass'] if ref else None,'source':row['record_path'] if row else None,'reference_source':ref['record_path'] if ref else None})
        tables['ablation']=points
        write_csv(out/'ablation_terminal.csv',points,list(points[0]) if points else [])
        fig,ax=plt.subplots(figsize=(10,4))
        labels=list(dict.fromkeys(p['method']+'/'+p['run_id'] for p in points))
        for index,label in enumerate(labels):
            values=[p['paired_difference_reference'] for p in points if p['method']+'/'+p['run_id']==label and p['paired_difference_reference'] is not None]
            ax.scatter([index]*len(values),values)
        ax.axhline(0,color='gray');ax.set_xticks(range(len(labels)),labels,rotation=15,ha='right',fontsize=7)
        ax.set_ylabel('Paired Q difference from matched Ours reference');ax.set_title('Independent generation ablations; exploratory, valid pairs only')
        fig.tight_layout();fig.savefig(out/'ablation_terminal.png',dpi=150);plt.close(fig)
    replay=read(ROOT/'replay_status.json',{})
    if replay.get('status')=='complete':
        points=[]
        for result in replay['results']:
            row=result['test_result_record'];base=result['baseline_test_record']
            proposal_prefix=str(Path(result['proposal_folder']).relative_to(ROOT))+'/'
            relevant=[c for c in calls if c['source'].startswith(proposal_prefix) or (c['method']==result['method'] and c['run_id']==result['run_id'])]
            points.append({**{k:result[k] for k in ('method','run_id','start_id','proposal_repeat','candidate_id','paired_valid','gain_over_same_H_start','functional_non_degradation','reused_H_start')},'scene_id':row['scene_id'],'status':row['status'],'Q':row['metrics']['overall'],'H_start_Q':base['metrics']['overall'],'functional_pass':row['functional']['functional_pass'],'H_start_functional_pass':base['functional']['functional_pass'],'actual_cli_sessions_excluding_shared_H_start':len(relevant),'known_tokens':sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in relevant),'unknown_usage_calls':sum(c['input_tokens'] is None for c in relevant),'source':str(Path(row['folder']).relative_to(ROOT)/'record.json')})
        tables['replay']=points
        write_csv(out/'frozen_meta_replay.csv',points,list(points[0]) if points else [])
        fig,ax=plt.subplots(figsize=(9,4))
        keys=list(dict.fromkeys((p['start_id'],p['proposal_repeat']) for p in points))
        differences=[]
        for index,key in enumerate(keys):
            initial=next((p for p in points if (p['start_id'],p['proposal_repeat'])==key and p['method']=='M_initial'),None)
            descendant=next((p for p in points if (p['start_id'],p['proposal_repeat'])==key and p['method']=='M_descendant'),None)
            valid=bool(initial and descendant and initial['paired_valid'] and descendant['paired_valid'])
            differences.append({'start_id':key[0],'proposal_repeat':key[1],'paired_valid':valid,'descendant_minus_initial_gain':descendant['gain_over_same_H_start']-initial['gain_over_same_H_start'] if valid else None,'descendant_minus_initial_functional_pass':int(descendant['functional_pass'])-int(initial['functional_pass']) if initial and descendant else None})
            for offset,method in [(-.12,'M_initial'),(.12,'M_descendant')]:
                point=next((p for p in points if (p['start_id'],p['proposal_repeat'])==key and p['method']==method),None)
                if point and point['paired_valid']:
                    ax.scatter(index+offset,point['gain_over_same_H_start'],color='C0' if offset<0 else 'C1',marker='o' if point['functional_non_degradation'] else 'x',label=method if index==0 else None)
        ax.axhline(0,color='gray');ax.set_xticks(range(len(keys)),[f'{s}/proposal{r}' for s,r in keys]);ax.set_ylabel('Selected H test Q minus identical H_start')
        ax.set_title('Frozen M replay; circles: function preserved, crosses: regression')
        if any(p['paired_valid'] for p in points):ax.legend()
        fig.tight_layout();fig.savefig(out/'frozen_meta_replay.png',dpi=150);plt.close(fig)
        tables['replay_paired']=differences
        write_csv(out/'frozen_meta_paired.csv',differences,list(differences[0]) if differences else [])
    external=read(ROOT/'external_status.json',{})
    if external.get('status')=='complete':
        points=[]
        for item in external['records']:
            row=item['reconstruction'];judge=item['adapted_evaluation']
            points.append({'method':item['method'],'scene_id':item['task_id'],'reconstruction_status':row['status'],'Q':row['metrics']['overall'],'functional_pass':row['functional']['functional_pass'],'judge_status':judge['status'],'adapted_score_0_100':judge.get('adapted_fused_score_0_100'),'rubric_score_0_100':judge.get('rubric_score_0_100'),'dimension_score_0_100':judge.get('dimension_score_0_100'),'official_score':None,'reuse_of':row.get('reuse_of'),'reuse_basis':row.get('reuse_basis'),'source':str(Path(row['folder']).relative_to(ROOT)/'record.json')})
        tables['external']=points
        write_csv(out/'blenderworld_adapted.csv',points,list(points[0]) if points else [])
    (out/'additional_stage_analysis.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    return tables

def figures_and_slots(out,rows,calls,archive,choices,improvement,manifest):
    import matplotlib.pyplot as plt
    terminal=[r for r in rows if r['split']=='test' and any(all(r[k]==c[k] for k in ('method','run_id','candidate_id')) for c in choices)]
    terminal_points=[{**{k:r[k] for k in ('method','run_id','candidate_id','scene_id','status')},'Q':r['metrics']['overall'],'functional_pass':r['functional']['functional_pass'],'reuse_of':r.get('reuse_of')} for r in terminal]
    write_csv(out/'terminal_quality.csv',terminal_points,['method','run_id','candidate_id','scene_id','status','Q','functional_pass','reuse_of'])
    fig,ax=plt.subplots(figsize=(9,4))
    for index,method in enumerate(METHODS):
        for ri,run in enumerate(('r1','r2')):
            data=[r['Q'] for r in terminal_points if r['method']==method and r['run_id']==run and r['Q'] is not None]
            ax.scatter([index+(ri-.5)*.2]*len(data),data,label=run if index==0 else None,marker=('o','x')[ri],color=('C0','C1')[ri])
    ax.set_xticks(range(4),METHODS,fontsize=8);ax.set_ylabel('Q; measured terminal scenes only');ax.legend();fig.tight_layout();fig.savefig(out/'terminal_quality.png',dpi=150);plt.close(fig)
    functions=[]
    for method in METHODS:
        for run in ('r1','r2'):
            data=[r for r in terminal if r['method']==method and r['run_id']==run]
            functions.append({'method':method,'run_id':run,'all_scheduled_scenes':4,'recorded_scenes':len(data),**{key:sum(bool(r['functional'].get(key)) for r in data) if len(data)==4 else None for key in ('structure_pass','material_pass','composite_pass','functional_pass')}})
    write_csv(out/'terminal_functional.csv',functions,list(functions[0]))
    fig,ax=plt.subplots(figsize=(9,4))
    for i,method in enumerate(METHODS):
        for j,run in enumerate(('r1','r2')):
            item=next(r for r in functions if r['method']==method and r['run_id']==run)
            if item['functional_pass'] is not None:ax.scatter(i+(j-.5)*.2,item['functional_pass']/4,color=('C0','C1')[j],marker=('o','x')[j]);ax.text(i+(j-.5)*.2,item['functional_pass']/4+.03,f"{run}: {item['functional_pass']}/4",fontsize=7,ha='center')
    ax.set_xticks(range(4),METHODS,fontsize=8);ax.set_ylim(-.05,1.2);ax.set_ylabel('All three fixed functional requirements passed / 4 test scenes');fig.tight_layout();fig.savefig(out/'terminal_functional.png',dpi=150);plt.close(fig)
    rates=[]
    for method in METHODS[1:]:
        data=[r for r in improvement if r['method']==method]
        rates.append({'method':method,'scheduled_repeats':2,'completed_repeat_pairs':sum(r['complete_valid_improvement'] is not None for r in data),'valid_improvements':sum(r['complete_valid_improvement'] is True for r in data),'fraction_of_all_scheduled':sum(r['complete_valid_improvement'] is True for r in data)/2 if all(r['complete_valid_improvement'] is not None for r in data) else None})
    write_csv(out/'complete_improvement_rate.csv',rates,list(rates[0]))
    fig,ax=plt.subplots(figsize=(9,3.8))
    for i,r in enumerate(rates):
        if r['fraction_of_all_scheduled'] is not None:
            ax.bar(i,r['fraction_of_all_scheduled']);ax.text(i,r['fraction_of_all_scheduled']+.04,f"{r['valid_improvements']}/2",ha='center')
        else:ax.text(i,.2,'pending',ha='center')
    ax.set_xticks(range(3),METHODS[1:],fontsize=8);ax.set_ylim(0,1.15);ax.set_ylabel('Complete valid improvement / 2 R&D runs');fig.tight_layout();fig.savefig(out/'complete_improvement_rate.png',dpi=150);plt.close(fig)
    rd=[]
    for run in ('r1','r2'):
        h0=[r for r in rows if r['run_id']==run and r['method']=='fixed_h0' and r['split']=='selection']
        if len(h0)!=2:continue
        base=sum(r['metrics']['overall'] for r in h0 if r['metrics']['valid'])/2
        shared=[c for c in calls if c['method']=='fixed_h0' and c['run_id']==run and any('/'+s+'/' in c['source'] for s in ('development','selection'))]
        for method in METHODS[1:]:
            selected_quality=base
            cumulative=list(shared)
            for k in (1,2):
                item=next((a for a in archive if a['method']==method and a['run_id']==run and a['candidate_id']==f'C{k}'),None)
                if item is None:continue
                added=[c for c in calls if c['method']==method and c['run_id']==run and f'/C{k}/' in c['source'] and '/test/' not in c['source']]
                cumulative+=added
                if item.get('accepted'):selected_quality=item['selection']['endpoint_quality']
                known=sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in cumulative if isinstance(c['input_tokens'],int) and isinstance(c['output_tokens'],int))
                reconstruction=[r for r in rows if r['run_id']==run and r['split'] in ('development','selection') and (r['method']=='fixed_h0' or (r['method']==method and r['candidate_id'] in [f'C{j}' for j in range(1,k+1)]))]
                folders=[ROOT/r['directory'] for r in reconstruction]
                ledgers=[p for folder in folders for p in folder.glob('*/render_ledger.json') if not p.is_symlink()]
                ledgers += [p for j in range(1,k+1) for p in (ROOT/'candidates'/run/method/f'C{j}').glob('probes/*/render_ledger.json')]
                attempts=sum(len(list(f.glob('steps/*/build.py'))) for f in folders)+sum(read(p).get('render_attempts',0) for p in ledgers)
                frames=sum(len(list(f.glob('steps/*/final.png'))) for f in folders)+sum(read(p).get('renders_completed',0) for p in ledgers)
                rd.append({'method':method,'run_id':run,'candidate_id':f'C{k}','candidate_status':item['status'],'candidate_selection_Q':item.get('selection',{}).get('endpoint_quality'),'retained_selection_Q':selected_quality,'selection_gain_from_H0':selected_quality-base,'cumulative_cli_sessions_including_shared_H0':len(cumulative),'cumulative_known_tokens':known,'usage_unknown_calls':sum(c['input_tokens'] is None for c in cumulative),'cumulative_cli_seconds':sum(c['seconds'] or 0 for c in cumulative),'cumulative_reconstruction_seconds':sum(r['seconds'] for r in reconstruction),'cumulative_render_attempts_upper_bound':attempts,'cumulative_render_frames':frames,'device':'+'.join(sorted({r.get('device','CPU') for r in reconstruction} | {h['device'] for r in reconstruction for h in r.get('render_device_history',[])} | {r.get('functional_device_mapping',{}).get('device','CPU') for r in reconstruction if r.get('functional_device_mapping')})),'shared_H0_cli_sessions':len(shared),'accepted':item['accepted'],'terminal_joint_pass':None})
    fields=['method','run_id','candidate_id','candidate_status','candidate_selection_Q','retained_selection_Q','selection_gain_from_H0','cumulative_cli_sessions_including_shared_H0','cumulative_known_tokens','usage_unknown_calls','cumulative_cli_seconds','cumulative_reconstruction_seconds','cumulative_render_attempts_upper_bound','cumulative_render_frames','device','shared_H0_cli_sessions','accepted','terminal_joint_pass']
    write_csv(out/'rd_cost_gain.csv',rd,fields)
    fig,ax=plt.subplots(figsize=(9,4))
    for run in ('r1','r2'):
        for method in METHODS[1:]:
            points=[r for r in rd if r['method']==method and r['run_id']==run]
            if points:ax.plot([r['cumulative_cli_sessions_including_shared_H0'] for r in points],[r['selection_gain_from_H0'] for r in points],'.-',label=method+'/'+run)
    if rd:ax.legend(fontsize=7)
    else:ax.text(.5,.5,'Candidate search pending',transform=ax.transAxes,ha='center')
    ax.axhline(0,color='gray');ax.set_xlabel('Actual R&D CLI sessions, including shared H0 and proposer calls');ax.set_ylabel('Retained Selection endpoint Q minus H0');fig.tight_layout();fig.savefig(out/'rd_cost_gain.png',dpi=150);plt.close(fig)
    slots=[]
    for run in ('r1','r2'):
        for method in METHODS:
            for candidate in (['H0'] if method=='fixed_h0' else ['C1','C2']):
                proposal=next((a for a in archive if a['run_id']==run and a['method']==method and a['candidate_id']==candidate),{})
                for scene in [s for s in manifest if s['split'] in ('development','selection')]:
                    found=next((r for r in rows if r['run_id']==run and r['method']==method and r['candidate_id']==candidate and r['scene_id']==scene['scene_id'] and r['split']==scene['split']),None)
                    status=found['status'] if found else ('not_run_proposal_failed' if proposal.get('status') in ('proposal_failed','meta_execution_failed') else 'pending')
                    slots.append({'method':method,'run_id':run,'candidate_id':candidate,'scene_id':scene['scene_id'],'split':scene['split'],'status':status,'source':found['record_path'] if found else None})
            choice=next((c for c in choices if c['run_id']==run and c['method']==method),{})
            for scene in [s for s in manifest if s['split']=='test']:
                found=next((r for r in terminal if r['method']==method and r['run_id']==run and r['scene_id']==scene['scene_id']),None)
                slots.append({'method':method,'run_id':run,'candidate_id':choice.get('candidate_id'),'scene_id':scene['scene_id'],'split':'test','status':found['status'] if found else 'pending','source':found['record_path'] if found else None})
    write_csv(out/'main_scheduled.csv',slots,list(slots[0]))
    return rates,slots

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=collect(ROOT);out=ROOT/'reports';out.mkdir(exist_ok=True)
    cfg=read(ROOT/'config.json');manifest=read(ROOT/'manifest.json');test_ids=[s['scene_id'] for s in manifest if s['split']=='test'];archive=read(ROOT/'archive.json',[])
    choices=read(ROOT/'selections.json',[])
    tests=[r for r in rows if r['split']=='test' and any(r['method']==c['method'] and r['run_id']==c['run_id'] and r['candidate_id']==c['candidate_id'] for c in choices)];paired=[];improvement=[]
    for method in ['sceneevolve_cli','generic_rsi','scene_rsi_pilot']:
        for run in ['r1','r2']:
            base={r['scene_id']:r for r in tests if r['method']=='fixed_h0' and r['run_id']==run}
            cand={r['scene_id']:r for r in tests if r['method']==method and r['run_id']==run}
            deltas=[];functional_delta=0;complete=True
            for sid in test_ids:
                a,b=base.get(sid),cand.get(sid)
                measured=bool(a and b and a['metrics']['valid'] and b['metrics']['valid'])
                delta=b['metrics']['overall']-a['metrics']['overall'] if measured else None
                paired.append({'method':method,'run_id':run,'scene_id':sid,'paired_valid':measured,'quality_difference':delta,'baseline_status':a['status'] if a else 'pending','candidate_status':b['status'] if b else 'pending','baseline_device':a.get('device') if a else None,'candidate_device':b.get('device') if b else None,'same_device_class':a.get('device')==b.get('device') if a and b else None})
                complete &= measured
                if measured:deltas.append(delta)
                if a and b:functional_delta+=int(b['functional']['functional_pass'])-int(a['functional']['functional_pass'])
            gain=sum(deltas)/len(deltas) if deltas else None
            improvement.append({'method':method,'run_id':run,'all_scheduled_pairs':len(test_ids),'valid_pairs':len(deltas),'conditional_gain':gain,'functional_pass_count_difference':functional_delta if base and cand else None,'complete_valid_improvement':bool(complete and gain is not None and gain>cfg['pilot']['quality_tolerance'] and functional_delta>=0) if len(base)==len(test_ids) and len(cand)==len(test_ids) else None})
    write_csv(out/'paired.csv',paired,['method','run_id','scene_id','paired_valid','quality_difference','baseline_status','candidate_status','baseline_device','candidate_device','same_device_class'])
    write_csv(out/'effective_improvement.csv',improvement,list(improvement[0]) if improvement else [])
    fig,ax=plt.subplots(figsize=(9,4));valid=[r for r in improvement if r['conditional_gain'] is not None]
    if valid:
        ax.scatter(range(len(valid)),[r['conditional_gain'] for r in valid]);ax.set_xticks(range(len(valid)),[r['method']+'/'+r['run_id'] for r in valid],rotation=20,ha='right',fontsize=8);ax.axhline(0,color='gray');ax.axhline(cfg['pilot']['quality_tolerance'],color='green',linestyle='--')
    else:ax.text(.5,.5,'Terminal comparison pending: no paired outcomes',transform=ax.transAxes,ha='center')
    ax.set_ylabel('Selected H minus common H0, paired Q');fig.tight_layout();fig.savefig(out/'effective_improvement.png',dpi=150);plt.close(fig)
    calls=[]
    for path in sorted(ROOT.rglob('session.json')):
        request=path.with_name('request.json')
        if not request.exists():continue
        s=read(path);parts=path.relative_to(ROOT).parts
        if 'retired' in parts:parts=parts[parts.index('retired')+1:]
        method=next((m for m in ['fixed_h0','sceneevolve_cli','generic_rsi','scene_rsi_pilot'] if m in parts),'preparation_or_supplement');run=next((r for r in ['r1','r2'] if r in parts),None)
        if parts[0] in ('results','candidates'):run,method=parts[1:3]
        mapping=read(path.parent.parent/'mapping_for_report.json',read(path.parent.parent/'mapping.json',{}))
        method=mapping.get('method',method);run=mapping.get('run_id',run)
        calls.append({'method':method,'run_id':run,'role':s.get('role'),'requested_model':s.get('requested_model'),'reported_model':s.get('actual_model'),'effort':s.get('reasoning_effort'),'status':s.get('status'),'exit_code':s.get('exit_code'),'error':s.get('error'),'seconds':s.get('seconds'),'started':s.get('started'),'finished':s.get('finished'),'input_tokens':s.get('input_tokens') if isinstance(s.get('input_tokens'),int) else None,'output_tokens':s.get('output_tokens') if isinstance(s.get('output_tokens'),int) else None,'observable_model_rounds':s.get('observable_model_turns'),'observable_cli_turns':s.get('observable_cli_turns'),'tools':s.get('tool_calls',len(s.get('tool_events',[]))),'source':str(path.relative_to(ROOT))})
        calls[-1]['preserved_service_attempt']='retired' in path.relative_to(ROOT).parts
        event_path=path.with_name('events.jsonl')
        events_text=event_path.read_text() if event_path.exists() else ''
        messages=[];malformed=None
        if s.get('status')=='failed':
            malformed=0
            for line in events_text.splitlines():
                try:event=json.loads(line)
                except json.JSONDecodeError:
                    malformed+=1;continue
                message=event.get('message') if event.get('type')=='error' else event.get('error',{}).get('message') if event.get('type')=='turn.failed' else None
                if message:messages.append(message)
        calls[-1]['cli_error_messages']=' | '.join(dict.fromkeys(messages)) or None
        calls[-1]['malformed_event_lines']=malformed
        routing_failure=s.get('status')=='failed' and 'workspace routing discovery failed' in events_text
        usage_limit=s.get('status')=='failed' and 'hit your usage limit' in events_text
        capacity=any('selected model is at capacity' in message.lower() for message in messages)
        calls[-1]['failure_category']='cli_usage_limit' if usage_limit else 'cli_workspace_routing_failure' if routing_failure else 'cli_model_capacity' if capacity else 'timeout' if 'TimeoutExpired' in str(s.get('error')) else 'other_cli_failure' if s.get('status')=='failed' else None
    write_csv(out/'calls.csv',calls,list(calls[0]) if calls else [])
    selection_access=[]
    for run in ('r1','r2'):
        for method in METHODS:
            for candidate in (['H0'] if method=='fixed_h0' else ['C1','C2']):
                prefix=f'results/{run}/{method}/{candidate}/selection/'
                measured=[r for r in rows if r['run_id']==run and r['method']==method and r['candidate_id']==candidate and r['split']=='selection']
                sessions=[c for c in calls if c['source'].startswith(prefix) or '/retired/'+prefix in c['source']]
                selection_access.append({'method':method,'run_id':run,'candidate_id':candidate,'scheduled_selection_scenes':2,'completed_fixed_evaluation_records':len(measured),'generator_cli_sessions':len(sessions),'observed_cli_turns':sum(c['observable_cli_turns'] or 0 for c in sessions),'underlying_model_rounds':None,'scope':'Reference images accessed only by fixed reconstruction/evaluation pipeline; counts are logged sessions, not internal image-view events'})
    write_csv(out/'selection_access.csv',selection_access,list(selection_access[0]))
    exports=[]
    for call_record in calls:
        if call_record['role']!='proposer':continue
        prompt_path=(ROOT/call_record['source']).with_name('prompt.txt')
        if not prompt_path.exists():continue
        text=prompt_path.read_text();marker='EXPLICIT_INPUT_JSON\n'
        if marker not in text:continue
        payload,_=json.JSONDecoder().raw_decode(text.split(marker,1)[1])
        entries=[a for a in payload.get('archive',[]) if isinstance(a.get('selection'),dict)]
        images=payload.get('attached_images',[])
        counts=[a['selection'].get('all_scheduled') for a in entries]
        known_counts=[n for n in counts if isinstance(n,int)]
        exports.append({'method':call_record['method'],'run_id':call_record['run_id'],'proposer_session':call_record['source'],'selection_aggregate_entries_disclosed':len(entries),'selection_scene_evaluations_represented':sum(known_counts) if len(known_counts)==len(counts) else None,'selection_scene_count_known_lower_bound':sum(known_counts),'selection_aggregate_entries_without_scene_count':len(counts)-len(known_counts),'raw_selection_image_attachments':sum('/selection/' in str(p) for p in images),'raw_main_test_image_attachments':sum('/test/' in str(p) for p in images),'attachment_check_basis':'Explicit attached_images paths in saved proposer payload; compact aggregate entries may omit all_scheduled, which is unknown rather than zero','source_prompt':str(prompt_path.relative_to(ROOT))})
    write_csv(out/'selection_feedback_exports.csv',exports,list(exports[0]) if exports else ['method','run_id','proposer_session','selection_aggregate_entries_disclosed'])
    costs=[]
    for run in ['r1','r2']:
        for method in ['fixed_h0','sceneevolve_cli','generic_rsi','scene_rsi_pilot']:
            selected=[c for c in calls if c['run_id']==run and c['method']==method and c['role'] in ('student','proposer') and '/test/' not in c['source'] and '/text_edit/' not in c['source']]
            costs.append({'run_id':run,'method':method,'actual_cli_sessions':len(selected),'known_tokens':sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in selected if isinstance(c['input_tokens'],int) and isinstance(c['output_tokens'],int)),'usage_unknown_calls':sum(not isinstance(c['input_tokens'],int) for c in selected),'cli_elapsed_seconds':sum(c['seconds'] or 0 for c in selected),'shared_H0_cost_note':'fixed_h0 development/selection seed data is physically generated once per repeat and shared by methods; charge separately when interpreting R&D cost'})
    write_csv(out/'development_cost.csv',costs,list(costs[0]))
    total_cost=[]
    for run,method in sorted({(str(c['run_id']),c['method']) for c in calls}):
        group=[c for c in calls if str(c['run_id'])==run and c['method']==method]
        total_cost.append({'run_id':run,'method':method,'cli_sessions':len(group),'known_input_tokens':sum(c['input_tokens'] for c in group if isinstance(c['input_tokens'],int)),'known_output_tokens':sum(c['output_tokens'] for c in group if isinstance(c['output_tokens'],int)),'unknown_usage_calls':sum(not isinstance(c['input_tokens'],int) for c in group),'failed_calls':sum(c['status']=='failed' for c in group),'cli_wall_seconds':sum(c['seconds'] or 0 for c in group),'roles':{role:sum(c['role']==role for c in group) for role in {c['role'] for c in group}}})
    write_csv(out/'method_total_cost.csv',total_cost,list(total_cost[0]) if total_cost else [])
    inference=[]
    for choice in choices:
        for row in rows:
            if row['split']!='test' or any(row[k]!=choice[k] for k in ('method','run_id','candidate_id')):continue
            reused=bool(row.get('reuse_of'));original=read(Path(row['reuse_of'])/'record.json') if reused else row
            actual=row['usage'];equivalent=original['usage']
            numeric=lambda value:value if isinstance(value,(int,float)) else None
            inference.append({'method':row['method'],'run_id':row['run_id'],'scene_id':row['scene_id'],'candidate_id':row['candidate_id'],'status':row['status'],'reused_identical_H0':reused,'physical_cli_sessions':numeric(actual.get('calls')),'physical_tokens':numeric(actual.get('total_tokens')),'physical_reconstruction_executions':numeric(actual.get('executions')),'physical_generation_seconds':0 if reused else numeric(row['runtime_status'].get('seconds')),'source_equivalent_cli_sessions':numeric(equivalent.get('calls')),'source_equivalent_tokens':numeric(equivalent.get('total_tokens')),'source_equivalent_reconstruction_executions':numeric(equivalent.get('executions')),'source_equivalent_generation_seconds':numeric(original['runtime_status'].get('seconds')),'source_device':original['device'],'source_record':str(Path(original['folder']).relative_to(ROOT)/'record.json'),'accounting_note':'Physical cost is billed once; source-equivalent cost describes the same final H0 inference when outcomes are reused, not additional billing or a speed comparison.'})
    write_csv(out/'final_inference_cost.csv',inference,list(inference[0]) if inference else ['method','run_id','scene_id','candidate_id','status','physical_cli_sessions','source_equivalent_cli_sessions','source_record'])
    additional=additional_stage_tables(out,rows,choices,calls)
    result={'method_realization':{},'paired':paired,'complete_valid_improvement':improvement,'candidates':archive,'development_cost':costs,'untested_original_candidate_joint_terminal_pass':None,'M_descendants_actually_used':[]}
    result['cli_failure_counts']={category:sum(call['failure_category']==category for call in calls) for category in sorted({call['failure_category'] for call in calls if call['failure_category']})}
    result['cli_call_log_coverage']={'raw_request_session_pairs':len(calls),'disclosed_initial_log_loss':read(ROOT/'cli_checks/initial_sandbox_failures.json',{}).get('sessions',0),'note':'The two disclosed initial failures are included in the global budget but have no recoverable original request/session logs; this table does not fabricate them.'}
    result['additional_stage_analysis']=additional
    rates,slots=figures_and_slots(out,rows,calls,archive,choices,improvement,manifest)
    result.update(complete_valid_improvement_rates=rates,main_scheduled_counts={s:sum(r['status']==s for r in slots) for s in sorted({r['status'] for r in slots})})
    for p in ROOT.glob('candidates/*/*/C2/meta_execution.json'):
        d=read(p);prior=read(p.parent.parent/'C1/proposal_result.json',{})
        effective=prior.get('M_strategy_structure_changed',False) and str(p.parent.parent/'C1/meta.py')==d['source'] and (p.parent/'proposal_call/request.json').exists()
        later=read(p.parent/'proposal_result.json',{})
        candidate=next((a for a in archive if a['run_id']==p.parent.parent.parent.name and a['method']==p.parent.parent.name and a['candidate_id']=='C2'),{})
        usable=effective and later.get('status')=='proposed' and candidate.get('development',{}).get('completed',0)>0
        result['M_descendants_actually_used'].append({'strategy_descendant_used':effective,'usable_descendant':usable,'subsequent_proposal_status':later.get('status'),'subsequent_development_successes':candidate.get('development',{}).get('completed',0),'candidate':str(p.parent.relative_to(ROOT)),'M_source_used':d['source'],'plan':d['plan']})
    for method in ['generic_rsi','scene_rsi_pilot']:
        effective=any(x['strategy_descendant_used'] and ('/'+method+'/') in x['candidate'] for x in result['M_descendants_actually_used'])
        usable=any(x['usable_descendant'] and ('/'+method+'/') in x['candidate'] for x in result['M_descendants_actually_used'])
        result['method_realization'][method]={'executed_strategy_descendant':effective,'usable_descendant':usable,'label':('generic_rsi_cli_adapted' if effective else 'generic_fixed_meta') if method=='generic_rsi' else 'scene_rsi_pilot','note':'本轮未获得可用元策略后代' if not usable else '后代策略已用于下一次提案且产生可运行H；尚不等于元能力提高'}
    (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    ledger=current();ledger['all_scheduled']=cfg['pilot'].get('scheduled_main_reconstructions');ledger['all_scheduled_scope']='main planned reconstruction slots only; smoke and additional stages are separate';ledger['main_scheduled_counts']=result['main_scheduled_counts'];(ROOT/'ledger.json').write_text(json.dumps(ledger,indent=2))
    return result

if __name__=='__main__':main()
