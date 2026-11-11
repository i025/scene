# Reference inventory, approximate normalized image bounds:
# Room enclosure fills the photograph. The back wall begins near x=.46 and
# meets the dusty floor near y=.65. Foreground jambs are at both image edges.
# Exposed studs, surviving horizontal lath, cables and a white electrical box
# occupy x=.10-.47. The work light blooms near (.38,.10).
# White double-hung window: x=.62-.92, y=.09-.43; dark blue exterior.
# Folding aluminum ladder: x=.56-1, y=.22-.80, overlapping the window.
# Broken timber and plaster cover the floor, densest at lower right; several
# boards are stacked against the back wall. Hidden construction is uncertain.
#
# Review of the second render: the rear wall and window are too far left and
# low, the open top shows a dark background, the electrical box and work light
# are outside the frame, and the surfaces look too uniformly pale. This build
# shifts the view left and downward, extends the walls upward, makes the left
# foreground details visible, and assigns rough materials to actual meshes.
# The ladder is moved right, given wider rectangular rails, and kept side-on.
# Estimated expanded primitives: architecture 10, window 23, framing 65,
# electrical and lamp 24, ladder 30, rear wall courses 26, debris 100:
# approximately 278 meshes. No booleans or fillets.

from sceneact import *
import bpy
import random
import math

random.seed(41)
scene = Scene("Room under renovation")

brick = (.30, .25, .18)
wood = (.25, .12, .055)
wood2 = (.38, .22, .11)
lath = (.40, .27, .15)
white = (.78, .77, .68)
dark = (.085, .065, .045)
metal = (.48, .51, .50)
dust = (.39, .35, .28)

room = Asset("Enclosing walls and floor")
room.include("floor", box((3.0, 6.4, .12), center=(0, .20, -.07), color=dust))
room.include("back left", box((1.55, .17, 5.2), center=(-.725, 3.10, 2.60), color=brick))
room.include("back right", box((.25, .17, 5.2), center=(1.375, 3.10, 2.60), color=brick))
room.include("back below window", box((1.20, .17, 1.00), center=(.65, 3.10, .50), color=brick))
room.include("back above window", box((1.20, .17, 2.56), center=(.65, 3.10, 3.92), color=brick))
room.include("left masonry", box((.15, 6.0, 5.2), center=(-1.50, .10, 2.60), color=(.22,.17,.12)))
room.include("right wall", box((.15, 6.0, 5.2), center=(1.50, .10, 2.60), color=(.28,.23,.17)))
scene.include("room", room)

rear = Asset("Rear masonry and lower courses")
for i in range(15):
    z = .10 + i * .067
    rear.include("lower course %02d" % i,
                 box((2.94,.018,.016), center=(0,3.005,z),
                     color=(.22,.17,.12) if i % 3 else (.39,.29,.18)))
for i in range(9):
    z = 1.10 + i * .28
    rear.include("left joint %02d" % i,
                 box((1.42,.012,.009), center=(-.76,3.003,z), color=(.25,.20,.14)))
rear.include("wall seam", box((.65,.025,.04), center=(-.86,2.99,1.75), color=dark))
scene.include("rear wall detail", rear)

window = Asset("White double hung window")
window.include("dark exterior", box((1.13,.035,1.60), center=(.65,3.105,1.80),
                                   color=(.025,.055,.075)))
for x in (.04, 1.26):
    window.include("dark side casing %s" % x,
                   box((.085,.13,1.78), center=(x,2.985,1.80), color=dark))
for z in (.92, 2.68):
    window.include("dark horizontal casing %s" % z,
                   box((1.31,.13,.085), center=(.65,2.985,z), color=dark))
for x in (.11, 1.19):
    window.include("white side frame %s" % x,
                   box((.075,.08,1.61), center=(x,2.91,1.80), color=white))
for z in (1.04, 1.79, 2.57):
    window.include("white sash rail %s" % z,
                   box((1.12,.085,.075), center=(.65,2.91,z), color=white))
window.include("sill", box((1.28,.22,.08), center=(.65,2.91,.99),
                           color=(.58,.54,.43)))
window.include("lower sash rail", box((1.02,.04,.026), center=(.65,2.90,1.69),
                                      color=(.24,.24,.21)))
