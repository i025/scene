# Reference and last-render comparison, estimated in phone-screen coordinates:
# 1. Vaults: the reference has broad curved, shaded vault surfaces and ribs
#    converging toward a bright arcade. The render is a pale, symmetric tunnel
#    with thin angular outlines and little visible vault curvature.
# 2. Foreground: the reference railing enters at lower left and slopes down to
#    the right, with stairs visible behind it. In the render its left endpoint
#    is around (.31,.64), and it crosses most of the lower frame. Lower the
#    stair assembly and extend it left; the railing remains open.
# 3. Large bubble: the reference bubble is cropped at the right screen edge;
#    the render shows a complete circle approximately (.60,.42)-(.86,.88).
#    Move its center right and enlarge it, retaining the small sphere behind.
# 4. Small sphere: the reference is dark magenta; the rendered sphere is pale
#    pink near (.47,.62). Use a darker, saturated material and directional light.
# 5. Background: the reference is bright with shadowed columns and openings;
#    the render's far end is flat and lacks depth. Increase the contrast between
#    stone, shadowed recesses, and daylight, without darkening the whole hall.
# Camera remains at the previous tested pose: the observed discrepancies are
# mainly local and the last projection trial showed that a higher aim moves all
# landmarks down together. The numeric table below reports geometry projections,
# not observed silhouette positions or proof of visibility.
#
# Inventory: vaulted hall and side arcades, background and upper frame; clustered
# columns on both sides; marble stair and ornate rail in lower foreground;
# suspended chandelier left of center; small magenta and large iridescent spheres
# in the corridor, with the large one overlapping the right arcade. Screen edges
# and hidden structure make exact geometry and depth uncertain.
# Approximate expanded primitive count: architecture 5; transverse ribs 96;
# diagonals 60; columns 84; side arches 60; openings 21; stairs and rail 55;
# chandelier 14; spheres 2, plus a few lights: approximately 400 meshes.
# Every rod, box, and ball is one primitive; no Boolean or fillet expansion.

from sceneact import *
import bpy
import math
from mathutils import Vector

CAMERA_POSITION = (0.1, -9.3, 4.2)
CAMERA_TARGET = (0.0, 5.2, 3.75)
CAMERA_LENS = 29
HALL_WIDTH = 7.0
HALL_HEIGHT = 7.2
BAYS = [-2.0, 1.0, 4.0, 7.0, 10.0, 13.0]
STAIR_Y = -1.9
STAIR_LIFT = 1.15
BUBBLE_CENTER = (4.2, .95, 2.9)
BUBBLE_RADIUS = 1.95

stone = (.65, .58, .48)
light_stone = (.80, .74, .64)
rib_color = (.32, .27, .22)
red = (.24, .018, .018)
gold = (.55, .32, .075)
dark = (.08, .06, .045)

scene = Scene("Neo-Gothic heritage hall")

def line(parent, name, a, b, radius, color):
    if sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-8:
        parent.include(name, rod(radius, start=a, end=b, color=color))

def path(parent, name, points, radius, color):
    for i in range(len(points) - 1):
        line(parent, "%s_%02d" % (name, i),
             points[i], points[i + 1], radius, color)

architecture = Asset("Vaults")
architecture.include("floor", box((8.5, 22, .18),
    center=(0, 3.5, -.09), color=(.57, .51, .43)))
architecture.include("left_wall", box((.24, 22, 7.5),
    center=(-4.25, 3.5, 3.75), color=stone))
architecture.include("right_wall", box((.24, 22, 7.5),
    center=(4.25, 3.5, 3.75), color=stone))
architecture.include("ceiling", box((8.5, 22, .18),
    center=(0, 3.5, 7.45), color=light_stone))
architecture.include("far_wall", box((8.5, .18, 7.5),
    center=(0, 14.1, 3.75), color=light_stone))

