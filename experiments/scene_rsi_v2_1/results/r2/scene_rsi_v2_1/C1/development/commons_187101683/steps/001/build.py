from sceneact import *
import bpy, math, random
from mathutils import Vector

# Image-space inventory (origin top left; approximate, uncertain hidden geometry):
# Sofa: (.02,.28)-(.97,.97); two back cushions, two seats, broad arms and
# low upholstered base. Left loose pillow (.13,.31)-(.31,.54); right pillow
# partly hidden by the arm. Feet and rear structure mostly hidden.
# Table: (.32,.62)-(1.0,1.0); thin rectangular top, apron, four square legs;
# right extent and lower legs leave the frame. It occludes the sofa.
# Cups/saucers: (.46,.55)-(.56,.67), (.71,.55)-(.85,.68), on folded pale
# cloths. Hollow tapered cups have small outward-facing loop handles.
# Plant: (.56,.33)-(.73,.65); charcoal tapered pot supports branching
# foliage and five loose pale blue flower masses with open space between.
# Wall fills upper background; gray curtain (.80,0)-(1,.44), bright window
# beyond its right edge. Gray carpet supports all furniture.
# Single-view depth, curtain gathering, and concealed sofa parts are estimates.

random.seed(24)
scene = Scene('Warm living room')
ochre = (.66,.335,.105)
seatcol = (.72,.397,.145)
pillowcol = (.84,.53,.235)
wood = (.055,.036,.025)
green = (.16,.29,.115)

room = Asset('Architecture')
room.include('floor', box((200,200,.12), center=(0,0,-.07), color=(.36,.35,.33)))
room.include('wall', box((12,.16,7), center=(0,1.48,3.3), color=(.78,.765,.72)))
room.include('window_glow', box((1.5,.04,4.2), center=(2.55,1.365,2.3), color=(.96,.98,.98)))
scene.include('Architecture', room)

sofa = Asset('Golden velvet sofa')
sofa.include('lower upholstered base', fillet_box((3.55,1.12,.43), .085, center=(0,.55,.325), color=ochre))
sofa.include('seat support', fillet_box((3.47,1.14,.28), .07, center=(0,.52,.65), color=ochre))
for i,x in enumerate((-.755,.755)):
    sofa.include('seat cushion '+str(i),
                 fillet_box((1.48,.99,.25), .095, center=(x,.34,.865), color=seatcol))
    back = fillet_box((1.49,.25,.85), .085, center=(x,.94,1.295), color=seatcol)
    back.turn('x',-6)
    sofa.include('back cushion '+str(i),back)
for i,x in enumerate((-1.62,1.62)):
    sofa.include('arm '+str(i),fillet_box((.37,1.25,1.18), .075,
                                        center=(x,.51,.715),color=ochre))
    sofa.include('arm top '+str(i),fillet_box((.38,1.18,.15), .07,
                                            center=(x,.49,1.26),color=seatcol))
for i,x in enumerate((-1.35,1.35)):
    for j,y in enumerate((.07,1.0)):
        sofa.include('foot %d %d'%(i,j),box((.10,.10,.12),center=(x,y,.075),color=(.12,.075,.038)))
left = fillet_box((.62,.22,.64), .09, center=(-1.08,.43,1.30), color=pillowcol)
left.turn(euler=(13,-10,-7))
sofa.include('left loose pillow',left)
right = fillet_box((.55,.20,.56),.085,center=(1.12,.65,1.27),color=(.80,.47,.18))
right.turn(euler=(9,8,-9))
sofa.include('right loose pillow',right)
scene.include('Sofa',sofa)

table = Asset('Dark wood coffee table')
table.include('top', box((2.55,.93,.085),center=(.80,-.99,1.105),color=wood))
table.include('front apron',box((2.47,.065,.13),center=(.80,-1.405,1.015),color=(.033,.023,.018)))
table.include('back apron',box((2.47,.065,.13),center=(.80,-.575,1.015),color=wood))
for i,x in enumerate((-.39,1.99)):
    table.include('side apron '+str(i),box((.065,.84,.13),center=(x,-.99,1.015),color=wood))
    for j,y in enumerate((-1.39,-.59)):
        table.include('leg %d %d'%(i,j),box((.085,.085,1.04),center=(x,y,.52),color=(.027,.020,.016)))
scene.include('Table',table)

