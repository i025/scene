from sceneact import *
import bpy
import math
import random

random.seed(24)

CAMERA = (0.0, -3.8, 2.10)
TARGET = (-0.08, 1.5, 1.90)
LENS = 27
SHELF_HEIGHTS = (0.95, 1.60, 2.25, 2.95)
BENCH_W, BENCH_D, BENCH_Z = 3.95, 2.50, 0.75
RIGHT_RUN = 2.90
LEFT_RUN = 2.30
RIGHT_REAR = 2.185
LEFT_REAR = 2.045

scene = Scene("Old woodworking tool shop")
plaster = (.76, .78, .73)
oak = (.46, .265, .105)
honey = (.61, .37, .14)
darkwood = (.24, .13, .065)
iron = (.105, .12, .115)
steel = (.36, .39, .37)
black = (.045, .055, .05)
brass = (.50, .38, .17)

def wood():
    t = random.random()
    return (.28 + .30*t, .14 + .21*t, .055 + .085*t)

def put(parent, key, node):
    parent.include(key, node)
    return node

def block(parent, key, size, center, color):
    return put(parent, key, box(size=size, center=center, color=color))

def bar(parent, key, start, end, width, depth, color):
    dx, dy, dz = (end[i]-start[i] for i in range(3))
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    center = tuple((start[i]+end[i])/2 for i in range(3))
    node = box((width, depth, length), center=center, color=color)
    if abs(dy) < 1e-8:
        node.turn('y', math.degrees(math.atan2(dx, dz)), pivot=center)
    else:
        node.turn('x', -math.degrees(math.atan2(dy, dz)), pivot=center)
    return put(parent, key, node)

room = Asset("Plaster walls and window")
block(room, "back wall", (4.9,.12,5.2), (-.10,2.48,2.55), plaster)
block(room, "right wall", (.12,5.4,5.2), (2.25,-.15,2.55), (.78,.79,.74))
block(room, "left wall", (.12,5.4,5.2), (-2.55,-.15,2.55), (.71,.75,.71))
block(room, "floor", (4.8,6,.12), (-.15,-.25,-.08), (.31,.29,.23))
block(room, "window recess", (.045,2.50,3.90), (-2.47,.12,2.43), darkwood)
for j in range(3):
    for k in range(3):
        block(room, f"glass {j} {k}", (.025,.74,1.13),
              (-2.435,-.69+j*.80,1.17+k*1.20),
              (.32+.035*k,.57+.035*k,.66+.035*k))
for j in range(4):
    block(room, f"window upright {j}", (.09,.045,3.72),
          (-2.40,-1.09+j*.80,2.41), (.42,.38,.27))
for k in range(4):
    block(room, f"window cross rail {k}", (.10,2.48,.055),
          (-2.40,.11,.59+k*1.20), (.49,.44,.30))
scene.include("architecture", room)

shelves = Asset("Continuous wooden wall shelving")
for i,z in enumerate(SHELF_HEIGHTS):
    block(shelves, f"back shelf {i}", (4.55,.46,.065), (-.12,2.16,z), honey)
    block(shelves, f"back front edge {i}", (4.55,.045,.095),
          (-.12,1.925,z-.018), oak)
    block(shelves, f"right shelf {i}", (.48,RIGHT_RUN,.07),
          (1.99,RIGHT_REAR-RIGHT_RUN/2,z), honey)
    block(shelves, f"right front edge {i}", (.045,RIGHT_RUN,.105),
          (1.745,RIGHT_REAR-RIGHT_RUN/2,z-.017), oak)
    if i > 0:
        block(shelves, f"left shelf {i}", (.41,LEFT_RUN,.055),
              (-2.30,LEFT_REAR-LEFT_RUN/2,z), honey)
for i,x in enumerate((-2.18,-1.1,.15,1.45)):
    block(shelves, f"back narrow upright {i}", (.045,.07,2.55),
          (x,2.35,1.74), darkwood)
    for j,z in enumerate(SHELF_HEIGHTS):
        bar(shelves, f"bracket {i} {j}", (x,2.30,z-.28),
            (x,1.99,z-.035), .025,.035,iron)
