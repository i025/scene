from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and approximate normalized image anchors:
# - Pale walls occupy the upper half; their corner is near (0.46, 0.03).
# - Rear hearth: dark arched opening roughly (0.42, 0.23)-(0.85, 0.46),
#   framed with muted stone. The white cooking range at left spans
#   approximately (0.00, 0.27)-(0.39, 0.51).
# - Central stone chimney rises from approximately (0.43, 0.22) to
#   (0.60, 0.57), overlapping the hearth and the table.
# - Large wooden worktable occupies approximately (0.18, 0.45)-(0.71, 0.87).
#   Its edges slope down-right and down-left; utensils and food cover its top.
# - Stone floor fills the foreground, with dark brick flooring at the right.
# - Pots, baskets and fuel cluster beside the hearth at the right edge.
# The dark interior of the hearth and small individual utensils are uncertain.
# Approximate primitive budget: floor and architecture 100, table and chimney 35,
# cookware and food 90, hearth accessories 25; approximately 250 meshes.

random.seed(23)
scene = Scene("Historic kitchen")

# Camera and principal dimensions are kept separate for later adjustment.
CAM_POS = (7.5, -11.5, 12.0)
CAM_TARGET = (0.0, 0.35, 1.05)
CAM_LENS = 39
ROOM_W, ROOM_D = 8.6, 7.6
TABLE_W, TABLE_D = 3.7, 2.75
TABLE_CENTER = (0.0, -0.55)

plaster = (0.72, 0.73, 0.70)
stone = (0.43, 0.40, 0.34)
mortar = (0.31, 0.30, 0.27)
dark = (0.075, 0.070, 0.059)
wood = (0.35, 0.19, 0.095)
wood_light = (0.46, 0.28, 0.14)
iron = (0.16, 0.16, 0.14)
cream = (0.70, 0.68, 0.59)
ochre = (0.55, 0.35, 0.15)

def add(asset, name, node):
    asset.include(name, node)
    return node

def cylinder(asset, name, x, y, z, radius, height, color):
    return add(asset, name, rod(radius, start=(x,y,z),
                                end=(x,y,z+height), color=color))

# Floor: large pale slabs beneath the work area and darker brick around it.
floor = Asset("floor_and_paving")
add(floor, "base", box((ROOM_W, ROOM_D, .12), center=(0,0,-.12),
                        color=(.27,.27,.23)))
for i in range(11):
    for j in range(9):
        x = -3.45 + i*.67
        y = -3.1 + j*.67
        if x > 2.3:
            continue
        shade = random.uniform(-.035,.035)
        add(floor, "slab_%02d_%02d"%(i,j),
            box((.65,.65,.025), center=(x,y,-.045),
                color=(.43+shade,.42+shade,.36+shade)))
# Sparse dark brick courses along the right side.
for j in range(16):
    for i in range(4):
        x = 2.55+i*.43+(j%2)*.21
        y = -3.25+j*.41
        add(floor, "brick_%02d_%02d"%(i,j),
            box((.41,.39,.018), center=(x,y,-.035),
                color=(.27,.27,.23)))
scene.include("floor", floor)

architecture = Asset("walls_and_hearth")
# Rear wall: pale plaster above a deep black fireplace.
add(architecture, "upper_rear_wall",
    box((8.6,.20,3.0), center=(0,3.65,4.45), color=plaster))
add(architecture, "left_rear_pier",
    box((2.75,.20,3.0), center=(-2.92,3.65,1.45), color=plaster))
add(architecture, "right_rear_pier",
    box((1.85,.20,3.0), center=(3.38,3.65,1.45), color=plaster))
add(architecture, "fireplace_dark_back",
    box((4.05,.13,2.65), center=(.50,3.72,1.31), color=dark))
# Lower dark firebrick blocks and iron grate inside the opening.
for x in (-1.22, -0.70, -.18, .34, .86, 1.38, 1.90):
    for z in (.22,.63,1.04):
        add(architecture, "firebrick_%.2f_%.2f"%(x,z),
            box((.49,.035,.37), center=(x,3.62,z),
                color=(.14,.13,.11)))
for z in (.32,.55,.78,1.01,1.24):
    add(architecture, "grate_bar_%.2f"%z,
        rod(.025, start=(-.35,3.43,z), end=(1.55,3.43,z), color=iron))
for x in (-.3,.25,.8,1.5):
    add(architecture, "grate_upright_%.2f"%x,
        rod(.025, start=(x,3.42,.24), end=(x,3.42,1.35), color=iron))