for j, y in enumerate(BAYS):
    bay = Asset("Vault bay %02d" % j)
    profile = [
        (-3.5, y, 3.7), (-3.32, y, 4.58),
        (-2.85, y, 5.44), (-2.02, y, 6.25),
        (-1.02, y, 6.86), (0, y, HALL_HEIGHT),
        (1.02, y, 6.86), (2.02, y, 6.25),
        (2.85, y, 5.44), (3.32, y, 4.58), (3.5, y, 3.7)
    ]
    path(bay, "deep_rib", profile, .105, rib_color)
    path(bay, "rib_highlight",
         [(x * .97, yy - .04, z - .09) for x, yy, z in profile],
         .035, light_stone)
    architecture.include("bay_%02d" % j, bay)

line(architecture, "ridge", (0, -2, 7.2), (0, 13, 7.2), .055, rib_color)
for j in range(len(BAYS) - 1):
    y0, y1 = BAYS[j], BAYS[j + 1]
    ym = (y0 + y1) / 2
    for side in (-1, 1):
        for k, yy in enumerate((y0, y1)):
            path(architecture, "diagonal_%d_%d_%d" % (j, side, k),
                 [(side * 3.5, yy, 3.9),
                  (side * 2.65, (yy + ym) / 2, 5.35),
                  (side * 1.35, ym, 6.45),
                  (0, ym, 7.16)], .065, rib_color)
scene.include("Vaults", architecture)

columns = Asset("Columns and pointed arcades")
for j, y in enumerate(BAYS):
    for side in (-1, 1):
        x = side * 3.5
        col = Asset("Clustered column")
        col.include("main_shaft", rod(.19, start=(x, y, .15),
                                     end=(x, y, 3.68), color=light_stone))
        for k, (dx, dy) in enumerate(((-.17, 0), (.17, 0),
                                      (0, -.16), (0, .16))):
            col.include("cluster_%d" % k, rod(.065,
                start=(x + dx, y + dy, .16),
                end=(x + dx, y + dy, 3.62), color=stone))
        col.include("base", box((.61, .61, .2),
                                center=(x, y, .12), color=stone))
        col.include("capital", box((.67, .67, .22),
                                   center=(x, y, 3.69), color=light_stone))
        columns.include("column_%d_%d" % (side, j), col)

for side in (-1, 1):
    for j in range(len(BAYS) - 1):
        y0, y1 = BAYS[j], BAYS[j + 1]
        ym = (y0 + y1) / 2
        x = side * 3.53
        path(columns, "side_arch_%d_%d" % (side, j),
             [(x, y0, 3.65), (x, y0 + .25, 4.25),
              (x, y0 + .75, 4.75), (x, ym, 5.18),
              (x, y1 - .75, 4.75), (x, y1 - .25, 4.25),
              (x, y1, 3.65)], .075, rib_color)
scene.include("Columns", columns)

openings = Asset("Arcade openings")
for side in (-1, 1):
    for j, y in enumerate((2.5, 5.5, 8.5, 11.5)):
        openings.include("side_recess_%d_%d" % (side, j),
            box((.035, 1.55, 2.5), center=(side * 4.10, y, 2.4),
                color=(.24, .21, .17)))
        openings.include("side_light_%d_%d" % (side, j),
            box((.04, .85, 1.8), center=(side * 4.07, y, 2.55),
                color=(.78, .76, .66)))
for j, x in enumerate((-2.2, -1.1, 0, 1.1, 2.2)):
    openings.include("far_daylight_%d" % j,
        box((.68, .035, 3.1), center=(x, 13.98, 3.25),
            color=(1.0, .94, .80)))
scene.include("Arcade openings", openings)

stairs = Asset("Staircase and railing")
stairs.include("upper_landing", box((3.6, 2.0, .20),
    center=(-1.85, STAIR_Y + .95, .65 + STAIR_LIFT), color=light_stone))
for i in range(10):
    x = -1.80 + i * .38
    z = .64 - i * .13 + STAIR_LIFT
    stairs.include("marble_tread_%02d" % i,
        box((.40, 1.45, .13), center=(x, STAIR_Y, z), color=light_stone))
    stairs.include("tread_nosing_%02d" % i,
        box((.045, 1.47, .035), center=(x + .19, STAIR_Y, z + .055),
            color=stone))

