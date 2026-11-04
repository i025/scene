from sceneact import *
import bpy, math

# Approximate image landmarks (u,v): pole (.73,.03)-(.72,.84),
# rear lockers (.42,.39)-(.62,.61), chair (.48,.60), floor vanishing
# region (.46,.57), left bunks (.00,.68)-(.39,.44).
# Camera is nearly level, looking down a narrow shipboard compartment.
# Most uncertain: room depth, berth spacing, and foreground pillar distance.
CAMERA = (0.05, -4.8, 1.66)
TARGET = (0.0, 3.5, 1.69)
LENS = 26
ROOM_W, ROOM_D, ROOM_H = 3.65, 11.0, 3.35
LIGHT_POWER = 170

scene = Scene('Shipboard sleeping compartment')
cream = (.58,.57,.45)
ivory = (.76,.75,.61)
red = (.29,.075,.038)
floor_col = (.31,.105,.055)
steel = (.24,.28,.27)
dark = (.035,.055,.052)
white = (.72,.74,.69)
orange = (.42,.22,.105)

def bx(parent, name, size, pos, col):
    parent.include(name, box(size, center=pos, color=col))
def rd(parent, name, a, b, r, col):
    parent.include(name, rod(radius=r, start=a, end=b, color=col))

architecture = Asset('room architecture')
bx(architecture,'painted deck',(ROOM_W,ROOM_D,.12),(0,.5,-.06),floor_col)
bx(architecture,'port wall',(.13,ROOM_D,ROOM_H),(-1.88,.5,ROOM_H/2),cream)
bx(architecture,'starboard wall',(.13,ROOM_D,ROOM_H),(1.88,.5,ROOM_H/2),ivory)
bx(architecture,'rear bulkhead',(ROOM_W,.13,ROOM_H),(0,5.95,ROOM_H/2),cream)
bx(architecture,'ceiling',(ROOM_W,ROOM_D,.12),(0,.5,3.41),(.33,.30,.22))
for x in (-1.805,1.805):
    bx(architecture,'lower paint '+str(x),(.018,ROOM_D,.82),(x,.5,.41),red)
    bx(architecture,'base strip '+str(x),(.035,ROOM_D,.09),(x,.5,.065),(.20,.10,.055))
for i,y in enumerate([-3.3,-1.5,.5,2.7,4.9]):
    bx(architecture,f'ceiling crossbeam {i}',(3.65,.15,.22),(0,y,3.24),orange)
for i,x in enumerate([-1.45,-.68,.10,1.03]):
    bx(architecture,f'ceiling longitudinal {i}',(.10,10.8,.16),(x,.5,3.28),(.46,.29,.17))
scene.include('room',architecture)

post = Asset('dominant support column')
rd(post,'lower red column',(.82,-.55,.035),(.82,-.55,1.43),.086,red)
rd(post,'upper cream column',(.82,-.55,1.43),(.82,-.55,3.4),.086,(.72,.66,.46))
rd(post,'base collar',(.82,-.55,.015),(.82,-.55,.06),.115,(.40,.21,.10))
scene.include('column',post)

# Three long, narrow sleeping berths on the port side.
bunks = Asset('three tier bunks')
for i,z in enumerate([.53,1.10,1.67]):
    bx(bunks,f'mattress {i}',(.79,2.98,.13),(-1.30,1.97,z),white)
    bx(bunks,f'canvas edge {i}',(.83,3.03,.055),(-1.30,1.97,z-.085),(.36,.40,.36))
    for x in [-1.735,-.865]:
        rd(bunks,f'long rail {i} {x}',(x,.38,z-.08),(x,3.56,z-.08),.025,dark)
    for y in [.40,3.55]:
        rd(bunks,f'end rail {i} {y}',(-1.74,y,z-.075),(-.86,y,z-.075),.022,dark)
    bx(bunks,f'pillow {i}',(.57,.43,.13),(-1.30,3.17,z+.11),(.68,.70,.63))
for x in [-1.75,-.85]:
    for y in [.37,3.58]:
        rd(bunks,f'upright {x} {y}',(x,y,.05),(x,y,2.33),.024,dark)
# Farther small upper berth and back frame.
for z in [1.04,1.62]:
    bx(bunks,f'rear bedding {z}',(.83,1.12,.105),(-1.28,4.25,z),white)
scene.include('berths',bunks)

