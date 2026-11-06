# Reference inventory, normalized image coordinates (approximate):
# - Pale wall, x 0-.82, y 0-.74; mostly blank, behind all furniture.
# - Dark gray curtain, x .81-.99, y 0-.43; vertical folds, gathered near middle.
# - Mustard sofa, x .02-.97, y .28-.94: broad upholstered base, two seat
#   cushions, three back sections, thick arms, and a loose pillow at left.
#   Lower surfaces are partly hidden by the foreground table.
# - Dark rectangular coffee table, x .32-1.0, y .56-1.0: top, apron and
#   visible legs; its right and lower edges extend beyond the image.
# - Two white cups and saucers on thin rectangular napkins or magazines,
#   x .40-.59 and .65-.87, y .54-.69.
# - Small dark plant pot and branching green stems with pale blue-purple
#   flower clusters, x .55-.73, y .33-.65, overlapping the sofa.
# - Gray rug and a narrow strip of darker floor at the bottom.
# Occluded sofa backs, table legs, and curtain structure are approximate.
#
# Primitive estimate: architecture 6; sofa about 13 boxes/balls; table 7;
# cups and settings about 18; plant pot, stems, leaves and flowers about 85.
# Total approximately 130 primitives, with no fillet boxes or Boolean operations.

from sceneact import *
import bpy
import math
import random

random.seed(11)
scene = Scene("Living room")

wall = (0.78, 0.77, 0.75)
floor = (0.23, 0.21, 0.20)
rug = (0.36, 0.35, 0.34)
sofa = (0.64, 0.35, 0.13)
sofa_light = (0.74, 0.44, 0.19)
sofa_back = (0.76, 0.47, 0.23)
sofa_shadow = (0.52, 0.27, 0.10)
table_color = (0.075, 0.055, 0.044)
white = (0.88, 0.88, 0.84)
green = (0.25, 0.35, 0.16)
flower = (0.56, 0.60, 0.69)

architecture = Asset("Architecture")
architecture.include("back_wall", box((9, .12, 4.5), center=(0, .95, 2.2), color=wall))
architecture.include("floor", box((9, 8, .10), center=(0, -1.5, -.07), color=floor))
architecture.include("rug", box((6.5, 3.0, .025), center=(0, -1.65, .005), color=rug))
scene.include("architecture", architecture)

# Curtain is a set of broad, slightly irregular fabric folds.
curtain = Asset("Curtain")
curtain.include("dark_backing", box((.77, .12, 2.95), center=(2.15, .79, 1.95), color=(.16, .16, .17)))
for i in range(6):
    x = 1.82 + i * .13
    c = [(0.22, .22, .23), (.32, .32, .33), (.18, .18, .19)][i % 3]
    curtain.include("fold_%02d" % i, box((.10, .07, 2.95), center=(x, .69 - .025 * (i % 2), 1.95), color=c))
scene.include("curtain", curtain)

couch = Asset("Mustard sofa")
couch.include("lower_base", box((4.30, .88, .52), center=(0, .13, .35), color=sofa))
couch.include("front_lower_panel", box((3.50, .06, .44), center=(0, -.34, .36), color=sofa_light))
couch.include("seat_deck", box((3.60, .90, .20), center=(0, -.03, .68), color=sofa_shadow))
couch.include("left_arm", box((.58, 1.02, 1.20), center=(-1.88, -.04, .62), color=sofa))
couch.include("right_arm", box((.57, 1.02, 1.22), center=(1.88, -.04, .63), color=sofa_light))
for i, x in enumerate((-.89, .89)):
    couch.include("seat_cushion_%d" % i,
                  fillet_box((1.72, .83, .31), radius=.10,
                             center=(x, -.10, .83), color=sofa_light))
for i, x in enumerate((-1.13, 0, 1.13)):
    couch.include("back_cushion_%d" % i,
                  fillet_box((1.10, .30, .83), radius=.07,
                             center=(x, .43, 1.30), color=sofa_back))
pillow = fillet_box((.75, .19, .62), radius=.06,
                    center=(-1.38, .13, 1.27), color=(.86, .57, .28))
pillow.turn(axis="+y", degrees=-14)
couch.include("loose_pillow", pillow)
scene.include("sofa", couch)

