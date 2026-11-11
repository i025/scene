# Reference anchors, normalized image coordinates, estimated visually:
# Foreground top (.07,.33)-(.91,.54), nearest foot around (.28,.97),
# far foot around (.87,.73), blue vise around (.38,.56).
# Rear orange bench spans the left crop to approximately (.85,.30);
# its log facade is partly hidden by the foreground bench.
# Lumber rack fills upper-left (.00,.00)-(.42,.28); corrugated wall,
# router, lamp, drill and storage occupy the upper middle and right.
# Major horizontal bench edges rise toward the right; white legs enclose
# large open spaces. Hidden backs and the exact stove geometry are uncertain.
#
# Comparison with the second rendered image:
# 1. Foreground top rendered around (.20,.51)-(.98,.72), versus reference
#    (.07,.33)-(.91,.54); the nearest foot is around (.34,.94) versus (.28,.97).
#    Its long edge has a similar upward-right slope. The rendered top is too
#    low and right, and the visible legs are much too short.
# 2. Rear bench top rendered around (0,.40)-(.88,.56), versus roughly
#    (0,.25)-(.85,.40). Rack is mostly cropped at left, while the reference
#    rack occupies the upper left. The wall appears considerably brighter.
# 3. Both benches overlap correctly, but the white bench needs taller, broader
#    leg members and a visible open rail beneath the top. Its top is too pale.
#
# Corrections: lower CAM_TARGET.z to move both bench tops upward; raise the
# foreground top and lengthen its legs to preserve the lower foot silhouette.
# Move the foreground bench left to move its left corner and vise left, while
# leaving the rear bench position unchanged. Move the lumber rack right so
# more appears at upper left. Darken the backdrop and use warmer, less uniform
# lighting; brightness depends on lighting as well as material color.
# Camera trial projections below are computed separately from these observed
# silhouette estimates. A small downward aim trial is checked and restored if
# it moves the bench landmarks in the wrong direction.
# Estimated primitive meshes: about 410: 192 log discs, 65 bench holes,
# 55 bench and clamp parts, 35 wall and rack parts, 40 machine parts,
# and roughly 25 other architectural and storage parts.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Woodworking shop")

# Independently editable camera and principal asset dimensions.
CAM_POS = (-3.7, -6.4, 3.05)
OLD_TARGET = (0.0, .12, 1.12)
CAM_TARGET = (0.0, .12, .70)
CAM_LENS = 65
BENCH_L, BENCH_D = 3.05, .94
BENCH_X, BENCH_Y, BENCH_Z = -.37, -.78, 1.18
REAR_L, REAR_D, REAR_Y, REAR_Z = 4.8, .92, .93, 1.02

white = (.76, .74, .67)
white_edge = (.86, .84, .77)
topmat = (.48, .30, .17)
orange = (.58, .29, .055)
blue = (.018, .14, .34)
yellow = (.92, .53, .01)
dark = (.045, .043, .037)
metal = (.25, .26, .25)
black = (.018, .02, .019)

