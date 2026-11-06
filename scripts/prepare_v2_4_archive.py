"""V2.4 natural-image evidence archive, minimally adapted from V2.3.

Never follow external resource paths or collect entire historical experiment roots.
Historical logs must first be selectively copied under audit_sources and labelled.
"""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import tarfile
import time
from PIL import Image, PngImagePlugin

TEXT = {'.py', '.sh', '.json', '.jsonl', '.txt', '.log', '.md', '.diff',
        '.yaml', '.yml', '.csv', '.html', '.css'}
EXPERIMENT = Path('experiments/scene_rsi_v2_4')
TAG = 'scene-rsi-v2.4-2026-11-06'
BASE_URL = 'https://github.com/i025/scene/releases/download/' + TAG + '/'
SECRET = re.compile(r'(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def bundle_for(rel):
    # Preserve method ownership even for smoke/failed/preparation-history records.
    for method in ('fixed', 'structured', 'active'):
        if method in rel.parts:
            return method
    return 'shared-evidence'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--bundles', type=Path, required=True)
    parser.add_argument('--pack', action='store_true')
    parser.add_argument('--only-bundle', help='Repack one named group; existing bundles are never overwritten')
    args = parser.parse_args()
    source, repo = args.source.resolve(), args.repo.resolve()
    destination = repo / EXPERIMENT
    destination.mkdir(parents=True, exist_ok=True)
    args.bundles.mkdir(parents=True, exist_ok=True)
    final = json.loads((source / 'FINAL_STATUS.json').read_text())
    if final['phase'] != 'all_scheduled_terminal':
        raise RuntimeError('Archive only after V2.4 scheduled work is terminal')
    manifest = json.loads((source / 'manifest.json').read_text())
    used_ids = set()
    for path in list((source / 'results').glob('*/*/*/*/*/record.json')) + list((source / 'tasks').glob('*/evidence/record.json')):
        used_ids.add(json.loads(path.read_text())['scene_id'])
    selected_ids = {entry[role]['scene_id'] for entry in manifest
                    for role in ('source', 'transfer') if entry[role] is not None}
    if selected_ids - used_ids:
        raise ValueError('Manifest includes unaccessed source/test labels; withhold them before publication: '
                         + ', '.join(sorted(selected_ids - used_ids)))
    home = source.parents[5]
    # Public path placeholders preserve relationships while removing server account names.
    replacements = [
        (str(source), '__EXPERIMENT_ROOT__'),
        (str(source.parents[2] / 'files-pasted-by-the-user-sceneevolve'), '__SCENEEVOLVE_REPRO__'),
        (str(home / 'projects/BlenderWorld'), '__BLENDERWORLD_ROOT__'),
        (str(home / 'projects/e-harness/datasets/web_scenes'), '__COMMONS_DATA_ROOT__'),
        (str(home), '__SERVER_USER_ROOT__'),
        ('/home/' + home.name, '__SERVER_USER_ROOT__'),
    ]
    redactions, excluded, inventory = [], [], []
    groups = {}

    def public_bytes(path, rel):
        data = path.read_bytes()
        if path.suffix not in TEXT:
            changes = 0
            if path.suffix == '.png' and any(prefix.encode() in data for prefix in [str(home), '/home/' + home.name]):
                # PNG text metadata must be encoded by its image writer. Byte replacement
                # damages the container; retain decoded pixels and sanitize only metadata.
                picture = Image.open(path)
                metadata = PngImagePlugin.PngInfo()
                for key, value in picture.info.items():
                    if isinstance(value, str):
                        for old, new in replacements:
                            value = value.replace(old, new)
                        metadata.add_text(key, value)
                output = io.BytesIO()
                picture.save(output, format='PNG', pnginfo=metadata, exif=b'')
                data = output.getvalue()
                assert Image.open(io.BytesIO(data)).tobytes() == picture.tobytes()
                redactions.append({'path': str(EXPERIMENT / rel),
                                   'changes': 'png_metadata_paths_sanitized_exif_removed_decoded_pixels_unchanged'})
            for prefix in [str(home).encode(), ('/home/' + home.name).encode()]:
                replacement = prefix[:-len(home.name)] + b'_' * len(home.name)
                changes += data.count(prefix)
                data = data.replace(prefix, replacement)
            if changes:
                redactions.append({'path': str(EXPERIMENT / rel),
                                   'changes': 'binary_account_path_equal_length:' + str(changes)})
            if SECRET.search(data.decode('latin1')):
                raise ValueError('Credential pattern in binary: ' + str(rel))
            return data
        text = data.decode('utf-8')
        changes = []
        for old, new in replacements:
            count = text.count(old)
            if count:
                text = text.replace(old, new)
                changes.append('server_path:' + str(count))
        if re.search(r'\b' + re.escape(home.name) + r'\b', text):
            text = re.sub(r'\b' + re.escape(home.name) + r'\b', 'SERVER_USER', text)
            changes.append('server_account_name')
        if SECRET.search(text):
            raise ValueError('Credential pattern requires manual review: ' + str(rel))
        if changes:
            redactions.append({'path': str(EXPERIMENT / rel), 'changes': '|'.join(changes)})
        return text.encode('utf-8')

    def keep_in_git(rel, size):
        if rel.name == 'stage_events.jsonl':
            return True
        if rel.name == 'response.txt' and rel.parent.name in ('common_diagnosis', 'diagnosis', 'coding') and size <= 262144:
            # Small structured diagnosis/coding responses support offline review.
            return True
        if rel.suffix.lower() in ('.png','.jpg','.jpeg') and size <= 1_000_000:
            if rel.name in ('reference.png','final.png','source_repaired.png','transfer_repaired.png','object_map.png','probe.png','before.png','after_material.png','after_move.png') or rel.name.startswith('probe_'):
                return True
        if rel.name in ('system.txt','proposer.txt','LICENSE','codex-help.txt','codex-exec-help.txt','codex-version.txt'):
            return True
        if rel.parts[0] in ('reports','figures'):
            return rel.suffix in TEXT or rel.suffix in ('.png', '.jpg')
        if rel.parts[0] == 'metrics' and rel.suffix == '.json':
            return True
        if rel.suffix == '.json' and (rel.name in {
                'config.json', 'manifest.json', 'state.json', 'FINAL_STATUS.json', 'STATUS_AUDIT.json',
                'candidate.json', 'stage1.json', 'stage2.json', 'observations.json', 'record.json',
                'session.json', 'request.json', 'selection_freeze.json', 'all_candidates_frozen.json', 'freeze.json'}
                or rel.parent == Path('audit_sources')):
            # Required report inputs and historical audit snapshots stay directly readable.
            return True
        if rel.suffix in ('.py', '.sh', '.md', '.diff', '.yaml', '.yml', '.csv'):
            return True
        if rel.suffix == '.json' and size <= 262144:
            return True
        return rel.parent == Path('.') and rel.suffix == '.txt'

    for base, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in ('__pycache__', '.git', 'node_modules', 'matplotlib_cache', '.venv', 'venv', 'model-cache'))
        names += [d for d in dirs if (Path(base) / d).is_symlink()]
        dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
        for name in sorted(names):
            path = Path(base) / name
            rel = path.relative_to(source)
            if path.suffix in ('.pyc', '.cubin', '.zst') or name in ('.env', 'auth.json', 'credentials.json', '.netrc', 'id_rsa', 'id_ed25519'):
                excluded.append({'path': str(rel), 'reason': 'cache_or_credential_file_not_published'})
                continue
            group = bundle_for(rel)
            groups.setdefault(group, []).append((path, rel))
            if args.pack:
                continue
            if path.is_symlink():
                target = path.resolve()
                if not target.is_relative_to(source):
                    excluded.append({'path': str(rel), 'reason': 'external_dependency_link; source not copied'})
                    continue
                data = None
                size = target.stat().st_size if target.exists() else 0
            else:
                size = path.stat().st_size
                data = public_bytes(path, rel) if keep_in_git(rel, size) else None
            public = destination / rel
            git_copy = keep_in_git(rel, size) and data is not None
            if git_copy:
                public.parent.mkdir(parents=True, exist_ok=True)
                public.write_bytes(data)
            origin = ('historical_V2_1_V2_2_audit_copy' if rel.parts[0] == 'audit_sources' else
                      'historical_V2_2_reconstruction_copy' if len(rel.parts) == 4 and rel.parts[0] == 'tasks' and rel.parts[2] == 'evidence' else
                      'historical_H_reused_as_V2_4_start' if rel.parts[0] == 'fixed_h' else 'V2_4_current')
            scientific_run = rel.parts[1] if len(rel.parts) > 1 and rel.parts[0] in ('tasks', 'results') and rel.parts[1].startswith(('task', 'smoke')) else 'common_or_historical'
            inventory.append({'run_id': scientific_run, 'archive_group': group,
                              'method': group if group in ('fixed', 'structured', 'active') else None,
                              'evidence_origin': origin, 'artifact_type': path.suffix.lstrip('.') or 'file',
                              'relative_path': str(EXPERIMENT / rel), 'download_url': '',
                              'size_bytes': size, 'size_basis': 'original_local_artifact_bytes_before_path_redaction', 'public_git_size_bytes': len(data) if git_copy else '', 'git_status': 'included' if git_copy else 'release_only',
                              'upload_status': 'pending',
                              'not_uploaded_reason': 'source_symlink_target_missing' if path.is_symlink() and not path.resolve().exists() else '',
                              'bundle_name': group + '.tar.gz'})
    if args.pack:
        for group, files in sorted(groups.items()):
            if args.only_bundle and group != args.only_bundle:
                continue
            target = args.bundles / (group + '.tar.gz')
            if target.exists():
                raise FileExistsError('Do not overwrite an existing bundle: ' + str(target))
            total = 0
            with tarfile.open(target, 'w:gz', compresslevel=1, dereference=False) as archive:
                for path, rel in files:
                    arcname = str(EXPERIMENT / rel)
                    if path.is_symlink():
                        resolved = path.resolve()
                        if not resolved.is_relative_to(source):
                            continue
                        info = tarfile.TarInfo(arcname)
                        info.type = tarfile.SYMTYPE
                        info.linkname = os.path.relpath(resolved, path.parent)
                        archive.addfile(info)
                    else:
                        data = public_bytes(path, rel)
                        info = tarfile.TarInfo(arcname)
                        info.size = len(data)
                        info.mtime = int(path.stat().st_mtime)
                        info.mode = 0o755 if path.suffix == '.sh' else 0o644
                        archive.addfile(info, io.BytesIO(data))
                    total += 1
            print(json.dumps({'bundle': target.name, 'files': total, 'bytes': target.stat().st_size}), flush=True)
            if target.stat().st_size >= 2_000_000_000:
                raise ValueError('Bundle exceeds conservative release asset bound: ' + str(target))
        name = 'pack_redactions_' + args.only_bundle + '.json' if args.only_bundle else 'pack_redactions.json'
        (args.bundles / name).write_text(json.dumps(redactions, ensure_ascii=False, indent=2))
        return
    fields = ['run_id', 'archive_group', 'method', 'evidence_origin', 'artifact_type', 'relative_path', 'download_url', 'size_bytes', 'size_basis', 'public_git_size_bytes', 'git_status',
              'upload_status', 'not_uploaded_reason', 'bundle_name']
    write_csv(repo / 'artifacts_index_v2_4.csv', inventory, fields)
    (repo / 'docs').mkdir(exist_ok=True)
    (repo / 'docs/V2_4_REDACTIONS.json').write_text(json.dumps({'server_paths': 'replaced with documented placeholders',
        'used_natural_image_source_ids': sorted(selected_ids), 'unaccessed_source_labels_in_manifest': 0, 'raw_originals': 'retained unchanged on the server',
        'credential_scan_matches': 0, 'files': redactions, 'excluded_files': excluded}, ensure_ascii=False, indent=2))
    (repo / 'docs/V2_4_ARCHIVE_STATE.json').write_text(json.dumps({'created': time.time(), 'experiment': str(EXPERIMENT),
        'source_status': final['phase'], 'last_live_state_preserved': 'state.json', 'completion_audit': 'STATUS_AUDIT.json',
        'archive_only_new_model_calls': 0, 'archive_only_new_render_frames': 0, 'source_files_untouched': True,
        'archive_scope': 'all existing V2.4 fixed/structured/active records, shared evidence, natural-image source and transfer attempts, smoke, snapshots, candidates and failures; selectively copied historical evidence explicitly labelled; no new execution',
        'JSON_policy': 'All raw JSON retained in Release; Git includes required record/decision/session/config/metrics/audit snapshot inputs and other JSON <=262144 bytes. Large geometry snapshots are release_only, never omitted.',
        'bundles': sorted(group + '.tar.gz' for group in groups),
        'path_placeholders': dict((new, 'external resource; see V2.4 dependency documentation') for old, new in replacements)}, ensure_ascii=False, indent=2))
    print(json.dumps({'indexed_files': len(inventory), 'git_files': sum(r['git_status']=='included' for r in inventory),
                      'bundles': len(groups), 'natural_image_manifest': 'selected actually accessed source/transfer images; original attribution retained'}))


if __name__ == '__main__':
    main()
