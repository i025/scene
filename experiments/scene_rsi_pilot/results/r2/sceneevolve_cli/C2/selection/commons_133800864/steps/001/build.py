# Anchors: window occupies x=0-.30, y=0-.80; cabinet spans x=.29-1, y=0-.53.
# Paper roll bounds approximately (.61,.08)-(.83,.42); ring center approximately (.36,.42).
# Counter/wall boundary runs from approximately (0,.81) through (.48,.66) to (1,.71).
# Perspective edges: counter depth slopes down-left; cabinet bottom slopes down-right then up-right.
# Foreground jug overlaps blender; towel overlaps window and counter accessories.
# Sink is cropped at bottom-left; cabinet top and right side extend beyond frame.
from sceneact import *
import bpy
import math

scene = Scene(name="Window-side kitchen")
CREAM = (.77,.72,.59)
DOOR = (.81,.76,.64)
WHITE = (.88,.85,.75)
CHROME = (.48,.48,.40)
GRANITE = (.29,.265,.205)
NAVY = (.025,.045,.095)

def add(parent, name, node):
    parent.include(name, node)

architecture = Asset("Architecture")
add(architecture,"back_wall",box((3.5,.08,3.1),center=(0,.71,1.4),color=(.71,.67,.54)))
add(architecture,"right_wall",box((.08,2.4,3.1),center=(1.15,-.4,1.4),color=(.73,.68,.55)))
scene.include("architecture",architecture)

window = Asset("Window and Venetian blind")
add(window,"daylight_glass",box((1.25,.025,1.91),center=(-.92,.647,1.72),color=(.72,.86,.89)))
for i,x in enumerate((-1.56,-.29)):
    add(window,"vertical_trim_%d"%i,box((.055,.09,2.08),center=(x,.59,1.73),color=WHITE))
for i,z in enumerate((.70,2.74)):
    add(window,"horizontal_trim_%d"%i,box((1.32,.10,.06),center=(-.925,.58,z),color=WHITE))
add(window,"window_mullion",box((.035,.055,1.94),center=(-1.0,.58,1.72),color=(.86,.87,.79)))
add(window,"window_crossbar",box((1.2,.06,.045),center=(-.93,.57,1.7),color=WHITE))
for i in range(32):
    z=.77+i*.061
    slat=box((1.27,.105,.014),center=(-.925,.49,z),color=(.82,.83,.75))
    slat.turn('x',-13)
    add(window,"blind_slat_%02d"%i,slat)
for i,x in enumerate((-1.36,-.62)):
    add(window,"blind_ladder_%d"%i,box((.011,.008,1.98),center=(x,.425,1.73),color=(.74,.74,.65)))
add(window,"sill",box((1.36,.22,.065),center=(-.94,.54,.725),color=WHITE))
scene.include("window",window)

cabinet=Asset("Cream wall cabinet")
add(cabinet,"carcass",box((1.18,.49,1.65),center=(.34,.40,2.115),color=CREAM))
# The left return is a broad exposed cabinet side.
add(cabinet,"left_return",box((.035,.51,1.67),center=(-.265,.395,2.12),color=(.80,.76,.65)))
add(cabinet,"bottom",box((1.2,.53,.045),center=(.335,.375,1.285),color=DOOR))
for j,(x,w) in enumerate(((.105,.66),(.70,.49))):
    add(cabinet,"door_%d"%j,box((w,.043,1.60),center=(x,.125,2.13),color=DOOR))
    for k,xx in enumerate((x-w/2+.043,x+w/2-.043)):
        add(cabinet,"stile_%d_%d"%(j,k),box((.046,.022,1.53),center=(xx,.094,2.13),color=(.84,.79,.66)))
    for k,zz in enumerate((1.395,2.865)):
        add(cabinet,"rail_%d_%d"%(j,k),box((w-.065,.022,.047),center=(x,.093,zz),color=(.84,.79,.66)))
    add(cabinet,"recess_%d"%j,box((w-.13,.012,1.38),center=(x,.102,2.13),color=(.785,.737,.61)))
add(cabinet,"small_knob",ball(.022,center=(.46,.052,1.59),color=(.37,.32,.19)))
add(cabinet,"knob_stem",rod(.012,start=(.46,.08,1.59),end=(.46,.04,1.59),color=CHROME))
scene.include("cabinet",cabinet)

