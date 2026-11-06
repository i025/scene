from sceneact import *
import bpy
import math

# Reference inventory, estimated normalized image bounds:
# - Dark steel hall and ribbed roof: entire upper frame; columns and beams cross
#   the ceiling. Tall windows line the left wall, approximately x=0.00–0.24.
# - Stainless processing equipment and elevated platforms: x=0.23–0.94,
#   y=0.29–0.81. Largest machine is right of center; smaller units continue left.
# - Yellow platform guardrails, stairs and supports: x=0.08–0.96, y=0.43–0.98.
#   The foreground stairs overlap equipment and platform legs.
# - Silver ducts and pipe elbows: x=0.29–0.83, y=0.21–0.54; some connections
#   are hidden behind the equipment.
# - Green vertical tank: x=0.36–0.45, y=0.53–0.78, in front of the platform.
# - Blue and silver conveyor equipment: x=0.00–0.70, y=0.72–1.00, partly
#   cropped at the bottom. Green epoxy floor is visible between its supports.
# - Additional equipment at the far right is partly occluded and uncertain.
#
# Approximate expanded primitive count: hall 70, machines and platforms 60,
# rails and stairs 115, ducts and hangers 35, tank 10, conveyors 75:
# about 365 separate primitive meshes. Sweep tubes expand to 2*n-1 primitives.
# Equipment dimensions, repetitions and positions remain explicit below.

scene = Scene("Workshop reconstruction")

steel = (0.18, 0.21, 0.22)
steel_edge = (0.29, 0.32, 0.32)
roof = (0.23, 0.25, 0.25)
wall = (0.35, 0.37, 0.37)
glass = (0.66, 0.82, 0.88)
floor_color = (0.12, 0.34, 0.27)
yellow = (0.95, 0.65, 0.025)
yellow_dark = (0.73, 0.48, 0.015)
silver = (0.67, 0.70, 0.69)
silver_light = (0.79, 0.81, 0.79)
silver_dark = (0.37, 0.41, 0.40)
dark = (0.16, 0.19, 0.19)
blue = (0.07, 0.28, 0.62)
green = (0.015, 0.36, 0.24)
white = (0.79, 0.83, 0.81)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# Building: floor, distant wall, side windows, roof and steel framing.
hall = Asset("steel_frame_hall")
add_box(hall, "green_epoxy_floor", (24, 27, .12), (0, 4, -.07), floor_color)
add_box(hall, "left_wall", (.20, 27, 6.3), (-10, 4, 3.15), wall)
add_box(hall, "far_wall", (20, .20, 6.3), (0, 17.4, 3.15), wall)
add_box(hall, "roof_deck", (20.5, 27, .16), (0, 4, 6.45), roof)

# Bright vertical daylight strips against the left side wall.
for i, y in enumerate([-7.7, -4.7, -1.7, 1.3, 4.3, 7.3, 10.3, 13.3, 16.1]):
    add_box(hall, "window_%02d" % i, (.035, 1.05, 3.0),
            (-9.88, y, 2.75), glass)
    for z in (1.28, 2.1, 3.15, 4.22):
        add_box(hall, "window_crossbar_%02d_%s" % (i, z),
                (.08, 1.09, .045), (-9.82, y, z), steel)
    add_box(hall, "window_mullion_%02d" % i, (.08, .045, 3.0),
            (-9.82, y, 2.75), steel)

# Posts and beams are deliberately substantial and visibly connected.
for i, y in enumerate([-8, -2.8, 2.4, 7.6, 12.8, 17.2]):
    for x in (-9.7, 9.7):
        add_box(hall, "column_%02d_%s" % (i, x), (.23, .24, 6.3),
                (x, y, 3.15), steel)
        add_box(hall, "column_flange_%02d_%s" % (i, x), (.42, .11, 6.3),
                (x, y, 3.15), steel_edge)
    add_box(hall, "roof_crossbeam_%02d" % i, (19.5, .28, .34),
            (0, y, 6.12), steel)
