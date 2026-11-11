# Reference inventory, normalized image coordinates (x right, y down):
# - Raised concrete resting platform: approximately (0.00, 0.48)-(1.00, 1.00),
#   with its front edge descending from (0.00, 0.58) to (0.70, 1.00).
# - Foreground cow: approximately (0.35, 0.38)-(0.84, 0.89); broad white
#   body, irregular black patches, dark head facing right, folded legs and tail.
# - Other reclining cows: overlapping dark and white bodies from the left edge
#   through the center, with additional partially hidden cows behind the rails.
# - Galvanized steel stall dividers: repeated rounded horizontal loops and
#   upright posts across approximately (0.00, 0.15)-(1.00, 0.75). They overlap
#   the cows, and recede toward the left background.
# - Concrete rear wall and blue door: wall occupies the top third, door
#   approximately (0.31, 0.04)-(0.43, 0.19). A person is cropped at the far
#   right, behind the rails. Rear stall contents are partly occluded.
# Dominant edges: wall seams are nearly horizontal; the front platform edge
# slopes downward to the right; parallel rails recede toward the left.
#
# Stable projection anchors (reference estimates, not calibration):
# A: foreground platform front edge at image bottom, approximately (.68, .98).
# B: blue door top-left, approximately (.32, .04).
# C: foreground cow's upper back, approximately (.50, .46).
# D: foremost divider top front bend, approximately (.84, .28).
# Their exact world correspondences are uncertain in the single image.
#
# Expanded primitive estimate: architecture ~22; 8 stall loops and posts
# ~105 rods; 5 cows ~105 ellipsoids; person ~9; bedding ~35.
# Approximately 276 meshes total. No Boolean operations.
from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)

# Major scene parameters and camera are independent for later editing.
STALL_SPACING = 1.28
STALL_COUNT = 8
PLATFORM_FRONT = -1.65
PLATFORM_BACK = 2.05
PLATFORM_TOP = 0.18
CAMERA_POSITION = (8.3, -12.8, 6.2)
CAMERA_TARGET = (0.0, 0.25, 0.95)
CAMERA_LENS = 43

scene = Scene("Modern dairy barn")
concrete = (0.46, 0.47, 0.46)
floor_color = (0.38, 0.36, 0.30)
steel = (0.58, 0.62, 0.63)
wall = (0.51, 0.54, 0.54)
white = (0.78, 0.78, 0.72)
black = (0.045, 0.052, 0.048)
pink = (0.52, 0.37, 0.34)
blue = (0.035, 0.10, 0.22)

building = Asset("Barn architecture")
building.include("walkway", box((19, 12, .14), center=(0, 0, -.09), color=floor_color))
building.include("raised resting platform", box((15, 3.7, .26),
    center=(0, (PLATFORM_FRONT + PLATFORM_BACK)/2, .05), color=concrete))
building.include("platform front fascia", box((15, .10, .27),
    center=(0, PLATFORM_FRONT, .04), color=(.34,.35,.34)))
building.include("rear concrete wall", box((19, .16, 2.6),
    center=(0, 3.65, 1.30), color=wall))
building.include("upper light wall", box((19, .18, 1.55),
    center=(0, 3.65, 3.22), color=(.75,.78,.78)))
building.include("blue doorway", box((1.35,.10,1.95),
    center=(-2.55,3.52,1.05), color=blue))
building.include("door inner panel", box((1.17,.04,1.60),
    center=(-2.55,3.44,1.04), color=(.045,.12,.25)))
for x in [-8,-5.6,-3.22,-.5,2.3,5.3,8.2]:
    building.include("wall upright %.1f"%x, box((.11,.22,4.0),
        center=(x,3.48,2.0), color=(.06,.17,.29)))
for x in [-7,-5,-3,-1,1,3,5,7]:
    building.include("upper wall seam %.1f"%x, box((.025,.03,1.55),
        center=(x,3.53,3.22), color=(.45,.48,.49)))
scene.include("architecture", building)

