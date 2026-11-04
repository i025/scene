import json
import re
from pathlib import Path


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image. Match camera, framing, occlusions and major color regions. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'First produce a complete economical scene with all major visible objects. '
                'In brief code comments record approximate normalized image landmarks, camera assumptions, '
                'and the principal uncertain proportions. Audit API constraints before returning code. '
                'Keep camera, object dimensions and lighting parameters easy to revise. '
                'Do not spend the first build on dense subpixel decoration.'
            )},
            runtime.image(task['image'])
        ]}
    ]
    successful = []
    calls = 0
    executions = 0
    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        can_build = executions < 3 and budget['executions'] > 0
        if not can_build and not successful:
            break
        response = runtime.ask(messages)
        calls += 1
        messages.append(response)
        text = response.get('content') or ''
        if not isinstance(text, str):
            text = ''
        selection = re.fullmatch(r'SELECT\s+(\d+)\s*', text.strip(), re.I)
        if selection:
            step = int(selection.group(1))
            if step in successful:
                runtime.select(step)
                return
        if text.strip().upper() == 'DONE' and successful:
            runtime.select(successful[-1])
            return
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not can_build:
            messages.append({'role': 'user', 'content': (
                f'No executions remain. Select an observed successful build: {successful}. '
                'Reply SELECT followed by its step number. Do not generate unexecutable revisions.'
            )})
            continue
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content': (
                'Return exactly one complete Python program in one python code block. '
                f'Alternatively SELECT an observed successful step from {successful}, or DONE if one exists. '
                'No successful output means reconstruction failure, not completion.'
            )})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        result = runtime.execute(blocks[0])
        executions += 1
        visible = bool(result.get('ok') and result.get('image'))
        step = result.get('step')
        if visible and isinstance(step, int):
            successful.append(step)
        report = {k: v for k, v in result.items() if k != 'image'}
        remaining = runtime.remaining()
        can_retry = executions < 3 and remaining['executions'] > 0
        if not visible:
            guidance = (
                'BUILD/OUTPUT FAILURE: no successful rendered view is available for this attempt. '
                'Do not claim a visual comparison. Read the error and audit the whole program for '
                'related faults, especially fillet radii, missing World, repeated include keys, '
                'zero-length rods and operations performed before realize. '
                'Return a complete corrected program if executions remain; preserve the intended composition.'
            )
        elif can_retry:
            guidance = (
                'Compare this render with the original reference in the first user message. '
                'In brief comments identify the three largest visible discrepancies and the parameter '
                'changes intended to fix them. Check image borders, major object extents, floor/wall '
                'boundaries, edge slopes, foreground/background size ratios, occlusions and broad tones. '
                'If errors move coherently across the scene, correct camera orientation/framing; '
                'if localized, correct the relevant object or placement. Do not change focal length '
                'and object scale indiscriminately. Preserve already matching regions and editable groups. '
                'Return one complete revised program, or SELECT an existing successful step if further '
                'changes are unjustified. Add fine detail only after composition is credible.'
            )
        else:
            guidance = (
                'No executions remain. Compare the successful rendered builds already shown with the '
                'reference. Reply SELECT followed by the best successful step number. '
                'Prefer framing, silhouettes, visibility and broad colors over detail count. '
                'Do not return a revised program.'
            )
        content = [{'type': 'text', 'text': (
            json.dumps(report, default=str) + '\n' + guidance +
            f'\nSuccessful steps: {successful}. Remaining: {remaining}'
        )}]
        if visible:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
    if successful:
        runtime.select(successful[-1])
