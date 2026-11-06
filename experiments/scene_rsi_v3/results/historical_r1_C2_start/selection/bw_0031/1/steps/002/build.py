from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, with approximate normalized image bounds:
# - The lower photograph occupies x=.03-.95, y=.65-1.00. It shows a
#   rectangular control room with a pale back wall and darker floor.
# - The main wall cabinet occupies approximately x=.03-.65, y=.69-.86:
#   rows of pale square instruments in dark frames, with a central grille
#   and a smaller instrument bank to its right.
# - The long console occupies approximately x=.03-.68, y=.78-1.00:
#   a sloping control face, dense controls, a horizontal writing ledge,
#   and a dark supporting base. The foreground partly obscures its base.
# - A separate smaller console is visible at x=.76-.94, y=.76-.90.
# - The yellow GRID diagram occupies the separate upper inset at
#   x=.03-.52, y=.19-.64. Its physical location in the room is uncertain.
#   It is represented here on the right wall, with its visible parts editable.
# - The photograph does not establish the ceiling, camera-side wall, or
#   precise room dimensions; those areas are inferred.
#
# Estimated expanded SceneAct primitive count:
# architecture 6; wall cabinet and instruments 135; long console 90;
# small console 24; GRID panel 45; ceiling fixtures 3; total about 303.
# Each box and rod is one primitive. Text is added after realization.
# The prior build failed before rendering because the world node collection
# was accessed as world_nodes.nodes. The world initialization below repairs
# that traceback; no visual comparison has yet been possible.

scene = Scene("1970s Grid Dispatch Room")

wall_color = (0.76, 0.75, 0.71)
ceiling_color = (0.82, 0.81, 0.77)
floor_color = (0.37, 0.35, 0.32)
cabinet_color = (0.68, 0.68, 0.63)
face_color = (0.80, 0.79, 0.74)
dark_color = (0.075, 0.075, 0.068)
trim_color = (0.22, 0.22, 0.20)
yellow_color = (0.89, 0.69, 0.12)
red_color = (0.74, 0.025, 0.018)
amber_color = (1.0, 0.48, 0.025)
black_color = (0.035, 0.035, 0.03)

def add(asset, name, node):
    asset.include(name, node)

architecture = Asset("Architecture")
add(architecture, "Floor",
    box(size=(9.0, 6.4, 0.12), center=(0, 0, -0.06), color=floor_color))
add(architecture, "Back_wall",
    box(size=(9.0, 0.12, 3.6), center=(0, 3.2, 1.8), color=wall_color))
add(architecture, "Right_wall",
    box(size=(0.12, 6.4, 3.6), center=(4.5, 0, 1.8), color=wall_color))
add(architecture, "Ceiling",
    box(size=(9.0, 6.4, 0.10), center=(0, 0, 3.65), color=ceiling_color))
add(architecture, "Back_baseboard",
    box(size=(9.0, .05, .12), center=(0, 3.1, .06), color=trim_color))
add(architecture, "Right_baseboard",
    box(size=(.05, 6.4, .12), center=(4.41, 0, .06), color=trim_color))
scene.include("Architecture", architecture)

cabinet = Asset("Main_wall_instrument_cabinet")
add(cabinet, "Cabinet_body",
    box(size=(5.9, .20, 2.75), center=(-1.36, 3.03, 1.48), color=cabinet_color))
for i, x in enumerate((-4.28, -2.98, -1.68, -.38, .22, 1.54)):
    add(cabinet, "Vertical_joint_%02d" % i,
        box(size=(.018, .018, 2.72), center=(x, 2.916, 1.48), color=trim_color))
for i, z in enumerate((.18, 2.75)):
    add(cabinet, "Horizontal_joint_%02d" % i,
        box(size=(5.88, .018, .018), center=(-1.36, 2.916, z), color=trim_color))

for col in range(7):
    for row in range(4):
        x = -4.04 + col * .39
        z = .88 + row * .37
        label = "Meter_%02d_%02d" % (col, row)
        add(cabinet, label + "_frame",
            box(size=(.29, .035, .29), center=(x, 2.895, z), color=dark_color))
        add(cabinet, label + "_face",
            box(size=(.235, .018, .235), center=(x, 2.869, z), color=face_color))
        add(cabinet, label + "_needle",
            rod(.007, start=(x, 2.853, z-.045),
                end=(x+.055, 2.853, z+.055), color=dark_color))

