from sceneact import *
import bpy, math, random
random.seed(12)

# Observations: reference benches fill the right edge and recede steeply left;
# feedback shows too much room, smaller machinery, and an exposed wall top.
# Estimated reference landmarks: main wheel (340,95), small wheel (182,108),
# anvil (220,149), foreground machine (402,206), floor marker (66,273).
# Main correction family: camera translation and aim. Moving closer increases
# foreground scale and parallax; the more oblique view steepens bench edges.
# Camera remains an uncertain estimate; geometry dimensions are preserved.
# Semantic builders: bench -> timber workstation; flywheel -> cast wheel;
# vice -> bench vice; can -> floor container. All movable parts stay grouped.

scene = Scene("Historic metalworking shop")
wood=(.25,.20,.13)
topwood=(.37,.31,.22)
iron=(.12,.135,.13)
steel=(.43,.46,.43)
rust=(.29,.21,.14)
plaster=(.57,.59,.53)

def B(a,k,s,p,c):
    return a.include(k,box(size=s,center=p,color=c))
def R(a,k,p,q,r,c):
    return a.include(k,rod(radius=r,start=p,end=q,color=c))
def T(a,k,pts,r,c):
    return a.include(k,sweep_tube(points=pts,radius=r,color=c))
def ring(a,k,p,r,t,c,plane="xz"):
    pts=[]
    for j in range(25):
        v=j*math.tau/24
        if plane=="xz":
            pts.append((p[0]+r*math.cos(v),p[1],p[2]+r*math.sin(v)))
        elif plane=="xy":
            pts.append((p[0]+r*math.cos(v),p[1]+r*math.sin(v),p[2]))
        else:
            pts.append((p[0],p[1]+r*math.cos(v),p[2]+r*math.sin(v)))
    return T(a,k,pts,t,c)

room=Asset("architecture")
B(room,"plank_floor",(16,16,.12),(0,-3,-.07),(.44,.36,.25))
B(room,"lower_wall",(13,.22,1.55),(0,1.72,.775),plaster)
B(room,"upper_wall",(13,.22,.6),(0,1.72,4.15),plaster)
B(room,"left_wall",(.16,7,4.4),(-6.1,-1.7,2.2),plaster)
for i,x in enumerate((-5.8,-3.65,-1.45,.78,3.02,5.3)):
    B(room,f"pier_{i}",(.29,.24,2.4),(x,1.72,2.72),plaster)
for i,x in enumerate((-4.72,-2.55,-.34,1.9,4.16)):
    B(room,f"sill_{i}",(1.98,.48,.12),(x,1.52,1.62),(.32,.33,.28))
    B(room,f"glass_{i}",(1.91,.035,2.12),(x,1.78,2.76),(.80,.87,.88))
    for j,xx in enumerate((x-.98,x,x+.98)):
        B(room,f"mullion_{i}_{j}",(.045,.10,2.25),(xx,1.69,2.77),(.36,.39,.37))
    B(room,f"crossbar_{i}",(1.98,.10,.045),(x,1.68,2.72),(.39,.41,.38))
scene.include("architecture",room)

def bench(x,w):
    a=Asset("heavy timber workstation")
    B(a,"top",(w,1,.16),(x,.48,1.05),topwood)
    B(a,"front_apron",(w,.11,.27),(x,-.015,.86),wood)
    B(a,"lower_shelf",(w-.22,.74,.065),(x,.47,.30),(.22,.20,.14))
    for i,xx in enumerate((x-w/2+.14,x+w/2-.14)):
        for j,y in enumerate((.10,.83)):
            B(a,f"leg_{i}_{j}",(.15,.16,.98),(xx,y,.49),wood)
        B(a,f"stretcher_{i}",(.13,.88,.12),(xx,.46,.29),wood)
    return a

for i,(x,w) in enumerate(((2,2.6),(-.45,2.2),(-2.5,1.8),(-4.3,1.65),(-5.65,.95))):
    scene.include(f"bench_{i}",bench(x,w))

