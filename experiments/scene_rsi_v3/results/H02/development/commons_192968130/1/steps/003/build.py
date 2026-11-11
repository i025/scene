from sceneact import *
import bpy
import math

# Reference inventory and image anchors, normalized to 512 x 342:
# Slat wall x=0–0.46, y=0.11–0.76; white door x=0.31–0.45,
# y=0.29–0.77; sideboard x=0–0.20, y=0.65–0.80. The door overlaps
# the slats. The counter's left edge runs from (0.46,0.59) to (0.36,1).
# A black sink lies around (0.54,0.67), and the foreground black hob starts
# near y=0.77. Dark upper cabinets overlap the backsplash at upper right.
# Vertical edges are nearly vertical; counter and cabinet edges converge
# toward the back. Sink depth and geometry beyond the image are uncertain.
#
# Comparison with the second render, ranked by visible extent and contrast:
# 1. The foreground hob is missing, whereas the reference has a large black
#    surface from y~0.77 to the bottom. Move its center forward in the
#    visible counter run, from y=-0.35 to y=1.0, to bring it into frame.
# 2. The rendered upper cabinet is a light peach region at x~0.62–1, rather
#    than dark walnut starting around x~0.46. Extend its front toward the
#    aisle and lower it slightly; use darker wood and reduce direct lighting.
#    This should move its lower contour left and down and darken the mass.
# 3. Door bounds are approximately x=0.34–0.47, y=0.36–0.84, versus
#    x=0.31–0.45, y=0.29–0.77. The counter junction is near (0.54,0.62)
#    versus (0.46,0.59). Aim the camera slightly farther right and down:
#    background anchors should move left and up. The back-wall top is also
#    too low, near y=0.21 versus 0.11, so raise the slat panel top.
# 4. The sideboard is nearly fully cropped in the render; shift it right so
#    its white front enters at the left edge. Preserve the door/slat overlap.
# Observed brightness depends on light as well as color and orientation.
#
# Expanded primitive estimate: about 190 meshes: 64 slats, 25 floor seams,
# 48 hob-ring rods, 20 stone veins, and approximately 33 other parts.

scene = Scene('Modern kitchen interior')

# Camera parameters are separate from architectural and furniture dimensions.
cam_position = (-0.45, -0.1, 1.72)
cam_target = (0.65, 4.2, 1.28)
cam_lens = 24
back_y = 4.8
right_x = 2.3
room_height = 3.35
counter_left = 0.72
counter_right = right_x
counter_front = -6.0
counter_back = 4.65
counter_height = 0.91

wall_white = (0.80, 0.79, 0.76)
floor_color = (0.48, 0.45, 0.40)
wood_dark = (0.055, 0.019, 0.008)
wood_mid = (0.28, 0.105, 0.038)
wood_light = (0.39, 0.18, 0.068)
black = (0.012, 0.012, 0.011)
metal = (0.39, 0.39, 0.37)
stone = (0.77, 0.75, 0.70)

architecture = Asset('architecture')
architecture.include('floor', box((10, 14, 0.12),
    center=(-2.0, -1.0, -0.06), color=floor_color))
architecture.include('right_wall', box((0.12, 14, room_height),
    center=(right_x + 0.10, -1.0, room_height / 2), color=wall_white))
architecture.include('back_wall', box((10, 0.12, room_height),
    center=(-2.0, back_y + 0.07, room_height / 2), color=wall_white))
architecture.include('ceiling', box((10, 14, 0.10),
    center=(-2.0, -1.0, room_height + 0.05), color=(0.78, 0.77, 0.75)))
scene.include('architecture', architecture)

floor_detail = Asset('floor_plank_joints')
for i in range(17):
    y = -5.5 + i * 0.62
    floor_detail.include('cross_joint_%02d' % i,
        box((8.0, 0.006, 0.003), center=(-1.8, y, 0.003),
            color=(0.39, 0.37, 0.34)))
for i in range(8):
    x = -3.4 + i * 0.72
    floor_detail.include('length_joint_%02d' % i,
        box((0.006, 10.5, 0.003), center=(x, -0.45, 0.004),
            color=(0.40, 0.38, 0.35)))
