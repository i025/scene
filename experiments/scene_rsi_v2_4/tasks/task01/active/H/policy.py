import json
from pathlib import Path
import re


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text':
                'Reconstruct this RGB image. Match its camera and framing. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Available budget: {runtime.remaining()}'},
            runtime.image(task['image'])
        ]}
    ]
    executions = 0
    while True:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        if text.strip().upper() == 'DONE':
            return
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            messages.append({'role': 'user', 'content':
                'Return one complete runnable program in one python code block, '
                'or exactly DONE. Do not return a patch or an unexecuted proposed scene.'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        executions += 1
        budget = runtime.remaining()
        has_image = bool(result.get('image'))
        feedback = json.dumps({k: v for k, v in result.items() if k != 'image'})
        if has_image:
            instruction = (
                'Compare this render with the original reference, not just the preceding render. '
                'Review perspective landmarks, silhouettes, visible surface proportions, '
                'occlusion order and negative spaces. Mechanical checks establish only their '
                'stated properties. Separate observations from competing explanations. '
                'If attribution remains unresolved, do not prescribe a universal camera or '
                'object correction. Choose the smallest supported revision, preserving '
                'matching groups and semantic parts. State its evidence and expected visible '
                'effect in program comments. A revised program must be complete.'
            )
        else:
            instruction = (
                'No rendered image was returned. Use the actual errors or logs for repairs; '
                'do not infer visual defects from this result. For a timeout without a located '
                'bottleneck, reduce expanded geometry and material costs while preserving '
                'the complete inventory and editable groups. A retry requires a complete program.'
            )
        if budget['executions'] <= 0:
            instruction += (
                ' No executions remain. Review the available evidence and reply exactly DONE. '
                'Do not emit an unverified replacement: the last successful build is submitted.'
            )
        else:
            instruction += (
                ' Reply with a complete revised program if a correction is supported and '
                'affordable; otherwise reply exactly DONE. Reserve the remaining execution '
                'for verification of the intended submission, not a disposable diagnostic.'
            )
        content = [{'type': 'text', 'text':
            feedback + '\n' + instruction +
            f'\nExecutions attempted: {executions}. Remaining: {budget}'}]
        if has_image:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
