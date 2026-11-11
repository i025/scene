# Reference inventory and anchors (normalized image coordinates, x right, y down):
# - Narrow unfinished room, doorway edges at x~0.04 and x~0.97; floor begins
#   around y~0.64 at the rear and fills the foreground.
# - Back wall and white double-hung window: outer window bounds approximately
#   (0.62, 0.09)-(0.93, 0.43); dark reveal, white sash and blue-dark glass.
# - Exposed left wall framing occupies x~0.16-0.47, with vertical dark studs,
#   narrow pale laths and a white electrical box around (0.15,0.36)-(0.25,0.49).
# - Aluminum folding ladder occupies roughly (0.56,0.22)-(0.99,0.79).
#   Its front rails slope from lower left to upper right; rear legs descend
#   toward the right edge. Rungs cross the open center.
# - Foreground debris occupies approximately (0.27,0.74)-(0.95,0.98):
#   scattered broken brown laths over pale rubble and dusty floor.
# - A bright warm work light near (0.38,0.12) overlaps the left studs. The
#   structure immediately behind it and the right side of the room are uncertain.
# - Dominant edges: vertical door jambs and studs; horizontal back-wall brick
#   courses and window sash; ladder rails rise steeply to the right.
# Approximate primitive count: architecture 18, brick courses 105, studs/laths 30,
# window 16, ladder 31, debris 60, light and electrical box 7: ~267 total.
# The brick surface uses simple geometry, not a photograph or projected texture.

import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(19)
scene = Scene("Unfinished room")

# Parameters are kept separate so room and camera can be adjusted independently.
ROOM_W = 2.55
ROOM_D = 3.45
ROOM_H = 3.02
BACK_Y = 3.45
CAMERA_POSITION = (0.02, -3.95, 1.67)
CAMERA_TARGET = (0.13, 2.70, 1.47)
CAMERA_LENS = 26.0

mortar = (0.30, 0.255, 0.195)
brick_colors = [
    (0.36, 0.265, 0.18), (0.40, 0.30, 0.215),
    (0.33, 0.245, 0.17), (0.44, 0.335, 0.24),
    (0.37, 0.285, 0.22)
]
wood_dark = (0.20, 0.105, 0.055)
wood_mid = (0.38, 0.235, 0.13)
wood_light = (0.54, 0.39, 0.235)
dust = (0.46, 0.43, 0.36)
metal = (0.57, 0.60, 0.59)
metal_dark = (0.30, 0.33, 0.32)
white = (0.81, 0.79, 0.69)
glass = (0.035, 0.105, 0.16)

def add(parent, name, node):
    parent.include(name, node)

def plank_between(parent, name, a, b, width, thickness, color):
    # Slim squared strip with its long axis between a and b.
    a, b = Vector(a), Vector(b)
    delta = b - a
    length = delta.length
    if length <= 1e-5:
        return
    mid = (a + b) * 0.5
    obj = box((width, thickness, length), center=tuple(mid), color=color)
    # SceneAct rotations follow XYZ Euler angles. A direction in the XZ plane
    # is represented by its inclination about Y.
    angle = math.degrees(math.atan2(delta.x, delta.z))
    obj.turn(axis='+y', degrees=angle, pivot=tuple(mid))
    add(parent, name, obj)

# Architectural shell, kept open toward the camera.
shell = Asset("room_shell")
add(shell, "dusty_floor", box((ROOM_W, ROOM_D + 1.3, .10),
    center=(0, 1.75, -.055), color=dust))
add(shell, "back_mortar", box((ROOM_W, .13, ROOM_H),
    center=(0, BACK_Y + .08, ROOM_H/2), color=mortar))
add(shell, "left_substrate", box((.12, ROOM_D, ROOM_H),
    center=(-ROOM_W/2-.06, ROOM_D/2, ROOM_H/2), color=(.27,.22,.16)))
# Right wall mostly outside the photograph, with a visible near jamb.
add(shell, "right_wall_edge", box((.12, 1.1, ROOM_H),
    center=(ROOM_W/2+.06, .05, ROOM_H/2), color=(.38,.31,.21)))
add(shell, "left_door_jamb", box((.13,.18,ROOM_H),
    center=(-1.31,-.11,ROOM_H/2), color=(.49,.39,.20)))
add(shell, "left_jamb_inner", box((.055,.20,ROOM_H),
    center=(-1.215,-.12,ROOM_H/2), color=(.69,.57,.30)))
add(shell, "right_door_jamb", box((.095,.18,ROOM_H),
    center=(1.30,-.10,ROOM_H/2), color=(.55,.45,.27)))
add(scene, "architecture", shell)

