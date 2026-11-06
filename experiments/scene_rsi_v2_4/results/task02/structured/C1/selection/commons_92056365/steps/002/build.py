import bpy
import math
import random
from sceneact import *

# Reference inventory, normalized approximate bounds:
# Room: ceiling (0,0)-(1,.31), rear windows (0,.30)-(.72,.54),
# right windows (.72,.24)-(1,.65), dark narrow floor tiles below.
# Booths: left lane (0,.51)-(.33,.90), cropped front table (0,.85)-(.46,1).
# Chairs: square upholstered backs, thin arms, exposed chrome pedestal feet;
# repeated center/right (.34,.52)-(.85,.96). Front right back overlaps palm.
# Pendants: large left (.02,.12)-(.23,.40); small bells across (.12,.32)-(1,.44).
# Large shade landmarks: rim width 1, dome height .42 of width, neck width .36;
# pale curved interior visible under dark dome, thin rim, two neck bands.
# Palm: (.77,.40)-(1,1), long narrow leaflets, several overlapping fronds.
# Rear planter: (.32,.49)-(.58,.62). Exterior foliage is bright and indistinct.
# Hidden seating and exterior depth remain uncertain.
#
# Revision from rendered evidence:
# 1. Header is too low while furniture height is closer: architectural profile
#    changed by raising window heads, preserving camera and furniture depths.
# 2. Exterior trees read as giant isolated circles: local foliage profile and
#    cluster scale changed, with smaller overlapping masses beyond the windows.
# 3. Palm is outside the right crop: placement changed independently of its shape.
#    Right foreground chair is also moved inward to restore its overlap.
# 4. Largest shade is too far right and its neck too short: placement and local
#    neck proportions changed separately; open shell construction preserved.
# 5. Seating lacks the reference's dark planes: upholstery reflectance reduced.
#    Foreground booth/table placement adjusted toward the left crop.
# This is a combined correction, not an isolated causal test.
#
# Named SceneAct groups retain editable semantic children and local factories.
# Approximate expanded count: architecture 115, furniture 190, lamps 90 including
# Boolean operands, palm 185, rear vegetation 45, exterior 65: about 690 meshes.
# No rendering, file loading or saving is performed here.

random.seed(14)
scene = Scene("Window_side_cafeteria")
WHITE = (.85, .85, .85)
FRAME = (.27, .27, .27)
FABRIC = (.22, .22, .22)
SIDE = (.28, .28, .28)
DARK = (.035, .035, .035)
TOP = (.19, .19, .19)
METAL = (.60, .60, .60)
LEAF = (.035, .035, .035)

def add(parent, name, node):
    parent.include(name, node)
    return node

def place(asset, name, position, angle=0):
    asset.turn(axis="+z", degrees=angle, pivot=(0, 0, 0))
    asset.move(position)
    scene.include(name, asset)
    return asset

def ellipsoid(factors, center, color):
    n = ball(radius=1, color=color)
    n.resize(factors, pivot=(0, 0, 0))
    n.move(center)
    return n

room = Asset("Room")
add(room, "floor", box(size=(13,19,.13), center=(0,2,-.075),
                       color=(.18,.18,.18)))
add(room, "ceiling", box(size=(13,19,.12), center=(0,2,4.10),
                         color=(.89,.89,.89)))
for i in range(49):
    add(room, "ceiling_joint_%02d" % i,
        box(size=(12.9,.012,.009), center=(0,-6.5+i*.35,4.032),
            color=(.63,.63,.63)))
add(room, "back_apron", box(size=(12.8,.18,.48),
    center=(0,9,.24), color=WHITE))
add(room, "back_sill", box(size=(12.8,.27,.09),
    center=(0,8.94,.70), color=FRAME))
add(room, "back_header", box(size=(12.8,.20,.13),
    center=(0,9,3.66), color=FRAME))
add(room, "right_apron", box(size=(.18,16,.48),
    center=(6.3,1,.24), color=WHITE))
add(room, "right_sill", box(size=(.28,16,.09),
    center=(6.25,1,.70), color=FRAME))
add(room, "right_header", box(size=(.18,16,.13),
    center=(6.3,1,3.66), color=FRAME))
for i,x in enumerate([-6.25,-3.75,-1.25,1.25,3.75,6.25]):
    add(room, "back_mullion_%d" % i,
        box(size=(.065,.13,2.96), center=(x,8.98,2.18), color=FRAME))
for i,y in enumerate([-6,-3.2,-.4,2.4,5.2,8.95]):
    add(room, "right_mullion_%d" % i,
        box(size=(.13,.065,2.96), center=(6.27,y,2.18), color=FRAME))
for i in range(28):
    add(room, "floor_long_joint_%d" % i,
        box(size=(.009,18,.003), center=(-6.4+i*.47,1.8,-.006),
            color=(.36,.36,.36)))
for i in range(22):
    add(room, "floor_cross_joint_%d" % i,
        box(size=(12.7,.009,.003), center=(0,-6.5+i*.79,-.004),
            color=(.30,.30,.30)))
scene.include("architecture", room)

