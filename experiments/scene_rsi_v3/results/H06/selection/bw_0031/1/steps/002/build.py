# Reference inventory and visual comparison, normalized to the full slide:
# The room photograph occupies (0.03, 0.65)-(0.94, 1.00). Within that
# photograph, the instrument wall runs from its left edge to about x=.58;
# its upper cabinet band is light, with square instruments below and a dark
# horizontal grille near the middle. The long desk crosses the foreground,
# from the cropped left edge to roughly x=.70, and hides the wall base.
# A dark vertical doorway is near x=.75; the small independent console is
# at the right edge. The visible floor is dark and extends to the lower edge.
# The yellow GRID panel is a separate photograph on the slide, not demonstrably
# on a particular room wall; its mounting in this reconstruction is uncertain.
#
# Previous render versus the room photograph, expressed within the photograph
# and the rendered frame respectively:
# - Wall instruments: reference approximately (0,.23)-(.58,.62); render
#   mostly hidden behind the room shell and desk, approximately (.34,.44)-(.69,.52).
# - Foreground desk: reference approximately (0,.39)-(.70,1); render
#   approximately (.15,.46)-(.68,.66). Its upper edge should rise toward
#   the right; the render is too small and nearly horizontal.
# - Right console and doorway: reference around (.71,.16)-(1,.65);
#   render obscured by the right wall.
# - Floor: reference occupies the lower right; render shows the outside of a
#   box and a large empty gray background. The ceiling occludes the interior.
# Largest corrections: remove camera-facing enclosure occlusion; put the
# camera inside the room at lower elevation, looking across the long desk;
# enlarge the foreground desk in frame. Preserve the relative wall bank,
# grille, doorway and small console relationships. The wall and ceiling still
# exist, but are positioned behind or above the camera's field of view.
# The first camera was (7.7,-11.7,6.3), target (0,.45,1.22), lens 38.
# New camera is near the left/front of the room, looking toward the back
# right. This should make the desk run diagonally upward to the right, expose
# the rear bank, and keep the right-hand console visible. Landmark projections
# below compare the previous camera with the final and a small aim trial.
# These projected points are not measured visible silhouette bounds.
#
# Primitive budget: architecture ~12, wall cabinets and seams ~15,
# instrument frames/faces ~72, grille ~8, main desk ~95, small desk ~20,
# yellow mimic ~48, ceiling fixtures ~4: about 274 SceneAct primitives.
# Unseen room boundaries and the mimic panel mounting remain uncertain.

from sceneact import *
import bpy
import math
from mathutils import Vector

# Dimensions are in plausible room-scale units, not surveyed measurements.
ROOM_W = 8.4
ROOM_D = 7.2
ROOM_H = 3.1
BACK_Y = 2.8
LEFT_X = -4.2
RIGHT_X = 4.2
FRONT_Y = BACK_Y - ROOM_D

DESK_X = -0.75
DESK_Y = -0.15
DESK_W = 5.75
DESK_D = 1.75
DESK_BASE_H = 0.76
DESK_ANGLE = 16.0

# Camera position, aim, and lens are independent of object dimensions.
CAMERA_POSITION = (-5.5, -7.5, 3.05)
CAMERA_TARGET = (-0.20, 1.45, 1.13)
CAMERA_LENS = 30.0
BASE_POSITION = (7.7, -11.7, 6.3)
BASE_TARGET = (0.0, 0.45, 1.22)
BASE_LENS = 38.0

wall = (0.70, 0.68, 0.63)
upper_wall = (0.77, 0.75, 0.70)
floor_col = (0.30, 0.275, 0.25)
metal = (0.62, 0.61, 0.57)
light_metal = (0.76, 0.75, 0.70)
face = (0.88, 0.86, 0.80)
seam = (0.34, 0.33, 0.31)
dark = (0.10, 0.105, 0.10)
black = (0.025, 0.025, 0.022)
yellow = (0.93, 0.66, 0.12)
red = (0.72, 0.035, 0.025)
amber = (1.0, 0.48, 0.02)

