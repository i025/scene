from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(22)
scene = Scene('Crowded electronics workbench')
black=(.018,.022,.022)
dark=(.045,.052,.050)
cream=(.63,.65,.58)
silver=(.48,.51,.47)
red=(.58,.025,.015)
yellow=(.95,.66,.025)

def boxpart(name,size,center,color,parent=None):
    n=box(size,center=center,color=color)
    (scene if parent is None else parent).include(name,n)
    return n

# Main furniture and architecture.
boxpart('Brown laminate worktop',(2.12,1.42,.055),(0,0,.72),(.37,.235,.16))
boxpart('Back wall',(2.5,.045,1.8),(0,.735,1.58),(.56,.55,.48))
boxpart('Left wall',(.04,1.6,1.9),(-1.10,.02,1.55),(.37,.36,.30))

# Monitor.
monitor=Asset('Monitor assembly')
boxpart('Monitor foot',(.31,.22,.025),(-.69,.38,.767),black,monitor)
boxpart('Monitor neck',(.045,.055,.25),(-.69,.43,.90),black,monitor)
boxpart('Black monitor bezel',(.69,.060,.565),(-.69,.435,1.385),(.009,.012,.014),monitor)
boxpart('Blue display',(.632,.006,.494),(-.69,.400,1.393),(.025,.36,.81),monitor)
boxpart('Light blue desktop',(.622,.003,.444),(-.69,.395,1.411),(.14,.53,.91),monitor)
boxpart('Blue taskbar',(.625,.004,.020),(-.69,.391,1.173),(.015,.20,.65),monitor)
monitor.turn('z',11,pivot=(-.69,.435,1.385))
scene.include('Monitor',monitor)

# Oscilloscope.
boxpart('Oscilloscope housing',(.52,.29,.25),(-.40,.285,.90),cream)
boxpart('Oscilloscope face',(.509,.012,.232),(-.40,.134,.90),(.73,.74,.66))
boxpart('CRT dark bezel',(.248,.012,.190),(-.513,.123,.906),(.27,.29,.26))
boxpart('CRT glass',(.217,.005,.157),(-.513,.115,.906),(.055,.085,.080))
for x in [-.59,-.23]:
    boxpart('Oscilloscope foot'+str(x),(.045,.18,.022),(x,.28,.765),black)

# Stacked instruments beside the oscilloscope.
for i in range(2):
    z=.813+i*.131
    boxpart('Small instrument '+str(i),(.232,.235,.125),(-.852,.20,z),(.43,.46,.41))
    boxpart('Instrument front '+str(i),(.220,.010,.108),(-.852,.077,z),(.63,.65,.57))
    boxpart('Instrument display '+str(i),(.135,.005,.043),(-.88,.070,z+.018),(.075,.12,.095))
boxpart('Upper instrument vents',(.17,.16,.004),(-.852,.20,1.011),(.18,.22,.19))

# Power supply.
boxpart('Black power supply',(.31,.23,.125),(.013,.40,.818),(.018,.023,.022))
boxpart('Power supply top',(.30,.21,.008),(.013,.40,.884),(.22,.25,.23))

# Upright digital multimeter.
meter=Asset('Upright multimeter')
boxpart('Yellow rubber shell',(.172,.057,.309),(.285,.235,.954),yellow,meter)
boxpart('Dark meter face',(.143,.007,.273),(.285,.203,.958),(.20,.22,.20),meter)
boxpart('Display frame',(.130,.004,.091),(.285,.197,1.031),(.10,.13,.11),meter)
boxpart('LCD screen',(.116,.003,.064),(.285,.193,1.034),(.43,.51,.42),meter)
meter.turn('x',-12,pivot=(.285,.235,.80))
meter.turn('z',-7)
scene.include('Yellow multimeter',meter)

# Keyboard and circuit board.
keyboard=Asset('Keyboard')
boxpart('Keyboard body',(.79,.285,.030),(-.385,-.285,.771),(.045,.050,.048),keyboard)
keyboard.turn('z',15)
scene.include('Computer keyboard',keyboard)
boxpart('Blue circuit board',(.19,.125,.008),(-.57,-.015,.759),(.025,.15,.32))

# Notebook and papers.
for i in range(4):
    n=boxpart('Notebook paper '+str(i),(.345,.285,.0018),(.57,.135,.753+i*.002),(.86,.85,.78))
    n.turn('z',-12+i*3)
