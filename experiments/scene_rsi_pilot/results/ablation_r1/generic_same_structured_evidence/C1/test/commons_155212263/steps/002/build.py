from sceneact import *
import bpy, math, random

random.seed(21)
scene = Scene("Old metalworking workshop")

# Reference anchors (estimated): anvil (.43,.39), large wheel (.67,.25),
# small wheel (.35,.29), drawer (.60,.71), floor marker (.13,.71).
# Camera looks down the length of a wall bench from its right foreground.
CAMERA_POSITION = (6.6, -7.7, 4.5)
CAMERA_TARGET = (-.65, .15, 1.20)
CAMERA_LENS = 43
BENCH_HEIGHT = .91
WALL_Y = .97
DAYLIGHT_POWER = 1000
FILL_POWER = 400

wood = (.27,.225,.155)
oldwood = (.36,.31,.225)
iron = (.14,.16,.155)
steel = (.32,.34,.32)
rust = (.24,.17,.105)
plaster = (.46,.51,.48)

def block(parent, key, size, pos, col):
    return parent.include(key, box(size, center=pos, color=col))

def bar(parent, key, radius, start, end, col=iron):
    return parent.include(key, rod(radius, start=start, end=end, color=col))

def ring(parent, key, center, radius, thickness, axis='x', col=iron):
    # Modest path resolution keeps construction economical.
    points = []
    for i in range(25):
        a = math.tau*i/24
        c, s = radius*math.cos(a), radius*math.sin(a)
        if axis == 'x':
            p = (center[0], center[1]+c, center[2]+s)
        elif axis == 'y':
            p = (center[0]+c, center[1], center[2]+s)
        else:
            p = (center[0]+c, center[1]+s, center[2])
        points.append(p)
    return parent.include(key, sweep_tube(points=points, radius=thickness, color=col))

# Runtime repair: substantially fewer primitives and path vertices, no booleans,
# no individual nails, no per-material procedural node graphs, fast Eevee rendering.
# Major geometry, object positions, and camera remain consistent with the first build.
floor = Asset("Pine floorboards")
for i in range(36):
    block(floor, f"plank_{i}", (13,.215,.055),
          (-.6,-5.5+i*.22,-.033),
          (.39+random.uniform(-.03,.03),
           .32+random.uniform(-.025,.025),
           .225+random.uniform(-.02,.02)))
scene.include("floor", floor)

architecture = Asset("Plastered walls")
block(architecture,"lower_wall",(12,.23,1.30),(-1,1.12,.65),plaster)
block(architecture,"upper_wall",(12,.23,.4),(-1,1.12,3.62),plaster)
block(architecture,"left_return",(.18,4.6,3.8),(-6.35,-.95,1.87),(.48,.49,.44))
for i,x in enumerate((-5.7,-3.35,-.95,1.50,3.65)):
    block(architecture,f"pier_{i}",(.29,.25,2.25),(x,1.12,2.4),plaster)
scene.include("architecture",architecture)

windows = Asset("Workshop windows")
for i,(x,w) in enumerate(((-4.53,2.04),(-2.15,2.10),(.28,2.14),(2.58,1.82))):
    win = Asset(f"Window {i}")
    block(win,"pane",(w,.035,1.67),(x,1.12,2.58),(.84,.90,.94))
    block(win,"sill",(w+.24,.39,.09),(x,.91,1.72),(.32,.32,.27))
    for j,xx in enumerate((x-w/2,x+w/2,x+.12)):
        block(win,f"vertical_{j}",(.052,.12,1.77),(xx,1.01,2.58),(.33,.37,.35))
    block(win,"crossbar",(w,.10,.045),(x,1.005,2.47),(.35,.37,.33))
    windows.include(f"window_{i}",win)
scene.include("windows",windows)

walltools=Asset("Wall pipes and handles")
for i,x in enumerate((-5.5,-3.,-.5,2.25)):
    walltools.include(f"pipe_{i}",sweep_tube(
        points=[(x,.79,3.30),(x,.79,2.30),(x+.18,.79,2.20),
                (x+.18,.79,1.83),(x+.29,.79,1.68)],
        radius=.022,color=rust))
