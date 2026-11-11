# Reference inventory and approximate normalized image bounds (x right, y down):
# - Pale wall: (0,0) to (0.83,0.75), largely occluded by sofa.
# - Dark curtain/window area: (0.81,0) to (1,0.43), vertically folded gray fabric.
# - Mustard sofa: (0.02,0.28) to (0.97,0.95), with two arms, two back
#   cushions, three seat areas, a lower front panel, and a loose left pillow.
# - Dark coffee table: (0.32,0.59) to (1,1); broad rectangular top overlaps
#   the sofa, with dark legs descending out of frame.
# - Two white cups and saucers: approximately (0.40,0.55)-(0.59,0.68)
#   and (0.65,0.55)-(0.87,0.70), resting on pale rectangular napkins.
# - Central potted flowers: approximately (0.56,0.33)-(0.72,0.65);
#   dark tapered pot, thin green stems, foliage, and blue-lavender blossoms.
# - Gray floor: visible mostly at bottom and lower right.
# Distinctive overlaps: table covers the sofa's lower front; flowers overlap the
# sofa back; the cups and pot sit on the tabletop; curtain lies behind right arm.
# Dominant edges: sofa top nearly horizontal, table's rear edge slopes slightly
# upward to the right, its front edge slopes down to the right, legs near vertical.
# The sofa back, rear table legs, and window details are partly occluded and uncertain.
#
# Visual anchors: sofa top left (.17,.28), right arm top (.81,.41),
# tabletop rear left (.32,.61), pot top (.61,.53), table front right (1,.72).
# Projection points below are approximate correspondences, not calibration.
# Expanded primitive estimate: architecture ~13, sofa ~15, table 5,
# cups/napkins ~24, pot and flowers ~100; total approximately 160 meshes.
# Camera parameters are separate from furniture dimensions.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(18)
scene = Scene("Living room")

# Major geometry parameters.
SOFA_W = 3.75
SOFA_Y = 0.65
SOFA_DEPTH = 0.95
TABLE_W = 2.95
TABLE_DEPTH = 1.02
TABLE_Y = -0.95
TABLE_TOP_Z = 0.69
CAM_POS = (0.05, -7.6, 2.65)
CAM_TARGET = (0.0, 0.12, 1.00)
CAM_LENS = 43

wall = (0.77, 0.76, 0.73)
floor = (0.31, 0.30, 0.29)
ochre = (0.68, 0.34, 0.105)
ochre_light = (0.76, 0.43, 0.16)
ochre_shadow = (0.54, 0.255, 0.068)
wood = (0.045, 0.035, 0.030)
ceramic = (0.88, 0.89, 0.85)
leaf = (0.19, 0.30, 0.12)
leaf_light = (0.32, 0.42, 0.18)
stem = (0.21, 0.29, 0.12)
flower = (0.46, 0.50, 0.65)
flower_light = (0.64, 0.68, 0.78)

architecture = Asset("Architecture")
architecture.include("back_wall", box((10, 0.12, 5), center=(0, 1.38, 2.48), color=wall))
architecture.include("floor", box((10, 10, 0.10), center=(0, 0, -0.05), color=floor))
architecture.include("window_shadow", box((0.85, 0.05, 3.8), center=(2.05, 1.29, 2.35), color=(0.13, 0.13, 0.13)))
# Pleated curtain, with irregular vertical folds.
for i, (x, width, shade) in enumerate([
    (1.68, .18, .22), (1.82, .18, .32), (1.95, .15, .19),
    (2.08, .17, .40), (2.23, .16, .25), (2.37, .15, .13)]):
    architecture.include("curtain_fold_%02d" % i,
        box((width, .10, 3.55), center=(x, 1.18 + .025*(i % 2), 2.26),
            color=(shade, shade*.99, shade*.97)))
scene.include("architecture", architecture)

sofa = Asset("Mustard sofa")
sofa.include("lower_body", fillet_box((SOFA_W-.30, SOFA_DEPTH, .63), .09,
    center=(0, SOFA_Y, .38), color=ochre_shadow))
sofa.include("front_upholstered_panel", fillet_box((SOFA_W-.34, .15, .43), .055,
    center=(0, SOFA_Y-.49, .31), color=ochre))
sofa.include("back_frame", fillet_box((SOFA_W-.32, .32, 1.10), .09,
    center=(0, SOFA_Y+.34, 1.12), color=ochre))
for i, x in enumerate((-0.84, 0.84)):
    sofa.include("back_cushion_%d" % i, fillet_box((1.64, .28, .67), .08,
        center=(x, SOFA_Y+.13, 1.22), color=ochre_light))
for i, x in enumerate((-1.10, 0, 1.10)):
    sofa.include("seat_cushion_%d" % i, fillet_box((1.07, .78, .28), .09,
        center=(x, SOFA_Y-.12, .79), color=ochre_light if i == 1 else ochre))
for side, x in (("left", -1.77), ("right", 1.77)):
    sofa.include(side+"_arm", fillet_box((.39, 1.04, 1.05), .075,
        center=(x, SOFA_Y-.03, .62), color=ochre))
# Pillow rests against left back cushion, with slightly irregular tilt.
pillow = fillet_box((.63, .18, .57), .075, center=(-1.20, SOFA_Y-.16, 1.22),
                    color=(.86, .56, .25))
pillow.turn(axis="+y", degrees=-14)
sofa.include("loose_left_pillow", pillow)
scene.include("sofa", sofa)

