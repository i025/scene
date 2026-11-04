from sceneact import *
import bpy
import math
import random

random.seed(19)
scene = Scene("Electronics workbench")

CAMERA_POSITION = (0.48, -2.75, 2.34)
CAMERA_TARGET = (0.0, 0.13, 1.03)
CAMERA_LENS = 45
BENCH_SIZE = (2.18, 1.40, 0.07)
MONITOR_SIZE = (0.70, 0.055, 0.51)
SCOPE_SIZE = (0.53, 0.30, 0.28)

wood = (0.34, 0.19, 0.12)
black = (0.018, 0.023, 0.024)
dark = (0.055, 0.065, 0.064)
gray = (0.45, 0.47, 0.43)
cream = (0.66, 0.68, 0.57)
silver = (0.57, 0.60, 0.57)
red = (0.63, 0.025, 0.018)
yellow = (0.94, 0.59, 0.018)
paper = (0.82, 0.82, 0.73)

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def B(a, name, size, center, color):
    a.include(name, box(size=size, center=center, color=color))

def R(a, name, radius, start, end, color):
    a.include(name, rod(radius=radius, start=start, end=end, color=color))

def S(a, name, points, radius, color):
    a.include(name, sweep_tube(points=points, radius=radius, color=color))

bench = asset("brown workbench")
B(bench, "laminated top", BENCH_SIZE, (0, -0.02, 0.705), wood)
B(bench, "front edge", (2.18, 0.035, 0.065), (0, -0.713, 0.70), (0.24, .13, .08))
wall = asset("rear wall")
B(wall, "plaster", (3.1, .07, 2.8), (0, .735, 1.30), (.54, .54, .46))
B(wall, "left return", (.06, 1.7, 2.5), (-1.17, .1, 1.3), (.43, .44, .38))

# Wall storage, with distinct recessed drawer fronts and pale labels.
for ci, (cx, width, rows, cols, cz) in enumerate([
    (-.02, .56, 4, 4, 1.86),
    (.70, .82, 5, 5, 1.84)
]):
    a = asset("parts cabinet %d" % ci)
    height = .44 if ci == 0 else .52
    B(a, "outer case", (width, .16, height), (cx, .64, cz), black)
    cw = (width-.035)/cols
    ch = (height-.025)/rows
    for row in range(rows):
        for col in range(cols):
            x = cx-width/2+.018+cw*(col+.5)
            z = cz-height/2+.012+ch*(row+.5)
            k = "%d_%d" % (row,col)
            B(a, "drawer "+k, (cw-.009,.013,ch-.009),
              (x,.548,z), (.18,.21,.20))
            B(a, "label "+k, (cw*.55,.004,ch*.24),
              (x,.539,z-ch*.18), (.60,.62,.56))
            B(a, "pull "+k, (cw*.27,.017,.008),
              (x,.53,z+ch*.12), (.10,.12,.12))

papers = asset("wall paperwork")
for i,(x,z,w,h) in enumerate([
    (-.12,1.40,.45,.28),(.31,1.38,.37,.31),(.70,1.35,.38,.30)
]):
    B(papers,"sheet%d"%i,(w,.006,h),(x,.691,z),paper)
    for j in range(5):
        B(papers,"writing%d_%d"%(i,j),(w*.65,.002,.002),
          (x,.686,z+.07-j*.023),(.56,.57,.53))

# Computer monitor: blue inset face and a modest desktop stand.
monitor = asset("computer monitor")
mx,my,mz = -.74,.41,1.40
B(monitor,"black housing",MONITOR_SIZE,(mx,my,mz),black)
B(monitor,"blue screen",(.638,.006,.435),(mx,my-.031,mz+.006),(.025,.35,.78))
B(monitor,"task bar",(.638,.003,.018),(mx,my-.036,mz-.201),(.015,.18,.57))
B(monitor,"top screen highlight",(.638,.003,.023),(mx,my-.036,mz+.211),(.04,.48,.94))
B(monitor,"login box",(.047,.003,.023),(mx+.02,my-.037,mz-.004),(.62,.72,.77))
B(monitor,"login stripe",(.011,.002,.018),(mx+.015,my-.039,mz-.004),(.82,.13,.08))
B(monitor,"login caption",(.12,.002,.003),(mx,my-.039,mz-.035),(.58,.76,.87))
R(monitor,"neck",.026,(mx,.43,.79),(mx,.43,1.15),black)
B(monitor,"foot",(.30,.19,.024),(mx,.39,.761),black)

