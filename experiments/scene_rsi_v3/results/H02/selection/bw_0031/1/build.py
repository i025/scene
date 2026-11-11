# Visual estimates from the room photograph in the reference:
# The instrument wall occupies approximately x=.03-.65, y=.66-.89 of
# the complete poster; the dark doorway is at x=.68-.75, y=.69-.83.
# The foreground console spans x=.03-.67, y=.78-1.00, overlapping the
# instrument wall. Its long edges rise toward the right. The small console
# is at x=.77-.94, y=.76-.90, with open dark floor in front of it.
# The separate yellow panel occupies x=.03-.52, y=.19-.64 of the poster;
# its physical position in the photographed room is not established.
#
# Previous render: the cabinet bank appears approximately x=.09-.63,
# y=.38-.57, the main console x=.10-.90, y=.51-.67, and the yellow panel
# x=.72-.82, y=.37-.48. A broad gray exterior occupies the upper third;
# the doorway and small console are obscured. The main desk is nearly
# horizontal instead of receding strongly to the right, and its control
# face lacks the dark panel outlines seen in the photograph.
#
# Ranked corrections:
# 1. CAMERA_POS and CAMERA_TARGET move the viewpoint inside the room and
#    toward the left; CAMERA_LENS enlarges the room, removes the exterior
#    silhouette and makes desk edges rise toward the right.
# 2. DOOR_X and SMALL_X separate the rear objects from the wall bank;
#    the doorway and small console should appear at the right of the desk.
# 3. DESK_DEPTH increases the visible sloping surface; dark outlines and
#    switches increase contrast. Lower, more distant lighting reduces the
#    washed-out appearance, which is affected by illumination as well as
#    material color and surface orientation.
# The room is rectangular; hidden ceiling and rear depth are uncertain.
# Expanded estimate: architecture 7, instrument bank 125, main desk 120,
# GRID panel 55, small console 18, doorway 5: approximately 330 meshes.

import math
import bpy
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

ROOM_W, ROOM_D, ROOM_H = 8.4, 7.2, 3.2
BACK_Y = 3.6
BANK_X, BANK_W = -1.45, 5.5
DESK_X, DESK_Y, DESK_W, DESK_DEPTH = -1.35, -0.05, 5.7, 1.35
DOOR_X, SMALL_X = 1.85, 3.15
CAMERA_POS = (-3.65, -3.35, 2.45)
CAMERA_TARGET = (-0.05, 2.4, 1.35)
CAMERA_LENS = 25

wall = (0.67, 0.66, 0.62)
cabinet = (0.57, 0.56, 0.52)
ivory = (0.74, 0.73, 0.67)
paper = (0.84, 0.83, 0.76)
frame = (0.13, 0.13, 0.12)
black = (0.025, 0.026, 0.024)
floor = (0.25, 0.23, 0.20)
yellow = (0.80, 0.57, 0.08)
red = (0.72, 0.025, 0.012)
amber = (1.0, 0.48, 0.025)

scene = Scene("1970s grid dispatch room")

room = Asset("Architecture")
room.include("floor", box((ROOM_W, ROOM_D, .12),
    center=(0, 0, -.06), color=floor))
room.include("back wall", box((ROOM_W, .12, ROOM_H),
    center=(0, BACK_Y, ROOM_H/2), color=wall))
room.include("left wall", box((.12, ROOM_D, ROOM_H),
    center=(-ROOM_W/2, 0, ROOM_H/2), color=wall))
room.include("right wall", box((.12, ROOM_D, ROOM_H),
    center=(ROOM_W/2, 0, ROOM_H/2), color=wall))
# The camera is inside the room; the ceiling remains open for visibility.
for i, x in enumerate((-2.4, 0.0, 2.4)):
    room.include("fluorescent troffer %d" % i,
        box((1.35, .36, .045), center=(x, 1.55, 3.12), color=paper))
scene.include("Architecture", room)

bank = Asset("Wall instrument bank")
bank.include("cabinet body", box((BANK_W, .28, 2.45),
    center=(BANK_X, 3.38, 1.53), color=cabinet))
