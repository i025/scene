"""Explicit one-shot connectivity recovery; keep failed experimental outcomes."""
import shutil
import subprocess
import time

from pilot import ROOT, call, config, current, read, write_json


def main():
    marker = ROOT / 'service_pause.json'
    if not marker.exists():
        return
    folder = ROOT / 'service_incident_03/connection_check_001'
    if (folder / 'request.json').exists():
        raise SystemExit('The single connection check for this incident has already been used. Inspect its logs; no repeated recovery submissions.')
    if (ROOT / 'model_usage_limit.json').exists():
        raise SystemExit('The recorded CLI quota limit still blocks model calls.')
    if current()['cli_sessions'] >= 600:
        raise SystemExit('The 600-session budget is exhausted.')
    folder.mkdir(parents=True, exist_ok=True)
    pause = read(marker)
    shutil.copy2(marker, folder / 'pause_before_check.json')
    write_json(folder / 'recovery_policy.json', {
        'time': time.time(), 'explicit_command': 'resume-service',
        'maximum_connection_checks': 1, 'failed_experiment_resampling': False,
        'remaining_tasks_only': True, 'max_cli_sessions': 600,
    })
    marker.unlink()
    try:
        response, session = call('Connectivity check only. Reply READY.', config()['model'],
                                 folder, role='service_connectivity_check', timeout=120)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        if not marker.exists():
            write_json(marker, pause)
        raise
    write_json(folder / 'recovered.json', {'time': time.time(), 'exit_code': session['exit_code'],
               'response': response, 'actual_model_routing': session['actual_model'],
               'note': 'Connection succeeded; failed experimental records remain unchanged.'})


if __name__ == '__main__':
    main()
