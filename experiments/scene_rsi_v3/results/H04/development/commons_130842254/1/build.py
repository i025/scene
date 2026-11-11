from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Visual inventory, normalized image coordinates, estimated from the photograph:
# Pale walls fill the upper image; the rear corner is near (.39,.03).
# The left cooking range spans (0,.27)-(.37,.51), with two dark openings,
# a dark counter, small vessels and a broad low stone arch behind it.
# The dark rear hearth spans approximately (.41,.22)-(.84,.46), with a
# stone arch, iron grate and partly obscured hanging vessels.
# The central chimney extends from finial (.51,.23) to base near (.50,.64);
# its pale tapered cap and shaft overlap the hearth and wooden worktable.
# The worktable occupies approximately (.18,.45)-(.72,.87), with diagonal
# edges, raised boards around the chimney, plates, bread, cloth and utensils.
# Large pale slabs occupy the foreground; darker small paving and baskets lie
# to the right. Individual items inside the hearth are partly occluded.
#
# Comparison with second render, approximate visible contours:
# - Finial: reference (.51,.23), render (.48,.25); this is reasonably close.
# - Rear arch: reference (.41,.22)-(.84,.46), render (.52,.25)-(.91,.48);
#   the left side is hidden by the chimney, and the right end extends too far.
# - Table: reference roughly (.18,.45)-(.72,.87), render (.18,.43)-(.70,.77);
#   both have diagonal edges and overlap the chimney, but the reference extends
#   farther downward and its top has more varied occupied areas and gaps.
# - Foreground: reference has irregular medium-dark stone and dark paving at
#   right; render has a very pale, regular grid and an untextured right strip.
# - Reference range extends off the left edge; render's range is shorter and
#   lighter. Both views crop room boundaries.
#
# Ranked corrections:
# 1. Darken and vary floor and furnishings and add darker right-hand paving.
#    This changes broad light/dark regions; lighting also affects brightness.
# 2. Extend the table toward the camera using TABLE_FRONT and lengthen its
#    legs. Its near contour should move down, while the chimney stays fixed.
# 3. Shift and slightly narrow the rear hearth using HEARTH_CX and HEARTH_RX;
#    its right spring moves left, preserving the chimney overlap.
# 4. Add cap seams and varied tabletop contents, preserving open gaps. The
#    photograph's cap is tapered with horizontal courses, not a smooth cone.
# Camera is retained: the finial and general crop already agree, whereas the
# hearth and table discrepancies differ locally. A small trial is still
# projected below and restored, with computed values separate from observations.
# Estimated expanded primitives: paving 150, architecture 60, range 35,
# table/chimney 30, tabletop objects 95, hearth accessories 25: about 395,
# plus one custom hood mesh. No fillet boxes or multi-point tubes are used.

random.seed(23)
scene = Scene("Historic kitchen")

CAM_POS = (7.5, -11.5, 12.0)
CAM_TARGET = (0.0, 0.35, 1.05)
CAM_LENS = 64
TABLE_W = 3.7
TABLE_FRONT = -2.38
TABLE_BACK = .82
HEARTH_CX = -.05
HEARTH_RX = 1.95

plaster = (.66,.68,.66)
stone = (.34,.32,.27)
dark = (.045,.043,.035)
wood = (.23,.12,.055)
wood_top = (.33,.19,.085)
iron = (.105,.10,.085)
cream = (.62,.60,.51)
ochre = (.43,.26,.10)

def put(asset, name, node):
    asset.include(name, node)
    return node

def cyl(asset, name, x, y, z, radius, height, color):
    return put(asset, name, rod(radius, start=(x,y,z),
                               end=(x,y,z+height), color=color))

# Irregular stone floor, cropped at every edge of the camera.
floor = Asset("floor_and_paving")
put(floor, "dark_floor_base",
    box((30,30,.12), center=(0,0,-.12), color=(.17,.18,.15)))
for i in range(13):
    for j in range(12):
        x = -4.15 + i*.65
        y = -4.6 + j*.65
        if x > 2.32:
            continue
        q = random.uniform(-.055,.045)
        put(floor, "stone_slab_%02d_%02d"%(i,j),
            box((.625,.625,.025), center=(x,y,-.045),
                color=(.32+q,.31+q,.26+q)))
