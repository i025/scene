import math
import random
import bpy
from sceneact import *

random.seed(17)

# Reference anchors: monitor (.025,.03)-(.35,.44), scope (.21,.42)-(.45,.58),
# keyboard (.10,.62)-(.53,.91), meter (.58,.40)-(.68,.63).
# Review: the successful render framed too much bench edge and left wall.
# Increase lens 42 -> 47 with object scales retained; extend desktop toward camera.
# Monitor was too short and low: increase its height and raise it, rotate toward camera.
# Large surfaces were too pale: darken desktop, cabinet faces and black plastics.
DESK_W, DESK_D, DESK_Z = 2.85, 2.15, .74
CAMERA_POS = (.18, -3.25, 2.68)
CAMERA_TARGET = (0, .25, 1.16)
CAMERA_LENS = 47
KEY_POWER, FILL_POWER = 135, 40

scene = Scene('Electronics workbench')
black = (.009,.012,.011)
dark = (.025,.031,.028)
cream = (.56,.57,.50)
paper = (.82,.82,.75)
red = (.45,.012,.009)
yellow = (.88,.52,.008)
metal = (.38,.41,.38)

def B(a,n,s,p,c):
    return a.include(n,box(size=s,center=p,color=c))

def R(a,n,r,p,q,c):
    if sum((p[k]-q[k])**2 for k in range(3)) > 1e-10:
        return a.include(n,rod(radius=r,start=p,end=q,color=c))

def cable(a,n,pts,r,c):
    clean=[]
    for p in pts:
        if not clean or sum((p[k]-clean[-1][k])**2 for k in range(3)) > 1e-10:
            clean.append(p)
    for j in range(len(clean)-1):
        R(a,n+'_'+str(j),r,clean[j],clean[j+1],c)

def finish(n,a):
    return scene.include(n,a)

room=Asset('Architecture and bench')
B(room,'wall',(4,.12,3.1),(0,1.04,1.45),(.43,.43,.37))
B(room,'desktop',(DESK_W,DESK_D,.075),(0,-.17,DESK_Z-.0375),(.245,.125,.075))
finish('room',room)

bins=Asset('Wall drawer cabinets')
for bank,cx,w,cols in [(0,.12,.78,4),(1,1.07,.99,6)]:
    B(bins,f'case_{bank}',(w,.22,.61),(cx,.88,2.10),black)
    for row in range(5):
        for col in range(cols):
            x=cx-w/2+(col+.5)*w/cols
            z=1.835+row*.112
            B(bins,f'drawer_{bank}_{row}_{col}',(w/cols-.012,.025,.093),
              (x,.754,z),(.065,.078,.067))
            B(bins,f'label_{bank}_{row}_{col}',(.071,.006,.020),
              (x,.737,z-.018),(.36,.38,.33))
            B(bins,f'handle_{bank}_{row}_{col}',(.038,.013,.009),
              (x,.727,z+.012),(.13,.15,.13))
finish('parts_storage',bins)

notes=Asset('Wall papers')
for i,(x,z,w,h) in enumerate([(-.02,1.54,.42,.34),(.43,1.51,.38,.30),(.82,1.48,.37,.29)]):
    B(notes,f'page_{i}',(w,.006,h),(x,.958,z),paper)
    for j in range(4):
        B(notes,f'line_{i}_{j}',(w*.65,.003,.0015),
          (x,.952,z+.07-j*.035),(.59,.60,.55))
finish('wall_notes',notes)

monitor=Asset('Computer monitor')
mx,my,mz=-.94,.53,1.66
B(monitor,'housing',(.84,.075,.80),(mx,my,mz),black)
B(monitor,'screen',(.755,.008,.698),(mx,.487,mz+.005),(.015,.26,.69))
B(monitor,'blue_desktop',(.738,.003,.637),(mx,.481,mz+.025),(.07,.40,.77))
B(monitor,'taskbar',(.75,.004,.024),(mx,.477,mz-.331),(.009,.13,.48))
for i in range(3):
    B(monitor,f'icon_{i}',(.014,.004,.018),(mx-.06+i*.055,.475,mz-.02),
      (.75,.78,.79) if i!=2 else (.65,.18,.15))
    B(monitor,f'caption_{i}',(.029,.003,.003),(mx-.06+i*.055,.473,mz-.038),(.65,.73,.79))
