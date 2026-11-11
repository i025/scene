import bpy
import math
from mathutils import Vector
from sceneact import *

# Reference inventory and visual anchors, estimated in normalized image coordinates:
# - Warehouse storage rack fills the left and lower image, roughly (0, .13) to
#   (1, 1); dark horizontal shelves recede toward the lower right.
# - Near upright is visible from approximately (.02, .92) to (.20, .11).
#   Its braces and shelves overlap large wrapped pallets at the left.
# - Large pale wrapped pallet: approximately (.05, .55) to (.29, .84);
#   another pale pallet is centered near (.42, .66).
# - Corrugated roof covers most of the upper and right image. A rectangular
#   skylight lies near (.71, .25), with dark grid lines.
# - White strip lights cross the upper image along a down-right diagonal:
#   approximately (.38, .03), (.53, .20), (.68, .40), (.79, .54), (.86, .63).
# - Beams and rack edges converge toward the lower-right background. The
#   foreground rack partly hides the ceiling; rack contents beyond it are
#   uncertain and represented as simple cartons and pallets.
#
# Approximate primitive budget: architecture 60, rack frames and braces 85,
# pallets and cartons 70, light fixtures and skylight 25, total about 240.
# The camera and the major dimensions are independent parameters.

scene = Scene('Warehouse')

# Camera and principal scene dimensions.
CAMERA_POS = (1.15, -8.8, 1.25)
CAMERA_TARGET = (-0.45, 2.5, 7.1)
CAMERA_LENS = 22
ROOF_Z = 8.2
RACK_X0 = -4.3
RACK_X1 = -0.9
RACK_Y0 = -5.5
RACK_Y1 = 19.0

# Restrained palette, approximating the warm industrial lighting.
roof_col = (0.24, 0.22, 0.145)
roof_alt = (0.31, 0.285, 0.19)
beam_col = (0.19, 0.18, 0.13)
steel_col = (0.25, 0.255, 0.22)
steel_light = (0.38, 0.37, 0.29)
shelf_col = (0.18, 0.16, 0.11)
pallet_col = (0.43, 0.29, 0.10)
cardboard = (0.52, 0.38, 0.19)
cardboard_light = (0.67, 0.56, 0.35)
wrap_col = (0.62, 0.60, 0.47)
wrap_light = (0.73, 0.71, 0.58)

architecture = Asset('Warehouse architecture')
architecture.include('roof_surface', box((19, 36, .16),
    center=(0, 5, ROOF_Z + .12), color=roof_col))
architecture.include('far_wall', box((19, .18, 8.2),
    center=(0, 20.5, 4.1), color=(.31, .30, .22)))
architecture.include('floor', box((19, 36, .12),
    center=(0, 5, -.12), color=(.24, .23, .18)))

# Roof corrugation runs along the depth of the building.
for i in range(35):
    x = -8.5 + i * .5
    architecture.include('roof_rib_%02d' % i,
        box((.055, 36, .065), center=(x, 5, ROOF_Z-.015),
            color=roof_alt if i % 2 else beam_col))
# Broad transverse structural purlins.
for i, y in enumerate((-7, -3, 1, 5, 9, 13, 17, 21)):
    architecture.include('roof_crossbeam_%d' % i,
        box((19, .17, .26), center=(0, y, ROOF_Z-.20), color=beam_col))
scene.include('architecture', architecture)

# A bright glazed roof panel, with an explicit dark metal grid. It is placed
# slightly below the roof so it is visible from inside.
skylight = Asset('Rectangular skylight')
sky_x, sky_y = 2.15, 2.0
skylight.include('glazing', box((2.1, 2.8, .035),
    center=(sky_x, sky_y, ROOF_Z-.095), color=(.78, .83, .75)))
for dx in (-1.08, 1.08):
    skylight.include('side_frame_%s' % dx,
        box((.10, 2.95, .09), center=(sky_x+dx, sky_y, ROOF_Z-.16),
            color=beam_col))
for dy in (-1.45, 1.45):
    skylight.include('end_frame_%s' % dy,
        box((2.25, .10, .09), center=(sky_x, sky_y+dy, ROOF_Z-.16),
            color=beam_col))
for i in range(1, 6):
    skylight.include('grid_long_%d' % i,
        box((.035, 2.8, .045),
            center=(sky_x-1.05+i*.35, sky_y, ROOF_Z-.17), color=beam_col))
for i in range(1, 8):
    skylight.include('grid_cross_%d' % i,
        box((2.1, .035, .045),
            center=(sky_x, sky_y-1.4+i*.35, ROOF_Z-.17), color=beam_col))
scene.include('skylight', skylight)

# Long suspended fluorescent fittings, broken into the visible separate lamps.
lights_asset = Asset('Suspended fluorescent fittings')
for i, y in enumerate((-6.0, -1.8, 2.4, 6.6, 10.8, 15.0)):
    x = .35
    lights_asset.include('fixture_body_%d' % i,
        box((.23, 2.75, .11), center=(x, y, ROOF_Z-.32),
            color=(.34, .33, .26)))
    lights_asset.include('luminous_strip_%d' % i,
        box((.16, 2.55, .055), center=(x, y, ROOF_Z-.39),
            color=(1.0, .93, .64)))
scene.include('ceiling_lights', lights_asset)

