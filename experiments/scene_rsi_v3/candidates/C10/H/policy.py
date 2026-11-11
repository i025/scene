import json
from pathlib import Path
import re


PROJECTION_GUIDANCE = '''
Use a small numerical projection check before committing camera or major geometry changes.
Choose a few explicit world-space landmarks corresponding to reference points you can
actually identify, distributed across foreground, main subject and background. Use points
on geometry, not an EMPTY's origin or a whole-room bounding box. Record reference estimates
separately from computed projections. Keep each reference point's identity and estimate
stable across revisions. If you correct an estimate or change correspondence, explain why;
never move the reference estimate merely to make the current reconstruction appear closer.
A feature cropped by an image boundary supplies a crop constraint, not an exact location
for an unseen physical corner. Mark uncertain correspondences and do not fit them tightly.

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
Use the original image aspect throughout. Coordinates are x right and y down.
Projection checks do not establish visibility, silhouette, material appearance or correct
hidden geometry. The complete rendered view remains the final check.

Make the projection check affect the chosen parameters, rather than merely printing a
report after choosing them. Before revising a major asset or camera, identify which anchors
should improve and which already matching anchors should remain stable. For the same
landmarks, compare the previous state, a small trial and the proposed final state. Recompute
world points after geometry transformations, including the actual scale pivot and offsets.
Check both ends of an affected contour: increasing height about its base primarily moves
its top, while preserving the top requires a different pivot or compensating translation.
A trial moving in the correct direction does not justify an arbitrarily larger final step.
Check the final step for overshoot and regressions before committing it.

For confidently matched points, print reference, previous projection, candidate projection
and residuals in original-image pixels. Use this small table to shorten, revise or restore
an edit that overshoots or damages a protected anchor. If a tradeoff is necessary, state
which visible discrepancy takes priority and why. Do not require every uncertain landmark
to improve and do not run a large search. Keep reference estimates, computed points and
observed rendered contours distinct. A known numerical regression must not be described
as preserving a matching feature.

With a fixed camera position, aiming upward generally moves stationary scene features
downward in the image. Lens changes scale positions about the principal point; moving the
camera changes foreground and background differently. Do not compensate a local dimension
or placement error by moving every matching background feature. Retain the full scene and
original author-view aspect when checking crops, occlusions and broad appearance.
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
                    'the intended reference bounds as if the render achieved them. Keep the '
                    'reference correspondences stable; explain any corrected estimate. '
                    'Rank the largest discrepancies by visible extent and contrast. For each '
                    'proposed correction, name its parameter, predict the direction of movement '
                    'and name an already matching anchor to protect. In the revised program, '
                    'compare previous and final candidate projections for the same points before '
                    'committing camera or major geometry changes. Include geometry scale pivots '
                    'and translations in this check. A correct small-trial direction alone is '
                    'insufficient: shorten or revise a final step that overshoots or damages '
                    'protected anchors, and explain any necessary tradeoff. '
                    'A common translation, scale error or edge-slope error may suggest camera '
                    'changes; inconsistent errors may require asset placement or proportion '
                    'changes. Check multiple anchors before choosing and preserve matching '
                    'regions. If bounds mostly agree, inspect surface profile, component '
                    'proportions, negative spaces and broad light/dark distribution instead '
                    'of adding repeated tiny parts. Distinguish observed brightness from '
                    'material color: illumination and surface orientation also affect it. '
                    'Computed projections are not observed visible contours. Make only '
                    'image-supported corrections in a complete revised program, or reply DONE. '
                ) + f'Remaining: {runtime.remaining()}'}
            ])
        else:
            content.append({'type': 'text', 'text': (
                'No rendered image is available. Repair the reported execution failure using '
                'the actual error evidence; do not infer visual defects from this failure. '
                'Return a complete corrected program if an execution remains, or DONE. '
            ) + f'Remaining: {runtime.remaining()}'})
        messages.append({'role': 'user', 'content': content})
