"""Publish archive bundles with existing Git credentials; never persist credentials."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import requests

REPO = 'i025/scene'
TAG = 'scene-rsi-pilot-2026-11-04'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundles', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    args = parser.parse_args()
    result = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                            capture_output=True, text=True, timeout=20,
                            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'})
    credentials = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    if result.returncode or not credentials.get('password'):
        raise RuntimeError('Existing Git credential helper did not provide a credential; values are not printed.')
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + credentials['password'],
                            'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    api = 'https://api.github.com/repos/' + REPO
    response = session.get(api + '/releases/tags/' + TAG, timeout=30)
    if response.status_code == 404:
        response = session.post(api + '/releases', json={
            'tag_name': TAG, 'target_commitish': 'main', 'name': 'Scene-RSI 首轮探索性实验归档',
            'prerelease': True, 'draft': False,
            'body': '已有实验的完整脱敏证据，按运行分包；包含失败、拒绝和未选中候选。'
                    '不含模型权重、环境、缓存或未使用的预留数据。归档没有新增模型调用或渲染。'
                    '\n解压全部 tar.gz 到仓库根目录。见 main 分支 README、docs/AS_RUN_PROTOCOL.md、'
                    'docs/REVIEW_INDEX.md 和 artifacts_index.csv。无内容哈希验证。'}, timeout=30)
    response.raise_for_status()
    release = response.json()
    state = {'release_url': release['html_url'], 'tag': TAG, 'assets': [], 'credentials_saved': False}
    existing = {asset['name']: asset for asset in release.get('assets', [])}
    args.state.parent.mkdir(parents=True, exist_ok=True)
    for path in sorted(args.bundles.glob('*.tar.gz')):
        if path.name in existing:
            asset = existing[path.name]
            if asset['size'] != path.stat().st_size:
                raise ValueError('Existing asset size differs; no overwrite: ' + path.name)
        else:
            with path.open('rb') as handle:
                uploaded = session.post(release['upload_url'].split('{', 1)[0], params={'name': path.name},
                                        data=handle, headers={'Content-Type': 'application/gzip'}, timeout=(20, 600))
            uploaded.raise_for_status()
            asset = uploaded.json()
        state['assets'].append({'name': asset['name'], 'size_bytes': asset['size'],
                                'url': asset['browser_download_url'], 'status': 'uploaded'})
        args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(state['assets'][-1]), flush=True)
    checked = session.get(api + '/releases/' + str(release['id']) + '/assets', timeout=30)
    checked.raise_for_status()
    remote = {asset['name']: asset['size'] for asset in checked.json()}
    assert all(remote[row['name']] == row['size_bytes'] for row in state['assets'])
    state['remote_asset_listing_verified'] = True
    args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
