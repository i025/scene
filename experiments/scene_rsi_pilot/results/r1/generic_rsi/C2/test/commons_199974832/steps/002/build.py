from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(24)
scene=Scene("Antique woodworking tool room")

# Visual estimates, reference/render: upper shelf left (.18,.34)/(.23,.36),
# shelf corner (.77,.33)/(.75,.35), bowl (.65,.89)/(.66,.83).
# Largest error is pale tool surfaces: preserve SceneAct diffuse colors when
# enabling shader nodes. Framing correction: lens 31 -> 36 enlarges coverage,
# moving left shelf edge left and foreground tools toward the lower crop.
# Preserve shelf corner alignment and the four horizontal shelf bands.
# Assemblies: solid plaster, window/racks, shelf banks, hanging squares,
# crowded solid workbench, planes, blades, oil pot, bottle and shavings.
# Openings remain in handles and between square arms; bench is a filled slab.
# Room depth and individual tool proportions remain uncertain.

BACK=2.35
CAMERA=(-.45,-5.35,2.62)
TARGET=(.05,1.05,1.99)
LENS=36
SHELF_Z=(1.19,1.70,2.23,2.78)
WOOD=(.38,.19,.065)
HONEY=(.56,.32,.12)
DARKWOOD=(.22,.105,.04)
IRON=(.105,.12,.115)
STEEL=(.35,.37,.34)
WALL=(.76,.78,.72)

def add(p,n,o):
    p.include(n,o)
    return o

def block(p,n,size,center,color,rotation=None):
    o=box(size=size,center=center,color=color)
    if rotation:
        o.turn(euler=rotation)
    return add(p,n,o)

def bar(p,n,a,b,r=.012,color=IRON):
    return add(p,n,rod(radius=r,start=a,end=b,color=color))

architecture=Asset("Architecture")
# Extend plaster above the frame, eliminating the unintended open sky band.
block(architecture,"back plaster",(5.85,.13,7),(0,BACK+.1,3.35),WALL)
block(architecture,"right plaster",(.13,5.7,7),(2.9,-.4,3.35),(.79,.79,.72))
block(architecture,"left plaster",(.12,5.5,7),(-2.9,-.3,3.35),(.72,.76,.71))
block(architecture,"floor",(5.8,7,.12),(0,-.7,-.07),(.27,.24,.19))
scene.include("Room",architecture)

window=Asset("Tall left window")
block(window,"blue glass",(.035,1.9,2.73),(-2.815,1.15,2.22),(.42,.72,.81))
for yy in (.2,.82,1.45,2.1):
    block(window,"upright"+str(yy),(.09,.055,2.85),(-2.76,yy,2.22),(.75,.79,.75))
for zz in (.8,1.62,2.53,3.67):
    block(window,"cross"+str(zz),(.10,2,.055),(-2.75,1.15,zz),(.78,.80,.72))
scene.include("Window",window)

shelves=Asset("Wall shelf system")
for i,z in enumerate(SHELF_Z):
    block(shelves,f"back plank {i}",(4.58,.45,.065),(.20,2.08,z),HONEY)
    block(shelves,f"back pale front edge {i}",(4.6,.035,.032),(.2,1.84,z+.005),(.65,.43,.20))
    block(shelves,f"right return {i}",(.48,3.8,.068),(2.61,.25,z),HONEY)
    for x in (-1.87,.05,2.17):
        bar(shelves,f"bracket {i} {x}",(x,2.28,z-.29),(x,1.94,z-.035),.014)
for x in (-1.89,2.18):
    block(shelves,"standard"+str(x),(.045,.045,2),(x,2.29,1.83),(.20,.22,.20))
scene.include("Shelving",shelves)

