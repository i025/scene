from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(9)
scene = Scene('Kitchen corner')
cream=(.79,.75,.63)
ivory=(.90,.88,.79)
white=(.93,.92,.86)
metal=(.52,.53,.48)

def add(name,node):
    scene.include(name,node)
    return node

def tube(name,pts,r,col):
    return add(name,sweep_tube(points=pts,radius=r,color=col))

# Walls, stone worktop, and the tall wall cabinet.
add('back wall',box((4,.12,3.4),center=(0,.79,1.7),color=(.76,.74,.65)))
add('counter slab',box((3.4,1.12,.055),center=(0,.12,.895),color=(.37,.35,.29)))
add('backsplash',box((3.4,.045,.15),center=(0,.70,.985),color=(.37,.35,.29)))
add('lower cabinets',box((3.4,.94,.86),center=(0,.16,.43),color=(.64,.60,.47)))
add('cabinet body',box((1.05,.48,1.55),center=(.55,.49,2.365),color=cream))
add('cabinet left side',box((.035,.50,1.59),center=(.015,.48,2.365),color=(.84,.81,.71)))
add('cabinet underside',box((1.09,.50,.045),center=(.55,.48,1.585),color=(.73,.71,.61)))

# Raised frame and inset center panel on the cupboard door.
front=.232
add('door inset',box((.96,.032,1.44),center=(.57,front,2.37),color=(.80,.77,.66)))
for x in (.075,1.065):
    add('door stile '+str(x),box((.062,.052,1.52),center=(x,front-.022,2.37),color=(.86,.82,.71)))
for z in (1.64,3.10):
    add('door rail '+str(z),box((1.04,.052,.075),center=(.57,front-.022,z),color=(.86,.82,.71)))
for x in (.13,1.01):
    add('panel molding '+str(x),box((.018,.018,1.34),center=(x,.199,2.37),color=(.73,.70,.59)))
for z in (1.71,3.03):
    add('panel molding '+str(z),box((.88,.018,.019),center=(.57,.199,z),color=(.73,.70,.59)))
add('cabinet knob stem',rod(.016,start=(1.012,.18,1.92),end=(1.012,.125,1.92),color=metal))
add('cabinet knob',ball(.027,center=(1.012,.117,1.92),color=(.48,.46,.34)))

# Window and closely spaced horizontal Venetian blinds.
add('window recess',box((1.60,.035,2.65),center=(-.86,.713,1.97),color=(.34,.46,.46)))
add('window glass',box((1.49,.018,2.52),center=(-.86,.682,1.97),color=(.64,.78,.80)))
for x in (-1.64,-.085):
    add('window upright '+str(x),box((.065,.11,2.68),center=(x,.64,1.97),color=ivory))
for z in (.65,3.29,1.89):
    add('window crosspiece '+str(z),box((1.59,.10,.065),center=(-.86,.63,z),color=ivory))
for x in (-1.17,-.59):
    add('glass muntin '+str(x),box((.026,.035,2.6),center=(x,.64,1.97),color=(.86,.87,.80)))
# Soft patches of foliage visible through the narrow blind gaps.
for i in range(65):
    x=random.uniform(-1.6,-.13)
    z=random.uniform(.8,3.25)
    add('outside foliage %02d'%i,ball(random.uniform(.018,.065),center=(x,.661,z),color=random.choice([(.36,.48,.40),(.48,.61,.54),(.73,.79,.73)])))
for i in range(43):
    z=.73+i*.059
    slat=box((1.53,.105,.014),center=(-.86,.566,z),color=(.86,.87,.79))
    slat.turn('x',-14)
    add('blind slat %02d'%i,slat)
for x in (-1.32,-.37):
    add('blind ladder '+str(x),box((.013,.012,2.52),center=(x,.499,1.98),color=(.75,.75,.66)))
tube('blind cord',[(-.22,.47,2.94),(-.22,.47,1.96),(-.215,.47,1.82)],.004,(.83,.80,.67))
add('cord pull',rod(.012,length=.055,center=(-.215,.47,1.81),color=(.83,.79,.63)))
add('window sill',box((1.67,.22,.045),center=(-.86,.59,.665),color=ivory))

# Door-mounted vertical paper towel dispenser.
add('paper holder top mounting',rod(.043,start=(.56,.192,2.64),end=(.56,.105,2.64),color=metal))
add('paper spindle finial',ball(.033,center=(.56,.095,2.66),color=(.43,.43,.36)))
add('paper holder lower bracket',rod(.025,start=(.56,.19,1.91),end=(.56,.065,1.91),color=(.27,.28,.24)))
add('paper bottom spindle',rod(.027,length=.09,center=(.56,.052,1.94),color=(.24,.25,.22)))
add('paper towel roll',rod(.156,length=.647,center=(.56,.036,2.285),color=(.94,.92,.84)))
add('paper roll top',rod(.153,length=.006,center=(.56,.036,2.611),color=(.91,.88,.78)))
add('paper inner core',rod(.021,length=.008,center=(.56,.036,2.616),color=(.46,.39,.28)))
# A loose outer edge down the right-hand side.
add('paper loose edge',box((.022,.017,.618),center=(.698,-.047,2.28),color=(.96,.94,.86)))

