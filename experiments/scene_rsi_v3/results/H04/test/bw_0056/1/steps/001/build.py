# Cleanroom packaging line reconstruction.
# Reference inventory and visual anchors, normalized image coordinates (x right, y down):
# - Foreground operator: roughly (0.17, 0.00)-(0.68, 1.00); white coat, hairnet,
#   side-profile face, raised arm reaching the HMI. Lower body is partly occluded.
# - Background operator: (0.00, 0.15)-(0.22, 1.00); white coat, hairnet, glasses,
#   hands held at waist. Legs and body partly cropped/occluded.
# - HMI: (0.62, 0.06)-(0.80, 0.47), tall tilted pale screen with metal rim;
#   its lower edge overlaps the machine and its left edge meets the operator's hand.
# - Packaging line: (0.43, 0.37)-(1.00, 1.00); dark mechanical center, metal frames,
#   transparent guards, pale belt running toward the foreground at lower right.
# - Conveyor: near end around (0.56, 0.82)-(0.84, 1.00), recedes toward (0.53, 0.68).
# - Room: bright ceiling panels across top and upper left, pale back/right walls,
#   very little floor visible. Horizontal architectural edges recede to the right.
# Major edge directions: HMI sides slope up to the right; belt sides converge toward
# the rear; ceiling grid and guard rails recede toward the center of the image.
# Uncertain: machine internals behind the operator and reflective guard, concealed
# legs, and exact products on the belt. Their geometry is kept schematic.
#
# Approximate expanded primitive count: room 35; machine and guard 100; HMI 12;
# two people 42; ceiling lights 15; total about 205 meshes. No fillet boxes,
# Boolean operations, or dense tube paths are used.

from sceneact import *
import bpy
import math
from mathutils import Vector

# Independent camera parameters and scene proportions, in meters.
CAMERA_POS = (3.55, -6.7, 2.35)
CAMERA_TARGET = (0.02, 1.65, 1.67)
CAMERA_LENS = 37
ROOM_W, ROOM_D, ROOM_H = 8.0, 12.0, 3.65
LINE_X = 1.05
BELT_WIDTH = 1.02
BELT_FRONT, BELT_BACK, BELT_Z = -1.8, 4.4, 0.91

scene = Scene("Cleanroom packaging line")
white = (0.82, 0.91, 0.89)
wall = (0.70, 0.82, 0.80)
floor = (0.61, 0.74, 0.72)
steel = (0.48, 0.59, 0.59)
darksteel = (0.12, 0.20, 0.20)
black = (0.035, 0.065, 0.065)
belt = (0.83, 0.90, 0.85)
glass = (0.54, 0.80, 0.79)
skin = (0.73, 0.51, 0.40)
hairnet = (0.64, 0.81, 0.79)
screen = (0.79, 0.94, 0.93)

