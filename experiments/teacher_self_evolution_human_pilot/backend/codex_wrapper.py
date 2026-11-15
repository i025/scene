"""Existing CLI transport, staged images and observable accounting for V3."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import threading
from data import write_json
from processes import cpu_environment, run_group
ROOT=Path(__file__).resolve().parent.parent

DISABLED_FEATURES = (
    'shell_tool', 'unified_exec', 'apps', 'plugins', 'hooks', 'multi_agent',
    'browser_use', 'browser_use_external', 'browser_use_full_cdp_access',
    'computer_use', 'image_generation', 'memories', 'skill_search',
    'workspace_dependencies', 'sleep_tool', 'view_image',
)


def check_service_pause():
    pause=ROOT/'protocol_pause.json' if (ROOT/'protocol_pause.json').exists() else ROOT/'service_pause.json'
    if pause.exists():
        raise RuntimeError('Service submissions paused: '+str(pause))

def command(settings, workspace, response, images, schema=None):
    args=[settings['command'],'exec','--ephemeral','--json','--skip-git-repo-check',
          '--sandbox','read-only','--cd',str(workspace),'--model',settings.get('model',settings.get('name')),
          '--output-last-message',str(response)]
    for key,value in {'model_reasoning_effort':settings['reasoning_effort'],'approval_policy':'never',
                       'web_search':'disabled','mcp_servers':{},'project_doc_max_bytes':0}.items():
        args+=['-c',key+'='+json.dumps(value)]
    for feature in DISABLED_FEATURES:args+=['--disable',feature]
    if schema:args+=['--output-schema',str(schema)]
    for path in images:args+=['--image',str(path)]
    return args+['-']

def audit_events(folder):
    events=[]; malformed=0
    for line in (folder/'events.jsonl').read_text().splitlines():
        try:events.append(json.loads(line))
        except json.JSONDecodeError:malformed+=1
    items={}
    for e in events:
        item=e.get('item',{})
        if item:items[item.get('id',str(len(items)))]=item
    counts={key:sum(i.get('type')==key for i in items.values()) for key in
            ['command_execution','file_change','mcp_tool_call','web_search','image_view','collab_tool_call']}
    usages=[e['usage'] for e in events if e['type']=='turn.completed' and 'usage' in e]
    usage={k:sum(u[k] for u in usages) if usages and all(isinstance(u.get(k),int) for u in usages) else None
           for k in ['input_tokens','output_tokens','cached_input_tokens']}
    model_events=[e['model'] for e in events if isinstance(e.get('model'),str)]
    return {**usage,'observed_model':model_events[-1] if model_events else 'unknown',
            'observed_model_source':'CLI JSON model field' if model_events else None,
            'cli_sessions':1,'observable_cli_turns':sum(e['type']=='turn.started' for e in events),
            'observable_tool_counts':counts,'tool_calls':sum(counts.values()),
            'observable_model_requests_lower_bound':1 if any(e['type']=='turn.completed' for e in events) else 0,
            'exact_model_requests':None,'request_visibility_coverage':None,
            'events_malformed_lines':malformed,'usage_events':usages,
            'tool_events':[e for e in events if e.get('item',{}).get('type') in counts],
            'first_event_time':None,'raw_event_count':len(events)}

def call(prompt,settings,folder,images=(),*,role,timeout=None,schema=None,log=None):
    from budget import guard
    check_service_pause();guard('cli')
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    if (folder/'request.json').exists():raise FileExistsError('Never overwrite a CLI attempt: '+str(folder))
    anonymous=ROOT/'session_staging';anonymous.mkdir(exist_ok=True)
    workspace=anonymous/('S'+str(time.time_ns()));workspace.mkdir()
    staged=[]
    for n,source in enumerate(images):
        target=workspace/f'image_{n:03d}{Path(source).suffix}'
        shutil.copy2(source,target);staged.append(target)
    (folder/'prompt.txt').write_text(prompt)
    response=folder/'response.txt';schema_path=None
    if schema:
        schema_path=folder/'response_schema.json';write_json(schema_path,schema)
    args=command(settings,workspace,response,staged,schema_path)
    request={'role':role,'requested_model':settings.get('model',settings.get('name')),
             'reasoning_effort':settings['reasoning_effort'],'images':[str(p) for p in staged],
             'original_images_for_audit':list(map(str,images)),'command':args,
             'fresh_session':True,'sandbox':'read-only','tools_disabled':list(DISABLED_FEATURES),
             'project_doc_max_bytes':0,'hidden_history':'ephemeral session; project docs disabled; global system prompt not independently observable','cost_usd':None}
    write_json(folder/'request.json',request)
    start=time.monotonic();error=None;rc=None
    session={**request,'started':time.time(),'status':'running'}
    write_json(folder/'session.json',session)
    cfg=json.loads((ROOT/'config.json').read_text())
    first_event=[];stop_watch=threading.Event()
    def watch_events():
        path=folder/'events.jsonl'
        while not stop_watch.wait(.05):
            if path.exists() and path.stat().st_size:
                first_event.append(time.time());return
    watcher=threading.Thread(target=watch_events,daemon=True);watcher.start()
    try:
        with (folder/'prompt.txt').open() as inp,(folder/'events.jsonl').open('w') as out,(folder/'stderr.log').open('w') as err:
            rc=run_group(args,timeout=timeout or settings['timeout'],stdin=inp,stdout=out,stderr=err,
                         cwd=workspace,env=cpu_environment(threads=cfg['resources']['threads_per_metric']),
                         measurement_path=folder/'process.json',memory_limit_bytes=int(cfg['resources']['memory_limit_gb']*1024**3))
    except (subprocess.TimeoutExpired,OSError) as exc:
        error=repr(exc)
    stop_watch.set();watcher.join()
    session.update(exit_code=rc,error=error,finished=time.time(),seconds=time.monotonic()-start)
    session.update(audit_events(folder))
    session['first_event_time']=first_event[0] if first_event else None
    session['first_event_time_scope']='First nonempty CLI stdout observed at 50ms sampling; not model inference start'
    session['service_queue_seconds']=None
    session['actual_model']=session['observed_model']
    session['status']='completed' if rc==0 and error is None else 'timeout' if error and 'TimeoutExpired' in error else 'failed'
    session['total_tokens']=session['input_tokens']+session['output_tokens'] if all(isinstance(session[k],int) for k in ['input_tokens','output_tokens']) else None
    session['H_execution_bypass_detected']=role=='H' and session['tool_calls']>0
    session['nested_agent_status']='No tools observed; backend request count unknown' if not session['tool_calls'] else 'CLI-adapted nested agent'
    write_json(folder/'session.json',session)
    if log:log({'event':'codex_session',**session,'call_dir':str(folder)})
    if session['status']!='completed':
        failure_text=(folder/'events.jsonl').read_text()+(folder/'stderr.log').read_text()
        marker=next((v for v in ['workspace routing discovery failed','hit your usage limit','Connection refused'] if v in failure_text),None)
        if marker:write_json(ROOT/'service_pause.json',{'reason':marker,'session':str(folder),'time':time.time(),'note':'Service/transport evidence; no attribution to scene algorithm; no further submissions until explicit recovery'})
        raise RuntimeError(f"CLI {session['status']}: {folder}; {error}")
    if session['tool_calls']:
        write_json(ROOT/'protocol_pause.json',{'reason':'Unexpected internal CLI tools','session':str(folder),'time':time.time()})
        raise RuntimeError('Unexpected inner tools; preserved and charged: '+str(folder))
    return response.read_text().strip(),session
