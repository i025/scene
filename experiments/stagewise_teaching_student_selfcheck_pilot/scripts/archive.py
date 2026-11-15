"""Archive this two-scene pilot using the existing public-release transport."""
import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

WORK = Path(__file__).resolve().parent
PROJECT = WORK.parents[1]
NAME = 'stagewise_teaching_student_selfcheck_pilot'
SOURCE = PROJECT / 'outputs' / NAME
REPO = PROJECT / 'archive/scene'
REL = Path('experiments') / NAME
BRANCH = 'research/stagewise-teaching-student-selfcheck-pilot'
TAG = 'stagewise-teaching-student-selfcheck-pilot-2026-11-15'
BUNDLE = NAME + '_full.tar.gz'
INDEX = REPO / 'artifacts_index_stagewise.csv'
TERMINAL = {'completed', 'failed', 'timeout', 'invalid', 'budget_exhausted',
            'interrupted', 'blocked', 'partial'}
sys.path.insert(0, str(PROJECT / 'work/scene_v3_archive'))
from prepare_archive import public_text, SECRET, CREDENTIAL_FILES, SKIP_DIRS
from github_release_v3 import auth_session


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prepare():
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=REPO, text=True).strip()
    if branch != BRANCH:
        raise ValueError('Wrong checkout branch: ' + branch)
    bundle = WORK / BUNDLE
    if bundle.exists():
        raise FileExistsError('Preserve the completed package; use an explicit new archive directory')
    # Keep the same lock as the finite runner until its complete snapshot is packed.
    with (SOURCE / 'experiment.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads((SOURCE / 'state.json').read_text())
        if state['status'] not in TERMINAL:
            raise ValueError('Experiment has no terminal snapshot: ' + state['status'])
        _prepare_locked(bundle, state)


def _prepare_locked(bundle, state):
    target = WORK / 'public_package' / NAME
    target.mkdir(parents=True, exist_ok=True)
    core = REPO / REL
    core.mkdir(parents=True, exist_ok=True)
    replacements = [(str(PROJECT), '${PROJECT_ROOT}'),
                    ('${USER_STORAGE}', '${USER_STORAGE}'),
                    ('${USER_HOME}', '${USER_HOME}')]
    rows, redactions, excluded = [], [], []
    for path in sorted(SOURCE.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(SOURCE)
        if path.is_symlink() or any(part in SKIP_DIRS for part in rel.parts):
            excluded.append({'path': str(rel), 'reason': 'symlink or environment/cache directory'})
            continue
        if path.name in CREDENTIAL_FILES:
            excluded.append({'path': str(rel), 'reason': 'credential file; never publish'})
            continue
        if (rel.parts[0] == 'session_staging' or path.suffix in {'.pyc', '.blend1', '.tmp'}
                or path.name == 'experiment.lock'):
            continue
        data = path.read_bytes()
        changes = []
        if path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.blend', '.webp', '.mp4'}:
            if SECRET.search(data):
                raise ValueError('Sensitive credential pattern: ' + str(rel))
            data, changes = public_text(data, replacements)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        if changes:
            redactions.append({'path': str(rel), 'fields': changes})
        in_git = (path.suffix not in {'.blend', '.log', '.jsonl', '.time'}
                  and len(data) < 8_000_000)
        if in_git:
            out = core / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
        rows.append({'run_id': NAME, 'artifact_type': path.suffix[1:] or 'text',
                     'relative_path': str(rel), 'size_bytes': len(data),
                     'git_status': 'included' if in_git else 'release_only',
                     'bundle_name': BUNDLE, 'download_url': '', 'upload_status': 'local',
                     'not_uploaded_reason': ''})
    note = {'originals_retained': True, 'credential_values_present': False,
            'changes': redactions, 'excluded': excluded,
            'source_media': 'Two Commons originals retained under their individual attribution and licenses; no blanket relicensing',
            'source_status': state['status'],
            'session_staging': 'Duplicate temporary attachments excluded; original image audit references and their source/render files retained'}
    write(core / 'PUBLIC_REDACTIONS.json', note)
    shutil.copy2(core / 'PUBLIC_REDACTIONS.json', target / 'PUBLIC_REDACTIONS.json')

    def public_owner(info):
        info.uid = info.gid = 0
        info.uname = info.gname = ''
        return info

    with tarfile.open(bundle, 'w:gz', compresslevel=3) as archive:
        archive.add(target, arcname=target.name, filter=public_owner)
    with INDEX.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    receipt = {'path': str(bundle), 'bytes': bundle.stat().st_size,
               'file_count': len(rows), 'time': time.time(), 'source_status': state['status'],
               'contains_all_existing_attempts': True, 'source_media_count': 2,
               'excluded': excluded, 'originals_retained': True}
    write(WORK / 'PACK_RECEIPT.json', receipt)
    print(json.dumps(receipt), flush=True)


def publish():
    session = auth_session('environment')
    api = 'https://api.github.com/repos/i025/scene'
    response = session.get(api + '/releases/tags/' + TAG, timeout=30)
    if response.status_code == 404:
        body = ('两个来源、两个持续场景任务：D01阶段式教师纠错，提炼冻结通用检查策略，'
                'T01由同一学生模型自主检查，测试不调用教师。实际完成与失败见逐步表；'
                '没有自动质量评分、A/B胜负、权重训练或教师自进化结论。'
                '完整离线包包含两张许可允许再分发的历史参考原图、所有已有检查点、增量补丁、'
                '渲染、反馈、冻结策略和脱敏调用日志。解压后打开 '
                + NAME + '/reports/index.html。来源归属见 SOURCE_ATTRIBUTION.md 和 manifest.json。')
        response = session.post(api + '/releases', json={
            'tag_name': TAG, 'target_commitish': BRANCH,
            'name': '阶段式教师纠错与学生自主检查：单图开发、单图测试',
            'draft': False, 'prerelease': True, 'body': body}, timeout=30)
    response.raise_for_status()
    release = response.json()
    path = WORK / BUNDLE
    same = [item for item in release['assets'] if item['name'] == path.name]
    if same:
        asset = same[0]
    else:
        with path.open('rb') as stream:
            response = session.post(release['upload_url'].split('{')[0],
                                    params={'name': path.name}, data=stream,
                                    headers={'Content-Type': 'application/gzip'}, timeout=(30, 600))
        response.raise_for_status()
        asset = response.json()
    if asset['state'] != 'uploaded' or asset['size'] != path.stat().st_size:
        raise ValueError('Existing asset incomplete or size differs; not overwritten')
    response = session.get(api + '/releases/' + str(release['id']) + '/assets', timeout=30)
    response.raise_for_status()
    live = next(item for item in response.json() if item['name'] == path.name)
    if live['state'] != 'uploaded' or live['size'] != path.stat().st_size:
        raise ValueError('Remote asset not confirmed')
    import requests
    head = requests.head(asset['browser_download_url'], allow_redirects=True, timeout=60)
    head.raise_for_status()
    receipt = {'release_url': release['html_url'], 'asset_url': asset['browser_download_url'],
               'name': path.name, 'bytes': asset['size'], 'state': asset['state'],
               'public_head_status': head.status_code, 'credential_values_saved': False,
               'time': time.time()}
    write(REPO / 'docs/STAGEWISE_RELEASE.json', receipt)
    write(WORK / 'UPLOAD_RECEIPT.json', receipt)
    with INDEX.open() as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        row.update(download_url=asset['browser_download_url'], upload_status='uploaded')
    with INDEX.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)


def authenticated(action):
    # Reuse the existing child-only Git credential bridge; never save or print secrets.
    askpass = PROJECT / 'work/scene_v2_1_archive/github_askpass.py'
    command = (['git', '-c', 'http.version=HTTP/1.1', '-c', 'credential.helper=',
                'push', '-u', 'origin', BRANCH] if action == 'push' else
               [sys.executable, str(Path(__file__).resolve()), 'release-child'])
    shell = ('set +x +v; source ${USER_HOME}/.bashrc >/dev/null 2>&1; set +x +v; '
             'unset GIT_CURL_VERBOSE GIT_TRACE GIT_TRACE_CURL; '
             'test -n "$GITHUB_NAME" && test -n "$SCENE_TOKEN" || exit 78; '
             'export GITHUB_NAME SCENE_TOKEN; export GIT_ASKPASS="$1"; shift; exec "$@"')
    environment = os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    for key in ['GIT_TRACE', 'GIT_CURL_VERBOSE', 'GIT_TRACE_CURL']:
        environment.pop(key, None)
    subprocess.run(['bash', '--noprofile', '--norc', '-i', '-c', shell,
                    'stagewise-archive-auth', str(askpass), *command],
                   env=environment, cwd=REPO, check=True, timeout=1800)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'push', 'release', 'release-child'])
    action = parser.parse_args().action
    if action == 'prepare':
        prepare()
    elif action == 'release-child':
        publish()
    else:
        authenticated(action)
