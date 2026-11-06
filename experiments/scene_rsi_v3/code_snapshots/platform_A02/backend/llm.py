"""Frozen Student model, invoked exclusively through a fresh read-only Codex CLI."""
import json
from pathlib import Path
import time

from codex_wrapper import call
from data import ROOT, write_json


def image_message(path):
    return {'type': 'image_file', 'path': str(Path(path).resolve())}


def conversation_prompt(messages):
    """Preserve every role, message position and multimodal part in explicit JSON.

    codex exec accepts one prompt plus image attachments, not API role messages.
    Image occurrences are kept in order; their numeric indices map to --image inputs.
    """
    images, transcript = [], []
    for index, message in enumerate(messages):
        mapped = {**message, 'message_index': index}
        if isinstance(message.get('content'), list):
            content = []
            for part_index, part in enumerate(message['content']):
                if part['type'] == 'image_file':
                    images.append(str(Path(part['path']).resolve()))
                    content.append({'type': 'image_attachment', 'attachment_index': len(images),
                                    'part_index': part_index})
                else:
                    content.append(part)
            mapped['content'] = content
        transcript.append(mapped)
    prompt = (
        'You are the frozen Student in an indoor 3D reconstruction experiment. '
        'Answer the final message in the following ordered conversation. The embedded system '
        'messages specify the task rules; embedded assistant messages are your prior responses. '
        'Preserve their roles and chronological order when continuing the conversation. '
        'Image attachment N is the Nth --image input (one-based); each occurrence is mapped '
        'at its exact message and content position below. Compare reference and feedback images. '
        'Do not use tools, execute commands, render, save files, edit project files, access '
        'the network, or call models. Generate one complete Python program in a ```python '
        'code block, or exactly DONE when the harness permits. Blender execution is managed '
        'by runtime outside this CLI call.\n\nORDERED_CONVERSATION_JSON:\n'
    )
    return prompt + json.dumps(transcript, ensure_ascii=False, indent=2), images


class ImageLLM:
    def __init__(self, settings, log, deadline):
        self.settings, self.log, self.deadline = settings, log, deadline
        runtime = getattr(log, '__self__', None)
        self.output_dir = Path(getattr(runtime, 'output_dir', settings.get('log_dir', ROOT / 'work' / 'student_calls')))
        self.usage = {'calls': 0, 'input_tokens': 'unknown', 'output_tokens': 'unknown',
                      'cached_input_tokens': 'unknown', 'total_tokens': 'unknown',
                      'seconds': 0.0, 'cost_usd': 'unknown'}
        self._totals = {key: 0 for key in ('input_tokens', 'output_tokens', 'cached_input_tokens', 'total_tokens')}

    def __call__(self, messages):
        timeout = min(self.settings['timeout'], self.deadline - time.monotonic())
        if timeout <= 0:
            raise TimeoutError('Scene deadline reached')
        self.usage['calls'] += 1
        folder = self.output_dir / 'student_calls' / f'{self.usage["calls"]:03d}_{time.time_ns()}'
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / 'messages.json', messages)
        prompt, images = conversation_prompt(messages)
        prompt += '\nPUBLIC TASK REQUIREMENTS (not the hidden evaluation rubric):\n'+self.settings['task_instruction']
        self.log({'event': 'model_request', 'role': 'H', 'messages': messages,
                  'model': self.settings.get('name', self.settings.get('model')),
                  'reasoning_effort': self.settings['reasoning_effort'], 'call_dir': str(folder)})
        started = time.monotonic()
        try:
            text, session = call(prompt, self.settings, folder, images, role='H',
                                 timeout=timeout, log=self.log)
            for key in self._totals:
                value = session[key]
                self._totals[key] = (self._totals[key] + value
                                     if isinstance(value, int) and isinstance(self._totals[key], int)
                                     else 'unknown')
                self.usage[key] = self._totals[key]
            message = {'role': 'assistant', 'content': text}
            self.log({'event': 'model_response', 'role': 'H', 'message': message,
                      'call_dir': str(folder)})
            return message
        except Exception as error:
            for key in self._totals:
                self._totals[key] = self.usage[key] = 'unknown'
            self.log({'event': 'model_error', 'role': 'H', 'error': repr(error),
                      'call_dir': str(folder)})
            raise
        finally:
            self.usage['seconds'] += time.monotonic() - started
