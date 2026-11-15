import bpy
from mathutils import Vector

# Move the existing camera inside the room and reframe the back wall.
cam = bpy.data.objects.get('SceneActView')
if cam is None or cam.type != 'CAMERA':
    raise RuntimeError('Existing SceneActView camera not found')
cam.location = (-0.30, -3.90, 2.15)
target = Vector((0.0, 4.0, 2.15))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 22.5
bpy.context.scene.camera = cam