import bpy, math, random
from sceneact import *

random.seed(24)
scene = Scene('Old hand tool workshop')
wood = (.34,.19,.085)
oak = (.48,.30,.14)
lightwood = (.58,.40,.22)
steel = (.29,.34,.34)
brightsteel = (.49,.54,.53)
darksteel = (.10,.14,.14)
brass = (.36,.31,.16)
counter = 0

def put(name, node):
    global counter
    counter += 1
    scene.include('%s_%05d' % (name, counter), node)
    return node

def cube(name, size, pos, col):
    return put(name, box(size=size, center=pos, color=col))

def line(name, a, b, r=.008, col=steel):
    return put(name, rod(radius=r, start=a, end=b, color=col))

def tube(name, points, r=.008, col=steel):
    return put(name, sweep_tube(points=points, radius=r, color=col))

def ring(name, center, radius, col=steel, thickness=.007, plane='xy', squash=1):
    x,y,z = center
    pts = []
    for j in range(33):
        a = j*math.tau/32
        if plane == 'xy':
            pts.append((x+radius*math.cos(a), y+radius*squash*math.sin(a), z))
        elif plane == 'xz':
            pts.append((x+radius*math.cos(a), y, z+radius*squash*math.sin(a)))
        else:
            pts.append((x, y+radius*math.cos(a), z+radius*squash*math.sin(a)))
    return tube(name, pts, thickness, col)

# Architecture.
for j in range(16):
    x = -2.1+j*.28
    cube('floor plank', (.275,4.4,.065), (x,-.55,-.045),
         (.30+random.random()*.10,.19+random.random()*.06,.10+random.random()*.04))
    for k in range(3):
        xx = x+random.uniform(-.12,.12)
        line('floor grain',(xx,-2.7,.001),(xx,1.4,.001),.0008,(.22,.135,.07))

for j in range(17):
    x = -2.35+j*.29
    cube('wall board',(.284,.08,3.3),(x,.69,1.55),
         (random.uniform(.32,.45),random.uniform(.17,.25),random.uniform(.075,.12)))
    for k in range(6):
        xx = x+random.uniform(-.135,.135)
        line('wall grain',(xx,.645,0),(xx+random.uniform(-.012,.012),.645,3.15),
             random.uniform(.0007,.0016),(.22,.115,.05))
    for z in (.6,1.85,2.45):
        if random.random()<.7:
            n = ball(.014,center=(x+random.uniform(-.09,.09),.636,z),color=(.105,.06,.025))
            n.resize((1,.2,1.35))
            put('wood knot',n)
cube('baseboard',(4.7,.07,.13),(0,.59,.08),wood)

# Main bench.
cube('bench slab',(2.35,1,.11),(0,.025,1.23),lightwood)
cube('front worn rail',(2.36,.07,.09),(0,-.483,1.205),oak)
cube('rear rim',(2.35,.055,.055),(0,.49,1.29),wood)
for x in (-1.04,1.04):
    for y in (-.34,.40):
        cube('bench leg',(.095,.105,1.15),(x,y,.58),oak)
        cube('leg worn corner',(.015,.11,.89),(x-.035,y,.61),lightwood)
cube('lower stretcher',(2.12,.07,.12),(0,.39,.28),wood)
for x in (-.64,.64):
    cube('drawer partition',(.055,.84,.79),(x,.01,.79),wood)
for x in (-1.105,1.105):
    cube('side carcass',(.055,.88,.82),(x,.01,.79),oak)

for j in range(12):
    y = -.43+j*.079
    line('top seam',(-1.16,y,1.287),(1.16,y,1.287),.0017,(.22,.18,.12))
for j in range(150):
    x,y = random.uniform(-1.16,1.16),random.uniform(-.45,.47)
    line('top scratch',(x,y,1.288),
         (min(x+random.uniform(.015,.12),1.16),y+random.uniform(-.008,.008),1.288),
         random.uniform(.0005,.0013),
         random.choice([(.65,.51,.33),(.28,.25,.19),(.43,.38,.28)]))
for j in range(42):
    cube('front chipped wood',(random.uniform(.009,.07),.005,random.uniform(.006,.026)),
         (random.uniform(-1.16,1.16),-.521,1.23+random.uniform(-.04,.04)),
         random.choice([lightwood,wood,(.68,.50,.29)]))

