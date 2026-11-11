# Reference inventory and visual anchors, normalized to 512 x 340:
# - Room: floor fills roughly (0,.40)-(1,1); side walls converge toward
#   the back around (.50,.39). Ceiling fills upper third. Long floor and
#   ceiling edges converge near the central blackboard.
# - Rear stage at approximately (.37,.24)-(.66,.44), with a dark red
#   curtain, green side strips, pale valance, and green board in front.
# - Wooden student desks occupy (.00,.40)-(.93,.88), in several receding
#   rows. Their dark horizontal tops overlap thin legs and benches.
# - Foreground desk at (.14,.59)-(.37,.88), another at (.51,.55)-(.70,.82).
#   Blue and black school bags sit beneath or beside several desks.
# - Tall bright windows and brown doors run along both side walls; the
#   lower wall is yellow, the upper wall pale cream. Window openings and
#   furniture partly obscure each other. Side-wall details are uncertain.
# - Three dark ceiling fans appear across the ceiling; fluorescent lights
#   and small framed pictures are secondary details.
# Approximate expanded primitive count: architecture 15, stage 14,
# windows/doors 35, 24 desks and benches about 240, bags 18,
# ceiling fittings 22, wall details 12; total roughly 356 meshes.
# Every repeated object remains a named editable SceneAct asset.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene('Classroom')

# Major dimensions and camera are kept separate for adjustment.
ROOM_W = 9.2
FRONT_Y = -8.0
BACK_Y = 9.0
ROOM_H = 4.35
CAM_POS = (0.0, -11.3, 2.65)
CAM_TARGET = (0.0, 4.2, 1.95)
CAM_LENS = 23.0

cream = (0.79, 0.79, 0.67)
yellow = (0.95, 0.68, 0.015)
floor_col = (0.68, 0.57, 0.41)
wood = (0.30, 0.20, 0.12)
wood_top = (0.33, 0.27, 0.21)
dark = (0.075, 0.065, 0.055)
green = (0.08, 0.27, 0.22)
brown = (0.31, 0.19, 0.10)

room = Asset('Architecture')
room.include('floor', box((ROOM_W, BACK_Y-FRONT_Y, .12),
                          center=(0, (FRONT_Y+BACK_Y)/2, -.06),
                          color=floor_col))
room.include('ceiling', box((ROOM_W, BACK_Y-FRONT_Y, .12),
                            center=(0, (FRONT_Y+BACK_Y)/2, ROOM_H+.06),
                            color=(.86,.87,.81)))
for side in (-1, 1):
    x = side * ROOM_W/2
    room.include('upper_wall_%s' % side,
                 box((.12, BACK_Y-FRONT_Y, ROOM_H-1.05),
                     center=(x, (FRONT_Y+BACK_Y)/2, (ROOM_H+1.05)/2),
                     color=cream))
    room.include('yellow_dado_%s' % side,
                 box((.13, BACK_Y-FRONT_Y, 1.05),
                     center=(x-side*.008, (FRONT_Y+BACK_Y)/2, .525),
                     color=yellow))
room.include('back_wall', box((ROOM_W,.15,ROOM_H),
                              center=(0,BACK_Y,ROOM_H/2), color=cream))
scene.include('architecture', room)

# Thin tile lines give the foreground floor its square-grid appearance.
tiles = Asset('Floor tile joints')
for x in [i*.65 for i in range(-7,8)]:
    tiles.include('x_%s' % x, box((.012,BACK_Y-FRONT_Y,.004),
                                   center=(x,.5,.004), color=(.56,.48,.37)))
for y in [FRONT_Y+i*.65 for i in range(27)]:
    tiles.include('y_%s' % y, box((ROOM_W,.012,.004),
                                   center=(0,y,.005), color=(.56,.48,.37)))
scene.include('floor_joints', tiles)

