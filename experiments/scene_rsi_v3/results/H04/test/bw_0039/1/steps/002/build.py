# Reference inventory and visual anchors, normalized image coordinates:
# Door jamb at x=0.00–0.13; exposed left studs at x=0.13–0.46.
# Rear brick wall fills the upper background; window outer frame x=0.62–0.92,
# y=0.09–0.43. Its lower pane and right edge are partly covered by the ladder.
# Electrical box x=0.15–0.25, y=0.36–0.50. Bright work lamp x=0.32–0.45,
# near the upper edge. Ladder spans roughly x=0.56–1.00, y=0.22–0.80:
# its front rails slope upward to the right, with visible gaps between steps.
# Floor rubble and broken strips span x=0.25–1.00, y=0.70–1.00.
# Studs and jambs are nearly vertical; floor edges converge at the rear.
# Brick behind the framing, the ladder's far legs, and the window exterior
# are partly occluded and their exact construction remains uncertain.
#
# Comparison with the previous complete render:
# Window reference bounds about (0.62,0.09)–(0.92,0.43); rendered about
# (0.50,0.37)–(0.66,0.53). Ladder reference foot about (0.59,0.79);
# rendered about (0.58,0.74). Foreground left floor reference about
# (0.25,0.98); rendered about (0.09,0.90). The rendered lamp was around
# (0.24,0.34), while the reference is near (0.40,0.10).
# Largest differences, ranked: (1) the rear wall and window are too small
# and low, and the empty region above the wall is absent from the reference;
# (2) a large bright right wall obscures the rear, unlike the photograph;
# (3) ladder rails appear nearly vertical rather than diagonal, and the
# ladder is too small; (4) the image is too pale and evenly illuminated.
# Corrections: BACK_Y moves the rear wall toward the camera, enlarging the
# window and raising its top; camera aim is lowered and turned left, shifting
# stationary landmarks upward and right. Taller walls eliminate the top crop.
# The right wall is reduced to a narrow foreground jamb. Ladder top X is moved
# right of its feet, making the rails rise rightward; its front and rear depth
# spread is retained. Darker surfaces and localized warm light restore contrast.
# A numerical baseline/trial/final camera table below checks camera directions;
# geometry projections are not evidence of rendered visibility.
#
# Estimated primitive meshes: room and framing ~90, window ~16, ladder ~28,
# electrical and lamp ~8, debris ~95; approximately 237 total.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(21)
scene = Scene('Room under renovation')

# Camera and major dimensions are separately editable.
ROOM_W = 2.55
ROOM_H = 3.75
BACK_Y = 3.15
CAMERA_POSITION = (0.0, -3.55, 1.67)
OLD_TARGET = (0.10, 2.35, 1.48)
CAMERA_TARGET = (-0.35, 2.35, 1.22)
CAMERA_LENS = 32

wood = (.25, .115, .050)
wood_light = (.40, .22, .105)
wood_dark = (.105, .050, .024)
brick = (.29, .245, .17)
mortar = (.19, .17, .125)
metal = (.51, .54, .52)
metal_dark = (.23, .26, .25)
white = (.73, .73, .65)
blue = (.018, .055, .085)

room = Asset('room_enclosure')
room.include('floor', box((ROOM_W, 6.7, .12),
    center=(0, .8, -.07), color=(.34, .32, .26)))
# A window opening assembled from four wall sections.
wl, wr, wb, wt = .10, 1.12, 1.23, 2.62
room.include('back_left', box((wl+ROOM_W/2, .15, ROOM_H),
    center=((-ROOM_W/2+wl)/2, BACK_Y, ROOM_H/2), color=brick))
room.include('back_right', box((ROOM_W/2-wr, .15, ROOM_H),
    center=((wr+ROOM_W/2)/2, BACK_Y, ROOM_H/2), color=brick))
room.include('back_below', box((wr-wl, .15, wb),
    center=((wl+wr)/2, BACK_Y, wb/2), color=brick))
room.include('back_above', box((wr-wl, .15, ROOM_H-wt),
    center=((wl+wr)/2, BACK_Y, (wt+ROOM_H)/2), color=brick))
room.include('left_brick_backing', box((.12, 4.1, ROOM_H),
    center=(-1.28, 1.1, ROOM_H/2), color=(.20,.16,.10)))

# Irregular masonry lines, visible on the far wall around the window.
for i in range(23):
    z = .10 + i*.16
    intervals = [(-1.25,1.25)] if z < wb or z > wt else [(-1.25,wl),(wr,1.25)]
    for j,(a,b) in enumerate(intervals):
        if b-a > .04:
            room.include('mortar_%02d_%d'%(i,j), box((b-a,.012,.012),
                center=((a+b)/2,BACK_Y-.081,z), color=mortar))
    for j in range(3):
        x = -1.05 + j*.80 + (.35 if i%2 else 0)
        if x < 1.24 and not (wl-.03 < x < wr+.03 and wb < z < wt):
            room.include('joint_%02d_%d'%(i,j), box((.012,.014,.135),
                center=(x,BACK_Y-.083,z+.075), color=mortar))
for i in range(10):
    z=.09+i*.072
    room.include('rear_lath_%02d'%i, box((2.42,.032,.045),
        center=(0,BACK_Y-.11,z),color=wood_light if i%3 else wood))
scene.include('room', room)

framing = Asset('exposed_timber_framework')
for i,y in enumerate((-.45,.15,.72,1.27,1.82,2.38,2.95)):
    framing.include('stud_%02d'%i,box((.11,.105,ROOM_H),
        center=(-1.17,y,ROOM_H/2),color=wood_dark if i%2==0 else wood))
framing.include('bottom_plate',box((.13,3.7,.10),
    center=(-1.17,1.20,.07),color=wood))
for i in range(30):
    z=.16+i*.105
    framing.include('left_lath_%02d'%i,box((.025,3.55,.040),
        center=(-1.235,1.30,z),color=wood_light if i%4 else wood_dark))
framing.include('left_door_jamb',box((.15,.20,ROOM_H),
    center=(-1.30,-.45,ROOM_H/2),color=(.48,.40,.23)))
framing.include('left_inner_trim',box((.07,.21,ROOM_H),
    center=(-1.17,-.48,ROOM_H/2),color=(.22,.14,.07)))
framing.include('right_door_jamb',box((.11,.17,ROOM_H),
    center=(1.30,-.45,ROOM_H/2),color=(.49,.44,.32)))
scene.include('framing',framing)

window = Asset('white_double_hung_window')
cx=(wl+wr)/2
window.include('dark_recess',box((wr-wl+.09,.04,wt-wb+.10),
    center=(cx,BACK_Y+.035,(wb+wt)/2),color=(.045,.040,.028)))
window.include('upper_glass',box((.82,.035,.57),
    center=(cx,BACK_Y-.005,2.27),color=(.035,.075,.095)))
window.include('lower_glass',box((.82,.035,.53),
    center=(cx,BACK_Y-.005,1.58),color=blue))
for name,x in [('left',wl),('right',wr)]:
    window.include('outer_'+name,box((.10,.10,1.48),
        center=(x,BACK_Y-.095,(wb+wt)/2),color=white))
for name,z in [('top',wt),('bottom',wb),('meeting_rail',1.90)]:
    window.include(name,box((1.11,.10,.085),
        center=(cx,BACK_Y-.095,z),color=white))
for i,x in enumerate((wl+.10,wr-.10)):
    window.include('sash_side_%d'%i,box((.04,.06,1.19),
        center=(x,BACK_Y-.15,1.94),color=(.58,.59,.53)))
window.include('sill',box((1.18,.17,.08),
    center=(cx,BACK_Y-.14,1.20),color=(.57,.55,.47)))
for i in range(7):
    x=wl+.15+i*.115
    window.include('lower_glass_reflection_%d'%i,box((.012,.008,.36),
        center=(x,BACK_Y-.03,1.56),color=(.025,.105,.20)))
scene.include('window',window)

electrical=Asset('electrical_box_and_conduit')
electrical.include('body',box((.19,.27,.43),center=(-1.04,.05,1.53),
    color=(.69,.70,.66)))
electrical.include('lid',box((.025,.26,.40),center=(-.935,.05,1.53),
    color=(.81,.81,.74)))
electrical.include('red_cap',box((.12,.14,.035),center=(-1.02,.04,1.765),
    color=(.37,.06,.04)))
electrical.include('conduit',rod(.018,start=(-1.04,.05,1.30),
    end=(-1.04,.05,.10),color=(.42,.42,.38)))
scene.include('electrical',electrical)

# The front pair shifts right with height, reproducing the prominent diagonal.
ladder=Asset('folding_aluminum_ladder')
TOP_X, TOP_Y, TOP_Z = .98, 2.22, 2.35
FOOT_X, FRONT_Y, REAR_Y = .12, .80, 2.90
LADDER_WIDTH=.43
for side in (-1,1):
    fx=FOOT_X+side*LADDER_WIDTH/2
    tx=TOP_X+side*LADDER_WIDTH/2
    ladder.include('front_rail_%s'%side,rod(.045,
        start=(fx,FRONT_Y,.06),end=(tx,TOP_Y,TOP_Z),color=metal))
    ladder.include('rear_rail_%s'%side,rod(.040,
        start=(1.18+side*LADDER_WIDTH/2,REAR_Y,.06),
        end=(tx,TOP_Y,TOP_Z),color=metal))
    ladder.include('front_foot_%s'%side,box((.12,.16,.065),
        center=(fx,FRONT_Y,.05),color=metal_dark))
    ladder.include('hinge_%s'%side,ball(.06,
        center=(tx,TOP_Y,TOP_Z-.04),color=metal_dark))
for i in range(7):
    t=(i+1)/8
    x=FOOT_X+(TOP_X-FOOT_X)*t
    y=FRONT_Y+(TOP_Y-FRONT_Y)*t
    z=.06+(TOP_Z-.06)*t
    ladder.include('step_%d'%i,box((LADDER_WIDTH+.07,.13,.048),
        center=(x,y,z),color=metal))
for side in (-1,1):
    ladder.include('spreader_%s'%side,rod(.018,
        start=(.44+side*LADDER_WIDTH/2,1.35,.92),
        end=(1.10+side*LADDER_WIDTH/2,2.65,.92),color=metal_dark))
ladder.include('top_cap',box((LADDER_WIDTH+.12,.16,.09),
    center=(TOP_X,TOP_Y,TOP_Z),color=(.36,.39,.37)))
# A narrow red marking on the near front rail.
ladder.include('red_label',rod(.020,start=(.02,.93,.27),
    end=(.26,1.32,.90),color=(.54,.045,.025)))
scene.include('ladder',ladder)

worklight=Asset('temporary_warm_work_light')
worklight.include('mount',box((.08,.12,.18),
    center=(-1.03,.92,2.62),color=(.26,.20,.13)))
worklight.include('bulb',ball(.10,center=(-.94,.92,2.62),
    color=(1.0,.88,.63)))
worklight.include('cable',rod(.012,start=(-1.12,.92,2.56),
    end=(-1.12,.92,.35),color=(.08,.08,.07)))
scene.include('work_light',worklight)

debris=Asset('broken_lath_and_rubble')
for i in range(42):
    x=random.uniform(-.85,1.10)
    y=random.uniform(-.65,1.55)
    length=random.uniform(.25,1.05)
    angle=random.uniform(-math.pi,math.pi)
    dx,dy=math.cos(angle)*length/2,math.sin(angle)*length/2
    z=random.uniform(.025,.09)
    debris.include('strip_%02d'%i,rod(random.uniform(.012,.027),
        start=(x-dx,y-dy,z),end=(x+dx,y+dy,z+.01),
        color=random.choice([wood,wood_light,wood_dark,(.45,.29,.14)])))
for i in range(55):
    x=random.uniform(-1.18,1.18)
    y=random.uniform(-.8,2.65)
    s=random.uniform(.025,.13)
    debris.include('rubble_%02d'%i,box((s,s*random.uniform(.5,1.3),s*.32),
        center=(x,y,s*.16),
        color=random.choice([(.39,.36,.29),(.25,.22,.17),(.48,.43,.34)])))
scene.include('debris',debris)

realize(scene)
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
background.inputs['Color'].default_value=(.15,.13,.10,1)
background.inputs['Strength'].default_value=.28

# The trial aim change is checked before restoring and setting the final camera.
landmarks=[
    ('window upper left',(wl,BACK_Y-.095,wt),(.63,.10)),
    ('window lower right',(wr,BACK_Y-.095,wb),(.92,.43)),
    ('ladder front foot',(FOOT_X-LADDER_WIDTH/2,FRONT_Y,.06),(.59,.79)),
    ('foreground floor edge',(-1.15,-.45,0),(.25,.98)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv=None if clip.w<=1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        print(name,'reference',ref,'projected',uv)

set_view(CAMERA_POSITION,OLD_TARGET,lens=CAMERA_LENS,sensor=36)
projection_table('Baseline camera on revised geometry')
set_view(CAMERA_POSITION,(-.05,2.35,1.38),lens=CAMERA_LENS,sensor=36)
projection_table('Small leftward and downward aim trial')
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
projection_table('Final camera')

area_emitter((-.90,.85,2.65),power=210,size=.25,
    target=(0,2.0,1.4),color=(1.0,.68,.35))
area_emitter((.2,-1.0,2.8),power=120,size=2.5,
    target=(0,2.0,1.0),color=(1.0,.83,.62))
area_emitter((.7,3.0,2.0),power=28,size=.8,
    target=(.2,1.2,1.0),color=(.40,.53,1.0))
