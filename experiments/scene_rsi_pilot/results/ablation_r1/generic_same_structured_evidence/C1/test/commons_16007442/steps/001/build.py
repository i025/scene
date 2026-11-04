import math
import random
import bpy
from sceneact import *

random.seed(17)

# Estimated image anchors, origin upper-left:
# monitor (.025,.04)-(.35,.46); oscilloscope (.21,.41)-(.45,.59)
# yellow meter (.58,.40)-(.68,.63); keyboard (.10,.65)-(.53,.91)
# lamp shade (.49,.16)-(.84,.29); desktop front edge below frame.
# Camera looks downward toward a wall-backed bench; moderate wide-angle perspective.
DESK_W, DESK_D, DESK_Z = 2.65, 1.65, .74
CAMERA_POS = (0.18, -3.25, 2.68)
CAMERA_TARGET = (0.0, .25, 1.16)
CAMERA_LENS = 42
KEY_POWER, FILL_POWER = 190, 65

scene = Scene('Electronics workbench')
black = (.025,.029,.028)
dark = (.065,.073,.068)
cream = (.62,.63,.55)
paper = (.85,.85,.77)
red = (.53,.025,.018)
yellow = (.93,.59,.015)
metal = (.42,.44,.40)

def asset(name):
    return Asset(name)

def cube(a, name, size, center, color):
    return a.include(name, box(size=size, center=center, color=color))

def tube(a, name, points, radius, color):
    clean = [points[0]]
    for p in points[1:]:
        if sum((p[k]-clean[-1][k])**2 for k in range(3)) > 1e-10:
            clean.append(p)
    if len(clean) > 1:
        return a.include(name, sweep_tube(points=clean, radius=radius, color=color))

def cyl(a, name, radius, start, end, color):
    return a.include(name, rod(radius=radius, start=start, end=end, color=color))

def sphere(a, name, radius, center, color):
    return a.include(name, ball(radius=radius, center=center, color=color))

def rounded(a, name, size, center, color, radius=.01):
    # Every radius is capped against the smallest actual dimension.
    r = min(radius, min(size)*.45)
    return a.include(name, fillet_box(size=size, radius=r, center=center, color=color))

room = asset('Room and work surface')
cube(room,'wall',(4,.12,3.1),(0,1.04,1.45),(.56,.55,.47))
cube(room,'desktop',(DESK_W,DESK_D,.075),(0,.03,DESK_Z-.0375),(.34,.205,.135))
cube(room,'front_edge',(DESK_W,.035,.065),(0,-.79,.69),(.24,.13,.08))
scene.include('room',room)

# Wall-mounted small-parts drawers.
bins = asset('Wall parts drawers')
for bank, (cx,w,cols) in enumerate([(-.12,.78,4),(.83,.99,6)]):
    cube(bins,f'case_{bank}',(w,.22,.61),(cx,.88,2.02),(.045,.05,.045))
    for row in range(5):
        for col in range(cols):
            xx=cx-w/2+(col+.5)*w/cols
            zz=1.755+row*.112
            cube(bins,f'drawer_{bank}_{row}_{col}',(w/cols-.012,.025,.093),(xx,.754,zz),(.15,.17,.15))
            cube(bins,f'label_{bank}_{row}_{col}',(.071,.005,.022),(xx,.738,zz-.018),(.59,.60,.52))
            cube(bins,f'handle_{bank}_{row}_{col}',(.043,.012,.009),(xx,.729,zz+.012),(.28,.29,.25))
scene.include('parts_storage',bins)

# Papers pinned beneath drawers.
wallpapers = asset('Wall notes')
for i,(x,z,w,h) in enumerate([(-.02,1.54,.42,.34),(.43,1.51,.38,.30),(.82,1.48,.37,.29)]):
    cube(wallpapers,f'paper_{i}',(w,.006,h),(x,.958,z),paper)
    for j in range(7):
        cube(wallpapers,f'writing_{i}_{j}',(w*.67,.003,.0015),(x,.952,z+h*.30-j*.027),(.58,.59,.53))
