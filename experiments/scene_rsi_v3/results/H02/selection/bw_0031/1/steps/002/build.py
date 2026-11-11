# Reference anchors, estimated within the room photograph at the bottom of the
# reference: cabinet bank x=0.03–0.65, y=0.66–0.91; doorway x=0.68–0.77,
# y=0.68–0.85; small console x=0.77–0.94, y=0.76–0.94; main console
# x=0.03–0.67, y=0.78–1.00. The main console overlaps the cabinet bank.
# Cabinet horizontal edges rise slightly toward the right; the console's long
# edges rise more strongly toward the right. The console is cropped at left
# and bottom. The right floor is a large dark, open area.
#
# Comparison with previous render: the wall bank appeared around x=.37–.69,
# y=.39–.51 and the desk around x=.22–.60, y=.48–.61, surrounded by empty
# gray exterior. In the reference photograph both fill most of their frame.
# The previous view also exposed the outer side walls, hid the right console
# and doorway, and made instrument details nearly white.
# Largest discrepancies: (1) exterior camera and unused frame, (2) missing
# visible right-hand room features, (3) weak dark/light contrast in controls.
# CAMERA_POS, CAMERA_TARGET and CAMERA_LENS move the camera inside the open
# front, closer and lower; this enlarges the desk and wall and removes exterior
# wall silhouettes. DESK_Y and DESK_W position the desk across the foreground.
# BANK_X and BANK_W extend the instrument wall to the left frame. The doorway
# and smaller desk occupy the right rear; their exact depth is uncertain.
# The separate yellow reference panel has no established position in the room
# photo; it is mounted on the wall beside the right console.
#
# Expanded primitive estimate: architecture 6, wall bank approximately 130,
# main desk approximately 120, small desk 20, GRID panel 45: about 321 meshes.

import math
import bpy
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

ROOM_W, ROOM_D, ROOM_H = 8.4, 6.2, 3.25
BANK_X, BANK_W = -1.35, 5.65
DESK_X, DESK_Y, DESK_W = -1.25, -0.25, 5.75
CAMERA_POS = (-4.7, -8.8, 3.15)
CAMERA_TARGET = (-0.15, 2.05, 1.28)
CAMERA_LENS = 35

wall = (0.69, 0.68, 0.63)
cabinet = (0.65, 0.64, 0.59)
ivory = (0.83, 0.82, 0.75)
paper = (0.90, 0.89, 0.82)
frame = (0.20, 0.20, 0.18)
black = (0.045, 0.045, 0.04)
floor = (0.29, 0.27, 0.24)
yellow = (0.89, 0.68, 0.13)
red = (0.72, 0.025, 0.012)
amber = (1.0, 0.50, 0.025)

scene = Scene("1970s electrical dispatch control room")

room = Asset("Room architecture")
room.include("floor", box((ROOM_W, ROOM_D, .12),
                          center=(0, 0, -.06), color=floor))
room.include("back wall", box((ROOM_W, .12, ROOM_H),
                              center=(0, ROOM_D/2, ROOM_H/2), color=wall))
room.include("right wall", box((.12, ROOM_D, ROOM_H),
                               center=(ROOM_W/2, 0, ROOM_H/2), color=wall))
room.include("left wall", box((.12, ROOM_D, ROOM_H),
                              center=(-ROOM_W/2, 0, ROOM_H/2), color=wall))
# Open ceiling for camera and lighting; troffers indicate the ceiling plane.
for i, x in enumerate((-2.5, 0, 2.5)):
    room.include("fluorescent troffer %d" % i,
                 box((1.4, .40, .045), center=(x, 1.5, 3.15), color=paper))
scene.include("Architecture", room)

bank = Asset("Wall instrument cabinets")
bank.include("cabinet bank", box((BANK_W, .32, 2.35),
    center=(BANK_X, 2.86, 1.53), color=cabinet))
bank.include("upper fascia", box((BANK_W, .34, .25),
    center=(BANK_X, 2.85, 2.58), color=ivory))
