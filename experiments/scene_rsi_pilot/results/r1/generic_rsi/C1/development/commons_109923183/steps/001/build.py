from sceneact import *
import bpy, math, random
from mathutils import Vector

# Landmarks (normalized): head crest (.08,.25), pillow (.20,.39),
# seat foot (.82,.66), front feet (.33,.84)/(.78,.93),
# wall-floor corner at right (.93,.50). Uncertainty: depth and hidden rear legs.
# Camera looks down from the open/front side; chaise long axis is world X.
CAMERA = (2.65, -6.3, 4.0)
TARGET = (0.0, 0.0, 1.00)
LENS = 48
LENGTH, WIDTH, SEAT_Z = 2.35, .90, .79
LIGHT_POWER = 650
random.seed(7)

scene = Scene('Salon')
cream = (.72,.69,.59)
wall = (.75,.73,.66)
sage = (.28,.35,.29)
gold = (.62,.56,.40)
trim = (.76,.71,.57)
fabric = (.81,.76,.65)

def add(parent, name, node):
    parent.include(name, node)

def tube(parent, name, points, radius=.018, color=sage):
    add(parent, name, sweep_tube(points=points, radius=radius, color=color))

def bezier(points, steps=25):
    a,b,c,d = [Vector(p) for p in points]
    return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d)
            for t in [i/steps for i in range(steps+1)]]

architecture = Asset('Paneled room')
add(architecture,'floor',box((12,12,.12),center=(0,0,-.065),color=(.22,.115,.066)))
add(architecture,'back wall',box((8,.15,4),center=(0,1.10,2),color=wall))
# Raised molding on the wall, including the large inset panels.
for i,z in enumerate((.10,.18,.31,1.64,1.72,1.94,2.03,2.48)):
    add(architecture,f'horizontal molding {i}',
        box((7,.045,.025 if i not in (1,4) else .055),center=(0,1.002,z),color=cream))
for i,(x0,x1) in enumerate(((-2.65,-1.35),(-1.31,.32),(.36,2.00))):
    for k,inset in enumerate((0,.035)):
        xa,xb=x0+inset,x1-inset
        za,zb=.39+inset,1.55-inset
        for j,x in enumerate((xa,xb)):
            add(architecture,f'panel {i} {k} upright {j}',
                box((.017,.025,zb-za),center=(x,.998,(za+zb)/2),color=cream))
        for j,z in enumerate((za,zb)):
            add(architecture,f'panel {i} {k} horizontal {j}',
                box((xb-xa,.025,.018),center=((xa+xb)/2,.998,z),color=cream))
for x in (-1.33,.34,2.13):
    add(architecture,f'wall seam {x}',box((.008,.012,2.6),center=(x,1.013,1.35),color=(.44,.43,.37)))
add(architecture,'right projecting pier',box((.27,.34,3.4),center=(2.36,.97,1.7),color=(.78,.78,.72)))
for z in (.17,1.7,1.78):
    add(architecture,f'pier trim {z}',box((.32,.39,.04),center=(2.36,.95,z),color=cream))
scene.include('Architecture',architecture)

# Broad parquet boards, staggered and diagonal, with restrained color variation.
parquet=Asset('Parquet')
for j in range(-12,13):
    for i in range(-7,8):
        u=i*.65+(j%2)*.325
        v=j*.145
        x=.707*u-.707*v
        y=.707*u+.707*v
        if -4<x<4 and -4<y<1.1:
            c=random.uniform(.78,1.12)
            p=box((.644,.140,.014),center=(x,y,.004),
                  color=(.255*c,.145*c,.088*c))
            p.turn('z',45)
            add(parquet,f'board {i} {j}',p)
scene.include('Parquet',parquet)

chaise=Asset('Antique chaise longue')
# Frame rails follow the upholstered seat and rounded foot.
front_rail=[(-1.02,-.48,.65),(-.83,-.49,.59),(-.50,-.49,.57),
            (-.15,-.49,.55),(.18,-.49,.52),(.48,-.49,.55),
            (.88,-.47,.56),(1.15,-.40,.58)]
tube(chaise,'front carved apron',front_rail,.052,sage)
tube(chaise,'apron upper gold edge',[(x,y-.018,z+.043) for x,y,z in front_rail],.012,trim)
tube(chaise,'apron lower gold edge',[(x,y-.025,z-.037) for x,y,z in front_rail],.010,trim)
tube(chaise,'rear rail',[(-1,.43,.61),(.8,.43,.59),(1.15,.34,.59)],.04,sage)
foot_arc=[(1.03+.19*math.cos(t),.40*math.sin(t),.61)
          for t in [(-math.pi/2)+i*math.pi/30 for i in range(31)]]
