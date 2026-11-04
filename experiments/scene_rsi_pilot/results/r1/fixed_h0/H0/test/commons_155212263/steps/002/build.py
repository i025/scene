from sceneact import *
import bpy
import math
import random

random.seed(12)
scene = Scene("Historic workshop")

wood = (.25,.22,.16)
top = (.39,.36,.27)
darkwood = (.16,.15,.11)
iron = (.16,.18,.17)
steel = (.43,.45,.42)
rust = (.30,.23,.16)
wall = (.61,.64,.58)

def boxpart(name, size, center, color):
    scene.include(name, box(size, center=center, color=color))

def rodpart(name, radius, start, end, color):
    scene.include(name, rod(radius=radius, start=start, end=end, color=color))

def tube(name, points, radius, color):
    scene.include(name, sweep_tube(points=points, radius=radius, color=color))

def ring(name, center, radius, thickness, color, plane="xz"):
    x,y,z = center
    points=[]
    for i in range(33):
        a=i*2*math.pi/32
        if plane=="xz":
            points.append((x+radius*math.cos(a),y,z+radius*math.sin(a)))
        else:
            points.append((x+radius*math.cos(a),y+radius*math.sin(a),z))
    tube(name,points,thickness,color)

# Individual long floorboards.
boxpart("floor foundation",(15,12,.10),(-2,-2,-.09),wood)
for i in range(39):
    c=random.uniform(.9,1.12)
    boxpart("floorboard%d"%i,(14,.205,.045),(-2,-6+i*.212,-.025),
            (.43*c,.37*c,.27*c))
    for j in range(2):
        x=random.uniform(-6,4)
        boxpart("board joint%d_%d"%(i,j),(.009,.203,.002),
                (x,-6+i*.212,.0001),(.21,.20,.15))

# Back wall and tall daylight windows.
boxpart("back plaster",(12,.20,4.6),(-2,1.52,2.25),wall)
boxpart("left wall",(.18,6,4.6),(-7.5,-1.4,2.25),(.55,.57,.51))
boxpart("baseboard",(12,.07,.17),(-2,1.38,.085),(.32,.33,.27))
for i,x in enumerate([-6.30,-4.35,-2.35,-.20,2.05]):
    w=1.65 if i<3 else 1.85
    boxpart("window surround%d"%i,(w+.18,.08,2.25),(x,1.375,3.02),(.36,.39,.36))
    boxpart("bright glass%d"%i,(w,.035,2.09),(x,1.32,3.04),(.87,.94,.98))
    boxpart("deep sill%d"%i,(w+.27,.48,.105),(x,1.14,1.93),(.43,.44,.37))
    for side in [-1,1]:
        boxpart("jamb%d_%d"%(i,side),(.055,.12,2.16),
                (x+side*w/2,1.25,3.02),(.40,.44,.41))
    boxpart("window mullion%d"%i,(.045,.12,2.12),(x,1.25,3.02),(.39,.43,.41))
    boxpart("window crossbar%d"%i,(w,.12,.04),(x,1.25,2.77),(.46,.49,.45))
    boxpart("window bottom%d"%i,(w,.14,.065),(x,1.24,1.99),(.33,.37,.34))

rodpart("wall pipe",.028,(3.27,1.20,1.35),(3.27,1.20,4.1),rust)
tube("pipe elbow",[(2.78,1.20,1.03),(2.64,1.20,1.1),(2.70,1.20,1.25),
                   (3.13,1.20,1.30),(3.27,1.20,1.43)],.027,rust)
rodpart("long leaning handle",.028,(3.30,.95,.3),(3.82,1.10,2.72),(.32,.23,.14))
for i,x in enumerate([-6.8,-5,-3.25,-1.5,.8]):
    rodpart("wall tool%d"%i,.016,(x,1.16,2.21),(x+.04,1.16,2.94),rust)
    ring("wall tool loop%d"%i,(x+.04,1.16,3.00),.065,.013,iron)

# Oil cans and small containers on sills.
for i in range(24):
    x=random.uniform(-7,2.8)
    y=random.uniform(1.00,1.18)
    h=random.uniform(.10,.22)
    c=random.choice([(.31,.34,.30),(.45,.43,.34),(.27,.30,.29)])
    rodpart("sill can%d"%i,.038,(x,y,1.99),(x,y,1.99+h),c)
    rodpart("can neck%d"%i,.016,(x,y,1.99+h),(x,y,2.04+h),iron)
    if i%4==0:
        rodpart("oil spout%d"%i,.008,(x,y,2.02+h),(x+.10,y,2.12+h),steel)