# Brick on the rear wall; leave the window reveal unobstructed. Brickwork is
# intentionally irregular in tone, with thin mortar lines between the courses.
bricks = Asset("exposed_back_brick")
win_l, win_r = -0.05, 1.00
win_b, win_t = 1.04, 2.62
course_h = .145
brick_w = .40
for row in range(20):
    z = .065 + row * course_h
    x = -ROOM_W/2 - (brick_w/2 if row % 2 else 0)
    col = 0
    while x < ROOM_W/2:
        xl = max(x, -ROOM_W/2)
        xr = min(x + brick_w - .014, ROOM_W/2)
        if xr > xl:
            # Crop bricks along the window opening to preserve the clean reveal.
            intervals = [(xl, xr)]
            if z + course_h/2 > win_b and z - course_h/2 < win_t:
                intervals = []
                if xl < win_l:
                    intervals.append((xl, min(xr,win_l)))
                if xr > win_r:
                    intervals.append((max(xl,win_r), xr))
            for k,(lo,hi) in enumerate(intervals):
                if hi-lo > .018:
                    add(bricks, f"course_{row}_{col}_{k}",
                        box((hi-lo,.032,course_h-.012),
                            center=((lo+hi)/2,BACK_Y-.018,z),
                            color=brick_colors[(row*3+col*7)%len(brick_colors)]))
        x += brick_w
        col += 1
add(scene, "back_wall_bricks", bricks)

# Bare timber stud wall and a few remaining horizontal laths.
framing = Asset("left_exposed_framing")
for i, y in enumerate((.10,.62,1.15,1.70,2.23,2.78,3.27)):
    add(framing, f"vertical_stud_{i}",
        box((.105,.105,ROOM_H), center=(-1.19,y,ROOM_H/2),
            color=wood_dark if i%2==0 else wood_mid))
add(framing, "lower_plate", box((.12,ROOM_D,.10),
    center=(-1.19,ROOM_D/2,.08), color=wood_mid))
add(framing, "upper_plate", box((.12,ROOM_D,.11),
    center=(-1.19,ROOM_D/2,2.95), color=wood_dark))
for i in range(13):
    z = .43 + i*.155
    # Short irregular sections at the back of the wall, leaving framing visible.
    add(framing, f"remaining_lath_{i}",
        box((.025,1.22,.035), center=(-1.105,2.58,z),
            color=wood_light if i%3 else wood_mid))
add(scene, "left_wall_woodwork", framing)

# Window: dark recess, white outer frame, two dark panes and central sash.
window = Asset("white_double_hung_window")
wc = (win_l+win_r)/2
ww, wh = win_r-win_l, win_t-win_b
add(window, "dark_reveal", box((ww+.13,.055,wh+.14),
    center=(wc,BACK_Y-.052,(win_b+win_t)/2), color=(.075,.065,.05)))
add(window, "upper_glass", box((ww-.13,.025,(wh-.19)/2),
    center=(wc,BACK_Y-.092,win_b+wh*.735), color=glass))
add(window, "lower_glass", box((ww-.13,.025,(wh-.19)/2),
    center=(wc,BACK_Y-.092,win_b+wh*.255), color=(.025,.09,.17)))
for name,x in (("left",win_l+.04),("right",win_r-.04)):
    add(window, name+"_outer_frame", box((.085,.075,wh),
        center=(x,BACK_Y-.12,(win_b+win_t)/2), color=white))
for name,z in (("head",win_t-.04),("sill",win_b+.04),
               ("meeting_rail",win_b+wh*.50)):
    add(window, name, box((ww,.075,.085 if name!="meeting_rail" else .11),
        center=(wc,BACK_Y-.12,z), color=white))
# Fine lower pane divisions evoke the dark vertical lines visible in the image.
for i in range(9):
    x = win_l+.13+i*(ww-.26)/8
    add(window, f"lower_pane_line_{i}", box((.012,.02,wh*.37),
        center=(x,BACK_Y-.145,win_b+wh*.25), color=(.12,.18,.19)))
add(scene, "window", window)

# Electrical box and conduit on the left stud.
electrical = Asset("electrical_box_and_conduit")
add(electrical, "white_box", box((.105,.27,.39),
    center=(-1.075,.35,1.52), color=(.79,.78,.70)))
add(electrical, "box_top", box((.11,.28,.025),
    center=(-1.075,.35,1.725), color=(.68,.66,.59)))
add(electrical, "red_cap", box((.06,.095,.025),
    center=(-1.06,.28,1.75), color=(.46,.12,.09)))
add(electrical, "conduit", rod(.014, start=(-1.07,.35,.03),
    end=(-1.07,.35,1.32), color=(.48,.47,.41)))
add(scene, "electrical", electrical)

