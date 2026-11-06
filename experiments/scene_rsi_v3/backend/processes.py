"""Bounded experiment-owned processes and observable process-tree resources."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time



def cpu_environment(*, threads, cuda_visible=''):
    environment = os.environ.copy()
    environment['CUDA_VISIBLE_DEVICES'] = cuda_visible
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
        environment[key] = str(threads)
    environment['SCENE_RSI_NUM_THREADS'] = str(threads)
    return environment


def stop_project_tree(process):
    # Only descendants of the process created by this experiment are signalled.
    rows = subprocess.check_output(['ps', '-eo', 'pid=,ppid='], text=True)
    parents = [tuple(map(int, row.split())) for row in rows.splitlines()]
    descendants = [process.pid]
    for parent in descendants:
        descendants.extend(pid for pid, ppid in parents if ppid == parent and pid not in descendants)
    for pid in reversed(descendants):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_measured(command, *, timeout, measurement_path, memory_limit_bytes=None, **kwargs):
    """GNU time supplies waited-tree CPU; sample summed live-tree RSS every 0.1s.

    The sampled RSS maximum is a lower bound on the exact simultaneous peak.
    GNU time maxrss is the largest individual waited process, not their RSS sum.
    """
    import psutil
    measurement_path = Path(measurement_path)
    measurement_path.parent.mkdir(parents=True, exist_ok=True)
    usage_path = measurement_path.with_suffix('.time.txt')
    wrapped = ['/usr/bin/time', '-o', str(usage_path), '-f', '%U %S %M %x', '--', *command]
    started_wall, started = time.time(), time.monotonic()
    maximum_tree_rss = 0
    sampled_pids = set()
    timed_out = False
    memory_limit_exceeded = False
    with subprocess.Popen(wrapped, start_new_session=True, **kwargs) as process:
        measurement_path.write_text(json.dumps({'status':'running','pid':process.pid,'command':command,'started':started_wall,'timeout_seconds':timeout,'memory_limit_bytes':memory_limit_bytes},indent=2)+'\n')
        root = psutil.Process(process.pid)
        while process.poll() is None:
            try:
                members = [root, *root.children(recursive=True)]
                total_rss = 0
                for member in members:
                    try:
                        total_rss += member.memory_info().rss
                        sampled_pids.add(member.pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                maximum_tree_rss = max(maximum_tree_rss, total_rss)
            except psutil.NoSuchProcess:
                pass
            if memory_limit_bytes is not None and maximum_tree_rss > memory_limit_bytes:
                memory_limit_exceeded = True
            if time.monotonic() - started >= timeout or memory_limit_exceeded:
                timed_out = not memory_limit_exceeded
                # Keep GNU time alive long enough to collect the killed child's usage.
                for child in root.children(recursive=False):
                    stop_project_tree(child)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    stop_project_tree(process)
                break
            time.sleep(0.1)
        process.wait()
        returncode = process.returncode
        # Disallow an orphan surviving a command's apparent completion.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    cpu_user = cpu_system = peak_individual_rss = None
    if usage_path.exists():
        lines = usage_path.read_text().splitlines()
        # GNU time also writes a signal/nonzero status explanation above its numeric row.
        values = lines[-1].split() if lines else []
        if len(values) == 4:
            cpu_user, cpu_system = map(float, values[:2])
            peak_individual_rss = int(values[2])
    result = {'status':'completed' if returncode==0 else 'timeout' if timed_out else 'failed','pid':process.pid,'command': command, 'started': started_wall, 'finished': time.time(),
              'seconds': time.monotonic() - started, 'returncode': returncode,
              'timed_out': timed_out, 'timeout_seconds': timeout,
              'memory_limit_exceeded': memory_limit_exceeded, 'memory_limit_bytes': memory_limit_bytes,
              'cpu_user_seconds': cpu_user, 'cpu_system_seconds': cpu_system,
              'peak_individual_rss_kib': peak_individual_rss,
              'sampled_peak_tree_rss_kib_lower_bound': maximum_tree_rss / 1024,
              'sample_interval_seconds': 0.1, 'sampled_process_count': len(sampled_pids),
              'cpu_scope': 'GNU time waited child and reaped descendants',
              'rss_scope': 'sampled simultaneous sum of experiment process tree; lower bound'}
    measurement_path.write_text(json.dumps(result, indent=2) + '\n')
    return result


def run_group(command, *, timeout, **kwargs):
    # Existing callers may opt into the same process-tree ledger without changing return type.
    measurement_path = kwargs.pop('measurement_path', None)
    if measurement_path is not None:
        result = run_measured(command, timeout=timeout, measurement_path=measurement_path, **kwargs)
        if result['timed_out']:
            raise subprocess.TimeoutExpired(command, timeout)
        return result['returncode']
    with subprocess.Popen(command, start_new_session=True, **kwargs) as process:
        try:
            process.communicate(timeout=timeout)
        except BaseException:
            stop_project_tree(process)
            process.wait()
            raise
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return process.returncode
