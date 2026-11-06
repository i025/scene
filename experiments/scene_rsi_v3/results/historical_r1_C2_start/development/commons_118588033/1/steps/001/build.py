# Reference inventory, normalized image coordinates (approximate):
# Room: rust-red floor (0, .63, 1, 1), cream walls, exposed ceiling and beams
# (0, 0, 1, .25). Back wall and many pipes are partly obscured.
# Left: dark green machinery/cabinets (0, .47, .22, .76), long narrow bench
# (0, .61, .40, .94), wall vent (0, .20, .20, .37).
# Three-tier narrow bunk/shelving unit (.13, .32, .43, .72), pale mattresses,
# black frame, gaps between levels.
# Center: black wire enclosure (.38, .31, .68, .70), upright posts, mesh-like
# rails, gray lockers and a chair visible inside; rear objects partly occluded.
# Right: large cream structural column with brown lower half (.68, 0, .80, .85);
# gray wall panel (.77, .34, .91, .47), red safety fixture (.77, .50, .85, .61);
# dark green bench at lower right (.80, .75, 1, 1).
# Overhead: exposed cream pipes, brown ceiling beams, three pendant lamps.
# Expanded primitive estimate: approximately 175 boxes and rods, including
# repeated cage rails, bunk parts, lockers, pipes, and furniture.

from sceneact import *
import bpy
import math

scene = Scene('Ship interior')

cream = (0.62, 0.59, 0.49)
wall = (0.60, 0.59, 0.51)
ceiling = (0.39, 0.30, 0.24)
rust = (0.29, 0.105, 0.065)
dark = (0.035, 0.045, 0.041)
green = (0.025, 0.075, 0.062)
metal = (0.29, 0.31, 0.29)
lightgrey = (0.60, 0.61, 0.57)
white = (0.76, 0.76, 0.67)
black = (0.025, 0.028, 0.026)

def add_box(parent, name, size, pos, color):
    parent.include(name, box(size=size, center=pos, color=color))

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

room = Asset('architecture')
add_box(room, 'red floor', (7.4, 10.4, .12), (0, 1.0, -.08), rust)
add_box(room, 'back wall', (7.4, .15, 3.9), (0, 5.0, 1.95), wall)
add_box(room, 'left wall', (.15, 10.4, 3.9), (-3.7, 0, 1.95), wall)
add_box(room, 'right wall', (.15, 10.4, 3.9), (3.7, 0, 1.95), wall)
add_box(room, 'ceiling', (7.4, 10.4, .15), (0, 0, 3.93), ceiling)
add_box(room, 'back skirting', (7.4, .08, .25), (0, 4.88, .13), (0.24, .11, .08))
for i, y in enumerate((-2.5, .15, 2.6, 4.6)):
    add_box(room, 'transverse ceiling beam %d' % i, (7.4, .22, .35), (0, y, 3.64), cream)
for i, x in enumerate((-2.8, -1.5, .1, 1.7, 3.2)):
    add_box(room, 'ceiling joist %d' % i, (.13, 9.8, .15), (x, .15, 3.78), (0.35, .22, .16))
scene.include('architecture', room)

# Thick support pillar, with the lower part painted deep red-brown.
pillar = Asset('foreground structural pillar')
add_rod(pillar, 'cream upper shaft', (1.38, -.02, 1.68), (1.38, -.02, 3.92), .19, (0.73, .69, .57))
add_rod(pillar, 'brown lower shaft', (1.38, -.02, .05), (1.38, -.02, 1.68), .19, (0.27, .12, .08))
add_rod(pillar, 'foot collar', (1.38, -.02, .02), (1.38, -.02, .10), .24, (0.34, .23, .18))
scene.include('foreground structural pillar', pillar)

# Exposed pipes follow the ceiling and turn down the back wall.
pipes = Asset('exposed overhead pipes')
for i, x in enumerate((-2.75, -2.2, 1.0, 1.85, 2.6)):
    z = 3.35 - .08 * (i % 2)
    add_rod(pipes, 'long pipe %d' % i, (x, -3.6, z), (x, 4.75, z), .055, cream)
    if i in (1, 2, 3):
        add_rod(pipes, 'down pipe %d' % i, (x, 4.75, z), (x, 4.75, 1.0), .055, cream)
