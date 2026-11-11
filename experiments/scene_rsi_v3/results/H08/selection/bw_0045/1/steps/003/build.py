from sceneact import *
import bpy
from mathutils import Vector

# Reference inventory and comparison with the second render, in normalized image
# coordinates. Estimates describe visible contours, not calibrated landmarks.
# Rear wall: reference fills the top with the blue door at approximately
# (.32, 0)-(.43, .20); render door is clipped at the left edge around
# (0, .10)-(.06, .35). The worker is at (.96, .12)-(1, .35) in the reference
# and around (.54, .11)-(.59, .32) in the render.
# Closest cow: reference about (.35, .36)-(.83, .85); render about
# (.52, .50)-(.90, .94). The render shows mostly rumps, while the reference
# shows a longer side profile, folded legs, neck and head.
# Curb: reference enters at (0, .55) and exits near (.75, 1); render enters
# around (.05, .61) and exits near (.42, 1). Rail tops in the reference are
# almost horizontal and overlap the cows; the rendered rails have a much
# steeper diagonal and the gaps look like a view down the ends of the stalls.
# Ranked corrections:
# 1. Rotate the camera toward the side of the row and lower its elevation.
#    This should make the cow bodies longer in image space, flatten the rail
#    and curb slopes, and reduce the top-down view of the beds.
# 2. Move the background door and worker along the wall independently: the
#    door should move right and the worker toward the right crop.
# 3. Increase the nearest cow's side-facing irregular dark patches and dirty
#    rump, and soften the simplified bodies and folded-leg silhouettes.
# The exposed bed and walking alley remain continuous. Far cows, limbs, and
# the full envelope of the barn are uncertain and partly occluded.
# Estimated expanded primitive meshes: architecture 21, rails 90, cows 144,
# floor marks 22, worker 7 = approximately 284, plus SceneAct markers.

scene = Scene("Modern dairy free-stall barn")

# Independent geometry and camera parameters.
BED_LENGTH = 3.45
STALL_Y = [-4.15, -2.80, -1.45, -.10, 1.25, 2.60, 3.95, 5.30]
CAMERA_POSITION = (-10.5, -5.0, 3.25)
CAMERA_TARGET = (0.0, -.05, .92)
CAMERA_LENS = 48
WALL_Y = 6.25
DOOR_X = -0.3
WORKER_X = 7.3

steel = (.57, .61, .60)
white = (.72, .70, .62)
black = (.018, .020, .018)
pink = (.42, .31, .29)
blue = (.025, .10, .24)
wall = (.40, .42, .42)
cladding = (.77, .79, .79)
concrete = (.47, .48, .46)
dirty = (.28, .27, .22)

def ell(parent, name, center, scale, color):
    node = ball(1, center=center, color=color)
    node.resize(scale, pivot=center)
    parent.include(name, node)
    return node

def rail(parent, name, a, b, radius=.038, color=steel):
    parent.include(name, rod(radius, start=a, end=b, color=color))

arch = Asset("Barn architecture")
arch.include("walking alley",
             box((26, 26, .12), center=(0, 0, -.12),
                 color=(.30, .29, .25)))
arch.include("raised concrete beds",
             box((BED_LENGTH, 20, .24), center=(0, 1, .06),
                 color=concrete))
arch.include("concrete curb",
             box((.15, 20, .29), center=(-1.76, 1, .07),
                 color=(.34, .35, .33)))
arch.include("lower concrete wall",
             box((28, .18, 1.50), center=(0, WALL_Y, .75), color=wall))
arch.include("upper white cladding",
             box((28, .16, 2.70), center=(0, WALL_Y+.01, 2.85),
                 color=cladding))
arch.include("door frame",
             box((1.50, .10, 2.20),
                 center=(DOOR_X, WALL_Y-.13, 1.10),
                 color=(.012, .045, .11)))
arch.include("blue metal door",
             box((1.32, .06, 2.02),
                 center=(DOOR_X, WALL_Y-.20, 1.10), color=blue))
for z in (.60, 1.55):
    arch.include("door panel %.2f" % z,
                 box((1.15, .025, .78),
                     center=(DOOR_X, WALL_Y-.24, z),
                     color=(.025, .13, .29)))
for i, x in enumerate((-9, -6, -3, 1.15, 4.6, 8, 11)):
    arch.include("blue wall post %d" % i,
                 box((.13, .20, 4.2), center=(x, WALL_Y-.15, 2.1),
                     color=(.025, .11, .23)))
for i, x in enumerate((-8, -5, -2, 2.8, 6.1, 9.5)):
    arch.include("cladding seam %d" % i,
                 box((.015, .025, 2.7),
                     center=(x, WALL_Y-.10, 2.85),
                     color=(.59, .61, .60)))
scene.include("architecture", arch)

# Repeated divider loops: long upper tube, rounded nose, lower return and post.
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
    rail(divider, "upright", (1.43, y, .18), (1.43, y, 1.38), .043)
    equipment.include("divider %d" % i, divider)
for j, x in enumerate((-1.45, 1.40)):
    rail(equipment, "continuous rail %d" % j,
         (x, -5.2, 1.48), (x, 6.2, 1.48), .035)
scene.include("stall equipment", equipment)

