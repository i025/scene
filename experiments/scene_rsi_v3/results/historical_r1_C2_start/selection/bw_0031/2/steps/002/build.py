# Reference inventory (normalized image coordinates, approximate):
# The lower photograph occupies x=.03-.94, y=.65-1.00. It shows a rectangular
# control room with a pale instrument wall, dark floor, a long sloping console
# in front, and a smaller independent console at the right. The upper photograph
# shows a yellow GRID mimic panel, approximately x=.03-.52, y=.19-.64.
# Rear instruments are partly hidden by the main console. The room above and
# outside the photographic crop is uncertain. The mimic panel's physical
# location in the room is uncertain; it is mounted on the rear wall here.
#
# Named assets: Architecture, Instrument wall, Main console, GRID mimic board,
# Secondary console, and Ceiling fixtures. Their children describe visible parts.
#
# Approximate expanded primitive count: architecture 6, instrument wall 110,
# main console 100, GRID board 40, secondary console 20, fixtures 6: about 282.
# Text labels are additional Blender text objects.
#
# The preceding build failed before rendering because rod() was passed
# positional endpoints. This version supplies start, end, and color by keyword.
# No visual comparison was possible from that failed build.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s Grid Dispatch Control Room")

ivory = (0.68, 0.66, 0.60)
wall = (0.76, 0.74, 0.68)
panel = (0.65, 0.64, 0.59)
panel_light = (0.79, 0.77, 0.70)
dark = (0.14, 0.15, 0.14)
black = (0.035, 0.04, 0.035)
floor_color = (0.31, 0.28, 0.24)
yellow = (0.90, 0.68, 0.12)
red = (0.70, 0.035, 0.025)
amber = (0.95, 0.48, 0.035)
white = (0.87, 0.86, 0.79)

architecture = Asset("Architecture")
architecture.include("Floor", box(size=(10, 8, .12), center=(0, 0, -.06), color=floor_color))
architecture.include("Rear wall", box(size=(10, .16, 3.7), center=(0, 3.8, 1.85), color=wall))
architecture.include("Right wall", box(size=(.16, 8, 3.7), center=(4.92, 0, 1.85), color=wall))
architecture.include("Ceiling", box(size=(10, 8, .12), center=(0, 0, 3.76), color=ivory))
architecture.include("Rear skirting", box(size=(9.8, .06, .12), center=(0, 3.68, .06), color=dark))
architecture.include("Right skirting", box(size=(.06, 7.8, .12), center=(4.82, 0, .06), color=dark))
scene.include("Architecture", architecture)

wall_panels = Asset("Rear instrument wall")
for i in range(9):
    x = -4.35 + i * .76
    wall_panels.include(
        "Cabinet_%02d" % i,
        box(size=(.735, .09, 3.12), center=(x, 3.68, 1.62), color=panel_light))
    wall_panels.include(
        "Cabinet_seam_%02d" % i,
        box(size=(.018, .015, 3.05), center=(x + .36, 3.615, 1.62), color=dark))

for bank, columns in enumerate(((-4.47, -4.00, -3.53),
                                (-.74, -.27, .20, .67))):
    for col, x in enumerate(columns):
        for row in range(4):
            z = 1.20 + row * .42
            name = "%d_%d_%d" % (bank, col, row)
            wall_panels.include(
                "Meter_frame_" + name,
                box(size=(.31, .035, .31), center=(x, 3.608, z), color=dark))
            wall_panels.include(
                "Meter_face_" + name,
                box(size=(.245, .025, .245), center=(x, 3.582, z), color=white))
            wall_panels.include(
                "Meter_pointer_" + name,
                box(size=(.016, .012, .09), center=(x + .025, 3.565, z), color=black))

wall_panels.include(
    "Vent recess",
    box(size=(1.48, .035, .72), center=(-2.0, 3.60, 1.82), color=dark))
for i in range(7):
    wall_panels.include(
        "Vent slat_%02d" % i,
        box(size=(1.36, .02, .032),
            center=(-2.0, 3.572, 1.55 + .09 * i), color=panel_light))
scene.include("Instrument wall", wall_panels)

console = Asset("Main sloping operating console")
console.include(
    "Cabinet body",
    box(size=(5.65, 1.28, .73), center=(-.55, -.40, .365), color=dark))
console.include(
    "Front fascia",
    box(size=(5.65, .06, .50), center=(-.55, -1.06, .46), color=panel))
console.include(
    "Writing ledge",
    box(size=(5.85, .48, .075), center=(-.55, -1.16, .84), color=panel_light))
console.include(
    "Writing ledge rim",
    box(size=(5.85, .035, .10), center=(-.55, -1.40, .81), color=dark))

angle = 18.0
a = math.radians(angle)
surface_y = -.30
surface_z = 1.02
surface_depth = 1.38

def slope_point(x, t, lift=0.0):
    return (x,
            surface_y + t * math.cos(a) - lift * math.sin(a),
            surface_z + t * math.sin(a) + lift * math.cos(a))

def deck_box(size, center, color):
    obj = box(size=size, center=center, color=color)
    obj.turn(axis="+x", degrees=angle)
    return obj

console.include(
    "Inclined control deck",
    deck_box((5.65, surface_depth, .10), (-.55, surface_y, surface_z), panel_light))

for i in range(7):
    x = -3.23 + i * .88
    console.include(
        "Deck divider_%02d" % i,
        deck_box((.025, 1.25, .015), slope_point(x, 0, .065), dark))

