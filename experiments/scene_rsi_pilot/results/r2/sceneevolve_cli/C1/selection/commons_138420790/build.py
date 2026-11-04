from sceneact import *
import bpy

# Island is too low and its top exposes too much depth: lower camera and aim.
# Rear cabinets are too pale; reduce their reflectance and the broad illumination.
# Hood is too tall; shorten it, and move the right partition/post toward frame right.

scene = Scene("Kitchen showroom")
BLACK = (.009,.012,.011)
DARK = (.018,.023,.021)
WOOD = (.39,.235,.115)

def add(parent, name, size, center, color):
    node = box(size=size, center=center, color=color)
    parent.include(name, node)
    return node

architecture = Asset("Architecture")
add(architecture,"floor",(20,18,.12),(0,0,-.065),(.55,.54,.50))
add(architecture,"back_wall",(13,.15,4.4),(0,2.25,2.2),(.15,.17,.16))
add(architecture,"left_wall",(.15,12,4.4),(-8,1,2.2),(.25,.26,.24))
add(architecture,"ceiling",(18,14,.13),(0,0,4.13),(.012,.018,.017))
add(architecture,"upper_wall_band",(9,.10,.68),(.6,2.13,3.04),(.29,.31,.29))
for i in range(-6,7):
    add(architecture,f"floor_x_{i}",(.004,16,.001),(i*1.15,0,.001),(.40,.40,.37))
    add(architecture,f"floor_y_{i}",(18,.004,.001),(0,i*1.15,.001),(.40,.40,.37))
for i,y in enumerate((-2,-.3,1.4,3.1)):
    add(architecture,f"beam_{i}",(14,.20,.30),(0,y,3.94),(.022,.029,.028))
for i in range(12):
    add(architecture,f"deck_rib_{i}",(.035,12,.075),(-5+i*.8,0,4.03),(.035,.043,.040))
add(architecture,"large_crossbeam",(.34,12,.40),(2.25,0,3.88),(.035,.045,.043))
scene.include("architecture",architecture)

posts = Asset("Oak structural posts")
add(posts,"foreground_post",(.32,.34,4.3),(-1.94,.02,2.15),WOOD)
add(posts,"right_post",(.18,.23,4.1),(4.85,1.46,2.05),WOOD)
scene.include("posts",posts)

rear = Asset("Fitted rear kitchen")
add(rear,"left_tower",(.98,.69,2.45),(-2.05,1.55,1.225),BLACK)
add(rear,"left_tower_front",(.945,.035,2.39),(-2.05,1.185,1.225),(.024,.029,.027))
add(rear,"left_tower_joint",(.96,.012,.008),(-2.05,1.158,2.16),(.007,.009,.008))
add(rear,"base_cabinet",(4.50,.65,.88),(.25,1.65,.47),DARK)
add(rear,"base_toe",(4.50,.50,.11),(.25,1.69,.055),(.008,.012,.011))
for i in range(6):
    add(rear,f"base_door_{i}",(.735,.035,.78),(-1.62+i*.75,1.303,.48),DARK)
add(rear,"rear_counter",(4.60,.75,.055),(.25,1.61,.94),(.10,.11,.095))
add(rear,"black_splashback",(4.65,.06,1.25),(.20,2.08,1.66),(.014,.019,.016))
add(rear,"warm_niche",(3.30,.035,.40),(-.20,2.025,1.25),(.25,.19,.16))
add(rear,"niche_ledge",(3.35,.24,.035),(-.20,1.93,1.035),(.15,.14,.12))
add(rear,"upper_cabinets",(4.50,.42,.56),(.25,1.88,1.93),(.017,.022,.019))
for i in range(7):
    add(rear,f"upper_seam_{i}",(.009,.016,.55),(-2+i*.75,1.658,1.93),(.006,.010,.008))
add(rear,"light_strip",(3.25,.035,.013),(-.20,1.663,1.64),(.72,.49,.30))
ox=3.10
add(rear,"oven_tower",(.94,.77,2.55),(ox,1.63,1.275),(.015,.021,.019))
add(rear,"oven_lower_door",(.85,.035,.70),(ox,1.227,.49),DARK)
for i,z in enumerate((1.13,1.66)):
    add(rear,f"oven_frame_{i}",(.81,.055,.49),(ox,1.213,z),(.20,.22,.21))
    add(rear,f"oven_glass_{i}",(.70,.018,.325),(ox,1.176,z+.025),(.009,.019,.023))
    add(rear,f"oven_controls_{i}",(.76,.022,.072),(ox,1.169,z+.207),(.10,.12,.12))
    add(rear,f"oven_handle_{i}",(.65,.055,.028),(ox,1.125,z-.135),(.36,.39,.38))
add(rear,"oven_upper_door",(.86,.035,.49),(ox,1.227,2.22),DARK)
add(rear,"right_black_partition",(1.14,.48,2.76),(4.15,1.79,1.38),DARK)
add(rear,"right_reveal",(.07,.76,2.9),(4.76,1.64,1.45),(.065,.08,.07))
scene.include("rear_kitchen",rear)

