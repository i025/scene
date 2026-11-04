from sceneact import *
import bpy, math, random
from mathutils import Vector, Matrix

# Step 2 discrepancies:
# 1. Chaise is ~35px too far right; translate its complete assembly X=-.23,
#    shorten only its foot end slightly. Keep camera lens and distance fixed.
# 2. Head is too high, apron too open and tubular, pillow too rigid:
#    lower head crest .12m, fill the apron, soften pillow and turn its face forward.
# 3. Floor is too bright, upholstery stripes too strong, wall slopes down right:
#    darken parquet, narrow/fade stripes, rotate room +9 degrees independently.
# Reference landmarks: crest (.05,.25), foot (.82,.73), feet (.32,.85)/(.78,.93).
# Uncertainty remains in hidden supports and headrest depth.
CAMERA=(.30,-4.0,3.20)
TARGET=(-.15,.05,.96)
LENS=48
WALL_Y=1.75
CHAISE_ANGLE=-12
CHAISE_OFFSET=(-.23,0,0)
KEY_POWER=330
random.seed(7)
scene=Scene('Salon')
wall=(.64,.60,.51)
cream=(.70,.66,.57)
sage=(.20,.265,.215)
gold=(.46,.39,.27)
trim=(.63,.56,.43)

def add(parent,name,node):
    parent.include(name,node)

def tube(parent,name,points,radius=.018,color=sage):
    clean=[]
    for p in points:
        p=tuple(p)
        if not clean or sum((a-b)**2 for a,b in zip(p,clean[-1]))>1e-12:
            clean.append(p)
    if len(clean)>1:
        add(parent,name,sweep_tube(points=clean,radius=radius,color=color))

def bezier(points,steps=20):
    a,b,c,d=[Vector(p) for p in points]
    return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
            for t in [i/steps for i in range(steps+1)]]

architecture=Asset('Paneled room')
add(architecture,'wall',box((9,.15,4),center=(0,WALL_Y,2),color=wall))
fy=WALL_Y-.10
for i,z in enumerate((.075,.135,.2325,1.23,1.29,1.455,1.5225,1.86)):
    add(architecture,f'molding {i}',box((8,.044,.025 if i not in (1,4) else .046),
         center=(0,fy,z),color=cream))
for i,(x0,x1) in enumerate(((-2.8,-.85),(-.81,1.42))):
    for k,inset in enumerate((0,.035)):
        xa,xb=x0+inset,x1-inset
        za,zb=.26+inset,1.16-inset
        for j,x in enumerate((xa,xb)):
            add(architecture,f'panel {i} {k} vertical {j}',
                box((.017,.025,zb-za),center=(x,fy-.012,(za+zb)/2),color=cream))
        for j,z in enumerate((za,zb)):
            add(architecture,f'panel {i} {k} horizontal {j}',
                box((xb-xa,.025,.018),center=((xa+xb)/2,fy-.012,z),color=cream))
for x in (-.82,.38):
    add(architecture,f'seam {x}',box((.006,.01,3),center=(x,WALL_Y-.078,1.5),
                                   color=(.36,.33,.27)))
add(architecture,'right pier',box((.26,.36,3.4),center=(1.88,WALL_Y-.04,1.7),
                                color=(.72,.70,.62)))
for i,z in enumerate((.13,1.28,1.34)):
    add(architecture,f'pier trim {i}',box((.31,.4,.035),
        center=(1.88,WALL_Y-.06,z),color=cream))
for i,x in enumerate((-.79,-.72)):
    add(architecture,f'door fitting {i}',rod(.014,length=.05,
        center=(x,fy-.025,1.37),color=(.07,.065,.045)))
architecture.turn('z',9,pivot=(0,WALL_Y,0))
scene.include('Architecture',architecture)
scene.include('Floor foundation',box((12,12,.12),center=(0,0,-.065),
                                   color=(.075,.029,.017)))
