import math
import random
import bpy
from sceneact import *

random.seed(17)

# Image anchors (upper-left origin): monitor (.03,.04)-(.35,.46),
# scope (.21,.42)-(.45,.59), meter (.58,.40)-(.68,.63),
# keyboard (.10,.65)-(.53,.91), lamp (.49,.16)-(.84,.29).
# Camera assumes a downward view across a deep, wall-backed workbench.
DESK_W, DESK_D, DESK_Z = 2.65, 1.65, .74
CAMERA_POS = (.18, -3.25, 2.68)
CAMERA_TARGET = (0, .25, 1.16)
CAMERA_LENS = 42
KEY_POWER, FILL_POWER = 190, 65

# Runtime repair: inexpensive primitive geometry replaces filleted solids and
# densely sampled sweeps. The intended camera and object arrangement are retained.
scene = Scene('Electronics workbench')
black = (.025,.029,.028)
dark = (.065,.073,.068)
cream = (.62,.63,.55)
paper = (.85,.85,.77)
red = (.53,.025,.018)
yellow = (.93,.59,.015)
metal = (.42,.44,.40)

def B(a, n, s, p, c):
    return a.include(n, box(size=s, center=p, color=c))

def R(a, n, r, p, q, c):
    if sum((p[k]-q[k])**2 for k in range(3)) > 1e-10:
        return a.include(n, rod(radius=r, start=p, end=q, color=c))

def cable(a, n, pts, r, c):
    clean = []
    for p in pts:
        if not clean or sum((p[k]-clean[-1][k])**2 for k in range(3)) > 1e-10:
            clean.append(p)
    for j in range(len(clean)-1):
        R(a, n+'_'+str(j), r, clean[j], clean[j+1], c)

def finish(name, a):
    scene.include(name, a)

room = Asset('Architecture')
B(room,'wall',(4,.12,3.1),(0,1.04,1.45),(.56,.55,.47))
B(room,'desktop',(DESK_W,DESK_D,.075),(0,.03,DESK_Z-.0375),(.34,.205,.135))
finish('room',room)

bins = Asset('Wall drawer cabinets')
for bank,cx,w,cols in [(0,-.12,.78,4),(1,.83,.99,6)]:
    B(bins,f'case_{bank}',(w,.22,.61),(cx,.88,2.02),black)
    for row in range(5):
        for col in range(cols):
            x = cx-w/2+(col+.5)*w/cols
            z = 1.755+row*.112
            B(bins,f'drawer_{bank}_{row}_{col}',
              (w/cols-.012,.025,.093),(x,.754,z),(.15,.17,.15))
            B(bins,f'label_{bank}_{row}_{col}',
              (.071,.006,.022),(x,.737,z-.018),(.59,.60,.52))
finish('parts_storage',bins)

notes = Asset('Wall papers')
for i,(x,z,w,h) in enumerate([(-.02,1.54,.42,.34),(.43,1.51,.38,.30),(.82,1.48,.37,.29)]):
    B(notes,f'page_{i}',(w,.006,h),(x,.958,z),paper)
    for j in range(3):
        B(notes,f'line_{i}_{j}',(w*.65,.003,.002),(x,.952,z+.07-j*.045),(.62,.63,.57))
finish('wall_notes',notes)

monitor = Asset('Computer monitor')
B(monitor,'housing',(.84,.075,.65),(-.91,.53,1.53),black)
B(monitor,'screen',(.755,.008,.545),(-.91,.487,1.535),(.025,.36,.73))
B(monitor,'blue_desktop',(.738,.003,.48),(-.91,.481,1.553),(.11,.48,.77))
B(monitor,'taskbar',(.75,.004,.023),(-.91,.477,1.273),(.025,.18,.55))
for i in range(3):
    B(monitor,f'icon_{i}',(.017,.004,.019),(-.97+i*.057,.475,1.53),(.75,.78,.79))
B(monitor,'neck',(.065,.08,.30),(-.91,.56,1.04),dark)
B(monitor,'foot',(.38,.28,.025),(-.91,.49,.885),dark)
monitor.turn('z',15,pivot=(-.91,.53,1.53))
finish('monitor',monitor)

