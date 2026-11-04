from sceneact import *
import bpy
import math
import random

random.seed(21)

CAMERA_POSITION = (5.0, -7.1, 4.25)
CAMERA_TARGET = (-0.85, 0.0, 1.48)
CAMERA_LENS = 39
BENCH_LENGTH = 8.0
BENCH_DEPTH = 1.15
BENCH_HEIGHT = 1.22
LARGE_WHEEL_RADIUS = 0.49
SMALL_WHEEL_RADIUS = 0.29

scene = Scene("Historic metalworking workshop")

wood = (0.29, 0.23, 0.145)
edgewood = (0.21, 0.175, 0.12)
floorwood = (0.44, 0.365, 0.25)
iron = (0.105, 0.12, 0.115)
steel = (0.31, 0.33, 0.31)
rust = (0.24, 0.16, 0.095)
wall = (0.53, 0.54, 0.46)
pale = (0.73, 0.73, 0.64)

def B(a, name, size, center, color):
    a.include(name, box(size=size, center=center, color=color))

def R(a, name, radius, start, end, color):
    a.include(name, rod(radius=radius, start=start, end=end, color=color))

def wheel(a, name, center, radius, color, spokes=6):
    w = Asset(name)
    x, y, z = center
    n = 28
    for i in range(n):
        t = 2 * math.pi * i / n
        u = 2 * math.pi * (i + 1) / n
        R(w, "rim_%d" % i, 0.029,
          (x + radius * math.cos(t), y, z + radius * math.sin(t)),
          (x + radius * math.cos(u), y, z + radius * math.sin(u)), color)
    R(w, "hub", 0.085, (x,y-.095,z), (x,y+.095,z), color)
    for i in range(spokes):
        t = 2 * math.pi * i / spokes
        # Slightly swept spokes retain the cast-wheel silhouette.
        pts = [
            (x+.065*math.cos(t), y, z+.065*math.sin(t)),
            (x+radius*.52*math.cos(t+.24), y,
             z+radius*.52*math.sin(t+.24)),
            (x+radius*.96*math.cos(t+.05), y,
             z+radius*.96*math.sin(t+.05))
        ]
        w.include("spoke_%d" % i,
                  sweep_tube(points=pts, radius=.025, color=color))
    a.include(name, w)
    return w

# Visible timber flooring, with narrow dark joints.
floor = Asset("Worn plank floor")
for i in range(42):
    x = -6.0 + i*.265
    shift = .65 if i % 2 else 0
    for j in range(4):
        y = -7.2 + j*2.3 + shift
        c = tuple(v * random.uniform(.91,1.07) for v in floorwood)
        B(floor, "board_%d_%d" % (i,j), (.257,2.285,.075),
          (x,y,-.045), c)
scene.include("floor", floor)

# Window wall: opaque lower masonry and broad bright glazed openings.
architecture = Asset("Plaster wall and windows")
B(architecture, "lower_wall", (11,.22,1.92), (-1,.91,.93), wall)
B(architecture, "upper_wall", (11,.22,.35), (-1,.91,4.73), wall)
for i, x in enumerate([-6.35,-4.0,-1.65,.70,3.05,4.35]):
    B(architecture, "pier_%d" % i, (.19,.27,3.0), (x,.87,3.16),
      (.47,.49,.43))
for i in range(4):
    x = -5.18 + i*2.35
    B(architecture, "daylight_%d" % i, (2.15,.035,2.55),
      (x,1.015,3.24), (.83,.9,.94))
    for k, xx in enumerate([x-1.08,x,x+1.08]):
        B(architecture, "vertical_frame_%d_%d" % (i,k),
          (.058,.13,2.65), (xx,.81,3.24), (.24,.28,.26))
    for k, z in enumerate([1.94,3.30,4.55]):
        B(architecture, "horizontal_frame_%d_%d" % (i,k),
          (2.22,.14,.055), (x,.81,z), (.29,.31,.27))
    B(architecture, "sill_%d" % i, (2.38,.43,.10),
      (x,.70,1.92), (.29,.29,.24))
scene.include("architecture", architecture)

# Heavy continuous bench with gaps beneath it.
bench = Asset("Continuous scarred wooden workbench")
B(bench, "top", (BENCH_LENGTH,BENCH_DEPTH,.16),
  (-1,0,BENCH_HEIGHT), wood)
B(bench, "front_apron", (BENCH_LENGTH,.13,.23),
  (-1,-.53,1.045), edgewood)
B(bench, "back_apron", (BENCH_LENGTH,.12,.20),
  (-1,.48,1.05), edgewood)
