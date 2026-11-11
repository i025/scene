# Reference inventory and visual anchors (normalized image coordinates, approximate):
# - Foreground concrete bed and curb: x 0.00-1.00, y 0.56-1.00; dark bedding
#   and a manure-covered alley occupy the lower left. The curb rises toward the right.
# - Three prominent reclining Holstein cows: foreground x 0.34-0.83, y 0.36-0.94;
#   middle x 0.20-0.61, y 0.34-0.76; left x 0.00-0.36, y 0.31-0.70.
#   Their bodies overlap, with heads toward image right. Additional cows are partly
#   hidden behind the galvanized rails. Legs and far-side details are uncertain.
# - Repeating silver stall dividers: x 0.00-1.00, y 0.15-0.73. Long rails recede
#   across the image; curved ends and vertical supports overlap cows and beds.
# - Background wall: x 0.00-1.00, y 0.00-0.34. Pale upper panels, gray concrete
#   lower wall, dark blue posts and blue door at x 0.32-0.42.
# - Partially occluded worker at the far right, x 0.94-1.00, y 0.12-0.47.
# Dominant edges: the wall base and long rail edges run slightly downward to the
# right; stall ends and the curb recede diagonally into the left background.
#
# Estimated expanded primitives: architecture ~20, beds and alley ~12, stall pipes
# ~125 (including short segmented bends), cows ~100, worker ~10, bedding ~25;
# approximately 300 meshes in total. Hidden geometry is deliberately schematic.

from sceneact import *
import bpy
import math
import random

random.seed(12)

scene = Scene("Modern dairy free stall barn")

# Major dimensions, positions and camera are kept independent for revision.
BARN_LENGTH = 15.0
BARN_DEPTH = 10.0
BED_Z = 0.24
STALL_WIDTH = 1.22
STALL_COUNT = 8
CAMERA_POSITION = (7.2, -11.8, 5.1)
CAMERA_TARGET = (0.0, 0.65, 1.05)
CAMERA_LENS = 38

concrete = (0.43, 0.44, 0.43)
bed_color = (0.55, 0.56, 0.54)
wall_gray = (0.43, 0.45, 0.45)
wall_white = (0.76, 0.79, 0.79)
blue = (0.025, 0.105, 0.23)
steel = (0.57, 0.62, 0.62)
white = (0.78, 0.77, 0.70)
black = (0.035, 0.039, 0.036)
dirty = (0.28, 0.27, 0.22)
pink = (0.48, 0.36, 0.34)

architecture = Asset("Barn architecture")
architecture.include("floor", box((BARN_LENGTH, BARN_DEPTH, 0.18),
                                 center=(0, 0, -0.12), color=concrete))
architecture.include("rear concrete wall", box((15, 0.20, 1.58),
                                 center=(0, 4.6, 0.79), color=wall_gray))
architecture.include("rear upper wall", box((15, 0.16, 2.55),
                                 center=(0, 4.65, 2.84), color=wall_white))
for x in (-6.8, -3.75, 0.0, 3.8, 7.0):
    architecture.include("blue wall post %.1f" % x,
                         box((0.14, 0.21, 4.0), center=(x, 4.49, 2.0), color=blue))
for x in (-5.2, -1.8, 1.9, 5.5):
    architecture.include("upper panel seam %.1f" % x,
                         box((0.025, 0.025, 2.4), center=(x, 4.55, 2.85),
                             color=(0.54, 0.58, 0.59)))
# The door is a dark blue inset on the rear wall.
architecture.include("door dark opening", box((1.45, 0.06, 2.35),
                     center=(-3.0, 4.47, 1.18), color=(0.018, 0.045, 0.09)))
architecture.include("door left leaf", box((0.64, 0.05, 2.17),
                     center=(-3.34, 4.42, 1.13), color=blue))
architecture.include("door right leaf", box((0.64, 0.05, 2.17),
                     center=(-2.66, 4.42, 1.13), color=blue))
architecture.include("door crossbar", box((1.33, 0.05, 0.05),
                     center=(-3.0, 4.38, 1.10), color=(0.04, 0.10, 0.19)))
scene.include("architecture", architecture)

platform = Asset("Raised concrete resting platform")
platform.include("bed slab", box((13.3, 5.3, 0.25),
                 center=(0, 0.65, 0.105), color=bed_color))
platform.include("front curb", box((13.4, 0.17, 0.32),
                 center=(0, -2.02, 0.13), color=(0.36, 0.37, 0.35)))
platform.include("front alley", box((15, 2.4, 0.025),
                 center=(0, -3.28, -0.005), color=(0.28, 0.27, 0.21)))
# Fine, sparse bedding and wear visible at this scale.
for i in range(25):
    x = random.uniform(-6.3, 6.3)
    y = random.uniform(-1.95, 2.8)
    platform.include("bedding fleck %02d" % i,
                     box((random.uniform(.08, .3), .025, .008),
                         center=(x, y, BED_Z + .004),
                         color=(.39, .36, .28)))
scene.include("concrete beds and alley", platform)

def pipe(asset, name, a, b, r=.037):
    asset.include(name, rod(r, start=a, end=b, color=steel))

