# Reference inventory and visual anchors, estimated from the supplied composite:
# - The control-room photograph occupies the lower portion of the reference.
#   Its back wall has pale rectangular cabinets and a regular grid of square
#   instruments; a dark horizontal ventilation grille is near its center.
# - A long foreground console runs diagonally across the photograph, from the
#   cropped lower-left toward the back-right. Its light sloping control panels
#   contain many dark switches and meters; a dark base supports them.
# - A smaller pale console stands against the right wall, with a dark base.
# - The yellow GRID board shown above the room photograph is a separate reference
#   to be incorporated into the room; its exact original room position is unknown.
# - The room photograph's important relative anchors, normalized to that photograph:
#   back-wall upper-left (0.00, 0.00), grille center (0.35, 0.36),
#   console near-left contour (0.03, 0.89), console far-right end (0.70, 0.40),
#   small console top (0.90, 0.43). These are approximate visual correspondences.
# - Dominant edges: back wall is nearly horizontal; the console long edges rise
#   strongly toward the right; cabinet verticals are nearly vertical.
# - The console overlaps the lower wall instruments. Rear corners and ceiling are
#   partially cropped, so the unobserved extent of the room is uncertain.
#
# Expanded geometry estimate: architecture ~8 boxes; wall cabinets and instruments
# ~125 boxes; main console body and controls ~150 boxes/rods; right console ~35;
# GRID board and diagram ~55; lights ~5. Total approximately 380 primitives.
# Tiny labels and repeated markings are intentionally simplified.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s_Grid_Control_Room")

# Major room and console parameters, independently editable.
ROOM_W = 9.2
ROOM_D = 6.7
ROOM_H = 3.35
CONSOLE_X0, CONSOLE_X1 = -4.25, 2.20
CONSOLE_Y = -0.65
CONSOLE_Z = 0.90
CAMERA_POSITION = (-7.5, -10.5, 5.1)
CAMERA_TARGET = (-0.15, 1.0, 1.38)
CAMERA_LENS = 35

wall = (0.73, 0.71, 0.66)
wall_light = (0.82, 0.80, 0.75)
cabinet = (0.73, 0.72, 0.68)
panel = (0.79, 0.78, 0.72)
paper = (0.87, 0.85, 0.78)
dark = (0.12, 0.12, 0.11)
base = (0.22, 0.21, 0.19)
yellow = (0.95, 0.70, 0.13)
red = (0.75, 0.035, 0.025)
amber = (0.95, 0.48, 0.035)
black = (0.045, 0.045, 0.04)

architecture = Asset("Architecture")
architecture.include("Floor", box((ROOM_W, ROOM_D, 0.12), (0, 0, -0.06), (0.38, 0.36, 0.32)))
architecture.include("Back_wall", box((ROOM_W, 0.12, ROOM_H), (0, 3.3, ROOM_H/2), wall_light))
architecture.include("Right_wall", box((0.12, ROOM_D, ROOM_H), (4.6, 0, ROOM_H/2), wall))
architecture.include("Ceiling", box((ROOM_W, ROOM_D, 0.10), (0, 0, ROOM_H), wall_light))
architecture.include("Back_baseboard", box((ROOM_W, 0.05, 0.16), (0, 3.20, 0.08), base))
scene.include("Architecture", architecture)

# Back wall instrument bank: regular cabinet bays and visible square instruments.
bank = Asset("Main_wall_instrument_bank")
bank.include("Cabinet_backing", box((6.5, 0.16, 2.45), (-1.15, 3.18, 1.48), cabinet))
for i in range(9):
    x = -4.15 + i * 0.76
    bank.include("Cabinet_seam_%02d" % i,
                 box((0.015, 0.018, 2.35), (x, 3.085, 1.50), (0.41, 0.40, 0.37)))
# Left and right clusters; center is occupied by the ventilation grille.
for col in list(range(5)) + list(range(8, 11)):
    x = -3.92 + col * 0.49
    for row in range(4):
        z = 1.12 + row * 0.40
        bank.include("Meter_frame_%02d_%02d" % (col, row),
                     box((0.31, 0.035, 0.29), (x, 3.065, z), dark))
        bank.include("Meter_face_%02d_%02d" % (col, row),
                     box((0.245, 0.012, 0.225), (x, 3.040, z), paper))
        bank.include("Meter_needle_%02d_%02d" % (col, row),
                     box((0.012, 0.008, 0.095), (x + 0.01, 3.030, z), dark))