for i in range(9):
    x = BANK_X - BANK_W/2 + i * BANK_W/8
    bank.include("cabinet seam %d" % i, box((.014, .018, 2.12),
        center=(x, 2.68, 1.49), color=(.40, .39, .36)))

# Square instruments surround a broad, dark horizontal ventilation grille.
for col in range(12):
    if 5 <= col <= 7:
        continue
    x = BANK_X - 2.58 + col * .45
    for row in range(4):
        z = .83 + row * .34
        bank.include("instrument border %d %d" % (col, row),
            box((.29, .026, .27), center=(x, 2.675, z), color=frame))
        bank.include("instrument face %d %d" % (col, row),
            box((.235, .015, .215), center=(x, 2.653, z), color=ivory))
        bank.include("instrument pointer %d %d" % (col, row),
            rod(.007, start=(x-.045, 2.64, z-.045),
                end=(x+.035, 2.64, z+.055), color=black))
bank.include("vent dark opening", box((1.28, .03, .73),
    center=(-1.20, 2.665, 1.48), color=frame))
for i in range(6):
    bank.include("vent horizontal slat %d" % i, box((1.20, .015, .035),
        center=(-1.20, 2.642, 1.22 + .105*i), color=ivory))
scene.include("Wall instrument bank", bank)

desk = Asset("Main dispatch console")
desk.include("dark pedestal", box((DESK_W-.16, 1.10, .72),
    center=(DESK_X, DESK_Y, .36), color=(.22, .21, .19)))
desk.include("lower plinth", box((DESK_W-.30, 1.0, .12),
    center=(DESK_X, DESK_Y, .07), color=black))
desk.include("horizontal writing ledge", box((DESK_W, .50, .075),
    center=(DESK_X, DESK_Y-.63, .78), color=ivory))
desk.include("front lip", box((DESK_W, .05, .11),
    center=(DESK_X, DESK_Y-.89, .75), color=cabinet))
angle = math.radians(19)
sy, sz = DESK_Y + .10, .96
slab = box((DESK_W, 1.12, .13), center=(DESK_X, sy, sz), color=ivory)
slab.turn(axis="+x", degrees=19)
desk.include("sloping control surface", slab)

def desk_point(x, v, height):
    return (x, sy + v*math.cos(angle) - height*math.sin(angle),
            sz + v*math.sin(angle) + height*math.cos(angle))

for s in range(7):
    x = DESK_X - DESK_W/2 + .42 + s*.82
    plate = box((.73, .91, .018), center=desk_point(x, 0, .075), color=paper)
    plate.turn(axis="+x", degrees=19)
    desk.include("control panel %d" % s, plate)
    for r in range(3):
        for c in range(4):
            xx = x - .255 + c*.17
            v = -.28 + r*.24
            desk.include("switch %d %d %d" % (s, r, c),
                rod(.024, start=desk_point(xx, v, .088),
                    end=desk_point(xx, v, .125), color=frame))
    meter = box((.22, .13, .015), center=desk_point(x, .36, .09), color=frame)
    meter.turn(axis="+x", degrees=19)
    desk.include("panel meter %d" % s, meter)
scene.include("Main dispatch console", desk)

door = Asset("Doorway")
door.include("dark doorway", box((.78, .035, 2.20),
    center=(2.00, 2.985, 1.10), color=(.16, .16, .15)))
door.include("left jamb", box((.09, .10, 2.25),
    center=(1.57, 2.92, 1.12), color=ivory))
door.include("right jamb", box((.09, .10, 2.25),
    center=(2.43, 2.92, 1.12), color=ivory))
door.include("head jamb", box((.95, .10, .10),
    center=(2.00, 2.92, 2.23), color=ivory))
scene.include("Rear doorway", door)

small = Asset("Small independent console")
small.include("cabinet", box((1.35, .78, .77),
    center=(3.22, 2.12, .39), color=(.35, .34, .31)))
small.include("top", box((1.42, .84, .10),
    center=(3.22, 2.12, .81), color=ivory))
for r in range(3):
    for c in range(5):
        x, y = 2.72 + c*.25, 1.86 + r*.22
        small.include("button %d %d" % (r, c),
            rod(.026, start=(x, y, .87), end=(x, y, .90),
                color=red if (r == 0 and c == 4) else frame))
