# Reference inventory and visual anchors, estimated from the supplied composite:
# - The room photograph occupies approximately x=.03-.94, y=.65-1.00.
#   Its left instrument wall fills the upper-left of the photograph, while the
#   long foreground desk runs diagonally from the lower-left toward the center.
# - The wall-mounted cabinet bank is light colored, with repeated square dark
#   instrument frames and a horizontal vent. Its top edge slopes gently down
#   toward the right in the photograph.
# - The main desk has a pale, sloping control surface over a dark pedestal.
#   Its front edge slopes down toward the right; its rear edge rises toward the
#   right. It overlaps the lower portion of the instrument wall.
# - A doorway and small freestanding console occupy the right rear of the room.
#   The precise room depth, ceiling, and hidden cabinet portions are uncertain.
# - The separate yellow GRID panel occupies approximately x=.03-.52,
#   y=.19-.64 in the supplied composite. Its black vertical single-line diagram,
#   amber square indicators, red lamps, and left-hand controls are distinctive.
#   The source does not establish its physical position inside the photographed
#   room; it is placed on the right wall as a visible training display.
# - Image anchors for the reconstructed room: wall bank near upper left,
#   main desk centered in the foreground, yellow panel on the right rear wall,
#   doorway and small console at right. This is a plausible integration of two
#   source images, not a claim that the yellow panel appears in the room photo.
#
# Primitive budget: approximately 350 SceneAct boxes and rods, including roughly
# 90 wall instruments, 95 console controls, 35 GRID diagram segments and
# indicators, 20 small-console details, and the room/cabinet structure.
# Camera and major geometry parameters are kept separate for later adjustment.

import math
import bpy
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

# ------------------------- adjustable scene parameters ------------------------
ROOM_W = 8.4
ROOM_D = 6.0
ROOM_H = 3.2
DESK_W = 5.35
DESK_D = 1.32
DESK_X = -0.85
DESK_Y = -0.48
GRID_W = 1.15
GRID_H = 1.65
GRID_X = 2.66
CAMERA_POSITION = (9.2, -12.8, 7.0)
CAMERA_TARGET = (0.0, 0.55, 1.22)
CAMERA_LENS = 34

cream = (0.68, 0.67, 0.62)
wall = (0.75, 0.74, 0.69)
floor_color = (0.31, 0.30, 0.27)
metal = (0.67, 0.67, 0.63)
panel = (0.77, 0.76, 0.70)
dark = (0.09, 0.095, 0.09)
black = (0.025, 0.027, 0.023)
paper = (0.87, 0.86, 0.78)
yellow = (0.91, 0.69, 0.13)
amber = (1.0, 0.55, 0.035)
red = (0.72, 0.025, 0.012)
scene = Scene("1970s grid dispatch room")

# The back wall is y=+3. The camera looks from the open front of the room.
architecture = Asset("Architecture")
architecture.include("floor", box((ROOM_W, ROOM_D, 0.12),
    center=(0, 0, -0.06), color=floor_color))
architecture.include("back_wall", box((ROOM_W, 0.12, ROOM_H),
    center=(0, ROOM_D/2, ROOM_H/2), color=wall))
architecture.include("right_wall", box((0.12, ROOM_D, ROOM_H),
    center=(ROOM_W/2, 0, ROOM_H/2), color=wall))
architecture.include("left_wall", box((0.12, ROOM_D, ROOM_H),
    center=(-ROOM_W/2, 0, ROOM_H/2), color=wall))
# Ceiling is deliberately not a solid occluder, so the room remains visible from
# the elevated overall camera. Physical light fixtures establish its height.
for x in (-2.4, 0.0, 2.4):
    architecture.include("ceiling_light_%s" % x, box((1.35, 0.42, 0.055),
        center=(x, 1.45, 3.12), color=(0.96, 0.96, 0.87)))
scene.include("Architecture", architecture)

# Tall modular instrument cabinets on the back wall.
bank = Asset("Main wall instrument bank")
bank.include("cabinet_body", box((5.55, 0.32, 2.10),
    center=(-1.15, 2.76, 1.55), color=metal))
bank.include("cabinet_header", box((5.55, 0.34, 0.12),
    center=(-1.15, 2.75, 2.54), color=cream))
for x in (-3.80, -3.10, -2.40, -1.70, -1.00, -0.30, 0.40, 1.10, 1.55):
    bank.include("seam_%s" % x, box((0.018, 0.018, 1.88),
        center=(x, 2.585, 1.54), color=(0.42, 0.42, 0.39)))

# Uniform square instruments; a vent leaves the visible central interruption.
for col in range(12):
    x = -3.65 + col * 0.425
    if 5 <= col <= 7:
        continue
    for row in range(4):
        z = 0.98 + row * 0.32
        bank.include("meter_frame_%02d_%02d" % (col, row),
            box((0.265, 0.027, 0.245), center=(x, 2.57, z), color=dark))
        bank.include("meter_face_%02d_%02d" % (col, row),
            box((0.214, 0.014, 0.195), center=(x, 2.55, z), color=paper))
        bank.include("meter_needle_%02d_%02d" % (col, row),
            rod(0.006, start=(x-0.050, 2.535, z-0.045),
                end=(x+0.035, 2.535, z+0.055), color=black))
