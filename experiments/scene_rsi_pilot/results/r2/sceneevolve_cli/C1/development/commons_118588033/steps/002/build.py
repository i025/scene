from sceneact import *
import bpy, math

# The first render is too bright; darken the deck and reduce ambient illumination.
# The column is too far right; shift it left and face the right-wall fittings toward the camera.
# Foreground bunks obscure too much of the left side; retain the deeper berths and raise rear lockers.

scene = Scene('Ship accommodation')
cream=(.52,.49,.36)
wall=(.57,.59,.49)
ivory=(.70,.71,.59)
brown=(.22,.055,.025)
floorcolor=(.25,.065,.027)
steel=(.35,.39,.36)
dark=(.035,.055,.049)
blue=(.045,.095,.115)

def cube(parent,name,size,pos,color):
    parent.include(name,box(size,center=pos,color=color))

def tube(parent,name,a,b,radius=.025,color=dark):
    parent.include(name,rod(radius,start=a,end=b,color=color))

architecture=Asset('Painted steel compartment')
cube(architecture,'deck',(5.2,11,.13),(0,0,-.07),floorcolor)
cube(architecture,'port bulkhead',(.14,10,3.45),(-2.08,.2,1.72),wall)
cube(architecture,'starboard bulkhead',(.14,7.1,3.45),(2.08,1.8,1.72),wall)
cube(architecture,'rear bulkhead',(4.2,.16,3.45),(0,3.55,1.72),wall)
cube(architecture,'overhead',(4.3,10,.13),(0,.2,3.48),cream)
cube(architecture,'port skirting',(.045,9,.29),(-1.99,.1,.145),brown)
cube(architecture,'starboard skirting',(.045,7,.30),(1.99,1.8,.15),brown)
cube(architecture,'rear skirting',(4.05,.035,.30),(0,3.44,.15),brown)
cube(architecture,'right transverse partition',(1.03,.13,3.45),(1.62,1.38,1.72),wall)
cube(architecture,'partition skirting',(1.03,.045,.30),(1.62,1.29,.15),brown)
for i,y in enumerate([-2.6,-.4,1.7,3.3]):
    cube(architecture,f'transverse beam {i}',(4.1,.17,.25),(0,y,3.22),(.40,.25,.12))
for i,x in enumerate([-1.4,-.65,.2,1.1]):
    cube(architecture,f'longitudinal rib {i}',(.075,8.7,.12),(x,.3,3.32),(.54,.38,.21))
column_x=.75
tube(architecture,'column lower',(column_x,-.62,.03),(column_x,-.62,1.44),.115,brown)
tube(architecture,'column upper',(column_x,-.62,1.44),(column_x,-.62,3.49),.115,(.59,.40,.20))
tube(architecture,'column foot',(column_x,-.62,.015),(column_x,-.62,.065),.145,(.30,.12,.055))
cube(architecture,'foreground right jamb',(.20,.20,3.6),(1.34,-2.30,1.8),brown)
scene.include('architecture',architecture)

bunks=Asset('Three tier port berths')
for k,z in enumerate([.49,1.12,1.75]):
    cube(bunks,f'bed frame {k}',(1.22,2.18,.075),(-1.37,2.30,z),dark)
    cube(bunks,f'mattress {k}',(1.16,2.10,.12),(-1.37,2.30,z+.09),(.61,.64,.58))
    cube(bunks,f'pillow {k}',(.77,.37,.14),(-1.37,3.03,z+.19),(.73,.73,.64))
    cube(bunks,f'blanket fold {k}',(1.16,.38,.035),(-1.37,1.57,z+.16),(.47,.53,.47))
for i,y in enumerate([1.20,3.40]):
    for j,x in enumerate([-1.98,-.75]):
        tube(bunks,f'upright {i} {j}',(x,y,.03),(x,y,2.40),.025,dark)
    tube(bunks,f'upper cross {i}',(-1.98,y,2.23),(-.75,y,2.23),.025,dark)
for k,z in enumerate([.43,1.06,1.69,2.24]):
    tube(bunks,f'long rail {k}',(-.75,1.20,z),(-.75,3.40,z),.022,dark)
scene.include('berths',bunks)

