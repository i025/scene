import bpy, math, random
from sceneact import *

random.seed(12)
scene = Scene("Electronics repair workbench")
black=(.018,.023,.024)
ivory=(.66,.68,.60)
red=(.57,.018,.012)
yellow=(.96,.64,.015)
metal=(.46,.49,.46)
serial=0

def add(node):
    global serial
    serial+=1
    scene.include("part_%03d"%serial,node)
    return node

def B(size,center,color):
    return add(box(size=size,center=center,color=color))

def R(radius,start,end,color):
    return add(rod(radius=radius,start=start,end=end,color=color))

# Architecture and work surface.
B((2.42,1.40,.075),(0,0,.70),(.39,.225,.16))
B((2.6,.055,2.2),(0,.735,1.40),(.69,.69,.63))
B((.055,1.6,2.5),(-1.24,.05,1.10),(.40,.41,.36))

# Large equipment shapes use SceneAct.
monitor=Asset("computer monitor")
for name,size,p,c in [
    ("housing",(.73,.065,.55),(-.80,.42,1.45),black),
    ("blue border",(.675,.006,.486),(-.80,.384,1.45),(.015,.26,.75)),
    ("desktop",(.653,.004,.432),(-.80,.379,1.463),(.14,.50,.82)),
    ("taskbar",(.653,.004,.019),(-.80,.376,1.238),(.015,.20,.63))]:
    monitor.include(name,box(size=size,center=p,color=c))
monitor.turn("Z",11,pivot=(-.80,.42,1.45))
add(monitor)
R(.022,(-.82,.45,1.17),(-.80,.47,.80),black)
B((.28,.22,.025),(-.80,.44,.755),black)

# Oscilloscope, with broad CRT and dense controls on its right.
B((.55,.31,.292),(-.41,.36,.90),ivory)
B((.54,.016,.27),(-.41,.196,.90),(.74,.75,.67))
B((.28,.015,.223),(-.525,.181,.907),(.24,.26,.23))
B((.242,.006,.186),(-.525,.169,.907),(.065,.095,.088))
for x in (-.62,-.20):
    B((.055,.15,.018),(x,.34,.748),black)
for i in range(4):
    for j in range(3):
        x=-.311+i*.043
        z=.821+j*.066
        R(.014,(x,.181,z),(x,.148,z),(.61,.64,.56))

# Power supply beneath left edge of monitor.
B((.253,.27,.237),(-.96,.065,.863),(.57,.60,.52))
B((.238,.012,.219),(-.96,-.078,.863),ivory)
B((.177,.009,.070),(-.96,-.088,.915),(.12,.17,.14))
B((.133,.004,.037),(-.96,-.094,.918),(.30,.37,.27))
for x in (-1.03,-.96,-.89):
    R(.017,(x,-.086,.824),(x,-.112,.824),ivory)

# Low black test instrument at the back.
B((.38,.26,.11),(.115,.41,.805),black)
for x,c in [(-.025,yellow),(.065,ivory),(.15,black),(.23,red),(.275,red)]:
    R(.011,(x,.27,.807),(x,.248,.807),c)
B((.095,.06,.025),(.14,.40,.877),(.42,.45,.47))

# Upright multimeter, angled back.
meter=Asset("yellow digital multimeter")
for name,size,p,c in [
    ("shell",(.18,.065,.343),(.36,.155,.958),yellow),
    ("face",(.148,.008,.291),(.36,.118,.965),(.16,.20,.19)),
    ("screen rim",(.135,.006,.076),(.36,.110,1.059),(.07,.10,.09)),
    ("screen",(.117,.004,.055),(.36,.105,1.062),(.46,.55,.43)),
    ("dial pointer",(.009,.008,.031),(.36,.078,.949),(.67,.68,.58))]:
    meter.include(name,box(size=size,center=p,color=c))
meter.include("selector",rod(radius=.037,start=(.36,.108,.943),end=(.36,.088,.943),color=(.10,.13,.12)))
for k in range(3):
    meter.include("socket"+str(k),rod(radius=.009,start=(.315+k*.043,.111,.824),end=(.315+k*.043,.097,.824),color=black))
meter.turn("X",-11,pivot=(.36,.155,.79))
add(meter)

# Keyboard, calculator, circuit boards and second multimeter.
kb=B((.79,.285,.027),(-.49,-.35,.759),(.035,.043,.045))
kb.turn("Z",12)
calc=B((.175,.268,.028),(-1.00,-.51,.757),(.12,.16,.17))
calc.turn("Z",-12)
B((.16,.11,.009),(-.67,.025,.750),(.02,.17,.28))
B((.13,.10,.009),(-.84,-.105,.750),(.025,.21,.28))
B((.105,.16,.043),(-.26,-.08,.761),(.09,.11,.12))
small=B((.14,.23,.037),(.23,-.205,.760),black)
small.turn("Z",-14)
face=B((.112,.196,.006),(.23,-.205,.782),(.73,.59,.055))
face.turn("Z",-14)
R(.032,(.23,-.227,.786),(.23,-.227,.797),black)