# Small darker masonry courses along the right side.
for i in range(5):
    for j in range(15):
        x = 2.40 + i*.40 + (j%2)*.19
        y = -3.8 + j*.41
        q = random.uniform(-.025,.025)
        put(floor, "dark_paver_%02d_%02d"%(i,j),
            box((.38,.39,.018), center=(x,y,-.035),
                color=(.19+q,.19+q,.16+q)))
scene.include("floor", floor)

arch = Asset("rear_hearth_and_walls")
put(arch, "upper_plaster",
    box((30,.22,8),center=(0,3.70,6.4),color=plaster))
put(arch, "left_pier",
    box((12,.22,2.4),center=(HEARTH_CX-HEARTH_RX-6,3.70,1.2),
        color=plaster))
put(arch, "right_pier",
    box((12,.22,2.4),center=(HEARTH_CX+HEARTH_RX+6,3.70,1.2),
        color=plaster))
put(arch, "left_wall",
    box((.20,20,10),center=(-4.55,1,4.95),color=plaster))

arch_base, arch_rise = 1.30, 1.05
for i in range(16):
    x0=HEARTH_CX-HEARTH_RX+i*(2*HEARTH_RX/16)
    x1=HEARTH_CX-HEARTH_RX+(i+1)*(2*HEARTH_RX/16)
    xc=(x0+x1)/2
    u=(xc-HEARTH_CX)/HEARTH_RX
    top=arch_base+arch_rise*math.sqrt(max(0,1-u*u))
    put(arch, "dark_opening_%02d"%i,
        box((x1-x0+.01,.08,top),center=(xc,3.62,top/2),color=dark))
    put(arch, "plaster_above_opening_%02d"%i,
        box((x1-x0+.01,.20,2.43-top),
            center=(xc,3.70,(top+2.43)/2),color=plaster))
pts=[]
for i in range(13):
    t=math.pi-i*math.pi/12
    pts.append((HEARTH_CX+HEARTH_RX*math.cos(t),3.44,
                arch_base+arch_rise*math.sin(t)))
for i in range(12):
    put(arch,"arch_stone_%02d"%i,
        rod(.105,start=pts[i],end=pts[i+1],color=stone))
for x in (HEARTH_CX-HEARTH_RX,HEARTH_CX+HEARTH_RX):
    put(arch,"jamb_%s"%x,
        box((.22,.30,1.3),center=(x,3.49,.65),color=stone))
for z in (.32,.55,.78,1.01,1.24):
    put(arch,"grate_cross_%s"%z,
        rod(.025,start=(-.75,3.39,z),end=(1.1,3.39,z),color=iron))
for x in (-.70,-.15,.40,1.05):
    put(arch,"grate_vertical_%s"%x,
        rod(.025,start=(x,3.38,.24),end=(x,3.38,1.35),color=iron))
scene.include("architecture",arch)

# Range body and its visible openings and counter vessels.
rng=Asset("left_masonry_cooking_range")
put(rng,"body",box((4.0,.92,.79),center=(-3.05,2.55,.40),
                   color=(.56,.58,.54)))
put(rng,"counter",box((4.1,1.0,.09),center=(-3.05,2.55,.84),
                      color=(.20,.20,.17)))
for k,x in enumerate((-4.2,-3.05,-1.90)):
    put(rng,"oven_opening_%d"%k,
        box((.65,.035,.43),center=(x,2.075,.22),color=dark))
    b=ball(.325,center=(x,2.06,.43),color=dark)
    b.resize((1,.10,.68))
    put(rng,"oven_round_top_%d"%k,b)
    for j in range(3):
        px=x+(j-1)*.25
        cyl(rng,"pot_%d_%d"%(k,j),px,2.54,.89,.105+(j%2)*.025,
            .12,(.30,.26,.20))
        cyl(rng,"pot_lip_%d_%d"%(k,j),px,2.54,1.01,.125+(j%2)*.025,
            .018,cream)
pts=[]
for i in range(9):
    t=math.pi-i*math.pi/8
    pts.append((-3.05+2.15*math.cos(t),3.38,1.37+.70*math.sin(t)))
for i in range(8):
    put(rng,"range_arch_%d"%i,
        rod(.095,start=pts[i],end=pts[i+1],color=stone))
scene.include("cooking_range",rng)

# Broad table, longer on its foreground side.
table=Asset("worktable")
table_depth=TABLE_BACK-TABLE_FRONT
table_y=(TABLE_BACK+TABLE_FRONT)/2
put(table,"planked_top",
    box((TABLE_W,table_depth,.14),center=(0,table_y,.92),color=wood_top))
