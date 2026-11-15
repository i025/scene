import bpy
from math import radians
from mathutils import Matrix, Vector

# Give the existing monitor housing its own contrasting finish.
housing = bpy.data.objects.get('silver monitor back')
bezel = bpy.data.objects.get('monitor lower bezel')
mat = bpy.data.materials.get('Monitor back - contrasting silver')
if mat is None:
    mat = bpy.data.materials.new('Monitor back - contrasting silver')
    mat.diffuse_color = (0.31, 0.32, 0.33, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    if shader:
        shader.inputs['Base Color'].default_value = (0.31, 0.32, 0.33, 1.0)
        shader.inputs['Metallic'].default_value = 0.25
        shader.inputs['Roughness'].default_value = 0.48

def descendants(root):
    for child in root.children:
        yield child
        yield from descendants(child)

if housing:
    for obj in descendants(housing):
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mat)

# Turn and gently tilt the panel as a unit, keeping its support on the desk.
pivot = Vector((1.48, 2.22, 1.06))
transform = (Matrix.Translation(pivot) @ Matrix.Rotation(radians(-8), 4, 'Z') @ Matrix.Rotation(radians(-7), 4, 'X') @ Matrix.Translation(-pivot))
for panel in (housing, bezel):
    if panel:
        panel.matrix_world = transform @ panel.matrix_world
