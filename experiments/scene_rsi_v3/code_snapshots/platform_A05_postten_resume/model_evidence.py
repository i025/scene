"""Bounded common model evidence; full measurements and transcripts remain on disk."""
import json
import re


def projected_objects(objects):
    """Bound numeric detail; retain all real IDs separately in the context."""
    def priority(obj):
        numeric=re.fullmatch(r'[0-9.]+',obj['name']) is not None
        if obj['type']=='EMPTY' and not numeric:return 0
        if obj['type'] in ['CAMERA','LIGHT']:return 1
        if not numeric and not re.fullmatch(r'(Box|Cylinder|Sphere)(\.\d+)?',obj['name']):return 2
        return 3
    selected=sorted(objects,key=lambda obj:(priority(obj),obj['name']))[:128]
    keys=['name','type','parent','parent_chain','finite_nonempty_mesh','excluded_as_structural','world_geometry_aabb_approx','projected_bbox_normalized_approx','hide_render']
    return [{key:obj[key] for key in keys} for obj in selected]


def compact_structure(source):
    if not source:
        return source
    result={key:value for key,value in source.items() if key not in ('objects','input_blend','render_settings')}
    objects=source.get('objects',[])
    target=source.get('target',{})
    wanted={target.get('object'),*target.get('mesh_names',[])[:16]}
    by_name={obj['name']:obj for obj in objects}
    for name in list(wanted):
        wanted.update(by_name.get(name,{}).get('parent_chain',[]))
    def priority(obj):
        if obj['name'] in wanted:return 0
        if obj.get('finite_nonempty_mesh') is False:return 1
        if obj['type']=='EMPTY' and not re.fullmatch(r'[0-9.]+',obj['name']):return 2
        if obj['type'] in ('CAMERA','LIGHT'):return 3
        return 4
    chosen=sorted(objects,key=lambda obj:(priority(obj),obj['name']))[:64]
    concise=[]
    for obj in chosen:
        item={key:obj.get(key) for key in ('name','type','parent','vertex_count','finite_nonempty_mesh','excluded_as_structural','hide_render')}
        box=obj.get('world_geometry_aabb_approx')
        item['aabb_approx']={key:[round(v,5) for v in box[key]] for key in ('min','max')} if box else None
        item['material_names']=[m['name'] for m in obj.get('materials',[]) if m]
        concise.append(item)
    result['objects']=concise
    relations=result.get('approximate_relations',{})
    for key in ('approximate_support_candidates','approximate_overlap_candidates'):
        values=relations.get(key,[])
        relations[key+'_total_count']=len(values)
        relations[key]=values[:32]
        relations[key+'_projection']='first32 in fixed collector order; full list retained; no true mesh contact/collision inference'
    result['evidence_projection']={'full_object_count':len(objects),'shown_count':len(concise),'omitted_count':len(objects)-len(concise),'rule':'max64, target/first16 target meshes and ancestors, invalid meshes, named EMPTY groups, camera/lights, others; name tie order','raw_snapshot_retained':True,'omitted':'Repeated shader-node trees, duplicate matrices and remaining detailed object rows; this summary does not certify omitted objects.'}
    return result


