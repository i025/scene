# Reference inventory and image anchors (normalized image coordinates, estimates):
# - Foreground pale tabletop: x 0.00–0.46, y 0.84–1.00; cropped by image.
# - Left row of dark booth backs: x 0.00–0.33, y 0.51–0.90; repeated horizontal
#   tops recede toward the bright rear windows. Booth interiors are occluded.
# - Dining tables and upholstered chairs: x 0.38–0.89, y 0.52–1.00. Tables are
#   pale horizontal slabs; darker rectangular chair backs overlap their edges.
# - Rear glazing: x 0.03–0.66, y 0.31–0.54. Right glazing: x 0.65–1.00,
#   y 0.24–0.58. Thin dark mullions divide a very bright exterior.
# - Pendant shades: largest at x 0.02–0.23, y 0.12–0.40, with smaller hanging
#   lamps across the middle and rear. The foreground shade overlaps the glazing.
# - Plant at right: x 0.78–1.00, y 0.39–1.00, in front of windows and chairs.
#   A smaller plant occupies the center rear. Individual leaves are uncertain.
# - Ceiling x 0–1, y 0–0.34; floor x 0.30–1, y 0.58–1.00.
# Dominant edges: near-horizontal ceiling/window transoms, vertical mullions,
# and floor/tables receding toward the image center. All positions are estimates.
#
# Primitive budget: architecture and glazing ~75 boxes; floor joints ~28;
# tables ~32 primitives; booths ~24; chairs ~75; lamps ~65; plants ~100.
# Total approximately 400 expanded primitives. Every primitive is a separate mesh.

from sceneact import *
import bpy
import math
import random

random.seed(18)
scene = Scene('Restaurant interior')

# Camera and major room dimensions are deliberately independent parameters.
CAMERA_POSITION = (0.15, -9.8, 3.05)
CAMERA_TARGET = (0.0, 3.0, 1.75)
CAMERA_LENS = 25
ROOM_WIDTH = 10.6
ROOM_DEPTH = 13.0
ROOM_HEIGHT = 4.0
BACK_Y = 5.1
RIGHT_X = ROOM_WIDTH / 2

ivory = (0.76, 0.77, 0.74)
ceiling_color = (0.75, 0.76, 0.73)
floor_color = (0.26, 0.28, 0.27)
grout = (0.43, 0.44, 0.42)
frame = (0.19, 0.21, 0.20)
window = (0.89, 0.91, 0.88)
white = (0.74, 0.76, 0.73)
table_color = (0.69, 0.71, 0.68)
upholstery = (0.29, 0.31, 0.30)
metal = (0.24, 0.26, 0.25)
leaf_color = (0.20, 0.24, 0.21)
leaf_light = (0.29, 0.32, 0.28)

room = Asset('architecture')
room.include('floor', box((ROOM_WIDTH, ROOM_DEPTH, .12),
                          center=(0, -.7, -.06), color=floor_color))
room.include('ceiling', box((ROOM_WIDTH, ROOM_DEPTH, .10),
                            center=(0, -.7, ROOM_HEIGHT + .05), color=ceiling_color))
room.include('back_low_wall', box((ROOM_WIDTH, .14, .78),
                                   center=(0, BACK_Y, .39), color=ivory))
room.include('back_header', box((ROOM_WIDTH, .14, .45),
                                 center=(0, BACK_Y, 3.77), color=ivory))
room.include('right_low_wall', box((.14, ROOM_DEPTH, .75),
                                    center=(RIGHT_X, -.7, .375), color=ivory))
room.include('right_header', box((.14, ROOM_DEPTH, .4),
                                  center=(RIGHT_X, -.7, 3.8), color=ivory))
# Bright window panes and dark structural frames.
room.include('rear_bright_glazing', box((10.35, .035, 2.70),
                                        center=(0, BACK_Y + .03, 2.15), color=window))
for i, x in enumerate([-5.15, -3.15, -1.05, 1.05, 3.15, 5.15]):
    room.include('rear_mullion_%d' % i, box((.075, .12, 2.9),
                                           center=(x, BACK_Y-.055, 2.17), color=frame))
for z in (.77, 3.53):
    room.include('rear_rail_%.2f' % z, box((10.5, .12, .075),
                                          center=(0, BACK_Y-.06, z), color=frame))
