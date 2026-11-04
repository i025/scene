"""Passive evidence triage and dependency-aware shared-policy revision planning.

Consumes only the supplied development packet. No execution, rendering or probes.
Source findings are static observations, not functional or visual measurements.
"""
import ast


CHECKS = ('structure_pass', 'material_pass', 'composite_pass')
ACTIONS = {
    'structure_pass': 'Preserve finite nonempty separate meshes and resolve failed construction APIs before visual revision.',
    'material_pass': 'Resolve the target parent subtree; copy shared materials for local edits and preserve non-target geometry, parents and finishes.',
    'composite_pass': 'Keep the intended complete composite under one semantic parent; preserve relative transforms and unrelated objects during movement.'
}


def _dict(value):
    return value if isinstance(value, dict) else {}


def _source_sites(program):
    try:
        tree = ast.parse(program)
    except (SyntaxError, TypeError) as exc:
        return {}, str(exc)
    sites = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            sites.setdefault(name, []).append(node.lineno)
    return sites, None


def plan(packet):
    diagnoses = []
    work = []
    counts = {key: {'pass': 0, 'fail': 0, 'unknown': 0} for key in CHECKS}
    risks = {key: 0 for key in CHECKS}

    for scene in packet.get('development', []):
        sid = scene.get('scene_id', 'unknown')
        functional = _dict(scene.get('functional'))
        structure = _dict(scene.get('structure'))
        regression = _dict(scene.get('regression'))
        target = scene.get('target_object') or functional.get('target_object') or 'unknown'
        program = scene.get('program') or ''
        sites, parse_error = _source_sites(program)
        objects = [o for o in structure.get('objects', []) if isinstance(o, dict)]
        target_row = next((o for o in objects if o.get('name') == target), {})
        target_info = _dict(regression.get('target_selection')) or _dict(structure.get('target'))
        target_meshes = target_info.get('mesh_names', [])
        dependencies = {
            'parent': target_row.get('parent', 'unknown'),
            'mesh_names': target_meshes,
            'shown_materials': sorted({m for o in objects if o.get('name') in target_meshes
                                       for m in o.get('material_names', [])}),
            'target_modules': scene.get('target_modules', 'unknown'),
            'declared_dependencies': scene.get('dependencies', 'unknown'),
            'projection': structure.get('evidence_projection', 'unknown')
        }

        def emit(kind, observation, hypothesis, change, location='unknown',
                 object_id='unknown', rank=3, checks=()):
            row = {
                'scene_id': sid, 'object_id': object_id, 'code_location': location,
                'observation': observation, 'observation_type': kind,
                'hypothesis': hypothesis, 'probe': 'none; disabled',
                'probe_result': 'not_run; frozen ablation', 'planned_change': change,
                'dependencies': dependencies if object_id == target else 'unknown'
            }
            diagnoses.append(row)
            work.append({'priority': rank, 'diagnosis_index': len(diagnoses)-1,
                         'regression_checks': list(checks)})

        for key in CHECKS:
            value = functional.get(key)
            state = 'pass' if value is True else 'fail' if value is False else 'unknown'
            counts[key][state] += 1
            details = structure.get('structure_pass') if key == 'structure_pass' else regression.get(
                'material' if key == 'material_pass' else 'move', 'unknown')
            emit('measured' if value is not None else 'missing_evidence',
                 {'functional_check': key, 'reported_value': value, 'fixed_details': details},
                 'A pass covers the prescribed target operation only; absent results remain unknown.',
                 ACTIONS[key], object_id=target, rank=1 if value is False else 4, checks=(key,))

        metrics = _dict(scene.get('metrics'))
        if scene.get('status') != 'complete' or metrics.get('valid') is False:
            emit('reported_output_failure',
                 {'status': scene.get('status'), 'valid': metrics.get('valid')},
                 'Failure cause is unknown without an execution log; no visual measurement is inferred.',
                 'Repair the general build/output path before visual interpretation.',
                 rank=0, checks=CHECKS)

        events = _dict(scene.get('trajectory')).get('events', [])
        failed_events = [e for e in events if e.get('event') == 'execution_result' and e.get('ok') is False]
        for event in failed_events:
            error = str(event.get('stderr') or event.get('error') or 'Missing error details')
            if 'Fillet exceeds half the smallest dimension' in error:
                change = 'Audit every fillet radius against minimum thickness before the first Blender execution.'
                module = 'sceneact.construction.fillet_box'
            elif 'NoneType' in error and ('world' in error or 'use_nodes' in error):
                change = 'Initialize a missing Blender World after realize before using its properties.'
                module = 'generated world setup after realize'
            else:
                change = 'Use the actual exception to audit analogous API calls before retrying.'
                module = 'unknown'
            emit('measured_execution_failure',
                 {'step': event.get('step'), 'error_tail': error[-1800:]},
                 'This attempt failed; its missing render cannot support visual diagnosis.',
                 change, location=module, rank=0, checks=('structure_pass',))

        if parse_error:
            emit('static_source_observation', {'parse_error': parse_error},
                 'The supplied source cannot be statically inspected.',
                 'Preserve unknown mappings and repair source syntax when applicable.', rank=0,
                 checks=('structure_pass',))

        # Exact source sites are not inferred semantic target mappings.
        mesh_sites = sites.get('bpy.data.objects.new', []) + sites.get('bpy.data.meshes.new', [])
        if mesh_sites:
            risks['composite_pass'] += 1
            emit('static_source_observation', {'direct_bpy_creation_lines': sorted(mesh_sites)},
                 'Directly created geometry may escape the semantic SceneAct parent; ownership needs review.',
                 'Keep complete object geometry in SceneAct Assets and preserve semantic parent membership.',
                 location={'source': 'supplied program', 'lines': sorted(mesh_sites)}, rank=2,
                 checks=('structure_pass', 'composite_pass'))

        if 'bpy.data.materials' in program:
            risks['material_pass'] += 1
            emit('static_source_observation', 'Source accesses Blender material datablocks.',
                 'Global edits or shared finishes may affect unrelated objects; this is a risk, not a failed regression.',
                 'Scope customization to exact parent descendants and copy shared materials before local changes.',
                 rank=2, checks=('material_pass',))

        include_sites = [(name, lines) for name, lines in sites.items() if name.endswith('.include')]
        if include_sites:
            emit('static_source_observation', {'include_call_sites': include_sites},
                 'Repeated per-parent keys can overwrite objects; static call presence alone does not prove duplication.',
                 'Audit loop/helper keys and semantic grouping before interpreting apparent omissions.',
                 location={'source': 'supplied program', 'sites': include_sites}, rank=2,
                 checks=('structure_pass', 'composite_pass'))

        camera_lines = sites.get('set_view', [])
        emit('reported_metrics', metrics or 'No metrics supplied.',
             'Camera pose/focal length, object proportions, depth and appearance remain competing explanations; scores do not identify the cause.',
             'In shared H, compare architecture and near/far image anchors before choosing camera or local scale corrections.',
             location={'source': 'supplied program', 'set_view_lines': camera_lines} if camera_lines else 'unknown',
             rank=3, checks=('structure_pass', 'composite_pass'))

        relations = _dict(structure.get('approximate_relations'))
        emit('approximate_geometry' if relations else 'missing_evidence',
             {key: relations.get(key) for key in (
                 'approximate_support_candidates_total_count', 'approximate_overlap_candidates_total_count',
                 'semantic_support_pass', 'true_mesh_collision_pass', 'limitation')},
             'AABB candidates do not establish contact, collision or semantic support; primitive overlaps may be intentional.',
             'Use explicit support anchors/shared dimensions and inspect visible contact and overlap order during normal render review.',
             rank=3, checks=('structure_pass', 'composite_pass'))
        emit('evidence_availability',
             {'attached_image_count': len(scene.get('attached_images', [])),
              'semantic_object_completeness': functional.get('semantic_object_completeness')},
             'Visibility may reflect cropping, occlusion or omitted geometry; this planner does not infer pixel content from attachment paths.',
             'Shared H must compare visible inventory with source membership, unique keys and depth order before adding or moving objects.',
             rank=3, checks=('structure_pass', 'composite_pass'))

    priorities = sorted(CHECKS, key=lambda key: (-counts[key]['fail'], -risks[key], CHECKS.index(key)))
    work.sort(key=lambda row: (row['priority'], row['diagnosis_index']))
    return {
        'probes': [], 'requested_probes': [], 'diagnoses': diagnoses,
        'regression_priorities': priorities, 'regression_counts': counts,
        'static_risk_counts': risks, 'work_queue': work, 'regression_guidance': True,
        'instruction': (
            'Use only supplied passive development evidence. Address observed execution failures first, '
            'then explicit fixed regression failures and dependency risks, then uncertain visual causes. '
            'Work queue ranks are planning heuristics, not new acceptance criteria. Preserve unknown '
            'scene/object/code mappings. Retain structure, local material non-target preservation and '
            'composite movement checks. No active probes, independent renders, evaluator changes or '
            'causal claims from single score deltas. Propose reusable H changes, never per-scene patches.'
        )
    }