for i,x in enumerate([-4.75,-3.2,-1.65,-.05,1.55,2.7]):
    for j,y in enumerate([-.43,.40]):
        B(bench,"leg_%d_%d"%(i,j),(.16,.17,1.09),(x,y,.55),edgewood)
    B(bench,"foot_cross_%d"%i,(.20,1.08,.13),(x,-.04,.20),wood)
    B(bench,"end_stretcher_%d"%i,(.13,.92,.13),(x,0,.46),edgewood)
B(bench,"low_rail",(7.5,.12,.13),(-1,-.33,.32),edgewood)
for i in range(22):
    x = random.uniform(-4.8,2.8)
    y = random.uniform(-.49,.46)
    B(bench,"top_scar_%d"%i,
      (random.uniform(.08,.36),.012,.003),(x,y,1.302),
      (.17,.15,.105))
scene.include("bench",bench)

# Dominant foreground lathe and its handwheel.
lathe = Asset("Foreground iron lathe")
for i,x in enumerate([.88,2.16]):
    B(lathe,"foot_%d"%i,(.31,.43,.075),(x,-.03,1.34),iron)
    B(lathe,"pedestal_%d"%i,(.16,.25,.29),(x,-.03,1.50),iron)
    B(lathe,"bearing_%d"%i,(.27,.30,.29),(x,-.03,1.70),iron)
    R(lathe,"bearing_cap_%d"%i,.15,
      (x-.11,-.03,1.77),(x+.11,-.03,1.77),iron)
B(lathe,"long_bed",(1.65,.26,.12),(1.55,-.02,1.54),iron)
R(lathe,"main_spindle",.077,(.64,-.03,1.76),(2.65,-.03,1.76),steel)
R(lathe,"chuck",.17,(.70,-.03,1.76),(.97,-.03,1.76),iron)
R(lathe,"chuck_ring",.175,(.71,-.03,1.76),(.76,-.03,1.76),steel)
B(lathe,"tool_slide",(.37,.40,.10),(1.44,-.18,1.64),steel)
R(lathe,"tool_post",.041,(1.43,-.18,1.67),(1.43,-.18,1.96),iron)
B(lathe,"tool_post_head",(.27,.11,.055),(1.43,-.18,1.95),iron)
R(lathe,"tail_crank",.025,(2.62,-.03,1.76),(2.62,-.03,1.49),iron)
R(lathe,"wood_crank_handle",.065,(2.59,-.03,1.49),(2.91,-.03,1.49),
  (.43,.36,.24))
R(lathe,"rear_upright",.055,(.88,.32,1.30),(.88,.32,2.38),iron)
wheel(lathe,"large_flywheel",(.88,.26,2.31),
      LARGE_WHEEL_RADIUS,(.13,.145,.14),5)
R(lathe,"flywheel_axle",.06,(.88,.04,2.31),(.88,.51,2.31),steel)
R(lathe,"wheel_crank",.025,(1.16,.19,2.02),(1.16,-.02,2.02),steel)
R(lathe,"wheel_grip",.042,(1.16,-.03,2.02),(1.34,-.03,2.02),wood)
scene.include("lathe",lathe)

# The anvil has a broad flat face, narrow waist and projecting tapered horn.
anvil = Asset("Central anvil")
B(anvil,"stump",(.53,.56,.66),(-.92,-.09,.88),(.23,.18,.12))
B(anvil,"base",(.62,.47,.10),(-.92,-.09,1.36),rust)
B(anvil,"waist",(.28,.29,.28),(-.92,-.09,1.53),rust)
B(anvil,"shoulders",(.52,.38,.13),(-.92,-.09,1.69),rust)
B(anvil,"flat_face",(.68,.39,.075),(-.94,-.09,1.79),(.32,.28,.20))
for i in range(5):
    r=.17*(1-i/5.6)
    R(anvil,"horn_%d"%i,r,
      (-.61+i*.115,-.09,1.72),
      (-.61+(i+1)*.115,-.09,1.72),rust)
B(anvil,"heel",(.22,.34,.16),(-1.37,-.09,1.73),rust)
scene.include("anvil",anvil)

# A second smaller belt-driven machine farther along the bench.
machine = Asset("Small wheel machine")
B(machine,"base",(.68,.49,.09),(-2.05,.04,1.35),iron)
for i,x in enumerate([-2.25,-1.88]):
    B(machine,"support_%d"%i,(.09,.19,.34),(x,.10,1.54),steel)
R(machine,"axle",.055,(-2.08,-.17,1.88),(-2.08,.36,1.88),steel)
wheel(machine,"small_flywheel",(-2.08,-.02,1.88),
      SMALL_WHEEL_RADIUS,(.23,.31,.32),6)
