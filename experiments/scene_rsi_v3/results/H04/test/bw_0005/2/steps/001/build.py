# Reference inventory and visual anchors, estimated from the small classroom inset:
# The inset occupies approximately (0.58, 0.44)–(0.91, 0.96) of the supplied
# 512 x 288 graphic; the surrounding text and portraits are not part of the room.
# Within the inset, a row of tall windows occupies the upper back wall, light wood
# flooring covers the lower half, and low wooden shelves divide the room.
# A foreground open cabinet overlaps a red oval rug; low cabinets and activity
# tables sit behind it. The right and rear edges of the room are partly occluded.
# Dominant edges of shelves and flooring converge toward the back of the room.
# Scene landmarks below are approximate room-relative estimates, not calibration.
#
# Expanded primitive estimate: approximately 190 boxes and rods, including
# architecture, window frames, furniture, trays, materials and floor seams.
# No fillet boxes, tube expansions, Boolean operations or external assets.

import bpy
import math
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

scene = Scene("Montessori classroom")

# Major dimensions and camera are independent parameters, in meters.
ROOM_W, ROOM_D, ROOM_H = 8.0, 6.2, 3.0
CAMERA_POSITION = (8.6, -9.5, 4.7)
CAMERA_TARGET = (0.0, 0.35, 0.72)
CAMERA_LENS = 31

cream = (0.82, 0.80, 0.70)
floor_color = (0.65, 0.47, 0.29)
wood = (0.59, 0.38, 0.20)
wood_light = (0.72, 0.52, 0.30)
wood_dark = (0.38, 0.23, 0.12)
window_frame = (0.88, 0.87, 0.79)
glass = (0.66, 0.79, 0.79)
rug_color = (0.48, 0.12, 0.08)
white = (0.88, 0.86, 0.76)
green = (0.25, 0.42, 0.19)
blue = (0.19, 0.37, 0.49)
yellow = (0.83, 0.61, 0.20)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Architecture: only the rear and right walls are present so the view remains open.
architecture = Asset("Architecture")
add_box(architecture, "light wood floor", (ROOM_W, ROOM_D, 0.10),
        (0, 0, -0.05), floor_color)
add_box(architecture, "rear cream wall", (ROOM_W, 0.12, ROOM_H),
        (0, ROOM_D / 2, ROOM_H / 2), cream)
add_box(architecture, "right cream wall", (0.12, ROOM_D, ROOM_H),
        (ROOM_W / 2, 0, ROOM_H / 2), cream)
add_box(architecture, "rear baseboard", (ROOM_W, 0.06, 0.12),
        (0, ROOM_D / 2 - 0.08, 0.06), window_frame)
add_box(architecture, "right baseboard", (0.06, ROOM_D, 0.12),
        (ROOM_W / 2 - 0.08, 0, 0.06), window_frame)
# Restrained floor plank seams.
for i in range(16):
    x = -ROOM_W / 2 + (i + 1) * ROOM_W / 17
    add_box(architecture, "floor seam %02d" % i, (0.008, ROOM_D, 0.002),
            (x, 0, 0.002), (0.48, 0.34, 0.21))
scene.include("architecture", architecture)

# The rear windows read as a continuous daylight row, with individual frames.
windows = Asset("Rear window row")
window_y = ROOM_D / 2 - 0.075
for i in range(6):
    x = -3.27 + i * 1.28
    add_box(windows, "window glass %d" % i, (1.15, 0.025, 1.48),
            (x, window_y, 1.99), glass)
    for dx in (-0.59, 0.59):
        add_box(windows, "window upright %d %.2f" % (i, dx),
                (0.055, 0.06, 1.60), (x + dx, window_y - 0.025, 1.99),
                window_frame)
    for z in (1.21, 2.77):
        add_box(windows, "window rail %d %.2f" % (i, z),
                (1.23, 0.06, 0.06), (x, window_y - 0.025, z),
                window_frame)
    add_box(windows, "window center mullion %d" % i, (0.035, 0.06, 1.48),
            (x, window_y - 0.04, 1.99), window_frame)
add_box(windows, "continuous sill", (7.85, 0.20, 0.08),
        (0, window_y - 0.08, 1.18), window_frame)
scene.include("windows", windows)

def shelf(name, x, y, width, depth, height, facing="front"):
    """Open shelf with broad top, two tiers and visible partitions."""
    a = Asset(name)
    t = 0.045
    add_box(a, "top", (width, depth, t), (x, y, height - t / 2), wood_light)
    add_box(a, "bottom", (width, depth, t), (x, y, 0.085), wood)
    add_box(a, "middle shelf", (width, depth, t),
            (x, y, height * 0.51), wood_light)
    for side in (-1, 1):
        add_box(a, "side %d" % side, (t, depth, height - 0.10),
                (x + side * (width - t) / 2, y, height / 2 + 0.02), wood)
    add_box(a, "center partition", (t, depth, height - 0.16),
            (x, y, height / 2), wood)
    # Thin rear panel keeps the front compartments readable.
    back_y = y + depth / 2 - t / 2 if facing == "front" else y - depth / 2 + t / 2
    add_box(a, "back panel", (width - 2 * t, 0.025, height - 0.12),
            (x, back_y, height / 2), wood_dark)
    scene.include(name, a)
    return a