scope = Asset('Oscilloscope')
B(scope,'body',(.66,.36,.35),(-.41,.51,.963),cream)
B(scope,'face',(.64,.012,.324),(-.41,.323,.966),(.68,.69,.61))
B(scope,'bezel',(.325,.018,.248),(-.545,.309,.97),(.25,.28,.25))
B(scope,'screen',(.277,.006,.208),(-.545,.296,.97),(.055,.10,.105))
for col in range(3):
    for row in range(4):
        x,z=-.285+col*.066,.866+row*.064
        R(scope,f'knob_{col}_{row}',.017,(x,.31,z),(x,.275,z),cream)
for i in range(4):
    B(scope,f'button_{i}',(.027,.013,.011),(-.29+i*.046,.294,1.106),(.43,.44,.39))
finish('oscilloscope',scope)

psu = Asset('Left bench instruments')
B(psu,'main_case',(.32,.31,.27),(-1.035,.28,.891),(.48,.49,.42))
B(psu,'front',(.30,.012,.245),(-1.035,.118,.891),cream)
B(psu,'display_border',(.215,.01,.094),(-1.035,.108,.947),(.19,.22,.18))
B(psu,'display',(.183,.004,.063),(-1.035,.101,.95),(.24,.30,.23))
for i in range(3):
    R(psu,f'knob_{i}',.024,(-1.125+i*.085,.104,.855),(-1.125+i*.085,.073,.855),cream)
B(psu,'upper_unit',(.29,.25,.105),(-1.04,.34,1.08),cream)
B(psu,'upper_display',(.115,.008,.045),(-1.075,.209,1.085),(.14,.19,.15))
finish('power_instruments',psu)

power = Asset('Rear black power box')
B(power,'case',(.43,.27,.13),(.08,.56,.817),black)
for i in range(4):
    R(power,f'socket_{i}',.018,(-.075+i*.095,.417,.824),
      (-.075+i*.095,.407,.824),yellow if i==0 else cream)
B(power,'switch',(.035,.016,.04),(.22,.409,.825),red)
for i in range(2):
    pts=[(.02+.12*math.cos(j*2*math.pi/12),
          .55+.075*math.sin(j*2*math.pi/12),.90+i*.012) for j in range(13)]
    cable(power,f'coil_{i}',pts,.008,(.11,.13,.14))
finish('rear_power_box',power)

meter = Asset('Standing yellow multimeter')
B(meter,'yellow_case',(.23,.075,.43),(.43,.36,1.015),yellow)
B(meter,'face',(.19,.014,.377),(.43,.316,1.02),(.10,.12,.11))
B(meter,'lcd',(.152,.006,.10),(.43,.305,1.133),(.41,.47,.37))
for i in range(4):
    B(meter,f'digit_{i}',(.012,.003,.033),(.384+i*.029,.300,1.137),(.22,.28,.22))
R(meter,'dial',.055,(.43,.3,.996),(.43,.282,.996),(.18,.20,.18))
R(meter,'pointer',.007,(.43,.278,.996),(.451,.278,1.028),cream)
for i in range(3):
    R(meter,f'input_{i}',.013,(.367+i*.061,.302,.869),(.367+i*.061,.286,.869),black)
meter.turn('x',-12,pivot=(.43,.36,.8))
meter.turn('z',-8,pivot=(.43,.36,.8))
finish('yellow_multimeter',meter)

keyboard = Asset('Keyboard')
B(keyboard,'base',(.99,.36,.045),(-.49,-.29,.775),(.045,.05,.048))
for row in range(5):
    for col in range(14):
        if row==0 and 4<=col<=8:
            continue
        B(keyboard,f'key_{row}_{col}',(.053,.05,.018),
          (-.92+col*.063,-.428+row*.061,.807),(.075,.083,.079))
B(keyboard,'spacebar',(.29,.045,.016),(-.51,-.428,.808),dark)
keyboard.turn('z',14,pivot=(-.49,-.29,.775))
finish('keyboard',keyboard)

calc = Asset('Calculator')
B(calc,'case',(.23,.38,.027),(-1.10,-.64,.78),(.24,.27,.25))
B(calc,'display',(.17,.065,.008),(-1.10,-.524,.8),(.44,.51,.42))
for row in range(6):
    for col in range(4):
        B(calc,f'button_{row}_{col}',(.035,.033,.009),
          (-1.172+col*.048,-.586-row*.041,.8),
          (.58,.61,.55) if row<3 else (.27,.32,.31))
calc.turn('z',12,pivot=(-1.1,-.64,.78))
finish('calculator',calc)

