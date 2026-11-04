from sceneact import *
import bpy, math, random
random.seed(18)

scene = Scene("Historic metalworking workshop")
wood=(.25,.19,.115)
edgewood=(.19,.145,.09)
iron=(.16,.17,.16)
rust=(.24,.19,.13)
steel=(.37,.38,.35)
wall=(.56,.59,.53)

def add(name,node):
    scene.include(name,node)
    return node

def B(name,size,pos,color):
    return add(name,box(size,center=pos,color=color))

def R(name,r,a,b,c=iron):
    return add(name,rod(r,start=a,end=b,color=c))

def tube(name,pts,r,c=iron):
    return add(name,sweep_tube(points=pts,radius=r,color=c))

# Individual worn floorboards.
for j in range(46):
    y=-6+j*.195
    for k in range(4):
        x=-7+k*3.4+(j%3)*.34
        col=(.43+random.uniform(-.045,.045),
             .35+random.uniform(-.035,.035),
             .235+random.uniform(-.025,.025))
        B("floorboard_%s_%s"%(j,k),(3.387,.187,.085),(x+1.69,y,-.05),col)
        for end in (-1.58,1.58):
            for dy in (-.057,.057):
                R("floor_nail",.007,(x+1.69+end,y+dy,-.004),
                  (x+1.69+end,y+dy,.003),(.15,.14,.11))

# Pale plaster wall with tall daylight windows.
B("wall_lower",(15,.26,1.9),(-1,1.75,.95),wall)
B("wall_upper",(15,.26,.65),(-1,1.75,4.85),wall)
for x,w in [(-7,.8),(-4.65,.28),(-1.75,.3),(1.25,.34),(4.2,.5)]:
    B("window_pier",(w,.29,3.05),(x,1.75,3),wall)
for x,w in [(-5.8,2),(-3.2,2.45),(-.25,2.55),(2.7,2.35)]:
    B("window_sill",(w+.28,.65,.13),(x,1.53,2.17),(.34,.34,.28))
    B("window_glass",(w,.055,2.22),(x,1.82,3.37),(.76,.85,.86))
    for xx in (x-w/2,x,x+w/2):
        B("window_frame",(.055,.12,2.28),(xx,1.68,3.37),(.27,.3,.28))
    for z in (2.25,3.35,4.49):
        B("window_crossbar",(w+.1,.13,.055),(x,1.67,z),(.27,.3,.28))
    for xx in (x-w*.25,x+w*.25):
        B("thin_glazing_bar",(.022,.08,2.2),(xx,1.64,3.36),(.48,.5,.45))

for i in range(95):
    x=random.uniform(-7,5)
    z=random.uniform(.15,2.06)
    c=random.choice([(.46,.48,.41),(.63,.63,.55),(.51,.53,.46)])
    B("plaster_wear",(random.uniform(.03,.27),.008,random.uniform(.025,.19)),
      (x,1.608,z),c)

# Long timber workbench.
for j in range(5):
    B("bench_top_board",(10.3,.252,.17),
      (-.8,-.02+j*.258,1.43+random.uniform(-.009,.009)),wood)
B("front_apron",(10.3,.14,.3),(-.8,-.2,1.18),edgewood)
B("back_apron",(10.3,.12,.25),(-.8,1.07,1.22),edgewood)
for x in [-5.6,-3.9,-2.15,-.3,1.5,3.7]:
    for y in [-.12,.98]:
        B("bench_leg",(.19,.21,1.33),(x,y,.67),(.155,.13,.088))
        B("leg_foot",(.27,.29,.13),(x,y,.1),(.19,.17,.12))
    B("lower_stretcher",(.17,1.14,.14),(x,.43,.35),edgewood)
B("long_lower_rail",(9.65,.15,.18),(-.85,.9,.38),edgewood)
for i in range(100):
    x=random.uniform(-5.9,4.1)
    y=random.uniform(-.12,1.08)
    B("bench_scratch",(random.uniform(.025,.18),.006,.002),
      (x,y,1.522),(.46,.39,.26))

for x in [-4.6,-3.05,-1.4]:
    B("drawer_front",(1.14,.12,.24),(x,-.28,1.08),(.21,.18,.12))
    R("drawer_pull",.027,(x-.12,-.365,1.1),(x+.12,-.365,1.1))
    for xx in [x-.12,x+.12]:
        R("drawer_pull_stud",.02,(xx,-.36,1.1),(xx,-.29,1.1))

