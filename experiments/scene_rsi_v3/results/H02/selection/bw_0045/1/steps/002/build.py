# Reference anchors, estimated in normalized image coordinates:
# Rear wall and door: wall fills the top; door x .32-.43, y .04-.24.
# Rails span the frame from roughly y .15 to .69; their long edges slope gently
# downward to the right. Rounded dividers overlap cows.
# Foreground cow: x .35-.82, y .37-.92, with rump left and head right.
# Two other large, partly overlapping cows occupy x 0-.58, y .30-.76.
# Curb crosses the lower image, from approximately (0,.57) to (.69,1).
# Worker is cropped at the far right, approximately x .94-1, y .12-.47.
# Far-side bodies, feet and connections hidden by the rails remain uncertain.
#
# Comparison with the successful prior render:
# 1. Largest discrepancy: cows occupy only about y .44-.74 and are too small;
#    the reference's nearest cow extends to about y .92. Increase camera lens
#    from 38 to 57 and move the target toward the occupied stalls. This should
#    enlarge the cows and crop the platform edges out of the image.
# 2. The prior render shows empty gray space above and left of the building;
#    the reference is filled edge to edge by the barn. Extend the rear wall and
#    floor and lower the camera to reduce the visible top-down floor area.
# 3. The prior cows appear as a row of small, mostly white oval backs; the
#    reference has three large overlapping side silhouettes, including a dark
#    middle cow. Increase cow size and place a broad dark patch on the middle
#    animal; use side patches on the camera-facing flanks.
# 4. Prior rails appear thin and numerous across the animals. Increase the
#    visible pipe radius modestly and retain the rounded divider contours.
# The door and blue posts remain background anchors, while their precise
# projection may shift with the camera correction.
#
# Expanded primitive estimate: architecture 16, slab and alley 5, rails about
# 120, cows about 135, worker 7, surface marks 35: approximately 318 meshes.

from sceneact import *
import bpy
import random

random.seed(19)
scene = Scene("Modern dairy free stall barn")

# Camera parameters are independent of the asset dimensions.
CAMERA_POSITION = (7.6, -12.7, 3.8)
CAMERA_TARGET = (-0.8, 0.35, 1.06)
CAMERA_LENS = 57
BED_Z = 0.24
STALL_WIDTH = 1.24
STALL_COUNT = 9

concrete = (0.39, 0.40, 0.39)
bed_color = (0.48, 0.49, 0.47)
wall_gray = (0.37, 0.39, 0.39)
wall_white = (0.72, 0.75, 0.75)
blue = (0.018, 0.075, 0.17)
steel = (0.52, 0.57, 0.57)
white = (0.73, 0.71, 0.64)
black = (0.018, 0.022, 0.020)
dirty = (0.25, 0.23, 0.18)
pink = (0.45, 0.34, 0.31)

architecture = Asset("Barn architecture")
architecture.include("floor", box((30, 22, .16), center=(0, 0, -.12), color=concrete))
architecture.include("lower concrete wall", box((30, .20, 1.55),
                     center=(0, 4.6, .775), color=wall_gray))
architecture.include("upper wall panels", box((30, .16, 4.0),
                     center=(0, 4.65, 3.55), color=wall_white))
for i, x in enumerate((-9.7, -6.8, -3.75, 0, 3.8, 7.0, 10.5)):
    architecture.include("blue structural post %d" % i,
                         box((.14, .22, 5.55), center=(x, 4.48, 2.78), color=blue))
for i, x in enumerate((-8.2, -5.2, -1.8, 1.9, 5.5, 8.9)):
    architecture.include("panel seam %d" % i,
                         box((.022, .025, 3.9), center=(x, 4.54, 3.5),
                             color=(.52, .56, .56)))
architecture.include("door opening", box((1.45, .06, 2.35),
                     center=(-3.0, 4.46, 1.18), color=(.014, .035, .07)))
architecture.include("door left leaf", box((.64, .05, 2.17),
                     center=(-3.34, 4.41, 1.13), color=blue))
architecture.include("door right leaf", box((.64, .05, 2.17),
                     center=(-2.66, 4.41, 1.13), color=blue))
architecture.include("door crossbar", box((1.33, .05, .05),
                     center=(-3, 4.37, 1.1), color=(.035, .08, .15)))
scene.include("architecture", architecture)

platform = Asset("Raised concrete resting beds and walkway")
platform.include("bed slab", box((24, 5.3, .25),
                 center=(0, .65, .105), color=bed_color))
platform.include("front curb", box((24, .18, .32),
                 center=(0, -2.02, .13), color=(.31, .32, .30)))
platform.include("manure alley", box((30, 4.2, .025),
                 center=(0, -4.15, -.015), color=(.28, .27, .20)))
