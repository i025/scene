# Reference versus first render, visually estimated in normalized coordinates:
# - Back door: reference x=.32-.43, y=.00-.20; render x=.50-.59, y=.22-.43.
# - Right blue post: reference x=.90-.93; render x=.89-.91, with its base too low.
# - Foreground cow: reference x=.35-.84, y=.36-.84; rendered cows are much
#   smaller, approximately x=.20-.78, y=.38-.72 collectively.
# - Near curb: reference enters at left around y=.58 and exits the bottom near
#   x=.64; render enters around (.08,.49) and exits at the lower right.
# Largest discrepancies: 1. cow size and black/white coverage; 2. camera
# elevation, scene scale and crop; 3. door position and stall-loop silhouettes.
# The first render exposed the entire platform, while the reference crops both
# ends and has a much shallower downward view. Cows overlap the partitions and
# one another; their individual rear silhouettes and distant membership remain
# uncertain.
# Corrections: lower CAMERA_POSITION.z and increase CAMERA_LENS to enlarge the
# cattle and move the near curb downward; shift the door left independently.
# Increase cow barrel width and length, give each animal a different coat, and
# use broad irregular markings on the actual surface. Rounded metal loops remain
# open below the rail, with broad gaps occupied by the cows.
#
# Reference anchors: door top-left (.32,.00), right post at wall division
# (.91,.11), middle divider top around (.53,.26), nearest cow rump around
# (.43,.60), near curb around (.45,.88). These are image estimates; the
# correspondence of the cow and divider anchors is approximate.
# Primitive estimate: architecture 16; 9 partitions * 8 rods = 72 plus 5
# crossbars; 7 cows * about 15 shapes = 105; worker 8; bedding marks 30;
# total about 236 meshes. No booleans or nested primitive expansions.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(15)
scene = Scene("Dairy free-stall barn")

# Parameters for camera, room and the main equipment remain independent.
CAMERA_POSITION = (7.5, -11.0, 3.35)
CAMERA_TARGET = (0.0, 0.15, 1.0)
CAMERA_LENS = 55
BED_FRONT = -1.25
BED_BACK = 1.65
BED_TOP = .23
SPACING = 1.24
WALL_Y = 4.4
DOOR_X = -4.15

metal = (.48, .52, .52)
wall = (.46, .47, .46)
white = (.67, .66, .58)
black = (.025, .028, .025)
blue = (.025, .075, .16)
floor_color = (.37, .38, .36)
straw_color = (.27, .23, .14)

def ellipsoid(center, radii, color):
    obj = ball(1, center=center, color=color)
    obj.resize(radii, pivot=center)
    return obj

architecture = Asset("Barn architecture")
architecture.include("concrete aisle", box((20, 16, .12), center=(0, 0, -.09), color=floor_color))
architecture.include("raised concrete bed", box((15, BED_BACK-BED_FRONT, .23),
    center=(0, (BED_FRONT+BED_BACK)/2, .115), color=(.47, .47, .44)))
architecture.include("bed front curb", box((15, .12, .23),
    center=(0, BED_FRONT, .115), color=(.32, .33, .31)))
architecture.include("bedding aisle", box((16, 3.3, .018),
    center=(0, -2.91, -.02), color=(.30, .27, .19)))
architecture.include("lower concrete wall", box((22, .15, 1.38),
    center=(0, WALL_Y, .69), color=wall))
architecture.include("upper wall panels", box((22, .12, 3.7),
    center=(0, WALL_Y+.025, 3.23), color=(.70, .72, .71)))
architecture.include("wall division trim", box((22, .06, .055),
    center=(0, WALL_Y-.09, 1.40), color=(.34, .36, .35)))
architecture.include("blue door frame", box((1.48, .14, 2.05),
    center=(DOOR_X, WALL_Y-.13, 1.025), color=(.025, .09, .19)))
architecture.include("blue door leaf", box((1.27, .035, 1.84),
    center=(DOOR_X, WALL_Y-.22, 1.02), color=blue))
architecture.include("door central seam", box((.035, .025, 1.75),
    center=(DOOR_X+.08, WALL_Y-.25, 1.02), color=(.018, .055, .12)))
for i, x in enumerate((-5.9, 3.55)):
    architecture.include("blue structural post %d" % i,
        box((.16, .20, 4.6), center=(x, WALL_Y-.16, 2.3),
            color=(.035, .12, .23)))
architecture.include("blue header", box((3.0, .14, .14),
    center=(DOOR_X, WALL_Y-.17, 2.11), color=(.035, .12, .23)))
