# Reference inventory, normalized to the visible phone-screen interior:
# - Receding warm stone rib vaults occupy the upper half; arches and clustered
#   columns converge toward the bright background. Outer structure is occluded.
# - A marble stair and dark-red, gold-trimmed open balustrade occupy the lower
#   left and cross diagonally toward the lower right.
# - A brass chandelier hangs left of center, above the stair.
# - A small dark magenta sphere overlaps the distant arcade near center;
#   a much larger rainbow bubble overlaps the right arcade and is cropped right.
#
# Comparison with the previous full render, estimated from the supplied images:
# - Background vault: reference has strongly shaded curved ribs and bright
#   openings; render has pale, nearly uniform angular outlines (largest contrast
#   discrepancy). Darken ribs and add varied recessed wall openings.
# - Foreground stair/railing: reference occupies roughly the lower third, with
#   diagonal open red metalwork; render is almost entirely absent below the
#   floor. Raise and move this asset independently into the visible foreground.
# - Large bubble: reference is cropped at the right and has saturated bands;
#   render is a complete pale circle around x=.62, y=.65. Enlarge it and move
#   it to the right; use a more saturated interference shader.
# - Small sphere: reference is deep magenta with a dark side; render is pale
#   pink near x=.47, y=.62. Darken its material and reduce frontal illumination.
# - The rendered hall is symmetric and the reference is partially obscured;
#   exact correspondences and hidden geometry remain uncertain.
# Camera parameters remain unchanged, preserving the established background
# framing. The camera trial below checks projection direction and is restored.
#
# Approximate expanded primitive count: architecture 5, arch ribs 96,
# diagonal ribs 60, columns 84, side arches 60, window panels 12, stairs and
# railing 57, chandelier 14, spheres 2: about 390 meshes. Each rod, ball or
# box is one primitive. No fillet boxes, sweeps, or Boolean operations.

from sceneact import *
import bpy
import math
from mathutils import Vector

HALL_HALF_WIDTH = 3.5
HALL_HEIGHT = 7.2
BAY_YS = [-2.0, 1.0, 4.0, 7.0, 10.0, 13.0]

CAMERA_POSITION = (0.1, -9.3, 4.2)
CAMERA_TARGET = (0.0, 5.2, 3.75)
CAMERA_LENS = 29

STONE = (0.64, 0.57, 0.46)
LIGHT_STONE = (0.79, 0.73, 0.63)
RIB = (0.34, 0.29, 0.24)
RED = (0.25, 0.025, 0.025)
GOLD = (0.55, 0.32, 0.08)
DARK = (0.09, 0.065, 0.045)
MAGENTA = (0.42, 0.003, 0.24)

scene = Scene("Neo-Gothic heritage hall")

def line(parent, name, a, b, radius, color):
    if sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-8:
        parent.include(name, rod(radius, start=a, end=b, color=color))

def path(parent, name, points, radius, color):
    for i in range(len(points) - 1):
        line(parent, "%s_%02d" % (name, i), points[i], points[i + 1],
             radius, color)

architecture = Asset("Vaults")
architecture.include("floor", box((8.5, 22, .18),
    center=(0, 3.5, -.09), color=(.58, .52, .44)))
architecture.include("left_wall", box((.24, 22, 7.5),
    center=(-4.25, 3.5, 3.75), color=STONE))
architecture.include("right_wall", box((.24, 22, 7.5),
    center=(4.25, 3.5, 3.75), color=STONE))
architecture.include("ceiling", box((8.5, 22, .18),
    center=(0, 3.5, 7.45), color=LIGHT_STONE))
architecture.include("far_wall", box((8.5, .18, 7.5),
    center=(0, 14.1, 3.75), color=LIGHT_STONE))

for j, y in enumerate(BAY_YS):
    bay = Asset("Vault bay %02d" % j)
    profile = [
        (-3.5, y, 3.7), (-3.30, y, 4.65),
        (-2.75, y, 5.55), (-1.70, y, 6.48),
        (0, y, HALL_HEIGHT), (1.70, y, 6.48),
        (2.75, y, 5.55), (3.30, y, 4.65), (3.5, y, 3.7)
    ]
    path(bay, "deep_rib", profile, .10, RIB)
    path(bay, "rib_highlight",
         [(x * .97, yy - .04, z - .09) for x, yy, z in profile],
         .035, LIGHT_STONE)
    architecture.include("bay_%02d" % j, bay)

