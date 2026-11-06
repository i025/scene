"""Freeze only after A and the real deterministic checks have finished."""
from pathlib import Path
import json
import time
import sys
import pilot

ROOT=Path(__file__).resolve().parent
assert pilot.read(ROOT/'state.json')['phase']=='A_completed'
assert pilot.read(ROOT/'tests/diagnostic_contracts.json')['status']=='passed'
assert pilot.read(ROOT/'tests/report_contracts.json')['status']=='passed'
assert len(pilot.read(ROOT/'tests/calibration.json'))==8
probe=pilot.read(ROOT/'tests/target_probe_64/probe.json')
assert probe['status']=='completed' and probe['target_selection']['object']=='Z_fault_target'
assert probe['non_target_preserved'] is True
assert not (ROOT/'configs/BC_freeze.json').exists()
assert not list((ROOT/'diagnosis').glob('case*'))
cost=pilot.current();assert cost['cli_sessions']+30<=180
pilot.write_json(ROOT/'configs/BC_freeze.json',{'time':time.time(),'protocol':'protocol_BC.md',
    'engineering_M':'initial_meta/scene_rsi_v2_2/meta.py','control_M':'code_snapshots/v2_1_initial_meta/scene_rsi_v2_1/meta.py',
    'auto_evolved_M':False,'tasks':10,'arms':2,'max_probes_per_case_per_arm':2,
    'max_regressions_per_case_per_arm':3,'coding_calls_per_arm':1,'C_CLI_upper':30,
    'global_CLI_cap':180,'global_frame_cap':600,'ledger_at_freeze':cost,
    'schedule':[{'scene_id':f'case{i:02d}','method':m,'status':'not_started'} for i in range(1,11) for m in ['v2_1_fixed','v2_2_evidence']],
    'quality_direction_tolerance':.005,'API_contract_hints_disclosed':True,
    'fixtures_created_after_M_frozen':True,'truth_evaluator_only':True})
print('BC_FROZEN_BEFORE_ANY_DIAGNOSIS_MODEL_CALL')
