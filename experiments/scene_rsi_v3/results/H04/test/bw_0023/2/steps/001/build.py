# Reference inventory and visual anchors (normalized image coordinates, estimates):
# The requested reconstruction is the interior visible on the phone, presented without
# the phone or hand. Its perspective looks along the hall toward a bright distant arcade.
# - Repeated warm stone pointed vaults: upper half, converging toward the distant center.
# - Clustered columns and pointed side arcades: left and right, partially occluded.
# - Staircase and dark-red ornate railing: foreground lower third, descending diagonally.
# - Brass chandelier and warm bulbs: left of center, suspended above the stair.
# - Large iridescent sphere: foreground right, overlapping the arcade and stair.
# - Small matte magenta sphere: behind it, near the center.
# Dominant edges: ribs rise to pointed crowns; stair and railing descend toward image right;
# arcade lines converge toward the bright far end. Hidden architecture is uncertain.
#
# Approximate geometry budget: floor and walls 5, vault ribs ~105, columns ~72,
# arcades ~70, stair and railing ~80, chandelier ~20, spheres 2: about 354 primitives.
# Each rod, box or ball is one SceneAct primitive. Curves use short rod segments.
#
# Reference landmark estimates below are illustrative scene correspondences, not
# calibration: far arch crown (0.50, 0.32), near left column capital (0.24, 0.46),
# foreground railing endpoint (0.20, 0.80). Projection output is a numerical check,
# not proof of visibility or visual agreement.

from sceneact import *
import bpy
import math
from mathutils import Vector

# Major dimensions and independently editable camera parameters.
HALL_HALF_WIDTH = 3.5
HALL_HEIGHT = 7.2
BAY_SPACING = 3.0
BAY_YS = [-2.0, 1.0, 4.0, 7.0, 10.0, 13.0]
CAMERA_POSITION = (0.1, -9.3, 4.2)
CAMERA_TARGET = (0.0, 5.2, 3.75)
CAMERA_LENS = 29

stone = (0.68, 0.62, 0.51)
light_stone = (0.79, 0.74, 0.65)
shadow_stone = (0.43, 0.39, 0.33)
floor_color = (0.64, 0.59, 0.51)
red = (0.22, 0.028, 0.022)
gold = (0.57, 0.35, 0.10)
dark = (0.105, 0.085, 0.07)
magenta = (0.75, 0.005, 0.40)

scene = Scene("Heritage cathedral hall")

architecture = Asset("Vaults and architecture")
architecture.include("floor", box((7.0, 21.0, 0.18), center=(0, 3.5, -0.09), color=floor_color))
architecture.include("left_outer_wall", box((0.25, 21.0, 7.4), center=(-4.25, 3.5, 3.7), color=stone))
architecture.include("right_outer_wall", box((0.25, 21.0, 7.4), center=(4.25, 3.5, 3.7), color=stone))
architecture.include("ceiling", box((8.5, 21.0, 0.20), center=(0, 3.5, 7.45), color=light_stone))
# Bright end wall is pale, with inset window panels to suggest daylight.
architecture.include("far_wall", box((8.5, 0.20, 7.4), center=(0, 14.0, 3.7), color=light_stone))

def add_rod(parent, name, a, b, radius, color):
    if sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-8:
        parent.include(name, rod(radius, start=a, end=b, color=color))

def add_path(parent, prefix, points, radius, color):
    for i in range(len(points) - 1):
        add_rod(parent, "%s_%02d" % (prefix, i), points[i], points[i + 1], radius, color)

# Transverse pointed arches: the separate ribs retain visible structural hierarchy.
for j, y in enumerate(BAY_YS):
    rib = Asset("Vault bay %02d" % j)
    profile = [
        (-HALL_HALF_WIDTH, y, 3.7),
        (-3.30, y, 4.65),
        (-2.75, y, 5.55),
        (-1.70, y, 6.48),
        (0.0, y, HALL_HEIGHT),
        (1.70, y, 6.48),
        (2.75, y, 5.55),
        (3.30, y, 4.65),
        (HALL_HALF_WIDTH, y, 3.7),
    ]
    add_path(rib, "transverse_rib", profile, 0.075, shadow_stone)
    # Thinner adjacent molding reinforces the deep, layered rib profile.
    profile2 = [(x * 0.97, yy + 0.07, z - 0.08) for x, yy, z in profile]
    add_path(rib, "rib_molding", profile2, 0.035, light_stone)
    architecture.include("vault_bay_%02d" % j, rib)