add(cabinet, "Vent_frame",
    box(size=(1.17, .04, .65), center=(-.77, 2.89, 1.53), color=trim_color))
add(cabinet, "Vent_recess",
    box(size=(1.08, .018, .56), center=(-.77, 2.86, 1.53), color=dark_color))
for i in range(7):
    add(cabinet, "Vent_louver_%02d" % i,
        box(size=(1.04, .025, .025), center=(-.77, 2.842, 1.30+i*.075),
            color=cabinet_color))

for col in range(4):
    for row in range(4):
        x = .01 + col*.28
        z = .93 + row*.35
        label = "Right_meter_%02d_%02d" % (col, row)
        add(cabinet, label + "_frame",
            box(size=(.205, .035, .27), center=(x, 2.895, z), color=dark_color))
        add(cabinet, label + "_face",
            box(size=(.15, .018, .21), center=(x, 2.869, z), color=face_color))
scene.include("Main_wall_instrument_cabinet", cabinet)

console = Asset("Long_sloped_operator_console")
cx, cy = -1.05, .35
length = 5.55
add(console, "Pedestal",
    box(size=(length, 1.0, .72), center=(cx, cy+.04, .36), color=trim_color))
add(console, "Lower_front_panel",
    box(size=(length, .06, .63), center=(cx, cy-.49, .40), color=dark_color))
add(console, "Writing_ledge",
    box(size=(length+.12, .55, .09), center=(cx, cy-.69, .85), color=face_color))

slope_angle = math.radians(22)
slope_center_y = cy + .10
slope_center_z = 1.07
sloping_surface = box(size=(length, 1.10, .10),
                      center=(cx, slope_center_y, slope_center_z),
                      color=face_color)
sloping_surface.turn(axis="x", degrees=22)
add(console, "Sloping_control_surface", sloping_surface)

def slope_point(x, local_y, lift=.07):
    return (x,
            slope_center_y + local_y*math.cos(slope_angle) - lift*math.sin(slope_angle),
            slope_center_z + local_y*math.sin(slope_angle) + lift*math.cos(slope_angle))

normal = (0, -math.sin(slope_angle), math.cos(slope_angle))
for col in range(19):
    x = cx-length/2+.18+col*.285
    for row in range(4):
        p = slope_point(x, -.38+row*.23)
        label = "Control_%02d_%02d" % (col, row)
        if (col+row) % 5 == 0:
            plate = box(size=(.105, .12, .016), center=p, color=dark_color)
            plate.turn(axis="x", degrees=22)
            add(console, label + "_meter", plate)
        else:
            end = (p[0], p[1]+normal[1]*.045, p[2]+normal[2]*.045)
            add(console, label + "_knob",
                rod(.027, start=p, end=end, color=dark_color))
for i in range(7):
    x = cx-length/2+i*length/6
    add(console, "Section_divider_%02d" % i,
        rod(.008, start=slope_point(x, -.51, .06),
            end=slope_point(x, .51, .06), color=trim_color))
scene.include("Long_sloped_operator_console", console)

small = Asset("Small_right_control_console")
add(small, "Pedestal",
    box(size=(1.25, .8, .76), center=(3.56, 1.55, .38), color=trim_color))
add(small, "Writing_edge",
    box(size=(1.35, .36, .08), center=(3.56, 1.06, .82), color=face_color))
small_top = box(size=(1.30, .74, .09), center=(3.56, 1.57, .98), color=face_color)
small_top.turn(axis="x", degrees=20)
add(small, "Sloped_face", small_top)
for i in range(7):
    for j in range(3):
        x = 3.04+i*.17
        ly = -.25+j*.24
        y = 1.57+ly*math.cos(math.radians(20))-.06*math.sin(math.radians(20))
        z = .98+ly*math.sin(math.radians(20))+.06*math.cos(math.radians(20))
        add(small, "Switch_%02d_%02d" % (i, j),
            rod(.025, start=(x, y, z), end=(x, y-.012, z+.035), color=dark_color))
scene.include("Small_right_control_console", small)

