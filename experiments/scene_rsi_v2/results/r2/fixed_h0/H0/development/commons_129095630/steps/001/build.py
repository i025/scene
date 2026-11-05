import bpy, math, random
from sceneact import *
random.seed(24)

scene = Scene('Old craft workshop')
wood = (.34,.19,.085)
oak = (.48,.30,.14)
lightwood = (.58,.40,.22)
edgewood = (.39,.25,.13)
steel = (.29,.34,.34)
brightsteel = (.49,.54,.53)
darksteel = (.10,.14,.14)
brass = (.36,.31,.16)

def put(name, node):
    scene.include(name, node)
    return node

def cube(name, size, pos, col):
    return put(name, box(size=size, center=pos, color=col))

def line(name, a, b, r=.008, col=steel):
    return put(name, rod(radius=r, start=a, end=b, color=col))

def tube(name, points, r=.008, col=steel):
    return put(name, sweep_tube(points=points, radius=r, color=col))

def ring(name, center, radius, col=steel, thickness=.007, plane='xy', squash=1):
    x,y,z=center
    pts=[]
    for j in range(41):
        a=j*math.tau/40
        if plane=='xy':
            p=(x+radius*math.cos(a),y+radius*squash*math.sin(a),z)
        elif plane=='xz':
            p=(x+radius*math.cos(a),y,z+radius*squash*math.sin(a))
        else:
            p=(x,y+radius*math.cos(a),z+radius*squash*math.sin(a))
        pts.append(p)
    return tube(name,pts,thickness,col)

# Planked floor and vertical tongue-and-groove wall.
for j in range(16):
    x=-2.1+j*.28
    cube('floor plank %02d'%j,(.275,4.4,.065),(x,-.55,-.045),
         (.30+random.random()*.10,.19+random.random()*.06,.10+random.random()*.04))
    for k in range(4):
        xx=x+random.uniform(-.12,.12)
        line('floor grain',(xx,-2.7,.001),(xx,1.4,.001),.0008,(.22,.135,.07))
for j in range(17):
    x=-2.35+j*.29
    c=(random.uniform(.32,.45),random.uniform(.17,.25),random.uniform(.075,.12))
    cube('wall board %02d'%j,(.284,.08,3.3),(x,.69,1.55),c)
    for k in range(7):
        xx=x+random.uniform(-.135,.135)
        line('wall grain',(xx,.645,0),(xx+random.uniform(-.012,.012),.645,3.15),
             random.uniform(.0007,.0016),(.22,.115,.05))
    for z in (.6,1.85,2.45):
        if random.random()<.7:
            knot=ball(.014,center=(x+random.uniform(-.09,.09),.636,z),color=(.105,.06,.025))
            knot.resize((1,.2,1.35))
            put('wood knot',knot)
cube('baseboard',(4.7,.07,.13),(0,.59,.08),wood)

# The main old wooden workbench.
cube('thick bench slab',(2.35,1.00,.11),(0,.025,1.23),lightwood)
cube('front worn rail',(2.36,.07,.09),(0,-.483,1.205),oak)
cube('rear rim',(2.35,.055,.055),(0,.49,1.29),edgewood)
for x in (-1.04,1.04):
    for y in (-.34,.40):
        cube('bench leg',(.095,.105,1.15),(x,y,.58),oak)
        cube('leg worn corner',(.015,.11,.89),(x-.035,y,.61),lightwood)
cube('back lower stretcher',(2.12,.07,.12),(0,.39,.28),wood)
for x in (-.69,.69):
    cube('drawer partition',(.055,.84,.79),(x,.01,.79),wood)
cube('left side carcass',(.055,.88,.82),(-1.105,.01,.79),oak)
cube('right side carcass',(.055,.88,.82),(1.105,.01,.79),oak)

# Weathered bench top: thin strips, scratches, dark stains.
for j in range(12):
    y=-.43+j*.079
    line('top board seam',(-1.16,y,1.287),(1.16,y,1.287),.0017,(.22,.18,.12))
for j in range(170):
    x=random.uniform(-1.16,1.16)
    y=random.uniform(-.45,.47)
    length=random.uniform(.015,.12)
    line('table scratches',(x,y,1.288),(min(x+length,1.16),y+random.uniform(-.008,.008),1.288),
         random.uniform(.0005,.0013), random.choice([(.65,.51,.33),(.28,.25,.19),(.43,.38,.28)]))
