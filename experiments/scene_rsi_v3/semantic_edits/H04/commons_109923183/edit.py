import bpy


def edit():
    names = ['Ball']
    names += ['Ball.%03d' % i for i in range(1, 125)]
    names += ['Box.%03d' % i for i in range(30, 49)]
    names += ['Rod.%03d' % i for i in range(2, 143)]

    blue = (0.02, 0.08, 0.8, 1.0)
    material = bpy.data.materials.new(name='Chaise Technical Blue')
    material.diffuse_color = blue
    material.roughness = 0.45
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value = blue
    shader.inputs['Roughness'].default_value = 0.45
    material.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])

    for name in names:
        obj = bpy.data.objects[name]
        obj.data = obj.data.copy()
        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            for index in range(len(obj.data.materials)):
                obj.data.materials[index] = material
        for slot in obj.material_slots:
            if slot.link == 'OBJECT':
                slot.material = material
