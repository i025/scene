import bpy

# Extend the existing ceiling toward the camera to cover the exposed strip.
ceiling = bpy.data.objects.get('Box.006')
if ceiling:
    ceiling.scale.y *= 1.5
    ceiling.location.y -= 2.0

# Give the floor a distinct, subdued grey finish.
floor = bpy.data.objects.get('Box')
if floor and floor.type == 'MESH':
    mat = bpy.data.materials.new('Floor - warm grey stone')
    mat.diffuse_color = (0.29, 0.31, 0.30, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.29, 0.31, 0.30, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.78
    floor.data.materials.clear()
    floor.data.materials.append(mat)

# Subtle procedural grain keeps the cabinet fronts editable geometry.
wood = bpy.data.materials.new('Cabinet - natural oak grain')
wood.use_nodes = True
nodes = wood.node_tree.nodes
links = wood.node_tree.links
bsdf = nodes.get('Principled BSDF')
bsdf.inputs['Roughness'].default_value = 0.58
tex = nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 4.0
tex.inputs['Detail'].default_value = 3.0
tex.inputs['Roughness'].default_value = 0.7
coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (3.0, 2.0, 45.0)
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.23
ramp.color_ramp.elements[0].color = (0.29, 0.15, 0.075, 1)
ramp.color_ramp.elements[1].position = 0.78
ramp.color_ramp.elements[1].color = (0.63, 0.40, 0.22, 1)
links.new(coord.outputs['Generated'], mapping.inputs[0])
links.new(mapping.outputs[0], tex.inputs['Vector'])
links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
for name in ('Box.051', 'Box.052', 'Box.053', 'Box.054', 'Box.055', 'Box.056', 'Box.057', 'Box.058', 'Box.049'):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        obj.data.materials.clear()
        obj.data.materials.append(wood)

# Reduce the broad fill slightly so upholstery and architectural edges read clearly.
for name, energy in (('SceneActArea', 360.0), ('SceneActArea.001', 300.0), ('SceneActArea.002', 150.0)):
    light = bpy.data.objects.get(name)
    if light and light.type == 'LIGHT':
        light.data.energy = energy
