from sceneact import *
import bpy
import math
import random

# Reference inventory (estimated normalized image bounds):
# Pale narrow-plank ceiling: (0,0)-(1,.32), with small ceiling roses.
# Rear windows: (0,.30)-(.68,.56); right windows: (.65,.27)-(1,.61).
# Dark mullions and low horizontal rails surround bright outdoor foliage.
# Dark narrow rectangular floor tiles: (.25,.57)-(1,1).
# Left booth backs: (0,.52)-(.33,.89); foreground tabletop: (0,.86)-(.46,1).
# Center/right tables and slab-backed pedestal chairs: (.34,.52)-(.88,1).
# Large near pendant: (.02,.12)-(.23,.36), neck and long suspension above.
# Nine smaller pendants recede across the image at approximately y=.35-.43.
# Right palm: (.78,.40)-(1,1), with long divided fronds and open gaps.
# Low rear planter: (.31,.49)-(.59,.59). Small cups sit on several tables.
# Occluded supports and distant outdoor details remain uncertain.
#
# Feedback comparison:
# The nearest pendant and palm were outside the first camera framing.
# Left booth ends were too far left; the nearest right chair was too far right.
# Exterior surfaces looked like solid gray walls and furniture lacked contrast.
# Keep the existing semantic furniture hierarchy while correcting these locations,
# bringing the right window corner left, and making the exterior luminous.
#
# Expanded primitive estimate: architecture 115, exterior 27,
# eleven tables 55, fifteen chairs 75, five booths 25,
# ten pendants 90 including cutters, palm 122, rear plants 37,
# accessories 12; approximately 660 primitives. No fillet boxes.
# Each pendant uses one Boolean cut; leaves use single scaled balls.

random.seed(12)
scene = Scene("Windowed cafeteria revised")

CEILING = (.84,.85,.82)
WHITE = (.75,.77,.73)
FRAME = (.14,.17,.15)
METAL = (.53,.56,.53)
DARK = (.025,.034,.027)
UPHOL = (.20,.235,.21)
FLOOR = (.14,.17,.15)

architecture = Asset("Architecture")
architecture.include("tiled_floor",
    box((12,17,.12), center=(0,1,-.08), color=FLOOR))
architecture.include("pale_ceiling",
    box((12,17,.14), center=(0,1,4.35), color=CEILING))
for j in range(48):
    architecture.include("ceiling_plank_joint_%02d" % j,
        box((11.9,.010,.008), center=(0,-6.8+j*.32,4.273),
            color=(.58,.60,.56)))
for i in range(25):
    architecture.include("floor_long_joint_%02d" % i,
        box((.009,16,.004), center=(-5.8+i*.48,1,.001),
            color=(.30,.33,.30)))
for j in range(14):
    architecture.include("floor_cross_joint_%02d" % j,
        box((12,.009,.004), center=(0,-6+j*1.15,.002),
            color=(.26,.29,.26)))

RIGHT_WALL = 4.25
architecture.include("rear_low_wall",
    box((12,.20,.66), center=(0,8,.33), color=(.66,.69,.64)))
architecture.include("rear_header",
    box((12,.20,.22), center=(0,8,4.13), color=WHITE))
for z in (.78,1.12,3.98):
    architecture.include("rear_rail_"+str(z),
        box((12,.13,.065), center=(0,7.93,z), color=FRAME))
for i,x in enumerate((-5.8,-4,-2,0,2,RIGHT_WALL)):
    architecture.include("rear_mullion_%d" % i,
        box((.075,.13,3.24), center=(x,7.93,2.42), color=FRAME))
architecture.include("right_low_wall",
    box((.18,16,.68), center=(RIGHT_WALL,.1,.34),
        color=(.68,.71,.66)))
architecture.include("right_header",
    box((.18,16,.20), center=(RIGHT_WALL,.1,4.12), color=WHITE))