# Towel ring fixed to the cabinet's visible left side.
add('towel mounting disk',rod(.052,start=(-.009,.395,1.975),end=(-.037,.395,1.975),color=metal))
add('towel mounting center',rod(.032,start=(-.035,.395,1.975),end=(-.105,.395,1.975),color=(.58,.57,.47)))
ring=[]
for i in range(81):
    a=2*math.pi*i/80
    ring.append((-.113,.333+.139*math.sin(a),1.811+.167*math.cos(a)))
tube('oval towel ring',ring,.009,(.62,.64,.60))
add('ring hinge',ball(.019,center=(-.113,.333,1.978),color=metal))

# Sink cutout is represented by a dark basin and bright steel lip.
add('sink rim',fillet_box((.72,.59,.023),radius=.075,center=(-.78,-.16,.932),color=(.42,.43,.37)))
add('sink black interior',fillet_box((.64,.51,.022),radius=.075,center=(-.78,-.16,.946),color=(.055,.063,.054)))
add('sink bowl bottom',fillet_box((.47,.37,.018),radius=.06,center=(-.78,-.16,.948),color=(.09,.105,.09)))
tube('sink inner highlight',[(-1.08,-.37,.951),(-1.08,.045,.951),(-.98,.085,.951),(-.53,.085,.951)],.008,(.46,.48,.42))
add('faucet foot',rod(.049,length=.025,center=(-.69,.204,.95),color=metal))
tube('faucet', [(-.69,.204,.951),(-.69,.204,1.22),(-.69,.199,1.30),(-.69,.176,1.337),(-.69,.126,1.346),(-.69,.09,1.317),(-.69,.09,1.275)],.015,(.61,.63,.59))
add('tap base',rod(.034,length=.03,center=(-.86,.18,.96),color=metal))
tube('tap lever',[(-.86,.18,.97),(-.87,.18,1.03),(-.91,.18,1.08)],.013,metal)
add('small drain cap',rod(.045,length=.018,center=(-.45,.28,.94),color=(.19,.19,.15)))

# Blender, tucked behind the jug.
add('blender base',fillet_box((.22,.23,.26),radius=.045,center=(.255,.39,1.055),color=(.035,.041,.038)))
add('blender base upper',rod(.105,length=.038,center=(.255,.39,1.202),color=(.035,.039,.035)))
add('blender control',ball(.021,center=(.255,.267,1.075),color=(.25,.27,.22)))
add('blender cup',rod(.067,start=(.255,.39,1.21),end=(.205,.39,1.55),color=(.65,.68,.61),))
add('blender cup rim',rod(.071,length=.012,center=(.205,.39,1.55),color=(.65,.66,.59)))
add('blender cup dark core',rod(.043,start=(.255,.39,1.22),end=(.213,.39,1.49),color=(.29,.33,.29)))

# Small objects beside the towel.
add('green cylindrical can',rod(.047,length=.23,center=(-.022,.368,1.045),color=(.32,.37,.23)))
add('can lid',rod(.049,length=.012,center=(-.022,.368,1.163),color=(.56,.57,.44)))
add('small silver container',rod(.027,length=.22,center=(.032,.245,1.035),color=(.58,.60,.51)))

# Brita-style dark blue water-filter pitcher.
add('blue filter pitcher',fillet_box((.29,.235,.41),radius=.067,center=(.88,.405,1.14),color=(.055,.105,.22)))
add('pitcher water side',fillet_box((.023,.19,.31),radius=.01,center=(1.02,.395,1.12),color=(.30,.36,.40)))
add('pitcher lid',fillet_box((.32,.265,.048),radius=.045,center=(.88,.395,1.361),color=(.43,.46,.43)))
add('pitcher sloping spout',box((.085,.13,.045),center=(.747,.34,1.35),color=(.43,.45,.41)))
tube('pitcher handle',[(1.012,.42,1.32),(1.105,.42,1.28),(1.145,.42,1.18),(1.145,.42,1.06),(1.09,.42,1.00),(1.01,.42,1.02)],.028,(.46,.49,.46))

# Translucent gallon jug with a narrow shoulder and short capped neck.
jugx,jugy=.58,.035
levels=[(.928,.100,.090),(.947,.133,.108),(1.00,.147,.117),(1.14,.142,.114),
        (1.225,.121,.10),(1.29,.078,.066),(1.315,.047,.045)]
# Rings joined after realization form a softly squared bottle.
add('jug cap',rod(.035,length=.032,center=(jugx,jugy,1.354),color=(.82,.83,.76)))
add('jug neck',rod(.037,length=.043,center=(jugx,jugy,1.32),color=(.74,.77,.70)))

