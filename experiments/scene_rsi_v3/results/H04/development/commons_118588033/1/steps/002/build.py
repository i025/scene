# Reference versus first render, normalized image coordinates:
# Foreground column foot: reference (.72,.84), render (.66,.67).
# Column color boundary: reference (.72,.47), render (.66,.52).
# Rear locker upper left: reference (.40,.39), render (.40,.47).
# Bunk front upper corner: reference (.38,.36), render (.38,.48).
# Reference ceiling and floor fill the entire frame; the render has gray bands
# at top and bottom and a large, overly open foreground floor.
# Reference bunk has conspicuous dark posts and several separate pale bunks;
# rendered bunk is smaller and its rails and dark gaps are less prominent.
# Reference right wall panel and red equipment are conspicuous; in the render
# they are largely hidden or too small. The foreground cabinet should be dark.
# Near-vertical posts remain approximately vertical in both views. Floor and
# bench edges recede toward the center. The reference column overlaps the
# worktable; the bunk overlaps the lockers. Their exact depths are uncertain.
#
# Ranked corrections:
# 1. Increase lens from 31 to 48 mm. Predicted: foreground and background
#    features move away from image center, removing the empty frame bands and
#    raising rear lockers and bunk while moving the column foot downward.
# 2. Move column from y=.25 to y=-.65 and x=1.12 to x=1.05. Predicted:
#    its foot moves down and right, and the shaft becomes taller in the frame.
# 3. Place the wall panel and red equipment on a nearer right wall section,
#    moving their visible contours rightward and enlarging them. Increase bunk
#    rail contrast and show three separate mattresses with dark gaps.
# 4. Replace spherical lamp shades with flattened dark shades and bright
#    undersides, and darken the cabinet and floor. Illumination still affects
#    the final apparent colors.
# Camera trial projections are printed separately from the observed contours.
#
# Inventory: room envelope and exposed beams, foreground green benches and
# dark louvered cabinet, left metal bunks with pale bedding, rear lockers,
# worktable and chair, cream/red column, wall heater, dark wall board, red
# fire equipment, white notice, ceiling pipes and hanging lamps. Hidden
# portions of furniture and the wall equipment are estimated.
# Expanded primitive estimate: architecture 8, column 3, bunk 27, lockers 28,
# cabinet 27, benches 10, table/chair 13, heater 7, wall objects 7,
# overhead 19, lamps 9: approximately 158 meshes.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene('Utility bunk room')

cream = (.65, .64, .56)
wall_light = (.72, .71, .63)
floor_col = (.25, .075, .047)
brown = (.25, .075, .045)
dark = (.035, .045, .038)
black = (.018, .023, .020)
metal = (.34, .37, .35)
green = (.018, .075, .055)

def add(asset, name, node):
    asset.include(name, node)

# Asset dimensions and camera settings are independent parameters.
ROOM_WIDTH = 5.8
ROOM_DEPTH = 12.0
ROOM_HEIGHT = 3.35
COLUMN_X, COLUMN_Y = 1.05, -.65
BUNK_X0, BUNK_X1 = -2.50, -.84
BUNK_Y0, BUNK_Y1 = .55, 4.12
CAMERA_POSITION = (0.0, -7.7, 2.05)
CAMERA_TARGET = (0.0, 2.1, 1.55)
CAMERA_LENS = 48

room = Asset('Architecture')
add(room, 'floor', box((ROOM_WIDTH, ROOM_DEPTH, .12),
    center=(0, 1.1, -.06), color=floor_col))
add(room, 'rear_wall', box((ROOM_WIDTH, .14, ROOM_HEIGHT),
    center=(0, 5.0, 1.675), color=cream))
add(room, 'left_wall', box((.14, ROOM_DEPTH, ROOM_HEIGHT),
    center=(-2.9, 1.1, 1.675), color=cream))
add(room, 'right_wall', box((.14, 5.4, ROOM_HEIGHT),
    center=(2.9, 2.3, 1.675), color=wall_light))
add(room, 'ceiling', box((ROOM_WIDTH, ROOM_DEPTH, .12),
    center=(0, 1.1, 3.36), color=(.43,.35,.28)))
add(room, 'rear_baseboard', box((ROOM_WIDTH,.06,.28),
    center=(0,4.91,.14), color=brown))
add(room, 'left_baseboard', box((.06,10,.27),
    center=(-2.81,1,.135), color=brown))
add(room, 'right_baseboard', box((.06,5.4,.27),
    center=(2.81,2.3,.135), color=brown))
scene.include('architecture', room)

pillar = Asset('Front support column')
add(pillar, 'upper', rod(.145, start=(COLUMN_X,COLUMN_Y,1.45),
    end=(COLUMN_X,COLUMN_Y,3.35), color=(.76,.74,.65)))
