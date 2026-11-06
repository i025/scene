# Reference inventory (normalized image coordinates, approximate):
# Classroom: pale ceiling (0,0)-(1,.25), cream walls with yellow lower band,
# and warm square-tiled floor (0,.43)-(1,1). Left windows and right doors
# recede toward the dark stage. The stage (.37,.23)-(.66,.45) has green
# side drapes, a pale valance, dark burgundy curtain and a green board.
# Dark wooden desks with open leg frames and benches fill the middle and
# foreground. Principal desks occupy (.14,.59)-(.36,.89) and
# (.51,.52)-(.70,.82). Bags sit at (.09,.72), (.49,.64), (.64,.69)
# and (.76,.60). Ceiling fans, lights, wall speakers and framed notices
# are visible. Furniture behind other furniture and small wall details are
# uncertain.
#
# Comparison with the second rendering: the main scene features sit too low
# in the frame, the stage is too narrow and light, desk surfaces and frames
# lack the reference's dark contrast, and the floor is too gray. Aim the
# camera higher, widen and darken the stage, darken desks, and warm the floor.
# The repeated desks, wall openings, bags and fixtures retain editable parts.
# Estimated primitive count: room and tile joints 80, openings 46, stage 27,
# desks 24*6 = 144, benches 36, bags 24, fixtures 35; approximately 392.
# No Boolean operations or expanded fillets are used.

from sceneact import *
import bpy
import math

scene = Scene('Classroom')

cream = (.87, .85, .72)
yellow = (.98, .68, .008)
white = (.91, .91, .85)
darkwood = (.12, .075, .042)
wood = (.23, .15, .085)
black = (.014, .021, .024)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

room = Asset('Architecture')
add(room, 'floor', (10, 18, .12), (0, 0, -.06), (.74, .61, .46))
add(room, 'ceiling', (10, 18, .12), (0, 0, 4.65), (.90, .90, .85))
for side in (-1, 1):
    x = side * 5
    add(room, 'lower_wall_' + str(side), (.14, 18, 1.35),
        (x, 0, .675), yellow)
    add(room, 'upper_wall_' + str(side), (.14, 18, 3.30),
        (x, 0, 3.0), cream)
add(room, 'back_wall', (10, .16, 4.65), (0, 8.95, 2.325), cream)
add(room, 'back_lower_band', (10, .08, 1.1), (0, 8.84, .55), yellow)

for i in range(-12, 13):
    add(room, 'floor_joint_x_' + str(i), (.008, 18, .004),
        (i * .4, 0, .004), (.64, .51, .39))
for j in range(-22, 23):
    add(room, 'floor_joint_y_' + str(j), (10, .008, .004),
        (0, j * .4, .005), (.64, .51, .39))
for y in (-8.8, -.4, 4.8):
    add(room, 'ceiling_beam_' + str(y), (10, .25, .14),
        (0, y, 4.52), white)
scene.include('architecture', room)

openings = Asset('Side_wall_openings')
for k, y in enumerate((-6.4, -3.3, -.2, 2.9, 5.8)):
    add(openings, 'left_window_light_' + str(k), (.035, 1.40, 2.50),
        (-4.90, y, 2.26), (.99, .99, .91))
    for dy in (-.73, .73):
        add(openings, 'left_frame_%d_%s' % (k, dy), (.10, .10, 2.65),
            (-4.82, y + dy, 2.25), wood)
    add(openings, 'left_lintel_' + str(k), (.10, 1.55, .12),
        (-4.82, y, 3.54), wood)
    add(openings, 'left_sill_' + str(k), (.13, 1.55, .10),
        (-4.80, y, .98), wood)
    add(openings, 'left_mullion_' + str(k), (.07, .06, 2.42),
        (-4.79, y, 2.25), wood)
for k, y in enumerate((-5.4, -1.8, 1.8, 5.3)):
    add(openings, 'right_door_' + str(k), (.045, 1.22, 2.65),
        (4.90, y, 1.84), (.25, .17, .10))
    for dy in (-.65, .65):
        add(openings, 'right_jamb_%d_%s' % (k, dy), (.12, .10, 2.75),
            (4.81, y + dy, 1.85), darkwood)
    add(openings, 'right_header_' + str(k), (.12, 1.4, .12),
        (4.81, y, 3.24), darkwood)
scene.include('windows_and_doors', openings)

stage = Asset('Stage_and_blackboard')
add(stage, 'platform', (7.2, 1.5, .22), (0, 8.0, .11), (.22, .14, .07))
add(stage, 'dark_opening', (7.15, .10, 2.65),
    (0, 8.78, 2.55), (.012, .010, .009))
add(stage, 'burgundy_curtain', (5.1, .06, 2.05),
    (0, 8.68, 2.90), (.045, .006, .009))
for x in (-3.25, 3.25):
    add(stage, 'green_side_curtain_' + str(x), (.48, .12, 2.65),
        (x, 8.58, 2.47), (.07, .20, .015))
add(stage, 'valance_top', (6.7, .12, .20), (0, 8.52, 3.84),
    (.88, .85, .73))
for i in range(15):
    stage.include('valance_fold_' + str(i),
        ball(radius=.14, center=(-3.22 + i * .46, 8.48, 3.70),
             color=(.84, .81, .69)))
add(stage, 'blackboard_frame', (2.20, .09, 1.10),
    (0, 8.22, 1.64), (.58, .59, .48))
