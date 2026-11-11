# Reference inventory, estimated from the lower photograph in the slide:
# - The photograph occupies approximately x=.03-.94, y=.65-1.00 of the slide.
# - A long console crosses the foreground from the left edge toward the center
#   right; its pale sloping control surface overlaps the instrument wall.
# - The pale instrument wall fills the left and middle background. Its square
#   meters are arranged in rows and columns, with a dark horizontal grille.
# - A doorway and a smaller independent console occupy the right background.
#   Floor is visible in the right foreground. Wall/floor junctions are partly
#   obscured by the furniture.
# - The yellow GRID panel appears in a separate photograph above the room image;
#   its actual location in the room is uncertain. It is placed on the right
#   wall, where it can also be viewed using the second camera.
#
# Comparison with the previous render:
# 1. The ceiling and right wall formed a large opaque shell in the foreground;
#    the control-room interior was largely hidden. The ceiling is omitted from
#    the camera-facing shell and the panorama camera is moved inside the room.
#    This should expose the background bank and foreground console.
# 2. The rendered desk occupied roughly x=.15-.68, y=.44-.62 of the full image,
#    while the photograph shows the desk spanning most of its lower half.
#    Moving the camera closer and lower should enlarge it and reduce the
#    excessive downward angle.
# 3. The numerical projections from the previous program used a landscape
#    aspect, while the supplied image and actual rendering are portrait.
#    Those projections therefore do not establish visible pixel coverage.
#    The diagnostics below use 374 x 512 and identifiable geometry corners.
# 4. The yellow panel and independent console may have been occluded by the
#    shell, so the scene keeps one of each rather than adding duplicates.
#    The wall bank, console, panel, grille, doorway and right console retain
#    separate editable SceneAct assets.
#
# Approximate primitive count: architecture 8, bank 130, console 105,
# small console 18, GRID panel 56, ceiling lights 4: about 321 meshes.
# Boxes and rods each emit one primitive; no Boolean or fillet expansions.
#
# Camera and geometry parameters are independent. The image is a collage, so
# anchor coordinates below estimate the corresponding positions in a hypothetical
# full-frame room view; they are not calibrated slide coordinates.

from sceneact import *
import bpy
import math
from mathutils import Vector

IMAGE_WIDTH, IMAGE_HEIGHT = 374, 512
CAMERA_POSITION = (-5.6, -8.5, 3.0)
CAMERA_TARGET = (0.0, 1.35, 1.25)
CAMERA_LENS = 29
ROOM_W, ROOM_D, ROOM_H = 9.0, 7.0, 3.3
DESK_LENGTH = 6.3
DESK_CENTER_X = -1.05
DESK_CENTER_Y = -0.35

