from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(12)
scene = Scene('Window dining room')
dark = (.065, .075, .06)
fabric = (.32, .35, .31)
metal = (.58, .60, .56)

def add(name, node):
    scene.include(name, node)

add('floor', box((11, 17, .16), center=(0, 1.5, -.10), color=(.24, .26, .23)))
for i in range(28):
    add('long floor seam%d' % i,
        box((.009, 17, .003), center=(-5.4+i*.4, 1.5, -.017), color=(.43,.44,.40)))
for j in range(28):
    add('cross floor seam%d' % j,
        box((11, .009, .003), center=(0,-6.5+j*.61,-.016), color=(.38,.40,.36)))

add('ceiling', box((11,17,.13), center=(0,1.5,3.53), color=(.89,.90,.86)))
for i in range(83):
    add('ceiling seam%d' % i,
        box((11,.009,.005), center=(0,-6.7+i*.2,3.461), color=(.66,.68,.63)))

add('rear base',box((10.4,.18,.91),center=(0,8.1,.445),color=(.68,.71,.65)))
add('rear sill',box((10.5,.3,.09),center=(0,8.02,.94),color=(.42,.45,.40)))
add('rear header',box((10.5,.19,.18),center=(0,8.1,3.16),color=(.53,.56,.50)))
for i,x in enumerate([-5.1,-3.4,-1.7,0,1.7,3.4,5.1]):
    add('rear mullion%d'%i,box((.065,.14,2.22),center=(x,8.06,2.07),color=(.34,.39,.33)))
add('right base',box((.18,15,.88),center=(5.1,.6,.44),color=(.73,.75,.69)))
add('right sill',box((.29,15,.08),center=(5.04,.6,.94),color=(.43,.47,.40)))
add('right header',box((.16,15,.16),center=(5.1,.6,3.2),color=(.53,.57,.49)))
for i,y in enumerate([-6,-3.8,-1.6,.6,2.8,5,7.2,8.1]):
    add('right post%d'%i,box((.13,.065,2.27),center=(5.05,y,2.08),color=(.42,.47,.39)))

add('outside ground',box((45,40,.15),center=(0,16,-.25),color=(.87,.89,.83)))
add('distant facade',box((24,.2,2.5),center=(0,16,1.1),color=(.89,.90,.85)))
for i in range(14):
    x=random.uniform(-12,12)
    y=random.uniform(10,14)
    z=random.uniform(1.8,3.4)
    add('outside trunk%d'%i,rod(.035,start=(x,y,0),end=(x,y,z),color=(.55,.59,.49)))
    for j in range(3):
        add('outside canopy%d_%d'%(i,j),
            ball(random.uniform(.5,.85),
                 center=(x+random.uniform(-.7,.7),y+random.uniform(-.5,.5),z+random.uniform(-.3,.5)),
                 color=(.71,.75,.65)))

def pedestal(asset,name,x,y,height=.56):
    asset.include(name+'foot',rod(.29,length=.065,center=(x,y,.047),color=metal))
    asset.include(name+'column',rod(.07,length=height-.07,center=(x,y,(height+.07)/2),color=metal))

def chair(name,x,y,facing=1,width=.91):
    a=Asset(name)
    pedestal(a,'base',x,y)
    a.include('seat',box((width,.69,.15),center=(x,y,.61),color=fabric))
    a.include('back',box((width,.10,.83),center=(x,y-facing*.33,1.005),color=fabric))
    for s in [-1,1]:
        a.include('side'+str(s),box((.065,.69,.54),center=(x+s*(width/2-.03),y,.89),color=(.36,.39,.34)))
        a.include('trim'+str(s),box((.014,.70,.017),center=(x+s*width/2,y,1.17),color=(.66,.68,.62)))
    add(name,a)

