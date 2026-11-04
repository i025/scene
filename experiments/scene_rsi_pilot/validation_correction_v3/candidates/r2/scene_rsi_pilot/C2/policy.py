import json
from pathlib import Path
import re


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image with a complete editable SceneAct scene. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'First build: establish camera, all major visible objects, semantic assemblies, '
                'supports and broad materials. Keep repeated surface detail inexpensive. '
                'Perform the source preflight described in the system instructions before returning code.'
            )},
            runtime.image(task['image'])
        ]}
    ]
    successful = []
    asks = 0
    executions = 0
    last_valid = False
    while asks < 5:
        remaining = runtime.remaining()
        if remaining['model_calls'] <= 0 or remaining['seconds'] <= 0:
            break
        can_build = remaining['executions'] > 0 and executions < 3
        if not can_build and not successful:
            break
        response = runtime.ask(messages)
        asks += 1
        messages.append(response)
        text = response.get('content') or ''
        choice = re.fullmatch(r'\s*SELECT\s+(\d+)\s*', text, re.I)
        if choice:
            step = int(choice.group(1))
            if step in successful:
                runtime.select(step)
                return
            messages.append({'role': 'user', 'content': 'That step has no confirmed valid render. Select only a listed successful step.'})
            continue
        if text.strip().upper() == 'DONE':
            if successful:
                runtime.select(successful[-1])
                return
            messages.append({'role': 'user', 'content': 'No valid output exists. DONE cannot repair a failed build. Return a complete corrected program if execution budget remains.'})
            continue
        if not can_build:
            break
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content': 'Return exactly one complete Python program in one python code block, or DONE after a valid render.'})
            continue
        remaining = runtime.remaining()
        if remaining['executions'] <= 0 or remaining['seconds'] <= 0:
            break
        result = runtime.execute(blocks[0])
        executions += 1
        last_valid = bool(result.get('ok') and result.get('image'))
        step = result.get('step')
        if last_valid and isinstance(step, int):
            successful.append(step)
        details = {k: v for k, v in result.items() if k != 'image'}
        remaining = runtime.remaining()
        can_build = remaining['executions'] > 0 and executions < 3
        if last_valid:
            instruction = (
                'Inspect this actual render against the original reference. Separate visual estimates '
                'from measured runtime facts. Compare architectural edges and several near/far anchors '
                'before attributing object size error to focal length. Check visible object inventory, '
                'occlusion order, contacts, and complete assembly membership. '
            )
            if can_build:
                instruction += (
                    'Choose one highest-impact revision family: camera, object geometry/placement, '
                    'or appearance. Name affected modules and dependent supports in code comments; '
                    'preserve unrelated geometry/materials. Return a complete revised program, DONE, '
                    'or SELECT followed by a successful step number if an earlier render is better.'
                )
            else:
                instruction += (
                    'No executions remain. Review only: reply DONE to retain the latest valid build, '
                    'or SELECT followed by a successful step number. Do not produce unexecutable revisions.'
                )
        else:
            instruction = (
                'BUILD/OUTPUT FAILURE: no valid rendered observation is available for this attempt. '
                'Do not infer visual errors or invent measurements. Use the supplied error/traceback '
                'to repair the program. Audit all fillet bounds, unique include keys, positive dimensions, '
                'nonzero rods, and explicit world creation after realize. A timeout has unknown phase '
                'unless the log identifies it: reduce repeated decorative geometry and tube samples '
                'while retaining object silhouettes, supports and semantic groups. '
                'Return a complete corrected program only if executions remain.'
            )
            if successful:
                runtime.select(successful[-1])
        content = [{'type': 'text', 'text': json.dumps(details, default=str) + '\n' + instruction +
                    f'\nSuccessful steps: {successful}. Remaining: {remaining}.'}]
        if last_valid:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
        if not can_build and not successful:
            break
    if successful:
        runtime.select(successful[-1])
