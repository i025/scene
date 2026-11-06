from sceneact import *
import bpy
import math
import random

# Reference inventory (normalized image bounds):
# architecture: slatted pale ceiling (0,0)-(1,.32), rear windows
# (0,.30)-(.73,.56), right windows (.70,.25)-(1,.60), dark tiled
# floor (0,.56)-(1,1). Thin dark mullions and deep horizontal sills.
# booth_0..4: left receding upholstered backs (0,.52)-(.33,.90),
# overlapped by pale tabletops, especially foreground_table (0,.85)-(.46,1).
# table_* and chair_*: central/right furniture (.34,.52)-(.88,.98);
# broad rectangular backs, thin seats, chrome stems and circular feet.
# pendant_*: dark bell shades, dominant foreground left (.02,.12)-(.23,.36),
# neck and cord; smaller shades around (.12,.37), (.15,.42), (.39,.41),
# (.50,.40), (.60,.37), (.77,.34), (.82,.40), (.98,.39).
# foreground_palm: dark separated feather fronds (.76,.40)-(1,1),
# overlapping right furniture; rear_planter (.32,.49)-(.57,.60).
# Exterior is bright, irregular vegetation; exact distant objects and
# furniture hidden by the booths, chairs, and palm remain uncertain.
#
# Review of first image: foreground pendant and palm fell outside framing;
# chair/table colors were too pale, exterior shrubs too solid and prominent,
# rear ceiling line too low, foreground booth too small. Corrections below
# retain the named furniture hierarchy and move only supported local items.
# Expanded primitive estimate: architecture 108, booths 20, tables 84,
# chairs 85, pendants 72, palm 173, rear planting 26, exterior 15,
# small table objects 12: approximately 695 meshes including Boolean
# operands and the five primitives per three-point sweep. No fillet boxes.

random.seed(14)
scene = Scene("Cafeteria reconstruction")
ivory = (.77,.78,.75)
frame = (.18,.20,.18)
upholstery = (.115,.135,.12)
seatcolor = (.16,.18,.16)
tablecolor = (.57,.60,.55)
metal = (.48,.52,.49)
dark = (.025,.035,.026)
floorcolor = (.095,.12,.105)
ceiling_z = 3.95

architecture = Asset("architecture")
architecture.include("tiled_floor", box((10.6,16,.13), center=(0,3,-.08), color=floorcolor))
architecture.include("ceiling", box((10.6,16,.12), center=(0,3,ceiling_z+.06), color=(.84,.85,.82)))
for i in range(45):
    architecture.include("ceiling_seam_%02d" % i,
                         box((10.5,.011,.008), center=(0,-4.8+i*.35,ceiling_z-.004),
                             color=(.49,.52,.48)))
for i in range(25):
    architecture.include("floor_length_joint_%02d" % i,
                         box((.009,16,.005), center=(-5.1+i*.43,3,-.009),
                             color=(.27,.30,.27)))
for j in range(17):
    architecture.include("floor_cross_joint_%02d" % j,
                         box((10.5,.009,.005), center=(0,-4+j*.88,-.008),
                             color=(.22,.25,.22)))
architecture.include("rear_apron", box((10.3,.2,1.05), center=(0,10.15,.525), color=ivory))
architecture.include("rear_sill", box((10.4,.34,.10), center=(0,10.02,1.10), color=(.48,.51,.47)))
architecture.include("rear_header", box((10.4,.14,.12), center=(0,10.12,3.69), color=frame))
architecture.include("rear_ceiling_beam", box((10.4,.18,.15), center=(0,10.05,3.83), color=(.53,.56,.52)))
for i,x in enumerate([-5,-3.3,-1.6,.1,1.8,3.5,5]):
    architecture.include("rear_mullion_%d" % i,
                         box((.065,.12,2.55), center=(x,10.1,2.40), color=frame))
architecture.include("right_apron", box((.17,15,1.05), center=(5.05,2.7,.525), color=ivory))
architecture.include("right_sill", box((.30,15,.10), center=(4.99,2.7,1.10), color=(.48,.51,.47)))
architecture.include("right_header", box((.14,15,.12), center=(5.07,2.7,3.69), color=frame))
for i,y in enumerate([-4,-1,2,5,8,10]):
    architecture.include("right_mullion_%d" % i,
                         box((.085,.065,2.55), center=(5.02,y,2.40), color=frame))
scene.include("architecture", architecture)

