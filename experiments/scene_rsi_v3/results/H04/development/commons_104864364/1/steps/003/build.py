# Reference inventory and comparison, normalized image coordinates:
# Architecture: cream ceiling and upper walls, yellow lower walls, light tiled
# floor, and windows and doors along both sides. Wall and floor edges converge
# toward the stage; reference ceiling fans partly cross the top crop.
# Stage: reference about (.37,.24)-(.66,.43), last render about
# (.40,.31)-(.60,.46). The rendered dark recess is too small and low.
# Board: reference about (.48,.33)-(.58,.41), render about (.46,.38)-(.55,.44).
# Foreground left desk: reference about (.14,.59)-(.37,.89), render about
# (.25,.62)-(.40,.83). Foreground right desk: reference about (.51,.55)-(.70,.82),
# render about (.55,.62)-(.70,.80). Desks overlap benches and bags; rear desks
# become densely occluded. The rendered benches have overly solid supports.
# Reference nearest windows start near x=.04, y=.18; rendered window frames
# start around x=.15, y=.28. Their precise depths and correspondences are uncertain.
# Reference floor has a varied, warm tile pattern; the last render is flatter.
#
# Largest supported corrections:
# 1. Increase lens from 23 to 27 mm and lower target slightly: background stage
#    and window corners should spread outward and move upward, while foreground
#    objects spread outward. The small projection trial below checks direction.
# 2. Make the curtain nearly black and widen its stage locally, retaining red
#    highlights and green wings. The dark rear region should occupy more area.
# 3. Move the nearest left desk left and widen it, moving its outline toward
#    (.14,.59)-(.37,.89). Replace solid bench supports with thin legs to restore
#    the visible gaps. Darken desk surfaces; their brightness also depends on light.
# 4. Move nearest fans toward the camera to put their silhouettes near the top
#    crop, and add warm floor-tile variation. Side opening depth is uncertain.
#
# Approximate expanded primitive count: room 6, floor joints 42, openings 68,
# stage 16, desks 28*9=252, bags 24, fans 20, other fittings 15: about 443.
# Each room, desk, bag, opening and fitting is an editable named SceneAct asset.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene('Classroom')

ROOM_W = 9.2
FRONT_Y, BACK_Y = -8.0, 9.0
ROOM_H = 4.35
CAM_POS = (0.0, -11.3, 2.65)
OLD_TARGET = (0.0, 4.2, 0.40)
CAM_TARGET = (0.0, 4.2, 0.08)
OLD_LENS, CAM_LENS = 23.0, 27.0

cream = (.84, .83, .70)
yellow = (.98, .72, .025)
floor_col = (.72, .62, .48)
wood = (.20, .13, .075)
wood_top = (.19, .16, .13)
dark = (.035, .035, .032)
brown = (.30, .20, .12)

room = Asset('Architecture')
room.include('floor', box((ROOM_W, 17, .12), center=(0, .5, -.06), color=floor_col))
room.include('ceiling', box((ROOM_W, 17, .12), center=(0, .5, ROOM_H+.06),
                            color=(.88, .89, .84)))
for s in (-1, 1):
    x = s * ROOM_W / 2
    room.include('upper_wall_%s' % s,
        box((.12, 17, ROOM_H-1.05), center=(x, .5, 2.70), color=cream))
    room.include('yellow_lower_wall_%s' % s,
        box((.13, 17, 1.05), center=(x-s*.008, .5, .525), color=yellow))
room.include('rear_wall', box((ROOM_W, .15, ROOM_H),
                              center=(0, 9, ROOM_H/2), color=cream))
scene.include('architecture', room)

tiles = Asset('Floor tile joints')
for i in range(-7, 8):
    tiles.include('long_%d' % i,
        box((.010, 17, .004), center=(i*.65, .5, .004), color=(.62,.54,.43)))
for i in range(27):
    tiles.include('cross_%d' % i,
        box((ROOM_W, .010, .004), center=(0, -8+i*.65, .005), color=(.62,.54,.43)))
scene.include('floor_joints', tiles)

