"""Counterexamples for source/repeat accounting; no real task or model execution."""
import ast
import copy
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent
source=HERE.parents[1]/'analyze.py'
tree=ast.parse(source.read_text())
names={'mean','paired_test_data'}
scope={'statistics':statistics,'TERMINAL':{'completed','failed','timeout','invalid'}}
exec(compile(ast.Module(body=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names],type_ignores=[]),str(source),'exec'),scope)
pair=scope['paired_test_data']
manifest=[{'scene_id':'fixture','split':'test'}]
state={'H_start':'start','H_best':'best'}

def row(version,repeat,bw,*,status='completed',valid=True,utility=None):
    return {'scene_id':'fixture','split':'test','H_version':version,'repeat':repeat,
            'status':status,'valid':valid,'BW':bw,'Q':None,
            'e2e_BW_utility':bw if utility is None else utility}


records=[row('start',1,60),row('start',2,80),row('best',1,70),
         row('best',2,None,status='failed',valid=False,utility=0)]
rows,points=pair(records,manifest,state,2)
d=rows[0]
assert d['start_execution_success']==2 and d['best_execution_success']==1
assert d['start_BW_conditional']==70 and d['best_BW_conditional']==70
assert d['BW_paired_difference']==10 and d['paired_successful_generations']==1
assert d['start_BW_utility']==70 and d['best_BW_utility']==35 and d['BW_utility_difference']==-35
assert points[-1]['BW'] is None and points[-1]['utility']==0
checks=['Matched successes give +10, while all-scheduled utility gives -35; raw failure BW remains null']
service=copy.deepcopy(records);service[-1]=row('best',2,None)
d=pair(service,manifest,state,2)[0][0]
assert d['best_execution_success']==2 and d['best_BW_utility'] is None and d['BW_utility_difference'] is None
checks.append('Valid scene with failed/missing evaluation does not acquire zero utility')
d=pair(records[:-1],manifest,state,2)[0][0]
assert d['best_finished']==1 and d['best_BW_utility'] is None
empty,empty_points=pair([],manifest,state,2)
assert empty[0]['BW_paired_difference'] is None and empty[0]['BW_utility_difference'] is None
assert all(point['BW'] is None and point['status']=='not_started' for point in empty_points)
checks.append('Pending repeats and wholly unstarted Test retain null, with planned denominator two')
same=pair(records[:2],manifest,{'H_start':'start','H_best':'start'},2)[0][0]
assert same['same_H_artifact_reuse'] and same['BW_paired_difference']==0
checks.append('Same-H reuse is explicitly labelled and never becomes a new generation')
result={'status':'passed','checks':checks,'fixture_only':True,'new_CLI_calls':0,'new_Blender_jobs':0}
(HERE/'paired_statistics_tests.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
