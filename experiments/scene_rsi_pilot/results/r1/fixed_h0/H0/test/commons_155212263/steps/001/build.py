from sceneact import *
import bpy
import math
import random

random.seed(17)
scene = Scene("Old metalworking workshop")

wood = (.24,.21,.145)
wood_top = (.36,.33,.235)
wood_dark = (.14,.135,.095)
iron = (.135,.145,.14)
rust = (.255,.19,.125)
steel = (.40,.43,.41)
blue = (.19,.29,.32)
plaster = (.60,.63,.57)

def add(name, node):
    scene.include(name, node)
    return node

def B(name, size, center, color):
    return add(name, box(size=size, center=center, color=color))

def R(name, radius, start, end, color):
    return add(name, rod(radius=radius, start=start, end=end, color=color))

def sphere(name, radius, center, color, scale=None):
    obj = ball(radius=radius, center=center, color=color)
    if scale:
        obj.resize(scale)
    return add(name, obj)

def ring(name, center, radius, thickness, color, plane="xz"):
    pts = []
    for i in range(65):
        a = 2*math.pi*i/64
        if plane == "xz":
            p = (center[0]+radius*math.cos(a), center[1], center[2]+radius*math.sin(a))
        elif plane == "xy":
            p = (center[0]+radius*math.cos(a), center[1]+radius*math.sin(a), center[2])
        else:
            p = (center[0], center[1]+radius*math.cos(a), center[2]+radius*math.sin(a))
        pts.append(p)
    return add(name, sweep_tube(points=pts, radius=thickness, color=color))

# Long, worn plank floor.
for j in range(35):
    y = -5.9+j*.225
    for i in range(5):
        x = -7.1+i*2.35+(j%3)*.25
        c = random.uniform(.83,1.12)
        B(f"floor_{j}_{i}", (2.335,.219,.075), (x,y,-.045),
          (.40*c,.345*c,.245*c))
        for end in (-1,1):
            sphere(f"nail_{j}_{i}_{end}", .008,
                   (x+end*1.05,y-.065,-.004), (.13,.125,.10), (1,1,.25))

# The workroom shell and uneven wall surfaces.
B("back_wall", (11,.20,4.8), (-1.7,1.50,2.25), plaster)
B("left_end_wall", (.20,7.3,4.8), (-7.1,-2.0,2.25), (.55,.56,.49))
B("wall_base", (11,.09,.20), (-1.7,1.355,.12), (.28,.29,.24))
for i in range(80):
    x = random.uniform(-6.8,3.4)
    z = random.uniform(.3,3.9)
    if z > 1.88 and -6.5 < x < 3.0:
        continue
    B("plaster_stain_%d"%i, (random.uniform(.08,.35),.009,random.uniform(.06,.32)),
      (x,1.393,z), random.choice([(.52,.55,.49),(.65,.66,.59),(.46,.49,.43)]))

# Tall bright windows, deep ledges, thin dark frames.
for k, x in enumerate([-5.75,-3.65,-1.45,.85,2.65]):
    w = 1.75 if k < 4 else 1.25
    B(f"window_recess_{k}", (w+.16,.12,2.12), (x,1.365,2.94), (.29,.32,.29))
    B(f"window_glass_{k}", (w,.025,1.96), (x,1.285,2.98), (.88,.94,.96))
    B(f"sill_{k}", (w+.30,.43,.105), (x,1.19,1.91), (.40,.41,.35))
    for sx in [-1,1]:
        B(f"window_jamb_{k}_{sx}", (.065,.12,2.05), (x+sx*w/2,1.235,2.96), (.38,.41,.38))
    B(f"window_middle_{k}", (.047,.10,2.00), (x,1.22,2.97), (.36,.39,.37))
    B(f"window_cross_{k}", (w,.10,.045), (x,1.22,2.76), (.45,.47,.43))
    B(f"window_bottom_{k}", (w,.13,.075), (x,1.22,1.99), (.35,.38,.34))

# Wall pipes, brackets, and hanging tools.
R("right_wall_pipe", .034, (3.13,1.19,1.45), (3.13,1.19,4.15), rust)
add("pipe_bend", sweep_tube(points=[(2.6,1.18,1.05),(2.56,1.18,1.12),
    (2.61,1.18,1.26),(2.85,1.18,1.32),(3.13,1.18,1.45)], radius=.03, color=rust))
