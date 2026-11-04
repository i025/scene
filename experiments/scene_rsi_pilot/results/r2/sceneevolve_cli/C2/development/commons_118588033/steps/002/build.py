from sceneact import *
import bpy

# Reference anchors: column foot (.72,.84); rear floor boundary near (.66,.69).
# Reference lamp center (.39,.16); bunks occupy roughly (.02,.35)-(.41,.73).
# Floor edges recede upward toward the rear machinery; ceiling runs converge centrally.
# Column overlaps the right bulkhead, leaving the red fire fitting visible.
# Corrections: reduce frontal fill; move bunks aisleward; move front lamp right/nearer.
# Camera and all other groups remain as in the successful first build.

scene = Scene('Ship machinery and sleeping compartment')
W, D, H = 3.6, 8.9, 3.15
CAMERA = (0.12, -4.7, 1.69)
TARGET = (-0.08, 2.7, 1.52)
LENS = 26
cream = (.65,.64,.49)
pale = (.74,.75,.66)
redfloor = (.30,.105,.065)
maroon = (.23,.075,.048)
dark = (.035,.05,.045)
green = (.055,.105,.085)

architecture = Asset('room shell')
architecture.include('deck', box((W,D,.12), center=(0,.25,-.06), color=redfloor))
architecture.include('port wall', box((.12,D,H), center=(-1.86,.25,H/2), color=cream))
architecture.include('starboard wall', box((.12,D,H), center=(1.86,.25,H/2), color=cream))
architecture.include('end bulkhead', box((W,.12,H), center=(0,4.72,H/2), color=pale))
architecture.include('ceiling', box((W,D,.12), center=(0,.25,H+.06), color=(.39,.34,.25)))
for x in (-1.79,1.79):
    architecture.include('base strip '+str(x), box((.035,D,.22), center=(x,.25,.11), color=maroon))
for y in (-3.3,-1.5,.35,2.15,4.1):
    architecture.include('ceiling rib '+str(y), box((W,.105,.20), center=(0,y,3), color=(.49,.39,.27)))
for x in (-1.15,-.43,.38,1.13):
    architecture.include('longitudinal beam '+str(x), box((.065,D,.13), center=(x,.25,3.05), color=(.55,.43,.30)))
scene.include('architecture', architecture)

column = Asset('foreground painted stanchion')
column.include('lower red shaft', rod(.105, start=(.88,-.92,.04), end=(.88,-.92,1.55), color=maroon))
column.include('upper cream shaft', rod(.105, start=(.88,-.92,1.55), end=(.88,-.92,3.16), color=(.73,.67,.48)))
column.include('foot', rod(.14, length=.045, center=(.88,-.92,.025), color=(.36,.21,.13)))
column.include('upper collar', rod(.14, length=.15, center=(.88,-.92,2.91), color=(.55,.46,.30)))
scene.include('column', column)

bunks = Asset('three tier port bunks')
for z in (.50,1.04,1.57):
    bunks.include('bed pan '+str(z), box((.74,3.55,.065), center=(-1.34,1.18,z), color=(.28,.32,.29)))
    bunks.include('white mattress '+str(z), box((.69,3.38,.105), center=(-1.32,1.20,z+.075), color=(.67,.68,.61)))
    bunks.include('pillow '+str(z), box((.57,.40,.14), center=(-1.32,2.53,z+.15), color=(.79,.79,.72)))
    bunks.include('outer lip '+str(z), box((.035,3.60,.08), center=(-.95,1.18,z+.025), color=(.46,.48,.41)))
for y in (-.66,1.02,2.98):
    bunks.include('upright '+str(y), rod(.023, start=(-.94,y,.08), end=(-.94,y,1.98), color=dark))
    bunks.include('wall upright '+str(y), rod(.021, start=(-1.73,y,.1), end=(-1.73,y,1.98), color=dark))
bunks.include('long upper rail', rod(.018, start=(-.94,-.66,1.98), end=(-.94,2.98,1.98), color=dark))
# +X moves every bunk edge right without altering tier spacing or perspective.
bunks.move((.25,0,0))
scene.include('bunks', bunks)

bench = Asset('low port green bench')
bench.include('seat', box((.49,5.05,.09), center=(-1.48,-.45,.31), color=green))
bench.include('front fascia', box((.045,5.05,.20), center=(-1.21,-.45,.22), color=(.075,.10,.075)))
for y in (-2.65,-.8,1.3):
    bench.include('leg '+str(y), box((.05,.055,.27), center=(-1.28,y,.135), color=dark))
