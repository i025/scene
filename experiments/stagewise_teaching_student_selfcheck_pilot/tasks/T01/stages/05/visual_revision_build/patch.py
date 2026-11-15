import bpy

# Extend the existing back wall horizontally to cover the remaining left-edge void.
wall = bpy.data.objects.get('Box.042')
if wall is None:
    raise RuntimeError('Existing back wall mesh Box.042 was not found')
wall.scale.x *= 2.0
