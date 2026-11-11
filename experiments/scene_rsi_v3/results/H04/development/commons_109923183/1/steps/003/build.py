# Reference versus previous rendered view, approximate normalized bounds:
# Chaise: reference (0.03, 0.23)–(0.83, 0.94); render
# (0.28, 0.32)–(0.67, 0.73). It is much too small.
# Back crest: reference (0.08, 0.25), rendered contour near (0.29, 0.32).
# Seat foot: reference (0.81, 0.68), rendered near (0.67, 0.59).
# Front leg: reference bottom (0.77, 0.93), rendered near (0.60, 0.72).
# Wall panel top: reference near y=0.12; render near y=0.30–0.36.
# Foreground cane chair: reference enters at (0, 0.80); render is a small,
# detached patch near (0.04, 0.56).
#
# Largest discrepancies: (1) chaise scale and framing, (2) pale floor and
# overly bright overall appearance, (3) wall edge slope and panel height,
# (4) foreground chair crop, (5) blocky side infill and cushion silhouette.
# The rendered wall edges fall toward the right, while the reference edges are
# nearly horizontal and rise slightly. The pillow overlaps the back in both.
# The rendered arm has an excessively rectangular infill and a visible gap.
#
# Camera lens is increased from 42 to 65: chaise anchors should spread outward
# from image center. Camera x is reduced to 0.8: wall edges should become flatter.
# The target is lowered slightly: stationary features should move upward.
# A numerical trial below prints the old and candidate projections and rejects
# the camera change if its selected landmark error becomes worse. The upper panel
# molding is raised locally to bring its visible contour upward independently.
# The foreground chair is moved closer to the camera and leftward to crop it.
# The floor material is made darker; lighting also affects the final appearance.
# The chair's upholstered side is enlarged and its top follows the arm.
# Unseen furniture and room geometry remain uncertain.
#
# Estimated expanded primitives: room ~38; chaise ~230, including six fillet
# boxes and sweep expansions; foreground chair ~35; total approximately 303.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Antique chaise interior")
CX, CY = 0.0, -0.12
L, W, Z = 2.35, 0.91, 0.67
OLD_CAMERA = (3.25, -6.7, 4.0)
OLD_TARGET = (-0.05, 0.12, 0.78)
OLD_LENS = 42
CAMERA_POSITION = (0.8, -6.7, 4.0)
CAMERA_TARGET = (-0.12, 0.12, 0.69)
CAMERA_LENS = 65

wall = (0.72, 0.70, 0.65)
trim = (0.82, 0.79, 0.72)
shadow = (0.55, 0.53, 0.48)
wood = (0.10, 0.038, 0.022)
frame = (0.25, 0.27, 0.21)
frame_light = (0.43, 0.42, 0.32)
fabric = (0.75, 0.69, 0.64)
fabric_edge = (0.58, 0.52, 0.46)
stripe = (0.61, 0.48, 0.44)

def add(asset, name, node):
    asset.include(name, node)

def tube(asset, name, points, radius, color):
    add(asset, name, sweep_tube(points=points, radius=radius, color=color))

room = Asset("Architecture")
add(room, "floor", box((12, 10, 0.12), center=(0, 0, -0.08), color=wood))
for i, y in enumerate([-2.4, -1.65, -0.9, -0.15, 0.6, 1.35]):
    add(room, "floor_seam_%02d" % i,
        box((8, 0.005, 0.003), center=(0, y, -0.017),
            color=(0.075, 0.027, 0.016)))

add(room, "back_wall", box((8, 0.12, 4.5),
                           center=(0, 1.22, 2.15), color=wall))
add(room, "baseboard", box((8, 0.11, 0.18),
                            center=(0, 1.13, 0.11), color=trim))
add(room, "baseboard_top", box((8, 0.12, 0.035),
                                center=(0, 1.11, 0.22), color=shadow))
add(room, "chair_rail", box((8, 0.12, 0.065),
                             center=(0, 1.10, 2.22), color=trim))
add(room, "upper_rail", box((8, 0.10, 0.035),
                             center=(0, 1.11, 2.55), color=trim))
for name, z in [("low", 0.39), ("high", 2.06)]:
    add(room, "panel_outer_" + name,
        box((4.35, 0.055, 0.028), center=(0.10, 1.125, z), color=trim))
    add(room, "panel_inner_" + name,
        box((4.20, 0.060, 0.010),
            center=(0.10, 1.095, z + (0.045 if name == "low" else -0.045)),
            color=shadow))
