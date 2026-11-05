import bpy, math, random
from sceneact import *

random.seed(12)
scene = Scene("Historic stone kitchen")
plaster_col = (.73,.76,.71)
wood_col = (.37,.23,.11)
stone_col = (.49,.47,.39)
iron_col = (.075,.08,.065)

def block(name, size, pos, color):
    scene.include(name, box(size, center=pos, color=color))

block("floor foundation", (8.7,8.6,.15), (0,0,-.12), (.35,.34,.28))
block("left plaster wall", (.20,7.7,5.7), (-4.05,0,2.8), plaster_col)
block("right return wall", (.20,2.6,5.7), (4.1,2.65,2.8), plaster_col)
block("dark rear backing", (8.3,.13,3.0), (0,3.84,1.48), (.15,.145,.105))
block("left niche backing", (2.7,.06,1.8), (-2.62,3.74,.89), (.34,.32,.24))
block("hearth floor", (3.8,1.18,.08), (.72,3.18,.02), (.25,.24,.18))

block("worktable top", (3.30,2.66,.14), (0,-.18,.87), (.43,.30,.16))
for x in (-1.38,1.38):
    for y in (-1.28,.91):
        block("table leg "+str((x,y)), (.15,.16,.82), (x,y,.43), wood_col)
    block("table side apron "+str(x), (.09,2.45,.22), (x,-.18,.71), wood_col)
block("table front apron", (2.90,.09,.22), (0,-1.38,.71), wood_col)

block("chimney pedestal", (1.02,1.03,.34), (0,.30,1.10), (.52,.48,.37))
block("pedestal cornice", (1.15,1.16,.10), (0,.30,1.31), (.67,.63,.52))
block("stone chimney shaft", (.80,.84,1.10), (0,.30,1.91), (.66,.62,.51))
for z in (1.40,2.41,2.49):
    block("shaft molding "+str(z), (.96,1.0,.06), (0,.30,z), (.69,.65,.54))
block("front recessed panel", (.58,.012,.76), (0,-.127,1.94), (.60,.565,.46))
for x in (-.32,.32):
    block("panel stile "+str(x), (.025,.027,.82), (x,-.144,1.94), (.69,.65,.54))
block("panel bottom", (.65,.028,.027), (0,-.144,1.53), (.68,.64,.53))

block("back wooden screen", (2.50,.075,.51), (0,.93,1.23), wood_col)
block("front wooden screen", (2.20,.075,.52), (.18,-.66,1.23), (.43,.255,.115))
block("left wooden screen", (.075,1.48,.50), (-1.08,.10,1.23), (.41,.26,.12))
posts=[(-1.08,-.66),(1.28,-.66),(-1.25,.93),(1.25,.93)]
for i,(x,y) in enumerate(posts):
    block("screen post "+str(i), (.095,.095,.66), (x,y,1.27), (.29,.17,.075))

block("dresser slab", (3.08,.94,.11), (-2.50,2.78,1.01), (.40,.40,.33))
for i,x in enumerate((-4.0,-2.75,-1.1)):
    block("dresser pier "+str(i), (.20,.87,.87), (x,2.83,.46), (.63,.66,.58))
block("dresser upper band", (3.05,.87,.21), (-2.52,2.83,.85), (.63,.66,.58))

for i,x in enumerate((-.05,.64,1.35)):
    scene.include("grate upright "+str(i), rod(.023,start=(x,3.45,.12),end=(x,3.45,1.42),color=iron_col))
for i,z in enumerate((.25,.46,.67,.88,1.09)):
    scene.include("grate rail "+str(i), rod(.018,start=(-.13,3.43,z),end=(1.66,3.43,z),color=iron_col))
for i in range(5):
    scene.include("poker "+str(i), rod(.012,start=(2.27+i*.07,2.98,.08),end=(2.17+i*.07,3.06,1.66+i*.05),color=iron_col))
    x=-1.55+i*.13
    scene.include("hanging implement "+str(i), rod(.012,start=(x,3.03,1.25),end=(x,3.03,2.14),color=iron_col))
