import bpy

rgba = (0.02, 0.08, 0.8, 1.0)
target_names = {
    *(f"Box.{i:03d}" for i in range(39, 83)),
    *(f"Box.{i:03d}" for i in range(129, 138)),
    *(f"Box.{i:03d}" for i in range(163, 175)),
    *(f"Rod.{i:03d}" for i in range(191, 216)),
    "Rod.219",
}
group_names = {
    "bench_tools", "far_bench", "foreground_bench",
    "last_bench", "middle_bench", "under_bench_pail",
}

missing = [
    name for name in target_names
    if bpy.data.objects.get(name) is None
    or bpy.data.objects[name].type != 'MESH'
]
if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(sorted(missing)))

targets = {bpy.data.objects[name] for name in target_names}
stack = list(targets)
stack.extend(
    bpy.data.objects[name]
    for name in group_names
    if bpy.data.objects.get(name) is not None
)
visited = set()
while stack:
    obj = stack.pop()
    if obj in visited:
        continue
    visited.add(obj)
    if obj.type == 'MESH':
        targets.add(obj)
    stack.extend(obj.children)

material = bpy.data.materials.new("Workbench_Blue")
material.use_nodes = True
material.diffuse_color = rgba
material.roughness = 0.45
bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = rgba
bsdf.inputs["Roughness"].default_value = 0.45

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate slot creation when mesh data is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object overrides leave existing mesh data and shared materials untouched.
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = material