rail_y = STAIR_Y - .76
x0, x1 = -2.10, 1.90
z0, z1 = 1.72 + STAIR_LIFT, .35 + STAIR_LIFT
line(stairs, "gold_handrail", (x0, rail_y, z0), (x1, rail_y, z1), .055, gold)
line(stairs, "red_lower_rail", (x0, rail_y, z0 - .70),
     (x1, rail_y, z1 - .70), .045, red)
line(stairs, "gold_middle_rail", (x0, rail_y, z0 - .37),
     (x1, rail_y, z1 - .37), .025, gold)
for i in range(14):
    t = i / 13
    x = x0 + (x1 - x0) * t
    z = z0 + (z1 - z0) * t
    line(stairs, "baluster_%02d" % i, (x, rail_y, z - .70),
         (x, rail_y, z), .027, red)
    if i < 13:
        line(stairs, "diagonal_ornament_%02d" % i,
             (x + .04, rail_y, z - .62),
             (x + .27, rail_y, z - .20), .021, red)
scene.include("Staircase & railing", stairs)

chandelier = Asset("Chandelier")
cx, cy, cz = -1.15, 2.1, 3.25
line(chandelier, "suspension", (cx, cy, 6.8),
     (cx, cy, cz + .45), .025, dark)
chandelier.include("brass_body", ball(.15, center=(cx, cy, cz), color=gold))
for i in range(6):
    a = 2 * math.pi * i / 6
    end = (cx + .62 * math.cos(a), cy + .62 * math.sin(a), cz + .08)
    line(chandelier, "arm_%02d" % i, (cx, cy, cz), end, .035, gold)
    chandelier.include("bulb_%02d" % i,
        ball(.085, center=(end[0], end[1], end[2] + .10),
             color=(1, .82, .52)))
scene.include("Chandelier", chandelier)

spheres = Asset("Spheres")
spheres.include("large_iridescent_bubble",
    ball(BUBBLE_RADIUS, center=BUBBLE_CENTER, color=(.6, .25, .55)))
spheres.include("small_magenta_sphere",
    ball(.42, center=(-.38, 3.45, 2.72), color=(.32, .001, .18)))
scene.include("Spheres", spheres)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
sc.render.image_settings.file_format = "PNG"

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
wn = sc.world.node_tree.nodes
background = wn.get("Background")
if background is None:
    background = wn.new("ShaderNodeBackground")
output = wn.get("World Output")
if output is None:
    output = wn.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68, .63, .54, 1)
