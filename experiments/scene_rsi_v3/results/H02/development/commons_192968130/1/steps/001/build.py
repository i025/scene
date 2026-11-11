from sceneact import *
import bpy
import math

# Reference inventory and visual anchors, normalized to the 512 x 342 image:
# - Floor: lower left, approximately (0.00, 0.75) to (0.40, 1.00).
# - Vertical walnut slat wall: (0.00, 0.11) to (0.46, 0.76), behind the door.
# - White door and frame: (0.31, 0.29) to (0.45, 0.77); handle at (0.34, 0.59).
# - Low black-and-white cabinet at far left: (0.00, 0.65) to (0.20, 0.80).
# - Counter: left edge runs from approximately (0.36, 1.00) to (0.46, 0.59);
#   pale stone surface and black hob occupy the foreground. A black sink is farther back.
# - White backsplash occupies the right side, from about (0.57, 0.39) to (1, 1).
# - Dark upper cabinets occupy the upper right, overlapping the backsplash; their
#   lower edge recedes toward approximately (0.53, 0.43). A long light is underneath.
# Dominant directions: vertical wall slats and door edges; countertop, cabinets and
# backsplash converge toward the back. The back wall meets the counter at its far end.
# Hidden cabinet interiors, the room behind the camera, and details outside frame are
# uncertain. Small wall outlets, door handle, extractor underside and hob rings are visible.
#
# Estimated expanded primitive count: about 160 meshes, including 43 wall slats,
# 25 floor seams, 4 hob ring outlines made from 48 short rods, and the architectural,
# cabinet, counter, sink, door and lighting components.

scene = Scene('Modern kitchen interior')

# Major dimensions and camera parameters are kept separate for adjustment.
room_width = 6.2
back_y = 4.8
right_x = 2.3
room_height = 3.15
counter_left = 0.72
counter_right = right_x
counter_front = -5.7
counter_back = 4.65
counter_height = 0.91
cam_position = (-0.45, -5.7, 1.72)
cam_target = (0.30, 4.2, 1.47)
cam_lens = 24

white = (0.82, 0.82, 0.79)
wall_white = (0.79, 0.78, 0.75)
floor_color = (0.48, 0.45, 0.40)
wood_dark = (0.115, 0.045, 0.021)
wood_mid = (0.30, 0.115, 0.045)
wood_light = (0.40, 0.19, 0.075)
black = (0.018, 0.018, 0.017)
metal = (0.39, 0.39, 0.37)
stone = (0.73, 0.71, 0.66)

architecture = Asset('architecture')
architecture.include('floor', box((room_width, 13, 0.12),
                                  center=(-0.8, -1.1, -0.06), color=floor_color))
architecture.include('right_wall', box((0.12, 13, room_height),
                                       center=(right_x + 0.10, -1.2, room_height / 2),
                                       color=wall_white))
architecture.include('back_wall', box((room_width, 0.12, room_height),
                                      center=(-0.8, back_y + 0.07, room_height / 2),
                                      color=wall_white))
architecture.include('ceiling', box((room_width, 13, 0.10),
                                    center=(-0.8, -1.1, room_height + 0.05),
                                    color=(0.75, 0.74, 0.72)))
scene.include('architecture', architecture)

# Broad plank-like floor joints, kept subtle.
floor_detail = Asset('floor_plank_joints')
for i in range(17):
    y = -5.5 + i * 0.62
    floor_detail.include('cross_joint_%02d' % i,
                         box((5.9, 0.008, 0.003), center=(-0.75, y, 0.003),
                             color=(0.36, 0.34, 0.31)))
for i in range(8):
    x = -3.4 + i * 0.72
    floor_detail.include('length_joint_%02d' % i,
                         box((0.007, 10.5, 0.003), center=(x, -0.45, 0.004),
                             color=(0.38, 0.36, 0.33)))
scene.include('floor_detail', floor_detail)

# Walnut slat feature wall, with dark narrow recesses between individual battens.
slatwall = Asset('walnut_slat_feature_wall')
slatwall.include('dark_backing', box((4.25, 0.055, 2.62),
                                     center=(-1.62, 4.71, 1.43), color=wood_dark))
