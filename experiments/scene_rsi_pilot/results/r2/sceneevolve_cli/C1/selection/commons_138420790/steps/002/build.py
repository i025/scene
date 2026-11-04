from sceneact import *
import bpy

# The feedback view is blocked by the left wall; move that wall beyond the camera.
# Match the island/post framing with a lower aim and a slightly wider field of view.
# Extend the pale suspended hood upward to match its tall silhouette in the reference.

scene = Scene("Kitchen showroom")
BLACK = (.025,.029,.028)
DARK = (.048,.055,.051)
WOOD = (.47,.29,.145)

def add(parent, name, size, center, color):
    node = box(size=size, center=center, color=color)
    parent.include(name, node)
    return node

architecture = Asset("Architecture")
add(architecture,"floor",(20,18,.12),(0,0,-.065),(.65,.64,.60))
add(architecture,"back_wall",(13,.15,4.4),(0,2.25,2.2),(.24,.26,.25))
add(architecture,"left_wall",(.15,12,4.4),(-8,1,2.2),(.33,.34,.32))
add(architecture,"ceiling",(18,14,.13),(0,0,4.13),(.028,.034,.033))
add(architecture,"upper_wall_band",(8,.10,.68),(.2,2.13,3.04),(.37,.39,.37))
for i in range(-6,7):
    add(architecture,f"floor_x_{i}",(.006,16,.001),(i*1.15,0,.001),(.48,.48,.45))
    add(architecture,f"floor_y_{i}",(18,.006,.001),(0,i*1.15,.001),(.48,.48,.45))
for i,y in enumerate((-2,-.3,1.4,3.1)):
    add(architecture,f"beam_{i}",(14,.20,.30),(0,y,3.94),(.045,.052,.051))
for i in range(12):
    add(architecture,f"deck_rib_{i}",(.035,12,.075),(-5+i*.8,0,4.03),(.075,.083,.080))
add(architecture,"large_crossbeam",(.30,12,.38),(2.25,0,3.88),(.065,.075,.073))
scene.include("architecture",architecture)

posts = Asset("Oak structural posts")
add(posts,"foreground_post",(.32,.34,4.3),(-2.04,.02,2.15),WOOD)
add(posts,"right_post",(.18,.23,4.1),(3.48,1.46,2.05),WOOD)
scene.include("posts",posts)

rear = Asset("Fitted rear kitchen")
add(rear,"left_tower",(.98,.69,2.45),(-2.45,1.55,1.225),BLACK)
add(rear,"left_tower_front",(.945,.035,2.39),(-2.45,1.185,1.225),(.045,.050,.048))
add(rear,"left_tower_joint",(.96,.012,.008),(-2.45,1.158,2.16),(.015,.019,.018))
add(rear,"base_cabinet",(3.95,.65,.88),(-.02,1.65,.47),DARK)
add(rear,"base_toe",(3.95,.50,.11),(-.02,1.69,.055),(.018,.023,.022))
for i in range(5):
    add(rear,f"base_door_{i}",(.775,.035,.78),(-1.60+i*.79,1.303,.48),DARK)
add(rear,"rear_counter",(4.06,.75,.055),(-.02,1.61,.94),(.16,.17,.15))
add(rear,"black_splashback",(4.12,.06,1.25),(-.06,2.08,1.66),(.035,.040,.037))
add(rear,"warm_niche",(2.94,.035,.40),(-.52,2.025,1.25),(.32,.27,.23))
add(rear,"niche_ledge",(3.05,.24,.035),(-.52,1.93,1.035),(.22,.21,.18))
add(rear,"upper_cabinets",(3.95,.42,.56),(-.04,1.88,1.93),(.040,.045,.042))
for i in range(6):
    add(rear,f"upper_seam_{i}",(.009,.016,.55),(-1.98+i*.79,1.658,1.93),(.017,.022,.019))
add(rear,"light_strip",(2.92,.035,.013),(-.53,1.663,1.64),(.95,.73,.46))
add(rear,"oven_tower",(.94,.77,2.55),(2.47,1.63,1.275),(.037,.043,.041))
add(rear,"oven_lower_door",(.85,.035,.70),(2.47,1.227,.49),DARK)
for i,z in enumerate((1.13,1.66)):
    add(rear,f"oven_frame_{i}",(.81,.055,.49),(2.47,1.213,z),(.27,.29,.28))
    add(rear,f"oven_glass_{i}",(.70,.018,.325),(2.47,1.176,z+.025),(.018,.030,.034))
    add(rear,f"oven_controls_{i}",(.76,.022,.072),(2.47,1.169,z+.207),(.16,.18,.18))
    add(rear,f"oven_handle_{i}",(.65,.055,.028),(2.47,1.125,z-.135),(.46,.49,.48))
add(rear,"oven_upper_door",(.86,.035,.49),(2.47,1.227,2.22),DARK)
add(rear,"right_black_partition",(.69,.48,2.76),(3.24,1.79,1.38),DARK)
add(rear,"right_reveal",(.07,.76,2.9),(3.61,1.64,1.45),(.12,.14,.13))
scene.include("rear_kitchen",rear)

