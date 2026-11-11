# Reference inventory and visual estimates, normalized image coordinates:
# Foreground folding bench: top about (.07,.33)-(.91,.53), left foot (.28,.97),
# right foot (.87,.73). White apron and splayed legs surround large open gaps.
# Blue vise on front, yellow inserts, perforated panels, hanging clamps.
# Rear bench: orange top extends beyond left crop to about (.85,.29), with a
# log-end mosaic on its front; saw at left, blue drill, lamp and CNC on top.
# Background: dark lumber rack at upper left, corrugated wall, tools, stove and
# storage at right. Floor is visible around and through the foreground bench.
# Long bench edges slope upward to the right; foreground bench overlaps rear.
#
# Comparison with previous render: foreground top occupied roughly
# (.38,.49)-(.74,.61), versus reference (.07,.33)-(.91,.53); its left foot was
# near (.44,.70) versus (.28,.97). Rear bench was about (.19,.43)-(.70,.64),
# versus reference extending off the left edge and ending near (.85,.29).
# Rack occupied approximately (.03,.24)-(.30,.49), versus reference mostly
# (.00,.00)-(.42,.29). The render showed too much floor and a bright blank
# right wall. The bench silhouettes were too small and the background too pale.
# Largest corrections: increase camera image scale and lower camera elevation,
# bringing bench contours outward and feet downward; aim higher so background
# details enter the upper frame. Darken wall and lighting, and extend the wall
# to remove the prominent bright corner. Keep foreground/rear overlap.
# Camera trial projections below report old and candidate camera separately;
# the candidate is accepted only if its landmarks improve overall image-space
# agreement. Geometry and camera parameters remain independent.
#
# Primitive estimate: about 430 meshes: 220 log discs, 70 bench details,
# 35 architecture/rack pieces, 50 machine pieces, and 55 other details.
# Occluded backs and exact machine internals are uncertain.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(14)
scene = Scene("Woodworking shop")

BENCH_L, BENCH_D, BENCH_Z, BENCH_Y = 3.05, .84, .91, -.78
REAR_L, REAR_D, REAR_Y, REAR_Z = 4.8, .92, .93, 1.02
OLD_POS, OLD_TARGET, OLD_LENS = (-4.9,-7.6,4.65), (0,.28,.95), 40
CAM_POS, CAM_TARGET, CAM_LENS = (-3.7,-6.4,3.05), (0,.12,1.12), 65

white=(.77,.75,.67)
white_edge=(.88,.86,.77)
topmat=(.55,.36,.22)
orange=(.62,.34,.085)
blue=(.025,.16,.38)
yellow=(.95,.57,.015)
dark=(.065,.065,.06)
metal=(.30,.31,.29)
black=(.025,.028,.027)

def B(a,n,s,c,col):
    a.include(n,box(size=s,center=c,color=col))
def R(a,n,p,q,r,col):
    a.include(n,rod(radius=r,start=p,end=q,color=col))

room=Asset("Architecture")
B(room,"concrete_floor",(15,14,.12),(0,0,-.065),(.32,.32,.30))
B(room,"back_wall",(14,.13,5),(0,3.05,2.5),(.16,.16,.14))
B(room,"dark_left_bay",(3.1,.10,4),(-2.65,2.94,2),(.075,.07,.055))
# Wall ribs give the visible corrugated workshop backdrop.
for i in range(34):
    x=-1.0+i*.13
    B(room,"wall_rib_%02d"%i,(.026,.035,4.2),(x,2.96,2.1),(.105,.11,.105))
scene.include("architecture",room)

rear=Asset("Rear log faced workbench")
B(rear,"heavy_body",(REAR_L,REAR_D,.80),(0,REAR_Y,.50),(.13,.095,.06))
B(rear,"orange_worktop",(REAR_L+.05,REAR_D+.05,.075),(0,REAR_Y,REAR_Z),orange)
B(rear,"front_lip",(REAR_L+.05,.055,.10),(0,REAR_Y-REAR_D/2-.02,REAR_Z-.065),(.42,.23,.075))
B(rear,"rear_edge",(REAR_L,.055,.08),(0,REAR_Y+REAR_D/2,REAR_Z+.045),(.36,.20,.09))
logcols=[(.53,.41,.29),(.69,.56,.39),(.39,.29,.20),(.76,.64,.46)]
for row in range(5):
    z=.18+row*.155
    for col in range(24):
        x=-2.30+col*.20+(row%2)*.095
        if x>2.35: continue
        r=random.uniform(.065,.095)
        y=REAR_Y-REAR_D/2-.034
        R(rear,"bark_%d_%d"%(row,col),(x,y,z),(x,y-.017,z),r,(.11,.075,.05))
        R(rear,"grain_%d_%d"%(row,col),(x,y-.018,z),(x,y-.023,z),r*.78,random.choice(logcols))
scene.include("rear_bench",rear)

front=Asset("Folding birch plywood workbench")
B(front,"hardboard_top",(BENCH_L,BENCH_D,.055),(0,BENCH_Y,BENCH_Z),topmat)
B(front,"plywood_top_edge",(BENCH_L,BENCH_D,.045),(0,BENCH_Y,BENCH_Z-.045),(.73,.60,.43))
B(front,"front_white_apron",(BENCH_L-.04,.07,.17),(0,BENCH_Y-BENCH_D/2+.035,BENCH_Z-.16),white_edge)
B(front,"rear_white_apron",(BENCH_L-.04,.07,.15),(0,BENCH_Y+BENCH_D/2-.035,BENCH_Z-.15),white)
for x,label in [(-BENCH_L/2+.04,"left"),(BENCH_L/2-.04,"right")]:
    B(front,label+"_end_rail",(.08,BENCH_D,.15),(x,BENCH_Y,BENCH_Z-.14),white)
for i in range(10):
    for j in range(4):
        x=-1.27+i*.28
        y=BENCH_Y-.28+j*.18
        R(front,"top_dog_%d_%d"%(i,j),(x,y,BENCH_Z+.028),(x,y,BENCH_Z+.031),.010,(.25,.17,.12))
for i in range(14):
    x=-1.28+i*.197
    R(front,"apron_hole_%02d"%i,(x,BENCH_Y-BENCH_D/2-.003,BENCH_Z-.16),
      (x,BENCH_Y-BENCH_D/2-.009,BENCH_Z-.16),.014,(.24,.23,.20))
for side,x in (("left",-1.19),("right",1.19)):
    for face,y in (("front",BENCH_Y-.30),("back",BENCH_Y+.30)):
        footx=x+(-.15 if x<0 else .15)
        leg=box(size=(.20,.105,.84),center=((x+footx)/2,y,.45),color=white)
        leg.turn(axis="+y",degrees=(-10 if x<0 else 10))
        front.include(side+"_"+face+"_leg",leg)
        B(front,side+"_"+face+"_foot",(.22,.14,.045),(footx,y,.035),(.67,.65,.58))
    B(front,side+"_inner_panel",(.045,.53,.52),(x,BENCH_Y,.47),(.68,.65,.55))
    B(front,side+"_upper_crossbar",(.10,.66,.095),(x,BENCH_Y,.75),white_edge)
    outerx=x+(-.027 if x<0 else .027)
    for k in range(4):
        for m in range(3):
            y=BENCH_Y-.20+m*.18
            z=.28+k*.12
            R(front,side+"_panel_hole_%d_%d"%(k,m),(outerx,y,z),
              (outerx+(-.006 if x<0 else .006),y,z),.012,(.23,.22,.19))
for i,x in enumerate((-1.32,-.38,.47,1.25)):
    B(front,"yellow_stop_%d"%i,(.105,.075,.18),(x,BENCH_Y+.02,BENCH_Z-.16),yellow)
B(front,"front_left_yellow",(.13,.055,.17),(-1.34,BENCH_Y-.43,BENCH_Z-.18),yellow)
B(front,"vise_white_mount",(.48,.075,.23),(-.63,BENCH_Y-.46,.74),white_edge)
B(front,"vise_blue_body",(.38,.09,.09),(-.63,BENCH_Y-.515,.74),blue)
for i,x in enumerate((-.77,-.50)):
    R(front,"vise_bolt_%d"%i,(x,BENCH_Y-.565,.74),(x,BENCH_Y-.58,.74),.025,(.63,.64,.60))
R(front,"vise_screw",(-.64,BENCH_Y-.57,.74),(-.64,BENCH_Y-.70,.74),.028,metal)
R(front,"vise_handle",(-.82,BENCH_Y-.70,.85),(-.40,BENCH_Y-.70,.56),.025,metal)
R(front,"vise_handle_tip_a",(-.84,BENCH_Y-.70,.86),(-.80,BENCH_Y-.70,.83),.033,(.46,.09,.08))
R(front,"vise_handle_tip_b",(-.42,BENCH_Y-.70,.58),(-.38,BENCH_Y-.70,.55),.033,(.46,.09,.08))
for i in range(3):
    x=-1.30+i*.09
    R(front,"clamp_bar_%d"%i,(x,BENCH_Y-.39,.18),(x,BENCH_Y-.39,.71),.012,metal)
    B(front,"clamp_handle_%d"%i,(.045,.045,.13),(x,BENCH_Y-.40,.36+i*.035),(.90,.27,.025))
    B(front,"clamp_jaw_%d"%i,(.10,.06,.035),(x+.025,BENCH_Y-.39,.69),(.19,.20,.19))
