from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(21)
scene = Scene('Garden bistro')
cream = (0.79, 0.59, 0.29)
pale = (0.88, 0.73, 0.46)

def tube(asset, name, points, radius=.009, color=cream):
    asset.include(name, sweep_tube(points=points, radius=radius, color=color))

def ellipse_points(rx, ry, center, plane='XY', n=100):
    cx,cy,cz=center
    if plane == 'XY':
        return [(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n),cz) for i in range(n+1)]
    return [(cx+rx*math.cos(i*2*math.pi/n),cy,cz+ry*math.sin(i*2*math.pi/n)) for i in range(n+1)]

table = Asset('Folding round table')
tx,ty=-.64,-.17
tube(table,'rolled tabletop edge',ellipse_points(.475,.475,(tx,ty,.785)),.009,pale)
tube(table,'under top ring',ellipse_points(.447,.447,(tx,ty,.772)),.006)
for i,x in enumerate((tx-.30,tx+.30)):
    tube(table,'folding leg A'+str(i),[(x,ty-.37,.025),(x,ty+.28,.768)],.009)
    tube(table,'folding leg B'+str(i),[(x,ty+.37,.025),(x,ty-.28,.768)],.009)
for i,y in enumerate((ty-.30,ty+.30)):
    tube(table,'lower transverse rail'+str(i),[(tx-.30,y,.135),(tx+.30,y,.135)],.008)
tube(table,'hinge rail',[(tx-.30,ty,.39),(tx+.30,ty,.39)],.007)
scene.include('table',table)

chair_specs=[(-.65,.55,-7),(.76,-.16,-19)]
def transform(p,cx,cy,angle):
    a=math.radians(angle)
    x,y,z=p
    return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)

for index,(cx,cy,ang) in enumerate(chair_specs):
    ch=Asset('Folding chair '+str(index))
    def path(name,pts,r=.008,col=cream):
        tube(ch,name,[transform(p,cx,cy,ang) for p in pts],r,col)
    path('seat rolled rim',ellipse_points(.247,.218,(0,-.015,.465)),.008,pale)
    for side,x in enumerate((-.205,.205)):
        path('cross leg forward '+str(side),[(x,-.29,.018),(x,.19,.478)],.010)
        path('cross leg backward '+str(side),[(x,.29,.018),(x,-.20,.478)],.010)
        path('back upright '+str(side),[(x,.15,.43),(x,.225,.65),(x*.96,.275,.86),(x*.85,.30,1.045)],.0075)
        path('seat bracket '+str(side),[(x,-.15,.448),(x,.13,.432),(x,.20,.38)],.007)
    path('front foot rail',[(-.205,-.245,.085),(.205,-.245,.085)],.007)
    path('rear cross rail',[(-.205,.24,.13),(.205,.24,.13)],.006)
    path('back lower arch',[(-.195,.23,.57),(-.16,.25,.64),(-.09,.265,.685),(0,.27,.698),(.09,.265,.685),(.16,.25,.64),(.195,.23,.57)],.006)
    # Oval back panels are slightly reclined.
    pts=[]
    for j in range(121):
        a=2*math.pi*j/120
        z=.972+.276*math.sin(a)
        pts.append((.196*math.cos(a),.277+(z-.972)*.13,z))
    path('oval back rim',pts,.008,pale)
    scene.include('chair '+str(index),ch)

scene.include('earth',box((200,200,.10),center=(0,0,-.065),color=(.19,.235,.105)))
# Irregular masses behind the individual hedge leaves.
for i in range(17):
    x=-3.4+i*.43
    scene.include('hedge volume '+str(i),box((.59,.65,2.4),center=(x,1.31,1.02+random.uniform(-.1,.1)),color=(.025,.12,.035)))
scene.include('left shaded shrub',ball(.75,center=(-2.3,1.05,.65),color=(.02,.075,.022)))
realize(scene)

