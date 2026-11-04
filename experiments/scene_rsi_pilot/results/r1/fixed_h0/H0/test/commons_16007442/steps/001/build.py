import bpy, math, random
from sceneact import *

random.seed(12)
scene = Scene("Electronics workbench")
ivory=(.69,.69,.61)
black=(.018,.022,.023)
gray=(.24,.27,.27)
red=(.56,.018,.012)
yellow=(.96,.63,.015)
wood=(.36,.20,.135)
counter=0

def add(n):
    global counter
    counter+=1
    scene.include("object_%04d"%counter,n)
    return n
def B(size,loc,col):
    return add(box(size=size,center=loc,color=col))
def R(radius,a,b,col):
    return add(rod(radius=radius,start=a,end=b,color=col))
def S(r,loc,col):
    return add(ball(radius=r,center=loc,color=col))
def W(points,r=.004,col=black):
    return add(sweep_tube(points=points,radius=r,color=col))
def localbox(parent,name,size,loc,col):
    parent.include(name,box(size=size,center=loc,color=col))
def localrod(parent,name,r,a,b,col):
    parent.include(name,rod(radius=r,start=a,end=b,color=col))

# Bench, walls, and a very narrow glimpse of the floor.
B((2.42,1.38,.075),(0,0,.70),wood)
B((2.55,.055,1.95),(0,.73,1.36),(.73,.73,.67))
B((.06,1.6,2.5),(-1.23,.0,1.05),(.49,.49,.44))
B((4,4,.08),(0,0,-.05),(.20,.20,.18))
for x in (-1.06,1.06):
    B((.07,1.12,.65),(x,0,.34),(.17,.17,.15))

# Storage cabinets on the upper wall, with individual translucent drawers.
for cx,cz,w,h,nc,nr in [(-.02,1.99,.64,.40,4,4),(.79,1.98,.86,.53,6,5)]:
    B((w,.17,h),(cx,.647,cz),(.035,.041,.039))
    for row in range(nr):
        for col in range(nc):
            dx=w/nc; dz=h/nr
            x=cx-w/2+dx*(col+.5)
            z=cz-h/2+dz*(row+.5)
            B((dx-.009,.025,dz-.009),(x,.547,z),(.19+random.random()*.055,.22,.21))
            B((dx*.36,.009,.016),(x,.529,z-.016),(.69,.71,.63))
            B((dx*.23,.012,.006),(x,.520,z+.006),(.10,.12,.11))
# Papers pinned beneath the cabinets.
for x,z,sx,sz in [(-.05,1.43,.39,.27),(.37,1.42,.39,.28),(.76,1.43,.30,.27)]:
    B((sx,.006,sz),(x,.687,z),(.87,.87,.81))
    for k in range(11):
        B((sx*random.uniform(.4,.84),.002,.0012),(x,.682,z+.09-k*.016),(.65,.66,.62))

# Computer monitor, slightly turned toward the bench.
monitor=Asset("monitor")
mx,my,mz=-.80,.40,1.43
localbox(monitor,"case",(.71,.061,.53),(mx,my,mz),(.018,.021,.023))
localbox(monitor,"blue rim",(.657,.006,.467),(mx,my-.034,mz),(.015,.37,.81))
localbox(monitor,"desktop",(.639,.004,.418),(mx,my-.038,mz+.012),(.13,.51,.81))
localbox(monitor,"taskbar",(.639,.005,.019),(mx,my-.041,mz-.207),(.018,.25,.68))
for k in range(2):
    localbox(monitor,"icon"+str(k),(.015,.005,.019),(mx-.02+k*.082,my-.043,mz-.008),(.88,.88,.80))
    localbox(monitor,"iconred"+str(k),(.010,.005,.007),(mx-.02+k*.082,my-.047,mz-.003),(.72,.13,.12))
    localbox(monitor,"caption"+str(k),(.043,.005,.002),(mx-.02+k*.082,my-.047,mz-.023),(.78,.87,.92))
