from sceneact import *
import bpy, math, random
random.seed(21)

scene = Scene("School classroom")
cream = (.87,.86,.68)
yellow = (.94,.70,.025)
wood = (.23,.17,.085)
topwood = (.20,.17,.115)
framewood = (.29,.20,.105)

def B(name,size,center,color):
    obj = box(size=size,center=center,color=color)
    scene.include(name,obj)
    return obj

# Tiled floor.
B("floor foundation",(8.6,19,.13),(0,1,-.10),(.67,.55,.35))
for i in range(27):
    for j in range(59):
        x=-4.16+i*.32
        y=-8.28+j*.32
        v=random.uniform(-.065,.065)
        B("floor tile %d %d"%(i,j),(.315,.315,.025),
          (x,y,-.018),(.71+v,.62+v,.44+v))
        if random.random()<.18:
            B("tile grain %d %d"%(i,j),(.014,.22,.002),
              (x+random.uniform(-.12,.12),y,0),(.64+v,.54+v,.36+v))

# Architecture.
for x in [-4.35,4.35]:
    B("upper side wall "+str(x),(.18,19.2,3.45),(x,1,2.875),cream)
    B("yellow dado "+str(x),(.20,19.2,1.17),(x,1,.57),yellow)
    B("skirting "+str(x),(.23,19.2,.12),(x,1,.06),(.39,.30,.14))
B("back wall",(8.8,.18,4.6),(0,10.5,2.3),cream)
B("ceiling",(8.8,19.3,.14),(0,1,4.62),(.91,.91,.84))
for y in [-6,-1,4,9]:
    B("ceiling crossbeam "+str(y),(8.7,.20,.25),(0,y,4.43),(.89,.89,.82))
for x in [-2.1,2.1]:
    B("long ceiling rib "+str(x),(.18,19,.15),(x,1,4.47),(.93,.93,.86))

# Windows and timber shutters.
for side in [-1,1]:
    x=side*4.225
    for idx,y in enumerate([-5.6,-1.9,1.7,5.1,8.0]):
        width=1.38 if idx<4 else 1.0
        B("window recess %s %s"%(side,idx),(.045,width,2.56),
          (x,y,2.38),(.19,.15,.095))
        B("window daylight %s %s"%(side,idx),(.052,width-.15,2.35),
          (x-side*.035,y,2.40),(.98,.98,.87))
        for yy in [y-width/2,y+width/2]:
            B("window jamb %s %s %s"%(side,idx,yy),(.15,.095,2.65),
              (x-side*.08,yy,2.36),framewood)
        for zz in [1.04,3.15,3.69]:
            B("window rail %s %s %s"%(side,idx,zz),(.15,width,.085),
              (x-side*.08,y,zz),framewood)
        B("window mullion %s %s"%(side,idx),(.13,.065,2.54),
          (x-side*.08,y,2.36),framewood)
        if (side==-1 and idx in [0,2,3]) or (side==1 and idx in [1,2,3]):
            B("wood door %s %s"%(side,idx),(.15,width*.70,1.94),
              (x-side*.10,y+width*.13,1.78),(.40,.29,.14))
            for yy in [y-width*.15,y+width*.37]:
                B("door stile %s %s %s"%(side,idx,yy),(.18,.035,1.72),
                  (x-side*.115,yy,1.78),(.55,.42,.23))
            for zz in [1.03,1.8,2.55]:
                B("door rail %s %s %s"%(side,idx,zz),(.18,width*.56,.04),
                  (x-side*.115,y+width*.1,zz),(.54,.42,.24))
    for y in [-3.6,.1,3.65,6.7]:
        B("wall pilaster %s %s"%(side,y),(.18,.19,4.35),
          (side*4.13,y,2.19),(.88,.85,.67))

# Stage, curtains and chalkboard.
B("raised platform",(7.1,2,.24),(0,9.45,.12),(.38,.30,.17))
B("stage yellow edge",(7.12,.15,.27),(0,8.45,.135),(.70,.48,.045))
B("dark stage backdrop",(6.7,.13,3.35),(0,10.24,2.1),(.12,.07,.035))
for side in [-1,1]:
    for k in range(10):
        x=side*(2.38+k*.11)
        B("green curtain %s %s"%(side,k),(.15,.20,3.1),(x,10.02,2.17),
          (.12+random.random()*.045,.22+random.random()*.04,.055))
    for k in range(6):
        x=side*(1.95+k*.105)
        B("burgundy curtain %s %s"%(side,k),(.14,.18,2.55),
          (x,10.02,2.35),(.17+random.random()*.04,.075,.045))
