def frame(camera, nominal_lens):
    camera.data.lens = nominal_lens


def size(group, nominal_scale):
    group.scale = tuple(nominal_scale)


def show(objects, visible):
    for obj in objects:
        obj.hide_render = not bool(visible)


def support(group, nominal_z):
    group.location.z = nominal_z


def local_material(obj, rgba):
    rgba = tuple(rgba)
    originals = [slot.material for slot in obj.material_slots]
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
                        base_color = node.inputs.get('Base Color')
                        if base_color is not None:
                            base_color.default_value = rgba
            copies[key] = material
        slot.material = copies[key]
