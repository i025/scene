from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(28)
scene = Scene('Old woodworking tool room')
wood = (.34,.16,.055)
oak = (.52,.29,.105)
honey = (.65,.39,.15)
darkwood = (.22,.105,.038)
iron = (.095,.105,.10)
steel = (.32,.34,.31)
wall = (.78,.80,.75)

def B(parent, name, size, pos, col, rot=None):
    n = box(size=size, center=pos, color=col)
    if rot:
        n.turn(euler=rot)
    parent.include(name,n)
    return n

def R(parent,name,a,b,r,col):
    n=rod(radius=r,start=a,end=b,color=col)
    parent.include(name,n)
    return n

def T(parent,name,points,r,col):
    n=sweep_tube(points=points,radius=r,color=col)
    parent.include(name,n)
    return n

def tint(c):
    k=random.uniform(.78,1.15)
    return tuple(min(.9,v*k) for v in c)

room=Asset('white plaster and shelves')
B(room,'back plaster',(5.6,.12,4.6),(0,2.18,2.15),wall)
B(room,'left plaster',(.12,6.4,4.6),(-2.75,-.95,2.15),(.79,.81,.76))
B(room,'right plaster',(.12,6.4,4.6),(2.75,-.95,2.15),(.84,.84,.78))
B(room,'floor',(5.6,6.5,.12),(0,-.8,-.08),(.35,.32,.25))

# The tall window and narrow tool rack at the left edge.
B(room,'window dark reveal',(.035,2.0,2.9),(-2.673,.20,2.38),(.12,.17,.16))
for j in range(3):
    for k in range(2):
        B(room,'blue daylight pane%d%d'%(j,k),(.025,.61,1.32),
          (-2.643,-.44+j*.66,1.69+k*1.39),(.40,.60,.66))
for y in [-.78,-.12,.54,1.20]:
    B(room,'window vertical'+str(y),(.085,.045,2.9),(-2.60,y,2.38),(.68,.70,.63))
B(room,'window transom',(.09,2.02,.065),(-2.60,.20,2.36),(.73,.75,.69))
for z in [1.05,1.91,2.93]:
    B(room,'left rack '+str(z),(.20,2.45,.075),(-2.50,.24,z),honey)

levels=[1.03,1.52,2.07,2.70]
for idx,z in enumerate(levels):
    B(room,'back shelf %d'%idx,(5.25,.50,.078),(0,1.86,z),tint(honey))
    B(room,'back shelf front %d'%idx,(5.28,.035,.045),(0,1.595,z-.025),(.65,.40,.18))
    B(room,'right shelf %d'%idx,(.50,3.70,.08),(2.48,.10,z),tint(honey))
    B(room,'left shelf %d'%idx,(.38,1.55,.065),(-2.48,1.10,z),honey)
    for x in [-2.1,-.85,.65,2.05]:
        B(room,'bracket %s %s'%(idx,x),(.035,.07,.28),(x,2.08,z-.17),(.22,.22,.18))
        R(room,'bracket diagonal %s %s'%(idx,x),(x,2.08,z-.30),(x,1.70,z-.05),.016,iron)
for x in [-1.95,.95]:
    B(room,'upright shelf support'+str(x),(.045,.055,1.85),(x,2.07,1.77),(.30,.27,.19))
scene.include('room',room)

# Traditional wooden and iron hand planes, with separate soles, mouths,
# tilted irons, wedges and arched handles.
def plane(name,x,y,z,length=.40,width=.14,angle=0,metal=False):
    a=Asset(name)
    c=tint(random.choice([wood,oak,honey,darkwood]))
    B(a,'body',(length,width,.105),(0,0,.058),iron if metal else c)
    B(a,'sole',(length+.015,width+.008,.014),(0,0,.009),steel if metal else darkwood)
    B(a,'mouth',(.047,width*.86,.009),(.025,0,.116),(.07,.065,.045))
    B(a,'inclined blade',(.055,width*.69,.22),(.005,0,.175),steel,rot=(0,-29,0))
    B(a,'wedge',(.075,width*.63,.125),(.055,0,.14),tint(wood),rot=(0,-25,0))
    if metal:
        R(a,'front knob stem',(-length*.30,0,.11),(-length*.30,0,.18),.023,darkwood)
        a.include('front knob',ball(radius=.043,center=(-length*.30,0,.19),color=darkwood))
    else:
        B(a,'nose end',(.025,width*.96,.13),(-length*.46,0,.073),c)
    if length>.29:
        T(a,'arched rear tote',[(length*.22,0,.105),(length*.28,0,.21),
          (length*.36,0,.27),(length*.43,0,.245),(length*.44,0,.13)],.022,darkwood)
    a.turn('z',angle,pivot=(0,0,0))
    a.move((x,y,z))
    scene.include(name,a)

