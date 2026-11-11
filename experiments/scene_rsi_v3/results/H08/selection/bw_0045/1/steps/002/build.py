from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory, normalized image coordinates, and comparison with step 1:
# - Background wall fills the top of the reference; its blue door is at roughly
#   (.32, 0)-(.43, .21). In the render, the door is around (.49,.21)-(.56,.36)
#   and the wall has exposed outer edges and a large empty region.
# - Closest cow: reference roughly (.35,.36)-(.83,.85); rendered cow group
#   occupies about (.29,.42)-(.66,.70), with individual cows much too small.
# - Front curb: reference runs from (0,.55) toward (.75,1); the rendered
#   platform is a small isolated island around (.12,.45)-(.73,.90).
# - Reference rail tops traverse nearly the full image, with long lines sloping
#   gently down to the right. In the render the row converges toward the upper
#   right, and the foreground contains too much empty floor.
# - The worker is clipped at the upper-right reference edge, not standing fully
#   visible against an exposed wall. Cow legs and the far ends of the stalls
#   are partly occluded.
# Largest differences: 1. camera direction, scale and crop; 2. stall row and
# cow silhouettes are too small; 3. wall and floor edges are overexposed.
# Correction: move CAMERA_POSITION to the opposite side of the row and closer,
# aim toward the middle stalls, and increase the lens. This should make the
# rows recede to image left, enlarge the nearest cow, and crop the platform and
# wall edges. The projection table below prints the prior camera, a small trial
# from the new camera, and the final camera; these numerical geometry points
# are not claims about visible silhouette bounds.
# Cows retain individual body, neck, head, folded legs, udder and patches.
# Divider loops overlap the cows and one another, with open spaces underneath.
# Expanded mesh estimate: architecture 15, dividers 80, cows 150, floor 20,
# worker 7: approximately 272 primitives, plus SceneAct markers.

scene = Scene("Modern dairy free-stall barn")

# Geometry and camera parameters are independent.
BED_LENGTH = 3.45
STALL_Y = [-3.1, -1.75, -.4, .95, 2.30, 3.65, 5.0]
CAMERA_POSITION = (-5.8, -8.4, 3.65)
CAMERA_TARGET = (-.05, -.05, .85)
CAMERA_LENS = 48

steel = (.56, .60, .59)
white = (.74, .72, .65)
black = (.022, .024, .021)
pink = (.42, .31, .29)
blue = (.025, .10, .24)
wall = (.43, .45, .45)
cladding = (.77, .79, .79)
floor = (.48, .49, .47)

def ell(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)
    return obj

def rail(parent, name, a, b, radius=.038, color=steel):
    parent.include(name, rod(radius, start=a, end=b, color=color))

# Extend the building and floor beyond the camera crop; the actual unseen
# envelope is uncertain. The visible door, wall seam and posts are retained.
arch = Asset("Barn architecture")
arch.include("alley floor", box((24, 24, .12), center=(0, 0, -.12),
                               color=(.32, .31, .27)))
arch.include("raised concrete beds",
             box((BED_LENGTH, 18, .24), center=(0, 1.2, .06), color=floor))
arch.include("front concrete curb",
             box((.15, 18, .29), center=(-1.76, 1.2, .07),
                 color=(.37, .38, .36)))
arch.include("lower concrete wall",
             box((24, .18, 1.50), center=(0, 6.25, .75), color=wall))
arch.include("upper white cladding",
             box((24, .16, 2.7), center=(0, 6.26, 2.85), color=cladding))
arch.include("door frame",
             box((1.50, .10, 2.20), center=(-2.35, 6.12, 1.10),
                 color=(.015, .055, .13)))
arch.include("blue metal door",
             box((1.32, .06, 2.02), center=(-2.35, 6.05, 1.10), color=blue))
for z in (.60, 1.55):
    arch.include("door recessed panel %.2f" % z,
                 box((1.15, .025, .78), center=(-2.35, 6.01, z),
                     color=(.025, .13, .29)))
for i, x in enumerate((-8, -5.0, -3.2, .8, 4.6, 8)):
    arch.include("blue wall post %d" % i,
                 box((.13, .20, 4.2), center=(x, 6.10, 2.1),
                     color=(.025, .11, .23)))
for i, x in enumerate((-7, -4, -1.1, 2.6, 5.8, 8.5)):
    arch.include("cladding seam %d" % i,
                 box((.015, .025, 2.7), center=(x, 6.15, 2.85),
                     color=(.59, .61, .60)))
