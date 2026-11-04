import bpy

names = ["Workbench details"] + [
    f"Workbench details.{i:03d}" for i in range(1, 115)
]

missing = [name for name in names if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError("Missing target objects: " + ", ".join(missing))

targets = set()
for name in names:
    obj = bpy.data.objects[name]
    targets.add(obj)
    targets.update(obj.children_recursive)

meshes = [obj for obj in targets if obj.type == "MESH"]
if not meshes:
    raise RuntimeError("No target meshes found.")

material = bpy.data.materials.new("Workbench Blue")
material.use_nodes = True
material.diffuse_color = (0.02, 0.08, 0.8, 1.0)
material.roughness = 0.45

bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
bsdf.inputs["Roughness"].default_value = 0.45
bsdf.inputs["Alpha"].default_value = 1.0

for obj in meshes:
    if not obj.material_slots:
        # Isolate an empty material table before modifying shared mesh data.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object-level overrides leave shared meshes and original materials intact.
    for slot in obj.material_slots:
        slot.link = "OBJECT"
        slot.material = material
