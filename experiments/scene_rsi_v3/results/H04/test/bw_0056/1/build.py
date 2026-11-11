# Reference inventory, approximate normalized image bounds:
# Foreground operator: (0.17, 0.00)-(0.68, 1.00), hairnet and profile at
# top, white coat below, raised sleeve and hand overlapping the HMI.
# Background worker: (0.00, 0.15)-(0.21, 1.00), white coat, hairnet,
# glasses and hands at waist; partly obscured by foreground operator.
# HMI: (0.62, 0.06)-(0.80, 0.46), slanted light screen and metallic frame.
# Machine: (0.42, 0.38)-(1.00, 1.00), dark central mechanisms, transparent
# guards, stainless rails and pale conveyor extending toward lower right.
# Room: light walls, ceiling panels and grid; little floor is visible.
# The belt edges converge toward the rear; the HMI sides rise to the right.
# Internal machine details behind the operator and guards remain uncertain.
#
# Comparison against the second render, estimated from the visible images:
# - Foreground head/hairnet: reference x=.24-.42, y=0-.20; render roughly
#   x=.11-.27, y=.43-.65. The render is much too low and left. Its torso
#   also lacks the reference's long, broad coat silhouette.
# - Background worker: reference x=0-.21, y=.15-1; absent in the render.
# - Screen: reference x=.62-.80, y=.06-.46; render x=.62-.80, y=.23-.55.
#   Its horizontal placement is close, but it is low.
# - Foreground belt: reference approximately x=.55-.84, y=.81-1; render
#   x=.60-.95, y=.76-1. It is somewhat too far right and its front is cropped.
# - Background ceiling: reference panels at y=.05-.28; render ceiling grid
#   dominates y=0-.34, while an unsupported gray opening fills the left.
# - Reference machine contains a prominent dark center and gaps below the HMI;
#   rendered machinery is pale and lacks contrast. Guard rails overlap it.
#
# Ranked image-supported corrections:
# 1. Raise and shift the foreground person right; increase coat height and
#    place the reaching hand on the screen. These are local asset changes.
# 2. Extend the rear wall laterally and reposition the background worker into
#    the left opening, eliminating the unsupported gray area.
# 3. Lower camera height and aim slightly downward. This should move stationary
#    architecture and machine features upward, with a larger effect nearby.
#    The projection table below compares the prior camera and proposed camera;
#    it prints actual point projections, distinct from the observed contours.
# 4. Raise the HMI locally; shift the conveyor slightly left and shorten its
#    visible near end. Add dark open mechanical layers and preserve guard gaps.
# Brightness depends on lighting and orientation as well as base colors; the
# render is washed out, so illumination is restrained while dark parts remain.
#
# Expanded primitive estimate: architecture 53, machine 95, HMI 8, foreground
# person 19, background person 17, total approximately 192 meshes. Boxes,
# balls and rods each count once; no booleans, fillets or nested tube paths.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Cleanroom packaging line")

# Camera and major dimensions are independent.
OLD_CAM_POS = (0.0, -7.0, 2.10)
OLD_CAM_TARGET = (0.0, 1.0, 2.03)
CAM_POS = (0.0, -7.0, 1.75)
CAM_TARGET = (0.0, 1.0, 1.86)
CAM_LENS = 42.0
ROOM_W, ROOM_D, ROOM_H = 15.0, 16.0, 3.35
LINE_X = 1.02
BELT_W = 1.08
BELT_FRONT, BELT_BACK, BELT_Z = -1.85, 5.2, .88

coat = (.82, .91, .89)
wall = (.66, .79, .77)
steel = (.36, .48, .47)
steel_light = (.58, .69, .67)
darksteel = (.075, .13, .13)
black = (.025, .045, .045)
skin = (.70, .47, .37)
hairnet = (.54, .72, .70)
glass = (.53, .77, .75)

