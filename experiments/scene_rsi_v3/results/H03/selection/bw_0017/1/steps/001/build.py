# Reference inventory and visual anchors, estimated from the 512 x 267 image:
# - Dark steel hall: full image; ceiling beams cross the upper 0.00–0.39,
#   left wall and tall strip windows occupy x 0.00–0.25, y 0.32–0.66.
# - Main right processing machine: x 0.60–0.80, y 0.29–0.71;
#   broad stainless hood, dark horizontal opening, insulated duct over top.
# - Left processing machine: x 0.23–0.46, y 0.34–0.65, partly hidden
#   by yellow rails, with a silver overhead duct.
# - Raised platform and yellow rails: approximately x 0.10–0.96,
#   y 0.42–0.77; stairs descend toward the viewer at center and right.
# - Green vertical tank: x 0.36–0.45, y 0.53–0.78, in front of platform.
# - Foreground conveyors: x 0.00–0.72, y 0.70–1.00; blue roller beds,
#   white/silver frames, legs and transverse connections.
# - Green floor is visible mainly at bottom right. Distant machinery at far
#   right and behind the platforms is partly occluded and uncertain.
# Dominant edges: roof beams run mostly left-to-right, receding slightly upward
# toward the right; yellow rails are nearly horizontal; stair rails slope down
# toward the foreground. Conveyor frames overlap the tank and platform legs.
#
# Approximate expanded primitives: architecture 60, processing equipment 45,
# ducts 35, platforms/rails/stairs 100, tank 12, conveyors 75, total ~327.
# Shapes use separate SceneAct parts, with no Boolean or fillet expansion.

import math
import json
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

# Room and equipment dimensions are in approximate metres.
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
black = (0.055, 0.065, 0.06)

scene = Scene("Workshop")

def add(parent, name, shape):
    parent.include(name, shape)

def b(parent, name, size, center, color):
    add(parent, name, box(size=size, center=center, color=color))

def r(parent, name, a, c, radius, color):
    add(parent, name, rod(radius=radius, start=a, end=c, color=color))

# Building shell: open front and right sides for the reference camera.
hall = Asset("Steel_frame_hall")
b(hall, "green_epoxy_floor", (ROOM_W, ROOM_D, .12),
  (0, 3, -.06), floor_green)
b(hall, "roof_sheet", (ROOM_W, ROOM_D, .18),
  (0, 3, ROOM_H), roof)
b(hall, "left_wall", (.18, ROOM_D, 6.3),
  (-ROOM_W/2, 3, 3.15), wall)
b(hall, "far_wall", (ROOM_W, .18, 6.3),
  (0, 15.4, 3.15), wall)

# Steel column rows, horizontal girders, and roof purlins.
for j, y in enumerate((-8, -3, 2, 7, 12, 15)):
    for side, x in enumerate((-10.25, 10.25)):
        b(hall, f"column_web_{j}_{side}", (.20, .25, 7.0),
          (x, y, 3.5), steel)
        b(hall, f"column_flange_{j}_{side}", (.48, .08, 7.0),
          (x, y, 3.5), steel)
    b(hall, f"roof_crossbeam_{j}", (20.7, .28, .36),
      (0, y, 6.91), steel)
for i, x in enumerate((-8, -4, 0, 4, 8)):
    b(hall, f"long_roof_purlin_{i}", (.18, 24.5, .18),
      (x, 3, 6.94), steel)

# Left-wall window strips. Bright glazing sits slightly in front of wall.
for i, y in enumerate((-7.0, -4.4, -1.8, .8, 3.4, 6.0, 8.6, 11.2, 13.8)):
    b(hall, f"window_glazing_{i}", (.035, .92, 2.55),
      (-10.38, y, 3.05), window)
    for z in (1.76, 3.05, 4.34):
        b(hall, f"window_crossbar_{i}_{z}", (.055, 1.0, .055),
          (-10.34, y, z), dark_metal)
    for dy in (-.49, .49):
        b(hall, f"window_jamb_{i}_{dy}", (.055, .055, 2.65),
          (-10.34, y+dy, 3.05), dark_metal)
scene.include("building", hall)

# Platforms, support legs, railings and stairs.
platform = Asset("Operating_platforms")
b(platform, "main_deck", (15.3, 3.0, .20), (-.2, 4.1, PLATFORM_Z), silver)
b(platform, "deck_front_fascia", (15.3, .12, .35),
  (-.2, 2.56, PLATFORM_Z-.12), dark_metal)
for i, x in enumerate((-7.4, -4.7, -1.9, 1.0, 3.8, 6.9)):
    for j, y in enumerate((2.8, 5.3)):
        b(platform, f"support_{i}_{j}", (.17, .17, 2.45),
          (x, y, 1.22), dark_metal)
        b(platform, f"foot_{i}_{j}", (.42, .42, .08),
          (x, y, .04), silver)