scene.include('wall_notes',wallpapers)

# LCD monitor with a blue desktop and broad dark bezel.
monitor = asset('Computer monitor')
rounded(monitor,'housing',(.84,.075,.65),(-.91,.53,1.53),black,.025)
cube(monitor,'screen',(.755,.008,.545),(-.91,.487,1.535),(.025,.36,.73))
cube(monitor,'desktop_gradient',(.738,.003,.48),(-.91,.481,1.553),(.11,.48,.77))
cube(monitor,'taskbar',(.75,.004,.023),(-.91,.477,1.273),(.025,.18,.55))
for i in range(3):
    cube(monitor,f'icon_{i}',(.017,.004,.019),(-.97+i*.057,.475,1.53),(.68,.72,.72))
    cube(monitor,f'icon_label_{i}',(.035,.003,.004),(-.97+i*.057,.473,1.509),(.69,.76,.81))
cube(monitor,'neck',(.065,.08,.30),(-.91,.56,1.04),(.08,.09,.08))
rounded(monitor,'foot',(.38,.28,.025),(-.91,.49,.885),dark)
monitor.turn('z',15,pivot=(-.91,.53,1.53))
scene.include('monitor',monitor)

# Oscilloscope.
scope=asset('Oscilloscope')
rounded(scope,'body',(.66,.36,.35),(-.41,.51,.963),cream,.018)
cube(scope,'front',(.64,.012,.324),(-.41,.323,.966),(.68,.69,.61))
cube(scope,'screen_bezel',(.325,.018,.248),(-.545,.309,.97),(.25,.28,.25))
cube(scope,'glass',(.277,.006,.208),(-.545,.296,.97),(.055,.10,.105))
for i in range(6):
    cube(scope,f'grid_vertical_{i}',(.001,.002,.195),(-.66+i*.046,.291,.97),(.12,.17,.16))
for i in range(5):
    cube(scope,f'grid_horizontal_{i}',(.265,.002,.001),(-.545,.29,.88+i*.046),(.12,.17,.16))
for col in range(3):
    for row in range(4):
        xx=-.285+col*.066
        zz=.866+row*.064
        cyl(scope,f'knob_{col}_{row}',.017,(xx,.31,zz),(xx,.275,zz),(.70,.71,.64))
        cube(scope,f'knob_mark_{col}_{row}',(.002,.002,.011),(xx,.272,zz+.004),(.18,.18,.16))
for i in range(6):
    cube(scope,f'top_button_{i}',(.027,.013,.011),(-.30+i*.034,.294,1.106),(.43,.44,.39))
scene.include('oscilloscope',scope)

# Power supply beneath monitor, with a second small instrument stacked behind.
psu=asset('Left bench instruments')
rounded(psu,'main_case',(.32,.31,.27),(-1.035,.28,.891),(.48,.49,.42))
cube(psu,'front_panel',(.30,.012,.245),(-1.035,.118,.891),(.58,.59,.50))
cube(psu,'display_border',(.215,.01,.094),(-1.035,.108,.947),(.19,.22,.18))
cube(psu,'display',(.183,.004,.063),(-1.035,.101,.95),(.24,.30,.23))
for i in range(3):
    cyl(psu,f'control_{i}',.024,(-1.125+i*.085,.104,.855),(-1.125+i*.085,.073,.855),cream)
for i in range(2):
    cyl(psu,f'jack_{i}',.013,(-1.07+i*.075,.103,.793),(-1.07+i*.075,.08,.793),red if i else black)
cube(psu,'upper_instrument',(.29,.25,.105),(-1.04,.34,1.08),(.58,.59,.50))
cube(psu,'upper_display',(.115,.008,.045),(-1.075,.209,1.085),(.14,.19,.15))
scene.include('power_instruments',psu)

# Small black rear power box.
power=asset('Rear power box')
rounded(power,'case',(.43,.27,.13),(.08,.56,.817),black)
for i in range(4):
    cyl(power,f'socket_{i}',.018,(-.075+i*.095,.417,.824),(-.075+i*.095,.407,.824),yellow if i==0 else (.5,.49,.39))
