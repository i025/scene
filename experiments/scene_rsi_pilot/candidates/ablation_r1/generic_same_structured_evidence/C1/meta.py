"""Evidence organization only; no model calls, file access or rendering."""

KEYS = ('structure_pass', 'material_pass', 'composite_pass')


def _rows(value):
    if isinstance(value, list):
        for item in value:
            yield from _rows(item)
    elif isinstance(value, dict):
        if 'scene_id' in value and ('status' in value or 'trajectory' in value):
            yield value
        else:
            for key in ('development', 'archive', 'archive_raw_development', 'scenes', 'results'):
                if key in value:
                    yield from _rows(value[key])


def _diagnose(scene, origin):
    events = (scene.get('trajectory') or {}).get('events', [])
    failures = []
    successes = []
    for event in events:
        if event.get('event') != 'execution_result':
            continue
        if event.get('ok') is False:
            failures.append({
                'step': event.get('step'),
                'stderr': event.get('stderr'),
                'error': event.get('error')
            })
        elif event.get('ok') is True:
            successes.append(event.get('step'))
    missing = scene.get('status') != 'complete' or (scene.get('metrics') or {}).get('valid') is False
    return {
        'scene_id': scene.get('scene_id'),
        'origin': origin,
        'object_id': scene.get('target_object', 'unknown'),
        'observation_type': 'supplied_execution_and_measurement_evidence',
        'observation': ('No valid final output: reconstruction failure.' if missing else
                        'Completed output; inspect supplied reference/render pair for visual disagreement.'),
        'execution_failures': failures,
        'successful_execution_steps': successes,
        'metrics': scene.get('metrics'),
        'functional': scene.get('functional'),
        'regression': scene.get('regression'),
        'geometry_limits': (scene.get('structure') or {}).get('measurement_limit'),
        'hypothesis': 'Preventable API failures may consume opportunities for visual correction; verify against the trajectory.',
        'planned_change': 'Prioritize valid first builds and evidence-based visual revision while preserving edit operability.'
    }


def plan(packet):
    current = list(_rows(packet.get('development', [])))
    diagnoses = [_diagnose(row, 'development') for row in current]
    for key in ('archive_raw_development', 'archive'):
        diagnoses.extend(_diagnose(row, key) for row in _rows(packet.get(key, [])))

    counts = {}
    for key in KEYS:
        values = [(row.get('functional') or {}).get(key) for row in current]
        counts[key] = {
            'pass': sum(value is True for value in values),
            'fail': sum(value is False for value in values),
            'unknown': sum(value is not True and value is not False for value in values)
        }
    priorities = sorted(KEYS, key=lambda key: (-counts[key]['fail'], key))

    observed = packet.get('controlled_probes') or []
    probe_evidence = []
    used_pairs = set()
    for probe in observed:
        result = probe.get('result') or {}
        kind = probe.get('probe', result.get('probe'))
        used_pairs.add((probe.get('scene_id'), kind))
        before = probe.get('baseline_visual_metrics') or {}
        after = probe.get('visual_metrics') or {}
        deltas = {}
        if before.get('valid') is True and after.get('valid') is True:
            for key in ('overall', 'ssim', 'lpips', 'dino', 'psnr'):
                a, b = before.get(key), after.get(key)
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    deltas[key] = b - a
        probe_evidence.append({
            'scene_id': probe.get('scene_id'), 'kind': kind,
            'status': result.get('status', 'unknown'),
            'target_selection': result.get('target_selection'),
            'metric_deltas': deltas,
            'interpretation': 'One intervention on the specified target only. Missing metrics are unknown; a small response does not identify a global cause.'
        })

    declared = packet.get('already_executed_probe_count', 0)
    used = max(len(observed), declared if isinstance(declared, int) else 0)
    available = max(0, 2 - used)
    complete = [row for row in current if row.get('status') == 'complete'
                and (row.get('metrics') or {}).get('valid') is True]

    def score(row):
        value = (row.get('metrics') or {}).get('overall')
        return value if isinstance(value, (int, float)) else float('inf')

    complete.sort(key=score)
    probes = []
    # Prefer global camera sensitivity across scenes before scaling an arbitrary small part.
    for row in complete:
        kind = 'isolate' if (row.get('functional') or {}).get('composite_pass') is False else 'camera_focal'
        pair = (row.get('scene_id'), kind)
        if len(probes) < available and pair not in used_pairs:
            probes.append({'scene_id': pair[0], 'kind': pair[1]})
            used_pairs.add(pair)

    instruction = (
        'Improve shared H and callable plan(packet) in M under the unchanged objective, roles, '
        'SceneAct sources, evaluator, splits and resource limits. Inspect every supplied development '
        'record and archive, including execution failures preceding completed outputs. Start with '
        'the earliest preventable failure and determine whether successful renders arrived early '
        'enough for a visual correction. Separate observed errors, visual estimates and hypotheses. '
        'Use supplied source semantics to audit fillet limits, world initialization after realize, '
        'include-key replacement, emitted mesh naming and material sharing. Inspect all supplied '
        'reference/render pairs for framing, silhouette, occlusion and large tonal errors. '
        'Interpret probes using their actual selected subtree, pivot and preserved variables; '
        'never generalize a small decorative-part scale probe to whole-object scale. '
        'Preserve functional successes; prescribed Blender edits prove operability only, not '
        'semantic completeness, true collision, or metric recovery. Unknown measurements remain '
        'unknown; missing output is failure. Propose a general process change with explicit risks '
        'and a falsifiable expected effect, such as earlier first successful rendering and more '
        'usable visual revisions. Do not hardcode scene IDs, paths or answers. Selection aggregates '
        'inform retention only; no Selection images or labels may be inferred or accessed. '
        'Return complete replacement files. This is an exploration branch, not acceptance of H. '
        'Keep the full supplied evidence available; these diagnoses are an index, not a substitute. '
        'No independent evaluation, filesystem exploration, external models or extra renders.'
    )
    return {
        'probes': probes,
        'regression_guidance': True,
        'instruction': instruction,
        'diagnoses': diagnoses,
        'regression_priorities': priorities,
        'functional_counts': counts,
        'probe_evidence': probe_evidence,
        'evidence_priority': ['missing_output', 'execution_failures', 'first_success_timing',
                              'reference_render_disagreement', 'controlled_interventions',
                              'functional_regressions'],
        'archive_note': 'Only explicitly supplied archive records are available; empty archives provide no historical evidence.'
    }