scene.include("shelving", shelves)

def plane(name, position, length=.40, width=.16, height=.13,
          angle=0, metal=False, detailed=False):
    a = Asset(name)
    x,y,z = position
    c = darkwood if metal else wood()
    block(a, "sole", (length,width,.035), (x,y,z+.018), steel if metal else c)
    if metal:
        for side in (-1,1):
            block(a, f"cheek {side}", (length*.94,.018,height*.66),
                  (x,y+side*width*.45,z+height*.32), iron)
        block(a, "frog", (.10,width*.64,height*.50),
              (x-.015,y,z+height*.42), iron)
    else:
        block(a, "wood body", (length,width,height), (x,y,z+height*.50), c)
        block(a, "dark mouth", (.07,width*.88,.012),
              (x+.015,y,z+height+.003), darkwood)
    blade = box((.055,width*.68,height*1.05),
                center=(x+.015,y,z+height*.93), color=steel if metal else iron)
    blade.turn('y', -24)
    a.include("sloping iron", blade)
    if detailed or length > .36:
        put(a, "front knob", rod(radius=width*.20,
            start=(x+length*.29,y,z+height*.72),
            end=(x+length*.29,y,z+height*1.30), color=darkwood))
        put(a, "knob top", ball(radius=width*.235,
            center=(x+length*.29,y,z+height*1.32), color=darkwood))
        p0 = (x-length*.31,y,z+height*.72)
        p1 = (x-length*.37,y,z+height*1.65)
        p2 = (x-length*.19,y,z+height*1.82)
        p3 = (x-length*.12,y,z+height*.83)
        for j,(p,q) in enumerate(((p0,p1),(p1,p2),(p2,p3))):
            put(a, f"rear handle {j}",
                rod(radius=width*.115,start=p,end=q,color=darkwood))
    a.turn('z', angle, pivot=position)
    return a

toprow = Asset("Top shelf moulding planes")
for i in range(34):
    x = -2.20+i*.126
    h = random.uniform(.15,.31)
    a = Asset(f"narrow moulding plane {i}")
    c = wood()
    block(a, "body", (.095,random.uniform(.23,.36),h),
          (x,2.13,2.985+h/2), c)
    ironpiece = box((.028,.10,.17),center=(x,2.11,3+h),color=iron)
    ironpiece.turn('x', random.uniform(-22,-9))
    a.include("iron", ironpiece)
    toprow.include(f"plane {i}", a)
scene.include("upper moulding plane collection", toprow)

for row,z in enumerate(SHELF_HEIGHTS[:3]):
    rack = Asset(f"Back shelf tool collection {row}")
    count = 12 if row < 2 else 14
    for i in range(count):
        x = -2.13+i*(4.12/(count-1))
        length = random.uniform(.24,.40)
        a = plane(f"wood plane {row} {i}", (x,2.10,z+.038),
                  length=length,width=.20,height=random.uniform(.10,.18),
                  angle=random.uniform(-9,9),metal=(row==2 and i%3==0))
        rack.include(f"plane {i}", a)
    scene.include(f"back tool shelf {row}", rack)

for row,z in enumerate(SHELF_HEIGHTS):
    rack = Asset(f"Right shelf tool collection {row}")
    for i in range(7):
        y = -1.16+i*.48
        a = plane(f"right plane {row} {i}", (2,y,z+.04),
                  length=random.uniform(.29,.44),width=.19,
                  height=random.uniform(.12,.24),angle=90,
                  metal=(i%4==1 and row<3))
        rack.include(f"plane {i}", a)
    scene.include(f"right tool shelf {row}", rack)

