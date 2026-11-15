import bpy
bpy.data.objects['red_cube_geometry'].location.x += 100
raise RuntimeError('intentional_fixture_failure_after_local_change')