# Timber benches form a continuous row.
for i,(x,length) in enumerate([(-5.65,2.7),(-2.6,3.1),(1.00,3.9)]):
    bench=Asset("bench%d"%i)
    bench.include("top",box((length,1.10,.16),center=(x,.40,1.0),color=top))
    bench.include("front apron",box((length,.14,.23),center=(x,-.10,.83),color=wood))
    bench.include("back rail",box((length,.10,.14),center=(x,.84,.70),color=darkwood))
    for a,lx in enumerate([x-length/2+.17,x+length/2-.17]):
        for b,y in enumerate([-.01,.79]):
            bench.include("leg%d%d"%(a,b),box((.16,.17,.90),center=(lx,y,.45),color=darkwood))
        bench.include("crosspiece%d"%a,box((.15,.92,.12),center=(lx,.4,.25),color=wood))
    bench.include("low rail",box((length-.2,.11,.12),center=(x,.60,.24),color=wood))
    scene.include("bench%d"%i,bench)
    for j in range(7):
        xx=random.uniform(x-length/2+.1,x+length/2-.1)
        yy=random.uniform(-.10,.88)
        boxpart("bench wear%d_%d"%(i,j),(.22,.025,.003),(xx,yy,1.082),(.23,.23,.17))

# Open foreground drawer.
boxpart("drawer bottom",(1.12,.72,.055),(.65,-.48,.57),(.25,.26,.19))
boxpart("drawer face",(1.18,.085,.29),(.65,-.85,.69),(.21,.22,.17))
for x in [.07,1.23]:
    boxpart("drawer side"+str(x),(.06,.73,.28),(x,-.48,.69),(.31,.31,.23))
boxpart("drawer rear",(1.12,.055,.25),(.65,-.13,.69),darkwood)
ring("drawer pull",(.65,-.90,.70),.073,.013,(.41,.39,.29))
for i in range(4):
    rodpart("drawer scrap%d"%i,.012,(.25+i*.2,-.69,.62),(.43+i*.14,-.26,.62),rust)

# Main lathe; axis runs along the bench.
for i,x in enumerate([.28,2.30]):
    boxpart("lathe foot%d"%i,(.43,.51,.075),(x,.41,1.12),iron)
    boxpart("lathe pedestal%d"%i,(.20,.29,.32),(x,.41,1.31),iron)
    boxpart("pedestal shoulder%d"%i,(.32,.35,.12),(x,.41,1.45),iron)
boxpart("lathe bed",(2.52,.32,.12),(1.32,.42,1.44),iron)
for y in [.20,.61]:
    rodpart("lathe steel rail"+str(y),.045,(.02,y,1.49),(2.61,y,1.49),steel)
boxpart("headstock",(.50,.46,.32),(.38,.43,1.68),iron)
rodpart("headstock round housing",.18,(.17,.43,1.77),(.62,.43,1.77),iron)
rodpart("spindle",.075,(.45,.43,1.77),(.93,.43,1.77),steel)
rodpart("chuck",.135,(.83,.43,1.77),(1.00,.43,1.77),(.23,.25,.23))
for i in range(3):
    a=i*2*math.pi/3
    boxpart("chuck jaw%d"%i,(.12,.065,.065),
            (1.0,.43+.10*math.cos(a),1.77+.10*math.sin(a)),steel)
boxpart("tailstock slide",(.47,.45,.09),(2.13,.43,1.54),iron)
rodpart("tailstock barrel",.15,(1.91,.43,1.74),(2.35,.43,1.74),iron)
boxpart("tailstock upright",(.22,.31,.20),(2.20,.43,1.63),iron)
rodpart("tailstock quill",.055,(1.67,.43,1.77),(2.66,.43,1.77),steel)
rodpart("end crank",.022,(2.66,.43,1.77),(2.66,.43,1.51),iron)
rodpart("end handle",.037,(2.66,.43,1.51),(2.91,.43,1.51),(.43,.36,.26))
boxpart("carriage",(.44,.44,.12),(1.39,.40,1.56),iron)
rodpart("tool rest upright",.045,(1.38,.15,1.55),(1.38,.15,1.84),iron)
boxpart("tool rest top",(.49,.095,.06),(1.38,.15,1.84),iron)
ring("carriage wheel",(1.40,.09,1.48),.10,.018,iron)

