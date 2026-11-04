import json
from pathlib import Path
import re


GUIDANCE = '''
Produce a compact, complete first reconstruction immediately, leaving time for
visual correction. Aim for about 180 lines and 250 expanded primitive meshes;
these are planning targets, not external resource limits. Include architecture,
all major visible objects, separate materials, and meaningful composite Asset
groups. Prioritize projected silhouettes, perspective, occlusion and large color
regions before ornament. Keep camera and major dimensions in named parameters.

Before coding, record at most six short comments with visually estimated image
anchors. Use normalized coordinates with origin at TOP LEFT, x right and y down.
Include major bounds, floor/wall boundaries, two perspective edge directions,
and a foreground/background overlap. Record uncertain anchors as uncertain.
Use the actual photograph's framing, including cropped objects and empty spaces.
Do not replace irregular visible silhouettes with generic category prototypes.
Model broad visible surfaces as surfaces with thickness, not just outline rods.

Execution reliability:
- Keep all geometry and relationships in SceneAct; do not redefine constructors
  or bypass the backend with another mesh generator.
- realize(scene) clears Blender. Create camera, lights, materials and world after it.
- Initialize the world before accessing nodes:
  sc = bpy.context.scene
  if sc.world is None:
      sc.world = bpy.data.worlds.new('Ambient')
  sc.world.use_nodes = True
- fillet_box needs 0 < radius <= half the smallest size component, including
  thickness. It expands to up to 23 meshes. Use boxes for thin flat panels.
- Each include key must be unique within its parent, including nested loop keys.
  Duplicate keys replace children. rod endpoints must differ.
- sweep_tube produces rods and spheres; use sparse control points. Avoid dense
  decorative geometry and costly Boolean assemblies. Use simple procedural
  materials for surface patterns; never use the photograph as a texture.
- Keep supports, frames and upholstery together under editable object groups.
- Do not render or save files yourself. Do not change the fixed rendering engine,
  samples, resolution, denoising, backend or resource limits. Configure scene
  lighting, materials and camera only within the permitted API.

Visual correction:
Compare reference and render explicitly before changing code. Distinguish a shared
projection error from individual shape errors. Check edge slopes, visible top/side
surface ratios and near/far size ratios as well as bounding boxes. Focal length
changes framing; camera distance changes perspective too. Do not compensate for
a wrong camera by independently stretching many unrelated objects. Conversely,
do not move a good camera to fix one misplaced object. Use modest changes when
uncertain. Preserve correctly matched geometry, groups and materials.
For brightness, distinguish a global exposure/illumination mismatch from a local
material mismatch. Avoid simultaneously darkening all materials and all lights.
Spend correction renders on the largest visible discrepancies, not tiny details.

A failed execution or missing image provides no new visual evidence. Repair the
reported error and audit the requirements above. After a timeout, substantially
simplify repeated geometry. Missing output is failure, not a quality measurement.
Never claim numerical similarity scores that were not supplied.

Normally return exactly one complete Python code block. A specifically requested
visual audit instead requires concise observations and no code. After a successful
build you may reply DONE to retain the latest successful build, or SELECT <step>
to retain another supplied successful step. Only supplied successful steps count.
All work must use this conversation and the supplied interfaces: no external tools,
filesystem exploration, assets, subprocesses, other models or independent renders.
'''

AUDIT = '''
Perform a visual audit before the next program revision. Return no code and do
not request another render. Use the original reference and the labeled actual
render below; previous prose descriptions are hypotheses, not observations.
In at most 220 words:
1. Give three high-confidence anchor comparisons as reference (x,y) versus render
   (x,y), using top-left normalized image coordinates. These are visual estimates,
   not measured scores. Include a major silhouette and an architectural boundary.
2. Compare two long edge directions and one foreground/background occlusion.
3. Decide whether the dominant mismatch is camera, local geometry, or appearance.
   Explain which observations support that decision. If several unrelated objects
   need the same apparent shift or scale, test the camera explanation first.
4. Specify at most three concrete parameter changes, their intended image-space
   effects, and one already-correct feature each change must preserve.
Do not infer a camera correction from an isolated object. Do not invent detail
hidden by occlusion. If evidence is ambiguous, favor a smaller reversible change.
'''


def _text(response):
    content = response.get('content') or ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(item.get('text', '') for item in content
                         if isinstance(item, dict) and item.get('type') == 'text')
    return ''


def _chosen(text, successful):
    match = re.fullmatch(r'SELECT\s+(\d+)\s*', text.strip(), re.I)
    if match:
        for step in successful:
            if str(step) == match.group(1):
                return step
    return None


