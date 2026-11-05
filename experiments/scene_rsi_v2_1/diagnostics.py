"""Development-only visual localization and explicit failure evidence."""
from pathlib import Path
import json
from PIL import Image, ImageDraw


def failure_evidence(row):
    folder=Path(row['alias_of'] if 'alias_of' in row else row['folder'])
    calls=[json.loads(p.read_text()) for p in sorted(folder.glob('student_calls/*/session.json'))]
    failed=[c for c in calls if c['status']=='failed']
    status=row['runtime_status'];trace=str(status)
    logs=[]
    for p in sorted(folder.glob('steps/*/stderr*')):
        logs.append({'path':str(p),'text':p.read_text(errors='replace')[-12000:]})
    executions=[json.loads(p.read_text()) for p in sorted(folder.glob('steps/*/result.json'))]
    execution_failures=[e for e in executions if not e['ok']]
    if not row['metrics']['valid'] and failed:
        category='codex_timeout' if any('TimeoutExpired' in str(c) for c in failed) else 'codex_call_failure'
    elif not row['metrics']['valid']:
        category='blender_execution_failure' if list(folder.glob('steps/*/build.py')) else 'program_generation_failure'
    elif not row['functional']['checks']['structure']['gate_pass']:
        category='structure_check_failure'
    elif not row['functional']['functional_pass']:
        category='edit_or_regression_failure'
    else:category='successful_visual_reconstruction'
    return {'category':category,'runtime_status':status,'failed_calls':[{k:c.get(k) for k in ['status','error','exit_code','seconds','call_dir']} for c in failed],
            'execution_errors':logs,'execution_failures':[{'error':e['error'],'stdout':e['stdout'][-12000:],'stderr':e['stderr'][-12000:]} for e in execution_failures],'related_modules':['policy.py','system.txt'],
            'valid_blend':row['metrics']['valid'],'visual_quality':row['metrics']['overall'],
            'quality_interpretation':'Measured continuous Q; low quality localized by image evidence, not an arbitrary success threshold'}


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
        prompt='Identify a concrete visible discrepancy between reference image 1 and reconstruction image 2. Image 3 is the SAME reconstruction with approximate projected object/group bounds (not segmentation). Use only actual object IDs below. Largest mesh, floor, or first name is NOT evidence of fault. State uncertainty; use object_id="unknown" when mapping is ambiguous, and camera_focal may use object_id=null. Choose at most two discriminating sensitivity probes: camera_focal multiplies the existing lens by 1.1 at fixed geometry/pose; object_scale multiplies the named object/group by 1.1 about its GEOMETRY AABB CENTER (not its origin), fixed camera; isolate hides OTHER meshes but does not unhide the target. No other probe parameters are available. Do not infer unique causality from an image. Return JSON findings. Each finding: scene_id, object_id, observation, hypothesis, probe, code_module, confidence. code_module is camera,object_parameters,object_coverage,support_relations,material_edit,or unknown. No fixture labels or hidden truth are supplied.\n'+json.dumps({'scene_id':scene['scene_id'],'objects':projection,'measured_structure':scene['structure'],'metrics':scene['metrics']},ensure_ascii=False)
        schema={'type':'object','additionalProperties':False,'properties':{'findings':{'type':'array','maxItems':2,'items':{'type':'object','additionalProperties':False,'properties':{'scene_id':{'type':'string'},'object_id':{'type':['string','null']},'observation':{'type':'string'},'hypothesis':{'type':'string'},'probe':{'type':'string','enum':['camera_focal','object_scale','isolate']},'code_module':{'type':'string'},'confidence':{'type':'string','enum':['low','medium','high']}},'required':['scene_id','object_id','observation','hypothesis','probe','code_module','confidence']}}},'required':['findings']}
        text,session=call(prompt,config()['proposer'],case/'visual_call',[*images,str(case/'object_map.png')],role='development_localizer',schema=schema)
        findings=json.loads(text)['findings']
        ids={o['name'] for o in objects}
        for finding in findings:
            if finding['scene_id']!=scene['scene_id']:raise ValueError('Localizer returned another scene')
            if finding['object_id'] not in ids and finding['object_id'] not in [None,'unknown']:raise ValueError('Localizer invented object ID')
        results.extend(findings)
    write_json(dest/'findings.json',results)
    return results
