# Reference inventory and visual anchors, estimated from the 512 x 293 image:
# - Back wall: blue modular panels, approximately (0.10, 0.23)-(0.69, 0.84).
# - Right wall: blue panels, approximately (0.69, 0.13)-(0.91, 0.91).
# - Wall corner at about (0.69, 0.27)-(0.69, 0.80).
# - Left stainless double-door cabinet: (0.16, 0.40)-(0.31, 0.83).
# - Dandelion mural: (0.37, 0.24)-(0.64, 0.80), behind cabinet and screen.
# - Digital display: (0.79, 0.33)-(0.88, 0.50) on right wall.
# - Foreground floor: approximately (0, 0.84)-(1, 1), bounded by pale coved skirting.
# - Exposed ceiling: approximately (0, 0)-(1, 0.24); dark ceiling grid,
#   structural framing, a visible white LED panel and exposed service elements.
# - Dominant edges: back-wall horizontal edges slope slightly down to the right;
#   right-wall top and bottom edges slope upward toward the back corner.
#   Vertical wall seams remain nearly vertical. Numbered annotation circles are ignored.
# - Hidden wall returns, ceiling services and mural details are uncertain.
# Estimated SceneAct primitives: architecture ~35, cabinet ~30, mural ~100,
#   ceiling ~50, screen ~10, totaling approximately 225 separate primitives.
# The mural is built from editable geometry, not an image or projected texture.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(12)

# Explicit scene and camera parameters.
ROOM_W = 6.6
ROOM_D = 3.25
ROOM_H = 3.05
CORNER_X = 3.3
BACK_Y = 1.65
FRONT_Y = -1.60
CAMERA_POSITION = (7.0, -11.8, 4.15)
CAMERA_TARGET = (0.25, 0.82, 1.55)
CAMERA_LENS = 34

BLUE = (0.075, 0.42, 0.65)
BLUE_LIGHT = (0.10, 0.48, 0.70)
SEAM = (0.035, 0.25, 0.35)
FLOOR = (0.55, 0.59, 0.58)
WHITE = (0.88, 0.92, 0.89)
METAL = (0.55, 0.60, 0.60)
DARK_METAL = (0.25, 0.31, 0.32)
GLASS_DARK = (0.19, 0.25, 0.25)
CEILING = (0.20, 0.24, 0.24)
GRID = (0.47, 0.53, 0.53)

scene = Scene("Clean laboratory")
architecture = Asset("Modular cleanroom architecture")
architecture.include("floor", box((8.3, 6.5, 0.14), center=(0, 0, -0.07), color=FLOOR))
architecture.include("back wall", box((ROOM_W, 0.12, ROOM_H),
    center=(0, BACK_Y, ROOM_H/2), color=BLUE))
architecture.include("right wall", box((0.12, ROOM_D, ROOM_H),
    center=(CORNER_X, 0.025, ROOM_H/2), color=BLUE_LIGHT))

# Panel joints are narrow dark recessed-looking strips on the visible wall surfaces.
for i, x in enumerate((-2.75, -1.65, -0.55, 0.55, 1.65, 2.75)):
    architecture.include("back panel joint %02d" % i,
        box((0.012, 0.009, 2.99), center=(x, BACK_Y-0.066, 1.52), color=SEAM))
for i, y in enumerate((-1.15, -0.35, 0.45, 1.25)):
    architecture.include("right panel joint %02d" % i,
        box((0.009, 0.012, 2.99), center=(CORNER_X-0.066, y, 1.52), color=SEAM))
# Pale coved floor-wall transition, represented by sloping rounded strips.
architecture.include("back skirting", box((ROOM_W, 0.13, 0.105),
    center=(0, BACK_Y-0.10, 0.055), color=WHITE))
architecture.include("right skirting", box((0.13, ROOM_D, 0.105),
    center=(CORNER_X-0.10, 0.025, 0.055), color=WHITE))
architecture.include("back cove curve", rod(0.048, start=(-3.3, BACK_Y-0.16, 0.055),
    end=(3.25, BACK_Y-0.16, 0.055), color=WHITE))
architecture.include("right cove curve", rod(0.048, start=(CORNER_X-0.16, FRONT_Y, 0.055),
    end=(CORNER_X-0.16, BACK_Y-0.16, 0.055), color=WHITE))
scene.include("architecture", architecture)

# Full-height printed feature panel. Layered lines and seed heads suggest the
# translucent dandelion photograph while remaining separately editable geometry.
mural = Asset("Dandelion feature wall")
MX0, MX1 = -0.95, 1.50
MZ0, MZ1 = 0.10, 3.00
MY = BACK_Y - 0.078
mural.include("pale image substrate", box((MX1-MX0, 0.014, MZ1-MZ0),
    center=((MX0+MX1)/2, MY, (MZ0+MZ1)/2), color=(0.76, 0.86, 0.81)))
