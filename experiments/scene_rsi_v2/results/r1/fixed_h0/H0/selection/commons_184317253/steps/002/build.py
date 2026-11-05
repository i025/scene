import bpy, math, random
from sceneact import *
random.seed(21)

scene=Scene("Historic tiled chamber")
ivory=(.69,.72,.67)
wood=(.060,.041,.027)
iron=(.035,.042,.037)

def block(name,size,center,color):
    scene.include(name,box(size=size,center=center,color=color))

block("stone floor",(12,12,.16),(0,0,-.10),(.38,.39,.33))
block("rear plaster wall",(8,.30,7.3),(0,3.47,3.60),ivory)
block("left masonry pier",(.40,8,8),(-3.8,1,3.95),(.71,.73,.67))
block("right wall",(.30,8,7),(4,2,3.45),ivory)
block("ceramic backing",(4.70,.045,4.05),(-1.37,3.285,2.15),(.53,.59,.49))
block("stone skirting",(7.7,.15,.23),(0,3.18,.13),(.49,.51,.45))

block("fireplace soot",(1.27,.045,2.38),(-.05,3.20,1.23),(.105,.108,.079))
block("left fireplace jamb",(.14,.60,2.1),(-.72,2.96,1.07),(.49,.50,.43))
block("right fireplace jamb",(.14,.60,2.1),(.62,2.96,1.07),(.52,.53,.46))
block("hearth",(1.55,.92,.13),(-.05,2.78,.08),(.28,.29,.25))
block("hood white apron",(1.55,.94,.61),(-.05,2.84,2.57),(.77,.79,.73))
block("black fireback",(.90,.08,.70),(-.05,3.12,.60),(.045,.050,.040))
for x in (-.47,.37):
    scene.include("fire iron"+str(x),rod(.023,start=(x,2.98,.17),end=(x,2.98,.97),color=iron))
scene.include("fire iron crossbar",rod(.024,start=(-.47,2.98,.93),end=(.37,2.98,.93),color=iron))

for i,(x,w) in enumerate(((1.13,.79),(2.02,.89),(3.04,1.02),(3.80,.40))):
    block("cabinet body"+str(i),(w,.69,2.27),(x,3.00,1.42),wood)
    block("cabinet cornice"+str(i),(w+.07,.77,.09),(x,2.97,2.59),(.075,.057,.039))
    block("cabinet recessed panel"+str(i),(w-.14,.035,2.09),(x,2.638,1.42),(.074,.052,.034))
    for s in (-1,1):
        block("cabinet upright"+str((i,s)),(.065,.08,2.23),(x+s*(w/2-.04),2.60,1.43),(.040,.028,.019))
    for z in (.39,2.43):
        block("cabinet rail"+str((i,z)),(w-.06,.07,.065),(x,2.60,z),(.043,.030,.021))

block("open shelving shadow",(.32,.08,2.08),(1.62,3.08,1.39),(.017,.020,.016))
for z in (.40,.84,1.29,1.75,2.22):
    block("open shelf"+str(z),(.34,.57,.045),(1.62,2.83,z),(.048,.036,.024))

block("raised stone platform",(3.2,1.15,.13),(2.40,2.13,.48),(.49,.50,.44))
for x in (1.03,2.35,3.70):
    block("platform support"+str(x),(.16,.88,.43),(x,2.23,.22),(.39,.40,.34))
block("platform edge",(3.25,.11,.07),(2.40,1.53,.40),(.34,.35,.30))

for i,(x,y) in enumerate(((-2.6,1.03),(1.04,1.03),(3.8,1.03))):
    scene.include("barrier post"+str(i),rod(.020,start=(x,y,.02),end=(x,y,.83),color=(.35,.36,.32)))
    block("post foot"+str(i),(.25,.20,.04),(x,y,.025),(.29,.30,.26))
scene.include("burgundy barrier",rod(.023,start=(-4,1.03,.74),end=(4,1.03,.74),color=(.15,.022,.030)))

realize(scene)

