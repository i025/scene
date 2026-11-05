from sceneact import *
import bpy, math, random
random.seed(19)
scene = Scene(name="Antique toolmaker workshop")
wood=(.36,.20,.080)
edge=(.49,.29,.12)
pale=(.58,.39,.19)
dark=(.20,.105,.042)
steel=(.22,.28,.29)
silver=(.43,.49,.49)
iron=(.045,.075,.080)
brass=(.25,.25,.105)
serial=0

def add(name,node):
    global serial
    serial+=1
    scene.include(name+"_%05d"%serial,node)
    return node
def B(name,size,p,c=wood):
    return add(name,box(size=size,center=p,color=c))
def R(name,r,a,b,c=steel):
    return add(name,rod(radius=r,start=a,end=b,color=c))
def S(name,pts,r=.01,c=steel):
    return add(name,sweep_tube(points=pts,radius=r,color=c))
def E(name,p,scale,c):
    n=ball(radius=1,center=p,color=c)
    n.resize(scale)
    return add(name,n)
def loop(name,p,rx,ry,r=.009,c=steel,vertical=False):
    pts=[]
    for j in range(49):
        a=j*math.tau/48
        pts.append((p[0]+rx*math.cos(a),
                    p[1] if vertical else p[1]+ry*math.sin(a),
                    p[2]+ry*math.sin(a) if vertical else p[2]))
    return S(name,pts,r,c)

# Individually planked pine walls and floor.
B("floor backing",(7,7,.10),(0,0,-.08),dark)
for i in range(24):
    x=-3.5+i*.30
    B("floor plank",(.292,6,.05),(x,-1,-.015),
      (.30+random.random()*.07,.17+random.random()*.045,.075+random.random()*.025))
B("wall backing",(7,.12,4.8),(0,.96,2),dark)
for i in range(21):
    x=-3.4+i*.34
    B("wall plank",(.333,.065,4.7),(x,.865,2),
      (.29+random.random()*.09,.145+random.random()*.065,.055+random.random()*.03))
    for k in range(5):
        z=random.uniform(.2,3.4)
        E("pine knot",(x+random.uniform(-.11,.11),.829,z),
          (.012+random.random()*.011,.003,.019),(.095,.043,.018))
    for k in range(5):
        xx=x+random.uniform(-.14,.14)
        S("fine vertical grain",[(xx,.829,.1),(xx+.008,.828,1.4),
                                (xx-.006,.828,2.6),(xx,.828,3.6)],.0013,
          (.21,.105,.039))
for x in (-1.85,.18,1.90):
    B("wall bead",(.025,.026,4.6),(x,.816,2),dark)

# Workbench and its dark open carcass.
B("bench slab",(3.05,1.24,.105),(0,.04,1.56),edge)
B("abraded front edge",(3.10,.055,.055),(0,-.588,1.56),pale)
B("rear lip",(3.05,.035,.045),(0,.645,1.63),dark)
for x in (-1.38,1.38):
    for y in (-.45,.51):
        B("bench leg",(.115,.13,1.48),(x,y,.75),wood)
    B("side apron",(.10,1.12,.23),(x,.02,1.36),wood)
B("back stretcher",(2.8,.10,.12),(0,.49,.30),dark)
B("front rail",(2.9,.08,.075),(0,-.47,1.04),dark)
B("left drawer recess",(.82,.84,1.13),(-1,.02,.88),(.080,.049,.022))
for x in (-1.44,-.55):
    B("left cabinet upright",(.065,.98,1.18),(x,-.06,.89),edge)
for z in (.33,.70,1.07,1.43):
    B("drawer runner",(.88,.98,.045),(-1,-.04,z),wood)
B("right drawer recess",(.76,.83,.96),(1.04,.02,.95),(.075,.05,.025))
for x in (.64,1.44):
    B("right cabinet upright",(.060,.98,.98),(x,-.04,.91),edge)

