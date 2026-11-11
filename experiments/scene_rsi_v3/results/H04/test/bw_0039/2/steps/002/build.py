# Reference and rendered comparison, normalized image coordinates:
# - Window: reference approximately (.62,.09)-(.93,.43); previous render
#   approximately (.47,.38)-(.61,.54). It is much too small and low.
# - Ladder: reference approximately (.56,.22)-(1,.79); previous render
#   approximately (.46,.42)-(.70,.72). It is too small and leftward.
# - Left doorway: reference runs off the top and bottom near x=.04-.14;
#   previous render is a complete freestanding jamb at x=.12-.19.
# - Debris: reference fills approximately (.27,.74)-(1,1); previous render
#   approximately (.22,.69)-(.79,.81), with too much empty foreground.
# - The reference has near-vertical jambs, a steep ladder sloping right as it
#   rises, dark exposed framing, and a strongly lit patch near the upper left.
#   The ladder overlaps the window and back wall. The room continues beyond the
#   crop; the exact right wall and ceiling are uncertain.
#
# Ranked corrections:
# 1. CAMERA_LENS: increase 26 to 46 mm. Background window and ladder enlarge
#    about the image center; the door jambs and floor crop more strongly.
# 2. CAMERA_TARGET x: move left from .13 to -.55, moving visible room features
#    to the right. CAMERA_TARGET z: lower from 1.47 to 1.05, moving features up.
#    The numerical trial below prints both the old and revised projections.
# 3. Extend wall and floor beyond the camera crop. Darken timber and masonry,
#    strengthen the local warm light, and concentrate longer debris in the
#    foreground. These affect local contours and illumination, not camera aim.
# 4. Broaden the front ladder rails and steps, preserving open gaps, and make
#    the window recess and lower blue pane more distinct.
#
# Approximate expanded primitive count: shell 8, back masonry 115, framing 32,
# window 19, electrical 5, ladder 29, debris 92, lamp 3: about 303 meshes.
# Named assets preserve editable architectural and object groupings.

import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(19)
scene = Scene("Unfinished room")

ROOM_W = 2.55
ROOM_D = 3.45
ROOM_H = 4.2
BACK_Y = 3.45
CAMERA_POSITION = (0.02, -3.95, 1.67)
CAMERA_TARGET = (-0.55, 2.70, 1.05)
CAMERA_LENS = 46.0
OLD_TARGET = (0.13, 2.70, 1.47)
OLD_LENS = 26.0

wood_dark = (.105, .052, .025)
wood_mid = (.27, .145, .065)
wood_light = (.43, .27, .13)
dust = (.32, .30, .245)
metal = (.46, .49, .48)
metal_dark = (.25, .28, .27)
white = (.75, .74, .66)
brick_colors = [
    (.29, .235, .17), (.33, .265, .19), (.27, .215, .15),
    (.36, .285, .205), (.30, .24, .18)
]

def add(parent, name, node):
    parent.include(name, node)

def rail(parent, name, a, b, width, depth, color):
    a, b = Vector(a), Vector(b)
    d = b - a
    mid = (a + b) * .5
    node = box((width, depth, d.length), center=tuple(mid), color=color)
    # A box aligned to its endpoint vector, including its depth component.
    direction = d.normalized()
    quat = Vector((0, 0, 1)).rotation_difference(direction)
    e = quat.to_euler()
    node.turn(euler=tuple(math.degrees(v) for v in e), pivot=tuple(mid))
    add(parent, name, node)

shell = Asset("room_shell")
add(shell, "dusty_floor", box((ROOM_W, 8.0, .10),
    center=(0, 1.0, -.055), color=dust))
add(shell, "back_mortar", box((ROOM_W, .13, ROOM_H),
    center=(0, BACK_Y + .08, ROOM_H / 2), color=(.25,.22,.17)))
add(shell, "left_substrate", box((.12, 5.4, ROOM_H),
    center=(-ROOM_W/2-.06, 1.4, ROOM_H/2), color=(.16,.125,.085)))
add(shell, "right_wall_edge", box((.12, 2.0, ROOM_H),
    center=(ROOM_W/2+.06, -.25, ROOM_H/2), color=(.31,.26,.18)))
add(shell, "left_door_jamb", box((.13,.18,ROOM_H),
    center=(-1.31,-.11,ROOM_H/2), color=(.44,.34,.16)))
add(shell, "left_jamb_inner", box((.055,.20,ROOM_H),
    center=(-1.215,-.12,ROOM_H/2), color=(.57,.46,.23)))
add(shell, "right_door_jamb", box((.095,.18,ROOM_H),
    center=(1.30,-.10,ROOM_H/2), color=(.43,.34,.20)))
