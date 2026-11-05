import bpy, math, random
from sceneact import *
from mathutils import Vector
random.seed(24)

scene = Scene("Old stone kitchen")
cream=(.70,.67,.55)
plaster=(.72,.74,.68)
stone=(.43,.42,.34)
wood=(.33,.19,.075)
darkwood=(.20,.13,.065)
ceramic=(.66,.69,.61)
ochre=(.55,.32,.10)
metal=(.18,.20,.17)

def add(name, node):
    scene.include(name,node)
    return node
def cube(name,size,loc,col):
    return add(name,box(size,center=loc,color=col))
def cylinder(name,r,p,q,c):
    return add(name,rod(r,start=p,end=q,color=c))
def tube(name,pts,r,c):
    return add(name,sweep_tube(points=pts,radius=r,color=c))
def ring(name,x,y,z,r,thick,c):
    return tube(name,[(x+r*math.cos(i*2*math.pi/48),y+r*math.sin(i*2*math.pi/48),z) for i in range(49)],thick,c)

# Uneven, worn stone paving.
cube("foundation",(10,10,.16),(0,0,-.13),(.27,.27,.22))
for j in range(25):
    for i in range(25):
        x=(i-12)*.39
        y=(j-12)*.39
        if abs(x)<2.65 and abs(y+.25)<2.6:
            continue
        c=random.choice([(.32,.32,.26),(.36,.35,.28),(.39,.38,.30),(.29,.30,.25),(.41,.39,.31)])
        cube("old paving %d %d"%(i,j),(.378,.378,random.uniform(.055,.075)),(x,y,-.035),c)
for j in range(11):
    for i in range(11):
        x=(i-5)*.48
        y=(j-5)*.48-.25
        c=random.choice([(.51,.49,.39),(.56,.54,.44),(.46,.46,.37),(.60,.57,.46),(.53,.51,.41)])
        ob=cube("large flag %d %d"%(i,j),(.467,.467,.07),(x,y,.005+random.uniform(-.009,.009)),c)
        ob.turn('z',random.uniform(-1.1,1.1))

# Enclosing plaster walls, with broad arched kitchen recesses.
back_y=3.55
wall=box((9.6,.44,6.6),center=(0,back_y,3.3),color=plaster)
def arch_cutter(cx,cy,w,spring,depth):
    a=box((w,depth,spring+.12),center=(cx,cy,spring/2-.06))
    b=rod(w/2,start=(cx,cy-depth/2,spring),end=(cx,cy+depth/2,spring))
    return fuse(a,b)
wall=subtract(wall,arch_cutter(.9,back_y,4.1,1.35,1.0),
              arch_cutter(4.0,back_y,1.7,1.05,1.0))
add("rear plaster wall",wall)
cube("black hearth interior",(4.15,.12,2.9),(.9,3.94,1.45),(.105,.105,.075))
cube("right dark recess",(1.6,.12,1.8),(4.0,3.94,.9),(.16,.14,.10))
cube("left plaster wall",(.3,8.2,6.6),(-4.75,.05,3.3),plaster)

def arch_stones(cx,cy,r,spring,width,depth):
    for k in range(17):
        a=(k+.5)*math.pi/17
        x=cx+r*math.cos(a)
        z=spring+r*math.sin(a)
        ob=box((width,depth,.37),center=(x,cy,z),color=random.choice([
            (.43,.42,.34),(.47,.45,.36),(.50,.48,.39),(.39,.39,.32)]))
        ob.turn('y',90-math.degrees(a))
        add("arch voussoir %.2f %d"%(cx,k),ob)
    for side in [-1,1]:
        for j in range(4):
            cube("arch upright %.2f %d %d"%(cx,side,j),(.30,depth,.37),
                 (cx+side*r,cy,.18+j*.36),(.44,.43,.35))
arch_stones(.9,3.28,2.12,1.35,.40,.40)
arch_stones(4.0,3.27,.91,1.05,.27,.38)

