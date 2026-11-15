from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(12)
scene = Scene('Warm living room')
wall = (0.72, 0.70, 0.68)
carpet = (0.31, 0.30, 0.30)
sofa = (0.67, 0.34, 0.105)
sofa_light = (0.73, 0.40, 0.15)
pillow = (0.88, 0.61, 0.29)
darkwood = (0.075, 0.045, 0.032)
scene.include('Warm gray wall', box((12, .12, 5), center=(0, 1.05, 2.5), color=wall))
scene.include('Gray carpet', box((12, 10, .08), center=(0, -1, -.05), color=carpet))

couch = Asset('Caramel upholstered sofa')
couch.include('Lower upholstered base', fillet_box((3.65, .87, .47), radius=.10, center=(0, .16, .29), color=sofa))
couch.include('Left broad arm', fillet_box((.43, 1.05, 1.02), radius=.085, center=(-1.72, .05, .57), color=sofa))
couch.include('Right broad arm', fillet_box((.43, 1.05, 1.02), radius=.085, center=(1.72, .05, .57), color=sofa_light))
for i, x in enumerate((-.78, .78)):
    couch.include('Back cushion %d' % i, fillet_box((1.53, .30, .78), radius=.10, center=(x, .56, 1.20), color=sofa_light if i else sofa))
for i, x in enumerate((-.78, .78)):
    couch.include('Seat cushion %d' % i, fillet_box((1.52, .82, .34), radius=.12, center=(x, -.08, .72), color=sofa_light if i else sofa))
leftp = fillet_box((.57, .17, .57), radius=.075, center=(-1.25, .20, 1.20), color=pillow)
leftp.turn(axis='+y', degrees=-18)
leftp.turn(axis='+z', degrees=-7)
couch.include('Left tilted pillow', leftp)
rightp = fillet_box((.52, .17, .51), radius=.07, center=(1.27, .24, 1.20), color=(.83,.56,.28))
rightp.turn(axis='+y', degrees=12)
couch.include('Right pillow', rightp)
scene.include('Sofa', couch)

# Long low coffee table, closer to the viewer than the sofa.
table = Asset('Dark wood coffee table')
table.include('Thick rectangular tabletop', box((3.45, 1.12, .13), center=(.38, -1.02, .70), color=darkwood))
table.include('Front apron', box((3.23,.08,.19), center=(.38,-1.51,.56), color=(.045,.029,.022)))
table.include('Rear apron', box((3.23,.08,.19), center=(.38,-.53,.56), color=(.045,.029,.022)))
for x in (-1.19, 1.95):
    for y in (-1.48, -.56):
        table.include('Square leg %.2f %.2f' % (x,y), box((.14,.14,.61), center=(x,y,.30), color=(.045,.027,.020)))
scene.include('Coffee table', table)

# Fabric napkins are layered flat pieces, with a few muted colored accents.
for label,x in [('Left',-.46),('Right',.98)]:
    cloth = Asset(label+' patterned napkin')
    cloth.include('Main cloth', box((.83,.53,.012), center=(x,-1.03,.775), color=(.72,.77,.72)))
    for j in range(3):
        stripe = box((.70,.025,.004), center=(x,-1.22+j*.17,.784), color=(.67,.70,.66) if j != 1 else (.77,.69,.68))
        stripe.turn(axis='+z', degrees=-5)
        cloth.include('Woven stripe %d' % j, stripe)
    scene.include(label+' napkin',cloth)

# Window edge and broad dark pleated curtains.
scene.include('Bright window strip', box((.38,.05,3.2), center=(2.13,1.00,1.76), color=(.87,.87,.84)))
curtain = Asset('Charcoal window curtain')
for i in range(8):
    x=1.48+i*.095
    curtain.include('Vertical curtain fold %d' % i, fillet_box((.14,.11,2.55), radius=.055, center=(x,.91,1.86), color=(.17+i%3*.025,.17+i%3*.025,.18+i%3*.025)))
scene.include('Curtain',curtain)

# Small tapered forms are constructed as editable meshes after the main scene is realized.
realize(scene)

def material(name,color,roughness=.7):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    return mat

porcelain=material('Soft white porcelain',(.88,.88,.85),.22)
inside=material('Cup interior shadow',(.58,.59,.57),.32)
potmat=material('Rough charcoal ceramic',(.105,.11,.105),.95)
leafmat=material('Sage green leaves',(.25,.37,.18),.88)
leaflight=material('Light green leaves',(.39,.49,.25),.85)
stemmat=material('Green stems',(.20,.30,.12),.9)
flower=material('Pale lavender blue flowers',(.48,.50,.65),.86)
flowerlight=material('Flower pale tips',(.64,.65,.75),.85)

