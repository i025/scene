# Reference versus previous render, approximate normalized image coordinates:
# Window: reference (.62,.09)-(.93,.43); render (.62,.20)-(.90,.51).
# Ladder: reference (.56,.22)-(1,.79); render (.58,.28)-(1,.80).
# Debris: reference (.27,.74)-(1,1); render (.20,.73)-(1,1).
# Electrical box: reference (.15,.36)-(.25,.49); render (.18,.36)-(.25,.49).
# The reference doorway is cropped at both ends, as in the render. The ladder
# overlaps the window; its rails rise rightward, with open spaces between rungs.
#
# Largest discrepancies and supported corrections:
# 1. The back wall is too uniformly pale and its regular brick grid is much too
#    prominent. Replace the broad field with rough brown exposed substrate and
#    retain horizontal exposed courses below the window. Add procedural variation.
# 2. WINDOW_TOP increases from 2.62 to 3.18, raising the window head while
#    retaining its lower edge. Its width increases slightly toward the right.
# 3. LADDER_TOP rises and its front foot moves left, moving the hinge upward
#    and the lower rail left while keeping the wall and camera fixed.
# 4. Darken exposed wood and floor, concentrate debris toward the right, and
#    enlarge the bright warm work-light patch. Illumination also affects the
#    apparent brightness of the brick, wood, and metal.
# Camera is unchanged from the previous render; projection output below reports
# computed geometric points separately from the observed image contours.
#
# Inventory: room shell and doorway; exposed left studs and laths; rear masonry
# and lower horizontal strips; white double-hung window and dark blue panes;
# aluminum folding ladder with rails, steps, braces and feet; electrical box
# and conduit; floor debris; bright work lamp. Right wall and concealed areas
# are uncertain. Approximate expanded primitives: shell 8, framing 33,
# back wall 27, window 20, ladder 29, electrical 5, debris 112, lamp 2:
# approximately 236 meshes. Each box, rod, or ball is one primitive.

import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(24)
scene = Scene("Unfinished room")

ROOM_W = 2.55
ROOM_H = 4.2
BACK_Y = 3.45
CAMERA_POSITION = (0.02, -3.95, 1.67)
CAMERA_TARGET = (-0.55, 2.70, 1.05)
CAMERA_LENS = 46.0

WIN_L, WIN_R = -.05, 1.12
WIN_B, WIN_T = 1.04, 3.18
FRONT_BOTTOM = Vector((-.12, 1.05, .04))
FRONT_TOP = Vector((.78, 2.32, 2.39))
BACK_BOTTOM = Vector((1.35, 2.88, .04))
BACK_TOP = FRONT_TOP.copy()
RAIL_SPACING = .42

wood_dark = (.095, .047, .023)
wood_mid = (.23, .12, .055)
wood_light = (.40, .245, .12)
dust = (.29, .275, .225)
metal = (.48, .50, .48)
metal_dark = (.27, .29, .28)
white = (.76, .75, .67)

def add(parent, name, node):
    parent.include(name, node)

def rail(parent, name, a, b, width, depth, color):
    a, b = Vector(a), Vector(b)
    delta = b - a
    midpoint = (a + b) * .5
    obj = box((width, depth, delta.length), center=tuple(midpoint), color=color)
    q = Vector((0, 0, 1)).rotation_difference(delta.normalized())
    obj.turn(euler=tuple(math.degrees(v) for v in q.to_euler()),
             pivot=tuple(midpoint))
    add(parent, name, obj)

shell = Asset("room_shell")
add(shell, "dusty_floor", box((ROOM_W, 8, .10),
    center=(0, 1, -.055), color=dust))
add(shell, "back_exposed_wall", box((ROOM_W, .13, ROOM_H),
    center=(0, BACK_Y+.08, ROOM_H/2), color=(.26,.225,.165)))
add(shell, "left_dark_substrate", box((.12, 5.4, ROOM_H),
    center=(-ROOM_W/2-.06, 1.4, ROOM_H/2), color=(.105,.075,.046)))
add(shell, "right_wall_edge", box((.12, 2, ROOM_H),
    center=(ROOM_W/2+.06, -.25, ROOM_H/2), color=(.31,.26,.18)))