add(scene, "architecture", shell)

# The wall is a muted, uneven field of masonry with an open window reveal.
win_l, win_r = -.05, 1.00
win_b, win_t = 1.04, 2.62
bricks = Asset("exposed_back_brick")
course_h = .145
brick_w = .40
for row in range(29):
    z = .065 + row * course_h
    x = -ROOM_W/2 - (brick_w/2 if row % 2 else 0)
    col = 0
    while x < ROOM_W/2:
        xl = max(x, -ROOM_W/2)
        xr = min(x + brick_w - .012, ROOM_W/2)
        intervals = [(xl, xr)]
        if z + course_h/2 > win_b and z - course_h/2 < win_t:
            intervals = []
            if xl < win_l:
                intervals.append((xl, min(xr, win_l)))
            if xr > win_r:
                intervals.append((max(xl, win_r), xr))
        for k, (lo, hi) in enumerate(intervals):
            if hi-lo > .018:
                add(bricks, f"course_{row}_{col}_{k}",
                    box((hi-lo,.025,course_h-.009),
                        center=((lo+hi)/2,BACK_Y-.015,z),
                        color=brick_colors[(row*3+col*7)%len(brick_colors)]))
        x += brick_w
        col += 1
add(scene, "back_wall_bricks", bricks)

framing = Asset("left_exposed_framing")
for i, y in enumerate((-.18,.10,.62,1.15,1.70,2.23,2.78,3.27)):
    add(framing, f"vertical_stud_{i}", box((.105,.105,ROOM_H),
        center=(-1.19,y,ROOM_H/2),
        color=wood_dark if i%2==0 else wood_mid))
add(framing, "lower_plate", box((.12,4.2,.10),
    center=(-1.19,1.35,.08), color=wood_mid))
for i in range(19):
    z = .36 + i*.145
    add(framing, f"remaining_lath_{i}", box((.025,1.40,.035),
        center=(-1.105,2.48,z),
        color=wood_light if i%3 else wood_mid))
add(scene, "left_wall_woodwork", framing)

window = Asset("white_double_hung_window")
wc = (win_l+win_r)/2
ww, wh = win_r-win_l, win_t-win_b
add(window, "dark_reveal", box((ww+.15,.055,wh+.16),
    center=(wc,BACK_Y-.052,(win_b+win_t)/2), color=(.038,.035,.027)))
add(window, "upper_glass", box((ww-.13,.025,(wh-.19)/2),
    center=(wc,BACK_Y-.092,win_b+wh*.735), color=(.035,.10,.125)))
add(window, "lower_glass", box((ww-.13,.025,(wh-.19)/2),
    center=(wc,BACK_Y-.092,win_b+wh*.255), color=(.018,.055,.16)))
for name,x in (("left",win_l+.04),("right",win_r-.04)):
    add(window, name+"_outer_frame", box((.085,.075,wh),
        center=(x,BACK_Y-.12,(win_b+win_t)/2), color=white))
for name,z in (("head",win_t-.04),("sill",win_b+.04),
               ("meeting_rail",win_b+wh*.50)):
    add(window, name, box((ww,.075,.085 if name!="meeting_rail" else .105),
        center=(wc,BACK_Y-.12,z), color=white))
for i in range(10):
    x = win_l+.13+i*(ww-.26)/9
    add(window, f"lower_pane_line_{i}", box((.012,.02,wh*.37),
        center=(x,BACK_Y-.145,win_b+wh*.25), color=(.08,.13,.15)))
add(scene, "window", window)

electrical = Asset("electrical_box_and_conduit")
add(electrical, "white_box", box((.105,.27,.39),
    center=(-1.075,.35,1.52), color=(.72,.72,.66)))
add(electrical, "box_top", box((.11,.28,.025),
    center=(-1.075,.35,1.725), color=(.57,.56,.51)))
add(electrical, "red_cap", box((.06,.095,.025),
    center=(-1.06,.28,1.75), color=(.40,.07,.05)))
add(electrical, "conduit", rod(.014,start=(-1.07,.35,.03),
    end=(-1.07,.35,1.32),color=(.38,.37,.33)))
add(scene, "electrical", electrical)