# Ridge and diagonal ribs suggest cross vaulting between successive transverse arches.
add_rod(architecture, "central_ridge", (0, -2, 7.2), (0, 13, 7.2), 0.055, shadow_stone)
for j in range(len(BAY_YS) - 1):
    y0, y1 = BAY_YS[j], BAY_YS[j + 1]
    ym = (y0 + y1) / 2
    for side in (-1, 1):
        for end, yy in enumerate((y0, y1)):
            add_path(
                architecture, "diagonal_%d_%d_%d" % (j, side, end),
                [(side * 3.5, yy, 3.9),
                 (side * 2.65, (yy + ym) / 2, 5.35),
                 (side * 1.35, ym, 6.45),
                 (0, ym, 7.16)],
                0.047, stone
            )
scene.include("Vaults", architecture)

columns = Asset("Clustered columns and side arcades")
for j, y in enumerate(BAY_YS):
    for side in (-1, 1):
        x = side * 3.5
        col = Asset("Column %s %d" % (side, j))
        col.include("main_shaft", rod(0.19, start=(x, y, 0.14), end=(x, y, 3.68), color=light_stone))
        for k, (dx, dy) in enumerate(((-0.17, 0), (0.17, 0), (0, -0.16), (0, 0.16))):
            col.include("cluster_shaft_%d" % k,
                        rod(0.065, start=(x + dx, y + dy, 0.16),
                            end=(x + dx, y + dy, 3.62), color=stone))
        col.include("base", box((0.61, 0.61, 0.20), center=(x, y, 0.12), color=stone))
        col.include("capital", box((0.67, 0.67, 0.22), center=(x, y, 3.69), color=light_stone))
        columns.include("column_%s_%d" % (side, j), col)

# Pointed arches running along the side walls.
for side in (-1, 1):
    for j in range(len(BAY_YS) - 1):
        y0, y1 = BAY_YS[j], BAY_YS[j + 1]
        ym = (y0 + y1) / 2
        x = side * 3.53
        path = [(x, y0, 3.65), (x, y0 + 0.25, 4.25),
                (x, y0 + 0.75, 4.75), (x, ym, 5.18),
                (x, y1 - 0.75, 4.75), (x, y1 - 0.25, 4.25),
                (x, y1, 3.65)]
        add_path(columns, "side_arch_%s_%d" % (side, j), path, 0.065, shadow_stone)
scene.include("Columns", columns)

# A staircase in the foreground descends from the left-rear landing toward the
# right foreground. The railing is open so the marble steps remain visible.
stairs = Asset("Staircase and railing")
stairs.include("upper_landing", box((3.4, 2.0, 0.20), center=(-1.35, -1.2, 0.65), color=light_stone))
steps = 9
for i in range(steps):
    x = -1.30 + i * 0.38
    z = 0.64 - i * 0.13
    stairs.include("marble_tread_%02d" % i,
                   box((0.40, 1.45, 0.13), center=(x, -2.15, z), color=light_stone))
    stairs.include("tread_nosing_%02d" % i,
                   box((0.045, 1.47, 0.035), center=(x + 0.19, -2.15, z + 0.055), color=stone))
