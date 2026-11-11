from sceneact import *
import bpy
import random

# Discrepancy ledger, normalized image coordinates:
# 1. Nearest cow and raised bed: reference cow roughly (.35,.36)-(.83,.84),
#    rendered cow roughly (.57,.48)-(.90,.88). Visible but too small and too
#    far right; the bed's near corner is also exposed at (.63,1). Increase the
#    scene's image scale and shift the camera aim along the row. The foreground
#    bed and cow should fill the lower center and extend beyond the frame.
# 2. Rear wall and blue door: reference wall spans the full image width, with
#    the door around (.32,.02)-(.43,.20). The rendered wall starts around
#    (.45,0), and the door is around (.58,.19)-(.67,.46). The left boundary
#    is visible with wrong placement and the door is too low. Extend the wall,
#    lower the camera elevation, and aim higher while keeping the wall behind
#    the stalls. Its exact continuation outside the photograph is uncertain.
# 3. Foreground aisle and stall row: reference curb runs from about (0,.55)
#    toward (.72,1); render runs from (.11,.54) to (.63,1), with too much
#    bare foreground. Both are visible with wrong framing. Enlarge the row
#    in frame and reduce camera height; retain floor contact and divider height.
#    The reference worker is clipped at (.94,.12)-(1,.38), whereas the rendered
#    worker is clipped at the right edge near (.98,.43); camera and worker
#    placement are adjusted together.
# The curb slopes down to the right in both images, although the render is
# steeper. Cows at near and far depths are both too small, supporting a camera
# scale correction; the wall edge and door also require local extension and
# placement. Keep the row direction, steel loops, and raised slab as anchors.
# The exact number and shape of heavily occluded rear cows are uncertain.
#
# Inventory: concrete aisle, raised bed and curb (lower half); multiple lying
# Holstein cows with tails, folded legs, udders, ears and heads (middle);
# repeating tubular galvanized dividers, posts and cross rails (middle and
# upper middle); concrete and pale wall, blue door and blue columns (top);
# partially clipped worker at far right; bedding and damp floor marks.
# Approximate expanded primitive count: building 13, cows 6*22=132,
# divider paths 8*17 plus posts and feet=152, floor marks 35, worker 6:
# roughly 340 meshes. Paths and cow parts remain named and editable.

random.seed(21)
scene = Scene("Dairy barn free stalls")

concrete = (.43, .44, .42)
wallgray = (.43, .45, .44)
whitewall = (.70, .73, .72)
blue = (.025, .085, .17)
steel = (.54, .59, .60)
white = (.72, .70, .60)
black = (.018, .021, .019)
pink = (.36, .25, .23)

def ellipsoid(center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

building = Asset("Barn architecture")
building.include("concrete aisle", box((16, 18, .12), center=(0, 0, -.12),
                                        color=(.32, .31, .27)))
building.include("raised stall bed", box((4.5, 14, .24), center=(0, .15, .03),
                                         color=concrete))
building.include("front curb", box((.14, 14, .28), center=(-2.25, .15, .04),
                                   color=(.34, .35, .33)))
building.include("lower concrete wall", box((.16, 22, 1.25),
                    center=(3.85, 0, .57), color=wallgray))
building.include("upper pale wall", box((.16, 22, 3.2),
                    center=(3.85, 0, 2.77), color=whitewall))
building.include("blue double door", box((.19, 1.65, 2.3),
                    center=(3.74, 1.85, 1.12), color=blue))
building.include("door seam", box((.035, .025, 2.05),
                    center=(3.62, 1.85, 1.15), color=(.012, .035, .07)))
for j, y in enumerate((-7.8, -4.1, -.6, 3.25, 6.8, 10.5)):
    building.include("blue column %d" % j,
                     box((.24, .18, 4.4), center=(3.69, y, 2.16), color=blue))
building.include("horizontal wall beam", box((.16, 22, .13),
                    center=(3.68, 0, 2.0), color=blue))
scene.include("architecture", building)

def make_cow(idx, y, x=0, size=1, mostly_black=False):
    a = Asset("Resting Holstein %d" % idx)

    def P(u, v, w):
        return (x + u*size, y + v*size, .16 + w*size)

    def E(name, p, s, color):
        a.include(name, ellipsoid(P(*p), tuple(q*size for q in s), color))

    base = black if mostly_black else white
    E("barrel torso", (-.25, 0, .47), (1.04, .44, .44), base)
    E("shoulder", (.45, 0, .52), (.47, .39, .38), base)
    E("hindquarter", (-.94, 0, .38), (.42, .40, .35), base)
    E("neck", (.83, 0, .53), (.41, .30, .30), black)
    E("head", (1.14, -.02, .54), (.34, .23, .24), black)
    E("pale muzzle", (1.39, -.04, .45), (.18, .17, .13), (.52, .46, .42))
    E("wet nose", (1.52, -.04, .47), (.07, .13, .075), (.12, .11, .10))
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
        E("small pale shoulder patch", (.35, -.37, .67), (.14, .055, .12), white)

    a.include("tail", rod(.025*size, start=P(-1.20, -.10, .35),
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
    y = -4.55 + i*1.31
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
for i in range(26):
    x = random.uniform(-2.08, 1.6)
    y = random.uniform(-5.5, 6.5)
    surface.include("bedding %d" % i,
        box((random.uniform(.07, .20), random.uniform(.025, .08), .008),
            center=(x, y, .156),
            color=random.choice([(.44,.40,.30), (.50,.46,.34), (.35,.34,.27)])))
for i in range(12):
    x = random.uniform(-4.0, -2.45)
    y = random.uniform(-5.5, 6.5)
    surface.include("damp mark %d" % i,
        ellipsoid((x, y, -.053),
                  (random.uniform(.10,.30), random.uniform(.08,.22), .008),
                  (.22,.23,.20)))
scene.include("surface details", surface)

worker = Asset("Worker in rear aisle")
worker.include("trousers", box((.23,.34,.72), center=(2.80,-4.35,.39),
                                color=(.08,.12,.19)))
worker.include("blue jacket", ellipsoid((2.80,-4.35,1.02), (.18,.26,.40),
                                         (.035,.12,.27)))
worker.include("head", ellipsoid((2.80,-4.35,1.49), (.13,.13,.17),
                                  (.40,.29,.23)))
worker.include("hair", ellipsoid((2.80,-4.35,1.60), (.14,.14,.08),
                                  (.08,.07,.06)))
worker.include("arm", rod(.075, start=(2.79,-4.55,1.23),
                           end=(2.55,-4.60,.91), color=(.035,.12,.27)))
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
background.inputs["Color"].default_value = (.68,.74,.78,1)
background.inputs["Strength"].default_value = .52

set_view((-7.8,-9.2,3.0), (.15,.55,1.02), lens=55, sensor=36)
area_emitter((-2,-3,7), power=1200, size=7, target=(0,0,0),
             color=(.78,.87,1))
area_emitter((2,3,5), power=700, size=6, target=(0,0,.5),
             color=(.84,.90,1))
