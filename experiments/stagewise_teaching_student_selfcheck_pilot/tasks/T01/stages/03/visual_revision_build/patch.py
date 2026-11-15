import bpy
from mathutils import Vector

# Move toward a more frontal view of the back wall and widen the field of view
# so both perimeter cabinet groups fit around the island.
cam = bpy.data.objects.get('SceneActView')
if cam is not None and cam.type == 'CAMERA':
    cam.location = (3.7, -10.0, 4.0)
    target = Vector((0.0, 1.15, 1.35))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 43.0
