# Reference inventory and approximate image anchors, normalized x/y:
# - Chaise longue: overall bounds (0.03, 0.23) to (0.83, 0.94).
#   Upholstered back at left, long pale seat extending right, carved dark frame,
#   and visible legs beneath. The rear of the seat overlaps the back and pillow.
# - Pillow: approximately (0.09, 0.28) to (0.32, 0.54), in front of the back.
# - Paneled cream wall: across the upper and right background; molding lines run
#   almost horizontally, rising slightly toward the right.
# - Dark wooden floor: lower half, behind and beneath the chaise.
# - Bright curtained window: narrow strip at far left, partly hidden by the chaise.
# - Partial cane chair: lower-left corner, mostly outside the image.
# - Small dark rectangular tag: on the right half of the seat.
# The concealed back of the chaise and most of the foreground chair are uncertain.
#
# Approximate landmarks used for a numerical projection report:
#   back crest (0.08, 0.25), seat foot (0.81, 0.68),
#   front leg bottom (0.77, 0.93), wall panel upper-right (0.88, 0.10).
# Projection is only a framing check; the correspondences are approximate.
#
# Expanded primitive estimate: architecture ~35, chaise ~110 including tube
# expansions, pillow 1, tag 1, foreground chair ~18; total about 165 meshes.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Antique chaise interior")

# Major dimensions and camera controls are deliberately kept separate.
CHAISE_X = 0.0
CHAISE_Y = -0.12
SEAT_LENGTH = 2.35
SEAT_WIDTH = 0.91
SEAT_Z = 0.67
CAMERA_POSITION = (3.25, -6.7, 4.0)
CAMERA_TARGET = (-0.05, 0.12, 0.78)
CAMERA_LENS = 42

cream = (0.76, 0.72, 0.64)
wall_color = (0.72, 0.70, 0.65)
trim = (0.82, 0.79, 0.72)
shadow_trim = (0.55, 0.53, 0.48)
wood = (0.19, 0.095, 0.064)
frame = (0.30, 0.31, 0.25)
frame_light = (0.49, 0.47, 0.36)
fabric = (0.78, 0.73, 0.68)
fabric_edge = (0.62, 0.57, 0.51)
stripe = (0.64, 0.52, 0.48)

def add(asset, name, node):
    asset.include(name, node)

def tube(asset, name, points, radius, color):
    add(asset, name, sweep_tube(points=points, radius=radius, color=color))

# Floor: broad dark brown planks, with fine restrained seams.
room = Asset("Architecture")
add(room, "floor", box((12, 10, 0.12), center=(0, 0, -0.08), color=wood))
for i, y in enumerate([-2.4, -1.65, -0.90, -0.15, 0.60, 1.35]):
    add(room, "floor_seam_%02d" % i,
        box((8, 0.008, 0.004), center=(0, y, -0.016), color=(0.12, 0.065, 0.045)))

# Rear wall and its broad inset panel.
add(room, "back_wall", box((8, 0.12, 4.5), center=(0, 1.22, 2.15), color=wall_color))
add(room, "baseboard", box((8, 0.11, 0.18), center=(0, 1.13, 0.11), color=trim))
add(room, "baseboard_top", box((8, 0.12, 0.035), center=(0, 1.11, 0.22), color=shadow_trim))
add(room, "chair_rail", box((8, 0.12, 0.065), center=(0, 1.10, 1.79), color=trim))
add(room, "upper_rail", box((8, 0.10, 0.035), center=(0, 1.11, 2.16), color=trim))
# Applied rectangular moulding, with a darker inset line.
for name, z in [("low", 0.39), ("high", 1.65)]:
    add(room, "panel_outer_" + name,
        box((4.35, 0.055, 0.028), center=(0.10, 1.125, z), color=trim))
    add(room, "panel_inner_" + name,
        box((4.20, 0.060, 0.010), center=(0.10, 1.095, z + (0.045 if name == "low" else -0.045)), color=shadow_trim))
for name, x in [("left", -2.075), ("right", 2.275)]:
    add(room, "panel_outer_" + name,
        box((0.028, 0.055, 1.28), center=(x, 1.125, 1.02), color=trim))
    add(room, "panel_inner_" + name,
        box((0.010, 0.060, 1.18), center=(x + (0.045 if name == "left" else -0.045), 1.095, 1.02), color=shadow_trim))
