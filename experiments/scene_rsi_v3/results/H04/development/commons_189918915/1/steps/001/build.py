import bpy
import math
import random
from mathutils import Vector
from sceneact import *

# Reference inventory and visual anchors, estimated in normalized image coordinates:
# - Left storage rack: x 0.00–0.68, y 0.08–1.00; tall perforated uprights,
#   dark horizontal shelves and diagonal braces. Its shelves converge toward lower right.
# - Wrapped pallets and cardboard cartons: x 0.00–0.73, y 0.00–1.00, interrupted
#   by large black openings between shelves. Foreground loads overlap rack beams.
# - A narrow continuation of storage at right: x 0.80–1.00, y 0.04–1.00.
# - Corrugated ceiling: x 0.05–1.00, y 0.00–0.78, crossed by dark structural beams.
# - Skylight: approximately x 0.59–0.84, y 0.20–0.39, with a dark grid.
# - Long bright fluorescent fixtures: diagonal bands from upper left toward lower right;
#   largest visible segments around (0.39,0.05), (0.54,0.23), (0.69,0.42),
#   (0.79,0.55), and (0.86,0.65).
# - Floor and lower portions of the warehouse are outside the frame. The distant rack
#   contents and exact roof construction are uncertain and represented schematically.
# Dominant edges run diagonally down-right in the image; upright rack posts rise from
# lower-left toward upper-right. The storage structure occludes the ceiling.
#
# Expanded primitive estimate: roof and beams ~35, skylight ~15, lamps ~18,
# racks and braces ~95, pallets and loads ~85, for approximately 250 primitives.
# Each box or rod below is one SceneAct primitive.

random.seed(7)
scene = Scene("Warehouse aisle")

# Major dimensions and camera parameters are kept independent for revision.
aisle_half_width = 2.25
rack_depth = 1.50
rack_length = 25.0
roof_z = 9.7
camera_position = (0.25, -8.4, 1.35)
camera_target = (0.15, 1.8, 8.7)
camera_lens = 29

steel = (0.23, 0.22, 0.16)
steel_edge = (0.37, 0.34, 0.24)
beam_color = (0.31, 0.28, 0.20)
roof_color = (0.29, 0.28, 0.21)
roof_rib = (0.20, 0.20, 0.16)
wood = (0.48, 0.31, 0.10)
wood_light = (0.62, 0.43, 0.17)
carton_colors = [(0.60, 0.48, 0.28), (0.69, 0.58, 0.37),
                 (0.49, 0.40, 0.25), (0.75, 0.66, 0.46)]
wrap_colors = [(0.69, 0.66, 0.52), (0.55, 0.54, 0.46),
               (0.78, 0.75, 0.62)]
dark = (0.095, 0.10, 0.085)

architecture = Asset("warehouse_architecture")
architecture.include("roof_surface", box((14, 36, .16), center=(0, 3, roof_z),
                                         color=roof_color))
# Long roof seams emphasize the perspective of the corrugated metal.
for i in range(26):
    x = -6.5 + i * .52
    architecture.include("roof_seam_%02d" % i,
        box((.035, 35, .07), center=(x, 3, roof_z-.12), color=roof_rib))
for i, y in enumerate([-10, -5, 0, 5, 10, 15, 20]):
    architecture.include("transverse_roof_girder_%d" % i,
        box((13, .20, .34), center=(0, y, roof_z-.30), color=beam_color))
scene.include("architecture", architecture)

# Ceiling window is a luminous inset panel with a visible metal grid. Its dark
# border hides the simplified junction with the opaque roof sheet.
skylight = Asset("ceiling_skylight")
sky_x, sky_y = 1.05, 2.25
skylight.include("bright_glazing", box((2.0, 2.5, .06),
    center=(sky_x, sky_y, roof_z-.12), color=(0.79, 0.83, 0.73)))
for x in (sky_x-1, sky_x+1):
    skylight.include("long_border_%s" % x, box((.09, 2.6, .11),
        center=(x, sky_y, roof_z-.18), color=dark))
for y in (sky_y-1.25, sky_y+1.25):
    skylight.include("short_border_%s" % y, box((2.1, .09, .11),
        center=(sky_x, y, roof_z-.18), color=dark))
for i in range(1, 5):
    x = sky_x - 1 + i*.4
    skylight.include("grid_long_%d" % i, box((.035, 2.5, .10),
        center=(x, sky_y, roof_z-.20), color=steel))
for i in range(1, 6):
    y = sky_y - 1.25 + i*(2.5/6)
    skylight.include("grid_cross_%d" % i, box((2.0, .035, .10),
        center=(sky_x, y, roof_z-.20), color=steel))
scene.include("skylight", skylight)

# Fixtures run lengthwise over the aisle, separated by dark gaps.
fixtures = Asset("fluorescent_ceiling_lights")
for i, y in enumerate([-8.0, -3.8, .4, 4.6, 8.8, 13.0, 17.2]):
    fixtures.include("housing_%d" % i, box((.27, 3.35, .12),
        center=(-.45, y, roof_z-.38), color=(.43,.40,.29)))
    fixtures.include("diffuser_%d" % i, box((.19, 3.18, .045),
        center=(-.45, y, roof_z-.46), color=(1.0,.94,.68)))
scene.include("ceiling_lights", fixtures)

