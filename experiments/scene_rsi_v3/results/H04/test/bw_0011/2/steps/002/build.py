# Reference inventory and anchors, estimated from the 512 x 293 image:
# - Blue back wall: (0.10, 0.22)-(0.69, 0.84), divided by vertical seams.
# - Blue right wall: (0.69, 0.13)-(0.91, 0.91); its near edge is at right.
# - Cabinet: (0.16, 0.40)-(0.31, 0.83), with two dark glazed openings,
#   a pale metal frame, central handles, and several horizontal shelves.
# - Feature mural: (0.37, 0.24)-(0.64, 0.80), pale above and warm below,
#   with large, airy seed heads and dark crossing stems.
# - Clock: (0.79, 0.33)-(0.88, 0.50), in front of the right wall.
# - Floor begins at the back wall around y=0.83 and the right-wall corner
#   around (0.69, 0.80); a pale curved cove follows both wall bases.
# - Ceiling occupies roughly the top 0.23 of the picture, with dark panels,
#   rails, a white LED panel, and partially exposed structure.
# - Back-wall horizontal edges are almost level; right-wall edges rise toward
#   the near right edge. Vertical seams are nearly vertical.
# - Hidden wall returns and the detailed ceiling services remain uncertain.
#
# Comparison with the first complete render:
# 1. Framing/camera: back-wall corner floor was observed near (0.69, 0.69)
#    instead of (0.69, 0.80); mural upper left near (0.46, 0.33) instead of
#    (0.37, 0.24). The room occupied a small island in the image, and the
#    floor and ceiling edges were exposed against the world background.
# 2. Viewpoint: the rendered right wall was seen mainly from outside and the
#    clock was hidden. The camera moves inside the open front and to the left
#    of the right wall. This should expose the screen, move the near skirting
#    endpoint rightward, and make the room surround the frame.
# 3. Ceiling and floor: the rendered floor occupied a small isolated slab and
#    the roof appeared as a thin floating slab. Extending both toward the
#    camera should crop them at the image edges and provide the reference's
#    continuous foreground and ceiling.
# 4. The rendered cabinet and mural were too small and faint. Their dimensions
#    and their wall positions are adjusted independently of the camera; darker
#    stems, door openings, and stronger panel contrast improve their legibility.
# Camera position, target and lens are explicit below. The numerical check
# prints reference and computed points separately and compares a small trial
# upward aim with the selected aim; it does not prove visible contours.
#
# Estimated expanded primitive count: architecture ~24, cabinet ~23,
# mural ~145, screen ~3, ceiling ~35, total about 230. All dimensions are
# positive; rods have distinct endpoints. The mural is editable geometry,
# not the reference image, a background, or a projected texture.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(24)

# Major dimensions and camera are independently editable.
W = 5.40
H = 3.05
BACK = 1.65
RIGHT = W / 2
FRONT = -3.10
CAMERA_POSITION = (-0.15, -7.4, 1.90)
CAMERA_TARGET = (0.72, 1.35, 1.57)
CAMERA_LENS = 35.0

BLUE = (0.045, 0.36, 0.59)
BLUE_RIGHT = (0.045, 0.38, 0.60)
SEAM = (0.025, 0.22, 0.33)
FLOOR = (0.48, 0.52, 0.51)
COVE = (0.80, 0.85, 0.82)
STEEL = (0.57, 0.62, 0.61)
STEEL_LIGHT = (0.76, 0.80, 0.78)
GLASS = (0.12, 0.18, 0.18)
CEILING = (0.18, 0.21, 0.21)
RAIL = (0.46, 0.51, 0.50)

scene = Scene("Clean laboratory")

architecture = Asset("Modular cleanroom architecture")
architecture.include(
    "continuous grey floor",
    box((12, 13, 0.12), center=(0, -2.4, -0.07), color=FLOOR)
)
architecture.include(
    "blue back wall",
    box((W, 0.10, H), center=(0, BACK, H / 2), color=BLUE)
)
architecture.include(
    "blue right wall",
    box((0.10, BACK - FRONT, H),
        center=(RIGHT, (BACK + FRONT) / 2, H / 2), color=BLUE_RIGHT)
)

