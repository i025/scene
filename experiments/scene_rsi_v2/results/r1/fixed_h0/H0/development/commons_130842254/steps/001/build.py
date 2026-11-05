import bpy, math, random
from sceneact import *
random.seed(17)
scene = Scene("Old stone kitchen")
cream=(.69,.66,.55)
stone=(.48,.46,.37)
wood=(.34,.19,.085)
darkwood=(.19,.115,.055)
iron=(.075,.079,.065)
white=(.77,.79,.71)
ochre=(.59,.36,.12)

def add(name,node):
    scene.include(name,node)
    return node

def block(name,size,center,color):
    return add(name,box(size,center=center,color=color))

def cylinder(name,r,h,center,color):
    return add(name,rod(r,length=h,center=center,color=color))

def ring(name,x,y,z,r,color,th=.015):
    pts=[(x+r*math.cos(i*math.tau/32),y+r*math.sin(i*math.tau/32),z) for i in range(33)]
    add(name,sweep_tube(points=pts,radius=th,color=color))

# Worn, uneven paving.
block("foundation",(8,8,.16),(0,0,-.13),(.32,.32,.27))
for j in range(21):
    y=-3.8+j*.38
    for i in range(20):
        x=-3.9+i*.405+(j%2)*.20
        c=random.uniform(.39,.55)
        tile=box((.392,.365,random.uniform(.035,.055)),center=(x,y,-.025),color=(c,c*.98,c*.84))
        add("paving_%d_%d"%(j,i),tile)

# Back and side walls with deep cooking recesses.
back=box((8,.44,5.8),center=(0,3.35,2.86),color=(.77,.79,.73))
def arch_cut(cx,width,spring,rise,depth=1.1):
    a=box((width,depth,spring+.2),center=(cx,3.3,(spring-.2)/2))
    b=rod(1,length=depth,center=(cx,3.3,spring),axis='+y')
    b.resize((width/2,1,rise))
    return fuse(a,b)
back=subtract(back,arch_cut(.8,3.65,1.35,1.25),arch_cut(-2.65,2.8,1.23,.94),arch_cut(3.55,1.25,.95,.65))
add("plastered rear wall",back)
block("left plaster wall",(.28,7.4,5.8),(-4,0,2.86),(.72,.75,.69))
block("right return wall",(.24,3.2,5.8),(4,2,2.86),(.72,.74,.67))
block("main recess darkness",(3.7,.15,2.5),(.8,3.81,1.2),(.082,.08,.055))
block("left recess backing",(2.9,.12,2.2),(-2.65,3.8,1.05),(.26,.245,.18))
block("right recess darkness",(1.3,.15,1.7),(3.5,3.78,.8),(.12,.095,.063))
block("hearth stone floor",(3.7,1.1,.11),(.8,3.2,.035),(.24,.235,.18))

# Arch stones, individually jointed.
def arch_stones(name,cx,width,spring,rise,count):
    for i in range(count):
        t=(i+.5)*math.pi/count
        x=cx+width*.5*math.cos(t)
        z=spring+rise*math.sin(t)
        tangent=math.atan2(rise*math.cos(t),-width*.5*math.sin(t))
        n=box((width*math.pi/(2*count)*1.05,.49,.24),
              center=(x,3.08,z),color=(random.uniform(.43,.53),random.uniform(.42,.49),random.uniform(.34,.40)))
        n.turn(axis='+y',degrees=-math.degrees(tangent))
        add(name+str(i),n)
arch_stones("great arch stone ",.8,3.88,1.36,1.38,19)
arch_stones("left arch stone ",-2.65,2.99,1.23,1.06,15)
arch_stones("right arch stone ",3.55,1.45,.95,.75,9)
for x in (-1.15,2.76):
    for j in range(4):
        block("hearth jamb %s %s"%(x,j),(.26,.5,.34),(x,3.09,.18+j*.34),stone)

# Long masonry counter, its two dark arched compartments.
counter=box((3.0,.88,.96),center=(-2.45,2.77,.48),color=(.66,.68,.60))
for x in (-3.18,-1.82):
    cut=box((.96,1.2,.43),center=(x,2.77,.17))
    top=rod(.48,length=1.2,axis='+y',center=(x,2.77,.38))
    counter=subtract(counter,cut,top)
add("arched masonry dresser",counter)
block("dresser dark top",(3.14,1.0,.10),(-2.43,2.72,1.0),(.39,.39,.31))