island = Asset("Island")
add(island,"cabinet_body",(2.34,1.23,.88),(0,-.13,.50),(.53,.55,.53))
add(island,"plinth",(2.22,1.08,.105),(0,-.10,.075),(.16,.18,.17))
add(island,"left_end",(.075,1.29,.94),(-1.155,-.13,.52),(.60,.62,.60))
add(island,"right_end",(.045,1.25,.91),(1.165,-.13,.51),(.63,.65,.62))
for i,z in enumerate((.252,.537,.817)):
    add(island,f"drawer_{i}",(2.26,.045,.267),(.025,-.772,z),(.65,.67,.64))
    add(island,f"drawer_gap_{i}",(2.26,.025,.013),(.025,-.797,z+.141),(.21,.23,.21))
counter = box((2.43,1.36,.052),center=(0,-.13,1.012),color=(.81,.82,.77))
cut = box((.58,.41,.20),center=(.28,.16,1.015))
island.include("counter",subtract(counter,cut))
add(island,"sink_bottom",(.57,.40,.018),(.28,.16,.925),(.44,.47,.44))
for name,size,center in (
    ("left",(.018,.41,.07),(-.001,.16,.967)),
    ("right",(.018,.41,.07),(.561,.16,.967)),
    ("back",(.58,.018,.07),(.28,.356,.967)),
    ("front",(.58,.018,.07),(.28,-.036,.967))):
    add(island,"sink_"+name,size,center,(.65,.68,.64))
island.include("tap",sweep_tube(
    points=[(.65,.34,1.04),(.65,.34,1.24),(.64,.32,1.29),
            (.59,.27,1.30),(.48,.25,1.30),(.45,.25,1.26)],
    radius=.013,color=(.53,.57,.55)))
island.include("tap_base",rod(.032,start=(.65,.34,1.037),end=(.65,.34,1.065),color=(.34,.37,.36)))
scene.include("island",island)

hood = Asset("Suspended stone extractor")
add(hood,"stone_body",(1.03,.88,1.98),(-.11,.15,2.89),(.72,.72,.65))
add(hood,"underside",(.94,.78,.025),(-.11,.15,1.893),(.44,.45,.40))
add(hood,"filter",(.43,.36,.012),(-.11,.15,1.876),(.21,.23,.21))
add(hood,"lower_lip",(.18,.06,.018),(-.35,-.30,1.91),(.52,.54,.49))
scene.include("hood",hood)

objects = Asset("Niche kettle")
objects.include("red_body",ball(.087,center=(-.51,1.68,1.065),color=(.61,.012,.024)))
add(objects,"black_foot",(.145,.12,.025),(-.51,1.68,.992),(.02,.024,.023))
objects.include("handle",sweep_tube(
    points=[(-.58,1.68,1.08),(-.59,1.68,1.17),(-.54,1.68,1.20),
            (-.46,1.68,1.18),(-.44,1.68,1.09)],
    radius=.014,color=(.025,.028,.025)))
scene.include("kettle",objects)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Roughness"].default_value=.5
    c=tuple(bs.inputs["Base Color"].default_value[:3])
    if sum(abs(c[i]-WOOD[i]) for i in range(3)) < .035:
        coord=nt.nodes.new("ShaderNodeTexCoord")
        stretch=nt.nodes.new("ShaderNodeVectorMath")
        stretch.operation='MULTIPLY'
        stretch.inputs[1].default_value=(32,32,1.2)
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=3
        noise.inputs["Detail"].default_value=3
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(.20,.105,.047,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(.57,.38,.21,1)
        nt.links.new(coord.outputs["Generated"],stretch.inputs[0])
        nt.links.new(stretch.outputs[0],noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.18
        bump.inputs["Distance"].default_value=.012
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    if sum(abs(c[i]-(.72,.72,.65)[i]) for i in range(3)) < .025:
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=100
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.15
        bump.inputs["Distance"].default_value=.008
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    if .32 < c[0] < .56 and c[2] > c[0] and abs(c[1]-c[2]) < .06:
        bs.inputs["Metallic"].default_value=.8
        bs.inputs["Roughness"].default_value=.24

CAMERA_POSITION=(-6.3,-4.2,2.85)
CAMERA_TARGET=(-.30,.20,1.65)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=47)
sc=bpy.context.scene
sc.camera.data.sensor_fit='VERTICAL'
sc.camera.data.sensor_height=32
sc.camera.data.clip_start=.05
sc.camera.data.clip_end=100
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.48,.51,.48,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.23
area_emitter((-3.1,-3.6,3.6),power=1050,size=4,target=(0,.2,1),color=(1,.94,.83))
area_emitter((1.6,-1.1,3.7),power=650,size=3,target=(0,0,1),color=(.91,.96,1))
area_emitter((-.7,1.60,1.61),power=65,size=1.8,target=(-.7,2.02,1.20),color=(1,.72,.49))
area_emitter((-2.8,1.1,3.4),power=180,size=1.7,target=(-1.7,1.3,1.5),color=(1,.94,.82))
sc.view_settings.view_transform='AgX'
