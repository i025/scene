# Reference inventory and visual anchors (normalized image coordinates, x right, y down):
# The input is a slide containing two photographs; the room occupies roughly
# (0.03, 0.65)-(0.94, 1.00), while the yellow GRID panel is shown separately at
# (0.03, 0.19)-(0.52, 0.64). Its placement inside the room is therefore uncertain.
# Room photo: main cabinet wall at approximately (0.03, 0.66)-(0.66, 0.88);
# long console at (0.03, 0.78)-(0.68, 0.99), overlapping the cabinet wall;
# small right console at (0.76, 0.76)-(0.94, 0.90); dark doorway or recess near
# (0.68, 0.68)-(0.76, 0.84). Floor fills the lower right.
# The long console's leading edge rises toward the right; its long rear edge
# also rises toward the right. Cabinet seams are nearly vertical. The room
# corners and ceiling are partly outside the photo, so their extent is uncertain.
# The inset panel has a yellow rectangular face, black single-line diagram,
# red round lamps, amber square lamps, black switches and small German labels.
#
# Projection anchors used below, estimated from the room photograph after
# mapping that photograph into the full output frame:
# A: left end of the cabinet/console junction, approximately (0.08, 0.43)
# B: right end of the cabinet/console junction, approximately (0.68, 0.39)
# C: nearest left console corner, approximately (0.08, 0.76)
# D: right console corner, approximately (0.68, 0.62)
# E: doorway top, approximately (0.76, 0.21), uncertain.
# These are approximate visual correspondences, not calibrated points. They
# describe the room photo, enlarged to fill the output, rather than the slide.
#
# Estimated expanded SceneAct primitives: architecture ~12, main wall and
# ventilation ~110, main console ~145, small console ~30, GRID panel ~60,
# lights and fittings ~8: about 365 meshes. Text is added using bpy.
# The adjustable camera parameters and principal asset dimensions are below.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

# Dimensions are plausible ergonomic estimates, not measured dimensions.
ROOM_W = 9.4
ROOM_D = 6.3
ROOM_H = 3.4
WALL_Y = 2.35
CAB_X0, CAB_X1 = -4.3, 1.45
CAB_Z0, CAB_Z1 = 0.65, 2.72
CON_X0, CON_X1 = -4.55, 1.38
CON_FRONT, CON_BACK = -1.0, 0.72
CON_TOP_FRONT, CON_TOP_BACK = 0.83, 1.40
CAM_POS = (-7.7, -10.5, 5.4)
CAM_TARGET = (-0.15, 0.60, 1.23)
CAM_LENS = 34
ASPECT_X, ASPECT_Y = 1920, 1080

cream = (0.72, 0.70, 0.64)
wall_col = (0.72, 0.72, 0.69)
panel_col = (0.73, 0.72, 0.67)
edge = (0.24, 0.25, 0.24)
black = (0.055, 0.060, 0.058)
ivory = (0.88, 0.87, 0.80)
floor_col = (0.37, 0.35, 0.32)
yellow = (0.90, 0.69, 0.16)
red = (0.72, 0.055, 0.035)
amber = (0.96, 0.49, 0.06)

scene = Scene("1970s Grid Dispatch Room")