# Heavy industrial storage rack: near and far uprights with shelf beams,
# depth crosspieces, and a few diagonal braces. The frame recedes along Y.
rack = Asset('Tall pallet rack')
upright_y = [-5.4, -1.4, 2.6, 6.6, 10.6, 14.6, 18.6]
levels = [1.45, 3.10, 4.75, 6.40]
for j, y in enumerate(upright_y):
    for side, x in [('outer', RACK_X0), ('aisle', RACK_X1)]:
        rack.include('%s_upright_%d' % (side, j),
            box((.14, .14, 7.7), center=(x, y, 3.85), color=steel_light))
    for k, z in enumerate((1.4, 3.05, 4.7, 6.35)):
        rack.include('depth_beam_%d_%d' % (j, k),
            box((3.5, .11, .12), center=((RACK_X0+RACK_X1)/2, y, z),
                color=steel_col))
    for k, z in enumerate((1.9, 4.2)):
        rack.include('frame_diagonal_%d_%d' % (j, k),
            rod(.045, start=(RACK_X0, y, z-.6),
                end=(RACK_X1, y, z+.6), color=steel_col))
for k, z in enumerate(levels):
    for side, x in [('outer', RACK_X0), ('aisle', RACK_X1)]:
        rack.include('%s_long_beam_%d' % (side, k),
            box((.15, RACK_Y1-RACK_Y0, .18),
                center=(x, (RACK_Y0+RACK_Y1)/2, z), color=shelf_col))
    rack.include('shelf_deck_%d' % k,
        box((3.25, RACK_Y1-RACK_Y0, .07),
            center=((RACK_X0+RACK_X1)/2, (RACK_Y0+RACK_Y1)/2, z+.02),
            color=(.20, .19, .15)))
scene.include('rack_structure', rack)

# Pallet loads are distinct editable assemblies. Their varied heights and
# positions leave visible black gaps between the shelves and packages.
loads = Asset('Stored pallet loads')

def add_load(name, x, y, shelf_z, w, d, h, color, wrapped=False):
    a = Asset(name)
    a.include('wooden_pallet', box((w+.12, d+.12, .14),
        center=(x, y, shelf_z+.13), color=pallet_col))
    # Two visible feet give the pallet its characteristic open base.
    for idx, yy in enumerate((y-d*.32, y+d*.32)):
        a.include('pallet_foot_%d' % idx,
            box((w+.1, .11, .10), center=(x, yy, shelf_z+.055),
                color=(.31, .20, .07)))
    a.include('main_load', box((w, d, h),
        center=(x, y, shelf_z+.20+h/2), color=color))
    if wrapped:
        # A handful of broad wrap seams, rather than sub-pixel striping.
        for i in range(3):
            z = shelf_z+.20+h*(.23+i*.25)
            a.include('wrap_band_%d' % i,
                box((w+.012, d+.012, .035), center=(x, y, z),
                    color=wrap_light))
        a.include('vertical_wrap_seam',
            box((.035, d+.02, h*.94),
                center=(x+w*.18, y, shelf_z+.20+h*.5), color=wrap_light))
    else:
        a.include('carton_seam', box((.025, d+.015, h*.96),
            center=(x, y, shelf_z+.20+h*.5), color=(.39, .29, .15)))
    loads.include(name, a)

# Large foreground loads and smaller loads further down the aisle.
add_load('foreground_wrapped_load', -2.50, -4.2, 3.20, 2.35, 2.35, 1.45, wrap_col, True)
add_load('foreground_lower_cartons', -2.60, -4.2, 1.55, 2.45, 2.3, 1.12, cardboard_light)
add_load('upper_foreground_carton', -2.65, -4.0, 6.50, 2.3, 2.35, 1.18, cardboard_light)
add_load('middle_wrapped_pallet', -2.55, -.25, 4.85, 2.25, 2.15, 1.16, wrap_light, True)
add_load('middle_lower_box', -2.60, -.20, 1.55, 2.30, 2.2, 1.05, cardboard)
add_load('middle_box', -2.60, 3.4, 3.20, 2.20, 2.15, 1.12, cardboard_light)
add_load('middle_upper_box', -2.65, 4.0, 6.50, 2.20, 2.1, 1.0, cardboard)
add_load('distant_wrapped', -2.55, 7.5, 4.85, 2.20, 2.0, 1.05, wrap_col, True)
add_load('distant_carton_a', -2.6, 8.0, 1.55, 2.2, 1.9, 1.0, cardboard_light)
add_load('distant_carton_b', -2.6, 11.8, 3.20, 2.2, 1.9, 1.0, cardboard)
add_load('distant_carton_c', -2.6, 15.8, 4.85, 2.1, 1.8, .9, cardboard_light)
add_load('distant_carton_d', -2.6, 17.5, 1.55, 2.1, 1.8, 1.0, wrap_col)
scene.include('pallet_loads', loads)

realize(scene)

# Ensure a world exists after SceneAct clears the Blender scene.
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
background.inputs['Color'].default_value = (.34, .29, .18, 1)
background.inputs['Strength'].default_value = .38

set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -2, 7.6), power=900, size=5,
             target=(-2, -1, 3), color=(1.0, .78, .43))
area_emitter((1, 7, 7.6), power=1200, size=6,
             target=(-2, 7, 3), color=(1.0, .84, .56))
area_emitter((3, 2, 7.7), power=700, size=4,
             target=(0, 1, 4), color=(.85, .9, .77))

# Bright fittings and glazing remain visibly luminous.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if 'luminous_strip' in obj.name or 'glazing' in obj.name:
        mat = bpy.data.materials.new('Light surface ' + obj.name)
        mat.diffuse_color = (1.0, .96, .76, 1)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (1.0, .96, .80, 1)
                bsdf.inputs['Emission Strength'].default_value = 3.0
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = (1.0, .96, .80, 1)
        obj.data.materials.clear()
        obj.data.materials.append(mat)

sc.view_settings.view_transform = 'AgX'