def pull(name,x,y,z,w=.20):
    for dx in (-w/2,w/2):
        E(name+" screw",(x+dx,y,z+.025),(.017,.008,.017),iron)
    S(name+" handle",[(x-w/2,y-.015,z+.025),(x-w*.43,y-.042,z-.027),
      (x-w*.22,y-.055,z-.055),(x+w*.22,y-.055,z-.055),
      (x+w*.43,y-.042,z-.027),(x+w/2,y-.015,z+.025)],.011,iron)

def drawer(name,x,w,z,front,depth=.72,h=.20):
    B(name+" base",(w,depth,.03),(x,front+depth/2,z-h/2),(.32,.21,.095))
    B(name+" face",(w+.025,.060,h),(x,front,z),edge)
    for xx in (x-w/2+.022,x+w/2-.022):
        B(name+" side",(.043,depth,h-.025),(xx,front+depth/2,z),pale)
    B(name+" back",(w,.03,h-.025),(x,front+depth,z),wood)
    pull(name,x,front-.040,z,.23 if w>.9 else .20)
    for k in range(45):
        xx=x+random.uniform(-w*.47,w*.47)
        zz=z+random.uniform(-h*.43,h*.43)
        B("drawer scars",(random.uniform(.004,.065),.002,random.uniform(.001,.008)),
          (xx,front-.031,zz),random.choice([dark,wood,pale]))

drawer("left top",-1,.78,1.27,-.89,.73,.21)
drawer("left middle",-1,.78,.91,-.98,.76,.21)
drawer("left bottom",-1,.78,.40,-1.02,.79,.21)
drawer("center",-.02,1.18,1.23,-.88,.79,.25)
drawer("right top",1.06,.72,1.28,-.85,.75,.19)
drawer("right lower",1.06,.72,.60,-.93,.76,.20)

# Dense contents visible in each open drawer.
for k in range(15):
    x=-.54+k*.074
    y=random.uniform(-.66,-.31)
    R("wooden handle",.029,(x,y,1.27),(x+.025,y+.22,1.29),
      (.30+random.random()*.16,.15+random.random()*.09,.055))
    R("chisel shank",.009,(x,y-.17,1.26),(x,y+.025,1.28),steel)
    R("handle ferrule",.030,(x,y+.01,1.273),(x+.003,y+.04,1.277),brass)
for k in range(30):
    x=random.uniform(-1.32,-.67)
    y=random.uniform(-.85,-.46)
    R("left drawer thin tools",.009,(x,y,1.29),(x+.015,y+.15,1.30),
      random.choice([pale,steel,dark]))
for k in range(13):
    x=-1.32+k*.051
    R("bottom drawer strips",.012,(x,-.96,.43),(x,-.54,.44),pale)
for k in range(50):
    x=random.uniform(.75,1.35); y=random.uniform(-.77,-.34)
    loop("drawer metal fittings",(x,y,1.30),.012,.020,.0035,iron)
for k in range(7):
    R("right drawer files",.008,(.77+k*.08,-.81,.62),
      (.80+k*.08,-.41,.63),steel)
E("small tin in drawer",(-.31,-.48,1.32),(.090,.10,.082),steel)
loop("tin rim",(-.31,-.48,1.39),.075,.075,.009,silver)

# Coarse worn protective mats.
B("left cloth",(1.51,.99,.012),(-.65,-.025,1.626),(.27,.28,.245))
B("right cloth",(1.05,.98,.012),(.80,.025,1.626),(.30,.31,.27))
B("rear rag",(.57,.43,.008),(.02,.37,1.635),(.33,.30,.23))
for k in range(160):
    x=random.uniform(-1.44,1.44); y=random.uniform(-.51,.57)
    B("mat small mark",(random.uniform(.008,.055),random.uniform(.002,.015),.001),
      (x,y,1.638),random.choice([(.19,.20,.17),(.39,.37,.29),(.25,.25,.20)]))