room.include('right_bright_glazing', box((.035, 12.8, 2.72),
                                         center=(RIGHT_X+.03, -.7, 2.15), color=window))
for i, y in enumerate([-6.9, -4.5, -2.1, .3, 2.7, 5.0]):
    room.include('right_mullion_%d' % i, box((.12, .075, 2.88),
                                             center=(RIGHT_X-.05, y, 2.15), color=frame))
for z in (.77, 3.53):
    room.include('right_rail_%.2f' % z, box((.12, 12.8, .075),
                                            center=(RIGHT_X-.05, -.7, z), color=frame))
# Ceiling plank seams and floor tile seams give the long perspective lines.
for i in range(21):
    x = -5.0 + i*.5
    room.include('ceiling_seam_%02d' % i, box((.012, 12.8, .008),
                                              center=(x, -.7, 3.993), color=(.58,.59,.57)))
for i in range(16):
    x = -5.1 + i*.68
    room.include('floor_long_joint_%02d' % i, box((.012, 12.8, .006),
                                                  center=(x, -.7, .006), color=grout))
for i in range(14):
    y = -6.7 + i*.9
    room.include('floor_cross_joint_%02d' % i, box((10.4, .012, .006),
                                                   center=(0, y, .008), color=grout))
scene.include('room', room)

# Booth row: broad solid backs with small seat and base elements.
booths = Asset('left_booths')
for i, y in enumerate([-5.1, -2.85, -.6, 1.65, 3.8]):
    booth = Asset('booth_%d' % i)
    booth.include('back', box((3.0, .16, 1.16),
                              center=(-3.82, y, .79), color=upholstery))
    booth.include('seat', box((2.85, .73, .14),
                              center=(-3.82, y+.47, .48), color=(.34,.36,.35)))
    booth.include('plinth', box((2.65, .48, .36),
                                center=(-3.82, y+.42, .20), color=(.24,.26,.25)))
    booth.include('top_trim', box((3.0, .17, .035),
                                   center=(-3.82, y, 1.38), color=(.42,.44,.42)))
    booths.include('booth_%d' % i, booth)
scene.include('booths', booths)

def make_table(name, x, y, sx=1.45, sy=.88):
    a = Asset(name)
    a.include('light_tabletop', box((sx, sy, .065), center=(x,y,.78), color=table_color))
    a.include('edge', box((sx, sy, .035), center=(x,y,.727), color=(.35,.37,.35)))
    a.include('pedestal', rod(.055, start=(x,y,.08), end=(x,y,.73), color=metal))
    a.include('foot', box((.62,.48,.045), center=(x,y,.055), color=metal))
    return a

tables = Asset('dining_tables')
for i, (x,y,sx,sy) in enumerate([
    (-3.55,-6.05,3.45,1.28), (-3.7,-3.85,2.65,.8),
    (-3.7,-1.65,2.55,.75), (-3.7,.6,2.45,.72),
    (-.65,-2.65,1.55,.9), (1.72,-2.25,1.55,.9),
    (-.65,.1,1.45,.84), (1.72,.35,1.45,.84),
    (-.65,2.65,1.4,.8), (1.72,2.8,1.4,.8),
    (3.65,1.25,1.22,.78)]):
    tables.include('table_%02d' % i, make_table('table_%02d' % i,x,y,sx,sy))
scene.include('tables', tables)

def make_chair(name, x, y, facing=1):
    a = Asset(name)
    # Chairs face toward or away from the rear; back is on the outward side.
    back_y = y - facing*.29
    a.include('seat', box((.72,.67,.10), center=(x,y,.52), color=upholstery))
    a.include('back', box((.74,.105,.88), center=(x,back_y,.99), color=upholstery))
    a.include('back_edge', box((.77,.12,.035), center=(x,back_y,1.42), color=(.44,.46,.44)))
    for j, (dx,dy) in enumerate([(-.29,-.25),(.29,-.25),(-.29,.25),(.29,.25)]):
        a.include('leg_%d' % j, rod(.025, start=(x+dx,y+dy,.045),
                                    end=(x+dx,y+dy,.50), color=metal))
    return a