grid = Asset("GRID_single_line_mimic_panel")
board_x, board_y, board_z = 4.39, -.65, 1.98
front_x = 4.337
add(grid, "Yellow_backplate",
    box(size=(.08, 1.38, 1.78), center=(board_x, board_y, board_z),
        color=yellow_color))

def grid_bar(name, y1, z1, y2, z2, thickness=.018):
    add(grid, name, rod(thickness/2, start=(front_x, y1, z1),
                        end=(front_x, y2, z2), color=black_color))

grid_bar("Main_bus", board_y+.27, board_z-.70, board_y+.27, board_z+.72, .025)
for k, dz in enumerate((-.52, -.18, .17, .50)):
    z = board_z+dz
    grid_bar("Branch_%d" % k, board_y+.27, z, board_y-.18, z, .023)
    grid_bar("Branch_return_%d" % k, board_y-.18, z, board_y-.18, z+.17, .023)
for k, dz in enumerate((-.36, .02, .39)):
    z = board_z+dz
    for side in (-1, 1):
        y = board_y+.27+side*.17
        grid_bar("Bridge_%d_%d" % (k, side), y, z, y, z+.17, .018)
        add(grid, "Amber_indicator_%d_%d" % (k, side),
            box(size=(.035, .075, .075), center=(front_x-.018, y, z+.085),
                color=amber_color))
for k, dz in enumerate((-.72, .69)):
    add(grid, "Red_bus_lamp_%d" % k,
        rod(.045, start=(front_x, board_y+.27, board_z+dz),
            end=(front_x-.035, board_y+.27, board_z+dz), color=red_color))
for k in range(5):
    z = board_z+.62-k*.29
    y = board_y-.48
    add(grid, "Selector_plate_%d" % k,
        box(size=(.025, .15, .15), center=(front_x-.005, y, z), color=face_color))
    add(grid, "Selector_knob_%d" % k,
        rod(.033, start=(front_x-.02, y, z), end=(front_x-.06, y, z),
            color=black_color))
    add(grid, "Red_lamp_%d" % k,
        rod(.038, start=(front_x-.02, y+.18, z),
            end=(front_x-.055, y+.18, z), color=red_color))
for k, dz in enumerate((-.57, -.18, .23, .58)):
    add(grid, "Amber_square_%d" % k,
        box(size=(.035, .075, .075),
            center=(front_x-.02, board_y+.52, board_z+dz), color=amber_color))
scene.include("GRID_single_line_mimic_panel", grid)

fixtures = Asset("Ceiling_fluorescent_fixtures")
for i, x in enumerate((-2.7, .4, 3.2)):
    add(fixtures, "Troffer_%d" % i,
        box(size=(1.55, .35, .045), center=(x, .75, 3.57), color=face_color))
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
background.inputs["Color"].default_value = (.63, .61, .56, 1)
background.inputs["Strength"].default_value = .45

def make_emission(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = strength
    return mat

red_emission = make_emission("Red indicator emission", (.74, .025, .018), 1.4)
amber_emission = make_emission("Amber indicator emission", (1.0, .48, .025), 1.2)
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    name = obj.name.lower()
    material = None
    if "red_lamp" in name or "red_bus_lamp" in name:
        material = red_emission
    elif "amber_indicator" in name or "amber_square" in name:
        material = amber_emission
    if material is not None:
        obj.data.materials.clear()
        obj.data.materials.append(material)

ink = bpy.data.materials.new("Mimic label ink")
ink.diffuse_color = (.015, .015, .012, 1)

def board_text(name, text, y, z, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (front_x-.045, y, z)
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    obj.data.materials.append(ink)

board_text("GRID_title", "GRID", board_y-.58, board_z+.77, .085)
board_text("Fehler_label", "FEHLER-STELLE K", board_y+.02, board_z+.61, .045)
board_text("Netz_label", "NETZ", board_y-.60, board_z-.79, .05)

area_emitter((-2.8, .5, 3.35), power=700, size=3.0, target=(-1, 1, 0))
area_emitter((1.0, 1.2, 3.35), power=650, size=3.0, target=(0, 1, 0))
area_emitter((3.4, -.5, 3.3), power=450, size=2.5, target=(2, 1, 1))
area_emitter((-3.0, -4.0, 3.0), power=350, size=4.0, target=(0, 1, 1))

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
