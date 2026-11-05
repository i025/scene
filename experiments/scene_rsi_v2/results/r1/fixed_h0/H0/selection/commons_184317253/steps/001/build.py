import bpy, math, random
from mathutils import Vector
from sceneact import *

random.seed(21)
scene = Scene("Historic tiled interior")

ivory=(.76,.76,.68)
stone=(.48,.48,.40)
wood=(.105,.078,.053)
iron=(.055,.061,.055)

def block(name,size,center,color):
    scene.include(name,box(size=size,center=center,color=color))

block("stone floor",(11,13,.16),(0,0,-.11),(.43,.43,.36))
block("rear plaster wall",(8,.30,6.6),(0,3.47,3.25),ivory)
block("left masonry pier",(.48,9,7.4),(-3.8,1,3.65),(.70,.70,.62))
block("right wall",(.35,8,6.3),(4,2,3.1),(.72,.73,.65))
block("ceramic wall backing",(4.65,.045,3.75),(-1.37,3.285,2.15),(.66,.69,.57))
block("low stone skirting",(7.7,.16,.27),(0,3.18,.16),(.58,.59,.51))

# Fireplace, with a deep shadowed opening beneath the hood.
block("fireplace soot",(1.27,.04,2.38),(-.05,3.20,1.23),(.16,.16,.12))
block("left fireplace jamb",(.14,.60,2.1),(-.72,2.96,1.07),(.55,.55,.46))
block("right fireplace jamb",(.14,.60,2.1),(.62,2.96,1.07),(.57,.57,.49))
block("hearth",(1.55,.92,.13),(-.05,2.78,.08),(.35,.35,.29))
block("hood lower white apron",(1.55,.94,.61),(-.05,2.84,2.57),(.81,.82,.75))
block("black fireback",(.90,.08,.70),(-.05,3.12,.60),(.065,.070,.059))
for x in (-.47,.37):
    scene.include("fire iron"+str(x),rod(.026,start=(x,2.98,.17),end=(x,2.98,.97),color=iron))
scene.include("fire iron crossbar",rod(.025,start=(-.47,2.98,.93),end=(.37,2.98,.93),color=iron))

# Tall, very dark timber storage cabinets.
for i,(x,w) in enumerate(((1.19,.76),(2.04,.90),(3.04,.98),(3.78,.40))):
    block("cabinet carcass "+str(i),(w,.67,2.28),(x,3.00,1.42),wood)
    block("cabinet cornice "+str(i),(w+.07,.75,.095),(x,2.97,2.59),(.14,.115,.080))
    for s in (-1,1):
        block("cabinet stile %s %s"%(i,s),(.065,.075,2.20),(x+s*(w/2-.05),2.625,1.43),(.075,.056,.039))
    block("cabinet recessed door "+str(i),(w-.17,.035,2.05),(x,2.648,1.42),(.115,.088,.061))
    for dz in (.48,2.30):
        block("cabinet door rail %s %s"%(i,dz),(w-.10,.075,.07),(x,2.61,dz),(.077,.059,.040))
    scene.include("cabinet handle"+str(i),rod(.014,start=(x+w*.25,2.59,1.40),end=(x+w*.25,2.59,1.57),color=(.18,.17,.12)))

# An open shelf among the cupboards.
block("open shelving back",(.32,.08,2.05),(1.66,3.08,1.38),(.035,.035,.026))
for z in (.49,.93,1.36,1.80,2.24):
    block("shelf "+str(z),(.34,.58,.045),(1.66,2.83,z),(.085,.070,.048))

# Raised pale stone platform in front of the cabinetry.
block("raised bench slab",(3.15,1.15,.13),(2.39,2.13,.48),(.59,.59,.51))
for x in (1.03,2.35,3.70):
    block("platform support"+str(x),(.16,.88,.43),(x,2.23,.22),(.47,.47,.39))
block("bench front molding",(3.2,.11,.075),(2.39,1.53,.40),(.42,.42,.35))

# Foreground museum rope barrier.
for i,(x,y) in enumerate(((-3.0,-.67),(.90,-.37),(3.8,.66))):
    scene.include("barrier post "+str(i),rod(.024,start=(x,y,.03),end=(x,y,.86),color=(.39,.40,.36)))
    block("post foot "+str(i),(.29,.22,.045),(x,y,.035),(.31,.32,.29))
scene.include("left burgundy ribbon",rod(.027,start=(-3,-.67,.75),end=(.9,-.37,.75),color=(.20,.035,.045)))
scene.include("right burgundy ribbon",rod(.027,start=(.9,-.37,.75),end=(3.8,.66,.75),color=(.20,.035,.045)))