# Left-hand masonry preparation counter, with two low arch openings.
counter=box((3.65,1.04,1.02),center=(-2.72,2.56,.51),color=(.64,.66,.59))
for x in [-3.66,-2.06]:
    counter=subtract(counter,arch_cutter(x,2.55,1.12,.18,1.5))
add("arched white counter",counter)
cube("counter stone slab",(3.86,1.19,.12),(-2.72,2.55,1.08),(.48,.48,.40))

# Stone border running above the left work area.
for i in range(12):
    x=-4.7+i*.31
    z=2.23+.70*math.sin(i/11*math.pi)
    ob=cube("left low arch edging %d"%i,(.38,.30,.27),(x,3.24,z),(.45,.44,.36))
    ob.turn('y',-30*math.cos(i/11*math.pi))
cube("left recess shadow",(3.7,.10,1.05),(-2.8,3.31,1.67),(.30,.30,.23))

# Large central stone chimney and its stepped octagonal hood.
cx,cy=0,.05
cube("chimney foot",(1.08,1.07,.18),(cx,cy,.12),(.48,.46,.36))
cube("chimney base",( .88,.88,.92),(cx,cy,.63),(.48,.46,.36))
cube("base ledge",(1.09,1.08,.14),(cx,cy,1.15),(.62,.58,.46))
cube("main chimney shaft",(.83,.83,1.55),(cx,cy,1.98),(.61,.58,.47))
cube("shaft top molding",(1.02,1.02,.13),(cx,cy,2.80),(.67,.63,.51))
cube("shaft narrow molding",(.95,.95,.08),(cx,cy,2.91),(.65,.61,.50))
# Subtle joints on the dressed stone shaft.
for z in [1.42,2.01,2.59]:
    cube("shaft horizontal joint %.2f"%z,(.836,.008,.014),(cx,cy-.419,z),(.48,.46,.38))
cube("shaft vertical joint",(.014,.008,.52),(cx+.12,cy-.42,1.72),(.51,.48,.39))

# Heavy timber work tables arranged around the chimney.
for name,x,y,sx,sy in [
    ("front",0,-1.24,3.08,.83),
    ("left",-1.12,-.03,.81,1.65),
    ("right",1.13,-.03,.81,1.65)
]:
    cube(name+" table top",(sx,sy,.14),(x,y,1.02),(.40,.25,.115))
    for a in range(max(2,int(sx/.22))):
        xx=x-sx/2+(a+.5)*sx/max(2,int(sx/.22))
        cube(name+" plank seam "+str(a),(.012,sy,.006),(xx,y,1.094),(.23,.14,.065))
    cube(name+" apron",(sx,.065,.20),(x,y-sy/2+.05,.86),wood)
    for dx in [-sx/2+.12,sx/2-.12]:
        for dy in [-sy/2+.12,sy/2-.12]:
            cube(name+" leg "+str(dx)+str(dy),(.13,.14,.93),(x+dx,y+dy,.47),wood)
    cube(name+" lower stretcher",(sx-.13,.09,.11),(x,y,.28),darkwood)

# Raised wooden dividers holding utensils and jars.
cube("left raised shelf",(.12,1.77,.47),(-.77,.17,1.33),(.43,.27,.12))
cube("rear left shelf ledge",(.29,1.78,.08),(-.84,.17,1.58),(.43,.29,.15))
cube("rear right divider",(1.28,.11,.49),(.87,.72,1.34),(.37,.22,.09))
cube("right upright divider",(.10,1.16,.45),(.77,-.25,1.32),(.41,.25,.10))
cube("right shelf ledge",(.27,1.27,.07),(.79,-.20,1.57),(.43,.28,.12))

# Objects with turned ceramic profiles will be made after realization.
vessels=[]
def vessel(name,x,y,z,r,h,col,kind="bowl"):
    vessels.append((name,x,y,z,r,h,col,kind))
