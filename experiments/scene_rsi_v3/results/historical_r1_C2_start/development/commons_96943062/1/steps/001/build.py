# Reference inventory, approximate normalized image bounds:
# - Dark carpeted floor: (0, .59) to (1, 1), scattered debris and long strips.
# - Beige back wall: (.11, .37) to (.53, .61); dark vent and electrical fixtures.
# - Beige right wall: (.52, .03) to (1, .82); large framed whiteboard.
# - Suspended tiled ceiling: (0, 0) to (.59, .39), with grid, lights and gaps.
# - Bright partial left partition: (0, .32) to (.12, .66), partly occluded.
# - American flag and diagonal pole near rear corner: (.45, .32) to (.59, .43).
# - Yellow folded insulation or mat on floor: (.56, .68) to (.90, .79).
# - Broken dark ceiling panels, metallic strips and small fragments across floor.
# The room beyond the image and the exact forms of the debris are uncertain.
#
# Primitive estimate: architecture 8, ceiling grid and fixtures 55,
# whiteboard 6, back-wall fixtures 9, flag and pole 16, floor debris 30:
# approximately 124 separate SceneAct primitives, with no Boolean operations.

from sceneact import *
import bpy
import math

scene = Scene('Damaged classroom')

# Palette
wall = (0.69, 0.68, 0.62)
back_wall = (0.62, 0.62, 0.57)
ceiling = (0.69, 0.71, 0.70)
grid = (0.47, 0.49, 0.48)
carpet = (0.105, 0.105, 0.09)
trim = (0.105, 0.11, 0.10)
metal = (0.43, 0.46, 0.45)
white = (0.84, 0.85, 0.83)

architecture = Asset('Room architecture')
architecture.include('carpeted floor', box((7.4, 17.0, .12), center=(-.7, -.5, -.06), color=carpet))
architecture.include('right wall', box((.12, 17.0, 3.35), center=(3.0, -.5, 1.675), color=wall))
architecture.include('back wall', box((7.4, .12, 3.35), center=(-.7, 8.0, 1.675), color=back_wall))
architecture.include('right dark baseboard', box((.035, 16.9, .18), center=(2.925, -.5, .09), color=trim))
architecture.include('back dark baseboard', box((7.3, .035, .18), center=(-.7, 7.92, .09), color=trim))
# Partial bright wall at the left edge.
architecture.include('left partition', box((.12, 5.8, 2.9), center=(-4.35, 4.9, 1.45), color=(.82,.84,.83)))
architecture.include('left partition vertical seam', box((.014,.018,2.7), center=(-4.275,3.5,1.45), color=(.65,.68,.67)))
scene.include('architecture', architecture)

# Ceiling as an intact field with dark gaps cut visually into its left side.
ceiling_asset = Asset('Suspended ceiling')
ceiling_asset.include('ceiling field', box((7.4,17.0,.10), center=(-.7,-.5,3.35), color=ceiling))
for i, x in enumerate([-4.3,-3.1,-1.9,-.7,.5,1.7,2.9]):
    ceiling_asset.include('long ceiling rail %02d' % i,
        box((.018,16.9,.018), center=(x,-.5,3.288), color=grid))
for i in range(15):
    y = -7.5 + i * 1.1
    ceiling_asset.include('cross ceiling rail %02d' % i,
        box((7.3,.018,.018), center=(-.7,y,3.287), color=grid))
# Light panels, visible mainly at the left side of the photograph.
for i,y in enumerate((1.6, 3.8, 6.0)):
    ceiling_asset.include('fluorescent panel %d' % i,
        box((1.12,1.02,.016), center=(-2.5,y,3.275), color=(.79,.81,.80)))
# Open or missing tiles at the far left.
for i,y in enumerate((4.2,5.4,6.6)):
    ceiling_asset.include('missing dark tile %d' % i,
        box((1.08,.82,.016), center=(-3.75,y,3.265), color=(.095,.11,.11)))
ceiling_asset.include('round ceiling detector',
    ball(.09, center=(-1.45,2.7,3.22), color=(.78,.78,.74)))
scene.include('ceiling', ceiling_asset)

board = Asset('Wall mounted whiteboard')
# A thin board on the interior face of the right wall.
board.include('white writing surface',
    box((.035,4.55,1.50), center=(2.915,3.42,1.84), color=(.87,.88,.87)))
for z in (1.08,2.60):
    board.include('horizontal frame %.2f' % z,
        box((.045,4.66,.045), center=(2.88,3.42,z), color=metal))
for y in (1.10,5.74):
    board.include('vertical frame %.2f' % y,
        box((.045,.045,1.55), center=(2.88,y,1.84), color=metal))
board.include('lower marker ledge',
    box((.14,4.55,.035), center=(2.84,3.42,1.05), color=(.61,.63,.61)))
scene.include('whiteboard', board)

fixtures = Asset('Back wall fixtures')
fixtures.include('vent dark inset',
    box((.90,.025,.40), center=(-2.25,7.91,1.91), color=(.24,.28,.27)))
for z in (1.76,1.84,1.92,2.00,2.06):
    fixtures.include('vent slat %.2f' % z,
        box((.84,.018,.012), center=(-2.25,7.89,z), color=(.34,.37,.35)))
fixtures.include('electrical panel',
    box((.31,.055,.47), center=(-.55,7.89,1.72), color=(.36,.40,.38)))