boxpart('Solder station',(.245,.23,.12),(.86,.285,.814),(.16,.22,.20))
boxpart('Solder station face',(.233,.009,.095),(.86,.165,.818),(.34,.39,.35))
boxpart('Solder stand base',(.18,.18,.025),(.76,.015,.768),(.27,.23,.16))

# Handheld meter on the tabletop.
handmeter=Asset('Handheld meter')
boxpart('Handheld meter case',(.108,.197,.035),(.155,-.20,.782),(.035,.046,.038),handmeter)
boxpart('Handheld yellow face',(.083,.171,.004),(.155,-.20,.802),(.72,.59,.05),handmeter)
boxpart('Handheld LCD',(.067,.052,.004),(.155,-.148,.806),(.38,.46,.36),handmeter)
handmeter.turn('z',-15)
scene.include('Handheld meter',handmeter)

# Calculator.
calculator=Asset('Calculator')
boxpart('Calculator body',(.175,.254,.026),(-.867,-.493,.779),(.045,.060,.053),calculator)
boxpart('Calculator face',(.155,.232,.004),(-.867,-.493,.794),(.64,.66,.59),calculator)
boxpart('Calculator LCD',(.126,.047,.003),(-.867,-.412,.798),(.24,.33,.27),calculator)
calculator.turn('z',15)
scene.include('Calculator',calculator)

# Wall drawers.
for name,cx,w,cols,rows,z,h in [
    ('Left cabinet',.03,.53,4,4,1.98,.47),
    ('Right cabinet',.70,.72,6,6,1.99,.57)]:
    boxpart(name,(w,.145,h),(cx,.674,z),(.025,.034,.032))

# Pinned sheets.
for i,(x,z,w,h) in enumerate([(-.02,1.48,.34,.29),(.32,1.47,.32,.28),(.64,1.48,.29,.29)]):
    boxpart('Wall paper '+str(i),(w,.003,h),(x,.704,z),(.83,.82,.74))

# Long overhead task lamp.
lamp=Asset('Task lamp')
boxpart('Lamp long black shade',(.69,.165,.067),(.365,.44,1.682),(.010,.015,.015),lamp)
boxpart('Lamp underside',(.59,.124,.005),(.35,.44,1.646),(.73,.75,.65),lamp)
boxpart('Lamp rounded end',(.105,.177,.077),(.735,.44,1.680),(.018,.023,.022),lamp)
lamp.turn('z',-11)
scene.include('Overhead light',lamp)

# Tool case on the near right.
case=Asset('Screwdriver case')
boxpart('Tool case tray',(.30,.35,.018),(.90,-.455,.761),(.19,.24,.24),case)
boxpart('Blue package header',(.30,.061,.006),(.90,-.312,.798),(.02,.15,.34),case)
boxpart('Red package stripe',(.30,.029,.006),(.90,-.356,.800),(.67,.04,.026),case)
case.turn('z',-8)
scene.include('Driver package',case)

realize(scene)

# Small repeated geometry is batched into material meshes to keep scene creation fast.
materials={}
batches={}
def material(c):
    key=tuple(c)
    if key not in materials:
        m=bpy.data.materials.new('Finish '+str(key))
        m.diffuse_color=(*key,1)
        m.use_nodes=True
        bs=m.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value=(*key,1)
        bs.inputs['Roughness'].default_value=.68
        materials[key]=m
    return materials[key]

def addpoly(c,verts,faces):
    key=tuple(c)
    if key not in batches:
        batches[key]=[[],[]]
    v,f=batches[key]
    off=len(v)
    v.extend(verts)
    f.extend([tuple(off+i for i in face) for face in faces])

def detailbox(center,size,c,angle=0):
    x,y,z=center
    a,b,d=[s/2 for s in size]
    ca,sa=math.cos(angle),math.sin(angle)
    verts=[]
    for zz in [-d,d]:
        for xx,yy in [(-a,-b),(a,-b),(a,b),(-a,b)]:
            verts.append((x+xx*ca-yy*sa,y+xx*sa+yy*ca,z+zz))
    addpoly(c,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

def cylinder(a,b,r,c,n=12,r2=None):
    a,b=Vector(a),Vector(b)
    axis=(b-a).normalized()
    ref=Vector((0,0,1)) if abs(axis.z)<.9 else Vector((0,1,0))
    u=axis.cross(ref).normalized()
    v=axis.cross(u).normalized()
    rr=r if r2 is None else r2
    verts=[]
    for p,rad in [(a,r),(b,rr)]:
        for i in range(n):
            t=i*2*math.pi/n
            verts.append(tuple(p+rad*(math.cos(t)*u+math.sin(t)*v)))
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    addpoly(c,verts,faces)

def wire(name,points,c=black,r=.004):
    cu=bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'
    cu.resolution_u=1
    cu.bevel_depth=r
    cu.bevel_resolution=1
    sp=cu.splines.new('POLY')
    sp.points.add(len(points)-1)
    for q,p in zip(sp.points,points):
        q.co=(*p,1)
    ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob)
    cu.materials.append(material(c))
    return ob

