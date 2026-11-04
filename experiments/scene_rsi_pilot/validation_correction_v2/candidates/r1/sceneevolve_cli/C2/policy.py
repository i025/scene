import json
from pathlib import Path
import re


GUIDANCE = '''
Reconstruct from the supplied RGB only. Use the fixed SceneAct API and meaningful
multipart Asset groups. No tools, file exploration, reference textures, projections,
additional views, rendering calls or saving calls. The runner renders and saves.
Do not change runner settings, resolution, sampling, backend or resource limits.

Before coding, state a compact visible-image specification: major silhouettes and
normalized bounds (top-left origin), architectural boundary endpoints, perspective
line directions, foreground cropping, and occlusion order. Distinguish observations
from uncertain depth assumptions. Name camera position, target, lens and major object
dimensions as parameters. Build all substantial visible objects on the first attempt.
Match the visible negative spaces as carefully as occupied regions: openings between
supports, under furniture, around foreground objects and through the room.

Keep construction economical. SceneAct sweep_tube emits a sphere at every point and
one cylinder per segment; fillet_box emits many separate meshes. Long decorative
loops and floor grids can create thousands of objects before rendering even begins.
Use boxes for flat parts, rods for straight parts, and short sweeps for curved outlines.
Restrict repeated geometry to visible regions. Use procedural material patterns for
fine surface markings, never the input image. Avoid modeling subpixel stitches, grain,
weave and hidden flooring as separate objects. Preserve object identities and editable
parts; do not merge the entire scene. Prefer a few hundred primitives where possible,
without omitting important objects. Simplify detail further when time is short.

Check source before returning every program:
- fillet_box requires 0 < radius <= half the smallest size component.
- rod endpoints are keyword arguments and must be distinct. Consecutive sweep points
  must be distinct. All dimensions must be positive and finite.
- include replaces a child with the same key; include every loop index in repeated keys.
- Transform pivots default to bounding-box centers; specify other pivots explicitly.
- realize clears Blender. Create camera, lights and material customization afterward.
  Obtain bpy.context.scene after realize. Create its world if None and enable use_nodes
  before accessing Background. Mesh names need not equal SceneAct include keys:
  target mesh descendants of the relevant marker and copy shared materials for local edits.
- Keep all visible parts of an object under its meaningful assembly through revisions.

After rendering, compare actual images, not the intended effect of code. Use a small
residual table: region or landmark, reference estimate, rendered estimate, discrepancy,
likely cause, and proposed parameter change. Estimates are visual, not measurements.
Check architecture and foreground together before changing the camera. Global position
errors suggest aim/shift; slopes suggest orientation; near/far ratios suggest camera
position and lens. Local errors suggest geometry or placement. Explain any coupled
camera and geometry change. Prioritize silhouette, occlusion, framing, large color
regions and illumination over ornament. Avoid simultaneously darkening every material
and reducing all lights: isolate the dominant cause of a brightness discrepancy.
Do not infer hidden objects or exact physical dimensions from category conventions.

A visual audit is a model-only comparison, not permission to execute anything.
When requested, begin with BEST <step>, choosing the best available successful render
against the reference. This records a fallback, not a claim about an unrendered revision.
Then provide the requested critique and/or one complete standalone Python program in
one python fenced block. Preserve sound geometry and change at most three coherent
parameter families. Never return a patch. SELECT <step> ends reconstruction with that
successful output. DONE accepts the latest successful output. Missing or failed output
is a failure, not an image to critique. Repair the reported cause and related source
hazards; never invent metrics or claim visual validation of an unrendered program.
'''


def _text(response):
    content = response.get('content') or ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(item.get('text', '') for item in content
                         if isinstance(item, dict) and item.get('type') == 'text')
    return ''


