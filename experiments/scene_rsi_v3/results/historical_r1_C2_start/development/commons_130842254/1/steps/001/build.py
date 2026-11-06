# Reference inventory (normalized image coordinates, approximate):
# - Pale plaster walls and stone floor: entire image; rear walls meet above the
#   large dark hearth. Floor is visible around and beneath the central table.
# - Rear hearth (0.40,0.22)-(0.86,0.46): wide low black arched recess,
#   stone arch surround, iron grate and dark cookware; much is shadowed.
# - Left cooking counter (0.00,0.27)-(0.37,0.51): pale masonry top with
#   dark arched openings and a row of ceramic vessels.
# - Right recess (0.87,0.32)-(1.00,0.59): dark small opening and pots.
# - Central stone chimney (0.43,0.22)-(0.59,0.62): tall square shaft,
#   projecting stepped base, tiered pyramidal cap and round finial.
# - Wooden worktable (0.18,0.46)-(0.73,0.89): rectangular tabletop and
#   legs, raised inner wooden panels enclosing chimney, overlapping dishes.
# - Tableware: numerous plates, bowls, jugs and food on the tabletop and
#   inner shelf. Their exact contents and occluded back sides are uncertain.
# Estimated primitives: floor ~110, architecture ~65, chimney ~13,
# table ~20, dishes and food ~90, total approximately 300 meshes.

from sceneact import *
import bpy
import math
import random

random.seed(12)
scene = Scene("Historic kitchen")
stone = (0.49, 0.45, 0.38)
stone_light = (0.64, 0.61, 0.54)
mortar = (0.35, 0.33, 0.29)
plaster = (0.74, 0.77, 0.74)
dark = (0.095, 0.085, 0.068)
iron = (0.12, 0.115, 0.10)
wood = (0.37, 0.22, 0.12)
wood_edge = (0.27, 0.15, 0.08)
cream = (0.72, 0.69, 0.59)
ochre = (0.53, 0.31, 0.13)
grey = (0.35, 0.37, 0.34)

def add(parent, name, shape):
    parent.include(name, shape)

def arch_band(parent, prefix, cx, y, spring, radius, width, color, segments=11):
    # Chord segments form a low stone arch in the vertical XZ plane.
    for i in range(segments):
        a = math.pi * i / segments
        b = math.pi * (i + 1) / segments
        p = (cx + radius * math.cos(a), y, spring + radius * 0.48 * math.sin(a))
        q = (cx + radius * math.cos(b), y, spring + radius * 0.48 * math.sin(b))
        add(parent, prefix + str(i), rod(width, start=p, end=q, color=color))

# Stone slab floor, with irregular warm grey tones.
floor = Asset("flagstone floor")
add(floor, "subfloor", box((8.5, 8.2, 0.12), center=(0, 0, -0.10), color=mortar))
for ix in range(12):
    for iy in range(10):
        x = -3.85 + ix * .70 + (0.09 if iy % 2 else 0)
        y = -3.65 + iy * .75
        c = random.choice([(0.48,.46,.40),(.53,.51,.45),(.44,.44,.39),(.57,.55,.48)])
        add(floor, "slab_%02d_%02d" % (ix, iy),
            box((.68,.73,.035), center=(x,y,-.025), color=c))
scene.include("floor", floor)

walls = Asset("plaster walls and hearth")
add(walls, "rear plaster", box((8.4,.16,5.0), center=(0,3.65,2.5), color=plaster))
add(walls, "left plaster", box((.16,7.3,5.0), center=(-4.15,0,2.5), color=(.70,.73,.70)))

# Wide rear recess: dark rectangle plus shallow elliptical arched crown.
add(walls, "hearth shadow", box((3.45,.055,1.15), center=(.57,3.52,.58), color=dark))
crown = ball(1, center=(.57,3.50,1.12), color=dark)
crown.resize((1.72,.035,.64))
add(walls, "hearth curved shadow", crown)
arch_band(walls, "hearth voussoir ", .57, 3.43, 1.13, 1.77, .115, stone_light, 13)
add(walls, "hearth left pier", box((.22,.26,1.12), center=(-1.19,3.44,.56), color=stone))
add(walls, "hearth right pier", box((.22,.26,1.12), center=(2.33,3.44,.56), color=stone))
# Iron grate and irons in the fireplace.
for z in (.26,.42,.58,.74,.90):
    add(walls, "grate rail %.2f" % z,
        rod(.022, start=(-.50,3.34,z), end=(1.20,3.34,z), color=iron))