def plane(name,x,y,z,length=.38,width=.12,wood=WOOD,angle=0,metal=False,detail=1):
    p=Asset(name)
    c=STEEL if metal else wood
    block(p,"solid sole",(length,width,.065),(0,0,.034),c)
    block(p,"body",(length*.91,width*.94,.092),(0,0,.102),c)
    block(p,"inclined iron",(.065,width*.85,.18),(.035,0,.17),IRON,(0,-27,0))
    if detail:
        bar(p,"tote left",(-length*.30,0,.13),(-length*.32,0,.29),.021,DARKWOOD)
        bar(p,"tote grip",(-length*.32,0,.29),(-length*.13,0,.31),.024,DARKWOOD)
        bar(p,"tote right",(-length*.13,0,.31),(-length*.08,0,.15),.019,DARKWOOD)
        add(p,"front knob",ball(.037,center=(length*.30,0,.17),color=DARKWOOD))
    p.turn(axis="z",degrees=angle,pivot=(0,0,0))
    p.move((x,y,z))
    scene.include(name,p)

for row,z in enumerate(SHELF_Z):
    count=(15,16,17,36)[row]
    for j in range(count):
        x=-1.97+j*4.35/(count-1)
        if row==3:
            h=random.uniform(.14,.29)
            p=Asset(f"Top molding plane {j}")
            block(p,"wood stock",(.079,.20,h),(x,2.07,z+.035+h/2),
                  random.choice([WOOD,HONEY,DARKWOOD]))
            block(p,"protruding iron",(.035,.055,h*.65),(x,2.045,z+h*.75),
                  IRON,(0,random.uniform(-13,13),0))
            scene.include(f"Top molding plane {j}",p)
        elif j%4==1:
            h=random.uniform(.14,.30)
            p=Asset(f"Upright shelf tool {row} {j}")
            block(p,"wood body",(.16,.25,h),(x,2.08,z+.035+h/2),
                  random.choice([WOOD,HONEY,DARKWOOD]))
            block(p,"blade",(.035,.09,.15),(x,2.02,z+h+.04),IRON,(0,-18,0))
            scene.include(f"Upright shelf tool {row} {j}",p)
        else:
            plane(f"Back plane {row} {j}",x,2.02,z+.035,
                  length=random.uniform(.23,.38),width=.13,
                  wood=random.choice([WOOD,HONEY,DARKWOOD]),
                  angle=random.uniform(-9,9),detail=0)

for row,z in enumerate(SHELF_Z):
    for j in range(10):
        y=-1.32+j*.36
        if j%3:
            plane(f"Right plane {row} {j}",2.60,y,z+.04,
                  length=random.uniform(.24,.38),width=.15,
                  wood=random.choice([WOOD,HONEY,DARKWOOD]),
                  angle=90+random.uniform(-9,9),detail=0)
        else:
            p=Asset(f"Right tall block {row} {j}")
            h=random.uniform(.2,.34)
            block(p,"stock",(.24,.19,h),(2.61,y,z+.035+h/2),WOOD)
            block(p,"iron",(.09,.04,.15),(2.59,y,z+h+.04),IRON)
            scene.include(f"Right tall block {row} {j}",p)

walltools=Asset("Hanging measuring tools")
def strip(name,a,b,width=.065,color=IRON,depth=.028):
    a,b=Vector(a),Vector(b)
    d=b-a
    o=box((width,depth,d.length),center=tuple((a+b)/2),color=color)
    o.turn(axis="y",degrees=math.degrees(math.atan2(d.x,d.z)))
    add(walltools,name,o)

for i,(cx,cz,s) in enumerate([(-.85,3.49,.90),(-.55,3.65,.82),(-.22,3.83,.74)]):
    strip(f"square left {i}",(cx-s*.58,2.30,cz-.36),(cx,2.30,cz+.26),.083)
    strip(f"square right {i}",(cx,2.30,cz+.26),(cx+s*.60,2.30,cz-.34),.083)
    strip(f"square inner {i}",(cx-s*.34,2.285,cz-.36),(cx+.02,2.285,cz+.04),.024,STEEL)
for i in range(3):
    cx=.63+i*.28
    top=3.92-i*.20
    strip(f"divider left {i}",(cx-.16,2.29,top-.65),(cx,2.29,top),.025,DARKWOOD)
    strip(f"divider right {i}",(cx,2.29,top),(cx+.15,2.29,top-.66),.025,DARKWOOD)
