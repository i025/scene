# Reference inventory and observed comparison (normalized image coordinates):
# The reference foreground cow spans approximately (.35,.36)-(.84,.84), with
# a visible head at the right, a large pale flank, folded legs and a tail.
# In the previous render, the nearest animals span about (.40,.44)-(.87,.75)
# collectively; their heads are largely hidden, and their coats are too finely
# mottled. The reference has large black and white regions, including two dark
# cows behind the foreground cow.
# The reference curb enters at (0,.57) and leaves the bottom near (.65,1);
# the rendered curb enters around (0,.55) and continues to the right edge near
# (.88,.88). The reference crops the row at both sides and shows deeper cow
# overlaps. The render exposes more continuous platform and foreground aisle.
# The reference blue door is near (.32,0)-(.43,.20); the rendered door is near
# (.30,.16)-(.46,.37). The right blue post is near x=.91 in the reference and
# outside the render. The wall division is near y=.11 in the reference and
# about y=.35 in the render.
# The silver partition loops overlap the cows, with large open gaps beneath the
# upper tubes. The near curb slopes down to the right, as do the rail tops.
# Exact membership of distant cows and hidden sides is uncertain.
#
# Ranked corrections:
# 1. CAMERA_POSITION moves closer and slightly toward the front of the stalls;
#    this enlarges the cows, deepens overlaps, and steepens the curb edge.
#    CAMERA_TARGET and CAMERA_LENS remain independently adjustable. The
#    projection check compares the previous and candidate cameras and rejects
#    a candidate if the foreground or both background anchors regress badly.
# 2. WALL_DIVISION and DOOR_TOP rise, moving those background contours upward;
#    RIGHT_POST_X moves the post left into the frame. These are local changes.
# 3. Cow bodies are elongated toward their heads, heads are raised and shifted
#    outward, and coarse, broad coat patches replace fine procedural speckling.
#    These changes enlarge the foreground cow contour and reveal its head.
# 4. Rails are brightened and rounded bends retained. Light and material
#    reflectance both affect their appearance; the renderer determines both.
#
# Expanded primitive estimate: architecture 13; 9 dividers x 8 rods = 72,
# plus 5 cross rails; 7 cows x approximately 17 primitives = 119; worker 7;
# scattered bedding 22. Total approximately 238 meshes. No booleans.
# Each named asset retains meaningful editable children.
from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(22)
scene = Scene("Modern dairy free stall barn")

# Camera and geometry parameters are intentionally independent.
OLD_CAMERA_POSITION = (7.5, -11.0, 3.35)
OLD_CAMERA_TARGET = (0.0, 0.15, 0.85)
OLD_CAMERA_LENS = 55
CAMERA_POSITION = (6.3, -8.8, 3.0)
CAMERA_TARGET = (0.0, 0.25, 0.95)
CAMERA_LENS = 55
BED_FRONT = -1.25
BED_BACK = 1.65
BED_TOP = .23
SPACING = 1.24
WALL_Y = 4.4
WALL_DIVISION = 2.30
DOOR_X = -4.15
DOOR_TOP = 2.65
RIGHT_POST_X = 2.65

metal = (.55, .58, .57)
white = (.69, .67, .59)
black = (.025, .029, .026)
blue = (.025, .075, .16)
concrete = (.39, .40, .38)

def ellipsoid(center, radii, color):
    shape = ball(1, center=center, color=color)
    shape.resize(radii, pivot=center)
    return shape

arch = Asset("Barn architecture")
arch.include("concrete aisle", box((20,16,.12), center=(0,0,-.09),
                                  color=(.39,.40,.38)))
arch.include("raised resting bed", box((16,BED_BACK-BED_FRONT,BED_TOP),
    center=(0,(BED_FRONT+BED_BACK)/2,BED_TOP/2), color=(.48,.48,.45)))
arch.include("front curb", box((16,.13,BED_TOP),
    center=(0,BED_FRONT,BED_TOP/2), color=(.31,.32,.30)))
arch.include("bedding aisle", box((18,3.4,.018),
    center=(0,-2.94,-.02), color=(.29,.26,.17)))
arch.include("lower concrete wall", box((22,.15,WALL_DIVISION),
    center=(0,WALL_Y,WALL_DIVISION/2), color=(.45,.46,.45)))
arch.include("upper wall panels", box((22,.12,4.0),
    center=(0,WALL_Y+.025,WALL_DIVISION+2), color=(.72,.74,.73)))
arch.include("wall division trim", box((22,.06,.055),
    center=(0,WALL_Y-.09,WALL_DIVISION), color=(.34,.36,.35)))
arch.include("door frame", box((1.48,.14,DOOR_TOP),
    center=(DOOR_X,WALL_Y-.13,DOOR_TOP/2), color=(.025,.09,.19)))
arch.include("door leaf", box((1.27,.035,DOOR_TOP-.20),
    center=(DOOR_X,WALL_Y-.22,(DOOR_TOP-.20)/2), color=blue))
