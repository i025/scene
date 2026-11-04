from sceneact import *
import bpy
import math

# Camera hypothesis: looking diagonally across a showroom kitchen, with nearly
# vertical uprights. Island occupies roughly (.33,.56)-(.90,.85), hood
# (.42,.04)-(.73,.44), foreground timber (.16,0)-(.31,.99).
# Long cabinet edges recede up/right; depth edges recede up/left.
# Occlusion: foreground timber, island, suspended hood, rear cabinetry, walls.
P = dict(island_x=.35, island_y=-.10, island_w=2.20, island_d=1.04,
         counter_z=.96, ceiling_z=3.65,
         camera=(-4.35,-6.35,2.65), target=(.10,.35,1.85), lens=37)

scene = Scene("Modern kitchen showroom")
WHITE=(.69,.70,.67)
TOP=(.79,.80,.75)
BLACK=(.025,.029,.028)
DARK=(.055,.061,.059)
WOOD=(.40,.255,.135)
HOOD=(.72,.71,.65)
METAL=(.38,.40,.39)

def cube(asset, name, size, center, color):
    asset.include(name, box(size, center=center, color=color))

architecture=Asset("Architecture")
cube(architecture,"floor",(14,13,.12),(0,0,-.07),(.63,.62,.58))
cube(architecture,"rear_wall",(9,.16,3.7),(0,2.42,1.80),(.25,.27,.26))
cube(architecture,"left_wall",(.15,6,3.7),(-3.3,.6,1.80),(.34,.35,.32))
cube(architecture,"dark_ceiling",(10,9,.12),(0,0,3.71),(.025,.031,.030))
# Thin, quiet grout lines on large pale porcelain tiles.
for i in range(-6,7):
    cube(architecture,"tile_joint_x_%02d"%i,(.008,12,.002),(i*1.15,0,-.008),(.41,.41,.38))
for i in range(-5,6):
    cube(architecture,"tile_joint_y_%02d"%i,(13,.008,.002),(0,i*1.15,-.007),(.41,.41,.38))
scene.include("architecture",architecture)

ceiling=Asset("Exposed dark ceiling structure")
for i,x in enumerate([-3.0,-1.6,.0,1.6,3.2]):
    cube(ceiling,"main_beam_%d"%i,(.16,8,.26),(x,.0,3.49),(.035,.043,.042))
for i,y in enumerate([-2.4,-.7,1.0,2.7]):
    cube(ceiling,"cross_beam_%d"%i,(8,.13,.18),(0,y,3.54),(.045,.052,.050))
for i in range(13):
    cube(ceiling,"roof_seam_%d"%i,(.018,8,.025),(-3.6+i*.6,0,3.635),(.07,.075,.070))
cube(ceiling,"wide_overhead_girder",( .32,8,.34),(2.15,-.3,3.42),(.12,.14,.14))
scene.include("ceiling_structure",ceiling)

posts=Asset("Natural oak structural posts")
cube(posts,"foreground_post",(.34,.35,3.76),(-1.98,-1.38,1.87),WOOD)
cube(posts,"distant_post",(.19,.20,3.65),(2.48,1.55,1.825),WOOD)
scene.include("timber_posts",posts)

rear=Asset("Rear black kitchen cabinetry")
# Tall left bank and the broad recessed counter niche.
cube(rear,"left_tall_case",(.88,.64,2.12),(-2.02,1.95,1.06),BLACK)
for i in range(2):
    cube(rear,"left_door_%d"%i,(.427,.025,2.04),(-2.245+i*.439,1.615,1.075),(.035,.039,.037))
cube(rear,"rear_base",(3.35,.62,.88),(.02,1.93,.46),BLACK)
cube(rear,"rear_worktop",(3.42,.69,.045),(.02,1.895,.922),(.10,.105,.095))
for i in range(5):
    cube(rear,"base_door_%d"%i,(.65,.027,.79),(-1.31+i*.67,1.603,.46),(.037,.041,.039))
