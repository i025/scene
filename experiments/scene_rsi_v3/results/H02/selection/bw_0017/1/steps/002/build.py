from sceneact import *
import bpy

# Reference estimates, in normalized image coordinates:
# Roof and dark beams occupy y=0.00–0.34; tall left windows x=0.00–0.25,
# y=0.34–0.64. The machine line spans x=0.23–0.94, y=0.30–0.73.
# Yellow platform rails overlap machines at y=0.44–0.61. Three diagonal
# stair runs descend across x=0.06–0.32, 0.40–0.58 and 0.73–0.89.
# The green tank occupies x=0.36–0.45, y=0.53–0.80. Silver and blue
# foreground conveyors fill x=0.00–0.69, y=0.70–1.00.
# Platform rails are nearly horizontal; stair rails slope upward to the right.
# The roof beams recede toward the right. Duct connections and equipment behind
# the machines are partially occluded and remain approximate.
#
# Comparison with the previous render:
# 1. Camera/crop: the render showed the roof exterior and blank background over
#    roughly y=0.00–0.30; the reference shows the roof underside there. The
#    platform and foreground conveyors were too small and left too much empty
#    floor around them. Lowering and moving the camera inside the hall and
#    increasing its lens moves the machinery outward and fills the frame.
# 2. Perspective: the rendered platform rails slope visibly down to the right,
#    while the reference rails are nearly horizontal. Reducing the camera's
#    lateral offset should flatten them while retaining a modest diagonal view.
# 3. Foreground: rendered blue conveyors were confined roughly to x=0.08–0.52,
#    y=0.67–0.87, instead of continuing through the bottom edge. Bringing the
#    camera closer and extending the frames toward it should crop the foreground.
# 4. Background: rendered wall windows occupied x=0.00–0.30 and were too
#    prominent relative to the equipment. The closer, lower viewpoint should
#    reduce their visible area; extending the roof prevents an exterior crop.
# 5. Local details: the render showed three flat box-like machine faces and
#    comparatively sparse ductwork. Layered fronts, pipe bends and an open
#    conveyor framework add the visible broad shapes and gaps. Exact hidden
#    machine connections remain uncertain.
#
# Estimated expanded primitive count: hall 75, platform and stairs 140,
# machines and ducts 70, tank 9, conveyors and transfer frames 115;
# approximately 409 simple boxes, rods and balls. No Boolean operations.

scene = Scene("Steel_frame_production_hall")

# Camera parameters are independent of asset positions and dimensions.
camera_position = (2.0, -12.0, 4.6)
camera_target = (0.0, 2.5, 3.0)
camera_lens = 32

hall_width = 16.0
hall_height = 7.0
platform_z = 2.35

dark = (0.09, 0.11, 0.115)
steel = (0.20, 0.23, 0.23)
wall = (0.26, 0.28, 0.28)
roof = (0.25, 0.27, 0.27)
window = (0.75, 0.86, 0.91)
silver = (0.58, 0.62, 0.62)
light_silver = (0.75, 0.77, 0.75)
dark_silver = (0.34, 0.38, 0.38)
yellow = (0.98, 0.64, 0.015)
green = (0.015, 0.31, 0.22)
floor_green = (0.14, 0.35, 0.27)
blue = (0.07, 0.24, 0.57)
white = (0.82, 0.84, 0.81)

def put(parent, name, node):
    parent.include(name, node)

def segment(parent, name, a, b, radius, color):
    put(parent, name, rod(radius, start=a, end=b, color=color))

def rail(parent, name, x0, x1, y, z=platform_z, height=1.05, posts=4):
    for j, h in enumerate((0.10, 0.55, height)):
        segment(parent, name + "_bar_" + str(j),
                (x0, y, z + h), (x1, y, z + h), 0.028, yellow)
    for j in range(posts):
        x = x0 + (x1 - x0) * j / max(posts - 1, 1)
        segment(parent, name + "_post_" + str(j),
                (x, y, z), (x, y, z + height), 0.032, yellow)