for x in [-6.2,-4.8,-2.4,-.30,2.65]:
    R(f"hanging_shaft{x}", .017, (x,1.17,2.25), (x+.06,1.17,2.95), iron)
    ring(f"tool_loop{x}", (x+.06,1.17,3.04), .075,.018,rust)
    B(f"shaft_mount{x}", (.13,.08,.07), (x,1.26,2.65), rust)
R("long_diagonal_handle", .032, (3.22,.86,.44), (3.70,1.05,2.64), (.29,.20,.11))

# Bottles, cans, oilers, and clutter along the ledge.
for i in range(36):
    x = random.uniform(-6.5,2.8)
    y = random.uniform(.99,1.20)
    z = 1.98
    h = random.uniform(.08,.25)
    rad = random.uniform(.025,.060)
    c = random.choice([(.30,.31,.27),(.47,.46,.36),(.22,.26,.24),(.52,.40,.27)])
    R(f"sill_container{i}", rad, (x,y,z), (x,y,z+h), c)
    R(f"sill_neck{i}", rad*.42, (x,y,z+h), (x,y,z+h+.055), iron)
    if i%5 == 0:
        R(f"oiler_spout{i}", .009, (x,y,z+h+.025), (x+.12,y,z+h+.12), steel)

# Three separate heavy timber workbenches.
for bi,(x,length) in enumerate([(-5.35,2.65),(-2.35,2.95),(1.10,3.75)]):
    bench = Asset(f"bench_{bi}")
    bench.include("slab", box((length,1.12,.18), center=(x,.40,1.00), color=wood_top))
    bench.include("front_apron", box((length,.13,.25), center=(x,-.115,.815), color=wood))
    bench.include("rear_apron", box((length,.12,.22), center=(x,.88,.80), color=wood_dark))
    for lx in [x-length/2+.19,x+length/2-.19]:
        for y in [-.025,.80]:
            bench.include(f"leg_{lx}_{y}",box((.16,.17,.88),center=(lx,y,.44),color=wood_dark))
        brace = box((.11,.10,.99),center=(lx+.25,.75,.48),color=wood)
        brace.turn('y',33)
        bench.include(f"brace_{lx}",brace)
    bench.include("bottom_stretcher",box((length-.25,.12,.12),center=(x,.60,.23),color=wood))
    scene.include(f"bench_{bi}",bench)
    for q in range(28):
        sx=random.uniform(x-length/2+.05,x+length/2-.05)
        sy=random.uniform(-.12,.93)
        B(f"bench_scar{bi}_{q}",(random.uniform(.035,.25),.012,.003),
          (sx,sy,1.092),random.choice([(.20,.20,.15),(.49,.46,.34),(.30,.29,.21)]))

# Open shallow drawer projecting toward the viewer.
B("drawer_bottom",(1.10,.69,.065),(.72,-.46,.55),(.22,.23,.17))
B("drawer_front",(1.12,.08,.31),(.72,-.81,.67),(.19,.19,.14))
for x in [.15,1.29]:
    B("drawer_side"+str(x),(.065,.70,.29),(x,-.47,.67),(.27,.27,.19))
B("drawer_back",(1.10,.06,.26),(.72,-.12,.67),wood_dark)
ring("drawer_handle",(.72,-.862,.67),.075,.014,(.40,.38,.28))
for i in range(7):
    R(f"drawer_scrap{i}",.012,(.28+i*.12,-.65,.61),(.50+i*.09,-.25,.61),rust)

# Main horizontal lathe and its massive cast iron feet.
for x in [.35,2.30]:
    B("lathe_foot"+str(x),(.41,.54,.07),(x,.42,1.12),iron)
    B("lathe_foot_neck"+str(x),(.20,.28,.33),(x,.42,1.30),iron)
    sphere("lathe_foot_bulge"+str(x),.16,(x,.42,1.38),iron,(1,1,.8))
