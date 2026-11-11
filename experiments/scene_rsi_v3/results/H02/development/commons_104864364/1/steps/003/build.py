from sceneact import *
import bpy
import math

# Visual estimates, normalized to the 512 x 340 reference:
# Reference stage and green pillars: x .38-.67, y .24-.43; rendered:
# approximately x .38-.62, y .34-.54. Reference board: x .48-.58,
# y .33-.42; rendered: x .45-.54, y .40-.48.
# Reference foreground desk tops: x .14-.36 and .51-.70, y .55-.65;
# rendered: x .18-.39 and .53-.72, y .70-.78. The reference blue bag
# is around x .64-.72, y .68-.86; rendered around x .69-.77, y .79-.96.
# Reference ceiling fans touch the top crop; rendered hubs are around y .16.
# Reference desk rows overlap densely, but retain open leg gaps; the render
# has similar converging edges but fewer dark overlaps and a wide foreground.
# Side openings, furniture behind desks, and bag straps are partly occluded.
#
# Largest differences: (1) common downward displacement of the stage, desk
# tops and fans; (2) stage is too narrow and its board is left of center;
# (3) foreground desks are too low and the left black bag is outside the crop.
# Lower CAM_TARGET raises room features in the frame. Increase STAGE_SCALE
# and shift STAGE_X right to widen and center its dark backdrop and board.
# Move foreground desks and bags slightly farther away to raise their contours
# and avoid cropping; move the left bag inward. Restore edge desks farther back.
# Darken desktop material and retain warm floor and yellow wall regions;
# their apparent brightness also depends on lighting and surface orientation.
# Expanded primitive estimate: room 68, stage 21, openings 61, desks 144,
# benches 48, bags 20, details 13, fans 30, total approximately 405 meshes.

scene = Scene("Classroom")
ROOM_W, ROOM_L, ROOM_H = 9.6, 19.0, 4.25
CAM_POS = (.38, -10.8, 2.65)
CAM_TARGET = (.38, 5.2, .12)
CAM_LENS = 25
STAGE_SCALE = 1.52
STAGE_X = .65

cream = (.84, .83, .68)
ceiling = (.86, .87, .81)
yellow = (.98, .72, .015)
floor_col = (.73, .61, .46)
grout = (.65, .54, .42)
wood = (.15, .085, .042)
wood_light = (.28, .17, .09)
darkwood = (.11, .065, .035)
metal = (.13, .13, .12)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

room = Asset("architecture")
add(room, "floor", (ROOM_W, ROOM_L, .10), (0, 0, -.06), floor_col)
add(room, "left_wall", (.16, ROOM_L, ROOM_H), (-4.8, 0, ROOM_H/2), cream)
add(room, "right_wall", (.16, ROOM_L, ROOM_H), (4.8, 0, ROOM_H/2), cream)
add(room, "back_wall", (ROOM_W, .16, ROOM_H), (0, 9.5, ROOM_H/2), cream)
add(room, "left_yellow_band", (.18, ROOM_L, 1.17), (-4.78, 0, .585), yellow)
add(room, "right_yellow_band", (.18, ROOM_L, 1.17), (4.78, 0, .585), yellow)
add(room, "ceiling", (ROOM_W, ROOM_L, .12), (0, 0, ROOM_H), ceiling)
for i, y in enumerate((-6.3, -1.5, 3.3, 7.8)):
    add(room, "ceiling_beam_%d" % i, (ROOM_W, .22, .22),
        (0, y, ROOM_H-.12), (.91, .91, .84))
for i in range(19):
    add(room, "floor_joint_x_%d" % i, (.009, ROOM_L, .006),
        (-4.5+i*.5, 0, .002), grout)
for i in range(38):
    add(room, "floor_joint_y_%d" % i, (ROOM_W, .009, .006),
        (0, -9.25+i*.5, .003), grout)
scene.include("room", room)

