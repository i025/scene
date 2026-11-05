import bpy, math, random
from sceneact import *

random.seed(24)
scene = Scene('Antique tool bench')
wood = (.36,.22,.11)
oak = (.49,.32,.17)
pale = (.60,.44,.26)
iron = (.27,.32,.32)
silver = (.49,.54,.53)
dark = (.065,.105,.115)
brass = (.34,.31,.17)
count = 0

def add(node):
    global count
    count += 1
    scene.include('part_%04d' % count, node)
    return node

def block(size, pos, color=oak):
    return add(box(size=size, center=pos, color=color))

def bar(a, b, radius=.009, color=iron):
    return add(rod(radius=radius, start=a, end=b, color=color))

def curve(points, radius=.008, color=iron):
    return add(sweep_tube(points=points, radius=radius, color=color))

def loop(center, radius, color=iron, wire=.006, plane='xy', aspect=1):
    x,y,z = center
    points = []
    for j in range(25):
        t = math.tau*j/24
        if plane == 'xy':
            points.append((x+radius*math.cos(t),y+radius*aspect*math.sin(t),z))
        else:
            points.append((x+radius*math.cos(t),y,z+radius*aspect*math.sin(t)))
    return curve(points,wire,color)

# Broad wooden wall boards and floor.
for i in range(13):
    block((.31,.07,3.3),(-1.95+i*.315,.70,1.58),
          (random.uniform(.32,.43),random.uniform(.18,.25),random.uniform(.08,.13)))
for i in range(12):
    block((.32,4.4,.055),(-1.95+i*.325,-.6,-.035),
          (random.uniform(.32,.42),random.uniform(.21,.28),random.uniform(.11,.16)))
block((4.3,.08,.13),(0,.61,.07),wood)

# Main cabinet bench.
block((2.35,1.01,.095),(0,.025,1.23),pale)
block((2.37,.055,.075),(0,-.491,1.215),oak)
block((2.35,.045,.045),(0,.50,1.29),wood)
for x in (-1.065,1.065):
    for y in (-.34,.39):
        block((.085,.095,1.14),(x,y,.57),oak)
block((2.17,.07,.10),(0,.39,.25),wood)
for x in (-1.12,-.64,.64,1.12):
    block((.045,.79,.77),(x,.03,.81),wood)

def drawer(x,z,w,fy,depth):
    block((w,depth,.024),(x,fy+depth/2,z-.045),wood)
    block((w+.025,.045,.14),(x,fy,z),oak)
    for xx in (x-w/2,x+w/2):
        block((.023,depth,.12),(xx,fy+depth/2,z+.007),pale)
    block((w,.025,.12),(x,fy+depth,z),wood)
    curve([(x-.064,fy-.028,z),(x-.054,fy-.053,z-.038),
           (x,fy-.060,z-.052),(x+.054,fy-.053,z-.038),
           (x+.064,fy-.028,z)],.008,dark)
    for xx in (x-.064,x+.064):
        bar((xx,fy-.026,z),(xx,fy-.035,z),.013,iron)

drawer(-.885,1.06,.48,-.65,.53)
drawer(-.885,.79,.48,-.65,.49)
drawer(-.885,.40,.48,-.69,.52)
drawer(0,.975,1.22,-.76,.60)
drawer(.89,1.055,.48,-.62,.51)
drawer(.90,.63,.48,-.65,.51)

# Contents of the drawers.
for i in range(8):
    x = -.53+i*.15
    bar((x,-.70,1.035),(x+.022,-.28,1.067),.010,silver)
    bar((x+.008,-.44,1.063),(x+.022,-.26,1.083),.026,
        random.choice([wood,oak,pale]))
for i in range(5):
    block((.055,.27,.085),(-1.075+i*.085,-.40,.435),(.64,.55,.38))
for i in range(6):
    x = random.uniform(-1.07,-.72)
    y = random.uniform(-.58,-.24)
    bar((x,y,1.11),(x+.035,y+.12,1.115),.006,brass)
