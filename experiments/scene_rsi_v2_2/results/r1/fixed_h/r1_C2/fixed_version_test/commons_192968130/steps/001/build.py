from sceneact import *
import bpy
import math

# Reference inventory (normalized image bounds, approximate):
# Architecture: pale floor (0,.75)-(1,1), white ceiling (0,0)-(.46,.12),
# rear walnut slat wall (0,.11)-(.46,.76), glossy ivory right wall (.57,.28)-(1,1).
# Door: (.31,.29)-(.45,.77), white frame, inset leaf, small silver handle.
# Low bench: (0,.65)-(.20,.81), dark carcass, white drawer, dark recessed top.
# Kitchen: stone worktop (.36,.59)-(1,1), dark sink (.46,.63)-(.62,.72),
# black induction hob (.40,.76)-(.82,1), four thin burner outlines.
# Walnut overhead cabinetry (.46,0)-(1,.44), including end panel, long fronts,
# metallic hood underside and warm undercabinet strip. Rear/near ends are occluded.
# Small wall switches and sockets remain separate named parts.
# Asset coverage maps directly to the named assets below.
# Estimated expanded primitives: architecture 6, slats 45, door 10, bench 7,
# kitchen base/worktop 8 including Boolean operands, sink 12, hob 86,
# overhead cabinetry 13, electrical fixtures 6: approximately 193 meshes.
# The sink interior and cabinet ends outside the photograph remain uncertain.

scene = Scene("Warm narrow kitchen")
WHITE = (.81,.80,.75)
WALL = (.79,.78,.72)
WOOD = (.18,.073,.028)
SLAT = (.32,.145,.061)
DARK = (.017,.019,.017)
STONE = (.59,.55,.45)
METAL = (.35,.36,.33)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
add(architecture, "floor", (8,10,.10), (-.5,0,-.055), (.52,.49,.42))
add(architecture, "rear_wall", (6,.12,3.5), (-1.4,3.08,1.75), (.075,.045,.027))
add(architecture, "right_wall", (.12,9,3.5), (1.56,-.6,1.75), WALL)
add(architecture, "ceiling", (8,9,.12), (-1.6,-.6,2.98), (.86,.85,.80))
add(architecture, "rear_baseboard", (4,.035,.065), (-1.7,2.995,.035), (.7,.66,.57))
scene.include("architecture", architecture)

slats = Asset("Rear walnut slat wall")
slat_pitch = .079
for i in range(45):
    x = -3.20 + i*slat_pitch
    add(slats, "vertical_slat_%02d" % i, (.049,.050,2.67),
        (x,2.979,1.35), SLAT)
scene.include("wood_wall", slats)

door = Asset("White interior door")
door_left, door_right = -.72,.20
door_height = 2.16
add(door, "opening_shadow", (1.01,.055,2.24), (-.26,2.931,1.12), (.17,.15,.12))
add(door, "door_leaf", (.825,.045,2.085), (-.26,2.878,1.047), (.78,.79,.76))
for label,x in [("left",door_left),("right",door_right)]:
    add(door, label+"_jamb", (.058,.074,2.22), (x,2.85,1.11), (.9,.9,.86))
add(door, "top_frame", (.98,.074,.065), (-.26,2.85,2.19), (.9,.9,.86))
add(door, "hinge_side_reveal", (.009,.009,2.05), (.155,2.85,1.06), (.42,.42,.39))
add(door, "handle_backplate", (.029,.015,.11), (-.57,2.84,1.025), METAL)
door.include("handle_spindle", rod(.016,start=(-.57,2.845,1.055),end=(-.57,2.80,1.055),color=METAL))
door.include("lever_handle", rod(.012,start=(-.57,2.80,1.055),end=(-.46,2.80,1.055),color=METAL))
add(door, "keyhole", (.012,.008,.025), (-.57,2.827,.985), (.09,.09,.08))
scene.include("door", door)

bench = Asset("Low black and white bench")
bx = -2.18
add(bench, "dark_case", (1.43,.48,.44), (bx,2.70,.24), (.025,.028,.026))
add(bench, "white_drawer", (1.30,.024,.285), (bx,2.443,.225), (.82,.84,.81))
add(bench, "left_front_edge", (.035,.035,.40), (bx-.695,2.425,.24), DARK)
add(bench, "right_front_edge", (.035,.035,.40), (bx+.695,2.425,.24), DARK)
add(bench, "top_dark_wood", (1.45,.50,.045), (bx,2.69,.473), (.085,.061,.036))
add(bench, "drawer_top_gap", (1.31,.027,.023), (bx,2.426,.389), DARK)
add(bench, "recessed_plinth", (1.30,.39,.045), (bx,2.73,.025), DARK)
scene.include("bench", bench)

