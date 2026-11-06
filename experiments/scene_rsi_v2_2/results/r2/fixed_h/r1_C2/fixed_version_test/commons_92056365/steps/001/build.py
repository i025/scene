from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image coordinates:
# Architecture: pale slatted ceiling (0,0)-(1,.33); rear glazing
# (0,.30)-(1,.57); right glazing (.66,.25)-(1,.65); dark tiled floor
# (0,.54)-(1,1). Slim dark mullions, pale window rails and outdoor foliage.
# Foreground left table (0,.85)-(.46,1), and broad upholstered booth
# backs (0,.52)-(.33,.90). More booths recede towards the rear left.
# Center/right dining: pale rectangular tables (.34,.52)-(.85,.76),
# gray slab-backed swivel seats (.34,.53)-(.88,1), polished pedestal feet.
# Large foreground pendant (.015,.04)-(.24,.40); smaller dark pendants
# distributed across the ceiling, with long thin cords and white undersides.
# Dense palm at right (.77,.40)-(1,1); low leafy divider near rear center.
# Windows conceal uncertain exterior detail; chair/table overlaps conceal
# some supports. Only economical, plausible supports are included.
#
# Named assets below map these groups to editable semantic child parts.
# Estimated expansion: architecture 105 primitives, exterior 25,
# 8 tables 40, 15 chairs 75, 5 benches 25, 11 lamps about 55,
# plants about 110, accessories 12: roughly 550 primitive meshes.
# Shade Boolean operands are limited to two per pendant.

random.seed(12)
scene = Scene("Windowed cafeteria")

WHITE = (.79,.80,.77)
CEILING = (.86,.87,.83)
FRAME = (.35,.38,.35)
METAL = (.50,.53,.51)
DARK = (.055,.075,.062)
UPHOL = (.31,.35,.32)
FLOOR = (.24,.28,.26)

architecture = Asset("Architecture")
architecture.include("tiled_floor", box((12,17,.12), center=(0,1,-.08), color=FLOOR))
architecture.include("slatted_ceiling", box((12,17,.14), center=(0,1,4.35), color=CEILING))
# Restrained thin joints preserve the narrow ceiling plank rhythm.
for j in range(48):
    y = -6.8+j*.32
    architecture.include("ceiling_joint_%02d"%j,
                         box((11.9,.012,.008), center=(0,y,4.273), color=(.55,.58,.55)))
for i in range(25):
    x=-5.8+i*.48
    architecture.include("floor_long_joint_%02d"%i,
                         box((.012,16,.006),center=(x,1,.0),color=(.46,.49,.46)))
for j in range(14):
    architecture.include("floor_cross_joint_%02d"%j,
                         box((12,.012,.006),center=(0,-6+j*1.15,.002),color=(.38,.42,.39)))

# Window walls are open between framing members; pale exterior provides daylight.
architecture.include("rear_sill_wall",box((12,.20,.66),center=(0,8,.33),color=(.70,.73,.69)))
architecture.include("rear_header",box((12,.20,.22),center=(0,8,4.13),color=WHITE))
for z in (.78,1.12,3.98):
    architecture.include("rear_rail_"+str(z),box((12,.13,.075),center=(0,7.93,z),color=FRAME))
for i,x in enumerate((-5.8,-4,-2,0,2,4,5.8)):
    architecture.include("rear_mullion_%d"%i,box((.075,.13,3.24),center=(x,7.93,2.42),color=FRAME))
architecture.include("right_low_wall",box((.18,16,.68),center=(5.9,.1,.34),color=(.70,.73,.69)))
architecture.include("right_header",box((.18,16,.20),center=(5.9,.1,4.12),color=WHITE))
for z in (.80,1.13,4.0):
    architecture.include("right_rail_"+str(z),box((.13,16,.07),center=(5.83,.1,z),color=FRAME))