bench = Asset('port foreground bench')
bx(bench,'green seat',(.62,3.9,.075),(-1.48,-.71,.48),(.035,.105,.084))
for y in [-2.30,-.6,.9]:
    for x in [-1.70,-1.23]:
        rd(bench,f'leg {y} {x}',(x,y,.02),(x,y,.45),.019,steel)
rd(bench,'long lower brace',(-1.25,-2.5,.20),(-1.25,1.2,.20),.018,steel)
scene.include('port bench',bench)

# Louvered dark equipment housings, conspicuous along the left image edge.
equipment=Asset('port louvered equipment')
for i,y in enumerate([-.93,-.30]):
    bx(equipment,f'housing {i}',(.48,.56,.79),(-1.49,y,.94),(.065,.105,.108))
    bx(equipment,f'front recess {i}',(.016,.45,.64),(-1.237,y,.94),(.018,.034,.037))
    for j in range(17):
        bx(equipment,f'vent fin {i} {j}',(.034,.43,.012),(-1.222,y,.645+j*.036),(.22,.28,.27))
    bx(equipment,f'top rim {i}',(.52,.60,.035),(-1.49,y,1.35),(.11,.16,.15))
scene.include('vent cabinets',equipment)

# Tall gray locker bank in the central background.
lockers = Asset('rear steel lockers')
for i,x in enumerate([-.53,-.11,.31]):
    bx(lockers,f'cabinet {i}',(.405,.55,1.88),(x,4.56,1.08),(.43,.47,.44))
    bx(lockers,f'door {i}',(.376,.035,1.77),(x,4.265,1.10),(.47,.50,.46))
    for z in [.57,1.56,1.65,1.74]:
        for k in range(3):
            bx(lockers,f'slot {i} {z} {k}',(.16,.012,.014),(x,4.242,z+k*.032),(.20,.25,.23))
    bx(lockers,f'latch {i}',(.025,.045,.10),(x+.125,4.217,1.12),(.13,.16,.15))
    for z in [.42,1.70]:
        bx(lockers,f'hinge {i} {z}',(.024,.047,.06),(x-.16,4.22,z),(.25,.29,.27))
scene.include('lockers',lockers)

chair=Asset('small tubular chair')
bx(chair,'seat',(.43,.43,.055),(-.32,2.57,.51),(.32,.32,.22))
bx(chair,'back pad',(.43,.065,.35),(-.32,2.82,.91),(.38,.40,.32))
for x in [-.53,-.11]:
    rd(chair,f'back upright {x}',(x,2.79,.10),(x,2.79,1.10),.019,(.53,.55,.46))
    rd(chair,f'front leg {x}',(x,2.30,.03),(x,2.39,.52),.018,(.52,.53,.46))
    rd(chair,f'seat rail {x}',(x,2.35,.48),(x,2.79,.48),.019,(.52,.53,.46))
scene.include('chair',chair)

tank=Asset('central machinery')
bx(tank,'main rectangular casing',(.65,.66,.96),(.54,2.79,.54),(.23,.26,.23))
bx(tank,'upper lid',(.71,.71,.07),(.54,2.79,1.055),(.27,.29,.25))
bx(tank,'front panel',(.54,.025,.70),(.54,2.442,.57),(.29,.31,.28))
for x in [.25,.83]:
    rd(tank,f'vertical pipe {x}',(x,2.78,1.04),(x,2.78,2.52),.028,(.24,.22,.15))
rd(tank,'top connecting pipe',(.25,2.78,2.52),(.83,2.78,2.52),.028,steel)
rd(tank,'side brass pipe',(.93,2.87,.17),(.93,2.87,1.67),.033,(.39,.34,.20))
for z in [.95,1.35]:
    rd(tank,f'valve cross {z}',(.83,2.70,z),(1.03,2.70,z),.017,(.17,.18,.14))
scene.include('machinery',tank)

rightbench=Asset('cropped starboard bench')
bx(rightbench,'seat',(.54,2.5,.065),(1.54,-2.01,.48),(.025,.095,.073))
for y in [-2.95,-1.0]:
    for x in [1.33,1.75]:
        rd(rightbench,f'leg {x} {y}',(x,y,.015),(x,y,.45),.018,steel)
scene.include('right bench',rightbench)

fixtures=Asset('bulkhead fixtures')
# Dark rectangular notice board on starboard wall.
bx(fixtures,'board',(.045,1.00,.76),(1.792,2.48,1.99),(.21,.25,.23))
for y in [1.97,2.99]:
    bx(fixtures,f'board side {y}',(.05,.025,.80),(1.765,y,1.99),(.39,.40,.32))
