"""Prepare a separate V3 archive; no models, renders, credential reads or Git mutation.

The live experiment may be incomplete. Its actual state, failed attempts and all
permitted raw artifacts are retained. Unlicensed BW reference media are withheld.
"""
import argparse
from collections import defaultdict
import csv
import io
import json
import os
from pathlib import Path
import re
import tarfile
import time

from PIL import Image, ImageDraw

EXPERIMENT = Path('experiments/scene_rsi_v3')
TEXT = {'.py', '.sh', '.json', '.jsonl', '.txt', '.log', '.md', '.diff', '.yaml', '.yml', '.csv', '.html', '.css', '.toml', '.svg'}
MEDIA = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.tif', '.tiff', '.exr', '.mp4', '.mov', '.blend'}
SKIP_DIRS = {'__pycache__', '.git', '.venv', 'venv', 'node_modules', 'model-cache', 'matplotlib_cache'}
CREDENTIAL_FILES = {'.env', 'auth.json', 'credentials.json', '.netrc', 'id_rsa', 'id_ed25519', 'cookies.txt'}
SECRET = re.compile(rb'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
SAFE_FIGURES = {'development_contact_sheet.png', 'evolution.png', 'quality_points.png',
                 'dimensions_and_function.png', 'cost_and_timing.png', 'cpu_benchmark.png',
                 'research_chain.png', 'HM_lineage.png'}
CORE_JSON = {'config.json', 'manifest.json', 'state.json', 'record.json', 'round0.json',
             'record_before_A02_evaluator.json',
             'request.json', 'session.json', 'freeze.json', 'selection_freeze.json',
             'final_selection_freeze.json', 'proposal.json', 'decisions.json',
             'observation.json', 'action_request.json', 'actions_index.json', 'ledger.json'}


def load(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)


def paths(source):
    for base, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS and not (Path(base) / name).is_symlink())
        for name in sorted(names):
            path = Path(base) / name
            if path.is_symlink() or name in CREDENTIAL_FILES or path.suffix in {'.pyc', '.cubin', '.zst'}:
                continue
            yield path


def group_for(rel):
    parts = rel.parts
    if parts[0] == 'meta_replay_stage':
        return 'meta-replay'
    if parts[0] in {'preparation', 'session_staging', 'initial_m', 'fixed_h', 'configs', 'backend'}:
        return 'preparation'
    if parts[0] == 'rounds' and len(parts) > 1:
        return 'round' + parts[1].zfill(2)
    if parts[0] == 'meta_traces' and len(parts) > 1 and re.fullmatch('round[0-9]+', parts[1]):
        return parts[1]
    if parts[0] == 'candidates' and len(parts) > 1 and re.fullmatch('C[0-9]+', parts[1]):
        return 'round' + parts[1][1:].zfill(2)
    if parts[0] == 'results' and len(parts) > 2:
        if parts[2] == 'test':
            return 'final'
        if parts[1] == 'historical_r1_C2_start':
            return 'baseline'
        if re.fullmatch('[CH][0-9]+', parts[1]):
            return 'round' + parts[1][1:].zfill(2)
    if parts[0] == 'code_snapshots' and len(parts) > 1 and re.fullmatch('M_round[0-9]+', parts[1]):
        return 'round' + parts[1].split('round')[-1].zfill(2)
    return 'preparation'


def placeholder(label):
    image = Image.new('RGB', (512, 320), '#f4f4f4')
    draw = ImageDraw.Draw(image)
    draw.multiline_text((25, 110), 'REFERENCE WITHHELD\nLicense not confirmed for redistribution.\nNot an experimental result.\n' + label[:65], fill='#333333', spacing=8)
    stream = io.BytesIO(); image.save(stream, format='PNG')
    return stream.getvalue()


