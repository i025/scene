# Reference inventory, approximate normalized image bounds:
# - The lower photograph occupies x=.03-.94, y=.65-1.00. Its rectangular
#   room has a pale rear instrument wall, a right wall, and a dark floor.
#   Ceiling and room boundaries beyond the crop are uncertain.
# - The rear wall carries rows of square, dark-framed meters, with a wide
#   horizontal ventilation grille left of center. The main console occludes
#   the lower portion of the wall.
# - A long console extends diagonally across the foreground. It has a dark
#   cabinet, pale horizontal writing ledge, sloping control deck, and many
#   small controls. A smaller independent console stands at the right.
# - The upper photograph shows a yellow GRID mimic board at x=.03-.52,
#   y=.19-.64, with a black single-line diagram, red round indicators,
#   amber rectangular indicators, black selectors, and German labels.
#   Its exact position in the room is uncertain; it is placed on the rear wall.
#
# Review of the successful preceding render: the camera was outside the room,
# so the ceiling and right wall obscured most of the interior. The console was
# too small in the frame and the right console was hidden. This revision moves
# the overview camera inside the room and frames the rear wall and both desks.
#
# Approximate expanded primitive count: architecture 5, instrument wall 116,
# main console 160, GRID board 45, secondary console 25, fixtures 4:
# approximately 355 meshes. Text objects are additional.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s Grid Dispatch Control Room")

wall = (0.69, 0.68, 0.64)
ceiling = (0.76, 0.75, 0.71)
panel = (0.72, 0.71, 0.66)
light_panel = (0.82, 0.81, 0.76)
meter_face = (0.88, 0.87, 0.81)
dark = (0.18, 0.18, 0.17)
black = (0.035, 0.038, 0.035)
floor_color = (0.27, 0.25, 0.22)
yellow = (0.91, 0.68, 0.12)
red = (0.70, 0.035, 0.02)
amber = (0.96, 0.42, 0.025)

architecture = Asset("Architecture")
architecture.include("Floor", box(size=(12, 10, .12),
                                  center=(0, 0, -.06), color=floor_color))
architecture.include("Rear wall", box(size=(12, .15, 3.7),
                                      center=(0, 4.0, 1.85), color=wall))
architecture.include("Right wall", box(size=(.15, 10, 3.7),
                                       center=(5.93, -.95, 1.85), color=wall))
architecture.include("Ceiling", box(size=(12, 10, .12),
                                    center=(0, 0, 3.76), color=ceiling))
architecture.include("Rear skirting", box(size=(11.8, .04, .12),
                                          center=(0, 3.90, .06), color=dark))
scene.include("Architecture", architecture)

# The cabinets fill the visible back wall. Meter banks flank the vent.
instruments = Asset("Rear instrument cabinets")
for i in range(12):
    x = -4.95 + i * .78
    instruments.include("Cabinet %02d" % i,
        box(size=(.76, .08, 3.12), center=(x, 3.88, 1.61), color=panel))
    instruments.include("Vertical seam %02d" % i,
        box(size=(.014, .012, 3.05), center=(x + .38, 3.829, 1.61), color=dark))

meter_columns = [-4.95, -4.48, -4.01, -3.54, -0.72, -0.25, .22, .69, 1.16]
for col, x in enumerate(meter_columns):
    for row in range(4):
        z = 1.17 + row * .41
        key = "%02d_%02d" % (col, row)
        instruments.include("Meter frame " + key,
            box(size=(.30, .035, .30), center=(x, 3.805, z), color=dark))
        instruments.include("Meter face " + key,
            box(size=(.235, .018, .235), center=(x, 3.777, z), color=meter_face))
        instruments.include("Meter needle " + key,
            box(size=(.012, .01, .085), center=(x + .02, 3.761, z), color=black))

instruments.include("Vent recess",
    box(size=(1.55, .035, .73), center=(-2.22, 3.80, 1.84), color=dark))
for i in range(7):
    instruments.include("Vent slat %02d" % i,
        box(size=(1.43, .02, .035),
            center=(-2.22, 3.77, 1.56 + i * .09), color=light_panel))
scene.include("Instrument wall", instruments)

