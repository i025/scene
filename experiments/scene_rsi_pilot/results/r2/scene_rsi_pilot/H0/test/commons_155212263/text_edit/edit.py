import bpy

rgba = (0.02, 0.08, 0.8, 1.0)
mesh_names = {
    "Box.193", "Box.196", "Box.200",
    "Box.213", "Box.217", "Box.221",
}
group_names = {
    "bench_leg", "bench_scratch", "bench_top_board",
    "distant_wheel_tool_table", "large_flywheel_tool_table",
    "smaller_flywheel_tool_table",
}
tokens = (
    "workbench", "worktable", "bench", "desk",
    "table", "benchtop", "tabletop",
)

objects = tuple(bpy.context.scene.objects)
by_name = {obj.name: obj for obj in objects}

missing = mesh_names.difference(by_name)
if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(sorted(missing)))

roots = {
    obj for obj in objects
    if obj.name in mesh_names
    or obj.name in group_names
    or (
        (obj.type == "MESH" or obj.parent is not None)
        and any(token in obj.name.lower() for token in tokens)
    )
}

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
    if not obj.material_slots:
        # Isolate material-slot changes when the mesh is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object-linked overrides preserve shared mesh materials and polygon indices.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