for x in (-.45,-.13,.19,.51,.83,1.15):
    add(walls, "grate upright %.2f" % x,
        rod(.018, start=(x,3.33,.20), end=(x,3.33,1.0), color=iron))
# Left masonry counter, seen against the side of the hearth.
add(walls, "left counter body", box((2.75,1.05,.76), center=(-2.65,2.93,.38), color=(.69,.69,.63)))
add(walls, "left counter top", box((2.78,1.08,.09), center=(-2.65,2.90,.80), color=(.46,.45,.40)))
for x in (-3.32,-2.25):
    add(walls, "counter opening %.2f" % x, box((.70,.04,.39), center=(x,2.38,.20), color=dark))
    ar = ball(1, center=(x,2.35,.39), color=dark)
    ar.resize((.35,.03,.23))
    add(walls, "counter arched opening %.2f" % x, ar)
arch_band(walls, "left arch ", -2.65, 3.46, 1.25, 1.38, .09, stone, 9)
# Small right alcove and shadow.
add(walls, "right alcove shadow", box((1.05,.04,.85), center=(3.20,3.53,.43), color=dark))
arc = ball(1, center=(3.20,3.51,.84), color=dark)
arc.resize((.53,.03,.26))
add(walls, "right alcove crown", arc)
arch_band(walls, "right arch ", 3.20,3.43,.84,.55,.09,stone,7)
scene.include("architecture", walls)

# Central square chimney and distinct stepped cap.
chimney = Asset("central stone chimney")
add(chimney, "wide plinth", box((1.18,1.08,.22), center=(0,.30,.91), color=stone))
add(chimney, "plinth bevel course", box((1.04,.96,.16), center=(0,.30,1.10), color=stone_light))
add(chimney, "square shaft", box((.72,.70,1.70), center=(0,.30,1.98), color=(.62,.59,.53)))
add(chimney, "shaft lower collar", box((.87,.83,.11), center=(0,.30,1.20), color=stone_light))
add(chimney, "shaft upper collar", box((.90,.86,.12), center=(0,.30,2.84), color=stone_light))
add(chimney, "upper molding", box((1.00,.95,.11), center=(0,.30,2.94), color=(.69,.66,.59)))
# Tapered cap built from progressively smaller courses.
for i, (s,z) in enumerate(((.91,3.05),(.76,3.20),(.60,3.35),(.43,3.50),(.25,3.63))):
    add(chimney, "cap course %d" % i,
        box((s,s*.96,.15), center=(0,.30,z), color=(.68,.65,.59)))
add(chimney, "round finial", ball(.115, center=(0,.30,3.79), color=(.72,.70,.64)))
scene.include("chimney", chimney)

# Square wooden table around the masonry column.
table = Asset("central work table")
add(table, "tabletop", box((3.25,2.75,.13), center=(0,.22,.79), color=wood))
for x in (-1.43,1.43):
    for y in (-.92,1.36):
        add(table, "leg %.2f %.2f" % (x,y),
            box((.14,.14,.78), center=(x,y,.39), color=wood_edge))
for y in (-1.02,1.46):
    add(table, "apron %.2f" % y, box((3.0,.09,.28), center=(0,y,.61), color=wood_edge))
for x in (-1.49,1.49):
    add(table, "side apron %.2f" % x, box((.09,2.38,.28), center=(x,.22,.61), color=wood_edge))
# Inner raised boards form an open square around the shaft.
for y in (-.47,1.04):
    add(table, "raised panel y %.2f" % y,
        box((1.95,.08,.47), center=(0,y,1.06), color=(.43,.25,.13)))
for x in (-.97,.97):
    add(table, "raised panel x %.2f" % x,
        box((.08,1.55,.47), center=(x,.28,1.06), color=(.43,.25,.13)))
scene.include("worktable", table)

