import bpy

target_names = [f"Box.{i:03d}" for i in range(123, 165)]
missing = [name for name in target_names if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError("Missing target objects: " + ", ".join(missing))

targets = {bpy.data.objects[name] for name in target_names}
bench = bpy.data.objects.get("bench")
if bench is not None:
    pending = [bench]
    while pending:
        obj = pending.pop()
        pending.extend(obj.children)
        if obj.type == "MESH":
            targets.add(obj)

if any(obj.type != "MESH" for obj in targets):
    raise RuntimeError("A declared target is not a mesh.")

blue = bpy.data.materials.new(name="Workbench_Blue")
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

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(blue)
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = blue