realize(scene)

def mat(name,color,rough=0.8,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m

plaster=mat("uneven limewashed plaster",(.76,.78,.71))
p=plaster.node_tree.nodes.get("Principled BSDF")
noise=plaster.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=5
noise.inputs["Detail"].default_value=4
ramp=plaster.node_tree.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.20
ramp.color_ramp.elements[0].color=(.51,.54,.46,1)
ramp.color_ramp.elements[1].position=.74
ramp.color_ramp.elements[1].color=(.84,.85,.78,1)
plaster.node_tree.links.new(noise.outputs["Fac"],ramp.inputs[0])
plaster.node_tree.links.new(ramp.outputs[0],p.inputs["Base Color"])
bump=plaster.node_tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.17
bump.inputs["Distance"].default_value=.055
plaster.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
plaster.node_tree.links.new(bump.outputs[0],p.inputs["Normal"])

white=mat("chalk white hood",(.81,.83,.76))
cream=mat("tile warm ivory",(.70,.70,.54),.5)
blue=mat("ceramic cobalt",(.095,.24,.31),.40)
teal=mat("ceramic turquoise",(.24,.40,.39),.45)
pale=mat("ceramic pale blue",(.47,.58,.54),.5)
gold=mat("old gold ochre",(.54,.39,.075),.48,.25)
black=mat("blackened cast iron",(.045,.052,.047),.67,.55)
darkwood=mat("aged brown oak",(.075,.047,.026),.85)

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    if material: ob.data.materials.append(material)
    return ob

def cube(name,loc,scale,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object
    ob.name=name
    ob.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(material)
    return ob

def line(name,pts,radius,material):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.bevel_depth=radius
    cu.bevel_resolution=2
    sp=cu.splines.new("POLY")
    sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):
        p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob

def lathe(name,profile,center,material,n=48):
    verts=[]
    for z,r in profile:
        for j in range(n):
            a=2*math.pi*j/n
            verts.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),center[2]+z))
    faces=[]
    for i in range(len(profile)-1):
        for j in range(n):
            faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    ob=mesh(name,verts,faces,material)
    for poly in ob.data.polygons: poly.use_smooth=True
    return ob

# Four-sided taper of the broad extractor canopy.
verts=[
    (-.825,2.37,2.87),(.725,2.37,2.87),(.725,3.31,2.87),(-.825,3.31,2.87),
    (-.105,2.95,4.30),(.005,2.95,4.30),(.005,3.16,4.30),(-.105,3.16,4.30)]
mesh("tapered plaster smoke hood",verts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],white)

# The vault is an actual curved interior surface.
verts=[]; faces=[]
N=96; M=32
for i in range(M+1):
    phi=(math.pi/2)*i/M
    rr=4.65*math.cos(phi)
    zz=5.05+3.55*math.sin(phi)
    for j in range(N):
        a=2*math.pi*j/N
        verts.append((rr*math.cos(a),2.0+rr*math.sin(a),zz))
for i in range(M):
    for j in range(N):
        faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
ob=mesh("high domed plaster ceiling",verts,faces,plaster)
for f in ob.data.polygons: f.use_smooth=True

# Broad arched plaster ribs, seen against the upper wall.
def ribbon(name,pts,width,material,y=3.08):
    v=[]
    for i,(x,z) in enumerate(pts):
        a=pts[max(0,i-1)]
        b=pts[min(len(pts)-1,i+1)]
        dx=b[0]-a[0]; dz=b[1]-a[1]
        d=math.hypot(dx,dz)
        nx=-dz/d; nz=dx/d
        v += [(x+nx*width/2,y,z+nz*width/2),(x-nx*width/2,y,z-nz*width/2)]
    return mesh(name,v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],material)
pts=[]
for i in range(51):
    a=math.pi*i/100
    pts.append((-2.45+3.65*math.sin(a),3.63+2.26*math.cos(a)))
ribbon("left sweeping vault rib",pts,.16,white)
pts=[]
for i in range(51):
    t=i/50
    pts.append((1.12+3.45*t,3.73+2.38*math.sin(t*math.pi/2)))
ribbon("right sweeping vault rib",pts,.21,white)
line("fine vault seam",[(-3.6,3.10,6.35),(-2.45,3.10,6.42),(-1.15,3.10,6.12),(.15,3.10,5.13),(1.0,3.10,4.05)],.010,mat("vault seam",(.49,.51,.45)))

