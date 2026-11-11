import bpy


def edit():
    target_ids = (
        'Box.216', 'Box.217', 'Box.218',
        'Box.219', 'Box.220', 'Box.221',
    )
    blue = (0.02, 0.08, 0.8, 1.0)

    material = bpy.data.materials.new(name='DeskTechnicalBlue')
    material.diffuse_color = blue
    material.roughness = 0.45
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = blue
    principled.inputs['Roughness'].default_value = 0.45
    material.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    for object_id in target_ids:
        obj = bpy.data.objects[object_id]
        obj.data = obj.data.copy()
        if len(obj.material_slots) == 0:
            obj.data.materials.append(material)
        else:
            for slot in obj.material_slots:
                slot.material = material