# Front railing slopes with the stairs. Posts and two slim rails preserve open gaps.
rail_y = -2.91
x0, x1 = -1.48, 2.12
z0, z1 = 1.72, 0.48
add_rod(stairs, "golden_handrail", (x0, rail_y, z0), (x1, rail_y, z1), 0.055, gold)
add_rod(stairs, "red_lower_rail", (x0, rail_y, z0 - 0.70), (x1, rail_y, z1 - 0.70), 0.045, red)
add_rod(stairs, "middle_rail", (x0, rail_y, z0 - 0.37), (x1, rail_y, z1 - 0.37), 0.026, gold)
for i in range(13):
    t = i / 12
    x = x0 + (x1 - x0) * t
    z = z0 + (z1 - z0) * t
    add_rod(stairs, "baluster_%02d" % i, (x, rail_y, z - 0.70), (x, rail_y, z), 0.026, red)
    if i < 12:
        xa = x + 0.05
        xb = x + (x1 - x0) / 12 - 0.05
        add_rod(stairs, "diagonal_ornament_%02d" % i,
                (xa, rail_y, z - 0.62), (xb, rail_y, z - 0.18), 0.018, red)
scene.include("Staircase & railing", stairs)

# Chandelier: restrained radial arms and bulbs.
chandelier = Asset("Brass chandelier")
cx, cy, cz = -1.15, 2.1, 3.25
add_rod(chandelier, "suspension_chain", (cx, cy, 6.8), (cx, cy, cz + 0.45), 0.025, dark)
chandelier.include("central_body", ball(0.15, center=(cx, cy, cz), color=gold))
for i in range(6):
    a = 2 * math.pi * i / 6
    end = (cx + 0.62 * math.cos(a), cy + 0.62 * math.sin(a), cz + 0.08)
    add_rod(chandelier, "arm_%02d" % i, (cx, cy, cz), end, 0.035, gold)
    chandelier.include("bulb_%02d" % i, ball(0.085, center=(end[0], end[1], end[2] + 0.10), color=(1.0, 0.82, 0.45)))
scene.include("Chandelier", chandelier)

spheres = Asset("AR spheres")
spheres.include("large_iridescent_bubble", ball(1.15, center=(1.62, 1.15, 2.80), color=(0.55, 0.36, 0.75)))
spheres.include("small_magenta_sphere", ball(0.38, center=(-0.38, 3.45, 2.72), color=magenta))
scene.include("Spheres", spheres)

realize(scene)

# Use the requested aspect in both the projection check and final scene.
sc = bpy.context.scene
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
world_nodes = sc.world.node_tree.nodes
background = world_nodes.get("Background")
if background is None:
    background = world_nodes.new("ShaderNodeBackground")
output = world_nodes.get("World Output")
if output is None:
    output = world_nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.66, 0.70, 0.73, 1)
background.inputs["Strength"].default_value = 0.45

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-1.0, 1.8, 4.2), power=950, size=2.0, target=(0, 1, 2), color=(1.0, 0.75, 0.49))
area_emitter((0, 12.8, 5.6), power=2200, size=4.5, target=(0, 2, 3), color=(1.0, 0.91, 0.78))
area_emitter((0, -5, 6.5), power=1000, size=6, target=(0, 2, 2.5), color=(1.0, 0.87, 0.72))

# Organize realized meshes in named Blender collections, preserving SceneAct objects.
collection_names = ["Vaults", "Columns", "Staircase & railing", "Chandelier", "Spheres"]
collections = {}
for name in collection_names:
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        sc.collection.children.link(coll)
    collections[name] = coll

# Resolve semantic names through object ancestors because SceneAct may create marker parents.
for obj in list(sc.objects):
    if obj.type != "MESH":
        continue
    chain = []
    node = obj
    while node:
        chain.append(node.name.lower())
        node = node.parent
    label = " ".join(chain)
    dest = None
    if any(s in label for s in ("bubble", "magenta_sphere", "ar spheres")):
        dest = "Spheres"
    elif any(s in label for s in ("chandelier", "bulb_", "suspension_chain")):
        dest = "Chandelier"
    elif any(s in label for s in ("staircase", "tread", "baluster", "rail", "ornament", "landing")):
        dest = "Staircase & railing"
    elif any(s in label for s in ("column", "side_arch", "shaft", "capital")):
        dest = "Columns"
    elif any(s in label for s in ("vault", "rib", "architecture", "wall", "floor", "ceiling", "ridge", "diagonal")):
        dest = "Vaults"
    if dest:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        collections[dest].objects.link(obj)

