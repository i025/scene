# Reference inventory and image anchors (normalized x, y; visual estimates):
# - Historic room photograph occupies approximately (0.03, 0.65)-(0.94, 1.00)
#   of the supplied slide. Its back instrument wall spans most of its upper half.
# - Long foreground control desk: approximately (0.03, 0.78)-(0.68, 0.99)
#   within the slide; its top edges converge toward the rear right.
# - Main wall instrument arrays: approximately (0.03, 0.73)-(0.54, 0.86);
#   a dark horizontal ventilation grille interrupts the center.
# - Independent small right console: approximately (0.76, 0.77)-(0.94, 0.91).
# - Tall dark doorway/cabinet is between the main wall and the small console.
# - Yellow GRID panel is shown separately in the reference, at
#   (0.03, 0.19)-(0.52, 0.64). Its precise location in the room is uncertain;
#   it is represented here as a wall-mounted panel on the right side.
# - The photograph crops the foreground desk and floor; hidden room boundaries
#   and the exact wall-to-wall relationship remain uncertain.
# - Dominant edges: horizontal wall panel seams, converging desk edges, and
#   mostly vertical wall seams. The desk occludes the lower instrument wall.
#
# Scene geometry is a plausible reconstruction of the photographed room, not
# a reproduction of the surrounding slide, text, or photographic borders.
# Camera and dimensions are independent parameters below.
#
# Approximate primitive count: architecture 11; main wall and grille 55;
# main desk 100; small console 25; GRID panel 48; ceiling and lights 7.
# Total approximately 246 separate primitives, plus camera and lights.
# All projection reference values below are independent visual estimates.

from sceneact import *
import bpy
import math
from mathutils import Vector

# -------------------- Adjustable scene parameters --------------------
ROOM_W = 8.0
ROOM_D = 6.4
ROOM_H = 3.25
BACK_Y = 2.7
LEFT_X = -4.0
RIGHT_X = 4.0

DESK_X = -0.55
DESK_Y = -0.35
DESK_W = 5.6
DESK_D = 1.75
DESK_H = 0.75
SLOPE_ANGLE = 20.0

CAMERA_POSITION = (7.7, -11.7, 6.3)
CAMERA_TARGET = (0.0, 0.45, 1.22)
CAMERA_LENS = 38.0

# Neutral, aged 1970s palette.
wall = (0.66, 0.65, 0.61)
wall_light = (0.78, 0.77, 0.72)
seam = (0.40, 0.40, 0.38)
floor_color = (0.34, 0.31, 0.28)
metal = (0.62, 0.62, 0.58)
metal_light = (0.77, 0.76, 0.71)
dark = (0.12, 0.13, 0.13)
face = (0.88, 0.86, 0.79)
black = (0.035, 0.038, 0.037)
red = (0.75, 0.06, 0.035)
amber = (1.0, 0.52, 0.025)
yellow = (0.95, 0.68, 0.12)

scene = Scene('1970s Grid Dispatch Room')

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# -------------------- Architecture --------------------
architecture = Asset('Architecture')
add_box(architecture, 'floor', (ROOM_W, ROOM_D, 0.12),
        (0, -0.5, -0.06), floor_color)
add_box(architecture, 'back_wall', (ROOM_W, 0.12, ROOM_H),
        (0, BACK_Y, ROOM_H/2), wall_light)
add_box(architecture, 'left_wall', (0.12, ROOM_D, ROOM_H),
        (LEFT_X, -0.5, ROOM_H/2), wall)
add_box(architecture, 'right_wall', (0.12, ROOM_D, ROOM_H),
        (RIGHT_X, -0.5, ROOM_H/2), wall_light)
add_box(architecture, 'ceiling', (ROOM_W, ROOM_D, 0.10),
        (0, -0.5, ROOM_H + 0.05), wall_light)
