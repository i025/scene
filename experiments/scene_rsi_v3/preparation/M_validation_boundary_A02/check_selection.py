import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from pilot import run_scene,manifest,H_START
row=run_scene(manifest('selection')[0],H_START,'M000')
assert row['evaluation_status']=='completed', row['bw']
assert row['bw']['delivery_evidence_version']=='original_delivery_metadata_A02'
assert row['bw']['native_evidence_version']=='authored_native_project_facts_A02'
assert next(r['score'] for r in row['bw']['rubric_scores'] if r['id']=='R06')==0
(ROOT/'preparation/M_validation_boundary_A02/corrected_selection_check.json').write_text(json.dumps({'status':'passed','scene_id':row['scene_id'],'S_BW':row['bw']['S_BW'],'R06':0,'new_H_calls':0,'new_renders':0,'score_source':str(Path(row['folder'])/'bw_evidence/evaluation.json')},indent=2)+'\n')
