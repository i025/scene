from sceneact import *
import bpy
import random

# Discrepancy ledger, normalized image coordinates, x right and y down:
# 1. Nearest cow: reference (.35,.36)-(.83,.84); rendered approximately
#    (.65,.58)-(1,.96), with its head outside the right frame or occluded.
#    The visible body is too far right and low. Shift the camera aim toward
#    the near end of the row and widen its view; this should move the cow
#    left and up while retaining its contact with the raised bed.
# 2. Rear wall and door: reference door (.32,0)-(.43,.20), rendered door
#    (.63,.19)-(.75,.53). The door is visible with wrong placement and size.
#    Move it along the wall and reduce its height. The reference wall/concrete
#    boundary is nearly horizontal at y=.10; the rendered boundary slopes
#    from roughly .30 to .45. Adjust wall orientation and boundary height
#    locally so the background is flatter and higher in the image.
# 3. Stall loops and foreground curb: reference loops occupy approximately
#    (0,.15)-(1,.72), with the curb running (0,.55) to (.72,1); rendered
#    loops occupy (0,.34)-(1,.92), curb (0,.61)-(.48,1). They are visible
#    but too low and steep. Camera aim and view width should lift the row,
#    while retaining full-height posts and connected divider loops. Reference
#    foreground bedding and manure at lower left are mostly absent in the
#    render; add an aisle surface at that edge. The worker visible at the
#    upper-right reference edge is outside or clipped from the render; its
#    exact depth is uncertain, so reposition it locally.
# Comparison at two depths: both the nearest cow and distant row lie lower
# than their reference counterparts; the wall boundary also lies too low.
# Preserve the repeated stall spacing, floor contact, the dark middle cow,
# blue structural members, and the overall receding direction. Corrections
# here are proposals and have not yet been verified in a new rendering.
#
# Inventory: raised concrete bed and foreground passage, roughly (0,.5)-(1,1);
# resting cows with broad flanks, folded legs, heads, ears, udders and tails,
# roughly (0,.25)-(.85,.86); repeated tubular stall loops and uprights,
# (0,.15)-(1,.73); concrete and light wall, blue door and columns (0,0)-(1,.3);
# clipped worker at right; thin bedding, wet marks and foreground manure.
# Rear cows and the portions outside the frame are uncertain.
# Estimated expanded meshes: architecture 18, seven cows about 150,
# ten divider paths 170 plus 20 supports and plates, floor details 42,
# worker 6: about 406 primitive meshes.

random.seed(21)
scene = Scene("Modern dairy barn")

concrete = (.39, .40, .38)
wallgray = (.43, .45, .44)
whitewall = (.72, .75, .74)
blue = (.025, .075, .15)
steel = (.52, .57, .58)
white = (.70, .68, .58)
black = (.018, .021, .019)
pink = (.36, .25, .23)