scene = Scene('1970s power dispatch control room')

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# The room is enclosed; the front wall and ceiling are behind/above the
# camera. This avoids the exterior shell masking the photographed interior.
architecture = Asset('Architecture')
add(architecture, 'floor', (ROOM_W, ROOM_D, .12),
    (0, (BACK_Y+FRONT_Y)/2, -.06), floor_col)
add(architecture, 'back_wall', (ROOM_W, .12, ROOM_H),
    (0, BACK_Y, ROOM_H/2), upper_wall)
add(architecture, 'left_wall', (.12, ROOM_D, ROOM_H),
    (LEFT_X, (BACK_Y+FRONT_Y)/2, ROOM_H/2), wall)
add(architecture, 'right_wall', (.12, ROOM_D, ROOM_H),
    (RIGHT_X, (BACK_Y+FRONT_Y)/2, ROOM_H/2), wall)
# The camera is outside the cropped front opening. Only the portions of the
# front wall to its sides are modeled; exact front-wall features are unknown.
add(architecture, 'ceiling', (ROOM_W, ROOM_D, .10),
    (0, (BACK_Y+FRONT_Y)/2, ROOM_H+.05), upper_wall)
add(architecture, 'back_skirting', (ROOM_W, .035, .12),
    (0, BACK_Y-.08, .06), seam)
for i, x in enumerate((-3.55, -2.4, -1.25, -.1, 1.05, 2.2, 3.35)):
    add(architecture, 'upper_wall_joint_%d' % i, (.018, .025, 1.20),
        (x, BACK_Y-.075, 2.49), seam)
scene.include('Architecture', architecture)

# The tall bank has a blank upper cabinet band and a lower field of meters.
bank = Asset('Main wall instrument bank')
add(bank, 'cabinet_body', (5.90, .20, 2.70),
    (-1.10, BACK_Y-.14, 1.35), light_metal)
for i, x in enumerate((-3.99, -2.83, -1.67, -.51, .65, 1.81)):
    add(bank, 'cabinet_division_%d' % i, (.022, .026, 2.68),
        (x, BACK_Y-.25, 1.35), seam)
add(bank, 'upper_horizontal_joint', (5.86, .026, .025),
    (-1.10, BACK_Y-.255, 1.76), seam)

# Uniform instruments occupy both sides of the broad central grille.
for col in range(12):
    x = -3.76 + .47*col
    for row in range(3):
        if 4 <= col <= 7:
            continue
        z = .71 + .37*row
        add(bank, 'meter_frame_%02d_%d' % (col,row),
            (.32,.045,.30), (x,BACK_Y-.285,z), dark)
        add(bank, 'meter_face_%02d_%d' % (col,row),
            (.245,.018,.225), (x,BACK_Y-.317,z), face)
        # Single dark pointer per large instrument.
        pointer = box((.012,.012,.085),
                      center=(x,BACK_Y-.331,z), color=dark)
        pointer.turn(axis='+y', degrees=((col*19+row*23)%70)-35)
        bank.include('meter_pointer_%02d_%d' % (col,row), pointer)
add(bank, 'grille_recess', (1.72,.045,.70),
    (-1.17,BACK_Y-.29,1.09), dark)
for i in range(6):
    add(bank, 'grille_slat_%d' % i, (1.62,.024,.032),
        (-1.17,BACK_Y-.322,.80+i*.115), light_metal)
scene.include('Main wall instrument bank', bank)

door = Asset('Rear doorway')
add(door, 'dark_doorway', (.68,.05,2.05), (2.38,BACK_Y-.085,1.14), dark)
add(door, 'door_panel', (.48,.025,1.72), (2.38,BACK_Y-.12,1.08),
    (.28,.27,.25))
add(door, 'upper_glass', (.39,.018,.58), (2.38,BACK_Y-.14,1.66),
    (.43,.43,.40))
scene.include('Rear doorway', door)