line(architecture, "ridge", (0, -2, 7.2), (0, 13, 7.2), .055, RIB)
for j in range(len(BAY_YS) - 1):
    y0, y1 = BAY_YS[j], BAY_YS[j + 1]
    ym = (y0 + y1) / 2
    for side in (-1, 1):
        for k, yy in enumerate((y0, y1)):
            path(architecture, "diagonal_%d_%d_%d" % (j, side, k),
                 [(side * 3.5, yy, 3.9),
                  (side * 2.65, (yy + ym) / 2, 5.35),
                  (side * 1.35, ym, 6.45), (0, ym, 7.16)],
                 .065, RIB)
scene.include("Vaults", architecture)

columns = Asset("Columns and pointed arcades")
for j, y in enumerate(BAY_YS):
    for side in (-1, 1):
        x = side * 3.5
        col = Asset("Clustered column")
        col.include("main_shaft", rod(.19, start=(x, y, .15),
                                      end=(x, y, 3.68), color=LIGHT_STONE))
        for k, (dx, dy) in enumerate(((-.17, 0), (.17, 0), (0, -.16), (0, .16))):
            col.include("cluster_%d" % k, rod(.065,
                start=(x + dx, y + dy, .16),
                end=(x + dx, y + dy, 3.62), color=STONE))
        col.include("base", box((.61, .61, .2), center=(x, y, .12), color=STONE))
        col.include("capital", box((.67, .67, .22),
                                   center=(x, y, 3.69), color=LIGHT_STONE))
        columns.include("column_%d_%d" % (side, j), col)

for side in (-1, 1):
    for j in range(len(BAY_YS) - 1):
        y0, y1 = BAY_YS[j], BAY_YS[j + 1]
        ym = (y0 + y1) / 2
        x = side * 3.53
        path(columns, "side_arch_%d_%d" % (side, j),
             [(x, y0, 3.65), (x, y0 + .25, 4.25),
              (x, y0 + .75, 4.75), (x, ym, 5.18),
              (x, y1 - .75, 4.75), (x, y1 - .25, 4.25),
              (x, y1, 3.65)], .075, RIB)
scene.include("Columns", columns)

# Bright far-end glazing and darker side recesses provide depth cues.
openings = Asset("Arcade openings")
for side in (-1, 1):
    for j, y in enumerate((2.5, 5.5, 8.5, 11.5)):
        openings.include("side_recess_%d_%d" % (side, j),
            box((.035, 1.55, 2.5), center=(side * 4.10, y, 2.4),
                color=(.30, .27, .23)))
        openings.include("side_light_%d_%d" % (side, j),
            box((.04, .85, 1.8), center=(side * 4.07, y, 2.55),
                color=(.77, .76, .66)))
for x in (-2.2, -1.1, 0, 1.1, 2.2):
    openings.include("far_daylight_%s" % x,
        box((.68, .035, 3.1), center=(x, 13.98, 3.25),
            color=(1.0, .92, .73)))
scene.include("Arcade openings", openings)

# The stair is raised into view locally; the camera and vaults remain unchanged.
stairs = Asset("Staircase and railing")
STAIR_Y = -1.9
STAIR_LIFT = 1.65
stairs.include("upper_landing", box((3.4, 2.0, .20),
    center=(-1.35, STAIR_Y + .95, .65 + STAIR_LIFT), color=LIGHT_STONE))
for i in range(9):
    x = -1.30 + i * .38
    z = .64 - i * .13 + STAIR_LIFT
    stairs.include("marble_tread_%02d" % i,
        box((.40, 1.45, .13), center=(x, STAIR_Y, z), color=LIGHT_STONE))
    stairs.include("tread_nosing_%02d" % i,
        box((.045, 1.47, .035), center=(x + .19, STAIR_Y, z + .055), color=STONE))

rail_y = STAIR_Y - .76
x0, x1 = -1.48, 2.12
z0, z1 = 1.72 + STAIR_LIFT, .48 + STAIR_LIFT
line(stairs, "gold_handrail", (x0, rail_y, z0), (x1, rail_y, z1), .055, GOLD)
line(stairs, "red_lower_rail", (x0, rail_y, z0 - .70),
     (x1, rail_y, z1 - .70), .045, RED)
line(stairs, "gold_middle_rail", (x0, rail_y, z0 - .37),
     (x1, rail_y, z1 - .37), .025, GOLD)
for i in range(13):
    t = i / 12
    x = x0 + (x1 - x0) * t
    z = z0 + (z1 - z0) * t
    line(stairs, "baluster_%02d" % i, (x, rail_y, z - .70),
         (x, rail_y, z), .027, RED)
    if i < 12:
        line(stairs, "diagonal_ornament_%02d" % i,
             (x + .04, rail_y, z - .62),
             (x + .26, rail_y, z - .20), .021, RED)
scene.include("Staircase & railing", stairs)

