from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(19)
scene = Scene(name="Old toolmaker's bench")

wood=(.43,.25,.105)
edge=(.57,.36,.16)
lightwood=(.61,.42,.22)
darkwood=(.25,.135,.065)
steel=(.26,.31,.32)
bright=(.48,.53,.52)
iron=(.075,.105,.105)
brass=(.30,.28,.13)

def B(name,size,center,col=wood):
    n=box(size=size,center=center,color=col)
    scene.include(name,n)
    return n
def R(name,r,a,b,col=steel):
    n=rod(radius=r,start=a,end=b,color=col)
    scene.include(name,n)
    return n
def S(name,pts,r=.01,col=steel):
    n=sweep_tube(points=pts,radius=r,color=col)
    scene.include(name,n)
    return n
def ballshape(name,p,scale,col):
    n=ball(radius=1,center=p,color=col)
    n.resize(scale)
    scene.include(name,n)
    return n
def loop(name,c,rx,ry,r=.009,col=steel,plane="xy"):
    pts=[]
    for j in range(49):
        t=j*2*math.pi/48
        if plane=="xy": p=(c[0]+rx*math.cos(t),c[1]+ry*math.sin(t),c[2])
        else: p=(c[0]+rx*math.cos(t),c[1],c[2]+ry*math.sin(t))
        pts.append(p)
    return S(name,pts,r,col)

# Planked room.
B("floor foundation",(7,7,.12),(0,0,-.09),darkwood)
for i in range(23):
    x=-3.4+i*.30
    B("floor board %02d"%i,(.292,6,.06),(x,-1.0,-.015),
      (.35+random.random()*.09,.205+random.random()*.055,.105+random.random()*.03))
    for y in (-2.8,-.7,1.4):
        R("floor nail",.006,(x+.12,y,.017),(x+.12,y,.020),iron)
B("wall backing",(7,.14,4.5),(0,.97,1.9),darkwood)
for i in range(19):
    x=-3.2+i*.35
    B("vertical pine wall %02d"%i,(.343,.065,4.4),(x,.865,1.9),
      (.34+random.random()*.10,.19+random.random()*.075,.085+random.random()*.04))
    for j in range(4):
        z=random.uniform(.4,3.0)
        ballshape("oval wood knot",(x+random.uniform(-.10,.10),.824,z),
                  (.018,.004,.027),(.115,.066,.030))
for x in (-1.83,.17,1.91):
    B("wall joining bead",(.027,.03,4.1),(x,.814,1.95),(.28,.15,.068))

# Solid wooden bench.
B("thick scarred worktop",(3.05,1.24,.115),(0,.04,1.56),edge)
B("front worn edge",(3.10,.055,.075),(0,-.588,1.55),lightwood)
B("back raised edge",(3.05,.045,.065),(0,.645,1.64),darkwood)
for x in (-1.38,1.38):
    for y in (-.45,.51):
        B("square bench leg",(.135,.14,1.48),(x,y,.75),wood)
    B("side apron",(.12,1.12,.23),(x,.015,1.36),wood)
B("front drawer rail",(2.9,.10,.09),(0,-.47,1.04),darkwood)
B("lower back crossbar",(2.8,.10,.12),(0,.49,.30),darkwood)
# Left cabinet carcass, with dark openings.
B("left cabinet shadow",(.82,.86,1.13),(-1.0,.01,.88),(.115,.082,.043))
for x in (-1.44,-.55):
    B("left cabinet stile",(.065,.98,1.18),(x,-.06,.89),edge)
for z in (.33,.70,1.07,1.43):
    B("left drawer separator",(.88,1.0,.055),(-1.0,-.04,z),wood)
B("right cabinet shadow",(.76,.86,.96),(1.04,.01,.95),(.12,.085,.05))
for x in (.64,1.44):
    B("right side stile",(.065,.98,.98),(x,-.04,.91),edge)

def pull(name,x,y,z,w=.20):
    for dx in (-w/2,w/2):
        ballshape(name+" screw",(x+dx,y-.010,z+.025),(.019,.009,.019),iron)
    S(name+" hanging handle",
      [(x-w/2,y-.025,z+.022),(x-w*.44,y-.055,z-.028),
       (x-w*.22,y-.070,z-.057),(x+w*.22,y-.070,z-.057),
       (x+w*.44,y-.055,z-.028),(x+w/2,y-.025,z+.022)],.013,iron)

