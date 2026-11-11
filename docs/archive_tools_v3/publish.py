"""V3 publishing only; existing Git authentication is the default.

--auth bashrc is an explicit user-authorized child-only bridge. Credentials are
neither returned to this process nor printed or saved. No global Git change.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
BRANCH = 'research/scene-rsi-v3-10rounds'
TAG = 'scene-rsi-v3-10rounds-2026-11-07'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'push', 'release', 'verify'])
    parser.add_argument('--repo', type=Path, default=ROOT / 'archive' / 'scene')
    parser.add_argument('--auth', choices=['git', 'bashrc'], default='git')
    parser.add_argument('--tag', default=TAG)
    parser.add_argument('--bundles', type=Path, default=WORK / 'bundles')
    parser.add_argument('--state', default='docs/V3_RELEASE_UPLOAD_STATE.json')
    parser.add_argument('--index', default='artifacts_index_v3.csv')
    parser.add_argument('--commit')
    args = parser.parse_args()
    remote = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=args.repo, text=True).strip()
    if remote not in {'https://github.com/i025/scene.git', 'git@github.com:i025/scene.git'}:
        raise ValueError('Archive origin differs from the requested repository; it has not been changed')
    if args.action == 'push':
        branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=args.repo, text=True).strip()
        if branch != BRANCH:
            raise ValueError('Refuse to push from a different checked-out branch: ' + branch)
    environment = os.environ.copy()
    for key in ['GIT_CURL_VERBOSE', 'GIT_TRACE', 'GIT_TRACE_CURL', 'BASH_ENV', 'ENV']:
        environment.pop(key, None)
    environment.update(GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    git = ['git', '-c', 'http.version=HTTP/1.1']
    if args.auth == 'bashrc':
        # Override helpers only in this optional child, not in local/global config.
        git += ['-c', 'credential.helper=']
    if args.action == 'status':
        command = git + ['ls-remote', '--heads', 'origin', BRANCH]
    elif args.action == 'push':
        command = git + ['push', '-u', 'origin', BRANCH]
    elif args.action == 'verify':
        if args.commit is None:
            raise ValueError('Verification requires an explicit pushed commit')
        command = [sys.executable, str(WORK / 'verify_remote.py'), '--commit', args.commit,
                   '--repo', str(args.repo.resolve()), '--release-state', args.state,
                   '--auth-source', 'environment' if args.auth == 'bashrc' else 'git']
    else:
        command = [sys.executable, str(WORK / 'github_release_v3.py'), '--bundles', str(args.bundles.resolve()),
                   '--state', args.state, '--index', args.index, '--tag', args.tag,
                   '--auth-source', 'environment' if args.auth == 'bashrc' else 'git']
    if args.auth == 'bashrc':
        askpass = ROOT / 'work' / 'scene_v2_1_archive' / 'github_askpass.py'
        if not askpass.is_file():
            raise FileNotFoundError('Existing credential prompt bridge is missing')
        shell = ('set +x +v; source /home/xymo/.bashrc >/dev/null 2>&1; set +x +v; '
                 'unset GIT_CURL_VERBOSE GIT_TRACE GIT_TRACE_CURL; '
                 'test -n "$GITHUB_NAME" && test -n "$SCENE_TOKEN" || exit 78; '
                 'export GITHUB_NAME SCENE_TOKEN; export GIT_ASKPASS="$1"; shift; exec "$@"')
        command = ['bash', '--noprofile', '--norc', '-i', '-c', shell,
                   'scene-v3-auth', str(askpass), *command]
    # In Git mode the user configured helper remains in charge. This program
    # never reads the shell file, credential values, or a Codex auth file.
    result = subprocess.run(command, cwd=args.repo, env=environment, text=True,
                            timeout=7200 if args.action == 'release' else 1800)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