def ellipsoid(center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

building = Asset("Barn architecture")
building.include("concrete aisle", box((18, 20, .12), center=(0, 0, -.12),
                                      color=(.32, .31, .27)))
building.include("raised stall bed", box((4.5, 15, .24),
                                         center=(0, .3, .03), color=concrete))
building.include("front curb", box((.14, 15, .28), center=(-2.25, .3, .04),
                                   color=(.31, .32, .30)))
# The walls are continuous beyond the photograph's edges.
building.include("lower concrete wall", box((.16, 24, .95),
                    center=(4.2, 0, .42), color=wallgray))
building.include("upper pale wall", box((.16, 24, 3.6),
                    center=(4.2, 0, 2.69), color=whitewall))
building.include("blue double door", box((.19, 1.50, 1.85),
                    center=(4.08, 4.0, .88), color=blue))
building.include("door seam", box((.035, .025, 1.72),
                    center=(3.96, 4.0, .88), color=(.01, .03, .06)))
for j, y in enumerate((-8, -4.1, -.6, 3.25, 6.8, 10.5)):
    building.include("blue column %d" % j,
                     box((.24, .18, 4.4), center=(4.04, y, 2.16), color=blue))
building.include("horizontal wall beam", box((.16, 24, .10),
                    center=(4.03, 0, 2.15), color=blue))
scene.include("architecture", building)

def make_cow(idx, y, x=0, size=1, mostly_black=False):
    a = Asset("Resting Holstein %d" % idx)

    def P(u, v, w):
        return (x + u * size, y + v * size, .16 + w * size)

    def E(name, p, s, color):
        a.include(name, ellipsoid(P(*p), tuple(q * size for q in s), color))

    base = black if mostly_black else white
    E("barrel torso", (-.25, 0, .47), (1.04, .44, .44), base)
    E("shoulder", (.45, 0, .52), (.47, .39, .38), base)
    E("hindquarter", (-.94, 0, .38), (.42, .40, .35), base)
    E("neck", (.83, 0, .53), (.41, .30, .30), black)
    E("head", (1.14, -.02, .54), (.34, .23, .24), black)
    E("pale muzzle", (1.39, -.04, .45), (.18, .17, .13), (.52, .46, .42))
    E("wet nose", (1.52, -.04, .47), (.07, .13, .075), (.09, .085, .08))
    E("near ear", (1.05, -.27, .68), (.19, .11, .055), black)
    E("far ear", (1.08, .22, .67), (.18, .10, .055), black)
    E("folded hind leg", (-.73, -.32, .18), (.44, .17, .15),
      (.48, .46, .39) if not mostly_black else (.19, .18, .15))
    E("folded front leg", (.46, -.30, .16), (.43, .16, .12), base)
    E("front hoof", (.77, -.31, .14), (.13, .14, .08), (.18, .17, .15))
    E("udder", (-.55, -.20, .16), (.28, .18, .12), pink)

    if not mostly_black:
        spots = [
            (-.80, -.37, .50, .26, .08, .22),
            (-.47, -.40, .66, .22, .07, .20),
            (-.15, -.42, .48, .23, .06, .19),
            (.18, -.39, .65, .19, .07, .18),
            (.43, -.34, .45, .14, .07, .17),
            (-.62, -.13, .86, .29, .24, .06),
            (-.02, -.07, .89, .26, .22, .06),
            (.38, -.08, .82, .18, .18, .07),
        ]
        for k, (u, v, w, sx, sy, sz) in enumerate(spots):
            if (k + idx) % 5 != 0:
                E("coat patch %d" % k, (u, v, w), (sx, sy, sz), black)
    else:
        E("small pale shoulder patch", (.35, -.37, .67),
          (.14, .055, .12), white)

    a.include("tail", rod(.025 * size, start=P(-1.20, -.10, .35),
                          end=P(-1.46, -.35, -.02), color=(.22, .21, .17)))
    E("tail tuft", (-1.46, -.35, -.02), (.065, .045, .09), black)
    scene.include("cow %d" % idx, a)

for i, (yy, xx, ss, dark) in enumerate([
    (-3.15, -.05, 1.08, False),
    (-1.82, -.36, .99, True),
    (-.55, -.12, 1.00, False),
    (.77, -.34, .96, False),
    (2.08, -.08, .94, False),
    (3.35, -.38, .90, False),
    (4.60, -.18, .90, False),
]):
    make_cow(i, yy, xx, ss, dark)

stalls = Asset("Galvanized steel free-stall dividers")
for i in range(10):
    y = -4.55 + i * 1.31
    points = [
        (-1.78, y, .24), (-1.75, y, .66),
        (-1.63, y, .88), (-1.42, y, .98),
        (.94, y, .98), (1.16, y, .91),
        (1.27, y, .72), (1.22, y, .45),
        (1.08, y, .38)
    ]
    stalls.include("curved divider %d" % i,
                   sweep_tube(points=points, radius=.038, color=steel))
    stalls.include("support post %d" % i,
                   rod(.043, start=(1.48, y, .15),
                       end=(1.48, y, 1.20), color=steel))
    stalls.include("base plate %d" % i,
                   box((.20, .19, .035), center=(1.48, y, .16),
                       color=(.37, .40, .39)))
for j, (x, z) in enumerate(((1.48, 1.16), (-1.70, 1.02), (.88, .99))):
    stalls.include("continuous rail %d" % j,
                   rod(.037, start=(x, -5.3, z),
                       end=(x, 8.1, z), color=steel))
scene.include("stall equipment", stalls)

surface = Asset("Bedding and floor marks")
# A thin dirty bedding strip along the outside edge of the curb.
surface.include("foreground aisle bedding",
                box((1.35, 15, .012), center=(-3.05, .3, -.052),
                    color=(.35, .32, .24)))
for i in range(26):
    x = random.uniform(-2.08, 1.6)
    y = random.uniform(-5.5, 6.5)
    surface.include("bedding %d" % i,
        box((random.uniform(.07, .20), random.uniform(.025, .08), .008),
            center=(x, y, .156),
            color=random.choice([(.44, .40, .30), (.50, .46, .34),
                                 (.35, .34, .27)])))
for i in range(12):
    x = random.uniform(-4.0, -2.45)
    y = random.uniform(-5.5, 6.5)
    surface.include("damp mark %d" % i,
        ellipsoid((x, y, -.044),
                  (random.uniform(.10, .30), random.uniform(.08, .22), .008),
                  (.22, .23, .20)))
scene.include("surface details", surface)

worker = Asset("Worker in rear aisle")
worker.include("trousers", box((.23, .34, .72), center=(2.80, -5.4, .39),
                              color=(.08, .12, .19)))
worker.include("blue jacket", ellipsoid((2.80, -5.4, 1.02), (.18, .26, .40),
                                       (.035, .12, .27)))
worker.include("head", ellipsoid((2.80, -5.4, 1.49), (.13, .13, .17),
                                (.40, .29, .23)))
worker.include("hair", ellipsoid((2.80, -5.4, 1.60), (.14, .14, .08),
                                (.08, .07, .06)))
worker.include("arm", rod(.075, start=(2.79, -5.60, 1.23),
                          end=(2.55, -5.65, .91), color=(.035, .12, .27)))
scene.include("worker", worker)

realize(scene)

for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .75

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
background.inputs["Color"].default_value = (.68, .74, .78, 1)
background.inputs["Strength"].default_value = .52

set_view((-7.8, -9.2, 3.0), (.85, -.65, .80), lens=48, sensor=36)
area_emitter((-2, -3, 7), power=1200, size=7, target=(0, 0, 0),
             color=(.78, .87, 1))
area_emitter((2, 3, 5), power=700, size=6, target=(0, 0, .5),
             color=(.84, .90, 1))