localbox(monitor,"power",(.009,.006,.004),(mx+.27,my-.035,mz-.245),(.3,.63,.27))
monitor.turn('Z',11,pivot=(mx,my,mz))
add(monitor)
R(.022,(-.81,.43,1.17),(-.79,.45,.82),(.05,.05,.05))
B((.28,.22,.028),(-.79,.43,.759),(.035,.035,.034))

# Oscilloscope.
scope=Asset("oscilloscope")
localbox(scope,"body",(.54,.29,.295),(-.40,.35,.917),ivory)
localbox(scope,"front",(.525,.018,.274),(-.40,.194,.917),(.72,.73,.65))
localbox(scope,"screen bezel",(.272,.014,.225),(-.513,.178,.923),(.20,.22,.20))
localbox(scope,"screen",(.237,.009,.185),(-.513,.168,.923),(.065,.096,.092))
for j in range(9):
    localbox(scope,"vgrid"+str(j),(.001,.002,.175),(-.625+j*.028,.162,.923),(.13,.17,.15))
for j in range(7):
    localbox(scope,"hgrid"+str(j),(.23,.002,.001),(-.513,.161,.84+j*.027),(.13,.17,.15))
for i in range(4):
    for j in range(4):
        x=-.305+i*.040; z=.827+j*.056
        localrod(scope,"knob%d%d"%(i,j),.013 if j<3 else .010,(x,.159,z),(x,.141,z),(.64,.66,.59))
        localbox(scope,"label%d%d"%(i,j),(.023,.002,.002),(x,.158,z+.02),(.20,.23,.20))
for x in (-.61,-.19):
    localbox(scope,"foot"+str(x),(.055,.16,.021),(x,.34,.758),black)
scope.turn('Z',-3,pivot=(-.4,.35,.9))
add(scope)

# Power supply on the left.
B((.255,.25,.245),(-.94,.065,.874),(.60,.62,.54))
B((.238,.016,.224),(-.94,-.071,.874),(.64,.66,.58))
B((.177,.012,.069),(-.94,-.084,.929),(.15,.20,.17))
B((.127,.006,.035),(-.94,-.092,.931),(.31,.37,.28))
for x in (-1.015,-.94,-.87):
    R(.018,(x,-.085,.836),(x,-.107,.836),(.62,.65,.56))
for x,c in [(-1.01,red),(-.88,black)]:
    R(.009,(x,-.087,.796),(x,-.11,.796),c)

# Instrument behind central meter.
B((.38,.25,.105),(.12,.40,.805),(.035,.043,.044))
B((.37,.012,.093),(.12,.269,.805),(.025,.03,.03))
for x,c in [(-.015,yellow),(.072,ivory),(.155,black),(.235,red),(.276,red)]:
    R(.012,(x,.258,.805),(x,.245,.805),c)
# Cable and headphones on its top.
for x in (.00,.10):
    W([(x-.06,.42,.87),(x-.075,.39,.92),(x-.025,.36,.94),(x+.04,.39,.91)],.009,(.045,.055,.075))
B((.09,.055,.025),(.13,.39,.879),(.46,.49,.50))

# Yellow upright digital multimeter.
meter=Asset("upright multimeter")
localbox(meter,"rubber shell",(.179,.062,.334),(.37,.16,.96),yellow)
localbox(meter,"inset",(.148,.009,.291),(.37,.123,.966),(.18,.21,.20))
localbox(meter,"lcd rim",(.135,.007,.075),(.37,.116,1.057),(.11,.14,.13))
localbox(meter,"lcd",(.118,.004,.054),(.37,.111,1.06),(.49,.57,.46))
localrod(meter,"dial",.038,(.37,.113,.943),(.37,.098,.943),(.13,.15,.14))
localbox(meter,"pointer",(.009,.009,.035),(.37,.088,.951),(.56,.57,.48))
for k in range(12):
    a=k*math.tau/12
    localbox(meter,"dialmark"+str(k),(.010,.003,.004),(.37+.057*math.sin(a),.110,.943+.058*math.cos(a)),(.70,.70,.55))
for i,c in enumerate([black,black,red]):
    localrod(meter,"socket"+str(i),.009,(.325+i*.043,.114,.826),(.325+i*.043,.100,.826),c)
meter.turn('X',-11,pivot=(.37,.16,.795))
add(meter)