# Sparse, low-contrast bedding and soiled areas.
for i in range(35):
    x = random.uniform(-8, 8)
    y = random.uniform(-1.90, 2.7)
    platform.include("bedding fleck %02d" % i,
                     box((random.uniform(.10, .34), random.uniform(.025, .08), .008),
                         center=(x, y, BED_Z + .005),
                         color=(.34, .32, .26)))
scene.include("beds and walkway", platform)

def pipe(asset, name, a, b, radius=.045):
    asset.include(name, rod(radius, start=a, end=b, color=steel))

stalls = Asset("Galvanized steel stall dividers")
for i in range(STALL_COUNT):
    x = -5.8 + i * STALL_WIDTH
    p = [(x, -1.76, .30), (x, -1.76, 1.06),
         (x, -1.69, 1.20), (x, -1.52, 1.30),
         (x, -1.30, 1.34), (x, 1.72, 1.34),
         (x, 2.03, 1.27), (x, 2.22, 1.10),
         (x, 2.24, .48)]
    for j in range(len(p)-1):
        pipe(stalls, "divider %02d outer %02d" % (i, j), p[j], p[j+1])
    q = [(x, -1.57, .77), (x, .80, .77),
         (x, 1.29, .71), (x, 1.62, .57)]
    for j in range(len(q)-1):
        pipe(stalls, "divider %02d inner %02d" % (i, j), q[j], q[j+1], .038)
    pipe(stalls, "divider %02d foot" % i, (x, 2.24, .25), (x, 2.24, .48))
for j, (y, z) in enumerate(((1.80, 1.37), (2.35, .95), (3.05, 1.18))):
    pipe(stalls, "continuous cross rail %d" % j, (-10, y, z), (10, y, z), .043)
for i, x in enumerate((-8, -4, 0, 4, 8)):
    pipe(stalls, "cross rail upright %d" % i, (x, 3.05, .24), (x, 3.05, 1.18))
scene.include("stall rail equipment", stalls)

def ellipsoid(asset, name, center, scale, color):
    node = ball(1.0, center=center, color=color)
    node.resize(scale, pivot=center)
    asset.include(name, node)

def make_cow(index, x, y, size=1.0, dark_body=False):
    cow = Asset("Reclining Holstein cow %02d" % index)
    s = size
    def E(name, dx, dy, dz, sx, sy, sz, color):
        ellipsoid(cow, name,
                  (x + dx*s, y + dy*s, BED_Z + dz*s),
                  (sx*s, sy*s, sz*s), color)

    E("barrel", 0, 0, .48, .53, 1.02, .47, black if dark_body else white)
    E("shoulder", 0, .56, .49, .46, .44, .40, black)
    if not dark_body:
        # Thin ellipsoids sit on the visible side and top of the white barrel.
        E("large flank patch", .48, -.24, .56, .095, .31, .22, black)
        E("upper flank patch", .37, .24, .78, .16, .23, .09, black)
        E("small flank patch", .50, .13, .53, .045, .13, .13, black)
        E("rump dark patch", .19, -.69, .60, .28, .22, .23, black)
    else:
        E("pale lower flank", .40, -.49, .25, .15, .34, .14, white)
    E("dirty rump", 0, -.83, .30, .43, .25, .23, dirty)
    E("neck", 0, .88, .47, .33, .43, .29, black)
    E("head", 0, 1.19, .48, .27, .32, .25, black)
    E("white face blaze", .02, 1.42, .48, .16, .10, .16, white)
    E("muzzle", .02, 1.52, .37, .18, .12, .10, pink)
    E("near ear", .31, 1.10, .63, .19, .12, .07, black)
    E("far ear", -.31, 1.10, .63, .19, .12, .07, black)
    E("folded hind leg", .30, -.47, .14, .25, .43, .13, white)
    E("folded front leg", .26, .55, .13, .24, .38, .12, white)
    E("udder", .03, -.35, .17, .27, .27, .14, (0.52, .40, .37))
    cow.include("tail", rod(.035*s,
                start=(x, y-.94*s, BED_Z+.37*s),
                end=(x+.18*s, y-1.38*s, BED_Z+.03*s), color=dirty))
    scene.include("cow %02d" % index, cow)

make_cow(1, -5.20, -.03, 1.00)
make_cow(2, -3.93, -.06, 1.06)
make_cow(3, -2.65, -.08, 1.11, True)
make_cow(4, -1.36, -.12, 1.12)
make_cow(5, -.06, -.02, 1.06)
make_cow(6, 1.23, .13, 1.00)
make_cow(7, 2.52, .28, .96)
make_cow(8, 3.80, .42, .92)

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

for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs["Base Color"].default_value[:3])
    if max(abs(rgb[i] - steel[i]) for i in range(3)) < .025:
        bsdf.inputs["Metallic"].default_value = .8
        bsdf.inputs["Roughness"].default_value = .25
    elif max(abs(rgb[i] - pink[i]) for i in range(3)) < .025:
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
