# Reference inventory (normalized image bounds, approximate):
# Foreground folding bench (0.07,0.32)-(0.91,0.98): broad brown top with
# small dog holes, pale apron and splayed perforated legs, blue front vise,
# yellow stops, and clamps hanging at left. Rear parts are partly occluded.
# Long rear bench (0,0.25)-(0.90,0.70): ochre work surface and log-end
# mosaic front, overlapped by foreground bench. Track saw at left, blue drill
# press near center-left, CNC router and lamp on right.
# Back wall (0,0)-(1,0.32): lumber shelving at left, vertical corrugated
# wall, hanging tools, dark stove/cabinet and racks at right. Floor is gray.
# Estimates are from the single photograph; hidden construction is uncertain.
# Expanded primitive estimate: approximately 290 meshes, mostly log ends,
# shelving, tools and bench perforation markers. No Boolean operations.

from sceneact import *
import bpy
import math
import random

random.seed(13)
scene = Scene('Woodworking shop')

# Shared palette
ply = (0.79, 0.77, 0.69)
ply_light = (0.88, 0.86, 0.79)
ply_edge = (0.61, 0.53, 0.40)
top = (0.56, 0.36, 0.20)
top_edge = (0.70, 0.49, 0.28)
dark = (0.075, 0.078, 0.075)
black = (0.035, 0.040, 0.039)
steel = (0.39, 0.41, 0.39)
blue = (0.035, 0.21, 0.49)
yellow = (0.96, 0.62, 0.025)
orange = (0.90, 0.31, 0.025)

def add(asset, name, node):
    asset.include(name, node)

# Floor and industrial walls
room = Asset('architecture')
add(room, 'concrete floor', box((15, 13, .12), (0, 0, -.08), (.42, .42, .39)))
add(room, 'back wall', box((13, .15, 4.2), (0, 3.12, 2.05), (.31, .30, .26)))
add(room, 'right wall', box((.13, 7, 4.2), (5.3, -.3, 2.05), (.35, .34, .29)))
# Corrugations on the visible wall.
for i in range(27):
    x = -0.65 + i * .105
    add(room, 'wall rib %02d' % i, box((.028, .025, 2.65), (x, 3.025, 2.18), (.20, .21, .20)))
scene.include('architecture', room)

# Foreground bench. X is the length, Y is depth.
bench = Asset('foreground folding workbench')
add(bench, 'hardboard top', box((3.85, 1.18, .105), (0, -1.45, 1.02), top))
add(bench, 'exposed laminated front edge', box((3.85, .035, .075), (0, -2.045, .995), top_edge))
add(bench, 'exposed laminated end edge', box((.035, 1.18, .075), (1.92, -1.45, .995), top_edge))
# Dog holes: restrained dark shallow discs on surface.
for ix in range(12):
    for iy in range(3):
        x = -1.66 + ix * .30
        y = -1.84 + iy * .32
        add(bench, 'top dog hole %d %d' % (ix,iy),
            rod(.011, start=(x,y,1.074), end=(x,y,1.078), color=(.29,.22,.15)))
# Front and back aprons, long pale structural rails.
add(bench, 'front apron', box((3.54, .095, .28), (0, -1.99, .79), ply_light))
add(bench, 'rear apron', box((3.54, .085, .22), (0, -.94, .83), ply))
add(bench, 'left end apron', box((.10, 1.0, .20), (-1.73, -1.47, .82), ply))
add(bench, 'right end apron', box((.10, 1.0, .20), (1.73, -1.47, .82), ply))
# Long narrow shelf and open top compartment beneath the worktop.
add(bench, 'under top shelf', box((2.75,.66,.055), (.02,-1.48,.79), ply_light))
for x in (-1.20, .15, 1.30):
    add(bench, 'yellow bench stop %.2f'%x, box((.13,.16,.22), (x,-1.48,.90), yellow))
# Four angled legs: boxes rotated around Y to give splayed front silhouette.
for x in (-1.46, 1.46):
    for y in (-1.84, -1.03):
        leg = box((.20,.16,1.01), (x + (-.10 if x < 0 else .10),y,.47), ply_light)
        leg.turn(axis='y', degrees=(-9 if x < 0 else 9))
        add(bench, 'splayed leg %.2f %.2f'%(x,y), leg)
# Panel between right-side legs, with visible perforations.
add(bench, 'right folding panel', box((.075,.77,.60), (1.48,-1.43,.47), ply))
for z in (.29,.39,.49,.59,.69):
    for y in (-1.70,-1.53,-1.36,-1.19):
        add(bench, 'right panel hole %.2f %.2f'%(z,y),
            rod(.012, start=(1.525,y,z), end=(1.53,y,z), color=(.32,.30,.26)))
# Small front apron holes.
for i in range(16):
    x = -1.25 + i*.17
    add(bench, 'apron hole %02d'%i,
        rod(.013, start=(x,-2.045,.79), end=(x,-2.05,.79), color=(.29,.28,.25)))