def rotate_xy(x,y,cx,cy,a):
    dx,dy=x-cx,y-cy
    return (cx+math.cos(a)*dx-math.sin(a)*dy,
            cy+math.sin(a)*dx+math.cos(a)*dy)

# Monitor's tiny desktop details.
for i,c in enumerate([(.9,.30,.12),(.25,.65,.20),(.20,.47,.84),(.92,.76,.06)]):
    x,y=rotate_xy(-.696+(i%2)*.014,.389,-.69,.435,math.radians(11))
    detailbox((x,y,1.394+(i//2)*.016),(.012,.003,.013),c,math.radians(11))
for i in range(4):
    x,y=rotate_xy(-.974+i*.017,.388,-.69,.435,math.radians(11))
    detailbox((x,y,1.173),(.008,.003,.007),(.63,.76,.87),math.radians(11))

# Keyboard keys with separate function row and numeric block.
a=math.radians(15)
for row in range(5):
    for col in range(14):
        x=-.755+col*.038
        y=-.389+row*.044
        x,y=rotate_xy(x,y,-.385,-.285,a)
        detailbox((x,y,.794),(.032,.035,.012),(.017,.021,.020),a)
        if (row+col)%3==0:
            detailbox((x-.004,y,.8005),(.008,.002,.0005),(.37,.39,.35),a)
for row in range(5):
    for col in range(3):
        x,y=rotate_xy(-.155+col*.040,-.389+row*.044,-.385,-.285,a)
        detailbox((x,y,.794),(.033,.035,.012),(.019,.023,.021),a)
for col in range(13):
    x,y=rotate_xy(-.753+col*.043,-.155,-.385,-.285,a)
    detailbox((x,y,.794),(.032,.019,.010),(.025,.029,.027),a)
x,y=rotate_xy(-.47,-.397,-.385,-.285,a)
detailbox((x,y,.800),(.19,.033,.008),(.022,.026,.024),a)

# Calculator keys.
for row in range(6):
    for col in range(4):
        x,y=rotate_xy(-.920+col*.035,-.461-row*.025,-.867,-.493,a)
        detailbox((x,y,.801),(.026,.019,.005),(.16,.20,.19) if row else (.32,.40,.39),a)

# Oscilloscope controls, fine markings and graticule.
for row in range(4):
    for col in range(4):
        x=-.348+col*.046
        z=.979-row*.047
        cylinder((x,.125,z),(x,.101,z),.010 if col<2 else .014,(.58,.60,.53))
        detailbox((x,.098,z+.006),(.002,.002,.008),(.24,.27,.24))
for i in range(8):
    detailbox((-.607+i*.027,.110,.906),(.0007,.001,.147),(.12,.17,.145))
for i in range(6):
    detailbox((-.513,.110,.834+i*.029),(.207,.001,.0007),(.12,.17,.145))
for i in range(7):
    detailbox((-.346+i*.026,.122,1.006),(.017,.004,.007),(.30,.33,.29))
for row in range(3):
    for col in range(7):
        detailbox((-.345+col*.022,.123,.993-row*.050),(.010,.002,.002),(.25,.29,.25))
for k in range(2):
    z=.813+k*.131
    for j in range(2):
        cylinder((-.809+j*.037,.068,z-.025),(-.809+j*.037,.049,z-.025),.013,(.55,.58,.50))
for i in range(9):
    detailbox((-.92+i*.017,.20,1.015),(.003,.13,.002),black)

# Small board components.
for i in range(7):
    x=-.645+random.random()*.15
    y=-.058+random.random()*.085
    detailbox((x,y,.773),(.026,.017,.015),(.025,.032,.029))
    for j in range(4):
        detailbox((x-.009+j*.006,y,.771),(.002,.026,.003),(.57,.60,.54))
for x in [-.65,-.49]:
    detailbox((x,-.007,.777),(.018,.028,.027),(.49,.51,.46))
for i,c in enumerate([yellow,black,red]):
    cylinder((-.065+i*.085,.28,.817),(-.065+i*.085,.263,.817),.013,c)
wire('Coiled supply cable',[(-.10,.45,.894),(-.13,.42,.97),(-.07,.38,.99),(.03,.40,.94),(.08,.48,.93),(-.03,.49,.93),(-.11,.44,.94)],(.19,.23,.26),.009)

# Upright meter detail positions follow its tilt.
def meterpoint(x,y,z):
    # Rotation about base followed by a slight turn about the body.
    t=math.radians(-12)
    yy=.235+(y-.235)*math.cos(t)-(z-.80)*math.sin(t)
    zz=.80+(y-.235)*math.sin(t)+(z-.80)*math.cos(t)
    xx,yy=rotate_xy(x,yy,.285,.267,math.radians(-7))
    return (xx,yy,zz)

cylinder(meterpoint(.285,.192,.925),meterpoint(.285,.176,.925),.035,black,20)
cylinder(meterpoint(.285,.173,.925),meterpoint(.301,.173,.949),.003,(.73,.74,.62),8)
for i in range(13):
    t=i*math.pi*2/13
    p=meterpoint(.285+.052*math.cos(t),.191,.925+.052*math.sin(t))
    detailbox(p,(.006,.003,.004),(.76,.77,.65))
for i in range(3):
    cylinder(meterpoint(.248+i*.037,.190,.841),meterpoint(.248+i*.037,.173,.841),.008,black)
for i in range(3):
    detailbox((.252+i*.028,.255,1.076),(.019,.002,.002),(.71,.73,.61))

# Handheld meter knob.
cylinder((.155,-.235,.807),(.155,-.235,.818),.027,black,18)
cylinder((.150,-.25,.819),(.164,-.225,.819),.002,(.69,.70,.57),8)

# Cabinets: dark frame, individually modeled drawers and pale labels.
for name,cx,w,cols,rows,z,h in [
    ('Left',.03,.53,4,4,1.98,.47),
    ('Right',.70,.72,6,6,1.99,.57)]:
    dw=(w-.02)/cols
    dh=(h-.023)/rows
    for row in range(rows):
        for col in range(cols):
            x=cx-w/2+.01+dw*(col+.5)
            zz=z-h/2+.012+dh*(row+.5)
            c=(.17+random.random()*.035,.20+random.random()*.03,.185+random.random()*.03)
            detailbox((x,.594,zz),(dw-.006,.016,dh-.007),c)
            detailbox((x,.583,zz-.012),(dw*.59,.003,dh*.24),(.60,.62,.54))
            detailbox((x,.575,zz+.006),(dw*.26,.013,.007),(.095,.12,.105))
            if random.random()>.25:
                detailbox((x,.580,zz-.013),(dw*.30,.002,.002),(.24,.27,.23))

# Pinned paper lines.
for x,z,w,h in [(-.02,1.48,.34,.29),(.32,1.47,.32,.28),(.64,1.48,.29,.29)]:
    for j in range(9):
        detailbox((x,.701,z+h*.32-j*.019),(w*random.uniform(.3,.8),.001,.001),(.60,.61,.54))
for i in range(16):
    detailbox((.58+random.uniform(-.06,.06),.04+i*.010,.763),
              (random.uniform(.035,.16),.0014,.001),(.48,.48,.44),math.radians(-8))

# Hanging pliers with bifurcated steel jaws and curved red handles.
for i,(x,z) in enumerate([(-.46,1.415),(-.34,1.40),(-.17,1.405)]):
    cylinder((x-.008,.666,z+.012),(x-.017,.668,z+.105),.007,(.24,.27,.24))
    cylinder((x+.008,.666,z+.012),(x+.007,.668,z+.105),.007,(.30,.32,.28))
    cylinder((x,.656,z+.010),(x,.644,z+.010),.013,(.36,.38,.32))
    wire('Red pliers handle left '+str(i),[(x-.005,.652,z+.007),(x-.025,.648,z-.031),(x-.030,.645,z-.075),(x-.019,.645,z-.084)],(.47,.045,.025),.009)
    wire('Red pliers handle right '+str(i),[(x+.005,.652,z+.007),(x+.030,.648,z-.028),(x+.041,.645,z-.066),(x+.032,.645,z-.079)],(.47,.045,.025),.009)

# Can and water bottle.
cylinder((.636,.43,.75),(.636,.43,.953),.044,(.60,.63,.56),24)
cylinder((.636,.43,.953),(.636,.43,.959),.047,(.72,.76,.68),24)
cylinder((.636,.43,.960),(.636,.43,.962),.035,(.36,.41,.36),24)
detailbox((.637,.421,.964),(.018,.026,.002),(.15,.20,.17))
for i in range(5):
    detailbox((.636,.385,.787+i*.027),(.040,.002,.012),(.18,.27,.20))
cylinder((.96,.55,.75),(.96,.55,.91),.045,(.40,.48,.43),20)
cylinder((.96,.55,.91),(.96,.55,.972),.045,(.48,.56,.49),20,r2=.018)
cylinder((.96,.55,.972),(.96,.55,1.024),.018,(.47,.56,.50),16)
cylinder((.96,.55,1.024),(.96,.55,1.05),.022,(.045,.13,.27),16)
for zz in [.78,.81,.84,.87]:
    cylinder((.96,.55,zz),(.96,.55,zz+.004),.046,(.45,.53,.47),20)

# Lamp arm.
cylinder((.835,.48,.75),(.835,.48,1.615),.011,(.035,.043,.039))
cylinder((.835,.48,1.615),(.69,.45,1.68),.018,black)
cylinder((.825,.46,1.61),(.85,.46,1.61),.030,black)
wire('Lamp power cord',[(.74,.45,1.68),(.89,.45,1.65),(.91,.43,1.55),(.85,.40,1.34),(.87,.40,.99),(.94,.14,.76)],black,.005)

# Soldering station and its iron.
cylinder((.81,.16,.82),(.81,.141,.82),.024,black)
detailbox((.917,.154,.829),(.024,.012,.034),(.58,.035,.018))
cylinder((.78,.09,.86),(.86,.25,1.01),.021,(.07,.27,.25))
cylinder((.78,.09,.86),(.706,-.026,.782),.006,(.57,.60,.54))
pts=[]
for j in range(170):
    t=j/169*math.pi*2*10
    f=j/169
    pts.append((.765+.033*math.cos(t),.005+f*.115,.81+f*.088+.033*math.sin(t)))
wire('Soldering iron spiral cradle',pts,(.25,.29,.25),.003)
wire('Iron electrical cable',[(.86,.25,1.01),(.91,.32,1.00),(.98,.22,.86),(.99,.06,.76),(.89,-.04,.76),(.78,.10,.76)],black,.006)

# Leads on tabletop: irregular loops rather than a regular coil.
for i in range(12):
    cx=random.uniform(-.10,.37)
    cy=random.uniform(-.41,-.13)
    rx=random.uniform(.12,.29)
    ry=random.uniform(.065,.175)
    phase=random.uniform(0,6)
    pts=[]
    for j in range(42):
        t=phase+j/41*math.pi*2.12
        xx=cx+rx*math.cos(t)+.015*math.sin(t*3+i)
        yy=cy+ry*math.sin(t)+.012*math.cos(t*2+i)
        zz=.764+.0015*i+.005*math.sin(t*2)**2
        pts.append((xx,yy,zz))
    wire('Loose test lead '+str(i),pts,red if i%3==0 else black,.0035 if i%3 else .0045)

wire('Red lead from upright meter',[meterpoint(.322,.173,.841),(.36,.12,.79),(.40,-.02,.77),(.45,-.20,.78),(.29,-.51,.78),(.02,-.48,.78)],red,.0045)
wire('Black lead from upright meter',[meterpoint(.283,.173,.841),(.28,.10,.79),(.24,-.06,.77),(.08,-.22,.78),(.16,-.47,.78),(.49,-.50,.78)],black,.0045)
wire('Keyboard cable',[(-.20,-.13,.77),(-.31,-.02,.76),(-.39,.05,.76),(-.34,.15,.76)],black,.006)
wire('Long front lead',[(-.56,-.30,.76),(-.57,-.52,.76),(-.42,-.62,.76),(-.10,-.61,.77),(.18,-.54,.78)],black,.004)

# Probes across the front edge.
for i,(x,y,dx,dy,c) in enumerate([
    (.10,-.54,.34,-.025,black),
    (.22,-.59,.32,-.015,red),
    (-.02,-.43,-.21,.11,black),
    (.43,-.33,.19,.15,red)]):
    cylinder((x,y,.785),(x+dx*.67,y+dy*.67,.785),.010,c)
    cylinder((x+dx*.67,y+dy*.67,.785),(x+dx,y+dy,.785),.0028,(.64,.66,.58))
    cylinder((x+dx*.59,y+dy*.59,.785),(x+dx*.65,y+dy*.65,.785),.014,c)
for i in range(5):
    x=random.uniform(-.08,.48)
    y=random.uniform(-.52,-.24)
    cylinder((x,y,.775),(x+.035,y+.015,.775),.006,(.48,.47,.36))

# Tape spool with a visible hole.
cylinder((-.20,-.39,.750),(-.20,-.39,.771),.040,(.75,.75,.64),24)
cylinder((-.20,-.39,.772),(-.20,-.39,.773),.025,(.34,.41,.34),24)
cylinder((-.20,-.39,.774),(-.20,-.39,.775),.016,(.72,.76,.65),20)
cylinder((-.20,-.39,.776),(-.20,-.39,.777),.010,(.27,.35,.28),16)

# Tape offcuts and scraps.
for i in range(14):
    detailbox((random.uniform(.51,.80),random.uniform(-.55,-.28),.751),
              (random.uniform(.026,.055),random.uniform(.016,.026),.0012),
              (.96,.72,.035),random.uniform(-1.2,1.2))
for i in range(6):
    detailbox((random.uniform(.55,.96),random.uniform(-.20,.03),.752),
              (.048,.032,.001),(.83,.82,.74),random.uniform(-.5,.5))

# Screwdrivers in their transparent retail tray.
for i in range(7):
    x=.78+i*.038
    x1,y1=rotate_xy(x,-.558,.90,-.455,math.radians(-8))
    x2,y2=rotate_xy(x,-.454,.90,-.455,math.radians(-8))
    x3,y3=rotate_xy(x,-.330,.90,-.455,math.radians(-8))
    cylinder((x1,y1,.783),(x2,y2,.783),.011,(.40,.035,.021))
    cylinder((x2,y2,.783),(x3,y3,.783),.003,(.52,.57,.53))
for i in range(4):
    x=.76+i*.09
    x1,y1=rotate_xy(x,-.62,.90,-.455,math.radians(-8))
    x2,y2=rotate_xy(x,-.29,.90,-.455,math.radians(-8))
    cylinder((x1,y1,.804),(x2,y2,.804),.002,(.42,.49,.47))

# Brush and small container at the right.
cylinder((.66,-.15,.762),(.75,-.29,.762),.012,(.33,.21,.12))
for i in range(19):
    xx=.75+random.uniform(-.034,.034)
    cylinder((xx,-.285,.766),(xx+.010,-.37,.766),.0015,(.37,.32,.22),6)
cylinder((.98,-.09,.75),(.98,-.09,.81),.066,(.14,.19,.17),24)
cylinder((.98,-.09,.811),(.98,-.09,.815),.069,(.38,.43,.38),24)
cylinder((.98,-.09,.816),(.98,-.09,.818),.055,(.18,.24,.20),24)

# Flush all detail batches.
for col,(verts,faces) in batches.items():
    mesh=bpy.data.meshes.new('Detailed components')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('Components '+str(col),mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material(col))

# Sparse readable labels.
def label(body,loc,size,color,rotation=(math.pi/2,0,0)):
    cu=bpy.data.curves.new('Printed marking','FONT')
    cu.body=body
    cu.size=size
    cu.extrude=0
    ob=bpy.data.objects.new(body,cu)
    bpy.context.collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=rotation
    cu.materials.append(material(color))
label('TEKTRONIX',(-.35,.119,1.011),.008,(.19,.23,.19))
label('CASIO',(-.916,-.398,.802),.009,(.19,.23,.19),(0,0,.26))
label('0.00',(.248,.239,1.027),.021,(.10,.16,.10))
label('Windows',(-.73,.386,1.364),.008,(.76,.85,.91))
label('PRECISION',(.80,-.318,.806),.012,(.76,.80,.77),(0,0,-.14))

set_view((.12,-2.43,2.47),(-.015,.13,1.175),lens=43,sensor=36)
area_emitter((-.55,-.60,2.65),power=170,size=1.55,target=(0,0,.80),color=(1,.94,.84))
area_emitter((.38,.38,1.61),power=24,size=.60,target=(.35,-.10,.74),color=(.91,.96,1))

sc=bpy.context.scene
sc.world.color=(.18,.18,.16)
sc.render.engine='CYCLES'
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.cycles.max_bounces=4
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
