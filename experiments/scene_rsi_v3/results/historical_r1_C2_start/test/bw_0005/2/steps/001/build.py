from sceneact import *
import bpy
import math

# Reference inventory, estimated from the classroom photograph at the right of
# the supplied graphic (rough normalized bounds within that photograph):
# - Rectangular room: floor 0.00–1.00 x 0.45–1.00; cream back wall above it.
# - Four tall windows: approximately 0.08–0.58 x 0.05–0.38, with white frames.
# - Low wooden storage along the left and back walls: 0.04–0.48 x 0.37–0.70.
# - Large open shelf in the foreground: 0.37–0.91 x 0.52–0.97, with a top,
#   sides, shelves, dividers, and small learning materials.
# - Child-scale work tables and chairs occupy the middle and right; some are
#   partially hidden by the foreground shelf. A round rug is beneath that shelf.
# - A door or tall pale panel is at the far right. Small items and the room
#   beyond the photograph's irregular border are uncertain.
#
# Approximate expanded primitive count: architecture 33, foreground cabinet 28,
# other storage 55, tables and stools 45, materials 55, rug 2: about 218 meshes.
# Dimensions and placement below remain explicit for subsequent adjustment.

scene = Scene("Montessori classroom")
wood = (0.56, 0.34, 0.17)
wood_light = (0.73, 0.53, 0.31)
wood_edge = (0.47, 0.27, 0.12)
wood_inside = (0.64, 0.43, 0.23)
cream = (0.86, 0.84, 0.77)
white = (0.94, 0.93, 0.87)
dark = (0.22, 0.18, 0.13)
floor_color = (0.68, 0.53, 0.38)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
add_box(architecture, "light wood floor", (9.2, 7.3, 0.12),
        (0, 0, -0.07), floor_color)
add_box(architecture, "back cream wall", (9.2, 0.16, 3.15),
        (0, 3.62, 1.575), cream)
add_box(architecture, "right cream wall", (0.16, 7.3, 3.15),
        (4.55, 0, 1.575), cream)
add_box(architecture, "back baseboard", (9.1, 0.06, 0.13),
        (0, 3.50, 0.085), white)
add_box(architecture, "right baseboard", (0.06, 7.1, 0.13),
        (4.44, 0, 0.085), white)

# Subtle seams describe long floor boards without overwhelming the room.
for i in range(15):
    x = -4.4 + i * 0.62
    add_box(architecture, "floor plank seam %02d" % i,
            (0.009, 7.15, 0.004), (x, 0, 0.001), (0.55, 0.42, 0.31))

windows = Asset("Back wall windows")
for i, x in enumerate((-3.25, -1.82, -0.39, 1.04)):
    # Pale daylight panes sit just in front of the opaque back wall.
    add_box(windows, "window %d daylight" % i, (1.13, 0.035, 1.46),
            (x, 3.515, 2.02), (0.69, 0.80, 0.79))
    for side in (-1, 1):
        add_box(windows, "window %d side frame %d" % (i, side),
                (0.065, 0.065, 1.58), (x + side * 0.59, 3.47, 2.02), white)
    for z in (1.24, 2.80):
        add_box(windows, "window %d horizontal frame %.2f" % (i, z),
                (1.25, 0.065, 0.07), (x, 3.47, z), white)
    add_box(windows, "window %d central sash" % i, (0.035, 0.07, 1.48),
            (x, 3.455, 2.02), white)
    add_box(windows, "window %d sill" % i, (1.32, 0.19, 0.065),
            (x, 3.43, 1.23), white)
architecture.include("windows", windows)
add_box(architecture, "right wall door", (0.04, 1.0, 2.35),
        (4.445, 2.45, 1.175), (0.68, 0.57, 0.42))
add_box(architecture, "door inset", (0.025, 0.72, 1.82),
        (4.42, 2.45, 1.22), (0.73, 0.64, 0.51))
scene.include("architecture", architecture)

def cabinet(name, cx, cy, width, depth, height, compartments=3, back=True):
    a = Asset(name)
    t = 0.065
    add_box(a, "bottom", (width, depth, t), (cx, cy, t / 2), wood)
    add_box(a, "top", (width + 0.06, depth + 0.04, t),
            (cx, cy, height - t / 2), wood_light)
    for sign in (-1, 1):
        add_box(a, "side %d" % sign, (t, depth, height),
                (cx + sign * (width - t) / 2, cy, height / 2), wood)
    add_box(a, "middle shelf", (width - 2 * t, depth - 0.03, t),
            (cx, cy, height * 0.50), wood_light)
    for j in range(1, compartments):
        x = cx - width / 2 + width * j / compartments
        add_box(a, "divider %d" % j, (t * 0.7, depth - 0.03, height - 2 * t),
                (x, cy, height / 2), wood_inside)
    if back:
        add_box(a, "back panel", (width - 2 * t, 0.025, height - 2 * t),
                (cx, cy + depth / 2 - 0.025, height / 2), wood_inside)
    scene.include(name, a)
    return a