cube(power,'red_switch',(.035,.016,.04),(.22,.409,.825),red)
for i in range(2):
    tube(power,f'coiled_lead_{i}',[(.02+.12*math.cos(t),.55+.075*math.sin(t),.9+i*.012) for t in [j*.18 for j in range(40)]],.009,(.11,.13,.14))
scene.include('rear_power_box',power)

# Standing digital multimeter.
meter=asset('Standing yellow multimeter')
rounded(meter,'rubber_case',(.23,.075,.43),(.43,.36,1.015),yellow,.024)
rounded(meter,'face',(.19,.014,.377),(.43,.316,1.02),(.10,.12,.11),.008)
cube(meter,'lcd',(.152,.006,.10),(.43,.305,1.133),(.41,.47,.37))
for i in range(4):
    # Dark segmented-looking reading.
    cube(meter,f'digit_{i}',(.019,.003,.037),(.379+i*.03,.300,1.137),(.21,.27,.21))
cyl(meter,'selector',.055,(.43,.3,.996),(.43,.286,.996),(.18,.20,.18))
cyl(meter,'selector_pointer',.008,(.43,.278,.996),(.451,.278,1.028),(.65,.65,.55))
for i in range(3):
    cyl(meter,f'input_{i}',.013,(.367+i*.061,.302,.869),(.367+i*.061,.286,.869),black)
meter.turn('x',-12,pivot=(.43,.36,.8))
meter.turn('z',-8,pivot=(.43,.36,.8))
scene.include('yellow_multimeter',meter)

# Keyboard, individually editable key rows.
keyboard=asset('Black computer keyboard')
rounded(keyboard,'base',(.99,.36,.045),(-.49,-.29,.775),(.045,.05,.048),.017)
for row in range(5):
    for col in range(15):
        if row==0 and 4<=col<=8:
            continue
        xx=-.94+col*.061
        yy=-.428+row*.061
        rounded(keyboard,f'key_{row}_{col}',(.052,.05,.018),(xx,yy,.807),(.075,.083,.079),.004)
        if (row+col)%3==0:
            cube(keyboard,f'legend_{row}_{col}',(.011,.008,.001),(xx-.009,yy,.817),(.40,.43,.40))
rounded(keyboard,'spacebar',(.29,.045,.016),(-.57,-.428,.808),dark,.004)
keyboard.turn('z',14,pivot=(-.49,-.29,.775))
scene.include('keyboard',keyboard)

calc=asset('Calculator at left edge')
rounded(calc,'case',(.23,.38,.027),(-1.10,-.64,.78),(.24,.27,.25),.012)
cube(calc,'display',(.17,.065,.008),(-1.10,-.524,.8),(.44,.51,.42))
for row in range(6):
    for col in range(4):
        rounded(calc,f'button_{row}_{col}',(.035,.033,.009),(-1.172+col*.048,-.586-row*.041,.8),(.58,.61,.55) if row<3 else (.27,.32,.31),.003)
calc.turn('z',12,pivot=(-1.1,-.64,.78))
scene.include('calculator',calc)