for i in range(10):
    x,y = random.uniform(.70,1.07),random.uniform(-.57,-.20)
    curve([(x,y,1.11),(x+.026,y+.03,1.115),(x-.016,y+.06,1.115)],.004,iron)
block((.31,.26,.045),(.89,-.39,.70),(.61,.59,.49))
block((.15,.22,.012),(.96,-.43,.73),(.73,.68,.54))

# Two oil cans.
for x,y in [(-.96,.31),(-.67,.33)]:
    n = add(ball(.103,center=(x,y,1.335),color=(.30,.30,.15)))
    n.resize((1,1,.62))
    loop((x,y,1.29),.094,brass,.005)
    bar((x,y,1.38),(x,y,1.414),.041,iron)
    bar((x,y,1.412),(x-.027,y,1.58),.013,iron)

# Open metal cylindrical cup.
cx,cy = -.45,.07
bar((cx,cy,1.292),(cx,cy,1.303),.060,brass)
loop((cx,cy,1.423),.060,brass,.006)
# A thin hollow wall made from one closed ribbon mesh after realization.
cup_data = (cx,cy)

# Two-tier metal carousel with eight divided compartments.
tx,ty = .46,.285
for z,r in [(1.46,.245),(1.74,.258)]:
    n = add(ball(1,center=(tx,ty,z),color=dark))
    n.resize((r,r,.028))
    loop((tx,ty,z+.054),r,(.20,.29,.31),.008)
    loop((tx,ty,z-.004),r*.96,dark,.006)
    for j in range(8):
        a = math.tau*j/8
        n = block((r,.008,.061),
                  (tx+.5*r*math.cos(a),ty+.5*r*math.sin(a),z+.025),
                  (.12,.19,.20))
        n.turn('z',math.degrees(a))
bar((tx,ty,1.29),(tx,ty,1.90),.014,iron)
curve([(tx-.02,ty,1.84),(tx-.01,ty,1.96),(tx+.025,ty,1.995),
       (tx+.052,ty,1.975),(tx+.045,ty,1.92),(tx+.006,ty,1.86)],
      .008,(.22,.34,.37))

# Tools laid flat on the table.
def pliers(x,y,length=.34,angle=0):
    a = math.radians(angle)
    def p(dx,dy,z=1.304):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),z)
    for s in (-1,1):
        curve([p(s*.035,-length*.53),p(s*.044,-length*.30),
               p(s*.012,0),p(-s*.025,length*.29),
               p(-s*.026,length*.46)],.009,iron)
    bar(p(0,0),p(0,0,1.319),.014,silver)

def scissors(x,y,length=.32,angle=0):
    a = math.radians(angle)
    def p(dx,dy):
        return (x+dx*math.cos(a)-dy*math.sin(a),
                y+dx*math.sin(a)+dy*math.cos(a),1.309)
    for s in (-1,1):
        points = [p(s*.038+.027*math.cos(j*math.tau/24),
                    -length*.36+.039*math.sin(j*math.tau/24))
                  for j in range(25)]
        curve(points,.0055,silver)
        curve([p(s*.038,-length*.25),p(0,0),p(-s*.016,length*.51)],.007,silver)

pliers(-.99,-.08,.36,-15)
pliers(-.84,-.08,.35,-12)
pliers(-.69,-.02,.31,14)
scissors(-.56,-.22,.34,-5)
scissors(-.44,-.24,.29,8)
pliers(-.15,-.06,.35,10)
pliers(-.025,.06,.31,15)

for x in (-.30,.045):
    curve([(x-.027,-.36,1.307),(x-.031,-.19,1.31),
           (x-.012,.06,1.31),(x,.14,1.31),
           (x+.013,.06,1.31),(x+.032,-.19,1.31),
           (x+.028,-.36,1.307)],.0065,silver)
    bar((x-.03,-.18,1.315),(x+.03,-.18,1.315),.005,iron)

