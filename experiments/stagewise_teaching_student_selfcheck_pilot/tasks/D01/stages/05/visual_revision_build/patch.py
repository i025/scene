import bpy

# Tighten the view and move it toward the left foreground wall.
cam = bpy.data.objects.get('SceneActView')
if cam and cam.type == 'CAMERA':
    cam.location.x = -0.85
    cam.location.y = -4.35
    cam.data.lens = 26.0

# Extend the existing ceiling laterally and toward the camera to cover the frame.
ceiling = bpy.data.objects.get('Box.006')
if ceiling:
    ceiling.scale.x *= 1.35
    ceiling.scale.y *= 1.25

def set_surface(name, color, roughness=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        return
    mat.diffuse_color = (*color, 1.0)
    if mat.use_nodes:
        shader = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if shader:
            shader.inputs['Base Color'].default_value = (*color, 1.0)
            if roughness is not None:
                shader.inputs['Roughness'].default_value = roughness

set_surface('Floor - warm grey stone', (0.30, 0.32, 0.31), 0.82)
set_surface('SceneActSurface_2', (0.55, 0.45, 0.39), 0.9)

# Give the right visitor chair its own darker olive upholstery.
chair = bpy.data.objects.get('visitor chair right')
if chair:
    copies = {}
    stack = list(chair.children)
    while stack:
        obj = stack.pop()
        stack.extend(obj.children)
        if obj.type != 'MESH':
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.name in ('SceneActSurface_3.001', 'SceneActSurface_4.001'):
                if mat.name not in copies:
                    new = mat.copy()
                    new.name = 'Right visitor chair olive ' + mat.name
                    new.diffuse_color = (0.24, 0.28, 0.025, 1.0)
                    if new.use_nodes:
                        shader = next((n for n in new.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                        if shader:
                            shader.inputs['Base Color'].default_value = (0.24, 0.28, 0.025, 1.0)
                            shader.inputs['Roughness'].default_value = 0.88
                    copies[mat.name] = new
                slot.material = copies[mat.name]

# Retain left-side daylight while moderating broad fill.
for name, factor in [('SceneActArea', 0.78), ('SceneActArea.001', 0.88)]:
    light = bpy.data.objects.get(name)
    if light and light.type == 'LIGHT':
        light.data.energy *= factor
