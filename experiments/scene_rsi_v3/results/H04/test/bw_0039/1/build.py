# Reference and previous-render comparison (normalized image coordinates):
# - Rear window: reference approximately (0.63, 0.09)-(0.92, 0.43);
#   previous render approximately (0.58, 0.30)-(0.80, 0.51).
# - Ladder: reference approximately (0.56, 0.22)-(1.00, 0.80);
#   previous render approximately (0.54, 0.31)-(0.84, 0.76).
# - Electrical box: reference approximately (0.15, 0.36)-(0.25, 0.50);
#   previous render approximately (0.18, 0.41)-(0.28, 0.53).
# - Foreground debris: reference concentrated around x=0.30-1.00,
#   y=0.77-1.00; previous render spreads from x=0.25-1.00, y=0.70-1.00.
# - Rear wall/floor intersection: reference near y=0.67; previous render
#   near y=0.66. The left doorway and foreground floor crops are broadly
#   comparable. The ladder crosses the window; its rails rise to the right.
#
# Ranked visible discrepancies:
# 1. The previous rear wall has conspicuous open dark space above and to the
#    right; the photograph is enclosed. Increase rear wall extent and add the
#    right-hand wall, predicting that those dark regions become masonry.
# 2. The window is too low and small. Increase its width and height and raise
#    its top, predicting a higher top and farther-right right edge while
#    retaining the rear wall/floor intersection.
# 3. The ladder is too short and narrow. Raise its hinge and widen its rear
#    footprint, predicting a higher top and an open triangular right silhouette.
# 4. The lamp is a small point in the render; raise it and increase its local
#    illumination. The previous scene is also too evenly pale: material color,
#    light intensity, and surface orientation all contribute to that appearance.
# 5. Move the loose strips toward the right foreground and use flat rectangular
#    wood pieces. Their exact individual positions and hidden wall construction
#    remain uncertain.
# The camera is preserved: background, foreground, and box have inconsistent
# errors, so local geometry changes are better supported than a common shift.
# A reference-versus-projection table is printed for selected geometry points.
#
# Estimated expanded mesh count: room and timber approximately 95, window 16,
# ladder 22, electrical and lamp 8, floor debris 95: approximately 236.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(21)
scene = Scene("Renovation room")

# Major dimensions and camera are independent.
ROOM_LEFT = -1.28
ROOM_RIGHT = 2.55
BACK_Y = 3.15
ROOM_H = 5.0
CAMERA_POSITION = (0.0, -3.55, 1.67)
CAMERA_TARGET = (-0.35, 2.35, 1.22)
CAMERA_LENS = 32

wood = (0.23, 0.105, 0.047)
wood_light = (0.39, 0.22, 0.11)
wood_dark = (0.10, 0.047, 0.022)
brick = (0.26, 0.225, 0.16)
mortar = (0.19, 0.17, 0.13)
metal = (0.50, 0.53, 0.52)
metal_dark = (0.22, 0.24, 0.23)
white = (0.75, 0.74, 0.66)

# Architecture includes a physical opening for the window.
room = Asset("room_enclosure")
room.include("floor", box((3.9, 7.0, 0.12),
    center=(0.63, 0.75, -0.07), color=(0.33, 0.31, 0.25)))

wl, wr, wb, wt = 0.27, 1.79, 1.48, 3.82
room.include("rear_left", box((wl-ROOM_LEFT, 0.15, ROOM_H),
    center=((ROOM_LEFT+wl)/2, BACK_Y, ROOM_H/2), color=brick))
room.include("rear_right", box((ROOM_RIGHT-wr, 0.15, ROOM_H),
    center=((wr+ROOM_RIGHT)/2, BACK_Y, ROOM_H/2), color=brick))
room.include("rear_below_window", box((wr-wl, 0.15, wb),
    center=((wl+wr)/2, BACK_Y, wb/2), color=brick))
room.include("rear_above_window", box((wr-wl, 0.15, ROOM_H-wt),
    center=((wl+wr)/2, BACK_Y, (wt+ROOM_H)/2), color=brick))
room.include("left_backing", box((0.12, 4.2, ROOM_H),
    center=(-1.28, 1.05, ROOM_H/2), color=(0.18, 0.145, 0.095)))
room.include("right_wall", box((0.13, 4.1, ROOM_H),
    center=(2.55, 1.10, ROOM_H/2), color=(0.24, 0.215, 0.16)))

# Subtle horizontal masonry seams and retained lower wood lath.
for i in range(29):
    z = 0.11 + i * 0.16
    intervals = [(ROOM_LEFT, ROOM_RIGHT)] if z < wb or z > wt else [
        (ROOM_LEFT, wl), (wr, ROOM_RIGHT)]
    for j, (a, b) in enumerate(intervals):
        if b-a > 0.03:
            room.include("mortar_%02d_%d" % (i, j),
                box((b-a, 0.012, 0.012),
                    center=((a+b)/2, BACK_Y-0.081, z), color=mortar))
    for j in range(4):
        x = -1.08 + j*0.88 + (0.36 if i % 2 else 0)
        if x < ROOM_RIGHT and not (wl-0.03 < x < wr+0.03 and wb < z < wt):
            room.include("brick_joint_%02d_%d" % (i, j),
                box((0.012, 0.014, 0.13),
                    center=(x, BACK_Y-0.083, z+0.075), color=mortar))