pcb = Asset('Loose circuit board')
B(pcb,'board',(.25,.18,.012),(-.72,.03,.766),(.025,.17,.31))
for i in range(6):
    x,y=-.80+(i%3)*.07,-.025+(i//3)*.075
    B(pcb,f'chip_{i}',(.029,.038,.014),(x,y,.78),black)
    B(pcb,f'pins_{i}',(.044,.025,.004),(x,y,.775),metal)
finish('circuit_board',pcb)

tester = Asset('Small handheld tester')
B(tester,'body',(.18,.29,.06),(.24,-.18,.785),black)
B(tester,'screen',(.102,.073,.008),(.24,-.10,.822),(.38,.43,.34))
R(tester,'dial',.046,(.24,-.19,.816),(.24,-.19,.835),yellow)
tester.turn('z',-13,pivot=(.24,-.18,.785))
finish('handheld_tester',tester)

pages = Asset('Bench notebook')
for i in range(3):
    p=B(pages,f'page_{i}',(.46,.34,.003),(.76,.23,.759+i*.004),paper)
    p.turn('z',-12+i*2,pivot=(.76,.23,.76))
for i in range(6):
    B(pages,f'rule_{i}',(.34,.0015,.001),(.76,.13+i*.035,.773),(.57,.64,.64))
finish('bench_papers',pages)

solder = Asset('Soldering station')
B(solder,'base',(.36,.29,.10),(1.08,.35,.795),(.23,.25,.22))
B(solder,'front',(.30,.009,.07),(1.08,.197,.80),(.11,.14,.13))
R(solder,'knob',.025,(1.10,.19,.80),(1.10,.17,.80),metal)
B(solder,'tray',(.20,.17,.025),(1.05,.33,.857),dark)
B(solder,'sponge',(.15,.12,.012),(1.05,.33,.876),(.43,.34,.10))
# The open spring silhouette uses a short, economical helix.
pts=[]
for j in range(33):
    t=j*math.pi/2
    pts.append((1.11+.047*math.cos(t),.43+j*.003,.92+j*.003))
cable(solder,'holder',pts,.007,metal)
R(solder,'iron_handle',.034,(1.05,.28,.91),(1.11,.56,1.04),(.055,.22,.22))
R(solder,'band',.037,(1.10,.51,1.018),(1.114,.56,1.04),cream)
R(solder,'shaft',.012,(1.114,.56,1.04),(1.15,.73,1.12),metal)
finish('solder_station',solder)

containers = Asset('Cans and bottle')
for i,(x,y,h,r) in enumerate([(.86,.66,.32,.055),(.99,.71,.26,.045),(.88,.52,.20,.035)]):
    R(containers,f'can_{i}',r,(x,y,.75),(x,y,.75+h),(.48,.51,.46))
    R(containers,f'rim_{i}',r*1.025,(x,y,.75+h-.012),(x,y,.75+h),(.69,.70,.64))
    B(containers,f'label_{i}',(r*1.4,.007,h*.5),(x,y-r-.002,.75+h*.47),(.19,.30,.29))
    R(containers,f'cap_{i}',r*.5,(x,y,.75+h),(x,y,.77+h),dark)
R(containers,'bottle',.067,(1.21,.80,.76),(1.21,.80,1.045),(.30,.38,.33))
R(containers,'neck',.026,(1.21,.80,1.045),(1.21,.80,1.14),(.42,.46,.40))
R(containers,'cap',.03,(1.21,.80,1.13),(1.21,.80,1.17),(.05,.10,.22))
finish('containers',containers)

lamp = Asset('Articulated desk lamp')
B(lamp,'clamp',(.16,.15,.10),(1.24,.68,.79),black)
R(lamp,'lower_arm',.018,(1.23,.67,.83),(1.19,.75,1.47),black)
R(lamp,'parallel_arm',.011,(1.18,.67,.84),(1.14,.75,1.47),metal)
R(lamp,'upper_arm',.017,(1.19,.75,1.47),(.91,.64,1.83),black)
shade=B(lamp,'shade',(.84,.22,.105),(.49,.60,1.85),(.018,.023,.023))
shade.turn('z',-10,pivot=(.49,.60,1.85))
B(lamp,'diffuser',(.67,.15,.012),(.45,.60,1.794),(.57,.58,.49))
cable(lamp,'cord',[(1.23,.71,.79),(1.28,.78,1.12),(1.20,.78,1.49),(.94,.68,1.84)],.007,black)
finish('desk_lamp',lamp)

pliers = Asset('Hanging pliers')
for i,x in enumerate([-.61,-.45,-.26]):
    z=1.36+(i%2)*.015
    R(pliers,f'jaw_a_{i}',.012,(x-.014,.93,z+.10),(x-.025,.93,z+.19),metal)
    R(pliers,f'jaw_b_{i}',.011,(x+.009,.93,z+.10),(x+.02,.93,z+.19),metal)
    cable(pliers,f'handle_a_{i}',[(x-.008,.92,z+.10),(x-.048,.92,z+.016),(x-.055,.92,z-.065)],.014,red)
    cable(pliers,f'handle_b_{i}',[(x+.008,.92,z+.10),(x+.05,.92,z+.01),(x+.048,.92,z-.06)],.014,red)
finish('hanging_tools',pliers)

wires = Asset('Test leads and loose cables')
for i in range(9):
    cx=random.uniform(-.38,.48)
    cy=random.uniform(-.47,-.08)
    rx=random.uniform(.17,.39)
    ry=random.uniform(.08,.20)
    phase=random.uniform(0,6)
    pts=[]
    for j in range(17):
        t=phase+j*2*math.pi/16
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

small = Asset('Foreground tools and solder')
R(small,'reel',.058,(-.52,-.55,.748),(-.52,-.55,.778),metal)
R(small,'reel_label',.045,(-.52,-.55,.779),(-.52,-.55,.782),(.71,.74,.61))
R(small,'reel_hole',.015,(-.52,-.55,.783),(-.52,-.55,.785),black)
R(small,'screwdriver',.026,(.31,-.72,.79),(.59,-.69,.79),dark)
R(small,'shaft',.008,(.59,-.69,.79),(.83,-.665,.79),metal)
cable(small,'plier_a',[(.53,-.62,.79),(.68,-.68,.79),(.73,-.62,.79),(.70,-.53,.79)],.016,red)
cable(small,'plier_b',[(.53,-.62,.79),(.63,-.52,.79),(.73,-.49,.79)],.016,red)
R(small,'jaw_a',.012,(.53,-.62,.79),(.41,-.58,.79),metal)
R(small,'jaw_b',.012,(.53,-.62,.79),(.42,-.65,.79),metal)
finish('foreground_tools',small)

scraps = Asset('Tape scraps and components')
for i in range(10):
    x,y=random.uniform(.65,1.1),random.uniform(-.65,-.30)
    p=B(scraps,f'tape_{i}',(random.uniform(.045,.10),.028,.002),(x,y,.75),(.92,.65,.035))
    p.turn('z',random.uniform(-55,55),pivot=(x,y,.75))
for i in range(5):
    x=.75+i*.035
    R(scraps,f'lead_{i}',.0018,(x,-.20,.757),(x,-.38,.757),metal)
    R(scraps,f'resistor_{i}',.007,(x,-.27,.757),(x,-.30,.757),(.50,.36,.17))
finish('tape_and_components',scraps)

organizer = Asset('Cropped component organizer')
B(organizer,'case',(.34,.51,.065),(1.26,-.52,.778),(.10,.14,.17))
for i in range(5):
    B(organizer,f'divider_{i}',(.005,.47,.018),(1.12+i*.065,-.52,.818),(.28,.32,.31))
for i in range(3):
    B(organizer,f'crossbar_{i}',(.30,.006,.017),(1.26,-.70+i*.17,.818),(.29,.33,.33))
B(organizer,'blue_label',(.27,.11,.004),(1.26,-.35,.825),(.035,.19,.38))
B(organizer,'red_label',(.22,.07,.004),(1.26,-.50,.825),(.53,.055,.025))
finish('component_organizer',organizer)

# API audit: no fillets or boolean operations; positive primitive dimensions;
# distinct rod endpoints; unique indexed sibling keys; no material-name assumptions.
realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient world')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (.37,.39,.35,1)
background.inputs['Strength'].default_value = .30

set_view(CAMERA_POS,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.6,-.7,3.2),power=KEY_POWER,size=2.3,
             target=(0,.15,.75),color=(1,.94,.81))
area_emitter((1.8,-1.1,2.0),power=FILL_POWER,size=1.8,
             target=(0,.15,1),color=(.80,.88,1))

# One global material treatment avoids unintended edits to shared finishes.
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs = mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value = .64

sc.render.engine = 'BLENDER_EEVEE_NEXT'
sc.render.resolution_x = 512
sc.render.resolution_y = 388
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = 0
sc.render.image_settings.file_format = 'PNG'