scene.include("architecture", architecture)

# A sequence of freestall dividers extends beyond the frame at both ends.
stalls = Asset("Galvanized stall dividers")
for i in range(9):
    x = (i-4)*SPACING
    part = Asset("Divider %02d" % i)
    def seg(name, a, b, r=.036):
        part.include(name, rod(r, start=a, end=b, color=metal))
    # Vertical leg at the rear of the cubicle, curved upper tube, and the
    # returning lower loop leave open space for the reclining cow.
    seg("mounting upright", (x,1.43,.24), (x,1.43,1.48), .045)
    seg("upper return", (x,1.43,1.48), (x,1.28,1.55))
    seg("top rail", (x,1.28,1.55), (x,-.73,1.55))
    seg("top curved corner", (x,-.73,1.55), (x,-1.02,1.44))
    seg("outer curved nose", (x,-1.02,1.44), (x,-1.12,1.21))
    seg("lower bend", (x,-1.12,1.21), (x,-1.00,1.04))
    seg("lower rail", (x,-1.00,1.04), (x,.48,.76))
    seg("lower return", (x,.48,.76), (x,.76,.80))
    stalls.include("divider %02d" % i, part)
for j, (y, z) in enumerate(((1.40,1.50), (2.25,1.34), (2.72,1.10),
                             (3.10,.92), (3.38,1.42))):
    stalls.include("long cross rail %d" % j,
        rod(.032, start=(-7,y,z), end=(7,y,z), color=metal))
scene.include("stall equipment", stalls)

# Surface patches are made as shared procedural coat materials after realization.
# Solid dark animals are included because the reference has large dark masses.
cows = Asset("Resting Holstein cows")
cow_specs = [
    (-4.70, .02, "pale"),
    (-3.46, .02, "mixed"),
    (-2.22, -.02, "dark"),
    (-.98, -.02, "dark"),
    (.26, -.03, "mixed"),
    (1.50, -.02, "mixed"),
    (2.74, -.04, "mixed"),
]
for i, (x, y, coat) in enumerate(cow_specs):
    cow = Asset("Holstein %02d" % i)
    base = black if coat == "dark" else white
    cow.include("barrel", ellipsoid((x,y,.65), (.60,1.08,.43), base))
    cow.include("broad rump", ellipsoid((x,y-.66,.59), (.56,.52,.39), base))
    cow.include("shoulder", ellipsoid((x,y+.62,.67), (.48,.47,.38), base))
    cow.include("neck", ellipsoid((x,y+.99,.72), (.34,.45,.30), black))
    cow.include("head", ellipsoid((x,y+1.35,.74), (.28,.35,.25), black))
    cow.include("white face", ellipsoid((x,y+1.61,.72), (.17,.11,.19), white))
    cow.include("wet muzzle", ellipsoid((x,y+1.66,.62), (.22,.14,.12), (.12,.105,.095)))
    for s in (-1,1):
        cow.include("ear %d" % s, ellipsoid((x+s*.29,y+1.30,.88), (.19,.13,.075), black))
        cow.include("folded leg %d" % s, ellipsoid((x+s*.37,y+.10,.32), (.19,.55,.13), base))
        cow.include("hoof %d" % s, ellipsoid((x+s*.38,y+.50,.29), (.13,.17,.075), (.15,.14,.12)))
    cow.include("udder", ellipsoid((x-.24,y-.48,.34), (.24,.29,.15), (.45,.32,.29)))
    cow.include("tail", rod(.025, start=(x-.04,y-1.03,.48),
        end=(x-.12,y-1.45,.18), color=(.20,.18,.13)))
    cow.include("tail tuft", ellipsoid((x-.12,y-1.45,.17), (.055,.11,.055), black))
    cows.include("cow %02d" % i, cow)
scene.include("cows", cows)

worker = Asset("Worker for scale")
px, py = 4.3, 3.5
worker.include("head", ellipsoid((px,py,1.68), (.12,.11,.15), (.35,.25,.19)))
worker.include("hair", ellipsoid((px,py,1.79), (.12,.11,.07), (.08,.07,.06)))
worker.include("blue jacket", ellipsoid((px,py,1.32), (.21,.13,.34), (.035,.13,.29)))
for s in (-1,1):
    worker.include("arm %d" % s, rod(.065, start=(px+s*.17,py,1.50),
        end=(px+s*.25,py-.06,1.06), color=(.04,.14,.30)))
    worker.include("leg %d" % s, rod(.075, start=(px+s*.10,py,1.02),
        end=(px+s*.13,py,.38), color=(.08,.10,.13)))