B(machine,"bed",(.69,.18,.10),(-2.07,-.13,1.52),steel)
R(machine,"working_shaft",.052,(-2.50,-.19,1.60),(-1.63,-.19,1.60),steel)
scene.include("small_machine",machine)

def vise(name,x,y,z,scale=1):
    a=Asset(name)
    B(a,"mount",(.28*scale,.28*scale,.10*scale),(x,y,z),iron)
    B(a,"body",(.29*scale,.32*scale,.22*scale),
      (x,y-.10*scale,z+.12*scale),iron)
    for i,yy in enumerate([y-.06*scale,y-.32*scale]):
        B(a,"jaw_%d"%i,(.35*scale,.075*scale,.19*scale),
          (x,yy,z+.27*scale),steel)
    R(a,"screw",.038*scale,(x,y-.51*scale,z+.12*scale),
      (x,y+.05*scale,z+.12*scale),steel)
    R(a,"handle",.018*scale,(x,y-.51*scale,z-.10*scale),
      (x,y-.51*scale,z+.37*scale),steel)
    scene.include(name,a)

vise("Large front mounted vise",-.08,-.60,1.15,1.10)
vise("Distant bench vise",-3.54,-.44,1.31,.70)
vise("Far end vise",-4.65,-.30,1.30,.55)

# Projecting open drawer: dark interior and separate thick sides.
drawer=Asset("Open foreground drawer")
B(drawer,"bottom",(.97,.70,.055),(1.05,-.94,.86),(.12,.125,.105))
B(drawer,"front",(.99,.09,.28),(1.05,-1.27,.99),edgewood)
for i,x in enumerate([.59,1.51]):
    B(drawer,"side_%d"%i,(.065,.69,.28),(x,-.94,.99),wood)
B(drawer,"back",(.92,.07,.20),(1.05,-.62,.96),wood)
R(drawer,"pull_mount",.048,(1.05,-1.325,.98),(1.05,-1.37,.98),rust)
R(drawer,"pull",.075,(1.05,-1.375,.98),(1.05,-1.39,.98),rust)
B(drawer,"offcut",(.40,.13,.045),(.97,-.91,.91),(.47,.43,.30))
scene.include("drawer",drawer)

# Loose tools, metal stock and pale paper on the crowded surface.
tools=Asset("Bench tools and stock")
for i in range(10):
    x=-3.7+i*.55
    y=random.uniform(-.40,.10)
    length=random.uniform(.23,.43)
    R(tools,"steel_tool_%d"%i,.018,(x,y,1.335),
      (x+length,y+.12,1.335),steel)
    R(tools,"handle_%d"%i,.033,(x-.13,y-.035,1.335),
      (x,y,1.335),(.34,.23,.14))
for i in range(5):
    x=.30+i*.15
    R(tools,"foreground_chisel_%d"%i,.021,(x,-.48,1.34),
      (x+.20,-.14,1.34),(.48,.49,.45))
    R(tools,"chisel_handle_%d"%i,.035,(x-.07,-.59,1.34),
      (x,-.48,1.34),wood)
for i,(x,y) in enumerate([(1.05,-.31),(1.60,-.37),(2.42,.18)]):
    p=box(size=(.40,.28,.007),center=(x,y,1.325),
          color=(.72,.70,.61))
    p.turn(axis="+z",degrees=-12+i*18)
    tools.include("paper_%d"%i,p)
for i in range(4):
    B(tools,"stacked_stock_%d"%i,(.53,.22,.035),
      (-2.74,-.26,1.34+i*.037),(.46,.39,.26))
B(tools,"small_wood_box",(.42,.31,.24),(-3.08,.28,1.45),wood)
scene.include("tools",tools)

# Sill clutter: cans, bottles and compact metal tools.
sill=Asset("Window sill objects")
for i in range(18):
    x=-5.4+i*.47
    rad=random.uniform(.035,.065)
    h=random.uniform(.12,.28)
    c=random.choice([steel,iron,rust,(.53,.53,.46)])
    R(sill,"can_%d"%i,rad,(x,.57,1.98),(x,.57,1.98+h),c)
    if i%3==0:
        R(sill,"bottle_neck_%d"%i,rad*.37,
          (x,.57,1.98+h),(x,.57,2.06+h),c)
for i,x in enumerate([-3.8,-1.25,1.45]):
    R(sill,"upright_tool_%d"%i,.018,(x,.64,2.0),(x,.64,2.54),iron)
    R(sill,"crossbar_%d"%i,.015,(x-.13,.64,2.44),(x+.13,.64,2.44),iron)
scene.include("sill_objects",sill)