for i in range(43):
    x = -3.70 + i * 0.096
    slatwall.include('vertical_slat_%02d' % i,
                     box((0.058, 0.045, 2.62), center=(x, 4.66, 1.43),
                         color=wood_light if i % 4 == 0 else wood_mid))
slatwall.include('top_border', box((4.25, 0.045, 0.035),
                                   center=(-1.62, 4.65, 2.75), color=wood_dark))
scene.include('slatwall', slatwall)

# White door in front of the slat wall.
door = Asset('white_door')
door_x = -0.24
door.include('frame', box((0.91, 0.075, 2.18), center=(door_x, 4.57, 1.09),
                          color=(0.91, 0.91, 0.88)))
door.include('door_leaf', box((0.77, 0.035, 2.04), center=(door_x, 4.515, 1.06),
                              color=(0.83, 0.83, 0.80)))
door.include('left_reveal', box((0.009, 0.008, 2.02),
                                center=(door_x - 0.388, 4.49, 1.06), color=(0.55, 0.55, 0.52)))
door.include('top_reveal', box((0.78, 0.008, 0.009),
                               center=(door_x, 4.49, 2.08), color=(0.57, 0.57, 0.54)))
door.include('handle_plate', box((0.035, 0.015, 0.14),
                                 center=(door_x - 0.27, 4.478, 0.96), color=metal))
door.include('handle', rod(0.012, start=(door_x - 0.27, 4.46, 1.00),
                           end=(door_x - 0.13, 4.46, 1.00), color=(0.65, 0.65, 0.63)))
door.include('keyhole', ball(0.012, center=(door_x - 0.27, 4.462, 0.91), color=black))
scene.include('door', door)

switches = Asset('wall_switches')
switches.include('switch', box((0.13, 0.025, 0.11),
                               center=(-0.86, 4.60, 1.13), color=(0.86, 0.86, 0.83)))
switches.include('outlet', box((0.10, 0.025, 0.10),
                               center=(-0.83, 4.60, 0.27), color=(0.85, 0.85, 0.82)))
scene.include('switches', switches)

# Low cabinet, partially cropped by the left edge of the photograph.
sideboard = Asset('low_sideboard')
sideboard.include('body', box((1.72, 0.48, 0.48), center=(-3.44, 4.37, 0.28), color=black))
sideboard.include('white_front', box((1.52, 0.018, 0.29),
                                     center=(-3.46, 4.117, 0.20), color=(0.83, 0.84, 0.82)))
sideboard.include('warm_top_edge', box((1.53, 0.018, 0.025),
                                       center=(-3.46, 4.105, 0.37), color=wood_mid))
scene.include('sideboard', sideboard)

# Counter and its pale backsplash. A single continuous stone slab gives the strong
# diagonal foreground silhouette; the sink is represented by layered inset surfaces.
kitchen = Asset('kitchen_counter')
counter_width = counter_right - counter_left
counter_len = counter_back - counter_front
kitchen.include('base_cabinet', box((counter_width, counter_len, 0.84),
                                    center=((counter_left + counter_right) / 2,
                                            (counter_front + counter_back) / 2, 0.42),
                                    color=(0.29, 0.20, 0.14)))
kitchen.include('stone_worktop', box((counter_width + 0.08, counter_len, 0.065),
                                     center=((counter_left + counter_right) / 2,
                                             (counter_front + counter_back) / 2,
                                             counter_height), color=stone))
kitchen.include('backsplash', box((0.035, counter_len, 1.03),
                                  center=(right_x - 0.015, (counter_front + counter_back) / 2,
                                          1.46), color=(0.86, 0.86, 0.83)))
kitchen.include('backsplash_end_panel', box((counter_width, 0.035, 1.0),
                                            center=((counter_left + counter_right) / 2,
                                                    counter_back, 1.46), color=(0.38, 0.16, 0.07)))
scene.include('kitchen', kitchen)