def table(name,x,y,w=1.35,d=.86):
    a=Asset(name)
    a.include('top',box((w,d,.055),center=(x,y,.88),color=(.72,.74,.68)))
    a.include('edge',box((w+.015,d+.015,.025),center=(x,y,.846),color=(.30,.33,.28)))
    for i,xx in enumerate([x-w*.32,x+w*.32]):
        a.include('leg%d'%i,box((.045,.055,.82),center=(xx,y,.42),color=metal))
        a.include('foot%d'%i,rod(.14,length=.035,center=(xx,y,.025),color=metal))
    a.include('sugar',box((.12,.10,.11),center=(x+.13,y,.962),color=(.88,.88,.82)))
    a.include('ashtray',rod(.08,length=.018,center=(x-.18,y-.05,.917),color=(.77,.79,.72)))
    add(name,a)

for row,y in enumerate([-2,.5,3,5.5]):
    table('right table%d'%row,2.87,y,1.48,.89)
    chair('right near%d'%row,2.88,y-.88,1,1.04)
    chair('right far%d'%row,2.88,y+.87,-1,1.04)
    table('middle table%d'%row,.35,y+.35,1.25,.82)
    chair('middle near%d'%row,.34,y-.45,1,.92)
    chair('middle far%d'%row,.34,y+1.14,-1,.92)

for row,y in enumerate([-3.65,-1.05,1.55,4.15,6.55]):
    a=Asset('left booth%d'%row)
    a.include('back',box((2.12,.14,.95),center=(-3.17,y-.42,.98),color=(.29,.33,.29)))
    a.include('seat',box((2.12,.76,.18),center=(-3.17,y,.56),color=(.37,.40,.34)))
    for s in [-1,1]:
        a.include('arm'+str(s),box((.08,.83,.60),center=(-3.17+s*1.02,y,.83),color=(.39,.42,.36)))
    for xx in [-3.85,-2.5]:
        pedestal(a,str(xx),xx,y,.46)
    add('left booth%d'%row,a)
    table('left table%d'%row,-3.17,y+.77,2.14,1.02)
table('foreground table',-2.65,-5.35,2.75,1.30)

# Revolved metal lamp profiles are built as separate mesh surfaces after
# the SceneAct scene is realized, avoiding costly solid Boolean operations.
lamps=[
    (-3.6,-3.15,1.22),(-3.15,.35,.87),(-3.15,3.1,.75),(-3.15,5.7,.69),
    (.2,-.05,.83),(.2,3,.74),(.2,5.9,.67),
    (3.2,-.2,1),(3.2,2.7,.79),(3.2,5.8,.70),(4.65,3.8,.70)
]
for i,(x,y,s) in enumerate(lamps):
    a=Asset('pendant%d'%i)
    z=2.64
    a.include('neck',rod(.145*s,length=.32*s,center=(x,y,z+.43*s),color=dark))
    a.include('band',rod(.149*s,length=.025,center=(x,y,z+.44*s),color=(.46,.49,.43)))
    a.include('wire',rod(.007,start=(x,y,z+.59*s),end=(x,y,3.46),color=(.18,.21,.17)))
    a.include('rose',rod(.075*s,length=.018,center=(x,y,3.451),color=dark))
    add('pendant%d'%i,a)

for x in [-2.3,1.5,4]:
    for y in [-3,1.5,5.5]:
        add('ceiling fitting%s%s'%(x,y),
            rod(.09,length=.009,center=(x,y,3.447),color=(.56,.59,.52)))

def leaf(name,a,b,width,color):
    av,bv=Vector(a),Vector(b)
    delta=bv-av
    n=ball(1,color=color)
    n.resize((width,width*.25,delta.length/2))
    n.turn('y',math.degrees(math.acos(max(-1,min(1,delta.z/delta.length)))),pivot=(0,0,0))
    n.turn('z',math.degrees(math.atan2(delta.y,delta.x)),pivot=(0,0,0))
    n.move(tuple((av+bv)/2))
    add(name,n)

