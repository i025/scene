"""V2.4 engineered M. Numerical sensitivity is evidence, not a causal oracle."""
from itertools import combinations
import math

MENU = ['camera_focal', 'camera_tilt', 'object_scale', 'object_depth', 'isolate']


def discrimination(hypotheses, tool):
    scores = []
    for a, b in combinations(hypotheses, 2):
        x, y = a['predictions'][tool], b['predictions'][tool]
        midpoint_gap = abs((x['lower'] + x['upper'] - y['lower'] - y['upper']) / 2)
        width = ((x['upper'] - x['lower']) + (y['upper'] - y['lower'])) / 2
        scores.append(min(1., midpoint_gap / (width + .003)))
    return sum(scores) / len(scores) if scores else 0.


def plan_probes(context):
    remaining = context['remaining_probe_budget']
    assert remaining >= 0
    if not context['valid_blend']:
        return {'probes': [], 'reason': 'No valid Blender scene: diagnose program/execution evidence.', 'scores': {}}
    scores = {tool: discrimination(context['hypotheses'], tool) for tool in MENU}
    if context['method'] == 'structured':
        chosen = []
    elif context['method'] == 'fixed':
        chosen = ['camera_focal', 'object_scale']
    else:
        chosen = sorted(MENU, key=lambda t: (-scores[t], MENU.index(t)))
        chosen = [t for t in chosen if scores[t] >= .15]
    probes = []
    for tool in chosen:
        target = context['probe_targets'][tool]
        if tool not in ('camera_focal', 'camera_tilt') and target == 'unknown':
            continue
        probes.append({'probe': tool, 'object_id': target, 'predicted_discrimination': scores[tool]})
    return {'probes': probes[:remaining], 'scores': scores,
            'reason': 'Partial interval separation calibrated independently; identical forecasts score zero. Unknown targets are not fabricated.'}


def plan_patch(context, observations):
    outcomes = {o['request']['probe']: o['outcome'] for o in observations if o['status'] == 'completed'}
    updated = []
    for hypothesis in context['hypotheses']:
        residuals = []
        for tool, outcome in outcomes.items():
            interval = hypothesis['predictions'][tool]
            center = (interval['lower'] + interval['upper']) / 2
            half_width = (interval['upper'] - interval['lower']) / 2 + .003
            residuals.append(abs(outcome - center) / half_width)
        z = sum(residuals) / len(residuals) if residuals else None
        updated.append({'id': hypothesis['id'], 'module': hypothesis['module'],
                        'object_id': hypothesis['object_id'], 'forecast_residual': z,
                        'weight': math.exp(-.5 * min(z*z, 25)) if z is not None else None})
    ranked = sorted(updated, key=lambda h: -(h['weight'] or 0))
    calibrated = bool(outcomes) and min(h['forecast_residual'] for h in updated) <= 3
    ratio = ranked[0]['weight'] / max(ranked[1]['weight'], 1e-9) if calibrated else None
    selected = ranked[0]['module'] if calibrated and ratio >= 2 else 'unresolved'
    if not outcomes:
        selected = context['initial_module']
    return {'selected_module': selected, 'hypothesis_update': updated, 'outcomes': outcomes,
            'forecast_calibration': 'at_least_one_compatible' if calibrated else 'insufficient_or_no_observation',
            'evidence_ratio': ratio, 'decision_changed': selected != context['initial_module'],
            'planned_shared_H_change': 'Use the recorded sensitivities to develop general reconstruction instructions/algorithm; never insert per-image parameters. Investigate '+selected,
            'limitations': 'A forecast miss can reflect calibration error. No hypothesis is declared causally false solely from this scalar. Natural images have no fault-module ground truth.',
            'M_origin': 'engineer_revision_v2_4_not_automatic_descendant'}