# Exposed blue PCB and components.
pcb=asset('Loose blue circuit board')
cube(pcb,'board',(.25,.18,.012),(-.72,.03,.766),(.025,.17,.31))
for i in range(8):
    xx=-.82+(i%4)*.055
    yy=-.025+(i//4)*.075
    cube(pcb,f'chip_{i}',(.029,.038,.014),(xx,yy,.78),black)
    for j in range(3):
        cube(pcb,f'pin_{i}_{j}',(.039,.004,.003),(xx,yy-.012+j*.012,.776),metal)
for i in range(4):
    cyl(pcb,f'capacitor_{i}',.012,(-.8+i*.05,.09,.776),(-.8+i*.05,.09,.813),(.13,.16,.15))
scene.include('circuit_board',pcb)

# Foreground small handheld tester.
tester=asset('Handheld foreground tester')
rounded(tester,'housing',(.18,.29,.06),(.24,-.18,.785),black,.018)
cube(tester,'screen',(.102,.073,.008),(.24,-.10,.822),(.38,.43,.34))
cyl(tester,'dial',.046,(.24,-.19,.816),(.24,-.19,.835),yellow)
for i in range(2):
    cyl(tester,f'port_{i}',.014,(.20+i*.08,-.29,.803),(.20+i*.08,-.315,.803),red if i else black)
tester.turn('z',-13,pivot=(.24,-.18,.785))
scene.include('handheld_tester',tester)

# Papers and notebook on the right.
notes=asset('Bench notebook and loose pages')
for i in range(4):
    page=cube(notes,f'page_{i}',(.46,.34,.003),(.76,.23,.759+i*.004),(.88,.87,.79))
    page.turn('z',-12+i*2,pivot=(.76,.23,.76))
for i in range(10):
    cube(notes,f'notebook_rule_{i}',(.34,.0015,.001),(.76,.12+i*.023,.779),(.57,.64,.64))
scene.include('bench_papers',notes)

# Solder station, coiled holder and iron.
solder=asset('Soldering station')
rounded(solder,'station_base',(.36,.29,.10),(1.08,.35,.795),(.23,.25,.22))
cube(solder,'front_panel',(.30,.009,.07),(1.08,.197,.80),(.11,.14,.13))
cyl(solder,'temperature_knob',.025,(1.10,.19,.80),(1.10,.17,.80),(.39,.43,.38))
rounded(solder,'sponge_tray',(.20,.17,.025),(1.05,.33,.857),(.18,.19,.15))
cube(solder,'sponge',(.15,.12,.012),(1.05,.33,.876),(.43,.34,.10))
tube(solder,'iron_holder',[(1.11+.047*math.cos(t),.43+t*.004,.92+t*.004) for t in [j*.23 for j in range(105)]],.009,metal)
cyl(solder,'iron_handle',.034,(1.05,.28,.91),(1.11,.56,1.04),(.055,.22,.22))
cyl(solder,'handle_band',.037,(1.10,.51,1.018),(1.114,.56,1.04),(.62,.66,.60))
cyl(solder,'iron_shaft',.012,(1.114,.56,1.04),(1.15,.73,1.12),metal)
scene.include('solder_station',solder)

# Spray cans, bottle and small containers along the rear.
containers=asset('Rear cans and bottle')
for i,(xx,yy,h,r) in enumerate([(.86,.66,.32,.055),(.99,.71,.26,.045),(.88,.52,.20,.035)]):
    cyl(containers,f'can_{i}',r,(xx,yy,.75),(xx,yy,.75+h),(.48,.51,.46))
    cyl(containers,f'rim_{i}',r*1.025,(xx,yy,.75+h-.013),(xx,yy,.75+h),(.69,.70,.64))
    cube(containers,f'can_label_{i}',(r*1.4,.007,h*.5),(xx,yy-r-.002,.75+h*.47),(.19,.30,.29))
    cyl(containers,f'cap_{i}',r*.50,(xx,yy,.75+h),(xx,yy,.77+h),dark)
cyl(containers,'bottle_body',.067,(1.21,.80,.76),(1.21,.80,1.02),(.30,.38,.33))
sphere(containers,'bottle_shoulder',.066,(1.21,.80,1.015),(.35,.43,.38))
cyl(containers,'bottle_neck',.026,(1.21,.80,1.03),(1.21,.80,1.14),(.42,.46,.40))
cyl(containers,'bottle_cap',.03,(1.21,.80,1.13),(1.21,.80,1.17),(.05,.10,.22))
scene.include('containers',containers)

# Black articulated work lamp across the upper-right of the photograph.
lamp=asset('Articulated desk lamp')
rounded(lamp,'clamp',(.16,.15,.10),(1.24,.68,.79),black)
cyl(lamp,'lower_arm',.018,(1.23,.67,.83),(1.19,.75,1.47),black)
cyl(lamp,'parallel_lower_arm',.011,(1.18,.67,.84),(1.14,.75,1.47),metal)
cyl(lamp,'upper_arm',.017,(1.19,.75,1.47),(.91,.64,1.83),black)
sphere(lamp,'hinge',.045,(.91,.64,1.83),black)
rounded(lamp,'long_shade',(.84,.22,.105),(.49,.60,1.85),(.018,.023,.023),.045)
cube(lamp,'underside_diffuser',(.67,.15,.012),(.45,.60,1.794),(.57,.58,.49))
lamp.members['long_shade'].turn('z',-10,pivot=(.49,.60,1.85))
tube(lamp,'power_cord',[(1.23,.71,.79),(1.28,.78,1.12),(1.20,.78,1.49),(.94,.68,1.84),(.87,.68,1.85)],.007,black)
scene.include('desk_lamp',lamp)

# Hanging pliers and cutters.
tools=asset('Pliers hanging on wall')
for i,xx in enumerate([(-.61),(-.45),(-.26)]):
    zz=1.36+(i%2)*.015
    cyl(tools,f'jaw_left_{i}',.012,(xx-.014,.93,zz+.10),(xx-.025,.93,zz+.19),metal)
    cyl(tools,f'jaw_right_{i}',.011,(xx+.009,.93,zz+.10),(xx+.02,.93,zz+.19),metal)
    sphere(tools,f'pivot_{i}',.019,(xx,.927,zz+.08),(.22,.24,.21))
    tube(tools,f'handle_left_{i}',[(xx-.008,.92,zz+.08),(xx-.048,.92,zz+.016),(xx-.055,.92,zz-.065),(xx-.035,.92,zz-.09)],.014,red)
    tube(tools,f'handle_right_{i}',[(xx+.008,.92,zz+.08),(xx+.05,.92,zz+.01),(xx+.048,.92,zz-.06)],.014,red)
scene.include('hanging_tools',tools)

# Leads form the characteristic loose, crossing loops across the foreground.
wires=asset('Loose test leads and cables')
for i in range(15):
    cx=random.uniform(-.38,.48)
    cy=random.uniform(-.47,-.08)
    rx=random.uniform(.17,.39)
    ry=random.uniform(.08,.20)
    phase=random.uniform(0,6)
    points=[]
    for j in range(46):
        t=phase+j*math.pi*2/45
        points.append((cx+rx*math.cos(t),cy+ry*math.sin(t),.765+.007*i/15+.011*math.sin(t*2+i)**2))
    tube(wires,f'loop_{i}',points,.0055,red if i%3 else black)
tube(wires,'meter_red_cord',[(.43,.28,.84),(.46,.12,.76),(.60,-.10,.77),(.56,-.39,.77),(.24,-.55,.78)],.007,red)
tube(wires,'meter_black_cord',[(.38,.28,.84),(.34,.07,.76),(.55,-.15,.78),(.29,-.43,.78),(-.10,-.52,.77)],.006,black)
tube(wires,'left_black_cable',[(-1.04,.10,.80),(-1.15,-.05,.77),(-.97,-.25,.77),(-.65,-.12,.77),(-.53,-.32,.77)],.009,black)
tube(wires,'station_cord',[(1.05,.29,.94),(.92,.17,.82),(.89,-.10,.77),(1.14,-.21,.77),(1.29,-.08,.77)],.009,black)
for i in range(7):
    xx=-.36+i*.13
    yy=-.57+(i%3)*.035
    cyl(wires,f'probe_handle_{i}',.014,(xx,yy,.783),(xx+.21,yy+.035,.786),red if i%2 else black)
    cyl(wires,f'probe_tip_{i}',.004,(xx+.21,yy+.035,.786),(xx+.29,yy+.049,.786),metal)
    cyl(wires,f'probe_collar_{i}',.021,(xx+.025,yy+.004,.783),(xx+.055,yy+.009,.783),(.19,.20,.17))
scene.include('test_leads',wires)

# Solder reel and foreground hand tools.
small=asset('Foreground small tools')
cyl(small,'solder_reel',.058,(-.52,-.55,.748),(-.52,-.55,.778),(.53,.56,.51))
cyl(small,'reel_label',.045,(-.52,-.55,.779),(-.52,-.55,.782),(.71,.74,.61))
cyl(small,'reel_hole',.015,(-.52,-.55,.783),(-.52,-.55,.785),(.10,.12,.10))
cyl(small,'screwdriver_handle',.026,(.31,-.72,.79),(.59,-.69,.79),(.13,.15,.13))
cyl(small,'screwdriver_shaft',.008,(.59,-.69,.79),(.83,-.665,.79),metal)
tube(small,'pliers_handle_a',[(.53,-.62,.79),(.68,-.68,.79),(.73,-.62,.79),(.70,-.53,.79)],.016,red)
tube(small,'pliers_handle_b',[(.53,-.62,.79),(.63,-.52,.79),(.73,-.49,.79)],.016,red)
cyl(small,'pliers_jaw_a',.012,(.53,-.62,.79),(.41,-.58,.79),metal)
cyl(small,'pliers_jaw_b',.012,(.53,-.62,.79),(.42,-.65,.79),metal)
scene.include('foreground_tools',small)

scraps=asset('Yellow tape scraps and components')
for i in range(11):
    xx=random.uniform(.65,1.1)
    yy=random.uniform(-.65,-.30)
    piece=cube(scraps,f'tape_{i}',(random.uniform(.045,.10),.028,.002),(xx,yy,.75),(.92,.65,.035))
    piece.turn('z',random.uniform(-55,55),pivot=(xx,yy,.75))
for i in range(6):
    xx=.75+i*.035
    cyl(scraps,f'resistor_lead_{i}',.0018,(xx,-.20,.757),(xx,-.38,.757),metal)
    cyl(scraps,f'resistor_{i}',.007,(xx,-.27,.757),(xx,-.30,.757),(.50,.36,.17))
scene.include('tape_and_components',scraps)

# Cropped component organizer at lower right.
organizer=asset('Right foreground component organizer')
rounded(organizer,'case',(.34,.51,.065),(1.26,-.52,.778),(.10,.14,.17),.012)
for i in range(5):
    cube(organizer,f'separator_{i}',(.005,.47,.018),(1.12+i*.065,-.52,.818),(.28,.32,.31))
for i in range(3):
    cube(organizer,f'crossbar_{i}',(.30,.006,.017),(1.26,-.70+i*.17,.818),(.29,.33,.33))
cube(organizer,'blue_label',(.27,.11,.004),(1.26,-.35,.825),(.035,.19,.38))
cube(organizer,'red_label',(.22,.07,.004),(1.26,-.50,.825),(.53,.055,.025))
scene.include('component_organizer',organizer)

# Audit: all repeated children have indexed unique keys; all tube paths are cleaned;
# all sizes/radii are positive, fillets capped to < half of the thinnest dimension.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(.37,.39,.35,1)
background.inputs['Strength'].default_value=.30

set_view(CAMERA_POS,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.6,-.7,3.2),power=KEY_POWER,size=2.3,target=(0,.15,.75),color=(1,.94,.81))
area_emitter((1.8,-1.1,2.0),power=FILL_POWER,size=1.8,target=(0,.15,1),color=(.80,.88,1))

# Materials are customized through descendants of semantic groups.
def meshes_under(obj):
    for child in obj.children:
        if child.type=='MESH':
            yield child
        yield from meshes_under(child)

for group_name in ['monitor','yellow_multimeter','oscilloscope']:
    group=bpy.data.objects.get(group_name)
    if group:
        for obj in meshes_under(group):
            for slot in obj.material_slots:
                mat=slot.material
                if mat and mat.use_nodes:
                    bs=mat.node_tree.nodes.get('Principled BSDF')
                    if bs:
                        bs.inputs['Roughness'].default_value=.48

sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
sc.camera.data.lens=CAMERA_LENS
