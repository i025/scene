import ast
import json
from pathlib import Path
import re


PROCEDURE = '''
Shared reconstruction procedure:
Return a complete first build immediately, with a short planning ledger in code comments.
List every prominent object, including cropped foreground objects, its approximate normalized
image bounds, visible supports, silhouette-defining parts and occlusion order. Record 5-8
reference anchors distributed across foreground, subject and architecture, plus perspective
line directions and a camera hypothesis. These are visual estimates, not calibration.
Keep camera, major dimensions, placements, material palette and lighting parameters together.

Compact means economical representation, not missing surfaces or semantic parts. Establish
all major objects and their distinctive profiles in the first build. Allocate geometry to
visible changes in contour, thickness, curvature and negative space before small ornament.
Do not represent a broad shaped panel solely with a tubular outline; supply its filled body.
Do not substitute an oval for a visibly angular cushion or a constant-radius rail for a broad
shaped apron merely to reduce mesh count. Use short connected SceneAct assemblies to capture
such profiles. Match silhouette and projected proportions before surface microdetail.

Use a named Asset for each independently editable semantic object. Within it, group attached
subassemblies with their trim, inlays, panels and fixtures. Moving a rail should carry its own
attached edging; moving furniture should carry its frame, upholstery and supports. Separate
independent nearby objects into their own Assets even if they share a wall or material.
Use descriptive stable names, not names chosen to affect an evaluator's target ordering.
Before realize, inspect source membership against the object ledger, including nested groups.
A passing edit on a helper assembly does not certify a complete semantic object.
Print a compact inventory of top-level child names and descendant primitive counts, and the
whole-scene count: sum(n.solid is not None for n in scene.traverse()). Count expanded primitives,
not helper calls. Numeric primitive targets are unvalidated planning heuristics, not quality
criteria or hard limits. Remove repeated subpixel detail before simplifying major silhouettes.
Prefer simple assemblies to Boolean operations; use restrained shaders for surface patterns.

Implementation semantics to respect:
- include(name,node) replaces a child with that name. Use unique loop names. Attaching a node
  owned by a different parent clones it; use the returned node for subsequent attachment edits.
- fillet_box requires 0 < radius <= min(size)/2, including thickness. It emits up to 23 meshes.
  sweep_tube with N points emits N spheres and N-1 cylinders. Use rod for straight members;
  use enough distinct control points for visible curves, without dense ornamental sweeps.
- Dimensions, radii and coordinates must be finite; dimensions and radii must be positive.
  Rod endpoints must differ. Avoid empty groups in bounding-box calculations.
- Transform a complete group around an explicit meaningful pivot when preserving support or
  attachment matters. Default pivots are world AABB centers, not necessarily asset origins.
  AABB landmarks and support candidates do not establish true mesh contact or collision.
- realize clears Blender and its world. Create all bpy materials, camera and lights afterward.
  sc = bpy.context.scene
  if sc.world is None:
      sc.world = bpy.data.worlds.new('Ambient')
  sc.world.use_nodes = True
  Do not retain pre-realize bpy references.
- Geometry must use SceneAct. Do not create meshes or curves through bpy or change the library.

Material assignment and pattern coordinates:
SceneAct emits semantic attachment names on EMPTY markers; meshes retain primitive node names
such as Box, Ball and Rod. Searching mesh names for attachment labels can silently match nothing.
After realize, locate the intended semantic marker and traverse its descendants to find meshes.
For each targeted assignment, count matched meshes and assert the expected set is nonempty.
The compiler shares materials by exact RGBA finish. Copy a material before changing just one
object's appearance; changing a shared material affects all its users. Assign copied materials
only to intended descendants, preserving other objects. A palette match is appropriate only
when every user of that finish should receive the same treatment.
Generated coordinates normalize each primitive separately. Object texture coordinates without
an explicit reference object are also local to each mesh, not continuous world coordinates.
A scaled box can therefore stretch a supposedly small floor pattern over the entire floor.
For continuous patterns across an assembly, use a common existing semantic EMPTY as the explicit
ShaderNodeTexCoord.object and connect its Object output; account for that marker's transform.
Choose pattern spacing in that shared coordinate frame from visible repetition in the image.
Do not create geometry for fabric stitches or tiny floor seams. Keep floor seams restrained,
cloth patterns low contrast, and the large material color regions faithful to the reference.

Revision discipline:
Compare the reference and actual render using the anchor ledger, recording both approximate
positions and residual directions in code comments. Separate three questions:
1. Camera: do architecture and multiple independent objects show a coherent framing or
   perspective residual? Lens changes at fixed pose change framing; camera translation changes
   depth-dependent ratios. Neither alone proves the true camera. Do not fit only the main object
   while ignoring wall edges, foreground crops or background anchors.
2. Geometry: with a plausible camera, which local contours, projected dimensions, supports or
   occlusions remain wrong? Edit the entire relevant semantic group, or its complete subassembly.
   Scaling a helper rail is not a test of whole-object scale. Avoid global scaling for local shape.
3. Appearance: with camera and geometry fixed, compare large brightness/color regions, material
   assignment, texture scale, roughness and light direction. Verify shader targeting and coordinate
   semantics before compensating with color or light intensity. Avoid simultaneous large changes
   to albedo and illumination unless there is a specific explanation.
Choose the largest evidence-supported correction family per revision. Preserve matched anchors
and all ledger objects; document any necessary coupled change. Prefer essential silhouette
corrections to fine decoration. An unrendered rewrite has no demonstrated improvement.

Failures and budgets:
Five fresh CLI sessions, three Blender executions and 1200 seconds are hard limits. The external
logger counts actual model events; one session need not equal one observable turn. Work only
through the supplied controller. Do not use tools, other models, filesystem exploration or network.
Never render extra views, save files or modify the fixed renderer's engine, resolution, sampling
or resource settings. Noise alone is not a reason to change renderer settings.
On failure, use the actual exception/logs to repair the cause and audit the semantics above.
Missing output is failure; do not describe an unseen render. A timeout without stage logs does
not identify the stalled stage. Simplifying repeated detail is a conservative recovery option,
not proof that geometry caused the timeout. Preserve complete objects and supports when reducing
cost. DONE is allowed only after inspecting a successful render. SELECT <step> may choose only
one of the supplied successful rendered steps. In selection-only mode, generate no new code.
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
    # Read only this candidate's instruction file, not scene data or archives.
    prompt = (Path(__file__).parent / 'system.txt').read_text() + '\n' + PROCEDURE
    reference = runtime.image(task['image'])
    successful = {}
    latest_code = None
    latest_report = None
    last_visible = False
    calls = 0
    attempts = 0
    correction = ''

    def retain_last():
        if successful:
            runtime.select(next(reversed(successful)))

    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        can_execute = attempts < 3 and budget['executions'] > 0
        if not can_execute and len(successful) < 2:
            break

        # Reconstruct bounded context from observed artifacts. Do not repeatedly resend
        # all old programs and renderer logs. Keep the latest program and a valid fallback.
        content = [
            {'type': 'text', 'text':
             f"Reference: {task['width']} x {task['height']}. "
             f'Budget remaining: {budget}. Controller ask invocations: {calls}; '
             f'execution invocations: {attempts}. These are not inferred event counts.'},
            reference]
        if latest_code is not None and can_execute:
            content.append({'type': 'text', 'text':
                            'Latest attempted complete program:\n```python\n' + latest_code + '\n```'})
        if latest_report is not None:
            content.append({'type': 'text', 'text':
                            'Latest execution/output report:\n' + json.dumps(latest_report, default=str)})
        if successful and can_execute and not last_visible:
            step = next(reversed(successful))
            content.append({'type': 'text', 'text':
                            f'Last visibly successful fallback program, step {step}:\n```python\n' +
                            successful[step]['code'] + '\n```'})
        for step, artifact in successful.items():
            content.extend([
                {'type': 'text', 'text': f'Observed successful render, step {step}:'},
                artifact['image']])
        if correction:
            content.append({'type': 'text', 'text': correction})

        if not can_execute:
            instruction = (
                'SELECTION ONLY: no executions remain. Compare the supplied renders against the '
                'reference, considering framing, silhouettes, completeness and appearance. '
                'Do not assume later is better. Reply exactly SELECT <step> from '
                f'{list(successful)}. Do not generate code.')
        elif latest_report is None:
            instruction = (
                'Reconstruct the reference with an editable SceneAct hierarchy. Return one complete '
                'Python program now, with the compact object/anchor ledger in comments. '
                'Audit attachment, material targeting and texture-coordinate semantics.')
        elif last_visible:
            instruction = (
                'Review the observed render against the reference. In comments of a complete revised '
                'program, identify camera, local geometry and appearance residuals separately, choose '
                'the highest-priority correction and list anchors to preserve. Audit semantic group '
                'membership. Return one complete program, DONE, or SELECT <successful step>.')
        else:
            instruction = (
                'The latest attempt has no usable successful render. Diagnose only from its report. '
                'Repair the observed cause, retaining all major objects and complete edit groups. '
                'Return a complete program, or SELECT a supplied successful fallback. '
                'Do not score or claim improvement for missing output.')
        content.append({'type': 'text', 'text': instruction})
        response = runtime.ask([
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': content}])
        calls += 1
        text = _text(response).strip()
        choice = re.fullmatch(r'SELECT\s+(\d+)', text, re.I)
        if choice and int(choice.group(1)) in successful:
            runtime.select(int(choice.group(1)))
            return
        if text.upper() == 'DONE' and successful and can_execute:
            retain_last()
            return
        if not can_execute:
            correction = f'Selection response was invalid. Reply exactly SELECT <step> from {list(successful)}.'
            continue

        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S | re.I)
        if len(blocks) != 1:
            correction = ('Return exactly one complete program in one python code block. '
                          f'Eligible successful steps: {list(successful)}. '
                          'DONE requires an observed successful render.')
            continue
        code = blocks[0]
        try:
            ast.parse(code)
        except SyntaxError as exc:
            correction = ('Syntax failure before Blender execution: ' + str(exc) +
                          '\nCorrect this unexecuted program and return it in full:\n```python\n' +
                          code + '\n```\nNo Blender execution was consumed.')
            continue
        budget = runtime.remaining()
        if budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        latest_code = code
        correction = ''
        attempts += 1
        try:
            result = runtime.execute(code)
        except Exception as exc:
            result = {'ok': False, 'error': f'{type(exc).__name__}: {exc}',
                      'output_failure': 'Execution interface raised; stage and artifact availability unknown.'}
        if not isinstance(result, dict):
            result = {'ok': False, 'error': 'Execution returned no structured output report.'}
        latest_report = {k: v for k, v in result.items() if k != 'image'}
        last_visible = False
        step = result.get('step')
        if result.get('ok') and result.get('image') and type(step) is int:
            try:
                rendered_image = runtime.image(result['image'])
                if rendered_image is None:
                    raise ValueError('Image interface returned no image')
            except Exception as exc:
                latest_report['output_failure'] = f'Cannot obtain rendered image: {type(exc).__name__}: {exc}'
            else:
                successful[step] = {'image': rendered_image, 'code': code}
                last_visible = True
        if not last_visible:
            latest_report['usable_render'] = False
            latest_report.setdefault('output_failure', 'No successful image with a selectable step was returned.')
        else:
            latest_report['usable_render'] = True
    retain_last()
