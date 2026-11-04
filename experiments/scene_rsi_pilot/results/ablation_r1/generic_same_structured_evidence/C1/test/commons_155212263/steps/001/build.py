from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(21)
scene = Scene("Old metalworking shop")

# Estimated image anchors: back bench (.06,.30), anvil (.43,.39),
# main flywheel (.67,.25), front bench edge (.82,.70), floor arrow (.13,.71).
# Camera looks diagonally along the workbench; right foreground is deliberately cropped.
CAMERA_POSITION = (6.6, -7.7, 4.5)
CAMERA_TARGET = (-.65, .15, 1.20)
CAMERA_LENS = 43
BENCH_HEIGHT = .91
WALL_Y = .97
wood = (.27,.225,.155)
oldwood = (.36,.31,.225)
iron = (.14,.16,.155)
steel = (.32,.34,.32)
rust = (.24,.17,.105)
plaster = (.46,.51,.48)

def add(parent, key, node):
    return parent.include(key, node)

def block(parent,key,size,pos,col):
    return add(parent,key,box(size,center=pos,color=col))

def bar(parent,key,r,a,b,col=iron):
    return add(parent,key,rod(r,start=a,end=b,color=col))

def ring(parent,key,center,r,t,axis='x',col=iron):
    points=[]
    for i in range(65):
        a=2*math.pi*i/64
        if axis=='x':
            points.append((center[0],center[1]+r*math.cos(a),center[2]+r*math.sin(a)))
        elif axis=='y':
            points.append((center[0]+r*math.cos(a),center[1],center[2]+r*math.sin(a)))
        else:
            points.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),center[2]))
    add(parent,key,sweep_tube(points=points,radius=t,color=col))

# Separate long floorboards and joints.
floor = Asset("Worn pine floor")
for j in range(49):
    y=-6+j*.177
    block(floor,f"board_{j}",(13,.171,.055),(-.6,y,-.033),
          (.37+random.random()*.085,.30+random.random()*.055,.205+random.random()*.04))
    for k in range(4):
        x=-5.5+k*3.1+(j%3)*.38
        block(floor,f"joint_{j}_{k}",(.009,.171,.003),(x,y,-.003),(.15,.135,.10))
        for dy in (-.055,.055):
            bar(floor,f"nail_{j}_{k}_{dy}",.006,(x+.035,y+dy,0),(x+.035,y+dy,.003),iron)
scene.include("floor",floor)

# Plastered rear wall, with luminous window recesses.
architecture=Asset("Workshop walls and windows")
block(architecture,"lower_wall",(12,.23,1.30),(-1,WALL_Y+.15,.65),plaster)
block(architecture,"upper_wall",(12,.23,.40),(-1,WALL_Y+.15,3.62),plaster)
for i,x in enumerate((-5.7,-3.35,-.95,1.50,3.65)):
    block(architecture,f"pier_{i}",(.29,.25,2.25),(x,WALL_Y+.15,2.40),(.43,.48,.45))
for i,(x,w) in enumerate(((-4.53,2.04),(-2.15,2.10),(.28,2.14),(2.58,1.82))):
    window=Asset(f"Window {i}")
    block(window,"bright_glass",(w,.035,1.67),(x,1.12,2.58),(.83,.89,.90))
    for side in (-1,1):
        block(window,f"jamb_{side}",(.065,.14,1.77),(x+side*w/2,1.01,2.58),oldwood)
    block(window,"sill",(w+.24,.39,.09),(x,.91,1.72),(.32,.32,.27))
    block(window,"top",(w+.10,.13,.07),(x,1.01,3.43),oldwood)
    block(window,"mullion",(.047,.10,1.67),(x+.12,1.005,2.58),(.33,.37,.35))
    block(window,"crossbar",(w,.10,.045),(x,1.005,2.47),(.35,.37,.33))
    architecture.include(f"window_{i}",window)
