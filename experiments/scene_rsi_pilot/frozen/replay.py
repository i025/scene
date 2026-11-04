"""Budget-gated frozen-M replay, gated by a real used descendant and new reserved scenes."""
from pathlib import Path
import json
import time
import pilot
from pilot import ROOT,read,write_json,current,run_scene,propose,summarize,better


def main():
    existing=read(ROOT/'replay_status.json',{})
    if existing.get('status')=='complete':return
    if not (ROOT/'selection_freeze.json').exists():raise RuntimeError('Main selection must be frozen first')
    desc=None
    for rid in ['r1','r2']:
        proposal=read(ROOT/'candidates'/rid/'scene_rsi_pilot'/'C1'/'proposal_result.json',{})
        invocation=read(ROOT/'candidates'/rid/'scene_rsi_pilot'/'C2'/'meta_execution.json',{})
        candidate=ROOT/'candidates'/rid/'scene_rsi_pilot'/'C1'/'meta.py'
        subsequent=next((a for a in read(ROOT/'archive.json',[]) if a['method']=='scene_rsi_pilot' and a['run_id']==rid and a['candidate_id']=='C2'),{})
        if proposal.get('M_strategy_structure_changed') and invocation.get('source')==str(candidate) and subsequent.get('development',{}).get('completed',0)>0:
            desc=candidate;break
    if desc is None:
        write_json(ROOT/'replay_status.json',{'status':'pending_no_executed_strategy_descendant','message':'本轮未获得可用元策略后代；只有提示字符串变化也不算结构策略后代。','entrypoint':'bash run.sh resume'});return
    starts=[];archive=read(ROOT/'archive.json',[])
    for method in ['sceneevolve_cli','generic_rsi']:
        entry=next((a for a in archive if a['method']==method and a['run_id']=='r2' and a['candidate_id']=='C1'),{})
        source=ROOT/'candidates'/'r2'/method/'C1'
        if entry.get('development',{}).get('completed',0)>0:starts.append(source)
    if not starts:
        write_json(ROOT/'replay_status.json',{'status':'pending_no_qualified_unfamiliar_start','message':'没有已执行成功、未出现在Ours显式研发档案中的预保留异方法H起点。'});return
    available=600-current()['cli_sessions']
    if available<49:
        write_json(ROOT/'replay_status.json',{'status':'pending_budget','required_cli_upper_bound':49,'remaining_cli':available,'scope':'smallest feasibility replay: one unfamiliar H, one proposal per frozen M, 1dev/1selection/1newtest'});return
    # Prefer two distinct source programs and two independent proposals per M/start.
    unique=[]
    for source in starts:
        if not any(all((source/name).read_text()==(other/name).read_text() for name in ['policy.py','system.txt']) for other in unique):unique.append(source)
    existing_protocol=read(ROOT/'replay_protocol.json')
    full=(existing_protocol['scope']=='two_starts_two_repeats') if existing_protocol else available>=166 and len(unique)>=2
    starts=unique[:2] if full else unique[:1];repeats=2 if full else 1
    initial=ROOT/'initial_meta/scene_rsi_pilot/meta.py';reserved=[s for s in read(ROOT/'manifest.json') if s['split']=='reserved']
    if len(reserved)<3*len(starts):raise RuntimeError('Need three reserved scene groups per foreign start')
    specifications=[]
    for index,source in enumerate(starts,1):
        scenes=[{**s,'split':split} for s,split in zip(reserved[3*(index-1):3*index],['replay_development','replay_selection','replay_test'])]
        specifications.append({'start_id':f's{index}','H_start':str(source),'scenes':scenes})
    scope='two_starts_two_repeats' if full else 'feasibility_only_one_start_one_proposal_per_M'
    protocol={'scope':scope,'M_initial':str(initial),'M_descendant':str(desc),'starts':specifications,'proposal_repeats':repeats,'K':1,'meta_frozen':True,'explicit_memory':'Both receive only the same H_start development trajectory and source. No external historical archive. Learned rules inside frozen M source remain part of M.','main_test_reused':False,'historical_exposure':'exploratory source images were historically screened','budget_upper_cli':166 if full else 49,'generation_condition_label':'Both proposers see the same neutral frozen_meta method label; treatment IDs are only in report mappings.','time':time.time()}
    if not existing_protocol:write_json(ROOT/'replay_protocol.json',protocol)
    choices=[];bases={};original_common=pilot.COMMON
    pilot.COMMON += '\nFROZEN META REPLAY: meta.py is immutable in this stage. Do not return a change to meta.py. Only shared policy.py/system.txt may change. This is K=1 and there is no future M modification. Both frozen M versions start from the identical unfamiliar H and explicit development evidence.'
    try:
        for specification in specifications:
            sid=specification['start_id'];source=Path(specification['H_start']);scenes=specification['scenes'];base_run='replay_'+sid
            base_dev=run_scene('H_start',base_run,'H_start',scenes[0],source)
            base_sel=run_scene('H_start',base_run,'H_start',scenes[1],source)
            bases[sid]={'selection':base_sel,'source':source,'test_scene':scenes[2]}
            for repetition in range(1,repeats+1):
                run=f'replay_{sid}_r{repetition}'
                for label,meta in [('M_initial',initial),('M_descendant',desc)]:
                    # Neutral label in model input; separate paths preserve independent calls.
                    candidate,result=propose('frozen_meta',run+'_'+label,1,source,meta,[base_dev],[],total_candidates=1)
                    write_json(candidate/'mapping_for_report.json',{'method':label,'run_id':run,'start_id':sid})
                    valid=result['status']=='proposed' and (candidate/'meta.py').read_text()==meta.read_text()
                    chosen=source;cid='H_start';summary=None
                    if valid:
                        run_scene(label,run,'C1',scenes[0],candidate,meta=str(meta))
                        selection=run_scene(label,run,'C1',scenes[1],candidate,meta=str(meta));summary=summarize([selection])
                        if better(summary,summarize([base_sel]),summarize([base_sel])):chosen=candidate;cid='C1'
                    choices.append({'method':label,'run_id':run,'start_id':sid,'proposal_repeat':repetition,'candidate_id':cid,'source':str(chosen),'M_source':str(meta),'proposal_folder':str(candidate),'proposal_valid_with_frozen_M':valid,'selection':summary})
    finally:pilot.COMMON=original_common
    frozen=read(ROOT/'replay_selection_freeze.json')
    if frozen:
        if frozen['choices']!=choices:raise RuntimeError('Replay resume choices differ from first frozen choices')
    else:write_json(ROOT/'replay_selection_freeze.json',{'choices':choices,'time':time.time(),'test_unseen_in_this_stage':True})
    base_tests={sid:run_scene('H_start','replay_'+sid,'H_start',base['test_scene'],base['source']) for sid,base in bases.items()}
    results=[]
    for choice in choices:
        base_test=base_tests[choice['start_id']];scene=bases[choice['start_id']]['test_scene']
        result=base_test if choice['candidate_id']=='H_start' else run_scene(choice['method'],choice['run_id'],choice['candidate_id'],scene,Path(choice['source']),meta=choice['M_source'])
        valid=result['metrics']['valid'] and base_test['metrics']['valid']
        results.append({**choice,'test_result_record':result,'baseline_test_record':base_test,'reused_H_start':choice['candidate_id']=='H_start','paired_valid':valid,'gain_over_same_H_start':result['metrics']['overall']-base_test['metrics']['overall'] if valid else None,'functional_non_degradation':int(result['functional']['functional_pass'])>=int(base_test['functional']['functional_pass'])})
    write_json(ROOT/'replay_status.json',{'status':'complete','scope':scope,'interpretation':'All points and paired differences only; this is not evidence of general monotonic meta-capability improvement.','results':results,'base_tests':base_tests,'remaining_cli':600-current()['cli_sessions']})

if __name__=='__main__':main()
