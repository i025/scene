"""Record explicit network recovery and immutable post-ten-round selection."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]/'outputs/scene_rsi_v3'


def read(path):
    return json.loads(path.read_text())


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    folder=ROOT/'preparation/service_recovery_01'
    snapshot=ROOT/'code_snapshots/platform_A05_postten_resume'
    assert not snapshot.exists() and not (ROOT/'configs/amendment_05.json').exists()
    assert read(ROOT/'launches/005_resume.json')['status']=='failed'
    assert len(list((ROOT/'rounds').glob('*/record.json')))==10
    assert read(folder/'freeze_resume_tests.json')['status']=='passed'
    assert (ROOT/'final_selection_freeze.json').read_bytes()==(folder/'final_selection_freeze.json').read_bytes()
    assert (ROOT/'test_repeat_plan.json').read_bytes()==(folder/'test_repeat_plan.json').read_bytes()
    failed=ROOT/'results/H04/test/bw_0016/1'
    assert (failed/'status.json').exists() and not (failed/'scene.blend').exists()
    config=read(ROOT/'config.json')
    config['pilot']['postfreeze_resume_snapshot']='code_snapshots/platform_A05_postten_resume'
    write(ROOT/'config.json',config)
    original=read(ROOT/'service_pause.json')
    (ROOT/'service_pause.json').rename(folder/'cleared_service_pause_marker.json')
    snapshot.mkdir()
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in {'.py','.md'}:shutil.copy2(path,snapshot/path.name)
    for name in ['backend','initial_m','fixed_h']:
        shutil.copytree(ROOT/name,snapshot/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['config.json','manifest.json','final_selection_freeze.json','test_repeat_plan.json']:
        shutil.copy2(ROOT/name,snapshot/name)
    row={'time_utc':datetime.now(timezone.utc).isoformat(),'scope':'post-ten-round resume only',
         'snapshot':str(snapshot.relative_to(ROOT)),'protocol':'PROTOCOL_AMENDMENT_05.md',
         'original_service_pause':original,'recovery':read(folder/'RECOVERY_EVIDENCE.json'),
         'tests':read(folder/'freeze_resume_tests.json'),'H_M_changed':False,
         'original_final_freeze_preserved':True,'failed_task_resampled':False,
         'models_resources_evaluator_budgets_changed':False,'new_model_probe_calls':0,
         'previous_partial_local_commits':['f9025880c9dfd8bc0cd26e130d7e1702ec1ff204','5efa87be6ffe81bb2149078a67518b0df2846fc2']}
    write(snapshot/'PLATFORM_SNAPSHOT.json',row);write(ROOT/'configs/amendment_05.json',row)
    state=read(ROOT/'state.json');state.update(phase='network_recovered_resume_ready',postfreeze_resume_snapshot=config['pilot']['postfreeze_resume_snapshot'])
    write(ROOT/'state.json',state)
    print(json.dumps({'status':'recovery_recorded','H_best':state['H_best'],'M_final':state['M_retained'],
                      'failed_task_retained':str(failed.relative_to(ROOT)),'first_freeze_time':read(ROOT/'final_selection_freeze.json')['time']}))


if __name__=='__main__':main()