# Left return wall.
block(architecture,"left_wall",(.18,4.6,3.8),(-6.35,-.95,1.87),(.48,.49,.44))
scene.include("architecture",architecture)

# Wall mounted pipes and a long leaning handle.
pipes=Asset("Wall pipes and hand tools")
for i,x in enumerate((-5.5,-3.0,-.5,2.25)):
    add(pipes,f"bent_pipe_{i}",sweep_tube(
        points=[(x,.79,2.96),(x,.79,2.30),(x+.18,.79,2.20),(x+.18,.79,1.83),
                (x+.29,.79,1.68)],radius=.022,color=rust))
    for z in (2.20,2.85):
        block(pipes,f"clip_{i}_{z}",(.09,.07,.035),(x,.79,z),steel)
bar(pipes,"leaning_wood_handle",.032,(3.55,.76,.70),(4.06,.85,3.45),(.24,.14,.07))
bar(pipes,"short_handle",.029,(3.19,.72,.18),(3.63,.82,1.38),oldwood)
scene.include("wall_tools",pipes)

# Continuous irregular workbench, with individual heavy supports.
bench=Asset("Long timber workbench")
for i in range(9):
    x=-5.3+i*1.07
    block(bench,f"top_{i}",(1.055,1.04,.135),(x,.17,BENCH_HEIGHT),oldwood)
    block(bench,f"front_apron_{i}",(1.05,.10,.18),(x,-.33,.77),wood)
    for y in (-.25,.56):
        block(bench,f"leg_{i}_{y}",(.13,.15,.82),(x-.40,y,.41),(.20,.18,.125))
    block(bench,f"stretcher_{i}",(.12,.92,.10),(x-.40,.15,.24),wood)
    block(bench,f"lower_shelf_{i}",(.99,.80,.055),(x,.15,.24),(.21,.20,.145))
scene.include("bench",bench)

# Foreground lathe bed, headstock and tailstock.
lathe=Asset("Foreground metal lathe")
for j,y in enumerate((-.08,.22)):
    bar(lathe,f"bed_rail_{j}",.058,(.75,y,1.075),(3.75,y,1.075),steel)
for i,x in enumerate((.88,3.43)):
    block(lathe,f"foot_{i}",(.24,.57,.08),(x,.07,.995),iron)
    block(lathe,f"standard_{i}",(.13,.25,.28),(x,.07,1.15),iron)
block(lathe,"headstock_base",(.54,.48,.11),(1.18,.07,1.18),iron)
block(lathe,"headstock_upright",(.30,.32,.39),(1.13,.07,1.38),iron)
bar(lathe,"head_spindle",.105,(.91,.07,1.48),(1.62,.07,1.48),steel)
bar(lathe,"chuck",.15,(1.52,.07,1.48),(1.70,.07,1.48),iron)
block(lathe,"tailstock_base",(.52,.46,.09),(2.89,.07,1.18),iron)
block(lathe,"tailstock_body",(.37,.30,.27),(2.91,.07,1.36),iron)
bar(lathe,"tail_spindle",.058,(2.50,.07,1.47),(3.43,.07,1.47),steel)
bar(lathe,"work_piece",.052,(1.70,.07,1.48),(2.51,.07,1.48),(.40,.33,.21))
ring(lathe,"tail_handwheel",(3.40,.07,1.47),.15,.022,'x',iron)
bar(lathe,"tail_handwheel_spoke",.017,(3.40,-.07,1.47),(3.40,.21,1.47),iron)
bar(lathe,"tail_crank",.021,(3.40,.21,1.47),(3.59,.21,1.47),oldwood)
block(lathe,"sliding_carriage",(.41,.48,.10),(2.13,.03,1.18),steel)
block(lathe,"tool_post",(.13,.12,.19),(2.12,.03,1.32),iron)
bar(lathe,"tool_post_lever",.018,(1.96,.03,1.43),(2.29,.03,1.43),iron)
bar(lathe,"carriage_feed",.027,(2.12,-.23,1.17),(2.12,-.43,1.17),steel)
ring(lathe,"carriage_handwheel",(2.12,-.44,1.17),.13,.018,'y',iron)
scene.include("lathe",lathe)

