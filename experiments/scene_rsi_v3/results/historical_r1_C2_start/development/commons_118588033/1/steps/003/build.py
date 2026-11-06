# Reference inventory, approximate normalized image bounds:
# Rust-red floor occupies the lower half; cream bulkheads and exposed brown
# ceiling framing surround a crowded industrial interior. Some wall and pipe
# routes are obscured.
# Left foreground: dark green machinery (0,.48,.21,.73), a narrow green
# bench (0,.61,.39,.95), and a cream ventilator (0,.21,.19,.37).
# Left middle: three pale bunks with dark metal supports (.13,.34,.40,.69).
# Center: black enclosure (.39,.31,.69,.70), gray lockers, table and chair.
# The mesh and rear equipment are partly occluded.
# Right: cream column with brown lower section (.68,0,.80,.85), cream
# partition with dark board, red fixture and notice (.76,.33,1,.66), and
# cropped green bench (.80,.75,1,1).
# Overhead: beams, pipes, bright foreground pendant and smaller distant lamps.
#
# Comparison with the second render: the foreground pendant is too far left
# and low, the left machinery and ventilator are largely out of frame, and
# the right bench and wall fixtures are hidden. The white ceiling beams are
# too prominent. The central bunk and enclosure positions are broadly retained.
# Primitive estimate: about 185 boxes and rods, including repeated details.

from sceneact import *
import bpy

scene = Scene('Ship interior')

wall = (0.56, 0.55, 0.47)
cream = (0.67, 0.64, 0.54)
ceiling = (0.30, 0.23, 0.19)
rust = (0.22, 0.075, 0.045)
black = (0.025, 0.030, 0.027)
green = (0.025, 0.075, 0.061)
metal = (0.29, 0.31, 0.29)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

room = Asset('architecture')
B(room, 'floor', (7.4, 11.4, .12), (0, .5, -.08), rust)
B(room, 'back wall', (7.4, .15, 3.9), (0, 5, 1.95), wall)
B(room, 'left wall', (.15, 11.4, 3.9), (-3.7, .5, 1.95), wall)
B(room, 'right wall', (.15, 11.4, 3.9), (3.7, .5, 1.95), wall)
B(room, 'ceiling', (7.4, 11.4, .15), (0, .5, 3.93), ceiling)
B(room, 'back baseboard', (7.4, .08, .25), (0, 4.88, .13), (.22, .10, .07))
for i, y in enumerate((-3.0, -.35, 2.3, 4.6)):
    B(room, 'transverse beam %d' % i, (7.4, .20, .19),
      (0, y, 3.76), (.48, .38, .30))
for i, x in enumerate((-2.8, -1.5, .1, 1.7, 3.2)):
    B(room, 'ceiling joist %d' % i, (.13, 10.6, .15),
      (x, .15, 3.78), (.31, .19, .13))
scene.include('architecture', room)

pillar = Asset('foreground structural pillar')
R(pillar, 'cream upper shaft', (1.35, -1.55, 1.68),
  (1.35, -1.55, 3.95), .17, (.68, .64, .54))
R(pillar, 'brown lower shaft', (1.35, -1.55, .05),
  (1.35, -1.55, 1.68), .17, (.25, .105, .065))
R(pillar, 'foot collar', (1.35, -1.55, .02),
  (1.35, -1.55, .09), .21, (.30, .20, .15))
scene.include('foreground structural pillar', pillar)

pipes = Asset('exposed overhead pipes')
for i, x in enumerate((-2.75, -2.2, 1.0, 1.85, 2.6)):
    z = 3.36 - .08 * (i % 2)
    R(pipes, 'long pipe %d' % i, (x, -4.7, z),
      (x, 4.75, z), .055, cream)
    if i in (1, 2, 3):
        R(pipes, 'down pipe %d' % i, (x, 4.75, z),
          (x, 4.75, 1), .055, cream)
for i, y in enumerate((-2.0, .9, 3.4)):
    R(pipes, 'cross pipe %d' % i, (-3.5, y, 3.25),
      (2.8, y, 3.25), .042, (.20, .20, .18))
