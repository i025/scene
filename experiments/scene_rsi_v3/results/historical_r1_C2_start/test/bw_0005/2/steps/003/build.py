from sceneact import *
import bpy

# Reference inventory, estimated within the classroom photograph:
# - Light wood floor fills the lower half; cream back wall fills the upper half.
# - Four large windows occupy roughly x=0.08–0.60, y=0.05–0.37.
# - Low open wooden shelves line the left and back, with gaps between them.
# - A broad two-tier shelf occupies roughly x=0.38–0.88, y=0.52–0.93,
#   overlapping a dark red round rug. Trays and small objects sit on top.
# - Child-sized tables and stools sit behind it and to the right.
# - A door and additional low furniture are visible at the far right.
# Objects behind the foreground shelf and the room beyond the image edges
# are partly occluded and their exact positions are uncertain.
#
# Render comparison: the previous view exposed the cut edges of the back wall
# and floor, had a large blank right wall, and washed out the wood and windows.
# This version extends the room past the camera framing, turns the camera
# toward the window wall, and reduces the lighting intensity. The cabinet
# arrangement and open, readable shelves are preserved.
#
# Estimated expanded primitive count: room and windows 64, five cabinets 45,
# tables and stools 30, shelf and table materials 40, rug 2; approximately 181.

scene = Scene("Montessori classroom")

wall = (0.80, 0.77, 0.68)
trim = (0.91, 0.89, 0.82)
floor = (0.58, 0.43, 0.30)
seam = (0.46, 0.33, 0.22)
wood = (0.53, 0.33, 0.16)
wood_light = (0.67, 0.47, 0.27)
wood_back = (0.43, 0.29, 0.17)
tray = (0.70, 0.56, 0.37)

