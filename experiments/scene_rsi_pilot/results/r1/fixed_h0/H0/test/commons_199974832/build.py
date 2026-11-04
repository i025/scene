from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(18)
scene=Scene("Old woodworking tool museum")
wood=(.22,.085,.025)
oak=(.36,.17,.055)
honey=(.48,.255,.075)
darkwood=(.105,.043,.014)
iron=(.027,.032,.029)
steel=(.24,.265,.25)
cream=(.72,.70,.58)

def add(n,o):
    scene.include(n,o)
    return o
def cube(n,s,p,c):
    return add(n,box(s,center=p,color=c))
def cyl(n,a,b,r,c):
    return add(n,rod(radius=r,start=a,end=b,color=c))
def seg(n,a,b,w,d,c):
    a,b=Vector(a),Vector(b)
    v=b-a
    ob=box((v.length,d,w),center=tuple((a+b)/2),color=c)
    ob.turn('y',-math.degrees(math.atan2(v.z,v.x)))
    return add(n,ob)

cube('rear wall',(6.4,.16,7),(0,2.75,3),(.62,.66,.62))
cube('right wall',(.16,6,7),(3.05,0,3),(.68,.70,.66))
cube('left wall',(.14,6,7),(-3.05,0,3),(.55,.61,.59))
cube('floor',(6.2,7,.12),(0,-.4,-.08),(.17,.13,.085))
cube('window recess',(.045,2.25,3.25),(-2.956,.15,2.39),(.055,.095,.10))
cube('window blue',(.03,2.12,3.10),(-2.922,.15,2.40),(.15,.36,.48))
for y in (-.94,-.40,.15,.69,1.24):
    cube('window mullion '+str(y),(.10,.045,3.18),(-2.88,y,2.40),(.63,.69,.67))
for z in (.83,2.39,3.97):
    cube('window crossbar '+str(z),(.10,2.22,.055),(-2.88,.15,z),(.67,.71,.67))
cube('window sill',(.24,2.38,.09),(-2.82,.15,.80),honey)

levels=[1.17,1.78,2.40,3.03]
for i,z in enumerate(levels):
    cube('back shelf '+str(i),(5.65,.46,.065),(0,2.42,z),honey)
    cube('back shelf edge '+str(i),(5.66,.045,.055),(0,2.175,z-.02),oak)
    cube('right shelf '+str(i),(.47,3.9,.075),(2.78,.56,z),honey)
    for x in (-2.3,-.75,.85,2.2):
        cube('back label '+str((i,x)),(.25,.012,.035),(x,2.147,z-.018),cream)
    for y in (-1,-.25,.62,1.65):
        cube('side label '+str((i,y)),(.012,.23,.035),(2.531,y,z-.018),cream)
    for x in (-2.35,0,2.3):
        cube('support '+str((i,x)),(.045,.25,.19),(x,2.55,z-.13),(.24,.25,.21))

def plane(n,x,y,z,length=.45,width=.14,angle=0,woody=True):
    a=Asset(n)
    c=random.choice([wood,oak,honey,darkwood])
    a.include('sole',box((length,width,.035),center=(x,y,z+.02),color=darkwood if woody else iron))
    a.include('body',box((length*.98,width,.12),center=(x,y,z+.08),color=c if woody else iron))
    blade=box((.055,width*.83,.23),center=(x+.02,y,z+.21),color=iron)
    blade.turn('y',-27)
    a.include('iron',blade)
    wedge=box((.055,width*.57,.13),center=(x-.025,y-.005,z+.17),color=oak)
    wedge.turn('y',-28)
    a.include('wedge',wedge)
    if length>.33:
        a.include('knob stem',rod(radius=.03,start=(x-length*.32,y,z+.13),end=(x-length*.32,y,z+.22),color=darkwood))
        a.include('knob',ball(radius=.041,center=(x-length*.32,y,z+.23),color=c))
        a.include('handle',sweep_tube(points=[(x+length*.31,y,z+.13),(x+length*.29,y,z+.29),(x+length*.21,y,z+.32),(x+length*.14,y,z+.26),(x+length*.16,y,z+.13)],radius=.027,color=c))
    a.turn('z',angle,pivot=(x,y,z))
    scene.include(n,a)

