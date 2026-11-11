from sceneact import *
import bpy
import math

# Reference inventory and image anchors (normalized image coordinates):
# Floor fills roughly (0, .50)-(1, 1); its tile lines converge toward (.50, .41).
# Cream walls flank the room; yellow lower bands run from the side edges toward
# the back, with their upper edges sloping toward the central vanishing point.
# The dark stage and green-framed black curtain occupy approximately
# (.38, .24)-(.67, .43), with a green chalkboard at (.48, .33)-(.58, .42).
# Foreground desks occupy (.14, .57)-(.37, .89) and (.51, .53)-(.70, .83).
# Their horizontal tops overlap many smaller desks arranged in rows behind them.
# Blue and black school bags lie under and beside several desks, notably around
# (.64, .68)-(.72, .86) and (.09, .72)-(.18, .91).
# Bright left windows and brown shutters occupy the left wall; brown doors and
# dark wall-mounted speakers punctuate both sides. Ceiling fans and white beams
# occupy the upper portion. Fine details and hidden desk parts are uncertain.
# Dominant edges: wall/floor boundaries and desk rows converge toward the back;
# desk top edges are mostly horizontal. Walls and furniture occlude one another.
#
# Expanded primitive estimate: architecture and stage ~45, tile strips ~55,
# desks and benches ~200, windows/doors ~55, fans/lights ~40, bags ~14;
# total roughly 410 meshes. Each item is an editable SceneAct asset or child.

scene = Scene("Classroom")

# Major dimensions and camera are kept separate for adjustment.
ROOM_W, ROOM_L, ROOM_H = 9.6, 19.0, 4.25
BACK_Y = 9.5
CAM_POS = (0.0, -10.8, 2.65)
CAM_TARGET = (0.0, 5.2, 1.75)
CAM_LENS = 25

cream = (0.84, 0.83, 0.68)
ceiling = (0.85, 0.87, 0.82)
yellow = (0.95, 0.72, 0.025)
floor_col = (0.68, 0.53, 0.36)
grout = (0.56, 0.45, 0.33)
wood = (0.30, 0.19, 0.105)
wood_light = (0.42, 0.28, 0.16)
darkwood = (0.16, 0.105, 0.065)
green = (0.055, 0.27, 0.12)
black = (0.025, 0.026, 0.022)
white = (0.90, 0.90, 0.80)
metal = (0.16, 0.16, 0.14)

def asset(name):
    return Asset(name)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Envelope: the near end is open for the camera.
room = asset("architecture")
add(room, "tiled_floor", (ROOM_W, ROOM_L, .10), (0, 0, -.06), floor_col)
add(room, "left_upper_wall", (.16, ROOM_L, ROOM_H), (-ROOM_W/2, 0, ROOM_H/2), cream)
add(room, "right_upper_wall", (.16, ROOM_L, ROOM_H), (ROOM_W/2, 0, ROOM_H/2), cream)
add(room, "back_wall", (ROOM_W, .16, ROOM_H), (0, BACK_Y, ROOM_H/2), cream)
add(room, "left_yellow_dado", (.18, ROOM_L, 1.17), (-ROOM_W/2+.02, 0, .585), yellow)
add(room, "right_yellow_dado", (.18, ROOM_L, 1.17), (ROOM_W/2-.02, 0, .585), yellow)
add(room, "ceiling", (ROOM_W, ROOM_L, .12), (0, 0, ROOM_H), ceiling)
for i, y in enumerate((-6.3, -1.5, 3.3, 7.8)):
    add(room, "ceiling_beam_%d" % i, (ROOM_W, .22, .22), (0, y, ROOM_H-.12), (0.91, .91, .84))
# Tile joints are thin, flush strips rather than individual floor tiles.
for i in range(19):
    x = -4.5 + i*.5
    add(room, "floor_joint_x_%d" % i, (.014, ROOM_L, .006), (x, 0, .002), grout)
for i in range(38):
    y = -9.25 + i*.5
    add(room, "floor_joint_y_%d" % i, (ROOM_W, .014, .006), (0, y, .003), grout)
scene.include("room", room)