def embedded_public_specs(source, manifest, file_paths):
    """Read only specs already embedded in generated task records, never attachments."""
    declared = {str(Path(raw).resolve()): row['scene_id']
                for row in manifest for raw in row.get('attachments', [])}
    specs = {}
    for path in file_paths:
        if path.name != 'task.json':
            continue
        task = load(path)
        sources = task.get('public_attachment_sources', [])
        if not sources:
            continue
        instruction, cursor = task['instruction'], 0
        markers = ['\nPUBLIC TASK ATTACHMENT ' + Path(raw).name + ':\n' for raw in sources]
        starts = []
        for marker in markers:
            start = instruction.index(marker, cursor)
            starts.append(start)
            cursor = start + len(marker)
        for index, raw in enumerate(sources):
            key = str(Path(raw).resolve())
            scene_id = declared[key]
            end = starts[index + 1] if index + 1 < len(starts) else len(instruction)
            body = instruction[starts[index] + len(markers[index]):end]
            if not body.strip():
                raise ValueError('Empty embedded public attachment: ' + str(path))
            if key not in specs:
                specs[key] = {'scene_id': scene_id, 'attachment_name': Path(raw).name,
                              'source': 'BlenderWorld/tasks/' + scene_id + '/attachments/' + Path(raw).name,
                              'body': body, 'task_records': []}
            elif specs[key]['body'] != body:
                raise ValueError('Different embedded spec revisions require explicit review: ' + str(path))
            specs[key]['task_records'].append(str(path.relative_to(source)))
    return list(specs.values())


def public_text(data, replacements, embedded_specs=()):
    value = data.decode('utf-8')
    changes = []
    for spec in embedded_specs:
        marker = ('[WITHHELD_PUBLIC_TASK_ATTACHMENT: source=' + spec['source'] +
                  '; task_id=' + spec['scene_id'] +
                  '; redistribution_license_not_confirmed; full_original_retained_on_server]')
        variants = {}
        for ascii_only in (False, True):
            old, new = spec['body'], marker
            for _ in range(4):
                variants[old] = new
                old = json.dumps(old, ensure_ascii=ascii_only)[1:-1]
                new = json.dumps(new, ensure_ascii=ascii_only)[1:-1]
        count = 0
        for old, new in sorted(variants.items(), key=lambda pair: len(pair[0]), reverse=True):
            count += value.count(old)
            value = value.replace(old, new)
        if count:
            changes.append({'kind': 'embedded_public_spec_withheld', 'task_id': spec['scene_id'],
                            'source': spec['source'], 'count': count})
    for old, new in replacements:
        count = value.count(old)
        if count:
            changes.append({'prefix': new, 'count': count})
            value = value.replace(old, new)
    return value.encode('utf-8'), changes


def keep_git(rel, size):
    if rel.name in {'LICENSE', 'COPYING', 'NOTICE'}:
        return True
    if rel.suffix in {'.py', '.sh', '.md', '.diff', '.csv', '.yaml', '.yml', '.toml', '.html', '.css', '.svg'}:
        return size <= 8_000_000
    if rel.suffix == '.json':
        return rel.name in CORE_JSON or rel.parts[0] in {'configs', 'metrics'} or size <= 262144
    if rel.name in {'system.txt', 'stage_events.jsonl'}:
        return True
    if rel == Path('render_attempts.jsonl'):
        return size <= 8_000_000
    if rel.suffix in {'.png', '.jpg', '.jpeg', '.webp'} and size <= 1_500_000:
        return rel.parts[0] in {'figures', 'reports'} or (rel.parts[:2] == ('meta_replay_stage', 'figures') and rel.name == 'replay_paired_points.png') or rel.name in {
            'final.png', 'reference.png', 'before.png', 'after.png', 'after_material.png',
            'after_move.png', 'object_map.png', 'functional_contact_sheet.png'}
    return False


