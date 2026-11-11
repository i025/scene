"""Publish V3 bundles using existing credentials; no overwrite and no hashes."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import time

import requests

REPOSITORY = 'i025/scene'
BRANCH = 'research/scene-rsi-v3-10rounds'
TAG = 'scene-rsi-v3-10rounds-2026-11-07'


def release_body(receipt):
    state = receipt['source_status']
    rounds = state['round_completed']
    phase = state['phase']
    if phase == 'all_scheduled_terminal' and rounds == 10:
        status = 'completed：state记录十轮终态；逐任务成功、失败与终测覆盖仍以原始表为准'
    elif phase in {'interrupted', 'failed', 'blocked'}:
        status = phase + '：未完成项目原样保留，不将中断计为完成'
    else:
        status = 'incomplete snapshot：快照记录活动阶段，不根据旧state推断当前进程仍在运行'
    base_note=('\n\n本Release仅上传 preparation/final 两个增量包；未变动的baseline及round01–10复用已完成附件：'
               +receipt['base_release_url']+'。先将基础13包解压到新的复核目录，再覆盖解压本次两个更新包；原实验及旧附件不改写。'
               if 'base_release_url' in receipt else '')
    return (f'Scene-RSI V3 实际产物快照，归档状态：{status}。\n\n'
            f'快照 phase={phase}；实际完成研发轮次={rounds}/10；'
            f'H保留版本={state.get("H_retained", state.get("H_start", "unknown"))}；'
            f'M探索版本={state.get("M_retained", state.get("M_start", "unknown"))}。'
            '这不是十个成功升级的声明，也不是基础模型训练。未完成/失败/被拒绝结果完整保留。\n\n'
            '完整脱敏日志、场景工程和真实渲染按 preparation/baseline/roundXX/final 分包。'
            '只公开许可允许的媒体；模型权重、环境、缓存、认证信息、未使用私有测试标签不在附件中。'
            '解压各 tar.gz 至仓库根目录。BW质量是 BW-style / CLI-adapted，不能作为官方榜单分数。\n\n'
            f'分支：{BRANCH}；核心入口 README、experiments/scene_rsi_v3/reports/index.html、'
            '逐场景与逐轮CSV，以及 artifacts_index_v3.csv。'
            '发布不启动模型或Blender，不修改科学结果，不做内容哈希验证。'+base_note)


def auth_session(source):
    if source == 'environment':
        token = os.environ['SCENE_TOKEN']
    else:
        result = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                                capture_output=True, text=True, timeout=20,
                                env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'})
        credentials = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
        if result.returncode or not credentials.get('password'):
            raise RuntimeError('Existing Git authentication unavailable; no credential values were printed or saved')
        token = credentials['password']
    session = requests.Session()
    session.trust_env = False
    session.proxies.update(requests.utils.get_environ_proxies('https://api.github.com'))
    session.headers.update({'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                            'X-GitHub-Api-Version': '2022-11-28'})
    return session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundles', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--index', type=Path, default=Path('artifacts_index_v3.csv'))
    parser.add_argument('--tag', default=TAG)
    parser.add_argument('--auth-source', choices=['git', 'environment'], default='git')
    args = parser.parse_args()
    receipt = json.loads((args.bundles / 'PACK_RECEIPT.json').read_text())
    files = sorted(args.bundles.glob('*.tar.gz'))
    if not files:
        raise ValueError('No completed local bundles to publish')
    if any(path.stat().st_size >= 2_000_000_000 for path in files):
        raise ValueError('Bundle exceeds 2 GB; split before attempting upload')
    session = auth_session(args.auth_source)
    api = 'https://api.github.com/repos/' + REPOSITORY
    response = session.get(api + '/releases/tags/' + args.tag, timeout=30)
    if response.status_code == 404:
        response = session.post(api + '/releases', json={
            'tag_name': args.tag, 'target_commitish': BRANCH, 'name': 'Scene-RSI V3 十轮演化实验实际快照',
            'prerelease': True, 'draft': False, 'body': release_body(receipt)}, timeout=30)
    response.raise_for_status()
    release = response.json()
    state = {'release_url': release['html_url'], 'tag': args.tag, 'assets': [],
             'source_status': receipt['source_status'], 'credentials_saved': False,
             'published_at': time.time(), 'content_hash_verification': False,
             'matching_rule': 'Existing same-name assets reused only when recorded byte size matches; no overwrite'}
    existing = {asset['name']: asset for asset in release.get('assets', [])}
    args.state.parent.mkdir(parents=True, exist_ok=True)
    for path in files:
        reused = path.name in existing
        if reused:
            asset = existing[path.name]
            if asset['size'] != path.stat().st_size:
                raise ValueError('Existing Release asset size differs; use a new snapshot tag, never overwrite: ' + path.name)
        else:
            with path.open('rb') as handle:
                response = session.post(release['upload_url'].split('{', 1)[0], params={'name': path.name}, data=handle,
                                        headers={'Content-Type': 'application/gzip'}, timeout=(20, 600))
            response.raise_for_status()
            asset = response.json()
            if asset['size'] != path.stat().st_size:
                raise ValueError('GitHub reported a different uploaded byte size: ' + path.name)
        state['assets'].append({'name': asset['name'], 'size_bytes': asset['size'],
                                'url': asset['browser_download_url'], 'status': 'uploaded',
                                'reused_existing_same_size': reused})
        args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        with args.index.open(newline='') as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            # A withheld reference never becomes uploaded merely because another
            # permitted artifact shares its planned archive group.
            if row['bundle_name'] == asset['name'] and row['git_status'] != 'withheld_license':
                row.update(download_url=asset['browser_download_url'], upload_status='uploaded', not_uploaded_reason='')
        with args.index.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)
        print(json.dumps(state['assets'][-1]), flush=True)
    response = session.get(api + '/releases/' + str(release['id']) + '/assets', params={'per_page': 100}, timeout=30)
    response.raise_for_status()
    remote = {asset['name']: asset['size'] for asset in response.json()}
    if not all(remote[asset['name']] == asset['size_bytes'] for asset in state['assets']):
        raise ValueError('Remote Release asset listing differs from the saved receipt')
    state['remote_asset_listing_verified'] = True
    args.state.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