for j in range(45):
    x=random.uniform(-1.16,1.16)
    cube('chipped front edge',(random.uniform(.009,.07),.005,random.uniform(.006,.026)),
         (x,-.521,1.23+random.uniform(-.04,.04)),random.choice([lightwood,wood,(.68,.50,.29)]))

def drawer(name,x,z,w,depth,front_y):
    # Hollow open drawer with its interior exposed to the camera.
    cube(name+' bottom',(w,depth,.026),(x,front_y+depth/2,z-.035),(.32,.23,.13))
    cube(name+' front',(w+.035,.052,.145),(x,front_y,z),oak)
    cube(name+' left',(.027,depth,.135),(x-w/2,front_y+depth/2,z+.005),lightwood)
    cube(name+' right',(.027,depth,.135),(x+w/2,front_y+depth/2,z+.005),lightwood)
    cube(name+' rear',(w,.028,.12),(x,front_y+depth,z),wood)
    for k in range(13):
        xx=x+random.uniform(-w/2,w/2)
        cube('drawer patina',(random.uniform(.004,.024),.002,random.uniform(.015,.07)),
             (xx,front_y-.027,z+random.uniform(-.055,.055)),random.choice([lightwood,wood]))
    for xx in (x-.065,x+.065):
        put('handle fixing',rod(radius=.015,length=.009,center=(xx,front_y-.032,z),axis='+y',color=darksteel))
    tube('iron drop handle',[(x-.065,front_y-.045,z),(x-.052,front_y-.06,z-.042),
                            (x,front_y-.065,z-.052),(x+.052,front_y-.06,z-.042),
                            (x+.065,front_y-.045,z)],.008,darksteel)
    return front_y

drawer('upper left drawer',-.885,1.055,.49,.53,-.66)
drawer('middle left drawer',-.885,.785,.49,.49,-.64)
drawer('bottom left drawer',-.885,.405,.49,.52,-.67)
drawer('wide middle drawer',0,.97,1.22,.59,-.76)
drawer('upper right drawer',.89,1.055,.48,.51,-.61)
drawer('bottom right drawer',.90,.63,.48,.51,-.64)

# Interior dividers and assorted material in the drawers.
for x in (-1.03,-.90,-.76):
    cube('left drawer divider',(.018,.43,.055),(x,-.40,1.055),wood)
for j in range(21):
    x=random.uniform(-1.08,-.70)
    y=random.uniform(-.60,-.19)
    line('small drawer tools',(x,y,1.108),(x+.035,y+.10,1.11),.006,
         random.choice([steel,brass,wood]))
for j in range(9):
    x=-1.075+j*.046
    cube('paper packets',(.033,.25,.10),(x,-.40,.438),(.64,.55,.37))
for j in range(9):
    x=-.54+j*.13
    y=-.45+random.uniform(-.04,.04)
    z=1.035
    line('drawer chisel shaft',(x,-.70,z),(x+.025,-.27,z+.035),.012,steel)
    line('drawer wooden grip',(x,-.43,z+.03),(x+.02,-.25,z+.05),
         .027,random.choice([wood,oak,(.57,.34,.15)]))
    ring('grip ferrule',(x,-.43,z+.03),.029,brass,.004,plane='xz')
for j in range(34):
    x=random.uniform(.70,1.08)
    y=random.uniform(-.57,-.18)
    line('right drawer metal pieces',(x,y,1.11),(x+.025,y+.035,1.115),.0035,steel)
cube('folded cloth in bottom drawer',(.30,.27,.045),(.89,-.38,.70),(.63,.60,.48))
cube('paper in right lower drawer',(.16,.25,.015),(.95,-.43,.725),(.73,.68,.53))

# Tall two-tier, dark iron compartmented rotating organizer.
tx,ty=.48,.265
for level,radius in [(1.45,.24),(1.73,.255)]:
    disk=ball(1,center=(tx,ty,level),color=(.065,.105,.112))
    disk.resize((radius,radius,.035))
    put('carousel circular tray',disk)
    ring('carousel rolled rim',(tx,ty,level+.055),radius,(.21,.30,.31),.010)
    ring('carousel bottom rim',(tx,ty,level-.01),radius*.91,(.13,.20,.21),.006)
    for k in range(8):
        a=k*math.tau/8
        p=(tx+radius*math.cos(a),ty+radius*math.sin(a),level+.055)
        line('tray radial partitions',(tx,ty,level+.055),p,.008,(.16,.24,.25))
        line('tray outer wall',(p[0],p[1],level-.005),p,.009,(.13,.19,.20))
    for k in range(18):
        a=random.random()*math.tau
        rr=random.uniform(.07,radius*.8)
        line('tray hardware',(tx+rr*math.cos(a),ty+rr*math.sin(a),level+.025),
             (tx+rr*math.cos(a)+.018,ty+rr*math.sin(a)+.015,level+.034),.004,steel)
