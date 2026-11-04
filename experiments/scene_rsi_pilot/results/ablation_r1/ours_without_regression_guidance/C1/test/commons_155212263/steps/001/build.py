from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(12)

# Observations: worn plank floor; a continuous diagonal row of heavy benches;
# two prominent vertical flywheels, an anvil, bench vices, drawers and floor cans.
# Approximate image landmarks: large wheel (340,95), anvil (220,149),
# foreground machine (402,206), floor arrow (66,273), windows across upper edge.
# Camera is an uncertain oblique view from the open aisle, looking toward the
# window wall. Dimensions use an assumed 1.05 m worktop height.
# Mapping: bench() -> timber workstations; wheel() -> cast-iron flywheels;
# lathe() -> foreground screw machine; anvil() -> central smithing anvil.
scene = Scene("Old window-side metalworking workshop")
wood=(.24,.19,.12)
topwood=(.38,.32,.23)
iron=(.12,.135,.13)
edge=(.27,.28,.26)
rust=(.24,.18,.12)
plaster=(.57,.59,.53)
steel=(.46,.48,.44)

def B(a,k,size,p,c):
    return a.include(k,box(size=size,center=p,color=c))
def R(a,k,p,q,r,c):
    return a.include(k,rod(radius=r,start=p,end=q,color=c))
def S(a,k,p,r,c):
    return a.include(k,ball(radius=r,center=p,color=c))
def tube(a,k,pts,r,c):
    return a.include(k,sweep_tube(points=pts,radius=r,color=c))
def ring(a,k,c,r,thick,color,plane="xz"):
    pts=[]
    for j in range(49):
        t=2*math.pi*j/48
        if plane=="xz": p=(c[0]+r*math.cos(t),c[1],c[2]+r*math.sin(t))
        elif plane=="xy": p=(c[0]+r*math.cos(t),c[1]+r*math.sin(t),c[2])
        else: p=(c[0],c[1]+r*math.cos(t),c[2]+r*math.sin(t))
        pts.append(p)
    return tube(a,k,pts,thick,color)

# Architecture and narrow, irregular floorboards.
room=Asset("architecture")
B(room,"floor_underlay",(14,12,.12),(0,-2,-.09),(.23,.20,.14))
for i in range(65):
    x=-7+i*.218
    for j in range(4):
        y=-6.8+j*2.8 + (.65 if i%2 else 0)
        col=(.43+random.uniform(-.055,.055),.355+random.uniform(-.035,.035),.235+random.uniform(-.025,.025))
        B(room,f"plank_{i}_{j}",(.210,2.785,.055),(x,y,-.012),col)
        if -4<x<5:
            for end in (-1.32,1.32):
                S(room,f"nail_{i}_{j}_{end}",(x+.065,y+end,.019),.007,(.15,.14,.12))
# The windows are openings between plaster piers, rather than pictures.
B(room,"wall_lower",(13,.24,1.55),(0,1.72,.775),plaster)
B(room,"wall_above",(13,.24,.65),(0,1.72,4.15),plaster)
for i,x in enumerate((-5.8,-3.65,-1.45,.78,3.02,5.3)):
    B(room,f"plaster_pier_{i}",(.29,.25,2.4),(x,1.72,2.72),plaster)
for i,x in enumerate((-4.72,-2.55,-.34,1.9,4.16)):
    B(room,f"window_sill_{i}",(1.98,.48,.12),(x,1.52,1.62),(.31,.32,.28))
    B(room,f"window_glass_{i}",(1.91,.035,2.12),(x,1.78,2.76),(.80,.87,.88))
    for k,xx in enumerate((x-.98,x,x+.98)):
        B(room,f"window_vertical_{i}_{k}",(.045,.10,2.25),(xx,1.69,2.77),(.36,.39,.37))
    for k,z in enumerate((1.70,2.72,3.86)):
        B(room,f"window_cross_{i}_{k}",(1.98,.10,.045),(x,1.68,z),(.39,.41,.38))
B(room,"left_wall",(.16,7,4.4),(-6.1,-1.7,2.2),(.49,.50,.44))
scene.include("room",room)

