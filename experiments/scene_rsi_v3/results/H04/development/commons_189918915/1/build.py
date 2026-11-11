import bpy
import math
import random
from mathutils import Vector, Euler
from sceneact import *

# Visual inventory, normalized coordinates, estimated from the photograph:
# Main left rack and cargo: (0,.08)-(.90,1), with upright frames, long shelf
# beams, pallets, cartons, wrapped loads and irregular dark gaps. Foreground
# wrapped load is approximately (0,.56)-(.28,.88). A narrow opposing rack is
# visible at the extreme right. Hidden rack contents remain uncertain.
# Roof: upper and right background, with corrugations and crossing beams.
# Skylight: approximately (.59,.20)-(.84,.39), bright with a dark grid.
# Fluorescent strips: from approximately (.35,0) to (.88,.65).
# Roof and shelf lines descend to the right; uprights rise to the right.
# Cargo overlaps shelves; rack silhouettes overlap the roof.
#
# Comparison with the second render, in order of visual extent:
# 1. The rendered light row runs from about (.68,0) to (.29,.76), opposite
#    the reference slope from (.35,0) to (.88,.65). The rack has the same
#    reversed slope. Change camera_roll from +25 to -25 degrees: upper
#    endpoints should move left and lower endpoints right.
# 2. The rendered foreground rack is a thin strip at the left and a large
#    empty dark region occupies the bottom center; the reference rack and
#    loads cover most of the lower half. The roll correction should bring the
#    left rack across the lower frame. Extend the visible rack and cargo into
#    more bays to preserve its continuous silhouette and dark internal gaps.
# 3. The rendered skylight occupies roughly (.57,.33)-(.88,.50), versus
#    (.59,.20)-(.84,.39) in the reference. Roll affects its position; move
#    the skylight along the roof separately to raise it in the corrected view.
# 4. The rendered rack members are overly pale and the cargo too sparse.
#    Dark steel, pallet boards and varied larger loads should produce the
#    reference's alternating dark bays and warm, irregular rectangular goods.
#    Illumination also affects the observed brightness.
# Camera projections below are numerical checks, not observed contour bounds.
# Expanded estimate: roof 40, skylight 16, fixtures 14, racks 256,
# cargo and pallet parts about 220, total about 546 single-mesh primitives.

random.seed(17)
scene = Scene("Warehouse reconstruction")

roof_z = 9.7
left_inner, left_outer = -2.25, -3.8
right_inner, right_outer = 5.8, 7.2
bays = [-11.2, -8.0, -4.8, -1.6, 1.6, 4.8, 8.0, 11.2, 14.4]
levels = [1.0, 3.25, 5.48, 7.62]
camera_position = (0.25, -8.4, 1.35)
camera_target = (0.15, 1.8, 8.7)
camera_lens = 29
camera_roll = -25

steel = (.16, .16, .11)
steel_edge = (.27, .26, .18)
beam_color = (.22, .20, .13)
roof_color = (.25, .24, .17)
roof_rib = (.16, .16, .11)
dark = (.055, .06, .045)
wood = (.48, .31, .09)
cargo_colors = [
    (.58, .45, .25), (.68, .55, .34), (.46, .36, .21),
    (.70, .66, .50), (.57, .54, .43), (.76, .71, .55)
]

architecture = Asset("warehouse_architecture")
architecture.include("roof_surface", box(
    (18, 40, .16), center=(1, 3, roof_z), color=roof_color))
for i in range(31):
    architecture.include("roof_seam_%02d" % i, box(
        (.035, 39, .07), center=(-7.5+i*.52, 3, roof_z-.12),
        color=roof_rib))
for i, y in enumerate([-10, -5, 0, 5, 10, 15, 20]):
    architecture.include("roof_girder_%d" % i, box(
        (17, .20, .34), center=(1, y, roof_z-.30), color=beam_color))
scene.include("architecture", architecture)

sky_x, sky_y = 1.45, 1.0
skylight = Asset("ceiling_skylight")
skylight.include("glazing", box(
    (2.0, 2.5, .06), center=(sky_x, sky_y, roof_z-.22),
    color=(.84, .88, .78)))
for i, x in enumerate((sky_x-1, sky_x+1)):
    skylight.include("side_border_%d" % i, box(
        (.09, 2.6, .10), center=(x, sky_y, roof_z-.28), color=dark))
for i, y in enumerate((sky_y-1.25, sky_y+1.25)):
    skylight.include("end_border_%d" % i, box(
        (2.1, .09, .10), center=(sky_x, y, roof_z-.28), color=dark))
for i in range(1, 5):
    skylight.include("long_grid_%d" % i, box(
        (.032, 2.5, .09), center=(sky_x-1+i*.4, sky_y, roof_z-.31),
        color=steel))
for i in range(1, 7):
    skylight.include("cross_grid_%d" % i, box(
        (2, .032, .09), center=(sky_x, sky_y-1.25+i*2.5/7, roof_z-.31),
        color=steel))
scene.include("skylight", skylight)