# Racks are composed of upright frames, shelf beams and braces, with the
# principal left-hand row carrying most of the visible loads.
levels = [1.0, 3.25, 5.48, 7.62]
bay_positions = [-8.0, -4.8, -1.6, 1.6, 4.8, 8.0, 11.2, 14.4]
for side in (-1, 1):
    inner_x = side * aisle_half_width
    outer_x = side * (aisle_half_width + rack_depth)
    rack = Asset("left_storage_rack" if side == -1 else "right_storage_rack")
    for j, y in enumerate(bay_positions):
        for k, x in enumerate((inner_x, outer_x)):
            rack.include("upright_%d_%d" % (j,k), box((.14,.15,8.9),
                center=(x,y,4.45), color=steel_edge))
        # Cross-bracing in the side frame makes the open lattice visible.
        for k in range(3):
            z0 = .8 + k*2.45
            rack.include("frame_diagonal_%d_%d" % (j,k),
                rod(.035, start=(inner_x,y,z0),
                    end=(outer_x,y,z0+1.45), color=steel))
            rack.include("frame_cross_%d_%d" % (j,k),
                box((rack_depth,.08,.075),
                    center=((inner_x+outer_x)/2,y,z0+1.45), color=steel))
    for j in range(len(bay_positions)-1):
        ya, yb = bay_positions[j], bay_positions[j+1]
        mid_y = (ya+yb)/2
        for k, z in enumerate(levels):
            for q, x in enumerate((inner_x, outer_x)):
                rack.include("shelf_beam_%d_%d_%d" % (j,k,q),
                    box((.12,yb-ya,.19), center=(x,mid_y,z), color=beam_color))
            rack.include("deck_%d_%d" % (j,k),
                box((rack_depth, yb-ya-.12, .07),
                    center=((inner_x+outer_x)/2,mid_y,z+.04), color=dark))
    scene.include("rack_left" if side == -1 else "rack_right", rack)

    loads = Asset("left_palletized_goods" if side == -1 else "right_palletized_goods")
    for j in range(len(bay_positions)-1):
        ya, yb = bay_positions[j], bay_positions[j+1]
        # Several open bays preserve the irregular dark gaps in the photograph.
        for k, z in enumerate(levels):
            if (j*3+k+(0 if side == -1 else 2)) % 7 == 0:
                continue
            center_y = (ya+yb)/2 + random.uniform(-.22,.22)
            center_x = (inner_x+outer_x)/2
            pallet_w = 1.28
            pallet_l = random.uniform(1.45,2.05)
            loads.include("pallet_%d_%d" % (j,k),
                box((pallet_w,pallet_l,.14),
                    center=(center_x,center_y,z+.16), color=wood))
            height = random.uniform(.90,1.65)
            col = random.choice(wrap_colors if (j+k)%3 != 0 else carton_colors)
            loads.include("load_%d_%d" % (j,k),
                box((1.20,pallet_l-.10,height),
                    center=(center_x,center_y,z+.24+height/2), color=col))
            # Wide bands suggest wrapping and strapped cartons without excessive detail.
            if (j+k)%2 == 0:
                for b, frac in enumerate((.20,.78)):
                    loads.include("wrap_band_%d_%d_%d" % (j,k,b),
                        box((1.22,pallet_l-.08,.035),
                            center=(center_x,center_y,z+.24+height*frac),
                            color=(.78,.74,.60)))
    scene.include("loads_left" if side == -1 else "loads_right", loads)

realize(scene)

# Set original portrait aspect before the projection check and final render.
sc = bpy.context.scene
sc.render.resolution_x = 341
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.27, 0.23, 0.14, 1)
background.inputs["Strength"].default_value = .55

set_view(camera_position, camera_target, lens=camera_lens, sensor=36)

# Reference positions are independent visual estimates, not calibration targets.
# The projections establish only camera-space positions, not visibility.
landmarks = [
    ("skylight_corner", (sky_x-1, sky_y-1.25, roof_z-.18), (.59,.20)),
    ("left_front_upright_top", (-aisle_half_width, -8.0, 8.9), (.12,.14)),
    ("left_distant_shelf", (-aisle_half_width, 8.0, 5.48), (.66,.76)),
    ("foreground_pallet_corner", (-aisle_half_width, -4.8, 3.25), (.12,.73)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name, point, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, "reference", ref, "projected",
              None if uv is None else tuple(round(v,3) for v in uv))

projection_table("Camera landmark check")
# Verify direction of a small upward aim trial, then restore the chosen camera.
set_view(camera_position, (camera_target[0],camera_target[1],camera_target[2]+.25),
         lens=camera_lens, sensor=36)
projection_table("Upward aim trial")
set_view(camera_position, camera_target, lens=camera_lens, sensor=36)
projection_table("Restored camera")

area_emitter((0,-3,8.7), power=1100, size=6, target=(0,0,3), color=(1,.79,.45))
area_emitter((0,7,8.8), power=1400, size=7, target=(0,5,3), color=(1,.84,.55))
area_emitter((-3,-3,6.8), power=650, size=5, target=(-3,0,3.5), color=(1,.72,.38))

# Make fixture diffusers and glazing emit light while retaining editable meshes.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    color = bsdf.inputs["Base Color"].default_value
    if color[0] > .95 and color[1] > .88 and color[2] > .6:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (1.0,.88,.56,1)
            bsdf.inputs["Emission Strength"].default_value = 5.0
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (1.0,.88,.56,1)
            bsdf.inputs["Emission Strength"].default_value = 5.0

sc.view_settings.view_transform = "AgX"
