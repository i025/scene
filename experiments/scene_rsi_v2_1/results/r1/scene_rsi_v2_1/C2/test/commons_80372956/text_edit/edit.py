import bpy

RGBA = (0.02, 0.08, 0.8, 1.0)
ROUGHNESS = 0.45
required_names = {"Ball.005", "Rod.082", "Rod.083"}

group = bpy.data.objects.get("arm_00")
if group is None or group.type != "EMPTY":
    raise RuntimeError("Required target group 'arm_00' is missing.")

targets = []
pending = list(group.children)
while pending:
    obj = pending.pop()
    pending.extend(obj.children)
    if obj.type == "MESH":
        targets.append(obj)

if not required_names.issubset({obj.name for obj in targets}):
    raise RuntimeError("Required target meshes are missing from 'arm_00'.")

material_copies = {}

def blue_material(source):
    key = source.as_pointer() if source else None
    if key in material_copies:
        return material_copies[key]

    mat = source.copy() if source else bpy.data.materials.new("arm_00_Blue")
    mat.name = (source.name + "_arm_00_Blue") if source else "arm_00_Blue"
    mat.diffuse_color = RGBA
    mat.roughness = ROUGHNESS
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shaders = [node for node in nodes if node.type == "BSDF_PRINCIPLED"]

    if not shaders:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        output = next(
            (node for node in nodes
             if node.type == "OUTPUT_MATERIAL" and node.is_active_output),
            None,
        )
        if output is None:
            output = nodes.new("ShaderNodeOutputMaterial")
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
        shaders = [shader]

    for shader in shaders:
        for name, value in (
            ("Base Color", RGBA),
            ("Roughness", ROUGHNESS),
            ("Alpha", 1.0),
        ):
            socket = shader.inputs.get(name)
            if socket is not None:
                for link in list(socket.links):
                    links.remove(link)
                socket.default_value = value

    material_copies[key] = mat
    return mat

for obj in targets:
    if len(obj.material_slots) == 0:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(blue_material(None))
    else:
        for slot in obj.material_slots:
            replacement = blue_material(slot.material)
            slot.link = "OBJECT"
            slot.material = replacement