B("open_drawer_bottom",(1.3,.75,.065),(2.12,-.55,.92),(.22,.20,.14))
for x in [1.46,2.78]:
    B("open_drawer_side",(.065,.8,.3),(x,-.55,1.05),(.24,.21,.14))
B("open_drawer_face",(1.4,.09,.38),(2.12,-.98,1.04),(.19,.18,.13))
R("open_drawer_handle",.035,(1.98,-1.05,1.05),(2.28,-1.05,1.05),(.38,.35,.22))
for i in range(9):
    x=random.uniform(1.55,2.65)
    R("drawer_scrap",.025,(x,-.7,.98),(x+.12,-.25,1.02),rust)

# Anvil.
B("anvil_stump",(.62,.65,1.12),(-.9,.13,.57),(.20,.15,.09))
B("anvil_base",(.73,.53,.13),(-.9,.11,1.56),rust)
B("anvil_waist",(.37,.35,.35),(-.9,.11,1.78),(.27,.23,.17))
B("anvil_crown",(.88,.43,.22),(-.87,.11,1.99),(.36,.32,.25))
for i in range(18):
    t=i/18
    R("anvil_horn",.155*(1-t)+.009,
      (-.42+t*.65,.11,1.99),(-.42+(t+1/18)*.65,.11,1.99),(.36,.32,.25))
B("anvil_heel",(.32,.39,.14),(-1.47,.11,2.02),(.32,.29,.23))

# Hand-cranked workshop machinery.
def wheel_machine(name,x,y,z,r):
    B(name+"_foot",(.56,.5,.09),(x,y,1.58),iron)
    B(name+"_column",(.115,.14,z-1.56),
      (x+.09,y+.18,(z+1.56)/2),(.23,.23,.19))
    B(name+"_bearing",(.24,.27,.17),(x,y+.12,z),rust)
    R(name+"_axle",.065,(x,y-.22,z),(x,y+.35,z),steel)
    for rr,thickness,c in [(r,.045,iron),(r-.065,.018,(.32,.33,.3))]:
        tube(name+"_rim",
             [(x+rr*math.cos(j*math.tau/72),y-.16,
               z+rr*math.sin(j*math.tau/72)) for j in range(73)],thickness,c)
    R(name+"_hub",.105,(x,y-.24,z),(x,y-.09,z))
    for j in range(5):
        a=j*math.tau/5
        pts=[]
        for k in range(13):
            t=k/12
            rr=.08+(r-.11)*t
            aa=a+.7*(1-t)
            pts.append((x+rr*math.cos(aa),y-.16,z+rr*math.sin(aa)))
        tube(name+"_curved_spoke",pts,.035)
    a=-.65
    xx=x+r*.76*math.cos(a)
    zz=z+r*.76*math.sin(a)
    R(name+"_crank",.027,(xx,y-.16,zz),(xx,y-.43,zz),rust)
    R(name+"_wood_grip",.05,(xx,y-.44,zz),(xx,y-.66,zz),(.30,.23,.14))
    B(name+"_tool_table",(.54,.44,.08),(x+.06,y-.01,1.99),iron)
    R(name+"_drill_spindle",.027,(x+.08,y-.06,1.82),(x+.08,y-.06,2.32),steel)

wheel_machine("large_flywheel",1.25,.79,2.83,.62)
wheel_machine("smaller_flywheel",-2.05,.62,2.24,.37)
wheel_machine("distant_wheel",-4.8,.65,1.98,.23)

# Dominant foreground vise.
B("vise_mount",(.48,.5,.12),(2.7,.22,1.59),iron)
B("vise_pedestal",(.26,.29,.32),(2.7,.2,1.78),iron)
R("vise_body",.145,(2.22,.17,1.93),(3.14,.17,1.93),(.20,.21,.19))
for x in [2.42,2.88]:
    B("vise_jaw_upright",(.14,.39,.31),(x,.17,2.05),(.20,.21,.19))
    B("vise_jaw_face",(.17,.44,.065),(x,.17,2.225),(.43,.43,.38))
