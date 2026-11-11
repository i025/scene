# Reference inventory and comparison with the second rendered view:
# - Foreground cow: reference approximately (.35,.38)-(.84,.89); rendered
#   individual cows occupy only about .10-.15 of image width and sit around
#   y=.50-.76. The reference animal is substantially larger and its head and
#   folded legs are visible; the render shows mostly rounded rumps.
# - Door: reference approximately (.32,.04)-(.43,.19); rendered approximately
#   (.43,.25)-(.51,.46). The top-left correspondence remains uncertain because
#   the reference door's upper frame meets the image crop.
# - Platform edge: reference crosses the left edge near y=.58 and the bottom
#   near x=.68; rendered crosses left near y=.58 and exits right near y=.97.
#   The exact physical point on this long cropped edge is uncertain.
# - Divider bend: reference approximately (.84,.28); previous computed
#   correspondence (.642,.491), although overlapping rails make identity
#   uncertain. Rails cross in front of animals in both images.
# - Worker: reference is cropped at the right edge, around (.95,.13)-(1,.43);
#   the worker is outside the second rendered crop.
# The platform edge and rail runs slope down to the right. The second render
# has broad empty foreground and orderly gaps between small, circular animals;
# the photograph has overlapping, elongated bodies and more layered railwork.
# Brightness differences also depend on illumination and surface orientation.
#
# Ranked corrections: (1) camera framing and animal scale, (2) animal
# silhouettes and coat distribution, (3) door and worker placement.
# Trial a longer lens, aiming a little lower and toward the right: the door
# should move left and up while the foreground subjects expand. The cow-back
# point is the protected anchor; its projection and the uncertain edge and
# divider points are checked before choosing the camera. A compromise is
# expected because the reference correspondences do not uniquely calibrate
# the camera. A local door adjustment is deliberately avoided.
# Cows are elongated in their own long-axis direction about each animal's
# center; the trial and final landmark positions are recomputed below. This
# should reveal more flank and reduce the circular rump silhouette while the
# door anchor remains fixed. Procedural coat shading supplies irregular broad
# black and white regions without making a grid of raised circular patches.
#
# Expanded primitive estimate: architecture 23; 9 dividers * 10 plus 3
# continuous rails = 93; 7 cows * 14 = 98; worker 7; bedding 25.
# Total approximately 246 meshes, with no Boolean operations.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Modern dairy free stall barn")

STALL_SPACING = 1.28
PLATFORM_FRONT = -1.65
PLATFORM_BACK = 2.05
PLATFORM_TOP = .18
COW_LENGTH = 1.15

OLD_POSITION = (8.3, -12.8, 4.8)
OLD_TARGET = (0.0, .25, 1.08)
OLD_LENS = 53
TRIAL_POSITION = OLD_POSITION
TRIAL_TARGET = (.35, .25, .96)
TRIAL_LENS = 61
FINAL_POSITION = OLD_POSITION
FINAL_TARGET = (.65, .25, .84)
FINAL_LENS = 69

concrete = (.40, .41, .40)
walkway = (.29, .28, .23)
steel = (.51, .56, .58)
wall = (.46, .48, .48)
upper = (.73, .76, .77)
cow_white = (.72, .71, .65)
cow_black = (.025, .030, .027)
pink = (.46, .32, .29)
blue = (.025, .075, .17)

architecture = Asset("Barn architecture")
architecture.include("walkway", box((19, 12, .14),
    center=(0, 0, -.09), color=walkway))
architecture.include("raised concrete resting platform", box((15, 3.7, .26),
    center=(0, (PLATFORM_FRONT + PLATFORM_BACK)/2, .05), color=concrete))
architecture.include("front concrete fascia", box((15, .10, .27),
    center=(0, PLATFORM_FRONT, .04), color=(.30, .31, .30)))
architecture.include("rear concrete wall", box((19, .16, 2.6),
    center=(0, 3.65, 1.30), color=wall))
architecture.include("upper light wall", box((19, .18, 1.55),
    center=(0, 3.65, 3.22), color=upper))
architecture.include("blue metal door", box((1.35, .10, 1.95),
    center=(-2.55, 3.52, 1.05), color=blue))
architecture.include("door recessed panel", box((1.17, .04, 1.60),
    center=(-2.55, 3.44, 1.04), color=(.035, .10, .21)))
for i, x in enumerate((-8, -5.6, -3.22, -.5, 2.3, 5.3, 8.2)):
    architecture.include("blue wall column %d" % i, box((.11, .22, 4.0),
        center=(x, 3.48, 2), color=(.045, .13, .24)))
for i, x in enumerate((-7, -5, -3, -1, 1, 3, 5, 7)):
    architecture.include("upper wall seam %d" % i, box((.025, .03, 1.55),
        center=(x, 3.53, 3.22), color=(.43, .46, .47)))
scene.include("architecture", architecture)