for i, x in enumerate((-2.10, -0.80, 0.42, 1.58, 2.35)):
    architecture.include(
        "back vertical panel seam %02d" % i,
        box((0.012, 0.012, H - 0.06),
            center=(x, BACK - 0.057, H / 2), color=SEAM)
    )
for i, y in enumerate((-2.40, -1.35, -0.30, 0.75)):
    architecture.include(
        "right vertical panel seam %02d" % i,
        box((0.012, 0.012, H - 0.06),
            center=(RIGHT - 0.057, y, H / 2), color=SEAM)
    )

architecture.include(
    "back cove backing",
    box((W, 0.14, 0.10), center=(0, BACK - 0.12, 0.05), color=COVE)
)
architecture.include(
    "back rounded cove",
    rod(0.065, start=(-W / 2, BACK - 0.18, 0.06),
        end=(RIGHT - 0.12, BACK - 0.18, 0.06), color=COVE)
)
architecture.include(
    "right cove backing",
    box((0.14, BACK - FRONT, 0.10),
        center=(RIGHT - 0.12, (BACK + FRONT) / 2, 0.05), color=COVE)
)
architecture.include(
    "right rounded cove",
    rod(0.065, start=(RIGHT - 0.18, FRONT, 0.06),
        end=(RIGHT - 0.18, BACK - 0.18, 0.06), color=COVE)
)
architecture.include(
    "right edge upright",
    box((0.07, 0.07, H + 0.08),
        center=(RIGHT, FRONT + 0.04, H / 2), color=(0.39, 0.44, 0.43))
)
scene.include("architecture", architecture)

# Feature wall: a light printed-looking surface with editable plant forms.
mural = Asset("Dandelion feature wall")
MX0, MX1 = -0.70, 1.40
MZ0, MZ1 = 0.10, 3.00
MY = BACK - 0.066
mural.include(
    "pale mural field",
    box((MX1 - MX0, 0.014, MZ1 - MZ0),
        center=((MX0 + MX1) / 2, MY, (MZ0 + MZ1) / 2),
        color=(0.79, 0.88, 0.83))
)
# Subtle warm low band; the principal visual detail is the plant geometry.
for i in range(6):
    z = 0.14 + i * 0.12
    mural.include(
        "warm lower field %d" % i,
        box((MX1 - MX0, 0.006, 0.125),
            center=((MX0 + MX1) / 2, MY - 0.012, z),
            color=(0.75 + 0.012 * i, 0.63 + 0.030 * i, 0.49 + 0.045 * i))
    )
INK = (0.20, 0.08, 0.16)
MID = (0.34, 0.27, 0.29)
FINE = (0.43, 0.48, 0.44)
stems = [
    ((-0.60, 0.12), (0.38, 1.54)),
    ((-0.51, 0.12), (0.20, 1.80)),
    ((-0.22, 0.12), (0.82, 1.45)),
    ((0.02, 0.12), (0.56, 1.84)),
    ((0.40, 0.12), (-0.10, 1.37)),
    ((0.68, 0.12), (0.05, 1.20)),
    ((1.15, 0.12), (0.65, 1.53)),
    ((1.30, 0.12), (0.20, 0.90)),
    ((-0.65, 0.43), (1.25, 0.78)),
    ((-0.60, 0.78), (1.20, 0.28)),
    ((-0.48, 1.02), (0.60, 0.54)),
    ((0.10, 0.85), (0.84, 1.52)),
    ((-0.15, 1.33), (0.75, 0.52)),
    ((0.29, 1.48), (0.39, 2.64)),
]
for i, (a, b) in enumerate(stems):
    mural.include(
        "dark plant stem %02d" % i,
        rod(0.010 if i < 9 else 0.007,
            start=(a[0], MY - 0.030, a[1]),
            end=(b[0], MY - 0.030, b[1]), color=INK)
    )

