"""Shared fixture transformation helpers."""

def frame(camera, nominal_lens):
    camera.data.lens = nominal_lens


def size(group, nominal_scale):
    group.scale = tuple(nominal_scale)


def show(objects, visible):
    for obj in objects:
        obj.hide_render = not visible


def support(object, contact_z):
    object.location.z = contact_z


def local_material(object, rgba):
    # Isolate slot assignments when geometry data is shared.
    if object.data.users > 1:
        object.data = object.data.copy()

    # Read the effective slot material, including object-level overrides.
    slot = object.material_slots[0]
    material = slot.material.copy()
    slot.material = material
    material.diffuse_color = tuple(rgba)

    if material.use_nodes and material.node_tree is not None:
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Base Color'].default_value = tuple(rgba)