def mat(name,color,rough=.8,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=rough
    p.inputs["Metallic"].default_value=metal
    return m

plaster=mat("aged lime plaster",(.71,.74,.68))
p=plaster.node_tree.nodes.get("Principled BSDF")
noise=plaster.node_tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=5
noise.inputs["Detail"].default_value=4
ramp=plaster.node_tree.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.18
ramp.color_ramp.elements[0].color=(.56,.59,.52,1)
ramp.color_ramp.elements[1].position=.82
ramp.color_ramp.elements[1].color=(.79,.82,.76,1)
plaster.node_tree.links.new(noise.outputs["Fac"],ramp.inputs[0])
plaster.node_tree.links.new(ramp.outputs[0],p.inputs["Base Color"])
bump=plaster.node_tree.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.12
bump.inputs["Distance"].default_value=.035
plaster.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
plaster.node_tree.links.new(bump.outputs[0],p.inputs["Normal"])

white=mat("chalk plaster",(.78,.80,.74))
cream=mat("ivory ceramic",(.66,.67,.49),.48)
blue=mat("deep blue ceramic",(.065,.18,.25),.43)
teal=mat("turquoise ceramic",(.15,.32,.32),.43)
pale=mat("pale blue ceramic",(.37,.49,.46),.48)
gold=mat("muted ochre ornament",(.42,.29,.045),.60,.12)
black=mat("blackened iron",(.028,.034,.030),.72,.45)
darkwood=mat("dark old door timber",(.043,.027,.014))
stone=mat("marble door surround",(.57,.59,.51))

def mesh(name,verts,faces,material):
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    if material: me.materials.append(material)
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
    for point,co in zip(sp.points,pts):
        point.co=(*co,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob

def lathe(name,profile,center,material,n=64):
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

verts=[(-.825,2.37,2.87),(.725,2.37,2.87),(.725,3.31,2.87),(-.825,3.31,2.87),
       (-.105,2.95,4.30),(.005,2.95,4.30),(.005,3.16,4.30),(-.105,3.16,4.30)]
mesh("tapered smoke canopy",verts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],white)

# Dome and the broad pendentive arches below it.
verts=[]; faces=[]
N=112; M=36
for i in range(M+1):
    phi=math.pi*.5*i/M
    rr=4.65*math.cos(phi)
    z=5.80+3.55*math.sin(phi)
    for j in range(N):
        a=2*math.pi*j/N
        verts.append((rr*math.cos(a),2+rr*math.sin(a),z))
for i in range(M):
    for j in range(N):
        faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
ob=mesh("high plaster dome",verts,faces,plaster)
for f in ob.data.polygons: f.use_smooth=True

def ribbon(name,pts,width,material,y=3.08):
    v=[]
    for i,(x,z) in enumerate(pts):
        a=pts[max(0,i-1)]; b=pts[min(len(pts)-1,i+1)]
        dx=b[0]-a[0]; dz=b[1]-a[1]
        d=math.hypot(dx,dz)
        nx=-dz/d; nz=dx/d
        v.extend([(x+nx*width/2,y,z+nz*width/2),(x-nx*width/2,y,z-nz*width/2)])
    return mesh(name,v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],material)

pts=[]
for i in range(71):
    t=i/70
    pts.append((-3.65+4.82*t,3.95+2.12*math.sqrt(max(0,1-t*t))))
ribbon("broad left arch",pts,.17,white)
pts=[]
for i in range(71):
    t=i/70
    pts.append((1.17+3.5*t,3.95+2.25*math.sin(t*math.pi/2)))
ribbon("broad right arch",pts,.19,white)
seam=mat("fine grey vault seams",(.48,.52,.46))
line("upper arch seam",[(-3.7,3.09,6.70),(-2.5,3.09,6.72),(-1.3,3.09,6.4),(-.1,3.09,5.58),(.95,3.09,4.23),(1.33,3.09,4.23),(2.15,3.09,5.28),(3.7,3.09,6.45)],.009,seam)

def archpoly(cx,y,z,w,h,material,name):
    pts=[(cx-w/2,y,z),(cx+w/2,y,z),(cx+w/2,y,z+h-w/2)]
    for i in range(1,33):
        a=math.pi*i/32
        pts.append((cx+w/2*math.cos(a),y,z+h-w/2+w/2*math.sin(a)))
    return mesh(name,pts,[tuple(range(len(pts)))],material)