def put(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Room architecture")
put(architecture, "floor", (18, 18, 0.10), (0, 0, -0.06), floor)
put(architecture, "back wall", (18, 0.14, 3.1),
    (0, 4.13, 1.55), wall)
put(architecture, "right wall", (0.14, 18, 3.1),
    (5.7, -4.8, 1.55), wall)
put(architecture, "back baseboard", (18, 0.05, 0.13),
    (0, 4.025, 0.075), trim)
put(architecture, "right baseboard", (0.05, 18, 0.13),
    (5.60, -4.8, 0.075), trim)
for i in range(27):
    x = -8.4 + i * 0.63
    put(architecture, "floorboard seam %02d" % i,
        (0.008, 17.8, 0.003), (x, 0, -0.008), seam)

windows = Asset("Back wall daylight windows")
for i, x in enumerate((-3.45, -2.03, -0.61, 0.81, 2.23)):
    put(windows, "pane %d" % i, (1.18, 0.025, 1.48),
        (x, 4.035, 2.06), (0.57, 0.70, 0.67))
    for s in (-1, 1):
        put(windows, "side frame %d %d" % (i, s), (0.07, 0.07, 1.60),
            (x + s * 0.625, 3.99, 2.06), trim)
    for j, z in enumerate((1.29, 2.83)):
        put(windows, "horizontal frame %d %d" % (i, j),
            (1.32, 0.07, 0.075), (x, 3.99, z), trim)
    put(windows, "central mullion %d" % i, (0.035, 0.08, 1.48),
        (x, 3.98, 2.06), trim)
    put(windows, "sill %d" % i, (1.36, 0.19, 0.055),
        (x, 3.94, 1.27), trim)
architecture.include("windows", windows)
put(architecture, "door", (0.035, 1.05, 2.25),
    (5.60, 3.10, 1.125), (0.59, 0.48, 0.34))
put(architecture, "door inset", (0.025, 0.77, 1.82),
    (5.57, 3.10, 1.20), (0.67, 0.57, 0.43))
scene.include("architecture", architecture)

def cabinet(name, x, y, width, depth, height, bays):
    a = Asset(name)
    t = 0.06
    put(a, "bottom", (width, depth, t), (x, y, t / 2), wood)
    put(a, "top", (width + 0.05, depth + 0.04, t),
        (x, y, height - t / 2), wood_light)
    put(a, "middle shelf", (width - 2*t, depth - 0.02, t),
        (x, y, height * 0.50), wood_light)
    for s in (-1, 1):
        put(a, "end panel %d" % s, (t, depth, height),
            (x + s * (width - t) / 2, y, height / 2), wood)
    for i in range(1, bays):
        put(a, "divider %d" % i, (0.045, depth - 0.03, height - 2*t),
            (x - width/2 + width*i/bays, y, height/2), wood)
    put(a, "back panel", (width - 2*t, 0.025, height - 2*t),
        (x, y + depth/2 - 0.025, height/2), wood_back)
    scene.include(name, a)

cabinet("foreground open shelf", 0.45, -1.10, 3.00, 0.75, 0.92, 3)
cabinet("left aisle shelf", -3.20, 0.35, 1.55, 0.65, 0.85, 3)
cabinet("left back shelf", -3.05, 2.85, 2.10, 0.53, 0.80, 3)
cabinet("back wall shelf", -0.40, 3.62, 2.65, 0.48, 0.72, 4)
cabinet("right back shelf", 3.15, 3.25, 1.75, 0.52, 0.78, 3)

materials = Asset("Shelf learning materials")
for i in range(5):
    x = -0.63 + i * 0.54
    put(materials, "top tray %d" % i, (0.40, 0.30, 0.035),
        (x, -1.10, 0.94), tray)
    for j in range(2):
        h = 0.08 + 0.025 * ((i+j) % 3)
        put(materials, "geometric block %d %d" % (i, j),
            (0.09, 0.09, h), (x - 0.10 + j*0.17, -1.10, 0.96 + h/2),
            (0.57, 0.39, 0.20))
for i in range(3):
    x = -0.53 + i * 0.96
    put(materials, "lower tray %d" % i, (0.55, 0.36, 0.07),
        (x, -1.18, 0.12), tray)
    put(materials, "middle box %d" % i, (0.39, 0.29, 0.13),
        (x, -1.17, 0.57), (0.67, 0.52, 0.33))
for i in range(4):
    x = -3.85 + i * 0.50
    put(materials, "left shelf tray %d" % i, (0.35, 0.26, 0.04),
        (x, 2.85, 0.82), tray)
    put(materials, "left shelf block %d" % i, (0.11, 0.11, 0.12),
        (x, 2.85, 0.90), wood_light)
for i in range(4):
    x = -1.28 + i * 0.57
    put(materials, "back shelf box %d" % i, (0.32, 0.25, 0.11),
        (x, 3.60, 0.78), tray)
scene.include("learning materials", materials)

def table(name, x, y, w, d):
    a = Asset(name)
    put(a, "top", (w, d, 0.06), (x, y, 0.60), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, "leg %d %d" % (sx, sy), (0.065, 0.065, 0.57),
                (x + sx*(w/2 - 0.10), y + sy*(d/2 - 0.10), 0.285),
                wood)
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    put(a, "seat", (0.39, 0.36, 0.05), (x, y, 0.35), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, "leg %d %d" % (sx, sy), (0.045, 0.045, 0.33),
                (x + sx*0.15, y + sy*0.13, 0.165), wood)
    scene.include(name, a)

table("center activity table", -0.90, 1.15, 1.55, 0.82)
table("right activity table", 2.20, 1.45, 1.35, 0.75)
stool("center stool left", -1.95, 1.10)
stool("center stool back", -0.65, 1.95)
stool("right stool front", 2.90, 0.75)
stool("right stool back", 2.20, 2.20)

activity = Asset("Activity table materials")
put(activity, "center tray", (0.48, 0.30, 0.035),
    (-0.88, 1.15, 0.65), tray)
for i in range(3):
    put(activity, "center block %d" % i, (0.09, 0.09, 0.10),
        (-1.02 + i*0.14, 1.15, 0.72), wood)
put(activity, "right tray", (0.38, 0.26, 0.035),
    (2.20, 1.45, 0.65), tray)
scene.include("activity materials", activity)

rug = Asset("Round red rug")
rug.include("outer rug", rod(radius=1.34, start=(0.35, -1.05, 0.006),
                             end=(0.35, -1.05, 0.020),
                             color=(0.36, 0.08, 0.045)))
rug.include("inner rug", rod(radius=1.17, start=(0.35, -1.05, 0.021),
                             end=(0.35, -1.05, 0.025),
                             color=(0.48, 0.16, 0.09)))
scene.include("rug", rug)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],
                            output.inputs["Surface"])
background.inputs["Color"].default_value = (0.84, 0.88, 0.93, 1)
background.inputs["Strength"].default_value = 0.28

set_view((3.0, -6.5, 2.7), (0.0, 1.8, 1.05), lens=25)
area_emitter((-1.4, 3.6, 2.7), power=550, size=4.0,
             target=(0, 0.0, 0.4), color=(1.0, 0.90, 0.78))
area_emitter((0.5, -2.5, 3.8), power=220, size=5.0,
             target=(0, 1.0, 0.5), color=(1.0, 0.96, 0.89))

sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