for x in (-1.63,1.63):
    for y in (TABLE_FRONT+.22,TABLE_BACK-.22):
        put(table,"leg_%s_%s"%(x,y),
            box((.15,.15,.91),center=(x,y,.46),color=wood))
for y in (TABLE_FRONT+.16,TABLE_BACK-.16):
    put(table,"apron_long_%s"%y,
        box((3.5,.09,.25),center=(0,y,.78),color=wood))
for x in (-1.68,1.68):
    put(table,"apron_short_%s"%x,
        box((.09,table_depth-.35,.25),center=(x,table_y,.78),color=wood))
put(table,"rear_partition",
    box((2.45,.10,.52),center=(0,.27,1.25),color=wood))
put(table,"right_partition",
    box((.10,1.35,.52),center=(1.18,-.38,1.25),color=wood))
put(table,"left_partition",
    box((.10,1.20,.43),center=(-1.18,-.32,1.21),color=wood))
scene.include("worktable",table)

chimney=Asset("central_stone_chimney")
put(chimney,"wide_base",box((1.25,1.16,.20),center=(0,.06,1.10),
                           color=(.38,.37,.32)))
put(chimney,"base_step",box((1.08,.99,.16),center=(0,.06,1.27),
                           color=(.46,.45,.40)))
put(chimney,"shaft",box((.78,.72,1.56),center=(0,.06,2.10),
                       color=(.53,.52,.46)))
for z,s in ((1.44,.90),(2.84,.90),(2.94,.99)):
    put(chimney,"moulding_%s"%z,
        box((s,s*.90,.09),center=(0,.06,z),color=(.59,.58,.51)))
put(chimney,"hood_bottom",
    box((1.05,.92,.12),center=(0,.06,3.05),color=(.61,.60,.53)))
put(chimney,"finial",
    ball(.105,center=(0,.06,4.08),color=(.66,.64,.58)))
# Fine horizontal stone joints across the visible front face of the cap.
for i,z in enumerate((3.31,3.55,3.77)):
    f=(z-3.11)/.86
    half=.525*(1-f)+.11*f
    front=-.402*(1-f)-.04*f
    put(chimney,"hood_joint_%d"%i,
        rod(.009,start=(-half,front-.007,z),
            end=(half,front-.007,z),color=(.43,.42,.36)))
scene.include("stone_chimney",chimney)

# Tableware: distinct shapes and colors distributed along several edges.
dishes=Asset("tableware_and_food")
def bowl(name,x,y,r,z=.995):
    cyl(dishes,name+"_body",x,y,z,r,.10,ochre)
    cyl(dishes,name+"_rim",x,y,z+.095,r*1.04,.025,cream)
    cyl(dishes,name+"_inside",x,y,z+.122,r*.78,.012,(.27,.20,.13))
def plate(name,x,y,r,z=.995):
    cyl(dishes,name+"_plate",x,y,z,r,.035,cream)
    cyl(dishes,name+"_center",x,y,z+.037,r*.72,.012,(.43,.42,.36))
for i,(x,y,r) in enumerate([
    (-1.45,-2.04,.17),(-.97,-2.05,.20),(-.48,-2.04,.17),
    (.06,-2.05,.20),(.57,-2.04,.18),(1.07,-2.02,.21),
    (-1.47,-1.48,.14),(-1.43,-1.05,.15),(-1.44,-.57,.17),
    (1.44,-1.45,.16),(1.43,-.92,.18)]):
    bowl("earthenware_%02d"%i,x,y,r)
for i,(x,y,r) in enumerate([
    (-1.40,.36,.18),(-.96,.43,.15),(-.70,-1.52,.20),
    (.78,-1.62,.19),(1.38,.30,.18),(-1.40,-.15,.13)]):
    plate("plate_%02d"%i,x,y,r)
for i,(x,y) in enumerate([
    (-1.50,-1.78),(-1.20,-1.75),(-.91,-1.74),
    (-.56,-1.73),(.20,-1.76),(.48,-1.76)]):
    b=ball(.13,center=(x,y,1.07),color=(.51,.32,.15))
    b.resize((1.3,.75,.5))
    put(dishes,"bread_%02d"%i,b)