for i,y in enumerate((-5,-2,1,4,7.9)):
    architecture.include("right_mullion_%d"%i,box((.12,.07,3.23),center=(5.83,y,2.42),color=FRAME))
architecture.include("left_wall",box((.15,16,4.3),center=(-5.95,.1,2.1),color=(.73,.76,.72)))
scene.include("architecture",architecture)

outside=Asset("Pale outdoor view")
outside.include("rear_haze",box((25,.1,7),center=(0,11,3),color=(.88,.90,.86)))
outside.include("side_haze",box((.1,24,7),center=(9,1,3),color=(.91,.92,.88)))
outside.include("distant_ground",box((25,18,.1),center=(0,12,-.12),color=(.76,.79,.73)))
for i in range(12):
    x=random.uniform(-9,9)
    y=random.uniform(9.3,10.3)
    z=random.uniform(1.3,2.6)
    outside.include("tree_trunk_%d"%i,rod(.045,start=(x,y,.1),end=(x,y,z),color=(.56,.60,.53)))
    canopy=ball(random.uniform(.6,1.05),center=(x,y,z+.5),color=(.70,.75,.67))
    canopy.resize((1,.7,1))
    outside.include("distant_tree_%d"%i,canopy)
scene.include("exterior",outside)

def table(name,x,y,w=1.55,d=.85):
    a=Asset(name)
    a.include("dark_top_edge",box((w,d,.075),center=(x,y,.87),color=(.20,.24,.21)))
    a.include("pale_laminate_top",box((w-.018,d-.018,.035),center=(x,y,.923),color=(.78,.81,.77)))
    a.include("pedestal",rod(.055,start=(x,y,.10),end=(x,y,.85),color=METAL))
    a.include("foot_cross_x",box((.70,.085,.05),center=(x,y,.055),color=METAL))
    a.include("foot_cross_y",box((.085,.54,.05),center=(x,y,.055),color=METAL))
    scene.include(name,a)
    return a

def chair(name,x,y,angle=0):
    a=Asset(name)
    # Local forward is -Y, with a broad thin back and a visible deep seat.
    a.include("seat",box((.76,.69,.13),center=(x,y,.58),color=UPHOL))
    a.include("back",box((.78,.095,.88),center=(x,y+.31,1.01),color=UPHOL))
    a.include("back_edge",box((.79,.10,.035),center=(x,y+.31,1.455),color=(.48,.52,.47)))
    a.include("chrome_stem",rod(.065,start=(x,y,.09),end=(x,y,.54),color=(.66,.69,.66)))
    a.include("round_base",rod(.27,length=.065,center=(x,y,.055),color=(.65,.68,.64)))
    a.turn("z",angle,pivot=(x,y,0))
    scene.include(name,a)
    return a

def bench(name,x,y,width=2.7):
    a=Asset(name)
    a.include("upholstered_seat",box((width,.71,.20),center=(x,y,.56),color=(.30,.35,.31)))
    a.include("broad_back",box((width,.16,.95),center=(x,y+.34,.99),color=(.32,.37,.33)))
    a.include("top_piping",box((width,.18,.035),center=(x,y+.34,1.48),color=(.51,.55,.50)))
    for dx in (-width*.36,width*.36):
        a.include("support_"+str(dx),box((.12,.46,.43),center=(x+dx,y,.25),color=(.36,.40,.36)))
    scene.include(name,a)

# Closest table and long banks on the left, successively narrower in perspective.
table("foreground_left_table",-3.0,-4.15,3.0,1.55)
for i,y in enumerate((-3.1,-.9,1.25,3.4,5.5)):
    bench("left_booth_%d"%i,-3.55,y,2.9)
    if i>0:
        table("left_booth_table_%d"%i,-3.50,y-.75,2.75,1.05)

# Staggered central/right dining groups.
table("front_right_table",2.1,-1.35,1.85,1.05)
chair("front_right_near_seat",2.77,-2.38,0)
chair("front_right_left_seat",.88,-1.42,90)
chair("front_right_far_seat",2.58,-.36,180)

