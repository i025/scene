# Reference inventory and visual anchors, normalized image coordinates:
# Foreground folding bench: top approximately (0.07, 0.33)-(0.91, 0.52);
# front left foot near (0.28, 0.97), right foot near (0.87, 0.73).
# Long hardboard top has softly rounded corners, small dog holes, white edge rails,
# yellow stops, a blue front vise, splayed white perforated legs and hanging clamps.
# Rear workbench: orange top approximately (0.00, 0.25)-(0.86, 0.42), with
# a circular-log mosaic across its front. It overlaps the foreground bench.
# Track saw at left, blue drill press around (0.31, 0.31), CNC gantry router
# around (0.61, 0.25), and articulated lamp around (0.48, 0.19).
# Background: timber racks at upper left; corrugated dark wall, stove and tool
# storage at upper right. Much of the lower rear wall is occluded.
# Dominant bench edges rise toward image right. Vertical legs remain nearly vertical.
# Floor occupies the lower right and foreground; warm overhead and task lighting.
# Approximate primitive count: ~360, including about 105 log ends, 45 bench holes,
# and 40 shelf and equipment details. All components remain editable SceneAct parts.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Woodworking shop")

# Camera and principal dimensions are deliberately independent.
CAM_POS = (-4.9, -7.6, 4.65)
CAM_TARGET = (0.0, 0.28, 0.95)
CAM_LENS = 40
BENCH_L = 3.05
BENCH_D = 0.84
BENCH_Z = 0.91
BENCH_Y = -0.78
REAR_L = 4.8
REAR_D = 0.92
REAR_Y = 0.93
REAR_Z = 1.02

white = (0.77, 0.75, 0.67)
white_edge = (0.88, 0.86, 0.77)
ply = (0.56, 0.39, 0.23)
topmat = (0.58, 0.39, 0.25)
orange = (0.63, 0.36, 0.10)
blue = (0.025, 0.19, 0.43)
yellow = (0.95, 0.60, 0.015)
dark = (0.075, 0.075, 0.07)
metal = (0.35, 0.36, 0.34)
black = (0.025, 0.03, 0.03)

def put(asset, name, node):
    asset.include(name, node)

def B(asset, name, size, center, color):
    put(asset, name, box(size=size, center=center, color=color))

def R(asset, name, a, b, radius, color):
    put(asset, name, rod(radius=radius, start=a, end=b, color=color))

# Architecture: concrete slab, corrugated back wall and the dark left storage bay.
room = Asset("Architecture")
B(room, "concrete_floor", (12, 11, .12), (0, 0, -.065), (.38, .38, .36))
B(room, "back_wall", (10, .13, 3.65), (0, 3.05, 1.82), (.25, .25, .22))
B(room, "right_wall", (.12, 5.0, 3.65), (4.2, .7, 1.82), (.37, .35, .29))
B(room, "left_dark_bay", (3.0, .10, 2.8), (-2.65, 2.94, 1.70), (.10, .095, .075))
for i in range(27):
    x = -.78 + i * .13
    B(room, "wall_rib_%02d" % i, (.025, .035, 3.1), (x, 2.96, 1.85), (.17, .18, .17))
scene.include("architecture", room)

# Rear workbench and its round log-end front.
rear = Asset("Rear log faced workbench")
B(rear, "heavy_body", (REAR_L, REAR_D, .80), (0, REAR_Y, .50), (.16, .12, .08))
B(rear, "orange_worktop", (REAR_L + .05, REAR_D + .05, .075),
  (0, REAR_Y, REAR_Z), orange)
B(rear, "front_lip", (REAR_L + .05, .055, .10),
  (0, REAR_Y - REAR_D/2 - .02, REAR_Z - .065), (.47, .27, .10))
B(rear, "rear_edge", (REAR_L, .055, .08), (0, REAR_Y + REAR_D/2, REAR_Z + .045), (.42, .25, .12))
# End grain discs lie in the front plane, with dark bark rims.
log_cols = [(.53,.42,.30), (.68,.56,.39), (.40,.31,.22), (.76,.66,.48)]
for row in range(5):
    z = .18 + row * .155
    for col in range(25):
        x = -2.32 + col * .19 + (row % 2) * .09
        if x > 2.35:
            continue
        r = random.uniform(.066, .092)
        y = REAR_Y - REAR_D/2 - .034
        R(rear, "bark_%d_%d" % (row,col), (x,y,z), (x,y-.018,z), r, (.13,.10,.075))
        R(rear, "endgrain_%d_%d" % (row,col), (x,y-.019,z), (x,y-.024,z), r*.78, random.choice(log_cols))
scene.include("rear_bench", rear)

