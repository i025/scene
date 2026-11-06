"""Confirm public V2.4 branch, core evidence and four Release assets; read only."""
from pathlib import Path
from urllib.parse import quote
import argparse
import csv
import io
import json
import time
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
TAG = 'scene-rsi-v2.4-2026-11-06'
BRANCH = 'research/scene-rsi-v2.4'
EXP = 'experiments/scene_rsi_v2_4/'
BUNDLES = {'fixed.tar.gz', 'structured.tar.gz', 'active.tar.gz', 'shared-evidence.tar.gz'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True, help='Actual pushed scientific/final commit ID')
    parser.add_argument('--repo', type=Path, default=ROOT/'archive/scene')
    parser.add_argument('--final', action='store_true', help='Write FINAL rather than CORE local receipt')
    parser.add_argument('--write-docs', action='store_true', help='Also write public verification receipts in repo/docs')
    args = parser.parse_args()
    api = 'https://api.github.com/repos/i025/scene'
    session = requests.Session()
    # Keep network proxy routing while avoiding implicit .netrc authentication.
    session.trust_env = False
    session.proxies.update(requests.utils.get_environ_proxies(api))
    session.headers.update({'Accept': 'application/vnd.github+json'})
    requested = session.get(api+'/commits/'+quote(args.commit, safe=''), timeout=30)
    requested.raise_for_status()
    commit = requested.json()['sha']
    branch = session.get(api+'/branches/'+quote(BRANCH, safe=''), timeout=30)
    branch.raise_for_status()
    assert branch.json()['commit']['sha'] == commit, 'Requested commit is not the actual V2.4 branch head'
    paths = ['README.md', 'UPLOAD_SUMMARY_V2_4.md', 'docs/AS_RUN_PROTOCOL_V2_4.md',
        'docs/REVIEW_INDEX_V2_4.md', 'docs/COMMANDS_V2_4.md', 'scripts/offline_v2_4.py']
    paths += [EXP+name for name in ['experiment.py', 'meta.py', 'inspect_blend.py', 'analyze.py', 'audit_results.py',
        'backend/runtime.py', 'fixed_h/r1_C2/policy.py', 'tasks/task01/active/H/policy.py',
        'metrics/scene_metrics.csv', 'metrics/candidates.csv', 'metrics/summary.json', 'metrics/implementation_audit.json',
        'reports/index.html', 'reports/REPORT_ZH.md', 'figures/figure1_failure_audit.png',
        'figures/figure3_actual_diagnostics.png', 'figures/figure4_fresh_reconstructions.png',
        'figures/figure4_selected_transfer.png', 'figures/figure4_shared_H_diff.png',
        'figures/figure5_results_cost.png', 'figures/figure6_real_edit_preservation.png']]
    records = []
    for path in paths:
        url = 'https://raw.githubusercontent.com/i025/scene/'+commit+'/'+path
        response = session.get(url, timeout=30)
        response.raise_for_status()
        row = {'path': path, 'url': url, 'http_status': response.status_code,
               'bytes_read': len(response.content), 'anonymous': True}
        if path.endswith('.png'):
            with Image.open(io.BytesIO(response.content)) as picture:
                picture.load(); row['decoded_image_size'] = list(picture.size)
        if path.endswith('scene_metrics.csv'):
            rows = list(csv.DictReader(io.StringIO(response.text)))
            row['formal_rows'] = sum(item['scope'] == 'formal' for item in rows)
            assert row['formal_rows'] == 16
        if path.endswith('candidates.csv'):
            row['candidate_rows'] = len(list(csv.DictReader(io.StringIO(response.text))))
            assert row['candidate_rows'] == 6
        records.append(row)
    state = json.loads((args.repo/'docs/V2_4_RELEASE_UPLOAD_STATE.json').read_text())
    assert state['tag'] == TAG and state['remote_asset_listing_verified']
    assert {asset['name'] for asset in state['assets']} == BUNDLES
    release = session.get(api+'/releases/tags/'+TAG, timeout=30)
    release.raise_for_status()
    listing = session.get(api+'/releases/'+str(release.json()['id'])+'/assets', timeout=30)
    listing.raise_for_status()
    remote = {asset['name']: asset for asset in listing.json()}
    assert set(remote) == BUNDLES, 'Require exactly four V2.4 Release assets'
    checks = []
    for asset in state['assets']:
        public = remote[asset['name']]
        assert public['size'] == asset['size_bytes'] and public['browser_download_url'] == asset['url']
        response = session.head(public['browser_download_url'], allow_redirects=True, timeout=45)
        response.raise_for_status()
        length = int(response.headers['Content-Length']) if 'Content-Length' in response.headers else None
        if length is not None:
            assert length == public['size'], asset['name']
        checks.append({'name': asset['name'], 'public_url': public['browser_download_url'],
            'http_status': response.status_code, 'size_bytes_from_GitHub_API': public['size'],
            'HTTP_Content_Length': length, 'HTTP_size_verified': length is not None,
            'API_size_matches_upload_receipt': True, 'anonymous': True})
    receipt = {'time': time.time(), 'commit': commit, 'requested_commit': args.commit, 'branch': BRANCH,
        'actual_branch_head_verified': True, 'tag': TAG, 'release_url': release.json()['html_url'],
        'core_files': records, 'release_assets': checks, 'new_model_calls': 0, 'new_Blender_jobs': 0,
        'credentials_saved_or_read': False, 'no_content_hash_verification': True,
        'limits': 'Public HTTP reads and recorded sizes confirm accessibility; archives are not downloaded or compared by content.'}
    name = 'FINAL_REMOTE_VERIFICATION.json' if args.final else 'CORE_REMOTE_VERIFICATION.json'
    (WORK/name).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    if args.write_docs:
        (args.repo/'docs/V2_4_REMOTE_CONTENT_CHECK.json').write_text(json.dumps(
            {'commit': commit, 'branch': BRANCH, 'actual_branch_head_verified': True, 'files': records}, ensure_ascii=False, indent=2)+'\n')
        (args.repo/'docs/V2_4_REMOTE_ASSET_CHECK.json').write_text(json.dumps(
            {'tag': TAG, 'release_url': release.json()['html_url'], 'assets': checks, 'all_publicly_readable': True}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'commit': commit, 'branch': BRANCH, 'public_core_files_verified': len(records),
        'public_assets_verified': len(checks), 'asset_bytes': sum(row['size_bytes_from_GitHub_API'] for row in checks)}))


if __name__ == '__main__':
    main()