table("middle_table",.40,1.05,1.65,.98)
chair("middle_near_seat",.20,.08,0)
chair("middle_left_seat",-.80,1.10,90)
chair("middle_far_seat",.48,2.0,180)

table("right_middle_table",3.33,1.35,1.62,.98)
chair("right_middle_near_seat",3.25,.39,0)
chair("right_middle_left_seat",2.20,1.38,90)
chair("right_middle_far_seat",3.35,2.29,180)

table("rear_center_table",.05,3.61,1.65,.9)
chair("rear_center_near_seat",.05,2.75,0)
chair("rear_center_left_seat",-1.05,3.62,90)
chair("rear_center_far_seat",.12,4.48,180)

table("rear_right_table",3.15,4.16,1.7,.95)
chair("rear_right_near_seat",3.17,3.24,0)
chair("rear_right_left_seat",1.98,4.14,90)
chair("rear_right_far_seat",3.15,5.06,180)

# The main lamp is close to the camera. Small repetitions establish depth.
def pendant(name,x,y,bottom,radius):
    a=Asset(name)
    dome_center=bottom+.035
    dome=ball(radius,center=(x,y,dome_center),color=DARK)
    dome.resize((1,1,.72))
    cutter=box((radius*2.5,radius*2.5,radius*1.5),
               center=(x,y,dome_center-radius*.75),color=DARK)
    a.include("flared_dome",subtract(dome,cutter))
    a.include("bright_inner_disk",rod(radius*.87,length=.016,
                                     center=(x,y,bottom+.014),color=(.87,.89,.83)))
    a.include("shade_lip",rod(radius,length=.032,center=(x,y,bottom+.03),color=DARK))
    # A smaller pale disk shows beneath the dark lip.
    a.include("underside",rod(radius*.89,length=.012,center=(x,y,bottom+.009),color=(.87,.89,.82)))
    neckbottom=bottom+radius*.50
    necktop=bottom+radius*1.11
    a.include("cylindrical_neck",rod(radius*.31,start=(x,y,neckbottom),
                                  end=(x,y,necktop),color=DARK))
    a.include("neck_band",rod(radius*.318,length=.025,
                             center=(x,y,necktop-.12),color=(.50,.54,.47)))
    a.include("suspension_wire",rod(.009,start=(x,y,necktop),end=(x,y,4.27),color=(.24,.28,.24)))
    a.include("ceiling_rose",rod(.085,length=.025,center=(x,y,4.255),color=DARK))
    scene.include(name,a)

pendant("large_foreground_pendant",-3.75,-3.13,3.00,.67)
pendant("left_second_pendant",-3.68,.15,2.94,.42)
pendant("left_third_pendant",-3.68,3.0,2.98,.30)
pendant("left_rear_pendant",-3.68,5.85,2.99,.23)
pendant("center_rear_pendant",-.90,5.8,2.99,.26)
pendant("center_pendant",1.0,2.53,3.04,.35)
pendant("center_distant_pendant",1.0,6.7,3.02,.22)
pendant("right_large_pendant",3.53,.12,3.10,.42)
pendant("right_middle_pendant",4.4,3.47,3.02,.28)
pendant("right_rear_pendant",4.5,6.5,3.03,.24)

# Foliage uses individual tapered blades, with explicit open gaps.
def leaf_blade(name,start,end,width,color):
    mid=tuple(start[k]*.46+end[k]*.54 for k in range(3))
    direction=tuple(end[k]-start[k] for k in range(3))
    length=math.sqrt(sum(v*v for v in direction))
    leaf=ball(1,center=mid,color=color)
    leaf.resize((width,.022,length*.52))
    # Orient the original long Z axis along the blade.
    dx,dy,dz=direction
    tilt=math.degrees(math.acos(max(-1,min(1,dz/length))))
    az=math.degrees(math.atan2(dy,dx))
    leaf.turn("y",tilt,pivot=mid)
    leaf.turn("z",az,pivot=mid)
    return leaf

