import bpy

scene = bpy.context.scene
target = scene.objects.get("Box.362")
group = scene.objects.get("paper on desk")

if target is None or target.type != "MESH":
    raise RuntimeError("Required target mesh 'Box.362' is missing.")

targets = set()
stack = [target]
if group is not None:
    stack.append(group)

visited = set()
while stack:
    obj = stack.pop()
    if obj in visited:
        continue
    visited.add(obj)
    if obj.type == "MESH":
        targets.add(obj)
    stack.extend(obj.children)

material = bpy.data.materials.new("Workbench_Blue_Surface")
material.use_nodes = True
material.diffuse_color = (0.02, 0.08, 0.8, 1.0)
material.roughness = 0.45

nodes = material.node_tree.nodes
nodes.clear()
shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
shader.inputs["Roughness"].default_value = 0.45
output = nodes.new("ShaderNodeOutputMaterial")
material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate slot creation when the mesh is shared with other objects.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object overrides leave shared meshes and original materials untouched.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
