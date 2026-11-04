import bpy

target_names = [
    "Box", "Box.001", "Box.155", "Box.156", "Box.157",
    "Rod.001", "Rod.002", "Rod.003", "Rod.004", "Rod.005",
]
group_names = ["brown workbench", "left bench power supply"]

scene_objects = {obj.name: obj for obj in bpy.context.scene.objects}
missing = [
    name for name in target_names + group_names
    if name not in scene_objects
]
if missing:
    raise RuntimeError("Missing required targets: " + ", ".join(missing))

targets = set()
for name in target_names:
    obj = scene_objects[name]
    if obj.type != 'MESH':
        raise RuntimeError("Required target is not a mesh: " + name)
    targets.add(obj)

# Include components belonging to the existing assembly hierarchies.
pending = [scene_objects[name] for name in group_names + target_names]
visited = set()
while pending:
    obj = pending.pop()
    if obj in visited:
        continue
    visited.add(obj)
    if obj.type == 'MESH':
        targets.add(obj)
    pending.extend(obj.children)

blue = bpy.data.materials.new(name="Workbench_Blue")
blue.use_nodes = True
blue.diffuse_color = (0.02, 0.08, 0.8, 1.0)
blue.roughness = 0.45

nodes = blue.node_tree.nodes
nodes.clear()
shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.inputs["Base Color"].default_value = (0.02, 0.08, 0.8, 1.0)
shader.inputs["Roughness"].default_value = 0.45
output = nodes.new("ShaderNodeOutputMaterial")
blue.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])

for obj in sorted(targets, key=lambda item: item.name):
    if not obj.material_slots:
        # Isolate an empty slot list when the mesh is shared.
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.materials.append(blue)

    # Object-level overrides leave shared mesh materials and other objects intact.
    for slot in obj.material_slots:
        slot.link = 'OBJECT'
        slot.material = blue