openings = Asset('Side windows and doors')
for s in (-1, 1):
    inner = s * (ROOM_W/2-.075)
    for j, y in enumerate((-6.2, -2.3, 1.5, 5.0)):
        w = Asset('Window %s %s' % (s, j))
        w.include('dark_reveal', box((.028, 1.25, 2.54),
                  center=(inner-s*.015, y, 2.04), color=(.27,.23,.16)))
        w.include('bright_pane', box((.03, 1.05, 2.30),
                  center=(inner-s*.035, y, 2.06), color=(1,1,.92)))
        for dy in (-.60, .60):
            w.include('jamb_%s' % dy, box((.075,.075,2.55),
                      center=(inner-s*.06,y+dy,2.04), color=brown))
        for z in (.78, 2.94, 3.29):
            w.include('crossbar_%s' % z, box((.08,1.25,.065),
                      center=(inner-s*.065,y,z), color=brown))
        openings.include('window_%s_%s' % (s,j), w)
    for j,y in enumerate((-4.25, 2.95)):
        d = Asset('Door %s %s' % (s,j))
        d.include('leaf', box((.055,.82,2.45),
                  center=(inner-s*.075,y,1.23), color=(.31,.22,.14)))
        for dy in (-.44,.44):
            d.include('jamb_%s' % dy, box((.08,.07,2.55),
                      center=(inner-s*.10,y+dy,1.27), color=(.20,.14,.09)))
        openings.include('door_%s_%s' % (s,j), d)
scene.include('wall_openings', openings)

stage = Asset('Rear stage')
stage.include('platform', box((6.9,1.15,.22), center=(0,8.15,.11),
                              color=(.43,.31,.14)))
stage.include('dark_recess', box((6.55,.08,2.35), center=(0,8.88,2.56),
                                 color=(.025,.021,.018)))
stage.include('curtain', box((5.45,.06,1.80), center=(0,8.81,2.70),
                             color=(.075,.012,.016)))
for x in (-3.15,3.15):
    stage.include('green_wing_%s' % x, box((.38,.10,2.34),
                  center=(x,8.72,2.57), color=(.045,.23,.065)))
stage.include('valance', box((6.55,.12,.28), center=(0,8.63,3.73),
                             color=(.82,.78,.64)))
stage.include('front_lip', box((6.9,.08,.18), center=(0,7.56,.22),
                               color=(.52,.37,.13)))
board = Asset('Chalkboard')
board.include('surface', box((2.55,.07,1.18), center=(0,7.91,1.65),
                             color=(.12,.30,.25)))
for x in (-1.30,1.30):
    board.include('side_%s' % x, box((.055,.09,1.26),
                  center=(x,7.86,1.65), color=(.60,.58,.43)))
for z in (1.04,2.26):
    board.include('edge_%s' % z, box((2.64,.09,.055),
                  center=(0,7.86,z), color=(.60,.58,.43)))
stage.include('chalkboard', board)
stage.include('lectern', box((.55,.43,1.02), center=(2.22,7.44,.72),
                             color=(.47,.68,.69)))
scene.include('stage', stage)

def student_station(name, x, y, width=1.42, depth=.62):
    a = Asset(name)
    a.include('top', box((width,depth,.09), center=(x,y,.79), color=wood_top))
    a.include('apron', box((width-.08,.055,.15),
                           center=(x,y-depth/2+.045,.67), color=wood))
    for sx in (-1,1):
        for sy in (-1,1):
            a.include('leg_%s_%s' % (sx,sy), box((.058,.058,.73),
                      center=(x+sx*(width/2-.075),y+sy*(depth/2-.075),.37),
                      color=wood))
    a.include('bench_seat', box((width*.83,.27,.06),
                                 center=(x,y-.47,.43), color=(.18,.14,.10)))
    for sx in (-1,1):
        a.include('bench_leg_%s' % sx, box((.055,.055,.39),
                  center=(x+sx*width*.34,y-.47,.21), color=wood))
    return a

for row,y in enumerate((-5.0,-2.9,-.9,1.0,2.85,4.55,6.05)):
    for col,x in enumerate((-3.65,-1.72,1.05,3.35)):
        width = 1.42
        if row == 0 and col == 1:
            x, width = -2.05, 1.72
        scene.include('desk_%d_%d' % (row,col),
                      student_station('Student desk %d %d' % (row,col),
                                      x,y,width))