# Broad central wooden worktable.
block("table slab",(3.35,2.78,.16),(0,-.15,.88),(.41,.29,.16))
for x in (-1.39,1.39):
    for y in (-1.28,.96):
        leg=box((.15,.17,.83),center=(x,y,.43),color=wood)
        leg.turn(axis='+y',degrees=(3 if x>0 else -3))
        add("table leg %s %s"%(x,y),leg)
for x in (-1.38,1.38):
    block("side apron "+str(x),(.10,2.55,.26),(x,-.15,.70),wood)
block("front apron",(2.88,.09,.24),(0,-1.35,.70),wood)
for i in range(8):
    block("table plank joint"+str(i),(.009,2.7,.004),(-1.55+i*.43,-.15,.966),(.24,.18,.10))

# Inner preparation enclosure and the central stone stove.
block("stove base",(1.07,1.09,.34),(0,.31,1.08),(.53,.49,.37))
block("stove lower plinth",(1.18,1.19,.12),(0,.31,1.30),cream)
block("stone central column",(.82,.87,1.12),(0,.31,1.91),(.65,.61,.49))
for z in (1.39,2.39,2.48):
    block("column molding "+str(z),(1.0,1.03,.075),(0,.31,z),(.70,.66,.54))
# Subtle shallow rectangular panels on the two exposed faces.
block("front column panel",(.59,.014,.78),(0,-.132,1.94),(.60,.565,.455))
block("front panel lower molding",(.65,.035,.035),(0,-.151,1.55),cream)
block("left column panel",(.014,.62,.78),(-.417,.31,1.94),(.63,.59,.475))
block("back wooden screen",(2.62,.09,.57),(0,.91,1.25),wood)
block("front wooden screen",(2.23,.10,.57),(.19,-.72,1.25),(.42,.245,.105))
block("left short screen",(.09,1.43,.55),(-1.10,.1,1.24),(.43,.27,.12))
for x,y in [(-1.1,-.72),(1.31,-.72),(-1.31,.91),(1.31,.91)]:
    block("screen upright "+str((x,y)),(.10,.10,.73),(x,y,1.27),darkwood)
    cylinder("post cap "+str((x,y)),.071,.075,(x,y,1.65),ochre)

# Bowls and earthenware are assembled with visible rounded rims.
def bowl(name,x,y,z,r=.16,col=ochre):
    b=ball(r,center=(x,y,z+r*.28),color=col)
    b.resize((1,1,.42))
    add(name+" body",b)
    cylinder(name+" hollow",r*.81,.012,(x,y,z+r*.61),tuple(v*.62 for v in col))
    ring(name+" lip",x,y,z+r*.64,r*.94,col,.018)
def plate(name,x,y,z,r=.17,col=white):
    cylinder(name+" base",r,.022,(x,y,z),col)
    ring(name+" rim",x,y,z+.018,r*.92,col,.012)
    ring(name+" inner",x,y,z+.022,r*.72,tuple(v*.88 for v in col),.006)
def pot(name,x,y,z,r=.16,h=.26,col=iron):
    cylinder(name+" body",r,h,(x,y,z+h*.5),col)
    ring(name+" mouth",x,y,z+h,r,col,.023)
    cylinder(name+" inside",r*.82,.009,(x,y,z+h+.002),tuple(v*.48 for v in col))
    for s in (-1,1):
        add(name+" handle"+str(s),sweep_tube(points=[(x+s*r*.9,y,z+h*.72),(x+s*r*1.37,y,z+h*.8),(x+s*r*1.45,y,z+h*.45),(x+s*r*.93,y,z+h*.39)],radius=.018,color=col))
def cup(name,x,y,z,r=.065,h=.15,col=ochre):
    cylinder(name+" shell",r,h,(x,y,z+h/2),col)
    cylinder(name+" dark opening",r*.76,.008,(x,y,z+h+.002),tuple(v*.46 for v in col))
    ring(name+" rim",x,y,z+h,r,col,.008)
    pts=[(x+r,y,z+h*.8),(x+r*1.65,y,z+h*.8),(x+r*1.7,y,z+h*.35),(x+r,y,z+h*.28)]
    add(name+" handle",sweep_tube(points=pts,radius=.012,color=col))
def bottle(name,x,y,z,col=(.22,.23,.12),r=.065):
    cylinder(name+" body",r,.21,(x,y,z+.105),col)
    b=ball(r,center=(x,y,z+.21),color=col)
    b.resize((1,1,.7)); add(name+" shoulder",b)
    cylinder(name+" neck",r*.40,.13,(x,y,z+.285),col)
    ring(name+" lip",x,y,z+.355,r*.45,col,.009)