bar(walltools,"long_handle",.032,(3.55,.76,.7),(4.06,.85,3.45),(.24,.14,.07))
bar(walltools,"short_handle",.029,(3.19,.72,.18),(3.63,.82,1.38),oldwood)
scene.include("wall_tools",walltools)

bench=Asset("Heavy timber workbench")
block(bench,"top",(9.62,1.04,.135),(-1.02,.17,BENCH_HEIGHT),oldwood)
block(bench,"apron",(9.62,.10,.18),(-1.02,-.33,.77),wood)
block(bench,"lower_shelf",(9.62,.75,.055),(-1.02,.17,.24),(.21,.20,.145))
for i in range(9):
    x=-5.7+i*1.07
    for j,y in enumerate((-.25,.56)):
        block(bench,f"leg_{i}_{j}",(.13,.15,.82),(x,y,.41),(.20,.18,.125))
    block(bench,f"cross_member_{i}",(.12,.92,.10),(x,.15,.24),wood)
scene.include("bench",bench)

lathe=Asset("Foreground lathe")
for j,y in enumerate((-.08,.22)):
    bar(lathe,f"bed_rail_{j}",.058,(.75,y,1.075),(3.75,y,1.075),steel)
for i,x in enumerate((.88,3.43)):
    block(lathe,f"foot_{i}",(.24,.57,.08),(x,.07,.995),iron)
    block(lathe,f"standard_{i}",(.13,.25,.28),(x,.07,1.15),iron)
block(lathe,"headstock_base",(.54,.48,.11),(1.18,.07,1.18),iron)
block(lathe,"headstock",(.30,.32,.39),(1.13,.07,1.38),iron)
bar(lathe,"head_spindle",.105,(.91,.07,1.48),(1.62,.07,1.48),steel)
bar(lathe,"chuck",.15,(1.52,.07,1.48),(1.70,.07,1.48),iron)
block(lathe,"tail_base",(.52,.46,.09),(2.89,.07,1.18),iron)
block(lathe,"tailstock",(.37,.30,.27),(2.91,.07,1.36),iron)
bar(lathe,"tail_spindle",.058,(2.50,.07,1.47),(3.43,.07,1.47),steel)
bar(lathe,"workpiece",.052,(1.70,.07,1.48),(2.51,.07,1.48),(.40,.33,.21))
ring(lathe,"tail_wheel",(3.40,.07,1.47),.15,.022)
bar(lathe,"tail_spoke",.017,(3.40,-.07,1.47),(3.40,.21,1.47))
bar(lathe,"tail_grip",.025,(3.40,.21,1.47),(3.59,.21,1.47),oldwood)
block(lathe,"carriage",(.41,.48,.10),(2.13,.03,1.18),steel)
block(lathe,"tool_post",(.13,.12,.19),(2.12,.03,1.32),iron)
bar(lathe,"tool_lever",.018,(1.96,.03,1.43),(2.29,.03,1.43))
bar(lathe,"feed_screw",.027,(2.12,-.23,1.17),(2.12,-.43,1.17),steel)
ring(lathe,"feed_wheel",(2.12,-.44,1.17),.13,.018,'y')
scene.include("lathe",lathe)

machine=Asset("Large flywheel machine")
block(machine,"foot",(.60,.52,.09),(.62,.47,1.02),iron)
block(machine,"column",(.17,.19,.84),(.62,.47,1.46),iron)
bar(machine,"axle",.067,(.37,.42,2.04),(.93,.42,2.04),steel)
for i,x in enumerate((.52,.67)):
    ring(machine,f"rim_{i}",(x,.42,2.04),.48,.035)
bar(machine,"hub",.115,(.44,.42,2.04),(.74,.42,2.04))
for k in range(6):
    points=[]
    for j in range(5):
        r=.085+j*.091
        a=k*math.tau/6+.48*j/4
        points.append((.51,.42+r*math.cos(a),2.04+r*math.sin(a)))
    machine.include(f"curved_spoke_{k}",sweep_tube(points=points,radius=.032,color=iron))
bar(machine,"crank",.028,(.40,.42,2.04),(.40,.63,1.84),steel)
bar(machine,"grip",.034,(.40,.63,1.84),(.19,.63,1.84),oldwood)
scene.include("flywheel",machine)