# Shared stone material with restrained procedural weathering.
stone_mat = bpy.data.materials.new("Warm aged sandstone")
stone_mat.diffuse_color = (0.70, 0.64, 0.54, 1)
stone_mat.use_nodes = True
nodes = stone_mat.node_tree.nodes
links = stone_mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.70, 0.64, 0.54, 1)
bsdf.inputs["Roughness"].default_value = 0.76
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 7.5
noise.inputs["Detail"].default_value = 3.0
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.13
bump.inputs["Distance"].default_value = 0.035
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# Soap-film appearance from a view-angle color ramp, with transmission.
bubble_mat = bpy.data.materials.new("Iridescent soap film")
bubble_mat.use_nodes = True
nodes = bubble_mat.node_tree.nodes
links = bubble_mat.node_tree.links
p = nodes.get("Principled BSDF")
p.inputs["Roughness"].default_value = 0.08
p.inputs["Metallic"].default_value = 0.18
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value = 0.42
elif "Transmission" in p.inputs:
    p.inputs["Transmission"].default_value = 0.42
p.inputs["IOR"].default_value = 1.33
facing = nodes.new("ShaderNodeLayerWeight")
facing.inputs["Blend"].default_value = 0.35
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for idx, (position, color) in enumerate([
    (0.00, (0.90, 0.24, 0.60, 1)),
    (0.18, (0.98, 0.55, 0.10, 1)),
    (0.35, (0.20, 0.85, 0.80, 1)),
    (0.53, (0.25, 0.26, 0.88, 1)),
    (0.70, (0.86, 0.26, 0.70, 1)),
    (1.00, (0.75, 0.90, 0.94, 1))
]):
    e = ramp.color_ramp.elements[0] if idx == 0 else ramp.color_ramp.elements.new(position)
    e.position = position
    e.color = color
links.new(facing.outputs["Facing"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], p.inputs["Base Color"])

bulb_mat = bpy.data.materials.new("Warm luminous glass")
bulb_mat.use_nodes = True
bp = bulb_mat.node_tree.nodes.get("Principled BSDF")
bp.inputs["Base Color"].default_value = (1.0, 0.75, 0.36, 1)
if "Emission Color" in bp.inputs:
    bp.inputs["Emission Color"].default_value = (1.0, 0.59, 0.21, 1)
    bp.inputs["Emission Strength"].default_value = 4.0
elif "Emission" in bp.inputs:
    bp.inputs["Emission"].default_value = (1.0, 0.59, 0.21, 1)

for obj in sc.objects:
    if obj.type != "MESH":
        continue
    names = []
    n = obj
    while n:
        names.append(n.name.lower())
        n = n.parent
    label = " ".join(names)
    if "large_iridescent_bubble" in label:
        obj.data.materials.clear()
        obj.data.materials.append(bubble_mat)
        for poly in obj.data.polygons:
            poly.use_smooth = True
    elif "bulb_" in label:
        obj.data.materials.clear()
        obj.data.materials.append(bulb_mat)
    elif any(s in label for s in ("floor", "wall", "ceiling", "shaft", "column", "vault")):
        obj.data.materials.clear()
        obj.data.materials.append(stone_mat)

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass

# Projection check. Values are printed separately from reference estimates.
from mathutils import Vector
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y
)
landmarks = [
    ("far arch crown", (0.0, 10.0, 7.2), (0.50, 0.32)),
    ("left column capital", (-3.5, 1.0, 3.69), (0.24, 0.46)),
    ("near railing endpoint", (-1.48, -2.91, 1.72), (0.20, 0.80)),
]
print("Landmark | reference estimate | projected")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5 * (clip.x / clip.w + 1),
        0.5 * (1 - clip.y / clip.w)
    )
    print(name, reference, None if uv is None else tuple(round(v, 3) for v in uv))