def plate(name,x,y,z,r,col=ceramic):
    vessel(name,x,y,z,r,.055,col,"plate")
def jug(name,x,y,z,r,h,col):
    vessel(name,x,y,z,r,h,col,"jug")
    pts=[]
    for i in range(18):
        a=-math.pi/2+i*math.pi/17
        pts.append((x+r*.76+r*.65*math.cos(a),y,z+h*.53+h*.29*math.sin(a)))
    tube(name+" handle",pts,.023,col)

# Front table: bread, dishes, trenchers and pale fish.
for name,x,y,r,c in [
    ("front golden bowl",.62,-1.57,.23,(.64,.42,.17)),
    ("front cream bowl",.16,-1.63,.19,(.62,.56,.40)),
    ("large ochre basin",-1.03,-1.19,.23,(.63,.42,.16)),
    ("white bowl",-1.39,-.90,.15,(.69,.74,.68)),
    ("dark food bowl",-1.03,-1.58,.20,(.29,.23,.13)),
    ("back serving dish",1.37,-.08,.23,(.53,.55,.48))]:
    vessel(name,x,y,1.10,r,.13,c)
plate("small white plate",-1.40,-1.29,1.105,.14,(.72,.77,.73))
plate("bread platter",-.57,-1.35,1.105,.22,(.56,.40,.20))
for i in range(4):
    o=ball(.12,center=(-.65+i*.09,-1.36+random.uniform(-.07,.07),1.17),color=(.62,.39,.15))
    o.resize((1.15,.75,.46))
    add("bread roll "+str(i),o)
for i in range(5):
    o=ball(.09,center=(-1.07+random.uniform(-.09,.09),-1.60+random.uniform(-.08,.08),1.20),color=(.24,.16,.08))
    o.resize((1.0,.60,.5));add("brown food "+str(i),o)
