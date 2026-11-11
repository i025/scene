# Reference inventory, normalized image bounds (approximate):
# - Narrow room, floor and exposed walls: entire image; rear wall at y ~= .08-.66.
# - White double-hung window: (.63,.09)-(.91,.43), dark exterior visible.
# - Exposed left wall studs, lath, wiring and electrical box:
#   (0,.00)-(.47,.91), partly obscured by foreground door trim.
# - Aluminum folding ladder: (.56,.22)-(.99,.80), overlapping window and rear wall.
#   Two sloped side assemblies, rectangular rungs, hinge and red markings.
# - Floor debris and timber strips: (.23,.64)-(1,1), densest at lower right.
# - Bright warm work light: (.30,.00)-(.48,.19), partly blown out.
# - Foreground doorway trim at left and right edges; outside geometry is uncertain.
# Primitive estimate: architecture ~28, wall studs and lath ~65, window ~14,
# ladder ~29, debris ~65, electrical/wires/light ~17: approximately 218 meshes.
# Surface irregularity is suggested through a few shared procedural materials.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Renovation room")

# Shared colors
mortar = (0.34, 0.29, 0.22)
brick = (0.40, 0.32, 0.24)
wood = (0.30, 0.16, 0.085)
wood_light = (0.47, 0.31, 0.17)
lath = (0.43, 0.30, 0.19)
white = (0.83, 0.81, 0.71)
dark = (0.075, 0.066, 0.052)
metal = (0.57, 0.59, 0.57)
rubber = (0.12, 0.12, 0.11)

room = Asset("Room shell")
room.include("floor", box((2.85, 5.6, .12), center=(0, .45, -.07),
                          color=(.48, .43, .35)))
# The window is an opening in four independent rear wall pieces.
room.include("rear_left", box((1.55, .18, 3.2),
                             center=(-.65, 3.12, 1.6), color=brick))
room.include("rear_right", box((.25, .18, 3.2),
                              center=(1.30, 3.12, 1.6), color=brick))
room.include("rear_below_window", box((1.05, .18, 1.04),
                                     center=(.65, 3.12, .52), color=brick))
room.include("rear_above_window", box((1.05, .18, .66),
                                     center=(.65, 3.12, 2.87), color=brick))
room.include("left_masonry", box((.14, 5.45, 3.2),
                                center=(-1.40, .4, 1.6), color=(.32,.25,.18)))
room.include("right_wall", box((.14, 5.45, 3.2),
                              center=(1.40, .4, 1.6), color=(.40,.33,.24)))
scene.include("architecture", room)

# Brick joints are deliberately restrained: the back wall is old and dusty.
rear = Asset("Rear wall visible masonry")
for z in [0.15, .28, .41, .54, .67, .80, .93]:
    rear.include("horizontal_joint_%02d" % int(z*100),
                 box((2.65,.012,.012), center=(0,3.015,z), color=(.25,.22,.17)))
for z in [1.16,1.34,1.52,1.70,1.88,2.06,2.24,2.42,2.60,2.78,2.96,3.14]:
    rear.include("left_joint_%02d" % int(z*100),
                 box((1.48,.012,.009), center=(-.66,3.015,z), color=(.30,.25,.19)))
scene.include("rear_masonry_detail", rear)

window = Asset("White double hung window")
# Dark outside aperture and aged wooden outer casing.
window.include("night_glass", box((.99,.035,1.48), center=(.65,3.105,1.78),
                                   color=(.045,.085,.12)))
for x in (.10,1.20):
    window.include("outer_side_"+str(x), box((.09,.12,1.70), center=(x,2.995,1.77),
                                              color=(.15,.10,.065)))
for z in (.94,2.60):
    window.include("outer_horizontal_"+str(z), box((1.19,.12,.085),
                   center=(.65,2.995,z), color=(.15,.10,.065)))
for x in (.16,1.14):
    window.include("white_side_"+str(x), box((.065,.075,1.48),
                   center=(x,2.945,1.78), color=white))
for z in (1.05,1.77,2.50):
    window.include("white_rail_"+str(z), box((1.03,.075,.075),
                   center=(.65,2.945,z), color=white))
window.include("center_sash_rail", box((1.00,.085,.055),
               center=(.65,2.92,1.67), color=(.68,.67,.60)))
window.include("sill", box((1.18,.20,.07), center=(.65,2.91,1.00),
                           color=(.61,.56,.46)))
