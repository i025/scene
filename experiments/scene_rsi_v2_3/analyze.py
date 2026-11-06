"""Offline raw tables, all-case figures and Chinese report; never calls models or Blender."""
from collections import Counter
from pathlib import Path
import csv
import html
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/scene-rsi-v23-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from skimage.metrics import structural_similarity,peak_signal_noise_ratio
from common import ROOT,read,write,current
from experiment import METHODS,regions
from meta import MENU

LABEL={'fixed':'Fixed','structured':'Structured','active':'Active'}
COLORS=['#718096','#d69e2e','#287f8e']


def table(path,rows):
    write(path.with_suffix('.json'),rows)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.with_suffix('.csv').open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=keys);writer.writeheader()
        writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows)


def visual(reference,image):
    if not image.exists():return {'psnr':None,'ssim':None,'lpips':None,'dinov2':None}
    a=np.asarray(Image.open(reference).convert('RGB'),dtype=np.float32)/255
    b=np.asarray(Image.open(image).convert('RGB'),dtype=np.float32)/255
    p=peak_signal_noise_ratio(a,b,data_range=1)
    return {'psnr':float(p) if np.isfinite(p) else None,'psnr_perfect_match':not np.isfinite(p),'ssim':float(structural_similarity(a,b,channel_axis=2,data_range=1)),'lpips':None,'dinov2':None}


