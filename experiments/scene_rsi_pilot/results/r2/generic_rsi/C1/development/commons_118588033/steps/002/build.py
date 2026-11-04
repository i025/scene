from sceneact import *
import bpy

# Comparison anchors: foreground column, berth front upright, locker tops,
# machinery chest, pendant shade, and right wall fittings.
# The first build placed most aisle edges reasonably, but its pale illumination
# flattened the dark compartment. Keep the camera fixed; deepen the palette.
# Local silhouette corrections raise the berth mattresses and locker tops.
# A transverse starboard bulkhead exposes the board and telephone to the camera.
CAM = (0, -3, 1.66)
TARGET = (-.08, 4.7, 1.64)

scene = Scene('Ship accommodation compartment')
cream = (.40,.42,.34)
pale = (.57,.56,.45)
red = (.23,.062,.037)
deck = (.26,.075,.043)
dark = (.035,.048,.040)
green = (.025,.075,.059)
linen = (.49,.51,.44)

def put(a,n,g):
    a.include(n,g)

architecture = Asset('Compartment architecture')
put(architecture,'Painted steel deck',box((4,11,.12),(0,2.7,-.06),deck))
put(architecture,'Port bulkhead',box((.16,9.2,3.3),(-1.98,3.1,1.65),cream))
put(architecture,'Starboard longitudinal bulkhead',box((.16,8.3,3.3),(1.98,3.65,1.65),pale))
put(architecture,'Rear bulkhead',box((4,.14,3.3),(0,7.72,1.65),cream))
put(architecture,'Ceiling',box((4,10,.14),(0,2.8,3.36),(.19,.16,.105)))
# The visible right wall is a return rather than a nearly edge-on wall.
put(architecture,'Starboard transverse return',box((.94,.13,3.3),(1.52,3.75,1.65),pale))
put(architecture,'Return lower red paint',box((.94,.024,.43),(1.52,3.674,.215),red))
for side in (-1,1):
    put(architecture,f'Lower wall paint {side}',box((.035,9,.43),(side*1.885,3,.215),red))
    put(architecture,f'Skirting {side}',box((.07,9,.065),(side*1.87,3,.045),(.16,.071,.035)))
for i,y in enumerate([-.9,.8,2.7,4.6,6.6]):
    put(architecture,f'Transverse beam {i}',box((3.9,.17,.28),(0,y,3.12),(.34,.22,.12)))
for i,x in enumerate([-1.55,-.88,-.15,.65,1.45]):
    put(architecture,f'Longitudinal beam {i}',box((.085,8.7,.11),(x,3,3.22),(.32,.20,.105)))
scene.include('Architecture',architecture)

pillar = Asset('Foreground supporting column')
px,py = .87,.64
put(pillar,'Lower oxblood shaft',rod(.108,start=(px,py,.05),end=(px,py,1.40),color=red))
put(pillar,'Upper cream shaft',rod(.112,start=(px,py,1.40),end=(px,py,3.28),color=(.59,.49,.29)))
put(pillar,'Deck collar',rod(.145,length=.045,center=(px,py,.035),color=(.33,.16,.075)))
put(pillar,'Overhead collar',rod(.15,length=.14,center=(px,py,3.16),color=(.39,.25,.12)))
scene.include('Main pillar',pillar)

bunks = Asset('Port triple berth')
for i,y in enumerate([1.3,4.85]):
    for j,x in enumerate([-1.82,-.65]):
        put(bunks,f'Post {i} {j}',rod(.025,start=(x,y,.18),end=(x,y,2.48),color=dark))