def add_box(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def add_rod(asset, name, radius, start, end, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

# Room shell. The far and right walls meet behind the visible equipment.
room = Asset("Architecture")
add_box(room, "floor", (ROOM_W, ROOM_D, 0.12), (0, 0, -0.06), floor_col)
add_box(room, "rear_wall", (ROOM_W, 0.12, ROOM_H), (0, WALL_Y + 0.10, ROOM_H / 2), wall_col)
add_box(room, "right_wall", (0.12, ROOM_D, ROOM_H), (4.64, -0.30, ROOM_H / 2), wall_col)
add_box(room, "ceiling", (ROOM_W, ROOM_D, 0.10), (0, -0.30, ROOM_H + 0.05), (0.78, 0.78, 0.74))
add_box(room, "rear_baseboard", (ROOM_W, 0.035, 0.13), (0, WALL_Y + 0.02, 0.065), (0.32, 0.32, 0.30))
scene.include("Architecture", room)

# Continuous wall cabinet, with panel joints and dense square meter arrays.
wall = Asset("Main_meter_wall")
add_box(wall, "cabinet_body", (CAB_X1-CAB_X0, 0.26, CAB_Z1-CAB_Z0),
        ((CAB_X0+CAB_X1)/2, WALL_Y-0.12, (CAB_Z0+CAB_Z1)/2), panel_col)
for i in range(8):
    x = CAB_X0 + i * (CAB_X1-CAB_X0) / 7
    add_box(wall, "cabinet_joint_%02d" % i, (0.014, 0.015, 1.98), (x, WALL_Y-0.263, 1.69), (0.46, 0.46, 0.43))
# The wide ventilation grille interrupts the instrument field near the middle.
add_box(wall, "vent_surround", (1.02, 0.035, 0.63), (-1.03, WALL_Y-0.29, 1.92), (0.43, 0.43, 0.40))
for j in range(8):
    add_box(wall, "vent_louver_%02d" % j, (0.89, 0.016, 0.026),
            (-1.03, WALL_Y-0.314, 1.68 + j*0.065), black)
# Two banks of meters, leaving a distinct central opening for the grille.
meter_xs = [-4.08, -3.76, -3.44, -3.12, -2.80, -2.48, -2.16,
            -0.31, 0.01, 0.33, 0.65, 0.97, 1.29]
for col, x in enumerate(meter_xs):
    for row in range(4):
        z = 1.20 + row*0.32
        add_box(wall, "meter_frame_%02d_%02d" % (col, row), (0.235, 0.035, 0.235),
                (x, WALL_Y-0.29, z), edge)
        add_box(wall, "meter_face_%02d_%02d" % (col, row), (0.178, 0.014, 0.178),
                (x, WALL_Y-0.315, z), ivory)
        # A short needle makes the meter legible without detailed dial geometry.
        add_rod(wall, "meter_needle_%02d_%02d" % (col, row), 0.007,
                (x-0.040, WALL_Y-0.326, z-0.035),
                (x+0.035, WALL_Y-0.326, z+0.030), black)
scene.include("Main_meter_wall", wall)

# Long control desk: lower body, front writing shelf and inclined operating face.
console = Asset("Long_sloping_control_console")
length = CON_X1-CON_X0
add_box(console, "pedestal", (length-0.16, 1.28, 0.77),
        ((CON_X0+CON_X1)/2, -0.03, 0.385), (0.38, 0.37, 0.34))
add_box(console, "horizontal_writing_surface", (length, 0.43, 0.07),
        ((CON_X0+CON_X1)/2, CON_FRONT+0.215, CON_TOP_FRONT), ivory)

# A shallow rectangular slab rotated about X to span the sloping face.
slope_y0 = CON_FRONT + 0.39
slope_y1 = CON_BACK
slope_z0 = CON_TOP_FRONT + 0.025
slope_z1 = CON_TOP_BACK
slope_len = math.hypot(slope_y1-slope_y0, slope_z1-slope_z0)
slope_angle = math.degrees(math.atan2(slope_z1-slope_z0, slope_y1-slope_y0))
surface = box((length, slope_len, 0.09),
              center=((CON_X0+CON_X1)/2, (slope_y0+slope_y1)/2, (slope_z0+slope_z1)/2),
              color=ivory)
surface.turn(axis="+x", degrees=slope_angle)
console.include("inclined_control_surface", surface)

def slope_point(x, t, offset=0.0):
    y = slope_y0 + t*(slope_y1-slope_y0)
    z = slope_z0 + t*(slope_z1-slope_z0)
    a = math.radians(slope_angle)
    return (x, y-math.sin(a)*offset, z+math.cos(a)*offset)

# Panel division lines and distinct rows of controls on the slope.
for i in range(9):
    x = CON_X0 + 0.12 + i*(length-0.24)/8
    add_rod(console, "surface_seam_%02d" % i, 0.010,
            slope_point(x, 0.05, 0.055), slope_point(x, 0.95, 0.055), (0.43,0.43,0.40))
for col in range(20):
    x = CON_X0 + 0.18 + col*(length-0.36)/19
    for row in range(3):
        t = 0.22 + row*0.27
        p = slope_point(x, t, 0.063)
        q = slope_point(x, t, 0.105)
        add_rod(console, "control_%02d_%02d" % (col,row),
                0.026 if row != 2 else 0.035, p, q, black if (col+row)%5 else (0.32,0.30,0.26))
# Larger rectangular instrument plates, aligned with the inclined surface.
for i in range(8):
    x = CON_X0 + 0.40 + i*(length-0.8)/7
    p = slope_point(x, 0.82, 0.068)
    plate = box((0.27, 0.16, 0.022), center=p, color=(0.43,0.43,0.40))
    plate.turn(axis="+x", degrees=slope_angle)
    console.include("instrument_plate_%02d" % i, plate)
scene.include("Long_sloping_control_console", console)

# Back-right doorway/recess, represented as a dark inset on the wall.
door = Asset("Back_wall_doorway")
add_box(door, "dark_recess", (0.66, 0.035, 2.12), (2.28, WALL_Y-0.30, 1.18), (0.20,0.20,0.19))
add_box(door, "door_inner", (0.46, 0.020, 1.95), (2.28, WALL_Y-0.325, 1.18), (0.34,0.34,0.32))
add_box(door, "door_window", (0.33, 0.014, 0.60), (2.28, WALL_Y-0.342, 1.75), (0.18,0.20,0.20))
scene.include("Back_wall_doorway", door)

# Independent small desk to the right of the doorway.
small = Asset("Right_independent_console")
add_box(small, "pedestal", (1.55, 0.75, 0.75), (3.60, 1.35, 0.375), (0.41,0.40,0.37))
smalltop = box((1.62, 0.85, 0.09), center=(3.60, 1.34, 0.84), color=ivory)
smalltop.turn(axis="+x", degrees=12)
small.include("inclined_top", smalltop)
for i in range(8):
    for j in range(2):
        x = 2.98 + i*0.175
        y = 1.14 + j*0.29
        z = 0.86 + (y-1.34)*math.tan(math.radians(12))
        add_rod(small, "small_control_%02d_%02d" % (i,j), 0.025,
                (x,y,z+0.03), (x,y,z+0.08), black)
scene.include("Right_independent_console", small)

# Yellow GRID board is mounted above the right console; its room position is
# uncertain because it is a separate photograph in the reference slide.
grid = Asset("GRID_single_line_mimic_panel")
GX, GY, GZ = 3.63, WALL_Y-0.30, 2.26
GW, GH = 1.54, 1.57
add_box(grid, "yellow_panel", (GW, 0.07, GH), (GX, GY, GZ), yellow)
front_y = GY - 0.045
# Main vertical bus and horizontal branches.
add_rod(grid, "central_bus", 0.018, (GX+0.25,front_y,GZ-0.66), (GX+0.25,front_y,GZ+0.66), black)
for k, zoff in enumerate((-0.40, -0.08, 0.26, 0.54)):
    add_rod(grid, "branch_%02d" % k, 0.014,
            (GX-0.28, front_y, GZ+zoff), (GX+0.48, front_y, GZ+zoff), black)
    add_box(grid, "amber_indicator_%02d" % k, (0.105,0.025,0.105),
            (GX+0.04,front_y-0.016,GZ+zoff), amber)
    add_box(grid, "amber_indicator_right_%02d" % k, (0.105,0.025,0.105),
            (GX+0.40,front_y-0.016,GZ+zoff), amber)
for k in range(5):
    z = GZ+0.53-k*0.25
    add_box(grid, "switch_label_%02d" % k, (0.22,0.018,0.18),
            (GX-0.50,front_y-0.008,z), ivory)
    add_rod(grid, "red_lamp_%02d" % k, 0.056,
            (GX-0.50,front_y-0.018,z), (GX-0.50,front_y-0.055,z), red)
for k, zoff in enumerate((-0.56, 0.56)):
    add_box(grid, "breaker_%02d" % k, (0.11,0.025,0.14),
            (GX+0.25,front_y-0.020,GZ+zoff), red)
for k in range(4):
    z = GZ-0.55+k*0.20
    add_rod(grid, "selector_switch_%02d" % k, 0.045,
            (GX-0.69,front_y-0.012,z), (GX-0.69,front_y-0.055,z), black)
scene.include("GRID_single_line_mimic_panel", grid)

# Visible ceiling light fixtures.
fixtures = Asset("Ceiling_fluorescent_fixtures")
for x in (-2.7, 0.0, 2.7):
    add_box(fixtures, "troffer_%s" % str(x), (1.65, 0.48, 0.035),
            (x, -0.05, ROOM_H-0.025), (0.91,0.91,0.85))
scene.include("Ceiling_fluorescent_fixtures", fixtures)

realize(scene)

# Make emissive indicator faces and troffers recognizable in both views.
def set_emission_by_name(name_fragment, color, strength):
    mat = bpy.data.materials.new(name_fragment + "_emissive")
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color, 1)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color, 1)
    for obj in bpy.data.objects:
        if name_fragment in obj.name and obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(mat)