B("valance header",(6.7,.27,.31),(0,9.96,3.87),(.88,.85,.62))
for i in range(19):
    ob=ball(radius=.185,center=(-3.1+i*.345,9.91,3.70),color=(.85,.82,.61))
    ob.resize((1,.45,1.25))
    scene.include("scalloped curtain "+str(i),ob)
B("blackboard surround",(2.84,.11,1.42),(.25,9.23,1.46),(.40,.32,.16))
B("green chalkboard",(2.68,.06,1.27),(.25,9.155,1.47),(.15,.29,.24))
B("chalk tray",(2.87,.19,.045),(.25,9.10,.77),(.48,.42,.27))
for i,(a,b) in enumerate([
    ((-.92,9.105,.89),(-.58,9.105,1.98)),
    ((-.63,9.10,1.12),(-.40,9.10,1.82))
]):
    scene.include("chalk line "+str(i),rod(radius=.008,start=a,end=b,color=(.58,.65,.52)))
B("blue stage poster",(1.02,.05,1.47),(2.62,9.55,1.21),(.35,.66,.75))
for i in range(8):
    B("poster marks "+str(i),(.04,.015,.84),(2.22+i*.105,9.515,1.20),(.63,.78,.73))

def desk(name,x,y,w=1.65,d=.64,h=.88):
    a=Asset(name)
    a.include("desktop",box((w,d,.095),center=(x,y,h),color=topwood))
    a.include("apron",box((w-.07,.065,.19),
                         center=(x,y-d/2+.05,h-.14),color=wood))
    for ix,xx in enumerate([x-w/2+.095,x+w/2-.095]):
        for iy,yy in enumerate([y-d/2+.075,y+d/2-.075]):
            a.include("leg %s %s"%(ix,iy),box((.065,.065,h-.075),
                      center=(xx,yy,(h-.075)/2),color=(.31,.24,.13)))
        a.include("stretcher "+str(ix),box((.05,d-.08,.055),
                  center=(xx,y,.23),color=(.34,.26,.15)))
    a.include("shelf",box((w-.19,d*.62,.055),
                         center=(x,y,.52),color=(.27,.21,.13)))
    scene.include(name,a)

def bench(name,x,y,w=1.5):
    a=Asset(name)
    a.include("seat",box((w,.28,.065),center=(x,y,.48),color=(.29,.22,.12)))
    for i,xx in enumerate([x-w/2+.10,x+w/2-.10]):
        a.include("support "+str(i),box((.065,.21,.46),
                  center=(xx,y,.23),color=(.34,.27,.16)))
    scene.include(name,a)

placements=[
    (-1.77,-3.40,1.87),(.95,-1.98,1.72),(3.12,-.37,1.53),
    (-1.72,-.67,1.72),(.87,.20,1.68),
    (-1.65,1.38,1.67),(.83,2.02,1.65),(3.05,2.32,1.52),
    (-1.58,3.22,1.58),(.78,3.70,1.60),(2.96,4.28,1.46),
    (-1.52,4.86,1.53),(.74,5.25,1.52),
    (-1.48,6.30,1.49),(.73,6.67,1.47),(2.83,6.25,1.4),
    (-3.35,.05,1.35),(-3.26,2.94,1.30),(-3.09,5.38,1.24)]
for i,(x,y,w) in enumerate(placements):
    desk("desk "+str(i),x,y,w)
    bench("bench "+str(i),x,y+.68,w-.08)
desk("teacher table",-1,8.75,1.6,.62,.91)

# Papers and books.
for i in [0,3,5,8,10,13,16]:
    x,y,w=placements[i]
    B("exercise book "+str(i),(.38,.27,.028),(x-.25,y,.945),(.65,.64,.57))
    B("paper "+str(i),(.35,.25,.008),(x-.23,y,.965),(.90,.89,.78))
    if i in [3,10,16]:
        B("red notebook "+str(i),(.29,.23,.025),(x+.29,y+.025,.948),(.44,.12,.12))

