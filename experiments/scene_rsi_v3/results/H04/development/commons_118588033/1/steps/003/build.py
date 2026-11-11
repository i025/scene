# Reference versus second render, approximate normalized image coordinates:
# - Column foot: reference (.72,.84), render (.76,.82); its color boundary is
#   at reference y=.47, render y=.55. The column overlaps the rear furniture.
# - Rear lockers: reference roughly x=.40-.63, y=.39-.61; render approximately
#   x=.36-.59, y=.44-.62, behind the bunk.
# - Bunk front upright: reference near x=.40, y=.32-.70; render near x=.32,
#   y=.42-.76. Both show pale mattresses separated by dark gaps.
# - Foreground left equipment: reference x=0-.20, y=.48-.72; the render clips
#   most of it at the left edge. The left bench recedes diagonally toward the bunk.
# - Right wall board: reference x=.77-.90, y=.34-.46; render is almost entirely
#   cropped. The red wall object is likewise cropped at the right edge.
# - Nearest lamp: reference center about (.39,.16); render center about
#   (.33,.30). Ceiling structures reach the upper frame in both images.
# Vertical posts are nearly vertical; bench edges recede toward the center.
# The rendered floor is much lighter and more uniform than the reference.
#
# Ranked corrections and predicted effects:
# 1. Move the right wall fixtures onto a front-facing wall return: the dark board
#    and red object move left into view and grow in visible area.
# 2. Move the column left and raise its paint boundary: its shaft and foot move
#    left, while the brown/cream transition moves upward.
# 3. Shift the bunk front frame right and extend its posts upward, bringing the
#    high-contrast frame closer to its reference silhouette. Shift lockers right
#    and raise their tops locally. Preserve their overlap and mattress gaps.
# 4. Move the nearest hanging lamp toward the camera and raise it; its shade
#    becomes larger and moves upward. Bring the heater and foreground cabinet
#    farther into the image. Darken the floor and moderate ambient lighting;
#    apparent brightness also depends on the lights and surface orientation.
# Camera is retained because foreground and background errors are inconsistent.
# The program prints a small camera trial and restores the original camera.
# Inventory: room, beams and pipes, column, bunk and bedding, lockers, table,
# chair, benches, foreground equipment, heater, wall board, fire equipment,
# notice and hanging lamps. Hidden depths and rear furniture remain uncertain.
# Expanded primitive estimate: architecture 9, column 3, bunk 26, lockers 28,
# equipment 26, benches 10, furniture 12, heater 7, wall fixtures 8,
# overhead 17, lamps 9: approximately 155 separate meshes.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene('Utility bunk room')
cream = (.61, .60, .52)
wall = (.70, .69, .61)
floor_color = (.19, .055, .033)
brown = (.23, .065, .038)
black = (.018, .023, .020)
dark = (.035, .045, .038)
metal = (.34, .37, .35)
green = (.018, .075, .055)

def add(parent, name, shape):
    parent.include(name, shape)

# Independent major dimensions, positions, and camera parameters.
ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT = 5.8, 12.0, 3.35
COLUMN_X, COLUMN_Y, COLUMN_TRANSITION = .90, -.65, 1.85
BUNK_X0, BUNK_X1 = -2.30, -.54
BUNK_Y0, BUNK_Y1 = .55, 4.12
CAMERA_POSITION = (0.0, -7.7, 2.05)
CAMERA_TARGET = (0.0, 2.1, 1.55)
CAMERA_LENS = 48

room = Asset('Architecture')
add(room, 'floor', box((ROOM_WIDTH, ROOM_DEPTH, .12),
    center=(0,1.1,-.06), color=floor_color))
add(room, 'rear_wall', box((ROOM_WIDTH,.14,ROOM_HEIGHT),
    center=(0,5,1.675), color=cream))
add(room, 'left_wall', box((.14,ROOM_DEPTH,ROOM_HEIGHT),
    center=(-2.9,1.1,1.675), color=cream))
add(room, 'right_wall', box((.14,5.4,ROOM_HEIGHT),
    center=(2.9,2.3,1.675), color=wall))
# A short front-facing return gives the right wall objects their visible face.
add(room, 'right_return', box((1.35,.12,3.35),
    center=(2.48,2.9,1.675), color=wall))
add(room, 'ceiling', box((ROOM_WIDTH,ROOM_DEPTH,.12),
    center=(0,1.1,3.36), color=(.43,.35,.28)))
add(room, 'rear_baseboard', box((ROOM_WIDTH,.06,.28),
    center=(0,4.91,.14), color=brown))
