"""Minimal anonymous remote reads after publishing; no model, Blender or hashes."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image
import requests

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
BRANCH = 'research/scene-rsi-v3-10rounds'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--repo', type=Path, default=ROOT / 'archive' / 'scene')
    parser.add_argument('--release-state', default='docs/V3_RELEASE_UPLOAD_STATE.json')
    parser.add_argument('--png', default='experiments/scene_rsi_v3/figures/shared_patch_case.png')
    args = parser.parse_args()
    receipt = {'requested_commit': args.commit, 'branch': BRANCH, 'time': time.time(),
               'core_files': [], 'release_assets': [], 'complete': False,
               'new_model_calls': 0, 'new_Blender_jobs': 0, 'credentials_read': False,
               'limits': 'Anonymous HTTP readability and file sizes only; archives are not downloaded or compared by content'}
    output = WORK / 'REMOTE_VERIFICATION.json'
    def save():
        output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    save()
    environment = os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    remote = subprocess.check_output(['git', '-c', 'http.version=HTTP/1.1', 'ls-remote',
        'https://github.com/i025/scene.git', 'refs/heads/' + BRANCH], text=True, timeout=60, env=environment)
    head = remote.split()[0] if remote.strip() else None
    if head != args.commit:
        raise ValueError('Requested commit is not the actual pushed V3 branch head')
    receipt['actual_branch_head_verified'] = True
    save()
    session = requests.Session()
    session.trust_env = False
    session.proxies.update(requests.utils.get_environ_proxies('https://api.github.com'))
    paths = ['README.md', 'experiments/scene_rsi_v3/pilot.py',
             'experiments/scene_rsi_v3/metrics/rounds.csv', 'experiments/scene_rsi_v3/metrics/scenes.csv',
             'experiments/scene_rsi_v3/metrics/actions.csv', 'experiments/scene_rsi_v3/reports/index.html', args.png,
             'docs/V3_REVIEW_INDEX.md', 'experiments/scene_rsi_v3/finish_test.py',
             'experiments/scene_rsi_v3/metrics/final_test_raw.csv',
             'experiments/scene_rsi_v3/metrics/final_test_sources.csv',
             'experiments/scene_rsi_v3/metrics/final_completion_cost_delta.csv',
             'experiments/scene_rsi_v3/reports/FINAL_TEST_SUMMARY_ZH.md',
             'experiments/scene_rsi_v3/reports/M07_REVIEW_ZH.md',
             'experiments/scene_rsi_v3/figures/final_test_contact_sheet.png',
             'experiments/scene_rsi_v3/figures/final_test_quality.png',
             'experiments/scene_rsi_v3/figures/M07_action_evidence.png',
             'experiments/scene_rsi_v3/PROTOCOL_AMENDMENT_07.md',
             'experiments/scene_rsi_v3/A07_EDIT_RECOVERY.json',
             'experiments/scene_rsi_v3/recover_edits.py',
             'experiments/scene_rsi_v3/figures/semantic_edit_results.png']
    for path in paths:
        url = f'https://raw.githubusercontent.com/i025/scene/{args.commit}/{path}'
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            receipt['failure'] = {'stage': 'core_read', 'path': path, 'http_status': response.status_code}; save()
        response.raise_for_status()
        item = {'path': path, 'url': url, 'http_status': response.status_code, 'bytes_read': len(response.content)}
        if path.endswith('.csv'):
            item['rows'] = len(list(csv.DictReader(io.StringIO(response.text))))
        if path.endswith('.png'):
            with Image.open(io.BytesIO(response.content)) as image:
                image.load(); item['decoded_size'] = list(image.size)
        receipt['core_files'].append(item); save()
    local = json.loads((args.repo / args.release_state).read_text())
    response = session.get('https://api.github.com/repos/i025/scene/releases/tags/' + local['tag'], timeout=30)
    if response.status_code != 200:
        receipt['failure'] = {'stage': 'public_release_listing', 'http_status': response.status_code,
                              'reason': 'No repeated retries; API limit or permission must be reported'}; save()
    response.raise_for_status()
    release = response.json()
    response = session.get('https://api.github.com/repos/i025/scene/releases/' + str(release['id']) + '/assets',
                           params={'per_page': 100}, timeout=30)
    response.raise_for_status()
    assets = {a['name']: a for a in response.json()}
    for item in local['assets']:
        asset = assets[item['name']]
        if asset['state'] != 'uploaded' or asset['size'] != item['size_bytes'] or asset['browser_download_url'] != item['url']:
            raise ValueError('Release listing differs from upload receipt: ' + item['name'])
        response = session.head(item['url'], allow_redirects=True, timeout=45)
        response.raise_for_status()
        length = int(response.headers['Content-Length']) if 'Content-Length' in response.headers else None
        if length is not None and length != asset['size']:
            raise ValueError('Public asset HEAD length differs: ' + item['name'])
        receipt['release_assets'].append({'name': item['name'], 'url': item['url'], 'size_bytes': asset['size'],
                                          'public_http_status': response.status_code, 'public_asset_state': asset['state'], 'http_content_length': length})
        save()
    receipt.update(complete=True, release_url=release['html_url']); save()
    print(json.dumps({'commit': args.commit, 'core_files_read': len(receipt['core_files']),
                      'assets_readable': len(receipt['release_assets']), 'receipt': str(output)}))


if __name__ == '__main__':
    main()