for col in range(17):
    x = -3.13 + col * .32
    for row in range(4):
        t = -.49 + row * .30
        name = "%02d_%02d" % (col, row)
        if row == 3 and col % 3 == 0:
            console.include(
                "Instrument frame_" + name,
                deck_box((.20, .19, .018), slope_point(x, t, .065), dark))
            console.include(
                "Instrument face_" + name,
                deck_box((.15, .14, .012), slope_point(x, t, .079), white))
        else:
            console.include(
                "Control_" + name,
                ball(radius=.043 if row < 2 else .035,
                     center=slope_point(x, t, .10),
                     color=black if (col + row) % 4 else red))
    if col % 2 == 0:
        console.include(
            "Switch_%02d" % col,
            deck_box((.09, .13, .018), slope_point(x, .02, .075), dark))
scene.include("Main console", console)

grid = Asset("GRID single line mimic panel")
gx, gy, gz = -3.22, 3.49, 2.35
grid.include(
    "Yellow enamel board",
    box(size=(1.36, .08, 1.95), center=(gx, gy, gz), color=yellow))
front = gy - .055

def grid_line(name, x1, z1, x2, z2, width=.025):
    grid.include(
        name,
        rod(radius=width / 2,
            start=(gx + x1, front, gz + z1),
            end=(gx + x2, front, gz + z2),
            color=black))

grid_line("Main bus", .22, -.82, .22, .83, .035)
grid_line("Upper branch", -.20, .43, .42, .43)
grid_line("Lower branch", -.20, -.34, .42, -.34)
grid_line("Left feeder", -.20, -.34, -.20, .43)
grid_line("Right upper feeder", .42, .43, .42, .13)
grid_line("Right lower feeder", .42, -.34, .42, -.65)
grid_line("Upper crossbar", -.03, .13, .42, .13)
grid_line("Lower crossbar", -.03, -.65, .42, -.65)

for j, z in enumerate((.67, .25, -.18, -.58)):
    grid.include(
        "Red signal_%d" % j,
        ball(radius=.055, center=(gx - .43, front - .025, gz + z), color=red))
    grid.include(
        "Rotary dial_%d" % j,
        box(size=(.16, .02, .16),
            center=(gx - .43, front - .01, gz + z), color=white))
    grid.include(
        "Black selector_%d" % j,
        ball(radius=.038, center=(gx - .43, front - .035, gz + z), color=black))

for j, (x, z) in enumerate(((.02, .43), (.22, .43), (.42, .43),
                            (.02, -.34), (.22, -.34), (.42, -.34),
                            (.22, .75), (.22, -.76))):
    grid.include(
        "Indicator surround_%d" % j,
        box(size=(.105, .025, .12),
            center=(gx + x, front - .015, gz + z), color=black))
    grid.include(
        "Amber indicator_%d" % j,
        box(size=(.065, .025, .08),
            center=(gx + x, front - .034, gz + z), color=amber))
scene.include("GRID mimic board", grid)

right = Asset("Right side console and opening")
right.include(
    "Opening surround",
    box(size=(.05, 1.15, 1.95), center=(4.805, 2.14, 1.55), color=ivory))
right.include(
    "Opening dark interior",
    box(size=(.035, .83, 1.62), center=(4.775, 2.14, 1.48), color=dark))
right.include(
    "Door lower panel",
    box(size=(.025, .77, .67), center=(4.748, 2.14, .99), color=panel))
right.include(
    "Small console base",
    box(size=(1.35, .76, .72), center=(3.73, 1.80, .36), color=dark))
right.include(
    "Small console deck",
    box(size=(1.40, .83, .12), center=(3.73, 1.80, .78), color=panel_light))
right.include(
    "Small raised back",
    box(size=(1.40, .13, .42), center=(3.73, 2.15, 1.01), color=panel_light))
for i in range(7):
    for j in range(2):
        right.include(
            "Small control_%d_%d" % (i, j),
            ball(radius=.037, center=(3.18 + i * .18, 1.57 + j * .22, .87),
                 color=red if (i + j) % 6 == 0 else black))
scene.include("Secondary console", right)

fixtures = Asset("Fluorescent ceiling fixtures")
for x in (-2.8, 0, 2.8):
    for y in (-1.7, 1.4):
        fixtures.include(
            "Troffer_%s_%s" % (x, y),
            box(size=(1.65, .38, .055), center=(x, y, 3.66), color=white))
scene.include("Ceiling lighting", fixtures)

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
background.inputs["Color"].default_value = (0.71, 0.70, 0.66, 1)
background.inputs["Strength"].default_value = .36

area_emitter((0, -1.5, 3.48), power=800, size=5, target=(0, .5, 0))
area_emitter((-3, 1.4, 3.42), power=400, size=3, target=(-2, 1, 0))
area_emitter((3, 1.3, 3.42), power=350, size=3, target=(2, 1, 0))

def label(body, location, size=.065):
    curve = bpy.data.curves.new("Label_" + body, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = .0005
    obj = bpy.data.objects.new("GRID label " + body, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    mat = bpy.data.materials.get("Label ink")
    if mat is None:
        mat = bpy.data.materials.new("Label ink")
        mat.diffuse_color = (.02, .02, .02, 1)
    curve.materials.append(mat)

label("GRID", (gx - .56, front - .045, gz + .83), .10)
label("FEHLERSTELLE", (gx + .29, front - .045, gz + .76), .045)
label("SCHALTER", (gx - .57, front - .045, gz - .80), .045)

set_view((7.7, -10.8, 5.5), (-.25, .65, 1.35), lens=35)
overview = sc.camera
overview.name = "Camera - room overview"

bpy.ops.object.camera_add(location=(-1.1, -4.7, 2.8))
detail = bpy.context.object
detail.name = "Camera - console and GRID detail"
direction = Vector((-2.25, 1.4, 1.62)) - detail.location
detail.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
detail.data.lens = 45
sc.camera = overview

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass
sc.render.image_settings.file_format = "PNG"
