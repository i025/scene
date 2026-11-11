# Reference inventory, approximate normalized image bounds:
# - Foreground operator (0.17, 0.00)-(0.68, 1.00): white coat, hairnet,
#   side-profile face and raised sleeve; hand overlaps the screen.
# - Background worker (0.00, 0.14)-(0.21, 1.00): white coat, hairnet,
#   glasses, hands together and dark trousers.
# - Touchscreen (0.62, 0.06)-(0.80, 0.46): tall pale display with a
#   sloping silver frame and an articulated support behind it.
# - Conveyor and guarded machine (0.42, 0.34)-(1.00, 1.00): belt extends
#   toward lower right; glass guard, dark mechanisms, posts and rails overlap.
# - Background: pale cleanroom walls and a ceiling grid with bright panels.
#   Floor, the equipment's rear, and mechanisms behind the guard are uncertain.
#
# Comparison with the supplied previous render:
# - Foreground operator: reference spans approximately x=.17-.68 and full
#   height; rendered figure is approximately x=.31-.43, y=.40-.72. It is
#   much too small and does not overlap the screen.
# - Foreground belt end: reference is near (.70,.95); rendered belt is near
#   (.44,.67). The entire line occupies too small a portion of the image.
# - HMI top: reference approximately (.76,.07); rendered approximately
#   (.57,.32). Its apparent scale and position are both too small.
# - Background worker: reference approximately x=.00-.21, y=.14-1.00;
#   rendered figure is near x=.38-.43, y=.42-.70.
# - Ceiling/background: reference fills the frame; the render exposes the
#   outside of a room box and a large gray surround. The reference's screen
#   rises to the right, while the rendered panel is almost upright.
#
# Largest corrections: (1) move the camera inside the room and closer to the
# operator and line, expanding all foreground contours and removing the room
# exterior; (2) separately place the operator left and the HMI right so the
# raised hand reaches the screen; (3) put the second worker farther left and
# back; (4) reduce the guard's height and increase the contrast of the visible
# machinery. Camera target and lens are independent of asset positions.
# The camera trial below prints projections for a small aim adjustment before
# restoring the selected camera. Computed points are not visible-bound tests.
#
# Expanded primitive estimate: room 35; machine, belt and guard 75; HMI 9;
# two staff 47; total approximately 166 meshes. No booleans or fillet boxes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Cleanroom packaging line")

# Camera and principal dimensions are deliberately independent.
CAMERA_POSITION = (0.0, -3.75, 1.65)
CAMERA_TARGET = (0.05, 1.0, 1.60)
CAMERA_LENS = 35
ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT = 8.0, 11.0, 3.0
OP_X, OP_Y = -0.86, -0.48
MACHINE_X = 0.95
BELT_WIDTH = 0.90
BELT_FRONT, BELT_BACK, BELT_Z = -1.55, 3.8, 0.81

white = (0.87, 0.94, 0.92)
coat = (0.83, 0.91, 0.89)
coat_shadow = (0.70, 0.81, 0.79)
wall = (0.70, 0.83, 0.81)
ceiling = (0.67, 0.81, 0.79)
floor = (0.63, 0.76, 0.73)
steel = (0.42, 0.53, 0.52)
steel_light = (0.64, 0.75, 0.73)
darksteel = (0.15, 0.23, 0.23)
black = (0.035, 0.060, 0.058)
belt = (0.83, 0.91, 0.88)
glass = (0.56, 0.78, 0.76)
skin = (0.70, 0.48, 0.37)
hairnet = (0.54, 0.72, 0.70)

