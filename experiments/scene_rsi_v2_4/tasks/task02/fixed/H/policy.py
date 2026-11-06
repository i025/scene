import json
from pathlib import Path
import re


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image. Match its camera and framing. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'Build a complete editable scene; reserve available execution '
                'and model-call capacity for rendered review.'
            )},
            runtime.image(task['image'])
        ]}
    ]
    rendered = False
    while True:
        remaining = runtime.remaining()
        if remaining['model_calls'] <= 0 or remaining['seconds'] <= 0:
            return
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE':
                if rendered:
                    return
                messages.append({'role': 'user', 'content': (
                    'No rendered image has been returned yet. Do not claim visual '
                    'verification. Return one complete program in a python code '
                    'block if execution budget remains.'
                )})
            else:
                messages.append({'role': 'user', 'content': (
                    'Return one complete program in a python code block, or DONE '
                    'after reviewing an available rendering.'
                )})
            continue
        remaining = runtime.remaining()
        if remaining['executions'] <= 0 or remaining['seconds'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        render = result.get('image')
        remaining = runtime.remaining()
        report = json.dumps({k: v for k, v in result.items() if k != 'image'})
        if render:
            rendered = True
            guidance = (
                'Compare this full rendered view with the original reference. '
                'Separate execution validity, emitted-part integrity and visual '
                'agreement. Review shared perspective anchors, silhouettes and '
                'internal gaps, occlusions, and broad tonal regions. Identify the '
                'largest supported discrepancy and competing explanations. '
                'If attribution is unresolved, say so in revision comments; do '
                'not convert sensitivity into a causal diagnosis. Preserve '
                'matching groups and change a coherent parameter family where '
                'possible. Return a complete revised program if a correction is '
                'supported and execution budget remains, otherwise DONE. '
                'A revision replaces the last successful build; an unexecuted '
                'proposal is not a verified improvement.'
            )
        else:
            guidance = (
                'This execution returned no rendered image. Use explicit status '
                'and traceback evidence to diagnose execution failure; do not '
                'infer visual defects from absent imagery. If a timeout is '
                'reported, its bottleneck remains unknown unless logs locate it. '
                'Retry with a complete program only if budget remains. Preserve '
                'semantic groups and visible coverage when reducing cost. Do '
                'not claim this build was visually verified.'
            )
        content = [{'type': 'text', 'text': (
            report + '\n' + guidance + f' Remaining: {remaining}'
        )}]
        if render:
            content.append(runtime.image(render))
        messages.append({'role': 'user', 'content': content})