parquet=Asset('Dark parquet floor')
for j in range(-27,24):
    for i in range(-10,11):
        u=i*.70+(j%2)*.35
        v=j*.16
        x=.707*u-.707*v
        y=.707*u+.707*v
        if -5<x<5 and -5<y<2.2:
            c=random.uniform(.78,1.17)
            p=box((.698,.158,.012),center=(x,y,.001),
                  color=(.080*c,.033*c,.021*c))
            p.turn('z',45)
            add(parquet,f'board {i} {j}',p)
scene.include('Parquet',parquet)

chaise=Asset('Antique chaise longue')
front_rail=[(-1.02,-.48,.65),(-.83,-.49,.59),(-.50,-.49,.57),
            (-.15,-.49,.55),(.18,-.49,.52),(.48,-.49,.55),
            (.88,-.47,.56),(1.10,-.40,.58)]
tube(chaise,'front apron structure',front_rail,.036)
tube(chaise,'upper apron edge',[(x,y-.018,z+.043) for x,y,z in front_rail],.010,trim)
tube(chaise,'lower apron edge',[(x,y-.025,z-.037) for x,y,z in front_rail],.008,trim)
tube(chaise,'rear rail',[(-1,.43,.61),(.8,.43,.59),(1.10,.34,.59)],.035)
arc=[(.98+.19*math.cos(t),.40*math.sin(t),.61)
     for t in [-math.pi/2+i*math.pi/25 for i in range(26)]]
tube(chaise,'rounded foot frame',arc,.036)
tube(chaise,'foot gilding',[(x+.014,y,z+.034) for x,y,z in arc],.009,trim)
for label,x,y in [('head front',-.85,-.43),('foot front',1.01,-.26),
                  ('head rear',-.88,.36),('foot rear',1.01,.34)]:
    s=1 if x>0 else -1
    pts=bezier([(x,y,.62),(x+s*.12,y,.42),
                (x-s*.08,y-.015,.20),(x+s*.015,y-.035,.065)])
    tube(chaise,label+' leg',pts,.033)
    tube(chaise,label+' highlight',[(a,b-.027,c) for a,b,c in pts],.007,trim)
    add(chaise,label+' foot',ball(.039,center=pts[-1],color=sage))

back_outline=[(-1.09,-.43,.77),(-1.22,-.48,1.18),(-1.29,-.42,1.46),
              (-1.29,-.28,1.56),(-1.30,0,1.58),(-1.25,.28,1.53),
              (-1.17,.43,1.40),(-1.04,.45,.83)]
tube(chaise,'head surround',back_outline,.033)
tube(chaise,'head gold',[(x+.02,y-.008,z+.012) for x,y,z in back_outline],.010,trim)
arm_top=bezier([(-1.23,-.48,1.38),(-1.10,-.54,1.21),
                (-.85,-.54,1.17),(-.59,-.49,1.14)])
arm_return=bezier([(-.59,-.49,1.14),(-.70,-.51,.99),
                   (-.64,-.51,.77),(-.49,-.49,.70)])
arm_outline=arm_top+arm_return[1:]+[(-.83,-.51,.69),(-1.04,-.50,.78),(-1.23,-.48,1.38)]
tube(chaise,'near arm wood',arm_outline,.028)
tube(chaise,'near arm gold',[(x,y-.026,z) for x,y,z in arm_outline],.009,trim)
far_top=bezier([(-1.22,.43,1.43),(-1.05,.45,1.26),
                (-.77,.46,1.24),(-.55,.43,1.28)])
tube(chaise,'far arm crest',far_top,.028)
tube(chaise,'far arm gold',[(x,y-.015,z+.023) for x,y,z in far_top],.009,trim)
tube(chaise,'far support',bezier([far_top[-1],(-.62,.43,1.13),
                                (-.55,.43,.98),(-.43,.43,.87)]),.025)
for i in range(8):
    a=i*math.pi/4
    add(chaise,f'flower petal {i}',ball(.024,
        center=(.19+.054*math.cos(a),-.548,.535+.039*math.sin(a)),color=trim))
