"""Count actual new CLI attempts and render submissions; no quality metrics."""
import json
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent


def current():
    sessions = [json.loads(p.read_text()) for p in ROOT.glob('tasks/**/session.json')]
    sessions += [json.loads(p.read_text()) for p in ROOT.glob('self_modification/**/session.json')]
    requests = list(ROOT.glob('tasks/**/request.json')) + list(ROOT.glob('self_modification/**/request.json'))
    path = ROOT / 'render_attempts.jsonl'
    frames = sum(json.loads(x)['frames'] for x in path.read_text().splitlines()) if path.exists() else 0
    return {'cli_sessions':len(requests), 'render_attempts':frames,
            'known_input_tokens':sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'),int)),
            'known_output_tokens':sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'),int)),
            'usage_known_sessions':sum(isinstance(s.get('input_tokens'),int) for s in sessions),
            'usage_unknown_sessions':sum(not isinstance(s.get('input_tokens'),int) for s in sessions),
            'observable_tool_calls':sum(s.get('tool_calls',0) for s in sessions)}


def guard(kind, amount=1):
    value = current()
    cap = json.loads((ROOT/'config.json').read_text())['pilot']
    key, limit = ('cli_sessions','max_cli_sessions') if kind=='cli' else ('render_attempts','max_render_frames')
    (ROOT/'ledger.json').write_text(json.dumps(value,indent=2)+'\n')
    if value[key]+amount > cap[limit]:
        raise RuntimeError('Frozen budget exhausted: '+kind)
    if kind=='render':
        with (ROOT/'render_attempts.jsonl').open('a') as out:
            out.write(json.dumps({'time':time.time(),'frames':amount})+'\n')
