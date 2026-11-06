from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, estimated from the lower photograph:
# - Pale instrument wall: x=.03-.65, y=.65-.87; regular square meter banks,
#   central horizontal vent, cabinet seams. Its left side is cropped.
# - Long desk: x=.03-.68, y=.78-1.00; inclined control surface, horizontal
#   writing ledge, closely spaced controls and dark pedestal. Its near end is
#   cropped and its lower portion is partly obscured by the image boundary.
# - Right wall and doorway: x=.64-.78, y=.66-.88; small dark doorway.
# - Small independent desk: x=.76-.94, y=.74-.90.
# - Yellow GRID panel is a separate inset in the source image. Its physical
#   position in the room is uncertain; an editable panel is placed on the
#   right wall so that it remains visible from the second camera.
# - Ceiling and unseen sides are uncertain. The room is open at the camera side.
#
# Render review: the previous overview left extensive empty space above the room,
# showed exposed outer floor edges, and made the desks too small. This revision
# moves the camera inside the room, fills the frame with the instrument wall and
# console, adds the visible doorway, and darkens the floor and pedestal. The
# inset's yellow panel is retained, though its location in the room is unknown.
#
# Estimated expanded primitives: architecture 8, wall cabinet 120, main
# console 116, small desk 25, GRID panel 53, ceiling fixtures 3: about 325.
# Each box and rod below contributes one primitive; text objects are separate.

scene = Scene("1970s Grid Dispatch Room")
wall = (.68, .67, .63)
ceiling = (.76, .75, .71)
floor = (.29, .27, .24)
cabinet_color = (.65, .64, .60)
face = (.75, .74, .69)
dark = (.07, .065, .058)
trim = (.18, .17, .15)
yellow = (.84, .61, .10)
red = (.72, .018, .012)
amber = (1.0, .42, .018)
black = (.025, .023, .020)

def add(asset, name, node):
    asset.include(name, node)

architecture = Asset("Architecture")
add(architecture, "Floor", box(size=(10, 8, .12), center=(0, 0, -.06), color=floor))
add(architecture, "Back_wall", box(size=(10, .12, 3.5), center=(0, 3.2, 1.75), color=wall))
add(architecture, "Right_wall", box(size=(.12, 8, 3.5), center=(5, -.8, 1.75), color=wall))
add(architecture, "Ceiling", box(size=(10, 8, .1), center=(0, -.8, 3.55), color=ceiling))
add(architecture, "Back_baseboard", box(size=(10, .04, .10), center=(0, 3.12, .05), color=trim))
add(architecture, "Right_baseboard", box(size=(.04, 8, .10), center=(4.92, -.8, .05), color=trim))
# A dark doorway and its light surround, seen against the far wall.
add(architecture, "Door_frame", box(size=(.70, .04, 2.30), center=(2.25, 3.105, 1.15), color=face))
add(architecture, "Door_opening", box(size=(.49, .025, 2.05), center=(2.25, 3.075, 1.07), color=trim))
scene.include("Architecture", architecture)

cab = Asset("Main_wall_instrument_cabinet")
add(cab, "Body", box(size=(6.4, .18, 2.92), center=(-1.65, 3.02, 1.48), color=cabinet_color))
for i, x in enumerate((-4.82, -3.65, -2.48, -1.31, -.14, 1.48)):
    add(cab, "Cabinet_seam_%02d" % i,
        box(size=(.014, .012, 2.86), center=(x, 2.921, 1.48), color=trim))
for i, z in enumerate((.12, 2.90)):
    add(cab, "Cabinet_horizontal_seam_%d" % i,
        box(size=(6.35, .012, .014), center=(-1.65, 2.92, z), color=trim))

# Meter arrays: separate dark frames, pale faces and simple pointers.
for col in range(7):
    for row in range(4):
        x, z = -4.62 + col*.41, .72 + row*.39
        n = "Meter_%02d_%02d" % (col, row)
        add(cab, n+"_frame", box(size=(.31,.035,.31), center=(x,2.895,z), color=dark))
        add(cab, n+"_face", box(size=(.25,.016,.25), center=(x,2.868,z), color=face))
        add(cab, n+"_pointer", rod(.006, start=(x,2.855,z-.045),
                                   end=(x+.05,2.855,z+.045), color=dark))