add(room, 'left_baseboard', box((.06,10,.27),
    center=(-2.81,1,.135), color=brown))
add(room, 'return_baseboard', box((1.35,.05,.27),
    center=(2.48,2.82,.135), color=brown))
scene.include('architecture', room)

pillar = Asset('Front support column')
add(pillar,'upper',rod(.145,start=(COLUMN_X,COLUMN_Y,COLUMN_TRANSITION),
    end=(COLUMN_X,COLUMN_Y,3.35),color=(.76,.74,.65)))
add(pillar,'lower',rod(.145,start=(COLUMN_X,COLUMN_Y,.05),
    end=(COLUMN_X,COLUMN_Y,COLUMN_TRANSITION),color=brown))
add(pillar,'foot',rod(.20,start=(COLUMN_X,COLUMN_Y,.015),
    end=(COLUMN_X,COLUMN_Y,.07),color=(.34,.23,.17)))
scene.include('support_column',pillar)

bunk = Asset('Left bunk beds')
for x in (BUNK_X0,BUNK_X1):
    for y in (BUNK_Y0,BUNK_Y1):
        add(bunk,'post_%s_%s'%(x,y),rod(.036,
            start=(x,y,.05),end=(x,y,2.55),color=black))
for z in (.43,1.00,1.57,2.05):
    for x in (BUNK_X0,BUNK_X1):
        add(bunk,'long_rail_%s_%s'%(z,x),rod(.025,
            start=(x,BUNK_Y0,z),end=(x,BUNK_Y1,z),color=black))
    for y in (BUNK_Y0,BUNK_Y1):
        add(bunk,'end_rail_%s_%s'%(z,y),rod(.025,
            start=(BUNK_X0,y,z),end=(BUNK_X1,y,z),color=black))
for i,z in enumerate((.49,1.06,1.63)):
    add(bunk,'mattress_%d'%i,box((1.58,3.15,.11),
        center=(-1.42,2.37,z),color=(.64,.65,.59)))
    add(bunk,'pillow_%d'%i,box((1.12,.50,.10),
        center=(-1.42,3.62,z+.10),color=(.76,.76,.70)))
scene.include('bunk',bunk)

lockers = Asset('Rear gray lockers')
for i in range(4):
    x = -.65+i*.42
    add(lockers,'body_%d'%i,box((.40,.43,1.95),
        center=(x,4.65,1.285),color=metal))
    add(lockers,'door_%d'%i,box((.36,.025,1.83),
        center=(x,4.425,1.30),color=(.44,.47,.44)))
    add(lockers,'handle_%d'%i,box((.028,.035,.15),
        center=(x+.13,4.398,1.25),color=dark))
    for k in range(4):
        add(lockers,'vent_%d_%d'%(i,k),box((.22,.016,.018),
            center=(x,4.394,1.85-k*.065),color=(.22,.24,.22)))
scene.include('lockers',lockers)

cabinet = Asset('Left foreground equipment')
add(cabinet,'body',box((.86,1.82,1.28),
    center=(-2.12,-.15,.72),color=(.045,.065,.058)))
add(cabinet,'top',box((.98,1.98,.08),
    center=(-2.12,-.15,1.39),color=dark))
for j in range(3):
    yy=-.75+j*.57
    add(cabinet,'panel_%d'%j,box((.025,.48,.95),
        center=(-1.68,yy,.76),color=(.065,.09,.08)))
    for k in range(7):
        add(cabinet,'louver_%d_%d'%(j,k),box((.018,.39,.022),
            center=(-1.66,yy,.42+k*.10),color=(.16,.19,.17)))
scene.include('foreground_equipment',cabinet)

benches = Asset('Benches')
add(benches,'left_seat',box((.48,3.55,.075),
    center=(-1.78,-.70,.51),color=green))
for y in (-2.18,.65):
    for x in (-1.94,-1.61):
        add(benches,'left_leg_%s_%s'%(x,y),
            rod(.025,start=(x,y,.03),end=(x,y,.49),color=black))
add(benches,'right_seat',box((.57,2.65,.075),
    center=(2.12,-1.38,.49),color=green))
for y in (-2.44,-.36):
    for x in (1.90,2.32):
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
    center=(-.40,3.09,.53),color=(.58,.58,.50)))
add(furniture,'chair_back',box((.47,.07,.43),
    center=(-.40,3.30,.81),color=(.53,.54,.47)))
for x in (-.60,-.20):
    for y in (2.92,3.27):
        add(furniture,'chair_leg_%s_%s'%(x,y),
            rod(.018,start=(x,y,.04),end=(x,y,.54),color=(.56,.57,.50)))