scene.include('floor_detail', floor_detail)

slatwall = Asset('walnut_slat_feature_wall')
slat_height = 2.90
slatwall.include('dark_backing', box((6.2, 0.055, slat_height),
    center=(-2.60, 4.71, 0.12 + slat_height / 2), color=wood_dark))
for i in range(64):
    x = -5.62 + i * 0.096
    slatwall.include('vertical_slat_%02d' % i,
        box((0.058, 0.045, slat_height),
            center=(x, 4.66, 0.12 + slat_height / 2),
            color=wood_light if i % 4 == 0 else wood_mid))
slatwall.include('top_border', box((6.2, 0.045, 0.035),
    center=(-2.60, 4.65, 3.02), color=wood_dark))
scene.include('slatwall', slatwall)

door = Asset('white_door')
door_x = -0.24
door.include('frame', box((0.91, 0.075, 2.18),
    center=(door_x, 4.57, 1.09), color=(0.91, 0.91, 0.88)))
door.include('door_leaf', box((0.77, 0.035, 2.04),
    center=(door_x, 4.515, 1.06), color=(0.83, 0.83, 0.80)))
door.include('left_reveal', box((0.009, 0.008, 2.02),
    center=(door_x - 0.388, 4.49, 1.06), color=(0.55, 0.55, 0.52)))
door.include('top_reveal', box((0.78, 0.008, 0.009),
    center=(door_x, 4.49, 2.08), color=(0.57, 0.57, 0.54)))
door.include('handle_plate', box((0.035, 0.015, 0.14),
    center=(door_x - 0.27, 4.478, 0.96), color=metal))
door.include('handle', rod(0.012, start=(door_x - 0.27, 4.46, 1.00),
    end=(door_x - 0.13, 4.46, 1.00), color=(0.65, 0.65, 0.63)))
door.include('keyhole', ball(0.012,
    center=(door_x - 0.27, 4.462, 0.91), color=black))
scene.include('door', door)

switches = Asset('wall_switches')
switches.include('switch', box((0.13, 0.025, 0.11),
    center=(-0.86, 4.60, 1.13), color=(0.86, 0.86, 0.83)))
switches.include('outlet', box((0.10, 0.025, 0.10),
    center=(-0.83, 4.60, 0.27), color=(0.85, 0.85, 0.82)))
scene.include('switches', switches)

sideboard = Asset('low_sideboard')
sideboard.include('body', box((1.72, 0.48, 0.48),
    center=(-2.68, 4.37, 0.28), color=black))
sideboard.include('white_front', box((1.52, 0.018, 0.29),
    center=(-2.70, 4.117, 0.20), color=(0.83, 0.84, 0.82)))
sideboard.include('warm_top_edge', box((1.53, 0.018, 0.025),
    center=(-2.70, 4.105, 0.37), color=wood_mid))
scene.include('sideboard', sideboard)

kitchen = Asset('kitchen_counter')
counter_width = counter_right - counter_left
counter_len = counter_back - counter_front
counter_center_y = (counter_front + counter_back) / 2
kitchen.include('base_cabinet', box((counter_width, counter_len, 0.84),
    center=((counter_left + counter_right) / 2, counter_center_y, 0.42),
    color=(0.22, 0.13, 0.08)))
kitchen.include('stone_worktop', box((counter_width + 0.08, counter_len, 0.065),
    center=((counter_left + counter_right) / 2, counter_center_y, counter_height),
    color=stone))
kitchen.include('backsplash', box((0.035, counter_len, 1.03),
    center=(right_x - 0.015, counter_center_y, 1.46),
    color=(0.86, 0.86, 0.83)))
kitchen.include('backsplash_end_panel', box((counter_width, 0.035, 1.0),
    center=((counter_left + counter_right) / 2, counter_back, 1.46),
    color=(0.15, 0.045, 0.012)))
scene.include('kitchen', kitchen)