# Long desk, separate pedestal, horizontal writing ledge, inclined control
# surface and individual face plates.
desk = Asset('Long operator desk')
add(desk, 'base', (DESK_W,DESK_D-.12,DESK_BASE_H),
    (DESK_X,DESK_Y,DESK_BASE_H/2), (.31,.30,.28))
add(desk, 'front_panel', (DESK_W,.055,.58),
    (DESK_X,DESK_Y-DESK_D/2,.38), (.40,.39,.36))
add(desk, 'writing_ledge', (DESK_W+.08,.43,.075),
    (DESK_X,DESK_Y-.68,.80), light_metal)
for i in range(6):
    x = DESK_X-DESK_W/2+i*DESK_W/5
    add(desk, 'front_seam_%d' % i, (.018,.025,.55),
        (x,DESK_Y-DESK_D/2-.04,.38), seam)

angle = math.radians(DESK_ANGLE)
panel_center = (DESK_X, DESK_Y+.17, .99)
def desk_point(x, y, z):
    return (panel_center[0]+x,
            panel_center[1]+y*math.cos(angle)-z*math.sin(angle),
            panel_center[2]+y*math.sin(angle)+z*math.cos(angle))
p = box((DESK_W,1.12,.08), center=panel_center, color=light_metal)
p.turn(axis='+x', degrees=DESK_ANGLE)
desk.include('inclined_panel', p)
for j in range(5):
    x = -DESK_W/2+.575+j*1.15
    plate = box((1.08,1.02,.018), center=desk_point(x,0,.052), color=face)
    plate.turn(axis='+x', degrees=DESK_ANGLE)
    desk.include('face_plate_%d' % j, plate)
    for r in range(3):
        for c in range(5):
            xx = x-.42+c*.21
            yy = -.34+r*.32
            if r == 2 and c in (1,3):
                meter = box((.13,.12,.018), center=desk_point(xx,yy,.07),
                            color=dark)
                meter.turn(axis='+x', degrees=DESK_ANGLE)
                desk.include('desk_meter_%d_%d_%d' % (j,r,c), meter)
            else:
                desk.include('desk_control_%d_%d_%d' % (j,r,c),
                    rod(radius=.028, start=desk_point(xx,yy,.07),
                        end=desk_point(xx,yy,.105),
                        color=red if (j*7+r*5+c)%19 == 0 else dark))
scene.include('Long operator desk', desk)

small = Asset('Right independent console')
SX, SY = 3.12, 1.55
add(small, 'base', (1.50,.88,.78), (SX,SY,.39), (.39,.38,.35))
add(small, 'toe', (1.26,.03,.12), (SX,SY-.46,.08), dark)
sa = math.radians(16)
scen = (SX,SY,.91)
def small_point(x,y,z):
    return (scen[0]+x,scen[1]+y*math.cos(sa)-z*math.sin(sa),
            scen[2]+y*math.sin(sa)+z*math.cos(sa))
s = box((1.54,.92,.08), center=scen, color=face)
s.turn(axis='+x', degrees=16)
small.include('sloped_top', s)
for r in range(3):
    for c in range(5):
        x = -.56+c*.28
        y = -.27+r*.27
        small.include('control_%d_%d' % (r,c),
            rod(radius=.026,start=small_point(x,y,.05),
                end=small_point(x,y,.085),
                color=red if (r,c)==(2,3) else dark))
scene.include('Right independent console', small)

# GRID panel on the right wall, facing the room. The source presents it
# separately; its exact position relative to the room is not established.
grid = Asset('Yellow GRID mimic panel')
GX, GY, GZ = 4.115, -.10, 1.92
add(grid, 'yellow_board', (.07,1.42,1.78), (GX,GY,GZ), yellow)
FX = GX-.052
def grid_line(name, a, b, radius=.011):
    grid.include(name, rod(radius=radius,
        start=(FX,GY+a[0],GZ+a[1]), end=(FX,GY+b[0],GZ+b[1]),
        color=black))
grid_line('main_bus', (0,-.78), (0,.78), .014)
for k,z in enumerate((-.49,-.20,.17,.48)):
    grid_line('crossbar_%d'%k,(-.36,z),(.36,z))