for i in range(10):
    z = 0.09 + i*0.072
    room.include("rear_lath_%02d" % i,
        box((3.72, 0.032, 0.045),
            center=(0.62, BACK_Y-0.11, z),
            color=wood_light if i % 3 else wood))
scene.include("architecture", room)

framing = Asset("exposed_wood_framing")
for i, y in enumerate((-0.45, 0.15, 0.72, 1.27, 1.82, 2.38, 2.95)):
    framing.include("stud_%02d" % i,
        box((0.11, 0.105, ROOM_H), center=(-1.17, y, ROOM_H/2),
            color=wood_dark if i % 2 == 0 else wood))
framing.include("bottom_plate", box((0.13, 3.7, 0.10),
    center=(-1.17, 1.20, 0.07), color=wood))
for i in range(35):
    z = 0.16 + i*0.105
    framing.include("old_lath_%02d" % i,
        box((0.025, 3.55, 0.040), center=(-1.235, 1.30, z),
            color=wood_light if i % 4 else wood_dark))
framing.include("left_door_jamb", box((0.15, 0.20, ROOM_H),
    center=(-1.30, -0.45, ROOM_H/2), color=(0.48, 0.40, 0.23)))
framing.include("left_inner_trim", box((0.07, 0.21, ROOM_H),
    center=(-1.17, -0.48, ROOM_H/2), color=(0.22, 0.14, 0.07)))
framing.include("right_door_jamb", box((0.11, 0.17, ROOM_H),
    center=(2.50, -0.45, ROOM_H/2), color=(0.49, 0.44, 0.32)))
scene.include("timber_framing", framing)

# Two dark glazed sashes, white surround, sill, and meeting rail.
window = Asset("white_double_hung_window")
cx = (wl+wr)/2
mid = 2.61
window.include("dark_recess", box((wr-wl+0.10, 0.04, wt-wb+0.10),
    center=(cx, BACK_Y+0.035, (wb+wt)/2), color=(0.04, 0.035, 0.025)))
window.include("upper_pane", box((wr-wl-0.18, 0.035, wt-mid-0.12),
    center=(cx, BACK_Y-0.005, (mid+wt)/2), color=(0.035, 0.075, 0.095)))
window.include("lower_pane", box((wr-wl-0.18, 0.035, mid-wb-0.12),
    center=(cx, BACK_Y-0.005, (wb+mid)/2), color=(0.018, 0.055, 0.11)))
for name, x in (("left", wl), ("right", wr)):
    window.include("frame_"+name, box((0.10, 0.10, wt-wb+0.12),
        center=(x, BACK_Y-0.095, (wb+wt)/2), color=white))
for name, z in (("top", wt), ("bottom", wb), ("meeting_rail", mid)):
    window.include(name, box((wr-wl+0.11, 0.10, 0.085),
        center=(cx, BACK_Y-0.095, z), color=white))
for i, x in enumerate((wl+0.10, wr-0.10)):
    window.include("sash_side_%d" % i,
        box((0.04, 0.06, wt-wb-0.20),
            center=(x, BACK_Y-0.15, (wb+wt)/2), color=(0.58, 0.59, 0.53)))
window.include("sill", box((wr-wl+0.18, 0.17, 0.08),
    center=(cx, BACK_Y-0.14, wb-0.03), color=(0.57, 0.55, 0.47)))
for i in range(7):
    x = wl+0.20+i*(wr-wl-0.40)/6
    window.include("lower_reflection_%d" % i,
        box((0.014, 0.008, 0.60),
            center=(x, BACK_Y-0.03, 2.02), color=(0.025, 0.10, 0.20)))
scene.include("window", window)

electrical = Asset("electrical_box_and_conduit")
electrical.include("body", box((0.19, 0.27, 0.43),
    center=(-1.04, 0.05, 1.62), color=(0.69, 0.70, 0.66)))
electrical.include("lid", box((0.025, 0.26, 0.40),
    center=(-0.935, 0.05, 1.62), color=(0.81, 0.81, 0.74)))
electrical.include("red_cap", box((0.12, 0.14, 0.035),
    center=(-1.02, 0.04, 1.855), color=(0.37, 0.06, 0.04)))
electrical.include("conduit", rod(0.018, start=(-1.04, 0.05, 1.39),
    end=(-1.04, 0.05, 0.10), color=(0.42, 0.42, 0.38)))
scene.include("electrical", electrical)

