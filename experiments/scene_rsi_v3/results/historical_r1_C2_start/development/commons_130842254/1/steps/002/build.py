# Reference inventory, estimated normalized image bounds:
# Pale plaster walls fill the upper background; worn stone flooring fills the
# lower half. The visible boundaries of the room are outside the frame.
# A broad dark arched hearth occupies roughly (0.40, 0.22)-(0.85, 0.47),
# with a stone arch, iron grate and partly obscured cookware.
# A masonry cooking counter and its two dark openings occupy
# (0.00, 0.27)-(0.37, 0.51), with pottery across the top.
# A smaller dark recess, pots and baskets are at (0.86, 0.33)-(1.00, 0.58).
# The central stone chimney occupies (0.43, 0.22)-(0.59, 0.63), with
# a square shaft, projecting base, tapered cap and spherical finial.
# The wooden table occupies (0.18, 0.46)-(0.73, 0.88); it surrounds the
# chimney and carries raised wooden boards, dishes, food and small vessels.
# The exact contents of the dark hearth and occluded table areas are uncertain.
#
# Comparison with the first render: the scene was framed too widely, showing
# the edges of a miniature room. The table, chimney, hearth and counter were
# consequently much too small. The camera is tightened, walls and floor extend
# beyond the frame, and the floor and tableware are made less uniformly pale.
# Estimated expanded primitives: floor 145, architecture 55, chimney 14,
# table 12, tableware and food 120, hearth objects 45: about 391 meshes.

from sceneact import *
import bpy
import math
import random

random.seed(21)
scene = Scene("Historic kitchen")

plaster = (0.71, 0.74, 0.71)
stone = (0.42, 0.40, 0.35)
stone_light = (0.58, 0.56, 0.50)
dark = (0.055, 0.050, 0.041)
iron = (0.10, 0.095, 0.080)
wood = (0.36, 0.205, 0.105)
wood_edge = (0.26, 0.14, 0.070)
cream = (0.70, 0.68, 0.59)
ochre = (0.52, 0.30, 0.12)
grey = (0.32, 0.34, 0.31)

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

floor = Asset("worn flagstone floor")
add(floor, "dark mortar foundation",
    box((15, 15, .12), center=(0, 0, -.10), color=(.28, .28, .24)))
floor_colors = [
    (.40, .40, .35), (.46, .45, .39), (.50, .48, .41),
    (.42, .43, .38), (.53, .51, .44), (.46, .46, .40)
]
for ix in range(12):
    for iy in range(12):
        x = -4.05 + ix * .74 + (.11 if iy % 2 else 0)
        y = -4.10 + iy * .74
        add(floor, "flagstone %02d %02d" % (ix, iy),
            box((.72, .72, .035), center=(x, y, -.025),
                color=random.choice(floor_colors)))
scene.include("floor", floor)

walls = Asset("plaster walls and hearth")
add(walls, "rear plaster wall",
    box((16, .16, 10), center=(0, 3.65, 5), color=plaster))
add(walls, "left plaster wall",
    box((.16, 15, 10), center=(-4.15, 0, 5), color=(.68, .71, .68)))

# The dark surfaces are placed in front of the plaster, representing the
# visible depth of the hearth without adding uncertain hidden architecture.
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
        color=(.62, .63, .58)))
add(walls, "left cooking counter top",
    box((2.78, 1.08, .09), center=(-2.65, 2.90, .80),
        color=(.40, .39, .34)))
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

chimney = Asset("central stone chimney")
add(chimney, "wide plinth",
    box((1.18, 1.08, .22), center=(0, .30, .91), color=stone))
add(chimney, "plinth upper course",
    box((1.04, .96, .16), center=(0, .30, 1.10), color=stone_light))
add(chimney, "square shaft",
    box((.72, .70, 1.70), center=(0, .30, 1.98),
        color=(.60, .57, .51)))
add(chimney, "shaft lower collar",
    box((.87, .83, .11), center=(0, .30, 1.20), color=stone_light))
add(chimney, "shaft upper collar",
    box((.90, .86, .12), center=(0, .30, 2.84), color=stone_light))
add(chimney, "upper projecting molding",
    box((1.00, .95, .11), center=(0, .30, 2.94),
        color=(.67, .64, .57)))
for i, (s, z) in enumerate([
    (.91, 3.05), (.76, 3.20), (.60, 3.35), (.43, 3.50), (.25, 3.63)
]):
    add(chimney, "cap stone course %d" % i,
        box((s, s * .96, .15), center=(0, .30, z),
            color=(.67, .64, .58)))
add(chimney, "cap finial",
    ball(.115, center=(0, .30, 3.79), color=(.71, .69, .63)))
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
            color=(.41, .23, .11)))
for x in (-.97, .97):
    add(table, "raised board side %.2f" % x,
        box((.08, 1.55, .47), center=(x, .28, 1.06),
            color=(.41, .23, .11)))
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
# A few long pale food pieces and dark utensils on the near right tabletop.
for i in range(4):
    item = ball(1, center=(.70 + i * .10, -.76 + i * .07, .965),
                color=(.55, .50, .42))
    item.resize((.23, .045, .035))
    item.turn('+z', -20)
    add(wares, "long food item %d" % i, item)
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
background.inputs["Strength"].default_value = .55

# Tighten the view around the table and hearth; the larger walls extend
# beyond the image rather than revealing the room's outer edges.
set_view((7.4, -10.6, 10.5), (0, .55, 1.48), lens=66)
area_emitter((0, -3, 8), power=950, size=7, target=(0, .5, 0))
area_emitter((-4, 0, 5), power=350, size=5, target=(0, 1, 1))
