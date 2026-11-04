from sceneact import *
import bpy
import math
import random

# Evidence ledger: pixel locations are visual estimates, not calibration.
# Reference: back shelf edges near y128/174/216/260; render 2 near
# y149/185/220/254. Reference kettle near (192,297), render near (177,293).
# Reference upper tools crop at y0; render has an unwanted empty band y0:49.
# Reference left window x0:90; render window approximately x0:90.
# Back shelves remain nearly horizontal; right returns rise toward the right.
# Reference bench crops the bottom and sides, occluding lower room inventory.
# Render retains these crops but shows a larger empty strip behind the bench.
# Measured facts: steps 1 and 2 returned valid images; observed execution times
# were 32.652 and 34.119 seconds. No geometric calibration was measured.
#
# CHOSEN FAMILY: camera only. Modestly increase focal length, lower the camera
# and lower its target. Prediction: crop the empty upper band, spread the far
# shelf levels vertically, and retain approximately the kettle's vertical position.
# Three independent anchors motivating this change: upper wall crop, far shelf
# spacing, and near kettle/bench contact. Horizontal framing remains uncertain.
# Geometry, lighting, finishes, semantic owners and support planes stay fixed.
# Render 2 has improved dark/light ordering, though inventory remains visually
# simplified and the foreground less crowded than the photograph.
#
# Ownership/support ledger:
# architecture -> room(): plaster, floor, window panes and attached frame.
# shelves -> boards/brackets; explicit levels[] are actual back/right board tops.
# plane slots -> plane(): stock, iron, knob and tote share one editable Asset.
# top_moulding slots -> upright wood stock and attached cutter on upper shelf.
# left_rack slots -> rack rail and its attached handles/blades.
# hanging slots -> individual wall tools on the corresponding plaster face.
# workbench -> top, apron, legs and vise; actual support surface BENCH_Z.
# foreground chisel/saw/kettle/bottle/tray/mallet/offcut slots -> loose Assets.
# Tray nails belong to their tray; kettle bail/lid/spout belong to kettle.
# labels -> shelf-front decoration. Historic tool identities remain uncertain.
# Relative scale only. Foreground tools occlude the bench; bench occludes floor.

rng = random.Random(18)
S = Scene("Historic woodworking tool shop")
C = {
    "wall": (.71,.73,.68), "wood": (.39,.20,.075),
    "honey": (.59,.33,.12), "edge": (.67,.42,.19),
    "darkwood": (.22,.115,.055), "iron": (.105,.115,.108),
    "steel": (.37,.39,.36), "black": (.045,.053,.049),
    "bench": (.36,.29,.19), "glass": (.47,.59,.57)
}
CAMERA = dict(position=(.05,-4.65,2.63),
              target=(.08,1.40,1.84), lens=34)
BACK_Y = 2.05
BENCH_Z = .91
LIGHTING = dict(world_strength=.14, window_power=230, fill_power=150)

def add(name, node):
    return S.include(name, node)

def cube(owner, name, size, center, color):
    return owner.include(name, box(size, center=center, color=color))