# Paper and soldering equipment at the right.
paper=B((.39,.38,.003),(.76,.19,.741),(.90,.90,.85))
paper.turn("Z",-14)
B((.26,.26,.12),(.90,.44,.799),(.15,.20,.19))
R(.022,(.94,.30,.81),(.94,.272,.81),black)
R(.026,(.80,.29,.85),(.97,.43,.96),(.07,.33,.35))
R(.014,(.69,.21,.80),(.81,.30,.86),(.045,.065,.065))
R(.004,(.61,.15,.754),(.70,.22,.807),metal)
R(.043,(.74,.54,.743),(.74,.54,.975),(.49,.52,.47))
R(.046,(.74,.54,.974),(.74,.54,.984),(.66,.67,.61))
R(.033,(1.085,.60,.745),(1.085,.60,.94),(.34,.40,.37))
R(.014,(1.085,.60,.93),(1.085,.60,1.025),(.42,.46,.42))
R(.018,(1.085,.60,1.025),(1.085,.60,1.05),(.08,.15,.29))

# Long black lamp across the upper right.
R(.012,(1.025,.42,.75),(1.025,.47,1.40),black)
R(.012,(1.025,.47,1.40),(.88,.48,1.65),black)
R(.015,(.88,.48,1.65),(.65,.45,1.66),black)
lamp=B((.76,.19,.089),(.35,.405,1.66),(.012,.017,.017))
lamp.turn("Z",-7)
under=B((.65,.13,.006),(.35,.405,1.611),(.55,.57,.51))
under.turn("Z",-7)

# Drawer cabinet carcasses.
B((.65,.17,.43),(-.015,.65,2.00),(.028,.035,.034))
B((.87,.17,.55),(.79,.65,1.99),(.027,.035,.034))

# Small solder reel and organizer.
R(.043,(-.18,-.43,.742),(-.18,-.43,.755),(.74,.76,.69))
R(.030,(-.18,-.43,.755),(-.18,-.43,.767),(.25,.41,.36))
R(.012,(-.18,-.43,.767),(-.18,-.43,.771),(.73,.74,.67))
B((.26,.28,.025),(1.07,-.43,.751),(.12,.16,.18))
R(.057,(1.09,.015,.742),(1.09,.015,.824),(.12,.15,.14))
for z in (.743,.824):
    R(.074,(1.09,.015,z),(1.09,.015,z+.009),(.37,.40,.36))

realize(scene)

