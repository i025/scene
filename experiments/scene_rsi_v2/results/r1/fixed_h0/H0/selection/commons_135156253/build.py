from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(21)
scene = Scene('Garden bistro furniture')
gold = (.78,.53,.22)
ivory = (.93,.75,.46)

def tube(asset,name,pts,r=.008,color=gold):
    asset.include(name,sweep_tube(points=pts,radius=r,color=color))

def ellipse(rx,ry,z,cx=0,cy=0,n=100):
    return [(cx+rx*math.cos(2*math.pi*i/n),
             cy+ry*math.sin(2*math.pi*i/n),z) for i in range(n+1)]

tx,ty=-.40,-.12
topz=.88
table=Asset('Round folding table')
tube(table,'top rolled edge',ellipse(.49,.49,topz,tx,ty),.009,ivory)
tube(table,'underside ring',ellipse(.465,.465,topz-.013,tx,ty),.006)
for i,x in enumerate((tx-.30,tx+.30)):
    tube(table,'crossed support A '+str(i),[(x,ty-.38,.02),(x,ty+.29,topz-.018)],.009)
    tube(table,'crossed support B '+str(i),[(x,ty+.38,.02),(x,ty-.29,topz-.018)],.009)
for i,y in enumerate((ty-.31,ty+.31)):
    tube(table,'low crossbar '+str(i),[(tx-.30,y,.13),(tx+.30,y,.13)],.008)
tube(table,'hinge',[(tx-.30,ty,.43),(tx+.30,ty,.43)],.007)
scene.include('table',table)

specs=[(-.47,.65,7,1.20),(.80,.04,-40,1.0)]

def transform(p,cx,cy,angle,width=1):
    x,y,z=p
    x*=width
    a=math.radians(angle)
    return (cx+x*math.cos(a)-y*math.sin(a),
            cy+x*math.sin(a)+y*math.cos(a),z)

for i,(cx,cy,ang,width) in enumerate(specs):
    chair=Asset('Folding chair '+str(i))
    def path(name,pts,r=.008,color=gold):
        tube(chair,name,[transform(p,cx,cy,ang,width) for p in pts],r,color)
    path('seat rim',ellipse(.247,.218,.465,0,-.015),.008,ivory)
    for j,x in enumerate((-.205,.205)):
        path('crossed leg A '+str(j),[(x,-.29,.018),(x,.19,.478)],.010)
        path('crossed leg B '+str(j),[(x,.29,.018),(x,-.20,.478)],.010)
        path('curved back standard '+str(j),
             [(x,.15,.43),(x,.225,.65),(x*.96,.275,.86),(x*.85,.30,1.045)],.008)
        path('seat support '+str(j),[(x,-.15,.448),(x,.13,.432),(x,.20,.38)],.006)
    path('front low rail',[(-.205,-.245,.085),(.205,-.245,.085)],.007)
    path('rear low rail',[(-.205,.24,.13),(.205,.24,.13)],.006)
    path('back arch',[(-.195,.23,.57),(-.16,.25,.64),(-.09,.265,.685),
                      (0,.27,.698),(.09,.265,.685),(.16,.25,.64),(.195,.23,.57)],.006)
    pts=[]
    for k in range(121):
        a=2*math.pi*k/120
        z=.972+.276*math.sin(a)
        pts.append((.196*math.cos(a),.277+(z-.972)*.13,z))
    path('oval back rim',pts,.008,ivory)
    scene.include('chair '+str(i),chair)

scene.include('lawn base',box((30,30,.1),center=(0,0,-.063),color=(.08,.19,.055)))
scene.include('dark hedge interior',box((12,.75,3.5),center=(0,1.86,1.5),color=(.008,.043,.014)))
realize(scene)

