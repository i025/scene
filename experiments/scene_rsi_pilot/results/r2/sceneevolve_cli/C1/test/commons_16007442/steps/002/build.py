from sceneact import *
import bpy, math, random
random.seed(18)

# Framing was too wide: enlarge the scene and crop the front desk edge.
# Reverse the camera's lateral offset to match the monitor and bench perspective.
# Enlarge the monitor and lamp, and darken the washed-out wall and desktop.

scene=Scene('Electronics workbench')
BLACK=(.012,.016,.015)
GREY=(.40,.43,.40)
CREAM=(.59,.61,.52)
RED=(.48,.015,.009)
YELLOW=(.88,.53,.012)

def put(p,n,s,c,col):
    p.include(n,box(s,center=c,color=col))
def line(p,n,a,b,r,col):
    p.include(n,rod(r,start=a,end=b,color=col))
def path(p,n,pts,r,col):
    for i in range(len(pts)-1):
        line(p,n+str(i),pts[i],pts[i+1],r,col)
def knob(p,n,x,y,z,r=.014,color=GREY):
    line(p,n,(x,y,z),(x,y-.019,z),r,color)

room=Asset('Room and bench')
put(room,'back wall',(3.8,.08,2.8),(0,.88,1.4),(.48,.49,.44))
put(room,'left wall',(.07,2.8,2.8),(-1.39,-.25,1.4),(.35,.36,.32))
put(room,'desktop',(2.85,2.05,.085),(0,-.17,.73),(.28,.135,.083))
put(room,'back trim',(2.85,.045,.08),(0,.78,.80),(.20,.12,.075))
scene.include('architecture',room)