# A few faint blue reflections in the glass.
for i in range(5):
    window.include("glass_reflection_%d" % i,
                   box((.035,.008,.055), center=(.40+i*.115,3.075,1.27+(i%2)*.09),
                       color=(.035,.16,.30)))
scene.include("window", window)

# Left-hand exposed construction: old vertical studs, narrow laths and backing.
framing = Asset("Left exposed wood framing")
for i,y in enumerate((-1.93,-1.30,-.63,.08,.77,1.48,2.20,2.88)):
    framing.include("stud_%d" % i, box((.11,.10,3.15),
                    center=(-1.28,y,1.57), color=wood if i%2 else (.37,.21,.11)))
framing.include("top_plate", box((.13,5.05,.11), center=(-1.28,.48,3.12), color=wood))
framing.include("bottom_plate", box((.14,5.05,.13), center=(-1.28,.48,.09), color=wood))
# Closely spaced lath survives in selected wall bays.
for j in range(23):
    z=.34+j*.105
    framing.include("lath_front_%02d" % j,
        box((.035,.58,.052), center=(-1.205,-.96,z), color=lath))
    if j < 19:
        framing.include("lath_rear_%02d" % j,
            box((.035,.57,.047), center=(-1.205,.43,z+.03), color=(.36,.25,.16)))
scene.include("exposed_framing", framing)

# Foreground jambs, very close to the camera.
doorway = Asset("Doorway foreground")
doorway.include("left_jamb", box((.16,.20,3.4), center=(-1.43,-2.08,1.65),
                                  color=(.61,.49,.26)))
doorway.include("left_inner_trim", box((.045,.22,3.4), center=(-1.315,-2.07,1.65),
                                       color=(.24,.15,.075)))
doorway.include("right_jamb", box((.12,.18,3.4), center=(1.42,-2.08,1.65),
                                   color=(.59,.49,.30)))
scene.include("doorway", doorway)

electrical = Asset("Electrical box and surface cables")
electrical.include("box", box((.25,.18,.55), center=(-1.14,-1.25,1.55),
                               color=(.79,.79,.72)))
electrical.include("box_side", box((.035,.20,.55), center=(-1.00,-1.25,1.55),
                                    color=(.58,.58,.53)))
electrical.include("box_top_cap", box((.20,.18,.045), center=(-1.13,-1.25,1.85),
                                      color=(.37,.14,.12)))
electrical.include("conduit_down", rod(.018, start=(-1.11,-1.25,1.27),
                                       end=(-1.11,-1.25,.17), color=(.40,.40,.36)))
electrical.include("wire_1", sweep_tube(points=[(-1.18,.76,.17),(-1.17,.80,1.10),
                   (-1.18,.75,1.91),(-1.16,.65,2.60)], radius=.012, color=(.10,.11,.12)))
electrical.include("wire_2", sweep_tube(points=[(-1.16,.84,.12),(-1.15,.91,.96),
                   (-1.15,.88,1.75),(-1.18,.82,2.50)], radius=.009, color=(.36,.39,.38)))
scene.include("electrical", electrical)

# A-frame ladder; each pair of rails and the open triangular side remains editable.
ladder = Asset("Aluminum folding ladder")
front_bottom_y = -.15
top_y = 1.80
back_bottom_y = 2.65
bottom_z = .06
top_z = 2.55
# Ladder is slightly to the right of room center and roughly faces the camera.
for side, x in enumerate((.33,.88)):
    ladder.include("front_rail_%d" % side,
        rod(.045, start=(x,front_bottom_y,bottom_z), end=(x,top_y,top_z), color=metal))
    ladder.include("rear_rail_%d" % side,
        rod(.039, start=(x,back_bottom_y,bottom_z), end=(x,top_y,top_z), color=(.49,.51,.50)))
    ladder.include("front_foot_%d" % side,
        box((.12,.20,.07), center=(x,front_bottom_y,.055), color=rubber))
    ladder.include("rear_foot_%d" % side,
        box((.12,.17,.07), center=(x,back_bottom_y,.055), color=rubber))
    ladder.include("hinge_%d" % side,
        ball(.075, center=(x,top_y,top_z), color=(.40,.42,.40)))
for j in range(8):
    t=.13+j*.105
    yy=front_bottom_y+(top_y-front_bottom_y)*t
    zz=bottom_z+(top_z-bottom_z)*t
    ladder.include("front_step_%d" % j,
        box((.56,.105,.045), center=(.605,yy-.025,zz), color=(.67,.68,.64)))
