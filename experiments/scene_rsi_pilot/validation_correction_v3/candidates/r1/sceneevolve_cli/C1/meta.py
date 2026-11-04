"""Local SceneEvolve teacher: fixed meta-policy, shared harness evolution."""
def plan(packet):
    return {'probes': [], 'regression_guidance': True,
            'instruction': packet['sceneevolve_teacher_template'] + '\nADAPTATION: This is one candidate in a sequential K=2 pilot. Return one general shared candidate, preserve all full development trajectories provided, and retain the best Selection-eligible H including H0. The meta program is fixed for this baseline. Identical diagnostic tools and two probe slots are available; this initial fixed teacher schedule does not request them.'}