def drawer(name,x,z,w,depth,fy):
    cube(name+' bottom',(w,depth,.026),(x,fy+depth/2,z-.035),(.32,.23,.13))
    cube(name+' front',(w+.035,.052,.145),(x,fy,z),oak)
    cube(name+' left',(.027,depth,.135),(x-w/2,fy+depth/2,z+.005),lightwood)
    cube(name+' right',(.027,depth,.135),(x+w/2,fy+depth/2,z+.005),lightwood)
    cube(name+' rear',(w,.028,.12),(x,fy+depth,z),wood)
    for k in range(13):
        cube('drawer patina',(random.uniform(.004,.024),.002,random.uniform(.015,.07)),
             (x+random.uniform(-w/2,w/2),fy-.027,z+random.uniform(-.055,.055)),
             random.choice([lightwood,wood]))
    for xx in (x-.065,x+.065):
        line('handle fixing',(xx,fy-.029,z),(xx,fy-.042,z),.015,darksteel)
    tube('iron drop handle',[
        (x-.065,fy-.045,z),(x-.052,fy-.06,z-.042),
        (x,fy-.065,z-.052),(x+.052,fy-.06,z-.042),
        (x+.065,fy-.045,z)],.008,darksteel)

drawer('upper left',-.885,1.055,.49,.53,-.66)
drawer('middle left',-.885,.785,.49,.49,-.64)
drawer('bottom left',-.885,.405,.49,.52,-.67)
drawer('wide center',0,.97,1.22,.59,-.76)
drawer('upper right',.89,1.055,.48,.51,-.61)
drawer('bottom right',.90,.63,.48,.51,-.64)

for x in (-1.03,-.90,-.76):
    cube('drawer divider',(.018,.43,.055),(x,-.40,1.055),wood)
for j in range(24):
    x,y = random.uniform(-1.08,-.70),random.uniform(-.60,-.19)
    line('small drawer tools',(x,y,1.108),(x+.035,y+.10,1.11),.006,
         random.choice([steel,brass,wood]))
for j in range(9):
    cube('paper packet',(.033,.25,.10),(-1.075+j*.046,-.40,.438),(.64,.55,.37))
for j in range(9):
    x = -.54+j*.13
    line('drawer chisel',(x,-.70,1.035),(x+.025,-.27,1.07),.012,steel)
    line('drawer wood grip',(x,-.43,1.065),(x+.02,-.25,1.085),.027,
         random.choice([wood,oak,(.57,.34,.15)]))
    ring('grip ferrule',(x,-.43,1.065),.029,brass,.004,plane='xz')
for j in range(38):
    x,y = random.uniform(.70,1.08),random.uniform(-.57,-.18)
    line('drawer metal pieces',(x,y,1.11),(x+.025,y+.035,1.115),.0035,steel)
cube('folded cloth',(.30,.27,.045),(.89,-.38,.70),(.63,.60,.48))
cube('paper in lower drawer',(.16,.25,.015),(.95,-.43,.725),(.73,.68,.53))

# Two-tier rotary parts organizer.
tx,ty = .48,.265
for level,radius in [(1.45,.24),(1.73,.255)]:
    disk = ball(1,center=(tx,ty,level),color=(.065,.105,.112))
    disk.resize((radius,radius,.035))
    put('carousel tray',disk)
    ring('carousel upper rim',(tx,ty,level+.055),radius,(.21,.30,.31),.010)
    ring('carousel bottom rim',(tx,ty,level-.01),radius*.91,(.13,.20,.21),.006)
    for k in range(8):
        a = k*math.tau/8
        p = (tx+radius*math.cos(a),ty+radius*math.sin(a),level+.055)
        # Thin upright radial sheets.
        divider = cube('tray divider',(radius,.008,.06),
                       (tx+radius*.5*math.cos(a),ty+radius*.5*math.sin(a),level+.026),
                       (.12,.19,.20))
        divider.turn('z',math.degrees(a))
        line('divider top',(tx,ty,level+.055),p,.005,(.20,.28,.29))
    for k in range(16):
        a,rr = random.random()*math.tau,random.uniform(.07,radius*.8)
        px,py = tx+rr*math.cos(a),ty+rr*math.sin(a)
        line('tray hardware',(px,py,level+.025),(px+.018,py+.015,level+.034),.004,steel)
