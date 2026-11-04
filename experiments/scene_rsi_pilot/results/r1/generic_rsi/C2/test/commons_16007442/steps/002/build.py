from sceneact import *
import bpy, math, random
random.seed(19)

# Visible assemblies: bench, monitor, scope, supply, keyboard, two meters,
# lamp, drawer cabinets, pliers, solder station, calculator, papers and leads.
# Reference/render estimates: monitor top-left (.03,.11)/(.09,.19),
# monitor bottom-right (.35,.36)/(.37,.46), scope center (.33,.50)/(.35,.55),
# yellow meter center (.63,.51)/(.60,.52), keyboard (.30,.76)/(.34,.77).
# Largest isolated silhouette error: monitor is too short and insufficiently oblique.
# Correction family: monitor dimensions and orientation, anchored at its lower edge.
# Expected movement: upper edge rises, left edge extends left; desktop stays fixed.
# Preserve the yellow-meter/paper region and the foreground keyboard/lead coverage.
# Filled surfaces: desktop, instrument panels, drawer faces, papers and screen.
# True openings: lamp arms and separated plier handles. Hidden depths remain uncertain.

DESK_W, DESK_D, DESK_Z = 3.35, 1.9, .76
CAMERA = (-.25, -3.85, 3.38)
TARGET = (0, .27, 1.17)
LENS = 43
LIGHT_POWER = 170
scene = Scene('Electronics workbench')
wood=(.39,.235,.15)
black=(.018,.022,.022)
cream=(.62,.64,.56)
silver=(.48,.52,.51)
red=(.57,.025,.018)
yellow=(.94,.61,.025)
white=(.81,.80,.73)
blue=(.015,.32,.82)

def B(a,n,s,c,col):
    a.include(n,box(s,center=c,color=col))
def R(a,n,p,q,r,col):
    a.include(n,rod(r,start=p,end=q,color=col))
def S(a,n,pts,r,col):
    a.include(n,sweep_tube(points=pts,radius=r,color=col))
def asset(n):
    a=Asset(n)
    scene.include(n,a)
    return a
def sheet(a,n,x,y,z,w,h,angle=0,col=white):
    node=box((w,h,.003),center=(x,y,z),color=col)
    if angle:
        node.turn('z',angle)
    a.include(n,node)

desk=asset('workbench')
B(desk,'solid brown desktop',(DESK_W,DESK_D,.085),(0,0,DESK_Z-.044),wood)
B(desk,'front apron',(3.35,.07,.20),(0,-.91,.61),(.28,.16,.10))
wall=asset('back wall')
B(wall,'plaster',(4,.075,2.7),(0,1.015,1.65),(.53,.53,.46))
B(wall,'left wall',(.075,2,2.8),(-1.76,.1,1.6),(.34,.35,.30))

# Monitor display assembly is corrected independently of its supporting stand.
mon=asset('monitor')
display=Part('display')
mon.include('display',display)
cx,cy,cz=-1.04,.60,1.63
B(display,'rear body',(1.03,.105,.79),(cx,cy,cz),black)
B(display,'blue screen',(.93,.009,.666),(cx,cy-.058,cz+.018),(.025,.37,.87))
B(display,'screen top bar',(.93,.006,.045),(cx,cy-.065,cz+.328),(.01,.49,.98))
B(display,'screen taskbar',(.93,.007,.025),(cx,cy-.066,cz-.303),(.015,.19,.67))
for i in range(2):
    B(display,'desktop icon '+str(i),(.028,.006,.034),(cx+.02+i*.12,cy-.067,cz+.012),(.77,.82,.87))
    B(display,'icon red '+str(i),(.012,.007,.014),(cx+.026+i*.12,cy-.071,cz+.02),red)
    B(display,'icon caption '+str(i),(.074,.007,.006),(cx+.02+i*.12,cy-.069,cz-.021),(.65,.81,.95))
# Bottom stays at z=1.235. Taller panel fills the missing upper-left blue region.
display.resize((1.16,1,1.43),pivot=(cx,cy,1.235))
display.turn('z',24,pivot=(cx,cy,1.235))
display.move((-.12,0,0))
B(mon,'neck',(.09,.12,.44),(cx-.12,.65,1.03),black)
B(mon,'foot',(.49,.31,.045),(cx-.12,.53,.795),black)

