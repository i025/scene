# Reference inventory, approximate normalized image bounds:
# Chaise (0.04, 0.23)–(0.83, 0.94): pale long seat, curved raised head,
# upholstered side arms, dark carved wooden frame, and curved legs.
# Cream pillow (0.08, 0.27)–(0.32, 0.53), overlapping the head.
# Small green label (0.68, 0.53)–(0.71, 0.59) on the seat.
# Cream paneled wall and baseboard occupy the upper half; a wall return
# appears at the far right. Dark wooden floor occupies the lower half.
# Bright window and curtain are partly visible at left. A cropped cane chair
# fragment occupies the lower-left corner. Rear legs and hidden surfaces
# are uncertain.
#
# Comparison with the first render: the chaise was much too small in frame,
# the floor too light, the seat too narrow and thin, and the near upholstered
# arm insufficiently filled. The wall molding was too repetitive.
# This revision enlarges the view, darkens the floor, fills the chaise's
# silhouette, and uses fewer, larger wall panels.
#
# Estimated expanded count: approximately 220 primitives, including tube
# segments and balls, wall molding, upholstery stripes, and chair fragment.

from sceneact import *
import bpy
import math

scene = Scene("Paneled room and chaise")

wall = (0.66, 0.63, 0.57)
trim = (0.75, 0.72, 0.65)
trim_dark = (0.51, 0.49, 0.44)
floor_color = (0.105, 0.045, 0.027)
frame = (0.27, 0.25, 0.19)
frame_highlight = (0.50, 0.46, 0.34)
upholstery = (0.72, 0.64, 0.59)
side_fabric = (0.62, 0.54, 0.49)
pillow_color = (0.80, 0.72, 0.60)
stripe_color = (0.58, 0.46, 0.43)

def tube(parent, name, points, radius, color):
    parent.include(name, sweep_tube(points=points, radius=radius, color=color))

room = Asset("architecture")
room.include("dark_wood_floor",
             box((9, 8, 0.10), center=(0, 0, -0.07), color=floor_color))
room.include("back_wall",
             box((8, 0.12, 3.6), center=(0, 1.40, 1.8), color=wall))
room.include("right_wall_return",
             box((0.12, 2.7, 3.6), center=(3.05, 0.20, 1.8), color=wall))
room.include("baseboard",
             box((7.9, 0.08, 0.20), center=(0, 1.30, 0.16), color=trim))
room.include("baseboard_cap",
             box((7.9, 0.10, 0.035), center=(0, 1.27, 0.28), color=trim))

def wall_rod(name, a, b, radius=0.012, color=trim):
    room.include(name, rod(radius, start=a, end=b, color=color))

# Large framed wall panels, with two narrow profiles around each inset.
for idx, (left, right) in enumerate([(-3.10, -1.12), (-1.02, 1.98), (2.08, 3.0)]):
    for k, inset in enumerate((0.0, 0.055)):
        x0, x1 = left + inset, right - inset
        z0, z1 = 0.38 + inset, 1.80 - inset
        y = 1.315 - k * 0.007
        for suffix, a, b in [
            ("bottom", (x0,y,z0), (x1,y,z0)),
            ("top", (x0,y,z1), (x1,y,z1)),
            ("left", (x0,y,z0), (x0,y,z1)),
            ("right", (x1,y,z0), (x1,y,z1))
        ]:
            wall_rod("panel_%d_%d_%s" % (idx,k,suffix), a, b, 0.011)

wall_rod("upper_rail", (-3.8,1.28,2.02), (3.0,1.28,2.02), 0.025)
wall_rod("upper_rail_shadow", (-3.8,1.31,2.12), (3.0,1.31,2.12), 0.008, trim_dark)
# Narrow vertical joints in the upper wall.
for i, x in enumerate((-1.18, 0.18)):
    wall_rod("upper_joint_%d" % i, (x,1.325,1.84), (x,1.325,3.1), 0.004, trim_dark)
# Two small dark wall fittings.
for i, x in enumerate((-1.05, -0.96)):
    room.include("wall_fitting_%d" % i,
                 ball(0.025, center=(x,1.25,1.99), color=(0.12,0.11,0.09)))
scene.include("architecture", room)

floor_seams = Asset("floorboard_seams")
for i in range(-6, 7):
    y = i * 0.53
    floor_seams.include("seam_%d" % i,
        rod(0.0025, start=(-4,y,-0.013), end=(4,y,-0.013),
            color=(0.065,0.025,0.016)))
scene.include("floorboard_seams", floor_seams)

window = Asset("window_and_curtain")
window.include("bright_window",
               box((0.45,0.06,2.9), center=(-2.66,1.20,1.50),
                   color=(0.95,0.94,0.88)))
window.include("window_frame",
               box((0.055,0.10,2.9), center=(-2.42,1.14,1.5),
                   color=(0.78,0.75,0.67)))
for i in range(5):
    window.include("curtain_fold_%d" % i,
        box((0.065,0.08,2.8),
            center=(-2.39+i*0.055,1.09-(i%2)*0.025,1.45),
            color=(0.67+i*0.015,0.62+i*0.015,0.53+i*0.015)))
scene.include("window_and_curtain", window)

chaise = Asset("chaise_longue")

# A broad seat with a domed upper face and a full upholstered edge.
seat = ball(1, center=(0.08,0,0.68), color=upholstery)
seat.resize((1.43,0.66,0.23))
chaise.include("broad_seat_cushion", seat)
chaise.include("seat_underbody",
    box((2.35,1.13,0.17), center=(0.03,0,0.60), color=upholstery))