scene.include("utensil rail",rod(.022,start=(-1.66,3.03,2.10),end=(-.90,3.03,2.10),color=wood_col))

realize(scene)

mats={}
def mat(name,col,rough=.85,noise=False):
    if name in mats:
        return mats[name]
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    nt=m.node_tree
    bs=nt.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*col,1)
    bs.inputs["Roughness"].default_value=rough
    if noise:
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=7
        tex.inputs["Detail"].default_value=3
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(*(v*.70 for v in col),1)
        ramp.color_ramp.elements[1].position=.83
        ramp.color_ramp.elements[1].color=(*(min(1,v*1.12) for v in col),1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.23
        bump.inputs["Distance"].default_value=.035
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    mats[name]=m
    return m

def mesh_obj(name,verts,faces,material):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob

plaster=mat("old plaster",plaster_col,noise=True)
stone=mat("weathered stone",stone_col,noise=True)
oak=mat("aged oak",wood_col,noise=True)
for ob in list(bpy.context.scene.objects):
    if ob.type=="MESH":
        material=None
        if "wall" in ob.name:
            material=plaster
        elif any(s in ob.name for s in ("table","wooden screen","screen post")):
            material=oak
        if material:
            ob.data.materials.clear()
            ob.data.materials.append(material)

def cube(name,size,pos,material):
    sx,sy,sz=[v/2 for v in size]
    vs=[(x,y,z) for z in (-sz,sz) for y in (-sy,sy) for x in (-sx,sx)]
    fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    ob=mesh_obj(name,vs,fs,material)
    ob.location=pos
    return ob

def arch_wall(name,cx,width,spring,rise):
    verts=[]; faces=[]
    for i in range(29):
        x=cx-width/2+width*i/28
        u=(x-cx)/(width/2)
        z=spring+rise*math.sqrt(max(0,1-u*u))
        verts.extend([(x,3.13,z),(x,3.13,5.7),(x,3.53,z),(x,3.53,5.7)])
    for i in range(28):
        a=i*4;b=(i+1)*4
        faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b)])
    mesh_obj(name,verts,faces,plaster)

arch_wall("left plaster arch",-2.62,2.78,1.22,.94)
arch_wall("main plaster arch",.70,3.82,1.30,1.28)
arch_wall("right plaster arch",3.47,1.48,.91,.71)
cube("left hearth jamb",(.26,.49,1.35),(-1.20,3.12,.675),stone)
cube("right hearth jamb",(.25,.49,1.32),(2.63,3.12,.66),stone)
cube("right wall separation",(.15,.40,5.7),(2.70,3.32,2.85),plaster)

def arch_band(name,cx,width,spring,rise,count):
    for i in range(count):
        t0=i*math.pi/count+.007
        t1=(i+1)*math.pi/count-.007
        vs=[]
        for y in (2.97,3.17):
            for t,r in ((t0,0),(t1,0),(t1,.22),(t0,.22)):
                vs.append((cx+(width/2+r)*math.cos(t),y,spring+(rise+r)*math.sin(t)))
        fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]
        factor=random.uniform(.90,1.10)
        m=mat(name+" stone "+str(i),tuple(v*factor for v in stone_col),noise=True)
        mesh_obj(name+str(i),vs,fs,m)

arch_band("great arch",.70,3.82,1.30,1.28,19)
arch_band("left arch",-2.62,2.78,1.22,.94,14)
arch_band("right arch",3.47,1.48,.91,.71,9)

dressermat=mat("dresser masonry",(.62,.65,.58),noise=True)
for cx in (-3.38,-1.95):
    vs=[];fs=[]
    for i in range(17):
        t=math.pi*i/16
        x=cx+.49*math.cos(t)
        z=.29+.42*math.sin(t)
        vs.extend([(x,2.365,z),(x,2.365,.85)])
    for i in range(16):
        a=2*i
        fs.append((a,a+2,a+3,a+1))
    mesh_obj("arched dresser opening "+str(cx),vs,fs,dressermat)

