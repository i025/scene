from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(19)
scene = Scene("Daylit diner")

cream = (.78,.79,.75)
metal = (.43,.45,.43)
upholstery = (.29,.32,.29)
dark = (.055,.065,.052)

def add(name, obj):
    scene.include(name, obj)

# Small rectangular floor tiles.
add("floor foundation", box((15,19,.12), center=(0,1.5,-.09), color=(.37,.38,.35)))
for ix in range(49):
    for iy in range(39):
        x = -7.3 + ix*.30
        y = -7.0 + iy*.46
        c = random.uniform(.235,.30)
        add("tile_%d_%d"%(ix,iy),
            box((.291,.451,.025), center=(x,y,-.015), color=(c,c*1.02,c*.96)))

# The low, white boarded ceiling.
add("ceiling", box((14.3,18,.12), center=(0,1.5,3.48), color=(.88,.89,.85)))
for k in range(108):
    y=-7.3+k*.164
    add("ceiling board joint%d"%k,
        box((14.2,.009,.006),center=(0,y,3.414),color=(.64,.66,.63)))

# Glazed rear and right walls. The glass is intentionally almost invisible.
add("rear sill",box((13,.20,.16),center=(0,9,.91),color=(.58,.60,.56)))
add("rear header",box((13,.18,.17),center=(0,9,3.18),color=metal))
add("rear low wall",box((13,.16,.83),center=(0,9,.415),color=(.73,.75,.70)))
for i,x in enumerate([-6.5,-4.3,-2.1,.1,2.3,4.5,6.5]):
    add("rear window upright%d"%i,box((.065,.12,2.35),center=(x,8.98,2.04),color=metal))
add("rear transom",box((13,.09,.045),center=(0,8.98,1.10),color=metal))
add("right low wall",box((.16,16,.83),center=(6.5,1,.415),color=(.74,.75,.71)))
add("right sill",box((.21,16,.12),center=(6.47,1,.92),color=metal))
add("right header",box((.16,16,.15),center=(6.47,1,3.19),color=metal))
for i,y in enumerate([-6,-3.6,-1.2,1.2,3.6,6,8.95]):
    add("right window upright%d"%i,box((.11,.065,2.30),center=(6.47,y,2.04),color=metal))

# Pale outdoor scenery, seen through the large windows.
add("bright rear exterior",box((30,.12,9),center=(0,15,3),color=(.91,.93,.88)))
add("bright side exterior",box((.12,30,9),center=(12,2,3),color=(.92,.94,.89)))
for i in range(33):
    x=random.uniform(-10,11)
    y=random.uniform(10.8,14.2)
    h=random.uniform(1.7,3.2)
    add("outside trunk%d"%i,rod(.035,start=(x,y,0),end=(x,y,h),color=(.48,.51,.46)))
    for j in range(5):
        p=(x+random.uniform(-.7,.7),y+random.uniform(-.4,.4),h+random.uniform(-.4,.5))
        foliage=ball(random.uniform(.35,.65),center=p,color=(.65,.69,.62))
        foliage.resize((1,1,.8))
        add("outside foliage%d_%d"%(i,j),foliage)
for i in range(4):
    add("distant building%d"%i,box((2.5,1.4,.7),center=(-6+i*3.2,11,.55),color=(.80,.82,.77)))

def booth(name,x,y,width=2.5):
    a=Asset(name)
    a.include("plinth",box((width,.67,.17),center=(x,y,.17),color=(.18,.21,.19)))
    a.include("seat",fillet_box((width,.73,.17),radius=.035,center=(x,y,.43),color=upholstery))
    a.include("back",fillet_box((width,.125,.77),radius=.025,center=(x,y-.36,.79),color=(.30,.33,.30)))
    a.include("back top piping",rod(.013,start=(x-width/2,y-.36,1.17),end=(x+width/2,y-.36,1.17),color=(.43,.45,.40)))
    add(name,a)