add(pillar, 'lower', rod(.145, start=(COLUMN_X,COLUMN_Y,.05),
    end=(COLUMN_X,COLUMN_Y,1.45), color=brown))
add(pillar, 'foot', rod(.20, start=(COLUMN_X,COLUMN_Y,.015),
    end=(COLUMN_X,COLUMN_Y,.07), color=(.34,.23,.17)))
scene.include('support_column', pillar)

bunk = Asset('Left bunk beds')
for x in (BUNK_X0,BUNK_X1):
    for y in (BUNK_Y0,BUNK_Y1):
        add(bunk, 'post_%s_%s'%(x,y), rod(.036,
            start=(x,y,.05), end=(x,y,2.15), color=black))
for z in (.43,1.00,1.57,2.05):
    for x in (BUNK_X0,BUNK_X1):
        add(bunk,'long_rail_%s_%s'%(z,x),rod(.025,
            start=(x,BUNK_Y0,z),end=(x,BUNK_Y1,z),color=black))
    for y in (BUNK_Y0,BUNK_Y1):
        add(bunk,'end_rail_%s_%s'%(z,y),rod(.025,
            start=(BUNK_X0,y,z),end=(BUNK_X1,y,z),color=black))
for i,z in enumerate((.49,1.06,1.63)):
    add(bunk,'mattress_%d'%i,box((1.50,3.15,.11),
        center=(-1.67,2.37,z),color=(.64,.65,.59)))
    add(bunk,'pillow_%d'%i,box((1.12,.50,.10),
        center=(-1.67,3.62,z+.10),color=(.76,.76,.70)))
scene.include('bunk', bunk)

lockers = Asset('Rear gray lockers')
for i in range(4):
    x = -.90 + i*.42
    add(lockers,'body_%d'%i,box((.40,.43,1.68),
        center=(x,4.65,1.15),color=metal))
    add(lockers,'door_%d'%i,box((.36,.025,1.56),
        center=(x,4.425,1.17),color=(.44,.47,.44)))
    add(lockers,'handle_%d'%i,box((.028,.035,.15),
        center=(x+.13,4.398,1.17),color=dark))
    for k in range(4):
        add(lockers,'vent_%d_%d'%(i,k),box((.22,.016,.018),
            center=(x,4.394,1.61-k*.065),color=(.22,.24,.22)))
scene.include('lockers', lockers)

cabinet = Asset('Left foreground equipment')
add(cabinet,'body',box((.86,1.82,1.28),
    center=(-2.43,-.15,.72),color=(.045,.065,.058)))
add(cabinet,'top',box((.98,1.98,.08),
    center=(-2.43,-.15,1.39),color=dark))
for j in range(3):
    yy = -.75+j*.57
    add(cabinet,'panel_%d'%j,box((.025,.48,.95),
        center=(-1.99,yy,.76),color=(.065,.09,.08)))
    for k in range(7):
        add(cabinet,'louver_%d_%d'%(j,k),box((.018,.39,.022),
            center=(-1.97,yy,.42+k*.10),color=(.16,.19,.17)))
scene.include('foreground_equipment',cabinet)

benches = Asset('Benches')
add(benches,'left_seat',box((.48,3.55,.075),
    center=(-1.94,-.70,.51),color=green))
for y in (-2.18,.65):
    for x in (-2.10,-1.77):
        add(benches,'left_leg_%s_%s'%(x,y),
            rod(.025,start=(x,y,.03),end=(x,y,.49),color=black))
add(benches,'right_seat',box((.57,2.65,.075),
    center=(2.42,-1.38,.49),color=green))
for y in (-2.44,-.36):
    for x in (2.20,2.62):
        add(benches,'right_leg_%s_%s'%(x,y),
            rod(.025,start=(x,y,.03),end=(x,y,.47),color=black))
scene.include('benches',benches)

furniture = Asset('Rear worktable and chair')
add(furniture,'table_top',box((1.18,.84,.10),
    center=(.42,3.38,.88),color=(.20,.22,.19)))
add(furniture,'table_body',box((.94,.68,.69),
    center=(.54,3.48,.47),color=(.17,.19,.16)))
for x in (-.08,.94):
    for y in (3.05,3.69):
        add(furniture,'table_leg_%s_%s'%(x,y),
            rod(.035,start=(x,y,.04),end=(x,y,.85),color=dark))
add(furniture,'chair_seat',box((.47,.43,.07),
    center=(-.52,3.09,.53),color=(.58,.58,.50)))
add(furniture,'chair_back',box((.47,.07,.43),
    center=(-.52,3.30,.81),color=(.53,.54,.47)))
for x in (-.72,-.32):
    for y in (2.92,3.27):
        add(furniture,'chair_leg_%s_%s'%(x,y),
            rod(.018,start=(x,y,.04),end=(x,y,.54),color=(.56,.57,.50)))
