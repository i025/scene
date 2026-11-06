from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image bounds:
# Architecture: pale slatted ceiling (0,0)-(1,.34), dark tiled floor
# (0,.55)-(1,1); rear glazing (.02,.31)-(.76,.58), right glazing
# (.73,.24)-(1,.58), with thin dark mullions and broad pale sills.
# Left booths (0,.51)-(.38,.91): long upholstered backs, seats and plinths;
# foreground tabletop (0,.85)-(.47,1) overlaps the closest booth.
# Tables and pedestal chairs (.34,.51)-(.88,.98): thin rectangular tops,
# broad upholstered rectangular backs, seat pads, single polished stems
# and circular feet. Far furniture is partly hidden by nearer furniture.
# Pendants: dominant left shade (.02,.12)-(.23,.40); smaller shades at
# (.07,.35), (.13,.40), (.37,.38), (.47,.36), (.57,.34),
# (.73,.30), (.79,.38), (.94,.35). Thin cords meet the ceiling.
# Large right palm (.75,.39)-(1,1): several arching fronds with separated
# narrow leaflets, overlapping right chairs; smaller planting at rear.
# Exterior detail is washed out and uncertain; only soft vegetation masses
# are represented. Hidden furniture and room extents remain approximate.
#
# Asset mapping: architecture, booth_*, table_*, chair_*, pendant_*,
# foreground_palm, rear_planter, exterior_vegetation.
# Estimated expanded geometry: architecture 85, booths 20, tables 24,
# chairs 90, pendants ~45 including cutters, palms ~112, exterior 18:
# approximately 394 primitive meshes, no fillet boxes or dense tube paths.

random.seed(14)
scene = Scene("Window-side cafeteria")
ivory = (.79,.80,.76)
frame = (.36,.38,.35)
upholstery = (.27,.30,.27)
seatcolor = (.31,.34,.30)
tablecolor = (.72,.74,.68)
metal = (.57,.60,.57)
dark = (.075,.095,.075)
floorcolor = (.22,.25,.23)

architecture = Asset("architecture")
architecture.include("tiled_floor", box((10.6,15,.13), center=(0,3.4,-.08), color=floorcolor))
architecture.include("ceiling", box((10.6,15,.12), center=(0,3.4,3.56), color=(.87,.88,.84)))
# Long narrow ceiling boards, with subdued seams.
for i in range(39):
    y = -3.6+i*.365
    architecture.include("ceiling_seam_%02d"%i,
                         box((10.5,.012,.009), center=(0,y,3.491), color=(.58,.61,.57)))
for x in [-4.8+i*.43 for i in range(24)]:
    architecture.include("floor_long_joint_%s"%x,
                         box((.013,15,.006), center=(x,3.4,-.009), color=(.41,.43,.39)))
for j in range(17):
    architecture.include("floor_cross_joint_%02d"%j,
                         box((10.5,.014,.006), center=(0,-3.4+j*.84,-.008), color=(.36,.39,.35)))
# Rear and right window assemblies. Bright exterior replaces any image backdrop.
architecture.include("rear_apron", box((10.3,.20,1.02), center=(0,10.15,.51), color=ivory))
architecture.include("rear_sill", box((10.4,.34,.11), center=(0,10.02,1.06), color=(.64,.66,.61)))
architecture.include("rear_header", box((10.4,.15,.13), center=(0,10.12,3.27), color=frame))
for i,x in enumerate([-5,-3.3,-1.6,.1,1.8,3.5,5]):
    architecture.include("rear_mullion_%d"%i, box((.075,.13,2.2), center=(x,10.1,2.18), color=frame))
architecture.include("right_apron", box((.17,13.8,1.02), center=(5.05,3.2,.51), color=ivory))
architecture.include("right_sill", box((.30,14,.10), center=(4.99,3.2,1.06), color=(.63,.66,.60)))
architecture.include("right_header", box((.14,14,.12), center=(5.07,3.2,3.28), color=frame))
for i,y in enumerate([-3,0,3,6,9]):
    architecture.include("right_mullion_%d"%i, box((.10,.075,2.21), center=(5.02,y,2.18), color=frame))
architecture.include("rear_ceiling_beam", box((10.4,.15,.18), center=(0,9.98,3.36), color=(.65,.68,.63)))
scene.include("architecture", architecture)

