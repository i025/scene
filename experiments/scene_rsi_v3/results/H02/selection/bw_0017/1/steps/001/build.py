from sceneact import *
import bpy
import math

# Reference inventory and anchors, estimated in normalized image coordinates:
# - Dark steel roof and beams: x=0–1, y=0–0.33; shallow diagonals converge right.
# - Left wall with vertical bright windows: x=0–0.27, y=0.32–0.67.
# - Main raised processing line: x=0.22–0.96, y=0.29–0.76.
#   Pale stainless housings sit behind yellow platform rails, with silver ducts above.
# - Yellow stairs descend toward the foreground at x=0.18–0.31, 0.40–0.57,
#   and 0.73–0.89. The railings overlap the machines and their dark supports.
# - Green vertical tank: x=0.36–0.45, y=0.54–0.83, in front of the platform.
# - Foreground silver framework and blue roller conveyors: x=0–0.68, y=0.72–1.
# - Glossy green floor is most visible at bottom right. Far equipment and machinery
#   connections are partly occluded; their precise layout is uncertain.
# Dominant edges: upright columns, nearly horizontal platform rails, diagonal stairs,
# and roof beams receding toward the right rear.
#
# Approximate expanded primitive count: architecture 55; platforms and railings 125;
# machines and ducts 75; stairs 75; tank 10; conveyors 95; background 15.
# Total about 450 simple boxes and rods, with no booleans or fillet expansions.

scene = Scene("Workshop")

# Main dimensions and camera are independent to allow later adjustments.
hall_w, hall_d, hall_h = 16.0, 23.0, 7.0
platform_z = 2.35
camera_position = (8.0, -21.0, 8.5)
camera_target = (0.0, 2.3, 2.7)
camera_lens = 34

steel = (0.19, 0.22, 0.23)
steel_dark = (0.075, 0.09, 0.095)
roof = (0.20, 0.22, 0.22)
wall = (0.30, 0.32, 0.31)
window = (0.71, 0.82, 0.87)
silver = (0.63, 0.66, 0.66)
silver_light = (0.76, 0.78, 0.76)
silver_dark = (0.37, 0.40, 0.40)
yellow = (0.95, 0.63, 0.015)
green = (0.025, 0.31, 0.20)
floor_green = (0.18, 0.40, 0.31)
blue = (0.09, 0.28, 0.65)
white = (0.80, 0.82, 0.79)

def add(parent, name, node):
    parent.include(name, node)

def rail_segment(asset, name, a, b, zbase=platform_z, height=1.05, posts=4):
    ax, ay = a
    bx, by = b
    for j, z in enumerate((zbase + 0.12, zbase + 0.58, zbase + height)):
        add(asset, name + "_horizontal_" + str(j),
            rod(0.027, start=(ax, ay, z), end=(bx, by, z), color=yellow))
    for i in range(posts):
        t = i / (posts - 1) if posts > 1 else 0
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        add(asset, name + "_post_" + str(i),
            rod(0.032, start=(x, y, zbase), end=(x, y, zbase + height), color=yellow))

def stair(asset, name, x, y_front, y_back, width=1.05, steps=9):
    # Stairs rise from the foreground towards the platform.
    bottom_z, top_z = 0.05, platform_z
    for side in (-1, 1):
        xx = x + side * width / 2
        add(asset, name + "_stringer_" + str(side),
            rod(0.065, start=(xx, y_front, bottom_z),
                end=(xx, y_back, top_z), color=yellow))
        add(asset, name + "_handrail_" + str(side),
            rod(0.032, start=(xx, y_front, bottom_z + 1.0),
                end=(xx, y_back, top_z + 1.0), color=yellow))
        add(asset, name + "_midrail_" + str(side),
            rod(0.023, start=(xx, y_front, bottom_z + 0.52),
                end=(xx, y_back, top_z + 0.52), color=yellow))
        for j in range(4):
            t = j / 3
            yy = y_front + (y_back - y_front) * t
            zz = bottom_z + (top_z - bottom_z) * t
            add(asset, name + "_post_%s_%s" % (side, j),
                rod(0.027, start=(xx, yy, zz), end=(xx, yy, zz + 1.0),
                    color=yellow))
    for i in range(steps):
        t = (i + 0.5) / steps
        yy = y_front + (y_back - y_front) * t
        zz = bottom_z + (top_z - bottom_z) * t
        add(asset, name + "_tread_" + str(i),
            box((width, 0.24, 0.055), center=(x, yy, zz), color=silver_dark))

