from sceneact import *
import bpy, math, random
random.seed(23)

# Back wall occupies approximately (0.16,0.00)-(0.86,0.71).
# Four honey-colored shelf edges run near image y=.33,.45,.57,.68.
# The right shelving returns toward the viewer, filling the right edge.
# The blue-white window and upright chisels occupy the leftmost .16.
# Large black carpenter squares form nested diagonals across the upper wall.
# A crowded workbench obscures the lowest quarter of the room.

scene = Scene('Antique woodworking tool room')
WOOD = (.34,.16,.055)
HONEY = (.56,.30,.105)
DARKWOOD = (.20,.095,.035)
IRON = (.075,.085,.080)
STEEL = (.31,.32,.28)
WALL = (.71,.73,.67)

def add(parent, name, node):
    parent.include(name, node)
    return node

def beam(parent, name, a, b, width, depth, color):
    dx,dy,dz = (b[i]-a[i] for i in range(3))
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    q = box((width,depth,length), center=tuple((a[i]+b[i])/2 for i in range(3)),color=color)
    q.turn('y', math.degrees(math.acos(dz/length)))
    q.turn('z', math.degrees(math.atan2(dy,dx)))
    return add(parent,name,q)

room = Asset('Room architecture')
add(room,'back plaster',box((6.6,.13,4.6),center=(0,1.72,2.25),color=WALL))
add(room,'right plaster',box((.13,5.7,4.6),center=(3.23,-1.05,2.25),color=(.77,.77,.70)))
add(room,'left plaster',box((.12,4.7,4.6),center=(-3.23,-.7,2.25),color=(.68,.70,.64)))
add(room,'floor',box((6.5,6,.12),center=(0,-.8,-.08),color=(.25,.23,.17)))
add(room,'window recess',box((.025,2.25,2.85),center=(-3.15,-.08,2.20),color=(.17,.25,.26)))
for k in range(3):
    add(room,'window glass%d'%k,box((.03,.66,2.63),center=(-3.12,-.82+k*.73,2.22),color=(.48,.72,.79)))
for k in range(4):
    add(room,'window vertical%d'%k,box((.12,.055,2.93),center=(-3.06,-1.18+k*.73,2.22),color=(.70,.73,.67)))
for z in (.79,2.04,3.66):
    add(room,'window horizontal'+str(z),box((.14,2.4,.07),center=(-3.04,-.10,z),color=(.68,.71,.64)))
scene.include('architecture',room)

shelves=Asset('Wall shelves and brackets')
levels=(.98,1.58,2.22,2.94)
for j,z in enumerate(levels):
    add(shelves,'back shelf%d'%j,box((6.15,.48,.075),center=(0,1.36,z),color=HONEY))
    add(shelves,'right shelf%d'%j,box((.48,3.9,.075),center=(2.96,-.40,z),color=HONEY))
    for k,x in enumerate((-2.6,-1.1,.6,2.2)):
        add(shelves,'bracket%d_%d'%(j,k),box((.035,.32,.22),center=(x,1.48,z-.12),color=(.18,.19,.16)))
    for k in range(7):
        add(shelves,'back label%d_%d'%(j,k),box((.19,.008,.037),center=(-2.7+k*.84,1.114,z-.006),color=(.86,.83,.65)))
    for k in range(4):
        add(shelves,'right label%d_%d'%(j,k),box((.008,.20,.035),center=(2.716,-1.9+k*.92,z),color=(.85,.83,.67)))
scene.include('shelving',shelves)

def plane(name, pos, scale=1, angle=0, wooden=True):
    a=Asset(name)
    x,y,z=pos
    c=random.choice([WOOD,HONEY,DARKWOOD,(.39,.23,.10)])
    if wooden:
        add(a,'body',box((.43*scale,.17*scale,.145*scale),center=(x,y,z+.078*scale),color=c))
        add(a,'sole',box((.45*scale,.18*scale,.025*scale),center=(x,y,z+.012*scale),color=DARKWOOD))
    else:
        add(a,'metal sole',box((.47*scale,.18*scale,.035*scale),center=(x,y,z+.02*scale),color=IRON))
        add(a,'frog',box((.18*scale,.13*scale,.085*scale),center=(x,y,z+.07*scale),color=IRON))
        add(a,'rear handle',rod(.032*scale,start=(x+.15*scale,y,z+.05*scale),end=(x+.12*scale,y,z+.23*scale),color=DARKWOOD))
        add(a,'front knob',rod(.032*scale,length=.085*scale,center=(x-.16*scale,y,z+.075*scale),color=WOOD))
    blade=box((.065*scale,.13*scale,.24*scale),center=(x+.025*scale,y,z+.16*scale),color=STEEL)
    blade.turn('y',-27)
    add(a,'iron blade',blade)
    wedge=box((.07*scale,.115*scale,.15*scale),center=(x-.035*scale,y-.005,z+.14*scale),color=c)
    wedge.turn('y',-27)
    add(a,'blade wedge',wedge)
    a.turn('z',angle,pivot=(x,y,z))
    return a

