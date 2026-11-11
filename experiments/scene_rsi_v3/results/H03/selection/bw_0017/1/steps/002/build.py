# Reference inventory, estimated from the 512 x 267 photograph:
# Hall: full frame; dark ceiling and beams y=0.00–0.39; tall side windows
# x=0.00–0.25, y=0.32–0.66; green floor visible at lower right.
# Right processing machine: x=0.60–0.80, y=0.29–0.71, with silver
# hood, dark opening and overhead insulated duct.
# Left and middle machines: x=0.23–0.60, y=0.34–0.66, partly occluded.
# Raised platforms and yellow rails: x=0.10–0.96, y=0.42–0.77.
# Stairs descend toward the foreground at left, center and right.
# Green tank: x=0.36–0.45, y=0.53–0.78, in front of the platform.
# Foreground conveyor frames and blue beds: x=0.00–0.72, y=0.70–1.00.
# Distant right equipment and hidden machine connections are uncertain.
# Main roof and platform edges run roughly horizontally; stair rails descend
# toward the foreground. Conveyor frames overlap the tank and platform legs.
#
# Expanded primitive estimate: hall ~100, platform and stairs ~150, machines
# ~50, ducts ~30, tank ~8, conveyors ~75: approximately 413 separate meshes.
# No Boolean, fillet or layout-helper expansion is used.
#
# The previous execution failed before scene construction because `json` is
# outside the frozen import contract. This program emits JSON diagnostic text
# without importing json; no visual changes are inferred from that failure.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

ROOM_W, ROOM_D, ROOM_H = 21.0, 25.0, 7.2
PLATFORM_Z = 2.55
CAMERA_POSITION = (9.0, -22.0, 8.1)
CAMERA_TARGET = (0.0, 3.0, 2.75)
CAMERA_LENS = 34.0
IMAGE_WIDTH, IMAGE_HEIGHT = 512, 267

steel = (0.085, 0.105, 0.105)
roof = (0.19, 0.205, 0.19)
wall = (0.25, 0.27, 0.25)
silver = (0.63, 0.68, 0.67)
light_silver = (0.79, 0.82, 0.80)
dark_metal = (0.19, 0.23, 0.22)
yellow = (0.95, 0.59, 0.015)
green = (0.015, 0.39, 0.28)
floor_green = (0.13, 0.39, 0.29)
blue = (0.05, 0.24, 0.56)
window = (0.69, 0.81, 0.84)

scene = Scene("Workshop")

