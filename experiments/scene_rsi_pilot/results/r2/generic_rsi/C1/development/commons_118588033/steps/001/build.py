from sceneact import *
import bpy
import math

# Camera hypothesis: a narrow shipboard room viewed nearly along its length.
# Floor fills the lower 38%; bunks occupy left .04-.42, lockers center .40-.63,
# and the close cream/red pillar occupies approximately x .70-.79.
# Ceiling lines and bed rails converge near (.49,.35). Foreground furniture
# occludes bunks, which overlap the rear lockers and central pipe enclosure.
CAM = (0.0, -3.0, 1.66)
TARGET = (-0.08, 4.7, 1.64)
ROOM_W, ROOM_L, ROOM_H = 3.8, 8.3, 3.28

scene = Scene('Ship accommodation compartment')
cream = (.65,.65,.54)
pale = (.77,.76,.64)
red = (.30,.105,.073)
floor_color = (.36,.145,.095)
steel = (.37,.40,.37)
dark = (.055,.075,.066)
green = (.075,.14,.125)
linen = (.69,.70,.61)

def add(parent, name, node):
    parent.include(name, node)

architecture = Asset('Compartment architecture')
add(architecture, 'Red painted deck', box((4.0,11,.12), (0,2.7,-.06), floor_color))
add(architecture, 'Port wall', box((.16,9.2,3.3), (-1.98,3.1,1.65), cream))
add(architecture, 'Starboard wall', box((.16,8.3,3.3), (1.98,3.65,1.65), pale))
add(architecture, 'Rear bulkhead', box((4,.14,3.3), (0,7.72,1.65), cream))
add(architecture, 'Ceiling', box((4,10,.14), (0,2.8,3.36), (.31,.28,.20)))
for side in (-1,1):
    add(architecture, f'Lower red wall {side}', box((.035,9,.43), (side*1.885,3.0,.215), red))
    add(architecture, f'Wall skirting {side}', box((.07,9,.065), (side*1.87,3,.045), (.22,.12,.075)))
for i,y in enumerate([-.9,.8,2.7,4.6,6.6]):
    add(architecture, f'Transverse overhead beam {i}',
        box((3.9,.17,.28),(0,y,3.12),(.48,.34,.20)))
for i,x in enumerate([-1.55,-.88,-.15,.65,1.45]):
    add(architecture, f'Ceiling longitudinal {i}',
        box((.085,8.7,.11),(x,3,3.22),(.47,.32,.20)))
scene.include('Architecture',architecture)

pillar = Asset('Foreground supporting column')
add(pillar,'Lower oxblood shaft',rod(.108,start=(1.03,.64,.05),end=(1.03,.64,1.40),color=red))
add(pillar,'Upper ivory shaft',rod(.112,start=(1.03,.64,1.40),end=(1.03,.64,3.28),color=(.73,.65,.44)))
add(pillar,'Deck collar',rod(.145,length=.045,center=(1.03,.64,.035),color=(.46,.25,.14)))
add(pillar,'Overhead collar',rod(.15,length=.14,center=(1.03,.64,3.16),color=(.52,.37,.22)))
scene.include('Main pillar',pillar)

# Three long canvas bunks along the port wall, with black tubular supports.
bunks = Asset('Port triple berth')
for i,y in enumerate([1.3,4.85]):
    for j,x in enumerate([-1.82,-.65]):
        add(bunks,f'Post {i} {j}',rod(.028,start=(x,y,.18),end=(x,y,2.48),color=dark))