for i in range(9):
    window.include("blue exterior reflection %d" % i,
                   box((.035,.01,.035),
                       center=(.25+i*.09,3.075,1.26+(i%3)*.045),
                       color=(.025,.10,.23)))
scene.include("window", window)

framing = Asset("Left wall exposed studs and lath")
for i,y in enumerate((-2.65,-2.05,-1.42,-.79,-.14,.54,1.22,1.90,2.58)):
    framing.include("stud %02d" % i,
                    box((.12,.11,5.0), center=(-1.39,y,2.5),
                        color=wood if i%2 else wood2))
framing.include("bottom plate", box((.14,5.8,.14), center=(-1.36,.05,.08), color=wood))
framing.include("top framing", box((.14,5.8,.13), center=(-1.36,.05,4.9), color=wood))
for i in range(28):
    z = .20 + i*.105
    framing.include("front lath %02d" % i,
                    box((.03,.53,.046), center=(-1.30,-1.73,z), color=lath))
    if i < 24:
        framing.include("middle lath %02d" % i,
                        box((.03,.56,.044), center=(-1.30,.20,z+.03),
                            color=(.31,.20,.11)))
scene.include("exposed framing", framing)

jamb = Asset("Foreground painted doorway")
jamb.include("left painted jamb", box((.18,.20,5.2), center=(-1.45,-2.86,2.60),
                                      color=(.50,.39,.18)))
jamb.include("left dark inner edge", box((.055,.22,5.2), center=(-1.33,-2.85,2.60),
                                         color=(.17,.10,.045)))
jamb.include("right painted jamb", box((.10,.20,5.2), center=(1.46,-2.86,2.60),
                                       color=(.49,.40,.23)))
scene.include("doorway", jamb)

electric = Asset("Electrical box and loose cables")
electric.include("white box", box((.24,.22,.55), center=(-1.20,-2.15,1.63),
                                  color=(.74,.74,.67)))
electric.include("box side", box((.035,.23,.55), center=(-1.065,-2.15,1.63),
                                 color=(.49,.49,.45)))
electric.include("red upper cap", box((.21,.20,.035), center=(-1.20,-2.15,1.92),
                                      color=(.33,.12,.09)))
electric.include("down conduit", rod(.018, start=(-1.16,-2.15,1.35),
                                     end=(-1.16,-2.15,.12), color=(.35,.35,.31)))
for i in range(3):
    y = -.15 + i*.10
    electric.include("hanging cable %d" % i,
                     sweep_tube(points=[(-1.27,y,2.78),(-1.26,y+.04,1.9),
                                        (-1.25,y+.08,.83),(-1.20,y+.13,.14)],
                                radius=.009+i*.002,
                                color=(.08,.09,.09) if i != 1 else (.31,.32,.29)))
scene.include("electrical", electric)

ladder = Asset("Aluminum folding ladder")
front_foot = (.30,.55,.08)
hinge = (1.20,1.28,2.54)
back_foot = (1.72,1.86,.08)
for j,dy in enumerate((-.18,.18)):
    ladder.include("front side rail %d" % j,
                   rod(.055, start=(front_foot[0],front_foot[1]+dy,front_foot[2]),
                       end=(hinge[0],hinge[1]+dy,hinge[2]), color=metal))
    ladder.include("rear side rail %d" % j,
                   rod(.047, start=(back_foot[0],back_foot[1]+dy,back_foot[2]),
                       end=(hinge[0],hinge[1]+dy,hinge[2]), color=(.40,.43,.42)))
    ladder.include("front foot %d" % j,
                   box((.15,.14,.075), center=(front_foot[0],front_foot[1]+dy,.055),
                       color=(.10,.10,.09)))
    ladder.include("rear foot %d" % j,
                   box((.15,.14,.075), center=(back_foot[0],back_foot[1]+dy,.055),
                       color=(.10,.10,.09)))
    ladder.include("hinge %d" % j,
                   ball(.075, center=(hinge[0],hinge[1]+dy,hinge[2]),
                        color=(.30,.32,.31)))
for i in range(7):
    t = .14+i*.115
    x = front_foot[0]+(hinge[0]-front_foot[0])*t
    y = front_foot[1]+(hinge[1]-front_foot[1])*t
    z = front_foot[2]+(hinge[2]-front_foot[2])*t
    ladder.include("front step %d" % i,
                   box((.16,.44,.045), center=(x,y,z), color=(.61,.63,.60)))
