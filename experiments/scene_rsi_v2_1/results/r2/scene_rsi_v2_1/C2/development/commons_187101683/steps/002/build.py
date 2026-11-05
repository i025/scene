from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Discrepancy ledger, normalized image coordinates, top-left origin:
# High confidence, shared framing: sofa rendered bounds (.125,.285)-(.875,.80),
# reference about (.02,.28)-(.97,.96). Cups and table also appear too small.
# Increase camera magnification and reduce downward angle; preserve sofa top framing.
# High confidence, table: rendered slab (.255,.66)-(.934,.82), reference
# (.32,.60)-(>1,.78). Raise tabletop/contact anchors by .19, move ensemble right.
# Reference legs are cropped at bottom; rendered front feet are entirely visible.
# High confidence, cup arrangement: rendered centers (.44,.67),(.69,.67);
# reference (.515,.60),(.77,.60). Reduce world spacing while increasing magnification.
# High confidence, plant: rendered pot around (.56,.65), reference (.65,.59).
# Move with tabletop. Rendered flower arrangement has long bare stems and thin heads;
# compress stem heights relative to pot, retain separate heads, increase head coverage.
# Medium confidence, upholstery: render is pale cream-orange; reference is deep ochre.
# Deepen upholstery materials, leaving wall and porcelain unchanged.
# Curtain rendered as regular narrow waves; reference has broad gathered folds.
# Reduce fold count and broaden the draping displacement.
#
# Inventory/component anchors:
# Sofa back panels: ref centers (.32,.41),(.61,.41), seam x=.47;
# seats below, arms at x=.09/.91, loose pillow bounds (.13,.31)-(.32,.53).
# Table supports napkins, saucers, two cups and pot; all contact heights move together.
# Plant leaf mass ref (.575,.44)-(.725,.54), flower heads (.56,.33)-(.73,.47).
# Wall behind sofa; curtain behind right arm. Rear legs/window limits uncertain.

random.seed(19)
scene = Scene('Warm living room corrected')

ochre = (.48,.225,.058)
seatcol = (.59,.295,.082)
backcol = (.65,.335,.098)
pillowcol = (.73,.445,.185)
darkwood = (.038,.025,.017)

architecture = Asset('Architecture')
architecture.include('floor', box((16,14,.12), center=(0,0,-.09),
                                  color=(.31,.295,.28)))
architecture.include('wall', box((14,.12,7), center=(0,1.27,3.35),
                                 color=(.76,.75,.71)))
scene.include('architecture', architecture)

sofa = Asset('Mustard upholstered sofa')
base = Part('Base and front rail',
    fillet_box((3.70,1.02,.49), .095, center=(0,.32,.35), color=ochre),
    fillet_box((3.23,.19,.30), .055, center=(0,-.225,.48), color=(.47,.225,.065)))
sofa.include('base', base)
sofa.include('back structure', fillet_box((3.40,.27,1.30), .10,
                 center=(0,.79,1.04), color=ochre))
for i,x in enumerate((-.79,.79)):
    b = fillet_box((1.57,.30,.85), .085, center=(x,.594,1.23), color=backcol)
    b.turn('x', -5)
    sofa.include('back panel '+str(i), Part('Back cushion '+str(i), b))
    s = fillet_box((1.55,.85,.24), .10, center=(x,.05,.72), color=seatcol)
    welt = sweep_tube(
        points=[(x-.69,-.36,.707),(x-.40,-.39,.697),
                (x+.40,-.39,.697),(x+.69,-.36,.707)],
        radius=.009, color=(.42,.19,.043))
    sofa.include('seat '+str(i), Part('Seat cushion and seam '+str(i),s,welt))
for i,x in enumerate((-1.69,1.69)):
    sofa.include('arm '+str(i), Part('Upholstered arm '+str(i),
        fillet_box((.40,1.08,1.23), .085, center=(x,.22,.64),
                   color=(.54,.26,.065)),
        fillet_box((.39,.98,.18), .08, center=(x,.22,1.20),
                   color=(.60,.30,.087))))
pillow = fillet_box((.67,.23,.66), .09, center=(-1.12,.26,1.18), color=pillowcol)
pillow.turn(euler=(12,-10,-11))
sofa.include('loose pillow', Part('Loose left pillow', pillow))
scene.include('sofa',sofa)

# Placement is independent of component widths/depths and cup spacing.
ensemble_dx = .20
table_x, table_y, table_h = .47+ensemble_dx, -1.25, .84
table_w, table_d = 2.73, .94
table = Asset('Dark rectangular coffee table')
table.include('top', Part('Tabletop',
    box((table_w,table_d,.085), center=(table_x,table_y,table_h), color=darkwood)))