bank.include("upper fascia", box((BANK_W, .30, .28),
    center=(BANK_X, 3.36, 2.61), color=ivory))
for i in range(9):
    x = BANK_X - BANK_W/2 + i*BANK_W/8
    bank.include("vertical seam %d" % i,
        box((.012, .018, 2.13), center=(x, 3.225, 1.48),
            color=(.35, .34, .31)))
for col in range(12):
    if 5 <= col <= 7:
        continue
    x = BANK_X - 2.50 + col*.435
    for row in range(4):
        z = .83 + row*.33
        bank.include("instrument border %d %d" % (col, row),
            box((.285, .028, .26), center=(x, 3.205, z), color=frame))
        bank.include("instrument face %d %d" % (col, row),
            box((.232, .014, .207), center=(x, 3.182, z), color=paper))
        bank.include("instrument pointer %d %d" % (col, row),
            rod(.007, start=(x-.045, 3.171, z-.04),
                end=(x+.035, 3.171, z+.05), color=black))
bank.include("vent dark opening", box((1.25, .03, .70),
    center=(-1.27, 3.20, 1.47), color=frame))
for i in range(6):
    bank.include("vent slat %d" % i,
        box((1.19, .015, .03), center=(-1.27, 3.176, 1.21+i*.105),
            color=ivory))
scene.include("Wall instrument bank", bank)

desk = Asset("Main dispatch console")
desk.include("dark pedestal", box((DESK_W-.15, 1.10, .70),
    center=(DESK_X, DESK_Y, .35), color=(.17, .16, .14)))
desk.include("lower plinth", box((DESK_W-.25, .98, .12),
    center=(DESK_X, DESK_Y, .06), color=black))
desk.include("writing ledge", box((DESK_W, .42, .07),
    center=(DESK_X, DESK_Y-.74, .77), color=paper))
desk.include("front lip", box((DESK_W, .05, .10),
    center=(DESK_X, DESK_Y-.96, .75), color=cabinet))
angle = math.radians(17)
sy, sz = DESK_Y + .02, .96
slab = box((DESK_W, DESK_DEPTH, .12),
    center=(DESK_X, sy, sz), color=ivory)
slab.turn(axis="+x", degrees=17)
desk.include("inclined control surface", slab)

def point_on_desk(x, v, h):
    return (x, sy + v*math.cos(angle) - h*math.sin(angle),
            sz + v*math.sin(angle) + h*math.cos(angle))

for section in range(7):
    x = DESK_X - DESK_W/2 + .41 + section*.81
    border = box((.74, 1.13, .012),
        center=point_on_desk(x, 0, .067), color=frame)
    border.turn(axis="+x", degrees=17)
    desk.include("panel border %d" % section, border)
    face = box((.70, 1.09, .014),
        center=point_on_desk(x, 0, .078), color=paper)
    face.turn(axis="+x", degrees=17)
    desk.include("panel face %d" % section, face)
    for row in range(3):
        for col in range(4):
            xx = x-.25+col*.166
            v = -.34+row*.27
            desk.include("switch %d %d %d" % (section, row, col),
                rod(.023, start=point_on_desk(xx, v, .09),
                    end=point_on_desk(xx, v, .125), color=frame))
    meter = box((.22, .13, .014),
        center=point_on_desk(x, .43, .09), color=frame)
    meter.turn(axis="+x", degrees=17)
    desk.include("console meter %d" % section, meter)
scene.include("Main dispatch console", desk)

door = Asset("Rear doorway")
door.include("dark recess", box((.76, .035, 2.18),
    center=(DOOR_X, 3.525, 1.09), color=(.12, .12, .11)))
door.include("left jamb", box((.08, .10, 2.23),
    center=(DOOR_X-.42, 3.47, 1.11), color=ivory))
door.include("right jamb", box((.08, .10, 2.23),
    center=(DOOR_X+.42, 3.47, 1.11), color=ivory))
door.include("lintel", box((.92, .10, .09),
    center=(DOOR_X, 3.47, 2.22), color=ivory))
