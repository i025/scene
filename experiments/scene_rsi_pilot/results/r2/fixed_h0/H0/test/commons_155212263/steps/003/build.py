from sceneact import *
import bpy, math, random
random.seed(18)

scene=Scene("Old metalworking workshop")
counter=0
wood=(.25,.19,.115)
darkwood=(.16,.125,.078)
iron=(.105,.115,.11)
rust=(.23,.17,.105)
steel=(.36,.37,.34)
plaster=(.48,.53,.48)

def add(name,node):
    global counter
    counter+=1
    scene.include("%s_%05d"%(name,counter),node)
    return node

def B(name,size,pos,c):
    return add(name,box(size,center=pos,color=c))

def R(name,r,a,b,c=iron):
    return add(name,rod(r,start=a,end=b,color=c))

def T(name,pts,r,c=iron):
    return add(name,sweep_tube(points=pts,radius=r,color=c))

# Closely laid, long, weathered wooden floorboards.
B("floor_foundation",(24,18,.08),(0,-2,-.10),(.22,.18,.12))
for j in range(64):
    y=-9+j*.19
    for k in range(5):
        x=-10+k*3.8+(j%3)*.45
        v=random.uniform(-.035,.035)
        B("floorboard",(3.79,.183,.075),(x+1.9,y,-.043),
          (.38+v,.295+v,.19+v))
        for dx in (-1.82,1.82):
            for dy in (-.055,.055):
                R("nail",.006,(x+1.9+dx,y+dy,-.002),
                  (x+1.9+dx,y+dy,.001),(.13,.12,.095))

# Continuous wall with correctly filled window bays.
B("lower_plaster_wall",(18,.3,2.12),(-2,1.8,1.06),plaster)
B("upper_plaster_wall",(18,.3,1.4),(-2,1.8,5.1),plaster)
windows=[(-6.0,1.9),(-3.55,1.9),(-.9,2.05),(1.95,2.25)]
for x,w in windows:
    B("window_light",(w,.07,2.65),(x,1.91,3.5),(.77,.86,.89))
    B("deep_stone_sill",(w+.27,.66,.12),(x,1.53,2.16),(.29,.31,.27))
    for xx in (x-w/2,x+w/2):
        B("window_side_frame",(.065,.15,2.73),(xx,1.65,3.5),(.20,.25,.23))
    for xx in (x-w*.25,x,x+w*.25):
        B("glazing_bar",(.025,.10,2.67),(xx,1.64,3.5),(.36,.40,.37))
    for z in (2.19,3.25,4.83):
        B("window_cross_frame",(w+.1,.13,.048),(x,1.64,z),(.26,.30,.27))
for a,b in [(-11,-6.95),(-5.05,-4.5),(-2.6,-1.925),(.125,.825),(3.075,7)]:
    B("masonry_pier",(b-a,.32,3.3),((a+b)/2,1.8,3.6),plaster)
for i in range(130):
    x=random.uniform(-8,5)
    z=random.uniform(.12,2.05)
    B("plaster_stain",(random.uniform(.035,.28),.009,random.uniform(.04,.28)),
      (x,1.645,z),random.choice([(.40,.45,.40),(.54,.56,.49),(.45,.49,.43)]))

# Heavy continuous bench.
for j in range(5):
    B("bench_plank",(10.8,.25,.17),(-.75,-.025+j*.255,1.43+random.uniform(-.006,.006)),wood)
B("front_apron",(10.8,.14,.27),(-.75,-.2,1.22),darkwood)
B("back_apron",(10.8,.14,.24),(-.75,1.07,1.23),darkwood)
for x in [-5.7,-4.1,-2.4,-.5,1.5,3.9]:
    for y in (-.10,.98):
        B("bench_leg",(.19,.21,1.37),(x,y,.685),darkwood)
        B("foot",(.25,.28,.10),(x,y,.08),(.18,.145,.09))
    B("cross_stretcher",(.15,1.15,.16),(x,.44,.34),darkwood)
B("long_stretcher",(10,.15,.16),(-.6,.90,.34),darkwood)
for i in range(170):
    x=random.uniform(-5.9,4.5)
    y=random.uniform(-.13,1.1)
    B("worn_top_mark",(random.uniform(.02,.15),.008,.002),(x,y,1.522),(.40,.33,.22))

for x in (-4.8,-3.3,-1.8,-.4):
    B("drawer",(1.14,.12,.24),(x,-.28,1.08),(.19,.155,.095))
    R("drawer_handle",.025,(x-.12,-.37,1.10),(x+.12,-.37,1.10))
    for dx in (-.12,.12):
        R("handle_stud",.018,(x+dx,-.37,1.10),(x+dx,-.29,1.10))