# Main operating desk: a pale sloping deck over a dark cabinet, with a
# separate horizontal ledge at the operator's side.
console = Asset("Main sloping operating console")
console.include("Cabinet body",
    box(size=(6.15, 1.34, .76), center=(-1.0, -.10, .38), color=dark))
console.include("Front fascia",
    box(size=(6.15, .055, .48), center=(-1.0, -.80, .48), color=panel))
console.include("Lower plinth",
    box(size=(5.96, 1.20, .13), center=(-1.0, -.08, .065), color=black))
console.include("Horizontal writing ledge",
    box(size=(6.30, .46, .075), center=(-1.0, -1.00, .83), color=light_panel))
console.include("Ledge front trim",
    box(size=(6.30, .035, .08), center=(-1.0, -1.23, .81), color=dark))

slope_angle = 17.0
a = math.radians(slope_angle)
deck_y = .04
deck_z = 1.00

def deck_point(x, t, lift=0.0):
    return (x,
            deck_y + t * math.cos(a) - lift * math.sin(a),
            deck_z + t * math.sin(a) + lift * math.cos(a))

def deck_box(size, center, color):
    item = box(size=size, center=center, color=color)
    item.turn(axis="+x", degrees=slope_angle)
    return item

console.include("Sloping control surface",
    deck_box((6.15, 1.38, .10), (-1.0, deck_y, deck_z), light_panel))
for i in range(8):
    x = -3.96 + i * .84
    console.include("Control panel seam %02d" % i,
        deck_box((.018, 1.28, .014), deck_point(x, 0, .057), dark))

for col in range(20):
    x = -3.88 + col * .30
    for row in range(5):
        t = -.53 + row * .255
        key = "%02d_%02d" % (col, row)
        if row == 4 and col % 3 == 0:
            console.include("Deck meter frame " + key,
                deck_box((.18, .17, .016), deck_point(x, t, .065), dark))
            console.include("Deck meter face " + key,
                deck_box((.135, .125, .012), deck_point(x, t, .077), meter_face))
        else:
            console.include("Control knob " + key,
                ball(radius=.026 if row > 1 else .033,
                     center=deck_point(x, t, .083),
                     color=red if (col * 3 + row) % 19 == 0 else black))
    if col % 2 == 0:
        console.include("Switch plate %02d" % col,
            deck_box((.10, .12, .012), deck_point(x, -.04, .063), panel))
scene.include("Main console", console)

# Yellow mimic board. Placement on the wall is an inference from the
# separate reference photograph, not a measured room location.
grid = Asset("GRID single line mimic panel")
gx, gy, gz = -3.95, 3.69, 2.75
grid.include("Yellow enamel board",
    box(size=(1.30, .07, 1.70), center=(gx, gy, gz), color=yellow))
front = gy - .047

def grid_line(name, x1, z1, x2, z2, width=.025):
    grid.include(name, rod(radius=width / 2,
        start=(gx + x1, front, gz + z1),
        end=(gx + x2, front, gz + z2), color=black))

grid_line("Vertical main bus", .18, -.74, .18, .74, .034)
grid_line("Upper bus", -.16, .38, .43, .38)
grid_line("Lower bus", -.16, -.30, .43, -.30)
grid_line("Left branch", -.16, -.30, -.16, .38)
grid_line("Upper right branch", .43, .38, .43, .12)
grid_line("Lower right branch", .43, -.30, .43, -.58)
grid_line("Upper cross connection", -.03, .12, .43, .12)
grid_line("Lower cross connection", -.03, -.58, .43, -.58)

for i, z in enumerate((.58, .27, -.05, -.38, -.66)):
    grid.include("Selector dial %d" % i,
        box(size=(.15, .018, .15), center=(gx - .43, front - .012, gz + z),
            color=meter_face))
    grid.include("Selector knob %d" % i,
        ball(radius=.040, center=(gx - .43, front - .04, gz + z), color=black))
for i, (x, z) in enumerate(((.00, .38), (.18, .38), (.36, .38),
                             (.00, -.30), (.18, -.30), (.36, -.30))):
    grid.include("Lamp housing %d" % i,
        box(size=(.10, .022, .12), center=(gx+x, front-.018, gz+z), color=black))
    grid.include("Amber lamp %d" % i,
        box(size=(.066, .018, .082), center=(gx+x, front-.038, gz+z), color=amber))
