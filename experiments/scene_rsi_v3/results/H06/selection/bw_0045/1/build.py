# Reference inventory, normalized coordinates (x right, y down):
# Foreground cow: (.35,.36)-(.84,.86), pale barrel, irregular black flank
# markings, dark head, pale muzzle, folded legs and tail. Other reclining cows
# overlap to the left and behind it; some legs and heads are hidden.
# Steel dividers: (.00,.15)-(1.00,.83), rounded loops around the cows, with
# uprights and long rails. Concrete curb runs from approximately (0,.54) to
# (.72,1); brown aisle occupies the lower-left corner.
# Background: pale paneled wall above gray concrete, dark blue door near
# (.32,.04)-(.43,.20), blue columns, partly cropped worker at right.
# Wall edges are nearly horizontal; curb descends to the right; repeated
# stalls recede toward the left. Hidden stall ends and the precise cow count
# are uncertain.
#
# Comparison with second render:
# The door appeared around (.15,.24)-(.26,.52), below and left of the
# reference. The worker appeared around (.64,.19)-(.69,.45), rather than
# being cropped on the right. The cows were cropped at the bottom and read
# mainly as rounded backs, while the reference shows large side silhouettes.
# The bed curb and brown aisle were mostly absent. The reference rail loops
# overlap the cows with open gaps; the rendered rails formed a strong overhead
# grid. The wall covered the upper edge in both images.
# Largest discrepancies: (1) viewpoint and crop, (2) cow silhouettes and
# markings, (3) rail/curb overlap. Camera position is moved farther back,
# lowered and made more nearly perpendicular to the cow lengths; this should
# bring the foreground cow and curb into frame and show more of the flanks.
# Door and worker are moved independently along the wall toward their
# reference positions. Their vertical coordinates remain fixed.
# Flat procedural markings replace raised patch ellipsoids, which produced
# conspicuous round spots. These changes preserve separate editable cow parts.
#
# Estimated expanded primitives: architecture ~28, 10 dividers with 9-point
# sweeps 170 plus 13 posts/rails, 7 cows ~98, worker 7, wear 20; total ~336.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Modern dairy barn")

# Camera, equipment and building parameters are independent.
BASE_POS = (-3.7, -8.6, 3.7)
BASE_TARGET = (.1, .35, 1.18)
BASE_LENS = 44
CAM_POS = (-3.8, -13.5, 3.0)
CAM_TARGET = (.15, -.25, 1.25)
CAM_LENS = 48
WALL_Y = 5.6
BED_X0, BED_X1 = -2.10, 3.30
BED_Y0, BED_Y1 = -8.0, 5.0
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

architecture = Asset("Barn architecture")
architecture.include("aisle", box((30,30,.12), center=(0,0,-.10),
                                  color=(.29,.27,.20)))
architecture.include("raised_bed", box(
    (BED_X1-BED_X0,BED_Y1-BED_Y0,.22),
    center=((BED_X0+BED_X1)/2,(BED_Y0+BED_Y1)/2,.01), color=bed_color))
architecture.include("bed_curb", box((.16,BED_Y1-BED_Y0,.25),
    center=(BED_X0,(BED_Y0+BED_Y1)/2,.04), color=concrete))
architecture.include("lower_concrete_wall", box((30,.18,1.30),
    center=(0,WALL_Y,.65), color=wall_color))
architecture.include("upper_wall_panels", box((30,.18,4.0),
    center=(0,WALL_Y,3.30), color=panel_color))
for i,x in enumerate((-8,-4.2,-.5,3.25,7.0)):
    architecture.include("blue_post_%d"%i, box((.15,.20,5.3),
        center=(x,WALL_Y-.12,2.65), color=blue))
for i,x in enumerate((-7,-6,-5,-3.2,-2.2,-1.2,.5,1.5,2.5,4.3,5.3,6.3)):
    architecture.include("panel_seam_%d"%i, box((.018,.025,4.0),
        center=(x,WALL_Y-.105,3.30), color=(.62,.64,.64)))

# Door translation: rightward on the wall; top and base move together.
DOOR_X = -.15
architecture.include("door_frame", box((1.25,.12,1.80),
    center=(DOOR_X,WALL_Y-.13,.90),color=blue))
architecture.include("door_leaf", box((1.08,.035,1.58),
    center=(DOOR_X,WALL_Y-.205,.84),color=(.025,.065,.15)))
architecture.include("door_crossbar", box((1.08,.035,.045),
    center=(DOOR_X,WALL_Y-.23,.84),color=(.07,.12,.21)))
architecture.include("door_joint", box((.035,.035,1.58),
    center=(DOOR_X,WALL_Y-.23,.84),color=(.06,.11,.20)))
scene.include("barn", architecture)

stalls = Asset("Galvanized steel freestall equipment")
for i in range(10):
    y = -4.65 + i*SPACING
    divider = Asset("Stall divider %02d"%i)
    divider.include("curved_loop", sweep_tube(points=[
        (2.55,y,.15),(2.55,y,1.30),(2.45,y,1.40),
        (.40,y,1.40),(-.92,y,1.37),(-1.19,y,1.28),
        (-1.22,y,1.05),(-1.10,y,.96),(.45,y,.87)],
        radius=.035,color=steel))
    divider.include("support_post",rod(.038,start=(2.55,y,.13),
        end=(2.55,y,1.40),color=steel))
    stalls.include("divider_%02d"%i,divider)
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
    E("folded_hind_leg",-1.00,-.34,.18,.49,.17,.14,body)
    E("folded_foreleg",.38,-.34,.17,.53,.15,.12,body)
    E("hoof",.79,-.34,.17,.14,.14,.08,(.20,.19,.17))
    E("udder",-.78,-.19,.18,.29,.20,.15,pink)
    E("eye",1.38,-.235,.60,.035,.025,.035,(.008,.008,.007))
    p1=(xoff-1.42*scale,y-.08*scale,.12+.39*scale)
    p2=(xoff-1.62*scale,y-.24*scale,.12+.08*scale)
    cow.include("tail",rod(.035*scale,start=p1,end=p2,color=(.25,.22,.18)))
    scene.include(name,cow)

cow_asset("Foreground Holstein",-3.63,0,1.05)
cow_asset("Second dark Holstein",-2.60,-.18,1.00,True)
cow_asset("Third Holstein",-1.57,-.27,.98)
cow_asset("Fourth Holstein",-.54,-.27,.96)
cow_asset("Fifth Holstein",.49,-.24,.94)
cow_asset("Sixth Holstein",1.52,-.28,.91)
cow_asset("Distant Holstein",2.55,-.30,.88)

wear=Asset("Sparse bedding")
for i in range(20):
    x=-1.90+((i*37)%48)/10
    y=-4.30+((i*31)%85)/10
    wear.include("straw_%02d"%i,box((.13,.027,.009),
        center=(x,y,.128),color=(.47,.43,.32)))
scene.include("bedding",wear)

WORKER_X = 6.6
worker=Asset("Worker at rear")
worker.include("torso",box((.40,.24,.65),
    center=(WORKER_X,5.18,1.18),color=(.08,.20,.35)))
worker.include("head",ellipsoid((WORKER_X,5.18,1.72),
    (.15,.14,.18),(.45,.30,.23)))
worker.include("hair",ellipsoid((WORKER_X,5.18,1.83),
    (.15,.14,.075),(.08,.07,.06)))
for label,dx in (("left",-.12),("right",.12)):
    worker.include(label+"_leg",rod(.075,start=(WORKER_X+dx,5.18,.87),
        end=(WORKER_X+dx,5.18,.17),color=(.09,.13,.18)))
worker.include("left_arm",rod(.07,start=(WORKER_X-.19,5.18,1.42),
    end=(WORKER_X-.35,5.08,1.04),color=(.08,.20,.35)))
worker.include("right_arm",rod(.07,start=(WORKER_X+.19,5.18,1.42),
    end=(WORKER_X+.30,5.08,1.06),color=(.08,.20,.35)))
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

# Numerical checks use points on actual geometry. Reference estimates are
# separate from projections; the curb's image-border crossing is not a corner.
# For the door, baseline and final points differ by its actual translation.
anchors=[
    ("door upper left",(-2.025,5.37,1.80),
     (DOOR_X-.625,5.37,1.80),(.32,.04)),
    ("cow muzzle",(1.77,-3.68,.60),(1.77,-3.68,.60),(.82,.54)),
    ("wall junction",(-.5,5.48,1.30),(-.5,5.48,1.30),(.50,.21)),
    ("cow rump",(-1.67,-3.63,.58),(-1.67,-3.63,.58),(.37,.66)),
]
def project_points(label, points):
    bpy.context.view_layer.update()
    cam=sc.camera
    dg=bpy.context.evaluated_depsgraph_get()
    matrix=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    values=[]
    print(label)
    for (name,old,new,ref),point in zip(anchors,points):
        clip=matrix @ cam.matrix_world.inverted() @ Vector((*point,1))
        uv=None if clip.w<=1e-8 else (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        values.append(uv)
        print(name,"reference",ref,"projected",
              None if uv is None else tuple(round(v,3) for v in uv))
    return values

set_view(BASE_POS,BASE_TARGET,lens=BASE_LENS,sensor=36)
baseline=project_points("Baseline", [a[1] for a in anchors])
set_view(CAM_POS,(CAM_TARGET[0],CAM_TARGET[1],CAM_TARGET[2]+.10),
         lens=CAM_LENS,sensor=36)
project_points("Small upward aim trial", [a[2] for a in anchors])
set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS,sensor=36)
final=project_points("Proposed final", [a[2] for a in anchors])
for i,(name,old,new,ref) in enumerate(anchors):
    if baseline[i] is not None and final[i] is not None:
        b=math.dist(baseline[i],ref)
        f=math.dist(final[i],ref)
        print(name,"baseline error",round(b,3),"final error",round(f,3),
              "improved" if f<b else "worsened")

area_emitter((0,-1,7),power=1600,size=8,target=(0,0,0),color=(.82,.90,1))
area_emitter((-4,3,5),power=650,size=6,target=(0,0,1),color=(.90,.94,1))

# Procedural coat markings are part of the surface, rather than raised blobs.
# The shared material remains editable in Blender.
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
    elif abs(c[0]-white[0])<.015 and abs(c[1]-white[1])<.015:
        nt=mat.node_tree
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=3.3
        tex.inputs["Detail"].default_value=2.0
        tex.inputs["Roughness"].default_value=.7
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.43
        ramp.color_ramp.elements[0].color=(.018,.021,.019,1)
        ramp.color_ramp.elements[1].position=.48
        ramp.color_ramp.elements[1].color=(.76,.74,.67,1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value=.86
    elif abs(c[0]-.16)<.015 and abs(c[1]-.15)<.015:
        bsdf.inputs["Roughness"].default_value=.20
    else:
        bsdf.inputs["Roughness"].default_value=.80
