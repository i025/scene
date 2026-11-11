# Reference inventory and approximate normalized image anchors:
# - Nearest cow: x .35-.83, y .36-.93; rump at lower left, head at right.
#   A darker cow lies immediately behind it, with more cows partly occluded at left.
# - Curved galvanized dividers and cross rails: x 0-1, y .14-.72.
#   Their loops overlap the cows; the main horizontal rails descend gently rightward.
# - Raised bed edge: approximately (0,.57) to (.66,1.0); manure alley below left.
# - Background concrete and pale wall fill the upper frame; blue door x .32-.43,
#   y 0-.23; worker is partially cropped at far right x .94-1, y .12-.46.
# - The cows' hidden legs, far-side rail connections and background depth are uncertain.
#
# Comparison with the last successful render, ranked by visible extent:
# 1. The rendered cows are small end-on ovals at approximately y .45-.79, rather
#    than the large overlapping side silhouettes in the reference. CAMERA_POSITION
#    moves toward the row direction, so the cows' length projects toward image right
#    and adjacent animals overlap more strongly. CAMERA_LENS is increased to enlarge
#    the foreground animals; the nearest cow should extend farther down the image.
# 2. The rendered bed edge lies around y .65-.92 with too much pale empty foreground,
#    versus the reference's diagonal curb from y .57 at left to the bottom near x .66.
#    The more oblique camera angle makes the curb steeper; the darker alley restores
#    the broad foreground contrast.
# 3. The rendered door is around x .47-.58, y .20-.49, whereas the reference door
#    is near x .32-.43, y 0-.23. The camera target and DOOR_X are adjusted to move
#    the door left and upward relative to the cows.
# 4. The render has repetitive white backs and round spots, while the reference has
#    a large dark middle cow and irregular side markings. Cow proportions and patch
#    shapes are varied. The reference rails form open loops around the animals;
#    their spacing and distinctive bent ends are retained.
# Brightness differences also depend on lighting and orientation, not only color.
#
# Estimated expanded primitive count: architecture 20, floor and bed 4, rail
# dividers 10*10 plus 7 cross members = 107, cows roughly 8*16 = 128,
# worker 7; total about 266 meshes. No Boolean operations or external assets.

from sceneact import *
import bpy
import math
import random

random.seed(28)
scene = Scene("Dairy barn free stalls")

# Camera and scene dimensions can be adjusted independently.
CAMERA_POSITION = (13.5, -7.7, 3.3)
CAMERA_TARGET = (-0.8, 0.4, 1.15)
CAMERA_LENS = 58
BED_Z = 0.24
STALL_WIDTH = 1.25
STALL_COUNT = 10
DOOR_X = -4.1

concrete = (0.39, 0.40, 0.39)
bed_color = (0.50, 0.50, 0.47)
wall_gray = (0.38, 0.40, 0.40)
wall_white = (0.76, 0.78, 0.77)
blue = (0.018, 0.075, 0.17)
steel = (0.58, 0.62, 0.61)
white = (0.77, 0.74, 0.66)
black = (0.022, 0.025, 0.022)
dirty = (0.27, 0.25, 0.19)
pink = (0.48, 0.36, 0.33)

architecture = Asset("Barn architecture")
architecture.include("concrete floor", box((35, 24, .16),
                     center=(0, 0, -.12), color=concrete))
architecture.include("lower concrete wall", box((35, .20, 1.55),
                     center=(0, 4.6, .775), color=wall_gray))
architecture.include("upper wall panels", box((35, .16, 4.0),
                     center=(0, 4.65, 3.55), color=wall_white))
for i, x in enumerate((-12, -8.8, -5.6, -2.4, .8, 4.0, 7.2, 10.4)):
    architecture.include("blue structural post %d" % i,
        box((.14, .22, 5.55), center=(x, 4.48, 2.78), color=blue))
for i, x in enumerate((-10.4, -7.2, -4.0, -.8, 2.4, 5.6, 8.8)):
    architecture.include("panel seam %d" % i,
        box((.018, .025, 3.9), center=(x, 4.54, 3.5),
            color=(.56, .59, .59)))
architecture.include("door frame", box((1.48, .07, 2.35),
                     center=(DOOR_X, 4.45, 1.18), color=(.012, .035, .07)))
architecture.include("door left leaf", box((.67, .05, 2.18),
                     center=(DOOR_X-.35, 4.40, 1.13), color=blue))
architecture.include("door right leaf", box((.67, .05, 2.18),
                     center=(DOOR_X+.35, 4.40, 1.13), color=blue))
architecture.include("door horizontal frame", box((1.40, .05, .055),
                     center=(DOOR_X, 4.36, 1.10), color=(.035, .08, .15)))
scene.include("architecture", architecture)

platform = Asset("Raised resting platform and alley")
platform.include("bed slab", box((30, 5.3, .25),
                 center=(0, .65, .105), color=bed_color))
platform.include("front curb", box((30, .18, .32),
                 center=(0, -2.02, .13), color=(.32, .33, .31)))
platform.include("manure alley", box((35, 5, .025),
                 center=(0, -4.55, -.015), color=(.27, .26, .19)))
scene.include("beds and walkway", platform)

def pipe(asset, name, a, b, radius=.042):
    asset.include(name, rod(radius, start=a, end=b, color=steel))

