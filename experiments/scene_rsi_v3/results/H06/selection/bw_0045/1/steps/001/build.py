# Reference inventory and visual anchors (normalized image coordinates, x right/y down):
# - Raised concrete beds and curb: approximately (0.00, 0.53)-(1.00, 1.00).
#   The front curb runs diagonally down toward the right; brown aisle occupies lower left.
# - Nearest reclining Holstein: approximately (0.36, 0.39)-(0.84, 0.87);
#   broad white flank with irregular dark patches, dark neck/head and pale muzzle.
# - Additional overlapping cows: approximately (0.00, 0.25)-(0.59, 0.71).
#   Their bodies and legs are partly hidden by each other and the stall rails.
# - Galvanized stall dividers: approximately (0.00, 0.15)-(1.00, 0.83).
#   Repeated rounded loops cross in front of cows; long horizontal rails recede into depth.
# - Rear wall: approximately (0.00, 0.00)-(1.00, 0.28), pale upper panels,
#   gray concrete lower wall, blue door near (0.37, 0.10), blue structural posts.
# - Partly cropped worker near (0.97, 0.13)-(1.00, 0.40).
# Dominant edges: the bed front slopes down to the right; horizontal rear wall
# edges are nearly level; rails converge gently toward the distant left.
# Occluded cow legs, exact rear stall count, and door depth are uncertain.
#
# Expanded primitive estimate: architecture ~15; stall tubes ~130 (each tube
# expands to 2*n-1); cows ~110; worker ~10; total roughly 265 meshes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Modern dairy freestall barn")

# Major dimensions and camera are kept independent for later editing.
BED_X0, BED_X1 = -2.7, 2.9
BED_Y0, BED_Y1 = -3.4, 4.6
STALL_SPACING = 1.03
CAM_POS = (8.1, -11.8, 5.4)
CAM_TARGET = (0.0, 0.3, 1.15)
CAM_LENS = 42

concrete = (0.48, 0.49, 0.48)
bedmat = (0.56, 0.57, 0.56)
wallgray = (0.43, 0.45, 0.46)
panel = (0.77, 0.80, 0.81)
blue = (0.025, 0.10, 0.25)
steel = (0.66, 0.70, 0.71)
black = (0.035, 0.038, 0.036)
white = (0.76, 0.75, 0.68)
pink = (0.52, 0.38, 0.36)
straw = (0.34, 0.30, 0.19)

barn = Asset("Barn architecture")
barn.include("aisle", box((13, 13, .12), center=(0, 0, -.09), color=(.30, .28, .21)))
barn.include("raised_bed", box((BED_X1-BED_X0, BED_Y1-BED_Y0, .25),
                               center=((BED_X0+BED_X1)/2, (BED_Y0+BED_Y1)/2, .045),
                               color=bedmat))
barn.include("front_curb", box((.19, BED_Y1-BED_Y0, .30),
                               center=(BED_X0, (BED_Y0+BED_Y1)/2, .08), color=concrete))
barn.include("rear_concrete_wall", box((13, .15, 1.38),
                                       center=(0, 5.0, .69), color=wallgray))
barn.include("upper_wall_panels", box((13, .15, 2.25),
                                      center=(0, 5.0, 2.50), color=panel))
for x in (-5.7, -2.6, 1.5, 5.5):
    barn.include("blue_column_%s" % x, box((.16, .22, 3.7),
                                           center=(x, 4.88, 1.85), color=blue))
for x in (-4.6, -3.5, -.9, .25, 2.8, 4.0):
    barn.include("panel_joint_%s" % x, box((.025, .025, 2.15),
                                           center=(x, 4.90, 2.50), color=(.58,.61,.62)))
barn.include("door_frame", box((1.35,.10,1.65), center=(-1.55,4.87,.83), color=blue))
barn.include("door_leaf", box((1.16,.04,1.43), center=(-1.55,4.80,.78), color=(.025,.075,.18)))
barn.include("door_crossbar", box((1.15,.04,.05), center=(-1.55,4.76,.88), color=(.08,.15,.26)))
scene.include("barn", barn)

# Divider loop lies along the cow's length. The repeated dividers define individual bays.
stalls = Asset("Galvanized freestall dividers")
for i in range(9):
    y = BED_Y0 + i * STALL_SPACING
    divider = Asset("Stall divider %02d" % (i+1))
    divider.include("loop", sweep_tube(
        points=[(2.35,y,.20), (2.35,y,1.32), (2.20,y,1.47),
                (.35,y,1.47), (-.82,y,1.43), (-1.12,y,1.30),
                (-1.12,y,1.02), (-.90,y,.94), (.55,y,.89)],
        radius=.038, color=steel))
    divider.include("front_upright", rod(.043, start=(2.35,y,.16),
                                        end=(2.35,y,1.49), color=steel))
    stalls.include("divider_%02d" % i, divider)
for j, (x,z) in enumerate(((2.34,1.39), (1.82,.73), (-.74,1.41))):
    stalls.include("longitudinal_rail_%d" % j,
                   rod(.036, start=(x,BED_Y0,z), end=(x,BED_Y1,z), color=steel))
scene.include("stall_equipment", stalls)