# Keyboard and separate keys on the foreground left.
keyboard=Asset("keyboard")
localbox(keyboard,"frame",(.78,.279,.032),(-.48,-.35,.769),(.035,.040,.043))
for row in range(5):
    for col in range(16):
        x=-.835+col*.046
        y=-.457+row*.047
        if row==0 and 4<=col<=9:
            continue
        localbox(keyboard,"key%d_%d"%(row,col),(.039,.039,.015),(x,y,.793),(.055,.062,.066))
        if random.random()<.55:
            localbox(keyboard,"legend%d_%d"%(row,col),(.009,.006,.001),(x-.008,y+.005,.801),(.46,.47,.43))
localbox(keyboard,"space",(.258,.036,.015),(-.54,-.457,.793),(.065,.070,.070))
keyboard.turn('Z',12,pivot=(-.48,-.35,.77))
add(keyboard)
# Mouse.
mouse=add(fillet_box(size=(.105,.16,.046),radius=.027,center=(-.26,-.09,.772),color=(.10,.12,.12)))
W([(-.25,-.01,.755),(-.22,.01,.76),(-.29,.11,.75),(-.20,.16,.75)],.004,black)

# Calculator at the lower left.
calc=Asset("calculator")
localbox(calc,"case",(.17,.265,.031),(-.99,-.515,.768),(.13,.16,.17))
localbox(calc,"face",(.157,.24,.008),(-.99,-.515,.788),(.70,.71,.64))
localbox(calc,"display",(.126,.049,.006),(-.99,-.435,.795),(.30,.37,.30))
for j in range(6):
    for i in range(4):
        localbox(calc,"button%d%d"%(i,j),(.027,.022,.009),(-1.043+i*.035,-.474-j*.027,.799),
                 (.09,.11,.13) if j<4 else (.24,.29,.29))
calc.turn('Z',-12,pivot=(-.99,-.515,.76))
add(calc)

# Loose circuit boards.
for x,y,s in [(-.66,.02,.16),(-.82,-.10,.12)]:
    B((s,.11,.008),(x,y,.755),(.025,.20,.33))
    for k in range(9):
        xx=x+random.uniform(-s*.4,s*.4)
        yy=y+random.uniform(-.04,.04)
        B((.017,.025,.011),(xx,yy,.765),(.04,.045,.04))
        for dx in (-.012,.012):
            R(.0018,(xx+dx,yy-.01,.764),(xx+dx,yy+.01,.764),(.55,.56,.51))
    for k in range(5):
        R(.006,(x-s*.38+k*.025,y+.035,.76),(x-s*.38+k*.025,y+.035,.785),(.07,.12,.17))

# Flat second multimeter amid tangled leads.
flat=Asset("small multimeter")
localbox(flat,"black body",(.14,.23,.036),(.245,-.205,.775),(.026,.032,.033))
localbox(flat,"yellow face",(.116,.196,.006),(.245,-.205,.796),(.74,.59,.055))
localbox(flat,"display",(.092,.055,.006),(.245,-.145,.801),(.34,.43,.36))
localrod(flat,"dial",.033,(.245,-.225,.800),(.245,-.225,.811),(.035,.042,.039))
for x in (.21,.28):
    localrod(flat,"port"+str(x),.009,(x,-.286,.80),(x,-.286,.807),black)
flat.turn('Z',-16,pivot=(.245,-.205,.78))
add(flat)

# Soldering station, white paper, coiled iron holder, and bottle at right.
paper=B((.37,.36,.003),(.77,.18,.747),(.88,.88,.82))
paper.turn('Z',-13)
for k in range(12):
    B((random.uniform(.09,.22),.0015,.001),(.78,.12+k*.012,.750),(.55,.57,.53))
B((.25,.26,.12),(.88,.43,.804),(.16,.20,.19))
B((.23,.014,.105),(.88,.291,.805),(.20,.24,.22))
R(.022,(.92,.28,.81),(.92,.254,.81),(.055,.06,.06))
# Soldering iron resting diagonally.
R(.026,(.78,.29,.86),(.94,.41,.96),(.08,.34,.35))
R(.015,(.69,.21,.81),(.79,.30,.87),(.055,.07,.075))
R(.006,(.61,.15,.773),(.70,.22,.82),(.49,.51,.48))
for k in range(15):
    t=k*math.tau/14
    x=.94+.034*math.cos(t)
    y=.46+.034*math.sin(t)
    R(.004,(x,y,.86+k*.005),(x,y,.865+k*.005),(.24,.25,.24))
