import bpy
import math
from sceneact import *

# Reference inventory and approximate normalized image anchors:
# - Tall pallet rack fills the left edge and lower image. Its near upright
#   runs from roughly (.02, .94) to (.20, .12); shelf edges descend right.
# - A large wrapped foreground load occupies about (.04, .56)-(.29, .84);
#   another pale load appears near (.37, .59)-(.52, .75).
# - Dark shelf gaps, steel framing, yellow pallets and cartons overlap behind
#   those loads and continue toward the bottom-right corner. Distant contents
#   and the portions hidden behind the rack are uncertain.
# - Corrugated roof fills the upper and right image. The bright gridded
#   skylight occupies approximately (.60, .20)-(.83, .37).
# - Strip lights follow a down-right diagonal from about (.37, 0) toward
#   (.87, .65); broad roof beams cross that direction.
#
# Comparison with the second render, ranked by visible extent and contrast:
# 1. The reference rack and its loads reach across almost the entire bottom;
#    the render has a blank wall across roughly (.60, .76)-(1, 1). Turning
#    CAMERA_TARGET_X left and extending the occupied rack toward the aisle
#    should move its receding silhouette right and cover more of that region.
# 2. The rendered lamp line runs approximately (.40, 0) to (.61, .80),
#    steeper than the reference line from (.37, 0) to (.87, .65). CAMERA_ROLL
#    rotates the composition so the lights and shelf edges descend further
#    right. The rack uprights will also rotate, as they do in the reference.
# 3. The rendered skylight is about (.58, .37)-(.80, .51), below the reference
#    skylight. Moving SKYLIGHT_Y closer predicts an upward shift; its bright
#    grid and roof overlap are retained.
# 4. The foreground render contains pale, sparse shelves, while the
#    reference has a prominent wrapped load, dark gaps, yellow pallet edges,
#    and more loaded levels. LOAD_X and the foreground loads move visible
#    packages toward the aisle and increase their foreground coverage.
#    Brightness depends on lighting and face orientation as well as material.
#
# Expanded primitive estimate: architecture 47, skylight 18, lamps 14,
# rack about 120, loads about 120, totaling roughly 319 boxes and rods.

scene = Scene('Warehouse')

# Camera parameters are independent of asset dimensions and positions.
CAMERA_POS = (1.15, -8.8, 1.25)
CAMERA_TARGET_X = -1.30
CAMERA_TARGET = (CAMERA_TARGET_X, 2.5, 10.7)
CAMERA_LENS = 22
CAMERA_ROLL = -0.22

ROOF_Z = 8.2
RACK_X0, RACK_X1 = -4.3, -0.9
RACK_Y0, RACK_Y1 = -7.5, 23.0
SKYLIGHT_X, SKYLIGHT_Y = 2.15, -4.0
LOAD_X = -1.95

roof_col = (.24, .22, .145)
roof_alt = (.31, .285, .19)
beam_col = (.15, .145, .10)
steel_col = (.23, .235, .20)
steel_light = (.36, .35, .27)
shelf_col = (.13, .12, .085)
pallet_col = (.44, .28, .075)
cardboard = (.53, .38, .18)
cardboard_light = (.68, .55, .31)
wrap_col = (.61, .59, .46)
wrap_light = (.76, .72, .58)
lamp_color = (1.0, .93, .64)
glass_color = (.78, .83, .75)

architecture = Asset('Warehouse architecture')
architecture.include('roof_surface', box(
    (19, 42, .16), center=(0, 5, ROOF_Z + .12), color=roof_col))
architecture.include('far_wall', box(
    (19, .18, 8.2), center=(0, 24.5, 4.1), color=(.31, .30, .22)))
architecture.include('floor', box(
    (19, 42, .12), center=(0, 5, -.12), color=(.24, .23, .18)))

for i in range(35):
    x = -8.5 + i * .5
    architecture.include('roof_rib_%02d' % i, box(
        (.055, 42, .065), center=(x, 5, ROOF_Z-.015),
        color=roof_alt if i % 2 else beam_col))
for i, y in enumerate((-7, -3, 1, 5, 9, 13, 17, 21)):
    architecture.include('roof_crossbeam_%d' % i, box(
        (19, .17, .26), center=(0, y, ROOF_Z-.20), color=beam_col))
