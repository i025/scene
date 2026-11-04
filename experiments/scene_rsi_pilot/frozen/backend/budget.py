"""Single-process observable budget accounting; no content fingerprints."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

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
    return {'cli_sessions':len(sessions)+2,'initial_sandbox_failures':2,'observable_cli_turns':turns,'observable_model_rounds':None,'tool_calls':tools,'known_input_tokens':tokens_in,'known_output_tokens':tokens_out,'usage_unknown_sessions':unknown+2,'render_attempts_upper_bound':frames,'renders_completed':complete_frames,'device':'CPU','max_cli_sessions':600,'max_render_frames':1500}

def guard(kind,amount=1):
    value=current()
    (ROOT/'ledger.json').write_text(json.dumps(value,indent=2))
    key,limit=('cli_sessions',600) if kind=='cli' else ('render_attempts_upper_bound',1500)
    if value[key]+amount>limit:raise RuntimeError('Global budget exhausted: '+kind)
