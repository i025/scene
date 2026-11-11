# Reference inventory and comparison with the first render:
# - Background wall: reference fills the entire upper edge; wall junction is
#   near y=.11-.22. Previous render had a large empty gray area above the wall
#   and the junction around y=.30-.48.
# - Blue door: reference bounds approximately (.32,.04)-(.43,.20); previous
#   render bounds approximately (.54,.30)-(.61,.45).
# - Foreground cow: reference approximately (.35,.36)-(.84,.85); previous
#   render approximately (.25,.59)-(.48,.78), partly obscured by the end rail.
# - Front curb: reference enters left edge around y=.54 and exits bottom near
#   x=.72; previous render enclosed a small island, with a visible near corner.
# - Rail loops: reference fill the width, overlap the cows, and recede left;
#   previous render shows a small rectangular array receding to the right.
# - Worker: reference is cropped at the right edge, around (.95,.12)-(1,.39);
#   previous render is fully visible around (.91,.37)-(.96,.59).
# Largest discrepancies: 1) framing and viewing direction; 2) cow size and
# side-on silhouette; 3) excessive empty floor and exposed bed perimeter.
# Camera correction: move to the side of the row and lower it; this makes the
# cows larger, sends their heads right, and makes the wall fill the upper image.
# Bed and wall are extended beyond the crop. Rail spacing and cow positions
# remain independent; uncertainty remains in hidden stall and wall geometry.
# Dominant reference edges: wall joints are nearly horizontal; the curb falls
# toward the right; the divider rails recede toward the left.
# Approximate expanded primitive count: architecture 20, 8 dividers * 15
# tube primitives plus supports and rails ~135, 7 cows * 18 ~126, worker 8,
# surface marks 18; approximately 310 total primitives.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Indoor dairy freestall barn")

# Camera and principal dimensions are independent.
CAM_POS = (-3.7, -8.6, 3.7)
CAM_TARGET = (0.1, 0.35, 1.18)
CAM_LENS = 44
BED_X0, BED_X1 = -2.10, 3.30
BED_Y0, BED_Y1 = -8.0, 5.0
WALL_Y = 5.6
SPACING = 1.03

steel = (.59, .63, .64)
concrete = (.46, .47, .46)
bed_color = (.50, .50, .47)
wall_color = (.43, .45, .45)
panel_color = (.77, .79, .79)
blue = (.025, .075, .18)
white = (.76, .74, .67)
black = (.025, .029, .027)
pink = (.48, .36, .34)
mud = (.28, .26, .20)

architecture = Asset("Barn architecture")
architecture.include("aisle", box((30, 30, .12), center=(0,0,-.10),
                                   color=(.29,.27,.20)))
architecture.include("raised_bed", box((BED_X1-BED_X0, BED_Y1-BED_Y0,.22),
    center=((BED_X0+BED_X1)/2,(BED_Y0+BED_Y1)/2,.01), color=bed_color))
architecture.include("bed_curb", box((.16,BED_Y1-BED_Y0,.25),
    center=(BED_X0,(BED_Y0+BED_Y1)/2,.04), color=concrete))
architecture.include("lower_concrete_wall", box((30,.18,1.30),
    center=(0,WALL_Y,.65), color=wall_color))
architecture.include("upper_wall", box((30,.18,4.0),
    center=(0,WALL_Y,3.30), color=panel_color))
for i,x in enumerate((-8,-4.2,-.5,3.25,7.0)):
    architecture.include("blue_structural_post_%d"%i,
        box((.15,.20,5.3),center=(x,WALL_Y-.12,2.65),color=blue))
for i,x in enumerate((-7,-6,-5,-3.2,-2.2,-1.2,.5,1.5,2.5,4.3,5.3,6.3)):
    architecture.include("wall_panel_seam_%d"%i,
        box((.018,.025,4.0),center=(x,WALL_Y-.105,3.30),
            color=(.62,.64,.64)))
architecture.include("door_frame", box((1.25,.12,1.80),
    center=(-1.40,WALL_Y-.13,.90),color=blue))
architecture.include("door_leaf", box((1.08,.035,1.58),
    center=(-1.40,WALL_Y-.205,.84),color=(.025,.065,.15)))
architecture.include("door_middle_rail", box((1.08,.035,.045),
    center=(-1.40,WALL_Y-.23,.84),color=(.07,.12,.21)))
