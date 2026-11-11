from sceneact import *
import bpy
import math
import random
from mathutils import Vector

# Reference inventory and anchors (normalized image coordinates, visual estimates):
# Pale plaster walls fill the upper image, meeting near (.40, .02). The rear
# dark hearth and its stone arch span roughly (.41, .22)-(.84, .46); a white
# range and its dark openings occupy (0, .27)-(.37, .51). The chimney finial
# is near (.51, .23), and its stone shaft overlaps both hearth and table.
# The table spans approximately (.18, .45)-(.72, .87), with diagonal edges,
# wooden partitions, dishes and food. Foreground paving extends to the lower
# edge; dark floor, vessels and baskets occupy the right side.
# The hearth interior and individual small utensils remain partly occluded.
#
# Comparison with the completed first render:
# 1. Framing: chimney finial reference (.51,.23), render about (.49,.34);
#    table foreground reference about (.48,.86), render about (.52,.66).
#    Rear arch reference spans about (.41,.22)-(.84,.46), render about
#    (.53,.34)-(.75,.49). The render exposes the floor and wall boundaries,
#    whereas the photograph crops all of them.
# 2. The reference hearth is a broad dark arch; the render has a conspicuous
#    rectangular dark patch above the arch. The left range is also too small.
# 3. The reference chimney has a sloped pyramidal cap; the rendered cap is
#    strongly stair-stepped. The reference table is more crowded and darker.
# Edge directions are broadly similar: table and paving edges descend toward
# the image foreground. The chimney overlaps the rear hearth and worktable in
# both views, so that arrangement is retained.
#
# Corrections: increase CAM_LENS from 39 to 64 to enlarge the common scene
# about the principal point, moving the finial upward and foreground down,
# and extend walls and floor to eliminate their visible external boundaries.
# A small target trial is projected below before the chosen camera is restored.
# Increase the range width, replace the rectangular hearth top with an arched
# dark silhouette and stone band, and replace the chimney's stepped cap with
# a single tapered mesh. Darken the wooden table and floor materials; observed
# brightness is also affected by the lighting and surface orientation.
# Primitive estimate: floor ~100, architecture and arches ~55, range ~30,
# table and chimney ~25, tableware ~85, hearth items ~25: about 320 meshes.
# Custom tapered cap is one additional mesh.

random.seed(23)
scene = Scene("Historic kitchen")

CAM_POS = (7.5, -11.5, 12.0)
CAM_TARGET = (0.0, 0.35, 1.05)
CAM_LENS = 64
TABLE_W, TABLE_D = 3.7, 2.75
TABLE_CENTER = (0.0, -0.55)

plaster = (.67, .69, .67)
stone = (.38, .37, .32)
dark = (.055, .052, .044)
wood = (.27, .15, .075)
wood_light = (.38, .235, .12)
iron = (.12, .12, .105)
cream = (.68, .66, .57)
ochre = (.49, .31, .14)

def add(a, name, node):
    a.include(name, node)
    return node

def cyl(a, name, x, y, z, r, h, color):
    return add(a, name, rod(r, start=(x, y, z),
                            end=(x, y, z+h), color=color))

# Large continuous floor and irregular pale slabs, with darker paving at right.
floor = Asset("floor_and_paving")
add(floor, "dark_floor", box((30, 30, .12), center=(0, 0, -.12),
                             color=(.22, .225, .195)))
for i in range(12):
    for j in range(11):
        x = -3.85 + i*.67
        y = -4.1 + j*.67
        if x > 2.35:
            continue
        q = random.uniform(-.045, .035)
        add(floor, "slab_%02d_%02d" % (i,j),
            box((.645,.645,.025), center=(x,y,-.045),
                color=(.39+q,.38+q,.33+q)))
scene.include("floor", floor)

# Broad wall surfaces extend beyond the camera crop. The rear opening is
# assembled from a dark arched back and plaster strips over its curve.
arch = Asset("rear_hearth_and_walls")
add(arch, "rear_upper_plaster",
    box((30,.22,8), center=(0,3.70,6.4), color=plaster))
add(arch, "left_pier",
    box((12,.22,2.4), center=(-7.6,3.70,1.2), color=plaster))
add(arch, "right_pier",
    box((12,.22,2.4), center=(8.6,3.70,1.2), color=plaster))
add(arch, "left_wall",
    box((.20,20,10), center=(-4.25,1.0,4.95), color=plaster))

# The opening is approximated by vertical strips whose tops follow an arch,
# avoiding the conspicuous rectangular dark area in the previous render.
arch_cx, arch_rx, arch_base, arch_rise = .50, 2.10, 1.30, 1.05
for i in range(16):
    x0 = arch_cx - arch_rx + i*(2*arch_rx/16)
    x1 = arch_cx - arch_rx + (i+1)*(2*arch_rx/16)
    xc = (x0+x1)/2
    u = (xc-arch_cx)/arch_rx
    top = arch_base + arch_rise*math.sqrt(max(0,1-u*u))
    add(arch, "dark_arch_section_%02d"%i,
        box((x1-x0+.01,.08,top), center=(xc,3.62,top/2), color=dark))
    # Plaster above each section extends to the upper wall.
    add(arch, "plaster_over_arch_%02d"%i,
        box((x1-x0+.01,.20,2.43-top),
            center=(xc,3.70,(top+2.43)/2), color=plaster))
