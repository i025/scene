# Reference inventory, estimated normalized image bounds:
# Operator: x=.17-.68, y=0-1; side-facing head, white coat, raised arm
# overlapping the left edge of the HMI. Lower body is cropped.
# Background worker: x=0-.21, y=.14-1; coat, hairnet, glasses, joined hands.
# HMI: x=.62-.80, y=.06-.46; silver portrait panel leaning right at the top.
# Machine: x=.42-1, y=.34-1; dark central mechanism, stainless frame,
# transparent foreground guard and pale belt extending toward the lower right.
# Ceiling lights and seams occupy the upper background. The floor and the
# concealed interior of the machine are uncertain.
#
# Comparison with the previous full render:
# 1. Operator's head and hairnet appear around x=.18-.33, y=.22-.42,
#    versus reference x=.24-.42, y=0-.20. The coat also looks round and
#    shapeless. Move the operator forward and right, lengthen the upper body,
#    and raise the head; these changes move its top upward and enlarge it.
# 2. Background worker appears around x=.09-.20, y=.37-.91, versus
#    reference x=0-.21, y=.14-1. Move this figure forward and left to enlarge
#    its silhouette and raise its head in the image.
# 3. Rendered HMI is approximately x=.66-.87, y=.10-.49; reference is
#    x=.62-.80, y=.06-.46. Move the panel left and slightly up. Its top
#    already leans right, so preserve that edge direction.
# 4. Rendered conveyor fills much of the lower-right corner, whereas reference
#    belt is narrower, around x=.53-.82 near the bottom. Shift the machine
#    left and narrow the belt; this also moves its near endpoint left.
# 5. Rendered machine interiors are too pale and sparse, with large blank
#    areas. Add darker horizontal working surfaces, supports and actuators.
#    The render is also washed out; reduce illumination and give steel and
#    guard appropriate surface finishes. Brightness is affected by light and
#    orientation as well as material color.
# The background ceiling occupies roughly y=0-.30 in both images; retain
# the camera to avoid disturbing that alignment. Previous projection output
# placed the background light at (.259,.138), near its estimated (.27,.12).
# No camera change is made; the table below reports the selected geometry.
#
# Expanded primitive estimate: architecture 36, conveyor/guard/mechanisms 84,
# HMI 9, foreground operator 17, background worker 21: about 167 meshes.
# Each box, ball and rod emits one primitive; there are no Boolean operations.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Cleanroom packaging line")

CAMERA_POSITION = (0.0, -3.75, 1.65)
CAMERA_TARGET = (0.05, 1.0, 1.60)
CAMERA_LENS = 35
ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT = 8.0, 11.0, 3.0
MACHINE_X = 0.70
BELT_WIDTH = 0.72
BELT_FRONT, BELT_BACK, BELT_Z = -1.45, 3.8, 0.81
OP_X, OP_Y = -0.69, -0.92

white = (0.88, 0.94, 0.92)
coat = (0.81, 0.90, 0.88)
coat_shadow = (0.68, 0.79, 0.77)
wall = (0.66, 0.80, 0.78)
ceiling = (0.65, 0.80, 0.78)
floor = (0.60, 0.73, 0.71)
steel = (0.39, 0.51, 0.50)
steel_light = (0.61, 0.72, 0.71)
darksteel = (0.12, 0.20, 0.20)
black = (0.025, 0.045, 0.045)
belt_color = (0.82, 0.90, 0.87)
glass = (0.62, 0.83, 0.81)
skin = (0.68, 0.44, 0.34)
hairnet = (0.47, 0.68, 0.66)

def bx(parent, name, size, center, color, opacity=1.0):
    parent.include(name, box(size=size, center=center, color=color,
                             opacity=opacity))