# Vise at front left: pale jaw, two blue cast sections and steel screw handle.
add(bench, 'vise wooden jaw', box((.48,.105,.23), (-.98,-2.10,.79), ply_light))
add(bench, 'vise left blue plate', box((.18,.045,.10), (-1.09,-2.17,.78), blue))
add(bench, 'vise right blue plate', box((.18,.045,.10), (-.84,-2.17,.78), blue))
add(bench, 'vise screw', rod(.035, start=(-.96,-2.16,.79), end=(-.96,-2.36,.79), color=steel))
add(bench, 'vise handle', rod(.025, start=(-1.17,-2.36,1.00), end=(-.72,-2.36,.54), color=(.29,.26,.24)))
add(bench, 'vise handle tip', ball(.047, center=(-.72,-2.36,.54), color=(.48,.08,.07)))
# Clamps hanging along left leg.
for i in range(3):
    x = -1.70 + i*.10
    add(bench, 'hanging clamp bar %d'%i, rod(.017, start=(x,-1.98,.76), end=(x-.05,-1.98,.14), color=steel))
    add(bench, 'hanging clamp grip %d'%i, box((.07,.07,.14), (x-.05,-1.98,.20+i*.08), orange if i==0 else dark))
    add(bench, 'hanging clamp head %d'%i, box((.15,.07,.045), (x,-1.98,.73), dark))
scene.include('foreground bench', bench)

# Rear long workbench and its log-end face.
rear = Asset('rear log mosaic workbench')
add(rear, 'solid bench body', box((5.70,1.15,1.04), (-.35,1.25,.53), (.21,.17,.12)))
add(rear, 'worktop', box((5.85,1.27,.11), (-.35,1.25,1.10), (.66,.38,.11)))
add(rear, 'front edge', box((5.85,.055,.08), (-.35,.60,1.08), (.80,.52,.19)))
# Visible round cut ends form an irregular, dense mosaic. Randomized, shared colors.
wood_colors = [(.57,.42,.27),(.68,.55,.38),(.43,.31,.21),(.76,.66,.49),(.53,.43,.32)]
for row in range(5):
    for col in range(19):
        x = -3.12 + col*.305 + (row%2)*.14 + random.uniform(-.025,.025)
        z = .12 + row*.205 + random.uniform(-.02,.02)
        r = random.uniform(.073,.128)
        add(rear, 'log bark %d %d'%(row,col),
            rod(r, start=(x,.575,z), end=(x,.55,z), color=(.16,.13,.105)))
        add(rear, 'log cut face %d %d'%(row,col),
            rod(r*.76, start=(x,.548,z), end=(x,.54,z), color=random.choice(wood_colors)))
scene.include('rear workbench', rear)

# Track saw and its guide on the rear left.
saw = Asset('track saw')
add(saw, 'guide rail', box((1.65,.14,.025), (-2.10,.93,1.18), (.63,.66,.65)))
add(saw, 'saw sole', box((.45,.30,.045), (-2.24,1.00,1.23), (.33,.35,.34)))
add(saw, 'motor housing', box((.34,.25,.22), (-2.25,1.00,1.36), (.68,.70,.67)))
add(saw, 'dark handle', box((.16,.10,.12), (-2.26,1.00,1.54), (.08,.10,.10)))
add(saw, 'green switch', box((.075,.055,.04), (-2.27,.94,1.61), (.25,.50,.11)))
scene.include('track saw', saw)

# Blue drill press.
drill = Asset('blue drill press')
add(drill, 'base', box((.39,.31,.055), (-1.05,1.30,1.19), dark))
add(drill, 'upright column', rod(.032, start=(-1.05,1.34,1.21), end=(-1.05,1.34,1.91), color=steel))
add(drill, 'motor head', box((.27,.24,.19), (-1.05,1.30,1.87), blue))
add(drill, 'head cap', box((.23,.21,.045), (-1.05,1.30,1.98), dark))
add(drill, 'drill spindle', rod(.024, start=(-1.06,1.23,1.76), end=(-1.06,1.23,1.50), color=steel))
add(drill, 'small work table', box((.25,.22,.035), (-1.05,1.27,1.49), blue))
add(drill, 'feed handle', rod(.014, start=(-.92,1.28,1.80), end=(-.75,1.28,1.70), color=dark))
scene.include('drill press', drill)

# CNC router: bed, two side supports, cross gantry, carriage and spindle.
cnc = Asset('CNC gantry router')
add(cnc, 'dark bed', box((1.82,.88,.09), (.86,1.43,1.24), (.12,.12,.11)))
add(cnc, 'sacrificial board', box((1.46,.68,.04), (.90,1.43,1.31), (.72,.67,.56)))
for x in (.12,1.61):
    add(cnc, 'rail %.2f'%x, box((.08,.84,.065), (x,1.43,1.34), steel))
    add(cnc, 'gantry support %.2f'%x, box((.09,.10,.49), (x,1.43,1.54), (.17,.18,.18)))
