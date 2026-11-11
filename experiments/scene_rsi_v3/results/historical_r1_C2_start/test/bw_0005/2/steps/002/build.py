from sceneact import *
import bpy

# Reference inventory, estimated within the small classroom photograph:
# - Cream back wall and a nearly full row of tall windows: upper half.
# - Light wood floor: lower half, extending through the foreground.
# - Low open shelves along the left and back, partly occluding one another.
# - A broad foreground shelf with two open tiers, trays and small materials;
#   it overlaps a warm red round rug.
# - Child-scale activity tables and chairs in the center and at the right.
# - A pale door and additional low storage at the far right.
# Fine details and objects partly hidden by the shelf are uncertain.
#
# Comparison with the previous render: the room was shown as a distant cutaway,
# the right wall hid much of the layout, and the furniture occupied too little
# of the frame. This revision puts the camera inside the room, faces the back
# wall more directly, and uses warmer, less washed-out wood and floor colors.
#
# Approximate expanded primitive count: architecture and windows 55, five
# cabinets 45, tables and chairs 58, learning materials 37, rug 2: about 197.

scene = Scene("Montessori classroom")

wall = (0.82, 0.79, 0.70)
trim = (0.93, 0.91, 0.83)
floor_wood = (0.66, 0.50, 0.34)
floor_seam = (0.52, 0.38, 0.25)
wood = (0.56, 0.35, 0.17)
wood_light = (0.70, 0.50, 0.29)
wood_dark = (0.39, 0.24, 0.12)
wood_back = (0.51, 0.35, 0.21)
tray_color = (0.73, 0.59, 0.40)

def put(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Room architecture")
put(architecture, "light wood floor", (9.4, 8.4, 0.10),
    (0, 0, -0.06), floor_wood)
put(architecture, "back wall", (9.4, 0.14, 3.05),
    (0, 4.13, 1.525), wall)
put(architecture, "right wall", (0.14, 8.4, 3.05),
    (4.63, 0, 1.525), wall)
put(architecture, "back baseboard", (9.3, 0.05, 0.13),
    (0, 4.025, 0.075), trim)
put(architecture, "right baseboard", (0.05, 8.2, 0.13),
    (4.53, 0, 0.075), trim)
for i in range(16):
    x = -4.55 + 0.60 * i
    put(architecture, "floorboard seam %02d" % i,
        (0.008, 8.2, 0.003), (x, 0, -0.008), floor_seam)

windows = Asset("Daylight windows")
for i, x in enumerate((-3.45, -2.03, -0.61, 0.81, 2.23)):
    put(windows, "pane %d" % i, (1.18, 0.025, 1.48),
        (x, 4.035, 2.06), (0.65, 0.77, 0.74))
    for s in (-1, 1):
        put(windows, "side frame %d %d" % (i, s), (0.07, 0.07, 1.60),
            (x + s * 0.625, 3.99, 2.06), trim)
    for z in (1.29, 2.83):
        put(windows, "horizontal frame %d %.2f" % (i, z),
            (1.32, 0.07, 0.075), (x, 3.99, z), trim)
    put(windows, "central mullion %d" % i, (0.035, 0.08, 1.48),
        (x, 3.98, 2.06), trim)
    put(windows, "window sill %d" % i, (1.36, 0.19, 0.055),
        (x, 3.94, 1.27), trim)
architecture.include("windows", windows)
put(architecture, "door", (0.035, 1.05, 2.25),
    (4.53, 3.10, 1.125), (0.65, 0.55, 0.41))
put(architecture, "door inset", (0.025, 0.77, 1.82),
    (4.50, 3.10, 1.20), (0.72, 0.64, 0.52))
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
    x = -0.63 + i*0.54
    put(materials, "top tray %d" % i, (0.40, 0.30, 0.035),
        (x, -1.10, 0.94), tray_color)
    for j in range(2):
        h = 0.08 + 0.025*((i+j) % 3)
        put(materials, "geometric block %d %d" % (i, j),
            (0.09, 0.09, h),
            (x - 0.10 + j*0.17, -1.10, 0.96 + h/2),
            (0.64, 0.46, 0.26))
for i in range(3):
    x = -0.53 + i*0.96
    put(materials, "lower tray %d" % i, (0.55, 0.36, 0.07),
        (x, -1.18, 0.12), tray_color)
    put(materials, "middle box %d" % i, (0.39, 0.29, 0.13),
        (x, -1.17, 0.57), (0.70, 0.56, 0.37))
for i in range(4):
    x = -3.85 + i*0.50
    put(materials, "left shelf tray %d" % i, (0.35, 0.26, 0.04),
        (x, 2.85, 0.82), tray_color)
    put(materials, "left shelf block %d" % i, (0.11, 0.11, 0.12),
        (x, 2.85, 0.90), wood_light)
for i in range(4):
    x = -1.28 + i*0.57
    put(materials, "back shelf box %d" % i, (0.32, 0.25, 0.11),
        (x, 3.60, 0.78), tray_color)
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

def chair(name, x, y):
    a = Asset(name)
    put(a, "seat", (0.39, 0.36, 0.05), (x, y, 0.35), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, "leg %d %d" % (sx, sy), (0.045, 0.045, 0.33),
                (x + sx*0.15, y + sy*0.13, 0.165), wood)
    for sx in (-1, 1):
        put(a, "back upright %d" % sx, (0.045, 0.045, 0.34),
            (x + sx*0.15, y + 0.14, 0.53), wood)
    put(a, "backrest", (0.34, 0.05, 0.13),
        (x, y + 0.14, 0.64), wood_light)
    scene.include(name, a)

table("center activity table", -0.90, 1.15, 1.55, 0.82)
table("right activity table", 2.20, 1.45, 1.35, 0.75)
chair("center chair left", -1.95, 1.10)
chair("center chair back", -0.65, 1.95)
chair("right chair front", 2.90, 0.75)
chair("right chair back", 2.20, 2.20)

activity = Asset("Activity table materials")
put(activity, "center tray", (0.48, 0.30, 0.035),
    (-0.88, 1.15, 0.65), tray_color)
for i in range(3):
    put(activity, "center block %d" % i, (0.09, 0.09, 0.10),
        (-1.02 + i*0.14, 1.15, 0.72), wood)
put(activity, "right tray", (0.38, 0.26, 0.035),
    (2.20, 1.45, 0.65), tray_color)
scene.include("activity materials", activity)

rug = Asset("Round red rug")
rug.include("outer rug", rod(radius=1.34, start=(0.35, -1.05, 0.006),
                             end=(0.35, -1.05, 0.020),
                             color=(0.43, 0.12, 0.075)))
rug.include("inner rug", rod(radius=1.17, start=(0.35, -1.05, 0.021),
                             end=(0.35, -1.05, 0.025),
                             color=(0.58, 0.23, 0.13)))
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
background.inputs["Strength"].default_value = 0.35

# The camera sits inside the near corner, looking across the furnishings
# toward the windows. The ceiling height is estimated at 3.05 m.
set_view((3.25, -7.0, 2.75), (-0.10, 1.65, 1.05), lens=24)
area_emitter((-1.25, 3.65, 2.55), power=900, size=4.0,
             target=(0, 0.0, 0.35), color=(1.0, 0.90, 0.76))
area_emitter((0.5, -2.5, 3.5), power=400, size=5.0,
             target=(0, 1.0, 0.5), color=(1.0, 0.96, 0.88))

sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
