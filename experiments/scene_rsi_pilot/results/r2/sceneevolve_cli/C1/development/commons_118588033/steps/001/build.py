from sceneact import *
import bpy, math

# Reference anchors: main column at (0.73, 0.49), extending nearly full height.
# Left bunks occupy (0.00, 0.38) to (0.42, 0.84).
# Rear lockers occupy (0.42, 0.38) to (0.65, 0.61).
# Rear floor boundary is near y=0.68; foreground floor fills lower third.
# Ceiling lamps lie near (0.39, 0.16) and (0.47, 0.29).
# Right bench enters at (0.82, 0.76); red wall fixture is near (0.81, 0.55).

scene = Scene('Ship accommodation')
cream = (.63,.62,.48)
wall = (.67,.68,.58)
ivory = (.79,.79,.67)
brown = (.24,.075,.035)
floorcolor = (.35,.12,.065)
steel = (.39,.43,.40)
dark = (.055,.075,.068)
blue = (.075,.14,.16)
white = (.72,.73,.66)

def cube(parent, name, size, pos, color):
    parent.include(name, box(size, center=pos, color=color))

def tube(parent, name, a, b, radius=.025, color=dark):
    parent.include(name, rod(radius, start=a, end=b, color=color))

architecture = Asset('Painted steel compartment')
cube(architecture,'deck',(5.2,11,.13),(0,0,-.07),floorcolor)
cube(architecture,'port bulkhead',(.14,10,3.45),(-2.08,.2,1.72),wall)
cube(architecture,'starboard bulkhead',(.14,7.1,3.45),(2.08,1.8,1.72),wall)
cube(architecture,'rear bulkhead',(4.2,.16,3.45),(0,4.55,1.72),wall)
cube(architecture,'overhead',(4.3,10,.13),(0,.2,3.48),cream)
cube(architecture,'port skirting',(.045,9,.29),(-1.99,.1,.145),brown)
cube(architecture,'starboard skirting',(.045,7,.30),(1.99,1.8,.15),brown)
cube(architecture,'rear skirting',(4.05,.035,.30),(0,4.44,.15),brown)
for i,y in enumerate([-2.6,-.4,1.7,3.9]):
    cube(architecture,f'overhead transverse beam {i}',(4.1,.17,.25),(0,y,3.22),(.48,.32,.17))
for i,x in enumerate([-1.4,-.65,.2,1.1]):
    cube(architecture,f'ceiling longitudinal rib {i}',(.075,8.7,.12),(x,.3,3.32),(.63,.48,.29))
# Prominent cylindrical support, ochre above and reddish brown below.
tube(architecture,'column lower',(1.07,-.62,.03),(1.07,-.62,1.44),.125,brown)
tube(architecture,'column upper',(1.07,-.62,1.44),(1.07,-.62,3.49),.125,(.68,.48,.24))
tube(architecture,'column foot',(1.07,-.62,.015),(1.07,-.62,.065),.155,(.35,.17,.09))
# A cropped post at the extreme right.
cube(architecture,'foreground right jamb',(.20,.20,3.6),(1.68,-2.30,1.8),brown)
scene.include('architecture',architecture)

bunks = Asset('Three tier port berths')
for j,y in enumerate([.20,2.42]):
    for k,z in enumerate([.54,1.18,1.83]):
        cube(bunks,f'bed frame {j} {k}',(.91,2.12,.085),(-1.49,y,z),dark)
        cube(bunks,f'mattress {j} {k}',(.85,2.02,.135),(-1.49,y,z+.10),(.69,.71,.65))
        cube(bunks,f'pillow {j} {k}',(.66,.39,.15),(-1.49,y+.72,z+.22),(.78,.78,.71))
        cube(bunks,f'blanket fold {j} {k}',(.85,.43,.04),(-1.49,y-.60,z+.18),(.54,.60,.56))
for i,y in enumerate([- .87,1.28,3.49]):
    for h,x in enumerate([-1.98,-1.00]):
        tube(bunks,f'upright {i} {h}',(x,y,.04),(x,y,2.43),.027,dark)
    tube(bunks,f'upper cross {i}',(-1.98,y,2.22),(-1.0,y,2.22),.025,dark)