for i in range(4):
    t = .20+i*.19
    x = back_foot[0]+(hinge[0]-back_foot[0])*t
    y = back_foot[1]+(hinge[1]-back_foot[1])*t
    z = back_foot[2]+(hinge[2]-back_foot[2])*t
    ladder.include("back rung %d" % i,
                   rod(.018, start=(x,y-.20,z), end=(x,y+.20,z), color=(.32,.34,.33)))
ladder.include("red warning strip",
               rod(.057, start=(.48,.52,.55), end=(.75,.74,1.29),
                   color=(.56,.07,.035)))
ladder.include("hinge top", box((.17,.49,.08), center=(1.20,1.28,2.55),
                                color=(.36,.38,.37)))
scene.include("folding ladder", ladder)

debris = Asset("Loose lath and construction rubble")
for i in range(58):
    x = random.uniform(-.15,1.38)
    y = random.uniform(-2.55,.15)
    piece = box((random.uniform(.28,1.25),random.uniform(.025,.065),
                 random.uniform(.018,.035)),
                center=(x,y,.025+(i%5)*.012),
                color=random.choice([wood,wood2,lath,(.48,.32,.17)]))
    piece.turn("+z", random.uniform(-85,85))
    debris.include("broken lath %02d" % i, piece)
for i in range(35):
    piece = box((random.uniform(.05,.15),random.uniform(.04,.12),.025),
                center=(random.uniform(-1.20,1.36),random.uniform(-2.5,2.5),.018),
                color=random.choice([(.55,.50,.40),(.32,.28,.21),(.48,.42,.32)]))
    piece.turn("+z", random.uniform(0,180))
    debris.include("plaster fragment %02d" % i, piece)
for i in range(6):
    debris.include("stacked back board %d" % i,
                   box((1.22,.11,.045), center=(.71,2.84,.06+i*.055),
                       color=(.35+i*.012,.21+i*.008,.10)))
scene.include("floor debris", debris)

lamp = Asset("Temporary work light")
lamp.include("bulb", ball(.12, center=(-1.20,-1.35,2.91), color=(1,.92,.72)))
lamp.include("socket", box((.09,.10,.16), center=(-1.23,-1.35,3.06),
                           color=(.29,.22,.14)))
scene.include("work light", lamp)

realize(scene)

# Assign procedural surface variation by matching the colors emitted by
# SceneAct. This keeps materials shared and applies them to actual meshes.
def textured(name, low, high, scale, bump_strength):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*low,1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value = .94
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 3
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*low,1)
    ramp.color_ramp.elements[1].color = (*high,1)
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = .04
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return mat

masonry_mat = textured("Rough aged brick", (.16,.12,.08),(.38,.30,.20), 9, .24)
floor_mat = textured("Dust and plaster floor", (.24,.21,.16),(.53,.48,.38), 55, .24)
wood_mat = textured("Aged exposed timber", (.13,.06,.025),(.38,.22,.10), 7, .16)

def near_color(a,b):
    return sum((a[i]-b[i])**2 for i in range(3)) < .0005

for ob in bpy.context.scene.objects:
    if ob.type != "MESH" or not ob.data.materials:
        continue
    old = ob.data.materials[0]
    col = tuple(old.diffuse_color[:3])
    replacement = None
    if near_color(col,brick) or near_color(col,(.22,.17,.12)) or near_color(col,(.28,.23,.17)):
        replacement = masonry_mat
    elif near_color(col,dust):
        replacement = floor_mat
    elif near_color(col,wood) or near_color(col,wood2) or near_color(col,lath):
        replacement = wood_mat
    if replacement:
        ob.data.materials.clear()
        ob.data.materials.append(replacement)

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
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.10,.11,.12,1)
background.inputs["Strength"].default_value = .15

set_view((-.15,-3.30,2.05),(-.48,2.3,.85),lens=34,sensor=36)
area_emitter((-1.14,-1.35,2.88), power=360, size=.24,
             target=(0,1.0,1.3), color=(1.0,.72,.42))
area_emitter((-.3,-2.7,3.1), power=120, size=2.5,
             target=(0,1.1,1.2), color=(1.0,.82,.61))
area_emitter((.8,2.8,2.0), power=25, size=.8,
             target=(0,.8,1.2), color=(.45,.57,1.0))
