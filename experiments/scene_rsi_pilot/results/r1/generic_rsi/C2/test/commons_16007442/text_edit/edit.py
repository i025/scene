import bpy

target_names = [
    "Box", "Box.001", "Box.051", "Box.052", "Box.053", "Box.054", "Box.055",
    "Box.328", "Box.329", "Box.330", "Box.331", "Box.332", "Box.333",
    "Box.334", "Box.335", "Box.336", "Box.337", "Box.338", "Box.339",
    "Rod.012", "Rod.013", "Rod.014", "Rod.125", "Rod.126", "Rod.127",
    "Rod.128", "Rod.129", "Rod.130", "Rod.131", "Rod.132", "Rod.133",
    "Rod.134", "Rod.135", "Rod.136", "Rod.137", "Rod.138", "Rod.139",
    "Rod.140", "Rod.141", "Rod.142", "Rod.143",
]

missing = [
    name for name in target_names
    if bpy.data.objects.get(name) is None
    or bpy.data.objects[name].type != 'MESH'
]
if missing:
    raise RuntimeError("Missing target meshes: " + ", ".join(missing))

targets = {bpy.data.objects[name] for name in target_names}
for group_name in ("bench power supply", "desk clutter", "workbench"):
    group = bpy.data.objects.get(group_name)
    if group is not None:
        targets.update(obj for obj in group.children_recursive if obj.type == 'MESH')

# Include existing descendants of explicitly identified components.
for obj in tuple(targets):
    targets.update(child for child in obj.children_recursive if child.type == 'MESH')

material = bpy.data.materials.new(name="Workbench_Blue")
material.use_nodes = True
material.diffuse_color = (0.02, 0.08, 0.8, 1.0)
material.roughness = 0.45
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
principled.inputs["Roughness"].default_value = 0.45
principled.inputs["Alpha"].default_value = 1.0

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate a shared mesh before adding a material slot.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(material)

    # Object-level overrides preserve materials on other users of shared meshes.
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = material