def _pair(runtime, task, result):
    return [
        {'type': 'text', 'text': 'ORIGINAL RGB REFERENCE:'},
        runtime.image(task['image']),
        {'type': 'text', 'text': f"ACTUAL SUCCESSFUL RENDER, step {result['step']}:"},
        runtime.image(result['image'])]


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt + '\n' + GUIDANCE},
        {'role': 'user', 'content': [
            {'type': 'text', 'text':
             'Reconstruct this RGB photograph as an editable SceneAct scene. '
             'Return a compact complete first program with explicit camera parameters. '
             f"Image dimensions: {task['width']} x {task['height']}. "
             f'Available budget: {runtime.remaining()}'},
            runtime.image(task['image'])]}]
    successful = []
    renders = {}
    selected = None
    audit_used = False

    while True:
        budget = runtime.remaining()
        if (budget['model_calls'] <= 0 or budget['seconds'] <= 0
                or budget['executions'] <= 0):
            break
        response = runtime.ask(messages)
        messages.append(response)
        text = _text(response)
        choice = _chosen(text, successful)
        if choice is not None:
            runtime.select(choice)
            return
        if text.strip().upper() == 'DONE' and successful:
            runtime.select(selected)
            return
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S | re.I)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content':
                'Return exactly one complete runnable Python code block. '
                'DONE or SELECT is permitted only after a successful build. '
                f'Successful steps: {successful}. Remaining: {runtime.remaining()}'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        result = runtime.execute(blocks[0])
        valid = bool(result.get('ok') and result.get('image')
                     and result.get('step') is not None)
        feedback = {k: v for k, v in result.items() if k != 'image'}
        if valid:
            selected = result['step']
            if selected not in successful:
                successful.append(selected)
            renders[selected] = result['image']
            runtime.select(selected)
        elif selected is not None:
            runtime.select(selected)

        budget = runtime.remaining()
        # Use the otherwise spare session only if two corrections and a final
        # selection session still fit the remaining call budget.
        do_audit = (valid and not audit_used and len(successful) == 1
                    and budget['model_calls'] >= 4
                    and budget['executions'] >= 2
                    and budget['seconds'] > 420)
        if do_audit:
            content = [{'type': 'text', 'text':
                        json.dumps(feedback, default=str) + '\n' + AUDIT}]
            content.extend(_pair(runtime, task, result))
            messages.append({'role': 'user', 'content': content})
            audit = runtime.ask(messages)
            messages.append(audit)
            audit_used = True
            instruction = (
                'Use the visual audit above to revise the successful program. '
                'Check that each proposed change has the stated image-space effect. '
                'Resolve contradictory suggestions conservatively. Implement at most '
                'three high-impact corrections and preserve already-correct groups. '
                'Return one complete Python program, or DONE / SELECT <step>.')
            messages.append({'role': 'user', 'content': instruction +
                f'\nSuccessful steps: {successful}. Remaining: {runtime.remaining()}'})
            continue

        if valid:
            if budget['executions'] > 0:
                instruction = (
                    'Compare the labeled images directly. In at most three code '
                    'comments identify reference-versus-render anchor discrepancies, '
                    'their likely causes, and expected effects of the corrections. '
                    'Check whether prior changes moved the anchors in the intended '
                    'direction; reduce or reverse an overshoot. Return a complete '
                    'corrected program, or DONE / SELECT <step>. Preserve good groups '
                    'and avoid unrelated changes. Do not spend a render on tiny detail.')
            else:
                instruction = 'Execution budget is exhausted. No further program can be executed.'
        else:
            instruction = (
                'EXECUTION FAILURE: no new usable reconstruction is available. '
                'Do not critique a nonexistent image. Repair the actual error and '
                'audit world initialization, fillet radii and unique include keys. '
                'After a timeout, substantially simplify repeated geometry. '
                'Return a compact complete corrected program if executions remain. '
                'DONE / SELECT is allowed only to retain an earlier successful build.')
        content = [{'type': 'text', 'text':
                    json.dumps(feedback, default=str) + '\n' + instruction +
                    f'\nSuccessful steps: {successful}. Remaining: {runtime.remaining()}'}]
        if valid:
            content.extend(_pair(runtime, task, result))
        messages.append({'role': 'user', 'content': content})

    # Keep the full conversation and label all eligible images together for review.
    budget = runtime.remaining()
    if len(successful) > 1 and budget['model_calls'] > 0 and budget['seconds'] > 30:
        content = [{'type': 'text', 'text':
                    'Execution is finished. Choose the strongest successful render '
                    'against the original reference. Judge camera, projected silhouettes, '
                    'occlusions, large color regions and visible object completeness. '
                    'An intended improvement is not evidence that it worked. Ignore '
                    'revision order and avoid preferring extra detail over alignment. '
                    f'Return only SELECT <step> from {successful}. '
                    'No program, tools, new renders or invented scores.\nORIGINAL REFERENCE:'},
                   runtime.image(task['image'])]
        for step in successful:
            content.extend([
                {'type': 'text', 'text': f'SUCCESSFUL STEP {step}:'},
                runtime.image(renders[step])])
        messages.append({'role': 'user', 'content': content})
        response = runtime.ask(messages)
        messages.append(response)
        choice = _chosen(_text(response), successful)
        if choice is not None:
            selected = choice
    if selected is not None:
        runtime.select(selected)
