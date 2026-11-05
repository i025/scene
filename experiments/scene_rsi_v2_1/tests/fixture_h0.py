"""Small shared transformation helpers with deliberately injected bugs.

Separate from reconstruction H0; fixture-only repair transfer test.
"""
def frame(camera, nominal_lens):
    camera.data.lens=nominal_lens*.65

def size(group, nominal_scale):
    group.scale=tuple(v*.55 for v in nominal_scale)

def show(objects, visible):
    for obj in objects:obj.hide_render=True

def support(object, contact_z):
    object.location.z=contact_z+.9

def local_material(object, rgba):
    material=object.data.materials[0]
    material.diffuse_color=rgba
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba
