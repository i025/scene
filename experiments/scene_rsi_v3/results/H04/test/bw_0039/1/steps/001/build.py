# Reference inventory and anchors (normalized image coordinates, visual estimates):
# - Narrow unfinished room, floor in lower half; left doorway/jamb x=0.00-0.14.
# - Rear wall spans x=0.45-1.00, with exposed brown masonry and horizontal lath.
# - White double-hung window x=0.63-0.92, y=0.09-0.43; dark blue glazing.
# - Exposed left wall studs and lath x=0.13-0.46, extending floor to ceiling.
# - White electrical box x=0.15-0.25, y=0.36-0.49.
# - Aluminum folding ladder x=0.56-0.98, y=0.22-0.80; front rails overlap window.
# - Broken wooden strips and rubble across floor x=0.25-1.00, y=0.72-1.00.
# - Bright warm work light near x=0.40, y=0.10. Window and rear wall partly
#   occluded by ladder; construction behind studs and outside window is uncertain.
# Dominant edges: wall studs almost vertical; ladder rails rise toward image right;
# floor edges converge toward the rear; horizontal rear-wall courses.
# Estimated expanded primitive meshes: architecture ~95, window ~15, ladder ~35,
# electrical/light ~8, floor debris ~75; total approximately 230.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(21)
scene = Scene('Construction room')

# Dimensions and camera parameters are independent.
ROOM_W = 2.55
ROOM_L = 4.25
ROOM_H = 2.90
BACK_Y = 4.25
CAMERA_POSITION = (0.0, -3.55, 1.67)
CAMERA_TARGET = (0.10, 2.35, 1.48)
CAMERA_LENS = 32

wood = (0.28, 0.145, 0.070)
wood_light = (0.43, 0.255, 0.13)
wood_dark = (0.16, 0.085, 0.043)
brick = (0.36, 0.285, 0.205)
mortar = (0.29, 0.255, 0.20)
plaster = (0.46, 0.42, 0.33)
metal = (0.62, 0.65, 0.64)
metal_dark = (0.28, 0.31, 0.30)
white = (0.78, 0.77, 0.68)
blue = (0.035, 0.10, 0.16)
floor_color = (0.46, 0.43, 0.35)

# Architectural enclosure: solid rear wall with an actual window opening.
architecture = Asset('room_enclosure')
architecture.include('floor', box((ROOM_W, ROOM_L + 3.0, 0.12),
    center=(0, 1.75, -0.07), color=floor_color))
# Rear wall assembled around the opening.
win_l, win_r = 0.18, 1.15
win_b, win_t = 1.26, 2.54
architecture.include('rear_left', box((win_l + ROOM_W/2, .13, ROOM_H),
    center=((-ROOM_W/2 + win_l)/2, BACK_Y, ROOM_H/2), color=brick))
architecture.include('rear_right', box((ROOM_W/2-win_r, .13, ROOM_H),
    center=((win_r+ROOM_W/2)/2, BACK_Y, ROOM_H/2), color=brick))
architecture.include('rear_below_window', box((win_r-win_l, .13, win_b),
    center=((win_l+win_r)/2, BACK_Y, win_b/2), color=brick))
architecture.include('rear_above_window', box((win_r-win_l, .13, ROOM_H-win_t),
    center=((win_l+win_r)/2, BACK_Y, (win_t+ROOM_H)/2), color=brick))
architecture.include('left_wall_backing', box((.10, ROOM_L, ROOM_H),
    center=(-ROOM_W/2, ROOM_L/2, ROOM_H/2), color=(.27,.22,.16)))
architecture.include('right_wall_edge', box((.10, ROOM_L, ROOM_H),
    center=(ROOM_W/2, ROOM_L/2, ROOM_H/2), color=(.39,.34,.25)))

# Rear masonry: restrained irregular horizontal joints and a few vertical seams.
for i in range(17):
    z = .12 + i*.165
    if z > ROOM_H: break
    intervals = [(-1.25, 1.25)] if z < win_b or z > win_t else [(-1.25,win_l),(win_r,1.25)]
    for j,(a,b) in enumerate(intervals):
        if b-a > .03:
            architecture.include('rear_joint_%02d_%d'%(i,j),
                box((b-a,.012,.014), center=((a+b)/2, BACK_Y-.073,z), color=mortar))
    for j in range(3):
        x = -1.07 + j*.78 + (.35 if i%2 else 0)
        if -1.23 < x < 1.23 and not (win_l-.03 < x < win_r+.03 and win_b < z < win_t):
            architecture.include('rear_seam_%02d_%d'%(i,j),
                box((.012,.013,.14), center=(x,BACK_Y-.075,z+.075), color=mortar))

# Horizontal old lath, concentrated on the bottom of rear wall.
for i in range(10):
    z=.10+i*.075
    architecture.include('rear_lath_%02d'%i,
        box((2.40,.035,.045), center=(0,BACK_Y-.11,z), color=wood_light if i%3 else wood))
scene.include('architecture', architecture)

# Left wall framework, lath, and foreground door trim.
framework = Asset('exposed_left_wall')
for i,y in enumerate((-.15,.55,1.25,1.95,2.67,3.38,4.05)):
    framework.include('stud_%02d'%i, box((.10,.10,2.88),
        center=(-1.18,y,1.44), color=wood if i%2 else wood_dark))
framework.include('top_plate',box((.12,4.2,.10),center=(-1.18,2.1,2.83),color=wood))
framework.include('bottom_plate',box((.12,4.2,.10),center=(-1.18,2.1,.08),color=wood))
for i in range(26):
    z=.17+i*.097
    framework.include('left_lath_%02d'%i,box((.025,3.95,.045),
        center=(-1.235,2.10,z),color=wood_light if i%4 else wood_dark))
# Near doorway, thick cream-painted jambs.
framework.include('near_left_jamb',box((.16,.18,3.0),center=(-1.29,-.12,1.50),color=(.65,.58,.38)))
framework.include('near_left_inner_trim',box((.065,.19,3.0),center=(-1.14,-.14,1.5),color=(.34,.25,.14)))
framework.include('near_right_jamb',box((.10,.15,3.0),center=(1.31,-.05,1.5),color=(.64,.59,.43)))
scene.include('left_framing',framework)

# White double-hung window: dark opening, two separate panes, broad frame and meeting rail.
window = Asset('double_hung_window')
window.include('dark_recess',box((1.04,.045,1.37),center=(.665,4.29,1.90),color=(.075,.065,.047)))
window.include('upper_glass',box((.78,.035,.50),center=(.665,4.255,2.22),color=blue))
window.include('lower_glass',box((.78,.035,.48),center=(.665,4.255,1.65),color=(.025,.09,.17)))
for name,x in [('left',.19),('right',1.14)]:
    window.include('outer_'+name,box((.10,.10,1.35),center=(x,4.16,1.90),color=white))
for name,z in [('top',2.53),('bottom',1.27),('meeting_rail',1.91)]:
    window.include(name,box((1.04,.10,.085),center=(.665,4.16,z),color=white))
for x in (.29,1.04):
    window.include('sash_vertical_'+str(x),box((.045,.06,1.10),center=(x,4.13,1.90),color=(.66,.65,.57)))
window.include('sill',box((1.13,.16,.08),center=(.665,4.12,1.24),color=(.61,.58,.48)))
scene.include('window',window)

# Electrical box on the near left stud, with a conduit descending behind it.
electrical = Asset('electrical_box')
electrical.include('box_body',box((.19,.26,.43),center=(-1.06,.43,1.48),color=(.80,.80,.72)))
electrical.include('box_lid',box((.025,.255,.40),center=(-.955,.43,1.48),color=(.88,.88,.80)))
electrical.include('top_red_cap',box((.12,.13,.035),center=(-1.04,.42,1.71),color=(.38,.09,.07)))
electrical.include('conduit',rod(.018,start=(-1.06,.44,1.27),end=(-1.06,.44,.12),color=(.55,.55,.50)))
scene.include('electrical',electrical)

# Open A-frame aluminum stepladder. Front and back leg pairs are sloped in depth.
ladder = Asset('aluminum_folding_ladder')
top_z=2.17
top_y=3.08
top_x=.68
width=.48
front_y=1.80
rear_y=3.70
for side in (-1,1):
    x=top_x+side*width/2
    ladder.include('front_rail_'+str(side),rod(.045,start=(x,front_y,.06),
        end=(x,top_y,top_z),color=metal))
    ladder.include('rear_rail_'+str(side),rod(.042,start=(x,rear_y,.06),
        end=(x,top_y,top_z),color=metal))
    ladder.include('foot_front_'+str(side),box((.13,.17,.07),center=(x,front_y,.055),color=metal_dark))
    ladder.include('foot_rear_'+str(side),box((.13,.17,.07),center=(x,rear_y,.055),color=metal_dark))
for i in range(7):
    t=(i+1)/8
    z=.06+(top_z-.06)*t
    y=front_y+(top_y-front_y)*t
    ladder.include('front_step_%02d'%i,box((width+.09,.15,.045),
        center=(top_x,y,z),color=metal))
    if i<5:
        y2=rear_y+(top_y-rear_y)*t
        ladder.include('rear_rung_%02d'%i,rod(.022,start=(top_x-width/2,y2,z),
            end=(top_x+width/2,y2,z),color=metal_dark))
ladder.include('top_cap',box((width+.13,.18,.10),center=(top_x,top_y,top_z),color=(.40,.42,.40)))
for side in (-1,1):
    x=top_x+side*(width/2+.015)
    ladder.include('hinge_'+str(side),ball(.065,center=(x,top_y,top_z-.06),color=metal_dark))
    ladder.include('spreader_'+str(side),rod(.018,start=(x,2.26,.85),end=(x,3.45,.85),color=metal_dark))
# Red ladder label.
ladder.include('red_label',box((.015,.34,.055),center=(top_x-width/2-.046,2.13,.61),color=(.63,.08,.045)))
scene.include('ladder',ladder)

# Work light and cable on the left side.
worklight=Asset('temporary_work_light')
worklight.include('lamp_mount',box((.07,.13,.18),center=(-1.02,1.30,2.39),color=(.38,.33,.23)))
worklight.include('bulb',ball(.095,center=(-.95,1.30,2.39),color=(1.0,.86,.55)))
worklight.include('cable_upper',rod(.012,start=(-1.12,1.30,2.30),end=(-1.12,1.30,.38),color=(.12,.12,.10)))
scene.include('worklight',worklight)

# Irregular loose timber and small chunks of masonry on the floor.
debris=Asset('floor_debris')
for i in range(32):
    x=random.uniform(-.92,1.05)
    y=random.uniform(-.35,2.45)
    length=random.uniform(.30,1.12)
    angle=random.uniform(-math.pi,math.pi)
    dx=math.cos(angle)*length/2
    dy=math.sin(angle)*length/2
    z=random.uniform(.035,.075)
    debris.include('wood_strip_%02d'%i,rod(random.uniform(.012,.026),
        start=(x-dx,y-dy,z),end=(x+dx,y+dy,z+.01),
        color=random.choice([wood,wood_light,wood_dark,(.52,.35,.20)])))
for i in range(42):
    x=random.uniform(-1.14,1.14)
    y=random.uniform(-.5,3.45)
    size=random.uniform(.035,.13)
    debris.include('rubble_%02d'%i,box((size,size*random.uniform(.55,1.3),size*.35),
        center=(x,y,size*.17),color=random.choice([(.50,.46,.38),(.36,.32,.27),(.60,.55,.45)])))
scene.include('debris',debris)

realize(scene)

# Set the final aspect explicitly to the original photograph's 383:512.
sc=bpy.context.scene
sc.render.resolution_x=383
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.render.pixel_aspect_x=1
sc.render.pixel_aspect_y=1

if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(0.22,0.20,0.16,1)
background.inputs['Strength'].default_value=.35

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
area_emitter((-.85,1.15,2.48),power=260,size=.35,
    target=(0,2.5,1.2),color=(1.0,.72,.40))
area_emitter((.4,-1.5,2.65),power=300,size=3.0,
    target=(0,2.3,1.0),color=(1.0,.85,.65))
area_emitter((.65,4.0,2.05),power=90,size=1.0,
    target=(.2,1.2,1.1),color=(.45,.57,1.0))

# Small projection check. Reference estimates are independent of projections.
# These test directions only; the rendered image is needed to assess appearance.
landmarks=[
    ('window upper left',(.19,4.16,2.53),(.63,.10)),
    ('window lower right',(1.14,4.16,1.27),(.92,.43)),
    ('ladder front foot',(.44,1.80,.06),(.59,.79)),
    ('foreground left floor',(-1.15,-.1,0),(.25,.98)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    projection=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,'reference',ref,'projected',uv)

projection_table('Final camera landmark projections')
