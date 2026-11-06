# Reference inventory, approximate normalized image bounds:
# Wall: (0, 0)-(.83, .74), mostly blank and behind the furniture.
# Curtain: (.81, 0)-(.98, .43), dark gathered folds.
# Mustard sofa: (.02, .28)-(.97, .95), two broad back cushions, seat
# cushions, thick arms, lower upholstered front, and one loose left pillow.
# Coffee table: (.32, .57)-(1, 1), dark top and legs, cropped at right
# and bottom, overlapping the sofa.
# Two white cups, saucers and papers: (.40, .54)-(.60, .69) and
# (.65, .54)-(.88, .70), on the table.
# Dark flower pot and green stems with pale blue flowers:
# (.55, .33)-(.73, .65), in front of the sofa.
# Gray rug occupies the foreground; the furniture hides its rear edge.
# Hidden sofa, curtain and table surfaces are uncertain.
#
# Comparison with the first rendering: the sofa was too small and pale,
# the table was too far left, and the camera looked down too steeply.
# The curtain appeared as straight stripes and the plant was too sparse.
# This revision enlarges and warms the sofa, shifts the foreground table
# right, lowers the camera, and adds gathered curtain and foliage shapes.
#
# Expanded primitive estimate: architecture 3; curtain 12; sofa 7 boxes
# plus 6 fillet boxes (up to 156); table 6; settings 18; plant about 115.
# Total approximately 317 primitives, including fillet-box expansion.

from sceneact import *
import bpy
import math

scene = Scene("Living room")

wall = (.76, .75, .73)
floor = (.20, .18, .17)
rug = (.32, .31, .30)
sofa = (.55, .275, .085)
sofa_light = (.67, .365, .12)
sofa_back = (.70, .40, .16)
sofa_shadow = (.46, .22, .065)
table_color = (.045, .033, .027)
white = (.86, .87, .84)
green = (.20, .30, .12)
flower = (.48, .53, .64)

architecture = Asset("Architecture")
architecture.include("back_wall", box((10, .12, 5), center=(0, .95, 2.45), color=wall))
architecture.include("floor", box((10, 9, .10), center=(0, -1.5, -.07), color=floor))
architecture.include("rug", box((7, 3.7, .025), center=(0, -1.9, .005), color=rug))
scene.include("architecture", architecture)

curtain = Asset("Curtain")
curtain.include("dark_backing", box((.87, .12, 3.4), center=(2.25, .79, 2.0), color=(.075, .075, .08)))
# Narrow vertical folds and diagonal gathered fabric at the lower right.
for i in range(5):
    x = 1.91 + i * .16
    c = [(.14, .14, .15), (.24, .24, .25), (.11, .11, .12)][i % 3]
    curtain.include("upper_fold_%d" % i,
                    box((.11, .08, 2.8), center=(x, .67, 2.12), color=c))
for i in range(3):
    fold = box((.13, .10, 1.15), center=(2.30 + .13*i, .57, 1.32), color=(.22 + .04*i,)*3)
    fold.turn(axis="+y", degrees=-18 - 7*i)
    curtain.include("gathered_fold_%d" % i, fold)
scene.include("curtain", curtain)

couch = Asset("Mustard sofa")
couch.include("lower_base", box((5.22, .98, .60), center=(0, .13, .36), color=sofa))
couch.include("front_lower_panel", box((4.34, .07, .51), center=(0, -.385, .36), color=sofa_light))
couch.include("seat_deck", box((4.38, .98, .20), center=(0, -.03, .73), color=sofa_shadow))
couch.include("left_arm", fillet_box((.65, 1.08, 1.38), radius=.09,
                                      center=(-2.30, -.04, .70), color=sofa))
couch.include("right_arm", fillet_box((.65, 1.08, 1.38), radius=.09,
                                       center=(2.30, -.04, .70), color=sofa_light))
for i, x in enumerate((-1.09, 1.09)):
    couch.include("seat_cushion_%d" % i,
                  fillet_box((2.13, .92, .34), radius=.11,
                             center=(x, -.10, .90), color=sofa_light))