for j in range(56):
    x=-2.67+j*.097+random.uniform(-.013,.013)
    h=random.uniform(.15,.32)
    cube('moulding plane '+str(j),(.075,.23,h),(x,2.42,3.07+h/2),random.choice([wood,oak,honey,darkwood]))
    blade=box((.025,.05,.14),center=(x,2.303,3.12+h*.65),color=iron)
    blade.turn('y',random.uniform(-24,16))
    add('moulding cutter '+str(j),blade)
for j in range(15):
    plane('metal plane '+str(j),-2.55+j*.36,2.39,2.44,random.uniform(.28,.4),.15,random.uniform(-9,9),j%4==0)
for j in range(13):
    plane('wood plane '+str(j),-2.52+j*.42,2.40,1.82,random.uniform(.34,.47),.19,random.uniform(-8,8),True)
for j in range(10):
    plane('bottom plane '+str(j),-2.4+j*.52,2.39,1.21,random.uniform(.43,.58),.22,random.uniform(-7,7),True)
for k,z in enumerate(levels):
    for j in range(11):
        y=-1.05+j*.33
        if k==3:
            h=random.uniform(.18,.43)
            cube('right tall tool '+str((k,j)),(.23,.22,h),(2.78,y,z+.04+h/2),random.choice([oak,wood,darkwood]))
            b=box((.04,.10,.22),center=(2.73,y,z+.32),color=iron)
            b.turn('x',-20)
            add('side blade '+str(j),b)
        else:
            plane('side plane '+str((k,j)),2.78,y,z+.045,.35,.19,90,k!=0)
for z in (1.62,2.59,3.50):
    cube('window tool rail '+str(z),(.18,2.55,.06),(-2.72,.10,z),honey)
    for j in range(9):
        y=-1+j*.28
        h=random.uniform(.25,.48)
        cyl('window handle '+str((z,j)),(-2.69,y,z+.07),(-2.69,y,z+h),.045,random.choice([wood,oak,darkwood]))
        cyl('window blade '+str((z,j)),(-2.69,y,z-.18),(-2.69,y,z+.07),.012,steel)

def strip(n,x1,z1,x2,z2,w=.08,c=iron):
    seg(n,(x1-.16,2.637,z1),(x2-.16,2.637,z2),w,.027,c)
strip('great square left',-2.10,4.10,-1.18,5,.14)
strip('great square right',-1.18,5,-.15,3.96,.14)
strip('middle square left',-1.95,3.85,-1.20,4.60,.14)
strip('middle square right',-1.20,4.60,-.31,3.71,.14)
strip('small square left',-1.65,3.66,-1.15,4.15,.15)
strip('small square right',-1.15,4.15,-.55,3.55,.15)
strip('bright square edge',-2.09,4.12,-1.18,5.02,.014,steel)
strip('bright return',-1.17,4.96,-.17,3.96,.014,steel)
strip('tall square',.16,3.63,.16,4.90,.075)
strip('angled square',-.29,3.98,.16,4.70,.075)
strip('upper square upright',-.56,4.27,-.56,4.79,.075)
strip('upper square top',-.56,4.79,-.02,4.79,.075)
for i in range(13):
    x=-1.91+i*.065
    z=4.29+i*.065
    strip('etched graduation '+str(i),x,z,x+.023,z-.023,.007,cream)
for j,(x,z,h) in enumerate(((.78,4.9,.90),(.82,4.12,.53),(1.05,3.65,.33))):
    strip('divider left '+str(j),x,z,x-.19,z-h,.029,wood if j<2 else steel)
    strip('divider right '+str(j),x,z,x+.18,z-h,.029,wood if j<2 else steel)
    cyl('divider pivot '+str(j),(x-.16,2.61,z),(x-.16,2.57,z),.035,steel)
    strip('divider bridge '+str(j),x-.12,z-h*.69,x+.13,z-h*.69,.014,steel)
for j,(x,z) in enumerate(((1.52,4.36),(2.08,3.92))):
    cube('mallet handle '+str(j),(.065,.065,.76),(x,2.60,z),wood)
    cube('mallet head '+str(j),(.42,.12,.12),(x,2.58,z+.36),darkwood if j==0 else iron)
    cube('mallet heel '+str(j),(.24,.085,.075),(x-.04,2.59,z-.39),wood)
