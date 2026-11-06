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
                f'Budget: {runtime.remaining()}'
            )},
            runtime.image(task['image'])
        ]}
    ]
    rendered_view_seen = False
    while True:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE' and rendered_view_seen:
                return
            messages.append({'role': 'user', 'content': (
                'Return one complete program in a python code block. '
                'DONE is allowed only after inspecting an available rendered view. '
                'Do not claim successful execution or verification without evidence.'
            )})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        has_image = bool(result.get('image'))
        rendered_view_seen = rendered_view_seen or has_image
        report = json.dumps({k: v for k, v in result.items() if k != 'image'})
        if has_image:
            guidance = (
                'Inspect this rendered view against the original reference. '
                'Read execution status separately from image availability. '
                'Compare large boundaries, multiple independent landmarks, silhouettes, '
                'negative spaces, occlusion order and regional tone. '
                'In revision comments, distinguish observed discrepancies from uncertain causes. '
                'Choose the smallest coherent correction supported by those observations; '
                'do not bundle speculative camera, geometry and lighting changes. '
                'A shared displacement suggests checking the camera but does not prove a camera fault. '
                'Preserve matching regions and editable semantic groups. '
                'Return a complete revised program if correction is justified and execution budget remains, '
                'otherwise DONE. The last successful build is submitted; an unexecuted revision is not verified.'
            )
        else:
            guidance = (
                'No rendered view was returned for this execution. '
                'Use the reported status and actual traceback to identify executable failures. '
                'Do not infer appearance or camera errors from a missing image. '
                'If a timeout is reported without a localized cause, keep the bottleneck unknown '
                'and reduce expanded geometry and Boolean cost while preserving coverage and groups. '
                'Return a complete corrected program if execution budget remains. '
                'Do not claim this attempt was visually verified.'
            )
        content = [{'type': 'text', 'text': (
            report + '\n' + guidance + f'\nRemaining: {runtime.remaining()}'
        )}]
        if has_image:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