for k,z in enumerate([.46,1.10,1.75,2.26]):
    tube(bunks,f'long rail {k}',(-1.00,-.87,z),(-1.00,3.49,z),.022,dark)
scene.include('berths',bunks)

equipment = Asset('Port foreground ventilated cabinets')
for i,y in enumerate([-1.28,-.54]):
    cube(equipment,f'cabinet {i}',(.61,.65,.83),(-1.72,y,1.01),blue)
    cube(equipment,f'cabinet top {i}',(.68,.70,.045),(-1.72,y,1.45),(.12,.19,.19))
    for k in range(14):
        cube(equipment,f'louver {i} {k}',(.018,.48,.018),(-1.402,y,.66+k*.049),(.27,.33,.31))
    cube(equipment,f'edge upright {i}',(.04,.04,.78),(-1.38,y-.29,1.02),(.10,.14,.15))
cube(equipment,'long low green bench',(.53,3.6,.08),(-1.66,-.52,.41),(.055,.13,.12))
for i,y in enumerate([-2.05,.84]):
    tube(equipment,f'bench leg {i}',(-1.46,y,.05),(-1.46,y,.40),.025,dark)
scene.include('foreground cabinets',equipment)

lockers = Asset('Rear gray lockers')
for i,x in enumerate([-.62,-.12,.38]):
    cube(lockers,f'locker body {i}',(.48,.59,1.64),(x,3.70,1.18),(.43,.47,.44))
    cube(lockers,f'locker door {i}',(.445,.027,1.51),(x,3.386,1.19),(.51,.54,.50))
    cube(lockers,f'door seam {i}',(.012,.02,1.52),(x+.226,3.365,1.19),(.22,.27,.25))
    for j,z in enumerate([.75,1.61]):
        for k in range(4):
            cube(lockers,f'vent {i} {j} {k}',(.21,.018,.013),(x,3.365,z+k*.055),(.28,.33,.31))
    cube(lockers,f'handle {i}',(.025,.04,.13),(x+.145,3.34,1.19),(.17,.20,.18))
    for k in [0,1]:
        cube(lockers,f'hinge {i} {k}',(.025,.028,.07),(x-.20,3.35,.70+k*.9),(.63,.63,.55))
    cube(lockers,f'top baggage {i}',(.32,.34,.16),(x,3.69,2.08),(.27,.31,.28))
scene.include('lockers',lockers)

chair = Asset('Small rear chair')
cx,cy=-.31,2.20
cube(chair,'seat',(.48,.46,.065),(cx,cy,.47),(.34,.31,.21))
cube(chair,'back',(.46,.065,.39),(cx,cy+.21,.82),(.47,.47,.36))
for i,x in enumerate([cx-.22,cx+.22]):
    for j,y in enumerate([cy-.19,cy+.19]):
        tube(chair,f'leg {i} {j}',(x,y,.02),(x,y,.47),.021,(.57,.59,.52))
    tube(chair,f'back frame {i}',(x,cy+.21,.44),(x,cy+.21,1.06),.023,(.57,.59,.52))
    tube(chair,f'arm {i}',(x,cy-.16,.70),(x,cy+.21,.70),.022,(.57,.59,.52))
scene.include('chair',chair)

machine = Asset('Rear utility unit')
cube(machine,'metal base',(.69,.68,.88),(.69,2.35,.46),(.25,.29,.27))
cube(machine,'top plate',(.78,.76,.07),(.69,2.35,.94),(.34,.37,.32))
cube(machine,'front inset',(.55,.025,.62),(.69,1.995,.49),(.29,.32,.29))
tube(machine,'vertical valve riser',(.70,2.35,.95),(.70,2.35,1.65),.045,(.26,.28,.22))
tube(machine,'valve cross',(.48,2.35,1.43),(.91,2.35,1.43),.027,(.31,.28,.15))
scene.include('utility machine',machine)

