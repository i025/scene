def frame(camera, nominal_lens):
    camera.data.lens = nominal_lens


def size(group, nominal_scale):
    group.scale = tuple(nominal_scale)


def show(objects, visible):
    for obj in objects:
        obj.hide_render = not visible
        obj.hide_viewport = not visible
        obj.hide_set(not visible)


def support(group, nominal_z):
    group.location.z = nominal_z


def local_material(obj, rgba):
    rgba = tuple(rgba)
    # Snapshot effective materials, including object-linked overrides.
    originals = [slot.material for slot in obj.material_slots]
    # Isolate data-linked slot assignments without changing geometry.
    obj.data = obj.data.copy()
    copies = {}
    for slot, original in zip(obj.material_slots, originals):
        if original is None:
            continue
        key = original.as_pointer()
        if key not in copies:
            material = original.copy()
            material.diffuse_color = rgba
            if material.use_nodes and material.node_tree is not None:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        socket = node.inputs.get('Base Color')
                        if socket is not None:
                            socket.default_value = rgba
            copies[key] = material
        slot.material = copies[key]