R("lathe_front_rail",.055,(.15,.20,1.43),(2.64,.20,1.43),steel)
R("lathe_back_rail",.055,(.15,.57,1.43),(2.64,.57,1.43),iron)
B("lathe_bed",(2.46,.32,.11),(1.36,.43,1.36),iron)
B("headstock_lower",(.52,.49,.30),(.48,.43,1.62),iron)
sphere("headstock_round",.22,(.60,.42,1.72),iron,(1.2,1,.85))
R("headstock_spindle",.091,(.52,.42,1.73),(1.04,.42,1.73),steel)
R("chuck",.15,(.91,.42,1.73),(1.07,.42,1.73),(.20,.22,.21))
for a in [0,120,240]:
    t=math.radians(a)
    B("chuck_jaw"+str(a),(.14,.075,.075),(1.055,.42+.10*math.cos(t),1.73+.10*math.sin(t)),steel)
B("tailstock_base",(.46,.46,.10),(2.08,.42,1.49),iron)
sphere("tailstock_body",.175,(2.13,.42,1.66),iron,(1.45,1,.85))
R("tailstock_quill",.065,(1.73,.42,1.73),(2.42,.42,1.73),steel)
R("end_crank_axis",.028,(2.36,.42,1.73),(2.70,.42,1.73),iron)
R("end_crank",.024,(2.67,.42,1.73),(2.67,.42,1.50),iron)
R("end_crank_grip",.042,(2.67,.42,1.50),(2.87,.42,1.50),(.43,.36,.24))
B("tool_rest_post",(.10,.10,.25),(1.37,.13,1.59),iron)
B("tool_rest",(.51,.105,.07),(1.37,.13,1.75),iron)
B("carriage",(.47,.42,.14),(1.43,.40,1.49),(.23,.25,.23))
ring("carriage_handwheel",(1.48,.085,1.40),.10,.019,iron)

# Elevated flywheels with open, curved spokes.
def flywheel(label,x,y,z,r,color):
    ring(label+"_rim",(x,y,z),r,.038,color)
    ring(label+"_rim_edge",(x,y-.035,z),r-.045,.014,(.40,.42,.37))
    R(label+"_hub",.105,(x,y-.11,z),(x,y+.12,z),color)
    for n in range(5):
        a=2*math.pi*n/5
        pts=[]
        for j in range(9):
            t=j/8
            rr=.07+(r-.09)*t
            ang=a+.48*math.sin(t*math.pi)
            pts.append((x+rr*math.cos(ang),y-.008,z+rr*math.sin(ang)))
        add(label+"_spoke"+str(n),sweep_tube(points=pts,radius=.032,color=color))
    R(label+"_axle",.043,(x,y-.24,z),(x,y+.28,z),steel)
    R(label+"_crank",.022,(x,y-.23,z),(x+r*.63,y-.23,z-.13),rust)
    R(label+"_handle",.030,(x+r*.63,y-.23,z-.13),(x+r*.63,y-.43,z-.13),wood_dark)

B("wheel_support_base",(.48,.35,.10),(.46,.78,1.15),iron)
R("wheel_upright",.057,(.48,.78,1.18),(.48,.78,2.23),iron)
R("wheel_second_upright",.035,(.83,.84,1.15),(.48,.84,2.23),rust)
flywheel("large_drive_wheel",.48,.70,2.25,.48,(.20,.23,.23))
# Thin belt descending beside the machine.
add("drive_belt",sweep_tube(points=[(.09,.76,2.48),(.04,.76,2.17),
 (.19,.76,1.28),(.34,.76,1.22),(.82,.76,2.10),(.88,.76,2.43)],
 radius=.014,color=(.17,.13,.09)))

# Central anvil, with broad face, pinched waist and pointed horn.
ax=-1.40
B("anvil_wood_block",(.73,.63,.60),(ax,.17,.73),(.23,.20,.13))
B("anvil_base",(.68,.48,.10),(ax,.17,1.14),(.32,.28,.20))
B("anvil_waist",(.30,.34,.32),(ax,.17,1.34),(.38,.32,.22))
for side in [-1,1]:
    shoulder=box((.18,.36,.30),center=(ax+side*.21,.17,1.41),color=(.40,.34,.24))
    shoulder.turn("y",side*22)
    add("anvil_shoulder"+str(side),shoulder)
B("anvil_face",(.79,.43,.15),(ax,.17,1.58),(.48,.43,.32))
B("anvil_heel",(.24,.42,.14),(ax-.48,.17,1.58),(.43,.38,.28))
for j in range(15):
    t=j/14
    x=ax+.40+t*.57
    rad=.175*(1-t)+.013
    R("anvil_horn"+str(j),rad,(x,.17,1.56),(x+.048,.17,1.56+.035*t),(.46,.39,.27))
B("anvil_face_hole",(.07,.065,.004),(ax-.43,.17,1.654),(.10,.11,.09))

# Second smaller machine and blue flywheel.
B("small_machine_base",(.93,.51,.10),(-3.05,.40,1.14),iron)
for x in [-3.40,-2.70]:
    B("small_machine_pedestal"+str(x),(.17,.28,.27),(x,.40,1.29),(.28,.29,.25))
R("small_lathe_bed",.045,(-3.65,.30,1.40),(-2.40,.30,1.40),steel)
R("small_lathe_spindle",.075,(-3.60,.43,1.49),(-2.45,.43,1.49),iron)
R("blue_wheel_stand",.035,(-2.95,.77,1.10),(-2.95,.77,1.88),iron)
flywheel("blue_flywheel",-2.95,.65,1.89,.325,blue)
B("small_vise_body",(.31,.31,.18),(-3.75,.12,1.24),iron)
B("small_vise_jaws",(.40,.16,.12),(-3.75,.12,1.39),steel)
R("small_vise_screw",.025,(-3.75,-.22,1.27),(-3.75,.19,1.27),steel)

# Several more compact tools fading into the distance.
for i,x in enumerate([-4.25,-5.1,-5.85,-6.40]):
    B(f"rear_machine_base{i}",(.60,.40,.09),(x,.40,1.13),iron)
    B(f"rear_machine_body{i}",(.23,.25,.32),(x,.43,1.31),(.25,.27,.24))
    R(f"rear_machine_spindle{i}",.065,(x-.35,.36,1.48),(x+.30,.36,1.48),steel)
    R(f"rear_machine_vertical{i}",.034,(x,.69,1.1),(x,.69,1.98),iron)
    if i%2==0:
        flywheel(f"distant_wheel{i}",x,.69,1.88,.21,(.27,.31,.29))
    B(f"rear_wooden_box{i}",(.39,.30,.30),(x-.28,.73,1.25),(.35,.28,.18))

# Vise fixed to the front edge near the anvil.
B("front_vise_mount",(.39,.37,.12),(-.55,-.06,1.14),iron)
B("front_vise_body",(.31,.35,.26),(-.55,-.15,1.24),(.23,.25,.23))
B("front_vise_fixed_jaw",(.10,.39,.19),(-.68,-.15,1.36),steel)
B("front_vise_moving_jaw",(.10,.39,.19),(-.43,-.15,1.36),steel)
R("front_vise_screw",.044,(-.55,-.52,1.22),(-.55,-.10,1.22),iron)
R("vise_crossbar",.018,(-.74,-.54,1.22),(-.36,-.54,1.22),steel)
for x in [-.74,-.36]:
    sphere("vise_handle_end"+str(x),.032,(x,-.54,1.22),iron)

# Files, chisels, tongs and loose parts on the bench tops.
for i in range(28):
    x=random.uniform(-6.4,2.58)
    y=random.uniform(-.04,.73)
    if -.0<x<2.5 and y>.20:
        continue
    length=random.uniform(.19,.48)
    ang=random.uniform(-.30,.30)
    p=(x,y,1.115)
    q=(x+length*math.cos(ang),y+length*math.sin(ang),1.12)
    R("loose_tool_steel"+str(i),random.uniform(.008,.018),p,q,steel)
    R("loose_tool_handle"+str(i),.026,(x-.13,y,1.12),(x,y,1.12),
      random.choice([(.40,.27,.14),(.23,.19,.12),(.48,.36,.20)]))
for i in range(8):
    x=.12+i*.115
    R("parallel_chisel"+str(i),.018,(x,-.02,1.12),(x+.30,.32,1.13),steel)
    R("parallel_chisel_grip"+str(i),.028,(x-.07,-.11,1.12),(x,-.02,1.12),(.34,.25,.15))
B("sheet_of_metal",(.49,.38,.014),(1.07,-.025,1.112),(.57,.58,.53))
for i in range(5):
    sphere("metal_sheet_hole"+str(i),.018,(.90+i*.075,-.07,1.122),iron,(1,1,.15))
B("folded_paper",(.31,.29,.009),(1.57,.01,1.115),(.70,.69,.59))
for i in range(5):
    R("loose_long_rod"+str(i),.014,(-2.35+i*.08,.00,1.13),(-1.90+i*.08,.12,1.13),steel)