add(shell, "left_door_jamb", box((.13,.18,ROOM_H),
    center=(-1.31,-.11,ROOM_H/2), color=(.44,.34,.16)))
add(shell, "left_jamb_inner", box((.055,.20,ROOM_H),
    center=(-1.215,-.12,ROOM_H/2), color=(.57,.46,.23)))
add(shell, "right_door_jamb", box((.095,.18,ROOM_H),
    center=(1.30,-.10,ROOM_H/2), color=(.43,.34,.20)))
add(scene, "architecture", shell)

# Horizontal surviving wood and masonry courses at the bottom of the rear wall.
back = Asset("rear_exposed_courses")
for i in range(12):
    z = .07 + i*.075
    add(back, "horizontal_course_%02d" % i,
        box((2.53,.035,.045), center=(0,BACK_Y-.018,z),
            color=[(.30,.22,.14),(.38,.28,.17),(.25,.19,.125)][i%3]))
for i in range(8):
    x = -.95 + i*.29
    add(back, "lower_course_joint_%02d" % i,
        box((.012,.012,.07), center=(x,BACK_Y-.041,.32+(i%3)*.15),
            color=(.15,.115,.075)))
# A dark line across the weathered wall appears left of the window.
add(back, "old_wall_rail", box((.76,.035,.045),
    center=(-.69,BACK_Y-.035,1.62), color=(.13,.095,.055)))
add(scene, "back_wall_detail", back)

framing = Asset("left_exposed_framing")
for i, y in enumerate((-.18,.10,.62,1.15,1.70,2.23,2.78,3.27)):
    add(framing, "vertical_stud_%d" % i, box((.105,.105,ROOM_H),
        center=(-1.19,y,ROOM_H/2),
        color=wood_dark if i%2==0 else wood_mid))
add(framing, "lower_plate", box((.12,4.2,.10),
    center=(-1.19,1.35,.08), color=wood_mid))
for i in range(21):
    z = .30+i*.145
    add(framing, "remaining_lath_%02d" % i,
        box((.025,1.40,.035), center=(-1.105,2.48,z),
            color=wood_light if i%3 else wood_mid))
add(scene, "left_wall_woodwork", framing)

window = Asset("white_double_hung_window")
wc = (WIN_L+WIN_R)/2
ww, wh = WIN_R-WIN_L, WIN_T-WIN_B
add(window, "dark_reveal", box((ww+.15,.055,wh+.16),
    center=(wc,BACK_Y-.052,(WIN_B+WIN_T)/2), color=(.038,.035,.027)))
# The lower sash is shorter than the upper sash in the photograph.
meeting = WIN_B + wh*.36
add(window, "upper_glass", box((ww-.14,.025,WIN_T-meeting-.10),
    center=(wc,BACK_Y-.092,(meeting+WIN_T)/2), color=(.025,.085,.105)))
add(window, "lower_glass", box((ww-.14,.025,meeting-WIN_B-.10),
    center=(wc,BACK_Y-.092,(WIN_B+meeting)/2), color=(.012,.045,.16)))
for name,x in (("left",WIN_L+.04),("right",WIN_R-.04)):
    add(window, name+"_outer_frame", box((.085,.075,wh),
        center=(x,BACK_Y-.12,(WIN_B+WIN_T)/2), color=white))
for name,z,height in (("head",WIN_T-.04,.085),
                      ("sill",WIN_B+.04,.085),
                      ("meeting_rail",meeting,.105)):
    add(window, name, box((ww,.075,height),
        center=(wc,BACK_Y-.12,z), color=white))