stage = Asset("stage_and_blackboard")
def stagebox(name, size, center, color):
    add(stage, name, (size[0]*STAGE_SCALE, size[1], size[2]),
        (STAGE_X+center[0]*STAGE_SCALE, center[1], center[2]), color)
stagebox("platform", (5.0, 1.45, .20), (0, 8.45, .10), (.48, .32, .16))
stagebox("dark_curtain", (4.4, .12, 2.0), (0, 9.35, 2.30), (.022, .012, .015))
stagebox("left_green_column", (.34, .22, 2.35), (-2.50, 9.18, 2.17), (.025, .30, .045))
stagebox("right_green_column", (.34, .22, 2.35), (2.50, 9.18, 2.17), (.025, .30, .045))
stagebox("top_valance", (4.8, .16, .32), (0, 9.13, 3.38), (.83, .81, .68))
for i in range(9):
    stagebox("curtain_fold_%d" % i, (.035, .04, 1.48),
             (-1.95+i*.48, 9.25, 2.23), (.07, .025, .028))
# The board is narrower relative to the enlarged backdrop.
stagebox("board_frame", (1.75, .12, 1.18), (0, 8.68, 1.64), (.63, .57, .40))
stagebox("chalkboard", (1.65, .05, 1.06), (0, 8.60, 1.64), (.10, .27, .20))
stagebox("board_left_support", (.07, .50, .72), (-.70, 8.73, .60), (.24, .22, .15))
stagebox("board_right_support", (.07, .50, .72), (.70, 8.73, .60), (.24, .22, .15))
stagebox("lectern", (.62, .55, 1.05), (-1.65, 8.35, .73), wood)
stagebox("blue_chart", (.44, .035, .92), (1.73, 8.87, 1.46), (.22, .69, .81))
scene.include("stage", stage)

openings = Asset("side_windows_and_doors")
for side in (-1, 1):
    inside_x = side*(ROOM_W/2-.13)
    for j, y in enumerate((-6.7, -2.8, 1.1, 4.9)):
        if side == 1 and j == 0:
            continue
        add(openings, "window_light_%s_%d" % (side,j),
            (.035, 1.45, 2.23), (inside_x, y, 2.35), (.98, .98, .87))
        for k, dy in enumerate((-.76, .76)):
            add(openings, "window_side_%s_%d_%d" % (side,j,k),
                (.10, .095, 2.35), (inside_x-side*.04, y+dy, 2.35), wood_light)
        for k, z in enumerate((1.19, 3.50)):
            add(openings, "window_rail_%s_%d_%d" % (side,j,k),
                (.10, 1.60, .09), (inside_x-side*.04, y, z), wood_light)
        add(openings, "window_mullion_%s_%d" % (side,j),
            (.10, .07, 2.25), (inside_x-side*.06, y, 2.35), wood_light)
        add(openings, "shutter_%s_%d" % (side,j),
            (.08, .55, 2.20), (inside_x-side*.075, y+.98, 2.30), (.38, .24, .14))
    for j, y in enumerate((-4.7, 3.0, 7.1)):
        add(openings, "door_%s_%d" % (side,j), (.08, 1.0, 2.35),
            (inside_x-side*.06, y, 1.18), (.35, .22, .13))
        add(openings, "door_frame_%s_%d" % (side,j), (.10, .09, 2.45),
            (inside_x-side*.09, y-.54, 1.22), (.23, .16, .10))
scene.include("windows_and_doors", openings)

def desk(name, x, y, width=1.45, depth=.72, height=.78):
    d = Asset(name)
    add(d, "desktop", (width, depth, .085), (x, y, height), wood)
    add(d, "front_apron", (width-.08, .055, .16),
        (x, y-depth/2+.04, height-.13), wood_light)
    for ix, xx in enumerate((x-width/2+.09, x+width/2-.09)):
        for iy, yy in enumerate((y-depth/2+.07, y+depth/2-.07)):
            add(d, "leg_%d_%d" % (ix,iy), (.065, .065, height-.05),
                (xx, yy, (height-.05)/2), wood_light)
    return d

