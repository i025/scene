"""Observation only: stage events survive a killed Blender subprocess."""
import json
import os
import time
from pathlib import Path


def event(stage, **values):
    target = os.environ.get('SCENE_RSI_TELEMETRY')
    if target:
        with Path(target).open('a') as stream:
            stream.write(json.dumps({'stage': stage, 'time': time.time(), **values}) + '\n')
