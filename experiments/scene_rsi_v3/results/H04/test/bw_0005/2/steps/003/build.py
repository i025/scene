# Reference inventory, estimated from the classroom photograph in the graphic:
# The photographic inset occupies approximately x=.58-.97, y=.44-.96 in the
# original image. Estimates below are relative to the rectangular inset.
# Back windows: x=.08-.62, y=.07-.31; cream wall continues to the right.
# Foreground cabinet: x=.34-.79, y=.48-.88, overlapping a red oval rug at
# x=.28-.85, y=.70-.97. Its broad front contains dark open shelves.
# Left and rear low shelves: x=.03-.40, y=.32-.67; tables and small chairs
# occupy the middle; another cabinet and materials are visible at right.
# Shelf edges slope down toward the right; depth edges rise toward the right.
# The outer brush boundary obscures parts of the floor and side walls.
#
# Previous render versus reference, using inset-relative visual estimates:
# Background window region was x=.36-.97, y=.18-.51, versus approximately
# x=.08-.62, y=.07-.31 in the photograph. The foreground cabinet was roughly
# x=.21-.50, y=.62-.98, versus x=.34-.79, y=.48-.88 in the photograph.
# A large gray exterior area at upper left and along the left edge is absent
# from the reference. The foreground rug was partly cut off at the bottom.
# The foreground cabinet has a visible open front, but the rendered interior
# is too pale, and the repeated windows occupy too much of the rear wall.
# Reference and render both contain low shelves with gaps between them.
#
# Ranked corrections:
# 1. Extend the floor and back wall beyond the camera's field of view, and
#    remove the intrusive near right wall. This removes gray exterior wedges.
# 2. Turn the camera more directly toward the back wall, with a small sideways
#    offset. Window edges should become closer to horizontal and the left
#    window region should move left. A numerical trial below records the
#    direction of projected foreground and background landmarks.
# 3. Place the main cabinet locally to the right and slightly farther back.
#    Its front should move toward the center-right and upward, keeping more
#    of the rug visible. Reduce its depth and retain broad open shelf gaps.
# 4. Concentrate four windows on the left side of the back wall, leaving a
#    cream wall at right. Reduce light intensity and use warm wood and darker
#    cabinet recesses to improve the broad contrast. Brightness is affected by
#    light and orientation as well as the material colors.
#
# Uncertain: exact furniture and window counts, wall extent beyond the crop,
# and small objects obscured by the brush edge. Major meshes are named assets
# with editable child parts. Ceiling height is estimated at 3.0 m.
#
# Expanded primitive estimate: architecture 18; windows 25; seven cabinets
# about 57; trays and shelf materials about 55; two tables and four stools 30;
# rug 1; total about 186 primitives. No fillets, booleans, clones, or tubes.

import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

scene = Scene("Montessori classroom interior")

# Room, furnishing and camera parameters are independent.
ROOM_WIDTH = 10.5
ROOM_DEPTH = 9.0
ROOM_HEIGHT = 3.0
BACK_Y = 3.4
CAMERA_POSITION = (2.15, -5.3, 2.65)
CAMERA_TARGET = (0.0, 1.1, 1.08)
CAMERA_LENS = 24.0
MAIN_X, MAIN_Y = 0.65, -1.1
MAIN_WIDTH, MAIN_DEPTH, MAIN_HEIGHT = 2.25, 0.58, 0.87

wall = (0.78, 0.75, 0.65)
trim = (0.86, 0.84, 0.75)
floor = (0.63, 0.46, 0.30)
wood = (0.55, 0.35, 0.19)
wood_light = (0.68, 0.47, 0.27)
wood_dark = (0.29, 0.18, 0.095)
glass = (0.61, 0.72, 0.67)
rug_red = (0.43, 0.075, 0.052)
cream = (0.80, 0.77, 0.66)
green = (0.28, 0.39, 0.19)
blue = (0.23, 0.37, 0.39)
yellow = (0.73, 0.51, 0.19)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Room architecture")
add(architecture, "light wood floor",
    (ROOM_WIDTH, ROOM_DEPTH, 0.10), (0, -1.0, -0.05), floor)
add(architecture, "cream back wall",
    (ROOM_WIDTH, 0.12, ROOM_HEIGHT), (0, BACK_Y, ROOM_HEIGHT / 2), wall)
add(architecture, "back skirting",
    (ROOM_WIDTH, 0.06, 0.13), (0, BACK_Y - 0.09, 0.065), trim)