architecture.include("door_vertical_joint", box((.035,.035,1.58),
    center=(-1.40,WALL_Y-.23,.84),color=(.06,.11,.20)))
scene.include("barn",architecture)

stalls = Asset("Galvanized steel freestall equipment")
# Loops extend along the animals; the rounded open ends face the aisle.
for i in range(10):
    y = -4.65 + i*SPACING
    div = Asset("Divider %02d"%i)
    div.include("bent_loop", sweep_tube(points=[
        (2.55,y,.15),(2.55,y,1.30),(2.45,y,1.40),
        (.40,y,1.40),(-.92,y,1.37),(-1.19,y,1.28),
        (-1.22,y,1.05),(-1.10,y,.96),(.45,y,.87)],
        radius=.035,color=steel))
    div.include("support_post",rod(.038,start=(2.55,y,.13),
                                   end=(2.55,y,1.40),color=steel))
    stalls.include("divider_%02d"%i,div)
for i,(x,z) in enumerate(((2.53,1.36),(2.34,.76),(-.80,1.38))):
    stalls.include("long_rail_%d"%i,rod(.032,start=(x,-5.2,z),
                                      end=(x,5.0,z),color=steel))
scene.include("stall_equipment",stalls)

def ellipsoid(center, scale, color):
    obj=ball(1,center=center,color=color)
    obj.resize(scale,pivot=center)
    return obj

def cow_asset(name,y,xoff,scale,mostly_dark=False):
    cow=Asset(name)
    def E(label,x,y0,z,sx,sy,sz,col):
        p=(xoff+x*scale,y+y0*scale,.12+z*scale)
        cow.include(label,ellipsoid(p,(sx*scale,sy*scale,sz*scale),col))
    body = black if mostly_dark else white
    E("barrel",-.34,0,.53,1.04,.48,.48,body)
    E("rump",-1.12,0,.44,.48,.46,.40,body)
    E("shoulder",.40,0,.54,.50,.43,.43,body)
    E("neck",.87,0,.52,.55,.32,.30,black)
    E("head",1.27,-.02,.53,.38,.24,.25,black)
    E("muzzle",1.57,-.04,.45,.19,.20,.13,pink)
    E("wet_nose",1.69,-.05,.46,.09,.16,.085,(.16,.15,.14))
    E("near_ear",1.13,-.27,.72,.21,.10,.07,black)
    E("far_ear",1.13,.24,.72,.20,.09,.07,black)
    E("hind_leg_folded",-1.00,-.34,.18,.49,.17,.14,body)
    E("foreleg_folded",.38,-.34,.17,.53,.15,.12,body)
    E("hoof",.79,-.34,.17,.14,.14,.08,(.20,.19,.17))
    E("udder",-.78,-.19,.18,.29,.20,.15,pink)
    E("eye",1.38,-.235,.60,.035,.025,.035,(.008,.008,.007))
    if not mostly_dark:
        # Broad flank marks and a dark neck create the dominant light/dark areas.
        for j,(x,y0,z,sx,sy,sz) in enumerate((
            (-.83,-.41,.60,.34,.09,.25),
            (-.30,-.45,.66,.23,.07,.22),
            (.07,-.40,.75,.19,.08,.19),
            (.28,-.27,.89,.22,.13,.10),
            (-.32,.00,.98,.35,.23,.055),
            (-1.12,-.10,.77,.31,.27,.10))):
            E("coat_patch_%d"%j,x,y0,z,sx,sy,sz,black)
    else:
        E("pale_flank",-1.20,-.37,.35,.25,.10,.16,(.47,.43,.35))
    # A thin trailing tail is visible against the bed edge.
    p1=(xoff-1.42*scale,y-.08*scale,.12+.39*scale)
    p2=(xoff-1.62*scale,y-.24*scale,.12+.08*scale)
    cow.include("tail",rod(.035*scale,start=p1,end=p2,color=(.25,.22,.18)))
    scene.include(name,cow)

cow_asset("Foreground Holstein",-3.63,.0,1.05)
cow_asset("Second dark Holstein",-2.60,-.18,1.00,True)
cow_asset("Third Holstein",-1.57,-.27,.98)
cow_asset("Fourth Holstein",-.54,-.27,.96)
cow_asset("Fifth Holstein",.49,-.24,.94)
cow_asset("Sixth Holstein",1.52,-.28,.91)
cow_asset("Distant Holstein",2.55,-.30,.88)