cube(rear,"niche_back",(2.64,.035,.52),(-.22,2.226,1.23),(.20,.16,.14))
cube(rear,"niche_bottom",(2.65,.63,.025),(-.22,1.92,.963),(.13,.12,.11))
cube(rear,"niche_upper_dark_band",(2.76,.60,.40),(-.20,1.96,1.72),(.038,.045,.043))
cube(rear,"niche_led",(2.55,.025,.014),(-.22,2.05,1.512),(.95,.77,.56))
# Broad black panels over the niche.
for i in range(4):
    cube(rear,"upper_panel_%d"%i,(.69,.035,.40),(-1.245+i*.70,1.635,1.72),(.045,.052,.049))
scene.include("rear_cabinets",rear)

oven=Asset("Tall appliance tower")
cube(oven,"tower_body",(.86,.72,2.18),(1.78,1.92,1.09),(.022,.027,.025))
cube(oven,"tower_left_stile",(.10,.025,2.10),(1.39,1.545,1.10),(.07,.076,.071))
cube(oven,"tower_right_stile",(.11,.025,2.10),(2.15,1.545,1.10),(.065,.07,.066))
for i,z in enumerate([.59,1.18]):
    cube(oven,"oven_frame_%d"%i,(.65,.055,.49),(1.77,1.535,z),(.24,.25,.23))
    cube(oven,"oven_glass_%d"%i,(.57,.022,.32),(1.77,1.497,z-.035),(.018,.029,.032))
    cube(oven,"control_band_%d"%i,(.60,.025,.073),(1.77,1.494,z+.185),(.31,.32,.30))
    cube(oven,"handle_%d"%i,(.53,.046,.024),(1.77,1.46,z+.115),(.44,.46,.44))
cube(oven,"bottom_door",(.65,.03,.29),(1.77,1.53,.19),(.038,.043,.039))
cube(oven,"upper_door",(.65,.03,.46),(1.77,1.53,1.78),(.032,.039,.035))
scene.include("oven_tower",oven)

side=Asset("Right dark partition")
cube(side,"end_wall",(.18,1.34,2.38),(2.40,1.97,1.19),(.035,.042,.038))
cube(side,"upper_gray_fascia",(3.4,.22,.37),(.91,2.28,2.42),(.30,.33,.32))
scene.include("right_partition",side)

island=Asset("Pale gray island with three handleless drawers")
cx,cy=P["island_x"],P["island_y"]
w,d=P["island_w"],P["island_d"]
cube(island,"dark_recessed_plinth",(w-.10,d-.10,.095),(cx,cy,.07),(.19,.20,.18))
cube(island,"main_carcass",(w,d,.81),(cx,cy,.505),(.55,.57,.54))
cube(island,"left_waterfall_end",(.055,d,.91),(cx-w/2-.005,cy,.505),WHITE)
cube(island,"right_end",(.035,d,.87),(cx+w/2-.012,cy,.49),WHITE)
cube(island,"stone_countertop",(w+.045,d+.035,.045),(cx,cy,.9725),TOP)
# Drawer fronts are on the camera-facing long side.
for i,(z,h) in enumerate([(.226,.245),(.491,.245),(.756,.245)]):
    cube(island,"drawer_%d"%i,(w-.07,.038,h),(cx+.012,cy-d/2-.008,z),(.66,.68,.65))
    cube(island,"drawer_shadow_%d"%i,(w-.075,.018,.016),(cx+.012,cy-d/2-.009,z+h/2+.008),(.25,.27,.24))
scene.include("island",island)

sink=Asset("Flush inset sink and chrome mixer")
sx,sy=.62,.105
cube(sink,"sink_rim",(.57,.40,.009),(sx,sy,.998),(.53,.57,.54))
cube(sink,"sink_inner",(.50,.33,.010),(sx,sy,1.003),(.42,.47,.44))
cube(sink,"sink_basin",(.435,.266,.007),(sx,sy,1.009),(.53,.58,.55))
sink.include("tap_base",rod(.033,start=(sx+.03,sy+.29,.997),end=(sx+.03,sy+.29,1.03),color=METAL))
sink.include("tap_upright",rod(.014,start=(sx+.03,sy+.29,1.02),end=(sx+.03,sy+.29,1.25),color=(.60,.64,.62)))
sink.include("tap_neck",sweep_tube(points=[(sx+.03,sy+.29,1.25),(sx+.03,sy+.27,1.29),(sx+.03,sy+.13,1.29),(sx+.03,sy+.10,1.25)],radius=.014,color=(.62,.65,.63)))
sink.include("tap_handle",rod(.009,start=(sx+.075,sy+.29,1.07),end=(sx+.075,sy+.29,1.16),color=(.52,.56,.54)))
# Minimal pale cooktop lines toward the left side of the slab.
cube(sink,"flush_hob",(.62,.46,.006),(-.29,-.12,1.0),(.71,.74,.69))
for i,x in enumerate([-.46,-.16]):
    cube(sink,"hob_mark_%d"%i,(.19,.006,.002),(x,-.22,1.005),(.87,.88,.82))