cube("fish cutting board",(.94,.62,.035),(.85,-1.13,1.115),(.40,.32,.21))
for i in range(6):
    x=.51+(i%3)*.25
    y=-1.34+(i//3)*.27
    ob=ball(.15,center=(x,y,1.17),color=(.52+.025*i,.54+.02*i,.48+.02*i))
    ob.resize((1.4,.35,.27))
    ob.turn('z',random.uniform(-25,25))
    add("whole fish "+str(i),ob)
    tail=box((.13,.12,.018),center=(x-.21,y,1.17),color=(.45,.47,.41))
    tail.turn('z',35);add("fish tail "+str(i),tail)
    add("fish eye "+str(i),ball(.012,center=(x+.145,y-.025,1.205),color=(.10,.11,.08)))
plate("stacked white dishes",-.68,-.56,1.10,.23,(.77,.81,.75))
for i in range(3):
    plate("stacked dish "+str(i),-.68,-.56,1.12+i*.028,.23-i*.008,(.74,.78,.73))
for i in range(5):
    jug("table little jug "+str(i),-1.32+random.uniform(-.14,.16),-.50+i*.21,1.10,.09,.20,random.choice([ceramic,ochre,(.48,.51,.44)]))
for i in range(7):
    vessel("shelf cup "+str(i),.79,-.65+i*.19,1.61,.060,.11,
            random.choice([(.57,.41,.19),(.65,.68,.58),(.30,.33,.25)]),"cup")
for i in range(4):
    vessel("left shelf bowl "+str(i),-.85,-.40+i*.42,1.63,.12,.065,(.57,.63,.58))
for i in range(3):
    jug("back shelf jar "+str(i),.45+i*.35,.72,1.63,.075,.22,random.choice([ochre,ceramic,(.24,.27,.19)]))
# A few small utensils across the work surface.
for i in range(5):
    x=-.45+i*.15
    cylinder("wooden utensil "+str(i),.015,(x,-1.12,1.13),(x+.24,-.95,1.14),(.34,.25,.12))

# Pottery and cooking equipment on the long wall counter.
for i in range(13):
    x=-4.36+i*.25
    y=2.48+random.uniform(-.25,.24)
    c=random.choice([(.67,.69,.62),(.48,.40,.27),(.60,.56,.43),(.33,.31,.23)])
    if i%3==0:
        jug("counter jug "+str(i),x,y,1.15,.11,.25,c)
    else:
        vessel("counter bowl "+str(i),x,y,1.15,.13,.12,c)
for i in range(3):
    plate("counter plates "+str(i),-3.9+i*.55,2.18,1.16,.15,(.57,.60,.55))
cube("chopping block",(.57,.38,.07),(-1.77,2.52,1.17),(.32,.23,.12))
for i in range(4):
    o=ball(.1,center=(-1.95+i*.14,2.48,1.26),color=(.41,.31,.17))
    o.resize((1,.7,.55));add("loaf on counter "+str(i),o)

# Iron hearth grate and andirons in the shadowed recess.
for i in range(9):
    cylinder("grate bar "+str(i),.022,(-.45+i*.31,3.32,.24),(-.45+i*.31,3.32,1.36),(.075,.083,.067))
for z in [.34,.65,.97,1.25]:
    cylinder("grate horizontal "+str(z),.025,(-.6,3.30,z),(2.15,3.30,z),(.075,.08,.063))
for i in range(6):
    log=rod(.08,start=(-.3+i*.30,3.09,.14),end=(.05+i*.30,3.52,.17),color=(.13,.09,.045))
    add("hearth wood "+str(i),log)
# Small warm glow at the left side of the fireplace.
for i in range(3):
    o=ball(.055,center=(-.70+i*.07,3.30,.90+i*.07),color=(.95,.34,.045))
    o.resize((.65,.7,2.1));add("embers "+str(i),o)

# Tall tripod, cauldron, baskets, buckets, and jars around the room.
for x,y in [(2.95,2.95),(-1.1,3.03)]:
    vessel("large iron pot "+str(x),x,y,.12,.26,.39,(.12,.15,.12),"pot")
    ring("pot rim "+str(x),x,y,.51,.26,.025,(.27,.28,.22))
for x,y,r in [(3.10,1.97,.33),(3.63,1.77,.25),(4.19,2.08,.30)]:
    vessel("floor basket "+str(x),x,y,.04,r,.26,(.35,.23,.12),"basket")
    for k in range(6):
        ring("basket weave "+str(x)+str(k),x,y,.07+k*.035,r*(.78+k*.035),.011,(.43,.31,.17))
for i in range(5):
    x=3.65+(i%3)*.34
    y=2.64+(i//3)*.35
    vessel("storage crock "+str(i),x,y,.04,.19,.30+random.random()*.16,
            random.choice([(.21,.20,.14),(.30,.24,.15),(.41,.40,.31)]),"pot")
for i in range(3):
    plate("leaning lid "+str(i),2.81+i*.21,2.57,.42+i*.12,.17,(.51,.56,.49))
# Suspended implements.
cylinder("utensil rack",.035,(-1.6,3.12,2.73),(-.80,3.12,2.73),(.20,.19,.13))
for i in range(5):
    x=-1.55+i*.16
    cylinder("hanging handle "+str(i),.018,(x,3.10,2.85),(x,3.10,2.31),(.23,.24,.18))
    ob=ball(.072,center=(x,3.10,2.28),color=(.29,.31,.24))
    ob.resize((.8,.25,1.2));add("hanging ladle "+str(i),ob)
cylinder("right tool pole",.025,(3.12,3.00,.35),(3.12,3.00,1.95),(.39,.36,.25))
tube("hanging white cloth",[(3.10,2.99,1.88),(2.99,2.97,1.65),(3.00,2.94,1.38),(3.15,2.94,1.35),(3.21,2.97,1.63),(3.10,2.99,1.88)],.045,(.66,.66,.55))

realize(scene)

# Low-polygon stone hood, with a tall conical, tiered silhouette.
def material(name,col,roughness=.85):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Roughness'].default_value=roughness
    return m
def tapered(name,z0,z1,r0,r1,col,n=8):
    verts=[]
    for z,r in [(z0,r0),(z1,r1)]:
        for i in range(n):
            a=2*math.pi*(i+.5)/n
            verts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material(name,col))
    bevel=ob.modifiers.new("soft dressed edges",'BEVEL');bevel.width=.009;bevel.segments=1
tapered("hood lower cornice",2.93,3.04,.66,.69,(.67,.63,.52))
tapered("hood sloping lower tier",3.04,3.37,.69,.54,(.68,.65,.55))
tapered("hood first seam",3.37,3.40,.55,.55,(.53,.50,.42))
tapered("hood middle tier",3.40,3.70,.55,.38,(.69,.65,.55))
tapered("hood second seam",3.70,3.73,.39,.39,(.55,.52,.44))
tapered("hood upper tier",3.73,4.04,.39,.15,(.69,.65,.54))
tapered("hood apex",4.04,4.17,.15,.07,(.67,.63,.52))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.11,location=(cx,cy,4.23))
bpy.context.object.scale=(.82,.82,1.20)
bpy.context.object.data.materials.append(material("finial stone",(.70,.67,.57)))