def material(name,color,rough=.65,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal
    return m

metalmat=material('Painted warm ivory iron',pale,.48,.18)
def mesh_object(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    if isinstance(mat,list):
        for m in mat: mesh.materials.append(m)
    else:
        mesh.materials.append(mat)
    return obj

def perforated_panel(name,rx,ry,step,mapper):
    verts=[]; faces=[]
    # Each small metal web encloses an irregular pierced opening.
    for ix in range(-int(rx/step)-1,int(rx/step)+2):
        for iy in range(-int(ry/step)-1,int(ry/step)+2):
            x=ix*step; y=iy*step
            outer=[(step*.5,0),(step*.5,step*.5),(0,step*.5),(-step*.5,step*.5),
                   (-step*.5,0),(-step*.5,-step*.5),(0,-step*.5),(step*.5,-step*.5)]
            if any(((x+u)/rx)**2+((y+v)/ry)**2>1 for u,v in outer):
                continue
            start=len(verts)
            for u,v in outer: verts.append(mapper(x+u,y+v))
            hole=step*random.uniform(.24,.39)
            stretch=random.uniform(.65,1.15)
            phase=random.uniform(-.3,.3)
            for k in range(8):
                a=k*math.pi/4+phase
                r=hole*random.uniform(.75,1.17)
                verts.append(mapper(x+math.cos(a)*r,y+math.sin(a)*r*stretch))
            for k in range(8):
                faces.append((start+k,start+(k+1)%8,start+8+(k+1)%8,start+8+k))
    # Continuous narrow border closes the edges of the pierced sheet.
    base=len(verts)
    for r in (1,.956):
        for k in range(160):
            a=k*2*math.pi/160
            verts.append(mapper(rx*r*math.cos(a),ry*r*math.sin(a)))
    for k in range(160):
        faces.append((base+k,base+(k+1)%160,base+160+(k+1)%160,base+160+k))
    obj=mesh_object(name,verts,faces,metalmat)
    mod=obj.modifiers.new('thin iron sheet','SOLIDIFY')
    mod.thickness=.002
    return obj

perforated_panel('Pierced circular table top',.468,.468,.033,
                 lambda x,y:(tx+x,ty+y,.786))
for i,(cx,cy,ang) in enumerate(chair_specs):
    perforated_panel('Pierced seat '+str(i),.240,.211,.025,
        lambda x,y,cx=cx,cy=cy,ang=ang:transform((x,y-.015,.466),cx,cy,ang))
    perforated_panel('Pierced oval back '+str(i),.190,.269,.022,
        lambda x,z,cx=cx,cy=cy,ang=ang:transform((x,.277+z*.13,.972+z),cx,cy,ang))

# A textured, slightly patchy lawn beneath the furniture.
ground=bpy.data.objects.get('earth')
earthmat=material('Mottled lawn soil',(.17,.24,.095),.95)
nodes=earthmat.node_tree.nodes
links=earthmat.node_tree.links
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=27
noise.inputs['Detail'].default_value=3
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.22
ramp.color_ramp.elements[0].color=(.075,.095,.031,1)
ramp.color_ramp.elements[1].position=.79
ramp.color_ramp.elements[1].color=(.29,.36,.12,1)
links.new(noise.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and 'earth' in obj.name.lower():
        obj.data.materials.clear()
        obj.data.materials.append(earthmat)

grassmats=[material('Grass '+str(i),c,.94) for i,c in enumerate([
    (.17,.29,.075),(.23,.36,.10),(.30,.39,.13),(.105,.23,.065),(.36,.39,.16)])]
verts=[];faces=[];indices=[]
for i in range(43000):
    x=random.uniform(-4,4); y=random.uniform(-3.5,1.35)
    h=random.uniform(.012,.065)
    w=random.uniform(.0011,.0034)
    a=random.uniform(0,2*math.pi)
    dx=math.cos(a)*w;dy=math.sin(a)*w
    bendx=random.uniform(-.018,.018);bendy=random.uniform(-.018,.018)
    k=len(verts)
    verts.extend([(x-dx,y-dy,-.009),(x+dx,y+dy,-.009),(x+bendx,y+bendy,h)])
    faces.append((k,k+1,k+2));indices.append(random.randrange(len(grassmats)))
obj=mesh_object('Individual lawn blades',verts,faces,grassmats)
for poly,idx in zip(obj.data.polygons,indices): poly.material_index=idx

leafmats=[material('Hedge foliage '+str(i),c,.88) for i,c in enumerate([
    (.018,.095,.027),(.027,.15,.038),(.045,.21,.055),(.075,.25,.063),
    (.018,.12,.048),(.105,.28,.077),(.035,.18,.08)])]
verts=[];faces=[];indices=[]
for i in range(26000):
    x=random.uniform(-4,4)
    z=random.uniform(.08,2.6)
    y=1.00+random.uniform(-.12,.18)+.045*math.sin(x*8+z*7)
    length=random.uniform(.018,.052)
    width=length*random.uniform(.33,.65)
    a=random.uniform(0,2*math.pi)
    axis=Vector((math.cos(a),random.uniform(-.35,.35),math.sin(a)))
    across=Vector((-math.sin(a),random.uniform(-.45,.45),math.cos(a)))
    c=Vector((x,y,z))
    points=[c-axis*length,c-across*width,c+axis*length,c+across*width,c+Vector((0,-.009,0))]
    k=len(verts);verts.extend([tuple(p) for p in points])
    faces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
    idx=random.choices(range(7),[3,5,5,2,4,1,2])[0]
    indices.extend([idx]*4)
obj=mesh_object('Dense small hedge leaves',verts,faces,leafmats)
for poly,idx in zip(obj.data.polygons,indices):poly.material_index=idx

# A few larger leaves and small pale flowers along the left edge.
verts=[];faces=[];indices=[]
for i in range(210):
    x=random.uniform(-3,-1.25);y=random.uniform(.55,1.15);z=random.uniform(.08,.62)
    a=random.uniform(0,6.28);l=random.uniform(.035,.085);w=l*.48
    k=len(verts)
    verts.extend([(x-l*math.cos(a),y,z-l*math.sin(a)),(x-w*math.sin(a),y-.015,z+w*math.cos(a)),
                  (x+l*math.cos(a),y,z+l*math.sin(a)),(x+w*math.sin(a),y+.015,z-w*math.cos(a))])
    faces.append((k,k+1,k+2,k+3));indices.append(random.randrange(7))
obj=mesh_object('Broad leaves on left',verts,faces,leafmats)
for poly,idx in zip(obj.data.polygons,indices):poly.material_index=idx

set_view((1.65,-4.6,2.48),(-.02,.12,.66),lens=63)
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.64,.72,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.48
area_emitter((-3,-4,6),power=850,size=5,target=(0,0,.3),color=(1,.92,.78))
area_emitter((3,1,5),power=350,size=4,target=(0,0,.5),color=(.76,.87,1))
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
