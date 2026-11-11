import bpy
import math
import random
from mathutils import Vector
from sceneact import *

# Reference inventory and visual anchors, normalized image coordinates:
# - Cream wall: full width, top to blue boundary at y about .61.
# - Dark blue lower wall: full width, y .61–.93, partly hidden by furniture.
# - Green chalkboard: x .11–.895, y .28–.68; two adjacent panels with
#   a narrow vertical join at x .50. Chalk smears cover much of its surface.
# - Small paper above board: x .46–.61, y .06–.23, hanging from two threads.
# - Rear desk: pale wood top x .19–.60, y .79–.85; chair back behind it
#   at x .29–.38, y .73–.80. Thin metal legs continue downward.
# - Foreground desk: pale wood top x .09–.59, y .88–.96, cropped legs.
# - Foreground chair: x .14–.28, y .92–1.00, partly cropped.
# - Right desk: top x .75–1.00, y .89–.96, with cropped metal legs
#   and a partially visible wooden chair back beneath it.
# - Narrow floor strip appears below the wall at y about .93.
# Dominant edges are nearly horizontal and vertical; desk edges converge only
# slightly. The foreground desks occlude the rear desk legs and the floor.
# The exact furniture construction and portions outside the frame are uncertain.
#
# Estimated expanded primitives: architecture 4, board and trim 7, chalk
# marks about 105, paper and hanging parts about 20, furniture about 35:
# approximately 171 separate meshes in total.

random.seed(19)

# Editable scene and camera parameters.
BOARD_WIDTH = 5.40
BOARD_HEIGHT = 1.80
BOARD_BOTTOM = 1.28
BOARD_Y = -0.035
WALL_WIDTH = 9.0
WALL_HEIGHT = 5.0
BLUE_HEIGHT = 1.57

CAMERA_POSITION = (0.0, -8.0, 2.13)
CAMERA_TARGET = (0.0, 0.0, 2.13)
CAMERA_LENS = 42.3

scene = Scene("Classroom")
cream = (0.79, 0.78, 0.72)
blue = (0.018, 0.105, 0.34)
green_left = (0.075, 0.20, 0.115)
green_right = (0.052, 0.155, 0.095)
wood = (0.72, 0.44, 0.20)
wood_light = (0.90, 0.67, 0.37)
wood_edge = (0.72, 0.40, 0.16)
metal = (0.43, 0.46, 0.44)

architecture = Asset("architecture")
architecture.include("cream_wall", box(
    (WALL_WIDTH, .10, WALL_HEIGHT),
    center=(0, .08, WALL_HEIGHT / 2), color=cream))
architecture.include("blue_lower_wall", box(
    (WALL_WIDTH, .026, BLUE_HEIGHT),
    center=(0, .012, BLUE_HEIGHT / 2), color=blue))
architecture.include("floor", box(
    (WALL_WIDTH, 8, .08), center=(0, -3.9, -.045),
    color=(0.60, 0.43, 0.31)))
architecture.include("baseboard", box(
    (WALL_WIDTH, .045, .055), center=(0, -.025, .035),
    color=(0.78, 0.72, 0.61)))
scene.include("architecture", architecture)

board = Asset("chalkboard")
half = BOARD_WIDTH / 2
board.include("left_green_panel", box(
    (half, .075, BOARD_HEIGHT),
    center=(-half / 2, BOARD_Y, BOARD_BOTTOM + BOARD_HEIGHT / 2),
    color=green_left))
board.include("right_green_panel", box(
    (half, .075, BOARD_HEIGHT),
    center=(half / 2, BOARD_Y, BOARD_BOTTOM + BOARD_HEIGHT / 2),
    color=green_right))
board.include("center_joint", box(
    (.026, .025, BOARD_HEIGHT),
    center=(0, -.085, BOARD_BOTTOM + BOARD_HEIGHT / 2),
    color=(.23, .24, .19)))
board.include("bottom_edge", box(
    (BOARD_WIDTH, .036, .026),
    center=(0, -.083, BOARD_BOTTOM), color=(.42, .44, .36)))

# Broad semitransparent chalk residue: sparse vertical streaks and curved
# swipes. All marks are separate editable elements on the board face.
chalk = Asset("chalk_residue")
front_y = -.093
for i in range(63):
    x = random.uniform(-2.64, 2.64)
    zmid = random.uniform(1.48, 2.95)
    length = random.uniform(.12, .88)
    z0 = max(BOARD_BOTTOM + .025, zmid - length / 2)
    z1 = min(BOARD_BOTTOM + BOARD_HEIGHT - .025, zmid + length / 2)
    if z1 <= z0:
        continue
    right = x > 0
    col = random.choice([
        (.19, .31, .22), (.24, .35, .26), (.31, .40, .31),
        (.13, .26, .17), (.40, .47, .38)
    ])
    width = random.uniform(.006, .025) if right else random.uniform(.008, .032)
    chalk.include("vertical_smear_%02d" % i, box(
        (width, .006, z1-z0), center=(x, front_y, (z0+z1)/2),
        color=col))
for i in range(26):
    x = random.uniform(-2.58, -.18)
    z = random.uniform(1.40, 2.92)
    dx = random.uniform(.08, .34)
    dz = random.uniform(-.10, .10)
    chalk.include("short_chalk_stroke_%02d" % i, rod(
        random.uniform(.005, .011),
        start=(x, -.100, z), end=(x+dx, -.100, z+dz),
        color=random.choice([(.42, .50, .40), (.31, .41, .32),
                             (.25, .36, .27)])))