chisels = Asset("Chisels and gouges beside the window")
for row,z in enumerate((1.60,2.25,2.95)):
    for i in range(9):
        y = -1.05+i*.34
        handle_h = random.uniform(.23,.43)
        base = z+.035
        put(chisels, f"steel shaft {row} {i}", rod(radius=.014,
            start=(-2.24,y,base),end=(-2.24,y,base+.22),color=steel))
        put(chisels, f"brass ferrule {row} {i}", rod(radius=.030,
            start=(-2.24,y,base+.18),end=(-2.24,y,base+.235),color=brass))
        put(chisels, f"wood handle {row} {i}",
            rod(radius=random.uniform(.035,.050),
                start=(-2.24,y,base+.235),
                end=(-2.24,y,base+.235+handle_h),color=wood()))
scene.include("window chisel racks", chisels)

walltools = Asset("Hanging squares dividers and hammers")
Y = 2.385
square_paths = [
    [(-2.05,Y,4.05),(-1.25,Y,4.85),(-.20,Y,3.81)],
    [(-1.93,Y,3.91),(-1.24,Y,4.57),(-.48,Y,3.82)],
    [(-1.68,Y,3.66),(-1.25,Y,4.08),(-.72,Y,3.57)]
]
for i,pts in enumerate(square_paths):
    for j in range(2):
        bar(walltools, f"square blade {i} {j}", pts[j],pts[j+1],
            .115 if i<2 else .14,.025,iron)
        p,q = pts[j],pts[j+1]
        bar(walltools, f"square edge {i} {j}",
            (p[0]+.025,p[1]-.017,p[2]),
            (q[0]+.025,q[1]-.017,q[2]), .012,.009,steel)
for i,(x,h,spread) in enumerate(((.09,1.20,.34),(.53,.88,.26),(.55,.47,.18))):
    top = (x,Y,4.67-i*.34)
    bar(walltools, f"divider left {i}", top,(x-spread,Y,top[2]-h),
        .032,.025,iron if i==0 else darkwood)
    bar(walltools, f"divider right {i}", top,(x+spread,Y,top[2]-h),
        .032,.025,iron if i==0 else darkwood)
    put(walltools, f"divider hinge {i}",ball(radius=.042,center=top,color=brass))
bar(walltools, "upright square",(-.51,Y,3.67),(-.51,Y,4.55),.055,.025,iron)
bar(walltools, "square horizontal",(-.51,Y,4.55),(-.82,Y,4.55),.075,.025,iron)
for i,(x,z,handle) in enumerate(((1.02,4.10,.86),(1.42,3.65,.63))):
    block(walltools, f"hammer handle {i}",(.075,.065,handle),(x,Y-.015,z),darkwood)
    block(walltools, f"hammer head {i}",(.39,.13,.13),(x,Y-.03,z+handle/2),iron)
    if i==0:
        block(walltools, "wood mallet head",(.36,.16,.17),(x,Y-.025,z+.45),darkwood)
for i,s in enumerate((-1,1)):
    put(walltools, f"brass compass leg {i}",rod(radius=.014,
        start=(.55,Y-.025,3.66),end=(.55+s*.16,Y-.025,3.32),color=brass))
put(walltools, "compass pivot",ball(radius=.035,center=(.55,Y-.025,3.66),color=steel))
bar(walltools, "old saw blade",(-2.54,Y,4.80),(-1.87,Y,4.55),.17,.025,steel)
block(walltools, "saw handle",(.25,.055,.22),(-1.86,Y-.01,4.57),darkwood)
scene.include("hanging wall tools", walltools)

hanging = Asset("High right wall planes")
for i in range(4):
    z = 3.52+i*.39
    y = .40+i*.21
    block(hanging, f"hanging body {i}",(.09,.58,.115),(2.17,y,z),darkwood)
    block(hanging, f"hanging steel sole {i}",(.035,.63,.025),(2.11,y,z-.065),steel)
    put(hanging, f"hanging knob {i}",rod(radius=.046,
        start=(2.11,y-.17,z+.03),end=(2,y-.17,z+.16),color=darkwood))
scene.include("right hanging planes", hanging)

