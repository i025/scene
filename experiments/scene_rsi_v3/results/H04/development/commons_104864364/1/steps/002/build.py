# Reference inventory and comparison, normalized to 512 x 340:
# Room: pale walls and ceiling, yellow lower wall, tiled floor. Perspective
# lines converge near the rear center. Windows, doors and furniture overlap.
# Stage: reference approximately (.37,.24)-(.66,.44); rendered approximately
# (.42,.41)-(.58,.56). Its curtain and board were too small and too low.
# Foreground desk: reference approximately (.14,.59)-(.37,.88); rendered
# left desks approximately (.10,.72)-(.25,.90) and (.32,.72)-(.45,.90).
# Reference right foreground desk approximately (.51,.55)-(.70,.82);
# rendered right desk approximately (.55,.72)-(.69,.90).
# Windows: reference left bright windows start near (.04,.18); rendered
# left window tops are near (.16,.38). Several window placements are uncertain.
# Ceiling fans: reference nearest fans are cropped by the top edge, whereas
# rendered fans sit around y=.25. Reference ceiling and floor edges converge
# toward the stage; the render has similar symmetry but too much upper wall.
#
# Ranked corrections:
# 1. Lower camera target: stationary stage, desk tops and window corners should
#    move upward together; this also brings foreground furniture higher.
# 2. Enlarge the stage and board locally in width: their outer contours should
#    spread left and right while preserving the room's existing side edges.
# 3. Move foreground desk columns locally and darken their tops and legs.
#    Their silhouette should be less uniformly aligned and benches less prominent.
# 4. Increase window brightness and add dark openings, door leaves, bags and
#    ceiling fittings. Unseen window depths and stage details remain uncertain.
#
# Estimated expanded mesh count: architecture 6, floor joints 42, wall openings
# 64, stage and board 17, desks 28*8=224, bags 6*4=24, fans 4*5=20,
# other fittings and wall details 15: approximately 412 meshes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene('Classroom')

ROOM_W = 9.2
FRONT_Y = -8.0
BACK_Y = 9.0
ROOM_H = 4.35
CAM_POS = (0.0, -11.3, 2.65)
OLD_TARGET = (0.0, 4.2, 1.95)
CAM_TARGET = (0.0, 4.2, 0.40)
CAM_LENS = 23.0

cream = (.84, .83, .70)
yellow = (.98, .72, .025)
floor_col = (.72, .62, .48)
wood = (.25, .17, .10)
wood_top = (.27, .22, .17)
dark = (.045, .043, .038)
brown = (.32, .22, .13)

room = Asset('Architecture')
room.include('floor', box((ROOM_W, BACK_Y-FRONT_Y, .12),
                          center=(0, .5, -.06), color=floor_col))
room.include('ceiling', box((ROOM_W, BACK_Y-FRONT_Y, .12),
                            center=(0, .5, ROOM_H+.06),
                            color=(.88,.89,.84)))
for s in (-1, 1):
    x = s*ROOM_W/2
    room.include('upper_wall_%s'%s,
                 box((.12,17,ROOM_H-1.05), center=(x,.5,2.70), color=cream))
    room.include('yellow_lower_wall_%s'%s,
                 box((.13,17,1.05), center=(x-s*.008,.5,.525), color=yellow))
room.include('rear_wall', box((ROOM_W,.15,ROOM_H),
                              center=(0,9,ROOM_H/2), color=cream))
scene.include('architecture',room)

tiles = Asset('Floor tile joints')
for i in range(-7,8):
    tiles.include('long_%d'%i,
                  box((.010,17,.004),center=(i*.65,.5,.004),
                      color=(.62,.54,.43)))
for i in range(27):
    tiles.include('cross_%d'%i,
                  box((ROOM_W,.010,.004),center=(0,-8+i*.65,.005),
                      color=(.62,.54,.43)))
scene.include('floor_joints',tiles)