tube(chaise,'rounded foot frame',foot_arc,.045,sage)
tube(chaise,'rounded foot gilding',[(x+.018,y,z+.034) for x,y,z in foot_arc],.011,trim)

# Cabriole legs, each modeled as a curved structural member.
for label,x,y in [('head front',-.85,-.43),('foot front',1.08,-.37),
                  ('head rear',-.88,.36),('foot rear',1.06,.34)]:
    s=1 if x>0 else -1
    pts=bezier([(x,y,.62),(x+s*.15,y,.42),
                (x-s*.08,y-.015,.20),(x+s*.015,y-.035,.065)])
    tube(chaise,label+' leg',pts,.037,sage)
    tube(chaise,label+' leg highlight',[(a,b-.030,c) for a,b,c in pts],.009,trim)
    add(chaise,label+' foot',ball(.045,center=pts[-1],color=sage))

# Backrest frame runs across the head of the chaise.
back_outline=[(-1.09,-.43,.77),(-1.22,-.48,1.20),(-1.29,-.42,1.56),
              (-1.29,-.28,1.68),(-1.30,.00,1.70),(-1.25,.28,1.63),
              (-1.17,.43,1.47),(-1.04,.45,.83)]
tube(chaise,'head carved surround',back_outline,.037,sage)
tube(chaise,'head gilded outside',[(x+.020,y-.008,z+.012) for x,y,z in back_outline],.011,trim)

# High near-side upholstered arm: tall at the head, falling toward the seat.
arm_top=bezier([(-1.23,-.48,1.43),(-1.10,-.54,1.21),
                (-.85,-.54,1.17),(-.59,-.49,1.14)])
arm_return=bezier([(-.59,-.49,1.14),(-.70,-.51,.99),
                   (-.64,-.51,.77),(-.49,-.49,.70)])
arm_bottom=[(-.49,-.49,.70),(-.83,-.51,.69),(-1.04,-.50,.78),(-1.23,-.48,1.43)]
arm_outline=arm_top+arm_return[1:]+arm_bottom[1:]
tube(chaise,'near arm wood',arm_outline,.031,sage)
tube(chaise,'near arm gold',[(x,y-.026,z) for x,y,z in arm_outline],.010,trim)
far_top=bezier([(-1.22,.43,1.51),(-1.05,.45,1.26),
                (-.77,.46,1.24),(-.55,.43,1.28)])
tube(chaise,'far arm crest',far_top,.032,sage)
tube(chaise,'far arm gold',[(x,y-.015,z+.023) for x,y,z in far_top],.010,trim)
tube(chaise,'far arm curved support',bezier([far_top[-1],(-.62,.43,1.13),
                  (-.55,.43,.98),(-.43,.43,.87)]),.027,sage)

# Economical carved flowers and curved leaves on the central apron.
for i in range(7):
    ang=i*2*math.pi/7
    add(chaise,f'apron flower petal {i}',ball(.025,
        center=(.19+.055*math.cos(ang),-.548,.535+.037*math.sin(ang)),color=trim))
add(chaise,'apron flower center',ball(.025,center=(.19,-.567,.535),color=gold))
for side in (-1,1):
    for j in range(2):
        pts=[(.19+side*(.04+t*.19),-.538,.53+.025*math.sin(t*math.pi*2+j))
             for t in [i/18 for i in range(19)]]
        tube(chaise,f'apron scroll {side} {j}',pts,.009,trim)
scene.include('Chaise',chaise)

# The foreground cropped cane chair is a separate assembly.
chair=Asset('Foreground cane chair')
chair_center=(-1.55,-1.56,.46)
for k in range(2):
    pts=[(chair_center[0]+(.43+k*.026)*math.cos(t),
          chair_center[1]+(.40+k*.026)*math.sin(t),.46+k*.012)
         for t in [i*2*math.pi/64 for i in range(65)]]
    tube(chair,f'seat rim {k}',pts,.028,sage if k==0 else gold)
for j in range(-8,9):
    d=j*.042
    extent=math.sqrt(max(.001,.36*.36-d*d))
    tube(chair,f'cane horizontal {j}',[(-1.55-extent,-1.56+d,.466),
              (-1.55+extent,-1.56+d,.466)],.0045,(.48,.32,.17))
    tube(chair,f'cane vertical {j}',[(-1.55+d,-1.56-extent,.47),
              (-1.55+d,-1.56+extent,.47)],.0045,(.55,.39,.22))
