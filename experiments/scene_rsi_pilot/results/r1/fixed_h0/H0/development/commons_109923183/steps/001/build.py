import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(18)
scene = Scene("French chaise longue")
ivory=(.72,.69,.59)
paint=(.40,.47,.41)
gilt=(.66,.59,.43)
cloth=(.85,.80,.69)

scene.include("floor",box((12,12,.12),center=(0,0,-.07),color=(.22,.12,.075)))

# Individual polished parquet strips.
floor=Asset("parquet")
for i in range(-7,8):
    for j in range(-7,8):
        for k in range(5):
            u=i*.68
            v=j*.68
            if (i+j)%2:
                px,py=u+(k+.5)*.136,v+.34
                sx,sy=.132,.674
            else:
                px,py=u+.34,v+(k+.5)*.136
                sx,sy=.674,.132
            x=(px-py)*.7071
            y=(px+py)*.7071
            c=random.uniform(.78,1.15)
            p=box((sx,sy,.018),center=(x,y,.004),color=(.255*c,.135*c,.078*c))
            p.turn("z",45)
            floor.include(f"strip_{i}_{j}_{k}",p)
scene.include("wood flooring",floor)

wall_y=1.04
scene.include("paneled back wall",box((7,.16,3.5),center=(0,wall_y+.08,1.72),color=(.73,.71,.64)))
for z,h,d in [(.10,.16,.055),(.24,.035,.075),(.32,.026,.045),(1.93,.045,.055),(2.04,.032,.07),(2.27,.075,.07)]:
    scene.include("horizontal molding "+str(z),box((6.5,d,h),center=(0,wall_y-d/2,z),color=(.79,.77,.69)))
for x in [-1.65,-.70,.98,1.98]:
    scene.include("door join "+str(x),box((.012,.008,3),center=(x,wall_y-.007,1.5),color=(.38,.37,.31)))
def panel(name,x1,x2,z1,z2):
    for inset,r in [(0,.014),(.035,.009),(.053,.006)]:
        yy=wall_y-.028-inset*.12
        pts=[(x1+inset,yy,z1+inset),(x2-inset,yy,z1+inset),
             (x2-inset,yy,z2-inset),(x1+inset,yy,z2-inset),(x1+inset,yy,z1+inset)]
        scene.include(name+str(inset),sweep_tube(points=pts,radius=r,color=(.82,.80,.72)))
panel("large recessed wall panel",-1.54,1.78,.43,1.82)
for x in [-.93,-.81]:
    scene.include("dark door pull"+str(x),rod(.018,start=(x,wall_y-.04,1.94),end=(x,wall_y-.065,2.015),color=(.12,.115,.085)))

# Window opening and soft hanging drapery on the left.
scene.include("left wall",box((.16,3.5,3.5),center=(-2.10,-.65,1.72),color=(.76,.73,.65)))
scene.include("luminous window",box((.025,1.5,2.8),center=(-1.998,-.85,1.65),color=(.96,.97,.92)))
for j in range(12):
    y=-1.5+j*.10
    scene.include("curtain fold"+str(j),rod(.065,start=(-1.94+.022*math.sin(j),y,.13),end=(-1.94+.022*math.sin(j),y,3.1),color=(.79+.04*(j%2),.75+.04*(j%2),.65+.05*(j%2))))
scene.include("right projecting pier",box((.28,.53,3.0),center=(2.10,.80,1.5),color=(.81,.80,.73)))
panel("right panel",2.02,2.48,.39,2.05)

chaise=Asset("antique painted chaise")
# Deep upholstered seat and shaped wooden seat rail.
chaise.include("seat support",fillet_box((2.54,1.02,.13),radius=.13,center=(0,0,.59),color=paint))
# The front apron has a gently falling center.
front=[(-1.22,-.51,.61),(-.95,-.53,.57),(-.63,-.53,.55),(-.30,-.53,.51),
       (0,-.53,.49),(.30,-.53,.51),(.67,-.53,.54),(1.05,-.49,.56),(1.23,-.40,.60)]
