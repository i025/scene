from sceneact import *
import bpy, math, random
from mathutils import Vector, Matrix

# Three largest discrepancies in step 1:
# 1. Chaise occupies only ~49% image width versus ~79%: move camera closer,
#    retain 48mm lens. Target crest (.07,.25), foot (.82,.73), feet (.32,.85)/(.78,.93).
# 2. Wall moldings slope down right and floor boundary is too low:
#    face wall more directly; move wall back .65m and lower panel molding heights.
#    Rotate chaise independently to preserve its useful oblique silhouette.
# 3. Floor and furniture are too pale, and foreground chair is fully visible:
#    darken parquet, reduce ambient/fill, move cane chair toward bottom-left crop.
# Uncertain: hidden head geometry, wall distance, pillow orientation.
CAMERA = (.30, -4.0, 3.20)
TARGET = (-.15, .05, .96)
LENS = 48
CHAISE_ROTATION = -12
WALL_Y = 1.75
SEAT_Z = .79
KEY_POWER = 420
random.seed(7)

scene = Scene('Salon')
wall = (.65,.62,.54)
cream = (.69,.66,.57)
sage = (.22,.29,.24)
gold = (.49,.43,.30)
trim = (.66,.60,.46)
fabric = (.78,.71,.61)

def add(parent, name, node):
    parent.include(name, node)

def tube(parent, name, points, radius=.018, color=sage):
    add(parent, name, sweep_tube(points=points, radius=radius, color=color))

def bezier(points, steps=20):
    a,b,c,d = [Vector(p) for p in points]
    return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
            for t in [i/steps for i in range(steps+1)]]

architecture = Asset('Paneled room')
add(architecture,'floor',box((12,12,.12),center=(0,0,-.065),color=(.12,.057,.032)))
add(architecture,'wall',box((9,.15,4),center=(0,WALL_Y,2),color=wall))
fy = WALL_Y-.10
for i,z in enumerate((.10,.18,.31,1.64,1.72,1.94,2.03,2.48)):
    z *= .75
    add(architecture,f'horizontal molding {i}',
        box((8,.044,.025 if i not in (1,4) else .046),
            center=(0,fy,z),color=cream))
for i,(x0,x1) in enumerate(((-2.8,-.85),(-.81,1.42))):
    for k,inset in enumerate((0,.035)):
        xa,xb=x0+inset,x1-inset
        za,zb=.26+inset,1.16-inset
        for j,x in enumerate((xa,xb)):
            add(architecture,f'panel {i} {k} upright {j}',
                box((.017,.025,zb-za),center=(x,fy-.012,(za+zb)/2),color=cream))
        for j,z in enumerate((za,zb)):
            add(architecture,f'panel {i} {k} horizontal {j}',
                box((xb-xa,.025,.018),center=((xa+xb)/2,fy-.012,z),color=cream))
for x in (-.82,.38):
    add(architecture,f'seam {x}',box((.007,.01,3),
        center=(x,WALL_Y-.078,1.5),color=(.35,.33,.28)))
add(architecture,'right pier',box((.26,.36,3.4),
    center=(1.88,WALL_Y-.04,1.7),color=(.73,.73,.66)))
for i,z in enumerate((.13,1.28,1.34)):
    add(architecture,f'pier trim {i}',box((.31,.4,.035),
        center=(1.88,WALL_Y-.06,z),color=cream))
# Small dark door fittings above the head.
for i,x in enumerate((-.79,-.72)):
    add(architecture,f'door fitting {i}',rod(.014,length=.05,
        center=(x,fy-.025,1.37),color=(.07,.065,.045)))
scene.include('Architecture',architecture)

parquet=Asset('Parquet')
for j in range(-27,24):
    for i in range(-10,11):
        u=i*.70+(j%2)*.35
        v=j*.16
        x=.707*u-.707*v
        y=.707*u+.707*v
        if -5<x<5 and -5<y<WALL_Y:
            c=random.uniform(.80,1.15)
            p=box((.696,.156,.012),center=(x,y,.001),
                  color=(.145*c,.068*c,.037*c))
            p.turn('z',45)
            add(parquet,f'board {i} {j}',p)
scene.include('Parquet',parquet)

chaise=Asset('Antique chaise longue')
front_rail=[(-1.02,-.48,.65),(-.83,-.49,.59),(-.50,-.49,.57),
            (-.15,-.49,.55),(.18,-.49,.52),(.48,-.49,.55),
            (.88,-.47,.56),(1.15,-.40,.58)]
tube(chaise,'front apron',front_rail,.049)
tube(chaise,'upper apron edge',[(x,y-.018,z+.043) for x,y,z in front_rail],.012,trim)
tube(chaise,'lower apron edge',[(x,y-.025,z-.037) for x,y,z in front_rail],.010,trim)
tube(chaise,'rear rail',[(-1,.43,.61),(.8,.43,.59),(1.15,.34,.59)],.04)
foot_arc=[(1.03+.19*math.cos(t),.40*math.sin(t),.61)
          for t in [-math.pi/2+i*math.pi/25 for i in range(26)]]