for z in (.80,1.13,4.0):
    architecture.include("right_rail_"+str(z),
        box((.13,16,.065), center=(RIGHT_WALL-.07,.1,z), color=FRAME))
for i,y in enumerate((-5,-2,1,4,7.9)):
    architecture.include("right_mullion_%d" % i,
        box((.10,.07,3.23), center=(RIGHT_WALL-.07,y,2.42), color=FRAME))
architecture.include("left_wall",
    box((.15,16,4.3), center=(-5.95,.1,2.1), color=(.74,.76,.72)))
scene.include("architecture", architecture)

outside = Asset("Bright exterior")
EXTERIOR = (.96,.975,.95)
outside.include("rear_daylight_backdrop",
    box((25,.10,8), center=(0,11,3), color=EXTERIOR))
outside.include("side_daylight_backdrop",
    box((.10,24,8), center=(7,1,3), color=EXTERIOR))
outside.include("outdoor_ground",
    box((25,18,.10), center=(0,12,-.12), color=(.77,.80,.74)))
for i in range(12):
    x = random.uniform(-9,9)
    y = random.uniform(9.4,10.3)
    z = random.uniform(1.3,2.6)
    outside.include("tree_trunk_%d" % i,
        rod(.035, start=(x,y,.1), end=(x,y,z), color=(.45,.49,.43)))
    canopy = ball(random.uniform(.6,1.05),
                  center=(x,y,z+.5), color=(.61,.66,.58))
    canopy.resize((1,.7,1))
    outside.include("tree_canopy_%d" % i, canopy)
scene.include("exterior", outside)

def table(name,x,y,w=1.55,d=.85):
    a = Asset(name)
    a.include("dark_laminate_edge",
        box((w,d,.065), center=(x,y,.87), color=(.10,.13,.11)))
    a.include("pale_laminate_surface",
        box((w-.018,d-.018,.035), center=(x,y,.921),
            color=(.72,.75,.70)))
    a.include("chrome_pedestal",
        rod(.052,start=(x,y,.10),end=(x,y,.85),color=METAL))
    a.include("foot_cross_x",
        box((.70,.075,.045),center=(x,y,.055),color=METAL))
    a.include("foot_cross_y",
        box((.075,.54,.045),center=(x,y,.055),color=METAL))
    scene.include(name,a)

def chair(name,x,y,angle=0):
    a = Asset(name)
    a.include("padded_seat",
        box((.76,.69,.13),center=(x,y,.58),color=UPHOL))
    a.include("broad_padded_back",
        box((.78,.095,.88),center=(x,y+.31,1.01),color=UPHOL))
    a.include("top_piping",
        box((.79,.10,.025),center=(x,y+.31,1.455),
            color=(.36,.40,.35)))
    a.include("chrome_stem",
        rod(.065,start=(x,y,.09),end=(x,y,.54),
            color=(.62,.65,.61)))
    a.include("circular_chrome_base",
        rod(.27,length=.065,center=(x,y,.055),color=(.62,.65,.61)))
    a.turn("z",angle,pivot=(x,y,0))
    scene.include(name,a)

def bench(name,x,y,width=2.7):
    a = Asset(name)
    a.include("upholstered_seat",
        box((width,.71,.20),center=(x,y,.56),color=UPHOL))
    a.include("broad_back",
        box((width,.16,.95),center=(x,y+.34,.99),
            color=(.19,.23,.20)))
    a.include("top_piping",
        box((width,.18,.025),center=(x,y+.34,1.48),
            color=(.37,.41,.36)))
    for k,dx in enumerate((-width*.36,width*.36)):
        a.include("support_%d" % k,
            box((.12,.46,.43),center=(x+dx,y,.25),
                color=(.24,.28,.24)))
    scene.include(name,a)

table("foreground_left_table",-2.3,-3.55,3.0,1.55)
for i,y in enumerate((-3.1,-.9,1.25,3.4,5.5)):
    bench("left_booth_%d" % i,-2.75,y,2.9)
    if i > 0:
        table("left_booth_table_%d" % i,-2.75,y-.75,2.75,1.05)