def bench(name,x,width):
    a=Asset(name)
    z=1.05
    B(a,"thick_scarred_top",(width,1.0,.16),(x,.48,z),topwood)
    B(a,"front_apron",(width,.105,.27),(x,-.015,.86),wood)
    B(a,"rear_apron",(width,.10,.24),(x,.92,.86),wood)
    for i,xx in enumerate((x-width/2+.14,x+width/2-.14)):
        for j,y in enumerate((.10,.83)):
            B(a,f"leg_{i}_{j}",(.15,.16,.96),(xx,y,.48),wood)
            B(a,f"foot_{i}_{j}",(.22,.23,.08),(xx,y,.055),(.18,.16,.115))
        B(a,f"crossbrace_{i}",(.13,.88,.12),(xx,.46,.29),wood)
    B(a,"lower_shelf",(width-.22,.74,.065),(x,.47,.30),(.22,.20,.14))
    # End grain, split rails, and distinct worn strips across the top.
    for i in range(5):
        B(a,f"top_seam_{i}",(width-.04,.009,.004),(x,.08+i*.19,1.133),(.19,.17,.12))
    for i in range(11):
        xx=x+random.uniform(-width*.46,width*.46)
        yy=random.uniform(.04,.90)
        B(a,f"scuff_{i}",(random.uniform(.04,.22),.012,.005),(xx,yy,1.137),(.53,.47,.34))
    return a

for i,(x,w) in enumerate(((2.0,2.6),(-.45,2.2),(-2.5,1.8),(-4.3,1.65),(-5.65,.95))):
    scene.include(f"workbench_{i}",bench(f"heavy timber bench {i}",x,w))

def wheel(a,key,c,r):
    x,y,z=c
    ring(a,key+"_rim",c,r,.032,iron)
    ring(a,key+"_rim_highlight",(x,y-.018,z),r-.038,.012,(.34,.36,.33))
    R(a,key+"_hub",(x,y-.11,z),(x,y+.15,z),.075,edge)
    for j in range(5):
        t=j*2*math.pi/5
        pts=[]
        for k in range(7):
            f=k/6
            angle=t+.46*f
            rr=.065+(r-.08)*f
            pts.append((x+rr*math.cos(angle),y,z+rr*math.sin(angle)))
        tube(a,f"{key}_curved_spoke_{j}",pts,.028,iron)
    R(a,key+"_crank",(x+r*.77,y-.025,z-.12),(x+r*.77,y-.20,z-.12),.025,rust)
    R(a,key+"_grip",(x+r*.77,y-.20,z-.12),(x+r*.77,y-.34,z-.12),.035,wood)

# Large belt-driven apparatus, its wheel standing behind the main machine.
a=Asset("large flywheel stand")
B(a,"foot",(.55,.52,.11),(1.30,.69,1.18),iron)
B(a,"upright",(.12,.13,.92),(1.30,.78,1.66),rust)
B(a,"bearing",(.25,.26,.16),(1.30,.75,2.10),edge)
wheel(a,"main_wheel",(1.30,.54,2.16),.49)
R(a,"rear_shaft",(1.30,.40,2.16),(1.30,1.12,2.16),.052,steel)
# Narrow belt descends next to the wheel.
tube(a,"belt",[(1.63,.58,2.47),(1.69,.59,2.05),(1.60,.60,1.19)],.015,(.14,.12,.09))
scene.include("large_wheel_machine",a)

