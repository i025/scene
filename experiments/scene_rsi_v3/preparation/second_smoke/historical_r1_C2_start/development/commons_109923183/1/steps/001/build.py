# Reference inventory, estimated image bounds:
# - Chaise longue, approximately (0.04, 0.23)–(0.83, 0.94): long pale
#   upholstered seat, raised curved head at image left, wood frame, arms,
#   carved trim and curved legs. Its far side and rear supports are occluded.
# - Cream pillow on the raised head, approximately (0.08, 0.28)–(0.33, 0.53).
# - Small dark rectangular label on the seat, approximately (0.68, 0.53)–(0.71, 0.59).
# - Paneled cream wall and baseboard behind the chaise, approximately
#   (0.02, 0.00)–(1.00, 0.55); a vertical wall return is visible at right.
# - Dark brown wooden floor, approximately (0.00, 0.50)–(1.00, 1.00).
# - Bright window and pale curtain at the far left, partially occluded.
# - Fragment of a cane chair at bottom left, approximately (0.00, 0.80)–
#   (0.20, 1.00); its remaining shape is outside the photograph.
#
# Estimated expanded primitive count: about 250, including tube segments,
# seat stripes, panel moldings, chair fragment and decorative frame details.

from sceneact import *
import bpy
import math

scene = Scene("Chaise interior")

ivory = (0.72, 0.69, 0.62)
wall_trim = (0.82, 0.79, 0.72)
wall_shadow = (0.55, 0.53, 0.48)
floor_color = (0.22, 0.105, 0.067)
wood = (0.34, 0.30, 0.22)
wood_light = (0.57, 0.51, 0.38)
wood_dark = (0.24, 0.21, 0.16)
fabric = (0.77, 0.69, 0.63)
stripe = (0.61, 0.49, 0.47)
pillow_color = (0.85, 0.79, 0.67)

# Architecture is built as separate editable wall, panel, and floor parts.
room = Asset("architecture")
room.include("floor", box((8, 7, 0.10), center=(0, 0, -0.07), color=floor_color))
room.include("back_wall", box((8, 0.12, 3.5), center=(0, 1.37, 1.75), color=ivory))
room.include("right_return", box((0.12, 2.5, 3.5), center=(3.02, 0.20, 1.75), color=ivory))
room.include("baseboard", box((7.8, 0.08, 0.19), center=(0, 1.27, 0.17), color=wall_trim))
room.include("baseboard_cap", box((7.8, 0.09, 0.035), center=(0, 1.24, 0.28), color=wall_trim))

def wall_line(name, a, b, radius=0.012, col=wall_trim):
    room.include(name, rod(radius, start=a, end=b, color=col))

# Large inset wall panels with double narrow molding.
for idx, (x0, x1) in enumerate([(-2.8, -0.67), (-0.57, 1.72), (1.82, 2.90)]):
    for k, inset in enumerate((0.0, 0.075)):
        z0, z1 = 0.42 + inset, 1.82 - inset
        xa, xb = x0 + inset, x1 - inset
        y = 1.295 - k * 0.005
        wall_line("panel_%d_%d_bottom" % (idx, k), (xa, y, z0), (xb, y, z0), 0.012)
        wall_line("panel_%d_%d_top" % (idx, k), (xa, y, z1), (xb, y, z1), 0.012)
        wall_line("panel_%d_%d_left" % (idx, k), (xa, y, z0), (xa, y, z1), 0.012)
        wall_line("panel_%d_%d_right" % (idx, k), (xb, y, z0), (xb, y, z1), 0.012)
wall_line("upper_rail", (-3.7, 1.27, 2.05), (3.0, 1.27, 2.05), 0.025)
wall_line("upper_rail_shadow", (-3.7, 1.28, 2.15), (3.0, 1.28, 2.15), 0.012, wall_shadow)
scene.include("architecture", room)

# Sparse long seams suggest the dark wooden boards.
floor = Asset("floorboard_seams")
for i in range(-6, 7):
    y = i * 0.47
    floor.include("seam_%d" % i,
                  rod(0.003, start=(-3.8, y, -0.012), end=(3.8, y, -0.012),
                      color=(0.12, 0.055, 0.035)))
scene.include("floorboard_seams", floor)