def B(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def R(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

def E(parent, name, center, radii, color):
    obj = ball(1, center=center, color=color)
    obj.resize(radii, pivot=center)
    parent.include(name, obj)

room = Asset("Cleanroom architecture")
B(room, "floor", (ROOM_W, ROOM_D, .08), (0, 1, -.05), (.60, .73, .70))
B(room, "back wall", (ROOM_W, .08, ROOM_H), (0, 8.0, ROOM_H/2), wall)
B(room, "right wall", (.08, ROOM_D, ROOM_H), (4.5, 1, ROOM_H/2),
  (.70, .82, .80))
B(room, "ceiling", (ROOM_W, ROOM_D, .08), (0, 1, ROOM_H), (.72, .83, .81))
for x in (-6, -4.5, -3, -1.5, 0, 1.5, 3, 4.5, 6):
    B(room, "ceiling longitudinal %.1f" % x, (.022, 15.8, .02),
      (x, 1, ROOM_H-.05), (.52, .67, .65))
for y in (-4, -2, 0, 2, 4, 6, 7.9):
    B(room, "ceiling cross %.1f" % y, (14.9, .022, .02),
      (0, y, ROOM_H-.05), (.52, .67, .65))
for x in (-5.25, -3.75, -2.25, -.75, .75, 2.25, 3.75):
    for y in (-3, -1, 1, 3, 5, 7):
        B(room, "light panel %.2f %.2f" % (x, y), (1.05, 1.13, .025),
          (x, y, ROOM_H-.065), (.93, .98, .96))
for x in (-3, -1, 1, 3):
    B(room, "floor seam x %.1f" % x, (.012, 15.8, .004),
      (x, 1, -.008), (.50, .65, .63))
for y in (-2, 0, 2, 4, 6):
    B(room, "floor seam y %.1f" % y, (14.9, .012, .004),
      (0, y, -.007), (.50, .65, .63))
scene.include("architecture", room)

machine = Asset("Stainless packaging machine")
B(machine, "lower enclosure", (1.55, 4.55, .40),
  (LINE_X, 1.15, .40), (.48, .60, .58))
B(machine, "front fascia", (1.55, .05, .36),
  (LINE_X, -1.13, .41), (.60, .70, .68))
B(machine, "nameplate", (.34, .012, .10),
  (LINE_X+.42, -1.163, .48), (.82, .88, .85))
B(machine, "nameplate stripe", (.17, .01, .012),
  (LINE_X+.42, -1.172, .49), darksteel)

mid = (BELT_FRONT + BELT_BACK)/2
length = BELT_BACK - BELT_FRONT
B(machine, "conveyor bed", (BELT_W+.12, length, .10),
  (LINE_X, mid, BELT_Z-.06), darksteel)
B(machine, "light conveyor belt", (BELT_W, length, .035),
  (LINE_X, mid, BELT_Z), (.80, .89, .85))
for x in (LINE_X-BELT_W/2-.04, LINE_X+BELT_W/2+.04):
    B(machine, "belt edge %.2f" % x, (.055, length, .105),
      (x, mid, BELT_Z+.035), steel)
    B(machine, "raised guide %.2f" % x, (.035, 4.6, .035),
      (x, 1.6, 1.12), steel_light)
    for y in (-.25, 1.0, 2.25, 3.5):
        R(machine, "guide support %.2f %.2f" % (x, y),
          (x, y, .92), (x, y, 1.12), .016, steel)
for i, y in enumerate((.0, .65, 1.30, 1.95, 2.60, 3.25, 3.90)):
    B(machine, "waiting tray %d" % i, (.62, .39, .028),
      (LINE_X, y, BELT_Z+.035), (.72, .82, .70))
    B(machine, "tray contents %d" % i, (.50, .27, .018),
      (LINE_X, y, BELT_Z+.057), (.65, .76, .59))

for x in (LINE_X-.83, LINE_X+.83):
    for y in (-1.0, .35, 1.75, 3.20):
        B(machine, "guard post %.2f %.2f" % (x, y), (.055, .055, 1.02),
          (x, y, 1.39), steel_light)
    B(machine, "guard top rail %.2f" % x, (.055, 4.26, .055),
      (x, 1.10, 1.91), steel_light)
    B(machine, "guard lower rail %.2f" % x, (.045, 4.26, .045),
      (x, 1.10, 1.02), steel)
    for j, (y0, y1) in enumerate(((-.97, .32), (.38, 1.72), (1.78, 3.17))):
        B(machine, "clear side panel %.2f %d" % (x, j),
          (.012, y1-y0, .85), (x, (y0+y1)/2, 1.45), glass, .10)
for y in (-1.0, .35, 1.75, 3.2):
    B(machine, "guard crossbar %.2f" % y, (1.69, .055, .055),
      (LINE_X, y, 1.91), steel_light)
B(machine, "front guard pane", (1.61, .012, .85),
  (LINE_X, -1.01, 1.45), glass, .08)

# Mechanical layers retain visible openings and repeated actuators.
B(machine, "dark rear head", (1.15, .76, .55),
  (LINE_X, 2.28, 1.68), (.035, .065, .065))
B(machine, "upper head plate", (1.43, 1.05, .075),
  (LINE_X, 2.27, 1.98), steel)
B(machine, "lower head plate", (1.38, 1.05, .075),
  (LINE_X, 2.27, 1.36), steel)
B(machine, "dark open lower mechanism", (1.12, .55, .16),
  (LINE_X, 1.83, 1.24), (.035, .065, .065))
for x in (LINE_X-.47, LINE_X-.16, LINE_X+.16, LINE_X+.47):
    R(machine, "pneumatic cylinder %.2f" % x,
      (x, 1.77, 1.57), (x, 1.77, 1.91), .047, steel_light)
    R(machine, "piston %.2f" % x,
      (x, 1.77, 1.35), (x, 1.77, 1.57), .019, steel)
for z in (1.40, 1.57, 1.78):
    R(machine, "cross linkage %.2f" % z,
      (LINE_X-.61, 1.70, z), (LINE_X+.61, 1.70, z), .022, darksteel)
for y in (.10, .8, 2.95, 3.35):
    B(machine, "machine cross rail %.2f" % y, (1.47, .07, .065),
      (LINE_X, y, 1.01), steel)
for i, x in enumerate((2.0, 2.45, 2.86, 3.27)):
    B(machine, "right upright %d" % i, (.09, .11, .63),
      (x, -1.15, .72), steel)
    B(machine, "right cap %d" % i, (.13, .14, .06),
      (x, -1.15, 1.06), black)
    B(machine, "right foot %d" % i, (.18, .23, .10),
      (x, -1.15, .36), darksteel)
scene.include("packaging machine", machine)

hmi = Asset("Articulated touchscreen")
R(hmi, "support mast", (1.75, .75, 1.83), (1.75, .75, 2.65), .065, darksteel)
R(hmi, "support elbow", (1.75, .75, 2.65), (1.45, .35, 2.85), .060, steel)
E(hmi, "hinge", (1.75, .75, 2.65), (.10, .10, .10), darksteel)
panel_center = (1.20, .20, 2.73)
panel = box((.74, .085, 1.19), center=panel_center, color=(.31, .44, .43))
panel.turn(axis="+y", degrees=20, pivot=panel_center)
hmi.include("screen metal rim", panel)
screen_center = (1.20, .148, 2.73)
display = box((.62, .018, 1.04), center=screen_center, color=(.74, .89, .90))
display.turn(axis="+y", degrees=20, pivot=screen_center)
hmi.include("screen face", display)
inside_center = (1.20, .135, 2.75)
inside = box((.46, .008, .79), center=inside_center, color=(.86, .95, .94))
inside.turn(axis="+y", degrees=20, pivot=inside_center)
hmi.include("display interior", inside)
scene.include("HMI", hmi)

# Foreground operator has a long coat and a profile oriented toward the HMI.
person = Asset("Foreground operator")
B(person, "coat body", (.77, .37, 1.34), (-.65, -3.05, 1.30), coat)
E(person, "coat shoulders", (-.65, -3.05, 1.96), (.40, .23, .24), coat)
B(person, "coat skirt", (.82, .39, .84), (-.65, -3.05, .54), (.80, .90, .88))
B(person, "coat front seam", (.016, .012, 1.0), (-.37, -3.25, 1.10),
  (.67, .78, .76))
E(person, "neck", (-.63, -3.05, 2.14), (.11, .10, .13), skin)
E(person, "head", (-.58, -3.05, 2.32), (.15, .13, .21), skin)
E(person, "profile", (-.46, -3.06, 2.32), (.07, .10, .12), skin)
E(person, "nose", (-.39, -3.08, 2.35), (.045, .045, .037), skin)
E(person, "hairnet", (-.66, -3.02, 2.47), (.19, .16, .15), hairnet)
R(person, "hairnet edge", (-.83, -3.12, 2.43),
  (-.54, -3.12, 2.40), .015, (.73, .85, .82))
R(person, "upper sleeve", (-.32, -3.02, 1.98), (.06, -2.91, 1.95), .14, coat)
E(person, "elbow", (.06, -2.91, 1.95), (.14, .14, .14), coat)
R(person, "forearm sleeve", (.06, -2.91, 1.95), (.54, -2.15, 2.25), .105, coat)
E(person, "cuff", (.54, -2.15, 2.25), (.11, .10, .08), (.86, .94, .92))
R(person, "extended hand", (.55, -2.15, 2.25), (.88, .08, 2.65), .045, skin)
E(person, "fingertips", (.88, .08, 2.65), (.065, .055, .06), skin)
R(person, "lower sleeve", (-.98, -3.05, 1.88), (-1.0, -3.05, 1.20), .10, coat)
scene.include("foreground operator", person)

worker = Asset("Background operator")
B(worker, "coat body", (.62, .32, 1.03), (-2.20, -.25, 1.02), coat)
E(worker, "shoulders", (-2.20, -.25, 1.48), (.34, .19, .20), coat)
B(worker, "coat skirt", (.68, .34, .55), (-2.20, -.25, .53), (.80, .90, .88))
for side in (-1, 1):
    E(worker, "trouser leg %d" % side, (-2.20+side*.13, -.25, .22),
      (.12, .13, .25), (.10, .16, .15))
E(worker, "head", (-2.20, -.26, 1.78), (.14, .12, .19), skin)
E(worker, "hairnet", (-2.20, -.25, 1.91), (.16, .14, .12), hairnet)
R(worker, "glasses", (-2.32, -.385, 1.80), (-2.08, -.385, 1.80), .012, darksteel)
R(worker, "left upper sleeve", (-2.46, -.27, 1.40), (-2.47, -.34, 1.09), .09, coat)
R(worker, "left forearm", (-2.47, -.34, 1.09), (-2.18, -.41, 1.00), .075, coat)
R(worker, "right upper sleeve", (-1.94, -.27, 1.40), (-1.94, -.34, 1.10), .09, coat)
R(worker, "right forearm", (-1.94, -.34, 1.10), (-2.13, -.41, 1.00), .075, coat)
E(worker, "hands", (-2.15, -.42, 1.00), (.10, .06, .06), skin)
scene.include("background worker", worker)

realize(scene)
set_view(OLD_CAM_POS, OLD_CAM_TARGET, lens=CAM_LENS, sensor=36)
sc = bpy.context.scene
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100

# Fixed world landmarks are actual points on the new geometry. The reference
# estimates are visual correspondences and do not prove visibility or fit.
landmarks = [
    ("screen top", (1.0, .20, 3.29), (.74, .06)),
    ("belt front left", (LINE_X-BELT_W/2, BELT_FRONT, BELT_Z), (.56, .84)),
    ("head top", (LINE_X, 2.27, 2.02), (.55, .38)),
    ("background ceiling panel", (-2.775, 4.435, ROOM_H-.065), (.25, .16)),
    ("foreground hairnet top", (-.66, -3.02, 2.62), (.32, .01)),
]

def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    mat = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    values = []
    for label, point, ref in landmarks:
        clip = mat @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        values.append((label, ref, uv))
    return values

old_values = projections()
cam = sc.camera
cam.location = CAM_POS
cam.rotation_euler = (Vector(CAM_TARGET)-cam.location).to_track_quat("-Z", "Y").to_euler()
new_values = projections()
print("landmark | reference | prior camera | proposed camera")
for old, new in zip(old_values, new_values):
    def fmt(v):
        return None if v is None else tuple(round(a, 3) for a in v)
    print(old[0], old[1], fmt(old[2]), fmt(new[2]))

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
background.inputs["Color"].default_value = (.68, .82, .79, 1)
background.inputs["Strength"].default_value = .38

area_emitter((-1, -3, 3.15), power=350, size=4.0,
             target=(-.5, 0, 1.2), color=(.88, 1.0, .97))
area_emitter((1, 1, 3.15), power=450, size=4.0,
             target=(1, 1, 1), color=(.88, 1.0, .98))
area_emitter((-2, 5, 3.15), power=350, size=3.5,
             target=(0, 2, 1), color=(.86, .98, 1.0))

for mat in bpy.data.materials:
    if mat.use_nodes:
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Roughness"].default_value = .45

sc.camera.data.dof.use_dof = True
sc.camera.data.dof.focus_distance = 4.1
sc.camera.data.dof.aperture_fstop = 11.0
sc.render.image_settings.file_format = "PNG"
