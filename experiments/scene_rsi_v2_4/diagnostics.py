"""Development-only visual localization and explicit failure evidence."""
from pathlib import Path
import json
from PIL import Image, ImageDraw


def classify_failure(valid, functional, status, calls, executions, events):
    failed=[c for c in calls if c['status']=='failed']
    trace=str(status['error'])
    last_stage=events[-1]['stage'] if events else None
    outer_exhausted='outer_scene_deadline' in trace or 'BudgetExceeded' in trace
    if valid:
        category=('structure_check_failure' if not functional['checks']['structure']['gate_pass'] else
                  'edit_or_regression_failure' if not functional['functional_pass'] else 'successful_visual_reconstruction')
    elif failed:
        category='codex_timeout' if any('TimeoutExpired' in str(c.get('error')) for c in failed) else 'codex_service_failure'
    elif 'outer_scene_deadline' in trace:
        category='outer_total_budget_exhausted'
    elif executions:
        final=executions[-1];error=str(final['error'])
        names=[e['stage'] for e in events]
        timeout='TimeoutExpired' in error
        if timeout:
            if 'render_started' in names and 'render_completed' not in names:category='render_timeout'
            elif last_stage=='boolean_started':category='blender_geometry_timeout'
            elif 'scene_build_started' in names and 'scene_build_completed' not in names:category='blender_scene_build_timeout_unresolved'
            else:category='outer_total_budget_exhausted' if outer_exhausted else 'execution_timeout_stage_unknown'
        elif 'scene_build_started' not in names and 'python_validation_started' in names:category='python_program_construction_error'
        elif 'render_started' in names:category='blender_render_error'
        elif 'scene_build_started' in names:category='blender_scene_build_error'
        else:category='execution_failure_stage_unknown'
    elif outer_exhausted:category='outer_total_budget_exhausted'
    elif any(word in trace for word in ['SyntaxError','JSONDecodeError','Invalid','parse']):category='python_program_construction_error'
    else:category='program_generation_failure_undetermined'
    return {'category':category,'last_observed_stage':last_stage,
            'outer_budget_exhausted':outer_exhausted,
            'attribution':'Stage/log evidence only. Scene build timeout without finer events is not proven Boolean/mesh overload.'}


def failure_evidence(row):
    folder=Path(row['alias_of'] if 'alias_of' in row else row['folder'])
    calls=[json.loads(p.read_text()) for p in sorted(folder.glob('student_calls/*/session.json'))]
    execution_paths=sorted(folder.glob('steps/*/result.json'))
    executions=[json.loads(p.read_text()) for p in execution_paths]
    event_paths=sorted(folder.glob('steps/*/stage_events.jsonl'))
    latest_events=[json.loads(line) for line in event_paths[-1].read_text().splitlines()] if event_paths else []
    measured=classify_failure(row['metrics']['valid'],row['functional'],row['runtime_status'],calls,executions,latest_events)
    failed=[c for c in calls if c['status']=='failed']
    logs=[{'path':str(p),'text':p.read_text(errors='replace')[-12000:]} for p in sorted(folder.glob('steps/*/stderr*'))]
    return {**measured,'runtime_status':row['runtime_status'],
            'failed_calls':[{k:c.get(k) for k in ['status','error','exit_code','seconds','call_dir']} for c in failed],
            'execution_errors':logs,
            'execution_failures':[{'error':e['error'],'stdout':e['stdout'][-12000:],'stderr':e['stderr'][-12000:]} for e in executions if not e['ok']],
            'stage_event_paths':list(map(str,event_paths)), 'related_modules':['policy.py','system.txt'],
            'valid_blend':row['metrics']['valid'],'visual_quality':row['metrics']['overall'],
            'quality_interpretation':'Continuous measured Q is not geometry truth; infrastructure errors do not identify a visual module'}


def object_map(render, objects, output):
    image=Image.open(render).convert('RGB');draw=ImageDraw.Draw(image)
    # Name order is only display order. No size-based diagnosis or default target.
    entries=[]
    for obj in objects:
        box=obj['projected_bbox_normalized_approx']
        if box is None:continue
        if obj['type']=='EMPTY' or (obj['type']=='MESH' and obj['parent'] is None):
            entries.append(obj)
    for i,obj in enumerate(entries[:48]):
        b=obj['projected_bbox_normalized_approx'];x0,y0,x1,y1=[max(0,min(1,v)) for v in b]
        if x1<=x0 or y1<=y0:continue
        xy=(x0*image.width,y0*image.height,x1*image.width,y1*image.height)
        draw.rectangle(xy,outline=(255,50,30),width=1)
        draw.text((xy[0],xy[1]),str(i)+':'+obj['name'][:35],fill=(255,20,20),stroke_width=1,stroke_fill='white')
    image.save(output)
    return [{'object_id':o['name'],'parent':o['parent'],'type':o['type'],'bbox':o['projected_bbox_normalized_approx']} for o in objects if o['projected_bbox_normalized_approx'] is not None]


