# Reference inventory, approximate normalized image bounds:
# Room enclosure fills frame; rear wall occupies x=.45-1, with its floor junction
# around y=.65. Left doorway and exposed studs occupy x=0-.47.
# White double-hung window occupies x=.62-.92, y=.09-.43. The exterior is dark.
# Aluminum folding ladder occupies x=.56-1, y=.23-.80, overlapping the window.
# Electrical box occupies x=.15-.25, y=.36-.51; cables extend down the left wall.
# Warm work light blooms near x=.37, y=.10. Loose lath and rubble cover the floor,
# especially x=.35-1, y=.72-1. Stacked boards sit along the rear wall.
# Geometry behind the window, ladder, and foreground doorway is uncertain.
#
# Feedback comparison: the previous camera showed the outside of the room and
# made the rear window too small and central. It also made the ladder read as a
# narrow frontal ladder. This revision moves the camera into the doorway, frames
# the room more tightly, and turns the ladder to show its diagonal side profile.
# Primitive estimate: room and window 27, left framing and lath 60, ladder 34,
# electrical and lamp 18, debris 95, masonry joints 18: about 252 meshes.

from sceneact import *
import bpy
import math
import random

random.seed(41)
scene = Scene("Room under renovation")

brick = (0.33, 0.28, 0.21)
mortar = (0.24, 0.21, 0.17)
wood = (0.27, 0.14, 0.075)
wood2 = (0.40, 0.25, 0.14)
lath = (0.42, 0.30, 0.19)
dust = (0.48, 0.44, 0.36)
white = (0.79, 0.78, 0.70)
dark = (0.095, 0.075, 0.055)
metal = (0.55, 0.58, 0.56)
metal_dark = (0.30, 0.33, 0.32)

# Room shell. The four back wall pieces leave the window opening intact.
room = Asset("Enclosing walls and floor")
room.include("floor", box((3.0, 6.0, .12), center=(0,.35,-.07),
                          color=dust))
room.include("back left", box((1.55,.17,3.5), center=(-.725,3.10,1.75),
                              color=brick))
room.include("back right", box((.25,.17,3.5), center=(1.375,3.10,1.75),
                               color=brick))
room.include("back below window", box((1.20,.17,1.00),
                                      center=(.65,3.10,.50), color=brick))
room.include("back above window", box((1.20,.17,.86),
                                      center=(.65,3.10,3.07), color=brick))
room.include("left masonry", box((.15,5.6,3.5), center=(-1.50,.35,1.75),
                                 color=(.24,.19,.14)))
room.include("right wall", box((.15,5.6,3.5), center=(1.50,.35,1.75),
                               color=(.33,.28,.21)))
scene.include("room", room)

# Back wall is rough with horizontally layered exposed masonry and lath.
rear = Asset("Rear masonry and lower exposed courses")
for i in range(15):
    z = .10 + i*.067
    rear.include("lower course %02d" % i,
                 box((2.94,.015,.018), center=(0,3.005,z),
                     color=(.23,.19,.14) if i % 3 else (.42,.33,.22)))
for i in range(8):
    z=1.1+i*.29
    rear.include("left irregular joint %02d" % i,
                 box((1.42,.012,.012),center=(-.76,3.003,z),
                     color=(.26,.22,.17)))
rear.include("dark horizontal wall seam",
             box((.65,.025,.04),center=(-.86,2.99,1.75),color=dark))
scene.include("rear wall detail", rear)

window = Asset("White double hung window")
window.include("dark exterior", box((1.13,.035,1.60),
                                    center=(.65,3.105,1.80),
                                    color=(.035,.065,.09)))
for x in (.04,1.26):
    window.include("dark side casing %s" % x,
                   box((.085,.13,1.78),center=(x,2.985,1.80),color=dark))
for z in (.92,2.68):
    window.include("dark horizontal casing %s" % z,
                   box((1.31,.13,.085),center=(.65,2.985,z),color=dark))
for x in (.11,1.19):
    window.include("white side frame %s" % x,
                   box((.075,.08,1.61),center=(x,2.91,1.80),color=white))
for z in (1.04,1.79,2.57):
    window.include("white sash rail %s" % z,
                   box((1.12,.085,.075),center=(.65,2.91,z),color=white))
window.include("sill",box((1.28,.22,.08),center=(.65,2.91,.99),
                          color=(.62,.59,.49)))
