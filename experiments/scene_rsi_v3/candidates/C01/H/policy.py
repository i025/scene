import json
from pathlib import Path
import re


REVIEW = '''Review the labeled original reference and current render together at the original image aspect ratio.
Before writing a revised program, put a compact discrepancy ledger in its opening comments.
For the three largest supported mismatches, record:
- the visible reference object or architectural boundary;
- approximate reference and rendered normalized coordinates (x right, y down);
- whether it is absent from the program, outside the camera frame, occluded, or visible with wrong shape/placement; mark uncertain causes unknown;
- the parameter family to change and the expected direction of its image-space effect.
Include foreground fragments and frame-edge objects in this comparison. An emitted asset is not evidence that its visible reference portion appears in the render.
Check architectural edge slopes and at least two objects at different depths before changing the camera. If the background already matches but a foreground object does not, preserve the matching background while considering local position, orientation and dimensions. Do not assume that moving an object closer will bring it into frame: off-axis objects can move farther beyond the frame edge.
Preserve plausible floor contact and connected furniture construction while correcting projected placement. Do not lower furniture through the floor merely to hide excess visible height; consider camera height/aim, depth and supported proportions together.
State which already matching anchors should remain stable. Spend the revision on the largest visible discrepancies before surface microdetail. A proposed correction is not verified until its resulting render is inspected.
Return one complete revised Python program, or DONE if no supported correction remains.'''


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': [
        {'type': 'text', 'text': 'Reconstruct this RGB image. Match its camera and framing. ' +
         f"Image dimensions: {task['width']} x {task['height']}. Budget: {runtime.remaining()}"},
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
        content = [{'type': 'text', 'text': json.dumps({k: v for k, v in result.items() if k != 'image'}) +
                    f'\nRemaining: {runtime.remaining()}'}]
        if result.get('image'):
            content.extend([
                {'type': 'text', 'text': 'ORIGINAL REFERENCE:'},
                runtime.image(task['image']),
                {'type': 'text', 'text': 'CURRENT EXECUTION RENDER:'},
                runtime.image(result['image']),
                {'type': 'text', 'text': REVIEW}
            ])
        else:
            content.append({'type': 'text', 'text':
                'No rendered image is available from this execution. Use the actual error and logs to repair the complete program. Do not infer visual defects or claim visual verification from this failure. Return one complete Python program if a retry remains, otherwise DONE.'})
        messages.append({'role': 'user', 'content': content})
