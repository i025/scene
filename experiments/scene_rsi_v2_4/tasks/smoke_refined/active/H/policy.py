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
    while True:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE':
                return
            messages.append({'role': 'user', 'content': (
                'Return one complete program in a python code block, or DONE. '
                f'Remaining: {runtime.remaining()}'
            )})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        metadata = {k: v for k, v in result.items() if k != 'image'}
        has_image = bool(result.get('image'))
        if has_image:
            instruction = (
                'Compare this rendered camera view with the original reference. '
                'Audit landmarks across the whole frame, including boundaries, '
                'foreground and background, before attributing a discrepancy. '
                'Separate absent geometry from emitted geometry that is cropped or occluded. '
                'Keep camera and local geometry explanations unresolved when both fit. '
                'A local improvement can accompany a global regression; inspect both. '
                'Do not infer a unique cause from a scalar score or successful hierarchy checks. '
                'If revising, state the supported discrepancy, intended parameter family, '
                'predicted landmark motion and landmarks to preserve in program comments. '
                'Return one complete revised program, or DONE if no supported revision is justified. '
                'The last successful build is submitted; there is no automatic best-build rollback.'
            )
        else:
            instruction = (
                'No rendered image was returned. Use actual execution diagnostics to repair '
                'a reported error. Do not infer camera, coverage or appearance defects from '
                'a missing image. A timeout alone does not identify its bottleneck. '
                'If retrying after a timeout, reduce expanded geometry and material cost '
                'while preserving the complete scene and editable groups. '
                'Return one complete revised program when a retry is justified, or DONE. '
                'Do not claim visual verification without a successful rendered image.'
            )
        content = [{'type': 'text', 'text': (
            json.dumps(metadata) + '\n' + instruction +
            f' Remaining: {runtime.remaining()}'
        )}]
        if has_image:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
