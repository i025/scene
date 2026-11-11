# Reference inventory, estimated from the original slide:
# - The room photograph occupies (0.03, 0.65)-(0.94, 1.00) of the slide.
#   Its left edge crops the instrument bank and the foreground desk.
# - Within the photograph, the foreground desk extends roughly from (0, .38)
#   to (.70, 1). Its long edges rise toward the right and its dark base
#   occludes the lower part of the instrument wall.
# - The pale back-wall cabinets occupy approximately (0, 0)-(.69, .57).
#   Square instruments flank a dark horizontal grille around (.34, .34).
# - A dark doorway stands around (.72, .10)-(.78, .55), and a separate
#   small console occupies approximately (.81, .30)-(1, .67).
# - The yellow GRID board is shown separately on the slide. Its position
#   relative to the room is uncertain; a wall mounting is an interpretation.
# - The foreground crop and hidden room boundaries are not physical corners.
#
# Comparison with the previous complete render, using the room photograph
# expanded to a frame for rough comparison:
# 1. The near left wall covers approximately x=0-.36 of the render, while
#    the reference shows instruments and desk there. Camera position and wall
#    occlusion are the largest high-contrast discrepancies.
# 2. The desk is approximately (.36,.47)-(.88,.69) in the render, versus
#    (0,.38)-(.70,1) in the reference; it is too small and its long edge is
#    too flat. Moving the camera inside and closer should enlarge the desk,
#    move its near end left/down, and reveal the bank.
# 3. The render's background instruments are only around (.36,.43)-(.60,.53);
#    in the reference they extend across much of the left background. The
#    doorway and separate small console are also largely hidden.
# 4. The reference has a dark desk base and floor; the render is washed out.
#    Brightness depends on illumination and orientation as well as color.
#    Lighting is reduced and the desk base is given a darker metal finish.
# The long desk must overlap the bank, while a gap remains between it and
# the independent console. The upper wall and the doorway protect the
# background relationships while the camera is changed.
#
# Camera trial: the prior camera was outside the left wall. The new position
# is inside the room and closer to the foreground desk. Lens and aim remain
# separately adjustable. Projection tables below compare the actual previous
# and proposed cameras plus a small aim trial. They are point projections,
# not measured silhouette bounds or proof of visibility. If a small lens trial
# improves the selected landmark error without seriously worsening a protected
# doorway anchor, it is retained; otherwise it is restored.
#
# Approximate SceneAct primitive count: architecture 12, instrument bank
# 92, doorway 3, main desk 94, smaller console 19, GRID board 40, ceiling
# fixtures 4: about 264 primitives. Rods and boxes each count as one.
# No external files, texture images, rendering, or saving are used.

from sceneact import *
import bpy
import math
from mathutils import Vector

# Room dimensions are plausible estimates, not surveyed dimensions.
ROOM_W, ROOM_D, ROOM_H = 8.4, 7.2, 3.1
BACK_Y = 2.8
FRONT_Y = BACK_Y - ROOM_D
LEFT_X, RIGHT_X = -4.2, 4.2

DESK_X, DESK_Y = -0.75, -0.15
DESK_W, DESK_D = 5.75, 1.75
DESK_BASE_H, DESK_ANGLE = 0.76, 16.0
SX, SY = 3.12, 1.55

# Position, aim and lens are independent of the asset dimensions.
BASE_POSITION = (-5.5, -7.5, 3.05)
BASE_TARGET = (-0.20, 1.45, 1.13)
BASE_LENS = 30.0
CAMERA_POSITION = (-3.80, -3.95, 2.25)
CAMERA_TARGET = (-0.25, 1.55, 1.30)
CAMERA_LENS = 26.0

wall = (0.70, 0.68, 0.63)
upper_wall = (0.77, 0.75, 0.70)
floor_col = (0.28, 0.25, 0.22)
metal = (0.60, 0.59, 0.55)
light_metal = (0.72, 0.71, 0.67)
face = (0.85, 0.83, 0.77)
seam = (0.34, 0.33, 0.31)
dark = (0.095, 0.095, 0.085)
black = (0.025, 0.025, 0.022)
yellow = (0.88, 0.62, 0.10)
red = (0.72, 0.035, 0.025)
amber = (0.95, 0.43, 0.015)

