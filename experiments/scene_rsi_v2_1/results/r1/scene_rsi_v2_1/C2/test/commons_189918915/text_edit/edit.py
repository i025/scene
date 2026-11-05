import bpy

target_names = [f"Box.{i:03d}" for i in range(844, 854)]
group = bpy.data.objects.get("Left pallet load 00")
if group is None or group.type != 'EMPTY':
    raise RuntimeError("Required target group 'Left pallet load 00' is missing.")

targets = {}
stack = list(group.children)
while stack:
    obj = stack.pop()
    stack.extend(obj.children)
    if obj.type == 'MESH':
        targets[obj.name] = obj

for name in target_names:
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != 'MESH' or name not in targets:
        raise RuntimeError(f"Required target mesh is missing or outside its group: {name}")

blue = bpy.data.materials.new(name="Left pallet load 00 Blue")
blue.use_nodes = True
blue.diffuse_color = (0.02, 0.08, 0.8, 1.0)
blue.roughness = 0.45

nodes = blue.node_tree.nodes
nodes.clear()
shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
shader.inputs["Roughness"].default_value = 0.45
shader.inputs["Alpha"].default_value = 1.0
output = nodes.new("ShaderNodeOutputMaterial")
blue.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])

for obj in targets.values():
    if not obj.material_slots:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(blue)
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = blue