arch.include("door seam", box((.035,.025,DOOR_TOP-.24),
    center=(DOOR_X+.08,WALL_Y-.25,(DOOR_TOP-.24)/2), color=(.018,.055,.12)))
for i,x in enumerate((-5.9,RIGHT_POST_X)):
    arch.include("blue post %d" % i, box((.16,.20,5.0),
        center=(x,WALL_Y-.16,2.5), color=(.035,.12,.23)))
arch.include("blue header", box((3.0,.14,.14),
    center=(DOOR_X,WALL_Y-.17,DOOR_TOP+.06), color=(.035,.12,.23)))
scene.include("architecture", arch)

stalls = Asset("Galvanized steel free stall partitions")
for i in range(9):
    x = (i-4)*SPACING
    divider = Asset("Divider %02d" % i)
    def segment(name,a,b,r=.038):
        divider.include(name, rod(r,start=a,end=b,color=metal))
    segment("upright", (x,1.43,.24),(x,1.43,1.49),.045)
    segment("upper rear bend", (x,1.43,1.49),(x,1.28,1.56))
    segment("upper rail", (x,1.28,1.56),(x,-.75,1.56))
    segment("rounded corner", (x,-.75,1.56),(x,-1.00,1.47))
    segment("loop front", (x,-1.00,1.47),(x,-1.10,1.23))
    segment("loop lower bend", (x,-1.10,1.23),(x,-1.00,1.06))
    segment("lower return rail", (x,-1.00,1.06),(x,.47,.78))
    segment("return end", (x,.47,.78),(x,.76,.82))
    stalls.include("divider %02d" % i, divider)
for j,(y,z) in enumerate(((1.40,1.50),(2.25,1.34),(2.72,1.10),
                           (3.10,.92),(3.38,1.42))):
    stalls.include("cross rail %d" % j,
        rod(.035,start=(-7,y,z),end=(7,y,z),color=metal))
scene.include("stall equipment",stalls)

# A separate palette color marks white cow parts for procedural material
# assignment; dark cows retain a plain dark material.
cows = Asset("Reclining Holstein cows")
cow_specs = [
    (-4.70,.02,"pale"), (-3.46,.02,"mixed"), (-2.22,-.02,"dark"),
    (-.98,-.02,"dark"), (.26,-.03,"mixed"), (1.50,-.02,"mixed"),
    (2.74,-.04,"mixed")
]
for i,(x,y,coat) in enumerate(cow_specs):
    cow = Asset("Holstein %02d" % i)
    base = black if coat == "dark" else white
    cow.include("barrel",ellipsoid((x,y,.65),(.61,1.10,.43),base))
    cow.include("rump",ellipsoid((x,y-.67,.59),(.56,.51,.38),base))
    cow.include("shoulder",ellipsoid((x,y+.64,.67),(.48,.48,.37),base))
    cow.include("neck",ellipsoid((x,y+1.05,.76),(.31,.43,.29),black))
    cow.include("head",ellipsoid((x,y+1.40,.80),(.27,.32,.24),black))
    cow.include("white face",ellipsoid((x,y+1.64,.78),(.15,.10,.17),(.73,.71,.64)))
    cow.include("muzzle",ellipsoid((x,y+1.69,.68),(.21,.14,.11),(.12,.105,.095)))
    for s in (-1,1):
        cow.include("ear %d" % s,ellipsoid((x+s*.28,y+1.34,.92),
                                           (.19,.13,.07),black))
        cow.include("folded leg %d" % s,ellipsoid((x+s*.37,y+.12,.32),
                                                  (.19,.53,.13),base))
        cow.include("hoof %d" % s,ellipsoid((x+s*.38,y+.49,.29),
                                            (.13,.16,.075),(.15,.14,.12)))
    cow.include("udder",ellipsoid((x-.24,y-.48,.34),(.24,.29,.15),(.45,.32,.29)))
    cow.include("tail",rod(.025,start=(x-.04,y-1.03,.48),
                            end=(x-.12,y-1.45,.18),color=(.20,.18,.13)))
    cow.include("tail tuft",ellipsoid((x-.12,y-1.45,.17),(.055,.11,.055),black))
    cows.include("cow %02d" % i,cow)
scene.include("cows",cows)

worker = Asset("Farm worker")
px,py = 3.9,3.5
worker.include("head",ellipsoid((px,py,1.68),(.12,.11,.15),(.35,.25,.19)))
worker.include("hair",ellipsoid((px,py,1.79),(.12,.11,.07),(.08,.07,.06)))
worker.include("blue jacket",ellipsoid((px,py,1.32),(.21,.13,.34),(.035,.13,.29)))
for s in (-1,1):
    worker.include("arm %d" % s,rod(.065,start=(px+s*.17,py,1.50),
        end=(px+s*.25,py-.06,1.06),color=(.04,.14,.30)))
    worker.include("leg %d" % s,rod(.075,start=(px+s*.10,py,1.02),
        end=(px+s*.13,py,.38),color=(.08,.10,.13)))
