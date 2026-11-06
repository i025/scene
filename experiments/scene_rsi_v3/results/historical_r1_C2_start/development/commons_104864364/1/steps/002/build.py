# Reference inventory, estimated normalized image bounds:
# Cream classroom with yellow lower walls, pale tiled floor and white ceiling.
# Ceiling occupies roughly (0,0)-(1,.26), floor roughly (0,.42)-(1,1).
# Bright framed openings line the left wall; brown doors and windows line the right.
# Dark stage with burgundy curtain, green side curtains and pale scalloped valance
# occupies about (.37,.23)-(.66,.45); a green board overlaps its lower center.
# Rows of dark wooden school desks, thin legs and benches occupy the middle and
# foreground; prominent desks are at (.14,.59)-(.36,.89) and (.51,.52)-(.70,.82).
# Several blue and black backpacks lie on the floor and under desks.
# Ceiling fans, lights, wall speakers and framed notices are visible. Small details
# and geometry hidden behind furniture remain uncertain.
#
# Comparison with first render: the stage and foreground furniture were too small,
# the stage appeared too low, desk surfaces were too pale, bags were too spherical,
# and the nearest ceiling beam occupied too much of the top of the image. This
# revision adjusts framing and stage size, darkens furniture, makes upright bags,
# and moves the nearest beam out of view.
# Estimated expanded primitives: architecture and floor joints 75, side openings 55,
# stage 24, desks 24*6=144, seating 36, bags 30, fixtures 40; about 404 meshes.

from sceneact import *
import bpy
import math

scene = Scene('Classroom')

cream = (0.86, 0.85, 0.70)
yellow = (0.96, 0.67, 0.015)
white = (0.91, 0.91, 0.84)
darkwood = (0.19, 0.12, 0.065)
wood = (0.29, 0.20, 0.12)
black = (0.025, 0.032, 0.035)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

room = Asset('Architecture')
add(room, 'floor', (10, 18, .12), (0, 0, -.06), (.69, .55, .39))
add(room, 'ceiling', (10, 18, .12), (0, 0, 4.65), (.89, .90, .85))
for side in (-1, 1):
    x = side * 5
    add(room, 'lower_wall_'+str(side), (.14, 18, 1.35),
        (x, 0, .675), yellow)
    add(room, 'upper_wall_'+str(side), (.14, 18, 3.30),
        (x, 0, 3.0), cream)
add(room, 'back_wall', (10, .16, 4.65), (0, 8.95, 2.325), cream)
add(room, 'back_lower_band', (10, .08, 1.1), (0, 8.84, .55), yellow)

# Narrow joints give the tiled floor its regular perspective grid.
for i in range(-12, 13):
    add(room, 'floor_joint_x_'+str(i), (.009, 18, .004),
        (i*.4, 0, .004), (.57, .46, .34))
for j in range(-22, 23):
    add(room, 'floor_joint_y_'+str(j), (10, .009, .004),
        (0, j*.4, .005), (.57, .46, .34))
for y in (-8.8, -.4, 4.8):
    add(room, 'ceiling_beam_'+str(y), (10, .25, .14),
        (0, y, 4.52), white)
scene.include('architecture', room)

openings = Asset('Side_wall_openings')
for k, y in enumerate((-6.4, -3.3, -.2, 2.9, 5.8)):
    add(openings, 'left_window_light_'+str(k), (.035, 1.40, 2.50),
        (-4.90, y, 2.26), (.98, .98, .88))
    for dy in (-.73, .73):
        add(openings, 'left_frame_%d_%s'%(k,dy), (.10, .10, 2.65),
            (-4.82, y+dy, 2.25), wood)
    add(openings, 'left_lintel_'+str(k), (.10, 1.55, .12),
        (-4.82, y, 3.54), wood)
    add(openings, 'left_sill_'+str(k), (.13, 1.55, .10),
        (-4.80, y, .98), wood)
    add(openings, 'left_mullion_'+str(k), (.07, .06, 2.42),
        (-4.79, y, 2.25), wood)
for k, y in enumerate((-5.4, -1.8, 1.8, 5.3)):
    add(openings, 'right_door_'+str(k), (.045, 1.22, 2.65),
        (4.90, y, 1.84), (.29, .21, .14))
    for dy in (-.65, .65):
        add(openings, 'right_jamb_%d_%s'%(k,dy), (.12, .10, 2.75),
            (4.81, y+dy, 1.85), darkwood)
    add(openings, 'right_header_'+str(k), (.12, 1.4, .12),
        (4.81, y, 3.24), darkwood)
scene.include('windows_and_doors', openings)

stage = Asset('Stage_and_blackboard')
add(stage, 'platform', (6.4, 1.5, .22), (0, 8.0, .11), (.28, .19, .10))
add(stage, 'dark_opening', (6.35, .10, 2.65),
    (0, 8.78, 2.55), (.035, .027, .023))
add(stage, 'burgundy_curtain', (4.55, .06, 2.05),
    (0, 8.68, 2.90), (.12, .014, .018))
for x in (-2.85, 2.85):
    add(stage, 'green_side_curtain_'+str(x), (.48, .12, 2.65),
        (x, 8.58, 2.47), (.10, .26, .022))
add(stage, 'valance_top', (5.9, .12, .20), (0, 8.52, 3.84), (.88, .85, .73))
for i in range(13):
    stage.include('valance_fold_'+str(i),
        ball(radius=.14, center=(-2.75+i*.46, 8.48, 3.70),
             color=(.84, .81, .69)))
add(stage, 'blackboard_frame', (2.20, .09, 1.10),
    (0, 8.22, 1.64), (.58, .59, .48))