anvil=Asset("Anvil on timber block")
block(anvil,"timber",(.60,.63,.78),(-.75,-.17,.40),(.20,.17,.115))
block(anvil,"base",(.65,.48,.10),(-.75,-.17,.97),rust)
block(anvil,"lower",(.43,.36,.14),(-.75,-.17,1.07),rust)
block(anvil,"waist",(.25,.27,.25),(-.75,-.17,1.23),rust)
block(anvil,"shoulder",(.49,.36,.13),(-.75,-.17,1.38),rust)
block(anvil,"face",(.68,.38,.075),(-.78,-.17,1.465),(.37,.32,.24))
for i in range(6):
    x=-.44+i*.07
    bar(anvil,f"horn_{i}",.135*(1-i/6.5),(x,-.17,1.402),(x+.08,-.17,1.402),rust)
block(anvil,"heel",(.19,.29,.11),(-1.17,-.17,1.435),rust)
scene.include("anvil",anvil)

small=Asset("Small blue wheel apparatus")
block(small,"base",(.57,.48,.09),(-2.05,.23,1.01),iron)
block(small,"support",(.13,.15,.48),(-2.05,.23,1.28),steel)
ring(small,"rim",(-2.05,.12,1.62),.31,.027,'y',(.20,.32,.35))
bar(small,"hub",.065,(-2.05,-.01,1.62),(-2.05,.26,1.62),steel)
for i in range(6):
    a=i*math.tau/6
    bar(small,f"spoke_{i}",.018,(-2.05,.12,1.62),
        (-2.05+.28*math.cos(a),.12,1.62+.28*math.sin(a)),(.21,.33,.35))
scene.include("small_wheel",small)

for i,x in enumerate((.08,-2.85,-4.32)):
    vise=Asset(f"Bench vise {i}")
    block(vise,"mount",(.30,.31,.10),(x,-.28,1.01),iron)
    block(vise,"body",(.30,.34,.20),(x,-.37,1.13),iron)
    for j,xx in enumerate((x-.13,x+.13)):
        block(vise,f"jaw_{j}",(.075,.30,.16),(xx,-.38,1.24),steel)
    bar(vise,"screw",.045,(x,-.35,1.12),(x,-.75,1.12),steel)
    bar(vise,"handle",.017,(x,-.76,.94),(x,-.76,1.31),steel)
    scene.include(f"vise_{i}",vise)

drawer=Asset("Open wooden tool drawer")
block(drawer,"bottom",(.98,.67,.045),(1.71,-.68,.59),(.18,.17,.12))
block(drawer,"front",(.99,.075,.27),(1.71,-1,.73),wood)
block(drawer,"back",(.99,.055,.23),(1.71,-.36,.71),wood)
for i,x in enumerate((1.23,2.19)):
    block(drawer,f"side_{i}",(.055,.67,.26),(x,-.68,.72),oldwood)
bar(drawer,"handle",.029,(1.59,-1.055,.73),(1.83,-1.055,.73))
for i in range(3):
    bar(drawer,f"loose_tool_{i}",.017,(1.35+i*.20,-.85,.63),(1.50+i*.18,-.43,.65),steel)
scene.include("drawer",drawer)

tools=Asset("Tools and metal plates on bench")
for i in range(12):
    x=random.uniform(-5.65,3.45)
    y=random.uniform(-.23,.60)
    length=random.uniform(.15,.43)
    bar(tools,f"shaft_{i}",.014,(x,y,.997),(x+length,y+.05,1.003),steel)
    if i%2==0:
        bar(tools,f"grip_{i}",.027,(x-.12,y-.015,1.00),(x,y,1.00),oldwood)
    else:
        block(tools,f"hammer_head_{i}",(.07,.17,.065),(x+length,y+.05,1.025),iron)
for i,(x,y) in enumerate(((1.08,-.17),(2.65,-.23),(-1.56,.03),(-3.44,.15))):
    block(tools,f"plate_{i}",(.40,.25,.018),(x,y,1.00),(.46,.46,.40))
for i in range(5):
    block(tools,f"wood_block_{i}",(.26,.15,.10),(-5.5+i*.71,.42,1.045),(.40,.29,.16))
scene.include("bench_tools",tools)