window.include("lower sash dark bar",
               box((1.02,.04,.025),center=(.65,2.90,1.69),
                   color=(.25,.25,.23)))
for i in range(9):
    window.include("distant blue reflection %d" % i,
        box((.035,.01,.035),center=(.25+i*.09,3.075,1.26+(i%3)*.045),
            color=(.03,.12,.25)))
scene.include("window", window)

framing = Asset("Left wall timber studs and remaining lath")
for i,y in enumerate((-2.25,-1.65,-1.02,-.38,.30,.98,1.65,2.33,2.92)):
    framing.include("stud %02d" % i,
        box((.12,.11,3.45),center=(-1.39,y,1.72),
            color=wood if i%2 else wood2))
framing.include("bottom plate",box((.14,5.25,.14),
                                   center=(-1.36,.30,.08),color=wood))
framing.include("top plate",box((.15,5.25,.13),
                                center=(-1.36,.30,3.37),color=wood))
for i in range(26):
    z=.24+i*.105
    framing.include("front lath %02d" % i,
        box((.03,.53,.047),center=(-1.30,-1.33,z),color=lath))
    if i < 22:
        framing.include("middle lath %02d" % i,
            box((.03,.56,.045),center=(-1.30,.64,z+.03),
                color=(.33,.22,.13)))
scene.include("exposed framing",framing)

jamb = Asset("Foreground door jamb")
jamb.include("left painted jamb",
             box((.16,.18,3.6),center=(-1.45,-2.36,1.75),
                 color=(.57,.46,.24)))
jamb.include("left dark inner edge",
             box((.05,.20,3.6),center=(-1.34,-2.35,1.75),
                 color=(.21,.13,.07)))
jamb.include("right painted jamb",
             box((.10,.18,3.6),center=(1.46,-2.36,1.75),
                 color=(.54,.45,.28)))
scene.include("doorway",jamb)

electric = Asset("Electrical box and loose cables")
electric.include("white box",box((.24,.21,.55),
                                  center=(-1.24,-1.75,1.63),
                                  color=(.78,.78,.72)))
electric.include("box side",box((.035,.22,.55),
                                 center=(-1.105,-1.75,1.63),
                                 color=(.56,.56,.52)))
electric.include("red upper cap",box((.21,.20,.035),
                                     center=(-1.24,-1.75,1.92),
                                     color=(.36,.14,.12)))
electric.include("down conduit",
                 rod(.018,start=(-1.20,-1.75,1.35),
                     end=(-1.20,-1.75,.12),color=(.42,.42,.38)))
for i in range(3):
    y=.23+i*.10
    electric.include("hanging cable %d" % i,
        sweep_tube(points=[(-1.27,y,2.78),(-1.26,y+.04,1.9),
                           (-1.25,y+.08,.83),(-1.20,y+.13,.14)],
                   radius=.009+i*.002,
                   color=(.11,.12,.12) if i!=1 else (.38,.39,.36)))
scene.include("electrical",electric)

# A-frame folding ladder viewed from the side. Its near rail rises strongly
# toward image right; the other leg slopes down to the right from the hinge.
ladder = Asset("Aluminum folding ladder")
# Rails lie mainly along X so the characteristic triangular profile is visible.
front_foot=(-.02,.55,.08)
hinge=(1.03,1.28,2.54)
back_foot=(1.48,1.86,.08)
for j,dy in enumerate((-.15,.15)):
    ladder.include("front side rail %d" % j,
        rod(.045,start=(front_foot[0],front_foot[1]+dy,front_foot[2]),
            end=(hinge[0],hinge[1]+dy,hinge[2]),color=metal))
    ladder.include("rear side rail %d" % j,
        rod(.043,start=(back_foot[0],back_foot[1]+dy,back_foot[2]),
            end=(hinge[0],hinge[1]+dy,hinge[2]),color=(.48,.50,.48)))
    ladder.include("front rubber foot %d" % j,
        box((.15,.13,.075),center=(front_foot[0],front_foot[1]+dy,.055),
            color=(.13,.13,.12)))
    ladder.include("rear rubber foot %d" % j,
        box((.15,.13,.075),center=(back_foot[0],back_foot[1]+dy,.055),
            color=(.13,.13,.12)))
    ladder.include("hinge %d" % j,
        ball(.075,center=(hinge[0],hinge[1]+dy,hinge[2]),
             color=metal_dark))
