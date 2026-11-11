import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

# Reference inventory and visual anchors, estimated from the room photograph
# at the bottom of the supplied slide. Coordinates below are normalized to that
# photograph, not to the entire slide:
# - Rear cabinet wall: upper-left (0.00, 0.03), upper-right around (0.68, 0.06).
#   Its light cabinet faces contain meter arrays and a dark horizontal grille.
# - Main desk: front-left edge around (0.02, 0.66), far-right rear corner around
#   (0.70, 0.39), dark base extending toward the lower edge. The long desk edges
#   rise toward the right; the desk overlaps the lower instrument wall.
# - Doorway: around (0.72, 0.10)–(0.80, 0.56).
# - Small right console: around (0.81, 0.35)–(1.00, 0.82).
# - Floor: visible around the consoles, especially the lower right.
# The yellow GRID panel is separately pictured in the slide; its actual location
# in the room is uncertain. It is placed on the right wall as an interpretation.
#
# Comparison with the previous complete render:
# 1. The previous room was much too small: the rear wall upper left projected at
#    (0.32, 0.32), and the desk front left at (0.16, 0.51), in the full portrait
#    frame. The image showed large empty gray margins and the exterior of the
#    ceiling and right wall. These are the largest discrepancies.
# 2. The previous main desk occupied approximately x=.16–.65 and y=.45–.63 in
#    the full render, while the room photo shows a much larger desk with a
#    prominent dark base and a long edge rising toward the right.
# 3. The rear wall, door and separate console were largely hidden by the roof
#    and right wall. The back-wall meters and vent were therefore not legible.
# 4. The previous camera viewed from the opposite side, reversing the desk's
#    long-edge slope compared with the photograph.
#
# Corrections: CAMERA_POSITION moves to the front-left and inside the room,
# which should reverse the long-edge slope and reveal the right-hand doorway.
# CAMERA_LENS and CAMERA_TARGET enlarge and center the room features. Removing
# the ceiling slab from the camera view reveals the rear wall; the room retains
# a ceiling plane above the camera, and the right wall is retained. The desk is
# moved closer to the back wall and its surface is deeper, producing the broad
# inclined plane and foreground base. A numerical camera trial below prints
# projections before and after a small target change and restores the chosen
# camera. Projections measure points, not visible contours or occlusion.
#
# Expanded primitive estimate: architecture 5; rear wall and grille 17;
# meters 32*3=96; main desk 6+8+72+16=102; door 3; small console 16;
# GRID panel about 33; ceiling fixtures 3. Approximately 275 primitives,
# plus several text objects. All details are individually editable.

CAMERA_POSITION = (-3.5, -6.7, 3.05)
CAMERA_TARGET = (0.05, 1.65, 1.35)
CAMERA_LENS = 25.0

ROOM_W = 8.4
ROOM_D = 7.0
ROOM_H = 3.2
BACK_Y = 2.8

scene = Scene("1970s control room")

wall = (0.73, 0.71, 0.67)
ceiling_color = (0.77, 0.76, 0.72)
floor_color = (0.32, 0.29, 0.26)
cabinet = (0.66, 0.65, 0.61)
pale = (0.81, 0.79, 0.73)
panel = (0.70, 0.69, 0.65)
dark = (0.14, 0.13, 0.12)
black = (0.035, 0.034, 0.03)
yellow = (0.91, 0.67, 0.08)
red = (0.8, 0.06, 0.035)
amber = (1.0, 0.48, 0.04)