base = Asset("Counter and lower cupboards")
add(base, "lower_cupboard_mass", (1.19,6.4,.83), (.91,-.17,.425), (.41,.35,.26))
add(base, "front_face", (.025,6.35,.77), (.304,-.17,.44), (.57,.52,.43))
counter = box((1.24,6.45,.052),center=(.91,-.18,.896),color=STONE)
sink_cut = box((.69,.65,.18),center=(.84,1.78,.895),color=STONE)
base.include("stone_counter_with_sink_opening", subtract(counter,sink_cut))
add(base,"stone_front_edge",(.035,6.45,.055),(.289,-.18,.889),STONE)
add(base,"rear_stone_upstand",(.03,6.4,.045),(1.49,-.17,.94),STONE)
scene.include("counter",base)

sink = Asset("Inset dark sink and drainer")
sx,sy=.84,1.78
add(sink,"basin_bottom",(.65,.61,.025),(sx,sy,.764),(.025,.029,.024))
for label,x in [("left",sx-.335),("right",sx+.335)]:
    add(sink,label+"_basin_wall",(.022,.64,.13),(x,sy,.828),(.055,.058,.045))
for label,y in [("near",sy-.315),("far",sy+.315)]:
    add(sink,label+"_basin_wall",(.69,.022,.13),(sx,y,.828),(.055,.058,.045))
for label,x in [("left",sx-.365),("right",sx+.365)]:
    add(sink,label+"_metal_rim",(.025,.71,.013),(x,sy,.930),(.25,.23,.16))
for label,y in [("near",sy-.345),("far",sy+.345)]:
    add(sink,label+"_metal_rim",(.75,.025,.013),(sx,y,.930),(.25,.23,.16))
add(sink,"ribbed_draining_panel",(.20,.62,.014),(1.28,sy,.931),(.075,.078,.060))
for i in range(6):
    add(sink,"drainer_rib_%d"%i,(.14,.012,.009),(1.28,sy-.25+i*.10,.942),(.28,.26,.19))
scene.include("sink",sink)

hob=Asset("Black glass induction hob")
add(hob,"glass_surface",(.97,1.80,.018),(.865,-.92,.932),(.008,.012,.012))
add(hob,"thin_metal_edge",(.995,1.825,.006),(.865,-.92,.920),(.18,.18,.15))
burners=[(.61,-.30,.205),(1.12,-.33,.183),(.61,-1.18,.205),(1.12,-1.23,.225)]
for j,(x,y,r) in enumerate(burners):
    for k in range(20):
        a=2*math.pi*k/20
        b=2*math.pi*(k+1)/20
        hob.include("burner_%d_arc_%02d"%(j,k),
            rod(.0024,start=(x+r*math.cos(a),y+r*math.sin(a),.944),
                end=(x+r*math.cos(b),y+r*math.sin(b),.944),
                color=(.15,.16,.14)))
for i in range(4):
    add(hob,"touch_control_%d"%i,(.025,.005,.001),(.92+i*.055,-1.65,.944),(.35,.35,.29))
scene.include("hob",hob)

upper = Asset("Overhead walnut cabinetry")
cabinet_front=.36
cabinet_bottom=1.86
add(upper,"cabinet_body",(1.15,6.1,1.53),(.94,-.13,2.635),WOOD)
add(upper,"rear_end_panel",(1.18,.055,1.56),(.925,2.895,2.635),(.155,.064,.026))
# The long wooden front is split by fine vertical seams.
for i in range(5):
    yy=-2.55+i*1.19
    add(upper,"wood_front_%d"%i,(.042,1.176,1.47),(cabinet_front,yy,2.645),WOOD)
add(upper,"front_lower_wood_lip",(.065,6.1,.055),(.343,-.13,1.87),(.095,.038,.013))
add(upper,"underside_wood",(1.10,6.08,.038),(.96,-.13,1.845),(.22,.13,.059))
add(upper,"hood_metal_underside",(.81,1.8,.027),(.94,-.72,1.818),(.43,.44,.41))
add(upper,"hood_filter_one",(.54,.62,.009),(.90,-1.15,1.799),(.27,.29,.27))
add(upper,"hood_filter_two",(.54,.62,.009),(.90,-.36,1.799),(.27,.29,.27))
add(upper,"hood_front_rail",(.04,1.85,.035),(.50,-.72,1.817),(.48,.47,.41))
add(upper,"continuous_warm_light",(.025,6.0,.018),(1.37,-.13,1.816),(1.0,.77,.39))
scene.include("upper_cabinetry",upper)