# Side-wall openings are represented as bright inset panes over the wall;
# thin frames and dark timber doors provide the visible rhythm.
side_details = Asset('Windows and doors')
for s in (-1, 1):
    inner_x = s*(ROOM_W/2-.075)
    for j, y in enumerate((-6.2,-2.3,1.5,5.0)):
        window = Asset('Window_%s_%s' % (s,j))
        window.include('bright_glazing', box((.025,1.14,2.38),
                       center=(inner_x-s*.015,y,2.05), color=(.96,.96,.84)))
        for dy in (-.60,.60):
            window.include('upright_%s' % dy, box((.07,.075,2.55),
                           center=(inner_x-s*.035,y+dy,2.04), color=brown))
        for z in (.78,3.29):
            window.include('cross_%s' % z, box((.07,1.28,.08),
                           center=(inner_x-s*.035,y,z), color=brown))
        window.include('upper_bar', box((.08,1.2,.055),
                       center=(inner_x-s*.05,y,2.94), color=brown))
        side_details.include('window_%s_%s' % (s,j), window)
    for j,y in enumerate((-4.25, 2.95)):
        door = Asset('Door_%s_%s' % (s,j))
        door.include('leaf', box((.035,.82,2.45),
                     center=(inner_x-s*.05,y,1.23), color=(.35,.24,.15)))
        for dy in (-.44,.44):
            door.include('frame_%s' % dy, box((.08,.07,2.55),
                         center=(inner_x-s*.08,y+dy,1.27), color=(.22,.15,.10)))
        side_details.include('door_%s_%s' % (s,j),door)
scene.include('wall_openings', side_details)

# Raised stage and its curtain occupy the center of the far wall.
stage = Asset('Rear stage')
stage.include('platform', box((4.9,1.15,.22), center=(0,8.15,.11),
                              color=(.42,.30,.14)))
stage.include('dark_recess', box((4.45,.08,2.35), center=(0,8.88,2.56),
                                 color=(.075,.055,.043)))
stage.include('red_curtain', box((3.62,.06,1.80), center=(0,8.81,2.70),
                                 color=(.18,.025,.028)))
for x in (-2.15,2.15):
    stage.include('green_side_%s'%x, box((.36,.10,2.34),
                  center=(x,8.72,2.57), color=(.08,.28,.10)))
stage.include('valance', box((4.4,.12,.28), center=(0,8.63,3.73),
                             color=(.79,.75,.60)))
stage.include('front_lip', box((4.9,.08,.18), center=(0,7.56,.22),
                               color=(.54,.40,.16)))
board = Asset('Chalkboard')
board.include('green_surface', box((1.75,.07,.98), center=(0,7.91,1.61),
                                  color=(.16,.34,.29)))
for x in (-.90,.90):
    board.include('side_frame_%s'%x, box((.055,.09,1.08),
                  center=(x,7.86,1.61), color=(.60,.58,.43)))
for z in (1.09,2.13):
    board.include('horizontal_frame_%s'%z, box((1.85,.09,.055),
                  center=(0,7.86,z), color=(.60,.58,.43)))
stage.include('chalkboard',board)
stage.include('lectern', box((.5,.43,1.0),center=(1.6,7.44,.72),
                             color=(.51,.62,.62)))
scene.include('stage',stage)

# Each student station contains a tabletop, four legs, and a separate
# low bench. Depth is the room's y direction.
def student_station(name, x, y, width=1.35, depth=.62):
    a = Asset(name)
    top_z = .79
    a.include('desktop', box((width,depth,.095),
              center=(x,y,top_z), color=wood_top))
    a.include('front_apron', box((width-.08,.055,.20),
              center=(x,y-depth/2+.045,.65), color=wood))
    for sx in (-1,1):
        for sy in (-1,1):
            a.include('leg_%s_%s'%(sx,sy),
                box((.065,.065,.73),
                    center=(x+sx*(width/2-.085),y+sy*(depth/2-.075),.37),
                    color=wood))
    # Seat is behind the desk from the viewer's side and visible through legs.
    seat_y = y-.58
    a.include('bench_seat',box((width*.84,.30,.075),
              center=(x,seat_y,.44),color=(.25,.20,.16)))
    for sx in (-1,1):
        a.include('bench_leg_%s'%sx,box((.055,.055,.40),
                  center=(x+sx*width*.35,seat_y,.21),color=wood))
    return a

# Three groups of narrow desk rows, with clear central aisles.
for row,y in enumerate((-5.0,-2.9,-.9,1.0,2.85,4.55,6.05)):
    for col,x in enumerate((-3.20,-1.08,1.10,3.20)):
        # The nearest side stations are partly outside the photograph.
        scene.include('desk_%d_%d'%(row,col),
                      student_station('Student desk %d %d'%(row,col),
                                      x,y,1.30,.62))

# A few distinct backpacks: simplified bags with visible straps and pockets.
def backpack(name, x, y, color, scale=1):
    a=Asset(name)
    a.include('body', box((.37*scale,.22*scale,.54*scale),
              center=(x,y,.27*scale),color=color))
    a.include('front_pocket', box((.27*scale,.04*scale,.23*scale),
              center=(x,y-.13*scale,.19*scale),color=tuple(c*.78 for c in color)))
    a.include('handle', rod(.018*scale,
              start=(x-.11*scale,y,.55*scale),
              end=(x+.11*scale,y,.55*scale),color=dark))
    return a