def B(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def R(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

architecture = Asset("Architecture")
B(architecture, "floor", (ROOM_W, ROOM_D, .12),
  (0, -.65, -.06), floor_color)
B(architecture, "rear_wall", (ROOM_W, .12, ROOM_H),
  (0, BACK_Y + .06, ROOM_H / 2), wall)
B(architecture, "right_wall", (.12, ROOM_D, ROOM_H),
  (ROOM_W / 2 + .06, -.65, ROOM_H / 2), wall)
# The ceiling is above the camera. Its front edge is behind the camera so it
# encloses the room without presenting its exterior face in the camera view.
B(architecture, "ceiling", (ROOM_W, ROOM_D, .08),
  (0, -.65, ROOM_H + .04), ceiling_color)
B(architecture, "rear_baseboard", (ROOM_W, .04, .12),
  (0, BACK_Y - .025, .06), dark)
scene.include("architecture", architecture)

cabinets = Asset("Rear meter cabinet wall")
B(cabinets, "cabinet_body", (5.70, .25, 2.77),
  (-1.25, BACK_Y - .13, 1.55), cabinet)
for i in range(7):
    x = -4.04 + i * .92
    B(cabinets, "cabinet_seam_%02d" % i, (.018, .025, 2.64),
      (x, BACK_Y - .27, 1.55), dark)
B(cabinets, "upper_header", (5.64, .03, .11),
  (-1.25, BACK_Y - .27, 2.72), pale)

# Meter banks frame a broad, dark ventilation grille.
for bank, x0 in enumerate((-3.86, .31)):
    for col in range(4):
        for row in range(4):
            x = x0 + .265 * col
            z = .91 + .31 * row
            name = "%d_%d_%d" % (bank, col, row)
            B(cabinets, "meter_bezel_" + name, (.215, .035, .245),
              (x, BACK_Y - .285, z), dark)
            B(cabinets, "meter_face_" + name, (.176, .014, .202),
              (x, BACK_Y - .309, z), pale)
            R(cabinets, "meter_pointer_" + name, .008,
              (x - .025, BACK_Y - .32, z - .045),
              (x + .025, BACK_Y - .32, z + .038), dark)
B(cabinets, "vent_opening", (1.50, .04, .72),
  (-1.25, BACK_Y - .29, 1.59), dark)
for i in range(7):
    B(cabinets, "vent_blade_%d" % i, (1.42, .025, .042),
      (-1.25, BACK_Y - .32, 1.31 + i * .09), cabinet)
scene.include("rear_cabinets", cabinets)

desk = Asset("Main sloping control desk")
DESK_X = -1.05
DESK_W = 5.65
DESK_Y = .15
ANGLE = 18.0
angle = math.radians(ANGLE)
SURFACE_Y = DESK_Y + .17
SURFACE_Z = 1.14

B(desk, "pedestal", (5.42, 1.32, .79),
  (DESK_X, DESK_Y, .405), (.25, .23, .21))
B(desk, "lower_plinth", (5.44, 1.34, .12),
  (DESK_X, DESK_Y, .07), dark)
B(desk, "writing_ledge", (5.76, .47, .08),
  (DESK_X, DESK_Y - .88, .90), pale)
B(desk, "writing_edge", (5.76, .035, .10),
  (DESK_X, DESK_Y - 1.12, .88), dark)
surface = box((DESK_W, 1.45, .09),
              center=(DESK_X, SURFACE_Y, SURFACE_Z), color=pale)
surface.turn(axis="+x", degrees=ANGLE)
desk.include("inclined_control_surface", surface)

def surface_point(x, along, lift):
    return (x,
            SURFACE_Y + along * math.cos(angle) - lift * math.sin(angle),
            SURFACE_Z + along * math.sin(angle) + lift * math.cos(angle))

for i in range(8):
    x = DESK_X - 2.67 + i * .76
    R(desk, "panel_divider_%d" % i, .010,
      surface_point(x, -.66, .052), surface_point(x, .66, .052), dark)

for col in range(24):
    x = DESK_X - 2.61 + col * .225
    for row in range(3):
        p = surface_point(x, -.43 + row * .31, .068)
        R(desk, "control_%02d_%d" % (col, row), .023,
          p, (p[0], p[1] - .012, p[2] + .035), dark)

for i in range(8):
    x = DESK_X - 2.38 + i * .68
    bezel = box((.31, .20, .022),
                center=surface_point(x, .48, .065), color=dark)
    bezel.turn(axis="+x", degrees=ANGLE)
    desk.include("instrument_bezel_%d" % i, bezel)
    face = box((.25, .15, .012),
               center=surface_point(x, .48, .083), color=pale)
    face.turn(axis="+x", degrees=ANGLE)
    desk.include("instrument_face_%d" % i, face)
scene.include("main_desk", desk)

door = Asset("Doorway")
B(door, "outer_frame", (.93, .065, 2.30),
  (2.38, BACK_Y - .05, 1.15), pale)
B(door, "dark_opening", (.71, .035, 2.04),
  (2.38, BACK_Y - .095, 1.08), dark)
B(door, "inner_door", (.47, .025, 1.80),
  (2.42, BACK_Y - .12, 1.02), (.30, .29, .27))
scene.include("doorway", door)

small = Asset("Small independent right console")
B(small, "pedestal", (1.48, .94, .80),
  (3.30, 1.48, .40), (.30, .28, .26))
small_top = box((1.58, 1.00, .10), center=(3.30, 1.48, .89), color=pale)
small_top.turn(axis="+x", degrees=12)
small.include("sloping_top", small_top)
for i in range(5):
    for j in range(3):
        x = 2.80 + i * .25
        y = 1.20 + j * .23
        z = .97 + (y - 1.48) * math.tan(math.radians(12))
        R(small, "control_%d_%d" % (i, j), .022,
          (x, y, z), (x, y, z + .035), dark)
scene.include("small_console", small)

# The separate panel reference provides the face design but does not establish
# a unique location in the room. This placement is therefore explicitly uncertain.
grid = Asset("Yellow GRID mimic panel")
gx, gy, gz = 4.16, .15, 2.00
B(grid, "yellow_panel", (.045, 1.42, 1.82), (gx, gy, gz), yellow)
line_x = gx - .035

def gridline(name, a, b, radius=.014):
    R(grid, name, radius,
      (line_x, gy + a[0], gz + a[1]),
      (line_x, gy + b[0], gz + b[1]), black)

gridline("main_bus", (.10, -.77), (.10, .77), .018)
for i, z in enumerate((-.48, .08, .55)):
    gridline("cross_%d" % i, (-.29, z), (.43, z))
for i, y in enumerate((-.27, .36)):
    gridline("branch_%d" % i, (y, -.48), (y, .55))
for i, (y, z) in enumerate(((.10, -.70), (.10, .70),
                             (-.27, .08), (.36, .08))):
    R(grid, "red_lamp_%d" % i, .053,
      (line_x - .012, gy + y, gz + z),
      (line_x - .045, gy + y, gz + z), red)
for i, (y, z) in enumerate(((-.27, -.48), (.10, -.48), (.36, -.48),
                             (-.27, .55), (.10, .55), (.36, .55))):
    B(grid, "amber_lamp_%d" % i, (.035, .09, .09),
      (line_x - .025, gy + y, gz + z), amber)
for i in range(4):
    z = gz - .54 + i * .34
    B(grid, "selector_dial_%d" % i, (.016, .17, .17),
      (line_x - .01, gy - .52, z), pale)
    R(grid, "selector_knob_%d" % i, .047,
      (line_x - .02, gy - .52, z),
      (line_x - .065, gy - .52, z), dark)
scene.include("grid_mimic_panel", grid)

fixtures = Asset("Ceiling fluorescent fixtures")
for i, x in enumerate((-2.5, 0, 2.5)):
    B(fixtures, "fixture_%d" % i, (1.55, .38, .035),
      (x, .25, ROOM_H - .035), (1.0, .96, .84))
scene.include("ceiling_fixtures", fixtures)

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
background.inputs["Strength"].default_value = .45

# Preserve the source's portrait aspect for the runner and diagnostics.
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
area_emitter((0, -.2, 3.08), power=1000, size=4.0,
             target=(0, .8, .4), color=(1.0, .95, .87))
area_emitter((-3.0, -3.0, 2.8), power=500, size=3.0,
             target=(-1.0, 1.3, 1.1), color=(1.0, .97, .91))

# Second editable camera, aimed at the console and mimic panel.
bpy.ops.object.camera_add(location=(-.2, -3.5, 2.25))
detail_camera = bpy.context.object
detail_camera.name = "Camera - console and GRID detail"
detail_camera.rotation_euler = (Vector((2.2, 1.2, 1.45)) -
                                detail_camera.location).to_track_quat('-Z', 'Y').to_euler()
detail_camera.data.lens = 35
# The panorama remains the active camera.
panorama = next(obj for obj in sc.objects
                if obj.type == "CAMERA" and obj != detail_camera)
panorama.name = "Camera - room panorama"
sc.camera = panorama

# German labels on the face of the yellow panel.
label_mat = bpy.data.materials.new("GRID label lettering")
label_mat.diffuse_color = (.03, .03, .025, 1)
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
label("Fault label", "FEHLERSTELLE", -.60, -.82, .06)

# Small projection check: full portrait reference coordinates are estimates for
# a room-filling reconstruction, separate from the room-photo crop estimates.
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
    "desk_front_left": (DESK_X - 2.88, DESK_Y - 1.12, .90),
    "desk_back_right": (DESK_X + DESK_W / 2, SURFACE_Y + .68, 1.36),
    "door_top": (2.38, BACK_Y - .12, 2.30),
}

def project_points():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = panorama.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = {}
    for name, p in POINTS.items():
        clip = matrix @ panorama.matrix_world.inverted() @ Vector((*p, 1.0))
        result[name] = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1),
            .5 * (1 - clip.y / clip.w))
    return result

chosen = project_points()
original_rotation = panorama.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2] + .10))
panorama.rotation_euler = (trial_target - panorama.location).to_track_quat('-Z', 'Y').to_euler()
trial = project_points()
panorama.rotation_euler = original_rotation
bpy.context.view_layer.update()
print("Landmark                 reference    chosen projection    upward aim trial")
for name in POINTS:
    print("%-24s %-12s %-20s %s" %
          (name, REFERENCE[name], chosen[name], trial[name]))

# The external runner owns rendering and saving.