# Benchtop power supply at the left.
supply = asset("left bench power supply")
B(supply,"case",(.25,.26,.30),(-.91,.24,.91),(.40,.43,.35))
B(supply,"front panel",(.24,.012,.27),(-.91,.104,.91),cream)
B(supply,"display",(.15,.008,.063),(-.91,.094,.98),(.13,.19,.15))
for i in range(3):
    R(supply,"knob%d"%i,.021,(-.98+i*.064,.09,.865),(-.98+i*.064,.063,.865),gray)
for i in range(2):
    R(supply,"socket%d"%i,.010,(-.96+i*.085,.088,.80),(-.96+i*.085,.066,.80),
      red if i else black)

scope = asset("oscilloscope")
B(scope,"case",SCOPE_SIZE,(-.51,.31,.925),cream)
B(scope,"front",(.515,.015,.255),(-.51,.151,.925),(.68,.70,.62))
B(scope,"screen surround",(.275,.018,.208),(-.61,.137,.933),(.36,.40,.35))
B(scope,"dark glass",(.239,.005,.174),(-.61,.124,.933),(.075,.11,.10))
for i in range(5):
    B(scope,"screen grid v%d"%i,(.001,.002,.161),(-.71+i*.05,.120,.933),(.13,.18,.15))
for i in range(4):
    B(scope,"screen grid h%d"%i,(.228,.002,.001),(-.61,.120,.872+i*.04),(.13,.18,.15))
for row in range(3):
    for col in range(3):
        R(scope,"control%d_%d"%(row,col),.014,
          (-.42+col*.052,.133,.859+row*.062),
          (-.42+col*.052,.104,.859+row*.062),(.58,.60,.53))
for i in range(5):
    B(scope,"top switch%d"%i,(.024,.012,.009),(-.44+i*.034,.128,1.033),gray)
for x in (-.70,-.32):
    B(scope,"foot%.2f"%x,(.05,.12,.02),(x,.31,.775),black)

rear = asset("rear black power box")
B(rear,"body",(.34,.24,.12),(-.12,.38,.82),black)
B(rear,"front stripe",(.32,.008,.035),(-.12,.255,.817),(.07,.08,.07))
for i in range(4):
    R(rear,"terminal%d"%i,.013,(-.24+i*.08,.249,.816),
      (-.24+i*.08,.226,.816),yellow if i==0 else red if i==3 else silver)
for i in range(2):
    B(rear,"coiled item%d"%i,(.10,.11,.035),(-.20+i*.12,.40,.905),(.12,.17,.21))
S(rear,"top lead",[(-.29,.39,.93),(-.31,.48,.95),(-.17,.51,.94),(-.08,.44,.93)],.006,silver)

# Upright yellow multimeter; local geometry tilted back as a unit.
meter = asset("upright yellow multimeter")
B(meter,"yellow shell",(.17,.058,.315),(.26,.30,.948),yellow)
B(meter,"dark face",(.141,.007,.279),(.26,.267,.949),(.18,.21,.19))
B(meter,"LCD",(.115,.004,.065),(.26,.262,1.038),(.40,.48,.38))
for i in range(3):
    B(meter,"LCD segment%d"%i,(.018,.002,.028),(.225+i*.033,.258,1.037),(.19,.25,.20))
R(meter,"selector",.037,(.26,.258,.925),(.26,.246,.925),black)
R(meter,"selector pointer",.006,(.26,.239,.925),(.281,.239,.942),gray)
for i in range(3):
    R(meter,"input%d"%i,.009,(.215+i*.044,.258,.831),(.215+i*.044,.243,.831),black)
meter.turn(axis="+x",degrees=-10,pivot=(.26,.30,.79))

small = asset("small foreground meter")
B(small,"yellow rim",(.132,.21,.039),(.21,-.19,.774),yellow)
B(small,"face",(.112,.188,.008),(.21,-.19,.798),black)
B(small,"display",(.085,.05,.004),(.21,-.133,.805),(.42,.48,.39))
R(small,"dial",.029,(.21,-.207,.803),(.21,-.207,.817),(.23,.26,.24))
for i in range(2):
    R(small,"jack%d"%i,.009,(.183+i*.052,-.268,.805),(.183+i*.052,-.268,.816),red if i else black)
small.turn(axis="+z",degrees=-12)

keyboard = asset("keyboard")
B(keyboard,"body",(.79,.285,.032),(-.48,-.285,.765),black)
for row in range(5):
    for col in range(15):
        if row == 0 and 4 <= col <= 9:
            continue
        B(keyboard,"key%d_%d"%(row,col),(.041,.039,.012),
          (-.835+col*.049,-.391+row*.050,.787),(.045,.05,.048))