plantx,planty=4.37,-2.7
add('palm planter',rod(.37,length=.57,center=(plantx,planty,.285),color=(.18,.22,.16)))
for k in range(16):
    ang=random.uniform(0,2*math.pi)
    h=random.uniform(1.6,2.55)
    reach=random.uniform(.75,1.45)
    points=[]
    for j in range(9):
        t=j/8
        points.append((plantx+math.cos(ang)*reach*t,
                       planty+math.sin(ang)*reach*t,
                       .42+h*(1-(1-t)**2)-.5*t*t))
    add('palm stem%d'%k,sweep_tube(points=points,radius=.009,color=(.13,.19,.11)))
    for j in range(2,9):
        t=j/8
        base=Vector(points[j])
        for side in [-1,1]:
            lateral=Vector((-math.sin(ang),math.cos(ang),0))*side
            end=base+lateral*(.43*(1-t)+.17)+Vector((math.cos(ang)*.16,math.sin(ang)*.16,-.16))
            leaf('leaf%d_%d_%d'%(k,j,side),tuple(base),tuple(end),.036,(.095,.15,.075))

for i in range(16):
    x=-1.9+i*.19
    y=6.85+random.uniform(-.15,.15)
    h=random.uniform(.8,1.35)
    add('rear stem%d'%i,rod(.01,start=(x,y,.62),end=(x,y,h),color=(.22,.29,.17)))
    for j in range(3):
        leaf('rear leaf%d_%d'%(i,j),(x,y,h-j*.12),
             (x+random.uniform(-.25,.25),y+random.uniform(-.16,.16),h+.13-j*.1),
             .07,(.28,.35,.23))

realize(scene)

def material(name,color,roughness=.4,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    return m

lamp_outer=material('dark enamel',dark,.26,.25)
lamp_inner=material('white reflector',(.84,.86,.79),.35,.15)
for i,(x,y,s) in enumerate(lamps):
    vertices=[]
    faces=[]
    segments=48
    rings=12
    for inner in [False,True]:
        radius=(.421 if inner else .43)*s
        for j in range(rings+1):
            theta=(math.pi/2)*(j/rings)
            r=radius*math.sin(theta)
            z=2.64+radius*math.cos(theta)
            for k in range(segments):
                ang=2*math.pi*k/segments
                vertices.append((x+r*math.cos(ang),y+r*math.sin(ang),z))
    layer=(rings+1)*segments
    for side in range(2):
        off=side*layer
        for j in range(rings):
            for k in range(segments):
                a=off+j*segments+k
                b=off+j*segments+(k+1)%segments
                c=b+segments
                d=a+segments
                faces.append((a,b,c,d) if side==0 else (d,c,b,a))
    mesh=bpy.data.meshes.new('reflector profile')
    mesh.from_pydata(vertices,[],faces)
    mesh.materials.append(lamp_outer)
    mesh.materials.append(lamp_inner)
    obj=bpy.data.objects.new('bell shade%d'%i,mesh)
    bpy.context.collection.objects.link(obj)
    for p in mesh.polygons:
        p.material_index=int(p.index>=rings*segments)
        p.use_smooth=True

set_view((-4,-7.4,2.15),(-.1,4,1.72),lens=33,sensor=36)
area_emitter((0,7.7,2.8),power=1900,size=8,target=(0,0,.5),color=(1,1,.96))
area_emitter((4.8,1.5,2.6),power=1600,size=7,target=(-2,1,1),color=(1,1,.97))
area_emitter((-1,-3,3.35),power=320,size=5,target=(0,2,.4))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Daylight world')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(.78,.80,.75,1)
background.inputs['Strength'].default_value=.65
sc.render.engine='CYCLES'
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.45
sc.use_nodes=True
tree=sc.node_tree
tree.nodes.clear()
rl=tree.nodes.new('CompositorNodeRLayers')
bw=tree.nodes.new('CompositorNodeRGBToBW')
out=tree.nodes.new('CompositorNodeComposite')
tree.links.new(rl.outputs['Image'],bw.inputs[0])
tree.links.new(bw.outputs[0],out.inputs[0])