for i, z in enumerate((.68, -.68)):
    grid.include("Red lamp housing %d" % i,
        box(size=(.105, .022, .115), center=(gx+.18, front-.018, gz+z), color=black))
    grid.include("Red lamp %d" % i,
        ball(radius=.042, center=(gx+.18, front-.045, gz+z), color=red))
scene.include("GRID mimic board", grid)

# Small independent desk and dark wall opening.
secondary = Asset("Right hand console and opening")
secondary.include("Opening surround",
    box(size=(.05, 1.10, 1.85), center=(5.83, 2.55, 1.58), color=light_panel))
secondary.include("Opening interior",
    box(size=(.025, .79, 1.58), center=(5.79, 2.55, 1.52), color=dark))
secondary.include("Opening lower panel",
    box(size=(.02, .73, .64), center=(5.77, 2.55, 1.01), color=panel))
secondary.include("Small console cabinet",
    box(size=(1.48, .78, .73), center=(4.30, 2.10, .365), color=dark))
secondary.include("Small console deck",
    box(size=(1.56, .86, .10), center=(4.30, 2.10, .77), color=light_panel))
secondary.include("Small raised back",
    box(size=(1.56, .14, .40), center=(4.30, 2.46, .98), color=panel))
for i in range(7):
    for j in range(2):
        secondary.include("Small control %d %d" % (i, j),
            ball(radius=.033, center=(3.77+i*.17, 1.88+j*.23, .84),
                 color=red if (i+j) % 7 == 0 else black))
scene.include("Secondary console", secondary)

fixtures = Asset("Fluorescent ceiling fixtures")
for x in (-2.8, 1.3):
    for y in (-.5, 2.4):
        fixtures.include("Troffer %.1f %.1f" % (x, y),
            box(size=(1.65, .40, .035), center=(x, y, 3.67), color=meter_face))
scene.include("Ceiling fixtures", fixtures)

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
background.inputs["Color"].default_value = (.72, .70, .66, 1)
background.inputs["Strength"].default_value = .42

area_emitter((-2.5, .0, 3.50), power=650, size=4,
             target=(-2, 1.5, .5), color=(1.0, .95, .88))
area_emitter((2.2, .5, 3.50), power=650, size=4,
             target=(2, 2, .5), color=(1.0, .96, .90))
area_emitter((-1, -3.0, 3.1), power=300, size=4,
             target=(-1, 2, 1.2), color=(1.0, .97, .92))

# Assign a modest emissive component to the existing red and amber finishes.
for mat in bpy.data.materials:
    if not mat.use_nodes or not mat.node_tree:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    col = bsdf.inputs["Base Color"].default_value
    if col[0] > .55 and col[1] < .52 and col[2] < .10:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (col[0], col[1], col[2], 1)
            bsdf.inputs["Emission Strength"].default_value = .35

def label(body, location, size=.045):
    curve = bpy.data.curves.new("Label " + body, "FONT")
    curve.body = body
    curve.size = size
    obj = bpy.data.objects.new("GRID label " + body, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    mat = bpy.data.materials.get("Label ink")
    if mat is None:
        mat = bpy.data.materials.new("Label ink")
        mat.diffuse_color = (.02, .02, .02, 1)
    curve.materials.append(mat)

label("FEHLERSTELLE", (gx+.23, front-.05, gz+.66), .043)
label("SCHALTER", (gx-.60, front-.05, gz-.79), .043)

# Overview camera is inside the room, looking toward the rear-right corner.
set_view((-5.9, -7.0, 3.05), (-.35, 2.0, 1.30), lens=27)
overview = sc.camera
overview.name = "Camera - room overview"

bpy.ops.object.camera_add(location=(-5.05, -3.0, 2.45))
detail = bpy.context.object
detail.name = "Camera - console and GRID detail"
direction = Vector((-2.65, 2.15, 1.85)) - detail.location
detail.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
detail.data.lens = 32
sc.camera = overview

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass
sc.render.image_settings.file_format = "PNG"
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