def bx(parent, name, size, center, color, opacity=1.0):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def rd(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def ell(parent, name, center, dimensions, color):
    obj = ball(radius=0.5, center=center, color=color)
    obj.resize(dimensions)
    parent.include(name, obj)

# Open room shell: the camera is inside the room.
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
    bx(room, "ceiling_length_seam_%d" % i, (.018, 10.8, .012),
       (x, 1.5, 2.941), steel_light)
for i, y in enumerate((-3, -1, 1, 3, 5, 6.7)):
    bx(room, "ceiling_cross_seam_%d" % i, (7.8, .018, .012),
       (0, y, 2.94), steel_light)
for i, x in enumerate((-2.25, -.75, .75, 2.25)):
    for j, y in enumerate((-2.0, 0, 2.0, 4.0, 6.0)):
        bx(room, "ceiling_light_%d_%d" % (i, j), (.95, .72, .018),
           (x, y, 2.925), (0.96, 1.0, .98))
for i, x in enumerate((-2, 0, 2)):
    bx(room, "floor_seam_%d" % i, (.012, 10.8, .004),
       (x, 1.5, .002), (0.53, .68, .65))
scene.include("architecture", room)

# Conveyor and a separate, legible assembly of visible machine parts.
machine = Asset("stainless_packaging_machine")
belt_len = BELT_BACK - BELT_FRONT
belt_mid = (BELT_BACK + BELT_FRONT) / 2
bx(machine, "machine_body", (1.55, 3.6, .48),
   (MACHINE_X, 1.65, .38), (.53, .65, .63))
bx(machine, "belt_bed", (BELT_WIDTH+.20, belt_len, .13),
   (MACHINE_X, belt_mid, BELT_Z-.09), darksteel)
bx(machine, "belt_surface", (BELT_WIDTH, belt_len, .045),
   (MACHINE_X, belt_mid, BELT_Z), belt)
for side in (-1, 1):
    x = MACHINE_X + side*(BELT_WIDTH/2+.07)
    bx(machine, "belt_side_%d" % side, (.065, belt_len, .14),
       (x, belt_mid, BELT_Z), steel)
    bx(machine, "guide_rail_%d" % side, (.032, 4.4, .04),
       (x-side*.07, 1.05, BELT_Z+.13), steel_light)
    for i, y in enumerate((-.9, .2, 1.3, 2.4, 3.3)):
        bx(machine, "guide_bracket_%d_%d" % (side, i), (.045, .045, .18),
           (x, y, BELT_Z+.08), steel)
for i, y in enumerate((-.8, .0, .8, 1.6, 2.4, 3.2)):
    bx(machine, "tray_%d" % i, (.59, .35, .025),
       (MACHINE_X, y, BELT_Z+.04), (.75, .84, .78))

# The enclosure is low in the foreground and surrounds the working area.
guard = Part("transparent_guard")
for side in (-1, 1):
    x = MACHINE_X + side*.82
    for i, y in enumerate((-.15, 1.15, 2.45, 3.5)):
        bx(guard, "upright_%d_%d" % (side, i), (.045, .045, .87),
           (x, y, 1.20), steel_light)
    for z in (.78, 1.62):
        bx(guard, "long_frame_%d_%s" % (side, str(z)), (.045, 3.70, .045),
           (x, 1.67, z), steel_light)
    bx(guard, "clear_side_%d" % side, (.012, 3.60, .79),
       (x, 1.67, 1.20), glass, .10)
for i, y in enumerate((-.15, 3.5)):
    for z in (.78, 1.62):
        bx(guard, "cross_frame_%d_%s" % (i, str(z)), (1.68, .045, .045),
           (MACHINE_X, y, z), steel_light)
    bx(guard, "clear_end_%d" % i, (1.60, .012, .78),
       (MACHINE_X, y, 1.20), glass, .08)
machine.include("guard_enclosure", guard)

# Dark openings and horizontal machine structures are more important than
# tiny fasteners at this image size.
mech = Part("working_mechanisms")
bx(mech, "back_housing", (1.26, .85, .72),
   (MACHINE_X, 2.55, 1.28), darksteel)
bx(mech, "upper_housing", (1.22, .72, .15),
   (MACHINE_X, 2.40, 1.68), black)
bx(mech, "working_plate", (1.30, .68, .08),
   (MACHINE_X, 1.75, 1.10), steel)
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

# HMI: portrait screen, inclined to match the diagonal reference silhouette.
hmi = Asset("articulated_touchscreen")
rd(hmi, "column", (1.42, 1.0, 1.3), (1.42, 1.0, 1.91), .065, darksteel)
rd(hmi, "support_arm", (1.42, 1.0, 1.88), (1.27, .43, 2.05), .06, steel)
ell(hmi, "arm_pivot", (1.27, .43, 2.05), (.17, .17, .17), darksteel)
panel = Part("tilted_panel")
bx(panel, "panel_back", (.63, .10, .95), (1.10, .18, 2.16), steel)
bx(panel, "panel_bezel", (.59, .025, .90), (1.10, .117, 2.16), darksteel)
bx(panel, "display", (.49, .014, .79), (1.10, .097, 2.16), (.76, .88, .90))
panel.turn(axis="y", degrees=18, pivot=(1.10, .18, 2.16))
hmi.include("panel", panel)
scene.include("hmi", hmi)

# A simple side-facing foreground figure, with broad rounded coat volumes.
operator = Asset("foreground_operator")
x, y = OP_X, OP_Y
ell(operator, "coat_lower", (x, y, .70), (.69, .43, 1.05), coat)
ell(operator, "coat_torso", (x+.02, y, 1.37), (.65, .42, .85), white)
ell(operator, "shoulder", (x+.16, y, 1.63), (.49, .43, .39), white)
rd(operator, "neck", (x+.10, y, 1.68), (x+.10, y, 1.82), .09, skin)
ell(operator, "head", (x+.13, y, 1.93), (.29, .27, .37), skin)
ell(operator, "profile_nose", (x+.30, y-.015, 1.94), (.11, .11, .08), skin)
ell(operator, "hairnet", (x+.04, y+.02, 2.08), (.43, .36, .29), hairnet)
rd(operator, "hairnet_edge", (x-.14, y-.17, 2.04),
   (x+.18, y-.17, 2.04), .013, white)
# The hand ends at the display's left edge.
rd(operator, "upper_raised_sleeve", (x+.20, y-.02, 1.61),
   (x+.55, y-.01, 1.55), .155, white)
rd(operator, "forearm_sleeve", (x+.55, y-.01, 1.55),
   (.56, .02, 1.96), .12, white)
rd(operator, "touching_hand", (.56, .02, 1.96),
   (.72, .07, 2.08), .052, skin)
rd(operator, "far_sleeve", (x-.20, y+.03, 1.58),
   (x-.22, y+.04, 1.07), .12, coat)
scene.include("foreground_operator", operator)

# Background worker stands behind and left of the main operator.
worker = Asset("background_worker")
wx, wy = -2.00, 2.15
for side in (-1, 1):
    bx(worker, "trouser_%d" % side, (.15, .17, .54),
       (wx+side*.10, wy, .28), black)
    bx(worker, "shoe_%d" % side, (.18, .26, .09),
       (wx+side*.10, wy-.04, .055), black)
ell(worker, "coat_skirt", (wx, wy, .78), (.62, .34, .94), coat)
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

# SceneAct colors remain the source of the material palette.
for ob in bpy.data.objects:
    if ob.type == "MESH":
        for polygon in ob.data.polygons:
            if ob.name.startswith(("Ball", "Rod")):
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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .86, .83, 1)
background.inputs["Strength"].default_value = .45

