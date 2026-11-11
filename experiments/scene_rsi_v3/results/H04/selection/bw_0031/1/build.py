import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

# Reference inventory and image anchors, estimated from the photograph at the
# bottom of the slide. Coordinates here are normalized to that photograph:
# - Rear cabinet wall: x=0.00–0.69, y=0.00–0.56. Pale panel doors contain
#   regular square meter banks; a dark horizontal grille sits near the center.
# - Long desk: x=0.00–0.71, y=0.36–1.00. Its near end overlaps the bottom
#   edge, its rear end overlaps the cabinet wall, and its long edges rise
#   noticeably toward the right. Pale sloping controls sit above a dark base.
# - Door: approximately x=0.71–0.79, y=0.10–0.56.
# - Small independent console: x=0.81–1.00, y=0.33–0.83.
# - Dark floor: visible around the furniture, especially at lower right.
# - Yellow GRID panel: shown separately on the slide; its room placement is
#   uncertain. Its face has black circuit lines, red round lamps, amber square
#   lamps, black selector knobs, and small German labels.
# Room corners hidden behind furniture are uncertain.
#
# Comparison with the last complete render, using the full rendered portrait:
# 1. A blank gray region fills approximately y=0.00–0.32, whereas the room
#    photograph contains a continuous interior. The camera was outside the
#    near edge of the room; the floor and ceiling terminated inside the view.
# 2. The rendered desk spans approximately x=0.04–0.83, y=0.49–0.72; in the
#    photograph it dominates the foreground and its long edges rise more
#    sharply to the right. The rendered pedestal is much lighter in appearance.
# 3. The rendered rear wall is around y=0.34–0.57, with the vent and meter
#    banks partly obscured by the desk. The reference has more exposed meter
#    wall and a dark grille. The small right console is mostly lost at the edge.
# 4. A yellow panel is visible at the render's far right; its reference room
#    location is unknown, so it remains an editable interpretation.
#
# Corrections, ranked by visible impact:
# - Extend the floor and ceiling toward the camera and place CAMERA_POSITION
#   inside the enclosure. This should replace the gray exterior with interior
#   surfaces and preserve the room's rectangular wall relationship.
# - Move CAMERA_POSITION farther left, lower it slightly, and aim across the
#   room. This should steepen the desk's right-rising edges and reveal the
#   right-hand console. A numerical check prints the old and new projections,
#   plus a small upward-aim trial, for actual geometry landmarks.
# - Increase DESK_DEPTH and darken its pedestal; these changes enlarge the
#   foreground sloped surface and restore the large dark region beneath it.
# - Move the rear instruments upward and spread the meter banks across the
#   cabinet wall, making them visible above the desk. These are local changes.
# Illumination and surface orientation also affect the observed brightness.
#
# Primitive estimate: architecture 5; cabinet wall, seams and vent 18;
# meters 40*2=80; desk body 5, separators 8, controls 84, instruments 16;
# door 3; small console 17; GRID panel and diagram about 35; fixtures 3.
# Approximately 274 SceneAct box/rod primitives, plus text objects.
# No Boolean operations or external files are used.

CAMERA_POSITION = (-5.0, -3.85, 2.55)
CAMERA_TARGET = (-0.10, 1.35, 1.35)
CAMERA_LENS = 25.0
OLD_POSITION = (-3.5, -6.7, 3.05)
OLD_TARGET = (0.05, 1.65, 1.35)
OLD_LENS = 25.0

ROOM_W = 8.4
ROOM_D = 11.0
ROOM_H = 3.2
BACK_Y = 2.8
ROOM_CENTER_Y = BACK_Y - ROOM_D / 2

scene = Scene("1970s grid control room")

wall = (0.68, 0.66, 0.62)
ceiling = (0.76, 0.74, 0.70)
floor = (0.26, 0.235, 0.21)
cabinet = (0.63, 0.62, 0.58)
pale = (0.79, 0.77, 0.72)
dark = (0.105, 0.095, 0.085)
black = (0.025, 0.025, 0.023)
yellow = (0.88, 0.62, 0.065)
red = (0.80, 0.025, 0.012)
amber = (1.0, 0.40, 0.015)