table = Asset("Coffee table")
table.include("dark_top", box((TABLE_W, TABLE_DEPTH, .11),
    center=(.35, TABLE_Y, TABLE_TOP_Z), color=wood))
for i, x in enumerate((-.99, 1.69)):
    for j, y in enumerate((TABLE_Y-.40, TABLE_Y+.40)):
        table.include("leg_%d_%d" % (i,j),
            box((.14, .14, .66), center=(x, y, .34), color=wood))
scene.include("coffee_table", table)

# Napkins, plates and cup forms are separate editable parts.
def make_place_setting(name, x, y):
    a = Asset(name)
    nap = box((.67, .42, .018), center=(x, y, .755), color=(.66, .72, .69))
    nap.turn(axis="+z", degrees=-6)
    a.include("folded_napkin", nap)
    nap2 = box((.59, .34, .015), center=(x+.01, y, .768), color=(.84, .86, .80))
    nap2.turn(axis="+z", degrees=4)
    a.include("top_napkin", nap2)
    saucer = ball(.25, center=(x, y, .79), color=ceramic)
    saucer.resize((1, .72, .075))
    a.include("saucer", saucer)
    # A broad white body and darker recessed top give an open cup silhouette.
    a.include("cup_body", rod(.145, start=(x,y,.80), end=(x,y,1.035), color=ceramic))
    a.include("cup_rim", rod(.151, start=(x,y,1.025), end=(x,y,1.046), color=(.95,.95,.91)))
    a.include("coffee_surface", rod(.119, start=(x,y,1.046), end=(x,y,1.049), color=(.47,.40,.30)))
    a.include("handle", sweep_tube(points=[
        (x-.12,y,1.00), (x-.21,y,1.015), (x-.23,y,.96),
        (x-.20,y,.89), (x-.13,y,.88)], radius=.018, color=ceramic))
    scene.include(name, a)

make_place_setting("Left place setting", -.49, -.92)
make_place_setting("Right place setting", 1.04, -.91)

plant = Asset("Flower pot and bouquet")
px, py = .30, -.76
# Pot is assembled from stacked dark tapered cylinders.
for i in range(5):
    z0 = .75 + i*.057
    radius = .14 + i*.012
    plant.include("pot_section_%d" % i, rod(radius, start=(px,py,z0),
        end=(px,py,z0+.061), color=(.10,.115,.09)))
plant.include("pot_lip", rod(.205, start=(px,py,1.025), end=(px,py,1.065),
                              color=(.12,.13,.105)))
plant.include("soil", rod(.177, start=(px,py,1.065), end=(px,py,1.069),
                           color=(.12,.10,.07)))

# Bouquet structure: individual stems, leaf shapes and small flower clusters.
heads = [
    (-.29,-.01,1.46), (-.20,.02,1.56), (-.08,.02,1.39),
    (.01,.02,1.68), (.13,.02,1.52), (.27,.00,1.53),
    (.32,.04,1.44), (.08,-.03,1.34), (-.15,-.06,1.32)]
for i, (dx,dy,z) in enumerate(heads):
    base = (px + dx*.15, py + dy, 1.065)
    end = (px+dx, py+dy, z)
    plant.include("stem_%02d" % i, rod(.009, start=base, end=end, color=stem))
    # Three little leaf ellipsoids distributed along the stem.
    for j in range(3):
        t = .32 + .17*j
        side = -1 if (i+j)%2 else 1
        lx = px + dx*t + side*.065
        ly = py + dy*t + (.025 if j%2 else -.025)
        lz = 1.065 + (z-1.065)*t
        blade = ball(.073, center=(lx,ly,lz), color=leaf_light if j==1 else leaf)
        blade.resize((1.15,.30,.28))
        blade.turn(axis="+y", degrees=side*25)
        plant.include("leaf_%02d_%d" % (i,j), blade)
    # Loose, uneven flower head built from a few visible florets.
    for j in range(7):
        ang = 2*math.pi*j/7
        r = .045 if j else 0
        fl = ball(.033 if j else .042,
                  center=(end[0]+r*math.cos(ang), end[1]+r*.42*math.sin(ang),
                          end[2]+r*.65*math.sin(ang)),
                  color=flower_light if (i+j)%3==0 else flower)
        plant.include("blossom_%02d_%d" % (i,j), fl)
scene.include("flower_arrangement", plant)

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
background.inputs["Color"].default_value = (0.72, 0.72, 0.70, 1)
background.inputs["Strength"].default_value = 0.45

sc.render.resolution_x = 512
sc.render.resolution_y = 342
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((-3.4, -4.0, 5.4), power=850, size=4.5,
             target=(0, .2, .8), color=(1.0,.92,.82))
area_emitter((3.7, -.1, 4.6), power=450, size=3.0,
             target=(0, .5, 1.0), color=(.86,.91,1.0))

# Projection check: reference coordinates and geometry landmarks are kept separate.
landmarks = [
    ("sofa upper left", (.17,.28), (-1.68, .99, 1.555)),
    ("right arm top", (.81,.41), (1.57, .10, 1.145)),
    ("table rear left", (.32,.61), (-1.125, -.44, .745)),
    ("pot upper rim", (.61,.53), (.30, -.76, 1.065)),
    ("table front right", (1.0,.72), (1.825, -1.46, .745)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=512, y=342,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark | reference | projected")
for name, ref, p in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