add(chaise,'flower center',ball(.023,center=(.19,-.567,.535),color=gold))
for side in (-1,1):
    for j in range(2):
        tube(chaise,f'scroll {side} {j}',
             [(.19+side*(.04+t*.19),-.538,.53+.025*math.sin(t*math.pi*2+j))
              for t in [i/16 for i in range(17)]],.008,trim)
# Carved crest ornament, distinct from the structural back.
for i in range(7):
    y=-.13+i*.043
    add(chaise,f'crest carving {i}',ball(.023,
         center=(-1.30,y,1.59+.025*math.sin(i*math.pi/6)),color=trim))
scene.include('Chaise',chaise)

chair=Asset('Foreground cane chair')
cx,cy,cz=-1.36,-1.34,.46
for k in range(2):
    pts=[(cx+(.43+k*.026)*math.cos(t),cy+(.40+k*.026)*math.sin(t),cz+k*.012)
         for t in [i*2*math.pi/48 for i in range(49)]]
    tube(chair,f'rim {k}',pts,.028,sage if k==0 else gold)
for j in range(-10,11):
    d=j*.034
    extent=math.sqrt(max(.001,.36*.36-d*d))
    tube(chair,f'cane horizontal {j}',[(cx-extent,cy+d,cz+.006),
         (cx+extent,cy+d,cz+.006)],.0035,(.30,.18,.09))
    tube(chair,f'cane vertical {j}',[(cx+d,cy-extent,cz+.01),
         (cx+d,cy+extent,cz+.01)],.0035,(.37,.24,.12))
for i,(x,y) in enumerate(((cx+.32,cy-.26),(cx-.32,cy+.26))):
    tube(chair,f'chair leg {i}',[(x,y,.44),(x+.03,y,.05)],.031)
scene.include('Cane chair',chair)
curtains=Asset('Window curtains')
for i in range(13):
    x=-1.99+i*.027
    add(curtains,f'fold {i}',rod(.042,length=3,
        center=(x,.92+.05*math.sin(i*1.5),1.5),
        color=(.79+.035*(i%2),.76+.035*(i%2),.67+.04*(i%2))))
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

upholstery=mat('Ivory with delicate rose stripes',(.78,.71,.61))
nt=upholstery.node_tree
nodes,links=nt.nodes,nt.links
tex=nodes.new('ShaderNodeTexCoord')
sep=nodes.new('ShaderNodeSeparateXYZ')
links.new(tex.outputs['Generated'],sep.inputs[0])
mul=nodes.new('ShaderNodeMath')
mul.operation='MULTIPLY';mul.inputs[1].default_value=145
links.new(sep.outputs['Y'],mul.inputs[0])
sine=nodes.new('ShaderNodeMath');sine.operation='SINE'
links.new(mul.outputs[0],sine.inputs[0])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.95
ramp.color_ramp.elements[0].color=(.78,.71,.61,1)
ramp.color_ramp.elements[1].position=.995
ramp.color_ramp.elements[1].color=(.65,.48,.43,1)
links.new(sine.outputs[0],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=170
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.12
bump.inputs['Distance'].default_value=.004
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs[0],nodes.get('Principled BSDF').inputs['Normal'])
pillowmat=mat('Warm cream damask pillow',(.77,.65,.47))
pn=pillowmat.node_tree.nodes;pl=pillowmat.node_tree.links
n=pn.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=52
b=pn.new('ShaderNodeBump');b.inputs['Strength'].default_value=.23
b.inputs['Distance'].default_value=.009
pl.new(n.outputs['Fac'],b.inputs['Height'])
pl.new(b.outputs[0],pn.get('Principled BSDF').inputs['Normal'])
woodmat=mat('Painted sage apron',sage)
extra=[]

def spow(v,e):
    return math.copysign(abs(v)**e,v)

