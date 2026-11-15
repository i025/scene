import bpy
from mathutils import Matrix

# Shorten each upholstered back from below while retaining its top height.
for name in ('upholstered back', 'upholstered back.001'):
    obj = bpy.data.objects.get(name)
    if obj:
        top = 1.38
        obj.matrix_world = Matrix.Translation((0, 0, top)) @ Matrix.Diagonal((1, 1, 0.76, 1)) @ Matrix.Translation((0, 0, -top)) @ obj.matrix_world

# Raise the seats and arms to expose more of each pedestal.
for name in ('seat cushion', 'arm left', 'arm right', 'seat cushion.001', 'arm left.001', 'arm right.001'):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.matrix_world = Matrix.Translation((0, 0, 0.20)) @ obj.matrix_world

# Extend each stem upward from its existing foot; leave the cross bases on the floor.
for name in ('central stem', 'central stem.001'):
    obj = bpy.data.objects.get(name)
    if obj:
        bottom = 0.12
        obj.matrix_world = Matrix.Translation((0, 0, bottom)) @ Matrix.Diagonal((1, 1, 1.59, 1)) @ Matrix.Translation((0, 0, -bottom)) @ obj.matrix_world