def drawer(name,x,w,z,front,depth=.70,h=.19):
    B(name+" bottom",(w,depth,.035),(x,front+depth/2,z-h/2),(.38,.27,.13))
    B(name+" front",(w+.035,.065,h),(x,front,z),edge)
    for xx in (x-w/2+.025,x+w/2-.025):
        B(name+" side",(.045,depth,h-.025),(xx,front+depth/2,z+.004),lightwood)
    B(name+" back",(w,.035,h-.025),(x,front+depth,z),wood)
    pull(name,x,front-.043,z,.23 if w>.9 else .20)
    for k in range(12):
        xx=x+random.uniform(-w*.46,w*.46)
        zz=z+random.uniform(-h*.40,h*.40)
        B(name+" face scratches",(random.uniform(.025,.10),.0015,.002),
          (xx,front-.034,zz),darkwood)
    return z+h*.5

drawer("left upper drawer",-1.0,.78,1.27,-.89,.73,.21)
drawer("left middle drawer",-1.0,.78,.91,-.98,.76,.21)
drawer("left bottom drawer",-1.0,.78,.40,-1.02,.79,.21)
drawer("broad central drawer",-.02,1.18,1.23,-.88,.79,.25)
drawer("right upper drawer",1.06,.72,1.28,-.85,.75,.19)
drawer("right low drawer",1.06,.72,.60,-.93,.76,.20)

# Loose drawer contents.
for k in range(13):
    x=-.55+k*.087
    y=random.uniform(-.65,-.30)
    R("drawer wooden chisel handle",.030,(x,y,1.23),(x+.025,y+.23,1.25),
      (.40+random.random()*.16,.23+random.random()*.08,.11))
    R("drawer chisel tang",.012,(x,y-.16,1.22),(x,y+.03,1.24),steel)
    R("handle end band",.032,(x,y+.16,1.248),(x+.004,y+.18,1.25),brass)
for k in range(17):
    x=random.uniform(-1.31,-.68)
    y=random.uniform(-.87,-.43)
    R("left drawer sliver",.009,(x,y,1.255),(x+.02,y+.15,1.26),lightwood)
for k in range(13):
    x=random.uniform(-1.32,-.68)
    R("bottom drawer slender tool",.013,(x,-.95,.41),(x,-.54,.42),lightwood)
for k in range(34):
    x=random.uniform(.76,1.34)
    y=random.uniform(-.77,-.37)
    loop("small iron drawer fitting",(x,y,1.278),.015,.023,.004,iron)
for k in range(6):
    R("right drawer file",.009,(.78+k*.09,-.81,.60),(.82+k*.09,-.42,.61),steel)

# Dirty protective cloths on the top.
B("left grey work mat",(1.51,.99,.012),(-.65,-.025,1.626),(.40,.40,.34))
B("right grey work mat",(1.05,.98,.012),(.80,.025,1.626),(.43,.43,.37))
B("small overlapping rag",(.57,.43,.008),(.02,.37,1.635),(.46,.43,.34))
for k in range(80):
    x=random.uniform(-1.45,1.45)
    y=random.uniform(-.53,.59)
    B("tiny bench scratch",(random.uniform(.015,.08),.002,.001),
      (x,y,1.638),(.25,.24,.18))

# Two greenish brass oil cans at the rear left.
for i,x in enumerate((-1.19,-.77)):
    ballshape("oil can rounded body",(x,.44,1.71),(.16,.13,.105),(.28,.29,.14))
    R("oil can base rim",.145,(x,.44,1.64),(x,.44,1.663),brass)
    R("oil can neck",.065,(x,.44,1.76),(x,.44,1.82),brass)
    # tapered spout assembled in short steps
    for j in range(13):
        r=.046*(1-j/14)+.005
        R("tapered oil nozzle",r,(x,.44,1.81+j*.017),
          (x-.003,.44,1.83+j*.017),(.24,.28,.27))
    R("oil can collar",.069,(x,.44,1.79),(x,.44,1.81),bright)