R(.045,(.73,.53,.75),(.73,.53,.98),(.50,.53,.49))
R(.042,(.73,.53,.985),(.73,.53,.995),(.65,.66,.61))
R(.023,(1.075,.60,.75),(1.075,.60,.96),(.35,.40,.38))
R(.012,(1.075,.60,.95),(1.075,.60,1.04),(.45,.49,.45))
R(.019,(1.075,.60,1.04),(1.075,.60,1.06),(.10,.17,.29))

# Hanging pliers and cutters on the wall.
for x,z,scale in [(-.39,1.33,1),(-.24,1.30,.95),(-.04,1.31,.80)]:
    R(.008,(x,.655,z+.13),(x,.655,z+.21),(.16,.17,.15))
    R(.009,(x-.006,.63,z+.07),(x-.035,.625,z+.14),(.31,.32,.29))
    R(.009,(x+.006,.63,z+.07),(x+.035,.625,z+.14),(.31,.32,.29))
    W([(x,.623,z+.085),(x-.045,.62,z+.02),(x-.052,.62,z-.045),(x-.035,.62,z-.06)],.012,red)
    W([(x,.623,z+.085),(x+.041,.62,z+.025),(x+.050,.62,z-.043),(x+.034,.62,z-.06)],.012,red)
    S(.014,(x,.615,z+.065),(.30,.31,.27))

# Long black overhead task lamp and its adjustable arm.
R(.013,(1.02,.43,.76),(1.02,.47,1.39),black)
R(.013,(1.02,.47,1.39),(.88,.48,1.64),black)
R(.015,(.88,.48,1.64),(.65,.47,1.66),black)
S(.030,(1.02,.47,1.39),(.04,.045,.04))
lamp=Asset("long work lamp")
localbox(lamp,"hood",(.73,.19,.095),(.36,.40,1.655),(.015,.020,.020))
localbox(lamp,"underside",(.64,.135,.008),(.35,.40,1.602),(.60,.62,.56))
for i in range(16):
    localbox(lamp,"vent"+str(i),(.003,.14,.002),(.075+i*.021,.40,1.704),(.08,.09,.08))
lamp.turn('Z',-7,pivot=(.36,.4,1.65))
add(lamp)
W([(.94,.49,1.63),(1.07,.50,1.58),(1.04,.51,1.35),(1.10,.45,1.08),(1.06,.30,.76)],.006,black)

# Clear solder reel near the front.
R(.045,(-.18,-.43,.744),(-.18,-.43,.758),(.73,.75,.67))
R(.032,(-.18,-.43,.759),(-.18,-.43,.770),(.27,.42,.37))
R(.014,(-.18,-.43,.771),(-.18,-.43,.774),(.69,.70,.63))

# Large, naturally tangled test leads spread across the bench.
for i in range(16):
    cx=random.uniform(-.16,.58); cy=random.uniform(-.38,.04)
    rx=random.uniform(.10,.32); ry=random.uniform(.065,.18)
    phase=random.uniform(0,math.tau)
    pts=[]
    for k in range(49):
        t=phase+k*math.tau/40
        pts.append((cx+rx*math.cos(t),cy+ry*math.sin(t),.754+.004*math.sin(t*3+i)+i*.0007))
    W(pts,.0035,red if i%3==0 else black)
W([(.33,.10,.81),(.37,-.03,.76),(.58,-.10,.755),(.62,-.31,.758),(.40,-.46,.757),(.14,-.43,.76)],.005,red)
W([(.41,.11,.82),(.47,-.02,.75),(.64,-.14,.756),(.53,-.39,.76),(.25,-.55,.753)],.004,black)
for a,b,c in [((.13,-.56,.76),(.50,-.60,.76),red),
              ((.05,-.53,.77),(.42,-.57,.77),black),
              ((.54,-.28,.765),(.68,-.12,.765),red)]:
    R(.010,a,b,c)
    d=tuple(b[i]+(b[i]-a[i])*.22 for i in range(3))
    R(.003,b,d,(.54,.55,.50))
