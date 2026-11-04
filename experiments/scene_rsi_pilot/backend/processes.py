import os
import signal
import subprocess


def cpu_environment(cuda_visible=''):
    environment = os.environ.copy()
    environment['CUDA_VISIBLE_DEVICES'] = cuda_visible
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
        environment[key] = '2'
    return environment


def stop_project_tree(process):
    # Nested Codex CLI calls may start their own sessions. Enumerate only descendants
    # of the process we created before signalling any of them.
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


def run_group(command, *, timeout, **kwargs):
    with subprocess.Popen(command, start_new_session=True, **kwargs) as process:
        try:
            process.communicate(timeout=timeout)
        except BaseException:
            stop_project_tree(process)
            process.wait()
            raise
        finally:
            # Only the newly created project process group is ever signalled.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return process.returncode