ladder = Asset("aluminum_folding_ladder")
front_bottom = Vector((.12,1.05,.04))
front_top = Vector((.78,2.32,2.12))
back_bottom = Vector((1.28,2.88,.04))
back_top = Vector((.78,2.32,2.12))
rail_spacing = .42
for side in (-1,1):
    dx = side*rail_spacing/2
    fb = front_bottom + Vector((dx,0,0))
    ft = front_top + Vector((dx,0,0))
    bb = back_bottom + Vector((dx,0,0))
    bt = back_top + Vector((dx,0,0))
    rail(ladder, f"front_rail_{side}", fb, ft, .075,.06,metal)
    rail(ladder, f"rear_rail_{side}", bb, bt, .065,.055,metal_dark)
    add(ladder, f"front_foot_{side}", box((.12,.17,.065),
        center=tuple(fb+Vector((0,0,.025))),color=(.13,.13,.12)))
    add(ladder, f"rear_foot_{side}", box((.12,.16,.065),
        center=tuple(bb+Vector((0,0,.025))),color=(.13,.13,.12)))
for i in range(7):
    t = .15+i*.12
    p = front_bottom.lerp(front_top,t)
    add(ladder, f"front_step_{i}", box((rail_spacing+.035,.105,.035),
        center=(p.x,p.y-.018,p.z),color=metal))
for i in range(4):
    t = .25+i*.18
    p = back_bottom.lerp(back_top,t)
    add(ladder, f"rear_rung_{i}", rod(.021,
        start=(p.x-rail_spacing/2,p.y,p.z),
        end=(p.x+rail_spacing/2,p.y,p.z),color=metal_dark))
for side in (-1,1):
    xoff = side*rail_spacing/2
    add(ladder,f"hinge_{side}",ball(.065,
        center=(front_top.x+xoff,front_top.y,front_top.z),color=metal_dark))
    a = front_bottom.lerp(front_top,.54)+Vector((xoff,0,0))
    b = back_bottom.lerp(back_top,.54)+Vector((xoff,0,0))
    add(ladder,f"spread_brace_{side}",rod(.014,
        start=tuple(a),end=tuple(b),color=metal_dark))
p1 = front_bottom.lerp(front_top,.12)+Vector((-.215,-.04,0))
p2 = front_bottom.lerp(front_top,.36)+Vector((-.215,-.04,0))
rail(ladder,"red_rail_mark",p1,p2,.045,.016,(.52,.065,.035))
add(scene,"ladder",ladder)

debris = Asset("construction_debris")
for i in range(48):
    x = random.uniform(-.95,1.10)
    y = random.uniform(-.45,1.55)
    length = random.uniform(.25,1.15)
    width = random.uniform(.025,.07)
    z = .035 + random.uniform(0,.065)
    board = box((length,width,.025),center=(x,y,z),
        color=random.choice([wood_dark,wood_mid,wood_light]))
    board.turn(axis='+z',degrees=random.uniform(-80,80),pivot=(x,y,z))
    add(debris,f"broken_lath_{i}",board)
for i in range(44):
    x = random.uniform(-1.1,1.1)
    y = random.uniform(-.65,2.1)
    sx, sy = random.uniform(.025,.12), random.uniform(.025,.12)
    h = random.uniform(.015,.06)
    add(debris,f"rubble_{i}",box((sx,sy,h),center=(x,y,h/2),
        color=random.choice([(.43,.39,.30),(.28,.25,.20),(.50,.46,.37)])))
add(scene,"floor_debris",debris)

lamp = Asset("work_light")
add(lamp,"lamp_body",ball(.09,center=(-1.02,1.52,2.63),color=(1,.84,.56)))
add(lamp,"lamp_mount",box((.10,.10,.18),
    center=(-1.12,1.52,2.62),color=metal_dark))
add(scene,"work_lamp",lamp)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 383
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
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.12,.115,.10,1)
background.inputs["Strength"].default_value = .25

landmarks = [
    ("window upper left",(win_l,BACK_Y-.12,win_t),(.62,.09)),
    ("window lower right",(win_r,BACK_Y-.12,win_b),(.93,.43)),
    ("ladder upper hinge",tuple(front_top),(.86,.23)),
    ("ladder front foot",tuple(front_bottom),(.58,.79)),
    ("left doorway base",(-1.215,-.12,.02),(.14,.98)),
]
def print_projections(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(f"{name:24s} reference={ref!s:13s} projected={uv!s}")

# Print the former camera, a small aim trial, and the selected new camera.
set_view(CAMERA_POSITION,OLD_TARGET,lens=OLD_LENS)
print_projections("Previous camera")
set_view(CAMERA_POSITION,(-.05,2.70,1.35),lens=OLD_LENS)
print_projections("Small left/down aim trial")
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
print_projections("Selected camera")

area_emitter((-0.95,1.25,2.65),power=350,size=.25,
    target=(0,2.0,1.2),color=(1.0,.72,.42))
area_emitter((0,-1.2,2.8),power=170,size=2.6,
    target=(0,2,1.2),color=(1.0,.82,.62))
area_emitter((.45,3.2,2.25),power=40,size=1.0,
    target=(0,1.0,1.2),color=(.58,.72,1.0))
