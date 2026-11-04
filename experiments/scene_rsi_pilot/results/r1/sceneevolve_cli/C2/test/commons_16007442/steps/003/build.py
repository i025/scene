from sceneact import *
import bpy
import math
import random

random.seed(19)
scene = Scene("Electronics workbench")

CAMERA_POSITION = (-.48, -2.75, 2.34)
CAMERA_TARGET = (0, .13, 1.03)
CAMERA_LENS = 45
BENCH_SIZE = (2.18, 1.70, .07)
MONITOR_SIZE = (.805, .055, .663)
SCOPE_SIZE = (.53, .30, .28)

wood = (.235, .115, .065)
black = (.009, .013, .014)
gray = (.34, .36, .33)
cream = (.48, .50, .43)
silver = (.48, .51, .48)
red = (.55, .014, .009)
yellow = (.88, .49, .008)
paper = (.74, .74, .68)

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def B(a, name, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    assert all(math.isfinite(v) for v in center)
    a.include(name, box(size=size, center=center, color=color))

def R(a, name, radius, start, end, color):
    assert math.isfinite(radius) and radius > 0
    assert all(math.isfinite(v) for v in (*start, *end))
    assert sum((u-v)**2 for u,v in zip(start,end)) > 1e-16
    a.include(name, rod(radius=radius, start=start, end=end, color=color))

def S(a, name, points, radius, color):
    assert radius > 0
    assert all(all(math.isfinite(v) for v in p) for p in points)
    assert all(sum((u-v)**2 for u,v in zip(p,q)) > 1e-16
               for p,q in zip(points,points[1:]))
    a.include(name, sweep_tube(points=points, radius=radius, color=color))

bench = asset("brown workbench")
B(bench,"laminated top",BENCH_SIZE,(0,-.17,.705),wood)
B(bench,"front edge",(2.18,.035,.065),(0,-1.013,.70),(.18,.085,.045))

wall = asset("rear wall")
B(wall,"plaster",(3.1,.07,2.8),(0,.735,1.30),(.43,.43,.37))
B(wall,"left return",(.06,1.7,2.5),(-1.17,.1,1.3),(.34,.35,.30))

for ci,(cx,width,rows,cols,cz) in enumerate([
    (-.02,.56,4,4,1.86),(.70,.82,5,5,1.84)
]):
    a = asset("parts cabinet %d"%ci)
    height = .44 if ci == 0 else .52
    B(a,"outer case",(width,.16,height),(cx,.64,cz),black)
    cw=(width-.035)/cols
    ch=(height-.025)/rows
    for row in range(rows):
        for col in range(cols):
            x=cx-width/2+.018+cw*(col+.5)
            z=cz-height/2+.012+ch*(row+.5)
            k="%d_%d"%(row,col)
            B(a,"drawer "+k,(cw-.009,.013,ch-.009),
              (x,.548,z),(.035,.048,.043))
            B(a,"label "+k,(cw*.55,.004,ch*.24),
              (x,.539,z-ch*.18),(.43,.45,.40))
            B(a,"pull "+k,(cw*.27,.017,.008),
              (x,.53,z+ch*.12),(.025,.032,.03))

papers=asset("wall paperwork")
for i,(x,z,w,h) in enumerate([
    (-.12,1.40,.45,.28),(.31,1.38,.37,.31),(.70,1.35,.38,.30)
]):
    B(papers,"sheet%d"%i,(w,.006,h),(x,.691,z),paper)
    for j in range(5):
        B(papers,"writing%d_%d"%(i,j),(w*.65,.002,.002),
          (x,.686,z+.07-j*.023),(.52,.53,.49))

monitor=asset("computer monitor")
mx,my,mz=-.81,.41,1.43
B(monitor,"black housing",MONITOR_SIZE,(mx,my,mz),black)
B(monitor,"blue screen",(.7337,.006,.5655),
  (mx,my-.031,mz+.0078),(.025,.35,.78))
B(monitor,"task bar",(.7337,.003,.0234),
  (mx,my-.036,mz-.2613),(.015,.18,.57))
B(monitor,"top screen highlight",(.7337,.003,.0299),
  (mx,my-.036,mz+.2743),(.04,.48,.94))
B(monitor,"login box",(.05405,.003,.0299),
  (mx+.023,my-.037,mz-.0052),(.62,.72,.77))
B(monitor,"login stripe",(.01265,.002,.0234),
  (mx+.01725,my-.039,mz-.0052),(.82,.13,.08))
B(monitor,"login caption",(.138,.002,.0039),
  (mx,my-.039,mz-.0455),(.58,.76,.87))
R(monitor,"neck",.026,(mx,.43,.79),(mx,.43,1.15),black)
B(monitor,"foot",(.30,.19,.024),(mx,.39,.761),black)
monitor.turn(axis="+z",degrees=24,pivot=(mx,my,mz))

supply=asset("left bench power supply")
B(supply,"case",(.25,.26,.30),(-.91,.24,.91),(.28,.31,.25))
B(supply,"front panel",(.24,.012,.27),(-.91,.104,.91),cream)
B(supply,"display",(.15,.008,.063),(-.91,.094,.98),(.055,.09,.065))
for i in range(3):
    R(supply,"knob%d"%i,.021,(-.98+i*.064,.09,.865),
      (-.98+i*.064,.063,.865),gray)
for i in range(2):
    R(supply,"socket%d"%i,.010,(-.96+i*.085,.088,.80),
      (-.96+i*.085,.066,.80),red if i else black)

scope=asset("oscilloscope")
B(scope,"case",SCOPE_SIZE,(-.51,.31,.925),cream)
B(scope,"front",(.515,.015,.255),(-.51,.151,.925),(.52,.54,.47))
B(scope,"screen surround",(.275,.018,.208),
  (-.61,.137,.933),(.25,.29,.25))
B(scope,"dark glass",(.239,.005,.174),(-.61,.124,.933),(.035,.055,.045))
for i in range(5):
    B(scope,"screen grid v%d"%i,(.001,.002,.161),
      (-.71+i*.05,.120,.933),(.08,.12,.09))
for i in range(4):
    B(scope,"screen grid h%d"%i,(.228,.002,.001),
      (-.61,.120,.872+i*.04),(.08,.12,.09))
for row in range(3):
    for col in range(3):
        R(scope,"control%d_%d"%(row,col),.014,
          (-.42+col*.052,.133,.859+row*.062),
          (-.42+col*.052,.104,.859+row*.062),(.43,.45,.39))
for i in range(5):
    B(scope,"top switch%d"%i,(.024,.012,.009),
      (-.44+i*.034,.128,1.033),gray)
for i,x in enumerate((-.70,-.32)):
    B(scope,"foot%d"%i,(.05,.12,.02),(x,.31,.775),black)

rear=asset("rear black power box")
B(rear,"body",(.34,.24,.12),(-.12,.38,.82),black)
B(rear,"front stripe",(.32,.008,.035),(-.12,.255,.817),(.035,.04,.035))
for i in range(4):
    R(rear,"terminal%d"%i,.013,(-.24+i*.08,.249,.816),
      (-.24+i*.08,.226,.816),
      yellow if i==0 else red if i==3 else silver)
for i in range(2):
    B(rear,"coiled item%d"%i,(.10,.11,.035),
      (-.20+i*.12,.40,.905),(.07,.10,.13))
S(rear,"top lead",[(-.29,.39,.93),(-.31,.48,.95),
                  (-.17,.51,.94),(-.08,.44,.93)],.006,silver)

meter=asset("upright yellow multimeter")
B(meter,"yellow shell",(.17,.058,.315),(.26,.30,.948),yellow)
B(meter,"dark face",(.141,.007,.279),(.26,.267,.949),(.095,.12,.105))
B(meter,"LCD",(.115,.004,.065),(.26,.262,1.038),(.27,.34,.26))
for i in range(3):
    B(meter,"LCD segment%d"%i,(.018,.002,.028),
      (.225+i*.033,.258,1.037),(.09,.14,.10))
R(meter,"selector",.037,(.26,.258,.925),(.26,.246,.925),black)
R(meter,"selector pointer",.006,(.26,.239,.925),(.281,.239,.942),gray)
for i in range(3):
    R(meter,"input%d"%i,.009,(.215+i*.044,.258,.831),
      (.215+i*.044,.243,.831),black)
meter.turn(axis="+x",degrees=-10,pivot=(.26,.30,.79))
meter.resize((1.2,1.2,1.2),pivot=(.26,.30,.79))
meter.move((.035,0,0))

small=asset("small foreground meter")
B(small,"yellow rim",(.132,.21,.039),(.21,-.19,.774),yellow)
B(small,"face",(.112,.188,.008),(.21,-.19,.798),black)
B(small,"display",(.085,.05,.004),(.21,-.133,.805),(.29,.35,.27))
R(small,"dial",.029,(.21,-.207,.803),(.21,-.207,.817),(.13,.16,.14))
for i in range(2):
    R(small,"jack%d"%i,.009,(.183+i*.052,-.268,.805),
      (.183+i*.052,-.268,.816),red if i else black)
small.turn(axis="+z",degrees=-12)

keyboard=asset("keyboard")
B(keyboard,"body",(.79,.285,.032),(-.48,-.285,.765),black)
for row in range(5):
    for col in range(15):
        if row==0 and 4<=col<=9:
            continue
        B(keyboard,"key%d_%d"%(row,col),(.041,.039,.012),
          (-.835+col*.049,-.391+row*.050,.787),(.023,.028,.025))
B(keyboard,"space",(.26,.036,.012),(-.49,-.391,.787),(.028,.033,.03))
keyboard.turn(axis="+z",degrees=13)

calculator=asset("calculator")
B(calculator,"body",(.18,.28,.035),(-.94,-.53,.769),(.035,.045,.04))
B(calculator,"LCD",(.142,.061,.005),(-.94,-.45,.791),(.30,.36,.29))
for row in range(5):
    for col in range(4):
        B(calculator,"button%d_%d"%(row,col),(.030,.025,.009),
          (-.999+col*.039,-.49-row*.035,.792),(.41,.43,.38))
calculator.turn(axis="+z",degrees=14)

board=asset("exposed circuit board")
B(board,"blue pcb",(.22,.15,.014),(-.62,.035,.756),(.012,.09,.28))
for i in range(5):
    B(board,"chip%d"%i,(.025,.035,.014),(-.70+i*.036,.032,.77),black)
for i in range(6):
    R(board,"capacitor%d"%i,.009,(-.69+i*.032,.083,.765),
      (-.69+i*.032,.083,.789),silver)
board.turn(axis="+z",degrees=15)

lamp=asset("black task lamp")
B(lamp,"clamp",(.08,.09,.11),(.91,.49,.80),black)
R(lamp,"lower arm",.014,(.91,.49,.83),(.78,.49,1.19),black)
R(lamp,"upper arm",.014,(.78,.49,1.19),(.76,.48,1.52),black)
R(lamp,"parallel arm",.009,(.81,.49,1.20),(.79,.48,1.51),silver)
R(lamp,"hinge",.032,(.75,.455,1.50),(.75,.505,1.50),black)
B(lamp,"long shade",(.69,.24,.10),(.365,.43,1.53),black)
B(lamp,"end housing",(.14,.22,.10),(.76,.43,1.52),black)
B(lamp,"underside diffuser",(.59,.19,.007),
  (.345,.43,1.477),(.60,.61,.53))
B(lamp,"small switch",(.035,.05,.008),(.125,.43,1.584),silver)
S(lamp,"power cord",[(.77,.48,1.49),(.86,.51,1.42),
                    (.83,.49,1.22),(.94,.48,.93),(.91,.35,.76)],.006,black)

station=asset("soldering equipment")
B(station,"base",(.26,.23,.09),(.79,.24,.79),(.06,.085,.08))
B(station,"sloped panel",(.23,.018,.075),(.79,.115,.825),(.19,.22,.19))
R(station,"temperature knob",.025,(.83,.098,.83),(.83,.076,.83),black)
B(station,"iron stand foot",(.21,.18,.023),(.76,-.06,.756),(.09,.10,.085))
R(station,"stand upright",.013,(.77,-.035,.77),(.84,.015,.94),silver)
for i in range(8):
    x=.82+i*.012
    pts=[(x,.005+.035*math.cos(t),.941+.035*math.sin(t))
         for t in (0,math.pi/2,math.pi,3*math.pi/2,2*math.pi)]
    S(station,"spring%d"%i,pts,.005,(.17,.20,.19))
R(station,"iron grip",.024,(.87,.07,.97),(.94,.24,1.04),(.015,.15,.17))
R(station,"iron collar",.026,(.86,.05,.962),(.88,.09,.978),silver)
R(station,"iron shaft",.007,(.78,-.13,.89),(.86,.05,.962),silver)
S(station,"iron cord",[(.94,.24,1.04),(1.01,.30,1.01),
                      (1.04,.19,.85),(.98,-.10,.75),(.71,-.30,.75)],.009,black)

cans=asset("rear cans and bottle")
for i,(x,y,h,r) in enumerate([(.61,.47,.23,.041),(.74,.51,.20,.038)]):
    R(cans,"can%d"%i,r,(x,y,.745),(x,y,.745+h),silver)
    B(cans,"dark label%d"%i,(r*1.7,.008,h*.48),
      (x,y-r,.745+h*.49),(.09,.13,.10))
    R(cans,"cap%d"%i,r*.76,(x,y,.745+h),(x,y,.755+h),gray)
R(cans,"water bottle",.045,(1,.56,.76),(1,.56,.99),(.18,.25,.23))
R(cans,"bottle shoulder",.030,(1,.56,.99),(1,.56,1.045),(.25,.31,.27))
R(cans,"blue cap",.022,(1,.56,1.045),(1,.56,1.077),(.025,.08,.22))

tools=asset("hanging pliers")
for i,(x,z) in enumerate([(-.50,1.40),(-.38,1.38),(-.23,1.36)]):
    R(tools,"left handle%d"%i,.010,
      (x-.045,.661,z-.13),(x-.015,.654,z-.035),red)
    R(tools,"right handle%d"%i,.010,
      (x+.045,.661,z-.13),(x+.015,.654,z-.035),red)
    R(tools,"left jaw%d"%i,.007,
      (x-.015,.654,z-.035),(x+.012,.653,z+.06),silver)
    R(tools,"right jaw%d"%i,.007,
      (x+.015,.654,z-.035),(x-.009,.653,z+.06),silver)
    R(tools,"pivot%d"%i,.014,(x,.645,z-.025),(x,.635,z-.025),gray)

wires=asset("test leads and loose cables")
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
    R(wires,"plug%d"%i,.008,p,
      (p[0]+.043,p[1]+.014,p[2]+.002),black if i%2 else red)
S(wires,"upright meter red lead",[(.325,.25,.85),(.36,.12,.78),
  (.47,-.10,.76),(.35,-.36,.77),(.04,-.42,.77)],.004,red)
S(wires,"upright meter black lead",[(.265,.25,.85),(.16,.12,.78),
  (.12,-.07,.76),(.30,-.30,.77),(.50,-.43,.77)],.004,black)
# Preserve the rear extent while increasing foreground spread.
wires.resize((1,1.35,1),pivot=(.2,.25,.75))

probes=asset("foreground probes and hand tools")
for i,(x,y,angle,col) in enumerate([
    (.11,-.72,-8,black),(.35,-.69,-18,red),(.52,-.59,35,black),
    (.47,-.19,65,(.03,.14,.45)),(.59,-.21,70,yellow)
]):
    dx=.12*math.cos(math.radians(angle))
    dy=.12*math.sin(math.radians(angle))
    R(probes,"handle%d"%i,.012,(x-dx,y-dy,.773),(x+dx,y+dy,.773),col)
    R(probes,"steel point%d"%i,.003,(x+dx,y+dy,.773),
      (x+dx*1.7,y+dy*1.7,.773),silver)

misc=asset("small desktop items")
R(misc,"solder spool",.044,(-.27,-.35,.747),(-.27,-.35,.768),silver)
R(misc,"spool center",.018,(-.27,-.35,.768),(-.27,-.35,.773),(.10,.27,.17))
for i in range(10):
    x=random.uniform(.64,.94)
    y=random.uniform(-.60,-.26)
    B(misc,"yellow tape scrap%d"%i,(random.uniform(.035,.065),.026,.002),
      (x,y,.747),(.90,.59,.012))
for i,(x,y) in enumerate([(.49,.17),(.82,-.12),(-.12,.47)]):
    B(misc,"paper scrap%d"%i,(.14,.15,.002),(x,y,.748),paper)
B(misc,"right blue packaging",(.17,.41,.012),(1.035,-.46,.76),(.012,.065,.22))
for i in range(6):
    R(misc,"packaged tool%d"%i,.009,(.99+i*.021,-.65,.78),
      (.99+i*.021,-.40,.78),red if i%2 else black)
B(misc,"package header",(.17,.06,.006),(1.035,-.285,.776),(.07,.16,.34))

# Checked: positive finite dimensions, distinct rod/sweep endpoints,
# unique indexed children, explicit transformation pivots, no fillets.
# Camera, world and lights follow realize. No rendering or saving calls.
realize(scene)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.45,-1.2,2.6),power=100,size=1.4,
             target=(0,.1,.8),color=(1,.94,.83))
area_emitter((.50,.35,1.60),power=18,size=.65,
             target=(.42,-.12,.74),color=(1,1,.94))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Workshop world")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.34,.36,.35,1)
background.inputs["Strength"].default_value=.38

seen=set()
for obj in bpy.data.objects:
    if obj.type!="MESH":
        continue
    for material in obj.data.materials:
        if material is None or material.as_pointer() in seen:
            continue
        seen.add(material.as_pointer())
        material.use_nodes=True
        bsdf=material.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        bsdf.inputs["Roughness"].default_value=.72
        color=bsdf.inputs["Base Color"].default_value
        if color[2]>.65 and color[0]<.08 and color[1]>.25:
            emission=bsdf.inputs.get("Emission Color")
            if emission is None:
                emission=bsdf.inputs.get("Emission")
            strength=bsdf.inputs.get("Emission Strength")
            if emission is not None:
                emission.default_value=(color[0],color[1],color[2],1)
            if strength is not None:
                strength.default_value=.45