# A distant right wall completes the rectangular room without obscuring furniture.
add(architecture, "right wall", (0.12, ROOM_DEPTH, ROOM_HEIGHT),
    (ROOM_WIDTH / 2, -1.0, ROOM_HEIGHT / 2), wall)
for i in range(14):
    x = -4.8 + i * 0.72
    add(architecture, "subtle floor joint %02d" % i,
        (0.006, ROOM_DEPTH, 0.002), (x, -1.0, 0.002),
        (0.49, 0.35, 0.22))
scene.include("architecture", architecture)

# Four windows on the left rear wall, with a light sill and individual frames.
windows = Asset("Back wall daylight windows")
window_y = BACK_Y - 0.075
for i in range(4):
    x = -3.65 + i * 1.13
    add(windows, "window glass %d" % i, (0.97, 0.028, 1.18),
        (x, window_y, 2.08), glass)
    for s in (-1, 1):
        add(windows, "window side %d %d" % (i, s), (0.06, 0.06, 1.30),
            (x + s * 0.52, window_y - 0.03, 2.08), trim)
    for z in (1.46, 2.70):
        add(windows, "window rail %d %.2f" % (i, z), (1.08, 0.06, 0.06),
            (x, window_y - 0.03, z), trim)
    add(windows, "window mullion %d" % i, (0.035, 0.07, 1.18),
        (x, window_y - 0.04, 2.08), trim)
add(windows, "window sill", (4.55, 0.19, 0.07),
    (-1.955, window_y - 0.08, 1.43), trim)
scene.include("windows", windows)

def shelf(name, x, y, width, depth, height, divisions=2):
    a = Asset(name)
    t = 0.045
    add(a, "top", (width, depth, t), (x, y, height - t / 2), wood_light)
    add(a, "bottom", (width, depth, t), (x, y, 0.07), wood)
    add(a, "middle shelf", (width, depth, t),
        (x, y, height * 0.50), wood_light)
    for side in (-1, 1):
        add(a, "side %d" % side, (t, depth, height - 0.08),
            (x + side * (width - t) / 2, y, height / 2 + 0.01), wood)
    for j in range(1, divisions):
        add(a, "vertical divider %d" % j, (t, depth, height - 0.15),
            (x - width / 2 + width * j / divisions, y, height / 2), wood)
    add(a, "recessed back", (width - 2 * t, 0.025, height - 0.12),
        (x, y + depth / 2 - 0.025, height / 2), wood_dark)
    scene.include(name, a)

shelf("foreground open cabinet", MAIN_X, MAIN_Y, MAIN_WIDTH,
      MAIN_DEPTH, MAIN_HEIGHT, 3)
shelf("left island cabinet", -2.35, 0.45, 1.70, 0.52, 0.82)
shelf("middle island cabinet", 0.25, 1.05, 1.50, 0.52, 0.82)
shelf("back left cabinet", -3.30, 2.98, 1.55, 0.48, 0.80)
shelf("back middle cabinet", -1.35, 2.98, 1.55, 0.48, 0.80)
shelf("back right cabinet", 1.30, 2.98, 1.70, 0.48, 0.80)
shelf("right side cabinet", 3.25, 1.85, 1.30, 0.48, 0.80)

materials = Asset("Loose Montessori materials")
def tray(name, x, y, z, width=0.34, depth=0.22):
    add(materials, name + " base", (width, depth, 0.025), (x, y, z), wood_dark)
    for s in (-1, 1):
        add(materials, name + " long edge %d" % s,
            (width, 0.022, 0.04), (x, y + s * depth / 2, z + 0.025),
            wood_light)
        add(materials, name + " end %d" % s,
            (0.022, depth, 0.04), (x + s * width / 2, y, z + 0.025),
            wood_light)

tray_positions = [
    (-2.80, 0.45, 0.84), (-2.10, 0.45, 0.84),
    (-0.15, 1.05, 0.84), (0.55, 1.05, 0.84),
    (-3.40, 2.98, 0.82), (-1.50, 2.98, 0.82),
    (1.10, 2.98, 0.82), (1.70, 2.98, 0.82),
    (MAIN_X - 0.65, MAIN_Y, 0.89),
    (MAIN_X, MAIN_Y, 0.89),
    (MAIN_X + 0.65, MAIN_Y, 0.89),
]
for i, p in enumerate(tray_positions):
    tray("activity tray %02d" % i, *p)

