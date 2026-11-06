# Reference inventory, normalized image bounds (approximate):
# Architecture: bright paneled ceiling (0,0)-(1,.32), dark tiled floor
# (0,.57)-(1,1), rear windows (.04,.31)-(.66,.57), right windows
# (.65,.23)-(1,.56). Window mullions and ceiling seams are visible.
# Booths: dark upholstered backs and pale tabletops along left edge
# (0,.52)-(.45,1), partially cropped and overlapping.
# Dining area: small square tables and pedestal chairs across center and right
# (.35,.50)-(.91,1); distant furniture is partly occluded.
# Pendant lamps: large dark shade at upper left and several smaller hanging
# shades receding across the ceiling (.02,.07)-(1,.46).
# Plant: dense, narrow leaves and stems at right (.77,.39)-(1,1); the pot
# and some stems are obscured by chairs.
# Exterior beyond the windows is bright and indistinct.
#
# Approximate primitive expansion: architecture 35, booths 24, tables 25,
# chairs 75, pendant lights 32, plant 45: about 236 meshes total.

from sceneact import *
import bpy
import math
import random

random.seed(7)
scene = Scene("Restaurant")

white = (0.79, 0.79, 0.77)
ceiling = (0.78, 0.78, 0.76)
floorcol = (0.19, 0.19, 0.18)
trim = (0.25, 0.25, 0.24)
glass = (0.86, 0.87, 0.85)
upholstery = (0.23, 0.23, 0.22)
tablecol = (0.67, 0.67, 0.65)
metal = (0.48, 0.48, 0.46)
lampcol = (0.075, 0.075, 0.073)
leafcol = (0.13, 0.16, 0.13)

architecture = Asset("architecture")
architecture.include("floor", box((11, 16, .12), center=(0, 1, -.06), color=floorcol))
architecture.include("ceiling", box((11, 16, .10), center=(0, 1, 3.75), color=ceiling))
architecture.include("rear_lower_wall", box((11, .12, .70), center=(0, 7, .35), color=white))
architecture.include("rear_header", box((11, .12, .25), center=(0, 7, 3.61), color=white))
architecture.include("rear_glazing", box((11, .035, 2.65), center=(0, 7.05, 2.0), color=glass))
architecture.include("right_lower_wall", box((.12, 15, .65), center=(5.5, .3, .325), color=white))
architecture.include("right_glazing", box((.035, 15, 2.75), center=(5.55, .3, 2.04), color=glass))
architecture.include("right_header", box((.12, 15, .22), center=(5.5, .3, 3.64), color=white))
for i, x in enumerate((-5.4, -3.2, -1.1, 1.1, 3.25, 5.4)):
    architecture.include("rear_mullion_%d" % i, box((.065, .10, 2.8), center=(x, 6.96, 2.02), color=trim))
architecture.include("rear_sill", box((11, .14, .07), center=(0, 6.96, .72), color=trim))
for i, y in enumerate((-5, -2.2, .6, 3.4, 6.2)):
    architecture.include("right_mullion_%d" % i, box((.10, .075, 2.9), center=(5.46, y, 2.03), color=trim))
architecture.include("right_sill", box((.12, 15, .07), center=(5.45, .3, .70), color=trim))
# Long ceiling panel joints.
for i in range(20):
    x = -5.25 + i * .55
    architecture.include("ceiling_joint_%d" % i, box((.012, 15.8, .008), center=(x, 1, 3.688), color=(.55,.55,.53)))
scene.include("architecture", architecture)

# Fine straight joints in the dark tiled floor.
floor_details = Asset("floor_tile_joints")
for i in range(15):
    x = -5.25 + i * .75
    floor_details.include("long_%d" % i, box((.012, 15, .005), center=(x, 1, .003), color=(.32,.32,.30)))
for i in range(19):
    y = -6 + i * .75
    floor_details.include("cross_%d" % i, box((10.8, .012, .005), center=(0, y, .004), color=(.31,.31,.29)))
scene.include("floor_tiles", floor_details)

# Left-side booths, with a visible broad back and pale tabletop.
for i, y in enumerate((-4.3, -1.65, 1.0, 3.65, 5.7)):
    booth = Asset("booth_%d" % i)
    booth.include("back", box((2.45, .16, 1.03), center=(-4.05, y, .77), color=upholstery))
    booth.include("top_edge", box((2.47, .18, .035), center=(-4.05, y, 1.30), color=(.38,.38,.37)))
    booth.include("seat", box((2.25, .74, .15), center=(-4.08, y+.48, .47), color=upholstery))
    booth.include("tabletop", box((2.25, 1.05, .075), center=(-3.87, y+1.10, .77), color=tablecol))
    booth.include("table_pedestal", rod(.055, start=(-3.85,y+1.1,.08), end=(-3.85,y+1.1,.74), color=metal))
    scene.include("booth_%d" % i, booth)