for level,z in enumerate([.91,1.43,1.98]):
    put(bunks,f'Canvas mattress {level}',box((1.11,3.48,.085),(-1.23,3.05,z),linen))
    put(bunks,f'Rounded canvas front {level}',rod(.045,start=(-1.76,1.29,z+.015),end=(-.70,1.29,z+.015),color=(.60,.62,.54)))
    for side,x in enumerate([-1.80,-.67]):
        put(bunks,f'Long rail {level} {side}',rod(.023,start=(x,1.23,z-.07),end=(x,4.93,z-.07),color=dark))
    for k,y in enumerate([1.27,4.87]):
        put(bunks,f'End rail {level} {k}',rod(.023,start=(-1.8,y,z-.07),end=(-.65,y,z-.07),color=dark))
    put(bunks,f'Pillow {level}',box((.77,.45,.12),(-1.26,4.43,z+.09),(.63,.64,.55)))
    put(bunks,f'Folded sheet {level}',box((.95,.42,.035),(-1.22,1.67,z+.055),(.53,.55,.47)))
put(bunks,'Front tall upright',rod(.026,start=(-.64,1.23,.1),end=(-.64,1.23,2.65),color=dark))
scene.include('Three bunks',bunks)

bench = Asset('Port low bench')
put(bench,'Green seat',box((.64,4.8,.095),(-1.57,.25,.45),green))
for i,y in enumerate([-1.9,.1,2.35]):
    for j,x in enumerate([-1.8,-1.34]):
        put(bench,f'Leg {i} {j}',box((.045,.05,.43),(x,y,.215),dark))
scene.include('Port bench',bench)

for idx,y in enumerate([-.72,.18]):
    a=Asset(f'Port ventilated cabinet {idx}')
    put(a,'Body',box((.53,.73,.83),(-1.60,y,.94),(.055,.10,.085)))
    put(a,'Top lip',box((.59,.79,.045),(-1.60,y,1.375),(.065,.12,.095)))
    put(a,'Vent recess',box((.018,.58,.66),(-1.324,y,.96),(.018,.033,.028)))
    for k in range(15):
        put(a,f'Louver {k}',box((.028,.57,.016),(-1.305,y,.65+k*.041),(.16,.23,.19)))
    for side in (-1,1):
        put(a,f'Frame {side}',box((.025,.035,.76),(-1.29,y+side*.32,.96),(.075,.13,.10)))
    scene.include(f'Vent cabinet {idx}',a)

heater=Asset('Port wall ventilation unit')
put(heater,'Enclosure',box((.25,.76,.86),(-1.75,.92,2.30),(.43,.46,.37)))
put(heater,'Dark opening',box((.025,.57,.52),(-1.612,.89,2.24),(.025,.037,.028)))
for i in range(6):
    put(heater,f'Grille slat {i}',box((.045,.57,.036),(-1.585,.89,2.04+i*.079),(.51,.54,.44)))
put(heater,'Control panel',box((.027,.43,.105),(-1.606,.94,2.63),(.29,.32,.25)))
scene.include('Wall ventilator',heater)

lockers=Asset('Rear silver lockers')
for j,x in enumerate([-.69,-.12,.45]):
    put(lockers,f'Body {j}',box((.55,.62,2.20),(x,6.20,1.295),(.30,.34,.30)))
    put(lockers,f'Door {j}',box((.505,.035,2.06),(x,5.868,1.305),(.36,.40,.36)))
    put(lockers,f'Seam {j}',box((.012,.017,2.02),(x+.248,5.843,1.305),(.13,.17,.14)))
    put(lockers,f'Handle {j}',box((.035,.055,.14),(x+.15,5.82,1.25),(.10,.13,.10)))
    for k in range(5):
        put(lockers,f'Upper vent {j} {k}',box((.24,.012,.018),(x-.04,5.844,1.88+k*.055),(.18,.23,.19)))
    for k in range(3):
        put(lockers,f'Lower vent {j} {k}',box((.24,.012,.015),(x-.04,5.844,.53+k*.055),(.18,.23,.19)))
    put(lockers,f'Stored roll {j}',rod(.15,start=(x-.20,6.16,2.50),end=(x+.18,6.16,2.50),color=(.26,.30,.24)))
scene.include('Rear lockers',lockers)