scene.include("architecture", arch)

# Rounded horizontal dividers, open under their return bars. Their tubes extend
# along each cow while continuous rails tie the row together.
equipment = Asset("Galvanized stall equipment")
for i, y in enumerate(STALL_Y):
    divider = Part("divider %d" % i)
    points = [
        (-1.65, y, 1.31), (-1.48, y, 1.43),
        (-1.23, y, 1.48), (.95, y, 1.48),
        (1.35, y, 1.42), (1.49, y, 1.28),
        (1.49, y, .98), (1.38, y, .76),
        (1.18, y, .70), (.63, y, .84), (-.12, y, .92)
    ]
    for j in range(len(points)-1):
        rail(divider, "loop segment %d" % j, points[j], points[j+1], .039)
    rail(divider, "front upright", (1.43,y,.18), (1.43,y,1.38), .043)
    equipment.include("divider %d" % i, divider)
for j, x in enumerate((-1.45, 1.40)):
    rail(equipment, "continuous top rail %d" % j,
         (x,-4.5,1.48), (x,6.1,1.48), .035)
scene.include("stall equipment", equipment)

# Lower, fuller recumbent bodies. Some coats are predominantly black, as in the
# photo, instead of giving every animal the same small spots.
def make_cow(index, x, y, scale, dark=False):
    cow = Asset("Holstein cow %d" % index)
    def p(dx, dy, dz):
        return (x+dx*scale, y+dy*scale, .18+dz*scale)
    def e(name, dx,dy,dz, sx,sy,sz, color):
        return ell(cow, name, p(dx,dy,dz),
                   (sx*scale,sy*scale,sz*scale), color)

    coat = black if dark else white
    e("barrel", -.16, 0, .51, 1.02,.55,.45, coat)
    e("rounded rump", -.82, 0, .43, .43,.51,.37, coat)
    e("shoulder", .52, 0, .53, .45,.50,.39, coat)
    e("neck", .89, 0, .62, .43,.34,.32, black)
    e("head", 1.18,-.02,.65, .33,.27,.25, black)
    e("face blaze", 1.37,-.06,.62, .14,.24,.12, white)
    e("muzzle", 1.48,-.06,.57, .13,.19,.09, pink)
    e("near ear", 1.04,-.29,.78, .20,.12,.07, black)
    e("far ear", 1.03,.28,.78, .19,.10,.07, black)
    e("folded rear leg", -.72,-.40,.17, .44,.17,.15, coat)
    e("rear hoof", -1.02,-.44,.14, .16,.13,.085, (.13,.12,.11))
    e("folded front leg", .52,-.38,.18, .42,.16,.13, coat)
    e("front hoof", .80,-.39,.14, .15,.12,.08, (.13,.12,.11))
    e("udder", -.48,-.18,.16, .27,.23,.13, (.55,.40,.36))
    if dark:
        patches = [
            (-.73,-.41,.54,.28,.13,.25),
            (-.13,-.49,.48,.22,.08,.20),
            (.38,-.38,.74,.20,.15,.10)
        ]
        patchcol = white
    else:
        patches = [
            (-.68,-.39,.69,.27,.13,.18),
            (-.20,-.49,.60,.23,.09,.22),
            (.09,-.49,.64,.17,.08,.20),
            (.36,-.38,.78,.23,.13,.12),
            (-.53,.02,.93,.34,.27,.05),
            (.04,.02,.96,.28,.25,.05),
            (.46,-.12,.85,.20,.20,.06)
        ]
        patchcol = black
    for k, (dx,dy,dz,sx,sy,sz) in enumerate(patches):
        e("coat patch %d" % k, dx,dy,dz,sx,sy,sz,patchcol)
    rail(cow, "tail", p(-1.03,-.20,.35), p(-1.39,-.50,.025),
         .034*scale, (.23,.20,.16))
    scene.include("cow %d" % index, cow)

make_cow(1, -.05, -2.43, 1.07, False)
make_cow(2, -.22, -1.08, 1.02, True)
make_cow(3, -.35, .27, 1.00, False)
make_cow(4, -.42, 1.62, .97, True)
make_cow(5, -.48, 2.97, .94, False)
make_cow(6, -.53, 4.32, .90, False)