# Objects on the main tabletop.
for name,x,y,r,c in [
    ("large cream platter",-.88,-1.13,.23,white),
    ("gold front bowl",.93,-1.18,.21,(.68,.43,.16)),
    ("small front bowl",.48,-1.27,.17,(.53,.40,.23)),
    ("left gold bowl",-1.41,-.67,.20,ochre),
    ("left white saucer",-1.48,-.24,.13,white),
    ("rear white dish",-.92,.99,.16,white),
    ("right dark plate",1.42,.48,.22,(.35,.35,.29))]:
    if "bowl" in name: bowl(name,x,y,.97,r,c)
    else: plate(name,x,y,.977,r,c)
for i in range(4):
    plate("stacked cream plates"+str(i),-.93,-.83,.99+i*.025,.20-i*.006,white)
for i,(x,y) in enumerate([(-1.43,.18),(-1.40,.51),(-1.30,.80),(.98,.90),(.67,-.91),(-.68,-.97)]):
    cup("table cup"+str(i),x,y,.97,r=.066,h=.13,col=white if i%2 else ochre)
pot("small pewter pot",-1.42,.78,.98,.13,.20,(.48,.53,.50))
pot("table tin jug",-1.20,.42,.98,.11,.24,(.51,.55,.50))
bottle("green table bottle",.94,-.48,.98)
bottle("brown table bottle",1.13,-.31,.98,(.29,.20,.085))
for i in range(8):
    x=-.87+i*.25
    cup("rail cup "+str(i),x,-.72,1.56,.046,.12,ochre if i%3 else white)
for i in range(5):
    cup("back rail vessels"+str(i),-1.02+i*.48,.91,1.56,.05,.12,white if i%2 else ochre)

# Food, utensils, cutting boards and folded cloth.
block("front cutting board",(1.08,.42,.035),(.50,-1.02,.99),(.48,.35,.19))
for i in range(6):
    x=random.uniform(-1.40,-.85); y=random.uniform(-1.15,-.45)
    loaf=ball(random.uniform(.07,.105),center=(x,y,1.025),color=(.49,.32,.14))
    loaf.resize((1.5,.85,.48)); add("bread roll"+str(i),loaf)
for i in range(7):
    x=.05+i*.14; y=-1.03+random.uniform(-.12,.10)
    f=ball(.09,center=(x,y,1.035),color=(.54,.55,.46))
    f.resize((1.65,.52,.26)); f.turn(axis='+z',degrees=random.uniform(-30,30)); add("fish"+str(i),f)
    tail=box((.105,.085,.018),center=(x-.13,y,1.036),color=(.43,.45,.37))
    tail.turn(axis='+z',degrees=40); add("fish tail"+str(i),tail)
for i in range(3):
    cloth=box((.46,.22,.019),center=(.58+i*.11,-1.21+i*.07,1.056+i*.007),color=(.63,.64,.55))
    cloth.turn(axis='+z',degrees=20+i*12); add("folded linen"+str(i),cloth)
for i in range(5):
    x=-1.54+i*.13
    add("wooden spoon"+str(i),rod(.012,start=(x,.17,1.01),end=(x+.18,.53,1.015),color=(.33,.22,.11)))
    b=ball(.045,center=(x+.19,.55,1.017),color=(.41,.29,.15)); b.resize((.65,1,.15)); add("spoon head"+str(i),b)

# Dresser crockery and cookware.
for i in range(11):
    x=-3.78+i*.255
    y=2.55+random.uniform(-.15,.17)
    if i%3==0: pot("dresser pot"+str(i),x,y,1.07,.13,.19,(.22,.21,.16))
    elif i%3==1: bowl("dresser bowl"+str(i),x,y,1.07,.135,white if i%2 else ochre)
    else: cup("dresser mug"+str(i),x,y,1.06,.08,.18,white)
plate("dresser plate",-3.07,2.43,1.08,.20,white)
for i in range(4):
    loaf=ball(.10,center=(-1.55+i*.11,2.63,1.13),color=(.52,.41,.25))
    loaf.resize((1.2,.8,.5)); add("dresser bread"+str(i),loaf)

# Black fire irons and cooking vessels in the far hearth.
for x in (.08,.90,1.70):
    add("fire rack upright"+str(x),rod(.024,start=(x,3.43,.18),end=(x,3.43,1.51),color=iron))
for z in (.24,.47,.70,.93,1.16):
    add("fire rack bar"+str(z),rod(.018,start=(-.10,3.40,z),end=(1.82,3.40,z),color=iron))