add(cnc, 'gantry crossbeam', box((1.58,.11,.12), (.865,1.43,1.77), (.58,.59,.56)))
add(cnc, 'carriage', box((.22,.17,.20), (.94,1.35,1.69), dark))
add(cnc, 'router motor', box((.15,.14,.26), (.94,1.25,1.62), (.12,.13,.13)))
add(cnc, 'router yellow collar', box((.16,.15,.055), (.94,1.25,1.73), yellow))
add(cnc, 'router bit', rod(.012, start=(.94,1.25,1.49), end=(.94,1.25,1.36), color=steel))
scene.include('CNC router', cnc)

# Articulated task lamp behind the machinery.
lamp = Asset('articulated task lamp')
add(lamp, 'lamp base', box((.22,.20,.035), (-.35,1.70,1.18), (.43,.43,.40)))
for name,a,b in [
    ('lower arm',(-.35,1.70,1.20),(-.48,1.70,1.91)),
    ('upper arm',(-.48,1.70,1.91),(-.08,1.70,2.25)),
    ('shade support',(-.08,1.70,2.25),(.05,1.70,2.13))]:
    add(lamp,name,rod(.014,start=a,end=b,color=(.67,.68,.65)))
add(lamp, 'lamp shade', box((.25,.22,.12), (.06,1.70,2.10), (.66,.67,.63)))
scene.include('task lamp', lamp)

# Lumber shelf along back left.
rack = Asset('wall lumber rack')
for x in (-3.05,-1.65):
    add(rack,'upright %.2f'%x,box((.075,.48,2.55),(x,2.72,1.84),(.13,.12,.10)))
for z in (1.28,1.70,2.12,2.54,2.94):
    add(rack,'shelf %.2f'%z,box((1.72,.54,.07),(-2.35,2.70,z),(.22,.18,.13)))
    for j in range(3):
        length = random.uniform(1.05,1.65)
        add(rack,'lumber %.2f %d'%(z,j),box((length,.11,.055),
            (-2.35+random.uniform(-.08,.08),2.48+j*.13,z+.07+j*.02),
            random.choice([(.45,.29,.16),(.62,.43,.25),(.72,.57,.38)])))
# Extra rough timber lying along the bench.
for i in range(4):
    add(rack,'loose plank %d'%i,box((1.65,.13,.055),(-2.15,1.87+i*.11,1.19+i*.035),(.55,.37,.21)))
scene.include('lumber rack',rack)

# Dark stove/cabinet and wall storage toward the right edge.
storage = Asset('stove and wall storage')
add(storage,'cast iron stove body',box((.66,.50,.62),(2.53,2.37,1.42),(.09,.095,.09)))
add(storage,'stove top',box((.75,.57,.07),(2.53,2.37,1.76),(.07,.075,.07)))
add(storage,'stove door',box((.39,.025,.35),(2.53,2.105,1.40),(.15,.15,.14)))
add(storage,'stove flue',rod(.09,start=(2.54,2.42,1.79),end=(2.54,2.42,3.12),color=(.10,.10,.095)))
# Vertical stock and tool rack.
for i in range(8):
    x = 3.00+i*.10
    add(storage,'vertical stock %d'%i,rod(.018,start=(x,2.70,1.05),end=(x,2.70,2.63-(i%3)*.12),color=(.34,.34,.31)))
add(storage,'stock rack base',box((1.0,.35,.08),(3.36,2.68,1.03),dark))
add(storage,'tool cabinet',box((.72,.45,.84),(4.15,2.54,.57),(.16,.15,.13)))
for i in range(4):
    add(storage,'red bin %d'%i,box((.15,.20,.12),(3.91+i*.18,2.30,1.08),(.52,.08,.035)))
# Scattered hand tools along the wall.
for i in range(8):
    x = -.70+i*.11
    add(storage,'hanging tool %d'%i,rod(.018,start=(x,2.99,2.17),end=(x,2.99,2.53+(i%3)*.07),color=(.12,.11,.10)))
scene.include('wall storage',storage)

realize(scene)

# Establish camera and lighting after realization.
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
background.inputs['Color'].default_value = (0.33,0.32,0.29,1)
background.inputs['Strength'].default_value = .55

set_view((5.2,-8.8,4.5), (0,0.30,1.18), lens=38)
area_emitter((0,-3,6.7), power=1150, size=5, target=(0,0,0), color=(1.0,.84,.67))
area_emitter((-4,1,4.5), power=650, size=4, target=(0,0,1), color=(1.0,.90,.76))
area_emitter((.08,1.65,2.05), power=80, size=.45, target=(.3,1.1,1), color=(1.0,.80,.55))