# Sparse low bedding and soiling. Major floor areas remain continuous.
marks = Asset("Bedding and soiled floor")
for i in range(24):
    x = -1.52 + ((i*37) % 292)/100.0
    y = -4.0 + ((i*79) % 960)/100.0
    ell(marks, "bed mark %02d" % i, (x,y,.186),
        (.07+(i%3)*.025, .04+(i%4)*.015, .009),
        (.39,.37,.29) if i%2 else (.46,.43,.33))
for i in range(8):
    ell(marks, "alley mark %02d" % i,
        (-2.1-(i%3)*.35, -4+i*1.25, -.054),
        (.30,.43,.007), (.27,.27,.22))
scene.include("floor marks", marks)

worker = Asset("Worker near back wall")
wx, wy = 5.0, 5.85
worker.include("left trouser leg", box((.17,.18,.72),
               center=(wx-.10,wy,.38), color=(.10,.12,.16)))
worker.include("right trouser leg", box((.17,.18,.72),
               center=(wx+.10,wy,.38), color=(.10,.12,.16)))
worker.include("blue work jacket", box((.50,.28,.62),
               center=(wx,wy,1.07), color=(.07,.18,.37)))
ell(worker, "head", (wx,wy,1.54), (.14,.13,.18), (.32,.23,.18))
ell(worker, "hair", (wx,wy,1.66), (.14,.13,.075), (.07,.06,.05))
rail(worker, "left arm", (wx-.21,wy,1.30), (wx-.36,wy-.10,.90),
     .085, (.07,.18,.37))
rail(worker, "right arm", (wx+.21,wy,1.30), (wx+.30,wy-.10,.91),
     .085, (.07,.18,.37))
scene.include("worker", worker)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100

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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (.70,.75,.80,1)
background.inputs["Strength"].default_value = .48

# Compare geometry projections before and after a small camera trial.
# These reference points are approximate and their visibility is not guaranteed.
landmarks = [
    ("door upper right", (-1.69,6.01,2.11), (.43,.04)),
    ("nearest divider top", (1.40,-3.10,1.48), (.72,.31)),
    ("near curb", (-1.76,-3.10,.215), (.12,.72)),
    ("nearest muzzle", (1.53,-2.49,.79), (.79,.55)),
]

def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print("Projection", label)
    for name, pt, ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*pt,1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, "reference", ref, "computed",
              None if uv is None else tuple(round(v,3) for v in uv))

set_view((6.8,-11.4,5.1), (0,.45,.72), lens=36, sensor=36)
projection_table("previous camera")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
projection_table("revised camera before trial")
cam = sc.camera
original_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1],
                       CAMERA_TARGET[2]+.12))
cam.rotation_euler = (trial_target - cam.location).to_track_quat('-Z','Y').to_euler()
projection_table("trial aim slightly upward")
cam.rotation_euler = original_rotation
projection_table("final restored revised camera")

area_emitter((0,-1,7.0), power=1400, size=8,
             target=(0,0,.4), color=(.80,.88,1))
area_emitter((-4,-4,4.5), power=500, size=6,
             target=(0,0,.5), color=(.87,.92,1))

# SceneAct shares finish materials. Select actual meshes by their assigned base
# color, then assign one copied material per selected surface family. Only the
# dedicated steel and muzzle colors use these finishes in this scene.
def customize_finish(color, label, metallic, roughness):
    selected = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for index, mat in enumerate(obj.data.materials):
            if not mat or not mat.use_nodes:
                continue
            bs = mat.node_tree.nodes.get("Principled BSDF")
            if bs is None:
                continue
            c = bs.inputs["Base Color"].default_value
            if sum(abs(c[k]-color[k]) for k in range(3)) < .025:
                selected.append((obj,index,mat))
    if not selected:
        print(label, "no matching mesh materials found")
        return
    source = selected[0][2]
    print(label, "source shared users", source.users)
    copy = source.copy()
    copy.name = label
    shader = copy.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    for obj, index, mat in selected:
        obj.data.materials[index] = copy
    print(label, "mesh count", len(selected), "assigned", copy.name,
          "metallic", shader.inputs["Metallic"].default_value,
          "roughness", shader.inputs["Roughness"].default_value)

customize_finish(steel, "stall galvanized steel", .72, .28)
customize_finish(pink, "cow moist muzzle", 0.0, .27)
customize_finish(floor, "rough concrete beds", 0.0, .86)