for k,y in enumerate((-.36,-.12,.12,.36)):
    grid_line('branch_%d'%k,(y,-.49),(y,.48),.009)
for r,z in enumerate((-.49,-.20,.17,.48)):
    for c,y in enumerate((-.36,-.12,.12,.36)):
        add(grid,'amber_indicator_%d_%d'%(r,c),(.025,.09,.10),
            (FX-.018,GY+y,GZ+z),amber)
for i,z in enumerate((.64,.37,.10,-.18,-.46)):
    grid.include('red_lamp_%d'%i,
        rod(radius=.055,start=(FX-.01,GY-.55,GZ+z),
            end=(FX-.055,GY-.55,GZ+z),color=red))
for i,z in enumerate((.32,.05,-.22,-.49)):
    grid.include('selector_%d'%i,
        rod(radius=.04,start=(FX-.01,GY+.55,GZ+z),
            end=(FX-.055,GY+.55,GZ+z),color=black))
scene.include('Yellow GRID mimic panel', grid)

ceiling = Asset('Fluorescent ceiling fixtures')
for i,(x,y) in enumerate(((-2,-1.2),(1,-1.2),(-2,1.2),(1,1.2))):
    add(ceiling,'fixture_%d'%i,(1.5,.38,.025),
        (x,y,ROOM_H-.02),face)
scene.include('Fluorescent ceiling fixtures', ceiling)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get('Background') or nodes.new('ShaderNodeBackground')
output = nodes.get('World Output') or nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],
                             output.inputs['Surface'])
background.inputs['Color'].default_value = (.72,.70,.66,1)
background.inputs['Strength'].default_value = .45

# Preserve the original portrait aspect for the runner and projection checks.
sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100

# A small numerical check compares the actual old and new camera projections.
# References below correspond to the room photograph expanded to the frame.
# The left foreground edge is a crop constraint, not a physical desk corner.
landmarks = [
    ('bank top left', (-3.99,BACK_Y-.25,2.70), (.02,.08)),
    ('grille center', (-1.17,BACK_Y-.32,1.09), (.36,.37)),
    ('desk front left', (DESK_X-DESK_W/2,DESK_Y-DESK_D/2,.80), (.03,.72)),
    ('desk rear right', desk_point(DESK_W/2,.56,.04), (.70,.43)),
    ('small console', (SX,SY,.95), (.88,.49)),
]
def projections(position, target, lens):
    set_view(position, target, lens=lens)
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for _,point,_ in landmarks:
        clip = proj @ cam.matrix_world.inverted() @ Vector((*point,1.0))
        result.append(None if clip.w <= 1e-8 else
                      (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return result

baseline = projections(BASE_POSITION, BASE_TARGET, BASE_LENS)
trial = projections(CAMERA_POSITION,
                    (CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]+.12),
                    CAMERA_LENS)
final = projections(CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS)
print('Landmark: reference | previous camera | aim trial | final camera')
for (name,point,ref),old,tst,new in zip(landmarks,baseline,trial,final):
    def fmt(v):
        return None if v is None else tuple(round(a,3) for a in v)
    def err(v):
        return float('inf') if v is None else math.hypot(v[0]-ref[0],v[1]-ref[1])
    print(name, ref, fmt(old), fmt(tst), fmt(new),
          'final versus previous:', 'closer' if err(new)<err(old) else 'farther')
# Trial aim is restored above. Geometry dimensions are retained from the
# previous build within normal approximation; exposed visibility is the main
# correction. Projection comparisons cannot prove occlusion or surface shape.

area_emitter((-1.5,-1.0,2.96),power=700,size=4.5,
             target=(-1,1.0,1),color=(1,.95,.88))
area_emitter((2.2,1.0,2.95),power=450,size=3,
             target=(1.5,2.2,1),color=(1,.96,.90))
area_emitter((-3.5,-3.5,2.8),power=350,size=3,
             target=(-1,1,1),color=(1,.96,.90))
