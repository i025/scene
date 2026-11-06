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
                'Build a complete editable scene. Separate estimates of local shape, '
                'projected size, depth, and camera pose; prioritize visible silhouettes '
                'and openings before repeated surface detail.'
            )},
            runtime.image(task['image'])
        ]}
    ]
    while runtime.remaining()['model_calls'] > 0 and runtime.remaining()['seconds'] > 0:
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE':
                return
            messages.append({'role': 'user', 'content':
                             'Return one complete program in a python code block, or DONE.'})
            continue
        if runtime.remaining()['executions'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        has_image = bool(result.get('image'))
        evidence = json.dumps({k: v for k, v in result.items() if k != 'image'})
        if has_image:
            review = (
                'Compare this render with the original reference. In comments of any '
                'revision, record the largest supported discrepancies and the parameter '
                'family chosen for each. Distinguish a wrong local profile or opening '
                'from uniform projected size and depth; compare shared scene landmarks '
                'before changing the camera. Check contour, visible interior, gaps and '
                'occlusion, not only object bounding boxes. Preserve matching groups. '
                'A successful build or hierarchy check does not establish visual fidelity. '
                'Return a complete revised program if a correction is supported and '
                'execution budget remains; otherwise finish with DONE. '
            )
        else:
            review = (
                'No rendered image was returned. Use the execution diagnostics to repair '
                'an explicit failure. Do not infer visual defects from missing output. '
                'For a timeout, the bottleneck is unknown unless logs locate it; simplify '
                'expanded geometry and Boolean work while preserving complete coverage '
                'and editable groups. Return a complete retry only if execution budget '
                'remains. Do not claim rendered verification. '
            )
        content = [{'type': 'text', 'text':
                    evidence + '\n' + review + f'Remaining: {runtime.remaining()}'}]
        if has_image:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
