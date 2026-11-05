from sceneact import *
import bpy, math, random
random.seed(21)

scene = Scene("Daylit office")
white = (.88,.89,.86)
wall = (.79,.79,.74)
green = (.43,.47,.035)
metal = (.43,.46,.45)

def add(name, node):
    scene.include(name, node)
    return node

def bx(name, size, center, color):
    return add(name, box(size=size, center=center, color=color))

def rr(name, radius, start, end, color):
    return add(name, rod(radius=radius, start=start, end=end, color=color))

# Room shell and the broad ceiling soffit.
bx("gray stone floor", (4.5,8.8,.12), (2.1,1.8,-.06), (.40,.43,.42))
bx("back wall", (4.35,.16,3.4), (2.1,5.65,1.7), (.86,.87,.83))
bx("left plaster wall", (.16,8.5,3.4), (-.08,1.5,1.7), (.85,.86,.82))
bx("warm right wall", (.16,8.5,3.4), (4.33,1.5,1.7), (.66,.55,.46))
bx("ceiling", (4.5,8.7,.15), (2.1,1.5,3.43), (.86,.86,.81))
bx("ceiling transverse beam", (4.4,.52,.40), (2.1,.75,3.15), (.83,.83,.78))
bx("left skirting", (.055,7.8,.085), (.035,1.6,.043), (.40,.43,.41))
bx("rear skirting", (4.25,.045,.08), (2.1,5.54,.04), (.43,.45,.42))
bx("right skirting", (.05,7.7,.10), (4.22,1.6,.05), (.32,.34,.32))

# Tall glazed doors down the left side.
bx("window recess", (.035,3.27,2.73), (.016,3.00,1.64), (.61,.68,.67))
bx("bright glazing", (.028,3.13,2.59), (.04,3.00,1.64), (.76,.87,.89))
for y in (1.40,2.18,2.96,3.74,4.60):
    bx("window vertical frame "+str(y), (.095,.055,2.7), (.091,y,1.64), (.92,.94,.91))
for z in (.29,2.98):
    bx("window horizontal frame "+str(z), (.105,3.3,.065), (.09,3.0,z), (.93,.94,.91))
bx("window transom", (.09,3.25,.045), (.10,3.0,2.61), (.91,.93,.91))
bx("window sill", (.20,3.4,.075), (.1,3.0,.255), (.87,.88,.82))
bx("blind housing", (.20,3.45,.14), (.13,3.0,3.04), (.73,.72,.65))
rr("blind lower rail", .021, (.19,1.34,2.96), (.19,4.67,2.96), (.48,.46,.38))
for y in (2.24,3.80):
    rr("door handle "+str(y), .014, (.17,y,1.20), (.17,y,1.42), (.49,.53,.52))
bx("light switch", (.025,.095,.13), (.102,1.04,1.30), (.93,.93,.89))

# Heater against the rear wall.
bx("heater body", (.91,.20,.65), (.76,5.36,.43), (.87,.89,.88))
bx("heater top", (.91,.23,.025), (.76,5.35,.765), (.96,.96,.92))
for x in (.37,.48,.59,.70,.81,.92,1.03,1.14):
    bx("heater vent "+str(x), (.043,.014,.10), (x,5.248,.185), (.56,.60,.60))
for x in (.42,1.09):
    bx("heater foot "+str(x), (.055,.12,.12), (x,5.34,.10), (.62,.65,.64))

# Oak storage along the right wall.
bx("cabinet mass", (.47,4.08,1.12), (4.02,3.55,.58), (.59,.39,.22))
bx("oak top", (.53,4.11,.055), (3.99,3.55,1.17), (.70,.49,.28))
for i in range(6):
    yy=1.85+i*.67
    bx("cabinet door "+str(i), (.035,.655,1.045), (3.765,yy,.585), (.64+.025*(i%2),.44+.02*(i%2),.26))
    rr("cabinet handle "+str(i), .009, (3.735,yy-.10,.98), (3.735,yy+.10,.98), (.44,.39,.29))
# Fine long wood-grain streaks on the exposed fronts.
for i in range(105):
    yy=random.uniform(1.53,5.55)
    zz=random.uniform(.10,1.10)
    length=random.uniform(.06,.38)
    bx("oak grain "+str(i), (.002,length,.0025), (3.744,yy,zz),
       random.choice([(.48,.31,.17),(.73,.53,.32),(.57,.37,.20)]))

# White desk with a solid front modesty panel.
bx("desk top", (2.26,1.18,.075), (3.02,3.50,1.045), (.92,.93,.88))
bx("desk front", (2.20,.065,.77), (3.03,2.975,.62), (.86,.88,.83))
bx("desk right side", (.07,1.08,.98), (4.11,3.51,.52), (.86,.88,.84))
bx("desk left support", (.065,.93,.97), (1.94,3.56,.52), (.86,.88,.84))

