import bpy

rgba = (0.02, 0.08, 0.8, 1.0)
roughness = 0.45
mesh_names = {
    "Box.193", "Box.196", "Box.200",
    "Box.213", "Box.217", "Box.221",
}
group_names = {
    "bench_leg", "bench_scratch", "bench_top_board",
    "distant_wheel_tool_table",
    "large_flywheel_tool_table",
    "smaller_flywheel_tool_table",
}
tokens = ("workbench", "worktable", "bench", "desk", "table",
          "benchtop", "tabletop")

objects = list(bpy.context.scene.objects)
by_name = {obj.name: obj for obj in objects}

missing = sorted(mesh_names - by_name.keys())
if missing:
    raise RuntimeError("Missing required target meshes: " + ", ".join(missing))

roots = set()
for obj in objects:
    named_match = any(token in obj.name.lower() for token in tokens)
    if (
        obj.name in mesh_names
        or obj.name in group_names
        or (named_match and (
            obj.type == "MESH"
            or (obj.type == "EMPTY" and obj.parent is not None)
        ))
    ):
        roots.add(obj)

targets = set()
pending = list(roots)
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
    raise RuntimeError("No workbench assembly meshes found.")

material = bpy.data.materials.new("Workbench_Blue")
material.use_nodes = True
material.diffuse_color = rgba
material.roughness = roughness
bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = rgba
bsdf.inputs["Roughness"].default_value = roughness
bsdf.inputs["Alpha"].default_value = rgba[3]

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate slot creation when the mesh datablock is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object-level overrides leave shared mesh material assignments untouched.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
