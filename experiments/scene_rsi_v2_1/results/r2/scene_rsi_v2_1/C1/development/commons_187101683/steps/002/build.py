from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory, normalized coordinates, top-left origin:
# Sofa (.02,.28)-(.97,.97): broad upholstered arms, low base, two seats,
# two backs; loose left pillow (.13,.31)-(.31,.54), partly hidden right pillow.
# Table (.32,.62)-(1,1): rectangular thin top, narrow apron, square legs.
# Table occludes sofa; its right edge and leg bottoms extend outside the frame.
# Cups (.46,.55)-(.56,.66), (.71,.55)-(.83,.67) rest on saucers and folded linen.
# Plant (.56,.33)-(.73,.65): compact blue flower heads, leafy middle,
# tapered charcoal pot. Stems have visible negative space between flower heads.
# Wall upper background, gray curtain (.81,0)-(.97,.42), bright right window.
# Concealed sofa structure and rear legs are uncertain.
# Feedback correction: table edge direction and foreground placement were wrong;
# left cup was too far left, flower mass too tall, upholstery too pale.
random.seed(24)
scene = Scene('Living room reconstruction')
ochre=(.51,.235,.055)
seatcol=(.64,.315,.075)
pillowcol=(.77,.445,.15)
wood=(.043,.027,.018)

room=Asset('Architecture')
room.include('carpet',box((100,100,.12),center=(0,0,-.07),color=(.32,.31,.30)))
room.include('wall',box((12,.16,7),center=(0,1.48,3.3),color=(.78,.765,.73)))
room.include('window',box((1.5,.04,4.2),center=(2.55,1.365,2.3),color=(.97,.98,.99)))
scene.include('Architecture',room)

sofa=Asset('Golden velvet sofa')
sofa.include('base',fillet_box((3.55,1.12,.47),.075,center=(0,.55,.325),color=ochre))
sofa.include('seat support',fillet_box((3.47,1.14,.26),.06,center=(0,.52,.66),color=ochre))
for i,x in enumerate((-.755,.755)):
    sofa.include('seat '+str(i),fillet_box((1.48,.99,.25),.085,center=(x,.34,.89),color=seatcol))
    back=fillet_box((1.49,.25,.84),.06,center=(x,.94,1.335),color=seatcol)
    back.turn('x',-6)
    sofa.include('back '+str(i),back)
for i,x in enumerate((-1.62,1.62)):
    sofa.include('arm '+str(i),fillet_box((.37,1.25,1.18),.055,center=(x,.51,.715),color=ochre))
    sofa.include('arm cap '+str(i),fillet_box((.38,1.18,.15),.055,center=(x,.49,1.26),color=seatcol))
for i,x in enumerate((-1.35,1.35)):
    for j,y in enumerate((.07,1)):
        sofa.include('foot %d %d'%(i,j),box((.10,.10,.10),center=(x,y,.055),color=(.10,.06,.03)))
left=fillet_box((.62,.22,.61),.065,center=(-1.11,.43,1.33),color=pillowcol)
left.turn(euler=(13,-10,-7))
sofa.include('left pillow',left)
right=fillet_box((.55,.20,.56),.075,center=(1.12,.65,1.29),color=(.71,.36,.09))
right.turn(euler=(9,8,-9))
sofa.include('right pillow',right)
scene.include('Sofa',sofa)

# Table is turned independently: its long edges rise toward the right in view.
angle=math.radians(25)
def tablepoint(x,y,z):
    dx=x-.8
    dy=(y+.99)*.90
    return (.85+dx*math.cos(angle)-dy*math.sin(angle),
            -.99+dx*math.sin(angle)+dy*math.cos(angle),z+.07)

def tablepart(node):
    node.resize((1,.90,1),pivot=(.8,-.99,0))
    node.turn('z',25,pivot=(.8,-.99,0))
    node.move((.05,0,.07))
    return node

table=Asset('Dark wooden coffee table')
table.include('top',tablepart(box((2.55,.93,.075),center=(.8,-.99,1.105),color=wood)))
table.include('front apron',tablepart(box((2.47,.06,.11),center=(.8,-1.405,1.02),color=(.027,.017,.012))))
table.include('rear apron',tablepart(box((2.47,.06,.11),center=(.8,-.575,1.02),color=wood)))
for i,x in enumerate((-.39,1.99)):
    table.include('side '+str(i),tablepart(box((.065,.84,.11),center=(x,-.99,1.02),color=wood)))
    for j,y in enumerate((-1.39,-.59)):
        table.include('leg %d %d'%(i,j),tablepart(box((.085,.085,1.08),center=(x,y,.50),color=(.022,.015,.011))))