scene.include('Cane chair',chair)

# Curtains at the left edge: broad pale vertical folds beside the daylight.
curtains=Asset('Window curtains')
for i in range(11):
    x=-2.02+i*.033
    add(curtains,f'curtain fold {i}',rod(.045,length=2.85,
        center=(x,.55+.055*math.sin(i*1.5),1.50),
        color=(.84+.035*(i%2),.82+.035*(i%2),.74+.04*(i%2))))
scene.include('Curtains',curtains)

realize(scene)

# Mesh upholstery is kept as separate, named components.
def mat(name,color,roughness=.75):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return m

upholstery=mat('Ivory woven upholstery with fine rose stripes',fabric)
nt=upholstery.node_tree
nodes,links=nt.nodes,nt.links
tex=nodes.new('ShaderNodeTexCoord')
sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(tex.outputs['Generated'],sep.inputs[0])
wave=nodes.new('ShaderNodeMath');wave.operation='MULTIPLY'
wave.inputs[1].default_value=110
links.new(sep.outputs['Y'],wave.inputs[0])
sine=nodes.new('ShaderNodeMath');sine.operation='SINE'
links.new(wave.outputs[0],sine.inputs[0])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for pos,col in [(0,(.76,.70,.61,1)),(.79,(.86,.80,.70,1)),
                (.89,(.65,.40,.37,1)),(.95,(.84,.77,.66,1))]:
    e=ramp.color_ramp.elements[0] if pos==0 else ramp.color_ramp.elements.new(pos)
    e.position=pos;e.color=col
links.new(sine.outputs[0],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=160
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15
bump.inputs['Distance'].default_value=.009
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],nodes.get('Principled BSDF').inputs['Normal'])
pillowmat=mat('Warm cream damask pillow',(.82,.75,.61))
pn=pillowmat.node_tree.nodes;pl=pillowmat.node_tree.links
n=pn.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=65
b=pn.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22
b.inputs['Distance'].default_value=.012
pl.new(n.outputs['Fac'],b.inputs['Height'])
pl.new(b.outputs[0],pn.get('Principled BSDF').inputs['Normal'])

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
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    obj.location=center;obj.rotation_euler=rotation;obj.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    return obj

cushion('Long upholstered seat',(.12,0,SEAT_Z),(1.12,.445,.145),upholstery,.33,.55)
cushion('Padded head back',(-1.18,0,1.28),(.09,.425,.36),upholstery,.44,.52,
        (0,math.radians(-12),0))
cushion('Far padded arm',(-.87,.415,1.085),(.31,.055,.17),upholstery,.5,.55)

def polygon_panel(name,points,material):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(points,[],[tuple(range(len(points)))])
    mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    sol=o.modifiers.new('Padded panel thickness','SOLIDIFY');sol.thickness=.042
    bev=o.modifiers.new('Soft upholstery border','BEVEL');bev.width=.025;bev.segments=3
    return o
polygon_panel('Near upholstered side panel',[(x,y+.017,z) for x,y,z in arm_outline[:-1]],upholstery)

# Loose pillow, leaning into the high head, with pointed soft corners.
cushion('Large loose cream pillow',(-.91,-.035,1.285),(.155,.325,.33),
        pillowmat,.35,.36,(math.radians(-8),math.radians(-19),math.radians(-5)))

# Small green museum label on the foot end of the upholstery.
labelmat=mat('Dark teal label',(.055,.22,.18))
label=bpy.data.objects.new('Small green seat label',bpy.data.meshes.new('Label mesh'))
bpy.context.collection.objects.link(label)
label.data.from_pydata([(.65,.085,.939),(.73,.085,.939),(.73,.245,.939),(.65,.245,.939)],
                       [],[(0,1,2,3)])
label.data.materials.append(labelmat)
ink=mat('Label pale print',(.65,.75,.66))
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.69,.13+i*.025,.941))
    o=bpy.context.object;o.name='Small label printing'
    o.dimensions=(.033 if i!=1 else .021,.004,.001)
    o.data.materials.append(ink)

# All geometry above uses finite positive radii and valid nonrepeated tube points.
# Soft daylight from the cropped window at image left.
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.77,.83,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3.5,-.5,3.5),power=LIGHT_POWER,size=3.0,target=(0,0,.7),color=(1,.94,.83))
area_emitter((1,-3,3.7),power=110,size=3.5,target=(0,0,.8),color=(1,.96,.9))
sc.view_settings.view_transform='AgX'
