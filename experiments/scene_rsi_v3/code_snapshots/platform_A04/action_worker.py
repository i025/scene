"""Execute one M action in a disposable scene process; never resave source .blend."""
import argparse, json, runpy, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--blend');p.add_argument('--action');p.add_argument('--context');p.add_argument('--output');p.add_argument('--render-settings');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
import bpy
bpy.ops.wm.open_mainfile(filepath=args.blend)
context=json.loads(Path(args.context).read_text())
sys.path[:0]=[str(Path(args.action).parent.parent),str(Path(__file__).parent),str(Path(args.action).parent)]
result=runpy.run_path(args.action)['run'](context)
Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False))
if args.render_settings:
    sys.path.insert(0,str(Path(__file__).parent/'backend'))
    from render import render_scene
    render_scene(Path(args.output).parent,json.loads(Path(args.render_settings).read_text()))
