from sceneact import *
import bpy, math

# Step 2 discrepancies and corrections:
# 1. Berths, cabinets and chair sit too low; pitch camera downward 2 degrees,
#    then raise these assemblies modestly. Keep lens fixed at 26 mm.
#    Move column slightly closer to preserve its matching foot at (.72,.84).
# 2. Berth front ends too far left, rear lockers too narrow and low:
#    widen berths toward aisle; widen/raise locker bank, shift it right.
# 3. Floor and walls too bright: darker deck, reduced ambient/fill light,
#    exposure -.45. Restore the cropped brown upright at the right border.
# Reference landmarks: pendant (.39,.16), column (.73,.00)-(.72,.84),
# lockers (.42,.39)-(.63,.61), front berth end (.39,.44)-(.39,.70),
# chair (.48,.60), machinery (.56,.55)-(.70,.69).
# Uncertain: room depth and actual wall-to-berth distance.
CAMERA = (.05, -3.8, 1.50)
TARGET = (0, 4.5, 1.24)
LENS = 26
ROOM_W, ROOM_D, ROOM_H = 3.65, 11, 3.35
LIGHT_POWER = 120

scene = Scene('Shipboard sleeping compartment')
cream = (.43,.43,.34)
ivory = (.54,.53,.42)
red = (.22,.043,.023)
floor_col = (.16,.037,.022)
steel = (.19,.23,.21)
dark = (.023,.036,.030)
white = (.62,.65,.59)
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
bx(architecture,'ceiling',(ROOM_W,ROOM_D,.12),(0,.5,3.41),(.23,.20,.14))
for x,h in [(-1.805,.65),(1.805,.28)]:
    bx(architecture,'lower paint '+str(x),(.018,ROOM_D,h),(x,.5,h/2),red)
    bx(architecture,'base strip '+str(x),(.035,ROOM_D,.09),(x,.5,.065),(.15,.06,.032))
for i,y in enumerate([-3.3,-1.5,.5,2.7,4.9]):
    bx(architecture,f'ceiling crossbeam {i}',(3.65,.15,.22),(0,y,3.24),orange)
for i,x in enumerate([-1.45,-.68,.10,1.03]):
    bx(architecture,f'ceiling longitudinal {i}',(.10,10.8,.16),(x,.5,3.28),(.36,.21,.11))
bx(architecture,'broad forward cross girder',(3.65,.20,.29),(0,-.70,3.18),(.39,.23,.12))
scene.include('room',architecture)

post = Asset('dominant support column')
PX, PY = .765, -.78
rd(post,'lower red column',(PX,PY,.035),(PX,PY,1.55),.090,red)
rd(post,'upper cream column',(PX,PY,1.55),(PX,PY,3.4),.090,(.61,.50,.31))
rd(post,'base collar',(PX,PY,.015),(PX,PY,.06),.118,(.30,.12,.05))
scene.include('column',post)

border = Asset('cropped right foreground upright')
bx(border,'brown upright',(.14,.18,3.42),(1.53,-1.67,1.71),(.23,.10,.043))
scene.include('right border upright',border)

bunks = Asset('three tier bunks')
# Front inner rail now reaches farther into the aisle.
INNER, OUTER = -.54, -1.735
BC = (INNER+OUTER)/2
BW = OUTER-INNER
BW = abs(BW)-.06
for i,z in enumerate([.68,1.25,1.82]):
    bx(bunks,f'mattress {i}',(BW,2.98,.12),(BC,1.97,z),white)
    bx(bunks,f'canvas edge {i}',(BW+.04,3.03,.05),(BC,1.97,z-.08),(.28,.32,.27))
    for x in [OUTER,INNER]:
        rd(bunks,f'long rail {i} {x}',(x,.38,z-.08),(x,3.56,z-.08),.024,dark)
    for y in [.40,3.55]:
        rd(bunks,f'end rail {i} {y}',(OUTER,y,z-.075),(INNER,y,z-.075),.022,dark)
    bx(bunks,f'pillow {i}',(.57,.43,.12),(-1.25,3.17,z+.10),(.61,.64,.57))
    # Small uneven rolls soften the otherwise perfectly straight bedding.
    rd(bunks,f'blanket roll {i}',(-1.56,.63,z+.055),(-.69,.63,z+.055),.045,(.52,.55,.49))
for x in [OUTER,INNER]:
    for y in [.37,3.58]:
        rd(bunks,f'upright {x} {y}',(x,y,.05),(x,y,2.45),.024,dark)
for z in [1.17,1.75]:
    bx(bunks,f'rear bedding {z}',(.83,1.12,.105),(-1.28,4.25,z),white)
scene.include('berths',bunks)

bench = Asset('port foreground bench')
bx(bench,'green seat',(.62,3.9,.075),(-1.48,-.71,.58),(.014,.055,.036))
for y in [-2.30,-.6,.9]:
    for x in [-1.70,-1.23]:
        rd(bench,f'leg {y} {x}',(x,y,.02),(x,y,.55),.019,steel)
