# Reference inventory, estimated from the original 374 x 512 slide:
# The room photograph occupies (0.03, 0.65)-(0.94, 1.00). Its upper and
# left edges crop the room. The meter wall spans approximately
# (0.03, 0.66)-(0.66, 0.87); the long console overlaps its lower portion
# at (0.03, 0.78)-(0.68, 1.00). A dark doorway is near
# (0.68, 0.68)-(0.76, 0.85), and a separate small console is at
# (0.76, 0.76)-(0.94, 0.91). Floor remains visible in the foreground.
# Long desk edges rise to the right; cabinet seams are nearly vertical.
# The separately photographed yellow GRID panel occupies
# (0.03, 0.19)-(0.52, 0.64). Its precise position in the room is uncertain.
#
# Comparison with the last render: the wall begins near y=0.33 in the render,
# while the room photograph begins at y=0.65 in the slide. The foreground
# console spans approximately x=0.00-0.77 and y=0.48-0.72 in the render;
# the photo's console spans x=0.03-0.68 and y=0.78-1.00. These are observed
# contours in different contexts, not a calibrated comparison: the photo
# is a landscape inset, whereas the last render fills a portrait frame.
# The wall grille and desk overlap are recognizable. The rendered desk edge
# rises rightward, as in the photo, but the render exposes a cutaway floor
# edge and a large gray void, and the doorway is obscured by the yellow board.
# The reference crops the room instead of showing its outer shell.
#
# Ranked corrections: (1) remove the conspicuous gray void and cutaway floor
# silhouette by extending the floor and walls outside the camera crop;
# (2) increase room coverage in the portrait view using camera lens and target;
# (3) place the GRID board on the right wall rather than over the doorway,
# preserving the wall meter array and console positions. The panel's position
# remains uncertain because the separate inset does not establish its location.
# The existing cabinet and console geometry has identity scale and translation.
# The camera trial aims lower and uses a modestly longer lens; it should move
# the console lower and enlarge it while protecting the far console corner.
# The numerical comparison retains the previous approximate room-photo anchors;
# these are not estimates of the slide itself, and C is a crop constraint.
# The trial is accepted only if it improves the weighted anchor error without
# excessively worsening the far corner. Printed projections are not visibility.
#
# Expanded SceneAct primitive estimate: room 4, cabinet 123, main console 80,
# doorway 3, independent console 18, GRID 34, fixtures 3: about 265 meshes.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

ROOM_H = 3.4
WALL_Y = 2.35
CAB_X0, CAB_X1 = -4.3, 1.45
CAB_Z0, CAB_Z1 = 0.65, 2.72
CON_X0, CON_X1 = -4.55, 1.38
CON_FRONT, CON_BACK = -1.0, 0.72
CON_TOP_FRONT, CON_TOP_BACK = 0.83, 1.40

CAM_PREVIOUS = ((-6.3, -8.0, 3.35), (-0.4, 0.75, 1.35), 32)
CAM_TRIAL = ((-6.3, -8.0, 3.35), (-0.4, 0.75, 1.20), 34)

wall_col = (0.69, 0.68, 0.64)
panel_col = (0.66, 0.65, 0.61)
ivory = (0.78, 0.77, 0.71)
edge = (0.20, 0.20, 0.19)
black = (0.035, 0.037, 0.035)
yellow = (0.80, 0.57, 0.09)
red = (0.72, 0.025, 0.018)
amber = (0.90, 0.39, 0.015)

scene = Scene("1970s Grid Dispatch Room")