# Small bright arch-headed clerestory openings.
glow=mat("daylight beyond windows",(1,1,.91))
ps=glow.node_tree.nodes.get("Principled BSDF")
ps.inputs["Emission Color"].default_value=(.95,1,.94,1)
ps.inputs["Emission Strength"].default_value=2.8
def archpoly(cx,y,z,w,h,material,name):
    pts=[(cx-w/2,y,z),(cx+w/2,y,z),(cx+w/2,y,z+h-w/2)]
    for i in range(1,25):
        a=math.pi*i/24
        pts.append((cx+w/2*math.cos(a),y,z+h-w/2+w/2*math.sin(a)))
    return mesh(name,pts,[tuple(range(len(pts)))],material)
for i,(x,z,w,h) in enumerate(((-1.72,6.38,.43,.91),(.42,6.16,.48,.83),(2.58,6.60,.50,.91))):
    archpoly(x,3.13,z,w+.13,h+.08,mat("window reveal"+str(i),(.58,.61,.52)),"window reveal "+str(i))
    archpoly(x+.035,3.105,z+.04,w,h,glow,"bright high window "+str(i))

# Floral tilework, built from colored ceramic polygons.
tv=[]; tf=[]; ti=[]
def tilepoly(coords,idx,y=3.245):
    k=len(tv)
    tv.extend((x,y,z) for x,z in coords)
    tf.append(tuple(range(k,k+len(coords))))
    ti.append(idx)
def disk(x,z,rx,rz,idx,rot=0,n=10):
    co=[]
    for j in range(n):
        a=2*math.pi*j/n
        xx=rx*math.cos(a); zz=rz*math.sin(a)
        co.append((x+xx*math.cos(rot)-zz*math.sin(rot),z+xx*math.sin(rot)+zz*math.cos(rot)))
    tilepoly(co,idx,3.237)

doorx=-2.15
def in_door(x,z):
    dx=abs(x-doorx)
    return dx<.91 and z<2.98

s=.205
for row in range(19):
    z=.35+(row+.5)*s
    for col in range(23):
        x=-3.72+(col+.5)*s
        if x>.98 or z>4.18 or in_door(x,z): continue
        tilepoly([(x-s*.49,z-s*.49),(x+s*.49,z-s*.49),(x+s*.49,z+s*.49),(x-s*.49,z+s*.49)],0)
        for k in range(8):
            a=k*math.pi/4
            cx=x+.055*math.cos(a); cz=z+.055*math.sin(a)
            disk(cx,cz,.031,.014,1 if (row+col+k)%3 else 2,a)
        disk(x,z,.026,.026,2,n=8)
        disk(x,z,.010,.010,0,n=8)
        for ax,az in ((-1,-1),(-1,1),(1,-1),(1,1)):
            disk(x+ax*.088,z+az*.088,.014,.023,3,ax*az*.7,n=6)
ob=mesh("individual floral ceramic ornaments",tv,tf,None)
for ma in (cream,blue,teal,pale): ob.data.materials.append(ma)
for p,i in zip(ob.data.polygons,ti): p.material_index=i

# A narrow patterned top tile border.
for j in range(90):
    x=-3.7+j*.052
    if x>.96: break
    mesh("top border blue diamond",[(x-.022,3.23,4.18),(x,3.23,4.235),(x+.022,3.23,4.18),(x,3.23,4.125)],[(0,1,2,3)],blue)

# Door and its marble pointed arch surround.
archpoly(doorx,3.19,.08,1.78,2.78,white,"outer marble door arch")
archpoly(doorx,3.16,.09,1.39,2.51,darkwood,"arched wooden double door")
for x in (doorx-.40,doorx+.40):
    cube("recessed door panel",(x,3.125,1.13),(.55,.045,1.83),darkwood)
    for xx in (x-.29,x+.29):
        cube("door frame strip",(xx,3.08,1.16),(.045,.055,2.0),gold)
    for z in (.19,1.98):
        cube("horizontal door framing",(x,3.08,z),(.59,.05,.045),gold)
    # Small closely spaced gilded studs and fretwork.
    for row in range(14):
        for col in range(4):
            xx=x-.20+col*.13
            zz=.32+row*.115
            a=.038
            mesh("door fret diamond",[(xx-a,3.069,zz),(xx,3.069,zz+a),(xx+a,3.069,zz),(xx,3.069,zz-a)],[(0,1,2,3)],gold)
            disk_dummy=0
cube("central door stile",(doorx,3.065,1.17),(.055,.06,2.18),darkwood)