for i,(x,y,length,angle) in enumerate([
    (.20,-.12,.38,5),(.30,-.09,.35,4),
    (.45,-.04,.48,11),(.57,-.01,.44,16),
    (.72,.04,.46,13),(.86,.13,.44,16),(.99,.16,.43,17)]):
    a = math.radians(angle)
    def p(t):
        return (x-math.sin(a)*t,y+math.cos(a)*t,1.315)
    bar(p(-length*.44),p(length*.40),.010,silver)
    if i not in (0,4):
        bar(p(-length*.46),p(-length*.14),.022,pale)

# Hammer, mallet, and stacked sharpening stones.
bar((.74,-.32,1.327),(.64,.12,1.327),.023,pale)
block((.24,.072,.067),(.64,.12,1.349),iron)
bar((.89,-.25,1.32),(.83,.035,1.32),.022,oak)
n = block((.25,.085,.085),(.83,.035,1.35),(.44,.39,.30))
n.turn('z',12)
block((.33,.19,.024),(.94,-.16,1.305),wood)
n = block((.31,.16,.046),(.94,-.15,1.34),(.46,.48,.44))
n.turn('z',17)
n = block((.25,.13,.042),(.90,-.06,1.386),(.61,.61,.54))
n.turn('z',14)

# Upright punches along the right edge.
block((.17,.52,.045),(1.075,.20,1.325),pale)
for j in range(6):
    y = .005+j*.085
    h = random.uniform(.16,.22)
    bar((1.075,y,1.34),(1.058,y,1.34+h),.011,silver)
    bar((1.067,y,1.40),(1.058,y,1.34+h-.015),.019,pale)
for j in range(4):
    y = .31+j*.038
    bar((-.35,y,1.32),(-.13,y,1.32),.017,oak)
    bar((-.13,y,1.32),(.08,y+.01,1.32),.005,iron)

n = block((.29,.017,.095),(.035,-.42,1.343),(.70,.67,.53))
n.turn('x',-20)

# Foreground stool.
sx,sy = .15,-1.075
seat = block((.83,.64,.085),(sx,sy,.48),(.40,.37,.28))
for x in (sx-.32,sx+.32):
    for y in (sy-.24,sy+.24):
        block((.065,.065,.45),(x,y,.225),wood)
block((.67,.045,.045),(sx,sy-.24,.17),oak)
block((.045,.48,.045),(sx-.32,sy,.17),oak)

# Cropped neighboring furniture.
block((.67,1.02,.08),(-1.67,-.02,1.10),oak)
for x in (-1.94,-1.39):
    block((.075,.08,1.05),(x,-.34,.53),wood)
block((.64,.82,.06),(-1.67,.02,.39),wood)
for j in range(5):
    block((.48,.40,.025),(-1.65,.04,1.16+j*.025),
          random.choice([(.40,.43,.35),(.53,.49,.37),(.32,.35,.30)]))
bar((-1.91,.17,1.36),(-1.53,.17,1.36),.071,(.49,.39,.25))
block((.25,.20,.11),(-1.83,.37,1.43),(.22,.055,.045))
for x in (-1.56,-1.28):
    bar((x,-1.39,.02),(x,-1.39,.72),.022,(.15,.19,.18))
bar((-1.56,-1.39,.66),(-1.28,-1.39,.66),.025,iron)
n = add(ball(.18,center=(-1.38,-1.52,.40),color=(.19,.24,.22)))
n.resize((1,.83,.14))

for y in (-.40,.06,.46):
    bar((1.44,y,.04),(1.44,y,1.12),.018,dark)
block((.35,.76,.043),(1.53,.02,1.13),dark)
bar((1.44,-.4,.12),(1.44,.45,.9),.012,dark)

# Open wooden wall box.
block((.56,.04,.43),(.98,.60,2.03),wood)
block((.59,.24,.035),(.98,.49,1.84),oak)
block((.59,.035,.11),(.98,.36,1.88),oak)
for x in (.70,1.26):
    block((.03,.24,.23),(x,.48,1.94),wood)

realize(scene)

# Thin open cup shell, avoiding many individual wall elements.
verts,faces = [],[]
for z in (1.30,1.423):
    for j in range(32):
        a = math.tau*j/32
        verts.append((cx+.060*math.cos(a),cy+.060*math.sin(a),z))