R("vise_screw",.048,(2.18,.17,1.93),(3.58,.17,1.93),steel)
for i in range(18):
    x=3.05+i*.023
    R("screw_thread",.058,(x,.17,1.93),(x+.009,.17,1.93),(.24,.25,.23))
R("vise_handle_hub",.085,(3.53,.17,1.93),(3.68,.17,1.93))
R("vise_tommy_bar",.026,(3.64,.17,1.56),(3.64,.17,2.15),steel)
for z in [1.55,2.16]:
    add("vise_handle_end",ball(.047,center=(3.64,.17,z),color=iron))
B("vise_long_leg",(.115,.14,.92),(2.7,.12,1.04),iron)
B("vise_leg_toe",(.28,.28,.09),(2.7,.09,.59),iron)

B("small_vise_base",(.36,.32,.08),(.1,-.05,1.58),rust)
R("small_vise_barrel",.095,(-.16,-.06,1.74),(.39,-.06,1.74))
for x in [-.06,.21]:
    B("small_vise_jaw",(.09,.29,.23),(x,-.06,1.85),steel)
R("small_vise_handle",.021,(.43,-.06,1.46),(.43,-.06,1.87))
R("hanging_vise_leg",.055,(.02,-.11,1.66),(.02,-.23,.38))
add("hanging_leg_tip",ball(.065,center=(.02,-.23,.38),color=iron))

# Tools scattered over the bench.
for i in range(12):
    x=random.uniform(.35,1.9)
    y=random.uniform(-.05,.47)
    length=random.uniform(.28,.64)
    R("loose_file",.018,(x,y,1.56),(x+.1,y+length,1.56),steel)
    R("file_wood_handle",.035,(x-.025,y-.13,1.56),(x,y,1.56),(.30,.21,.12))
for x,y,s in [(1.8,.09,.31),(2.05,.51,.26),(3.38,.55,.3),(-2.7,.25,.27)]:
    B("steel_plate",(s,.34,.025),(x,y,1.55),(.43,.44,.40))
    for dx in [-.08,.08]:
        R("plate_dark_hole",.018,(x+dx,y,1.565),(x+dx,y,1.571),(.09,.10,.09))
for x,y in [(-1.7,.08),(-3.0,.65),(-3.7,.3),(.5,.83)]:
    R("hammer_handle",.025,(x,y,1.57),(x+.35,y+.2,1.58),(.43,.31,.16))
    B("hammer_head",(.15,.29,.11),(x+.35,y+.2,1.62),iron)
for i in range(18):
    x=random.uniform(-5.5,-2.3)
    y=random.uniform(.02,1)
    R("background_metal_tool",random.uniform(.012,.03),(x,y,1.55),
      (x+random.uniform(.1,.35),y+random.uniform(.1,.4),1.57),steel)
for x in [-4.2,-3.2,-2.65]:
    B("small_tool_block",(.28,.24,.24),(x,.8,1.67),rust)
    R("standing_tool",.025,(x,.8,1.7),(x+.03,.8,2.02))

# Oil cans and jars on window sills.
for i in range(24):
    x=random.uniform(-6.4,3.8)
    y=1.42+random.uniform(-.07,.06)
    h=random.uniform(.09,.26)
    r=random.uniform(.035,.073)
    R("sill_can",r,(x,y,2.25),(x,y,2.25+h),
      random.choice([iron,steel,(.30,.24,.16)]))
    R("oil_can_neck",r*.3,(x,y,2.25+h),(x,y,2.31+h))
    if i%3==0:
        R("oil_spout",.012,(x,y,2.3+h),(x+.09,y,2.42+h),steel)
for x in [-5.8,-3.9,-1.2,.8,3.4]:
    R("ledge_hand_tool",.018,(x,1.48,2.25),(x+.04,1.48,2.68))

tube("wall_pipe",[(3.66,1.52,4.65),(3.66,1.52,3.85),(3.46,1.52,3.68),
                  (3.46,1.52,2.1),(3.67,1.52,1.92)],.035,(.28,.29,.24))
tube("left_pipe",[(-4.5,1.48,4.7),(-4.5,1.48,3.1),
                  (-4.3,1.48,2.8),(-4.3,1.48,2.45)],.027,rust)
