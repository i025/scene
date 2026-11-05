import bpy, math, random
from sceneact import *
random.seed(18)

scene = Scene("Historic kitchen")
CSTONE=(.53,.50,.40)
PLASTER=(.76,.78,.72)
WOOD=(.38,.235,.105)
DARK=(.13,.14,.105)
POT=(.64,.68,.61)
items=[]
pots=[]

def put(name,node):
    scene.include(name,node)
    return node

def block(name,size,loc,col):
    return put(name,box(size,center=loc,color=col))

def bar(name,a,b,r,col):
    return put(name,rod(r,start=a,end=b,color=col))

def loop(name,x,y,z,r,t,col):
    pts=[(x+r*math.cos(i*math.tau/24),y+r*math.sin(i*math.tau/24),z) for i in range(25)]
    return put(name,sweep_tube(points=pts,radius=t,color=col))

def vessel(name,x,y,z,r,h,col=POT,kind="bowl"):
    pots.append((name,x,y,z,r,h,col,kind))

def jug(name,x,y,z,r,h,col):
    vessel(name,x,y,z,r,h,col,"jug")
    pts=[]
    for i in range(13):
        a=-math.pi/2+i*math.pi/12
        pts.append((x+r*.76+r*.64*math.cos(a),y,z+h*.54+h*.28*math.sin(a)))
    put(name+" handle",sweep_tube(points=pts,radius=.018,color=col))

# Main architecture.
block("floor foundation",(9.5,10,.14),(0,0,-.10),(.32,.32,.26))
block("left wall",(.22,8.0,6.2),(-4.5,.5,3.1),PLASTER)
block("rear upper plaster",(9.4,.32,3.05),(0,3.6,4.68),PLASTER)
block("rear left pier",(.75,.44,3.2),(-4.25,3.56,1.6),(.69,.70,.62))
block("hearth left pier",(.52,.45,1.55),(-1.43,3.51,.775),CSTONE)
block("hearth right pier",(.48,.48,1.55),(2.83,3.51,.775),CSTONE)
block("far right pier",(.36,.44,1.4),(4.50,3.55,.7),CSTONE)
block("dark fireplace back",(4.05,.08,2.5),(.71,3.94,1.25),(.12,.12,.085))
block("small recess dark back",(1.28,.08,1.9),(3.72,3.94,.95),(.18,.16,.11))

# Segmented arches, with plaster above them filled after realization.
arch_specs=[(.70,2.12,1.10,18),(-3.0,1.42,1.22,13),(3.73,.72,.92,11)]
for ai,(cx,r,spring,n) in enumerate(arch_specs):
    for k in range(n):
        a=math.pi*(k+.5)/n
        ob=box((math.pi*r/n+.025,.43,.27),
               center=(cx+r*math.cos(a),3.34,spring+r*math.sin(a)),
               color=random.choice([(.43,.42,.34),(.48,.46,.37),(.54,.51,.41)]))
        ob.turn('y',90-math.degrees(a))
        put("arch stone %d %d"%(ai,k),ob)

# Pale counter on the left, with two dark arched bays.
block("counter slab",(3.32,1.03,.12),(-2.96,2.67,1.08),(.57,.58,.50))
for i,x in enumerate([-4.49,-3.02,-1.43]):
    block("counter pier "+str(i),(.24,.95,1.02),(x,2.66,.51),(.65,.67,.60))
for i,x in enumerate([-3.76,-2.20]):
    block("counter opening darkness "+str(i),(1.24,.06,.84),(x,3.09,.42),(.18,.21,.16))
    for k in range(9):
        a=(k+.5)*math.pi/9
        q=box((.25,.92,.22),center=(x+.63*math.cos(a),2.67,.22+.63*math.sin(a)),color=(.64,.66,.59))
        q.turn('y',90-math.degrees(a))
        put("counter arch %d %d"%(i,k),q)

# Central square stone column and its cornices.
block("chimney plinth",(1.02,1.02,.18),(0,.18,.12),(.49,.46,.36))
block("chimney lower shaft",(.82,.82,.87),(0,.18,.64),(.55,.52,.41))
block("chimney waist ledge",(1.03,1.03,.13),(0,.18,1.12),(.66,.61,.48))
block("chimney upper shaft",(.79,.79,1.42),(0,.18,1.88),(.64,.60,.49))
block("chimney capital",(1.00,1.00,.12),(0,.18,2.64),(.69,.64,.51))
block("chimney capital upper",(1.09,1.09,.09),(0,.18,2.74),(.68,.63,.51))
for z in [1.38,1.91,2.42]:
    block("stone joint "+str(z),(.796,.009,.012),(0,-.22,z),(.53,.49,.40))
