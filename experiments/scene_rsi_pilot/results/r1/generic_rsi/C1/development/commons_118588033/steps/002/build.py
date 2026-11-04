from sceneact import *
import bpy, math

# Three principal discrepancies in step 1:
# 1. Foreground column and equipment too small: advance camera 1 m and lower it
#    .16 m. Preserve focal length; column target is u=.73, foot v=.84.
# 2. Rear lockers too small/highly recessed: bring bank forward .8 m and raise
#    its top .12 m; move pendant toward aisle to target (.39,.16).
# 3. Broad tones too bright, with excessive red on right wall: reduce lighting,
#    darken deck/walls, and lower the right wall's red paint boundary.
# Landmarks: berths right edge (.39,.44-.69), lockers (.42,.39)-(.63,.61),
# machinery (.56,.55)-(.70,.69), chair (.48,.60), column (.73,.00-.84).
# Uncertain dimensions remain berth depth and distance to rear bulkhead.
CAMERA = (.05, -3.8, 1.50)
TARGET = (0, 4.5, 1.53)
LENS = 26
ROOM_W, ROOM_D, ROOM_H = 3.65, 11, 3.35
LIGHT_POWER = 105

scene = Scene('Shipboard sleeping compartment')
cream = (.48,.47,.37)
ivory = (.59,.57,.44)
red = (.24,.048,.025)
floor_col = (.22,.057,.028)
steel = (.21,.25,.23)
dark = (.025,.040,.035)
white = (.65,.67,.60)
orange = (.34,.17,.075)

def bx(parent, name, size, pos, col):
    parent.include(name, box(size, center=pos, color=col))

def rd(parent, name, a, b, r, col):
    parent.include(name, rod(radius=r, start=a, end=b, color=col))

architecture = Asset('room architecture')
bx(architecture,'painted deck',(ROOM_W,ROOM_D,.12),(0,.5,-.06),floor_col)
bx(architecture,'port wall',(.13,ROOM_D,ROOM_H),(-1.88,.5,ROOM_H/2),cream)
bx(architecture,'starboard wall',(.13,ROOM_D,ROOM_H),(1.88,.5,ROOM_H/2),ivory)
bx(architecture,'rear bulkhead',(ROOM_W,.13,ROOM_H),(0,5.95,ROOM_H/2),cream)
bx(architecture,'ceiling',(ROOM_W,ROOM_D,.12),(0,.5,3.41),(.25,.22,.16))
for x,h in [(-1.805,.65),(1.805,.28)]:
    bx(architecture,'lower paint '+str(x),(.018,ROOM_D,h),(x,.5,h/2),red)
    bx(architecture,'base strip '+str(x),(.035,ROOM_D,.09),(x,.5,.065),(.17,.07,.035))
for i,y in enumerate([-3.3,-1.5,.5,2.7,4.9]):
    bx(architecture,f'ceiling crossbeam {i}',(3.65,.15,.22),(0,y,3.24),orange)
for i,x in enumerate([-1.45,-.68,.10,1.03]):
    bx(architecture,f'ceiling longitudinal {i}',(.10,10.8,.16),(x,.5,3.28),(.36,.21,.11))
scene.include('room',architecture)

post = Asset('dominant support column')
rd(post,'lower red column',(.82,-.55,.035),(.82,-.55,1.62),.086,red)
rd(post,'upper cream column',(.82,-.55,1.62),(.82,-.55,3.4),.086,(.64,.54,.34))
rd(post,'base collar',(.82,-.55,.015),(.82,-.55,.06),.115,(.31,.13,.055))
scene.include('column',post)

bunks = Asset('three tier bunks')
for i,z in enumerate([.53,1.10,1.67]):
    bx(bunks,f'mattress {i}',(.79,2.98,.13),(-1.30,1.97,z),white)
    bx(bunks,f'canvas edge {i}',(.83,3.03,.055),(-1.30,1.97,z-.085),(.30,.34,.29))
    for x in [-1.735,-.865]:
        rd(bunks,f'long rail {i} {x}',(x,.38,z-.08),(x,3.56,z-.08),.025,dark)
    for y in [.40,3.55]:
        rd(bunks,f'end rail {i} {y}',(-1.74,y,z-.075),(-.86,y,z-.075),.022,dark)
    bx(bunks,f'pillow {i}',(.57,.43,.13),(-1.30,3.17,z+.11),(.62,.64,.57))
for x in [-1.75,-.85]:
    for y in [.37,3.58]:
        rd(bunks,f'upright {x} {y}',(x,y,.05),(x,y,2.33),.024,dark)
for z in [1.04,1.62]:
    bx(bunks,f'rear bedding {z}',(.83,1.12,.105),(-1.28,4.25,z),white)
scene.include('berths',bunks)

bench = Asset('port foreground bench')
bx(bench,'green seat',(.62,3.9,.075),(-1.48,-.71,.48),(.018,.066,.045))
for y in [-2.30,-.6,.9]:
    for x in [-1.70,-1.23]:
        rd(bench,f'leg {y} {x}',(x,y,.02),(x,y,.45),.019,steel)