scope=asset('oscilloscope')
sx,sy,sz=-.58,.38,1.015
B(scope,'housing',(.81,.40,.39),(sx,sy,sz),cream)
B(scope,'front panel',(.80,.024,.37),(sx,sy-.211,sz),(.72,.74,.65))
B(scope,'screen bezel',(.397,.022,.30),(sx-.171,sy-.230,sz+.006),(.26,.29,.26))
B(scope,'glass screen',(.34,.009,.245),(sx-.171,sy-.245,sz+.006),(.065,.105,.105))
for k in range(5):
    B(scope,'grid vertical '+str(k),(.001,.003,.232),(sx-.305+k*.067,sy-.251,sz+.006),(.12,.18,.17))
for k in range(4):
    B(scope,'grid horizontal '+str(k),(.326,.003,.001),(sx-.171,sy-.251,sz-.085+k*.059),(.12,.18,.17))
for ix in range(3):
    for iz in range(4):
        R(scope,'control knob %d %d'%(ix,iz),
          (sx+.094+ix*.089,sy-.232,sz-.121+iz*.076),
          (sx+.094+ix*.089,sy-.263,sz-.121+iz*.076),
          .021 if iz<3 else .014,(.63,.65,.59))
for i in range(5):
    B(scope,'upper control '+str(i),(.030,.007,.012),(sx+.06+i*.055,sy-.249,sz+.163),(.21,.25,.23))
for i,x in enumerate((sx-.29,sx+.29)):
    B(scope,'foot '+str(i),(.07,.14,.04),(x,sy,.805),black)

ps=asset('bench power supply')
B(ps,'body',(.36,.37,.30),(-1.27,.24,.93),(.44,.46,.39))
B(ps,'front',(.35,.018,.28),(-1.27,.046,.93),(.65,.65,.55))
B(ps,'upper dark display',(.27,.009,.095),(-1.27,.033,1.004),(.08,.11,.10))
for i in range(3):
    R(ps,'knob '+str(i),(-1.38+i*.10,.027,.877),(-1.38+i*.10,-.003,.877),.026,cream)
B(ps,'small device',(.27,.25,.13),(-1.27,.31,1.145),(.66,.68,.59))
B(ps,'small display',(.13,.008,.055),(-1.26,.178,1.155),(.1,.18,.16))

strip=asset('rear power strip')
B(strip,'case',(.55,.18,.12),(.19,.55,.847),black)
for i,col in enumerate((yellow,cream,cream,red,red)):
    R(strip,'socket '+str(i),(-.025+i*.103,.451,.849),(-.025+i*.103,.434,.849),.021,col)