def rd(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def ell(parent, name, center, dimensions, color):
    obj = ball(radius=0.5, center=center, color=color)
    obj.resize(dimensions)
    parent.include(name, obj)

room = Asset("cleanroom_architecture")
bx(room, "floor", (ROOM_WIDTH, ROOM_DEPTH, .10), (0, 1.5, -.06), floor)
bx(room, "back_wall", (ROOM_WIDTH, .10, ROOM_HEIGHT),
   (0, 6.95, ROOM_HEIGHT/2), wall)
bx(room, "right_wall", (.10, ROOM_DEPTH, ROOM_HEIGHT),
   (3.95, 1.5, ROOM_HEIGHT/2), wall)
bx(room, "left_wall", (.10, ROOM_DEPTH, ROOM_HEIGHT),
   (-3.95, 1.5, ROOM_HEIGHT/2), wall)
bx(room, "ceiling", (ROOM_WIDTH, ROOM_DEPTH, .10),
   (0, 1.5, ROOM_HEIGHT), ceiling)

for i, x in enumerate((-3.0, -1.5, 0, 1.5, 3.0)):
    bx(room, "ceiling_long_seam_%d" % i, (.018, 10.8, .012),
       (x, 1.5, 2.941), steel_light)
for i, y in enumerate((-3, -1, 1, 3, 5, 6.7)):
    bx(room, "ceiling_cross_seam_%d" % i, (7.8, .018, .012),
       (0, y, 2.94), steel_light)
for i, x in enumerate((-2.25, -.75, .75, 2.25)):
    for j, y in enumerate((-2.0, 0, 2.0, 4.0, 6.0)):
        bx(room, "ceiling_light_%d_%d" % (i, j), (.95, .72, .018),
           (x, y, 2.925), (.97, 1.0, .98))
for i, x in enumerate((-2, 0, 2)):
    bx(room, "floor_seam_%d" % i, (.012, 10.8, .004),
       (x, 1.5, .002), (.49, .65, .63))
scene.include("architecture", room)

machine = Asset("stainless_packaging_machine")
belt_len = BELT_BACK - BELT_FRONT
belt_mid = (BELT_BACK + BELT_FRONT) / 2
bx(machine, "machine_body", (1.55, 3.6, .48),
   (MACHINE_X, 1.65, .38), (.48, .60, .59))
bx(machine, "belt_bed", (BELT_WIDTH+.20, belt_len, .13),
   (MACHINE_X, belt_mid, BELT_Z-.09), darksteel)
bx(machine, "belt_surface", (BELT_WIDTH, belt_len, .045),
   (MACHINE_X, belt_mid, BELT_Z), belt_color)
for side in (-1, 1):
    x = MACHINE_X + side*(BELT_WIDTH/2+.07)
    bx(machine, "belt_side_%d" % side, (.065, belt_len, .14),
       (x, belt_mid, BELT_Z), steel)
    bx(machine, "guide_rail_%d" % side, (.032, 4.4, .04),
       (x-side*.06, 1.05, BELT_Z+.13), steel_light)
    for i, y in enumerate((-.9, .2, 1.3, 2.4, 3.3)):
        bx(machine, "guide_bracket_%d_%d" % (side, i), (.045, .045, .18),
           (x, y, BELT_Z+.08), steel)
for i, y in enumerate((-.8, .0, .8, 1.6, 2.4, 3.2)):
    bx(machine, "tray_%d" % i, (.50, .35, .025),
       (MACHINE_X, y, BELT_Z+.04), (.75, .84, .78))

guard = Part("transparent_guard")
for side in (-1, 1):
    x = MACHINE_X + side*.82
    for i, y in enumerate((-.15, 1.15, 2.45, 3.5)):
        bx(guard, "upright_%d_%d" % (side, i), (.045, .045, .87),
           (x, y, 1.20), steel_light)
    for z in (.78, 1.62):
        bx(guard, "long_frame_%d_%s" % (side, str(z)),
           (.045, 3.70, .045), (x, 1.67, z), steel_light)
    bx(guard, "clear_side_%d" % side, (.012, 3.60, .79),
       (x, 1.67, 1.20), glass, .08)
for i, y in enumerate((-.15, 3.5)):
    for z in (.78, 1.62):
        bx(guard, "cross_frame_%d_%s" % (i, str(z)), (1.68, .045, .045),
           (MACHINE_X, y, z), steel_light)
    bx(guard, "clear_end_%d" % i, (1.60, .012, .78),
       (MACHINE_X, y, 1.20), glass, .06)
machine.include("guard_enclosure", guard)

mech = Part("working_mechanisms")
bx(mech, "back_housing", (1.26, .85, .72),
   (MACHINE_X, 2.55, 1.28), darksteel)
bx(mech, "upper_housing", (1.22, .72, .15),
   (MACHINE_X, 2.40, 1.68), black)
bx(mech, "working_plate", (1.30, .68, .08),
   (MACHINE_X, 1.75, 1.10), steel)
bx(mech, "dark_lower_gap", (1.20, .50, .12),
   (MACHINE_X, 2.0, 1.00), black)
bx(mech, "upper_cross_member", (1.40, .13, .10),
   (MACHINE_X, 1.95, 1.54), darksteel)
for i, dx in enumerate((-.46, -.16, .16, .46)):
    x = MACHINE_X + dx
    rd(mech, "pneumatic_cylinder_%d" % i, (x, 1.75, 1.22),
       (x, 1.75, 1.58), .055, steel_light)
    rd(mech, "piston_%d" % i, (x, 1.75, 1.11),
       (x, 1.75, 1.23), .023, darksteel)
    bx(mech, "cylinder_mount_%d" % i, (.16, .14, .04),
       (x, 1.75, 1.60), steel)
for i, y in enumerate((.50, 1.0, 1.5, 2.0, 2.5)):
    rd(mech, "roller_%d" % i, (MACHINE_X-.62, y, .95),
       (MACHINE_X+.62, y, .95), .025, steel)
for side in (-1, 1):
    x = MACHINE_X+side*.68
    rd(mech, "longitudinal_guide_%d" % side, (x, .15, 1.02),
       (x, 3.20, 1.02), .025, steel)
    for j, y in enumerate((.5, 1.6, 2.7)):
        bx(mech, "guide_block_%d_%d" % (side, j), (.13, .15, .09),
           (x, y, 1.03), steel_light)
for i, y in enumerate((-1.25, -.65)):
    bx(mech, "foreground_post_%d" % i, (.09, .09, .66),
       (MACHINE_X+.84, y, .52), steel_light)
    bx(mech, "foreground_cap_%d" % i, (.15, .13, .055),
       (MACHINE_X+.84, y, .88), black)
    bx(mech, "nameplate_%d" % i, (.20, .012, .08),
       (MACHINE_X+.65, y-.06, 1.28), white)
machine.include("mechanisms", mech)
scene.include("machine", machine)

hmi = Asset("articulated_touchscreen")
rd(hmi, "column", (1.15, 1.0, 1.3), (1.15, 1.0, 1.96), .065, darksteel)
rd(hmi, "support_arm", (1.15, 1.0, 1.93), (1.02, .43, 2.10), .06, steel)
ell(hmi, "arm_pivot", (1.02, .43, 2.10), (.17, .17, .17), darksteel)
panel = Part("tilted_panel")
bx(panel, "panel_back", (.63, .10, .95), (.85, .18, 2.21), steel)
bx(panel, "panel_bezel", (.59, .025, .90), (.85, .117, 2.21), darksteel)
bx(panel, "display", (.49, .014, .79), (.85, .097, 2.21), (.76, .88, .90))
panel.turn(axis="y", degrees=18, pivot=(.85, .18, 2.21))
hmi.include("panel", panel)
scene.include("hmi", hmi)

operator = Asset("foreground_operator")
x, y = OP_X, OP_Y
# Separate torso and skirt make the coat less spherical while retaining soft
# shoulders. Its lower part is cropped by the camera, as in the reference.
bx(operator, "coat_lower", (.62, .40, 1.00), (x, y, .66), coat)
bx(operator, "coat_torso", (.62, .40, .76), (x+.02, y, 1.42), white)
ell(operator, "shoulder", (x+.12, y, 1.73), (.52, .43, .34), white)
rd(operator, "neck", (x+.10, y, 1.82), (x+.10, y, 1.98), .09, skin)
ell(operator, "head", (x+.13, y, 2.09), (.29, .27, .37), skin)
ell(operator, "profile_nose", (x+.30, y-.015, 2.10), (.11, .11, .08), skin)
ell(operator, "hairnet", (x+.04, y+.02, 2.24), (.43, .36, .29), hairnet)
rd(operator, "hairnet_edge", (x-.14, y-.17, 2.20),
   (x+.18, y-.17, 2.20), .013, white)
rd(operator, "upper_raised_sleeve", (x+.20, y-.02, 1.71),
   (x+.54, y-.01, 1.69), .15, white)
rd(operator, "forearm_sleeve", (x+.54, y-.01, 1.69),
   (.35, .02, 2.04), .12, white)
rd(operator, "touching_hand", (.35, .02, 2.04),
   (.51, .07, 2.16), .052, skin)
rd(operator, "far_sleeve", (x-.20, y+.03, 1.69),
   (x-.22, y+.04, 1.12), .12, coat)
bx(operator, "coat_hem_seam", (.58, .012, .015),
   (x, y-.207, .77), coat_shadow)
scene.include("foreground_operator", operator)

worker = Asset("background_worker")
wx, wy = -1.88, .78
for side in (-1, 1):
    bx(worker, "trouser_%d" % side, (.15, .17, .54),
       (wx+side*.10, wy, .28), black)
    bx(worker, "shoe_%d" % side, (.18, .26, .09),
       (wx+side*.10, wy-.04, .055), black)
bx(worker, "coat_skirt", (.58, .34, .94), (wx, wy, .78), coat)
ell(worker, "coat_torso", (wx, wy, 1.34), (.56, .33, .69), white)
rd(worker, "neck", (wx, wy, 1.63), (wx, wy, 1.73), .075, skin)
ell(worker, "face", (wx, wy-.02, 1.83), (.27, .24, .33), skin)
ell(worker, "hairnet", (wx, wy, 1.98), (.36, .30, .24), hairnet)
rd(worker, "glasses", (wx-.10, wy-.145, 1.86),
   (wx+.10, wy-.145, 1.86), .012, darksteel)
for side in (-1, 1):
    rd(worker, "upper_sleeve_%d" % side,
       (wx+side*.24, wy, 1.52), (wx+side*.27, wy-.07, 1.20), .11, coat)
    rd(worker, "fore_sleeve_%d" % side,
       (wx+side*.27, wy-.07, 1.20), (wx+side*.07, wy-.20, 1.13), .09, white)
    ell(worker, "hand_%d" % side,
        (wx+side*.06, wy-.21, 1.13), (.10, .10, .11), skin)
scene.include("background_worker", worker)

realize(scene)

for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name.startswith(("Ball", "Rod")):
        for polygon in ob.data.polygons:
            polygon.use_smooth = True

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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .86, .83, 1)
background.inputs["Strength"].default_value = .32

sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)

# The camera is unchanged from the previous successful render. Projections are
# numerical point checks; they are not tests of visible silhouette or occlusion.
landmarks = [
    ("operator hairnet top", (OP_X+.04, OP_Y+.02, 2.385), (.32, .00)),
    ("screen upper edge", (.98, .18, 2.66), (.76, .06)),
    ("near belt end", (MACHINE_X, BELT_FRONT, BELT_Z), (.68, .94)),
    ("background ceiling light", (-1.275, 1.64, 2.925), (.27, .12)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
matrix = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("landmark | reference estimate | projected")
for name, point, ref in landmarks:
    clip = matrix @ cam.matrix_world.inverted() @ Vector((*point, 1))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v, 3) for v in uv))

area_emitter((-1.2, -1.0, 2.85), power=300, size=4.0,
             target=(0, 1, 1), color=(.85, 1.0, .96))
area_emitter((1.5, 2.5, 2.85), power=300, size=4.0,
             target=(.7, 1.5, .8), color=(.84, .98, .97))
area_emitter((-2.5, 4.5, 2.85), power=220, size=3.0,
             target=(-1, 2, 1), color=(.87, 1.0, .98))

cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (
    Vector(CAMERA_POSITION) - Vector((OP_X, OP_Y, 1.55))
).length
cam.data.dof.aperture_fstop = 8.0
