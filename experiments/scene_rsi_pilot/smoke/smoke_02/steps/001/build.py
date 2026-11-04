from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(19)

scene = Scene('Victorian reading corner')
gold = (.57,.34,.16)
fabric = (.65,.43,.24)
wood = (.16,.075,.025)

scene.include('floor', box((8,8,.12), center=(0,0,-.085), color=(.22,.19,.14)))
scene.include('rear_wall', box((6,.12,3.8), center=(0,1.35,1.8), color=(.55,.49,.37)))
scene.include('side_wall', box((.12,5,3.8), center=(-1.6,0,1.8), color=(.47,.42,.32)))

# Window and its deep recess.
scene.include('window_dark_recess', box((1.32,.08,2.5), center=(-.35,1.265,1.93), color=(.12,.17,.18)))
scene.include('window_glass', box((1.13,.035,2.35), center=(-.35,1.205,1.95), color=(.52,.69,.77)))
for x in (-.96,.25):
    scene.include('window_jamb'+str(x), box((.055,.12,2.55), center=(x,1.16,1.94),color=(.55,.48,.34)))
scene.include('window_mullion',box((.035,.1,2.4),center=(-.34,1.14,1.95),color=(.74,.73,.64)))

chair = Asset('large upholstered armchair')
chair.include('lower_body',fillet_box((1.4,1.25,.39),.10,center=(0,0,.49),color=fabric))
chair.include('front_apron',fillet_box((1.37,.18,.31),.06,center=(0,-.59,.48),color=fabric))
chair.include('seat_cushion',fillet_box((1.05,1.02,.22),.105,center=(0,-.035,.755),color=fabric))
chair.include('back',fillet_box((1.39,.30,.72),.14,center=(0,.50,1.055),color=fabric))
chair.include('back_cushion',fillet_box((1.12,.21,.54),.09,center=(0,.305,1.10),color=fabric))
for x in (-.66,.66):
    chair.include('arm_body'+str(x),fillet_box((.28,1.23,.51),.12,center=(x,-.025,.74),color=fabric))
    chair.include('rolled_arm'+str(x),fillet_box((.34,1.23,.28),.135,center=(x,-.025,.995),color=fabric))
    chair.include('arm_front'+str(x),fillet_box((.31,.17,.52),.10,center=(x,-.57,.765),color=fabric))
for x in (-.55,.55):
    for y in (-.48,.45):
        chair.include('leg'+str((x,y)),rod(.052,start=(x,y,.10),end=(x*.97,y,.38),color=wood))
        chair.include('foot'+str((x,y)),ball(.061,center=(x,y,.115),color=wood))
scene.include('chair',chair)

# Narrow raised piping follows cushion edges.
for z in (.69,.845):
    pts=[]
    for i in range(65):
        a=2*math.pi*i/64
        # rounded rectangular contour
        xx=.49*math.copysign(abs(math.cos(a))**.26,math.cos(a))
        yy=.455*math.copysign(abs(math.sin(a))**.26,math.sin(a))
        pts.append((xx,yy-.035,z))
    scene.include('seat_piping'+str(z),sweep_tube(points=pts,radius=.009,color=(.48,.29,.14)))

# A second upholstered seat enters the bottom-left corner.
other=Asset('foreground ottoman')
other.include('ottoman_cushion',fillet_box((.76,.75,.22),.10,center=(-1.0,-1.32,.46),color=fabric))
other.include('ottoman_base',box((.65,.63,.21),center=(-1.,-1.32,.28),color=wood))
scene.include('foreground_ottoman',other)

# Rug with individually articulated borders and floral ornaments.
scene.include('rug',box((3.0,3.15,.025),center=(.08,-.48,.002),color=(.09,.105,.095)))
scene.include('rug_inner',box((2.57,2.72,.009),center=(.08,-.48,.019),color=(.70,.69,.53)))
for inset,width,col in [(0.06,.035,(.64,.48,.29)),(.13,.055,(.73,.66,.48)),(.24,.025,(.30,.23,.16)),(.30,.035,(.19,.22,.20))]:
    for x in (-1.5+inset,1.5-inset):
        scene.include('borderx'+str((inset,x)),box((width,3.15-2*inset,.008),center=(x+.08,-.48,.026),color=col))
    for y in (-1.575+inset,1.575-inset):
        scene.include('bordery'+str((inset,y)),box((3-2*inset,width,.008),center=(.08,y-.48,.026),color=col))

