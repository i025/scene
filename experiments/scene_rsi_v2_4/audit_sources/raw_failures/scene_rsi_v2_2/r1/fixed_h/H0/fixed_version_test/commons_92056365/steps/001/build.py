from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(12)
scene = Scene('Window dining room')
ivory=(.82,.83,.79)
dark=(.075,.085,.072)
fabric=(.32,.35,.31)
metal=(.57,.59,.55)

def add(name,node):
    scene.include(name,node)

add('floor',box((11,17,.16),center=(0,1.5,-.1),color=(.24,.26,.23)))
# Narrow rectangular floor tiles.
for x in range(27):
    xx=-5.3+x*.4
    add('floor joint x'+str(x),box((.012,17,.004),center=(xx,1.5,-.014),color=(.43,.44,.4)))
for j in range(28):
    yy=-6.5+j*.61
    for i in range(27):
        xx=-5.1+i*.4
        add('tile end%d_%d'%(j,i),box((.39,.009,.004),center=(xx,yy+(i%2)*.305,-.013),color=(.40,.42,.38)))

add('ceiling',box((11,17,.13),center=(0,1.5,3.53),color=(.88,.89,.85)))
for i in range(83):
    add('ceiling seam'+str(i),box((11,.012,.008),center=(0,-6.7+i*.2,3.458),color=(.60,.62,.58)))

# Rear and right glazing, with opaque lower panels and narrow metal frames.
add('rear base',box((10.4,.18,.91),center=(0,8.1,.445),color=(.66,.69,.63)))
add('rear sill',box((10.5,.3,.09),center=(0,8.02,.94),color=(.42,.45,.4)))
add('rear header',box((10.5,.19,.18),center=(0,8.10,3.16),color=(.51,.54,.48)))
for i,x in enumerate([-5.1,-3.4,-1.7,0,1.7,3.4,5.1]):
    add('rear mullion'+str(i),box((.065,.14,2.22),center=(x,8.06,2.07),color=(.34,.39,.33)))
add('right base',box((.18,15,.88),center=(5.1,.6,.44),color=(.73,.75,.69)))
add('right sill',box((.29,15,.08),center=(5.04,.6,.94),color=(.43,.47,.40)))
add('right header',box((.16,15,.16),center=(5.1,.6,3.2),color=(.53,.57,.49)))
for i,y in enumerate([-6,-3.8,-1.6,.6,2.8,5,7.2,8.1]):
    add('right post'+str(i),box((.13,.065,2.27),center=(5.05,y,2.08),color=(.42,.47,.39)))
# Pale outdoor architecture and foliage beyond the open glazing.
add('outside ground',box((45,40,.15),center=(0,16,-.25),color=(.86,.88,.82)))
add('distant facade',box((22,.2,2.9),center=(0,15,1.3),color=(.86,.87,.82)))
for i in range(16):
    x=random.uniform(-12,12)
    y=random.uniform(10,14)
    z=random.uniform(1.8,3.4)
    add('outside trunk'+str(i),rod(.035,start=(x,y,0),end=(x,y,z),color=(.55,.59,.49)))
    for j in range(5):
        n=ball(random.uniform(.45,.85),center=(x+random.uniform(-.7,.7),y+random.uniform(-.5,.5),z+random.uniform(-.3,.5)),color=(.68,.72,.61))
        add('outside canopy%d_%d'%(i,j),n)

def pedestal(asset,name,x,y,height=.56):
    asset.include(name+'foot',rod(.29,length=.075,center=(x,y,.055),color=metal))
    asset.include(name+'column',rod(.075,length=height-.07,center=(x,y,(height+.07)/2),color=metal))

def chair(name,x,y,facing=1,width=.91):
    a=Asset(name)
    pedestal(a,'base',x,y)
    a.include('seat',box((width,.69,.15),center=(x,y,.61),color=fabric))
    a.include('back',box((width,.115,.83),center=(x,y-facing*.33,1.005),color=fabric))
    for s in [-1,1]:
        a.include('side'+str(s),box((.085,.69,.54),center=(x+s*(width/2-.04),y,.89),color=(.36,.39,.34)))
        a.include('edge'+str(s),box((.019,.72,.021),center=(x+s*width/2,y,1.17),color=(.64,.66,.60)))
    add(name,a)