tube(chaise,'rounded foot frame',foot_arc,.043)
tube(chaise,'foot gilding',[(x+.018,y,z+.034) for x,y,z in foot_arc],.01,trim)
for label,x,y in [('head front',-.85,-.43),('foot front',1.08,-.37),
                  ('head rear',-.88,.36),('foot rear',1.06,.34)]:
    s=1 if x>0 else -1
    pts=bezier([(x,y,.62),(x+s*.15,y,.42),
                (x-s*.08,y-.015,.20),(x+s*.015,y-.035,.065)])
    tube(chaise,label+' leg',pts,.035)
    tube(chaise,label+' highlight',[(a,b-.030,c) for a,b,c in pts],.009,trim)
    add(chaise,label+' foot',ball(.041,center=pts[-1],color=sage))

back_outline=[(-1.09,-.43,.77),(-1.22,-.48,1.20),(-1.29,-.42,1.56),
              (-1.29,-.28,1.68),(-1.30,0,1.70),(-1.25,.28,1.63),
              (-1.17,.43,1.47),(-1.04,.45,.83)]
tube(chaise,'head surround',back_outline,.036)
tube(chaise,'head gold',[(x+.020,y-.008,z+.012) for x,y,z in back_outline],.011,trim)
arm_top=bezier([(-1.23,-.48,1.43),(-1.10,-.54,1.21),
                (-.85,-.54,1.17),(-.59,-.49,1.14)])
arm_return=bezier([(-.59,-.49,1.14),(-.70,-.51,.99),
                   (-.64,-.51,.77),(-.49,-.49,.70)])
arm_outline=arm_top+arm_return[1:]+[(-.83,-.51,.69),(-1.04,-.50,.78),(-1.23,-.48,1.43)]
tube(chaise,'near arm wood',arm_outline,.030)
tube(chaise,'near arm gold',[(x,y-.026,z) for x,y,z in arm_outline],.01,trim)
far_top=bezier([(-1.22,.43,1.51),(-1.05,.45,1.26),
                (-.77,.46,1.24),(-.55,.43,1.28)])
tube(chaise,'far arm crest',far_top,.031)
tube(chaise,'far arm gold',[(x,y-.015,z+.023) for x,y,z in far_top],.01,trim)
tube(chaise,'far support',bezier([far_top[-1],(-.62,.43,1.13),
                  (-.55,.43,.98),(-.43,.43,.87)]),.026)
for i in range(8):
    a=i*math.pi/4
    add(chaise,f'flower petal {i}',ball(.026,
        center=(.19+.054*math.cos(a),-.548,.535+.039*math.sin(a)),color=trim))
add(chaise,'flower center',ball(.025,center=(.19,-.567,.535),color=gold))
for side in (-1,1):
    for j in range(2):
        tube(chaise,f'scroll {side} {j}',
             [(.19+side*(.04+t*.19),-.538,.53+.025*math.sin(t*math.pi*2+j))
              for t in [i/16 for i in range(17)]],.009,trim)
scene.include('Chaise',chaise)

chair=Asset('Foreground cane chair')
cx,cy,cz=-1.45,-1.47,.46
for k in range(2):
    pts=[(cx+(.43+k*.026)*math.cos(t),cy+(.40+k*.026)*math.sin(t),cz+k*.012)
         for t in [i*2*math.pi/48 for i in range(49)]]
    tube(chair,f'rim {k}',pts,.028,sage if k==0 else gold)
for j in range(-10,11):
    d=j*.034
    extent=math.sqrt(max(.001,.36*.36-d*d))
    tube(chair,f'cane horizontal {j}',[(cx-extent,cy+d,cz+.006),
         (cx+extent,cy+d,cz+.006)],.0035,(.37,.23,.12))
    tube(chair,f'cane vertical {j}',[(cx+d,cy-extent,cz+.01),
         (cx+d,cy+extent,cz+.01)],.0035,(.43,.29,.15))
for i,(x,y) in enumerate(((cx+.32,cy-.26),(cx-.32,cy+.26))):
    tube(chair,f'chair leg {i}',[(x,y,.44),(x+.03,y,.05)],.031)
scene.include('Cane chair',chair)

curtains=Asset('Window curtains')
for i in range(13):
    x=-1.88+i*.027
    add(curtains,f'fold {i}',rod(.042,length=3.0,
        center=(x,.92+.05*math.sin(i*1.5),1.5),
        color=(.77+.035*(i%2),.74+.035*(i%2),.65+.04*(i%2))))
scene.include('Curtains',curtains)
realize(scene)

def mat(name,color,roughness=.75):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return m

