import json
from pathlib import Path
import re


def _text(response):
    content = response.get('content') or ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(item.get('text', '') for item in content if isinstance(item, dict))
    return ''


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image with editable SceneAct geometry. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                'First produce a complete program, including a short evidence/ownership ledger in comments. '
                'Prioritize camera, major silhouettes, visible inventory and support before small decoration. '
                f'Available budget: {runtime.remaining()}')},
            runtime.image(task['image'])]}
    ]
    successes = []
    selected = None
    audited = False
    pending_code = None
    attempts = 0

    def ask():
        response = runtime.ask(messages)
        messages.append(response)
        return _text(response).strip()

    def note(text, image_path=None):
        content = [{'type': 'text', 'text': text}]
        if image_path:
            content.append(runtime.image(image_path))
        messages.append({'role': 'user', 'content': content})

    while True:
        budget = runtime.remaining()
        if budget['seconds'] <= 0 or budget['model_calls'] <= 0:
            break
        if budget['executions'] <= 0:
            if successes:
                note('Execution budget exhausted. Review only; do not write another program. '
                     f'Successful rendered steps: {successes}. '
                     'Reply SELECT <step> for the best supported full-scene reconstruction, or DONE to keep the current selection. '
                     'Use the reference and supplied renders; do not invent scores or claim unseen edits succeeded.')
                text = ask()
                match = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
                if match and int(match.group(1)) in successes:
                    selected = int(match.group(1))
                    runtime.select(selected)
            break

        text = ask()
        choice = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
        if choice and int(choice.group(1)) in successes:
            selected = int(choice.group(1))
            runtime.select(selected)
            return
        if text.upper() == 'DONE':
            if successes:
                return
            note('No successful rendered output exists. This is a reconstruction failure, not completion. '
                 'Return a complete runnable program if execution budget remains.')
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            note('Return exactly one complete Python program in one python code block, '
                 'or DONE/SELECT <successful step> after a successful rendering.')
            continue
        pending_code = blocks[0]

        # One observable review turn protects the scarce Blender executions.
        # The draft itself remains runnable if the review is malformed.
        budget = runtime.remaining()
        if not audited and budget['model_calls'] >= 2 and budget['seconds'] > 0:
            audited = True
            note('PRE-EXECUTION REVIEW: the preceding program has NOT run. Review it in this same model role. '
                 'Check every fillet radius against half the smallest dimension, distinct rod endpoints, '
                 'unique include keys in loops, and world creation AFTER realize. '
                 'Check each visible object has a semantic Asset owner, including upholstery and decoration; '
                 'check local material selection reaches actual mesh descendants and copies shared materials. '
                 'Check support offsets, camera framing and cropped foreground inventory. '
                 'Return exactly READY if unchanged, otherwise one complete corrected Python program. '
                 'Do not claim measured render or regression results. '
                 f'Remaining: {budget}')
            review = ask()
            reviewed = re.findall(r'```python\s*\n(.*?)```', review, re.S)
            if len(reviewed) == 1:
                pending_code = reviewed[0]
            elif review.upper() != 'READY':
                note('Review did not supply an unambiguous replacement. Executing the preceding complete draft; '
                     'the review is not evidence of success.')

        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        attempts += 1
        result = runtime.execute(pending_code)
        step = result.get('step')
        has_render = bool(result.get('image'))
        good = result.get('ok') is True and has_render
        if good and isinstance(step, int):
            successes.append(step)
            selected = step
        elif selected is not None:
            runtime.select(selected)
        feedback = {k: v for k, v in result.items() if k != 'image'}
        if not good:
            instruction = (
                'BUILD/OUTPUT FAILURE: no valid successful rendering was supplied for this attempt. '
                'Diagnose the actual error or missing image; do not compare an absent render. '
                'Review all related API assumptions before returning a complete repaired program. '
                'Preserve unrelated geometry and camera during error repair.')
        else:
            instruction = (
                'Compare this full-scene render with the reference. Record observations separately from hypotheses. '
                'First compare architecture, horizon/edge directions, foreground crops and multiple depth anchors. '
                'Then compare object silhouette, internal proportions, contact and occlusion order. '
                'Choose a coherent correction: camera parameters with geometry fixed, or one semantic object '
                'and its dependent parts with camera fixed. Do not infer whole-object scale from a decorative child. '
                'For a missing visible item, inspect construction/ownership, framing and occluders before adding a duplicate. '
                'Preserve non-target materials and composite relative transforms. '
                'Return a complete revised program if worthwhile and executable, DONE, or SELECT <successful step>.')
        note(json.dumps(feedback, default=str) + '\n' + instruction +
             f'\nAttempt: {attempts}. Successful rendered steps: {successes}. Remaining: {runtime.remaining()}',
             result.get('image') if good else None)
    if selected is not None:
        runtime.select(selected)