add_box(architecture, 'back_baseboard', (ROOM_W, 0.045, 0.16),
        (0, BACK_Y - 0.085, 0.08), seam)
for i, x in enumerate((-3.1, -1.7, -0.3, 1.1, 2.5)):
    add_box(architecture, 'wall_joint_%d' % i, (0.018, 0.025, ROOM_H),
            (x, BACK_Y - 0.075, ROOM_H/2), seam)
scene.include('Architecture', architecture)

# -------------------- Back wall instrument bank --------------------
wall_bank = Asset('Main wall instrument bank')
add_box(wall_bank, 'backing', (5.55, 0.16, 1.72),
        (-1.05, BACK_Y - 0.16, 1.45), metal)
# Large cabinet divisions remain visible behind the instruments.
for i, x in enumerate((-3.72, -2.62, -1.52, -0.42, 0.68, 1.68)):
    add_box(wall_bank, 'cabinet_seam_%d' % i, (0.025, 0.03, 1.72),
            (x, BACK_Y - 0.255, 1.45), seam)

# Uniform square indicators distributed around the central ventilation panel.
for col in range(12):
    x = -3.53 + col * 0.43
    for row in range(3):
        z = 0.96 + row * 0.41
        if 4 <= col <= 7:
            continue
        add_box(wall_bank, 'instrument_frame_%02d_%d' % (col, row),
                (0.32, 0.055, 0.32), (x, BACK_Y - 0.29, z), dark)
        add_box(wall_bank, 'instrument_face_%02d_%d' % (col, row),
                (0.24, 0.02, 0.24), (x, BACK_Y - 0.325, z), face)
        # A dark needle gives the square face a recognizable instrument reading.
        needle = box((0.012, 0.012, 0.105),
                     center=(x, BACK_Y - 0.341, z), color=dark)
        needle.turn(axis='+y', degrees=(col * 17 + row * 29) % 80 - 40)
        wall_bank.include('needle_%02d_%d' % (col, row), needle)

# Wide dark louvred ventilation opening.
add_box(wall_bank, 'vent_dark_recess', (1.64, 0.04, 0.79),
        (-1.16, BACK_Y - 0.29, 1.38), dark)
for i in range(6):
    add_box(wall_bank, 'vent_slat_%d' % i, (1.54, 0.025, 0.035),
            (-1.16, BACK_Y - 0.32, 1.09 + i * 0.115), metal_light)
scene.include('Main wall instrument bank', wall_bank)

# A narrow dark vertical feature seen beyond the main bank.
door = Asset('Rear doorway and cabinet')
add_box(door, 'dark_opening', (0.70, 0.055, 2.18),
        (2.46, BACK_Y - 0.09, 1.18), dark)
add_box(door, 'inner_panel', (0.51, 0.04, 1.86),
        (2.46, BACK_Y - 0.13, 1.18), (0.30, 0.29, 0.27))
add_box(door, 'upper_glazing', (0.40, 0.025, 0.65),
        (2.46, BACK_Y - 0.16, 1.70), (0.43, 0.44, 0.42))
scene.include('Rear doorway and cabinet', door)

# -------------------- Long sloping desk --------------------
desk = Asset('Long sloping operator desk')
add_box(desk, 'pedestal', (DESK_W, DESK_D - 0.12, DESK_H),
        (DESK_X, DESK_Y, DESK_H/2), (0.35, 0.34, 0.31))
add_box(desk, 'front_fascia', (DESK_W, 0.08, 0.63),
        (DESK_X, DESK_Y - DESK_D/2 + 0.02, 0.37), metal)
add_box(desk, 'writing_ledge', (DESK_W + 0.12, 0.47, 0.09),
        (DESK_X, DESK_Y - 0.66, DESK_H + 0.035), metal_light)
for i in range(6):
    x = DESK_X - DESK_W/2 + i * DESK_W/5
    add_box(desk, 'front_division_%d' % i, (0.022, 0.025, 0.57),
            (x, DESK_Y - DESK_D/2 - 0.03, 0.38), seam)