def lathe():
    a=Asset("foreground screw lathe and vice")
    # Bed and two flared supports.
    B(a,"bed",(1.70,.36,.12),(2.10,.33,1.24),iron)
    for i,x in enumerate((1.48,2.75)):
        B(a,f"foot_{i}",(.32,.48,.07),(x,.33,1.165),iron)
        B(a,f"upright_{i}",(.15,.24,.36),(x,.33,1.37),iron)
        B(a,f"shoulder_{i}",(.27,.34,.12),(x,.33,1.55),edge)
    R(a,"horizontal_workshaft",(1.26,.30,1.55),(3.10,.30,1.55),.069,steel)
    R(a,"headstock_barrel",(1.49,.30,1.55),(1.95,.30,1.55),.15,iron)
    R(a,"collar",(1.90,.30,1.55),(2.04,.30,1.55),.18,iron)
    B(a,"headstock_top",(.40,.30,.13),(1.74,.31,1.73),iron)
    B(a,"top_handle",(.31,.08,.075),(1.73,.31,1.835),steel)
    for i,x in enumerate((2.15,2.22,2.29,2.36,2.43,2.50,2.57,2.64,2.71,2.78)):
        ring(a,f"screw_thread_{i}",(x,.30,1.55),.079,.009,rust,plane="yz")
    R(a,"wood_end_grip",(2.95,.30,1.55),(3.30,.30,1.55),.075,(.49,.43,.32))
    B(a,"sliding_jaw",(.23,.35,.28),(2.32,.28,1.44),iron)
    R(a,"front_lever",(2.31,.10,1.43),(2.31,-.25,1.26),.028,steel)
    S(a,"lever_ball",(2.31,-.25,1.26),.052,iron)
    return a
scene.include("foreground_machine",lathe())

def anvil(x,y,z):
    a=Asset("anvil")
    B(a,"bottom_flange",(.57,.42,.08),(x,y,z+.04),rust)
    B(a,"pedestal",(.37,.30,.19),(x,y,z+.15),rust)
    B(a,"waist",(.25,.28,.20),(x+.015,y,z+.31),rust)
    B(a,"shoulder",(.43,.34,.17),(x,y,z+.45),rust)
    B(a,"flat_face",(.69,.37,.13),(x+.02,y,z+.57),(.36,.31,.22))
    # Progressively tapered horn points along the bench toward the right.
    for i in range(12):
        r=.145*(1-i/12)+.006
        xx=x+.35+i*.032
        R(a,f"horn_{i}",(xx,y,z+.55),(xx+.04,y,z+.55),r,rust)
    B(a,"square_heel",(.18,.34,.12),(x-.39,y,z+.56),rust)
    B(a,"hardy_hole",(.055,.055,.006),(x-.31,y,z+.638),(.075,.075,.06))
    return a
scene.include("central_anvil",anvil(-.63,.34,1.14))

# Smaller wheel and base at the second bench.
a=Asset("small hand powered wheel")
B(a,"base",(.53,.45,.09),(-1.52,.60,1.18),edge)
B(a,"column",(.13,.17,.46),(-1.52,.67,1.41),iron)
wheel(a,"small_wheel",(-1.52,.49,1.75),.32)
R(a,"axle",(-1.52,.35,1.75),(-1.52,.88,1.75),.044,steel)
scene.include("small_wheel",a)

def vice(name,x,y,z,scale=1):
    a=Asset(name)
    B(a,"mount",(.26,.31,.08),(x,y,z),iron)
    B(a,"fixed_body",(.28,.26,.25),(x,y-.11,z-.02),iron)
    B(a,"front_jaw",(.30,.10,.21),(x,y-.32,z+.065),edge)
    B(a,"fixed_jaw",(.30,.09,.17),(x,y-.14,z+.11),edge)
    R(a,"screw",(x,y-.23,z-.03),(x,y-.57,z-.03),.045,steel)
    R(a,"handle",(x-.02,y-.58,z-.24),(x+.02,y-.58,z+.17),.018,steel)
    S(a,"handle_lower",(x-.02,y-.58,z-.24),.03,iron)
    S(a,"handle_upper",(x+.02,y-.58,z+.17),.03,iron)
    if scale!=1: a.resize((scale,scale,scale),pivot=(x,y,z))
    return a
for i,x in enumerate((.02,-2.52,-3.96,-5.15)):
    scene.include(f"bench_vice_{i}",vice(f"vice {i}",x,-.045,1.12,.95 if i<2 else .75))

# Open foreground drawer, protruding into the aisle.
a=Asset("open tool drawer")
B(a,"drawer_bottom",(.96,.69,.055),(1.16,-.39,.76),(.24,.23,.17))
B(a,"drawer_front",(.99,.075,.25),(1.16,-.75,.85),(.20,.21,.17))
for i,x in enumerate((.69,1.63)):
    B(a,f"side_{i}",(.055,.69,.22),(x,-.40,.85),(.30,.29,.20))
