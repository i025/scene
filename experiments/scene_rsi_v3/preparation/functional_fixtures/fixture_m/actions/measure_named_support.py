"""Engineering fixture action, reusable for two named meshes; not an evolved M action."""

import bpy
from mathutils import Vector


def run(context):
    parameters = context['parameters']
    target = bpy.data.objects[parameters['object_id']]
    support = bpy.data.objects[parameters['support_id']]
    target_points = [target.matrix_world @ Vector(corner) for corner in target.bound_box]
    support_points = [support.matrix_world @ Vector(corner) for corner in support.bound_box]
    low = [min(point[axis] for point in target_points + support_points) for axis in range(3)]
    high = [max(point[axis] for point in target_points + support_points) for axis in range(3)]
    diagonal = (Vector(high) - Vector(low)).length
    gap = min(point.z for point in target_points) - max(point.z for point in support_points)
    overlap = all(min(max(point[axis] for point in target_points), max(point[axis] for point in support_points)) >
                  max(min(point[axis] for point in target_points), min(point[axis] for point in support_points)) for axis in (0, 1))
    normalized_gap = gap / diagonal
    return {'object_id': target.name, 'support_id': support.name,
            'normalized_vertical_gap': normalized_gap,
            'footprint_overlap_approx': overlap,
            'contact_approx_pass': overlap and abs(normalized_gap) <= parameters['tolerance'],
            'target_parent': target.parent.name if target.parent is not None else None,
            'scene_id': context['scene_id'],
            'limitation': 'Parameterized AABB contact approximation; not ground truth mesh support.'}
