import bpy

rgba = (0.02, 0.08, 0.8, 1.0)
names = (
    [f"Box.{i:03d}" for i in range(82, 104)]
    + ["Box.167", "Box.170"]
    + [f"Box.{i:03d}" for i in range(181, 186)]
    + ["Rod"]
    + [f"Rod.{i:03d}" for i in range(1, 6)]
    + [f"Rod.{i:03d}" for i in range(462, 479)]
)
group_names = ("loose_bench_tools", "table", "table.001", "workbench")
scene_objects = list(bpy.context.scene.objects)
by_name = {obj.name: obj for obj in scene_objects}

missing = [name for name in names if name not in by_name]
if missing:
    raise RuntimeError("Missing target objects: " + ", ".join(missing))

targets = set()
pending = [by_name[name] for name in names]
pending.extend(by_name[name] for name in group_names if name in by_name)
visited = set()

while pending:
    obj = pending.pop()
    if obj in visited:
        continue
    visited.add(obj)
    if obj.type == "MESH":
        targets.add(obj)
    pending.extend(obj.children)

if not targets:
    raise RuntimeError("No workbench target meshes found.")

material = bpy.data.materials.new("Workbench_Blue")
material.use_nodes = True
material.diffuse_color = rgba
material.roughness = 0.45
nodes = material.node_tree.nodes
nodes.clear()
shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.inputs["Base Color"].default_value = rgba
shader.inputs["Roughness"].default_value = 0.45
shader.inputs["Alpha"].default_value = 1.0
output = nodes.new("ShaderNodeOutputMaterial")
material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])

for obj in sorted(targets, key=lambda item: item.name):
    if len(obj.material_slots) == 0:
        # Isolate material-slot changes from any other users of this mesh.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object overrides preserve shared mesh materials and all non-target users.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
