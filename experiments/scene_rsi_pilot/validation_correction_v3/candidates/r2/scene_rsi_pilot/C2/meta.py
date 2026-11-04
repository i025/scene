"""Evidence-driven M: failure triage, bounded probes and dependency-aware regression planning.
Only supplied development records are inspected. No execution, rendering or file access.
"""
import re


CHECKS = ('structure_pass', 'material_pass', 'composite_pass')
INSTRUCTION = (
    'Improve reusable shared H, never a per-scene patched program. Preserve the fixed '
    'objective, evaluator, roles, interfaces and budgets. Separate measured facts, visual '
    'hypotheses and historical heuristics. Link scene_id, object_id, code_location, '
    'observation, hypothesis, probe, probe_result and planned_change. Unknown mappings '
    'remain unknown. A single probe score delta is sensitivity evidence, not causal '
    'attribution. Preserve passing structure, local material non-target preservation '
    'and composite movement behavior; inspect semantic completeness separately. '
    'Missing output is failure. Use only supplied raw development evidence; Selection '
    'aggregates inform retention, never inferred Selection images or labels.'
)


def _location(program, target, camera=False):
    if not isinstance(program, str) or program == 'missing':
        return 'unknown'
    matches = []
    for number, line in enumerate(program.splitlines(), 1):
        if camera:
            found = re.search(r'\bset_view\s*\(', line)
        else:
            found = target != 'unknown' and re.search(
                r'\.include\s*\(\s*[\'\"]' + re.escape(str(target)) + r'[\'\"]\s*,', line)
        if found:
            matches.append(number)
    return {'program_lines': matches, 'mapping': 'call site only; descendants unresolved'} if matches else 'unknown'


def _diagnosis(sid, oid, location, observation, hypothesis, probe, result, change, kind='measured'):
    return dict(scene_id=sid, object_id=oid, code_location=location,
                observation=observation, observation_type=kind, hypothesis=hypothesis,
                probe=probe, probe_result=result, planned_change=change)