# Cloth rectangles are slightly offset and turned, exposing their corners.
for i,(x,y,angle) in enumerate(((-.04,-1.02,-9),(.94,-1.03,-13))):
    cloth = Asset('Folded linen '+str(i))
    a=box((.61,.37,.012),center=(x,y,1.156),color=(.57,.67,.62))
    a.turn('z',angle)
    cloth.include('lower folded cloth',a)
    b=box((.50,.32,.009),center=(x+.025,y-.012,1.167),color=(.81,.83,.75))
    b.turn('z',angle+6)
    cloth.include('upper folded cloth',b)
    scene.include('Linen '+str(i),cloth)

cup_specs=[('Left porcelain',-.035,-1.025),('Right porcelain',.955,-1.035)]
for name,x,y in cup_specs:
    a=Asset(name)
    a.include('saucer',rod(.171,length=.013,center=(x,y,1.185),color=(.88,.91,.89)))
    a.include('saucer inner',rod(.126,length=.006,center=(x,y,1.195),color=(.94,.96,.93)))
    sign=-1 if x<.5 else 1
    pts=[]
    for k in range(25):
        t=2*math.pi*k/24
        pts.append((x+sign*(.117+.067*math.cos(t)),y,1.326+.079*math.sin(t)))
    a.include('porcelain handle',sweep_tube(points=pts,radius=.011,color=(.94,.96,.94)))
    scene.include(name,a)

plant=Asset('Blue flowers in charcoal pot')
px,py=.47,-.79
plant.include('pot core',rod(.105,length=.25,center=(px,py,1.293),color=(.055,.061,.055)))
# Fine horizontal courses reinforce the gently tapered earthenware silhouette.
for k in range(29):
    z=1.174+k*.0092
    r=.092+.034*k/28
    plant.include('pot course %02d'%k,rod(r,length=.010,center=(px,py,z),color=(.055+.007*(k%3),.061+.007*(k%3),.055+.006*(k%3))))
plant.include('dark soil',rod(.116,length=.008,center=(px,py,1.444),color=(.045,.035,.022)))

heads=[(-.18,.015,1.79,.080),(-.025,.06,1.91,.075),
       (.12,.025,1.83,.085),(.245,.045,1.77,.079),(.04,-.045,1.75,.066)]
for i,(dx,dy,z,r) in enumerate(heads):
    plant.include('flower stem '+str(i),rod(.007,start=(px,py,1.43),end=(px+dx,py+dy,z-.035),color=(.22,.34,.13)))
    # Clustered tiny florets remain inside a controlled round flower head.
    for j in range(58):
        az=random.uniform(0,2*math.pi)
        zz=random.uniform(-1,1)
        rr=math.sqrt(1-zz*zz)
        xx=px+dx+r*rr*math.cos(az)
        yy=py+dy+r*rr*math.sin(az)
        zf=z+r*zz*.88
        col=random.choice([(.57,.64,.72),(.69,.74,.79),(.79,.81,.80),(.52,.60,.69)])
        petal=ball(random.uniform(.010,.016),center=(xx,yy,zf),color=col)
        petal.resize((1,.85,.70))
        plant.include('floret %d %d'%(i,j),petal)

# Branches occupy a broad, airy foliage mass below the flower heads.
for i in range(25):
    ang=random.uniform(0,2*math.pi)
    spread=random.uniform(.12,.30)
    top=random.uniform(1.56,1.74)
    end=(px+math.cos(ang)*spread,py+math.sin(ang)*spread*.65,top)
    start=(px,py,1.43)
    plant.include('leaf branch '+str(i),rod(.0035,start=start,end=end,color=green))
    for j in range(3):
        t=.43+.24*j
        cx=start[0]+(end[0]-start[0])*t
        cy=start[1]+(end[1]-start[1])*t
        cz=start[2]+(end[2]-start[2])*t
        side=1 if j%2 else -1
        leaf=ball(1,center=(cx+side*.022*math.sin(ang),cy-side*.022*math.cos(ang),cz),color=random.choice([green,(.24,.37,.16),(.31,.42,.20)]))
        leaf.resize((.055,.017,.009))
        leaf.turn(euler=(random.uniform(-25,25),random.uniform(-35,35),math.degrees(ang)+side*35))
        plant.include('leaf %d %d'%(i,j),leaf)
scene.include('Plant',plant)

