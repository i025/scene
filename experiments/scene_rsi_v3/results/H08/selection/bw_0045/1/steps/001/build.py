from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory and visual anchors, estimated from the photograph:
# - Concrete rear wall and white upper cladding occupy approximately (0,0)-(1,.30);
#   dark blue door is around (.32,.02)-(.43,.23).
# - Receding galvanized stall dividers occupy roughly (0,.15)-(1,.78).
#   Their bright horizontal rails slope gently downward toward image right.
# - Four overlapping black-and-white reclining cows occupy roughly (0,.27)-(.83,.85).
#   The closest cow spans approximately (.35,.36)-(.83,.83), with its rump left,
#   black head right, folded legs below, and white flank carrying irregular black spots.
# - Raised concrete beds and curb cross the foreground diagonally from (0,.55)
#   to (.75,1); a dirty walking alley occupies the bottom left.
# - A small worker appears at the upper-right edge, partly obscured by rails.
# The far ends of cows, individual legs, and the full building envelope are occluded.
# Approximate expanded primitive budget: architecture 15, rails 90, cows 95,
# bedding and dirt 30, worker 9, total about 240 mesh primitives.

scene = Scene("Modern dairy free-stall barn")

# Major dimensions and camera are separately parameterized.
BED_LENGTH = 3.4
STALL_WIDTH = 1.42
STALL_Y = [-2.65, -1.23, 0.19, 1.61, 3.03, 4.45]
CAMERA_POSITION = (6.8, -11.4, 5.1)
CAMERA_TARGET = (0.0, 0.45, 0.72)
CAMERA_LENS = 36

concrete = (0.48, 0.49, 0.48)
bed_concrete = (0.56, 0.57, 0.55)
wall_gray = (0.47, 0.49, 0.49)
cladding = (0.78, 0.80, 0.80)
blue = (0.025, 0.12, 0.28)
steel = (0.63, 0.67, 0.66)
black = (0.025, 0.027, 0.025)
white = (0.80, 0.79, 0.73)
pink = (0.47, 0.34, 0.32)
dirt = (0.33, 0.31, 0.24)

def add_ball(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)
    return obj

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius, start=a, end=b, color=color))

architecture = Asset("Barn architecture")
architecture.include("walking alley", box((9.0, 13.5, .12), center=(0, 0, -.11), color=(.36,.35,.31)))
architecture.include("raised stall platform", box((BED_LENGTH, 10.8, .25), center=(0, .55, .05), color=bed_concrete))
architecture.include("concrete curb", box((.16, 10.8, .28), center=(-1.76, .55, .075), color=(.39,.40,.38)))
architecture.include("rear lower concrete wall", box((12, .18, 1.52), center=(0, 5.75, .76), color=wall_gray))
architecture.include("rear upper white wall", box((12, .16, 2.2), center=(0, 5.76, 2.62), color=cladding))
architecture.include("door blue frame", box((1.5, .08, 2.12), center=(-2.35, 5.63, 1.15), color=(.018,.07,.15)))
architecture.include("blue metal door", box((1.32, .06, 1.92), center=(-2.35, 5.57, 1.12), color=blue))
architecture.include("door inset upper", box((1.13, .025, .77), center=(-2.35, 5.52, 1.56), color=(.035,.16,.34)))
architecture.include("door inset lower", box((1.13, .025, .77), center=(-2.35, 5.52, .65), color=(.03,.13,.28)))
for x in [-5.5, -3.2, 0.7, 4.3]:
    architecture.include("blue structural column %.1f" % x,
                         box((.13,.20,3.7), center=(x,5.62,1.85), color=(.025,.12,.25)))
for x in [-4.5, -1.1, 2.4, 5.2]:
    architecture.include("wall panel joint %.1f" % x,
                         box((.018,.025,2.1), center=(x,5.65,2.6), color=(.58,.61,.61)))
scene.include("architecture", architecture)

