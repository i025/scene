from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image bounds (approximate):
# - Concrete resting platform and foreground passage: (0, .55)-(1, 1).
#   Raised curb, gray slab, sparse bedding and darker damp patches.
# - Receding galvanized stall dividers: (0, .13)-(1, .76).
#   Long horizontal tubes, rounded bends and vertical supports overlap the cows.
# - Several resting black-and-white cows: (0, .25)-(.88, .86).
#   Nearest animal has broad flank, folded legs, head facing right, and visible tail.
#   Farther animals are partially occluded by rails and one another.
# - Enclosing rear wall, blue door and dark blue columns: (0, 0)-(1, .25).
# - Partly occluded worker at far right: (.94, .03)-(1, .28).
# Hidden stall and animal details are uncertain.
#
# Expanded primitive estimate: architecture ~15, cows ~130, dividers ~120,
# floor details ~25, worker ~10; total approximately 300 meshes.

random.seed(21)
scene = Scene("Modern dairy free-stall barn")

concrete = (0.48, 0.49, 0.47)
wallgray = (0.50, 0.52, 0.52)
whitewall = (0.76, 0.79, 0.79)
blue = (0.035, 0.13, 0.26)
steel = (0.59, 0.64, 0.65)
darksteel = (0.37, 0.41, 0.41)
white = (0.77, 0.76, 0.66)
black = (0.035, 0.039, 0.037)
pink = (0.38, 0.28, 0.27)

# Building envelope and floor.
building = Asset("Barn architecture")
building.include("concrete aisle", box((13, 11, .12), center=(0, 0, -.12), color=(.39, .39, .35)))
building.include("raised stall bed", box((4.5, 9.4, .24), center=(0, .15, .03), color=concrete))
building.include("front curb", box((.14, 9.4, .28), center=(-2.25, .15, .04), color=(.36, .37, .35)))
building.include("rear lower concrete wall", box((.16, 11, 1.25), center=(3.85, .5, .57), color=wallgray))
building.include("rear upper wall", box((.16, 11, 2.6), center=(3.85, .5, 2.47), color=whitewall))
building.include("blue double door", box((.19, 1.65, 2.3), center=(3.74, 1.85, 1.12), color=blue))
building.include("door center seam", box((.035, .025, 2.05), center=(3.62, 1.85, 1.15), color=(.015, .06, .12)))
for j, y in enumerate((-4.1, -.6, 3.25, 5.6)):
    building.include("blue structural column %d" % j,
        box((.24, .18, 3.8), center=(3.69, y, 1.86), color=blue))
building.include("wall horizontal beam", box((.16, 11, .13), center=(3.68, .5, 2.0), color=blue))
scene.include("architecture", building)