# Folding ladder. Front pair run from the lower-left foreground to the hinge;
# rear pair lean toward the right/back. Rungs span the rails and leave open gaps.
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
    add(ladder, f"front_rail_{side}",
        rod(.035, start=tuple(fb), end=tuple(ft), color=metal))
    add(ladder, f"rear_rail_{side}",
        rod(.032, start=tuple(bb), end=tuple(bt), color=metal_dark))
    add(ladder, f"front_foot_{side}",
        box((.12,.17,.065), center=tuple(fb+Vector((0,0,.025))),
            color=(.18,.18,.16)))
    add(ladder, f"rear_foot_{side}",
        box((.12,.16,.065), center=tuple(bb+Vector((0,0,.025))),
            color=(.18,.18,.16)))
for i in range(7):
    t = .15+i*.12
    p = front_bottom.lerp(front_top,t)
    add(ladder, f"front_rung_{i}",
        rod(.025, start=(p.x-rail_spacing/2,p.y-.012,p.z),
            end=(p.x+rail_spacing/2,p.y-.012,p.z), color=metal))
for i in range(4):
    t = .25+i*.18
    p = back_bottom.lerp(back_top,t)
    add(ladder, f"rear_rung_{i}",
        rod(.021, start=(p.x-rail_spacing/2,p.y,p.z),
            end=(p.x+rail_spacing/2,p.y,p.z), color=metal_dark))
for side in (-1,1):
    xoff=side*rail_spacing/2
    add(ladder, f"hinge_{side}", ball(.065,
        center=(front_top.x+xoff,front_top.y,front_top.z), color=metal_dark))
    a=front_bottom.lerp(front_top,.54)+Vector((xoff,0,0))
    b=back_bottom.lerp(back_top,.54)+Vector((xoff,0,0))
    add(ladder, f"spread_brace_{side}",
        rod(.014,start=tuple(a),end=tuple(b),color=metal_dark))
# Red safety marking on one lower rail.
p1=front_bottom.lerp(front_top,.12)+Vector((-.215,-.035,0))
p2=front_bottom.lerp(front_top,.36)+Vector((-.215,-.035,0))
add(ladder,"red_rail_mark",rod(.038,start=tuple(p1),end=tuple(p2),color=(.57,.12,.08)))
add(scene, "ladder", ladder)

# Broken laths and masonry scattered on the foreground floor.
debris = Asset("construction_debris")
for i in range(35):
    x = random.uniform(-.95,1.10)
    y = random.uniform(-.12,1.65)
    length = random.uniform(.24,1.05)
    width = random.uniform(.025,.065)
    z = .035 + random.uniform(0,.045)
    board = box((length,width,.025), center=(x,y,z),
        color=random.choice([wood_dark,wood_mid,wood_light]))
    board.turn(axis='+z',degrees=random.uniform(-70,70),pivot=(x,y,z))
    add(debris,f"broken_lath_{i}",board)
for i in range(30):
    x=random.uniform(-1.05,1.05)
    y=random.uniform(-.25,2.1)
    sx=random.uniform(.035,.13)
    sy=random.uniform(.035,.13)
    h=random.uniform(.018,.065)
    add(debris,f"rubble_{i}",box((sx,sy,h),center=(x,y,h/2),
        color=random.choice([(0.54,.49,.39),(.37,.33,.27),(.60,.55,.46)])))
add(scene,"floor_debris",debris)

# Small visible work lamp with warm emission supplied by a light after realization.
lamp = Asset("work_light")
add(lamp,"lamp_body",ball(.07,center=(-1.02,1.52,2.63),color=(1.0,.78,.40)))
add(lamp,"lamp_mount",box((.10,.10,.18),center=(-1.12,1.52,2.62),color=metal_dark))
add(scene,"work_lamp",lamp)

realize(scene)

# Preserve the original 383:512 image aspect for projection and rendering.
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
background.inputs["Color"].default_value = (0.17,0.16,0.14,1)
background.inputs["Strength"].default_value = .38

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
area_emitter((-0.8,1.1,2.65),power=250,size=.40,
             target=(0.0,2.0,1.0),color=(1.0,.72,.40))
area_emitter((0,-1.2,2.8),power=300,size=2.8,
             target=(0,2,1.2),color=(1.0,.84,.65))
area_emitter((.45,3.2,2.25),power=85,size=1.0,
             target=(0,1.0,1.2),color=(.58,.72,1.0))

# Landmark table compares visible surface points with estimated image anchors.
# It diagnoses projection only; it does not verify visibility or appearance.
landmarks = [
    ("window upper left", (win_l,BACK_Y-.12,win_t), (.62,.09)),
    ("window lower right", (win_r,BACK_Y-.12,win_b), (.93,.43)),
    ("ladder upper hinge", tuple(front_top), (.86,.23)),
    ("ladder front foot", tuple(front_bottom), (.58,.79)),
    ("left doorway base", (-1.215,-.12,.02), (.14,.98)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
    y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print("Landmark                     reference       projected")
for name,p,ref in landmarks:
    clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv=None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(f"{name:28s} {ref!s:15s} {uv!s}")
