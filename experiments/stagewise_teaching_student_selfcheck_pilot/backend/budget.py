"""Count actual new CLI attempts and render submissions; no quality metrics."""
import json
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent


def current():
    bases = [ROOT/'tasks', ROOT/'transfer', ROOT/'preparation/model_checks']
    sessions = [json.loads(p.read_text()) for base in bases for p in base.glob('**/session.json')]
    requests = [p for base in bases for p in base.glob('**/request.json')]
    path = ROOT / 'render_attempts.jsonl'
    frames = sum(json.loads(x)['frames'] for x in path.read_text().splitlines()) if path.exists() else 0
    builds = ROOT/'build_attempts.jsonl'
    return {'cli_sessions':len(requests), 'render_attempts':frames,
            'build_attempts':len(builds.read_text().splitlines()) if builds.exists() else 0,
            'development_cli':sum(p.is_relative_to(ROOT/'tasks/D01') or p.is_relative_to(ROOT/'transfer') for p in requests),
            'test_cli':sum(p.is_relative_to(ROOT/'tasks/T01') for p in requests),
            'preparation_cli':sum(p.is_relative_to(ROOT/'preparation/model_checks') for p in requests),
            'known_input_tokens':sum(s['input_tokens'] for s in sessions if isinstance(s.get('input_tokens'),int)),
            'known_output_tokens':sum(s['output_tokens'] for s in sessions if isinstance(s.get('output_tokens'),int)),
            'usage_known_sessions':sum(isinstance(s.get('input_tokens'),int) for s in sessions),
            'usage_unknown_sessions':sum(not isinstance(s.get('input_tokens'),int) for s in sessions),
            'observable_tool_calls':sum(s.get('tool_calls',0) for s in sessions)}


def guard(kind, amount=1):
    value = current()
    cap = json.loads((ROOT/'config.json').read_text())['pilot']
    key, limit = {'cli':('cli_sessions','max_cli_sessions'),
                  'render':('render_attempts','max_render_frames'),
                  'build':('build_attempts','max_build_attempts')}[kind]
    (ROOT/'ledger.json').write_text(json.dumps(value,indent=2)+'\n')
    if value[key]+amount > cap[limit]:
        raise RuntimeError('Frozen budget exhausted: '+kind)
    if kind=='render':
        with (ROOT/'render_attempts.jsonl').open('a') as out:
            out.write(json.dumps({'time':time.time(),'frames':amount})+'\n')
    if kind=='build':
        with (ROOT/'build_attempts.jsonl').open('a') as out:
            out.write(json.dumps({'time':time.time(),'attempts':amount})+'\n')


def guard_partition(partition):
    value = current()
    cap = json.loads((ROOT/'config.json').read_text())['pilot']
    if value[partition+'_cli']+1 > cap[partition+'_cli_limit']:
        raise RuntimeError('Frozen partition CLI budget exhausted: '+partition)