palm=Asset("Foreground right palm")
px,py=4.72,-2.36
palm.include("dark_planter",rod(.42,length=.66,center=(px,py,.33),color=(.12,.17,.12)))
palm.include("planter_rim",rod(.45,length=.075,center=(px,py,.66),color=(.17,.22,.16)))
for i in range(9):
    az=i*2.399
    height=1.9+(i%4)*.24
    tip=(px+math.cos(az)*.78,py+math.sin(az)*.58,height)
    base=(px,py,.60)
    palm.include("arching_stem_%d"%i,rod(.018,start=base,end=tip,color=(.14,.21,.13)))
    # Long frond rachis with paired tapered leaflets.
    outward=(math.cos(az),math.sin(az))
    root=(tip[0]-.30*outward[0],tip[1]-.30*outward[1],tip[2]-.33)
    end=(tip[0]+.48*outward[0],tip[1]+.48*outward[1],tip[2]+.20)
    palm.include("frond_axis_%d"%i,rod(.012,start=root,end=end,color=(.10,.18,.10)))
    for j in range(4):
        t=.18+j*.19
        center=tuple(root[k]*(1-t)+end[k]*t for k in range(3))
        span=.40*(1-t)+.10
        for side in (-1,1):
            endpoint=(center[0]+side*(-outward[1])*span+outward[0]*.14,
                      center[1]+side*outward[0]*span+outward[1]*.14,
                      center[2]+.13)
            palm.include("leaf_%d_%d_%d"%(i,j,side),
                         leaf_blade("",center,endpoint,.047,(.095,.16,.09)))
scene.include("right_palm",palm)

divider=Asset("Rear leafy divider")
divider.include("rectangular_planter",box((3.3,.52,.43),center=(-1.0,5.35,.55),color=(.30,.36,.29)))
for i in range(18):
    x=-2.5+i*.18
    h=random.uniform(.35,.70)
    divider.include("foliage_%02d"%i,
                    ball(random.uniform(.15,.23),center=(x,5.35,1.0+h*.45),color=(.32,.41,.30)))
    divider.include("sprig_%02d"%i,
                    rod(.012,start=(x,5.35,.72),end=(x+.08,5.35,1.0+h),color=(.25,.34,.23)))
scene.include("rear_plants",divider)

# Small tabletop objects visible as pale dots and dark accents.
accessories=Asset("Tabletop accessories")
for i,(x,y) in enumerate(((2.1,-1.35),(.4,1.05),(3.33,1.35),(.05,3.61),(3.15,4.16),(-3.5,.5))):
    accessories.include("saucer_%d"%i,rod(.105,length=.018,center=(x,y,.951),color=(.87,.88,.82)))
    accessories.include("small_cup_%d"%i,rod(.045,length=.080,center=(x,y,.996),color=(.79,.82,.75)))
scene.include("accessories",accessories)

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
background.inputs["Color"].default_value=(.82,.85,.79,1)
background.inputs["Strength"].default_value=.65

# Bright overcast window lighting, subdued foreground, near-level photograph.
set_view((-.25,-7.35,2.52),(.25,4.2,2.10),lens=29,sensor=36)
area_emitter((0,7.35,3.1),power=1700,size=8,target=(0,0,1),color=(.94,.97,.91))
area_emitter((5.4,1.0,3.0),power=1300,size=7,target=(-1,1,1),color=(.94,.97,.91))
area_emitter((-2,-3,4.12),power=250,size=5,target=(0,1,0),color=(.91,.94,.88))

# Shared matte finishes; metallic stems retain restrained reflections.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value=.68
sc.render.image_settings.color_mode='RGB'
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.35
sc.view_settings.gamma=1.0
