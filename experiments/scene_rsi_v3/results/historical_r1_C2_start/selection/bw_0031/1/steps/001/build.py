from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, estimated normalized bounds:
# - Lower photograph: rectangular control room, roughly x=.03-.95, y=.65-1.
#   The back wall carries a uniform array of square instruments, a central
#   ventilation grille, and a narrower instrument bank on its right.
# - Long foreground console: x=.03-.68, y=.79-1; light sloping control face,
#   horizontal writing ledge, dark base, densely distributed controls.
# - Small independent console at the right wall: x=.76-.94, y=.75-.91.
# - Yellow GRID mimic panel: upper inset x=.03-.52, y=.19-.64; black single-line
#   diagram, red round lamps, amber square lamps, selector switches and labels.
#   Its exact location in the photographed room is uncertain, so it is placed on
#   the right wall where it can be inspected in the second camera.
# - The room continues outside the photograph; hidden walls and furniture are
#   uncertain. The ceiling is inferred from conventional room proportions.
#
# Estimated SceneAct mesh count: architecture 6, wall cabinet and instruments
# ~100, console and controls ~190, smaller console ~35, mimic panel ~70,
# ceiling lights 4: approximately 405 primitives. Text objects are created
# separately after realization. No image textures or external assets are used.

scene = Scene("1970s Grid Dispatch Room")

ivory = (0.72, 0.70, 0.64)
wall = (0.76, 0.75, 0.71)
floor_color = (0.38, 0.36, 0.32)
dark = (0.075, 0.075, 0.068)
trim = (0.22, 0.22, 0.20)
face = (0.79, 0.78, 0.72)
panel = (0.68, 0.68, 0.63)
yellow = (0.89, 0.69, 0.12)
red = (0.74, 0.025, 0.018)
amber = (1.0, 0.48, 0.025)
black = (0.035, 0.035, 0.03)

def put(asset, name, node):
    asset.include(name, node)

# The room is open on the camera side, as the corresponding wall is outside
# the photographic field of view.
architecture = Asset("Architecture")
put(architecture, "Floor", box((9.0, 6.4, 0.12), (0, 0, -0.06), floor_color))
put(architecture, "Back_wall", box((9.0, 0.12, 3.6), (0, 3.2, 1.8), wall))
put(architecture, "Right_wall", box((0.12, 6.4, 3.6), (4.5, 0, 1.8), wall))
put(architecture, "Ceiling", box((9.0, 6.4, 0.10), (0, 0, 3.65), ivory))
put(architecture, "Back_baseboard", box((9, .05, .12), (0, 3.1, .06), trim))
put(architecture, "Right_baseboard", box((.05, 6.4, .12), (4.41, 0, .06), trim))
scene.include("Architecture", architecture)

# Main back-wall instrument cabinet.
cabinet = Asset("Main_wall_instrument_cabinet")
put(cabinet, "Cabinet_body", box((5.9, .20, 2.75), (-1.36, 3.03, 1.48), panel))
for x in (-4.28, -2.98, -1.68, -.38, .22, 1.54):
    put(cabinet, "Vertical_joint_%s" % x,
        box((.018, .018, 2.72), (x, 2.916, 1.48), trim))
for z in (.18, 2.75):
    put(cabinet, "Horizontal_joint_%s" % z,
        box((5.88, .018, .018), (-1.36, 2.916, z), trim))

# Square instrument frames and pale faces; all lie in the vertical XZ plane.
for col in range(7):
    x = -4.04 + col * .39
    for row in range(4):
        z = .88 + row * .37
        prefix = "Meter_%02d_%02d" % (col, row)
        put(cabinet, prefix + "_frame", box((.29, .035, .29), (x, 2.895, z), dark))
        put(cabinet, prefix + "_face", box((.235, .018, .235), (x, 2.869, z), face))
        # Single pointer suggests the analogue dial without excessive detail.
        put(cabinet, prefix + "_needle",
            rod(.007, start=(x, 2.853, z-.045),
                end=(x+.055, 2.853, z+.055), color=dark))

# Wide ventilation grille in the center.
put(cabinet, "Vent_frame", box((1.17, .04, .65), (-.77, 2.89, 1.53), trim))
put(cabinet, "Vent_recess", box((1.08, .018, .56), (-.77, 2.86, 1.53), dark))
for i in range(7):
    put(cabinet, "Vent_louver_%02d" % i,
        box((1.04, .025, .025), (-.77, 2.842, 1.30+i*.075), panel))