table("front_right_table",1.55,-1.25,1.85,1.05)
chair("front_right_near_seat",1.88,-2.28,0)
chair("front_right_left_seat",.38,-1.32,90)
chair("front_right_far_seat",2.03,-.26,180)

table("middle_table",.15,1.05,1.65,.98)
chair("middle_near_seat",-.05,.08,0)
chair("middle_left_seat",-1.05,1.10,90)
chair("middle_far_seat",.23,2.0,180)

table("right_middle_table",2.92,1.35,1.62,.98)
chair("right_middle_near_seat",2.84,.39,0)
chair("right_middle_left_seat",1.79,1.38,90)
chair("right_middle_far_seat",2.94,2.29,180)

table("rear_center_table",-.05,3.61,1.65,.9)
chair("rear_center_near_seat",-.05,2.75,0)
chair("rear_center_left_seat",-1.15,3.62,90)
chair("rear_center_far_seat",.02,4.48,180)

table("rear_right_table",2.8,4.16,1.7,.95)
chair("rear_right_near_seat",2.82,3.24,0)
chair("rear_right_left_seat",1.63,4.14,90)
chair("rear_right_far_seat",2.8,5.06,180)

def pendant(name,x,y,bottom,radius):
    a = Asset(name)
    dome_center = bottom+.035
    dome = ball(radius,center=(x,y,dome_center),color=DARK)
    dome.resize((1,1,.72))
    cutter = box((radius*2.5,radius*2.5,radius*1.5),
        center=(x,y,dome_center-radius*.75),color=DARK)
    a.include("flared_metal_shade",subtract(dome,cutter))
    a.include("shade_lip",
        rod(radius,length=.028,center=(x,y,bottom+.025),color=DARK))
    a.include("white_inner_reflector",
        rod(radius*.93,length=.012,center=(x,y,bottom+.005),
            color=(.91,.92,.86)))
    neckbottom = bottom+radius*.50
    necktop = bottom+radius*1.20
    a.include("tall_cylindrical_neck",
        rod(radius*.34,start=(x,y,neckbottom),
            end=(x,y,necktop),color=DARK))
    for k,t in enumerate((.13,.25)):
        a.include("neck_band_%d" % k,
            rod(radius*.345,length=.026,
                center=(x,y,necktop-t*radius),
                color=(.37,.41,.35)))
    a.include("suspension_wire",
        rod(.008,start=(x,y,necktop),end=(x,y,4.27),
            color=(.16,.20,.16)))
    a.include("ceiling_rose",
        rod(.075,length=.025,center=(x,y,4.255),color=DARK))
    scene.include(name,a)

pendant("large_foreground_pendant",-2.05,-2.6,3.00,.67)
pendant("left_second_pendant",-3.30,.15,2.94,.42)
pendant("left_third_pendant",-3.30,3.0,2.98,.30)
pendant("left_rear_pendant",-3.30,5.85,2.99,.23)
pendant("center_rear_pendant",-.90,5.8,2.99,.26)
pendant("center_pendant",1.0,2.53,3.04,.35)
pendant("center_distant_pendant",1.0,6.7,3.02,.22)
pendant("right_large_pendant",2.45,.12,3.10,.42)
pendant("right_middle_pendant",3.75,3.47,3.02,.28)
pendant("right_rear_pendant",3.85,6.5,3.03,.24)

def leaf_blade(start,end,width,color):
    mid = tuple((start[k]+end[k])*.5 for k in range(3))
    dx,dy,dz = (end[k]-start[k] for k in range(3))
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    leaf = ball(1,center=mid,color=color)
    leaf.resize((width,.018,length*.52))
    tilt = math.degrees(math.acos(max(-1,min(1,dz/length))))
    azimuth = math.degrees(math.atan2(dy,dx))
    leaf.turn("y",tilt,pivot=mid)
    leaf.turn("z",azimuth,pivot=mid)
    return leaf

