#!/usr/bin/env python3
"""Git's credential prompt bridge; values exist only in the caller's environment."""
import os
import sys

prompt = sys.argv[1]
if prompt.startswith('Username'):
    print(os.environ['GITHUB_NAME'])
elif prompt.startswith('Password'):
    print(os.environ['SCENE_TOKEN'])
else:
    raise SystemExit(1)