block("vertical stone joint",(.011,.009,.49),(.13,-.223,1.65),(.54,.50,.41))

# Timber work surface surrounding the column.
tables=[("front",0,-1.19,3.18,.80),
        ("left",-1.14,.03,.80,1.68),
        ("right",1.14,.03,.80,1.68)]
for name,x,y,sx,sy in tables:
    block(name+" thick top",(sx,sy,.13),(x,y,.94),WOOD)
    block(name+" front apron",(sx,.08,.22),(x,y-sy/2+.05,.79),(.31,.18,.07))
    for dx in [-sx/2+.13,sx/2-.13]:
        for dy in [-sy/2+.12,sy/2-.12]:
            block(name+" leg "+str(dx)+str(dy),(.12,.13,.85),(x+dx,y+dy,.425),(.32,.18,.065))
    block(name+" stretcher",(sx-.16,.08,.09),(x,y,.24),(.29,.17,.07))
block("left tall divider",(.10,1.75,.43),(-.76,.17,1.21),(.44,.28,.13))
block("left shelf edge",(.27,1.78,.07),(-.80,.17,1.46),(.45,.29,.14))
block("right tall divider",(.10,1.58,.44),(.77,.12,1.22),(.40,.245,.10))
block("right shelf edge",(.27,1.60,.07),(.80,.12,1.47),(.45,.29,.13))

# Table pottery and food.
vessel("ochre mixing bowl",-1.07,-1.12,1.015,.235,.13,(.65,.43,.17))
vessel("front golden bowl",.61,-1.51,1.015,.235,.12,(.68,.46,.21))
vessel("front plain bowl",.12,-1.53,1.015,.19,.13,(.58,.52,.37))
vessel("brown food dish",-.92,-1.49,1.015,.19,.075,(.35,.27,.15))
vessel("bread plate",-.57,-1.19,1.015,.22,.05,(.58,.43,.23),"plate")
vessel("small white bowl",-1.42,-1.24,1.015,.13,.07,(.74,.78,.71))
vessel("small grey dish",-1.36,-.93,1.015,.13,.045,(.64,.70,.65),"plate")
for i in range(4):
    vessel("stacked white plate "+str(i),-.68,-.53,1.015+i*.024,.22-i*.005,.045,(.77,.81,.76),"plate")
for i in range(5):
    x=-.73+random.random()*.30
    y=-1.22+random.random()*.13
    ob=ball(.105,center=(x,y,1.09),color=(.64,.43,.20))
    ob.resize((1.15,.65,.45))
    put("bread roll "+str(i),ob)
for i in range(5):
    ob=ball(.076,center=(-.99+random.random()*.16,-1.55+random.random()*.13,1.10),color=(.30,.21,.11))
    ob.resize((1.1,.65,.5))
    put("food in dish "+str(i),ob)