for name, x in [("left", -2.075), ("right", 2.275)]:
    add(room, "panel_outer_" + name,
        box((0.028, 0.055, 1.69), center=(x, 1.125, 1.225), color=trim))
    add(room, "panel_inner_" + name,
        box((0.010, 0.060, 1.59),
            center=(x + (0.045 if name == "left" else -0.045), 1.095, 1.225),
            color=shadow))
for i, x in enumerate([-1.35, 0.38, 2.55]):
    add(room, "wall_seam_%d" % i,
        box((0.009, 0.025, 2.35), center=(x, 1.075, 1.42),
            color=(0.49, 0.47, 0.43)))
for i, x in enumerate([-1.10, -0.99]):
    add(room, "cabinet_pull_%d" % i,
        rod(0.018, start=(x, 1.045, 2.32),
            end=(x, 1.045, 2.40), color=(0.18, 0.16, 0.13)))

add(room, "window_light",
    box((0.65, 0.07, 3.2), center=(-2.75, 1.08, 1.75),
        color=(0.96, 0.96, 0.91)))
add(room, "window_jamb",
    box((0.08, 0.13, 3.4), center=(-2.39, 1.02, 1.75), color=trim))
for i in range(5):
    x = -2.96 + i * 0.09
    add(room, "curtain_fold_%d" % i,
        box((0.095, 0.08, 3.0), center=(x, 0.99 - 0.015*(i % 2), 1.68),
            color=(0.72+i*0.018, 0.68+i*0.018, 0.60+i*0.018)))
scene.include("architecture", room)

chaise = Asset("Chaise longue")
add(chaise, "wooden_seat_foundation",
    fillet_box((L, W, 0.13), radius=0.055,
               center=(CX, CY, Z-0.12), color=frame))
add(chaise, "seat_cushion",
    fillet_box((L, W, 0.19), radius=0.09,
               center=(CX, CY, Z), color=fabric))
for i in range(13):
    yy = CY-0.39+i*0.065
    add(chaise, "upholstery_stripe_%02d" % i,
        rod(0.0035, start=(CX-1.04, yy, Z+0.098),
            end=(CX+1.04, yy, Z+0.098), color=stripe))

tube(chaise, "near_seat_piping",
     [(CX-1.07,CY-0.44,0.76), (CX-0.65,CY-0.46,0.77),
      (CX+0.45,CY-0.46,0.77), (CX+1.05,CY-0.40,0.75)],
     0.012, fabric_edge)
tube(chaise, "near_carved_rail",
     [(CX-1.08,CY-0.47,0.57), (CX-0.70,CY-0.48,0.54),
      (CX-0.10,CY-0.48,0.53), (CX+0.57,CY-0.48,0.54),
      (CX+1.08,CY-0.42,0.53)], 0.029, frame_light)
tube(chaise, "foot_carved_rail",
     [(CX+1.08,CY-0.42,0.53), (CX+1.16,CY-0.23,0.54),
      (CX+1.16,CY+0.22,0.54), (CX+1.08,CY+0.42,0.56)],
     0.028, frame_light)

for ix, x in enumerate([CX-0.91, CX+0.99]):
    for iy, y in enumerate([CY-0.37, CY+0.34]):
        tube(chaise, "leg_%d_%d" % (ix, iy),
             [(x,y,0.56), (x+0.045,y,0.45), (x+0.035,y,0.30),
              (x-0.015,y-0.015,0.10), (x+0.015,y-0.04,0.055)],
             0.039, frame)
        add(chaise, "leg_joint_%d_%d" % (ix, iy),
            ball(0.055, center=(x,y,0.52), color=frame_light))
for i, x in enumerate([-0.62, 0.02, 0.67]):
    add(chaise, "apron_rosette_%d" % i,
        ball(0.047, center=(CX+x,CY-0.50,0.535), color=frame_light))

back = fillet_box((0.16, 0.92, 0.88), radius=0.065,
                  center=(CX-1.08, CY, 1.13), color=fabric)
back.turn(axis="+y", degrees=-13)
add(chaise, "upholstered_back", back)

for side, yy in [("near", CY-0.46), ("far", CY+0.46)]:
    tube(chaise, "back_outline_" + side,
         [(CX-1.00,yy,0.57), (CX-1.15,yy,0.80), (CX-1.29,yy,1.10),
          (CX-1.32,yy,1.42), (CX-1.25,yy,1.58), (CX-1.08,yy,1.62),
          (CX-0.92,yy,1.56)], 0.033, frame)