openings = Asset('Side windows and doors')
for s in (-1,1):
    inner = s*(ROOM_W/2-.075)
    for j,y in enumerate((-6.2,-2.3,1.5,5.0)):
        w = Asset('Window %s %s'%(s,j))
        w.include('dark_reveal',box((.028,1.25,2.54),
                  center=(inner-s*.015,y,2.04),color=(.27,.23,.16)))
        w.include('bright_pane',box((.03,1.05,2.30),
                  center=(inner-s*.035,y,2.06),color=(1.0,1.0,.92)))
        for dy in (-.60,.60):
            w.include('jamb_%s'%dy,box((.075,.075,2.55),
                      center=(inner-s*.06,y+dy,2.04),color=brown))
        for z in (.78,2.94,3.29):
            w.include('crossbar_%s'%z,box((.08,1.25,.065),
                      center=(inner-s*.065,y,z),color=brown))
        openings.include('window_%s_%s'%(s,j),w)
    for j,y in enumerate((-4.25,2.95)):
        d=Asset('Door %s %s'%(s,j))
        d.include('leaf',box((.055,.82,2.45),
                  center=(inner-s*.075,y,1.23),color=(.31,.22,.14)))
        for dy in (-.44,.44):
            d.include('jamb_%s'%dy,box((.08,.07,2.55),
                      center=(inner-s*.10,y+dy,1.27),color=(.20,.14,.09)))
        openings.include('door_%s_%s'%(s,j),d)
scene.include('wall_openings',openings)

# Enlarged rear stage is an independently editable asset.
stage = Asset('Rear stage')
stage.include('platform',box((6.6,1.15,.22),center=(0,8.15,.11),
                             color=(.43,.31,.14)))
stage.include('dark_recess',box((6.25,.08,2.35),center=(0,8.88,2.56),
                                color=(.055,.047,.036)))
stage.include('curtain',box((5.2,.06,1.80),center=(0,8.81,2.70),
                            color=(.15,.018,.021)))
for x in (-3.0,3.0):
    stage.include('green_wing_%s'%x,box((.38,.10,2.34),
                  center=(x,8.72,2.57),color=(.045,.23,.065)))
stage.include('valance',box((6.25,.12,.28),center=(0,8.63,3.73),
                            color=(.82,.78,.64)))
stage.include('front_lip',box((6.6,.08,.18),center=(0,7.56,.22),
                              color=(.52,.37,.13)))
board = Asset('Chalkboard')
board.include('surface',box((2.55,.07,1.18),center=(0,7.91,1.65),
                            color=(.12,.30,.25)))
for x in (-1.30,1.30):
    board.include('side_%s'%x,box((.055,.09,1.26),
                  center=(x,7.86,1.65),color=(.60,.58,.43)))
for z in (1.04,2.26):
    board.include('edge_%s'%z,box((2.64,.09,.055),
                  center=(0,7.86,z),color=(.60,.58,.43)))
stage.include('chalkboard',board)
stage.include('lectern',box((.55,.43,1.02),center=(2.22,7.44,.72),
                            color=(.47,.68,.69)))
scene.include('stage',stage)

def student_station(name,x,y,width=1.42,depth=.62):
    a=Asset(name)
    a.include('top',box((width,depth,.09),center=(x,y,.79),color=wood_top))
    a.include('apron',box((width-.08,.055,.15),
                          center=(x,y-depth/2+.045,.67),color=wood))
    for sx in (-1,1):
        for sy in (-1,1):
            a.include('leg_%s_%s'%(sx,sy),
                      box((.058,.058,.73),
                          center=(x+sx*(width/2-.075),
                                  y+sy*(depth/2-.075),.37),color=wood))
    # The low seat overlaps the leg space, as in the photograph.
    a.include('bench_seat',box((width*.83,.27,.06),
                               center=(x,y-.47,.43),color=(.23,.18,.13)))
    a.include('bench_support',box((width*.72,.05,.36),
                                  center=(x,y-.47,.22),color=wood))
    return a

for row,y in enumerate((-5.0,-2.9,-.9,1.0,2.85,4.55,6.05)):
    for col,x in enumerate((-3.65,-1.72,1.05,3.35)):
        scene.include('desk_%d_%d'%(row,col),
                      student_station('Student desk %d %d'%(row,col),x,y))

def backpack(name,x,y,color,scale=1):
    a=Asset(name)
    body=ball(.5,center=(x,y,.28*scale),color=color)
    body.resize((.72*scale,.43*scale,1.08*scale))
    a.include('rounded_body',body)
    a.include('front_pocket',box((.27*scale,.035*scale,.22*scale),
              center=(x,y-.12*scale,.17*scale),
              color=tuple(v*.72 for v in color)))
    a.include('handle',rod(.017*scale,start=(x-.1*scale,y,.55*scale),
                           end=(x+.1*scale,y,.55*scale),color=dark))
    a.include('strap',rod(.018*scale,start=(x+.16*scale,y,.40*scale),
                          end=(x+.27*scale,y-.07*scale,.03),color=dark))
    return a

