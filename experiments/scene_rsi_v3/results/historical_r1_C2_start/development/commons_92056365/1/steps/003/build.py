# Reference inventory, approximate normalized image bounds:
# Ceiling (0,0)-(1,.32): pale, closely spaced parallel panels, with a few
# small circular fixtures. Rear glazing (.03,.30)-(.65,.57) joins right
# glazing (.65,.23)-(1,.56); dark mullions and a low sill divide the panes.
# The exterior is bright and indistinct, with faint foliage.
# Dark tiled floor occupies the lower half, interrupted by furniture.
# Left booths (0,.50)-(.45,1): dark transverse backs, pale tables, much
# cropped by the frame. The nearest pale tabletop fills the lower left.
# Center/right dining furniture (.36,.50)-(.89,1): rectangular tabletops
# and upholstered chairs with separate backs, seats and metal pedestals.
# Large black pendant (.02,.03)-(.23,.40); smaller pendants across the
# room and right side. Foreground palm (.77,.39)-(1,1) obscures windows
# and chairs; smaller foliage appears near the back windows.
# Furniture behind other objects and the view through the windows are uncertain.
#
# Review of the second render: the pendant at upper left is much too small,
# the foreground palm is mostly off-frame, the closest left tabletop is
# missing, and ceiling seams radiate toward the back instead of running
# across the image. The rear/right window corner is also too far right.
# This revision adjusts those local objects, seam direction and view direction.
#
# Expanded primitive estimate: architecture and joints 105, booths 30,
# tables 56, chairs 135, lamps 45, plants 118, exterior suggestions 13:
# approximately 502 meshes. No Boolean or fillet expansions.

from sceneact import *
import bpy
import math
import random

random.seed(11)
scene = Scene("Restaurant")

white = (.80, .80, .78)
ceiling = (.84, .84, .82)
floorcol = (.12, .12, .115)
trim = (.22, .22, .21)
glass = (.96, .96, .94)
upholstery = (.20, .20, .19)
chaircol = (.27, .27, .26)
tablecol = (.68, .68, .65)
metal = (.46, .46, .44)
dark = (.045, .045, .043)
leafcol = (.075, .095, .072)

architecture = Asset("architecture")
architecture.include("floor", box((11, 22, .12), center=(0, -1, -.06), color=floorcol))
architecture.include("ceiling", box((11, 22, .10), center=(0, -1, 3.75), color=ceiling))
architecture.include("rear_lower_wall", box((11, .12, .72), center=(0, 7, .36), color=white))
architecture.include("rear_header", box((11, .12, .23), center=(0, 7, 3.62), color=white))
architecture.include("rear_glazing", box((11, .035, 2.72), center=(0, 7.06, 2.10), color=glass))
architecture.include("right_lower_wall", box((.12, 21, .68), center=(5.5, -3, .34), color=white))
architecture.include("right_glazing", box((.035, 21, 2.76), center=(5.56, -3, 2.09), color=glass))
architecture.include("right_header", box((.12, 21, .22), center=(5.5, -3, 3.64), color=white))
for i, x in enumerate((-5.4, -3.2, -1.1, 1.1, 3.25, 5.4)):
    architecture.include("rear_mullion_%d" % i,
        box((.065, .10, 2.83), center=(x, 6.96, 2.10), color=trim))
architecture.include("rear_sill", box((11, .15, .075), center=(0, 6.96, .73), color=trim))
for i, y in enumerate((-7.8, -5, -2.2, .6, 3.4, 6.2)):
    architecture.include("right_mullion_%d" % i,
        box((.10, .075, 2.90), center=(5.46, y, 2.09), color=trim))
architecture.include("right_sill", box((.12, 21, .075), center=(5.45, -3, .70), color=trim))
for i in range(47):
    y = -12 + i * .42
    architecture.include("ceiling_joint_%d" % i,
        box((10.9, .009, .008), center=(0, y, 3.694), color=(.60, .60, .58)))
for i, (x, y) in enumerate(((-2.8, -3), (1.0, -1), (-1.0, 3), (3.0, 4))):
    architecture.include("ceiling_fixture_%d" % i,
        rod(.11, start=(x,y,3.68), end=(x,y,3.695), color=(.48,.48,.46)))
scene.include("architecture", architecture)

floor_details = Asset("floor_tile_joints")
for i in range(19):
    x = -5.4 + i * .6
    floor_details.include("long_%d" % i,
        box((.012, 21, .006), center=(x, -1, .004), color=(.29,.29,.27)))
for i in range(27):
    y = -12 + i * .7
    floor_details.include("cross_%d" % i,
        box((10.8, .012, .006), center=(0, y, .005), color=(.29,.29,.27)))
scene.include("floor_tiles", floor_details)

for i, y in enumerate((-6.8, -4.3, -1.8, .7, 3.2, 5.7)):
    booth = Asset("booth_%d" % i)
    booth.include("back", box((2.65,.16,1.05), center=(-4.05,y,.77), color=upholstery))
    booth.include("top_edge", box((2.67,.18,.03), center=(-4.05,y,1.30), color=(.36,.36,.34)))
    booth.include("seat", box((2.45,.73,.14), center=(-4.08,y+.45,.47), color=upholstery))
    booth.include("tabletop", box((2.55,1.08,.065), center=(-3.95,y+1.12,.76), color=tablecol))
    booth.include("table_pedestal",
        rod(.055, start=(-3.95,y+1.12,.08), end=(-3.95,y+1.12,.72), color=metal))
    scene.include("booth_%d" % i, booth)