# Two antique green-brass oil cans.
for x in (-1.19,-.77):
    E("oil can body",(x,.44,1.715),(.15,.125,.095),(.22,.25,.095))
    R("oil can base",.139,(x,.44,1.64),(x,.44,1.66),brass)
    R("oil can neck",.060,(x,.44,1.76),(x,.44,1.82),brass)
    R("oil can collar",.068,(x,.44,1.795),(x,.44,1.815),silver)
    for j in range(15):
        radius=.039*(1-j/16)+.004
        R("tapering nozzle",radius,(x-j*.0006,.44,1.815+j*.017),
          (x-(j+1)*.0006,.44,1.835+j*.017),steel)

# Open cylindrical cup.
R("cup bottom",.076,(-.43,.25,1.645),(-.43,.25,1.655),brass)
for j in range(48):
    a=j*math.tau/48
    x=-.43+.076*math.cos(a); y=.25+.076*math.sin(a)
    R("cup wall",.0055,(x,y,1.65),(x,y,1.81),brass)
loop("cup rim",(-.43,.25,1.815),.077,.077,.007,silver)

# Scissors, pliers, dividers, and tongs, laid separately.
def path(name,pts,r=.012,c=steel):
    return S(name,[(x,y,1.657+z) for x,y,z in pts],r,c)
def scissors(x,y,L=.43,spread=.057):
    for side in (-1,1):
        loop("scissor finger ring",(x+side*spread,y-.13,1.66),
             .043,.062,.010,silver)
        path("scissor arm",[(x+side*spread,y-.072,0),
          (x+side*.021,y+.075,.008),(x-side*.025,y+L-.12,.008)],.011)
    R("scissor rivet",.020,(x,y+.075,1.66),(x,y+.075,1.68),silver)
scissors(-.68,-.31,.48,.062)
scissors(-.49,-.34,.37,.052)
path("tong", [(-1.39,-.40,0),(-1.31,-.28,0),(-1.28,-.10,0),
              (-1.24,.05,0),(-1.12,.11,0)],.018)
path("tong", [(-1.25,-.42,0),(-1.23,-.23,0),(-1.19,-.08,.006),
              (-1.22,.04,.006),(-1.14,.15,0)],.017,silver)
path("pliers", [(-1.11,-.38,0),(-1.13,-.21,0),(-1.06,-.04,0),
                (-1.02,.12,0),(-.94,.16,0)],.015)
path("pliers", [(-.97,-.37,0),(-1.03,-.17,0),(-1.06,-.04,.01),
                (-1.10,.11,0),(-1.03,.15,0)],.015)
for x in (-.22,-.045,.14):
    for side in (-1,1):
        path("slender pincers",[(x+side*.027,-.37,0),
          (x+side*.039,-.12,0),(x+side*.026,.07,.003),
          (x+side*.065,.20,0)],.011,silver if side==1 else steel)
    R("pincer hinge",.020,(x,.045,1.658),(x,.045,1.68),steel)
for x in (-.34,.04):
    S("rectangular iron grip",[(x-.030,-.39,1.66),(x-.030,-.14,1.66),
      (x+.030,-.14,1.66),(x+.030,-.39,1.66),(x-.030,-.39,1.66)],.010,silver)
    R("grip shank",.014,(x,-.14,1.66),(x,.07,1.66),steel)
# A horizontal hammer along the back.
R("hammer handle",.019,(-.27,.48,1.665),(.14,.48,1.665),wood)
B("hammer head",(.13,.065,.055),(-.29,.48,1.69),steel)

for i,x in enumerate((.37,.53,.70,.88)):
    y=-.10+random.uniform(-.02,.02)
    B("chisel blade",(.045,.30,.014),(x,y+.10,1.66),silver)
    R("chisel tang",.012,(x,y-.18,1.67),(x,y+.015,1.67),steel)
    E("chisel handle",(x,y-.24,1.68),(.031,.095,.027),pale)
    R("chisel ferrule",.023,(x,y-.18,1.67),(x,y-.135,1.67),brass)