scene.include('port bench', bench)

lockers = Asset('foreground ventilated metal cabinets')
for j,y in enumerate((-1.96,-1.24)):
    lockers.include('body '+str(j), box((.61,.63,.90), center=(-1.50,y,.83), color=(.105,.16,.15)))
    lockers.include('front panel '+str(j), box((.025,.55,.78), center=(-1.18,y,.84), color=(.15,.22,.21)))
    for k in range(15):
        lockers.include('vent %d %d'%(j,k), box((.014,.43,.014), center=(-1.162,y,.51+k*.041), color=(.035,.075,.071)))
    lockers.include('handle '+str(j), box((.027,.035,.12), center=(-1.139,y-.22,1.04), color=(.40,.43,.38)))
    lockers.include('top '+str(j), box((.66,.67,.035), center=(-1.49,y,1.30), color=(.16,.21,.19)))
scene.include('lockers', lockers)

vent = Asset('large cream wall ventilator')
vent.include('housing', box((.25,.69,.80), center=(-1.67,.20,2.12), color=(.66,.65,.53)))
vent.include('dark opening', box((.018,.52,.48), center=(-1.529,.20,2.10), color=(.055,.065,.057)))
for i in range(6):
    vent.include('louver '+str(i), box((.06,.55,.035), center=(-1.50,.20,1.90+i*.078), color=(.68,.68,.57)))
scene.include('ventilator', vent)

cage = Asset('black protective equipment frame')
for x in (-.68,.72):
    for y in (2.32,4.02):
        cage.include('post %s %s'%(x,y), rod(.022, start=(x,y,.02), end=(x,y,2.73), color=(.035,.039,.032)))
for z in (.06,1.06,2.73):
    cage.include('front crossbar '+str(z), rod(.018, start=(-.68,2.32,z), end=(.72,2.32,z), color=dark))
for x in (-.68,.72):
    cage.include('top longitudinal '+str(x), rod(.019, start=(x,2.32,2.73), end=(x,4.02,2.73), color=dark))
scene.include('equipment frame', cage)

machinery = Asset('rear silver electrical machinery')
machinery.include('main cabinet', box((.94,.60,1.59), center=(-.13,3.79,1.34), color=(.47,.51,.48)))
machinery.include('cabinet top', box((1.02,.65,.07), center=(-.13,3.79,2.16), color=(.57,.59,.52)))
for x in (-.39,.08):
    machinery.include('door '+str(x), box((.42,.028,1.44), center=(x,3.474,1.37), color=(.52,.55,.50)))
    machinery.include('door handle '+str(x), rod(.014, start=(x+.13,3.443,1.32), end=(x+.13,3.443,1.55), color=(.16,.19,.17)))
    for i in range(6):
        machinery.include('cabinet vents %s %s'%(x,i), box((.18,.015,.016), center=(x-.035,3.449,1.61+i*.055), color=(.31,.35,.32)))
for x in (-.42,-.08,.26):
    machinery.include('top fitting '+str(x), rod(.085, length=.12, center=(x,3.77,2.24), color=(.28,.32,.28)))
machinery.include('foreground machine body', box((.69,.64,.81), center=(.48,2.98,.58), color=(.25,.29,.25)))
machinery.include('machine upper deck', box((.77,.70,.08), center=(.48,2.98,1.02), color=(.36,.38,.31)))
machinery.include('small pump', rod(.17, length=.36, center=(.52,3.06,1.23), color=(.25,.30,.27)))
for x in (.28,.65):
    machinery.include('pipe '+str(x), rod(.029, start=(x,3.08,1.15), end=(x,3.08,2.13), color=(.50,.47,.32)))
scene.include('machinery', machinery)

chair = Asset('small cream metal chair')
for x in (-.47,-.04):
    for y in (2.19,2.63):
        chair.include('leg %s %s'%(x,y), rod(.017, start=(x,y,.03), end=(x,y,.51), color=(.58,.58,.45)))
chair.include('seat', box((.48,.49,.055), center=(-.255,2.40,.51), color=(.28,.29,.22)))
for x in (-.48,-.03):
    chair.include('back post '+str(x), rod(.018, start=(x,2.65,.40), end=(x,2.75,.99), color=(.62,.61,.48)))
chair.include('back rest', box((.43,.055,.26), center=(-.255,2.73,.88), color=(.31,.32,.25)))
chair.include('right arm', rod(.018, start=(-.01,2.22,.73), end=(-.01,2.65,.73), color=(.65,.64,.51)))
scene.include('chair', chair)

pipes = Asset('overhead and bulkhead pipes')
for i,x in enumerate((-.99,-.69,.42,.68)):
    pipes.include('ceiling run '+str(i), rod(.032 if i<2 else .045, start=(x,-3.8,2.72+i*.065), end=(x,4.48,2.72+i*.065), color=(.59,.61,.52)))
for y in (-1.8,.45,2.55):
    pipes.include('cross pipe '+str(y), rod(.035, start=(-1.7,y,2.67), end=(1.75,y,2.67), color=(.59,.60,.52)))
    pipes.include('hanger '+str(y), rod(.012, start=(-.73,y,2.70), end=(-.73,y,3.12), color=dark))
pipes.include('rear black riser', rod(.033, start=(.69,4.39,.21), end=(.69,4.39,2.82), color=dark))
pipes.include('rear horizontal black pipe', rod(.034, start=(-1.73,4.39,2.82), end=(.69,4.39,2.82), color=dark))
for x in (-.47,.1,.48):
    pipes.include('rear cream pipe '+str(x), rod(.039, start=(x,4.52,2.13), end=(x,4.52,3.12), color=(.63,.63,.49)))
scene.include('pipes', pipes)

wall_items = Asset('right bulkhead fittings')
wall_items.include('dark notice board', box((.045,.92,.74), center=(1.772,2.11,1.83), color=(.20,.24,.21)))
wall_items.include('board upper border', box((.055,.96,.035), center=(1.745,2.11,2.21), color=(.40,.41,.33)))
wall_items.include('white chart', box((.025,.61,.97), center=(1.765,.48,1.78), color=(.76,.75,.66)))
wall_items.include('fire equipment red backing', box((.13,.41,.65), center=(1.68,.84,1.12), color=(.70,.055,.025)))
wall_items.include('red curved housing', rod(.14, length=.40, center=(1.58,.84,1.15), color=(.81,.085,.035)))
wall_items.include('fire box pale label', box((.025,.12,.19), center=(1.425,.84,1.24), color=(.82,.75,.55)))
wall_items.include('fire box dark nozzle', rod(.036, start=(1.47,.84,1.42), end=(1.47,.84,1.55), color=dark))
scene.include('wall fittings', wall_items)

rightbench = Asset('cropped starboard bench')
rightbench.include('seat', box((.51,2,.075), center=(1.53,-2.67,.43), color=(.035,.085,.065)))
for y in (-3.35,-1.96):
    rightbench.include('legs '+str(y), rod(.021, start=(1.34,y,.02), end=(1.34,y,.40), color=dark))
scene.include('right bench', rightbench)

lamps = Asset('hanging lamps')
# Rightward movement offsets the nearer lamp's leftward perspective expansion.
# Bringing this above-eye fixture nearer moves it upward and enlarges its silhouette.
lamp_positions = [(-.34,-1.80,2.64),(-.43,1.83,2.68),(-.28,3.58,2.69)]
for i,(x,y,z) in enumerate(lamp_positions):
    lamps.include('stem '+str(i), rod(.024, start=(x,y,z+.10), end=(x,y,3.13), color=(.26,.28,.23)))
    lamps.include('shade '+str(i), rod(.18 if i==0 else .135, length=.085, center=(x,y,z), color=(.68,.71,.64)))
    lamps.include('glowing underside '+str(i), rod(.167 if i==0 else .125, length=.014, center=(x,y,z-.05), color=(1,.98,.85)))
scene.include('lamps', lamps)

realize(scene)
set_view(CAMERA, TARGET, lens=LENS, sensor=32)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.48,.49,.42,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .30
for i,(x,y,z) in enumerate(lamp_positions):
    area_emitter((x,y,z-.085), power=100 if i==0 else 70, size=.46,
                 target=(x,y,.1), color=(1,.92,.75))
# Lower frontal fill deepens shadows while retaining the existing overhead light.
area_emitter((0,-3.3,2.45), power=55, size=2.2, target=(0,1.2,.9), color=(.78,.83,1))
area_emitter((.8,2.8,2.7), power=80, size=1.5, target=(-.8,2.3,.8), color=(1,.96,.80))
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = 0
for mat in bpy.data.materials:
    if mat.use_nodes:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Roughness'].default_value = .73
