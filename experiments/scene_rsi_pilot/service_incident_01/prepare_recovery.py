"""One explicit service retry, preserving failures and excluding valid outputs."""
from pathlib import Path
import difflib
import json
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from budget import current
from data import write_json

if (HERE/'recovery_prepared.json').exists():
    raise SystemExit('Recovery already prepared; do not create another retry.')

def read(p):return json.loads(p.read_text())
def routed(folder):
    return any('workspace routing discovery failed' in p.read_text() for p in folder.glob('student_calls/*/events.jsonl'))
def move(p):
    target=HERE/'retired'/p.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    p.rename(target)
    moved.append({'original':str(p.relative_to(ROOT)),'preserved':str(target.relative_to(ROOT))})

rows=[(p,read(p)) for p in (ROOT/'results').glob('*/*/*/*/*/record.json')]
test=[(p,r) for p,r in rows if r['run_id'] in ('r1','r2') and r['split']=='test']
assert len(test)==32 and all(not r['metrics']['valid'] and not (p.parent/'final.png').exists() for p,r in test)
retry_scenes=[]
for p,r in rows:
    if r['status']!='failed' or r['split'] not in ('selection','test','external'):continue
    source=Path(r['reuse_of']) if r.get('reuse_of') else p.parent
    assert routed(source),str(source)
    assert not r['metrics']['valid'] and not (p.parent/'final.png').exists()
    retry_scenes.append((p,r))

failures=[]
for p in ROOT.rglob('session.json'):
    s=read(p);events=p.with_name('events.jsonl')
    if s['status']=='failed' and events.exists() and 'workspace routing discovery failed' in events.read_text():
        failures.append({'source':str(p.relative_to(ROOT)),'started':s.get('started'),'seconds':s.get('seconds'),'input_tokens':s.get('input_tokens'),'output_tokens':s.get('output_tokens')})
write_json(HERE/'routing_failures.json',failures)
write_json(HERE/'failed_scene_attempts.json',[r for p,r in retry_scenes])
write_json(HERE/'budget_before_recovery.json',current())
moved=[]
for name in ['archive.json','config.json','protocol.md','protocol_frozen.json']:
    shutil.copy2(ROOT/name,HERE/name)
for p,r in retry_scenes:move(p.parent)

retry_proposals=[]
for p in sorted((ROOT/'candidates').glob('*/*/*/proposal_result.json')):
    result=read(p)
    if result['status']!='proposal_failed':continue
    calls=list(p.parent.glob('proposal_call*/session.json'))
    failed=[c for c in calls if read(c)['status']=='failed' and 'workspace routing discovery failed' in c.with_name('events.jsonl').read_text()]
    if not failed:continue
    assert all(read(c)['status']=='failed' and not read(c).get('usage_events') for c in calls)
    retry_proposals.append(str(p.parent.relative_to(ROOT)))
    backup=HERE/'proposal_context_before_retry'/p.parent.relative_to(ROOT)
    backup.mkdir(parents=True,exist_ok=True)
    for old in p.parent.iterdir():
        if old.is_file():shutil.copy2(old,backup/old.name)
    for c in calls:move(c.parent)
    move(p)

for name in ['selection_freeze.json','selections.json','ablation_archive.json','ablation_protocol.json','ablation_selection_freeze.json','ablation_reference_selection.json','extras_status.json','replay_status.json','external_status.json','external_protocol.json','judgments','external_judgments','external_inputs']:
    p=ROOT/name
    if p.exists():move(p)

cfg=read(ROOT/'config.json')
cfg['service_recovery']={'id':'service_incident_01','max_additional_retry_per_affected_task':1,'only_no_output_routing_failures_reopened':True,'valid_scene_outputs_retained':True,'new_submission_pauses_on_routing_failure':True,'all_costs_preserved':True,'test_outputs_before_recovery':0,'ablation_scope_recomputed_from_remaining_budget_after_main':True}
write_json(ROOT/'config.json',cfg)
with (ROOT/'protocol.md').open('a') as f:
    f.write('''\n## 服务故障恢复补充（2026-11-02，非原始预注册）\n
Codex CLI 的 workspace routing discovery failed 在第一轮 C2 开发末段后连续出现。主终测的32个方法槽均无有效图像或指标，所有消融提案也均未返回模型输出。原选择冻结与全部失败记录移入 service_incident_01/retired，未删除失败分母或费用。新进程的真实图片最小调用恢复成功后，对无输出的服务故障任务统一开放最多一次额外尝试；正常生成错误、无效提案、已有有效场景不重采样。每次重试仍受共同5次学生调用、3次执行与原时限约束，全部新增调用计入600总上限。普通续跑不再次重试已经记录的失败。若路由再次失败，统一停止新提交。\n
由于没有有效终测反馈，恢复尚未完成的 C2 研发后重新冻结选择，之后再统一终测；原先在服务故障下生成的冻结文件保留作为历史事件，不称为最终科学结论。消融原先的2重复K2计划没有任何有效提案，恢复后按原先公开的剩余预算阶梯重新决定可完成规模，避免故障后仍按失真的剩余预算越限。未被重新纳入预算的旧消融失败保持服务失败/未完成，不改称成功。\n
报告分别保留原始失败尝试、恢复后的任务结果和物理执行成本。两个有效场景中的末次服务失败不触发整个场景重采样。代码中的停提交改动仅属共同运行器故障处理，不修改任何 H/M、评价函数或模型提示词。\n''')
for before,after,name in [(HERE/'backend_before/codex_wrapper.py',ROOT/'backend/codex_wrapper.py','codex_wrapper'),(HERE/'backend_before/pilot.py',ROOT/'pilot.py','pilot'),(HERE/'report_fix/analyze_before.py',ROOT/'analyze.py','analyze')]:
    (HERE/(name+'.diff')).write_text(''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='before/'+name+'.py',tofile='after/'+name+'.py')))
result={'time':time.time(),'status':'prepared_once','failed_scene_attempts_preserved':len(retry_scenes),'physical_scene_attempts_preserved':sum(not r.get('reuse_of') for p,r in retry_scenes),'candidate_proposals_reopened':retry_proposals,'routing_failures_including_prior_retained_timeout':len(failures),'valid_test_outputs_before_recovery':0,'moves':moved,'selection_will_refreeze_before_any_valid_test':True,'remaining_main_upper_bound_cli':328}
write_json(HERE/'recovery_prepared.json',result)
write_json(ROOT/'state.json',{'phase':'service_recovery_prepared','time':time.time(),'incident':'service_incident_01','no_jobs_running':True})
write_json(ROOT/'ledger.json',current())
print({k:v for k,v in result.items() if k not in ['moves','candidate_proposals_reopened']})