def add_box(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def add_rod(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

# Extended surfaces express the photographic crop; their distant limits are
# uncertain. The right wall remains perpendicular to the rear wall.
room = Asset("Architecture")
add_box(room, "floor", (35, 35, 0.12), (0, -7, -0.06), (0.31, 0.29, 0.26))
add_box(room, "rear_wall", (35, 0.12, 8), (0, WALL_Y + 0.10, 4), wall_col)
add_box(room, "right_wall", (0.12, 35, 8), (4.64, -7, 4), wall_col)
add_box(room, "rear_baseboard", (35, 0.035, 0.13),
        (0, WALL_Y + 0.02, 0.065), (0.25, 0.25, 0.23))
scene.include("Architecture", room)

wall = Asset("Main_meter_wall")
add_box(wall, "cabinet_body", (CAB_X1-CAB_X0, 0.26, CAB_Z1-CAB_Z0),
        ((CAB_X0+CAB_X1)/2, WALL_Y-0.12, (CAB_Z0+CAB_Z1)/2), panel_col)
for i in range(8):
    x = CAB_X0 + i*(CAB_X1-CAB_X0)/7
    add_box(wall, "cabinet_joint_%02d" % i, (0.014, 0.015, 1.98),
            (x, WALL_Y-0.263, 1.69), (0.37, 0.37, 0.34))
add_box(wall, "vent_surround", (1.02, 0.035, 0.63),
        (-1.03, WALL_Y-0.29, 1.92), (0.35, 0.35, 0.32))
for j in range(8):
    add_box(wall, "vent_louver_%02d" % j, (0.89, 0.016, 0.026),
            (-1.03, WALL_Y-0.314, 1.68+j*0.065), black)
meter_xs = [-4.08, -3.76, -3.44, -3.12, -2.80, -2.48, -2.16,
            -0.31, 0.01, 0.33, 0.65, 0.97, 1.29]
for col, x in enumerate(meter_xs):
    for row in range(4):
        z = 1.20 + row*0.32
        add_box(wall, "meter_frame_%02d_%02d" % (col, row),
                (0.235, 0.035, 0.235), (x, WALL_Y-0.29, z), edge)
        add_box(wall, "meter_face_%02d_%02d" % (col, row),
                (0.178, 0.014, 0.178), (x, WALL_Y-0.315, z), ivory)
scene.include("Main_meter_wall", wall)

console = Asset("Long_sloping_control_console")
length = CON_X1-CON_X0
add_box(console, "dark_pedestal", (length-0.16, 1.28, 0.77),
        ((CON_X0+CON_X1)/2, -0.03, 0.385), (0.23, 0.22, 0.20))
add_box(console, "horizontal_writing_surface", (length, 0.43, 0.07),
        ((CON_X0+CON_X1)/2, CON_FRONT+0.215, CON_TOP_FRONT), ivory)
slope_y0, slope_y1 = CON_FRONT+0.39, CON_BACK
slope_z0, slope_z1 = CON_TOP_FRONT+0.025, CON_TOP_BACK
slope_len = math.hypot(slope_y1-slope_y0, slope_z1-slope_z0)
slope_angle = math.degrees(math.atan2(slope_z1-slope_z0, slope_y1-slope_y0))
surface = box((length, slope_len, 0.09),
              center=((CON_X0+CON_X1)/2, (slope_y0+slope_y1)/2,
                      (slope_z0+slope_z1)/2), color=ivory)
surface.turn(axis="+x", degrees=slope_angle)
console.include("inclined_control_surface", surface)

def slope_point(x, t, offset=0):
    a = math.radians(slope_angle)
    return (x, slope_y0+t*(slope_y1-slope_y0)-math.sin(a)*offset,
            slope_z0+t*(slope_z1-slope_z0)+math.cos(a)*offset)

for i in range(9):
    x = CON_X0+0.12+i*(length-0.24)/8
    add_rod(console, "surface_seam_%02d" % i, 0.010,
            slope_point(x, 0.05, 0.055), slope_point(x, 0.95, 0.055),
            (0.34, 0.34, 0.31))
for col in range(20):
    x = CON_X0+0.18+col*(length-0.36)/19
    for row in range(3):
        t = 0.22+row*0.27
        add_rod(console, "control_%02d_%02d" % (col, row),
                0.026 if row != 2 else 0.035,
                slope_point(x, t, 0.063), slope_point(x, t, 0.105), black)
for i in range(8):
    x = CON_X0+0.40+i*(length-0.8)/7
    plate = box((0.27, 0.16, 0.022), center=slope_point(x, 0.82, 0.068),
                color=(0.28, 0.28, 0.26))
    plate.turn(axis="+x", degrees=slope_angle)
    console.include("instrument_plate_%02d" % i, plate)
scene.include("Long_sloping_control_console", console)

door = Asset("Back_wall_doorway")
add_box(door, "dark_recess", (0.66, 0.035, 2.12),
        (2.28, WALL_Y-0.30, 1.18), (0.15, 0.15, 0.14))
add_box(door, "door_inner", (0.46, 0.020, 1.95),
        (2.28, WALL_Y-0.325, 1.18), (0.28, 0.28, 0.26))
add_box(door, "door_window", (0.33, 0.014, 0.60),
        (2.28, WALL_Y-0.342, 1.75), (0.12, 0.14, 0.14))
scene.include("Back_wall_doorway", door)

small = Asset("Right_independent_console")
add_box(small, "pedestal", (1.55, 0.75, 0.75),
        (3.60, 1.35, 0.375), (0.25, 0.24, 0.22))
smalltop = box((1.62, 0.85, 0.09), center=(3.60, 1.34, 0.84), color=ivory)
smalltop.turn(axis="+x", degrees=12)
small.include("inclined_top", smalltop)
for i in range(8):
    for j in range(2):
        x, y = 2.98+i*0.175, 1.14+j*0.29
        z = 0.86+(y-1.34)*math.tan(math.radians(12))
        add_rod(small, "small_control_%02d_%02d" % (i, j), 0.025,
                (x, y, z+0.03), (x, y, z+0.08), black)
scene.include("Right_independent_console", small)

# Panel geometry is built locally facing -Y, then rotated about its center and
# translated to the right wall. This avoids covering the photographed doorway.
grid = Asset("GRID_single_line_mimic_panel")
GW, GH = 1.54, 1.57
add_box(grid, "yellow_panel", (GW, 0.07, GH), (0, 0, 0), yellow)
front_y = -0.045
add_rod(grid, "central_bus", 0.018, (0.25, front_y, -0.66),
        (0.25, front_y, 0.66), black)
for k, zoff in enumerate((-0.40, -0.08, 0.26, 0.54)):
    add_rod(grid, "branch_%02d" % k, 0.014,
            (-0.28, front_y, zoff), (0.48, front_y, zoff), black)
    for j, dx in enumerate((0.04, 0.40)):
        add_box(grid, "amber_indicator_%02d_%02d" % (k, j),
                (0.105, 0.025, 0.105), (dx, front_y-0.016, zoff), amber)
for k in range(5):
    z = 0.53-k*0.25
    add_box(grid, "switch_label_%02d" % k, (0.22, 0.018, 0.18),
            (-0.50, front_y-0.008, z), ivory)
    add_rod(grid, "red_lamp_%02d" % k, 0.056,
            (-0.50, front_y-0.018, z), (-0.50, front_y-0.055, z), red)
for k, zoff in enumerate((-0.56, 0.56)):
    add_box(grid, "breaker_%02d" % k, (0.11, 0.025, 0.14),
            (0.25, front_y-0.020, zoff), red)
for k in range(4):
    z = -0.55+k*0.20
    add_box(grid, "selector_dial_%02d" % k, (0.15, 0.015, 0.15),
            (-0.69, front_y-0.008, z), ivory)
    add_rod(grid, "selector_switch_%02d" % k, 0.045,
            (-0.69, front_y-0.018, z), (-0.69, front_y-0.055, z), black)
grid.turn(axis="+z", degrees=-90, pivot=(0, 0, 0))
grid.move((4.56, 0.55, 2.15))
scene.include("GRID_single_line_mimic_panel", grid)

fixtures = Asset("Ceiling_fluorescent_fixtures")
for i, x in enumerate((-2.7, 0.0, 2.7)):
    add_box(fixtures, "troffer_%02d" % i, (1.65, 0.48, 0.035),
            (x, -0.05, ROOM_H-0.025), (0.88, 0.88, 0.82))
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
background.inputs["Color"].default_value = (0.65, 0.65, 0.63, 1)
background.inputs["Strength"].default_value = 0.24

def emissive(fragment, color, strength):
    mat = bpy.data.materials.new(fragment + "_emissive")
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    for obj in bpy.data.objects:
        if fragment in obj.name and obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(mat)

emissive("red_lamp", (0.8, 0.025, 0.015), 0.7)
emissive("amber_indicator", (1.0, 0.34, 0.015), 0.7)
emissive("troffer", (1.0, 0.96, 0.83), 0.8)

# German labels lie on the panel's inward-facing surface.
def panel_label(text, y, z, size):
    curve = bpy.data.curves.new("Label_" + text, type="FONT")
    curve.body = text
    curve.size = size
    obj = bpy.data.objects.new("Label_" + text, curve)
    sc.collection.objects.link(obj)
    obj.location = (4.49, y, z)
    obj.rotation_euler = (math.radians(90), 0, math.radians(-90))
    mat = bpy.data.materials.get("Panel_label_ink")
    if mat is None:
        mat = bpy.data.materials.new("Panel_label_ink")
        mat.diffuse_color = (0.02, 0.02, 0.018, 1)
    curve.materials.append(mat)

panel_label("NETZ", 0.57, 2.82, 0.085)
panel_label("FEHLERSTELLE", 0.57, 1.48, 0.065)

# Use the original image aspect for comparison. The runner controls rendering.
sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

set_view(*CAM_PREVIOUS[:2], lens=CAM_PREVIOUS[2])
cam = sc.camera
cam.name = "Camera_Panorama"
anchors = [
    ("A cabinet left", (CAB_X0, WALL_Y-0.30, 1.10), (0.08, 0.43), 1.0),
    ("B cabinet right", (CAB_X1, WALL_Y-0.30, 1.10), (0.68, 0.39), 1.0),
    ("C console near left", (CON_X0, CON_FRONT, CON_TOP_FRONT), (0.08, 0.76), 0.5),
    ("D console far right", (CON_X1, CON_BACK, CON_TOP_BACK), (0.68, 0.62), 1.0),
]

def configure_camera(params):
    position, target, lens = params
    cam.location = position
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    bpy.context.view_layer.update()

def project(point):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    if clip.w <= 1e-8:
        return None
    return (0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))

def capture(params):
    configure_camera(params)
    return [project(point) for _, point, _, _ in anchors]

def residual(uv, ref):
    if uv is None:
        return None
    return ((uv[0]-ref[0])*374, (uv[1]-ref[1])*512)

def score(values):
    total = 0.0
    for uv, (_, _, ref, weight) in zip(values, anchors):
        if uv is None:
            return float("inf")
        r = residual(uv, ref)
        total += weight*(r[0]**2+r[1]**2)
    return total

previous = capture(CAM_PREVIOUS)
trial = capture(CAM_TRIAL)
# Protect the far desk corner against a major regression.
old_d = residual(previous[3], anchors[3][2])
new_d = residual(trial[3], anchors[3][2])
protected = (new_d is not None and old_d is not None and
             math.hypot(*new_d) <= math.hypot(*old_d)+10)
chosen_params = CAM_TRIAL if protected and score(trial) < score(previous) else CAM_PREVIOUS
final = capture(chosen_params)
for (name, point, ref, weight), old, test, chosen in zip(anchors, previous, trial, final):
    print(name, "reference", ref,
          "previous", old, "previous residual px", residual(old, ref),
          "trial", test, "trial residual px", residual(test, ref),
          "final", chosen, "final residual px", residual(chosen, ref))
print("Selected camera", chosen_params)

bpy.ops.object.camera_add(location=(-1.8, -5.3, 3.0))
detail_cam = bpy.context.object
detail_cam.name = "Camera_Console_and_GRID_Detail"
detail_target = Vector((2.2, 0.9, 1.55))
detail_cam.rotation_euler = (detail_target-detail_cam.location).to_track_quat("-Z", "Y").to_euler()
detail_cam.data.lens = 42
sc.camera = cam

area_emitter((-2.8, -0.5, 3.15), power=300, size=3.0, target=(-2, 0.7, 0.7))
area_emitter((1.0, 0.0, 3.15), power=300, size=3.0, target=(1, 1, 0.7))
area_emitter((3.4, 0.2, 3.1), power=220, size=2.0, target=(3, 1.5, 1.0))
area_emitter((-4.0, -5.0, 4.5), power=200, size=4.0, target=(-1, 1, 1))