def material(name,color,rough=.7,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m

paint=material('Warm cream painted metal',ivory,.46,.12)

def mesh_object(name,verts,faces,mats):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    if not isinstance(mats,list): mats=[mats]
    for m in mats: mesh.materials.append(m)
    return obj

def panel(name,rx,ry,step,mapper):
    verts=[]; faces=[]
    outerangles=[2*math.pi*k/12 for k in range(12)]
    for ix in range(-int(rx/step)-1,int(rx/step)+2):
        for iy in range(-int(ry/step)-1,int(ry/step)+2):
            x=ix*step
            y=iy*step
            outer=[]
            for a in outerangles:
                d=step*.5/max(abs(math.cos(a)),abs(math.sin(a)))
                outer.append((d*math.cos(a),d*math.sin(a)))
            if any(((x+u)/rx)**2+((y+v)/ry)**2>.995 for u,v in outer):
                continue
            start=len(verts)
            verts.extend(mapper(x+u,y+v) for u,v in outer)
            hole=step*random.uniform(.31,.43)
            stretch=random.uniform(.65,1.15)
            phase=random.uniform(-.7,.7)
            ox=random.uniform(-.07,.07)*step
            oy=random.uniform(-.07,.07)*step
            for a in outerangles:
                a+=phase
                r=hole*random.uniform(.78,1.12)
                verts.append(mapper(x+ox+math.cos(a)*r,y+oy+math.sin(a)*r*stretch))
            for k in range(12):
                faces.append((start+k,start+(k+1)%12,
                              start+12+(k+1)%12,start+12+k))
    start=len(verts)
    for scale in (1,.95):
        for k in range(160):
            a=2*math.pi*k/160
            verts.append(mapper(rx*scale*math.cos(a),ry*scale*math.sin(a)))
    for k in range(160):
        faces.append((start+k,start+(k+1)%160,start+160+(k+1)%160,start+160+k))
    obj=mesh_object(name,verts,faces,paint)
    obj.modifiers.new('metal thickness','SOLIDIFY').thickness=.0015

panel('Decorative pierced table',.483,.483,.035,
      lambda x,y:(tx+x,ty+y,topz+.001))
for i,(cx,cy,ang,width) in enumerate(specs):
    panel('Decorative pierced seat '+str(i),.240,.211,.027,
          lambda x,y,cx=cx,cy=cy,ang=ang,width=width:
              transform((x,y-.015,.466),cx,cy,ang,width))
    panel('Decorative pierced back '+str(i),.190,.269,.025,
          lambda x,z,cx=cx,cy=cy,ang=ang,width=width:
              transform((x,.277+z*.13,.972+z),cx,cy,ang,width))

groundmat=material('Patchy green lawn',(.08,.19,.045),.98)
nodes=groundmat.node_tree.nodes
links=groundmat.node_tree.links
tex=nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value=22
tex.inputs['Detail'].default_value=4
coord=nodes.new('ShaderNodeTexCoord')
links.new(coord.outputs['Object'],tex.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.23
ramp.color_ramp.elements[0].color=(.035,.085,.021,1)
ramp.color_ramp.elements[1].position=.78
ramp.color_ramp.elements[1].color=(.15,.27,.065,1)
links.new(tex.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.45
bump.inputs['Distance'].default_value=.018
links.new(tex.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj.dimensions.x>20:
        obj.data.materials.clear()
        obj.data.materials.append(groundmat)

grassmats=[material('Grass '+str(i),c,.95) for i,c in enumerate([
    (.055,.16,.029),(.10,.23,.045),(.15,.28,.06),
    (.035,.12,.028),(.20,.27,.085)])]
verts=[];faces=[];indices=[]
for i in range(85000):
    x=random.uniform(-4,4);y=random.uniform(-3.5,1.6)
    h=random.uniform(.012,.05)
    w=random.uniform(.001,.0028)
    a=random.uniform(0,2*math.pi)
    dx=w*math.cos(a);dy=w*math.sin(a)
    k=len(verts)
    verts.extend([(x-dx,y-dy,-.007),(x+dx,y+dy,-.007),
                  (x+random.uniform(-.013,.013),y+random.uniform(-.013,.013),h)])
    faces.append((k,k+1,k+2))
    indices.append(random.randrange(5))
obj=mesh_object('Fine lawn blades',verts,faces,grassmats)
for p,m in zip(obj.data.polygons,indices):p.material_index=m

leafmats=[material('Hedge leaf '+str(i),c,.86) for i,c in enumerate([
    (.006,.045,.013),(.010,.080,.020),(.018,.115,.028),
    (.035,.155,.038),(.009,.070,.032),(.052,.18,.045),
    (.015,.10,.045)])]
verts=[];faces=[];indices=[]
for i in range(75000):
    x=random.uniform(-4.5,4.5)
    z=random.uniform(.055,3)
    y=1.28+random.uniform(-.17,.20)+.095*math.sin(x*3.3+z*2.2)+.045*math.sin(x*13-z*9)
    length=random.uniform(.012,.037)
    width=length*random.uniform(.30,.58)
    a=random.uniform(0,2*math.pi)
    axis=Vector((math.cos(a),random.uniform(-.4,.4),math.sin(a)))
    across=Vector((-math.sin(a),random.uniform(-.5,.5),math.cos(a)))
    c=Vector((x,y,z))
    k=len(verts)
    verts.extend(tuple(p) for p in [
        c-axis*length,c-across*width,c+axis*length,c+across*width,
        c+Vector((0,-.008,0))])
    faces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
    m=random.choices(range(7),[3,5,5,2,4,1,2])[0]
    indices.extend([m]*4)
obj=mesh_object('Dense irregular hedge foliage',verts,faces,leafmats)
for p,m in zip(obj.data.polygons,indices):p.material_index=m

verts=[];faces=[];indices=[]
for i in range(1700):
    x=random.uniform(-3,-1.15)
    y=random.uniform(.77,1.38)
    z=random.uniform(.04,.68)
    a=random.uniform(0,2*math.pi)
    length=random.uniform(.025,.072)
    width=length*.52
    k=len(verts)
    verts.extend([
        (x-length*math.cos(a),y,z-length*math.sin(a)),
        (x-width*math.sin(a),y-.018,z+width*math.cos(a)),
        (x+length*math.cos(a),y,z+length*math.sin(a)),
        (x+width*math.sin(a),y+.018,z-width*math.cos(a))])
    faces.append((k,k+1,k+2,k+3))
    indices.append(random.randrange(7))
obj=mesh_object('Broad leaves at left hedge foot',verts,faces,leafmats)
for p,m in zip(obj.data.polygons,indices):p.material_index=m

flower=material('Small white lawn flowers',(.85,.85,.71),.8)
verts=[];faces=[]
for i in range(75):
    x=random.uniform(-2,-.8);y=random.uniform(-.15,.9)
    z=random.uniform(.025,.055)
    r=random.uniform(.003,.006)
    k=len(verts)
    verts.extend([(x-r,y,z),(x,y-r,z+.002),(x+r,y,z),(x,y+r,z+.002)])
    faces.append((k,k+1,k+2,k+3))
mesh_object('Tiny lawn flowers',verts,faces,flower)

set_view((1.50,-4.6,1.85),(.06,.16,.72),lens=66)

sc=bpy.context.scene
world=bpy.data.worlds.new('Soft outdoor ambient')
sc.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.67,.74,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.32
area_emitter((-3,-4,6),power=1050,size=5,target=(0,0,.4),color=(1,.93,.80))
area_emitter((3,0,5),power=180,size=4,target=(0,0,.5),color=(.78,.88,1))
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