veins = Asset('countertop_veining')
for i in range(20):
    y = -1.5 + i * 0.30
    x = 0.81 + (i * 0.37 % 1.22)
    dx = 0.10 + (i % 3) * 0.035
    veins.include('vein_%02d' % i, rod(0.003,
        start=(x, y, 0.947),
        end=(min(x + dx, 2.25), y + 0.07 + (i % 2) * 0.035, 0.947),
        color=(0.43, 0.40, 0.35)))
scene.include('veins', veins)

hob = Asset('induction_cooktop')
hob_y = 1.0
hob.include('glass', box((1.20, 2.05, 0.015),
    center=(1.48, hob_y, 0.953), color=(0.009, 0.010, 0.009)))
hob.include('near_edge', box((1.20, 0.018, 0.012),
    center=(1.48, hob_y - 1.02, 0.962), color=(0.28, 0.28, 0.26)))
for idx, (cx, cy, r) in enumerate([
        (1.12, hob_y - 0.45, 0.28), (1.78, hob_y - 0.45, 0.25),
        (1.12, hob_y + 0.38, 0.26), (1.78, hob_y + 0.38, 0.25)]):
    for j in range(12):
        a = 2 * math.pi * j / 12
        b = 2 * math.pi * (j + 1) / 12
        hob.include('ring_%d_%02d' % (idx, j), rod(0.004,
            start=(cx + r * math.cos(a), cy + r * math.sin(a), 0.965),
            end=(cx + r * math.cos(b), cy + r * math.sin(b), 0.965),
            color=(0.15, 0.15, 0.13)))
scene.include('hob', hob)

sink = Asset('dark_inset_sink')
sink.include('rim', box((1.06, 0.88, 0.012),
    center=(1.45, 3.28, 0.953), color=(0.18, 0.16, 0.13)))
sink.include('basin_opening', box((0.94, 0.76, 0.014),
    center=(1.45, 3.28, 0.960), color=(0.018, 0.018, 0.016)))
sink.include('back_inner_edge', box((0.86, 0.018, 0.008),
    center=(1.45, 3.62, 0.969), color=(0.29, 0.27, 0.23)))
scene.include('sink', sink)

upper = Asset('upper_walnut_cabinets')
upper_bottom = 2.08
upper_top = 3.35
upper_front = 1.08
upper.include('cabinet_body', box((right_x - upper_front, 10.0, upper_top - upper_bottom),
    center=((right_x + upper_front) / 2, -0.35, (upper_top + upper_bottom) / 2),
    color=(0.035, 0.010, 0.004)))
upper.include('front_panels', box((0.055, 10.0, 1.18),
    center=(upper_front, -0.35, 2.72), color=(0.065, 0.018, 0.005)))
upper.include('far_end_panel', box((1.25, 0.06, 1.27),
    center=(1.69, 4.62, 2.715), color=wood_dark))
upper.include('front_lower_trim', box((0.055, 10.0, 0.045),
    center=(1.05, -0.35, 2.08), color=(0.035, 0.010, 0.004)))
upper.include('extractor_metal', box((0.68, 2.35, 0.035),
    center=(1.62, 0.7, 2.055), color=(0.39, 0.38, 0.35)))
upper.include('extractor_dark_slot', box((0.025, 2.0, 0.008),
    center=(1.29, 0.7, 2.032), color=(0.10, 0.09, 0.08)))
upper.include('light_strip', box((0.045, 8.4, 0.025),
    center=(1.29, -0.22, 2.015), color=(1.0, 0.88, 0.63)))
scene.include('upper_cabinets', upper)

realize(scene)
set_view(cam_position, cam_target, lens=cam_lens, sensor=36)

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
background.inputs['Color'].default_value = (0.72, 0.72, 0.70, 1)
background.inputs['Strength'].default_value = 0.40

area_emitter((-2.7, -2.5, 2.85), power=500, size=4.5,
    target=(0.3, 2.0, 0.8), color=(1.0, 0.91, 0.80))
area_emitter((0.7, 2.6, 2.7), power=120, size=2.5,
    target=(1.7, 2.0, 1.0), color=(1.0, 0.76, 0.52))
area_emitter((1.15, -1.0, 2.00), power=75, size=2.0,
    target=(2.2, -0.5, 1.1), color=(1.0, 0.78, 0.55))