def rugflower(name,x,y,r,col):
    nodes=[]
    for j in range(7):
        a=j*2*math.pi/7
        pet=ball(r*.46,center=(x+math.cos(a)*r*.55,y+math.sin(a)*r*.55,.034),color=col)
        pet.resize((1,.55,.045))
        pet.turn('z',math.degrees(a))
        nodes.append(pet)
    c=ball(r*.23,center=(x,y,.037),color=(.53,.31,.16))
    c.resize((1,1,.08))
    nodes.append(c)
    scene.include(name,assemble(nodes))

for row in range(12):
    for column in range(10):
        x=-1.05+column*.25+(row%2)*.10
        y=-1.7+row*.23
        if x<1.26:
            col=random.choice([(.22,.28,.25),(.33,.34,.27),(.57,.48,.31),(.13,.21,.20)])
            rugflower('field_flower%d_%d'%(row,column),x,y,.075 if (row+column)%3 else .12,col)
for side in (-1,1):
    for k in range(17):
        rugflower('side_blossom'+str((side,k)),.08+side*1.35,-1.88+k*.176,.068,(.72,.61,.40))
for side in (-1,1):
    for k in range(15):
        rugflower('end_blossom'+str((side,k)),-1.17+k*.18,-.48+side*1.43,.065,(.72,.61,.40))

# Books lie at different angles on the seat.
def book(name,center,size,angle,cover):
    x,y,z=center
    w,d,h=size
    obj=Asset(name)
    obj.include('pages',box((w-.018,d-.025,h-.022),center=center,color=(.66,.54,.33)))
    for dz in (-h/2,h/2):
        obj.include('cover'+str(dz),box((w+.018,d+.016,.016),center=(x,y,z+dz),color=cover))
    obj.include('spine',box((.025,d,h),center=(x-w/2,y,z),color=cover))
    for i in range(5):
        obj.include('page_rule'+str(i),box((w-.03,.003,.002),center=(x,y-d/2+.011,z-h*.34+i*h*.15),color=(.39,.30,.19)))
    obj.turn('z',angle)
    scene.include(name,obj)
book('large ochre book',(.20,-.08,.94),(.43,.42,.16),-12,(.38,.24,.09))
book('dark decorated book',(.20,-.025,1.045),(.44,.36,.065),8,(.22,.18,.18))
book('small reddish book',(.12,.055,1.10),(.29,.32,.055),-7,(.38,.19,.16))

# Top hat resting on the left arm.
hat=Asset('black silk top hat')
hat.include('brim',rod(.235,length=.035,center=(-.66,-.32,1.17),color=(.024,.027,.026)))
hat.include('crown',rod(.155,length=.34,center=(-.66,-.32,1.35),color=(.025,.031,.033)))
hat.include('top',rod(.164,length=.027,center=(-.66,-.32,1.525),color=(.033,.039,.039)))
hat.include('hat_ribbon',rod(.158,length=.063,center=(-.66,-.32,1.225),color=(.055,.055,.052)))
hat.turn('y',-8)
scene.include('hat',hat)

# A dark folded cloth draped over the far right of the chair.
cloth=Asset('dark throw')
cloth.include('upper_fold',fillet_box((.65,.37,.10),.045,center=(.34,.53,1.45),color=(.034,.059,.064)))
cloth.include('hanging_fold',fillet_box((.37,.10,.38),.04,center=(.57,.54,1.28),color=(.035,.055,.060)))
cloth.turn('z',-9)
scene.include('throw',cloth)

realize(scene)