for i, (x, y, z, c) in enumerate([
    (-2.80, 0.45, 0.91, yellow), (-2.10, 0.45, 0.91, blue),
    (-0.15, 1.05, 0.91, green), (0.55, 1.05, 0.91, yellow),
    (MAIN_X - 0.65, MAIN_Y, 0.96, blue),
    (MAIN_X, MAIN_Y, 0.96, yellow),
    (MAIN_X + 0.65, MAIN_Y, 0.96, green),
]):
    add(materials, "geometric material %d" % i, (0.12, 0.10, 0.08),
        (x, y, z), c)

for i, (dx, z) in enumerate([
    (-0.70, 0.18), (0.0, 0.18), (0.70, 0.18),
    (-0.70, 0.54), (0.0, 0.54), (0.70, 0.54),
]):
    add(materials, "foreground shelf box %d" % i, (0.28, 0.22, 0.11),
        (MAIN_X + dx, MAIN_Y - 0.12, z), cream if i % 2 == 0 else wood_light)
scene.include("learning materials", materials)

def table(name, x, y, width, depth):
    a = Asset(name)
    add(a, "top", (width, depth, 0.06), (x, y, 0.59), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add(a, "leg %d %d" % (sx, sy), (0.055, 0.055, 0.55),
                (x + sx * (width / 2 - 0.08),
                 y + sy * (depth / 2 - 0.08), 0.28), wood)
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    add(a, "seat", (0.32, 0.30, 0.045), (x, y, 0.34), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add(a, "leg %d %d" % (sx, sy), (0.035, 0.035, 0.31),
                (x + sx * 0.12, y + sy * 0.11, 0.16), wood)
    scene.include(name, a)

table("central activity table", -1.20, 1.15, 1.10, 0.65)
table("right activity table", 2.30, 0.35, 1.00, 0.65)
for i, (x, y) in enumerate([
    (-1.55, 0.60), (-0.80, 0.60), (1.95, -0.18), (2.60, -0.18)
]):
    stool("child stool %d" % i, x, y)

rug = Asset("Round red rug")
rug.include("rug disk", rod(radius=1.14, length=0.018,
                            center=(MAIN_X, MAIN_Y, 0.012),
                            axis="+z", color=rug_red))
scene.include("rug", rug)

realize(scene)

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
background.inputs["Color"].default_value = (0.78, 0.83, 0.86, 1)
background.inputs["Strength"].default_value = 0.38

sc.render.engine = "CYCLES"
sc.cycles.samples = 128
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# Large warm source at the window side, with a softer front fill.
area_emitter((-2.0, 2.7, 3.5), power=950, size=4.0,
             target=(0, -0.4, 0.5), color=(1.0, 0.91, 0.78))
area_emitter((1.0, -3.5, 4.6), power=450, size=6.0,
             target=(0, 1.0, 0.6), color=(1.0, 0.96, 0.89))

# Reference coordinates are inset-relative image estimates, not projections.
# The previous camera and a small aim trial are reported for comparison with
# the selected camera. These points do not prove visibility or silhouette.
landmarks = [
    ("left window upper", (-4.17, window_y, 2.70), (0.08, 0.07)),
    ("right window upper", (-0.26, window_y, 2.70), (0.62, 0.07)),
    ("main cabinet upper left",
     (MAIN_X - MAIN_WIDTH / 2, MAIN_Y - MAIN_DEPTH / 2, MAIN_HEIGHT),
     (0.34, 0.48)),
    ("main cabinet upper right",
     (MAIN_X + MAIN_WIDTH / 2, MAIN_Y - MAIN_DEPTH / 2, MAIN_HEIGHT),
     (0.74, 0.58)),
    ("rear shelf left", (-4.075, 2.74, 0.80), (0.04, 0.37)),
    ("rug front", (MAIN_X, MAIN_Y - 1.14, 0.021), (0.54, 0.96)),
]

def project(point):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    if clip.w <= 1e-8:
        return None
    return (round(0.5 * (clip.x / clip.w + 1), 3),
            round(0.5 * (1 - clip.y / clip.w), 3))

def table_of_projections(label):
    print(label)
    for name, point, reference in landmarks:
        print(name, "reference", reference, "computed", project(point))

set_view((3.75, -4.65, 2.75), (-0.05, 1.05, 1.05), lens=23.5, sensor=36)
table_of_projections("Previous camera on revised geometry")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
table_of_projections("Selected camera")
set_view(CAMERA_POSITION,
         (CAMERA_TARGET[0] + 0.15, CAMERA_TARGET[1], CAMERA_TARGET[2]),
         lens=CAMERA_LENS, sensor=36)
table_of_projections("Small trial: aim 0.15 m right")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
bpy.context.view_layer.update()