for zoff,r,c in [(0,.037,paint),(.036,.012,gilt),(-.031,.012,gilt)]:
    chaise.include("carved apron"+str(zoff),sweep_tube(points=[(x,y,z+zoff) for x,y,z in front],radius=r,color=c))
chaise.include("far side rail",sweep_tube(points=[(-1.2,.48,.59),(-.6,.51,.56),(.4,.51,.56),(1.17,.43,.59)],radius=.035,color=paint))

# Cabriole legs, each with a small out-turned foot.
for x in [-1.04,1.03]:
    for y in [-.43,.40]:
        s=1 if x>0 else -1
        pts=[(x,y,.59),(x+s*.045,y,.47),(x+s*.015,y,.33),(x-s*.035,y,.17),(x+s*.015,y-.02,.055),(x+s*.08,y-.025,.045)]
        chaise.include(f"leg{x}{y}",sweep_tube(points=pts,radius=.037,color=paint))
        chaise.include(f"leg edge{x}{y}",sweep_tube(points=[(a,b-.026,c) for a,b,c in pts],radius=.009,color=gilt))

# High curved head with low flowing arms.
head_top=[(-1.23,-.47,1.40),(-1.36,-.41,1.61),(-1.40,-.20,1.69),
          (-1.40,.12,1.68),(-1.36,.39,1.56),(-1.25,.49,1.41)]
chaise.include("head crest",sweep_tube(points=head_top,radius=.033,color=paint))
chaise.include("head gilt crest",sweep_tube(points=[(x-.006,y-.014,z+.018) for x,y,z in head_top],radius=.010,color=gilt))
for side in [-1,1]:
    yy=side*.49
    top=[(-1.29,yy,1.49),(-1.12,yy*1.025,1.35),(-.94,yy*1.04,1.23),(-.72,yy*1.03,1.16),(-.56,yy,1.17)]
    chaise.include("swept arm"+str(side),sweep_tube(points=top,radius=.032,color=paint))
    chaise.include("arm gold"+str(side),sweep_tube(points=[(x,y-side*.019,z+.014) for x,y,z in top],radius=.009,color=gilt))
    upright=[(-.56,yy,1.17),(-.60,yy,1.06),(-.58,yy,.87),(-.49,yy,.68),(-.34,yy,.61)]
    chaise.include("arm upright"+str(side),sweep_tube(points=upright,radius=.030,color=paint))
    chaise.include("arm upright trim"+str(side),sweep_tube(points=[(x,y-side*.021,z) for x,y,z in upright],radius=.009,color=gilt))
    bottom=[(-1.27,yy,.72),(-1.10,yy,.66),(-.85,yy,.63),(-.61,yy,.63),(-.39,yy,.63)]
    chaise.include("side lower piping"+str(side),sweep_tube(points=bottom,radius=.025,color=paint))

# Floral reliefs at the middle of the front apron and crest.
for cx,cy,cz,scale in [(0,-.57,.51,.060),(-1.40,-.12,1.70,.037)]:
    for j in range(9):
        a=j*math.tau/9
        petal=ball(scale*.42,center=(cx+scale*math.cos(a),cy,cz+scale*.63*math.sin(a)),color=gilt)
        petal.resize((1,.36,.7))
        chaise.include("carved flower"+str(cx)+str(j),petal)
    chaise.include("flower center"+str(cx),ball(scale*.35,center=(cx,cy-.008,cz),color=(.75,.69,.53)))
scene.include("chaise",chaise)

# A cropped cane chair in the near-left corner.
chair=Asset("foreground cane chair")
chair.include("seat",fillet_box((.64,.64,.075),radius=.06,center=(-1.73,-1.40,.40),color=paint))
for x in [-2.02,-1.44]:
    chair.include("chair border"+str(x),rod(.025,start=(x,-1.71,.45),end=(x,-1.09,.45),color=gilt))
for y in [-1.70,-1.10]:
    chair.include("chair border"+str(y),rod(.025,start=(-2.02,y,.45),end=(-1.44,y,.45),color=gilt))