# Wall-hung handles, hooks and the large diagonal wooden implement.
hanging=Asset("Wall hung tools")
for i,x in enumerate([-4.5,-3.75,-2.9,-1.1,2.8]):
    R(hanging,"shaft_%d"%i,.022,(x,.68,1.47),(x+.05,.68,2.04),rust)
    B(hanging,"head_%d"%i,(.15,.055,.10),(x+.05,.68,2.05),iron)
R(hanging,"long_handle",.035,(2.75,.58,1.36),(3.35,.58,3.55),wood)
hanging.include("curved_pipe",sweep_tube(
    points=[(2.35,.63,2.75),(2.35,.63,1.98),
            (2.43,.63,1.65),(2.67,.63,1.52)],
    radius=.025,color=(.28,.29,.25)))
scene.include("hanging_tools",hanging)

# Containers beneath the bench; cylinders remain open at their visible tops.
def open_container(name,x,y,r,h,color):
    a=Asset(name)
    R(a,"bottom",r,(x,y,.04),(x,y,.08),color)
    n=20
    for i in range(n):
        t=2*math.pi*i/n
        u=2*math.pi*(i+1)/n
        # Flat upright staves form a visibly hollow container.
        mid=(t+u)/2
        side=box(size=(2*r*math.sin(math.pi/n)+.006,.035,h),
                 center=(x+r*math.cos(mid),y+r*math.sin(mid),h/2+.06),
                 color=color)
        side.turn(axis="+z",degrees=math.degrees(mid)+90)
        a.include("side_%d"%i,side)
        R(a,"rim_%d"%i,.018,
          (x+r*math.cos(t),y+r*math.sin(t),h+.06),
          (x+r*math.cos(u),y+r*math.sin(u),h+.06),iron)
    scene.include(name,a)

open_container("Pale bucket",1.53,-.55,.31,.52,(.47,.47,.36))
open_container("Cropped right barrel",2.87,-.35,.40,.70,(.24,.27,.18))
open_container("Distant bin",-3.25,-.13,.23,.43,(.27,.30,.25))
scrap=Asset("Stored scraps")
for i in range(5):
    R(scrap,"long_bar_%d"%i,.018,
      (-.28+i*.055,-.70,.11),(-.19+i*.06,-.60,1.05),rust)
for i in range(4):
    B(scrap,"underbench_box_%d"%i,(.48,.40,.30),
      (-3.6+i*.66,.06,.20),(.23,.22,.16))
scene.include("stored_scraps",scrap)

# A restrained floor marker visible on the left.
marker=Asset("Floor direction marker")
R(marker,"disc",.25,(-1.45,-2.7,.001),(-1.45,-2.7,.006),
  (.34,.41,.40))
B(marker,"arrow_stem",(.09,.23,.008),(-1.45,-2.70,.014),
  (.75,.76,.70))
for i,angle in enumerate([-42,42]):
    p=box(size=(.085,.20,.008),center=(-1.45+(-.055 if i==0 else .055),
                                      -2.79,.015),
          color=(.75,.76,.70))
    p.turn(axis="+z",degrees=angle)
    marker.include("arrow_head_%d"%i,p)
scene.include("floor_marker",marker)

realize(scene)

# Fine wear comes from procedural shading, not additional geometry.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if not bs:
        continue
    rgba=bs.inputs["Base Color"].default_value
    c=tuple(rgba[:3])
    bs.inputs["Roughness"].default_value=.83
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=26
    tex.inputs["Detail"].default_value=3
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=tuple(v*.66 for v in c)+(1,)
    ramp.color_ramp.elements[1].position=.83
    ramp.color_ramp.elements[1].color=tuple(min(v*1.15,1) for v in c)+(1,)
    links.new(tex.outputs["Fac"],ramp.inputs[0])
    links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.19
    bump.inputs["Distance"].default_value=.022
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    if max(c)-min(c)<.055 and max(c)<.52:
        bs.inputs["Metallic"].default_value=.52
        bs.inputs["Roughness"].default_value=.65
    if c[2]>.85 and c[0]>.75:
        bs.inputs["Emission Color"].default_value=(*c,1)
        bs.inputs["Emission Strength"].default_value=.65

set_view(CAMERA_POSITION,CAMERA_TARGET,lens=CAMERA_LENS,sensor=36)
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new("Workshop ambient")
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.66,.72,.76,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.36

area_emitter((-1.0,.25,4.6),power=1450,size=6,
             target=(-1,-1,0),color=(.88,.94,1.0))
area_emitter((1.5,-4,4.5),power=420,size=5,
             target=(-.5,0,1),color=(1.0,.91,.77))
area_emitter((-4,.1,3.6),power=600,size=3,
             target=(-3,-1,.8),color=(.88,.95,1))
