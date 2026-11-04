from sceneact import *
import bpy

# Reference anchors: lamp (.39,.16), column foot (.72,.84),
# bunk upright (.39,.70), chair (.47,.60), heater (.14,.30).
# Keep the successful second camera and 27 mm perspective.
# Largest local errors: left heater/cabinets were cropped excessively;
# move those assemblies inward. Chair was hidden by bunks; bring it forward
# and turn it slightly. Extend the pale right partition behind its fittings.
CAMERA = (.12, -2.60, 1.67)
TARGET = (0, 4.0, 1.07)
LENS = 27
POST_X, POST_Y = .72, .40
POST_PAINT_HEIGHT = 1.56
LIGHT_POWER = 65
FRONT_FILL_POWER = 48

scene = Scene('Ship accommodation compartment')
cream = (.52,.51,.40)
ivory = (.65,.65,.53)
brown = (.20,.052,.025)
redfloor = (.18,.052,.029)
green = (.018,.052,.035)
steel = (.30,.34,.32)
dark = (.025,.035,.030)

def asset(name):
    return scene.include(name, Asset(name))

def cube(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

def tube(parent, name, a, b, radius=.018, color=dark):
    return parent.include(name, rod(radius=radius, start=a, end=b, color=color))

architecture = asset('Compartment shell')
cube(architecture,'Red painted deck',(3.7,9,.12),(0,2,-.06),redfloor)
cube(architecture,'Port bulkhead',(.14,9,3.18),(-1.86,2,1.59),cream)
cube(architecture,'Rear bulkhead',(3.7,.15,3.18),(0,6.5,1.59),ivory)
cube(architecture,'Ceiling',(3.7,9,.13),(0,2,3.24),(.25,.20,.13))
cube(architecture,'Port red skirting',(.025,9,.32),(-1.775,2,.16),brown)
cube(architecture,'Rear red skirting',(3.7,.025,.32),(0,6.41,.16),brown)

wall = asset('Right partition')
cube(wall,'Cream transverse panel',(1.40,.15,3.14),(1.86,2.95,1.57),ivory)
cube(wall,'Red lower paint',(1.41,.025,.40),(1.86,2.861,.20),brown)
cube(wall,'Short right return',(.14,3.65,3.16),(1.91,4.75,1.58),cream)

post = asset('Foreground structural column')
tube(post,'Cream upper column',
     (POST_X,POST_Y,POST_PAINT_HEIGHT),(POST_X,POST_Y,3.23),
     .087,(.57,.43,.25))
tube(post,'Brown lower column',(POST_X,POST_Y,.06),
     (POST_X,POST_Y,POST_PAINT_HEIGHT),.088,brown)
tube(post,'Deck collar',(POST_X,POST_Y,.025),
     (POST_X,POST_Y,.075),.115,(.34,.19,.10))
cube(post,'Cropped right doorway jamb',(.16,.23,3.18),
     (.96,-.90,1.59),(.095,.026,.010))

beams = asset('Overhead beams')
for i,y in enumerate((-1.1,.75,2.75,4.75,6.3)):
    cube(beams,f'Transverse beam {i}',(3.62,.13,.29),
         (0,y,3.05),(.39,.25,.13))
for i,x in enumerate((-1.1,-.35,.55)):
    cube(beams,f'Long ceiling rib {i}',(.075,8.8,.14),
         (x,2,3.11),(.38,.25,.15))
for i,y in enumerate((-.8,1.1,3.2)):
    tube(beams,f'Port diagonal brace {i}',(-1.76,y,2.55),
         (-.90,y,3.17),.032,(.52,.39,.25))

bunks = asset('Three tier port berths')
for i,z in enumerate((.58,1.08,1.56)):
    cube(bunks,f'Berth frame {i}',(1.23,3.38,.065),
         (-1.055,3.18,z),dark)
    bunks.include(f'Mattress {i}',fillet_box(
        size=(1.19,3.27,.12),radius=.045,
        center=(-1.055,3.18,z+.082),color=(.59,.62,.57)))
    cube(bunks,f'Folded blanket {i}',(1.15,.61,.045),
         (-1.055,2.10,z+.16),(.46,.49,.44))
    bunks.include(f'Pillow {i}',fillet_box(
        size=(.65,.40,.12),radius=.055,
        center=(-1.13,4.45,z+.18),color=(.71,.71,.62)))
    tube(bunks,f'Outer berth rail {i}',(-.43,1.48,z+.01),
         (-.43,4.91,z+.01),.026,steel)
for i,y in enumerate((1.49,4.91)):
    for j,x in enumerate((-1.72,-.43)):
        tube(bunks,f'Upright {i} {j}',(x,y,.05),(x,y,2.35),.023)
    tube(bunks,f'Top crossbar {i}',(-1.72,y,2.34),
         (-.43,y,2.34),.022)
cube(bunks,'Hanging dark blanket',(.11,.46,.62),
     (-.53,4.30,1.98),(.035,.052,.048))

bench = asset('Long port bench')
cube(bench,'Green seat',(.48,5.6,.095),(-1.52,1.09,.40),green)
for i,y in enumerate((-1.1,1.,3.1)):
    tube(bench,f'Leg {i}',(-1.47,y,.02),(-1.47,y,.36),.023)
    tube(bench,f'Brace {i}',(-1.72,y,.06),(-1.30,y,.35),.016)

vents = asset('Port ventilated cabinets')
for i,y in enumerate((-.05,.67)):
    cube(vents,f'Cabinet body {i}',(.37,.61,.84),
         (-1.53,y,.92),(.065,.105,.095))
    cube(vents,f'Front inset {i}',(.025,.49,.68),
         (-1.326,y,.92),(.023,.040,.036))
    for j in range(15):
        cube(vents,f'Louver {i} {j}',(.032,.43,.018),
             (-1.304,y,.62+j*.042),(.17,.23,.21))
    cube(vents,f'Top {i}',(.42,.65,.035),
         (-1.53,y,1.36),(.11,.16,.14))
vents.move((.18,.15,0))

heater = asset('Port wall heater')
cube(heater,'Pale casing',(.23,.74,.73),(-1.65,1.,2.20),(.60,.59,.48))
cube(heater,'Grille inset',(.025,.59,.43),(-1.519,1.,2.15),dark)
for j in range(6):
    cube(heater,f'Slat {j}',(.043,.60,.035),
         (-1.493,1.,1.97+j*.072),(.56,.57,.48))
heater.move((.30,.30,0))
tube(heater,'Wall mounting upper',(-1.78,1.30,2.48),
     (-1.35,1.30,2.48),.025,(.48,.48,.39))
tube(heater,'Wall mounting lower',(-1.78,1.30,1.94),
     (-1.35,1.30,1.94),.025,(.48,.48,.39))

lockers = asset('Rear steel lockers')
LOCKER_Y = 4.70
for i,x in enumerate((-.41,.09,.59)):
    cube(lockers,f'Cabinet {i}',(.48,.57,1.83),
         (x,LOCKER_Y,1.15),steel)
    cube(lockers,f'Door {i}',(.445,.028,1.73),
         (x,LOCKER_Y-.305,1.15),(.38,.42,.39))
    cube(lockers,f'Seam {i}',(.012,.012,1.70),
         (x+.219,LOCKER_Y-.328,1.15),(.13,.16,.14))
    cube(lockers,f'Latch {i}',(.033,.045,.13),
         (x+.13,LOCKER_Y-.343,1.22),(.12,.14,.12))
    for j in range(4):
        cube(lockers,f'Upper vent {i} {j}',(.20,.012,.014),
             (x-.045,LOCKER_Y-.329,1.76-j*.045),(.20,.24,.21))
    for j in range(3):
        cube(lockers,f'Lower vent {i} {j}',(.20,.012,.013),
             (x-.045,LOCKER_Y-.329,.52-j*.045),(.20,.24,.21))
    lockers.include(f'Object above {i}',ball(
        radius=.14,center=(x,LOCKER_Y,2.14),color=(.22,.24,.20)))

table = asset('Rear work cabinet')
WORK_Y = 2.95
cube(table,'Cabinet body',(.78,.66,.77),
     (.65,WORK_Y,.435),(.19,.22,.18))
cube(table,'Worktop',(.89,.76,.065),
     (.65,WORK_Y,.85),(.25,.26,.21))
for i,x in enumerate((.46,.84)):
    cube(table,f'Front panel {i}',(.35,.025,.65),
         (x,WORK_Y-.345,.44),(.22,.25,.21))
    cube(table,f'Handle {i}',(.09,.034,.024),
         (x,WORK_Y-.37,.70),dark)
for i,(x,y) in enumerate(((.42,2.85),(.77,3.05),(.95,2.84))):
    tube(table,f'Workbench fitting {i}',(x,y,.89),
         (x,y,1.04),.05,(.17,.20,.16))

chair = asset('Pale metal chair')
cx,cy = -.12,2.65
chair_metal = (.56,.56,.45)
for i,x in enumerate((cx-.23,cx+.23)):
    for j,y in enumerate((cy-.22,cy+.22)):
        tube(chair,f'Leg {i} {j}',(x,y,.04),
             (x,y,.57),.020,chair_metal)
    tube(chair,f'Back upright {i}',(x,cy+.22,.54),
         (x,cy+.29,1.10),.024,chair_metal)
cube(chair,'Seat',(.49,.49,.075),(cx,cy,.57),(.19,.21,.16))
cube(chair,'Back cushion',(.44,.065,.31),
     (cx,cy+.26,.93),(.14,.16,.12))
tube(chair,'Back top',(cx-.23,cy+.29,1.11),
     (cx+.23,cy+.29,1.11),.025,chair_metal)
for i,x in enumerate((cx-.26,cx+.26)):
    tube(chair,f'Arm {i}',(x,cy-.19,.78),
         (x,cy+.24,.81),.023,chair_metal)
    tube(chair,f'Arm support {i}',(x,cy-.17,.56),
         (x,cy-.17,.78),.018,chair_metal)
chair.turn('z',-18,pivot=(cx,cy,0))

board = asset('Wall fittings')
cube(board,'Notice board rim',(.73,.055,.90),
     (1.65,2.844,1.90),(.32,.30,.23))
cube(board,'Dark chalkboard',(.67,.025,.82),
     (1.65,2.804,1.90),(.13,.17,.16))
cube(board,'Paper notice',(.28,.018,.53),
     (2.11,2.815,1.57),(.72,.72,.62))
board.include('Red fire backplate',fillet_box(
    size=(.34,.075,.62),radius=.035,
    center=(1.61,2.80,.94),color=(.66,.035,.016)))
board.include('Fire cylinder',rod(radius=.10,length=.39,
    center=(1.61,2.70,.96),color=(.66,.045,.020)))
board.include('Fire fitting',ball(radius=.07,
    center=(1.61,2.69,1.20),color=(.52,.05,.025)))
cube(board,'Fire label',(.10,.018,.18),
     (1.61,2.588,1.00),(.73,.62,.42))

rightbench = asset('Right foreground bench')
cube(rightbench,'Seat',(.48,1.50,.075),(1.25,-.55,.49),green)
for i,y in enumerate((-1.20,.10)):
    for j,x in enumerate((1.05,1.44)):
        tube(rightbench,f'Leg {i} {j}',(x,y,.015),(x,y,.46),.018)

pipes = asset('Overhead and rear plumbing')
for i,x in enumerate((-.94,-.57,.16)):
    tube(pipes,f'Long overhead pipe {i}',(x,-1.8,2.77),
         (x,6.3,2.77),.029,(.13,.15,.12))
for i,y in enumerate((1.5,3.4,5.1)):
    tube(pipes,f'Cross pipe {i}',(-1.76,y,2.65),
         (1.55,y,2.65),.026,(.10,.12,.10))
tube(pipes,'Cream port supply',(-1.73,-1.2,2.72),
     (-1.73,6.3,2.72),.055,(.64,.65,.54))
for i,x in enumerate((.62,.96)):
    tube(pipes,f'Rear vertical {i}',(x,3.50,.91),
         (x,3.50,2.74),.026,(.12,.14,.11))
    tube(pipes,f'Rear top turn {i}',(x,3.50,2.74),
         (x-.40,3.50,2.74),.027,(.12,.14,.11))
tube(pipes,'Rear frame left',(-.68,4.06,.05),(-.68,4.06,2.51),.023)
tube(pipes,'Rear frame top',(-.68,4.06,2.51),(.91,4.06,2.51),.023)
for i,x in enumerate((-.35,.21,.75)):
    tube(pipes,f'Ceiling drop {i}',(x,5.8,3.16),
         (x,5.8,2.40),.045,(.31,.31,.23))

lamps = asset('Hanging industrial lights')
lamp_positions = [(-.28,.30,2.75),(-.08,3.05,2.65),(.10,5.15,2.64)]
for i,(x,y,z) in enumerate(lamp_positions):
    tube(lamps,f'Stem {i}',(x,y,z+.06),
         (x,y,3.17),.023,(.15,.15,.11))
    shade = lamps.include(f'Shade dome {i}',ball(
        radius=.20,center=(x,y,z),color=(.20,.22,.19)))
    shade.resize((1,1,.54),pivot=(x,y,z))
    lamps.include(f'White lamp diffuser {i}',rod(
        radius=.201,length=.025,center=(x,y,z-.078),
        color=(.94,.96,.88)))

# Audit: all dimensions positive; fillets .045 and .055 <= .12/2,
# fire plate radius .035 <= .075/2. Rod endpoints differ.
# Indexed sibling keys are unique, rotations have explicit pivots.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient world')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (.40,.42,.35,1)
background.inputs['Strength'].default_value = .12

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'

for x,y,z in lamp_positions:
    area_emitter((x,y,z-.11),power=LIGHT_POWER,size=.40,
                 target=(x,y,.3),color=(.91,.95,1.0))
area_emitter((-.15,-1.8,2.65),power=FRONT_FILL_POWER,size=2,
             target=(0,3,1),color=(1,.85,.66))
area_emitter((.7,5.7,2.8),power=45,size=1.2,
             target=(0,3.8,.8),color=(.91,.94,.81))

# Material edits traverse semantic groups and copy shared materials.
floor_group = bpy.data.objects.get('Red painted deck')
if floor_group:
    for ob in floor_group.children_recursive:
        if ob.type == 'MESH' and ob.data.materials:
            mat = ob.data.materials[0].copy()
            ob.data.materials[0] = mat
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get('Principled BSDF')
            bsdf.inputs['Roughness'].default_value = .43
            noise = nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 38
            noise.inputs['Detail'].default_value = 2
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .08
            bump.inputs['Distance'].default_value = .008
            links.new(noise.outputs['Fac'],bump.inputs['Height'])
            links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])

for i in range(len(lamp_positions)):
    group = bpy.data.objects.get(f'White lamp diffuser {i}')
    if group:
        for ob in group.children_recursive:
            if ob.type == 'MESH' and ob.data.materials:
                mat = ob.data.materials[0].copy()
                ob.data.materials[0] = mat
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                bsdf.inputs['Emission Color'].default_value = (.90,.96,1,1)
                bsdf.inputs['Emission Strength'].default_value = 5