glow=mat("bright daylight",(.95,1,.95))
ps=glow.node_tree.nodes.get("Principled BSDF")
ps.inputs["Emission Color"].default_value=(.95,1,.95,1)
ps.inputs["Emission Strength"].default_value=2
reveal=mat("deep window reveals",(.46,.51,.43))
for i,(x,z,w,h) in enumerate(((-1.70,6.42,.43,.91),(.45,6.18,.48,.83),(2.65,6.58,.50,.91))):
    archpoly(x,3.13,z,w+.15,h+.10,reveal,"window recess"+str(i))
    archpoly(x+.055,3.105,z+.045,w,h,glow,"daylight opening"+str(i))

# Dense blue and ivory floral ceramic wall.
tv=[]; tf=[]; ti=[]
def tilepoly(coords,idx,y=3.237):
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
    tilepoly(co,idx)

doorx=-2.15
s=.165
for row in range(25):
    z=.20+(row+.5)*s
    for col in range(29):
        x=-3.72+(col+.5)*s
        if x>.99 or z>4.18: continue
        if abs(x-doorx)<.90 and z<2.98: continue
        tilepoly([(x-s*.49,z-s*.49),(x+s*.49,z-s*.49),(x+s*.49,z+s*.49),(x-s*.49,z+s*.49)],0,3.245)
        for k in range(8):
            a=k*math.pi/4
            disk(x+.045*math.cos(a),z+.045*math.sin(a),.028,.012,1 if (row+col+k)%3 else 2,a)
        disk(x,z,.022,.022,2,n=8)
        disk(x,z,.008,.008,0,n=8)
        for ax,az in ((-1,-1),(-1,1),(1,-1),(1,1)):
            disk(x+ax*.071,z+az*.071,.011,.019,3,ax*az*.7,n=6)
ob=mesh("floral ceramic tilework",tv,tf,None)
for ma in (cream,blue,teal,pale): ob.data.materials.append(ma)
for p,i in zip(ob.data.polygons,ti): p.material_index=i

for j in range(95):
    x=-3.72+j*.05
    if x>.99: break
    mesh("top tile border",[(x-.021,3.23,4.18),(x,3.23,4.235),(x+.021,3.23,4.18),(x,3.23,4.125)],[(0,1,2,3)],blue)

# Rectangular stone portal with a shallow arched doorway.
cube("portal stone frame",(doorx,3.185,1.52),(1.84,.12,3.04),stone)
archpoly(doorx,3.10,.07,1.43,2.31,darkwood,"arched wooden doorway")
for x in (doorx-.365,doorx+.365):
    cube("recessed timber panel",(x,3.075,1.05),(.57,.045,1.82),darkwood)
    for xx in (x-.285,x+.285):
        cube("dark vertical door framing",(xx,3.04,1.06),(.045,.045,1.90),darkwood)
    for z in (.17,1.97):
        cube("dark horizontal framing",(x,3.04,z),(.58,.045,.048),darkwood)
    for row in range(15):
        for col in range(4):
            xx=x-.205+col*.135
            zz=.27+row*.112
            a=.028
            mesh("small brass fret",[(xx-a,3.035,zz),(xx,3.035,zz+a),(xx+a,3.035,zz),(xx,3.035,zz-a)],[(0,1,2,3)],gold)
cube("central timber stile",(doorx,3.025,1.10),(.065,.06,2.06),darkwood)

cube("inscription marble border",(doorx,3.095,2.77),(1.76,.075,.43),stone)
cube("ochre plaque border",(doorx,3.043,2.77),(1.62,.035,.32),gold)
cube("blue inscription field",(doorx,3.017,2.77),(1.48,.022,.23),blue)
for i in range(23):
    x=doorx-.70+i*.061
    z=2.75+random.uniform(-.020,.020)
    line("calligraphic inscription",[(x,2.999,z+.075),(x+.011,2.999,z-.012),(x+.037,2.999,z-.020),(x+.048,2.999,z+.035)],.007,gold)
    if i%3==0:
        line("inscription dot",[(x+.020,2.997,2.84),(x+.026,2.997,2.84)],.007,gold)

