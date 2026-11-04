from sceneact import *
import bpy, math, random
random.seed(22)

scene = Scene('Electronics workbench')
brown=(.34,.20,.13)
black=(.018,.022,.024)
gray=(.55,.56,.51)
cream=(.67,.68,.60)
red=(.56,.025,.018)
yellow=(.95,.62,.025)

def block(name, size, pos, col, parent=None):
    node=box(size,center=pos,color=col)
    (parent or scene).include(name,node)
    return node
def bar(name,a,b,r,col,parent=None):
    node=rod(r,start=a,end=b,color=col)
    (parent or scene).include(name,node)
    return node
def cable(name, pts, col=black, r=.006, parent=None):
    node=sweep_tube(points=pts,radius=r,color=col)
    (parent or scene).include(name,node)
    return node
def text_obj(body,loc,size,col,rotation=(math.pi/2,0,0)):
    cu=bpy.data.curves.new('Label','FONT')
    cu.body=body
    cu.size=size
    cu.extrude=.0001
    ob=bpy.data.objects.new('Printed '+body,cu)
    bpy.context.collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=rotation
    ma=bpy.data.materials.new('Ink')
    ma.diffuse_color=(*col,1)
    ob.data.materials.append(ma)
    return ob

block('Desktop',(2.05,1.32,.065),(0,0,.72),brown)
block('Back wall',(2.6,.055,1.9),(0,.72,1.56),(.58,.57,.49))
block('Left wall',(.06,1.6,2),(-1.09,.05,1.5),(.36,.35,.29))
for x in [-.86,.86]:
    block('Desk leg '+str(x),(.07,.08,.72),(x,.25,.34),(.20,.17,.13))

# Wall-mounted parts cabinets, with individual translucent-looking drawers.
for name,cx,w,cols,rows,z in [('left',.08,.51,4,4,1.94),('right',.70,.67,6,6,1.95)]:
    block(name+' cabinet',(w,.16,.51),(cx,.665,z),(.035,.044,.043))
    dw=(w-.022)/cols
    dh=.477/rows
    for rr in range(rows):
        for cc in range(cols):
            x=cx-w/2+.011+dw*(cc+.5)
            zz=z-.239+dh*(rr+.5)
            block(f'{name} drawer {rr} {cc}',(dw-.008,.018,dh-.009),(x,.573,zz),(.19,.22,.21))
            block(f'{name} drawer label {rr} {cc}',(dw*.58,.004,dh*.24),(x,.561,zz-.013),(.61,.61,.53))
            block(f'{name} pull {rr} {cc}',(dw*.26,.013,.008),(x,.551,zz+.006),(.10,.12,.115))

# Pinned work sheets on back wall.
for i,(x,z,w,h) in enumerate([(-.01,1.48,.35,.28),(.34,1.45,.34,.26),(.65,1.48,.26,.29)]):
    block('Pinned paper '+str(i),(w,.003,h),(x,.681,z),(.83,.82,.73))
    for j in range(7):
        block(f'Paper line {i} {j}',(w*.72,.002,.001),(x,.678,z+h*.30-j*.021),(.57,.58,.53))

# Monitor, slightly turned toward the center of the desk.
monitor=Asset('Monitor')
block('Foot',(.32,.22,.025),(-.65,.39,.77),black,monitor)
bar('Monitor stem',(-.65,.43,.78),(-.65,.44,1.10),.035,black,monitor)
block('Monitor shell',(.66,.075,.56),(-.65,.45,1.38),(.012,.016,.018),monitor)
block('Display',(.607,.007,.487),(-.65,.408,1.39),(.025,.37,.82),monitor)
block('Bright desktop',(.596,.002,.434),(-.65,.403,1.407),(.13,.53,.89),monitor)
block('Taskbar',(.598,.003,.024),(-.65,.399,1.175),(.015,.22,.65),monitor)
for i in range(3):
    block('Taskbar icon '+str(i),(.009,.003,.009),(-.93+i*.017,.396,1.175),(.60,.76,.87),monitor)