for j in range(32):
    faces.append((j,(j+1)%32,(j+1)%32+32,j+32))
mesh = bpy.data.meshes.new('Cup shell')
mesh.from_pydata(verts,[],faces)
mesh.update()
obj = bpy.data.objects.new('Open metal cup',mesh)
bpy.context.collection.objects.link(obj)
mat = bpy.data.materials.new('Cup patinated brass')
mat.diffuse_color = (.29,.28,.17,1)
obj.data.materials.append(mat)

# Surface variation supplies grain, wear and tarnish without extra geometry.
for mat in bpy.data.materials:
    mat.use_nodes = True
    nodes,links = mat.node_tree.nodes,mat.node_tree.links
    bs = nodes.get('Principled BSDF')
    if bs is None:
        continue
    r,g,b = mat.diffuse_color[:3]
    bs.inputs['Base Color'].default_value = (r,g,b,1)
    bs.inputs['Roughness'].default_value = .76
    metal = abs(r-g)<.09 and b>r*.72 and r<.6
    if metal:
        bs.inputs['Metallic'].default_value = .68
        bs.inputs['Roughness'].default_value = .46
    tex = nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 8 if metal else 5
    tex.inputs['Detail'].default_value = 3
    coord = nodes.new('ShaderNodeTexCoord')
    scale = nodes.new('ShaderNodeVectorMath')
    scale.operation = 'MULTIPLY'
    scale.inputs[1].default_value = (3,3,32) if r>g*1.15 else (3,3,3)
    links.new(coord.outputs['Generated'],scale.inputs[0])
    links.new(scale.outputs[0],tex.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .22
    ramp.color_ramp.elements[0].color = (r*.48,g*.47,b*.45,1)
    ramp.color_ramp.elements[1].position = .78
    ramp.color_ramp.elements[1].color = (min(r*1.35,1),min(g*1.32,1),min(b*1.3,1),1)
    links.new(tex.outputs['Fac'],ramp.inputs[0])
    links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .20
    bump.inputs['Distance'].default_value = .006
    links.new(tex.outputs['Fac'],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],bs.inputs['Normal'])

# Distinct broad mottling on the stool's worn seat.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if abs(obj.location.z-.48)<.001 and obj.dimensions.x>.7 and obj.dimensions.y>.5:
        mat = bpy.data.materials.new('Worn stool surface')
        mat.use_nodes = True
        nd,lk = mat.node_tree.nodes,mat.node_tree.links
        bs = nd.get('Principled BSDF')
        tex = nd.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 15
        tex.inputs['Detail'].default_value = 5
        ramp = nd.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .35
        ramp.color_ramp.elements[0].color = (.12,.105,.075,1)
        ramp.color_ramp.elements[1].position = .64
        ramp.color_ramp.elements[1].color = (.54,.50,.39,1)
        lk.new(tex.outputs['Fac'],ramp.inputs[0])
        lk.new(ramp.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = .93
        obj.data.materials.clear()
        obj.data.materials.append(mat)

font = bpy.data.curves.new('Museum label text','FONT')
font.body = 'Please do not touch\nTools of the trade'
font.size = .016
font.align_x = 'CENTER'
text = bpy.data.objects.new('Museum label text',font)
bpy.context.collection.objects.link(text)
text.location = (.035,-.434,1.35)
text.rotation_euler = (math.radians(70),0,0)
ink = bpy.data.materials.new('Label ink')
ink.diffuse_color = (.065,.06,.045,1)
font.materials.append(ink)

set_view((.12,-3.65,3.02),(0,-.02,1.06),lens=43,sensor=36)
area_emitter((-2,-2.2,4.2),power=470,size=3,target=(0,0,1),color=(1,.88,.74))
area_emitter((1.8,-.4,3.3),power=170,size=2.2,target=(0,0,1),color=(.84,.91,1))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Workshop world')
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.20,.20,.18,1)
bg.inputs['Strength'].default_value = .4
sc.render.engine = 'CYCLES'
sc.cycles.samples = 16
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
