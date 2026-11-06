"""Known pending/failure/pair cases; does not alter any experimental record."""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import analyze

rows=analyze.measured_rows()
for row in rows:
    row.update(status='not_started',execution_success=None,functional_pass=None,Q=None,utility=None)
summary,pairs=analyze.summarize(rows)
assert summary['H0']['success_rate_all_scheduled'] is None
assert summary['r1_C2']['utility_all_scheduled'] is None
assert summary['pairs']['both_success_n']==0
failed=copy.deepcopy(rows)
for row in failed:row.update(status='failed',execution_success=False,functional_pass=False,utility=0)
summary,pairs=analyze.summarize(failed)
assert summary['H0']['conditional_Q'] is None
assert summary['H0']['utility_all_scheduled']==0
assert summary['H0']['success_rate_all_scheduled']==0
paired=copy.deepcopy(failed)
a=next(r for r in paired if r['candidate_id']=='H0')
b=next(r for r in paired if r['candidate_id']=='r1_C2' and r['scene_id']==a['scene_id'] and r['run_id']==a['run_id'])
a.update(status='completed',execution_success=True,Q=.4,utility=.4)
b.update(status='completed',execution_success=True,Q=.5,utility=.5)
summary,pairs=analyze.summarize(paired)
assert summary['pairs']['both_success_n']==1
assert abs(summary['pairs']['conditional_paired_Q_difference']-.1)<1e-9
analyze.save(analyze.ROOT/'tests/report_contracts.json',{'status':'passed','cases':['pending is not zero percent','failed raw Q remains null','failure utility separate zero','only both-success pairs contribute Q differences'],'remote_model_calls':0})
print('REPORT_CONTRACTS_PASSED')