background.inputs["Strength"].default_value = .25

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Same projection check as the earlier build; the small upward-aim trial is
# printed and restored, so the final camera retains its established framing.
landmarks = [
    ("far arch crown", (0, 10, 7.2), (.50, .32)),
    ("left column capital", (-3.5, 1, 3.69), (.24, .46)),
    ("rail left endpoint", (x0, rail_y, z0), (.20, .80)),
    ("bubble leftmost", (BUBBLE_CENTER[0] - BUBBLE_RADIUS,
                          BUBBLE_CENTER[1], BUBBLE_CENTER[2]), (.70, .50)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    mat = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name, point, ref in landmarks:
        clip = mat @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
        print(name, "reference estimate", ref, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

projection_table("Established camera")
cam = sc.camera
original_rotation = cam.rotation_euler.copy()
cam.rotation_euler = (Vector((0, 5.2, 3.95)) -
                      Vector(CAMERA_POSITION)).to_track_quat('-Z', 'Y').to_euler()
projection_table("Trial higher aim")
cam.rotation_euler = original_rotation
bpy.context.view_layer.update()

area_emitter((-1.2, 1.8, 3.6), power=850, size=1.4,
             target=(0, 1, 2.5), color=(1, .75, .48))
area_emitter((0, 12.8, 5.8), power=2800, size=4.0,
             target=(0, 3, 3), color=(1, .93, .81))
area_emitter((-3, -4, 6.5), power=400, size=5,
             target=(0, 2, 3), color=(1, .84, .68))

for name in ("Vaults", "Columns", "Staircase & railing", "Chandelier", "Spheres"):
    if bpy.data.collections.get(name) is None:
        coll = bpy.data.collections.new(name)
        sc.collection.children.link(coll)

stone_mat = bpy.data.materials.new("Aged warm sandstone")
stone_mat.use_nodes = True
nodes = stone_mat.node_tree.nodes
links = stone_mat.node_tree.links
p = nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (.65, .58, .48, 1)
p.inputs["Roughness"].default_value = .78
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 8
noise.inputs["Detail"].default_value = 3
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .12
bump.inputs["Distance"].default_value = .025
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], p.inputs["Normal"])

bubble_mat = bpy.data.materials.new("Thin-film interference")
bubble_mat.use_nodes = True
nodes = bubble_mat.node_tree.nodes
links = bubble_mat.node_tree.links
p = nodes.get("Principled BSDF")
p.inputs["Roughness"].default_value = .09
p.inputs["Metallic"].default_value = .10
p.inputs["IOR"].default_value = 1.33
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value = .32
elif "Transmission" in p.inputs:
    p.inputs["Transmission"].default_value = .32
facing = nodes.new("ShaderNodeLayerWeight")
facing.inputs["Blend"].default_value = .35
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors = [
    (0.00, (.95, .02, .44, 1)),
    (.12, (1.0, .37, .015, 1)),
    (.24, (.95, .85, .025, 1)),
    (.36, (.02, .75, .67, 1)),
    (.48, (.10, .16, .95, 1)),
    (.60, (.76, .02, .75, 1)),
    (.72, (1.0, .44, .05, 1)),
    (.84, (.05, .76, .77, 1)),
    (1.0, (.80, .95, .90, 1)),
]
for i, (position, color) in enumerate(colors):
    e = ramp.color_ramp.elements[0] if i == 0 else ramp.color_ramp.elements.new(position)
    e.position = position
    e.color = color
links.new(facing.outputs["Facing"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], p.inputs["Base Color"])

magenta_mat = bpy.data.materials.new("Matte deep magenta")
magenta_mat.use_nodes = True
p = magenta_mat.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (.32, .001, .16, 1)
p.inputs["Roughness"].default_value = .7

bulb_mat = bpy.data.materials.new("Warm luminous glass")
bulb_mat.use_nodes = True
p = bulb_mat.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (1, .8, .5, 1)
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1, .65, .30, 1)
    p.inputs["Emission Strength"].default_value = 4

daylight_mat = bpy.data.materials.new("Soft distant daylight")
daylight_mat.use_nodes = True
p = daylight_mat.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (1, .94, .80, 1)
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1, .90, .72, 1)
    p.inputs["Emission Strength"].default_value = .7

for obj in list(sc.objects):
    if obj.type != "MESH":
        continue
    names = []
    node = obj
    while node:
        names.append(node.name.lower())
        node = node.parent
    label = " ".join(names)
    dest = None
    if "sphere" in label or "bubble" in label:
        dest = "Spheres"
    elif "chandelier" in label or "bulb_" in label:
        dest = "Chandelier"
    elif any(s in label for s in ("staircase", "tread", "baluster", "rail", "ornament", "landing")):
        dest = "Staircase & railing"
    elif any(s in label for s in ("column", "side_arch", "shaft", "capital")):
        dest = "Columns"
    elif any(s in label for s in ("vault", "rib", "wall", "floor", "ceiling", "ridge")):
        dest = "Vaults"
    if dest:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        bpy.data.collections[dest].objects.link(obj)
    mat = None
    if "large_iridescent_bubble" in label:
        mat = bubble_mat
    elif "small_magenta_sphere" in label:
        mat = magenta_mat
    elif "bulb_" in label:
        mat = bulb_mat
    elif "far_daylight" in label:
        mat = daylight_mat
    elif any(s in label for s in ("floor", "wall", "ceiling", "shaft", "column")):
        mat = stone_mat
    if mat:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    if "sphere" in label or "bubble" in label:
        for poly in obj.data.polygons:
            poly.use_smooth = True

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass
