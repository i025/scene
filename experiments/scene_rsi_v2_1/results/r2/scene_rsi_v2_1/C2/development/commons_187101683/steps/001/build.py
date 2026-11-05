from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Estimated image inventory, normalized coordinates, origin at upper left:
# Wall: full upper background; floor begins around y=.88, mostly occluded.
# Sofa: (.02,.28)-(.97,.96). Back panels centered (.32,.41),(.61,.41),
#   extent about .30 x .25 each; narrow seam at x=.47.
#   Seat masses centered (.32,.62),(.65,.62), with a shallow center gap.
#   Arms centered (.09,.67),(.91,.62); left front arm extends to y=.94.
#   One loose pillow: (.13,.31)-(.32,.53), supported by seat/back.
# Table: (.32,.60)-(1.05,1.0), in front of and occluding sofa.
#   Thin top, broad dark front apron, four legs, some hidden/cropped.
# Cups: centers (.515,.60),(.765,.60); each body about .065 x .09.
#   Saucers beneath; folded pale napkins extend sideways beyond saucers.
# Plant: (.56,.33)-(.73,.65), pot centered (.647,.59).
#   Leaf mass (.575,.44)-(.725,.54); six separated flower heads above it,
#   with visible thin branching stems and open gaps between heads.
# Curtain: (.80,0)-(1,.43), folds and gathered drape; window beyond right edge.
# Hidden sofa construction, rear table legs, and window bounds are uncertain.

random.seed(19)
scene = Scene('Warm living room')
ochre = (.66,.345,.105)
seatcol = (.74,.425,.17)
backcol = (.79,.47,.20)
pillowcol = (.85,.58,.28)
darkwood = (.055,.038,.026)

architecture = Asset('Architecture')
architecture.include('floor', box((16,14,.12), center=(0,0,-.09), color=(.31,.295,.28)))
architecture.include('wall', box((14,.12,7), center=(0,1.27,3.35), color=(.76,.75,.71)))
scene.include('architecture', architecture)

sofa = Asset('Mustard upholstered sofa')
sofa.include('base', fillet_box((3.70,1.02,.49), .095, center=(0,.32,.35), color=ochre))
sofa.include('front upholstered rail', fillet_box((3.23,.19,.30), .055, center=(0,-.225,.48), color=(.65,.35,.12)))
sofa.include('back structure', fillet_box((3.40,.27,1.30), .10, center=(0,.79,1.04), color=ochre))
for i, x in enumerate((-.79,.79)):
    b = fillet_box((1.57,.30,.85), .085, center=(x,.594,1.23), color=backcol)
    b.turn('x', -5)
    sofa.include('back cushion '+str(i), b)
    s = fillet_box((1.55,.85,.24), .10, center=(x,.05,.72), color=seatcol)
    sofa.include('seat cushion '+str(i), s)
    # Fine darker seams near the front of the upholstered seat.
    sofa.include('seat welt '+str(i), sweep_tube(
        points=[(x-.69,-.36,.707),(x-.40,-.39,.697),(x+.40,-.39,.697),(x+.69,-.36,.707)],
        radius=.009, color=(.57,.30,.10)))
for i, x in enumerate((-1.69,1.69)):
    sofa.include('arm '+str(i), fillet_box((.40,1.08,1.23), .085,
                 center=(x,.22,.64), color=(.71,.395,.145)))
    sofa.include('arm upper pad '+str(i), fillet_box((.39,.98,.18), .08,
                 center=(x,.22,1.20), color=(.75,.43,.18)))
pillow = fillet_box((.67,.23,.66), .09, center=(-1.12,.26,1.18), color=pillowcol)
pillow.turn(euler=(12,-10,-11))
sofa.include('loose left pillow', pillow)
scene.include('sofa', sofa)

table = Asset('Dark rectangular coffee table')
table_x, table_y, table_h = .47, -1.25, .65
table_w, table_d = 2.73, .94
table.include('slab', box((table_w,table_d,.085),
              center=(table_x,table_y,table_h), color=darkwood))
table.include('front apron', box((table_w-.07,.075,.15),
              center=(table_x,table_y-table_d/2+.065,table_h-.11), color=(.029,.024,.018)))
for i, x in enumerate((table_x-table_w/2+.09, table_x+table_w/2-.09)):
    for j, y in enumerate((table_y-table_d/2+.085,table_y+table_d/2-.085)):
        table.include('leg %d %d'%(i,j), box((.095,.095,.60),
                       center=(x,y,.30), color=(.028,.024,.019)))
scene.include('table',table)

napkins = Asset('Napkins and saucers')
for i, x in enumerate((-.16,.85)):
    n=box((.72,.40,.012), center=(x,-1.245,.702), color=(.69,.77,.72))
    n.turn('z', -9 if i==0 else 8)
    napkins.include('folded linen '+str(i),n)
    n2=box((.57,.32,.007), center=(x+.025,-1.235,.711), color=(.81,.84,.79))
    n2.turn('z',5 if i==0 else -5)
    napkins.include('upper linen fold '+str(i),n2)
scene.include('napkins',napkins)

plant = Asset('Flowering plant')
plant_x,plant_y=.36,-.99
for i in range(20):
    a=2*math.pi*i/20
    z=.99+random.uniform(.08,.24)
    r=random.uniform(.15,.27)
    tip=(plant_x+math.cos(a)*r,plant_y+math.sin(a)*r,z)
    plant.include('foliage stem %02d'%i,rod(.006,start=(plant_x,plant_y,.93),end=tip,color=(.18,.30,.09)))
    for j in range(2):
        t=.6+j*.3
        base=Vector((plant_x,plant_y,.93)).lerp(Vector(tip),t)
        leaf=ball(.06,center=tuple(base),color=(.20+random.random()*.08,.36+random.random()*.08,.11))
        leaf.resize((1.65,.43,.32))
        leaf.turn(euler=(random.uniform(-25,25),random.uniform(-35,35),math.degrees(a)+j*80))
        plant.include('leaf %02d %d'%(i,j),leaf)

heads=[(-.23,.02,1.51,.083),(-.13,.08,1.63,.082),
       (.00,.07,1.47,.090),(.055,.08,1.75,.080),
       (.20,.035,1.60,.095),(.29,.02,1.52,.080)]
for i,(dx,dy,z,r) in enumerate(heads):
    p=(plant_x+dx,plant_y+dy,z)
    plant.include('flower stem '+str(i),sweep_tube(
        points=[(plant_x,plant_y,.94),(plant_x+dx*.4,plant_y+dy,1.23),p],
        radius=.005,color=(.26,.36,.15)))
    # Each clustered flower is a compact rounded head, with tiny separated florets.
    for j in range(44):
        u=(j+.5)/44
        zz=1-2*u
        a=j*2.399963
        rr=math.sqrt(max(0,1-zz*zz))
        q=Vector(p)+Vector((math.cos(a)*rr,math.sin(a)*rr,zz))*r
        col=random.choice([(.52,.59,.66),(.64,.70,.75),(.71,.75,.77),(.44,.53,.63)])
        fl=ball(.014,center=tuple(q),color=col)
        fl.resize((1,1,.72))
        plant.include('floret %d %d'%(i,j),fl)
scene.include('plant',plant)

curtain = Asset('Right gray curtain')
# Vertical pleats; mesh fabric surface added after realization.
scene.include('curtain',curtain)
realize(scene)

def mat(name,color,rough=.7):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m

def mesh_obj(name,verts,faces,material,parent=None):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    if parent: obj.parent=parent
    for p in mesh.polygons:p.use_smooth=True
    return obj

def empty(name):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    return o

