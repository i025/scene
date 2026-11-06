# Reference inventory, approximate normalized image bounds:
# Room: tiled floor (0,.42)-(1,1), cream upper and yellow lower side walls,
# white ceiling with beams; back wall and raised dark stage at (.37,.23)-(.65,.45).
# Left wall: tall bright windows and brown frames (.00,.15)-(.33,.52);
# right wall: tall brown doors/windows and small wall fixtures (.67,.13)-(1,.57).
# Furniture: many brown school desks in rows, with thin tops and open four-legged
# frames, receding toward stage; foreground desks at (.13,.58)-(.36,.90) and
# (.50,.51)-(.70,.83). Chairs and benches overlap and obscure some frames.
# Back stage: burgundy curtains, black recess, green side curtains, green board,
# pale valance, and a small blue-and-white object at right.
# Several blue/black school bags rest on the floor, notably at (.64,.69)-(.72,.86),
# (.09,.72)-(.18,.90), and (.76,.61)-(.83,.75).
# Ceiling fans and fluorescent lights are visible overhead. Wall signs, dark
# speakers, and small framed pictures are visible, but their details are uncertain.
# Occluded desk/chair geometry and objects outside the photograph are approximate.
#
# Primitive estimate: architecture ~45, tiles as thin strips ~30, stage ~12,
# desks 22 x 6 = 132, benches/chairs ~45, bags ~12, fixtures ~35:
# approximately 310 primitive meshes total. No boolean operations.

from sceneact import *
import bpy
import math

scene = Scene('Classroom')

cream = (0.86, 0.85, 0.70)
yellow = (0.97, 0.71, 0.025)
white = (0.91, 0.91, 0.84)
darkwood = (0.25, 0.16, 0.095)
wood = (0.39, 0.29, 0.18)
frame = (0.30, 0.22, 0.13)
black = (0.035, 0.042, 0.045)
green = (0.11, 0.29, 0.20)
blue = (0.02, 0.31, 0.57)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# The room's long axis is Y, with the camera at the near end.
room = Asset('Architecture')
add(room, 'floor', (10.0, 18.0, .12), (0, 0, -.06), (0.68, 0.57, 0.43))
add(room, 'ceiling', (10, 18, .12), (0, 0, 4.65), (0.88, 0.89, 0.83))
# Side walls are present behind the windows and door panels.
for side in (-1, 1):
    x = side * 5
    add(room, 'lower_wall_'+str(side), (.14, 18, 1.35), (x, 0, .675), yellow)
    add(room, 'upper_wall_'+str(side), (.14, 18, 3.30), (x, 0, 3.0), cream)
add(room, 'back_wall', (10, .16, 4.65), (0, 8.95, 2.325), cream)
add(room, 'back_lower_band', (10, .08, 1.1), (0, 8.84, .55), yellow)
# Floor tile joints are subtle, and converge naturally in perspective.
for i in range(-12, 13):
    add(room, 'floor_joint_x_'+str(i), (.012, 18, .004),
        (i*.4, 0, .004), (0.54, 0.45, 0.34))
for j in range(-22, 23):
    add(room, 'floor_joint_y_'+str(j), (10, .012, .004),
        (0, j*.4, .005), (0.54, 0.45, 0.34))
for y in (-5.7, -.4, 4.8):
    add(room, 'ceiling_beam_'+str(y), (10, .30, .20), (0, y, 4.48), white)
scene.include('architecture', room)

# Windows on the left, dark brown door/window units on the right.
windows = Asset('Side_wall_openings')
for k, y in enumerate((-6.4, -3.3, -.2, 2.9, 5.8)):
    add(windows, 'left_window_light_'+str(k), (.035, 1.40, 2.50),
        (-4.90, y, 2.26), (0.98, 0.98, 0.87))
    for dy in (-.73, .73):
        add(windows, 'left_frame_'+str(k)+'_'+str(dy), (.10, .10, 2.65),
            (-4.82, y+dy, 2.25), darkwood)
    add(windows, 'left_lintel_'+str(k), (.10, 1.55, .12),
        (-4.82, y, 3.54), wood)
    add(windows, 'left_sill_'+str(k), (.13, 1.55, .10),
        (-4.80, y, .98), wood)
    add(windows, 'left_mullion_'+str(k), (.07, .06, 2.42),
        (-4.79, y, 2.25), wood)
for k, y in enumerate((-5.4, -1.8, 1.8, 5.3)):
    add(windows, 'right_door_'+str(k), (.045, 1.22, 2.65),
        (4.90, y, 1.84), (0.31, 0.23, 0.16))
    for dy in (-.65, .65):
        add(windows, 'right_jamb_'+str(k)+'_'+str(dy), (.12, .10, 2.75),
            (4.81, y+dy, 1.85), (0.23, 0.16, 0.10))
    add(windows, 'right_header_'+str(k), (.12, 1.4, .12),
        (4.81, y, 3.24), darkwood)
scene.include('windows_and_doors', windows)

# Raised performance area at the far end.
stage = Asset('Stage_and_blackboard')
add(stage, 'platform', (5.5, 1.5, .22), (0, 8.0, .11), (0.31, 0.21, 0.12))
add(stage, 'stage_dark_opening', (5.3, .10, 2.35), (0, 8.78, 2.55), (0.055, 0.045, 0.035))
add(stage, 'burgundy_curtain', (3.55, .06, 1.75), (0, 8.68, 2.95), (0.18, 0.035, 0.035))
for x in (-2.35, 2.35):
    add(stage, 'green_side_curtain_'+str(x), (.47, .12, 2.5),
        (x, 8.58, 2.48), (0.12, 0.29, 0.045))