scene.include("Small independent console", small)

# Yellow GRID panel is placed on the back wall to remain visible in the room
# and in the detail camera. Its exact room location is not shown by the source.
grid = Asset("Yellow GRID single line diagram")
gx, gy, gz = 3.32, 2.995, 2.03
grid.include("yellow backboard", box((1.25, .055, 1.55),
    center=(gx, gy, gz), color=yellow))
front = gy - .04

def line(name, x1, z1, x2, z2, radius=.012):
    grid.include(name, rod(radius, start=(x1, front, z1),
                           end=(x2, front, z2), color=black))

bus = gx + .17
line("main bus", bus, gz-.70, bus, gz+.70, .015)
for k, z in enumerate((gz-.36, gz+.23)):
    line("diagram left %d" % k, bus-.22, z-.16, bus-.22, z+.16)
    line("diagram right %d" % k, bus+.22, z-.16, bus+.22, z+.16)
    line("diagram top %d" % k, bus-.22, z+.16, bus+.22, z+.16)
    line("diagram bottom %d" % k, bus-.22, z-.16, bus+.22, z-.16)
    for j in range(3):
        x = bus-.15 + .15*j
        grid.include("amber frame %d %d" % (k, j),
            box((.105, .022, .13), center=(x, front-.014, z), color=black))
        grid.include("amber lamp %d %d" % (k, j),
            box((.065, .018, .09), center=(x, front-.029, z), color=amber))
for j in range(5):
    z = gz+.54-j*.23
    x = gx-.42
    grid.include("selector plate %d" % j,
        box((.15, .018, .16), center=(x, front-.012, z), color=paper))
    grid.include("black selector %d" % j,
        rod(.034, start=(x, front-.025, z), end=(x, front-.065, z), color=black))
    grid.include("red indicator %d" % j,
        rod(.038, start=(x+.17, front-.025, z),
            end=(x+.17, front-.065, z), color=red))
for j, z in enumerate((gz-.64, gz+.56)):
    grid.include("red bus indicator %d" % j,
        box((.08, .025, .10), center=(bus, front-.025, z), color=red))
scene.include("GRID mimic panel", grid)

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
background.inputs["Color"].default_value = (.72, .71, .67, 1)
background.inputs["Strength"].default_value = .30

# Editable German function labels on the front of the yellow panel.
ink = bpy.data.materials.new("Dark German label ink")
ink.diffuse_color = (.02, .02, .015, 1)
def label(name, text, x, z, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.materials.append(ink)
    ob = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(ob)
    ob.location = (x, front-.055, z)
    ob.rotation_euler = (math.pi/2, 0, 0)
label("GRID label", "NETZ", gx+.27, gz+.63, .045)
label("Fault label", "FEHLERSTELLE", gx+.23, gz-.59, .034)
label("Selector label", "SCHALTER", gx-.52, gz-.68, .035)

# Use material colors to identify lamp surfaces after SceneAct realization.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    rgb = tuple(mat.diffuse_color[:3])
    is_red = abs(rgb[0]-.72) < .02 and rgb[1] < .06 and rgb[2] < .05
    is_amber = rgb[0] > .95 and .45 < rgb[1] < .55 and rgb[2] < .08
    if is_red or is_amber:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
            bsdf.inputs["Emission Strength"].default_value = .8

set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS)
overview = sc.camera
overview.name = "Camera - room overview"
set_view((.5, -3.4, 2.45), (2.0, 2.3, 1.35), lens=42)
sc.camera.name = "Camera - console and GRID detail"
sc.camera = overview

area_emitter((-1.5, -.2, 3.15), power=850, size=4.0,
             target=(-.5, 1.5, .8), color=(1.0, .96, .89))
area_emitter((2.4, 1.0, 3.05), power=450, size=2.5,
             target=(2.4, 2.4, 1.0), color=(1.0, .97, .91))
area_emitter((-3.5, -2.0, 2.8), power=300, size=3,
             target=(-1, 2.0, 1.2), color=(1.0, .98, .94))

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.cycles.samples = 32
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