strip("long black square vertical",(.35,2.30,3.04),(.35,2.30,4.06),.065)
strip("long black square foot",(.35,2.30,4.06),(.83,2.30,4.06),.065)
block(walltools,"wood level",(.10,.08,.92),(1.50,2.27,3.57),DARKWOOD)
block(walltools,"level cap",(.31,.10,.09),(1.50,2.23,3.98),DARKWOOD)
block(walltools,"level base",(.27,.10,.07),(1.50,2.23,3.15),DARKWOOD)
block(walltools,"hammer handle",(.055,.065,.52),(1.89,2.22,3.18),WOOD)
block(walltools,"hammer head",(.35,.09,.075),(1.89,2.20,3.44),IRON)
for i in range(2):
    xx=.75+i*.13
    bar(walltools,f"brass divider A{i}",(xx,2.24,3.12),(xx-.12,2.24,2.88),.011,(.49,.42,.22))
    bar(walltools,f"brass divider B{i}",(xx,2.24,3.12),(xx+.12,2.24,2.88),.011,(.49,.42,.22))
scene.include("Wall measuring collection",walltools)

rack=Asset("Window tool racks")
for z in (1.30,2.08,3):
    block(rack,f"rack rail {z}",(.22,1.86,.055),(-2.59,1.15,z),HONEY)
    for j in range(7):
        yy=.30+j*.25
        h=random.uniform(.22,.43)
        block(rack,f"blade {z} {j}",(.035,.035,.30),(-2.55,yy,z+.13),STEEL)
        add(rack,f"handle {z} {j}",
            rod(radius=.035,length=h,center=(-2.55,yy,z+.30+h/2),
                color=random.choice([WOOD,HONEY,DARKWOOD])))
scene.include("Window hand tools",rack)

bench=Asset("Foreground workbench")
block(bench,"thick top",(4.95,2.54,.15),(-.12,-.79,.82),(.38,.28,.15))
block(bench,"front apron",(4.8,.12,.37),(-.12,-2,.58),DARKWOOD)
for xx in (-2.12,1.92):
    for yy in (-1.75,.13):
        block(bench,f"leg {xx} {yy}",(.15,.15,.78),(xx,yy,.39),DARKWOOD)
block(bench,"rear raised board",(2.2,.22,.13),(.35,.30,1.01),HONEY)
scene.include("Workbench",bench)

for i,(x,y,l,ang) in enumerate([
    (-1.68,-.43,.65,-72),(-1.23,-.48,.63,-73),(-.82,-.31,.55,-64),
    (.50,.06,.70,5),(1.10,.26,.59,-8),(1.85,-.32,.60,80),
    (.93,-1.25,.80,-35),(-.24,-1.37,.66,-17)]):
    plane(f"Foreground bench plane {i}",x,y,.90,length=l,width=.20,
          wood=random.choice([WOOD,HONEY,DARKWOOD]),angle=ang,
          metal=i in (0,1,2,6),detail=1)

loose=Asset("Loose bench tools")
for j in range(6):
    x=-2.18+j*.20
    o=block(loose,f"long steel blade {j}",(.105,.78,.035),(x,-1.10,.96+j*.009),(.33,.35,.31))
    o.turn(axis="z",degrees=-19+j*3)
    add(loose,f"wood handle {j}",
        rod(radius=.052,length=.23,center=(x-.11,-1.57,1.01),axis="+y",color=HONEY))
for j in range(7):
    x=random.uniform(-1.5,1.7)
    y=random.uniform(-1.75,.1)
    o=block(loose,f"loose wooden ruler {j}",(random.uniform(.5,.92),.055,.025),(x,y,.98),HONEY)
    o.turn(axis="z",degrees=random.uniform(-55,55))
    if j<4:
        block(loose,f"steel chisel {j}",(.32,.042,.018),(x-.15,y+.06,1.015),STEEL)
bar(loose,"mallet handle",(1.15,-1.82,1),(1.72,-.92,1.05),.037,HONEY)
o=block(loose,"mallet head",(.43,.20,.20),(1.60,-1.10,1.08),HONEY)
o.turn(axis="z",degrees=-30)
scene.include("Scattered tools",loose)

