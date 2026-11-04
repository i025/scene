"""Finish measured local artifacts after CLI quota exhaustion; no model calls."""
from pathlib import Path
import collections
import csv
import difflib
import json
import subprocess
import sys
import time

from PIL import Image,ImageDraw,ImageOps
from pilot import ROOT,read,write_json,inspect,current,cpu_environment

METHODS=['fixed_h0','sceneevolve_cli','generic_rsi','scene_rsi_pilot']

def table(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def sheet(path,rows,columns):
    width,height=260,232
    canvas=Image.new('RGB',(width*columns,height*len(rows)),(238,242,246));draw=ImageDraw.Draw(canvas)
    for y,cells in enumerate(rows):
        for x,(label,source) in enumerate(cells):
            draw.multiline_text((x*width+7,y*height+6),label,fill=(30,45,60),spacing=3)
            if source and source.exists():
                with Image.open(source) as im:
                    tile=ImageOps.contain(im.convert('RGB'),(width-12,172))
                    canvas.paste(tile,(x*width+6,y*height+57))
            else:draw.text((x*width+10,y*height+120),'NO VALID OUTPUT / FAILED',fill=(150,55,55))
    canvas.save(path)

def main():
    dest=ROOT/'usage_limit_closeout';dest.mkdir(exist_ok=True)
    out=ROOT/'reports';out.mkdir(exist_ok=True)
    before=current();limits=[]
    for p in ROOT.rglob('session.json'):
        s=read(p);events=p.with_name('events.jsonl')
        if events.exists() and 'hit your usage limit' in events.read_text():
            messages=[json.loads(line) for line in events.read_text().splitlines()]
            limits.append({'source':str(p.relative_to(ROOT)),'started':s['started'],'status':s['status'],'usage':s.get('total_tokens'),'message':next(e['message'] for e in messages if e['type']=='error' and 'hit your usage limit' in e.get('message',''))})
    assert limits,'Quota closeout needs an actual logged usage-limit error'
    limits.sort(key=lambda r:r['started']);write_json(dest/'usage_limit_calls.json',limits)
    write_json(ROOT/'model_usage_limit.json',{'reason':'Codex CLI usage limit','first_logged_error':limits[0],'failed_cli_calls':len(limits),'automatic_retries':0,'prior_service_retry_already_used':True,'note':'The CLI reset message has no explicit timezone; retain its exact text. No third model or API used.'})
    for name in ['extras_status.json','external_status.json']:
        p=ROOT/name;old=read(p,{})
        backup=dest/(name.replace('.json','_before.json'))
        if not backup.exists():write_json(backup,old)
        write_json(p,{**old,'previous_runner_status':old.get('previous_runner_status',old.get('status')),'status':'blocked_model_usage_limit','valid_comparison_completed':False,'reason':'Logged Codex CLI quota errors; attempted slots and null metrics remain preserved'})
    for p in (ROOT/'results').glob('*/*/*/*/*/record.json'):
        row=read(p);folder=Path(row.get('reuse_of',p.parent));events=list(folder.glob('student_calls/*/events.jsonl'))
        if any('hit your usage limit' in e.read_text() for e in events):
            row['observed_model_service_failure']='cli_usage_limit'
            if row['status']=='failed':
                row.setdefault('failure_type_before_classification',row.get('failure_type'));row['failure_type']='cli_usage_limit'
            write_json(p,row)
    scenes=[s for s in read(ROOT/'manifest.json') if s['split']=='development'];choices=read(ROOT/'selections.json')
    selected=[];raw=[];records=[];raw_records=[]
    for scene in scenes:
        for run in ['r1','r2']:
            sid=scene['scene_id'];base=ROOT/'results'/run/'fixed_h0/H0/development'/sid
            selected_cells=[(f'{sid}\n{run} / Development only',base/'reference.png')];raw_cells=list(selected_cells)
            for method in METHODS:
                choice=next(c for c in choices if c['run_id']==run and c['method']==method)
                cid=choice['candidate_id'];source_method='fixed_h0' if cid=='H0' else method
                folder=ROOT/'results'/run/source_method/cid/'development'/sid;r=read(folder/'record.json',{})
                selected_cells.append((f"{method} / {cid}\nQ={r.get('metrics',{}).get('overall')}\n{r.get('status','not_run')}",folder/'final.png'))
                raw_cid='H0' if method=='fixed_h0' else 'C1';raw_folder=ROOT/'results'/run/method/raw_cid/'development'/sid;rr=read(raw_folder/'record.json',{})
                raw_cells.append((f"{method} / {raw_cid}\nQ={rr.get('metrics',{}).get('overall')}\n{rr.get('status','not_run_proposal_failed')}",raw_folder/'final.png'))
                raw_records.append({'method':method,'run_id':run,'scene_id':sid,'split':'development','candidate_id':raw_cid,'Q':rr.get('metrics',{}).get('overall'),'status':rr.get('status','not_run_proposal_failed'),'image':str(raw_folder.relative_to(ROOT)/'final.png') if (raw_folder/'final.png').exists() else None,'record':str(raw_folder.relative_to(ROOT)/'record.json') if rr else None})
                records.append({'method':method,'run_id':run,'scene_id':sid,'split':'development','candidate_id':cid,'Q':r.get('metrics',{}).get('overall'),'status':r.get('status','not_run'),'functional_pass':r.get('functional',{}).get('functional_pass'),'reuses_identical_H0':method!='fixed_h0' and cid=='H0','record':str(folder.relative_to(ROOT)/'record.json')})
            selected.append(selected_cells);raw.append(raw_cells)
    sheet(out/'selected_development.png',selected,5);sheet(out/'raw_c1_development.png',raw,5);table(out/'selected_development.csv',records);table(out/'raw_c1_development.csv',raw_records)
    views=[];edits=[];measurements=[];view_sources=[];view_folders=set()
    sid=scenes[0]['scene_id']
    for method in METHODS:
        choice=next(c for c in choices if c['run_id']=='r1' and c['method']==method);cid=choice['candidate_id']
        folder=ROOT/'results/r1'/('fixed_h0' if cid=='H0' else method)/cid/'development'/sid
        row=read(folder/'record.json');assert row['status']=='complete'
        inspect(folder,'views')
        view_folders.add(folder/'views')
        view_sources.append({'method':method,'run_id':'r1','scene_id':sid,'candidate_id':cid,'reference':str(folder.relative_to(ROOT)/'reference.png'),'input_view':str(folder.relative_to(ROOT)/'final.png'),'side_view':str(folder.relative_to(ROOT)/'views/view_side60.png'),'top_view':str(folder.relative_to(ROOT)/'views/view_top.png'),'view_device':read(folder/'views/actual_device.json',{}).get('device'),'source':str(folder.relative_to(ROOT)/'views/views.json'),'identical_H0_reuse':method!='fixed_h0' and cid=='H0'})
        views.append([(f'{method} / {cid}\nReference / Development',folder/'reference.png'),('Input camera',folder/'final.png'),('Fixed side +60 deg',folder/'views/view_side60.png'),('Fixed top view',folder/'views/view_top.png')])
        check=read(folder/'functional/mechanical.json')
        edits.append([(f'{method} / {cid}\nTarget: {check["target_selection"]["object"]}\nMechanical operation only',folder/'functional/before.png'),('Predefined blue material',folder/'functional/after_material.png'),('Predefined assembly move',folder/'functional/after_move.png')])
        measurements.append({'method':method,'run_id':'r1','scene_id':sid,'candidate_id':cid,'target_object':check['target_selection']['object'],'test_type':'predefined_mechanical_operations','material_target_success':check['material']['target_success'],'material_non_target_preserved':check['material']['non_target_preservation']['pass'],'move_target_success':check['move']['target_success'],'relative_part_matrix_max_difference':check['move']['relation_max_abs_matrix_delta'],'move_non_target_preserved':check['move']['non_target_preservation']['pass'],'source':str(folder.relative_to(ROOT)/'functional/mechanical.json')})
    sheet(out/'development_multiview.png',views,4);sheet(out/'development_mechanical_edits.png',edits,3);table(out/'development_mechanical_edits.csv',measurements);table(out/'development_multiview.csv',view_sources)
    write_json(dest/'display_rule.json',{'set_after_quota_failure':True,'selected_and_raw_C1_contacts':'All two Development scenes, both repeats, manifest scene order; blanks retained. Final Selection choices shown on Development only. No new evaluation or candidate selection.','multiview':'First manifest Development scene, r1, all methods selected by Selection; same fixed side60/top rule, identical H0 views reused','edit_board':'Existing prescribed mechanical material/move records; no text-editor inference','render_quality':'Frozen Cycles16/512/seed42/color settings; cpu_if_busy, authorized GPU0 only','views_are_not_independent_samples':True})
    remaining=['valid_main_held_out_comparison','text_instruction_edit_test','independent_visual_reviews','mechanism_ablations_with_valid_H','frozen_Ours_meta_replay_no_usable_descendant','BlenderWorld_valid_external_comparison']
    write_json(ROOT/'supplement_status.json',{'status':'blocked_model_usage_limit','text_editor_model_calls':0,'independent_judge_model_calls':0,'checker_engineering_controls':read(ROOT/'smoke/text_editor_checker/status.json'),'reason':'All selected Test reconstructions lack valid artifacts; no text or judge results invented'})
    rows=[read(p) for p in (ROOT/'results').glob('*/*/*/*/*/record.json')]
    runtime_success=sum(r['status']=='complete' and not r.get('reuse_of') and not r.get('runtime_status',{}).get('error') for r in rows)
    prior_closeout=read(dest/'closeout.json',{})
    write_json(dest/'closeout.json',{'status':'completed_local_artifacts_with_model_quota_block','formal_record_statuses':dict(collections.Counter(r['status'] for r in rows)),'physical_valid_reconstructions':sum(r['status']=='complete' and not r.get('reuse_of') for r in rows),'physical_runtime_completed_without_error':runtime_success,'reused_outcome_records':sum(bool(r.get('reuse_of')) for r in rows),'new_model_calls':current()['cli_sessions']-before['cli_sessions'],'additional_render_attempts':prior_closeout.get('additional_render_attempts',0)+current()['render_attempts_upper_bound']-before['render_attempts_upper_bound'],'render_attempts_this_resume':current()['render_attempts_upper_bound']-before['render_attempts_upper_bound'],'closeout_view_frames':sum(read(f/'render_ledger.json',{}).get('renders_completed',0) for f in view_folders),'pending':remaining,'no_scene_rsi_process_left_running':True})
    write_json(ROOT/'state.json',{'phase':'blocked_model_usage_limit','pending':remaining,'time':time.time(),'resume':'bash '+str(ROOT/'run.sh')+' resume','valid_main_test_comparison_available':False})
    write_json(ROOT/'ledger.json',current())
    subprocess.run([sys.executable,str(ROOT/'analyze.py')],check=True,env=cpu_environment())
    subprocess.run([sys.executable,str(ROOT/'report.py'),'--root',str(ROOT)],check=True,env=cpu_environment())
    for name in ['codex_wrapper','run.sh','report','analyze']:
        suffix='' if name=='run.sh' else '.py';old=dest/'before'/(name+suffix);new=ROOT/('backend/codex_wrapper.py' if name=='codex_wrapper' else name+suffix)
        (dest/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='before/'+old.name,tofile='after/'+new.name)))
    print(json.dumps(read(dest/'closeout.json'),ensure_ascii=False))

if __name__=='__main__':main()