bench = Asset("Heavy foreground workbench")
block(bench, "thick top",(BENCH_W,BENCH_D,.14),(-.12,-.31,BENCH_Z-.07),(.43,.29,.14))
block(bench, "front apron",(3.86,.12,.30),(-.12,-1.50,.53),oak)
for i,x in enumerate((-1.78,1.56)):
    for j,y in enumerate((-1.32,.64)):
        block(bench, f"leg {i} {j}",(.17,.18,.65),(x,y,.325),darkwood)
for i in range(5):
    block(bench, f"plank seam {i}",(3.87,.008,.003),
          (-.12,-1.29+i*.46,BENCH_Z+.002),(.20,.15,.085))
scene.include("workbench", bench)

chest = Asset("Open shallow wooden tool chest")
block(chest, "base",(1.27,.48,.08),(.38,.86,.85),darkwood)
block(chest, "back rail",(1.27,.055,.22),(.38,1.08,.98),oak)
for i,x in enumerate((-.23,.99)):
    block(chest, f"end {i}",(.055,.48,.22),(x,.86,.98),oak)
block(chest, "front rail",(1.27,.055,.13),(.38,.64,.90),honey)
scene.include("tool chest", chest)

for i in range(5):
    x = -1.66+i*.265
    y = -.83+(i%2)*.16
    a = plane(f"Foreground long metal plane {i}",(x,y,.77),
              length=random.uniform(.72,1.02),width=.19,height=.17,
              angle=76+random.uniform(-7,9),metal=True,detailed=True)
    scene.include(f"long iron plane {i}", a)
scene.include("central bench plane",
    plane("Central long bench plane",(.32,.06,.78),.93,.23,.16,-8,True,True))
scene.include("back wooden jointer",
    plane("Large wooden jointer",(.20,.64,.93),1.11,.22,.16,1,False,True))
scene.include("right foreground wooden plane",
    plane("Foreground wooden plane",(1.28,-.82,.77),.85,.24,.21,-25,False,True))
scene.include("small left wood plane",
    plane("Small left wooden plane",(-1.62,.36,.78),.57,.22,.16,12,False,False))

kettle = Asset("Black iron glue kettle")
kx,ky = -.62,.18
put(kettle, "body",ball(radius=.215,center=(kx,ky,.99),color=black))
put(kettle, "base",rod(radius=.166,start=(kx,ky,.775),end=(kx,ky,.84),color=iron))
put(kettle, "lid",rod(radius=.178,start=(kx,ky,1.135),end=(kx,ky,1.165),color=iron))
put(kettle, "lid knob",ball(radius=.035,center=(kx,ky,1.195),color=darkwood))
put(kettle, "spout",rod(radius=.049,start=(kx+.15,ky,1.02),
    end=(kx+.31,ky,1.16),color=iron))
put(kettle, "handle",sweep_tube(points=[
    (kx-.16,ky,1.09),(kx-.18,ky,1.36),(kx-.07,ky,1.45),
    (kx+.10,ky,1.43),(kx+.18,ky,1.33),(kx+.16,ky,1.09)],
    radius=.016,color=steel))
scene.include("kettle", kettle)

bottle = Asset("Cloudy pale bottle")
bx,by = -.08,-.03
put(bottle, "glass body",rod(radius=.092,start=(bx,by,.77),
    end=(bx,by,1.17),color=(.54,.59,.49)))
put(bottle, "shoulder",ball(radius=.091,center=(bx,by,1.16),color=(.55,.60,.51)))
put(bottle, "neck",rod(radius=.043,start=(bx,by,1.18),
    end=(bx,by,1.34),color=(.57,.62,.53)))
put(bottle, "cork",rod(radius=.040,start=(bx,by,1.33),
    end=(bx,by,1.37),color=(.46,.36,.22)))
block(bottle, "faded paper label",(.15,.012,.17),(bx,by-.09,1.005),(.69,.66,.50))
scene.include("pale bottle", bottle)