# Each divider is a visible loop of steel tube with an open lower region.
rails = Asset("Galvanized stall dividers")
for i, y in enumerate(STALL_Y):
    divider = Part("stall divider %d" % i)
    # High outer rail, sloping curved nose, lower return and uprights.
    path = [(-1.58,y,1.30), (-1.35,y,1.48), (1.03,y,1.48),
            (1.45,y,1.38), (1.50,y,1.12), (1.42,y,.80),
            (1.19,y,.66), (.54,y,.80), (-.12,y,.89)]
    for j in range(len(path)-1):
        add_rod(divider, "loop segment %d" % j, path[j], path[j+1], .045, steel)
    add_rod(divider, "front post", (1.42,y,.15), (1.42,y,1.36), .047, steel)
    add_rod(divider, "rear support", (-1.49,y,.18), (-1.49,y,1.36), .038, steel)
    rails.include("divider %d" % i, divider)
# Long rails tie the repeated dividers together.
for j, x in enumerate([1.42, -1.42]):
    add_rod(rails, "longitudinal top rail %d" % j,
            (x,-3.6,1.46), (x,5.45,1.46), .038, steel)
scene.include("stall equipment", rails)

# Cow body components use flattened ellipsoids to retain lying silhouettes.
# Spots are discrete flattened dark forms on the upper and camera-facing surfaces.
def make_cow(index, x, y, scale=1.0, phase=0):
    cow = Asset("Holstein cow %d" % index)
    def P(dx,dy,dz):
        return (x+dx*scale, y+dy*scale, .19+dz*scale)
    def ell(name, dx,dy,dz, sx,sy,sz, col):
        return add_ball(cow, name, P(dx,dy,dz), (sx*scale,sy*scale,sz*scale), col)
    ell("white barrel", -.12,0,.55, 1.08,.53,.48, white)
    ell("rounded rump", -.83,0,.48, .43,.49,.42, white)
    ell("shoulder", .57,0,.59, .43,.48,.42, white)
    ell("black neck", .91,0,.69, .47,.35,.34, black)
    ell("black head", 1.23,-.03,.70, .37,.27,.28, black)
    ell("white face blaze", 1.43,-.055,.68, .18,.255,.13, white)
    ell("moist muzzle", 1.57,-.055,.62, .16,.22,.105, pink)
    ell("left ear", 1.11,-.30,.84, .22,.12,.075, black)
    ell("right ear", 1.10,.28,.85, .20,.11,.07, black)
    ell("visible eye", 1.32,-.272,.79, .035,.025,.035, (0.01,.01,.01))
    ell("folded rear leg", -.74,-.40,.19, .45,.17,.16, white)
    ell("rear hoof", -1.02,-.46,.15, .17,.13,.10, (0.14,.13,.12))
    ell("folded front leg", .55,-.38,.20, .46,.17,.13, white)
    ell("front hoof", .83,-.39,.16, .16,.13,.09, (0.14,.13,.12))
    ell("udder", -.43,-.13,.18, .30,.25,.16, (0.59,.44,.40))
    # Broad irregular patches, clustered across the white upper body and flank.
    spots = [
        (-.60,-.36,.75,.34,.13,.22),
        (-.22,-.43,.66,.22,.11,.27),
        (.08,-.45,.72,.16,.09,.21),
        (.30,-.38,.86,.20,.11,.14),
        (-.52,.00,1.01,.31,.28,.055),
        (.05,.04,1.02,.26,.24,.06),
        (.47,-.17,.93,.20,.22,.07),
    ]
    for k,(dx,dy,dz,sx,sy,sz) in enumerate(spots):
        ell("black coat patch %d" % k, dx,dy,dz,sx,sy,sz,black)
    add_rod(cow, "tail", P(-1.05,-.20,.38), P(-1.38,-.45,.04), .045*scale, (0.24,.21,.17))
    scene.include("cow %d" % index, cow)

make_cow(1, -.05, -2.06, 1.0)
make_cow(2, -.35, -.65, .96)
make_cow(3, -.58, .77, .94)
make_cow(4, -.62, 2.19, .90)
make_cow(5, -.76, 3.58, .83)

