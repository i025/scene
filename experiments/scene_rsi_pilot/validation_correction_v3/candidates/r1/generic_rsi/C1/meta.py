"""Evidence-led planning using only the supplied development packet."""


def plan(packet):
    scenes = [s for s in packet.get('development', []) if isinstance(s, dict)]
    observations = packet.get('controlled_probes', []) or []
    used = packet.get('executed_probe_count', len(observations))
    if not isinstance(used, (int, float)):
        used = len(observations)
    available = max(0, 2 - max(int(used), len(observations)))
    seen = set()
    for observation in observations:
        if isinstance(observation, dict):
            seen.add((observation.get('scene_id'), observation.get('probe')))
    failures = 0
    successes = 0
    for scene in scenes:
        trajectory = scene.get('trajectory') or {}
        for event in trajectory.get('events', []):
            if event.get('event') == 'execution_result':
                if event.get('ok') is True:
                    successes += 1
                else:
                    failures += 1
    complete = [s for s in scenes if s.get('status') == 'complete'
                and (s.get('metrics') or {}).get('valid') is True]

    def score(scene):
        value = (scene.get('metrics') or {}).get('overall')
        return value if isinstance(value, (int, float)) else float('inf')

    complete.sort(key=score)
    probes = []
    # Execution starvation is directly observable; further renders cannot diagnose it.
    if failures < max(1, successes):
        for scene in complete:
            if len(probes) >= available:
                break
            sid = scene.get('scene_id')
            if not isinstance(sid, str):
                continue
            functional = scene.get('functional') or {}
            kind = 'isolate' if functional.get('functional_pass') is False else 'camera_focal'
            if (sid, kind) not in seen:
                probes.append({'scene_id': sid, 'kind': kind})
    instruction = (
        'Improve the general shared reconstruction procedure and callable plan(packet), using the '
        'entire supplied development archive, sources, execution traces, images, geometry summaries '
        'and prescribed edit regressions. Do not explore external files or specialize to scene IDs. '
        'First distinguish build failures, missing outputs, exhausted correction opportunities and '
        'visual mismatch. Count actual execution_result events; regression render counts describe '
        'a different operation and must not be substituted for reconstruction successes. '
        'Check whether API safeguards recover first-build success and permit useful visual revisions. '
        'Then assess framing, visible object coverage, silhouette, occlusion and broad tone before '
        'fine detail. Compare all available development cases, including regressions and failures. '
        'Interpret diagnostic interventions only at their actual target and pivot: a tiny component '
        'scale change cannot identify whole-object scale error, and one focal perturbation cannot '
        'establish an optimal camera or true geometry. Missing measurements remain unknown; missing '
        'required output is failure. Structural/edit passes certify only the prescribed operations, '
        'not semantic completeness, physical contact or metric 3D accuracy; AABBs are approximate. '
        'Do not optimize names to manipulate target selection. Preserve meaningful assemblies. '
        'Propose a falsifiable next change, state expected evidence and risks, and retain complete '
        'working replacement files with the fixed APIs, roles, objective, splits and budgets. '
        'Selection aggregates may inform retention only; do not request Selection images or labels. '
        'The latest valid meta program governs the next exploration branch independently of task '
        'program acceptance. No independent evaluation or rendering is permitted in the proposer session.'
    )
    return {'probes': probes, 'regression_guidance': True, 'instruction': instruction}