def end_rail(parent, name, x, y0, y1, z=platform_z):
    for j, h in enumerate((0.12, 0.57, 1.05)):
        segment(parent, name + "_bar_" + str(j),
                (x, y0, z + h), (x, y1, z + h), 0.028, yellow)
    for j in range(3):
        y = y0 + (y1 - y0) * j / 2
        segment(parent, name + "_post_" + str(j),
                (x, y, z), (x, y, z + 1.05), 0.032, yellow)

def stair(parent, name, x, front, back, width=1.05):
    low, high = 0.08, platform_z
    for side in (-1, 1):
        xx = x + side * width / 2
        for suffix, rise, radius in (
            ("stringer", 0.0, 0.055),
            ("middle", 0.52, 0.026),
            ("top", 1.02, 0.034),
        ):
            segment(parent, name + "_" + suffix + str(side),
                    (xx, front, low + rise),
                    (xx, back, high + rise), radius, yellow)
        for j in range(4):
            t = j / 3
            yy = front + (back - front) * t
            zz = low + (high - low) * t
            segment(parent, name + "_post_%s_%s" % (side, j),
                    (xx, yy, zz), (xx, yy, zz + 1.02), 0.027, yellow)
    for j in range(10):
        t = (j + 0.5) / 10
        yy = front + (back - front) * t
        zz = low + (high - low) * t
        put(parent, name + "_tread_" + str(j),
            box((width, 0.25, 0.055), center=(x, yy, zz),
                color=light_silver))

# Architecture. The front extension keeps the camera below the roof plane.
hall = Asset("Hall_structure")
put(hall, "epoxy_floor",
    box((hall_width, 36, 0.12), center=(0, -1.5, -0.07),
        color=floor_green))
put(hall, "left_wall",
    box((0.16, 36, hall_height), center=(-8, -1.5, 3.5), color=wall))
put(hall, "rear_wall",
    box((16, 0.16, hall_height), center=(0, 16.5, 3.5), color=wall))
put(hall, "roof_deck",
    box((16, 36, 0.14), center=(0, -1.5, 7.0), color=roof))
for y in (-14, -10, -6, -2, 2, 6, 10, 14):
    for x in (-7.8, 7.8):
        put(hall, "column_%s_%s" % (x, y),
            box((0.24, 0.24, 7.0), center=(x, y, 3.5), color=dark))
    put(hall, "crossbeam_" + str(y),
        box((15.8, 0.24, 0.30), center=(0, y, 6.75), color=dark))
for x in (-6, -3, 0, 3, 6):
    put(hall, "roof_purlin_" + str(x),
        box((0.10, 35, 0.12), center=(x, -1.5, 6.86), color=steel))
for i, y in enumerate(range(-14, 15, 2)):
    put(hall, "vertical_window_" + str(i),
        box((0.045, 0.78, 2.55), center=(-7.89, y, 3.45), color=window))
    put(hall, "window_vertical_mullion_" + str(i),
        box((0.06, 0.035, 2.58), center=(-7.85, y, 3.45), color=steel))
    put(hall, "window_horizontal_mullion_" + str(i),
        box((0.06, 0.80, 0.035), center=(-7.85, y, 3.45), color=steel))
for y in (-8, -1, 6, 13):
    put(hall, "roof_light_" + str(y),
        box((2.6, 0.16, 0.035), center=(0, y, 6.90), color=white))
scene.include("hall", hall)

# Raised deck and steel supports.
platform = Asset("Operating_platform_and_stairs")
put(platform, "walkway_deck",
    box((12.5, 2.9, 0.15), center=(0, 3.1, platform_z - 0.08),
        color=dark_silver))
for x in (-5.8, -3.0, 0, 3.0, 5.8):
    for y in (1.8, 4.4):
        put(platform, "deck_support_%s_%s" % (x, y),
            box((0.15, 0.15, platform_z),
                center=(x, y, platform_z / 2), color=steel))
for y in (1.75, 4.5):
    put(platform, "deck_beam_" + str(y),
        box((12.7, 0.16, 0.26), center=(0, y, platform_z - 0.24),
            color=dark))