electrical=Asset("Small wall fixtures")
for label,x,z in [("switch",-.93,1.10),("socket",-.90,.31)]:
    add(electrical,label+"_plate",(.09,.015,.085),(x,2.94,z),(.86,.86,.80))
    add(electrical,label+"_center",(.045,.009,.047),(x,2.928,z),(.69,.70,.66))
add(electrical,"right_wall_socket",(.012,.14,.11),(1.489,1.07,1.15),(.84,.83,.77))
scene.include("electrical",electrical)

realize(scene)

# Shared procedural finishes supply restrained grain and stone veining.
def material_for_color(rgb):
    for mat in bpy.data.materials:
        if mat.use_nodes:
            bs=mat.node_tree.nodes.get("Principled BSDF")
            if bs and max(abs(bs.inputs["Base Color"].default_value[i]-rgb[i]) for i in range(3))<.018:
                yield mat

def procedural(rgb, kind):
    for mat in list(material_for_color(rgb)):
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        tex=nt.nodes.new("ShaderNodeTexCoord")
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        nt.links.new(tex.outputs["Generated"],mapping.inputs[0])
        noise=nt.nodes.new("ShaderNodeTexNoise")
        nt.links.new(mapping.outputs[0],noise.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        if kind=="wood":
            mapping.inputs[1].default_value=(15,1.1,2.0)
            noise.inputs["Scale"].default_value=4
            noise.inputs["Detail"].default_value=2
            ramp.color_ramp.elements[0].color=(rgb[0]*.50,rgb[1]*.43,rgb[2]*.40,1)
            ramp.color_ramp.elements[1].color=(rgb[0]*1.35,rgb[1]*1.34,rgb[2]*1.25,1)
            bs.inputs["Roughness"].default_value=.32
        elif kind=="stone":
            mapping.inputs[1].default_value=(2.0,8.0,2.0)
            noise.inputs["Scale"].default_value=3.5
            noise.inputs["Detail"].default_value=3
            noise.inputs["Roughness"].default_value=.72
            ramp.color_ramp.elements[0].position=.32
            ramp.color_ramp.elements[0].color=(.18,.145,.105,1)
            ramp.color_ramp.elements[1].position=.46
            ramp.color_ramp.elements[1].color=(.73,.69,.58,1)
            bs.inputs["Roughness"].default_value=.32
        else:
            mapping.inputs[1].default_value=(3,12,.4)
            noise.inputs["Scale"].default_value=5
            noise.inputs["Detail"].default_value=2
            ramp.color_ramp.elements[0].color=(.37,.345,.29,1)
            ramp.color_ramp.elements[1].color=(.64,.61,.53,1)
            bs.inputs["Roughness"].default_value=.65
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

procedural(WOOD,"wood")
procedural(SLAT,"wood")
procedural(STONE,"stone")
procedural((.52,.49,.42),"floor")

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    col=bs.inputs["Base Color"].default_value
    if max(col[:3])<.035:
        bs.inputs["Roughness"].default_value=.19
    if abs(col[0]-WALL[0])<.018 and abs(col[1]-WALL[1])<.018:
        bs.inputs["Roughness"].default_value=.16
    if col[0]>.95 and .65<col[1]<.85:
        bs.inputs["Emission Color"].default_value=(1,.65,.25,1)
        bs.inputs["Emission Strength"].default_value=4

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
background.inputs["Color"].default_value=(.78,.80,.82,1)
background.inputs["Strength"].default_value=.35

set_view(position=(1.10,-2.50,1.60),target=(.54,3.0,1.24),lens=29.5,sensor=36)
area_emitter(position=(-2.3,-.5,2.7),power=650,size=3.8,target=(-.4,2.6,.8),color=(1,.91,.78))
area_emitter(position=(-1.8,-3.5,2.2),power=400,size=3.2,target=(.4,1.4,1.2),color=(.90,.94,1))
area_emitter(position=(1.28,1.4,1.76),power=35,size=.6,target=(1.44,1.4,1.2),color=(1,.72,.38))
area_emitter(position=(1.28,-1,1.76),power=45,size=.9,target=(1.45,-1,1.2),color=(1,.79,.48))
sc.view_settings.view_transform='AgX'
