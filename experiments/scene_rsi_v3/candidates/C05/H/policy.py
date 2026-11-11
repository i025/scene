import json
from pathlib import Path
import re


PROJECTION_GUIDANCE = '''
Before the runner renders, use a small numerical projection check to catch obvious
framing and placement errors in the scene you have actually built. Choose a few
explicit world-space points on identifiable geometry, distributed across the main
subject, background and cropped foreground. Record their reference estimates
separately from computed projections. An EMPTY origin or a room bounding box is
not a corresponding visible landmark. Use the original image aspect throughout.
After realize and set_view, update Blender's view layer and project each point:
    from mathutils import Vector
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
Coordinates are x right and y down. Print a compact reference-versus-projected
landmark table in execution output. Projection does not establish visibility,
silhouette, material appearance or correct hidden geometry.

Make this check useful within the current execution, including the first build:
if a confidently identified visible point is far outside its estimated region,
make a small supported correction before returning control to the runner. Do not
merely print a large known discrepancy and defer it to the next execution.
For partially cropped objects, identify an actual visible corner or the contour
entering the frame; do not require the entire object to fit inside the image.
For a surface, label which corner is being compared: its near edge, far edge,
and silhouette's topmost point are generally different image coordinates.

Keep the check small: an initial projection and at most a few interpretable
candidate changes, not a large search or an attempt to solve hidden geometry.
Hold geometry fixed when testing camera changes. Compare the same points before
and after each trial. A common displacement or scale error across independent
objects may justify a camera change; a local discrepancy with a matching
background favors changing the object's placement or dimensions. Neither pattern
uniquely identifies the cause. With a fixed camera position, aiming upward usually
moves stationary features downward. Lens changes scale about the principal point;
camera translation affects foreground and background differently.

Inspect each landmark's change, not only a summed error. Before accepting a trial,
check that already matching background anchors remain close and that reference-
visible foreground parts have not been pushed entirely out of frame. Restore or
reduce a trial that creates such a regression even if the aggregate error falls.
If geometry is changed afterward, recompute affected points from its final
parameters rather than retaining stale world coordinates. Print final projections
for the actual active camera after all accepted edits. If a correspondence is
uncertain or inconsistent with the other anchors, report that uncertainty instead
of forcing it to match. The complete rendered view remains the final check of
crops, overlaps, silhouettes and broad appearance.
'''


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    guidance = (
        '\nBefore writing the complete program, choose a small set of visible image anchors '
        'distributed across foreground, main subject and background. Record their approximate '
        'normalized positions or bounds in program comments, together with a few dominant edge '
        'directions and overlaps. Use the original image aspect throughout. These are visual '
        'estimates, not ground-truth calibration. Parameterize camera pose, target and lens '
        'separately from major asset dimensions and positions. Prioritize the contours and '
        'large light/dark regions that occupy the image; fine detail cannot repair incorrect '
        'framing or a wrong silhouette.'
    )
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': [
        {'type': 'text', 'text': 'Reconstruct this RGB image. Match its camera and framing. ' +
         f"Image dimensions: {task['width']} x {task['height']}. Budget: {runtime.remaining()}" + guidance + PROJECTION_GUIDANCE},
        runtime.image(task['image'])]}]
    while runtime.remaining()['model_calls'] > 0 and runtime.remaining()['seconds'] > 0:
        response = runtime.ask(messages)
        messages.append(response)
        text = response['content'] or ''
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if not blocks:
            if text.strip().upper() == 'DONE':
                return
            messages.append({'role': 'user', 'content': 'Return one complete program in a python code block, or DONE.'})
            continue
        if runtime.remaining()['executions'] <= 0:
            return
        result = runtime.execute(blocks[-1])
        content = [{'type': 'text', 'text': json.dumps({k: v for k, v in result.items() if k != 'image'})}]
        if result.get('image'):
            content.extend([
                {'type': 'text', 'text': 'Original reference, unchanged:'},
                runtime.image(task['image']),
                {'type': 'text', 'text': 'Current complete rendered camera view:'},
                runtime.image(result['image']),
                {'type': 'text', 'text': (
                    'Compare these two images directly. In brief comments before any revised code, '
                    'record reference versus rendered estimates for several of your anchors, '
                    'including at least one background and one foreground feature. Check crops, '
                    'edge slopes, overlaps, silhouette and internal gaps. Do not simply repeat '
                    'the intended reference bounds as if the render achieved them. Rank the '
                    'largest discrepancies by visible extent and contrast. For each proposed '
                    'correction, name the parameter and predict which anchors or contours will '
                    'move and in what direction. Verify camera-change directions with the small '
                    'numerical projection check before the next render; keep computed point '
                    'projections distinct from observed visible contours. '
                    'Inspect per-anchor regressions and foreground crops before accepting a '
                    'camera trial; lower total landmark error alone is insufficient. Recompute '
                    'the final projections after geometry edits, using points derived from the '
                    'final geometry parameters. A common translation, scale error, or edge-slope '
                    'error may suggest camera changes; inconsistent errors may require asset '
                    'placement or proportion changes. Check multiple anchors before choosing, '
                    'and preserve already matching regions. If bounds mostly agree, inspect '
                    'the actual surface profile, component proportions, negative spaces, '
                    'and broad light/dark distribution instead of adding repeated tiny parts. '
                    'Distinguish observed brightness from material color: illumination and '
                    'surface orientation also affect it. Make only image-supported corrections '
                    'in a complete revised program, or reply DONE. '
                ) + f'Remaining: {runtime.remaining()}'}
            ])
        else:
            content.append({'type': 'text', 'text': (
                'No rendered image is available. Repair the reported execution failure using '
                'the actual error evidence; do not infer visual defects from this failure. '
                'Return a complete corrected program if an execution remains, or DONE. '
            ) + f'Remaining: {runtime.remaining()}'})
        messages.append({'role': 'user', 'content': content})