def lathe(name, x, y, profile, mat, segments=32):
    verts=[]
    for r,z in profile:
        for i in range(segments):
            a=2*math.pi*i/segments
            verts.append((x+r*math.cos(a), y+r*math.sin(a), z))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            k=(i+1)%segments
            faces.append((j*segments+i,j*segments+k,(j+1)*segments+k,(j+1)*segments+i))
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in mesh.polygons: poly.use_smooth=True
    return obj

def curve_obj(name, points, radius, mat):
    cu=bpy.data.curves.new(name+' curve','CURVE'); cu.dimensions='3D'; cu.resolution_u=12
    cu.bevel_depth=radius; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(mat)
    return ob

for label,x,side in [('Left',-.46,-1),('Right',.98,1)]:
    y=-1.03
    lathe(label+' saucer',x,y,[(0,.799),(.15,.799),(.21,.805),(.24,.818),(.24,.825),(.18,.820),(0,.813)],porcelain)
    lathe(label+' tapered cup',x,y,[(0,.824),(.10,.824),(.125,.84),(.16,1.055),(.155,1.060),(.142,1.048),(.112,.865),(0,.85)],porcelain)
    points=[]
    for i in range(25):
        t=-math.pi/2+math.pi*i/24
        points.append((x+side*(.145+.105*math.cos(t)),y, .945+.080*math.sin(t)))
    curve_obj(label+' cup handle',points,.012,porcelain)

px,py=.28,-.73
lathe('Tapered charcoal flowerpot',px,py,[(0,.78),(.105,.78),(.14,.80),(.17,1.11),(.165,1.13),(.145,1.125),(.13,1.10),(0,1.10)],potmat)

# Curved stems, elongated pointed leaves, and loose spherical flower heads.
def leaf(name,start,end,width,mat):
    a=Vector(start); b=Vector(end); d=b-a
    perp=Vector((-d.y,d.x,0))
    if perp.length<.0001: perp=Vector((1,0,0))
    perp.normalize(); mid=a+d*.55+Vector((0,0,.025))
    verts=[a,mid+perp*width,b,mid-perp*width,mid+Vector((0,0,.018))]
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]); mesh.update()
    ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(mat)

for i in range(30):
    angle=random.random()*math.tau
    reach=random.uniform(.13,.38)
    z=random.uniform(1.20,1.47)
    end=(px+math.cos(angle)*reach,py+math.sin(angle)*reach,z)
    start=(px+random.uniform(-.04,.04),py+random.uniform(-.04,.04),1.08)
    curve_obj('Foliage stem %02d'%i,[start,end],.005,stemmat)
    for k in (0.45,0.72):
        base=Vector(start).lerp(Vector(end),k)
        direction=Vector((math.cos(angle+(-1 if k<.6 else 1)*.8),math.sin(angle+(-1 if k<.6 else 1)*.8),.34))
        tip=base+direction*random.uniform(.10,.18)
        leaf('Leaf %02d %.2f'%(i,k),base,tip,random.uniform(.018,.032),leaflight if i%3==0 else leafmat)

heads=[(-.27,.00,1.63),(-.10,.03,1.79),(.05,-.03,1.64),(.25,.04,1.57),(.12,.13,1.53)]
for h,(dx,dy,z) in enumerate(heads):
    center=Vector((px+dx,py+dy,z))
    curve_obj('Flower stem %d'%h,[(px,py,1.09),(px+dx*.6,py+dy*.6,1.37),center],.007,stemmat)
    for j in range(20):
        theta=math.acos(1-2*(j+.5)/20); phi=j*2.39996
        direction=Vector((math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)))
        pos=center+direction*.055
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.026,location=pos)
        ob=bpy.context.object; ob.name='Lavender flower %d florets %02d'%(h,j); ob.data.materials.append(flowerlight if j%4==0 else flower)

# Camera and illumination are configured after SceneAct realization.
set_view((.05,-6.8,2.35),(.05,0,1.00),lens=45)
area_emitter((3.4,-2.0,4.7),power=700,size=4.0,target=(0,0,.7),color=(1.0,.90,.78))
area_emitter((-3.5,-2.5,3.3),power=260,size=4.5,target=(0,0,1),color=(.82,.86,1.0))
if bpy.context.scene.world is None:
    bpy.context.scene.world=bpy.data.worlds.new('Warm ambient world')
bpy.context.scene.world.use_nodes=True
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.67,.65,1)
bpy.context.scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
bpy.context.scene.render.resolution_x=1280
bpy.context.scene.render.resolution_y=854
bpy.context.scene.render.resolution_percentage=100