realize(scene)

# Distinct materials for the finely patterned stone, paper, metal, and cloth.
def material(name,color,rough=.6):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m

stone=material('warm densely speckled granite',(.38,.36,.30),.76)
nt=stone.node_tree
p=nt.nodes.get('Principled BSDF')
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=185
noise.inputs['Detail'].default_value=3
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.23
ramp.color_ramp.elements[0].color=(.10,.105,.085,1)
ramp.color_ramp.elements[1].position=.77
ramp.color_ramp.elements[1].color=(.66,.61,.49,1)
el=ramp.color_ramp.elements.new(.48);el.color=(.32,.30,.25,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.20
bump.inputs['Distance'].default_value=.001
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],p.inputs['Normal'])

for ob in bpy.context.scene.objects:
    if ob.type!='MESH': continue
    if 'counter slab' in ob.name or 'backsplash' in ob.name:
        ob.data.materials.clear();ob.data.materials.append(stone)
    if any(s in ob.name for s in ['faucet','tap ','ring','mounting','knob','spindle','handle','sink rim']):
        for m in ob.data.materials:
            if m and m.use_nodes:
                q=m.node_tree.nodes.get('Principled BSDF')
                if q:
                    q.inputs['Metallic'].default_value=.72
                    q.inputs['Roughness'].default_value=.25

def mesh_object(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for poly in mesh.polygons: poly.use_smooth=True
    return ob

jugmat=material('milky white polyethylene',(.71,.75,.69),.36)
jugmat.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.075
verts=[];faces=[]
N=64
for z,rx,ry in levels:
    for i in range(N):
        a=2*math.pi*i/N
        c,s=math.cos(a),math.sin(a)
        verts.append((jugx+rx*math.copysign(abs(c)**.68,c),jugy+ry*math.copysign(abs(s)**.68,s),z))
for j in range(len(levels)-1):
    for i in range(N):
        faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(range(N-1,-1,-1)))
faces.append(tuple((len(levels)-1)*N+i for i in range(N)))
ob=mesh_object('rounded gallon water jug',verts,faces,jugmat)
bevel=ob.modifiers.new('gentle bottle molding','BEVEL');bevel.width=.012;bevel.segments=3

# Hanging cotton towel, with multiple long folds and an uneven doubled hem.
cloth=material('warm white terry cotton',(.84,.82,.73),.95)
nt=cloth.node_tree
q=nt.nodes.get('Principled BSDF')
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=250
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=.0015
nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],q.inputs['Normal'])
for layer in range(2):
    verts=[];faces=[]
    U,V=32,48
    for j in range(V+1):
        t=j/V
        width=.095+.095*math.sin(min(1,t*2)*math.pi/2)
        for i in range(U+1):
            u=i/U
            y=.329+(u-.5)*2*width
            z=1.665-.655*t+.025*math.sin(u*7+layer)*t**6
            x=-.136-.033*math.sin(u*math.pi*7+.6)*(.3+.7*t)-.018*t-layer*.025
            z-=.03*math.sin(u*math.pi)*math.sin(t*math.pi)
            verts.append((x,y,z+layer*.065))
    for j in range(V):
        for i in range(U):
            a=j*(U+1)+i
            faces.append((a,a+1,a+U+2,a+U+1))
    ob=mesh_object('draped hand towel '+str(layer),verts,faces,cloth)
    sol=ob.modifiers.new('cotton thickness','SOLIDIFY');sol.thickness=.003
    sub=ob.modifiers.new('soft folds','SUBSURF');sub.levels=1

# Small hand-written label on the front of the gallon jug.
ink=material('faded jug marker',(.28,.33,.28),.85)
curve=bpy.data.curves.new('FILTER hand lettering','FONT')
curve.body='FILTER'
curve.align_x='CENTER'
curve.size=.032
curve.space_character=1.15
curve.extrude=.0002
label=bpy.data.objects.new('FILTER',curve)
bpy.context.collection.objects.link(label)
label.location=(jugx-.012,jugy-.119,1.025)
label.rotation_euler=(math.pi/2,0,-.06)
label.data.materials.append(ink)

# Fine paper texture.
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and 'paper towel roll' in ob.name:
        mat=material('embossed paper',(.94,.92,.84),.93)
        nt=mat.node_tree
        n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=125;n.inputs['Detail'].default_value=2
        b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.001
        nt.links.new(n.outputs['Fac'],b.inputs['Height'])
        nt.links.new(b.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
        ob.data.materials.clear();ob.data.materials.append(mat)

set_view(position=(-1.74,-2.90,2.18),target=(.16,.32,1.83),lens=79,sensor=36)
area_emitter(position=(-1.65,.08,2.55),power=190,size=1.65,target=(.40,.25,1.55),color=(.83,.91,1))
area_emitter(position=(-.25,-1.60,2.75),power=100,size=2.1,target=(.35,.38,1.65),color=(1,.86,.67))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.57,.52,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.32
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.1
