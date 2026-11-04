from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(18)
scene = Scene("Antique woodworking tool shop")
wood = (.32,.145,.052)
oak = (.52,.29,.105)
honey = (.65,.40,.17)
darkwood = (.22,.105,.038)
iron = (.075,.082,.075)
steel = (.36,.38,.35)
wall = (.76,.78,.72)
cream = (.84,.82,.68)

def add(name, node):
    scene.include(name, node)
    return node

def cube(name, size, pos, color):
    return add(name, box(size=size, center=pos, color=color))

def segment(name, a, b, width, depth, color):
    a, b = Vector(a), Vector(b)
    d = b-a
    obj = box((d.length, depth, width), center=tuple((a+b)/2), color=color)
    obj.turn('y', -math.degrees(math.atan2(d.z,d.x)))
    return add(name,obj)

def cylinder(name, a,b,r,c):
    return add(name,rod(radius=r,start=a,end=b,color=c))

# A small room, seen over a densely covered workbench.
cube('rear plaster', (6.4,.16,5.2),(0,2.75,2.55),wall)
cube('right plaster', (.16,5.7,5.2),(3.05,.0,2.55),(.81,.82,.76))
cube('left plaster', (.14,5.7,5.2),(-3.05,0,2.55),(.69,.73,.69))
cube('floor',(6.2,7,.12),(0,-.4,-.08),(.30,.26,.19))

# Tall daylight window on the left.
cube('window dark reveal',(.045,2.25,3.25),(-2.956,.15,2.39),(.20,.25,.25))
cube('blue window glass',(.03,2.12,3.10),(-2.922,.15,2.40),(.39,.63,.71))
for yy in (-.94,.15,1.24):
    cube('window upright '+str(yy),(.10,.055,3.18),(-2.88,yy,2.40),(.79,.83,.79))
for zz in (.83,2.39,3.97):
    cube('window horizontal '+str(zz),(.10,2.22,.055),(-2.88,.15,zz),(.83,.84,.78))
cube('window sill',(.24,2.38,.09),(-2.82,.15,.80),honey)

# Shelves and the visible thin pale labels along their fronts.
shelflevels=[1.17,1.78,2.40,3.03]
for i,z in enumerate(shelflevels):
    cube('back shelf '+str(i),(5.65,.46,.075),(0,2.42,z),honey)
    cube('back shelf front '+str(i),(5.66,.045,.055),(0,2.175,z-.02),(.59,.36,.14))
    cube('right shelf '+str(i),(.47,3.48,.075),(2.78,.77,z),honey)
    for x in (-2.30,-.75,.85,2.2):
        cube('label back '+str((i,x)),(.25,.012,.042),(x,2.147,z-.018),cream)
    for y in (-.52,.62,1.65):
        cube('label side '+str((i,y)),(.012,.23,.042),(2.531,y,z-.018),cream)
    for x in (-2.35,.0,2.3):
        cube('shelf support '+str((i,x)),(.045,.25,.19),(x,2.55,z-.13),(.45,.42,.33))

# Plane bodies have visible iron cutters and the characteristic raised handles.
def plane(name,x,y,z,length=.45,width=.14,angle=0,woody=True):
    a=Asset(name)
    c=random.choice([wood,oak,honey,darkwood])
    a.include('sole',box((length,width,.045),center=(x,y,z+.025),color=darkwood if woody else iron))
    a.include('body',box((length*.98,width,.115),center=(x,y,z+.09),color=c if woody else iron))
    # A diagonal cutting iron and wooden wedge.
    blade=box((.055,width*.79,.21),center=(x+.02,y,z+.21),color=iron)
    blade.turn('y',-27)
    a.include('blade',blade)
    wedge=box((.055,width*.57,.13),center=(x-.025,y-.005,z+.17),color=oak)
    wedge.turn('y',-28)
    a.include('wedge',wedge)
    if length>.33:
        a.include('front knob',rod(radius=.036,start=(x-length*.32,y,z+.14),end=(x-length*.32,y,z+.23),color=darkwood))
        a.include('knob top',ball(radius=.042,center=(x-length*.32,y,z+.23),color=c))
        a.include('handle back',rod(radius=.028,start=(x+length*.31,y,z+.14),end=(x+length*.27,y,z+.31),color=c))
        a.include('handle top',rod(radius=.028,start=(x+length*.27,y,z+.31),end=(x+length*.15,y,z+.29),color=c))
        a.include('handle front',rod(radius=.025,start=(x+length*.15,y,z+.29),end=(x+length*.16,y,z+.14),color=c))
    a.turn('z',angle,pivot=(x,y,z))
    scene.include(name,a)