# Long yellow rails retain gaps at stairs.
for k, (x0, x1) in enumerate(((-7.7, -5.0), (-3.8, -.8), (.8, 4.3), (5.5, 7.4))):
    for z in (3.12, 3.65):
        r(platform, f"front_rail_{k}_{z}", (x0, 2.48, z),
          (x1, 2.48, z), .035, yellow)
    count = max(1, int((x1-x0)/1.1))
    for i in range(count+1):
        x = x0+(x1-x0)*i/count
        r(platform, f"front_post_{k}_{i}", (x, 2.48, 2.62),
          (x, 2.48, 3.67), .032, yellow)
for z in (3.12, 3.65):
    r(platform, f"rear_rail_{z}", (-7.8, 5.58, z),
      (7.4, 5.58, z), .035, yellow)
for i in range(15):
    x = -7.8+i*15.2/14
    r(platform, f"rear_post_{i}", (x, 5.58, 2.62),
      (x, 5.58, 3.65), .03, yellow)

def stair(parent, name, x, yfront, yback, width):
    # Lower end is toward the camera; open treads show through.
    n = 9
    for i in range(n):
        t = (i+.5)/n
        y = yfront+(yback-yfront)*t
        z = .12+(PLATFORM_Z-.12)*t
        b(parent, f"{name}_tread_{i}", (width, .32, .07),
          (x, y, z), light_silver)
    for side in (-1, 1):
        xx = x+side*width*.54
        r(parent, f"{name}_stringer_{side}",
          (xx, yfront, .12), (xx, yback, PLATFORM_Z), .065, silver)
        r(parent, f"{name}_handrail_{side}",
          (xx, yfront, 1.12), (xx, yback, PLATFORM_Z+1.03), .04, yellow)
        r(parent, f"{name}_midrail_{side}",
          (xx, yfront, .62), (xx, yback, PLATFORM_Z+.53), .027, yellow)
        for i in range(4):
            t = i/3
            y = yfront+(yback-yfront)*t
            z = .12+(PLATFORM_Z-.12)*t
            r(parent, f"{name}_post_{side}_{i}",
              (xx, y, z), (xx, y, z+1.03), .032, yellow)

stair(platform, "middle_stair", 0.0, -.6, 2.55, 1.05)
stair(platform, "right_stair", 5.0, -.6, 2.55, 1.05)
stair(platform, "left_stair", -4.4, -.15, 2.55, .95)
scene.include("platforms_and_stairs", platform)

# Stainless process machines, arranged along the platform.
machines = Asset("Stainless_processing_machines")
def machine(parent, name, x, y, w, d, h):
    base = PLATFORM_Z+.12
    b(parent, name+"_frame", (w, d, .26), (x, y, base+.13), dark_metal)
    for dx in (-w*.39, w*.39):
        b(parent, name+"_side_pedestal_"+str(dx), (.25, d*.87, .7),
          (x+dx, y, base+.50), silver)
    b(parent, name+"_main_body", (w, d, h*.64),
      (x, y, base+.7+h*.32), silver)
    b(parent, name+"_top_hood", (w*.93, d*.95, h*.27),
      (x, y, base+.7+h*.77), light_silver)
    front = y-d/2-.012
    b(parent, name+"_dark_process_opening", (w*.78, .035, h*.24),
      (x, front, base+.7+h*.50), dark_metal)
    for k in range(5):
        z = base+.7+h*.39+k*h*.052
        b(parent, name+f"_opening_louver_{k}", (w*.77, .04, .035),
          (x, front-.025, z), light_silver)
    for dx in (-w*.44, w*.44):
        b(parent, name+"_front_border_"+str(dx), (.09, .08, h*.64),
          (x+dx, front-.025, base+.7+h*.32), light_silver)

machine(machines, "large_right_machine", 3.5, 4.35, 3.4, 1.8, 2.0)
machine(machines, "left_machine", -4.7, 4.45, 2.7, 1.65, 1.55)
machine(machines, "center_machine", -.9, 5.0, 2.35, 1.4, 1.20)
# A small partially hidden machine at the far right.
b(machines, "far_right_cabinet", (1.25, 1.2, 2.25),
  (7.6, 6.7, 1.13), light_silver)
b(machines, "far_right_control", (.60, .08, .55),
  (7.6, 6.06, 1.6), dark_metal)
scene.include("machines", machines)

# Insulated silver ducts. Short rod segments describe the prominent bends.
ducts = Asset("Insulated_ducts_and_pipework")
def duct(name, points, radius=.24):
    for i in range(len(points)-1):
        r(ducts, name+f"_segment_{i}", points[i], points[i+1],
          radius, light_silver)
    for i, p in enumerate(points[1:-1]):
        add(ducts, name+f"_elbow_{i}", ball(radius=radius, center=p, color=light_silver))

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
    r(ducts, f"overhead_hanger_{i}", (x, 4.4, 6.1), (x, 4.4, 6.85), .028, dark_metal)