def plan(packet):
    scenes = packet.get('development', [])
    records = packet.get('controlled_probes', []) or []
    diagnoses = []
    work = []
    counts = {key: {'pass': 0, 'fail': 0, 'unknown': 0} for key in CHECKS}
    failed_outputs = 0
    for scene in scenes:
        sid = scene.get('scene_id', 'unknown')
        functional = scene.get('functional') or {}
        structure = scene.get('structure') or {}
        regression = scene.get('regression') or {}
        target_info = regression.get('target_selection') or structure.get('target') or {}
        target = target_info.get('object') or scene.get('target_object') or 'unknown'
        program = scene.get('program', '')
        location = _location(program, target)
        valid = scene.get('status') == 'complete' and (scene.get('metrics') or {}).get('valid') is not False
        for key in CHECKS:
            value = functional.get(key)
            counts[key]['pass' if value is True else 'fail' if value is False else 'unknown'] += 1
        if not valid:
            failed_outputs += 1
            events = (scene.get('trajectory') or {}).get('events', [])
            errors = [
                {'step': e.get('step'), 'error': e.get('error'), 'stderr': e.get('stderr')}
                for e in events if e.get('event') == 'execution_result' and e.get('ok') is False
            ]
            diagnoses.append(_diagnosis(
                sid, target, 'unknown',
                {'status': scene.get('status'), 'metrics': scene.get('metrics'), 'execution_errors': errors},
                'Runtime failure is observed; timeout phase and visual quality remain unknown.',
                'none', 'not_run',
                'Prioritize source preflight, explicit world initialization, bounded detail and failure-aware recovery.'))
            work.append({'scene_id': sid, 'priority': 0, 'module': 'runtime/preflight',
                         'checks': ['valid output', 'primitive bounds', 'world after realize'],
                         'risk': 'Simplification can remove salient structure; preserve semantic assemblies.'})
            continue
        related = [p for p in records if p.get('scene_id') == sid]
        for probe in related:
            result = probe.get('result') or {}
            kind = probe.get('probe', result.get('probe', 'unknown'))
            selected = (result.get('target_selection') or {}).get('object', 'unknown')
            before = probe.get('baseline_visual_metrics') or {}
            after = probe.get('visual_metrics') or {}
            deltas = {}
            for key in ('ssim', 'lpips', 'dino', 'psnr', 'overall'):
                a, b = before.get(key), after.get(key)
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    deltas[key] = b - a
            diagnoses.append(_diagnosis(
                sid, selected, _location(program, selected, camera=kind == 'camera_focal'),
                {'baseline': before, 'probe_metrics': after, 'deltas': deltas},
                'Camera, geometry, depth and occlusion remain competing explanations; no inverse step is established.',
                kind, result,
                'Fit multiple architectural and near/far anchors; revise camera separately from local geometry. '
                'For local scale changes inspect the pivot, attached parts and support dependencies.'))
        material = regression.get('material') or {}
        move = regression.get('move') or {}
        relations = structure.get('approximate_relations') or {}
        dependencies = {
            'target_selection': target_info,
            'target_modules': scene.get('target_modules', 'unknown'),
            'supplied_dependencies': scene.get('dependencies', 'unknown'),
            'support_candidates': relations.get('approximate_support_candidates', []),
            'overlap_candidates': relations.get('approximate_overlap_candidates', []),
            'limitation': relations.get('limitation', 'Unknown semantic contacts; AABB evidence is approximate.')
        }
        diagnoses.append(_diagnosis(
            sid, target, location,
            {'functional': functional, 'material': material, 'move': move,
             'semantic_object_completeness': functional.get('semantic_object_completeness'),
             'support_collision_truth': functional.get('support_collision_truth')},
            'Passing prescribed edits do not certify intended parts outside the selected subtree, '
            'physical contacts, or whether visually missing parts are omitted or occluded.',
            'fixed functional regression', regression.get('test_type', 'unknown'),
            'Audit semantic membership and unique child keys; derive support placement from shared parameters. '
            'Scope materials by ownership and copy shared materials before local changes. '
            'Preserve the tested descendant transform relations and non-target state.'))
        for key, module, risk, checks in (
            ('structure_pass', 'object construction and hierarchy',
             'Duplicate keys, invalid primitives and detached parts can lose editable structure.',
             ['finite nonempty geometry', 'unique child keys', 'visible inventory versus graph membership']),
            ('material_pass', 'local material assignment',
             'Shared material mutation or color-based selection can modify unrelated objects.',
             ['target surface', 'target geometry unchanged', 'non-target shaders and transforms unchanged']),
            ('composite_pass', 'assembly movement and support dependencies',
             'Partial ownership or an incorrect pivot can leave fittings behind or break support.',
             ['complete semantic membership', 'relative part transforms', 'non-target preservation', 'support gaps'])
        ):
            value = functional.get(key)
            work.append({'scene_id': sid, 'object_id': target, 'code_location': location,
                         'priority': 1 if value is False else 2 if value is None else 3,
                         'module': module, 'check': key, 'status': value,
                         'checks': checks, 'dependencies': dependencies, 'risk': risk})
    # Count all actual attempts, including failed probes; never silently replenish the budget.
    used = sum(max(1, int((p.get('result') or {}).get('render_attempts', 1) or 1)) for p in records)
    explicit = packet.get('already_executed_probe_count', packet.get('executed_probe_count'))
    if isinstance(explicit, (int, float)):
        used = max(used, int(explicit))
    unused = max(0, 2 - used)
    probes = []
    for scene in scenes:
        if not unused or scene.get('status') != 'complete':
            continue
        sid = scene.get('scene_id')
        if not sid:
            continue
        prior = {p.get('probe', (p.get('result') or {}).get('probe')) for p in records if p.get('scene_id') == sid}
        target = scene.get('target_object', 'unknown')
        for kind in ('camera_focal', 'object_scale'):
            if kind in prior or (kind == 'object_scale' and target in (None, 'unknown')):
                continue
            probes.append({'scene_id': sid, 'kind': kind})
            unused -= 1
            if unused == 0:
                break
        if probes:
            break
    priorities = sorted(CHECKS, key=lambda key: (-counts[key]['fail'], CHECKS.index(key)))
    work.sort(key=lambda row: row['priority'])
    return {'probes': probes, 'diagnoses': diagnoses,
            'regression_priorities': priorities, 'regression_counts': counts,
            'failed_output_count': failed_outputs, 'regression_worklist': work,
            'regression_guidance': True, 'instruction': INSTRUCTION,
            'evidence_limits': [
                'Absent functional fields are unknown, not measured failures.',
                'Reported failed-output functional failures remain counted, but are not attributed to geometry.',
                'Source call sites do not identify every generated mesh.',
                'Probe deltas do not identify a unique cause or establish statistical significance.',
                'No additional render or evaluation is performed by this planner.'
            ]}