# The top shelf is packed with narrow upright wooden moulding planes.
for j in range(52):
    x=-2.66+j*.103+random.uniform(-.012,.012)
    h=random.uniform(.16,.32)
    c=random.choice([wood,oak,honey,darkwood])
    cube('upright moulding plane '+str(j),(.078,.23,h),(x,2.42,3.07+h/2),c)
    ob=box((.028,.045,.14),center=(x,2.303,3.12+h*.65),color=iron)
    ob.turn('y',random.uniform(-20,15))
    add('moulding iron '+str(j),ob)
    cube('end grain '+str(j),(.048,.012,.055),(x,2.297,3.1),(.43,.26,.12))

# Middle shelves: a row of metal planes and a row of larger wooden ones.
for j in range(15):
    x=-2.55+j*.36
    plane('middle iron plane '+str(j),x,2.39,2.44,
          random.uniform(.28,.40),.15,random.uniform(-7,7),j%4==0)
for j in range(13):
    plane('lower wooden plane '+str(j),-2.52+j*.42,2.40,1.82,
          random.uniform(.34,.47),.19,random.uniform(-7,7),True)
for j in range(10):
    plane('bottom plane '+str(j),-2.4+j*.52,2.39,1.21,
          random.uniform(.43,.58),.22,random.uniform(-6,6),True)

# Tools on the perpendicular right-hand shelves.
for k,z in enumerate(shelflevels):
    for j in range(9):
        y=-.70+j*.36
        if k==3:
            cube('side tall plane '+str((k,j)),(.22,.20,random.uniform(.18,.39)),(2.78,y,z+.18),random.choice([oak,wood,darkwood]))
            blade=box((.035,.09,.22),center=(2.73,y,z+.34),color=iron)
            blade.turn('x',-18)
            add('side exposed iron '+str(j),blade)
        else:
            plane('side plane '+str((k,j)),2.78,y,z+.045,.34,.18,90, k!=0)

# Narrow racks across the window with upright handled tools.
for z in (1.62,2.59,3.50):
    cube('window rack '+str(z),(.18,2.55,.065),(-2.72,.10,z),honey)
    for j in range(8):
        yy=-1.0+j*.32
        h=random.uniform(.25,.48)
        cylinder('window handle '+str((z,j)),(-2.69,yy,z+.07),(-2.69,yy,z+h),.042,random.choice([wood,oak,darkwood]))
        cylinder('window blade '+str((z,j)),(-2.69,yy,z-.18),(-2.69,yy,z+.07),.012,steel)

# Large carpenter squares on the wall. All are actual strips of geometry.
def strip(name,x1,z1,x2,z2,w=.08,col=iron):
    segment(name,(x1,2.637,z1),(x2,2.637,z2),w,.025,col)

strip('great square left arm',-2.10,4.10,-1.18,5.00,.13)
strip('great square right arm',-1.18,5.00,-.15,3.96,.13)
strip('large square inner arm',-1.95,3.85,-1.20,4.60,.12)
strip('large square inner return',-1.20,4.60,-.31,3.71,.12)
strip('third square left',-1.65,3.66,-1.15,4.15,.14)
strip('third square right',-1.15,4.15,-.55,3.55,.14)
strip('steel square thin left',-2.09,4.12,-1.18,5.02,.018,steel)
strip('steel square thin return',-1.17,4.96,-.17,3.96,.018,steel)
strip('right tall square',.16,3.63,.16,4.70,.065)
strip('right angled square',-.29,3.98,.16,4.70,.065)
strip('upper slim square',-.56,4.27,-.56,4.79,.065)
strip('upper slim square horizontal',-.56,4.79,-.02,4.79,.065)
for i in range(8):
    x=-1.82+i*.075
    z=4.35+i*.075
    strip('square graduations '+str(i),x,z,x+.025,z-.025,.009,cream)

# Hanging dividers and calipers.
for j,(x,z,h) in enumerate(((.78,4.67,.72),(.82,3.92,.41),(1.05,3.56,.29))):
    strip('divider left '+str(j),x,z,x-.19,z-h,.026,oak if j<2 else steel)
    strip('divider right '+str(j),x,z,x+.18,z-h,.026,oak if j<2 else steel)
    cylinder('divider pivot '+str(j),(x,2.61,z),(x,2.57,z),.04,steel)
    strip('divider cross '+str(j),x-.12,z-h*.69,x+.13,z-h*.69,.016,steel)
