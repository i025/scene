"""Read-only projected bounds for explicitly selected objects and mesh descendants."""
def run(context):
    import bpy
    import math
    scene = bpy.context.scene
    camera = scene.camera
    if camera is None:
        return {'status': 'unavailable', 'reason': 'No active camera'}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    render = scene.render
    projection = camera.calc_matrix_camera(
        depsgraph, x=render.resolution_x, y=render.resolution_y,
        scale_x=render.pixel_aspect_x, scale_y=render.pixel_aspect_y)
    view = camera.matrix_world.inverted()
    rows = []
    for name in context['parameters']['object_ids']:
        root = scene.objects.get(name)
        if root is None:
            rows.append({'object_id': name, 'status': 'missing'})
            continue
        meshes = [o for o in [root] + list(root.children_recursive) if o.type == 'MESH']
        points = []
        behind = 0
        hidden = []
        for obj in meshes:
            if obj.hide_render:
                hidden.append(obj.name)
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                transform = projection @ view @ evaluated.matrix_world
                for vertex in mesh.vertices:
                    clip = transform @ vertex.co.to_4d()
                    if clip.w <= 1e-8:
                        behind += 1
                        continue
                    x = .5 * (clip.x / clip.w + 1)
                    y = .5 * (1 - clip.y / clip.w)
                    if math.isfinite(x) and math.isfinite(y):
                        points.append((float(x), float(y)))
            finally:
                evaluated.to_mesh_clear()
        row = {'object_id': name, 'mesh_count': len(meshes),
               'hidden_meshes': hidden, 'projected_vertex_count': len(points),
               'vertices_at_or_behind_camera': behind}
        if points:
            xs, ys = zip(*points)
            left, top, right, bottom = min(xs), min(ys), max(xs), max(ys)
            area = (right-left)*(bottom-top)
            intersection = max(0., min(1.,right)-max(0.,left)) * max(0., min(1.,bottom)-max(0.,top))
            row.update({'bounds_normalized': [left,top,right,bottom],
                        'bbox_area': area,
                        'bbox_in_frame_fraction': intersection/area if area > 0 else None})
        else:
            row['bounds_normalized'] = None
        rows.append(row)
    return {'status': 'ok', 'coordinate_convention': 'x right, y down; image bounds 0 to 1',
            'camera': {'name': camera.name, 'type': camera.data.type,
                       'lens': float(camera.data.lens)},
            'objects': rows,
            'limitations': 'Unoccluded projected vertex bounds, not visible silhouette or pixel coverage. Bounds crossing the camera plane are incomplete. Collection visibility and reference correspondence are not inferred.'}