def ellipsoid(radius, center, scale, color):
    n = ball(radius, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

# Cows recline lengthwise in their stalls. Each cow is a separate editable asset.
def add_cow(name, y, x_offset, scale=1.0, variation=0):
    cow = Asset(name)
    def E(label, c, s, col):
        p = (c[0]*scale+x_offset, c[1]*scale+y, c[2]*scale+.18)
        cow.include(label, ellipsoid(1, p, tuple(v*scale for v in s), col))
    E("barrel", (-.35,0,.52), (1.03,.43,.48), white)
    E("shoulder", (.38,0,.52), (.50,.39,.45), white)
    E("rump", (-1.06,0,.43), (.46,.42,.40), white)
    E("neck", (.84,0,.50), (.55,.31,.31), black)
    E("head", (1.25,-.03,.47), (.36,.24,.25), black)
    E("muzzle", (1.53,-.04,.39), (.17,.21,.13), pink)
    E("nose", (1.60,-.04,.40), (.09,.17,.085), (.16,.15,.14))
    E("near_ear", (1.15,-.28,.65), (.21,.10,.075), black)
    E("far_ear", (1.15,.23,.65), (.19,.09,.07), black)
    E("folded_hind_leg", (-.92,-.30,.18), (.48,.17,.14), white)
    E("folded_front_leg", (.45,-.29,.18), (.49,.14,.13), white)
    E("near_hoof", (.77,-.30,.17), (.14,.13,.085), (.19,.18,.16))
    E("udder", (-.78,-.15,.18), (.30,.22,.16), pink)
    # Large patches hug the visible top and near flank, preserving the cow silhouette.
    for k, (cx,cy,cz,sx,sy,sz) in enumerate([
        (-.78,-.30,.64,.32,.12,.26), (-.35,-.39,.55,.22,.07,.22),
        (.02,-.36,.71,.19,.08,.19), (.27,-.25,.83,.21,.12,.12),
        (-.20,.03,.96,.34,.22,.075), (-1.05,-.09,.79,.29,.25,.11)]):
        E("coat_patch_%d" % k, (cx,cy,cz), (sx,sy,sz), black)
    scene.include(name, cow)

add_cow("Foreground Holstein", -2.40, -.05, 1.02)
add_cow("Second Holstein", -1.30, -.45, .98)
add_cow("Third Holstein", -.22, -.60, .95)
add_cow("Fourth Holstein", .90, -.42, .92)
add_cow("Fifth Holstein", 2.00, -.60, .88)
add_cow("Distant Holstein", 3.10, -.60, .84)

# Sparse bedding and wear remain subordinate to the main concrete surface.
bedding = Asset("Bedding and floor wear")
for i in range(26):
    x = -2.45 + ((i*37) % 47)/10
    y = -3.10 + ((i*53) % 73)/10
    bedding.include("straw_mark_%02d" % i,
                    box((.10 + (i%3)*.04, .025, .008),
                        center=(x,y,.178), color=(.49,.45,.34)))
scene.include("bedding", bedding)

# Background worker provides a familiar scale reference.
worker = Asset("Worker")
worker.include("torso", box((.40,.23,.68), center=(4.45,4.40,1.18), color=(.08,.22,.40)))
worker.include("head", ellipsoid(.16, (4.45,4.40,1.73), (1,.9,1.15), (.47,.31,.23)))
worker.include("hair", ellipsoid(.16, (4.45,4.41,1.83), (1,.9,.55), (.09,.07,.06)))
worker.include("left_leg", rod(.085, start=(4.34,4.40,.85), end=(4.32,4.40,.16), color=(.10,.14,.20)))
worker.include("right_leg", rod(.085, start=(4.56,4.40,.85), end=(4.60,4.40,.16), color=(.10,.14,.20)))
worker.include("left_arm", rod(.075, start=(4.27,4.40,1.42), end=(4.10,4.28,1.02), color=(.08,.22,.40)))
worker.include("right_arm", rod(.075, start=(4.63,4.40,1.42), end=(4.72,4.25,1.04), color=(.08,.22,.40)))
scene.include("worker", worker)

realize(scene)

# World, cool overhead lighting and camera are configured after realization.
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70,.76,.82,1)
background.inputs["Strength"].default_value = .65

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0,-1,7), power=1500, size=8, target=(0,0,0), color=(.82,.90,1))
area_emitter((-4,3,5), power=800, size=6, target=(0,0,1), color=(.90,.94,1))

# Give galvanized steel a distinct soft metallic sheen, while keeping concrete matte.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    base = bsdf.inputs["Base Color"].default_value
    if abs(base[0]-.66) < .035 and abs(base[1]-.70) < .035:
        bsdf.inputs["Metallic"].default_value = .75
        bsdf.inputs["Roughness"].default_value = .27
    else:
        bsdf.inputs["Roughness"].default_value = .78

# Small projection check: estimates are uncertain visual correspondences, not calibration.
# The curb crop is an intersection with the image edge, not a physical bed corner.
references = [
    ("door upper corner", (-2.22,4.80,1.65), (.32,.04)),
    ("near divider top", (2.20,-2.37,1.47), (.80,.36)),
    ("foreground cow muzzle", (1.48,-2.44,.58), (.82,.55)),
    ("rear wall junction", (1.5,4.88,1.38), (.52,.22)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                             scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark                         reference       projected")
for label, point, ref in references:
    clip = proj @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(label, ref, None if uv is None else tuple(round(v,3) for v in uv))