def beam(owner, name, a, b, width, depth, color):
    dx, dz = b[0]-a[0], b[2]-a[2]
    length = math.sqrt(dx*dx + dz*dz)
    n = box((width,depth,length),
            center=((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2),
            color=color)
    n.turn('y', math.degrees(math.atan2(dx,dz)))
    return owner.include(name,n)

def room():
    a = Asset("room architecture")
    cube(a,"back_plaster",(5.65,.12,4.3),(0,2.19,2.05),C["wall"])
    cube(a,"right_plaster",(.12,4.9,4.3),(2.83,-.20,2.05),C["wall"])
    cube(a,"left_plaster",(.12,4.9,4.3),(-2.83,-.20,2.05),C["wall"])
    cube(a,"floor",(5.65,5.0,.10),(0,-.25,-.06),(.28,.26,.21))
    cube(a,"window_dark_recess",(.025,2.25,2.8),
         (-2.756,.75,2.32),(.15,.19,.18))
    for j in range(3):
        cube(a,f"glass_{j}",(.032,.68,2.58),
             (-2.73,-.02+j*.73,2.34),(.38,.63,.73))
    for j in range(4):
        cube(a,f"window_mullion_{j}",(.065,.035,2.8),
             (-2.69,-.38+j*.74,2.33),(.67,.67,.56))
    for z in (.95,2.25,3.72):
        cube(a,f"window_cross_{z}",(.07,2.26,.045),
             (-2.69,.73,z),(.69,.69,.59))
    add("architecture",a)

room()
shelves = Asset("wall shelving")
levels = [1.02,1.53,2.08,2.64]
for i,z in enumerate(levels):
    cube(shelves,f"back_board_{i}",(4.82,.43,.065),
         (-.12,1.83,z-.0325),C["edge"])
    cube(shelves,f"right_board_{i}",(.47,3.70,.065),
         (2.56,.17,z-.0325),C["edge"])
    for j,x in enumerate((-2.20,0,2.05)):
        cube(shelves,f"back_bracket_{i}_{j}",(.045,.27,.15),
             (x,1.94,z-.12),(.35,.33,.25))
for z in (1.65,2.49,3.22):
    cube(shelves,f"left_short_shelf_{z}",(.43,2.0,.055),
         (-2.56,.90,z),C["edge"])
add("shelves",shelves)

def plane(name, position, length=.38, width=.13, height=.12,
          angle=0, wood=True, detail=True):
    a = Asset(name)
    col = rng.choice([C["wood"],C["honey"],C["darkwood"]])
    cube(a,"stock",(length,width,height),(0,0,height/2),
         col if wood else C["iron"])
    if not wood:
        cube(a,"bright_sole",(length+.015,width+.015,.018),
             (0,0,.014),C["steel"])
    blade = box((.045,width*.82,height*.95),
                center=(.01,0,height*.95),color=C["iron"])
    blade.turn('y',-28)
    a.include("slanted_cutter",blade)
    if detail:
        a.include("front_knob",ball(width*.23,
                  center=(-length*.30,0,height+.035),color=col))
        a.include("tote_back",rod(.018,
                  start=(length*.28,0,height),
                  end=(length*.34,0,height+.12),color=col))
        a.include("tote_top",rod(.018,
                  start=(length*.34,0,height+.12),
                  end=(length*.13,0,height+.13),color=col))
    a.turn('z',angle,pivot=(0,0,0))
    a.move(position)
    add(name,a)

for level,z in enumerate(levels[:3]):
    count = [12,13,14][level]
    for i in range(count):
        x = -2.28+i*(4.40/(count-1))
        plane(f"back_plane_{level}_{i}",
              (x,1.78+rng.uniform(-.05,.035),z),
              length=rng.uniform(.25,.40),width=.13,
              height=rng.uniform(.085,.15),
              angle=rng.uniform(-9,9),
              wood=(i%5 != 1),detail=(i%3==0))

for i in range(36):
    a = Asset(f"upright moulding plane {i}")
    h = rng.uniform(.15,.32)
    w = rng.uniform(.055,.105)
    cube(a,"wood_stock",(w,.24,h),(0,0,h/2),
         rng.choice([C["wood"],C["honey"],C["darkwood"]]))
    if i%3 == 0:
        cube(a,"projecting_iron",(.018,.12,h*.65),
             (w*.19,0,h*.91),C["steel"])
    a.turn('y',rng.uniform(-13,13),pivot=(0,0,0))
    a.move((-2.35+i*.129,1.83,levels[3]))
    add(f"top_moulding_{i}",a)

for level,z in enumerate(levels):
    for i in range(9):
        y = -1.30+i*.39
        plane(f"right_plane_{level}_{i}",(2.54,y,z),
              length=rng.uniform(.26,.40),width=.16,
              height=rng.uniform(.12,.22),
              angle=90+rng.uniform(-7,7),
              wood=(i%4!=0),detail=(i%2==0))

for row,z in enumerate((1.69,2.52,3.24)):
    rack = Asset(f"left handle rack {row}")
    cube(rack,"rail",(.11,2.12,.055),(-2.48,.78,z),C["edge"])
    for i in range(9):
        y=-.15+i*.235
        h=rng.uniform(.22,.43)
        cube(rack,f"handle_{i}",(.09,.075,h),
             (-2.48,y,z+h/2),
             rng.choice([C["wood"],C["darkwood"]]))
        cube(rack,f"blade_{i}",(.028,.034,.16),
             (-2.48,y,z-.08),C["steel"])
    add(f"left_rack_{row}",rack)

def square(name, origin, size, angle, color):
    a=Asset(name)
    x,y,z=origin
    cube(a,"long_arm",(.065,.035,size),(0,0,size/2),color)
    cube(a,"short_arm",(size*.70,.035,.065),
         (size*.35,0,size-.032),color)
    cube(a,"edge_line",(.008,.039,size*.84),
         (.021,-.005,size*.48),(.36,.37,.32))
    a.turn('y',angle,pivot=(0,0,0))
    a.move((x,y,z))
    add(name,a)

for i in range(4):
    square(f"hanging_large_square_{i}",
           (-1.83+i*.26,2.095,3.01+i*.16),
           .91-i*.055,43,C["iron"])
square("upright_square",(.13,2.08,3.10),.94,0,C["black"])

for i,(x,z,h) in enumerate(
        ((.70,3.12,.74),(.94,3.47,.78),(.67,3.70,.63))):
    a=Asset(f"wall divider {i}")
    beam(a,"left_leg",(x-.15,2.08,z),(x,2.08,z+h),
         .025,.028,C["darkwood"])
    beam(a,"right_leg",(x+.16,2.08,z),(x,2.08,z+h),
         .025,.028,C["darkwood"])
    a.include("hinge",ball(.035,center=(x,2.06,z+h),
                          color=C["steel"]))
    add(f"hanging_divider_{i}",a)

for i,(x,z) in enumerate(((1.45,3.47),(1.85,3.15))):
    a=Asset(f"wall mallet {i}")
    cube(a,"handle",(.06,.065,.67),(x,2.07,z),C["wood"])
    cube(a,"head",(.37,.10,.105),(x,2.05,z+.22),
         C["darkwood"] if i==0 else C["iron"])
    add(f"hanging_mallet_{i}",a)

for i in range(3):
    a=Asset(f"right wall handsaw {i}")
    cube(a,"blade",(.05,.65,.14),
         (2.74,.62+i*.42,3.24+i*.25),C["steel"])
    cube(a,"wood_handle",(.10,.19,.21),
         (2.69,.26+i*.42,3.25+i*.25),C["darkwood"])
    add(f"high_saw_{i}",a)

bench=Asset("foreground workbench")
cube(bench,"heavy_top",(4.75,1.80,.15),
     (-.02,-1.08,BENCH_Z-.075),C["bench"])
cube(bench,"front_apron",(4.65,.10,.25),
     (-.02,-1.91,.66),C["darkwood"])
for i,x in enumerate((-2.04,1.94)):
    cube(bench,f"leg_{i}",(.16,.16,.76),(x,-1.35,.38),C["wood"])
cube(bench,"right_vise",(.34,.39,.28),(1.47,-.59,1.02),C["wood"])
cube(bench,"vise_jaw",(.13,.43,.31),(1.70,-.59,1.03),C["honey"])
add("workbench",bench)

for i in range(6):
    plane(f"bench_wood_plane_{i}",
          (-.85+i*.42,-.56+rng.uniform(-.08,.09),BENCH_Z),
          length=.54,width=.18,height=.12,
          angle=rng.uniform(-12,12),wood=True,detail=(i%2==0))

for i in range(8):
    a=Asset(f"loose chisel {i}")
    x=-2.03+i*.16
    y=-1.44+rng.uniform(-.14,.14)
    cube(a,"steel_blade",(.075,.64,.028),
         (x,y,BENCH_Z+.025),C["steel"])
    a.include("wood_handle",rod(.045,
              start=(x,y+.31,BENCH_Z+.05),
              end=(x,y+.57,BENCH_Z+.08),color=C["darkwood"]))
    a.turn('z',-13+i*2,pivot=(x,y,BENCH_Z))
    add(f"foreground_chisel_{i}",a)

for i in range(2):
    a=Asset(f"bench saw {i}")
    cube(a,"wide_blade",(.19,.85,.018),(0,0,0),(.34,.35,.32))
    cube(a,"handle",(.17,.22,.075),(0,.50,.045),C["darkwood"])
    a.turn('z',-24+i*18,pivot=(0,0,0))
    a.move((-1.55+i*.39,-1.23,BENCH_Z+.055+i*.035))
    add(f"bench_saw_{i}",a)

k=Asset("black metal kettle")
k.include("body",ball(.19,center=(-.76,-.64,1.13),
                     color=C["iron"]).resize((1,1,.92)))
k.include("lid",rod(.145,length=.025,
                   center=(-.76,-.64,1.30),color=C["steel"]))
k.include("lid_knob",ball(.032,
                        center=(-.76,-.64,1.34),color=C["black"]))
k.include("spout",rod(.043,start=(-.61,-.64,1.14),
                     end=(-.45,-.64,1.27),color=C["iron"]))
k.include("bail",sweep_tube(
    points=[(-.93,-.64,1.20),(-.95,-.64,1.47),
            (-.77,-.64,1.58),(-.59,-.64,1.46),(-.59,-.64,1.22)],
    radius=.012,color=C["steel"]))
add("kettle",k)

b=Asset("cloudy glass bottle")
b.include("body",rod(.075,length=.31,
                    center=(-.15,-.81,1.075),color=(.53,.57,.48)))
b.include("shoulder",ball(.075,
                         center=(-.15,-.81,1.23),color=(.56,.60,.51)))
b.include("neck",rod(.032,length=.13,
                    center=(-.15,-.81,1.31),color=(.60,.64,.55)))
cube(b,"paper_label",(.12,.012,.14),
     (-.15,-.886,1.10),(.64,.61,.47))
b.include("stopper",rod(.035,length=.035,
                       center=(-.15,-.81,1.39),color=(.63,.61,.48)))
add("bottle",b)

for j,(x,y) in enumerate(((.73,-1.51),(1.03,-1.12))):
    a=Asset(f"hardware tray {j}")
    cube(a,"bottom",(.54,.41,.035),(x,y,BENCH_Z+.025),C["iron"])
    for i,xx in enumerate((x-.27,x+.27)):
        cube(a,f"side_{i}",(.025,.43,.13),
             (xx,y,BENCH_Z+.085),C["steel"])
    for i,yy in enumerate((y-.205,y+.205)):
        cube(a,f"end_{i}",(.54,.025,.13),
             (x,yy,BENCH_Z+.085),C["steel"])
    for i in range(16):
        xx=x+rng.uniform(-.23,.23)
        yy=y+rng.uniform(-.16,.16)
        a.include(f"nail_{i}",rod(.006,
                  start=(xx,yy,BENCH_Z+.065),
                  end=(xx+rng.uniform(-.07,.07),yy+.09,BENCH_Z+.075),
                  color=(.52,.53,.48)))
    add(f"hardware_tray_{j}",a)

for i,(x,y,ang) in enumerate(
        ((1.55,-1.65,30),(1.80,-1.10,-35),(.25,-1.66,72))):
    a=Asset(f"loose mallet {i}")
    cube(a,"handle",(.055,.64,.055),(0,0,.04),C["edge"])
    cube(a,"head",(.34,.15,.15),(0,.26,.09),C["honey"])
    a.turn('z',ang,pivot=(0,0,0))
    a.move((x,y,BENCH_Z))
    add(f"bench_mallet_{i}",a)

for i in range(5):
    a=Asset(f"foreground offcut {i}")
    cube(a,"timber",(rng.uniform(.23,.47),.12,.065),
         (rng.uniform(-.8,.6),rng.uniform(-1.85,-1.12),BENCH_Z+.04),
         C["edge"])
    add(f"loose_offcut_{i}",a)

labels=Asset("shelf inventory labels")
for j,z in enumerate(levels):
    for i in range(5):
        cube(labels,f"label_{j}_{i}",(.16,.008,.033),
             (-1.95+i*.88,1.607,z-.025),(.80,.76,.60))
add("labels",labels)

# Pre-execution self-review:
# Camera is the only revised parameter family; construction and random sequence
# match step 2. No absent-object duplication or visibility-driven relocation.
# Complete owners and their dependent parts retain transforms and materials.
# Explicit support levels are preserved; irregular contacts remain approximate.
# Roughly 600 primitives, mainly repeated shelf planes and handle racks.
# Decorative cost: 32 tray nails and nine primitives for the curved kettle bail.
# Positive finite dimensions; no fillets; distinct rod endpoints; unique slots.
# realize precedes camera/world/lights. No geometry follows realization.
# No local shader edits, material selectors or shared-mesh changes are used.
# This is a code review, not a claim of passing structural or collision tests.

realize(S)
set_view(**CAMERA)
scene=bpy.context.scene
if scene.world is None:
    scene.world=bpy.data.worlds.new("World")
scene.world.use_nodes=True
background=scene.world.node_tree.nodes["Background"]
background.inputs["Color"].default_value=(.62,.69,.72,1)
background.inputs["Strength"].default_value=LIGHTING["world_strength"]
area_emitter((-3.1,-.6,3.4),
             power=LIGHTING["window_power"],size=3.0,
             target=(0,1,1.2),color=(.79,.90,1))
area_emitter((.2,-2.3,4.2),
             power=LIGHTING["fill_power"],size=4,
             target=(0,1.0,1.4),color=(1,.91,.76))
