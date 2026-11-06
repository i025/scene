"""Shared V3 safety caps from actual log records; absent usage stays unknown."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def limits():return json.loads((ROOT/'config.json').read_text())['pilot']
def current():
    sessions=[json.loads(p.read_text()) for p in ROOT.rglob('session.json') if 'code_snapshots' not in p.parts]
    requests=list(ROOT.rglob('request.json'))
    attempts=ROOT/'render_attempts.jsonl'
    frames=sum(json.loads(l)['frames'] for l in attempts.read_text().splitlines()) if attempts.exists() else 0
    return {'cli_sessions':len(requests),'render_attempts':frames,
            'known_input_tokens':sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'),int)),
            'known_output_tokens':sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'),int)),
            'usage_known_sessions':sum(isinstance(s.get('input_tokens'),int) for s in sessions),
            'usage_unknown_sessions':sum(not isinstance(s.get('input_tokens'),int) for s in sessions),
            'observable_tool_calls':sum(s.get('tool_calls',0) for s in sessions)}
def guard(kind,amount=1):
    value=current();cap=limits()
    phase=ROOT/'budget_phase.json'
    if phase.exists() and json.loads(phase.read_text())['phase']=='research':
        fraction=1-cap['reserve_fraction']
        cap={**cap,**{k:int(cap[k]*fraction) for k in ['max_cli_sessions','max_render_frames','max_input_tokens','max_output_tokens']}}
    (ROOT/'ledger.json').write_text(json.dumps(value,indent=2)+'\n')
    for key,maxkey in [('known_input_tokens','max_input_tokens'),('known_output_tokens','max_output_tokens')]:
        if value[key]>=cap[maxkey]:raise RuntimeError('Visible token safety cap reached: '+key)
    key,maxkey=('cli_sessions','max_cli_sessions') if kind=='cli' else ('render_attempts','max_render_frames')
    if value[key]+amount>cap[maxkey]:raise RuntimeError('Budget exhausted: '+kind)
    if kind=='render':
        import time
        with (ROOT/'render_attempts.jsonl').open('a') as out:out.write(json.dumps({'time':time.time(),'frames':amount})+'\n')
