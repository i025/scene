import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

# Reference inventory and anchors, estimated visually from the supplied image:
# The indoor photograph occupies the bottom of a slide; this reconstruction frames
# that room as the subject. The photograph's approximate normalized bounds are
# (0.03, 0.65)–(0.94, 1.00) in the full slide.
# Within that photograph:
# - Rear instrument wall: x 0.03–0.70, y 0.03–0.55; rows of square meters,
#   a broad central ventilation grille, and tall pale cabinet panels.
# - Main desk: x 0.03–0.72, y 0.40–0.95; long inclined control surface,
#   horizontal front writing ledge, dark supporting base. Its long edges run
#   diagonally upward toward the right in the photograph.
# - Right wall and doorway: x 0.68–0.95, y 0.02–0.80; a narrow dark doorway
#   overlaps the rear wall.
# - Small separate console: x 0.81–0.99, y 0.36–0.82, in front of the right wall.
# - Floor: lower part of the photograph, visible around and in front of desks.
# The yellow GRID panel is shown separately in the slide, not visibly located in
# the room photograph. Its placement on the right wall is therefore uncertain.
# Its yellow face, black circuit lines, red circular lamps, amber square lamps,
# switches, and small German labels follow the separate panel reference.
# The room corners and desk backs are partly occluded; their depth is approximate.
#
# Geometry budget: approximately 310 SceneAct primitives: architecture 10,
# rear cabinets and meters 110, main desk and controls 135, right console 25,
# GRID panel 30. Each box or rod emits one primitive. Text and four ceiling
# fixtures are added with bpy after realization. No Boolean operations are used.
#
# Reference landmark estimates below refer to the room photograph alone. They
# are approximate, not calibrated; projection prints are diagnostic only.
REFERENCE_LANDMARKS = {
    "rear_wall_upper_left": (0.03, 0.04),
    "rear_wall_upper_right": (0.70, 0.04),
    "desk_front_left": (0.04, 0.76),
    "desk_far_right": (0.70, 0.43),
    "door_top": (0.74, 0.15),
}

# Camera and room parameters are independent of asset dimensions.
CAMERA_POSITION = (7.4, -10.5, 5.6)
CAMERA_TARGET = (0.0, 0.50, 1.35)
CAMERA_LENS = 34
ROOM_WIDTH = 8.6
ROOM_DEPTH = 6.2
ROOM_HEIGHT = 3.4
BACK_Y = 2.65
FLOOR_Z = 0.0

scene = Scene("1970s Grid Control Room")

wall_col = (0.69, 0.67, 0.62)
wall_light = (0.78, 0.76, 0.70)
floor_col = (0.31, 0.29, 0.26)
cabinet_col = (0.61, 0.60, 0.56)
console_col = (0.64, 0.63, 0.59)
face_col = (0.76, 0.75, 0.69)
dark = (0.12, 0.12, 0.11)
black = (0.035, 0.035, 0.032)
white = (0.86, 0.84, 0.76)
yellow = (0.91, 0.67, 0.08)
red = (0.73, 0.06, 0.035)
amber = (1.0, 0.49, 0.035)