pipes = Asset('Exposed ship services')
for i,x in enumerate([-.86,.25,.62]):
    tube(pipes,f'rear dark upright {i}',(x,4.1,.9),(x,4.1,3.15),.043,dark)
    tube(pipes,f'overhead dark run {i}',(x,-1.5,3.13),(x,4.1,3.13),.043,dark)
for i,(x,z) in enumerate([(-1.87,2.62),(-1.65,2.95),(.91,3.25)]):
    tube(pipes,f'long ivory pipe {i}',(x,-3.6,z),(x,4.1,z),.052,ivory)
for i,y in enumerate([-2.0,-.2,1.6,3.4]):
    tube(pipes,f'pipe suspension {i}',(-1.65,y,2.95),(-1.65,y,3.40),.022,ivory)
tube(pipes,'left descending bent pipe',(-1.87,1.0,2.62),(-1.87,1.0,2.30),.055,ivory)
tube(pipes,'rear horizontal pipe',(-1.87,4.04,2.73),(1.85,4.04,2.73),.05,ivory)
scene.include('pipes',pipes)

details = Asset('Bulkhead fittings')
# Pale ventilation heater high on left wall.
cube(details,'vent casing',(.20,.69,.69),(-1.92,-.83,2.30),(.68,.68,.57))
cube(details,'vent black recess',(.018,.53,.45),(-1.805,-.83,2.28),(.065,.08,.075))
for i in range(6):
    cube(details,f'vent grille {i}',(.04,.53,.032),(-1.78,-.83,2.08+i*.076),(.67,.68,.59))
# Gray rectangular board on right wall.
cube(details,'notice board',(.045,1.12,.84),(1.977,2.00,1.97),(.27,.32,.30))
for i,y in enumerate([1.43,2.57]):
    cube(details,f'board side {i}',(.06,.035,.88),(1.94,y,1.97),(.43,.43,.35))
# Wall-mounted red emergency apparatus.
cube(details,'red fixture back',(.10,.44,.66),(1.92,.40,1.18),(.65,.035,.018))
tube(details,'red cylinder',(1.82,.40,.92),(1.82,.40,1.38),.13,(.76,.045,.02))
cube(details,'fixture pale label',(.025,.12,.15),(1.68,.40,1.16),(.84,.72,.48))
tube(details,'fixture handle',(1.80,.29,1.45),(1.80,.49,1.45),.03,(.60,.025,.012))
cube(details,'paper notice',(.02,.40,.57),(1.986,3.25,1.56),(.79,.79,.70))
for k in range(4):
    cube(details,f'notice text {k}',(.025,.26,.012),(1.969,3.25,1.70-k*.07),(.40,.42,.37))
# Foreground right green bench.
cube(details,'right bench',(.60,2.25,.075),(1.72,-1.75,.47),(.045,.13,.105))
for i,y in enumerate([-2.66,-.85]):
    tube(details,f'right bench leg {i}',(1.49,y,.02),(1.49,y,.45),.027,dark)
scene.include('details',details)

lamps = Asset('Pendant lamps')
for i,(x,y,z,r) in enumerate([(-.66,-1.0,2.98,.30),(-.40,1.65,2.92,.20),(-.2,3.35,2.9,.17)]):
    tube(lamps,f'stem {i}',(x,y,z+.07),(x,y,3.42),.022,dark)
    tube(lamps,f'shade {i}',(x,y,z),(x,y,z+.065),r,(.22,.25,.23))
    tube(lamps,f'white underside {i}',(x,y,z-.013),(x,y,z-.001),r*.87,(.95,.96,.88))
scene.include('lamps',lamps)

realize(scene)
set_view((.05,-4.55,1.64),(-.15,2.7,1.69),lens=29,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.34,.36,.30,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.38
area_emitter((-.65,-1.0,2.89),power=160,size=.65,target=(-.6,-.7,.1),color=(1,.91,.73))
area_emitter((-.40,1.65,2.83),power=130,size=.55,target=(-.4,1.7,.1),color=(.87,.94,1))
area_emitter((0,-3.4,2.7),power=100,size=2.4,target=(0,1,1.1),color=(1,.83,.62))
area_emitter((.6,3.5,2.9),power=80,size=1.0,target=(0,2.1,.7))
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.25