# Coffee table stands between camera and sofa.
coffee = Asset("Coffee table")
coffee.include("top", box((3.45, 1.27, .12), center=(.60, -1.28, .79), color=table_color))
coffee.include("front_apron", box((3.24, .07, .20), center=(.60, -1.87, .65), color=(.055, .040, .032)))
coffee.include("back_apron", box((3.24, .07, .16), center=(.60, -.69, .67), color=table_color))
for ix, x in enumerate((-.96, 2.16)):
    for iy, y in enumerate((-.1, -1.81)):
        # Back legs are mostly concealed by the sofa and tabletop.
        yy = -.72 if iy == 0 else y
        coffee.include("leg_%d_%d" % (ix, iy),
                       box((.13, .13, .72), center=(x, yy, .36), color=(.055, .042, .035)))
scene.include("coffee_table", coffee)

# Place settings: flat rectangular papers, circular saucers and ceramic cups.
for i, (x, y) in enumerate(((-.18, -1.28), (1.12, -1.19))):
    setting = Asset("Tea setting %d" % (i + 1))
    paper = box((.76, .48, .014), center=(x, y, .861), color=(.69, .73, .71))
    paper.turn(axis="+z", degrees=(-7 if i == 0 else 5))
    setting.include("paper", paper)
    paper2 = box((.65, .40, .012), center=(x+.025, y+.01, .872), color=(.86, .85, .81))
    paper2.turn(axis="+z", degrees=(4 if i == 0 else -4))
    setting.include("napkin", paper2)
    setting.include("saucer", rod(.245, length=.025, center=(x, y, .891), color=white))
    setting.include("cup_body", rod(.145, length=.25, center=(x, y, 1.025), color=white))
    setting.include("cup_rim", rod(.158, length=.022, center=(x, y, 1.157), color=(.95,.95,.92)))
    setting.include("tea_surface", rod(.125, length=.006, center=(x, y, 1.171), color=(.43,.34,.25)))
    # Open C-shaped handle, built from three short segments.
    hx = x - .16
    setting.include("handle_top", rod(.020, start=(hx, y, 1.10), end=(hx-.095, y, 1.11), color=white))
    setting.include("handle_side", rod(.020, start=(hx-.095, y, 1.11), end=(hx-.085, y, .99), color=white))
    setting.include("handle_bottom", rod(.020, start=(hx-.085, y, .99), end=(hx, y, .98), color=white))
    scene.include("tea_setting_%d" % i, setting)

plant = Asset("Flower pot")
plant.include("pot_body", rod(.20, length=.32, center=(.49, -.96, 1.03), color=(.12, .14, .12)))
plant.include("pot_rim", rod(.215, length=.045, center=(.49, -.96, 1.21), color=(.16, .18, .15)))
plant.include("soil", rod(.18, length=.012, center=(.49, -.96, 1.238), color=(.10, .09, .07)))

# Branches fan out visibly above the pot; small flower heads remain distinct.
tips = [
    (-.31, -.02, .51), (-.23, .03, .65), (-.13, -.06, .43),
    (-.05, .02, .77), (.06, -.05, .60), (.18, .04, .66),
    (.29, -.03, .50), (.34, .03, .36), (-.34, .07, .32),
    (.11, .09, .43), (-.12, .10, .52)
]
for i, (dx, dy, dz) in enumerate(tips):
    base = (.49, -.96, 1.23)
    end = (.49 + dx, -.96 + dy, 1.23 + dz)
    plant.include("stem_%02d" % i, rod(.009, start=base, end=end, color=green))
    for j, f in enumerate((.43, .65)):
        px = base[0] + dx*f
        py = base[1] + dy*f
        pz = base[2] + dz*f
        leaf = ball(.045, center=(px + (-1 if (i+j)%2 else 1)*.035, py, pz), color=(.30,.40,.20))
        leaf.resize((1.5, .45, .48))
        plant.include("leaf_%02d_%d" % (i,j), leaf)
    if i < 9:
        for j in range(5):
            a = j * 2 * math.pi / 5
            px = end[0] + .045 * math.cos(a)
            py = end[1] + .035 * math.sin(a)
            pz = end[2] + .025 * (j % 2)
            plant.include("flower_%02d_%d" % (i,j),
                          ball(.035, center=(px, py, pz), color=flower if j % 2 else (.68,.69,.76)))
scene.include("flower_pot", plant)

realize(scene)

# Soft daylight enters from camera left, producing the gentle wall gradient
# and shadows under the furniture.
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
background.inputs["Color"].default_value = (0.72, 0.72, 0.70, 1)
background.inputs["Strength"].default_value = .65

set_view((0.0, -7.6, 2.60), (0.0, -.05, 1.10), lens=43)
area_emitter((-3.8, -4.0, 5.2), power=850, size=4.5, target=(0, 0, .8))
area_emitter((3.0, -1.5, 3.6), power=260, size=3, target=(0, 0, 1))