B(monitor,'neck',(.065,.08,.30),(mx,.56,1.08),dark)
B(monitor,'foot',(.38,.28,.025),(mx,.49,.93),dark)
monitor.turn('z',28,pivot=(mx,my,mz))
finish('monitor',monitor)

scope=Asset('Oscilloscope')
B(scope,'body',(.66,.36,.35),(-.41,.51,.963),cream)
B(scope,'face',(.64,.012,.324),(-.41,.323,.966),(.64,.65,.57))
B(scope,'bezel',(.325,.018,.248),(-.545,.309,.97),(.19,.22,.19))
B(scope,'screen',(.277,.006,.208),(-.545,.296,.97),(.025,.055,.057))
for i in range(5):
    B(scope,f'grid_v_{i}',(.001,.002,.195),(-.653+i*.054,.291,.97),(.055,.085,.079))
for i in range(4):
    B(scope,f'grid_h_{i}',(.266,.002,.001),(-.545,.291,.895+i*.049),(.055,.085,.079))
for col in range(3):
    for row in range(4):
        x,z=-.285+col*.066,.866+row*.064
        R(scope,f'knob_{col}_{row}',.017,(x,.31,z),(x,.275,z),cream)
for i in range(5):
    B(scope,f'button_{i}',(.024,.013,.009),(-.30+i*.037,.294,1.106),(.34,.35,.30))
scope.move((-.12,.025,.035))
finish('oscilloscope',scope)

psu=Asset('Left bench instruments')
B(psu,'main_case',(.32,.31,.27),(-1.035,.28,.891),(.37,.39,.32))
B(psu,'front',(.30,.012,.245),(-1.035,.118,.891),cream)
B(psu,'display_border',(.215,.01,.094),(-1.035,.108,.947),(.10,.13,.10))
B(psu,'display',(.183,.004,.063),(-1.035,.101,.95),(.18,.24,.17))
for i in range(3):
    R(psu,f'knob_{i}',.024,(-1.125+i*.085,.104,.855),(-1.125+i*.085,.073,.855),cream)
B(psu,'upper_unit',(.29,.25,.105),(-1.04,.34,1.08),cream)
B(psu,'upper_display',(.115,.008,.045),(-1.075,.209,1.085),(.09,.13,.09))
finish('power_instruments',psu)

power=Asset('Rear black power box')
B(power,'case',(.43,.27,.13),(.08,.56,.817),black)
for i in range(4):
    R(power,f'socket_{i}',.018,(-.075+i*.095,.417,.824),
      (-.075+i*.095,.407,.824),yellow if i==0 else cream)
B(power,'switch',(.035,.016,.04),(.22,.409,.825),red)
for i in range(2):
    pts=[(.02+.12*math.cos(j*2*math.pi/12),
          .55+.075*math.sin(j*2*math.pi/12),.9+i*.012) for j in range(13)]
    cable(power,f'coil_{i}',pts,.008,(.05,.07,.075))
finish('rear_power_box',power)

meter=Asset('Standing yellow multimeter')
B(meter,'yellow_case',(.23,.075,.43),(.43,.36,1.015),yellow)
B(meter,'face',(.19,.014,.377),(.43,.316,1.02),(.055,.075,.065))
B(meter,'lcd',(.152,.006,.10),(.43,.305,1.133),(.32,.39,.29))
for i in range(4):
    B(meter,f'digit_{i}',(.009,.003,.033),(.384+i*.029,.300,1.137),(.11,.17,.11))
R(meter,'dial',.055,(.43,.3,.996),(.43,.282,.996),(.09,.12,.10))
R(meter,'pointer',.007,(.43,.278,.996),(.451,.278,1.028),cream)
for i in range(3):
    R(meter,f'input_{i}',.013,(.367+i*.061,.302,.869),(.367+i*.061,.286,.869),black)
