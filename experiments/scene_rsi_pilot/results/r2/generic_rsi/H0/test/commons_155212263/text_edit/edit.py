import bpy

scene_objects = list(bpy.context.scene.objects)
required_names = {
    "Box.193", "Box.196", "Box.200",
    "Box.213", "Box.217", "Box.221",
}
group_names = {
    "bench_leg", "bench_scratch", "bench_top_board",
    "distant_wheel_tool_table", "large_flywheel_tool_table",
    "smaller_flywheel_tool_table",
}
tokens = ("workbench", "worktable", "bench", "desk", "table", "benchtop", "tabletop")

by_name = {obj.name: obj for obj in scene_objects}
missing = required_names - by_name.keys()
if missing:
    raise RuntimeError("Missing required targets: " + ", ".join(sorted(missing)))
if any(by_name[name].type != "MESH" for name in required_names):
    raise RuntimeError("A required target is not a mesh")

seeds = set()
for obj in scene_objects:
    matches = any(token in obj.name.casefold() for token in tokens)
    if (
        obj.name in required_names
        or obj.name in group_names
        or (obj.type == "EMPTY" and obj.parent is not None and matches)
        or (obj.type == "MESH" and matches)
    ):
        seeds.add(obj)

targets = set()
pending = list(seeds)
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
    raise RuntimeError("No workbench assembly meshes found")

blue = bpy.data.materials.new(name="Workbench_Blue_RGBA_002_008_080")
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
    if len(obj.material_slots) == 0:
        # Isolate slot creation when mesh data is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(blue)

    # Object overrides preserve shared mesh materials and non-target objects.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = blue
