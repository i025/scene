# Reference inventory, approximate normalized image bounds:
# Pale wall: (0,0)-(.82,.74), behind the sofa.
# Dark gathered curtain: (.81,0)-(.98,.43), partly hidden by right arm.
# Mustard sofa: (.02,.28)-(.97,.95), two wide back cushions, seat
# cushions, broad arms, upholstered lower front, and a loose left pillow.
# Coffee table: (.32,.57)-(1,1), dark top and legs; cropped right and
# bottom, overlapping the sofa. Its rear legs are mostly obscured.
# Two white cups with saucers and overlapping rectangular papers:
# (.40,.54)-(.60,.69) and (.65,.54)-(.88,.70).
# Dark flowerpot with green foliage and pale blue flower clusters:
# (.55,.33)-(.73,.65), in front of the sofa.
# Gray foreground rug; hidden furniture surfaces are uncertain.
#
# Review of the second rendering: the sofa occupies too little vertical
# space, its lower edge sits too high, the table legs end within the frame,
# and the sofa is too pale. The curtain is too regular and the foliage
# lacks the reference's dense lower leaves. The revised geometry extends
# the sofa and legs downward, warms the upholstery, and gathers the curtain.
#
# Estimated expanded primitive count: architecture 3; curtain 10;
# sofa 3 boxes plus 7 fillet boxes (up to 182); table 6; two settings 18;
# plant approximately 120. Total approximately 342 primitives.

from sceneact import *
import bpy
import math

scene = Scene("Living room")

wall = (.76, .75, .73)
sofa_dark = (.48, .22, .055)
sofa_front = (.59, .30, .075)
sofa_seat = (.68, .37, .11)
sofa_back = (.70, .40, .15)
table_color = (.035, .025, .020)
white = (.88, .88, .85)
green = (.19, .29, .10)

architecture = Asset("Architecture")
architecture.include("wall", box((10, .12, 5.5), center=(0, .95, 2.0), color=wall))
architecture.include("floor", box((10, 9, .10), center=(0, -1.5, -.57),
                                   color=(.19, .17, .16)))
architecture.include("rug", box((7, 4, .025), center=(0, -1.9, -.495),
                                 color=(.30, .29, .28)))
scene.include("architecture", architecture)

curtain = Asset("Gathered gray curtain")
curtain.include("backing", box((.89, .12, 3.8), center=(2.25, .79, 1.95),
                               color=(.055, .055, .060)))
for i in range(5):
    x = 1.91 + i * .16
    c = [(.10, .10, .11), (.20, .20, .21), (.08, .08, .09)][i % 3]
    curtain.include("upper_fold_%d" % i,
                    box((.105, .08, 2.9), center=(x, .67, 2.30), color=c))
for i in range(4):
    fold = box((.12, .10, 1.25), center=(2.17 + .13*i, .57, 1.45),
               color=(.14 + .025*i,)*3)
    fold.turn(axis="+y", degrees=-18 - 6*i)
    curtain.include("gathered_fold_%d" % i, fold)
scene.include("curtain", curtain)

couch = Asset("Mustard upholstered sofa")
couch.include("lower_base", box((5.22, .98, 1.10), center=(0, .13, .11),
                                color=sofa_dark))
couch.include("front_lower_panel", box((4.34, .07, .98), center=(0, -.385, .105),
                                       color=sofa_front))
couch.include("seat_deck", box((4.38, .98, .20), center=(0, -.03, .73),
                               color=(.45, .21, .05)))
couch.include("left_arm", fillet_box((.65, 1.08, 1.88), radius=.09,
                                     center=(-2.30, -.04, .45), color=sofa_dark))
couch.include("right_arm", fillet_box((.65, 1.08, 1.88), radius=.09,
                                      center=(2.30, -.04, .45), color=sofa_front))
for i, x in enumerate((-1.09, 1.09)):
    couch.include("seat_cushion_%d" % i,
                  fillet_box((2.13, .92, .38), radius=.11,
                             center=(x, -.10, .91), color=sofa_seat))
for i, x in enumerate((-1.08, 1.08)):
    couch.include("back_cushion_%d" % i,
                  fillet_box((2.12, .34, 1.12), radius=.08,
                             center=(x, .43, 1.52), color=sofa_back))
pillow = fillet_box((.86, .20, .78), radius=.06,
                    center=(-1.68, .12, 1.47), color=(.82, .50, .18))
pillow.turn(axis="+y", degrees=-14)
couch.include("loose_left_pillow", pillow)
scene.include("sofa", couch)