for i in range(10):
    x = WIN_L+.13+i*(ww-.26)/9
    add(window, "lower_pane_line_%d" % i,
        box((.012,.02,meeting-WIN_B-.16),
            center=(x,BACK_Y-.145,(WIN_B+meeting)/2),
            color=(.06,.11,.15)))
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
for side in (-1,1):
    dx = side*RAIL_SPACING/2
    fb = FRONT_BOTTOM + Vector((dx,0,0))
    ft = FRONT_TOP + Vector((dx,0,0))
    bb = BACK_BOTTOM + Vector((dx,0,0))
    bt = BACK_TOP + Vector((dx,0,0))
    rail(ladder, "front_rail_%d" % side, fb, ft, .075,.06,metal)
    rail(ladder, "rear_rail_%d" % side, bb, bt, .065,.055,metal_dark)
    add(ladder, "front_foot_%d" % side, box((.12,.17,.065),
        center=tuple(fb+Vector((0,0,.025))),color=(.13,.13,.12)))
    add(ladder, "rear_foot_%d" % side, box((.12,.16,.065),
        center=tuple(bb+Vector((0,0,.025))),color=(.13,.13,.12)))
    add(ladder, "hinge_%d" % side, ball(.065,
        center=tuple(ft), color=metal_dark))
    a = fb.lerp(ft,.54)
    b = bb.lerp(bt,.54)
    add(ladder, "spread_brace_%d" % side,
        rod(.014,start=tuple(a),end=tuple(b),color=metal_dark))
for i in range(7):
    t = .15+i*.12
    p = FRONT_BOTTOM.lerp(FRONT_TOP,t)
    add(ladder, "front_step_%d" % i,
        box((RAIL_SPACING+.035,.105,.035),
            center=(p.x,p.y-.018,p.z),color=metal))
for i in range(4):
    t = .25+i*.18
    p = BACK_BOTTOM.lerp(BACK_TOP,t)
    add(ladder, "rear_rung_%d" % i,
        rod(.021,start=(p.x-RAIL_SPACING/2,p.y,p.z),
            end=(p.x+RAIL_SPACING/2,p.y,p.z),color=metal_dark))
p1 = FRONT_BOTTOM.lerp(FRONT_TOP,.12)+Vector((-.215,-.04,0))
p2 = FRONT_BOTTOM.lerp(FRONT_TOP,.36)+Vector((-.215,-.04,0))
rail(ladder,"red_rail_mark",p1,p2,.045,.016,(.52,.065,.035))
add(scene,"ladder",ladder)

debris = Asset("construction_debris")
for i in range(55):
    x = random.uniform(-.55,1.20)
    y = random.uniform(-.45,1.5)
    length = random.uniform(.25,1.15)
    width = random.uniform(.025,.065)
    z = .035 + random.uniform(0,.08)
    board = box((length,width,.025),center=(x,y,z),
        color=random.choice([wood_dark,wood_mid,wood_light]))
    board.turn(axis='+z',degrees=random.uniform(-85,85),pivot=(x,y,z))
    add(debris,"broken_lath_%02d" % i,board)
for i in range(57):
    x = random.uniform(-1.1,1.1)
    y = random.uniform(-.65,2.1)
    sx,sy = random.uniform(.025,.12),random.uniform(.025,.12)
    h = random.uniform(.015,.06)
    add(debris,"rubble_%02d" % i,box((sx,sy,h),center=(x,y,h/2),
        color=random.choice([(.43,.39,.30),(.25,.22,.17),(.50,.46,.37)])))
add(scene,"floor_debris",debris)

lamp = Asset("work_light")
add(lamp,"lamp_body",ball(.11,center=(-1.02,1.52,2.63),color=(1,.90,.67)))
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
background.inputs["Color"].default_value = (.10,.095,.08,1)
background.inputs["Strength"].default_value = .20

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS)
bpy.context.view_layer.update()

# Reference anchors are estimates. Projected points are geometric landmarks,
# not measurements of rendered silhouettes or visibility.
landmarks = [
    ("window upper left",(WIN_L,BACK_Y-.12,WIN_T),(.62,.09)),
    ("window lower right",(WIN_R,BACK_Y-.12,WIN_B),(.93,.43)),
    ("ladder hinge",tuple(FRONT_TOP),(.86,.23)),
    ("ladder front foot",tuple(FRONT_BOTTOM),(.58,.79)),
    ("left doorway base",(-1.215,-.12,.02),(.14,.98)),
]
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
    y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print("Landmark: reference estimate / computed projection")
for name,p,ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, uv)

area_emitter((-.95,1.25,2.65),power=450,size=.22,
    target=(0,2.0,1.2),color=(1.0,.72,.42))
area_emitter((0,-1.2,2.8),power=125,size=2.6,
    target=(0,2,1.2),color=(1.0,.82,.62))
area_emitter((.45,3.2,2.25),power=30,size=1.0,
    target=(0,1.0,1.2),color=(.58,.72,1.0))