scene.include("ductwork", ducts)

# Green pressure vessel on the floor, with rounded ends and short connections.
tank = Asset("Green_vertical_tank")
tx, ty = -3.0, .1
r(tank, "cylindrical_shell", (tx, ty, .40), (tx, ty, 2.65), .58, green)
add(tank, "upper_dome", ball(radius=.58, center=(tx, ty, 2.65), color=green))
add(tank, "lower_dome", ball(radius=.58, center=(tx, ty, .40), color=green))
# Small feet read under the vessel; connections are deliberately simple.
for i, (dx, dy) in enumerate(((-.37, -.26), (.37, -.26), (0, .40))):
    b(tank, f"foot_{i}", (.12, .12, .42), (tx+dx, ty+dy, .21), dark_metal)
r(tank, "top_nozzle", (tx, ty, 3.05), (tx, ty, 3.42), .09, silver)
r(tank, "side_nozzle", (tx+.48, ty, 1.8), (tx+.86, ty, 1.8), .09, silver)
scene.include("green_tank", tank)

# Foreground conveyor beds, with blue slats and pale support structures.
conveyors = Asset("Foreground_roller_conveyors")
def conveyor(name, x, y, length, width):
    z = .85
    b(conveyors, name+"_blue_bed", (length, width, .10), (x, y, z), blue)
    for side in (-1, 1):
        b(conveyors, name+f"_side_rail_{side}", (length, .10, .18),
          (x, y+side*width*.5, z+.06), light_silver)
    for j in range(11):
        xx = x-length/2+(j+.5)*length/11
        r(conveyors, name+f"_roller_{j}",
          (xx, y-width*.46, z+.09), (xx, y+width*.46, z+.09), .035, light_silver)
    for dx in (-length*.42, 0, length*.42):
        for side in (-1, 1):
            b(conveyors, name+f"_leg_{dx}_{side}", (.09, .09, .79),
              (x+dx, y+side*width*.39, .40), silver)
        b(conveyors, name+f"_crossbrace_{dx}", (.08, width*.85, .07),
          (x+dx, y, .25), silver)
    b(conveyors, name+"_drive_motor", (.35, .33, .28),
      (x+length*.32, y+width*.64, .62), dark_metal)

conveyor("front_line", -3.5, -6.6, 11.5, 1.25)
conveyor("middle_line", -2.0, -4.25, 10.5, 1.10)
conveyor("short_line", 2.6, -2.4, 5.3, 1.0)
# Connecting frame and pale machine covers at the conveyor junction.
b(conveyors, "transfer_frame", (3.6, 1.5, .18), (-.3, -3.15, 1.02), light_silver)
for dx in (-1.5, 1.5):
    b(conveyors, f"transfer_leg_{dx}", (.12, .12, .90), (-.3+dx, -3.15, .45), silver)
b(conveyors, "foreground_guard", (2.2, .12, .62), (-.3, -4.1, 1.20), light_silver)
scene.include("conveyors", conveyors)

realize(scene)

# World, materials, and lighting are configured after realization.
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

# Reuse the realized materials and set surface response by approximate color.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if not principled:
        continue
    c = principled.inputs["Base Color"].default_value
    if c[0] > .55 and abs(c[0]-c[1]) < .12:
        principled.inputs["Metallic"].default_value = .72
        principled.inputs["Roughness"].default_value = .30
    elif c[1] > c[0]*1.3 and c[1] > .25:
        principled.inputs["Metallic"].default_value = .20
        principled.inputs["Roughness"].default_value = .24
    else:
        principled.inputs["Roughness"].default_value = .48

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((-8, -2, 6.1), power=2200, size=8, target=(0, 3, 1.5))
area_emitter((1, 2, 6.8), power=1600, size=8, target=(0, 2, 0))
area_emitter((6, -4, 6.5), power=1000, size=7, target=(1, 3, 2))

# Actual-camera projection diagnostic. Reference estimates are approximate;
# the points correspond to emitted physical corners, rail ends, and tank top.
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
proj = cam.calc_matrix_camera(depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT,
                              scale_x=1, scale_y=1)
view = cam.matrix_world.inverted()
table = []
for name, xyz, ref in anchors:
    clip = proj @ view @ Vector((xyz[0], xyz[1], xyz[2], 1.0))
    if clip.w <= 0:
        table.append({"name": name, "reference": ref, "projection": None,
                      "residual": None, "behind_camera": True})
    else:
        uv = (0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
        table.append({"name": name, "reference": ref,
                      "projection": [round(v, 4) for v in uv],
                      "residual": [round(uv[i]-ref[i], 4) for i in range(2)],
                      "behind_camera": False})
print("ANCHOR_DIAGNOSTIC " + json.dumps(table, separators=(",", ":")))