# Foreground bench: major top, rails, braced frames and holes.
front = Asset("Folding birch plywood workbench")
B(front, "hardboard_top", (BENCH_L, BENCH_D, .055), (0, BENCH_Y, BENCH_Z), topmat)
B(front, "plywood_top_edge", (BENCH_L, BENCH_D, .045), (0, BENCH_Y, BENCH_Z-.045), (.73,.60,.43))
B(front, "front_white_apron", (BENCH_L-.04, .07, .17),
  (0, BENCH_Y-BENCH_D/2+.035, BENCH_Z-.16), white_edge)
B(front, "rear_white_apron", (BENCH_L-.04, .07, .15),
  (0, BENCH_Y+BENCH_D/2-.035, BENCH_Z-.15), white)
B(front, "left_end_rail", (.08, BENCH_D, .15), (-BENCH_L/2+.04, BENCH_Y, BENCH_Z-.14), white)
B(front, "right_end_rail", (.08, BENCH_D, .15), (BENCH_L/2-.04, BENCH_Y, BENCH_Z-.14), white)
# Top perforations: dark small circles just above the board.
for i in range(10):
    for j in range(4):
        x = -1.27 + i*.28
        y = BENCH_Y-.28+j*.18
        R(front, "top_dog_%d_%d" % (i,j), (x,y,BENCH_Z+.0275),
          (x,y,BENCH_Z+.030), .012, (.24,.17,.12))
# Front rail holes.
for i in range(14):
    x = -1.28+i*.197
    R(front, "apron_hole_%02d" % i,
      (x,BENCH_Y-BENCH_D/2-.003,BENCH_Z-.16),
      (x,BENCH_Y-BENCH_D/2-.008,BENCH_Z-.16), .014, (.25,.24,.21))
# Taper impression via broad angled plywood members; X-axis table length.
for side, x in (("left",-1.19),("right",1.19)):
    for face, y in (("front",BENCH_Y-.30),("back",BENCH_Y+.30)):
        footx = x + (-.16 if x < 0 else .16)
        leg = box(size=(.19,.105,.84), center=((x+footx)/2,y,.45), color=white)
        leg.turn(axis="+y", degrees=(-10 if x < 0 else 10))
        put(front, side+"_"+face+"_leg", leg)
        B(front, side+"_"+face+"_foot", (.22,.14,.045), (footx,y,.035), (.67,.65,.58))
    B(front, side+"_inner_plywood_panel", (.045,.53,.52), (x,BENCH_Y,.47), (.68,.65,.55))
    B(front, side+"_upper_crossbar", (.10,.66,.095), (x,BENCH_Y,.75), white_edge)
    # dark perforations on outward-facing plane of the side panel
    outerx = x + (-.027 if x < 0 else .027)
    for k in range(4):
        for m in range(3):
            y = BENCH_Y-.20 + m*.18
            z = .28+k*.12
            R(front, side+"_panel_hole_%d_%d" % (k,m),
              (outerx,y,z), (outerx+(-.006 if x<0 else .006),y,z), .012, (.23,.22,.19))
# Yellow work stops and inserts in apron.
for i,x in enumerate((-1.32,-.38,.47,1.25)):
    B(front, "yellow_stop_%d"%i, (.105,.075,.18), (x,BENCH_Y+.02,BENCH_Z-.16), yellow)
B(front, "front_left_yellow", (.13,.055,.17), (-1.34,BENCH_Y-.43,BENCH_Z-.18), yellow)
# Blue vise on the near edge.
B(front, "vise_white_mount", (.48,.075,.23), (-.63,BENCH_Y-.46,.74), white_edge)
B(front, "vise_blue_body", (.38,.09,.09), (-.63,BENCH_Y-.515,.74), blue)
for x in (-.77,-.50):
    R(front, "vise_bolt_"+str(x), (x,BENCH_Y-.565,.74), (x,BENCH_Y-.58,.74), .025, (.63,.64,.60))
R(front, "vise_screw", (-.64,BENCH_Y-.57,.74), (-.64,BENCH_Y-.70,.74), .028, metal)
R(front, "vise_handle", (-.82,BENCH_Y-.70,.85), (-.40,BENCH_Y-.70,.56), .025, (.31,.32,.31))
R(front, "vise_handle_tip_a", (-.84,BENCH_Y-.70,.86), (-.80,BENCH_Y-.70,.83), .033, (.46,.09,.08))
R(front, "vise_handle_tip_b", (-.42,BENCH_Y-.70,.58), (-.38,BENCH_Y-.70,.55), .033, (.46,.09,.08))
# Long clamps hanging from the left frame.
for i in range(3):
    x = -1.30 + i*.09
    R(front, "clamp_bar_%d"%i, (x,BENCH_Y-.39,.18), (x,BENCH_Y-.39,.71), .012, (.25,.25,.23))
    B(front, "clamp_handle_%d"%i, (.045,.045,.13), (x,BENCH_Y-.40,.36+i*.035), (.90,.27,.025))
    B(front, "clamp_jaw_%d"%i, (.10,.06,.035), (x+.025,BENCH_Y-.39,.69), (.19,.20,.19))