def table(name,x,y,w=1.45,d=1.05):
    a=Asset(name)
    a.include("dark edge",box((w,d,.065),center=(x,y,.785),color=(.12,.15,.13)))
    a.include("laminate",box((w-.018,d-.018,.023),center=(x,y,.829),color=(.72,.75,.70)))
    a.include("pedestal",rod(.055,start=(x,y,.09),end=(x,y,.77),color=(.47,.49,.46)))
    a.include("foot",rod(.28,length=.035,center=(x,y,.035),color=(.42,.44,.41)))
    add(name,a)

# Rows of long booth backs occupy the left side of the photograph.
for i,y in enumerate([-3.20,-.80,1.60,4.0,6.4,8.0]):
    booth("left booth%d"%i,-4.35,y,2.6)
for i,y in enumerate([-4.18,-1.80,.60,3.0,5.4,7.4]):
    table("left table%d"%i,-4.35,y,2.65,1.18)

def chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("base disc",rod(.245,length=.038,center=(x,y,.045),color=(.49,.51,.47)))
    a.include("base upper disc",rod(.16,length=.035,center=(x,y,.075),color=(.57,.59,.55)))
    a.include("chrome column",rod(.052,start=(x,y,.08),end=(x,y,.45),color=(.57,.60,.56)))
    a.include("seat",fillet_box((.77,.70,.13),radius=.025,center=(x,y,.49),color=upholstery))
    a.include("square upholstered back",fillet_box((.79,.12,.69),radius=.024,center=(x,y-.315,.84),color=(.32,.35,.31)))
    for side in [-1,1]:
        a.include("side panel"+str(side),
                  fillet_box((.085,.64,.36),radius=.018,center=(x+side*.355,y,.69),color=(.30,.33,.29)))
    a.turn('z',angle,pivot=(x,y,0))
    add(name,a)

# Square pedestal tables with individual upholstered swivel chairs.
for row,y in enumerate([-.10,2.55,5.15,7.35]):
    for col,x in enumerate([-.80,2.05,4.65]):
        table("dining table%d_%d"%(row,col),x,y,1.47,1.05)
        chair("near chair%d_%d"%(row,col),x,y-.94,0)
        chair("far chair%d_%d"%(row,col),x,y+.95,180)
        if col==0 and row>0:
            chair("aisle chair%d"%row,x-.99,y,-90)

# A few small tabletop objects.
for i,(x,y) in enumerate([(-.8,-.1),(2.05,2.55),(-.8,5.15),(4.65,5.15)]):
    add("ashtray%d"%i,rod(.10,length=.023,center=(x+.18,y,.855),color=(.52,.55,.50)))
    add("sugar holder%d"%i,box((.13,.10,.09),center=(x-.23,y+.12,.88),color=(.78,.79,.74)))

# Pendant lamps: narrow cylindrical necks and broad curved black shades.
def pendant(name,x,y,bottom,radius):
    a=Asset(name)
    shoulder=bottom+radius*.66
    necktop=shoulder+.40
    a.include("cord",rod(.009,start=(x,y,necktop),end=(x,y,3.42),color=(.13,.15,.12)))
    a.include("ceiling cap",rod(.075,length=.025,center=(x,y,3.405),color=(.14,.17,.13)))
    a.include("neck",rod(radius*.32,start=(x,y,shoulder),end=(x,y,necktop),color=dark))
    a.include("neck ring",rod(radius*.34,length=.035,center=(x,y,necktop-.09),color=(.22,.25,.20)))
    n=27
    for j in range(n):
        t=(j+.5)/n
        z=bottom+t*radius*.69
        r=radius*(.36+.64*math.sqrt(max(0,1-t*t)))
        a.include("shade ring%d"%j,rod(r,length=radius*.69/n+.003,center=(x,y,z),color=dark))
    a.include("white interior",rod(radius*.94,length=.012,center=(x,y,bottom-.006),color=(.84,.86,.79)))
    a.include("lower dark lip",rod(radius,length=.019,center=(x,y,bottom+.006),color=dark))
    a.include("opening",rod(radius*.94,length=.004,center=(x,y,bottom-.012),color=(.90,.91,.83)))
    add(name,a)