# Batch small surface details into a few lightweight meshes.
batches={}
def detail(size,center,color,angle=0):
    key=tuple(color)
    if key not in batches:
        batches[key]=[[],[]]
    verts,faces=batches[key]
    base=len(verts)
    sx,sy,sz=[v/2 for v in size]
    a=math.radians(angle)
    ca,sa=math.cos(a),math.sin(a)
    for x,y,z in [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
                  (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]:
        verts.append((center[0]+ca*x-sa*y,center[1]+sa*x+ca*y,center[2]+z))
    for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        faces.append(tuple(base+i for i in f))

def xytransform(x,y,cx,cy,angle):
    a=math.radians(angle)
    return (cx+math.cos(a)*x-math.sin(a)*y,
            cy+math.sin(a)*x+math.cos(a)*y)

# Individual keyboard keys.
for row in range(5):
    for col in range(16):
        if row==0 and 4<=col<=9:
            continue
        x,y=xytransform(-.355+col*.046,-.105+row*.046,-.49,-.35,12)
        detail((.039,.038,.014),(x,y,.782),(.052,.061,.065),12)
        if random.random()<.55:
            detail((.008,.004,.001),(x-.006,y+.006,.790),(.40,.43,.40),12)
x,y=xytransform(-.032,-.105,-.49,-.35,12)
detail((.258,.036,.014),(x,y,.782),(.055,.063,.066),12)

# Calculator face and buttons.
x,y=xytransform(0,0,-1,-.51,-12)
detail((.16,.247,.005),(x,y,.774),(.69,.71,.63),-12)
x,y=xytransform(0,.078,-1,-.51,-12)
detail((.128,.048,.003),(x,y,.779),(.27,.35,.27),-12)
for j in range(6):
    for i in range(4):
        x,y=xytransform(-.053+i*.035,.030-j*.027,-1,-.51,-12)
        detail((.027,.021,.008),(x,y,.781),(.10,.13,.15),-12)

# Drawer fronts, labels and handles.
for cx,cz,w,h,nc,nr in [(-.015,2.00,.65,.43,4,4),(.79,1.99,.87,.55,6,6)]:
    for row in range(nr):
        for col in range(nc):
            dx,dz=w/nc,h/nr
            x=cx-w/2+dx*(col+.5)
            z=cz-h/2+dz*(row+.5)
            detail((dx-.009,.019,dz-.009),(x,.550,z),(.17,.20,.19))
            detail((dx*.46,.004,.019),(x,.537,z-.019),(.65,.69,.61))
            detail((dx*.25,.007,.006),(x,.532,z+.006),(.065,.085,.075))

# Papers pinned on wall.
for x in (-.055,.36,.73):
    detail((.37,.005,.27),(x,.687,1.43),(.86,.86,.80))
    for j in range(11):
        detail((random.uniform(.16,.30),.001,.001),(x,.683,1.52-j*.016),(.64,.65,.60))

# CRT grid, instrument labels, LCD detail.
for j in range(9):
    detail((.001,.001,.175),(-.635+j*.0275,.164,.907),(.12,.16,.13))
for j in range(7):
    detail((.23,.001,.001),(-.525,.163,.825+j*.027),(.12,.16,.13))
for j in range(4):
    for i in range(4):
        detail((.024,.001,.002),(-.311+i*.043,.184,.825+j*.051),(.24,.28,.23))
for k in range(12):
    a=k*math.tau/12
    detail((.009,.003,.003),(.36+.055*math.sin(a),.080,.945+.055*math.cos(a)),(.72,.73,.57))
x,y=xytransform(0,.060,.23,-.205,-14)
detail((.093,.052,.004),(x,y,.787),(.35,.43,.34),-14)

# Monitor login icons on the blue face.
for x in (-.82,-.745):
    xx,yy=xytransform(x+.80,-.045,-.80,.42,11)
    detail((.014,.003,.017),(xx,yy,1.448),(.87,.88,.80),11)
    detail((.010,.003,.006),(xx,yy-.002,1.452),(.70,.10,.10),11)
    detail((.040,.002,.002),(xx,yy-.002,1.430),(.77,.87,.94),11)

# PCB chips, connector strips, and paper print.
for cx,cy in [(-.67,.025),(-.84,-.105)]:
    for i in range(8):
        x=cx+random.uniform(-.055,.055)
        y=cy+random.uniform(-.037,.037)
        detail((.018,.025,.012),(x,y,.763),(.025,.035,.034))
        for dx in (-.012,.012):
            detail((.003,.026,.003),(x+dx,y,.759),(.51,.54,.47))
for i in range(11):
    detail((random.uniform(.08,.22),.0015,.001),(.77,.12+i*.012,.744),(.58,.60,.55))
for i in range(9):
    detail((random.uniform(.025,.055),.022,.0015),
           (random.uniform(.67,.98),random.uniform(-.56,-.28),.741),(.96,.72,.045),
           random.uniform(-40,40))
for i in range(6):
    detail((.008,.25,.006),(.965+i*.038,-.43,.768),(.36,.41,.41))
for j in range(4):
    detail((.24,.007,.006),(1.07,-.535+j*.07,.768),(.36,.41,.41))
for i in range(15):
    detail((.003,.14,.001),(.07+i*.024,.405,1.706),(.075,.085,.08),-7)

def material(color):
    mat=bpy.data.materials.new("surface")
    mat.diffuse_color=(*color,1)
    mat.use_nodes=True
    p=mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Roughness"].default_value=.7
    return mat

mats={}
def getmat(color):
    key=tuple(color)
    if key not in mats:
        mats[key]=material(key)
    return mats[key]

for col,(verts,faces) in batches.items():
    mesh=bpy.data.meshes.new("small equipment details")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new("equipment details",mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(getmat(col))

# Smooth cables are inexpensive Blender curve objects.
def wire(points,r=.0035,color=black):
    cv=bpy.data.curves.new("flexible cable","CURVE")
    cv.dimensions="3D"
    cv.resolution_u=1
    cv.bevel_depth=r
    cv.bevel_resolution=2
    sp=cv.splines.new("POLY")
    sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):
        p.co=(*co,1)
    ob=bpy.data.objects.new("cable",cv)
    bpy.context.collection.objects.link(ob)
    cv.materials.append(getmat(color))

# Loops with varying size and open tails.
for i in range(14):
    cx=random.uniform(-.12,.53)
    cy=random.uniform(-.38,-.02)
    rx=random.uniform(.12,.30)
    ry=random.uniform(.07,.17)
    phase=random.uniform(0,math.tau)
    points=[]
    for k in range(53):
        t=phase+k*math.tau/46
        points.append((cx+rx*math.cos(t),cy+ry*math.sin(t),
                       .748+i*.0009+.003*math.sin(3*t+i)))
    wire(points,.0031,red if i%3==0 else black)

wire([(.33,.10,.82),(.36,-.02,.76),(.57,-.10,.75),(.61,-.30,.754),
      (.43,-.47,.752),(.12,-.43,.754)],.0043,red)
wire([(.41,.10,.82),(.47,-.02,.75),(.64,-.14,.75),(.54,-.39,.75),
      (.25,-.55,.75)],.004,black)
wire([(-.25,-.01,.75),(-.22,.03,.75),(-.31,.13,.75),(-.20,.17,.75)],.0035)
wire([(.94,.49,1.65),(1.07,.50,1.58),(1.04,.51,1.35),
      (1.10,.45,1.08),(1.06,.30,.75)],.005)
wire([(.85,.26,.76),(.76,.04,.75),(.89,-.04,.75),(1.03,-.07,.75),
      (1.16,.06,.76),(1.17,.29,.79)],.006)
for x in (0,.10):
    wire([(x-.06,.42,.87),(x-.075,.39,.92),(x-.025,.36,.94),
          (x+.04,.39,.91)],.008,(.04,.05,.07))

# Hanging red-handled pliers.
for x,z in [(-.40,1.34),(-.24,1.31),(-.045,1.32)]:
    wire([(x-.028,.63,z+.17),(x-.018,.63,z+.10),(x+.015,.63,z+.045)],.008,metal)
    wire([(x+.028,.63,z+.17),(x+.018,.63,z+.10),(x-.015,.63,z+.045)],.008,metal)
    wire([(x,.623,z+.085),(x-.042,.62,z+.02),(x-.05,.62,z-.042),
          (x-.032,.62,z-.06)],.011,red)
    wire([(x,.623,z+.085),(x+.040,.62,z+.02),(x+.049,.62,z-.043),
          (x+.033,.62,z-.06)],.011,red)

# Metallic soldering iron holder.
wire([(.95+.032*math.cos(k*math.tau/14),
       .46+.032*math.sin(k*math.tau/14),.84+k*.0007)
      for k in range(145)],.003,metal)

# Test probes, clips, and scattered hand tools.
for a,b,c in [
    ((.09,-.54,.76),(.46,-.585,.76),black),
    ((.16,-.57,.75),(.54,-.61,.75),red),
    ((.53,-.28,.76),(.66,-.12,.76),red)]:
    wire([a,b],.009,c)
    end=tuple(b[k]+(b[k]-a[k])*.24 for k in range(3))
    wire([b,end],.0025,metal)
for i in range(11):
    x=random.uniform(-.03,.62)
    y=random.uniform(-.51,-.08)
    a=random.random()*math.tau
    q=(x+.042*math.cos(a),y+.042*math.sin(a),.761)
    wire([(x,y,.761),q],.0055,red if i%2 else black)
    wire([q,(q[0]+.023*math.cos(a),q[1]+.023*math.sin(a),.761)],.002,metal)
for i in range(5):
    x=.88+i*.039
    wire([(x,-.59,.75),(x+.034,-.37,.76)],.008,
         (.38,.035,.02) if i%2 else black)
    wire([(x+.034,-.37,.76),(x+.047,-.28,.76)],.0025,metal)

def label(body,position,size,color,rotation=(math.pi/2,0,0)):
    cv=bpy.data.curves.new("printed lettering","FONT")
    cv.body=body
    cv.size=size
    ob=bpy.data.objects.new("instrument label",cv)
    bpy.context.collection.objects.link(ob)
    ob.location=position
    ob.rotation_euler=rotation
    cv.materials.append(getmat(color))

label("0.00",(.314,.071,1.035),.025,(.10,.17,.11),(math.radians(79),0,0))
label("TEKTRONIX",(-.65,.180,1.018),.009,(.16,.20,.17))
label("DIGITAL MULTIMETER",(.300,.087,1.003),.006,(.71,.71,.56),(math.radians(79),0,0))

# Efficient lighting and rendering; no geometry booleans or per-object modifiers.
for obj in bpy.context.scene.objects:
    if obj.type=="MESH":
        for mat in obj.data.materials:
            if mat:
                mat.use_nodes=True
                p=mat.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value=.73

set_view((.57,-2.83,2.64),(-.02,.12,1.20),lens=45)
area_emitter((-.65,-1.25,2.85),power=170,size=2.1,
             target=(0,.1,.8),color=(1,.94,.85))
area_emitter((.25,.40,1.58),power=25,size=.60,
             target=(.3,-.1,.74),color=(.91,.96,1))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.25,.27,.28,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.35
sc=bpy.context.scene
sc.render.engine="CYCLES"
sc.cycles.samples=16
sc.cycles.use_denoising=True
sc.cycles.max_bounces=4
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
