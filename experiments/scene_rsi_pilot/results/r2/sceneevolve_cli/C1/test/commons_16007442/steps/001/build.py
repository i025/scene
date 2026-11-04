from sceneact import *
import bpy, math, random
random.seed(18)

# Monitor occupies upper left: approximately (.03,.03)-(.36,.46).
# Desk fills the bottom half, with a warm brown surface.
# Oscilloscope sits at (.21,.42)-(.45,.59); yellow meter at (.58,.40)-(.68,.62).
# Keyboard extends diagonally across the lower left.
# Black task lamp spans (.49,.17)-(.87,.30), above the instruments.
# Small-parts drawers cover the upper right wall; tangled leads fill foreground center.

scene = Scene('Electronics workbench')
WOOD=(.34,.18,.105); BLACK=(.018,.022,.021); GREY=(.47,.48,.43)
CREAM=(.68,.69,.59); RED=(.55,.025,.018); YELLOW=(.93,.62,.025)
def put(parent,name,size,pos,color):
    parent.include(name,box(size,center=pos,color=color))
def line(parent,name,a,b,r,color):
    parent.include(name,rod(r,start=a,end=b,color=color))
def path(parent,name,points,r,color):
    for i in range(len(points)-1):
        line(parent,name+str(i),points[i],points[i+1],r,color)
def knob(parent,name,x,y,z,r=.014,color=GREY):
    line(parent,name,(x,y,z),(x,y-.019,z),r,color)

room=Asset('Room and bench')
put(room,'back wall',(3.4,.08,2.5),(0,.88,1.35),(.64,.65,.60))
put(room,'left wall',(.07,2.4,2.5),(-1.29,-.25,1.35),(.43,.44,.39))
put(room,'desktop',(2.62,1.68,.085),(0,-.03,.73),WOOD)
put(room,'back trim',(2.62,.045,.08),(0,.78,.80),(.25,.16,.10))
scene.include('architecture',room)