R(pipes, 'diagonal foreground pipe', (-3.6, -4.7, 3.75),
  (-1.2, -2.0, 3.06), .065, (.72, .71, .64))
R(pipes, 'diagonal brace', (-2.9, -3.7, 3.83),
  (-1.9, -2.7, 3.05), .045, (.68, .67, .60))
scene.include('exposed overhead pipes', pipes)

bunk = Asset('three tier bunk beds')
bx = -1.95
for i, x in enumerate((bx-.62, bx+.62)):
    for j, y in enumerate((1.0, 4.05)):
        R(bunk, 'upright %d %d' % (i, j), (x, y, .15),
          (x, y, 2.87), .035, black)
for k, z in enumerate((.58, 1.24, 1.91)):
    B(bunk, 'bed platform %d' % k, (1.25, 2.95, .10),
      (bx, 2.5, z), (.14, .16, .14))
    B(bunk, 'mattress %d' % k, (1.13, 2.78, .13),
      (bx, 2.48, z+.115), (.63, .64, .60))
    B(bunk, 'pillow %d' % k, (1.02, .48, .10),
      (bx, 3.48, z+.23), (.73, .73, .68))
    R(bunk, 'front rail %d' % k, (bx-.65, .99, z+.12),
      (bx+.65, .99, z+.12), .024, black)
scene.include('three tier bunk beds', bunk)

vent = Asset('left wall ventilator')
B(vent, 'housing', (.20, .86, .79), (-2.80, -3.0, 2.60), (.49, .50, .46))
B(vent, 'opening', (.03, .64, .52), (-2.68, -3.0, 2.60), (.08, .10, .09))
for i in range(6):
    B(vent, 'louver %d' % i, (.04, .63, .045),
      (-2.65, -3.0, 2.38+i*.085), (.52, .53, .48))
scene.include('left wall ventilator', vent)

machine = Asset('left machinery cabinets')
B(machine, 'cabinet body', (.85, 3.2, 1.25), (-2.75, -3.1, .625), (.055, .085, .08))
B(machine, 'top', (.95, 3.25, .09), (-2.72, -3.1, 1.29), (.10, .13, .12))
for i in range(9):
    y = -4.53+i*.35
    B(machine, 'panel %d' % i, (.025, .29, .92),
      (-2.31, y, .65), (.10, .14, .13))
    for j in range(4):
        B(machine, 'panel slot %d %d' % (i, j), (.012, .22, .018),
          (-2.29, y, .42+j*.15), (.19, .22, .20))
scene.include('left machinery cabinets', machine)

for name, x, y, length in [
    ('left bench', -2.30, -3.1, 4.2),
    ('right bench', 1.95, -4.9, 2.2)
]:
    bench = Asset(name)
    B(bench, 'seat plank', (.48, length, .10), (x, y, .51), green)
    for n, yy in enumerate((y-length*.37, y+length*.37)):
        R(bench, 'outer leg %d' % n, (x-.18, yy, .49),
          (x-.18, yy, .04), .025, black)
        R(bench, 'inner leg %d' % n, (x+.18, yy, .49),
          (x+.18, yy, .04), .025, black)
    scene.include(name, bench)

cage = Asset('central wire enclosure')
for i, x in enumerate((-.78, .70)):
    for j, y in enumerate((1.55, 4.15)):
        R(cage, 'corner post %d %d' % (i, j), (x, y, .05),
          (x, y, 2.95), .038, black)
for k, z in enumerate((.10, 1.15, 2.88)):
    R(cage, 'front crossbar %d' % k, (-.78, 1.55, z),
      (.70, 1.55, z), .026, black)
    R(cage, 'right side rail %d' % k, (.70, 1.55, z),
      (.70, 4.15, z), .025, black)
for i in range(6):
    y = 1.75+i*.43
    R(cage, 'side wire %d' % i, (.71, y, .20),
      (.71, y, 2.78), .009, (.10, .11, .10))
for i in range(6):
    z = .40+i*.38
    R(cage, 'side cross wire %d' % i, (.71, 1.6, z),
      (.71, 4.1, z), .008, (.10, .11, .10))