vise = Asset("Wooden bench vise and loose blocks")
block(vise, "fixed jaw",(.18,.58,.48),(1.12,.20,.99),oak)
block(vise, "moving jaw",(.15,.59,.42),(1.48,.20,.96),honey)
put(vise, "iron screw",rod(radius=.038,start=(1.12,.20,.96),
    end=(1.74,.20,.96),color=iron))
put(vise, "screw hub",rod(radius=.067,start=(1.68,.20,.96),
    end=(1.80,.20,.96),color=darkwood))
put(vise, "cross handle",rod(radius=.024,start=(1.75,-.07,.78),
    end=(1.75,.45,1.12),color=honey))
for i,(x,y,s) in enumerate(((.87,.48,.24),(1.48,.76,.28),(1.67,-.20,.21))):
    block(vise, f"loose block {i}",(s,.29,.15),(x,y,.825),wood())
scene.include("wood vise", vise)

# Open shallow basin, made entirely from explicit positive geometry.
# Sloped panels leave the interior open; no Boolean cutters are created.
bowl = Asset("Iron bowl filled with nails")
bc = (.68,-1.08,.94)
put(bowl, "basin bottom",rod(radius=.205,
    start=(bc[0],bc[1],.775),end=(bc[0],bc[1],.805),
    color=(.13,.15,.14)))
segments = 20
r0,r1 = .205,.320
z0,z1 = .798,1.045
slope_length = math.sqrt((r1-r0)**2+(z1-z0)**2)
slope_angle = math.degrees(math.atan2(r1-r0,z1-z0))
for i in range(segments):
    theta = 2*math.pi*i/segments
    center = (bc[0]+(r0+r1)*.5*math.cos(theta),
              bc[1]+(r0+r1)*.5*math.sin(theta),(z0+z1)*.5)
    panel = box((.025,2*r1*math.tan(math.pi/segments)*1.035,slope_length),
                center=center,color=(.13,.15,.14))
    panel.turn('y',slope_angle,pivot=center)
    panel.turn('z',math.degrees(theta),pivot=center)
    bowl.include(f"sloped basin panel {i}",panel)
    t1 = 2*math.pi*(i+1)/segments
    put(bowl,f"rim segment {i}",rod(radius=.015,
        start=(bc[0]+r1*math.cos(theta),bc[1]+r1*math.sin(theta),z1),
        end=(bc[0]+r1*math.cos(t1),bc[1]+r1*math.sin(t1),z1),
        color=iron))
for i in range(34):
    theta = random.uniform(0,2*math.pi)
    rad = random.uniform(.02,.24)
    x = bc[0]+rad*math.cos(theta)
    y = bc[1]+rad*math.sin(theta)
    z = .99+random.uniform(-.015,.065)
    angle = random.uniform(0,2*math.pi)
    length = random.uniform(.09,.18)
    end = (x+length*math.cos(angle),y+length*math.sin(angle),
           z+random.uniform(-.03,.03))
    put(bowl, f"nail {i}",rod(radius=.006,start=(x,y,z),end=end,color=steel))
    put(bowl, f"nail head {i}",ball(radius=.012,center=(x,y,z),color=steel))
scene.include("nail bowl", bowl)

loose = Asset("Loose bench tools and timber")
rule = Asset("Yellow wooden rule")
block(rule, "rule body",(1.48,.085,.025),(-.08,-1.25,.786),(.72,.51,.19))
for i in range(20):
    block(rule, f"graduation {i}",(.009,.025 if i%5 else .05,.003),
          (-.77+i*.071,-1.27,.801),darkwood)
rule.turn('z',-9,pivot=(-.08,-1.25,.786))
loose.include("folding rule",rule)
put(loose, "mallet handle",rod(radius=.033,start=(1.08,-1.62,.80),
    end=(1.60,-.97,.87),color=honey))
head = box((.46,.18,.18),center=(1.60,-.97,.89),color=honey)
head.turn('z',-34)
loose.include("mallet head",head)
for i,(x,y,ang) in enumerate(((-.44,-.61,11),(.02,-.65,-19))):
    n = box((.78,.065,.045),center=(x,y,.80+i*.025),color=honey)
    n.turn('z',ang)
    loose.include(f"offcut {i}",n)
