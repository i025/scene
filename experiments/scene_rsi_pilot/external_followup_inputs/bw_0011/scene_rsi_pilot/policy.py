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


PROCEDURE = '''
Additional shared procedure:
Build reliability comes before visual refinement. The fixed execution budget includes
construction, realization and output, not just renderer sampling. Leave all runner-owned
render settings unchanged: do not set engine, samples, denoising, resolution, output paths
or time limits. Camera, lights, world and scoped materials remain available as documented.

Make the FIRST program a complete economical scene, with all major visible semantic
objects, their attached parts, support surfaces and foreground crops. Economize repeated
surface decoration before simplifying major silhouettes or deleting inventory. Use a small
reusable palette instead of assigning a distinct random finish to every repeated element.
A straight tube needs one rod; do not densely sample straight stretches. In this fixed
implementation sweep_tube with n points expands to 2*n-1 primitive meshes, and a fillet_box
can expand to 23 primitive meshes. Assemblies and clones do not merge their meshes.
Count expanded primitives, not builder calls. A few hundred primitive meshes is an initial
planning heuristic, not an acceptance threshold or a measured safe runtime. Spend extra
geometry on visible curvature and negative space only when its image contribution warrants it.
Do not alter SceneAct, merge semantic owners, or rename groups to influence target selection.

Include a concise self-review in the complete program's comments before submitting it:
- inventory, owner, actual support surface, camera anchors and uncertainty;
- repeated-loop expansion and the most expensive decorative families;
- positive finite dimensions, valid fillet radii, distinct rod endpoints, unique include slots;
- realize before camera/world/lights, and nonempty correctly scoped material descendants.
This is a code review, not an execution or a claim of passing regression tests. Do not spend
a separate model turn merely declaring READY unless explicitly asked for such a review.

Separate camera, each semantic object's dimensions/pose, and appearance parameters.
Before changing camera, compare at least three independent visible anchors spanning depth
and image position: architectural edge directions, a near crop/contact, and a far object or
wall feature. Record approximate reference/render locations and mismatch directions in
comments, marking them as visual estimates. An unchanged anchor between two generated
renders is not evidence that it matches the reference. Prefer a modest correction supported
by several anchors. Do not rescale all objects to compensate for an uncertain camera.
Review scale at the complete semantic owner, not an automatically selected trim or child.

Review broad appearance alongside geometry: light/dark region ordering, dominant surface
colors, shadow locations and contrast. A consistent appearance mismatch across several
surfaces may justify one lighting/world correction with geometry and camera fixed. A local
mismatch may justify a scoped material correction with lighting fixed. Do not change both
indiscriminately. Preserve non-target shaders, mesh data and transforms during local edits.
Never infer a material's physical color uniquely from its photographed brightness.

For missing objects, trace builder calls, attached returned nodes and unique include slots,
then compare camera projection, actual wall/support faces and nearer occluders. Construction
is not proof of visibility. Check the object's full extent against perpendicular wall returns
as well as its nominal support plane before translating it. Preserve reference occluders;
do not merely move an item until it is exposed. Keep all dependent parts together and
recompute actual contact offsets after size or pose changes. AABB tops and overlaps alone
cannot certify contact or collision. Unknown ownership/name mappings remain unknown.

After a valid render, choose the largest supported discrepancy that can be addressed within
the remaining time. State the chosen parameter family, expected visible change and anchors
that should remain stable in comments, then return one complete revised program. Avoid
rewriting unrelated builders. Compare the resulting full scene, not just the intended target.
Measured runtime/status, visual hypotheses and historical heuristics are separate evidence.
Controlled probe deltas, if supplied, are scope-limited sensitivity observations, not causal
proof or transferable camera/scale factors. Never invent measurements for missing outputs.
'''


