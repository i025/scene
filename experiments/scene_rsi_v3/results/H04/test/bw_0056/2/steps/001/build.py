# Reference inventory and image anchors, estimated from the supplied 512 x 341 image:
# - Cleanroom: pale teal-white walls and ceiling throughout; ceiling panels at
#   approximately (0.18, 0.05)-(0.27, 0.12) and (0.62, 0.08)-(0.72, 0.15).
#   Floor is largely hidden by the workers and equipment.
# - Foreground operator: approximately (0.17, 0.00)-(0.68, 1.00), white coat,
#   hairnet and side-facing head; raised right arm overlaps the touchscreen.
# - Background worker: approximately (0.00, 0.14)-(0.21, 1.00), white coat,
#   hairnet, dark trousers, hands held together in front.
# - HMI: approximately (0.62, 0.06)-(0.80, 0.46), tall oblique pale screen
#   with a silver frame, attached to machinery behind it.
# - Packaging machine and transparent guard: approximately (0.42, 0.34)-(1, 1).
#   A pale belt enters from the lower right and recedes toward the center.
#   Dark internal gaps, horizontal rails, cylinders and framing remain visible.
# - Dominant edges: ceiling seams and conveyor rails converge toward the
#   background; HMI edges rise to the right. Guard frames are mostly vertical
#   and horizontal. The operator obscures much of the machine's left side.
# - Hidden parts, exact product shapes and mechanics behind guards are uncertain.
#
# Approximate expanded primitive count: architecture 26, machine and conveyor
# 95, HMI 13, foreground worker 25, background worker 22, total about 181.
# Each box, ball and rod is one SceneAct primitive. No boolean or fillet
# expansions are used.

from sceneact import *
import bpy
import math
from mathutils import Vector

# Independent camera and major-asset parameters.
CAMERA_POSITION = (4.9, -8.8, 2.6)
CAMERA_TARGET = (0.0, 1.05, 1.48)
CAMERA_LENS = 35
ROOM_WIDTH = 7.8
ROOM_DEPTH = 12.0
ROOM_HEIGHT = 3.15
MACHINE_X = 0.85
MACHINE_FRONT = -1.85
MACHINE_BACK = 3.65
BELT_WIDTH = 1.05
BELT_Z = 0.82
OPERATOR_X = -1.15
OPERATOR_Y = -0.30

scene = Scene("Cleanroom packaging line")

# Reusable palette. Values are deliberately cool and restrained.
wall = (0.73, 0.86, 0.84)
ceiling = (0.68, 0.82, 0.80)
floor_col = (0.60, 0.74, 0.72)
white = (0.90, 0.96, 0.94)
coat = (0.86, 0.94, 0.92)
coat_shadow = (0.73, 0.84, 0.82)
skin = (0.73, 0.52, 0.41)
hairnet = (0.60, 0.77, 0.75)
steel = (0.49, 0.59, 0.59)
steel_dark = (0.22, 0.31, 0.31)
black = (0.055, 0.09, 0.09)
belt_col = (0.81, 0.90, 0.86)
screen_col = (0.75, 0.88, 0.88)
glass_col = (0.52, 0.78, 0.77)

