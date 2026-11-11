# Reference inventory, normalized to the supplied composite image:
# - Lower photograph (roughly x=.03-.94, y=.65-1): rectangular control room,
#   viewed from above and to the left. Back wall carries rows of square instruments
#   at left, a central ventilation grille, and narrow instrument columns at right.
# - Long central console: x=.03-.70, y=.75-.99 in the lower photograph;
#   horizontal writing ledge, sloping control surface, dark supporting cabinet,
#   and dense rows of switches and indicators.
# - Small independent console at the back right: x=.75-.94, y=.72-.88.
# - Tall dark doorway or equipment opening on the right wall, behind the small desk.
# - Yellow GRID panel shown separately in the upper image: yellow rectangular face,
#   black single-line network, amber square indicators, red round lamps, switches,
#   and small German labels. Its position in the room is uncertain; it is mounted
#   on the right wall as an identifiable training exhibit.
# - Room boundaries outside the photograph and the console's hidden rear are uncertain.
# Estimated expansion: room and furniture ~25 meshes; wall instruments ~70;
#   console panels and controls ~160; GRID panel and its controls ~55;
#   total approximately 310 SceneAct primitives plus text and ceiling lights.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s Grid Control Room")

wall = (0.72, 0.71, 0.67)
wall_light = (0.84, 0.83, 0.78)
floor_col = (0.33, 0.31, 0.28)
metal = (0.65, 0.65, 0.61)
ivory = (0.81, 0.80, 0.73)
dark = (0.12, 0.13, 0.13)
black = (0.035, 0.038, 0.035)
yellow = (0.93, 0.69, 0.12)
red = (0.70, 0.035, 0.025)
amber = (0.95, 0.45, 0.035)

def add(asset, name, node):
    asset.include(name, node)

# Room: front and left sides remain open to the camera.
room = Asset("Room architecture")
add(room, "floor", box((9.0, 7.0, .12), center=(0, 0, -.06), color=floor_col))
add(room, "back wall", box((9.0, .14, 3.5), center=(0, 3.5, 1.75), color=wall_light))
add(room, "right wall", box((.14, 7.0, 3.5), center=(4.5, 0, 1.75), color=wall))
add(room, "ceiling", box((9.0, 7.0, .10), center=(0, 0, 3.55), color=wall_light))
add(room, "back skirting", box((9.0, .06, .12), center=(0, 3.40, .06), color=metal))
scene.include("Room architecture", room)

# Continuous cabinet wall with instrument arrays and grille.
cabinets = Asset("Main wall instrument cabinets")
add(cabinets, "cabinet body", box((6.0, .22, 2.15), center=(-1.35, 3.31, 1.38), color=metal))
for x in (-4.32, -3.0, -1.68, -.36, 1.02, 1.62):
    add(cabinets, "cabinet seam %.2f" % x,
        box((.018, .015, 2.05), center=(x, 3.185, 1.40), color=dark))

# Dark frames and pale square faces are deliberately separate editable parts.
for col in range(5):
    for row in range(4):
        x = -4.08 + col * .46
        z = .72 + row * .40
        add(cabinets, "meter frame %d %d" % (col, row),
            box((.31, .025, .30), center=(x, 3.17, z), color=dark))
        add(cabinets, "meter face %d %d" % (col, row),
            box((.245, .012, .23), center=(x, 3.15, z), color=ivory))
        add(cabinets, "meter needle %d %d" % (col, row),
            box((.018, .008, .12), center=(x, 3.14, z), color=dark))
for col in range(3):
    for row in range(5):
        x = .25 + col * .30
        z = .69 + row * .32
        add(cabinets, "narrow frame %d %d" % (col, row),
            box((.21, .025, .23), center=(x, 3.17, z), color=dark))
        add(cabinets, "narrow face %d %d" % (col, row),
            box((.16, .012, .18), center=(x, 3.15, z), color=ivory))
add(cabinets, "vent recess", box((1.25, .025, .75), center=(-.89, 3.16, 1.59), color=dark))
for j in range(7):
    add(cabinets, "vent slat %d" % j,
        box((1.17, .025, .045), center=(-.89, 3.14, 1.31 + .09*j), color=metal))
scene.include("Main wall instrument cabinets", cabinets)

# Main console: long sloping upper panel and projecting writing ledge.
# The local panel coordinate is rotated about X to face the camera.
console = Asset("Long operating console")
add(console, "dark pedestal", box((5.65, 1.12, .70), center=(-1.20, .42, .35), color=(.25, .24, .22)))
add(console, "writing ledge", box((5.95, .48, .09), center=(-1.20, -.32, .83), color=ivory))
panel_angle = math.radians(18)
panel_center = Vector((-1.20, .53, 1.08))
panel = box((5.95, 1.38, .09), center=tuple(panel_center), color=ivory)
panel.turn(axis="+x", degrees=18, pivot=tuple(panel_center))
add(console, "sloping control surface", panel)

def panel_pos(x, local_y, height=.065):
    return (x,
            panel_center.y + local_y*math.cos(panel_angle) - height*math.sin(panel_angle),
            panel_center.z + local_y*math.sin(panel_angle) + height*math.cos(panel_angle))

# Panel division lines and raised controls, spaced to retain the gaps seen in the photo.
for i in range(7):
    x = -4.05 + i*.91
    strip = box((.018, 1.28, .012), center=panel_pos(x, 0, .055), color=dark)
    strip.turn(axis="+x", degrees=18, pivot=panel_pos(x, 0, .055))
    add(console, "panel seam %d" % i, strip)