# Turned hollow pottery, separate meshes with visible lips and interiors.
for name,x,y,z,r,h,col,kind in vessels:
    if kind=="plate":
        profile=[(0,.012),(.55,.012),(.80,.18),(1,.72),(1,1),(.91,.90),(.73,.33),(.45,.16),(0,.16)]
    elif kind=="jug":
        profile=[(0,0),(.65,0),(.87,.12),(1,.43),(.91,.68),(.49,.83),(.43,1),(.58,1.02),(.57,1.07),(.35,1.07),(.34,.84),(.69,.63),(.75,.27),(.48,.14),(0,.14)]
    elif kind=="cup":
        profile=[(0,0),(.70,0),(.85,.09),(1,1),(.86,1.02),(.72,.16),(0,.13)]
    elif kind in ["pot","basket"]:
        profile=[(0,0),(.70,0),(.96,.20),(1,.70),(.90,1),(.77,1),(.84,.70),(.77,.22),(0,.15)]
    else:
        profile=[(0,0),(.50,0),(.76,.16),(1,.80),(1,1),(.91,1.04),(.84,.72),(.62,.21),(0,.13)]
    count=40
    verts=[]
    for rr,zz in profile:
        for i in range(count):
            a=i*2*math.pi/count
            verts.append((x+rr*r*math.cos(a),y+rr*r*math.sin(a),z+zz*h))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(count):
            faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material(name+" glaze",col,.38 if kind!="basket" else .9))
    for p in mesh.polygons:p.use_smooth=True

# Surface variation gives the plaster and masonry a quiet aged finish.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:continue
    color=bs.inputs['Base Color'].default_value
    if sum(color[:3])>1.2:
        nodes=mat.node_tree.nodes
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=7
        noise.inputs['Detail'].default_value=3
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.17
        bump.inputs['Distance'].default_value=.035
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view((7.4,-10.4,10.4),(-.05,.35,1.65),lens=48,sensor=36)
area_emitter((-3.3,-3.1,8.0),power=1450,size=5.0,target=(0,.6,.6),color=(.91,.96,1.0))
area_emitter((1,-.6,6.3),power=420,size=4,target=(0,1,1),color=(1,.90,.72))
bpy.ops.object.light_add(type='POINT',location=(-.62,3.10,1.0))
bpy.context.object.data.energy=16
bpy.context.object.data.color=(1,.32,.07)
bpy.context.object.data.shadow_soft_size=.15

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.39,.44,.45,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.38
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=471
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.2
sc.render.image_settings.file_format='PNG'
