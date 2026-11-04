import bpy

target_names = {
    "Ball.035", "Ball.036", "Ball.037", "Ball.038", "Ball.039",
    "Box.002", "Box.003", "Box.176", "Box.177", "Box.178",
    "Box.179", "Box.180", "Box.303", "Box.304", "Box.305",
    "Rod.013", "Rod.014", "Rod.015", "Rod.065", "Rod.066",
    "Rod.067", "Rod.068", "Rod.069", "Rod.070", "Rod.071",
}
group_names = {"desk_lamp", "small_bench_supply", "workbench"}

missing = [
    name for name in sorted(target_names)
    if bpy.data.objects.get(name) is None
    or bpy.data.objects[name].type != "MESH"
]
if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(missing))

targets = {bpy.data.objects[name] for name in target_names}
for name in group_names:
    group = bpy.data.objects.get(name)
    if group is not None:
        targets.update(
            obj for obj in group.children_recursive if obj.type == "MESH"
        )

material = bpy.data.materials.new("Workbench_Blue")
material.use_nodes = True
material.diffuse_color = (0.02, 0.08, 0.8, 1.0)
material.roughness = 0.45

nodes = material.node_tree.nodes
nodes.clear()
shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
shader.inputs["Roughness"].default_value = 0.45
shader.inputs["Alpha"].default_value = 1.0
output = nodes.new("ShaderNodeOutputMaterial")
material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate material-slot changes from any shared non-target mesh.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