# Open foreground drawer.
B("drawer_bottom",(1.30,.82,.055),(2.12,-.60,.92),(.20,.17,.105))
for x in (1.46,2.78):
    B("drawer_side",(.065,.86,.30),(x,-.60,1.05),(.24,.20,.13))
B("open_drawer_front",(1.42,.10,.37),(2.12,-1.05,1.05),(.18,.16,.105))
R("drawer_pull",.036,(1.97,-1.12,1.06),(2.28,-1.12,1.06),(.34,.32,.23))
for i in range(12):
    x=random.uniform(1.54,2.65)
    R("drawer_contents",.023,(x,-.87,.98),(x+.12,-.28,1),rust)

# Anvil on a rough wooden block.
B("anvil_stump",(.60,.64,1.13),(-.9,.13,.565),(.19,.13,.075))
B("anvil_feet",(.74,.55,.12),(-.9,.11,1.57),rust)
B("anvil_lower",(.50,.42,.16),(-.9,.11,1.69),(.25,.20,.13))
B("anvil_waist",(.32,.34,.29),(-.9,.11,1.85),(.29,.23,.15))
B("anvil_top",(.90,.43,.19),(-.87,.11,2.04),(.34,.29,.20))
B("anvil_heel",(.30,.38,.14),(-1.44,.11,2.04),(.31,.26,.18))
for i in range(22):
    t=i/22
    R("anvil_horn",.145*(1-t)+.006,
      (-.42+t*.67,.11,2.04),(-.42+(t+1/22)*.67,.11,2.04),(.33,.28,.19))

# Cast iron hand powered drilling machines, with broad curved spokes.
def wheel_machine(name,x,y,z,r):
    B(name+"_base",(.54,.45,.10),(x,y,1.58),iron)
    B(name+"_column",(.12,.15,z-1.52),(x+.10,y+.19,(z+1.52)/2),(.16,.17,.14))
    B(name+"_bearing",(.23,.25,.18),(x,y+.1,z),rust)
    R(name+"_shaft",.065,(x,y-.26,z),(x,y+.34,z),steel)
    for rr,thick in ((r,.043),(r-.065,.017)):
        T(name+"_rim",[(x+rr*math.cos(k*math.tau/80),y-.16,
                       z+rr*math.sin(k*math.tau/80)) for k in range(81)],thick)
    R(name+"_hub",.105,(x,y-.25,z),(x,y-.07,z),iron)
    for j in range(5):
        pts=[]
        for k in range(15):
            t=k/14
            rr=.07+(r-.09)*t
            angle=j*math.tau/5+.82*(1-t)
            pts.append((x+rr*math.cos(angle),y-.16,z+rr*math.sin(angle)))
        T(name+"_spoke",pts,.047 if r>.5 else .027)
    xx=x+r*.73
    zz=z-r*.32
    R(name+"_crank",.027,(xx,y-.17,zz),(xx,y-.43,zz),rust)
    R(name+"_grip",.045,(xx,y-.43,zz),(xx,y-.68,zz),(.27,.18,.09))
    B(name+"_table",(.52,.40,.075),(x+.05,y-.03,1.94),iron)
    R(name+"_spindle",.029,(x+.05,y-.03,1.78),(x+.05,y-.03,2.31),steel)
    R(name+"_feed",.035,(x+.12,y+.18,2.23),(x+.40,y+.18,2.23),iron)

wheel_machine("large_drill",1.25,.79,2.84,.62)
wheel_machine("middle_drill",-2.05,.63,2.24,.37)
wheel_machine("far_drill",-4.8,.65,1.99,.25)

# Main blacksmith's vise.
B("vise_mount",(.47,.48,.10),(2.70,.22,1.59),iron)
B("vise_neck",(.25,.28,.32),(2.70,.20,1.78),iron)
R("vise_barrel",.155,(2.18,.17,1.93),(3.15,.17,1.93),iron)
for x in (2.42,2.88):
    B("vise_jaw",(.16,.41,.32),(x,.17,2.06),iron)
    B("polished_jaw",(.17,.44,.065),(x,.17,2.235),(.34,.35,.31))
R("vise_screw",.048,(2.18,.17,1.93),(3.62,.17,1.93),steel)
for i in range(21):
    x=3.06+i*.024
    R("screw_thread",.058,(x,.17,1.93),(x+.009,.17,1.93),(.19,.20,.18))
R("screw_head",.086,(3.54,.17,1.93),(3.70,.17,1.93))
R("vise_handle",.027,(3.65,.17,1.50),(3.65,.17,2.14),steel)
for z in (1.49,2.15):
    add("handle_knob",ball(.047,center=(3.65,.17,z),color=iron))