roll=Asset("Paper towel and wall holder")
add(roll,"paper",rod(.143,start=(.18,-.045,1.58),end=(.18,-.045,2.24),color=(.91,.87,.74)))
add(roll,"paper_top",rod(.134,length=.006,center=(.18,-.045,2.244),color=(.84,.80,.68)))
add(roll,"top_finial",rod(.021,length=.075,center=(.18,-.045,2.287),color=CHROME))
add(roll,"finial_cap",ball(.025,center=(.18,-.045,2.323),color=CHROME))
for i,x in enumerate((.08,.28)):
    add(roll,"lower_support_%d"%i,rod(.017,start=(x,.11,1.56),end=(x,-.065,1.56),color=(.26,.25,.20)))
add(roll,"loose_sheet",box((.22,.006,.35),center=(.183,-.186,1.77),color=(.93,.89,.77)))
scene.include("paper_towels",roll)

towel=Asset("Ring and hanging hand towel")
add(towel,"mount_rosette",rod(.045,start=(-.283,.34,1.82),end=(-.32,.34,1.82),color=CHROME))
add(towel,"mount_neck",rod(.016,start=(-.32,.34,1.82),end=(-.385,.34,1.82),color=CHROME))
points=[]
for i in range(25):
    a=2*math.pi*i/24
    points.append((-.385,.34+.105*math.sin(a),1.665+.145*math.cos(a)))
add(towel,"oval_ring",sweep_tube(points=points,radius=.008,color=(.58,.58,.50)))
# Narrow cloth ribbons form a softly irregular, broad draped surface.
for i in range(11):
    v=(i-5)/5
    yy=.30+v*.083
    bottom=1.00+.048*math.cos(i*.75)+.045*abs(v)
    top=1.55+.035*math.cos(v*1.4)
    xx=-.402-.018*math.sin(i*1.6)
    add(towel,"hanging_fold_%d"%i,box((.024,.020,top-bottom),center=(xx,yy,(top+bottom)/2),color=(.84+.025*math.sin(i),.80+.025*math.sin(i),.69+.02*math.sin(i))))
add(towel,"folded_over_ring",rod(.033,start=(-.413,.21,1.54),end=(-.413,.39,1.54),color=(.89,.85,.74)))
scene.include("hand_towel",towel)

counter=Asset("Granite counter and sink")
slab=box((2.65,1.20,.065),center=(-.15,.03,.815),color=GRANITE)
hole=box((.78,.64,.20),center=(-.83,-.30,.815))
add(counter,"stone_slab",subtract(slab,hole))
add(counter,"cabinet_base",box((2.60,1.12,.75),center=(-.15,.07,.405),color=(.30,.255,.18)))
add(counter,"backsplash",box((2.65,.055,.15),center=(-.15,.615,.90),color=GRANITE))
add(counter,"sink_bottom",box((.75,.61,.025),center=(-.83,-.30,.645),color=(.055,.065,.060)))
for i,x in enumerate((-1.215,-.445)):
    add(counter,"sink_side_%d"%i,box((.018,.64,.17),center=(x,-.30,.73),color=(.14,.15,.13)))
    add(counter,"sink_rim_side_%d"%i,box((.028,.68,.015),center=(x,-.30,.854),color=CHROME))
for i,y in enumerate((-.62,.02)):
    add(counter,"sink_end_%d"%i,box((.78,.018,.17),center=(-.83,y,.73),color=(.13,.14,.12)))
    add(counter,"sink_rim_end_%d"%i,box((.81,.025,.014),center=(-.83,y,.854),color=CHROME))
add(counter,"tap_foot",rod(.049,length=.028,center=(-.85,.105,.862),color=CHROME))
add(counter,"tap_stem",rod(.016,start=(-.85,.105,.87),end=(-.85,.105,1.16),color=CHROME))
add(counter,"tap_spout",sweep_tube(points=[(-.85,.105,1.16),(-.85,.10,1.20),(-.85,.055,1.22),(-.85,-.035,1.20),(-.85,-.075,1.16)],radius=.014,color=CHROME))
for i,x in enumerate((-1.02,-.68)):
    add(counter,"tap_control_%d"%i,rod(.028,length=.025,center=(x,.10,.871),color=CHROME))
    add(counter,"tap_lever_%d"%i,rod(.011,start=(x,.1,.89),end=(x+.035,.10,.94),color=CHROME))
scene.include("counter",counter)