scene = Scene('1970s grid dispatch control room')

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Room shell. The open front corresponds to the cropped photographic view.
architecture = Asset('Architecture')
add(architecture, 'floor', (ROOM_W, ROOM_D, .12),
    (0, (BACK_Y + FRONT_Y)/2, -.06), floor_col)
add(architecture, 'back_wall', (ROOM_W, .12, ROOM_H),
    (0, BACK_Y, ROOM_H/2), upper_wall)
add(architecture, 'left_wall', (.12, ROOM_D, ROOM_H),
    (LEFT_X, (BACK_Y + FRONT_Y)/2, ROOM_H/2), wall)
add(architecture, 'right_wall', (.12, ROOM_D, ROOM_H),
    (RIGHT_X, (BACK_Y + FRONT_Y)/2, ROOM_H/2), wall)
add(architecture, 'ceiling', (ROOM_W, ROOM_D, .10),
    (0, (BACK_Y + FRONT_Y)/2, ROOM_H + .05), upper_wall)
add(architecture, 'back_skirting', (ROOM_W, .035, .12),
    (0, BACK_Y - .08, .06), seam)
for i, x in enumerate((-3.55, -2.4, -1.25, -.1, 1.05, 2.2, 3.35)):
    add(architecture, 'wall_joint_%d' % i, (.018, .025, 1.20),
        (x, BACK_Y - .075, 2.49), seam)
scene.include('Architecture', architecture)

# Upper cabinet band and regular instrument arrays surrounding the grille.
bank = Asset('Main wall instrument bank')
add(bank, 'cabinet_body', (5.90, .20, 2.70),
    (-1.10, BACK_Y - .14, 1.35), light_metal)
for i, x in enumerate((-3.99, -2.83, -1.67, -.51, .65, 1.81)):
    add(bank, 'cabinet_division_%d' % i, (.022, .026, 2.68),
        (x, BACK_Y - .25, 1.35), seam)
add(bank, 'upper_horizontal_joint', (5.86, .026, .025),
    (-1.10, BACK_Y - .255, 1.76), seam)
for col in range(12):
    x = -3.76 + .47 * col
    for row in range(3):
        if 4 <= col <= 7:
            continue
        z = .71 + .37 * row
        add(bank, 'meter_frame_%02d_%d' % (col, row),
            (.32, .045, .30), (x, BACK_Y - .285, z), dark)
        add(bank, 'meter_face_%02d_%d' % (col, row),
            (.245, .018, .225), (x, BACK_Y - .317, z), face)
        pointer = box((.012, .012, .085),
                      center=(x, BACK_Y - .331, z), color=dark)
        pointer.turn(axis='+y', degrees=((col * 19 + row * 23) % 70) - 35)
        bank.include('meter_pointer_%02d_%d' % (col, row), pointer)
add(bank, 'grille_recess', (1.72, .045, .70),
    (-1.17, BACK_Y - .29, 1.09), dark)
for i in range(6):
    add(bank, 'grille_slat_%d' % i, (1.62, .024, .032),
        (-1.17, BACK_Y - .322, .80 + i * .115), light_metal)
scene.include('Main wall instrument bank', bank)

door = Asset('Rear doorway')
add(door, 'dark_opening', (.68, .05, 2.05),
    (2.38, BACK_Y - .085, 1.14), dark)
add(door, 'door_panel', (.48, .025, 1.72),
    (2.38, BACK_Y - .12, 1.08), (.28, .27, .25))
add(door, 'upper_glass', (.39, .018, .58),
    (2.38, BACK_Y - .14, 1.66), (.43, .43, .40))
scene.include('Rear doorway', door)

desk = Asset('Long operator desk')
add(desk, 'base', (DESK_W, DESK_D - .12, DESK_BASE_H),
    (DESK_X, DESK_Y, DESK_BASE_H / 2), (.23, .22, .20))
add(desk, 'front_panel', (DESK_W, .055, .58),
    (DESK_X, DESK_Y - DESK_D/2, .38), (.30, .29, .27))