# Thin rays suggest dandelion umbrellas. Endpoint clipping confines them to
# the panel; the different sizes retain the reference's uneven airy gaps.
heads = [
    (-0.45, 2.64, 0.63),
    (0.40, 2.69, 0.64),
    (1.17, 2.43, 0.53),
    (-0.48, 1.82, 0.48),
    (0.74, 1.65, 0.47),
    (1.15, 1.06, 0.42),
    (-0.33, 0.79, 0.43),
]
for h, (cx, cz, radius) in enumerate(heads):
    mural.include(
        "seed head center %d" % h,
        ball(0.018, center=(cx, MY - 0.042, cz), color=MID)
    )
    for j in range(20):
        angle = 2 * math.pi * j / 20 + h * 0.19
        length = radius * (0.82 + 0.18 * random.random())
        ex = cx + length * math.cos(angle)
        ez = cz + length * math.sin(angle)
        if MX0 + 0.015 < ex < MX1 - 0.015 and MZ0 + 0.015 < ez < MZ1 - 0.015:
            sx = cx + 0.08 * math.cos(angle)
            sz = cz + 0.08 * math.sin(angle)
            mural.include(
                "seed filament %d %02d" % (h, j),
                rod(0.0023, start=(sx, MY - 0.041, sz),
                    end=(ex, MY - 0.041, ez), color=FINE)
            )
scene.include("feature mural", mural)

# Cabinet: metal surround, two separate dark glass openings, shelves and pulls.
cabinet = Asset("Stainless glazed storage cabinet")
CAB_X = -1.83
CAB_W = 1.15
CAB_H = 1.91
CAB_Y = BACK - 0.095
cabinet.include(
    "cabinet metal front",
    box((CAB_W, 0.10, CAB_H), center=(CAB_X, CAB_Y, CAB_H / 2),
        color=STEEL_LIGHT)
)
for i, dx in enumerate((-0.28, 0.28)):
    cabinet.include(
        "dark glazed opening %d" % i,
        box((0.37, 0.014, 1.63), center=(CAB_X + dx, CAB_Y - 0.060, 0.98),
            color=GLASS)
    )
    # Thin lighter strips are the shelf edges seen through the glass.
    for j, z in enumerate((0.33, 0.62, 0.91, 1.20, 1.49, 1.76)):
        cabinet.include(
            "door %d shelf edge %d" % (i, j),
            box((0.34, 0.012, 0.018),
                center=(CAB_X + dx, CAB_Y - 0.071, z),
                color=(0.47, 0.53, 0.51))
        )
    cabinet.include(
        "door pull %d" % i,
        rod(0.013, start=(CAB_X + (-0.055 if i == 0 else 0.055), CAB_Y - 0.085, 0.88),
            end=(CAB_X + (-0.055 if i == 0 else 0.055), CAB_Y - 0.085, 1.07),
            color=(0.28, 0.32, 0.31))
    )
cabinet.include(
    "center door divider",
    box((0.045, 0.025, CAB_H - 0.04),
        center=(CAB_X, CAB_Y - 0.065, CAB_H / 2), color=STEEL)
)
cabinet.include(
    "top cap",
    box((CAB_W + 0.04, 0.13, 0.055),
        center=(CAB_X, CAB_Y, CAB_H), color=STEEL_LIGHT)
)
scene.include("cabinet", cabinet)

# Digital screen on the inward-facing surface of the right wall.
screen = Asset("Digital time and date display")
SX = RIGHT - 0.065
SY = -1.00
SZ = 2.06
screen.include(
    "dark bezel",
    box((0.035, 0.92, 0.61), center=(SX, SY, SZ),
        color=(0.055, 0.10, 0.20))
)
screen.include(
    "blue display face",
    box((0.012, 0.84, 0.53), center=(SX - 0.025, SY, SZ),
        color=(0.055, 0.15, 0.29))
)
scene.include("digital display", screen)

# A continuous dark ceiling above the room and its white perimeter.
ceiling = Asset("Exposed T-grid ceiling")
ceiling.include(
    "dark ceiling field",
    box((8.0, 10.5, 0.10), center=(0, -2.6, 3.28), color=CEILING)
)
for i, x in enumerate((-3.0, -2.25, -1.50, -0.75, 0, 0.75, 1.50, 2.25, 3.0)):
    ceiling.include(
        "long grid rail %02d" % i,
        box((0.035, 9.5, 0.035), center=(x, -2.2, 3.08), color=RAIL)
    )