line('carousel spindle',(tx,ty,1.29),(tx,ty,1.88),.016,steel)
tube('carousel loop',[(tx-.025,ty,1.82),(tx-.016,ty,1.94),
                     (tx+.025,ty,1.975),(tx+.055,ty,1.955),
                     (tx+.047,ty,1.90),(tx+.012,ty,1.85)],.009,(.22,.35,.38))

# Oil cans.
for x,y in [(-.96,.30),(-.67,.32)]:
    base = ball(.105,center=(x,y,1.33),color=(.29,.29,.13))
    base.resize((1,1,.62))
    put('oil can reservoir',base)
    ring('oil can bottom',(x,y,1.286),.096,brass,.006)
    line('oil can collar',(x,y,1.382),(x,y,1.408),.045,steel)
    line('oil can spout',(x,y,1.405),(x-.021,y+.002,1.545),.018,darksteel)
    line('spout tip',(x-.021,y+.002,1.53),(x-.03,y,1.585),.009,steel)
    for j in range(7):
        a = random.random()*math.tau
        line('can tarnish',(x+.08*math.cos(a),y+.08*math.sin(a),1.33),
             (x+.075*math.cos(a),y+.075*math.sin(a),1.36),.004,(.46,.40,.20))

# Open cylindrical metal cup.
cx,cy = -.46,.08
line('cup base',(cx,cy,1.286),(cx,cy,1.298),.064,brass)
ring('cup rim',(cx,cy,1.43),.063,brass,.006)
for j in range(36):
    a = j*math.tau/36
    line('cup wall',(cx+.060*math.cos(a),cy+.060*math.sin(a),1.30),
         (cx+.060*math.cos(a),cy+.060*math.sin(a),1.426),.0055,(.29,.29,.20))
ring('cup foot',(cx,cy,1.30),.066,steel,.005)

def pliers(name,x,y,length=.31,angle=0):
    a = math.radians(angle)
    def p(dx,dy,dz=0):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),1.303+dz)
    for side in (-1,1):
        tube(name+' arm',[p(side*.035,-length*.54),
             p(side*.046,-length*.32),p(side*.016,-.015),
             p(-side*.022,length*.27),p(-side*.032,length*.41)],.009,steel)
        line(name+' jaw',p(-side*.032,length*.30),p(-side*.025,length*.48),.013,brightsteel)
    line(name+' pivot',p(0,0),p(0,0,.015),.016,darksteel)

def scissors(name,x,y,length=.32,angle=0):
    a = math.radians(angle)
    def p(dx,dy,z=1.306):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),z)
    for side in (-1,1):
        pts = [p(side*.043+.029*math.cos(t*math.tau/30),
                 -length*.40+.044*math.sin(t*math.tau/30)) for t in range(31)]
        tube(name+' bow',pts,.006,brightsteel)
        line(name+' shank',p(side*.04,-length*.28),p(-side*.008,.01),.007,steel)
        line(name+' blade',p(-side*.008,.01),p(-side*.021,length*.54),.009,brightsteel)
    line(name+' screw',p(0,0,1.307),p(0,0,1.321),.012,brass)

pliers('left pincers',-.98,-.08,.35,-15)
pliers('thin pincers',-.84,-.08,.34,-12)
pliers('broad pliers',-.68,-.02,.30,15)
scissors('large scissors',-.57,-.22,.34,-6)
scissors('second scissors',-.45,-.25,.28,9)
pliers('middle pliers',-.17,-.06,.34,12)
pliers('back tongs',-.05,.07,.30,16)

for x in (-.31,.035):
    tube('caliper arm',[(x-.026,-.35,1.305),(x-.03,-.19,1.31),
                       (x-.012,.05,1.31),(x,.13,1.31)],.007,steel)
    tube('caliper arm',[(x+.028,-.35,1.305),(x+.035,-.19,1.31),
                       (x+.012,.05,1.31),(x,.13,1.31)],.007,steel)
    line('caliper crossbar',(x-.03,-.18,1.315),(x+.03,-.18,1.315),.005,brightsteel)
    ring('caliper hinge',(x,.13,1.315),.016,steel,.004)