# Small open metal cup.
R("cup dark interior",.077,(-.43,.25,1.64),(-.43,.25,1.81),(.12,.13,.105))
for j in range(32):
    a=j*math.tau/32
    R("cup side",.008,(-.43+.078*math.cos(a),.25+.078*math.sin(a),1.65),
      (-.43+.078*math.cos(a),.25+.078*math.sin(a),1.82),brass)
loop("cup rolled rim",(-.43,.25,1.82),.079,.079,.009,bright)

# Pliers and shears spread across the foreground.
def toolpath(name,points,r=.012,col=steel):
    return S(name,[(x,y,1.656+z) for x,y,z in points],r,col)
def scissors(name,x,y,length=.39,spread=.055):
    z=1.658
    for s in (-1,1):
        loop(name+" finger ring",(x+s*spread,y-.13,z),.046,.070,.010,bright)
        S(name+" arm",[(x+s*spread,y-.075,z),(x+s*.025,y+.075,z+.006),
                      (x-s*.028,y+length-.12,z+.007)],.011,steel)
    R(name+" hinge",.022,(x,y+.075,z),(x,y+.075,z+.018),bright)
scissors("large shears",-.66,-.31,.47,.064)
scissors("small shears",-.49,-.34,.37,.052)
toolpath("left tong one",[(-1.39,-.40,0),(-1.31,-.28,0),(-1.28,-.10,0),(-1.24,.05,0),(-1.12,.11,0)],.019)
toolpath("left tong two",[(-1.25,-.42,0),(-1.23,-.23,0),(-1.19,-.08,.006),(-1.22,.04,.006),(-1.14,.15,0)],.017,bright)
R("pincer pivot",.026,(-1.225,-.05,1.66),(-1.225,-.05,1.683),iron)
toolpath("curved pliers a",[(-1.11,-.38,0),(-1.13,-.21,0),(-1.06,-.04,0),(-1.02,.12,0),(-.94,.16,0)],.016)
toolpath("curved pliers b",[(-.97,-.37,0),(-1.03,-.17,0),(-1.06,-.04,.01),(-1.10,.11,0),(-1.03,.15,0)],.016)
for x in (-.20,-.04,.14):
    toolpath("long slender pincers",[(x-.025,-.37,0),(x-.04,-.12,0),(x-.03,.07,0),(x-.075,.20,0)],.012,bright)
    toolpath("long slender pincers",[(x+.025,-.37,0),(x+.035,-.12,0),(x+.025,.07,0),(x+.07,.20,0)],.012,steel)
    R("pliers hinge",.021,(x,.045,1.656),(x,.045,1.675),steel)
# rectangular nutcracker handles
for x in (-.33,.04):
    S("rectangular tool loop",[(x-.035,-.37,1.66),(x-.035,-.13,1.66),
      (x+.035,-.13,1.66),(x+.035,-.37,1.66),(x-.035,-.37,1.66)],.012,bright)
    R("nutcracker jaw",.017,(x,-.13,1.66),(x,.06,1.66),steel)

# Chisels, files and handled punches on the right.
def chisel(name,x,y,L=.48,w=.04,ang=0):
    z=1.658
    n=box((w,L*.56,.014),center=(x,y+L*.16,z),color=bright)
    n.turn("+z",ang)
    scene.include(name+" blade",n)
    R(name+" shaft",.014,(x,y-L*.20,z+.01),(x,y+.02,z+.01),steel)
    ballshape(name+" handle",(x,y-L*.30,z+.025),(.035,L*.15,.029),lightwood)
    R(name+" ferrule",.025,(x,y-L*.20,z+.01),(x,y-L*.15,z+.01),brass)
for i,x in enumerate((.37,.52,.70,.88)):
    chisel("bench chisel "+str(i),x,-.12+random.uniform(-.025,.025),.56,.045)