for i, y in enumerate((-6.0, -5.15, -4.30, -3.45, -2.60, -1.75, -0.90, -0.05, 0.80, 1.60)):
    ceiling.include(
        "cross grid rail %02d" % i,
        box((7.0, 0.035, 0.035), center=(0, y, 3.08), color=RAIL)
    )
for i, y in enumerate((-2.9, -0.8, 1.25)):
    ceiling.include(
        "overhead structural beam %d" % i,
        box((7.0, 0.13, 0.13), center=(0, y, 3.23),
            color=(0.30, 0.34, 0.33))
    )
for i, x in enumerate((-2.2, -0.8, 0.8, 2.2)):
    ceiling.include(
        "suspension rod %d" % i,
        rod(0.012, start=(x, 0.6, 3.09), end=(x, 0.6, 3.30), color=STEEL)
    )
ceiling.include(
    "overhead pipe",
    rod(0.045, start=(-3.0, 0.9, 3.21),
        end=(3.0, 0.9, 3.21), color=(0.38, 0.43, 0.42))
)
for i, (x, y) in enumerate(((0.70, 0.45), (-1.5, -2.1), (1.55, -3.7))):
    ceiling.include(
        "LED panel %d" % i,
        box((0.70, 0.70, 0.025), center=(x, y, 3.055),
            color=(0.91, 0.96, 0.95))
    )
# Light-colored fascia along the far ceiling edge.
ceiling.include(
    "back ceiling fascia",
    box((W, 0.36, 0.055), center=(0, 1.42, 3.04), color=(0.73, 0.77, 0.75))
)
scene.include("ceiling", ceiling)

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
background.inputs["Color"].default_value = (0.80, 0.85, 0.84, 1)
background.inputs["Strength"].default_value = 0.45

# Keep the original 512:293 aspect for projection and final framing.
sc.render.resolution_x = 512
sc.render.resolution_y = 293
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)

landmarks = [
    ("back corner floor", (RIGHT - 0.12, BACK - 0.12, 0.08), (0.69, 0.80)),
    ("mural upper left", (MX0, MY, MZ1), (0.37, 0.24)),
    ("cabinet upper left", (CAB_X - CAB_W / 2, CAB_Y - 0.06, CAB_H), (0.16, 0.40)),
    ("right foreground skirting", (RIGHT - 0.12, FRONT, 0.08), (0.91, 0.91)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y
    )
    print(label)
    for name, point, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            round(0.5 * (clip.x / clip.w + 1), 3),
            round(0.5 * (1 - clip.y / clip.w), 3)
        )
        print(name, "reference", ref, "computed", uv)

projection_table("Selected camera")
set_view(
    CAMERA_POSITION,
    (CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2] + 0.08),
    lens=CAMERA_LENS
)
projection_table("Trial upward aim")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
bpy.context.view_layer.update()

# Text faces toward the room; local horizontal runs along the right wall.
def screen_text(name, text, location, size, color):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    mat = bpy.data.materials.new(name + " material")
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color, 1)
        if "Emission Color" in bs.inputs:
            bs.inputs["Emission Color"].default_value = (*color, 1)
            bs.inputs["Emission Strength"].default_value = 0.5
    curve.materials.append(mat)

screen_text("display time", "09:29:07", (SX - 0.035, SY, SZ + 0.03),
            0.125, (0.67, 0.82, 0.88))
screen_text("display date", "2026  11  11", (SX - 0.036, SY, SZ - 0.14),
            0.042, (0.53, 0.70, 0.78))

area_emitter((0.70, 0.45, 3.02), power=330, size=1.0,
             target=(0.70, 0.45, 0))
area_emitter((-1.50, -2.10, 3.02), power=350, size=1.1,
             target=(-1.50, -2.10, 0))
area_emitter((1.55, -3.70, 3.02), power=350, size=1.1,
             target=(1.55, -3.70, 0))

sc.render.engine = "CYCLES"
sc.view_settings.view_transform = "AgX"