rail(platform, "front_left", -6.2, -3.7, 1.65, posts=4)
rail(platform, "front_middle", -2.45, 0.0, 1.65, posts=4)
rail(platform, "front_right", 1.25, 3.95, 1.65, posts=4)
rail(platform, "front_end", 5.2, 6.2, 1.65, posts=2)
rail(platform, "rear_guard", -6.2, 6.2, 4.55, posts=10)
end_rail(platform, "left_guard", -6.2, 1.65, 4.55)
end_rail(platform, "right_guard", 6.2, 1.65, 4.55)
stair(platform, "left_stair", -3.05, -1.65, 1.65)
stair(platform, "middle_stair", 0.62, -1.75, 1.65)
stair(platform, "right_stair", 4.58, -1.75, 1.65)
scene.include("platform", platform)

# Stainless units, with broad separate panels and recessed-looking dark bands.
machines = Asset("Processing_machines")
for i, (x, width, height) in enumerate(
        ((-4.35, 2.35, 1.38), (-0.85, 2.50, 1.40), (3.05, 2.80, 2.02))):
    y = 3.45
    base = platform_z + 0.28
    put(machines, "machine_%d_base" % i,
        box((width, 1.7, 0.30), center=(x, y, platform_z + 0.15),
            color=dark_silver))
    put(machines, "machine_%d_body" % i,
        box((width, 1.4, height), center=(x, y, base + height / 2),
            color=light_silver))
    put(machines, "machine_%d_face" % i,
        box((width * 0.86, 0.05, height * 0.56),
            center=(x, y - 0.73, base + height * 0.48), color=silver))
    put(machines, "machine_%d_opening" % i,
        box((width * 0.76, 0.055, height * 0.20),
            center=(x, y - 0.765, base + height * 0.60), color=dark))
    for j in range(3):
        put(machines, "machine_%d_front_rail_%d" % (i, j),
            box((width * 0.78, 0.055, 0.04),
                center=(x, y - 0.80, base + height * (0.38 + 0.09 * j)),
                color=light_silver))
    put(machines, "machine_%d_top_cap" % i,
        box((width * 0.92, 1.25, 0.14),
            center=(x, y, base + height + 0.04), color=silver))
for i, x in enumerate((5.9, 6.8)):
    put(machines, "control_cabinet_" + str(i),
        box((0.62, 0.75, 1.60), center=(x, 4.25, 3.15), color=white))
    put(machines, "control_display_" + str(i),
        box((0.20, 0.03, 0.14), center=(x, 3.86, 3.50), color=dark))
scene.include("processing_machines", machines)

ducts = Asset("Insulated_ducts_and_pipework")
def pipe(name, points, radius=0.14):
    for i in range(len(points) - 1):
        segment(ducts, name + "_" + str(i), points[i], points[i + 1],
                radius, light_silver)

pipe("left_riser", [(-4.4, 3.7, 3.9), (-4.4, 3.7, 4.9),
                     (-4.3, 3.7, 5.1), (-3.95, 3.7, 5.15),
                     (-3.1, 3.7, 4.95), (-2.9, 3.7, 4.6)], 0.16)
pipe("right_riser", [(3.05, 3.7, 4.2), (3.05, 3.7, 5.2),
                      (3.15, 3.7, 5.42), (3.4, 3.7, 5.48),
                      (4.0, 3.7, 5.22), (4.1, 3.7, 4.8)], 0.17)
pipe("rear_header", [(-5.8, 4.5, 4.6), (-2.8, 4.5, 4.6),
                      (0, 4.5, 4.6), (3.2, 4.5, 4.6),
                      (6.1, 4.5, 4.6)], 0.12)
pipe("left_process_pipe", [(-5.7, 2.8, 1.15), (-5.7, 2.8, 2.0),
                            (-5.2, 2.8, 2.0), (-5.2, 3.1, 2.5)], 0.10)
for i, x in enumerate((-4.0, 3.5)):
    segment(ducts, "ceiling_hanger_" + str(i),
            (x, 3.7, 5.1), (x, 3.7, 6.75), 0.025, steel)
scene.include("ducts", ducts)

tank = Asset("Green_vertical_vessel")
tx, ty = -2.15, -0.25
segment(tank, "cylindrical_shell", (tx, ty, 0.42), (tx, ty, 2.05),
        0.56, green)