def add_table(name, x, y):
    a = Asset(name)
    a.include("top", box((1.22,.90,.065), center=(x,y,.76), color=tablecol))
    a.include("dark_edge", box((1.24,.92,.025), center=(x,y,.72), color=(.23,.23,.22)))
    a.include("pedestal", rod(.055, start=(x,y,.08), end=(x,y,.71), color=metal))
    a.include("foot", box((.56,.48,.045), center=(x,y,.045), color=metal))
    scene.include(name, a)

def add_chair(name, x, y, facing=1):
    a = Asset(name)
    a.include("seat", box((.68,.61,.10), center=(x,y,.48), color=chaircol))
    a.include("back", box((.70,.11,.75), center=(x,y-facing*.29,.85), color=chaircol))
    a.include("top_rim", box((.72,.035,.025), center=(x,y-facing*.355,1.23), color=metal))
    a.include("stem", rod(.06, start=(x,y,.08), end=(x,y,.43), color=metal))
    a.include("base", box((.56,.48,.05), center=(x,y,.05), color=metal))
    scene.include(name, a)

for row, y in enumerate((-4.0,-1.25,1.4,3.85,5.85)):
    for col, x in enumerate((-.75,1.55,3.65)):
        if row == 0 and col == 0:
            continue
        add_table("table_%d_%d" % (row,col), x, y)
        add_chair("chair_near_%d_%d" % (row,col), x-.12, y-.80, 1)
        if row > 0 or col != 2:
            add_chair("chair_far_%d_%d" % (row,col), x+.12, y+.78, -1)

def add_lamp(name, x, y, z, r):
    a = Asset(name)
    a.include("cord", rod(.012, start=(x,y,z+.47), end=(x,y,3.69), color=dark))
    a.include("ceiling_cap", rod(r*.14, start=(x,y,3.67), end=(x,y,3.70), color=dark))
    a.include("neck", rod(r*.36, start=(x,y,z+.10), end=(x,y,z+.47), color=dark))
    shade = ball(r, center=(x,y,z), color=dark)
    shade.resize((1,1,.55))
    a.include("shade", shade)
    a.include("rim", rod(r*.95, start=(x,y,z-.18), end=(x,y,z-.14), color=dark))
    scene.include(name, a)

add_lamp("large_left_pendant", -2.85, -5.8, 2.72, .72)
for i, (x,y,z,r) in enumerate([
    (-4.0,.3,2.78,.42), (-3.8,3.4,2.79,.34),
    (-1.5,4.8,2.83,.30), (.1,3.9,2.88,.34),
    (1.55,3.0,2.88,.39), (3.25,4.25,2.84,.29),
    (4.3,1.6,2.84,.43), (5.0,5.5,2.90,.30)
]):
    add_lamp("pendant_%d" % i,x,y,z,r)

# Fronds spread outward, with paired narrow leaves and intervening gaps.
plant = Asset("foreground_plant")
px, py = 3.75, -4.15
plant.include("pot", box((.66,.66,.68), center=(px,py,.34), color=(.25,.25,.23)))
for i in range(12):
    angle = i * 2.399
    base = (px,py,.40)
    tip = (px + .80*math.cos(angle), py + .80*math.sin(angle),
           2.35 + .15*(i%3))
    plant.include("frond_%d" % i, rod(.014, start=base, end=tip, color=leafcol))
    for j in range(6):
        t = .44 + .09*j
        sx = base[0]*(1-t)+tip[0]*t
        sy = base[1]*(1-t)+tip[1]*t
        sz = base[2]*(1-t)+tip[2]*t
        side = -1 if j%2 else 1
        a = angle + side*.95
        length = .65*(1.15-.55*t)
        end = (sx+length*math.cos(a), sy+length*math.sin(a), sz+.23)
        plant.include("leaf_%d_%d" % (i,j),
            rod(.025, start=(sx,sy,sz), end=end, color=leafcol))
scene.include("foreground_plant", plant)

rearplant = Asset("rear_window_plants")
for k, (x,y) in enumerate(((-1.8,5.3),(-1.2,5.5),(-.7,5.25))):
    for i in range(6):
        angle = i*2.4+k
        start = (x,y,.48)
        end = (x+.32*math.cos(angle),y+.32*math.sin(angle),1.20+.09*(i%3))
        rearplant.include("stem_%d_%d" % (k,i), rod(.012,start=start,end=end,color=leafcol))
        mid = tuple((start[q]+end[q])/2 for q in range(3))
        side = (end[0]+.15*math.cos(angle+1.2),end[1]+.15*math.sin(angle+1.2),end[2]-.1)
        rearplant.include("leaf_%d_%d" % (k,i), rod(.025,start=mid,end=side,color=leafcol))
scene.include("rear_window_plants", rearplant)

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
background.inputs["Color"].default_value = (.85,.85,.83,1)
background.inputs["Strength"].default_value = .8

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    if c[0] > .94 and c[1] > .94 and c[2] > .92:
        bsdf.inputs["Emission Color"].default_value = (.92,.92,.90,1)
        bsdf.inputs["Emission Strength"].default_value = .7

set_view((-.55,-8.1,2.65), (1.15,3.1,1.75), lens=30, sensor=36)
area_emitter((0,4.5,3.4), power=1000, size=8, target=(0,0,.5))
area_emitter((4.7,-1,3.0), power=650, size=6, target=(0,0,1))