line('carousel central spindle',(tx,ty,1.29),(tx,ty,1.88),.016,steel)
tube('carousel loop handle',[(tx-.025,ty,1.82),(tx-.016,ty,1.94),
                            (tx+.025,ty,1.975),(tx+.055,ty,1.955),
                            (tx+.047,ty,1.90),(tx+.012,ty,1.85)],.009,(.22,.35,.38))

# Two old oil cans at the back left.
for x,y in [(-.96,.30),(-.67,.32)]:
    base=ball(.105,center=(x,y,1.33),color=(.29,.29,.13))
    base.resize((1,1,.62))
    put('oil can rounded reservoir',base)
    ring('oil can bottom seam',(x,y,1.286),.096,brass,.006)
    put('oil can collar',rod(radius=.045,length=.026,center=(x,y,1.395),color=steel))
    # Narrow tapered-looking spouts formed by nested rods.
    line('oil can spout',(x,y,1.405),(x-.021,y+.002,1.545),.018,darksteel)
    line('oil can spout tip',(x-.021,y+.002,1.53),(x-.03,y,1.585),.009,steel)
    for j in range(8):
        a=random.random()*math.tau
        line('oil can tarnish',(x+.08*math.cos(a),y+.08*math.sin(a),1.33),
             (x+.075*math.cos(a),y+.075*math.sin(a),1.36),.004,(.46,.40,.20))

# Cylindrical open metal cup.
cx,cy=-.46,.08
put('cup base',rod(radius=.064,length=.012,center=(cx,cy,1.292),color=brass))
ring('cup rim',(cx,cy,1.43),.063,brass,.006)
for j in range(36):
    a=j*math.tau/36
    line('cup wall',(cx+.060*math.cos(a),cy+.060*math.sin(a),1.30),
         (cx+.060*math.cos(a),cy+.060*math.sin(a),1.426),.0055,(.29,.29,.20))
ring('cup foot',(cx,cy,1.30),.066,steel,.005)

# Flat tabletop pliers, scissors, dividers, nippers.
def pliers(name,x,y,length=.31,angle=0):
    a=math.radians(angle)
    def p(dx,dy,dz=0):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),1.303+dz)
    for side in (-1,1):
        tube(name+' curved arm',[p(side*.035,-length*.54),
             p(side*.046,-length*.32),p(side*.016,-.015),
             p(-side*.022,length*.27),p(-side*.032,length*.41)],.009,steel)
        line(name+' jaw',p(-side*.032,length*.30),
             p(-side*.025,length*.48),.013,brightsteel)
    put(name+' pivot',rod(radius=.016,length=.015,center=p(0,0,.006),color=darksteel))

def scissors(name,x,y,length=.32,angle=0):
    a=math.radians(angle)
    def p(dx,dy,z=1.306):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),z)
    for side in (-1,1):
        pts=[p(side*.043+.029*math.cos(t*math.tau/30),
               -length*.40+.044*math.sin(t*math.tau/30)) for t in range(31)]
        tube(name+' finger bow',pts,.006,brightsteel)
        line(name+' shank',p(side*.04,-length*.28),p(-side*.008,.01),.007,steel)
        line(name+' blade',p(-side*.008,.01),p(-side*.021,length*.54),.009,brightsteel)
    put(name+' screw',rod(radius=.012,length=.013,center=p(0,0,1.316),color=brass))

pliers('left pincers',-.98,-.08,.35,-15)
pliers('thin pincers',-.84,-.08,.34,-12)
pliers('broad pliers',-.68,-.02,.30,15)
scissors('large scissors',-.57,-.22,.34,-6)
scissors('second scissors',-.45,-.25,.28,9)
pliers('middle pliers',-.17,-.06,.34,12)
pliers('back tongs',-.05,.07,.30,16)
# Long narrow calipers.
for x,lean in [(-.31,-.025),(.035,.024)]:
    tube('caliper arm one',[(x-.026,-.35,1.305),(x-.03,-.19,1.31),
                           (x-.012,.05,1.31),(x,.13,1.31)],.007,steel)
    tube('caliper arm two',[(x+.028,-.35,1.305),(x+.035,-.19,1.31),
                           (x+.012,.05,1.31),(x,.13,1.31)],.007,steel)
    line('caliper crossbar',(x-.03,-.18,1.315),(x+.03,-.18,1.315),.005,brightsteel)
    ring('caliper hinge',(x,.13,1.315),.016,steel,.004)