# Straight segments with rounded corners form each visible free-stall divider.
rails = Asset("Galvanized stall dividers")
for i in range(STALL_COUNT):
    x = (i - 3.5) * STALL_SPACING
    stall = Asset("stall divider %02d" % i)
    # Loop projects from the rear toward the cows' shoulder end. Its open
    # interior and bent front are important to the silhouette.
    pts = [(x,1.78,1.48),(x,.30,1.48),(x,-.16,1.46),
           (x,-.42,1.36),(x,-.48,1.20),(x,-.42,1.05),
           (x,-.12,.94),(x,1.48,.78)]
    for j in range(len(pts)-1):
        stall.include("curved rail segment %d"%j,
            rod(.038, start=pts[j], end=pts[j+1], color=steel))
    stall.include("front upright", rod(.045, start=(x,-.48,.17),
        end=(x,-.48,1.20), color=steel))
    stall.include("rear upright", rod(.042, start=(x,1.77,.18),
        end=(x,1.77,1.48), color=steel))
    rails.include("divider %02d"%i, stall)
# Longitudinal high rails give the layered horizontal structure in the photo.
for k, y in enumerate((1.72, 2.12)):
    rails.include("long rail %d"%k, rod(.033, start=(-5.9,y,1.50+k*.13),
        end=(5.9,y,1.50+k*.13), color=steel))
scene.include("stall equipment", rails)

def ellipsoid(center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

def make_cow(name, x, y, scale=1.0, pattern=0):
    # Cows lie lengthwise from back to front. Heads turn toward image right.
    a = Asset(name)
    def E(part, dx, dy, z, sx, sy, sz, color):
        c = (x + dx*scale, y + dy*scale, PLATFORM_TOP + z*scale)
        a.include(part, ellipsoid(c, (sx*scale,sy*scale,sz*scale),color))
    E("barrel", 0, 0, .43, .47,.91,.39, white)
    E("rump", 0, -.62, .40, .45,.40,.35, white)
    E("shoulder", 0, .57, .43, .40,.40,.34, white)
    E("neck", .10, .82, .43, .27,.43,.28, black)
    E("head", .15, 1.12, .43, .23,.33,.22, black)
    E("muzzle", .15, 1.39, .37, .19,.15,.12, pink)
    E("muzzle dark wet nose", .15, 1.48, .39, .16,.08,.075, (.12,.11,.105))
    E("left ear", -.12, 1.10, .60, .15,.16,.065, black)
    E("right ear", .38, 1.10, .60, .15,.16,.065, black)
    E("folded hind leg", -.24,-.68,.19,.25,.34,.13, white)
    E("folded front leg", .24,.61,.16,.21,.36,.12, white)
    E("udder", .14,-.42,.17,.22,.30,.14, pink)
    # Broad surface patches use flattened ellipsoids close to the body.
    patches = [(-.38,-.27,.49,.105,.36,.23),
               (-.36,.40,.50,.09,.23,.22),
               (.37,-.60,.43,.10,.26,.21),
               (.36,.05,.55,.10,.26,.20),
               (-.05,-.20,.78,.24,.23,.035),
               (.07,.43,.75,.22,.22,.035)]
    if pattern % 2:
        patches = [(dx,dy,z,sx,sy,sz) for dx,dy,z,sx,sy,sz in patches]
    for j,(dx,dy,z,sx,sy,sz) in enumerate(patches):
        E("black coat patch %d"%j,dx,dy,z,sx,sy,sz,black)
    a.include("tail", rod(.028*scale,
        start=(x,y-.91*scale,PLATFORM_TOP+.34*scale),
        end=(x+.17*scale,y-1.24*scale,PLATFORM_TOP+.12*scale),
        color=(.24,.22,.18)))
    return a

# Individual animals occupy alternating stalls; the leftmost ones are cropped
# or partly hidden, as in the reference.
cows = Asset("Resting Holstein cows")
for i,(x,y,s) in enumerate([(-3.95,-.02,.91),(-2.68,.04,.94),
                            (-1.38,.02,.96),(-.06,.00,1.00),
                            (1.23,.12,.94),(2.53,.38,.87)]):
    cows.include("cow %d"%(i+1), make_cow("Holstein %d"%(i+1),x,y,s,i))
scene.include("cows", cows)

# Restrained straw and manure flecks, kept as editable low-cost geometry.
bedding = Asset("Sparse bedding")
for i in range(35):
    x = random.uniform(-5.7,5.7)
    y = random.uniform(-1.52,1.95)
    bedding.include("straw %02d"%i, box((random.uniform(.08,.22),.018,.008),
        center=(x,y,.187),color=random.choice([(0.47,.42,.28),(.57,.51,.35),(.34,.32,.25)])))
scene.include("bedding", bedding)

# A distant person establishes the equipment scale.
person = Asset("Barn worker")
px, py = 5.15, 2.95
person.include("torso", box((.40,.25,.60),center=(px,py,1.35),color=(.10,.24,.42)))
person.include("head", ellipsoid((px,py,1.83),(.14,.13,.18),(.49,.35,.27)))
person.include("hair", ellipsoid((px,py+.015,1.95),(.14,.13,.09),(.12,.10,.09)))
for side in (-1,1):
    person.include("leg %d"%side, rod(.085,start=(px+side*.10,py,1.06),
        end=(px+side*.12,py,.43),color=(.10,.13,.17)))
    person.include("arm %d"%side, rod(.07,start=(px+side*.23,py,1.54),
        end=(px+side*.29,py-.06,1.15),color=(.10,.24,.42)))
scene.include("worker",person)

realize(scene)

# Metallic rails and rough concrete are assigned after realization.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    name = obj.name.lower()
    for mat in obj.data.materials:
        if not mat:
            continue
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if any(t in name for t in ("rail", "divider", "upright")):
                bsdf.inputs["Metallic"].default_value = .72
                bsdf.inputs["Roughness"].default_value = .27
            elif "nose" in name or "muzzle" in name:
                bsdf.inputs["Roughness"].default_value = .25
            else:
                bsdf.inputs["Roughness"].default_value = .83

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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68,.75,.82,1)
background.inputs["Strength"].default_value = .55

