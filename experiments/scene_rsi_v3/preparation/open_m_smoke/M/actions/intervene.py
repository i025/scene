"""Camera/object sensitivity and shared-material checks. Explicit object selection."""
def run(context):
    import bpy
    from mathutils import Vector
    p = context['parameters']
    scene = bpy.context.scene
    operation = p['operation']
    if operation == 'camera_focal':
        before = scene.camera.data.lens
        scene.camera.data.lens *= p['factor']
        return {'operation': operation, 'before': before, 'after': scene.camera.data.lens,
                'interpretation': 'Sensitivity intervention, not unique causal identification'}
    obj = bpy.data.objects[p['object_id']]
    if operation == 'object_scale':
        before = list(obj.scale)
        obj.scale *= p['factor']
        return {'object_id': obj.name, 'before': before, 'after': list(obj.scale)}
    if operation == 'isolate':
        names = {obj.name} | {o.name for o in obj.children_recursive}
        for other in scene.objects:
            if other.type == 'MESH': other.hide_render = other.name not in names
        return {'object_id': obj.name, 'visible_meshes': sorted(names)}
    if operation == 'depth':
        before = list(obj.matrix_world.translation)
        ray = obj.matrix_world.translation - scene.camera.matrix_world.translation
        obj.location += ray * p['fraction']
        return {'object_id': obj.name, 'before': before, 'after': list(obj.matrix_world.translation)}
    if operation == 'material_dependencies':
        materials = {s.material.name for s in obj.material_slots if s.material}
        return {'object_id': obj.name, 'shared_with': [o.name for o in scene.objects if o != obj
                and any(s.material and s.material.name in materials for s in o.material_slots)]}
    raise ValueError('Unsupported initial operation; design an additional reusable action if needed')