add(cab, "Vent_frame", box(size=(1.12,.035,.63), center=(-.95,2.895,1.49), color=trim))
add(cab, "Vent_dark_recess", box(size=(1.03,.018,.54), center=(-.95,2.865,1.49), color=dark))
for i in range(7):
    add(cab, "Vent_louver_%d" % i,
        box(size=(1.0,.015,.025), center=(-.95,2.849,1.27+i*.073), color=face))
for col in range(4):
    for row in range(4):
        x, z = -.22 + col*.27, .78 + row*.36
        n = "Right_meter_%02d_%02d" % (col,row)
        add(cab, n+"_frame", box(size=(.21,.035,.28), center=(x,2.895,z), color=dark))
        add(cab, n+"_face", box(size=(.16,.016,.22), center=(x,2.868,z), color=face))
scene.include("Main_wall_instrument_cabinet", cab)

console = Asset("Long_sloped_operator_console")
cx, cy, length = -1.40, .55, 5.75
add(console, "Pedestal", box(size=(length,1.03,.70), center=(cx,cy+.12,.35), color=trim))
add(console, "Dark_front", box(size=(length,.035,.61), center=(cx,cy-.41,.38), color=dark))
add(console, "Writing_ledge", box(size=(length+.12,.48,.085),
                                  center=(cx,cy-.62,.80), color=face))
angle = math.radians(21)
sy, sz = cy+.10, 1.01
surface = box(size=(length,1.15,.10), center=(cx,sy,sz), color=face)
surface.turn(axis="x", degrees=21)
add(console, "Sloping_control_surface", surface)

def desk_point(x, local_y, lift=.065):
    return (x, sy+local_y*math.cos(angle)-lift*math.sin(angle),
            sz+local_y*math.sin(angle)+lift*math.cos(angle))

for col in range(20):
    x = cx-length/2+.16+col*.285
    for row in range(5):
        p = desk_point(x, -.43+row*.21)
        name = "Control_%02d_%02d" % (col,row)
        if (col+row) % 6 == 0:
            plate = box(size=(.10,.10,.015), center=p, color=trim)
            plate.turn(axis="x", degrees=21)
            add(console, name+"_meter", plate)
        else:
            add(console, name+"_knob",
                rod(.022, start=p, end=(p[0],p[1]-.013,p[2]+.034), color=dark))
for i in range(7):
    x = cx-length/2+i*length/6
    add(console, "Section_divider_%d" % i,
        rod(.006, start=desk_point(x,-.54,.058),
            end=desk_point(x,.54,.058), color=trim))
scene.include("Long_sloped_operator_console", console)

small = Asset("Small_right_control_console")
add(small, "Pedestal", box(size=(1.32,.76,.72), center=(3.55,2.05,.36), color=trim))
add(small, "Writing_edge", box(size=(1.40,.35,.08), center=(3.55,1.60,.78), color=face))
top = box(size=(1.35,.72,.09), center=(3.55,2.06,.93), color=face)
top.turn(axis="x", degrees=20)
add(small, "Sloping_face", top)
for i in range(7):
    for j in range(3):
        x, ly = 3.04+i*.17, -.24+j*.23
        y = 2.06+ly*math.cos(math.radians(20))-.055*math.sin(math.radians(20))
        z = .93+ly*math.sin(math.radians(20))+.055*math.cos(math.radians(20))
        add(small, "Switch_%02d_%02d" % (i,j),
            rod(.022, start=(x,y,z), end=(x,y-.012,z+.033), color=dark))
scene.include("Small_right_control_console", small)

grid = Asset("GRID_single_line_mimic_panel")
bx, by, bz = 4.91, .0, 2.05
front = 4.85
add(grid, "Yellow_backplate", box(size=(.07,1.45,1.82), center=(bx,by,bz), color=yellow))