def make_table(name,x,y,w=1.45,d=.87):
    a=Asset(name)
    a.include("laminate_top",box((w,d,.055),center=(x,y,.79),color=tablecolor))
    a.include("dark_edge",box((w+.009,d+.009,.025),center=(x,y,.758),color=(.12,.15,.12)))
    for k,dx in enumerate([-.34,.34]):
        a.include("support_%d"%k,rod(.032,start=(x+dx,y,.07),end=(x+dx,y,.75),color=metal))
        a.include("foot_%d"%k,box((.10,.57,.045),center=(x+dx,y,.045),color=metal))
    scene.include(name,a)

def make_chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("seat",box((.72,.61,.105),center=(x,y,.51),color=seatcolor))
    a.include("broad_back",box((.75,.085,.74),center=(x,y-.29,.88),color=upholstery))
    a.include("back_support",box((.56,.045,.23),center=(x,y-.245,.54),color=upholstery))
    a.include("polished_pedestal",rod(.052,start=(x,y,.08),end=(x,y,.46),color=metal))
    a.include("circular_base",rod(.255,length=.045,center=(x,y,.045),color=metal))
    if angle:
        a.turn('z',angle,pivot=(x,y,0))
    scene.include(name,a)

for i,y in enumerate([-1.30,1.15,3.55,5.95,8.25]):
    a=Asset("booth_%d"%i)
    a.include("wide_back",box((2.70,.17,.94),center=(-3.25,y,.75),color=upholstery))
    a.include("seat_cushion",box((2.70,.64,.15),center=(-3.25,y+.36,.45),color=seatcolor))
    a.include("recessed_base",box((2.42,.48,.36),center=(-3.25,y+.34,.19),color=(.08,.11,.085)))
    a.include("end_trim",box((.045,.68,.55),center=(-1.89,y+.26,.40),color=(.32,.35,.31)))
    scene.include("booth_%d"%i,a)
    make_table("left_table_%d"%i,-3.23,y+1.10,2.58,.94)

for row,y in enumerate([-.35,2.15,4.65,7.1]):
    make_table("center_table_%d"%row,.10,y,1.48,.92)
    make_chair("center_near_chair_%d"%row,.10,y-.79)
    make_chair("center_far_chair_%d"%row,.10,y+.79,180)
    make_table("right_table_%d"%row,2.28,y+.25,1.53,.92)
    make_chair("right_near_chair_%d"%row,2.28,y-.54)
    if row>0:
        make_chair("right_far_chair_%d"%row,2.28,y+1.04,180)

make_table("foreground_table",-2.70,-2.43,2.75,1.42)

def pendant(name,x,y,r,bottom):
    a=Asset(name)
    dome=ball(r,center=(x,y,bottom),color=dark)
    dome.resize((1,1,.78),pivot=(x,y,bottom))
    cutter=box((r*2.5,r*2.5,r*2),center=(x,y,bottom-r),color=dark)
    a.include("bell_dome",subtract(dome,cutter))
    a.include("pale_inner_surface",rod(r*.94,length=.012,center=(x,y,bottom-.008),color=(.65,.68,.61)))
    a.include("rim",rod(r,length=.018,center=(x,y,bottom+.008),color=dark))
    a.include("neck",rod(r*.34,length=r*.77,center=(x,y,bottom+r*.85),color=dark))
    for k,t in enumerate([.79,1.02]):
        a.include("neck_band_%d"%k,rod(r*.345,length=.024,center=(x,y,bottom+r*t),color=(.30,.34,.29)))
    a.include("cord",rod(.008,start=(x,y,bottom+r*1.25),end=(x,y,ceiling_z),color=(.10,.13,.10)))
    a.include("ceiling_rose",rod(.065,length=.022,center=(x,y,ceiling_z-.012),color=dark))
    scene.include(name,a)

pendant("pendant_front_left",-2.78,-.05,.64,2.58)
pendant("pendant_left_second",-3.5,3.10,.43,2.42)
pendant("pendant_left_third",-3.5,5.8,.33,2.40)
pendant("pendant_rear_left",-2.6,8.1,.25,2.37)
pendant("pendant_rear_center",-.15,7.7,.28,2.45)
pendant("pendant_center",1.15,4.15,.37,2.58)
pendant("pendant_right_front",2.18,1.30,.43,2.68)
pendant("pendant_right_middle",3.5,4.9,.29,2.46)
pendant("pendant_right_rear",4.25,8.0,.24,2.40)

