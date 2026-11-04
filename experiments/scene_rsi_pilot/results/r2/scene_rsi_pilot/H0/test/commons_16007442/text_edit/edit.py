import bpy

names = ["Workbench details"] + [
    f"Workbench details.{i:03d}" for i in range(1, 115)
]
targets = set()
missing = []

for name in names:
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != 'MESH':
        missing.append(name)
    else:
        targets.add(obj)
        targets.update(child for child in obj.children_recursive
                       if child.type == 'MESH')

if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(missing))

material = bpy.data.materials.new("Workbench Blue")
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

for obj in targets:
    if not obj.material_slots:
        # Isolate slot creation when the mesh has other users.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object overrides preserve shared mesh materials and polygon assignments.
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = material