# Soft horizontal color bands echo the warm lower edge of the reference mural.
for i in range(5):
    z = 0.12 + i*0.12
    mural.include("warm lower band %d" % i,
        box((MX1-MX0, 0.004, 0.125), center=((MX0+MX1)/2, MY-0.01, z),
            color=(0.72+0.025*i, 0.62+0.04*i, 0.48+0.05*i)))
INK = (0.24, 0.13, 0.21)
FINE = (0.38, 0.41, 0.37)
# Dark crossing plant stems.
stems = [
    ((-0.78,0.14),(-0.30,1.13)), ((-0.58,0.14),(0.60,1.78)),
    ((0.05,0.12),(0.95,1.22)), ((0.45,0.14),(-0.32,1.95)),
    ((1.22,0.12),(0.61,1.44)), ((1.38,0.12),(0.10,1.05)),
    ((-0.88,0.40),(1.32,0.68)), ((-0.63,0.75),(0.98,0.33)),
    ((-0.14,1.05),(0.77,1.65)), ((0.23,0.70),(1.12,1.36))
]
for i, (a,b) in enumerate(stems):
    mural.include("stem %02d" % i, rod(0.012,
        start=(a[0],MY-0.025,a[1]), end=(b[0],MY-0.025,b[1]), color=INK))
# Airy radial seed heads, cropped naturally at the image's rectangular panel.
heads = [(-0.45,2.45,0.70), (0.73,2.55,0.63), (1.25,1.94,0.46),
         (-0.57,1.63,0.42), (0.50,1.45,0.36)]
for h,(cx,cz,r) in enumerate(heads):
    mural.include("seed head center %d" % h,
        ball(0.025, center=(cx,MY-0.038,cz), color=FINE))
    for j in range(13):
        ang = 2*math.pi*j/13 + h*0.17
        ex = cx + r*math.cos(ang)
        ez = cz + r*math.sin(ang)
        if MX0+0.02 < ex < MX1-0.02 and MZ0+0.02 < ez < MZ1-0.02:
            sx = cx + 0.10*r*math.cos(ang)
            sz = cz + 0.10*r*math.sin(ang)
            mural.include("seed filament %d %02d" % (h,j), rod(0.0035,
                start=(sx,MY-0.038,sz), end=(ex,MY-0.038,ez), color=FINE))
scene.include("feature mural", mural)

# Recessed-looking stainless cabinet with two glazed doors and visible shelves.
cabinet = Asset("Stainless glazed storage cabinet")
CAB_X, CAB_Z = -2.00, 0.93
CAB_W, CAB_H = 1.20, 1.85
CAB_Y = BACK_Y - 0.18
cabinet.include("dark interior", box((CAB_W,0.10,CAB_H),
    center=(CAB_X,CAB_Y,CAB_Z), color=GLASS_DARK))
cabinet.include("top frame", box((CAB_W+0.08,0.16,0.08),
    center=(CAB_X,CAB_Y-0.02,CAB_H), color=METAL))
cabinet.include("bottom frame", box((CAB_W+0.08,0.16,0.08),
    center=(CAB_X,CAB_Y-0.02,0.05), color=METAL))
for i,x in enumerate((CAB_X-CAB_W/2, CAB_X, CAB_X+CAB_W/2)):
    cabinet.include("vertical frame %d" % i, box((0.065,0.16,CAB_H),
        center=(x,CAB_Y-0.03,CAB_Z), color=METAL))
for i,z in enumerate((0.35,0.68,1.01,1.34,1.67)):
    cabinet.include("shelf %d" % i, box((1.08,0.10,0.026),
        center=(CAB_X,CAB_Y-0.085,z), color=(0.66,0.70,0.68)))
for i,x in enumerate((CAB_X-0.30,CAB_X+0.30)):
    cabinet.include("glass door %d" % i,
        box((0.48,0.016,1.65),center=(x,CAB_Y-0.105,0.94),
            color=(0.44,0.53,0.51),opacity=0.24))
    cabinet.include("door handle %d" % i,
        rod(0.014,start=(CAB_X+(-0.075 if i==0 else 0.075),CAB_Y-0.13,0.80),
            end=(CAB_X+(-0.075 if i==0 else 0.075),CAB_Y-0.13,1.04),
            color=(0.79,0.82,0.80)))
scene.include("cabinet", cabinet)

# Right-wall digital clock: screen and luminous type.
screen = Asset("Wall digital time display")
SX = CORNER_X - 0.078
SY, SZ = 0.05, 2.10
screen.include("dark blue bezel", box((0.035,0.90,0.61),
    center=(SX,SY,SZ), color=(0.10,0.16,0.29)))