# Broad central ventilation grille, with a restrained number of slats.
bank.include("vent_border", box((1.24, 0.032, 0.70),
    center=(-1.10, 2.56, 1.66), color=dark))
bank.include("vent_inside", box((1.15, 0.018, 0.62),
    center=(-1.10, 2.535, 1.66), color=(0.27, 0.28, 0.26)))
for j in range(6):
    bank.include("vent_slat_%d" % j, box((1.13, 0.018, 0.025),
        center=(-1.10, 2.52, 1.42+j*0.095), color=cream))
scene.include("Main wall instrument bank", bank)

# Main desk: horizontal writing ledge in front and a sloping top behind.
# A rotated shallow box is used for each of the control face and its backing.
desk = Asset("Main sloping dispatch console")
desk.include("pedestal", box((DESK_W-0.18, 1.02, 0.69),
    center=(DESK_X, DESK_Y+0.03, 0.355), color=(0.24, 0.24, 0.22)))
desk.include("front_kick", box((DESK_W-0.3, 0.08, 0.16),
    center=(DESK_X, DESK_Y-0.47, 0.10), color=dark))
desk.include("writing_surface", box((DESK_W, 0.50, 0.075),
    center=(DESK_X, DESK_Y-0.53, 0.76), color=paper))
desk.include("writing_front_edge", box((DESK_W, 0.045, 0.10),
    center=(DESK_X, DESK_Y-0.79, 0.74), color=metal))
# Surface rises toward the back of the room.
slope = math.radians(20)
slope_len = 0.94
surface_y = DESK_Y + 0.13
surface_z = 0.94
slab = box((DESK_W, slope_len, 0.12),
    center=(DESK_X, surface_y, surface_z), color=panel)
slab.turn(axis="+x", degrees=20)
desk.include("sloping_control_surface", slab)

# Coordinate conversion for details laid flat against the inclined desk.
def desk_point(x, v, lift=0.0):
    return (x,
            surface_y + v*math.cos(slope) - lift*math.sin(slope),
            surface_z + v*math.sin(slope) + lift*math.cos(slope))

# Several separately outlined control sections convey the long console's
# distribution without relying on tiny, unreadable sub-pixel decorations.
for section in range(7):
    x = DESK_X - DESK_W/2 + 0.39 + section*0.76
    p = desk_point(x, 0.05, 0.074)
    plate = box((0.66, 0.70, 0.018), center=p, color=(0.85, 0.84, 0.77))
    plate.turn(axis="+x", degrees=20)
    desk.include("control_section_%d" % section, plate)
    for row in range(3):
        for col in range(4):
            xx = x - 0.235 + col*0.155
            v = -0.23 + row*0.21
            a = desk_point(xx, v, 0.085)
            b = desk_point(xx, v, 0.115)
            desk.include("switch_%d_%d_%d" % (section, row, col),
                rod(0.025 if row != 2 else 0.018, start=a, end=b, color=dark))
    # One larger pale instrument on each section.
    p = desk_point(x, 0.29, 0.09)
    meter = box((0.20, 0.11, 0.018), center=p, color=(0.35, 0.35, 0.32))
    meter.turn(axis="+x", degrees=20)
    desk.include("console_meter_%d" % section, meter)
scene.include("Main sloping dispatch console", desk)

# A dark doorway, with a pale surround, behind the right-hand console.
door = Asset("Rear doorway")
door.include("recess", box((0.80, 0.045, 2.20),
    center=(2.16, 2.91, 1.10), color=(0.16, 0.16, 0.15)))
door.include("left_jamb", box((0.09, 0.11, 2.25),
    center=(1.73, 2.84, 1.12), color=paper))
door.include("right_jamb", box((0.09, 0.11, 2.25),
    center=(2.59, 2.84, 1.12), color=paper))
door.include("lintel", box((0.95, 0.11, 0.10),
    center=(2.16, 2.84, 2.23), color=paper))
scene.include("Rear doorway", door)

# GRID panel is mounted on the right wall, facing toward the room interior.
# Its local horizontal axis is world Y and its outward normal is world -X.
grid = Asset("Yellow GRID single-line mimic panel")
gx = ROOM_W/2 - 0.09
gy = 1.24
gz = 2.02
grid.include("yellow_backboard", box((0.075, GRID_W, GRID_H),
    center=(gx, gy, gz), color=yellow))
front_x = gx - 0.052
# Diagram occupies the right two-thirds of the panel, as on the source.
def grid_line(name, y1, z1, y2, z2, width=0.012):
    grid.include(name, rod(width, start=(front_x, y1, z1),
                            end=(front_x, y2, z2), color=black))
