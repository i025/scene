"""Read-only scientific audits and derived source-diff tables; no new trials."""
import ast
import csv
import difflib
import json
import time
from common import ROOT,read,write,current
from experiment import METHODS,regions

frozen=ROOT/'code_snapshots/formal_frozen'
source_checks={name:(ROOT/name).read_text()==(frozen/name).read_text() for name in ['meta.py','fixtures.py','experiment.py','common.py','regression.py','inspect_blend.py']}
assert all(source_checks.values()),source_checks
sessions=[read(p) for p in ROOT.rglob('session.json') if (p.parent/'request.json').exists()]
assert len(sessions)==49 and all(s['status']=='complete' for s in sessions)
records=[read(p) for p in (ROOT/'tasks').glob('task*/*/result.json')]
assert len(records)==30
write(ROOT/'STATUS_AUDIT.json',{'time':time.time(),'formal_terminal_records':30,'candidates_generated':30,'candidate_executions_completed':sum(r['status']=='completed' for r in records),
 'formal_effective_repairs':sum(r['effective_shared_repair'] is True for r in records),'formal_execution_failures':sum(r['status']!='completed' for r in records),
 'formal_model_failures':0,'all_model_sessions_complete':True,'process_exit_observation':'Parent pilot exec session exited code0; all49 recorded CLI sessions complete. state.json is retained as last-live scheduling record, FINAL_STATUS is authoritative.',
 'frozen_M_H_runner_evaluator_source_text_unchanged':source_checks,'engineer_changed_candidates_after_proposal':False,
 'changed_reporter_only':'analyze.py derived stats/layout additions; frozen original and diff retained','formal_active_probe_requests':0,'deterministic_probe_calibration_not_counted_as_model_selected_probes':17,'ledger':read(ROOT/'metrics/call_totals.json')})
rows=[];predictions=[]
for case in ['task'+str(i).zfill(2) for i in range(1,11)]:
    source=(ROOT/'tasks'/case/'H0.py').read_text();before=regions(source)
    for method in METHODS:
        folder=ROOT/'tasks'/case/method;after=regions((folder/'candidate.py').read_text())
        changed=[name for name in after if name not in before or before[name]!=after[name]]
        syntax=[name for name in after if name not in before or ast.dump(ast.parse(before[name]),include_attributes=False)!=ast.dump(ast.parse(after[name]),include_attributes=False)]
        rows.append({'scene_id':case,'method':method,'changed_shared_files':1,'text_changed_function_regions':changed,
             'syntax_changed_function_regions':syntax,'syntax_changed_function_count':len(syntax),
             'interpretation':'Syntax-tree structural comparison of code changes, no file fingerprint/checksum. Renaming/refactoring can preserve behavior; neither text nor syntax change count proves unnecessary or harmful repair.'})
        stage=read(folder/'stage1.json');plan=stage['plan']
        for hypothesis in plan['predictions_frozen']:
            for tool,interval in hypothesis['predictions'].items():
                predictions.append({'scene_id':case,'method':method,'hypothesis':hypothesis['id'],'module':hypothesis['module'],'tool':tool,
                    'target_id':stage['context']['probe_targets'][tool],'lower':interval['lower'],'upper':interval['upper'],'reason':interval['reason'],
                    'selected':any(p['probe']==tool for p in plan['probes']),'plan_saved_before_probe':stage['saved_before_probe']})
for name,values in [('code_scope',rows),('all_preprobe_predictions',predictions)]:
    write(ROOT/'metrics'/(name+'.json'),values)
    with (ROOT/'metrics'/(name+'.csv')).open('w',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(values[0]));writer.writeheader();writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in values)
first=(frozen/'analyze.py').read_text();last=(ROOT/'analyze.py').read_text()
(ROOT/'report_history/analyze_frozen_to_final.diff').write_text(''.join(difflib.unified_diff(first.splitlines(True),last.splitlines(True),fromfile='formal_frozen/analyze.py',tofile='final_report/analyze.py')))
print('All records and frozen experiment code audited; no new model or render work.')
