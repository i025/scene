# Reference inventory, estimated normalized image bounds:
# - Raised concrete resting platform: (0.00, 0.46)-(1.00, 1.00), partly hidden
#   by cows; front curb separates it from the straw-covered aisle.
# - Recumbent Holstein cows: approximately (0.00, 0.27)-(0.84, 0.93).
#   The nearest cow has a broad white body, black patches, folded legs, an udder,
#   a dark head, pale muzzle, ears and a tail. Other cows overlap and are partly
#   occluded by both their neighbors and the rails.
# - Galvanized tubular stall dividers: (0.00, 0.15)-(1.00, 0.82). Repeated
#   elongated curved rails and upright supports overlap the cows. Far ends are
#   obscured or outside the frame.
# - Back wall: (0.00, 0.00)-(1.00, 0.32), gray concrete below pale panels, with
#   blue structural posts and a blue door near the left center.
# - A partially visible worker stands at the far right, behind the rails.
# - Foreground aisle contains sparse straw and patches of darker wet concrete.
#
# Expanded primitive estimate: architecture ~18; platform and aisle ~12;
# eight stall dividers at 15 primitives each ~120; cross rails and uprights
# ~20; five cows at about 19 primitives each ~95; worker ~8; scattered straw
# and floor marks ~35. Total approximately 310 mesh primitives.
# Cows and stall layout remain separate named assets with editable child parts.

from sceneact import *
import bpy
import math
import random

random.seed(17)

scene = Scene("Modern dairy free-stall barn")

concrete = (0.48, 0.49, 0.47)
curbmat = (0.52, 0.53, 0.51)
floorgray = (0.43, 0.44, 0.41)
wallgray = (0.40, 0.42, 0.42)
panelwhite = (0.72, 0.75, 0.75)
blue = (0.025, 0.12, 0.27)
steel = (0.57, 0.61, 0.61)
white = (0.79, 0.77, 0.69)
black = (0.035, 0.038, 0.034)
pink = (0.53, 0.38, 0.34)
hoof = (0.19, 0.18, 0.16)
straw = (0.48, 0.43, 0.29)