rails = Asset("Galvanized free stall dividers")
for i in range(9):
    x = (i - 3.5) * STALL_SPACING
    stall = Asset("Divider %02d" % i)
    points = [(x, 1.78, 1.48), (x, .30, 1.48), (x, -.16, 1.46),
              (x, -.39, 1.39), (x, -.48, 1.27), (x, -.47, 1.12),
              (x, -.35, 1.02), (x, -.12, .94), (x, 1.48, .78)]
    for j in range(len(points)-1):
        stall.include("loop segment %d" % j,
            rod(.038, start=points[j], end=points[j+1], color=steel))
    stall.include("front support", rod(.045, start=(x, -.48, .18),
        end=(x, -.48, 1.24), color=steel))
    stall.include("rear support", rod(.042, start=(x, 1.77, .18),
        end=(x, 1.77, 1.48), color=steel))
    rails.include("stall %02d" % i, stall)
for k, y in enumerate((1.72, 2.12, 2.50)):
    rails.include("continuous rail %d" % k, rod(.033,
        start=(-6.3, y, 1.50+k*.08), end=(6.8, y, 1.50+k*.08),
        color=steel))
scene.include("stall equipment", rails)

def ellipsoid(center, scale, color):
    n = ball(1, center=center, color=color)
    n.resize(scale, pivot=center)
    return n

def make_cow(name, x, y, s, variant):
    a = Asset(name)
    def E(part, dx, dy, z, sx, sy, sz, color):
        # The length factor acts about this animal's (x,y) center.
        center = (x + dx*s, y + dy*s*COW_LENGTH, PLATFORM_TOP + z*s)
        a.include(part, ellipsoid(center,
            (sx*s, sy*s*COW_LENGTH, sz*s), color))

    coat = cow_black if variant in (1, 3) else cow_white
    E("barrel", 0, 0, .43, .53, .94, .40, coat)
    E("rump", 0, -.64, .39, .50, .40, .35, coat)
    E("shoulder", 0, .57, .43, .46, .42, .34, coat)
    E("neck", .06, .84, .47, .32, .43, .30, cow_black)
    E("head", .12, 1.15, .46, .26, .34, .23, cow_black)
    E("muzzle", .12, 1.42, .39, .20, .15, .12, pink)
    E("wet nose", .12, 1.52, .40, .17, .085, .075, (.11, .10, .09))
    E("left ear", -.15, 1.10, .61, .17, .16, .065, cow_black)
    E("right ear", .37, 1.10, .61, .17, .16, .065, cow_black)
    E("folded rear leg", -.25, -.68, .16, .26, .34, .13, cow_white)
    E("folded foreleg", .23, .62, .15, .23, .36, .12, cow_white)
    E("udder", .13, -.44, .17, .23, .29, .14, pink)
    a.include("tail", rod(.028*s,
        start=(x, y-.92*s*COW_LENGTH, PLATFORM_TOP+.33*s),
        end=(x+.17*s, y-1.28*s*COW_LENGTH, PLATFORM_TOP+.10*s),
        color=(.20, .18, .14)))
    return a

cows = Asset("Resting Holstein cows")
cow_positions = [(-5.20, -.02, .91), (-3.95, -.02, .91),
                 (-2.68, .04, .94), (-1.38, .02, .96),
                 (-.06, .00, 1.00), (1.23, .12, .98),
                 (2.53, .38, .96)]
for i, (x, y, s) in enumerate(cow_positions):
    cows.include("cow %d" % (i+1),
        make_cow("Holstein %d" % (i+1), x, y, s, i))
scene.include("cows", cows)

bedding = Asset("Thin scattered bedding")
for i in range(25):
    x = random.uniform(-5.7, 5.7)
    y = random.uniform(-1.52, 1.95)
    bedding.include("straw %02d" % i, box((random.uniform(.08, .22), .018, .008),
        center=(x, y, .187),
        color=random.choice(((.42,.36,.23), (.52,.46,.30), (.30,.29,.22)))))
scene.include("bedding", bedding)

person = Asset("Barn worker")
px, py = 5.15, 2.95
person.include("torso", box((.40, .25, .60),
    center=(px, py, 1.35), color=(.08, .20, .37)))
person.include("head", ellipsoid((px, py, 1.83),
    (.14, .13, .18), (.49, .35, .27)))
person.include("hair", ellipsoid((px, py+.015, 1.95),
    (.14, .13, .09), (.12, .10, .09)))
for side in (-1, 1):
    person.include("leg %d" % side, rod(.085,
        start=(px+side*.10, py, 1.06),
        end=(px+side*.12, py, .43), color=(.08, .11, .15)))
    person.include("arm %d" % side, rod(.07,
        start=(px+side*.23, py, 1.54),
        end=(px+side*.29, py-.06, 1.15), color=(.08, .20, .37)))
scene.include("worker", person)