def add_box(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def add_ball(parent, name, radius, center, color, scale=None):
    obj = ball(radius=radius, center=center, color=color)
    if scale:
        obj.resize(scale)
    parent.include(name, obj)

# Room shell and recessed ceiling grid.
room = Asset("cleanroom_architecture")
add_box(room, "floor", (ROOM_WIDTH, ROOM_DEPTH, 0.12),
        (0, 2.0, -0.07), floor_col)
add_box(room, "back_wall", (ROOM_WIDTH, 0.12, ROOM_HEIGHT),
        (0, 7.9, ROOM_HEIGHT/2), wall)
add_box(room, "right_wall", (0.12, ROOM_DEPTH, ROOM_HEIGHT),
        (3.9, 2.0, ROOM_HEIGHT/2), wall)
add_box(room, "left_wall", (0.12, ROOM_DEPTH, ROOM_HEIGHT),
        (-3.9, 2.0, ROOM_HEIGHT/2), wall)
add_box(room, "ceiling", (ROOM_WIDTH, ROOM_DEPTH, 0.10),
        (0, 2.0, ROOM_HEIGHT), ceiling)
for i, x in enumerate((-3.0, -1.5, 0.0, 1.5, 3.0)):
    add_box(room, "ceiling_long_seam_%d" % i, (0.018, 11.8, 0.012),
            (x, 2.0, ROOM_HEIGHT-0.057), steel)
for i, y in enumerate((-3.0, -1.0, 1.0, 3.0, 5.0, 7.0)):
    add_box(room, "ceiling_cross_seam_%d" % i, (7.7, 0.018, 0.012),
            (0, y, ROOM_HEIGHT-0.058), steel)
for i, x in enumerate((-2.25, 0.75, 2.25)):
    for j, y in enumerate((-1.9, 0.1, 2.1, 4.1, 6.1)):
        add_box(room, "recessed_light_%d_%d" % (i, j),
                (1.00, 0.72, 0.025), (x, y, ROOM_HEIGHT-0.07), white)
for i, x in enumerate((-2.0, 0.0, 2.0)):
    add_box(room, "floor_seam_%d" % i, (0.012, 11.5, 0.004),
            (x, 2, 0.001), (0.48, 0.64, 0.62))
scene.include("architecture", room)

# Main stainless frame and the through conveyor.
machine = Asset("packaging_machine")
add_box(machine, "lower_machine_body", (1.65, 4.35, 0.53),
        (MACHINE_X, 1.05, 0.38), (0.56, 0.68, 0.67))
add_box(machine, "front_base", (1.72, 0.12, 0.58),
        (MACHINE_X, MACHINE_FRONT+0.2, 0.32), steel)
add_box(machine, "conveyor_bed", (BELT_WIDTH+0.20, 5.50, 0.15),
        (MACHINE_X, 0.90, BELT_Z-0.09), steel_dark)
add_box(machine, "conveyor_belt", (BELT_WIDTH, 5.42, 0.055),
        (MACHINE_X, 0.90, BELT_Z), belt_col)
for side in (-1, 1):
    x = MACHINE_X + side*(BELT_WIDTH/2+0.09)
    add_box(machine, "conveyor_side_%d" % side, (0.085, 5.55, 0.15),
            (x, 0.90, BELT_Z+0.015), steel)
    add_box(machine, "guide_rail_%d" % side, (0.035, 4.8, 0.045),
            (x-side*0.08, 1.0, BELT_Z+0.16), steel)
    for j, y in enumerate((-1.55, 0.05, 1.65, 3.05)):
        add_box(machine, "rail_support_%d_%d" % (side, j),
                (0.045, 0.045, 0.18), (x, y, BELT_Z+0.09), steel_dark)
# Trays are understated pale rectangles, distributed along the belt.
for i, y in enumerate((-1.3, -0.35, 0.60, 1.55, 2.50, 3.35)):
    add_box(machine, "product_tray_%d" % i, (0.66, 0.42, 0.026),
            (MACHINE_X, y, BELT_Z+0.046), (0.75, 0.84, 0.78))
    add_box(machine, "tray_inner_%d" % i, (0.54, 0.30, 0.010),
            (MACHINE_X, y, BELT_Z+0.065), (0.84, 0.91, 0.85))

# Framing, transparent guard, and visible internal mechanism.
for i, y in enumerate((-0.25, 1.05, 2.35, 3.45)):
    for side in (-1, 1):
        x = MACHINE_X + side*0.89
        add_box(machine, "guard_upright_%d_%d" % (i, side),
                (0.055, 0.055, 1.25), (x, y, 1.32), steel)
for side in (-1, 1):
    x = MACHINE_X + side*0.89
    for z in (0.76, 1.90):
        add_box(machine, "guard_long_frame_%d_%s" % (side, str(z)),
                (0.055, 3.78, 0.055), (x, 1.60, z), steel)
    add_box(machine, "clear_guard_side_%d" % side,
            (0.012, 3.65, 1.05), (x, 1.60, 1.34), glass_col, 0.13)
for i, y in enumerate((-0.25, 3.45)):
    for z in (0.76, 1.90):
        add_box(machine, "guard_cross_%d_%s" % (i, str(z)),
                (1.80, 0.055, 0.055), (MACHINE_X, y, z), steel)
    add_box(machine, "clear_guard_end_%d" % i,
            (1.70, 0.012, 1.05), (MACHINE_X, y, 1.34), glass_col, 0.10)
# Central dark machine module visible through enclosure.
add_box(machine, "rear_machine_housing", (1.15, 1.05, 0.80),
        (MACHINE_X, 2.15, 1.35), steel_dark)
add_box(machine, "upper_machine_head", (0.92, 0.65, 0.18),
        (MACHINE_X, 2.0, 1.80), black)
add_box(machine, "horizontal_working_plate", (1.45, 0.70, 0.10),
        (MACHINE_X, 1.35, 1.13), steel)
for i, xoff in enumerate((-0.52, -0.18, 0.18, 0.52)):
    x = MACHINE_X+xoff
    add_rod(machine, "actuator_body_%d" % i, (x, 1.30, 1.35),
            (x, 1.30, 1.73), 0.075, steel)
    add_rod(machine, "actuator_rod_%d" % i, (x, 1.30, 1.16),
            (x, 1.30, 1.36), 0.025, steel_dark)
    add_box(machine, "actuator_mount_%d" % i, (0.20, 0.18, 0.055),
            (x, 1.30, 1.77), steel)
for i, y in enumerate((0.48, 0.95, 1.42, 1.89, 2.36)):
    add_rod(machine, "transverse_roller_%d" % i,
            (MACHINE_X-0.68, y, 0.96),
            (MACHINE_X+0.68, y, 0.96), 0.035, steel)
for side in (-1, 1):
    x = MACHINE_X + side*0.73
    add_rod(machine, "long_guide_%d" % side, (x, 0.08, 1.05),
            (x, 3.15, 1.05), 0.025, steel_dark)
    for j, y in enumerate((0.5, 1.6, 2.7)):
        add_box(machine, "guide_block_%d_%d" % (side, j), (0.16, 0.18, 0.11),
                (x, y, 1.04), steel)
# Small plates and utility posts on the foreground right.
for i, y in enumerate((-1.65, -1.05)):
    add_box(machine, "foreground_post_%d" % i, (0.09, 0.09, 0.72),
            (MACHINE_X+0.95, y, 0.55), steel)
    add_box(machine, "post_cap_%d" % i, (0.15, 0.13, 0.055),
            (MACHINE_X+0.95, y, 0.94), black)
    add_box(machine, "nameplate_%d" % i, (0.25, 0.015, 0.10),
            (MACHINE_X+0.58, y-0.06, 1.28), white)
scene.include("machine", machine)

# HMI with a pivoting support arm. The panel is tilted toward the operator.
hmi = Asset("articulated_touchscreen")
add_rod(hmi, "mount_column", (1.42, 1.64, 1.32), (1.42, 1.64, 2.05), 0.085, steel_dark)
add_rod(hmi, "lower_arm", (1.42, 1.64, 2.02), (1.60, 1.05, 2.18), 0.07, steel)
add_ball(hmi, "elbow_joint", 0.11, (1.60, 1.05, 2.18), steel_dark)
add_rod(hmi, "upper_arm", (1.60, 1.05, 2.18), (1.12, 0.58, 2.35), 0.07, steel)
add_ball(hmi, "screen_pivot", 0.095, (1.12, 0.58, 2.35), steel_dark)
# Panel geometry is made as a single editable subtree, then tilted.
panel = Part("panel")
add_box(panel, "panel_back", (0.76, 0.10, 0.95), (1.02, 0.43, 2.40), steel)
add_box(panel, "dark_bezel", (0.70, 0.035, 0.89), (1.02, 0.365, 2.40), (0.29, 0.40, 0.43))
add_box(panel, "display", (0.59, 0.012, 0.77), (1.02, 0.341, 2.40), screen_col)
add_box(panel, "display_lower_strip", (0.54, 0.014, 0.035),
        (1.02, 0.331, 2.08), (0.57, 0.70, 0.73))
panel.turn(axis="y", degrees=12, pivot=(1.02, 0.43, 2.40))
hmi.include("tilted_hmi", panel)
scene.include("hmi", hmi)

# A readable low-detail human silhouette assembled from independent pieces.
def person(name, x, y, scale, operating=False):
    p = Asset(name)
    def point(a, b, c):
        return (x+a*scale, y+b*scale, c*scale)
    def b(n, size, pos, color):
        add_box(p, n, tuple(v*scale for v in size), point(*pos), color)
    def ballp(n, radius, pos, color, factors=None):
        add_ball(p, n, radius*scale, point(*pos), color, factors)
    def limb(n, a, bpos, radius, color):
        add_rod(p, n, point(*a), point(*bpos), radius*scale, color)
    # Feet, dark trousers and long white coat.
    for side in (-1, 1):
        b("trouser_%d" % side, (0.18, 0.20, 0.60),
          (side*0.13, 0, 0.31), black)
        b("shoe_%d" % side, (0.20, 0.30, 0.10),
          (side*0.13, -0.05, 0.07), black)
    b("coat_skirt", (0.62, 0.38, 0.74), (0, 0, 0.77), coat)
    b("coat_torso", (0.61, 0.36, 0.70), (0, 0, 1.36), white)
    b("coat_front_placket", (0.035, 0.012, 0.80),
      (0.07, -0.19, 1.17), coat_shadow)
    b("coat_pocket", (0.16, 0.012, 0.15), (-0.18, -0.198, 1.05), coat_shadow)
    limb("neck", (0, 0, 1.65), (0, 0, 1.77), 0.09, skin)
    ballp("head", 0.19, (0.02, -0.01, 1.88), skin, (0.82, 0.82, 1.20))
    ballp("hairnet_cap", 0.21, (-0.02, 0.025, 2.03), hairnet, (1.05, 0.90, 0.75))
    limb("hairnet_edge", (-0.18, -0.11, 1.99), (0.15, -0.11, 1.99), 0.018, white)
    if operating:
        # Raised arm stretches toward HMI; hand overlaps the left display edge.
        limb("raised_upper_sleeve", (0.25, 0, 1.57), (0.55, 0.12, 1.54), 0.15, white)
        limb("raised_fore_sleeve", (0.55, 0.12, 1.54), (0.97, 0.34, 1.83), 0.12, white)
        limb("touching_hand", (0.97, 0.34, 1.83), (1.11, 0.40, 1.91), 0.055, skin)
        limb("other_upper_sleeve", (-0.25, 0, 1.56), (-0.26, -0.03, 1.17), 0.13, coat)
        limb("other_fore_sleeve", (-0.26, -0.03, 1.17), (-0.12, -0.12, 0.94), 0.11, coat)
    else:
        for side in (-1, 1):
            limb("upper_sleeve_%d" % side, (side*0.27, 0, 1.55),
                 (side*0.30, -0.07, 1.22), 0.12, coat)
            limb("fore_sleeve_%d" % side, (side*0.30, -0.07, 1.22),
                 (side*0.10, -0.22, 1.14), 0.10, white)
            ballp("hand_%d" % side, 0.065, (side*0.09, -0.23, 1.14), skin)
        # Suggest glasses without facial detail.
        limb("glasses_bar", (-0.11, -0.17, 1.91), (0.11, -0.17, 1.91), 0.014, steel_dark)
    return p

scene.include("foreground_operator", person("foreground_operator", OPERATOR_X, OPERATOR_Y, 1.0, True))
scene.include("background_worker", person("background_worker", -2.55, 3.25, 0.94, False))

realize(scene)

# Configure finishes after realization. SceneAct's generated materials inherit
# colors; change broad surface families by their object names where available.
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    name = ob.name.lower()
    for mat in ob.data.materials:
        if not mat:
            continue
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            continue
        if any(s in name for s in ("steel", "frame", "rail", "roller", "actuator", "arm", "column", "post")):
            bsdf.inputs["Metallic"].default_value = 0.65
            bsdf.inputs["Roughness"].default_value = 0.30
        elif "guard" in name and "clear" in name:
            bsdf.inputs["Roughness"].default_value = 0.12
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = 0.18
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "DITHERED"
        else:
            bsdf.inputs["Roughness"].default_value = 0.65
        if "recessed_light" in name or "display" in name:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (0.80, 1.0, 0.97, 1)
                bsdf.inputs["Emission Strength"].default_value = 0.55

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
background.inputs["Color"].default_value = (0.70, 0.87, 0.85, 1)
background.inputs["Strength"].default_value = 0.65

# Preserve the reference aspect ratio for the projection check and final camera.
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((0, -2, 3.0), power=700, size=5.0,
             target=(0, 0.5, 0.8), color=(0.84, 1.0, 0.97))
area_emitter((-2.5, 3.8, 3.0), power=500, size=4.0,
             target=(0, 2.0, 1.0), color=(0.82, 0.98, 0.97))
area_emitter((3.0, 1.0, 3.0), power=450, size=3.0,
             target=(0.5, 1.0, 1.0), color=(0.85, 1.0, 0.98))

# A few identifiable geometric landmarks. These are approximate correspondence
# estimates, not calibration and not a visibility or silhouette test.
landmarks = [
    ("foreground belt end", (MACHINE_X, MACHINE_FRONT, BELT_Z), (0.68, 0.94)),
    ("guard near upper corner", (MACHINE_X+0.89, -0.25, 1.90), (0.75, 0.63)),
    ("HMI upper center", (1.02, 0.43, 2.875), (0.75, 0.07)),
    ("background light corner", (-1.25, 4.46, ROOM_HEIGHT-0.07), (0.27, 0.12)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("landmark | reference (u,v) | projected (u,v)")
for name, p, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v, 3) for v in uv))

# Moderate depth of field with the foreground operator as the focal subject.
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector(CAMERA_POSITION) -
                               Vector((OPERATOR_X, OPERATOR_Y, 1.4))).length
cam.data.dof.aperture_fstop = 8.0