# Rows of wooden moulding planes fill the back wall.
for i in range(43):
    x=-2.48+i*.116
    a=Asset('upper moulding plane %02d'%i)
    h=random.uniform(.17,.30)
    c=tint(random.choice([wood,oak,honey,darkwood]))
    B(a,'narrow wooden stock',(.092,.33,h),(x,1.87,2.74+h/2),c,
      rot=(0,random.uniform(-8,8),random.uniform(-5,5)))
    B(a,'dark iron',(.043,.05,h+.10),(x,1.82,2.77+h/2),iron,rot=(0,-13,0))
    B(a,'end grain',(.080,.012,h*.70),(x,1.696,2.76+h*.43),tint(oak))
    scene.include(a.name,a)

for row,z in enumerate([1.56,2.11]):
    for i in range(12):
        x=-2.32+i*.40
        plane('back plane %d %d'%(row,i),x,1.79,z,
              random.uniform(.29,.44),random.uniform(.11,.17),
              random.uniform(-9,9),metal=(random.random()<.32))
for i in range(10):
    plane('lower long plane %d'%i,-2.26+i*.49,1.79,1.07,
          random.uniform(.40,.60),.18,random.uniform(-8,8),False)

# Side shelves recede toward the corner.
for row,z in enumerate(levels):
    for j in range(9):
        y=-1.49+j*.405
        plane('right wall plane %d %d'%(row,j),2.43,y,z+.045,
              random.uniform(.30,.49),.17,90+random.uniform(-7,7),
              metal=(row<3 and random.random()<.35))
for z in [2.77,3.02]:
    for j in range(5):
        y=-1.0+j*.43
        B(room,'high wood block %s %s'%(z,j),(.26,.30,random.uniform(.15,.29)),
          (2.47,y,z),tint(oak))

# Chisels: blades and rounded wooden handles.
def chisel(parent,name,p,length=.48,angle=0):
    x,y,z=p
    a=Asset(name)
    R(a,'steel shaft',(0,0,0),(0,0,length*.48),.012,steel)
    B(a,'flat blade',(.042,.009,length*.19),(0,0,length*.075),steel)
    R(a,'ferrule',(0,0,length*.48),(0,0,length*.54),.025,(.40,.36,.22))
    R(a,'wood handle',(0,0,length*.54),(0,0,length*.90),.034,tint(wood))
    a.include('rounded handle end',ball(radius=.034,center=(0,0,length*.90),color=wood))
    a.turn('y',angle,pivot=(0,0,0))
    a.move(p)
    parent.include(name,a)

rack=Asset('left window chisels')
for row,z in enumerate([1.12,2.00,2.99]):
    for j in range(10):
        y=-.81+j*.205
        chisel(rack,'rack chisel %d %d'%(row,j),(-2.44,y,z),random.uniform(.39,.67),
               random.uniform(-8,8))
scene.include('window tools',rack)

# Large hanging carpenter's squares on the exposed upper wall.
decor=Asset('hanging wall tools')
def segment(name,p,q,w,col,depth=.025):
    x1,z1=p; x2,z2=q
    dx=x2-x1; dz=z2-z1
    n=B(decor,name,(math.hypot(dx,dz),depth,w),
        ((x1+x2)/2,2.082,(z1+z2)/2),col)
    n.turn('y',-math.degrees(math.atan2(dz,dx)))
    return n

for i in range(3):
    x=-1.89+i*.28
    z=3.58-i*.16
    segment('square rising%d'%i,(x-.35,z-.30),(x+.34,z+.41),.105,iron)
    segment('square falling%d'%i,(x+.34,z+.41),(x+1.10,z-.30),.105,iron)
    segment('square pale inset%d'%i,(x-.29,z-.28),(x+.34,z+.35),.016,(.58,.58,.50))
segment('slim square 1',(-.17,3.23),(.28,4.10),.065,iron)
segment('slim square 2',(.28,4.10),(.28,3.21),.065,iron)
segment('divider left',(.54,3.22),(.81,4.05),.034,darkwood)
segment('divider right',(.81,4.05),(1.10,3.22),.034,darkwood)
segment('small divider left',(.67,3.16),(.82,3.56),.025,iron)
segment('small divider right',(.82,3.56),(.98,3.16),.025,iron)
for x in [.76,.84,.92]:
    R(decor,'compass point'+str(x),(x,2.06,3.09),(x+.07,2.06,3.29),.009,(.44,.38,.20))