def ellipsoid(center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

# Enclosing architecture and the long working surfaces.
building = Asset("Barn architecture")
building.include("concrete floor", box((16, 15, .16), center=(0, 0, -.13), color=floorgray))
building.include("rear concrete wall", box((16, .20, 1.55), center=(0, 5.1, .77), color=wallgray))
building.include("upper light wall panels", box((16, .18, 2.6), center=(0, 5.1, 2.85), color=panelwhite))
for x in (-7.1, -3.55, 0, 3.55, 7.1):
    building.include("blue structural post %.2f" % x,
                     box((.15, .24, 4.3), center=(x, 4.96, 2.15), color=blue))
for x in (-6.0, -4.8, -2.4, -1.2, 1.2, 2.4, 4.8, 6.0):
    building.include("panel seam %.2f" % x,
                     box((.024, .025, 2.55), center=(x, 4.98, 2.85), color=(.47,.51,.52)))
building.include("blue door", box((1.40, .07, 2.15), center=(-2.45, 4.94, 1.08), color=blue))
building.include("door inset upper", box((1.15, .025, .79), center=(-2.45, 4.89, 1.51), color=(.035,.16,.34)))
building.include("door inset lower", box((1.15, .025, .82), center=(-2.45, 4.89, .55), color=(.025,.12,.27)))
building.include("door horizontal rail", box((1.3,.045,.065), center=(-2.45,4.86,1.02), color=(.10,.23,.38)))
scene.include("barn", building)

platform = Asset("Raised concrete beds")
platform.include("platform slab", box((13, 6.8, .22), center=(0, .65, .05), color=concrete))
platform.include("front curb", box((13, .18, .28), center=(0, -2.79, .10), color=curbmat))
for x in (-4.8, -2.4, 0, 2.4, 4.8):
    platform.include("slab joint %.1f" % x, box((.018,6.65,.008), center=(x,.65,.165), color=(.31,.32,.30)))
scene.include("resting platform", platform)

# Stall dividers lie in vertical X/Z planes. Each has a long open side and
# curved return, so the occupied space and gaps remain visible between cows.
stalls = Asset("Galvanized stall partitions")
for j in range(8):
    y = -2.35 + j * .96
    pts = [(-2.65,y,1.34), (-1.95,y,1.36), (.65,y,1.36),
           (1.25,y,1.32), (1.44,y,1.18), (1.43,y,.80),
           (1.27,y,.68), (.83,y,.69)]
    stalls.include("curved divider %02d" % j,
                   sweep_tube(points=pts, radius=.038, color=steel))
    stalls.include("floor upright %02d" % j,
                   rod(.044, start=(1.38,y,.17), end=(1.38,y,1.19), color=steel))
    stalls.include("rear foot %02d" % j,
                   rod(.035, start=(-2.40,y,.17), end=(-2.40,y,1.35), color=steel))
# Rails running across the row provide continuity and overlapping depth.
for x,z in [(-2.40,1.36), (1.33,1.32)]:
    stalls.include("cross rail %.2f" % x,
                   rod(.037, start=(x,-2.65,z), end=(x,4.78,z), color=steel))
scene.include("stall equipment", stalls)

# A cow is built from broad smooth volumes and visible irregular patches.
# Neighboring cows share the same scale but vary their markings and poses.
def make_cow(name, x, y, scale=1.0, variant=0):
    cow = Asset(name)
    s = scale
    def point(a,b,c):
        return (x+a*s, y+b*s, .17+c*s)
    def blob(label, a,b,c, sx,sy,sz, col):
        cow.include(label, ellipsoid(point(a,b,c), (sx*s,sy*s,sz*s), col))

    blob("barrel", -.25,0,.55, 1.02,.43,.43, white)
    blob("rounded rump", -1.00,0,.48, .49,.41,.37, white)
    blob("shoulder", .42,0,.56, .53,.41,.43, white)
    blob("neck", .88,0,.64, .48,.30,.32, black)
    blob("head", 1.20,-.02,.62, .36,.24,.25, black)
    blob("muzzle", 1.48,-.03,.53, .18,.20,.13, (0.51,.46,.43))
    blob("wet nose", 1.59,-.04,.54, .09,.15,.075, (0.20,.20,.19))
    blob("near ear", 1.16,-.27,.78, .19,.105,.065, black)
    blob("far ear", 1.11,.27,.78, .18,.10,.06, black)
    blob("near eye", 1.31,-.234,.71, .035,.020,.035, (0.01,.01,.01))
    blob("folded front leg", .57,-.20,.22, .47,.18,.14, white)
    blob("front hoof", .93,-.22,.20, .18,.16,.09, hoof)
    blob("folded hind leg", -.83,-.16,.22, .44,.25,.16, white)
    blob("hind hoof", -1.15,-.27,.18, .19,.14,.09, hoof)
    blob("udder", -.67,-.08,.20, .31,.24,.17, pink)

    # Visible side patches: thin ellipsoids on the camera-facing side of barrel.
    patches = [(-.62,-.403,.65,.29,.035,.23),
               (-.05,-.424,.56,.26,.035,.27),
               (.43,-.382,.70,.22,.035,.23),
               (-.95,-.34,.39,.25,.035,.16)]
    if variant % 2:
        patches = [(-.76,-.39,.66,.38,.035,.20),
                   (-.23,-.426,.46,.24,.035,.22),
                   (.27,-.405,.64,.34,.035,.27)]
    for i,(a,b,c,sx,sy,sz) in enumerate(patches):
        blob("side marking %d" % i,a,b,c,sx,sy,sz,black)
    blob("top marking", -.22,.04,.94, .36,.26,.028, black)
    tailpts = [point(-1.32,.10,.45), point(-1.48,-.03,.20),
               point(-1.57,-.12,.06), point(-1.77,-.25,.045)]
    cow.include("tail", sweep_tube(points=tailpts, radius=.025*s, color=(.25,.23,.19)))
    return cow

# Bodies point toward the head rail. The nearest animals have the largest
# visible area; rear animals are partially obscured by the intervening rails.
cow_positions = [
    (-.15,-1.86,1.03,0),
    (-.42,-.86,1.00,1),
    (-.65,.15,.98,0),
    (-.38,1.18,.95,1),
    (-.70,2.18,.92,0),
    (-.35,3.15,.90,1),
    (-.75,4.05,.86,0),
]
for k,(x,y,s,v) in enumerate(cow_positions):
    scene.include("cow %02d" % (k+1), make_cow("Holstein %02d" % (k+1),x,y,s,v))

# Sparse, thin bedding strands and dark wet marks keep the floor readable.
bedding = Asset("Bedding and aisle marks")
for i in range(22):
    x = random.uniform(-6.0, 5.0)
    y = random.uniform(-5.3, -2.95)
    length = random.uniform(.18,.55)
    angle = random.uniform(-.5,.5)
    bedding.include("straw strand %02d" % i,
        rod(.008, start=(x,y,.005),
            end=(x+length*math.cos(angle),y+length*math.sin(angle),.006),
            color=straw))
for i in range(12):
    x = random.uniform(1.7,5.3)
    y = random.uniform(-2.5,.2)
    bedding.include("wet floor patch %02d" % i,
        ellipsoid((x,y,.174), (random.uniform(.08,.25),random.uniform(.06,.16),.006),
                  (.28,.30,.28)))
scene.include("bedding and marks", bedding)

# A worker in the far aisle provides a human scale reference.
worker = Asset("Worker in blue coveralls")
worker.include("torso", ellipsoid((5.35,4.65,1.29),(.23,.15,.39),(.07,.19,.35)))
worker.include("head", ellipsoid((5.35,4.64,1.79),(.13,.12,.17),(.42,.29,.23)))
worker.include("dark hair", ellipsoid((5.35,4.65,1.91),(.14,.12,.08),(.07,.06,.05)))
worker.include("left leg", rod(.085,start=(5.25,4.65,.15),end=(5.28,4.65,.98),color=(.10,.13,.19)))
worker.include("right leg", rod(.085,start=(5.46,4.65,.15),end=(5.42,4.65,.98),color=(.10,.13,.19)))
worker.include("left arm", rod(.07,start=(5.17,4.65,1.50),end=(5.05,4.55,1.05),color=(.07,.19,.35)))
worker.include("right arm", rod(.07,start=(5.51,4.65,1.48),end=(5.61,4.53,1.09),color=(.07,.19,.35)))
scene.include("worker", worker)

realize(scene)

# Configure material response after realization. SceneAct creates one material
# for each finish; classify by approximate base color.
for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        c = bsdf.inputs["Base Color"].default_value
        if abs(c[0]-.57)<.04 and abs(c[1]-.61)<.04 and abs(c[2]-.61)<.04:
            bsdf.inputs["Metallic"].default_value = .72
            bsdf.inputs["Roughness"].default_value = .27
        elif c[0] < .08 and c[1] < .08 and c[2] < .08:
            bsdf.inputs["Roughness"].default_value = .64
        else:
            bsdf.inputs["Roughness"].default_value = .83

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
background.inputs["Color"].default_value = (0.69,0.76,0.82,1)
background.inputs["Strength"].default_value = .65

set_view((7.7,-12.8,5.7), (0,.65,.75), lens=38)
area_emitter((0,-1,7), power=1800, size=8, target=(0,0,0), color=(.80,.88,1.0))
area_emitter((-5,3,5), power=900, size=6, target=(0,1,0), color=(.86,.92,1.0))