# Tall cast iron flywheel machine behind the lathe.
wheelmachine=Asset("Large flywheel machine")
block(wheelmachine,"foot",(.60,.52,.09),(.62,.47,1.02),iron)
block(wheelmachine,"column",(.17,.19,.84),(.62,.47,1.46),iron)
bar(wheelmachine,"axle",.067,(.37,.42,2.04),(.93,.42,2.04),steel)
for i,x in enumerate((.52,.67)):
    ring(wheelmachine,f"rim_{i}",(x,.42,2.04),.48,.035,'x',iron)
    ring(wheelmachine,f"inner_rim_{i}",(x,.42,2.04),.414,.014,'x',steel)
bar(wheelmachine,"hub",.115,(.44,.42,2.04),(.74,.42,2.04),iron)
for k in range(6):
    a=k*math.tau/6
    pts=[]
    for j in range(8):
        r=.085+j*.052
        ang=a+.48*j/7
        pts.append((.51,.42+r*math.cos(ang),2.04+r*math.sin(ang)))
    add(wheelmachine,f"curved_spoke_{k}",sweep_tube(points=pts,radius=.032,color=iron))
bar(wheelmachine,"crank",.028,(.40,.42,2.04),(.40,.63,1.84),steel)
bar(wheelmachine,"crank_grip",.034,(.40,.63,1.84),(.19,.63,1.84),oldwood)
scene.include("flywheel",wheelmachine)

# Anvil on a thick timber block.
anvil=Asset("Anvil and timber stand")
block(anvil,"stump",(.60,.63,.78),(-.75,-.17,.40),(.20,.17,.115))
for i in range(4):
    block(anvil,f"grain_split_{i}",(.008,.014,.62),(-.99+i*.13,-.493,.42),(.10,.09,.06))
block(anvil,"base",(.65,.48,.10),(-.75,-.17,.97),rust)
block(anvil,"lower",(.43,.36,.14),(-.75,-.17,1.07),rust)
block(anvil,"waist",(.25,.27,.25),(-.75,-.17,1.23),rust)
block(anvil,"shoulder",(.49,.36,.13),(-.75,-.17,1.38),rust)
block(anvil,"face",(.68,.38,.075),(-.78,-.17,1.465),(.37,.32,.24))
# Tapered horn made of short overlapping coaxial sections.
for i in range(12):
    x=-.44+i*.035
    r=.135*(1-i/13)
    bar(anvil,f"horn_{i}",r,(x,-.17,1.402),(x+.045,-.17,1.402),rust)
block(anvil,"heel",(.19,.29,.11),(-1.17,-.17,1.435),rust)
scene.include("anvil",anvil)

# Smaller blue flywheel farther along the workbench.
small=Asset("Small blue wheel apparatus")
block(small,"base",(.57,.48,.09),(-2.05,.23,1.01),iron)
block(small,"upright",(.13,.15,.48),(-2.05,.23,1.28),steel)
ring(small,"rim",(-2.05,.12,1.62),.31,.027,'y',(.20,.32,.35))
ring(small,"rim_inner",(-2.05,.12,1.62),.263,.013,'y',steel)
bar(small,"hub",.065,(-2.05,-.01,1.62),(-2.05,.26,1.62),steel)
for k in range(6):
    a=k*math.tau/6
    bar(small,f"spoke_{k}",.017,(-2.05,.12,1.62),
        (-2.05+.28*math.cos(a),.12,1.62+.28*math.sin(a)),(.21,.33,.35))
scene.include("small_wheel",small)