# Architecture: green floor, strip-window wall, steel frame, and profiled roof.
architecture = Asset("Hall_structure")
add(architecture, "green_epoxy_floor",
    box((hall_w, hall_d, 0.12), center=(0, 1, -0.08), color=floor_green))
add(architecture, "left_wall",
    box((0.16, hall_d, hall_h), center=(-8, 1, hall_h / 2), color=wall))
add(architecture, "rear_wall",
    box((hall_w, 0.16, hall_h), center=(0, 12.5, hall_h / 2), color=wall))
add(architecture, "roof_deck",
    box((hall_w, hall_d, 0.13), center=(0, 1, hall_h), color=roof))
for y in (-9, -5, -1, 3, 7, 11):
    add(architecture, "left_column_" + str(y),
        box((0.23, 0.23, hall_h), center=(-7.75, y, hall_h / 2), color=steel_dark))
    add(architecture, "right_column_" + str(y),
        box((0.23, 0.23, hall_h), center=(7.75, y, hall_h / 2), color=steel_dark))
    add(architecture, "roof_crossbeam_" + str(y),
        box((15.6, 0.22, 0.28), center=(0, y, 6.75), color=steel_dark))
for x in (-5.1, -2.5, 0, 2.5, 5.1):
    add(architecture, "roof_purlin_" + str(x),
        box((0.11, 22, 0.12), center=(x, 1, 6.86), color=steel))
for i, y in enumerate((-8, -6, -4, -2, 0, 2, 4, 6, 8, 10)):
    add(architecture, "window_" + str(i),
        box((0.04, 0.85, 2.65), center=(-7.89, y, 3.45), color=window))
    add(architecture, "window_mullion_" + str(i),
        box((0.06, 0.035, 2.7), center=(-7.84, y, 3.45), color=steel))
    add(architecture, "window_crossbar_" + str(i),
        box((0.06, 0.9, 0.04), center=(-7.84, y, 3.45), color=steel))
for y in (-6, 0, 6):
    add(architecture, "ceiling_light_" + str(y),
        box((3.0, 0.15, 0.035), center=(0, y, 6.91), color=white))
scene.include("hall", architecture)

# Continuous structural platform under the processing line.
platform = Asset("Raised_steel_platform")
add(platform, "walkway_deck",
    box((12.5, 3.0, 0.16), center=(0, 3.2, platform_z - 0.08), color=silver_dark))
for x in (-5.8, -3.0, 0, 3.0, 5.8):
    for y in (1.85, 4.5):
        add(platform, "support_%s_%s" % (x, y),
            box((0.16, 0.16, platform_z), center=(x, y, platform_z / 2), color=steel))
for y in (1.8, 4.55):
    add(platform, "longitudinal_beam_" + str(y),
        box((12.7, 0.15, 0.24), center=(0, y, platform_z - 0.22), color=steel))
rail_segment(platform, "front_left", (-6.2, 1.72), (-3.7, 1.72), posts=4)
rail_segment(platform, "front_middle", (-2.3, 1.72), (0.1, 1.72), posts=4)
rail_segment(platform, "front_right", (1.5, 1.72), (4.0, 1.72), posts=4)
rail_segment(platform, "front_end", (5.15, 1.72), (6.2, 1.72), posts=2)
rail_segment(platform, "rear", (-6.2, 4.65), (6.2, 4.65), posts=9)
rail_segment(platform, "left_end", (-6.2, 1.72), (-6.2, 4.65), posts=3)
rail_segment(platform, "right_end", (6.2, 1.72), (6.2, 4.65), posts=3)
stair(platform, "left_stair", -3.0, -1.15, 1.72, width=1.05)
stair(platform, "middle_stair", 0.8, -1.3, 1.72, width=1.05)
stair(platform, "right_stair", 4.6, -1.3, 1.72, width=1.05)
scene.include("platform_and_stairs", platform)