rd(bench,'long lower brace',(-1.25,-2.5,.20),(-1.25,1.2,.20),.018,steel)
scene.include('port bench',bench)

equipment = Asset('port louvered equipment')
for i,y in enumerate([-.93,-.30]):
    bx(equipment,f'housing {i}',(.48,.56,.79),(-1.49,y,.94),(.035,.065,.067))
    bx(equipment,f'front recess {i}',(.016,.45,.64),(-1.237,y,.94),(.012,.023,.025))
    for j in range(17):
        bx(equipment,f'vent fin {i} {j}',(.034,.43,.012),(-1.222,y,.645+j*.036),(.14,.20,.19))
    bx(equipment,f'top rim {i}',(.52,.60,.035),(-1.49,y,1.35),(.07,.11,.10))
scene.include('vent cabinets',equipment)

lockers = Asset('rear steel lockers')
for i,x in enumerate([-.53,-.11,.31]):
    bx(lockers,f'cabinet {i}',(.405,.55,2.00),(x,3.76,1.14),(.35,.39,.35))
    bx(lockers,f'door {i}',(.376,.035,1.89),(x,3.465,1.16),(.39,.43,.38))
    for z in [.57,1.64,1.73,1.82]:
        for k in range(3):
            bx(lockers,f'slot {i} {z} {k}',(.16,.012,.014),(x,3.442,z+k*.032),(.16,.21,.18))
    bx(lockers,f'latch {i}',(.025,.045,.10),(x+.125,3.417,1.12),(.10,.13,.11))
    for z in [.42,1.78]:
        bx(lockers,f'hinge {i} {z}',(.024,.047,.06),(x-.16,3.42,z),(.20,.24,.21))
    bx(lockers,f'case above locker {i}',(.31,.41,.18),(x,3.77,2.23),(.23,.25,.20))
scene.include('lockers',lockers)

chair = Asset('small tubular chair')
bx(chair,'seat',(.43,.43,.055),(-.25,2.27,.51),(.25,.26,.17))
bx(chair,'back pad',(.43,.065,.35),(-.25,2.52,.91),(.29,.32,.24))
for x in [-.46,-.04]:
    rd(chair,f'back upright {x}',(x,2.49,.10),(x,2.49,1.10),.019,(.46,.48,.37))
    rd(chair,f'front leg {x}',(x,2.00,.03),(x,2.09,.52),.018,(.46,.48,.37))
    rd(chair,f'seat rail {x}',(x,2.05,.48),(x,2.49,.48),.019,(.46,.48,.37))
scene.include('chair',chair)

tank = Asset('central machinery')
bx(tank,'main rectangular casing',(.65,.66,.96),(.54,2.49,.54),(.17,.20,.17))
bx(tank,'upper lid',(.71,.71,.07),(.54,2.49,1.055),(.23,.25,.20))
bx(tank,'front panel',(.54,.025,.70),(.54,2.142,.57),(.22,.25,.20))
for x in [.25,.83]:
    rd(tank,f'vertical pipe {x}',(x,2.48,1.04),(x,2.48,2.52),.028,(.21,.18,.10))
rd(tank,'top connecting pipe',(.25,2.48,2.52),(.83,2.48,2.52),.028,steel)
rd(tank,'side brass pipe',(.93,2.57,.17),(.93,2.57,1.67),.033,(.32,.27,.14))
for z in [.95,1.35]:
    rd(tank,f'valve cross {z}',(.83,2.40,z),(1.03,2.40,z),.017,(.13,.14,.10))
scene.include('machinery',tank)

rightbench = Asset('cropped starboard bench')
bx(rightbench,'seat',(.54,2.5,.065),(1.54,-2.01,.48),(.014,.063,.038))
for y in [-2.95,-1.0]:
    for x in [1.33,1.75]:
        rd(rightbench,f'leg {x} {y}',(x,y,.015),(x,y,.45),.018,steel)
scene.include('right bench',rightbench)

fixtures = Asset('bulkhead fixtures')
# Move board and emergency telephone forward for the reference's larger wall fixtures.
bx(fixtures,'board',(.045,1.08,.80),(1.792,1.78,2.00),(.16,.20,.18))
for y in [1.23,2.33]:
    bx(fixtures,f'board side {y}',(.05,.025,.84),(1.765,y,2.00),(.30,.31,.24))
for z in [1.58,2.42]:
    bx(fixtures,f'board edge {z}',(.05,1.12,.025),(1.765,1.78,z),(.30,.31,.24))