# Vises at the front edge.
for i,x in enumerate((.08,-2.85,-4.32)):
    vise=Asset(f"Bench vise {i}")
    block(vise,"mount",(.30,.31,.10),(x,-.28,1.01),iron)
    block(vise,"body",(.30,.34,.20),(x,-.37,1.13),iron)
    for j,xx in enumerate((x-.13,x+.13)):
        block(vise,f"jaw_{j}",(.075,.30,.16),(xx,-.38,1.24),steel)
    bar(vise,"screw",.045,(x,-.35,1.12),(x,-.75,1.12),steel)
    bar(vise,"handle",.017,(x,-.76,.94),(x,-.76,1.31),steel)
    for z in (.94,1.31):
        add(vise,f"knob_{z}",ball(.030,center=(x,-.76,z),color=steel))
    scene.include(f"vise_{i}",vise)

# Wide open wooden drawer projecting into the foreground.
drawer=Asset("Open foreground tool drawer")
block(drawer,"bottom",(.98,.67,.045),(1.71,-.68,.59),(.18,.17,.12))
block(drawer,"front",(.99,.075,.27),(1.71,-1.00,.73),wood)
block(drawer,"back",(.99,.055,.23),(1.71,-.36,.71),wood)
for i,x in enumerate((1.23,2.19)):
    block(drawer,f"side_{i}",(.055,.67,.26),(x,-.68,.72),oldwood)
bar(drawer,"handle",.029,(1.59,-1.055,.73),(1.83,-1.055,.73),iron)
for i in range(6):
    bar(drawer,f"contents_{i}",.017,(1.31+i*.12,-.85,.63),(1.48+i*.09,-.43,.65),steel)
scene.include("open_drawer",drawer)

# Economical editable tools, plates, wooden blocks and bottles.
tools=Asset("Bench tools and loose hardware")
for i in range(18):
    x=random.uniform(-5.65,3.45)
    y=random.uniform(-.23,.60)
    length=random.uniform(.15,.43)
    bar(tools,f"tool_shaft_{i}",.014,(x,y,.997),(x+length,y+.05,1.003),steel)
    if i%3==0:
        bar(tools,f"tool_handle_{i}",.027,(x-.12,y-.015,1.00),(x,y,1.00),oldwood)
    elif i%3==1:
        block(tools,f"hammer_head_{i}",(.07,.17,.065),(x+length,y+.05,1.025),iron)
for i,(x,y) in enumerate(((1.08,-.17),(2.65,-.23),(-1.56,.03),(-3.44,.15))):
    block(tools,f"flat_plate_{i}",(.40,.25,.018),(x,y,1.00),(.46,.46,.40))
    for j in range(2):
        bar(tools,f"plate_bolt_{i}_{j}",.022,(x-.12+j*.24,y,1.009),(x-.12+j*.24,y,1.018),iron)
for i in range(9):
    x=-5.5+i*.41
    block(tools,f"wood_block_{i}",(.26,.15,.10),(x,.42,1.045),(.40,.29,.16))
scene.include("loose_tools",tools)

# Window ledge inventory.
ledge=Asset("Window ledge jars and tools")
for i in range(25):
    x=random.uniform(-5.8,3.25)
    h=random.uniform(.09,.24)
    r=random.uniform(.025,.051)
    col=random.choice([(.22,.24,.20),(.45,.44,.35),(.28,.22,.15),(.55,.56,.50)])
    bar(ledge,f"jar_{i}",r,(x,.86,1.77),(x,.86,1.77+h),col)
    bar(ledge,f"neck_{i}",r*.53,(x,.86,1.77+h),(x,.86,1.81+h),iron)
for i in range(8):
    x=-5.6+i*.62
    bar(ledge,f"upright_tool_{i}",.014,(x,.90,1.78),(x+.04,.90,2.14),iron)
scene.include("sill_inventory",ledge)