monitor=Asset('Computer display')
put(monitor,'foot',(.39,.25,.025),(-.88,.40,.79),BLACK)
line(monitor,'stand',(-.88,.47,.80),(-.88,.49,1.17),.037,BLACK)
put(monitor,'bezel',(.77,.065,.62),(-.88,.47,1.49),(.012,.015,.016))
put(monitor,'blue display',(.706,.008,.536),(-.88,.432,1.51),(.025,.34,.72))
put(monitor,'desktop blue',(.704,.005,.468),(-.88,.425,1.525),(.13,.49,.77))
put(monitor,'taskbar',(.704,.006,.025),(-.88,.42,1.264),(.025,.18,.60))
for i,c in enumerate(((.8,.18,.06),(.20,.6,.2),(.05,.35,.8),(.9,.65,.1))):
    put(monitor,'logo'+str(i),(.018,.003,.018),(-.90+(i%2)*.023,.42,1.52-(i//2)*.023),c)
monitor.turn('z',-12,pivot=(-.88,.47,1.49))
scene.include('monitor',monitor)

scope=Asset('Oscilloscope')
put(scope,'body',(.58,.34,.30),(-.43,.39,.97),CREAM)
put(scope,'face',(.575,.013,.285),(-.43,.212,.97),(.72,.73,.64))
put(scope,'screen bezel',(.285,.019,.235),(-.555,.198,.975),(.27,.30,.28))
put(scope,'screen',(.247,.006,.190),(-.555,.185,.975),(.045,.075,.071))
for col in range(4):
    for row in range(3):
        knob(scope,'dial%d_%d'%(col,row),-.365+col*.057,.19,.888+row*.069,
             .017 if col>1 else .012,(.55,.57,.51))
for j in range(5):
    put(scope,'button'+str(j),(.024,.014,.011),(-.36+j*.042,.19,1.085),(.38,.41,.37))
scene.include('scope',scope)

supply=Asset('Bench power supply')
put(supply,'case',(.28,.27,.30),(-.94,.18,.955),(.54,.56,.49))
put(supply,'front',(.27,.015,.28),(-.94,.037,.955),(.62,.64,.55))
put(supply,'display',(.21,.01,.078),(-.94,.025,1.018),(.065,.10,.085))
for i in range(3):
    knob(supply,'knob'+str(i),-1.02+.08*i,.019,.90,.025,(.54,.56,.50))
put(supply,'label',(.16,.01,.025),(-.95,.024,1.10),(.80,.77,.53))
scene.include('supply',supply)

unit=Asset('Black instrument')
put(unit,'body',(.40,.25,.16),(.12,.45,.88),(.025,.032,.033))
put(unit,'top',(.39,.24,.012),(.12,.45,.969),(.17,.20,.21))
for i,c in enumerate((YELLOW,BLACK,(.65,.67,.63),RED)):
    knob(unit,'socket'+str(i),-.015+.09*i,.315,.86,.017,c)
path(unit,'headphone lead',[(.02,.43,1.0),(-.01,.47,1.07),(.08,.53,1.09),(.19,.49,1.04)],.013,BLACK)
scene.include('instrument',unit)

meter=Asset('Upright yellow multimeter')
put(meter,'rubber case',(.205,.065,.36),(.45,.32,1.005),YELLOW)
put(meter,'dark face',(.173,.012,.31),(.45,.28,1.01),(.09,.12,.12))
put(meter,'lcd',(.14,.008,.075),(.45,.27,1.111),(.46,.52,.43))
put(meter,'lcd shadow',(.09,.004,.009),(.45,.264,1.106),(.19,.26,.21))
knob(meter,'selector',.45,.263,.973,.047,BLACK)
for i in range(3):
    knob(meter,'jack'+str(i),.398+i*.05,.262,.865,.013,RED if i==2 else BLACK)
meter.turn('x',-12,pivot=(.45,.32,.84))
scene.include('yellow meter',meter)

keyboard=Asset('Keyboard')
put(keyboard,'base',(.87,.33,.035),(-.48,-.36,.80),(.026,.031,.030))
for row in range(5):
    for col in range(13):
        put(keyboard,'key%d_%d'%(row,col),(.043,.039,.018),
            (-.867+col*.059,-.484+row*.052,.826),(.045,.052,.052))
put(keyboard,'space',(.26,.037,.019),(-.56,-.49,.828),BLACK)
keyboard.turn('z',14,pivot=(-.48,-.36,.80))
scene.include('keyboard',keyboard)

mouse=Asset('Mouse')
mouse.include('body',ball(.066,center=(.39,-.05,.814),color=(.48,.49,.45)))
mouse.members['body'].resize((.72,1.22,.60))
path(mouse,'cord',[(.39,-.01,.82),(.38,.07,.79),(.29,.13,.78),(.15,.11,.78),(.12,.17,.78)],.006,BLACK)
scene.include('mouse',mouse)

hand=Asset('Small handheld meter')
put(hand,'body',(.14,.23,.033),(.32,-.25,.807),(.025,.03,.027))
put(hand,'screen',(.095,.052,.006),(.32,-.19,.828),(.45,.53,.43))
line(hand,'dial',(.32,-.28,.826),(.32,-.28,.842),.035,YELLOW)
put(hand,'yellow button',(.025,.023,.008),(.28,-.23,.83),YELLOW)
hand.turn('z',-16)
scene.include('small meter',hand)

calc=Asset('Calculator')
put(calc,'case',(.19,.31,.034),(-1.04,-.62,.805),(.13,.15,.15))
put(calc,'lcd',(.15,.064,.008),(-1.04,-.527,.827),(.43,.51,.44))
for row in range(5):
    for col in range(4):
        put(calc,'key%d%d'%(row,col),(.03,.028,.009),(-1.10+col*.04,-.735+row*.035,.828),(.56,.58,.54))
calc.turn('z',-13)
scene.include('calculator',calc)

drawers=Asset('Parts organizer on wall')
for cabinet,(cx,width,ncols) in enumerate(((.98,.94,6),(.06,.62,4))):
    put(drawers,'frame'+str(cabinet),(width,.16,.53),(cx,.79,1.91),(.055,.065,.06))
    for row in range(5):
        for col in range(ncols):
            x=cx-width/2+.026+(col+.5)*(width-.045)/ncols
            z=1.68+row*.099
            w=(width-.045)/ncols-.009
            put(drawers,'drawer%d_%d_%d'%(cabinet,row,col),(w,.021,.080),(x,.696,z),(.19,.22,.20))
            put(drawers,'label%d_%d_%d'%(cabinet,row,col),(w*.59,.005,.021),(x,.682,z-.015),(.64,.65,.58))
scene.include('drawers',drawers)

papers=Asset('Wall paper and hanging tools')
for i in range(3):
    put(papers,'sheet'+str(i),(.35,.008,.27),(-.13+i*.36,.818,1.42),(.79,.79,.72))
for k,x in enumerate((-.51,-.37,-.19)):
    z=1.38+(.04 if k==1 else 0)
    path(papers,'left grip'+str(k),[(x-.025,.76,z+.08),(x-.035,.751,z-.035),(x-.066,.75,z-.12),(x-.055,.75,z-.18)],.012,RED)
    path(papers,'right grip'+str(k),[(x+.015,.76,z+.09),(x+.025,.751,z-.035),(x+.060,.75,z-.12),(x+.045,.75,z-.18)],.012,RED)
    line(papers,'jaw'+str(k),(x-.018,.76,z+.035),(x,.76,z+.15),.014,(.17,.18,.16))
scene.include('wall details',papers)

lamp=Asset('Long black task lamp')
put(lamp,'base',(.19,.17,.035),(1.02,.38,.80),BLACK)
path(lamp,'upright',[(1.02,.4,.81),(1.03,.47,1.33),(.98,.47,1.62)],.015,(.035,.04,.037))
line(lamp,'arm',(.98,.47,1.62),(.67,.43,1.68),.025,BLACK)
put(lamp,'long shade',(.79,.20,.072),(.42,.43,1.68),(.012,.017,.016))
put(lamp,'shade underside',(.67,.15,.008),(.39,.43,1.639),(.66,.68,.60))
lamp.members['long shade'].turn('z',-8)
scene.include('lamp',lamp)

station=Asset('Soldering station')
put(station,'box',(.27,.25,.13),(.91,.32,.86),(.19,.23,.21))
put(station,'panel',(.25,.012,.11),(.91,.188,.86),(.055,.065,.061))
knob(station,'control',.94,.176,.86,.035,BLACK)
line(station,'iron grip',(.96,.20,.97),(1.10,.38,1.10),.028,(.09,.30,.31))
line(station,'iron tip',(.96,.20,.97),(.82,.04,.84),.009,(.43,.47,.46))
path(station,'cord',[(1.10,.38,1.10),(1.18,.36,1.05),(1.22,.17,.82),(1.15,-.05,.79),(.94,-.12,.79)],.011,BLACK)
scene.include('soldering station',station)

misc=Asset('Workbench clutter')
for i in range(2):
    x=.74+i*.13
    line(misc,'can'+str(i),(x,.58,.78),(x,.58,1.02-i*.025),.047,(.49,.53,.51))
    line(misc,'can top'+str(i),(x,.58,1.019-i*.025),(x,.58,1.03-i*.025),.038,(.24,.27,.26))
line(misc,'bottle', (1.18,.66,.79),(1.18,.66,1.13),.057,(.38,.44,.41))
line(misc,'bottle neck',(1.18,.66,1.13),(1.18,.66,1.21),.023,(.53,.58,.55))
line(misc,'cap',(1.18,.66,1.21),(1.18,.66,1.24),.025,(.12,.14,.27))
put(misc,'circuit board',(.24,.17,.018),(-.67,.015,.80),(.025,.13,.29))
for i in range(5):
    put(misc,'board component'+str(i),(.026,.035,.021),(-.75+i*.038,.015,.82),(.16,.18,.17))
put(misc,'paper on desk',(.35,.34,.005),(.79,.04,.79),(.81,.80,.73))
for i in range(9):
    x=random.uniform(.64,1.04); y=random.uniform(-.73,-.35)
    note=box((.065,.046,.003),center=(x,y,.789),color=(.96,.72,.10))
    note.turn('z',random.uniform(-30,30))
    misc.include('sticky note'+str(i),note)
line(misc,'solder reel',(-.38,-.59,.785),(-.38,-.59,.817),.046,(.53,.61,.56))
line(misc,'reel center',(-.38,-.59,.817),(-.38,-.59,.82),.018,(.25,.22,.18))
put(misc,'right tool package',(.22,.40,.018),(1.13,-.57,.79),(.13,.18,.27))
for i in range(6):
    line(misc,'precision tool'+str(i),(1.045+i*.031,-.72,.814),(1.045+i*.031,-.43,.814),.007,(.32,.34,.34))
scene.include('clutter',misc)

wires=Asset('Tangled test leads')
for i in range(16):
    cx=random.uniform(-.18,.62); cy=random.uniform(-.59,-.15)
    rx=random.uniform(.12,.29); ry=random.uniform(.07,.18)
    start=random.uniform(0,6.28)
    pts=[]
    for j in range(9):
        a=start+j*math.pi/4
        pts.append((cx+rx*math.cos(a),cy+ry*math.sin(a),.793+i*.0016))
    path(wires,'loop%d_'%i,pts,.0045,RED if i%3 else BLACK)
for i in range(5):
    x=-.12+i*.14
    line(wires,'probe grip'+str(i),(x,-.67,.818),(x+.21,-.72,.818),.012,RED if i%2 else BLACK)
    line(wires,'probe metal'+str(i),(x+.21,-.72,.818),(x+.30,-.735,.818),.003,(.56,.58,.54))
path(wires,'meter red',[(.51,.25,.86),(.55,.04,.79),(.67,-.22,.80),(.48,-.52,.81)],.005,RED)
path(wires,'meter black',[(.42,.25,.86),(.34,.12,.79),(.19,-.05,.79),(.22,-.39,.81)],.005,BLACK)
scene.include('leads',wires)

realize(scene)
CAMERA_POSITION=(.65,-3.25,2.68)
CAMERA_TARGET=(0,.12,1.21)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=44)
area_emitter((-.3,-1.1,3.6),power=190,size=2.3,target=(0,.1,.9))
area_emitter((1.0,.4,2.3),power=65,size=1.1,target=(.2,-.2,.8))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.39,.43,.47,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.28
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
sc.render.resolution_x=512
sc.render.resolution_y=388
sc.render.resolution_percentage=100