# Pottery: shallow flattened spheres with contrasting inner surfaces.
def dish(parent, name, x, y, z, radius, outer, inner=None):
    base = ball(1, center=(x,y,z), color=outer)
    base.resize((radius,radius,.055))
    add(parent, name + " body", base)
    if inner is not None:
        top = ball(1, center=(x,y,z+.035), color=inner)
        top.resize((radius*.78,radius*.78,.018))
        add(parent, name + " interior", top)

def pot(parent, name, x, y, z, radius, height, color):
    body = ball(1, center=(x,y,z+height*.42), color=color)
    body.resize((radius,radius,height*.43))
    add(parent, name+" body", body)
    add(parent, name+" rim", rod(radius*.67, length=.045,
                                  center=(x,y,z+height*.82), color=color))
    add(parent, name+" opening", rod(radius*.49, length=.012,
                                      center=(x,y,z+height*.85), color=dark))

wares = Asset("tableware and food")
# Front table edge: bowls and platters.
for i,(x,y,r,c) in enumerate([
    (-1.22,-.79,.18,cream),(-.84,-.90,.19,ochre),(-.40,-.88,.16,cream),
    (.02,-.87,.18,ochre),(.43,-.87,.17,cream),(.85,-.83,.20,ochre),
    (1.24,-.70,.19,grey),(-1.24,-.37,.14,cream),(-1.25,.04,.15,ochre),
    (-1.25,.47,.17,cream),(1.26,-.25,.17,grey),(1.25,.17,.16,cream),
    (1.25,.60,.18,grey)]):
    dish(wares,"table dish %02d"%i,x,y,.90,r,c, (c[0]*.75,c[1]*.75,c[2]*.75))
# Plate and bread group on left and near edge.
for i,(x,y) in enumerate([(-1.25,.85),(-.85,1.29),(-.40,1.30),(.10,1.31),(.58,1.30),(1.02,1.25)]):
    dish(wares,"rear plate %d"%i,x,y,.90,.16,cream,(.49,.43,.32))
for i,(x,y) in enumerate([(-1.21,-.60),(-1.20,-.49),(-1.05,-.60),(-.68,-.82),(-.58,-.82)]):
    b=ball(.09,center=(x,y,.97),color=(.59,.40,.20))
    b.resize((1.25,.72,.45))
    add(wares,"bread %d"%i,b)
# Small bottles and cups along the enclosure's top ledges.
for i,(x,y) in enumerate([(-.78,-.47),(-.40,-.47),(.12,-.47),(.55,-.47),
                           (.97,-.18),(.97,.20),(.97,.65),(-.97,.20),(-.97,.70)]):
    pot(wares,"shelf vessel %d"%i,x,y,1.30,.07,.20,
        random.choice([ochre,grey,(.52,.48,.37),(.22,.23,.18)]))
# White pitcher and large dishes in the back left area.
pot(wares,"white jug",-.90,1.18,.90,.11,.28,cream)
dish(wares,"large pale platter",-.66,.99,.91,.24,(.75,.75,.69),(.88,.87,.79))
scene.include("tableware", wares)

counterware = Asset("hearth and counter pottery")
for i,(x,y,r,h,c) in enumerate([
    (-3.72,2.83,.14,.16,ochre),(-3.40,2.82,.13,.18,grey),
    (-3.05,2.88,.12,.17,cream),(-2.70,2.88,.12,.19,ochre),
    (-2.35,2.85,.14,.17,cream),(-2.02,2.84,.12,.17,grey),
    (-1.73,2.85,.13,.19,ochre),(1.55,3.12,.18,.22,grey),
    (1.93,3.08,.19,.27,iron),(2.67,3.05,.21,.22,ochre),
    (3.05,3.03,.23,.22,wood_edge),(3.51,3.00,.24,.30,iron)]):
    z = .85 if x < -1.5 else .03
    pot(counterware,"hearth pot %d"%i,x,y,z,r,h,c)
scene.include("counter vessels", counterware)

realize(scene)
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
background.inputs["Color"].default_value = (0.70,0.73,0.72,1)
background.inputs["Strength"].default_value = .7

set_view((7.4,-10.6,10.5), (0,.55,1.05), lens=43)
area_emitter((0,-3,8), power=1050, size=7, target=(0,.5,0))
area_emitter((-4,0,5), power=450, size=5, target=(0,1,1))