bx(fixtures,'red wall box',(.16,.33,.55),(1.70,.79,1.29),(.61,.018,.012))
bx(fixtures,'red box foot',(.21,.39,.07),(1.68,.79,1.02),(.58,.018,.012))
rd(fixtures,'red handset',(1.58,.70,1.30),(1.58,.70,1.50),.043,(.73,.03,.018))
rd(fixtures,'other handset end',(1.58,.87,1.29),(1.58,.87,1.50),.035,(.63,.02,.012))
rd(fixtures,'handset top',(1.58,.70,1.50),(1.58,.87,1.50),.04,(.70,.025,.015))
bx(fixtures,'telephone label',(.012,.12,.075),(1.605,.80,1.23),(.16,.10,.055))
bx(fixtures,'wall vent case',(.22,.66,.72),(-1.69,-.20,2.34),(.53,.52,.41))
bx(fixtures,'vent dark opening',(.018,.49,.48),(-1.568,-.20,2.32),(.028,.036,.029))
for j in range(6):
    bx(fixtures,f'wall vent slat {j}',(.035,.50,.037),(-1.54,-.20,2.11+j*.078),(.56,.56,.44))
scene.include('wall fixtures',fixtures)

pipes = Asset('overhead pipes and supports')
for i,x in enumerate([-1.54,-.95,.48]):
    rd(pipes,f'long overhead pipe {i}',(x,-3.5,2.91),(x,5.7,2.91),.035 if i<2 else .022,ivory)
for i,y in enumerate([-.6,1.8,3.7,5.25]):
    rd(pipes,f'cross overhead pipe {i}',(-1.8,y,2.86),(1.63,y,2.86),.025,ivory)
    rd(pipes,f'pipe drop {i}',(-1.64,y,2.86),(-1.64,y,2.51),.026,ivory)
    rd(pipes,f'pipe hook {i}',(-1.64,y,2.51),(-1.36,y,2.51),.026,ivory)
for y in [2.2,4.4]:
    rd(pipes,f'black overhead frame {y}',(-.78,y,2.68),(.84,y,2.68),.021,dark)
    rd(pipes,f'frame upright {y}',(.84,y,.04),(.84,y,2.68),.021,dark)
# The front berth end has a strong black rectangular silhouette.
rd(pipes,'front berth high upright',(-.85,.37,.05),(-.85,.37,2.83),.028,dark)
rd(pipes,'front berth overhead tie',(-.85,.37,2.83),(.64,.37,2.83),.024,dark)
scene.include('pipes',pipes)

# API audit: positive sizes/radii; distinct rod endpoints; unique include keys.
# No Boolean geometry, external assets, rendering, or file operations.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes['Background']
background.inputs['Color'].default_value = (.35,.38,.30,1)
background.inputs['Strength'].default_value = .14

def material(name, color, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Roughness'].default_value = .58
    bs.inputs['Metallic'].default_value = metal
    return m

shade_mat = material('gray enamel lamp shades',(.24,.28,.24),.3)
glow = material('lamp white luminous underside',(.94,.96,.86))
bs = glow.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value = (.9,.96,.88,1)
bs.inputs['Emission Strength'].default_value = 4
for i,(x,y,z,r) in enumerate([
    (-.32,-.45,2.96,.235),
    (-.18,2.15,2.91,.17),
    (-.22,4.30,2.89,.12)
]):
    bpy.ops.mesh.primitive_cone_add(
        vertices=32, radius1=r, radius2=r*.38,
        depth=.12, location=(x,y,z))
    ob = bpy.context.object
    ob.name = f'Pendant enamel shade {i}'
    ob.data.materials.append(shade_mat)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=r*.94, depth=.016,
        location=(x,y,z-.065))
    bpy.context.object.data.materials.append(glow)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=.017, depth=.33,
        location=(x,y,z+.22))
    bpy.context.object.data.materials.append(shade_mat)
    area_emitter((x,y,z-.095),
                 power=LIGHT_POWER if i==0 else 75,
                 size=.42, target=(x,y,.1),
                 color=(1,.95,.81))

# Adjust deck finish through its semantic parent, preserving separate meshes.
deck_parent = bpy.data.objects.get('painted deck')
if deck_parent:
    for ob in deck_parent.children_recursive:
        if ob.type == 'MESH':
            for slot in ob.material_slots:
                if slot.material:
                    m = slot.material.copy()
                    slot.material = m
                    m.use_nodes = True
                    nodes = m.node_tree.nodes
                    links = m.node_tree.links
                    bs = nodes.get('Principled BSDF')
                    bs.inputs['Roughness'].default_value = .34
                    noise = nodes.new('ShaderNodeTexNoise')
                    noise.inputs['Scale'].default_value = 85
                    noise.inputs['Detail'].default_value = 2
                    bump = nodes.new('ShaderNodeBump')
                    bump.inputs['Strength'].default_value = .13
                    bump.inputs['Distance'].default_value = .012
                    links.new(noise.outputs['Fac'],bump.inputs['Height'])
                    links.new(bump.outputs['Normal'],bs.inputs['Normal'])

area_emitter((.3,-3.0,2.7), power=55, size=2.5,
             target=(0,2,1), color=(1,.85,.68))
area_emitter((1.2,3.7,2.8), power=55, size=2,
             target=(-1,2,1), color=(.86,.91,1))
set_view(CAMERA,TARGET,lens=LENS,sensor=36)
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
