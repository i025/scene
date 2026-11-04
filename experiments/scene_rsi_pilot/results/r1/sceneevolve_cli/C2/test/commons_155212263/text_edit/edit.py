import bpy

target_names = (
    [f"Box.{i:03d}" for i in range(208, 258)]
    + [f"Box.{i:03d}" for i in range(281, 285)]
    + ["Rod.101", "Rod.102"]
)

missing = [
    name for name in target_names
    if bpy.data.objects.get(name) is None
    or bpy.data.objects[name].type != "MESH"
]
if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(missing))

targets = {bpy.data.objects[name] for name in target_names}

# Include components belonging to the declared assemblies.
for group_name in ("bench", "Distant bench vise"):
    group = bpy.data.objects.get(group_name)
    if group is not None:
        targets.update(
            obj for obj in group.children_recursive if obj.type == "MESH"
        )

rgba = (0.02, 0.08, 0.8, 1.0)
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
        # Isolate an empty slot table if the mesh is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object-level overrides leave shared meshes and original materials intact.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