def flywheel(name,x,y,z,r,col):
    ring(name+" outer",(x,y,z),r,.031,col)
    ring(name+" lip",(x,y-.035,z),r-.035,.012,(.39,.42,.39))
    rodpart(name+" hub",.077,(x,y-.10,z),(x,y+.12,z),col)
    for i in range(5):
        a=i*2*math.pi/5
        pts=[]
        for j in range(6):
            t=j/5
            rr=.06+(r-.075)*t
            aa=a+.40*math.sin(math.pi*t)
            pts.append((x+rr*math.cos(aa),y,z+rr*math.sin(aa)))
        tube(name+" spoke%d"%i,pts,.026,col)
    rodpart(name+" axle",.030,(x,y-.20,z),(x,y+.18,z),steel)
    rodpart(name+" crank",.019,(x,y-.19,z),(x+r*.68,y-.19,z-.14),rust)
    rodpart(name+" grip",.026,(x+r*.68,y-.19,z-.14),(x+r*.68,y-.35,z-.14),darkwood)

rodpart("large wheel stand",.045,(.16,.82,1.12),(.16,.82,2.27),iron)
rodpart("wheel diagonal brace",.028,(.65,.85,1.14),(.16,.85,2.27),iron)
flywheel("large flywheel",.16,.73,2.30,.47,(.20,.24,.24))
tube("drive belt",[(-.22,.80,2.52),(-.28,.80,2.18),(-.08,.80,1.29),
                   (.13,.80,1.24),(.55,.80,2.17),(.59,.80,2.49)],.011,(.18,.14,.10))

# Anvil with flared shoulders and tapered horn.
ax=-1.58
boxpart("anvil block",(.69,.62,.56),(ax,.16,.76),(.24,.20,.13))
boxpart("anvil base",(.68,.48,.11),(ax,.16,1.12),(.33,.29,.20))
boxpart("anvil waist",(.28,.31,.32),(ax,.16,1.33),(.38,.33,.23))
for s in [-1,1]:
    ob=box((.20,.36,.29),center=(ax+s*.20,.16,1.43),color=(.42,.36,.25))
    ob.turn('y',s*23)
    scene.include("anvil shoulder"+str(s),ob)
boxpart("anvil face",(.80,.44,.14),(ax,.16,1.59),(.48,.43,.32))
boxpart("anvil heel",(.22,.43,.13),(ax-.48,.16,1.59),(.45,.40,.29))
for i in range(8):
    t=i/7
    rodpart("anvil horn%d"%i,.17*(1-t)+.014,
            (ax+.40+t*.51,.16,1.56+t*.04),
            (ax+.48+t*.51,.16,1.56+t*.04),(.47,.41,.29))
boxpart("anvil square hole",(.065,.065,.003),(ax-.43,.16,1.663),(.12,.13,.10))

# Smaller blue machine and far tools.
boxpart("small lathe base",(1.12,.51,.09),(-3.27,.42,1.13),iron)
for x in [-3.68,-2.87]:
    boxpart("small machine foot"+str(x),(.18,.29,.25),(x,.42,1.29),iron)
rodpart("small bed",.048,(-3.83,.32,1.43),(-2.62,.32,1.43),steel)
rodpart("small spindle",.065,(-3.72,.46,1.52),(-2.65,.46,1.52),iron)
rodpart("small wheel stand",.033,(-3.12,.76,1.14),(-3.12,.76,1.97),iron)
flywheel("blue wheel",-3.12,.68,1.98,.32,(.20,.32,.36))

for i,x in enumerate([-4.46,-5.28,-6.05,-6.77]):
    boxpart("far machine base%d"%i,(.59,.43,.08),(x,.42,1.12),iron)
    boxpart("far machine body%d"%i,(.21,.26,.30),(x,.44,1.29),(.27,.29,.25))
    rodpart("far spindle%d"%i,.052,(x-.31,.39,1.45),(x+.28,.39,1.45),steel)
    rodpart("far stand%d"%i,.028,(x,.73,1.16),(x,.73,1.93),iron)
    if i in [0,2]:
        flywheel("far wheel%d"%i,x,.73,1.89,.20,(.28,.32,.30))
    boxpart("far box%d"%i,(.31,.29,.25),(x-.25,.76,1.25),(.35,.28,.19))

# Front-edge vise.
boxpart("vise base",(.39,.38,.10),(-.72,-.04,1.12),iron)
boxpart("vise body",(.31,.36,.23),(-.72,-.16,1.25),iron)
for x in [-.86,-.60]:
    boxpart("vise jaw"+str(x),(.10,.38,.17),(x,-.16,1.38),steel)
rodpart("vise screw",.037,(-.72,-.52,1.24),(-.72,-.11,1.24),iron)
rodpart("vise handle",.019,(-.92,-.54,1.24),(-.49,-.54,1.24),steel)