def add_box(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def ellipsoid(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    parent.include(name, obj)

# Room is deliberately open on the camera side.
room = Asset("Cleanroom architecture")
add_box(room, "floor", (ROOM_W, ROOM_D, .10), (0, 2, -.08), floor)
add_box(room, "back wall", (ROOM_W, .10, ROOM_H), (0, 7.0, ROOM_H/2), wall)
add_box(room, "right wall", (.10, ROOM_D, ROOM_H), (3.95, 2, ROOM_H/2), (0.75, .86, .84))
add_box(room, "ceiling", (ROOM_W, ROOM_D, .10), (0, 2, ROOM_H), (.77, .87, .85))
# A thin ceiling grid and luminous recessed panels define the room depth.
for x in (-3, -1.5, 0, 1.5, 3):
    add_box(room, "ceiling longitudinal %.1f" % x, (.025, 11.8, .018),
            (x, 2, ROOM_H-.065), (.59, .72, .70))
for y in (-2, 0, 2, 4, 6):
    add_box(room, "ceiling cross %.1f" % y, (7.9, .025, .018),
            (0, y, ROOM_H-.065), (.59, .72, .70))
for x in (-2.25, -.75, .75, 2.25):
    for y in (-1, 1, 3, 5):
        add_box(room, "recessed light %.1f %.1f" % (x, y), (1.12, 1.18, .022),
                (x, y, ROOM_H-.075), (1.0, 1.0, .97))
# restrained floor seams
for x in (-3, -1, 1, 3):
    add_box(room, "floor seam x %.1f" % x, (.012, 11.7, .004), (x, 2, -.026), (.48, .64, .62))
for y in (-2, 0, 2, 4, 6):
    add_box(room, "floor seam y %.1f" % y, (7.9, .012, .004), (0, y, -.025), (.48, .64, .62))
scene.include("room", room)

machine = Asset("Stainless packaging machine")
# Main lower casing and supporting frame.
add_box(machine, "main base", (1.75, 4.6, .63), (LINE_X, 1.25, .42), (.53, .65, .64))
add_box(machine, "front base fascia", (1.74, .07, .48), (LINE_X, -1.02, .46), (.67, .76, .74))
for x in (LINE_X-.78, LINE_X+.78):
    for y in (-.95, .65, 2.45, 3.48):
        add_box(machine, "frame post %.2f %.2f" % (x, y), (.085, .085, 1.55),
                (x, y, 1.12), steel)
        add_box(machine, "foot %.2f %.2f" % (x, y), (.14, .14, .15), (x, y, .075), darksteel)
    add_box(machine, "lower long rail %.2f" % x, (.08, 4.55, .10), (x, 1.25, .81), steel)
    add_box(machine, "upper long rail %.2f" % x, (.07, 4.55, .07), (x, 1.25, 1.84), steel)
for y in (-.95, .65, 2.45, 3.48):
    add_box(machine, "upper cross rail %.2f" % y, (1.62, .07, .07),
            (LINE_X, y, 1.84), steel)

# Conveyor extends toward the camera through the machine.
belt_mid = (BELT_FRONT + BELT_BACK)/2
belt_len = BELT_BACK - BELT_FRONT
add_box(machine, "belt bed", (BELT_WIDTH, belt_len, .11), (LINE_X, belt_mid, BELT_Z-.06), darksteel)
add_box(machine, "pale conveyor belt", (BELT_WIDTH-.07, belt_len, .035),
        (LINE_X, belt_mid, BELT_Z+.01), belt)
for x in (LINE_X-.57, LINE_X+.57):
    add_box(machine, "conveyor edge rail %.2f" % x, (.065, belt_len+.1, .12),
            (x, belt_mid, BELT_Z+.045), steel)
    add_box(machine, "upper guide %.2f" % x, (.035, 4.7, .035),
            (x, 1.5, 1.19), steel)
    for y in (-.8, .5, 1.8, 3.1):
        add_rod(machine, "guide support %.2f %.2f" % (x, y),
                (x, y, .96), (x, y, 1.19), .018, darksteel)
# Low, pale waiting trays, spaced down the belt.
for i, y in enumerate((.05, .70, 1.35, 2.0, 2.65, 3.30)):
    add_box(machine, "product tray %02d" % i, (.65, .38, .035),
            (LINE_X, y, BELT_Z+.045), (.73, .83, .72))
    add_box(machine, "product insert %02d" % i, (.51, .27, .022),
            (LINE_X, y, BELT_Z+.075), (.70, .79, .61))

# Visible machine head: dark recess, shafts, crossbars, actuator array.
add_box(machine, "dark central machine head", (1.18, 1.15, .63),
        (LINE_X, 2.15, 1.46), (.10, .17, .17))
add_box(machine, "head top plate", (1.48, 1.23, .09),
        (LINE_X, 2.15, 1.81), steel)
add_box(machine, "head lower plate", (1.37, 1.0, .09),
        (LINE_X, 2.15, 1.17), steel)
for x in (LINE_X-.45, LINE_X-.15, LINE_X+.15, LINE_X+.45):
    add_rod(machine, "vertical pneumatic cylinder %.2f" % x,
            (x, 1.65, 1.32), (x, 1.65, 1.75), .055, steel)
    add_rod(machine, "actuator piston %.2f" % x,
            (x, 1.65, 1.10), (x, 1.65, 1.32), .023, (.68, .76, .74))
for z in (1.25, 1.45, 1.65):
    add_rod(machine, "transverse linkage %.2f" % z,
            (LINE_X-.61, 1.57, z), (LINE_X+.61, 1.57, z), .022, darksteel)
for y in (.0, .55, 2.95, 3.35):
    add_box(machine, "machine crosspiece %.2f" % y, (1.50, .07, .075),
            (LINE_X, y, 1.03), steel)
# Transparent guard sheets, split into panels with visible gaps and metal frames.
for side in (-1, 1):
    x = LINE_X + side*.79
    for j, (y0, y1) in enumerate(((-.9, .60), (.70, 2.40), (2.50, 3.43))):
        add_box(machine, "clear side guard %d %d" % (side, j),
                (.012, y1-y0, .86), (x, (y0+y1)/2, 1.37), glass, opacity=.17)
for y in (-.91, 3.43):
    add_box(machine, "clear end guard %.2f" % y, (1.51, .012, .84),
            (LINE_X, y, 1.38), glass, opacity=.15)
add_box(machine, "small nameplate", (.27, .015, .10), (LINE_X+.48, -1.065, .54), (.83, .88, .85))
add_box(machine, "nameplate line", (.16, .008, .012), (LINE_X+.48, -1.075, .55), darksteel)
# Small foreground uprights and end equipment visible at the right.
for x in (LINE_X+.88, LINE_X+1.25, LINE_X+1.62):
    add_box(machine, "foreground upright %.2f" % x, (.10, .12, .57), (x, -1.35, .75), steel)
    add_box(machine, "black cap %.2f" % x, (.12, .14, .055), (x, -1.35, 1.055), black)
scene.include("packaging machine", machine)

# A screen as a thin framed rectangle in a plane tilted toward the operator.
# Using a common tilt makes the layered panel and display remain aligned.
hmi = Asset("Articulated HMI")
add_rod(hmi, "vertical arm", (1.76, 1.20, 1.73), (1.76, 1.20, 2.23), .07, darksteel)
add_rod(hmi, "diagonal arm", (1.76, 1.20, 2.23), (1.40, .93, 2.43), .065, steel)
ellipsoid(hmi, "hinge", (1.76, 1.20, 2.23), (.11, .11, .11), darksteel)
# Screen faces camera/left; front is toward negative Y.
panel_center = (1.33, .88, 2.38)
panel = box((.78, .10, 1.10), center=panel_center, color=(.50, .62, .61))
panel.turn(axis="+y", degrees=18, pivot=panel_center)
hmi.include("metal screen frame", panel)
front_center = (1.33, .817, 2.38)
display = box((.64, .018, .94), center=front_center, color=screen)
display.turn(axis="+y", degrees=18, pivot=front_center)
hmi.include("luminous screen face", display)
scene.include("HMI and support", hmi)

# Simplified people: coherent coat silhouettes and visible reaching arms.
def person(name, x, y, scale=1.0, operating=False):
    p = Asset(name)
    def P(dx, dy, z):
        return (x+dx*scale, y+dy*scale, z*scale)
    def E(label, center, dims, color):
        ellipsoid(p, label, P(*center), tuple(v*scale for v in dims), color)
    def R(label, a, b, r, color):
        add_rod(p, label, P(*a), P(*b), r*scale, color)
    # legs and shoes
    for side in (-1, 1):
        E("trouser leg %d" % side, (side*.13, 0, .31), (.115, .14, .34), (.16, .22, .21))
        E("shoe %d" % side, (side*.13, -.055, .045), (.14, .22, .07), (.09, .14, .14))
    E("long coat", (0, 0, .93), (.34, .22, .64), (.90, .95, .93))
    E("shoulders", (0, 0, 1.38), (.34, .21, .22), (.91, .96, .94))
    E("neck", (0, 0, 1.59), (.10, .095, .13), skin)
    E("head", (0, 0, 1.77), (.145, .13, .21), skin)
    E("hairnet cap", (-.025, .015, 1.89), (.16, .145, .13), hairnet)
    # nose projects right in the image
    E("nose", (.14, -.025, 1.79), (.055, .045, .045), skin)
    if operating:
        R("raised upper sleeve", (.20, -.01, 1.43), (.48, -.05, 1.39), .105, (.91, .96, .94))
        R("raised forearm sleeve", (.48, -.05, 1.39), (.72, .02, 1.62), .085, (.90, .95, .93))
        E("touching hand", (.76, .03, 1.65), (.085, .055, .06), skin)
        R("lower sleeve", (-.20, 0, 1.37), (-.23, -.04, 1.02), .10, (.88, .94, .92))
    else:
        R("left sleeve", (-.23, 0, 1.37), (-.24, -.08, 1.04), .09, (.89, .95, .93))
        R("right sleeve", (.23, 0, 1.37), (.25, -.11, 1.06), .09, (.89, .95, .93))
        R("left bent arm", (-.24, -.08, 1.04), (.02, -.16, .99), .075, (.89, .95, .93))
        R("right bent arm", (.25, -.11, 1.06), (.08, -.17, .99), .075, (.89, .95, .93))
        E("hands", (.05, -.18, 1.0), (.11, .07, .07), skin)
        R("glasses bridge", (-.12, -.123, 1.80), (.12, -.123, 1.80), .012, darksteel)
    scene.include(name, p)

person("foreground operator", -.78, .15, 1.35, True)
person("background worker", -2.15, 2.30, 1.0, False)

realize(scene)

# Camera and render setup are applied after realization because it clears Blender.
set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
sc = bpy.context.scene
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.70, .86, .84, 1)
background.inputs["Strength"].default_value = .7

area_emitter((0, -2, 3.5), power=700, size=5, target=(0, 1, 1), color=(.86, 1.0, .98))
area_emitter((-2, 3, 3.5), power=600, size=4, target=(0, 1, 1), color=(.88, 1.0, .98))
area_emitter((3, 3, 3.4), power=500, size=4, target=(1, 1, 1), color=(.82, .96, 1.0))

# Small reference-versus-projection table. Points lie on actual geometry; these
# tentative correspondences are visual estimates, not fitted calibration.
landmarks = [
    ("HMI top", (1.16, .88, 2.90), (.74, .06)),
    ("belt front left", (LINE_X-.50, BELT_FRONT, BELT_Z), (.56, .84)),
    ("machine head top", (LINE_X, 2.15, 1.855), (.55, .38)),
    ("background ceiling panel", (-.75, 5, ROOM_H-.075), (.25, .16)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
proj = cam.calc_matrix_camera(dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                              scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("landmark | reference (x,y) | projected (x,y)")
for label, point, ref in landmarks:
    clip = proj @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(label, ref, None if uv is None else tuple(round(v, 3) for v in uv))

# Apply broad material properties to the realized geometry.
for mat in bpy.data.materials:
    if mat.use_nodes:
        principled = mat.node_tree.nodes.get("Principled BSDF")
        if principled:
            principled.inputs["Roughness"].default_value = .48

sc.render.image_settings.file_format = "PNG"
sc.camera.data.dof.use_dof = False