# Cauldron located on the viewing ray toward the fireplace.
cx=-1.15; cy=1.80
lathe("large iron cauldron",[(.12,.30),(.17,.43),(.27,.51),(.57,.54),(.73,.50),(.76,.52),(.79,.52),(.79,.48),(.72,.47),(.23,.39),(.19,0)],(cx,cy,0),black)
for z,r in ((.77,.52),(.22,.44)):
    line("heavy cauldron rim",[(cx+r*math.cos(2*math.pi*i/80),cy+r*math.sin(2*math.pi*i/80),z) for i in range(81)],.018,black)
for dx in (-.52,.52):
    line("cauldron loop handle",[(cx+dx+.085*math.cos(2*math.pi*i/32),cy,.63+.105*math.sin(2*math.pi*i/32)) for i in range(33)],.022,black)
for a in (0,2.1,4.2):
    cube("cauldron short foot",(cx+.34*math.cos(a),cy+.34*math.sin(a),.10),(.11,.13,.20),black)

potmat=mat("dark earthenware",(.041,.049,.038))
for i,(x,r,h) in enumerate(((.96,.13,.34),(1.70,.11,.29),(2.32,.12,.39),(2.98,.13,.37),(3.71,.15,.43))):
    lathe("cabinet vessel"+str(i),[(0,.065),(.03,r*.77),(h*.37,r),(h*.64,r*.91),(h*.80,r*.40),(h*.95,r*.31),(h,r*.43)],(x,2.96,2.64),potmat)
    line("vessel lip",[(x+r*.43*math.cos(2*math.pi*j/28),2.96+r*.43*math.sin(2*math.pi*j/28),2.64+h) for j in range(29)],.009,potmat)

joint=mat("floor joints",(.24,.25,.21))
floor_mats=[mat("limestone slab"+str(i),(.34+.022*i,.35+.021*i,.29+.019*i)) for i in range(6)]
for ix in range(-7,7):
    for iy in range(-6,6):
        x=ix*.70+(iy%2)*.35
        y=iy*.63
        cube("individual worn floor slab",(x,y,-.011),(.687,.616,.045),random.choice(floor_mats))

damage=mat("worn wall plaster",(.43,.47,.40))
for i in range(145):
    x=random.uniform(.78,3.95)
    z=random.uniform(2.76,4.05)
    if random.random()<.65:
        w=random.uniform(.018,.10); h=random.uniform(.025,.13)
        mesh("flaking plaster",[(x-w,3.306,z),(x-w*.4,3.305,z+h),(x+w*.4,3.304,z+h*.65),(x+w,3.305,z-h*.3),(x,3.305,z-h)],[(0,1,2,3,4)],damage)

# A small carpet corner enters the lower right of the frame.
rug=mat("burgundy carpet",(.16,.028,.040))
cube("visitor carpet",(2.25,-.30,.025),(2.10,2.20,.025),rug)

# Small pale lettering on the museum barrier.
letter=mat("barrier lettering",(.66,.65,.55))
for x in (-1.80,.10,2.0):
    cu=bpy.data.curves.new("museum label","FONT")
    cu.body="MEVLÂHANE"
    cu.size=.055
    cu.extrude=0
    ob=bpy.data.objects.new("museum ribbon lettering",cu)
    bpy.context.collection.objects.link(ob)
    ob.location=(x,1.003,.727)
    ob.rotation_euler=(math.pi/2,0,0)
    ob.data.materials.append(letter)

set_view((-3.30,-.60,1.50),(-.25,3.00,3.35),lens=24.5,sensor=36)
area_emitter((-2.4,.6,6.8),power=650,size=3.2,target=(-.9,2.4,2.6),color=(.88,.96,1))
area_emitter((2,1,7.6),power=250,size=2.4,target=(.3,2.4,2.3),color=(1,1,.93))
area_emitter((-.5,-2.5,4.5),power=65,size=4,target=(0,3,2),color=(1,.95,.85))

world=bpy.data.worlds.new("soft daylight")
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.62,.69,.70,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.22
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=340
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=-.35
