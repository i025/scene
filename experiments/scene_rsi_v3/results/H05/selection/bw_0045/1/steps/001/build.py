# Reference inventory and visual anchors, estimated in normalized image coordinates:
# - Raised concrete beds and curb: foreground diagonal edge from (0, .57) to
#   (.69, 1); near floor occupies lower right and straw/manure lower left.
# - Foreground cow: body roughly (.35, .43)-(.76, .84), head at (.72, .37)-(.85, .57);
#   black-and-white flank, folded legs and tail. Other reclining cows overlap behind it
#   toward the left, with bodies occupying (.00, .31)-(.56, .72).
# - Galvanized stall loops: repeated silver tubes occupy most of the image from
#   (.00, .15) to (1, .72); loops run diagonally in perspective and overlap cows.
# - Back wall fills the upper band; blue door around (.32, .03)-(.43, .21);
#   blue structural posts at approximately x=.16 and x=.91. Person partly cropped
#   at upper right, approximately (.94, .12)-(1, .39).
# - Dominant edges: the bed curb and rail tops descend toward the right; wall/floor
#   boundaries are nearly horizontal. Far stalls and cows are partly occluded.
# Estimated expanded primitives: architecture 16, stalls about 115 rods, cows
# about 110 ellipsoids/rods, person 9, straw marks 25; total approximately 275.
# The hidden side of each cow and exact distant stall membership are uncertain.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(12)
scene = Scene("Modern dairy free-stall barn")

# Explicit scene dimensions and camera parameters.
STALL_SPACING = 1.25
STALL_COUNT = 7
BED_FRONT = -1.15
BED_BACK = 1.65
BED_TOP = 0.23
CAMERA_POSITION = (7.5, -11.0, 5.0)
CAMERA_TARGET = (0.0, 0.15, 0.9)
CAMERA_LENS = 43

concrete = (.43, .44, .43)
bed_color = (.51, .52, .50)
wall_color = (.57, .58, .57)
metal = (.62, .66, .66)
blue = (.035, .12, .26)
black = (.028, .035, .032)
white = (.73, .72, .64)
pink = (.49, .36, .34)
straw = (.39, .32, .17)

architecture = Asset("Barn architecture")
architecture.include("concrete floor", box((19, 15, .14), center=(0, 0, -.12), color=concrete))
architecture.include("raised resting platform", box((12.0, 2.8, .23),
    center=(0, .25, .115), color=bed_color))
architecture.include("front concrete curb", box((12, .13, .24),
    center=(0, BED_FRONT, .12), color=(.38, .39, .37)))
architecture.include("straw covered foreground", box((12, 2.5, .025),
    center=(0, -2.47, -.035), color=(.30, .27, .17)))
architecture.include("rear lower concrete wall", box((18, .16, 1.35),
    center=(0, 4.4, .675), color=(.46, .47, .46)))
architecture.include("rear upper wall", box((18, .13, 3.4),
    center=(0, 4.43, 3.05), color=(.74, .76, .75)))
architecture.include("wall dividing trim", box((18, .10, .10),
    center=(0, 4.32, 1.38), color=(.34, .36, .37)))
architecture.include("blue door", box((1.42, .10, 1.85),
    center=(-2.1, 4.31, .95), color=blue))
architecture.include("door inset", box((1.17, .025, 1.42),
    center=(-2.1, 4.24, 1.02), color=(.025, .075, .16)))
for i, x in enumerate((-4.0, 3.55)):
    architecture.include("blue column %d" % i, box((.14, .17, 4.3),
        center=(x, 4.22, 2.15), color=(.035, .14, .29)))
architecture.include("blue lintel", box((3.8, .14, .14),
    center=(-2.4, 4.22, 2.02), color=(.035, .13, .27)))
scene.include("architecture", architecture)

