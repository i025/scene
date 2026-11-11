"""One bounded post-test batch: reports, missing old assets, then two update bundles."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from finalize import WORK, PROJECT, read, write, run, wait_launch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch', type=Path, required=True)
    parser.add_argument('--status-dir', type=Path, default=WORK / 'final_completion_pipeline')
    args = parser.parse_args()
    lock = (WORK / 'finish_after_test.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.sched_setaffinity(0, set(range(8)))
    source, repo = PROJECT / 'outputs/scene_rsi_v3', PROJECT / 'archive/scene'
    folder = args.status_dir.resolve()
    folder.mkdir(exist_ok=False)
    receipt = {'status': 'waiting_test', 'started': time.time(), 'pid': os.getpid(),
               'launch': str(args.launch), 'new_research_rounds': 0,
               'new_model_calls': 0, 'new_Blender_jobs': 0,
               'base_snapshot': 'S20261111T034024Z',
               'immutable_reused_groups': ['baseline'] + [f'round{t:02d}' for t in range(1, 11)],
               'new_groups': ['preparation', 'final']}
    def stage(status, **values):
        receipt.update(status=status, **values);write(folder / 'status.json', receipt)
    stage('waiting_test')
    try:
        launch = wait_launch(args.launch.resolve(), source, True, 36)
        stage('offline_reports', experiment_launch=launch)
        for name, command in [
            ('M07_review', [sys.executable, str(source / 'audit_m07.py')]),
            ('final_statistics', [sys.executable, str(source / 'final_statistics.py'),
                                  '--private-output', str(WORK / 'private_final_test_contact_sheet.png')]),
            ('report', [sys.executable, str(source / 'analyze.py'), 'report'])]:
            if run(command, folder, name) != 0:raise RuntimeError(name + ' failed; original records unchanged')
        stage('complete_missing_base_assets')
        base_state = Path('docs/V3_RELEASE_UPLOAD_STATE_S20261111T034024Z.json')
        base_command = [sys.executable, str(WORK / 'publish.py'), 'release', '--repo', str(repo),
                        '--auth', 'bashrc', '--tag', 'scene-rsi-v3-10rounds-S20261111T034024Z',
                        '--bundles', str(WORK / 'bundles/S20261111T034024Z'), '--state', str(base_state)]
        if run(base_command, folder, 'missing_base_assets', timeout=7200) != 0:
            raise RuntimeError('Base asset upload incomplete; no repeated upload loop was started')
        base = read(repo / base_state)
        if len(base['assets']) != 13 or base['remote_asset_listing_verified'] is not True:
            raise RuntimeError('All 13 old packages require actual upload/listing receipts')
        snapshot = datetime.now(timezone.utc).strftime('S%Y%m%dT%H%M%SZ_final')
        stage('final_delta_archive', base_release=base['release_url'], snapshot_id=snapshot)
        command = [sys.executable, str(WORK / 'finalize.py'), '--launch', str(args.launch.resolve()),
                   '--snapshot-id', snapshot, '--publish', '--auth', 'bashrc',
                   '--base-release-state', str(base_state), '--delta-groups', 'preparation', 'final']
        code = run(command, folder, 'final_delta_archive', timeout=14400)
        final = read(WORK / 'finalizations' / snapshot / 'FINALIZATION.json')
        stage('completed' if code == 0 else 'archive_failed_or_partial', finalization=final,
              finished=time.time())
        return code
    finally:
        error = sys.exc_info()[1]
        if error is not None:
            stage('interrupted_or_failed', failed_stage=receipt['status'],
                  error_type=type(error).__name__, error=str(error), finished=time.time())


if __name__ == '__main__':
    for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        os.environ[key] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    raise SystemExit(main())