# Chisels, files and wooden-handled implements on the right half.
def tool(name,x,y,length=.40,angle=0,handle=True):
    a=math.radians(angle)
    def p(t,z=1.31):
        return (x-math.sin(a)*t,y+math.cos(a)*t,z)
    line(name+' steel shaft',p(-length*.43),p(length*.35),.010,brightsteel)
    if handle:
        line(name+' wood grip',p(-length*.47,1.322),p(-length*.13,1.322),.023,lightwood)
        line(name+' ferrule',p(-length*.14,1.322),p(-length*.10,1.322),.025,steel)
    else:
        line(name+' broad steel',p(-length*.40),p(length*.24),.018,steel)
for i,(x,y,l,a) in enumerate([
    (.20,-.12,.37,6),(.29,-.10,.34,4),(.45,-.05,.48,11),
    (.57,-.02,.44,17),(.72,.03,.46,13),(.85,.12,.44,16),
    (.98,.15,.42,17)]):
    tool('table tool '+str(i),x,y,l,a,i not in (0,4))

# Hammer with long pale wood handle and rectangular steel head.
line('hammer handle',(.75,-.32,1.325),(.64,.10,1.325),.025,(.55,.40,.24))
cube('hammer head',(.24,.075,.065),(.64,.115,1.343),steel)
cube('hammer polished face',(.035,.082,.07),(.53,.115,1.343),brightsteel)
# Small mallet.
line('small mallet grip',(.89,-.25,1.32),(.83,.03,1.32),.022,oak)
head=cube('mallet head',(.25,.085,.09),(.83,.03,1.35),(.42,.38,.29))
head.turn('z',12)

# Pale blocks and sharpening stones at the right.
stone=cube('large sharpening stone',(.31,.16,.052),(.92,-.15,1.33),(.46,.48,.44))
stone.turn('z',18)
stone=cube('upper stone',(.25,.13,.045),(.88,-.06,1.38),(.60,.60,.52))
stone.turn('z',14)
cube('wooden stone base',(.33,.19,.025),(.92,-.16,1.30),wood)

# Rack of upright punches against the far right corner.
rack=cube('punch rack',(.19,.51,.052),(1.075,.21,1.33),lightwood)
for j in range(6):
    x=1.075+random.uniform(-.018,.018)
    y=.015+j*.085
    height=.16+random.uniform(-.025,.055)
    line('upright punch',(x,y,1.35),(x-.016,y,1.35+height),.013,brightsteel)
    line('punch wooden handle',(x-.009,y,1.41),(x-.016,y,1.35+height-.025),.021,
         random.choice([oak,lightwood,(.60,.49,.34)]))
    ring('punch cap',(x-.016,y,1.35+height),.023,steel,.004)

# A few horizontal wooden handles at the rear.
for j in range(5):
    y=.29+j*.036
    line('rear horizontal handle',(-.36,y,1.32),(-.12,y+.01,1.32),.018,oak)
    line('rear horizontal blade',(-.12,y+.01,1.32),(.10,y+.02,1.32),.006,steel)

# Small cream museum label at the front of the work surface.
label=cube('cream information label',(.31,.045,.105),(.04,-.414,1.342),(.67,.64,.49))
label.turn('x',-22)

# Worn square stool in the foreground.
sx,sy=.15,-1.06
cube('stool thick seat',(.83,.64,.085),(sx,sy,.48),(.29,.25,.18))
for x in (sx-.32,sx+.32):
    for y in (sy-.24,sy+.24):
        cube('stool leg',(.065,.065,.45),(x,y,.225),wood)
cube('stool lower rung',(.67,.045,.045),(sx,sy-.24,.18),oak)
cube('stool side rung',(.045,.48,.045),(sx-.32,sy,.18),oak)
for j in range(120):
    x=random.uniform(sx-.4,sx+.4)
    y=random.uniform(sy-.30,sy+.30)
    chip=ball(random.uniform(.008,.046),center=(x,y,.526),
              color=random.choice([(.42,.39,.29),(.49,.46,.34),(.19,.18,.14),(.35,.32,.24)]))
    chip.resize((random.uniform(.6,2),random.uniform(.4,1.2),.02))
    put('stool worn paint',chip)
cube('stool front rim',(.85,.025,.04),(sx,sy-.322,.48),(.24,.18,.11))