add(desk, 'writing_ledge', (DESK_W + .08, .43, .075),
    (DESK_X, DESK_Y - .68, .80), light_metal)
for i in range(6):
    x = DESK_X - DESK_W/2 + i * DESK_W/5
    add(desk, 'front_seam_%d' % i, (.018, .025, .55),
        (x, DESK_Y - DESK_D/2 - .04, .38), seam)

angle = math.radians(DESK_ANGLE)
panel_center = (DESK_X, DESK_Y + .17, .99)

def desk_point(x, y, z):
    return (panel_center[0] + x,
            panel_center[1] + y*math.cos(angle) - z*math.sin(angle),
            panel_center[2] + y*math.sin(angle) + z*math.cos(angle))

panel = box((DESK_W, 1.12, .08), center=panel_center, color=light_metal)
panel.turn(axis='+x', degrees=DESK_ANGLE)
desk.include('inclined_panel', panel)
for j in range(5):
    x = -DESK_W/2 + .575 + j * 1.15
    plate = box((1.08, 1.02, .018), center=desk_point(x, 0, .052),
                color=face)
    plate.turn(axis='+x', degrees=DESK_ANGLE)
    desk.include('face_plate_%d' % j, plate)
    for r in range(3):
        for c in range(5):
            xx = x - .42 + c * .21
            yy = -.34 + r * .32
            if r == 2 and c in (1, 3):
                meter = box((.13, .12, .018),
                            center=desk_point(xx, yy, .07), color=dark)
                meter.turn(axis='+x', degrees=DESK_ANGLE)
                desk.include('desk_meter_%d_%d_%d' % (j, r, c), meter)
            else:
                desk.include('desk_control_%d_%d_%d' % (j, r, c),
                    rod(radius=.028, start=desk_point(xx, yy, .07),
                        end=desk_point(xx, yy, .105),
                        color=red if (j*7+r*5+c) % 19 == 0 else dark))
scene.include('Long operator desk', desk)

small = Asset('Right independent console')
add(small, 'base', (1.50, .88, .78), (SX, SY, .39), (.36, .35, .32))
add(small, 'toe', (1.26, .03, .12), (SX, SY - .46, .08), dark)
sa = math.radians(16)
small_center = (SX, SY, .91)

def small_point(x, y, z):
    return (small_center[0] + x,
            small_center[1] + y*math.cos(sa) - z*math.sin(sa),
            small_center[2] + y*math.sin(sa) + z*math.cos(sa))

top = box((1.54, .92, .08), center=small_center, color=face)
top.turn(axis='+x', degrees=16)
small.include('sloped_top', top)
for r in range(3):
    for c in range(5):
        x, y = -.56 + c*.28, -.27 + r*.27
        small.include('control_%d_%d' % (r, c),
            rod(radius=.026, start=small_point(x, y, .05),
                end=small_point(x, y, .085),
                color=red if (r, c) == (2, 3) else dark))
scene.include('Right independent console', small)

# The separate image of the yellow panel does not establish its exact room
# position. It is placed on the right wall, facing into the room.
grid = Asset('Yellow GRID mimic panel')
GX, GY, GZ = 4.115, -.10, 1.92
add(grid, 'yellow_board', (.07, 1.42, 1.78), (GX, GY, GZ), yellow)
FX = GX - .052

def grid_line(name, a, b, radius=.011):
    grid.include(name, rod(radius=radius,
        start=(FX, GY+a[0], GZ+a[1]),
        end=(FX, GY+b[0], GZ+b[1]), color=black))

grid_line('main_bus', (0, -.78), (0, .78), .014)
for k, z in enumerate((-.49, -.20, .17, .48)):
    grid_line('crossbar_%d' % k, (-.36, z), (.36, z))
for k, y in enumerate((-.36, -.12, .12, .36)):
    grid_line('branch_%d' % k, (y, -.49), (y, .48), .009)
for r, z in enumerate((-.49, -.20, .17, .48)):
    for c, y in enumerate((-.36, -.12, .12, .36)):
        add(grid, 'amber_indicator_%d_%d' % (r, c),
            (.025, .09, .10), (FX-.018, GY+y, GZ+z), amber)