for name,x,y,c,s in [
    ('foreground_black',-3.55,-6.15,(.025,.035,.045),1.0),
    ('foreground_blue',1.65,-5.55,(.01,.22,.50),1.05),
    ('central_black',.20,-3.65,(.025,.04,.04),.8),
    ('right_blue',3.55,-3.7,(.01,.30,.50),.85),
    ('left_blue',-2.55,-1.9,(.02,.20,.37),.65),
    ('middle_blue',1.9,1.3,(.01,.26,.43),.55)]:
    scene.include(name,backpack(name,x,y,c,s))

ceiling=Asset('Ceiling fittings')
for y in (-5.8,-.3,4.4):
    ceiling.include('beam_%s'%y,box((ROOM_W,.24,.16),
                    center=(0,y,4.25),color=(.84,.85,.80)))
for x,y in ((-2.6,-1.7),(1.7,1.9),(-.2,5.7)):
    ceiling.include('light_%s_%s'%(x,y),box((.20,1.0,.045),
                    center=(x,y,4.24),color=(.95,.95,.86)))

def fan(name,x,y):
    f=Asset(name)
    f.include('downrod',rod(.035,start=(x,y,4.35),end=(x,y,3.92),
                            color=(.19,.18,.16)))
    f.include('hub',ball(.13,center=(x,y,3.90),color=(.19,.18,.16)))
    for k in range(3):
        ang=2*math.pi*k/3+.2
        blade=box((1.25,.15,.035),
                  center=(x+.64*math.cos(ang),y+.64*math.sin(ang),3.89),
                  color=(.20,.19,.17))
        blade.turn('+z',math.degrees(ang))
        f.include('blade_%d'%k,blade)
    return f

for i,(x,y) in enumerate(((-2.6,-5.1),(2.5,-4.5),(-2.1,2.0),(2.2,3.1))):
    ceiling.include('fan_%d'%i,fan('Ceiling fan %d'%i,x,y))
scene.include('ceiling_fittings',ceiling)

wall_items=Asset('Wall details')
for s,y in ((-1,3.7),(1,-.2)):
    wall_items.include('speaker_%s'%s,box((.15,.55,.78),
                       center=(s*(ROOM_W/2-.15),y,3.23),color=(.06,.09,.10)))
for s,y in ((-1,-3.4),(-1,1.0),(1,-3.8),(1,2.0)):
    wall_items.include('frame_%s_%s'%(s,y),
        box((.04,.50,.62),center=(s*(ROOM_W/2-.08),y,3.57),
            color=(.27,.24,.18)))
    wall_items.include('picture_%s_%s'%(s,y),
        box((.045,.39,.50),center=(s*(ROOM_W/2-.11),y,3.57),
            color=(.74,.79,.72)))
scene.include('wall_details',wall_items)

realize(scene)
set_view(CAM_POS,OLD_TARGET,lens=CAM_LENS,sensor=36)
sc=bpy.context.scene
sc.render.resolution_x=512
sc.render.resolution_y=340
sc.render.resolution_percentage=100

# Projection checks use actual geometry points. Reference estimates and
# computed projections are printed separately; correspondence is approximate.
landmarks=[
    ('board upper left',(-1.30,7.86,2.26),(.45,.33)),
    ('board lower right',(1.30,7.86,1.04),(.58,.42)),
    ('near desk left',(-2.43,-5.31,.835),(.15,.60)),
    ('near desk right',(-1.01,-5.31,.835),(.36,.60)),
    ('left window top',(-4.48,-2.9,3.29),(.04,.18))
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=512,y=340,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print('%-22s ref=%s projected=%s'%
              (name,ref,None if uv is None else tuple(round(v,3) for v in uv)))

projection_table('Previous aim')
# A small trial verifies that lowering aim moves fixed points upward.
set_view(CAM_POS,(0,4.2,1.75),lens=CAM_LENS,sensor=36)
projection_table('Small downward aim trial')
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
projection_table('Revised aim')

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
background.inputs['Color'].default_value=(.75,.76,.72,1)
background.inputs['Strength'].default_value=.8
area_emitter((0,-3,4.05),power=800,size=7,target=(0,1,0))
area_emitter((0,5,4.05),power=600,size=6,target=(0,4,0))