def b(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def r(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

# Steel-frame building, open on the camera-facing side.
hall = Asset("Steel_frame_hall")
b(hall, "green_epoxy_floor", (ROOM_W, ROOM_D, .12),
  (0, 3, -.06), floor_green)
b(hall, "roof_sheet", (ROOM_W, ROOM_D, .18),
  (0, 3, ROOM_H), roof)
b(hall, "left_wall", (.18, ROOM_D, 6.3),
  (-ROOM_W / 2, 3, 3.15), wall)
b(hall, "far_wall", (ROOM_W, .18, 6.3),
  (0, 15.4, 3.15), wall)

for j, y in enumerate((-8, -3, 2, 7, 12, 15)):
    for side, x in enumerate((-10.25, 10.25)):
        b(hall, "column_web_%d_%d" % (j, side), (.20, .25, 7.0),
          (x, y, 3.5), steel)
        b(hall, "column_flange_%d_%d" % (j, side), (.48, .08, 7.0),
          (x, y, 3.5), steel)
    b(hall, "roof_crossbeam_%d" % j, (20.7, .28, .36),
      (0, y, 6.91), steel)

for i, x in enumerate((-8, -4, 0, 4, 8)):
    b(hall, "long_roof_purlin_%d" % i, (.18, 24.5, .18),
      (x, 3, 6.94), steel)

for i, y in enumerate((-7.0, -4.4, -1.8, .8, 3.4, 6.0, 8.6, 11.2, 13.8)):
    b(hall, "window_glazing_%d" % i, (.035, .92, 2.55),
      (-10.38, y, 3.05), window)
    for k, z in enumerate((1.76, 3.05, 4.34)):
        b(hall, "window_crossbar_%d_%d" % (i, k), (.055, 1.0, .055),
          (-10.34, y, z), dark_metal)
    for k, dy in enumerate((-.49, .49)):
        b(hall, "window_jamb_%d_%d" % (i, k), (.055, .055, 2.65),
          (-10.34, y + dy, 3.05), dark_metal)
scene.include("building", hall)

# Platforms and individually editable yellow rail and stair components.
platform = Asset("Operating_platforms")
b(platform, "main_deck", (15.3, 3.0, .20),
  (-.2, 4.1, PLATFORM_Z), silver)
b(platform, "deck_front_fascia", (15.3, .12, .35),
  (-.2, 2.56, PLATFORM_Z - .12), dark_metal)
for i, x in enumerate((-7.4, -4.7, -1.9, 1.0, 3.8, 6.9)):
    for j, y in enumerate((2.8, 5.3)):
        b(platform, "support_%d_%d" % (i, j), (.17, .17, 2.45),
          (x, y, 1.22), dark_metal)
        b(platform, "foot_%d_%d" % (i, j), (.42, .42, .08),
          (x, y, .04), silver)

for k, (x0, x1) in enumerate(((-7.7, -5.0), (-3.8, -.8),
                               (.8, 4.3), (5.5, 7.4))):
    for j, z in enumerate((3.12, 3.65)):
        r(platform, "front_rail_%d_%d" % (k, j),
          (x0, 2.48, z), (x1, 2.48, z), .035, yellow)
    count = max(1, int((x1 - x0) / 1.1))
    for i in range(count + 1):
        x = x0 + (x1 - x0) * i / count
        r(platform, "front_post_%d_%d" % (k, i),
          (x, 2.48, 2.62), (x, 2.48, 3.67), .032, yellow)

for j, z in enumerate((3.12, 3.65)):
    r(platform, "rear_rail_%d" % j,
      (-7.8, 5.58, z), (7.4, 5.58, z), .035, yellow)
for i in range(15):
    x = -7.8 + i * 15.2 / 14
    r(platform, "rear_post_%d" % i,
      (x, 5.58, 2.62), (x, 5.58, 3.65), .03, yellow)

def stair(parent, name, x, yfront, yback, width):
    n = 9
    for i in range(n):
        t = (i + .5) / n
        y = yfront + (yback - yfront) * t
        z = .12 + (PLATFORM_Z - .12) * t
        b(parent, name + "_tread_%d" % i, (width, .32, .07),
          (x, y, z), light_silver)
    for side in (-1, 1):
        xx = x + side * width * .54
        r(parent, name + "_stringer_%d" % side,
          (xx, yfront, .12), (xx, yback, PLATFORM_Z), .065, silver)
        r(parent, name + "_handrail_%d" % side,
          (xx, yfront, 1.12), (xx, yback, PLATFORM_Z + 1.03), .04, yellow)
        r(parent, name + "_midrail_%d" % side,
          (xx, yfront, .62), (xx, yback, PLATFORM_Z + .53), .027, yellow)
        for i in range(4):
            t = i / 3
            y = yfront + (yback - yfront) * t
            z = .12 + (PLATFORM_Z - .12) * t
            r(parent, name + "_post_%d_%d" % (side, i),
              (xx, y, z), (xx, y, z + 1.03), .032, yellow)

stair(platform, "middle_stair", 0.0, -.6, 2.55, 1.05)
stair(platform, "right_stair", 5.0, -.6, 2.55, 1.05)
stair(platform, "left_stair", -4.4, -.15, 2.55, .95)
scene.include("platforms_and_stairs", platform)

machines = Asset("Stainless_processing_machines")

def machine(parent, name, x, y, width, depth, height):
    base = PLATFORM_Z + .12
    b(parent, name + "_frame", (width, depth, .26),
      (x, y, base + .13), dark_metal)
    for i, dx in enumerate((-width * .39, width * .39)):
        b(parent, name + "_pedestal_%d" % i, (.25, depth * .87, .7),
          (x + dx, y, base + .50), silver)
    b(parent, name + "_main_body", (width, depth, height * .64),
      (x, y, base + .7 + height * .32), silver)
    b(parent, name + "_top_hood", (width * .93, depth * .95, height * .27),
      (x, y, base + .7 + height * .77), light_silver)
    front = y - depth / 2 - .012
    b(parent, name + "_dark_process_opening", (width * .78, .035, height * .24),
      (x, front, base + .7 + height * .50), dark_metal)
    for k in range(5):
        z = base + .7 + height * .39 + k * height * .052
        b(parent, name + "_opening_louver_%d" % k, (width * .77, .04, .035),
          (x, front - .025, z), light_silver)
    for i, dx in enumerate((-width * .44, width * .44)):
        b(parent, name + "_front_border_%d" % i, (.09, .08, height * .64),
          (x + dx, front - .025, base + .7 + height * .32), light_silver)

machine(machines, "large_right_machine", 3.5, 4.35, 3.4, 1.8, 2.0)
machine(machines, "left_machine", -4.7, 4.45, 2.7, 1.65, 1.55)
machine(machines, "center_machine", -.9, 5.0, 2.35, 1.4, 1.20)
b(machines, "far_right_cabinet", (1.25, 1.2, 2.25),
  (7.6, 6.7, 1.13), light_silver)
b(machines, "far_right_control", (.60, .08, .55),
  (7.6, 6.06, 1.6), dark_metal)
scene.include("machines", machines)

ducts = Asset("Insulated_ducts_and_pipework")

def duct(name, points, radius=.24):
    for i in range(len(points) - 1):
        r(ducts, name + "_segment_%d" % i,
          points[i], points[i + 1], radius, light_silver)
    for i, point in enumerate(points[1:-1]):
        ducts.include(name + "_elbow_%d" % i,
                      ball(radius=radius, center=point, color=light_silver))

duct("right_exhaust", [(3.6, 4.4, 5.15), (3.6, 4.4, 5.9),
                       (3.3, 4.4, 6.22), (2.5, 4.4, 6.22)], .26)
duct("left_exhaust", [(-4.7, 4.45, 4.87), (-4.7, 4.45, 5.65),
                      (-4.35, 4.45, 5.95), (-3.2, 4.45, 5.85),
                      (-2.6, 4.45, 5.55), (-2.15, 4.45, 4.95)], .23)
duct("horizontal_process_pipe", [(-7.4, 5.0, 4.45), (-5.9, 5.0, 4.45),
                                 (-5.5, 5.0, 4.1), (-1.0, 5.0, 4.1)], .12)
duct("right_side_pipe", [(5.35, 4.7, 4.5), (6.0, 4.7, 4.5),
                        (6.0, 4.7, 3.1), (7.6, 4.7, 3.1)], .12)
for i, x in enumerate((-5.0, -2.2, 2.5, 4.0, 6.0)):
    r(ducts, "overhead_hanger_%d" % i,
      (x, 4.4, 6.1), (x, 4.4, 6.85), .028, dark_metal)
scene.include("ductwork", ducts)

tank = Asset("Green_vertical_tank")
tx, ty = -3.0, .1
r(tank, "cylindrical_shell", (tx, ty, .40), (tx, ty, 2.65), .58, green)
tank.include("upper_dome", ball(radius=.58, center=(tx, ty, 2.65), color=green))
tank.include("lower_dome", ball(radius=.58, center=(tx, ty, .40), color=green))
for i, (dx, dy) in enumerate(((-.37, -.26), (.37, -.26), (0, .40))):
    b(tank, "foot_%d" % i, (.12, .12, .42),
      (tx + dx, ty + dy, .21), dark_metal)
r(tank, "top_nozzle", (tx, ty, 3.05), (tx, ty, 3.42), .09, silver)
r(tank, "side_nozzle", (tx + .48, ty, 1.8),
  (tx + .86, ty, 1.8), .09, silver)
scene.include("green_tank", tank)

conveyors = Asset("Foreground_roller_conveyors")

def conveyor(name, x, y, length, width):
    z = .85
    b(conveyors, name + "_blue_bed", (length, width, .10),
      (x, y, z), blue)
    for side in (-1, 1):
        b(conveyors, name + "_side_rail_%d" % side, (length, .10, .18),
          (x, y + side * width * .5, z + .06), light_silver)
    for j in range(11):
        xx = x - length / 2 + (j + .5) * length / 11
        r(conveyors, name + "_roller_%d" % j,
          (xx, y - width * .46, z + .09),
          (xx, y + width * .46, z + .09), .035, light_silver)
    for j, dx in enumerate((-length * .42, 0, length * .42)):
        for side in (-1, 1):
            b(conveyors, name + "_leg_%d_%d" % (j, side), (.09, .09, .79),
              (x + dx, y + side * width * .39, .40), silver)
        b(conveyors, name + "_crossbrace_%d" % j, (.08, width * .85, .07),
          (x + dx, y, .25), silver)
    b(conveyors, name + "_drive_motor", (.35, .33, .28),
      (x + length * .32, y + width * .64, .62), dark_metal)

conveyor("front_line", -3.5, -6.6, 11.5, 1.25)
conveyor("middle_line", -2.0, -4.25, 10.5, 1.10)
conveyor("short_line", 2.6, -2.4, 5.3, 1.0)
b(conveyors, "transfer_frame", (3.6, 1.5, .18),
  (-.3, -3.15, 1.02), light_silver)
for i, dx in enumerate((-1.5, 1.5)):
    b(conveyors, "transfer_leg_%d" % i, (.12, .12, .90),
      (-.3 + dx, -3.15, .45), silver)
b(conveyors, "foreground_guard", (2.2, .12, .62),
  (-.3, -4.1, 1.20), light_silver)
scene.include("conveyors", conveyors)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.72, 0.80, 0.84, 1)
background.inputs["Strength"].default_value = 0.65

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if not principled:
        continue
    c = principled.inputs["Base Color"].default_value
    if c[0] > .55 and abs(c[0] - c[1]) < .12:
        principled.inputs["Metallic"].default_value = .72
        principled.inputs["Roughness"].default_value = .30
    elif c[1] > c[0] * 1.3 and c[1] > .25:
        principled.inputs["Metallic"].default_value = .20
        principled.inputs["Roughness"].default_value = .24
    else:
        principled.inputs["Roughness"].default_value = .48

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-8, -2, 6.1), power=2200, size=8, target=(0, 3, 1.5))
area_emitter((1, 2, 6.8), power=1600, size=8, target=(0, 2, 0))
area_emitter((6, -4, 6.5), power=1000, size=7, target=(1, 3, 2))