scene.include('worktable_and_chair',furniture)

heater = Asset('Wall heater')
add(heater,'housing',box((.72,.40,.78),
    center=(-1.98,1.55,2.45),color=(.51,.52,.46)))
add(heater,'front',box((.59,.035,.55),
    center=(-1.98,1.335,2.43),color=(.24,.26,.23)))
for j in range(5):
    add(heater,'grille_%d'%j,box((.52,.035,.055),
        center=(-1.98,1.31,2.23+j*.10),color=(.09,.11,.09)))
scene.include('wall_heater',heater)

fixtures = Asset('Right wall mounted equipment')
add(fixtures,'dark_board',box((.75,.045,.78),
    center=(1.78,2.81,2.15),color=(.20,.23,.21)))
add(fixtures,'board_top_frame',box((.80,.06,.035),
    center=(1.78,2.77,2.56),color=dark))
add(fixtures,'board_side_frame',box((.035,.06,.82),
    center=(1.38,2.77,2.15),color=dark))
add(fixtures,'red_housing',box((.34,.16,.51),
    center=(1.82,2.73,1.26),color=(.72,.09,.065)))
add(fixtures,'rounded_red_top',ball(.17,
    center=(1.82,2.73,1.51),color=(.72,.09,.065)))
add(fixtures,'label',box((.13,.015,.20),
    center=(1.82,2.64,1.37),color=(.83,.80,.71)))
add(fixtures,'notice',box((.53,.03,.70),
    center=(2.48,2.82,1.94),color=(.74,.74,.67)))
scene.include('wall_equipment',fixtures)

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
# Pale diagonal braces visible around the nearest lamp.
add(overhead,'brace_a',rod(.055,start=(-2.45,-2.7,3.20),
    end=(-1.15,-.95,2.68),color=(.70,.68,.58)))
add(overhead,'brace_b',rod(.045,start=(-.95,-2.0,3.25),
    end=(-1.15,-.95,2.68),color=(.70,.68,.58)))
scene.include('ceiling_structure',overhead)

lamps = Asset('Hanging lamps')
for i,(x,y,z,r) in enumerate((
    (-.50,-2.10,2.86,.27),(-.54,2.0,2.72,.17),
    (-.52,4.05,2.65,.12))):
    add(lamps,'cord_%d'%i,rod(.015,start=(x,y,3.25),
        end=(x,y,z+.12),color=dark))
    shade=ball(r,center=(x,y,z),color=(.14,.16,.14))
    shade.resize((1,1,.30))
    add(lamps,'shade_%d'%i,shade)
    add(lamps,'diffuser_%d'%i,rod(r*.90,
        start=(x,y,z-.085),end=(x,y,z-.055),color=(1,.98,.86)))
scene.include('hanging_lamps',lamps)

realize(scene)
sc=bpy.context.scene
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100

# These world points are on geometry. Reference values are visual estimates;
# projections are printed separately and do not establish visible contours.
landmarks=[
    ('column_foot',(COLUMN_X,COLUMN_Y,.07),(.72,.84)),
    ('column_boundary',(COLUMN_X,COLUMN_Y,COLUMN_TRANSITION),(.72,.47)),
    ('locker_top_left',(-.85,4.425,2.20),(.40,.39)),
    ('bunk_front_top',(BUNK_X1,BUNK_Y0,2.55),(.40,.32)),
    ('board_top_left',(1.405,2.78,2.54),(.77,.34)),
    ('bench_foreground',(-1.61,-2.475,.55),(.00,.83)),
]

def project_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    mat=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=mat @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,'reference',ref,'projected',
            None if uv is None else tuple(round(v,3) for v in uv))

# A small upward aim trial shows its direction. The previous camera is restored.
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
project_table('Retained camera')
set_view(CAMERA_POSITION,(0.0,2.1,1.65),lens=CAMERA_LENS)
project_table('Upward aim trial')
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
project_table('Restored final camera')

if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get('Background')
if background is None:
    background=nodes.new('ShaderNodeBackground')
output=nodes.get('World Output')
if output is None:
    output=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],
                             output.inputs['Surface'])
background.inputs['Color'].default_value=(.32,.30,.27,1)
background.inputs['Strength'].default_value=.35
area_emitter((-.7,-1.0,3.04),power=300,size=2.0,target=(0,1,0))
area_emitter((-.6,3.0,2.8),power=130,size=1.8,target=(0,3,0))
area_emitter((1.8,-3.5,2.8),power=80,size=3,target=(0,2,1))