# Rails divide the beds. Their open, rounded outer ends are modeled with short
# tube segments, while long horizontal members provide the dominant perspective.
stalls = Asset("Galvanized stall dividers")
for i in range(STALL_COUNT):
    x = -5.5 + i * STALL_WIDTH
    # A division follows the length of the cow from the rear curb to the front.
    # The short angled sections approximate the characteristic loop bends.
    p = [
        (x, -1.76, .38), (x, -1.76, 1.10),
        (x, -1.62, 1.28), (x, -1.38, 1.34),
        (x, 1.75, 1.34), (x, 2.13, 1.24),
        (x, 2.30, 1.05), (x, 2.30, .47)
    ]
    for j in range(len(p) - 1):
        pipe(stalls, "divider %02d upper %02d" % (i, j), p[j], p[j+1])
    q = [(x, -1.55, .74), (x, .94, .74),
         (x, 1.45, .67), (x, 1.77, .53)]
    for j in range(len(q)-1):
        pipe(stalls, "divider %02d lower %02d" % (i, j), q[j], q[j+1], .032)
    pipe(stalls, "divider %02d foot" % i, (x, 2.30, .27), (x, 2.30, .47), .042)
# Continuous pipes link the separate loops across the row.
for j, (y, z) in enumerate(((1.8, 1.37), (2.35, .95), (3.05, 1.17))):
    pipe(stalls, "continuous rail %d" % j, (-6.6, y, z), (6.6, y, z), .038)
for x in (-6.1, -2.4, 1.3, 5.0):
    pipe(stalls, "rail upright %.1f" % x, (x, 3.05, .24), (x, 3.05, 1.17), .043)
scene.include("stall rail equipment", stalls)

def ellipsoid(asset, name, center, scale, color):
    node = ball(1.0, center=center, color=color)
    node.resize(scale, pivot=center)
    asset.include(name, node)

def make_cow(index, x, y, size=1.0, flip=False):
    # Cow axis runs along the stall, head pointing toward the barn interior.
    cow = Asset("Holstein cow %02d" % index)
    s = size
    def E(name, dx, dy, dz, sx, sy, sz, color):
        ellipsoid(cow, name, (x + dx*s, y + dy*s, BED_Z + dz*s),
                  (sx*s, sy*s, sz*s), color)

    E("white barrel", 0, 0, .48, .50, .97, .46, white)
    E("dark shoulder", 0, .51, .48, .46, .43, .40, black)
    E("hind black patch", -.19, -.52, .59, .34, .33, .27, black)
    E("side middle patch", .45, -.14, .56, .075, .31, .20, black)
    E("side upper patch", .38, .28, .73, .13, .23, .12, black)
    E("rump soiling", -.01, -.75, .30, .39, .23, .21, dirty)
    E("neck", 0, .84, .47, .32, .43, .29, black)
    E("head", 0, 1.17, .46, .27, .31, .25, black)
    E("white face blaze", 0, 1.39, .48, .17, .10, .17, white)
    E("moist muzzle", 0, 1.49, .35, .19, .12, .10, pink)
    E("near ear", -.32, 1.08, .62, .20, .12, .07, black)
    E("far ear", .32, 1.08, .62, .20, .12, .07, black)
    E("folded near hind leg", -.26, -.47, .16, .25, .42, .14, white)
    E("folded near front leg", -.23, .54, .13, .23, .38, .12, white)
    E("udder", 0, -.29, .17, .28, .26, .14, (0.57, .45, .42))
    cow.include("tail", rod(.035*s,
                start=(x, y-.90*s, BED_Z+.38*s),
                end=(x-.19*s, y-1.34*s, BED_Z+.04*s), color=dirty))
    scene.include("cow %02d" % index, cow)

# Positioned one cow per occupied bay. Their bodies overlap in the camera view.
make_cow(1, -4.8, -.08, .88)
make_cow(2, -3.55, -.08, .99)
make_cow(3, -2.25, -.10, 1.02)
make_cow(4, -.98, -.05, 1.04)
make_cow(5, .30, .02, 1.00)
make_cow(6, 1.55, .22, .90)
make_cow(7, 2.85, .38, .88)
make_cow(8, 4.15, .50, .85)

# Small worker in the distant aisle establishes the real-world rail scale.
worker = Asset("Worker in blue coveralls")
wx, wy = 5.55, 3.86
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

# Establish rough surface families after SceneAct has created its materials.
for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs["Base Color"].default_value[:3])
    if max(abs(rgb[i] - steel[i]) for i in range(3)) < .04:
        bsdf.inputs["Metallic"].default_value = .8
        bsdf.inputs["Roughness"].default_value = .27
    elif max(abs(rgb[i] - pink[i]) for i in range(3)) < .04:
        bsdf.inputs["Roughness"].default_value = .24
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
background.inputs["Strength"].default_value = .65

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -1, 7), power=1900, size=8,
             target=(0, 0, 0), color=(.82, .90, 1.0))
area_emitter((-5, 2, 5), power=800, size=5,
             target=(0, 1, .5), color=(.88, .93, 1.0))
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