coffee = Asset("Dark coffee table")
coffee.include("top", box((3.70, 1.25, .12), center=(.90, -1.38, .79),
                           color=table_color))
coffee.include("front_apron", box((3.50, .08, .20), center=(.90, -1.96, .65),
                                   color=(.025, .018, .015)))
for ix, x in enumerate((-.79, 2.59)):
    for iy, y in enumerate((-.83, -1.94)):
        coffee.include("leg_%d_%d" % (ix, iy),
                       box((.14, .14, 1.22), center=(x, y, .11),
                           color=(.025, .018, .015)))
scene.include("coffee_table", coffee)

for i, (x, y) in enumerate(((.04, -1.38), (1.37, -1.30))):
    setting = Asset("Tea setting %d" % (i + 1))
    paper = box((.77, .48, .014), center=(x, y, .861), color=(.57, .63, .60))
    paper.turn(axis="+z", degrees=(-7 if i == 0 else 5))
    setting.include("paper", paper)
    napkin = box((.65, .40, .012), center=(x+.025, y+.01, .872),
                 color=(.82, .82, .79))
    napkin.turn(axis="+z", degrees=(4 if i == 0 else -4))
    setting.include("napkin", napkin)
    setting.include("saucer", rod(.245, length=.025, center=(x, y, .891), color=white))
    setting.include("cup", rod(.145, length=.25, center=(x, y, 1.025), color=white))
    setting.include("rim", rod(.158, length=.022, center=(x, y, 1.157),
                               color=(.95, .95, .92)))
    setting.include("inside", rod(.125, length=.006, center=(x, y, 1.171),
                                  color=(.65, .62, .56)))
    hx = x - .16
    setting.include("handle_top", rod(.020, start=(hx, y, 1.10),
                                      end=(hx-.095, y, 1.11), color=white))
    setting.include("handle_side", rod(.020, start=(hx-.095, y, 1.11),
                                       end=(hx-.085, y, .99), color=white))
    setting.include("handle_bottom", rod(.020, start=(hx-.085, y, .99),
                                         end=(hx, y, .98), color=white))
    scene.include("tea_setting_%d" % i, setting)

plant = Asset("Flower pot")
px, py = .73, -1.06
plant.include("pot_body", rod(.20, length=.32, center=(px, py, 1.03),
                               color=(.065, .075, .060)))
plant.include("pot_rim", rod(.215, length=.045, center=(px, py, 1.21),
                              color=(.09, .10, .08)))
plant.include("soil", rod(.18, length=.012, center=(px, py, 1.238),
                          color=(.08, .07, .055)))
tips = [
    (-.31, -.02, .51), (-.23, .03, .65), (-.13, -.06, .43),
    (-.05, .02, .77), (.06, -.05, .60), (.18, .04, .66),
    (.29, -.03, .50), (.34, .03, .36), (-.34, .07, .32),
    (.11, .09, .43), (-.12, .10, .52), (.24, -.06, .40)
]
for i, (dx, dy, dz) in enumerate(tips):
    base = (px, py, 1.23)
    end = (px+dx, py+dy, 1.23+dz)
    plant.include("stem_%02d" % i, rod(.008, start=base, end=end, color=green))
    for j, f in enumerate((.30, .43, .57, .70)):
        qx, qy, qz = px+dx*f, py+dy*f, 1.23+dz*f
        leaf = ball(.045, center=(qx + (-1 if (i+j)%2 else 1)*.045, qy, qz),
                    color=(.25, .36, .13))
        leaf.resize((1.6, .45, .48))
        plant.include("leaf_%02d_%d" % (i, j), leaf)
    if i < 9:
        for j in range(5):
            a = j * 2 * math.pi / 5
            plant.include("flower_%02d_%d" % (i, j),
                          ball(.035, center=(end[0]+.045*math.cos(a),
                                             end[1]+.035*math.sin(a),
                                             end[2]+.025*(j%2)),
                               color=(.48,.53,.64) if j%2 else (.64,.65,.72)))
scene.include("flower_pot", plant)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .70, .68, 1)
background.inputs["Strength"].default_value = .35

set_view((0.0, -7.6, 2.05), (0.0, -.05, 1.18), lens=43)
area_emitter((-3.8, -4.0, 5.2), power=750, size=4.5, target=(0, 0, .8))
area_emitter((3.0, -1.5, 3.6), power=120, size=3, target=(0, 0, 1))