# Three large stainless processing units, arranged along the raised platform.
machines = Asset("Processing_machines")
for i, (x, w, h) in enumerate(((-4.4, 2.35, 1.35), (-0.8, 2.55, 1.5), (3.1, 2.75, 2.05))):
    y = 3.45
    add(machines, "machine_%d_base" % i,
        box((w, 1.7, 0.3), center=(x, y, platform_z + 0.18), color=silver_dark))
    add(machines, "machine_%d_housing" % i,
        box((w, 1.45, h), center=(x, y, platform_z + 0.35 + h / 2), color=silver_light))
    add(machines, "machine_%d_front_panel" % i,
        box((w * 0.86, 0.045, h * 0.52),
            center=(x, y - 0.75, platform_z + 0.40 + h * 0.48), color=silver))
    add(machines, "machine_%d_dark_opening" % i,
        box((w * 0.70, 0.055, 0.21),
            center=(x, y - 0.78, platform_z + 0.46 + h * 0.68), color=steel_dark))
    for j in range(3):
        add(machines, "machine_%d_panel_line_%d" % (i, j),
            box((w * 0.72, 0.025, 0.025),
                center=(x, y - 0.81, platform_z + 0.50 + j * 0.16), color=silver_dark))
    add(machines, "machine_%d_upper_cap" % i,
        box((w * 0.9, 1.3, 0.15),
            center=(x, y, platform_z + 0.35 + h + 0.05), color=silver))
# Side cabinets and smaller equipment at the far right.
for i, x in enumerate((5.9, 6.9)):
    add(machines, "control_cabinet_" + str(i),
        box((0.68, 0.75, 1.6), center=(x, 4.4, 3.15), color=white))
    add(machines, "cabinet_screen_" + str(i),
        box((0.22, 0.025, 0.16), center=(x, 4.0, 3.5), color=steel_dark))
scene.include("processing_line", machines)

# Insulated pipes, elbows represented by short angled cylindrical segments.
ducts = Asset("Insulated_ducts")
def tube_chain(name, pts, radius=0.15):
    for i in range(len(pts) - 1):
        add(ducts, name + "_section_" + str(i),
            rod(radius, start=pts[i], end=pts[i + 1], color=silver_light))
for i, x in enumerate((-4.4, -0.8, 3.1)):
    top = platform_z + (1.8 if i < 2 else 2.4)
    tube_chain("riser_" + str(i),
               [(x, 3.8, top), (x, 3.8, 5.35),
                (x + 0.15, 3.8, 5.55), (x + 0.65, 3.8, 5.50),
                (x + 1.0, 3.8, 5.25)], 0.17)
    add(ducts, "hanger_" + str(i),
        rod(0.025, start=(x + 0.55, 3.8, 5.5),
            end=(x + 0.55, 3.8, 6.75), color=steel))
tube_chain("horizontal_header",
           [(-5.6, 4.6, 4.75), (-2.6, 4.6, 4.75),
            (0.2, 4.6, 4.75), (3.6, 4.6, 4.75), (6.2, 4.6, 4.75)], 0.12)
tube_chain("side_process_pipe",
           [(-5.7, 2.9, 1.2), (-5.7, 2.9, 2.0),
            (-5.1, 2.9, 2.0), (-5.1, 3.2, 2.5)], 0.10)
scene.include("ductwork", ducts)

# Green vertical vessel in front of the raised line.
tank = Asset("Green_vertical_tank")
tx, ty = -2.15, -0.15
add(tank, "cylindrical_shell",
    rod(0.56, start=(tx, ty, 0.42), end=(tx, ty, 2.05), color=green))