rd(bench,'long lower brace',(-1.25,-2.5,.24),(-1.25,1.2,.24),.018,steel)
scene.include('port bench',bench)

equipment = Asset('port louvered equipment')
for i,y in enumerate([-.70,-.07]):
    bx(equipment,f'housing {i}',(.48,.56,.70),(-1.49,y,1.09),(.030,.055,.057))
    bx(equipment,f'front recess {i}',(.016,.45,.58),(-1.237,y,1.09),(.010,.020,.022))
    for j in range(17):
        bx(equipment,f'vent fin {i} {j}',(.034,.43,.012),(-1.222,y,.82+j*.033),(.12,.17,.16))
    bx(equipment,f'top rim {i}',(.52,.60,.035),(-1.49,y,1.455),(.06,.10,.09))
scene.include('vent cabinets',equipment)

lockers = Asset('rear steel lockers')
for i,x in enumerate([-.45,.03,.51]):
    bx(lockers,f'cabinet {i}',(.465,.55,2.02),(x,3.35,1.28),(.32,.36,.32))
    bx(lockers,f'door {i}',(.436,.035,1.91),(x,3.055,1.30),(.37,.41,.36))
    for z in [.72,1.78,1.87,1.96]:
        for k in range(3):
            bx(lockers,f'slot {i} {z} {k}',(.17,.012,.014),(x,3.032,z+k*.032),(.15,.20,.17))
    bx(lockers,f'latch {i}',(.025,.045,.10),(x+.15,3.007,1.26),(.08,.11,.09))
    for z in [.56,1.92]:
        bx(lockers,f'hinge {i} {z}',(.024,.047,.06),(x-.19,3.01,z),(.19,.23,.20))
    bx(lockers,f'case above locker {i}',(.34,.41,.18),(x,3.36,2.39),(.20,.23,.18))
scene.include('lockers',lockers)

chair = Asset('small tubular chair')
bx(chair,'seat',(.43,.43,.055),(-.17,2.12,.63),(.23,.24,.15))
back = box((.43,.065,.35),center=(-.17,2.37,1.03),color=(.25,.29,.21))
back.turn('x',-9)
chair.include('back pad',back)
for x in [-.38,.04]:
    rd(chair,f'back upright {x}',(x,2.34,.06),(x,2.39,1.22),.019,(.43,.46,.35))
    rd(chair,f'front leg {x}',(x,1.85,.03),(x,1.94,.64),.018,(.43,.46,.35))
    rd(chair,f'seat rail {x}',(x,1.90,.60),(x,2.34,.60),.019,(.43,.46,.35))
    rd(chair,f'arm support {x}',(x,1.97,.64),(x,1.97,.84),.017,(.43,.46,.35))
    rd(chair,f'arm {x}',(x,1.94,.84),(x,2.32,.84),.019,(.43,.46,.35))
scene.include('chair',chair)

tank = Asset('central machinery')
bx(tank,'main rectangular casing',(.77,.66,1.02),(.66,2.18,.57),(.14,.17,.14))
bx(tank,'upper lid',(.83,.71,.07),(.66,2.18,1.115),(.20,.22,.17))
bx(tank,'front panel',(.66,.025,.76),(.66,1.832,.60),(.19,.22,.17))
for x in [.31,1.01]:
    rd(tank,f'vertical pipe {x}',(x,2.17,1.10),(x,2.17,2.62),.027,(.19,.16,.09))
rd(tank,'top connecting pipe',(.31,2.17,2.62),(1.01,2.17,2.62),.027,steel)
rd(tank,'side brass pipe',(1.10,2.26,.17),(1.10,2.26,1.76),.030,(.29,.24,.12))
for z in [1.03,1.43]:
    rd(tank,f'valve cross {z}',(.99,2.09,z),(1.18,2.09,z),.017,(.12,.13,.09))
for x in [.42,.83]:
    rd(tank,f'casing foot {x}',(x,2.12,.01),(x,2.12,.12),.035,steel)
scene.include('machinery',tank)

rightbench = Asset('cropped starboard bench')
bx(rightbench,'seat',(.54,2.5,.065),(1.34,-2.01,.40),(.012,.053,.031))
for y in [-2.95,-1.0]:
    for x in [1.13,1.55]:
        rd(rightbench,f'leg {x} {y}',(x,y,.015),(x,y,.37),.018,steel)
scene.include('right bench',rightbench)

fixtures = Asset('bulkhead fixtures')
# Board slightly wider along wall; telephone retains its successful position.
bx(fixtures,'board',(.045,1.20,.80),(1.792,1.78,2.00),(.14,.18,.16))
for y in [1.17,2.39]:
    bx(fixtures,f'board side {y}',(.05,.025,.84),(1.765,y,2.00),(.27,.28,.21))
for z in [1.58,2.42]:
    bx(fixtures,f'board edge {z}',(.05,1.24,.025),(1.765,1.78,z),(.27,.28,.21))