# Sweeping wiped arcs on the left panel.
for j in range(4):
    points = []
    for k in range(7):
        t = math.pi * (0.12 + .73*k/6)
        points.append((-1.00 + (.55+j*.075)*math.cos(t),
                       -.102,
                       2.30 + (.58+j*.045)*math.sin(t)))
    for k in range(len(points)-1):
        chalk.include("arc_%d_%d" % (j, k), rod(
            .008, start=points[k], end=points[k+1],
            color=(.34, .43, .34)))
board.include("chalk_marks", chalk)
scene.include("chalkboard", board)

# Paper sheet and string above the board; marks suggest small printed rows.
notice = Asset("hanging_notice")
notice.include("sheet", box(
    (.96, .018, .75), center=(.20, -.045, 3.69),
    color=(.83, .81, .75)))
notice.include("top_edge", box(
    (.96, .012, .012), center=(.20, -.060, 4.065),
    color=(.67, .64, .57)))
notice.include("left_string", rod(
    .004, start=(-.27, -.052, 4.06), end=(.20, -.052, 4.42),
    color=(.60, .58, .51)))
notice.include("right_string", rod(
    .004, start=(.67, -.052, 4.06), end=(.20, -.052, 4.42),
    color=(.60, .58, .51)))
for i in range(10):
    z = 3.43 + i*.057
    notice.include("printed_row_%02d" % i, box(
        (random.uniform(.42, .78), .004, .007),
        center=(.20 + random.uniform(-.06, .06), -.058, z),
        color=(.50, .49, .45)))
notice.include("wall_hook", ball(.052, center=(-.46, -.055, 3.89),
                                  color=(.09, .09, .075)))
scene.include("notice", notice)

def add_desk(name, x, y, width, depth, top_z, height):
    desk = Asset(name)
    desk.include("wooden_top", box(
        (width, depth, .065), center=(x, y, top_z),
        color=wood_light))
    desk.include("front_wood_edge", box(
        (width, .025, .06),
        center=(x, y-depth/2-.012, top_z-.008), color=wood_edge))
    # Tubular legs are visible as pale gray vertical supports.
    for side in (-1, 1):
        for fore in (-1, 1):
            lx = x + side*(width/2-.13)
            ly = y + fore*(depth/2-.10)
            desk.include("leg_%s_%s" % (side, fore), rod(
                .026, start=(lx, ly, .025), end=(lx, ly, top_z-.04),
                color=metal))
    desk.include("under_top_bar", rod(
        .018, start=(x-width/2+.10, y, top_z-.13),
        end=(x+width/2-.10, y, top_z-.13), color=metal))
    scene.include(name, desk)

def add_chair(name, x, y, width, back_bottom, back_top):
    chair = Asset(name)
    chair.include("plywood_back", box(
        (width, .055, back_top-back_bottom),
        center=(x, y, (back_bottom+back_top)/2), color=wood))
    chair.include("back_top_edge", box(
        (width, .06, .025), center=(x, y, back_top),
        color=(.84, .59, .31)))
    for side in (-1, 1):
        xx = x + side*(width/2-.05)
        chair.include("back_support_%s" % side, rod(
            .018, start=(xx, y+.025, .18),
            end=(xx, y+.025, back_top-.03), color=metal))
    chair.include("seat", box(
        (width, .42, .045), center=(x, y-.16, .47),
        color=wood_light))
    scene.include(name, chair)

# Rear desk and chair, set away from the viewer.
add_chair("rear_chair", -1.23, -1.42, .64, .88, 1.17)
add_desk("rear_desk", -.72, -1.72, 2.48, .54, .82, .82)

# Cropped foreground furniture.
add_desk("foreground_left_desk", -.79, -3.35, 2.50, .62, .79, .79)
add_chair("foreground_left_chair", -1.48, -3.71, .70, .47, .82)
add_desk("foreground_right_desk", 2.46, -3.32, 1.77, .59, .78, .78)
add_chair("foreground_right_chair", 2.23, -3.67, .73, .44, .79)

realize(scene)

# The reference aspect is preserved for both projection checks and final view.
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 337
sc.render.resolution_percentage = 100

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

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
background.inputs["Color"].default_value = (.78, .79, .76, 1)
background.inputs["Strength"].default_value = .8

area_emitter((-3, -4, 6), power=850, size=5,
             target=(0, 0, 1.5), color=(1.0, .94, .84))
area_emitter((4, -2, 5), power=350, size=4,
             target=(0, 0, 1.5), color=(.86, .91, 1.0))

# Reference estimates and projected coordinates remain separate. These
# landmarks lie on the visible geometry, including background and foreground.
landmarks = [
    ("board upper left", (-2.70, -.075, 3.08), (.11, .28)),
    ("board lower right", (2.70, -.075, 1.28), (.895, .68)),
    ("rear desk left top", (-1.96, -1.99, .8525), (.19, .80)),
    ("foreground left edge", (-2.04, -3.66, .8225), (.09, .89)),
]

bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark                      reference       projected")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5 * (clip.x / clip.w + 1),
        .5 * (1 - clip.y / clip.w))
    print("%-28s %s %s" % (name, reference,
          None if uv is None else tuple(round(v, 3) for v in uv)))
