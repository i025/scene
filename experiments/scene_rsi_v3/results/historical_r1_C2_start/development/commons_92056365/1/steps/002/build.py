# Reference inventory, approximate normalized image bounds:
# Bright ceiling, narrow parallel panel seams: (0,0)-(1,.32).
# Rear and right windows, dark mullions and bright exterior:
# (.02,.23)-(1,.58). The outside view is indistinct.
# Dark tiled floor: (0,.55)-(1,1), partly hidden by furniture.
# Left booth backs and tabletops: (0,.51)-(.45,1), several cropped.
# Center and right square tables and pedestal chairs: (.35,.50)-(.91,1).
# Large foreground pendant: (.02,.04)-(.23,.40); smaller pendants
# extend toward the rear and right. Their suspension cords are thin.
# Dense plant at right: (.77,.39)-(1,1), with its pot mostly hidden.
# Smaller plants are visible in front of the rear windows.
#
# Review of first render: the ceiling was cropped away at the top; furniture
# was too small and low in the frame; windows looked like opaque gray walls;
# the foreground lamp was too flat; the right plant was much too sparse.
# The revised camera moves forward and lower, the ceiling extends behind it,
# the window surfaces are brighter, and plant and lamp silhouettes are fuller.
#
# Primitive estimate: architecture and joints 84; booths 25; dining tables
# 44; chairs 115; pendants 45; foreground and rear plants 100; approximately
# 413 separate primitives. No booleans or fillet expansions are used.

from sceneact import *
import bpy
import math
import random

random.seed(11)
scene = Scene("Restaurant")

white = (.78, .78, .76)
ceiling = (.82, .82, .80)
floorcol = (.12, .12, .115)
trim = (.25, .25, .24)
glass = (.96, .96, .94)
upholstery = (.21, .21, .20)
chaircol = (.29, .29, .28)
tablecol = (.67, .67, .64)
metal = (.45, .45, .43)
dark = (.055, .055, .052)
leafcol = (.095, .12, .09)

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
for i in range(28):
    x = -5.4 + i * .4
    architecture.include("ceiling_joint_%d" % i,
                         box((.008, 21.8, .008), center=(x, -1, 3.694),
                             color=(.54, .54, .52)))
scene.include("architecture", architecture)

floor_details = Asset("floor_tile_joints")
for i in range(19):
    x = -5.4 + i * .6
    floor_details.include("long_%d" % i,
                          box((.012, 21, .006), center=(x, -1, .004),
                              color=(.30, .30, .28)))
for i in range(27):
    y = -12 + i * .7
    floor_details.include("cross_%d" % i,
                          box((10.8, .012, .006), center=(0, y, .005),
                              color=(.30, .30, .28)))
scene.include("floor_tiles", floor_details)

# The backs are transverse to the viewing direction, with tabletops between.
for i, y in enumerate((-5.8, -3.3, -.8, 1.7, 4.2, 6.1)):
    booth = Asset("booth_%d" % i)
    booth.include("back", box((2.55, .16, 1.05),
                              center=(-4.10, y, .77), color=upholstery))
    booth.include("top_edge", box((2.57, .18, .03),
                                  center=(-4.10, y, 1.30), color=(.37, .37, .35)))
    booth.include("seat", box((2.35, .73, .14),
                              center=(-4.12, y + .45, .47), color=upholstery))
    booth.include("tabletop", box((2.4, 1.06, .065),
                                  center=(-3.95, y + 1.12, .76), color=tablecol))
    booth.include("table_pedestal",
                  rod(.055, start=(-3.95, y + 1.12, .08),
                      end=(-3.95, y + 1.12, .72), color=metal))
    scene.include("booth_%d" % i, booth)

def add_table(name, x, y, w=1.22, d=.90):
    a = Asset(name)
    a.include("top", box((w, d, .065), center=(x, y, .76), color=tablecol))
    a.include("dark_edge", box((w + .02, d + .02, .025),
                               center=(x, y, .72), color=(.23, .23, .22)))
    a.include("pedestal", rod(.055, start=(x, y, .08), end=(x, y, .71), color=metal))
    a.include("foot", box((.56, .48, .045), center=(x, y, .045), color=metal))
    scene.include(name, a)

def add_chair(name, x, y, facing=1):
    a = Asset(name)
    a.include("seat", box((.68, .61, .10), center=(x, y, .48), color=chaircol))
    a.include("back", box((.70, .11, .75),
                          center=(x, y - facing * .29, .85), color=chaircol))
    a.include("top_rim", box((.72, .035, .025),
                             center=(x, y - facing * .355, 1.23), color=metal))
    a.include("stem", rod(.06, start=(x, y, .08), end=(x, y, .43), color=metal))
    a.include("base", box((.56, .48, .05), center=(x, y, .05), color=metal))
    scene.include(name, a)