for name,x,y,c,s in [
    ('foreground_black',-3.55,-6.15,(.035,.05,.07),1.0),
    ('foreground_blue',1.65,-5.55,(.015,.27,.55),1.05),
    ('central_black',.20,-3.65,(.035,.06,.065),.8),
    ('right_blue',3.55,-3.7,(.02,.34,.56),.85),
    ('left_blue',-2.55,-1.9,(.025,.24,.41),.65),
    ('middle_blue',1.9,1.3,(.02,.30,.47),.55)]:
    scene.include(name,backpack(name,x,y,c,s))

# Ceiling beams, fluorescent strips, and flat-bladed fans.
ceiling = Asset('Ceiling fittings')
for y in (-5.8,-.3,4.4):
    ceiling.include('beam_%s'%y,box((ROOM_W,.24,.16),
                    center=(0,y,4.25),color=(.81,.82,.77)))
for x,y in ((-2.6,-1.7),(1.7,1.9),(-.2,5.7)):
    ceiling.include('light_%s_%s'%(x,y),box((.20,1.0,.045),
                    center=(x,y,4.24),color=(.92,.92,.83)))

def fan(name,x,y):
    f=Asset(name)
    f.include('downrod',rod(.035,start=(x,y,4.35),end=(x,y,3.92),
                            color=(.24,.23,.21)))
    f.include('hub',ball(.13,center=(x,y,3.90),color=(.23,.22,.20)))
    for k in range(3):
        ang=2*math.pi*k/3+.2
        blade=box((1.25,.16,.035),center=(x+.64*math.cos(ang),
                   y+.64*math.sin(ang),3.89),color=(.25,.24,.21))
        blade.turn('+z', math.degrees(ang))
        f.include('blade_%d'%k,blade)
    return f
for i,(x,y) in enumerate(((-2.6,-5.1),(2.5,-4.5),(-2.1,2.0),(2.2,3.1))):
    ceiling.include('fan_%d'%i,fan('Ceiling fan %d'%i,x,y))
scene.include('ceiling_fittings',ceiling)

# Dark wall-mounted speakers and small high pictures.
wall_items=Asset('Wall details')
for s,y in ((-1,3.7),(1,-.2)):
    wall_items.include('speaker_%s'%s,box((.15,.55,.78),
                       center=(s*(ROOM_W/2-.15),y,3.23),
                       color=(.09,.13,.14)))
for s,y in ((-1,-3.4),(-1,1.0),(1,-3.8),(1,2.0)):
    wall_items.include('picture_frame_%s_%s'%(s,y),
        box((.04,.50,.62),center=(s*(ROOM_W/2-.08),y,3.57),
            color=(.27,.24,.18)))
    wall_items.include('picture_%s_%s'%(s,y),
        box((.045,.39,.50),center=(s*(ROOM_W/2-.11),y,3.57),
            color=(.74,.79,.72)))
scene.include('wall_details',wall_items)

realize(scene)
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(0.72,0.75,0.72,1)
background.inputs['Strength'].default_value=.7
area_emitter((0,-3,4.05),power=650,size=7,target=(0,1,0))
area_emitter((0,5,4.05),power=500,size=6,target=(0,4,0))

# Reference estimates are separate from computed projections; these are
# approximate correspondences and do not establish visibility.
landmarks=[
    ('backboard upper left',(-.90,7.86,2.13),(.45,.33)),
    ('backboard lower right',(.90,7.86,1.09),(.58,.42)),
    ('near desk upper left',(-1.73,-5.31,.84),(.15,.60)),
    ('near desk upper right',(-.43,-5.31,.84),(.36,.60)),
    ('left window top',(-4.48,-2.9,3.29),(.04,.18)),
]
bpy.context.view_layer.update()
cam=sc.camera
dg=bpy.context.evaluated_depsgraph_get()
proj=cam.calc_matrix_camera(dg,x=512,y=340,
                            scale_x=sc.render.pixel_aspect_x,
                            scale_y=sc.render.pixel_aspect_y)
print('Landmark                         reference       projected')
for name,p,ref in landmarks:
    clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),
                                  .5*(1-clip.y/clip.w))
    print('%-32s %s %s'%(name,ref,
          None if uv is None else tuple(round(v,3) for v in uv)))