fixtures.include('electrical panel dark interior',
    box((.20,.018,.32), center=(-.55,7.85,1.75), color=(.14,.17,.16)))
cover = box((.54,.045,.48), center=(-.29,7.80,1.39), color=(.44,.48,.45))
cover.turn(axis='+y', degrees=-35)
fixtures.include('hanging metal panel cover', cover)
fixtures.include('small wall plate', box((.16,.025,.20), center=(.27,7.89,1.36), color=(.76,.76,.71)))
fixtures.include('small switch', box((.12,.025,.16), center=(.02,7.89,1.42), color=(.71,.72,.68)))
scene.include('back wall fixtures', fixtures)

flag = Asset('Hanging American flag')
# Small hanging flag, a set of narrow fabric-colored strips in the back-wall plane.
flag.include('diagonal flag pole', rod(.018, start=(1.80,7.86,3.04), end=(2.96,6.05,2.84), color=(.25,.25,.23)))
flag.include('flag field', box((.43,.025,.83), center=(1.89,7.80,2.57), color=(.84,.82,.75)))
for i in range(7):
    x = 1.68 + i * .065
    flag.include('red stripe %02d' % i,
        box((.033,.014,.78), center=(x,7.78,2.57), color=(.57,.09,.10)))
flag.include('blue canton', box((.20,.018,.30), center=(1.76,7.765,2.81), color=(.12,.18,.30)))
for i in range(3):
    for j in range(2):
        flag.include('canton spot %d %d' % (i,j),
            ball(.012, center=(1.70+i*.055,7.75,2.75+j*.10), color=(.85,.85,.80)))
scene.include('flag', flag)

debris = Asset('Floor debris')
# Dark fallen ceiling pieces, distributed across left and middle of the floor.
pieces = [
    ((1.05,.62,.035),(-2.7,1.4,.035),-13,(.20,.21,.19)),
    ((.85,.42,.028),(-1.6,3.8,.03),16,(.18,.19,.17)),
    ((1.35,.54,.035),(-1.95,-1.05,.04),-10,(.25,.25,.22)),
    ((.78,.37,.025),(-3.25,2.65,.025),8,(.27,.27,.24)),
    ((.70,.30,.024),(.6,3.35,.025),-18,(.38,.37,.31)),
    ((.55,.24,.018),(-1.1,4.3,.02),-8,(.29,.29,.25)),
]
for i,(size,center,angle,color) in enumerate(pieces):
    p = box(size, center=center, color=color)
    p.turn(axis='+z', degrees=angle)
    debris.include('broken panel %02d' % i, p)
# Thin loose strips and frame rails.
for i,(start,end,r,col) in enumerate([
    ((-3.3,.1,.055),(-1.0,-.65,.055),.025,(.55,.57,.55)),
    ((-2.9,-1.2,.065),(-1.0,-1.9,.065),.025,(.30,.31,.29)),
    ((-2.65,1.55,.07),(-1.15,1.26,.07),.018,(.48,.49,.45)),
    ((-2.9,3.8,.05),(-1.4,4.1,.05),.016,(.42,.43,.39)),
    ((1.25,-2.0,.025),(2.9,-3.8,.025),.035,(.61,.58,.51)),
    ((1.55,-2.15,.03),(3.0,-3.45,.03),.035,(.67,.65,.59)),
    ((-2.5,-.75,.06),(-1.3,-1.5,.06),.015,(.12,.13,.12)),
]):
    debris.include('loose strip %02d' % i, rod(r, start=start, end=end, color=col))
for i,(x,y) in enumerate([(-3.0,2.1),(-2.3,3.1),(-.9,2.4),(.0,3.8),(.9,4.2),(-1.9,.2),(.4,1.6)]):
    debris.include('small fragment %02d' % i,
        box((.13,.10,.018), center=(x,y,.02), color=(.37,.37,.32)))
scene.include('floor debris', debris)

mat = Asset('Yellow folded floor insulation')
# Overlapping flat slabs give the pile the broad stepped outline of the reference.
mat.include('lower folded layer', box((1.75,1.25,.07), center=(1.55,.0,.045), color=(.64,.51,.21)))
mat.include('middle folded layer', box((1.70,1.10,.07), center=(1.60,-.12,.105), color=(.73,.60,.27)))
top = box((1.72,1.12,.065), center=(1.70,-.25,.16), color=(.78,.66,.31))
top.turn(axis='+z', degrees=-8)
mat.include('upper yellow sheet', top)
mat.include('left folded edge', box((.16,1.00,.10), center=(.77,.06,.10), color=(.80,.67,.33)))
mat.include('second folded edge', box((.12,.98,.09), center=(.94,.05,.12), color=(.69,.55,.23)))
scene.include('yellow floor insulation', mat)

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
background.inputs['Color'].default_value = (0.72, 0.75, 0.76, 1)
background.inputs['Strength'].default_value = 0.7

set_view((-2.0,-8.6,1.72), (2.55,7.7,1.50), lens=30, sensor=36)
area_emitter((-1.8,-2.0,3.05), power=550, size=5.0, target=(0,3,0))
area_emitter((-3.5,5.0,2.8), power=380, size=4.0, target=(1,5,1))
area_emitter((1.0,3.0,3.15), power=220, size=3.0, target=(1,3,0))
