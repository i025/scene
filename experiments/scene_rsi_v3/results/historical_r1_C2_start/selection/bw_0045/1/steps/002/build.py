# Reference inventory, normalized image bounds:
# - Concrete back wall and white upper panels: (0,0)-(1,.32), with blue
#   posts and a blue door near x=.38. Wall continues beyond the image.
# - Repeated galvanized tubular stall dividers: (0,.14)-(1,.78), overlapping
#   the animals. Their curved returns, open interiors and upright posts matter.
# - Several reclining black-and-white cows: (0,.25)-(.84,.92), with the
#   nearest cow showing a large flank, head, folded legs, udder and tail.
#   The animals toward the back and left are partly occluded.
# - Raised concrete bedding surface and front curb: (0,.52)-(1,1), with
#   sparse bedding; dirty aisle appears along the lower left edge.
# - Worker in blue at the far right, partly outside the frame and behind rails.
#
# Review of the first render: the scene was framed much too widely and from
# too high an angle, making the cows and dividers small and exposing the edges
# of a freestanding platform. The reference is a close, lower view into a
# continuous barn. The cow markings also appeared as isolated circular disks.
# This revision tightens and lowers the view, extends the floor and wall past
# the frame, and uses irregular procedural coat markings on the body surfaces.
#
# Approximate expanded primitive count: architecture and floor 25; dividers
# 9 * (15 + 2) + 3 = 156; seven cows * about 24 = 168; worker 8;
# bedding and floor marks 35. Total approximately 392 primitives.

from sceneact import *
import bpy
import math
import random

random.seed(17)
scene = Scene("Dairy barn free stalls")

concrete = (0.43, 0.44, 0.42)
wallgray = (0.38, 0.40, 0.39)
panelwhite = (0.72, 0.75, 0.74)
blue = (0.018, 0.065, 0.15)
steel = (0.52, 0.56, 0.56)
white = (0.72, 0.70, 0.62)
black = (0.025, 0.028, 0.025)
pink = (0.48, 0.34, 0.30)
hoof = (0.15, 0.14, 0.12)