# Two lime-green upholstered visitor chairs.
def visitor(name, x, y, yaw):
    a=Asset(name)
    def put(n,node): a.include(n,node)
    put("seat",fillet_box((.79,.69,.15),radius=.085,center=(x,y,.53),color=green))
    back=fillet_box((.80,.145,.76),radius=.085,center=(x,y-.30,.91),color=green)
    back.turn(axis="x",degrees=-5)
    put("back",back)
    for s in (-1,1):
        arm=fillet_box((.12,.51,.35),radius=.055,center=(x+s*.40,y+.025,.72),color=(.41,.46,.025))
        arm.turn(axis="x",degrees=-13)
        put("arm"+str(s),arm)
        put("seat bracket"+str(s),rod(radius=.022,start=(x+s*.31,y,.43),end=(x+s*.31,y-.30,.73),color=metal))
    put("pedestal",rod(radius=.028,start=(x,y,.10),end=(x,y,.48),color=metal))
    for j in range(4):
        an=math.radians(45+j*90)
        end=(x+.49*math.cos(an),y+.43*math.sin(an),.045)
        put("foot"+str(j),rod(radius=.024,start=(x,y,.10),end=end,color=metal))
        put("foot pad"+str(j),box((.09,.07,.026),center=(end[0],end[1],.025),color=(.22,.24,.22)))
    a.turn(axis="z",degrees=yaw,pivot=(x,y,.5))
    add(name,a)
visitor("left visitor chair",2.44,2.20,-3)
visitor("right visitor chair",3.70,2.14,10)

# Taller charcoal executive chair behind the desk.
add("executive back",fillet_box((.58,.15,.76),radius=.10,center=(2.68,4.71,1.18),color=(.30,.29,.25)))
add("executive seat",fillet_box((.59,.52,.13),radius=.065,center=(2.68,4.44,.75),color=(.29,.28,.24)))
rr("executive column",.038,(2.68,4.47,.15),(2.68,4.47,.73),(.33,.35,.34))
for j in range(5):
    an=j*math.tau/5
    rr("executive foot "+str(j),.021,(2.68,4.47,.18),(2.68+.35*math.cos(an),4.47+.35*math.sin(an),.08),metal)

# Thin desktop monitor, rear casing and stand visible.
bx("monitor stand foot", (.43,.24,.025), (3.35,3.91,1.101), (.61,.62,.60))
rr("monitor stalk",.026,(3.35,3.94,1.10),(3.35,4.00,1.36),(.57,.58,.57))
monitor=box((.64,.055,.49),center=(3.35,4.015,1.48),color=(.57,.55,.53))
monitor.turn(axis="x",degrees=-12)
monitor.turn(axis="z",degrees=-8)
add("monitor back",monitor)
add("monitor logo",ball(.018,center=(3.35,3.975,1.48),color=(.35,.34,.32)))
bx("keyboard",(.50,.17,.025),(3.20,3.66,1.098),(.77,.79,.76))
bx("paper stack",(.30,.23,.018),(2.96,3.45,1.096),(.94,.94,.91))
bx("desk organizer",(.16,.14,.16),(3.76,3.91,1.165),(.81,.82,.77))
for i in range(4):
    rr("pen "+str(i),.005,(3.72+i*.02,3.90,1.21),(3.71+i*.02,3.90,1.35),(.35,.38,.36))

# Ceramic cup on the desk.
rr("mug",.065,(3.67,3.66,1.09),(3.67,3.66,1.23),(.89,.90,.85))
add("mug handle",sweep_tube(points=[(3.72,3.66,1.21),(3.78,3.66,1.21),(3.79,3.66,1.14),(3.72,3.66,1.13)],radius=.011,color=(.86,.87,.82)))

# Potted plants with individually modelled, pointed elliptical leaves.
def leaf(name, center, length, width, direction, color):
    n=ball(radius=1,center=(0,0,0),color=color)
    n.resize((width*.5,width*.20,length*.5))
    n.turn(axis="y",degrees=direction[0],pivot=(0,0,0))
    n.turn(axis="z",degrees=direction[1],pivot=(0,0,0))
    n.move(center)
    add(name,n)