meter.turn('x',-12,pivot=(.43,.36,.8))
meter.turn('z',-8,pivot=(.43,.36,.8))
finish('yellow_multimeter',meter)

# Keyboard depth and rotation correct its narrow, nearly horizontal silhouette.
keyboard=Asset('Keyboard')
B(keyboard,'base',(1.02,.43,.045),(-.49,-.29,.775),black)
for row in range(6):
    for col in range(14):
        if row==0 and 4<=col<=8:
            continue
        x,y=-.94+col*.065,-.465+row*.066
        B(keyboard,f'key_{row}_{col}',(.054,.053,.018),(x,y,.807),(.025,.033,.029))
        if (row+col)%3==0:
            B(keyboard,f'legend_{row}_{col}',(.009,.006,.001),(x-.009,y,.817),(.23,.26,.23))
B(keyboard,'spacebar',(.30,.049,.016),(-.52,-.465,.808),dark)
keyboard.turn('z',25,pivot=(-.49,-.29,.775))
finish('keyboard',keyboard)

calc=Asset('Calculator')
B(calc,'case',(.23,.38,.027),(-1.10,-.64,.78),(.10,.13,.12))
B(calc,'display',(.17,.065,.008),(-1.10,-.524,.8),(.32,.40,.30))
for row in range(6):
    for col in range(4):
        B(calc,f'button_{row}_{col}',(.035,.033,.009),
          (-1.172+col*.048,-.586-row*.041,.8),
          (.46,.49,.43) if row<3 else (.13,.18,.17))
calc.turn('z',12,pivot=(-1.1,-.64,.78))
finish('calculator',calc)