# Cabinet positions reflect the reference: a long foreground island, other
# islands behind it, and storage along the window wall and room edge.
shelf("foreground open cabinet", 0.55, -1.65, 2.20, 0.58, 0.88)
shelf("middle left cabinet", -2.10, 0.55, 1.72, 0.52, 0.85)
shelf("middle right cabinet", 1.35, 0.92, 1.65, 0.52, 0.84)
shelf("rear left cabinet", -2.65, 2.54, 1.90, 0.52, 0.80)
shelf("rear center cabinet", -0.30, 2.54, 1.65, 0.52, 0.80)
shelf("rear right cabinet", 2.25, 2.54, 1.80, 0.52, 0.80)

# Loose, simplified Montessori materials: shallow trays and a few blocks.
materials = Asset("Montessori materials")
def tray(name, x, y, z, w=0.38, d=0.25):
    add_box(materials, name + " base", (w, d, 0.035), (x, y, z), wood_dark)
    for s in (-1, 1):
        add_box(materials, name + " long rim %d" % s,
                (w, 0.025, 0.055), (x, y + s * d / 2, z + 0.035), wood_light)
        add_box(materials, name + " end rim %d" % s,
                (0.025, d, 0.055), (x + s * w / 2, y, z + 0.035), wood_light)

for i, (x, y, z) in enumerate([
    (-2.65, 0.55, 0.88), (-1.92, 0.55, 0.88),
    (0.88, 0.92, 0.87), (1.57, 0.92, 0.87),
    (-3.18, 2.54, 0.83), (-2.48, 2.54, 0.83),
    (-0.55, 2.54, 0.83), (1.85, 2.54, 0.83),
    (2.48, 2.54, 0.83),
    (-0.15, -1.65, 0.91), (0.55, -1.65, 0.91), (1.25, -1.65, 0.91),
]):
    tray("tray %02d" % i, x, y, z)

for i, (x, y, z, c) in enumerate([
    (-2.65, 0.55, 0.96, yellow), (-1.92, 0.55, 0.96, blue),
    (0.88, 0.92, 0.95, green), (1.57, 0.92, 0.95, yellow),
    (-0.15, -1.65, 0.99, blue), (0.55, -1.65, 0.99, yellow),
    (1.25, -1.65, 0.99, green), (-2.48, 2.54, 0.91, yellow),
]):
    add_box(materials, "learning block %d" % i, (0.12, 0.10, 0.09),
            (x, y, z), c)
# A few boxes inside the foreground cabinet make the open compartments legible.
for i, (x, z) in enumerate([(-0.13, 0.19), (0.53, 0.19), (1.24, 0.19),
                             (-0.13, 0.55), (0.66, 0.55), (1.29, 0.55)]):
    add_box(materials, "cabinet material %d" % i, (0.30, 0.24, 0.13),
            (x, -1.78, z), wood_light if i % 2 else white)
scene.include("materials", materials)

def table(name, x, y, width=1.25, depth=0.70):
    a = Asset(name)
    add_box(a, "top", (width, depth, 0.065), (x, y, 0.59), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(a, "leg %d %d" % (sx, sy), (0.06, 0.06, 0.55),
                    (x + sx * (width / 2 - 0.09),
                     y + sy * (depth / 2 - 0.09), 0.28), wood)
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    add_box(a, "seat", (0.33, 0.31, 0.045), (x, y, 0.34), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(a, "leg %d %d" % (sx, sy), (0.035, 0.035, 0.31),
                    (x + sx * 0.125, y + sy * 0.11, 0.16), wood)
    scene.include(name, a)

table("central activity table", -0.55, 0.25)
table("right activity table", 2.62, -0.20, 1.05, 0.65)
for i, (x, y) in enumerate([(-1.02, -0.35), (0.0, -0.35),
                             (-0.75, 0.85), (2.35, -0.79), (2.98, -0.79)]):
    stool("child stool %d" % i, x, y)

# A low cylinder, scaled after realization, forms the round rust-red rug.
rug = Asset("Round red rug")
rug.include("rug disk", rod(radius=1.0, length=0.018,
                             center=(0.53, -1.65, 0.012), axis="+z",
                             color=rug_color))
scene.include("rug", rug)

# A low display ledge on the right, present near the right side of the inset.
shelf("right side storage", 3.25, 1.60, 1.05, 0.45, 0.78)

realize(scene)

# Room appearance and renderer.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.78, 0.84, 0.89, 1)
background.inputs["Strength"].default_value = 0.65

sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# Warm daylight from behind the window row, plus broad ambient fill.
area_emitter((0, 4.3, 3.5), power=1800, size=5.0,
             target=(0, -0.3, 0.5), color=(1.0, 0.91, 0.77))
area_emitter((-3.0, -4.5, 5.5), power=900, size=7.0,
             target=(0, 0, 0.5), color=(1.0, 0.96, 0.88))

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
bpy.context.view_layer.update()

# Reference estimates are relative to the room inset, not the surrounding graphic.
# They identify geometry landmarks; projection does not establish visibility.
landmarks = [
    ("left window upper corner", (-3.86, window_y, 2.77), (0.08, 0.05)),
    ("right window upper corner", (3.72, window_y, 2.77), (0.89, 0.05)),
    ("foreground shelf top left", (-0.55, -1.94, 0.88), (0.35, 0.58)),
    ("foreground shelf top right", (1.65, -1.94, 0.88), (0.77, 0.69)),
    ("rear shelf corner", (-3.60, 2.28, 0.80), (0.08, 0.44)),
]

def project(point):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y
    )
    clip = matrix @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    if clip.w <= 1e-8:
        return None
    return (0.5 * (clip.x / clip.w + 1),
            0.5 * (1 - clip.y / clip.w))

print("Landmark: reference inset UV -> projected UV")
for name, point, reference in landmarks:
    print(name, reference, "->", project(point))