for level,z in enumerate([.58,1.12,1.68]):
    add(bunks,f'Canvas mattress {level}',box((1.11,3.48,.105),(-1.23,3.05,z),linen))
    add(bunks,f'Mattress rounded front {level}',
        rod(.058,start=(-1.76,1.29,z+.015),end=(-.70,1.29,z+.015),color=(.73,.74,.66)))
    for side,x in enumerate([-1.80,-.67]):
        add(bunks,f'Long bed rail {level} {side}',rod(.026,start=(x,1.23,z-.07),end=(x,4.93,z-.07),color=dark))
    for k,y in enumerate([1.27,4.87]):
        add(bunks,f'Bed end {level} {k}',rod(.025,start=(-1.8,y,z-.07),end=(-.65,y,z-.07),color=dark))
    add(bunks,f'Pillow {level}',box((.77,.45,.13),(-1.26,4.43,z+.105),(.77,.77,.67)))
    # Irregular folded blankets create restrained soft-looking layers.
    add(bunks,f'Folded sheet {level}',box((.95,.42,.045),(-1.22,1.67,z+.07),(.66,.68,.60)))
add(bunks,'Front upright extending above beds',rod(.026,start=(-.64,1.23,.1),end=(-.64,1.23,2.65),color=dark))
scene.include('Three bunks',bunks)

bench = Asset('Port low bench')
add(bench,'Long green seat',box((.64,4.8,.095),(-1.57,.25,.45),green))
for i,y in enumerate([-1.9,.1,2.35]):
    for j,x in enumerate([-1.8,-1.34]):
        add(bench,f'Leg {i} {j}',box((.045,.05,.43),(x,y,.215),dark))
scene.include('Port bench',bench)

# Two ventilated metal equipment boxes dominate the lower left edge.
for idx,y in enumerate([-.72,.18]):
    cabinet = Asset(f'Port ventilated cabinet {idx}')
    add(cabinet,'Body',box((.53,.73,.83),(-1.60,y,.94),(.10,.16,.15)))
    add(cabinet,'Top lip',box((.59,.79,.045),(-1.60,y,1.375),(.12,.18,.16)))
    add(cabinet,'Front vent inset',box((.018,.58,.66),(-1.324,y,.96),(.035,.055,.052)))
    for k in range(15):
        add(cabinet,f'Vent louver {k}',box((.028,.57,.016),(-1.305,y,.65+k*.041),(.28,.33,.29)))
    for side in [-1,1]:
        add(cabinet,f'Frame {side}',box((.025,.035,.76),(-1.29,y+side*.32,.96),(.13,.20,.17)))
    scene.include(f'Vent cabinet {idx}',cabinet)

# Pale wall-mounted ventilation heater, seen high on the left.
heater = Asset('Port wall ventilation unit')
add(heater,'Enclosure',box((.25,.76,.86),(-1.75,.92,2.30),(.61,.62,.52)))
add(heater,'Dark grille opening',box((.025,.57,.52),(-1.612,.89,2.24),(.045,.060,.053)))
for i in range(6):
    slat=box((.045,.57,.036),(-1.585,.89,2.04+i*.079),(.65,.67,.58))
    add(heater,f'Horizontal grille slat {i}',slat)
add(heater,'Top control panel',box((.027,.43,.105),(-1.606,.94,2.63),(.43,.46,.39)))
scene.include('Wall ventilator',heater)

lockers = Asset('Rear silver lockers')
for j,x in enumerate([-.69,-.12,.45]):
    add(lockers,f'Cabinet body {j}',box((.55,.62,1.93),(x,6.20,1.16),(.45,.48,.44)))
    add(lockers,f'Door panel {j}',box((.505,.035,1.79),(x,5.868,1.17),(.49,.52,.48)))
    add(lockers,f'Door seam {j}',box((.012,.017,1.75),(x+.248,5.843,1.17),(.21,.24,.22)))
    add(lockers,f'Handle {j}',box((.035,.055,.14),(x+.15,5.82,1.25),(.16,.19,.17)))
    for k in range(5):
        add(lockers,f'Upper slot {j} {k}',box((.24,.012,.018),(x-.04,5.844,1.66+k*.055),(.23,.27,.24)))
    for k in range(3):
        add(lockers,f'Lower slot {j} {k}',box((.24,.012,.015),(x-.04,5.844,.53+k*.055),(.26,.30,.27)))
    add(lockers,f'Top storage roll {j}',rod(.15,start=(x-.20,6.16,2.23),end=(x+.18,6.16,2.23),color=(.42,.45,.39)))