for x in [-3.7,-2.8,-1.55,.1,3.9]:
    R("hanging_wall_rod",.019,(x,1.51,2.5),(x+.1,1.51,3.56),rust)
    B("wall_tool_handle",(.075,.075,.23),(x+.09,1.49,3.48),(.25,.17,.095))
R("leaning_long_handle",.042,(3.86,1.25,.06),(4.35,1.53,2.77),(.34,.24,.12))
R("leaning_iron_bar",.025,(-3.5,-.05,.05),(-3.2,.25,1.38))

# Open containers under the bench.
def bucket(name,x,y,z,r,h,c):
    R(name+"_base",r*.91,(x,y,z),(x,y,z+.035),c)
    for j in range(40):
        a=j*math.tau/40
        R(name+"_side",r*.081,
          (x+r*.86*math.cos(a),y+r*.86*math.sin(a),z),
          (x+r*math.cos(a),y+r*math.sin(a),z+h),c)
    for zz,rr in [(z+.05,r*.88),(z+h,r)]:
        tube(name+"_rim",
             [(x+rr*math.cos(k*math.tau/48),
               y+rr*math.sin(k*math.tau/48),zz) for k in range(49)],
             .018,(.31,.31,.25))

bucket("cream_bucket",2.35,-.02,.03,.36,.66,(.55,.54,.43))
R("bucket_contents",.23,(2.35,-.02,.07),(2.35,-.02,.48),(.19,.17,.12))
bucket("green_can",3.58,.22,.02,.38,.72,(.23,.28,.19))
R("green_can_lid",.39,(3.58,.22,.73),(3.58,.22,.77),(.25,.27,.19))
R("green_can_neck",.09,(3.58,.22,.77),(3.58,.22,.87),rust)
for x in [-4.7,-3.4,-1.9]:
    B("underbench_box",(.65,.62,.58),(x,.52,.34),(.23,.24,.17))
    for i in range(4):
        B("stored_board",(.055,.45,.63),(x-.22+i*.13,.52,.65),(.26,.21,.13))
for i in range(10):
    x=random.uniform(-1.5,1.5)
    R("underbench_scrap",.035,(x,.62,.12),
      (x+.18,.75,random.uniform(.4,.8)),rust)

# Floor direction disc and painted arrow.
R("floor_marker",.34,(-1.6,-2.2,.002),(-1.6,-2.2,.007),(.32,.40,.40))
B("arrow_stem",(.13,.25,.006),(-1.6,-2.21,.014),(.78,.80,.73))
a=B("arrow_left",(.12,.28,.006),(-1.68,-2.08,.014),(.78,.80,.73))
a.turn('z',-43)
a=B("arrow_right",(.12,.28,.006),(-1.52,-2.08,.014),(.78,.80,.73))
a.turn('z',43)

realize(scene)

# Procedural surface variation.
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    col=tuple(bs.inputs["Base Color"].default_value)
    bs.inputs["Roughness"].default_value=.82
    noise=nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=27
    noise.inputs["Detail"].default_value=3
    noise.inputs["Roughness"].default_value=.75
    ramp=nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.17
    ramp.color_ramp.elements[0].color=(col[0]*.58,col[1]*.58,col[2]*.58,1)
    ramp.color_ramp.elements[1].position=.83
    ramp.color_ramp.elements[1].color=(
        min(col[0]*1.22,1),min(col[1]*1.22,1),min(col[2]*1.22,1),1)
    nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.22
    bump.inputs["Distance"].default_value=.025
    nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if abs(col[0]-col[1])<.035 and col[0]<.46:
        bs.inputs["Metallic"].default_value=.55
        bs.inputs["Roughness"].default_value=.5
    if col[2]>.75:
        bs.inputs["Emission Color"].default_value=(.72,.83,.87,1)
        bs.inputs["Emission Strength"].default_value=.65

set_view((6.5,-7.8,5.0),(-.65,.38,1.55),lens=44)
area_emitter((-.8,-2.2,6.3),power=1250,size=6,target=(-.5,.3,1),color=(1,.94,.81))
area_emitter((-.8,1.2,4.3),power=1700,size=5,target=(-1,-1,1),color=(.80,.91,1))
area_emitter((-5,-.5,3.8),power=500,size=3,target=(-3,0,1),color=(.85,.91,1))

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Workshop ambient world")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.22,.24,.25,1)
background.inputs["Strength"].default_value=.35

sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.25