def solve(task, runtime):
    # Read only the candidate's own instructions; no scene/data exploration.
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt + '\n' + PROCEDURE},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image with editable SceneAct geometry. '
                f"Image dimensions: {task['width']} x {task['height']}. "
                'Return one complete economical program, including the evidence/ownership '
                'ledger and inline pre-execution self-review. Preserve major curved silhouettes, '
                'visible inventory and support; defer dense textile marks, floor subdivisions '
                'and tiny ornament. Plan camera using near and far anchors. '
                f'Available budget: {runtime.remaining()}')},
            runtime.image(task['image'])]}
    ]
    successes = []
    selected = None
    attempts = 0
    execution_history = []

    def note(text, image_path=None):
        content = [{'type': 'text', 'text': text}]
        if image_path:
            content.append(runtime.image(image_path))
        messages.append({'role': 'user', 'content': content})

    def ask():
        response = runtime.ask(messages)
        messages.append(response)
        return _text(response).strip()

    def choose(text):
        match = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
        if match:
            step = int(match.group(1))
            if step in successes:
                return step
        return None

    while True:
        budget = runtime.remaining()
        if budget['seconds'] <= 0 or budget['model_calls'] <= 0:
            break
        if budget['executions'] <= 0:
            if successes:
                note('Execution budget exhausted. Review supplied successful full-scene renders '
                     'against the reference, including unchanged anchors, appearance and inventory. '
                     f'Successful steps: {successes}; current fallback: {selected}. '
                     'Reply SELECT <step> or DONE. Do not provide unexecutable edits or infer '
                     'success from a failed attempt. No unseen measurements are available.')
                text = ask()
                choice = choose(text)
                if choice is not None:
                    selected = choice
            break

        if execution_history:
            note('Scheduling evidence from this reconstruction only: ' +
                 json.dumps(execution_history, default=str) +
                 '\nElapsed values cover runtime.execute as observed through remaining seconds; '
                 'they do not isolate compilation, rendering or output time. A timeout does not '
                 'identify the slow phase. A camera-only revision still rebuilds the entire scene. '
                 'Allow time for a full execution and inspection; keep the successful fallback '
                 'if a useful revision is unlikely to finish. Do not alter fixed render settings. '
                 f'Remaining: {budget}')

        text = ask()
        choice = choose(text)
        if choice is not None:
            selected = choice
            break
        if text.upper() == 'DONE':
            if successes:
                break
            note('BUILD/OUTPUT FAILURE: no successful rendered output exists. DONE cannot '
                 'complete this reconstruction. Return a complete repaired economical program '
                 'if execution budget remains; do not invent a visual diagnosis.')
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            note('Return exactly one complete Python program in one python code block, '
                 'or DONE/SELECT <successful step> after a successful rendering. '
                 'Include your pre-execution self-review in program comments.')
            continue
        pending_code = blocks[0]

        # No extra model review or hidden execution: self-review is part of the draft.
        before = runtime.remaining()
        if before['executions'] <= 0 or before['seconds'] <= 0:
            break
        attempts += 1
        result = runtime.execute(pending_code)
        after = runtime.remaining()
        step = result.get('step')
        good = (result.get('ok') is True and bool(result.get('image'))
                and type(step) is int)
        elapsed = max(0.0, before['seconds'] - after['seconds'])
        execution_history.append({
            'attempt': attempts, 'step': step,
            'valid_render_returned': good,
            'execute_elapsed_seconds': round(elapsed, 3)
        })
        if good:
            successes.append(step)
            selected = step
        # Explicit fallback also protects against a later failed or missing output.
        if selected is not None:
            runtime.select(selected)

        feedback = {k: v for k, v in result.items() if k != 'image'}
        if not good:
            timeout = 'timeout' in str(result.get('error', '')).lower()
            instruction = (
                'BUILD/OUTPUT FAILURE: this attempt supplied no selectable successful render. '
                'Diagnose the reported error, missing image or missing step before visual work. '
                'There is no image-based evidence for this attempt. Preserve camera, semantic '
                'inventory, major dimensions and unrelated materials during repair. ')
            if timeout:
                instruction += (
                    'The reported timeout establishes a deadline failure, not its internal cause. '
                    'Review expanded primitive count, sweep sampling, repeated decorations, '
                    'unique finishes and costly Boolean assemblies. Reduce avoidable construction '
                    'cost while preserving important silhouettes, owners, supports and occluders. '
                    'Do not try to repair this by changing samples, engine or runner limits. ')
            else:
                instruction += (
                    'Review all related API assumptions, including primitive bounds, endpoints, '
                    'attachment names and world initialization. If no error explains missing '
                    'output, keep its cause unknown. ')
            instruction += 'Return a complete repaired program, or SELECT a prior successful step.'
        else:
            instruction = (
                'Compare this full-scene render with the reference. Separate measured facts from '
                'visual estimates and hypotheses. Check several near/far anchors, edge directions, '
                'foreground crops, whole-owner silhouette, support and occlusion. Also compare '
                'dominant light/dark regions and shadow contrast. Choose the largest supported '
                'discrepancy: camera, one semantic object with its dependents, or appearance. '
                'Hold other families fixed. An anchor unchanged across generated renders still '
                'needs comparison with the reference. Before moving an apparently absent object, '
                'check construction and all relevant wall faces and occluders; do not duplicate '
                'it or move it merely to expose it. Preserve local material non-target state and '
                'composite transforms. Return one complete revised program with a short prediction '
                'and inline self-review, DONE, or SELECT <successful step>.')
        note(json.dumps(feedback, default=str) + '\n' + instruction +
             f'\nAttempt: {attempts}. Successful steps: {successes}. '
             f'Current fallback: {selected}. Remaining: {after}',
             result.get('image') if good else None)

    if selected is not None:
        runtime.select(selected)