B("vise_long_leg",(.13,.15,.98),(2.70,.12,1.05),iron)
B("vise_toe",(.27,.25,.10),(2.70,.10,.57),iron)

# Front leg vise and suspended handles.
B("small_vise_mount",(.36,.32,.08),(.1,-.05,1.58),rust)
R("small_vise_body",.10,(-.17,-.06,1.75),(.38,-.06,1.75))
for x in (-.065,.21):
    B("small_vise_jaw",(.10,.30,.24),(x,-.06,1.85),steel)
R("small_screw",.037,(-.22,-.06,1.75),(.48,-.06,1.75),steel)
R("small_handle",.022,(.44,-.06,1.45),(.44,-.06,1.89))
R("vise_forged_leg",.057,(.02,-.11,1.67),(.02,-.24,.35))
add("leg_tip",ball(.065,center=(.02,-.24,.35),color=iron))
for x in (-.20,.16):
    R("hanging_tongs",.021,(x,-.27,1.53),(x-.06,-.36,.26),rust)

# Files, chisels and other individual tools.
for i in range(18):
    x=random.uniform(.35,1.95)
    y=random.uniform(-.08,.50)
    length=random.uniform(.28,.65)
    R("file",.018,(x,y,1.56),(x+.11,y+length,1.56),steel)
    R("file_handle",.033,(x-.025,y-.14,1.56),(x,y,1.56),(.28,.18,.085))
for x,y,s in [(1.80,.08,.33),(2.06,.51,.28),(3.40,.53,.30),(-2.7,.25,.27)]:
    B("metal_plate",(s,.34,.025),(x,y,1.55),(.38,.39,.36))
    for dx in (-.08,.08):
        R("plate_hole",.018,(x+dx,y,1.565),(x+dx,y,1.57),(.065,.07,.065))
for x,y in [(-1.7,.08),(-3,.65),(-3.7,.3),(.5,.83),(-4.8,.25)]:
    R("hammer_shaft",.026,(x,y,1.57),(x+.36,y+.2,1.58),(.38,.26,.12))
    B("hammer_head",(.16,.29,.11),(x+.36,y+.2,1.62),iron)
for i in range(48):
    x=random.uniform(-5.8,-2.2)
    y=random.uniform(-.05,1)
    R("scattered_tool",random.uniform(.012,.028),(x,y,1.56),
      (x+random.uniform(.1,.34),y+random.uniform(.12,.42),1.57),steel)
for x in (-5.2,-4.2,-3.2,-2.65):
    B("tool_block",(.26,.23,.22),(x,.80,1.66),rust)
    R("upright_tool",.025,(x,.8,1.70),(x+.035,.8,2.04))
# Small secondary vices along the distant bench.
for x in (-5.3,-3.9,-3.0):
    B("distant_vise_base",(.30,.30,.08),(x,.2,1.58),iron)
    R("distant_vise_body",.075,(x-.24,.2,1.74),(x+.24,.2,1.74))
    for dx in (-.10,.09):
        B("distant_vise_jaw",(.075,.25,.19),(x+dx,.2,1.84),steel)
    R("distant_vise_handle",.018,(x+.28,.2,1.48),(x+.28,.2,1.86))

# Crowded window ledges.
for i in range(46):
    x=random.uniform(-6.8,3.0)
    y=1.40+random.uniform(-.06,.07)
    h=random.uniform(.09,.25)
    r=random.uniform(.035,.065)
    R("oil_can",r,(x,y,2.23),(x,y,2.23+h),
      random.choice([iron,steel,(.28,.20,.11),(.38,.36,.28)]))
    R("can_neck",r*.32,(x,y,2.23+h),(x,y,2.3+h))
    if i%3==0:
        R("oil_spout",.010,(x,y,2.29+h),(x+.09,y,2.42+h),steel)
for x in (-6,-5.5,-4.2,-3.7,-2.5,-1.4,.1,2.6):
    R("sill_tool",.018,(x,1.45,2.24),(x+.04,1.45,2.68))

# Pipes and wall-hung tools.
T("right_pipe",[(3.45,1.51,4.8),(3.45,1.51,3.4),(3.25,1.51,3.21),
                (3.25,1.51,2.05),(3.44,1.51,1.93)],.030,(.25,.27,.22))
T("left_pipe",[(-4.6,1.49,4.7),(-4.6,1.49,3.1),(-4.35,1.49,2.9),
               (-4.35,1.49,2.45)],.026,rust)