# Small raised teaching platform, green side posts, dark curtain and valance.
stage = asset("stage_and_blackboard")
add(stage, "platform", (5.5, 1.45, .20), (0, 8.45, .10), (0.48, .32, .16))
add(stage, "curtain_recess", (4.4, .12, 2.0), (0, 9.35, 2.30), (.035, .021, .025))
add(stage, "left_green_column", (.34, .22, 2.35), (-2.50, 9.18, 2.17), (.05, .32, .08))
add(stage, "right_green_column", (.34, .22, 2.35), (2.50, 9.18, 2.17), (.05, .32, .08))
add(stage, "top_valance", (4.8, .16, .32), (0, 9.13, 3.38), (.80, .79, .65))
for i in range(9):
    add(stage, "curtain_fold_%d" % i, (.035, .04, 1.48), (-1.95+i*.48, 9.25, 2.23), (.095, .045, .046))
add(stage, "board_frame", (2.02, .12, 1.18), (0, 8.68, 1.64), (.63, .57, .40))
add(stage, "chalkboard", (1.90, .05, 1.06), (0, 8.60, 1.64), (.12, .29, .22))
add(stage, "board_foot_left", (.07, .50, .72), (-.78, 8.73, .60), (.24, .22, .15))
add(stage, "board_foot_right", (.07, .50, .72), (.78, 8.73, .60), (.24, .22, .15))
add(stage, "lectern", (.62, .55, 1.05), (-1.65, 8.35, .73), wood)
add(stage, "blue_chart", (.44, .035, .92), (1.73, 8.87, 1.46), (.22, .69, .81))
scene.include("stage", stage)

# Windows and door panels on the side walls. Bright panels approximate daylight;
# inner frames and shutters remain distinct editable objects.
openings = asset("side_windows_and_doors")
for side in (-1, 1):
    wall_x = side*(ROOM_W/2-.105)
    inside_x = wall_x-side*.025
    for j, y in enumerate((-6.7, -2.8, 1.1, 4.9)):
        if side == 1 and j == 0:
            continue
        add(openings, "%s_window_light_%d" % (side,j),
            (.035, 1.45, 2.23), (inside_x, y, 2.35), (0.95, .96, .81))
        for dy in (-.76, .76):
            add(openings, "%s_window_side_%d_%s" % (side,j,dy),
                (.10, .095, 2.35), (inside_x-side*.04, y+dy, 2.35), wood_light)
        for z in (1.19, 3.50):
            add(openings, "%s_window_rail_%d_%s" % (side,j,z),
                (.10, 1.60, .09), (inside_x-side*.04, y, z), wood_light)
        add(openings, "%s_window_mullion_%d" % (side,j),
            (.10, .07, 2.25), (inside_x-side*.06, y, 2.35), wood_light)
        # One narrow shutter, visible beside each bright opening.
        add(openings, "%s_shutter_%d" % (side,j),
            (.08, .55, 2.20), (inside_x-side*.075, y+.98, 2.30), (.38, .24, .14))
    for j, y in enumerate((-4.7, 3.0, 7.1)):
        add(openings, "%s_door_%d" % (side,j), (.08, 1.0, 2.35),
            (inside_x-side*.06, y, 1.18), (.35, .22, .13))
        add(openings, "%s_door_frame_%d" % (side,j), (.10, .09, 2.45),
            (inside_x-side*.09, y-.54, 1.22), (.23, .16, .10))
scene.include("windows_and_doors", openings)

# Wooden desks, with open space below tops and legs visible through gaps.
def desk(name, x, y, width=1.45, depth=.72, height=.78):
    d = asset(name)
    add(d, "desktop", (width, depth, .085), (x, y, height), wood)
    add(d, "front_apron", (width-.08, .055, .22),
        (x, y-depth/2+.04, height-.16), wood_light)
    for ix, xx in enumerate((x-width/2+.09, x+width/2-.09)):
        for iy, yy in enumerate((y-depth/2+.07, y+depth/2-.07)):
            add(d, "leg_%d_%d" % (ix,iy), (.075, .075, height-.05),
                (xx, yy, (height-.05)/2), wood_light)
    return d