# Shallow segmented stone arch; each segment remains independently editable.
arch_points = []
for i in range(13):
    t = math.pi - i*math.pi/12
    arch_points.append((.50 + 2.10*math.cos(t), 3.44,
                        1.33 + 1.05*math.sin(t)))
for i in range(12):
    add(architecture, "arch_stone_%02d"%i,
        rod(.105, start=arch_points[i], end=arch_points[i+1], color=stone))
for x in (-1.6,2.6):
    add(architecture, "arch_jamb_%.1f"%x,
        box((.22,.29,1.35), center=(x,3.49,.68), color=stone))
# Left side wall, kept low enough to expose the scene from the elevated view.
add(architecture, "left_wall",
    box((.18,4.0,3.2), center=(-4.2,1.65,1.55), color=plaster))
scene.include("architecture", architecture)

# White masonry range with three dark arched-looking openings and pots.
range_asset = Asset("left_masonry_cooking_range")
add(range_asset, "masonry_body",
    box((2.85,.92,.79), center=(-2.55,2.55,.40), color=(.66,.67,.62)))
add(range_asset, "dark_countertop",
    box((2.95,1.00,.09), center=(-2.55,2.55,.84), color=(.30,.30,.27)))
for k,x in enumerate((-3.48,-2.55,-1.65)):
    add(range_asset, "oven_opening_%d"%k,
        box((.59,.025,.47), center=(x,2.075,.25), color=dark))
    add(range_asset, "opening_round_top_%d"%k,
        ball(.30, center=(x,2.06,.47), color=dark))
    for j in range(3):
        px = x + (j-1)*.22
        cylinder(range_asset, "range_pot_%d_%d"%(k,j), px,2.54,.89,
                 .10+(j%2)*.025, .12, (0.38,.34,.28))
        cylinder(range_asset, "range_lip_%d_%d"%(k,j), px,2.54,1.01,
                 .12+(j%2)*.025, .018, cream)
scene.include("cooking_range", range_asset)

# Main table and its four legs, broad planked top, and raised wooden partitions.
table = Asset("worktable")
tx, ty = TABLE_CENTER
add(table, "table_top",
    box((TABLE_W,TABLE_D,.14), center=(tx,ty,.92), color=wood_light))
for x in (-1.63,1.63):
    for y in (-1.70,.60):
        add(table, "leg_%.1f_%.1f"%(x,y),
            box((.15,.15,.91), center=(x,y,.46), color=wood))
for y in (-1.72,.62):
    add(table, "long_apron_%.1f"%y,
        box((3.5,.09,.25), center=(0,y,.78), color=wood))
for x in (-1.68,1.68):
    add(table, "short_apron_%.1f"%x,
        box((.09,2.32,.25), center=(x,-.55,.78), color=wood))
# Raised boards enclose the central cooking area; front remains open.
add(table, "rear_partition",
    box((2.45,.10,.52), center=(0,.27,1.25), color=wood))
add(table, "right_partition",
    box((.10,1.35,.52), center=(1.18,-.38,1.25), color=wood))
add(table, "left_partition",
    box((.10,1.20,.43), center=(-1.18,-.32,1.21), color=wood))
scene.include("worktable", table)

# Central pale stone chimney, stepped base and tapered upper hood.
chimney = Asset("central_stone_chimney")
add(chimney, "wide_base", box((1.25,1.16,.20), center=(0,.06,1.10),
                                color=(.48,.47,.41)))
add(chimney, "base_step", box((1.08,.99,.16), center=(0,.06,1.27),
                                color=(.56,.55,.49)))
add(chimney, "shaft", box((.78,.72,1.56), center=(0,.06,2.10),
                            color=(.62,.61,.55)))
for z,s in ((1.44,.90),(2.84,.90),(2.94,.99)):
    add(chimney, "moulding_%.2f"%z,
        box((s,s*.90,.09), center=(0,.06,z), color=(.67,.66,.59)))
# Four diminishing courses give the hood a stepped, sloping silhouette.
for k,(w,h) in enumerate(((1.05,.20),(.86,.25),(.65,.25),(.44,.24))):
    z = 3.08 + sum((.20,.25,.25,.24)[:k]) + h/2
    add(chimney, "hood_course_%d"%k,
        box((w,w*.88,h), center=(0,.06,z), color=(.70,.69,.63)))
add(chimney, "finial", ball(.105, center=(0,.06,4.12),
                              color=(.72,.70,.64)))
scene.include("stone_chimney", chimney)