chair=Asset('Aisle chair')
cx,cy=-.25,4.32
put(chair,'Seat',box((.47,.45,.075),(cx,cy,.48),(.31,.34,.26)))
for i,x in enumerate([cx-.21,cx+.21]):
    for j,y in enumerate([cy-.19,cy+.18]):
        put(chair,f'Leg {i} {j}',rod(.019,start=(x,y,.06),end=(x,y,.48),color=(.42,.45,.35)))
    put(chair,f'Back support {i}',rod(.022,start=(x,cy+.18,.43),end=(x,cy+.26,1.02),color=(.46,.49,.38)))
put(chair,'Back panel',box((.43,.055,.28),(cx,cy+.24,.86),(.22,.27,.20)))
for i,x in enumerate([cx-.25,cx+.25]):
    put(chair,f'Arm {i}',rod(.022,start=(x,cy-.15,.68),end=(x,cy+.22,.68),color=(.46,.48,.36)))
scene.include('Chair',chair)

equipment=Asset('Central machinery enclosure')
put(equipment,'Machine chest',box((.74,.69,.89),(.79,4.66,.55),(.16,.19,.16)))
put(equipment,'Upper rim',box((.8,.75,.065),(.79,4.66,1.025),(.24,.27,.20)))
put(equipment,'Motor',rod(.17,length=.35,center=(.78,4.66,1.22),color=(.20,.23,.17)))
for i,x in enumerate([.27,1.24]):
    for j,y in enumerate([4.10,5.28]):
        put(equipment,f'Cage upright {i} {j}',rod(.023,start=(x,y,.02),end=(x,y,2.61),color=dark))
for i,z in enumerate([.10,1.28,2.56]):
    put(equipment,f'Front cage rail {i}',rod(.021,start=(.27,4.10,z),end=(1.24,4.10,z),color=dark))
    put(equipment,f'Left cage rail {i}',rod(.021,start=(.27,4.10,z),end=(.27,5.28,z),color=dark))
put(equipment,'Machine pipe',rod(.035,start=(.75,4.66,1.27),end=(.75,4.66,2.65),color=(.26,.29,.21)))
scene.include('Machinery cage',equipment)

pipes=Asset('Overhead pipework')
for i,x in enumerate([-1.45,-.95,.22,.53]):
    put(pipes,f'Long service pipe {i}',rod(.035 if i<2 else .026,start=(x,-.8,2.88),end=(x,7.5,2.88),color=(.43,.47,.36)))
put(pipes,'Port curved water main',sweep_tube(points=[
    (-1.83,-1.4,2.92),(-1.63,-.6,2.92),(-1.22,.60,2.61),
    (-.92,1.7,2.61),(-.92,2.2,2.91)],radius=.047,color=(.58,.61,.48)))
put(pipes,'Cross room black main',rod(.035,start=(-1.8,4.48,2.72),end=(1.5,4.48,2.72),color=dark))
put(pipes,'Black downpipe',rod(.034,start=(1.5,4.48,2.72),end=(1.5,4.48,.3),color=dark))
for i,y in enumerate([.5,2.65,4.8,6.6]):
    put(pipes,f'Hanger {i}',rod(.014,start=(-.96,y,2.87),end=(-.96,y,3.25),color=(.15,.18,.12)))
for i,x in enumerate([0,.48,.96]):
    put(pipes,f'Rear branch {i}',sweep_tube(points=[
        (x,7.55,1),(x,7.55,2.7),(x,7.2,3.02),(x,5.8,3.02)],
        radius=.035,color=(.30,.35,.25)))
put(pipes,'Red valve stem',rod(.025,start=(-.53,3.6,2.15),end=(-.53,3.6,2.71),color=(.43,.035,.018)))
put(pipes,'Valve handle',rod(.017,start=(-.64,3.6,2.48),end=(-.42,3.6,2.48),color=(.61,.035,.015)))
scene.include('Pipes',pipes)