tube(chaise, "back_crest",
     [(CX-1.25,CY-0.46,1.58), (CX-1.30,CY-0.26,1.63),
      (CX-1.31,CY,1.64), (CX-1.30,CY+0.26,1.63),
      (CX-1.25,CY+0.46,1.58)], 0.027, frame_light)

for side, yy in [("near", CY-0.47), ("far", CY+0.47)]:
    tube(chaise, "arm_rail_" + side,
         [(CX-1.27,yy,1.46), (CX-1.16,yy,1.28), (CX-0.98,yy,1.13),
          (CX-0.78,yy,1.04), (CX-0.61,yy,1.01)], 0.033, frame_light)
    tube(chaise, "arm_support_" + side,
         [(CX-0.61,yy,1.01), (CX-0.59,yy,0.87),
          (CX-0.51,yy,0.69), (CX-0.48,yy,0.59)], 0.033, frame)
    add(chaise, "arm_infill_" + side,
        fillet_box((0.68, 0.07, 0.48), radius=0.03,
                   center=(CX-0.92, yy, 0.88), color=fabric))

pillow = fillet_box((0.22, 0.58, 0.59), radius=0.095,
                    center=(CX-0.91, CY-0.01, 1.20),
                    color=(0.85,0.78,0.65))
pillow.turn(axis="+y", degrees=-17)
add(chaise, "loose_pillow", pillow)
add(chaise, "seat_label",
    box((0.16, 0.095, 0.006), center=(CX+0.56,CY+0.08,0.772),
        color=(0.07,0.17,0.15)))
scene.include("chaise_longue", chaise)

chair = Asset("Foreground cane chair")
add(chair, "cane_panel",
    fillet_box((0.74, 0.60, 0.045), radius=0.02,
               center=(-2.05,-2.85,0.49), color=(0.49,0.31,0.22)))
for yy in [-3.15, -2.55]:
    add(chair, "chair_long_rim_%s" % yy,
        rod(0.035, start=(-2.40,yy,0.51), end=(-1.70,yy,0.51),
            color=frame_light))
for xx in [-2.40, -1.70]:
    add(chair, "chair_short_rim_%s" % xx,
        rod(0.035, start=(xx,-3.15,0.51), end=(xx,-2.55,0.51),
            color=frame_light))
for i in range(7):
    x = -2.34 + i*0.10
    add(chair, "cane_line_%d" % i,
        rod(0.004, start=(x,-3.09,0.516), end=(x,-2.61,0.516),
            color=(0.69,0.51,0.38)))
scene.include("foreground_chair", chair)

realize(scene)
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
background.inputs["Color"].default_value = (0.80,0.78,0.73,1)
background.inputs["Strength"].default_value = 0.42

area_emitter((-3.3,-3.0,4.8), power=500, size=4.0,
             target=(0,0,0.8), color=(1.0,0.91,0.81))
area_emitter((2.0,-0.5,4.7), power=180, size=3.5,
             target=(0,0,0.5), color=(1.0,0.96,0.91))

landmarks = [
    ("back crest", (CX-1.30,CY-0.26,1.63), (0.08,0.25)),
    ("seat foot", (CX+1.16,CY-0.23,0.75), (0.81,0.68)),
    ("front leg bottom", (CX+1.005,CY-0.41,0.055), (0.77,0.93)),
    ("wall panel upper right", (2.275,1.10,2.06), (0.88,0.10)),
]

def project_table():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for name, point, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            0.5*(clip.x/clip.w+1), 0.5*(1-clip.y/clip.w))
        result.append(uv)
    return result

# Compare old and trial camera on the same actual geometry. The reference points
# remain separate from computed projections; visibility still requires a render.
set_view(OLD_CAMERA, OLD_TARGET, lens=OLD_LENS)
old_uv = project_table()
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
trial_uv = project_table()
print("Landmark                 reference       old camera       candidate")
for (name, point, ref), old, trial in zip(landmarks, old_uv, trial_uv):
    print("%-24s %s %s %s" % (name, ref, old, trial))

def error(values):
    total = 0.0
    for (_, _, ref), uv in zip(landmarks, values):
        if uv is None:
            return 1e9
        total += (uv[0]-ref[0])**2 + (uv[1]-ref[1])**2
    return total

if error(trial_uv) >= error(old_uv):
    set_view(OLD_CAMERA, OLD_TARGET, lens=OLD_LENS)
    print("Restored old camera: trial landmark error did not improve.")
else:
    print("Using candidate camera: selected landmark error improved.")