# Folding ladder: front pair and steps, rear pair, hinge and spreaders.
ladder = Asset("aluminum_folding_ladder")
TOP_X, TOP_Y, TOP_Z = 1.26, 2.22, 2.95
FOOT_X, FRONT_Y, REAR_Y = 0.12, 0.80, 2.90
LADDER_WIDTH = 0.43
for side in (-1, 1):
    fx = FOOT_X + side*LADDER_WIDTH/2
    tx = TOP_X + side*LADDER_WIDTH/2
    ladder.include("front_rail_%s" % side, rod(0.045,
        start=(fx, FRONT_Y, 0.06), end=(tx, TOP_Y, TOP_Z), color=metal))
    ladder.include("rear_rail_%s" % side, rod(0.040,
        start=(1.95+side*LADDER_WIDTH/2, REAR_Y, 0.06),
        end=(tx, TOP_Y, TOP_Z), color=metal))
    ladder.include("front_foot_%s" % side, box((0.12, 0.16, 0.065),
        center=(fx, FRONT_Y, 0.05), color=metal_dark))
    ladder.include("hinge_%s" % side, ball(0.06,
        center=(tx, TOP_Y, TOP_Z-0.04), color=metal_dark))
for i in range(7):
    t = (i+1)/8
    x = FOOT_X+(TOP_X-FOOT_X)*t
    y = FRONT_Y+(TOP_Y-FRONT_Y)*t
    z = 0.06+(TOP_Z-0.06)*t
    ladder.include("step_%d" % i, box((LADDER_WIDTH+0.07, 0.13, 0.048),
        center=(x, y, z), color=metal))
for side in (-1, 1):
    ladder.include("spreader_%s" % side, rod(0.018,
        start=(0.48+side*LADDER_WIDTH/2, 1.32, 1.0),
        end=(1.70+side*LADDER_WIDTH/2, 2.65, 1.0), color=metal_dark))
ladder.include("top_cap", box((LADDER_WIDTH+0.12, 0.16, 0.09),
    center=(TOP_X, TOP_Y, TOP_Z), color=(0.36, 0.39, 0.37)))
ladder.include("red_rail_label", rod(0.020,
    start=(0.02, 0.93, 0.30), end=(0.30, 1.28, 1.03),
    color=(0.54, 0.045, 0.025)))
scene.include("ladder", ladder)

worklight = Asset("temporary_work_light")
worklight.include("mount", box((0.08, 0.12, 0.18),
    center=(-1.03, 0.65, 3.38), color=(0.26, 0.20, 0.13)))
worklight.include("bulb", ball(0.11, center=(-0.94, 0.65, 3.38),
    color=(1.0, 0.94, 0.76)))
worklight.include("cable", rod(0.012, start=(-1.12, 0.65, 3.30),
    end=(-1.12, 0.65, 0.35), color=(0.08, 0.08, 0.07)))
scene.include("work_light", worklight)

# The scattered wood pieces are narrow flat strips, not cylindrical sticks.
debris = Asset("broken_lath_and_rubble")
for i in range(42):
    x = random.uniform(-0.48, 1.65)
    y = random.uniform(-0.85, 1.35)
    length = random.uniform(0.25, 1.05)
    angle = random.uniform(-180, 180)
    z = random.uniform(0.025, 0.09)
    strip = box((length, random.uniform(0.025, 0.055), 0.024),
        center=(x, y, z),
        color=random.choice([wood, wood_light, wood_dark, (0.45, 0.29, 0.14)]))
    strip.turn("+z", angle)
    debris.include("strip_%02d" % i, strip)
for i in range(55):
    x = random.uniform(-1.15, 1.90)
    y = random.uniform(-0.85, 2.65)
    s = random.uniform(0.025, 0.13)
    debris.include("rubble_%02d" % i,
        box((s, s*random.uniform(0.5, 1.3), s*0.32),
            center=(x, y, s*0.16),
            color=random.choice([(0.39, 0.36, 0.29), (0.25, 0.22, 0.17),
                                 (0.48, 0.43, 0.34)])))
scene.include("floor_debris", debris)

realize(scene)

sc = bpy.context.scene
sc.render.resolution_x = 383
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

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
background.inputs["Color"].default_value = (0.15, 0.13, 0.10, 1)
background.inputs["Strength"].default_value = 0.22

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Computed point projections are distinct from observed image silhouettes.
landmarks = [
    ("window upper left", (wl, BACK_Y-0.095, wt), (0.63, 0.10)),
    ("window lower right", (wr, BACK_Y-0.095, wb), (0.92, 0.43)),
    ("ladder front foot", (FOOT_X-LADDER_WIDTH/2, FRONT_Y, 0.06), (0.59, 0.79)),
    ("foreground floor edge", (-1.15, -0.45, 0), (0.25, 0.98)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print("Reference and projected geometry landmarks")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
    print(name, "reference", reference, "projected", uv)

area_emitter((-0.90, 0.60, 3.38), power=350, size=0.22,
    target=(0, 2.0, 1.4), color=(1.0, 0.72, 0.42))
area_emitter((0.2, -1.0, 2.8), power=95, size=2.5,
    target=(0, 2.0, 1.0), color=(1.0, 0.83, 0.62))
area_emitter((0.7, 3.0, 2.1), power=20, size=0.8,
    target=(0.2, 1.2, 1.0), color=(0.40, 0.53, 1.0))