palm = Asset("Foreground right palm")
px,py = 2.94,-1.65
palm.include("dark_planter",
    rod(.36,length=.60,center=(px,py,.30),color=(.07,.10,.07)))
palm.include("planter_rim",
    rod(.39,length=.065,center=(px,py,.60),color=(.11,.15,.10)))
for i in range(10):
    az = i*2.399
    outward = (math.cos(az),math.sin(az))
    height = 1.95+(i%4)*.23
    root = (px+outward[0]*.10,py+outward[1]*.10,.62)
    bend = (px+outward[0]*.42,py+outward[1]*.42,height-.20)
    end = (px+outward[0]*1.00,py+outward[1]*.83,height+.18)
    palm.include("stem_%d" % i,
        rod(.014,start=root,end=bend,color=(.075,.13,.07)))
    palm.include("frond_rachis_%d" % i,
        rod(.010,start=bend,end=end,color=(.075,.13,.07)))
    for j in range(5):
        t = .08+j*.18
        center = tuple(bend[k]*(1-t)+end[k]*t for k in range(3))
        span = .43*(1-t)+.09
        for side in (-1,1):
            endpoint = (
                center[0]-side*outward[1]*span+outward[0]*.21,
                center[1]+side*outward[0]*span+outward[1]*.21,
                center[2]+.06-.15*t)
            palm.include("leaf_%d_%d_%d" % (i,j,side),
                leaf_blade(center,endpoint,.033,(.045,.085,.043)))
scene.include("right_palm",palm)

divider = Asset("Rear leafy divider")
divider.include("rectangular_planter",
    box((3.3,.52,.43),center=(-1.0,5.35,.55),
        color=(.19,.25,.18)))
for i in range(18):
    x = -2.5+i*.18
    h = random.uniform(.35,.70)
    foliage = ball(random.uniform(.15,.23),
        center=(x,5.35,1.0+h*.45),color=(.20,.29,.18))
    foliage.resize((1,.8,1.2))
    divider.include("foliage_%02d" % i,foliage)
    divider.include("sprig_%02d" % i,
        rod(.012,start=(x,5.35,.72),end=(x+.08,5.35,1.0+h),
            color=(.15,.23,.13)))
scene.include("rear_plants",divider)

accessories = Asset("Tabletop accessories")
for i,(x,y) in enumerate(((1.55,-1.25),(.15,1.05),(2.92,1.35),
                         (-.05,3.61),(2.8,4.16),(-2.75,.5))):
    accessories.include("saucer_%d" % i,
        rod(.105,length=.018,center=(x,y,.951),
            color=(.86,.88,.81)))
    accessories.include("cup_%d" % i,
        rod(.045,length=.080,center=(x,y,.996),
            color=(.77,.80,.73)))
scene.include("accessories",accessories)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.88,.90,.85,1)
background.inputs["Strength"].default_value = .50

set_view((-.25,-7.35,2.52),(.25,4.2,2.10),lens=29,sensor=36)
area_emitter((0,7.4,3.1),power=2000,size=8,
             target=(0,0,1),color=(.97,.98,.94))
area_emitter((4.0,1.0,3.0),power=1500,size=7,
             target=(-1,1,1),color=(.97,.98,.94))
area_emitter((-2,-3,4.12),power=110,size=5,
             target=(0,1,0),color=(.95,.97,.92))

for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = .60
        c = bsdf.inputs["Base Color"].default_value
        # Only the specially colored exterior backdrops receive emission.
        if c[0] > .94 and c[1] > .96 and c[2] > .93:
            bsdf.inputs["Emission Color"].default_value = (.96,.975,.95,1)
            bsdf.inputs["Emission Strength"].default_value = 1.4

sc.render.image_settings.color_mode = 'RGB'
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .20
sc.view_settings.gamma = 1.0