head = ball(1, center=(-1.18,0,1.05), color=upholstery)
head.resize((0.27,0.63,0.62))
head.turn(axis="+y", degrees=-17)
chaise.include("raised_upholstered_head", head)

# Side panels fill the visible enclosed arm area.
for s in (-1,1):
    side = ball(1, center=(-1.02,s*0.53,0.91), color=side_fabric)
    side.resize((0.40,0.11,0.43))
    side.turn(axis="+y", degrees=-24)
    chaise.include("upholstered_side_%d" % s, side)

tube(chaise, "head_outer_crest",
     [(-1.04,-0.60,0.68),(-1.31,-0.62,0.94),
      (-1.45,-0.54,1.31),(-1.44,-0.31,1.52),
      (-1.40,0,1.59),(-1.44,0.31,1.52),
      (-1.45,0.54,1.31),(-1.31,0.62,0.94),(-1.04,0.60,0.68)],
     0.036, frame)
tube(chaise, "head_crest_highlight",
     [(-1.41,-0.51,1.31),(-1.40,-0.29,1.49),
      (-1.36,0,1.56),(-1.40,0.29,1.49),(-1.41,0.51,1.31)],
     0.011, frame_highlight)

for s in (-1,1):
    y = s*0.60
    tube(chaise, "arm_rail_%d" % s,
         [(-1.37,y,1.29),(-1.23,y*1.04,1.10),
          (-1.04,y*1.05,0.97),(-0.82,y*1.05,0.92),
          (-0.70,y*1.02,0.72),(-0.57,y,0.60)],
         0.035, frame)
    tube(chaise, "arm_highlight_%d" % s,
         [(-1.28,y*1.02,1.14),(-1.05,y*1.05,1.00),
          (-0.83,y*1.05,0.95)], 0.010, frame_highlight)
    tube(chaise, "seat_apron_%d" % s,
         [(-0.88,s*0.56,0.52),(-0.48,s*0.61,0.49),
          (0.20,s*0.62,0.47),(0.91,s*0.59,0.48),
          (1.27,s*0.49,0.50)], 0.036, frame)
    tube(chaise, "apron_highlight_%d" % s,
         [(-0.78,s*0.57,0.54),(-0.42,s*0.62,0.51),
          (0.26,s*0.63,0.49),(0.93,s*0.60,0.50)],
         0.010, frame_highlight)

tube(chaise, "foot_end_rail",
     [(1.20,-0.51,0.50),(1.36,-0.36,0.49),
      (1.43,0,0.48),(1.36,0.36,0.49),(1.20,0.51,0.50)],
     0.035, frame)

for x in (-0.75,1.22):
    for s in (-1,1):
        y = s*0.51
        tube(chaise, "leg_%s_%s" % (x,s),
             [(x,y,0.52),(x+0.04,y*1.04,0.38),
              (x-0.01,y*1.08,0.22),(x-0.04,y*1.10,0.08),
              (x+0.005,y*1.10,0.045)], 0.036, frame)
        chaise.include("leg_knee_%s_%s" % (x,s),
                       ball(0.062, center=(x,y,0.49), color=frame_highlight))

for i, dx in enumerate((-0.12,0,0.12)):
    ornament = ball(0.052, center=(0.20+dx,-0.63,0.48), color=frame_highlight)
    ornament.resize((1.0,0.28,0.65))
    chaise.include("apron_carving_%d" % i, ornament)

# Restrained woven lines on the broad cushion.
for i in range(-10,11):
    y = i*0.055
    frac = abs(y)/0.66
    x_end = 0.08 + 1.36*math.sqrt(max(0.05,1.0-frac*frac))
    z = 0.68 + 0.23*math.sqrt(max(0.05,1.0-frac*frac)) + 0.004
    chaise.include("upholstery_stripe_%02d" % (i+10),
        rod(0.003, start=(-0.91,y,z), end=(x_end,y,z), color=stripe_color))

# A soft, thick pillow leaning against the raised head.
pillow = ball(1, center=(-1.02,-0.02,1.23), color=pillow_color)
pillow.resize((0.24,0.42,0.38))
pillow.turn(axis="+y", degrees=-23)
chaise.include("cream_pillow", pillow)

label = box((0.14,0.075,0.009), center=(0.74,-0.08,0.91),
            color=(0.025,0.14,0.13))
chaise.include("seat_label", label)
scene.include("chaise_longue", chaise)

fragment = Asset("foreground_cane_chair_fragment")
fragment.include("cane_seat",
    box((0.74,0.54,0.045), center=(-2.12,-1.75,0.47),
        color=(0.42,0.27,0.17)))
tube(fragment, "seat_rim",
     [(-2.49,-2.02,0.49),(-1.75,-2.02,0.49),
      (-1.75,-1.48,0.49),(-2.49,-1.48,0.49)], 0.037, frame_highlight)
for i in range(8):
    x = -2.44+i*0.09
    fragment.include("cane_line_%d" % i,
        rod(0.004, start=(x,-1.99,0.496), end=(x,-1.51,0.496),
            color=(0.65,0.49,0.34)))
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
background.inputs["Color"].default_value = (0.73,0.71,0.67,1)
background.inputs["Strength"].default_value = 0.55

set_view((1.8,-6.5,3.45), (-0.05,0.12,0.83), lens=65)
area_emitter((-3.8,-2.8,4.7), power=700, size=4.0,
             target=(-0.2,0.1,0.6), color=(1.0,0.91,0.80))
area_emitter((2.8,-0.8,4.5), power=240, size=3.5,
             target=(0,0,0.7), color=(1.0,0.95,0.88))