# Repeated open loops, with an open lower front and rounded bends represented by
# short diagonal segments. Their long direction is perpendicular to the bed curb.
stalls = Asset("Galvanized free stall partitions")
for i in range(STALL_COUNT):
    x = (i - 3) * STALL_SPACING
    partition = Asset("Stall divider %02d" % i)
    def rail(name, a, b, radius=.035):
        partition.include(name, rod(radius, start=a, end=b, color=metal))
    rail("front upright", (x, -1.02, .24), (x, -1.02, 1.35), .045)
    rail("upper bend", (x, -1.02, 1.35), (x, -.90, 1.48))
    rail("upper long rail", (x, -.90, 1.48), (x, 1.38, 1.48))
    rail("rear bend", (x, 1.38, 1.48), (x, 1.62, 1.34))
    rail("rear down curve", (x, 1.62, 1.34), (x, 1.64, .86))
    rail("return bend", (x, 1.64, .86), (x, 1.47, .72))
    rail("lower long rail", (x, 1.47, .72), (x, -.30, .72))
    rail("lower rising bend", (x, -.30, .72), (x, -.45, .82))
    rail("mounting foot", (x, -1.15, .25), (x, -.88, .25), .045)
    stalls.include("partition %02d" % i, partition)
# Long horizontal rails add the visible crosswise rhythm behind the cows.
for j, (y, z) in enumerate(((1.48, 1.45), (2.25, 1.18), (2.65, .83))):
    stalls.include("continuous cross rail %d" % j,
        rod(.035, start=(-5.4, y, z), end=(5.4, y, z), color=metal))
scene.include("stall equipment", stalls)

# Cows rest along the long axis of the stalls. The facing camera sees their
# near side, dark patches and broad silhouettes, with heads toward the rear.
def ellipsoid(center, radii, color):
    shape = ball(1, center=center, color=color)
    shape.resize(radii, pivot=center)
    return shape

def make_cow(name, x, y, variation=0):
    cow = Asset(name)
    # Broad resting barrel with low, uneven silhouette.
    cow.include("white barrel", ellipsoid((x, y, .59), (.50, .94, .40), white))
    cow.include("rump", ellipsoid((x, y-.59, .54), (.49, .45, .36), white))
    cow.include("shoulders", ellipsoid((x, y+.58, .64), (.42, .41, .36), white))
    cow.include("neck", ellipsoid((x, y+.91, .68), (.30, .39, .26), black))
    cow.include("head", ellipsoid((x, y+1.20, .69), (.27, .31, .23), black))
    cow.include("white face blaze", ellipsoid((x, y+1.41, .70), (.13, .12, .18), white))
    cow.include("moist muzzle", ellipsoid((x, y+1.47, .60), (.22, .14, .12), (.18, .16, .15)))
    for side in (-1, 1):
        cow.include("ear %d" % side, ellipsoid((x+side*.28, y+1.18, .83),
            (.20, .13, .075), black))
        cow.include("folded leg %d" % side, ellipsoid((x+side*.33, y-.10, .31),
            (.18, .48, .14), white))
        cow.include("hoof %d" % side, ellipsoid((x+side*.34, y+.25, .28),
            (.13, .16, .08), (.16, .15, .13)))
    # Slightly raised patches on the visible left and top surface.
    for k, (dx, dy, z, rx, ry, rz) in enumerate([
        (-.35,-.48,.68,.16,.25,.19), (-.42,.08,.68,.10,.27,.20),
        (-.24,.45,.91,.21,.22,.075), (.08,-.21,.96,.23,.25,.055),
        (.29,.35,.87,.17,.25,.07), (-.39,.40,.56,.10,.14,.16)]):
        cow.include("black flank marking %d" % k,
            ellipsoid((x+dx, y+dy, z), (rx, ry, rz), black))
    cow.include("tail", rod(.025, start=(x-.07,y-.88,.46),
        end=(x-.12,y-1.25,.18), color=(.19,.17,.13)))
    cow.include("tail tuft", ellipsoid((x-.12,y-1.25,.17), (.055,.12,.05), black))
    return cow

cows = Asset("Reclining Holstein cows")
for i, (x, y) in enumerate(((-3.65,.05), (-2.38,.03), (-1.15,.04),
                             (.10,.00), (1.35,.03), (2.60,.10))):
    cows.include("cow %d" % (i+1), make_cow("Holstein %d" % (i+1), x, y, i))
scene.include("cows", cows)

# Small, partly obscured staff member near the far wall gives scale.
person = Asset("Farm worker")
px, py = 4.25, 3.45
person.include("head", ellipsoid((px, py, 1.65), (.12,.11,.15), (.34,.25,.19)))
person.include("hair", ellipsoid((px, py, 1.76), (.12,.11,.07), (.08,.07,.06)))
person.include("blue jacket", ellipsoid((px, py, 1.30), (.22,.13,.34), (.05,.17,.37)))
for s in (-1, 1):
    person.include("arm %d" % s, rod(.065, start=(px+s*.18,py,1.48),
        end=(px+s*.27,py-.08,1.02), color=(.06,.18,.36)))
    person.include("leg %d" % s, rod(.075, start=(px+s*.10,py,.99),
        end=(px+s*.13,py,.38), color=(.10,.13,.17)))