door.include("door window", box((.55, .02, .65),
    center=(DOOR_X, 3.495, 1.63), color=(.30, .30, .28)))
scene.include("Rear doorway", door)

small = Asset("Small independent control console")
small.include("cabinet", box((1.35, .75, .77),
    center=(SMALL_X, 2.75, .39), color=(.30, .29, .26)))
small.include("control top", box((1.42, .81, .10),
    center=(SMALL_X, 2.75, .81), color=paper))
for row in range(3):
    for col in range(5):
        x = SMALL_X-.50+col*.25
        y = 2.49+row*.22
        small.include("button %d %d" % (row, col),
            rod(.025, start=(x, y, .87), end=(x, y, .90),
                color=red if (row == 0 and col == 4) else frame))
scene.include("Small independent console", small)

# The separate panel photograph does not establish its room location.
# Place it on the right-hand wall beside the small console.
grid = Asset("Yellow GRID single line diagram")
gx, gy, gz = 3.31, 3.505, 2.12
grid.include("yellow backboard", box((1.25, .055, 1.50),
    center=(gx, gy, gz), color=yellow))
front = gy-.04

def line(name, x1, z1, x2, z2, radius=.012):
    grid.include(name, rod(radius, start=(x1, front, z1),
        end=(x2, front, z2), color=black))

bus = gx+.17
line("main bus", bus, gz-.69, bus, gz+.69, .014)
for k, z in enumerate((gz-.34, gz+.23)):
    line("loop left %d" % k, bus-.22, z-.16, bus-.22, z+.16)
    line("loop right %d" % k, bus+.22, z-.16, bus+.22, z+.16)
    line("loop top %d" % k, bus-.22, z+.16, bus+.22, z+.16)
    line("loop bottom %d" % k, bus-.22, z-.16, bus+.22, z-.16)
    for j in range(3):
        x = bus-.15+j*.15
        grid.include("amber frame %d %d" % (k, j),
            box((.105, .022, .13), center=(x, front-.014, z), color=black))
        grid.include("amber lamp %d %d" % (k, j),
            box((.065, .018, .09), center=(x, front-.029, z), color=amber))
for j in range(5):
    z = gz+.53-j*.22
    x = gx-.42
    grid.include("selector dial %d" % j,
        box((.15, .018, .16), center=(x, front-.012, z), color=paper))
    grid.include("black selector %d" % j,
        rod(.034, start=(x, front-.025, z),
            end=(x, front-.065, z), color=black))
    grid.include("red round indicator %d" % j,
        rod(.038, start=(x+.17, front-.025, z),
            end=(x+.17, front-.065, z), color=red))
for j, z in enumerate((gz-.63, gz+.55)):
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
background.inputs["Color"].default_value = (.70, .69, .65, 1)
background.inputs["Strength"].default_value = .22

ink = bpy.data.materials.new("German label ink")
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

label("Grid label", "NETZ", gx+.25, gz+.62, .045)
label("Fault label", "FEHLERSTELLE", gx+.22, gz-.58, .033)
label("Selector label", "SCHALTER", gx-.52, gz-.68, .034)

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(mat.diffuse_color[:3])
    is_red = abs(rgb[0]-.72) < .02 and rgb[1] < .06 and rgb[2] < .05
    is_amber = rgb[0] > .95 and .43 < rgb[1] < .53 and rgb[2] < .08
    if (is_red or is_amber) and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = .8

set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS)
overview = sc.camera
overview.name = "Camera - room overview"
set_view((.7, -.9, 2.25), (2.5, 3.0, 1.55), lens=38)
sc.camera.name = "Camera - console and GRID detail"
sc.camera = overview

area_emitter((-1.5, .8, 3.05), power=450, size=4.0,
    target=(-.5, 1.8, .8), color=(1.0, .96, .90))
area_emitter((2.4, 1.9, 3.05), power=260, size=2.5,
    target=(2.4, 3.0, 1.0), color=(1.0, .97, .92))
area_emitter((-3.2, -1.0, 2.9), power=180, size=3.0,
    target=(-1, 2.5, 1.2), color=(1.0, .98, .94))

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