# Loose hand tools, sheets and bars.
for i in range(24):
    x=random.uniform(-6.8,2.55)
    y=random.uniform(-.08,.24)
    length=random.uniform(.20,.43)
    rodpart("loose blade%d"%i,.012,(x,y,1.10),(x+length,y+.13,1.11),steel)
    rodpart("loose grip%d"%i,.025,(x-.11,y-.03,1.11),(x,y,1.11),
            random.choice([(.36,.26,.15),(.45,.34,.20),(.23,.20,.14)]))
for i in range(6):
    rodpart("neat file%d"%i,.017,(-.27+i*.12,-.07,1.11),
            (.02+i*.12,.26,1.12),steel)
boxpart("metal sheet",(.48,.37,.012),(.98,-.03,1.10),(.59,.60,.55))
for i in range(3):
    rodpart("sheet hole%d"%i,.017,(.85+i*.11,-.09,1.107),(.85+i*.11,-.09,1.111),iron)
boxpart("paper",(.30,.27,.008),(1.54,-.03,1.10),(.72,.71,.64))
for i in range(6):
    x=-1.05+i*.065
    rodpart("hanging tong%d"%i,.013,(x,-.21,1.03),(x-.06,-.24,.28),rust)
for i in range(4):
    x=-5.15+i*.5
    boxpart("underbench drawer%d"%i,(.43,.48,.28),(x,.27,.61),(.25,.27,.21))
    rodpart("drawer handle%d"%i,.016,(x-.06,.02,.62),(x+.06,.02,.62),iron)

# Cylindrical storage bins.
def can(name,x,y,r,h,color):
    rodpart(name+" body",r,(x,y,.02),(x,y,h),color)
    rodpart(name+" dark opening",r*.91,(x,y,h+.002),(x,y,h+.006),(.16,.17,.13))
    ring(name+" rim",(x,y,h+.01),r,.013,(.36,.36,.29),"xy")

can("pale foreground bin",1.18,-.12,.32,.63,(.58,.57,.46))
can("green bin",2.69,.16,.36,.76,(.24,.30,.21))
can("rear pail",-4.12,.16,.23,.48,(.34,.37,.29))
can("rust pail",-5.16,.13,.20,.44,(.36,.28,.19))
boxpart("scrap in bin",(.31,.19,.045),(1.18,-.10,.66),(.32,.29,.21))
rodpart("wood in bin",.065,(1.10,-.15,.52),(1.22,-.11,.76),(.37,.29,.18))
for i in range(3):
    boxpart("bin label%d"%i,(.022,.007,.15),(1.07+i*.10,-.431,.34),(.24,.25,.20))

# Painted navigation marker on the floor.
rodpart("floor marker",.28,(-2.70,-1.86,.004),(-2.70,-1.86,.008),(.35,.43,.43))
boxpart("arrow shaft",(.11,.23,.004),(-2.70,-1.87,.012),(.79,.81,.76))
for s in [-1,1]:
    ob=box((.08,.19,.004),center=(-2.70+s*.055,-1.77,.013),color=(.79,.81,.76))
    ob.turn('z',s*45)
    scene.include("arrowhead"+str(s),ob)

realize(scene)

# Lightweight material treatment.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    c=tuple(bs.inputs["Base Color"].default_value[:3])
    bs.inputs["Roughness"].default_value=.78
    if min(c)>.82:
        bs.inputs["Emission Color"].default_value=(*c,1)
        bs.inputs["Emission Strength"].default_value=.7
    elif max(c)-min(c)<.085 and max(c)<.62:
        bs.inputs["Metallic"].default_value=.45
        bs.inputs["Roughness"].default_value=.55

# A single shared noise bump avoids costly geometry.
noise_group=None
for mat in bpy.data.materials:
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    c=bs.inputs["Base Color"].default_value
    if min(c[:3])>.82:
        continue
    n=mat.node_tree.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value=48
    n.inputs["Detail"].default_value=2
    b=mat.node_tree.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value=.16
    b.inputs["Distance"].default_value=.014
    mat.node_tree.links.new(n.outputs["Fac"],b.inputs["Height"])
    mat.node_tree.links.new(b.outputs["Normal"],bs.inputs["Normal"])

set_view((4.15,-6.10,3.65),(-1.55,.42,1.25),lens=38,sensor=36)
area_emitter((-.8,.55,4.5),power=1050,size=5,target=(-1,-.7,.5),color=(.86,.94,1))
area_emitter((2,-3.5,4.2),power=370,size=4,target=(-1,.3,1),color=(1,.91,.78))
area_emitter((-5,.65,3.7),power=350,size=2.8,target=(-4,-.2,1),color=(.88,.95,1))

sc=bpy.context.scene
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.43,.48,.51,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc.render.engine='CYCLES'
sc.cycles.samples=16
sc.cycles.use_denoising=True
sc.cycles.max_bounces=5
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.1