scene.include("foreground_bench", front)

# Track saw at the left end of rear bench.
saw = Asset("Track saw")
B(saw, "silver_track", (1.15,.14,.018), (-1.85,REAR_Y-.26,REAR_Z+.05), (.67,.70,.68))
B(saw, "sole_plate", (.44,.29,.035), (-1.75,REAR_Y-.20,REAR_Z+.08), (.48,.50,.48))
B(saw, "blade_housing", (.30,.20,.19), (-1.75,REAR_Y-.20,REAR_Z+.18), (.69,.71,.68))
B(saw, "motor", (.14,.18,.15), (-1.56,REAR_Y-.20,REAR_Z+.18), (.31,.34,.32))
R(saw, "top_handle", (-1.88,REAR_Y-.18,REAR_Z+.29), (-1.63,REAR_Y-.18,REAR_Z+.29), .025, dark)
B(saw, "green_switch", (.06,.05,.04), (-1.61,REAR_Y-.19,REAR_Z+.28), (.18,.39,.12))
scene.include("track_saw", saw)

# Blue drill press with base, upright, worktable and motor head.
drill = Asset("Blue benchtop drill press")
dx,dy = -.89, REAR_Y+.02
B(drill, "base", (.32,.27,.045), (dx,dy,REAR_Z+.06), (.10,.14,.15))
R(drill, "column", (dx,dy,REAR_Z+.07), (dx,dy,REAR_Z+.66), .035, (.25,.27,.27))
B(drill, "blue_head", (.22,.18,.14), (dx,dy,REAR_Z+.63), blue)
B(drill, "black_motor", (.14,.15,.18), (dx,dy+.11,REAR_Z+.65), dark)
B(drill, "work_table", (.24,.18,.035), (dx,dy-.04,REAR_Z+.30), blue)
R(drill, "chuck", (dx,dy-.06,REAR_Z+.55), (dx,dy-.06,REAR_Z+.37), .022, (.25,.26,.24))
R(drill, "feed_lever", (dx+.10,dy,REAR_Z+.58), (dx+.23,dy,REAR_Z+.49), .012, black)
scene.include("drill_press", drill)

# CNC router: dark bed, pale gantry bridge, rails and spindle.
cnc = Asset("CNC gantry router")
cx,cy = .55,REAR_Y+.06
B(cnc, "black_base", (1.40,.68,.08), (cx,cy,REAR_Z+.09), (.10,.11,.10))
B(cnc, "sacrificial_board", (1.10,.49,.035), (cx,cy,REAR_Z+.15), (.64,.54,.39))
for x in (cx-.57,cx+.57):
    B(cnc, "side_rail_"+str(x), (.065,.67,.10), (x,cy,REAR_Z+.19), (.24,.25,.24))
    B(cnc, "gantry_upright_"+str(x), (.08,.11,.38), (x,cy+.16,REAR_Z+.36), (.31,.32,.31))
B(cnc, "gantry_beam", (1.25,.11,.13), (cx,cy+.16,REAR_Z+.53), (.63,.65,.61))
B(cnc, "carriage", (.19,.15,.19), (cx+.06,cy+.10,REAR_Z+.49), (.14,.15,.14))
R(cnc, "router_spindle", (cx+.06,cy+.02,REAR_Z+.53), (cx+.06,cy+.02,REAR_Z+.24), .052, (.19,.19,.17))
B(cnc, "yellow_router_cap", (.13,.13,.07), (cx+.06,cy+.02,REAR_Z+.55), (.82,.61,.05))
scene.include("cnc_router", cnc)

# Articulated task lamp, with a pale metal conical-looking shade.
lamp = Asset("Articulated task lamp")
lx,ly = -0.53,REAR_Y+.30
B(lamp, "round_base", (.25,.18,.025), (lx,ly,REAR_Z+.055), (.58,.58,.53))
R(lamp, "lower_arm", (lx,ly,REAR_Z+.07), (lx-.05,ly,REAR_Z+.63), .016, (.65,.66,.62))
R(lamp, "upper_arm", (lx-.05,ly,REAR_Z+.63), (lx+.30,ly,REAR_Z+.91), .016, (.65,.66,.62))
R(lamp, "second_upper_arm", (lx-.02,ly+.03,REAR_Z+.62), (lx+.32,ly+.03,REAR_Z+.88), .009, (.44,.45,.43))
R(lamp, "shade", (lx+.30,ly,REAR_Z+.91), (lx+.34,ly-.04,REAR_Z+.78), .085, (.72,.72,.66))
scene.include("task_lamp", lamp)

