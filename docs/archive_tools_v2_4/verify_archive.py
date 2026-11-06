"""Verify V2.4 archive paths, recorded sizes and local media; no Blender/models."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import argparse
import csv
import json
import re
import tarfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
EXPERIMENT = Path('experiments/scene_rsi_v2_4')
BUNDLES = {'fixed.tar.gz', 'structured.tar.gz', 'active.tar.gz', 'shared-evidence.tar.gz'}
TEXT = {'.py', '.sh', '.json', '.jsonl', '.txt', '.log', '.md', '.diff', '.yaml', '.yml', '.csv', '.html', '.css'}


def read(path):
    return json.loads(path.read_text())


def csv_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in ['href', 'src'] and value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT/'archive/scene')
    parser.add_argument('--source', type=Path, default=ROOT/'outputs/scene_rsi_v2_4')
    parser.add_argument('--bundles', type=Path, default=WORK/'bundles')
    parser.add_argument('--write-docs', action='store_true', help='Also save public verification receipts in repo/docs')
    args = parser.parse_args()
    repo, source, bundles = args.repo.resolve(), args.source.resolve(), args.bundles.resolve()
    rows = csv_rows(repo/'artifacts_index_v2_4.csv')
    index = {row['relative_path']: row for row in rows}
    assert len(index) == len(rows), 'Duplicate indexed artifact paths'
    paths = sorted(bundles.glob('*.tar.gz'))
    assert {path.name for path in paths} == BUNDLES, 'Require exactly four V2.4 bundles'
    changed = {entry['path'] for path in bundles.glob('pack_redactions*.json') for entry in read(path)}
    packed, assets, redacted_sizes = {}, [], []
    for path in paths:
        with tarfile.open(path) as archive:
            members = [member for member in archive.getmembers() if member.isfile() or member.issym()]
            for member in members:
                assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                assert member.name not in packed, 'Duplicate archive member: '+member.name
                assert member.name in index, 'Unindexed archive member: '+member.name
                row = index[member.name]
                assert row['bundle_name'] == path.name, 'Wrong bundle ownership: '+member.name
                packed[member.name] = {'bundle': path.name, 'size': member.size, 'symlink': member.issym()}
                if member.issym():
                    continue
                if row['git_status'] == 'included':
                    assert member.size == int(row['public_git_size_bytes']), member.name
                elif member.name not in changed or Path(member.name).suffix not in TEXT | {'.png'}:
                    assert member.size == int(row['size_bytes']), member.name
                else:
                    redacted_sizes.append({'path': member.name, 'original_bytes': int(row['size_bytes']),
                        'public_bytes': member.size, 'basis': 'Explicitly recorded text/PNG metadata redaction; length may change'})
        assets.append({'name': path.name, 'bytes': path.stat().st_size, 'members': len(members)})
    assert set(index) == set(packed), (len(set(index)-set(packed)), len(set(packed)-set(index)))
    original_sizes_checked = 0
    for name, row in index.items():
        relative = Path(name).relative_to(EXPERIMENT)
        original = source/relative
        if source.exists():
            assert original.exists(), 'Original indexed path missing: '+str(relative)
            assert original.stat().st_size == int(row['size_bytes']), 'Original size changed: '+str(relative)
            original_sizes_checked += 1
        if row['git_status'] == 'included':
            assert (repo/name).stat().st_size == int(row['public_git_size_bytes']), name
    scenes = csv_rows(repo/EXPERIMENT/'metrics/scene_metrics.csv')
    formal = [row for row in scenes if row['scope'] == 'formal']
    candidates = csv_rows(repo/EXPERIMENT/'metrics/candidates.csv')
    assert len(formal) == 16 and len(candidates) == 6, (len(formal), len(candidates))
    assert len({(r['task_id'], r['method'], r['role']) for r in formal}) == 16
    assert len({(r['task_id'], r['method']) for r in candidates}) == 6
    images = []
    for path in sorted((repo/EXPERIMENT).rglob('*.png')):
        with Image.open(path) as picture:
            picture.load()
            images.append({'path': str(path.relative_to(repo)), 'size': list(picture.size)})
    pending_release, missing = [], []
    documents = [repo/'README.md', repo/'UPLOAD_SUMMARY_V2_4.md', repo/'docs/REVIEW_INDEX_V2_4.md',
                 repo/EXPERIMENT/'reports/index.html', repo/EXPERIMENT/'reports/REPORT_ZH.md']
    for document in documents:
        assert document.exists(), document
        if document.suffix == '.html':
            parser = Links(); parser.feed(document.read_text()); targets = parser.targets
        else:
            targets = re.findall(r'\]\(([^)]+)\)', document.read_text())
        for target in targets:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            target_path = (document.parent/unquote(url.path)).resolve()
            assert target_path.is_relative_to(repo), 'Nonportable local link: '+target
            if target_path.exists():
                continue
            name = str(target_path.relative_to(repo))
            item = {'document': str(document.relative_to(repo)), 'target': target, 'artifact_path': name}
            if name in index and index[name]['git_status'] == 'release_only' and name.endswith('.blend'):
                pending_release.append(item)
            else:
                missing.append(item)
    assert not missing, missing
    blends = [name for name in packed if name.endswith('.blend')]
    coverage = {'indexed_files': len(index), 'packed_files': len(packed), 'all_indexed_paths_covered': True,
        'bundle_membership_verified': True, 'bundle_sizes': assets, 'blend_files_in_Release': len(blends),
        'source_sizes_checked': original_sizes_checked, 'source_size_check_available': source.exists(),
        'redacted_release_sizes': redacted_sizes, 'formal_CSV_rows': len(formal), 'candidate_CSV_rows': len(candidates),
        'verification': 'Ordinary path membership and recorded byte sizes; no hashes or checksums',
        'new_model_calls': 0, 'new_Blender_jobs': 0, 'new_render_frames': 0}
    media = {'PNG_files_decoded': len(images), 'all_decoded': True, 'images': images,
        'relative_links_checked': True, 'missing_local_required_links': missing,
        'blend_links_available_in_Release_but_not_overlaid': pending_release,
        'all_blend_files_locally_available': all((repo/name).exists() for name in blends),
        'blend_opening_not_performed': True,
        'meaning': 'Missing release_only .blend is an overlay availability state, not a reconstruction failure.'}
    receipt = {'coverage': coverage, 'media': media}
    (WORK/'LOCAL_ARCHIVE_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    if args.write_docs:
        (repo/'docs/V2_4_ARCHIVE_COVERAGE.json').write_text(json.dumps(coverage, ensure_ascii=False, indent=2)+'\n')
        (repo/'docs/V2_4_LOCAL_MEDIA_CHECK.json').write_text(json.dumps(media, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'indexed': len(index), 'bundles': len(assets), 'formal_rows': len(formal),
        'candidates': len(candidates), 'decoded_PNG': len(images), 'pending_blend_links': len(pending_release)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