scene.include("worker", worker)

debris = Asset("Loose bedding")
for i in range(30):
    x = random.uniform(-7,7)
    y = random.uniform(-4.3,-1.4)
    length = random.uniform(.07,.20)
    debris.include("straw %02d" % i,
        rod(.007, start=(x,y,-.005), end=(x+length,y+random.uniform(-.07,.07),-.004),
            color=(.43,.36,.23)))
scene.include("bedding", debris)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68,.73,.78,1)
background.inputs["Strength"].default_value = .32

# Irregular broad black markings on the white coat are generated in 3D, so
# they conform to the barrels and do not appear as raised circular spots.
coat_mat = bpy.data.materials.new("Holstein irregular coat")
coat_mat.use_nodes = True
nt = coat_mat.node_tree
bsdf = nt.nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value = .9
tex = nt.nodes.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 3.2
tex.inputs["Detail"].default_value = 2.0
tex.inputs["Roughness"].default_value = .7
coord = nt.nodes.new("ShaderNodeTexCoord")
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.interpolation = "CONSTANT"
ramp.color_ramp.elements[0].position = .46
ramp.color_ramp.elements[0].color = (.025,.027,.024,1)
ramp.color_ramp.elements[1].position = .47
ramp.color_ramp.elements[1].color = (.68,.66,.57,1)
nt.links.new(coord.outputs["Generated"], tex.inputs["Vector"])
nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

# SceneAct names are not guaranteed to propagate to meshes; identify white
# materials by their exact palette color and replace those slots for coat parts.
# White face markings also receive the same restrained mottling.
for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes:
            continue
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if shader is None:
            continue
        c = shader.inputs["Base Color"].default_value
        if sum(abs(c[k]-white[k]) for k in range(3)) < .035:
            slot.material = coat_mat
        elif sum(abs(c[k]-metal[k]) for k in range(3)) < .035:
            shader.inputs["Metallic"].default_value = .72
            shader.inputs["Roughness"].default_value = .28
        elif sum(abs(c[k]-v) for k,v in enumerate((.12,.105,.095))) < .035:
            shader.inputs["Roughness"].default_value = .22
        else:
            shader.inputs["Roughness"].default_value = .85

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((0,-1,7), power=1500, size=8, target=(0,0,0),
             color=(.80,.87,1.0))
area_emitter((-5,2,5), power=700, size=6, target=(0,0,.5),
             color=(.9,.93,1.0))

# Reference points and computed projections are separate. The door and post
# are reliable; cow and divider correspondences are approximate because of
# overlaps and repeated forms. The foreground point is on the actual curb.
landmarks = [
    ("door top left", (DOOR_X-.74,WALL_Y-.22,2.05), (.32,.02)),
    ("right post wall division", (3.55,WALL_Y-.26,1.40), (.91,.11)),
    ("central divider top", (.26,-.73,1.55), (.53,.26)),
    ("near cow rump", (1.50,-.68,.98), (.43,.55)),
    ("near curb top", (0,BED_FRONT,BED_TOP), (.45,.84)),
]

def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result = []
    for name, p, ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*p,1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        result.append((name,ref,uv))
    return result

def report(label, data):
    print(label)
    for name, ref, uv in data:
        print(name, "reference", ref, "projected", uv)

initial = projections()
report("Initial reference versus geometry projections", initial)

# A single conservative camera-aim trial is accepted only when both background
# anchors improve and the foreground curb remains visible. Geometry is fixed.
if all(item[2] is not None for item in initial):
    vertical_errors = [ref[1]-uv[1] for _,ref,uv in initial]
    if all(e > .09 for e in vertical_errors[:2]) or all(e < -.09 for e in vertical_errors[:2]):
        old_rotation = sc.camera.rotation_euler.copy()
        dz = .15 if vertical_errors[0] > 0 else -.15
        trial_target = Vector((CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]+dz))
        sc.camera.rotation_euler = (trial_target-sc.camera.location).to_track_quat('-Z','Y').to_euler()
        trial = projections()
        report("Candidate aim projections", trial)
        good = all(t[2] is not None for t in trial)
        if good:
            for index in (0,1):
                ref = initial[index][1]
                before = initial[index][2]
                after = trial[index][2]
                if abs(ref[1]-after[1]) > abs(ref[1]-before[1]):
                    good = False
            curb = trial[-1][2]
            if not (-.1 < curb[0] < 1.1 and -.1 < curb[1] < 1.1):
                good = False
        if not good:
            sc.camera.rotation_euler = old_rotation

report("Final active camera projections", projections())
