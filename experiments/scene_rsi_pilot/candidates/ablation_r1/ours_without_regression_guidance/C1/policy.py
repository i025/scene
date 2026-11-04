import json
from pathlib import Path
import re


REVIEW = '''Compare the reference and available successful renders. Separate observations from hypotheses. Review architectural edge directions and framing before changing object dimensions. Check foreground crops, depth order, support contacts, and visible-object coverage. A small part is not a proxy for its entire parent object. Choose one main correction family and state its expected visible effect; preserve unrelated parameters and all existing semantic groups. Return a complete revised Python program, DONE, or SELECT <successful step> to finish with an earlier build. Do not invent functional scores or measurements.'''


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image. Match its camera and framing. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'Build a complete, economical scene on the first execution. '
                'Before returning code, audit every fillet radius, unique sibling key, '
                'world initialization after realize, and support dependency. '
                'Include brief code comments recording image observations, uncertain '
                'camera assumptions, and semantic object-to-builder mappings. '
                'Prioritize silhouette, perspective, object coverage and contacts over tiny decoration.')},
            runtime.image(task['image'])]}]
    successful = []
    attempts = 0
    while True:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        if budget['executions'] <= 0 and not successful:
            return
        response = runtime.ask(messages)
        messages.append(response)
        text = response.get('content') or ''
        selection = re.fullmatch(r'SELECT\s+(\d+)', text.strip(), re.I)
        if selection:
            step = int(selection.group(1))
            if step in successful:
                runtime.select(step)
                return
            messages.append({'role': 'user', 'content':
                             f'Unknown or unsuccessful step. Available steps: {successful}.'})
            continue
        if text.strip().upper() == 'DONE':
            if successful:
                return
            messages.append({'role': 'user', 'content':
                             'No successful output exists. Return a complete corrected program.'})
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            messages.append({'role': 'user', 'content':
                             'Return one complete Python code block, DONE, or SELECT <successful step>.'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0:
            messages.append({'role': 'user', 'content':
                             f'No executions remain. Review only; return DONE or SELECT from {successful}.'})
            continue
        if budget['seconds'] <= 0:
            return
        attempts += 1
        result = runtime.execute(blocks[-1])
        step = result.get('step')
        valid = result.get('ok') is True and bool(result.get('image'))
        if valid and isinstance(step, int):
            successful.append(step)
        summary = {k: v for k, v in result.items() if k != 'image'}
        remaining = runtime.remaining()
        if valid:
            instruction = REVIEW
            if remaining['executions'] <= 0:
                instruction += ' No executions remain: return DONE or SELECT only.'
        else:
            instruction = (
                'This attempt failed or has no observable render. Do not diagnose an unseen image. '
                'Use the execution error to repair the complete program. Audit other occurrences '
                'of the same API mistake, initialization after realize, and duplicate sibling keys. '
                'Preserve the intended geometry unless the error requires a change.')
        content = [{'type': 'text', 'text':
                    json.dumps(summary, default=str) + '\n' + instruction +
                    f'\nSuccessful steps: {successful}. Attempts: {attempts}. Remaining: {remaining}'}]
        if valid:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