bx(fixtures,'red wall box',(.16,.33,.55),(1.70,.79,1.29),(.61,.018,.012))
bx(fixtures,'red box foot',(.21,.39,.07),(1.68,.79,1.02),(.58,.018,.012))
rd(fixtures,'red handset',(1.58,.70,1.30),(1.58,.70,1.50),.043,(.73,.03,.018))
rd(fixtures,'other handset end',(1.58,.87,1.29),(1.58,.87,1.50),.035,(.63,.02,.012))
rd(fixtures,'handset top',(1.58,.70,1.50),(1.58,.87,1.50),.04,(.70,.025,.015))
bx(fixtures,'telephone label',(.012,.12,.075),(1.605,.80,1.23),(.16,.10,.055))
# Vent moves back and up, bringing its full silhouette inside the left border.
bx(fixtures,'wall vent case',(.22,.66,.72),(-1.69,.35,2.47),(.50,.49,.38))
bx(fixtures,'vent dark opening',(.018,.49,.48),(-1.568,.35,2.45),(.023,.030,.024))
for j in range(6):
    bx(fixtures,f'wall vent slat {j}',(.035,.50,.037),(-1.54,.35,2.24+j*.078),(.53,.53,.41))
bx(fixtures,'small wall paper',(.014,.40,.52),(1.80,-.20,1.98),(.60,.59,.47))
scene.include('wall fixtures',fixtures)

pipes = Asset('overhead pipes and supports')
for i,x in enumerate([-1.54,-.95,.48]):
    rd(pipes,f'long overhead pipe {i}',(x,-3.5,2.91),(x,5.7,2.91),.035 if i<2 else .022,ivory)
for i,y in enumerate([-.6,1.8,3.7,5.25]):
    rd(pipes,f'cross overhead pipe {i}',(-1.8,y,2.86),(1.63,y,2.86),.025,ivory)
    rd(pipes,f'pipe drop {i}',(-1.64,y,2.86),(-1.64,y,2.51),.026,ivory)
    rd(pipes,f'pipe hook {i}',(-1.64,y,2.51),(-1.36,y,2.51),.026,ivory)
for y in [2.2,4.4]:
    rd(pipes,f'black overhead frame {y}',(-.54,y,2.68),(1.02,y,2.68),.024,dark)
    rd(pipes,f'frame upright {y}',(1.02,y,.04),(1.02,y,2.68),.024,dark)
rd(pipes,'front berth high upright',(-.54,.37,.05),(-.54,.37,2.83),.028,dark)
rd(pipes,'front berth overhead tie',(-.54,.37,2.83),(.92,.37,2.83),.024,dark)
rd(pipes,'rear left dark pipe',(-.61,3.15,.08),(-.61,3.15,2.87),.025,dark)
rd(pipes,'rear dark overhead',(-.61,3.15,2.87),(1.05,3.15,2.87),.025,dark)
scene.include('pipes',pipes)

# API audit: all dimensions/radii positive, rod endpoints distinct,
# unique child names, no Boolean operations or external assets.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes['Background']
background.inputs['Color'].default_value = (.35,.38,.30,1)
background.inputs['Strength'].default_value = .085

def material(name, color, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Roughness'].default_value = .58
    bs.inputs['Metallic'].default_value = metal
    return m

shade_mat = material('gray enamel lamp shades',(.20,.24,.20),.3)
glow = material('lamp white luminous underside',(.94,.96,.86))
bs = glow.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value = (.9,.96,.88,1)
bs.inputs['Emission Strength'].default_value = 5

for i,(x,y,z,r) in enumerate([
    (-.32,-.45,3.01,.235),
    (-.18,2.15,2.96,.17),
    (-.22,4.30,2.94,.12)
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
        vertices=12, radius=.017, depth=.28,
        location=(x,y,z+.195))
    bpy.context.object.data.materials.append(shade_mat)
    area_emitter((x,y,z-.095),
                 power=LIGHT_POWER if i==0 else 85,
                 size=.42, target=(x,y,.1),
                 color=(1,.95,.81))

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
                    bs.inputs['Roughness'].default_value = .27
                    noise = nodes.new('ShaderNodeTexNoise')
                    noise.inputs['Scale'].default_value = 85
                    noise.inputs['Detail'].default_value = 2
                    bump = nodes.new('ShaderNodeBump')
                    bump.inputs['Strength'].default_value = .09
                    bump.inputs['Distance'].default_value = .008
                    links.new(noise.outputs['Fac'],bump.inputs['Height'])
                    links.new(bump.outputs['Normal'],bs.inputs['Normal'])

area_emitter((.3,-3.0,2.7), power=27, size=2.5,
             target=(0,2,1), color=(1,.85,.68))
area_emitter((1.2,3.7,2.8), power=45, size=2,
             target=(-1,2,1), color=(.86,.91,1))
set_view(CAMERA,TARGET,lens=LENS,sensor=36)
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = -.45
