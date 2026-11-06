"""Single-process observable budget accounting; no content fingerprints."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def limits():
    return json.loads((ROOT/'config.json').read_text())['pilot']

def current():
    sessions=list(ROOT.rglob('request.json'))
    sessions=[p for p in sessions if p.parent.joinpath('session.json').exists()]
    frames=len(list(ROOT.rglob('steps/*/build.py')))
    complete_frames=len(list(ROOT.rglob('steps/*/final.png')))
    for p in ROOT.rglob('render_ledger.json'):
        if p.is_symlink():continue
        d=json.loads(p.read_text());frames+=d.get('render_attempts',0);complete_frames+=d.get('renders_completed',0)
    tokens_in=tokens_out=turns=tools=0;unknown=0
    for p in sessions:
        s=json.loads(p.with_name('session.json').read_text())
        if isinstance(s.get('total_tokens'),int):
            tokens_in+=s['input_tokens'];tokens_out+=s['output_tokens']
        else:unknown+=1
        turns+=s.get('observable_cli_turns') or sum('"turn.started"' in l for l in p.with_name('events.jsonl').read_text().splitlines()) if p.with_name('events.jsonl').exists() else 0
        tools+=s.get('tool_calls',len(s.get('tool_events',[])))
    device_counts={}
    for p in ROOT.rglob('actual_device.json'):
        if p.is_symlink():continue
        device=json.loads(p.read_text())['device']
        device_counts[device]=device_counts.get(device,0)+1
    # Original jobs predate per-render mapping and were explicitly CPU-only.
    devices={'CPU',*device_counts}
    return {'cli_sessions':len(sessions),'initial_sandbox_failures':0,'observable_cli_turns':turns,'observable_model_rounds':None,'tool_calls':tools,'known_input_tokens':tokens_in,'known_output_tokens':tokens_out,'usage_unknown_sessions':unknown,'render_attempts_upper_bound':frames,'renders_completed':complete_frames,'device':'+'.join(sorted(devices)),'device_mapping_record_counts':device_counts,'max_cli_sessions':limits()['max_cli_sessions'],'max_render_frames':limits()['max_render_frames']}

def guard(kind,amount=1):
    value=current()
    (ROOT/'ledger.json').write_text(json.dumps(value,indent=2))
    key,limit=('cli_sessions',limits()['max_cli_sessions']) if kind=='cli' else ('render_attempts_upper_bound',limits()['max_render_frames'])
    if value[key]+amount>limit:raise RuntimeError('Global budget exhausted: '+kind)