line_y = gy + 0.20
grid_line("main_bus", line_y, gz-0.72, line_y, gz+0.72, 0.014)
for k, z in enumerate((gz-0.42, gz+0.18)):
    grid_line("bus_cross_%d" % k, line_y-0.25, z, line_y+0.25, z)
    grid_line("loop_left_%d" % k, line_y-0.25, z-0.16, line_y-0.25, z+0.16)
    grid_line("loop_right_%d" % k, line_y+0.25, z-0.16, line_y+0.25, z+0.16)
    grid_line("loop_top_%d" % k, line_y-0.25, z+0.16, line_y+0.25, z+0.16)
    grid_line("loop_bottom_%d" % k, line_y-0.25, z-0.16, line_y+0.25, z-0.16)
    for j in range(3):
        yy = line_y - 0.16 + j*0.16
        grid.include("amber_frame_%d_%d" % (k, j),
            box((0.025, 0.105, 0.14), center=(front_x-0.016, yy, z), color=dark))
        grid.include("amber_lamp_%d_%d" % (k, j),
            box((0.025, 0.066, 0.095), center=(front_x-0.033, yy, z), color=amber))
for j, z in enumerate((gz-0.65, gz+0.54)):
    grid.include("red_bus_frame_%d" % j, box((0.025, 0.10, 0.13),
        center=(front_x-0.015, line_y, z), color=black))
    grid.include("red_bus_lamp_%d" % j, box((0.023, 0.065, 0.09),
        center=(front_x-0.032, line_y, z), color=red))
# Left column of selector switches and round red indicator lamps.
for j in range(5):
    z = gz + 0.57 - j*0.235
    y = gy - 0.39
    grid.include("selector_plate_%d" % j, box((0.016, 0.14, 0.16),
        center=(front_x-0.012, y, z), color=paper))
    grid.include("selector_knob_%d" % j,
        rod(0.034, start=(front_x-0.025, y, z),
            end=(front_x-0.070, y, z), color=black))
    grid.include("red_indicator_%d" % j,
        rod(0.036, start=(front_x-0.025, y+0.16, z),
            end=(front_x-0.065, y+0.16, z), color=red))
scene.include("Yellow GRID mimic panel", grid)

# Independent compact console in the right rear corner.
small = Asset("Small right control console")
small.include("cabinet", box((1.24, 0.72, 0.78),
    center=(3.10, 1.92, 0.40), color=(0.40, 0.40, 0.37)))
small.include("control_top", box((1.30, 0.78, 0.10),
    center=(3.10, 1.92, 0.84), color=paper))
for r in range(3):
    for c in range(5):
        x = 2.62 + c*0.24
        y = 1.69 + r*0.22
        small.include("button_%d_%d" % (r, c),
            rod(0.027, start=(x, y, 0.90), end=(x, y, 0.93),
                color=red if (r == 0 and c == 4) else dark))
scene.include("Small right control console", small)

realize(scene)

# Configure room lighting and render options after SceneAct clears the scene.
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
background.inputs["Color"].default_value = (0.72, 0.73, 0.70, 1)
background.inputs["Strength"].default_value = 0.38

# Assign softly emissive materials to the existing SceneAct indicator meshes.
def emission_material(name, color, strength):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color, 1)
    return m

red_mat = emission_material("Indicator red", (0.8, 0.025, 0.01), 1.1)
amber_mat = emission_material("Indicator amber", (1.0, 0.42, 0.015), 1.0)
light_mat = emission_material("Fluorescent diffuser", (0.96, 0.95, 0.83), 0.7)
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    n = ob.name.lower()
    mat = None
    if "red_indicator" in n or "red_bus_lamp" in n:
        mat = red_mat
    elif "amber_lamp" in n:
        mat = amber_mat
    elif "ceiling_light" in n:
        mat = light_mat
    if mat:
        ob.data.materials.clear()
        ob.data.materials.append(mat)

# German function labels on the yellow board. They are separate editable text.
label_mat = bpy.data.materials.new("GRID label ink")
label_mat.diffuse_color = (0.02, 0.02, 0.015, 1)
def grid_label(name, text, y, z, size=0.050):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0
    curve.materials.append(label_mat)
    ob = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(ob)
    # Local text x runs toward negative Y and text y upward.
    ob.location = (front_x-0.045, y, z)
    ob.rotation_euler = (math.pi/2, 0, -math.pi/2)
    return ob

grid_label("Label grid", "NETZ", gy+0.48, gz+0.70, 0.055)
grid_label("Label fault", "FEHLERSTELLE", gy+0.48, gz-0.58, 0.035)
grid_label("Label switch", "SCHALTER", gy-0.25, gz-0.70, 0.035)

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
overview = sc.camera
overview.name = "Camera - room overview"

# A second editable camera focuses on the main desk and GRID display.
set_view((7.4, -5.7, 4.1), (2.15, 1.25, 1.45), lens=43)
detail_camera = sc.camera
detail_camera.name = "Camera - console and GRID detail"
sc.camera = overview

area_emitter((0, -1.0, 5.7), power=1500, size=5.0,
             target=(0, 0.8, 0.8), color=(1.0, 0.95, 0.87))
area_emitter((-3.0, -0.5, 3.2), power=650, size=3.0,
             target=(-1.5, 2.0, 1.2), color=(1.0, 0.98, 0.92))
area_emitter((3.2, 0.4, 3.0), power=500, size=2.0,
             target=(3.9, 1.3, 1.7), color=(1.0, 0.95, 0.84))

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