# Vertical cabinet seams and two small dark pulls near the upper wall.
for i, x in enumerate([-1.35, 0.38, 2.55]):
    add(room, "wall_seam_%d" % i,
        box((0.009, 0.025, 1.90), center=(x, 1.075, 1.20), color=(0.49, 0.47, 0.43)))
for i, x in enumerate([-1.10, -0.99]):
    add(room, "cabinet_pull_%d" % i,
        rod(0.018, start=(x, 1.045, 1.93), end=(x, 1.045, 2.01), color=(0.18, 0.16, 0.13)))
# Bright opening and hanging curtain at the left.
add(room, "window_light", box((0.65, 0.07, 3.2), center=(-2.75, 1.08, 1.75), color=(0.96, 0.96, 0.91)))
add(room, "window_jamb", box((0.08, 0.13, 3.4), center=(-2.39, 1.02, 1.75), color=trim))
for i in range(5):
    x = -2.96 + i * 0.09
    add(room, "curtain_fold_%d" % i,
        box((0.095, 0.08, 3.0), center=(x, 0.99 - 0.015 * (i % 2), 1.68),
            color=(0.72 + i * 0.018, 0.68 + i * 0.018, 0.60 + i * 0.018)))
scene.include("architecture", room)

chaise = Asset("Chaise longue")
cx, cy = CHAISE_X, CHAISE_Y
# Low carved wooden foundation, extending under the upholstered mattress.
add(chaise, "wooden_seat_foundation",
    fillet_box((SEAT_LENGTH, SEAT_WIDTH, 0.13), radius=0.055,
               center=(cx, cy, SEAT_Z - 0.12), color=frame))
# Soft seat: a rounded central cushion with a gently rounded foot.
add(chaise, "seat_cushion",
    fillet_box((SEAT_LENGTH, SEAT_WIDTH, 0.19), radius=0.09,
               center=(cx, cy, SEAT_Z), color=fabric))
# Parallel fine woven stripes follow the long dimension.
for i in range(13):
    yy = cy - 0.39 + i * 0.065
    add(chaise, "upholstery_stripe_%02d" % i,
        rod(0.0035, start=(cx - 1.04, yy, SEAT_Z + 0.098),
            end=(cx + 1.04, yy, SEAT_Z + 0.098), color=stripe))
# Border piping around the exposed cushion and rail on the near side.
tube(chaise, "near_seat_piping",
     [(cx-1.07,cy-0.44,0.76),(cx-0.65,cy-0.46,0.77),
      (cx+0.45,cy-0.46,0.77),(cx+1.05,cy-0.40,0.75)],
     0.012, fabric_edge)
tube(chaise, "near_carved_rail",
     [(cx-1.08,cy-0.47,0.57),(cx-0.70,cy-0.48,0.54),
      (cx-0.10,cy-0.48,0.53),(cx+0.57,cy-0.48,0.54),
      (cx+1.08,cy-0.42,0.53)], 0.029, frame_light)
tube(chaise, "foot_carved_rail",
     [(cx+1.08,cy-0.42,0.53),(cx+1.16,cy-0.23,0.54),
      (cx+1.16,cy+0.22,0.54),(cx+1.08,cy+0.42,0.56)],
     0.028, frame_light)

# Cabriole-style legs: short jointed curves, with visible curved feet.
for ix, x in enumerate([cx-0.91, cx+0.99]):
    for iy, y in enumerate([cy-0.37, cy+0.34]):
        tube(chaise, "leg_%d_%d" % (ix, iy),
             [(x,y,0.56),(x+0.045,y,0.45),(x+0.035,y,0.30),
              (x-0.015,y-0.015,0.10),(x+0.015,y-0.04,0.055)],
             0.039, frame)
        add(chaise, "leg_joint_%d_%d" % (ix, iy),
            ball(0.055, center=(x,y,0.52), color=frame_light))
# Three restrained carved medallions along the front apron.
for i, x in enumerate([-0.62, 0.02, 0.67]):
    add(chaise, "apron_rosette_%d" % i,
        ball(0.047, center=(cx+x,cy-0.50,0.535), color=frame_light))

# Back panel leans outward at the head of the chaise. Its upper outline curves
# down toward the arm; a slim panel forms the visible upholstered end.
back = fillet_box((0.16, 0.92, 0.88), radius=0.065,
                  center=(cx-1.08, cy, 1.13), color=fabric)