def leaf(a,name,start,end,width,color):
    mid=tuple((start[i]+end[i])/2 for i in range(3))
    v=tuple(end[i]-start[i] for i in range(3))
    length=math.sqrt(sum(t*t for t in v))
    node=ball(1,center=(0,0,0),color=color)
    node.resize((width,.009,length/2),pivot=(0,0,0))
    node.turn('y',math.degrees(math.acos(v[2]/length)),pivot=(0,0,0))
    node.turn('z',math.degrees(math.atan2(v[1],v[0])),pivot=(0,0,0))
    node.move(mid)
    a.include(name,node)

palm=Asset("foreground_palm")
px,py=2.33,-1.30
palm.include("planter",rod(.29,length=.48,center=(px,py,.24),color=(.12,.16,.12)))
palm.include("soil",rod(.27,length=.022,center=(px,py,.49),color=(.035,.045,.025)))
for f in range(9):
    az=math.radians(15+f*40)
    reach=.66+(f%3)*.20
    height=1.65+(f%4)*.20
    base=(px,py,.45)
    bend=(px+math.cos(az)*reach*.38,py+math.sin(az)*reach*.38,height+.18)
    tip=(px+math.cos(az)*reach,py+math.sin(az)*reach,height-.12)
    palm.include("frond_stem_%d"%f,sweep_tube(points=[base,bend,tip],radius=.009,color=(.045,.075,.035)))
    for j in range(7):
        t=.10+j*.13
        point=tuple(bend[k]+(tip[k]-bend[k])*t for k in range(3))
        span=.34*(1-t)+.10
        for side in [-1,1]:
            end=(point[0]+math.cos(az+side*1.23)*span,
                 point[1]+math.sin(az+side*1.23)*span,
                 point[2]+.05-span*.33)
            leaf(palm,"leaf_%d_%d_%d"%(f,j,side),point,end,.021,(.028,.052,.023))
# Lower foliage fills the visible plant silhouette without hiding frond gaps.
for i in range(8):
    az=i*math.pi/4
    start=(px,py,.55)
    end=(px+.50*math.cos(az),py+.50*math.sin(az),1.10+(i%3)*.14)
    leaf(palm,"lower_leaf_%d"%i,start,end,.075,(.035,.063,.027))
scene.include("foreground_palm",palm)

rear=Asset("rear_planter")
rear.include("container",box((2.6,.43,.25),center=(-.95,8.75,1.03),color=(.18,.23,.17)))
for i in range(13):
    x=-2.1+i*.19
    z=1.24+random.random()*.16
    rear.include("stem_%d"%i,rod(.012,start=(x,8.74,1.12),end=(x,8.74,z+.17),color=(.14,.19,.12)))
    rear.include("foliage_%d"%i,ball(.15,center=(x,8.74,z),color=(.16,.22,.13)))
scene.include("rear_planter",rear)

outside=Asset("exterior_vegetation")
for i in range(15):
    node=ball(.38+random.random()*.4,
              center=(-6+i*.9,14.6+random.random()*2,.8+random.random()*.35),
              color=(.68,.71,.65))
    node.resize((1.3,1,.8))
    outside.include("distant_shrub_%d"%i,node)
scene.include("exterior_vegetation",outside)

# Small pale ashtrays visible on several tables.
for i,(x,y) in enumerate([(0.10,-.35),(2.28,-.10),(.1,2.15),(2.28,2.4)]):
    a=Asset("table_accessory_%d"%i)
    a.include("ashtray",rod(.078,length=.025,center=(x+.22,y,.833),color=(.72,.75,.70)))
    a.include("inner_recess",rod(.052,length=.005,center=(x+.22,y,.848),color=(.32,.36,.31)))
    a.include("small_packet",box((.10,.065,.035),center=(x+.34,y+.05,.837),color=(.66,.69,.63)))
    scene.include("table_accessory_%d"%i,a)

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
background.inputs["Color"].default_value=(.9,.92,.88,1)
background.inputs["Strength"].default_value=.45

# Use the emitted material colors directly; preserve dark furniture finishes.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        c=bs.inputs["Base Color"].default_value
        d=mat.diffuse_color
        if sum(d[:3]) < sum(c[:3]):
            c=d
        g=.28*c[0]+.55*c[1]+.17*c[2]
        bs.inputs["Base Color"].default_value=(g,g,g,c[3])
        bs.inputs["Roughness"].default_value=.48

set_view(position=(-.9,-5.55,1.88),target=(.25,5.3,1.45),lens=29,sensor=36)
area_emitter((0,10.9,3.0),power=1400,size=7,target=(0,1.5,.5))
area_emitter((5.5,2.4,3),power=1100,size=6,target=(-2,2,.8))
area_emitter((-2,-3,3.6),power=160,size=5,target=(0,3,.5))
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