def collect():
    truth=read(ROOT/'configs/truth_evaluator_only.json') if (ROOT/'configs/truth_evaluator_only.json').exists() else []
    rows=[];probes=[];calls=[]
    for label in truth:
        case=label['scene_id'];folder=ROOT/'tasks'/case
        findings=read(folder/'common_diagnosis/response.txt') if (folder/'common_diagnosis/response.txt').exists() else None
        for method in METHODS:
            dest=folder/method;result=read(dest/'result.json') if (dest/'result.json').exists() else None
            common_failure=(folder/'common_failure.json').exists()
            status=result['status'] if result else 'failed' if common_failure else 'running' if (dest/'stage1.json').exists() else 'not_started'
            decision=read(dest/'stage2.json') if (dest/'stage2.json').exists() else None
            plan=read(dest/'stage1.json')['plan'] if (dest/'stage1.json').exists() else None
            observations=read(dest/'observations.json') if (dest/'observations.json').exists() else []
            evaluation=read(dest/'evaluation.json') if (dest/'evaluation.json').exists() else None
            selected=decision['decision']['selected_code_module'] if decision else None
            exact=selected==label['exact_module'] if selected is not None else None
            decided=selected not in [None,'unresolved']
            correct_discrimination=bool(exact and observations and any(h['state']=='contradicted' for h in decision['decision']['hypothesis_update'])) if decision else None
            separated=0;consistent=0;prediction_n=0;empirical=0;true_matches=0;true_n=0
            for observation in observations:
                request=observation['request'];tool=request['probe'];value=observation['measurement']['outcome'] if observation['measurement'] else None
                score=request['predicted_pair_separation'];separated+=score>0
                fits=[]
                for hypothesis in plan['predictions_frozen']:
                    prediction=hypothesis['predictions'][tool];match=(prediction['lower']<=value<=prediction['upper']) if value is not None else None
                    if match is not None:
                        prediction_n+=1;consistent+=match;fits.append(match)
                        if hypothesis['module']==label['exact_module']:true_n+=1;true_matches+=match
                    probes.append({'scene_id':case,'method':method,'tool':tool,'object_id':request['object_id'],'hypothesis':hypothesis['id'],'hypothesis_module':hypothesis['module'],
                          'lower':prediction['lower'],'upper':prediction['upper'],'outcome':value,'prediction_matched':match,'predeclared_pair_separation':score,'status':observation['status']})
                empirical+=bool(fits and any(fits) and not all(fits))
            process_paths=[dest/'process.json',*sorted((dest/'probes').glob('*/process.json'))]
            process_seconds=sum(read(p)['seconds'] for p in process_paths if p.exists())
            probe_seconds=sum(read(p)['seconds'] for p in (dest/'probes').glob('*/process.json'))
            own_call=read(dest/'repair_call/session.json') if (dest/'repair_call/session.json').exists() else None
            shared_call=read(folder/'common_diagnosis/session.json') if (folder/'common_diagnosis/session.json').exists() else None
            allocated_model_seconds=(own_call['seconds'] if own_call and 'seconds' in own_call else 0)+(shared_call['seconds']/3 if shared_call and 'seconds' in shared_call else 0)
            completed=status=='completed';terminal=status in ['completed','failed','timeout','invalid']
            row={'method':method,'run_id':'v23_mechanism_1','candidate_id':'one_shared_proposal','parent':'H0','H_version':case+'/H0.py','M_version':'engineered_v2_3','scene_id':case,'fault_family':label['family'],'source_template':label['template'],
                 'split':'independent_transfer','status':status,'candidate_generated':(dest/'candidate.py').exists(),'failure_stage':result['failure_stage'] if result else 'common_diagnosis' if common_failure else None,'failure_reason':result['reason'] if result else None,
                 'exact_module_truth':label['exact_module'],'initial_module':findings['initial_module'] if findings else None,'initial_module_hit':findings['initial_module']==label['exact_module'] if findings else None,'selected_module':selected,'exact_module_hit':exact,'related_module_hit':selected in label['related_modules'] if selected is not None else None,
                 'diagnosis_decided':decided,'wrong_decided_diagnosis':decided and not exact,
                 'initial_confidence':findings['initial_confidence'] if findings else None,
                 'wrong_high_initial_confidence':findings['initial_confidence']>=.7 and findings['initial_module']!=label['exact_module'] if findings else None,'object_applicable':label['object_applicable'],
                 'object_top1_hit':findings['object_id'] in label['object_ids'] if findings and label['object_applicable'] else None,
                 'source_pass':evaluation['source']['all_pass'] if evaluation else None,'effective_shared_repair':result['effective_shared_repair'] if result else None,
                 'transfer_repair':result['transfer_repair'] if result else None,'regression':result['regression'] if result else None,
                 'end_to_end_utility':int(result['effective_shared_repair'] is True) if result and terminal else 0 if common_failure else None,
                 'probes_requested':len(plan['probes']) if plan else None,'probes_executed':sum(o['status']=='completed' for o in observations),
                 'preseparated_probes':separated,'observed_discriminating_probes':empirical,'correct_hypothesis_discrimination':correct_discrimination,
                 'prediction_consistent_n':consistent,'prediction_n':prediction_n,'true_hypothesis_prediction_matched_n':true_matches,'true_hypothesis_prediction_n':true_n,
                 'true_module_in_hypothesis_set':any(h['module']==label['exact_module'] for h in findings['hypotheses']) if findings else None,
                 'probes_with_numeric_outcome':sum(o['status']=='completed' and o['measurement']['outcome'] is not None for o in observations),'decision_changed_by_observations':decision['module_changed_by_observations'] if decision else None,
                 'changed_module_count':result.get('changed_module_count') if result else None,'changed_regions':result.get('changed_regions') if result else None,
                 'diagnosis_region_changed':result.get('diagnosis_region_changed') if result else None,
                 'changed_regions_outside_injected_function':[name for name in result['changed_regions'] if name!=(label['exact_module'].rsplit('.',1)[0] if label['exact_module'].startswith('SceneCompiler.emit.') else label['exact_module'])] if result and 'changed_regions' in result else None,
                 'patch_scope_limit':'Function region text comparison only; coordinated changes outside injected function are not automatically unnecessary or harmful','device':'CPU','threads':2,'blender_seconds':process_seconds,'probe_seconds':probe_seconds,'allocated_model_seconds':allocated_model_seconds,'research_seconds_excluding_shared_fixture_setup':process_seconds+allocated_model_seconds,
                 'actual_render_frames':sum(read(p)['renders_completed'] for p in dest.rglob('render_ledger.json')),
                 'invalid_or_unmeasured_probe_count':sum(o['status']!='completed' or o['measurement']['outcome'] is None for o in observations),
                 'function_checks':evaluation['transfer']['gates'] if evaluation else None,'visual_split':'source',
                 **visual(folder/'reference.png',dest/'source_repaired.png')}
            rows.append(row)
    for path in sorted(ROOT.rglob('session.json')):
        if 'request.json' not in [p.name for p in path.parent.iterdir()]:continue
        session=read(path);rel=path.relative_to(ROOT);case=rel.parts[1] if rel.parts[0]=='tasks' else 'smoke_connectivity'
        method=next((m for m in METHODS if m in rel.parts),'shared')
        calls.append({'path':str(rel),'scene_id':case,'method':method,'role':session['role'],'requested_model':session['requested_model'],'actual_model':session['actual_model'],'effort':session['reasoning_effort'],'status':session['status'],
                      'input_tokens':session['input_tokens'] if isinstance(session['input_tokens'],int) else None,'output_tokens':session['output_tokens'] if isinstance(session['output_tokens'],int) else None,'observable_turns':session['observable_cli_turns'],'tool_calls':session['tool_calls'],'seconds':session['seconds'] if 'seconds' in session else None,'cli_sessions':1})
    return rows,probes,calls