def localize(development, dest):
    from pilot import config,call,write_json,read
    if (dest/'findings.json').exists():return read(dest/'findings.json')
    dest.mkdir(parents=True,exist_ok=True)
    results=[]
    for index,scene in enumerate(development):
        if scene['status']!='complete':continue
        case=dest/str(index);case.mkdir(exist_ok=True)
        images=scene['attached_images']
        objects=scene['objects']
        projection=object_map(images[1],objects,case/'object_map.png')
        prompt='Identify a concrete visible discrepancy between reference image 1 and reconstruction image 2. Image 3 is the SAME reconstruction with approximate projected object/group bounds (not segmentation). Use only actual object IDs below. Largest mesh, floor, or first name is NOT evidence of fault. State uncertainty; use object_id="unknown" when mapping is ambiguous, and camera_focal may use object_id=null. Choose at most two discriminating sensitivity probes: camera_focal multiplies the existing lens by 1.1 at fixed geometry/pose; object_scale multiplies the named object/group by 1.1 about its GEOMETRY AABB CENTER (not its origin), fixed camera; isolate hides OTHER meshes but does not unhide the target. No other probe parameters are available. Do not infer unique causality from an image. Return JSON findings. For each discrepancy give two plausible alternatives when possible, each with module, explanation, predicted_probe_phenomenon and predicted_direction (improve/worsen/unchanged/unknown for the chosen probe at the supplied magnitude, predicted BEFORE observing it). State why the chosen probe distinguishes them, or why it cannot; never promise unique attribution. Each finding: scene_id, object_id, observation, hypothesis, probe, code_module, confidence, alternatives, probe_reason, mapping_evidence, uncertainty. code_module is camera,object_parameters,object_coverage,support_relations,part_dependencies,material_edit,or unknown. No fixture labels or hidden truth are supplied.\n'+json.dumps({'scene_id':scene['scene_id'],'objects':projection,'measured_structure':scene['structure'],'metrics':scene['metrics'],'public_program':scene['public_program']},ensure_ascii=False)
        schema={'type':'object','additionalProperties':False,'properties':{'findings':{'type':'array','maxItems':2,'items':{'type':'object','additionalProperties':False,'properties':{'scene_id':{'type':'string'},'object_id':{'type':['string','null']},'observation':{'type':'string'},'hypothesis':{'type':'string'},'probe':{'type':'string','enum':['camera_focal','object_scale','isolate']},'code_module':{'type':'string'},'confidence':{'type':'string','enum':['low','medium','high']},'alternatives':{'type':'array','minItems':2,'maxItems':3,'items':{'type':'object','additionalProperties':False,'properties':{'module':{'type':'string'},'explanation':{'type':'string'},'predicted_probe_phenomenon':{'type':'string'},'predicted_direction':{'type':'string','enum':['improve','worsen','unchanged','unknown']}},'required':['module','explanation','predicted_probe_phenomenon','predicted_direction']}},'probe_reason':{'type':'string'},'mapping_evidence':{'type':'string'},'uncertainty':{'type':'string'}},'required':['scene_id','object_id','observation','hypothesis','probe','code_module','confidence','alternatives','probe_reason','mapping_evidence','uncertainty']}}},'required':['findings']}
        saved=case/'visual_call/session.json'
        if saved.exists():
            session=read(saved)
            if session['status']!='complete':raise RuntimeError('Saved failed/interrupted common visual call is retained; no automatic resampling')
            text=(case/'visual_call/response.txt').read_text()
        else:text,session=call(prompt,config()['proposer'],case/'visual_call',[*images,str(case/'object_map.png')],role='development_localizer',schema=schema)
        findings=json.loads(text)['findings']
        ids={o['name'] for o in objects}
        for finding in findings:
            if finding['scene_id']!=scene['scene_id']:raise ValueError('Localizer returned another scene')
            if finding['object_id'] not in ids and finding['object_id'] not in [None,'unknown']:raise ValueError('Localizer invented object ID')
        results.extend(findings)
    write_json(dest/'findings.json',results)
    return results