# Sparse stone veining on the worktop.
veins = Asset('countertop_veining')
for i in range(32):
    y = -5.25 + i * 0.31
    x = 0.81 + (i * 0.37 % 1.22)
    dx = 0.10 + (i % 3) * 0.035
    veins.include('vein_%02d' % i,
                  rod(0.004, start=(x, y, 0.947),
                      end=(min(x + dx, 2.25), y + 0.07 + (i % 2) * 0.035, 0.947),
                      color=(0.43, 0.40, 0.35)))
scene.include('veins', veins)

hob = Asset('induction_cooktop')
hob.include('glass', box((1.20, 2.05, 0.015),
                         center=(1.48, -3.50, 0.953), color=(0.012, 0.014, 0.013)))
hob.include('near_edge', box((1.20, 0.018, 0.012),
                             center=(1.48, -4.52, 0.962), color=(0.32, 0.32, 0.29)))
for idx, (cx, cy, r) in enumerate([(1.12, -3.95, 0.28), (1.78, -3.95, 0.25),
                                   (1.12, -3.12, 0.26), (1.78, -3.12, 0.25)]):
    for j in range(12):
        a = 2 * math.pi * j / 12
        b = 2 * math.pi * (j + 1) / 12
        hob.include('ring_%d_%02d' % (idx, j),
                    rod(0.004, start=(cx + r * math.cos(a), cy + r * math.sin(a), 0.965),
                        end=(cx + r * math.cos(b), cy + r * math.sin(b), 0.965),
                        color=(0.18, 0.18, 0.16)))
scene.include('hob', hob)

sink = Asset('dark_inset_sink')
sink.include('rim', box((1.06, 0.88, 0.012),
                        center=(1.45, 2.15, 0.953), color=(0.18, 0.16, 0.13)))
sink.include('basin_opening', box((0.94, 0.76, 0.014),
                                  center=(1.45, 2.15, 0.960), color=(0.018, 0.018, 0.016)))
sink.include('back_inner_edge', box((0.86, 0.018, 0.008),
                                    center=(1.45, 2.49, 0.969), color=(0.29, 0.27, 0.23)))
scene.include('sink', sink)

# Long overhead walnut cabinetry with a thin metal extractor below.
upper = Asset('upper_walnut_cabinets')
upper_bottom = 2.17
upper_top = 3.15
upper_front = 1.34
upper.include('cabinet_body', box((right_x - upper_front, 10.0, upper_top - upper_bottom),
                                  center=((right_x + upper_front) / 2, -0.35,
                                          (upper_top + upper_bottom) / 2),
                                  color=wood_dark))
upper.include('front_panels', box((0.055, 10.0, 0.91),
                                  center=(upper_front, -0.35, 2.68), color=(0.20, 0.075, 0.03)))
upper.include('far_end_panel', box((1.0, 0.06, 1.03),
                                   center=(1.83, 4.62, 2.65), color=wood_dark))
upper.include('front_lower_trim', box((0.055, 10.0, 0.045),
                                      center=(1.30, -0.35, 2.17), color=(0.09, 0.038, 0.021)))
upper.include('extractor_metal', box((0.68, 2.35, 0.035),
                                     center=(1.76, -1.30, 2.145), color=(0.54, 0.53, 0.49)))
upper.include('extractor_dark_slot', box((0.025, 2.0, 0.008),
                                         center=(1.43, -1.3, 2.122), color=(0.14, 0.13, 0.12)))
upper.include('light_strip', box((0.045, 8.4, 0.025),
                                 center=(1.43, -0.22, 2.105), color=(1.0, 0.88, 0.63)))
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
background.inputs['Strength'].default_value = 0.45

area_emitter((-2.7, -2.5, 2.85), power=500, size=4.5,
             target=(0.3, 2.0, 0.8), color=(1.0, 0.91, 0.80))
area_emitter((0.7, 2.6, 2.7), power=230, size=2.5,
             target=(1.7, 2.0, 1.0), color=(1.0, 0.76, 0.52))
area_emitter((1.15, -1.0, 2.08), power=90, size=2.0,
             target=(2.2, -0.5, 1.1), color=(1.0, 0.78, 0.55))