for j in range(5):
    strip('right wall blade '+str(j),2.48+j*.17,4.32+j*.14,2.85+j*.17,4.45+j*.14,.13,iron)
# Large wooden bow saw by the window.
cyl('saw rail',(-2.70,-.75,1.15),(-2.70,1.02,1.15),.045,oak)
cyl('saw blade',(-2.70,-.75,1.48),(-2.70,1.02,1.48),.009,iron)
for y in (-.75,1.02):
    cube('saw upright '+str(y),(.11,.11,.43),(-2.70,y,1.3),wood)

cube('bench top',(5.25,2.7,.16),(-.10,-1.25,.87),(.24,.17,.095))
for i in range(8):
    cube('bench seam '+str(i),(.009,2.65,.004),(-2.6+i*.69,-1.25,.953),(.09,.065,.035))
for x in (-2.25,2.05):
    cube('bench leg '+str(x),(.16,.17,.85),(x,-.75,.42),darkwood)
cube('back board',(2.85,.40,.13),(.24,-.02,1.08),oak)
cube('rear block',(.30,.42,.43),(1.30,-.03,1.17),oak)
cube('vise',(.25,.35,.38),(-1.92,-.60,.94),wood)
plane('rear bench plane',.35,-.08,1.16,1.05,.26,-5,True)
plane('left bench plane',-1.45,-1.22,.97,.85,.25,83,True)
plane('diagonal plane',.18,-.85,.97,.98,.26,17,True)
plane('black bench plane',1.73,-.16,.99,.70,.25,-11,False)
plane('foreground plane',-.53,-1.80,.97,.70,.23,12,True)
for j in range(14):
    x=random.uniform(-1.6,1.5)
    y=random.uniform(-2,-.3)
    o=box((random.uniform(.3,.95),.065,.035),center=(x,y,1.015),color=random.choice([oak,honey,wood]))
    o.turn('z',random.uniform(-65,65))
    add('wood strip '+str(j),o)
for j in range(15):
    x=-2.2+j*.105
    y=-1.52+random.uniform(-.17,.15)
    a=Asset('chisel '+str(j))
    a.include('blade',box((.05,.72,.022),center=(x,y-.30,1.02),color=steel))
    a.include('ridge',box((.015,.69,.009),center=(x,y-.30,1.037),color=(.43,.45,.41)))
    a.include('ferrule',rod(radius=.033,start=(x,y+.025,1.04),end=(x,y+.11,1.04),color=iron))
    a.include('handle',rod(radius=.046,start=(x,y+.1,1.04),end=(x,y+.4,1.04),color=random.choice([wood,oak,darkwood])))
    a.include('end',ball(radius=.047,center=(x,y+.4,1.04),color=oak))
    a.turn('z',random.uniform(-19,19),pivot=(x,y,1.02))
    scene.include('chisel '+str(j),a)

cyl('glue pot',(-.97,-.43,.97),(-.97,-.43,1.30),.18,(.025,.045,.037))
cyl('pot rim',(-.97,-.43,1.30),(-.97,-.43,1.33),.195,steel)
cyl('pot lid',(-.97,-.43,1.33),(-.97,-.43,1.36),.17,iron)
cyl('lid knob',(-.97,-.43,1.35),(-.97,-.43,1.41),.025,wood)
add('pot handle',sweep_tube(points=[(-1.15,-.43,1.22),(-1.15,-.43,1.56),(-.98,-.43,1.66),(-.80,-.43,1.55),(-.79,-.43,1.22)],radius=.012,color=steel))
cyl('bottle',(-.28,-.46,.98),(-.28,-.46,1.37),.105,(.28,.32,.23))
add('bottle shoulder',ball(radius=.105,center=(-.28,-.46,1.36),color=(.28,.32,.23)))
cyl('bottle neck',(-.28,-.46,1.37),(-.28,-.46,1.51),.045,(.4,.44,.32))
cyl('bottle stopper',(-.28,-.46,1.49),(-.28,-.46,1.53),.048,cream)
cube('bottle paper',(.14,.012,.19),(-.28,-.561,1.21),(.56,.54,.4))