def make_table(name,x,y,w=1.45,d=.87):
    a=Asset(name)
    a.include("laminate_top",box((w,d,.065),center=(x,y,.79),color=tablecolor))
    a.include("dark_edge",box((w+.012,d+.012,.027),center=(x,y,.758),color=(.22,.25,.22)))
    for k,dx in enumerate([-.34,.34]):
        a.include("support_%d"%k,rod(.036,start=(x+dx,y,.08),end=(x+dx,y,.75),color=metal))
        a.include("foot_%d"%k,box((.12,.61,.055),center=(x+dx,y,.055),color=metal))
    scene.include(name,a)
    return a

def make_chair(name,x,y,angle=0):
    a=Asset(name)
    a.include("seat",box((.68,.60,.12),center=(x,y,.51),color=seatcolor))
    a.include("broad_back",box((.70,.095,.70),center=(x,y-.29,.87),color=upholstery))
    a.include("back_lower_support",box((.53,.055,.25),center=(x,y-.245,.54),color=upholstery))
    a.include("polished_pedestal",rod(.055,start=(x,y,.09),end=(x,y,.46),color=metal))
    a.include("circular_base",rod(.255,length=.055,center=(x,y,.055),color=metal))
    if angle:
        a.turn('z',angle,pivot=(x,y,0))
    scene.include(name,a)

# Left upholstered booths form a receding rhythm across the left half.
for i,y in enumerate([-.65,1.65,3.85,6.05,8.25]):
    a=Asset("booth_%d"%i)
    a.include("wide_back",box((2.52,.19,.92),center=(-3.48,y,.73),color=upholstery))
    a.include("seat_cushion",box((2.52,.64,.16),center=(-3.48,y+.36,.45),color=seatcolor))
    a.include("recessed_base",box((2.25,.48,.36),center=(-3.48,y+.34,.19),color=(.18,.21,.18)))
    a.include("end_trim",box((.065,.68,.55),center=(-2.20,y+.26,.40),color=(.40,.43,.39)))
    scene.include("booth_%d"%i,a)
    make_table("left_table_%d"%i,-3.45,y+1.05,2.43,.94)

# Main two rows of café tables and chairs.
for row,y in enumerate([.25,2.7,5.05,7.35]):
    make_table("center_table_%d"%row,.05,y,1.48,.92)
    make_chair("center_near_chair_%d"%row,.05,y-.79,0)
    make_chair("center_far_chair_%d"%row,.05,y+.79,180)
    make_table("right_table_%d"%row,2.75,y+.25,1.53,.92)
    make_chair("right_near_chair_%d"%row,2.75,y-.54,0)
    if row>0:
        make_chair("right_far_chair_%d"%row,2.75,y+1.04,180)

# Foreground table is cut by the image edge.
make_table("foreground_table",-2.70,-2.08,2.75,1.40)

# Suspended bell shades: a hemispherical dome, neck, visible pale underside.
def pendant(name,x,y,r,drop):
    a=Asset(name)
    bottom=3.5-drop
    dome=ball(r,center=(x,y,bottom),color=dark)
    dome.resize((1,1,.78),pivot=(x,y,bottom))
    cutter=box((r*2.5,r*2.5,r*2),center=(x,y,bottom-r),color=dark)
    a.include("bell_dome",subtract(dome,cutter))
    a.include("light_underneath",rod(r*.94,length=.018,center=(x,y,bottom+.005),color=(.89,.91,.84)))
    a.include("shade_rim",rod(r,length=.026,center=(x,y,bottom+.018),color=(.12,.15,.12)))
    a.include("neck",rod(r*.33,length=r*.64,center=(x,y,bottom+r*.83),color=dark))
    a.include("neck_band",rod(r*.34,length=.035,center=(x,y,bottom+r*.92),color=(.49,.52,.46)))
    cordstart=bottom+r*1.15
    a.include("cord",rod(.009,start=(x,y,cordstart),end=(x,y,3.5),color=(.18,.21,.17)))
    a.include("ceiling_rose",rod(.075,length=.025,center=(x,y,3.48),color=dark))
    scene.include(name,a)