def table(name,x,y,w=1.35,d=.86):
    a=Asset(name)
    a.include('top',box((w,d,.065),center=(x,y,.88),color=(.68,.70,.64)))
    a.include('edge',box((w+.025,d+.025,.035),center=(x,y,.85),color=(.31,.34,.29)))
    for xx in [x-w*.32,x+w*.32]:
        a.include('leg'+str(xx),box((.045,.055,.82),center=(xx,y,.42),color=(.55,.58,.51)))
        a.include('foot'+str(xx),rod(.14,length=.035,center=(xx,y,.025),color=metal))
    a.include('sugar',box((.12,.10,.12),center=(x+.13,y,.972),color=(.87,.87,.81)))
    a.include('ashtray',rod(.085,length=.022,center=(x-.18,y-.05,.927),color=(.77,.79,.72)))
    add(name,a)

# Two banks of compact upholstered pedestal seats.
for row,y in enumerate([-2.0,.5,3.0,5.5]):
    table('right table'+str(row),2.87,y,1.48,.89)
    chair('right near'+str(row),2.88,y-.88,1,1.04)
    chair('right far'+str(row),2.88,y+.87,-1,1.04)
    table('middle table'+str(row),.35,y+.35,1.25,.82)
    chair('middle near'+str(row),.34,y-.45,1,.92)
    chair('middle far'+str(row),.34,y+1.14,-1,.92)

# Broad booth benches on the left, their backs stepping into the distance.
for row,y in enumerate([-3.65,-1.05,1.55,4.15,6.55]):
    width=2.12
    a=Asset('left booth'+str(row))
    a.include('back',box((width,.16,.95),center=(-3.17,y-.42,.98),color=(.29,.33,.29)))
    a.include('seat',box((width,.76,.18),center=(-3.17,y,.56),color=(.37,.40,.34)))
    for s in [-1,1]:
        a.include('arm'+str(s),box((.1,.83,.60),center=(-3.17+s*1.01,y,.83),color=(.39,.42,.36)))
    for xx in [-3.85,-2.5]:
        pedestal(a,str(xx),xx,y,.46)
    add('left booth'+str(row),a)
    table('left table'+str(row),-3.17,y+.77,2.14,1.02)

# A cropped table in the immediate foreground.
table('foreground table',-2.65,-5.35,2.75,1.30)

def pendant(name,x,y,scale=1):
    z=2.73
    a=Asset(name)
    # Hollow hemispherical metal reflector, with an open white underside.
    outer=ball(.43*scale,center=(x,y,z),color=dark)
    inner=ball(.402*scale,center=(x,y,z-.018*scale),color=(.78,.8,.72))
    cutter=box((2*scale,2*scale,1.1*scale),center=(x,y,z-.55*scale))
    shade=subtract(outer,inner,cutter)
    a.include('shade',shade)
    a.include('rim',rod(.43*scale,length=.022*scale,center=(x,y,z+.005),color=dark))
    a.include('underside',rod(.396*scale,length=.008,center=(x,y,z-.009),color=(.86,.88,.79)))
    a.include('neck',rod(.145*scale,length=.32*scale,center=(x,y,z+.43*scale),color=dark))
    a.include('neck band',rod(.149*scale,length=.025,center=(x,y,z+.44*scale),color=(.47,.50,.43)))
    top=z+.59*scale
    a.include('wire',rod(.008,start=(x,y,top),end=(x,y,3.46),color=(.18,.21,.17)))
    a.include('ceiling rose',rod(.085*scale,length=.018,center=(x,y,3.451),color=dark))
    add(name,a)