def plant(name,x,y,height,radius,base,seed):
    rng=random.Random(seed)
    rr(name+" pot",radius,(x,y,.02),(x,y,base),(.065,.075,.065))
    rr(name+" rim",radius*1.045,(x,y,base-.035),(x,y,base),(.10,.105,.085))
    rr(name+" soil",radius*.91,(x,y,base),(x,y,base+.006),(.075,.052,.025))
    rr(name+" trunk",.019,(x,y,base),(x,y,height*.91),(.27,.24,.12))
    for j in range(31):
        angle=rng.uniform(0,math.tau)
        z=rng.uniform(base+.13,height-.08)
        reach=rng.uniform(.15,.47)*(0.7+.3*(1-z/height))
        if height<1: reach*=.40
        ex=x+math.cos(angle)*reach
        ey=y+math.sin(angle)*reach
        ez=min(height,z+rng.uniform(.04,.21))
        rr(name+" branch "+str(j),.006,(x,y,z-.13),(ex,ey,ez),(.22,.29,.10))
        for k in range(5):
            t=.32+k*.15
            lx=x+(ex-x)*t
            ly=y+(ey-y)*t
            lz=z-.13+(ez-z+.13)*t
            side=(-1 if k%2 else 1)
            off=.055 if height>1 else .02
            lx+=side*off*math.sin(angle)
            ly-=side*off*math.cos(angle)
            length=rng.uniform(.105,.18) if height>1 else .055
            leaf(name+" leaf "+str(j)+" "+str(k),(lx,ly,lz),length,length*.43,
                 (rng.uniform(35,80),math.degrees(angle)+side*45),
                 rng.choice([(.065,.23,.025),(.12,.32,.035),(.18,.38,.055),(.075,.28,.035)]))
plant("rear ficus",1.88,4.82,2.00,.17,.34,51)
plant("foreground shrub",.15,.45,1.39,.23,.27,27)
plant("desk small plant",2.83,3.91,1.35,.052,1.17,73)

# Tiny flower vase and several pale blossoms.
rr("flower vase",.044,(2.63,3.71,1.085),(2.63,3.71,1.21),(.70,.74,.62))
for i in range(7):
    xx=2.63+random.uniform(-.075,.075)
    yy=3.71+random.uniform(-.055,.055)
    zz=random.uniform(1.25,1.37)
    rr("flower stem "+str(i),.003,(2.63,3.71,1.17),(xx,yy,zz),(.21,.37,.09))
    for k in range(5):
        an=k*math.tau/5
        add("petal",ball(.019,center=(xx+.022*math.cos(an),yy+.022*math.sin(an),zz),color=(.88,.84,.68) if i%3 else (.65,.16,.24)))

# Small framed abstract botanical artwork.
bx("picture frame", (.64,.045,.86), (2.86,5.535,2.22), (.31,.20,.12))
bx("picture inner border", (.595,.015,.815), (2.86,5.504,2.22), (.72,.58,.39))
bx("dark painting", (.555,.012,.775), (2.86,5.491,2.22), (.16,.17,.14))
for i in range(22):
    xx=random.uniform(2.62,3.08)
    zz=random.uniform(1.88,2.56)
    c=random.choice([(.57,.37,.16),(.68,.54,.31),(.32,.37,.28),(.72,.65,.45),(.28,.25,.18)])
    shape=ball(1,center=(0,0,0),color=c)
    shape.resize((random.uniform(.025,.065),.009,random.uniform(.04,.11)))
    shape.turn(axis="y",degrees=random.uniform(-65,65),pivot=(0,0,0))
    shape.move((xx,5.475,zz))
    add("painted leaf "+str(i),shape)
for i in range(9):
    xx=random.uniform(2.63,3.07)
    rr("painting stem "+str(i),.004,(2.85,5.462,1.86),(xx,5.462,random.uniform(2.15,2.58)),(.58,.47,.29))

# Ceiling panel light.
bx("ceiling panel surround", (.82,.91,.035), (2.14,4.11,3.335), (.83,.84,.80))
bx("ceiling luminous panel", (.74,.82,.018), (2.14,4.11,3.31), (.98,.99,.98))

realize(scene)

# Surface finishes retain broad, soft highlights.
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                p=mat.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value=.76
                    if "metal" in obj.name.lower() or "pedestal" in obj.name.lower() or "foot" in obj.name.lower():
                        p.inputs["Metallic"].default_value=.52
                        p.inputs["Roughness"].default_value=.31
                    if "luminous" in obj.name.lower():
                        p.inputs["Emission Color"].default_value=(1,1,1,1)
                        p.inputs["Emission Strength"].default_value=2.5

set_view(position=(1.61,-2.20,1.65),target=(1.91,5.60,1.65),lens=26,sensor=36)
area_emitter(position=(.32,2.65,2.24),power=650,size=3.0,target=(2.9,3.4,.7),color=(.85,.94,1.0))
area_emitter(position=(2.18,3.95,3.24),power=220,size=.85,target=(2.6,3.3,0),color=(1.0,.98,.91))
area_emitter(position=(1.3,-.8,2.8),power=130,size=4,target=(2.5,3.8,1.0),color=(1,.97,.89))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.76,.80,.83,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.35