scene.include('Rear lockers',lockers)

# A small utility chair in the aisle.
chair = Asset('Aisle chair')
cx,cy = -.25,4.32
add(chair,'Seat cushion',box((.47,.45,.075),(cx,cy,.48),(.47,.48,.39)))
for i,x in enumerate([cx-.21,cx+.21]):
    for j,y in enumerate([cy-.19,cy+.18]):
        add(chair,f'Chair leg {i} {j}',rod(.019,start=(x,y,.06),end=(x,y,.48),color=(.60,.61,.51)))
    add(chair,f'Back support {i}',rod(.022,start=(x,cy+.18,.43),end=(x,cy+.26,1.02),color=(.64,.65,.55)))
add(chair,'Back panel',box((.43,.055,.28),(cx,cy+.24,.86),(.37,.40,.33)))
for i,x in enumerate([cx-.25,cx+.25]):
    add(chair,f'Armrest {i}',rod(.022,start=(x,cy-.15,.68),end=(x,cy+.22,.68),color=(.64,.64,.53)))
scene.include('Chair',chair)

equipment = Asset('Central machinery enclosure')
add(equipment,'Gray machine chest',box((.74,.69,.89),(.79,4.66,.55),(.25,.28,.25)))
add(equipment,'Machine upper rim',box((.8,.75,.065),(.79,4.66,1.025),(.36,.38,.31)))
add(equipment,'Upper motor',rod(.17,length=.35,center=(.78,4.66,1.22),color=(.32,.34,.29)))
for i,x in enumerate([.27,1.24]):
    for j,y in enumerate([4.10,5.28]):
        add(equipment,f'Cage vertical {i} {j}',rod(.023,start=(x,y,.02),end=(x,y,2.61),color=dark))
for i,z in enumerate([.10,1.28,2.56]):
    add(equipment,f'Front cage bar {i}',rod(.021,start=(.27,4.10,z),end=(1.24,4.10,z),color=dark))
    add(equipment,f'Left cage bar {i}',rod(.021,start=(.27,4.10,z),end=(.27,5.28,z),color=dark))
add(equipment,'Machine pipe',rod(.035,start=(.75,4.66,1.27),end=(.75,4.66,2.65),color=(.38,.39,.31)))
scene.include('Machinery cage',equipment)

# Overhead service pipes: clear elbows, longitudinal runs, and hanging braces.
pipes = Asset('Overhead pipework')
for i,x in enumerate([-1.45,-.95,.22,.53]):
    add(pipes,f'Long service pipe {i}',rod(.035 if i<2 else .026,start=(x,-.8,2.88),end=(x,7.5,2.88),color=(.57,.59,.48)))
add(pipes,'Port curved water main',sweep_tube(
    points=[(-1.83,-1.4,2.92),(-1.63,-.6,2.92),(-1.22,.60,2.61),(-.92,1.7,2.61),(-.92,2.2,2.91)],
    radius=.047,color=(.73,.73,.61)))
add(pipes,'Cross room black main',rod(.035,start=(-1.8,4.48,2.72),end=(1.5,4.48,2.72),color=dark))
add(pipes,'Black main downpipe',rod(.034,start=(1.5,4.48,2.72),end=(1.5,4.48,.3),color=dark))
for i,y in enumerate([.5,2.65,4.8,6.6]):
    add(pipes,f'Pipe hanger {i}',rod(.014,start=(-.96,y,2.87),end=(-.96,y,3.25),color=(.24,.25,.20)))
for i,x in enumerate([.0,.48,.96]):
    add(pipes,f'Rear overhead branch {i}',sweep_tube(
        points=[(x,7.55,1.0),(x,7.55,2.7),(x,7.2,3.02),(x,5.8,3.02)],
        radius=.035,color=(.44,.47,.38)))