for j in range(4):
    t=.20+j*.18
    yy=back_bottom_y+(top_y-back_bottom_y)*t
    zz=bottom_z+(top_z-bottom_z)*t
    ladder.include("rear_brace_%d" % j,
        rod(.016,start=(.33,yy,zz),end=(.88,yy,zz), color=(.42,.44,.43)))
# Red warning stripe on one rail.
ladder.include("red_label",
    rod(.049, start=(.33,.25,.57), end=(.33,.86,1.35), color=(.69,.12,.07)))
ladder.include("top_cap", box((.66,.17,.08), center=(.605,1.80,2.56),
                              color=(.38,.39,.37)))
scene.include("folding_ladder", ladder)

debris = Asset("Floor debris and loose timber")
# A scattered pile of narrow lath strips, with varied orientation.
for i in range(39):
    x=random.uniform(-.20,1.28)
    y=random.uniform(-1.85,-.30)
    length=random.uniform(.35,1.30)
    width=random.uniform(.025,.065)
    piece=box((length,width,random.uniform(.018,.035)),
              center=(x,y,.025+(i%4)*.015),
              color=random.choice([wood_light,wood,lath,(.55,.39,.23)]))
    piece.turn("+z", random.uniform(-75,75))
    debris.include("broken_lath_%02d" % i,piece)
# A few longer boards along the base of the back wall.
for i in range(5):
    debris.include("stacked_board_%d" % i,
        box((1.18,.11,.045),center=(.67,2.75,.055+i*.055),
            color=(.42+i*.015,.27+i*.01,.14)))
for i in range(22):
    x=random.uniform(-1.15,1.18)
    y=random.uniform(-1.9,2.5)
    debris.include("plaster_fragment_%02d" % i,
        box((random.uniform(.06,.16),random.uniform(.04,.12),.025),
            center=(x,y,.017),color=random.choice([(.62,.57,.46),(.49,.43,.34),(.69,.64,.53)])))
scene.include("construction_debris", debris)

lamp = Asset("Warm temporary work lamp")
lamp.include("bulb", ball(.105, center=(-1.08,.14,2.80), color=(1.0,.86,.55)))
lamp.include("socket", box((.09,.10,.13), center=(-1.10,.14,2.94), color=(.30,.25,.18)))
scene.include("work_light", lamp)

realize(scene)

# Apply shared procedural surface variation after realization.
def noise_material(name, c1, c2, scale, roughness=0.9, bump_strength=.18):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*c1,1)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nodes.get("Principled BSDF")
    bs.inputs["Roughness"].default_value=roughness
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=3
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(*c1,1)
    ramp.color_ramp.elements[1].color=(*c2,1)
    links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=bump_strength
    bump.inputs["Distance"].default_value=.065
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return mat

wallmat=noise_material("Dusty rough masonry",(.20,.16,.12),(.47,.39,.29),7,.96,.27)
floormat=noise_material("Dust and plaster floor",(.30,.27,.22),(.62,.57,.46),45,.95,.22)
woodmat=noise_material("Aged exposed wood",(.19,.10,.045),(.48,.31,.16),5,.88,.12)

for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    n=ob.name.lower()
    if any(s in n for s in ("rear_left","rear_right","rear_below","rear_above",
                             "left_masonry","right_wall")):
        ob.data.materials.clear()
        ob.data.materials.append(wallmat)
    elif "floor" in n and "fragment" not in n:
        ob.data.materials.clear()
        ob.data.materials.append(floormat)
    elif "stud_" in n or "plate" in n or "lath_" in n:
        ob.data.materials.clear()
        ob.data.materials.append(woodmat)

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
background.inputs["Color"].default_value=(.15,.17,.19,1)
background.inputs["Strength"].default_value=.35

set_view((0,-5.4,2.05), (0,1.05,1.52), lens=27, sensor=36)
area_emitter((-1.0,-.15,2.77), power=260, size=.45,
             target=(0,1.3,1.2), color=(1.0,.72,.39))
area_emitter((0,-3.1,3.4), power=350, size=3.5,
             target=(0,1.2,1.0), color=(1.0,.87,.71))
area_emitter((.8,2.80,2.0), power=65, size=1.0,
             target=(0,.5,1.2), color=(.50,.64,1.0))

# The fixed runner owns image dimensions, rendering, and saving.