# Large hand plane and sharpening blocks.
B("plane dark sole",(.32,.48,.045),(1.18,-.13,1.666),(.20,.21,.18))
B("plane wooden body",(.28,.40,.075),(1.18,-.11,1.713),(.40,.31,.21))
n=B("plane iron blade",(.23,.11,.022),(1.18,-.09,1.77),steel)
n.turn("+x",24)
B("plane rear grip",(.16,.045,.095),(1.18,.04,1.78),darkwood)
n=B("slanted pale whetstone",(.38,.16,.065),(1.15,-.36,1.70),(.49,.48,.40))
n.turn("+z",15)
for i in range(3):
    R("long rear file",.014,(.86+i*.12,.04,1.66),(.86+i*.12,.51,1.66),steel)

# Rear rack of upright awls and short handled punches.
B("right tool stand",(.50,.27,.09),(1.32,.42,1.69),lightwood)
for i in range(6):
    x=1.11+(i%3)*.15
    y=.31+(i//3)*.16
    h=.27+(2-i%3)*.07
    R("upright punch shaft",.012,(x,y,1.72),(x,y,1.72+h*.60),bright)
    ballshape("upright pale handle",(x,y,1.72+h*.75),(.036,.036,h*.26),(.64,.56,.40))
    R("handle end cap",.024,(x,y,1.72+h*.99),(x,y,1.72+h*1.015),bright)
    R("punch ferrule",.026,(x,y,1.72+h*.47),(x,y,1.72+h*.53),steel)

# Rotating two-tier dark circular parts organizer.
cx,cy=.44,.43
R("carousel vertical spindle",.023,(cx,cy,1.64),(cx,cy,2.47),iron)
for tier,z,rad in ((0,1.83,.35),(1,2.18,.38)):
    # platter with raised perimeter and six spoke partitions
    R("carousel shallow round floor",rad,(cx,cy,z),(cx,cy,z+.018),(.065,.10,.105))
    loop("carousel rolled outer lip",(cx,cy,z+.09),rad,rad,.014,(.16,.22,.23))
    for j in range(48):
        a=j*math.tau/48
        b=(j+1)*math.tau/48
        # narrow wall panels follow circular edge
        p1=(cx+rad*math.cos(a),cy+rad*math.sin(a),z+.02)
        p2=(cx+rad*math.cos(b),cy+rad*math.sin(b),z+.09)
        R("tray vertical rim",.009,p1,(p1[0],p1[1],z+.09),iron)
    for j in range(6):
        a=j*math.tau/6+.15
        ex=cx+rad*.95*math.cos(a)
        ey=cy+rad*.95*math.sin(a)
        for zz in (z+.025,z+.05,z+.075,z+.095):
            R("tray divider",.009,(cx,cy,zz),(ex,ey,zz),(.12,.18,.19))
    for j in range(22):
        a=random.random()*math.tau
        rr=random.uniform(.09,rad*.82)
        x=cx+rr*math.cos(a);y=cy+rr*math.sin(a)
        R("loose organizer screw",.005,(x,y,z+.023),(x+.03,y+.02,z+.03),steel)
loop("carousel carrying loop",(cx,cy,2.48),.050,.105,.013,steel,plane="xz")

# Small rear shelf and timber cubby high on the wall.
B("back wall shelf",(1.0,.30,.07),(1.19,.67,2.55),darkwood)
B("cubby back",(1.04,.045,.38),(1.19,.81,2.76),wood)
for x in (.67,1.71):
    B("cubby cheek",(.045,.30,.40),(x,.68,2.76),darkwood)
B("cubby upper board",(1.07,.30,.055),(1.19,.67,2.97),wood)

# Small label propped against the tools.
n=B("ivory museum label",(.35,.012,.14),(.12,-.49,1.71),(.67,.65,.49))
n.turn("+x",18)
for j in range(3):
    B("label printed line",(.20-j*.025,.003,.005),(.12,-.503,1.73-j*.025),(.14,.15,.12))

# Front stool: broad, very worn rectangular pad.
for x in (-.43,.55):
    for y in (-1.57,-.91):
        B("stool square legs",(.075,.075,.60),(x,y,.30),darkwood)
B("stool front cross rail",(1.08,.06,.075),(.06,-1.57,.23),wood)
B("stool left cross rail",(.06,.70,.075),(-.43,-1.24,.21),wood)
B("stool seat wooden rim",(1.18,.93,.10),(.06,-1.25,.67),(.29,.23,.14))
B("battered square stool cushion",(1.15,.91,.09),(.06,-1.25,.73),(.32,.31,.23))
for k in range(150):
    x=random.uniform(-.49,.60)
    y=random.uniform(-1.68,-.82)
    sx=random.uniform(.018,.085);sy=random.uniform(.015,.06)
    col=random.choice([(.16,.17,.14),(.45,.43,.31),(.25,.25,.19),(.53,.49,.35)])
    n=B("cushion worn patch",(sx,sy,.002),(x,y,.777),col)
    n.turn("+z",random.uniform(-60,60))

# Adjacent bench entering frame on the left.
B("neighbor bench surface",(.82,1.15,.12),(-2.03,-.02,1.40),edge)
for x in (-2.35,-1.72):
    for y in (-.43,.42):
        B("neighbor bench leg",(.10,.10,1.36),(x,y,.68),wood)
B("neighbor lower shelf",(.78,.95,.06),(-2.03,.02,.39),wood)
for j in range(7):
    B("stack of narrow wood strips",(.65,.07,.025),(-2.03,-.21+j*.085,1.48+j*.007),(.49,.40,.26))
ballshape("neighbor wooden tool handle",(-2.12,.20,1.55),(.30,.11,.065),lightwood)
# Black foreground support at bottom left.
R("foreground dark rail",.022,(-1.92,-1.83,0),(-1.92,-1.83,.70),iron)
R("foreground diagonal arm",.023,(-1.92,-1.83,.23),(-1.40,-1.64,.35),iron)
ballshape("foreground oval cap",(-1.41,-1.64,.36),(.14,.085,.025),(.21,.26,.25))
# Right black barrier cropped at frame edge.
for y in (-.75,-.38,.0,.38):
    R("black side guard vertical",.016,(1.79,y,.18),(1.79,y,1.52),iron)
R("black side top rail",.023,(1.79,-.80,1.52),(1.79,.58,1.52),iron)
R("black side bottom rail",.020,(1.79,-.80,.18),(1.79,.58,.18),iron)

realize(scene)

# Procedural surface variation gives aged metal, grain, and dirt without image textures.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    c=tuple(mat.diffuse_color[:3])
    # SceneAct materials may keep their actual color in the shader.
    if bs.inputs.get("Base Color"):
        c=tuple(bs.inputs["Base Color"].default_value[:3])
    brown=c[0]>c[2]*1.4 and c[0]>c[1]*1.13
    metal=(not brown and c[2]>=c[0]*.88 and c[0]<.57)
    bs.inputs["Roughness"].default_value=.78 if brown else (.48 if metal else .91)
    bs.inputs["Metallic"].default_value=.65 if metal else .0
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=18 if brown else 34
    tex.inputs["Detail"].default_value=3.5
    tex.inputs["Roughness"].default_value=.76
    coord=nodes.new("ShaderNodeTexCoord")
    mapping=nodes.new("ShaderNodeVectorMath");mapping.operation="MULTIPLY"
    mapping.inputs[1].default_value=(3,3,.14) if brown else (1,1,1)
    links.new(coord.outputs["Generated"],mapping.inputs[0])
    links.new(mapping.outputs["Vector"],tex.inputs["Vector"])
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=tuple(v*.47 for v in c)+(1,)
    ramp.color_ramp.elements[1].position=.83
    ramp.color_ramp.elements[1].color=tuple(min(1,v*1.25) for v in c)+(1,)
    links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.22 if brown else .16
    bump.inputs["Distance"].default_value=.009 if brown else .004
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((.43,-4.75,3.58),(-.10,-.01,1.36),lens=39,sensor=36)
area_emitter((-3,-3,5),power=650,size=3.4,target=(0,0,1.1),color=(1,.84,.65))
area_emitter((2,-.3,4.2),power=310,size=2.8,target=(0,0,1.1),color=(.78,.88,1))
world=bpy.context.scene.world
world.color=(.18,.18,.18)
bpy.context.scene.render.engine="CYCLES"
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=384
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform="AgX"