pot("hearth cauldron",2.10,2.90,.08,.31,.46,iron)
pot("back iron pot",1.88,3.43,.14,.24,.30,iron)
plate("cauldron lid",1.82,2.69,.55,.24,(.41,.45,.39))
for i in range(5):
    x=2.47+i*.06
    add("long fire tools"+str(i),rod(.014,start=(x,2.97,.17),end=(x-.16,3.00,1.76+i*.04),color=iron))
    ring("tool loop"+str(i),x-.16,3.00,1.78+i*.04,.047,iron,.008)
for i in range(4):
    z=.09+i*.065
    add("firewood"+str(i),rod(.06,start=(.30,3.16,z),end=(1.05,3.38,z+.03),color=(.20,.135,.065)))
# Wicker baskets and a cluster of storage pots to the right.
for k,(x,y,r) in enumerate([(2.84,2.30,.32),(3.49,2.49,.27)]):
    bowl("basket"+str(k),x,y,.04,r,(.40,.27,.13))
    for j in range(6):
        ring("basket weave%d_%d"%(k,j),x,y,.07+j*.038,r*(.81+j*.025),(.47,.33,.17),.012)
for i,(x,y,r,h) in enumerate([(3.20,2.90,.21,.32),(3.71,2.84,.25,.37),(3.58,2.21,.23,.31)]):
    pot("storage jar"+str(i),x,y,.02,r,h,(.22,.17,.105))
bowl("floor brass basin",2.93,2.99,.03,.28,(.40,.36,.23))
# Hanging pale cloth.
add("hanging towel",box((.25,.045,.57),center=(2.52,3.00,1.38),color=(.66,.67,.58)))
add("towel loop",sweep_tube(points=[(2.42,3,1.65),(2.49,3,1.88),(2.60,3,1.65)],radius=.012,color=white))

# A small group of vessels and suspended utensils at the left of the fireplace.
pot("left floor vessel",-1.20,2.76,.03,.23,.38,(.17,.20,.14))
pot("left raised pale crock",-1.24,2.88,.40,.16,.22,white)
for i in range(5):
    x=-1.53+i*.13
    add("suspended utensil stem"+str(i),rod(.012,start=(x,3.07,1.30),end=(x,3.07,2.25+random.uniform(-.07,.10)),color=iron))
    b=ball(.075,center=(x,3.065,1.30),color=(.27,.29,.24)); b.resize((.75,.25,1.25)); add("utensil head"+str(i),b)
add("utensil support",rod(.025,start=(-1.68,3.05,2.13),end=(-.85,3.05,2.13),color=darkwood))

realize(scene)

# Octagonal, stepped stone chimney hood with distinct horizontal courses.
def material(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=.86
    return m

def frustum(name,z0,z1,r0,r1,col,n=8):
    verts=[]
    for z,r in [(z0,r0),(z1,r1)]:
        for i in range(n):
            t=math.tau*i/n+math.pi/8
            verts.append((r*math.cos(t),.31+r*math.sin(t),z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(name+" material",col))
    bevel=obj.modifiers.new("soft worn edges",'BEVEL'); bevel.width=.009; bevel.segments=1
    obj.modifiers.new("weighted stone normals",'WEIGHTED_NORMAL')
    return obj
frustum("hood projecting foot",2.48,2.58,.66,.66,(.70,.66,.55))
frustum("hood sloping lower course",2.58,2.81,.65,.52,(.70,.665,.56))
frustum("hood lower joint",2.805,2.825,.535,.525,(.53,.50,.41))
frustum("hood middle course",2.825,3.12,.525,.39,(.72,.68,.57))
frustum("hood middle joint",3.115,3.135,.402,.395,(.55,.52,.44))
frustum("hood upper course",3.135,3.40,.395,.245,(.73,.69,.58))
frustum("hood upper joint",3.395,3.415,.255,.247,(.56,.53,.44))
frustum("hood crown",3.415,3.63,.247,.095,(.73,.69,.59))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.105,location=(0,.31,3.72))
bpy.context.object.name="rounded chimney finial"
bpy.context.object.scale=(.85,.85,1.22)
bpy.context.object.data.materials.append(material("finial limestone",(.70,.67,.57)))

# Quiet material variation and surface roughness.
for m in bpy.data.materials:
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs['Roughness'].default_value=.85

set_view((6.4,-8.6,9.0),target=(0,.55,1.35),lens=54,sensor=36)
area_emitter((-3,-1,7.2),power=1250,size=5,target=(0,.8,0),color=(.86,.93,1.0))
area_emitter((1,-3,5.4),power=380,size=4,target=(0,1,1),color=(1,.90,.74))
area_emitter((-.65,3.2,1.5),power=28,size=.35,target=(-.4,2.5,.8),color=(1,.43,.12))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.52,.57,.58,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=471
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