add(stage, 'blackboard', (2.07, .04, .97),
    (0, 8.15, 1.65), (.12, .25, .20))
for x in (-.82, .82):
    add(stage, 'board_support_'+str(x), (.045, .05, .72),
        (x, 8.24, .83), darkwood)
add(stage, 'blue_object_on_stage', (.45, .34, 1.00),
    (2.15, 8.1, .72), (.29, .63, .79))
scene.include('stage', stage)

def desk(name, x, y, width=1.55, depth=.66):
    a = Asset(name)
    add(a, 'top', (width, depth, .09), (x, y, .83), (.25, .18, .11))
    for dx in (-width/2+.08, width/2-.08):
        for dy in (-depth/2+.07, depth/2-.07):
            add(a, 'leg_%s_%s'%(dx,dy), (.06, .06, .79),
                (x+dx, y+dy, .395), (.27, .19, .11))
    add(a, 'under_top_rail', (width-.10, .055, .10),
        (x, y+.22, .69), darkwood)
    scene.include(name, a)

rows = (-6.0, -3.8, -1.6, .6, 2.8, 4.8, 6.3)
for r, y in enumerate(rows):
    desk('left_desk_%02d'%r, -1.85, y, 1.60, .68)
    desk('right_desk_%02d'%r, 1.40, y+.35, 1.70, .68)
    if r in (0, 1, 2, 3, 4):
        desk('outer_left_desk_%02d'%r, -4.0, y+.9, 1.25, .61)
        desk('outer_right_desk_%02d'%r, 3.95, y+1.05, 1.28, .61)

seats = Asset('Seats_and_benches')
for r, y in enumerate((-5.1, -2.9, -.7, 1.5, 3.7, 5.6)):
    for c, x in enumerate((-1.85, 1.4)):
        add(seats, 'seat_%d_%d'%(r,c), (1.25, .27, .07),
            (x, y, .46), (.20, .14, .08))
        for dx in (-.52, .52):
            add(seats, 'seat_leg_%d_%d_%s'%(r,c,dx), (.045, .045, .45),
                (x+dx, y, .225), darkwood)
scene.include('seating', seats)

# Flattened rounded bodies with pockets and straps suggest upright fabric backpacks.
bags = Asset('School_bags')
for i, (x,y,col) in enumerate([
    (-2.9,-6.7,(.018,.035,.052)),
    (2.25,-6.1,(.015,.22,.48)),
    (3.55,-3.9,(.015,.26,.46)),
    (.45,-4.0,(.018,.026,.028)),
    (-3.2,-2.5,(.025,.14,.25)),
    (3.1,.3,(.025,.20,.33))
]):
    body = ball(radius=1, center=(x,y,.36), color=col)
    body.resize((.30,.19,.39))
    bags.include('bag_body_'+str(i), body)
    add(bags, 'bag_front_pocket_'+str(i), (.38,.08,.25),
        (x,y-.19,.24), tuple(min(1,v*1.20) for v in col))
    bags.include('bag_handle_'+str(i),
        rod(radius=.022, start=(x-.10,y,.71), end=(x+.10,y,.71), color=black))
    bags.include('bag_strap_'+str(i),
        rod(radius=.018, start=(x+.18,y-.03,.57),
            end=(x+.32,y-.05,.12), color=black))
scene.include('bags', bags)

fixtures = Asset('Ceiling_and_wall_fixtures')
for n, (x,y) in enumerate(((-2.6,-5.2),(2.6,-4.8),(-1.8,1.4),(2.5,2.2))):
    fixtures.include('fan_stem_'+str(n),
        rod(radius=.035, start=(x,y,4.53), end=(x,y,4.12), color=black))
    fixtures.include('fan_hub_'+str(n),
        ball(radius=.105, center=(x,y,4.10), color=black))
    for blade in range(3):
        angle = blade*2*math.pi/3 + .3
        dx, dy = math.cos(angle), math.sin(angle)
        b = box(size=(.85,.14,.035),
                center=(x+dx*.50,y+dy*.50,4.10),
                color=(.17,.15,.13))
        b.turn(axis='+z', degrees=angle*180/math.pi)
        fixtures.include('fan_blade_%d_%d'%(n,blade), b)
for n,y in enumerate((-3.3, 2.5, 6.4)):
    add(fixtures, 'fluorescent_'+str(n), (1.6,.13,.055),
        (0,y,4.54), (1,1,.93))
for n,(x,y) in enumerate(((-4.77,1.1),(4.77,1.1))):
    add(fixtures, 'speaker_'+str(n), (.20,.58,.70),
        (x,y,3.2), (.035,.045,.042))
for n,(x,y) in enumerate(((-4.78,-3.9),(4.78,-3.5),(4.78,3.4))):
    add(fixtures, 'notice_frame_'+str(n), (.08,.50,.64),
        (x,y,3.6), (.27,.24,.19))
    add(fixtures, 'notice_paper_'+str(n), (.09,.40,.53),
        (x + (.055 if x<0 else -.055),y,3.6), (.84,.87,.79))
scene.include('fixtures', fixtures)

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
background.inputs['Color'].default_value = (.78, .81, .83, 1)
background.inputs['Strength'].default_value = .65

set_view((0,-12.7,2.65), (0,3.1,.95), lens=30, sensor=36)
area_emitter((0,-3,4.25), power=1100, size=7, target=(0,1,0))
area_emitter((0,5,4.2), power=900, size=6, target=(0,5,0))
area_emitter((-4.1,-1,3.0), power=550, size=5, target=(0,1,1))