scene.include('Table',table)

# Cups retain their measured image spacing independently of the table rotation.
cup_specs=[('Left porcelain',.245,-1.025),('Right porcelain',.955,-1.035)]
cup_positions=[]
for i,(name,x,y) in enumerate(cup_specs):
    x,y,_=tablepoint(x,y,0)
    cup_positions.append((name,x,y))
    cloth=Asset('Folded linen '+str(i))
    lower=box((.57,.33,.010),center=(x,y,1.226),color=(.48,.60,.54))
    lower.turn('z',-9 if i==0 else -13)
    cloth.include('lower fold',lower)
    upper=box((.49,.29,.008),center=(x+.02,y-.008,1.237),color=(.79,.82,.74))
    upper.turn('z',-3 if i==0 else -7)
    cloth.include('upper fold',upper)
    scene.include('Linen '+str(i),cloth)
    a=Asset(name)
    a.include('saucer',rod(.156,length=.012,center=(x,y,1.255),color=(.88,.92,.90)))
    a.include('saucer center',rod(.116,length=.006,center=(x,y,1.265),color=(.94,.96,.94)))
    sign=-1 if i==0 else 1
    pts=[]
    for k in range(25):
        t=2*math.pi*k/24
        pts.append((x+sign*(.104+.060*math.cos(t)),y,1.375+.066*math.sin(t)))
    a.include('loop handle',sweep_tube(points=pts,radius=.009,color=(.94,.96,.94)))
    scene.include(name,a)

plant=Asset('Blue flowers in charcoal pot')
px,py=.47,-.79
def pp(x,y,z):
    return (px+(x-px)*.80+.18,py+(y-py)*.80,1.244+(z-1.174)*.72)
def pr(r,start,end,col):
    return rod(r,start=pp(*start),end=pp(*end),color=col)
for k in range(29):
    z=1.174+k*.0092
    r=(.092+.034*k/28)*.88
    plant.include('pot course %02d'%k,rod(r,length=.008,center=pp(px,py,z),color=(.047+.005*(k%3),.052+.005*(k%3),.047+.005*(k%3))))
plant.include('soil',rod(.104,length=.006,center=pp(px,py,1.444),color=(.035,.027,.018)))
heads=[(-.18,.015,1.79,.080),(-.025,.06,1.91,.075),
       (.12,.025,1.83,.085),(.245,.045,1.77,.079),
       (.04,-.045,1.75,.066)]
for i,(dx,dy,z,r) in enumerate(heads):
    plant.include('flower stem '+str(i),pr(.0045,(px,py,1.43),(px+dx,py+dy,z-.035),(.20,.31,.11)))
    for j in range(74):
        az=random.uniform(0,2*math.pi)
        zz=random.uniform(-1,1)
        rr=math.sqrt(1-zz*zz)
        p=pp(px+dx+r*rr*math.cos(az),py+dy+r*rr*math.sin(az),z+r*zz*.88)
        col=random.choice([(.48,.57,.69),(.64,.70,.78),(.77,.80,.81),(.54,.63,.73)])
        petal=ball(random.uniform(.009,.013),center=p,color=col)
        petal.resize((1,.85,.65))
        plant.include('floret %d %d'%(i,j),petal)
for i in range(31):
    ang=random.uniform(0,2*math.pi)
    spread=random.uniform(.12,.30)
    end=(px+math.cos(ang)*spread,py+math.sin(ang)*spread*.65,random.uniform(1.56,1.74))
    start=(px,py,1.43)
    plant.include('branch '+str(i),pr(.0028,start,end,(.15,.27,.09)))
    for j in range(4):
        t=.35+.20*j
        cx=start[0]+(end[0]-start[0])*t
        cy=start[1]+(end[1]-start[1])*t
        cz=start[2]+(end[2]-start[2])*t
        side=1 if j%2 else -1
        leaf=ball(1,center=pp(cx+side*.022*math.sin(ang),cy-side*.022*math.cos(ang),cz),
                  color=random.choice([(.12,.25,.075),(.21,.34,.11),(.29,.39,.16)]))
        leaf.resize((.043,.012,.006))
        leaf.turn(euler=(random.uniform(-25,25),random.uniform(-35,35),math.degrees(ang)+side*35))
        plant.include('leaf %d %d'%(i,j),leaf)
scene.include('Plant',plant)

