import ast
import json
from pathlib import Path
import re


GUIDANCE = '''
Execution reliability and reconstruction procedure:
Produce a compact, complete first reconstruction immediately. Roughly 180 lines and
250 expanded primitive meshes are planning targets, not resource limits. Include
visible architecture and major objects with separate materials and meaningful Asset
owners. Simplify distant details before sacrificing foreground silhouettes or openings.
Do not change the fixed renderer, engine, sampling, resolution or resource settings.
The runner renders once; do not render or save files yourself.

Before coding, write at most six short comments containing:
- Reference anchors in normalized image coordinates, estimated visually: perspective
  convergence, floor and ceiling boundaries, near and far object bounds, and a salient
  opening or occlusion. Include anchors at multiple depths and on both sides of view.
- The principal semantic owners, visible component inventory and supporting surfaces.
Keep camera position, orientation, lens and major dimensions in named parameters.
Anchor estimates are hypotheses, not measured calibration or ground truth.

Known API requirements:
- realize(scene) clears Blender. Create camera, lights and world and customize Blender
  materials afterward. Keep geometry and relationships in SceneAct; do not redefine
  constructors, generate meshes by another route or modify the backend.
- Before accessing world nodes, use:
  sc = bpy.context.scene
  if sc.world is None:
      sc.world = bpy.data.worlds.new('Ambient')
  sc.world.use_nodes = True
- Dimensions and radii must be finite and positive. fillet_box requires radius <= half
  the SMALLEST size component, including thickness. Prefer box for thin panels.
- Each include key must be unique within its parent: reusing a key REPLACES a child.
  Include all relevant loop indices. Attaching an already-owned node may clone it;
  use the node returned by include when further edits must affect that attachment.
- Rod endpoints must differ; camera position and target must differ. sweep_tube
  creates one rod per segment and one sphere per point. fillet_box expands into many
  meshes. Count expanded repetitions, not just Python calls. Avoid dense lettering,
  tube samples and repeated ornament; use simple procedural materials for patterns.
- Do not access files, network, subprocesses, tools or other models from the program.

Editable ownership and material targeting:
Keep attached components under their complete semantic owner, including supports,
hardware and trim that should move together. Keep separate movable objects separate.
Move or resize the owner, preserving relative transforms; choose an explicit support
pivot when resizing should preserve contact. Do not scale an arbitrary selected child
as a substitute for resizing the object. Review bindings that could undo a later move.
Derive placement from the actual supporting surface, such as a shelf panel top, not
from the whole owner's AABB top. Bounds alone do not establish contact or collision.

SceneAct creates EMPTY markers using include slots but primitive meshes have generic
names such as Box and Rod. Do not look for semantic slot names in mesh.name or infer
identity from numeric suffixes. For custom shaders, use globally unique semantic slot
names for the intended parts and resolve their marker and mesh descendants after
realize. Check that the intended target exists and has mesh descendants. Ambiguous
mappings remain unknown; never fall back to matching similar colors or all materials.
Equal SceneAct finishes can share Blender materials. For a local shader change, copy
only the targeted material slots before editing their nodes; preserve non-target
materials, geometry, matrices and parents. Do not replace all finishes in an owner
when only one component needs a change. Initial global defaults may be deliberate,
but local corrections must have explicit scope. Do not globally rename or regroup
objects merely to obtain a convenient target.

Review after each successful render:
Compare the SAME reference anchors to the actual render, including near and far
bounds, floor/ceiling edges, perspective convergence and foreground crops. Write at
most three short comments in the next program: observed mismatch, hypothesized
parameter family, and predicted effect on at least two anchors. Preserve anchors
already matching. Rank discrepancies by visible area and structural importance.

First resolve camera versus geometry. Orientation affects convergence and slopes;
focal length changes framing about the optical center; camera translation changes
relative near/far sizes and occlusions. These are planning heuristics, not proof of a
cause. A single vanishing point or one object bound cannot determine the camera.
If architecture agrees but one object does not, inspect its complete owner dimensions
and placement before changing the camera. Avoid compensating for camera error with
independent movement of many unrelated components. Prefer one coherent parameter
family per revision; change a second only when independently supported by anchors.
Do not alter camera, repeated spacing, local dimensions and lighting simultaneously
without explaining their separate evidence. No fixed lens, scale or scene template.

For missing items, inspect construction and unique include slots first, then cropping,
occluders, depth ordering and contrast. Duplicate only if the inventory establishes
an omission. Preserve actual openings; solid placeholder bodies must not fill visible
interiors. Repetition should follow observed spacing and depth, with detail reduced
as projected size shrinks, rather than a uniformly detailed arbitrary count.

For appearance, compare broad regions and light/shadow placement. Rendered brightness
is not albedo. If many unrelated regions disagree similarly, inspect illumination or
exposure before recoloring them all. If only one surface disagrees, target that surface.
Do not simultaneously darken all materials, reduce every light and change exposure
based on one brightness impression. Do not chase render noise with extra geometry or
by changing fixed render settings. Tiny decoration comes after framing and proportions.

Evidence discipline and recovery:
Execution status, supplied metrics and functional checks are reported facts. Visual
anchor estimates are hypotheses. Historical heuristics are not scene measurements.
Controlled probe deltas, if supplied, describe sensitivity only for their actual
intervention and selected descendants; they do not establish cause or a universal
correction factor. Passing an edit test does not prove semantic completeness or
support. Partial object listings cannot certify omitted dependencies.
After failure or a missing output image, there is no new usable view to critique.
Repair the reported error and audit world initialization, primitive bounds and naming.
After timeout, substantially simplify repeated geometry and material variation.
Never invent numerical similarity scores or infer success from log text alone.

Return exactly one complete Python code block for a build or revision. After a valid
build, DONE retains the latest successful build; SELECT <step> retains a supplied
successful step. Do not assume the latest revision is best. All work uses only this
conversation and the supplied interfaces. No independent rendering or exploration.
'''