def tool(name,x,y,length=.40,angle=0,handle=True):
    a = math.radians(angle)
    def p(t,z=1.31):
        return (x-math.sin(a)*t,y+math.cos(a)*t,z)
    line(name+' shaft',p(-length*.43),p(length*.35),.010,brightsteel)
    if handle:
        line(name+' grip',p(-length*.47,1.322),p(-length*.13,1.322),.023,lightwood)
        line(name+' ferrule',p(-length*.14,1.322),p(-length*.10,1.322),.025,steel)
    else:
        line(name+' blade',p(-length*.40),p(length*.24),.018,steel)

for i,(x,y,l,a) in enumerate([
    (.20,-.12,.37,6),(.29,-.10,.34,4),(.45,-.05,.48,11),
    (.57,-.02,.44,17),(.72,.03,.46,13),(.85,.12,.44,16),(.98,.15,.42,17)]):
    tool('table tool',x,y,l,a,i not in (0,4))

line('hammer handle',(.75,-.32,1.325),(.64,.10,1.325),.025,(.55,.40,.24))
cube('hammer head',(.24,.075,.065),(.64,.115,1.343),steel)
cube('hammer face',(.035,.082,.07),(.53,.115,1.343),brightsteel)
line('mallet grip',(.89,-.25,1.32),(.83,.03,1.32),.022,oak)
n = cube('mallet head',(.25,.085,.09),(.83,.03,1.35),(.42,.38,.29))
n.turn('z',12)

n = cube('lower sharpening stone',(.31,.16,.052),(.92,-.15,1.33),(.46,.48,.44))
n.turn('z',18)
n = cube('upper sharpening stone',(.25,.13,.045),(.88,-.06,1.38),(.60,.60,.52))
n.turn('z',14)
cube('stone base',(.33,.19,.025),(.92,-.16,1.30),wood)

cube('punch rack',(.19,.51,.052),(1.075,.21,1.33),lightwood)
for j in range(6):
    x,y = 1.075+random.uniform(-.018,.018),.015+j*.085
    h = .16+random.uniform(-.025,.055)
    line('upright punch',(x,y,1.35),(x-.016,y,1.35+h),.013,brightsteel)
    line('punch grip',(x-.009,y,1.41),(x-.016,y,1.35+h-.025),.021,
         random.choice([oak,lightwood,(.60,.49,.34)]))
    ring('punch cap',(x-.016,y,1.35+h),.023,steel,.004)

for j in range(5):
    y = .29+j*.036
    line('rear handle',(-.36,y,1.32),(-.12,y+.01,1.32),.018,oak)
    line('rear blade',(-.12,y+.01,1.32),(.10,y+.02,1.32),.006,steel)

n = cube('cream label',(.31,.018,.105),(.04,-.414,1.342),(.67,.64,.49))
n.turn('x',-22)

# Foreground stool.
sx,sy = .15,-1.06
cube('stool seat',(.83,.64,.085),(sx,sy,.48),(.29,.25,.18))
for x in (sx-.32,sx+.32):
    for y in (sy-.24,sy+.24):
        cube('stool leg',(.065,.065,.45),(x,y,.225),wood)
cube('stool front rung',(.67,.045,.045),(sx,sy-.24,.18),oak)
cube('stool side rung',(.045,.48,.045),(sx-.32,sy,.18),oak)
for j in range(160):
    n = ball(random.uniform(.008,.046),
             center=(random.uniform(sx-.4,sx+.4),random.uniform(sy-.30,sy+.30),.526),
             color=random.choice([(.42,.39,.29),(.49,.46,.34),(.19,.18,.14),(.35,.32,.24)]))
    n.resize((random.uniform(.6,2),random.uniform(.4,1.2),.02))
    put('stool worn paint',n)
cube('stool front rim',(.85,.025,.04),(sx,sy-.322,.48),(.24,.18,.11))

# Neighboring bench on the left.
cube('left table top',(.67,1.04,.09),(-1.67,-.02,1.10),oak)
for x in (-1.94,-1.39):
    cube('left table leg',(.075,.08,1.05),(x,-.34,.53),wood)
