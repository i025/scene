import bpy

names = ["Workbench details"] + [
    f"Workbench details.{i:03d}" for i in range(1, 115)
]
missing = [name for name in names if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError("Missing target objects: " + ", ".join(missing))

targets = set()
pending = [bpy.data.objects[name] for name in names]
while pending:
    obj = pending.pop()
    if obj in targets:
        continue
    targets.add(obj)
    pending.extend(obj.children)

material = bpy.data.materials.new("Workbench Blue")
material.use_nodes = True
material.diffuse_color = (0.02, 0.08, 0.8, 1.0)
material.roughness = 0.45
bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
bsdf.inputs["Roughness"].default_value = 0.45

for obj in targets:
    if obj.type != "MESH":
        continue

    # Object-linked overrides preserve shared meshes and other objects' materials.
    if not obj.material_slots:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