tx,ty=.75,-1.65
cyl('tray base',(tx,ty,.98),(tx,ty,1.01),.43,(.075,.085,.077))
# A solid dark rim, with a few subtle seams.
add('tray outer rim',sweep_tube(points=[(tx+.425*math.cos(i*math.tau/64),ty+.425*math.sin(i*math.tau/64),1.12) for i in range(65)],radius=.047,color=(.105,.12,.107)))
for j in range(48):
    x=tx+random.uniform(-.29,.29)
    y=ty+random.uniform(-.29,.29)
    ang=random.random()*math.tau
    cyl('tray screw '+str(j),(x,y,1.04),(x+.12*math.cos(ang),y+.12*math.sin(ang),1.065),.007,(.37,.39,.35))
    if j%3==0:
        add('curled shaving '+str(j),sweep_tube(points=[(x+.037*math.cos(t*.7),y+.037*math.sin(t*.7),1.07+t*.002) for t in range(12)],radius=.006,color=(.43,.42,.31)))
for j,(x,y,ang) in enumerate(((1.57,-1.65,-28),(1.92,-1.15,23))):
    a=Asset('bench mallet '+str(j))
    a.include('handle',rod(radius=.035,start=(x,y-.45,1.04),end=(x,y+.3,1.04),color=honey))
    a.include('head',box((.39,.21,.19),center=(x,y+.23,1.09),color=oak))
    a.turn('z',ang,pivot=(x,y,1.04))
    scene.include('bench mallet '+str(j),a)
a=Asset('foreground square')
a.include('long arm',box((1.31,.09,.065),center=(1.31,-2.14,1.04),color=honey))
a.include('short arm',box((.11,.64,.065),center=(1.85,-1.87,1.04),color=honey))
a.turn('z',-20)
scene.include('foreground square',a)
for j in range(3):
    cube('gauge block '+str(j),(.27,.17,.14),(1.17+j*.31,-.77,1.05),random.choice([oak,darkwood,wood]))
    cyl('gauge stem '+str(j),(1.20+j*.28,-1.03,1.12),(1.20+j*.28,-.47,1.12),.025,oak)
for j in range(13):
    x=random.uniform(-2,1.7)
    y=random.uniform(-2.2,-.65)
    o=box((.19,.065,.007),center=(x,y,1.015),color=cream)
    o.turn('z',random.uniform(-30,30))
    add('paper tag '+str(j),o)
for j in range(12):
    x=random.uniform(-.9,.6)
    y=random.uniform(-2.1,-1.2)
    cyl('loose metal tool '+str(j),(x,y,1.04),(x+.36,y+.18,1.04),.012,steel)

realize(scene)
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and len(ob.data.polygons)<=12:
        m=ob.modifiers.new('Soft worn edges','BEVEL')
        m.width=.004
        m.segments=2
        ob.modifiers.new('Corner normals','WEIGHTED_NORMAL')

# Procedural grain and surface wear preserve the individual object colors.
for mat in bpy.data.materials:
    base=tuple(mat.diffuse_color)
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    if not bs:
        continue
    # SceneAct may already have assigned its color through the shader.
    current=tuple(bs.inputs['Base Color'].default_value)
    if max(current[:3])-min(current[:3])>.015 or max(current[:3])<.3:
        base=current
    bs.inputs['Base Color'].default_value=base
    bs.inputs['Roughness'].default_value=.77
    r,g,b=base[:3]
    if r>g*1.22 and g>b*1.25:
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=4
        tex.inputs['Detail'].default_value=3
        coord=nt.nodes.new('ShaderNodeTexCoord')
        mapping=nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(3,65,12)
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(r*.42,g*.4,b*.38,1)
        ramp.color_ramp.elements[1].position=.83
        ramp.color_ramp.elements[1].color=(r*1.12,g*1.1,b*1.06,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.19
        bump.inputs['Distance'].default_value=.012
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif max(base[:3])<.3:
        bs.inputs['Metallic'].default_value=.45
        bs.inputs['Roughness'].default_value=.5

set_view((-.35,-5.35,2.73),(0,1.18,2.12),lens=33,sensor=36)
area_emitter((-2.7,-.5,3.5),power=430,size=2.6,target=(0,1,1.6),color=(.79,.9,1))
area_emitter((.2,-2.4,4.7),power=240,size=3.5,target=(0,1,1.6),color=(1,.91,.78))
area_emitter((2,1,4.8),power=100,size=2.8,target=(0,.5,1.6))
world=bpy.data.worlds.new('Workshop ambient')
bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.25,.24,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.23
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=64
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=-.3