add(stage, 'valance', (4.8, .12, .34), (0, 8.52, 3.70), (0.86, 0.83, 0.68))
add(stage, 'blackboard_frame', (2.05, .09, 1.05), (0, 8.22, 1.65), (0.62, 0.61, 0.49))
add(stage, 'blackboard', (1.92, .04, .92), (0, 8.15, 1.66), (0.17, 0.31, 0.27))
add(stage, 'board_support_left', (.045, .05, .72), (-.75, 8.24, .86), darkwood)
add(stage, 'board_support_right', (.045, .05, .72), (.75, 8.24, .86), darkwood)
add(stage, 'blue_object_on_stage', (.42, .34, .95), (1.85, 8.1, .71), (0.31, 0.65, 0.80))
scene.include('stage', stage)

# Individual desks retain their tops, open frames and shelf/bench components.
def desk(name, x, y, width=1.55, depth=.66):
    a = Asset(name)
    add(a, 'top', (width, depth, .09), (x, y, .83), (0.35, 0.27, 0.19))
    for dx in (-width/2+.08, width/2-.08):
        for dy in (-depth/2+.07, depth/2-.07):
            add(a, 'leg_'+str(dx)+'_'+str(dy), (.055, .055, .79),
                (x+dx, y+dy, .395), (0.30, 0.23, 0.15))
    add(a, 'under_top_rail', (width-.10, .055, .10), (x, y+.22, .69), darkwood)
    scene.include(name, a)

# Two main blocks separated by a center aisle, plus side desks.
rows = (-6.0, -3.8, -1.6, .6, 2.8, 4.8, 6.3)
for r, y in enumerate(rows):
    desk('left_desk_%02d'%r, -1.85, y, 1.60, .68)
    desk('right_desk_%02d'%r, 1.40, y+.35, 1.70, .68)
    if r in (0, 1, 2, 3, 4):
        desk('outer_left_desk_%02d'%r, -4.0, y+.9, 1.25, .61)
        desk('outer_right_desk_%02d'%r, 3.95, y+1.05, 1.28, .61)

# Seats are simple dark horizontal boards on slender supports, behind desks.
seats = Asset('Seats_and_benches')
for r, y in enumerate((-5.1, -2.9, -.7, 1.5, 3.7, 5.6)):
    for c, x in enumerate((-1.85, 1.4)):
        add(seats, 'seat_%d_%d'%(r,c), (1.25, .27, .07),
            (x, y, .46), (0.26, 0.19, 0.12))
        for dx in (-.52, .52):
            add(seats, 'seat_leg_%d_%d_%s'%(r,c,dx), (.045, .045, .45),
                (x+dx, y, .225), darkwood)
scene.include('seating', seats)

# Backpacks are clustered under and next to the closest desks.
bags = Asset('School_bags')
for i, (x,y,col) in enumerate([
    (-2.9,-6.7,(.025,.06,.09)), (2.25,-6.1,(.02,.27,.55)),
    (3.55,-3.9,(.025,.35,.55)), (.45,-4.0,(.025,.04,.045)),
    (-3.2,-2.5,(.03,.20,.34)), (3.1,.3,(.03,.25,.40))
]):
    bags.include('bag_body_'+str(i), ball(radius=.32, center=(x,y,.32), color=col))
    add(bags, 'bag_front_pocket_'+str(i), (.38,.10,.29),
        (x,y-.28,.25), tuple(min(1,v*1.18) for v in col))
    bags.include('bag_handle_'+str(i), rod(radius=.025, start=(x-.12,y,.57),
                                            end=(x+.12,y,.57), color=black))
scene.include('bags', bags)

fixtures = Asset('Ceiling_and_wall_fixtures')
# Three dark, three-bladed ceiling fans.
for n, (x,y) in enumerate(((-2.6,-5.2),(2.6,-4.8),(-1.8,1.4),(2.5,2.2))):
    fixtures.include('fan_stem_'+str(n), rod(radius=.035, start=(x,y,4.53),
                                              end=(x,y,4.12), color=black))
    fixtures.include('fan_hub_'+str(n), ball(radius=.105, center=(x,y,4.10), color=black))
    for blade in range(3):
        angle = blade*2*math.pi/3 + .3
        dx,dy = math.cos(angle),math.sin(angle)
        fixtures.include('fan_blade_%d_%d'%(n,blade),
                         rod(radius=.055, start=(x+dx*.10,y+dy*.10,4.10),
                             end=(x+dx*.88,y+dy*.88,4.10), color=(.19,.17,.15)))
for n,y in enumerate((-3.3, 2.5, 6.4)):
    add(fixtures, 'fluorescent_'+str(n), (1.6,.13,.055), (0,y,4.54), (1,1,.93))
# Wall speakers and simple framed notices.
for n,(x,y) in enumerate(((-4.77,1.1),(4.77,1.1))):
    add(fixtures, 'speaker_'+str(n), (.20,.58,.70), (x,y,3.2), (0.055,.07,.065))
for n,(x,y) in enumerate(((-4.78,-3.9),(4.78,-3.5),(4.78,3.4))):
    add(fixtures, 'notice_frame_'+str(n), (.08,.50,.64), (x,y,3.6), (.27,.24,.19))
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
background.inputs['Color'].default_value = (0.78, 0.81, 0.83, 1)
background.inputs['Strength'].default_value = .65

set_view((0,-12.7,2.65), (0,3.1,1.85), lens=25, sensor=36)
area_emitter((0,-3,4.25), power=1100, size=7, target=(0,1,0))
area_emitter((0,5,4.2), power=900, size=6, target=(0,5,0))
area_emitter((-4.1,-1,3.0), power=550, size=5, target=(0,1,1))