add(stage, 'blackboard', (2.07, .04, .97),
    (0, 8.15, 1.65), (.08, .20, .15))
for x in (-.82, .82):
    add(stage, 'board_support_' + str(x), (.045, .05, .72),
        (x, 8.24, .83), darkwood)
add(stage, 'blue_object_on_stage', (.45, .34, 1.00),
    (2.5, 8.1, .72), (.29, .63, .79))
scene.include('stage', stage)

def desk(name, x, y, width=1.55, depth=.66):
    a = Asset(name)
    add(a, 'top', (width, depth, .09), (x, y, .83), (.14, .095, .058))
    for dx in (-width / 2 + .08, width / 2 - .08):
        for dy in (-depth / 2 + .07, depth / 2 - .07):
            add(a, 'leg_%s_%s' % (dx, dy), (.06, .06, .79),
                (x + dx, y + dy, .395), (.19, .13, .075))
    add(a, 'under_top_rail', (width - .10, .055, .10),
        (x, y + .22, .69), darkwood)
    scene.include(name, a)

rows = (-6.0, -3.8, -1.6, .6, 2.8, 4.8, 6.3)
for r, y in enumerate(rows):
    desk('left_desk_%02d' % r, -1.85, y, 1.60, .68)
    desk('right_desk_%02d' % r, 1.40, y + .35, 1.70, .68)
    if r in (0, 1, 2, 3, 4):
        desk('outer_left_desk_%02d' % r, -4.0, y + .9, 1.25, .61)
        desk('outer_right_desk_%02d' % r, 3.95, y + 1.05, 1.28, .61)

seats = Asset('Seats_and_benches')
for r, y in enumerate((-5.1, -2.9, -.7, 1.5, 3.7, 5.6)):
    for c, x in enumerate((-1.85, 1.4)):
        add(seats, 'seat_%d_%d' % (r, c), (1.25, .27, .07),
            (x, y, .46), (.14, .09, .05))
        for dx in (-.52, .52):
            add(seats, 'seat_leg_%d_%d_%s' % (r, c, dx), (.045, .045, .45),
                (x + dx, y, .225), darkwood)
scene.include('seating', seats)

bags = Asset('School_bags')
for i, (x, y, col) in enumerate([
    (-2.9, -6.7, (.008, .018, .028)),
    (2.25, -6.1, (.008, .16, .38)),
    (3.55, -3.9, (.008, .21, .37)),
    (.45, -4.0, (.008, .015, .017)),
    (-3.2, -2.5, (.015, .10, .20)),
    (3.1, .3, (.015, .15, .26))
]):
    body = ball(radius=1, center=(x, y, .36), color=col)
    body.resize((.27, .18, .39))
    bags.include('bag_body_' + str(i), body)
    add(bags, 'bag_front_pocket_' + str(i), (.34, .08, .25),
        (x, y - .18, .24), tuple(min(1, v * 1.25) for v in col))
    bags.include('bag_handle_' + str(i),
        rod(radius=.022, start=(x - .10, y, .71),
            end=(x + .10, y, .71), color=black))
    bags.include('bag_strap_' + str(i),
        rod(radius=.018, start=(x + .17, y - .03, .57),
            end=(x + .31, y - .05, .12), color=black))
scene.include('bags', bags)

fixtures = Asset('Ceiling_and_wall_fixtures')
for n, (x, y) in enumerate(((-2.6, -5.2), (2.6, -4.8),
                             (-1.8, 1.4), (2.5, 2.2))):
    fixtures.include('fan_stem_' + str(n),
        rod(radius=.035, start=(x, y, 4.53), end=(x, y, 4.12), color=black))
    fixtures.include('fan_hub_' + str(n),
        ball(radius=.105, center=(x, y, 4.10), color=black))
    for blade in range(3):
        angle = blade * 2 * math.pi / 3 + .3
        dx, dy = math.cos(angle), math.sin(angle)
        b = box(size=(.85, .14, .035),
                center=(x + dx * .50, y + dy * .50, 4.10),
                color=(.13, .11, .09))
        b.turn(axis='+z', degrees=angle * 180 / math.pi)
        fixtures.include('fan_blade_%d_%d' % (n, blade), b)
for n, y in enumerate((-3.3, 2.5, 6.4)):
    add(fixtures, 'fluorescent_' + str(n), (1.6, .13, .055),
        (0, y, 4.54), (1, 1, .93))
for n, (x, y) in enumerate(((-4.77, 1.1), (4.77, 1.1))):
    add(fixtures, 'speaker_' + str(n), (.20, .58, .70),
        (x, y, 3.2), (.025, .035, .032))
for n, (x, y) in enumerate(((-4.78, -3.9), (4.78, -3.5), (4.78, 3.4))):
    add(fixtures, 'notice_frame_' + str(n), (.08, .50, .64),
        (x, y, 3.6), (.27, .24, .19))
    add(fixtures, 'notice_paper_' + str(n), (.09, .40, .53),
        (x + (.055 if x < 0 else -.055), y, 3.6), (.84, .87, .79))
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

set_view((0, -12.7, 2.65), (0, 3.1, 1.55), lens=30, sensor=36)
area_emitter((0, -3, 4.25), power=1100, size=7, target=(0, 1, 0))
area_emitter((0, 5, 4.2), power=900, size=6, target=(0, 5, 0))
area_emitter((-4.1, -1, 3.0), power=550, size=5, target=(0, 1, 1))