def _program(text):
    blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S | re.I)
    return blocks[-1] if blocks else None


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt + '\n' + GUIDANCE},
        {'role': 'user', 'content': [
            {'type': 'text', 'text':
             'Give the compact RGB image specification, then a complete economical '
             'SceneAct program. Perform the source checks within this response. '
             'Include all major visible objects, but defer fine ornament. '
             f"Image dimensions: {task['width']} x {task['height']}. "
             f'Remaining budget: {runtime.remaining()}'},
            runtime.image(task['image'])]}]
    successful = []
    incumbent = None
    audited = False
    awaiting_audit = False
    execution_cost = 90.0

    def choose(step):
        nonlocal incumbent
        incumbent = step
        runtime.select(step)

    while True:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        if budget['executions'] <= 0 and not successful:
            break

        response = runtime.ask(messages)
        messages.append(response)
        text = _text(response)
        best = re.search(r'^\s*BEST\s+(\d+)\s*$', text, re.M | re.I)
        if best and int(best.group(1)) in successful:
            choose(int(best.group(1)))
        selection = re.fullmatch(r'\s*SELECT\s+(\d+)\s*', text, re.I)
        if selection:
            step = int(selection.group(1))
            if step in successful:
                choose(step)
                return
            messages.append({'role': 'user', 'content':
                             f'Invalid selection. Eligible successful steps: {successful}.'})
            continue
        if text.strip().upper() == 'DONE':
            if successful:
                choose(successful[-1])
                return
            messages.append({'role': 'user', 'content':
                             'No successful output exists. Return a complete program.'})
            continue

        code = _program(text)
        if awaiting_audit:
            awaiting_audit = False
            if code is None:
                messages.append({'role': 'user', 'content':
                    'Implement the visual audit in one complete program. Keep matching '
                    'parts intact. Begin BEST <step> to identify your fallback. '
                    f'Remaining: {runtime.remaining()}'})
                continue
        if code is None:
            messages.append({'role': 'user', 'content':
                             'Return a complete program in one python fenced block, '
                             f'or SELECT an eligible successful step: {successful}.'})
            continue

        budget = runtime.remaining()
        if budget['executions'] <= 0:
            messages.append({'role': 'user', 'content':
                             'No executions remain. Reply only SELECT <step> from '
                             f'{successful}. Do not produce unused code.'})
            continue
        if budget['seconds'] <= 0:
            break
        # A reviewed incumbent remains available if an attempted revision fails.
        before = budget['seconds']
        result = runtime.execute(code)
        budget = runtime.remaining()
        execution_cost = max(execution_cost, max(0.0, before-budget['seconds']))
        valid = bool(result.get('ok') and result.get('image')
                     and result.get('step') is not None)
        if valid:
            successful.append(result['step'])
            if incumbent is None:
                choose(result['step'])
            else:
                runtime.select(incumbent)
        elif incumbent is not None:
            runtime.select(incumbent)

        # Preserve complete responses, code and reported result text in context.
        details = json.dumps({k: v for k, v in result.items() if k != 'image'},
                             default=str)
        can_revise = (budget['executions'] > 0 and
                      (not successful or budget['seconds'] >
                       120.0 + 1.25 * execution_cost))
        if not valid:
            if not can_revise:
                instruction = (
                    'FAILED OUTPUT. No confirmed image exists for this attempt. '
                    'Choose among the successful images already shown; reply SELECT <step>. ')
            else:
                instruction = (
                    'FAILED OUTPUT. Do not critique an absent image. Inspect the full '
                    'reported error and source. Return a complete repaired program. '
                    'For a timeout, reduce repeated primitive counts and decorative '
                    'construction while retaining major silhouettes and editable groups. ')
        elif not can_revise:
            instruction = (
                'Finish with visual selection. Compare every successful render with '
                'the RGB reference, prioritizing framing, silhouettes, occlusions and '
                'broad appearance. Reply only SELECT <step>. No new code. ')
        elif (not audited and len(successful) == 1 and
              budget['model_calls'] >= 4 and
              budget['seconds'] > 300.0 + 2.5 * execution_cost):
            audited = True
            awaiting_audit = True
            instruction = (
                'Perform a dedicated visual audit before rewriting code. Begin BEST '
                '<step>. Give the residual table for at most three high-impact '
                'discrepancies, including negative spaces and architectural boundaries. '
                'Separate camera errors from local geometry and lighting errors. '
                'Specify concrete parameter changes and what should remain fixed. '
                'Do not return code on this turn. ')
        else:
            instruction = (
                'Begin BEST <step> by comparing the available successful outputs to '
                'the reference. Give at most three residuals and a complete revised '
                'program addressing them. Preserve matching regions and keep geometry '
                'economical. If no worthwhile correction remains, SELECT the best step. ')

        content = [{'type': 'text', 'text': details + '\n' + instruction +
                    f'Eligible steps: {successful}. Reviewed fallback: {incumbent}. '
                    f'Remaining: {budget}'}]
        if valid:
            content.extend([
                {'type': 'text', 'text': 'Original RGB reference:'},
                runtime.image(task['image']),
                {'type': 'text', 'text': f"Actual rendered step {result['step']}:"},
                runtime.image(result['image'])])
        messages.append({'role': 'user', 'content': content})
        if not can_revise and len(successful) <= 1:
            break

    if incumbent is not None:
        runtime.select(incumbent)