scene.include("worker",worker)

bedding = Asset("Scattered bedding")
for i in range(22):
    x = random.uniform(-7,7)
    y = random.uniform(-4.3,-1.4)
    length = random.uniform(.07,.20)
    bedding.include("straw %02d" % i,rod(.007,start=(x,y,-.005),
        end=(x+length,y+random.uniform(-.07,.07),-.004),color=(.43,.36,.23)))
scene.include("bedding",bedding)

realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value = (.68,.73,.78,1)
background.inputs["Strength"].default_value = .32

# Broad, smooth, irregular black regions on the pale coat.
coat_mat = bpy.data.materials.new("Broad Holstein coat markings")
coat_mat.use_nodes = True
nt = coat_mat.node_tree
shader = nt.nodes.get("Principled BSDF")
shader.inputs["Roughness"].default_value = .9
coord = nt.nodes.new("ShaderNodeTexCoord")
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 1.8
noise.inputs["Detail"].default_value = 1.3
noise.inputs["Roughness"].default_value = .55
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.interpolation = "CONSTANT"
ramp.color_ramp.elements[0].position = .45
ramp.color_ramp.elements[0].color = (.025,.027,.024,1)
ramp.color_ramp.elements[1].position = .46
ramp.color_ramp.elements[1].color = (.69,.67,.59,1)
nt.links.new(coord.outputs["Generated"],noise.inputs["Vector"])
nt.links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"],shader.inputs["Base Color"])

for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        c = bsdf.inputs["Base Color"].default_value
        if sum(abs(c[k]-white[k]) for k in range(3)) < .035:
            slot.material = coat_mat
        elif sum(abs(c[k]-metal[k]) for k in range(3)) < .035:
            bsdf.inputs["Metallic"].default_value = .72
            bsdf.inputs["Roughness"].default_value = .28
        elif sum(abs(c[k]-v) for k,v in enumerate((.12,.105,.095))) < .035:
            bsdf.inputs["Roughness"].default_value = .22
        else:
            bsdf.inputs["Roughness"].default_value = .85

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
set_view(OLD_CAMERA_POSITION,OLD_CAMERA_TARGET,lens=OLD_CAMERA_LENS)
area_emitter((0,-1,7),power=1500,size=8,target=(0,0,0),color=(.80,.87,1.0))
area_emitter((-5,2,5),power=700,size=6,target=(0,0,.5),color=(.9,.93,1.0))

# The reference coordinates are estimates of visible features. Individual cow
# and divider correspondences are less certain than wall features. The curb
# point is its actual near top edge, not the platform's far edge.
landmarks = [
    ("door top left",(DOOR_X-.74,WALL_Y-.22,DOOR_TOP),(.32,.02)),
    ("right post at division",(RIGHT_POST_X,WALL_Y-.26,WALL_DIVISION),(.91,.11)),
    ("divider top",(.26,-.75,1.56),(.53,.26)),
    ("foreground cow rump",(1.50,-.69,.97),(.43,.55)),
    ("near curb top",(0,BED_FRONT,BED_TOP),(.45,.84)),
]
def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(dg,x=sc.render.resolution_x,
        y=sc.render.resolution_y,scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result = []
    for name,p,ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*p,1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w))
        result.append((name,ref,uv))
    return result

def report(label,values):
    print(label)
    for name,ref,uv in values:
        print(name,"reference",ref,"projected",uv)

baseline = projections()
report("Previous camera, final geometry",baseline)
cam = sc.camera
old_location = cam.location.copy()
old_rotation = cam.rotation_euler.copy()
old_lens = cam.data.lens
cam.location = CAMERA_POSITION
cam.rotation_euler = (Vector(CAMERA_TARGET)-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens = CAMERA_LENS
trial = projections()
report("Candidate camera, final geometry",trial)

# Check every independent anchor and the foreground crop before accepting.
# Permit uncertain cow correspondences to shift, but reject a trial if it sends
# a visible foreground point far outside the image, or severely worsens both
# background points.
accept = all(row[2] is not None for row in trial)
if accept:
    for idx in (3,4):
        u,v = trial[idx][2]
        if not (-.15 < u < 1.15 and -.15 < v < 1.15):
            accept = False
    background_regressions = 0
    for idx in (0,1):
        ref = baseline[idx][1]
        before = baseline[idx][2]
        after = trial[idx][2]
        if before is not None:
            e0 = abs(ref[0]-before[0])+abs(ref[1]-before[1])
            e1 = abs(ref[0]-after[0])+abs(ref[1]-after[1])
            if e1 > e0+.12:
                background_regressions += 1
    if background_regressions == 2:
        accept = False
if not accept:
    cam.location = old_location
    cam.rotation_euler = old_rotation
    cam.data.lens = old_lens
    print("Candidate rejected due to anchor regression or foreground crop.")
else:
    print("Candidate accepted after per-anchor and crop checks.")
report("Final active camera projections",projections())