# Buckets, drums and dark storage underneath the bench.
storage=Asset("Under bench storage")
for i,(x,y,r,h) in enumerate(((2.20,-.22,.28,.53),(3.18,.02,.34,.59),(-3.05,.15,.20,.40),(-4.75,.15,.21,.45))):
    col=(.39,.38,.29) if i%2==0 else (.19,.24,.18)
    bar(storage,f"container_{i}",r,(x,y,.015),(x,y,h),col)
    ring(storage,f"rim_{i}",(x,y,h),r,.018,'z',iron)
    bar(storage,f"dark_top_{i}",r*.86,(x,y,h+.001),(x,y,h+.004),(.12,.13,.10))
    if i==0:
        block(storage,"pale_bucket_label",(.30,.018,.26),(x,y-r-.005,.28),(.64,.62,.50))
        ring(storage,"bucket_bail",(x,y,.51),.24,.010,'y',steel)
for i in range(5):
    x=-4.5+i*1.03
    block(storage,f"stored_box_{i}",(.48,.45,.39),(x,.31,.43),(.15,.17,.13))
scene.include("storage",storage)

# A few long tools leaning against the front supports.
leaning=Asset("Long handled tools")
for i,x in enumerate((-.30,-.05,-3.7)):
    bar(leaning,f"shaft_{i}",.021,(x,-.48,.05),(x+.10,-.43,.96),rust)
    block(leaning,f"head_{i}",(.13,.07,.13),(x+.10,-.43,.98),iron)
scene.include("leaning_tools",leaning)

# Small grey floor marker with white directional arrow.
marker=Asset("Floor direction marker")
bar(marker,"disc",.23,(-2.0,-2.04,.002),(-2.0,-2.04,.009),(.30,.36,.36))
block(marker,"arrow_stem",(.12,.19,.004),(-2.0,-2.06,.014),(.77,.79,.75))
for i in range(5):
    block(marker,f"arrow_tip_{i}",(.23-i*.037,.035,.004),(-2.0,-1.99+i*.029,.014),(.77,.79,.75))
scene.include("floor_marker",marker)

# API audit: all sizes/radii positive; all sibling keys unique.
# No fillet primitives used. Material edits traverse meshes after realization.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient world")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.62,.69,.73,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.35

# Subtle procedural wear, preserving the distinct modeled parts.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bsdf=nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    base=bsdf.inputs["Base Color"].default_value[:]
    bsdf.inputs["Roughness"].default_value=.76
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=18
    noise.inputs["Detail"].default_value=3
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.17
    ramp.color_ramp.elements[1].position=.84
    ramp.color_ramp.elements[0].color=tuple(c*.64 for c in base[:3])+(1,)
    ramp.color_ramp.elements[1].color=tuple(min(c*1.16,1) for c in base[:3])+(1,)
    mat.node_tree.links.new(noise.outputs["Fac"],ramp.inputs[0])
    mat.node_tree.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.19
    bump.inputs["Distance"].default_value=.018
    mat.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    mat.node_tree.links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    if max(base[:3])-min(base[:3])<.055 and sum(base[:3])/3<.45:
        bsdf.inputs["Metallic"].default_value=.48

# Give the window panes a soft overexposed daylight appearance.
group=bpy.data.objects.get("architecture")
if group:
    for obj in group.children_recursive:
        if obj.type=='MESH' and obj.dimensions.y<.055 and obj.dimensions.z>1.3:
            for slot in obj.material_slots:
                if slot.material:
                    slot.material=slot.material.copy()
                    bsdf=slot.material.node_tree.nodes.get("Principled BSDF")
                    if bsdf:
                        bsdf.inputs["Emission Color"].default_value=(.78,.86,.92,1)
                        bsdf.inputs["Emission Strength"].default_value=.65

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
area_emitter((-.9,.55,3.35),power=1000,size=5.0,target=(-.6,-1.0,.2),color=(.84,.91,1.0))
area_emitter((3,-3,4.6),power=400,size=4.0,target=(0,0,.8),color=(1.0,.88,.72))
area_emitter((-5,-1,3),power=250,size=2.5,target=(-3,0,1),color=(.85,.91,1.0))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.render.image_settings.file_format='PNG'