def chair(width=.98):
    a = Asset("Upholstered_pedestal_chair")
    add(a, "floor_foot", rod(radius=.30,length=.045,
        center=(0,0,.027),color=METAL))
    add(a, "pedestal", rod(radius=.065,length=.40,
        center=(0,0,.25),color=METAL))
    add(a, "seat", box(size=(width,.78,.13),
        center=(0,-.02,.53),color=FABRIC))
    add(a, "back", box(size=(width,.105,.74),
        center=(0,.37,.92),color=FABRIC))
    for side in [-1,1]:
        add(a, "arm_%d" % side, box(size=(.075,.76,.48),
            center=(side*(width/2-.025),.015,.78),color=SIDE))
    add(a, "back_top_seam", box(size=(width,.115,.018),
        center=(0,.37,1.295),color=SIDE))
    return a

def booth(width=1.95):
    a = Asset("Wide_booth")
    add(a,"base",box(size=(width-.12,.63,.33),
        center=(0,.02,.24),color=DARK))
    add(a,"seat",box(size=(width,.79,.14),
        center=(0,-.02,.48),color=FABRIC))
    add(a,"back",box(size=(width,.15,.80),
        center=(0,.36,.91),color=FABRIC))
    add(a,"top_seam",box(size=(width,.16,.025),
        center=(0,.36,1.32),color=SIDE))
    return a

def table(width=1.24, depth=.92, ashtray=False):
    a=Asset("Square_pedestal_table")
    add(a,"floor_disc",rod(radius=.31,length=.045,
        center=(0,0,.03),color=METAL))
    add(a,"column",rod(radius=.052,length=.75,
        center=(0,0,.42),color=METAL))
    add(a,"edge",box(size=(width,depth,.055),
        center=(0,0,.825),color=DARK))
    add(a,"top",box(size=(width-.012,depth-.012,.018),
        center=(0,0,.86),color=TOP))
    if ashtray:
        outer=rod(radius=.085,length=.029,center=(.17,.03,.889),
                  color=(.65,.65,.65))
        cutter=rod(radius=.062,length=.04,center=(.17,.03,.912),
                   color=(.65,.65,.65))
        add(a,"recessed_ashtray",subtract(outer,cutter))
    return a

for lane,x in enumerate([-3.4,-.40,2.52]):
    for row,y in enumerate([0,2.65,5.05,7.25]):
        place(table(ashtray=(row<2)), "table_%d_%d"%(lane,row),(x,y,0))
        if lane==0:
            place(booth(1.92),"left_booth_%d"%row,(x,y-1.03,0))
        else:
            place(chair(),"front_chair_%d_%d"%(lane,row),(x,y-1.02,0),180)
        if row>0:
            place(chair(.95),"rear_chair_%d_%d"%(lane,row),(x,y+.94,0))
place(booth(2.32),"foreground_left_booth",(-4.36,-2.65,0))
place(table(2.65,1.18),"foreground_left_table",(-4.12,-4.05,0))
place(chair(1.15),"foreground_right_chair",(2.55,-2.25,0),175)
place(table(1.33,1,True),"foreground_right_table",(1.55,-1.40,0))

def shade_shell(radius,height,thickness,color):
    outer=ellipsoid((radius,radius,height),(0,0,0),color)
    inner=ellipsoid((radius-thickness,radius-thickness,height-thickness),
                    (0,0,-.006),color)
    lower=box(size=(radius*3,radius*3,height*3),
              center=(0,0,-height*1.5),color=color)
    return subtract(outer,inner,lower)

def pendant(radius=.40,rim_height=2.70,large=False):
    a=Asset("Open_bell_pendant")
    dome_h=radius*.83
    shell=shade_shell(radius,dome_h,.027,DARK)
    shell.move((0,0,rim_height))
    add(a,"dark_dome_shell",shell)
    lining=shade_shell(radius-.030,dome_h-.027,.012,(.88,.88,.88))
    lining.move((0,0,rim_height+.004))
    add(a,"white_inner_shell",lining)
    nr=radius*.34
    nh=radius*(.96 if large else .70)
    neck_bottom=rim_height+dome_h*.78
    add(a,"neck",rod(radius=nr,length=nh,
        center=(0,0,neck_bottom+nh/2),color=DARK))
    for j,t in enumerate([.37,.72]):
        add(a,"neck_band_%d"%j,rod(radius=nr*1.025,length=.028,
            center=(0,0,neck_bottom+nh*t),color=(.42,.42,.42)))
    top=neck_bottom+nh
    if top<4.03:
        add(a,"suspension",rod(radius=.008,
            start=(0,0,top),end=(0,0,4.03),color=DARK))
    add(a,"ceiling_plate",rod(radius=.085,length=.018,
        center=(0,0,4.03),color=DARK))
    return a

place(pendant(.65,3.04,True),"large_left_pendant",(-4.66,-2.15,0))
for i,(x,y,r,z) in enumerate([
    (-3.4,3.5,.36,2.66),(-3.4,7.2,.27,2.60),
    (-.55,5,.34,2.69),(2.05,4.6,.39,2.77),
    (4.10,1.25,.49,2.96),(4.72,5.2,.32,2.73),
    (5.76,6.8,.29,2.72),(-4.9,6.5,.25,2.59)]):
    place(pendant(r,z),"repeating_pendant_%02d"%i,(x,y,0))