for i in range(6):
    x = -1.68+i*.21
    y = -1.48+random.uniform(-.08,.08)
    n = box((.095,.39,.018),center=(x,y,.81),color=steel)
    n.turn('z',random.uniform(-32,24))
    loose.include(f"loose plane iron {i}",n)
    put(loose, f"iron slot {i}",rod(radius=.012,
        start=(x,y-.03,.823),end=(x,y+.06,.823),color=black))
put(loose, "brace crank",sweep_tube(points=[
    (-1.96,-.61,.85),(-1.79,-.55,.86),(-1.72,-.29,.88),
    (-1.52,-.25,.89),(-1.44,-.11,.89)],radius=.022,color=steel))
put(loose, "brace palm grip",ball(radius=.076,center=(-1.95,-.61,.86),color=honey))
put(loose, "brace turning grip",rod(radius=.045,
    start=(-1.76,-.48,.87),end=(-1.73,-.32,.88),color=darkwood))
for i,dx in enumerate((-.15,.15)):
    put(loose, f"bench divider {i}",rod(radius=.012,
        start=(.12,-.78,.81),end=(.38+dx,-1.10,.82),color=steel))
put(loose, "divider hinge",ball(radius=.025,center=(.12,-.78,.82),color=brass))
scene.include("loose tabletop objects",loose)

sign = Asset("Small yellow shelf card")
card = box((.27,.018,.23),center=(-1.46,2.03,3.23),color=(.77,.59,.23))
card.turn('y',-13)
sign.include("card",card)
for i in range(4):
    block(sign, f"ink mark {i}",(.012,.008,.055),
          (-1.54+i*.039,2.014,3.25),(.18,.13,.055))
scene.include("shelf label",sign)

realize(scene)

for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    base = tuple(bsdf.inputs["Base Color"].default_value[:3])
    r,g,b = base
    bsdf.inputs["Roughness"].default_value = .72
    is_wood = r>g*1.23 and g>b*1.25 and r>.16
    is_metal = max(base)-min(base)<.095 and r<.49
    if is_wood:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 3.8
        tex.inputs["Detail"].default_value = 2
        tex.inputs["Roughness"].default_value = .68
        coord = nodes.new("ShaderNodeTexCoord")
        stretch = nodes.new("ShaderNodeVectorMath")
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (2.5,29,5)
        links.new(coord.outputs["Generated"],stretch.inputs[0])
        links.new(stretch.outputs["Vector"],tex.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .17
        ramp.color_ramp.elements[0].color = tuple(v*.65 for v in base)+(1,)
        ramp.color_ramp.elements[1].position = .84
        ramp.color_ramp.elements[1].color = tuple(min(v*1.22,1) for v in base)+(1,)
        links.new(tex.outputs["Fac"],ramp.inputs[0])
        links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .17
        bump.inputs["Distance"].default_value = .025
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    elif is_metal:
        bsdf.inputs["Metallic"].default_value = .70
        bsdf.inputs["Roughness"].default_value = .48
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 34
        tex.inputs["Detail"].default_value = 2
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .19
        bump.inputs["Distance"].default_value = .012
        links.new(tex.outputs["Fac"],bump.inputs["Height"])
        links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter((-3,-.65,3.4),power=650,size=3.2,
             target=(0,.4,1.4),color=(.79,.90,1))
area_emitter((.4,-2.2,4.5),power=350,size=4,
             target=(0,1,1.4),color=(1,.94,.82))
area_emitter((1.3,1.2,4.5),power=180,size=2,
             target=(0,1.2,1.7),color=(1,.97,.89))

bscene = bpy.context.scene
if bscene.world is None:
    bscene.world = bpy.data.worlds.new("Workshop ambient world")
bscene.world.use_nodes = True
bscene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.72,.78,.82,1)
bscene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .30
bscene.view_settings.view_transform = 'AgX'
bscene.view_settings.exposure = .15
