# Reference inventory and anchors, normalized image coordinates, estimated:
# Ceiling occupies y=0–.32, with closely spaced, nearly horizontal board seams.
# Rear window header is at y~.31, meeting the right wall at x~.65. Bright
# windows extend to y~.54, behind tables and a small plant. Right window
# header rises toward the right edge.
# Foreground tabletop occupies x=0–.46, y=.84–1. Dark booth backs occupy
# x=0–.33, y=.53–.90, with pale table surfaces between them.
# Dining tables and pedestal chairs occupy x=.38–.89, y=.52–1. Chair backs
# overlap the tables, and the foreground chairs obscure some supports.
# Nearest pendant occupies x=.02–.23, y=.12–.40. Smaller shades recede
# across the windows. Right palm occupies x=.78–1, y=.40–1; individual
# leaves and the planter are partly occluded.
#
# Comparison with second render:
# Rear corner is near (.68,.35), versus reference (.65,.31); the rear header
# is almost horizontal in both. Rendered foreground tabletop ends near x=.28,
# versus .46 in the reference. Rendered closest pendant is almost entirely
# cropped at x=0, y~.43–.53, versus reference x=.02–.23, y=.12–.40.
# Rendered foreground chairs end around y=.91, versus the reference reaching
# the bottom edge. The rendered palm occupies about x=.72–.97, y=.49–.77;
# the reference foliage is taller, darker, and continues to the bottom edge.
# Rendered ceiling seams converge strongly; reference seams run mostly across
# the image. Window brightness also depends on lighting and orientation.
#
# Ranked revisions:
# 1. Move the nearest pendant right and raise its shade: its silhouette should
#    enter the upper-left frame and grow above the window, without moving the
#    already reasonably placed rear pendants.
# 2. Widen and shift the foreground tabletop right, and bring the closest
#    chairs forward, extending their contours toward the lower image edge.
# 3. Enlarge and move the palm toward the camera, extending foliage upward and
#    downward while retaining visible gaps between fronds.
# 4. Change ceiling seams to run across the room. Lower the camera target
#    slightly so the rear header moves upward while retaining its edge slope.
# Expanded primitive estimate: room 105, booths 20, tables 44, chairs 126,
# lights 48, foreground palm 145, rear plant 33; total approximately 521.
# Each rod, box, or ball emits one mesh; no Boolean or fillet expansions.

from sceneact import *
import bpy
import math

scene = Scene('Restaurant interior')

CAMERA_POSITION = (0.15, -9.8, 3.05)
CAMERA_TARGET = (1.1, 3.0, 1.70)
CAMERA_LENS = 25
ROOM_WIDTH = 10.6
ROOM_DEPTH = 13.0
ROOM_HEIGHT = 4.0
BACK_Y = 5.1
RIGHT_X = ROOM_WIDTH / 2

ivory = (.72, .73, .70)
ceiling_color = (.77, .78, .75)
floor_color = (.105, .12, .115)
grout = (.29, .31, .29)
frame = (.12, .14, .13)
window = (.93, .95, .92)
table_color = (.69, .71, .68)
upholstery = (.115, .13, .125)
metal = (.10, .12, .11)
leaf_color = (.055, .075, .06)
leaf_light = (.11, .14, .105)

room = Asset('architecture')
room.include('floor', box((ROOM_WIDTH, ROOM_DEPTH, .12),
                          center=(0, -.7, -.06), color=floor_color))
room.include('ceiling', box((ROOM_WIDTH, ROOM_DEPTH, .10),
                            center=(0, -.7, ROOM_HEIGHT + .05),
                            color=ceiling_color))
room.include('back_low_wall', box((ROOM_WIDTH, .14, .78),
                                  center=(0, BACK_Y, .39), color=ivory))
room.include('back_header', box((ROOM_WIDTH, .14, .45),
                                center=(0, BACK_Y, 3.77), color=ivory))
room.include('right_low_wall', box((.14, ROOM_DEPTH, .75),
                                   center=(RIGHT_X, -.7, .375), color=ivory))
room.include('right_header', box((.14, ROOM_DEPTH, .4),
                                 center=(RIGHT_X, -.7, 3.8), color=ivory))
room.include('rear_bright_glazing', box((10.35, .035, 2.70),
                                        center=(0, BACK_Y + .03, 2.15),
                                        color=window))
for i, x in enumerate([-5.15, -3.15, -1.05, 1.05, 3.15, 5.15]):
    room.include('rear_mullion_%d' % i,
                 box((.075, .12, 2.9), center=(x, BACK_Y-.055, 2.17),
                     color=frame))
for z in (.77, 3.53):
    room.include('rear_rail_%.2f' % z,
                 box((10.5, .12, .075), center=(0, BACK_Y-.06, z),
                     color=frame))