fixtures = Asset("fluorescent_lights")
for i, y in enumerate([-8, -3.8, .4, 4.6, 8.8, 13, 17.2]):
    fixtures.include("housing_%d" % i, box(
        (.27, 3.35, .12), center=(-.45, y, roof_z-.38),
        color=(.35, .33, .23)))
    fixtures.include("diffuser_%d" % i, box(
        (.19, 3.18, .045), center=(-.45, y, roof_z-.46),
        color=(1.0, .94, .68)))
scene.include("lights", fixtures)

for side, inner_x, outer_x in [
    ("left", left_inner, left_outer),
    ("right", right_inner, right_outer)
]:
    rack = Asset(side + "_storage_rack")
    depth = abs(outer_x-inner_x)
    center_x = (inner_x+outer_x)/2
    for j, y in enumerate(bays):
        for k, x in enumerate((inner_x, outer_x)):
            rack.include("upright_%d_%d" % (j, k), box(
                (.13, .14, 8.9), center=(x, y, 4.45), color=steel_edge))
        for k in range(3):
            z0 = .8+k*2.45
            rack.include("diagonal_%d_%d" % (j, k), rod(
                .028, start=(inner_x, y, z0),
                end=(outer_x, y, z0+1.45), color=steel))
            rack.include("cross_%d_%d" % (j, k), box(
                (depth, .07, .065), center=(center_x, y, z0+1.45),
                color=steel))
    for j in range(len(bays)-1):
        ya, yb = bays[j:j+2]
        for k, z in enumerate(levels):
            for q, x in enumerate((inner_x, outer_x)):
                rack.include("beam_%d_%d_%d" % (j, k, q), box(
                    (.11, yb-ya, .17),
                    center=(x, (ya+yb)/2, z), color=beam_color))
            rack.include("deck_%d_%d" % (j, k), box(
                (depth, yb-ya-.12, .06),
                center=(center_x, (ya+yb)/2, z+.04), color=dark))
    scene.include(side+"_rack", rack)

    goods = Asset(side+"_palletized_goods")
    for j in range(len(bays)-1):
        ya, yb = bays[j:j+2]
        for k, z in enumerate(levels):
            if (j*3+k+(0 if side == "left" else 2)) % 8 == 0:
                continue
            cy = (ya+yb)/2 + random.uniform(-.2, .2)
            length = random.uniform(1.6, 2.5)
            width = depth-.18
            height = random.uniform(1.0, 1.7)
            goods.include("pallet_%d_%d" % (j, k), box(
                (width, length, .14),
                center=(center_x, cy, z+.16), color=wood))
            goods.include("load_%d_%d" % (j, k), box(
                (width-.08, length-.1, height),
                center=(center_x, cy, z+.24+height/2),
                color=random.choice(cargo_colors)))
            for b, frac in enumerate((.18, .78)):
                if (j+k) % 2 == 0:
                    goods.include("wrap_band_%d_%d_%d" % (j, k, b), box(
                        (width-.06, length-.08, .025),
                        center=(center_x, cy, z+.24+height*frac),
                        color=(.71, .68, .53)))
            if side == "left":
                for n, off in enumerate((-.4, .4)):
                    goods.include("pallet_block_%d_%d_%d" % (j, k, n), box(
                        (width*.85, .16, .12),
                        center=(center_x, cy+off*length, z+.08),
                        color=(.30, .19, .07)))
    scene.include(side+"_goods", goods)

realize(scene)
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
background.inputs["Color"].default_value = (.24, .20, .12, 1)
background.inputs["Strength"].default_value = .45

set_view(camera_position, camera_target, lens=camera_lens, sensor=36)
cam = sc.camera
base_rotation = cam.rotation_euler.copy()
landmarks = [
    ("skylight_corner", (sky_x-1, sky_y-1.25, roof_z-.28), (.59, .20)),
    ("foreground_shelf", (left_inner, -4.8, 3.25), (.12, .73)),
    ("distant_shelf", (left_inner, 8, 5.48), (.66, .76)),
    ("lamp_endpoint", (-.45, -5.39, roof_z-.46), (.39, .05))
]

def set_roll(degrees):
    cam.rotation_euler = (
        base_rotation.to_quaternion() @
        Euler((0, 0, math.radians(degrees))).to_quaternion()
    ).to_euler()

def projection_table(label):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name, point, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, "reference", ref, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

set_roll(25)
projection_table("Previous roll")
set_roll(20)
projection_table("Five-degree negative roll trial")
set_roll(camera_roll)
projection_table("Selected roll")

area_emitter((0, -3, 8.7), power=1100, size=6,
             target=(-1, 0, 3), color=(1, .79, .45))
area_emitter((0, 7, 8.8), power=1400, size=7,
             target=(-1, 5, 3), color=(1, .84, .55))
area_emitter((-3, -3, 6.8), power=650, size=5,
             target=(-3, 0, 3.5), color=(1, .72, .38))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    color = bsdf.inputs["Base Color"].default_value
    emission_color = None
    strength = 0
    if color[0] > .95 and color[1] > .88 and color[2] > .6:
        emission_color, strength = (1, .90, .65, 1), 5
    elif .82 < color[0] < .87 and color[1] > .86 and color[2] > .75:
        emission_color, strength = (.85, .91, .82, 1), 2
    if emission_color is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = strength

sc.view_settings.view_transform = "AgX"