# Desk panel tilts upward toward the back. Local coordinates are transformed
# about the panel center so controls remain attached to the actual surface.
panel_center = (DESK_X, DESK_Y + 0.20, 1.02)
angle = math.radians(SLOPE_ANGLE)
def desk_point(x, local_y, local_z=0.0):
    return (panel_center[0] + x,
            panel_center[1] + local_y * math.cos(angle) - local_z * math.sin(angle),
            panel_center[2] + local_y * math.sin(angle) + local_z * math.cos(angle))

panel = box((DESK_W, 1.15, 0.09), center=panel_center, color=metal_light)
panel.turn(axis='+x', degrees=SLOPE_ANGLE)
desk.include('inclined_control_surface', panel)

# Separate inset face plates establish the broad panel divisions.
for j in range(5):
    x = -DESK_W/2 + 0.57 + j * 1.12
    plate = box((1.03, 0.96, 0.018), center=desk_point(x, 0, 0.057), color=face)
    plate.turn(axis='+x', degrees=SLOPE_ANGLE)
    desk.include('sloped_face_plate_%d' % j, plate)
    # Rows of knobs and meters: geometry is kept large enough to read.
    for r in range(3):
        for c in range(4):
            px = x - 0.36 + c * 0.24
            py = -0.31 + r * 0.29
            if r == 2 and c in (1, 2):
                part = box((0.13, 0.13, 0.018),
                           center=desk_point(px, py, 0.078), color=dark)
                part.turn(axis='+x', degrees=SLOPE_ANGLE)
            else:
                p0 = desk_point(px, py, 0.076)
                p1 = desk_point(px, py, 0.115)
                part = rod(radius=0.034, start=p0, end=p1,
                           color=black if (r+c+j) % 4 else red)
            desk.include('control_%d_%d_%d' % (j, r, c), part)
scene.include('Long sloping operator desk', desk)

# -------------------- Independent right-hand console --------------------
small = Asset('Right independent console')
add_box(small, 'base', (1.55, 0.95, 0.78), (2.85, 1.45, 0.39), metal)
add_box(small, 'toe_recess', (1.30, 0.05, 0.14),
        (2.85, 0.955, 0.10), dark)
small_center = (2.85, 1.48, 0.92)
small_angle = math.radians(18)
def small_point(x, y, z):
    return (small_center[0] + x,
            small_center[1] + y*math.cos(small_angle) - z*math.sin(small_angle),
            small_center[2] + y*math.sin(small_angle) + z*math.cos(small_angle))
s = box((1.58, 0.96, 0.08), center=small_center, color=metal_light)
s.turn(axis='+x', degrees=18)
small.include('sloped_top', s)
for row in range(3):
    for col in range(5):
        x = -0.58 + col * 0.29
        y = -0.30 + row * 0.28
        small.include('control_%d_%d' % (row, col),
            rod(radius=0.029, start=small_point(x, y, 0.05),
                end=small_point(x, y, 0.09),
                color=red if (row == 2 and col == 3) else dark))
scene.include('Right independent console', small)

# -------------------- Yellow GRID single-line diagram --------------------
# The slide shows this panel separately, so its mounting point is interpretive.
grid = Asset('Yellow GRID single line mimic panel')
gx, gy, gz = 3.925, -0.15, 1.90
add_box(grid, 'yellow_board', (0.07, 1.50, 1.85),
        (gx, gy, gz), yellow)
# Panel face is the plane x = 3.88, facing into the room.
front_x = gx - 0.047
# Vertical and horizontal single-line conductors, arranged in a circuit network.
def grid_line(name, a, b, width=0.022):
    grid.include(name, rod(radius=width/2,
                           start=(front_x, gy+a[0], gz+a[1]),
                           end=(front_x, gy+b[0], gz+b[1]), color=black))