# Small clips and connectors scattered about.
for i in range(13):
    x=random.uniform(-.03,.62); y=random.uniform(-.51,-.08)
    a=random.random()*math.tau
    q=(x+.045*math.cos(a),y+.045*math.sin(a),.766)
    R(.006,(x,y,.766),q,red if i%2 else black)
    R(.002,q,(q[0]+.023*math.cos(a),q[1]+.023*math.sin(a),.766),(.60,.60,.51))

# Right-hand hand tools, scraps of yellow tape, component organizer.
for i in range(9):
    x=random.uniform(.67,.99); y=random.uniform(-.56,-.28)
    n=B((random.uniform(.027,.052),.022,.0015),(x,y,.749),(.94,.70,.06))
    n.turn('Z',random.uniform(-40,40))
for i in range(5):
    x=.87+i*.038
    R(.009,(x,-.58,.76),(x+.035,-.36,.77),(.40,.035,.018) if i%2 else (.07,.09,.12))
    R(.003,(x+.035,-.36,.77),(x+.047,-.28,.77),(.45,.47,.45))
B((.25,.28,.026),(1.06,-.41,.759),(.13,.17,.19))
for i in range(6):
    B((.014,.245,.007),(.96+i*.038,-.41,.78),(.40,.44,.44))
for j in range(4):
    B((.23,.009,.007),(1.06,-.515+j*.067,.78),(.40,.44,.44))
# A wire spool and loose accessories at the far right.
R(.057,(1.08,.03,.76),(1.08,.03,.84),(.15,.17,.16))
R(.073,(1.08,.03,.76),(1.08,.03,.77),(.40,.42,.39))
R(.073,(1.08,.03,.838),(1.08,.03,.848),(.40,.42,.39))
for k in range(10):
    R(.002,(.98,-.19+k*.009,.75),(1.12,-.19+k*.009,.75),(.48,.42,.27))
W([(.85,.26,.77),(.76,.04,.76),(.89,-.04,.76),(1.03,-.07,.76),(1.15,.06,.77),(1.17,.29,.80)],.007,black)

realize(scene)

# Small lettering is actual geometry on a few instrument faces.
def text_obj(body,loc,size,col,rotation=(math.pi/2,0,0)):
    curve=bpy.data.curves.new("printed marking","FONT")
    curve.body=body
    curve.size=size
    curve.extrude=0
    obj=bpy.data.objects.new("printed marking",curve)
    bpy.context.collection.objects.link(obj)
    obj.location=loc
    obj.rotation_euler=rotation
    mat=bpy.data.materials.new("ink")
    mat.diffuse_color=(*col,1)
    obj.data.materials.append(mat)
    return obj
text_obj("0.00",(.323,.081,1.038),.026,(.12,.19,.13), (math.radians(79),0,0))
text_obj("TEKTRONIX",(-.651,.154,1.044),.010,(.18,.21,.18))
text_obj("DIGITAL MULTIMETER",(.307,.103,1.007),.006,(.73,.73,.58),(math.radians(79),0,0))

# Matte surfaces with restrained highlights and small bevels.
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        if len(obj.data.polygons)>0:
            mat=obj.active_material
            if mat:
                mat.use_nodes=True
                bsdf=mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value=.70
            if len(obj.data.polygons)==6:
                mod=obj.modifiers.new("subtle edge rounding","BEVEL")
                mod.width=.0015
                mod.segments=1
                obj.modifiers.new("weighted corner normals","WEIGHTED_NORMAL")

set_view((1.04,-2.83,2.36),(-.015,.11,1.18),lens=44)
area_emitter((-.65,-1.3,2.8),power=180,size=2.5,target=(0,.1,.8),color=(1,.94,.84))
area_emitter((.15,.40,1.59),power=32,size=.65,target=(.25,-.1,.74),color=(.89,.95,1))
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.25,.27,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.40
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=32
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=388
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