pcb=Asset('Loose circuit board')
B(pcb,'board',(.25,.18,.012),(-.72,.03,.766),(.009,.09,.23))
for i in range(6):
    x,y=-.80+(i%3)*.07,-.025+(i//3)*.075
    B(pcb,f'pins_{i}',(.044,.025,.004),(x,y,.775),metal)
    B(pcb,f'chip_{i}',(.029,.038,.014),(x,y,.78),black)
for i in range(3):
    R(pcb,f'capacitor_{i}',.011,(-.81+i*.07,.09,.777),(-.81+i*.07,.09,.811),dark)
finish('circuit_board',pcb)

tester=Asset('Small handheld tester')
B(tester,'body',(.18,.29,.06),(.24,-.18,.785),black)
B(tester,'screen',(.102,.073,.008),(.24,-.10,.822),(.29,.36,.26))
R(tester,'dial',.046,(.24,-.19,.816),(.24,-.19,.835),yellow)
tester.turn('z',-13,pivot=(.24,-.18,.785))
finish('handheld_tester',tester)

pages=Asset('Bench notebook')
for i in range(3):
    p=B(pages,f'page_{i}',(.46,.34,.003),(.76,.23,.759+i*.004),paper)
    p.turn('z',-12+i*2,pivot=(.76,.23,.76))
for i in range(6):
    B(pages,f'rule_{i}',(.34,.0015,.001),(.76,.13+i*.035,.773),(.51,.58,.58))
finish('bench_papers',pages)

solder=Asset('Soldering station')
B(solder,'base',(.36,.29,.10),(1.08,.35,.795),(.13,.15,.12))
B(solder,'front',(.30,.009,.07),(1.08,.197,.80),(.045,.065,.055))
R(solder,'knob',.025,(1.10,.19,.80),(1.10,.17,.80),metal)
B(solder,'tray',(.20,.17,.025),(1.05,.33,.857),dark)
B(solder,'sponge',(.15,.12,.012),(1.05,.33,.876),(.32,.23,.055))
pts=[]
for j in range(33):
    t=j*math.pi/2
    pts.append((1.11+.047*math.cos(t),.43+j*.003,.92+j*.003))
cable(solder,'holder',pts,.007,metal)
R(solder,'iron_handle',.034,(1.05,.28,.91),(1.11,.56,1.04),(.018,.12,.12))
R(solder,'band',.037,(1.10,.51,1.018),(1.114,.56,1.04),cream)
R(solder,'shaft',.012,(1.114,.56,1.04),(1.15,.73,1.12),metal)
finish('solder_station',solder)

containers=Asset('Cans and bottle')
for i,(x,y,h,r) in enumerate([(.86,.66,.32,.055),(.99,.71,.26,.045),(.88,.52,.20,.035)]):
    R(containers,f'can_{i}',r,(x,y,.75),(x,y,.75+h),(.42,.45,.40))
    R(containers,f'rim_{i}',r*1.025,(x,y,.75+h-.012),(x,y,.75+h),(.63,.64,.58))
    B(containers,f'label_{i}',(r*1.4,.007,h*.5),(x,y-r-.002,.75+h*.47),(.11,.21,.20))
    R(containers,f'cap_{i}',r*.5,(x,y,.75+h),(x,y,.77+h),dark)
R(containers,'bottle',.067,(1.21,.80,.76),(1.21,.80,1.045),(.16,.24,.19))
R(containers,'neck',.026,(1.21,.80,1.045),(1.21,.80,1.14),(.26,.32,.26))
R(containers,'cap',.03,(1.21,.80,1.13),(1.21,.80,1.17),(.015,.035,.12))
finish('containers',containers)

lamp=Asset('Articulated desk lamp')
B(lamp,'clamp',(.16,.15,.10),(1.24,.68,.79),black)
R(lamp,'lower_arm',.018,(1.23,.67,.83),(1.19,.75,1.47),black)
R(lamp,'parallel_arm',.011,(1.18,.67,.84),(1.14,.75,1.47),metal)
R(lamp,'upper_arm',.017,(1.19,.75,1.47),(.91,.64,1.83),black)
shade=B(lamp,'shade',(.84,.22,.105),(.49,.60,1.85),(.005,.008,.008))
shade.turn('z',-10,pivot=(.49,.60,1.85))
B(lamp,'diffuser',(.67,.15,.012),(.45,.60,1.794),(.41,.42,.35))
cable(lamp,'cord',[(1.23,.71,.79),(1.28,.78,1.12),(1.20,.78,1.49),(.94,.68,1.84)],.007,black)
finish('desk_lamp',lamp)

pliers=Asset('Hanging pliers')
for i,x in enumerate([-.61,-.45,-.26]):
    z=1.36+(i%2)*.015
    R(pliers,f'jaw_a_{i}',.012,(x-.014,.93,z+.10),(x-.025,.93,z+.19),metal)
    R(pliers,f'jaw_b_{i}',.011,(x+.009,.93,z+.10),(x+.02,.93,z+.19),metal)
    cable(pliers,f'handle_a_{i}',[(x-.008,.92,z+.10),(x-.048,.92,z+.016),(x-.055,.92,z-.065)],.014,red)
    cable(pliers,f'handle_b_{i}',[(x+.008,.92,z+.10),(x+.05,.92,z+.01),(x+.048,.92,z-.06)],.014,red)
finish('hanging_tools',pliers)

wires=Asset('Test leads and loose cables')
for i in range(13):
    cx=random.uniform(-.38,.48)
    cy=random.uniform(-.47,-.08)
    rx=random.uniform(.17,.39)
    ry=random.uniform(.08,.20)
    phase=random.uniform(0,6)
    pts=[]
    for j in range(21):
        t=phase+j*2*math.pi/20
        pts.append((cx+rx*math.cos(t),cy+ry*math.sin(t),.773+i*.001))
    cable(wires,f'loop_{i}',pts,.0055,red if i%3 else black)
cable(wires,'meter_red',[(.43,.28,.84),(.46,.12,.76),(.60,-.10,.77),(.56,-.39,.77),(.24,-.55,.78)],.007,red)
cable(wires,'meter_black',[(.38,.28,.84),(.34,.07,.76),(.55,-.15,.78),(.29,-.43,.78),(-.10,-.52,.77)],.006,black)
cable(wires,'left_cable',[(-1.04,.10,.80),(-1.15,-.05,.77),(-.97,-.25,.77),(-.65,-.12,.77),(-.53,-.32,.77)],.009,black)
cable(wires,'station_cable',[(1.05,.29,.94),(.92,.17,.82),(.89,-.10,.77),(1.14,-.21,.77),(1.29,-.08,.77)],.009,black)
for i in range(5):
    x,y=-.36+i*.18,-.57+(i%3)*.035
    R(wires,f'probe_{i}',.014,(x,y,.79),(x+.21,y+.035,.79),red if i%2 else black)
    R(wires,f'tip_{i}',.004,(x+.21,y+.035,.79),(x+.29,y+.049,.79),metal)
finish('test_leads',wires)

small=Asset('Foreground tools and solder')
R(small,'reel',.058,(-.52,-.55,.748),(-.52,-.55,.778),metal)
R(small,'reel_label',.045,(-.52,-.55,.779),(-.52,-.55,.782),(.65,.69,.57))
R(small,'reel_hole',.015,(-.52,-.55,.783),(-.52,-.55,.785),black)
R(small,'screwdriver',.026,(.31,-.72,.79),(.59,-.69,.79),dark)
R(small,'shaft',.008,(.59,-.69,.79),(.83,-.665,.79),metal)
cable(small,'plier_a',[(.53,-.62,.79),(.68,-.68,.79),(.73,-.62,.79),(.70,-.53,.79)],.016,red)
cable(small,'plier_b',[(.53,-.62,.79),(.63,-.52,.79),(.73,-.49,.79)],.016,red)
R(small,'jaw_a',.012,(.53,-.62,.79),(.41,-.58,.79),metal)
R(small,'jaw_b',.012,(.53,-.62,.79),(.42,-.65,.79),metal)
finish('foreground_tools',small)

scraps=Asset('Tape scraps and components')
for i in range(10):
    x,y=random.uniform(.65,1.1),random.uniform(-.65,-.30)
    p=B(scraps,f'tape_{i}',(random.uniform(.045,.10),.028,.002),(x,y,.75),(.92,.65,.035))
    p.turn('z',random.uniform(-55,55),pivot=(x,y,.75))
for i in range(5):
    x=.75+i*.035
    R(scraps,f'lead_{i}',.0018,(x,-.20,.757),(x,-.38,.757),metal)
    R(scraps,f'resistor_{i}',.007,(x,-.27,.757),(x,-.30,.757),(.42,.28,.11))
finish('tape_and_components',scraps)

organizer=Asset('Cropped component organizer')
B(organizer,'case',(.34,.51,.065),(1.26,-.52,.778),(.035,.065,.09))
for i in range(5):
    B(organizer,f'divider_{i}',(.005,.47,.018),(1.12+i*.065,-.52,.818),(.19,.24,.23))
for i in range(3):
    B(organizer,f'crossbar_{i}',(.30,.006,.017),(1.26,-.70+i*.17,.818),(.19,.24,.24))
B(organizer,'blue_label',(.27,.11,.004),(1.26,-.35,.825),(.009,.09,.25))
B(organizer,'red_label',(.22,.07,.004),(1.26,-.50,.825),(.43,.025,.012))
finish('component_organizer',organizer)

# Audit: no fillets/booleans; all dimensions and radii positive.
# Rod paths remove duplicate points; repeated siblings have unique indexed keys.
# Materials below receive only global edits, avoiding shared-material ambiguity.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.32,.34,.30,1)
bg.inputs['Strength'].default_value=.18

set_view(CAMERA_POS,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.6,-.7,3.2),power=KEY_POWER,size=1.5,
             target=(0,.15,.75),color=(1,.94,.85))
area_emitter((1.8,-1.1,2.0),power=FILL_POWER,size=1.8,
             target=(0,.15,1),color=(.80,.88,1))

for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value=.57

sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