upholstery=mat('Ivory rose striped weave',fabric)
nt=upholstery.node_tree
nodes,links=nt.nodes,nt.links
tex=nodes.new('ShaderNodeTexCoord')
sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(tex.outputs['Generated'],sep.inputs[0])
mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=145
links.new(sep.outputs['Y'],mul.inputs[0])
sine=nodes.new('ShaderNodeMath');sine.operation='SINE'
links.new(mul.outputs[0],sine.inputs[0])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.80
ramp.color_ramp.elements[0].color=(.81,.74,.64,1)
ramp.color_ramp.elements[1].position=.94
ramp.color_ramp.elements[1].color=(.57,.32,.30,1)
links.new(sine.outputs[0],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=170
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13
bump.inputs['Distance'].default_value=.005
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],nodes.get('Principled BSDF').inputs['Normal'])
pillowmat=mat('Warm damask pillow',(.78,.68,.51))
pn=pillowmat.node_tree.nodes;pl=pillowmat.node_tree.links
n=pn.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=65
b=pn.new('ShaderNodeBump');b.inputs['Strength'].default_value=.20
b.inputs['Distance'].default_value=.008
pl.new(n.outputs['Fac'],b.inputs['Height'])
pl.new(b.outputs[0],pn.get('Principled BSDF').inputs['Normal'])

furniture_extra=[]
def spow(v,e):
    return math.copysign(abs(v)**e,v)

def cushion(name,center,scale,material,ex=.34,ez=.55,rotation=(0,0,0)):
    verts=[];faces=[]
    nu,nv=64,28
    for j in range(nv+1):
        p=-math.pi/2+math.pi*j/nv
        for i in range(nu):
            t=2*math.pi*i/nu
            verts.append((scale[0]*spow(math.cos(p),ez)*spow(math.cos(t),ex),
                          scale[1]*spow(math.cos(p),ez)*spow(math.sin(t),ex),
                          scale[2]*spow(math.sin(p),ez)))
    for j in range(nv):
        for i in range(nu):
            a=j*nu+i;b=j*nu+(i+1)%nu
            faces.append((a,b,b+nu,a+nu))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    obj.location=center;obj.rotation_euler=rotation;obj.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    furniture_extra.append(obj)
    return obj

cushion('Long upholstered seat',(.12,0,SEAT_Z),(1.12,.47,.145),upholstery,.33,.55)
cushion('Padded head back',(-1.18,0,1.28),(.09,.425,.36),upholstery,.44,.52,
        (0,math.radians(-12),0))
cushion('Far padded arm',(-.87,.415,1.085),(.31,.055,.17),upholstery,.5,.55)

# Use a triangulated, slightly padded side panel for reliable concave silhouette.
points=[(x,y+.017,z) for x,y,z in arm_outline[:-1]]
mesh=bpy.data.meshes.new('Near side upholstery')
mesh.from_pydata(points,[],[tuple(range(len(points)))]);mesh.update()
o=bpy.data.objects.new('Near upholstered side panel',mesh)
bpy.context.collection.objects.link(o);o.data.materials.append(upholstery)
sol=o.modifiers.new('Padding','SOLIDIFY');sol.thickness=.045
bev=o.modifiers.new('Soft border','BEVEL');bev.width=.018;bev.segments=3
furniture_extra.append(o)

# Wider pillow front, turned toward the open room.
cushion('Loose cream pillow',(-.91,-.055,1.30),(.16,.34,.34),
        pillowmat,.32,.36,
        (math.radians(-9),math.radians(-18),math.radians(-32)))

labelmat=mat('Dark teal museum label',(.035,.16,.125))
mesh=bpy.data.meshes.new('Label')
mesh.from_pydata([(.65,.085,.939),(.73,.085,.939),(.73,.245,.939),(.65,.245,.939)],
                 [],[(0,1,2,3)])
label=bpy.data.objects.new('Green seat label',mesh)
bpy.context.collection.objects.link(label);label.data.materials.append(labelmat)
furniture_extra.append(label)
ink=mat('Label print',(.65,.72,.59))
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.69,.13+i*.025,.941))
    o=bpy.context.object;o.name=f'Label printing {i}'
    o.dimensions=(.033 if i!=1 else .021,.004,.001)
    o.data.materials.append(ink);furniture_extra.append(o)

# Rotate the intact furniture assembly, leaving the wall aligned to the camera.
bpy.context.view_layer.update()
rot=Matrix.Rotation(math.radians(CHAISE_ROTATION),4,'Z')
root=bpy.data.objects.get('Chaise')
if root is not None:
    root.matrix_world=rot @ root.matrix_world
for o in furniture_extra:
    o.matrix_world=rot @ o.matrix_world
# Parent upholstery to its semantic furniture group after placement.
bpy.context.view_layer.update()
if root is not None:
    for o in furniture_extra:
        mw=o.matrix_world.copy()
        o.parent=root
        o.matrix_world=mw

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.67,.72,.80,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.19
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3.3,-.3,3.7),power=KEY_POWER,size=2.8,
             target=(0,0,.7),color=(1,.94,.83))
area_emitter((1,-3,3.7),power=45,size=3.5,target=(0,0,.8),color=(1,.96,.9))
sc.view_settings.view_transform='AgX'
# Audit: positive primitive dimensions/radii; unique component keys;
# valid fillet-free geometry, distinct consecutive tube points.
# No render or save: the runner manages both.