scene.include("worker", person)

# Sparse straw flecks on the near bedding, intentionally restrained.
debris = Asset("Scattered bedding straw")
for i in range(25):
    x = random.uniform(-5.4, 4.4)
    y = random.uniform(-3.55, -1.4)
    length = random.uniform(.08, .23)
    debris.include("straw %02d" % i, rod(.008, start=(x,y,-.014),
        end=(x+length,y+random.uniform(-.08,.08),-.012), color=straw))
scene.include("bedding flecks", debris)

realize(scene)

# Cool indoor light, soft ambient illumination, and material-specific finishes.
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
background.inputs["Color"].default_value = (.65, .72, .80, 1)
background.inputs["Strength"].default_value = .45

# SceneAct materials are identified through their base color, preserving the
# shared palette and keeping the equipment distinctly metallic.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    col = bsdf.inputs["Base Color"].default_value
    if sum(abs(col[i] - metal[i]) for i in range(3)) < .07:
        bsdf.inputs["Metallic"].default_value = .7
        bsdf.inputs["Roughness"].default_value = .28
    elif sum(abs(col[i] - .18) for i in range(3)) < .10:
        bsdf.inputs["Roughness"].default_value = .25
    else:
        bsdf.inputs["Roughness"].default_value = .82

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((0, -1, 7), power=1700, size=8, target=(0, 0, 0),
             color=(.80, .87, 1.0))
area_emitter((-5, 2, 5), power=850, size=6, target=(0, 0, .5),
             color=(.9, .93, 1.0))

# Preserve the photograph's 512:285 aspect for the projection check.
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# These are approximate visible feature correspondences; overlap makes the
# individual stall and cow correspondences uncertain.
landmarks = [
    ("door upper left", (-2.81, 4.25, 1.875), (.32, .03)),
    ("right column at wall base", (3.55, 4.12, 1.38), (.91, .22)),
    ("front bed curb center", (0, BED_FRONT, BED_TOP), (.48, .78)),
    ("middle divider top", (0, -.90, 1.48), (.53, .26)),
    ("foreground cow rump", (1.35, -.56, .90), (.51, .51)),
]
def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result = []
    for name, p, ref in landmarks:
        clip = proj @ cam.matrix_world.inverted() @ Vector((*p, 1))
        uv = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
        result.append((name, ref, uv))
    return result

initial = projections()
print("Landmark reference versus initial projection:")
for name, ref, uv in initial:
    print(name, "reference", ref, "projected", uv)

# A conservative correction addresses only a shared gross vertical displacement.
# Keep the camera position and scene geometry fixed, and reject trials that push
# a previously visible landmark out of frame or worsen a matching background.
valid = [(ref, uv) for _, ref, uv in initial if uv is not None]
if len(valid) == len(landmarks):
    errors = [ref[1]-uv[1] for ref, uv in valid]
    if all(e > .12 for e in errors) or all(e < -.12 for e in errors):
        old_rotation = sc.camera.rotation_euler.copy()
        adjustment = .12 if errors[0] > 0 else -.12
        trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1],
                               CAMERA_TARGET[2] + adjustment))
        sc.camera.rotation_euler = (trial_target - sc.camera.location).to_track_quat('-Z', 'Y').to_euler()
        trial = projections()
        acceptable = True
        for (_, ref, before), (_, _, after) in zip(initial, trial):
            if after is None or (0 <= before[0] <= 1 and not -.05 <= after[0] <= 1.05):
                acceptable = False
            elif abs(ref[1]-before[1]) < .08 and abs(ref[1]-after[1]) > .10:
                acceptable = False
        old_error = sum(abs(ref[1]-uv[1]) for _, ref, uv in initial)
        new_error = sum(abs(ref[1]-uv[1]) for _, ref, uv in trial if uv is not None)
        if not acceptable or new_error >= old_error:
            sc.camera.rotation_euler = old_rotation

print("Final active camera landmark projections:")
for name, ref, uv in projections():
    print(name, "reference", ref, "projected", uv)