window = Asset("window_and_curtain")
window.include("bright_window", box((0.48, 0.055, 2.8),
                                     center=(-3.05, 1.22, 1.53),
                                     color=(0.94, 0.93, 0.87)))
window.include("window_frame", box((0.055, 0.09, 2.8),
                                    center=(-2.79, 1.18, 1.52),
                                    color=(0.78, 0.75, 0.67)))
for i in range(5):
    window.include("curtain_fold_%d" % i,
                   box((0.065, 0.08, 2.75),
                       center=(-2.75 + i * 0.06, 1.13 - (i % 2) * 0.025, 1.48),
                       color=(0.72 + i * 0.015, 0.68 + i * 0.015, 0.60 + i * 0.015)))
scene.include("window_and_curtain", window)

# Chaise: its long axis is X; the head is at negative X.
chaise = Asset("chaise_longue")
# Upholstery is represented by a gently domed long cushion and a raised head.
seat = ball(1, center=(0.10, 0.0, 0.66), color=fabric)
seat.resize((1.39, 0.53, 0.19))
chaise.include("seat_cushion", seat)

# A shallow solid under the domed seat gives the upholstered front a full edge.
chaise.include("seat_underbody", box((2.35, 0.90, 0.17),
                                     center=(0.05, 0, 0.58), color=fabric))
head = ball(1, center=(-1.12, 0.0, 1.05), color=fabric)
head.resize((0.24, 0.51, 0.61))
head.turn(axis="+y", degrees=-17)
chaise.include("raised_upholstered_head", head)

# The upholstered near side of the head and the far arm create the enclosed shape.
side = ball(1, center=(-0.97, -0.43, 0.83), color=(0.71, 0.63, 0.57))
side.resize((0.36, 0.075, 0.38))
side.turn(axis="+y", degrees=-24)
chaise.include("near_upholstered_arm", side)
far_side = ball(1, center=(-0.97, 0.43, 0.84), color=(0.73, 0.65, 0.59))
far_side.resize((0.35, 0.075, 0.37))
far_side.turn(axis="+y", degrees=-24)
chaise.include("far_upholstered_arm", far_side)

def tube(parent, name, points, radius, color):
    parent.include(name, sweep_tube(points=points, radius=radius, color=color))

# Exposed curving rails follow the outer contour of the head, arms, and seat.
tube(chaise, "head_outer_crest",
     [(-1.05, -0.48, 0.69), (-1.31, -0.49, 0.91),
      (-1.43, -0.42, 1.30), (-1.42, -0.25, 1.51),
      (-1.39, 0.00, 1.59), (-1.42, 0.26, 1.51),
      (-1.43, 0.43, 1.30), (-1.31, 0.49, 0.91),
      (-1.05, 0.48, 0.69)], 0.035, wood)
tube(chaise, "head_crest_highlight",
     [(-1.39, -0.40, 1.30), (-1.38, -0.23, 1.49),
      (-1.35, 0.00, 1.55), (-1.38, 0.24, 1.49),
      (-1.39, 0.40, 1.30)], 0.012, wood_light)
for s in (-1, 1):
    y = s * 0.48
    tube(chaise, "arm_rail_%s" % s,
         [(-1.35, y, 1.30), (-1.22, y * 1.07, 1.10),
          (-1.04, y * 1.11, 0.96), (-0.82, y * 1.11, 0.91),
          (-0.70, y * 1.04, 0.72), (-0.57, y, 0.60)],
         0.034, wood)
    tube(chaise, "arm_rail_highlight_%s" % s,
         [(-1.28, y * 1.04, 1.13), (-1.06, y * 1.11, 0.99),
          (-0.83, y * 1.11, 0.94)], 0.010, wood_light)

# Seat apron rails and shaped end; rods keep the silhouette legible.
for s in (-1, 1):
    tube(chaise, "long_apron_%s" % s,
         [(-0.88, s * 0.46, 0.51), (-0.48, s * 0.49, 0.48),
          (0.20, s * 0.50, 0.46), (0.91, s * 0.48, 0.47),
          (1.26, s * 0.40, 0.49)], 0.035, wood)
    tube(chaise, "apron_highlight_%s" % s,
         [(-0.78, s * 0.47, 0.52), (-0.42, s * 0.50, 0.50),
          (0.26, s * 0.51, 0.48), (0.93, s * 0.49, 0.49)],
         0.010, wood_light)