cube('left low shelf',(.64,.82,.06),(-1.67,.02,.39),wood)
for j in range(8):
    cube('stacked boards',(.48,.40,.017),(-1.65,.04,1.16+j*.018),
         random.choice([(.40,.43,.35),(.52,.49,.36),(.32,.35,.30)]))
line('leather roll',(-1.91,.17,1.37),(-1.53,.17,1.37),.075,(.49,.39,.24))
cube('red box',(.25,.20,.11),(-1.83,.37,1.43),(.22,.055,.045))
for x in (-1.56,-1.28):
    line('chair upright',(x,-1.39,.02),(x,-1.39,.72),.022,(.15,.19,.18))
line('chair crossbar',(-1.56,-1.39,.66),(-1.28,-1.39,.66),.025,(.20,.25,.23))
n = ball(.19,center=(-1.38,-1.52,.40),color=(.19,.24,.22))
n.resize((1,.83,.14))
put('chair seat',n)

for y in (-.4,.06,.46):
    line('right iron upright',(1.43,y,.04),(1.43,y,1.12),.019,(.055,.075,.075))
cube('right iron table',(.35,.76,.045),(1.52,.02,1.13),(.12,.15,.15))
line('right brace',(1.43,-.4,.12),(1.43,.45,.90),.012,darksteel)

cube('wall bin back',(.56,.045,.43),(.98,.59,2.03),wood)
cube('wall bin bottom',(.59,.24,.04),(.98,.49,1.84),oak)
cube('wall bin lip',(.59,.035,.11),(.98,.36,1.88),oak)
for x in (.70,1.26):
    cube('wall bin side',(.035,.24,.23),(x,.48,1.94),wood)

realize(scene)

# Procedural aged finishes.
for mat in bpy.data.materials:
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    r,g,b = bs.inputs['Base Color'].default_value[:3]
    bs.inputs['Roughness'].default_value = .76
    if abs(r-g)<.10 and b>=r*.72 and r<.62:
        bs.inputs['Metallic'].default_value = .62
        bs.inputs['Roughness'].default_value = .48
    if r>g*1.20 and g>b*1.25:
        nodes,links = mat.node_tree.nodes,mat.node_tree.links
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 5
        tex.inputs['Detail'].default_value = 3
        tex.inputs['Roughness'].default_value = .78
        coord = nodes.new('ShaderNodeTexCoord')
        scale = nodes.new('ShaderNodeVectorMath')
        scale.operation = 'MULTIPLY'
        scale.inputs[1].default_value = (5,5,55)
        links.new(coord.outputs['Generated'],scale.inputs[0])
        links.new(scale.outputs[0],tex.inputs['Vector'])
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .18
        ramp.color_ramp.elements[0].color = (r*.57,g*.54,b*.50,1)
        ramp.color_ramp.elements[1].position = .83
        ramp.color_ramp.elements[1].color = (min(r*1.28,1),min(g*1.25,1),min(b*1.22,1),1)
        links.new(tex.outputs['Fac'],ramp.inputs[0])
        links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .17
        bump.inputs['Distance'].default_value = .008
        links.new(tex.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])

font = bpy.data.curves.new('label lettering','FONT')
font.body = "Please do not touch\nTools of the trade"
font.align_x = 'CENTER'
font.size = .018
obj = bpy.data.objects.new('information text',font)
bpy.context.collection.objects.link(obj)
obj.location = (.04,-.427,1.351)
obj.rotation_euler = (math.radians(68),0,0)
ink = bpy.data.materials.new('faded ink')
ink.diffuse_color = (.08,.075,.055,1)
obj.data.materials.append(ink)

set_view((.12,-3.65,3.02),(0,-.02,1.06),lens=43,sensor=36)
area_emitter((-2,-2.2,4.2),power=480,size=3.0,target=(0,0,1),color=(1,.88,.72))
area_emitter((1.8,-.4,3.3),power=180,size=2.2,target=(0,0,1),color=(.83,.90,1))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Workshop world')
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.20,.20,.18,1)
bg.inputs['Strength'].default_value = .45
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