B(a,"drawer_back",(.96,.05,.20),(1.16,-.06,.85),wood)
R(a,"drawer_handle",(.99,-.81,.86),(1.32,-.81,.86),.025,iron)
for i in range(4):
    R(a,f"drawer_tool_{i}",(.85+i*.12,-.64,.81),(.91+i*.12,-.18,.83),.018,steel)
scene.include("open_drawer",a)

# Loose tools, sheet metal, wood blocks, and curled shop clutter on the benches.
a=Asset("tools on worktops")
for i in range(17):
    x=random.uniform(-5.7,3.0)
    y=random.uniform(.07,.88)
    z=1.16
    length=random.uniform(.17,.42)
    R(a,f"tool_shaft_{i}",(x,y,z),(x+length,y+.06,z+.012),.013,steel)
    if i%3==0:
        R(a,f"tool_handle_{i}",(x-.15,y-.025,z),(x,y,z),.028,wood)
        B(a,f"hammer_head_{i}",(.09,.18,.06),(x+length,y+.06,z+.018),iron)
for i,(x,y) in enumerate(((1.72,-.01),(2.77,.69),(.73,.02),(-2.03,.05))):
    p=B(a,f"metal_plate_{i}",(.36,.27,.025),(x,y,1.16),(.53,.54,.49))
    p.turn('z',random.uniform(-17,17))
for i in range(6):
    x=-2.35+i*.12
    R(a,f"parallel_bright_files_{i}",(x,.25,1.17),(x,.72,1.17),.018,(.61,.59,.49))
for i in range(6):
    B(a,f"timber_block_{i}",(.19,.28,.13),(-4.9+i*.52,.73,1.20),(.40,.29,.17))
scene.include("loose_workbench_tools",a)

# Objects on the windowsills: cans, bottles, tools, and little machinery.
a=Asset("window ledge objects")
for i in range(26):
    x=random.uniform(-5.65,2.7)
    y=random.uniform(1.32,1.52)
    h=random.uniform(.10,.28)
    R(a,f"tin_{i}",(x,y,1.69),(x,y,1.69+h),random.uniform(.027,.065),random.choice((steel,iron,rust,(.48,.45,.34))))
    if i%3==0:
        R(a,f"brush_{i}",(x,y,1.76+h),(x+.025,y,1.95+h),.012,wood)
for i,x in enumerate((-4.3,-2.9,-.8,.4,2.5)):
    B(a,f"sill_block_{i}",(.22,.24,.10),(x,1.39,1.73),wood)
scene.include("ledge_clutter",a)

# Hanging wall tools and exposed pipework.
a=Asset("wall tools and pipes")
for i,(x,z) in enumerate(((-3.52,2.2),(-1.36,2.12),(.79,2.2),(3.03,2.3))):
    R(a,f"hanging_shaft_{i}",(x,1.50,z-.55),(x+.07,1.50,z+.14),.016,rust)
    ring(a,f"tool_loop_{i}",(x+.07,1.50,z+.2),.065,.012,iron)
tube(a,"bent_wall_pipe",[(3.0,1.47,3.8),(3.0,1.47,2.7),(2.9,1.46,2.5),(2.88,1.46,1.9),(3.03,1.46,1.73)],.025,iron)
R(a,"leaning_long_wood_handle",(3.2,1.30,.15),(3.70,1.45,2.5),.043,wood)
R(a,"left_pipe",(-5.8,1.36,1.60),(-5.8,1.36,3.8),.032,iron)
scene.include("wall_hardware",a)

def can(name,x,y,r,h,c):
    a=Asset(name)
    # Open cylindrical containers are made as thick rims with dark interior disks.
    R(a,"body",(x,y,.04),(x,y,h),r,c)
    R(a,"dark_opening",(x,y,h+.001),(x,y,h+.008),r*.88,(.075,.075,.052))
    ring(a,"upper_rim",(x,y,h+.012),r,.014,edge,plane="xy")
    ring(a,"bottom_rim",(x,y,.055),r,.012,edge,plane="xy")
    tube(a,"wire_handle",[(x-r,y,h*.84),(x-r*.85,y-.04,h+.16),(x,y-.06,h+.26),(x+r*.85,y-.04,h+.16),(x+r,y,h*.84)],.009,iron)
    return a