# Dishes, platters and provisions. Cylinders and thin contrasting tops suggest
# rims and hollow interiors while keeping the individual vessels editable.
dishes = Asset("tableware_and_food")
def bowl(name,x,y,r,z=.995):
    cylinder(dishes, name+"_body", x,y,z,r,.10, ochre)
    cylinder(dishes, name+"_rim", x,y,z+.095,r*1.04,.025, cream)
    cylinder(dishes, name+"_inside", x,y,z+.122,r*.78,.012,
             (0.31,.24,.16))
def plate(name,x,y,r,z=.995):
    cylinder(dishes,name+"_plate",x,y,z,r,.035,cream)
    cylinder(dishes,name+"_center",x,y,z+.037,r*.72,.012,
             (0.53,.52,.46))
for i,(x,y,r) in enumerate([
    (-1.45,-1.48,.17),(-.97,-1.53,.20),(-.48,-1.49,.17),
    (.06,-1.51,.20),(.57,-1.52,.18),(1.07,-1.49,.21),
    (-1.47,-.98,.14),(-1.43,-.57,.15),(-1.44,-.12,.17),
    (1.44,-1.03,.16),(1.43,-.57,.18)]):
    bowl("earthenware_%02d"%i,x,y,r)
for i,(x,y,r) in enumerate([(-1.40,.36,.18),(-.96,.43,.15),
                             (-.70,-1.05,.20),(.78,-1.13,.19),
                             (1.38,.30,.18)]):
    plate("plate_%02d"%i,x,y,r)
for i,(x,y) in enumerate([(-1.51,-1.25),(-1.20,-1.25),(-.91,-1.25),
                           (-.56,-1.22),(.20,-1.27),(.48,-1.27)]):
    add(dishes,"bread_%02d"%i,
        ball(.13,center=(x,y,1.07),color=(.64,.43,.23)))
# Several small vessels and bottles along the inner raised edge.
for i,(x,y) in enumerate([(-.98,.42),(-.55,.42),(.55,.42),(.95,.40),
                           (1.02,-.05),(1.02,-.45),(1.02,-.80)]):
    cylinder(dishes,"cup_%02d"%i,x,y,1.00,.075,.18,
             (0.35,.32,.24) if i%2 else cream)
    cylinder(dishes,"cup_lip_%02d"%i,x,y,1.18,.08,.02,cream)
# Two broad cloth-like pale patches and long utensils on the near tabletop.
add(dishes,"folded_cloth",
    box((.50,.37,.025),center=(.88,-1.18,1.01),color=(.62,.59,.51)))
for i in range(4):
    x=.62+i*.17
    add(dishes,"cutlery_%d"%i,
        rod(.018,start=(x,-1.42,1.04),end=(x+.12,-1.05,1.04),color=iron))
scene.include("tableware", dishes)

# Baskets and vessels beside the rear hearth.
hearth_items = Asset("hearth_pots_and_baskets")
for i,(x,y,r,h) in enumerate([(2.90,2.83,.31,.30),(3.50,2.75,.26,.30),
                               (3.72,2.15,.29,.38),(2.91,2.22,.24,.20),
                               (2.55,3.05,.21,.24)]):
    cylinder(hearth_items,"vessel_%d"%i,x,y,.02,r,h,
             (0.24,.20,.15) if i%2 else (0.36,.27,.17))
    cylinder(hearth_items,"vessel_rim_%d"%i,x,y,h+.02,r*1.05,.035,
             (0.30,.25,.18))
    cylinder(hearth_items,"vessel_opening_%d"%i,x,y,h+.056,r*.78,.012,dark)
# Hanging cookware on the back wall.
for i,(x,z,r) in enumerate([(1.7,1.45,.18),(2.0,1.15,.15),(1.65,.91,.13)]):
    add(hearth_items,"hanging_pan_%d"%i,
        rod(r,start=(x,3.39,z),end=(x,3.32,z),color=(.39,.39,.34)))
    add(hearth_items,"pan_handle_%d"%i,
        rod(.022,start=(x,3.35,z+r),end=(x,3.35,z+r+.24),color=iron))
scene.include("hearth_accessories", hearth_items)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 471
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
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
background.inputs["Strength"].default_value = .65

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
area_emitter((0,-3,8), power=1500, size=7, target=(0,0,0))
area_emitter((-4,1,6), power=700, size=5, target=(0,1,1))

# Projection check: reference estimates are independent of computed projections.
landmarks = [
    ("chimney finial", (0,.06,4.225), (.51,.22)),
    ("table front corner", (1.85,-1.925,.99), (.48,.86)),
    ("hearth left spring", (-1.60,3.44,1.33), (.43,.36)),
    ("hearth right spring", (2.60,3.44,1.33), (.84,.36)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark                  reference       projected")
for name,p,ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print("%-24s %s %s" % (name, ref, uv))