def flywheel(x,y,z,r):
    a=Asset("cast iron flywheel")
    ring(a,"rim",(x,y,z),r,.032,iron)
    R(a,"hub",(x,y-.09,z),(x,y+.15,z),.065,steel)
    for j in range(5):
        t=j*math.tau/5
        pts=[]
        for k in range(5):
            f=k/4
            rr=.06+(r-.075)*f
            ang=t+.48*f
            pts.append((x+rr*math.cos(ang),y,z+rr*math.sin(ang)))
        T(a,f"curved_spoke_{j}",pts,.028,iron)
    R(a,"crank",(x+r*.77,y,z-.12),(x+r*.77,y-.27,z-.12),.025,rust)
    R(a,"wood_grip",(x+r*.77,y-.23,z-.12),(x+r*.77,y-.36,z-.12),.035,wood)
    return a

a=Asset("large wheel apparatus")
B(a,"base",(.55,.52,.10),(1.30,.69,1.18),iron)
B(a,"upright",(.12,.13,.92),(1.30,.78,1.66),rust)
B(a,"bearing",(.25,.26,.16),(1.30,.75,2.10),steel)
a.include("wheel",flywheel(1.30,.54,2.16,.49))
R(a,"axle",(1.30,.40,2.16),(1.30,1.12,2.16),.052,steel)
T(a,"belt",[(1.63,.58,2.47),(1.69,.59,2.05),(1.60,.60,1.19)],.015,(.14,.12,.09))
scene.include("large_wheel",a)

a=Asset("small wheel apparatus")
B(a,"base",(.53,.45,.09),(-1.52,.60,1.18),steel)
B(a,"column",(.13,.17,.46),(-1.52,.67,1.41),iron)
a.include("wheel",flywheel(-1.52,.49,1.75,.32))
scene.include("small_wheel",a)

a=Asset("foreground screw lathe")
B(a,"bed",(1.70,.36,.12),(2.10,.33,1.24),iron)
for i,x in enumerate((1.48,2.75)):
    B(a,f"foot_{i}",(.32,.48,.07),(x,.33,1.165),iron)
    B(a,f"support_{i}",(.15,.24,.36),(x,.33,1.37),iron)
    B(a,f"bearing_{i}",(.27,.34,.12),(x,.33,1.55),steel)
R(a,"workshaft",(1.26,.30,1.55),(3.10,.30,1.55),.069,steel)
R(a,"headstock",(1.49,.30,1.55),(1.95,.30,1.55),.15,iron)
R(a,"collar",(1.90,.30,1.55),(2.04,.30,1.55),.18,iron)
B(a,"head_top",(.40,.30,.13),(1.74,.31,1.73),iron)
B(a,"top_handle",(.31,.08,.075),(1.73,.31,1.835),steel)
R(a,"wood_end_grip",(2.95,.30,1.55),(3.30,.30,1.55),.075,(.49,.43,.32))
B(a,"sliding_jaw",(.23,.35,.28),(2.32,.28,1.44),iron)
R(a,"lever",(2.31,.10,1.43),(2.31,-.25,1.26),.028,steel)
scene.include("foreground_lathe",a)

a=Asset("anvil")
x,y,z=-.63,.34,1.13
for k,s,p in (
    ("foot",(.57,.42,.08),(x,y,z+.04)),
    ("base",(.37,.30,.19),(x,y,z+.15)),
    ("waist",(.25,.28,.20),(x+.015,y,z+.31)),
    ("shoulder",(.43,.34,.17),(x,y,z+.45)),
    ("face",(.69,.37,.13),(x+.02,y,z+.57)),
    ("heel",(.18,.34,.12),(x-.39,y,z+.56))):
    B(a,k,s,p,rust)
for i in range(5):
    xx=x+.34+i*.078
    R(a,f"horn_{i}",(xx,y,z+.55),(xx+.085,y,z+.55),.145*(1-i/5)+.006,rust)
B(a,"hardy_hole",(.055,.055,.006),(x-.31,y,z+.638),(.065,.065,.05))
scene.include("anvil",a)

def vice(x,scale):
    a=Asset("bench vice")
    z=1.12
    B(a,"mount",(.26,.31,.08),(x,-.045,z),iron)
    B(a,"body",(.28,.26,.25),(x,-.155,z-.02),iron)
    B(a,"front_jaw",(.30,.10,.21),(x,-.365,z+.065),steel)
    B(a,"fixed_jaw",(.30,.09,.17),(x,-.185,z+.11),steel)
    R(a,"screw",(x,-.275,z-.03),(x,-.615,z-.03),.045,steel)
    R(a,"handle",(x-.02,-.625,z-.24),(x+.02,-.625,z+.17),.018,steel)
    if scale!=1:
        a.resize((scale,scale,scale),pivot=(x,-.045,z))
    return a