scene.include("foreground_bench",front)

saw=Asset("Track saw")
B(saw,"silver_track",(1.15,.14,.018),(-1.85,REAR_Y-.26,REAR_Z+.05),(.67,.70,.68))
B(saw,"sole_plate",(.44,.29,.035),(-1.75,REAR_Y-.20,REAR_Z+.08),(.48,.50,.48))
B(saw,"blade_housing",(.30,.20,.19),(-1.75,REAR_Y-.20,REAR_Z+.18),(.69,.71,.68))
B(saw,"motor",(.14,.18,.15),(-1.56,REAR_Y-.20,REAR_Z+.18),(.31,.34,.32))
R(saw,"top_handle",(-1.88,REAR_Y-.18,REAR_Z+.29),(-1.63,REAR_Y-.18,REAR_Z+.29),.025,dark)
B(saw,"green_switch",(.06,.05,.04),(-1.61,REAR_Y-.19,REAR_Z+.28),(.18,.39,.12))
scene.include("track_saw",saw)

drill=Asset("Blue benchtop drill press")
dx,dy=-.89,REAR_Y+.02
B(drill,"base",(.32,.27,.045),(dx,dy,REAR_Z+.06),(.10,.14,.15))
R(drill,"column",(dx,dy,REAR_Z+.07),(dx,dy,REAR_Z+.66),.035,metal)
B(drill,"blue_head",(.22,.18,.14),(dx,dy,REAR_Z+.63),blue)
B(drill,"black_motor",(.14,.15,.18),(dx,dy+.11,REAR_Z+.65),dark)
B(drill,"work_table",(.24,.18,.035),(dx,dy-.04,REAR_Z+.30),blue)
R(drill,"chuck",(dx,dy-.06,REAR_Z+.55),(dx,dy-.06,REAR_Z+.37),.022,metal)
R(drill,"feed_lever",(dx+.10,dy,REAR_Z+.58),(dx+.23,dy,REAR_Z+.49),.012,black)
scene.include("drill_press",drill)

cnc=Asset("CNC gantry router")
cx,cy=.55,REAR_Y+.06
B(cnc,"black_base",(1.40,.68,.08),(cx,cy,REAR_Z+.09),(.10,.11,.10))
B(cnc,"sacrificial_board",(1.10,.49,.035),(cx,cy,REAR_Z+.15),(.64,.54,.39))
for i,x in enumerate((cx-.57,cx+.57)):
    B(cnc,"side_rail_%d"%i,(.065,.67,.10),(x,cy,REAR_Z+.19),(.24,.25,.24))
    B(cnc,"gantry_upright_%d"%i,(.08,.11,.38),(x,cy+.16,REAR_Z+.36),(.31,.32,.31))
B(cnc,"gantry_beam",(1.25,.11,.13),(cx,cy+.16,REAR_Z+.53),(.63,.65,.61))
B(cnc,"carriage",(.19,.15,.19),(cx+.06,cy+.10,REAR_Z+.49),(.14,.15,.14))
R(cnc,"router_spindle",(cx+.06,cy+.02,REAR_Z+.53),(cx+.06,cy+.02,REAR_Z+.24),.052,(.19,.19,.17))
B(cnc,"yellow_router_cap",(.13,.13,.07),(cx+.06,cy+.02,REAR_Z+.55),(.82,.61,.05))
scene.include("cnc_router",cnc)

lamp=Asset("Articulated task lamp")
lx,ly=-.53,REAR_Y+.30
B(lamp,"base",(.25,.18,.025),(lx,ly,REAR_Z+.055),(.58,.58,.53))
R(lamp,"lower_arm",(lx,ly,REAR_Z+.07),(lx-.05,ly,REAR_Z+.63),.016,(.65,.66,.62))
R(lamp,"upper_arm",(lx-.05,ly,REAR_Z+.63),(lx+.30,ly,REAR_Z+.91),.016,(.65,.66,.62))
R(lamp,"parallel_arm",(lx-.02,ly+.03,REAR_Z+.62),(lx+.32,ly+.03,REAR_Z+.88),.009,(.44,.45,.43))
R(lamp,"shade",(lx+.30,ly,REAR_Z+.91),(lx+.34,ly-.04,REAR_Z+.78),.085,(.72,.72,.66))
scene.include("task_lamp",lamp)

rack=Asset("Wall lumber rack")
for i,z in enumerate((1.28,1.69,2.10,2.51,2.92)):
    B(rack,"shelf_%d"%i,(2.58,.43,.075),(-2.10,2.67,z),(.13,.09,.055))
for i,x in enumerate((-3.31,-1.08)):
    B(rack,"post_%d"%i,(.07,.08,2.60),(x,2.48,1.65),(.10,.08,.06))