for row, y in enumerate((-4.0, -1.25, 1.4, 3.85, 5.85)):
    for col, x in enumerate((-.75, 1.55, 3.65)):
        if row == 0 and col == 0:
            continue
        add_table("table_%d_%d" % (row, col), x, y)
        add_chair("chair_near_%d_%d" % (row, col), x - .12, y - .80, 1)
        if row > 0 or col != 2:
            add_chair("chair_far_%d_%d" % (row, col), x + .12, y + .78, -1)

# Domed shades have a substantial cylindrical neck and a broad dark rim.
def add_lamp(name, x, y, z, r):
    a = Asset(name)
    a.include("cord", rod(.012, start=(x, y, z + .47),
                          end=(x, y, 3.69), color=dark))
    a.include("ceiling_cap", rod(r * .14, start=(x, y, 3.67),
                                 end=(x, y, 3.70), color=dark))
    a.include("neck", rod(r * .36, start=(x, y, z + .10),
                          end=(x, y, z + .47), color=dark))
    shade = ball(r, center=(x, y, z), color=dark)
    shade.resize((1, 1, .55))
    a.include("shade", shade)
    a.include("rim", rod(r * .95, start=(x, y, z - .18),
                         end=(x, y, z - .14), color=dark))
    scene.include(name, a)

add_lamp("large_left_pendant", -4.1, -3.0, 2.68, .82)
for i, (x, y, z, r) in enumerate([
    (-4.0, .3, 2.78, .42), (-3.8, 3.4, 2.79, .34),
    (-1.5, 4.8, 2.83, .30), (.1, 3.9, 2.88, .34),
    (1.55, 3.0, 2.88, .39), (3.25, 4.25, 2.84, .29),
    (4.3, 1.6, 2.84, .43), (5.0, 5.5, 2.90, .30)
]):
    add_lamp("pendant_%d" % i, x, y, z, r)

# Narrow pointed leaves represented as slender rods radiating from curved fronds.
plant = Asset("foreground_plant")
plant.include("pot", box((.66, .66, .68), center=(4.65, -.9, .34),
                         color=(.25, .25, .23)))
for i in range(11):
    angle = i * 2.399
    base = (4.65, -.9, .40)
    tip = (4.65 + .65 * math.cos(angle),
           -.9 + .65 * math.sin(angle), 2.18 + .20 * (i % 3))
    plant.include("frond_%d" % i, rod(.014, start=base, end=tip, color=leafcol))
    for j in range(6):
        t = .46 + .085 * j
        sx = base[0] * (1 - t) + tip[0] * t
        sy = base[1] * (1 - t) + tip[1] * t
        sz = base[2] * (1 - t) + tip[2] * t
        side = -1 if j % 2 else 1
        a = angle + side * .95
        length = .57 * (1.15 - .55 * t)
        end = (sx + length * math.cos(a),
               sy + length * math.sin(a), sz + .23)
        plant.include("leaf_%d_%d" % (i, j),
                      rod(.023, start=(sx, sy, sz), end=end, color=leafcol))
scene.include("foreground_plant", plant)

rearplant = Asset("rear_window_plants")
for k, (x, y) in enumerate(((-1.8, 5.3), (-1.2, 5.5), (-.7, 5.25))):
    for i in range(6):
        angle = i * 2.4 + k
        start = (x, y, .48)
        end = (x + .32 * math.cos(angle), y + .32 * math.sin(angle),
               1.20 + .09 * (i % 3))
        rearplant.include("stem_%d_%d" % (k, i),
                          rod(.012, start=start, end=end, color=leafcol))
        mid = ((start[0] + end[0]) / 2,
               (start[1] + end[1]) / 2, (start[2] + end[2]) / 2)
        side = (end[0] + .15 * math.cos(angle + 1.2),
                end[1] + .15 * math.sin(angle + 1.2), end[2] - .1)
        rearplant.include("leaf_%d_%d" % (k, i),
                          rod(.025, start=mid, end=side, color=leafcol))
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
background.inputs["Color"].default_value = (.85, .85, .83, 1)
background.inputs["Strength"].default_value = .8

# Make the bright window planes read as daylight rather than unlit gray walls.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    if c[0] > .94 and c[1] > .94 and c[2] > .92:
        bsdf.inputs["Emission Color"].default_value = (.92, .92, .90, 1)
        bsdf.inputs["Emission Strength"].default_value = .7

set_view((-.55, -8.1, 2.65), (.35, 3.1, 1.75), lens=30, sensor=36)
area_emitter((0, 4.5, 3.4), power=1000, size=8, target=(0, 0, .5))
area_emitter((4.7, -1, 3.0), power=650, size=6, target=(0, 0, 1))