# Named curtain asset establishes its semantic anchor; the fabric surface below
# is parented to this asset's Blender collection after realization.
curtain=Asset('Gathered gray curtain')
curtain.include('tie',rod(.022,start=(1.72,1.10,1.86),end=(2.08,1.10,1.86),color=(.34,.32,.29)))
scene.include('Curtain',curtain)

realize(scene)

def mat(name,color,rough=.5):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    return m

porcelain=mat('Soft white glazed ceramic',(.89,.93,.92),.21)
coffee=mat('Tea visible inside cups',(.105,.060,.025),.25)

def lathe(name,profile,x,y,material):
    verts=[]; faces=[]; n=80
    for r,z in profile:
        for k in range(n):
            a=2*math.pi*k/n
            verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    for j in range(len(profile)-1):
        for k in range(n):
            q=j*n+k; kn=(k+1)%n
            faces.append((q,j*n+kn,(j+1)*n+kn,q+n))
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    return ob

for name,x,y in cup_specs:
    # Closed wall cross section: narrow foot, widening side, rounded rim,
    # inner wall and inner bottom. The cup is genuinely hollow.
    profile=[(.055,1.196),(.066,1.201),(.071,1.218),
             (.091,1.315),(.113,1.414),(.115,1.422),
             (.111,1.427),(.105,1.423),(.103,1.413),
             (.082,1.315),(.065,1.227),(.0,1.227),(.0,1.196),(.055,1.196)]
    ob=lathe(name+' hollow bowl',profile,x,y,porcelain)
    # Organize the custom surface under a named semantic asset collection.
    coll=bpy.data.collections.get(name)
    if coll:
        for c in list(ob.users_collection):c.objects.unlink(ob)
        coll.objects.link(ob)
    lathe(name+' tea surface',[(0,1.394),(.098,1.394)],x,y,coffee)

# Continuous curtain surface, hanging freely above and below its gathered waist.
verts=[]; faces=[]
nu,nv=72,95
for j in range(nv+1):
    t=j/nv
    z=3.65-2.33*t
    gather=math.exp(-((z-1.87)/.27)**2)
    left=1.46+.30*gather
    width=.78-.43*gather
    for i in range(nu+1):
        u=i/nu
        x=left+u*width
        y=1.18+.075*math.cos(u*math.pi*12)*(1-.40*gather)
        y-=.075*math.sin(math.pi*t)
        verts.append((x,y,z))
for j in range(nv):
    for i in range(nu):
        a=j*(nu+1)+i
        faces.append((a,a+1,a+nu+2,a+nu+1))
mesh=bpy.data.meshes.new('Curtain continuous folded fabric')
mesh.from_pydata(verts,[],faces);mesh.update()
ob=bpy.data.objects.new('Gathered curtain fabric',mesh)
bpy.context.collection.objects.link(ob)
ob.data.materials.append(mat('Gray taupe curtain',(.24,.235,.22),.76))
for p in mesh.polygons:p.use_smooth=True
sol=ob.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.008

# Fine material variation: velvet nap, carpet fibers, and subtle wood grain.
for m in list(bpy.data.materials):
    if not m.use_nodes:
        m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if not bs:continue
    color=bs.inputs['Base Color'].default_value
    r,g,b=color[:3]
    if r>.4 and r>g*1.30 and g>b*1.35:
        bs.inputs['Roughness'].default_value=.84
        nodes=m.node_tree.nodes; links=m.node_tree.links
        noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=145
        noise.inputs['Detail'].default_value=2
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.009
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif .25<r<.46 and abs(r-g)<.04 and abs(g-b)<.04:
        bs.inputs['Roughness'].default_value=.96
        nodes=m.node_tree.nodes;links=m.node_tree.links
        noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=210
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.42
        bump.inputs['Distance'].default_value=.018
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif r<.085 and r>g and g>b:
        bs.inputs['Roughness'].default_value=.40

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.72,.76,.80,1)
    bg.inputs['Strength'].default_value=.25

set_view((1.10,-6.30,2.50),(0,0,1.35),lens=64)
area_emitter((3.0,-.2,4.2),power=650,size=3.0,target=(0,.2,.8),color=(1.0,.96,.89))
area_emitter((-2.5,-3,3.7),power=110,size=4,target=(0,0,1),color=(.88,.92,1))
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0.1
sc.render.image_settings.file_format='PNG'