for col in range(4):
    for row in range(4):
        x = .01 + col*.28
        z = .93 + row*.35
        name = "Right_meter_%02d_%02d" % (col, row)
        put(cabinet, name+"_frame", box((.205, .035, .27), (x, 2.895, z), dark))
        put(cabinet, name+"_face", box((.15, .018, .21), (x, 2.869, z), face))
scene.include("Main_wall_instrument_cabinet", cabinet)

# Console face runs along X; in cross section the rear edge rises toward the wall.
# Controls are positioned in that plane, with their rods normal to it.
console = Asset("Long_sloped_operator_console")
cx, cy = -1.05, .35
length = 5.55
put(console, "Pedestal", box((length, 1.0, .72), (cx, cy+.04, .36), trim))
put(console, "Lower_front_panel", box((length, .06, .63), (cx, cy-.49, .40), dark))
put(console, "Writing_ledge", box((length+.12, .55, .09),
                                 (cx, cy-.69, .85), face))
slope_angle = math.radians(22)
slope_depth = 1.10
slope_center_y = cy+.10
slope_center_z = 1.07
slope = box((length, slope_depth, .10),
            (cx, slope_center_y, slope_center_z), face)
slope.turn(axis="x", degrees=22)
put(console, "Sloping_control_surface", slope)

def slope_point(x, local_y, lift=.07):
    return (x,
            slope_center_y + local_y*math.cos(slope_angle) - lift*math.sin(slope_angle),
            slope_center_z + local_y*math.sin(slope_angle) + lift*math.cos(slope_angle))

normal = (0, -math.sin(slope_angle), math.cos(slope_angle))
for col in range(19):
    x = cx-length/2+.18+col*.285
    for row in range(4):
        ly = -.38+row*.23
        p = slope_point(x, ly)
        if (col + row) % 5 == 0:
            # Small rectangular meter with a contrasting face.
            plate = box((.105, .12, .016), p, dark)
            plate.turn(axis="x", degrees=22)
            put(console, "Control_meter_%02d_%02d" % (col,row), plate)
        else:
            end = (p[0]+normal[0]*.045, p[1]+normal[1]*.045,
                   p[2]+normal[2]*.045)
            put(console, "Control_knob_%02d_%02d" % (col,row),
                rod(.027, start=p, end=end, color=dark))
# Panel divisions support the long sectional appearance of the desk.
for i in range(7):
    x = cx-length/2+i*length/6
    p1 = slope_point(x, -.51, .06)
    p2 = slope_point(x, .51, .06)
    put(console, "Section_divider_%02d" % i, rod(.008, start=p1, end=p2, color=trim))
scene.include("Long_sloped_operator_console", console)

# Separate smaller console against the right wall.
small = Asset("Small_right_control_console")
put(small, "Pedestal", box((1.25, .8, .76), (3.56, 1.55, .38), trim))
put(small, "Writing_edge", box((1.35, .36, .08), (3.56, 1.06, .82), face))
small_top = box((1.30, .74, .09), (3.56, 1.57, .98), face)
small_top.turn(axis="x", degrees=20)
put(small, "Sloped_face", small_top)
for i in range(7):
    for j in range(3):
        x = 3.04+i*.17
        ly = -.25+j*.24
        y = 1.57+ly*math.cos(math.radians(20))-.06*math.sin(math.radians(20))
        z = .98+ly*math.sin(math.radians(20))+.06*math.cos(math.radians(20))
        put(small, "Switch_%02d_%02d" % (i,j),
            rod(.025, start=(x,y,z), end=(x,y-.012,z+.035), color=dark))
scene.include("Small_right_control_console", small)

# Yellow mimic board on the right wall, facing left toward the room.
grid = Asset("GRID_single_line_mimic_panel")
board_x = 4.39
board_y = -.65
board_z = 1.98
put(grid, "Yellow_backplate",
    box((.08, 1.38, 1.78), (board_x, board_y, board_z), yellow))
front_x = 4.337

def grid_bar(name, y1, z1, y2, z2, thickness=.018):
    put(grid, name, rod(thickness/2, start=(front_x,y1,z1),
                        end=(front_x,y2,z2), color=black))