# Mallets and hand tools high on the right.
for j,(x,z) in enumerate(((1.52,4.36),(2.08,3.76))):
    cube('hanging mallet handle '+str(j),(.065,.065,.68),(x,2.60,z),wood)
    cube('hanging mallet head '+str(j),(.42,.12,.115),(x,2.58,z+.32),darkwood if j==0 else iron)
    cube('mallet heel '+str(j),(.24,.085,.075),(x-.04,2.59,z-.35),wood)
for j in range(4):
    strip('hanging right blade '+str(j),2.48+j*.17,4.32+j*.14,2.78+j*.17,4.42+j*.14,.11,iron)

# A large wood-framed bow saw to the left beneath the racks.
segment('saw frame low',(-2.91,-.75,1.15),(-2.52,1.02,1.15),.10,.10,oak)
cylinder('saw tension',(-2.87,-.75,1.48),(-2.52,1.02,1.48),.012,iron)
for y in (-.75,1.02):
    cube('saw upright '+str(y),(.11,.11,.43),(-2.70,y,1.30),wood)

# Main foreground bench, with several overlapping boards.
cube('workbench slab',(4.95,2.45,.16),(-.10,-1.25,.87),(.40,.29,.17))
for x in (-2.25,2.05):
    cube('bench leg '+str(x),(.16,.17,.85),(x,-.75,.42),darkwood)
for i in range(8):
    cube('bench plank seam '+str(i),(.012,2.42,.006),(-2.42+i*.64,-1.25,.953),(.22,.16,.095))
cube('rear bench raised board',(2.85,.40,.13),(.24,-.02,1.08),oak)
cube('large rear block',(.30,.42,.43),(1.30,-.03,1.17),oak)
cube('left vise block',(.25,.35,.38),(-1.92,-.60,.94),wood)

# Long planes and spare wooden tool bodies across the table.
plane('large bench plane rear',.35,-.08,1.16,1.05,.26,-5,True)
plane('bench plane left',-1.45,-1.22,.97,.78,.23,83,True)
plane('bench plane diagonal',.18,-.85,.97,.93,.25,17,True)
plane('black metal plane right',1.73,-.16,.99,.67,.23,-11,False)
plane('wood plane front',-.53,-1.80,.97,.67,.21,12,True)
for j in range(7):
    x=random.uniform(-1.6,1.5)
    y=random.uniform(-1.9,-.30)
    ob=box((random.uniform(.35,.9),.075,.045),center=(x,y,1.015),color=random.choice([oak,honey,wood]))
    ob.turn('z',random.uniform(-65,65))
    add('loose wood strip '+str(j),ob)

# Chisels, files and gouges laid in a fan on the left of the bench.
for j in range(12):
    x=-2.17+j*.115
    y=-1.52+random.uniform(-.15,.13)
    a=Asset('bench chisel '+str(j))
    a.include('long steel blade',box((.045,.66,.022),center=(x,y-.30,1.02),color=steel))
    a.include('blade spine',box((.018,.66,.015),center=(x,y-.30,1.039),color=(.55,.57,.51)))
    a.include('ferrule',rod(radius=.035,start=(x,y+.025,1.04),end=(x,y+.11,1.04),color=iron))
    a.include('wood handle',rod(radius=.048,start=(x,y+.10,1.04),end=(x,y+.38,1.04),color=random.choice([wood,oak,honey])))
    a.include('rounded end',ball(radius=.048,center=(x,y+.38,1.04),color=oak))
    a.turn('z',random.uniform(-17,17),pivot=(x,y,1.02))
    scene.include('bench chisel '+str(j),a)