table.include('apron', Part('Front apron',
    box((table_w-.07,.075,.15),
        center=(table_x,table_y-table_d/2+.065,table_h-.11),
        color=(.021,.016,.012))))
for i,x in enumerate((table_x-table_w/2+.09,table_x+table_w/2-.09)):
    for j,y in enumerate((table_y-table_d/2+.085,table_y+table_d/2-.085)):
        table.include('leg %d %d'%(i,j), Part('Table leg %d %d'%(i,j),
            box((.095,.095,table_h-.045),
                center=(x,y,(table_h-.045)/2),color=(.021,.017,.013))))
scene.include('table',table)

cup_xs = (.05+ensemble_dx,.88+ensemble_dx)
height_delta = .19
napkins = Asset('Napkins and saucers')
for i,x in enumerate(cup_xs):
    n = box((.64,.36,.012),center=(x,-1.245,.702+height_delta),
            color=(.69,.77,.72))
    n.turn('z',-9 if i==0 else 8)
    n2 = box((.53,.30,.007),center=(x+.025,-1.235,.711+height_delta),
             color=(.81,.84,.79))
    n2.turn('z',5 if i==0 else -5)
    napkins.include('linen '+str(i),Part('Folded napkin '+str(i),n,n2))
scene.include('napkins',napkins)

plant = Asset('Flowering plant')
plant_x,plant_y = .36+ensemble_dx,-.99
foliage = Part('Leaf and branch mass')
for i in range(26):
    a=2*math.pi*i/26
    z=.99+random.uniform(.08,.24)+height_delta
    r=random.uniform(.15,.27)
    tip=(plant_x+math.cos(a)*r,plant_y+math.sin(a)*r,z)
    foliage.include('branch %02d'%i,
        rod(.005,start=(plant_x,plant_y,.93+height_delta),end=tip,
            color=(.16,.27,.075)))
    for j in range(3):
        t=.48+j*.21
        p=Vector((plant_x,plant_y,.93+height_delta)).lerp(Vector(tip),t)
        leaf=ball(.057,center=tuple(p),
                  color=(.17+random.random()*.07,.30+random.random()*.08,.085))
        leaf.resize((1.65,.43,.32))
        leaf.turn(euler=(random.uniform(-25,25),random.uniform(-35,35),
                         math.degrees(a)+j*80))
        foliage.include('leaf %02d %d'%(i,j),leaf)
plant.include('foliage',foliage)

heads=[(-.23,.02,1.51,.083),(-.13,.08,1.63,.082),
       (.00,.07,1.47,.090),(.055,.08,1.75,.080),
       (.20,.035,1.60,.095),(.29,.02,1.52,.080)]
for i,(dx,dy,z,r) in enumerate(heads):
    # Shorten internal stem spacing while retaining the tabletop support anchor.
    z=.98+(z-.98)*.72+height_delta
    p=(plant_x+dx,plant_y+dy,z)
    flowers=Part('Flower head and stem '+str(i))
    flowers.include('stem',sweep_tube(
        points=[(plant_x,plant_y,.94+height_delta),
                (plant_x+dx*.4,plant_y+dy,1.23+height_delta*.6),p],
        radius=.005,color=(.24,.33,.12)))
    for j in range(58):
        u=(j+.5)/58
        zz=1-2*u
        a=j*2.399963
        rr=math.sqrt(max(0,1-zz*zz))
        q=Vector(p)+Vector((math.cos(a)*rr,math.sin(a)*rr,zz))*r
        col=random.choice([(.48,.56,.65),(.60,.67,.74),
                           (.70,.74,.78),(.40,.49,.61)])
        fl=ball(.018,center=tuple(q),color=col)
        fl.resize((1,1,.78))
        flowers.include('floret '+str(j),fl)
    plant.include('flower '+str(i),flowers)
scene.include('plant',plant)
scene.include('cups',Asset('Porcelain tea service'))
scene.include('curtain',Asset('Right gray curtain'))
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
    for p in mesh.polygons: p.use_smooth=True
    return obj

def empty(name):
    o=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(o)
    return o

def lathe(name,profile,center,material,parent):
    n=72
    verts=[]
    for r,z in profile:
        for k in range(n):
            a=2*math.pi*k/n
            verts.append((center[0]+r*math.cos(a),
                          center[1]+r*math.sin(a),center[2]+z))
    faces=[]
    for j in range(len(profile)-1):
        for k in range(n):
            a=j*n+k
            b=j*n+(k+1)%n
            faces.append((a,b,b+n,a+n))
    return mesh_obj(name,verts,faces,material,parent)