def grid_bar(name, y1, z1, y2, z2, width=.021):
    add(grid, name, rod(width/2, start=(front,y1,z1), end=(front,y2,z2), color=black))

grid_bar("Main_bus", by+.22,bz-.79,by+.22,bz+.79,.026)
for k, dz in enumerate((-.53,-.18,.18,.52)):
    grid_bar("Branch_%d" % k, by+.22,bz+dz,by-.16,bz+dz)
    grid_bar("Return_%d" % k, by-.16,bz+dz,by-.16,bz+dz+.16)
for k, dz in enumerate((-.40,-.03,.34)):
    for side in (-1,1):
        y = by+.22+side*.16
        grid_bar("Bridge_%d_%d" % (k,side), y,bz+dz,y,bz+dz+.18)
        add(grid, "Amber_indicator_%d_%d" % (k,side),
            box(size=(.035,.075,.075), center=(front-.02,y,bz+dz+.09), color=amber))
for i, dz in enumerate((-.72,.70)):
    add(grid, "Red_bus_lamp_%d" % i,
        rod(.042, start=(front,by+.22,bz+dz), end=(front-.035,by+.22,bz+dz), color=red))
for i in range(5):
    y, z = by-.49, bz+.61-i*.29
    add(grid, "Selector_dial_%d" % i,
        box(size=(.025,.16,.16), center=(front-.006,y,z), color=face))
    add(grid, "Selector_knob_%d" % i,
        rod(.031, start=(front-.02,y,z), end=(front-.06,y,z), color=black))
    add(grid, "Red_indicator_%d" % i,
        rod(.038, start=(front-.02,y+.18,z), end=(front-.06,y+.18,z), color=red))
for i, dz in enumerate((-.55,-.18,.20,.57)):
    add(grid, "Amber_square_%d" % i,
        box(size=(.035,.075,.075), center=(front-.02,by+.53,bz+dz), color=amber))
scene.include("GRID_single_line_mimic_panel", grid)

fixtures = Asset("Ceiling_fluorescent_fixtures")
for i, x in enumerate((-3,0,3)):
    add(fixtures, "Fluorescent_panel_%d" % i,
        box(size=(1.5,.34,.035), center=(x,1.0,3.48), color=face))
scene.include("Ceiling_fluorescent_fixtures", fixtures)

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
background.inputs["Color"].default_value = (.56,.54,.50,1)
background.inputs["Strength"].default_value = .30

# Add German labels to the editable panel.
ink = bpy.data.materials.new("German label ink")
ink.diffuse_color = (.012,.012,.010,1)
def board_text(name, body, y, z, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (front-.045,y,z)
    obj.rotation_euler = (math.pi/2,0,math.pi/2)
    curve.materials.append(ink)
board_text("Grid_label", "GRID", by-.60, bz+.76, .07)
board_text("Fault_location_label", "FEHLER-STELLE K", by+.02, bz+.65, .038)
board_text("Network_label", "NETZ", by-.60, bz-.80, .045)

area_emitter((-2.5,.7,3.35), power=400, size=3, target=(-1,1,0))
area_emitter((1,.9,3.35), power=400, size=3, target=(0,1,0))
area_emitter((3.5,1.0,3.35), power=300, size=2.5, target=(2,1,1))
area_emitter((-3,-3,3), power=180, size=4, target=(-1,1,1))

# The overview is positioned inside the open side so the floor and walls
# continue beyond the image edges, as in the photograph.
set_view((-5.4,-5.2,2.75), (-.25,1.9,1.40), lens=38, sensor=36)
overview = sc.camera
overview.name = "Camera_Overview"
bpy.ops.object.camera_add(location=(1.35,-2.8,2.30))
closeup = bpy.context.object
closeup.name = "Camera_Console_and_GRID_Closeup"
closeup.rotation_euler = (Vector((3.2,.35,1.55))-closeup.location).to_track_quat("-Z","Y").to_euler()
closeup.data.lens = 32
sc.camera = overview

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