for i, x in enumerate([-8.2, -5.0, -1.8, 1.4, 4.6, 7.8]):
    add_box(hall, "longitudinal_purlin_%02d" % i, (.12, 25, .16),
            (x, 4, 6.29), steel_edge)
for i, y in enumerate([-4, 3, 10, 16]):
    add_box(hall, "ceiling_light_%02d" % i, (2.0, .12, .025),
            (-1, y, 6.31), white)
scene.include("building", hall)

# Platform structure and enclosed machine bodies.
platform = Asset("processing_platforms")
add_box(platform, "main_platform_deck", (12.9, 3.0, .18),
        (.2, 3.7, 2.13), silver_dark)
for x in [-5.8, -2.8, .2, 3.2, 6.2]:
    for y in [2.35, 5.05]:
        add_box(platform, "platform_leg_%s_%s" % (x, y), (.16, .16, 2.05),
                (x, y, 1.05), silver_dark)
add_box(platform, "front_platform_beam", (12.9, .19, .27),
        (.2, 2.26, 1.96), silver)
add_box(platform, "rear_platform_beam", (12.9, .19, .27),
        (.2, 5.14, 1.96), silver)

# Individual machines have bodies, dark process openings and metallic lower frames.
machine_specs = [
    ("left_machine", -4.25, 3.85, 2.7, 2.0, 1.5),
    ("middle_machine", -1.10, 4.05, 2.6, 1.9, 1.35),
    ("large_machine", 3.15, 3.95, 3.5, 2.15, 2.25),
    ("far_right_machine", 7.25, 5.0, 1.55, 1.8, 1.75),
]
for name, x, y, w, d, h in machine_specs:
    unit = Asset(name)
    bottom = 2.24
    add_box(unit, "main_stainless_body", (w, d, h),
            (x, y, bottom + h/2), silver)
    add_box(unit, "upper_housing", (w*.91, d*.88, .22),
            (x, y, bottom + h + .10), silver_light)
    add_box(unit, "front_process_opening", (w*.82, .035, h*.34),
            (x, y-d/2-.025, bottom+h*.51), dark)
    add_box(unit, "front_lower_panel", (w*.88, .055, h*.23),
            (x, y-d/2-.05, bottom+h*.20), silver_light)
    for j in range(4):
        add_box(unit, "opening_slat_%d" % j, (w*.78, .035, .045),
                (x, y-d/2-.055, bottom+h*(.40+j*.07)), silver_dark)
    add_box(unit, "control_box", (.34, .18, .52),
            (x+w*.38, y-d/2-.12, bottom+h*.71), white)
    platform.include(name, unit)
scene.include("platform_and_machines", platform)

# Yellow safety rails along the main platform, with top and intermediate rails.
rails = Asset("yellow_platform_guardrails")
for i in range(16):
    x = -6.15 + i*.84
    add_rod(rails, "front_post_%02d" % i, (x, 2.19, 2.22),
            (x, 2.19, 3.25), .032, yellow)
for z in (2.70, 3.23):
    add_rod(rails, "front_horizontal_%s" % z,
            (-6.25, 2.19, z), (6.45, 2.19, z), .035, yellow)
for y in (2.25, 3.0, 3.75, 4.5, 5.15):
    add_rod(rails, "end_post_%s" % y, (6.48, y, 2.2),
            (6.48, y, 3.25), .032, yellow)
for z in (2.70, 3.23):
    add_rod(rails, "end_horizontal_%s" % z,
            (6.48, 2.2, z), (6.48, 5.15, z), .035, yellow)
for x in (-5.9, -3.7, -1.5, .7, 2.9, 5.1, 6.4):
    add_rod(rails, "rear_post_%s" % x, (x, 5.18, 2.2),
            (x, 5.18, 3.2), .028, yellow)
add_rod(rails, "rear_top_rail", (-6.1, 5.18, 3.2),
        (6.45, 5.18, 3.2), .032, yellow)
scene.include("platform_guardrails", rails)