island = Asset("Island")
add(island,"cabinet_body",(2.34,1.23,.88),(0,-.13,.50),(.43,.45,.43))
add(island,"plinth",(2.22,1.08,.105),(0,-.10,.075),(.10,.12,.11))
add(island,"left_end",(.075,1.29,.94),(-1.155,-.13,.52),(.49,.51,.49))
add(island,"right_end",(.045,1.25,.91),(1.165,-.13,.51),(.52,.54,.51))
for i,z in enumerate((.252,.537,.817)):
    add(island,f"drawer_{i}",(2.26,.045,.267),(.025,-.772,z),(.56,.58,.55))
    add(island,f"drawer_gap_{i}",(2.26,.025,.013),(.025,-.797,z+.141),(.14,.16,.14))
counter = box((2.43,1.36,.052),center=(0,-.13,1.012),color=(.73,.74,.69))
cut = box((.58,.41,.20),center=(.28,.16,1.015))
island.include("counter",subtract(counter,cut))
add(island,"sink_bottom",(.57,.40,.018),(.28,.16,.925),(.37,.40,.37))
for name,size,center in (
    ("left",(.018,.41,.07),(-.001,.16,.967)),
    ("right",(.018,.41,.07),(.561,.16,.967)),
    ("back",(.58,.018,.07),(.28,.356,.967)),
    ("front",(.58,.018,.07),(.28,-.036,.967))):
    add(island,"sink_"+name,size,center,(.55,.58,.54))
island.include("tap",sweep_tube(
    points=[(.65,.34,1.04),(.65,.34,1.24),(.64,.32,1.29),
            (.59,.27,1.30),(.48,.25,1.30),(.45,.25,1.26)],
    radius=.013,color=(.42,.46,.44)))
island.include("tap_base",rod(.032,start=(.65,.34,1.037),
                             end=(.65,.34,1.065),color=(.34,.37,.36)))
scene.include("island",island)

hood = Asset("Suspended stone extractor")
hx=.12
hz=2.76
add(hood,"stone_body",(1.03,.88,1.80),(hx,.15,hz),(.66,.66,.59))
add(hood,"underside",(.94,.78,.025),(hx,.15,1.852),(.34,.35,.30))
add(hood,"filter",(.43,.36,.012),(hx,.15,1.836),(.15,.17,.15))
add(hood,"lower_lip",(.18,.06,.018),(hx-.24,-.30,1.87),(.44,.46,.41))
scene.include("hood",hood)

objects = Asset("Niche kettle")
objects.include("red_body",ball(.087,center=(-.12,1.68,1.065),color=(.65,.005,.016)))
add(objects,"black_foot",(.145,.12,.025),(-.12,1.68,.992),(.008,.012,.011))
objects.include("handle",sweep_tube(
    points=[(-.19,1.68,1.08),(-.20,1.68,1.17),(-.15,1.68,1.20),
            (-.07,1.68,1.18),(-.05,1.68,1.09)],
    radius=.014,color=(.009,.012,.009)))
scene.include("kettle",objects)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Roughness"].default_value=.48
    c=tuple(bs.inputs["Base Color"].default_value[:3])
    if sum(abs(c[i]-WOOD[i]) for i in range(3)) < .025:
        coord=nt.nodes.new("ShaderNodeTexCoord")
        stretch=nt.nodes.new("ShaderNodeVectorMath")
        stretch.operation='MULTIPLY'
        stretch.inputs[1].default_value=(38,38,1.1)
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=3
        noise.inputs["Detail"].default_value=3
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(.105,.045,.016,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(.43,.25,.115,1)
        nt.links.new(coord.outputs["Generated"],stretch.inputs[0])
        nt.links.new(stretch.outputs[0],noise.inputs["Vector"])
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.20
        bump.inputs["Distance"].default_value=.012
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    if sum(abs(c[i]-(.66,.66,.59)[i]) for i in range(3)) < .025:
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=95
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.17
        bump.inputs["Distance"].default_value=.008
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    if .32 < c[0] < .48 and c[2] > c[0] and abs(c[1]-c[2]) < .06:
        bs.inputs["Metallic"].default_value=.85
        bs.inputs["Roughness"].default_value=.22

CAMERA_POSITION=(-6.3,-4.2,2.40)
CAMERA_TARGET=(-.30,.20,1.44)
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
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.40,.43,.40,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.10
area_emitter((-3.1,-3.6,3.6),power=510,size=3.5,
             target=(0,.2,1),color=(1,.94,.84))
area_emitter((1.6,-1.1,3.7),power=230,size=2.4,
             target=(0,0,1),color=(.91,.96,1))
area_emitter((-.3,1.60,1.61),power=45,size=1.7,
             target=(-.3,2.02,1.20),color=(1,.68,.46))
area_emitter((-2.8,1.1,3.4),power=70,size=1.4,
             target=(-1.7,1.3,1.5),color=(1,.94,.82))
sc.view_settings.view_transform='AgX'