equipment=Asset('Port foreground ventilated cabinets')
for i,y in enumerate([-1.03,-.29]):
    cube(equipment,f'cabinet {i}',(.61,.65,.83),(-1.72,y,1.24),blue)
    cube(equipment,f'cabinet top {i}',(.68,.70,.045),(-1.72,y,1.68),(.065,.13,.14))
    for k in range(14):
        cube(equipment,f'louver {i} {k}',(.018,.48,.018),(-1.402,y,.89+k*.049),(.19,.27,.27))
    cube(equipment,f'edge upright {i}',(.04,.04,.78),(-1.38,y-.29,1.25),(.065,.10,.11))
cube(equipment,'long low green bench',(.53,3.6,.08),(-1.66,-.52,.48),(.035,.09,.075))
for i,y in enumerate([-2.05,.84]):
    tube(equipment,f'bench leg {i}',(-1.46,y,.05),(-1.46,y,.47),.025,dark)
scene.include('foreground cabinets',equipment)

lockers=Asset('Rear gray lockers')
for i,x in enumerate([-.62,-.12,.38]):
    cube(lockers,f'locker body {i}',(.48,.59,1.69),(x,3.12,1.42),(.34,.39,.36))
    cube(lockers,f'locker door {i}',(.445,.027,1.57),(x,2.806,1.42),(.43,.47,.43))
    cube(lockers,f'door seam {i}',(.012,.02,1.57),(x+.226,2.785,1.42),(.15,.21,.18))
    for j,z in enumerate([1.01,1.85]):
        for k in range(4):
            cube(lockers,f'vent {i} {j} {k}',(.21,.018,.013),(x,2.785,z+k*.048),(.23,.29,.26))
    cube(lockers,f'handle {i}',(.025,.04,.13),(x+.145,2.76,1.42),(.10,.15,.12))
    for k in [0,1]:
        cube(lockers,f'hinge {i} {k}',(.025,.028,.07),(x-.20,2.77,.93+k*.9),(.55,.55,.46))
    tube(lockers,f'rolled bedding {i}',(x-.13,3.10,2.34),(x+.13,3.10,2.34),.12,(.22,.27,.23))
scene.include('lockers',lockers)

chair=Asset('Small rear chair')
cx,cy=-.31,1.90
cube(chair,'seat',(.48,.46,.065),(cx,cy,.47),(.28,.25,.16))
cube(chair,'back',(.46,.065,.39),(cx,cy+.21,.82),(.39,.40,.30))
for i,x in enumerate([cx-.22,cx+.22]):
    for j,y in enumerate([cy-.19,cy+.19]):
        tube(chair,f'leg {i} {j}',(x,y,.02),(x,y,.47),.021,(.48,.51,.44))
    tube(chair,f'back frame {i}',(x,cy+.21,.44),(x,cy+.21,1.06),.023,(.48,.51,.44))
    tube(chair,f'arm {i}',(x,cy-.16,.70),(x,cy+.21,.70),.022,(.48,.51,.44))
chair.turn(axis='+z',degrees=12)
scene.include('chair',chair)

machine=Asset('Rear utility unit')
cube(machine,'metal base',(.69,.68,.88),(.69,2.12,.46),(.18,.23,.20))
cube(machine,'top plate',(.78,.76,.07),(.69,2.12,.94),(.28,.31,.25))
cube(machine,'front inset',(.55,.025,.62),(.69,1.765,.49),(.22,.26,.22))
tube(machine,'vertical valve riser',(.70,2.12,.95),(.70,2.12,1.65),.045,(.21,.23,.16))
tube(machine,'valve cross',(.48,2.12,1.43),(.91,2.12,1.43),.027,(.26,.23,.11))
scene.include('utility machine',machine)

pipes=Asset('Exposed ship services')
for i,x in enumerate([-.86,.25,.62]):
    tube(pipes,f'rear dark upright {i}',(x,3.30,.9),(x,3.30,3.15),.035,dark)
    tube(pipes,f'overhead dark run {i}',(x,-1.5,3.13),(x,3.30,3.13),.035,dark)
for i,(x,z) in enumerate([(-1.87,2.62),(-1.65,2.95),(.91,3.25)]):
    tube(pipes,f'long ivory pipe {i}',(x,-3.6,z),(x,3.30,z),.046,ivory)
for i,y in enumerate([-2.0,-.2,1.6,3.2]):
    tube(pipes,f'pipe suspension {i}',(-1.65,y,2.95),(-1.65,y,3.40),.022,ivory)