pendant("pendant_front_left",-3.6,-1.65,.62,.94)
pendant("pendant_left_second",-3.5,1.7,.43,1.03)
pendant("pendant_left_third",-3.5,4.9,.33,1.04)
pendant("pendant_rear_left",-2.6,8.1,.25,1.12)
pendant("pendant_rear_center",-.15,7.7,.28,1.03)
pendant("pendant_center",1.15,4.15,.37,.97)
pendant("pendant_right_front",3.2,.80,.43,.83)
pendant("pendant_right_middle",3.95,4.35,.30,1.01)
pendant("pendant_right_rear",4.25,8.0,.24,1.10)

# Directional leaf helper. Ellipsoids remain separate named editable parts.
def leaf(a,name,start,end,width,color):
    mid=tuple((start[i]+end[i])/2 for i in range(3))
    v=tuple(end[i]-start[i] for i in range(3))
    length=math.sqrt(sum(t*t for t in v))
    node=ball(1,center=(0,0,0),color=color)
    node.resize((width,.012,length/2),pivot=(0,0,0))
    node.turn('y',math.degrees(math.acos(v[2]/length)),pivot=(0,0,0))
    node.turn('z',math.degrees(math.atan2(v[1],v[0])),pivot=(0,0,0))
    node.move(mid)
    a.include(name,node)

palm=Asset("foreground_palm")
px,py=4.12,-.75
palm.include("planter",rod(.34,length=.53,center=(px,py,.27),color=(.30,.33,.28)))
palm.include("soil",rod(.32,length=.025,center=(px,py,.54),color=(.11,.13,.09)))
for f in range(9):
    az=math.radians(35+f*40)
    reach=.8+(f%3)*.23
    height=1.55+(f%4)*.24
    base=(px,py,.46)
    tip=(px+math.cos(az)*reach,py+math.sin(az)*reach,height)
    mid=(px+math.cos(az)*reach*.45,py+math.sin(az)*reach*.45,height+.25)
    palm.include("frond_stem_%d"%f,sweep_tube(points=[base,mid,tip],radius=.013,color=(.15,.20,.12)))
    for j in range(5):
        t=.27+j*.145
        cx=mid[0]+(tip[0]-mid[0])*t
        cy=mid[1]+(tip[1]-mid[1])*t
        cz=mid[2]+(tip[2]-mid[2])*t
        span=.38*(1-t)+.12
        for side in [-1,1]:
            end=(cx+math.cos(az+side*1.15)*span,
                 cy+math.sin(az+side*1.15)*span,cz+.10-span*.3)
            leaf(palm,"leaf_%d_%d_%d"%(f,j,side),(cx,cy,cz),end,.034,(.13,.18,.11))
scene.include("foreground_palm",palm)

rear=Asset("rear_planter")
rear.include("container",box((2.6,.43,.25),center=(-.95,8.75,1.03),color=(.35,.39,.32)))
for i in range(13):
    x=-2.1+i*.19
    rear.include("foliage_%d"%i,ball(.19,center=(x,8.74,1.28+random.random()*.18),color=(.29,.35,.25)))
scene.include("rear_planter",rear)

outside=Asset("exterior_vegetation")
for i in range(15):
    outside.include("soft_shrub_%d"%i,
                    ball(.65+random.random()*.5,
                         center=(-6+i*.9,12.6+random.random(),1.1+random.random()*.6),
                         color=(.68,.72,.64)))
scene.include("exterior_vegetation",outside)

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
background.inputs["Color"].default_value=(.86,.89,.85,1)
background.inputs["Strength"].default_value=.8

# The photograph is nearly monochrome; restrained rough materials preserve it.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Roughness"].default_value=.67
        c=bs.inputs["Base Color"].default_value
        g=.28*c[0]+.55*c[1]+.17*c[2]
        bs.inputs["Base Color"].default_value=(g*.98,g,g*.97,c[3])

set_view(position=(-.9,-5.55,1.88),target=(.25,5.3,1.75),lens=29,sensor=36)
area_emitter((0,8.7,3.1),power=1700,size=7,target=(0,1.5,.4))
area_emitter((4.7,2.4,2.8),power=1300,size=6,target=(-2,2,1))
area_emitter((-2,-3,3.2),power=450,size=5,target=(0,3,.5))
sc.render.resolution_x=512
sc.render.resolution_y=379
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