board=asset('exposed circuit board')
B(board,'blue pcb',(.29,.20,.015),(-.86,.035,.786),(.025,.16,.34))
for i in range(9):
    x=-.97+(i%3)*.085
    y=-.026+(i//3)*.055
    B(board,'component '+str(i),(.040,.025,.018),(x,y,.802),black)
    if i%2==0:
        R(board,'capacitor '+str(i),(x+.022,y,.80),(x+.022,y,.833),.012,silver)

papers=asset('papers')
sheet(papers,'right notebook',.81,.30,.773,.65,.56,-13)
sheet(papers,'upper loose sheet',.59,.40,.778,.49,.41,-20)
for i in range(8):
    B(papers,'notebook ruling '+str(i),(.38,.0015,.001),(.89,.12+i*.033,.782),(.48,.51,.49))

meter=asset('yellow multimeter')
mx,my,mz=.40,.30,1.075
B(meter,'yellow protective shell',(.265,.085,.49),(mx,my,mz),yellow)
B(meter,'dark inset',(.218,.012,.421),(mx,my-.05,mz+.009),(.13,.16,.14))
B(meter,'lcd frame',(.19,.009,.115),(mx,my-.06,mz+.133),(.41,.45,.36))
B(meter,'lcd',(.164,.006,.075),(mx,my-.067,mz+.139),(.47,.56,.43))
R(meter,'rotary dial',(mx,my-.062,mz-.047),(mx,my-.084,mz-.047),.062,black)
B(meter,'dial pointer',(.012,.012,.06),(mx+.008,my-.095,mz-.032),(.59,.61,.53))
for i in range(4):
    B(meter,'button '+str(i),(.025,.015,.015),(mx-.075+i*.049,my-.07,mz+.055),cream)
for i,col in enumerate((black,black,red)):
    R(meter,'lead socket '+str(i),(mx-.072+i*.070,my-.061,mz-.183),(mx-.072+i*.070,my-.08,mz-.183),.015,col)
meter.turn('x',-12,pivot=(mx,my,mz))

kb=asset('keyboard')
kx,ky=-.61,-.47
B(kb,'keyboard tray',(1.19,.43,.047),(kx,ky,.799),black)
for row in range(5):
    for col in range(14):
        if row==0 and 3<=col<=8:
            continue
        B(kb,'key %d %d'%(row,col),(.062,.052,.013),
          (kx-.544+col*.080,ky-.166+row*.074,.830),(.055,.063,.060))
B(kb,'space bar',(.43,.051,.013),(kx-.106,ky-.166,.830),(.065,.07,.064))
for row in range(4):
    for col in range(3):
        B(kb,'numeric key %d %d'%(row,col),(.055,.052,.013),
          (kx+.385+col*.065,ky-.135+row*.073,.832),(.08,.085,.08))
kb.turn('z',13,pivot=(kx,ky,.8))

pm=asset('pocket meter')
B(pm,'case',(.22,.32,.065),(.22,-.30,.81),black)
B(pm,'yellow fascia',(.174,.257,.009),(.22,-.30,.849),(.71,.58,.09))
B(pm,'LCD',(.123,.068,.006),(.22,-.209,.858),(.51,.58,.43))
R(pm,'selector',(.22,-.32,.855),(.22,-.32,.875),.05,black)
pm.turn('z',-12)

calc=asset('calculator')
B(calc,'case',(.28,.46,.035),(-1.36,-.73,.802),(.12,.14,.13))
B(calc,'face',(.251,.408,.008),(-1.36,-.73,.824),(.66,.68,.61))
B(calc,'display',(.201,.092,.006),(-1.36,-.601,.832),(.29,.36,.28))
for j in range(5):
    for i in range(4):
        B(calc,'button %d %d'%(j,i),(.039,.038,.009),(-1.443+i*.056,-.70-j*.052,.834),(.16,.19,.17))
calc.turn('z',12)

drawers=asset('component cabinets')
for bank,x,w,cols,rows in [(0,.18,.88,4,3),(1,1.26,1.15,5,6)]:
    zbase=2.06 if bank==0 else 1.82
    h=.56 if bank==0 else 1.02
    B(drawers,'cabinet '+str(bank),(w,.22,h),(x,.883,zbase+h/2),(.055,.066,.06))
    for j in range(rows):
        for i in range(cols):
            xx=x-w/2+(i+.5)*w/cols
            zz=zbase+(j+.5)*h/rows
            B(drawers,'drawer %d %d %d'%(bank,j,i),(w/cols-.018,.018,h/rows-.018),
              (xx,.757,zz),(.18,.205,.18))
            B(drawers,'label %d %d %d'%(bank,j,i),(.078,.008,.025),(xx,.743,zz-.026),(.62,.64,.56))
            B(drawers,'handle %d %d %d'%(bank,j,i),(.071,.017,.014),(xx,.731,zz+.018),(.08,.09,.08))
for i in range(3):
    B(wall,'wall paper '+str(i),(.48,.007,.32),(-.02+i*.48,.963,1.665),(.79,.79,.71))
    for j in range(4):
        B(wall,'diagram line %d %d'%(i,j),(.28,.003,.001),(-.02+i*.48,.955,1.60+j*.041),(.57,.59,.53))

tools=asset('hanging pliers')
for idx,(x,z) in enumerate([(-.48,1.64),(-.30,1.59),(-.05,1.59)]):
    R(tools,'steel jaws '+str(idx),(x,.88,z),(x-.008,.88,z+.18),.015,(.26,.29,.27))
    S(tools,'left red handle '+str(idx),[(x,.88,z+.015),(x-.045,.88,z-.06),(x-.055,.88,z-.16)],.014,red)
    S(tools,'right red handle '+str(idx),[(x,.88,z+.015),(x+.04,.88,z-.063),(x+.03,.88,z-.16)],.014,red)

lamp=asset('task lamp')
R(lamp,'rear vertical support',(1.15,.67,.78),(1.15,.67,1.81),.019,black)
R(lamp,'upper diagonal arm',(1.15,.67,1.81),(.88,.67,1.94),.023,black)
R(lamp,'parallel arm',(1.20,.69,.88),(1.20,.69,1.82),.012,silver)
B(lamp,'long black shade',(.99,.27,.105),(.56,.60,1.985),(.015,.018,.016))
R(lamp,'rounded shade end',(.98,.48,1.985),(.98,.72,1.985),.060,black)
B(lamp,'shade underside',(.81,.20,.008),(.49,.60,1.928),(.43,.45,.39))
B(lamp,'shade highlight',(.075,.16,.004),(.105,.60,2.04),(.65,.67,.61))
S(lamp,'hanging electrical cable',[(1.17,.65,1.86),(1.27,.62,1.55),(1.21,.53,1.10),(1.34,.30,.79)],.009,black)

solder=asset('soldering equipment')
B(solder,'station',(.37,.34,.17),(1.16,.44,.855),(.20,.28,.26))
B(solder,'station front',(.35,.018,.14),(1.16,.26,.86),(.08,.12,.11))
R(solder,'temperature knob',(1.10,.244,.86),(1.10,.225,.86),.033,black)
B(solder,'switch',(.03,.012,.04),(1.26,.239,.87),red)
B(solder,'iron stand base',(.34,.32,.035),(1.43,.16,.79),(.22,.17,.11))
R(solder,'iron handle',(1.35,.13,.86),(1.49,.42,1.02),.038,(.06,.25,.25))
R(solder,'iron shaft',(1.35,.13,.86),(1.24,-.09,.80),.012,silver)
for i in range(6):
    R(solder,'holder coil '+str(i),(1.40+i*.012,.25+i*.024,.87+i*.014),
      (1.46+i*.012,.25+i*.024,.92+i*.014),.009,silver)
for i,(x,y,h) in enumerate([(1.02,.70,.30),(1.25,.72,.25),(1.54,.59,.37)]):
    R(solder,'can '+str(i),(x,y,.78),(x,y,.78+h),.059,(.46,.49,.45))
    R(solder,'can lid '+str(i),(x,y,.78+h),(x,y,.788+h),.064,silver)
    B(solder,'can label '+str(i),(.084,.007,.105),(x,y-.059,.87),(.57,.61,.56))

bottle=asset('water bottle')
R(bottle,'body',(1.56,.84,.81),(1.56,.84,1.15),.072,(.29,.35,.31))
R(bottle,'neck',(1.56,.84,1.15),(1.56,.84,1.26),.031,(.47,.53,.47))
R(bottle,'blue cap',(1.56,.84,1.26),(1.56,.84,1.30),.036,(.04,.12,.27))

cables=asset('loose electrical leads')
paths=[
([(.35,.24,.81),(.45,-.02,.79),(.61,-.39,.79),(.45,-.70,.79),(-.01,-.78,.79),(-.32,-.58,.79),(-.21,-.36,.79),(.10,-.39,.79)],red),
([(.42,.22,.80),(.73,-.05,.79),(.82,-.41,.79),(.67,-.76,.79),(.29,-.87,.79),(-.09,-.79,.79),(-.18,-.57,.79),(.18,-.52,.79)],black),
([(.21,-.44,.84),(-.04,-.48,.80),(-.36,-.44,.79),(-.39,-.63,.79),(-.16,-.71,.79),(.26,-.64,.79),(.41,-.46,.79),(.15,-.34,.79)],red),
([(-.65,-.04,.80),(-.79,-.17,.80),(-.55,-.37,.80),(-.28,-.32,.80),(-.23,-.53,.80),(.06,-.60,.80),(.45,-.54,.80),(.74,-.62,.80)],black),
([(.13,-.40,.82),(.46,-.48,.82),(.67,-.31,.79),(.62,-.11,.79),(.82,-.04,.79),(1.01,-.23,.79),(.79,-.51,.79)],red),
([(-.92,-.30,.80),(-.65,-.48,.80),(-.70,-.76,.79),(-.57,-.91,.79),(-.23,-.94,.79),(.02,-.82,.79)],black),
([(1.11,.25,.80),(1.00,.04,.80),(1.17,-.13,.79),(1.37,-.18,.80),(1.45,-.03,.81)],black)
]
for i,(pts,col) in enumerate(paths):
    S(cables,'lead '+str(i),pts,.008,col)
for i in range(3):
    x=.10+i*.23
    R(cables,'foreground probe '+str(i),(x,-.88,.806),(x+.37,-.93,.806),.014,black if i!=1 else red)
    R(cables,'probe steel tip '+str(i),(x-.13,-.86,.806),(x,-.88,.806),.005,silver)
for i in range(3):
    x=.62+i*.10
    R(cables,'clip lead '+str(i),(x,-.28,.80),(x+.14,-.15,.80),.013,(red,blue,yellow)[i])
    R(cables,'metal clip '+str(i),(x+.14,-.15,.80),(x+.20,-.10,.80),.007,silver)

clutter=asset('desk clutter')
R(clutter,'solder spool',(-.36,-.68,.781),(-.36,-.68,.81),.064,(.65,.67,.57))
R(clutter,'spool inset',(-.36,-.68,.812),(-.36,-.68,.818),.039,(.22,.40,.32))
R(clutter,'spool central hole',(-.36,-.68,.819),(-.36,-.68,.823),.013,black)
for i in range(9):
    x=.88+random.uniform(-.08,.31)
    y=-.40-random.random()*.45
    sheet(clutter,'yellow sticky scrap '+str(i),x,y,.78,.10,.045,random.uniform(-35,35),(.90,.66,.11))
sheet(clutter,'small receipt',1.20,-.19,.783,.13,.24,-16)
B(clutter,'right tool package',(.42,.67,.025),(1.48,-.68,.79),(.19,.22,.22))
for i in range(7):
    R(clutter,'packaged screwdriver '+str(i),(1.32+i*.050,-.94,.814),
      (1.37+i*.050,-.48,.814),.009,silver)
    R(clutter,'red packaged handle '+str(i),(1.37+i*.050,-.48,.814),
      (1.39+i*.050,-.32,.814),.019,(.39,.025,.015))
sheet(clutter,'blue package header',1.48,-.28,.82,.42,.15,0,(.035,.20,.42))
R(clutter,'right magnifier handle',(1.46,-.08,.80),(1.59,-.20,.82),.018,black)
R(clutter,'metal dish',(1.57,-.03,.79),(1.57,-.03,.83),.13,(.21,.25,.23))

# All dimensions/radii are positive; all tube paths have distinct consecutive points.
# Unique include keys preserve editable assemblies. Camera and lights follow realize.
realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.37,.40,.41,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-.7,-1.4,3.5),power=LIGHT_POWER,size=2.7,target=(0,.1,.8))
area_emitter((1.1,.5,2.5),power=45,size=1.2,target=(.3,0,.8),color=(1,.91,.74))

for obj in bpy.data.objects:
    if obj.type!='MESH':
        continue
    for slot in obj.material_slots:
        mat=slot.material
        if mat is None:
            continue
        mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF')
        if p:
            p.inputs['Roughness'].default_value=.63
        parent=obj.parent
        in_monitor=False
        while parent:
            if parent.name=='monitor':
                in_monitor=True
                break
            parent=parent.parent
        if in_monitor and p:
            col=p.inputs['Base Color'].default_value
            if col[2]>.5 and col[0]<.1:
                p.inputs['Emission Color'].default_value=col
                p.inputs['Emission Strength'].default_value=.45

for obj in bpy.data.objects:
    if obj.type=='MESH' and obj.parent and obj.parent.name=='solid brown desktop':
        if obj.active_material:
            mat=obj.active_material.copy()
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            nt=mat.node_tree
            p=nt.nodes.get('Principled BSDF')
            noise=nt.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=125
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.12
            bump.inputs['Distance'].default_value=.008
            nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
sc.view_settings.view_transform='Standard'
sc.view_settings.look='Medium High Contrast'
sc.view_settings.exposure=0
sc.view_settings.gamma=1