for i in range(7):
    t=.14+i*.115
    x=front_foot[0]+(hinge[0]-front_foot[0])*t
    y=front_foot[1]+(hinge[1]-front_foot[1])*t
    z=front_foot[2]+(hinge[2]-front_foot[2])*t
    ladder.include("front step %d" % i,
        box((.16,.38,.045),center=(x,y,z),color=(.66,.67,.63)))
for i in range(4):
    t=.2+i*.19
    x=back_foot[0]+(hinge[0]-back_foot[0])*t
    y=back_foot[1]+(hinge[1]-back_foot[1])*t
    z=back_foot[2]+(hinge[2]-back_foot[2])*t
    ladder.include("back rung %d" % i,
        rod(.018,start=(x,y-.17,z),end=(x,y+.17,z),color=metal_dark))
ladder.include("red warning strip",
    rod(.047,start=(.18,.54,.55),end=(.49,.75,1.29),
        color=(.61,.10,.06)))
ladder.include("hinge top",box((.17,.43,.08),center=(1.03,1.28,2.55),
                               color=(.40,.42,.40)))
scene.include("folding ladder",ladder)

debris=Asset("Loose wooden lath and broken plaster")
for i in range(55):
    x=random.uniform(-.25,1.38)
    y=random.uniform(-2.20,.15)
    length=random.uniform(.28,1.25)
    piece=box((length,random.uniform(.025,.065),random.uniform(.018,.035)),
              center=(x,y,.025+(i%5)*.012),
              color=random.choice([wood,wood2,lath,(.52,.37,.22)]))
    piece.turn("+z",random.uniform(-85,85))
    debris.include("broken lath %02d" % i,piece)
for i in range(32):
    x=random.uniform(-1.20,1.36)
    y=random.uniform(-2.2,2.5)
    p=box((random.uniform(.05,.15),random.uniform(.04,.12),.025),
          center=(x,y,.018),
          color=random.choice([(.63,.59,.49),(.39,.35,.28),(.54,.49,.40)]))
    p.turn("+z",random.uniform(0,180))
    debris.include("plaster and brick fragment %02d" % i,p)
for i in range(6):
    debris.include("stacked back board %d" % i,
        box((1.22,.11,.045),center=(.71,2.84,.06+i*.055),
            color=(.38+i*.012,.24+i*.008,.13)))
scene.include("floor debris",debris)

lamp=Asset("Temporary work light")
lamp.include("glowing bulb",ball(.12,center=(-1.20,-.62,2.91),
                                 color=(1,.92,.72)))
lamp.include("socket",box((.09,.10,.16),center=(-1.23,-.62,3.06),
                          color=(.31,.25,.18)))
scene.include("work light",lamp)

realize(scene)

# Shared procedural finishes retain distinctions between brick, dusty floor,
# aged wood and metal without relying on image textures.
def textured(name, low, high, scale, bump_strength):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*low,1)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value=.92
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=scale
    noise.inputs["Detail"].default_value=3
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(*low,1)
    ramp.color_ramp.elements[1].color=(*high,1)
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=bump_strength
    bump.inputs["Distance"].default_value=.035
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return mat

# SceneAct creates generic primitive names, so color and geometry above remain
# the reliable material assignment; the shared materials are available for
# subsequent editing of the corresponding surfaces.
textured("Rough aged masonry",(.21,.17,.13),(.42,.34,.25),9,.22)
textured("Dust and small plaster",(.30,.27,.22),(.62,.57,.46),42,.18)
textured("Aged timber",(.18,.09,.04),(.46,.29,.14),7,.12)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.12,.13,.14,1)
background.inputs["Strength"].default_value=.18

set_view((-.15,-3.30,2.05),(.25,2.3,1.55),lens=34,sensor=36)
area_emitter((-1.14,-.65,2.88),power=270,size=.30,
             target=(0,1.0,1.3),color=(1.0,.69,.38))
area_emitter((-.3,-2.7,3.1),power=200,size=2.5,
             target=(0,1.1,1.2),color=(1.0,.83,.62))
area_emitter((.8,2.8,2.0),power=30,size=.8,
             target=(0,.8,1.2),color=(.45,.57,1.0))