# Cows lie along the x direction, with their heads toward the right side of
# the photograph. Individual sculptural parts remain editable.
def ellipsoid(radius, center, scale, color):
    n = ball(radius, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

def make_cow(idx, y, x=0, size=1.0, pattern=0):
    a = Asset("Cow %d" % idx)
    def P(u, v, w):
        return (x + u * size, y + v * size, .17 + w * size)
    def E(name, p, s, color):
        a.include(name, ellipsoid(1, P(*p), tuple(q * size for q in s), color))
    E("barrel torso", (-.25, 0, .49), (1.03, .43, .46), white)
    E("shoulder", (.47, 0, .55), (.48, .38, .40), white)
    E("hindquarter", (-.93, 0, .40), (.42, .39, .37), white)
    E("neck", (.86, 0, .51), (.40, .31, .29), black)
    E("head", (1.15, -.015, .51), (.34, .23, .24), black)
    E("pale muzzle", (1.40, -.04, .43), (.17, .18, .13), (.55, .49, .45))
    E("wet nose", (1.52, -.045, .45), (.075, .14, .075), (.16, .14, .14))
    E("near ear", (1.06, -.27, .67), (.20, .115, .055), black)
    E("far ear", (1.08, .22, .66), (.18, .10, .055), black)
    E("folded near hind leg", (-.74, -.32, .19), (.43, .17, .16), (.60, .57, .49))
    E("folded near front leg", (.46, -.29, .17), (.43, .16, .12), white)
    E("hoof", (.77, -.31, .15), (.13, .15, .08), (.20, .19, .17))
    E("udder", (-.58, -.18, .17), (.29, .18, .12), pink)
    # Broad irregular patch shapes are deliberately concentrated on the
    # visible flank and top; small dark islands break up their edges.
    spots = [
        (-.78, -.388, .55, .25, .048, .23),
        (-.42, -.409, .69, .22, .045, .20),
        (-.08, -.421, .51, .25, .047, .21),
        (.25, -.379, .72, .19, .05, .18),
        (.48, -.32, .48, .15, .045, .18),
        (-.58, -.15, .87, .30, .22, .052),
        (.02, -.08, .91, .25, .21, .045),
        (.38, -.10, .83, .18, .18, .055),
    ]
    for k, (u, v, w, sx, sy, sz) in enumerate(spots):
        if (k + pattern) % 5 != 0:
            E("black coat patch %d" % k, (u, v, w), (sx, sy, sz), black)
    a.include("tail", rod(.026 * size, start=P(-1.20, -.10, .36),
                            end=P(-1.43, -.29, .09), color=(.25, .24, .20)))
    E("tail switch", (-1.43, -.29, .08), (.07, .045, .10), black)
    scene.include("cow_%d" % idx, a)

# Nearest cow and receding group.
for i, (yy, xx, ss) in enumerate([
    (-3.15, -.05, 1.08), (-1.82, -.36, .98), (-.55, -.12, 1.00),
    (.77, -.34, .96), (2.08, -.08, .92), (3.35, -.38, .88)
]):
    make_cow(i, yy, xx, ss, i)

# Galvanized divider loops: each loop has a low entrance curve, long upper
# rail and a down-turned front. The open center preserves the stall gaps.
stalls = Asset("Galvanized free-stall dividers")
for i in range(8):
    y = -3.85 + i * 1.31
    pts = [
        (-1.78, y, .24), (-1.74, y, .68),
        (-1.58, y, .90), (-1.35, y, .98),
        (.95, y, .98), (1.19, y, .92),
        (1.29, y, .72), (1.25, y, .45),
        (1.10, y, .38), (.80, y, .42)
    ]
    stalls.include("curved divider %d" % i, sweep_tube(points=pts, radius=.042, color=steel))
    stalls.include("upright %d" % i,
        rod(.045, start=(1.48, y, .14), end=(1.48, y, 1.20), color=steel))
    stalls.include("foot plate %d" % i,
        box((.21, .20, .035), center=(1.48, y, .16), color=darksteel))
# Long, continuous rails join the stall structure across the row.
for j, (x, z) in enumerate(((1.48, 1.16), (-1.70, 1.02), (.88, .99))):
    stalls.include("long rail %d" % j,
        rod(.04, start=(x, -4.3, z), end=(x, 5.5, z), color=steel))
scene.include("stall equipment", stalls)

# Sparse bedding and wet discoloration on the slab and aisle.
surface = Asset("Bedding and floor marks")
for i in range(22):
    x = random.uniform(-2.05, 1.6)
    y = random.uniform(-4.2, 4.5)
    surface.include("scattered bedding %d" % i,
        box((random.uniform(.07, .22), random.uniform(.025, .09), .008),
            center=(x, y, .156), color=random.choice([(.49, .45, .34), (.55, .51, .39), (.38, .37, .30)])))
for i in range(10):
    x = random.uniform(-4.0, -2.45)
    y = random.uniform(-4.4, 4.4)
    surface.include("damp mark %d" % i,
        ellipsoid(1, (x, y, -.053), (random.uniform(.12, .35), random.uniform(.08, .25), .008),
                  (.24, .25, .23)))
scene.include("floor details", surface)

# Distant worker, partly hidden by railings.
worker = Asset("Worker at rear aisle")
worker.include("trousers", box((.23, .34, .72), center=(2.80, -3.9, .39), color=(.10, .15, .22)))
worker.include("blue jacket", ellipsoid(1, (2.80, -3.9, 1.02), (.18, .26, .40), (.08, .20, .40)))
worker.include("head", ellipsoid(1, (2.80, -3.9, 1.49), (.13, .13, .17), (.47, .34, .26)))
worker.include("hair", ellipsoid(1, (2.80, -3.9, 1.60), (.14, .14, .08), (.10, .09, .08)))
worker.include("arm", rod(.075, start=(2.79, -4.10, 1.23), end=(2.55, -4.15, .91), color=(.08, .20, .40)))
scene.include("worker", worker)

realize(scene)

# Assign physically distinctive surface responses after realization.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value = .77
# Locate the generated rail meshes by their asset/part names where available.
for obj in bpy.data.objects:
    lname = obj.name.lower()
    if any(term in lname for term in ("divider", "upright", "long rail", "foot plate")):
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                bsdf = slot.material.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Metallic"].default_value = .72
                    bsdf.inputs["Roughness"].default_value = .28

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
background.inputs["Color"].default_value = (.68, .75, .80, 1)
background.inputs["Strength"].default_value = .65

set_view((-7.8, -9.2, 4.1), (0.25, .35, .82), lens=43, sensor=36)
area_emitter((-2, -3, 7), power=1500, size=7, target=(0, 0, 0), color=(.78, .87, 1.0))
area_emitter((2, 3, 5), power=850, size=6, target=(0, 0, .5), color=(.83, .90, 1.0))