scene.include('worktable_and_chair',furniture)

heater = Asset('Wall heater')
add(heater,'housing',box((.72,.40,.78),
    center=(-2.49,2.15,2.30),color=(.51,.52,.46)))
add(heater,'front',box((.59,.035,.55),
    center=(-2.49,1.935,2.28),color=(.24,.26,.23)))
for j in range(5):
    add(heater,'grill_%d'%j,box((.52,.035,.055),
        center=(-2.49,1.91,2.08+j*.10),color=(.09,.11,.09)))
scene.include('wall_heater',heater)

# Mounted on a wall-facing surface nearer the camera than the rear lockers.
wall_items = Asset('Right wall mounted equipment')
add(wall_items,'dark_panel',box((.045,.95,.85),
    center=(2.805,2.15,2.02),color=(.20,.23,.21)))
add(wall_items,'panel_frame_top',box((.06,1.0,.035),
    center=(2.775,2.15,2.46),color=dark))
add(wall_items,'red_housing',box((.16,.40,.59),
    center=(2.73,2.00,1.05),color=(.72,.09,.065)))
add(wall_items,'rounded_red_top',ball(.19,
    center=(2.73,2.00,1.34),color=(.72,.09,.065)))
add(wall_items,'label',box((.015,.13,.22),
    center=(2.64,2.00,1.15),color=(.83,.80,.71)))
add(wall_items,'white_notice',box((.03,.64,.76),
    center=(2.805,.93,1.70),color=(.74,.74,.67)))
scene.include('wall_equipment',wall_items)

overhead = Asset('Ceiling structure')
for y in (-2.0,.05,2.10,4.10):
    add(overhead,'crossbeam_%s'%y,box((5.8,.20,.24),
        center=(0,y,3.15),color=(.35,.19,.13)))
for x in (-2.55,-1.55,-.55,.45,1.45,2.45):
    add(overhead,'joist_%s'%x,box((.13,11.5,.18),
        center=(x,1.05,3.25),color=(.39,.23,.16)))
for z in (2.72,2.89):
    add(overhead,'rear_pipe_%s'%z,rod(.035,
        start=(-2.8,4.22,z),end=(2.8,4.22,z),color=dark))
add(overhead,'left_pipe',rod(.055,start=(-2.65,-3.8,2.93),
    end=(-2.65,4.5,2.93),color=(.57,.57,.50)))
add(overhead,'rear_vertical_pipe',rod(.055,start=(.92,4.73,1.55),
    end=(.92,4.73,3.10),color=(.60,.60,.53)))
scene.include('ceiling_structure',overhead)

lamps = Asset('Hanging lamps')
for i,(x,y,z,r) in enumerate((
        (-.72,.05,2.82,.27),(-.54,2.72,2.72,.17),
        (-.52,4.05,2.65,.12))):
    add(lamps,'cord_%d'%i,rod(.015,start=(x,y,3.25),
        end=(x,y,z+.12),color=dark))
    shade = ball(r,center=(x,y,z),color=(.14,.16,.14))
    shade.resize((1,1,.30))
    add(lamps,'shade_%d'%i,shade)
    add(lamps,'diffuser_%d'%i,rod(r*.90,
        start=(x,y,z-.085),end=(x,y,z-.055),color=(1.0,.98,.86)))
scene.include('hanging_lamps',lamps)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100

# Calculate the same geometry projections for the original camera and the
# proposed lens change. This is a numerical direction check, not a visibility
# or silhouette test.
landmarks = [
    ('column_foot', (COLUMN_X,COLUMN_Y,.07), (.72,.84)),
    ('column_color_boundary', (COLUMN_X,COLUMN_Y,1.45), (.72,.47)),
    ('locker_upper_left', (-1.10,4.425,1.93), (.40,.39)),
    ('bunk_front_upper', (BUNK_X1,BUNK_Y0,2.05), (.38,.36)),
    ('left_bench_front', (-1.77,-2.475,.55), (.00,.83)),
]

def project_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    results = {}
    for name,p,ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        results[name] = None if uv is None else tuple(round(v,3) for v in uv)
    print(label, results)

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=31)
project_table('Original lens, revised geometry')
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
project_table('Trial and final lens')
print('Reference estimates', {name:ref for name,p,ref in landmarks})

if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get('Background')
if background is None:
    background = nodes.new('ShaderNodeBackground')
output = nodes.get('World Output')
if output is None:
    output = nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],
                             output.inputs['Surface'])
background.inputs['Color'].default_value = (.32,.30,.27,1)
background.inputs['Strength'].default_value = .45
area_emitter((-.7,-1.0,3.04),power=350,size=2.0,target=(0,1,0))
area_emitter((-.6,3.0,2.8),power=160,size=1.8,target=(0,3,0))
area_emitter((1.8,-3.5,2.8),power=100,size=3,target=(0,2,1))