def bench(name, x, y, width=1.25):
    b = Asset(name)
    add(b, "seat", (width, .27, .055), (x, y, .46), darkwood)
    for i, xx in enumerate((x-width/2+.12, x+width/2-.12)):
        add(b, "leg_%d" % i, (.055, .055, .43), (xx, y, .22), wood_light)
    return b

for r, y in enumerate((-4.7, -2.5, -.3, 2.2, 4.7, 6.7)):
    for c, x in enumerate((-3.65, -1.35, 1.35, 3.65)):
        # Outer desks sit farther back, as visible along the side walls.
        yy = y + (.8 if r == 0 and c in (0, 3) else 0)
        w = 1.48 if abs(x) < 2 else 1.25
        scene.include("desk_%d_%d" % (r,c), desk("desk", x, yy, w))
        if r < 4:
            scene.include("bench_%d_%d" % (r,c), bench("bench", x, yy+.62, w-.12))

def bag(name, x, y, color, tilt=0):
    a = Asset(name)
    add(a, "main_body", (.42, .25, .55), (x, y, .29), color)
    add(a, "rounded_top", (.34, .24, .12), (x, y, .59), color)
    add(a, "front_pocket", (.30, .055, .25), (x, y-.15, .23),
        tuple(max(0, v*.72) for v in color))
    add(a, "strap", (.055, .12, .45), (x+.23, y+.02, .23), (.025, .03, .035))
    if tilt:
        a.turn(axis="+y", degrees=tilt, pivot=(x,y,0))
    return a
scene.include("blue_foreground_bag", bag("blue_bag", 1.90, -5.3, (.025,.27,.52), -8))
scene.include("black_foreground_bag", bag("black_bag", -2.85, -5.8, (.025,.04,.055), 8))
scene.include("black_middle_bag", bag("black_bag", .12, -3.8, (.035,.045,.04), -7))
scene.include("blue_right_bag", bag("blue_bag", 4.05, -3.05, (.025,.32,.48), 12))

details = Asset("wall_and_ceiling_details")
for side, y in ((-1, 2.5), (1, 1.5)):
    add(details, "speaker_%s" % side, (.32, .70, .66),
        (side*4.55, y, 3.18), (.025, .045, .045))
for side, y in ((-1,-5.0), (1,-5.3), (1,5.8)):
    add(details, "picture_frame_%s_%s" % (side,y), (.07,.58,.60),
        (side*4.68,y,3.45), (.27,.31,.28))
    add(details, "picture_face_%s_%s" % (side,y), (.075,.47,.49),
        (side*4.64,y,3.45), (.77,.80,.70))
for i, y in enumerate((-3.8, 1.4, 6.2)):
    add(details, "fluorescent_%d" % i, (1.45,.12,.07),
        (0,y,4.05), (.93,.94,.88))
scene.include("details", details)

for i, (x,y) in enumerate(((-2.65,-5.5),(2.55,-5.0),(-2.2,1.3),(2.4,2.2),(0,6.4))):
    fan = Asset("ceiling_fan_%d" % i)
    fan.include("stem", rod(.025, start=(x,y,4.18), end=(x,y,3.70), color=metal))
    fan.include("hub", ball(.12, center=(x,y,3.68), color=metal))
    for k in range(4):
        angle = k*math.pi/2 + .25
        blade = box((1.05,.13,.035),
                    center=(x+.55*math.cos(angle), y+.55*math.sin(angle),3.68),
                    color=(.16,.15,.13))
        blade.turn(axis="+z", degrees=math.degrees(angle))
        fan.include("blade_%d" % k, blade)
    scene.include("fan_%d" % i, fan)

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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.78, .82, .78, 1)
background.inputs["Strength"].default_value = .7

set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0, -2, 3.9), power=1000, size=8, target=(0,1,0))
area_emitter((-3, 3, 3.6), power=700, size=6, target=(0,3,0))
area_emitter((2, 7, 3.7), power=450, size=4, target=(0,7,0))