def backpack(name,x,y,color,scale=1):
    a = Asset(name)
    body = ball(.5, center=(x,y,.28*scale), color=color)
    body.resize((.72*scale,.43*scale,1.08*scale))
    a.include('rounded_body', body)
    a.include('front_pocket', box((.27*scale,.035*scale,.22*scale),
              center=(x,y-.12*scale,.17*scale),
              color=tuple(v*.72 for v in color)))
    a.include('handle', rod(.017*scale, start=(x-.1*scale,y,.55*scale),
                            end=(x+.1*scale,y,.55*scale), color=dark))
    a.include('strap', rod(.018*scale, start=(x+.16*scale,y,.40*scale),
                           end=(x+.27*scale,y-.07*scale,.03), color=dark))
    return a

for name,x,y,c,s in [
    ('foreground_black',-3.55,-6.15,(.025,.035,.045),1.0),
    ('foreground_blue',1.65,-5.55,(.01,.22,.50),1.05),
    ('central_black',.20,-3.65,(.025,.04,.04),.8),
    ('right_blue',3.55,-3.7,(.01,.30,.50),.85),
    ('left_blue',-2.55,-1.9,(.02,.20,.37),.65),
    ('middle_blue',1.9,1.3,(.01,.26,.43),.55)]:
    scene.include(name, backpack(name,x,y,c,s))

ceiling = Asset('Ceiling fittings')
for y in (-5.8,-.3,4.4):
    ceiling.include('beam_%s' % y, box((ROOM_W,.24,.16),
                    center=(0,y,4.25), color=(.84,.85,.80)))
for x,y in ((-2.6,-1.7),(1.7,1.9),(-.2,5.7)):
    ceiling.include('light_%s_%s' % (x,y), box((.20,1.0,.045),
                    center=(x,y,4.24), color=(.95,.95,.86)))

def fan(name,x,y):
    f = Asset(name)
    f.include('downrod', rod(.035, start=(x,y,4.35), end=(x,y,3.92),
                             color=(.19,.18,.16)))
    f.include('hub', ball(.13, center=(x,y,3.90), color=(.19,.18,.16)))
    for k in range(3):
        ang = 2*math.pi*k/3+.2
        blade = box((1.25,.15,.035),
                    center=(x+.64*math.cos(ang),y+.64*math.sin(ang),3.89),
                    color=(.20,.19,.17))
        blade.turn('+z', math.degrees(ang))
        f.include('blade_%d' % k, blade)
    return f

for i,(x,y) in enumerate(((-2.6,-6.2),(2.5,-5.8),(-2.1,2.0),(2.2,3.1))):
    ceiling.include('fan_%d' % i, fan('Ceiling fan %d' % i,x,y))
scene.include('ceiling_fittings', ceiling)

wall_items = Asset('Wall details')
for s,y in ((-1,3.7),(1,-.2)):
    wall_items.include('speaker_%s' % s, box((.15,.55,.78),
                       center=(s*(ROOM_W/2-.15),y,3.23), color=(.06,.09,.10)))
for s,y in ((-1,-3.4),(-1,1.0),(1,-3.8),(1,2.0)):
    wall_items.include('frame_%s_%s' % (s,y),
        box((.04,.50,.62), center=(s*(ROOM_W/2-.08),y,3.57),
            color=(.27,.24,.18)))
    wall_items.include('picture_%s_%s' % (s,y),
        box((.045,.39,.50), center=(s*(ROOM_W/2-.11),y,3.57),
            color=(.74,.79,.72)))
scene.include('wall_details', wall_items)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 340
sc.render.resolution_percentage = 100

landmarks = [
    ('board upper left', (-1.30,7.86,2.26), (.48,.33)),
    ('board lower right', (1.30,7.86,1.04), (.58,.41)),
    ('near desk left', (-2.91,-5.31,.835), (.14,.60)),
    ('near desk right', (-1.19,-5.31,.835), (.37,.60)),
    ('left window top', (-4.48,-2.9,3.29), (.04,.18)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=512, y=340,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip = proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print('%-22s reference=%s projected=%s' %
              (name,ref,None if uv is None else tuple(round(v,3) for v in uv)))

set_view(CAM_POS, OLD_TARGET, lens=OLD_LENS, sensor=36)
projection_table('Previous camera')
set_view(CAM_POS, (0,4.2,.30), lens=24, sensor=36)
projection_table('Small downward aim and longer lens trial')
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
projection_table('Revised camera')

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
background.inputs['Color'].default_value = (.75,.76,.72,1)
background.inputs['Strength'].default_value = .8
area_emitter((0,-3,4.05), power=800, size=7, target=(0,1,0))
area_emitter((0,5,4.05), power=600, size=6, target=(0,4,0))