for i, z in enumerate((.64, .37, .10, -.18, -.46)):
    grid.include('red_lamp_%d' % i,
        rod(radius=.055, start=(FX-.01, GY-.55, GZ+z),
            end=(FX-.055, GY-.55, GZ+z), color=red))
for i, z in enumerate((.32, .05, -.22, -.49)):
    grid.include('selector_%d' % i,
        rod(radius=.04, start=(FX-.01, GY+.55, GZ+z),
            end=(FX-.055, GY+.55, GZ+z), color=black))
scene.include('Yellow GRID mimic panel', grid)

ceiling = Asset('Fluorescent ceiling fixtures')
for i, (x, y) in enumerate(((-2, -1.2), (1, -1.2), (-2, 1.2), (1, 1.2))):
    add(ceiling, 'fixture_%d' % i, (1.5, .38, .025),
        (x, y, ROOM_H-.02), face)
scene.include('Fluorescent ceiling fixtures', ceiling)

realize(scene)
sc = bpy.context.scene
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
background.inputs['Color'].default_value = (.72, .70, .66, 1)
background.inputs['Strength'].default_value = .25

# Keep the reference's portrait aspect for both the checks and active camera.
sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100

# Estimated reference locations refer to the photograph expanded to the frame.
# The foreground left corner is uncertain because the photograph crops it.
landmarks = [
    ('bank top left', (-3.99, BACK_Y-.25, 2.70), (.02, .08)),
    ('grille center', (-1.17, BACK_Y-.32, 1.09), (.36, .37)),
    ('desk near left', (DESK_X-DESK_W/2, DESK_Y-DESK_D/2, .80), (.03, .72)),
    ('desk rear right', desk_point(DESK_W/2, .56, .04), (.70, .43)),
    ('door upper', (2.38, BACK_Y-.14, 2.165), (.75, .14)),
    ('small console', (SX, SY, .95), (.88, .49)),
]

def projections(position, target, lens):
    set_view(position, target, lens=lens)
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    out = []
    for _, p, _ in landmarks:
        clip = proj @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
        out.append(None if clip.w <= 1e-8 else
                   (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w)))
    return out

def error(uv, ref):
    if uv is None:
        return 10.0
    return math.hypot(uv[0]-ref[0], uv[1]-ref[1])

baseline = projections(BASE_POSITION, BASE_TARGET, BASE_LENS)
candidate = projections(CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS)
aim_trial = projections(CAMERA_POSITION,
                        (CAMERA_TARGET[0], CAMERA_TARGET[1],
                         CAMERA_TARGET[2] + .10), CAMERA_LENS)
lens_trial = projections(CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS + 1.0)

# Protect the doorway as well as the desk and grille when considering a
# modest lens adjustment. Uncertain cropped corners receive less weight.
weights = (.4, 1.0, .4, 1.0, 1.0, .7)
def score(values):
    return sum(w * error(v, item[2])
               for w, v, item in zip(weights, values, landmarks))

chosen_lens = CAMERA_LENS
if (score(lens_trial) < score(candidate)
        and error(lens_trial[4], landmarks[4][2])
        <= error(candidate[4], landmarks[4][2]) + .025):
    chosen_lens += 1.0
final = projections(CAMERA_POSITION, CAMERA_TARGET, chosen_lens)

print('Landmark | reference | baseline | aim trial | lens trial | final | change')
for item, old, at, lt, new in zip(
        landmarks, baseline, aim_trial, lens_trial, final):
    name, point, ref = item
    def fmt(v):
        return None if v is None else tuple(round(a, 3) for a in v)
    change = 'closer' if error(new, ref) < error(old, ref) else 'farther'
    print(name, ref, fmt(old), fmt(at), fmt(lt), fmt(new), change)

area_emitter((-1.5, -1.0, 2.96), power=400, size=4.5,
             target=(-1, 1.0, 1), color=(1, .95, .88))
area_emitter((2.2, 1.0, 2.95), power=250, size=3,
             target=(1.5, 2.2, 1), color=(1, .96, .90))
area_emitter((-3.5, -3.5, 2.8), power=180, size=3,
             target=(-1, 1, 1), color=(1, .96, .90))