def B(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def R(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

architecture = Asset("Architecture")
B(architecture, "floor", (ROOM_W, ROOM_D, .12),
  (0, ROOM_CENTER_Y, -.06), floor)
B(architecture, "back_wall", (ROOM_W, .12, ROOM_H),
  (0, BACK_Y + .06, ROOM_H / 2), wall)
B(architecture, "right_wall", (.12, ROOM_D, ROOM_H),
  (ROOM_W / 2 + .06, ROOM_CENTER_Y, ROOM_H / 2), wall)
B(architecture, "ceiling", (ROOM_W, ROOM_D, .08),
  (0, ROOM_CENTER_Y, ROOM_H + .04), ceiling)
B(architecture, "back_baseboard", (ROOM_W, .035, .12),
  (0, BACK_Y - .025, .06), dark)
scene.include("Architecture", architecture)

cabinets = Asset("Rear instrument cabinets")
B(cabinets, "cabinet_body", (5.70, .25, 2.77),
  (-1.25, BACK_Y - .13, 1.55), cabinet)
for i in range(7):
    x = -4.04 + i * .92
    B(cabinets, "vertical_seam_%02d" % i, (.014, .025, 2.64),
      (x, BACK_Y - .27, 1.55), dark)
B(cabinets, "upper_header", (5.64, .03, .09),
  (-1.25, BACK_Y - .27, 2.72), pale)

# Square instrument banks with pale faces and dark frames.
for bank, x0 in enumerate((-3.88, .24)):
    for col in range(5):
        for row in range(4):
            x = x0 + .25 * col
            z = 1.05 + .29 * row
            tag = "%d_%d_%d" % (bank, col, row)
            B(cabinets, "meter_frame_" + tag, (.205, .035, .23),
              (x, BACK_Y - .285, z), dark)
            B(cabinets, "meter_face_" + tag, (.164, .015, .19),
              (x, BACK_Y - .31, z), pale)

B(cabinets, "vent_recess", (1.48, .04, .70),
  (-1.25, BACK_Y - .29, 1.64), dark)
for i in range(7):
    B(cabinets, "vent_louver_%d" % i, (1.40, .025, .038),
      (-1.25, BACK_Y - .32, 1.37 + i * .085), cabinet)
scene.include("Rear instrument cabinets", cabinets)

desk = Asset("Main sloping control desk")
DESK_X = -1.05
DESK_W = 5.65
DESK_Y = .15
DESK_DEPTH = 1.65
ANGLE = 18.0
a = math.radians(ANGLE)
SURFACE_Y = DESK_Y + .17
SURFACE_Z = 1.14

B(desk, "dark_pedestal", (5.42, 1.45, .79),
  (DESK_X, DESK_Y, .405), (.14, .125, .11))
B(desk, "lower_plinth", (5.44, 1.47, .12),
  (DESK_X, DESK_Y, .07), dark)
B(desk, "horizontal_writing_ledge", (5.76, .45, .08),
  (DESK_X, DESK_Y - 1.03, .88), pale)
B(desk, "writing_front_edge", (5.76, .035, .10),
  (DESK_X, DESK_Y - 1.26, .86), dark)
surface = box((DESK_W, DESK_DEPTH, .09),
              center=(DESK_X, SURFACE_Y, SURFACE_Z), color=pale)
surface.turn(axis="+x", degrees=ANGLE)
desk.include("inclined_control_surface", surface)

def surface_point(x, along, lift):
    return (x,
            SURFACE_Y + along * math.cos(a) - lift * math.sin(a),
            SURFACE_Z + along * math.sin(a) + lift * math.cos(a))

for i in range(8):
    x = DESK_X - 2.67 + i * .76
    R(desk, "panel_divider_%d" % i, .010,
      surface_point(x, -.76, .053),
      surface_point(x, .76, .053), dark)

for col in range(21):
    x = DESK_X - 2.55 + col * .255
    for row in range(4):
        p = surface_point(x, -.55 + row * .30, .067)
        R(desk, "control_%02d_%d" % (col, row), .023,
          p, (p[0], p[1] - .012, p[2] + .038), dark)

for i in range(8):
    x = DESK_X - 2.38 + i * .68
    bezel = box((.31, .19, .022),
                center=surface_point(x, .62, .065), color=dark)
    bezel.turn(axis="+x", degrees=ANGLE)
    desk.include("instrument_bezel_%d" % i, bezel)
    face = box((.25, .14, .012),
               center=surface_point(x, .62, .083), color=pale)
    face.turn(axis="+x", degrees=ANGLE)
    desk.include("instrument_face_%d" % i, face)
scene.include("Main control desk", desk)

door = Asset("Doorway")
B(door, "outer_frame", (.93, .065, 2.30),
  (2.38, BACK_Y - .05, 1.15), pale)
B(door, "dark_opening", (.71, .035, 2.04),
  (2.38, BACK_Y - .095, 1.08), dark)
B(door, "inner_door", (.47, .025, 1.80),
  (2.42, BACK_Y - .12, 1.02), (.28, .27, .25))
scene.include("Doorway", door)

small = Asset("Small independent console")
B(small, "pedestal", (1.48, .94, .80),
  (3.30, 1.48, .40), (.22, .20, .18))
top = box((1.58, 1.00, .10),
          center=(3.30, 1.48, .89), color=pale)
top.turn(axis="+x", degrees=12)
small.include("sloping_top", top)
for i in range(5):
    for j in range(3):
        x = 2.80 + i * .25
        y = 1.20 + j * .23
        z = .97 + (y - 1.48) * math.tan(math.radians(12))
        R(small, "control_%d_%d" % (i, j), .022,
          (x, y, z), (x, y, z + .035), dark)
scene.include("Small independent console", small)

# Panel location is an interpretation; the slide presents it separately.
grid = Asset("Yellow GRID mimic panel")
gx, gy, gz = 4.16, .15, 2.00
B(grid, "yellow_face", (.045, 1.42, 1.82), (gx, gy, gz), yellow)
line_x = gx - .035

def gridline(name, p, q, radius=.014):
    R(grid, name, radius,
      (line_x, gy + p[0], gz + p[1]),
      (line_x, gy + q[0], gz + q[1]), black)

gridline("main_bus", (.10, -.77), (.10, .77), .018)
for i, z in enumerate((-.48, .08, .55)):
    gridline("cross_%d" % i, (-.29, z), (.43, z))
for i, y in enumerate((-.27, .36)):
    gridline("branch_%d" % i, (y, -.48), (y, .55))
for i, (y, z) in enumerate(((.10, -.70), (.10, .70),
                             (-.27, .08), (.36, .08))):
    R(grid, "red_indicator_%d" % i, .053,
      (line_x - .012, gy + y, gz + z),
      (line_x - .045, gy + y, gz + z), red)
for i, (y, z) in enumerate(((-.27, -.48), (.10, -.48), (.36, -.48),
                             (-.27, .55), (.10, .55), (.36, .55))):
    B(grid, "amber_indicator_%d" % i, (.035, .09, .09),
      (line_x - .025, gy + y, gz + z), amber)
for i in range(4):
    z = gz - .54 + i * .34
    B(grid, "selector_scale_%d" % i, (.016, .17, .17),
      (line_x - .01, gy - .52, z), pale)
    R(grid, "selector_knob_%d" % i, .047,
      (line_x - .02, gy - .52, z),
      (line_x - .065, gy - .52, z), black)
scene.include("GRID mimic panel", grid)

fixtures = Asset("Fluorescent ceiling fixtures")
for i, x in enumerate((-2.5, 0.0, 2.5)):
    B(fixtures, "troffer_%d" % i, (1.55, .38, .035),
      (x, .25, ROOM_H - .035), (1.0, .96, .86))
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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (.72, .70, .66, 1)
background.inputs["Strength"].default_value = .30

# The source aspect is 374:512. The long dimension exceeds 1920 pixels.
sc.render.resolution_x = 1536
sc.render.resolution_y = 2103
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
panorama = sc.camera
panorama.name = "Camera - room panorama"
area_emitter((0, .2, 3.08), power=700, size=4.0,
             target=(0, .8, .4), color=(1.0, .95, .87))
area_emitter((-3.0, -2.5, 2.8), power=320, size=3.0,
             target=(-1.0, 1.3, 1.1), color=(1.0, .97, .91))

bpy.ops.object.camera_add(location=(-.2, -3.5, 2.25))
detail_camera = bpy.context.object
detail_camera.name = "Camera - console and GRID detail"
detail_camera.rotation_euler = (
    Vector((2.2, 1.2, 1.45)) - detail_camera.location
).to_track_quat("-Z", "Y").to_euler()
detail_camera.data.lens = 35
sc.camera = panorama

# Apply emission to the existing indicator materials where their colors match.
# Preserve the shared palette rather than producing per-lamp materials.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    color = bsdf.inputs["Base Color"].default_value
    is_red = color[0] > .65 and color[1] < .12 and color[2] < .10
    is_amber = color[0] > .85 and .25 < color[1] < .55 and color[2] < .10
    if is_red or is_amber:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = tuple(color)
            bsdf.inputs["Emission Strength"].default_value = .65

label_mat = bpy.data.materials.new("GRID German lettering")
label_mat.diffuse_color = (.025, .025, .022, 1)

def label(name, text, y, z, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.size = size
    curve.extrude = .0003
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    ob.location = (line_x - .05, gy + y, gz + z)
    ob.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    ob.data.materials.append(label_mat)

label("GRID title", "NETZ", -.62, .78, .10)
label("Fault location label", "FEHLERSTELLE", -.60, -.82, .06)

# Numerical projection check. Reference values below are estimates for a
# room-filling portrait composition, distinct from the photograph-crop bounds.
# Projected points are geometry landmarks, not observed silhouette bounds.
REFERENCE = {
    "back_left": (.04, .27),
    "back_right": (.70, .29),
    "desk_front_left": (.04, .67),
    "desk_back_right": (.70, .50),
    "door_top": (.76, .35),
}
POINTS = {
    "back_left": (-4.04, BACK_Y - .27, 2.72),
    "back_right": (1.55, BACK_Y - .27, 2.72),
    "desk_front_left": (DESK_X - 2.88, DESK_Y - 1.26, .88),
    "desk_back_right": (DESK_X + DESK_W / 2,
                        SURFACE_Y + .78, 1.40),
    "door_top": (2.38, BACK_Y - .12, 2.30),
}

def set_camera_pose(position, target, lens):
    panorama.location = position
    panorama.rotation_euler = (
        Vector(target) - panorama.location
    ).to_track_quat("-Z", "Y").to_euler()
    panorama.data.lens = lens
    bpy.context.view_layer.update()

def project_points():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    projection = panorama.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y
    )
    result = {}
    for name, p in POINTS.items():
        clip = projection @ panorama.matrix_world.inverted() @ Vector((*p, 1.0))
        result[name] = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1),
            .5 * (1 - clip.y / clip.w)
        )
    return result

set_camera_pose(OLD_POSITION, OLD_TARGET, OLD_LENS)
old_projection = project_points()
set_camera_pose(CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS)
chosen_projection = project_points()
trial_target = (CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2] + .10)
set_camera_pose(CAMERA_POSITION, trial_target, CAMERA_LENS)
trial_projection = project_points()
set_camera_pose(CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS)

print("Landmark                reference       previous camera       chosen camera         upward trial")
for name in POINTS:
    print("%-23s %-15s %-21s %-21s %s" %
          (name, REFERENCE[name], old_projection[name],
           chosen_projection[name], trial_projection[name]))

# The external runner owns saving and rendering.