def add_box(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def add_rod(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

architecture = Asset("Architecture")
add_box(architecture, "floor", (ROOM_WIDTH, ROOM_DEPTH, 0.12),
        (0, -0.4, -0.06), floor_col)
add_box(architecture, "back_wall", (ROOM_WIDTH, 0.12, ROOM_HEIGHT),
        (0, BACK_Y + 0.06, ROOM_HEIGHT / 2), wall_col)
add_box(architecture, "right_wall", (0.12, ROOM_DEPTH, ROOM_HEIGHT),
        (ROOM_WIDTH / 2, -0.4, ROOM_HEIGHT / 2), wall_light)
add_box(architecture, "ceiling", (ROOM_WIDTH, ROOM_DEPTH, 0.08),
        (0, -0.4, ROOM_HEIGHT + 0.04), wall_light)
add_box(architecture, "back_baseboard", (ROOM_WIDTH, 0.05, 0.12),
        (0, BACK_Y - 0.04, 0.06), dark)
scene.include("architecture", architecture)

# Continuous cabinet wall with regular, recognizable instrument bays.
cabinets = Asset("Rear instrument cabinets")
cabinet_left, cabinet_right = -4.05, 1.65
add_box(cabinets, "cabinet_wall", (5.7, 0.23, 2.65),
        (-1.2, BACK_Y - 0.15, 1.48), cabinet_col)
# Panel joints and narrow upper headers.
for x in [-4.0, -3.05, -2.10, -1.15, -0.20, 0.75, 1.60]:
    add_box(cabinets, "joint_%s" % x, (0.018, 0.025, 2.55),
            (x, BACK_Y - 0.285, 1.48), dark)
add_box(cabinets, "header", (5.65, 0.035, 0.12),
        (-1.2, BACK_Y - 0.285, 2.61), face_col)

# Two banks of square meters flank the ventilation grille. Every meter has a
# dark bezel and pale face, with a small dark pointer.
meter_positions = []
for base_x, columns in [(-3.78, 4), (0.37, 4)]:
    for col in range(columns):
        for row in range(4):
            meter_positions.append((base_x + col * 0.26, 0.85 + row * 0.31))
for i, (x, z) in enumerate(meter_positions):
    add_box(cabinets, "meter_frame_%02d" % i, (0.205, 0.035, 0.235),
            (x, BACK_Y - 0.305, z), dark)
    add_box(cabinets, "meter_face_%02d" % i, (0.165, 0.015, 0.193),
            (x, BACK_Y - 0.329, z), white)
    add_rod(cabinets, "meter_needle_%02d" % i, 0.009,
            (x - 0.025, BACK_Y - 0.341, z - 0.045),
            (x + 0.025, BACK_Y - 0.341, z + 0.040), dark)

# A wide louvered ventilation grille is an important dark region in the photo.
add_box(cabinets, "vent_recess", (1.55, 0.035, 0.72),
        (-1.22, BACK_Y - 0.31, 1.54), dark)
for i in range(7):
    add_box(cabinets, "vent_louver_%02d" % i, (1.43, 0.025, 0.045),
            (-1.22, BACK_Y - 0.34, 1.28 + i * 0.085), cabinet_col)
scene.include("rear_cabinets", cabinets)

# Main long sloping console. Sloped surfaces are represented by rotated boxes;
# control points follow the same slope.
desk = Asset("Main sloping control desk")
desk_x = -0.93
desk_width = 5.45
desk_y = -0.02
add_box(desk, "dark_pedestal", (5.24, 1.25, 0.78),
        (desk_x, desk_y + 0.02, 0.40), (0.22, 0.21, 0.19))
add_box(desk, "front_plinth", (5.34, 0.08, 0.17),
        (desk_x, desk_y - 0.65, 0.12), dark)
# Horizontal writing ledge at the front.
add_box(desk, "writing_ledge", (5.55, 0.44, 0.08),
        (desk_x, desk_y - 0.79, 0.91), face_col)
add_box(desk, "writing_front_edge", (5.55, 0.035, 0.10),
        (desk_x, desk_y - 1.015, 0.88), dark)

# Control surface rises toward the rear.
slope_angle = math.radians(19)
surface_depth = 1.25
surface_center_y = desk_y + 0.05
surface_center_z = 1.16
surface = box((desk_width, surface_depth, 0.085),
              center=(desk_x, surface_center_y, surface_center_z), color=face_col)
surface.turn(axis="+x", degrees=19)
desk.include("inclined_surface", surface)

def surface_point(x, along, lift=0.06):
    return (x,
            surface_center_y + along * math.cos(slope_angle) - lift * math.sin(slope_angle),
            surface_center_z + along * math.sin(slope_angle) + lift * math.cos(slope_angle))

# Panel separators and groups of small dark controls, spaced visibly.
for i in range(7):
    x = desk_x - desk_width / 2 + 0.15 + i * 0.84
    p1 = surface_point(x, -0.56, 0.052)
    p2 = surface_point(x, 0.56, 0.052)
    add_rod(desk, "panel_divider_%02d" % i, 0.012, p1, p2, dark)

for col in range(24):
    x = desk_x - 2.52 + col * 0.215
    for row in range(3):
        along = -0.37 + row * 0.31
        p = surface_point(x, along, 0.075)
        add_rod(desk, "knob_%02d_%02d" % (col, row), 0.029,
                (p[0], p[1], p[2]),
                (p[0], p[1] - 0.018, p[2] + 0.053), dark)
# A row of larger pale instruments across the back.
for col in range(10):
    x = desk_x - 2.34 + col * 0.52
    p = surface_point(x, 0.47, 0.07)
    meter = box((0.26, 0.18, 0.025), center=p, color=dark)
    meter.turn(axis="+x", degrees=19)
    desk.include("desk_meter_bezel_%02d" % col, meter)
    p2 = surface_point(x, 0.47, 0.087)
    face = box((0.20, 0.13, 0.012), center=p2, color=white)
    face.turn(axis="+x", degrees=19)
    desk.include("desk_meter_face_%02d" % col, face)
scene.include("main_desk", desk)

# Doorway appears as a narrow dark rectangle, with a pale frame.
door = Asset("Doorway")
add_box(door, "frame", (0.90, 0.07, 2.25),
        (2.42, BACK_Y - 0.08, 1.13), (0.84, 0.82, 0.77))
add_box(door, "opening", (0.66, 0.035, 1.99),
        (2.42, BACK_Y - 0.125, 1.06), (0.18, 0.18, 0.16))
add_box(door, "door_inner", (0.44, 0.025, 1.72),
        (2.48, BACK_Y - 0.15, 1.01), (0.32, 0.31, 0.28))
scene.include("doorway", door)

small = Asset("Right freestanding console")
add_box(small, "base", (1.45, 0.90, 0.77),
        (3.25, 1.35, 0.40), (0.32, 0.31, 0.28))
small_top = box((1.55, 1.0, 0.10),
                center=(3.25, 1.35, 0.88), color=face_col)
small_top.turn(axis="+x", degrees=12)
small.include("sloped_top", small_top)
for i in range(6):
    for j in range(3):
        x = 2.66 + i * 0.23
        y = 1.07 + j * 0.23
        z = 0.96 + (y - 1.35) * math.tan(math.radians(12))
        add_rod(small, "button_%d_%d" % (i, j), 0.025,
                (x, y, z), (x, y, z + 0.035), dark)
scene.include("small_console", small)

# Yellow GRID board on the right wall: its room placement is an interpretation,
# because the reference shows it separately from the room photograph.
grid = Asset("GRID mimic panel")
gx = 4.22
gy = -0.25
gz = 2.02
add_box(grid, "yellow_face", (0.045, 1.45, 1.92),
        (gx, gy, gz), yellow)

# Black circuit diagram on the wall-facing plane, x fixed.
line_x = gx - 0.032
def grid_line(name, yz1, yz2, radius=0.014):
    add_rod(grid, name, radius,
            (line_x, gy + yz1[0], gz + yz1[1]),
            (line_x, gy + yz2[0], gz + yz2[1]), black)

grid_line("main_bus", (0.12, -0.78), (0.12, 0.78), 0.018)
for i, z in enumerate([-0.53, 0.08, 0.57]):
    grid_line("cross_bus_%d" % i, (-0.30, z), (0.47, z))
for i, y in enumerate([-0.27, 0.37]):
    grid_line("branch_%d" % i, (y, -0.54), (y, 0.08))
    grid_line("upper_branch_%d" % i, (y, 0.08), (y, 0.57))
for i, (y, z) in enumerate([(0.12, -0.75), (0.12, 0.75),
                             (-0.27, 0.08), (0.37, 0.08)]):
    add_box(grid, "red_lamp_%d" % i, (0.035, 0.105, 0.105),
            (line_x - 0.025, gy + y, gz + z), red)
for i, (y, z) in enumerate([(-0.27, -0.53), (0.12, -0.53),
                             (0.37, -0.53), (-0.27, 0.57),
                             (0.12, 0.57), (0.37, 0.57)]):
    add_box(grid, "amber_indicator_%d" % i, (0.035, 0.09, 0.09),
            (line_x - 0.025, gy + y, gz + z), amber)
for i in range(4):
    y = gy - 0.53
    z = gz - 0.55 + i * 0.36
    add_rod(grid, "selector_%d" % i, 0.055,
            (line_x - 0.025, y, z), (line_x - 0.075, y, z), dark)
scene.include("grid_mimic", grid)

realize(scene)

# Configure the scene after realize(), which clears Blender.
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
background.inputs["Color"].default_value = (0.72, 0.70, 0.65, 1)
background.inputs["Strength"].default_value = 0.45

# Original full-image aspect is retained for the reconstruction camera.
sc.render.resolution_x = 1122
sc.render.resolution_y = 1536
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((0, -1.0, 3.25), power=850, size=4.5,
             target=(0, 0.3, 0.0), color=(1.0, 0.94, 0.84))
area_emitter((-3.0, -2.0, 2.9), power=400, size=3.0,
             target=(-1, 1, 1), color=(1.0, 0.97, 0.89))

# Visible fluorescent fixtures, separate from the soft area emitters.
def make_emission(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = (*color, 1)
    return mat

light_mat = make_emission("Fluorescent diffuser", (1.0, 0.93, 0.78), 1.5)
for i, x in enumerate((-2.5, 0.0, 2.5)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.0, 3.36))
    obj = bpy.context.object
    obj.name = "Ceiling fluorescent fixture %d" % (i + 1)
    obj.dimensions = (1.4, 0.35, 0.035)
    obj.data.materials.append(light_mat)

# A compact German label on the mimic panel, set on the exposed face.
label_mat = bpy.data.materials.new("Panel lettering")
label_mat.diffuse_color = (0.035, 0.035, 0.03, 1)
def grid_label(name, body, y, z, size=0.085):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0.0005
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    # Text local x runs along the wall; its front faces the room.
    ob.location = (line_x - 0.045, gy + y, gz + z)
    ob.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    ob.data.materials.append(label_mat)

grid_label("GRID title", "NETZ", -0.62, 0.80, 0.10)
grid_label("Fault label", "FEHLERSTELLE", -0.57, -0.86, 0.065)

# Explicit geometry landmarks and projection table. The reference positions are
# estimates in the room crop, while the computed points use the full camera.
LANDMARKS = {
    "rear_wall_upper_left": (-4.3, BACK_Y, 3.4),
    "rear_wall_upper_right": (1.65, BACK_Y, 3.4),
    "desk_front_left": (desk_x - desk_width / 2, desk_y - 1.0, 0.91),
    "desk_far_right": (desk_x + desk_width / 2, surface_center_y + 0.59, 1.36),
    "door_top": (2.42, BACK_Y - 0.15, 2.25),
}
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y
)
print("Landmark                       reference       projected")
for name, point in LANDMARKS.items():
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5 * (clip.x / clip.w + 1),
        0.5 * (1 - clip.y / clip.w)
    )
    print("%-30s %-15s %s" % (name, REFERENCE_LANDMARKS[name], uv))

# The runner owns saving and rendering. No render or file write is performed here.