woodcols=[(.39,.24,.12),(.56,.36,.19),(.68,.48,.28),(.31,.20,.12)]
for level,z in enumerate((1.37,1.78,2.19,2.60,3.01)):
    for j in range(4):
        B(rack,"board_%d_%d"%(level,j),(random.uniform(1.1,2.35),.16,.045),
          (-2.15+random.uniform(-.22,.22),2.50+j*.075,z+j*.048),random.choice(woodcols))
scene.include("lumber_rack",rack)

stove=Asset("Cast iron stove")
B(stove,"firebox",(.75,.56,.62),(2.08,2.27,.46),(.055,.055,.05))
B(stove,"stove_top",(.82,.60,.07),(2.08,2.27,.80),(.08,.08,.075))
B(stove,"door",(.48,.025,.40),(2.08,1.975,.45),(.10,.10,.09))
B(stove,"door_panel",(.37,.018,.28),(2.08,1.958,.45),(.035,.035,.03))
for i,x in enumerate((1.79,2.37)):
    B(stove,"foot_%d"%i,(.10,.10,.18),(x,2.25,.09),dark)
R(stove,"chimney",(2.12,2.31,.81),(2.12,2.31,3.8),.10,dark)
scene.include("stove",stove)

storage=Asset("Tools and wall storage")
B(storage,"right_shelving",(.84,.35,1.48),(3.04,2.52,.76),(.12,.10,.08))
for row,z in enumerate((.35,.70,1.05,1.40)):
    B(storage,"shelf_%d"%row,(.88,.39,.045),(3.04,2.49,z),(.24,.16,.09))
    for i in range(4):
        B(storage,"bin_%d_%d"%(row,i),(.17,.25,.12),(2.73+i*.20,2.44,z+.08),
          (.30,.055,.035) if i%2 else (.10,.11,.10))
B(storage,"dark_tool_board",(1.38,.05,.38),(.18,2.90,2.25),(.09,.08,.06))
for i in range(12):
    x=-.38+i*.105
    R(storage,"hanging_tool_%d"%i,(x,2.86,1.81),(x,2.86,2.55+(i%3)*.08),.012,
      (.05,.05,.045) if i%3 else (.30,.13,.06))
scene.include("tool_storage",storage)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:
    background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:
    output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.26,.25,.22,1)
background.inputs["Strength"].default_value=.35
sc.render.resolution_x=511
sc.render.resolution_y=512
sc.render.resolution_percentage=100

landmarks=[
    ("front_top_left",(-BENCH_L/2,BENCH_Y-BENCH_D/2,BENCH_Z),(.08,.46)),
    ("front_top_right",(BENCH_L/2,BENCH_Y-BENCH_D/2,BENCH_Z),(.91,.39)),
    ("left_foot",(-1.35,BENCH_Y-.30,.035),(.28,.97)),
    ("rear_bench_left",(-REAR_L/2,REAR_Y-REAR_D/2,REAR_Z),(.00,.38)),
    ("rear_bench_right",(REAR_L/2,REAR_Y-REAR_D/2,REAR_Z),(.85,.29)),
]
def project_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    matrix=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    values=[]
    print(label, "landmark | reference | projected")
    for name,p,ref in landmarks:
        clip=matrix @ cam.matrix_world.inverted() @ Vector((*p,1))
        uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        values.append(uv)
        print(name,ref,None if uv is None else tuple(round(v,3) for v in uv))
    return values

set_view(OLD_POS,OLD_TARGET,lens=OLD_LENS)
old=project_table("previous")
# Test a small lens increase first; the predicted outward motion is measured.
sc.camera.data.lens=OLD_LENS*1.05
trial=project_table("small lens trial")
sc.camera.data.lens=OLD_LENS
# Candidate moves closer and lower, increasing foreground scale and reducing
# the excessive downward view. Retain it if landmark error improves overall.
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)
candidate=project_table("candidate")
def error(v):
    return sum((uv[0]-ref[0])**2+(uv[1]-ref[1])**2
               for uv,(_,p,ref) in zip(v,landmarks) if uv is not None)
if any(v is None for v in candidate) or error(candidate)>=error(old):
    set_view(OLD_POS,OLD_TARGET,lens=OLD_LENS)
    print("Candidate rejected; restored previous camera")
else:
    print("Candidate accepted; selected landmarks improved overall")

area_emitter((-3,-4,6),power=1000,size=5,target=(0,0,.5),color=(1,.83,.64))
area_emitter((3,1,4.5),power=650,size=4,target=(0,0,.5),color=(1,.89,.73))
area_emitter((lx+.32,ly-.05,REAR_Z+.78),power=65,size=.4,
             target=(lx+.25,ly-.05,REAR_Z),color=(1,.82,.58))
