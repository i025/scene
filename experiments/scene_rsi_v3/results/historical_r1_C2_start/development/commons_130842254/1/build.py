# Reference inventory, approximate normalized image bounds:
# Plaster walls fill the top; the floor fills the lower half. A worn rectangular
# flagstone area surrounds the table, with darker, finer paving beyond it.
# Rear hearth: (0.40, 0.22)-(0.85, 0.47), broad dark low arch, stone rim,
# iron grate and cookware; its dark interior is partly occluded.
# Left cooking counter: (0.00, 0.27)-(0.37, 0.51), pale masonry with two
# dark arched openings, pottery and a stone arch behind it.
# Right alcove: (0.87, 0.33)-(1.00, 0.59), dark recess, baskets and pots.
# Central chimney: (0.43, 0.22)-(0.59, 0.63), stone shaft, projecting base,
# tapered pyramidal cap, horizontal seams and spherical finial.
# Wooden table: (0.18, 0.46)-(0.73, 0.88), legs, raised inner boards,
# crowded dishes, food, jugs and small vessels around the chimney.
# A dark hanging iron fixture is visible above the left end of the hearth.
# Contents behind the chimney and inside the hearth remain uncertain.
#
# Render comparison: the table and chimney are close in width, but the hearth
# appears too low and the table too high; a steeper view spreads their vertical
# separation. The floor is too uniformly pale and tiled, the cap too stair-like,
# and the tableware too evenly spaced. The revision addresses these local issues.
# Estimated expanded meshes: floor 100, architecture 65, chimney 13, table 13,
# dishes and food 100, hearth vessels 45, hanging fixture 12: about 348 meshes.

from sceneact import *
import bpy
import math
import random

random.seed(21)
scene = Scene("Historic kitchen")

plaster = (.68, .71, .68)
stone = (.39, .37, .32)
stone_light = (.55, .52, .46)
dark = (.052, .048, .039)
iron = (.085, .080, .068)
wood = (.33, .18, .085)
wood_edge = (.25, .13, .060)
cream = (.68, .66, .57)
ochre = (.49, .28, .105)
grey = (.30, .32, .29)

def add(parent, name, obj):
    parent.include(name, obj)

def arch_band(parent, prefix, cx, y, spring, radius, thickness,
              color, segments=13, height_factor=.48):
    for i in range(segments):
        a = math.pi * i / segments
        b = math.pi * (i + 1) / segments
        p = (cx + radius * math.cos(a), y,
             spring + radius * height_factor * math.sin(a))
        q = (cx + radius * math.cos(b), y,
             spring + radius * height_factor * math.sin(b))
        add(parent, prefix + str(i),
            rod(thickness, start=p, end=q, color=color))

# Dark, worn outer paving with a smaller central area of large stone flags.
floor = Asset("worn stone flooring")
add(floor, "dark outer paving",
    box((16, 16, .12), center=(0, 0, -.10), color=(.27, .27, .23)))
floor_colors = [
    (.39, .39, .34), (.44, .43, .37), (.47, .45, .39),
    (.40, .41, .36), (.49, .47, .40), (.43, .43, .38)
]
for ix in range(9):
    for iy in range(9):
        x = -3.12 + ix * .72 + (.08 if iy % 2 else 0)
        y = -3.40 + iy * .72
        add(floor, "flagstone %02d %02d" % (ix, iy),
            box((.704, .704, .025), center=(x, y, -.026),
                color=random.choice(floor_colors)))
scene.include("floor", floor)

walls = Asset("plaster walls and hearth")
add(walls, "rear plaster wall",
    box((16, .16, 10), center=(0, 3.65, 5), color=plaster))
add(walls, "left plaster wall",
    box((.16, 15, 10), center=(-4.15, 0, 5),
        color=(.66, .69, .66)))

# Dark silhouettes sit in front of the wall; interior depth is uncertain.
add(walls, "main hearth shadow",
    box((3.45, .055, 1.15), center=(.57, 3.52, .58), color=dark))
crown = ball(1, center=(.57, 3.50, 1.12), color=dark)
crown.resize((1.72, .035, .64))
add(walls, "main hearth arched shadow", crown)
arch_band(walls, "main hearth stone ", .57, 3.43, 1.13,
          1.77, .115, stone_light)
add(walls, "main hearth left pier",
    box((.22, .26, 1.12), center=(-1.19, 3.44, .56), color=stone))
add(walls, "main hearth right pier",
    box((.22, .26, 1.12), center=(2.33, 3.44, .56), color=stone))
for z in (.26, .42, .58, .74, .90):
    add(walls, "grate horizontal %.2f" % z,
        rod(.022, start=(-.50, 3.34, z), end=(1.20, 3.34, z), color=iron))
