import json
from pathlib import Path
import shutil
import time
from PIL import Image
from data import ROOT, write_json
from llm import ImageLLM, image_message
from processes import run_measured
from devices import render_settings


class BudgetExceeded(RuntimeError):
    pass


class Runtime:
    def __init__(self, task, config, output_dir):
        self.task, self.config = task, config
        self.output_dir = Path(output_dir)
        self.deadline = time.monotonic() + config['budget']['seconds']
        self.calls, self.executions = 0, 0
        self.llm = None
        self.save_usage()

    def log(self, event):
        with (self.output_dir / 'trajectory.jsonl').open('a') as stream:
            stream.write(json.dumps({'time': time.time(), **event}, ensure_ascii=False) + '\n')

    def remaining(self):
        available_calls = self.config['budget']['model_calls'] - self.calls
        if self.executions >= self.config['budget']['executions']:
            available_calls = 0
        if self.deadline - time.monotonic() <= self.config['budget']['reserve_final_seconds']:
            available_calls = 0
        return {'model_calls': available_calls,
                'executions': self.config['budget']['executions'] - self.executions,
                'seconds': max(0, self.deadline - time.monotonic())}

    def check(self, resource):
        remaining = self.remaining()
        if remaining['seconds'] <= 0 or remaining[resource] <= 0:
            raise BudgetExceeded(f'Budget exhausted: {remaining}')

    def save_usage(self):
        usage = self.llm.usage if self.llm else {'calls': 0, 'input_tokens': None, 'output_tokens': None, 'total_tokens': None, 'seconds': 0.0}
        write_json(self.output_dir / 'usage.json', {**usage, 'calls': self.calls,
            'runtime_ask_attempts': self.calls,
            'cli_sessions': sum(path.with_name('request.json').exists() for path in
                                self.output_dir.glob('student_calls/*/session.json')),
            'executions': self.executions})

    def ask(self, messages):
        self.check('model_calls')
        self.calls += 1
        try:
            if self.llm is None:
                settings = {**self.config['model'], 'task_instruction':self.task['instruction'],
                            'threads': self.config['resources']['threads_per_metric']}
                deadline = self.deadline - self.config['budget']['reserve_final_seconds']
                self.llm = ImageLLM(settings, self.log, deadline)
            return self.llm(messages)
        finally:
            self.save_usage()

    def execute(self, code):
        """Build then render with distinct caps; each attempt consumes one execution."""
        from budget import guard
        self.check('executions')
        self.executions += 1
        self.save_usage()
        folder = self.output_dir / 'steps' / f'{self.executions:03d}'
        folder.mkdir(parents=True)
        (folder / 'build.py').write_text(code)
        settings, environment = render_settings(self.config, folder)
        environment['SCENE_RSI_TELEMETRY'] = str(folder / 'stage_events.jsonl')
        settings.update(width=self.task['width'], height=self.task['height'])
        write_json(folder / 'render_settings.json', settings)
        prefix = [self.config['blender']['executable'], '--background', '-noaudio', '--factory-startup',
                  '--disable-autoexec', '--threads', str(settings['threads']), '--python-exit-code', '1',
                  '--python', str(ROOT / 'render.py'), '--',
                  '--settings', str(folder / 'render_settings.json'), '--output-dir', str(folder)]
        self.log({'event': 'execute', 'step': self.executions, 'code': code})
        started = time.monotonic()
        error, failure_type = None, None
        measurements = {}
        for stage in ('build', 'render'):
            if stage == 'build':
                command = prefix + ['--code', str(folder / 'build.py'), '--build-only']
                available = self.remaining()['seconds'] - self.config['blender']['render_timeout']
                timeout = min(self.config['blender']['build_timeout'], available)
            else:
                command = prefix + ['--scene', str(folder / 'scene.blend')]
                timeout = min(self.config['blender']['render_timeout'], self.remaining()['seconds'])
            if timeout <= 0:
                failure_type, error = 'total_budget_exceeded', f'No {stage} budget remains'
                break
            if stage == 'render':
                guard('render')
                write_json(folder / 'render_ledger.json', {'render_attempts': 1, 'renders_completed': 0})
            self.log({'event': stage + '_started', 'step': self.executions, 'command': command,
                      'timeout': timeout, 'remaining': self.remaining()})
            with (folder / f'{stage}_stdout.log').open('w') as stdout, (folder / f'{stage}_stderr.log').open('w') as stderr:
                measured = run_measured(command, timeout=timeout, measurement_path=folder / f'{stage}_process.json',
                                        memory_limit_bytes=int(self.config['resources']['memory_limit_gb'] * 1024 ** 3),
                                        cwd=folder, stdout=stdout, stderr=stderr, env=environment)
            measurements[stage] = measured
            self.log({'event': stage + '_completed', 'step': self.executions, **measured})
            if measured['memory_limit_exceeded']:
                failure_type, error = 'resource_memory_limit', f'{stage} exceeded experiment memory limit'
                break
            if measured['timed_out']:
                failure_type = 'blender_build_timeout' if stage == 'build' else 'render_timeout'
                error = f'{stage} timed out after {timeout:.3f}s'
                break
            if measured['returncode']:
                failure_type = 'blender_build_error' if stage == 'build' else 'render_error'
                error = f'{stage} exited {measured["returncode"]}'
                if stage == 'build':
                    event_path = folder / 'stage_events.jsonl'
                    events = [json.loads(line)['stage'] for line in event_path.read_text().splitlines()] if event_path.exists() else []
                    if 'python_validation_started' in events and 'scene_build_started' not in events:
                        failure_type = 'invalid_generated_program'
                break
            if stage == 'render':
                write_json(folder / 'render_ledger.json', {'render_attempts': 1, 'renders_completed': 1})
        if error is None:
            try:
                with Image.open(folder / 'final.png') as image:
                    image.load()
                    if image.size != (self.task['width'], self.task['height']):
                        raise ValueError('Render dimensions do not match input')
                if not (folder / 'scene.blend').stat().st_size:
                    raise ValueError('Empty Blender project')
            except (OSError, ValueError) as exc:
                failure_type, error = 'invalid_output', repr(exc)
        outputs = {}
        for stream in ('stdout', 'stderr'):
            parts = [f'[{stage}]\n' + (folder / f'{stage}_{stream}.log').read_text(errors='replace')
                     for stage in ('build', 'render') if (folder / f'{stage}_{stream}.log').exists()]
            outputs[stream] = '\n'.join(parts)
            (folder / f'{stream}.log').write_text(outputs[stream])
        result = {'ok': error is None, 'step': self.executions, 'error': error, 'failure_type': failure_type,
                  'seconds': time.monotonic() - started, 'stages': measurements, **outputs,
                  'image': str(folder / 'final.png') if error is None else None}
        self.log({'event': 'execution_result', **result})
        write_json(folder / 'result.json', result)
        if result['ok']:
            self.select(self.executions)
        return result

    def select(self, step):
        folder = self.output_dir / 'steps' / f'{step:03d}'
        if not json.loads((folder / 'result.json').read_text())['ok']:
            raise ValueError('Cannot submit a failed step')
        for name in ('scene.blend', 'final.png', 'build.py', 'camera.json'):
            shutil.copyfile(folder / name, self.output_dir / name)
        if (folder / 'actual_device.json').exists():
            shutil.copyfile(folder / 'actual_device.json', self.output_dir / 'actual_device.json')
        write_json(self.output_dir / 'selected.json', {'step': step})
        self.log({'event': 'select', 'step': step})

    def image(self, path):
        if not Path(path).resolve().is_relative_to(self.output_dir.resolve()):
            raise ValueError('Runtime image must belong to the current scene input/render directory')
        return image_message(path)
