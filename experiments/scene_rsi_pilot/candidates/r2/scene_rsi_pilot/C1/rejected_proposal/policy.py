import ast
import json
from pathlib import Path
import re


def _preflight(code):
    """Static checks only; never execute a program outside runtime.execute."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f'Syntax error at line {exc.lineno}: {exc.msg}'
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', '')
        if name != 'fillet_box':
            continue
        kwargs = {item.arg: item.value for item in node.keywords}
        size = node.args[0] if node.args else kwargs.get('size')
        radius = node.args[1] if len(node.args) > 1 else kwargs.get('radius')
        try:
            size = ast.literal_eval(size)
            radius = ast.literal_eval(radius)
            dims = [size] * 3 if isinstance(size, (int, float)) else list(size)
            if len(dims) == 3 and (min(dims) <= 0 or radius <= 0 or radius > min(dims) / 2):
                return f'Invalid fillet_box dimensions/radius at line {node.lineno}; require 0 < radius <= min(size)/2.'
        except (ValueError, TypeError, SyntaxError):
            pass
    return None


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image with an editable SceneAct scene. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'First return a compact complete build, including all salient objects, '
                'their support parts, camera and lighting. Before the code give a brief '
                'visible-object inventory and camera hypothesis; mark uncertainty. '
                'Use stable semantic groups, unique child keys and parameter blocks '
                'for camera, object dimensions, placement and materials. '
                'Do not spend the first build on dense decorative repetition.')},
            runtime.image(task['image'])]}]
    successes = []
    last_failure = None
    asks = 0
    executions = 0
    while asks < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        can_build = budget['executions'] > 0 and executions < 3
        if not can_build and not successes:
            break
        response = runtime.ask(messages)
        asks += 1
        messages.append(response)
        text = response.get('content') or ''
        choice = re.fullmatch(r'SELECT\s+(\d+)', text.strip(), re.I)
        if choice:
            step = int(choice.group(1))
            if step in successes:
                runtime.select(step)
                return {'status': 'complete', 'selected_step': step}
            messages.append({'role': 'user', 'content': 'Select only a successful step listed in feedback.'})
            continue
        if text.strip().upper() == 'DONE':
            if successes:
                runtime.select(successes[-1])
                return {'status': 'complete', 'selected_step': successes[-1]}
            messages.append({'role': 'user', 'content': 'No valid rendered build exists. Return a complete corrected program; DONE cannot repair missing output.'})
            continue
        if not can_build:
            messages.append({'role': 'user', 'content': f'No executions remain. Do not write unexecutable revisions. Reply SELECT n using {successes}, or DONE for the latest successful step.'})
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content': 'Return exactly one complete Python program in one python code block, or DONE after a successful render.'})
            continue
        code = blocks[0]
        problem = _preflight(code)
        if problem:
            messages.append({'role': 'user', 'content': 'Static preflight rejected this program without a Blender execution: ' + problem + ' Return a complete corrected program. Audit every primitive and world initialization as well.'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        result = runtime.execute(code)
        executions += 1
        valid = result.get('ok') is True and bool(result.get('image')) and result.get('step') is not None
        if valid:
            successes.append(result['step'])
            last_failure = None
        else:
            last_failure = result.get('error') or 'Missing successful rendered output or step identifier'
        payload = {key: value for key, value in result.items() if key != 'image'}
        budget = runtime.remaining()
        if not valid:
            advice = (
                'BUILD FAILURE: no valid new render is available; do not infer visual quality. '
                'Repair the reported exception first. For timeout, simplify decorative repetition '
                'and primitive expansion while retaining semantic objects and their support parts. '
                'Do not bypass SceneAct with detached bpy geometry. Audit all fillet radii, '
                'rod endpoints, duplicate child keys, and post-realize world initialization. '
                'Return one compact complete corrected program if executions remain.')
        elif budget['executions'] <= 0 or executions >= 3:
            advice = (
                'Final review only; no executions remain. Compare the successful views already '
                'shown with the reference. Reply SELECT n for a listed successful step, or DONE '
                'for the latest. Do not generate another program.')
        else:
            advice = (
                'Compare this view with the original reference. Separate observations from '
                'hypotheses. Check architecture and at least three distributed image anchors '
                'before changing camera. If only one object disagrees, inspect its dimensions, '
                'pose, depth, ownership and occluders before changing focal length. '
                'Check visible inventory, contacts, gaps and foreground/background order. '
                'Choose one principal correction family and state its affected modules, '
                'dependencies and preservation risks. Keep unrelated parameters fixed; '
                'include only necessary dependent adjustments. Recheck complete group movement '
                'and local material scope. Return a complete revision, SELECT n, or DONE.')
        content = [{'type': 'text', 'text': json.dumps(payload, default=str) + '\n' + advice +
                    f'\nSuccessful steps: {successes}. Remaining: {budget}'}]
        if valid:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
    if successes:
        runtime.select(successes[-1])
        return {'status': 'complete', 'selected_step': successes[-1]}
    return {'status': 'failed', 'reason': last_failure or 'No successful rendered build'}