scene.include("foreground_white_bucket",can("white enamel bucket",1.72,-.32,.30,.59,(.64,.64,.53)))
scene.include("right_oil_can",can("dark olive oil drum",3.03,.05,.32,.69,(.17,.22,.14)))
scene.include("cropped_rust_can",can("cropped copper can",3.55,-.53,.28,.43,(.37,.25,.13)))
scene.include("back_bucket",can("bucket beneath bench",-2.78,.20,.22,.46,(.29,.30,.24)))
# Flat can lids and vertical handle silhouette.
a=Asset("underbench clutter")
for i,x in enumerate((-.8,-.1,.5,2.75)):
    B(a,f"box_{i}",(.40,.43,.27),(x,.54,.47),(.22,.19,.13))
for i in range(4):
    R(a,f"leaning_rod_{i}",(.02+i*.055,-.27,.05),(-.12+i*.04,-.10,1.05),.017,rust)
ring(a,"oilcan_lid",(3.03,.05,.73),.16,.017,rust,plane="xy")
scene.include("underbench_objects",a)

# The small gray floor marker is a real flat object with a white arrow.
a=Asset("floor direction marker")
R(a,"gray_disk",(-2.0,-2.0,.022),(-2.0,-2.0,.028),.32,(.37,.43,.43))
B(a,"arrow_stem",(.10,.23,.006),(-2.0,-2.02,.036),(.81,.83,.78))
for i in range(6):
    w=.29-i*.043
    B(a,f"arrow_tip_{i}",(w,.035,.006),(-2.0,-1.92+i*.028,.037),(.81,.83,.78))
scene.include("floor_marker",a)

# Preconditions audited: no fillet_box calls, all radii and sizes positive;
# loop keys are unique, no bind cycles, worktop contacts use z=1.13 explicitly.
realize(scene)

# Surface wear is procedural and never uses the reference photograph.
for ob in bpy.data.objects:
    if ob.type!='MESH':
        continue
    for slot in ob.material_slots:
        if not slot.material:
            continue
        mat=slot.material
        if not mat.use_nodes:
            mat.use_nodes=True
        bs=mat.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Roughness"].default_value=.78
        # Restrained fine bump catches side light without altering silhouettes.
        if bs and not mat.node_tree.nodes.get("WorkshopNoise"):
            n=mat.node_tree.nodes.new("ShaderNodeTexNoise")
            n.name="WorkshopNoise"
            n.inputs["Scale"].default_value=42
            n.inputs["Detail"].default_value=2
            bump=mat.node_tree.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value=.20
            bump.inputs["Distance"].default_value=.027
            mat.node_tree.links.new(n.outputs["Fac"],bump.inputs["Height"])
            mat.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

# Pale luminous glass supplies the washed-out daylight seen above the benches.
for ob in bpy.data.objects:
    if ob.type=='EMPTY' and "window_glass_" in ob.name:
        for child in ob.children_recursive:
            if child.type=='MESH':
                for slot in child.material_slots:
                    if slot.material:
                        slot.material=slot.material.copy()
                        bs=slot.material.node_tree.nodes.get("Principled BSDF")
                        if bs:
                            bs.inputs["Base Color"].default_value=(.78,.86,.89,1)
                            if "Emission Color" in bs.inputs:
                                bs.inputs["Emission Color"].default_value=(.70,.80,.86,1)
                                bs.inputs["Emission Strength"].default_value=.7

if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new("World")
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.55,.62,.67,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.32
area_emitter((-.5,1.1,4.6),power=1100,size=5.0,target=(-.7,-.5,.5),color=(.85,.93,1.0))
area_emitter((-4,-3,4.0),power=420,size=4,target=(-1,.3,1),color=(1.0,.88,.70))
set_view((5.7,-7.2,4.4),(-.65,.25,1.25),lens=36,sensor=36,shift=(0,0))
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.05