def contact(rows):
    cases=list(dict.fromkeys(r['scene_id'] for r in rows));w=256;h=225
    canvas=Image.new('RGB',(w*5,(len(cases)+1)*h),'white');draw=ImageDraw.Draw(canvas)
    for col,title in enumerate(['Reference','Faulty H0','Fixed','Structured','Active']):draw.text((col*w+8,15),title,fill='black')
    for index,case in enumerate(cases):
        folder=ROOT/'tasks'/case
        paths=[folder/'reference.png',folder/'final.png',*[folder/m/'source_repaired.png' for m in METHODS]]
        for col,path in enumerate(paths):
            y=(index+1)*h
            if path.exists():canvas.paste(Image.open(path).convert('RGB'),(col*w,y))
            else:draw.rectangle((col*w+4,y+4,(col+1)*w-4,y+188),outline='#aa3333');draw.text((col*w+10,y+50),'Missing output',fill='#aa3333')
            label=case+' reference' if col==0 else case+' H0 injected fault' if col==1 else case+' '+next(r['status'] for r in rows if r['scene_id']==case and r['method']==METHODS[col-2])
            draw.text((col*w+7,y+195),label,fill='black')
            if col>=2:
                row=next(r for r in rows if r['scene_id']==case and r['method']==METHODS[col-2]);draw.text((col*w+7,y+210),'P1  source SSIM='+str(round(row['ssim'],4) if row['ssim'] is not None else None),fill='black')
    canvas.save(ROOT/'figures/all_cases_contact.png')


def bars(ax,summary,key,title):
    values=[];texts=[]
    for method in METHODS:
        n,d=summary[method][key];values.append(n/d if d else 0);texts.append(f'{n}/{d}' if d else 'pending')
    ax.bar(range(3),values,color=COLORS)
    for i,(v,t) in enumerate(zip(values,texts)):ax.text(i,v+.025,t+(' pending' if summary[METHODS[i]]['terminal']<summary[METHODS[i]]['scheduled'] else ''),ha='center',fontsize=10)
    field={'object_top1':'object_top1_hit','exact_module':'exact_module_hit','correct_discrimination':'correct_hypothesis_discrimination','diagnosis_coverage':'diagnosis_decided','effective_repair':'effective_shared_repair','transfer_repair':'transfer_repair','regression':'regression'}[key]
    raw=read(ROOT/'metrics/scene_metrics.json')
    for i,method in enumerate(METHODS):
        points=[int(r[field]) for r in raw if r['method']==method and r[field] is not None]
        if points:ax.scatter(i+np.linspace(-.17,.17,len(points)),points,s=17,facecolors='white',edgecolors='#333333',zorder=4)
    ax.set_xticks(range(3),[LABEL[m] for m in METHODS]);ax.set_ylim(0,1.17);ax.set_title(title);ax.set_ylabel('Fraction')