set_emission_by_name("red_lamp", (0.8, 0.025, 0.015), 1.0)
set_emission_by_name("amber_indicator", (1.0, 0.34, 0.015), 0.8)
set_emission_by_name("troffer", (1.0, 0.96, 0.83), 1.5)

# German functional labels, on the yellow panel, facing the room.
def label(text, location, size=0.075):
    curve = bpy.data.curves.new("Label_" + text, type="FONT")
    curve.body = text
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new("Label_" + text, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    mat = bpy.data.materials.get("Panel_label_ink")
    if mat is None:
        mat = bpy.data.materials.new("Panel_label_ink")
        mat.diffuse_color = (0.03, 0.03, 0.025, 1)
    curve.materials.append(mat)

label("NETZ", (GX-0.02, front_y-0.06, GZ+0.67), 0.085)
label("FEHLERSTELLE", (GX-0.02, front_y-0.06, GZ-0.67), 0.065)

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
background.inputs["Color"].default_value = (0.75, 0.76, 0.75, 1)
background.inputs["Strength"].default_value = 0.45

sc.render.resolution_x = ASPECT_X
sc.render.resolution_y = ASPECT_Y
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
panorama_cam = sc.camera
panorama_cam.name = "Camera_Panorama"

# A short numerical comparison between the initial camera and a small lens
# trial. The reference estimates above remain fixed; the lower total residual
# chooses between these two candidates. Geometry landmarks are actual points
# on the corresponding desk, cabinet and recess.
from mathutils import Vector
anchors = [
    ("A cabinet left", (CAB_X0, WALL_Y-0.30, 1.10), (0.08, 0.43)),
    ("B cabinet right", (CAB_X1, WALL_Y-0.30, 1.10), (0.68, 0.39)),
    ("C console near left", (CON_X0, CON_FRONT, CON_TOP_FRONT), (0.08, 0.76)),
    ("D console far right", (CON_X1, CON_BACK, CON_TOP_BACK), (0.68, 0.62)),
]
def project(point):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    proj = sc.camera.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    clip = proj @ sc.camera.matrix_world.inverted() @ Vector((*point, 1))
    if clip.w <= 1e-8:
        return None
    return (0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))