# Packed rows of vintage molding planes: narrow upright wooden stocks above.
for k in range(42):
    x=-2.91+k*.141
    h=random.uniform(.15,.31)
    q=Asset('Upper molding plane %02d'%k)
    add(q,'stock',box((.105,.29,h),center=(x,1.38,3.00+h/2),color=random.choice([WOOD,HONEY,DARKWOOD])))
    iron=box((.034,.12,h*.75),center=(x,1.33,3.04+h*.65),color=STEEL)
    iron.turn('y',random.uniform(-20,10))
    add(q,'cutting iron',iron)
    scene.include('upper tool%d'%k,q)

for row,z in enumerate(levels[:3]):
    count=(12,13,12)[row]
    for k in range(count):
        x=-2.78+k*5.52/(count-1)
        p=plane('Back plane %d %d'%(row,k),(x,1.30,z+.045),
                random.uniform(.75,1.02),random.uniform(-7,7),wooden=(random.random()>.25))
        scene.include('back tool%d_%d'%(row,k),p)

# Deep return shelves on the right have larger block planes.
for row,z in enumerate(levels):
    for k in range(6):
        p=plane('Right shelf plane%d_%d'%(row,k),(2.95,-2.02+k*.63,z+.045),
                random.uniform(.95,1.25),90,wooden=(row!=0 or k%2==0))
        scene.include('return tool%d_%d'%(row,k),p)

walltools=Asset('Hanging squares saws and measuring tools')
# Three dramatic nested steel roofing squares on the upper left.
for k,(cx,top,span) in enumerate(((-1.38,4.46,1.25),(-1.38,4.15,1.05),(-1.38,3.83,.79))):
    beam(walltools,'square left%d'%k,(cx-span*.55,1.615,top-span*.59),(cx,1.615,top),.105,.035,IRON)
    beam(walltools,'square right%d'%k,(cx,1.615,top),(cx+span*.60,1.615,top-span*.58),.105,.035,IRON)
    beam(walltools,'square steel edge%d'%k,(cx-span*.52,1.586,top-span*.57),(cx,1.586,top-.025),.014,.012,STEEL)
for k in range(3):
    x=-.20+k*.46
    beam(walltools,'thin rule a%d'%k,(x-.18,1.60,3.48),(x+.07,1.60,4.30-k*.12),.045,.025,IRON)
    beam(walltools,'thin rule b%d'%k,(x+.07,1.60,4.30-k*.12),(x+.21,1.60,3.48),.035,.025,IRON)
for k in range(3):
    x=.83+k*.17
    beam(walltools,'divider left%d'%k,(x-.12,1.60,3.52+k*.20),(x,1.60,3.95+k*.20),.026,.025,DARKWOOD)
    beam(walltools,'divider right%d'%k,(x,1.60,3.95+k*.20),(x+.13,1.60,3.52+k*.20),.026,.025,DARKWOOD)
add(walltools,'large mallet shaft',box((.085,.08,.66),center=(1.63,1.57,3.88),color=WOOD))
add(walltools,'large mallet head',box((.36,.14,.15),center=(1.63,1.56,4.23),color=DARKWOOD))
add(walltools,'cross hammer handle',box((.065,.065,.51),center=(2.03,1.56,3.59),color=WOOD))
add(walltools,'cross hammer head',box((.42,.11,.10),center=(2.03,1.54,3.86),color=IRON))
beam(walltools,'long left saw',(-2.92,1.59,4.24),(-2.25,1.59,3.94),.18,.04,STEEL)
add(walltools,'saw handle',box((.25,.08,.22),center=(-2.91,1.55,4.26),color=DARKWOOD))
scene.include('hanging tools',walltools)

# Chisel racks against the left window.
racks=Asset('Window chisel racks')
for row,z in enumerate((1.20,2.35,3.34)):
    add(racks,'rack%d'%row,box((.18,2.35,.065),center=(-2.98,-.16,z),color=HONEY))
    for k in range(8):
        y=-1.15+k*.29
        h=random.uniform(.28,.46)
        add(racks,'handle%d_%d'%(row,k),rod(.042,start=(-2.96,y,z+.03),end=(-2.96,y,z+h),color=random.choice([WOOD,HONEY,DARKWOOD])))
        add(racks,'blade%d_%d'%(row,k),box((.025,.045,.23),center=(-2.96,y,z-.10),color=STEEL))
scene.include('left chisels',racks)

bench=Asset('Foreground workbench')
add(bench,'heavy top',box((5.65,2.05,.16),center=(-.10,-1.78,.73),color=(.31,.22,.115)))
for x in (-2.55,2.25):
    for y in (-2.45,-1.03):
        add(bench,'leg%s%s'%(x,y),box((.16,.16,.72),center=(x,y,.36),color=WOOD))