ceramic=mat('Soft ivory glazed porcelain',(.86,.88,.84),.22)
tea=mat('Tea in cups',(.16,.095,.035),.2)
potmat=mat('Charcoal flowerpot',(.055,.066,.058),.82)
soilmat=mat('Dark pot soil',(.055,.039,.022),1)
potparent=empty('Flowerpot components')
potbase=.697+height_delta
lathe('Tapered ribbed charcoal pot',
      [(0,0),(.092,0),(.104,.035),(.129,.235),(.138,.255),(.137,.272),
       (.119,.272),(.115,.251),(.111,.233),(0,.233)],
      (plant_x,plant_y,potbase),potmat,potparent)
for i in range(14):
    z=.02+i*.017
    r=.099+z*.13
    lathe('Pot horizontal ridge '+str(i),
          [(r,z-.0015),(r+.002,z),(r,z+.0015)],
          (plant_x,plant_y,potbase),potmat,potparent)
lathe('Soil surface',[(0,.245),(.114,.245)],
      (plant_x,plant_y,potbase),soilmat,potparent)

for i,x in enumerate(cup_xs):
    parent=empty('Porcelain cup and saucer '+str(i))
    y=-1.25
    lathe('Saucer '+str(i),
          [(0,0),(.095,0),(.169,.012),(.20,.022),(.203,.029),
           (.178,.034),(.12,.018),(0,.018)],
          (x,y,.718+height_delta),ceramic,parent)
    lathe('Open tea cup '+str(i),
          [(0,0),(.071,0),(.075,.018),(.088,.09),(.112,.225),
           (.112,.236),(.104,.239),(.101,.225),(.078,.080),
           (.066,.027),(0,.027)],
          (x,y,.742+height_delta),ceramic,parent)
    lathe('Visible tea '+str(i),[(0,.209),(.099,.209)],
          (x,y,.742+height_delta),tea,parent)
    side=-1 if i==0 else 1
    curve=bpy.data.curves.new('Handle curve '+str(i),'CURVE')
    curve.dimensions='3D'
    curve.bevel_depth=.012
    curve.bevel_resolution=4
    sp=curve.splines.new('POLY')
    sp.points.add(30)
    for k in range(31):
        a=-math.pi/2+math.pi*k/30
        xx=x+side*(.092+.112*math.cos(a))
        zz=.742+height_delta+.135+.068*math.sin(a)
        sp.points[k].co=(xx,y,zz,1)
    ob=bpy.data.objects.new('Cup handle '+str(i),curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(ceramic)
    ob.parent=parent

fabric=mat('Gray taupe curtain fabric',(.22,.215,.20),.95)
cp=empty('Curtain fabric panels')
verts=[]
faces=[]
nx,nz=65,48
for j in range(nz):
    t=j/(nz-1)
    z=1.20+t*2.7
    for i in range(nx):
        u=i/(nx-1)
        gather=math.exp(-((z-1.92)/.40)**2)
        x=1.66+.73*u+.23*gather*(1-u)
        y=.91+.10*math.sin(u*math.pi*9+.65*math.sin(t*4))
        y-=.29*gather*math.sin(u*math.pi)
        verts.append((x,y,z))
for j in range(nz-1):
    for i in range(nx-1):
        a=j*nx+i
        faces.append((a,a+1,a+1+nx,a+nx))
mesh_obj('Long gathered pleated curtain',verts,faces,fabric,cp)
sheer=mat('Bright window sheer',(.86,.88,.87),.85)
mesh_obj('Window light sheer',
         [(2.28,.99,1.1),(2.80,.99,1.1),(2.80,.99,4.1),(2.28,.99,4.1)],
         [(0,1,2,3)],sheer,cp)

# Procedural fabric variation; the photograph is never used as a texture.
for m in list(bpy.data.materials):
    if not m.use_nodes: m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    if not p: continue
    c=p.inputs['Base Color'].default_value
    if c[0]>.40 and c[0]>c[1]*1.25 and c[1]>c[2]*1.3:
        p.inputs['Roughness'].default_value=.88
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=145
        noise.inputs['Detail'].default_value=2
        bump=m.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.14
        bump.inputs['Distance'].default_value=.012
        m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])

# Keep foreground objects sharp and soften the sofa gently with camera focus.
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.70,.73,.77,1)
    bg.inputs['Strength'].default_value=.19

set_view((-.65,-5.9,2.28),(.03,0,1.20),lens=51,sensor=36)
area_emitter((3.1,-.25,3.4),power=590,size=3.2,
             target=(0,0,.65),color=(1,.95,.87))
area_emitter((-.9,-3.5,3.7),power=95,size=4.0,
             target=(0,0,1),color=(1,.94,.85))
cam=sc.camera
focus=empty('Focus on tea and flowers')
focus.location=(plant_x,-1.1,1.15)
cam.data.dof.use_dof=True
cam.data.dof.focus_object=focus
cam.data.dof.aperture_fstop=5.6

sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