# Dark lidded glue pot.
cylinder('glue pot body',(-.97,-.43,.97),(-.97,-.43,1.30),.18,(.065,.085,.075))
cylinder('glue pot rim',(-.97,-.43,1.30),(-.97,-.43,1.33),.195,steel)
cylinder('glue pot lid',(-.97,-.43,1.33),(-.97,-.43,1.36),.17,iron)
cylinder('glue pot lid knob',(-.97,-.43,1.35),(-.97,-.43,1.41),.025,wood)
add('pot arch handle',sweep_tube(points=[(-1.15,-.43,1.22),(-1.15,-.43,1.56),(-.98,-.43,1.66),(-.80,-.43,1.55),(-.79,-.43,1.22)],radius=.012,color=steel))
# A cloudy pale bottle.
cylinder('bottle body',(-.28,-.46,.98),(-.28,-.46,1.37),.105,(.58,.61,.48))
add('bottle shoulder',ball(radius=.105,center=(-.28,-.46,1.36),color=(.58,.61,.48)))
cylinder('bottle neck',(-.28,-.46,1.37),(-.28,-.46,1.51),.045,(.66,.68,.55))
cylinder('bottle cork',(-.28,-.46,1.49),(-.28,-.46,1.53),.048,cream)
cube('bottle paper label',(.14,.012,.19),(-.28,-.561,1.21),(.78,.76,.62))

# Metal tray with loose screws and curled shavings.
trayx,trayy=.75,-1.65
cylinder('tray base',(trayx,trayy,.98),(trayx,trayy,1.01),.43,(.26,.28,.26))
for j in range(44):
    ang=j*math.tau/44
    cylinder('tray rim '+str(j),
             (trayx+.425*math.cos(ang),trayy+.425*math.sin(ang),1.00),
             (trayx+.425*math.cos(ang),trayy+.425*math.sin(ang),1.18),.018,steel)
for j in range(39):
    x=trayx+random.uniform(-.29,.29)
    y=trayy+random.uniform(-.29,.29)
    ang=random.random()*math.tau
    cylinder('tray scrap '+str(j),(x,y,1.06),(x+.10*math.cos(ang),y+.10*math.sin(ang),1.075),.009,(.59,.61,.55))
    if j%3==0:
        add('curled shaving '+str(j),sweep_tube(points=[(x+.035*math.cos(t*.7),y+.035*math.sin(t*.7),1.07+t*.002) for t in range(12)],radius=.007,color=(.67,.64,.49)))

# Wooden mallets, squares, and marking gauges in the near right corner.
for j,(x,y,ang) in enumerate(((1.57,-1.65,-28),(1.92,-1.15,23))):
    a=Asset('bench mallet '+str(j))
    a.include('handle',rod(radius=.035,start=(x,y-.45,1.04),end=(x,y+.30,1.04),color=honey))
    a.include('head',box((.39,.21,.19),center=(x,y+.23,1.09),color=oak))
    a.turn('z',ang,pivot=(x,y,1.04))
    scene.include('bench mallet '+str(j),a)
a=Asset('foreground wooden square')
a.include('long limb',box((1.31,.09,.065),center=(1.31,-2.14,1.04),color=honey))
a.include('cross limb',box((.11,.64,.065),center=(1.85,-1.87,1.04),color=honey))
a.turn('z',-20)
scene.include('foreground wooden square',a)
for j in range(3):
    cube('small block '+str(j),(.27,.17,.14),(1.17+j*.31,-.77,1.05),random.choice([oak,darkwood,wood]))
    cylinder('marking gauge stem '+str(j),(1.20+j*.28,-1.03,1.12),(1.20+j*.28,-.47,1.12),.025,oak)

# A few paper inventory labels and scattered metal tools.
for j in range(9):
    x=random.uniform(-2.0,1.7)
    y=random.uniform(-2.20,-.65)
    ob=box((.19,.065,.007),center=(x,y,1.015),color=cream)
    ob.turn('z',random.uniform(-30,30))
    add('paper tag '+str(j),ob)
for j in range(5):
    x=random.uniform(-.7,.6)
    y=random.uniform(-2.1,-1.2)
    cylinder('loose drill '+str(j),(x,y,1.04),(x+.36,y+.18,1.04),.014,steel)

realize(scene)

# Slightly rounded edges catch the diffuse window light.
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH' and len(ob.data.polygons) <= 12:
        mod=ob.modifiers.new('Small worn edges','BEVEL')
        mod.width=.006
        mod.segments=1
        ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf=mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Roughness'].default_value=.72

set_view((-.35,-5.35,2.73),(0,1.18,2.25),lens=29,sensor=36)
area_emitter((-3,-.50,3.3),power=1050,size=3.3,target=(0,1,1.6),color=(.80,.91,1))
area_emitter((.2,-2.4,4.7),power=750,size=4.0,target=(0,1,1.6),color=(1,.91,.77))
area_emitter((2,1,4.8),power=350,size=2.8,target=(0,.5,1.6))
world=bpy.context.scene.world
world.color=(.26,.28,.26)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=384
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
