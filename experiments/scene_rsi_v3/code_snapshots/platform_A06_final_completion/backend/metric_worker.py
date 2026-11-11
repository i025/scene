"""Keep the existing LPIPS/DINO metric models resident in one owned process."""

import argparse
import atexit
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import threading
import time
import traceback

from processes import cpu_environment, stop_project_tree


class ResidentMetrics:
    """Serial JSONL client; the worker owns its models until close()."""

    def __init__(self, config_path, log_dir, gpu_uuid):
        self.config_path = Path(config_path).resolve()
        self.log_dir = Path(log_dir).resolve()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.gpu_uuid = gpu_uuid or ''
        config = json.loads(self.config_path.read_text())
        self.stderr_path = self.log_dir / 'resident_metrics_stderr.log'
        self.journal_path = self.log_dir / 'resident_metrics.jsonl'
        self._lock = threading.Lock()
        self._buffer = b''
        self._sequence = 0
        self._closed = False
        self._failed = False
        self._stderr = self.stderr_path.open('a', buffering=1)
        self.process = subprocess.Popen(
            [sys.executable, '-u', str(Path(__file__).resolve()), '--serve',
             '--config', str(self.config_path)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._stderr,
            cwd=Path(__file__).resolve().parent,
            env=cpu_environment(threads=config['resources']['threads_per_metric'], cuda_visible=self.gpu_uuid), start_new_session=True,
            bufsize=0,
        )
        self.pid = self.process.pid
        self._record('launch', config=str(self.config_path), gpu_uuid=self.gpu_uuid)
        try:
            ready = self._read_response(60)
            if ready.get('event') != 'ready' or ready.get('pid') != self.pid:
                raise RuntimeError(f'Invalid metric worker ready response: {ready}')
            self._record('ready', response=ready)
        except BaseException:
            self.close()
            raise

    def _record(self, event, **values):
        record = {'time': datetime.now(timezone.utc).isoformat(), 'event': event,
                  'pid': self.pid, **values}
        with self.journal_path.open('a') as stream:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')

    def _read_response(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            if b'\n' in self._buffer:
                line, self._buffer = self._buffer.split(b'\n', 1)
                return json.loads(line.decode('utf-8'))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f'Metric worker timed out after {timeout}s; {self.stderr_path}')
            ready, _, _ = select.select([self.process.stdout], [], [], remaining)
            if not ready:
                raise TimeoutError(f'Metric worker timed out after {timeout}s; {self.stderr_path}')
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError(f'Metric worker closed stdout (exit {self.process.poll()}); '
                                   f'{self.stderr_path}')
            self._buffer += chunk

    def request(self, op, reference, output_dir=None, timeout=600):
        if op not in ('check_models', 'score'):
            raise ValueError(f'Unknown metric operation: {op}')
        if op == 'score' and output_dir is None:
            raise ValueError('score requires output_dir')
        if timeout <= 0:
            raise ValueError('timeout must be positive')
        with self._lock:
            if self._closed or self._failed:
                raise RuntimeError('Metric worker is closed or has a failed request')
            self._sequence += 1
            request = {'id': self._sequence, 'op': op,
                       'reference': str(Path(reference).resolve())}
            if output_dir is not None:
                request['output_dir'] = str(Path(output_dir).resolve())
            started = time.monotonic()
            self._record('request', request=request)
            try:
                self.process.stdin.write((json.dumps(request) + '\n').encode('utf-8'))
                self.process.stdin.flush()
                response = self._read_response(timeout)
                self._record('response', seconds=time.monotonic() - started, response=response)
                if response.get('id') != request['id']:
                    raise RuntimeError(f'Metric response ID mismatch: {response}')
                if not response.get('ok'):
                    raise RuntimeError(f'Metric worker {response.get("error_type")}: '
                                       f'{response.get("error")}; {self.stderr_path}')
                return response['result']
            except BaseException as error:
                self._failed = True
                self._record('error', seconds=time.monotonic() - started,
                             error_type=type(error).__name__, error=str(error))
                raise

    def close(self):
        if self._closed:
            return
        self._closed = True
        started = time.monotonic()
        try:
            if self.process.poll() is None:
                # Includes this worker's CPU-only Blender validation children.
                stop_project_tree(self.process)
            self.process.wait(timeout=30)
        finally:
            for stream in (self.process.stdin, self.process.stdout, self._stderr):
                if stream is not None:
                    stream.close()
            self._record('close', seconds=time.monotonic() - started,
                         returncode=self.process.poll())


_worker = None


def current_worker():
    return _worker


def start_worker(config_path, log_dir, gpu_uuid):
    global _worker
    if _worker is not None:
        if (_worker.config_path != Path(config_path).resolve()
                or _worker.gpu_uuid != (gpu_uuid or '')):
            raise RuntimeError('A metric worker is already bound to another config/GPU')
        if _worker._closed or _worker.process.poll() is not None:
            raise RuntimeError('The existing metric worker has stopped')
        return _worker
    _worker = ResidentMetrics(config_path, log_dir, gpu_uuid)
    return _worker


def close_worker():
    global _worker
    if _worker is not None:
        try:
            _worker.close()
        finally:
            _worker = None


def serve(config_path):
    # Keep a private protocol fd, then redirect even native/library stdout to stderr.
    protocol = os.fdopen(os.dup(sys.stdout.fileno()), 'w', buffering=1)
    sys.stdout.flush()
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    from data import load_config, write_json
    from evaluate import check_models, score
    config = load_config(config_path)
    protocol.write(json.dumps({'event': 'ready', 'pid': os.getpid(),
                               'device': config['metrics']['device'],
                               'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES', '')}) + '\n')
    for line in sys.stdin:
        started = time.monotonic()
        request = {}
        try:
            request = json.loads(line)
            if request['op'] == 'check_models':
                result = check_models(request['reference'], config)
            elif request['op'] == 'score':
                result = score(request['reference'], request['output_dir'], config)
                write_json(Path(request['output_dir']) / 'image_metrics.json', result)
            else:
                raise ValueError(f'Unknown metric operation: {request["op"]}')
            response = {'id': request['id'], 'ok': True, 'result': result}
        except Exception as error:
            traceback.print_exc(file=sys.stderr)
            response = {'id': request.get('id'), 'ok': False,
                        'error_type': type(error).__name__, 'error': str(error)}
        response['seconds'] = time.monotonic() - started
        protocol.write(json.dumps(response, ensure_ascii=False, allow_nan=False) + '\n')
    protocol.close()


atexit.register(close_worker)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true', required=True)
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    serve(args.config)