scene.include('central wire enclosure', cage)

lockers = Asset('rear grey lockers')
for i in range(3):
    x = -.58+i*.50
    B(lockers, 'body %d' % i, (.47, .40, 1.72),
      (x, 3.60, 1.24), (.34, .37, .35))
    B(lockers, 'door %d' % i, (.42, .025, 1.60),
      (x, 3.38, 1.25), (.42, .44, .41))
    B(lockers, 'handle %d' % i, (.045, .035, .17),
      (x+.14, 3.35, 1.25), (.16, .18, .17))
    for j in range(3):
        B(lockers, 'vent %d %d' % (i, j), (.18, .012, .018),
          (x, 3.35, 1.75+j*.055), (.24, .26, .24))
scene.include('rear grey lockers', lockers)

desk = Asset('small work table and chair')
B(desk, 'table top', (.95, .60, .08), (.22, 2.65, .88), (.22, .22, .19))
B(desk, 'table front cabinet', (.80, .44, .76), (.27, 2.82, .45), (.21, .22, .20))
for i, x in enumerate((-.20, .62)):
    for j, y in enumerate((2.4, 2.9)):
        R(desk, 'table leg %d %d' % (i, j), (x, y, .84), (x, y, .08), .024, metal)
B(desk, 'chair seat', (.46, .43, .07), (-.48, 2.2, .53), (.47, .46, .39))
B(desk, 'chair back', (.45, .07, .48), (-.48, 2.41, .85), (.43, .43, .37))
for i, x in enumerate((-.66, -.30)):
    for j, y in enumerate((2.04, 2.34)):
        R(desk, 'chair leg %d %d' % (i, j), (x, y, .51),
          (x, y, .06), .018, (.6, .6, .53))
scene.include('small work table and chair', desk)

partition = Asset('right wall and fixtures')
B(partition, 'cream partition', (2.35, .13, 2.95),
  (2.70, 1.20, 1.48), (.63, .62, .54))
B(partition, 'brown baseboard', (2.35, .05, .26),
  (2.70, 1.12, .13), (.28, .12, .08))
B(partition, 'grey wall board', (.78, .055, .83),
  (2.65, 1.10, 2.05), (.20, .24, .23))
B(partition, 'white paper notice', (.55, .028, .88),
  (3.35, 1.10, 1.76), (.72, .72, .66))
B(partition, 'red safety box', (.38, .13, .60),
  (2.53, 1.02, 1.08), (.72, .075, .045))
B(partition, 'dark window', (.13, .025, .19),
  (2.53, .94, 1.18), (.19, .16, .14))
B(partition, 'small label', (.23, .025, .07),
  (2.53, .94, .91), (.85, .42, .30))
scene.include('right wall and fixtures', partition)

lamps = Asset('pendant lights')
for i, (x, y, z, rad) in enumerate((
    (-.52, -2.4, 3.65, .27),
    (-.70, 1.45, 3.12, .16),
    (-.30, 3.95, 3.06, .12)
)):
    R(lamps, 'cable %d' % i, (x, y, 3.90), (x, y, z+.13), .018, black)
    R(lamps, 'shade %d' % i, (x, y, z), (x, y, z+.10),
      rad, (.24, .25, .23))
    R(lamps, 'diffuser %d' % i, (x, y, z-.035), (x, y, z+.01),
      rad*.91, (.98, .96, .87))
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
background.inputs['Color'].default_value = (.36, .35, .31, 1)
background.inputs['Strength'].default_value = .38

set_view((.05, -7.2, 2.55), (.02, 2.2, 1.75), lens=30, sensor=36)
area_emitter((-.52, -2.4, 3.55), power=280, size=.6,
             target=(-1, 0, 0), color=(1, .84, .67))
area_emitter((-.7, 1.45, 3.1), power=170, size=.6,
             target=(0, 2.5, .2), color=(1, .92, .80))
area_emitter((1.5, -3, 3.1), power=120, size=2.5,
             target=(0, 2, 1), color=(1, .86, .72))