bank.include("Grille_surround", box((1.30, 0.045, 0.74), (-1.12, 3.05, 1.72), panel))
for j in range(8):
    bank.include("Grille_slit_%02d" % j,
                 box((1.13, 0.02, 0.035), (-1.12, 3.018, 1.46 + j*0.073), dark))
scene.include("Main_wall_instrument_bank", bank)

# Main console: a horizontal writing shelf in front of an inclined control face.
console = Asset("Main_sloped_control_console")
length = CONSOLE_X1 - CONSOLE_X0
cx = (CONSOLE_X0 + CONSOLE_X1) / 2
console.include("Dark_plinth", box((length, 1.25, 0.72), (cx, CONSOLE_Y, 0.36), base))
console.include("Front_fascia", box((length, 0.10, 0.46), (cx, CONSOLE_Y-0.64, 0.58), (0.32, 0.30, 0.27)))
console.include("Writing_shelf", box((length, 0.47, 0.07),
                                      (cx, CONSOLE_Y-0.49, 0.87), paper))
# Sloped face rises toward the back wall.
slope_angle = 23
face = box((length, 1.02, 0.085), (cx, CONSOLE_Y+0.22, 1.09), panel)
face.turn(axis="x", degrees=slope_angle)
console.include("Inclined_control_face", face)

# Surface coordinate mapping on the sloping face, including its normal offset.
a = math.radians(slope_angle)
def surface_point(x, v, lift=0.055):
    return (x, CONSOLE_Y + 0.22 + v*math.cos(a) - lift*math.sin(a),
            1.09 + v*math.sin(a) + lift*math.cos(a))

for bay in range(8):
    x = CONSOLE_X0 + 0.40 + bay*0.78
    # Narrow transverse panel seams.
    seam = box((0.014, 0.92, 0.008), surface_point(x-0.34, 0), dark)
    seam.turn(axis="x", degrees=slope_angle)
    console.include("Face_seam_%02d" % bay, seam)
    for row in range(3):
        for col in range(3):
            px = x - 0.22 + col*0.19
            v = -0.30 + row*0.28
            # A dark switch with pale mounting plate, tilted with the face.
            mounting = box((0.105, 0.085, 0.012), surface_point(px, v, 0.052), paper)
            mounting.turn(axis="x", degrees=slope_angle)
            console.include("Switch_plate_%02d_%02d_%02d" % (bay,row,col), mounting)
            p = surface_point(px, v, 0.068)
            console.include("Switch_%02d_%02d_%02d" % (bay,row,col),
                            rod(0.026, start=p,
                                end=(p[0], p[1]-0.025, p[2]+0.055), color=dark))
scene.include("Main_sloped_control_console", console)

# Small independent desk in the right rear corner.
small = Asset("Right_independent_console")
small.include("Pedestal", box((1.45, 0.78, 0.72), (3.38, 2.05, 0.36), base))
small.include("Writing_ledge", box((1.55, 0.45, 0.07), (3.38, 1.72, 0.82), paper))
small_face = box((1.55, 0.64, 0.08), (3.38, 2.11, 0.98), panel)
small_face.turn(axis="x", degrees=22)
small.include("Sloped_face", small_face)
for i in range(7):
    for j in range(2):
        x = 2.79 + i*0.19
        y = 1.99 + j*0.24
        z = 0.98 + (y-2.11)*math.tan(math.radians(22)) + 0.07
        small.include("Control_%02d_%02d" % (i,j),
                      rod(0.027, start=(x,y,z), end=(x,y-0.015,z+0.05), color=dark))
scene.include("Right_independent_console", small)

# Yellow grid mimic board: graphic arrangement follows the separately pictured
# board. Its location on the right wall is an uncertain reconstruction choice.
grid = Asset("GRID_single_line_mimic_board")
grid_x, grid_y, grid_z = 2.55, 3.03, 2.15
grid.include("Yellow_panel", box((1.25, 0.075, 1.60), (grid_x, grid_y, grid_z), yellow))
front_y = grid_y - 0.046
# Main black bus and branch lines.
grid.include("Vertical_bus", box((0.035, 0.015, 1.34), (grid_x+0.10, front_y, grid_z), black))
for k, zz in enumerate((1.68, 2.12, 2.56)):
    grid.include("Cross_bus_%d" % k, box((0.60, 0.016, 0.035),
                                          (grid_x+0.10, front_y, zz), black))