def add_table(name, x, y, w=1.25, d=.85):
    a = Asset(name)
    a.include("top", box((w,d,.065), center=(x,y,.76), color=tablecol))
    a.include("edge", box((w+.025,d+.025,.025), center=(x,y,.725), color=(.29,.29,.28)))
    a.include("pedestal", rod(.055, start=(x,y,.08), end=(x,y,.72), color=metal))
    a.include("foot", box((.56,.48,.045), center=(x,y,.045), color=metal))
    scene.include(name, a)

def add_chair(name, x, y, facing=1):
    # Seat and upright back are kept separate and editable.
    a = Asset(name)
    a.include("seat", box((.62,.58,.10), center=(x,y,.48), color=upholstery))
    a.include("back", box((.64,.10,.74), center=(x,y-facing*.28,.86), color=(.29,.29,.28)))
    a.include("back_rim", box((.67,.035,.035), center=(x,y-facing*.34,1.24), color=metal))
    a.include("stem", rod(.055, start=(x,y,.08), end=(x,y,.43), color=metal))
    a.include("base", box((.52,.45,.05), center=(x,y,.05), color=metal))
    scene.include(name, a)

# Rows of tables with chairs on their near and far sides.
for row, y in enumerate((-3.0, -.25, 2.35, 4.7)):
    for col, x in enumerate((-.9, 1.55, 3.65)):
        if row == 0 and col == 0:
            continue
        add_table("table_%d_%d" % (row,col), x,y,1.20,.83)
        add_chair("chair_near_%d_%d" % (row,col), x-.12,y-.82,1)
        if row > 0 or col != 2:
            add_chair("chair_far_%d_%d" % (row,col), x+.12,y+.78,-1)

# Pendant lamps: flattened domes and lower rims, suspended from the ceiling.
def add_lamp(name, x, y, z, r):
    a = Asset(name)
    a.include("cord", rod(.012, start=(x,y,z+.24), end=(x,y,3.69), color=lampcol))
    a.include("canopy", rod(r*.18, start=(x,y,3.67), end=(x,y,3.70), color=lampcol))
    a.include("neck", rod(r*.39, start=(x,y,z+.02), end=(x,y,z+.28), color=lampcol))
    dome = ball(r, center=(x,y,z), color=lampcol)
    dome.resize((1,1,.43))
    a.include("shade", dome)
    a.include("lower_rim", rod(r*.94, start=(x,y,z-.12), end=(x,y,z-.085), color=(.10,.10,.095)))
    scene.include(name, a)

add_lamp("large_left_pendant", -4.1, -2.0, 2.80, .74)
for i, (x,y,z,r) in enumerate([
    (-4.0,1.2,2.84,.40), (-3.8,4.0,2.83,.34),
    (-1.5,4.8,2.88,.30), (.1,3.9,2.94,.34),
    (1.55,3.2,2.95,.39), (3.25,4.25,2.90,.29),
    (4.25,1.8,2.91,.42), (5.0,5.5,2.95,.30)]):
    add_lamp("pendant_%d" % i,x,y,z,r)

# Right foreground plant, with an open branching silhouette.
plant = Asset("foreground_plant")
plant.include("pot", box((.62,.62,.64), center=(4.60,-.15,.32), color=(.27,.27,.25)))
for i in range(7):
    angle = i*2.399
    root = (4.60 + .06*math.cos(angle), -.15 + .06*math.sin(angle), .43)
    tip = (4.60 + .40*math.cos(angle), -.15 + .40*math.sin(angle), 2.12 + .20*(i%3))
    plant.include("stem_%d" % i, rod(.018, start=root, end=tip, color=leafcol))
    for j in range(4):
        t = .53 + .13*j
        sx = root[0]*(1-t)+tip[0]*t
        sy = root[1]*(1-t)+tip[1]*t
        sz = root[2]*(1-t)+tip[2]*t
        ang = angle + (-1 if j%2 else 1)*.72
        ex = sx + .58*math.cos(ang)
        ey = sy + .58*math.sin(ang)
        ez = sz + .18 + .08*(j%2)
        leaf = ball(1, center=((sx+ex)/2,(sy+ey)/2,(sz+ez)/2), color=leafcol)
        leaf.resize((.32,.055,.022))
        leaf.turn(axis="+z", degrees=math.degrees(ang))
        leaf.turn(axis="+y", degrees=-17)
        plant.include("leaf_%d_%d" % (i,j), leaf)
scene.include("plant", plant)

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
background.inputs["Color"].default_value = (0.82, 0.82, 0.80, 1)
background.inputs["Strength"].default_value = .8

set_view((0.0, -10.8, 3.05), (0.0, 3.2, 1.73), lens=30, sensor=36)
area_emitter((0, 4.7, 3.4), power=900, size=8, target=(0,0,.5))
area_emitter((4.7, 0, 3.0), power=600, size=6, target=(0,0,1))