# Inclined stairs at left and right, descending toward the camera.
def make_stair(name, x, front_y, back_y, width, height, steps):
    stair = Asset(name)
    for side in (-1, 1):
        sx = x + side*width/2
        add_rod(stair, "stringer_%s" % side,
                (sx, front_y, .12), (sx, back_y, height), .055, silver_dark)
        add_rod(stair, "handrail_%s" % side,
                (sx, front_y, 1.10), (sx, back_y, height+1.0), .038, yellow)
        add_rod(stair, "midrail_%s" % side,
                (sx, front_y, .62), (sx, back_y, height+.50), .028, yellow)
        for j in range(4):
            t = j/3
            yy = front_y + (back_y-front_y)*t
            zz = .12 + (height-.12)*t
            add_rod(stair, "railing_post_%s_%d" % (side, j),
                    (sx, yy, zz), (sx, yy, zz+1.0), .027, yellow)
    for j in range(steps):
        t = (j+.5)/steps
        yy = front_y+(back_y-front_y)*t
        zz = .12+(height-.12)*t
        add_box(stair, "tread_%02d" % j, (width, .27, .055),
                (x, yy, zz), silver_light)
    return stair

scene.include("left_access_stair", make_stair("left_access_stair",
              -4.9, -1.0, 2.2, 1.0, 2.18, 9))
scene.include("middle_access_stair", make_stair("middle_access_stair",
              -.6, -.85, 2.2, .95, 2.18, 9))
scene.include("right_access_stair", make_stair("right_access_stair",
              6.0, -1.15, 2.2, 1.05, 2.18, 9))

# Insulated ducts: short bent paths retain the prominent silhouettes.
ducts = Asset("insulated_ductwork")
ducts.include("left_duct", sweep_tube(
    points=[(-4.3,4.1,3.95), (-4.3,4.1,5.0), (-3.95,4.1,5.25),
            (-2.65,4.1,5.25), (-2.30,4.1,4.55)],
    radius=.19, color=silver_light))
ducts.include("large_duct", sweep_tube(
    points=[(3.0,4.1,4.52), (3.0,4.1,5.58), (3.3,4.1,5.78),
            (4.25,4.1,5.45), (4.25,4.1,4.50)],
    radius=.23, color=silver_light))
add_rod(ducts, "horizontal_process_pipe", (-5.8,5.3,4.55),
        (6.8,5.3,4.55), .11, silver)
add_rod(ducts, "lower_cross_pipe", (-5.8,2.5,1.45),
        (6.8,2.5,1.45), .08, silver_light)
for i, x in enumerate([-4.0, -1.0, 2.0, 5.0]):
    add_rod(ducts, "overhead_hanger_%d" % i, (x,5.3,4.55),
            (x,5.3,6.12), .025, silver_dark)
scene.include("ducts_and_process_piping", ducts)

# Green vertical process tank with domed ends, feet and top connection.
tank = Asset("green_vertical_tank")
tx, ty = -2.35, -.55
add_rod(tank, "cylindrical_shell", (tx,ty,.55), (tx,ty,2.05), .49, green)
tank.include("upper_dome", ball(radius=.49, center=(tx,ty,2.05), color=green))
tank.include("lower_dome", ball(radius=.49, center=(tx,ty,.55), color=green))
add_rod(tank, "top_nozzle", (tx,ty,2.44), (tx,ty,2.68), .075, silver)
add_rod(tank, "top_flange", (tx,ty,2.61), (tx,ty,2.66), .15, silver_dark)
for i, (dx,dy) in enumerate([(-.27,-.22),(.27,-.22),(-.27,.22),(.27,.22)]):
    add_rod(tank, "leg_%d" % i, (tx+dx,ty+dy,.05),
            (tx+dx,ty+dy,.65), .045, silver_dark)
scene.include("green_tank", tank)