B(keyboard,"space",(.26,.036,.012),(-.49,-.391,.787),(.055,.06,.058))
keyboard.turn(axis="+z",degrees=13)

calculator = asset("calculator")
B(calculator,"body",(.18,.28,.035),(-.94,-.53,.769),(.075,.09,.085))
B(calculator,"LCD",(.142,.061,.005),(-.94,-.45,.791),(.42,.48,.41))
for row in range(5):
    for col in range(4):
        B(calculator,"button%d_%d"%(row,col),(.030,.025,.009),
          (-.999+col*.039,-.49-row*.035,.792),(.53,.55,.49))
calculator.turn(axis="+z",degrees=14)

board = asset("exposed circuit board")
B(board,"blue pcb",(.22,.15,.014),(-.62,.035,.756),(.018,.14,.38))
for i in range(5):
    B(board,"chip%d"%i,(.025,.035,.014),(-.70+i*.036,.032,.77),black)
for i in range(6):
    R(board,"capacitor%d"%i,.009,(-.69+i*.032,.083,.765),
      (-.69+i*.032,.083,.789),silver)
board.turn(axis="+z",degrees=15)

# Large articulated black bench lamp.
lamp = asset("black task lamp")
B(lamp,"clamp",(.08,.09,.11),(.91,.49,.80),black)
R(lamp,"lower arm",.014,(.91,.49,.83),(.78,.49,1.19),black)
R(lamp,"upper arm",.014,(.78,.49,1.19),(.76,.48,1.66),black)
R(lamp,"parallel arm",.009,(.81,.49,1.20),(.79,.48,1.65),silver)
R(lamp,"hinge",.032,(.75,.455,1.64),(.75,.505,1.64),black)
B(lamp,"long shade",(.64,.185,.065),(.39,.43,1.67),black)
B(lamp,"end housing",(.14,.17,.072),(.76,.43,1.66),black)
B(lamp,"underside diffuser",(.54,.14,.007),(.37,.43,1.633),(.72,.73,.64))
B(lamp,"small switch",(.035,.05,.008),(.15,.43,1.707),silver)
S(lamp,"power cord",[(.77,.48,1.63),(.86,.51,1.49),(.83,.49,1.22),(.94,.48,.93),(.91,.35,.76)],.006,black)

# Soldering station, stand, metal spring and iron.
station = asset("soldering equipment")
B(station,"base",(.26,.23,.09),(.79,.24,.79),(.12,.15,.15))
B(station,"sloped panel",(.23,.018,.075),(.79,.115,.825),(.30,.33,.29))
R(station,"temperature knob",.025,(.83,.098,.83),(.83,.076,.83),black)
B(station,"iron stand foot",(.21,.18,.023),(.76,-.06,.756),(.18,.19,.17))
R(station,"stand upright",.013,(.77,-.035,.77),(.84,.015,.94),silver)
for i in range(8):
    # Economical eight visible rings, each using four short segments.
    x=.82+i*.012
    pts=[(x,.005+.035*math.cos(t),.941+.035*math.sin(t))
         for t in (0,math.pi/2,math.pi,3*math.pi/2,2*math.pi)]
    S(station,"spring%d"%i,pts,.005,(.25,.28,.27))
R(station,"iron grip",.024,(.87,.07,.97),(.94,.24,1.04),(.025,.20,.22))
R(station,"iron collar",.026,(.86,.05,.962),(.88,.09,.978),silver)
R(station,"iron shaft",.007,(.78,-.13,.89),(.86,.05,.962),silver)
S(station,"iron cord",[(.94,.24,1.04),(1.01,.30,1.01),(1.04,.19,.85),(.98,-.10,.75),(.71,-.30,.75)],.009,black)

cans = asset("rear cans and bottle")
for i,(x,y,h,r) in enumerate([(.61,.47,.23,.041),(.74,.51,.20,.038)]):
    R(cans,"can%d"%i,r,(x,y,.745),(x,y,.745+h),silver)
    B(cans,"dark label%d"%i,(r*1.7,.008,h*.48),(x,y-r,.745+h*.49),(.18,.23,.19))
    R(cans,"cap%d"%i,r*.76,(x,y,.745+h),(x,y,.755+h),gray)
R(cans,"water bottle",.045,(1.00,.56,.76),(1.00,.56,.99),(.31,.39,.37))
R(cans,"bottle shoulder",.030,(1.00,.56,.99),(1.00,.56,1.045),(.40,.46,.42))
R(cans,"blue cap",.022,(1.00,.56,1.045),(1.00,.56,1.077),(.035,.11,.28))

