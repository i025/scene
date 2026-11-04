import ast
import json
from pathlib import Path
import re


PROCEDURE = '''
Shared reconstruction procedure:
Produce a compact, complete first build immediately; do not spend a separate turn on planning.
In brief code comments record the dominant silhouettes, approximate normalized image bounds,
main perspective directions, occlusion order, and camera hypothesis. These are estimates,
not measured calibration. Put camera, major dimensions and placement parameters together.
First establish architecture, every prominent object, essential supports, large color regions,
and a plausible camera. Keep semantic objects as named Assets with all their constituent
parts inside them. Preserve separate meshes and editable material assignments.

Reliability requirements derived from the actual SceneAct implementation:
- include(name,node) REPLACES an existing child with that name. Use unique indexed names
  inside loops. Include the returned node if subsequently editing an attachment that was cloned.
- fillet_box requires 0 < radius <= min(size)/2, INCLUDING thickness. Choose a valid radius
  explicitly; do not alter the library. It emits up to 23 primitive meshes per call.
- sweep_tube with N points emits N spheres and N-1 cylinders. Use few control points;
  adjacent points must differ. Use rod for straight members. Avoid dense ornamental sweeps.
- All dimensions and coordinates must be finite; dimensions and radii must be positive.
- realize clears Blender, including its world. After realize, before accessing world nodes:
  sc = bpy.context.scene
  if sc.world is None:
      sc.world = bpy.data.worlds.new('Ambient')
  sc.world.use_nodes = True
  Then configure Background, camera and lighting. Do not retain pre-realize bpy references.
- All geometry must use SceneAct. bpy is for materials, lighting and camera customization;
  do not bypass the geometry interface with direct mesh or curve creation.

Count expanded primitives, not helper calls. Aim for roughly 200-350 meshes initially and
keep revisions below roughly 500 unless essential visible structure requires more. These are
planning targets, not reasons to omit major objects or supports. Avoid thousands of floor
boards, fabric stitches or repeated tiny marks; use restrained procedural materials for
surface patterns. Use a small reusable material palette. Prefer simple assemblies over
Boolean operations. Before realize, print the actual primitive count using
sum(n.solid is not None for n in scene.traverse()). Never render additional views, save files,
or change the fixed runner's resolution, engine, sampling or other resource settings.

After a successful rendering, compare it with the original using 5-8 stable visible anchors:
major object extremes, wall/floor intersections and distinctive foreground/background points.
Distinguish global perspective/framing errors from local object size or placement errors.
Correct camera using scene-wide evidence; change individual objects only for local residuals.
Keep camera fixed when revising material/light appearance. Prefer one coherent correction
family per revision, preserving already matched anchors. Do not add fine detail while major
silhouettes, occlusion, framing or brightness remain wrong. Never infer improvement without
an actual render. A noisy render alone does not authorize changing fixed renderer settings.

On execution failure, there is no rendered view to compare. Repair the reported cause and
audit the other reliability requirements before returning a complete replacement. On timeout,
substantially simplify repeated surface detail and primitive expansion while retaining major
objects and semantic groups. With little time or the final execution, prioritize a valid,
compact scene over ornament. DONE is allowed only after a successful visible render.
The controller may request SELECT <step> to retain a previously successful rendered build.
Only the supplied successful step numbers are eligible; never select unexecuted code.
'''


def _text(response):
    content = response.get('content') or ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(x.get('text', '') for x in content
                         if isinstance(x, dict) and x.get('type') == 'text')
    return ''


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text() + '\n' + PROCEDURE
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text':
             'Reconstruct this RGB image with an editable SceneAct hierarchy. Match camera and framing. '
             f"Image dimensions: {task['width']} x {task['height']}. "
             f'Budget: {runtime.remaining()}. Return one complete Python program now.'},
            runtime.image(task['image'])]}]
    successful = {}
    attempts = 0
    calls = 0
    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            return
        can_execute = attempts < 3 and budget['executions'] > 0
        if not can_execute:
            # No useful code-generation call remains. Review only when rollback is possible.
            if len(successful) < 2:
                return
            content = [{'type': 'text', 'text':
                        'No executions remain. Compare these successful builds against the original. '
                        'Choose the strongest overall camera, geometry, appearance and editable structure. '
                        'Reply exactly SELECT <step>. Do not generate code.'}]
            for step, path in successful.items():
                content.extend([{'type': 'text', 'text': f'Successful step {step}'},
                                runtime.image(path)])
            messages.append({'role': 'user', 'content': content})
        response = runtime.ask(messages)
        calls += 1
        messages.append(response)
        text = _text(response).strip()
        choice = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
        if choice and int(choice.group(1)) in successful:
            runtime.select(int(choice.group(1)))
            return
        if not can_execute:
            return
        if text.upper() == 'DONE' and successful:
            return
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S | re.I)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content':
                             'Return exactly one complete program in a python code block. '
                             'No valid build exists yet.' if not successful else
                             'Return exactly one complete program, DONE, or SELECT <successful step>.'})
            continue
        code = blocks[0]
        try:
            ast.parse(code)
        except SyntaxError as exc:
            messages.append({'role': 'user', 'content':
                             f'Python syntax failure before Blender execution: {exc}. '
                             'Return a corrected complete program. No execution was consumed.'})
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            return
        attempts += 1
        result = runtime.execute(code)
        visible_success = bool(result.get('ok') and result.get('image'))
        if visible_success and isinstance(result.get('step'), int):
            successful[result['step']] = result['image']
        report = {k: v for k, v in result.items() if k != 'image'}
        if visible_success:
            instruction = (
                'Compare this render to the original. Identify the largest coherent mismatch, '
                'then return a complete revised program, DONE, or SELECT <successful step>. '
                'Preserve complete semantic groups and already matched features.')
        else:
            instruction = (
                'Execution/output failure: no usable successful render is available for this attempt. '
                'Do not describe or score an unseen image. Repair the error and audit all reliability '
                'requirements. For timeout, reduce expanded primitive count and surface detail sharply. '
                'Return a compact complete program if executions remain.')
        content = [{'type': 'text', 'text': json.dumps(report, default=str) + '\n' + instruction +
                    f'\nSuccessful steps: {list(successful)}. Remaining: {runtime.remaining()}'}]
        if visible_success:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