# Approximate reference coordinates are (x right, y down), normalized.
# Each world point identifies an actual emitted feature, not an asset origin.
anchors = [
    ("tank_top", (tx, ty, 3.23), (.405, .53)),
    ("tank_bottom", (tx, ty, 0.0), (.405, .78)),
    ("main_machine_top_left", (1.92, 3.45, 5.41), (.62, .30)),
    ("main_machine_top_right", (5.08, 3.45, 5.41), (.79, .30)),
    ("platform_front_left", (-7.85, 2.56, 2.65), (.12, .57)),
    ("platform_front_right", (7.45, 2.56, 2.65), (.89, .58)),
    ("front_conveyor_left", (-9.25, -7.225, .95), (.02, .94)),
    ("right_stair_foot", (5.0, -.6, .12), (.80, .94)),
]

bpy.context.view_layer.update()
cam = sc.camera
depsgraph = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT, scale_x=1, scale_y=1
)
view = cam.matrix_world.inverted()
rows = []
for name, xyz, ref in anchors:
    clip = projection @ view @ Vector((xyz[0], xyz[1], xyz[2], 1.0))
    if clip.w <= 0:
        rows.append(
            '{"name":"%s","reference":[%.4f,%.4f],'
            '"projection":null,"residual":null,"behind_camera":true}'
            % (name, ref[0], ref[1])
        )
    else:
        u = .5 * (clip.x / clip.w + 1)
        v = .5 * (1 - clip.y / clip.w)
        rows.append(
            '{"name":"%s","reference":[%.4f,%.4f],'
            '"projection":[%.4f,%.4f],"residual":[%.4f,%.4f],'
            '"behind_camera":false}'
            % (name, ref[0], ref[1], u, v, u - ref[0], v - ref[1])
        )
print("ANCHOR_DIAGNOSTIC [" + ",".join(rows) + "]")