for i,(x,y,s) in enumerate([
    (-3.6,-3.15,1.22),(-3.15,.35,.87),(-3.15,3.1,.75),(-3.15,5.7,.69),
    (.2,-.05,.83),(.2,3.0,.74),(.2,5.9,.67),
    (3.2,-.2,1.0),(3.2,2.7,.79),(3.2,5.8,.7),(4.65,3.8,.7)
]):
    pendant('pendant'+str(i),x,y,s)

# Recessed round ceiling fittings.
for x in [-2.3,1.5,4]:
    for y in [-3,1.5,5.5]:
        add('ceiling fitting%s%s'%(x,y),rod(.10,length=.012,center=(x,y,3.447),color=(.54,.57,.50)))

def ellipsoid_between(name,a,b,width,color):
    av,bv=Vector(a),Vector(b)
    delta=bv-av
    n=ball(1,center=(0,0,0),color=color)
    n.resize((width,width*.32,delta.length/2))
    n.turn('y',math.degrees(math.acos(delta.z/delta.length)),pivot=(0,0,0))
    n.turn('z',math.degrees(math.atan2(delta.y,delta.x)),pivot=(0,0,0))
    n.move(tuple((av+bv)/2))
    add(name,n)

# Tall palm at the near right edge.
plantx,planty=4.37,-2.7
add('palm planter',rod(.38,length=.57,center=(plantx,planty,.285),color=(.18,.22,.16)))
for k in range(15):
    ang=random.uniform(0,2*math.pi)
    h=random.uniform(1.6,2.55)
    reach=random.uniform(.75,1.45)
    points=[]
    for j in range(9):
        t=j/8
        points.append((plantx+math.cos(ang)*reach*t,planty+math.sin(ang)*reach*t,.42+h*(1-(1-t)**2)-.5*t*t))
    add('palm stem'+str(k),sweep_tube(points=points,radius=.012,color=(.13,.19,.11)))
    for j in range(2,9):
        t=j/8
        base=Vector(points[j])
        for side in [-1,1]:
            sideways=Vector((-math.sin(ang),math.cos(ang),0))*side
            end=base+sideways*(.32*(1-t)+.14)+Vector((math.cos(ang)*.17,math.sin(ang)*.17,-.16))
            ellipsoid_between('leaf%d_%d_%d'%(k,j,side),tuple(base),tuple(end),.043,(.095,.15,.075))

# Low planting along the rear seating.
for i in range(16):
    x=-1.9+i*.19
    y=6.85+random.uniform(-.15,.15)
    h=random.uniform(.8,1.35)
    add('rear foliage stem'+str(i),rod(.012,start=(x,y,.62),end=(x,y,h),color=(.22,.29,.17)))
    for j in range(3):
        p=(x,y,h-j*.12)
        q=(x+random.uniform(-.25,.25),y+random.uniform(-.16,.16),h+.13-j*.1)
        ellipsoid_between('rear leaf%d_%d'%(i,j),p,q,.075,(.28,.35,.23))

realize(scene)
set_view((-4.0,-7.4,2.15),(-.1,4.0,1.72),lens=33,sensor=36)
area_emitter((0,7.7,2.8),power=1900,size=8,target=(0,0,.5),color=(1,1,.96))
area_emitter((4.8,1.5,2.6),power=1600,size=7,target=(-2,1,1),color=(1,1,.97))
area_emitter((-1,-3,3.35),power=320,size=5,target=(0,2,.4))

world=bpy.context.scene.world
world.color=(.78,.78,.75)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=32
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=379
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.exposure=.45
bpy.context.scene.camera.data.lens=33
# The source is an archival monochrome photograph.
bpy.context.scene.use_nodes=True
tree=bpy.context.scene.node_tree
tree.nodes.clear()
rl=tree.nodes.new('CompositorNodeRLayers')
bw=tree.nodes.new('CompositorNodeRGBToBW')
out=tree.nodes.new('CompositorNodeComposite')
tree.links.new(rl.outputs['Image'],bw.inputs[0])
tree.links.new(bw.outputs[0],out.inputs[0])
