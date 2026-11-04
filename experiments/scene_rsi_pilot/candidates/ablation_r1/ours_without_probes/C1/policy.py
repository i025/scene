import json
from pathlib import Path
import re


def _program(response):
    text = response.get('content') or ''
    if not isinstance(text, str):
        return '', None
    blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
    return text.strip(), blocks[-1] if blocks else None


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image with editable SceneAct geometry. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. '
                'First produce a complete build with concise comments recording visible anchors, '
                'uncertain camera/scale assumptions, object groups and support relations. '
                'Include all salient visible objects before fine decoration. '
                'An initial source audit may precede the first execution; no diagnostic probes are available.'
            )}, runtime.image(task['image'])]}]
    calls = 0
    executions = 0
    audited = False
    successful = []
    selected = None
    have_output = False

    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        if (budget['executions'] <= 0 or executions >= 3) and not have_output:
            break
        response = runtime.ask(messages)
        calls += 1
        messages.append(response)
        text, code = _program(response)
        choice = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
        if choice and int(choice.group(1)) in successful:
            selected = int(choice.group(1))
            break
        if text.upper() == 'DONE' and have_output:
            break
        if code is None:
            messages.append({'role': 'user', 'content': (
                'Return one complete Python program, or DONE after a successful observed render. '
                f'SELECT is allowed only for these successful rendered steps: {successful}. '
                'No output or missing imagery is a failure, not evidence of visual agreement.'
            )})
            continue

        budget = runtime.remaining()
        if budget['executions'] <= 0 or executions >= 3:
            messages.append({'role': 'user', 'content': (
                'No executions remain. Unexecuted revisions cannot be submitted. '
                f'Review the observed renders and return SELECT n from {successful}, or DONE '
                'to retain the last successful rendered build.'
            )})
            continue

        # One observable source-review turn, using the same model and interfaces.
        # Leave capacity for two rendered corrections whenever the initial budget permits.
        if not audited:
            audited = True
            if calls == 1 and budget['model_calls'] >= 4 and budget['seconds'] > 0:
                messages.append({'role': 'user', 'content': (
                    'SOURCE AUDIT ONLY: this draft has not executed and there is no render. '
                    'Return the complete corrected program now. Check every fillet radius against '
                    'half the smallest dimension, positive dimensions and distinct rod endpoints; '
                    'initialize a missing World after realize; check unique include keys in all loops '
                    'and helpers. Check that semantic object parts share their intended Asset, '
                    'material customization resolves meshes through the named parent subtree and '
                    'copies shared materials before local edits. Preserve the proposed composition '
                    'unless the source contradicts the reference. Keep camera and object scale '
                    'parameters separate. Do not claim this audit measured image quality or edit success.'
                )})
                continue

        budget = runtime.remaining()
        if budget['seconds'] <= 0 or budget['executions'] <= 0:
            break
        result = runtime.execute(code)
        executions += 1
        image_path = result.get('image')
        observed_success = result.get('ok') is True and bool(image_path)
        if observed_success:
            have_output = True
            step = result.get('step')
            if isinstance(step, int):
                successful.append(step)
                selected = step
        payload = {k: v for k, v in result.items() if k != 'image'}
        payload['observed_render_available'] = observed_success
        budget = runtime.remaining()
        if not observed_success:
            direction = (
                'EXECUTION/OUTPUT FAILURE: no valid rendered observation is available for this attempt. '
                'Use the actual error log; do not invent image measurements or infer visual changes. '
                'Repair the failure and audit other uses of the same API before returning a complete program.'
            )
        elif budget['executions'] <= 0 or executions >= 3:
            direction = (
                'FINAL REVIEW: no executions remain. Compare the reference and the available renders. '
                f'Return SELECT n from {successful}, or DONE to keep the last successful rendered build. '
                'Do not produce an unexecutable revision.'
            )
        else:
            direction = (
                'Compare this render with the original reference. In short source comments, separate '
                'observed discrepancies from hypotheses. Check framing and architecture anchors first; '
                'distinguish global camera disagreement from local object proportions. Check visible '
                'object inventory, cropping, occlusion order and support contacts before materials. '
                'Choose a small coherent correction with explicit affected modules and dependencies; '
                'preserve unrelated geometry and finishes. Return a complete revised program, DONE, '
                f'or SELECT n from {successful}. These are production revisions, not diagnostic probes.'
            )
        content = [{'type': 'text', 'text': json.dumps(payload, default=str) + '\n' + direction +
                    f'\nRemaining: {budget}'}]
        if observed_success:
            content.append(runtime.image(image_path))
        messages.append({'role': 'user', 'content': content})

    if not have_output:
        raise RuntimeError('Reconstruction failed: no successful execution with a returned render was observed.')
    if selected is not None:
        runtime.select(selected)