scene.include("sink_and_hob",sink)

hood=Asset("Large suspended rectangular plaster extractor")
cube(hood,"plaster_body",(1.10,.88,1.72),(.02,.09,2.71),HOOD)
cube(hood,"underside",(1.075,.85,.025),(.02,.09,1.845),(.48,.48,.43))
cube(hood,"underside_filter",(.65,.46,.009),(.02,.09,1.829),(.28,.29,.26))
cube(hood,"small_control",(.055,.015,.018),(.02,-.357,1.87),(.30,.31,.28))
scene.include("suspended_hood",hood)

kettle=Asset("Small red kettle on rear worktop")
kettle.include("body",ball(.104,center=(-.35,1.84,1.065),color=(.65,.012,.025)))
cube(kettle,"black_base",(.18,.15,.035),(-.35,1.84,.974),(.016,.018,.017))
cube(kettle,"front_dark",(.13,.055,.12),(-.35,1.754,1.035),(.013,.018,.017))
kettle.include("handle",sweep_tube(points=[(-.43,1.84,1.085),(-.43,1.84,1.17),(-.32,1.84,1.195),(-.25,1.84,1.14)],radius=.014,color=(.80,.015,.025)))
scene.include("red_kettle",kettle)

# Small ceiling track and spot fixtures.
track=Asset("Ceiling lighting")
cube(track,"track",(.045,3.7,.045),(-1.80,.35,3.38),(.04,.045,.041))
for i,y in enumerate([-.40,1.15]):
    track.include("stem_%d"%i,rod(.013,start=(-1.8,y,3.38),end=(-1.8,y,3.27),color=(.1,.11,.10)))
    track.include("spot_%d"%i,rod(.047,start=(-1.8,y,3.28),end=(-1.76,y-.06,3.20),color=(.43,.45,.42)))
scene.include("ceiling_lights",track)

print("SceneAct primitive count:",sum(n.solid is not None for n in scene.traverse()))
realize(scene)

# Reusable procedural finishes, with no image textures.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    col=bs.inputs["Base Color"].default_value
    rgb=tuple(col[:3])
    bs.inputs["Roughness"].default_value=.52
    if sum(abs(rgb[i]-WOOD[i]) for i in range(3)) < .08:
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=4.0
        tex.inputs["Detail"].default_value=3
        mapping=nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(8,8,.32)
        coords=nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(coords.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=(.16,.082,.033,1)
        ramp.color_ramp.elements[1].position=.80
        ramp.color_ramp.elements[1].color=(.57,.37,.20,1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.22
        bump.inputs["Distance"].default_value=.018
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    elif sum(abs(rgb[i]-HOOD[i]) for i in range(3)) < .025:
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=105
        tex.inputs["Detail"].default_value=2
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.16
        bump.inputs["Distance"].default_value=.012
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        bs.inputs["Roughness"].default_value=.85
    elif min(rgb)>.35 and max(rgb)-min(rgb)<.09:
        bs.inputs["Roughness"].default_value=.30

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.32,.35,.36,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.28

set_view(P["camera"],P["target"],lens=P["lens"],sensor=36)
area_emitter((-3.0,-3.3,3.2),power=850,size=4.0,target=(.1,.0,.7),color=(1.0,.94,.83))
area_emitter((1.8,-.7,3.3),power=450,size=3,target=(.3,.3,.8),color=(.89,.94,1.0))
area_emitter((-.25,1.94,1.49),power=45,size=1.6,target=(-.25,1.91,.95),color=(1.0,.69,.48))
area_emitter((-2.7,.8,2.8),power=160,size=1.8,target=(-1.0,1.5,1.1),color=(1.0,.94,.82))
sc.view_settings.view_transform='AgX'