room.include('right_bright_glazing',
             box((.035, 12.8, 2.72), center=(RIGHT_X+.03, -.7, 2.15),
                 color=window))
for i, y in enumerate([-6.9, -4.5, -2.1, .3, 2.7, 5.0]):
    room.include('right_mullion_%d' % i,
                 box((.12, .075, 2.88), center=(RIGHT_X-.05, y, 2.15),
                     color=frame))
for z in (.77, 3.53):
    room.include('right_rail_%.2f' % z,
                 box((.12, 12.8, .075), center=(RIGHT_X-.05, -.7, z),
                     color=frame))

for i in range(32):
    y = -6.9 + i*.39
    room.include('ceiling_board_joint_%02d' % i,
                 box((10.5, .009, .008), center=(0, y, 3.993),
                     color=(.55, .56, .54)))
for i in range(19):
    x = -5.1 + i*.56
    room.include('floor_long_joint_%02d' % i,
                 box((.012, 12.8, .006), center=(x, -.7, .006),
                     color=grout))
for i in range(17):
    y = -6.7 + i*.75
    room.include('floor_cross_joint_%02d' % i,
                 box((10.4, .012, .006), center=(0, y, .008),
                     color=grout))
scene.include('room', room)

booths = Asset('left_booths')
for i, y in enumerate([-5.1, -2.85, -.6, 1.65, 3.8]):
    booth = Asset('booth_%d' % i)
    booth.include('back', box((3.0, .16, 1.16),
                              center=(-3.82, y, .79), color=upholstery))
    booth.include('seat', box((2.85, .73, .14),
                              center=(-3.82, y+.47, .48),
                              color=(.17, .19, .18)))
    booth.include('plinth', box((2.65, .48, .36),
                                center=(-3.82, y+.42, .20), color=metal))
    booth.include('top_trim', box((3.0, .17, .035),
                                  center=(-3.82, y, 1.38),
                                  color=(.26, .28, .26)))
    booths.include('booth_%d' % i, booth)
scene.include('booths', booths)

def make_table(name, x, y, sx=1.45, sy=.88):
    a = Asset(name)
    a.include('light_tabletop',
              box((sx, sy, .065), center=(x, y, .78), color=table_color))
    a.include('edge',
              box((sx, sy, .035), center=(x, y, .727),
                  color=(.25, .27, .25)))
    a.include('pedestal',
              rod(.055, start=(x, y, .08), end=(x, y, .73), color=metal))
    a.include('foot',
              box((.62, .48, .045), center=(x, y, .055), color=metal))
    return a

tables = Asset('dining_tables')
table_positions = [
    (-2.55, -6.45, 5.4, 1.75), (-3.7, -3.85, 2.65, .8),
    (-3.7, -1.65, 2.55, .75), (-3.7, .6, 2.45, .72),
    (-.65, -3.55, 1.55, .9), (1.72, -3.35, 1.55, .9),
    (-.65, .1, 1.45, .84), (1.72, .35, 1.45, .84),
    (-.65, 2.65, 1.4, .8), (1.72, 2.8, 1.4, .8),
    (3.65, 1.25, 1.22, .78)]
for i, (x, y, sx, sy) in enumerate(table_positions):
    tables.include('table_%02d' % i,
                   make_table('table_%02d' % i, x, y, sx, sy))
scene.include('tables', tables)

def make_chair(name, x, y, facing=1):
    a = Asset(name)
    back_y = y - facing*.29
    a.include('seat', box((.72, .67, .10), center=(x, y, .52),
                          color=upholstery))
    a.include('back', box((.74, .105, .88), center=(x, back_y, .99),
                          color=upholstery))
    a.include('back_edge', box((.77, .12, .035),
                               center=(x, back_y, 1.42),
                               color=(.25, .27, .25)))
    a.include('stem', rod(.045, start=(x, y, .07), end=(x, y, .49),
                          color=metal))
    a.include('base', rod(.25, length=.055, center=(x, y, .055),
                          color=metal))
    for j, dx in enumerate([-.29, .29]):
        a.include('support_%d' % j,
                  rod(.022, start=(x+dx, y-.24, .12),
                      end=(x+dx, y-.24, .49), color=metal))
    return a

chairs = Asset('restaurant_chairs')
chair_positions = [
    (-.72, -4.85, 1), (1.74, -4.7, 1), (3.18, -4.5, 1),
    (-1.55, -2.35, -1), (.20, -2.35, -1), (1.75, -2.20, -1),
    (-.75, -.73, 1), (1.70, -.48, 1), (3.52, .35, 1),
    (-1.42, .83, -1), (.15, .83, -1), (1.70, 1.15, -1),
    (-.75, 1.93, 1), (1.68, 2.04, 1), (3.55, 2.02, -1),
    (-1.38, 3.33, -1), (.05, 3.33, -1), (1.7, 3.52, -1)]