for i in range(22):
    a=-2.0+i*.026
    chair.include("cane a"+str(i),rod(.0035,start=(a,-1.68,.451),end=(a,-1.12,.451),color=(.48,.36,.22)))
    b=-1.68+i*.026
    chair.include("cane b"+str(i),rod(.0035,start=(-2.0,b,.455),end=(-1.46,b,.455),color=(.52,.40,.26)))
scene.include("partial cane chair",chair)

realize(scene)

def material(name,color,roughness=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=roughness
    return m

fabric=material("ivory woven damask",cloth,.86)
pink=material("faded rose woven motifs",(.56,.34,.32),.9)
thread=material("muted flax fine stripes",(.64,.59,.49),.9)

# Fine weave catches the light without using image textures.
nt=fabric.node_tree
bs=nt.nodes.get("Principled BSDF")
noise=nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=180
noise.inputs["Detail"].default_value=2
bump=nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.17
bump.inputs["Distance"].default_value=.008
nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

def mesh_obj(name,verts,faces,mat):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    return ob

def tube(name,points,radius,mat):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.resolution_u=2
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    sp=cu.splines.new("POLY")
    sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def signedpow(v,p):
    return math.copysign(abs(v)**p,v)

# Rounded, generously padded long cushion.
verts=[];faces=[]
N=112;R=36
for j in range(R+1):
    lat=-math.pi/2+math.pi*j/R
    radial=abs(math.cos(lat))**.43
    for i in range(N):
        t=math.tau*i/N
        x=1.26*radial*signedpow(math.cos(t),.52)
        y=.505*radial*signedpow(math.sin(t),.52)
        z=.729+.125*signedpow(math.sin(lat),.65)
        verts.append((x,y,z))
for j in range(R):
    for i in range(N):
        ni=(i+1)%N
        faces.append((j*N+i,j*N+ni,(j+1)*N+ni,(j+1)*N+i))
mesh_obj("plump rounded chaise mattress",verts,faces,fabric)
pipe=[]
for i in range(N+1):
    t=math.tau*i/N
    pipe.append((1.258*signedpow(math.cos(t),.52),.505*signedpow(math.sin(t),.52),.715))
tube("mattress stitched welt",pipe,.006,thread)

def top_z(x,y):
    q=(abs(x)/1.26)**(2/.52)+(abs(y)/.505)**(2/.52)
    if q>=.97:return None
    radial=q**.5
    co=radial**(1/.43)
    return .729+.125*(max(0,1-co*co)**.5)**.65+.002

for row in range(27):
    y=-.46+row*.035
    pts=[]
    for k in range(101):
        x=-1.21+k*2.42/100
        z=top_z(x,y)
        if z is not None:pts.append((x,y,z))
    if len(pts)>1:
        tube("fine longitudinal stripe",pts,.0011,thread)
    for k in range(23):
        x=-1.17+k*.105+(row%2)*.048
        z=top_z(x,y+.007)
        if z is None:continue
        tube("tiny rose dash",[(x-.012,y+.007,z+.001),(x+.012,y+.007,z+.001)],.0021,pink)
        if row%3==0:
            tube("woven sprig",[(x,y-.001,z+.002),(x+.007,y+.014,z+.002)],.0016,pink)

# Upholstered back surface, bowed gently across the head.
vs=[];fs=[]
for j in range(25):
    u=j/24
    y=-.46+.92*u
    crest=1.48+.185*math.sin(math.pi*u)**.7
    for k in range(13):
        v=k/12
        z=.72+(crest-.72)*v
        x=-1.25-.12*v-.035*math.sin(math.pi*v)
        vs.append((x,y,z))
for j in range(24):
    for k in range(12):
        a=j*13+k
        fs.append((a,a+1,a+14,a+13))
back=mesh_obj("padded curved headboard",vs,fs,fabric)
sol=back.modifiers.new("upholstery thickness","SOLIDIFY");sol.thickness=.065

# Fabric panels below the flowing arms.
for side in [-1,1]:
    vs=[];fs=[]
    for j in range(25):
        u=j/24
        x=-1.27+.85*u
        top=1.49-.44*(math.sin(u*math.pi/2))**.65
        low=.72-.08*math.sin(u*math.pi/2)
        for k in range(10):
            v=k/9
            vs.append((x,side*(.485+.016*math.sin(v*math.pi)),low+(top-low)*v))
    for j in range(24):
        for k in range(9):
            a=j*10+k
            fs.append((a,a+1,a+11,a+10))
    ob=mesh_obj("upholstered side wing",vs,fs,fabric)
    so=ob.modifiers.new("soft panel thickness","SOLIDIFY");so.thickness=.035
    for j in range(19):
        u=(j+.4)/20
        x=-1.27+.85*u
        top=1.49-.44*(math.sin(u*math.pi/2))**.65
        low=.72-.08*math.sin(u*math.pi/2)
        tube("side fabric pinstripe",[(x,side*.506,low+.025),(x,side*.506,top-.025)],.0014,thread)
        for k in range(5):
            z=low+.07+k*.095
            if z<top-.04:
                tube("side pink stitch",[(x-.004,side*.508,z),(x+.004,side*.508,z+.012)],.0018,pink)

# Loose ivory pillow resting against the high end.
pillowmat=material("warm ivory pillow",(.89,.84,.73),.9)
pillowmat.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value=.95
vs=[];fs=[]
n=32
for side in [-1,1]:
    for j in range(n+1):
        v=-1+2*j/n
        for i in range(n+1):
            u=-1+2*i/n
            bulge=(max(0,1-u*u)*max(0,1-v*v))**.48
            # Pillow lies in the YZ plane and leans back at the top.
            z=1.185+v*.315
            y=-.055+u*.345
            x=-1.06-.19*v+side*(.027+.105*bulge)
            x+=.008*math.sin(u*36+v*12)*(abs(u)**7+abs(v)**7)
            vs.append((x,y,z))
stride=(n+1)**2
for s in range(2):
    for j in range(n):
        for i in range(n):
            a=s*stride+j*(n+1)+i
            fs.append((a,a+1,a+n+2,a+n+1))
for j in range(n):
    for a,b in [(j,j+1),(n*(n+1)+j,n*(n+1)+j+1),
                (j*(n+1),(j+1)*(n+1)),(j*(n+1)+n,(j+1)*(n+1)+n)]:
        fs.append((a,b,b+stride,a+stride))
p=mesh_obj("soft square loose pillow",vs,fs,pillowmat)
sub=p.modifiers.new("soft pillow seams","SUBSURF");sub.levels=1
# Small dark green museum label lying on the cushion.
tagmat=material("green museum card",(.055,.24,.19),.72)
tag=bpy.data.meshes.new("card")
tag.from_pydata([(.64,.10,.864),(.82,.10,.864),(.82,.19,.864),(.64,.19,.864)],[],[(0,1,2,3)])
obj=bpy.data.objects.new("small green exhibit label",tag)
bpy.context.collection.objects.link(obj);obj.data.materials.append(tagmat)
letter=material("label lettering",(.76,.82,.70),.9)
for i in range(4):
    tube("label pale marks",[(.685+i*.022,.132,.866),(.685+i*.022,.161,.866)],.0016,letter)

# Warm daylight and contact shadows.
for ob in bpy.data.objects:
    if ob.type=="MESH" and ("strip_" in ob.name):
        for m in ob.data.materials:
            if m and m.use_nodes:
                bs=m.node_tree.nodes.get("Principled BSDF")
                if bs:bs.inputs["Roughness"].default_value=.32
set_view((2.65,-4.65,3.30),(-.05,.02,1.00),lens=51)
area_emitter((-3,-1.6,3.2),power=480,size=2.8,target=(0,0,.7),color=(1,.94,.83))
area_emitter((1,-3,3.8),power=110,size=4,target=(0,0,.8),color=(1,.96,.87))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.69,.72,.76,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.24
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.15