# Wooden hand plane with its tilted iron and pale sharpening stone.
B("plane sole",(.30,.46,.035),(1.18,-.12,1.66),dark)
B("plane body",(.27,.38,.070),(1.18,-.10,1.706),(.31,.22,.125))
n=B("plane iron",(.23,.105,.02),(1.18,-.08,1.765),steel)
n.turn("+x",25)
B("plane handle",(.15,.045,.09),(1.18,.045,1.765),dark)
n=B("whetstone",(.36,.15,.052),(1.16,-.36,1.692),(.36,.36,.30))
n.turn("+z",15)
for i in range(3):
    R("rear file",.012,(.86+i*.12,.04,1.66),(.86+i*.12,.51,1.66),steel)

# Rack with six upright pale handles.
B("tool stand",(.50,.27,.075),(1.31,.42,1.68),pale)
for i in range(6):
    x=1.10+(i%3)*.15; y=.31+(i//3)*.16
    h=.24+(2-i%3)*.07
    R("upright punch",.010,(x,y,1.72),(x,y,1.72+h*.65),silver)
    E("punch wooden handle",(x,y,1.72+h*.76),(.030,.030,h*.25),
      (.49,.39,.25))
    R("punch cap",.024,(x,y,1.72+h*.99),(x,y,1.72+h*1.02),silver)
    R("punch ferrule",.023,(x,y,1.72+h*.49),(x,y,1.72+h*.55),steel)

# Two shallow dark metal trays, subdivided into radial compartments.
cx,cy=.44,.43
R("organizer spindle",.021,(cx,cy,1.64),(cx,cy,2.47),iron)
for z,rad in ((1.84,.35),(2.17,.38)):
    R("tray bottom",rad,(cx,cy,z),(cx,cy,z+.014),(.040,.070,.078))
    for k in range(8):
        loop("tray rim wall",(cx,cy,z+.018+k*.010),rad,rad,.0065,iron)
    loop("bright tray lip",(cx,cy,z+.094),rad,rad,.010,(.20,.30,.33))
    for j in range(7):
        a=j*math.tau/7+.15
        # Closely stacked rods form a solid thin divider.
        for k in range(9):
            zz=z+.02+k*.009
            R("radial partition",.0065,(cx,cy,zz),
              (cx+rad*.97*math.cos(a),cy+rad*.97*math.sin(a),zz),
              (.09,.16,.18))
        R("partition top edge",.008,(cx,cy,z+.098),
          (cx+rad*.96*math.cos(a),cy+rad*.96*math.sin(a),z+.098),
          (.24,.34,.36))
    for j in range(32):
        a=random.random()*math.tau; rr=random.uniform(.07,rad*.85)
        x=cx+rr*math.cos(a); y=cy+rr*math.sin(a)
        R("loose screw",.004,(x,y,z+.024),(x+.025,y+.015,z+.03),steel)
loop("organizer carry loop",(cx,cy,2.46),.048,.10,.012,steel,True)

# Wall-mounted open wooden shelf.
B("wall shelf",(1.0,.30,.055),(1.19,.67,2.55),dark)
B("shelf back",(1.04,.035,.38),(1.19,.81,2.76),wood)
for x in (.67,1.71):
    B("shelf side",(.040,.30,.40),(x,.68,2.76),dark)
B("upper shelf",(1.07,.30,.05),(1.19,.67,2.97),wood)

# Small tilted display card.
n=B("cream label",(.32,.012,.13),(.15,-.49,1.71),(.54,.53,.40))
n.turn("+x",18)
for j in range(3):
    for k in range(12-j*2):
        B("label tiny lettering",(.008,.002,.004),
          (.045+k*.016,-.504,1.74-j*.020),(.09,.105,.085))

# Square stained stool, offset to the right in the foreground.
sx=.43
for x in (sx-.49,sx+.49):
    for y in (-1.57,-.91):
        B("stool leg",(.065,.07,.60),(x,y,.30),dark)
B("stool front stretcher",(1.05,.06,.07),(sx,-1.57,.22),wood)
B("stool seat rim",(1.18,.93,.075),(sx,-1.25,.68),(.25,.18,.09))
B("stool seat",(1.15,.91,.075),(sx,-1.25,.745),(.27,.27,.215))
for k in range(240):
    x=sx+random.uniform(-.55,.55); y=random.uniform(-1.68,-.82)
    E("irregular seat stain",(x,y,.784),
      (random.uniform(.012,.083),random.uniform(.01,.055),.0014),
      random.choice([(.105,.12,.105),(.34,.32,.23),(.19,.20,.16),(.43,.40,.28)]))

# Partially cropped neighboring bench.
B("neighbor slab",(.82,1.15,.10),(-2.03,-.02,1.40),edge)
for x in (-2.35,-1.72):
    for y in (-.43,.42):
        B("neighbor leg",(.09,.09,1.36),(x,y,.68),wood)
B("neighbor shelf",(.78,.95,.055),(-2.03,.02,.39),wood)
for j in range(9):
    B("neighbor stacked strips",(.65,.065,.022),
      (-2.03,-.23+j*.072,1.47+j*.007),(.35,.30,.20))
E("neighbor tool handle",(-2.12,.20,1.55),(.30,.10,.06),pale)
B("reddish box",(.38,.22,.15),(-2.22,.39,1.55),(.15,.045,.025))
R("foreground rail",.023,(-1.92,-1.83,0),(-1.92,-1.83,.70),iron)
R("foreground arm",.024,(-1.92,-1.83,.23),(-1.40,-1.64,.35),iron)
E("foreground oval cap",(-1.41,-1.64,.36),(.14,.085,.025),steel)
for y in (-.75,-.38,0,.38):
    R("side guard vertical",.016,(1.79,y,.17),(1.79,y,1.52),iron)
R("side guard top",.023,(1.79,-.80,1.52),(1.79,.58,1.52),iron)
R("side guard bottom",.020,(1.79,-.80,.18),(1.79,.58,.18),iron)

realize(scene)

# Preserve the actual SceneAct colors when enabling Blender shaders.
for mat in bpy.data.materials:
    prior_color=tuple(mat.diffuse_color[:3])
    was_nodes=mat.use_nodes
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    c=tuple(bs.inputs["Base Color"].default_value[:3]) if was_nodes else prior_color
    bs.inputs["Base Color"].default_value=(*c,1)
    brown=c[0]>c[2]*1.4 and c[0]>c[1]*1.12
    metal=(not brown and c[2]>c[0]*.95 and c[0]<.5)
    bs.inputs["Roughness"].default_value=.80 if brown else (.45 if metal else .90)
    bs.inputs["Metallic"].default_value=.72 if metal else 0
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    coord=nodes.new("ShaderNodeTexCoord")
    mapping=nodes.new("ShaderNodeVectorMath")
    mapping.operation="MULTIPLY"
    mapping.inputs[1].default_value=(3,3,.13) if brown else (1,1,1)
    links.new(coord.outputs["Generated"],mapping.inputs[0])
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=15 if brown else 22
    noise.inputs["Detail"].default_value=4
    noise.inputs["Roughness"].default_value=.78
    links.new(mapping.outputs["Vector"],noise.inputs["Vector"])
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.22
    ramp.color_ramp.elements[0].color=(*(v*.38 for v in c),1)
    ramp.color_ramp.elements[1].position=.78
    ramp.color_ramp.elements[1].color=(*(min(1,v*1.28) for v in c),1)
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.28
    bump.inputs["Distance"].default_value=.007 if brown else .003
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((.30,-4.60,4.05),(-.26,-.02,1.43),lens=40,sensor=36)
area_emitter((-3,-3,5),power=510,size=3.0,target=(0,0,1.2),color=(1,.86,.70))
area_emitter((2,-.2,4),power=220,size=2.4,target=(0,0,1.2),color=(.78,.87,1))
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("Ambient")
    bpy.context.scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.24,.27,.30,1)
bg.inputs["Strength"].default_value=.18
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
