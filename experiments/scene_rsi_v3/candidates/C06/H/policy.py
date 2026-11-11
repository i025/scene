import json
from pathlib import Path
import re


PROJECTION_GUIDANCE = '''
Use a small numerical projection check before committing camera changes. Choose a few
explicit world-space landmarks corresponding to reference points you can actually identify:
for example a window corner, a furniture top corner and a foreground contour endpoint.
Record reference estimates separately from computed projections. Use points on geometry,
not an EMPTY's origin or a whole-room bounding box. Include foreground and background.
After realize and set_view, update Blender's view layer. For a world point p, project using:
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
Use the original image aspect for these calculations and the final camera. Coordinates
are x right and y down. Print a compact reference-versus-projected landmark table in
execution output. This requires no render. Projection checks do not establish visibility,
silhouette, material appearance or correct hidden geometry.
When changing camera aim, position or lens, compute the same landmark projections before
and after a small trial change to verify the direction rather than guessing. Restore a
trial that moves the selected landmarks the wrong way. With a fixed camera position,
aiming upward generally moves stationary scene features downward in the image. Lens
changes scale positions about the principal point; moving the camera changes foreground
and background differently. Do not compensate a local dimension or placement error by
moving every matching background feature. Keep this check small: a few landmarks and
candidate parameter adjustments, not a large search. Do not force uncertain point
correspondences or optimize hidden bounds. The complete rendered view remains the final
check of crops, occlusions, silhouettes and broad appearance.

Apply this same acceptance check to major geometry translations, rotations and rescaling.
For each such edit, identify both the feature needing correction and an already matching
feature to protect. Use corresponding explicit points on the affected geometry, transformed
by the actual proposed pivot, scale and translation. For example, increasing height about
the base leaves the base fixed and moves the top; it does not extend the bottom downward.
If the top should stay fixed while the bottom moves, choose the pivot or component edit
accordingly and check both endpoints. Preserve support and overlap relationships.
A trial establishing the right direction does not establish the right final magnitude.
Before committing the final parameters, compare baseline and final projections against the
same reference estimates and print which anchors improve or worsen. Reduce or restore an
edit that overshoots or damages a protected anchor without a stronger image-supported
reason. Do not merely print discrepancies and then ignore them. Use approximate tolerance
appropriate to the uncertainty of each correspondence, not exact fitting to guessed pixels.
For a cropped object, the image-border intersection is not its hidden physical corner;
record the crop constraint separately and do not force an off-screen corner onto the border.
These checks remain small and render-free; verify visible contours with the complete render.
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
                    'move and in what direction. Verify camera and major geometry changes with '
                    'the small numerical projection check before the next render. Compare both '
                    'the baseline and the final proposed magnitude, including an already matching '
                    'anchor to protect; reduce or restore unsupported overshoots. Keep computed '
                    'point projections distinct from observed visible contours. '
                    'A common translation, scale error, or edge-slope '
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
