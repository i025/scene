"""Fixed, small regression menu. Unknown ground truth stays unknown."""
import json

MENU = ['hierarchy_parts', 'known_support', 'mesh_intersection', 'material_preservation', 'composite_move', 'camera_framing']


def gate(required, applicable, measured_pass):
    return dict(required=required, applicable=applicable, measured_pass=measured_pass,
                gate_pass=(applicable and measured_pass is True) if required else True)


def geometric_checks():
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import inspect_blend as ib
    missing = []; detached = []; contracts = 0
    for obj in bpy.context.scene.objects:
        if 'scene_rsi_expected_children' not in obj:continue
        contracts += 1
        for name in json.loads(obj['scene_rsi_expected_children']):
            child = bpy.data.objects.get(name)
            if child is None:missing.append(dict(parent=obj.name, child=name))
            elif child.parent != obj:detached.append(dict(parent=obj.name, child=name))
    hierarchy = dict(applicable=contracts > 0, measured_pass=not (missing or detached) if contracts else None,
                     declared_groups=contracts, missing=missing, detached=detached,
                     meaning='Integrity of emitted part declarations; not completeness against reference image')
    supports = json.loads(bpy.context.scene.get('scene_rsi_supports', '[]'))
    support_rows = []
    boxes = {o.name: ib.world_bounds(o) for o in bpy.context.scene.objects if o.type == 'MESH'}
    diag = (ib.scene_bounds() or {}).get('diagonal_scene_units', 1)
    for pair in supports:
        a, b = boxes.get(pair['object']), boxes.get(pair['support'])
        if a is None or b is None:
            support_rows.append(dict(pair=pair, measured_pass=False, reason='Declared object missing'));continue
        gap = (a['min'][2] - b['max'][2]) / max(diag, 1e-9)
        overlap = all(min(a['max'][i], b['max'][i]) > max(a['min'][i], b['min'][i]) for i in (0, 1))
        support_rows.append(dict(pair=pair, normalized_vertical_gap=gap, footprint_overlap_approx=overlap,
                                 measured_pass=overlap and abs(gap) <= 0.01))
    # Broad phase only bounds; positive reports below are actual triangle-surface crossings.
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH' and ib.mesh_valid(o)]
    tested = 0; crossings = []; deps = bpy.context.evaluated_depsgraph_get(); trees = {}
    subset = meshes[:64]
    for index, a in enumerate(subset):
        for b in subset[index + 1:]:
            ba, bb = boxes[a.name], boxes[b.name]
            if not all(min(ba['max'][i], bb['max'][i]) - max(ba['min'][i], bb['min'][i]) > 1e-5 * max(diag, 1e-9) for i in range(3)):continue
            for obj in [a, b]:
                if obj.name not in trees:
                    mesh = obj.evaluated_get(deps).to_mesh()
                    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
                    polygons = [list(p.vertices) for p in mesh.polygons]
                    trees[obj.name] = BVHTree.FromPolygons(vertices, polygons)
                    obj.evaluated_get(deps).to_mesh_clear()
            tested += 1
            hits = trees[a.name].overlap(trees[b.name])
            if hits:crossings.append(dict(objects=[a.name, b.name], triangle_pairs=len(hits)))
    return {'hierarchy_parts': hierarchy,
            'known_support': dict(applicable=bool(supports), measured_pass=all(r['measured_pass'] for r in support_rows) if supports else None, rows=support_rows,
                                  meaning='Declared support; normalized AABB contact approximation, not true mesh support'),
            'mesh_intersection': dict(applicable=len(meshes) >= 2, measured_pass=not crossings if len(meshes) <= 64 and len(meshes) >= 2 else None,
                                      crossings=crossings, narrow_phase_pairs=tested, mesh_count=len(meshes), tested_mesh_count=len(subset),
                                      meaning='Triangle surface crossings; intended joints may also intersect. No containment test or semantic collision truth; supplemental, not hard gate')}


def execute_test(name):
    import bpy
    import inspect_blend as ib
    from mathutils import Vector
    if name in ['hierarchy_parts', 'known_support', 'mesh_intersection']:
        return geometric_checks()[name]
    target = ib.choose_target()
    if name == 'camera_framing':
        camera = bpy.context.scene.camera
        return dict(applicable=camera is not None, measured_pass=camera is not None and camera.data.lens > 0,
                    meaning='Camera validity only; no reference framing ground truth')
    if name == 'material_preservation':
        names = target['mesh_names']
        if not names:return dict(applicable=False, measured_pass=None)
        before = ib.snapshot_objects();ib.set_blue(names);after = ib.snapshot_objects()
        preserve = ib.unchanged(before, after, set(names))
        passed = ib.blue_success(names) and preserve['pass'] and all(before[n]['vertices'] == after[n]['vertices'] and before[n]['matrix_world'] == after[n]['matrix_world'] for n in names)
        return dict(applicable=True, measured_pass=passed, non_target=preserve, target=names, type='mechanical_not_text')
    if name == 'composite_move':
        group_name = target['group_name']
        if group_name is None:return dict(applicable=False, measured_pass=None)
        group = bpy.data.objects[group_name];before = ib.snapshot_objects();rel = ib.relative_matrices(group)
        matrix = group.matrix_world.copy();matrix.translation += Vector((0.1, 0, 0));group.matrix_world=matrix
        bpy.context.view_layer.update()
        error = ib.max_matrix_delta(rel, ib.relative_matrices(group))
        preserve = ib.unchanged(before, ib.snapshot_objects(), {group.name} | {o.name for o in ib.descendants(group)})
        integrity = geometric_checks()['hierarchy_parts']
        passed = error <= 1e-5 and preserve['pass'] and integrity['measured_pass'] is not False
        return dict(applicable=True, measured_pass=passed, relative_matrix_error=error, non_target=preserve, declared_integrity=integrity, type='mechanical_not_text')
    raise ValueError('Unknown regression test: ' + name)