chairs = Asset('restaurant_chairs')
chair_positions = [
    (-.72,-3.43,1), (1.74,-3.08,1), (3.18,-2.92,1),
    (-1.55,-1.78,-1), (.20,-1.78,-1), (1.75,-1.42,-1),
    (-.75,-.73,1), (1.70,-.48,1), (3.52,.35,1),
    (-1.42,.83,-1), (.15,.83,-1), (1.70,1.15,-1),
    (-.75,1.93,1), (1.68,2.04,1), (3.55,2.02,-1),
    (-1.38,3.33,-1), (.05,3.33,-1), (1.7,3.52,-1)]
for i,(x,y,f) in enumerate(chair_positions):
    chairs.include('chair_%02d' % i, make_chair('chair_%02d' % i,x,y,f))
scene.include('chairs', chairs)

# A pendant's shade is a stepped dark dome, with a pale underside.
def pendant(name,x,y,bottom,r):
    a = Asset(name)
    a.include('cord', rod(.015, start=(x,y,bottom+.55), end=(x,y,3.99),
                           color=(.22,.23,.22)))
    a.include('ceiling_cap', rod(.085, length=.035, center=(x,y,3.97),
                                  color=metal))
    a.include('shade_lower', rod(r, length=.10, center=(x,y,bottom+.05),
                                 color=(.11,.13,.12)))
    a.include('shade_middle', rod(r*.84, length=.16, center=(x,y,bottom+.17),
                                  color=(.12,.14,.13)))
    a.include('shade_upper', rod(r*.57, length=.14, center=(x,y,bottom+.32),
                                 color=(.13,.15,.14)))
    a.include('shade_neck', rod(r*.31, length=.15, center=(x,y,bottom+.46),
                                color=(.14,.16,.15)))
    a.include('underside', rod(r*.82, length=.018, center=(x,y,bottom-.005),
                                color=(.65,.67,.63)))
    return a

lamps = Asset('hanging_lights')
for i,(x,y,z,r) in enumerate([
    (-3.8,-4.1,2.76,.73), (-3.65,-.1,2.76,.39),
    (-3.55,3.45,2.72,.29), (-.75,3.8,2.67,.26),
    (1.0,2.7,2.67,.36), (2.72,3.7,2.68,.24),
    (3.62,1.55,2.67,.46), (4.65,3.4,2.68,.27)]):
    lamps.include('pendant_%d' % i, pendant('pendant_%d' % i,x,y,z,r))
scene.include('pendants', lamps)

def plant(name, x, y, height, spread, count):
    a = Asset(name)
    a.include('planter', rod(.30*spread, length=.52*height/2,
                              center=(x,y,.13*height), color=(.24,.26,.23)))
    # Leaves are flattened ellipsoids, distributed around visible long stems.
    for i in range(count):
        angle = i * 2.399
        radial = spread * (.32 + .55*((i*7)%11)/10.0)
        tipz = height*(.48 + .47*((i*5)%13)/12.0)
        bx = x + math.cos(angle)*radial*.12
        by = y + math.sin(angle)*radial*.12
        tx = x + math.cos(angle)*radial
        ty = y + math.sin(angle)*radial
        a.include('stem_%02d' % i, rod(.012, start=(bx,by,.25*height),
                                        end=(tx,ty,tipz), color=leaf_color))
        leaf = ball(1, center=(tx,ty,tipz), color=leaf_light if i%4==0 else leaf_color)
        leaf.resize((.075*spread,.32*spread,.045*height))
        leaf.turn(axis='+z', degrees=math.degrees(angle)-90)
        a.include('leaf_%02d' % i, leaf)
    return a

scene.include('foreground_plant', plant('foreground_plant',4.25,-2.0,2.65,1.15,28))
scene.include('rear_plant', plant('rear_plant',-1.95,3.6,1.45,.72,16))

realize(scene)

# Configure the world only after realization, which clears Blender's scene.
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
background.inputs['Color'].default_value = (0.86, 0.88, 0.85, 1)
background.inputs['Strength'].default_value = .8

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0,-1.5,3.75), power=700, size=7, target=(0,0,0))
area_emitter((0,4.5,3.0), power=900, size=6, target=(0,-2,1.0))
area_emitter((4.7,0,3.2), power=500, size=5, target=(0,0,1.0))