points = []
for i in range(13):
    t = math.pi - i*math.pi/12
    points.append((arch_cx+arch_rx*math.cos(t),3.44,
                   arch_base+arch_rise*math.sin(t)))
for i in range(12):
    add(arch, "stone_arch_%02d"%i,
        rod(.105,start=points[i],end=points[i+1],color=stone))
for x in (-1.6,2.6):
    add(arch,"stone_jamb_%s"%x,
        box((.22,.30,1.3),center=(x,3.49,.65),color=stone))
for z in (.32,.55,.78,1.01,1.24):
    add(arch,"grate_bar_%s"%z,
        rod(.022,start=(-.35,3.39,z),end=(1.55,3.39,z),color=iron))
for x in (-.3,.25,.8,1.5):
    add(arch,"grate_upright_%s"%x,
        rod(.022,start=(x,3.38,.24),end=(x,3.38,1.35),color=iron))
scene.include("architecture",arch)

# The left masonry range and the low arch framing above it.
rng = Asset("left_masonry_cooking_range")
add(rng,"body",box((3.55,.92,.79),center=(-2.8,2.55,.40),
                   color=(.62,.64,.60)))
add(rng,"counter",box((3.65,1.0,.09),center=(-2.8,2.55,.84),
                      color=(.25,.25,.22)))
for k,x in enumerate((-3.90,-2.8,-1.7)):
    add(rng,"oven_dark_%d"%k,
        box((.62,.035,.45),center=(x,2.075,.23),color=dark))
    b = ball(.31,center=(x,2.06,.45),color=dark)
    b.resize((1,.10,.68))
    add(rng,"oven_round_%d"%k,b)
    for j in range(3):
        px=x+(j-1)*.24
        cyl(rng,"pot_%d_%d"%(k,j),px,2.54,.89,.10+(j%2)*.025,.12,
            (.34,.30,.25))
        cyl(rng,"pot_rim_%d_%d"%(k,j),px,2.54,1.01,.12+(j%2)*.025,
            .018,cream)
# Low stone curve is visible behind the range.
pts=[]
for i in range(9):
    t=math.pi-i*math.pi/8
    pts.append((-2.7+1.9*math.cos(t),3.38,1.37+.70*math.sin(t)))
for i in range(8):
    add(rng,"range_arch_%d"%i,rod(.085,start=pts[i],end=pts[i+1],color=stone))
scene.include("cooking_range",rng)

table=Asset("worktable")
tx,ty=TABLE_CENTER
add(table,"top",box((TABLE_W,TABLE_D,.14),center=(tx,ty,.92),color=wood_light))
for x in (-1.63,1.63):
    for y in (-1.70,.60):
        add(table,"leg_%s_%s"%(x,y),
            box((.15,.15,.91),center=(x,y,.46),color=wood))
for y in (-1.72,.62):
    add(table,"long_apron_%s"%y,
        box((3.5,.09,.25),center=(0,y,.78),color=wood))
for x in (-1.68,1.68):
    add(table,"short_apron_%s"%x,
        box((.09,2.32,.25),center=(x,-.55,.78),color=wood))
add(table,"rear_partition",
    box((2.45,.10,.52),center=(0,.27,1.25),color=wood))
add(table,"right_partition",
    box((.10,1.35,.52),center=(1.18,-.38,1.25),color=wood))
add(table,"left_partition",
    box((.10,1.20,.43),center=(-1.18,-.32,1.21),color=wood))
scene.include("worktable",table)

chimney=Asset("central_stone_chimney")
add(chimney,"wide_base",box((1.25,1.16,.20),center=(0,.06,1.10),
                            color=(.43,.42,.37)))
add(chimney,"base_step",box((1.08,.99,.16),center=(0,.06,1.27),
                            color=(.52,.51,.46)))
add(chimney,"shaft",box((.78,.72,1.56),center=(0,.06,2.10),
                        color=(.58,.57,.51)))
for z,s in ((1.44,.90),(2.84,.90),(2.94,.99)):
    add(chimney,"moulding_%s"%z,
        box((s,s*.90,.09),center=(0,.06,z),color=(.63,.62,.55)))
add(chimney,"hood_bottom",
    box((1.05,.92,.12),center=(0,.06,3.05),color=(.65,.64,.57)))
add(chimney,"finial",ball(.105,center=(0,.06,4.08),color=(.70,.68,.62)))
scene.include("stone_chimney",chimney)

# Dishes are individually named assets with visible rims and interiors.
dishes=Asset("tableware_and_food")
def bowl(name,x,y,r,z=.995):
    cyl(dishes,name+"_body",x,y,z,r,.10,ochre)
    cyl(dishes,name+"_rim",x,y,z+.095,r*1.04,.025,cream)
    cyl(dishes,name+"_inside",x,y,z+.122,r*.78,.012,(.29,.22,.15))