containers=Asset("Bench containers")
add(containers,"black oil pot",rod(radius=.15,length=.24,center=(-.47,-.07,1.05),color=IRON))
add(containers,"pot rim",rod(radius=.17,length=.025,center=(-.47,-.07,1.18),color=STEEL))
add(containers,"pot lid",rod(radius=.115,length=.025,center=(-.47,-.07,1.21),color=IRON))
bar(containers,"pot wire left",(-.61,-.07,1.16),(-.55,-.07,1.44),.012,STEEL)
bar(containers,"pot wire top",(-.55,-.07,1.44),(-.37,-.07,1.44),.012,STEEL)
bar(containers,"pot wire right",(-.37,-.07,1.44),(-.32,-.07,1.16),.012,STEEL)
add(containers,"bottle body",rod(radius=.078,length=.29,center=(.16,-.26,1.06),color=(.48,.53,.42)))
add(containers,"bottle shoulder",ball(radius=.077,center=(.16,-.26,1.20),color=(.48,.53,.42)))
add(containers,"bottle neck",rod(radius=.036,length=.12,center=(.16,-.26,1.28),color=(.52,.57,.47)))
block(containers,"bottle paper label",(.126,.012,.12),(.16,-.335,1.07),(.70,.69,.54))
add(containers,"shavings bowl",rod(radius=.29,length=.085,center=(.65,-1.28,1),color=IRON))
for j in range(9):
    x=.65+random.uniform(-.21,.21)
    y=-1.28+random.uniform(-.19,.19)
    pts=[(x+.045*math.cos(t),y+.035*math.sin(t),1.065+.015*k)
         for k,t in enumerate((0,1.4,2.8,4.2,5.6))]
    add(containers,f"curl {j}",sweep_tube(points=pts,radius=.006,color=(.53,.55,.49)))
scene.include("Oil bottle pot and shavings",containers)

sign=Asset("Small shelf labels")
o=block(sign,"yellow placard",(.26,.025,.23),(-1.27,2.07,3.01),(.82,.56,.13))
o.turn(axis="y",degrees=12)
for j in range(12):
    block(sign,f"cream label {j}",(.13,.012,.025),(-1.85+j*.36,1.817,1.19),(.78,.76,.61))
scene.include("Shelf labels",sign)

# All dimensions are positive; bars have distinct endpoints; include keys unique.
realize(scene)

for material in bpy.data.materials:
    # Enabling nodes creates a default shader; explicitly transfer original RGB.
    color=tuple(material.diffuse_color)
    material.use_nodes=True
    nodes=material.node_tree.nodes
    links=material.node_tree.links
    bs=nodes.get("Principled BSDF")
    if bs is None:
        bs=nodes.new("ShaderNodeBsdfPrincipled")
        out=nodes.get("Material Output")
        if out is None:
            out=nodes.new("ShaderNodeOutputMaterial")
        links.new(bs.outputs["BSDF"],out.inputs["Surface"])
    bs.inputs["Base Color"].default_value=color
    bs.inputs["Roughness"].default_value=.77
    if color[0]>color[1]*1.25 and color[1]>color[2]*1.25:
        tex=nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=5
        tex.inputs["Detail"].default_value=2
        mapping=nodes.new("ShaderNodeVectorMath")
        mapping.operation="MULTIPLY"
        mapping.inputs[1].default_value=(3,40,7)
        coord=nodes.new("ShaderNodeTexCoord")
        links.new(coord.outputs["Generated"],mapping.inputs[0])
        links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
        ramp=nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.12
        ramp.color_ramp.elements[0].color=(color[0]*.64,color[1]*.62,color[2]*.58,1)
        ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[1].color=(color[0]*1.16,color[1]*1.13,color[2]*1.10,1)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    elif abs(color[0]-color[1])<.06 and color[0]<.45:
        bs.inputs["Metallic"].default_value=.55
        bs.inputs["Roughness"].default_value=.48

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("AmbientWorld")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.76,.83,.89,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.42
set_view(position=CAMERA,target=TARGET,lens=LENS,sensor=36)
# Keep illumination fixed while repairing the surface colors.
area_emitter(position=(-2.35,-.15,3.6),power=1050,size=3.2,
             target=(.1,1,1.3),color=(.86,.94,1))
area_emitter(position=(.4,-2.8,4),power=650,size=4,
             target=(0,1,1.4),color=(1,.94,.82))
sc.view_settings.view_transform="AgX"