def compact_trajectory(text):
    raw=[json.loads(line) for line in text.splitlines()]
    replacements=[]
    for event in raw:
        if event['event']!='execution_result':continue
        for stream in ('stdout','stderr'):
            original=event.get(stream,'');kept=[];seen=set()
            for output in original.splitlines():
                if output.startswith('Fra:') or (' | Sample ' in output):continue
                if output not in seen:kept.append(output);seen.add(output)
            filtered='\n'.join(kept)
            if len(original)>1000:
                replacements.extend([(original,filtered),(json.dumps(original)[1:-1],json.dumps(filtered)[1:-1])])
    def project(value):
        if isinstance(value,str):
            for original,filtered in replacements:value=value.replace(original,filtered)
            return value
        if isinstance(value,list):return [project(v) for v in value]
        if isinstance(value,dict):return {k:project(v) for k,v in value.items()}
        return value
    events=[]
    prior_messages=[]
    for event in raw:
        kind=event['event']
        if kind=='model_request':
            messages=event['messages'];shared=0
            while shared<min(len(messages),len(prior_messages)) and messages[shared]==prior_messages[shared]:shared+=1
            events.append({'event':kind,'new_messages':project(messages[shared:]),'unchanged_prefix_message_count':shared})
            prior_messages=messages
        elif kind=='codex_session':
            events.append({key:event.get(key) for key in ('event','status','exit_code','input_tokens','output_tokens','seconds')})
        elif kind=='execute':
            events.append({key:event.get(key) for key in ('event','step','code')})
        elif kind=='execution_result':
            item={key:event.get(key) for key in ('event','step','ok','error')}
            for stream in ('stdout','stderr'):
                kept=[];seen=set()
                for output in event.get(stream,'').splitlines():
                    if output.startswith('Fra:') or (' | Sample ' in output):continue
                    if output not in seen:kept.append(output);seen.add(output)
                item[stream]='\n'.join(kept)
            events.append(item)
        elif kind in ('model_response','select'):
            events.append({key:value for key,value in event.items() if key not in ('time','call_dir')})
        elif kind in ('build_started','build_completed','render_started','render_completed'):
            fields=('event','step','status','seconds','returncode','timed_out','timeout',
                    'timeout_seconds','remaining','memory_limit_exceeded','cpu_user_seconds',
                    'cpu_system_seconds','peak_individual_rss_kib','sampled_peak_tree_rss_kib_lower_bound')
            events.append({key:event[key] for key in fields if key in event})
        else:
            events.append(event)
    return {'projection':'Lossless request-prefix deduplication; repeated exact renderer log lines and Cycles progress removed. Full original transcript retained on disk.','events':events}


def bound_payload(payload,limit=420000):
    """Same deterministic input projection for every method, independent of scores."""
    declared_limit=limit
    limit-=4096  # Leave room for the explicit projection record itself.
    changes=[]
    size=lambda:len(json.dumps(payload,ensure_ascii=False).encode())
    before=size()
    for entry in payload.get('archive_raw_development',[]):
        if size()<=limit:break
        entry['trajectory']={'omitted_from_model_input':'Historical transcript omitted under common byte cap; full raw transcript remains archived.'}
        changes.append({'scene_id':entry['scene_id'],'removed':'historical trajectory only'})
    for kind in ('model_request','model_response'):
        for entry in payload.get('development',[])+payload.get('archive_raw_development',[]):
            if size()<=limit:break
            trajectory=entry.get('trajectory',{})
            if 'events' in trajectory:
                trajectory['events']=[e for e in trajectory['events'] if e['event']!=kind]
                changes.append({'scene_id':entry['scene_id'],'removed':kind,'retained':'Full H/system/P and all executed code/errors/results'})
    for entry in payload['development']:
        if size()<=limit:break
        events=entry['trajectory']['events'] if entry['trajectory'] else []
        successful={event['step'] for event in events if event['event']=='execution_result' and event['ok']}
        for event in events:
            if size()<=limit:break
            if event['event']=='execute' and event['code']==entry['program']:
                event['code']={'same_as':'development.program','step':event['step']}
                changes.append({'scene_id':entry['scene_id'],'step':event['step'],'removed':'Duplicate of current full P only'})
        for event in events:
            if size()<=limit:break
            if event['event']=='execute' and event['step'] in successful and isinstance(event['code'],str):
                event['code']={'archived_successful_prototype':event['step'],'current_P':'development.program'}
                changes.append({'scene_id':entry['scene_id'],'step':event['step'],'removed':'Earlier successful prototype code; all failed code/errors and current full P retained'})
    payload['common_evidence_projection']={'original_compact_bytes':before,'limit_bytes':declared_limit,'changes':changes,'full_raw_evidence_retained_on_disk':True,'selection_criterion':'size and fixed source order only, never score','encoding':'A04 compact JSON; projection order and intermediate legacy-size cutoffs unchanged'}
    wire_size=len(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode())
    if wire_size>declared_limit:raise ValueError('Development evidence exceeds frozen byte budget after explicit projection: '+str(wire_size))
    return payload['common_evidence_projection']