for i,x in enumerate((.02,-2.52,-3.96,-5.15)):
    scene.include(f"vice_{i}",vice(x,.95 if i<2 else .75))

a=Asset("open drawer")
B(a,"bottom",(.96,.69,.055),(1.16,-.39,.76),(.24,.23,.17))
B(a,"front",(.99,.075,.25),(1.16,-.75,.85),(.20,.21,.17))
for i,x in enumerate((.69,1.63)):
    B(a,f"side_{i}",(.055,.69,.22),(x,-.40,.85),(.30,.29,.20))
B(a,"back",(.96,.05,.20),(1.16,-.06,.85),wood)
R(a,"handle",(.99,-.81,.86),(1.32,-.81,.86),.025,iron)
scene.include("drawer",a)

a=Asset("loose worktop tools")
for i in range(12):
    x=random.uniform(-5.6,2.8)
    y=random.uniform(.09,.83)
    length=random.uniform(.18,.40)
    R(a,f"file_{i}",(x,y,1.16),(x+length,y+.06,1.17),.015,steel)
    if i%3==0:
        R(a,f"wood_handle_{i}",(x-.14,y-.025,1.16),(x,y,1.16),.028,wood)
        B(a,f"hammer_head_{i}",(.09,.18,.06),(x+length,y+.06,1.18),iron)
for i,(x,y) in enumerate(((1.72,-.01),(2.77,.69),(.73,.02),(-2.03,.05))):
    plate=B(a,f"sheet_{i}",(.36,.27,.025),(x,y,1.15),(.53,.54,.49))
    plate.turn("z",random.uniform(-17,17))
for i in range(5):
    R(a,f"parallel_file_{i}",(-2.3+i*.11,.25,1.16),(-2.3+i*.11,.70,1.16),.017,(.58,.57,.49))
for i in range(4):
    B(a,f"block_{i}",(.19,.28,.13),(-4.9+i*.65,.73,1.195),(.40,.29,.17))
scene.include("worktop_clutter",a)

a=Asset("windowsill clutter")
for i in range(16):
    x=random.uniform(-5.6,2.7)
    y=random.uniform(1.31,1.49)
    h=random.uniform(.10,.27)
    R(a,f"can_{i}",(x,y,1.69),(x,y,1.69+h),random.uniform(.03,.06),
      random.choice((steel,iron,rust)))
    if i%4==0:
        R(a,f"brush_{i}",(x,y,1.75+h),(x+.02,y,1.94+h),.012,wood)
scene.include("sill_objects",a)

a=Asset("wall hardware")
for i,(x,z) in enumerate(((-3.52,2.2),(-1.36,2.12),(.79,2.2),(3.03,2.3))):
    R(a,f"shaft_{i}",(x,1.50,z-.55),(x+.07,1.50,z+.14),.016,rust)
    ring(a,f"loop_{i}",(x+.07,1.50,z+.20),.065,.012,iron)
T(a,"bent_pipe",[(3,1.47,3.8),(3,1.47,2.7),(2.9,1.46,2.5),
                  (2.88,1.46,1.9),(3.03,1.46,1.73)],.025,iron)
R(a,"leaning_handle",(3.2,1.30,.15),(3.70,1.45,2.5),.043,wood)
R(a,"left_pipe",(-5.8,1.36,1.60),(-5.8,1.36,3.8),.032,iron)
scene.include("wall_tools",a)

def can(x,y,r,h,c):
    a=Asset("floor container")
    R(a,"body",(x,y,.03),(x,y,h),r,c)
    R(a,"dark_opening",(x,y,h+.001),(x,y,h+.008),r*.88,(.075,.075,.052))
    ring(a,"rim",(x,y,h+.012),r,.014,steel,"xy")
    return a