for x in (-.45, -.13, .19, .51, .83, 1.15):
    add(walls, "grate vertical %.2f" % x,
        rod(.018, start=(x, 3.33, .20), end=(x, 3.33, 1.0), color=iron))

add(walls, "left cooking counter body",
    box((2.75, 1.05, .76), center=(-2.65, 2.93, .38),
        color=(.60, .61, .56)))
add(walls, "left cooking counter top",
    box((2.78, 1.08, .09), center=(-2.65, 2.90, .80),
        color=(.38, .37, .32)))
for x in (-3.32, -2.25):
    add(walls, "counter dark opening %.2f" % x,
        box((.70, .04, .39), center=(x, 2.38, .20), color=dark))
    arch = ball(1, center=(x, 2.35, .39), color=dark)
    arch.resize((.35, .03, .23))
    add(walls, "counter opening crown %.2f" % x, arch)
arch_band(walls, "left counter arch ", -2.65, 3.46, 1.25,
          1.38, .09, stone, segments=9)

add(walls, "right alcove shadow",
    box((1.05, .04, .85), center=(3.20, 3.53, .43), color=dark))
right_crown = ball(1, center=(3.20, 3.51, .84), color=dark)
right_crown.resize((.53, .03, .26))
add(walls, "right alcove crown", right_crown)
arch_band(walls, "right alcove stone ", 3.20, 3.43, .84,
          .55, .09, stone, segments=7)
scene.include("architecture", walls)

fixture = Asset("hanging iron fixture")
for i, x in enumerate((-1.65, -1.40, -1.15)):
    add(fixture, "vertical bar %d" % i,
        rod(.025, start=(x, 3.20, 1.50), end=(x, 3.20, 2.38),
            color=iron))
for z in (1.95, 2.27):
    add(fixture, "crossbar %.2f" % z,
        rod(.026, start=(-1.78, 3.20, z), end=(-1.02, 3.20, z),
            color=iron))
for i, x in enumerate((-1.63, -1.37, -1.11)):
    add(fixture, "hanging utensil %d" % i,
        rod(.018, start=(x, 3.17, 1.94), end=(x, 3.17, 1.65),
            color=iron))
scene.include("hanging ironwork", fixture)

chimney = Asset("central stone chimney")
add(chimney, "wide plinth",
    box((1.18, 1.08, .22), center=(0, .30, .91), color=stone))
add(chimney, "plinth upper course",
    box((1.04, .96, .16), center=(0, .30, 1.10), color=stone_light))
add(chimney, "square shaft",
    box((.72, .70, 1.70), center=(0, .30, 1.98),
        color=(.57, .54, .48)))
add(chimney, "shaft lower collar",
    box((.87, .83, .11), center=(0, .30, 1.20), color=stone_light))
add(chimney, "shaft upper collar",
    box((.90, .86, .12), center=(0, .30, 2.84), color=stone_light))
add(chimney, "upper projecting molding",
    box((1.00, .95, .11), center=(0, .30, 2.94),
        color=(.63, .60, .53)))
# Short tapered courses reduce the strong staircase of the previous render.
for i, (s, z) in enumerate([
    (.90, 3.035), (.82, 3.12), (.74, 3.205), (.66, 3.29),
    (.58, 3.375), (.50, 3.46), (.42, 3.545), (.34, 3.63)
]):
    add(chimney, "cap stone course %d" % i,
        box((s, s * .96, .085), center=(0, .30, z),
            color=(.64, .61, .55)))
add(chimney, "cap finial",
    ball(.115, center=(0, .30, 3.76), color=(.69, .67, .61)))
scene.include("chimney", chimney)

table = Asset("wooden worktable")
add(table, "top",
    box((3.25, 2.75, .13), center=(0, .22, .79), color=wood))
for x in (-1.43, 1.43):
    for y in (-.92, 1.36):
        add(table, "leg %.2f %.2f" % (x, y),
            box((.14, .14, .78), center=(x, y, .39), color=wood_edge))
for y in (-1.02, 1.46):
    add(table, "long apron %.2f" % y,
        box((3.0, .09, .28), center=(0, y, .61), color=wood_edge))
for x in (-1.49, 1.49):
    add(table, "side apron %.2f" % x,
        box((.09, 2.38, .28), center=(x, .22, .61), color=wood_edge))
for y in (-.47, 1.04):
    add(table, "raised board across %.2f" % y,
        box((1.95, .08, .47), center=(0, y, 1.06),
            color=(.39, .21, .095)))
for x in (-.97, .97):
    add(table, "raised board side %.2f" % x,
        box((.08, 1.55, .47), center=(x, .28, 1.06),
            color=(.39, .21, .095)))
scene.include("worktable", table)

