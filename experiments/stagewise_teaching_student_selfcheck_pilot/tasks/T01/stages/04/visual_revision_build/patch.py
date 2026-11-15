import bpy
from mathutils import Vector

# Tighten the existing view around the furniture and look down enough to reveal
# more of the cabinet fronts behind the work island.
cam = bpy.data.objects.get('SceneActView')
if cam is not None and cam.type == 'CAMERA':
    cam.location = (4.8, -7.8, 4.2)
    target = Vector((0.0, 1.25, 1.35))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 46.0
    cam.data.shift_x = 0.0
    cam.data.shift_y = 0.0
    bpy.context.scene.camera = cam
