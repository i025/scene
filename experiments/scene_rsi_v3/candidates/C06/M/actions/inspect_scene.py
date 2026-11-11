"""Reusable object, hierarchy, material and camera facts, without cause attribution."""
def run(context):
    import bpy
    return {'objects': [{'object_id': obj.name, 'type': obj.type,
                         'parent': obj.parent.name if obj.parent else None,
                         'location': list(obj.matrix_world.translation),
                         'dimensions': list(obj.dimensions),
                         'materials': [slot.material.name if slot.material else None for slot in obj.material_slots]}
                        for obj in bpy.context.scene.objects],
            'camera': bpy.context.scene.camera.name if bpy.context.scene.camera else None,
            'mapping': 'unknown until reference/render evidence is associated by M'}