tube(chaise, "foot_end_rail",
     [(1.20, -0.42, 0.49), (1.35, -0.30, 0.48),
      (1.41, 0.0, 0.47), (1.35, 0.30, 0.48), (1.20, 0.42, 0.49)],
     0.035, wood)

# Cabriole legs: slender bent supports with rounded feet.
for x in (-0.75, 1.22):
    for s in (-1, 1):
        y = s * 0.40
        tube(chaise, "leg_%s_%s" % (x, s),
             [(x, y, 0.51), (x + 0.04, y * 1.04, 0.38),
              (x - 0.01, y * 1.08, 0.22), (x - 0.04, y * 1.10, 0.08),
              (x + 0.005, y * 1.10, 0.045)],
             0.035, wood)
        chaise.include("leg_knee_%s_%s" % (x, s),
                       ball(0.065, center=(x, y, 0.48), color=wood_light))

# A small carved central ornament on the visible apron.
for i, dx in enumerate((-0.12, 0, 0.12)):
    ornament = ball(0.055, center=(0.20 + dx, -0.51, 0.47), color=wood_light)
    ornament.resize((1.0, 0.28, 0.63))
    chaise.include("apron_carving_%d" % i, ornament)

# Fine, subdued longitudinal lines in the upholstery, clipped to a rounded end.
for i in range(-8, 9):
    y = i * 0.055
    frac = abs(y) / 0.52
    x_end = 0.10 + 1.32 * math.sqrt(max(0.05, 1.0 - frac * frac))
    x_start = -0.92
    z = 0.66 + 0.19 * math.sqrt(max(0.05, 1.0 - frac * frac)) + 0.003
    if x_end > x_start:
        chaise.include("seat_woven_stripe_%02d" % (i + 8),
                       rod(0.0035, start=(x_start, y, z),
                           end=(x_end, y, z), color=stripe))

pillow = box((0.39, 0.57, 0.48), center=(-1.04, -0.02, 1.18), color=pillow_color)
pillow.turn(axis="+y", degrees=-25)
chaise.include("cream_pillow", pillow)
piping = [
    (-1.14, -0.31, 1.00), (-1.29, -0.31, 1.40),
    (-1.25, 0.28, 1.40), (-1.10, 0.28, 1.00)
]
tube(chaise, "pillow_edge", piping, 0.009, (0.92, 0.85, 0.73))

label = box((0.13, 0.08, 0.008), center=(0.72, -0.08, 0.846),
            color=(0.055, 0.20, 0.18))
chaise.include("seat_label", label)
scene.include("chaise_longue", chaise)

# The cane chair is only a cropped fragment in the foreground.
fragment = Asset("foreground_cane_chair_fragment")
fragment.include("cane_seat", box((0.72, 0.52, 0.045),
                                  center=(-2.35, -1.65, 0.47),
                                  color=(0.55, 0.38, 0.25)))
tube(fragment, "seat_rim",
     [(-2.71, -1.91, 0.49), (-1.99, -1.91, 0.49),
      (-1.99, -1.39, 0.49), (-2.71, -1.39, 0.49)],
     0.035, wood_light)
for i in range(8):
    x = -2.65 + i * 0.08
    fragment.include("cane_line_%d" % i,
                     rod(0.004, start=(x, -1.88, 0.496),
                         end=(x, -1.42, 0.496), color=(0.74, 0.59, 0.43)))
scene.include("foreground_chair_fragment", fragment)

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
background.inputs["Color"].default_value = (0.78, 0.76, 0.71, 1)
background.inputs["Strength"].default_value = 0.7

set_view((3.0, -6.5, 3.45), (-0.05, 0.12, 0.78), lens=48)
area_emitter((-3.8, -2.8, 4.7), power=850, size=4.0,
             target=(-0.2, 0.1, 0.6), color=(1.0, 0.91, 0.79))
area_emitter((2.8, -0.8, 4.5), power=350, size=3.5,
             target=(0, 0, 0.7), color=(1.0, 0.95, 0.87))