# Secondary bench cropped along the left side.
cube('left neighboring table',(.67,1.04,.09),(-1.67,-.02,1.10),oak)
for x in (-1.94,-1.39):
    cube('neighbor table leg',(.075,.08,1.05),(x,-.34,.53),wood)
cube('left low shelf',(.64,.82,.06),(-1.67,.02,.39),wood)
for j in range(8):
    cube('stacked papers and boards',(.48,.40,.017),(-1.65,.04,1.16+j*.018),
         random.choice([(.40,.43,.35),(.52,.49,.36),(.32,.35,.30)]))
roll=rod(radius=.075,length=.38,center=(-1.72,.17,1.37),axis='+x',color=(.49,.39,.24))
put('leather roll',roll)
cube('small red box',(.25,.20,.11),(-1.83,.37,1.43),(.22,.055,.045))
# Chair fragment in lower left.
for x in (-1.56,-1.28):
    line('chair upright',(x,-1.39,.02),(x,-1.39,.72),.022,(.15,.19,.18))
line('chair crossbar',(-1.56,-1.39,.66),(-1.28,-1.39,.66),.025,(.20,.25,.23))
seat=ball(.19,center=(-1.38,-1.52,.40),color=(.19,.24,.22))
seat.resize((1,.83,.14))
put('chair seat fragment',seat)

# Dark metal structure cropped on the right.
for y in (-.4,.06,.46):
    line('right iron upright',(1.43,y,.04),(1.43,y,1.12),.019,(.055,.075,.075))
cube('right narrow machine table',(.35,.76,.045),(1.52,.02,1.13),(.12,.15,.15))
line('iron side brace',(1.43,-.4,.12),(1.43,.45,.90),.012,darksteel)

# Shallow wooden wall-mounted open box near the top right.
cube('wall bin back',(.56,.045,.43),(.98,.59,2.03),wood)
cube('wall bin bottom',(.59,.24,.04),(.98,.49,1.84),oak)
cube('wall bin lip',(.59,.035,.11),(.98,.36,1.88),oak)
for x in (.70,1.26):
    cube('wall bin side',(.035,.24,.23),(x,.48,1.94),wood)

realize(scene)

# Subtle procedural surface grain and aged finish.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:
        continue
    base=bs.inputs['Base Color'].default_value
    r,g,b=base[:3]
    bs.inputs['Roughness'].default_value=.76
    if abs(r-g)<.10 and b>=r*.72 and r<.62:
        bs.inputs['Metallic'].default_value=.62
        bs.inputs['Roughness'].default_value=.48
    if r>g*1.20 and g>b*1.25:
        nodes=mat.node_tree.nodes
        links=mat.node_tree.links
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=5
        tex.inputs['Detail'].default_value=3
        tex.inputs['Roughness'].default_value=.78
        coord=nodes.new('ShaderNodeTexCoord')
        scale=nodes.new('ShaderNodeVectorMath')
        scale.operation='MULTIPLY'
        scale.inputs[1].default_value=(5,5,55)
        links.new(coord.outputs['Generated'],scale.inputs[0])
        links.new(scale.outputs[0],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18
        ramp.color_ramp.elements[0].color=(r*.57,g*.54,b*.50,1)
        ramp.color_ramp.elements[1].position=.83
        ramp.color_ramp.elements[1].color=(min(r*1.28,1),min(g*1.25,1),min(b*1.22,1),1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.17
        bump.inputs['Distance'].default_value=.008
        links.new(tex.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])

# Tiny lettering on the tabletop card.
font=bpy.data.curves.new('label lettering','FONT')
font.body="Please do not touch\nTools of the trade"
font.align_x='CENTER'
font.size=.018
font.extrude=0
obj=bpy.data.objects.new('information text',font)
bpy.context.collection.objects.link(obj)
obj.location=(.04,-.445,1.351)
obj.rotation_euler=(math.radians(68),0,0)
ink=bpy.data.materials.new('faded black ink')
ink.diffuse_color=(.08,.075,.055,1)
obj.data.materials.append(ink)

set_view((.12,-3.65,3.02),(0,-.02,1.06),lens=43,sensor=36)
area_emitter((-2,-2.2,4.2),power=480,size=3.0,target=(0,0,1),color=(1,.88,.72))
area_emitter((1.8,-.4,3.3),power=180,size=2.2,target=(0,0,1),color=(.83,.90,1))
world=bpy.context.scene.world
world.color=(.20,.20,.18)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=384
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