def capture(lens):
    panorama_cam.data.lens = lens
    return [project(p) for _, p, _ in anchors]

previous = capture(CAM_LENS)
trial = capture(CAM_LENS + 2)
def score(projections):
    total = 0
    for uv, (_, _, ref) in zip(projections, anchors):
        if uv is None:
            return float("inf")
        total += ((uv[0]-ref[0])*ASPECT_X)**2 + ((uv[1]-ref[1])*ASPECT_Y)**2
    return total
chosen_lens = CAM_LENS + 2 if score(trial) < score(previous) else CAM_LENS
final = capture(chosen_lens)
for (name, point, ref), old, candidate, chosen in zip(anchors, previous, trial, final):
    def pix_res(uv):
        return None if uv is None else (
            round((uv[0]-ref[0])*ASPECT_X, 1),
            round((uv[1]-ref[1])*ASPECT_Y, 1))
    print(name, "ref", ref, "previous", old, "candidate", candidate,
          "previous residual px", pix_res(old), "candidate residual px", pix_res(candidate),
          "chosen residual px", pix_res(chosen))
print("Selected panorama lens", chosen_lens)

# A second named camera is available for later editing and close inspection.
bpy.ops.object.camera_add(location=(-1.8, -5.3, 3.35))
detail_cam = bpy.context.object
detail_cam.name = "Camera_Console_and_GRID_Detail"
detail_target = Vector((1.3, 1.0, 1.45))
detail_cam.rotation_euler = (detail_target-detail_cam.location).to_track_quat("-Z", "Y").to_euler()
detail_cam.data.lens = 42
sc.camera = panorama_cam

area_emitter((-2.8, -0.5, 3.15), power=500, size=3.0, target=(-2, 0.7, 0.7))
area_emitter((1.0, 0.0, 3.15), power=500, size=3.0, target=(1, 1, 0.7))
area_emitter((3.4, 0.2, 3.1), power=350, size=2.0, target=(3, 1.5, 1.0))
area_emitter((-4.0, -5.0, 4.5), power=450, size=4.0, target=(-1, 1, 1))