put(tank, "upper_head", ball(0.56, center=(tx, ty, 2.05), color=green))
put(tank, "lower_head", ball(0.52, center=(tx, ty, 0.43), color=green))
for i, (dx, dy) in enumerate(((-0.37, -0.30), (0.37, -0.30),
                               (-0.37, 0.30), (0.37, 0.30))):
    put(tank, "support_leg_" + str(i),
        box((0.09, 0.09, 0.46),
            center=(tx + dx, ty + dy, 0.23), color=steel))
segment(tank, "top_nozzle", (tx, ty, 2.50), (tx, ty, 2.78), 0.09, green)
segment(tank, "side_connection", (tx + 0.4, ty, 1.05),
        (tx + 0.9, ty, 1.05), 0.075, silver)
scene.include("tank", tank)

# Multiple foreground conveyors and open transfer frames.
conveyors = Asset("Blue_roller_conveyors")
for line, (cy, length, cx) in enumerate(
        ((-7.0, 11.2, -2.6), (-5.5, 10.0, -2.0),
         (-4.0, 8.5, -1.4), (-2.55, 6.5, -0.6))):
    z = 0.92
    put(conveyors, "blue_belt_" + str(line),
        box((length, 0.82, 0.07), center=(cx, cy, z), color=blue))
    for side in (-1, 1):
        yy = cy + side * 0.47
        put(conveyors, "guide_%d_%d" % (line, side),
            box((length, 0.07, 0.18), center=(cx, yy, z + 0.03),
                color=light_silver))
        for j in range(4):
            xx = cx - length * 0.43 + j * length * 0.86 / 3
            put(conveyors, "support_%d_%d_%d" % (line, side, j),
                box((0.07, 0.07, 0.88), center=(xx, yy, 0.46),
                    color=silver))
    for j in range(12):
        xx = cx - length * 0.46 + j * length * 0.92 / 11
        segment(conveyors, "roller_%d_%d" % (line, j),
                (xx, cy - 0.39, z + 0.06),
                (xx, cy + 0.39, z + 0.06), 0.035, light_silver)
    put(conveyors, "drive_motor_" + str(line),
        box((0.40, 0.35, 0.30),
            center=(cx + length * 0.35, cy + 0.65, 0.65), color=steel))

for i, x in enumerate((-4.8, -2.8, -0.8, 1.2, 3.2)):
    for side in (-1, 1):
        yy = -1.85 + side * 0.38
        put(conveyors, "transfer_side_%d_%d" % (i, side),
            box((1.7, 0.07, 0.12), center=(x, yy, 1.15),
                color=light_silver))
        put(conveyors, "transfer_leg_%d_%d" % (i, side),
            box((0.07, 0.07, 1.10), center=(x + side * 0.70, yy, 0.55),
                color=silver))
    for j in range(3):
        xx = x - 0.65 + 0.65 * j
        put(conveyors, "transfer_cross_%d_%d" % (i, j),
            box((0.06, 0.8, 0.08), center=(xx, -1.85, 1.15),
                color=light_silver))
scene.include("conveyors", conveyors)

realize(scene)

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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (0.65, 0.72, 0.76, 1)
background.inputs["Strength"].default_value = 0.55

set_view(camera_position, camera_target, lens=camera_lens, sensor=36)
area_emitter((-7.2, -2.5, 4.6), power=1900, size=7,
             target=(0, 2, 1.5))
area_emitter((-3.0, 5.0, 6.5), power=1200, size=6,
             target=(0, 2, 1.5))
area_emitter((3.0, -3.0, 6.4), power=1400, size=7,
             target=(0, 1, 1.2))
area_emitter((4.0, 8.0, 6.4), power=900, size=6,
             target=(0, 3, 2.0))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if abs(r - g) < 0.06 and abs(g - b) < 0.06 and 0.32 < r < 0.84:
        bsdf.inputs["Metallic"].default_value = 0.65
        bsdf.inputs["Roughness"].default_value = 0.30
    elif g > r * 1.3 and g > b * 1.05:
        bsdf.inputs["Metallic"].default_value = 0.18
        bsdf.inputs["Roughness"].default_value = 0.24
