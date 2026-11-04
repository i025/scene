import json
from pathlib import Path
import re


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image. Match camera, framing, visible geometry and materials. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'In short code comments, record your estimated image-space anchors and camera assumptions. '
                'Return a complete first build now, including all major visible objects. '
                'Before returning, audit every fillet radius, repeated include key, world initialization, '
                'and material assignment against the system instructions. '
                'Keep fine decoration economical so executions remain available for visual correction.')},
            runtime.image(task['image'])
        ]}
    ]
    valid_steps = []
    attempts = 0
    calls = 0
    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        if budget['executions'] <= 0 and len(valid_steps) < 2:
            return
        response = runtime.ask(messages)
        calls += 1
        messages.append(response)
        text = response.get('content') or ''
        selection = re.fullmatch(r'SELECT\s+(\d+)', text.strip(), re.I)
        if selection:
            step = int(selection.group(1))
            if step in valid_steps:
                runtime.select(step)
                return
            messages.append({'role': 'user', 'content': 'Select only a successful rendered step from ' + str(valid_steps) + '.'})
            continue
        if text.strip().upper() == 'DONE':
            if valid_steps:
                runtime.select(valid_steps[-1])
                return
            messages.append({'role': 'user', 'content': 'No valid rendered output exists. This is a reconstruction failure so far. Return a complete corrected program while execution budget remains.'})
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content': 'Return exactly one complete program in one python code block, DONE to keep the latest successful rendered build, or SELECT followed by a successful step number.'})
            continue
        budget = runtime.remaining()
        if attempts >= 3 or budget['executions'] <= 0 or budget['seconds'] <= 0:
            if len(valid_steps) >= 2:
                messages.append({'role': 'user', 'content': 'No executions remain. Compare the already supplied renders with the reference and reply SELECT n, choosing from ' + str(valid_steps) + '. Do not write more code.'})
                continue
            return
        attempts += 1
        result = runtime.execute(blocks[0])
        rendered = result.get('ok') is True and bool(result.get('image'))
        step = result.get('step')
        if rendered and isinstance(step, int):
            valid_steps.append(step)
        report = {k: v for k, v in result.items() if k != 'image'}
        report['usable_render'] = rendered
        remaining = runtime.remaining()
        if not rendered:
            guidance = (
                'FAILURE: no valid rendered output is available for this attempt. '
                'Do not infer visual quality from this result. Read the traceback and repair the root cause. '
                'Audit the entire program for the same error and the other documented API hazards. '
                'Preserve the intended composition; return a complete runnable replacement.'
            )
            if valid_steps:
                runtime.select(valid_steps[-1])
        elif remaining['executions'] > 0 and attempts < 3:
            guidance = (
                'Compare this render directly with the original reference. In brief code comments identify '
                'the largest two or three visible discrepancies and the parameter changes addressing them. '
                'Check architectural line slopes, framing, object silhouettes, relative sizes, occlusion, '
                'missing foreground objects, and large light/dark regions before small decoration. '
                'A global framing error calls for camera changes; a local silhouette error calls for geometry. '
                'Do not change focal length and object scale together without independent evidence. '
                'Return a complete revised program if a substantial correction is supported. '
                'Otherwise return DONE, or SELECT n to retain an earlier successful render.'
            )
        else:
            guidance = (
                'No more builds are available. Compare the successful renders already supplied with the '
                'reference and reply SELECT n for the best existing build. Do not generate unexecutable code.'
            )
        content = [{'type': 'text', 'text': json.dumps(report, default=str) + '\n' + guidance +
                    f'\nSuccessful rendered steps: {valid_steps}. Remaining: {remaining}'}]
        if rendered:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