# Rich woven upholstery, using only generated texture coordinates.
mat=bpy.data.materials.new('golden paisley tapestry')
mat.diffuse_color=(*fabric,1)
mat.use_nodes=True
n=mat.node_tree.nodes
l=mat.node_tree.links
bs=n.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.86
tex=n.new('ShaderNodeTexCoord')
mapping=n.new('ShaderNodeVectorMath'); mapping.operation='SCALE'
mapping.inputs[3].default_value=6.5
l.new(tex.outputs['Generated'],mapping.inputs[0])
noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3
noise.inputs['Detail'].default_value=3
noise.inputs['Roughness'].default_value=.75
l.new(mapping.outputs['Vector'],noise.inputs['Vector'])
wave=n.new('ShaderNodeTexWave'); wave.wave_type='RINGS'; wave.rings_direction='Z'
wave.inputs['Scale'].default_value=3.1
wave.inputs['Distortion'].default_value=6.8
wave.inputs['Detail'].default_value=4
wave.inputs['Detail Scale'].default_value=1.2
l.new(mapping.outputs['Vector'],wave.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
cr=ramp.color_ramp
cr.elements.remove(cr.elements[1])
colors=[(0,(.23,.12,.055,1)),(.18,(.43,.25,.11,1)),(.32,(.73,.52,.28,1)),(.45,(.82,.65,.40,1)),(.52,(.46,.32,.19,1)),(.61,(.72,.62,.43,1)),(.73,(.57,.35,.16,1)),(.88,(.78,.52,.26,1)),(1,(.39,.22,.11,1))]
cr.elements[0].color=colors[0][1]
for pos,c in colors[1:]:
    e=cr.elements.new(pos);e.color=c
l.new(wave.outputs['Color'],ramp.inputs[0])
l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=190
fine.inputs['Detail'].default_value=2
l.new(tex.outputs['Generated'],fine.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.018
l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj.data.materials:
        c=obj.data.materials[0].diffuse_color
        if abs(c[0]-fabric[0])<.015 and abs(c[1]-fabric[1])<.015:
            obj.data.materials.clear();obj.data.materials.append(mat)

# Curtains are softly corrugated fabric meshes.
def curtain(name,x0,x1,y,z0,z1,color,translucent=False):
    verts=[];faces=[]
    count=72
    for i in range(count+1):
        t=i/count
        x=x0+(x1-x0)*t
        yy=y+.045*math.sin(t*math.pi*18)
        verts.extend([(x,yy,z0),(x,yy,z1)])
    for i in range(count):
        faces.append((2*i,2*i+2,2*i+3,2*i+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    m=bpy.data.materials.new(name+' fabric');m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=1
    if translucent:
        p.inputs['Base Color'].default_value=(*color,1)
        if 'Transmission Weight' in p.inputs:p.inputs['Transmission Weight'].default_value=.24
    obj.data.materials.append(m)
    for polygon in mesh.polygons:polygon.use_smooth=True

curtain('left heavy drapes',-1.63,-.91,1.01,.02,3.4,(.43,.36,.25))
curtain('right heavy drapes',.30,.85,1.04,.05,3.4,(.44,.37,.27))
curtain('ivory net curtain',-.93,.30,1.12,.87,3.4,(.65,.74,.76),True)

# Add decorative scrolling lines across the most visible upholstered front.
def curve_line(name,points,radius,color):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=2
    sp=data.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    m=bpy.data.materials.new(name+' thread');m.diffuse_color=(*color,1);obj.data.materials.append(m)
for i in range(9):
    x=-.60+i*.15
    pts=[]
    for k in range(44):
        a=k/43*math.pi*3.5
        r=.008+.055*k/43
        pts.append((x+r*math.cos(a),-.689,.49+r*1.55*math.sin(a)))
    curve_line('woven scroll '+str(i),pts,.0034,(.78,.62,.37))

set_view((2.65,-3.75,2.80),(-.03,-.10,.74),lens=45)
area_emitter((-.70,.96,2.55),power=260,size=1.25,target=(0,-.2,.7),color=(.70,.83,1))
area_emitter((.2,-3.1,3.4),power=100,size=3,target=(0,0,.65),color=(1,.83,.62))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.25,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.3
sc=bpy.context.scene
sc.render.resolution_x=170
sc.render.resolution_y=256
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'