B(decor,'hanging mallet handle',(.063,.08,.77),(1.40,2.04,3.61),wood)
B(decor,'mallet head',(.32,.13,.13),(1.40,2.02,3.99),darkwood)
B(decor,'mallet lower end',(.15,.12,.09),(1.40,2.01,3.23),wood)
B(decor,'black hammer handle',(.045,.07,.53),(1.84,2.03,3.22),wood)
B(decor,'black hammer head',(.40,.10,.085),(1.84,2.01,3.48),iron)
# Fine hanging rulers and small labels.
for x in [-.52,-.38]:
    B(decor,'ruler'+str(x),(.035,.016,.64),(x,2.06,3.32),(.49,.51,.47),rot=(0,0,0))
    for k in range(16):
        B(decor,'ruler mark %s %s'%(x,k),(.023,.008,.004),(x,2.045,3.02+k*.037),iron)
B(decor,'yellow paper notice',(.25,.015,.25),(-1.16,2.04,2.99),(.82,.59,.16),rot=(0,-9,0))
for k in range(5):
    B(decor,'notice text'+str(k),(.16,.006,.009),(-1.16,2.025,3.06-k*.027),(.22,.17,.085))
scene.include('wall collection',decor)

# Foreground workbench, occupying the whole lower frame.
bench=Asset('crowded workbench')
B(bench,'thick plank top',(4.90,2.16,.16),(0,-1.38,.87),(.39,.25,.12))
for x in [-2.22,-.92,.45,1.91]:
    B(bench,'plank joint'+str(x),(.008,2.13,.005),(x,-1.38,.953),(.15,.105,.055))
for x in [-2.07,2.07]:
    for y in [-2.15,-.65]:
        B(bench,'bench leg %s %s'%(x,y),(.17,.18,.88),(x,y,.40),wood)
B(bench,'front apron',(4.8,.11,.32),(0,-2.40,.70),darkwood)
scene.include('workbench',bench)

# Several large bench planes and loose timber at the rear of the table.
for i,(x,y,angle,l) in enumerate([(-1.50,-.73,-8,.72),(-.52,-.57,2,.76),
 (.39,-.64,4,.85),(1.24,-.67,-15,.60),(.44,-1.27,9,.76),
 (-1.39,-1.45,-59,.57)]):
    plane('worktop wooden plane'+str(i),x,y,.96,l,.22,angle,i==5)
for i in range(7):
    B(bench,'stacked wood strip'+str(i),(random.uniform(.35,.90),.10,.045),
      (-.1+random.uniform(-.5,.5),-.93+random.uniform(-.2,.2),1.08+i*.033),
      tint(oak),rot=(0,0,random.uniform(-9,9)))

# Upright wooden plane body and a blocky carpenter's mallet on the right.
B(bench,'standing plane body',(.25,.27,.53),(1.30,-1.02,1.22),oak,rot=(0,-8,-9))
B(bench,'standing plane blade',(.08,.19,.27),(1.29,-1.02,1.54),iron,rot=(0,-22,-9))
R(bench,'mallet long shaft',(1.83,-2.35,.99),(1.40,-1.49,1.04),.042,honey)
B(bench,'mallet block head',(.56,.20,.21),(1.42,-1.51,1.08),honey,rot=(0,0,-30))
R(bench,'loose wooden handle',(.73,-2.23,.99),(1.28,-1.78,1.00),.035,oak)

# Flat steel saws, files, chisels and measuring rules cover the left foreground.
for i in range(9):
    x=-2.15+i*.23
    y=-1.87+random.uniform(-.18,.15)
    a=Asset('foreground chisel'+str(i))
    chisel(a,'tool',(0,0,0),random.uniform(.52,.83))
    a.turn('x',80,pivot=(0,0,0))
    a.turn('z',random.uniform(-24,24),pivot=(0,0,0))
    a.move((x,y,1.00))
    scene.include(a.name,a)
for i in range(4):
    n=B(bench,'flat saw blade'+str(i),(.17,.91,.012),
        (-1.42+i*.25,-1.64,1.035+i*.013),(.35,.37,.34),rot=(0,0,16-i*8))
    for j in range(12):
        B(bench,'saw teeth %d %d'%(i,j),(.025,.018,.012),
          (-1.51+i*.25,-2.03+j*.055,1.04+i*.013),steel,rot=(0,0,35))
for i in range(3):
    B(bench,'folding ruler section'+str(i),(.72,.037,.018),
      (-.34+i*.04,-2.11+i*.07,1.02+i*.023),(.68,.58,.34),rot=(0,0,11))
for i in range(20):
    B(bench,'rule tick'+str(i),(.008,.025,.004),(-.65+i*.032,-2.10,1.067),darkwood)

# Oil can, bottle, and the shallow trays of bright screws.
can=Asset('black oil can')
R(can,'can body',(-.70,-1.13,.98),(-.70,-1.13,1.34),.135,(.105,.14,.13))
R(can,'lid',(-.70,-1.13,1.34),(-.70,-1.13,1.37),.144,steel)
T(can,'wire bail',[(-.83,-1.13,1.34),(-.84,-1.13,1.55),(-.70,-1.13,1.65),
                   (-.56,-1.13,1.55),(-.56,-1.13,1.34)],.012,steel)