for i, y in enumerate((-1.3, 1.6, 3.4)):
    add_rod(pipes, 'cross pipe %d' % i, (-3.5, y, 3.24), (2.8, y, 3.24), .045, (0.26, .25, .22))
scene.include('exposed overhead pipes', pipes)

# Bunk beds viewed from the foot end, with distinct open gaps.
bunk = Asset('three tier bunk beds')
bx = -1.95
for i, x in enumerate((bx-.62, bx+.62)):
    for j, y in enumerate((1.0, 4.05)):
        add_rod(bunk, 'upright %d %d' % (i,j), (x,y,.15), (x,y,2.87), .035, black)
for k, z in enumerate((.58, 1.24, 1.91)):
    add_box(bunk, 'bed platform %d' % k, (1.25, 2.95, .10), (bx, 2.5, z), (0.16,.18,.16))
    add_box(bunk, 'mattress %d' % k, (1.13, 2.78, .13), (bx, 2.48, z+.115), (0.68,.68,.63))
    add_box(bunk, 'pillow %d' % k, (1.02, .48, .10), (bx, 3.48, z+.23), (0.78,.78,.72))
    add_rod(bunk, 'front bed rail %d' % k, (bx-.65, .99, z+.12), (bx+.65, .99, z+.12), .024, black)
scene.include('three tier bunk beds', bunk)

# Wall-mounted ventilator on left.
vent = Asset('left wall ventilator')
add_box(vent, 'housing', (.18, .78, .75), (-3.57, .55, 2.47), (0.49,.50,.46))
add_box(vent, 'dark opening', (.03, .60, .50), (-3.46, .55, 2.47), (0.10,.12,.11))
for i in range(6):
    add_box(vent, 'louver %d' % i, (.04,.59,.045), (-3.43,.55,2.25+i*.085), (0.52,.53,.47))
scene.include('left wall ventilator', vent)

# Low industrial equipment and its repeated narrow front panels.
machine = Asset('left machinery cabinets')
add_box(machine, 'cabinet body', (.72, 3.0, 1.22), (-3.2, -.25, .61), (0.075,.11,.10))
add_box(machine, 'top', (.82, 3.05, .09), (-3.18,-.25,1.25), (0.12,.15,.14))
for i in range(9):
    y = -1.54 + i*.32
    add_box(machine, 'panel %d' % i, (.025,.26,.89), (-2.82,y,.65), (0.12,.17,.16))
    for j in range(4):
        add_box(machine, 'panel slot %d %d' % (i,j), (.012,.20,.018), (-2.80,y,.43+j*.14), (0.20,.24,.22))
scene.include('left machinery cabinets', machine)

# Long dark green benches along the left and at the near right edge.
for name, x, y, length in [('left bench', -2.55, -1.15, 4.1),
                           ('right bench', 2.95, -2.9, 2.2)]:
    bench = Asset(name)
    add_box(bench, 'seat plank', (.48,length,.10), (x,y,.51), green)
    for n, yy in enumerate((y-length*.37, y+length*.37)):
        add_rod(bench, 'leg outer %d' % n, (x-.18,yy,.49), (x-.18,yy,.04), .025, dark)
        add_rod(bench, 'leg inner %d' % n, (x+.18,yy,.49), (x+.18,yy,.04), .025, dark)
    scene.include(name, bench)

# Central cage: structural posts, horizontal bars, and sparse wire grid.
cage = Asset('central wire enclosure')
for i, x in enumerate((-.78,.70)):
    for j, y in enumerate((2.0,4.15)):
        add_rod(cage, 'corner post %d %d' % (i,j), (x,y,.05), (x,y,2.90), .035, black)
for k, z in enumerate((.10,1.05,1.90,2.84)):
    add_rod(cage, 'front crossbar %d' % k, (-.78,2.0,z), (.70,2.0,z), .025, black)
    add_rod(cage, 'right side rail %d' % k, (.70,2.0,z), (.70,4.15,z), .025, black)
for i in range(9):
    x = -.72 + i*.17
    add_rod(cage, 'front vertical mesh %d' % i, (x,2.02,.2), (x,2.02,2.75), .008, (0.12,.13,.12))