realize(scene)
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
background.inputs["Color"].default_value = (.70, .76, .82, 1)
background.inputs["Strength"].default_value = .48

# Shared irregular coat finish. Generated coordinates vary over each rounded
# body part; the threshold creates broad, noncircular dark markings.
for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    if abs(c[0]-steel[0]) < .015 and abs(c[1]-steel[1]) < .015:
        bsdf.inputs["Metallic"].default_value = .72
        bsdf.inputs["Roughness"].default_value = .26
    elif (abs(c[0]-cow_white[0]) < .012 and
          abs(c[1]-cow_white[1]) < .012 and
          abs(c[2]-cow_white[2]) < .012):
        bsdf.inputs["Roughness"].default_value = .85
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 3.4
        tex.inputs["Detail"].default_value = 3.0
        tex.inputs["Roughness"].default_value = .7
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = .43
        ramp.color_ramp.elements[0].color = (.025, .03, .027, 1)
        ramp.color_ramp.elements[1].position = .49
        ramp.color_ramp.elements[1].color = (.72, .71, .65, 1)
        links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    elif c[0] < .15 and c[1] < .15 and c[2] < .15:
        bsdf.inputs["Roughness"].default_value = .30
    else:
        bsdf.inputs["Roughness"].default_value = .83

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100

# These are the same reference estimates and world correspondences used in
# previous builds. The cow point is transformed about (-.06, 0, .61), the
# center of that cow's barrel. Its y offset changes with the length factor.
# These computed projections are not a visibility or silhouette test.
anchors = [
    ("platform edge", (1.5, PLATFORM_FRONT, PLATFORM_TOP), (.68, .98), .5),
    ("door top left", (-3.225, 3.43, 2.025), (.32, .04), 1.3),
    ("cow upper back", (-.06, -.05, .96), (.50, .46), 1.3),
    ("divider top", (1.92, -.16, 1.46), (.84, .28), .4),
]

def transformed_anchor(index, length):
    p = anchors[index][1]
    if index != 2:
        return p
    pivot = (-.06, 0.0, PLATFORM_TOP+.43)
    return (p[0], pivot[1]+(p[1]-pivot[1])*length, p[2])

def camera_state(position, target, lens, length):
    set_view(position, target, lens=lens)
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    result = []
    for i, (name, p, ref, weight) in enumerate(anchors):
        point = transformed_anchor(i, length)
        q = projection @ cam.matrix_world.inverted() @ Vector((*point, 1))
        result.append(None if q.w <= 1e-8 else
            (.5*(q.x/q.w+1), .5*(1-q.y/q.w)))
    return result

states = [
    (OLD_POSITION, OLD_TARGET, OLD_LENS, 1.0),
    (TRIAL_POSITION, TRIAL_TARGET, TRIAL_LENS, 1.075),
    (FINAL_POSITION, FINAL_TARGET, FINAL_LENS, COW_LENGTH),
]
projections = [camera_state(*state) for state in states]

def score(points):
    return sum(w*((p[0]-ref[0])**2 + (p[1]-ref[1])**2)
        for (_, _, ref, w), p in zip(anchors, points) if p is not None)

# Permit a limited cow-back regression in exchange for a much larger framing
# improvement. Reject the final camera if it overshoots the trial score or
# moves the protected anchor more than 25 pixels farther from its estimate.
def pixel_error(point, reference):
    return math.hypot((point[0]-reference[0])*512,
                      (point[1]-reference[1])*285)

old_error = pixel_error(projections[0][2], anchors[2][2])
eligible = [0]
for i in (1, 2):
    if (projections[i][2] is not None and
        pixel_error(projections[i][2], anchors[2][2]) <= old_error + 25):
        eligible.append(i)
chosen = min(eligible, key=lambda i: score(projections[i]))
# Geometry was built at final length; choose a camera independently while
# evaluating the final geometry point with that same length.
camera_state(states[chosen][0], states[chosen][1], states[chosen][2], COW_LENGTH)

for j, (name, point, ref, weight) in enumerate(anchors):
    old = projections[0][j]
    trial = projections[1][j]
    final = camera_state(states[chosen][0], states[chosen][1],
                         states[chosen][2], COW_LENGTH)[j]
    if old is None or trial is None or final is None:
        continue
    def residual(q):
        return (round((q[0]-ref[0])*512, 1),
                round((q[1]-ref[1])*285, 1))
    print("%s reference=%s previous=%s previous_residual_px=%s "
          "trial=%s trial_residual_px=%s final=%s final_residual_px=%s" %
          (name, ref, old, residual(old), trial, residual(trial),
           final, residual(final)))

area_emitter((0, -2, 7), power=1600, size=8,
    target=(0, 0, 0), color=(.82, .90, 1))
area_emitter((-5, 1, 5), power=700, size=6,
    target=(0, 0, 0), color=(.90, .94, 1))