T(can,'spout',[(-.61,-1.13,1.35),(-.45,-1.10,1.46),(-.40,-1.09,1.58)],.022,steel)
scene.include('oil can',can)
R(bench,'bottle body',(.03,-1.19,.98),(.03,-1.19,1.36),.080,(.51,.54,.44))
R(bench,'bottle neck',(.03,-1.19,1.36),(.03,-1.19,1.46),.037,(.56,.57,.46))
R(bench,'bottle cork',(.03,-1.19,1.46),(.03,-1.19,1.49),.039,(.45,.32,.19))
B(bench,'bottle paper label',(.112,.012,.17),(.03,-1.272,1.18),(.73,.69,.54))
for k in range(5):
    B(bench,'faded label text'+str(k),(.08,.005,.005),(.03,-1.281,1.23-k*.022),(.35,.35,.27))

for ti,(cx,cy) in enumerate([(.85,-1.94),(1.05,-1.57)]):
    B(bench,'parts tray bottom'+str(ti),(.57,.41,.035),(cx,cy,1.015),(.18,.20,.18),rot=(0,0,-12))
    for sx in [-1,1]:
        B(bench,'tray end %d %d'%(ti,sx),(.035,.43,.105),(cx+sx*.28,cy,1.065),steel)
    for sy in [-1,1]:
        B(bench,'tray side %d %d'%(ti,sy),(.57,.026,.105),(cx,cy+sy*.205,1.065),steel)
    for j in range(48):
        x=cx+random.uniform(-.24,.24)
        y=cy+random.uniform(-.16,.16)
        z=1.05+random.uniform(.005,.065)
        ang=random.uniform(0,math.tau)
        ln=random.uniform(.045,.12)
        R(bench,'screw %d %d'%(ti,j),(x,y,z),(x+ln*math.cos(ang),y+ln*math.sin(ang),z+.01),.0055,(.49,.51,.48))
        R(bench,'screw head %d %d'%(ti,j),(x,y,z-.003),(x,y,z+.007),.012,steel)
# Scattered steel pieces and small shavings.
for j in range(32):
    x=random.uniform(-2.1,2.1); y=random.uniform(-2.30,-.67)
    if random.random()<.5:
        R(bench,'loose nail'+str(j),(x,y,.99),(x+.11,y+.04,1.005),.006,steel)
    else:
        T(bench,'wood shaving'+str(j),[(x,y,.975),(x+.05,y+.02,.989),
          (x+.08,y+.065,1.01),(x+.04,y+.09,1.02)],.009,(.61,.43,.21))

# Tiny pale museum inventory tickets on shelf edges.
labels=Asset('small shelf labels')
for z in levels:
    for x in [-2.12,-1.22,-.25,.84,1.93]:
        B(labels,'ticket %s %s'%(z,x),(.16,.009,.035),(x,1.567,z-.01),(.83,.81,.65))
        for k in range(4):
            B(labels,'print %s %s %s'%(z,x,k),(.018,.004,.006),
              (x-.048+k*.03,1.560,z-.01),(.23,.24,.20))
scene.include('inventory tickets',labels)

realize(scene)

# Subtle, three-dimensional material variation gives the old wood and iron
# their uneven surfaces without using any image textures.
for mat in bpy.data.materials:
    col=mat.diffuse_color
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:
        continue
    bs.inputs['Roughness'].default_value=.72
    r,g,b=col[:3]
    if r>g*1.18 and g>b*1.18:
        nt=mat.node_tree
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=3
        mapping=nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(2,30,5)
        coord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(r*.58,g*.56,b*.53,1)
        ramp.color_ramp.elements[1].position=.84
        ramp.color_ramp.elements[1].color=(min(r*1.24,1),min(g*1.23,1),min(b*1.22,1),1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.17
        bump.inputs['Distance'].default_value=.018
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    elif max(r,g,b)-min(r,g,b)<.09 and r<.57:
        bs.inputs['Metallic'].default_value=.62
        bs.inputs['Roughness'].default_value=.43

set_view((-.12,-4.95,2.65),(0,1.03,2.03),lens=31,sensor=36)
area_emitter((-3.0,-1.0,3.7),power=1150,size=3.2,target=(0,.7,1.6),color=(.84,.93,1.0))
area_emitter((.3,-2.0,4.6),power=650,size=4.0,target=(0,1.2,1.7),color=(1.0,.91,.76))
area_emitter((2.0,1.0,4.1),power=250,size=2.4,target=(0,0,1.2))
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.world.color=(.25,.25,.23)
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