for i in range(8):
    z = .35 + i*.30
    add_rod(cage, 'front horizontal mesh %d' % i, (-.75,2.02,z), (.68,2.02,z), .008, (0.12,.13,.12))
for i in range(9):
    y = 2.15+i*.23
    add_rod(cage, 'side vertical mesh %d' % i, (.71,y,.2), (.71,y,2.75), .008, (0.12,.13,.12))
scene.include('central wire enclosure', cage)

# Grey lockers behind the cage, with visible door divisions and handles.
lockers = Asset('rear grey lockers')
for i in range(3):
    x = -.65 + i*.55
    add_box(lockers, 'locker body %d' % i, (.51,.46,1.63), (x,3.77,1.14), (0.39,.42,.40))
    add_box(lockers, 'locker door %d' % i, (.44,.025,1.50), (x,3.525,1.17), (0.47,.49,.46))
    add_box(lockers, 'handle %d' % i, (.045,.035,.19), (x+.15,3.50,1.20), (0.20,.22,.20))
    for j in range(3):
        add_box(lockers, 'vent slot %d %d' % (i,j), (.20,.012,.018), (x,3.50,1.65+j*.06), (0.28,.30,.28))
scene.include('rear grey lockers', lockers)

desk = Asset('small work table and chair')
add_box(desk, 'table top', (1.0,.65,.08), (.15,2.73,.86), (0.23,.23,.20))
for i, x in enumerate((-.28,.58)):
    for j, y in enumerate((2.46,2.99)):
        add_rod(desk, 'table leg %d %d' % (i,j), (x,y,.82), (x,y,.08), .024, metal)
add_box(desk, 'chair seat', (.47,.45,.07), (-.48,2.55,.53), (0.48,.47,.40))
add_box(desk, 'chair back', (.46,.07,.52), (-.48,2.78,.86), (0.45,.45,.39))
for i, x in enumerate((-.66,-.30)):
    for j, y in enumerate((2.38,2.72)):
        add_rod(desk, 'chair leg %d %d' % (i,j), (x,y,.51), (x,y,.06), .018, lightgrey)
scene.include('small work table and chair', desk)

# Back wall panel and prominent red safety unit.
wall_objects = Asset('right wall fixtures')
add_box(wall_objects, 'grey wall board', (1.0,.06,.85), (2.35,4.88,2.28), (0.25,.29,.28))
add_box(wall_objects, 'paper notice', (.60,.025,.98), (3.22,4.86,1.86), (0.72,.72,.66))
add_box(wall_objects, 'red safety box', (.38,.12,.66), (2.30,4.80,1.19), (0.71,.09,.055))
add_box(wall_objects, 'safety box dark window', (.14,.025,.20), (2.30,4.72,1.36), (0.18,.15,.13))
add_box(wall_objects, 'safety label', (.23,.025,.08), (2.30,4.72,1.05), (0.88,.45,.32))
scene.include('right wall fixtures', wall_objects)

lamps = Asset('pendant lights')
for i, (x,y,z) in enumerate(((-1.52,-.3,3.28), (-.7,2.25,3.09), (-.3,4.05,3.05))):
    add_rod(lamps, 'lamp cable %d' % i, (x,y,3.78), (x,y,z+.15), .018, black)
    add_rod(lamps, 'lamp shade %d' % i, (x,y,z), (x,y,z+.12), .24 if i == 0 else .16, (0.24,.25,.23))
    add_rod(lamps, 'lamp diffuser %d' % i, (x,y,z-.035), (x,y,z+.01), .22 if i == 0 else .14, (0.95,.93,.82))
scene.include('pendant lights', lamps)

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
background.inputs['Color'].default_value = (0.40, 0.39, 0.34, 1)
background.inputs['Strength'].default_value = .55

set_view((0.05,-7.2,2.55), (0.02,2.2,1.75), lens=30, sensor=36)
area_emitter((-1.5,-.3,3.35), power=380, size=1.1, target=(-1,1,0), color=(1,.86,.68))
area_emitter((-.6,2.3,3.2), power=250, size=.8, target=(0,2.8,.2), color=(1,.94,.82))
area_emitter((1.5,-3,3.2), power=300, size=3.0, target=(0,2,1), color=(1,.86,.70))