def cushion(name,center,scale,material,ex=.34,ez=.55,rotation=(0,0,0),loose=False):
    verts=[];faces=[]
    nu,nv=64,28
    for j in range(nv+1):
        p=-math.pi/2+math.pi*j/nv
        for i in range(nu):
            t=2*math.pi*i/nu
            x=scale[0]*spow(math.cos(p),ez)*spow(math.cos(t),ex)
            y=scale[1]*spow(math.cos(p),ez)*spow(math.sin(t),ex)
            z=scale[2]*spow(math.sin(p),ez)
            if loose:
                # Small asymmetries and surface dimples keep the loose pillow soft.
                x*=1+.055*math.sin(t*5+p*7)
                z+=.018*math.sin(t*3)*math.cos(p)**2
            verts.append((x,y,z))
    for j in range(nv):
        for i in range(nu):
            a=j*nu+i;b=j*nu+(i+1)%nu
            faces.append((a,b,b+nu,a+nu))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.location=center;obj.rotation_euler=rotation
    obj.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    extra.append(obj)
    return obj

cushion('Long upholstered seat',(.095,0,.79),(1.095,.47,.145),upholstery)
cushion('Padded head back',(-1.18,0,1.24),(.09,.425,.31),upholstery,.44,.52,
        (0,math.radians(-12),0))
cushion('Far padded arm',(-.87,.415,1.085),(.31,.055,.17),upholstery,.5,.55)

def panel(name,points,material,thickness=.035):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(points,[],[tuple(range(len(points)))]);mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    sol=obj.modifiers.new('Thickness','SOLIDIFY');sol.thickness=thickness
    bevel=obj.modifiers.new('Soft edges','BEVEL');bevel.width=.012;bevel.segments=3
    extra.append(obj)
    return obj

panel('Near upholstered side panel',[(x,y+.017,z) for x,y,z in arm_outline[:-1]],upholstery,.045)
# Continuous carved apron closes the unsupported dark slot under the cushion.
panel('Solid scalloped front apron',
      [(-.65,-.49,.692),(1.08,-.43,.692),(1.10,-.43,.57),
       (.88,-.49,.52),(.48,-.51,.51),(.25,-.51,.485),
       (.15,-.51,.48),(-.15,-.51,.51),(-.50,-.51,.53),(-.65,-.50,.57)],
      woodmat,.045)
cushion('Loose cream pillow',(-.94,-.075,1.29),(.125,.34,.31),pillowmat,.42,.46,
        (math.radians(-9),math.radians(-19),math.radians(-60)),True)

labelmat=mat('Dark teal museum label',(.035,.16,.125))
panel('Green seat label',[(.60,.085,.939),(.68,.085,.939),
                         (.68,.245,.939),(.60,.245,.939)],labelmat,.001)
ink=mat('Label print',(.65,.72,.59))
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.64,.13+i*.025,.941))
    o=bpy.context.object;o.name=f'Label printing {i}'
    o.dimensions=(.033 if i!=1 else .021,.004,.001)
    o.data.materials.append(ink);extra.append(o)

bpy.context.view_layer.update()
transform=Matrix.Translation(Vector(CHAISE_OFFSET)) @ Matrix.Rotation(
    math.radians(CHAISE_ANGLE),4,'Z')
root=bpy.data.objects.get('Chaise')
if root is not None:
    root.matrix_world=transform @ root.matrix_world
for o in extra:
    o.matrix_world=transform @ o.matrix_world
bpy.context.view_layer.update()
if root is not None:
    for o in extra:
        mw=o.matrix_world.copy();o.parent=root;o.matrix_world=mw

# Slight satin sheen on the dark parquet, preserving its broad brown region.
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('Box'):
        for m in o.data.materials:
            if m and m.use_nodes:
                p=m.node_tree.nodes.get('Principled BSDF')
                if p:
                    col=p.inputs['Base Color'].default_value
                    if col[0]<.13 and col[1]<.08:
                        p.inputs['Roughness'].default_value=.38

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.67,.72,.80,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.16
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-3.3,-.3,3.7),power=KEY_POWER,size=2.8,
             target=(0,0,.7),color=(1,.94,.83))
area_emitter((1,-3,3.7),power=35,size=3.5,target=(0,0,.8),color=(1,.96,.9))
sc.view_settings.view_transform='AgX'
# Audit: positive finite sizes/radii, unique include keys, valid tube paths.
# Geometry and upholstery retain separate components within semantic assemblies.
# Runner handles rendering and saving.