# Preserve source image aspect for camera projection and rendering.
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((0,-2,7), power=1600, size=8, target=(0,0,0), color=(.82,.90,1))
area_emitter((-5,1,5), power=700, size=6, target=(0,0,0), color=(.90,.94,1))

# A small numerical camera trial: compare the starting lens with nearby
# candidates against stable visual estimates. The best weighted candidate is
# selected; no reference point is moved to fit the model. These sparse checks
# cannot establish visibility or appearance.
bpy.context.view_layer.update()
cam = sc.camera
anchors = [
    ("platform edge", (1.5, PLATFORM_FRONT, PLATFORM_TOP), (.68,.98), .7),
    ("door top left", (-3.225,3.43,2.025), (.32,.04), 1.0),
    ("cow upper back", (-.06,-.05,.96), (.50,.46), 1.0),
    ("divider top", (1.92,-.16,1.46), (.84,.28), .6),
]
def project(p):
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    q = matrix @ cam.matrix_world.inverted() @ Vector((*p,1))
    if q.w <= 1e-8:
        return None
    return (.5*(q.x/q.w+1), .5*(1-q.y/q.w))
def evaluate(lens):
    cam.data.lens = lens
    bpy.context.view_layer.update()
    points = [project(a[1]) for a in anchors]
    score = sum(a[3]*((p[0]-a[2][0])**2+(p[1]-a[2][1])**2)
                for a,p in zip(anchors,points) if p is not None)
    return score, points
previous = evaluate(CAMERA_LENS)
trial = evaluate(CAMERA_LENS - 2)
other = evaluate(CAMERA_LENS + 2)
choices = [(previous[0],CAMERA_LENS,previous[1]),
           (trial[0],CAMERA_LENS-2,trial[1]),
           (other[0],CAMERA_LENS+2,other[1])]
_, selected_lens, final_points = min(choices,key=lambda v:v[0])
cam.data.lens = selected_lens
bpy.context.view_layer.update()
for a,old,new in zip(anchors,previous[1],final_points):
    if old is None or new is None:
        continue
    ref = a[2]
    print("%s ref=%s previous=%s candidate=%s residual_px=(%.1f, %.1f)" %
          (a[0],ref,old,new,(new[0]-ref[0])*512,(new[1]-ref[1])*285))