def media_policy(source, manifest, file_paths):
    """Track exact source references and their CLI copies without content matching."""
    restricted = set()
    bw_ids = {row['scene_id'] for row in manifest if row['source_dataset'] != 'web_scenes'}
    approved_web = {row['scene_id'] for row in manifest if row['source_dataset'] == 'web_scenes'
                    and row['license'] and ('CC BY' in row['license'] or 'CC0' in row['license'] or 'public domain' in row['license'].lower())}
    for row in manifest:
        if row['scene_id'] not in approved_web:
            restricted.add(str(Path(row['image_path']).resolve()))
            restricted.update(str(Path(path).resolve()) for path in row.get('attachments', []))
    requests = [load(path) for path in file_paths if path.name == 'request.json' and path.with_name('session.json').exists()]
    for path in file_paths:
        if any(part in bw_ids for part in path.relative_to(source).parts):
            if 'reference' in path.name.lower() and path.suffix.lower() in MEDIA:
                restricted.add(str(path.resolve()))
    for _ in range(2):
        for request in requests:
            originals = request.get('original_images_for_audit', [])
            for original, staged in zip(originals, request.get('images', [])):
                original = str(Path(original).resolve())
                if original in restricted or ('BlenderWorld' in original and '/tasks/bw_' in original):
                    restricted.add(str(Path(staged).resolve()))
    return restricted, approved_web, bw_ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--bundles', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--pack', action='store_true')
    parser.add_argument('--only-group')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source, repo = args.source.resolve(), args.repo.resolve()
    destination = repo / EXPERIMENT
    if destination.resolve().is_relative_to(source):
        raise ValueError('Archive must be outside live experiment')
    manifest, state = load(source / 'manifest.json'), load(source / 'state.json')
    file_paths = list(paths(source))
    restricted, approved_web, bw_ids = media_policy(source, manifest, file_paths)
    embedded_specs = embedded_public_specs(source, manifest, file_paths)
    embedded_spec_index = [{key: value for key, value in spec.items() if key != 'body'} for spec in embedded_specs]
    home = Path.home().resolve()
    home_alias = '/home/' + home.name
    project = source.parents[1]
    replacements = [(str(source), '__EXPERIMENT_ROOT__'),
        (str(project), '__PROJECT_ROOT__'),
        (str(project.parent / 'files-pasted-by-the-user-sceneevolve'), '__SCENEEVOLVE_REPRO__'),
        (str(home / 'projects/BlenderWorld'), '__BLENDERWORLD_ROOT__'),
        (home_alias + '/projects/BlenderWorld', '__BLENDERWORLD_ROOT__'),
        (str(home / 'projects/e-harness/datasets/web_scenes'), '__COMMONS_DATA_ROOT__'),
        (home_alias + '/projects/e-harness/datasets/web_scenes', '__COMMONS_DATA_ROOT__'),
        (str(home), '__SERVER_USER_ROOT__'), (home_alias, '__SERVER_USER_ROOT__')]
    evaluated_ids = {load(path)['scene_id'] for path in file_paths if path.name == 'record.json'
                     and path.relative_to(source).parts[0] == 'results'
                     and load(path).get('bw', {}).get('evaluation_status') == 'completed'}
    unused_test_ids = {row['scene_id'] for row in manifest if row['split'] == 'test'} - evaluated_ids
    rows, exclusions, redactions = [], [], []
    groups = defaultdict(list)
    placeholder_files = {}
    for path in file_paths:
        rel = path.relative_to(source)
        reason = None
        if str(path.resolve()) in restricted:
            reason = 'reference_or_attachment_redistribution_license_not_confirmed'
        elif any(part in {'attachments', 'original_references'} for part in rel.parts):
            reason = 'original_reference_attachment_not_auto_licensed'
        elif any(scene_id in str(rel) for scene_id in unused_test_ids) and any('rubric' in part for part in rel.parts):
            reason = 'unused_reserved_test_rubric_not_published'
        elif rel.parts[0] == 'figures' and path.suffix.lower() in MEDIA and path.name not in SAFE_FIGURES:
            reason = 'composite_figure_reference_provenance_requires_review'
        if reason:
            exclusions.append({'relative_path':str(rel), 'reason':reason})
            if path.name == 'reference.png' or rel.parts[0] == 'figures':
                placeholder_files[rel] = placeholder(str(rel))
        group = group_for(rel)
        size = path.stat().st_size
        in_git = not reason and keep_git(rel, size)
        rows.append({'run_id':group, 'artifact_type':path.suffix.lstrip('.') or 'file',
            'relative_path':str(EXPERIMENT / rel), 'source_size_bytes':size, 'file_size_bytes':size,
            'git_status':'included' if in_git else 'withheld_license' if reason else 'release_only',
            'upload_status':'not_uploaded', 'not_uploaded_reason':reason or 'pending_Git_or_Release_upload',
            'bundle_name':'scene-rsi-v3-10rounds--' + group + '.tar.gz',
            'archive_group':group, 'download_url':'',
            'planned_download_url':f'https://github.com/i025/scene/releases/download/{args.tag}/scene-rsi-v3-10rounds--{group}.tar.gz'})
        if not reason:
            groups[group].append((path, rel))
        if args.dry_run or args.pack or not in_git:
            continue
        data = path.read_bytes()
        if SECRET.search(data):
            raise ValueError('Credential pattern requires review: ' + str(rel))
        if path.suffix in TEXT:
            data, changes = public_text(data, replacements, embedded_specs)
            if changes:
                redactions.append({'path':str(rel), 'changes':changes})
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows[-1]['file_size_bytes'] = len(data)
    reference_sources = {}
    for scene in manifest:
        if scene['scene_id'] in approved_web:
            candidates = [path for path in file_paths if path.name == 'reference.png' and scene['scene_id'] in path.relative_to(source).parts]
            original = candidates[0] if candidates else Path(scene['image_path'])
            rel = Path('data/public_references') / (scene['scene_id'] + original.suffix.lower())
            reference_sources[scene['scene_id']] = (original,rel)
            groups['preparation'].append((original,rel))
            size = original.stat().st_size
            rows.append({'run_id':'preparation','artifact_type':'licensed_reference_copy','relative_path':str(EXPERIMENT/rel),
                'source_size_bytes':size,'file_size_bytes':size,'git_status':'included','upload_status':'not_uploaded',
                'not_uploaded_reason':'pending_Git_or_Release_upload','bundle_name':'scene-rsi-v3-10rounds--preparation.tar.gz',
                'archive_group':'preparation','download_url':'',
                'planned_download_url':f'https://github.com/i025/scene/releases/download/{args.tag}/scene-rsi-v3-10rounds--preparation.tar.gz'})
    receipt = {'experiment':str(EXPERIMENT), 'source_status':state, 'source_files_untouched':True,
        'new_model_calls':0, 'new_render_frames':0, 'archive_created':time.time(),
        'indexed_artifacts':len(rows), 'groups':{key:len(value) for key,value in groups.items()},
        'all_experiment_terminal_required':False, 'phase_is_not_completion_evidence':True,
        'raw_logs_policy':'All permitted existing raw logs and generated outputs enter Release groups, including failed/incomplete records',
        'path_redactions':'Text-only prefix replacement and declared embedded public spec body withholding; original live files unchanged; binary .blend bytes not rewritten',
        'reference_policy':'Unlicensed original BW media, derived reference copies and attachments withheld from Git and Release; generated scene renders preserved',
        'embedded_public_spec_policy':'Bodies extracted only from existing generated task.json public_attachment_sources/instruction; raw attachment files and unused reserved Test specs never opened; plain and JSON-escaped bodies replaced by labelled WITHHELD markers in Git and Release; role/usage/budget/failure retained',
        'embedded_public_spec_sources':embedded_spec_index,
        'binary_policy':'No binary content mutation except explicitly labelled public reference placeholders',
        'path_placeholders':{new:'External resource or run root; configure locally before running' for old,new in replacements}}
    if args.dry_run:
        print(json.dumps({'dry_run':True,'receipt':receipt,'withheld':len(exclusions)}, ensure_ascii=False, indent=2)); return
    args.bundles.mkdir(parents=True, exist_ok=True)
    if args.pack:
        for group, files in sorted(groups.items()):
            if args.only_group and args.only_group != group:
                continue
            target = args.bundles / ('scene-rsi-v3-10rounds--' + group + '.tar.gz')
            if target.exists():
                raise FileExistsError('Never overwrite a previously packaged archive: ' + str(target))
            with tarfile.open(target, 'w:gz', compresslevel=1) as archive:
                for path, rel in files:
                    data = path.read_bytes()
                    if SECRET.search(data):
                        raise ValueError('Credential pattern requires review: ' + str(rel))
                    if path.suffix in TEXT:
                        data, changes = public_text(data, replacements, embedded_specs)
                        if changes:
                            redactions.append({'path':str(rel), 'changes':changes})
                    item = tarfile.TarInfo(str(EXPERIMENT / rel)); item.size = len(data)
                    item.mtime = int(path.stat().st_mtime); item.mode = 0o644
                    archive.addfile(item, io.BytesIO(data))
                notes = json.dumps({'archive_group':group, 'source_phase':state,
                    'license_exclusions':exclusions, 'source_state_captured_at_pack_start':True,
                    'reference_attribution':[{key:scene[key] for key in ['scene_id','title','author','license','license_url','source_page']}
                                              for scene in manifest if scene['scene_id'] in approved_web]}, ensure_ascii=False, indent=2).encode()
                item = tarfile.TarInfo(str(EXPERIMENT / 'release_notes' / (group + '.json'))); item.size = len(notes)
                archive.addfile(item, io.BytesIO(notes))
            if target.stat().st_size >= 2_000_000_000:
                raise ValueError('Archive exceeds 2 GB Release asset limit; split the named group')
            print(json.dumps({'group':group, 'files':len(files), 'bytes':target.stat().st_size, 'path':str(target)}), flush=True)
        write_json(args.bundles / 'PACK_RECEIPT.json', receipt)
        write_json(args.bundles / 'PACK_REDACTIONS.json', redactions)
        return
    destination.mkdir(parents=True, exist_ok=True)
    for rel, data in placeholder_files.items():
        target = destination / rel; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    reference_map, attribution = {}, []
    for scene in manifest:
        scene_id = scene['scene_id']
        if scene_id in approved_web:
            original, rel = reference_sources[scene_id]
            data = original.read_bytes()
            if SECRET.search(data):raise ValueError('Unexpected credential pattern in public reference')
            target = destination / rel; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
            reference_map[scene_id] = {'path':str(rel), 'status':'licensed_web_reference',
                'source_page':scene['source_page'], 'license':scene['license'], 'author':scene['author']}
            attribution.append(f"- {scene_id}: {scene['title']} — {scene['author']}; {scene['license']}; {scene['source_page']}; {scene['license_url']}")
        else:
            rel = Path('data/withheld_references') / (scene_id + '.png')
            target = destination / rel; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(placeholder(scene_id))
            reference_map[scene_id] = {'path':str(rel), 'status':'withheld_license_placeholder',
                'reason':'Original source media license does not establish redistribution permission in this archive'}
    write_json(destination / 'data/public_reference_map.json', reference_map)
    (destination / 'data/ATTRIBUTION_WEB.md').write_text('# 本次公开参考媒体归属\n\n只公开明确标注CC许可的web_scenes参考图片；BlenderWorld原始参考及附件只记录来源路径和ID，不公开媒体。\n\n' + '\n'.join(attribution) + '\n')
    fields = ['run_id','artifact_type','relative_path','source_size_bytes','file_size_bytes','git_status',
              'upload_status','not_uploaded_reason','bundle_name','archive_group','download_url','planned_download_url']
    write_csv(repo / 'artifacts_index_v3.csv', rows, fields)
    write_json(repo / 'docs/V3_ARCHIVE_STATE.json', receipt)
    write_json(repo / 'docs/V3_REDACTIONS.json', {'text_path_fields':redactions, 'license_exclusions':exclusions,
               'embedded_public_spec_sources':embedded_spec_index,
               'raw_originals':'unchanged on original server', 'credentials_read':False,
               'placeholder_policy':'Any replacement placeholder is visibly labelled and never counted as an experimental result'})
    print(json.dumps({'indexed':len(rows), 'git_files':sum(row['git_status']=='included' for row in rows),
                      'withheld_license':len(exclusions), 'groups':sorted(groups), 'source_phase':state.get('phase')}, ensure_ascii=False))


if __name__ == '__main__':
    for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key] = '1'
    main()