def B(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

def R(asset, name, start, end, radius, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

room = Asset("Architecture")
B(room, "concrete_floor", (15, 14, .12), (0, 0, -.065), (.27, .27, .25))
B(room, "back_wall", (14, .13, 5), (0, 3.05, 2.5), (.065, .064, .055))
B(room, "dark_storage_bay", (3.4, .10, 4), (-2.6, 2.94, 2), (.035, .031, .025))
for i in range(34):
    x = -1.0 + i * .13
    B(room, "wall_rib_%02d" % i, (.026, .035, 4.2),
      (x, 2.96, 2.1), (.075, .078, .072))
scene.include("architecture", room)

rear = Asset("Rear log faced workbench")
B(rear, "heavy_body", (REAR_L, REAR_D, .80),
  (0, REAR_Y, .50), (.095, .061, .039))
B(rear, "orange_worktop", (REAR_L + .05, REAR_D + .05, .075),
  (0, REAR_Y, REAR_Z), orange)
B(rear, "front_lip", (REAR_L + .05, .055, .10),
  (0, REAR_Y - REAR_D / 2 - .02, REAR_Z - .065), (.36, .17, .045))
B(rear, "rear_edge", (REAR_L, .055, .08),
  (0, REAR_Y + REAR_D / 2, REAR_Z + .045), (.30, .15, .055))
logcols = [(.40, .29, .18), (.60, .47, .31),
           (.30, .21, .13), (.69, .56, .38)]
for row in range(4):
    z = .19 + row * .19
    for col in range(24):
        x = -2.30 + col * .20 + (row % 2) * .095
        if x > 2.35:
            continue
        r = random.uniform(.070, .105)
        y = REAR_Y - REAR_D / 2 - .034
        R(rear, "bark_%d_%d" % (row, col),
          (x, y, z), (x, y - .017, z), r, (.075, .047, .028))
        R(rear, "grain_%d_%d" % (row, col),
          (x, y - .018, z), (x, y - .023, z), r * .79,
          random.choice(logcols))
scene.include("rear_bench", rear)

front = Asset("Folding birch plywood workbench")
X = BENCH_X
Y = BENCH_Y
Z = BENCH_Z
B(front, "hardboard_top", (BENCH_L, BENCH_D, .055),
  (X, Y, Z), topmat)
B(front, "plywood_top_edge", (BENCH_L, BENCH_D, .045),
  (X, Y, Z - .045), (.65, .50, .33))
# Separate rails and an open strip between them make the under-top gap legible.
B(front, "front_upper_rail", (BENCH_L - .04, .065, .075),
  (X, Y - BENCH_D/2 + .032, Z - .11), white_edge)
B(front, "front_lower_apron", (BENCH_L - .04, .07, .19),
  (X, Y - BENCH_D/2 + .035, Z - .30), white_edge)
B(front, "rear_white_apron", (BENCH_L - .04, .07, .15),
  (X, Y + BENCH_D/2 - .035, Z - .15), white)
for x, label in ((X - BENCH_L/2 + .04, "left"),
                 (X + BENCH_L/2 - .04, "right")):
    B(front, label + "_end_rail", (.08, BENCH_D, .15),
      (x, Y, Z - .14), white)
for i in range(10):
    for j in range(4):
        x = X - 1.27 + i * .28
        y = Y - .32 + j * .20
        R(front, "top_dog_%d_%d" % (i, j),
          (x, y, Z + .028), (x, y, Z + .031), .009, (.24, .15, .09))
for i in range(14):
    x = X - 1.28 + i * .197
    R(front, "apron_hole_%02d" % i,
      (x, Y - BENCH_D/2 - .003, Z - .30),
      (x, Y - BENCH_D/2 - .009, Z - .30),
      .013, (.25, .23, .19))
# The legs extend from the taller top nearly to the floor. Splayed members
# and thin end panels leave the large central space open.
for side, relx in (("left", -1.19), ("right", 1.19)):
    x = X + relx
    for face, y in (("front", Y - .34), ("back", Y + .34)):
        footx = x + (-.15 if relx < 0 else .15)
        leg = box(size=(.24, .11, 1.10),
                  center=((x + footx)/2, y, .57), color=white)
        leg.turn(axis="+y", degrees=(-8 if relx < 0 else 8))
        front.include(side + "_" + face + "_leg", leg)
        B(front, side + "_" + face + "_foot", (.23, .14, .035),
          (footx, y, .028), (.61, .59, .53))
    B(front, side + "_inner_panel", (.045, .58, .62),
      (x, Y, .55), (.66, .63, .55))
    B(front, side + "_upper_crossbar", (.10, .72, .09),
      (x, Y, Z - .22), white_edge)
    outerx = x + (-.027 if relx < 0 else .027)
    for k in range(4):
        for m in range(3):
            yy = Y - .22 + m * .20
            zz = .32 + k * .13
            R(front, side + "_panel_hole_%d_%d" % (k, m),
              (outerx, yy, zz),
              (outerx + (-.006 if relx < 0 else .006), yy, zz),
              .011, (.23, .22, .19))
for i, x in enumerate((-1.32, -.38, .47, 1.25)):
    B(front, "yellow_stop_%d" % i, (.105, .075, .16),
      (X + x, Y + .02, Z - .18), yellow)
B(front, "front_left_yellow", (.13, .055, .17),
  (X - 1.34, Y - BENCH_D/2 - .01, Z - .22), yellow)
B(front, "vise_white_mount", (.48, .075, .23),
  (X - .63, Y - BENCH_D/2 - .025, Z - .28), white_edge)
B(front, "vise_blue_body", (.38, .09, .09),
  (X - .63, Y - BENCH_D/2 - .08, Z - .28), blue)
for i, x in enumerate((-.77, -.50)):
    R(front, "vise_bolt_%d" % i,
      (X + x, Y - BENCH_D/2 - .13, Z - .28),
      (X + x, Y - BENCH_D/2 - .145, Z - .28), .025, (.6, .61, .57))
R(front, "vise_screw",
  (X - .64, Y - BENCH_D/2 - .14, Z - .28),
  (X - .64, Y - BENCH_D/2 - .27, Z - .28), .028, metal)
R(front, "vise_handle",
  (X - .82, Y - BENCH_D/2 - .27, Z - .17),
  (X - .40, Y - BENCH_D/2 - .27, Z - .46), .025, metal)
R(front, "vise_handle_tip_a",
  (X - .84, Y - BENCH_D/2 - .27, Z - .16),
  (X - .80, Y - BENCH_D/2 - .27, Z - .19), .033, (.42, .07, .06))
R(front, "vise_handle_tip_b",
  (X - .42, Y - BENCH_D/2 - .27, Z - .44),
  (X - .38, Y - BENCH_D/2 - .27, Z - .47), .033, (.42, .07, .06))
for i in range(3):
    x = X - 1.30 + i * .09
    R(front, "clamp_bar_%d" % i, (x, Y - .43, .20),
      (x, Y - .43, .92), .012, metal)
    B(front, "clamp_handle_%d" % i, (.045, .045, .13),
      (x, Y - .44, .37 + i * .035), (.80, .20, .015))
    B(front, "clamp_jaw_%d" % i, (.10, .06, .035),
      (x + .025, Y - .43, .88), (.16, .17, .16))
scene.include("foreground_bench", front)

saw = Asset("Track saw")
B(saw, "silver_track", (1.15, .14, .018),
  (-1.85, REAR_Y - .26, REAR_Z + .05), (.52, .55, .53))
B(saw, "sole_plate", (.44, .29, .035),
  (-1.75, REAR_Y - .20, REAR_Z + .08), (.42, .44, .42))
B(saw, "blade_housing", (.30, .20, .19),
  (-1.75, REAR_Y - .20, REAR_Z + .18), (.65, .67, .63))
B(saw, "motor", (.14, .18, .15),
  (-1.56, REAR_Y - .20, REAR_Z + .18), (.25, .28, .26))
R(saw, "top_handle", (-1.88, REAR_Y - .18, REAR_Z + .29),
  (-1.63, REAR_Y - .18, REAR_Z + .29), .025, dark)
B(saw, "green_switch", (.06, .05, .04),
  (-1.61, REAR_Y - .19, REAR_Z + .28), (.12, .34, .08))
scene.include("track_saw", saw)

drill = Asset("Blue benchtop drill press")
dx, dy = -.89, REAR_Y + .02
B(drill, "base", (.32, .27, .045), (dx, dy, REAR_Z + .06), (.07, .10, .11))
R(drill, "column", (dx, dy, REAR_Z + .07),
  (dx, dy, REAR_Z + .66), .035, metal)
B(drill, "blue_head", (.22, .18, .14), (dx, dy, REAR_Z + .63), blue)
B(drill, "black_motor", (.14, .15, .18), (dx, dy + .11, REAR_Z + .65), dark)
B(drill, "work_table", (.24, .18, .035), (dx, dy - .04, REAR_Z + .30), blue)
R(drill, "chuck", (dx, dy - .06, REAR_Z + .55),
  (dx, dy - .06, REAR_Z + .37), .022, metal)
R(drill, "feed_lever", (dx + .10, dy, REAR_Z + .58),
  (dx + .23, dy, REAR_Z + .49), .012, black)
scene.include("drill_press", drill)

cnc = Asset("CNC gantry router")
cx, cy = .55, REAR_Y + .06
B(cnc, "black_base", (1.40, .68, .08), (cx, cy, REAR_Z + .09), (.055, .06, .055))
B(cnc, "sacrificial_board", (1.10, .49, .035),
  (cx, cy, REAR_Z + .15), (.54, .44, .31))
for i, x in enumerate((cx - .57, cx + .57)):
    B(cnc, "side_rail_%d" % i, (.065, .67, .10),
      (x, cy, REAR_Z + .19), (.20, .21, .20))
    B(cnc, "gantry_upright_%d" % i, (.08, .11, .38),
      (x, cy + .16, REAR_Z + .36), (.25, .26, .25))
B(cnc, "gantry_beam", (1.25, .11, .13),
  (cx, cy + .16, REAR_Z + .53), (.52, .54, .50))
B(cnc, "carriage", (.19, .15, .19),
  (cx + .06, cy + .10, REAR_Z + .49), (.09, .10, .09))
R(cnc, "router_spindle", (cx + .06, cy + .02, REAR_Z + .53),
  (cx + .06, cy + .02, REAR_Z + .24), .052, (.12, .12, .11))
B(cnc, "yellow_router_cap", (.13, .13, .07),
  (cx + .06, cy + .02, REAR_Z + .55), (.76, .51, .02))
scene.include("cnc_router", cnc)

lamp = Asset("Articulated task lamp")
lx, ly = -.53, REAR_Y + .30
B(lamp, "base", (.25, .18, .025), (lx, ly, REAR_Z + .055), (.48, .48, .44))
R(lamp, "lower_arm", (lx, ly, REAR_Z + .07),
  (lx - .05, ly, REAR_Z + .63), .016, (.58, .59, .55))
R(lamp, "upper_arm", (lx - .05, ly, REAR_Z + .63),
  (lx + .30, ly, REAR_Z + .91), .016, (.58, .59, .55))
R(lamp, "parallel_arm", (lx - .02, ly + .03, REAR_Z + .62),
  (lx + .32, ly + .03, REAR_Z + .88), .009, (.40, .41, .39))
R(lamp, "shade", (lx + .30, ly, REAR_Z + .91),
  (lx + .34, ly - .04, REAR_Z + .78), .085, (.66, .66, .60))
scene.include("task_lamp", lamp)

rack = Asset("Wall lumber rack")
RACK_X = -1.65
for i, z in enumerate((1.28, 1.69, 2.10, 2.51, 2.92)):
    B(rack, "shelf_%d" % i, (2.58, .43, .075),
      (RACK_X, 2.67, z), (.095, .060, .033))
for i, x in enumerate((RACK_X - 1.21, RACK_X + 1.02)):
    B(rack, "post_%d" % i, (.07, .08, 2.60),
      (x, 2.48, 1.65), (.07, .052, .035))
woodcols = [(.30, .16, .07), (.46, .27, .12),
            (.58, .38, .19), (.24, .14, .07)]
for level, z in enumerate((1.37, 1.78, 2.19, 2.60, 3.01)):
    for j in range(4):
        B(rack, "board_%d_%d" % (level, j),
          (random.uniform(1.1, 2.35), .16, .045),
          (RACK_X + random.uniform(-.22, .22), 2.50 + j * .075, z + j * .048),
          random.choice(woodcols))
scene.include("lumber_rack", rack)

stove = Asset("Cast iron stove")
B(stove, "firebox", (.75, .56, .62), (2.08, 2.27, .46), (.035, .035, .032))
B(stove, "stove_top", (.82, .60, .07), (2.08, 2.27, .80), (.055, .055, .05))
B(stove, "door", (.48, .025, .40), (2.08, 1.975, .45), (.07, .07, .065))
B(stove, "door_panel", (.37, .018, .28), (2.08, 1.958, .45), (.025, .025, .022))
for i, x in enumerate((1.79, 2.37)):
    B(stove, "foot_%d" % i, (.10, .10, .18), (x, 2.25, .09), dark)
R(stove, "chimney", (2.12, 2.31, .81), (2.12, 2.31, 3.8), .10, dark)
scene.include("stove", stove)

storage = Asset("Tools and wall storage")
B(storage, "right_shelving", (.84, .35, 1.48), (3.04, 2.52, .76), (.08, .065, .05))
for row, z in enumerate((.35, .70, 1.05, 1.40)):
    B(storage, "shelf_%d" % row, (.88, .39, .045),
      (3.04, 2.49, z), (.18, .11, .055))
    for i in range(4):
        B(storage, "bin_%d_%d" % (row, i), (.17, .25, .12),
          (2.73 + i * .20, 2.44, z + .08),
          (.25, .035, .02) if i % 2 else (.065, .07, .065))
B(storage, "dark_tool_board", (1.38, .05, .38), (.18, 2.90, 2.25), (.055, .045, .03))
for i in range(12):
    x = -.38 + i * .105
    R(storage, "hanging_tool_%d" % i, (x, 2.86, 1.81),
      (x, 2.86, 2.55 + (i % 3) * .08), .012,
      (.035, .035, .03) if i % 3 else (.23, .085, .035))
scene.include("tool_storage", storage)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.20, .19, .17, 1)
background.inputs["Strength"].default_value = .25
sc.render.resolution_x = 511
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100

# These correspond to actual vertices or surface points, not asset origins.
# Computed projections do not imply the points are visible in the rendered view.
landmarks = [
    ("front_near_left", (X - BENCH_L/2, Y - BENCH_D/2, Z), (.08, .46)),
    ("front_near_right", (X + BENCH_L/2, Y - BENCH_D/2, Z), (.91, .39)),
    ("left_foot", (X - 1.34, Y - .34, .035), (.28, .97)),
    ("rear_right", (REAR_L/2, REAR_Y - REAR_D/2, REAR_Z), (.85, .29)),
    ("rack_shelf_right", (RACK_X + 1.29, 2.45, 2.51), (.40, .12)),
]

def project_table(label):
    bpy.context.view_layer.update()
    camera = sc.camera
    depsgraph = bpy.context.evaluated_depsgraph_get()
    projection = camera.calc_matrix_camera(
        depsgraph, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    print(label, "| reference UV | projected UV")
    for name, point, ref in landmarks:
        clip = projection @ camera.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
        result.append(uv)
        print(name, ref, None if uv is None else tuple(round(v, 3) for v in uv))
    return result

set_view(CAM_POS, OLD_TARGET, lens=CAM_LENS)
before = project_table("previous camera on revised geometry")
trial_target = (OLD_TARGET[0], OLD_TARGET[1], OLD_TARGET[2] - .08)
set_view(CAM_POS, trial_target, lens=CAM_LENS)
trial = project_table("small downward aim trial")
# Downward aiming should move stationary bench and rear points up in the image.
if (before[0] is not None and trial[0] is not None and
    before[3] is not None and trial[3] is not None and
    trial[0][1] < before[0][1] and trial[3][1] < before[3][1]):
    set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
    project_table("selected camera")
else:
    set_view(CAM_POS, OLD_TARGET, lens=CAM_LENS)
    print("Trial moved landmarks in the wrong direction; previous camera restored.")
    project_table("restored camera")

area_emitter((-3, -4, 6), power=850, size=5,
             target=(0, 0, .6), color=(1.0, .79, .58))
area_emitter((3, 1, 4.5), power=450, size=4,
             target=(0, 0, .6), color=(1.0, .85, .68))
area_emitter((lx + .32, ly - .05, REAR_Z + .78), power=70, size=.4,
             target=(lx + .25, ly - .05, REAR_Z), color=(1, .78, .48))