stalls = Asset("Galvanized stall dividers")
for i in range(STALL_COUNT):
    x = -6.3 + i * STALL_WIDTH
    # Open loops rise at the rear and curve down at the head end.
    p = [(x, -1.75, .26), (x, -1.75, 1.04),
         (x, -1.68, 1.20), (x, -1.48, 1.31),
         (x, 1.67, 1.31), (x, 2.03, 1.22),
         (x, 2.22, 1.05), (x, 2.23, .43)]
    for j in range(len(p)-1):
        pipe(stalls, "divider %02d upper %02d" % (i, j), p[j], p[j+1])
    q = [(x, -1.50, .72), (x, .85, .72),
         (x, 1.35, .65), (x, 1.65, .51)]
    for j in range(len(q)-1):
        pipe(stalls, "divider %02d lower %02d" % (i, j), q[j], q[j+1], .037)
for j, (y, z) in enumerate(((1.80, 1.36), (2.35, .98), (3.05, 1.18))):
    pipe(stalls, "continuous rail %d" % j, (-12, y, z), (12, y, z), .041)
for i, x in enumerate((-8, -4, 0, 4, 8)):
    pipe(stalls, "rail upright %d" % i, (x, 3.05, .24), (x, 3.05, 1.18))
scene.include("stall equipment", stalls)

def ellipsoid(asset, name, center, scale, color):
    node = ball(1.0, center=center, color=color)
    node.resize(scale, pivot=center)
    asset.include(name, node)

def make_cow(index, x, y, size=1.0, dark=False):
    cow = Asset("Reclining Holstein %02d" % index)
    s = size

    def E(name, dx, dy, dz, sx, sy, sz, color):
        ellipsoid(cow, name, (x+dx*s, y+dy*s, BED_Z+dz*s),
                  (sx*s, sy*s, sz*s), color)

    E("barrel", 0, 0, .48, .53, 1.00, .46, black if dark else white)
    E("shoulder", 0, .56, .48, .46, .45, .39, black)
    E("haunch", 0, -.70, .40, .48, .37, .37, black if dark else white)
    if not dark:
        E("flank patch A", .47, -.08, .58, .10, .26, .19, black)
        E("flank patch B", .40, .24, .73, .14, .21, .10, black)
        E("flank patch C", .48, -.37, .60, .08, .12, .12, black)
        E("top patch", -.12, -.43, .88, .24, .29, .07, black)
    else:
        E("pale lower flank", .41, -.49, .24, .14, .33, .13, white)
    E("soiled rump", .03, -.89, .28, .39, .20, .20, dirty)
    E("neck", 0, .88, .47, .32, .43, .29, black)
    E("head", 0, 1.20, .48, .27, .31, .25, black)
    E("white face", .02, 1.43, .48, .15, .10, .15, white)
    E("muzzle", .02, 1.52, .36, .18, .12, .10, pink)
    E("near ear", .31, 1.10, .63, .19, .12, .07, black)
    E("far ear", -.31, 1.10, .63, .19, .12, .07, black)
    E("folded hind leg", .30, -.48, .14, .24, .41, .13, white)
    E("folded front leg", .26, .52, .13, .23, .37, .12, white)
    E("udder", .03, -.35, .17, .27, .27, .14, (0.52, .40, .37))
    cow.include("tail", rod(.033*s,
        start=(x, y-.94*s, BED_Z+.37*s),
        end=(x+.18*s, y-1.39*s, BED_Z+.03*s), color=dirty))
    scene.include("cow %02d" % index, cow)

# Higher x is closer to the oblique camera. The dark animal sits behind
# the foreground white cow, as in the reference.
make_cow(1, -5.55, .12, .94)
make_cow(2, -4.28, .02, 1.00)
make_cow(3, -3.00, -.02, 1.03)
make_cow(4, -1.72, -.05, 1.06)
make_cow(5, -.44, -.06, 1.08)
make_cow(6, .84, -.06, 1.10, True)
make_cow(7, 2.12, -.13, 1.12)
make_cow(8, 3.40, .12, 1.00)

worker = Asset("Worker in blue coveralls")
wx, wy = 5.8, 3.85
worker.include("torso", box((.43, .26, .67), center=(wx, wy, 1.20),
                             color=(.035, .15, .37)))
ellipsoid(worker, "head", (wx, wy, 1.73), (.14, .13, .18), (.40, .29, .23))
ellipsoid(worker, "hair", (wx, wy, 1.84), (.14, .13, .08), (.07, .06, .05))
for side in (-1, 1):
    worker.include("leg %d" % side,
        rod(.085, start=(wx+side*.12, wy, .35),
            end=(wx+side*.12, wy, .94), color=(.035, .08, .16)))
    worker.include("arm %d" % side,
        rod(.075, start=(wx+side*.23, wy, 1.42),
            end=(wx+side*.33, wy-.04, .99), color=(.04, .15, .34)))
scene.include("worker", worker)

realize(scene)

for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs["Base Color"].default_value[:3])
    if max(abs(rgb[i]-steel[i]) for i in range(3)) < .025:
        bsdf.inputs["Metallic"].default_value = .8
        bsdf.inputs["Roughness"].default_value = .25
    elif max(abs(rgb[i]-pink[i]) for i in range(3)) < .025:
        bsdf.inputs["Roughness"].default_value = .25
    else:
        bsdf.inputs["Roughness"].default_value = .84

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
background.inputs["Color"].default_value = (.70, .77, .84, 1)
background.inputs["Strength"].default_value = .52

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -1, 7), power=1600, size=8,
             target=(0, 0, 0), color=(.82, .90, 1.0))
area_emitter((-5, 2, 5), power=650, size=5,
             target=(0, 1, .5), color=(.88, .93, 1.0))
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