def lathe(name,profile,center,material,parent):
    n=72
    v=[]
    for r,z in profile:
        for k in range(n):
            a=2*math.pi*k/n
            v.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),center[2]+z))
    f=[]
    for j in range(len(profile)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n
            f.append((a,b,b+n,a+n))
    return mesh_obj(name,v,f,material,parent)

ceramic=mat('Soft ivory glazed porcelain',(.86,.88,.84),.22)
tea=mat('Tea in cups',(.16,.095,.035),.2)
potmat=mat('Charcoal flowerpot',(.075,.085,.076),.82)
soilmat=mat('Dark pot soil',(.055,.039,.022),1)
potparent=empty('Flowerpot components')
lathe('Tapered ribbed charcoal pot',
      [(0,0),(.092,0),(.104,.035),(.129,.235),(.138,.255),(.137,.272),
       (.119,.272),(.115,.251),(.111,.233),(0,.233)],
      (plant_x,plant_y,.697),potmat,potparent)
for i in range(14):
    z=.02+i*.017
    r=.099+z*.13
    lathe('Pot fine horizontal ridge '+str(i),
          [(r,z-.0015),(r+.002,z),(r,z+.0015)],(plant_x,plant_y,.697),potmat,potparent)
lathe('Soil surface',[(0,.245),(.114,.245)],(plant_x,plant_y,.697),soilmat,potparent)

for i,x in enumerate((-.16,.85)):
    parent=empty('Porcelain cup and saucer '+str(i))
    y=-1.25
    lathe('Saucer '+str(i),[(0,0),(.095,0),(.169,.012),(.20,.022),(.203,.029),
          (.178,.034),(.12,.018),(0,.018)],(x,y,.718),ceramic,parent)
    lathe('Open tea cup '+str(i),
          [(0,0),(.071,0),(.075,.018),(.088,.09),(.112,.225),
           (.112,.236),(.104,.239),(.101,.225),(.078,.080),(.066,.027),(0,.027)],
          (x,y,.742),ceramic,parent)
    lathe('Visible tea '+str(i),[(0,.209),(.099,.209)],(x,y,.742),tea,parent)
    # Handles lie in the XZ plane, outward from each cup.
    side=-1 if i==0 else 1
    curve=bpy.data.curves.new('Handle curve '+str(i),'CURVE')
    curve.dimensions='3D';curve.bevel_depth=.012;curve.bevel_resolution=4
    sp=curve.splines.new('POLY');sp.points.add(30)
    for k in range(31):
        a=-math.pi/2+math.pi*k/30
        xx=x+side*(.092+.112*math.cos(a))
        zz=.742+.135+.068*math.sin(a)
        sp.points[k].co=(xx,y,zz,1)
    ob=bpy.data.objects.new('Cup handle '+str(i),curve)
    bpy.context.collection.objects.link(ob);ob.data.materials.append(ceramic);ob.parent=parent

# Broad fabric panel at the right edge, drawn into a gathered fold.
fabric=mat('Gray taupe curtain fabric',(.31,.30,.28),.95)
cp=empty('Curtain fabric panels')
verts=[];faces=[]
nx,nz=65,48
for j in range(nz):
    t=j/(nz-1)
    z=1.20+t*2.7
    for i in range(nx):
        u=i/(nx-1)
        # Narrow gathered waist around z=1.8, fuller top and bottom.
        gather=math.exp(-((z-1.92)/.35)**2)
        x=1.66+.73*u+.20*gather*(1-u)
        y=.91+.085*math.sin(u*math.pi*15+.35*math.sin(t*4))-.20*gather*math.sin(u*math.pi)
        verts.append((x,y,z))
for j in range(nz-1):
    for i in range(nx-1):
        a=j*nx+i;faces.append((a,a+1,a+1+nx,a+nx))
mesh_obj('Long gathered pleated curtain',verts,faces,fabric,cp)
sheer=mat('Bright window sheer',(.86,.88,.87),.85)
mesh_obj('Window light sheer',[(2.28,.99,1.1),(2.80,.99,1.1),(2.80,.99,4.1),(2.28,.99,4.1)],
         [(0,1,2,3)],sheer,cp)

# Subtle surface texture shared by upholstery; no photographic textures.
for m in list(bpy.data.materials):
    if not m.use_nodes:
        m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    if not p:continue
    c=p.inputs['Base Color'].default_value
    if c[0]>.45 and c[0]>c[1]*1.25 and c[1]>c[2]*1.3:
        p.inputs['Roughness'].default_value=.88
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=145
        noise.inputs['Detail'].default_value=2
        bump=m.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.14
        bump.inputs['Distance'].default_value=.012
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])

# Fine matte carpet variation.
floor_obj=next((o for o in bpy.data.objects if o.type=='MESH' and 'floor' in o.name.lower()),None)
if floor_obj and floor_obj.data.materials:
    m=floor_obj.data.materials[0];m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=190
    b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.27;b.inputs['Distance'].default_value=.014
    m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height'])
    m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])

sc=bpy.context.scene
if sc.world is None:sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.70,.73,.77,1)
    bg.inputs['Strength'].default_value=.24
set_view((.35,-6.65,2.65),(.02,-.02,1.06),lens=47,sensor=36)
area_emitter((3.1,-.25,3.4),power=680,size=3.2,target=(0,0,.65),color=(1,.95,.87))
area_emitter((-.9,-3.5,3.7),power=145,size=4.0,target=(0,0,1),color=(1,.94,.85))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