wallitems=Asset('Starboard bulkhead fittings')
put(wallitems,'Board frame',box((.63,.06,.86),(1.57,3.64,2.05),(.26,.24,.16)))
put(wallitems,'Dark notice board',box((.56,.018,.77),(1.57,3.599,2.05),(.13,.18,.16)))
put(wallitems,'Instruction placard',box((.30,.025,.77),(1.99,3.64,1.73),(.66,.65,.54)))
put(wallitems,'Telephone backing',box((.32,.07,.58),(1.43,3.59,1.23),(.59,.025,.012)))
put(wallitems,'Telephone lower box',box((.27,.14,.25),(1.43,3.50,1.08),(.71,.035,.018)))
put(wallitems,'Receiver bridge',rod(.057,start=(1.34,3.44,1.46),end=(1.52,3.44,1.46),color=(.76,.035,.018)))
for i,x in enumerate([1.34,1.52]):
    put(wallitems,f'Receiver end {i}',rod(.046,start=(x,3.44,1.32),end=(x,3.44,1.46),color=(.72,.025,.01)))
put(wallitems,'Dial',rod(.061,length=.018,center=(1.43,3.414,1.24),axis='+y',color=(.19,.12,.06)))
scene.include('Wall fittings',wallitems)

rightbench=Asset('Foreground starboard bench')
put(rightbench,'Green seat',box((.59,1.8,.075),(1.64,-.82,.51),green))
for i,y in enumerate([-1.5,-.1]):
    for j,x in enumerate([1.40,1.86]):
        put(rightbench,f'Leg {i} {j}',rod(.025,start=(x,y,.02),end=(x,y,.48),color=dark))
scene.include('Right bench',rightbench)

for i,(x,y,z,r) in enumerate([
    (-.37,-.12,3.01,.235),(-.27,3.12,2.79,.16),(-.13,5.67,2.76,.135)]):
    a=Asset(f'Pendant light {i}')
    put(a,'Suspension',rod(.014,start=(x,y,z+.06),end=(x,y,3.28),color=(.08,.11,.08)))
    put(a,'Enamel shade',resized(ball(r,center=(x,y,z),color=(.77,.81,.72)),(1,1,.40)))
    put(a,'Bright underside',rod(r*.94,length=.018,center=(x,y,z-.065),color=(1,1,.94)))
    put(a,'Socket',rod(.04,length=.09,center=(x,y,z+.11),color=(.11,.16,.11)))
    scene.include(f'Pendant {i}',a)

print('Primitive count:',sum(n.solid is not None for n in scene.traverse()))
realize(scene)
set_view(CAM,TARGET,lens=25,sensor=36)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value=(.22,.25,.19,1)
bg.inputs['Strength'].default_value=.16

for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:
        continue
    bs.inputs['Roughness'].default_value=.65
    c=bs.inputs['Base Color'].default_value
    if abs(c[0]-deck[0])<.025 and abs(c[1]-deck[1])<.025:
        bs.inputs['Roughness'].default_value=.30
        noise=mat.node_tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=9
        noise.inputs['Detail'].default_value=2
        bump=mat.node_tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.10
        bump.inputs['Distance'].default_value=.018
        mat.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        mat.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if c[0]>.95 and c[1]>.95:
        bs.inputs['Emission Color'].default_value=(.85,.94,1,1)
        bs.inputs['Emission Strength'].default_value=2.5

area_emitter((-.37,-.12,2.86),power=95,size=.43,target=(-.5,.7,0),color=(1,.90,.73))
area_emitter((-.27,3.10,2.66),power=80,size=.34,target=(-.2,3.5,.4),color=(.84,.94,1))
area_emitter((-.12,5.65,2.65),power=55,size=.30,target=(0,5.5,.5),color=(.95,1,.84))
area_emitter((0,-2.4,2.2),power=23,size=2.5,target=(0,3,1.3),color=(.86,.90,1))
sc.view_settings.view_transform='AgX'