scene.include('architecture', architecture)

skylight = Asset('Rectangular skylight')
skylight.include('glazing', box(
    (2.1, 2.8, .035), center=(SKYLIGHT_X, SKYLIGHT_Y, ROOF_Z-.095),
    color=glass_color))
for i, dx in enumerate((-1.08, 1.08)):
    skylight.include('side_frame_%d' % i, box(
        (.10, 2.95, .09), center=(SKYLIGHT_X+dx, SKYLIGHT_Y, ROOF_Z-.16),
        color=beam_col))
for i, dy in enumerate((-1.45, 1.45)):
    skylight.include('end_frame_%d' % i, box(
        (2.25, .10, .09), center=(SKYLIGHT_X, SKYLIGHT_Y+dy, ROOF_Z-.16),
        color=beam_col))
for i in range(1, 6):
    skylight.include('grid_long_%d' % i, box(
        (.035, 2.8, .045),
        center=(SKYLIGHT_X-1.05+i*.35, SKYLIGHT_Y, ROOF_Z-.17),
        color=beam_col))
for i in range(1, 8):
    skylight.include('grid_cross_%d' % i, box(
        (2.1, .035, .045),
        center=(SKYLIGHT_X, SKYLIGHT_Y-1.4+i*.35, ROOF_Z-.17),
        color=beam_col))
scene.include('skylight', skylight)

fixtures = Asset('Suspended fluorescent fittings')
for i, y in enumerate((-8.0, -4.0, 0, 4.0, 8.0, 12.0, 16.0)):
    fixtures.include('fixture_body_%d' % i, box(
        (.24, 2.8, .11), center=(.35, y, ROOF_Z-.32),
        color=(.34, .33, .26)))
    fixtures.include('luminous_strip_%d' % i, box(
        (.18, 2.6, .055), center=(.35, y, ROOF_Z-.40),
        color=lamp_color))
scene.include('ceiling_lights', fixtures)

rack = Asset('Tall pallet rack')
upright_y = [-7.4, -3.4, .6, 4.6, 8.6, 12.6, 16.6, 20.6]
levels = [1.45, 3.10, 4.75, 6.40]
for j, y in enumerate(upright_y):
    for side, x in [('outer', RACK_X0), ('aisle', RACK_X1)]:
        rack.include('%s_upright_%d' % (side, j), box(
            (.14, .14, 7.7), center=(x, y, 3.85), color=steel_light))
    for k, z in enumerate(levels):
        rack.include('depth_beam_%d_%d' % (j, k), box(
            (3.5, .11, .12),
            center=((RACK_X0+RACK_X1)/2, y, z), color=steel_col))
    for k, z in enumerate((1.9, 4.2, 6.3)):
        rack.include('frame_diagonal_%d_%d' % (j, k), rod(
            .035, start=(RACK_X0, y, z-.6),
            end=(RACK_X1, y, z+.6), color=steel_col))
for k, z in enumerate(levels):
    for side, x in [('outer', RACK_X0), ('aisle', RACK_X1)]:
        rack.include('%s_long_beam_%d' % (side, k), box(
            (.15, RACK_Y1-RACK_Y0, .18),
            center=(x, (RACK_Y0+RACK_Y1)/2, z), color=shelf_col))
    for j in range(15):
        y = -6.5 + 2*j
        rack.include('deck_cross_%d_%d' % (k, j), box(
            (3.25, .09, .07),
            center=((RACK_X0+RACK_X1)/2, y, z+.02), color=shelf_col))
scene.include('rack_structure', rack)

loads = Asset('Stored pallet loads')

def add_load(name, x, y, shelf_z, w, d, h, color, wrapped=False):
    load = Asset(name)
    load.include('wooden_pallet', box(
        (w+.12, d+.12, .14), center=(x, y, shelf_z+.13),
        color=pallet_col))
    for idx, yy in enumerate((y-d*.32, y+d*.32)):
        load.include('pallet_foot_%d' % idx, box(
            (w+.1, .11, .10), center=(x, yy, shelf_z+.055),
            color=(.31, .20, .07)))
    load.include('main_load', box(
        (w, d, h), center=(x, y, shelf_z+.20+h/2), color=color))
    if wrapped:
        for i in range(4):
            z = shelf_z+.20+h*(.16+i*.21)
            load.include('wrap_band_%d' % i, box(
                (w+.012, d+.012, .025), center=(x, y, z),
                color=wrap_light))
        load.include('vertical_wrap_seam', box(
            (.025, d+.02, h*.94),
            center=(x+w*.18, y, shelf_z+.20+h*.5), color=wrap_light))
    else:
        load.include('carton_seam', box(
            (.025, d+.015, h*.96),
            center=(x, y, shelf_z+.20+h*.5), color=(.39, .29, .15)))
    loads.include(name, load)