# Original 512:341 aspect ratio; the external runner handles final output.
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100

landmarks = [
    ("operator hairnet top", (OP_X+.04, OP_Y+.02, 2.225), (.32, .00)),
    ("screen upper edge", (1.23, .18, 2.61), (.76, .06)),
    ("near belt end", (MACHINE_X, BELT_FRONT, BELT_Z), (.68, .94)),
    ("background ceiling light", (-1.275, 1.64, 2.925), (.27, .12)),
]

def print_projections(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    print(label, "| reference | projected")
    for name, point, ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*point, 1))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        print(name, ref, None if uv is None else tuple(round(v, 3) for v in uv))

# Check a small upward aim trial and restore the chosen camera. The projected
# stationary landmarks should move down in the image for the upward trial.
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
print_projections("selected camera")
set_view(CAMERA_POSITION,
         (CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2]+.10),
         lens=CAMERA_LENS)
print_projections("upward aim trial")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
print_projections("restored camera")

area_emitter((-1.2, -1.0, 2.85), power=450, size=4.0,
             target=(0, 1, 1), color=(.85, 1.0, .96))
area_emitter((1.5, 2.5, 2.85), power=450, size=4.0,
             target=(.7, 1.5, .8), color=(.84, .98, .97))
area_emitter((-2.5, 4.5, 2.85), power=300, size=3.0,
             target=(-1, 2, 1), color=(.87, 1.0, .98))

cam = sc.camera
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector(CAMERA_POSITION) -
                               Vector((OP_X, OP_Y, 1.45))).length
cam.data.dof.aperture_fstop = 8.0