add(tank, "top_head", ball(0.56, center=(tx, ty, 2.05), color=green))
add(tank, "bottom_head", ball(0.54, center=(tx, ty, 0.43), color=green))
for i, (dx, dy) in enumerate(((-0.38, -0.32), (0.38, -0.32), (-0.38, 0.32), (0.38, 0.32))):
    add(tank, "leg_" + str(i),
        box((0.09, 0.09, 0.46), center=(tx + dx, ty + dy, 0.23), color=steel_dark))
add(tank, "top_nozzle",
    rod(0.09, start=(tx, ty, 2.5), end=(tx, ty, 2.82), color=green))
add(tank, "side_pipe",
    rod(0.075, start=(tx + 0.4, ty, 1.05), end=(tx + 0.9, ty, 1.05), color=silver))
scene.include("green_tank", tank)

# Foreground conveyor system: blue belts/rollers, open silver frames and legs.
conveyors = Asset("Foreground_conveyor_lines")
for line, (cy, length, cx) in enumerate(((-5.25, 9.4, -2.3), (-3.75, 7.5, -1.6),
                                         (-2.35, 5.8, -0.7))):
    z = 0.92
    add(conveyors, "belt_" + str(line),
        box((length, 0.82, 0.075), center=(cx, cy, z), color=blue))
    for side in (-1, 1):
        yy = cy + side * 0.48
        add(conveyors, "side_rail_%d_%d" % (line, side),
            box((length, 0.07, 0.18), center=(cx, yy, z + 0.02), color=silver_light))
        for j in range(4):
            xx = cx - length * 0.43 + j * length * 0.86 / 3
            add(conveyors, "leg_%d_%d_%d" % (line, side, j),
                box((0.07, 0.07, 0.88), center=(xx, yy, 0.46), color=silver))
    for j in range(12):
        xx = cx - length * 0.46 + j * length * 0.92 / 11
        add(conveyors, "roller_%d_%d" % (line, j),
            rod(0.035, start=(xx, cy - 0.4, z + 0.06),
                end=(xx, cy + 0.4, z + 0.06), color=silver_light))
    add(conveyors, "drive_motor_" + str(line),
        box((0.42, 0.35, 0.3),
            center=(cx + length * 0.36, cy + 0.65, 0.65), color=steel))
# Additional open stainless frames linking the foreground to the machines.
for i, x in enumerate((-4.8, -2.8, -0.8, 1.2, 3.2)):
    add(conveyors, "transfer_frame_top_" + str(i),
        box((1.65, 0.8, 0.10), center=(x, -1.65, 1.15), color=silver_light))
    for side in (-1, 1):
        add(conveyors, "transfer_frame_leg_%d_%d" % (i, side),
            box((0.07, 0.07, 1.1), center=(x + side * 0.7, -1.65, 0.55), color=silver))
scene.include("conveyors", conveyors)

realize(scene)

# World, lights, and camera are configured after realization.
sc = bpy.context.scene
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
background.inputs["Color"].default_value = (0.68, 0.75, 0.78, 1)
background.inputs["Strength"].default_value = 0.65

set_view(camera_position, camera_target, lens=camera_lens, sensor=36)
area_emitter((-6.8, -3, 5.2), power=1800, size=7, target=(0, 2, 1.5))
area_emitter((1, -2, 6.5), power=1500, size=7, target=(0, 2, 0))
area_emitter((3, 7, 6.4), power=1100, size=6, target=(0, 2, 1.8))

# Make material families read as reflective steel and glossy painted floor.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if abs(r - g) < 0.06 and abs(g - b) < 0.06 and 0.32 < r < 0.82:
        bsdf.inputs["Metallic"].default_value = 0.65
        bsdf.inputs["Roughness"].default_value = 0.31
    elif g > r * 1.3 and g > b * 1.05:
        bsdf.inputs["Metallic"].default_value = 0.18
        bsdf.inputs["Roughness"].default_value = 0.24