REVIEW = '''
Compare this actual render with the original reference using the same multi-depth
anchors. Identify the largest remaining discrepancy and any regressions. Separate
observations from hypotheses; review camera before local scale, construction before
omission, and explicit surface targeting before material changes. Preserve working
owners and non-target state. Return one complete revised program with at most three
short evidence/prediction comments, or DONE, or SELECT <successful step>. Spend a
remaining execution on a substantial correction, not tiny ornament.
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


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt + '\n' + GUIDANCE},
        {'role': 'user', 'content': [
            {'type': 'text', 'text':
             'Reconstruct this RGB image with an editable SceneAct scene. '
             'Deliver a compact complete first build, leaving time for correction. '
             'Record multi-depth anchors and semantic ownership in brief code comments. '
             f"Image dimensions: {task['width']} x {task['height']}. "
             f'Available budget: {runtime.remaining()}'},
            runtime.image(task['image'])]}]
    successful = []
    selected = None

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
                'DONE or SELECT <successful step> is permitted only after success. '
                f'Successful steps: {successful}. Remaining: {runtime.remaining()}'})
            continue
        code = blocks[0]
        try:
            ast.parse(code)
        except SyntaxError as error:
            messages.append({'role': 'user', 'content':
                f'Python syntax failure before execution: line {error.lineno}: '
                f'{error.msg}. No Blender execution or new render occurred. '
                'Return a complete corrected program. '
                f'Successful steps: {successful}. Remaining: {runtime.remaining()}'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        result = runtime.execute(code)
        valid = bool(result.get('ok') and result.get('image')
                     and result.get('step') is not None)
        if valid:
            selected = result['step']
            successful.append(selected)
            runtime.select(selected)
            instruction = 'This build succeeded.\n' + REVIEW
        else:
            instruction = (
                'EXECUTION/OUTPUT FAILURE: no usable new reconstruction is established. '
                'Do not critique a nonexistent rendering. Repair the reported error; '
                'audit world initialization, primitive bounds and unique include keys. '
                'If the build timed out, reduce repeated geometry substantially. '
                'If output is missing despite ok status, treat it as output failure, '
                'not visual evidence. Return a compact complete corrected program, '
                'or retain an earlier successful step if one exists.')
            if selected is not None:
                runtime.select(selected)
        budget = runtime.remaining()
        if valid and budget['executions'] <= 0:
            instruction = (
                'This build succeeded. No executions remain. Review this render '
                'against the original and earlier successful renders; do not write '
                'another program. A selection request follows if budget permits.')
        feedback = {k: v for k, v in result.items() if k != 'image'}
        content = [{'type': 'text', 'text':
                    json.dumps(feedback, default=str) + '\n' + instruction +
                    f'\nSuccessful steps: {successful}. Remaining: {budget}'}]
        if valid:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})

    # Review only real alternatives; never request unexecutable code.
    budget = runtime.remaining()
    if len(successful) > 1 and budget['model_calls'] > 0 and budget['seconds'] > 30:
        messages.append({'role': 'user', 'content':
            'Execution is finished. Compare the actual successful renders against '
            'the original reference. Prioritize agreement across near/far bounds, '
            'architectural perspective, openings, silhouettes and large color regions. '
            'Check whether later local fixes damaged previously matching anchors. '
            'Do not assume the latest is best or invent scores. '
            f'Return only SELECT <step> from {successful}. No code or new renders.'})
        response = runtime.ask(messages)
        messages.append(response)
        choice = _chosen(_text(response), successful)
        if choice is not None:
            selected = choice
    if selected is not None:
        runtime.select(selected)