for i,col in enumerate([(.9,.3,.15),(.3,.65,.2),(.2,.5,.9),(.95,.8,.1)]):
    block('Windows logo '+str(i),(.012,.003,.013),(-.655+(i%2)*.014,.398,1.389+(i//2)*.016),col,monitor)
block('Monitor power light',(.007,.003,.004),(-.388,.403,1.126),(.1,.8,.3),monitor)
monitor.turn('z',9,pivot=(-.65,.45,1.38))
scene.include('Computer monitor',monitor)

# Oscilloscope at the rear of the bench.
scope=Asset('Oscilloscope')
block('Scope case',(.51,.30,.245),(-.39,.26,.9),cream,scope)
block('Scope front',(.50,.017,.226),(-.39,.101,.9),(.70,.71,.64),scope)
block('Scope screen bevel',(.246,.012,.186),(-.493,.087,.909),(.24,.27,.25),scope)
block('Scope glass',(.218,.008,.158),(-.493,.078,.909),(.075,.12,.12),scope)
for k in range(8):
    block('Scope grid vertical '+str(k),(.001,.002,.15),(-.594+k*.029,.073,.909),(.14,.20,.18),scope)
for k in range(6):
    block('Scope grid horizontal '+str(k),(.21,.002,.001),(-.493,.073,.837+k*.029),(.14,.20,.18),scope)
for rr in range(4):
    for cc in range(4):
        xx=-.33+cc*.044
        zz=.976-rr*.046
        bar(f'Scope knob {rr} {cc}',(xx,.082,zz),(xx,.058,zz),.012 if cc<2 else .015,(.66,.66,.60),scope)
for i in range(7):
    block('Scope upper key '+str(i),(.019,.007,.008),(-.337+i*.025,.077,1.002),(.28,.31,.29),scope)
for x in [-.57,-.23]:
    block('Scope foot '+str(x),(.055,.17,.018),(x,.25,.767),black,scope)
scene.include('Oscilloscope',scope)

# Small stacked bench instruments on the left.
for k in range(2):
    zz=.81+k*.134
    block('Small instrument '+str(k),(.225,.23,.128),(-.835,.14,zz),(.44,.47,.42))
    block('Small instrument face '+str(k),(.214,.008,.11),(-.835,.019,zz),(.61,.63,.56))
    block('Small instrument screen '+str(k),(.125,.006,.046),(-.858,.011,zz+.019),(.09,.15,.12))
    for j in range(2):
        bar(f'Small dial {k} {j}',(-.79+j*.037,.007,zz-.025),(-.79+j*.037,-.011,zz-.025),.014,(.56,.57,.51))
block('Top instrument vent',(.15,.17,.006),(-.835,.14,1.012),(.23,.26,.23))
for i in range(9):
    block('Instrument vent '+str(i),(.003,.13,.003),(-.9+i*.016,.14,1.017),black)

# Black power supply behind meters.
block('Power supply',(.31,.22,.13),(.035,.38,.83),(.025,.03,.03))
block('Power supply top',(.29,.20,.009),(.035,.38,.901),(.25,.27,.25))
for i,c in enumerate([yellow,black,red]):
    bar('Supply socket '+str(i),(-.045+i*.081,.262,.835),(-.045+i*.081,.244,.835),.014,c)
for i in range(2):
    cable('Supply cable '+str(i),[(.03,.41,.91),(-.01,.40,1),(-.12,.44,.97),(-.10,.49,.91),(.09,.44,.93)],(.23,.27,.31),.009)

# Upright yellow multimeter.
meter=Asset('Yellow multimeter')
block('Yellow rubber body',(.17,.053,.30),(.29,.23,.945),yellow,meter)
block('Meter face',(.143,.008,.266),(.29,.198,.949),(.19,.21,.20),meter)
block('LCD surround',(.132,.005,.09),(.29,.192,1.025),(.11,.14,.13),meter)
block('LCD',(.117,.004,.065),(.29,.188,1.029),(.47,.56,.47),meter)
bar('Selector knob',(.29,.185,.921),(.29,.169,.921),.037,black,meter)
bar('Selector pointer',(.29,.165,.921),(.308,.164,.944),.004,(.72,.72,.65),meter)
for i in range(12):
    a=2*math.pi*i/12
    block('Meter scale '+str(i),(.007,.003,.005),(.29+.051*math.cos(a),.186,.921+.051*math.sin(a)),(.76,.77,.63),meter)
for i in range(3):
    bar('Meter plug '+str(i),(.25+i*.04,.184,.835),(.25+i*.04,.168,.835),.009,black,meter)
meter.turn('x',-13,pivot=(.29,.23,.80))
meter.turn('z',-8)
scene.include('Digital multimeter',meter)

# Keyboard with its many raised dark keycaps.
keyboard=Asset('Keyboard')
block('Keyboard base',(.78,.29,.026),(-.39,-.30,.773),(.045,.049,.048),keyboard)
for rr in range(5):
    for cc in range(15):
        x=-.755+cc*.039
        y=-.408+rr*.047
        block(f'Key {rr} {cc}',(.033,.038,.012),(x,y,.795),(.018+.005*(cc%3),.021+.005*(cc%3),.022+.005*(cc%3)),keyboard)
block('Space bar',(.205,.035,.013),(-.45,-.42,.798),(.022,.025,.024),keyboard)
for rr in range(5):
    for cc in range(3):
        block(f'Number pad {rr} {cc}',(.036,.037,.012),(-.13+cc*.043,-.405+rr*.047,.795),(.022,.025,.024),keyboard)
keyboard.turn('z',15)
scene.include('Keyboard',keyboard)

# Blue circuit board near the oscilloscope.
block('Blue circuit board',(.18,.12,.008),(-.57,-.025,.765),(.025,.15,.32))
for i in range(8):
    x=-.64+random.random()*.13
    y=-.071+random.random()*.09
    block('Board chip '+str(i),(.024,.018,.012),(x,y,.778),(.035,.04,.04))
    for j in range(3):
        block(f'Chip pin {i} {j}',(.003,.024,.003),(x-.008+j*.008,y,.777),(.60,.62,.57))
for x in [-.65,-.49]:
    block('Circuit terminal '+str(x),(.018,.027,.024),(x,-.014,.781),(.41,.44,.41))

# Papers, notebook and soldering equipment on right.
for i in range(5):
    p=block('Loose sheet '+str(i),(.34,.29,.0015),(.58,.13,.756+i*.002),(.85,.85,.78))
    p.turn('z',-13+i*3)
for i in range(15):
    block('Handwriting '+str(i),(.07+random.random()*.11,.0015,.001),(.58+random.uniform(-.05,.05),.045+i*.009,.769),(.46,.46,.43))
block('Solder station',(.25,.24,.115),(.86,.27,.815),(.16,.21,.20))
block('Station panel',(.24,.01,.09),(.86,.144,.82),(.31,.37,.34))
bar('Station adjustment',(.805,.135,.82),(.805,.117,.82),.026,black)
block('Station red switch',(.026,.01,.035),(.91,.133,.826),(.53,.04,.02))
block('Solder stand block',(.17,.17,.035),(.77,.03,.78),(.23,.20,.15))
for i in range(11):
    a=i*math.pi*2/10
    # a spring cradle rising diagonally
    pts=[]
    for j in range(13):
        t=(i+j/12)*2*math.pi
        yy=.015+(i+j/12)*.008
        pts.append((.77+.036*math.cos(t),yy,.825+(i+j/12)*.009+.036*math.sin(t)))
    cable('Iron spring '+str(i),pts,(.30,.31,.28),.003)
bar('Solder iron handle',(.78,.10,.87),(.86,.25,1.015),.022,(.08,.26,.26))
bar('Solder iron metal',(.78,.10,.87),(.71,-.015,.78),.007,(.47,.50,.47))

# Beverage can and bottle along the back right.
bar('Can',(.64,.40,.76),(.64,.40,.96),.045,(.60,.62,.57))
bar('Can rim',(.64,.40,.96),(.64,.40,.966),.047,(.75,.77,.70))
bar('Can top inset',(.64,.40,.966),(.64,.40,.968),.035,(.37,.40,.36))
for j in range(5):
    block('Can graphics '+str(j),(.037,.003,.012),(.64,.354,.79+j*.026),(.20,.28,.22))
bar('Bottle body',(.94,.52,.755),(.94,.52,.94),.046,(.51,.59,.54))
bar('Bottle neck',(.94,.52,.93),(.94,.52,1.02),.018,(.57,.65,.60))
bar('Bottle cap',(.94,.52,1.02),(.94,.52,1.047),.021,(.05,.15,.31))

# Long black overhead bench lamp and its support.
bar('Lamp upright',(.83,.48,.76),(.83,.48,1.59),.012,(.045,.05,.047))
bar('Lamp joint',(.83,.48,1.59),(.67,.44,1.65),.023,black)
lamp=Asset('Task lamp')
block('Long lamp housing',(.68,.18,.073),(.37,.42,1.665),(.015,.02,.02),lamp)
block('Lamp luminous underside',(.58,.135,.006),(.35,.42,1.625),(.73,.73,.62),lamp)
block('Lamp end grip',(.11,.19,.085),(.73,.42,1.66),(.025,.03,.03),lamp)
lamp.turn('z',-12)
scene.include('Overhead lamp',lamp)
cable('Lamp wire',[(.76,.45,1.67),(.91,.45,1.62),(.86,.40,1.40),(.86,.40,1.05),(.94,.19,.77)],black,.006)

# Hanging hand tools on the wall.
for i,(x,z) in enumerate([(-.46,1.40),(-.34,1.37),(-.17,1.38)]):
    bar('Pliers nose '+str(i),(x,.645,z+.10),(x+.008,.635,z+.015),.008,(.28,.30,.27))
    bar('Pliers handle left '+str(i),(x,.633,z+.015),(x-.024,.625,z-.075),.010,(.44,.045,.027))
    bar('Pliers handle right '+str(i),(x+.008,.633,z+.015),(x+.039,.625,z-.075),.010,(.44,.045,.027))
    bar('Pliers pivot '+str(i),(x,.624,z+.014),(x,.613,z+.014),.014,(.35,.36,.31))

# Handheld black meter lying in the middle foreground.
small=Asset('Small meter')
block('Small meter casing',(.105,.19,.031),(.17,-.22,.784),(.045,.055,.048),small)
block('Small meter yellow panel',(.081,.16,.004),(.17,-.22,.803),(.72,.58,.06),small)
block('Small meter display',(.066,.052,.004),(.17,-.17,.807),(.37,.46,.37),small)
bar('Small meter knob',(.17,-.238,.808),(.17,-.238,.817),.027,black,small)
small.turn('z',-17)
scene.include('Small test meter',small)

# Calculator in near left corner.
calc=Asset('Calculator')
block('Calculator shell',(.17,.255,.025),(-.86,-.48,.781),(.06,.075,.069),calc)
block('Calculator face',(.152,.234,.003),(-.86,-.48,.796),(.63,.65,.60),calc)
block('Calculator display',(.125,.047,.004),(-.86,-.401,.8),(.23,.32,.28),calc)
for rr in range(6):
    for cc in range(4):
        block(f'Calculator key {rr} {cc}',(.025,.021,.005),(-.913+cc*.034,-.453-rr*.025,.802),(.16,.19,.19) if rr>0 else (.30,.39,.40),calc)
calc.turn('z',15)
scene.include('Calculator',calc)

# Tangled test leads, looping broadly over the tabletop.
for i in range(15):
    cx=random.uniform(-.15,.43)
    cy=random.uniform(-.42,-.12)
    rx=random.uniform(.10,.29)
    ry=random.uniform(.06,.19)
    pts=[]
    phase=random.uniform(0,6)
    for j in range(55):
        t=phase+j/54*math.pi*2.2
        pts.append((cx+rx*math.cos(t),cy+ry*math.sin(t),.777+i*.001+ .007*math.sin(t*3)**2))
    cable('Tangled test lead '+str(i),pts,red if i%3==0 else black,.004 if i%4 else .005)
cable('Red meter lead',[(.33,.17,.82),(.36,.07,.77),(.45,-.11,.78),(.33,-.44,.79),(.03,-.46,.78)],(.65,.022,.012),.005)
cable('Black meter lead',[(.28,.17,.82),(.24,-.03,.77),(.07,-.15,.79),(.16,-.39,.79),(.49,-.46,.79)],black,.005)

# Test probes and metal clips near the front edge.
for i,(x,y,dx,dy,col) in enumerate([(.24,-.51,.32,-.025,black),(.32,-.56,.28,-.03,red),(-.02,-.44,-.20,.11,black),(.47,-.32,.17,.14,red)]):
    bar('Probe grip '+str(i),(x,y,.791),(x+dx*.65,y+dy*.65,.791),.011,col)
    bar('Probe shaft '+str(i),(x+dx*.65,y+dy*.65,.791),(x+dx,y+dy,.791),.003,(.62,.64,.59))
    bar('Probe collar '+str(i),(x+dx*.61,y+dy*.61,.791),(x+dx*.67,y+dy*.67,.791),.015,col)

# Tape spool.
bar('Tape spool',(-.17,-.39,.76),(-.17,-.39,.778),.041,(.73,.73,.62))
bar('Tape inner opening',(-.17,-.39,.779),(-.17,-.39,.781),.023,(.32,.37,.31))
bar('Tape core',(-.17,-.39,.781),(-.17,-.39,.782),.014,(.65,.70,.62))

# Yellow bits of tape and small debris on right front.
for i in range(15):
    x=random.uniform(.50,.79)
    y=random.uniform(-.55,-.26)
    p=block('Yellow tape offcut '+str(i),(.025+random.random()*.045,.022,.001),(x,y,.759),(.91,.69,.04))
    p.turn('z',random.uniform(-60,60))
for i in range(8):
    x=random.uniform(.53,.95)
    y=random.uniform(-.23,.04)
    p=block('Loose paper scrap '+str(i),(.052,.037,.001),(x,y,.76),(.80,.79,.70))
    p.turn('z',random.uniform(-30,30))

# Clear tool organizer in the lower right.
block('Tool kit base',(.29,.34,.02),(.89,-.43,.77),(.19,.23,.23))
for i in range(7):
    x=.77+i*.037
    bar('Driver red handle '+str(i),(x,-.53,.795),(x,-.43,.795),.012,(.38,.035,.023))
    bar('Driver shaft '+str(i),(x,-.43,.795),(x,-.31,.795),.004,(.51,.55,.53))
block('Tool kit clear lid',(.29,.34,.009),(.89,-.43,.823),(.46,.55,.56)).paint((.46,.55,.56),opacity=.25)
block('Tool kit blue header',(.29,.055,.005),(.89,-.286,.83),(.025,.16,.34))
block('Tool kit red header',(.29,.032,.006),(.89,-.332,.831),(.62,.04,.035))

# A small brush and scattered connectors.
bar('Brush handle',(.67,-.15,.77),(.75,-.29,.77),.013,(.35,.22,.10))
for i in range(16):
    xx=.745+random.uniform(-.035,.035)
    bar('Brush bristle '+str(i),(xx,-.29,.775),(xx+.012,-.38,.775),.0016,(.39,.34,.23))
for i in range(9):
    xx=random.uniform(-.30,.48)
    yy=random.uniform(-.56,-.25)
    bar('Loose connector '+str(i),(xx,yy,.777),(xx+.025,yy+.01,.777),.006,(.45,.43,.31))

realize(scene)

# Small printed markings created as real vector geometry.
text_obj('AUTO RANGE',(.241,.173,1.075),.009,(.77,.77,.67))
text_obj('0.00',(.255,.170,1.026),.024,(.09,.15,.10))
text_obj('TEKTRONIX',(-.356,.069,1.012),.008,(.15,.19,.17))
text_obj('CASIO',(-.913,-.376,.805),.009,(.15,.18,.16),rotation=(0,0,.25))

set_view((.06,-2.38,2.44),(-.01,.115,1.15),lens=43,sensor=36)
area_emitter((-.50,-.55,2.65),power=180,size=1.7,target=(0,0,.80),color=(1,.94,.82))
area_emitter((.33,.37,1.58),power=26,size=.65,target=(.30,-.12,.74),color=(.87,.94,1))
world=bpy.context.scene.world
world.color=(.20,.20,.18)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=512
bpy.context.scene.render.resolution_y=388
bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.view_settings.view_transform='AgX'
bpy.context.scene.view_settings.look='AgX - Medium High Contrast'
bpy.context.scene.camera.data.lens=43