block("fish board",(.99,.62,.032),(.83,-1.15,1.018),(.46,.37,.25))
for i in range(6):
    x=.48+(i%3)*.26
    y=-1.32+(i//3)*.25
    ob=ball(.13,center=(x,y,1.065),color=(.64,.65,.57))
    ob.resize((1.5,.37,.25))
    ob.turn('z',-18+(i%3)*12)
    put("fish "+str(i),ob)
    tail=box((.12,.10,.015),center=(x-.19,y,1.065),color=(.51,.54,.46))
    tail.turn('z',45)
    put("tail "+str(i),tail)
    put("fish eye "+str(i),ball(.009,center=(x+.14,y-.025,1.096),color=(.12,.13,.10)))
for i in range(5):
    jug("left tabletop jug "+str(i),-1.30+random.uniform(-.11,.11),-.43+i*.23,1.015,.075,.18,
        random.choice([(.65,.71,.66),(.53,.60,.55),(.64,.45,.22)]))
for i in range(7):
    vessel("right shelf cup "+str(i),.80,-.56+i*.21,1.51,.055,.105,
           random.choice([(.59,.43,.20),(.65,.69,.59),(.32,.36,.26)]),"cup")
for i in range(4):
    vessel("left shelf dish "+str(i),-.81,-.43+i*.43,1.50,.105,.05,(.61,.68,.62),"plate")
for i in range(3):
    jug("shelf bottle "+str(i),.80,.55+i*.12,1.51,.055,.23,
        random.choice([(.30,.33,.20),(.62,.43,.19)]))
vessel("chimney ledge cup",-.28,-.30,1.20,.055,.08,(.62,.45,.20),"cup")

# Ceramic work counter.
for i in range(12):
    x=-4.28+i*.247
    y=2.54+random.uniform(-.19,.20)
    col=random.choice([(.69,.73,.67),(.58,.57,.46),(.43,.37,.26),(.64,.47,.26)])
    if i%3==0:
        jug("counter pitcher "+str(i),x,y,1.15,.095,.22,col)
    else:
        vessel("counter bowl "+str(i),x,y,1.15,.12,.095,col)
for i in range(3):
    vessel("counter saucer "+str(i),-4.05+i*.54,2.28,1.15,.14,.04,(.64,.68,.61),"plate")
block("counter cutting board",(.54,.35,.05),(-1.85,2.65,1.17),(.32,.25,.15))
for i in range(3):
    ob=ball(.11,center=(-2.02+i*.15,2.64,1.24),color=(.53,.41,.24))
    ob.resize((1,.7,.5))
    put("counter loaf "+str(i),ob)

# Fireplace grate and cooking equipment.
for i in range(8):
    bar("grate upright "+str(i),(-.38+i*.32,3.39,.21),(-.38+i*.32,3.39,1.18),.018,(.095,.105,.08))
for z in [.30,.56,.83,1.10]:
    bar("grate crossbar "+str(z),(-.50,3.37,z),(1.98,3.37,z),.022,(.10,.11,.085))
for x,y in [(-1.03,2.99),(2.85,2.97)]:
    vessel("iron cauldron "+str(x),x,y,.06,.235,.40,(.16,.19,.15),"pot")
    loop("pot lip "+str(x),x,y,.46,.22,.018,(.30,.32,.25))
    vessel("pot lid "+str(x),x-.04,y,.47,.23,.035,(.38,.42,.35),"plate")
for i in range(3):
    vessel("near hearth pan "+str(i),2.59+i*.19,2.86,.30+i*.13,.16,.04,(.50,.56,.49),"plate")
for i in range(4):
    x=3.67+(i%2)*.37
    y=2.45+(i//2)*.40
    vessel("storage pot "+str(i),x,y,.025,.21,.29+i*.035,
           [(.28,.25,.17),(.19,.20,.14),(.35,.29,.20),(.40,.39,.29)][i],"pot")
vessel("wicker basket",3.11,1.99,.03,.31,.24,(.40,.27,.14),"basket")
for k in range(6):
    loop("basket weave "+str(k),3.11,1.99,.06+k*.035,.235+k*.010,.009,(.50,.35,.20))
vessel("small basket",3.75,1.96,.025,.23,.19,(.35,.25,.15),"basket")

# Hanging utensils.
bar("left utensil rack",(-1.70,3.12,2.65),(-1.00,3.12,2.65),.025,(.26,.25,.18))
for i in range(5):
    x=-1.66+i*.15
    bar("ladle shaft "+str(i),(x,3.10,2.75),(x,3.10,2.30),.012,(.28,.29,.23))
    ob=ball(.056,center=(x,3.10,2.27),color=(.35,.38,.30))
    ob.resize((.75,.25,1.1))
    put("ladle head "+str(i),ob)
bar("cloth support",(2.96,3.01,.40),(2.96,3.01,1.86),.020,(.43,.40,.29))
block("hanging linen",(.18,.05,.42),(2.96,2.98,1.52),(.72,.73,.65))

realize(scene)

def mat(name,col,rough=.85):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*col,1)
    b.inputs["Roughness"].default_value=rough
    return m

def mesh_obj(name,verts,faces,materials,indices=None):
    m=bpy.data.meshes.new(name)
    m.from_pydata(verts,[],faces)
    m.update()
    o=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(o)
    for a in materials:m.materials.append(a)
    if indices:
        for p,j in zip(m.polygons,indices):p.material_index=j
    return o

# Efficient combined paving mesh: larger flags around the table, small bricks outside.
floor_mats=[mat("paving "+str(i),c) for i,c in enumerate([
    (.43,.43,.35),(.49,.48,.39),(.54,.52,.42),(.58,.55,.44),
    (.36,.37,.29),(.39,.39,.31),(.32,.34,.27),(.45,.44,.34)])]
verts=[];faces=[];ids=[]
def tile(x,y,sx,sy,z,mi):
    n=len(verts)
    verts.extend([(x-sx/2,y-sy/2,z),(x+sx/2,y-sy/2,z),
                  (x+sx/2,y+sy/2,z),(x-sx/2,y+sy/2,z)])
    faces.append((n,n+1,n+2,n+3));ids.append(mi)
for j in range(29):
    for i in range(29):
        x=(i-14)*.32
        y=(j-14)*.32
        if -2.47<x<2.47 and -2.91<y<2.25:continue
        tile(x+(j%2)*.14,y,.308,.304,random.uniform(-.005,.004),random.randrange(4,8))
for j in range(11):
    for i in range(11):
        tile((i-5)*.46,(j-5)*.46-.35,.448,.448,random.uniform(.002,.014),random.randrange(4))
mesh_obj("individual worn floor stones",verts,faces,floor_mats,ids)

# Plaster regions between each arch and the upper wall.
pm=mat("old plaster",PLASTER)
for ai,(cx,r,spring,n) in enumerate(arch_specs):
    vs=[];fs=[]
    for k in range(n+1):
        a=math.pi*k/n
        x=cx+r*math.cos(a)
        z=spring+r*math.sin(a)+.14
        vs.extend([(x,3.53,z),(x,3.53,3.23)])
    for k in range(n):
        fs.append((2*k,2*k+1,2*k+3,2*k+2))
    mesh_obj("plaster over arch "+str(ai),vs,fs,[pm])

# Octagonal tapered chimney hood.
stone_mat=mat("hood limestone",(.70,.66,.55))
seam_mat=mat("hood joints",(.55,.51,.42))
def taper(name,z0,z1,r0,r1,material):
    vs=[]
    for z,r in [(z0,r0),(z1,r1)]:
        for i in range(8):
            a=(i+.5)*math.tau/8
            vs.append((r*math.cos(a),.18+r*math.sin(a),z))
    fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]
    for i in range(8):fs.append((i,(i+1)%8,(i+1)%8+8,i+8))
    return mesh_obj(name,vs,fs,[material])