for z in [1.59,2.39]:
    bx(fixtures,f'board edge {z}',(.05,1.04,.025),(1.765,2.48,z),(.39,.40,.32))
# Red emergency telephone / fire fixture below board.
bx(fixtures,'red wall box',(.16,.33,.55),(1.70,1.49,1.29),(.71,.035,.022))
bx(fixtures,'red box foot',(.21,.39,.07),(1.68,1.49,1.02),(.65,.035,.021))
rd(fixtures,'red handset',(1.58,1.40,1.30),(1.58,1.40,1.50),.043,(.82,.055,.029))
rd(fixtures,'other handset end',(1.58,1.57,1.29),(1.58,1.57,1.50),.035,(.70,.035,.02))
rd(fixtures,'handset top',(1.58,1.40,1.50),(1.58,1.57,1.50),.04,(.78,.045,.023))
bx(fixtures,'telephone label',(.012,.12,.075),(1.605,1.50,1.23),(.19,.13,.085))
# Port wall heater high above the foreground equipment.
bx(fixtures,'wall vent case',(.22,.66,.72),(-1.69,-.20,2.34),(.61,.60,.49))
bx(fixtures,'vent dark opening',(.018,.49,.48),(-1.568,-.20,2.32),(.045,.055,.05))
for j in range(6):
    bx(fixtures,f'wall vent slat {j}',(.035,.50,.037),(-1.54,-.20,2.11+j*.078),(.66,.66,.55))
scene.include('wall fixtures',fixtures)

pipes=Asset('overhead pipes and supports')
for i,x in enumerate([-1.54,-.95,.48]):
    rd(pipes,f'long overhead pipe {i}',(x,-3.5,2.91),(x,5.7,2.91),.035 if i<2 else .022,ivory)
for i,y in enumerate([-.6,1.8,3.7,5.25]):
    rd(pipes,f'cross overhead pipe {i}',(-1.8,y,2.86),(1.63,y,2.86),.025,ivory)
    rd(pipes,f'pipe drop {i}',(-1.64,y,2.86),(-1.64,y,2.51),.026,ivory)
    rd(pipes,f'pipe hook {i}',(-1.64,y,2.51),(-1.36,y,2.51),.026,ivory)
for y in [2.2,4.4]:
    rd(pipes,f'black overhead frame {y}',(-.78,y,2.68),(.84,y,2.68),.021,dark)
    rd(pipes,f'frame upright {y}',(.84,y,.04),(.84,y,2.68),.021,dark)
scene.include('pipes',pipes)

# Light shades are built as simple open conical metal shells after realization.
realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.43,.46,.40,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28

def material(name,color,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.58
    bs.inputs['Metallic'].default_value=metal
    return m

shade_mat=material('gray enamel lamp shades',(.33,.37,.34),.3)
glow=material('lamp white luminous underside',(.94,.96,.86))
bs=glow.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value=(.9,.96,.88,1)
bs.inputs['Emission Strength'].default_value=3.5
for i,(x,y,z,r) in enumerate([(-.69,-1.30,2.96,.255),(-.42,2.40,2.91,.17),(-.32,4.73,2.89,.12)]):
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=r,radius2=r*.38,depth=.12,location=(x,y,z))
    ob=bpy.context.object
    ob.name=f'Pendant enamel shade {i}'
    ob.data.materials.append(shade_mat)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r*.94,depth=.016,location=(x,y,z-.065))
    bpy.context.object.data.materials.append(glow)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.017,depth=.33,location=(x,y,z+.22))
    bpy.context.object.data.materials.append(shade_mat)
    area_emitter((x,y,z-.095),power=LIGHT_POWER if i==0 else 100,size=.55,target=(x,y,.1),color=(1,.95,.81))

# Subtle deck texture expresses worn painted metal without using any image assets.
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name.startswith('Box'):
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                p=mat.node_tree.nodes.get('Principled BSDF')
                if p: p.inputs['Roughness'].default_value=.67
deck_parent=bpy.data.objects.get('painted deck')
# Broad lighting keeps the shadowed berths legible.
area_emitter((.3,-3.8,2.7),power=110,size=3,target=(0,2,1),color=(1,.83,.64))
area_emitter((1.2,3.7,2.8),power=90,size=2,target=(-1,2,1),color=(.86,.91,1))
set_view(CAMERA,TARGET,lens=LENS,sensor=36)
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