chandelier = Asset("Chandelier")
cx, cy, cz = -1.15, 2.1, 3.25
line(chandelier, "suspension", (cx, cy, 6.8), (cx, cy, cz + .45), .025, DARK)
chandelier.include("brass_body", ball(.15, center=(cx, cy, cz), color=GOLD))
for i in range(6):
    a = 2 * math.pi * i / 6
    end = (cx + .62 * math.cos(a), cy + .62 * math.sin(a), cz + .08)
    line(chandelier, "arm_%02d" % i, (cx, cy, cz), end, .035, GOLD)
    chandelier.include("bulb_%02d" % i,
        ball(.085, center=(end[0], end[1], end[2] + .10),
             color=(1, .82, .52)))
scene.include("Chandelier", chandelier)

spheres = Asset("Spheres")
spheres.include("large_iridescent_bubble",
    ball(1.65, center=(2.9, .95, 2.85), color=(.6, .25, .55)))
spheres.include("small_magenta_sphere",
    ball(.38, center=(-.38, 3.45, 2.72), color=MAGENTA))
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
background.inputs["Color"].default_value = (.62, .58, .50, 1)
background.inputs["Strength"].default_value = .20

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Projection check: the trial aim is higher and should move stationary points
# downward. Restore the original camera after printing both projections.
landmarks = [
    ("far arch crown", (0, 10, 7.2), (.50, .32)),
    ("left column capital", (-3.5, 1, 3.69), (.24, .46)),
    ("raised railing endpoint", (-1.48, rail_y, z0), (.20, .80)),
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
        print(name, "reference", ref, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

projection_table("Original camera")
cam = sc.camera
original_rotation = cam.rotation_euler.copy()
cam.rotation_euler = (Vector((0, 5.2, 3.95)) -
                      Vector(CAMERA_POSITION)).to_track_quat('-Z', 'Y').to_euler()
projection_table("Trial higher aim")
cam.rotation_euler = original_rotation
bpy.context.view_layer.update()

area_emitter((-1.2, 1.8, 3.6), power=800, size=1.4,
             target=(0, 1, 2.5), color=(1, .72, .42))
area_emitter((0, 12.8, 5.8), power=2400, size=4.0,
             target=(0, 3, 3), color=(1, .90, .72))
area_emitter((-3, -4, 6.5), power=450, size=5,
             target=(0, 2, 3), color=(1, .84, .66))

# Named collections supplement the SceneAct semantic hierarchy.
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

bubble_mat = bpy.data.materials.new("Saturated thin-film interference")
bubble_mat.use_nodes = True
nodes = bubble_mat.node_tree.nodes
links = bubble_mat.node_tree.links
p = nodes.get("Principled BSDF")
p.inputs["Roughness"].default_value = .12
p.inputs["Metallic"].default_value = .16
p.inputs["IOR"].default_value = 1.33
if "Transmission Weight" in p.inputs:
    p.inputs["Transmission Weight"].default_value = .28
elif "Transmission" in p.inputs:
    p.inputs["Transmission"].default_value = .28
facing = nodes.new("ShaderNodeLayerWeight")
facing.inputs["Blend"].default_value = .35
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
colors = [
    (0.00, (.95, .02, .44, 1)),
    (.15, (1.0, .37, .015, 1)),
    (.30, (.95, .85, .025, 1)),
    (.45, (.02, .75, .67, 1)),
    (.60, (.10, .16, .95, 1)),
    (.75, (.76, .02, .75, 1)),
    (.90, (1.0, .44, .05, 1)),
    (1.0, (.80, .95, .90, 1)),
]
for i, (position, color) in enumerate(colors):
    e = ramp.color_ramp.elements[0] if i == 0 else ramp.color_ramp.elements.new(position)
    e.position = position
    e.color = color
links.new(facing.outputs["Facing"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], p.inputs["Base Color"])

bulb_mat = bpy.data.materials.new("Warm luminous glass")
bulb_mat.use_nodes = True
p = bulb_mat.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value = (1, .8, .5, 1)
if "Emission Color" in p.inputs:
    p.inputs["Emission Color"].default_value = (1, .65, .30, 1)
    p.inputs["Emission Strength"].default_value = 4

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
    if "large_iridescent_bubble" in label:
        obj.data.materials.clear()
        obj.data.materials.append(bubble_mat)
        for poly in obj.data.polygons:
            poly.use_smooth = True
    elif "bulb_" in label:
        obj.data.materials.clear()
        obj.data.materials.append(bulb_mat)
    elif any(s in label for s in ("floor", "wall", "ceiling", "shaft", "column")):
        obj.data.materials.clear()
        obj.data.materials.append(stone_mat)

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass
