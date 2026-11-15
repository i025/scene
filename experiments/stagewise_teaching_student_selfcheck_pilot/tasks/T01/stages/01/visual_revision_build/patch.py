import bpy
import random

# Extend the existing back wall beyond the camera's field of view.
wall = bpy.data.objects.get('Box.042')
if wall:
    wall.dimensions.x = 30.0
    wall.dimensions.z = 12.0
    wall.location.z = 6.0

# Give the existing plank materials a warm, subtly varied wood appearance.
for i in range(5):
    mat = bpy.data.materials.get('SceneActSurface_' + str(i))
    if not mat:
        continue
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    if not bsdf:
        continue
    for link in list(bsdf.inputs['Base Color'].links):
        links.remove(link)
    geometry = nodes.new('ShaderNodeNewGeometry')
    geometry.label = 'World position for wood grain'
    stretch = nodes.new('ShaderNodeVectorMath')
    stretch.operation = 'MULTIPLY'
    stretch.inputs[1].default_value = (10.0, 0.65, 3.0)
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.68
    ramp = nodes.new('ShaderNodeValToRGB')
    shade = (i - 2) * 0.012
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.19 + shade, 0.075 + shade * 0.5, 0.027 + shade * 0.2, 1)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.48 + shade, 0.255 + shade, 0.105 + shade * 0.5, 1)
    links.new(geometry.outputs['Position'], stretch.inputs[0])
    links.new(stretch.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.62

# Short cross-grain joints mark staggered board ends without changing coverage.
seam_mat = bpy.data.materials.get('Floor board end joints')
if seam_mat is None:
    seam_mat = bpy.data.materials.new('Floor board end joints')
    seam_mat.diffuse_color = (0.16, 0.085, 0.043, 1.0)
    seam_mat.use_nodes = True
    seam_bsdf = seam_mat.node_tree.nodes.get('Principled BSDF')
    seam_bsdf.inputs['Base Color'].default_value = (0.16, 0.085, 0.043, 1.0)
    seam_bsdf.inputs['Roughness'].default_value = 0.8
random.seed(19)
verts = []
faces = []
for i in range(42):
    x = -5.04 + i * 0.24
    offset = random.uniform(-1.0, 1.0)
    for j in range(-3, 4):
        y = j * 1.65 + offset
        if not -4.98 < y < 4.98:
            continue
        n = len(verts)
        verts.extend([(x-0.116,y-0.003,0.001), (x+0.116,y-0.003,0.001), (x+0.116,y+0.003,0.001), (x-0.116,y+0.003,0.001)])
        faces.append((n,n+1,n+2,n+3))
mesh = bpy.data.meshes.new('Staggered floor joint mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
joints = bpy.data.objects.new('Staggered floor board joints', mesh)
bpy.context.collection.objects.link(joints)
joints.data.materials.append(seam_mat)
joints.parent = bpy.data.objects.get('Room.001')
