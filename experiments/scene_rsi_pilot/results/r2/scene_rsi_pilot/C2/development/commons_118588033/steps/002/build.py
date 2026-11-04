from sceneact import *
import bpy
import math

# Inventory: cream ship compartment, rust-red deck, exposed overhead beams,
# three port berths, two vented cabinets and bench, rear lockers, chair,
# equipment chest, open cage, painted column, fire station, board, right bench.
# Near anchors: column foot and cropped benches. Far anchors: locker bank,
# rear pipes and partition. Cage rails occlude the chair and lockers.
# Scale and concealed construction are hypotheses.
#
# Revision family: CAMERA only.
# Observation (visual estimate): rendered column is left of the reference,
# rear lockers are too low and small, and the ceiling occupies too much frame.
# Hypothesis: camera distance, lateral position and pitch jointly explain the
# different near/far anchor errors. Focal length alone cannot explain them.
# Affected module: camera. No dependent supports or assembly geometry change.
# Intended change: approach the enclosure, aim downward, and narrow the view.
# Preservation risk: foreground lamp and cabinet cropping may change.
# Runtime fact: step 1 completed successfully; the revised view is untested.

scene = Scene('Shipboard compartment')

CAMERA_POSITION = (.67, -3.60, 1.72)
CAMERA_TARGET = (-.16, 2.60, .91)
CAMERA_LENS = 32.0
ROOM_WIDTH = 3.9
CEILING_Z = 3.22

cream = (.60,.59,.47)
pale = (.70,.70,.60)
steel = (.43,.48,.46)
dark = (.065,.085,.075)
red = (.42,.105,.065)
deck = (.32,.125,.075)
green = (.075,.15,.12)
white = (.77,.78,.70)