screen.include("blue display", box((0.009,0.82,0.53),
    center=(SX-0.024,SY,SZ), color=(0.10,0.20,0.36)))
scene.include("digital display", screen)

# Ceiling is an exposed dark plenum with T rails, open service layers, and
# broad luminous panels. These are kept above the principal wall objects.
ceiling = Asset("Exposed T-grid ceiling")
ceiling.include("dark upper slab", box((7.3,4.1,0.10),
    center=(0.0,0.0,3.40), color=CEILING))
for i,x in enumerate((-3.2,-2.4,-1.6,-0.8,0,0.8,1.6,2.4,3.2)):
    ceiling.include("long T rail %d" % i, box((0.032,3.85,0.035),
        center=(x,0,3.08),color=GRID))
for i,y in enumerate((-1.65,-0.85,-0.05,0.75,1.55)):
    ceiling.include("cross T rail %d" % i, box((6.5,0.032,0.035),
        center=(0,y,3.08),color=GRID))
for i,x in enumerate((-2.8,-0.8,1.2,3.0)):
    ceiling.include("suspension rod %d" % i, rod(0.014,
        start=(x,0.1,3.10),end=(x,0.1,3.38),color=METAL))
for i,y in enumerate((-1.2,0.25,1.1)):
    ceiling.include("structural beam %d" % i,box((6.8,0.12,0.12),
        center=(0,y,3.33),color=(0.29,0.33,0.33)))
ceiling.include("service pipe", rod(0.055,start=(-3.2,0.9,3.25),
    end=(3.2,0.9,3.25),color=(0.43,0.47,0.46)))
for i,(x,y) in enumerate(((0.8,0.75),(-2.0,-0.85),(2.4,-0.85))):
    ceiling.include("LED panel %d" % i, box((0.74,0.74,0.025),
        center=(x,y,3.065), color=(0.91,0.97,0.96)))
scene.include("ceiling", ceiling)

realize(scene)

# Configure world, camera, illumination and material finishes after realization.
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
background.inputs["Color"].default_value = (0.80,0.86,0.86,1)
background.inputs["Strength"].default_value = 0.55

# Preserve the source image aspect for the camera and projection check.
sc.render.resolution_x = 512
sc.render.resolution_y = 293
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)

# A few identifiable landmarks, with estimated image coordinates kept separate.
landmarks = [
    ("back corner floor", (CORNER_X-0.1,BACK_Y-0.1,0.08), (0.69,0.80)),
    ("mural upper left", (MX0,MY,3.0), (0.37,0.24)),
    ("cabinet upper left", (CAB_X-CAB_W/2,CAB_Y-0.1,CAB_H), (0.16,0.40)),
    ("right foreground skirting", (CORNER_X-0.1,FRONT_Y,0.08), (0.91,0.91)),
]
def projection_table(label):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    mat = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    print(label)
    for name,p,ref in landmarks:
        clip = mat @ cam.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            round(0.5*(clip.x/clip.w+1),3),
            round(0.5*(1-clip.y/clip.w),3))
        print(name, "reference", ref, "projected", uv)
projection_table("Reference versus initial projection")

# Check the direction of a small target-height adjustment, then restore the
# chosen camera; a rendered comparison is still needed to establish fit.
set_view(CAMERA_POSITION, (CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]+0.08),
    lens=CAMERA_LENS)
projection_table("Trial upward aim")
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
bpy.context.view_layer.update()

# Screen typography is positioned just in front of the right wall.
def add_screen_text(name, text, pos, size, color):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = pos
    # Local text x runs along the wall; its face points toward the room.
    obj.rotation_euler = (math.pi/2, 0, -math.pi/2)
    mat = bpy.data.materials.new(name + " material")
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color,1)
        if "Emission Color" in bs.inputs:
            bs.inputs["Emission Color"].default_value = (*color,1)
            bs.inputs["Emission Strength"].default_value = 0.7
    curve.materials.append(mat)
add_screen_text("display time", "09:29:07", (SX-0.032,SY,SZ+0.025), 0.125,
                (0.65,0.83,0.90))
add_screen_text("display date", "2026  11  11", (SX-0.033,SY,SZ-0.13), 0.045,
                (0.55,0.72,0.82))

area_emitter((0.8,0.75,3.02), power=450, size=1.3, target=(0.8,0.75,0))
area_emitter((-2.0,-0.85,3.02), power=400, size=1.3, target=(-2,-0.85,0))
area_emitter((2.4,-0.85,3.02), power=400, size=1.3, target=(2.4,-0.85,0))
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.view_settings.view_transform = "AgX"