# Inscribed ochre plaque above the doorway.
cube("plaque marble border",(doorx,3.15,3.13),(1.85,.075,.49),white)
cube("plaque gold surround",(doorx,3.095,3.13),(1.67,.045,.36),gold)
cube("plaque blue inset",(doorx,3.065,3.13),(1.52,.025,.26),blue)
for i in range(20):
    x=doorx-.69+i*.069
    z=3.11+random.uniform(-.025,.025)
    line("flowing plaque inscription",[(x,3.042,z+.08),(x+.015,3.042,z-.015),(x+.045,3.042,z-.025),(x+.055,3.042,z+.04)],.008,gold)
    if i%3==0:
        line("small inscription dot",[(x+.023,3.041,3.22),(x+.030,3.041,3.22)],.009,gold)

# The prominent old iron cauldron in front of the hearth.
cx=-.34; cy=1.12
lathe("round iron cauldron",[(.13,.31),(.16,.43),(.25,.52),(.57,.55),(.73,.51),(.76,.53),(.79,.53),(.79,.49),(.73,.48),(.24,.40)],(cx,cy,0),black)
for z,r in ((.76,.528),(.22,.445)):
    line("cauldron raised circular rim",[(cx+r*math.cos(2*math.pi*i/80),cy+r*math.sin(2*math.pi*i/80),z) for i in range(81)],.018,black)
for dx in (-.53,.53):
    pts=[]
    for i in range(33):
        a=2*math.pi*i/32
        pts.append((cx+dx+.10*math.cos(a),cy,.63+.11*math.sin(a)))
    line("iron loop handle",pts,.023,black)
for a in (0,2.1,4.2):
    x=cx+.34*math.cos(a); y=cy+.34*math.sin(a)
    cube("short cauldron foot",(x,y,.11),(.12,.13,.22),black)

# Dark ceramic jars sitting on the cabinet tops.
potmat=mat("smoked earthenware",(.085,.093,.078),.76)
for i,(x,r,h) in enumerate(((.97,.13,.34),(1.64,.12,.28),(2.27,.12,.39),(2.90,.13,.37),(3.67,.15,.43))):
    lathe("old storage vessel "+str(i),[(0,.07),(.025,r*.75),(.12,r),(.23*h/.37,r*.91),(h*.76,r*.40),(h*.94,r*.33),(h,r*.44)],(x,2.96,2.64),potmat)
    line("vessel lip "+str(i),[(x+r*.44*math.cos(2*math.pi*j/24),2.96+r*.44*math.sin(2*math.pi*j/24),2.64+h) for j in range(25)],.011,potmat)

# Stone floor joints and subtle irregular plaster damage.
jointmat=mat("stone joint",(.28,.29,.24))
for x in range(-5,6):
    line("floor longitudinal joint",[(x*.72,-5,.001),(x*.72,3.2,.001)],.007,jointmat)
for k in range(13):
    y=-4+k*.61
    line("floor cross joint",[(-4,y,.002),(4,y,.002)],.007,jointmat)

damage=mat("exposed aged plaster",(.52,.54,.46))
for i in range(80):
    x=random.uniform(.9,3.92)
    z=random.uniform(2.78,3.99)
    if random.random()<.45:
        w=random.uniform(.025,.13); h=random.uniform(.035,.17)
        mesh("irregular worn plaster",[(x-w,3.306,z),(x-w*.5,3.305,z+h),(x+w*.4,3.304,z+h*.6),(x+w,3.305,z-h*.3),(x,3.305,z-h)],[(0,1,2,3,4)],damage)

# Give the hood and main wall a softly weathered matte surface.
for ob in bpy.context.scene.objects:
    if ob.type=="MESH":
        if "rear plaster" in ob.name or "masonry pier" in ob.name or "right wall" in ob.name:
            ob.data.materials.clear()
            ob.data.materials.append(plaster)
        if "hood lower" in ob.name:
            ob.data.materials.clear()
            ob.data.materials.append(white)

# A little visible burgundy visitor carpet at the lower right.
rug=mat("burgundy visitor carpet",(.20,.055,.068))
cube("foreground carpet",(2.7,-1.10,.014),(2.2,2.3,.025),rug)

set_view((3.10,-6.10,1.66),(-.35,2.85,3.49),lens=24.5,sensor=36)
area_emitter((-2.4,.6,6.8),power=1700,size=3.4,target=(-.9,2.4,2.6),color=(.91,.97,1.0))
area_emitter((2.0,1.0,7.6),power=850,size=2.4,target=(.3,2.4,2.3),color=(1.0,1.0,.91))
area_emitter((.5,-3.5,4.5),power=240,size=5,target=(0,3,2.2),color=(1.0,.96,.85))

world=bpy.data.worlds.new("soft daylight")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.65,.71,.72,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.38
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=340
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.40