tube(pipes,'left descending pipe',(-1.87,1.0,2.62),(-1.87,1.0,2.30),.055,ivory)
tube(pipes,'rear horizontal pipe',(-1.87,3.24,2.73),(1.85,3.24,2.73),.045,ivory)
tube(pipes,'black transverse service',(-1.20,2.40,2.66),(.65,2.40,2.66),.033,dark)
tube(pipes,'foreground descending service',(-.70,1.25,.05),(-.70,1.25,2.65),.023,dark)
scene.include('pipes',pipes)

details=Asset('Bulkhead fittings')
cube(details,'vent casing',(.20,.69,.69),(-1.92,-.83,2.30),(.59,.59,.47))
cube(details,'vent black recess',(.018,.53,.45),(-1.805,-.83,2.28),(.035,.05,.045))
for i in range(6):
    cube(details,f'vent grille {i}',(.04,.53,.032),(-1.78,-.83,2.08+i*.076),(.58,.59,.48))
cube(details,'notice board',(.65,.045,.82),(1.42,1.285,2.02),(.20,.26,.23))
for i,x in enumerate([1.08,1.76]):
    cube(details,f'board side {i}',(.025,.06,.86),(x,1.26,2.02),(.36,.35,.26))
for i,z in enumerate([1.60,2.44]):
    cube(details,f'board rim {i}',(.70,.06,.025),(1.42,1.26,z),(.36,.35,.26))
cube(details,'red fixture back',(.36,.10,.63),(1.40,1.24,1.12),(.58,.018,.009))
tube(details,'red cylinder',(1.40,1.12,.88),(1.40,1.12,1.31),.12,(.72,.025,.012))
cube(details,'fixture label',(.12,.025,.15),(1.40,.985,1.12),(.72,.61,.38))
tube(details,'fixture handle',(1.30,1.11,1.40),(1.50,1.11,1.40),.028,(.61,.02,.009))
details.include('handle opening',ball(.065,center=(1.40,1.095,1.37),color=(.37,.27,.15)))
cube(details,'paper notice',(.38,.018,.57),(1.94,1.295,1.64),(.71,.71,.61))
for k in range(4):
    cube(details,f'notice text {k}',(.23,.025,.012),(1.94,1.279,1.78-k*.07),(.34,.36,.29))
cube(details,'right bench',(.60,2.25,.075),(1.72,-1.75,.47),(.025,.085,.065))
for i,y in enumerate([-2.66,-.85]):
    tube(details,f'right bench leg {i}',(1.49,y,.02),(1.49,y,.45),.027,dark)
scene.include('details',details)

lamps=Asset('Pendant lamps')
lamp_positions=[(-.40,-.8,3.06,.27),(-.40,1.65,2.98,.19),(-.2,3.15,2.9,.16)]
for i,(x,y,z,r) in enumerate(lamp_positions):
    tube(lamps,f'stem {i}',(x,y,z+.07),(x,y,3.42),.022,dark)
    tube(lamps,f'shade {i}',(x,y,z),(x,y,z+.065),r,(.17,.21,.19))
    tube(lamps,f'white underside {i}',(x,y,z-.013),(x,y,z-.001),r*.87,(.95,.96,.88))
    tube(lamps,f'shade crown {i}',(x,y,z+.06),(x,y,z+.13),r*.56,(.17,.21,.19))
scene.include('lamps',lamps)

realize(scene)
set_view((.05,-4.55,1.64),(-.15,2.7,1.69),lens=29,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.28,.23,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.16
area_emitter((-.40,-.8,2.99),power=100,size=.48,target=(-.6,-.7,.1),color=(1,.91,.75))
area_emitter((-.40,1.65,2.90),power=80,size=.42,target=(-.4,1.7,.1),color=(.87,.94,1))
area_emitter((0,-3.4,2.7),power=35,size=2.4,target=(0,1,1.1),color=(1,.83,.64))
area_emitter((.5,3.15,2.9),power=45,size=.7,target=(0,2.1,.7))
for mat in bpy.data.materials:
    if mat.use_nodes:
        bs=mat.node_tree.nodes.get('Principled BSDF')
        if bs:
            bs.inputs['Roughness'].default_value=.66
            col=bs.inputs['Base Color'].default_value
            if col[0]>.19 and col[0]<.30 and col[1]<.09:
                bs.inputs['Roughness'].default_value=.30
            if col[0]>.9 and col[1]>.9:
                bs.inputs['Emission Color'].default_value=(1,.96,.82,1)
                bs.inputs['Emission Strength'].default_value=3
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.45