pendant("large foreground left shade",-4.55,-1.65,2.32,.64)
for i,y in enumerate([1.55,4.45,7.4]):
    pendant("left receding light%d"%i,-4.35,y,2.35,.37)
pendant("central pendant",-.65,4.4,2.30,.36)
pendant("central distant pendant",-.60,8.0,2.34,.25)
pendant("right large pendant",3.0,3.15,2.38,.45)
pendant("right middle pendant",4.8,5.75,2.32,.30)
pendant("right far pendant",5.6,8.25,2.32,.26)
for i,(x,y) in enumerate([(-2,5),(.8,7),(4,-1),(-5,7),(1,-3)]):
    add("ceiling recessed trim%d"%i,rod(.075,length=.006,center=(x,y,3.407),color=(.39,.43,.38)))
    add("ceiling recessed center%d"%i,rod(.059,length=.008,center=(x,y,3.400),color=(.83,.85,.79)))

# Large feathery palm at the right edge of the seating.
plant=Asset("foreground palm")
px,py=2.95,-.45
plant.include("pot",rod(.30,length=.56,center=(px,py,.28),color=(.15,.18,.13)))
plant.include("soil",rod(.28,length=.015,center=(px,py,.565),color=(.07,.09,.06)))
for k in range(19):
    angle=random.uniform(0,2*math.pi)
    reach=random.uniform(.60,1.13)
    height=random.uniform(1.3,2.35)
    start=(px+random.uniform(-.10,.10),py+random.uniform(-.10,.10),.48)
    pts=[]
    for j in range(8):
        t=j/7
        pts.append((start[0]+math.cos(angle)*reach*t*t,
                    start[1]+math.sin(angle)*reach*t*t,
                    .48+(height-.48)*t-.16*t*t))
    plant.include("curving frond%d"%k,sweep_tube(points=pts,radius=.012,color=(.13,.19,.11)))
    for j in range(2,13):
        t=j/13
        cx=start[0]+math.cos(angle)*reach*t*t
        cy=start[1]+math.sin(angle)*reach*t*t
        cz=.48+(height-.48)*t-.16*t*t
        leaflen=.29*math.sin(math.pi*t)**.65+.035
        for side in [-1,1]:
            la=angle+side*1.0
            end=(cx+math.cos(la)*leaflen,cy+math.sin(la)*leaflen,cz+.06-.12*t)
            mid=((cx+end[0])/2,(cy+end[1])/2,(cz+end[2])/2+.025)
            plant.include("leaf%d_%d_%d"%(k,j,side),
                          sweep_tube(points=[(cx,cy,cz),mid,end],radius=.012 if j<10 else .008,
                                     color=(.10,.16,.085)))
add("palm",plant)

# A low planter full of small leaves near the back.
add("rear planter",box((2.7,.40,.35),center=(-2.15,6.95,.96),color=(.22,.26,.20)))
for i in range(55):
    x=random.uniform(-3.45,-.85)
    y=random.uniform(6.77,7.12)
    z=random.uniform(1.10,1.46)
    add("rear plant stem%d"%i,rod(.008,start=(x,y,1.08),end=(x,y,z),color=(.24,.30,.20)))
    leaf=ball(.055,center=(x,y,z),color=(.29,.37,.25))
    leaf.resize((1.8,.7,.5))
    add("rear plant leaf%d"%i,leaf)

realize(scene)
set_view(position=(-3.85,-7.0,1.77),target=(-.58,7.2,1.84),lens=25.5,sensor=36)

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.83,.87,.80,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.65
area_emitter((0,8.5,2.7),power=1700,size=7,target=(0,0,0),color=(.94,1,.92))
area_emitter((6.1,2.0,2.8),power=1300,size=6,target=(-2,1,.4),color=(.94,1,.94))
area_emitter((-2,-3,3.1),power=220,size=5,target=(0,3,0))
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.35
sc.render.image_settings.color_mode='RGB'
for obj in bpy.data.objects:
    if obj.type=='MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bs=mat.node_tree.nodes.get("Principled BSDF")
                if bs:
                    bs.inputs["Roughness"].default_value=.62