back.turn(axis="+y", degrees=-13)
add(chaise, "upholstered_back", back)
# Curved crest and end frames provide the distinctive outline.
for side, yy in [("near", cy-0.46), ("far", cy+0.46)]:
    tube(chaise, "back_outline_" + side,
         [(cx-1.00,yy,0.57),(cx-1.15,yy,0.80),(cx-1.29,yy,1.10),
          (cx-1.32,yy,1.42),(cx-1.25,yy,1.58),(cx-1.08,yy,1.62),
          (cx-0.92,yy,1.56)], 0.033, frame)
# Top crest across the back width.
tube(chaise, "back_crest",
     [(cx-1.25,cy-0.46,1.58),(cx-1.30,cy-0.26,1.63),
      (cx-1.31,cy,1.64),(cx-1.30,cy+0.26,1.63),(cx-1.25,cy+0.46,1.58)],
     0.027, frame_light)
# Low arms rise from the long seat into the curved back, visibly leaving
# the seat interior open above them.
for side, yy in [("near", cy-0.47), ("far", cy+0.47)]:
    tube(chaise, "arm_rail_" + side,
         [(cx-1.27,yy,1.46),(cx-1.16,yy,1.28),(cx-0.98,yy,1.13),
          (cx-0.78,yy,1.04),(cx-0.61,yy,1.01)],
         0.033, frame_light)
    tube(chaise, "arm_support_" + side,
         [(cx-0.61,yy,1.01),(cx-0.59,yy,0.87),
          (cx-0.51,yy,0.69),(cx-0.48,yy,0.59)],
         0.033, frame)
    # Upholstered infill below the arm.
    sidepad = fillet_box((0.62, 0.07, 0.37), radius=0.03,
                         center=(cx-0.91, yy, 0.84), color=fabric)
    add(chaise, "arm_infill_" + side, sidepad)

# Pillow leaning against the back, with a pale, softly rounded silhouette.
pillow = fillet_box((0.22, 0.58, 0.59), radius=0.095,
                    center=(cx-0.91, cy-0.01, 1.20), color=(0.89,0.84,0.73))
pillow.turn(axis="+y", degrees=-17)
add(chaise, "loose_pillow", pillow)
# Dark green small label on the seat.
add(chaise, "seat_label",
    box((0.16, 0.095, 0.006), center=(cx+0.56,cy+0.08,0.772), color=(0.10,0.22,0.20)))
scene.include("chaise_longue", chaise)

# Fragment of a cane chair in the immediate foreground, mostly cropped.
chair = Asset("Foreground cane chair")
add(chair, "cane_panel",
    fillet_box((0.74, 0.60, 0.045), radius=0.06,
               center=(-2.05,-1.55,0.49), color=(0.57,0.40,0.29)))
for yy in [-1.85, -1.25]:
    add(chair, "chair_long_rim_%s" % yy,
        rod(0.035, start=(-2.40,yy,0.51), end=(-1.70,yy,0.51), color=frame_light))
for xx in [-2.40, -1.70]:
    add(chair, "chair_short_rim_%s" % xx,
        rod(0.035, start=(xx,-1.85,0.51), end=(xx,-1.25,0.51), color=frame_light))
for i in range(7):
    x = -2.34 + i*0.10
    add(chair, "cane_line_%d" % i,
        rod(0.004, start=(x,-1.79,0.516), end=(x,-1.31,0.516), color=(0.75,0.60,0.45)))
scene.include("foreground_chair", chair)

realize(scene)

# The reference has a 4:3 frame.
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

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
background.inputs["Color"].default_value = (0.80, 0.78, 0.73, 1)
background.inputs["Strength"].default_value = 0.65

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((-3.3,-3.0,4.8), power=650, size=4.0,
             target=(0,0,0.8), color=(1.0,0.91,0.81))
area_emitter((2.0,-0.5,4.7), power=250, size=3.5,
             target=(0,0,0.5), color=(1.0,0.96,0.91))

# Numerical reference versus projected landmark report.
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
landmarks = [
    ("back crest", (cx-1.30,cy-0.26,1.63), (0.08,0.25)),
    ("seat foot", (cx+1.16,cy-0.23,0.75), (0.81,0.68)),
    ("front leg bottom", (cx+1.005,cy-0.41,0.055), (0.77,0.93)),
    ("wall panel upper right", (2.275,1.10,1.65), (0.88,0.10)),
]
print("Landmark                 reference       projected")
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
    print("%-24s %s %s" % (name, ref, uv))