# Long tools hanging below the tabletop.
for i in range(8):
    x=-1.00+i*.075
    R("hanging_tong"+str(i),.013,(x,-.18,1.04),(x-.06,-.22,.24+random.uniform(0,.12)),rust)
    sphere("tong_handle"+str(i),.035,(x,-.18,1.05),iron,(1,1,1.6))
for i in range(4):
    x=-4.85+i*.42
    B("underbench_drawer"+str(i),(.35,.40,.28),(x,.28,.58),(.22,.24,.19))
    R("drawer_pull"+str(i),.018,(x-.06,.045,.60),(x+.06,.045,.60),iron)

# Cans and barrels below the bench, including the large pale foreground bin.
def can(name,x,y,z,r,h,c):
    R(name+"_body",r,(x,y,z),(x,y,z+h),c)
    ring(name+"_rim",(x,y,z+h),r,.014,(.29,.29,.23),"xy")
    R(name+"_dark_opening",r*.88,(x,y,z+h+.002),(x,y,z+h+.006),(.135,.145,.115))
    ring(name+"_lower_rim",(x,y,z+.04),r,.012,iron,"xy")

can("pale_large_bin",1.22,-.14,.02,.32,.63,(.56,.55,.43))
can("green_foreground_can",2.64,.09,.02,.37,.75,(.22,.28,.19))
can("rear_bucket",-3.98,.22,.02,.24,.48,(.33,.35,.27))
can("rusty_pail",-5.00,.10,.02,.21,.45,(.34,.25,.17))
R("bin_wood_scrap",.08,(1.10,-.14,.54),(1.23,-.08,.75),(.37,.29,.17))
B("bin_flat_scrap",(.32,.21,.04),(1.23,-.13,.65),(.32,.30,.22))
for x in [1.09,1.22,1.35]:
    B("bin_mark"+str(x),(.025,.006,.17),(x,-.456,.33),(.20,.21,.17))

# A small floor direction marker visible in the aisle.
R("floor_marker",.30,(-2.22,-1.78,.004),(-2.22,-1.78,.009),(.31,.39,.40))
B("arrow_shaft",(.12,.25,.005),(-2.22,-1.80,.014),(.76,.79,.75))
for s in [-1,1]:
    ar=box((.095,.22,.005),center=(-2.22+s*.060,-1.69,.015),color=(.76,.79,.75))
    ar.turn('z',s*45)
    add("arrow_tip"+str(s),ar)

realize(scene)

# Procedural surface variation keeps the materials aged and tactile.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    base=tuple(bs.inputs["Base Color"].default_value[:3])
    bs.inputs["Roughness"].default_value=.78
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    if min(base)>.82:
        bs.inputs["Base Color"].default_value=(.77,.86,.90,1)
        bs.inputs["Emission Color"].default_value=(.77,.87,.94,1)
        bs.inputs["Emission Strength"].default_value=.8
        bs.inputs["Roughness"].default_value=.28
        continue
    noise=nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value=37
    noise.inputs["Detail"].default_value=3
    noise.inputs["Roughness"].default_value=.72
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=tuple(v*.72 for v in base)+(1,)
    ramp.color_ramp.elements[1].position=.84
    ramp.color_ramp.elements[1].color=tuple(min(v*1.20,1) for v in base)+(1,)
    links.new(noise.outputs["Fac"],ramp.inputs[0])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.22
    bump.inputs["Distance"].default_value=.018
    links.new(noise.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if max(base)-min(base)<.09 and max(base)<.60:
        bs.inputs["Metallic"].default_value=.48
        bs.inputs["Roughness"].default_value=.56

set_view((4.45,-6.45,3.95),(-1.40,.36,1.20),lens=39,sensor=36)
area_emitter((-1.0,.70,4.55),power=1150,size=5.0,target=(-1.0,-.6,.6),color=(.83,.91,1.0))
area_emitter((1.9,-3.7,4.4),power=430,size=4.0,target=(-1.0,.3,1),color=(1.0,.91,.77))
area_emitter((-5.1,.8,3.6),power=450,size=2.5,target=(-3.6,-.4,1.0),color=(.84,.91,1.0))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.42,.47,.50,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.38
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=384
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=.15
sc.render.image_settings.file_format='PNG'
