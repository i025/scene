"""Initial meta-programs and the common proposal interface (prepared before freeze)."""
from pathlib import Path

GENERIC = '''"""CLI/backend adaptation of the HyperAgents self-referential meta entry point."""
def plan(packet):
    # Keep the complete explicit archive available and use the common probe menu.
    scenes = packet['development']
    probes = []
    if scenes and scenes[0]['status'] == 'complete':
        probes = [{'scene_id': scenes[0]['scene_id'], 'kind': kind} for kind in ['camera_focal', 'object_scale']]
    return {'probes': probes, 'regression_guidance': True,
            'instruction': 'Improve the shared task program H and your meta-program M. Inspect the entire supplied development archive, sources, execution errors, renders, geometry, and regression measurements. Design a general change to the reconstruction process under the fixed objective and limits. You may change meta.py planning, probe selection, evidence prioritization, and the next research instruction. Preserve callable plan(packet). The next candidate uses the latest valid meta program; this is an exploration branch, not acceptance of its task program. Do not specialize to scene identifiers.'}
'''
OURS = '''"""scene_rsi_pilot M_initial: bounded intervention and dependency regression guidance."""
def plan(packet):
    scenes = packet['development']
    probes = []
    diagnoses = []
    for scene in scenes:
        if scene['status'] != 'complete':
            diagnoses.append({'scene_id': scene['scene_id'], 'object_id': 'unknown', 'code_location': 'unknown', 'observation': 'No valid output; consult execution log', 'observation_type': 'measured', 'hypothesis': 'unknown', 'probe': 'none', 'probe_result': 'not_run', 'planned_change': 'Investigate general runtime failure before visual diagnosis'})
            continue
        target = scene.get('target_object', 'unknown')
        # Paired one-factor interventions distinguish camera from geometry sensitivity.
        probes = [{'scene_id': scene['scene_id'], 'kind': kind} for kind in ['camera_focal', 'object_scale']]
        diagnoses.append({'scene_id': scene['scene_id'], 'object_id': target, 'code_location': 'unknown', 'observation': 'Reference/render disagreement; magnitude is measured by fixed visual metrics', 'observation_type': 'measured_metric_with_unresolved_visual_cause', 'hypothesis': 'Camera framing or object scale may contribute; this is a hypothesis, not attribution', 'probe': 'camera_focal and object_scale', 'probe_result': 'awaiting controlled intervention', 'planned_change': 'Use probe sensitivity and dependency regression evidence to choose a shared H change'})
        break
    failures = {key: sum(not row.get('functional', {}).get(key, False) for row in scenes) for key in ['structure_pass', 'material_pass', 'composite_pass']}
    priorities = sorted(failures, key=lambda key: (-failures[key], key))
    return {'probes': probes, 'diagnoses': diagnoses, 'regression_priorities': priorities, 'regression_guidance': True,
            'instruction': 'Improve shared H and executable M using the controlled probe results and fixed functional regression evidence. Cover camera/object scale confusion, support/spatial relations, and occlusion/omission as applicable. Keep measured facts separate from visual hypotheses and historical heuristics. Link scene_id, object_id, code_location, observation, hypothesis, probe, probe_result, planned_change; unknown mappings must remain unknown. Do not assert causality from a single score delta. Use target modules/dependencies and modification risks to prioritize object structure, local material non-target preservation and composite movement checks. All final objectives and acceptance remain fixed. Modify meta.py only when an executable strategy change is justified; a memory append alone is not meta improvement. Return a reusable H, never a per-scene patched P.'}
'''
SCENEEVOLVE = '''"""Local SceneEvolve teacher: fixed meta-policy, shared harness evolution."""
def plan(packet):
    return {'probes': [], 'regression_guidance': True,
            'instruction': packet['sceneevolve_teacher_template'] + '\\nADAPTATION: This is one candidate in a sequential K=2 pilot. Return one general shared candidate, preserve all full development trajectories provided, and retain the best Selection-eligible H including H0. The meta program is fixed for this baseline. Identical diagnostic tools and two probe slots are available; this initial fixed teacher schedule does not request them.'}
'''

COMMON = '''You are a research proposer in a small image-to-editable-3D experiment. Only modify policy.py, system.txt, meta.py inside the requested candidate snapshot. policy.solve(task,runtime) is the shared H, not a scene generator for a particular ID. runtime.ask(messages), execute(code), select(step), remaining(), image(path) are the ONLY permitted model/execution interfaces. Budget is 5 fresh CLI sessions, 3 Blender executions and 1200 seconds per reconstruction. No network, tools, hidden subagents, third models or filesystem/data exploration. SceneAct, model roles, evaluator, objective, splits and resource limits are immutable. Only development raw evidence is supplied; Selection aggregate results inform retention but no Selection images/labels are exposed. Do not hardcode IDs, paths or scene answers. You must return complete replacement file contents in the output JSON. Use code to implement a general shared procedure. All methods have the same source, raw evidence, fixed geometry/menu interfaces, functional scores, and up to two actual diagnostic renders. M may organize and interpret them. Describe the applicable scope and risks. Preserve a complete working policy and unchanged system API details unless intentionally improving instructions. No independent evaluation or rendering is allowed inside this session. Diagnose missing output as failure rather than inventing measurements. A single CLI session may contain more than one observable model turn; the external logger accounts for actual events.'''

def initialize(root: Path):
    for name,text in [('generic_rsi',GENERIC),('scene_rsi_pilot',OURS),('sceneevolve_cli',SCENEEVOLVE)]:
        folder=root/'initial_meta'/name;folder.mkdir(parents=True,exist_ok=True)
        path=folder/'meta.py'
        if not path.exists(): path.write_text(text)
