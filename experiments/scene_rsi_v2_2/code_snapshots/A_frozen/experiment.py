"""Fixed-version repeat experiment; no H/M evolution is run in V2.2."""
from pathlib import Path
import argparse
import json
import time
import pilot

ROOT = Path(__file__).resolve().parent


def smoke():
    scene = json.loads((ROOT.parent/'scene_rsi_v2_1/manifest.json').read_text())[0]
    scene = {**scene, 'split': 'smoke', 'scene_id': 'old_dev_excluded_smoke'}
    row = pilot.run_scene('fixed_h', 'smoke', 'r1_C2', scene, ROOT/'fixed_h/r1_C2')
    pilot.write_json(ROOT/'configs/smoke_cost.json', {
        'scene': scene, 'record': row, 'ledger': pilot.current(),
        'used_for_H_changes': False, 'A_scene_overlap': False})


def freeze_a():
    assert not (ROOT/'configs/A_freeze.json').exists()
    candidates = pilot.read(ROOT/'data/preparation_candidates.json')
    selection = [(0, 'portable_classroom'), (1, 'goa_classroom'), (3, 'longfellow_bedroom'),
                 (5, 'modern_kitchen'), (6, 'riverdale_reading_room'), (8, 'hc_restaurant')]
    scenes = []
    for order, (index, group) in enumerate(selection):
        row = candidates[index]
        image = Path(row['image_path']).resolve()
        scenes.append({**row, 'image_path': str(image), 'group_id': group, 'order': order,
                       'split': 'fixed_version_test', 'expected_composite': order in [1,2,3,5],
                       'expected_min_meshes': 1,
                       'historical_exposure': 'New page IDs absent from prior collection manifest; engineer eligibility contact sheet viewed before A; no reconstruction-driven selection',
                       'group_basis': 'Distinct named source locations; one view per location',
                       'applicability_basis': 'Structure and material required for all. Composite/declared-parts additionally required for furnished classroom, bedroom, kitchen, restaurant.'})
    pilot.write_json(ROOT/'manifest.json', scenes)
    schedule = []
    for rep in [1,2]:
        for scene in scenes:
            versions = ['H0','r1_C2'] if (scene['order']+rep)%2 else ['r1_C2','H0']
            for version in versions:
                schedule.append({'job_id': f"A_r{rep}_{scene['scene_id']}_{version}",
                                 'run_id': f'r{rep}', 'candidate_id': version,
                                 'scene_id': scene['scene_id'], 'status': 'not_started'})
    pilot.write_json(ROOT/'configs/A_schedule.json',schedule)
    cfg = pilot.config()
    cfg['pilot'].update(status='A_frozen', repeats=2, scheduled_main_reconstructions=24,
                        data_exposure='New source pages relative to prior H development; current eligibility selection documented; not strictly blinded')
    pilot.write_json(ROOT/'config.json',cfg)
    prior = pilot.read(ROOT/'configs/smoke_cost.json')
    freeze = {'frozen_utc_epoch':time.time(), 'H_versions':['fixed_h/H0','fixed_h/r1_C2'],
              'H_source':pilot.read(ROOT/'configs/source_versions.json'), 'n_scenes':6,'repetitions':2,
              'scheduled_reconstructions':24,'configuration':'config.json',
              'CLI_upper_forecast': {'smoke_measured':prior['ledger']['cli_sessions'], 'A':72,
                                     'C_common_localization':10,'C_repairs':20,'extra_reserve':20,
                                     'total_upper':125,'cap':180},
              'frame_upper_forecast':360,'frame_cap':600,
              'wall_forecast':'A generation at most 24*600s = 4h, plus CPU metrics/mechanical measurements; single heavy job; no unallocated GPU',
              'remote_sampling_seed':None, 'failure_raw_metrics':None,'failure_utility':0,
              'quality':'V2.1 Q: (clip(SSIM,0,1)+1-clip(LPIPS,0,1)+(1+clip(DINO,-1,1))/2)/3',
              'pairing':'scene_id and repetition; Q difference only both valid',
              'H_change_allowed':False,'M_search':False,
              'telemetry':'Common timestamp instrumentation only; actual SceneAct Boolean starts/completions, mesh sizes, build/render stages; retained modifiers are not executed operations'}
    pilot.write_json(ROOT/'configs/A_freeze.json',freeze)
    (ROOT/'protocol_A.md').write_text('''# V2.2 实验 A：执行前冻结协议

固定原始 H0 与 V2.1 r1/C2，不运行候选搜索，不从新图像修改 H/M。
6 个独立来源场景 × 2 次重复 × 2 个 H，共 24 次；按场景和重复交错 H 顺序。
来源与人工适用性检查见 manifest.json；新页面 ID 不在旧收集清单，本轮接触检查已公开记录，不宣称严格盲测。
模型 gpt-6.1-sol medium，真实图片附件；每任务最多 3 CLI 会话、2 次 Blender 执行、600 秒内层时间。
固定 CPU Cycles、2 线程、16 samples、512 长边、seed42、AgX；远端模型采样不可固定。
共同 V2.1 SceneAct 和外部 Q/功能门槛。V2.2 仅增加共同阶段/几何观测日志，不改两个 H 的算法。
分别报告全部预定分母、已完成、执行成功、必需功能合规、成功条件 Q、双方成功配对 Q 和独立失败零效用。
必需检查缺测不能通过；原始视觉缺测为 null。几何未知和机械编辑边界沿用 V2.1。
H0 始终是内部参照；A 无 Selection，不重新选择 H。不将固定 H 的收益归因于诊断或 RSI 搜索优越性。
完整预算和时间上界见 configs/A_freeze.json；不会按胜负扩大样本或调用上限。
''')


def experiment_a():
    freeze = pilot.read(ROOT/'configs/A_freeze.json')
    assert freeze['scheduled_reconstructions']==24
    scenes = {s['scene_id']:s for s in pilot.read(ROOT/'manifest.json')}
    schedule = pilot.read(ROOT/'configs/A_schedule.json')
    for job in schedule:
        if job['status'] in ['completed','failed','timeout','invalid']:
            continue
        job.update(status='running',started=time.time())
        pilot.write_json(ROOT/'configs/A_schedule.json',schedule)
        row = pilot.run_scene('fixed_h',job['run_id'],job['candidate_id'],scenes[job['scene_id']],ROOT/'fixed_h'/job['candidate_id'])
        job.update(status='completed' if row['metrics']['valid'] else 'failed',finished=time.time(),record=str(Path(row['folder'])/'record.json'))
        pilot.write_json(ROOT/'configs/A_schedule.json',schedule)
    pilot.write_json(ROOT/'state.json',{'phase':'A_completed','jobs':len(schedule),'time':time.time(),'ledger':pilot.current()})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['smoke','freeze-a','experiment-a','resume'])
    action=parser.parse_args().action
    {'smoke':smoke,'freeze-a':freeze_a,'experiment-a':experiment_a,'resume':experiment_a}[action]()