monitor=Asset('Computer display')
put(monitor,'foot',(.39,.25,.025),(-.88,.40,.79),BLACK)
line(monitor,'stand',(-.88,.47,.80),(-.88,.49,1.17),.037,BLACK)
put(monitor,'bezel',(.85,.065,.72),(-.92,.47,1.56),BLACK)
put(monitor,'display',(.785,.008,.644),(-.92,.432,1.57),(.018,.32,.79))
put(monitor,'desktop blue',(.781,.005,.584),(-.92,.425,1.585),(.10,.43,.79))
put(monitor,'taskbar',(.781,.006,.025),(-.92,.42,1.258),(.008,.13,.62))
for i,c in enumerate(((.85,.13,.03),(.15,.6,.15),(.025,.25,.85),(.95,.65,.06))):
    put(monitor,'logo'+str(i),(.019,.003,.019),
        (-.95+(i%2)*.025,.419,1.57-(i//2)*.025),c)
put(monitor,'login text',(.105,.003,.004),(-.93,.418,1.515),(.49,.69,.88))
monitor.turn('z',-12,pivot=(-.92,.47,1.56))
scene.include('monitor',monitor)

scope=Asset('Oscilloscope')
put(scope,'body',(.58,.34,.30),(-.43,.39,.97),CREAM)
put(scope,'face',(.575,.013,.285),(-.43,.212,.97),(.67,.68,.59))
put(scope,'screen bezel',(.285,.019,.235),(-.555,.198,.975),(.24,.27,.24))
put(scope,'screen',(.247,.006,.190),(-.555,.185,.975),(.025,.045,.038))
for i in range(7):
    put(scope,'screen grid v'+str(i),(.001,.001,.175),
        (-.663+i*.036,.180,.975),(.065,.09,.072))
for i in range(5):
    put(scope,'screen grid h'+str(i),(.233,.001,.001),
        (-.555,.179,.898+i*.038),(.065,.09,.072))
for col in range(4):
    for row in range(3):
        knob(scope,'dial%d_%d'%(col,row),-.365+col*.057,.19,.888+row*.069,
             .017 if col>1 else .012,(.49,.52,.45))
for j in range(5):
    put(scope,'button'+str(j),(.024,.014,.011),
        (-.36+j*.042,.19,1.085),(.30,.34,.29))
for i in range(2):
    put(scope,'foot'+str(i),(.07,.06,.022),(-.65+i*.43,.27,.805),BLACK)
scene.include('scope',scope)

supply=Asset('Bench power supply')
put(supply,'case',(.28,.27,.30),(-.94,.18,.955),(.44,.47,.39))
put(supply,'front',(.27,.015,.28),(-.94,.037,.955),(.53,.56,.45))
put(supply,'display',(.21,.01,.078),(-.94,.025,1.018),(.035,.065,.045))
for i in range(3):
    knob(supply,'knob'+str(i),-1.02+.08*i,.019,.90,.025,(.45,.48,.41))
put(supply,'label',(.16,.01,.025),(-.95,.024,1.10),(.69,.67,.42))
scene.include('supply',supply)

unit=Asset('Black instrument')
put(unit,'body',(.40,.25,.16),(.12,.45,.88),(.017,.025,.025))
put(unit,'top',(.39,.24,.012),(.12,.45,.969),(.09,.13,.15))
for i,c in enumerate((YELLOW,BLACK,(.60,.62,.57),RED)):
    knob(unit,'socket'+str(i),-.015+.09*i,.315,.86,.017,c)
path(unit,'headphone lead',[(.02,.43,1.0),(-.01,.47,1.07),
    (.08,.53,1.09),(.19,.49,1.04)],.013,BLACK)
for i in range(3):
    path(unit,'headphones'+str(i),[(-.02+i*.025,.46,.99),
        (-.04+i*.025,.56,1.05),(.08+i*.025,.61,1.06),
        (.20+i*.025,.54,.99)],.012,(.04,.055,.075))
scene.include('instrument',unit)

meter=Asset('Upright yellow multimeter')
put(meter,'rubber case',(.205,.065,.36),(.45,.32,1.005),YELLOW)
put(meter,'dark face',(.173,.012,.31),(.45,.28,1.01),(.065,.085,.075))
put(meter,'lcd',(.14,.008,.075),(.45,.27,1.111),(.39,.46,.35))
put(meter,'lcd digits',(.09,.004,.009),(.45,.264,1.106),(.15,.22,.16))
knob(meter,'selector',.45,.263,.973,.047,BLACK)
for i in range(8):
    a=i*math.pi/4
    put(meter,'dial mark'+str(i),(.012,.004,.006),
        (.45+.062*math.cos(a),.260,.973+.062*math.sin(a)),(.65,.65,.48))
for i in range(3):
    knob(meter,'jack'+str(i),.398+i*.05,.262,.865,.013,RED if i==2 else BLACK)
meter.turn('x',-12,pivot=(.45,.32,.84))
scene.include('yellow meter',meter)

keyboard=Asset('Keyboard')
put(keyboard,'base',(.93,.36,.035),(-.48,-.36,.80),(.015,.021,.020))
for row in range(5):
    for col in range(14):
        put(keyboard,'key%d_%d'%(row,col),(.047,.043,.019),
            (-.894+col*.063,-.500+row*.059,.826),(.025,.031,.029))
put(keyboard,'space',(.26,.043,.019),(-.56,-.50,.828),BLACK)
keyboard.turn('z',14,pivot=(-.48,-.36,.80))
scene.include('keyboard',keyboard)

mouse=Asset('Mouse')
mouse.include('body',ball(.066,center=(.39,-.05,.814),color=(.43,.45,.40)))
mouse.members['body'].resize((.72,1.22,.60))
path(mouse,'cord',[(.39,-.01,.82),(.38,.07,.79),(.29,.13,.78),
    (.15,.11,.78),(.12,.17,.78)],.006,BLACK)
scene.include('mouse',mouse)

hand=Asset('Small handheld meter')
put(hand,'body',(.14,.23,.033),(.32,-.25,.807),(.018,.025,.018))
put(hand,'screen',(.095,.052,.006),(.32,-.19,.828),(.37,.46,.33))
line(hand,'dial',(.32,-.28,.826),(.32,-.28,.842),.035,YELLOW)
put(hand,'button',(.025,.023,.008),(.28,-.23,.83),YELLOW)
hand.turn('z',-16)
scene.include('small meter',hand)

calc=Asset('Calculator')
put(calc,'case',(.19,.31,.034),(-1.04,-.62,.805),(.07,.09,.085))
put(calc,'lcd',(.15,.064,.008),(-1.04,-.527,.827),(.35,.43,.35))
for row in range(6):
    for col in range(4):
        put(calc,'key%d%d'%(row,col),(.03,.023,.009),
            (-1.10+col*.04,-.75+row*.032,.828),(.44,.47,.43))
calc.turn('z',-13)
scene.include('calculator',calc)

drawers=Asset('Parts organizers')
for cabinet,(cx,width,ncols) in enumerate(((.98,.94,6),(.06,.62,4))):
    put(drawers,'frame'+str(cabinet),(width,.16,.60),(cx,.79,2.00),(.027,.04,.032))
    for row in range(6):
        for col in range(ncols):
            x=cx-width/2+.026+(col+.5)*(width-.045)/ncols
            z=1.75+row*.096
            w=(width-.045)/ncols-.009
            name='%d_%d_%d'%(cabinet,row,col)
            put(drawers,'drawer'+name,(w,.021,.079),(x,.696,z),(.085,.115,.095))
            put(drawers,'label'+name,(w*.59,.005,.018),(x,.682,z-.016),(.47,.49,.40))
            put(drawers,'label ink'+name,(w*.34,.002,.003),(x,.678,z-.016),(.14,.17,.13))
scene.include('drawers',drawers)

papers=Asset('Wall paper and hanging tools')
for i in range(3):
    put(papers,'sheet'+str(i),(.35,.008,.27),(-.13+i*.36,.818,1.42),(.70,.70,.62))
    for j in range(5):
        put(papers,'writing%d_%d'%(i,j),(.21,.002,.001),
            (-.13+i*.36,.812,1.47+j*.017),(.47,.48,.42))
for k,x in enumerate((-.51,-.37,-.19)):
    z=1.38+(.04 if k==1 else 0)
    path(papers,'left grip'+str(k),[(x-.025,.76,z+.08),
        (x-.035,.751,z-.035),(x-.066,.75,z-.12),(x-.055,.75,z-.18)],.012,RED)
    path(papers,'right grip'+str(k),[(x+.015,.76,z+.09),
        (x+.025,.751,z-.035),(x+.060,.75,z-.12),(x+.045,.75,z-.18)],.012,RED)
    line(papers,'jaw'+str(k),(x-.018,.76,z+.035),(x,.76,z+.15),.014,(.12,.14,.12))
scene.include('wall details',papers)

lamp=Asset('Long black task lamp')
put(lamp,'base',(.19,.17,.035),(1.02,.38,.80),BLACK)
path(lamp,'upright',[(1.02,.4,.81),(1.03,.47,1.33),(.98,.47,1.70)],.015,BLACK)
line(lamp,'arm',(.98,.47,1.70),(.67,.43,1.76),.025,BLACK)
put(lamp,'long shade',(.94,.23,.083),(.41,.43,1.76),(.007,.011,.010))
put(lamp,'shade underside',(.80,.17,.008),(.39,.43,1.715),(.49,.52,.43))
lamp.members['long shade'].turn('z',-8)
line(lamp,'joint',(.85,.42,1.75),(.96,.42,1.75),.052,BLACK)
scene.include('lamp',lamp)

station=Asset('Soldering station')
put(station,'box',(.27,.25,.13),(.91,.32,.86),(.12,.17,.14))
put(station,'panel',(.25,.012,.11),(.91,.188,.86),(.03,.045,.035))
knob(station,'control',.94,.176,.86,.035,BLACK)
line(station,'iron grip',(.96,.20,.97),(1.10,.38,1.10),.028,(.06,.24,.25))
line(station,'iron tip',(.96,.20,.97),(.82,.04,.84),.009,(.38,.42,.39))
path(station,'cord',[(1.10,.38,1.10),(1.18,.36,1.05),(1.22,.17,.82),
    (1.15,-.05,.79),(.94,-.12,.79)],.011,BLACK)
put(station,'holder base',(.22,.20,.022),(1.08,-.10,.79),(.15,.13,.09))
for i in range(9):
    a=i*math.pi*2/8
    line(station,'holder coil'+str(i),
         (1.08+.048*math.cos(a),-.10+.048*math.sin(a),.82+i*.013),
         (1.08+.048*math.cos(a+.7),-.10+.048*math.sin(a+.7),.833+i*.013),
         .008,(.22,.25,.23))
scene.include('soldering station',station)

misc=Asset('Workbench clutter')
put(misc,'paper on desk',(.35,.34,.005),(.79,.04,.79),(.73,.73,.64))
for i in range(2):
    x=.74+i*.13
    line(misc,'can'+str(i),(x,.58,.78),(x,.58,1.02-i*.025),.047,(.36,.41,.37))
    line(misc,'can rim'+str(i),(x,.58,1.019-i*.025),(x,.58,1.03-i*.025),.043,(.56,.60,.55))
    put(misc,'can label'+str(i),(.06,.009,.10),(x,.531,.90),(.36,.36,.31))
line(misc,'bottle',(1.18,.66,.79),(1.18,.66,1.13),.057,(.25,.31,.26))
line(misc,'bottle neck',(1.18,.66,1.13),(1.18,.66,1.21),.023,(.39,.45,.38))
line(misc,'cap',(1.18,.66,1.21),(1.18,.66,1.24),.025,(.06,.07,.18))
put(misc,'circuit board',(.24,.17,.018),(-.67,.015,.80),(.015,.075,.23))
for i in range(7):
    put(misc,'board component'+str(i),(.024,.035,.021),
        (-.76+i*.030,.015,.82),(.11,.14,.11))
for i in range(12):
    note=box((random.uniform(.045,.075),.042,.003),
        center=(random.uniform(.64,1.05),random.uniform(-.73,-.35),.789),
        color=(.90,.63,.065))
    note.turn('z',random.uniform(-35,35))
    misc.include('sticky note'+str(i),note)
line(misc,'solder reel',(-.38,-.59,.785),(-.38,-.59,.817),.046,(.44,.53,.46))
line(misc,'reel center',(-.38,-.59,.817),(-.38,-.59,.821),.018,(.19,.16,.11))
put(misc,'right tool package',(.22,.40,.018),(1.13,-.57,.79),(.065,.11,.20))
for i in range(6):
    line(misc,'precision tool'+str(i),(1.045+i*.031,-.72,.814),
         (1.045+i*.031,-.43,.814),.007,(.24,.28,.25))
    line(misc,'tool handle'+str(i),(1.045+i*.031,-.72,.814),
         (1.045+i*.031,-.63,.814),.011,(.20,.025,.018))
scene.include('clutter',misc)

wires=Asset('Tangled test leads')
for i in range(18):
    cx=random.uniform(-.18,.62)
    cy=random.uniform(-.59,-.15)
    rx=random.uniform(.12,.29)
    ry=random.uniform(.07,.18)
    start=random.uniform(0,6.28)
    pts=[]
    for j in range(15):
        a=start+j*math.pi/7
        pts.append((cx+rx*math.cos(a),cy+ry*math.sin(a),
                    .795+i*.0015+.008*math.sin(a*2)))
    path(wires,'loop%d_'%i,pts,.0043,RED if i%2 else BLACK)
for i in range(5):
    x=-.12+i*.14
    line(wires,'probe grip'+str(i),(x,-.67,.828),(x+.21,-.72,.828),
         .012,RED if i%2 else BLACK)
    line(wires,'probe metal'+str(i),(x+.21,-.72,.828),(x+.30,-.735,.828),
         .003,(.48,.52,.46))
path(wires,'meter red',[(.51,.25,.86),(.55,.04,.79),(.67,-.22,.80),(.48,-.52,.82)],.005,RED)
path(wires,'meter black',[(.42,.25,.86),(.34,.12,.79),(.19,-.05,.79),(.22,-.39,.82)],.005,BLACK)
path(wires,'left cable',[(-.85,.05,.80),(-1.12,-.03,.80),(-1.20,-.24,.80),
    (-1.05,-.35,.81),(-.72,-.25,.82),(-.61,-.36,.83)],.009,BLACK)
scene.include('leads',wires)

realize(scene)
CAMERA_POSITION=(-.60,-3.25,2.68)
CAMERA_TARGET=(-.025,.14,1.23)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=50)
area_emitter((-.3,-1.1,3.6),power=135,size=2.0,target=(0,.1,.9))
area_emitter((1.0,.4,2.3),power=40,size=.9,target=(.2,-.2,.8))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.34,.38,.40,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.20
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.35
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
