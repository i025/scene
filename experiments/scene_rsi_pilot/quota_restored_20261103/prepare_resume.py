"""User-authorized resumption after quota restoration, with old failures retained."""
from pathlib import Path
import json
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from budget import current
from data import write_json

def read(p):return json.loads(p.read_text())
def limited(folder):return any('hit your usage limit' in p.read_text() for p in folder.glob('student_calls/*/events.jsonl'))

assert not (HERE/'recovery_prepared.json').exists(),'This resumption has already been prepared'
for model in ['sol','astra']:assert read(HERE/('check_'+model)/'session.json')['status']=='complete'
assert read(ROOT/'smoke/gpu_reassignment_check/actual_device.json')['gpu_uuid']=='GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5'
rows=[(p,read(p)) for p in (ROOT/'results').glob('*/*/*/*/*/record.json')]
tests=[(p,r) for p,r in rows if r['run_id'] in ('r1','r2') and r['split']=='test']
assert len(tests)==32 and all(not r['metrics']['valid'] and not (p.parent/'final.png').exists() for p,r in tests)
affected=[]
for p,r in rows:
    if r['status']=='failed' and limited(Path(r.get('reuse_of',p.parent))):
        assert not r['metrics']['valid'] and not (p.parent/'final.png').exists()
        affected.append((p,r))
assert len(affected)==50 and sum(not r.get('reuse_of') for p,r in affected)==24
write_json(HERE/'failed_scene_attempts.json',[r for p,r in affected])
write_json(HERE/'valid_partial_scenes_retained.json',[r for p,r in rows if r['status']=='complete' and r.get('observed_model_service_failure')=='cli_usage_limit'])
write_json(HERE/'budget_before_resume.json',current())
moves=[]
def move(p):
    dest=HERE/'retired'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);p.rename(dest)
    moves.append({'original':str(p.relative_to(ROOT)),'preserved':str(dest.relative_to(ROOT))})
for name in ['config.json','protocol.md','archive.json','protocol_frozen.json','state.json']:
    shutil.copy2(ROOT/name,HERE/('before_'+name))
for p,r in affected:move(p.parent)
proposals=[]
for p in sorted((ROOT/'candidates').glob('*/*/*/proposal_result.json')):
    result=read(p);calls=list(p.parent.glob('proposal_call*/session.json'))
    if result['status']!='proposal_failed' or not any('hit your usage limit' in c.with_name('events.jsonl').read_text() for c in calls):continue
    assert all(read(c)['status']=='failed' and not read(c).get('usage_events') for c in calls)
    backup=HERE/'proposal_context_before_retry'/p.parent.relative_to(ROOT);backup.mkdir(parents=True,exist_ok=True)
    for f in p.parent.iterdir():
        if f.is_file():shutil.copy2(f,backup/f.name)
    for c in calls:move(c.parent)
    proposals.append(str(p.parent.relative_to(ROOT)));move(p)
for name in ['model_usage_limit.json','selections.json','selection_freeze.json','extras_status.json','ablation_archive.json','ablation_protocol.json','ablation_selection_freeze.json','ablation_reference_selection.json','supplement_status.json','replay_status.json','external_status.json','external_protocol.json','judgments','external_judgments','external_inputs']:
    p=ROOT/name
    if p.exists():move(p)
cfg=read(ROOT/'config.json');cfg['resources']['gpu_allowlist']=['GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5']
cfg['resources']['authorization']='2026-11-02 user permits idle GPU; 2026-11-03 GPU0 busy, GPU1 verified idle; one experiment GPU at a time'
cfg['quota_restoration']={'id':'quota_restored_20261103','user_instruction':'现在Codex CLI 的额度限制解除了，还没完成的实验先完成','no_output_quota_failures_reopened_once':True,'valid_partial_artifacts_retained_without_resampling':True,'ordinary_program_and_validation_failures_unchanged':True,'max_cli_sessions_unchanged':600,'reselect_before_any_valid_main_test_feedback':True,'additional_phase_scale_from_remaining_budget_only':True}
write_json(ROOT/'config.json',cfg)
with (ROOT/'protocol.md').open('a') as f:f.write('''\n## 用户通知额度恢复后的续跑（2026-11-03）\n
用户明确要求“现在Codex CLI 的额度限制解除了，还没完成的实验先完成”。两个指定模型均已通过新的真实图片最小调用。依据这一新增授权，对额度耗尽且无有效输出的任务统一开放一次恢复；不是自动重复服务重试。35次额度失败和所有旧路由失败、冻结及费用完整保留，仍在600会话/1500帧总预算内。再次发生额度或路由失败即停止新提交。没有更换模型、提示、验收目标、数据或内层预算。\n
50条失败场景槽（24次物理重建、26次H0复用）及10次无输出提案被移入quota_restored_20261103/retired后待补。已成功的33条场景保留；其中有有效产物但内层被额度中断的记录也保留原状态与错误，不重采样。正常程序失败和r2/Ours/C1的验证拒绝均不重新尝试。此时全部32个主Test槽仍无任何有效图像/指标；补完研发后重新冻结选择，再统一终测。后续阶段按原有预算阶梯重新决定可完成规模。\n
GPU0已有其他任务，依据用户先前空闲卡授权，将实验允许设备切为GPU1 UUID GPU-c6683db1-d2aa-97b9-c1b4-e497bd7ff0c5，PCI00000000:25:00.0。已用同一开发smoke真实渲染验证映射；仍逐次检查占用、只用一张GPU、忙时CPU、相同质量、CPU两线程。先前GPU0记录保留，混合设备耗时不用于算法速度比较。\n''')
write_json(HERE/'recovery_prepared.json',{'time':time.time(),'reason':'explicit_user_reported_quota_restoration_and_requested_completion','failed_scene_attempts_preserved':len(affected),'physical_scene_attempts_preserved':24,'candidate_proposals_reopened':proposals,'valid_test_outputs_before_recovery':0,'moves':moves,'new_attempts_per_quota_affected_slot':1,'max_total_cli':600})
write_json(ROOT/'state.json',{'phase':'quota_restored_resume_prepared','time':time.time(),'no_active_scene_process':True})
write_json(ROOT/'ledger.json',current())
print({'status':'prepared','scene_slots':len(affected),'proposal_retries':len(proposals),'remaining_cli':600-current()['cli_sessions']})