add_load('foreground_wrapped_load', LOAD_X, -6.1, 3.20,
         2.0, 2.35, 1.45, wrap_col, True)
add_load('foreground_lower_cartons', LOAD_X, -6.1, 1.55,
         2.0, 2.3, 1.12, cardboard_light)
add_load('foreground_middle_cartons', LOAD_X, -6.1, 4.85,
         2.0, 2.3, 1.12, cardboard_light)
add_load('upper_foreground_carton', LOAD_X, -6.0, 6.50,
         2.0, 2.35, 1.18, cardboard_light)
add_load('middle_wrapped_pallet', LOAD_X, -2.25, 4.85,
         2.0, 2.15, 1.16, wrap_light, True)
add_load('middle_lower_box', LOAD_X, -2.2, 1.55,
         2.0, 2.2, 1.05, cardboard)
add_load('middle_box_near', LOAD_X, -2.2, 3.20,
         2.0, 2.15, 1.12, cardboard_light)
add_load('middle_box', LOAD_X, 1.4, 3.20,
         2.0, 2.15, 1.12, cardboard_light)
add_load('middle_upper_box', LOAD_X, 2.0, 6.50,
         2.0, 2.1, 1.0, cardboard)
add_load('distant_wrapped', LOAD_X, 5.5, 4.85,
         2.0, 2.0, 1.05, wrap_col, True)
add_load('distant_carton_a', LOAD_X, 6.0, 1.55,
         2.0, 1.9, 1.0, cardboard_light)
add_load('distant_carton_b', LOAD_X, 9.8, 3.20,
         2.0, 1.9, 1.0, cardboard)
add_load('distant_carton_c', LOAD_X, 13.8, 4.85,
         2.0, 1.8, .9, cardboard_light)
add_load('distant_carton_d', LOAD_X, 17.5, 1.55,
         2.0, 1.8, 1.0, wrap_col)
add_load('distant_carton_e', LOAD_X, 18.5, 3.20,
         2.0, 1.8, 1.0, cardboard_light)
scene.include('pallet_loads', loads)

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
sc.world.node_tree.links.new(background.outputs['Background'],
                             output.inputs['Surface'])
background.inputs['Color'].default_value = (.34, .29, .18, 1)
background.inputs['Strength'].default_value = .38

set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
# Rotate about the camera's own viewing axis.
from mathutils import Quaternion
camera = sc.camera
camera.rotation_mode = 'QUATERNION'
camera.rotation_quaternion = camera.rotation_quaternion @ Quaternion(
    (0, 0, 1), CAMERA_ROLL)

area_emitter((0, -2, 7.6), power=1100, size=5,
             target=(-2, -1, 3), color=(1.0, .78, .43))
area_emitter((1, 7, 7.6), power=1200, size=6,
             target=(-2, 7, 3), color=(1.0, .84, .56))
area_emitter((3, -2, 7.7), power=800, size=4,
             target=(0, 1, 4), color=(.85, .9, .77))

for mat in bpy.data.materials:
    c = mat.diffuse_color
    is_lamp = all(abs(c[i] - lamp_color[i]) < .015 for i in range(3))
    is_glass = all(abs(c[i] - glass_color[i]) < .015 for i in range(3))
    if not (is_lamp or is_glass):
        continue
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        emission = bsdf.inputs.get('Emission Color')
        if emission is None:
            emission = bsdf.inputs.get('Emission')
        if emission is not None:
            emission.default_value = (1.0, .97, .82, 1)
        strength = bsdf.inputs.get('Emission Strength')
        if strength is not None:
            strength.default_value = 4.0 if is_lamp else 2.5

sc.view_settings.view_transform = 'AgX'