for i, (x, y, facing) in enumerate(chair_positions):
    chairs.include('chair_%02d' % i,
                   make_chair('chair_%02d' % i, x, y, facing))
scene.include('chairs', chairs)

def pendant(name, x, y, bottom, r):
    a = Asset(name)
    top = bottom + .60*r
    a.include('cord', rod(.012, start=(x, y, top), end=(x, y, 3.99),
                          color=(.12, .13, .12)))
    a.include('ceiling_cap', rod(.075, length=.025,
                                 center=(x, y, 3.97), color=metal))
    dome = ball(1, center=(x, y, bottom+.12*r),
                color=(.025, .035, .03))
    dome.resize((r, r, .39*r))
    a.include('rounded_shade', dome)
    a.include('shade_rim',
              rod(r*.99, length=.045, center=(x, y, bottom+.035),
                  color=(.025, .035, .03)))
    a.include('shade_neck',
              rod(r*.32, length=.30*r, center=(x, y, bottom+.43*r),
                  color=(.035, .045, .04)))
    a.include('underside',
              rod(r*.88, length=.012, center=(x, y, bottom+.008),
                  color=(.36, .38, .35)))
    return a

lamps = Asset('hanging_lights')
for i, (x, y, z, r) in enumerate([
    (-1.85, -5.5, 3.12, .78), (-3.65, -.1, 2.76, .39),
    (-3.55, 3.45, 2.72, .29), (-.75, 3.8, 2.67, .26),
    (1.0, 2.7, 2.67, .36), (2.72, 3.7, 2.68, .24),
    (3.62, 1.55, 2.67, .46), (4.65, 3.4, 2.68, .27)]):
    lamps.include('pendant_%d' % i, pendant('pendant_%d' % i, x, y, z, r))
scene.include('pendants', lamps)

palm = Asset('foreground_palm')
px, py = 4.1, -4.0
palm.include('planter', rod(.40, length=.58, center=(px, py, .29),
                            color=(.12, .14, .12)))
for i in range(11):
    angle = 2*math.pi*i/11 + .17
    dx, dy = math.cos(angle), math.sin(angle)
    base = (px, py, .48)
    root = (px+dx*.12, py+dy*.12, 1.12)
    mid = (px+dx*.65, py+dy*.65, 2.10+.11*(i % 3))
    tip = (px+dx*1.42, py+dy*1.42, 2.38+.11*(i % 3))
    palm.include('stalk_%02d' % i,
                 rod(.016, start=base, end=root, color=leaf_color))
    palm.include('frond_lower_%02d' % i,
                 rod(.012, start=root, end=mid, color=leaf_color))
    palm.include('frond_upper_%02d' % i,
                 rod(.009, start=mid, end=tip, color=leaf_color))
    for j in range(5):
        t = .12 + .17*j
        cx = mid[0]*(1-t)+tip[0]*t
        cy = mid[1]*(1-t)+tip[1]*t
        cz = mid[2]*(1-t)+tip[2]*t
        length = .52*(1-.5*t)
        for side in (-1, 1):
            ex = cx + side*(-dy)*length + dx*.18
            ey = cy + side*dx*length + dy*.18
            ez = cz - .20
            palm.include('leaflet_%02d_%d_%d' % (i, j, side),
                         rod(.022, start=(cx, cy, cz), end=(ex, ey, ez),
                             color=leaf_light if (i+j) % 4 == 0 else leaf_color))
scene.include('foreground_plant', palm)

rear = Asset('rear_plant')
rx, ry = -1.95, 3.6
rear.include('pot', rod(.22, length=.35, center=(rx, ry, .175), color=metal))
for i in range(16):
    angle = i*2.399
    radial = .25 + .45*((i*7) % 11)/10
    tx = rx + math.cos(angle)*radial
    ty = ry + math.sin(angle)*radial
    tz = .75 + .65*((i*5) % 13)/12
    rear.include('stem_%02d' % i,
                 rod(.009, start=(rx, ry, .3), end=(tx, ty, tz),
                     color=leaf_color))
    leaf = ball(1, center=(tx, ty, tz), color=leaf_light)
    leaf.resize((.09, .16, .025))
    leaf.turn(axis='+z', degrees=math.degrees(angle))
    rear.include('leaf_%02d' % i, leaf)
scene.include('rear_plant', rear)

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
sc.world.node_tree.links.new(background.outputs['Background'],
                             output.inputs['Surface'])
background.inputs['Color'].default_value = (.86, .88, .85, 1)
background.inputs['Strength'].default_value = .55

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -1.5, 3.75), power=450, size=7, target=(0, 0, 0))
area_emitter((0, 4.5, 3.0), power=650, size=6, target=(0, -2, 1.0))
area_emitter((4.7, 0, 3.2), power=320, size=5, target=(0, 0, 1.0))
