from sceneact import *
import bpy, math

# Estimated anchors (origin upper left): main post x=.73, foot=(.72,.84);
# nearest lamp=(.39,.16); rear lockers=(.49,.48); bunk rails span x=.02-.40.
# Camera looks almost level down a narrow ship compartment, with slight upward pitch.
CAMERA = (0.12, -3.5, 1.67)
TARGET = (0.0, 4.0, 1.76)
LENS = 27
ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT = 3.7, 9.0, 3.18
POST_X, POST_Y = .91, .65
LIGHT_POWER = 150

scene = Scene('Ship accommodation compartment')
cream = (.57,.56,.43)
ivory = (.72,.72,.60)
brown = (.23,.075,.035)
redfloor = (.27,.085,.046)
green = (.025,.065,.045)
steel = (.34,.38,.36)
dark = (.035,.045,.04)
white = (.70,.71,.64)

def asset(name):
    return scene.include(name, Asset(name))

def cube(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

def tube(parent, name, a, b, radius=.018, color=dark):
    return parent.include(name, rod(radius=radius, start=a, end=b, color=color))

architecture = asset('Compartment shell')
cube(architecture,'Red painted deck',(ROOM_WIDTH,ROOM_DEPTH,.12),(0,2.5,-.06),redfloor)
cube(architecture,'Port bulkhead',(.14,ROOM_DEPTH,ROOM_HEIGHT),(-1.86,2.5,1.59),cream)
cube(architecture,'Rear bulkhead',(ROOM_WIDTH,.15,ROOM_HEIGHT),(0,6.95,1.59),ivory)
cube(architecture,'Ceiling',(ROOM_WIDTH,ROOM_DEPTH,.13),(0,2.5,3.24),(.37,.34,.25))
cube(architecture,'Port red skirting',(.025,ROOM_DEPTH,.35),(-1.775,2.5,.175),brown)
cube(architecture,'Rear red skirting',(ROOM_WIDTH,.025,.35),(0,6.86,.175),brown)

# A transverse wall at the right frames the machinery recess.
wall = asset('Right partition')
cube(wall,'Cream panel',(1.27,.15,3.14),(1.28,4.45,1.57),ivory)
cube(wall,'Red lower paint',(1.28,.025,.39),(1.28,4.36,.195),brown)
cube(wall,'Right return',(.14,5.1,3.16),(1.91,1.95,1.58),cream)
cube(wall,'Right return lower band',(.025,5.1,.39),(1.825,1.95,.195),brown)

post = asset('Foreground structural column')
tube(post,'Cream upper column',(POST_X,POST_Y,1.46),(POST_X,POST_Y,3.23),.105,(.56,.43,.25))
tube(post,'Brown lower column',(POST_X,POST_Y,.06),(POST_X,POST_Y,1.46),.106,brown)
tube(post,'Deck collar',(POST_X,POST_Y,.025),(POST_X,POST_Y,.075),.137,(.37,.22,.12))
# Cropped jamb at the extreme right.
cube(post,'Near right door jamb',(.20,.25,3.18),(1.50,-1.48,1.59),(.25,.10,.045))

beams = asset('Overhead beams')
for i,y in enumerate((-1.1,.75,2.75,4.75,6.6)):
    cube(beams,f'Transverse beam {i}',(3.62,.13,.29),(0,y,3.05),(.49,.34,.19))
for i,x in enumerate((-1.1,-.35,.55)):
    cube(beams,f'Long ceiling rib {i}',(.075,8.8,.14),(x,2.5,3.11),(.45,.32,.20))
for i,y in enumerate((-.8,1.1,3.2)):
    tube(beams,f'Port diagonal brace {i}',(-1.76,y,2.55),(-.90,y,3.17),.032,(.58,.46,.30))

# Three canvas-covered berths run lengthwise down the port side.
bunks = asset('Three tier port berths')
for i,z in enumerate((.62,1.22,1.84)):
    cube(bunks,f'Berth dark frame {i}',(.86,3.38,.065),(-1.25,3.18,z),dark)
    bunks.include(f'Mattress {i}',fillet_box(
        size=(.83,3.27,.12),radius=.045,center=(-1.25,3.18,z+.082),
        color=(.62,.65,.60)))
    cube(bunks,f'Folded blanket {i}',(.80,.61,.045),(-1.25,2.10,z+.16),(.50,.53,.47))
    bunks.include(f'Pillow {i}',fillet_box(
        size=(.62,.40,.12),radius=.055,center=(-1.25,4.45,z+.18),
        color=(.76,.76,.66)))
    tube(bunks,f'Outer berth edge {i}',(-.81,1.48,z+.01),(-.81,4.91,z+.01),.026,steel)
for i,y in enumerate((1.49,4.91)):
    for j,x in enumerate((-1.72,-.80)):
        tube(bunks,f'Bed upright {i} {j}',(x,y,.05),(x,y,2.38),.025,dark)
    tube(bunks,f'Bed top crossbar {i}',(-1.72,y,2.36),(-.80,y,2.36),.022,dark)
# Dark suspended fabric near the back of the upper bunk.
cube(bunks,'Hanging dark blanket',(.10,.38,.56),(-.85,4.48,2.04),(.045,.068,.065))

bench = asset('Long port bench')
cube(bench,'Green seat',(.48,5.6,.095),(-1.52,1.09,.40),green)
for i,y in enumerate((-1.1,1.0,3.1)):
    tube(bench,f'Bench leg {i}',(-1.47,y,.02),(-1.47,y,.36),.023,dark)
    tube(bench,f'Bench brace {i}',(-1.72,y,.06),(-1.30,y,.35),.016,dark)

# Foreground louvered equipment boxes.
vents = asset('Port ventilated cabinets')
for i,y in enumerate((-.05,.67)):
    cube(vents,f'Cabinet body {i}',(.37,.61,.84),(-1.53,y,.92),(.10,.14,.13))
    cube(vents,f'Cabinet front inset {i}',(.025,.49,.68),(-1.326,y,.92),(.035,.055,.052))
    for j in range(15):
        cube(vents,f'Cabinet louver {i} {j}',(.032,.43,.018),(-1.304,y,.62+j*.042),(.24,.29,.27))
    cube(vents,f'Cabinet top {i}',(.42,.65,.035),(-1.53,y,1.36),(.16,.20,.18))

# Wall-mounted pale heater, seen high on the left.
heater = asset('Port wall heater')
cube(heater,'Pale casing',(.23,.74,.73),(-1.65,1.0,2.20),(.65,.64,.52))
cube(heater,'Dark grille inset',(.025,.59,.43),(-1.519,1.0,2.15),(.045,.055,.048))
for j in range(6):
    cube(heater,f'Heater slat {j}',(.043,.60,.035),(-1.493,1.0,1.97+j*.072),(.59,.60,.51))

lockers = asset('Rear steel lockers')
for i,x in enumerate((-.58,-.08,.42)):
    cube(lockers,f'Locker cabinet {i}',(.48,.57,1.83),(x,5.75,1.15),steel)
    cube(lockers,f'Locker door {i}',(.445,.028,1.73),(x,5.445,1.15),(.41,.45,.42))
    cube(lockers,f'Door seam {i}',(.012,.012,1.70),(x+.219,5.422,1.15),(.16,.19,.17))
    cube(lockers,f'Latch {i}',(.033,.045,.13),(x+.13,5.407,1.22),(.13,.15,.14))
    for j in range(4):
        cube(lockers,f'Upper ventilation {i} {j}',(.20,.012,.014),(x-.045,5.421,1.76-j*.045),(.23,.27,.24))
    for j in range(3):
        cube(lockers,f'Lower ventilation {i} {j}',(.20,.012,.013),(x-.045,5.421,.52-j*.045),(.23,.27,.24))
    lockers.include(f'Object above locker {i}',ball(radius=.14,center=(x,5.74,2.14),color=(.26,.28,.24)))

table = asset('Rear work cabinet')
cube(table,'Metal cabinet body',(.86,.70,.86),(.65,4.55,.49),(.24,.26,.22))
cube(table,'Worktop',(.96,.80,.075),(.65,4.55,.96),(.32,.32,.26))
for i,x in enumerate((.44,.85)):
    cube(table,f'Front panel {i}',(.38,.025,.68),(x,4.185,.50),(.28,.30,.26))
    cube(table,f'Handle {i}',(.09,.034,.024),(x,4.158,.76),dark)
for i,(x,y) in enumerate(((.42,4.45),(.77,4.65),(.95,4.44))):
    tube(table,f'Workbench fitting {i}',(x,y,1.0),(x,y,1.15),.055,(.20,.23,.20))

chair = asset('Pale metal chair')
cx,cy=-.24,3.56
for i,x in enumerate((cx-.23,cx+.23)):
    for j,y in enumerate((cy-.22,cy+.22)):
        tube(chair,f'Leg {i} {j}',(x,y,.04),(x,y,.57),.020,(.60,.60,.49))
    tube(chair,f'Back upright {i}',(x,cy+.22,.54),(x,cy+.29,1.10),.024,(.67,.66,.53))
cube(chair,'Seat',(.49,.49,.075),(cx,cy,.57),(.23,.24,.19))
cube(chair,'Back cushion',(.44,.065,.31),(cx,cy+.26,.93),(.25,.26,.22))
tube(chair,'Back top',(cx-.23,cy+.29,1.11),(cx+.23,cy+.29,1.11),.025,(.67,.66,.53))
for i,x in enumerate((cx-.26,cx+.26)):
    tube(chair,f'Arm {i}',(x,cy-.19,.78),(x,cy+.24,.81),.023,(.65,.65,.53))
    tube(chair,f'Arm support {i}',(x,cy-.17,.56),(x,cy-.17,.78),.018,(.65,.65,.53))

board = asset('Wall fittings')
cube(board,'Notice board rim',(.76,.055,.90),(1.25,4.343,1.97),(.39,.36,.26))
cube(board,'Dark chalkboard',(.69,.025,.82),(1.25,4.303,1.97),(.19,.23,.21))
cube(board,'Paper notice',(.29,.018,.53),(1.80,4.315,1.57),(.77,.77,.67))
# Red fire equipment mounting, rounded visible silhouette.
board.include('Red fire backplate',fillet_box(size=(.34,.075,.62),radius=.035,
              center=(1.13,4.30,1.00),color=(.72,.055,.025)))
board.include('Fire cylinder',rod(radius=.10,length=.39,center=(1.13,4.20,1.02),color=(.70,.065,.03)))
board.include('Fire fitting',ball(radius=.07,center=(1.13,4.19,1.26),color=(.57,.075,.035)))
cube(board,'Fire label',(.10,.018,.18),(1.13,4.088,1.06),(.75,.65,.44))

rightbench = asset('Right foreground bench')
cube(rightbench,'Seat',(.48,1.70,.075),(1.34,-.92,.49),green)
for i,y in enumerate((-1.65,-.21)):
    for j,x in enumerate((1.14,1.53)):
        tube(rightbench,f'Leg {i} {j}',(x,y,.015),(x,y,.46),.018,dark)

pipes = asset('Overhead and rear plumbing')
for i,x in enumerate((-.94,-.57,.16)):
    tube(pipes,f'Long overhead pipe {i}',(x,-1.8,2.77),(x,6.7,2.77),.029,(.17,.19,.16))
for i,y in enumerate((1.5,3.4,5.1)):
    tube(pipes,f'Cross pipe {i}',(-1.76,y,2.65),(1.55,y,2.65),.026,(.13,.15,.13))
tube(pipes,'Cream port supply',(-1.73,-1.2,2.72),(-1.73,6.6,2.72),.055,(.69,.70,.59))
for i,x in enumerate((.62,.96)):
    tube(pipes,f'Rear vertical {i}',(x,5.13,.91),(x,5.13,2.74),.026,(.15,.17,.14))
    tube(pipes,f'Rear top turn {i}',(x,5.13,2.74),(x-.40,5.13,2.74),.027,(.15,.17,.14))
tube(pipes,'Rear black frame left',(-.68,5.06,.05),(-.68,5.06,2.51),.023,dark)
tube(pipes,'Rear black frame top',(-.68,5.06,2.51),(.91,5.06,2.51),.023,dark)
for i,x in enumerate((-.35,.21,.75)):
    tube(pipes,f'Ceiling drop {i}',(x,6.4,3.16),(x,6.4,2.40),.045,(.38,.38,.29))

lamps = asset('Hanging industrial lights')
lamp_positions = [(-.48,-.10,2.75),(-.30,3.05,2.65),(-.06,5.50,2.64)]
for i,(x,y,z) in enumerate(lamp_positions):
    tube(lamps,f'Pendant stem {i}',(x,y,z+.06),(x,y,3.17),.023,(.19,.19,.15))
    lamps.include(f'Shade dome {i}',ball(radius=.20,center=(x,y,z),color=(.27,.29,.26)))
    # Explicit pivot preserves the lamp position while flattening the dome.
    lamps.members[f'Shade dome {i}'].resize((1,1,.42),pivot=(x,y,z))
    lamps.include(f'White lamp diffuser {i}',rod(radius=.201,length=.025,
                  center=(x,y,z-.054),color=(.94,.96,.88)))

# Audit: all sizes/radii positive; fillets <= half smallest dimension.
# Repeated siblings have indexed keys; materials are edited through descendants.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient world')
sc.world.use_nodes = True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.44,.46,.39,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.30

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.view_settings.view_transform='AgX'

for i,(x,y,z) in enumerate(lamp_positions):
    area_emitter((x,y,z-.09),power=LIGHT_POWER,size=.42,
                 target=(x,y,.3),color=(.90,.95,1.0))
area_emitter((-.15,-2.3,2.65),power=100,size=2.2,target=(0,3,1.0),color=(1.0,.85,.65))
area_emitter((.7,5.7,2.8),power=100,size=1.3,target=(0,3.8,.8),color=(.91,.94,.81))

# Slightly irregular painted deck, without adding decorative geometry.
floor_group=bpy.data.objects.get('Red painted deck')
if floor_group:
    for ob in floor_group.children_recursive:
        if ob.type=='MESH' and ob.data.materials:
            mat=ob.data.materials[0].copy()
            ob.data.materials[0]=mat
            mat.use_nodes=True
            nodes=mat.node_tree.nodes
            links=mat.node_tree.links
            bsdf=nodes.get('Principled BSDF')
            bsdf.inputs['Roughness'].default_value=.39
            noise=nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=38
            noise.inputs['Detail'].default_value=2
            bump=nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.16
            bump.inputs['Distance'].default_value=.016
            links.new(noise.outputs['Fac'],bump.inputs['Height'])
            links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])

for i in range(len(lamp_positions)):
    group=bpy.data.objects.get(f'White lamp diffuser {i}')
    if group:
        for ob in group.children_recursive:
            if ob.type=='MESH' and ob.data.materials:
                mat=ob.data.materials[0].copy()
                ob.data.materials[0]=mat
                mat.use_nodes=True
                bsdf=mat.node_tree.nodes.get('Principled BSDF')
                bsdf.inputs['Emission Color'].default_value=(.90,.96,1,1)
                bsdf.inputs['Emission Strength'].default_value=3