floor_mats=[mat("paver "+str(i),(.37+i*.014,.37+i*.013,.31+i*.011),noise=True) for i in range(13)]
vs=[];fs=[];indices=[]
for j in range(23):
    for i in range(23):
        x=-4.6+i*.405+(j%2)*.20
        y=-4.5+j*.405
        z=random.uniform(-.017,-.006)
        a=len(vs)
        vs.extend([(x,y,z),(x+.392,y,z),(x+.392,y+.392,z),(x,y+.392,z)])
        fs.append((a,a+1,a+2,a+3))
        indices.append(random.randrange(13))
ob=mesh_obj("uneven stone paving",vs,fs,floor_mats[0])
for m in floor_mats[1:]:
    ob.data.materials.append(m)
for p,i in zip(ob.data.polygons,indices):
    p.material_index=i

def lathe(name,x,y,z,profile,material,n=24):
    vs=[];fs=[]
    for r,h in profile:
        for i in range(n):
            t=math.tau*i/n
            vs.append((x+r*math.cos(t),y+r*math.sin(t),z+h))
    for j in range(len(profile)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            fs.append((a,b,b+n,a+n))
    ob=mesh_obj(name,vs,fs,material)
    for p in ob.data.polygons:
        p.use_smooth=True
    return ob

cream=mat("cream glaze",(.73,.76,.69),.29)
gold=mat("honey glaze",(.61,.39,.15),.34)
iron=mat("blackened iron",iron_col,.70)
pewter=mat("pewter",(.44,.49,.46),.33)
brown=mat("brown earthenware",(.25,.18,.105),.65)
green=mat("olive bottle",(.20,.245,.12),.30)

def tube(name,pts,r,material):
    vs=[];fs=[];n=8
    for j,p in enumerate(pts):
        if j==0:
            d=tuple(pts[1][k]-p[k] for k in range(3))
        else:
            d=tuple(p[k]-pts[j-1][k] for k in range(3))
        length=math.sqrt(sum(v*v for v in d)) or 1
        d=tuple(v/length for v in d)
        ref=(0,0,1) if abs(d[2])<.9 else (0,1,0)
        u=(d[1]*ref[2]-d[2]*ref[1],d[2]*ref[0]-d[0]*ref[2],d[0]*ref[1]-d[1]*ref[0])
        ul=math.sqrt(sum(v*v for v in u)) or 1
        u=tuple(v/ul for v in u)
        v=(d[1]*u[2]-d[2]*u[1],d[2]*u[0]-d[0]*u[2],d[0]*u[1]-d[1]*u[0])
        for i in range(n):
            t=i*math.tau/n
            vs.append(tuple(p[k]+r*(u[k]*math.cos(t)+v[k]*math.sin(t)) for k in range(3)))
    for j in range(len(pts)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            fs.append((a,b,b+n,a+n))
    return mesh_obj(name,vs,fs,material)

def bowl(name,x,y,z,r=.16,m=gold):
    return lathe(name,x,y,z,[(0,0),(.55*r,0),(.84*r,.12*r),(r,.48*r),(r,.58*r),(.90*r,.58*r),(.80*r,.22*r),(.44*r,.12*r),(0,.12*r)],m)

def plate(name,x,y,z,r=.17,m=cream):
    return lathe(name,x,y,z,[(0,0),(.70*r,0),(r,.035),(r,.047),(.90*r,.050),(.65*r,.019),(0,.019)],m)

def cup(name,x,y,z,r=.06,h=.13,m=gold,handle=True):
    lathe(name,x,y,z,[(0,0),(.74*r,0),(r,h*.9),(r,h),(.80*r,h),(.76*r,.025),(0,.025)],m,20)
    if handle:
        tube(name+" handle",[(x+r,y,z+h*.81),(x+r*1.7,y,z+h*.8),(x+r*1.8,y,z+h*.35),(x+r*.85,y,z+h*.30)],.011,m)

def pot(name,x,y,z,r=.2,h=.3,m=iron):
    lathe(name,x,y,z,[(0,0),(.66*r,0),(r,h*.23),(1.04*r,h*.68),(.88*r,h),(.77*r,h),(.85*r,h*.65),(.70*r,.04),(0,.04)],m)
    for s in (-1,1):
        tube(name+" handle "+str(s),[(x+s*r*.86,y,z+h*.84),(x+s*r*1.35,y,z+h*.85),(x+s*r*1.40,y,z+h*.48),(x+s*r*.94,y,z+h*.41)],.019,m)

def bottle(name,x,y,z,m=green):
    lathe(name,x,y,z,[(0,0),(.065,0),(.065,.19),(.045,.24),(.025,.26),(.025,.35),(.032,.35),(.032,.37),(.018,.37),(.018,.27)],m,16)

hoodmat=mat("pale limestone hood",(.70,.66,.55),noise=True)
jointmat=mat("hood joints",(.54,.51,.42))
def hood(name,z0,z1,r0,r1,m):
    vs=[]
    for z,r in ((z0,r0),(z1,r1)):
        for i in range(8):
            t=math.tau*i/8+math.pi/8
            vs.append((r*math.cos(t),.30+r*math.sin(t),z))
    fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]
    fs.extend((i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8))
    mesh_obj(name,vs,fs,m)

hood("hood projecting lip",2.49,2.59,.64,.64,hoodmat)
for i,(z0,z1,r0,r1) in enumerate([(2.59,2.83,.64,.52),(2.84,3.12,.52,.39),(3.13,3.39,.39,.245),(3.40,3.61,.245,.09)]):
    hood("hood course "+str(i),z0,z1,r0,r1,hoodmat)
    if i<3:
        hood("hood mortar "+str(i),z1,z1+.01,r1*1.025,r1*1.025,jointmat)
lathe("rounded chimney finial",0,.30,3.60,[(0,0),(.06,.02),(.095,.07),(.092,.16),(.055,.21),(0,.22)],hoodmat,16)

bowl("foreground amber bowl",.94,-1.24,.95,.205,gold)
bowl("foreground stone bowl",.49,-1.31,.95,.155,brown)
bowl("left amber bowl",-1.39,-.66,.95,.195,gold)
plate("small white saucer",-1.48,-.25,.95,.125)
for i in range(5):
    plate("stacked plate "+str(i),-.84,-.71,.95+i*.023,.19-i*.004)
plate("back saucer",-1.20,.90,.96,.16)
plate("right pewter platter",1.43,.48,.95,.215,pewter)
for i,(x,y) in enumerate([(-1.44,.14),(-1.42,.49),(-1.30,.75),(-.71,-.99),(-1.22,-.39)]):
    cup("table mug "+str(i),x,y,.95,.065,.13,cream if i%2 else gold)
pot("pewter pitcher",-1.24,.38,.95,.10,.23,pewter)
pot("small tin vessel",-1.44,.71,.95,.115,.19,pewter)
for i in range(8):
    cup("front rail cup "+str(i),-.84+i*.27,-.66,1.51,.046,.12,cream if i%3==0 else gold)
for i in range(6):
    cup("back rail cup "+str(i),-1.08+i*.43,.93,1.51,.05,.12,cream if i%2 else gold)
bottle("olive bottle",1.03,-.38,.95)
bottle("brown bottle",1.16,-.20,.95,brown)
for i,(x,y) in enumerate(posts):
    cup("post cap "+str(i),x,y,1.60,.055,.06,gold,False)

bread=mat("baked bread",(.52,.35,.17),noise=True)
fishmat=mat("silver gray fish",(.49,.51,.44),.51)
def ellipsoid(name,pos,scale,m,rotation=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=pos)
    ob=bpy.context.object
    ob.name=name
    ob.scale=scale
    ob.rotation_euler[2]=rotation
    ob.data.materials.append(m)
    return ob

boardmat=mat("cutting board oak",(.47,.34,.18),noise=True)
cube("cutting board",(1.10,.42,.025),(.48,-1.02,.966),boardmat)
for i in range(7):
    ellipsoid("bread roll "+str(i),(-1.39+random.random()*.44,-1.15+random.random()*.66,1.00),(.115,.067,.035),bread,random.random()*3)
for i in range(6):
    x=.03+i*.16
    y=-1.04+random.uniform(-.10,.10)
    ellipsoid("fish "+str(i),(x,y,1.00),(.145,.041,.025),fishmat,.20)
    mesh_obj("fish tail "+str(i),[(x-.12,y,1.0),(x-.21,y-.065,1.0),(x-.21,y+.065,1.0)],[(0,1,2)],fishmat)
linen=mat("unbleached linen",(.65,.66,.58),noise=True)
for i in range(3):
    ob=cube("folded linen "+str(i),(.44,.22,.016),(.61+i*.06,-1.20+i*.045,1.025+i*.016),linen)
    ob.rotation_euler[2]=.35+i*.13
for i in range(4):
    x=-1.52+i*.10
    tube("wooden spoon stem "+str(i),[(x,.02,.972),(x+.16,.36,.972)],.009,oak)
    ellipsoid("wooden spoon bowl "+str(i),(x+.18,.39,.98),(.025,.049,.009),oak,-.4)

for i in range(12):
    x=-3.88+i*.242
    y=2.63+random.uniform(-.10,.12)
    if i%3==0:
        pot("dresser saucepan "+str(i),x,y,1.075,.125,.17,iron)
    elif i%3==1:
        bowl("dresser bowl "+str(i),x,y,1.075,.132,cream if i%2 else gold)
    else:
        cup("dresser jug "+str(i),x,y,1.075,.075,.17,cream)
plate("dresser platter",-3.08,2.45,1.08,.18,pewter)
for i in range(3):
    ellipsoid("dresser loaf "+str(i),(-1.64+i*.15,2.66,1.13),(.12,.08,.05),bread)

pot("large hearth cauldron",2.05,2.92,.04,.30,.43,iron)
pot("back cooking pot",1.86,3.39,.09,.235,.29,iron)
plate("cauldron lid",1.83,2.70,.48,.22,pewter)
pot("left green vessel",-1.20,2.73,.025,.22,.34,green)
pot("left pale crock",-1.22,2.84,.40,.145,.20,cream)
for i in range(5):
    ellipsoid("hanging spoon head "+str(i),(-1.55+i*.13,3.03,1.25),(.048,.016,.083),pewter)
for i,(x,y,r,h) in enumerate([(3.12,2.83,.22,.31),(3.66,2.73,.25,.37),(3.62,2.19,.23,.31)]):
    pot("storage jar "+str(i),x,y,.025,r,h,brown)
basketmat=mat("wicker",(.40,.27,.14),noise=True)
for k,(x,y,r) in enumerate([(2.76,2.26,.30),(3.29,2.46,.24)]):
    bowl("wicker basket "+str(k),x,y,.025,r,basketmat)
    for j in range(5):
        rr=r*(.80+.04*j)
        lathe("basket weave "+str((k,j)),x,y,.06+j*.026,[(rr,0),(rr+.010,.008),(rr,.016)],basketmat,32)
cube("hanging towel",(.24,.035,.52),(2.48,3.00,1.42),linen)
tube("towel loop",[(2.38,3.0,1.66),(2.48,3.0,1.88),(2.59,3.0,1.66)],.012,cream)

firemat=mat("glowing embers",(.65,.16,.025))
bs=firemat.node_tree.nodes.get("Principled BSDF")
bs.inputs["Emission Color"].default_value=(1,.17,.015,1)
bs.inputs["Emission Strength"].default_value=2
for i in range(3):
    ellipsoid("ember "+str(i),(-.87+i*.12,3.43,.88),(.045,.04,.07),firemat)

set_view((6.25,-8.50,8.85),target=(0,.62,1.38),lens=51,sensor=36)
area_emitter((-3,-1,7.4),power=1150,size=5,target=(0,1,0),color=(.88,.94,1.0))
area_emitter((1,-3,5.2),power=260,size=4,target=(0,.7,1),color=(1,.90,.76))
area_emitter((-.85,3.24,1.07),power=20,size=.3,target=(-.5,2.7,.8),color=(1,.35,.08))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Kitchen ambient world")
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.54,.58,.58,1)
bg.inputs["Strength"].default_value=.32
sc.render.engine="CYCLES"
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.cycles.max_bounces=5
sc.render.resolution_x=471
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=0
