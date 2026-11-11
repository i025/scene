import json
from pathlib import Path
import re


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    guidance = (
        '\nBefore writing the complete program, choose a small set of visible image anchors '
        'distributed across foreground, main subject and background. Record their approximate '
        'normalized positions or bounds in program comments, together with a few dominant edge '
        'directions and overlaps. Use the original image aspect throughout. These are visual '
        'estimates, not ground-truth calibration. Parameterize camera pose, target and lens '
        'separately from major asset dimensions and positions. Prioritize the contours and '
        'large light/dark regions that occupy the image; fine detail cannot repair incorrect '
        'framing or a wrong silhouette.'
    )
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': [
        {'type': 'text', 'text': 'Reconstruct this RGB image. Match its camera and framing. ' +
         f"Image dimensions: {task['width']} x {task['height']}. Budget: {runtime.remaining()}" + guidance},
        runtime.image(task['image'])]}]
    while runtime.remaining()['model_calls'] > 0 and runtime.remaining()['seconds'] > 0:
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE':
                return
            messages.append({'role': 'user', 'content': 'Return one complete program in a python code block, or DONE.'})
            continue
        if runtime.remaining()['executions'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        content = [{'type': 'text', 'text': json.dumps({k: v for k, v in result.items() if k != 'image'})}]
        if result.get('image'):
            content.extend([
                {'type': 'text', 'text': 'Original reference, unchanged:'},
                runtime.image(task['image']),
                {'type': 'text', 'text': 'Current complete rendered camera view:'},
                runtime.image(result['image']),
                {'type': 'text', 'text': (
                    'Compare these two images directly. In brief comments before any revised code, '
                    'record reference versus rendered estimates for several of your anchors, '
                    'including at least one background and one foreground feature. Check crops, '
                    'edge slopes, overlaps, silhouette and internal gaps. Do not simply repeat '
                    'the intended reference bounds as if the render achieved them. Rank the '
                    'largest discrepancies by visible extent and contrast. For each proposed '
                    'correction, name the parameter and predict which anchors or contours will '
                    'move and in what direction. A common translation, scale error, or edge-slope '
                    'error may suggest camera changes; inconsistent errors may require asset '
                    'placement or proportion changes. Check multiple anchors before choosing, '
                    'and preserve already matching regions. If bounds mostly agree, inspect '
                    'the actual surface profile, component proportions, negative spaces, '
                    'and broad light/dark distribution instead of adding repeated tiny parts. '
                    'Distinguish observed brightness from material color: illumination and '
                    'surface orientation also affect it. Make only image-supported corrections '
                    'in a complete revised program, or reply DONE. '
                ) + f'Remaining: {runtime.remaining()}'}
            ])
        else:
            content.append({'type': 'text', 'text': (
                'No rendered image is available. Repair the reported execution failure using '
                'the actual error evidence; do not infer visual defects from this failure. '
                'Return a complete corrected program if an execution remains, or DONE. '
            ) + f'Remaining: {runtime.remaining()}'})
        messages.append({'role': 'user', 'content': content})