def plate(name,x,y,r,z=.995):
    cyl(dishes,name+"_plate",x,y,z,r,.035,cream)
    cyl(dishes,name+"_center",x,y,z+.037,r*.72,.012,(.48,.47,.41))
for i,(x,y,r) in enumerate([
    (-1.45,-1.48,.17),(-.97,-1.53,.20),(-.48,-1.49,.17),
    (.06,-1.51,.20),(.57,-1.52,.18),(1.07,-1.49,.21),
    (-1.47,-.98,.14),(-1.43,-.57,.15),(-1.44,-.12,.17),
    (1.44,-1.03,.16),(1.43,-.57,.18)]):
    bowl("earthenware_%02d"%i,x,y,r)
for i,(x,y,r) in enumerate([
    (-1.40,.36,.18),(-.96,.43,.15),(-.70,-1.05,.20),
    (.78,-1.13,.19),(1.38,.30,.18)]):
    plate("plate_%02d"%i,x,y,r)
for i,(x,y) in enumerate([
    (-1.51,-1.25),(-1.20,-1.25),(-.91,-1.25),
    (-.56,-1.22),(.20,-1.27),(.48,-1.27)]):
    b=ball(.13,center=(x,y,1.07),color=(.58,.38,.20))
    b.resize((1.3,.75,.5))
    add(dishes,"bread_%02d"%i,b)
for i,(x,y) in enumerate([
    (-.98,.42),(-.55,.42),(.55,.42),(.95,.40),
    (1.02,-.05),(1.02,-.45),(1.02,-.80)]):
    cyl(dishes,"cup_%02d"%i,x,y,1.00,.075,.18,
        (.30,.28,.21) if i%2 else cream)
    cyl(dishes,"cup_lip_%02d"%i,x,y,1.18,.08,.02,cream)
add(dishes,"folded_cloth",
    box((.50,.37,.025),center=(.88,-1.18,1.01),color=(.58,.55,.48)))
for i in range(4):
    x=.62+i*.17
    add(dishes,"cutlery_%d"%i,
        rod(.018,start=(x,-1.42,1.04),end=(x+.12,-1.05,1.04),color=iron))
scene.include("tableware",dishes)

hearth=Asset("hearth_pots_and_baskets")
for i,(x,y,r,h) in enumerate([
    (2.90,2.83,.31,.30),(3.50,2.75,.26,.30),
    (3.72,2.15,.29,.38),(2.91,2.22,.24,.20),
    (2.55,3.05,.21,.24)]):
    cyl(hearth,"vessel_%d"%i,x,y,.02,r,h,
        (.20,.17,.13) if i%2 else (.31,.23,.14))
    cyl(hearth,"rim_%d"%i,x,y,h+.02,r*1.05,.035,(.28,.23,.16))
    cyl(hearth,"opening_%d"%i,x,y,h+.056,r*.78,.012,dark)
for i,(x,z,r) in enumerate([(1.7,1.45,.18),(2.0,1.15,.15),(1.65,.91,.13)]):
    add(hearth,"hanging_pan_%d"%i,
        rod(r,start=(x,3.39,z),end=(x,3.32,z),color=(.35,.35,.31)))
    add(hearth,"pan_handle_%d"%i,
        rod(.022,start=(x,3.35,z+r),end=(x,3.35,z+r+.24),color=iron))
scene.include("hearth_accessories",hearth)

realize(scene)

# One editable tapered mesh forms the broad, sloped stone hood.
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
mat.diffuse_color=(.66,.65,.59,1)
mat.use_nodes=True
bsdf=mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value=(.66,.65,.59,1)
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
background.inputs["Strength"].default_value=.55

set_view(CAM_POS,CAM_TARGET,lens=CAM_LENS)
area_emitter((0,-3,8),power=1200,size=7,target=(0,0,0))
area_emitter((-4,1,6),power=550,size=5,target=(0,1,1))

# Print projections for the prior lens, selected lens, and a small upward-aim
# trial. Reference values are image observations, not computed projections.
landmarks=[
    ("chimney finial",(0,.06,4.185),(.51,.23)),
    ("table front corner",(1.85,-1.925,.99),(.48,.86)),
    ("hearth left spring",(-1.60,3.44,1.30),(.43,.36)),
    ("hearth right spring",(2.60,3.44,1.30),(.84,.36))]
cam=sc.camera
def projected():
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    proj=cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    vals=[]
    for name,p,ref in landmarks:
        clip=proj @ cam.matrix_world.inverted() @ Vector((*p,1))
        vals.append(None if clip.w<=1e-8 else
                    (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return vals

cam.data.lens=39
prior=projected()
cam.data.lens=CAM_LENS
chosen=projected()
original_rotation=cam.rotation_euler.copy()
direction=Vector((CAM_TARGET[0],CAM_TARGET[1],CAM_TARGET[2]+.20))-cam.location
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
trial=projected()
cam.rotation_euler=original_rotation
bpy.context.view_layer.update()
print("Landmark | reference | previous lens | chosen lens | upward aim trial")
for i,(name,p,ref) in enumerate(landmarks):
    print(name,ref,prior[i],chosen[i],trial[i])