add(pipes,'Red valve stem',rod(.025,start=(-.53,3.6,2.15),end=(-.53,3.6,2.71),color=(.5,.08,.045)))
add(pipes,'Valve handle',rod(.017,start=(-.64,3.6,2.48),end=(-.42,3.6,2.48),color=(.65,.07,.03)))
scene.include('Pipes',pipes)

# Starboard fittings: dark notice board and bright red emergency wall telephone.
wallitems=Asset('Starboard bulkhead fittings')
add(wallitems,'Notice board frame',box((.065,1.05,.86),(1.862,3.55,2.02),(.36,.34,.25)))
add(wallitems,'Notice board face',box((.018,.95,.76),(1.82,3.55,2.02),(.23,.27,.25)))
add(wallitems,'White instruction sheet',box((.026,.45,.85),(1.86,2.28,1.77),(.76,.75,.64)))
add(wallitems,'Telephone mounting plate',box((.09,.37,.59),(1.80,2.79,1.30),(.67,.065,.035)))
add(wallitems,'Telephone lower body',box((.15,.28,.28),(1.70,2.79,1.16),(.78,.085,.045)))
add(wallitems,'Telephone receiver top',rod(.065,start=(1.66,2.68,1.55),end=(1.66,2.86,1.55),color=(.82,.09,.045)))
add(wallitems,'Telephone receiver grip',rod(.04,start=(1.65,2.68,1.33),end=(1.65,2.68,1.54),color=(.75,.055,.025)))
add(wallitems,'Telephone dial dark center',box((.02,.09,.12),(1.61,2.78,1.35),(.18,.14,.09)))
scene.include('Wall fittings',wallitems)

rightbench=Asset('Foreground starboard bench')
add(rightbench,'Green seat',box((.59,1.8,.075),(1.64,-.82,.51),(.045,.12,.095)))
for i,y in enumerate([-1.5,-.1]):
    for j,x in enumerate([1.40,1.86]):
        add(rightbench,f'Bench leg {i} {j}',rod(.025,start=(x,y,.02),end=(x,y,.48),color=dark))
scene.include('Right bench',rightbench)

# Hanging white enamel shades; each remains an editable assembly.
for i,(x,y,z,r) in enumerate([(-.72,-.12,2.86,.27),(-.42,3.12,2.79,.18),(-.13,5.67,2.76,.135)]):
    lamp=Asset(f'Pendant light {i}')
    add(lamp,'Suspension',rod(.014,start=(x,y,z+.06),end=(x,y,3.28),color=(.12,.15,.13)))
    add(lamp,'Shade dome',resized(ball(r,center=(x,y,z),color=(.83,.85,.77)),(1,1,.40)))
    add(lamp,'Luminous underside',rod(r*.94,length=.018,center=(x,y,z-.065),color=(1,1,.94)))
    add(lamp,'Dark socket',rod(.046,length=.105,center=(x,y,z+.12),color=(.18,.22,.18)))
    scene.include(f'Pendant {i}',lamp)

print('Primitive count:',sum(n.solid is not None for n in scene.traverse()))
realize(scene)
set_view(CAM,TARGET,lens=25,sensor=36)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.32,.27,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32

# Restrained deck variation, created procedurally without image textures.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.66
        base=bs.inputs['Base Color'].default_value
        if abs(base[0]-floor_color[0])<.035 and abs(base[1]-floor_color[1])<.035:
            bs.inputs['Roughness'].default_value=.36
            noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value=9
            noise.inputs['Detail'].default_value=2
            bump=mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.12
            bump.inputs['Distance'].default_value=.025
            mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
            mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

area_emitter((-.65,-.05,2.70),power=160,size=.52,target=(-.65,.5,0),color=(1,.91,.73))
area_emitter((-.38,3.10,2.66),power=120,size=.40,target=(0,3.5,.4),color=(.88,.95,1))
area_emitter((-.12,5.65,2.65),power=90,size=.35,target=(0,5.5,.5),color=(1,.96,.82))
area_emitter((0,-2.4,2.2),power=65,size=2.5,target=(0,3,1.3),color=(.85,.88,1))
sc.view_settings.view_transform='AgX'