curtain=Asset('Gathered gray curtain')
curtain.include('tie',rod(.018,start=(1.48,1.1,1.98),end=(1.83,1.1,1.98),color=(.26,.25,.23)))
scene.include('Curtain',curtain)
realize(scene)

def mat(name,col,rough=.5):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*col,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Roughness'].default_value=rough
    return m

def attach(ob,name):
    coll=bpy.data.collections.get(name)
    if coll:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        coll.objects.link(ob)

porcelain=mat('White glazed porcelain',(.90,.94,.93),.20)
tea=mat('Tea',(.10,.065,.029),.25)
def lathe(name,profile,x,y,material,asset):
    verts=[];faces=[];n=72
    for r,z in profile:
        for k in range(n):
            a=2*math.pi*k/n
            verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    for j in range(len(profile)-1):
        for k in range(n):
            q=j*n+k
            kn=(k+1)%n
            faces.append((q,j*n+kn,(j+1)*n+kn,q+n))
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    attach(ob,asset)
    return ob

for name,x,y in cup_positions:
    raw=[(.055,1.196),(.066,1.201),(.071,1.218),(.091,1.315),
         (.113,1.414),(.115,1.422),(.111,1.427),(.105,1.423),
         (.103,1.413),(.082,1.315),(.065,1.227),(0,1.227),
         (0,1.196),(.055,1.196)]
    profile=[(r*.90,1.266+(z-1.196)*.85) for r,z in raw]
    lathe(name+' hollow cup',profile,x,y,porcelain,name)
    lathe(name+' tea',[(0,1.432),(.087,1.432)],x,y,tea,name)

# Broad hanging folds; the waist is behind the sofa arm.
verts=[];faces=[]
nu,nv=72,95
for j in range(nv+1):
    t=j/nv
    z=3.65-2.33*t
    gather=math.exp(-((z-1.98)/.31)**2)
    left=1.13+.26*gather
    width=.68-.30*gather
    for i in range(nu+1):
        u=i/nu
        x=left+u*width
        y=1.18+.075*math.cos(u*math.pi*10)*(1-.35*gather)-.11*math.sin(math.pi*t)
        verts.append((x,y,z))
for j in range(nv):
    for i in range(nu):
        a=j*(nu+1)+i
        faces.append((a,a+1,a+nu+2,a+nu+1))
mesh=bpy.data.meshes.new('Curtain folds')
mesh.from_pydata(verts,[],faces)
mesh.update()
ob=bpy.data.objects.new('Gray draped fabric',mesh)
bpy.context.collection.objects.link(ob)
ob.data.materials.append(mat('Gray taupe fabric',(.19,.185,.175),.78))
for p in mesh.polygons:p.use_smooth=True
ob.modifiers.new('Fabric thickness','SOLIDIFY').thickness=.006
attach(ob,'Gathered gray curtain')

for m in list(bpy.data.materials):
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if not bs:continue
    r,g,b=bs.inputs['Base Color'].default_value[:3]
    nodes=m.node_tree.nodes
    links=m.node_tree.links
    if r>.4 and r>g*1.3 and g>b*1.35:
        bs.inputs['Roughness'].default_value=.83
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=150
        noise.inputs['Detail'].default_value=2
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(r*.70,g*.67,b*.63,1)
        ramp.color_ramp.elements[1].position=.82
        ramp.color_ramp.elements[1].color=(r*1.10,g*1.08,b*1.05,1)
        links.new(noise.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.13
        bump.inputs['Distance'].default_value=.007
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif .25<r<.40 and abs(r-g)<.04 and abs(g-b)<.04:
        bs.inputs['Roughness'].default_value=.95
        noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=190
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.33
        bump.inputs['Distance'].default_value=.012
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif r<.07 and r>g and g>b:
        bs.inputs['Roughness'].default_value=.42
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=5
        coord=nodes.new('ShaderNodeTexCoord')
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(2,65,4)
        links.new(coord.outputs['Generated'],mapping.inputs[0])
        links.new(mapping.outputs[0],tex.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.14
        bump.inputs['Distance'].default_value=.003
        links.new(tex.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('World')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(.72,.76,.80,1)
    bg.inputs['Strength'].default_value=.16
set_view((1.10,-6.30,2.50),(0,0,1.35),lens=64)
area_emitter((3.0,-.15,4.2),power=530,size=2.7,target=(0,.2,.8),color=(1,.96,.89))
area_emitter((-2.5,-3,3.7),power=65,size=4,target=(0,0,1),color=(.88,.92,1))
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