# Restrained irregular bedding and soiled patches on the exposed floor.
bedding = Asset("Sparse bedding and floor marks")
for i in range(24):
    x = -1.48 + ((i*37)%283)/100.0
    y = -3.65 + ((i*83)%850)/100.0
    sx = .09 + (i%3)*.035
    sy = .035 + (i%4)*.018
    z = .183
    add_ball(bedding, "scattered bedding %02d" % i, (x,y,z), (sx,sy,.012),
             (0.46,.43,.32) if i%2 else (0.38,.37,.31))
for i in range(7):
    x = -2.0 - (i%3)*.36
    y = -3.7 + i*1.25
    add_ball(bedding, "alley soiling %02d" % i, (x,y,-.043),
             (.35,.48,.008), (0.30,.29,.23))
scene.include("bedding", bedding)

# Small partly obscured worker gives the stall equipment a human scale.
worker = Asset("Worker at back of barn")
wx, wy = 3.6, 5.05
worker.include("trouser left", box((.18,.19,.72), center=(wx-.11,wy,.40), color=(.10,.13,.17)))
worker.include("trouser right", box((.18,.19,.72), center=(wx+.11,wy,.40), color=(.10,.13,.17)))
worker.include("blue jacket", box((.52,.29,.64), center=(wx,wy,1.08), color=(.08,.19,.39)))
add_ball(worker, "head", (wx,wy,1.57), (.15,.14,.19), (.34,.24,.19))
add_ball(worker, "hair", (wx,wy,1.69), (.15,.14,.08), (.08,.07,.06))
add_rod(worker, "left arm", (wx-.22,wy,1.31), (wx-.38,wy-.12,.88), .09, (.08,.19,.39))
add_rod(worker, "right arm", (wx+.22,wy,1.30), (wx+.32,wy-.12,.92), .09, (.08,.19,.39))
scene.include("worker", worker)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100

# Configure world after realization, which clears Blender's default scene.
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
background.inputs["Color"].default_value = (0.67, .73, .80, 1)
background.inputs["Strength"].default_value = .55

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0,-1,7.5), power=1500, size=8, target=(0,0,0), color=(.78,.86,1))
area_emitter((-4,-4,4.5), power=650, size=6, target=(0,0,.5), color=(.85,.90,1))

# SceneAct shares finishes. Assign copies for the selected distinctive metal and
# muzzle subsets so changes do not leak to other objects using the same finish.
def customize_matching(color, name, metallic, roughness):
    count = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for idx, mat in enumerate(obj.data.materials):
            if not mat or not mat.use_nodes:
                continue
            shader = mat.node_tree.nodes.get("Principled BSDF")
            if shader is None:
                continue
            c = shader.inputs["Base Color"].default_value
            if sum(abs(c[j]-color[j]) for j in range(3)) < .035:
                newmat = mat.copy()
                newmat.name = name
                obj.data.materials[idx] = newmat
                bs = newmat.node_tree.nodes.get("Principled BSDF")
                bs.inputs["Metallic"].default_value = metallic
                bs.inputs["Roughness"].default_value = roughness
                count += 1
    print(name, "selected meshes:", count, "metallic:", metallic, "roughness:", roughness)

customize_matching(steel, "stall galvanized metal", .72, .26)
customize_matching(pink, "cow moist muzzle", 0.0, .27)

# Reference-versus-projected landmark estimates. These test camera direction only;
# they do not verify silhouette, visibility, or material appearance.
landmarks = [
    ("blue door upper right", (-1.69,5.52,2.08), (.43,.04)),
    ("front divider top", (1.42,-2.65,1.46), (.72,.31)),
    ("foreground curb end", (-1.76,-3.6,.20), (.12,.72)),
    ("closest cow muzzle", (1.52,-2.11,.81), (.79,.55)),
]
def print_projection(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print("Landmark projection:", label)
    for name, p, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, "reference", ref, "projected",
              None if uv is None else tuple(round(v,3) for v in uv))
print_projection("initial")