def leaf_between(start,end,width,color):
    d=tuple(end[i]-start[i] for i in range(3))
    length=math.sqrt(sum(v*v for v in d))
    n=ellipsoid((width,.012,length/2),(0,0,0),color)
    n.turn(axis="+y",degrees=math.degrees(math.acos(d[2]/length)),
           pivot=(0,0,0))
    n.turn(axis="+z",degrees=math.degrees(math.atan2(d[1],d[0])),
           pivot=(0,0,0))
    n.move(tuple((start[i]+end[i])/2 for i in range(3)))
    return n

palm=Asset("Foreground_palm")
add(palm,"planter",box(size=(.62,.62,.62),center=(0,0,.31),
                       color=(.10,.10,.10)))
add(palm,"soil",box(size=(.55,.55,.025),center=(0,0,.63),color=DARK))
for f in range(10):
    theta=f*math.tau/10+.15
    reach=1.03+.17*math.sin(f*2.1)
    high=2.58+.24*math.sin(f*1.7)
    base=(0,0,.64)
    p1=(.18*math.cos(theta),.18*math.sin(theta),high-.55)
    p2=(.57*reach*math.cos(theta),.57*reach*math.sin(theta),high)
    p3=(reach*math.cos(theta),reach*math.sin(theta),high-.32)
    add(palm,"frond_stem_%d"%f,
        sweep_tube(points=[base,p1,p2,p3],radius=.010,color=LEAF))
    for j in range(5):
        t=.23+j*.15
        c=(reach*t*math.cos(theta),reach*t*math.sin(theta),
           high-.85*(t-.57)**2)
        for side in [-1,1]:
            spread=(.42*(1-t)+.11)*side
            tip=(c[0]+.25*math.cos(theta)-spread*math.sin(theta),
                 c[1]+.25*math.sin(theta)+spread*math.cos(theta),
                 c[2]-.16)
            add(palm,"leaflet_%d_%d_%d"%(f,j,side),
                leaf_between(c,tip,.024,LEAF))
place(palm,"right_foreground_palm",(3.25,-1.65,0),10)

planter=Asset("Rear_low_planter")
add(planter,"container",box(size=(3.5,.48,.46),
    center=(0,0,.70),color=(.22,.22,.22)))
for i in range(22):
    x=random.uniform(-1.65,1.65)
    y=random.uniform(-.18,.18)
    z=random.uniform(.98,1.30)
    add(planter,"foliage_%d"%i,
        ellipsoid((.19,.11,.10),(x,y,z),(.21,.21,.21)))
    if i%2==0:
        add(planter,"shoot_%d"%i,rod(radius=.012,
            start=(x,y,.90),end=(x+.07,y,z+.18),color=LEAF))
place(planter,"rear_foliage_divider",(-.75,6.4,0))

outside=Asset("Exterior")
add(outside,"ground",box(size=(60,45,.08),
    center=(0,25,-.16),color=(.91,.91,.91)))
# Distant low pavilion and clustered foliage replace dominant round masses.
add(outside,"distant_building",box(size=(16,2,1.15),
    center=(-2,16,.55),color=(.83,.83,.83)))
add(outside,"distant_roof",box(size=(17,2.5,.12),
    center=(-2,16,1.18),color=(.66,.66,.66)))
for i in range(9):
    x=-12+i*3.2
    y=19+random.uniform(-1,3)
    h=random.uniform(2.2,4.0)
    add(outside,"tree_trunk_%d"%i,
        rod(radius=.07,start=(x,y,0),end=(x,y,h),color=(.57,.57,.57)))
    for j in range(5):
        c=(x+random.uniform(-.8,.8),y+random.uniform(-.65,.65),
           h+random.uniform(-.55,.7))
        add(outside,"canopy_%d_%d"%(i,j),
            ellipsoid((random.uniform(.55,.9),.52,
                       random.uniform(.5,.85)),c,(.72,.72,.72)))
scene.include("exterior",outside)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.94,.94,.94,1)
background.inputs["Strength"].default_value=.8

# Camera preserved because local header and vegetation errors do not alone
# establish a shared projection error.
set_view(position=(-4.10,-8.40,2.62),
         target=(.30,5,1.94),lens=33,sensor=36)
area_emitter(position=(0,8,3.45),power=1800,size=9,
             target=(0,1,.3),color=(1,1,1))
area_emitter(position=(6,1,3.3),power=1400,size=7,
             target=(0,1,.8),color=(1,1,1))
area_emitter(position=(-3,-4,3.8),power=170,size=5,
             target=(0,2,.5),color=(1,1,1))

for material in bpy.data.materials:
    if material.use_nodes:
        bsdf=material.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Roughness"].default_value=.48

sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform="AgX"
sc.view_settings.exposure=.35
sc.camera.data.clip_start=.06
sc.camera.data.clip_end=150