def dish(parent, name, x, y, z, radius, outer, inner):
    body = ball(1, center=(x, y, z), color=outer)
    body.resize((radius, radius, .055))
    add(parent, name + " body", body)
    inside = ball(1, center=(x, y, z + .035), color=inner)
    inside.resize((radius * .78, radius * .78, .018))
    add(parent, name + " interior", inside)

def pot(parent, name, x, y, z, radius, height, color):
    body = ball(1, center=(x, y, z + height * .42), color=color)
    body.resize((radius, radius, height * .43))
    add(parent, name + " body", body)
    add(parent, name + " rim",
        rod(radius * .67, length=.045,
            center=(x, y, z + height * .82), color=color))
    add(parent, name + " opening",
        rod(radius * .49, length=.012,
            center=(x, y, z + height * .85), color=dark))

wares = Asset("table dishes and food")
table_dishes = [
    (-1.22, -.79, .18, cream), (-.84, -.90, .19, ochre),
    (-.40, -.88, .16, cream), (.02, -.87, .18, ochre),
    (.43, -.87, .17, cream), (.85, -.83, .20, ochre),
    (1.24, -.70, .19, grey), (-1.24, -.37, .14, cream),
    (-1.25, .04, .15, ochre), (-1.25, .47, .17, cream),
    (1.26, -.25, .17, grey), (1.25, .17, .16, cream),
    (1.25, .60, .18, grey)
]
for i, (x, y, r, c) in enumerate(table_dishes):
    x += random.uniform(-.06, .06)
    y += random.uniform(-.07, .07)
    dish(wares, "table dish %02d" % i, x, y, .90, r, c,
         (c[0] * .73, c[1] * .73, c[2] * .73))
for i, (x, y) in enumerate([
    (-1.25, .85), (-.85, 1.29), (-.40, 1.30),
    (.10, 1.31), (.58, 1.30), (1.02, 1.25)
]):
    dish(wares, "back plate %d" % i, x, y, .90, .16, cream,
         (.48, .42, .31))
for i, (x, y) in enumerate([
    (-1.21, -.60), (-1.20, -.49), (-1.05, -.60),
    (-.68, -.82), (-.58, -.82), (-1.20, .36), (-1.12, .43)
]):
    bread = ball(.09, center=(x, y, .97), color=(.58, .38, .18))
    bread.resize((1.25, .72, .45))
    add(wares, "bread %d" % i, bread)
for i, (x, y) in enumerate([
    (-.78, -.47), (-.40, -.47), (.12, -.47), (.55, -.47),
    (.97, -.18), (.97, .20), (.97, .65), (-.97, .20), (-.97, .70)
]):
    pot(wares, "ledge vessel %d" % i, x, y, 1.30, .07, .20,
        random.choice([ochre, grey, (.50, .46, .35), (.20, .21, .17)]))
pot(wares, "white jug", -.90, 1.18, .90, .11, .28, cream)
dish(wares, "large pale platter", -.66, .99, .91, .24,
     (.72, .72, .67), (.84, .84, .76))
for i in range(5):
    item = ball(1, center=(.70 + i * .10, -.76 + i * .07, .965),
                color=(.53, .48, .40))
    item.resize((.23, .045, .035))
    item.turn('+z', -20)
    add(wares, "long food item %d" % i, item)
# Hanging pale cloth on the near wooden panel.
add(wares, "folded hanging cloth",
    box((.25, .025, .36), center=(-.18, -.525, .93),
        color=(.72, .71, .66)))
scene.include("tableware", wares)

counterware = Asset("counter and hearth pottery")
vessels = [
    (-3.72, 2.83, .14, .16, ochre), (-3.40, 2.82, .13, .18, grey),
    (-3.05, 2.88, .12, .17, cream), (-2.70, 2.88, .12, .19, ochre),
    (-2.35, 2.85, .14, .17, cream), (-2.02, 2.84, .12, .17, grey),
    (-1.73, 2.85, .13, .19, ochre), (1.55, 3.12, .18, .22, grey),
    (1.93, 3.08, .19, .27, iron), (2.67, 3.05, .21, .22, ochre),
    (3.05, 3.03, .23, .22, wood_edge), (3.51, 3.00, .24, .30, iron),
    (2.65, 2.57, .25, .17, (.29, .20, .12)),
    (3.05, 2.51, .22, .25, (.20, .18, .14))
]
for i, (x, y, r, h, c) in enumerate(vessels):
    z = .85 if x < -1.5 else .03
    pot(counterware, "hearth vessel %d" % i, x, y, z, r, h, c)
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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .73, .72, 1)
background.inputs["Strength"].default_value = .48

set_view((7.4, -10.6, 12.8), (0, .55, 1.30), lens=70)
area_emitter((0, -3, 8), power=850, size=7, target=(0, .5, 0))
area_emitter((-4, 0, 5), power=300, size=5, target=(0, 1, 1))