scene = Scene("1970s dispatch control room")
wall = (.73, .71, .67)
floor_color = (.32, .30, .27)
cabinet = (.64, .63, .59)
face = (.80, .79, .74)
dark = (.105, .10, .09)
black = (.025, .025, .023)
yellow = (.90, .65, .10)
red = (.72, .035, .025)
amber = (1.0, .43, .025)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_rod(parent, name, radius, start, end, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

# The camera-facing wall and ceiling are omitted so they cannot obscure the
# photographed interior. Back and right walls preserve the visible enclosure.
room = Asset("Architecture")
add_box(room, "floor", (ROOM_W, ROOM_D, .12), (0, 0, -.06), floor_color)
add_box(room, "back_wall", (ROOM_W, .12, ROOM_H),
        (0, ROOM_D/2, ROOM_H/2), wall)
add_box(room, "right_wall", (.12, ROOM_D, ROOM_H),
        (ROOM_W/2, 0, ROOM_H/2), wall)
add_box(room, "back_baseboard", (ROOM_W, .04, .12),
        (0, ROOM_D/2-.09, .06), (.43, .41, .38))
# Door on the back wall, a visible dark rectangle with a pale surround.
add_box(room, "door_frame", (.83, .08, 2.08), (3.05, 3.40, 1.04), face)
add_box(room, "door_recess", (.64, .04, 1.88),
        (3.05, 3.34, 1.02), (.23, .22, .20))
add_box(room, "door_window", (.44, .025, .76),
        (3.05, 3.31, 1.42), (.37, .36, .33))
scene.include("architecture", room)

# Instrument bank: pale cabinet, repeated framed square instruments, and vent.
bank = Asset("Main_wall_instrument_bank")
add_box(bank, "cabinet_body", (6.45, .34, 2.45),
        (-1.18, 3.24, 1.34), cabinet)
add_box(bank, "upper_fascia", (6.45, .045, .43),
        (-1.18, 3.045, 2.35), face)
for i in range(7):
    x = -4.05 + i*.47
    for j in range(4):
        z = .55 + j*.40
        add_box(bank, "meter_frame_%d_%d" % (i, j), (.32, .035, .31),
                (x, 3.035, z), dark)
        add_box(bank, "meter_face_%d_%d" % (i, j), (.26, .022, .25),
                (x, 3.01, z), face)
        add_rod(bank, "meter_needle_%d_%d" % (i, j), .007,
                (x-.05, 2.995, z-.04), (x+.035, 2.995, z+.05), dark)
add_box(bank, "vent_opening", (1.20, .035, .79),
        (.12, 3.035, 1.29), dark)
for j in range(7):
    add_box(bank, "vent_slat_%d" % j, (1.13, .025, .035),
            (.12, 3.005, .99+j*.10), face)
for i in range(4):
    for j in range(4):
        x, z = 1.02+i*.30, .64+j*.37
        add_box(bank, "right_meter_frame_%d_%d" % (i, j),
                (.22, .035, .26), (x, 3.035, z), dark)
        add_box(bank, "right_meter_face_%d_%d" % (i, j),
                (.17, .022, .21), (x, 3.01, z), face)
scene.include("wall_instruments", bank)

# The desk has a dark pedestal, horizontal ledge and raised inclined panel.
desk = Asset("Long_sloping_operator_console")
add_box(desk, "pedestal", (DESK_LENGTH, 1.05, .69),
        (DESK_CENTER_X, DESK_CENTER_Y+.10, .36), (.34, .32, .29))
add_box(desk, "writing_ledge", (DESK_LENGTH+.12, .53, .09),
        (DESK_CENTER_X, DESK_CENTER_Y-.65, .78), face)
angle = math.degrees(math.atan2(.48, 1.08))
panel = box((DESK_LENGTH, 1.19, .095),
            center=(DESK_CENTER_X, DESK_CENTER_Y+.035, 1.08), color=face)
panel.turn(axis="x", degrees=angle)
desk.include("sloped_control_surface", panel)
add_box(desk, "rear_edge", (DESK_LENGTH, .07, .09),
        (DESK_CENTER_X, DESK_CENTER_Y+.58, 1.34), cabinet)

# Dark control groups distributed over the inclined surface.
normal_y = -math.sin(math.radians(angle))
normal_z = math.cos(math.radians(angle))
for i in range(16):
    x = DESK_CENTER_X - 2.95 + i*.39
    for j, t in enumerate((.16, .36, .57, .78, .92)):
        y = DESK_CENTER_Y-.50 + 1.08*t
        z = .845 + .48*t
        add_rod(desk, "control_%d_%d" % (i, j), .026 if j != 2 else .038,
                (x, y, z), (x, y+normal_y*.055, z+normal_z*.055),
                dark if (i+j)%7 else red)
    if i % 2 == 0:
        y = DESK_CENTER_Y+.07
        z = 1.10
        add_rod(desk, "large_dial_%d" % i, .061,
                (x+.12, y, z), (x+.12, y+normal_y*.035, z+normal_z*.035),
                dark)
scene.include("main_console", desk)

small = Asset("Right_independent_console")
add_box(small, "base", (1.35, .78, .78), (3.58, 2.27, .39), cabinet)
top = box((1.38, .84, .08), center=(3.58, 2.27, .86), color=face)
top.turn(axis="x", degrees=15)
small.include("sloped_top", top)
for i in range(5):
    for j in range(3):
        x = 3.08+i*.24
        y = 1.99+j*.23
        z = .91+(y-2.27)*math.tan(math.radians(15))
        add_rod(small, "switch_%d_%d" % (i, j), .027,
                (x, y, z), (x, y-.01, z+.05), dark)
scene.include("independent_console", small)

# GRID panel is one separate asset, mounted on the right return. Its placement
# within this room is uncertain because the source panel is a separate image.
grid = Asset("Yellow_GRID_mimic_panel")
GX, GY, GZ = 4.40, .95, 1.95
add_box(grid, "yellow_backboard", (.08, 1.70, 1.65),
        (GX, GY, GZ), yellow)

def wire(name, points):
    for i in range(len(points)-1):
        a, b = points[i], points[i+1]
        add_rod(grid, "%s_%d" % (name, i), .017,
                (GX-.055, GY+a[0], GZ+a[1]),
                (GX-.055, GY+b[0], GZ+b[1]), black)

wire("main_bus", [(0, -.73), (0, .73)])
wire("upper_loop", [(0, .43), (-.30, .43), (-.30, .11),
                    (.28, .11), (.28, .43), (0, .43)])
wire("lower_loop", [(0, .02), (-.30, .02), (-.30, -.28),
                    (.28, -.28), (.28, .02), (0, .02)])
wire("left_branch", [(0, -.39), (-.38, -.39), (-.38, -.53)])
wire("right_branch", [(0, -.39), (.38, -.39), (.38, -.53)])
for i, (dy, dz) in enumerate([
        (-.22,.27), (-.07,.27), (.08,.27), (.22,.27),
        (-.22,-.13), (-.07,-.13), (.08,-.13), (.22,-.13),
        (-.38,-.53), (.38,-.53)]):
    add_box(grid, "amber_frame_%d" % i, (.035, .12, .12),
            (GX-.075, GY+dy, GZ+dz), black)
    add_box(grid, "amber_lamp_%d" % i, (.025, .08, .08),
            (GX-.10, GY+dy, GZ+dz), amber)
for i, (dy, dz) in enumerate([
        (0,.60), (0,-.65), (-.59,.47), (-.59,.23),
        (-.59,-.02), (-.59,-.27), (.59,.43)]):
    add_rod(grid, "red_indicator_%d" % i, .055,
            (GX-.06, GY+dy, GZ+dz), (GX-.12, GY+dy, GZ+dz), red)
for i, dz in enumerate((.36, .02, -.34, -.58)):
    # Pale dial face under each dark selector knob.
    add_rod(grid, "selector_dial_%d" % i, .075,
            (GX-.055, GY-.69, GZ+dz), (GX-.075, GY-.69, GZ+dz), face)
    add_rod(grid, "selector_knob_%d" % i, .043,
            (GX-.075, GY-.69, GZ+dz), (GX-.14, GY-.69, GZ+dz), black)
scene.include("grid_mimic", grid)

fixtures = Asset("Fluorescent_troffers")
for i, x in enumerate((-2.3, .4)):
    add_box(fixtures, "housing_%d" % i, (1.55, .42, .04),
            (x, 1.0, ROOM_H-.04), cabinet)
    add_box(fixtures, "diffuser_%d" % i, (1.40, .32, .025),
            (x, 1.0, ROOM_H-.07), (.95, .94, .89))
scene.include("ceiling_lights", fixtures)

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
background.inputs["Color"].default_value = (.65, .63, .59, 1)
background.inputs["Strength"].default_value = .35

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
camera = sc.camera
camera.name = "Camera_Panorama"

# An editable second view is provided for close inspection of the equipment.
bpy.ops.object.camera_add(location=(2.0, -4.0, 2.6))
detail = bpy.context.object
detail.name = "Camera_Console_GRID_Closeup"
detail.rotation_euler = (
    Vector((2.7, .9, 1.45))-detail.location
).to_track_quat("-Z", "Y").to_euler()
detail.data.lens = 35
sc.camera = camera

area_emitter((-1, -.8, 3.05), power=650, size=4.0, target=(-1, 2, 1))
area_emitter((2.5, 1, 3.0), power=350, size=3.0, target=(2, 2, 1))
area_emitter((-3, 1, 2.9), power=300, size=2.5, target=(-2, 2.7, 1.2))

def grid_label(name, text, y, z, size):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (GX-.13, GY+y, GZ+z)
    obj.rotation_euler = (math.pi/2, 0, -math.pi/2)

grid_label("label_fault", "FEHLER-STELLE K", .08, .56, .042)
grid_label("label_switch", "SCHALTER", -.72, -.72, .040)

def emitter_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        if "Emission Color" in shader.inputs:
            shader.inputs["Emission Color"].default_value = (*color, 1)
            shader.inputs["Emission Strength"].default_value = strength
        elif "Emission" in shader.inputs:
            shader.inputs["Emission"].default_value = (*color, 1)
    return mat

# SceneAct assets remain editable; assign emissive material by the generated
# semantic object names when those names are available.
red_mat = emitter_material("Indicator red", (.65, .025, .01), 1.0)
amber_mat = emitter_material("Indicator amber", (1, .35, .015), 1.0)
light_mat = emitter_material("Fluorescent diffuser", (.95, .91, .80), 1.0)
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    n = obj.name.lower()
    mat = None
    if "red_indicator" in n:
        mat = red_mat
    elif "amber_lamp" in n:
        mat = amber_mat
    elif "diffuser" in n:
        mat = light_mat
    if mat:
        obj.data.materials.clear()
        obj.data.materials.append(mat)

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass

# Geometry diagnostic at the original portrait aspect. A projection is not a
# visibility test: an anchor may be occluded even when it lies in the frame.
anchors = [
    ("bank_upper_left", (-4.405, 3.045, 2.565), (.03, .25)),
    ("bank_upper_right", (2.045, 3.045, 2.565), (.64, .25)),
    ("vent_upper_left", (-.48, 3.005, 1.685), (.30, .40)),
    ("desk_front_left", (-4.26, -.615-0.65, .825), (.03, .79)),
    ("desk_front_right", (2.16, -.615-0.65, .825), (.70, .73)),
    ("door_top", (3.05, 3.31, 2.08), (.76, .32)),
    ("small_console_front", (4.255, 1.85, .82), (.92, .62)),
    ("grid_upper_corner", (4.345, 1.80, 2.775), (.94, .30)),
]

def diagnostic(cam):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(
        depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT, scale_x=1, scale_y=1)
    view = cam.matrix_world.inverted()
    result = []
    for name, point, ref in anchors:
        clip = proj @ view @ Vector((*point, 1.0))
        if clip.w <= 0:
            result.append(
                '{"anchor":"%s","reference":[%.4f,%.4f],'
                '"projection":null,"residual":null,"behind_camera":true}'
                % (name, ref[0], ref[1]))
        else:
            u = .5*(clip.x/clip.w+1)
            v = .5*(1-clip.y/clip.w)
            result.append(
                '{"anchor":"%s","reference":[%.4f,%.4f],'
                '"projection":[%.4f,%.4f],"residual":[%.4f,%.4f]}'
                % (name, ref[0], ref[1], u, v, u-ref[0], v-ref[1]))
    return "[" + ",".join(result) + "]"

print("ANCHOR_DIAGNOSTIC " + diagnostic(camera))