# Main low open shelf, facing the viewer, with generous visible compartments.
cabinet("foreground open materials shelf", 1.0, -0.95, 2.95, 0.73, 0.90, 3)
cabinet("left aisle shelf", -2.9, 0.45, 1.75, 0.63, 0.84, 3)
cabinet("left back shelf", -2.75, 2.48, 2.1, 0.54, 0.78, 3)
cabinet("back wall shelf", -0.15, 2.88, 2.5, 0.48, 0.70, 4)
cabinet("right wall low shelf", 3.35, 2.48, 1.60, 0.52, 0.75, 3)

# Small, individually readable Montessori trays and blocks on the shelves.
materials = Asset("Montessori learning materials")
for i in range(5):
    x = -0.15 + i * 0.57
    add_box(materials, "foreground top tray %d" % i, (0.40, 0.29, 0.045),
            (x, -0.95, 0.94), (0.78, 0.65, 0.44))
    for j in range(2):
        add_box(materials, "foreground geometric block %d %d" % (i, j),
                (0.09, 0.09, 0.09 + 0.025 * ((i + j) % 3)),
                (x - 0.10 + j * 0.17, -0.95, 1.02 + 0.0125 * ((i + j) % 3)),
                (0.70, 0.53 + 0.04 * (i % 2), 0.30))
for i in range(3):
    x = -0.04 + i * 0.96
    add_box(materials, "shelf lower tray %d" % i, (0.55, 0.39, 0.07),
            (x, -1.04, 0.13), (0.70, 0.50, 0.27))
    add_box(materials, "shelf middle box %d" % i, (0.39, 0.30, 0.13),
            (x, -1.03, 0.60), (0.76, 0.61, 0.40))
for i in range(4):
    x = -3.50 + 0.52 * i
    add_box(materials, "back shelf tray %d" % i, (0.36, 0.28, 0.04),
            (x, 2.45, 0.82), (0.78, 0.68, 0.50))
    add_box(materials, "back shelf block %d" % i, (0.12, 0.12, 0.12),
            (x, 2.45, 0.90), (0.62, 0.45, 0.26))
for i in range(4):
    x = -1.05 + 0.57 * i
    add_box(materials, "back wall box %d" % i, (0.32, 0.25, 0.11),
            (x, 2.85, 0.79), (0.77, 0.63, 0.42))
scene.include("learning materials", materials)

def table(name, x, y, w, d):
    a = Asset(name)
    add_box(a, "table top", (w, d, 0.065), (x, y, 0.60), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(a, "leg %d %d" % (sx, sy), (0.065, 0.065, 0.57),
                    (x + sx * (w / 2 - 0.10),
                     y + sy * (d / 2 - 0.10), 0.285), wood)
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    add_box(a, "seat", (0.38, 0.34, 0.055), (x, y, 0.35), wood_light)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(a, "leg %d %d" % (sx, sy), (0.045, 0.045, 0.33),
                    (x + sx * 0.14, y + sy * 0.12, 0.165), wood)
    scene.include(name, a)

table("center activity table", -0.65, 1.02, 1.55, 0.82)
table("right activity table", 2.25, 1.25, 1.30, 0.72)
stool("center stool left", -1.65, 0.95)
stool("center stool back", -0.45, 1.70)
stool("right stool", 2.95, 0.80)
stool("right back stool", 2.25, 1.90)

table_items = Asset("Activity table materials")
add_box(table_items, "center tray", (0.49, 0.31, 0.035),
        (-0.60, 1.02, 0.65), (0.76, 0.62, 0.42))
for i in range(3):
    add_box(table_items, "table block %d" % i, (0.09, 0.09, 0.10),
            (-0.75 + i * 0.14, 1.02, 0.72), (0.69, 0.48, 0.27))
add_box(table_items, "right table tray", (0.38, 0.26, 0.035),
        (2.25, 1.25, 0.65), (0.78, 0.66, 0.47))
scene.include("activity table materials", table_items)

# A shallow elliptical-looking round rug is visible beneath the central shelf.
rug = Asset("Round warm red rug")
rug.include("outer rug", rod(radius=1.24, start=(0.85, -0.88, 0.012),
                             end=(0.85, -0.88, 0.028), color=(0.47, 0.16, 0.10)))
rug.include("inner rug", rod(radius=1.08, start=(0.85, -0.88, 0.029),
                             end=(0.85, -0.88, 0.034), color=(0.61, 0.29, 0.16)))
scene.include("round rug", rug)

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
background.inputs["Color"].default_value = (0.83, 0.88, 0.95, 1)
background.inputs["Strength"].default_value = 0.55

set_view((8.9, -12.8, 6.9), (0.0, 0.45, 0.85), lens=33)
area_emitter((-2.0, 2.9, 3.3), power=1100, size=5.0,
             target=(0, 0, 0.3), color=(1.0, 0.91, 0.79))
area_emitter((1.0, -3.0, 5.8), power=700, size=5.0,
             target=(0, 0.7, 0.4), color=(1.0, 0.96, 0.88))
