"""V2.4 fixed first transfer pair; adapted from the V2.1 read-only archive check. No save, rendering, generation or scoring."""
import argparse
import json
from pathlib import Path
import sys
import bpy

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--original-root', type=Path, required=True)
parser.add_argument('--public-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
scenes = [
    'results/task01/reference/H_start/test/commons_192968130/scene.blend',
    'results/task01/active/C1/test/commons_192968130/scene.blend',
]


def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    return {
        'objects': sorted((obj.name, obj.type, obj.parent.name if obj.parent else None,
            [float(value) for row in obj.matrix_world for value in row],
            len(obj.data.vertices) if obj.type == 'MESH' else None,
            len(obj.data.polygons) if obj.type == 'MESH' else None) for obj in bpy.data.objects),
        'materials': sorted((mat.name, list(mat.diffuse_color), mat.roughness,
                             len(mat.node_tree.nodes) if mat.node_tree else 0) for mat in bpy.data.materials),
        'camera': [(obj.name, obj.data.lens) for obj in bpy.data.objects if obj.type == 'CAMERA'],
    }


results = []
for relative in scenes:
    original = inspect(args.original_root / relative)
    public = inspect(args.public_root / relative)
    results.append({'relative_path': relative, 'both_opened': True,
                    'recorded_structure_material_camera_unchanged': original == public,
                    'objects': len(public['objects']), 'materials': len(public['materials'])})
record = {'purpose': 'Archive file compatibility after equal-length account-path redaction; not a new experimental result.',
          'new_model_calls': 0, 'new_render_frames': 0, 'read_only_file_opens': 2 * len(scenes), 'results': results}
args.output.write_text(json.dumps(record, indent=2) + '\n')
assert all(row['recorded_structure_material_camera_unchanged'] for row in results)