wear=Asset("Sparse bedding and surface wear")
for i in range(18):
    x=-1.90+((i*37)%48)/10
    y=-4.30+((i*31)%85)/10
    wear.include("bedding_%02d"%i,box((.13,.027,.009),
        center=(x,y,.128),color=(.47,.43,.32)))
scene.include("bed_wear",wear)

worker=Asset("Worker at rear of barn")
worker.include("torso",box((.40,.24,.65),center=(4.35,5.18,1.18),
                           color=(.08,.20,.35)))
worker.include("head",ellipsoid((4.35,5.18,1.72),(.15,.14,.18),(.45,.30,.23)))
worker.include("hair",ellipsoid((4.35,5.18,1.83),(.15,.14,.075),(.08,.07,.06)))
for label,x in (("left",4.23),("right",4.47)):
    worker.include(label+"_leg",rod(.075,start=(x,5.18,.87),
                                    end=(x,5.18,.17),color=(.09,.13,.18)))
worker.include("left_arm",rod(.07,start=(4.16,5.18,1.42),
                              end=(4.00,5.08,1.04),color=(.08,.20,.35)))
worker.include("right_arm",rod(.07,start=(4.54,5.18,1.42),
                               end=(4.65,5.08,1.06),color=(.08,.20,.35)))
scene.include("worker",worker)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get("Background")
if background is None:
    background=nodes.new("ShaderNodeBackground")
output=nodes.get("World Output")
if output is None:
    output=nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.69,.74,.79,1)
background.inputs["Strength"].default_value=.60

sc.render.resolution_x=512
sc.render.resolution_y=285
sc.render.resolution_percentage=100

# Compare the previous camera, a small trial, and the proposed camera. These
# are projections of explicit geometry points, not measurements of silhouettes.
# Reference correspondences are approximate; the curb is cropped, so its
# image-border intersection is not treated as a physical corner.
anchors=[
    ("door upper left",(-2.025,5.37,1.80),(.32,.04)),
    ("foreground cow muzzle",(1.77,-3.68,.60),(.82,.54)),
    ("foreground divider bend",(-1.22,-4.65,1.28),(.61,.28)),
    ("wall junction at post",(-.5,5.48,1.30),(.50,.21)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    matrix=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    vals=[]
    print(label)
    for name,point,ref in anchors:
        clip=matrix @ cam.matrix_world.inverted() @ Vector((*point,1))
        uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        vals.append(uv)
        print(name,"reference",ref,"projected",
              None if uv is None else tuple(round(v,3) for v in uv))
    return vals

set_view((8.1,-11.8,5.4),(0,.3,1.15),lens=42,sensor=36)
baseline=projection_table("Previous camera on revised geometry")
set_view(CAM_POS,(CAM_TARGET[0],CAM_TARGET[1],CAM_TARGET[2]+.10),
         lens=CAM_LENS,sensor=36)
trial=projection_table("Small upward aim trial")
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
final=projection_table("Final camera")
for i,(name,point,ref) in enumerate(anchors):
    if baseline[i] is not None and final[i] is not None:
        old=math.dist(baseline[i],ref)
        new=math.dist(final[i],ref)
        print(name,"baseline error",round(old,3),"final error",round(new,3),
              "improved" if new<old else "worsened")
# Geometry changes extend the bed and wall beyond the crop; these do not move
# the door or cow points used above. The wall extension protects the background
# coverage, while the camera change is needed to make the foreground side-on.

area_emitter((0,-1,7),power=1600,size=8,target=(0,0,0),color=(.82,.90,1))
area_emitter((-4,3,5),power=650,size=6,target=(0,0,1),color=(.90,.94,1))
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf=mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c=bsdf.inputs["Base Color"].default_value
    if abs(c[0]-steel[0])<.02 and abs(c[1]-steel[1])<.02:
        bsdf.inputs["Metallic"].default_value=.75
        bsdf.inputs["Roughness"].default_value=.27
    elif abs(c[0]-.16)<.015 and abs(c[1]-.15)<.015:
        bsdf.inputs["Roughness"].default_value=.20
    else:
        bsdf.inputs["Roughness"].default_value=.80
