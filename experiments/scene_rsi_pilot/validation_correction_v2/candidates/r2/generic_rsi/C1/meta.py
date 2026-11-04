"""CLI/backend adaptation of the HyperAgents self-referential meta entry point."""
def plan(packet):
    # Keep the complete explicit archive available and use the common probe menu.
    scenes = packet['development']
    probes = []
    if scenes and scenes[0]['status'] == 'complete':
        probes = [{'scene_id': scenes[0]['scene_id'], 'kind': kind} for kind in ['camera_focal', 'object_scale']]
    return {'probes': probes, 'regression_guidance': True,
            'instruction': 'Improve the shared task program H and your meta-program M. Inspect the entire supplied development archive, sources, execution errors, renders, geometry, and regression measurements. Design a general change to the reconstruction process under the fixed objective and limits. You may change meta.py planning, probe selection, evidence prioritization, and the next research instruction. Preserve callable plan(packet). The next candidate uses the latest valid meta program; this is an exploration branch, not acceptance of its task program. Do not specialize to scene identifiers.'}