ledge=Asset("Jars and tools on window sills")
for i in range(15):
    x=-5.7+i*.62
    h=random.uniform(.09,.24)
    r=random.uniform(.025,.051)
    col=random.choice([(.22,.24,.20),(.45,.44,.35),(.28,.22,.15),(.55,.56,.50)])
    bar(ledge,f"jar_{i}",r,(x,.86,1.77),(x,.86,1.77+h),col)
    bar(ledge,f"neck_{i}",r*.53,(x,.86,1.77+h),(x,.86,1.81+h))
for i in range(5):
    x=-5.6+i*1.12
    bar(ledge,f"upright_tool_{i}",.014,(x,.90,1.78),(x+.04,.90,2.14))
scene.include("sill_inventory",ledge)

storage=Asset("Under bench buckets and boxes")
for i,(x,y,r,h) in enumerate(((2.20,-.22,.28,.53),(3.18,.02,.34,.59),
                             (-3.05,.15,.20,.40),(-4.75,.15,.21,.45))):
    col=(.39,.38,.29) if i%2==0 else (.19,.24,.18)
    bar(storage,f"container_{i}",r,(x,y,.015),(x,y,h),col)
    bar(storage,f"dark_opening_{i}",r*.86,(x,y,h+.001),(x,y,h+.005),(.12,.13,.10))
    ring(storage,f"rim_{i}",(x,y,h),r,.018,'z')
    if i==0:
        block(storage,"pale_label",(.30,.018,.26),(x,y-r-.005,.28),(.64,.62,.50))
for i in range(4):
    block(storage,f"box_{i}",(.48,.45,.39),(-4.5+i*1.03,.31,.43),(.15,.17,.13))
scene.include("storage",storage)

leaning=Asset("Long tools leaning at bench")
for i,x in enumerate((-.30,-.05,-3.7)):
    bar(leaning,f"shaft_{i}",.021,(x,-.48,.05),(x+.10,-.43,.96),rust)
    block(leaning,f"head_{i}",(.13,.07,.13),(x+.10,-.43,.98),iron)
scene.include("leaning_tools",leaning)

marker=Asset("Floor arrow marker")
bar(marker,"disc",.23,(-2,-2.04,.002),(-2,-2.04,.009),(.30,.36,.36))
block(marker,"stem",(.12,.19,.004),(-2,-2.06,.014),(.77,.79,.75))
for i in range(4):
    block(marker,f"tip_{i}",(.23-i*.05,.04,.004),(-2,-1.99+i*.035,.014),(.77,.79,.75))
scene.include("floor_marker",marker)

# API audit: no fillet radii or boolean operations; positive dimensions/radii;
# all rod endpoints differ, sweep samples are consecutive distinct points,
# and repeated siblings use indexed keys. World and lights follow realize.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient world")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
background.inputs[0].default_value=(.62,.69,.73,1)
background.inputs[1].default_value=.35

# Shared finish edits apply consistently to every object using that finish.
for mat in bpy.data.materials:
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Roughness"].default_value=.78

# Window-only edits copy materials and traverse their semantic parent.
window_group=bpy.data.objects.get("windows")
if window_group:
    for obj in window_group.children_recursive:
        if obj.type=="MESH" and obj.dimensions.y<.055 and obj.dimensions.z>1.3:
            for slot in obj.material_slots:
                if slot.material:
                    slot.material=slot.material.copy()
                    shader=slot.material.node_tree.nodes.get("Principled BSDF")
                    if shader:
                        shader.inputs["Emission Color"].default_value=(.78,.86,.92,1)
                        shader.inputs["Emission Strength"].default_value=.65

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
area_emitter((-.9,.55,3.35),power=DAYLIGHT_POWER,size=5,
             target=(-.6,-1,.2),color=(.84,.91,1))
area_emitter((3,-3,4.6),power=FILL_POWER,size=4,
             target=(0,0,.8),color=(1,.88,.72))
area_emitter((-5,-1,3),power=250,size=2.5,
             target=(-3,0,1),color=(.85,.91,1))

sc.render.engine="BLENDER_EEVEE_NEXT"
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.look="AgX - Medium High Contrast"
sc.render.image_settings.file_format="PNG"
