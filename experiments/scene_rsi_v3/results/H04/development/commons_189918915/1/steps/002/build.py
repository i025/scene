import bpy
import math
import random
from mathutils import Vector
from sceneact import *

# Reference inventory and anchors, normalized image coordinates:
# Roof and structure occupy most of the upper and right image. The skylight lies
# at approximately (.59,.20)-(.84,.39), with a dark perimeter and fine grid.
# Fluorescent strips run diagonally down-right, from about (.35,0) toward (.88,.65).
# The main rack and its cargo fill the left and lower image, from (0,.08) to
# roughly (.85,1). A foreground wrapped load occupies approximately
# (0,.57)-(.28,.88). Rack beams and open dark bays continue into the lower right.
# A narrow opposite rack is visible only at the extreme right edge. Hidden
# lower shelves, the far aisle, and the precise contents of distant bays are uncertain.
#
# Comparison with the previous complete render:
# 1. The rendered light row is almost vertical at x .40-.48; the reference row
#    slopes from x .35 at the top to x .88 at y .65. The rack and roof edges
#    share this slope discrepancy. Camera roll is the largest supported change:
#    rolling the camera should rotate these common edges together and move the
#    lower parts of the light row and rack toward the right.
# 2. The rendered opposite rack occupies much of x .65-1.0, while in the
#    reference it is mostly cropped at the extreme right. Its inner edge is
#    moved outward, leaving the principal left rack and its openings in place.
# 3. The rendered skylight is a dim square near (.49,.48); the reference
#    skylight is bright and near (.71,.29). Its position is adjusted independently
#    of the camera, and luminous glazing is placed below the roof underside.
# 4. The previous foreground is a pair of pale rack walls. The reference has
#    darker steel shelves and irregular wrapped loads with visible dark openings.
#    Darker steel and varied cargo sizes preserve those gaps.
# Observed contours are approximate; projection checks below are separate from
# these observed bounds and do not establish visibility.
#
# Expanded primitive estimate: architecture 40, skylight 18, lights 14,
# left rack 154, right rack 75, loads and pallets about 120; total about 421.

random.seed(17)
scene = Scene("Warehouse reconstruction")

roof_z = 9.7
left_inner = -2.25
left_outer = -3.8
right_inner = 5.8
right_outer = 7.2
bay_positions = [-8.0, -4.8, -1.6, 1.6, 4.8, 8.0, 11.2, 14.4]
levels = [1.0, 3.25, 5.48, 7.62]

camera_position = (0.25, -8.4, 1.35)
camera_target = (0.15, 1.8, 8.7)
camera_lens = 29
camera_roll = math.radians(25)

steel = (.19, .18, .12)
steel_edge = (.29, .27, .18)
beam_color = (.23, .21, .14)
roof_color = (.25, .24, .17)
roof_rib = (.16, .16, .11)
dark = (.065, .070, .052)
wood = (.46, .30, .10)
cargo_colors = [
    (.58, .46, .27), (.68, .57, .36), (.48, .39, .23),
    (.70, .66, .51), (.57, .55, .45), (.76, .71, .55)
]

architecture = Asset("warehouse_architecture")
architecture.include("roof_surface", box(
    (18, 36, .16), center=(1, 3, roof_z), color=roof_color))
for i in range(31):
    x = -7.5 + i * .52
    architecture.include("corrugation_%02d" % i, box(
        (.035, 35, .07), center=(x, 3, roof_z-.12), color=roof_rib))
for i, y in enumerate([-10, -5, 0, 5, 10, 15, 20]):
    architecture.include("roof_girder_%d" % i, box(
        (17, .20, .34), center=(1, y, roof_z-.30), color=beam_color))
scene.include("architecture", architecture)

# The panel lies below the underside of the continuous roof so its bright surface
# remains visible without a Boolean cut.
sky_x, sky_y = 1.45, -.2
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
        (.032, 2.5, .09),
        center=(sky_x-1+i*.4, sky_y, roof_z-.31), color=steel))
for i in range(1, 7):
    skylight.include("cross_grid_%d" % i, box(
        (2, .032, .09),
        center=(sky_x, sky_y-1.25+i*2.5/7, roof_z-.31), color=steel))
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
    for j, y in enumerate(bay_positions):
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
    for j in range(len(bay_positions)-1):
        ya, yb = bay_positions[j:j+2]
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
    for j in range(len(bay_positions)-1):
        ya, yb = bay_positions[j:j+2]
        for k, z in enumerate(levels):
            if (j*3+k+(0 if side == "left" else 2)) % 7 == 0:
                continue
            cy = (ya+yb)/2 + random.uniform(-.25, .25)
            length = random.uniform(1.35, 2.25)
            width = depth-.25
            height = random.uniform(.85, 1.65)
            goods.include("pallet_%d_%d" % (j, k), box(
                (width, length, .14),
                center=(center_x, cy, z+.16), color=wood))
            goods.include("load_%d_%d" % (j, k), box(
                (width-.08, length-.10, height),
                center=(center_x, cy, z+.24+height/2),
                color=random.choice(cargo_colors)))
            if (j+k) % 2 == 0:
                for b, frac in enumerate((.22, .76)):
                    goods.include("wrap_band_%d_%d_%d" % (j, k, b), box(
                        (width-.06, length-.08, .025),
                        center=(center_x, cy, z+.24+height*frac),
                        color=(.71, .68, .53)))
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
    ("skylight_near_corner", (sky_x-1, sky_y-1.25, roof_z-.28), (.59, .20)),
    ("front_upright_top", (left_inner, -8, 8.9), (.12, .14)),
    ("distant_shelf_corner", (left_inner, 8, 5.48), (.66, .76)),
    ("foreground_shelf_corner", (left_inner, -4.8, 3.25), (.12, .73)),
    ("lamp_near_endpoint", (-.45, -5.39, roof_z-.46), (.39, .05))
]

def projection_table(label):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name, point, reference in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, "reference", reference, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

# Compare the old unrolled camera with a small roll trial and the selected roll.
# A positive local camera roll rotates downward image edges toward the right.
from mathutils import Euler
projection_table("Unrolled camera")
cam.rotation_euler = (base_rotation.to_quaternion() @
                      Euler((0, 0, math.radians(5))).to_quaternion()).to_euler()
projection_table("Five-degree roll trial")
cam.rotation_euler = (base_rotation.to_quaternion() @
                      Euler((0, 0, camera_roll)).to_quaternion()).to_euler()
projection_table("Selected rolled camera")

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
    emission_strength = 0
    if color[0] > .95 and color[1] > .88 and color[2] > .6:
        emission_color = (1, .90, .65, 1)
        emission_strength = 5
    elif .82 < color[0] < .87 and color[1] > .86 and color[2] > .75:
        emission_color = (.85, .91, .82, 1)
        emission_strength = 2
    if emission_color is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission_color
            bsdf.inputs["Emission Strength"].default_value = emission_strength

sc.view_settings.view_transform = "AgX"