for i, x in enumerate((-1.08, 1.08)):
    couch.include("back_cushion_%d" % i,
                  fillet_box((2.12, .34, .98), radius=.08,
                             center=(x, .43, 1.46), color=sofa_back))
pillow = fillet_box((.86, .20, .72), radius=.06,
                    center=(-1.68, .12, 1.44), color=(.80, .49, .20))
pillow.turn(axis="+y", degrees=-14)
couch.include("loose_pillow", pillow)
scene.include("sofa", couch)

coffee = Asset("Coffee table")
coffee.include("top", box((3.70, 1.25, .12), center=(.90, -1.38, .79), color=table_color))
coffee.include("front_apron", box((3.50, .08, .20), center=(.90, -1.96, .65), color=(.035, .026, .021)))
for ix, x in enumerate((-.79, 2.59)):
    for iy, y in enumerate((-.83, -1.94)):
        coffee.include("leg_%d_%d" % (ix, iy),
                       box((.14, .14, .72), center=(x, y, .36), color=(.035, .026, .021)))
scene.include("coffee_table", coffee)

for i, (x, y) in enumerate(((.04, -1.38), (1.37, -1.30))):
    setting = Asset("Tea setting %d" % (i + 1))
    paper = box((.77, .48, .014), center=(x, y, .861), color=(.57, .63, .60))
    paper.turn(axis="+z", degrees=(-7 if i == 0 else 5))
    setting.include("paper", paper)
    paper2 = box((.65, .40, .012), center=(x+.025, y+.01, .872), color=(.82, .82, .79))
    paper2.turn(axis="+z", degrees=(4 if i == 0 else -4))
    setting.include("napkin", paper2)
    setting.include("saucer", rod(.245, length=.025, center=(x, y, .891), color=white))
    setting.include("cup_body", rod(.145, length=.25, center=(x, y, 1.025), color=white))
    setting.include("cup_rim", rod(.158, length=.022, center=(x, y, 1.157), color=(.95,.95,.92)))
    setting.include("cup_inside", rod(.125, length=.006, center=(x, y, 1.171), color=(.65,.62,.56)))
    hx = x - .16
    setting.include("handle_top", rod(.020, start=(hx, y, 1.10), end=(hx-.095, y, 1.11), color=white))
    setting.include("handle_side", rod(.020, start=(hx-.095, y, 1.11), end=(hx-.085, y, .99), color=white))
    setting.include("handle_bottom", rod(.020, start=(hx-.085, y, .99), end=(hx, y, .98), color=white))
    scene.include("tea_setting_%d" % i, setting)

plant = Asset("Flower pot")
px, py = .73, -1.06
plant.include("pot_body", rod(.20, length=.32, center=(px, py, 1.03), color=(.09, .105, .085)))
plant.include("pot_rim", rod(.215, length=.045, center=(px, py, 1.21), color=(.12, .14, .11)))
plant.include("soil", rod(.18, length=.012, center=(px, py, 1.238), color=(.08, .07, .055)))
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
    for j, f in enumerate((.38, .55, .72)):
        qx, qy, qz = px+dx*f, py+dy*f, 1.23+dz*f
        leaf = ball(.045, center=(qx + (-1 if (i+j)%2 else 1)*.035, qy, qz),
                    color=(.25,.36,.15))
        leaf.resize((1.6, .45, .48))
        plant.include("leaf_%02d_%d" % (i,j), leaf)
    if i < 9:
        for j in range(5):
            a = j * 2 * math.pi / 5
            plant.include("flower_%02d_%d" % (i,j),
                          ball(.035, center=(end[0]+.045*math.cos(a),
                                            end[1]+.035*math.sin(a),
                                            end[2]+.025*(j%2)),
                               color=flower if j%2 else (.64,.65,.72)))
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
background.inputs["Strength"].default_value = .42

set_view((0.0, -7.6, 2.05), (0.0, -.05, 1.18), lens=43)
area_emitter((-3.8, -4.0, 5.2), power=750, size=4.5, target=(0, 0, .8))
area_emitter((3.0, -1.5, 3.6), power=160, size=3, target=(0, 0, 1))
