"""M000: interactive multi-image research; descendants can change this strategy."""
import json


def research(context, api):
    observations = []
    while api.remaining()['sessions'] > 0:
        packet = {**context, 'observations': observations, 'remaining': api.remaining(),
                  'remaining_probe_budget': api.remaining()['diagnostic_frames'],
                  'already_executed_probe_count': sum(o['observation']['status']!='unavailable' for o in observations),
                  'strategy': 'Compare at least three independent development scenes. Form competing '
                  'explanations when useful, choose or write reusable actions, inspect actual observations, '
                  'then choose another experiment or propose one shared H/M change. Do not force an '
                  'experiment if execution evidence suffices. Distinguish sensitivity from unique cause. '
                  'No valid blend means diagnose program/service/budget evidence rather than geometry. '
                  'Mechanical test targets are not visual failure attributions; choose objects from image and native evidence. Unknown object/region/module mappings stay unknown. You may modify this meta.py '
                  'and add actions/*.py; decide whether a strategy change is justified. No scene IDs, '
                  'per-image parameters, evaluator or budget edits in shared code. An action accepts '
                  'run(context), uses current bpy scene, returns a JSON measurement. Its params include '
                  'object_id only from actual scene inventory. Record expected versus observed and '
                  'which subsequent decision changes. Stop without improvement if evidence is insufficient.'}
        decision = api.ask(packet)
        api.record_decision(decision)
        if decision['decision'] == 'action':
            if decision['new_action_source']:
                api.create_action(decision['action_name'], decision['new_action_source'],
                                  decision['scope'])
            observation = api.execute_action(decision['action_name'], decision['scene_id'],
                                             json.loads(decision['parameters_json']),
                                             decision['expectation'])
            observations.append({'request': decision, 'observation': observation})
        elif decision['decision'] == 'propose':
            return {'changes': decision['changes'], 'analysis': decision['analysis'],
                    'observations': observations, 'decision': decision}
        else:
            return {'changes': [], 'analysis': decision['analysis'],
                    'observations': observations, 'decision': decision}
    return {'changes': [], 'analysis': 'Research session cap reached; no fabricated patch.',
            'observations': observations, 'decision': None}