# Main vertical bus and branching single-line network.
grid_bar("Main_bus", board_y+.27, board_z-.70, board_y+.27, board_z+.72, .025)
for k, dz in enumerate((-.52, -.18, .17, .50)):
    z = board_z+dz
    grid_bar("Branch_%d" % k, board_y+.27, z, board_y-.18, z, .023)
    grid_bar("Branch_return_%d" % k, board_y-.18, z, board_y-.18, z+.17, .023)
for k, dz in enumerate((-.36, .02, .39)):
    z = board_z+dz
    for side in (-1, 1):
        y = board_y+.27+side*.17
        grid_bar("Bridge_%d_%d" % (k,side), y, z, y, z+.17, .018)
        put(grid, "Amber_indicator_%d_%d" % (k,side),
            box((.035,.075,.075), (front_x-.018,y,z+.085), amber))
for k, dz in enumerate((-.72, .69)):
    put(grid, "Red_bus_lamp_%d" % k,
        rod(.045, start=(front_x,board_y+.27,board_z+dz),
            end=(front_x-.035,board_y+.27,board_z+dz), color=red))
for k in range(5):
    z = board_z+.62-k*.29
    y = board_y-.48
    put(grid, "Selector_plate_%d" % k,
        box((.025,.15,.15), (front_x-.005,y,z), face))
    put(grid, "Selector_knob_%d" % k,
        rod(.033, start=(front_x-.02,y,z), end=(front_x-.06,y,z), color=black))
    put(grid, "Red_lamp_%d" % k,
        rod(.038, start=(front_x-.02,y+.18,z),
            end=(front_x-.055,y+.18,z), color=red))
for k, dz in enumerate((-.57, -.18, .23, .58)):
    put(grid, "Amber_square_%d" % k,
        box((.035,.075,.075), (front_x-.02,board_y+.52,board_z+dz), amber))
scene.include("GRID_single_line_mimic_panel", grid)

fixtures = Asset("Ceiling_fluorescent_fixtures")
for x in (-2.7, .4, 3.2):
    put(fixtures, "Troffer_%s" % x,
        box((1.55,.35,.045), (x,.75,3.57), face))
scene.include("Ceiling_fluorescent_fixtures", fixtures)

realize(scene)

# Explicit world initialization is required after SceneAct clears the scene.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
world_nodes = sc.world.node_tree.nodes
background = world_nodes.nodes.get("Background")
if background is None:
    background = world_nodes.nodes.new("ShaderNodeBackground")
output = world_nodes.nodes.get("World Output")
if output is None:
    output = world_nodes.nodes.new("ShaderNodeOutputWorld")
world_nodes.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.63, 0.61, 0.56, 1)
background.inputs["Strength"].default_value = .45

# Add editable German labels directly to the mimic panel.
def board_text(name, text, y, z, size=.065):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (front_x-.045, y, z)
    # Local text x points along +Y, local text y points along +Z; normal is +X.
    # Turning it toward the room gives a readable face from the -X side.
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    mat = bpy.data.materials.get("Mimic_label_ink")
    if mat is None:
        mat = bpy.data.materials.new("Mimic_label_ink")
        mat.diffuse_color = (.015,.015,.012,1)
    obj.data.materials.append(mat)
    return obj

board_text("GRID_title", "GRID", board_y-.58, board_z+.77, .085)
board_text("Fehler_label", "FEHLER-STELLE K", board_y+.02, board_z+.61, .045)
board_text("Netz_label", "NETZ", board_y-.60, board_z-.79, .05)

# Warm neutral room illumination.
area_emitter((-2.8, .5, 3.35), power=700, size=3.0, target=(-1,1,0))
area_emitter((1.0, 1.2, 3.35), power=650, size=3.0, target=(0,1,0))
area_emitter((3.4, -.5, 3.3), power=450, size=2.5, target=(2,1,1))
area_emitter((-3.0, -4.0, 3.0), power=350, size=4.0, target=(0,1,1))

# Overview is the active camera. The additional close-up camera remains
# available for an operator to select in Blender.
set_view((-6.6, -7.7, 3.35), (-.15, 1.15, 1.35), lens=32, sensor=36)
overview = sc.camera
overview.name = "Camera_Overview"
bpy.ops.object.camera_add(location=(1.25, -3.7, 2.65))
closeup = bpy.context.object
closeup.name = "Camera_Console_and_GRID_Closeup"
direction = Vector((2.4, .15, 1.48)) - closeup.location
closeup.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
closeup.data.lens = 30
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
