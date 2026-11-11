import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from bw_evaluate import judge_artifact
from data import write_json
c=json.loads((ROOT/'config.json').read_text())
scene=next(s for s in json.loads((ROOT/'manifest.json').read_text()) if s['scene_id']=='bw_0045')
folder=ROOT/'results/historical_r1_C2_start/selection/bw_0045/1'
rubric=json.loads(Path(scene['rubric_path']).read_text())
result=judge_artifact(folder/'reference.png',folder/'bw_evidence',rubric,c,folder/'judge_A03_1')
if result['evaluation_status']=='eval_failed':
 write_json(folder/'bw_evidence/evaluation_A03_attempt1.json',result)
 result=judge_artifact(folder/'reference.png',folder/'bw_evidence',rubric,c,folder/'judge_A03_2')
write_json(ROOT/'preparation/lighting_evidence_A03/controlled_evaluator_check.json',{'status':'passed' if result['evaluation_status']=='completed' else 'failed','evaluation_status':result['evaluation_status'],'error':result.get('evaluation_error'),'S_BW':result['S_BW'],'role':'judge','scope':'Planned actual baseline re-evaluation, reused by launch004; not an additional preparation judge','new_H_calls':0,'new_renders':0,'usage':result.get('judge_usage')})
assert result['evaluation_status']=='completed',result.get('evaluation_error')