def bench(name, x, y, width=1.25):
    b = asset(name)
    add(b, "seat", (width, .27, .055), (x, y, .46), darkwood)
    for i, xx in enumerate((x-width/2+.12, x+width/2-.12)):
        add(b, "leg_%d" % i, (.055, .055, .43), (xx, y, .22), wood_light)
    return b

# Four columns leave a central aisle, and rows recede to the stage.
for r, y in enumerate((-5.3, -2.8, -.3, 2.2, 4.7, 6.7)):
    for c, x in enumerate((-3.65, -1.35, 1.35, 3.65)):
        # The nearest outermost desk is partially beyond the photograph.
        w = 1.48 if abs(x) < 2 else 1.25
        scene.include("desk_%d_%d" % (r,c), desk("desk", x, y, w))
        if r < 4:
            scene.include("bench_%d_%d" % (r,c), bench("bench", x, y+.62, w-.12))

# Bags: broad irregular silhouette constructed from a main soft body and pocket.
def bag(name, x, y, color, tilt=0):
    a = asset(name)
    add(a, "main_body", (.42, .25, .55), (x, y, .29), color)
    add(a, "rounded_top", (.34, .24, .12), (x, y, .59), color)
    add(a, "front_pocket", (.30, .055, .25), (x, y-.15, .23),
        tuple(max(0, v*.72) for v in color))
    add(a, "strap", (.055, .12, .45), (x+.23, y+.02, .23), (.025, .03, .035))
    if tilt:
        a.turn(axis="+y", degrees=tilt, pivot=(x,y,0))
    return a
scene.include("blue_foreground_bag", bag("blue_bag", 2.08, -6.0, (.025,.27,.52), -8))
scene.include("black_foreground_bag", bag("black_bag", -3.25, -6.8, (.025,.04,.055), 8))
scene.include("black_middle_bag", bag("black_bag", .12, -3.8, (.035,.045,.04), -7))
scene.include("blue_right_bag", bag("blue_bag", 4.05, -3.05, (.025,.32,.48), 12))

# Dark wall-mounted loudspeakers, picture frames and fluorescent fittings.
details = asset("wall_and_ceiling_details")
for side, y in ((-1, 2.5), (1, 1.5)):
    add(details, "speaker_%s" % side, (.32, .70, .66),
        (side*4.55, y, 3.18), (.045, .065, .065))
for side, y in ((-1,-5.0), (1,-5.3), (1,5.8)):
    add(details, "picture_frame_%s_%s" % (side,y), (.07,.58,.60),
        (side*4.68,y,3.45), (.27,.31,.28))
    add(details, "picture_face_%s_%s" % (side,y), (.075,.47,.49),
        (side*4.64,y,3.45), (.77,.80,.70))
for i, y in enumerate((-3.8, 1.4, 6.2)):
    add(details, "fluorescent_%d" % i, (1.45,.12,.07), (0,y,4.05), (.93,.94,.88))
scene.include("details", details)

# Ceiling fans: compact hubs, suspension rods, and flat four-bladed silhouettes.
for i, (x,y) in enumerate(((-2.65,-5.5),(2.55,-5.0),(-2.2,1.3),(2.4,2.2),(0,6.4))):
    fan = asset("ceiling_fan_%d" % i)
    fan.include("stem", rod(.025, start=(x,y,4.18), end=(x,y,3.70), color=metal))
    fan.include("hub", ball(.12, center=(x,y,3.68), color=metal))
    for k in range(4):
        angle = k*math.pi/2 + .25
        blade = box((1.05,.13,.035),
                    center=(x+.55*math.cos(angle), y+.55*math.sin(angle),3.68),
                    color=(.19,.18,.15))
        blade.turn(axis="+z", degrees=math.degrees(angle))
        fan.include("blade_%d" % k, blade)
    scene.include("fan_%d" % i, fan)

realize(scene)

# Establish the world explicitly after realization.
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
background.inputs["Color"].default_value = (0.78, 0.82, 0.78, 1)
background.inputs["Strength"].default_value = .7

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0, -2, 3.9), power=1000, size=8, target=(0,1,0))
area_emitter((-3, 3, 3.6), power=700, size=6, target=(0,3,0))
area_emitter((2, 7, 3.7), power=450, size=4, target=(0,7,0))