for key,x,y,r,h,c in (
    ("white_bucket",1.72,-.32,.30,.59,(.64,.64,.53)),
    ("olive_can",3.03,.05,.32,.69,(.17,.22,.14)),
    ("cropped_copper_can",3.55,-.53,.28,.43,(.37,.25,.13)),
    ("back_bucket",-2.78,.20,.22,.46,(.29,.30,.24))):
    scene.include(key,can(x,y,r,h,c))

a=Asset("underbench clutter")
for i,x in enumerate((-.8,-.1,.5,2.75)):
    B(a,f"box_{i}",(.40,.43,.27),(x,.54,.47),(.22,.19,.13))
for i in range(3):
    R(a,f"leaning_rod_{i}",(.02+i*.06,-.27,.05),(-.12+i*.05,-.10,1.05),.017,rust)
scene.include("underbench_objects",a)

a=Asset("floor marker")
R(a,"disk",(-2,-2,.005),(-2,-2,.012),.32,(.37,.43,.43))
B(a,"arrow_stem",(.10,.23,.006),(-2,-2.02,.018),(.81,.83,.78))
for i in range(4):
    B(a,f"arrow_tip_{i}",(.29-i*.065,.045,.006),(-2,-1.92+i*.035,.019),(.81,.83,.78))
scene.include("floor_marker",a)

# Audit: all primitive sizes/radii positive, endpoints distinct, loop keys unique.
# No fillet boxes or bind dependencies. Bench top z=1.13 supports the equipment.
realize(scene)

def descendants(key):
    root=bpy.data.objects.get(key)
    return [o for o in root.children_recursive if o.type=="MESH"] if root else []

# Correct the visibly oversized floor pattern using world-space coordinates.
floor_mat=bpy.data.materials.new("worn longitudinal floorboards")
floor_mat.use_nodes=True
n=floor_mat.node_tree.nodes
l=floor_mat.node_tree.links
bs=n.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.83
geo=n.new("ShaderNodeNewGeometry")
mapping=n.new("ShaderNodeVectorMath")
mapping.operation="MULTIPLY"
mapping.inputs[1].default_value=(1,.22,1)
l.new(geo.outputs["Position"],mapping.inputs[0])
brick=n.new("ShaderNodeTexBrick")
brick.offset=.5
brick.offset_frequency=2
brick.inputs["Scale"].default_value=1
brick.inputs["Brick Width"].default_value=.22
brick.inputs["Row Height"].default_value=.62
brick.inputs["Mortar Size"].default_value=.002
brick.inputs["Mortar Smooth"].default_value=.001
brick.inputs["Color1"].default_value=(.40,.32,.21,1)
brick.inputs["Color2"].default_value=(.53,.44,.30,1)
brick.inputs["Mortar"].default_value=(.17,.14,.095,1)
l.new(mapping.outputs["Vector"],brick.inputs["Vector"])
l.new(brick.outputs["Color"],bs.inputs["Base Color"])
bump=n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.3
bump.inputs["Distance"].default_value=.014
l.new(brick.outputs["Fac"],bump.inputs["Height"])
l.new(bump.outputs["Normal"],bs.inputs["Normal"])
for ob in descendants("plank_floor"):
    ob.data.materials.clear()
    ob.data.materials.append(floor_mat)

for mat in list(bpy.data.materials):
    if mat==floor_mat:
        continue
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value=.76

glass_mat=bpy.data.materials.new("pale daylight glass")
glass_mat.use_nodes=True
bs=glass_mat.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(.78,.86,.89,1)
bs.inputs["Roughness"].default_value=.6
bs.inputs["Emission Color"].default_value=(.70,.80,.86,1)
bs.inputs["Emission Strength"].default_value=.7
for i in range(5):
    for ob in descendants(f"glass_{i}"):
        ob.data.materials.clear()
        ob.data.materials.append(glass_mat)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("World")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.55,.62,.67,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.32
area_emitter((-.5,1.1,4.6),power=1100,size=5,
             target=(-.7,-.5,.5),color=(.85,.93,1))
area_emitter((-4,-3,4),power=420,size=4,
             target=(-1,.3,1),color=(1,.88,.70))

# Lens is preserved; closer position and lower aim correct framing and parallax.
set_view((4.7,-4.7,3.65),(0,.35,.75),lens=36,sensor=36,shift=(0,0))
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.render.engine="CYCLES"
sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.05
# External runner performs saving and rendering.