for col in range(18):
    x = -3.94 + col*.32
    for row in range(4):
        ly = -.49 + row*.29
        p = panel_pos(x, ly, .07)
        # Small raised switch blocks produce the dense, legible control field.
        control = box((.075, .075, .045), center=p,
                      color=dark if (col+row)%3 else metal)
        control.turn(axis="+x", degrees=18, pivot=p)
        add(console, "switch %02d %d" % (col, row), control)
for col in range(9):
    x = -3.75 + col*.62
    p = panel_pos(x, .48, .07)
    face = box((.20, .16, .025), center=p, color=dark)
    face.turn(axis="+x", degrees=18, pivot=p)
    add(console, "upper indicator %d" % col, face)
scene.include("Long operating console", console)

# Small console at back right, with its own sloping top.
small = Asset("Right independent console")
add(small, "pedestal", box((1.65, .85, .75), center=(3.12, 2.20, .375), color=(.35,.34,.31)))
top_center = (3.12, 2.15, .85)
top = box((1.75, .95, .10), center=top_center, color=ivory)
top.turn(axis="+x", degrees=13, pivot=top_center)
add(small, "sloped top", top)
for i in range(7):
    for j in range(3):
        x = 2.43 + i*.22
        y = 1.88 + j*.22
        z = .92 + (y-2.15)*math.sin(math.radians(13))
        add(small, "control %d %d" % (i,j),
            box((.07,.07,.04), center=(x,y,z), color=dark))
scene.include("Right independent console", small)

# Door-like dark opening on the back wall.
door = Asset("Back wall doorway")
add(door, "dark opening", box((.75, .045, 2.25), center=(2.40, 3.39, 1.14), color=(.20,.20,.19)))
add(door, "door inner panel", box((.53, .025, 1.88), center=(2.40, 3.35, 1.16), color=(.39,.38,.34)))
scene.include("Back wall doorway", door)

# Yellow GRID single-line display, mounted on the right wall.
grid = Asset("Yellow GRID mimic panel")
add(grid, "yellow plate", box((.08, 1.70, 2.12), center=(4.39, .58, 1.84), color=yellow))
# Coordinates on the right wall use y horizontally and z vertically.
def gridbar(name, y, z, sy, sz, col=black, x=4.335):
    add(grid, name, box((.018, sy, sz), center=(x,y,z), color=col))
gridbar("vertical bus", .48, 1.85, .035, 1.83)
for z in (1.18, 1.56, 2.12, 2.49):
    gridbar("horizontal bus %.2f" % z, .48, z, .74, .035)
for y in (.18, .48, .78):
    for z in (1.56, 2.12):
        gridbar("amber frame %.2f %.2f" % (y,z), y,z,.19,.21,black,4.315)
        gridbar("amber lamp %.2f %.2f" % (y,z), y,z,.115,.14,amber,4.30)
for y,z in ((.48,1.00),(.48,2.72),(.98,2.42),(.98,1.27)):
    add(grid, "red lamp %.2f %.2f" % (y,z),
        rod(.075, start=(4.32,y,z), end=(4.28,y,z), color=red))
for i in range(4):
    y = -.03
    z = 1.15 + .42*i
    gridbar("switch plate %d" % i,y,z,.25,.25,ivory,4.32)
    add(grid, "black selector %d" % i,
        rod(.052, start=(4.30,y,z), end=(4.25,y,z), color=dark))
scene.include("Yellow GRID mimic panel", grid)

# Ceiling troffers.
lights = Asset("Ceiling fluorescent fixtures")
for x in (-2.5, 0.0, 2.5):
    for y in (-1.0, 1.6):
        add(lights, "troffer %.1f %.1f" % (x,y),
            box((1.55,.42,.035), center=(x,y,3.47), color=(.95,.94,.85)))
scene.include("Ceiling fluorescent fixtures", lights)

realize(scene)

# SceneAct establishes geometry; Blender customizes the presentation and cameras.
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
background.inputs["Color"].default_value = (0.68, 0.66, 0.61, 1)
background.inputs["Strength"].default_value = .6

# Main view approximates the elevated angle in the historical room photograph.
set_view((-7.8, -10.5, 5.5), (-.05, 1.45, 1.25), lens=35)
sc.camera.name = "Camera - room overview"
area_emitter((-3, -3, 5.3), power=1200, size=7, target=(0,1,0))
area_emitter((2, 1.2, 3.2), power=450, size=3.5, target=(0,1,0))

# Additional editable close-up camera.
bpy.ops.object.camera_add(location=(1.2, -3.7, 2.8))
close_cam = bpy.context.object
close_cam.name = "Camera - console and GRID detail"
direction = Vector((2.2, 1.2, 1.4)) - close_cam.location
close_cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
close_cam.data.lens = 42
sc.camera = bpy.data.objects.get("Camera - room overview")

# German labels on the yellow panel, placed as physical text in front of its surface.
def grid_text(body, y, z, size=.075):
    curve = bpy.data.curves.new("GRID label " + body, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = .001
    obj = bpy.data.objects.new("GRID label " + body, curve)
    sc.collection.objects.link(obj)
    obj.location = (4.275, y, z)
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    mat = bpy.data.materials.get("GRID label ink")
    if mat is None:
        mat = bpy.data.materials.new("GRID label ink")
        mat.diffuse_color = (.025,.025,.02,1)
    curve.materials.append(mat)

grid_text("NETZ", .26, 2.82, .09)
grid_text("FEHLERSTELLE", .25, .83, .065)

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