# Bags, with radii below half of each smallest dimension.
def backpack(name,x,y,color,scale=1):
    a=Asset(name)
    a.include("body",fillet_box((.43*scale,.26*scale,.64*scale),
              radius=.085*scale,center=(x,y,.34*scale),color=color))
    a.include("front pocket",fillet_box((.34*scale,.085*scale,.30*scale),
              radius=.035*scale,center=(x,y-.15*scale,.22*scale),
              color=tuple(v*.82 for v in color)))
    a.include("zipper",rod(radius=.008*scale,
              start=(x-.14*scale,y-.20*scale,.33*scale),
              end=(x+.14*scale,y-.20*scale,.33*scale),color=(.18,.25,.27)))
    a.include("handle",sweep_tube(points=[
        (x-.07*scale,y,.64*scale),(x-.07*scale,y,.73*scale),
        (x+.07*scale,y,.73*scale),(x+.07*scale,y,.64*scale)],
        radius=.018*scale,color=(.035,.055,.065)))
    for sign in [-1,1]:
        a.include("strap "+str(sign),sweep_tube(points=[
            (x+sign*.17*scale,y+.06*scale,.55*scale),
            (x+sign*.26*scale,y+.13*scale,.22*scale),
            (x+sign*.27*scale,y-.03*scale,.045),
            (x+sign*.13*scale,y-.13*scale,.035)],
            radius=.023*scale,color=(.025,.035,.04)))
    scene.include(name,a)

backpack("near blue backpack",1.34,-3.90,(.015,.29,.53),1.05)
backpack("left dark backpack",-2.84,-4.12,(.018,.045,.068),1.02)
backpack("middle black backpack",.16,-.92,(.025,.037,.045),.94)
backpack("right turquoise backpack",2.85,-1.28,(.015,.39,.53),.98)
backpack("back left blue backpack",-2.72,.16,(.025,.34,.56),.76)
satchel=fillet_box((.78,.33,.18),radius=.075,
                   center=(-1.83,-3.72,.16),color=(.02,.027,.03))
satchel.turn('z',15)
scene.include("black satchel",satchel)

# Ceiling fans.
def fan(name,x,y,z,angle):
    a=Asset(name)
    a.include("downrod",rod(radius=.022,start=(x,y,4.52),
                           end=(x,y,z+.08),color=(.16,.14,.10)))
    a.include("motor",ball(radius=.115,center=(x,y,z),color=(.17,.15,.12)))
    for k in range(3):
        blade=box((.86,.16,.025),center=(x+.48,y,z+.012),color=(.22,.20,.17))
        blade.turn('z',angle+k*120,pivot=(x,y,z))
        a.include("blade "+str(k),blade)
    scene.include(name,a)

fan("front left fan",-2.25,-4.1,4.05,18)
fan("front right fan",2.19,-3.6,4.08,-15)
fan("middle left fan",-2.07,2.5,4.04,9)
fan("middle right fan",2.12,2.8,4.04,-22)
fan("rear fan",0,8,4.04,22)

for i,(x,y) in enumerate([(-1.4,-1.5),(1.2,4.5),(-1.2,7.4)]):
    B("fluorescent housing "+str(i),(1.3,.16,.06),(x,y,4.39),(.62,.63,.58))
    B("fluorescent tube "+str(i),(1.17,.09,.035),(x,y,4.345),(.98,.98,.89))

for i,(side,y,z) in enumerate([(-1,-4.7,3.35),(-1,5.6,3.22),(1,1.4,3.30)]):
    speaker=box((.32,.49,.69),center=(side*4.02,y,z),color=(.025,.048,.044))
    speaker.turn('y',side*12)
    scene.include("wall speaker "+str(i),speaker)

for side,ys in [(-1,[-3.7,3.3,7]),(1,[-2.2,.2,4.6,7.6])]:
    for j,y in enumerate(ys):
        x=side*4.21
        B("picture frame %s %s"%(side,j),(.055,.44,.65),(x,y,3.76),(.30,.27,.19))
        B("picture paper %s %s"%(side,j),(.063,.35,.55),
          (x-side*.035,y,3.76),(.80,.81,.69))
        B("portrait %s %s"%(side,j),(.068,.18,.33),(x-side*.042,y,3.76),
          (.27,.39,.43) if side==1 else (.25,.25,.19))

realize(scene)
set_view(position=(.05,-8,1.96),target=(.05,9.3,.01),lens=23.5,sensor=36)

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.77,.80,.72,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.65
area_emitter((0,-1,4.25),power=1250,size=7,target=(0,2,0),color=(1,.96,.80))
area_emitter((-3.95,-2,2.8),power=1000,size=4,target=(1,1,1),color=(1,1,.91))
area_emitter((3.95,3,3),power=850,size=4,target=(-1,3,1),color=(1,.98,.86))
area_emitter((-3.8,6.5,2.7),power=650,size=3,target=(0,5,1),color=(1,1,.91))

sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.45
for obj in bpy.data.objects:
    if obj.type=='MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                p=mat.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value=.78
