"""Create two explicit preparation fixture copies, never modify original files."""
import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def box(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--variant', choices=['near_black', 'scale_error'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.output.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()))
    part, support = bpy.data.objects['Z_target_part'], bpy.data.objects['Support']
    bpy.context.view_layer.update()
    before = box(part)
    if args.variant == 'scale_error':
        part.scale *= 2.2
        bpy.context.view_layer.update()
        matrix = part.matrix_world.copy()
        matrix.translation.z += box(support)['max'][2] - box(part)['min'][2]
        part.matrix_world = matrix
        bpy.context.view_layer.update()
        change = 'Z_target_part uniformly scaled 2.2x; lower face kept on support to separate scale from floating'
    else:
        for light in bpy.data.lights:
            light.energy = 0
        world = bpy.context.scene.world
        world.color = (0, 0, 0)
        if world.use_nodes:
            for node in world.node_tree.nodes:
                if node.type == 'BACKGROUND':
                    node.inputs['Strength'].default_value = 0
        change = 'All light energies and world background strengths set to zero; geometry/materials retained'
    bpy.ops.wm.save_as_mainfile(filepath=str((args.output / 'scene.blend').resolve()))
    (args.output / 'variant_build.json').write_text(json.dumps({
        'creator': 'engineering_calibration_not_M', 'variant': args.variant,
        'source': str(args.source), 'target': part.name, 'before_target_aabb': before,
        'after_target_aabb': box(part), 'controlled_change': change,
        'truth_visibility': 'Evaluation-side fixture record; never injected as judge fault identity'}, indent=2) + '\n')


if __name__ == '__main__':
    main()
