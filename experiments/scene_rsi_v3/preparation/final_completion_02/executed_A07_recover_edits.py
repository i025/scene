"""A07: replay the four saved, validated editor programs; no model calls."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'backend')]
from semantic_edit import validate_editor_code, write_json
from processes import run_measured, cpu_environment


def run():
    config = json.loads((ROOT / 'config.json').read_text())
    os.sched_setaffinity(0, set(config['resources']['cpu_affinity']))
    with (ROOT / 'experiment.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        freeze = (ROOT / 'final_selection_freeze.json').read_text()
        outcomes = []
        for scene in config['pilot']['semantic_edit_subset']:
            for version in ['historical_r1_C2_start', 'H04']:
                folder = ROOT / 'semantic_edits' / version / scene
                old = json.loads((folder / 'status.json').read_text())
                if 'execution_recovery_A07' in old:
                    if old['status'] not in {'completed', 'failed', 'timeout'}:
                        raise RuntimeError('Interrupted A07 execution requires explicit review: ' + str(folder))
                    outcomes.append(old)
                    continue
                if old['status'] != 'failed' or old['failure_type'] != 'editor_blender_failure':
                    raise ValueError('A07 is only for the four observed platform import failures')
                if "ModuleNotFoundError: No module named 'yaml'" not in (folder / 'stderr.log').read_text():
                    raise ValueError('Different failure; do not silently grant another execution')
                validate_editor_code((folder / 'edit.py').read_text())
                output = folder / 'execution_recovery_A07'
                output.mkdir(exist_ok=False)
                shutil.copy2(folder / 'status.json', output / 'before_status.json')
                for name in ['edit.py', 'targets.json', 'settings.json']:
                    shutil.copy2(folder / name, output / name)
                current = {**old, 'status': 'running', 'checks': None,
                           'artifact_subdirectory': output.name,
                           'execution_recovery_A07': {'original_status': 'failed',
                               'original_status_path': str(output / 'before_status.json'),
                               'new_model_calls': 0, 'editor_program_changed': False,
                               'new_targets_selected': False, 'started': time.time()}}
                write_json(folder / 'status.json', current)
                blend = ROOT / 'results' / version / 'development' / scene / '1/scene.blend'
                command = [config['blender']['executable'], '--background', '--disable-autoexec',
                           '--threads', str(config['resources']['threads_per_blender']),
                           '--python-exit-code', '1', '--python', str(ROOT / 'semantic_edit.py'),
                           '--', '--worker', '--blend', str(blend), '--output', str(output)]
                with (output / 'stdout.log').open('w') as stdout, (output / 'stderr.log').open('w') as stderr:
                    process = run_measured(command, timeout=config['blender']['timeout'],
                        measurement_path=output / 'process.json', stdout=stdout, stderr=stderr,
                        memory_limit_bytes=int(config['resources']['memory_limit_gb'] * 1024 ** 3),
                        env=cpu_environment(threads=config['resources']['threads_per_blender']))
                current.update(status='completed' if process['returncode'] == 0 else 'timeout' if process['timed_out'] else 'failed',
                               blender_executions=old['blender_executions'] + 1,
                               seconds=old['seconds'] + process['seconds'], finished=time.time(),
                               duration_scope='Cumulative original and recovery active wall; intervening wait excluded',
                               failure_type=None if process['returncode'] == 0 else 'editor_recovery_execution_failure',
                               process=process)
                current['execution_recovery_A07'].update(finished=time.time(), process_seconds=process['seconds'])
                if process['returncode'] == 0:
                    current['checks'] = json.loads((output / 'text_edit.json').read_text())
                write_json(output / 'status.json', current)
                write_json(folder / 'status.json', current)
                outcomes.append(current)
                print(json.dumps({'H': version, 'scene': scene, 'status': current['status'],
                                  'mechanical_pass': current['checks']['mechanical_pass'] if current['checks'] else None}), flush=True)
        if freeze != (ROOT / 'final_selection_freeze.json').read_text():
            raise RuntimeError('Selection freeze changed during deterministic recovery')
        write_json(ROOT / 'A07_EDIT_RECOVERY.json', {'time': time.time(), 'amendment': 'A07',
            'scheduled': 4, 'terminal': len(outcomes), 'new_model_calls': 0,
            'new_research_rounds': 0, 'H_M_and_Test_scores_changed': False,
            'execution_completed': sum(row['status'] == 'completed' for row in outcomes),
            'mechanical_pass': sum(row['checks'] is not None and row['checks']['mechanical_pass'] for row in outcomes),
            'semantic_target_correctness': None})


if __name__ == '__main__':
    run()