for x in (-5.6,-3.7,-2.8,-1.55,.1,3.1):
    R("wall_tool",.019,(x,1.51,2.47),(x+.10,1.51,3.46),rust)
    B("wall_tool_grip",(.065,.07,.23),(x+.09,1.49,3.40),(.23,.145,.068))
    T("tool_hanger",[(x-.04,1.49,3.5),(x-.04,1.49,3.59),
                     (x+.05,1.49,3.59),(x+.05,1.49,3.5)],.012)
R("long_leaning_handle",.041,(3.86,1.22,.04),(4.33,1.5,2.77),(.27,.17,.08))
R("leaning_bar",.025,(-3.5,-.05,.04),(-3.2,.25,1.39))

# Under-bench boxes and open pails.
def bucket(name,x,y,z,r,h,c):
    R(name+"_bottom",r*.87,(x,y,z),(x,y,z+.035),c)
    for j in range(56):
        a=j*math.tau/56
        R(name+"_wall",r*.059,
          (x+r*.86*math.cos(a),y+r*.86*math.sin(a),z),
          (x+r*math.cos(a),y+r*math.sin(a),z+h),c)
    for zz,rr in ((z+.05,r*.88),(z+h,r)):
        T(name+"_rim",[(x+rr*math.cos(k*math.tau/60),
                       y+rr*math.sin(k*math.tau/60),zz) for k in range(61)],
          .015,(.27,.27,.21))
    T(name+"_handle",[(x+r*math.cos(k*math.pi/30),y,
                       z+h+.27*math.sin(k*math.pi/30)) for k in range(31)],.012)

bucket("cream_pail",2.35,-.02,.03,.36,.68,(.49,.48,.38))
R("pail_contents",.23,(2.35,-.02,.07),(2.35,-.02,.48),(.14,.12,.075))
for i in range(7):
    B("pail_scrap",(.14,.12,.09),(2.35+random.uniform(-.13,.13),
      -.02+random.uniform(-.12,.12),.47+random.uniform(0,.09)),rust)
bucket("green_can",3.58,.22,.02,.38,.72,(.16,.22,.13))
R("green_lid",.39,(3.58,.22,.73),(3.58,.22,.77),(.21,.23,.14))
R("green_neck",.09,(3.58,.22,.77),(3.58,.22,.87),rust)
for x in (-5.0,-3.8,-2.4,-1.6):
    B("storage_box",(.64,.63,.57),(x,.53,.34),(.18,.20,.13))
    for i in range(4):
        B("stored_plank",(.055,.45,.65),(x-.22+i*.13,.52,.67),(.23,.17,.095))
for i in range(20):
    x=random.uniform(-1.5,1.5)
    R("stored_iron",.028,(x,.64,.12),(x+.18,.76,random.uniform(.4,.9)),rust)

# Visitor floor marker.
R("direction_disc",.34,(-1.6,-2.2,.002),(-1.6,-2.2,.008),(.25,.34,.35))
B("arrow_stem",(.13,.27,.006),(-1.6,-2.19,.014),(.75,.78,.71))
for x,ang in [(-1.68,-43),(-1.52,43)]:
    n=B("arrow_head",(.12,.27,.006),(x,-2.06,.014),(.75,.78,.71))
    n.turn("z",ang)

realize(scene)

# Preserve the explicit SceneAct colors in the shader.
for mat in bpy.data.materials:
    source=tuple(mat.diffuse_color)
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get("Principled BSDF")
    if bs is None:
        continue
    bs.inputs["Base Color"].default_value=source
    bs.inputs["Roughness"].default_value=.79
    noise=nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=24
    noise.inputs["Detail"].default_value=3
    ramp=nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(source[0]*.63,source[1]*.63,source[2]*.63,1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(min(source[0]*1.15,1),
        min(source[1]*1.15,1),min(source[2]*1.15,1),1)
    nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.18
    bump.inputs["Distance"].default_value=.012
    nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if abs(source[0]-source[1])<.04 and source[0]<.42:
        bs.inputs["Metallic"].default_value=.55
        bs.inputs["Roughness"].default_value=.53
    if source[2]>.8:
        bs.inputs["Emission Color"].default_value=(.72,.84,.91,1)
        bs.inputs["Emission Strength"].default_value=1.1

set_view((6,-7,4.8),(-.25,.35,1.10),lens=43)
area_emitter((-.8,1.1,4.5),power=1000,size=5,
             target=(-1,-1,1),color=(.81,.90,1))
area_emitter((0,-3,5.5),power=450,size=5,
             target=(0,.3,1),color=(1,.90,.75))
area_emitter((-5,0,3.7),power=240,size=3,
             target=(-3,0,1),color=(.85,.91,1))
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
bg=sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.24,.28,.30,1)
bg.inputs["Strength"].default_value=.23
sc.render.engine="CYCLES"
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=-.55