for i,(x,y) in enumerate([
    (-.98,.42),(-.55,.42),(.55,.42),(.95,.40),
    (1.02,-.05),(1.02,-.45),(1.02,-.80)]):
    cyl(dishes,"cup_%02d"%i,x,y,1.00,.075,.18,
        (.26,.24,.17) if i%2 else cream)
    cyl(dishes,"cup_lip_%02d"%i,x,y,1.18,.08,.02,cream)
put(dishes,"folded_cloth",
    box((.57,.38,.025),center=(.87,-1.66,1.01),
        color=(.51,.48,.41)))
for i in range(4):
    x=.62+i*.17
    put(dishes,"utensil_%d"%i,
        rod(.018,start=(x,-1.91,1.04),end=(x+.12,-1.52,1.04),
            color=iron))
scene.include("tableware",dishes)

hearth=Asset("hearth_pots_and_baskets")
for i,(x,y,r,h) in enumerate([
    (2.40,2.83,.31,.30),(3.00,2.75,.26,.30),
    (3.22,2.15,.29,.38),(2.41,2.22,.24,.20),
    (2.05,3.05,.21,.24)]):
    cyl(hearth,"vessel_%d"%i,x,y,.02,r,h,
        (.17,.14,.10) if i%2 else (.27,.20,.12))
    cyl(hearth,"rim_%d"%i,x,y,h+.02,r*1.05,.035,(.25,.20,.13))
    cyl(hearth,"opening_%d"%i,x,y,h+.056,r*.78,.012,dark)
for i,(x,z,r) in enumerate([(1.2,1.45,.18),(1.5,1.15,.15),(1.15,.91,.13)]):
    put(hearth,"hanging_pan_%d"%i,
        rod(r,start=(x,3.39,z),end=(x,3.32,z),color=(.30,.30,.26)))
    put(hearth,"pan_handle_%d"%i,
        rod(.022,start=(x,3.35,z+r),end=(x,3.35,z+r+.24),color=iron))
scene.include("hearth_accessories",hearth)

realize(scene)

# One editable tapered mesh supplies the continuous hood surface.
verts=[
    (-.525,-.402,3.11),(.525,-.402,3.11),
    (.525,.522,3.11),(-.525,.522,3.11),
    (-.11,-.04,3.97),(.11,-.04,3.97),
    (.11,.16,3.97),(-.11,.16,3.97)]
faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),
       (1,5,6,2),(2,6,7,3),(3,7,4,0)]
mesh=bpy.data.meshes.new("Chimney tapered hood mesh")
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new("Chimney tapered stone hood",mesh)
bpy.context.scene.collection.objects.link(obj)
mat=bpy.data.materials.new("Hood limestone")
mat.diffuse_color=(.61,.60,.54,1)
mat.use_nodes=True
bsdf=mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value=(.61,.60,.54,1)
bsdf.inputs["Roughness"].default_value=.9
obj.data.materials.append(mat)

sc=bpy.context.scene
sc.render.resolution_x=471
sc.render.resolution_y=512
sc.render.resolution_percentage=100
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
background.inputs["Color"].default_value=(.70,.73,.72,1)
background.inputs["Strength"].default_value=.48

set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)
area_emitter((0,-3,8),power=1000,size=7,target=(0,0,0))
area_emitter((-4,1,6),power=450,size=5,target=(0,1,1))

# The camera remains unchanged. Compare a small upward-aim trial numerically,
# then restore the chosen pose; these point projections are not silhouettes.
landmarks=[
    ("finial",(0,.06,4.185),(.51,.23)),
    ("table front corner",(1.85,TABLE_FRONT,.99),(.48,.82)),
    ("hearth left spring",(HEARTH_CX-HEARTH_RX,3.44,1.30),(.43,.36)),
    ("hearth right spring",(HEARTH_CX+HEARTH_RX,3.44,1.30),(.84,.36))]
cam=sc.camera
def projected():
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    out=[]
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1))
        out.append(None if clip.w<=1e-8 else
                   (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return out

chosen=projected()
rotation=cam.rotation_euler.copy()
direction=Vector((CAM_TARGET[0],CAM_TARGET[1],CAM_TARGET[2]+.20))-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
trial=projected()
cam.rotation_euler=rotation
bpy.context.view_layer.update()
print("Landmark | reference estimate | retained camera | upward aim trial")
for i,(name,p,ref) in enumerate(landmarks):
    print(name,ref,chosen[i],trial[i])
