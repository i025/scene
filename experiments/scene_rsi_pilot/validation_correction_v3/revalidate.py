"""Revalidate saved original proposals once; never call models or rewrite their content."""
from pathlib import Path
import ast,difflib,json,sys,time
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from pilot import validate_source
AUDIT=ROOT/'validation_correction_v3'
results=[]
for snapshot in sorted((AUDIT/'candidates').glob('*/*/*/proposal_result.json')):
 relative=snapshot.parent.relative_to(AUDIT/'candidates');candidate=ROOT/'candidates'/relative
 original=json.loads(snapshot.read_text());method=relative.parts[1]
 response=next((candidate/n/'response.txt' for n in ('proposal_call_2','proposal_call') if (candidate/n/'response.txt').exists()),None)
 if response is None:
  results.append({'candidate':str(relative),'old_status':original['status'],'status':'no_raw_response_preserve_original'});continue
 answer=json.loads(response.read_text());changes={item['path']:item['content'] for item in answer['files']}
 source=Path(original['parent_source']);meta=Path(original['used_M'])
 parents={n:(source/n).read_text() for n in ('policy.py','system.txt')};parents['meta.py']=meta.read_text()
 audit={'candidate':str(relative),'raw_response':str(response.relative_to(ROOT)),'old_status':original['status'],'old_error':original.get('error'),'additional_model_calls':0,'source_content_edited_by_engineer':False,'version':'v3_type_name_logging'}
 try:
  if answer.get('requested_probes'):raise ValueError('Original response requested unresolved probes')
  if method=='sceneevolve_cli' and 'meta.py' in changes and changes['meta.py']!=parents['meta.py']:raise ValueError('SceneEvolve meta must stay fixed')
  for name,content in changes.items():
   if name not in parents:raise ValueError('File outside allowed set')
   if name.endswith('.py'):validate_source(content,name)
  if all(changes.get(n,parents[n])==parents[n] for n in ('policy.py','system.txt')):raise ValueError('Candidate did not modify shared H')
 except (ValueError,SyntaxError) as error:
  audit.update(status='rejected',error=str(error));result={**original,'status':'proposal_failed','error':str(error),'validation_version':'v3_type_name_logging'}
 else:
  merged={**parents,**changes}
  # These bytes come directly from the original CLI response or unchanged parent.
  for name,content in merged.items():
   if (candidate/name).read_text()!=content:
    if original['status']=='proposed':raise RuntimeError('Previously accepted source differs from original response')
    (candidate/name).write_text(content)
  diff=''.join(''.join(difflib.unified_diff(parents[n].splitlines(True),merged[n].splitlines(True),fromfile='parent/'+n,tofile=relative.parts[-1]+'/'+n)) for n in parents)
  (candidate/'changes.diff').write_text(diff)
  trees=[ast.parse(parents['meta.py']),ast.parse(merged['meta.py'])]
  for tree in trees:
   for node in ast.walk(tree):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):node.value='<string>'
  changed=ast.dump(trees[0])!=ast.dump(trees[1])
  result={**answer,'M_strategy_structure_changed':changed,'status':'proposed','M_changed':merged['meta.py']!=parents['meta.py'],'parent_source':str(source),'used_M':str(meta),'validation_version':'v3_type_name_logging','revalidation':audit}
  audit.update(status='accepted',newly_eligible=original['status']!='proposed',M_changed=result['M_changed'],M_strategy_structure_changed=changed)
 (candidate/'proposal_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 (candidate/'validation_v3.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));results.append(audit)
archive_path=ROOT/'archive.json';archive=json.loads(archive_path.read_text())
for entry in archive:
 matching=next((r for r in results if r['candidate']=='/'.join(entry[k] for k in ('run_id','method','candidate_id'))),None)
 if matching and matching.get('newly_eligible'):
  entry.update(status='revalidation_pending_evaluation',accepted=False,previous_status_v2=matching['old_status'],validation_version='v3_type_name_logging')
archive_path.write_text(json.dumps(archive,ensure_ascii=False,indent=2))
(AUDIT/'revalidation.json').write_text(json.dumps({'time':time.time(),'results':results,'extra_model_calls':0,'test_feedback_used':False},ensure_ascii=False,indent=2))
print(json.dumps(results,indent=2))
