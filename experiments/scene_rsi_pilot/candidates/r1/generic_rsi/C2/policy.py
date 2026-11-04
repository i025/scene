import json
import re
from pathlib import Path


FIRST_BUILD = (
    'Produce a complete economical scene, including cropped foreground objects and major '
    'occluders. In short code comments list visible assemblies, approximate normalized '
    'landmarks, important filled regions versus openings, and uncertain proportions. '
    'Keep camera, dimensions, placements and broad lighting explicit. Budget expanded '
    'primitive counts: sweep_tube creates a rod per segment and a ball per point; '
    'fillet_box creates many meshes. Initially aim for a few hundred emitted meshes, '
    'using short paths and procedural surface patterns. This is a planning target, not '
    'permission to omit important objects or merge meaningful parts. Solid panels must '
    'be represented by surfaces, not only outline tubes. Audit the supplied API checks. '
    'Return one complete runnable Python program in one python code block.'
)

REVISION = (
    'Compare the actual render with the reference. First assess framing, object coverage, '
    'silhouette, occlusion and broad tone, in that order, before fine detail. In brief '
    'code comments record approximate reference/render coordinates for a few stable '
    'landmarks, the largest supported error, the proposed parameter family, expected '
    'image movement, and two already matching regions to preserve. These are visual '
    'estimates, not measured calibration. Choose a coherent correction: camera pose '
    'for scene-wide slope/displacement errors, framing for coherent occupancy errors, '
    'or local shape/placement for isolated errors. A wrong opening or filled region '
    'requires geometry, not zoom. Do not simultaneously compensate focal length, '
    'camera distance and object scale for the same discrepancy. Keep the revision '
    'narrow and do not add decorative mesh loops. Preserve all semantic assemblies '
    'and plausible support. Return a complete program or SELECT an observed successful '
    'step if no supported improvement is worth the remaining time.'
)


def solve(task, runtime):
    prompt = (Path(__file__).parent / 'system.txt').read_text()
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': (
                'Reconstruct this RGB image. Match camera, framing, occlusions and major '
                f"color regions. Image dimensions: {task['width']} x {task['height']}. "
                f'Budget: {runtime.remaining()}. ' + FIRST_BUILD
            )},
            runtime.image(task['image'])
        ]}
    ]
    successful = []
    calls = 0
    executions = 0
    ask_costs = []
    build_costs = []
    last_failure = None

    def elapsed(before, after):
        return max(0.0, float(before['seconds']) - float(after['seconds']))

    while calls < 5:
        budget = runtime.remaining()
        if budget['model_calls'] <= 0 or budget['seconds'] <= 0:
            break
        slots = executions < 3 and budget['executions'] > 0
        # Use complete execute wall time, not the renderer's internal timing line.
        ask_reserve = max(ask_costs, default=120.0)
        build_reserve = 1.25 * max(build_costs, default=60.0)
        revision_reserve = ask_reserve + build_reserve + 20.0
        review_only = bool(successful) and (
            not slots or budget['seconds'] < revision_reserve
        )
        if not slots and not successful:
            break
        if review_only:
            messages.append({'role': 'user', 'content': (
                'Selection only: an execution slot or a conservative time reserve for '
                'another complete revision is unavailable. Do not generate code. '
                f'Successful observed steps: {successful}. Reply SELECT n for the best '
                'render against the reference, prioritizing framing, coverage, silhouette, '
                'occlusion and broad tones. Do not select a failed or unseen attempt. '
                f'Remaining: {budget}. Estimated revision reserve: {revision_reserve:.1f}s.'
            )})
        elif last_failure:
            messages.append({'role': 'user', 'content': (
                'The preceding attempt failed. Repair the reported cause throughout the '
                'complete program. For a timeout, simplify repeated geometry and long '
                'paths while retaining major silhouettes and assemblies; do not merely '
                'resubmit the same expensive scene. For API errors, preserve composition '
                'and audit related calls. Missing required output is failure, not a '
                f'visual result. Remaining: {budget}.'
            )})
        before = runtime.remaining()
        response = runtime.ask(messages)
        calls += 1
        ask_costs.append(elapsed(before, runtime.remaining()))
        messages.append(response)
        text = response.get('content') or ''
        if not isinstance(text, str):
            text = ''
        selection = re.fullmatch(r'SELECT\s+(\d+)\s*', text.strip(), re.I)
        if selection and int(selection.group(1)) in successful:
            runtime.select(int(selection.group(1)))
            return
        if text.strip().upper() == 'DONE' and successful:
            runtime.select(successful[-1])
            return
        if review_only:
            messages.append({'role': 'user', 'content': (
                f'Reply exactly SELECT n with n in {successful}. No further build is admitted.'
            )})
            continue
        blocks = re.findall(r'```python\s*\n(.*?)```', text, re.S)
        if len(blocks) != 1:
            messages.append({'role': 'user', 'content': (
                'Return exactly one complete program in one python code block, or SELECT '
                f'an observed successful step from {successful}. Without successful '
                'output, DONE is not completion.'
            )})
            continue
        budget = runtime.remaining()
        if executions >= 3 or budget['executions'] <= 0 or budget['seconds'] <= 0:
            break
        # Recheck after generation; model time may differ from previous calls.
        if successful and budget['seconds'] < build_reserve + 10.0:
            messages.append({'role': 'user', 'content': (
                'The proposed program was NOT executed: insufficient estimated time '
                'remains for a complete build. Select among the earlier observed outputs.'
            )})
            continue
        before = runtime.remaining()
        executions += 1
        result = runtime.execute(blocks[0])
        after = runtime.remaining()
        build_costs.append(elapsed(before, after))
        if not isinstance(result, dict):
            result = {'ok': False, 'error': 'Missing structured execution result'}
        step = result.get('step')
        visible = bool(result.get('ok') is True and result.get('image'))
        selectable = visible and type(step) is int
        if selectable:
            successful.append(step)
            last_failure = None
        else:
            last_failure = 'build_failure' if result.get('ok') is not True else 'missing_output'
        report = {k: v for k, v in result.items() if k != 'image'}
        report['observed_output_state'] = 'render_available' if selectable else last_failure
        if not selectable:
            guidance = (
                'BUILD/OUTPUT FAILURE: this attempt is not selectable. No successful '
                'rendered output may be claimed for it. Inspect the error before making '
                'a visual diagnosis. Audit dimensions, fillet radii, World creation after '
                'realize, distinct rod endpoints, unique include keys and layout copies. '
                'A timeout is an execution failure even if the code describes useful edits.'
            )
        else:
            guidance = REVISION
        content = [{'type': 'text', 'text': (
            json.dumps(report, default=str) + '\n' + guidance +
            f'\nSuccessful steps: {successful}. Remaining: {after}. '
            f'Observed complete execution wall times: {build_costs}.'
        )}]
        if visible:
            content.append(runtime.image(result['image']))
        messages.append({'role': 'user', 'content': content})
    if successful:
        runtime.select(successful[-1])
