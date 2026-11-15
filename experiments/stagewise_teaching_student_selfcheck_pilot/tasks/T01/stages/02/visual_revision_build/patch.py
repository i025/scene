import bpy
from mathutils import Vector

camera = bpy.data.objects.get('SceneActView')
if camera is None or camera.type != 'CAMERA':
    raise RuntimeError('Existing SceneActView camera was not found')
camera.location = (7.0, -6.0, 4.3)
target = Vector((0.0, 0.0, 0.68))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 52.0
bpy.context.scene.camera = camera