def cube(parent, key, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    return parent.include(key, box(size=size, center=center, color=color))

def tube(parent, key, a, b, radius=.018, color=dark):
    assert math.isfinite(radius) and radius > 0
    assert sum((a[i]-b[i])**2 for i in range(3)) > 0
    return parent.include(key, rod(radius=radius, start=a, end=b, color=color))

# Architecture remains outside furniture groups.
cube(scene,'deck',(4.5,11,.15),(0,1,-.085),deck)
cube(scene,'port_wall',(.14,10,3.3),(-1.96,1.1,1.57),cream)
cube(scene,'rear_wall',(4,.16,3.25),(0,5.9,1.57),cream)
cube(scene,'starboard_wall',(.15,9,3.3),(1.98,1.5,1.57),pale)
cube(scene,'overhead',(4.1,10,.13),(0,1.1,3.28),(.34,.29,.20))
cube(scene,'right_partition',(1.15,.16,3.2),(1.39,3.44,1.6),pale)
cube(scene,'right_partition_skirt',(1.15,.035,.28),(1.39,3.335,.14),red)
cube(scene,'port_skirt',(.035,9,.22),(-1.865,1,.11),(.19,.105,.067))
for i,y in enumerate([-3,-1.1,.9,2.9,4.8]):
    cube(scene,'overhead_crossbeam_%d'%i,(3.95,.15,.22),
         (0,y,3.12),(.48,.32,.19))
for i,x in enumerate([-1.55,-.85,.1,1.3]):
    cube(scene,'overhead_longitudinal_%d'%i,(.09,9.5,.16),
         (x,1.1,3.12),(.47,.36,.23))
for i,y in enumerate([-.7,1.5,3.7]):
    tube(scene,'diagonal_ceiling_brace_%d'%i,
         (-1.83,y,2.7),(-.95,y+.5,3.18),.035,pale)

column=Asset('Painted structural column')
cx,cy=.88,-.15
tube(column,'lower_shaft',(cx,cy,.04),(cx,cy,1.49),.104,(.32,.105,.055))
tube(column,'upper_shaft',(cx,cy,1.49),(cx,cy,3.2),.104,(.66,.49,.25))
tube(column,'foot',(cx,cy,.018),(cx,cy,.07),.139,(.37,.16,.085))
tube(column,'capital',(cx,cy,3.10),(cx,cy,3.22),.15,(.50,.35,.17))
scene.include('structural_column',column)

berths=Asset('Three tier sleeping berths')
BX,BY=-1.35,1.65
BERTH_LENGTH=3.55
for i,z in enumerate([.62,1.24,1.86]):
    cube(berths,'tray_%d'%i,(.92,BERTH_LENGTH,.065),(BX,BY,z),(.23,.27,.23))
    cube(berths,'mattress_%d'%i,(.86,BERTH_LENGTH-.10,.105),
         (BX,BY,z+.075),(.65,.67,.59))
    cube(berths,'folded_bedding_%d'%i,(.77,.6,.075),
         (BX,BY+1.18,z+.16),(.74,.75,.67))
    tube(berths,'outer_edge_%d'%i,(-.87,BY-1.78,z),(-.87,BY+1.78,z),.025,dark)
for i,y in enumerate([-.15,3.45]):
    for j,x in enumerate([-1.82,-.86]):
        tube(berths,'upright_%d_%d'%(i,j),(x,y,.06),(x,y,2.48),.021,dark)
    tube(berths,'end_top_%d'%i,(-1.82,y,2.48),(-.86,y,2.48),.018,dark)
scene.include('berths',berths)

port_bench=Asset('Port equipment bench')
cube(port_bench,'top',(.72,4.8,.095),(-1.55,-.47,.45),green)
for i,y in enumerate([-2.5,-.4,1.5]):
    for j,x in enumerate([-1.85,-1.23]):
        tube(port_bench,'leg_%d_%d'%(i,j),(x,y,.02),(x,y,.43),.025,dark)
scene.include('port_bench',port_bench)

for index,y in enumerate([-1.51,-.76]):
    cabinet=Asset('Vented equipment cabinet %d'%index)
    cube(cabinet,'body',(.48,.61,.79),(-1.60,y,.9),(.11,.20,.17))
    cube(cabinet,'top_lip',(.54,.66,.045),(-1.60,y,1.305),dark)
    cube(cabinet,'front_inset',(.018,.51,.67),(-1.348,y,.90),(.045,.065,.055))
    for j in range(15):
        cube(cabinet,'louver_%02d'%j,(.026,.46,.016),
             (-1.329,y,.59+j*.042),(.31,.36,.31))
    for k,yy in enumerate([y-.269,y+.269]):
        cube(cabinet,'front_rail_%d'%k,(.04,.035,.73),(-1.32,yy,.90),steel)
    scene.include('vented_cabinet_%d'%index,cabinet)

vent=Asset('Wall ventilation unit')
cube(vent,'case',(.18,.66,.67),(-1.80,.65,2.40),(.62,.63,.53))
cube(vent,'dark_opening',(.035,.52,.49),(-1.69,.65,2.39),(.055,.065,.057))
for j in range(6):
    cube(vent,'blade_%d'%j,(.07,.49,.037),(-1.66,.65,2.18+j*.075),(.59,.61,.53))
scene.include('wall_ventilator',vent)

lockers=Asset('Steel locker bank')
for i,x in enumerate([-.68,-.22,.24]):
    cube(lockers,'cabinet_%d'%i,(.445,.58,1.63),(x,4.38,1.12),(.45,.49,.46))
    cube(lockers,'door_%d'%i,(.414,.025,1.55),(x,4.073,1.13),(.49,.53,.50))
    for j,z in enumerate([.37,1.86]):
        cube(lockers,'hinge_%d_%d'%(i,j),(.025,.035,.06),(x-.18,4.047,z),(.25,.29,.27))
    cube(lockers,'handle_%d'%i,(.027,.045,.14),(x+.12,4.032,1.12),(.14,.17,.15))
    for j in range(5):
        cube(lockers,'vent_%d_%d'%(i,j),(.19,.012,.014),
             (x,4.052,1.58+j*.044),(.23,.28,.26))
    for j,xx in enumerate([x-.15,x+.15]):
        cube(lockers,'foot_%d_%d'%(i,j),(.045,.40,.21),(xx,4.38,.20),dark)
    cube(lockers,'label_%d'%i,(.13,.012,.05),(x,4.049,1.34),(.70,.70,.60))
scene.include('rear_lockers',lockers)

cage=Asset('Open metal enclosure')
for i,x in enumerate([-.66,.81]):
    for j,y in enumerate([1.47,4.48]):
        tube(cage,'post_%d_%d'%(i,j),(x,y,.02),(x,y,2.64),.022,dark)
for i,z in enumerate([.08,1.12,2.62]):
    tube(cage,'front_crossrail_%d'%i,(-.66,1.47,z),(.81,1.47,z),.019,dark)
    tube(cage,'right_rail_%d'%i,(.81,1.47,z),(.81,4.48,z),.018,dark)
tube(cage,'upper_left_rail',(-.66,1.47,2.64),(-.66,4.48,2.64),.018,dark)
for j,y in enumerate([2.05,2.65,3.25,3.85]):
    tube(cage,'right_vertical_%d'%j,(.81,y,.1),(.81,y,2.62),.010,(.13,.15,.12))
scene.include('enclosure',cage)

chair=Asset('Cream metal chair')
sx,sy=-.03,2.70
cube(chair,'seat',(.43,.45,.065),(sx,sy,.49),(.47,.48,.36))
cube(chair,'back',(.43,.07,.34),(sx,sy+.20,.86),(.54,.54,.42))
for i,x in enumerate([sx-.18,sx+.18]):
    for j,y in enumerate([sy-.17,sy+.17]):
        tube(chair,'leg_%d_%d'%(i,j),(x,y,.02),(x,y,.48),.018,(.51,.51,.40))
    tube(chair,'back_support_%d'%i,(x,sy+.18,.44),(x,sy+.22,1.01),.018,pale)
    tube(chair,'arm_%d'%i,(x,sy-.13,.70),(x,sy+.20,.70),.018,pale)
    tube(chair,'arm_support_%d'%i,(x,sy-.13,.49),(x,sy-.13,.70),.015,pale)
scene.include('chair',chair)

chest=Asset('Dark rear equipment chest')
cube(chest,'body',(.68,.67,.76),(.56,2.97,.44),(.22,.25,.21))
cube(chest,'lid',(.73,.72,.065),(.56,2.97,.85),(.28,.29,.23))
cube(chest,'front_edge',(.025,.025,.71),(.24,2.62,.45),(.39,.40,.32))
for i,x in enumerate([.32,.80]):
    cube(chest,'latch_%d'%i,(.055,.035,.11),(x,2.605,.72),(.42,.43,.34))
scene.include('equipment_chest',chest)

board=Asset('Wall notice board')
cube(board,'frame',(.70,.065,.69),(1.38,3.319,2.04),(.31,.32,.27))
cube(board,'surface',(.65,.017,.64),(1.38,3.277,2.04),(.23,.28,.25))
scene.include('notice_board',board)

fire=Asset('Red fire station')
cube(fire,'backplate',(.33,.055,.55),(1.23,3.315,1.18),(.72,.075,.035))
tube(fire,'cylinder',(1.23,3.22,1.00),(1.23,3.22,1.37),.105,(.78,.065,.025))
fire.include('shoulder',ball(.105,center=(1.23,3.22,1.37),color=(.78,.065,.025)))
tube(fire,'valve',(1.23,3.22,1.40),(1.23,3.22,1.49),.025,steel)
cube(fire,'handle',(.16,.055,.035),(1.23,3.22,1.47),(.32,.27,.18))
fire.include('hose',sweep_tube(
    points=[(1.27,3.18,1.47),(1.35,3.17,1.40),
            (1.35,3.17,1.18),(1.29,3.16,1.13)],
    radius=.016,color=dark))
cube(fire,'label',(.09,.015,.14),(1.23,3.105,1.21),(.84,.77,.57))
scene.include('fire_station',fire)

right_bench=Asset('Cropped starboard bench')
cube(right_bench,'seat',(.64,2.55,.075),(1.62,-1.77,.48),(.055,.14,.11))
for i,y in enumerate([-2.8,-.75]):
    for j,x in enumerate([1.37,1.87]):
        tube(right_bench,'leg_%d_%d'%(i,j),(x,y,.01),(x,y,.45),.024,dark)
    tube(right_bench,'crossbar_%d'%i,(1.37,y,.18),(1.87,y,.18),.018,dark)
scene.include('right_bench',right_bench)

pipes=Asset('Overhead and rear service pipes')
for i,x in enumerate([-1.53,-.90,.51]):
    tube(pipes,'ceiling_run_%d'%i,(x,-3,2.92),(x,5.4,2.92),.038,pale)
    for j,y in enumerate([-.5,1.5,3.7]):
        tube(pipes,'clamp_%d_%d'%(i,j),(x,y,2.87),(x,y,3.12),.014,(.30,.31,.25))
pipes.include('port_elbow',sweep_tube(
    points=[(-1.73,-1.4,3.15),(-1.73,-1.4,2.85),
            (-1.47,-1.4,2.74),(-.76,-1.4,2.74),(-.63,-1.4,2.93)],
    radius=.045,color=(.69,.70,.60)))
pipes.include('rear_cream_pipe',sweep_tube(
    points=[(.93,5.35,3.19),(.93,5.35,2.48),
            (.64,5.35,2.48),(.64,5.35,.33)],
    radius=.052,color=pale))
tube(pipes,'rear_black_vertical',(.43,4.80,.2),(.43,4.80,2.87),.035,dark)
tube(pipes,'rear_black_horizontal',(-1.20,4.80,2.87),(.43,4.80,2.87),.035,dark)
scene.include('service_pipes',pipes)

for i,(x,y,z,r) in enumerate([
        (-.79,-.65,2.66,.26),(-.49,2.06,2.57,.15),(-.18,4.15,2.50,.12)]):
    lamp=Asset('Pendant lamp %d'%i)
    tube(lamp,'stem',(x,y,z+.09),(x,y,3.15),.022,(.25,.28,.24))
    shade=ball(r,center=(x,y,z),color=(.60,.64,.61))
    shade.resize((1,1,.38))
    lamp.include('shade',shade)
    diffuser=ball(r*.90,center=(x,y,z-.055),color=(.97,.98,.89))
    diffuser.resize((1,1,.095))
    lamp.include('diffuser',diffuser)
    scene.include('pendant_%d'%i,lamp)

# Source preflight: positive finite dimensions, nonzero rods and sweep segments;
# indexed child keys are unique. All movable supports and fittings are members
# of their semantic assemblies. No bindings or composite parent transforms.
# Geometry and appearance remain identical to the successful first build.
realize(scene)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.43,.35,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.32

area_emitter((-.8,-.65,2.52),power=155,size=.65,target=(-.7,-.5,0),color=(1,.91,.73))
area_emitter((-.49,2.06,2.47),power=110,size=.5,target=(-.2,2,0),color=(.91,.96,1))
area_emitter((.1,4.6,2.7),power=100,size=.9,target=(0,3.3,1),color=(1,.96,.81))
area_emitter((.5,-3.5,2.5),power=110,size=3,target=(0,1,1),color=(1,.88,.72))

# Preserve the previous semantic pendant material customization.
for obj in bpy.data.objects:
    if obj.type=='MESH' and 'diffuser' in obj.name.lower():
        for slot in obj.material_slots:
            if slot.material:
                slot.material=slot.material.copy()
                slot.material.use_nodes=True
                bs=slot.material.node_tree.nodes.get('Principled BSDF')
                if bs:
                    if 'Emission Color' in bs.inputs:
                        bs.inputs['Emission Color'].default_value=(.9,.95,1,1)
                        bs.inputs['Emission Strength'].default_value=3
                    elif 'Emission' in bs.inputs:
                        bs.inputs['Emission'].default_value=(.9,.95,1,1)
sc.view_settings.view_transform='AgX'
