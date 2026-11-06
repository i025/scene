def frame(camera, nominal_lens):
    camera.data.lens=nominal_lens

def size(group, nominal_scale):
    group.scale=tuple(nominal_scale)

def show(objects, visible):
    for obj in objects:obj.hide_render=not visible

def support(group, nominal_z):
    group.location.z=nominal_z

def local_material(obj, rgba):
    obj.data=obj.data
    for i,original in enumerate(list(obj.data.materials)):
        material=original
        obj.data.materials[i]=material
        material.diffuse_color=rgba
        material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba
