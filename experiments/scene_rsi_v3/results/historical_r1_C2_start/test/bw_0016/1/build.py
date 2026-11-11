# Reference inventory, estimated normalized image bounds:
# Foreground folding bench (.07,.32)-(.91,.98): warm hardboard top with
# dog holes, pale plywood rails, splayed legs and perforated folding panels,
# blue vise and diagonal handle, yellow blocks and clamps at the left end.
# Rear bench (0,.24)-(.90,.70): ochre top and irregular log-end mosaic,
# partly hidden by the foreground bench. Track saw at left, blue drill press,
# articulated lamp and CNC gantry router across its top.
# Background (0,0)-(1,.34): stacked lumber and dark shelves at left,
# corrugated wall, hanging tools, dark machinery and upright stock at right.
# Concrete floor fills the lower right. Hidden construction is uncertain.
#
# Review: the previous render placed the foreground bench too small and low,
# with too much floor and too little of its legs visible. The reference also
# has a darker, more densely occupied background. This revision uses a closer,
# lower viewpoint, larger plywood legs and a fuller lumber-storage area.
# Approximate expanded count: 190 log discs, 65 bench-hole markers,
# 35 wall ribs, 80 lumber and storage pieces, and 65 other primitives:
# approximately 435 meshes. No Boolean operations.

from sceneact import *
import bpy
import random

random.seed(13)
scene = Scene('Woodworking shop')
ply = (.72, .70, .63)
lightply = (.84, .83, .77)
edge = (.58, .43, .28)
brown = (.50, .31, .18)
dark = (.055, .055, .05)
steel = (.34, .36, .35)
blue = (.025, .15, .39)
yellow = (.95, .57, .015)
orange = (.85, .24, .02)

def add(asset, name, node):
    asset.include(name, node)

room = Asset('architecture')
add(room, 'concrete floor', box((18,16,.12), (0,0,-.08), (.34,.34,.32)))
add(room, 'back wall', box((18,.16,7), (0,3.12,3.45), (.17,.17,.15)))
for i in range(35):
    x = -.9 + i*.105
    add(room, 'corrugated wall rib %02d' % i,
        box((.033,.035,4.0), (x,3.015,2.7), (.105,.11,.105)))
scene.include('architecture', room)

bench = Asset('foreground folding workbench')
add(bench, 'hardboard top', box((3.85,1.18,.105), (0,-1.45,1.05), brown))
add(bench, 'front laminated edge', box((3.85,.035,.075), (0,-2.045,1.025), edge))
add(bench, 'left laminated edge', box((.035,1.18,.075), (-1.92,-1.45,1.025), edge))
for ix in range(12):
    for iy in range(3):
        x = -1.66 + ix*.30
        y = -1.84 + iy*.32
        add(bench, 'top dog hole %d %d' % (ix,iy),
            rod(.011, start=(x,y,1.104), end=(x,y,1.108),
                color=(.22,.16,.10)))

add(bench, 'front upper rail', box((3.55,.075,.075), (0,-2.00,.96), lightply))
add(bench, 'front lower apron', box((3.48,.10,.23), (0,-2.00,.72), lightply))
add(bench, 'rear upper rail', box((3.55,.075,.08), (0,-.92,.95), ply))
add(bench, 'under top shelf', box((3.25,.83,.055), (0,-1.46,.80), ply))
for x in (-1.40,-.30,.80,1.52):
    add(bench, 'yellow block %.2f' % x,
        box((.14,.19,.20), (x,-1.60,.90), yellow))
for x in (-1.47,1.47):
    for y in (-1.83,-1.04):
        leg = box((.30,.16,1.00),
                  (x+(-.10 if x < 0 else .10),y,.49), lightply)
        leg.turn(axis='y', degrees=(-9 if x < 0 else 9))
        add(bench, 'splayed leg %.2f %.2f' % (x,y), leg)
add(bench, 'right folding panel', box((.075,.76,.62), (1.48,-1.43,.48), ply))
add(bench, 'left folding panel', box((.075,.69,.61), (-1.48,-1.43,.46), ply))
for z in (.26,.36,.46,.56,.66):
    for y in (-1.72,-1.55,-1.38,-1.21):
        add(bench, 'right panel hole %.2f %.2f' % (z,y),
            rod(.012, start=(1.526,y,z), end=(1.531,y,z),
                color=(.26,.25,.22)))
        add(bench, 'left panel hole %.2f %.2f' % (z,y),
            rod(.012, start=(-1.526,y,z), end=(-1.531,y,z),
                color=(.26,.25,.22)))
for i in range(15):
    x = -1.20+i*.17
    add(bench, 'apron hole %02d' % i,
        rod(.013, start=(x,-2.055,.72), end=(x,-2.06,.72),
            color=(.27,.25,.22)))
add(bench, 'vise jaw', box((.48,.12,.24), (-.96,-2.10,.80), lightply))
add(bench, 'vise blue left', box((.19,.045,.105), (-1.08,-2.17,.79), blue))
add(bench, 'vise blue right', box((.18,.045,.105), (-.83,-2.17,.79), blue))
add(bench, 'vise screw', rod(.034, start=(-.96,-2.18,.79),
                             end=(-.96,-2.35,.79), color=steel))
add(bench, 'vise handle', rod(.022, start=(-1.15,-2.36,1.00),
                              end=(-.69,-2.36,.55), color=steel))
add(bench, 'vise upper tip', ball(.042, center=(-1.15,-2.36,1.00),
                                  color=(.45,.07,.06)))
add(bench, 'vise lower tip', ball(.042, center=(-.69,-2.36,.55),
                                  color=(.45,.07,.06)))
for i in range(3):
    x = -1.72+i*.10
    add(bench, 'clamp bar %d' % i,
        rod(.017, start=(x,-1.99,.77), end=(x-.05,-1.99,.14), color=steel))
    add(bench, 'clamp grip %d' % i,
        box((.07,.07,.14), (x-.05,-1.99,.20+i*.08),
            orange if i == 0 else dark))
    add(bench, 'clamp head %d' % i,
        box((.15,.07,.045), (x,-1.99,.74), dark))
scene.include('foreground bench', bench)

rear = Asset('rear log mosaic workbench')
add(rear, 'bench body', box((5.70,1.15,1.04), (-.35,1.25,.53), (.13,.10,.075)))
add(rear, 'warm timber top', box((5.85,1.27,.11), (-.35,1.25,1.10), (.62,.34,.09)))
add(rear, 'front top edge', box((5.85,.055,.08), (-.35,.60,1.08), (.74,.44,.14)))
wood_colors = [(.57,.42,.27),(.68,.55,.38),(.43,.31,.21),
               (.76,.66,.49),(.53,.43,.32)]
for row in range(5):
    for col in range(19):
        x = -3.12+col*.305+(row%2)*.14+random.uniform(-.025,.025)
        z = .12+row*.205+random.uniform(-.02,.02)
        r = random.uniform(.075,.13)
        add(rear, 'log bark %d %d' % (row,col),
            rod(r, start=(x,.575,z), end=(x,.55,z), color=(.12,.095,.075)))
        add(rear, 'log face %d %d' % (row,col),
            rod(r*.76, start=(x,.548,z), end=(x,.54,z),
                color=random.choice(wood_colors)))
scene.include('rear workbench', rear)

saw = Asset('track saw')
add(saw, 'guide rail', box((1.65,.14,.025), (-2.10,.93,1.18), (.58,.62,.60)))
add(saw, 'sole', box((.45,.30,.045), (-2.24,1.00,1.23), (.30,.32,.31)))
add(saw, 'motor housing', box((.34,.25,.22), (-2.25,1.00,1.36), (.68,.70,.67)))
add(saw, 'handle', box((.16,.10,.12), (-2.26,1.00,1.54), (.08,.10,.10)))
add(saw, 'green switch', box((.075,.055,.04), (-2.27,.94,1.61), (.25,.50,.11)))
scene.include('track saw', saw)

drill = Asset('blue drill press')
add(drill, 'base', box((.39,.31,.055), (-1.05,1.30,1.19), dark))
add(drill, 'upright column',
    rod(.032, start=(-1.05,1.34,1.21), end=(-1.05,1.34,1.91), color=steel))
add(drill, 'motor head', box((.27,.24,.19), (-1.05,1.30,1.87), blue))
add(drill, 'head cap', box((.23,.21,.045), (-1.05,1.30,1.98), dark))
add(drill, 'drill spindle',
    rod(.024, start=(-1.06,1.23,1.76), end=(-1.06,1.23,1.50), color=steel))
add(drill, 'work table', box((.25,.22,.035), (-1.05,1.27,1.49), blue))
add(drill, 'feed handle',
    rod(.014, start=(-.92,1.28,1.80), end=(-.75,1.28,1.70), color=dark))
scene.include('drill press', drill)

cnc = Asset('CNC gantry router')
add(cnc, 'dark bed', box((1.82,.88,.09), (.86,1.43,1.24), (.10,.10,.095)))
add(cnc, 'sacrificial board', box((1.46,.68,.04), (.90,1.43,1.31), (.68,.63,.53)))
for x in (.12,1.61):
    add(cnc, 'rail %.2f' % x, box((.08,.84,.065), (x,1.43,1.34), steel))
    add(cnc, 'gantry support %.2f' % x,
        box((.09,.10,.49), (x,1.43,1.54), (.14,.15,.15)))
add(cnc, 'gantry crossbeam', box((1.58,.11,.12), (.865,1.43,1.77), (.50,.51,.49)))
add(cnc, 'carriage', box((.22,.17,.20), (.94,1.35,1.69), dark))
add(cnc, 'router motor', box((.15,.14,.26), (.94,1.25,1.62), (.09,.10,.10)))
add(cnc, 'yellow collar', box((.16,.15,.055), (.94,1.25,1.73), yellow))
add(cnc, 'router bit',
    rod(.012, start=(.94,1.25,1.49), end=(.94,1.25,1.36), color=steel))
scene.include('CNC router', cnc)

lamp = Asset('articulated task lamp')
add(lamp, 'base', box((.22,.20,.035), (-.35,1.70,1.18), (.43,.43,.40)))
for name,a,b in [
    ('lower arm',(-.35,1.70,1.20),(-.48,1.70,1.91)),
    ('upper arm',(-.48,1.70,1.91),(-.08,1.70,2.25)),
    ('shade support',(-.08,1.70,2.25),(.05,1.70,2.13))]:
    add(lamp, name, rod(.014,start=a,end=b,color=(.67,.68,.65)))
add(lamp, 'shade', box((.25,.22,.12), (.06,1.70,2.10), (.66,.67,.63)))
scene.include('task lamp', lamp)

rack = Asset('wall lumber rack')
for x in (-3.15,-1.55):
    add(rack, 'upright %.2f' % x,
        box((.075,.48,2.85), (x,2.72,2.00), (.10,.09,.08)))
for z in (1.28,1.70,2.12,2.54,2.94,3.35):
    add(rack, 'shelf %.2f' % z,
        box((1.95,.54,.07), (-2.35,2.70,z), (.16,.13,.10)))
    for j in range(4):
        length = random.uniform(1.05,1.85)
        add(rack, 'lumber %.2f %d' % (z,j),
            box((length,.105,.065),
                (-2.35+random.uniform(-.08,.08),2.45+j*.13,z+.08+j*.018),
                random.choice([(.36,.22,.12),(.55,.35,.19),(.67,.49,.30)])))
for i in range(5):
    add(rack, 'loose plank %d' % i,
        box((1.8,.13,.055), (-2.15,1.87+i*.11,1.19+i*.035), (.50,.32,.17)))
scene.include('lumber rack', rack)

storage = Asset('stove and wall storage')
add(storage, 'stove body', box((.66,.50,.62), (2.53,2.37,1.42), (.075,.08,.075)))
add(storage, 'stove top', box((.75,.57,.07), (2.53,2.37,1.76), (.06,.065,.06)))
add(storage, 'stove door', box((.39,.025,.35), (2.53,2.105,1.40), (.13,.13,.12)))
add(storage, 'stove flue',
    rod(.09,start=(2.54,2.42,1.79),end=(2.54,2.42,3.12),color=(.08,.08,.075)))
for i in range(8):
    x = 3.00+i*.10
    add(storage, 'vertical stock %d' % i,
        rod(.018,start=(x,2.70,1.05),end=(x,2.70,2.63-(i%3)*.12),
            color=(.29,.29,.27)))
add(storage, 'stock rack base', box((1.0,.35,.08), (3.36,2.68,1.03), dark))
add(storage, 'tool cabinet', box((.72,.45,.84), (4.15,2.54,.57), (.13,.12,.10)))
for i in range(4):
    add(storage, 'red bin %d' % i,
        box((.15,.20,.12), (3.91+i*.18,2.30,1.08), (.48,.06,.025)))
for i in range(8):
    x = -.70+i*.11
    add(storage, 'hanging tool %d' % i,
        rod(.018,start=(x,2.99,2.17),end=(x,2.99,2.53+(i%3)*.07),
            color=(.09,.08,.07)))
scene.include('wall storage', storage)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.24,.23,.21,1)
background.inputs['Strength'].default_value = .32

set_view((-5.2,-8.8,3.65), (0,-.55,1.02), lens=66)
area_emitter((-1,-3,6.7), power=900, size=5, target=(0,0,0),
             color=(1.0,.84,.67))
area_emitter((-4,1,4.5), power=400, size=4, target=(0,0,1),
             color=(1.0,.90,.76))
area_emitter((.08,1.65,2.05), power=55, size=.45, target=(.3,1.1,1),
             color=(1.0,.80,.55))