taper("hood lower rim",2.79,2.89,.64,.67,stone_mat)
taper("hood lower slope",2.89,3.19,.67,.52,stone_mat)
taper("hood lower joint",3.19,3.21,.53,.53,seam_mat)
taper("hood middle slope",3.21,3.48,.53,.37,stone_mat)
taper("hood upper joint",3.48,3.50,.38,.38,seam_mat)
taper("hood upper slope",3.50,3.78,.38,.13,stone_mat)
taper("hood tip",3.78,3.88,.13,.055,stone_mat)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.095,location=(0,.18,3.96))
bpy.context.object.scale=(.80,.80,1.15)
bpy.context.object.data.materials.append(stone_mat)

# Hollow ceramic meshes, including interiors and thick rims.
cache={}
for name,x,y,z,r,h,col,kind in pots:
    if kind=="plate":
        profile=[(0,.02),(.55,.02),(.82,.25),(1,.75),(1,1),(.90,.95),(.72,.38),(0,.22)]
    elif kind=="jug":
        profile=[(0,0),(.65,0),(.88,.14),(1,.43),(.86,.69),(.46,.83),(.41,1),(.53,1.03),
                 (.53,1.08),(.33,1.08),(.32,.85),(.66,.63),(.75,.27),(0,.13)]
    elif kind=="cup":
        profile=[(0,0),(.70,0),(.84,.10),(1,1),(.83,1),(.70,.17),(0,.14)]
    elif kind in ["pot","basket"]:
        profile=[(0,0),(.70,0),(.96,.24),(1,.70),(.89,1),(.76,1),(.83,.69),(.76,.23),(0,.15)]
    else:
        profile=[(0,0),(.48,0),(.75,.17),(1,.85),(1,1),(.88,1.02),(.80,.72),(.58,.23),(0,.14)]
    vs=[];fs=[];n=24
    for rr,zz in profile:
        for i in range(n):
            a=i*math.tau/n
            vs.append((x+r*rr*math.cos(a),y+r*rr*math.sin(a),z+h*zz))
    for k in range(len(profile)-1):
        for i in range(n):fs.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    key=(col,kind=="basket")
    if key not in cache:cache[key]=mat("pottery "+str(len(cache)),col,.9 if kind=="basket" else .42)
    ob=mesh_obj(name,vs,fs,[cache[key]])
    for p in ob.data.polygons:p.use_smooth=True

# Restrained procedural variation on the room surfaces.
for m in [pm,stone_mat]+floor_mats:
    ns=m.node_tree.nodes
    bs=ns.get("Principled BSDF")
    tex=ns.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=13
    tex.inputs["Detail"].default_value=2
    bump=ns.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.23
    bump.inputs["Distance"].default_value=.025
    m.node_tree.links.new(tex.outputs["Fac"],bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

set_view((6.4,-8.5,9.1),(-.05,.52,1.34),lens=44,sensor=36)
area_emitter((-3.4,-2.0,7.1),power=1250,size=4.7,target=(0,.6,.5),color=(.92,.97,1))
area_emitter((2,-1,5.8),power=270,size=3.5,target=(0,.8,1),color=(1,.90,.75))
bpy.ops.object.light_add(type="POINT",location=(-1.03,3.12,1.65))
bpy.context.object.data.energy=18
bpy.context.object.data.color=(1,.39,.10)
bpy.context.object.data.shadow_soft_size=.12
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.45,.49,.48,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.render.resolution_x=471
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.15