appliances=Asset("Countertop appliances")
add(appliances,"blender_base",rod(.105,length=.205,center=(-.04,.27,.955),color=(.026,.029,.023)))
add(appliances,"blender_collar",rod(.095,length=.04,center=(-.04,.27,1.07),color=(.08,.08,.065)))
cup=rod(.063,length=.29,center=(-.055,.27,1.22),color=(.49,.47,.37),opacity=.29)
cup.turn('y',-13)
add(appliances,"blender_cup",cup)
add(appliances,"cup_bottom",rod(.061,length=.022,center=(-.023,.27,1.084),color=(.12,.12,.095)))
add(appliances,"cup_lip",rod(.067,length=.012,center=(-.087,.27,1.367),color=(.52,.51,.43)))
# Water-filter pitcher: blue reservoir, pale slanted lid, and open handle.
body=ball(.20,center=(.56,.30,1.055),color=NAVY,opacity=.85)
body.resize((.80,.70,1.31))
add(appliances,"pitcher_body",body)
add(appliances,"pitcher_base",rod(.125,length=.025,center=(.56,.30,.849),color=(.08,.09,.10)))
lid=rod(.155,length=.028,center=(.56,.29,1.285),color=(.37,.38,.33))
lid.resize((1,.77,1))
lid.turn('y',-12)
add(appliances,"pitcher_lid",lid)
add(appliances,"pitcher_handle",sweep_tube(points=[(.68,.29,1.25),(.79,.29,1.20),(.82,.29,1.08),(.79,.29,.96),(.70,.29,.94)],radius=.027,color=(.36,.38,.34)))
scene.include("appliances",appliances)

jug=Asset("Translucent water jug")
body=ball(.155,center=(.245,-.12,1.005),color=(.70,.73,.66),opacity=.87)
body.resize((.93,.76,1.14))
add(jug,"rounded_body",body)
add(jug,"flat_lower_body",rod(.136,length=.17,center=(.245,-.12,.948),color=(.70,.73,.66),opacity=.88))
shoulder=ball(.113,center=(.245,-.12,1.14),color=(.73,.75,.67),opacity=.88)
shoulder.resize((1,.88,.66))
add(jug,"shoulder",shoulder)
add(jug,"neck",rod(.041,length=.061,center=(.245,-.12,1.209),color=(.78,.79,.70)))
add(jug,"cap",rod(.043,length=.029,center=(.245,-.12,1.242),color=(.85,.84,.73)))
add(jug,"handle",sweep_tube(points=[(.335,-.12,1.15),(.385,-.12,1.10),(.38,-.12,1.015),(.34,-.12,.99)],radius=.018,color=(.76,.78,.69)))
# Sparse gray label strokes on the front face.
for i in range(6):
    add(jug,"label_stroke_%d"%i,box((.002,.002,.021+.006*(i%2)),center=(.196+i*.016,-.241,.94),color=(.32,.34,.32)))
scene.include("water_jug",jug)

small=Asset("Small counter objects")
add(small,"green_canister",rod(.057,length=.19,center=(-.31,.26,.95),color=(.30,.33,.16)))
add(small,"canister_lid",rod(.060,length=.019,center=(-.31,.26,1.054),color=(.47,.45,.27)))
add(small,"small_tin",rod(.042,length=.046,center=(-.51,.035,.87),color=(.23,.22,.16)))
add(small,"tin_top",rod(.035,length=.005,center=(-.51,.035,.896),color=(.42,.39,.29)))
add(small,"soap_dish",box((.18,.12,.018),center=(-1.22,-.015,.866),color=(.37,.35,.26)))
add(small,"soap",box((.115,.075,.027),center=(-1.22,-.015,.888),color=(.81,.77,.58)))
scene.include("small_objects",small)

realize(scene)

# Procedural stone speckles and subtle paper grain.
for mat in bpy.data.materials:
    c=mat.diffuse_color
    if sum(abs(c[i]-GRANITE[i]) for i in range(3)) < .065:
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=185
        noise.inputs["Detail"].default_value=2
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.25
        ramp.color_ramp.elements[0].color=(.065,.058,.043,1)
        ramp.color_ramp.elements[1].position=.77
        ramp.color_ramp.elements[1].color=(.58,.53,.41,1)
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bs.inputs["Roughness"].default_value=.57
    elif sum(abs(c[i]-CHROME[i]) for i in range(3)) < .03:
        mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Metallic"].default_value=.8
        bs.inputs["Roughness"].default_value=.25

CAMERA_POSITION=(-1.10,-2.25,1.80)
CAMERA_TARGET=(-.035,.28,1.52)
CAMERA_LENS=57
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.68,.73,.78,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.38
area_emitter((-1.7,-.10,2.15),power=210,size=1.65,target=(.15,.25,1.3),color=(.84,.92,1))
area_emitter((-.3,-1.5,2.7),power=90,size=2.0,target=(.2,.2,1.3),color=(1,.84,.64))
sc.view_settings.view_transform='Standard'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
