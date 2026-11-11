import bpy


def edit():
    target_ids = (
        'Ball', 'Ball.001', 'Ball.002', 'Ball.003', 'Ball.004',
        'Ball.005', 'Ball.006', 'Ball.007', 'Ball.008',
        'Box.028', 'Box.029', 'Box.030',
        'Rod.006', 'Rod.007', 'Rod.008', 'Rod.009', 'Rod.010',
        'Rod.011', 'Rod.012', 'Rod.013', 'Rod.014', 'Rod.015',
        'Rod.016', 'Rod.017',
    )
    blue = (0.02, 0.08, 0.8, 1.0)
    material = bpy.data.materials.new(name='Chaise Technical Blue')
    material.diffuse_color = blue
    material.roughness = 0.45
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = blue
    shader.inputs['Roughness'].default_value = 0.45
    output = nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])

    for object_id in target_ids:
        obj = bpy.data.objects[object_id]
        obj.data = obj.data.copy()
        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            for index in range(len(obj.data.materials)):
                obj.data.materials[index] = material
        for slot in obj.material_slots:
            if slot.link == 'OBJECT':
                slot.material = material