add(bench,'back apron',box((5.4,.11,.25),center=(-.1,-.88,.55),color=DARKWOOD))
scene.include('workbench',bench)

# A foreground jumble: bench planes, wooden gauges, chisels, oil can and hardware.
for k,(x,y,s,ang) in enumerate(((-1.4,-1.1,1.8,5),(.25,-1.04,1.9,3),
                               (1.68,-1.32,1.4,88),(-.35,-1.68,1.5,-14),
                               (.83,-2.02,1.65,12),(-2.10,-2.03,1.5,74))):
    scene.include('bench plane%d'%k,plane('Large bench plane%d'%k,(x,y,.82),s,ang,k%3!=1))

loose=Asset('Loose bench tools')
for k in range(9):
    x=-2.4+k*.19
    y=-2.12+random.uniform(-.16,.18)
    beam(loose,'chisel blade%d'%k,(x,y,.845),(x+.32,y+.68,.86),.055,.025,STEEL)
    beam(loose,'chisel handle%d'%k,(x+.32,y+.68,.87),(x+.46,y+.96,.91),.08,.065,random.choice([WOOD,HONEY,DARKWOOD]))
for k in range(5):
    x=-.9+k*.43
    beam(loose,'loose ruler%d'%k,(x,-2.52,.86),(x+.83,-1.98,.88),.065,.025,HONEY)
# Steel fasteners contained in two shallow dark trays.
for k,(x,y) in enumerate(((.82,-2.38),(1.15,-1.96))):
    add(loose,'tray bottom%d'%k,box((.71,.46,.035),center=(x,y,.85),color=IRON))
    for j in (-1,1):
        add(loose,'tray side%d_%d'%(k,j),box((.72,.025,.15),center=(x,y+j*.23,.91),color=STEEL))
        add(loose,'tray end%d_%d'%(k,j),box((.025,.46,.15),center=(x+j*.35,y,.91),color=STEEL))
    for j in range(13):
        a=(x+random.uniform(-.28,.28),y+random.uniform(-.17,.17),.90)
        b=(a[0]+random.uniform(-.09,.09),a[1]+.09,.92)
        add(loose,'nail%d_%d'%(k,j),rod(.008,start=a,end=b,color=(.52,.53,.48)))
# Oil can and stoppered pale bottle.
add(loose,'oil can',rod(.18,length=.31,center=(-.83,-1.45,1.00),color=IRON))
add(loose,'can lid',rod(.19,length=.035,center=(-.83,-1.45,1.17),color=STEEL))
beam(loose,'oil spout',(-.83,-1.45,1.18),(-.77,-1.43,1.47),.025,.025,STEEL)
add(loose,'bottle',rod(.095,length=.40,center=(-.13,-1.47,1.04),color=(.48,.50,.37)))
add(loose,'bottle shoulder',ball(.096,center=(-.13,-1.47,1.23),color=(.48,.50,.37)))
add(loose,'bottle neck',rod(.040,length=.15,center=(-.13,-1.47,1.31),color=(.58,.58,.43)))
add(loose,'bottle label',box((.14,.012,.18),center=(-.13,-1.569,1.04),color=(.75,.72,.56)))
add(loose,'mallet head',box((.48,.25,.25),center=(2.02,-2.08,1.02),color=HONEY))
beam(loose,'mallet handle',(1.91,-2.13,1.02),(1.48,-2.87,.84),.075,.075,WOOD)
scene.include('bench contents',loose)

realize(scene)
CAMERA_POSITION = (-.38,-6.45,2.80)
CAMERA_TARGET = (0, .65, 2.05)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=32,sensor=36)
area_emitter((-3,-1.1,3.25),power=1150,size=3.0,target=(0,.5,1.4),color=(.86,.94,1))
area_emitter((.5,-3.4,4.7),power=900,size=4,target=(0,.6,1.5),color=(1,.92,.78))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.63,.69,.72,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
for mat in bpy.data.materials:
    mat.use_nodes=True
    p=mat.node_tree.nodes.get('Principled BSDF')
    if not p:
        continue
    col=p.inputs['Base Color'].default_value
    p.inputs['Roughness'].default_value=.72
    if col[0] > col[2]*1.7 and col[0] < .7:
        nodes=mat.node_tree.nodes
        tex=nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=7
        tex.inputs['Detail'].default_value=2
        mapping=nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(3,34,5)
        coord=nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
        mat.node_tree.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.17
        bump.inputs['Distance'].default_value=.035
        mat.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    elif abs(col[0]-col[1]) < .055 and col[0] < .55:
        p.inputs['Metallic'].default_value=.55
        p.inputs['Roughness'].default_value=.48
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