# Three red handled wall pliers.
tools = asset("hanging pliers")
for i,(x,z) in enumerate([(-.50,1.40),(-.38,1.38),(-.23,1.36)]):
    R(tools,"left handle%d"%i,.010,(x-.045,.661,z-.13),(x-.015,.654,z-.035),red)
    R(tools,"right handle%d"%i,.010,(x+.045,.661,z-.13),(x+.015,.654,z-.035),red)
    R(tools,"left jaw%d"%i,.007,(x-.015,.654,z-.035),(x+.012,.653,z+.06),silver)
    R(tools,"right jaw%d"%i,.007,(x+.015,.654,z-.035),(x-.009,.653,z+.06),silver)
    R(tools,"pivot%d"%i,.014,(x,.645,z-.025),(x,.635,z-.025),gray)

# Foreground wire tangle, separate editable leads.
wires = asset("test leads and loose cables")
for i in range(19):
    cx=random.uniform(-.18,.52)
    cy=random.uniform(-.46,-.17)
    rx=random.uniform(.12,.34)
    ry=random.uniform(.075,.20)
    phase=random.uniform(0,6.28)
    pts=[]
    for j in range(11):
        t=phase+j*math.pi*1.8/10
        pts.append((cx+rx*math.cos(t),cy+ry*math.sin(t),
                    .752+.006*(i%4)+.008*math.sin(j*1.1)**2))
    S(wires,"cable%d"%i,pts,.0038,red if i%3==0 else black)
    p=pts[0]
    R(wires,"plug%d"%i,.008,p,(p[0]+.043,p[1]+.014,p[2]+.002),black if i%2 else red)
S(wires,"upright meter red lead",[(.29,.25,.84),(.36,.12,.78),(.47,-.10,.76),(.35,-.36,.77),(.04,-.42,.77)],.004,red)
S(wires,"upright meter black lead",[(.23,.25,.84),(.16,.12,.78),(.12,-.07,.76),(.30,-.30,.77),(.50,-.43,.77)],.004,black)

probes = asset("foreground probes and hand tools")
for i,(x,y,angle,col) in enumerate([
    (.11,-.59,-8,black),(.35,-.56,-18,red),(.52,-.48,35,black),
    (.47,-.19,65,(.03,.14,.45)),(.59,-.21,70,yellow)
]):
    dx=.12*math.cos(math.radians(angle))
    dy=.12*math.sin(math.radians(angle))
    R(probes,"handle%d"%i,.012,(x-dx,y-dy,.773),(x+dx,y+dy,.773),col)
    R(probes,"steel point%d"%i,.003,(x+dx,y+dy,.773),(x+dx*1.7,y+dy*1.7,.773),silver)

misc = asset("small desktop items")
R(misc,"solder spool",.044,(-.27,-.35,.747),(-.27,-.35,.768),silver)
R(misc,"spool center",.018,(-.27,-.35,.768),(-.27,-.35,.773),(.18,.38,.27))
for i in range(10):
    x=random.uniform(.64,.94)
    y=random.uniform(-.60,-.26)
    B(misc,"yellow tape scrap%d"%i,(random.uniform(.035,.065),.026,.002),
      (x,y,.747),(.96,.69,.025))
for i,(x,y) in enumerate([(.49,.17),(.82,-.12),(-.12,.47)]):
    B(misc,"paper scrap%d"%i,(.14,.15,.002),(x,y,.748),paper)
B(misc,"right blue packaging",(.17,.41,.012),(1.035,-.46,.76),(.02,.10,.29))
for i in range(6):
    R(misc,"packaged tool%d"%i,.009,(.99+i*.021,-.65,.78),
      (.99+i*.021,-.40,.78),red if i%2 else black)
B(misc,"package header",(.17,.06,.006),(1.035,-.285,.776),(.12,.23,.43))

realize(scene)
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-.45,-1.2,2.6),power=160,size=2.1,target=(0,.1,.8),color=(1.0,.94,.83))
area_emitter((.50,.35,1.60),power=18,size=.65,target=(.42,-.12,.74),color=(1.0,1.0,.94))
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Workshop world")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.34,.36,.35,1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.38

# Screen surface remains geometry; emission only gives the blue display its glow.
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    for material in obj.data.materials:
        if material is None:
            continue
        material.use_nodes = True
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value=.72
            color = bsdf.inputs["Base Color"].default_value
            if color[2] > .65 and color[0] < .08 and color[1] > .25:
                emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
                strength = bsdf.inputs.get("Emission Strength")
                if emission:
                    emission.default_value=(color[0],color[1],color[2],1)
                if strength:
                    strength.default_value=.45
