import bpy
for name in ['Ball.003', 'Ball.004', 'Ball.005', 'Ball.006', 'Ball.007', 'Ball.008', 'Ball.009', 'Rod.040', 'Rod.041', 'Rod.042', 'Rod.043', 'Rod.044', 'Rod.045']:
    obj=bpy.data.objects[name]
    obj.data=obj.data.copy()
    mat=bpy.data.materials.new('checker_blue_'+name)
    mat.use_nodes=True
    mat.diffuse_color=(.02,.08,.8,1)
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.02,.08,.8,1)
    shader.inputs['Roughness'].default_value=.45
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:face.material_index=0