grid_line('main_vertical', (0.02, -0.78), (0.02, 0.78), 0.026)
for k, z in enumerate((-0.48, -0.19, 0.17, 0.47)):
    grid_line('crossbar_%d' % k, (-0.40, z), (0.38, z), 0.022)
for k, y in enumerate((-0.36, -0.12, 0.16, 0.37)):
    grid_line('branch_%d' % k, (y, -0.48), (y, 0.47), 0.018)
for row, z in enumerate((-0.48, -0.19, 0.17, 0.47)):
    for col, y in enumerate((-0.36, -0.12, 0.16, 0.37)):
        add_box(grid, 'amber_indicator_%d_%d' % (row, col),
                (0.023, 0.095, 0.105), (front_x-0.018, gy+y, gz+z), amber)
# Red signal lights and black selector switches.
for i, (y, z) in enumerate(((-0.56,0.65),(-0.56,0.36),(-0.56,0.07),
                             (-0.56,-0.23),(-0.56,-0.55),(0.57,0.60))):
    grid.include('red_signal_%d' % i,
        rod(radius=0.065, start=(front_x-0.015, gy+y, gz+z),
            end=(front_x-0.06, gy+y, gz+z), color=red))
for i, z in enumerate((0.32, 0.05, -0.22, -0.49)):
    grid.include('selector_%d' % i,
        rod(radius=0.045, start=(front_x-0.02, gy+0.58, gz+z),
            end=(front_x-0.065, gy+0.58, gz+z), color=black))
scene.include('Yellow GRID mimic panel', grid)

# -------------------- Ceiling fluorescent troffers --------------------
ceiling = Asset('Ceiling fluorescent troffers')
for i, (x, y) in enumerate(((-2.2, -1.1), (0.0, -1.1), (2.2, -1.1),
                             (-2.2, 1.2), (0.0, 1.2), (2.2, 1.2))):
    add_box(ceiling, 'troffer_%d' % i, (1.45, 0.43, 0.035),
            (x, y, ROOM_H - 0.035), face)
scene.include('Ceiling fluorescent troffers', ceiling)

# -------------------- Realize, camera, lighting --------------------
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
background.inputs['Color'].default_value = (0.72, 0.70, 0.66, 1)
background.inputs['Strength'].default_value = 0.5

# Preserve the original supplied image's portrait aspect.
sc.render.resolution_x = 374
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)

area_emitter((0, -2.5, 3.05), power=850, size=5,
             target=(0, 0.7, 0.8), color=(1.0, 0.94, 0.84))
area_emitter((-3, 0.2, 2.9), power=450, size=3,
             target=(-1, 1.5, 1), color=(1.0, 0.96, 0.89))
area_emitter((2.8, 0.0, 2.9), power=350, size=2.5,
             target=(2.5, 1.6, 1), color=(1.0, 0.95, 0.86))

# The landmark estimates refer to a room-filling reconstruction of the room
# photograph, rather than coordinates of the photograph within the title slide.
# These checks report only point projections; they do not establish visibility.
landmarks = [
    ('back wall upper left', (-3.72, BACK_Y-0.29, 2.31), (0.08, 0.30)),
    ('vent center', (-1.16, BACK_Y-0.32, 1.38), (0.39, 0.52)),
    ('desk front left', (DESK_X-DESK_W/2, DESK_Y-DESK_D/2, DESK_H), (0.06, 0.82)),
    ('desk rear right', (DESK_X+DESK_W/2, DESK_Y+0.75, 1.20), (0.72, 0.58)),
    ('small console top', (2.85, 1.48, 0.96), (0.84, 0.54)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print('Landmark                         reference        projected')
for name, p, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5*(clip.x/clip.w + 1), 0.5*(1 - clip.y/clip.w))
    print('%-31s %s %s' % (name, ref, None if uv is None else
                           (round(uv[0], 3), round(uv[1], 3))))