# Wall-side timber rack, uneven stacks of planks.
rack = Asset("Wall lumber rack")
for z in (1.28,1.69,2.10,2.51,2.92):
    B(rack, "shelf_%.2f"%z, (2.58,.43,.075), (-2.10,2.67,z), (.17,.12,.075))
for x in (-3.31,-1.08):
    B(rack, "rack_post_"+str(x), (.07,.08,2.60), (x,2.48,1.65), (.12,.10,.08))
woodcolors = [(.39,.24,.12),(.56,.36,.19),(.68,.48,.28),(.31,.20,.12)]
for level,z in enumerate((1.37,1.78,2.19,2.60,3.01)):
    for j in range(4):
        length = random.uniform(1.1,2.35)
        x = -2.15+random.uniform(-.22,.22)
        B(rack, "board_%d_%d"%(level,j), (length,.16,.045),
          (x,2.50+j*.075,z+j*.048), random.choice(woodcolors))
scene.include("lumber_rack", rack)

# Stove and pipe, plus dark storage and the wall tool area.
stove = Asset("Cast iron stove")
B(stove, "firebox", (.75,.56,.62), (2.08,2.27,.46), (.075,.075,.07))
B(stove, "stove_top", (.82,.60,.07), (2.08,2.27,.80), (.10,.10,.09))
B(stove, "door", (.48,.025,.40), (2.08,1.975,.45), (.12,.12,.11))
B(stove, "door_panel", (.37,.018,.28), (2.08,1.958,.45), (.045,.045,.04))
for x in (1.79,2.37):
    B(stove, "foot_"+str(x), (.10,.10,.18), (x,2.25,.09), (.08,.08,.075))
R(stove, "chimney", (2.12,2.31,.81), (2.12,2.31,3.3), .10, (.08,.08,.075))
scene.include("stove", stove)

storage = Asset("Tools and wall storage")
B(storage, "right_shelving", (.84,.35,1.48), (3.04,2.52,.76), (.15,.13,.11))
for z in (.35,.70,1.05,1.40):
    B(storage, "shelf_%s"%z, (.88,.39,.045), (3.04,2.49,z), (.29,.21,.13))
    for i in range(4):
        B(storage, "bin_%s_%s"%(z,i), (.17,.25,.12),
          (2.73+i*.20,2.44,z+.08), (.34,.08,.055) if i%2 else (.13,.14,.13))
# Vertical tool silhouettes behind the CNC.
for i in range(12):
    x = -.38+i*.105
    ztop = 2.55 + (i%3)*.08
    R(storage, "hanging_tool_%d"%i, (x,2.86,1.81), (x,2.86,ztop), .012,
      (.07,.07,.065) if i%3 else (.35,.17,.08))
B(storage, "dark_tool_board", (1.38,.05,.38), (.18,2.90,2.25), (.12,.11,.09))
scene.include("tool_storage", storage)

realize(scene)

# World and lighting are created after realization, which clears the Blender scene.
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
background.inputs["Color"].default_value = (0.34, 0.33, 0.30, 1)
background.inputs["Strength"].default_value = .45
sc.render.resolution_x = 511
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS)
area_emitter((-3,-4,6), power=1200, size=5, target=(0,0,.5), color=(1.0,.83,.64))
area_emitter((3,1,4.5), power=900, size=4, target=(0,0,.5), color=(1.0,.89,.73))
area_emitter((lx+.32,ly-.05,REAR_Z+.78), power=85, size=.4,
             target=(lx+.25,ly-.05,REAR_Z), color=(1,.82,.58))

# Small numerical projection check, using identifiable geometry points.
# Reference UV estimates and projections are separate: geometry visibility is
# checked only by the runner's rendered view.
landmarks = [
    ("front_top_left", (-BENCH_L/2, BENCH_Y-BENCH_D/2, BENCH_Z), (.08,.46)),
    ("front_top_right", (BENCH_L/2, BENCH_Y-BENCH_D/2, BENCH_Z), (.91,.39)),
    ("left_foot", (-1.35, BENCH_Y-.30, .035), (.28,.97)),
    ("rear_bench_left", (-REAR_L/2, REAR_Y-REAR_D/2, REAR_Z), (.00,.38)),
    ("rear_bench_right", (REAR_L/2, REAR_Y-REAR_D/2, REAR_Z), (.85,.29)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                                    scale_x=sc.render.pixel_aspect_x,
                                    scale_y=sc.render.pixel_aspect_y)
print("Landmark | reference UV | projected UV")
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point,1.0))
    uv = None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
