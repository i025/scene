import json
from pathlib import Path
import re


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
        'framing or a wrong silhouette. '
        '\nMake these anchors operational in the complete program: choose four to eight '
        'explicit world-space points on identifiable visible geometry, such as room corners, '
        'board corners, a foreground tabletop corner or a fixture endpoint. Associate each '
        'with its estimated reference image coordinate (x right, y down, both normalized). '
        'Use points with clear correspondence; a group origin or world AABB corner is not '
        'automatically a visible feature. After realize and camera setup, update the view '
        'layer and project these points numerically using the actual camera matrix. '
        'camera.calc_matrix_camera(depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT, '
        'scale_x=1, scale_y=1) preserves the supplied image aspect without changing runner '
        'render settings. Multiply by camera.matrix_world.inverted() and each homogeneous '
        'world point; for positive clip.w, normalized coordinates are '
        '(.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w)). Flag points behind the camera. '
        'Print one compact JSON table of anchor name, estimated reference coordinate, '
        'computed projection and residual. This is a geometry diagnostic, not a visibility '
        'test or image score. '
        'Before finalizing the program, use these projections to check framing and any '
        'predicted camera correction. If needed, evaluate a few small camera parameter '
        'perturbations numerically without rendering; compare their effects across anchors '
        'at different depths. Keep asset geometry fixed during that comparison, and restore '
        'the chosen camera before completion. Do not force uncertain anchors to exact '
        'agreement or deform the scene to fit incompatible estimates. A camera change '
        'should explain several residuals while preserving matching anchors. Local residuals '
        'may instead require asset placement or proportions. No extra renders, files or '
        'external calls are needed for this check.'
    )
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': [
        {'type': 'text', 'text': 'Reconstruct this RGB image. Match its camera and framing. ' +
         f"Image dimensions: {task['width']} x {task['height']}. Budget: {runtime.remaining()}" + guidance},
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
                    'move and in what direction. A common translation, scale error, or edge-slope '
                    'error may suggest camera changes; inconsistent errors may require asset '
                    'placement or proportion changes. Check multiple anchors before choosing, '
                    'and preserve already matching regions. '
                    'Compare the printed numerical anchor projections with the actual rendered '
                    'features. If they disagree, check correspondence, occlusion and matrix '
                    'updates rather than treating the diagnostic as visible pixel coverage. '
                    'In a revision, retain the reference estimates and print updated projections; '
                    'verify the sign and magnitude of camera changes numerically before rendering. '
                    'Explicitly check any inventory feature absent from the image for off-frame '
                    'placement or occlusion before adding a duplicate. '
                    'If bounds mostly agree, inspect '
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
