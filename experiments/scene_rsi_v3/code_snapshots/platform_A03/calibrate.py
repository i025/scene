"""Small evaluator calibration; commands collect, judge, report are explicit.

Only these preparation artifacts are used. No Selection/Test labels are read.
Collection renders; judgement makes real charged CLI calls. Import/report do neither.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import time
from pathlib import Path

from bw_evaluate import ROOT, collect_evidence, judge_artifact, write_json
from processes import cpu_environment, run_measured

OUT = ROOT / 'preparation' / 'bw_calibration'
FIXTURES = ROOT / 'preparation' / 'functional_fixtures'
CASES = ['correct', 'detached_part', 'missing_declared_part', 'broken_support',
         'shared_material_bad_edit', 'independent_local_edit', 'triangle_crossing',
         'near_black', 'scale_error']


def criterion(number, description, evidence_type, weight):
    return {'id': f'R{number:02d}', 'criterion': description, 'pass_condition': description,
            'fail_condition': 'The actual artifact does not satisfy the specified requirement.',
            'importance_weight': weight, 'evidence_type': evidence_type,
            'score_type': 'binary', 'score_values': [0, 1]}


def fixture_rubric(edited):
    target_color = 'blue' if edited else 'orange'
    return {'task_id': 'calibration_fixture', 'mode': 'known_controlled_scene',
            'prompt': 'Recreate the reference arrangement with two unit-cube parts, one gray support '
                      'and the declared Assembly hierarchy. Z_target_part rests on Support; '
                      f'Z_target_part must be {target_color}; A_unrelated_part must remain orange. '
                      'This is a controlled fixture, not a natural-image reconstruction score.',
            'rubrics': [
                criterion(1, 'Native mesh objects Z_target_part, A_unrelated_part and Support exist '
                          'as nonempty finite geometry; declarations alone do not establish presence.', 'scene_summary', 3),
                criterion(2, 'Assembly exists and both Z_target_part and A_unrelated_part are actual '
                          'children of Assembly, consistent with its scene_rsi_expected_children declaration.', 'scene_summary', 2),
                criterion(3, 'Z_target_part is supported by Support: its lower Z touches Support upper Z '
                          'within 0.01 of the fixture bounding diagonal and XY footprints overlap. '
                          'Use measured AABBs as a known-fixture approximation, not mesh collision truth.', 'scene_summary', 3),
                criterion(4, 'Both named parts have world-axis dimensions 1,1,1 and Support has dimensions '
                          '2,2,1, each within 0.05 fixture units; no extra intersecting Intruder geometry.', 'scene_summary', 2),
                criterion(5, f'The actual shader/material for Z_target_part is {target_color}, while '
                          'A_unrelated_part stays orange and Support stays gray. Check actual assigned '
                          'material slots/nodes, not only material names or generator claims.', 'scene_summary', 3),
                criterion(6, 'The rendered artifact visibly communicates the required two distinct cubes '
                          f'and gray support, correct arrangement and the required {target_color}/orange '
                          'part colors. A reasonable rendering variation is acceptable.', 'render', 2),
            ]}


def photograph_rubric():
    # Authored from the existing Goa classroom reference/task identity, not the
    # Terra output. Fixed before any BW calibration call; not an official BW task.
    return {'task_id': 'calibration_development_photo', 'mode': 'reference_reconstruction',
            'prompt': 'Reconstruct the supplied empty Goa classroom photograph as an editable 3D room. '
                      'Preserve the visible classroom furniture, spatial arrangement and main room '
                      'boundaries. Do not invent a unique hidden layout or absolute metric scale.',
            'rubrics': [
                criterion(1, 'The main visible classroom furniture types and major room surfaces are '
                          'recognizable in the artifact renders; generic featureless cubes alone do '
                          'not establish the requested object identities.', 'render', 3),
                criterion(2, 'Relative furniture arrangement, repetition/count at visible resolution, '
                          'major openings and room proportions follow the reference.', 'render', 3),
                criterion(3, 'Object-to-object and furniture-to-room size ratios are consistent with '
                          'the reference without requiring unstated absolute metric sizes.', 'render', 2),
                criterion(4, 'Visible major colors, lighting direction and material appearance are '
                          'consistent with the reference; reasonable matte simplification is allowed.', 'render', 2),
                criterion(5, 'The native project contains nonempty finite 3D mesh geometry with depth '
                          'and real material bindings, not only a reference image used as a billboard. '
                          'Identify actual geometry/material facts; a mesh-count threshold is not fidelity.', 'scene_summary', 2),
                criterion(6, 'The artifact as a whole clearly reads as the supplied classroom with the '
                          'visible main furniture and spatial enclosure; rendering noise or different '
                          'pixel values alone do not establish failure.', 'render', 3),
            ]}


def prepare_plan():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'plan.json'
    if path.exists():
        return json.loads(path.read_text())
    cfg = json.loads((ROOT / 'config.json').read_text())
    artifacts = []
    for name in CASES:
        variant = name in {'near_black', 'scale_error'}
        blend = (OUT / 'controlled_variants' / name if variant else FIXTURES / name) / 'scene.blend'
        reference = FIXTURES / 'correct' / 'final.png'
        if (not variant and not blend.is_file()) or not reference.is_file():
            raise FileNotFoundError(f'Known fixture missing: {blend}; {reference}')
        rubric = fixture_rubric(name in {'shared_material_bad_edit', 'independent_local_edit'})
        rubric_path = OUT / f'{name}_rubric.json'
        write_json(rubric_path, rubric)
        artifacts.append({'artifact_id': name, 'blend': str(blend), 'reference': str(reference),
                          'rubric': str(rubric_path), 'preview': name != 'correct', 'interior': False,
                          'controlled_variant': name if variant else None,
                          'expected_problem': None if name in {'correct', 'independent_local_edit'} else name})
    smoke = ROOT / 'preparation' / 'model_selection' / 'gpt-6.1-terra' / 'host_attempt'
    blend = smoke / 'execution' / 'scene.blend'
    request = json.loads((smoke / 'request.json').read_text())
    reference = Path(request['original_images_for_audit'][0])
    if not blend.is_file() or not reference.is_file():
        raise FileNotFoundError(f'Existing Terra smoke artifact missing: {blend}; {reference}')
    write_json(OUT / 'photograph_rubric.json', photograph_rubric())
    artifacts.append({'artifact_id': 'development_photo', 'blend': str(blend), 'reference': str(reference),
                      'rubric': str(OUT / 'photograph_rubric.json'), 'preview': False, 'interior': True,
                      'controlled_variant': None,
                      'expected_problem': 'unknown_real_reconstruction_quality'})
    schedule = [{'artifact_id': a['artifact_id'], 'repeat': repeat}
                for a in artifacts for repeat in (1, 2)]
    random.Random(42).shuffle(schedule)
    plan = {'version': 'bw_calibration_v3_1', 'created': time.time(), 'seed': 42,
            'purpose': 'Evaluator evidence routing and repeat noise; not method selection or performance tuning',
            'artifacts': artifacts, 'judge_schedule': schedule,
            'evaluation_configuration': cfg['evaluation'], 'judge_configuration': cfg['proposer'],
            'expected_cli_sessions': len(schedule), 'expected_render_attempts_without_failures': 50,
            'jitter_formula': 'max(abs(S_BW_repeat1 - S_BW_repeat2)) across completed pairs of the identical artifact, '
                              'including the real-photograph artifact; preview scores remain separately labelled',
            'delta_formula': 'max(2, maximum_absolute_repeat_difference); freeze only after every scheduled pair completes',
            'missing_requested_stressors': [],
            'known_fixture_limits': 'Existing fixtures provide omissions, hierarchy, support, crossings, shared material '
                                   'and legitimate independent edit. Black/scale cases are explicitly generated '
                                   'Blender copies of the correct fixture, not postprocessed fake renders.',
            'independence': 'Every judgement uses fresh session, anonymous E000xx directory and randomized artifact/view order; '
                            'same model as research remains a shared-model bias.'}
    write_json(path, plan)
    return plan


def collect(plan, cfg, selected=None):
    for artifact in plan['artifacts']:
        if selected and artifact['artifact_id'] not in selected:
            continue
        evidence = OUT / 'evidence' / artifact['artifact_id']
        if (evidence / 'evidence_status.json').exists():
            # Preserve successful, failed and interrupted attempts; never hide a rerun.
            continue
        if artifact['controlled_variant'] and not Path(artifact['blend']).exists():
            variant_folder = Path(artifact['blend']).parent
            command = [cfg['blender']['executable'], '--background', '--threads',
                       str(cfg['resources']['threads_per_blender']), '--python-exit-code', '2',
                       '--python', str(ROOT / 'calibration_variants.py'), '--', '--source',
                       str(FIXTURES / 'correct' / 'scene.blend'), '--output', str(variant_folder),
                       '--variant', artifact['controlled_variant']]
            with (OUT / f"{artifact['artifact_id']}_build.log").open('w') as log:
                measurement = run_measured(command, timeout=cfg['blender']['build_timeout'],
                    measurement_path=OUT / f"{artifact['artifact_id']}_build_timing.json",
                    memory_limit_bytes=int(cfg['resources']['memory_limit_gb'] * 1024 ** 3),
                    stdout=log, stderr=subprocess.STDOUT,
                    env=cpu_environment(threads=cfg['resources']['threads_per_blender'], cuda_visible=''))
            if measurement['returncode'] != 0 or measurement['timed_out']:
                raise RuntimeError('Controlled calibration variant creation failed: ' + artifact['artifact_id'])
        collect_evidence(artifact['blend'], evidence, cfg,
                         preview=artifact['preview'], interior=artifact['interior'])


def next_session():
    root = ROOT / 'evaluation_sessions'
    root.mkdir(exist_ok=True)
    values = [int(p.name[1:]) for p in root.glob('E*') if p.name[1:].isdigit()]
    return root / f'E{max(values, default=0) + 1:05d}'


def judge(plan, cfg, selected=None):
    by_id = {a['artifact_id']: a for a in plan['artifacts']}
    results = OUT / 'judgements'
    results.mkdir(exist_ok=True)
    for index, item in enumerate(plan['judge_schedule']):
        if selected and item['artifact_id'] not in selected:
            continue
        output = results / f"{item['artifact_id']}_repeat{item['repeat']}.json"
        if output.exists():
            continue
        artifact = by_id[item['artifact_id']]
        evidence = OUT / 'evidence' / artifact['artifact_id']
        status_path = evidence / 'evidence_status.json'
        if not status_path.exists():
            continue
        status = json.loads(status_path.read_text())
        if status['evaluation_status'] != 'pending_judge':
            continue
        views = list(status['images'])
        random.Random(4200 + index).shuffle(views)
        session = next_session()
        # Artifact/fault names are retained only outside the anonymous CLI cwd.
        write_json(OUT / f'judge_assignment_{index:03d}.json',
                   {**item, 'session': str(session), 'display_order': views})
        result = judge_artifact(artifact['reference'], evidence,
                                json.loads(Path(artifact['rubric']).read_text()), cfg, session,
                                display_order=views)
        write_json(output, {**item, **result, 'anonymous_session': str(session), 'display_order': views})
    report(plan)


def report(plan):
    rows, pairs, raw_results = [], [], {}
    for item in plan['judge_schedule']:
        path = OUT / 'judgements' / f"{item['artifact_id']}_repeat{item['repeat']}.json"
        result = json.loads(path.read_text()) if path.exists() else None
        if result is not None:
            raw_results[(item['artifact_id'], item['repeat'])] = result
        rows.append({**item, 'status': result['evaluation_status'] if result else 'not_started',
                     'S_BW': result['S_BW'] if result else None,
                     'S_rubric': result['S_rubric'] if result else None,
                     'S_dimension': result['S_dimension'] if result else None,
                     'preview': next(a['preview'] for a in plan['artifacts'] if a['artifact_id'] == item['artifact_id']),
                     'anonymous_session': result['anonymous_session'] if result else None})
    for artifact in plan['artifacts']:
        pair = sorted([r for r in rows if r['artifact_id'] == artifact['artifact_id']], key=lambda r: r['repeat'])
        complete = len(pair) == 2 and all(r['status'] == 'completed' for r in pair)
        pairs.append({'artifact_id': artifact['artifact_id'], 'preview': artifact['preview'],
                      'completed_pair': complete,
                      'absolute_BW_repeat_difference': abs(pair[0]['S_BW'] - pair[1]['S_BW']) if complete else None})
    complete = all(p['completed_pair'] for p in pairs)
    differences = [p['absolute_BW_repeat_difference'] for p in pairs if p['completed_pair']]
    jitter = max(differences) if differences else None
    means = {a['artifact_id']: sum(r['S_BW'] for r in rows if r['artifact_id'] == a['artifact_id']) / 2
             for a in plan['artifacts'] if all(r['status'] == 'completed' for r in rows
                                              if r['artifact_id'] == a['artifact_id'])}
    detection = []
    comparisons = [('missing_declared_part', 'correct', 'R01'), ('detached_part', 'correct', 'R02'),
                   ('broken_support', 'correct', 'R03'), ('triangle_crossing', 'correct', 'R04'),
                   ('near_black', 'correct', 'R06'), ('scale_error', 'correct', 'R04'),
                   ('shared_material_bad_edit', 'independent_local_edit', 'R05')]
    for broken, legal, criterion_id in comparisons:
        pair_known = broken in means and legal in means
        rates = {}
        if pair_known:
            for name in [broken, legal]:
                rates[name] = sum(next(r['score'] for r in raw_results[(name, repeat)]['rubric_scores']
                                      if r['id'] == criterion_id) for repeat in [1, 2]) / 2
        detection.append({'fault': broken, 'legal_control': legal,
                          'score_drop': means[legal] - means[broken] if pair_known else None,
                          'lower_BW_than_control': means[broken] < means[legal] if pair_known else None,
                          'target_criterion_id': criterion_id,
                          'fault_criterion_pass_rate': rates[broken] if pair_known else None,
                          'legal_criterion_pass_rate': rates[legal] if pair_known else None,
                          'criterion_detected_expected_problem': rates[broken] < rates[legal] if pair_known else None,
                          'interpretation': 'Known-fixture criterion is the sensitivity check. The BW difference is '
                                            'supplementary: correct uses formal views while bad fixtures use preview. '
                                            'No threshold retuning or statistical-significance claim.'})
    # Legal independent edit has a different task color instruction; report the
    # raw difference, do not force equality or tune rules after observing it.
    edit_known = 'correct' in means and 'independent_local_edit' in means
    legal_edit_verdicts = [{
        'repeat': repeat,
        'rubric_scores': raw_results[('independent_local_edit', repeat)]['rubric_scores'],
        'any_failed_requirement': any(r['score'] == 0 for r in raw_results[('independent_local_edit', repeat)]['rubric_scores']),
    } for repeat in [1, 2]] if 'independent_local_edit' in means else []
    result = {'status': 'completed' if complete else 'pending', 'all_scheduled': len(rows),
              'completed': sum(r['status'] == 'completed' for r in rows),
              'eval_failed': sum(r['status'] == 'eval_failed' for r in rows),
              'pairs': pairs, 'maximum_absolute_repeat_difference': jitter,
              'promotion_delta_recommendation': max(2, jitter) if complete else None,
              'freeze_status': 'ready_for_protocol_freeze' if complete else 'not_ready',
              'missing_requested_stressors': plan['missing_requested_stressors'],
              'known_problem_detection': detection,
              'legal_edit_requirement_evidence': legal_edit_verdicts,
              'manual_review_pending': (any(d['criterion_detected_expected_problem'] is False for d in detection)
                                        or any(v['any_failed_requirement'] for v in legal_edit_verdicts)) if complete else None,
              'legal_edit_BW_difference_from_correct': means['independent_local_edit'] - means['correct'] if edit_known else None,
              'legal_edit_review': 'Inspect rubric/eight-dimension evidence for any inappropriate edit penalty; '
                                   'different requested color and preview quality prevent interpreting the raw difference alone as a regression.',
              'limitations': 'Repeated fixed outputs measure judge variability only, not generator variance. '
                            'Preview and formal quality are not an evolution curve. No human validation is claimed.'}
    write_json(OUT / 'calibration.json', result)
    write_json(OUT / 'judgement_rows.json', rows)
    with (OUT / 'judgement_rows.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['collect', 'judge', 'report'])
    parser.add_argument('--case', action='append', choices=[*CASES, 'development_photo'])
    args = parser.parse_args()
    cfg = json.loads((ROOT / 'config.json').read_text())
    plan = prepare_plan()
    if args.command == 'collect':
        collect(plan, cfg, args.case)
    elif args.command == 'judge':
        judge(plan, cfg, args.case)
    else:
        report(plan)


if __name__ == '__main__':
    main()