def make_cow(index, x, y, scale, dark=False):
    cow = Asset("Holstein cow %d" % index)
    def p(dx, dy, dz):
        return (x + dx*scale, y + dy*scale, .18 + dz*scale)
    def e(name, dx, dy, dz, sx, sy, sz, color):
        return ell(cow, name, p(dx,dy,dz),
                   (sx*scale, sy*scale, sz*scale), color)

    coat = black if dark else white
    e("barrel", -.16, 0, .51, 1.04, .55, .45, coat)
    e("rounded rump", -.82, 0, .43, .43, .51, .37, coat)
    e("shoulder", .52, 0, .53, .45, .50, .39, coat)
    e("black neck", .89, 0, .62, .43, .34, .32, black)
    e("head", 1.18, -.02, .65, .33, .27, .25, black)
    e("face blaze", 1.37, -.06, .62, .14, .24, .12, white)
    e("muzzle", 1.48, -.06, .57, .13, .19, .09, pink)
    e("near ear", 1.04, -.29, .78, .20, .12, .07, black)
    e("far ear", 1.03, .28, .78, .19, .10, .07, black)
    e("folded rear leg", -.72, -.40, .17, .44, .17, .15, coat)
    e("rear hoof", -1.02, -.44, .14, .16, .13, .085, (.13,.12,.11))
    e("folded front leg", .52, -.38, .18, .42, .16, .13, coat)
    e("front hoof", .80, -.39, .14, .15, .12, .08, (.13,.12,.11))
    e("udder", -.48, -.18, .16, .27, .23, .13, (.55,.40,.36))
    if dark:
        patches = [
            (-.73,-.41,.54,.28,.13,.25),
            (-.13,-.49,.48,.22,.08,.20),
            (.38,-.38,.74,.20,.15,.10)
        ]
        patch_color = white
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
        patch_color = black
    for k, (dx,dy,dz,sx,sy,sz) in enumerate(patches):
        e("coat patch %d" % k, dx,dy,dz,sx,sy,sz, patch_color)
    if index == 1:
        e("soiled rump", -.90, -.38, .40, .32, .13, .24, (.36,.34,.27))
    rail(cow, "tail", p(-1.03,-.20,.35), p(-1.39,-.50,.025),
         .034*scale, (.23,.20,.16))
    scene.include("cow %d" % index, cow)

make_cow(1, -.05, -3.47, 1.07, False)
make_cow(2, -.22, -2.12, 1.02, True)
make_cow(3, -.35, -.77, 1.00, False)
make_cow(4, -.42, .58, .97, True)
make_cow(5, -.48, 1.93, .94, False)
make_cow(6, -.53, 3.28, .92, False)
make_cow(7, -.53, 4.63, .90, True)

marks = Asset("Bedding and soiled floor")
for i in range(22):
    x = -1.52 + ((i*37) % 292)/100.0
    y = -4.9 + ((i*79) % 1030)/100.0
    ell(marks, "bed mark %02d" % i, (x, y, .186),
        (.07+(i%3)*.025, .04+(i%4)*.015, .009),
        (.39,.37,.29) if i % 2 else (.46,.43,.33))
scene.include("floor marks", marks)

worker = Asset("Worker near back wall")
wx, wy = WORKER_X, 5.85
worker.include("left trouser leg",
               box((.17,.18,.72), center=(wx-.10,wy,.38),
                   color=(.10,.12,.16)))
worker.include("right trouser leg",
               box((.17,.18,.72), center=(wx+.10,wy,.38),
                   color=(.10,.12,.16)))
worker.include("blue work jacket",
               box((.50,.28,.62), center=(wx,wy,1.07),
                   color=(.07,.18,.37)))
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

# Point projections are separate from the observed contour estimates above.
# Door position was changed, so its point is not the same physical point as
# in the earlier build. The trial checks a small change in the new camera aim.
landmarks = [
    ("door upper right", (DOOR_X+.66, WALL_Y-.24, 2.11), (.43,.04)),
    ("nearest divider top", (1.40,-4.15,1.48), (.72,.31)),
    ("near curb", (-1.76,-4.15,.215), (.12,.72)),
    ("nearest muzzle", (1.53,-3.53,.79), (.79,.55)),
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

set_view((-5.8,-8.4,3.65), (-.05,-.05,.85), lens=48, sensor=36)
projection_table("previous camera with current geometry")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
projection_table("revised camera")
cam = sc.camera
saved_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1],
                       CAMERA_TARGET[2]+.12))
cam.rotation_euler = (trial_target-cam.location).to_track_quat('-Z','Y').to_euler()
projection_table("trial upward aim")
cam.rotation_euler = saved_rotation
projection_table("final restored camera")

area_emitter((0,-1,7.0), power=1400, size=8,
             target=(0,0,.4), color=(.80,.88,1))
area_emitter((-4,-4,4.5), power=500, size=6,
             target=(0,0,.5), color=(.87,.92,1))

# Finish colors identify dedicated surface families in this scene. Copy each
# shared material before assigning shader changes to the matching mesh subset.
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
                selected.append((obj, index, mat))
    if not selected:
        print(label, "no matching mesh materials found")
        return
    source = selected[0][2]
    print(label, "source material users", source.users)
    copy = source.copy()
    copy.name = label
    shader = copy.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    for obj, index, mat in selected:
        obj.data.materials[index] = copy
    print(label, "mesh count", len(selected), "material", copy.name,
          "metallic", shader.inputs["Metallic"].default_value,
          "roughness", shader.inputs["Roughness"].default_value)

customize_finish(steel, "stall galvanized steel", .72, .28)
customize_finish(pink, "cow moist muzzle", 0.0, .27)
customize_finish(concrete, "rough concrete beds", 0.0, .86)