# Foreground conveyor runs. The large blue belts and pale support frames occupy
# the lower image; shallow crossbars describe rollers without subpixel detail.
conveyor = Asset("foreground_conveyor_system")
def conveyor_run(name, cx, cy, length, width, z, along_x=True):
    part = Asset(name)
    if along_x:
        add_box(part, "blue_belt", (length,width,.10), (cx,cy,z), blue)
        for side in (-1,1):
            add_box(part, "side_rail_%s" % side, (length,.09,.19),
                    (cx,cy+side*width/2,z+.07), silver_light)
        for i in range(10):
            x = cx-length/2+(i+.5)*length/10
            add_rod(part, "roller_%02d" % i,
                    (x,cy-width*.48,z+.075), (x,cy+width*.48,z+.075),
                    .025, silver_light)
        for dx in (-length*.38, length*.38):
            for dy in (-width*.4,width*.4):
                add_box(part, "support_%s_%s" % (dx,dy), (.07,.07,z-.04),
                        (cx+dx,cy+dy,(z-.04)/2), silver)
    else:
        add_box(part, "blue_belt", (width,length,.10), (cx,cy,z), blue)
        for side in (-1,1):
            add_box(part, "side_rail_%s" % side, (.09,length,.19),
                    (cx+side*width/2,cy,z+.07), silver_light)
        for i in range(8):
            y = cy-length/2+(i+.5)*length/8
            add_rod(part, "roller_%02d" % i,
                    (cx-width*.48,y,z+.075), (cx+width*.48,y,z+.075),
                    .025, silver_light)
        for dx in (-width*.4,width*.4):
            for dy in (-length*.38,length*.38):
                add_box(part, "support_%s_%s" % (dx,dy), (.07,.07,z-.04),
                        (cx+dx,cy+dy,(z-.04)/2), silver)
    conveyor.include(name, part)

conveyor_run("front_blue_conveyor", -3.8, -5.15, 8.8, 1.05, .76)
conveyor_run("second_blue_conveyor", -3.5, -3.65, 8.2, .85, .82)
conveyor_run("transfer_conveyor", .0, -2.4, 3.7, .75, .89, False)
# Silver sheet enclosures and guides around the transfer section.
add_box(conveyor, "transfer_housing", (2.1,1.15,.65), (-.35,-2.5,.92), silver_light)
add_box(conveyor, "transfer_top_opening", (1.65,.75,.04), (-.35,-2.5,1.26), silver_dark)
add_box(conveyor, "small_motor", (.48,.32,.32), (1.0,-2.4,.50), dark)
scene.include("conveyor_line", conveyor)

realize(scene)

# World and lighting are configured after realization, which clears Blender.
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
background.inputs["Color"].default_value = (0.71, 0.79, 0.83, 1)
background.inputs["Strength"].default_value = .48

# Match material families by their source colors while retaining editable parts.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if abs(r-floor_color[0]) < .025 and abs(g-floor_color[1]) < .025:
        bsdf.inputs["Roughness"].default_value = .20
        bsdf.inputs["Metallic"].default_value = .12
    elif abs(r-green[0]) < .025 and abs(g-green[1]) < .025:
        bsdf.inputs["Roughness"].default_value = .32
        bsdf.inputs["Metallic"].default_value = .30
    elif abs(r-g) < .10 and abs(g-b) < .10 and r > .34:
        bsdf.inputs["Metallic"].default_value = .70
        bsdf.inputs["Roughness"].default_value = .29
    elif r > .65 and g > .38 and b < .15:
        bsdf.inputs["Metallic"].default_value = .35
        bsdf.inputs["Roughness"].default_value = .36

set_view((8.4, -20.7, 7.8), (0.0, 2.6, 2.75), lens=32, sensor=36)
area_emitter((-8, -2, 5.1), power=1800, size=7,
             target=(0, 2, 1.8), color=(.84,.91,1.0))
area_emitter((1, 2.5, 6.15), power=1500, size=7,
             target=(0, 2, 0), color=(1.0,.97,.92))
area_emitter((7, -7, 5.5), power=1100, size=6,
             target=(0, 2, 2), color=(1.0,1.0,1.0))

# The external runner owns rendering and saving; the scene requests the specified
# renderer, color management and output dimensions without writing any files.
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "AgX"
except TypeError:
    sc.view_settings.view_transform = "Filmic"