def ellipsoid(center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    return obj

barn = Asset("Barn architecture")
barn.include("continuous concrete floor",
             box((28, 22, .16), center=(0, 0, -.14),
                 color=(.35, .36, .33)))
barn.include("lower concrete wall",
             box((28, .20, 1.50), center=(0, 5.15, .75),
                 color=wallgray))
barn.include("upper insulated panels",
             box((28, .18, 3.0), center=(0, 5.15, 3.0),
                 color=panelwhite))
for i, x in enumerate((-10.7, -7.1, -3.55, 0, 3.55, 7.1, 10.7)):
    barn.include("blue structural column %02d" % i,
                 box((.16, .25, 4.5), center=(x, 5.00, 2.25),
                     color=blue))
for i, x in enumerate((-6.0, -4.8, -2.4, -1.2, 1.2, 2.4, 4.8, 6.0)):
    barn.include("vertical panel seam %02d" % i,
                 box((.018, .025, 2.9), center=(x, 5.04, 2.95),
                     color=(.48, .51, .50)))
barn.include("blue door frame",
             box((1.55, .08, 2.20), center=(-2.45, 5.01, 1.10),
                 color=(.012, .045, .11)))
barn.include("blue double door",
             box((1.38, .025, 1.98), center=(-2.45, 4.95, 1.08),
                 color=(.02, .08, .18)))
barn.include("door middle stile",
             box((.055, .025, 1.98), center=(-2.45, 4.925, 1.08),
                 color=(.015, .052, .12)))
barn.include("door cross bar",
             box((1.38, .025, .055), center=(-2.45, 4.92, 1.04),
                 color=(.015, .052, .12)))
scene.include("barn architecture", barn)

beds = Asset("Raised resting beds and aisle")
beds.include("resting slab",
             box((22, 8.0, .20), center=(0, 1.15, .05),
                 color=concrete))
beds.include("front curb",
             box((22, .17, .28), center=(0, -2.88, .08),
                 color=(.48, .49, .46)))
beds.include("bedding aisle",
             box((22, 5.0, .025), center=(0, -5.42, -.04),
                 color=(.37, .34, .24)))
for i, x in enumerate((-7.2, -4.8, -2.4, 0, 2.4, 4.8, 7.2)):
    beds.include("slab joint %02d" % i,
                 box((.015, 7.9, .006), center=(x, 1.15, .154),
                     color=(.28, .29, .27)))
scene.include("raised beds", beds)

stalls = Asset("Galvanized stall partitions")
for j in range(10):
    y = -2.36 + j * .94
    points = [
        (-2.85, y, 1.35), (-1.95, y, 1.36),
        (.63, y, 1.36), (1.20, y, 1.33),
        (1.43, y, 1.19), (1.43, y, .84),
        (1.29, y, .70), (.82, y, .70)
    ]
    stalls.include("curved divider %02d" % j,
                   sweep_tube(points=points, radius=.038, color=steel))
    stalls.include("front upright %02d" % j,
                   rod(.043, start=(1.38, y, .16),
                       end=(1.38, y, 1.21), color=steel))
    stalls.include("rear upright %02d" % j,
                   rod(.035, start=(-2.55, y, .16),
                       end=(-2.55, y, 1.35), color=steel))
for i, (x, z) in enumerate(((-2.55, 1.36), (1.35, 1.31), (1.46, .42))):
    stalls.include("continuous cross rail %02d" % i,
                   rod(.035, start=(x, -2.9, z),
                       end=(x, 6.4, z), color=steel))
scene.include("stall equipment", stalls)

# Coat surfaces are tagged with a distinctive base color, replaced by a
# shared procedural material after realization. This makes irregular patches
# wrap around the body instead of protruding as separate round disks.
coat_tag = (.72, .70, .62)
dark_coat = (.07, .07, .06)

def make_cow(name, x, y, scale=1.0, variant=0):
    cow = Asset(name)
    s = scale

    def p(a, b, c):
        return (x + a*s, y + b*s, .16 + c*s)

    def blob(label, a, b, c, sx, sy, sz, col):
        cow.include(label, ellipsoid(p(a, b, c),
                                     (sx*s, sy*s, sz*s), col))

    base = coat_tag if variant != 1 else dark_coat
    blob("broad barrel", -.22, 0, .56, 1.02, .45, .44, base)
    blob("rounded rump", -.97, 0, .49, .48, .42, .38, base)
    blob("shoulder", .43, 0, .55, .52, .40, .42, base)
    blob("neck", .86, 0, .65, .45, .30, .31, black)
    blob("head", 1.19, -.02, .64, .34, .23, .24, black)
    blob("pale muzzle", 1.46, -.03, .53, .18, .19, .12,
         (.48, .43, .40))
    blob("wet nose", 1.57, -.035, .54, .09, .15, .07,
         (.12, .13, .12))
    blob("near ear", 1.12, -.26, .79, .18, .10, .06, black)
    blob("far ear", 1.12, .25, .79, .18, .10, .06, black)
    blob("near eye", 1.29, -.235, .71, .03, .018, .03,
         (.008, .008, .008))
    blob("folded front leg", .56, -.20, .21, .48, .18, .13, base)
    blob("front hoof", .94, -.22, .19, .17, .15, .085, hoof)
    blob("folded hind leg", -.82, -.17, .22, .44, .24, .15, base)
    blob("hind hoof", -1.15, -.25, .18, .18, .14, .09, hoof)
    blob("udder", -.64, -.10, .18, .30, .22, .15, pink)
    cow.include("tail",
                sweep_tube(points=[p(-1.30, .10, .44),
                                   p(-1.46, -.02, .20),
                                   p(-1.56, -.14, .04),
                                   p(-1.78, -.25, .025)],
                           radius=.023*s, color=(.24, .22, .18)))
    return cow

positions = [
    (-.15, -1.87, 1.08, 0),
    (-.43, -.92, 1.04, 1),
    (-.68, .04, 1.01, 0),
    (-.40, 1.02, .99, 1),
    (-.73, 1.98, .97, 0),
    (-.40, 2.93, .95, 1),
    (-.76, 3.87, .92, 0),
    (-.48, 4.79, .90, 0),
]
for k, (x, y, s, v) in enumerate(positions):
    scene.include("cow %02d" % k, make_cow("Holstein %02d" % k, x, y, s, v))

surface = Asset("Bedding and floor marks")
for i in range(24):
    x = random.uniform(-6, 5)
    y = random.uniform(-5.7, -3.0)
    length = random.uniform(.14, .45)
    angle = random.uniform(-1.0, 1.0)
    surface.include("straw %02d" % i,
                    rod(.006, start=(x, y, -.023),
                        end=(x + length*math.cos(angle),
                             y + length*math.sin(angle), -.022),
                        color=(.55, .47, .29)))
for i in range(12):
    x = random.uniform(1.7, 5.0)
    y = random.uniform(-2.55, 1.2)
    surface.include("damp patch %02d" % i,
                    ellipsoid((x, y, .154),
                              (random.uniform(.07, .23),
                               random.uniform(.05, .14), .005),
                              (.25, .27, .25)))
scene.include("bedding and marks", surface)

worker = Asset("Worker in blue coveralls")
worker.include("torso", ellipsoid((5.35, 4.70, 1.29),
                                  (.22, .15, .38), (.045, .13, .25)))
worker.include("head", ellipsoid((5.35, 4.69, 1.78),
                                 (.12, .11, .16), (.38, .27, .21)))
worker.include("hair", ellipsoid((5.35, 4.70, 1.90),
                                 (.13, .11, .07), (.06, .05, .04)))
worker.include("left leg", rod(.08, start=(5.25, 4.70, .15),
                                end=(5.28, 4.70, .98), color=(.08, .10, .14)))
worker.include("right leg", rod(.08, start=(5.45, 4.70, .15),
                                 end=(5.41, 4.70, .98), color=(.08, .10, .14)))
worker.include("left arm", rod(.065, start=(5.17, 4.70, 1.49),
                                end=(5.04, 4.57, 1.07), color=(.045, .13, .25)))
worker.include("right arm", rod(.065, start=(5.52, 4.70, 1.48),
                                 end=(5.61, 4.56, 1.09), color=(.045, .13, .25)))
scene.include("worker", worker)

realize(scene)

# Shared irregular black-and-white hide material.
coat = bpy.data.materials.new("Irregular Holstein hide")
coat.use_nodes = True
nodes = coat.node_tree.nodes
links = coat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value = .82
tex = nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 3.5
tex.inputs["Detail"].default_value = 3.0
tex.inputs["Roughness"].default_value = .7
tex.inputs["Distortion"].default_value = .55
coord = nodes.new("ShaderNodeTexCoord")
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .43
ramp.color_ramp.elements[0].color = (.018, .021, .018, 1)
ramp.color_ramp.elements[1].position = .48
ramp.color_ramp.elements[1].color = (.72, .70, .62, 1)
links.new(coord.outputs["Generated"], tex.inputs["Vector"])
links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for i, mat in enumerate(obj.data.materials):
        if not mat:
            continue
        c = mat.diffuse_color
        if abs(c[0]-.72) < .015 and abs(c[1]-.70) < .015 and abs(c[2]-.62) < .015:
            obj.data.materials[i] = coat

for mat in bpy.data.materials:
    if mat == coat:
        continue
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    c = bs.inputs["Base Color"].default_value
    if abs(c[0]-.52) < .025 and abs(c[1]-.56) < .025 and abs(c[2]-.56) < .025:
        bs.inputs["Metallic"].default_value = .72
        bs.inputs["Roughness"].default_value = .28
    elif abs(c[0]-.12) < .015 and abs(c[1]-.13) < .015:
        bs.inputs["Roughness"].default_value = .23
    else:
        bs.inputs["Roughness"].default_value = .82

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
background.inputs["Color"].default_value = (.68, .73, .78, 1)
background.inputs["Strength"].default_value = .55

set_view((3.4, -10.8, 3.7), (0, .35, .95), lens=53)
area_emitter((0, -1, 7), power=1500, size=8,
             target=(0, 0, 0), color=(.82, .88, 1.0))
area_emitter((-5, 3, 5), power=650, size=6,
             target=(0, 1, 0), color=(.87, .92, 1.0))