def main():
    for name in ['metrics','figures','reports']:(ROOT/name).mkdir(exist_ok=True)
    rows,probes,calls=collect();baseline_rows=[]
    for case in dict.fromkeys(r['scene_id'] for r in rows):
        folder=ROOT/'tasks'/case;baseline_rows.append({'scene_id':case,'split':'source','method':'faulty_H0',**visual(folder/'reference.png',folder/'final.png')})
    table(ROOT/'metrics/baseline_source_metrics',baseline_rows)
    table(ROOT/'metrics/scene_metrics',rows);table(ROOT/'metrics/probe_predictions',probes);table(ROOT/'metrics/calls',calls)
    summary={}
    for method in METHODS:
        group=[r for r in rows if r['method']==method];n=len(group);terminal=[r for r in group if r['status'] in ['completed','failed','timeout','invalid']];valid=[r for r in group if r['status']=='completed'];decided=[r for r in group if r['diagnosis_decided']]
        owned=[c for c in calls if c['method']==method and c['scene_id'].startswith('task')];shared=[c for c in calls if c['method']=='shared' and c['scene_id'].startswith('task')]
        summary[method]={'scheduled':n,'candidates_generated':sum(r['candidate_generated'] for r in group),'terminal':len(terminal),'completed':len(valid),'failed':len(terminal)-len(valid),'status_counts':dict(Counter(r['status'] for r in group)),
            'conditional_source_mean_ssim':float(np.mean([r['ssim'] for r in valid if r['ssim'] is not None])) if any(r['ssim'] is not None for r in valid) else None,
            'conditional_source_finite_mean_psnr':float(np.mean([r['psnr'] for r in valid if r['psnr'] is not None])) if any(r['psnr'] is not None for r in valid) else None,
            'source_psnr_perfect_match_count':sum(r.get('psnr_perfect_match',False) for r in valid),
            'initial_exact_module':[sum(r['initial_module_hit'] is True for r in group),n],'exact_module':[sum(r['exact_module_hit'] is True for r in group),n],'related_module':[sum(r['related_module_hit'] is True for r in group),n],
            'object_top1':[sum(r['object_top1_hit'] is True for r in group),sum(r['object_applicable'] for r in group)],
            'diagnosis_coverage':[len(decided),n],'decided_accuracy':[sum(r['exact_module_hit'] is True for r in decided),len(decided)],
            'wrong_decided':[sum(r['wrong_decided_diagnosis'] for r in group),n],
            'effective_repair':[sum(r['effective_shared_repair'] is True for r in group),n],'transfer_repair':[sum(r['transfer_repair'] is True for r in group),n],
            'regression':[sum(r['regression'] is True for r in valid),len(valid)],
            'correct_discrimination':[sum(r['correct_hypothesis_discrimination'] is True for r in group),n],
            'observed_discriminating_probe':[sum(r['observed_discriminating_probes'] for r in group),sum(r['probes_executed'] for r in group)],
            'preseparated_probe':[sum(r['preseparated_probes'] for r in group),sum(r['probes_requested'] or 0 for r in group)],
            'prediction_consistency':[sum(r['prediction_consistent_n'] for r in group),sum(r['prediction_n'] for r in group)],
            'true_hypothesis_prediction_consistency':[sum(r['true_hypothesis_prediction_matched_n'] for r in group),sum(r['true_hypothesis_prediction_n'] for r in group)],
            'wrong_high_initial_confidence':[sum(r['wrong_high_initial_confidence'] is True for r in group),n],
            'invalid_programs':sum(r['status']=='invalid' for r in group),'candidate_execution_failures':sum(r['failure_stage']=='candidate_execution' for r in group),'regression_unmeasured':sum(r['regression'] is None for r in group),
            'own_cli':len(owned),'allocated_common_cli':len(shared)/3,'actual_shared_cli_counted_once':len(shared),
            'known_own_tokens':sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in owned),
            'own_model_seconds':sum(c['seconds'] for c in owned if c['seconds'] is not None),'blender_seconds':sum(r['blender_seconds'] for r in group),'actual_render_frames':sum(r['actual_render_frames'] for r in group),'changed_regions':[r['changed_module_count'] for r in group]}
    matched_cases=[r['scene_id'] for r in rows if r['method']=='active' and r['probes_executed']==2 and next(x for x in rows if x['scene_id']==r['scene_id'] and x['method']=='fixed')['probes_executed']==2]
    write(ROOT/'metrics/actual_probe_count_matched_subset.json',{'scene_ids':matched_cases,'n':len(matched_cases),'meaning':'Fixed and Active both actually executed two probes; main comparison otherwise matches budget caps, not necessarily actual usage.'})
    candidate_rows=[{k:r[k] for k in ['method','run_id','scene_id','candidate_id','parent','H_version','M_version','status','candidate_generated','failure_stage','failure_reason','effective_shared_repair','transfer_repair','regression','changed_regions','changed_regions_outside_injected_function','diagnosis_region_changed','actual_render_frames','research_seconds_excluding_shared_fixture_setup']} for r in rows]
    table(ROOT/'metrics/candidates',candidate_rows)
    write(ROOT/'metrics/summary.json',summary)
    ledger=current()
    ledger['observable_cli_turns']=sum(c['observable_turns'] for c in calls) if all(c['observable_turns'] is not None for c in calls) else None
    write(ROOT/'metrics/call_totals.json',ledger)
    if not rows:return
    contact(rows)
    plt.rcParams.update({'font.size':10})
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for ax,key,title in zip(axes.flat,['object_top1','exact_module','correct_discrimination','diagnosis_coverage'],['Object localization (same initial report)','Final module after updater','Correct discrimination / scheduled','Committed final diagnosis']):bars(ax,summary,key,title)
    fig.suptitle('Common initial module diagnosis: 10/10 in every arm. Fixed final labels are unresolved, not wrong.',fontsize=10)
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(ROOT/'figures/figure2_diagnosis.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for ax,key,title in zip(axes,['effective_repair','transfer_repair','regression'],['Effective shared repair','Independent scene transfer','New regression | executed']):bars(ax,summary,key,title)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure3_repair.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4));cost_points=[]
    for method,color in zip(METHODS,COLORS):
        group=[r for r in rows if r['method']==method];x=[];y=[];cost=0;benefit=0
        for r in group:
            owned=[c for c in calls if c['method']==method and c['scene_id']==r['scene_id']];shared=[c for c in calls if c['method']=='shared' and c['scene_id']==r['scene_id']]
            cost+=sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in owned)+sum((c['input_tokens'] or 0)+(c['output_tokens'] or 0) for c in shared)/3
            benefit+=r['effective_shared_repair'] is True;x.append(cost);y.append(benefit)
            cost_points.append({'method':method,'scene_id':r['scene_id'],'cumulative_observable_tokens_common_allocated_one_third':cost,'cumulative_effective_repairs':benefit,'actual_probe_count':r['probes_executed'],'allocated_research_seconds':r['research_seconds_excluding_shared_fixture_setup']})
        axes[0].plot(x,y,'o-',label=LABEL[method],color=color)
    table(ROOT/'metrics/cost_curve',cost_points)
    axes[0].set(xlabel='Cumulative observable tokens (common report / 3)',ylabel='Effective repairs',title='Actual cost / benefit');axes[0].legend()
    axes[1].bar(range(3),[sum(r['probes_executed'] for r in rows if r['method']==m) for m in METHODS],color=COLORS);axes[1].set_xticks(range(3),[LABEL[m] for m in METHODS]);axes[1].set(title='Actual probe executions',ylabel='Probe count')
    fig.tight_layout();fig.savefig(ROOT/'figures/figure5_cost.png',dpi=150);plt.close(fig)
    # Deterministic case selection: first Active effective repair, first Active failed repair; no aesthetic selection.
    successes=[r for r in rows if r['method']=='active' and r['effective_shared_repair'] is True];failures=[r for r in rows if r['method']=='active' and r['effective_shared_repair'] is False]
    selected=([successes[0]] if successes else [])+([failures[0]] if failures else [])
    if not failures:
        alternatives=[r for r in rows if r['method']=='active' and r['exact_module_hit'] is not True]
        if alternatives and alternatives[0] not in selected:selected.append(alternatives[0])
    write(ROOT/'metrics/case_selection.json',{'rule':'first Active effective repair, then first Active ineffective repair; if no repair failure, first module miss/unresolved (explicitly not called repair failure)','selected':[r['scene_id'] for r in selected],'all_failure_rows':[r['scene_id'] for r in failures]})
    panels=[]
    for row in selected:
        case=row['scene_id'];folder=ROOT/'tasks'/case;dest=folder/'active';panel=Image.new('RGB',(1024,610),'white');draw=ImageDraw.Draw(panel)
        images=[folder/'reference.png',folder/'final.png',next(iter(sorted((dest/'probes').glob('*/probe.png'))),folder/'missing.png'),dest/'transfer_repaired.png']
        labels=['Reference','Damaged reconstruction','Actual selected probe','Independent transfer after patch']
        for i,(path,label) in enumerate(zip(images,labels)):
            if path.exists():panel.paste(Image.open(path).convert('RGB'),(i*256,35))
            elif i==2:
                draw.rectangle((i*256+3,38,(i+1)*256-3,222),outline='#777777');draw.text((i*256+8,105),'No active probe requested',fill='#555555')
            else:draw.text((i*256+8,105),'No output: '+row['status'],fill='#9b3434')
            draw.text((i*256+4,12),label,fill='black')
        if not (dest/'stage1.json').exists():
            draw.text((8,242),case+' '+str(row['failure_stage'])+': '+str(row['failure_reason']),fill='#9b3434');panels.append(panel);continue
        plan=read(dest/'stage1.json')['plan'];decision=read(dest/'stage2.json')['decision'];obs=read(dest/'observations.json')
        lines=[case+': module '+str(row['selected_module'])+' ; truth '+row['exact_module_truth'],
               'Selected probes: '+', '.join(p['probe']+' @ '+p['object_id'] for p in plan['probes']),
               'Observed scalars: '+str([(o['request']['probe'],o['measurement']['outcome'] if o['measurement'] else None) for o in obs]),
               'Hypothesis update: '+str([(h['module'],h['state']) for h in decision['hypothesis_update']]),
               'Actual changed function regions: '+str(row['changed_regions']),
               'Source / transfer: '+str(row['source_pass'])+' / '+str(row['transfer_repair'])]
        import textwrap
        y=242
        for line in lines:
            for part in textwrap.wrap(line,width=142):draw.text((8,y),part,fill='black');y+=17
        selected_region=row['exact_module_truth']
        if selected_region.startswith('SceneCompiler.emit.'):selected_region='SceneCompiler.emit'
        before=regions((folder/'H0.py').read_text());after=regions((dest/'candidate.py').read_text()) if (dest/'candidate.py').exists() else {}
        # Display an evaluator-labelled code region after completion; never supplied as an injected answer.
        draw.text((8,y),'Actual fault-region source (post-run evaluator location; no causal credit to probes):',fill='black');y+=17
        for label,color,code in [('Before','#9b3434',before),('After','#215a39',after)]:
            if selected_region not in code:continue
            draw.text((8,y),label+' '+selected_region,fill=color);y+=17
            for line in code[selected_region].splitlines()[:5]:draw.text((8,y),line[:145],fill=color);y+=17
        panels.append(panel)
    if panels:
        board=Image.new('RGB',(1024,610*len(panels)),'white')
        for i,panel in enumerate(panels):board.paste(panel,(0,i*610))
        board.save(ROOT/'figures/figure4_cases.png')
    probe_visual=[]
    for case in dict.fromkeys(r['scene_id'] for r in rows):
        folder=ROOT/'tasks'/case;baseline=visual(folder/'reference.png',folder/'final.png')
        for method in METHODS:
            for pd in sorted((folder/method/'probes').glob('*')):
                if not pd.is_dir():continue
                measured=visual(folder/'reference.png',pd/'probe.png')
                probe_visual.append({'scene_id':case,'method':method,'probe_dir':str(pd.relative_to(ROOT)),
                    'baseline_psnr':baseline['psnr'],'baseline_ssim':baseline['ssim'],**measured,
                    'ssim_change':measured['ssim']-baseline['ssim'] if measured['ssim'] is not None and baseline['ssim'] is not None else None,
                    'scope':'Post-hoc auxiliary visual sensitivity; not supplied to M and not evidence of unique cause'})
    table(ROOT/'metrics/probe_visual_metrics',probe_visual)
    # Predefined first task provides a transparent fixed-probe counterpart, independent of beauty/winner.
    first=rows[0]['scene_id'];folder=ROOT/'tasks'/first;dest=folder/'fixed'
    board=Image.new('RGB',(1024,405),'white');draw=ImageDraw.Draw(board)
    pictures=[folder/'reference.png',folder/'final.png',dest/'probes/1/probe.png',dest/'probes/2/probe.png']
    titles=['Reference','Faulty H0','Fixed camera replay','Fixed geometry replay']
    for i,(path,title) in enumerate(zip(pictures,titles)):
        if path.exists():board.paste(Image.open(path).convert('RGB'),(i*256,30))
        draw.text((i*256+5,10),title,fill='black')
    if (dest/'stage2.json').exists():
        decision=read(dest/'stage2.json');obs=read(dest/'observations.json')
        lines=[first+' fixed: '+decision['decision']['selected_code_module']+' ; unresolved is NOT a wrong judgment.',
               'Actual outcomes: '+str([(o['request']['probe'],o['measurement']['outcome'] if o['measurement'] else None) for o in obs]),
               'Active counterpart: '+str(read(folder/'active/stage1.json')['plan']['probes']) if (folder/'active/stage1.json').exists() else 'Active trace pending',
               'This panel uses the first registered task. No active experiment is fabricated; no repair failure is invented.']
        for i,line in enumerate(lines):draw.text((5,235+i*25),line[:145],fill='black')
    board.save(ROOT/'figures/fixed_probe_counterpart.png')
    # Known correct/broken fixtures show actual support and edit-error detections.
    known=[('correct_support_relation','Correct support'),('defect_7','Injected support defect'),('correct_material_dependency','Independent local edit'),('defect_8','Injected shared-mesh edit defect')]
    board=Image.new('RGB',(1024,360),'white');draw=ImageDraw.Draw(board)
    for index,(name,title) in enumerate(known):
        folder=ROOT/'calibration/probes'/name
        if (folder/'probe.png').exists():board.paste(Image.open(folder/'probe.png').convert('RGB'),(index*256,30))
        draw.text((index*256+5,10),title,fill='black')
        if (folder/'measurement.json').exists():
            value=read(folder/'measurement.json');draw.text((index*256+5,232),'Measured discrepancy: '+str(value['outcome']),fill='black')
    for row,name in enumerate(['correct_dependency_move','defect_6']):
        path=ROOT/'calibration/probes'/name/'measurement.json'
        if path.exists():
            value=read(path);draw.text((6,272+row*25),name+': parent contract errors = '+str(value['details']['parent_contract_errors'])[:125],fill='black')
    board.save(ROOT/'figures/known_structure_edit_errors.png')
    # Figure 1 uses a real recorded case trace; boxes summarize execution, not synthetic scene imagery.
    fig,ax=plt.subplots(figsize=(13,3));ax.axis('off')
    texts=['Real images + H0','Competing hypotheses\npre-probe intervals','M chooses tools\nactual Blender execution','M compares observations\nshared H coding patch','Independent scene\nfixed external gates']
    for i,text in enumerate(texts):
        ax.text(.1+.2*i,.55,text,ha='center',va='center',bbox={'boxstyle':'round','facecolor':'#e4f0f0'},transform=ax.transAxes,fontsize=10)
        if i<4:ax.annotate('',xy=(.2+.2*i,.55),xytext=(.18+.2*i,.55),xycoords='axes fraction',arrowprops={'arrowstyle':'->'})
    ax.text(.5,.1,'Execution outline; actual per-case evidence is in Figure 4 and tasks/*/{stage1,observations,stage2,changes.diff}',ha='center',transform=ax.transAxes,fontsize=9)
    fig.tight_layout();fig.savefig(ROOT/'figures/figure1_executed_pipeline.png',dpi=150);plt.close(fig)
    write(ROOT/'metrics/figure_sources.json',{'figure1_executed_pipeline.png':{'sources':['tasks/*/*/stage1.json','tasks/*/*/observations.json','tasks/*/*/stage2.json'],'kind':'execution outline, separate from actual photographic evidence'},'figure2_diagnosis.png':{'sources':['metrics/scene_metrics.csv','metrics/summary.json'],'unit':'10 injected fault configurations across two templates; raw points overlaid'},'figure3_repair.png':{'sources':['metrics/scene_metrics.csv','metrics/summary.json'],'unit':'one proposal per task/method'},'figure4_cases.png':{'sources':['metrics/case_selection.json','tasks/*/*/changes.diff','tasks/*/*/stage1.json','tasks/*/*/stage2.json'],'selection':'first success and first failure/unresolved by predefined order'},'fixed_probe_counterpart.png':{'sources':['tasks/task01/fixed/observations.json','tasks/task01/fixed/stage2.json'],'selection':'first registered task, not selected for appearance'},'figure5_cost.png':{'sources':['metrics/cost_curve.csv','metrics/calls.csv'],'unit':'cumulative observable tokens and actual probe count; no dollar cost inferred'},'known_structure_edit_errors.png':{'sources':['calibration/probe_calibration.json','calibration/probes/*/measurement.json'],'unit':'deterministic calibration, excluded from formal rate'},'all_cases_contact.png':{'sources':['metrics/scene_metrics.csv','tasks/*/reference.png','tasks/*/*/source_repaired.png'],'selection':'every formal case in frozen order'},'script':'analyze.py'})
    total=ledger;text=['# Scene-RSI V2.3 中文实验报告','', '本轮是工程实现的三组领域诊断机制实验，不是新一轮多代 RSI。M 没有自动进化。共享 H 为真实 SceneAct Blender 编译器加少量支撑/编辑接口；不是自然图像重建流程的整体收益实验。','', '## 实际结果','', '|方法|完成/预定|精确模块|有效修复|迁移修复|新增回归|探测数|','|---|---|---|---|---|---|---|']
    for m in METHODS:
        s=summary[m];fmt=lambda key:'/'.join(map(str,s[key]));text.append(f"|{LABEL[m]}|{s['completed']}/{s['scheduled']}|{fmt('exact_module')}|{fmt('effective_repair')}|{fmt('transfer_repair')}|{fmt('regression')}|{sum(r['probes_executed'] for r in rows if r['method']==m)}|")
    text+=['',f"新增 CLI 会话 {total['cli_sessions']}/180；已知输入 token {total['known_input_tokens']}，输出 {total['known_output_tokens']}，usage 缺失 {total['usage_unknown_sessions']}；渲染尝试 {total['render_attempts_upper_bound']}/600，完成 {total['renders_completed']}。CPU 单重任务、2 线程，GPU 0。",'', '## 已观察到的结论','', '三组有效共享修复和迁移均10/10，固定检查新增回归0/10。共同初诊在全部任务已精确命中模块10/10，三组对象Top-1均7/9。Active正式探测0次，Structured0次，Fixed20次（19次有数值读数）；Active/Fixed实际两次探测匹配子集为0。本轮没有获得主动探测带来共享研发优势的证据，也不足以支持论文贡献一。', '', '重要适配：本轮给三组共享了一个强模型初诊，实际是在相同初诊之上比较探测/更新，而非三个完整端到端诊断程序；这种共享消除了初始定位差异并使修复接近天花板。当前试验未产生可区分竞争解释的正式Active实验，不能把不探测的成功修复归因于主动机制。', '', 'H轨迹：每个故障起点有三组各一次真实H-only编码提案，共30；全部在source和另一模板transfer执行。M轨迹：工程M保持不变，没有自动M后代或M-only候选。全部正式模型和候选执行失败0；准备期2个工程失败分列并保留日志。', '', '源码改动字段 changed_module_count 在原runner中实际统计函数文本不同区域，格式重排会放大数量。原字段未回写；补充 metrics/code_scope.csv 记录语法结构变化，二者都不能直接证明过度修复。过度修复的功能退化以固定回归检查为准。', '', '## 解释边界','', '- 10 个注入故障来自两个参数化家具模板，迁移换到另一模板及资产组合、尺寸、相机、旋转和材质所有权。不是 10 个独立自然场景，更不是全重建 RSI 的一般优势。', '- 公共SceneAct计划包含目标三维参数，源码也完整可见，输入强于仅参考图像的重建任务；当前契约错误往往可静态发现。本轮不证明在视觉歧义故障上的下游研发优势。',
        '- 多个解释都符合观测时，冻结更新器将Fixed的最终模块置为unresolved；无观测的Structured/Active则可保留置信>=0.7的初诊。因此最终模块标签差异还受该更新规则影响，不能把Fixed覆盖率下降直接解释为Active定位能力更强。另存三组共同初始模块命中。',
        '- 三组共享每任务一次初始图像/源码诊断，实际只调用一次并按三分之一分摊展示成本；对象 Top-1 因而本来就相同，不作为 Active 定位优势。后续 M 的探测与更新不同；每组仅一次同模型编码。', '- Fixed/Active 上限均为两个探测；报告实际执行数。若 Active 因无预测分歧而少用探测，不能称严格实际次数匹配。Structured 不探测，其较低成本单列。', '- 所有竞争解释区间命中率只是描述性值，排除错误解释反而可能降低该值；另列隐藏真模块假设的预测一致率与真假设缺席情况。错误高置信按初始confidence>=0.7且初始模块错误定义，不把无概率的最终已定判断冒充校准后的自信。',
        '- 区分率依据事前不相交区间与真实标量是否排除某些竞争解释；不把单纯画面改善当唯一因果证据。错误/过窄预测也可能制造虚假排除，保留所有原始预测。', '- 有效修复要求 source 与独立 transfer 的固定必要检查全通过；transfer rate 只看 transfer。新增回归以原本通过的相同检查转为失败定义。源场景失败导致未测的指标保持 null，端到端失败效用另记零。', '- 辅助视觉值对应source场景，不是transfer的图像重建准确率。像素完全相同的PSNR为数学上的正无穷，保存为null并同时标记psnr_perfect_match=true；这与没有执行而缺测的null不同。',
        '- 最终结构/编辑是执行当前 H 的机械操作与可控程序真值比较；没有文字编辑器模型、真实自然图像三维真值或完整 Mesh 支撑碰撞真值。', '- 可修源码包含多数正确实现，编码器可能独立于诊断找到错误。若修复率相同，只能报告成本、回归和诊断差异，不能宣称下游研发优势。', '- 本轮不产生自动 M 后代，也未进行陌生 H 起点冻结元回放，不支持元能力递归提升。', '', '## 证据与重画','', '全部原始点：../metrics/scene_metrics.csv；事前预测与观测：../metrics/probe_predictions.csv；实际调用：../metrics/calls.csv。脚本为 ../analyze.py，读取现有数据离线重算，不调用模型和 Blender。案例按注册任务顺序选首个成功与首个失败；无修复失败时明确展示诊断失败。', '', '每张图的统计单位是故障任务/方法，独立计数不是渲染视角。构造/烟测期间的工程失败日志完整保留，不回写 V2.2。']
    (ROOT/'reports/REPORT_ZH.md').write_text('\n'.join(text)+'\n')
    (ROOT/'reports/index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>Scene-RSI V2.3</title><style>body{max-width:1200px;margin:30px auto;font:16px sans-serif}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>Scene-RSI V2.3 真实机制实验</h1><p><a href="REPORT_ZH.md">中文报告</a> · <a href="../metrics/scene_metrics.csv">逐任务原始数据</a> · <a href="../metrics/probe_predictions.csv">事前预测与观测</a> · <a href="../metrics/calls.csv">实际成本</a></p>'+''.join('<h2>'+name+'</h2><img src="../figures/'+name+'">' for name in ['figure1_executed_pipeline.png','figure2_diagnosis.png','figure3_repair.png','figure4_cases.png','figure5_cost.png','known_structure_edit_errors.png','fixed_probe_counterpart.png','all_cases_contact.png'] if (ROOT/'figures'/name).exists())+'<pre>'+html.escape('\n'.join(text))+'</pre></html>')
    print(json.dumps({'summary':summary,'ledger':total},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