for side in (-1, 1):
    for k, zz in enumerate((1.68, 2.12, 2.56)):
        xx = grid_x + 0.10 + side*0.27
        grid.include("Branch_%d_%d" % (side,k),
                     box((0.035, 0.016, 0.22), (xx, front_y, zz+0.09), black))
        grid.include("Amber_indicator_%d_%d" % (side,k),
                     box((0.09, 0.025, 0.09), (xx, front_y-0.016, zz+0.08), amber))
for i in range(4):
    z = 1.66 + i*0.35
    grid.include("Round_red_lamp_%d" % i,
                 rod(0.065, start=(grid_x-0.40, front_y-0.03, z),
                     end=(grid_x-0.40, front_y-0.07, z), color=red))
    grid.include("Selector_%d" % i,
                 rod(0.042, start=(grid_x-0.22, front_y-0.03, z),
                     end=(grid_x-0.22, front_y-0.07, z), color=black))
for i, z in enumerate((1.57, 2.73)):
    grid.include("German_label_plate_%d" % i,
                 box((0.36, 0.02, 0.10), (grid_x+0.35, front_y-0.025, z), paper))
scene.include("GRID_single_line_mimic_board", grid)

lighting = Asset("Ceiling_fluorescent_fixtures")
for i, x in enumerate((-2.5, 0.2, 2.7)):
    lighting.include("Troffer_%d" % i,
                     box((1.75, 0.46, 0.035), (x, 0.3, ROOM_H-0.07), (0.94,0.93,0.86)))
scene.include("Ceiling_fluorescent_fixtures", lighting)

realize(scene)

# Configure a neutral, softly lit 1970s room.
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
background.inputs["Color"].default_value = (0.72, 0.70, 0.66, 1)
background.inputs["Strength"].default_value = 0.55

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((-2.5, -1.0, 3.1), power=500, size=3.5, target=(-1, 1, 0.7))
area_emitter((2.0, 1.0, 3.1), power=450, size=3.0, target=(1, 1, 0.7))

# Preserve the reference image aspect for the projection check and the active view.
sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# The photograph is a wide inset of a portrait collage. Its landscape composition
# must therefore be adapted to the portrait output; the estimates below are rough
# portrait-frame targets, not calibration.
landmarks = [
    ("wall grille center", (-1.12, 3.00, 1.72), (0.37, 0.39)),
    ("console near left corner", (CONSOLE_X0, CONSOLE_Y-0.72, 0.87), (0.12, 0.73)),
    ("console far right corner", (CONSOLE_X1, CONSOLE_Y+0.68, 1.30), (0.67, 0.52)),
    ("small console top", (3.38, 2.30, 1.13), (0.82, 0.52)),
    ("yellow panel top", (grid_x, grid_y, grid_z+0.80), (0.73, 0.24)),
]
def report_landmarks():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print("Landmark                       reference       projected")
    result = []
    for name, p, ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        result.append(uv)
        print("%-30s %s %s" % (name, ref, None if uv is None else
                                (round(uv[0],3), round(uv[1],3))))
    return result

uvs = report_landmarks()
# If a confidently visible landmark is outside the frame, widen the view once.
# This preserves camera direction and all geometry and makes the actual final
# camera and its projections explicit.
if any(uv is not None and (uv[0] < -0.05 or uv[0] > 1.05 or
                           uv[1] < -0.05 or uv[1] > 1.05) for uv in uvs):
    sc.camera.data.lens *= 0.82
    print("Widened lens to keep identified geometry in the portrait frame.")
    report_landmarks()

# Add a second editable close-up camera while retaining the panorama as active.
panorama = sc.camera
panorama.name = "Camera_Panorama"
set_view((0.6, -4.0, 2.7), (1.0, 1.2, 1.35), lens=42)
sc.camera.name = "Camera_Console_Grid_Detail"
sc.camera = panorama

# Editable German labels on the yellow board.
def add_label(name, body, location, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    return obj

add_label("Label_Fehlerstelle_top", "FEHLERSTELLE", (grid_x+0.35, front_y-0.040, 2.73), 0.042)
add_label("Label_Fehlerstelle_bottom", "FEHLERSTELLE", (grid_x+0.35, front_y-0.040, 1.57), 0.042)

# The runner controls final rendering and file delivery. These scene settings retain
# the requested engine and color treatment without invoking render or save here.
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.image_settings.file_format = "PNG"
