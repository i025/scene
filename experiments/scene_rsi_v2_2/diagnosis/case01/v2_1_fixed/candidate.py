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
    # Isolate data-linked slots without changing geometry or parenting.
    obj.data = obj.data.copy()
    # Object-linked slots must also receive private materials.
    for slot in obj.material_slots:
        original = slot.material
        if original is None:
            continue
        material = original.copy()
        slot.material = material
        material.diffuse_color = rgba
        if material.use_nodes and material.node_tree is not None:
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Base Color'].default_value = rgba
